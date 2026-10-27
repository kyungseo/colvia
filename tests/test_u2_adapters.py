"""Focused source contracts. Mocks are not native runtime qualification."""
from copy import deepcopy
import importlib
import importlib.util
import io
import json
import os
from pathlib import Path
import tempfile
import threading
import time
import unittest
from unittest.mock import Mock, patch
import uuid

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location('u2_adapter_test_host', ROOT / 'docs/development/verification/u2-host/host.py')
host = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(host)
common, native = host.contracts, host.claude_code
relay = importlib.import_module(native.__package__ + '.claude_relay')


class ReadHostTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='u2-adapters-')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()
        doc = self.root / 'reference.md'
        doc.write_text('Synthetic source only.\n')
        record = host.file_record(doc)[0]
        self.snapshot = {'home': 'home-synthetic', 'work': 'work-synthetic', 'state': 'completed',
                         'result_refs': {'manifest': {'id': 'result', 'sha256': 'a' * 64}},
                         'intent_ref': {'id': 'intent', 'sha256': 'b' * 64},
                         'continuation': {'effective_choice': {'kind': 'proposal'}, 'pending': None}}
        identity = {'approval': 'synthetic-approval', 'home': self.snapshot['home'], 'work': self.snapshot['work'],
            'actor': 'reader-synthetic', 'action': 'read-verify-only', 'scope_sha256': host.digest(host.canonical({'Reference': record})),
            'result_sha256': host.digest(host.canonical(self.snapshot['result_refs'])),
            'intent_sha256': host.digest(host.canonical(self.snapshot['intent_ref'])), 'grant': 'none; authority tools excluded'}
        self.cfg = {'core_project': str(self.root), 'core_snapshot_sha256': host.digest(host.canonical(self.snapshot)),
            'identity': identity, 'identity_sha256': host.digest(host.canonical(identity)),
            'documents': {'files': {'Reference': record}, 'outputs': []}, 'request_limit': 4, 'effect_limit': 4,
            'runtime_limits': {'native-start': 2, 'host-input': 4, 'bridge-request': 4}}
        self.reader = Mock(side_effect=lambda project, work: deepcopy(self.snapshot))

    def create(self, name, *, cfg=None, resume=False):
        cfg = cfg or self.cfg
        gate = common.ReadOnlyHost(cfg, host.digest(host.canonical(cfg)), self.root / name, self.reader,
                                   time.monotonic() + 60, resume=resume, worker=False)
        self.addCleanup(gate.close)
        gate.controller = Mock()
        gate.controller.dispatch.return_value = {'files': [{'file_id': 'Reference', 'content': 'Synthetic source only.\n'}]}
        return gate

    def envelope(self, gate, **changes):
        return {'session': gate.session, 'step': gate.step, 'call_id': 'call-1', 'tool': 'u2_read_file',
                'arguments': {'file_ids': ['Reference']}, 'identity': deepcopy(self.cfg['identity']), **changes}

    def test_read_result_binding_and_duplicate_after_fresh_host(self):
        gate = self.create('read')
        gate.open_step('session-1', 'step-1')
        result = gate.dispatch(self.envelope(gate))
        self.assertTrue(result['ok'])
        self.assertEqual(gate.effects, 1)
        gate.stop()
        gate.deadline = time.monotonic() - 1
        recovery = gate.recovery()  # Evidence remains readable after the execution deadline.
        self.assertEqual((recovery['requests'], recovery['effects'], recovery['pending']), (1, 1, None))
        gate.close()
        fresh = self.create('read', resume=True)
        self.assertEqual((fresh.requests, fresh.effects), (1, 1))
        with self.assertRaisesRegex(host.HostRefusal, 'step-reuse'):
            fresh.open_step('session-1', 'step-1')
        fresh.open_step('session-1', 'step-2')
        self.assertEqual(fresh.dispatch(self.envelope(fresh)), {'ok': False, 'code': 'duplicate-call'})
        fresh.controller.dispatch.assert_not_called()

    def test_identity_scope_and_session_refuse_before_worker(self):
        for name in ('actor', 'result', 'scope', 'session'):
            with self.subTest(name=name):
                gate = self.create(name)
                gate.open_step('session', 'step')
                envelope = self.envelope(gate)
                if name == 'actor': envelope['identity']['actor'] = 'owner'
                if name == 'result': envelope['identity']['result_sha256'] = 'f' * 64
                if name == 'scope': envelope['arguments'] = {'file_ids': ['Outside']}
                if name == 'session': envelope['session'] = 'foreign'
                result = gate.dispatch(envelope)
                self.assertFalse(result['ok'])
                self.assertEqual(gate.requests, 1)
                self.assertEqual(gate.effects, 0)
                gate.controller.dispatch.assert_not_called()
                self.assertEqual(gate.journal.rows[-2]['kind'], 'request')

    def test_fsync_failure_never_reaches_worker(self):
        gate = self.create('fsync')
        gate.open_step('session', 'step')
        with patch.object(common.os, 'fsync', side_effect=OSError('synthetic persistence failure')):
            with self.assertRaises(OSError):
                gate.dispatch(self.envelope(gate))
        self.assertTrue(gate.stopped)
        self.assertTrue(gate.journal.failed)
        gate.controller.dispatch.assert_not_called()

    def test_concurrent_calls_share_one_effect_slot(self):
        gate = self.create('concurrent')
        gate.open_step('session', 'step')
        barrier = threading.Barrier(3)
        outcomes, errors = [], []
        def call(number):
            try:
                barrier.wait()
                outcomes.append(gate.dispatch(self.envelope(gate, call_id='call-' + str(number))))
            except BaseException as error:
                errors.append(error)
        threads = [threading.Thread(target=call, args=(n,)) for n in (1, 2)]
        for thread in threads: thread.start()
        barrier.wait()
        for thread in threads:
            thread.join(5)
            self.assertFalse(thread.is_alive())
        self.assertEqual(errors, [])
        self.assertEqual(sum(result['ok'] for result in outcomes), 1)
        self.assertEqual((gate.requests, gate.effects), (2, 1))
        gate.controller.dispatch.assert_called_once()

    def test_stop_and_revoke_close_effects(self):
        for name in ('stop', 'revoke'):
            gate = self.create(name)
            gate.open_step('session', 'step')
            getattr(gate, name)()
            self.assertEqual(gate.dispatch(self.envelope(gate)), {'ok': False, 'code': 'closed-or-revoked'})
            gate.controller.dispatch.assert_not_called()
            if name == 'revoke':
                gate.stop(); gate.close()
                with self.assertRaisesRegex(host.HostRefusal, 'resume-not-safely-stopped'):
                    self.create(name, resume=True)

    def test_unknown_worker_effect_survives_stop_and_refuses_resume(self):
        gate = self.create('unknown')
        gate.open_step('session', 'step')
        gate.controller.dispatch.side_effect = host.HostRefusal('synthetic worker failure')
        self.assertFalse(gate.dispatch(self.envelope(gate))['ok'])
        self.assertIsNotNone(gate.pending)
        gate.stop(); gate.close()
        with self.assertRaises(host.HostRefusal):
            self.create('unknown', resume=True)

    def test_runtime_counts_and_config_are_not_reset_by_fresh_host(self):
        cfg = deepcopy(self.cfg)
        cfg['runtime_limits'] = {'native-start': 1, 'host-input': 1, 'bridge-request': 1}
        gate = self.create('budget', cfg=cfg)
        gate.reserve_runtime('native-start', {'session': 'native-1'})
        gate.reserve_runtime('host-input', {'session': 'native-1', 'step': 'input-1'})
        gate.reserve_runtime('bridge-request', {'session': 'native-1', 'request_id': 1})
        gate.stop()
        with self.assertRaisesRegex(host.HostRefusal, 'recovery-not-stopped'):
            gate.recovery()
        gate.native_stopped('native-1', True)
        gate.close()
        fresh = self.create('budget', cfg=cfg, resume=True)
        self.assertEqual(fresh.runtime_counts, cfg['runtime_limits'])
        before = fresh.journal.path.read_bytes()
        for kind in common.ReadOnlyHost.RUNTIME_KINDS:
            with self.assertRaisesRegex(host.HostRefusal, 'runtime-budget'):
                fresh.reserve_runtime(kind, {'session': 'native-2'})
        self.assertEqual(fresh.journal.path.read_bytes(), before)
        fresh.close()
        changed = deepcopy(cfg); changed['runtime_limits']['native-start'] = 2
        with self.assertRaisesRegex(host.HostRefusal, 'resume-anchor'):
            self.create('budget', cfg=changed, resume=True)

    def test_missing_partial_aliased_journal_and_concurrent_host_refuse(self):
        gate = self.create('journal')
        with self.assertRaises(host.HostRefusal):
            self.create('journal', resume=True)
        gate.stop(); gate.close()
        path = gate.journal.path
        original = path.read_bytes()
        path.write_bytes(original[:-1])
        with self.assertRaisesRegex(host.HostRefusal, 'journal-partial'):
            self.create('journal', resume=True)
        path.write_bytes(original)
        os.link(path, self.root / 'alias')
        with self.assertRaises(host.HostRefusal):
            common.EffectJournal(path)
        with self.assertRaises(FileNotFoundError):
            common.EffectJournal(self.root / 'missing')

    def test_core_identity_and_read_scope_rechecked(self):
        gate = self.create('core')
        self.snapshot['result_refs']['manifest']['sha256'] = 'f' * 64
        with self.assertRaisesRegex(host.HostRefusal, 'core-state-drift'):
            gate.check_core()
        cfg = deepcopy(self.cfg); cfg['documents']['outputs'] = ['Reference']
        cfg['core_snapshot_sha256'] = host.digest(host.canonical(self.snapshot))
        cfg['identity']['result_sha256'] = host.digest(host.canonical(self.snapshot['result_refs']))
        cfg['identity_sha256'] = host.digest(host.canonical(cfg['identity']))
        with self.assertRaisesRegex(host.HostRefusal, 'read-scope-drift'):
            self.create('write', cfg=cfg)


    def test_scope_precedence_after_effect_budget_exhaustion(self):
        cases = [('outside', 'u2_read_file', {'file_ids':['Outside']}, 'file-scope', True),
                 ('allowed', 'u2_read_file', {'file_ids':['Reference']}, 'effect-slot-budget', True),
                 ('verify', 'u2_verify', {'verifier_id':'DOC-LINKS'}, 'effect-slot-budget', True),
                 ('used-slot', 'u2_read_file', {'file_ids':['Outside']}, 'effect-slot-budget', False)]
        for name,tool,args,code,new_step in cases:
            with self.subTest(case=name):
                cfg=deepcopy(self.cfg);cfg['effect_limit']=2;cfg['documents']['verifiers']=['DOC-LINKS']
                gate=self.create('exhausted-'+name,cfg=cfg)
                for index in (1,2):
                    gate.open_step('session','read-'+str(index))
                    self.assertTrue(gate.dispatch(self.envelope(gate,call_id='read-'+str(index)))['ok'])
                if new_step:gate.open_step('session','negative')
                before=gate.effects
                result=gate.dispatch(self.envelope(gate,call_id='negative',tool=tool,arguments=args))
                self.assertEqual(result,{'ok':False,'code':code})
                self.assertEqual((gate.effects,gate.pending),(before,None))
                self.assertEqual(gate.controller.dispatch.call_count,2)
                self.assertEqual(gate.journal.rows[-1]['value']['code'],code)


