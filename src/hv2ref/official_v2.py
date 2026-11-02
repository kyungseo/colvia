"""Pure v2 history reducer. Closed means evidence-complete, never just a label."""
from . import official_schema as schema

need = schema.need


class History:
    def __init__(self, grant):
        self.grant = schema.grant_record(grant)
        self.scope = grant['scope']
        self.rows = []
        self.runtime_intent = self.runtime_start = self.runtime_failure = self.runtime_close = None
        self.children = []; self.rpc = set(); self.admission = None; self.bound = False
        self.callbacks = {}; self.pending = None; self.next_callback = 1
        self.workers = {}; self.completed_refs = []; self.ready = None
        self.revoked = False; self.latch = False; self.seal = None; self.terminal = None
        self.diagnostics = set()

    def active(self):
        need(not self.revoked and not self.latch and self.seal is None and self.runtime_close is None, 'v2-authority-closed')

    def worker(self, value):
        ordinal = value['worker_ordinal']
        need(ordinal in self.workers, 'v2-worker-without-intent')
        return self.workers[ordinal]

    def pending_callback(self, value):
        need(self.pending is not None and value['callback_id'] == self.pending, 'v2-pending-callback')
        return self.callbacks[self.pending]

    def consume_callback_id(self, value):
        need(value['callback_id'] == self.next_callback, 'v2-callback-ordinal')
        self.next_callback += 1

    def effect(self):
        effects = []
        for worker in self.workers.values():
            if worker['intent']['value']['role'] != 'write':
                continue
            if worker['failure'] is not None:
                effects.append('none')
            elif worker['result'] is not None:
                effects.append('unknown' if worker['close'] is not None and
                               worker['close']['value']['returncode'] != 0 else worker['result']['value']['effect'])
            else:
                effects.append('unknown')
        return 'unknown' if 'unknown' in effects else 'applied' if 'applied' in effects else 'none'

    def effect_refs(self):
        # Every write intent is represented, including unconfirmed attempts.
        return sorted((w['result'] or w['failure'] or w['intent'])['seq']
                      for w in self.workers.values() if w['intent']['value']['role'] == 'write')

    def closure_refs(self):
        rows = [w['close'] or w['failure'] for w in self.workers.values()]
        rows.append(self.runtime_close or self.runtime_failure)
        return sorted(row['seq'] for row in rows if row is not None)

    def processes_closed(self):
        runtime = self.runtime_intent is None or self.runtime_failure is not None or self.runtime_close is not None
        workers = all(w['failure'] is not None or (w['result'] is not None and w['close'] is not None)
                      for w in self.workers.values())
        return runtime and workers

    def identified_processes(self):
        """Resolution cannot infer spawn failure from missing PID/birth evidence."""
        if self.runtime_intent is not None and self.runtime_failure is None:
            need(self.runtime_start is not None and self.runtime_start['value']['birth'] is not None,
                 'v2-runtime-identity-unavailable')
        for worker in self.workers.values():
            if worker['failure'] is None:
                need(worker['start'] is not None and worker['start']['value']['birth'] is not None,
                     'v2-worker-identity-unavailable')

    def apply(self, row):
        kind, value = row['kind'], row['value']
        schema.event(kind, value)
        need(row['seq'] == len(self.rows) + 1, 'v2-row-sequence')
        if not self.rows:
            need(kind == 'granted' and value == {
                'grant': self.grant['grant'], 'scope_sha256': schema.digest(self.scope),
                'recovery_locator_sha256': schema.digest(self.grant['recovery_locator'])}, 'v2-grant-journal')
            self.rows.append(row)
            return
        need(kind != 'granted', 'v2-duplicate-grant')
        need(self.terminal is None or kind == 'operator-resolved-unknown', 'v2-event-after-terminal')
        if kind == 'runtime-reserved':
            self.active()
            need(self.runtime_intent is None and value['ordinal'] == 1, 'v2-runtime-reservation')
            self.runtime_intent = row
        elif kind == 'runtime-started':
            need(self.runtime_intent is not None and self.runtime_start is None and self.runtime_failure is None and
                 value['ordinal'] == 1, 'v2-runtime-start-order')
            self.runtime_start = row
        elif kind == 'runtime-spawn-failed':
            need(self.runtime_intent is not None and self.runtime_start is None and self.runtime_failure is None and
                 value['ordinal'] == 1 and value['reason'] == 'spawn_failed' and value['reaped'] is True, 'v2-runtime-spawn-failure')
            self.runtime_failure = row; self.revoked = True
        elif kind == 'runtime-child':
            need(self.runtime_start is not None and self.runtime_close is None and value not in self.children and
                 len(self.children) < 256, 'v2-runtime-child-order')
            self.children.append(value)
        elif kind == 'rpc-reserved':
            method = value['method']
            need(self.runtime_start is not None and self.runtime_close is None and method not in self.rpc, 'v2-rpc-order')
            if method != 'turn/interrupt':
                self.active()
                order = ('initialize', 'config/read', 'account/read', 'model/list', 'thread/start', 'turn/start')
                need(set(order[:order.index(method)]) <= self.rpc, 'v2-rpc-prerequisite')
                if method in ('thread/start', 'turn/start'):
                    need(self.admission is not None, 'v2-rpc-without-admission')
            else:
                need('turn/start' in self.rpc, 'v2-interrupt-before-turn')
            self.rpc.add(method)
        elif kind == 'admission':
            self.active()
            need(self.runtime_start is not None and self.admission is None and
                 {'initialize', 'config/read', 'account/read', 'model/list'} <= self.rpc,
                 'v2-admission-order')
            self.admission = row
        elif kind == 'bound':
            self.active()
            need(not self.bound and value['ordinal'] == 1 and value['established'] is True and
                 'turn/start' in self.rpc, 'v2-bind-order')
            self.bound = True
        elif kind == 'recovery-ready':
            self.active()
            output = self.scope['output_id']; original = self.scope['documents'][output]['original_identity']
            need(self.bound and self.pending is None and len(self.completed_refs) == 1 and self.ready is None and
                 value['output_id'] == output and value['recovery_ordinal'] == self.grant['recovery_locator']['recovery_ordinal'] and
                 value['original_identity'] == original and value['original_sha256'] == original['sha256'] and
                 value['byte_count'] == original['size'], 'v2-recovery-ready-binding')
            self.ready = row
        elif kind == 'callback-reserved':
            self.active()
            need(self.bound and self.pending is None and len(self.completed_refs) < 5, 'v2-callback-reservation-order')
            self.consume_callback_id(value)
            step = len(self.completed_refs)
            need(value['ordinal'] == step + 1, 'v2-step-ordinal')
            if step == 0:
                need(value['tool'] == 'read' and value['file_ids'] == self.scope['read_ids'] and
                     value['verifier_id'] is None and value['expected_identity'] is None, 'v2-read-step')
            elif step == 1:
                need(value['tool'] == 'write' and value['file_ids'] == [self.scope['output_id']] and
                     value['verifier_id'] is None and self.ready is not None and
                     value['expected_identity'] == self.scope['documents'][self.scope['output_id']]['original_identity'], 'v2-write-step')
            else:
                need(value['tool'] == 'verify' and value['file_ids'] == [] and
                     value['verifier_id'] == schema.VERIFIERS[step - 2] and value['expected_identity'] is None, 'v2-verifier-step')
            self.pending = value['callback_id']
            self.callbacks[self.pending] = {'reservation': row, 'worker': None}
        elif kind == 'worker-spawn-intent':
            self.active()
            callback = self.pending_callback(value)
            need(callback['worker'] is None and value['worker_ordinal'] == len(self.workers) + 1 and
                 len(self.workers) < self.scope['limits']['worker_limit'] and
                 value['role'] == callback['reservation']['value']['tool'] and
                 value['code_identity'] == self.scope['resources']['worker_digest'], 'v2-worker-intent')
            self.workers[value['worker_ordinal']] = {'intent': row, 'start': None, 'failure': None, 'result': None, 'close': None}
            callback['worker'] = value['worker_ordinal']
        elif kind == 'worker-started':
            worker = self.worker(value)
            need(worker['start'] is None and worker['failure'] is None, 'v2-worker-start-order')
            worker['start'] = row
        elif kind == 'worker-spawn-failed':
            worker = self.worker(value)
            need(worker['start'] is None and worker['failure'] is None and value['reason'] == 'spawn_failed' and
                 value['reaped'] is True, 'v2-worker-spawn-failure')
            worker['failure'] = row; self.revoked = True
        elif kind == 'worker-result':
            worker = self.worker(value)
            need(worker['start'] is not None and worker['result'] is None, 'v2-worker-result-order')
            callback = self.callbacks[worker['intent']['value']['callback_id']]['reservation']['value']
            role = callback['tool']
            need((value['reason'] is None) == value['success'], 'v2-worker-result-reason')
            if role == 'write':
                need(value['effect'] == ('applied' if value['success'] else 'unknown') and
                     (not value['success'] or (value['after'] is not None and
                                              value['before'] == callback['expected_identity'])) and
                     value['verifier_id'] is None and value['verifier_pass'] is None, 'v2-write-result')
            else:
                need(value['effect'] == 'none' and value['before'] is None and value['after'] is None, 'v2-nonwrite-result')
                if role == 'verify':
                    need(value['verifier_id'] == callback['verifier_id'] and
                         (value['verifier_pass'] is True if value['success'] else value['verifier_pass'] is not True), 'v2-verifier-result')
                else:
                    need(value['verifier_id'] is None and value['verifier_pass'] is None, 'v2-read-result')
            worker['result'] = row
            if value['effect'] == 'unknown':
                self.revoked = True; self.latch = True
        elif kind == 'worker-closed':
            worker = self.worker(value)
            need(worker['start'] is not None and worker['start']['value']['birth'] is not None and
                 worker['close'] is None and value['group_absent'] is True and
                 value['birth_absent'] is True, 'v2-worker-closure')
            worker['close'] = row
        elif kind == 'callback-completed':
            callback = self.pending_callback(value)
            need(callback['worker'] is not None, 'v2-completion-without-worker')
            worker = self.workers[callback['worker']]
            if worker['failure'] is not None:
                need(value['result_ref'] is None and value['closure_ref'] == worker['failure']['seq'] and
                     value['success'] is False and value['failure_code'] == 'spawn_failed', 'v2-failed-spawn-completion')
            else:
                need(worker['result'] is not None and worker['close'] is not None and
                     value['result_ref'] == worker['result']['seq'] and value['closure_ref'] == worker['close']['seq'] and
                     worker['result']['value']['effect'] != 'unknown', 'v2-completion-evidence')
                result = worker['result']['value']
                need(value['success'] == result['success'] and value['failure_code'] == result['reason'], 'v2-completion-result')
                if value['success']:
                    need(worker['close']['value']['returncode'] == 0, 'v2-completion-returncode')
                    tool = callback['reservation']['value']['tool']
                    need(tool != 'write' or result['effect'] == 'applied', 'v2-completion-write')
                    need(tool != 'verify' or result['verifier_pass'] is True, 'v2-completion-verifier')
            self.pending = None
            if value['success']:
                self.completed_refs.append(row['seq'])
            else:
                self.revoked = True
        elif kind == 'callback-aborted-before-spawn':
            callback = self.pending_callback(value)
            need(callback['worker'] is None, 'v2-abort-after-intent')
            self.pending = None; self.revoked = True
        elif kind == 'callback-refused':
            self.consume_callback_id(value)
            # A late refused call must not erase an already admitted callback.
            self.revoked = True
        elif kind == 'revoked':
            self.revoked = True
        elif kind == 'effect-unknown':
            need(value['callback_id'] is None or value['callback_id'] in self.callbacks,
                 'v2-unknown-callback')
            self.revoked = True; self.latch = True
        elif kind == 'diagnostic':
            key = (value['source'], value['phase'], value['reason'])
            need(key not in self.diagnostics and len(self.diagnostics) < 16 and
                 (len(self.diagnostics) < 15 or value['reason'] == 'diagnostic_limit'), 'v2-diagnostic-limit')
            self.diagnostics.add(key)
        elif kind == 'seal':
            self.active()
            need(self.pending is None and len(self.completed_refs) == 5 and value['completed_refs'] == self.completed_refs,
                 'v2-seal-order')
            writes = [w['result']['value'] for w in self.workers.values() if w['intent']['value']['role'] == 'write']
            need(len(writes) == 1 and writes[0]['effect'] == 'applied' and
                 value['result_identity'] == writes[0]['after'], 'v2-seal-identity')
            self.seal = row
        elif kind == 'processes-closed':
            need(self.runtime_start is not None and self.runtime_start['value']['birth'] is not None and
                 self.runtime_close is None and value['runtime_ref'] == self.runtime_start['seq'] and value['group_absent'] is True and
                 value['final_scan_confirmed'] is True and
                 value['children'] == [dict(child, absent=True) for child in self.children], 'v2-runtime-closure')
            self.runtime_close = row
        elif kind == 'terminal':
            need(value['document_write_effect'] == self.effect() and value['effect_refs'] == self.effect_refs() and
                 value['closure_refs'] == self.closure_refs(), 'v2-terminal-evidence')
            status = value['status']
            if status != 'unknown':
                need(self.pending is None and not self.latch and self.effect() != 'unknown' and self.processes_closed(),
                     'v2-terminal-not-closed')
                if status == 'completed':
                    need(self.seal is not None and self.effect() == 'applied', 'v2-terminal-unsealed')
                elif status == 'interrupted':
                    need(self.revoked, 'v2-terminal-not-revoked')
                else:
                    need('turn/start' not in self.rpc and not self.callbacks and not self.workers, 'v2-terminal-after-launch')
                    self.revoked = True
            else:
                self.revoked = True
            self.terminal = status
        elif kind == 'operator-resolved-unknown':
            need(self.terminal in (None, 'unknown') and value['grant'] == self.grant['grant'] and
                 value['journal_head'] == row['previous'] and value['previous_status'] == (self.terminal or 'incomplete') and
                 set(value['documents']) == set(self.scope['documents']), 'v2-resolution-binding')
            self.identified_processes()
            self.terminal = 'operator-resolved-unknown'; self.revoked = True
        if kind in ('worker-result', 'worker-closed'):
            worker = self.worker(value)
            if (worker['intent']['value']['role'] == 'write' and worker['result'] is not None and
                    worker['close'] is not None and worker['close']['value']['returncode'] != 0):
                self.revoked = True; self.latch = True
        self.rows.append(row)

    def summary(self):
        return {'schema_version': 2, 'grant': self.grant['grant'], 'scope': self.scope,
                'recovery_locator': self.grant['recovery_locator'], 'recovery_availability': 'not_checked',
                'rows': self.rows, 'head': self.rows[-1]['sha256'], 'completed': len(self.completed_refs),
                'pending': self.pending, 'revoked': self.revoked, 'sealed': self.seal is not None,
                'status': self.terminal or 'incomplete', 'document_write_effect': self.effect(),
                'runtime_reserved': self.runtime_intent is not None,
                'runtime_started': None if self.runtime_start is None else self.runtime_start['value'],
                'spawn_failed': self.runtime_failure is not None,
                'processes_closed': None if self.runtime_close is None else self.runtime_close['value'],
                'children': self.children, 'workers': len(self.workers), 'history': self}


