"""Single v2 effect writer; immutable live authority and minimal durable history."""
from pathlib import Path
import copy
import fcntl
import os
import time

from . import official_state as state, official_schema as schema, official_recovery as recovery
from .official_v2 import Journal
from .official_controller import Controller
from .official_documents import wire_bytes, end_process, HostRefusal
from .errors import ContractError

STEPS = [('u2_read_file', None), ('u2_write_file', None), ('u2_verify', 'DOC-LINKS'),
         ('u2_verify', 'DOC-GFM'), ('u2_verify', 'DOC-CLAIMS')]
ROLES = {'u2_read_file': 'read', 'u2_write_file': 'write', 'u2_verify': 'verify'}


def reason_code(error, default='internal_error'):
    # Only internal validator messages participate; OS paths cannot choose a code.
    if isinstance(error, TimeoutError):
        return 'deadline'
    if not isinstance(error, (ContractError, HostRefusal)):
        return default
    message = error.message if isinstance(error, ContractError) else str(error)
    if message in schema.REASONS:
        return message
    if any(needle in message for needle in ('closure unavailable', 'present-or-unconfirmed',
            'observed-child-present', 'still-present-or-unknown', 'process-observation-unavailable',
            'identity-unavailable', 'birth-unavailable')):
        return 'closure_unconfirmed'
    for needle, code in (('credential-like', 'content_rejected'), ('unapproved document', 'content_rejected'),
                         ('NUL document', 'content_rejected'), ('drift', 'document_drift'),
                         ('cancel', 'cancelled'), ('expired', 'deadline'), ('timeout', 'deadline'),
                         ('time exhausted', 'deadline'), ('recovery', 'recovery_unavailable')):
        if needle in message:
            return code
    return default


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
        self.spec = copy.deepcopy(spec); self.grant = grant
        self.storage = schema.project_grant(self.spec, grant)
        self.target = Path(spec['target']); self.controller = None; self.rpc = None
        self.calls = self.completed = 0; self.pending = None
        self.revoked = self.sealed = self.terminal = False
        self.seen = set(); self.thread = self.turn = None
        self.deadline = time.monotonic() + spec['request']['seconds']
        self.diagnostics = {}; self.diagnostics_flushed = False; self.stop_reason = 'internal_error'
        self.lock = None; self.journal = None
        self.run = state.capsule_path(self.target, grant)
        parent = self.target / '.hrn/executions'
        if not os.path.lexists(parent): state.directory(parent, create=True)
        state.directory(parent)
        lock_path = self.target / '.hrn/locks' / ('official-' + grant + '.lock')
        fd = os.open(lock_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
        self.lock = os.fdopen(fd, 'wb'); fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        staged = lock_path.with_suffix('.d')
        try:
            state.directory(staged, create=True)
            state.publish(staged / 'grant.json', self.storage)
            initial = Journal(staged / 'journal.jsonl', self.storage, create=True)
            initial.append('granted', {'grant': grant, 'scope_sha256': schema.digest(self.storage['scope']),
                                      'recovery_locator_sha256': schema.digest(self.storage['recovery_locator'])})
            state.rename_exclusive(staged, self.run)
            self.journal = Journal(self.run / 'journal.jsonl', self.storage)
            self.controller = Controller(self)
        except BaseException as error:
            try:
                if self.journal is not None: self.fail(error)
            finally: self.close()
            raise

    @property
    def workers(self):
        return len(self.journal.history().workers)

    def diagnostic(self, source, phase, reason, count):
        schema.choice(source, ('host', 'worker', 'runtime')); schema.choice(phase, schema.PHASES)
        schema.choice(reason, schema.REASONS); schema.integer(count)
        key = (source, phase, reason)
        if key not in self.diagnostics and len(self.diagnostics) >= 15:
            key = ('host', 'closure', 'diagnostic_limit')
        self.diagnostics[key] = min(schema.MAX_INT, self.diagnostics.get(key, 0) + count)

    def flush_diagnostics(self):
        if self.diagnostics_flushed: return
        for (source, phase, reason), count in self.diagnostics.items():
            self.journal.append('diagnostic', {'source': source, 'phase': phase, 'reason': reason, 'byte_count': count})
        self.diagnostics_flushed = True

    def cancelled(self):
        marker = self.run / 'cancel.json'
        if not os.path.lexists(marker): return False
        value = state.load(marker); schema.exact(value, 'grant reason')
        state.need(value['grant'] == self.grant, 'cancel-marker'); schema.choice(value['reason'], schema.REASONS)
        return True

    def authority(self, *, check_documents=True):
        state.need(not self.revoked and not self.sealed and not self.terminal, 'order_mismatch')
        state.need(time.monotonic() < self.deadline and time.time_ns() < self.spec['request']['expires_wall_ns'], 'deadline')
        state.need(not self.cancelled(), 'cancelled')
        state.need(schema.project_grant(self.spec, self.grant) == self.storage == state.load(self.run / 'grant.json'), 'grant-drift')
        self.journal.history().active()
        from .official_entry import observe_work
        current = observe_work(self.target, self.spec['request'], after_effect=True); expected = self.spec['work']
        state.need(all(current[k] == expected[k] for k in expected if k != 'worker_snapshot'), 'work-or-installation-drift')
        output = self.spec['request']['documents']['output']
        relative = Path(self.spec['documents']['files'][output]['path']).relative_to(Path(self.spec['request']['worker_root'])).as_posix()
        before, after = expected['worker_snapshot'], current['worker_snapshot']
        state.need(before['ignore_fingerprint'] == after['ignore_fingerprint'] and
                   [x for x in before['entries'] if x['path'] != relative] == [x for x in after['entries'] if x['path'] != relative], 'outside-output-project-drift')
        root = recovery.root_record(self.spec['host_control']['path'], target=self.target,
            worker_root=self.spec['request']['worker_root'], runtime_root=self.spec['runtime_root'],
            output=self.spec['documents']['files'][output]['path'])
        state.need(root == self.spec['host_control'], 'recovery-root-drift')
        if check_documents and self.controller is not None: self.controller.check_files()

    def bind(self, thread, turn):
        state.need(self.thread is None and self.turn is None and all(type(x) is str and 0 < len(x) < 256 for x in (thread, turn)), 'caller_mismatch')
        self.journal.append('bound', {'ordinal': 1, 'established': True})
        self.thread, self.turn = thread, turn

    def revoke(self, reason):
        schema.choice(reason, schema.REASONS)
        if not self.revoked:
            self.stop_reason = reason
            self.revoked = True
            self.journal.append('revoked', {'reason': reason})

    def refuse(self, tool='invalid', reason='protocol_refused', phase='callback_preflight'):
        if not self.revoked:
            self.stop_reason = reason
        self.revoked = True
        callback = self.journal.history().next_callback
        self.journal.append('callback-refused', {'callback_id': callback, 'tool': tool, 'phase': phase,
                            'reason': reason, 'current_call_effect': 'not_started'})
        return {'ok': False, 'worker_admitted': False, 'effect_status': 'not_started', 'reason': reason}

    def complete_pending(self, *, allow_abort=False, reason='worker_failed'):
        history = self.journal.history()
        if self.pending is None: return False
        callback = history.callbacks[self.pending]; ordinal = callback['worker']
        if ordinal is None:
            if allow_abort:
                self.journal.append('callback-aborted-before-spawn', {'callback_id': self.pending, 'reason': reason})
                self.pending = None; self.revoked = True
            return False
        worker = history.workers[ordinal]
        if worker['failure'] is not None:
            success = False; result_ref = None; closure_ref = worker['failure']['seq']; failure = 'spawn_failed'
        elif worker['result'] is not None and worker['close'] is not None and worker['result']['value']['effect'] != 'unknown':
            result = worker['result']['value']; success = result['success']; failure = result['reason']
            result_ref = worker['result']['seq']; closure_ref = worker['close']['seq']
        else:
            return False
        self.journal.append('callback-completed', {'callback_id': self.pending, 'success': success,
                            'result_ref': result_ref, 'closure_ref': closure_ref, 'failure_code': failure})
        self.pending = None
        if success: self.completed += 1
        else: self.revoked = True; self.stop_reason = failure
        return success

    def dispatch(self, envelope):
        reserved = False; role = 'invalid'; phase = 'callback_preflight'
        try:
            self.calls += 1; self.authority()
            state.need(self.calls <= 8 and self.pending is None and self.completed < 5 and self.workers < self.spec['request']['worker_limit'], 'order_mismatch')
            state.need(type(envelope) is dict and set(envelope) in (
                {'threadId', 'turnId', 'callId', 'tool', 'arguments'},
                {'threadId', 'turnId', 'callId', 'tool', 'arguments', 'namespace'}), 'input_shape')
            state.need(self.thread is not None and envelope['threadId'] == self.thread and envelope['turnId'] == self.turn and
                       envelope.get('namespace') is None, 'caller_mismatch')
            call = envelope['callId']
            state.need(type(call) is str and 0 < len(call) < 256 and call not in self.seen, 'caller_mismatch')
            tool, verifier = STEPS[self.completed]; args = envelope['arguments']; role = ROLES[tool]
            state.need(envelope['tool'] == tool and type(args) is dict and len(wire_bytes(envelope)) <= 65536, 'input_shape')
            output = self.spec['request']['documents']['output']
            if self.completed == 0:
                state.need(args == {'file_ids': self.spec['request']['read_ids']}, 'scope_mismatch')
            elif self.completed == 1:
                state.need(set(args) == {'file_id', 'expected_sha256', 'content'} and args['file_id'] == output and
                           args['expected_sha256'] == self.spec['documents']['source_digests'][output] and
                           type(args['content']) is str and len(args['content'].encode()) <= 65536, 'scope_mismatch')
            else:
                state.need(args == {'verifier_id': verifier}, 'order_mismatch')
            self.controller.preflight(tool, args)
            if role == 'write':
                phase = 'recovery'
                metadata = recovery.save_original(self.spec, self.grant, self.storage['scope']['documents'][output]['original_identity'])
                self.journal.append('recovery-ready', metadata)
            phase = 'reservation'; callback = self.journal.history().next_callback
            self.journal.append('callback-reserved', {'callback_id': callback, 'ordinal': self.completed + 1, 'tool': role,
                'file_ids': self.spec['request']['read_ids'] if role == 'read' else [output] if role == 'write' else [],
                'verifier_id': verifier, 'expected_identity': self.storage['scope']['documents'][output]['original_identity'] if role == 'write' else None})
            self.pending = callback; self.seen.add(call); reserved = True; phase = 'worker'
            result = self.controller.dispatch(tool, args)
            success = self.complete_pending()
            if not success:
                state.need(self.pending is None, 'closure_unconfirmed')
                return {'ok': False, 'reason': self.stop_reason, 'worker_admitted': True, 'effect_status': 'none'}
            if self.completed == self.spec['request']['worker_limit'] and self.completed < 5:
                self.revoke('worker_budget_consumed')
            return {'ok': True, 'result': result}
        except BaseException as error:
            reason = reason_code(error, 'recovery_unavailable' if phase == 'recovery' else 'worker_failed' if reserved else 'internal_error')
            self.stop_reason = reason
            self.diagnostic('host', phase if phase in schema.PHASES else 'worker', reason, len(str(error).encode(errors='replace')))
            if self.journal.failed:
                self.revoked = True
                raise
            if not reserved:
                result = self.refuse(role, reason, phase)
            else:
                self.complete_pending(allow_abort=True, reason=reason)
                history = self.journal.history(); self.revoked = True
                if self.pending is not None or history.effect() == 'unknown':
                    self.journal.append('effect-unknown', {'reason': reason, 'callback_id': self.pending})
                elif not history.revoked:
                    self.journal.append('revoked', {'reason': reason})
                result = {'ok': False, 'reason': reason, 'worker_admitted': history.callbacks[callback]['worker'] is not None,
                          'effect_status': 'unknown' if self.pending is not None or history.effect() == 'unknown' else 'none'}
            if not isinstance(error, Exception): raise
            return result

    def seal(self):
        self.authority()
        state.need(self.pending is None and self.completed == 5 and
                   set(self.controller.verifiers) == set(schema.VERIFIERS) and
                   all(v['pass'] for v in self.controller.verifiers.values()), 'order_mismatch')
        output = self.storage['scope']['output_id']
        identity, _ = recovery.document_observation(self.controller.files[output]['path'])
        history = self.journal.history()
        self.journal.append('seal', {'result_identity': identity, 'completed_refs': history.completed_refs})
        self.sealed = self.controller.sealed = True
        state.publish_receipt(self.target, self.run / 'receipt.json', {'grant': self.grant, 'status': 'effects-sealed', 'result_identity': identity, 'core_apply': False})

    def finish(self, status):
        state.need(not self.terminal, 'terminal-reused')
        self.flush_diagnostics(); history = self.journal.history()
        self.journal.append('terminal', {'status': status, 'stop_reason': None if status == 'completed' else self.stop_reason,
                            'document_write_effect': history.effect(), 'effect_refs': history.effect_refs(), 'closure_refs': history.closure_refs()})
        self.terminal = True; self.revoked = True
        value = state.read_capsule(self.target, self.grant); result = state.public_status(value)
        if status in ('completed', 'interrupted', 'revoked-before-launch'):
            result['cleanup_pending'] = recovery.cleanup_transient(value, self.spec['host_control'])
        return result

    def fail(self, error):
        if self.terminal or self.journal is None or self.journal.failed: return
        reason = reason_code(error); self.stop_reason = reason
        history = self.journal.history()
        self.revoke(reason)
        if history.pending is None and not history.latch and history.effect() != 'unknown' and history.processes_closed():
            status = 'revoked-before-launch' if 'turn/start' not in history.rpc and not history.callbacks else 'interrupted'
        else:
            if not history.latch:
                self.journal.append('effect-unknown', {'reason': reason, 'callback_id': history.pending})
            status = 'unknown'
        return self.finish(status)

    def close(self):
        try:
            if self.controller is not None and self.controller.active is not None:
                end_process(self.controller.active); self.controller.active = None
        finally:
            if self.lock is not None:
                self.lock.close(); self.lock = None
