"""Existing pure causal oracles ported to the first-format execution contract."""
import copy,hashlib,json,unittest
from colvia.execution import schema,history as v2
from colvia.codec import RecordError as ContractError
from colvia.codec import canonical_bytes as canonical

def digest(raw):return hashlib.sha256(raw).hexdigest()

BIRTH = 'Sat Oct 31 12:00:00 2026'
SHA = 'a' * 64


def identity(ino=2, sha=SHA):
    return dict(dev=1, ino=ino, mode=0o644, nlink=1, size=20, mtime_ns=10, ctime_ns=10, sha256=sha)


def grant(target='/synthetic/project'):
    return {'record_type': 'execution-contract', 'schema_version': 1, 'grant': SHA,
            'policy_version': schema.POLICY, 'target': target,
            'scope': {'work_id': 'synthetic-work', 'documents': {
                'Output': {'path': target + '/output.md', 'view': {'kind': 'replace-range', 'ranges': [[0, 20]]}, 'original_identity': identity()},
                'Reference': {'path': target + '/reference.md', 'view': {'kind': 'full'}, 'original_identity': identity(3)}},
                'read_ids': ['Output', 'Reference'], 'output_id': 'Output',
                'limits': {'seconds': 90, 'expires_wall_ns': 1800000000000000000, 'worker_limit': 5},
                'resources': dict.fromkeys(('python_digest', 'worker_digest', 'parser_digest', 'profile_digest', 'runtime_digest'), SHA),
                'recovery_store_id': 'b' * 32},
            'capability': dict(identity=SHA,policy_digest=SHA,protocol='bounded-document-rpc-1',observation_format='posix-document-process-1'),
            'recovery_locator': {'store_id': 'b' * 32, 'grant': SHA, 'recovery_ordinal': 1}}


class Chain:
    def __init__(self, value=None):
        self.grant = value or grant(); self.rows = []
        self.add('granted', grant=self.grant['grant'], scope_sha256=schema.digest(self.grant['scope']),
                 recovery_locator_sha256=schema.digest(self.grant['recovery_locator']))

    def add(self, kind, **value):
        row = {'seq': len(self.rows) + 1, 'previous': self.rows[-1]['sha256'] if self.rows else '0' * 64,
               'kind': kind, 'value': value}
        row['sha256'] = schema.digest(row); self.rows.append(row)
        return row['seq']

    def read(self):
        return v2.reduce(self.grant,self.rows)

    def launch(self):
        self.add('runtime-reserved', ordinal=1, host_pid=9000, host_birth=BIRTH)
        self.runtime = self.add('runtime-started', ordinal=1, pid=9001, birth=BIRTH)
        for method in ('initialize', 'config/read', 'account/read', 'model/list'):
            self.add('rpc-reserved', method=method)
        self.add('admission', **{'pass': True, 'capability_digest': SHA, 'policy_digest': SHA})
        for method in ('thread/start', 'turn/start'):
            self.add('rpc-reserved', method=method)
        self.add('bound', ordinal=1, established=True)
        return self

    def reserve(self, step):
        role = 'read' if step == 1 else 'write' if step == 2 else 'verify'
        if step == 2:
            self.add('recovery-ready', output_id='Output', recovery_ordinal=1, original_identity=identity(), original_sha256=SHA, byte_count=20)
        self.add('callback-reserved', callback_id=step, ordinal=step, tool=role,
                 file_ids=['Output', 'Reference'] if step == 1 else ['Output'] if step == 2 else [],
                 verifier_id=schema.VERIFIERS[step - 3] if step >= 3 else None,
                 expected_identity=identity() if step == 2 else None)
        return role

    def intent(self, step, role):
        self.add('worker-spawn-intent', callback_id=step, worker_ordinal=step, role=role, code_identity=self.grant['scope']['resources']['worker_digest'])

    def successful(self, step):
        role = self.reserve(step); self.intent(step, role)
        self.add('worker-started', worker_ordinal=step, pid=9010 + step, birth=BIRTH)
        ref = self.add('worker-result', worker_ordinal=step, success=True, effect='applied' if step == 2 else 'none',
                      before=identity() if step == 2 else None, after=identity(4, 'c' * 64) if step == 2 else None,
                      verifier_id=schema.VERIFIERS[step - 3] if step >= 3 else None, verifier_pass=True if step >= 3 else None, reason=None)
        closed = self.add('worker-closed', worker_ordinal=step, returncode=0, group_absent=True, birth_absent=True)
        self.add('callback-completed', callback_id=step, success=True, result_ref=ref, closure_ref=closed, failure_code=None)
        return self

    def close_runtime(self):
        self.add('processes-closed', runtime_ref=self.runtime, group_absent=True, final_scan_confirmed=True, children=[])

    def terminal(self, status):
        h = self.read()
        self.add('terminal', status=status, stop_reason=None if status == 'completed' else 'cancelled',
                 document_write_effect=h.effect(), effect_refs=h.effect_refs(), closure_refs=h.closure_refs())