def reduce(grant, rows):
    history = History(grant)
    need(bool(rows), 'v2-empty-journal')
    for row in rows:
        history.apply(row)
    return history


def read_capsule(target, grant, root, value):
    """Read only the four allowed local files; external availability stays unknown."""
    import os
    import stat
    from . import official_state as state
    from .official_documents import observe_journal, journal_identity
    schema.grant_record(value, target, grant)
    members = list(root.iterdir())
    names = {p.name for p in members}
    need({'grant.json', 'journal.jsonl'} <= names <= {'grant.json', 'journal.jsonl', 'cancel.json', 'receipt.json'},
         'v2-capsule-file-set')
    for member in members:
        info = member.lstat()
        need(stat.S_ISREG(info.st_mode) and info.st_nlink == 1 and info.st_uid == os.getuid() and
             stat.S_IMODE(info.st_mode) in (0o600, 0o644), 'v2-capsule-file-kind-mode')
        state.regular(member)
    rows, mode, observed = observe_journal(root / 'journal.jsonl')
    history = reduce(value, rows)
    result = history.summary()
    journal = None
    if result['status'] not in schema.CLOSED:
        need(stat.S_IMODE(root.lstat().st_mode) == 0o700, 'v2-live-capsule-not-private')
        need(all(stat.S_IMODE(p.lstat().st_mode) == 0o600 for p in members), 'v2-live-record-not-private')
        journal = Journal(root / 'journal.jsonl', value)
        need(journal.rows == rows and journal_identity((root / 'journal.jsonl').lstat()) == observed,
             'v2-journal-observation-drift')
    marker = None
    if 'cancel.json' in names:
        marker = state.load(root / 'cancel.json')
        schema.exact(marker, 'grant reason')
        need(marker['grant'] == grant, 'v2-cancel-grant'); schema.choice(marker['reason'], schema.REASONS)
    if 'receipt.json' in names:
        receipt = state.load(root / 'receipt.json')
        schema.exact(receipt, 'grant status result_identity core_apply')
        need(receipt['grant'] == grant and receipt['status'] == 'effects-sealed' and receipt['core_apply'] is False and
             history.seal is not None and receipt['result_identity'] == history.seal['value']['result_identity'],
             'v2-receipt-binding')
        schema.identity(receipt['result_identity'])
    result.update(root=root, journal=journal, cancel_requested=marker is not None)
    return result


