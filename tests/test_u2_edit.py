"""Edit contract, cross-consumer replay, and withheld-callback tests; no model calls."""
from copy import deepcopy
import importlib
import io
import json
import os
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from tests.fixtures.u2_edit import (host, edit, policy, native, publish, contract_on_disk,
                                    parent_and_admission, real_task, execution, baseline, snapshot_reader)

common = host.contracts
ops = importlib.import_module(host._package_name + '._macos_execution')
bounded = importlib.import_module(host._package_name + '.bounded_edit')
FIXTURE = Path(__file__).parent / 'fixtures/u2-edit-v59.json'


class EditContractTests(unittest.TestCase):
    def test_shared_contracts(self):
        self.assertEqual(policy.TEMPLATE_SHA256, 'bc61dc0e5e5300259a96bdaed6805402f64af39037859eb9449bb5bf78f0e697')
        for case in json.loads(FIXTURE.read_bytes())['contract_cases']:
            def bound(ref):
                value = case['documents'][ref['path']]
                common.require(common.digest(common.canonical(value)) == ref['sha256'], 'fixture-digest')
                return value
            with self.subTest(case=case['name']):
                if case['accepted']:
                    policy.contract(case['anchor'], bound)
                else:
                    with self.assertRaisesRegex(common.HostRefusal, case.get('error', '')):
                        policy.contract(case['anchor'], bound)

    def test_shared_journals_and_prefixes(self):
        f = json.loads(FIXTURE.read_bytes())
        budget = SimpleNamespace(anchor=f['anchor'], anchor_sha256=f['anchor_sha256'])
        for case in f['journal_cases']:
            with self.subTest(case=case['name']):
                if case['accepted']:
                    state = policy.budget_state(budget, case['rows'], case['now_ms'], validate_contract=False)
                    self.assertEqual(state['counts'], case['expected_counts'])
                    self.assertEqual(state['stopped'], case['stopped'])
                    self.assertEqual(state['terminal'], case['terminal'])
                else:
                    with self.assertRaisesRegex(common.HostRefusal, case.get('error', '')):
                        policy.budget_state(budget, case['rows'], case['now_ms'], validate_contract=False)
        good = f['journal_cases'][0]['rows']
        for length in range(1, len(good) + 1):
            policy.budget_state(budget, good[:length], 1_001_000, validate_contract=False)

    def test_closed_kind_and_resume_routes(self):
        addresses = ['1.1.1.1', policy.PEER]
        evidence = {'host': 'chatgpt.com', 'addresses': addresses, 'resolution_count': 1, 'selected_peer': policy.PEER}
        self.assertEqual(native.frozen_network_peer(59, addresses, evidence), policy.PEER)
        with self.assertRaises(common.HostRefusal):
            native.frozen_network_peer(59, addresses, {**evidence, 'selected_peer': '1.1.1.1'})
        f = json.loads(FIXTURE.read_bytes())
        b = object.__new__(native.Budget); b.anchor = f['anchor']
        self.assertEqual(b.execution_reserve_ms(), policy.RESERVE_MS)
        with self.assertRaisesRegex(common.HostRefusal, 'edit-resume-forbidden'):
            b.resume_check({}, 'unused')
        unknown = deepcopy(f['anchor']); unknown['kind'] = 'unknown'
        with self.assertRaises(common.HostRefusal): native.Budget._anchor_fields(unknown)
        unknown = deepcopy(f['anchor']); unknown['version'] = 60
        with self.assertRaises(common.HostRefusal): native.Budget._anchor_fields(unknown)
        s = object.__new__(native.LiveSession); s.budget = b
        with self.assertRaisesRegex(common.HostRefusal, 'dedicated-session'): s.launch()
        with self.assertRaisesRegex(common.HostRefusal, 'dedicated-iteration'): s.iterate()
        with self.assertRaises(common.HostRefusal):
            host.edit_only('resume', snapshot_reader=lambda *_: {}, baseline_reader=lambda *_: {})

    def test_sealed_stop_without_only_process_ended_is_rejected(self):
        f = json.loads(FIXTURE.read_bytes())
        rows = deepcopy(f['journal_cases'][0]['rows'])
        removed = [row for row in rows if row['event']['kind'] == 'process-ended']
        self.assertEqual(len(removed), 1)
        rows = [row for row in rows if row['event']['kind'] != 'process-ended']
        self.assertEqual([row['event']['kind'] for row in rows[-3:]], ['seal', 'candidate-receipt', 'execution-stop'])
        row = rows[-1]
        row['event']['seq'] -= 1
        row['event']['prev'] = rows[-2]['sha256']
        row['sha256'] = common.digest(common.wire_bytes(row['event']))
        budget = SimpleNamespace(anchor=f['anchor'], anchor_sha256=f['anchor_sha256'])
        with self.assertRaisesRegex(common.HostRefusal, '^edit-stop-terminal$'):
            policy.budget_state(budget, rows, 1_001_000, validate_contract=False)


class EditConsumptionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='edit-consumption-')
        self.addCleanup(self.tmp.cleanup); self.root = Path(self.tmp.name).resolve()

    def consume(self, anchor, ledger, lock, admission):
        adapter = edit if anchor['version'] == 59 else host.fresh_codex
        with patch.object(native.Budget, '_clock', return_value=1_001_000), patch.object(ops.time, 'time_ns', return_value=1_001_000_000_000), \
                patch.object(ops.MacExecution, 'continuous_ns', return_value=anchor['origin_monotonic_ns'] + (1_001_000 - anchor['origin_wall_ms']) * 1_000_000):
            return adapter.consume_activation(anchor, ledger_path=ledger.path, controller_lock_path=lock, admission=admission)

    def test_new_consumer_and_publication_failure_remain_consumed(self):
        for mode in ('normal', 'ledger-fsync', 'publication'):
            with self.subTest(mode=mode):
                root = self.root / mode; a = contract_on_disk(root)
                ledger, lock, admission = parent_and_admission(a, root)
                if mode == 'normal':
                    b = self.consume(a, ledger, lock, admission)
                    with patch.object(native.Budget, '_clock', return_value=1_001_000), patch.object(ops.time, 'time_ns', return_value=1_001_000_000_000):
                        self.assertEqual(b.read()['counts'], {'genesis': 1})
                else:
                    target = patch.object(common.os, 'fsync', side_effect=OSError('synthetic ledger')) if mode == 'ledger-fsync' else patch.object(edit, 'durable_private', side_effect=OSError('synthetic publication'))
                    with target, self.assertRaises(OSError): self.consume(a, ledger, lock, admission)
                    self.assertFalse(Path(a['run_directory']).exists())
                self.assertEqual(ledger.read()[-1]['kind'], 'edit-consumed')
                before = ledger.path.read_bytes()
                with self.assertRaises(common.HostRefusal): self.consume(a, ledger, lock, admission)
                self.assertEqual(ledger.path.read_bytes(), before)

    def test_both_real_consumers_reject_each_cross_kind_identifier(self):
        for old_version, new_version in ((58, 59), (59, 58)):
            for identifier in ('reservation_id', 'activation_sha256', 'run_directory', 'snapshot_sha256'):
                with self.subTest(old=old_version, new=new_version, identifier=identifier):
                    root = self.root / (str(old_version) + '-' + identifier); root.mkdir()
                    old = contract_on_disk(root / 'old', old_version)
                    ledger, lock, admission = parent_and_admission(old, root / 'old')
                    self.consume(old, ledger, lock, admission)
                    consumed = deepcopy(ledger.read()[-1]['value'])
                    new = contract_on_disk(root / 'new', new_version)
                    other, newlock, newadmission = parent_and_admission(new, root / 'new')
                    parent = deepcopy(other.rows[-1]['value'])
                    # Preserve a structurally valid historical row and collide one
                    # exact identifier. Both actual consumers scan this same ledger.
                    proposed = {'reservation_id': native.Budget.fresh_bound(new['activation'])['reservation_id'],
                                'activation_sha256': new['activation']['sha256'], 'run_directory': new['run_directory'],
                                'snapshot_sha256': new['accounting_snapshot']['sha256']}
                    consumed['reservation_id'] = 'historical-unique'
                    consumed['activation_sha256'] = '1' * 64
                    consumed['run_directory'] = '/synthetic/prior'
                    consumed['snapshot_sha256'] = '2' * 64
                    consumed[identifier] = proposed[identifier]
                    combined = common.EffectJournal(root / 'combined.jsonl', create=True)
                    combined.append('v58-consumed' if old_version == 58 else 'edit-consumed', consumed)
                    combined.append('edit-parent-reservation' if new_version == 59 else 'v58-parent-reservation', parent)
                    with self.assertRaisesRegex(common.HostRefusal, 'consumption-replay'):
                        self.consume(new, combined, newlock, newadmission)
                    self.assertFalse(Path(new['run_directory']).exists())

    def test_stale_snapshot_and_malformed_related_records_fail_closed(self):
        for version in (58, 59):
            for case in ('stale', 'torn-consumed', 'torn-parent', 'unknown-related'):
                with self.subTest(version=version, case=case):
                    root = self.root / (str(version) + '-' + case)
                    a = contract_on_disk(root, version)
                    original, lock, admission = parent_and_admission(a, root)
                    ledger = common.EffectJournal(root / 'test-ledger.jsonl', create=True)
                    if case == 'stale':
                        allocation = policy.ALLOCATION if version == 59 else host.fresh_codex.policy.ALLOCATION
                        before = {k: 0 for k in allocation}
                        value = {'version': 1, 'activation_sha256': '1' * 64, 'reservation_id': 'prior',
                                 'run_directory': '/synthetic/prior', 'allocation': allocation, 'snapshot_sha256': '2' * 64,
                                 'ledger_row_sha256': '3' * 64, 'counts_before': before, 'counts_after': allocation}
                        ledger.append('edit-consumed' if version == 59 else 'v58-consumed', value)
                    else:
                        ledger.append({'torn-consumed': 'edit-consumed', 'torn-parent': 'v58-parent-reservation',
                                       'unknown-related': 'edit-unknown'}[case], {'reservation_id': 'prior'})
                    ledger.append(original.rows[-1]['kind'], original.rows[-1]['value'])
                    with self.assertRaises(common.HostRefusal): self.consume(a, ledger, lock, admission)
                    self.assertFalse(Path(a['run_directory']).exists())


class EditCallbackTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='edit-callback-')
        self.addCleanup(self.tmp.cleanup); self.root = Path(self.tmp.name).resolve()

    def session(self):
        f = json.loads(FIXTURE.read_bytes()); s = object.__new__(edit.EditSession)
        s.run = self.root; s.closed = s.withheld = False; s.start = policy.START; s.phase = policy.PHASE; s.known = {}
        s.budget = Mock(); s.budget.anchor = f['anchor']; s.budget.anchor_sha256 = f['anchor_sha256']
        s.budget.read.return_value = {'prev': 'd' * 64, 'terminal': 'sealed-terminated'}
        subject = {'thread': 'thread', 'turn': 'turn', 'plan': 'plan', 'call': 'call'}
        s.admission = Mock(); s.admission.callback.return_value = ('u2_verify', {'verifier_id': 'DOC-CLAIMS'})
        s.admission.dispatch_subject.return_value = subject
        s.admission.turn = 'turn'; s.thread = 'thread'
        s.gate = Mock(); s.gate.cfg = {'identity': {'synthetic': True}}; s.gate.completed = 5
        s.gate.dispatch.return_value = {'ok': True, 'result': {'pass': True}, 'request': {'sha256': '1' * 64},
            'terminal': {'sha256': '2' * 64}, 'worker_result': {'tool': 'u2_verify', 'result_sha256': '3' * 64,
                'result_identity': '4' * 64, 'oracle_sha256': '5' * 64}}
        s.gate.seal.return_value = '4' * 64
        s.documents = SimpleNamespace(oracle_sha256='5' * 64, active=None)
        s.os = Mock(); s.os.stop_owned.return_value = True
        s.fd_controller = SimpleNamespace(closed=False, proxy=None, thread=None, leases={}, lease_bindings={}, revoke=Mock())
        s.fd_controller.close = lambda: setattr(s.fd_controller, 'closed', True)
        s.proxy_identity = Mock(return_value='p'); s.check_auth_metadata = Mock()
        client = object.__new__(native.LiveClient)
        client.failed = False; client.event_counts = {}; client.events = []; client.rpc_stage = 'turn/startPrepared'
        client.callback = s.callback; client.send = Mock(); client.selector = Mock()
        client.process = SimpleNamespace(stdin=io.BytesIO(), stdout=io.BytesIO(), stderr=io.BytesIO())
        s.client = client; s.spawned_process = client.process
        s.spawn_attempted = True
        message = {'method': 'item/tool/call', 'id': 1, 'params': {'callId': 'call'}}
        return s, message

    def test_final_result_receipt_precedes_termination_and_no_response(self):
        s, message = self.session()
        def stop(*_):
            self.assertTrue((self.root / 'candidate-receipt.json').is_file())
            self.assertEqual([c.args[0] for c in s.budget.reserve.call_args_list], ['worker-result', 'seal', 'candidate-receipt'])
            return True
        s.os.stop_owned.side_effect = stop
        with patch.object(native.LiveSession, 'turn', side_effect=lambda *_: s.client.event(message)):
            result = s.turn([])
        self.assertEqual(result['status'], 'sealed-terminated')
        s.client.send.assert_not_called()
        self.assertEqual([c.args[0] for c in s.budget.reserve.call_args_list],
                         ['worker-result', 'seal', 'candidate-receipt', 'process-ended', 'execution-stop'])
        self.assertTrue(s.cleanup['complete']); self.assertTrue(s.client.process.stdin.closed)
        with self.assertRaises(common.HostRefusal): s.turn([])

    def test_receipt_failure_and_cleanup_failure_never_report_completion(self):
        for case in ('receipt', 'cleanup'):
            with self.subTest(case=case):
                s, message = self.session()
                s.run = self.root / case; s.run.mkdir()
                if case == 'cleanup': s.os.stop_owned.return_value = False
                def store(path, value):
                    if case == 'receipt' and Path(path).name == 'candidate-receipt.json': raise OSError('synthetic persistence')
                    common.durable_private(path, value)
                with patch.object(edit, 'durable_private', side_effect=store), patch.object(native.LiveSession, 'turn', side_effect=lambda *_: s.client.event(message)):
                    with self.assertRaises((OSError, common.HostRefusal)): s.turn([])
                s.client.send.assert_not_called()
                self.assertNotIn('process-ended', [c.args[0] for c in s.budget.reserve.call_args_list])
                self.assertTrue(s.closed)


