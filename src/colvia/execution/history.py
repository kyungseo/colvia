"""Pure causal reducer. Closed means evidence-complete, never just a label.

Ported from established execution semantics; no old journal/store imports.
Runtime admission is bound to a qualified capability, not a model brand.
"""
from . import schema

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
        need(not self.revoked and not self.latch and self.seal is None and self.runtime_close is None, 'execution-authority-closed')

    def worker(self, value):
        ordinal = value['worker_ordinal']
        need(ordinal in self.workers, 'execution-worker-without-intent')
        return self.workers[ordinal]

    def pending_callback(self, value):
        need(self.pending is not None and value['callback_id'] == self.pending, 'execution-pending-callback')
        return self.callbacks[self.pending]

    def consume_callback_id(self, value):
        need(value['callback_id'] == self.next_callback, 'execution-callback-ordinal')
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
                 'execution-runtime-identity-unavailable')
        for worker in self.workers.values():
            if worker['failure'] is None:
                need(worker['start'] is not None and worker['start']['value']['birth'] is not None,
                     'execution-worker-identity-unavailable')

    def apply(self, row):
        schema.exact(row,'seq previous kind value sha256','execution-row-fields')
        schema.sha(row['previous']);schema.sha(row['sha256'])
        need(row['previous']==(self.rows[-1]['sha256'] if self.rows else '0'*64),'execution-row-predecessor')
        need(row['sha256']==schema.digest({k:row[k] for k in ('seq','previous','kind','value')}),'execution-row-digest')
        kind, value = row['kind'], row['value']
        schema.event(kind, value)
        need(row['seq'] == len(self.rows) + 1, 'execution-row-sequence')
        if not self.rows:
            need(kind == 'granted' and value == {
                'grant': self.grant['grant'], 'scope_sha256': schema.digest(self.scope),
                'recovery_locator_sha256': schema.digest(self.grant['recovery_locator'])}, 'execution-grant-journal')
            self.rows.append(row)
            return
        need(kind != 'granted', 'execution-duplicate-grant')
        need(self.terminal is None or kind == 'operator-resolved-unknown', 'execution-event-after-terminal')
        if kind == 'runtime-reserved':
            self.active()
            need(self.runtime_intent is None and value['ordinal'] == 1, 'execution-runtime-reservation')
            self.runtime_intent = row
        elif kind == 'runtime-started':
            need(self.runtime_intent is not None and self.runtime_start is None and self.runtime_failure is None and
                 value['ordinal'] == 1, 'execution-runtime-start-order')
            self.runtime_start = row
        elif kind == 'runtime-spawn-failed':
            need(self.runtime_intent is not None and self.runtime_start is None and self.runtime_failure is None and
                 value['ordinal'] == 1 and value['reason'] == 'spawn_failed' and value['reaped'] is True, 'execution-runtime-spawn-failure')
            self.runtime_failure = row; self.revoked = True
        elif kind == 'runtime-child':
            need(self.runtime_start is not None and self.runtime_close is None and value not in self.children and
                 len(self.children) < 256, 'execution-runtime-child-order')
            self.children.append(value)
        elif kind == 'rpc-reserved':
            method = value['method']
            need(self.runtime_start is not None and self.runtime_start['value']['birth'] is not None and self.runtime_close is None and method not in self.rpc, 'execution-rpc-order')
            if method != 'turn/interrupt':
                self.active()
                order = ('initialize', 'config/read', 'account/read', 'model/list', 'thread/start', 'turn/start')
                need(set(order[:order.index(method)]) <= self.rpc, 'execution-rpc-prerequisite')
                if method in ('thread/start', 'turn/start'):
                    need(self.admission is not None, 'execution-rpc-without-admission')
            else:
                need('turn/start' in self.rpc, 'execution-interrupt-before-turn')
            self.rpc.add(method)
        elif kind == 'admission':
            self.active()
            need(self.runtime_start is not None and self.runtime_start['value']['birth'] is not None and self.admission is None and
                 {'initialize', 'config/read', 'account/read', 'model/list'} <= self.rpc,
                 'execution-admission-order')
            need(value['capability_digest']==self.grant['capability']['identity'] and
                 value['policy_digest']==self.grant['capability']['policy_digest'],'execution-capability-mismatch')
            self.admission = row
        elif kind == 'bound':
            self.active()
            need(not self.bound and value['ordinal'] == 1 and value['established'] is True and
                 'turn/start' in self.rpc, 'execution-bind-order')
            self.bound = True
        elif kind == 'recovery-ready':
            self.active()
            output = self.scope['output_id']; original = self.scope['documents'][output]['original_identity']
            need(self.bound and self.pending is None and len(self.completed_refs) == 1 and self.ready is None and
                 value['output_id'] == output and value['recovery_ordinal'] == self.grant['recovery_locator']['recovery_ordinal'] and
                 value['original_identity'] == original and value['original_sha256'] == original['sha256'] and
                 value['byte_count'] == original['size'], 'execution-recovery-ready-binding')
            self.ready = row
        elif kind == 'callback-reserved':
            self.active()
            need(self.bound and self.pending is None and len(self.completed_refs) < 5, 'execution-callback-reservation-order')
            self.consume_callback_id(value)
            step = len(self.completed_refs)
            need(value['ordinal'] == step + 1, 'execution-step-ordinal')
            if step == 0:
                need(value['tool'] == 'read' and value['file_ids'] == self.scope['read_ids'] and
                     value['verifier_id'] is None and value['expected_identity'] is None, 'execution-read-step')
            elif step == 1:
                need(value['tool'] == 'write' and value['file_ids'] == [self.scope['output_id']] and
                     value['verifier_id'] is None and self.ready is not None and
                     value['expected_identity'] == self.scope['documents'][self.scope['output_id']]['original_identity'], 'execution-write-step')
            else:
                need(value['tool'] == 'verify' and value['file_ids'] == [] and
                     value['verifier_id'] == schema.VERIFIERS[step - 2] and value['expected_identity'] is None, 'execution-verifier-step')
            self.pending = value['callback_id']
            self.callbacks[self.pending] = {'reservation': row, 'worker': None}
        elif kind == 'worker-spawn-intent':
            self.active()
            callback = self.pending_callback(value)
            need(callback['worker'] is None and value['worker_ordinal'] == len(self.workers) + 1 and
                 len(self.workers) < self.scope['limits']['worker_limit'] and
                 value['role'] == callback['reservation']['value']['tool'] and
                 value['code_identity'] == self.scope['resources']['worker_digest'], 'execution-worker-intent')
            self.workers[value['worker_ordinal']] = {'intent': row, 'start': None, 'failure': None, 'result': None, 'close': None}
            callback['worker'] = value['worker_ordinal']
        elif kind == 'worker-started':
            worker = self.worker(value)
            need(worker['start'] is None and worker['failure'] is None, 'execution-worker-start-order')
            worker['start'] = row
        elif kind == 'worker-spawn-failed':
            worker = self.worker(value)
            need(worker['start'] is None and worker['failure'] is None and value['reason'] == 'spawn_failed' and
                 value['reaped'] is True, 'execution-worker-spawn-failure')
            worker['failure'] = row; self.revoked = True
        elif kind == 'worker-result':
            worker = self.worker(value)
            need(worker['start'] is not None and worker['result'] is None, 'execution-worker-result-order')
            callback = self.callbacks[worker['intent']['value']['callback_id']]['reservation']['value']
            role = callback['tool']
            need((value['reason'] is None) == value['success'], 'execution-worker-result-reason')
            if role == 'write':
                need(value['effect'] == ('applied' if value['success'] else 'unknown') and
                     (not value['success'] or (value['after'] is not None and
                                              value['before'] == callback['expected_identity'])) and
                     value['verifier_id'] is None and value['verifier_pass'] is None, 'execution-write-result')
            else:
                need(value['effect'] == 'none' and value['before'] is None and value['after'] is None, 'execution-nonwrite-result')
                if role == 'verify':
                    need(value['verifier_id'] == callback['verifier_id'] and
                         (value['verifier_pass'] is True if value['success'] else value['verifier_pass'] is not True), 'execution-verifier-result')
                else:
                    need(value['verifier_id'] is None and value['verifier_pass'] is None, 'execution-read-result')
            worker['result'] = row
            if value['effect'] == 'unknown':
                self.revoked = True; self.latch = True
        elif kind == 'worker-closed':
            worker = self.worker(value)
            need(worker['start'] is not None and worker['start']['value']['birth'] is not None and
                 worker['close'] is None and value['group_absent'] is True and
                 value['birth_absent'] is True, 'execution-worker-closure')
            worker['close'] = row
        elif kind == 'callback-completed':
            callback = self.pending_callback(value)
            need(callback['worker'] is not None, 'execution-completion-without-worker')
            worker = self.workers[callback['worker']]
            if worker['failure'] is not None:
                need(value['result_ref'] is None and value['closure_ref'] == worker['failure']['seq'] and
                     value['success'] is False and value['failure_code'] == 'spawn_failed', 'execution-failed-spawn-completion')
            else:
                need(worker['result'] is not None and worker['close'] is not None and
                     value['result_ref'] == worker['result']['seq'] and value['closure_ref'] == worker['close']['seq'] and
                     worker['result']['value']['effect'] != 'unknown', 'execution-completion-evidence')
                result = worker['result']['value']
                need(value['success'] == result['success'] and value['failure_code'] == result['reason'], 'execution-completion-result')
                if value['success']:
                    need(worker['close']['value']['returncode'] == 0, 'execution-completion-returncode')
                    tool = callback['reservation']['value']['tool']
                    need(tool != 'write' or result['effect'] == 'applied', 'execution-completion-write')
                    need(tool != 'verify' or result['verifier_pass'] is True, 'execution-completion-verifier')
            self.pending = None
            if value['success']:
                self.completed_refs.append(row['seq'])
            else:
                self.revoked = True
        elif kind == 'callback-aborted-before-spawn':
            callback = self.pending_callback(value)
            need(callback['worker'] is None, 'execution-abort-after-intent')
            self.pending = None; self.revoked = True
        elif kind == 'callback-refused':
            self.consume_callback_id(value)
            # A late refused call must not erase an already admitted callback.
            self.revoked = True
        elif kind == 'revoked':
            self.revoked = True
        elif kind == 'effect-unknown':
            need(value['callback_id'] is None or value['callback_id'] in self.callbacks,
                 'execution-unknown-callback')
            self.revoked = True; self.latch = True
        elif kind == 'diagnostic':
            key = (value['source'], value['phase'], value['reason'])
            need(key not in self.diagnostics and len(self.diagnostics) < 16 and
                 (len(self.diagnostics) < 15 or value['reason'] == 'diagnostic_limit'), 'execution-diagnostic-limit')
            self.diagnostics.add(key)
        elif kind == 'seal':
            self.active()
            need(self.pending is None and len(self.completed_refs) == 5 and value['completed_refs'] == self.completed_refs,
                 'execution-seal-order')
            writes = [w['result']['value'] for w in self.workers.values() if w['intent']['value']['role'] == 'write']
            need(len(writes) == 1 and writes[0]['effect'] == 'applied' and
                 value['result_identity'] == writes[0]['after'], 'execution-seal-identity')
            self.seal = row
        elif kind == 'processes-closed':
            need(self.runtime_start is not None and self.runtime_start['value']['birth'] is not None and
                 self.runtime_close is None and value['runtime_ref'] == self.runtime_start['seq'] and value['group_absent'] is True and
                 value['final_scan_confirmed'] is True and
                 value['children'] == [dict(child, absent=True) for child in self.children], 'execution-runtime-closure')
            self.runtime_close = row
        elif kind == 'terminal':
            need(value['document_write_effect'] == self.effect() and value['effect_refs'] == self.effect_refs() and
                 value['closure_refs'] == self.closure_refs(), 'execution-terminal-evidence')
            status = value['status']
            if status != 'unknown':
                need(self.pending is None and not self.latch and self.effect() != 'unknown' and self.processes_closed(),
                     'execution-terminal-not-closed')
                if status == 'completed':
                    need(self.seal is not None and self.effect() == 'applied', 'execution-terminal-unsealed')
                elif status == 'interrupted':
                    need(self.revoked, 'execution-terminal-not-revoked')
                else:
                    need('turn/start' not in self.rpc and not self.callbacks and not self.workers, 'execution-terminal-after-launch')
                    self.revoked = True
            else:
                self.revoked = True
            self.terminal = status
        elif kind == 'operator-resolved-unknown':
            need(self.terminal in (None, 'unknown') and value['grant'] == self.grant['grant'] and
                 value['journal_head'] == row['previous'] and value['previous_status'] == (self.terminal or 'incomplete') and
                 set(value['documents']) == set(self.scope['documents']), 'execution-resolution-binding')
            self.identified_processes()
            self.terminal = 'operator-resolved-unknown'; self.revoked = True
        if kind in ('worker-result', 'worker-closed'):
            worker = self.worker(value)
            if (worker['intent']['value']['role'] == 'write' and worker['result'] is not None and
                    worker['close'] is not None and worker['close']['value']['returncode'] != 0):
                self.revoked = True; self.latch = True
        self.rows.append(row)

    def summary(self):
        return {'schema_version': 1, 'grant': self.grant['grant'], 'scope': self.scope,
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
    need(bool(rows), 'execution-empty-journal')
    for row in rows:
        history.apply(row)
    return history

