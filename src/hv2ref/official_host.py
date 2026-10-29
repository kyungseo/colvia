"""Single effect writer for one consumed, installed execution grant."""
from pathlib import Path
import fcntl
import json
import os
import time
from . import official_state as state
from .official_documents import DocumentController, EffectJournal, wire_bytes, end_process

STEPS = [('u2_read_file', None), ('u2_write_file', None), ('u2_verify', 'DOC-LINKS'),
         ('u2_verify', 'DOC-GFM'), ('u2_verify', 'DOC-CLAIMS')]

class WorkerBudget:
    def __init__(self, host):
        self.host = host
        self.anchor = {'version': 4, 'approval': 'owner-official-' + host.grant}

    def check_worker_result(self, subject, phase, start, timeout):
        h = self.host
        h.authority(check_documents=False)
        state.need(h.pending is not None and h.workers < h.spec['request']['worker_limit'], 'worker-not-admitted')
        available = min(60, timeout, h.deadline - time.monotonic() - 5)
        state.need(available > 0, 'worker-time-exhausted')
        h.journal.append('worker-reserved', {'callId': h.pending, 'ordinal': h.workers + 1})
        h.workers += 1
        return available

    def reserve(self, kind, subject, phase, start):
        h = self.host
        if kind == 'worker-result':
            # Revocation while an admitted worker runs does not erase its result.
            state.need(h.pending is not None, 'worker-result-without-reservation')
        elif kind == 'seal':
            h.authority()
            state.need(h.pending is None and h.completed == 5 and not h.sealed, 'seal-state')
        else:
            state.need(False, 'correction-not-admitted')
        return h.journal.append(kind, subject)

class ClosedHost:
    """Read-only reconstruction of spent authority; never creates a controller."""
    def __init__(self, target, grant):
        self.target = Path(target); self.grant = grant
        value = state.read_capsule(self.target, grant)
        state.need(value['status'] in state.TERMINAL, 'restore-requires-closed-authority')
        self.head = value['head']

    def dispatch(self, envelope):
        value = state.read_capsule(self.target, self.grant)
        state.need(value['status'] in state.TERMINAL and value['head'] == self.head, 'closed-history-drift')
        return {'ok':False, 'worker_admitted':False, 'effect_status':'not_started', 'reason':'closed-authority'}

    def status(self):
        return state.public_status(state.read_capsule(self.target, self.grant))

