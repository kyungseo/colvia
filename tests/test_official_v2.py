"""Strict history and fail-closed oracles, without model or process claims."""
import copy
from contextlib import nullcontext
from pathlib import Path
import os
import tempfile
import unittest
from unittest import mock

from hv2ref import official_schema as schema, official_v2 as v2, official_state as state
from hv2ref.errors import ContractError
from hv2ref.official_documents import canonical, digest, journal_rows, HostRefusal

BIRTH = 'Sat Oct 31 12:00:00 2026'
SHA = 'a' * 64


def identity(ino=2, sha=SHA):
    return dict(dev=1, ino=ino, mode=0o644, nlink=1, size=20, mtime_ns=10, ctime_ns=10, sha256=sha)


def grant(target='/synthetic/project'):
    return {'record_type': 'official-execution-grant', 'schema_version': 2, 'grant': SHA,
            'policy_version': schema.POLICY, 'target': target,
            'scope': {'work_id': 'synthetic-work', 'documents': {
                'Output': {'path': target + '/output.md', 'view': {'kind': 'replace-range', 'ranges': [[0, 20]]}, 'original_identity': identity()},
                'Reference': {'path': target + '/reference.md', 'view': {'kind': 'full'}, 'original_identity': identity(3)}},
                'read_ids': ['Output', 'Reference'], 'output_id': 'Output',
                'limits': {'seconds': 90, 'expires_wall_ns': 1800000000000000000, 'worker_limit': 5},
                'installation': dict.fromkeys(('release_digest', 'binding_digest', 'work_scope_digest'), SHA),
                'resources': dict.fromkeys(('python_digest', 'worker_digest', 'parser_digest', 'profile_digest', 'app_server_digest'), SHA),
                'recovery_store_id': 'b' * 32},
            'recovery_locator': {'store_id': 'b' * 32, 'grant': SHA, 'recovery_ordinal': 1}}


class Chain:
    def __init__(self, value=None):
        self.grant = value or grant(); self.rows = []
        self.add('granted', grant=self.grant['grant'], scope_sha256=schema.digest(self.grant['scope']),
                 recovery_locator_sha256=schema.digest(self.grant['recovery_locator']))

    def add(self, kind, **value):
        row = {'seq': len(self.rows) + 1, 'previous': self.rows[-1]['sha256'] if self.rows else '0' * 64,
               'kind': kind, 'value': value}
        row['sha256'] = digest(canonical(row)); self.rows.append(row)
        return row['seq']

    def read(self):
        return v2.reduce(self.grant, journal_rows(b''.join(canonical(r) for r in self.rows)))

    def launch(self):
        self.add('runtime-reserved', ordinal=1, host_pid=9000, host_birth=BIRTH)
        self.runtime = self.add('runtime-started', ordinal=1, pid=9001, birth=BIRTH)
        for method in ('initialize', 'config/read', 'account/read', 'model/list'):
            self.add('rpc-reserved', method=method)
        self.add('admission', **{'pass': True, 'account_type': 'chatgpt', 'model_id': 'gpt-6.1-sol', 'effort': 'low', 'policy_digest': SHA})
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
        self.add('worker-spawn-intent', callback_id=step, worker_ordinal=step, role=role, code_identity=SHA)

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


