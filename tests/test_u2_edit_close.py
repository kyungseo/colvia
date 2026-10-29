"""Real edit Budget and product turn/close; transport, OS and host effects are fake.

These tests do not start the native runtime or qualify live process termination.
Actual worker effects are covered by the separate two-task offline verification.
"""
from copy import deepcopy
import io
import json
import os
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from tests.fixtures.u2_edit import host, edit, policy, native, publish, contract_on_disk, parent_and_admission
from tests.test_u2_edit import common, bounded, ops, FIXTURE


class EditClockAdmissionTests(unittest.TestCase):
    def test_expiry_and_clock_drift_do_not_consume(self):
        with tempfile.TemporaryDirectory(prefix='edit-clock-') as name:
            root = Path(name).resolve()
            for case in ('expired', 'margin', 'drift', 'admitted'):
                with self.subTest(case=case):
                    a = contract_on_disk(root / case)
                    ledger, lock, admission = parent_and_admission(a, root / case)
                    expiry = edit.runtime_expiry(a)
                    now = expiry if case == 'expired' else expiry - policy.STARTUP_MARGIN_MS
                    if case == 'admitted': now -= 1
                    continuous = a['origin_monotonic_ns'] + (now - a['origin_wall_ms']) * 1_000_000
                    if case == 'drift': continuous += 3_000_000_000
                    before = ledger.path.read_bytes()
                    with patch.object(ops.time, 'time_ns', return_value=now * 1_000_000), \
                            patch.object(ops.MacExecution, 'continuous_ns', return_value=continuous):
                        if case == 'admitted':
                            b = edit.consume_activation(a, ledger_path=ledger.path, controller_lock_path=lock, admission=admission)
                            self.assertEqual(b.read()['counts'], {'genesis': 1})
                        else:
                            reason = 'edit-consumption-clock-drift' if case == 'drift' else 'edit-consumption-expired'
                            with self.assertRaisesRegex(common.HostRefusal, '^' + reason + '$'):
                                edit.consume_activation(a, ledger_path=ledger.path, controller_lock_path=lock, admission=admission)
                            self.assertEqual(ledger.path.read_bytes(), before)
                            self.assertFalse(Path(a['run_directory']).exists())


class EditBudgetCloseTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='edit-real-budget-')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()
        self.enterContext(patch.object(ops.time, 'time_ns', return_value=1_001_000_000_000))
        self.enterContext(patch.object(ops.MacExecution, 'continuous_ns', return_value=1_100_000_000))

    def make_session(self, name, *, prefix=True):
        root = self.root / name; root.mkdir()
        a = contract_on_disk(root / 'contract')
        ledger, lock, admission = parent_and_admission(a, root / 'contract')
        budget = edit.consume_activation(a, ledger_path=ledger.path, controller_lock_path=lock, admission=admission)
        f = json.loads(FIXTURE.read_bytes())
        last_input = [i for i, row in enumerate(f['journal_cases'][0]['rows']) if row['event']['kind'] == 'input'][-1]
        rows = f['journal_cases'][0]['rows'][1:last_input] if prefix else f['journal_cases'][0]['rows'][1:2]
        run = root / 'run'; run.mkdir()
        owner = root / 'owner.txt'; owner.write_text('Synthetic approved edit.'); owner.chmod(0o600)
        cfg = {'identity': {'actor': 'synthetic-editor'}, 'owner_input': str(owner),
               'owner_input_sha256': common.digest(owner.read_bytes())}
        tools = json.loads((Path(edit.__file__).parents[1] / 'tool-profile-v2.json').read_text())
        runtime = {'input_template_identity': a['input_identity'], 'source_identity': a['source_identity'],
                   'candidate': a['candidate'], 'dynamic_tools': tools, 'expires_unix_ms': 2_700_000,
                   'phase': policy.PHASE, 'start': policy.START, 'journal_anchor_sha256': budget.anchor_sha256}
        ref = publish(run / 'spec.json', runtime)
        spec = {'command': policy.PHASE, 'phase': policy.PHASE, 'start': policy.START, 'run': str(run),
                'runtime': {'spec': ref['path']}, 'budget_directory': str(budget.directory),
                'budget_anchor_sha256': budget.anchor_sha256, 'task': publish(root / 'task.json', cfg),
                'owner_input': cfg['owner_input'], 'owner_input_sha256': cfg['owner_input_sha256']}
        gate = object.__new__(bounded.BoundedEditHost)
        gate.cfg = cfg; gate.controller = SimpleNamespace(active=None, oracle_sha256='a' * 64)
        gate.completed = 5; gate.pending = None; gate.lock = Mock(); gate.check_core = Mock()
        gate.dispatch = Mock(return_value={'ok': True, 'result': {'pass': True},
            'request': {'sha256': '6' * 64}, 'terminal': {'sha256': '5' * 64},
            'worker_result': {'tool': 'u2_verify', 'result_sha256': '7' * 64,
                              'result_identity': '9' * 64, 'oracle_sha256': 'a' * 64}})
        gate.seal = Mock(return_value='9' * 64)
        fd = SimpleNamespace(closed=False, proxy=None, thread=None, leases={}, lease_bindings={}, revoke=Mock())
        fd.close = lambda: setattr(fd, 'closed', True)
        s = edit.EditSession(spec, budget, run, gate=gate, fd_controller=fd)
        for row in rows:
            e = deepcopy(row['event'])
            if e['kind'] == 'start': e['subject']['execution_binding']['epoch_sha256'] = budget.anchor_sha256
            budget.reserve(e['kind'], e['subject'], e['phase'], e['start'])
        s.thread = 'thread-vector'; s.proxy_identity = Mock(return_value='b' * 64)
        s.execution_binding = {'launch_mode': a['launch_mode'], 'launch_contract_sha256': a['launch_contract_sha256'],
            'epoch_sha256': budget.anchor_sha256, 'approval': a['approval'], 'direct_tool_policy': a['direct_tool_policy']}
        return s, spec, fd, gate

    def attach_fake_transport(self, s, *, absent=True):
        client = object.__new__(native.LiveClient)
        client.failed = False; client.event_counts = {}; client.events = []; client.rpc_stage = 'turn/startPrepared'
        client.callback = s.callback; client.send = Mock(); client.selector = Mock()
        client.process = SimpleNamespace(stdin=io.BytesIO(), stdout=io.BytesIO(), stderr=io.BytesIO())
        s.client = client; s.spawned_process = client.process; s.spawn_attempted = True
        s.os = SimpleNamespace(stop_owned=Mock(return_value=absent), observe_owned=Mock(return_value={}))
        def request(method, params):
            if method == 'turn/prepare':
                inputs = params['input']; entries = []
                for t in s.admission.tools:
                    spec = {'type': 'function', 'name': t['name'], 'description': t['description'],
                            'strict': False, 'parameters': native.native_document_schema(t['inputSchema'])}
                    entries.append({'name': t['name'], 'origin': 'dynamic', 'namespace': 'functions',
                        'exposure': 'direct', 'implementation': 'synthetic::DynamicToolHandler', 'spec': spec})
                envelope = {'entries': entries, 'model_specs': [e['spec'] for e in entries], 'tool_mode': 'direct',
                    'namespaces': [], 'policy': {'expose_additional_permissions': False, 'require_managed_sandbox': False,
                        'require_unified_exec': False, 'allowed_tools': [{'namespace': None, 'name': t['name']} for t in s.admission.tools]}}
                return {'handle': 'synthetic-handle', 'manifest': {'version': 1, 'planId': 'plan-4',
                    'sourceIdentity': s.admission.source, 'buildIdentity': 'sha256:' + s.admission.candidate,
                    'toolEnvelope': envelope, 'snapshot': {'initial_input': inputs,
                        'history_binding': {'input_template': s.admission.template, 'input_sha256': common.digest(common.wire_bytes(inputs)),
                            'count': 0, 'sha256': 'd' * 64},
                        'context': {'execution_binding': s.execution_binding, 'model': {'slug': 'gpt-6-astra'},
                            'reasoning_effort': 'xhigh', 'wire_profile': {'api': 'responses_http', 'include_internal': False,
                                'compression': 'none', 'authentication': 'native_read_only'}}}}}
            self.assertEqual(method, 'turn/startPrepared')
            subject = {'thread': s.thread, 'plan': 'plan-4', 'turn': 'turn-4'}
            s.budget.reserve('turn', {'thread': s.thread, 'plan': 'plan-4'}, policy.PHASE, policy.START)
            s.budget.reserve('generation', {**subject, 'generation': 1}, policy.PHASE, policy.START)
            s.budget.reserve('dispatch', {**subject, 'call': 'call-4'}, policy.PHASE, policy.START)
            return {'turn': {'id': 'turn-4'}}
        client.request = request
        client.receive = lambda: {'method': 'item/tool/call', 'id': 7, 'params': {'threadId': s.thread, 'turnId': 'turn-4',
            'callId': 'call-4', 'namespace': None, 'tool': 'u2_verify', 'arguments': {'verifier_id': 'DOC-CLAIMS'}}}
        s.check_auth_metadata = Mock()
        return client

    def test_rpc_refusal_metadata_survives_close_without_response_content(self):
        secret = 'synthetic-token-and-account@example.invalid'
        cases = {'error': {'id': 1, 'error': {'code': -32602, 'message': secret, 'data': secret}},
                 'identity': {'id': 2, 'result': {}}, 'result': {'id': 1, 'result': []}}
        for name, response in cases.items():
            with self.subTest(case=name):
                s, _, _, _ = self.make_session('rpc-' + name, prefix=False)
                client = self.attach_fake_transport(s)
                client.sequence = 0
                client.receive = lambda: response
                try:
                    native.LiveClient.request(client, 'thread/start', {'ephemeral': True, 'dynamicTools': s.admission.tools})
                except common.HostRefusal as cause:
                    s.close(primary_error=cause)
                else:
                    self.fail('invalid RPC response accepted')
                raw = (s.run / 'edit-close.json').read_text()
                metadata = json.loads(raw)
                self.assertNotIn(secret, raw)
                self.assertEqual(metadata['rpc_failure'], {'method': 'thread/start', 'stage': 'thread/start',
                    'id_matches': name != 'identity', 'has_error': name == 'error',
                    'error_code': -32602 if name == 'error' else None,
                    'error_message_sha256': common.digest(secret.encode()) if name == 'error' else None})
                self.assertEqual(metadata['primary_error']['code'], 'RPC refused or identity drift')
                self.assertTrue(metadata['complete']); self.assertIsNone(metadata['terminal'])
                self.assertTrue(s.budget.read()['stopped'])
                self.assertNotIn('input', s.budget.read()['counts'])
                s.close()
                self.assertEqual((s.run / 'edit-close.json').read_text(), raw)

    def test_rpc_metadata_rejects_unbounded_or_unknown_fields(self):
        self.assertIsNone(edit.rpc_failure_metadata(None))
        value = {'method': 'secret', 'stage': ['secret'], 'id_matches': 1, 'has_error': 'secret',
                 'error_code': 2 ** 100, 'error_message_sha256': 'secret', 'response': 'secret'}
        self.assertEqual(edit.rpc_failure_metadata(SimpleNamespace(rpc_failure=value)),
                         {key: None for key in value if key != 'response'})

    def test_product_turn_bind_callback_close_with_real_budget(self):
        s, _, _, _ = self.make_session('success')
        client = self.attach_fake_transport(s)
        result = s.turn([{'type': 'text', 'text': 'Synthetic final verifier.', 'text_elements': []}])
        self.assertEqual(result['status'], 'sealed-terminated')
        state = s.budget.read()
        self.assertEqual(state['terminal'], 'sealed-terminated'); self.assertEqual(state['pending'], [])
        self.assertEqual(state['receipt']['sha256'], result['receipt_sha256'])
        self.assertTrue(s.cleanup['complete']); client.send.assert_not_called()
        self.assertEqual(json.loads((s.run / 'edit-close.json').read_text())['terminal'], 'sealed-terminated')

    def test_unknown_process_absence_and_verifier_failure_are_not_terminal(self):
        for case in ('unknown-absence', 'verifier-failed'):
            with self.subTest(case=case):
                s, _, _, gate = self.make_session(case)
                client = self.attach_fake_transport(s, absent=case != 'unknown-absence')
                if case == 'verifier-failed': gate.dispatch.return_value['result']['pass'] = False
                reason = 'edit-process-or-lease-unknown' if case == 'unknown-absence' else 'edit-verifier-failed-no-response'
                with self.assertRaisesRegex(common.HostRefusal, reason):
                    s.turn([{'type': 'text', 'text': 'Synthetic final verifier.', 'text_elements': []}])
                state = s.budget.read()
                self.assertIsNone(state['terminal']); self.assertNotIn('process-ended', state['counts'])
                client.send.assert_not_called()
                if case == 'verifier-failed':
                    self.assertTrue(state['stopped']); self.assertEqual(state['counts']['worker-result'], 5)
                    self.assertNotIn('host-refusal', state['counts']); self.assertNotIn('seal', state['counts'])
                before = (s.run / 'edit-close.json').read_bytes()
                s.close()  # Repeated close must not replace the first failure.
                self.assertEqual((s.run / 'edit-close.json').read_bytes(), before)

    def test_pre_spawn_and_gate_construction_failure_stop_epoch_and_preserve_cause(self):
        for case in ('gate-construction', 'before-spawn'):
            with self.subTest(case=case):
                s, spec, fd, gate = self.make_session(case, prefix=False)
                cause = common.HostRefusal('synthetic-core-drift')
                gate.check_core.side_effect = cause
                factory = patch.object(edit, 'BoundedEditHost', side_effect=cause) if case == 'gate-construction' else patch.object(edit, 'BoundedEditHost', return_value=gate)
                with factory, patch.object(edit, 'EditSession', return_value=s), self.assertRaisesRegex(common.HostRefusal, '^synthetic-core-drift$') as raised:
                    edit.run_edit(spec, fd_controller=fd, snapshot_reader=Mock(), baseline_reader=Mock())
                self.assertIs(raised.exception, cause)
                state = s.budget.read()
                self.assertTrue(state['stopped']); self.assertIsNone(state['terminal'])
                self.assertEqual(state['events'][-1]['subject']['reason'], 'failed')
                self.assertIsNone(s.spawned_process); self.assertFalse(s.spawn_attempted)
                metadata = json.loads((s.run / 'edit-close.json').read_text())
                self.assertEqual(metadata['primary_error']['code'], 'synthetic-core-drift')
                with self.assertRaisesRegex(common.HostRefusal, '^edit-execution-stopped$'):
                    edit.run_edit(spec, fd_controller=fd, snapshot_reader=Mock(), baseline_reader=Mock())

    def test_unknown_epoch_reentry_and_direct_cleanup_never_claim_absence(self):
        s, spec, fd, gate = self.make_session('unknown-reentry')
        self.attach_fake_transport(s, absent=False)
        with self.assertRaisesRegex(common.HostRefusal, '^edit-process-or-lease-unknown$'):
            s.turn([{'type': 'text', 'text': 'Synthetic final verifier.', 'text_elements': []}])
        journal = s.budget.directory / 'journal.jsonl'
        before = journal.read_bytes()
        with patch.object(edit, 'BoundedEditHost') as factory, patch.object(edit, 'close_unstarted') as close:
            with self.assertRaisesRegex(common.HostRefusal, '^edit-entry-already-started$'):
                edit.run_edit(spec, fd_controller=fd, snapshot_reader=Mock(), baseline_reader=Mock())
            factory.assert_not_called(); close.assert_not_called()
        with self.assertRaisesRegex(common.HostRefusal, '^edit-session-already-started$'):
            edit.EditSession(spec, s.budget, s.run, gate=gate, fd_controller=fd)
        other = self.root / 'direct-close'; other.mkdir()
        edit.close_unstarted(s.budget, fd, None, other, common.HostRefusal('synthetic-original-error'))
        metadata = json.loads((other / 'edit-close.json').read_text())
        self.assertFalse(metadata['complete'])
        self.assertEqual(metadata['cleanup_errors'][0]['code'], 'edit-prior-start-absence-unknown')
        self.assertEqual(journal.read_bytes(), before)
        self.assertNotIn('execution-stop', s.budget.read()['counts'])


if __name__ == '__main__':
    unittest.main()