class ClaudeEnvelopeTests(unittest.TestCase):
    def adapter(self):
        adapter = object.__new__(native.ClaudeCodeAdapter)
        adapter.os = native.execution_os(common.require, purpose='claude-native')
        adapter.session = str(uuid.uuid4())
        adapter.record = {'safe_events': [], 'relay_events': [], 'steps': []}
        adapter.persist = Mock()
        adapter.init_ok, adapter.actual_model, adapter.completed = False, False, False
        adapter.current = None
        adapter.assistant_calls, adapter.awaiting = [], []
        return adapter

    def test_only_empty_heartbeat_is_inert_and_duplicate_json_refused(self):
        session = str(uuid.uuid4())
        self.assertTrue(native.empty_heartbeat({'type': 'keep_alive', 'session_id': session}, session))
        for change in ({'message': 'effect'}, {'session_id': 'foreign'}, {'uuid': 'invalid'}):
            self.assertFalse(native.empty_heartbeat({'type': 'keep_alive', **change}, session))
        meta, value = native.frame_metadata(b'{"type":"keep_alive","type":"assistant"}', session, 'stdout', 1)
        self.assertFalse(meta['json_valid']); self.assertIsNone(value)

    def test_native_inventory_and_model_gate(self):
        adapter = self.adapter()
        event = {'type': 'system', 'subtype': 'init', 'session_id': adapter.session, 'model': native.MODEL,
            'tools': ['mcp__colvia__u2_read_file', 'mcp__colvia__u2_verify'], 'skills': [], 'plugins': [],
            'slash_commands': [], 'permissionMode': 'dontAsk'}
        adapter.event('stdout', event)
        self.assertTrue(adapter.init_ok)
        for field, value in (('model', 'other'), ('plugins', ['ambient']), ('tools', ['Bash']), ('permissionMode', 'bypassPermissions')):
            with self.subTest(field=field), self.assertRaises(host.HostRefusal):
                adapter.event('stdout', {**event, field: value})

    def test_lifecycle_cannot_complete_a_step_or_authorize_effect(self):
        adapter = self.adapter()
        command = str(uuid.uuid4())
        adapter.record['steps'] = [{'host_message_uuid': command}]
        event = {'type': 'command_lifecycle', 'command_uuid': command, 'state': 'completed',
                 'uuid': str(uuid.uuid4()), 'session_id': adapter.session}
        adapter.event('stdout', event)
        self.assertFalse(adapter.completed)
        self.assertFalse(adapter.init_ok)
        for change in ({'command_uuid': str(uuid.uuid4())}, {'state': 'cancelled'}, {'session_id': 'foreign'}, {'extra': 'effect'}):
            with self.assertRaises(host.HostRefusal):
                adapter.event('stdout', {**event, **change})

    def test_relay_and_assistant_arguments_must_match_before_dispatch(self):
        adapter = self.adapter()
        adapter.current = {'id': 'step'}
        adapter.init_ok = adapter.actual_model = True
        adapter.awaiting = [{'name': 'u2_read_file', 'arguments': {'file_ids': ['Reference']}}]
        adapter.assistant_calls = [{'tool': 'u2_read_file', 'arguments': {'file_ids': ['Other']}}]
        adapter.g = Mock()
        with self.assertRaisesRegex(host.HostRefusal, 'MCP-assistant-call-binding'):
            adapter.dispatch_ready()
        adapter.g.dispatch.assert_not_called()

    def test_relay_inventory_matches_existing_read_verify_schemas(self):
        profile = json.loads((ROOT / 'docs/development/verification/u2-host/tool-profile-v2.json').read_bytes())
        expected = {tool['name']: tool for tool in profile if tool['name'] in ('u2_read_file', 'u2_verify')}
        self.assertEqual([tool['name'] for tool in relay.TOOLS], ['u2_read_file', 'u2_verify'])
        descriptions = {'u2_read_file': '승인된 파일 ID의 원문을 읽습니다.',
                        'u2_verify': '고정 문서 검증기 한 개를 실행합니다.'}
        for tool in relay.TOOLS:
            with self.subTest(tool=tool['name']):
                # MCP descriptors omit the Codex function envelope. Parameter contracts stay exact.
                self.assertEqual(set(tool), {'name', 'description', 'inputSchema'})
                self.assertEqual(expected[tool['name']]['type'], 'function')
                self.assertEqual(tool['inputSchema'], expected[tool['name']]['inputSchema'])
                self.assertEqual(tool['description'], descriptions[tool['name']])
        with self.assertRaises(RuntimeError): relay.unique([('id', 1), ('id', 2)])

    def test_stop_still_terminates_child_if_host_journal_fails(self):
        adapter = self.adapter()
        adapter.closed = False
        adapter.g = Mock()
        adapter.g.stop.side_effect = OSError('synthetic journal failure')
        adapter.g.starts = {adapter.session}
        adapter.p = Mock(pid=777777, poll=Mock(return_value=0))
        adapter.p.stdin, adapter.p.stdout, adapter.p.stderr = io.BytesIO(), io.BytesIO(), io.BytesIO()
        adapter.rows, adapter.known = {}, {}
        adapter.scan = Mock()
        adapter.sel = Mock()
        adapter.up = adapter.down = None
        adapter.stderr_hash = __import__('hashlib').sha256()
        with patch.object(native.os, 'killpg') as kill:
            with self.assertRaisesRegex(OSError, 'synthetic journal failure'):
                adapter.close()
        kill.assert_called_once_with(adapter.p.pid, native.signal.SIGTERM)
        self.assertTrue(adapter.record['process_group_and_descendants_absent'])
        self.assertTrue(all(s.closed for s in (adapter.p.stdin, adapter.p.stdout, adapter.p.stderr)))
        adapter.g.native_stopped.assert_called_once_with(adapter.session, True)