class SchemaTests(unittest.TestCase):
    def test_minimal_grant_and_closed_fields(self):
        schema.grant_record(grant())
        for field in ('prompt', 'owner_statement', 'claims', 'argv', 'host_control_root'):
            value = grant(); value['scope'][field] = 'RAW_PAYLOAD'
            with self.subTest(field=field), self.assertRaises(ContractError):
                schema.grant_record(value)

    def test_projection_binding(self):
        chain = Chain(); chain.grant['scope']['limits']['seconds'] = 100
        with self.assertRaisesRegex(ContractError, 'v2-grant-journal'):
            chain.read()

    def test_metadata_type_bounds_and_aliases(self):
        for mutate in (
            lambda g: g.update(schema_version=True),
            lambda g: g['scope']['limits'].update(seconds=True),
            lambda g: g['scope']['limits'].update(worker_limit=2),
            lambda g: g['scope']['documents']['Output']['original_identity'].update(nlink=2),
            lambda g: g['scope']['documents']['Output'].update(path='/x/../payload'),
            lambda g: g['scope']['documents']['Reference'].update(original_identity=identity()),
            lambda g: g['scope']['resources'].update(worker_digest='raw payload'),
            lambda g: g['recovery_locator'].update(store_id='c' * 32),
        ):
            g = grant(); mutate(g)
            with self.subTest(value=g), self.assertRaises(ContractError):
                schema.grant_record(g)

    def test_all_events_reject_extra_fields_and_unknown_events(self):
        for kind, fields in schema.EVENT_FIELDS.items():
            with self.subTest(kind=kind), self.assertRaisesRegex(ContractError, 'v2-event-fields'):
                schema.event(kind, dict.fromkeys(fields.split() + ['payload']))
        with self.assertRaises(ContractError):
            schema.event('protocol', {})

    def test_duplicate_keys_hash_chain_and_torn_rows(self):
        raw = canonical(Chain().rows[0])
        for bad in (raw[:-1], raw.replace(b'"seq":1', b'"seq":1,"seq":1'), raw.replace(b'"seq":1', b'"seq":2')):
            with self.assertRaises((ContractError, ValueError, HostRefusal)):
                journal_rows(bad)


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
            v2.reduce(c.grant, c.rows)

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
        with self.assertRaisesRegex(ContractError, 'write-result'): v2.reduce(c.grant, c.rows)

    def test_nonzero_exit_cannot_complete_any_successful_callback(self):
        for step in (1, 2, 3):
            c = Chain().launch()
            for n in range(1, step + 1): c.successful(n)
            close = next(r for r in c.rows if r['kind'] == 'worker-closed' and r['value']['worker_ordinal'] == step)
            close['value']['returncode'] = 1
            with self.subTest(step=step), self.assertRaisesRegex(ContractError, 'completion-returncode'):
                v2.reduce(c.grant, c.rows)
            if step == 2:
                prefix = c.rows[:-1]
                history = v2.reduce(c.grant, prefix)
                self.assertEqual((history.effect(), history.revoked, history.latch), ('unknown', True, True))
                # The same contradiction must hold when close precedes result.
                prefix[-2], prefix[-1] = prefix[-1], prefix[-2]
                for index, row in enumerate(prefix, 1): row['seq'] = index
                history = v2.reduce(c.grant, prefix)
                self.assertEqual((history.effect(), history.revoked, history.latch), ('unknown', True, True))

    def test_successful_write_close_before_result_does_not_latch(self):
        c = Chain().launch().successful(1).successful(2)
        prefix = c.rows[:-1]
        prefix[-2], prefix[-1] = prefix[-1], prefix[-2]
        for index, row in enumerate(prefix, 1): row['seq'] = index
        history = v2.reduce(c.grant, prefix)
        self.assertEqual((history.effect(), history.revoked, history.latch), ('applied', False, False))

    def test_successful_write_requires_reserved_before_identity(self):
        for before in (None, identity(99)):
            c = Chain().launch().successful(1).successful(2)
            row = next(r for r in c.rows if r['kind'] == 'worker-result' and r['value']['worker_ordinal'] == 2)
            row['value']['before'] = before
            with self.subTest(before=before), self.assertRaisesRegex(ContractError, 'write-result'):
                v2.reduce(c.grant, c.rows)

    def test_callback_completion_requires_its_worker_closure(self):
        c = Chain().launch().successful(1)
        c.rows = [r for r in c.rows if r['kind'] != 'worker-closed']
        for index, row in enumerate(c.rows, 1): row['seq'] = index
        with self.assertRaisesRegex(ContractError, 'completion-evidence'):
            v2.reduce(c.grant, c.rows)

    def test_forged_verifier_success_rejected_and_failure_revokes(self):
        c = Chain().launch().successful(1).successful(2).successful(3)
        result = next(r for r in c.rows if r['kind'] == 'worker-result' and r['value']['worker_ordinal'] == 3)
        result['value'].update(success=False, verifier_pass=False, reason='verifier_failed')
        with self.assertRaisesRegex(ContractError, 'completion-result'): v2.reduce(c.grant, c.rows)
        c.rows[-1]['value'].update(success=False, failure_code='verifier_failed')
        h = v2.reduce(c.grant, c.rows)
        self.assertEqual((len(h.completed_refs), h.effect(), h.revoked), (2, 'applied', True))
        c.reserve(4)
        with self.assertRaisesRegex(ContractError, 'authority-closed'): v2.reduce(c.grant, c.rows)

    def test_runtime_unknown_has_no_fabricated_callback(self):
        c = Chain().launch()
        c.add('effect-unknown', reason='closure_unconfirmed', callback_id=None)
        self.assertTrue(c.read().latch)
        c.rows[-1]['value']['callback_id'] = 1
        with self.assertRaisesRegex(ContractError, 'unknown-callback'):
            v2.reduce(c.grant, c.rows)

    def test_verifier_failure_cannot_claim_a_passing_result(self):
        c = Chain().launch().successful(1).successful(2).successful(3)
        row = next(r for r in c.rows if r['kind'] == 'worker-result' and r['value']['worker_ordinal'] == 3)
        row['value'].update(success=False, reason='worker_failed')
        with self.assertRaisesRegex(ContractError, 'verifier-result'):
            v2.reduce(c.grant, c.rows)

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