def semantic_rows(rows):
    """Rebuild integrity after deliberate semantic mutation in retained oracles.

    The old tests called the reducer after bypassing its file-chain parser.
    New reducer checks both; recomputing hashes lets the same tests exercise
    the intended causal refusal rather than stop at the outer integrity check.
    """
    result=copy.deepcopy(rows);previous='0'*64
    for row in result:
        row['previous']=previous
        row['sha256']=schema.digest({k:row[k] for k in ('seq','previous','kind','value')})
        previous=row['sha256']
    return result

class TransitionTests(unittest.TestCase):
    def test_completed_requires_five_actual_successes_and_seal(self):
        c = Chain().launch()
        for step in range(1, 6): c.successful(step)
        h = c.read()
        c.add('seal', result_identity=identity(4, 'c' * 64), completed_refs=h.completed_refs)
        c.close_runtime(); c.terminal('completed')
        h = c.read(); self.assertEqual((h.terminal, h.effect()), ('completed', 'applied'))
        self.assertEqual(h.summary()['recovery_availability'], 'not_checked')

    def test_refusal_before_reservation_then_closure_is_interrupted_none(self):
        c = Chain().launch()
        c.add('callback-refused', callback_id=1, tool='invalid', phase='callback_preflight', reason='caller_mismatch', current_call_effect='not_started')
        self.assertEqual(c.read().summary()['status'], 'incomplete')
        c.close_runtime(); c.terminal('interrupted')
        self.assertEqual((c.read().terminal, c.read().effect()), ('interrupted', 'none'))

    def test_late_refusal_does_not_erase_applied(self):
        c = Chain().launch().successful(1).successful(2)
        c.add('callback-refused', callback_id=3, tool='verify', phase='callback_preflight', reason='order_mismatch', current_call_effect='not_started')
        c.close_runtime(); c.terminal('interrupted')
        self.assertEqual(c.read().effect(), 'applied')
        c.rows[-1]['value']['document_write_effect'] = 'none'
        with self.assertRaises(ContractError):
            v2.reduce(c.grant, semantic_rows(c.rows))

    def test_pre_intent_abort_can_close_but_crash_cannot(self):
        c = Chain().launch().successful(1); c.reserve(2)
        h = c.read(); self.assertEqual((h.summary()['status'], h.effect(), h.pending), ('incomplete', 'none', 2))
        c.add('callback-aborted-before-spawn', callback_id=2, reason='storage_failed')
        c.close_runtime(); c.terminal('interrupted'); self.assertEqual(c.read().effect(), 'none')

    def test_write_intent_without_identity_stays_unknown_and_cannot_resolve(self):
        c = Chain().launch().successful(1); c.reserve(2); c.intent(2, 'write')
        h = c.read(); self.assertEqual((h.summary()['status'], h.effect()), ('incomplete', 'unknown'))
        with self.assertRaisesRegex(ContractError, 'worker-identity-unavailable'):
            h.identified_processes()
        c.add('callback-aborted-before-spawn', callback_id=2, reason='storage_failed')
        with self.assertRaisesRegex(ContractError, 'abort-after-intent'): c.read()

    def test_synchronous_spawn_failure_is_the_only_post_intent_none(self):
        c = Chain().launch().successful(1); c.reserve(2); c.intent(2, 'write')
        failed = c.add('worker-spawn-failed', worker_ordinal=2, reason='spawn_failed', reaped=True)
        c.add('callback-completed', callback_id=2, success=False, result_ref=None, closure_ref=failed, failure_code='spawn_failed')
        c.close_runtime(); c.terminal('interrupted'); self.assertEqual(c.read().effect(), 'none')

    def test_write_failure_with_identical_bytes_is_unknown(self):
        c = Chain().launch().successful(1); c.reserve(2); c.intent(2, 'write')
        c.add('worker-started', worker_ordinal=2, pid=9012, birth=BIRTH)
        result = c.add('worker-result', worker_ordinal=2, success=False, effect='unknown', before=identity(), after=identity(), verifier_id=None, verifier_pass=None, reason='worker_failed')
        closed = c.add('worker-closed', worker_ordinal=2, returncode=1, group_absent=True, birth_absent=True)
        self.assertEqual(c.read().effect(), 'unknown')
        c.add('callback-completed', callback_id=2, success=False, result_ref=result, closure_ref=closed, failure_code='worker_failed')
        with self.assertRaisesRegex(ContractError, 'completion-evidence'): c.read()

    def test_write_applied_requires_nonnull_after(self):
        c = Chain().launch().successful(1).successful(2)
        row = next(r for r in c.rows if r['kind'] == 'worker-result' and r['value']['worker_ordinal'] == 2)
        row['value']['after'] = None
        with self.assertRaisesRegex(ContractError, 'write-result'): v2.reduce(c.grant, semantic_rows(c.rows))

    def test_nonzero_exit_cannot_complete_any_successful_callback(self):
        for step in (1, 2, 3):
            c = Chain().launch()
            for n in range(1, step + 1): c.successful(n)
            close = next(r for r in c.rows if r['kind'] == 'worker-closed' and r['value']['worker_ordinal'] == step)
            close['value']['returncode'] = 1
            with self.subTest(step=step), self.assertRaisesRegex(ContractError, 'completion-returncode'):
                v2.reduce(c.grant, semantic_rows(c.rows))
            if step == 2:
                prefix = c.rows[:-1]
                history = v2.reduce(c.grant, semantic_rows(prefix))
                self.assertEqual((history.effect(), history.revoked, history.latch), ('unknown', True, True))
                # The same contradiction must hold when close precedes result.
                prefix[-2], prefix[-1] = prefix[-1], prefix[-2]
                for index, row in enumerate(prefix, 1): row['seq'] = index
                history = v2.reduce(c.grant, semantic_rows(prefix))
                self.assertEqual((history.effect(), history.revoked, history.latch), ('unknown', True, True))

    def test_successful_write_close_before_result_does_not_latch(self):
        c = Chain().launch().successful(1).successful(2)
        prefix = c.rows[:-1]
        prefix[-2], prefix[-1] = prefix[-1], prefix[-2]
        for index, row in enumerate(prefix, 1): row['seq'] = index
        history = v2.reduce(c.grant, semantic_rows(prefix))
        self.assertEqual((history.effect(), history.revoked, history.latch), ('applied', False, False))

    def test_successful_write_requires_reserved_before_identity(self):
        for before in (None, identity(99)):
            c = Chain().launch().successful(1).successful(2)
            row = next(r for r in c.rows if r['kind'] == 'worker-result' and r['value']['worker_ordinal'] == 2)
            row['value']['before'] = before
            with self.subTest(before=before), self.assertRaisesRegex(ContractError, 'write-result'):
                v2.reduce(c.grant, semantic_rows(c.rows))

    def test_callback_completion_requires_its_worker_closure(self):
        c = Chain().launch().successful(1)
        c.rows = [r for r in c.rows if r['kind'] != 'worker-closed']
        for index, row in enumerate(c.rows, 1): row['seq'] = index
        with self.assertRaisesRegex(ContractError, 'completion-evidence'):
            v2.reduce(c.grant, semantic_rows(c.rows))

    def test_forged_verifier_success_rejected_and_failure_revokes(self):
        c = Chain().launch().successful(1).successful(2).successful(3)
        result = next(r for r in c.rows if r['kind'] == 'worker-result' and r['value']['worker_ordinal'] == 3)
        result['value'].update(success=False, verifier_pass=False, reason='verifier_failed')
        with self.assertRaisesRegex(ContractError, 'completion-result'): v2.reduce(c.grant, semantic_rows(c.rows))
        c.rows[-1]['value'].update(success=False, failure_code='verifier_failed')
        h = v2.reduce(c.grant, semantic_rows(c.rows))
        self.assertEqual((len(h.completed_refs), h.effect(), h.revoked), (2, 'applied', True))
        c.reserve(4)
        with self.assertRaisesRegex(ContractError, 'authority-closed'): v2.reduce(c.grant, semantic_rows(c.rows))

    def test_runtime_unknown_has_no_fabricated_callback(self):
        c = Chain().launch()
        c.add('effect-unknown', reason='closure_unconfirmed', callback_id=None)
        self.assertTrue(c.read().latch)
        c.rows[-1]['value']['callback_id'] = 1
        with self.assertRaisesRegex(ContractError, 'unknown-callback'):
            v2.reduce(c.grant, semantic_rows(c.rows))

    def test_verifier_failure_cannot_claim_a_passing_result(self):
        c = Chain().launch().successful(1).successful(2).successful(3)
        row = next(r for r in c.rows if r['kind'] == 'worker-result' and r['value']['worker_ordinal'] == 3)
        row['value'].update(success=False, reason='worker_failed')
        with self.assertRaisesRegex(ContractError, 'verifier-result'):
            v2.reduce(c.grant, semantic_rows(c.rows))

    def test_prelaunch_unsolicited_callback_is_refused_without_authority(self):
        c = Chain()
        c.add('callback-refused', callback_id=1, tool='invalid', phase='callback_preflight',
              reason='caller_mismatch', current_call_effect='not_started')
        c.terminal('revoked-before-launch')
        h = c.read()
        self.assertEqual((h.effect(), h.pending, len(h.workers)), ('none', None, 0))

    def test_unknown_latch_blocks_intent_and_seal(self):
        for operation in ('intent', 'seal'):
            c = Chain().launch().successful(1); c.reserve(2)
            c.add('effect-unknown', reason='closure_unconfirmed', callback_id=2)
            if operation == 'intent': c.intent(2, 'write')
            else: c.add('seal', result_identity=identity(), completed_refs=[])
            with self.subTest(operation=operation), self.assertRaisesRegex(ContractError, 'authority-closed'):
                c.read()

    def test_missing_worker_or_runtime_closure_blocks_terminal(self):
        for remove in ('worker-closed', 'processes-closed'):
            c = Chain().launch().successful(1)
            c.add('revoked', reason='cancelled'); c.close_runtime(); c.terminal('interrupted')
            # Preserve the chain prefix at the fault boundary, then try closure.
            if remove == 'worker-closed':
                c.rows = c.rows[:next(i for i,r in enumerate(c.rows) if r['kind'] == remove)]
                c.add('revoked', reason='closure_unconfirmed'); c.close_runtime()
            else:
                c.rows = c.rows[:-2]
            c.terminal('interrupted')
            with self.subTest(remove=remove), self.assertRaisesRegex(ContractError, 'terminal-not-closed'):
                c.read()

    def test_launch_and_runtime_intent_crash_are_distinct(self):
        c = Chain(); c.add('runtime-reserved', ordinal=1, host_pid=9000, host_birth=BIRTH)
        with self.assertRaisesRegex(ContractError, 'runtime-identity-unavailable'):
            c.read().identified_processes()
        c = Chain().launch(); c.close_runtime(); c.terminal('revoked-before-launch')
        with self.assertRaisesRegex(ContractError, 'terminal-after-launch'): c.read()

    def test_diagnostics_are_bounded_unique_and_non_authoritative(self):
        c = Chain()
        for reason in sorted(schema.REASONS - {'diagnostic_limit'})[:15]:
            c.add('diagnostic', source='host', phase='closure', reason=reason, byte_count=1)
        c.add('diagnostic', source='host', phase='closure', reason='diagnostic_limit', byte_count=100)
        self.assertEqual(c.read().effect(), 'none')
        c.add('diagnostic', source='runtime', phase='closure', reason='internal_error', byte_count=1)
        with self.assertRaisesRegex(ContractError, 'diagnostic-limit'): c.read()

    def test_operator_resolution_preserves_unknown_effect(self):
        c = Chain().launch().successful(1); c.reserve(2); c.intent(2, 'write')
        c.add('worker-started', worker_ordinal=2, pid=9012, birth=BIRTH)
        c.add('operator-resolved-unknown', grant=SHA, journal_head=c.rows[-1]['sha256'], previous_status='incomplete',
              documents={'Output': identity(), 'Reference': identity(3)}, process_absence=True,
              recovery_availability='missing', action='record-unknown-resolution')
        h = c.read(); self.assertEqual((h.terminal, h.effect()), ('operator-resolved-unknown', 'unknown'))



class IntegrityTests(unittest.TestCase):
    def test_mutation_without_rehash_refuses(self):
        c=Chain().launch();c.rows[-1]['value']['established']=False
        with self.assertRaisesRegex(ContractError,'row-digest'):c.read()
    def test_reordered_rows_refuse_even_with_valid_individual_digests(self):
        c=Chain().launch();c.rows[1],c.rows[2]=c.rows[2],c.rows[1]
        with self.assertRaises(ContractError):c.read()
    def test_admission_is_exact_capability_not_brand(self):
        c=Chain().launch();admission=next(r for r in c.rows if r['kind']=='admission')
        admission['value']['capability_digest']='b'*64
        with self.assertRaisesRegex(ContractError,'capability-mismatch'):v2.reduce(c.grant,semantic_rows(c.rows))
    def test_unknown_native_observation_vocabulary_refuses(self):
        value=grant();value['capability']['observation_format']='unqualified-native-format'
        with self.assertRaisesRegex(ContractError,'observation-unavailable'):schema.grant_record(value)