class Host:
    @staticmethod
    def restore_closed(target, grant):
        return ClosedHost(target, grant)

    def __init__(self, spec, grant):
        self.spec = json.loads(json.dumps(spec)); self.grant = grant
        self.target = Path(spec['target']); self.controller = None; self.rpc = None
        self.completed = self.calls = self.workers = 0
        self.pending = None; self.revoked = self.sealed = self.terminal = False
        self.seen = set(); self.thread = self.turn = None
        self.deadline = time.monotonic() + spec['request']['seconds']
        parent = self.target / '.hrn/executions'
        if not os.path.lexists(parent):
            state.directory(parent, create=True)
        state.directory(parent)
        self.lock = None
        self.run = state.capsule_path(self.target, grant)
        # writer_guard is held by the caller; this dedicated lock also pins ownership.
        lock_path = self.target / '.hrn/locks' / ('official-' + grant + '.lock')
        fd = os.open(lock_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
        self.lock = os.fdopen(fd, 'wb')
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        staged = lock_path.with_suffix('.d')
        try:
            state.directory(staged, create=True)
            state.publish(staged / 'grant.json', {'record_type': 'official-execution-grant', 'schema_version': 1,
                                                 'grant': grant, 'spec': self.spec})
            initial = EffectJournal(staged / 'journal.jsonl', create=True)
            initial.append('granted', {'grant': grant})
            state.rename_exclusive(staged, self.run)
            self.journal = EffectJournal(self.run / 'journal.jsonl')
        except BaseException:
            self.close(); raise
        try:
            workers = state.directory(self.run / 'workers', create=True)
            scratch = state.directory(self.run / 'scratch', create=True)
            docs = dict(spec['documents'], scratch=str(scratch))
            self.worker_budget = WorkerBudget(self)
            self.controller = DocumentController(docs, workers, self.worker_budget, 'official', 0, self.deadline)
        except BaseException as error:
            self.fail(error); self.close(); raise

    def cancelled(self):
        marker = self.run / 'cancel.json'
        if not os.path.lexists(marker):
            return False
        value = state.load(marker)
        state.need(set(value) == {'grant', 'reason'} and value['grant'] == self.grant and
                   type(value['reason']) is str and 0 < len(value['reason']) <= 512, 'cancel-marker')
        return True

    def authority(self, *, check_documents=True):
        state.need(not self.revoked and not self.sealed and not self.terminal, 'closed-authority')
        state.need(time.monotonic() < self.deadline and time.time_ns() < self.spec['request']['expires_wall_ns'], 'authority-expired')
        state.need(not self.cancelled(), 'cancel-requested')
        saved = state.load(self.run / 'grant.json')
        state.need(saved['spec'] == self.spec and saved['grant'] == self.grant == state.digest(state.canonical(self.spec)), 'grant-drift')
        # Re-read authority and verified installation, but allow this grant's own document change.
        from .official_entry import observe_work
        current = observe_work(self.target, self.spec['request'], after_effect=True)
        expected = self.spec['work']
        state.need(all(current[k] == expected[k] for k in expected if k != 'worker_snapshot'), 'work-or-installation-drift')
        # Allow exactly this controller's output change; all other snapshot entries remain fixed.
        output = self.spec['request']['documents']['output']
        relative = Path(self.spec['documents']['files'][output]['path']).relative_to(Path(self.spec['request']['worker_root'])).as_posix()
        before, after = expected['worker_snapshot'], current['worker_snapshot']
        state.need(before['ignore_fingerprint'] == after['ignore_fingerprint'] and
                   [x for x in before['entries'] if x['path'] != relative] ==
                   [x for x in after['entries'] if x['path'] != relative], 'outside-output-project-drift')
        if check_documents and self.controller is not None:
            self.controller.check_files()

    def bind(self, thread, turn):
        state.need(self.thread is None and self.turn is None and all(type(x) is str and 0 < len(x) < 256 for x in (thread, turn)), 'caller-binding')
        self.thread, self.turn = thread, turn
        self.journal.append('bound', {'thread': thread, 'turn': turn})

    def revoke(self, reason):
        if not self.revoked:
            self.journal.append('revoked', {'reason': reason, 'completed': self.completed, 'pending': self.pending})
            self.revoked = True

    def dispatch(self, envelope):
        admitted = False
        try:
            self.calls += 1
            self.authority()
            state.need(self.calls <= 8 and self.pending is None and self.completed < 5 and
                       self.workers < self.spec['request']['worker_limit'], 'callback-budget-or-pending')
            state.need(type(envelope) is dict and set(envelope) in (
                {'threadId','turnId','callId','tool','arguments'},
                {'threadId','turnId','callId','tool','arguments','namespace'}), 'callback-fields')
            state.need(self.thread is not None and envelope['threadId'] == self.thread and
                       envelope['turnId'] == self.turn and envelope.get('namespace') is None, 'callback-caller')
            call = envelope['callId']
            state.need(type(call) is str and 0 < len(call) < 256 and call not in self.seen, 'callback-reused')
            tool, verifier = STEPS[self.completed]; args = envelope['arguments']
            state.need(envelope['tool'] == tool and type(args) is dict and len(wire_bytes(envelope)) <= 65536, 'callback-tool-or-size')
            if self.completed == 0:
                state.need(args == {'file_ids': self.spec['request']['read_ids']}, 'read-scope')
            elif self.completed == 1:
                key = self.spec['request']['documents']['output']
                state.need(set(args) == {'file_id','expected_sha256','content'} and args['file_id'] == key and
                           args['expected_sha256'] == self.spec['documents']['source_digests'][key] and
                           type(args['content']) is str and len(args['content'].encode()) <= 65536, 'write-scope')
            else:
                state.need(args == {'verifier_id': verifier}, 'verifier-order')
            self.journal.append('callback-reserved', envelope)
            self.pending = call; self.seen.add(call); admitted = True
            result = self.controller.dispatch(tool, args)
            state.need(tool != 'u2_verify' or result['pass'] is True, 'verifier-failed')
            self.journal.append('callback-completed', {'callId': call, 'result': result})
            self.pending = None; self.completed += 1
            if self.completed == self.spec['request']['worker_limit'] and self.completed < 5:
                self.revoke('worker-budget-consumed')
            return {'ok': True, 'result': result}
        except BaseException as error:
            # Any exception after reservation leaves a conservative unresolved effect.
            self.revoked = True
            result = {'ok': False, 'reason': type(error).__name__, 'worker_admitted': admitted,
                      'effect_status': 'unknown' if admitted else 'not_started'}
            self.journal.append('effect-unknown' if admitted else 'refused', result)
            if admitted or not isinstance(error, Exception):
                raise
            return result

    def seal(self):
        self.authority()
        state.need(self.pending is None and self.completed == 5, 'seal-before-completion')
        identity = self.controller.seal(); self.sealed = True
        state.publish(self.run / 'receipt.json', {'status': 'effects-sealed', 'grant': self.grant,
                                                'result_identity': identity, 'core_apply': False})

    def finish(self, status):
        state.need(not self.terminal, 'terminal-reused')
        current = state.read_capsule(self.target, self.grant)
        state.need(status in state.TERMINAL | {'unknown'}, 'terminal-value')
        if status != 'unknown':
            state.need(current['pending'] is None, 'terminal-pending-effect')
            state.need(not current['runtime_reserved'] or current['spawn_failed'] or current['processes_closed'] is not None, 'terminal-before-process-close')
            state.need(status != 'completed' or current['sealed'], 'terminal-unsealed')
        self.journal.append('terminal', {'status': status})
        self.terminal = True
        return state.public_status(state.read_capsule(self.target, self.grant))

    def fail(self, error):
        if self.terminal:
            return
        self.revoked = True
        self.journal.append('effect-unknown', {'reason': type(error).__name__, 'pending': self.pending})
        self.finish('unknown')

    def close(self):
        try:
            if self.controller is not None and self.controller.active is not None:
                end_process(self.controller.active)
                self.controller.active = None
        finally:
            if self.lock is not None:
                self.lock.close(); self.lock = None