class ResolutionTests(unittest.TestCase):
    def test_preview_binds_process_absence_and_explicit_availability(self):
        c = Chain().launch().successful(1); c.reserve(2); c.intent(2, 'write')
        c.add('worker-started', worker_ordinal=2, pid=9012, birth=BIRTH)
        value = c.read().summary()
        with mock.patch.object(state, 'process_birth', return_value=''), mock.patch.object(state, 'group_absent', return_value=True), \
             mock.patch('hv2ref.official_recovery.document_observation', return_value=(identity(), b'')), \
             mock.patch('hv2ref.official_recovery.inspect', return_value='missing') as inspect:
            unchecked = v2.resolution_preview(value)
            inspect.assert_not_called()
            checked = v2.resolution_preview(value, host_control_root='/explicit/operator/root')
            self.assertEqual(unchecked['observation']['recovery_availability'], 'not_checked')
            self.assertEqual(checked['observation']['recovery_availability'], 'missing')
            self.assertNotEqual(unchecked['confirm_token'], checked['confirm_token'])
        with mock.patch.object(state, 'process_birth', return_value=BIRTH), mock.patch.object(state, 'group_absent', return_value=True), \
             self.assertRaisesRegex(ContractError, 'process-present-or-unconfirmed'):
            v2.resolution_preview(value)

    def test_null_birth_cannot_be_auto_closed_or_operator_resolved(self):
        c = Chain().launch()
        row = next(r for r in c.rows if r['kind'] == 'runtime-started')
        row['value']['birth'] = None
        h = v2.reduce(c.grant, c.rows)
        with self.assertRaisesRegex(ContractError, 'runtime-identity-unavailable'): h.identified_processes()
        c.close_runtime()
        with self.assertRaisesRegex(ContractError, 'runtime-closure'): v2.reduce(c.grant, c.rows)


class CapsuleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.target = Path(self.temp.name).resolve()
        (self.target / '.hrn/executions').mkdir(parents=True)
        self.root = self.target / '.hrn/executions' / SHA; self.root.mkdir(mode=0o700)
        self.chain = Chain(grant(str(self.target)))
        self.chain.terminal('revoked-before-launch')
        self.write()

    def write(self):
        for name, raw in (('grant.json', state.canonical(self.chain.grant)), ('journal.jsonl', b''.join(canonical(r) for r in self.chain.rows))):
            p = self.root / name; p.write_bytes(raw); p.chmod(0o600)

    def test_resolution_rejects_invalid_observation_before_durable_append(self):
        self.chain = Chain(grant(str(self.target)))
        self.write()
        path = self.root / 'journal.jsonl'; before = path.read_bytes()
        invalid = identity(); invalid['nlink'] = 2
        # In-process resolution path; lock/topology execution has separate integration coverage.
        with mock.patch('hv2ref.workspace.writer_guard', return_value=nullcontext()), \
             mock.patch('hv2ref.official_recovery.document_observation', return_value=(invalid, b'')):
            preview = state.resolution_preview(self.target, SHA)
            with self.assertRaises(ContractError):
                state.resolve(self.target, SHA, preview['confirm_token'])
        self.assertEqual(path.read_bytes(), before)
        self.assertEqual(state.read_capsule(self.target, SHA)['status'], 'incomplete')

    def test_closed_history_and_guard_need_no_external_root(self):
        value = state.read_capsule(self.target, SHA)
        self.assertEqual(value['status'], 'revoked-before-launch')
        self.assertTrue(value['revoked'])
        self.assertEqual(state.public_status(value)['recovery_availability'], 'not_checked')
        state.require_no_open(self.target)
        self.assertEqual(len(state.execution_truth(self.target)), 2)
        for p in self.root.iterdir(): p.chmod(0o644)
        state.require_no_open(self.target)

    def test_unexpected_payload_directory_alias_and_hardlink_fail_closed(self):
        extra = self.root / 'request.json'; extra.write_text('raw')
        with self.assertRaises(ContractError): state.require_no_open(self.target)
        extra.unlink(); extra.mkdir()
        with self.assertRaises(ContractError): state.require_no_open(self.target)
        extra.rmdir()
        p = self.root / 'grant.json'; p.rename(self.target / 'grant.json')
        p.symlink_to(self.target / 'grant.json')
        with self.assertRaises(ContractError): state.require_no_open(self.target)
        p.unlink(); os.link(self.target / 'grant.json', p)
        with self.assertRaises(ContractError): state.require_no_open(self.target)

    def test_unsupported_schema_and_raw_cancel_refuse(self):
        self.chain.grant['schema_version'] = 3; self.write()
        with self.assertRaises(ContractError): state.require_no_open(self.target)
        self.chain.grant['schema_version'] = 2; self.write()
        state.publish(self.root / 'cancel.json', {'grant': SHA, 'reason': 'RAW_CUSTOM_REASON'})
        with self.assertRaises(ContractError): state.require_no_open(self.target)

    def test_valid_prefix_after_failed_terminal_remains_blocked(self):
        self.chain.rows.pop(); self.write()
        value = state.read_capsule(self.target, SHA)
        self.assertEqual((value['status'], value['document_write_effect']), ('incomplete', 'none'))
        with self.assertRaises(ContractError): state.require_no_open(self.target)
        with (self.root / 'journal.jsonl').open('ab') as f: f.write(b'{')
        with self.assertRaises((ContractError, ValueError, HostRefusal)): state.require_no_open(self.target)

    def test_v1_closed_and_unknown_are_still_read_with_v1_rules(self):
        spec = {'target': str(self.target), 'request': {'worker_limit': 5}, 'documents': {'files': {}}}
        old_grant = state.digest(state.canonical(spec)); old_root = self.root.with_name(old_grant); old_root.mkdir(mode=0o700)
        state.publish(old_root / 'grant.json', {'record_type': 'official-execution-grant', 'schema_version': 1, 'grant': old_grant, 'spec': spec})
        c = Chain(); c.rows = []; c.add('granted', grant=old_grant); c.add('terminal', status='revoked-before-launch')
        p = old_root / 'journal.jsonl'; p.write_bytes(b''.join(canonical(r) for r in c.rows)); p.chmod(0o600)
        state.require_no_open(self.target)
        c.rows = c.rows[:1]; c.add('terminal', status='unknown')
        p.write_bytes(b''.join(canonical(r) for r in c.rows))
        self.assertEqual(state.read_capsule(self.target, old_grant)['status'], 'unknown')
        with self.assertRaises(ContractError): state.require_no_open(self.target)


if __name__ == '__main__':
    unittest.main()