class EditPreparationTests(unittest.TestCase):
    def test_nine_real_inputs_refuse_at_read_limit(self):
        resources = json.loads(Path(os.environ['EDIT_TEST_RESOURCES']).read_bytes())
        with tempfile.TemporaryDirectory(prefix='edit-nine-') as name:
            root = Path(name).resolve()
            cfg, _, _, _ = real_task(root / 'task', 'Nine', 9, resources)
            self.assertEqual(len(cfg['read_ids']), 9)
            self.assertEqual(set(cfg['read_ids']), set(cfg['documents']['files']))
            exe = execution(root / 'task', 'Nine', resources)
            with self.assertRaisesRegex(common.HostRefusal, '^edit-read-scope$'):
                host.edit_only('prepare', cfg=cfg, execution=exe, destination=root / 'prepared',
                               snapshot_reader=snapshot_reader, baseline_reader=baseline)
            self.assertFalse((root / 'prepared').exists())

    def test_preparation_binds_actual_inputs_without_consumption(self):
        resources = json.loads(Path(os.environ['EDIT_TEST_RESOURCES']).read_bytes())
        with tempfile.TemporaryDirectory(prefix='edit-prepare-positive-') as name:
            root = Path(name).resolve()
            cfg, _, _, _ = real_task(root / 'task', 'Prepared', 2, resources)
            exe = execution(root / 'task', 'Prepared', resources)
            prepared = host.edit_only('prepare', cfg=cfg, execution=exe, destination=root / 'prepared',
                                     snapshot_reader=snapshot_reader, baseline_reader=baseline)
            anchor = prepared['anchor']
            self.assertEqual(anchor['input_identity'], common.digest(common.canonical(cfg)))
            self.assertEqual(anchor['edit_scope']['read_ids'], cfg['read_ids'])
            self.assertEqual(anchor['edit_scope']['output']['path'], cfg['documents']['files']['PreparedOutput']['path'])
            self.assertEqual(native.Budget.fresh_bound(prepared['task']), cfg)
            self.assertFalse(Path(anchor['run_directory']).exists())
            self.assertFalse(Path(anchor['consumption']['path']).exists())
            tools = json.loads((Path(edit.__file__).parents[1] / 'tool-profile-v2.json').read_bytes())
            self.assertEqual(prepared['blueprint']['dynamic_tools'], tools)
            self.assertTrue(all(tool['type'] == 'function' for tool in tools))
            # Test the production binding before any transport or write: neither
            # stripped tags nor extra capabilities may become a runtime spec.
            budget = SimpleNamespace(anchor=anchor, fresh_bound=native.Budget.fresh_bound)
            for case in ('missing-type', 'wrong-type', 'extra-tool'):
                bad = deepcopy(prepared)
                if case == 'missing-type': bad['blueprint']['dynamic_tools'][0].pop('type')
                elif case == 'wrong-type': bad['blueprint']['dynamic_tools'][0]['type'] = 'custom'
                else: bad['blueprint']['dynamic_tools'].append(deepcopy(tools[0]))
                with self.subTest(case=case), patch.object(policy, 'contract'), self.assertRaisesRegex(common.HostRefusal, '^edit-blueprint-tools$'):
                    edit.materialize_runtime(bad, budget, {})
            self.assertFalse((Path(prepared['blueprint']['root']) / 'spec.json').exists())

    def test_negative_inputs_refuse_before_activation(self):
        resources_path = os.environ.get('EDIT_TEST_RESOURCES')
        self.assertIsNotNone(resources_path, 'bounded verification runner must supply fixed resources')
        resources = json.loads(Path(resources_path).read_bytes())
        with tempfile.TemporaryDirectory(prefix='edit-prepare-') as name:
            root = Path(name).resolve()
            cfg, _, _, _ = real_task(root / 'task', 'Negative', 2, resources)
            exe = execution(root / 'task', 'Negative', resources)
            for case in ('two-outputs', 'model', 'kind', 'envelope', 'baseline', 'reordered-pack'):
                with self.subTest(case=case):
                    bad, x = deepcopy(cfg), deepcopy(exe)
                    if case == 'two-outputs': bad['documents']['outputs'].append(bad['read_ids'][1])
                    elif case == 'model': x['model'] = 'unsupported'
                    elif case == 'kind': x['kind'] = 'unknown'
                    elif case == 'envelope': bad['identity']['approval'] = 'owner-edit-' + 'x' * 65_000; x['owner_message_id'] = 'x' * 65_000
                    elif case == 'baseline': bad['worker_base_commit'] = '0' * 40
                    else: bad['read_ids'].reverse()
                    destination = root / ('prepared-' + case)
                    with self.assertRaises(common.HostRefusal):
                        host.edit_only('prepare', cfg=bad, execution=x, destination=destination,
                                       snapshot_reader=snapshot_reader, baseline_reader=baseline)
                    self.assertFalse(destination.exists())


if __name__ == '__main__':
    unittest.main()