def resolution_preview(value, *, host_control_root=None):
    from . import official_state as state
    from .official_recovery import document_observation, inspect
    need(value['status'] not in schema.CLOSED, 'resolution-requires-unresolved-state')
    history = value['history']
    history.identified_processes()
    processes = []
    if history.runtime_start is not None:
        processes.append(history.runtime_start['value'])
    processes.extend(w['start']['value'] for w in history.workers.values() if w['start'] is not None)
    for process in processes:
        need(state.process_birth(process['pid']) != process['birth'] and state.group_absent(process['pid']),
             'v2-process-present-or-unconfirmed')
    for child in history.children:
        need(state.process_birth(child['pid']) != child['birth'], 'v2-observed-child-present')
    documents = {key: document_observation(item['path'], absent=True)[0]
                 for key, item in value['scope']['documents'].items()}
    availability = 'not_checked' if host_control_root is None else inspect(value, host_control_root)
    result = {'grant': value['grant'], 'journal_head': value['head'], 'previous_status': value['status'],
              'documents': documents, 'process_absence': True, 'recovery_availability': availability,
              'action': 'record-unknown-resolution'}
    return {'observation': result, 'confirm_token': schema.digest(result)}


class Journal:
    """Validate prospective v2 events before the durable append boundary."""
    def __init__(self, path, grant, *, create=False):
        from .official_documents import EffectJournal
        self.base = EffectJournal(path, create=create)
        self.grant = grant
        if self.base.rows:
            reduce(grant, self.base.rows)

    @property
    def rows(self):
        return self.base.rows

    @property
    def failed(self):
        return self.base.failed

    def append(self, kind, value):
        from .official_documents import canonical, digest
        with self.base.mutex:
            need(not self.base.failed, 'v2-journal-poisoned')
            row = {'seq': len(self.rows) + 1, 'previous': self.rows[-1]['sha256'] if self.rows else '0' * 64,
                   'kind': kind, 'value': value}
            row['sha256'] = digest(canonical(row))
            reduce(self.grant, [*self.rows, row])
            return self.base.append(kind, value)

    def history(self):
        need(self.base.read() == self.rows, 'v2-live-journal-drift')
        return reduce(self.grant, self.rows)
