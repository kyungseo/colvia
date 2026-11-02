"""Actual offline processes + production adapter/closure; no native sandbox claim."""
from pathlib import Path
import json
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
import unittest
from unittest import mock

import test_official_execution as fixture
from hv2ref import official_adapter as adapter, official_state as state, official_host as hostmod
from hv2ref import official_entry as entry, official_recovery as recovery
from hv2ref.workspace import writer_guard


class AdapterV2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): fixture.OfficialExecutionTests.setUpClass.__func__(cls)
    @classmethod
    def tearDownClass(cls): fixture.OfficialExecutionTests.tearDownClass.__func__(cls)
    def setUp(self): fixture.OfficialExecutionTests.setUp(self)
    prepare = fixture.OfficialExecutionTests.prepare

    def execute_script(self, mode='normal', content=fixture.AFTER, *, startup_warning=False,
                       cancel_after_read=False, split_warning=False):
        if startup_warning:
            self.request['runtime']['sha256'].update(BIN=entry.CLI_SHA256, CODE_MODE_HOST=entry.HELPER_SHA256)
        scenario = self.folder / 'scenario.json'
        scenario.write_text(json.dumps({'mode': mode, 'content': content, 'startup_warning': startup_warning}))
        prepared = self.prepare(); h = hostmod.Host(prepared['spec'], prepared['confirm_token']); self.addCleanup(h.close)
        spec = {'argv': [sys.executable, '-I', '-S', '-B', str(fixture.SOURCE / 'tests/fixtures/official_scripted_server.py'), str(scenario)],
                'env': dict(os.environ), 'cwd': str(self.folder), 'policy_sha256': 'a' * 64, 'tools': []}
        native_popen = subprocess.Popen
        admitted = []; errors = []
        original_reason = adapter.reason_code
        def capture_reason(error, default="internal_error"):
            errors.append(type(error).__name__ + ": " + str(error))
            return original_reason(error, default)
        def offline_popen(argv, **kwargs):
            if argv[0] == '/usr/bin/sandbox-exec' and '--spec' in argv:
                # Run the actual worker with the enclosing test sandbox. The
                # product worker.sb is materialized but is not native-qualified.
                argv = argv[argv.index('-f') + 2:]
                admitted.append(list(argv))
            return native_popen(argv, **kwargs)
        native_read = os.read
        first_stderr = True
        def read_chunk(fd, limit):
            nonlocal first_stderr
            peer = h.rpc.p if h.rpc else None
            if split_warning and first_stderr and peer and not peer.stderr.closed and fd == peer.stderr.fileno():
                data = native_read(fd, min(limit, 101))
                if data:
                    first_stderr = False
                return data
            return native_read(fd, limit)

        with mock.patch.object(os, 'read', new=read_chunk), mock.patch.object(adapter, 'launch_spec', return_value=spec), mock.patch.object(subprocess, 'Popen', side_effect=offline_popen), mock.patch.object(adapter, 'reason_code', side_effect=capture_reason), mock.patch.object(hostmod, 'reason_code', side_effect=capture_reason):
            if cancel_after_read:
                with ThreadPoolExecutor(max_workers=1) as pool:
                    future = pool.submit(self.cancel_when_read_completes, h)
                    result = adapter.run(h)
                    self.cancel_receipt = future.result(timeout=15)
            else:
                result = adapter.run(h)
        self.failure_detail = json.dumps({'result': result, 'errors': errors, 'rows': state.read_capsule(self.target,h.grant)['rows']})
        return h, result, admitted

    def cancel_when_read_completes(self, host):
        journal = host.run / 'journal.jsonl'
        until = time.monotonic() + 30
        while time.monotonic() < until:
            rows = [json.loads(line) for line in journal.read_bytes().splitlines(keepends=True)
                    if line.endswith(b'\n')]
            reads = {row['value']['callback_id'] for row in rows if row['kind'] == 'callback-reserved'
                     and row['value']['tool'] == 'read'}
            if any(row['kind'] == 'callback-completed' and row['value']['success']
                   and row['value']['callback_id'] in reads for row in rows):
                self.assertFalse(any(row['kind'] == 'revoked' for row in rows))
                cmd = [sys.executable, '-I', '-B', str(self.target/'colvia'), 'run', 'cancel',
                       '--grant', host.grant, '--reason', 'cancelled']
                reply = subprocess.run(cmd, capture_output=True, check=True, timeout=10)
                return json.loads(reply.stdout)
            time.sleep(.01)
        self.fail('read did not complete')

    def test_single_startup_warning_allows_normal_completion(self):
        h, result, workers = self.execute_script(startup_warning=True)
        self.assertEqual(('completed', 'applied', 5),
                         (result['status'], result['document_write_effect'], len(workers)))
        self.assertIs(result['initialize_path_warning_allowed'], True)
        self.assertEqual('single_read', result['initialize_path_warning_mode'])
        self.assertNotIn('runtime_first_failure', result)
        self.assertNotIn('initialize_path_warning_mode', state.public_status(state.read_capsule(self.target, h.grant)))

    def test_read_then_external_cancel_confirms_same_turn_and_preserves_files(self):
        before = {name: (self.target/name).read_bytes() for name in ('a', 'b', 'sentinel')}
        self.request['worker_limit'] = 1
        replies = []
        native_reply = adapter.Rpc.reply

        def capture(rpc, message, value, success=True):
            replies.append((success, dict(value)))
            return native_reply(rpc, message, value, success)

        with mock.patch.object(adapter.Rpc, 'reply', new=capture):
            h, result, workers = self.execute_script(startup_warning=True, cancel_after_read=True, split_warning=True)
        self.assertEqual([(False, {'ok': False, 'reason': 'cancelled', 'worker_admitted': True, 'effect_status': 'none'})], replies)
        self.assertEqual('joined_101', result['initialize_path_warning_mode'])
        self.assertIs(self.cancel_receipt['cancel_requested'], True)
        self.assertIs(self.cancel_receipt['effects_stopped'], False)
        self.assertEqual(h.grant, self.cancel_receipt['grant'])
        self.assertIs(result['cancel_seen_after_read'], True)
        self.assertIs(result['runtime_interrupt_confirmed'], True)
        self.assertEqual(('interrupted', 'none', 'closed', 1),
                         (result['status'], result['document_write_effect'], result['process_observation'], len(workers)))
        rows = state.read_capsule(self.target, h.grant)['rows']
        self.assertEqual(['read'], [r['value']['tool'] for r in rows if r['kind'] == 'callback-reserved'])
        self.assertEqual(['cancelled'], [r['value']['reason'] for r in rows if r['kind'] == 'revoked'])
        self.assertEqual('cancelled', rows[-1]['value']['stop_reason'])
        self.assertEqual(1, sum(r['kind'] == 'rpc-reserved' and r['value']['method'] == 'turn/interrupt' for r in rows))
        self.assertEqual(before, {name: (self.target/name).read_bytes() for name in before})
        status = state.public_status(state.read_capsule(self.target, h.grant))
        self.assertFalse({'runtime_interrupt_confirmed', 'cancel_seen_after_read'} & status.keys())

    def test_expired_read_window_does_not_send_read_result_or_double_count(self):
        self.request['worker_limit'] = 1
        replies = []
        native_reply = adapter.Rpc.reply
        def capture(rpc, message, value, success=True):
            replies.append((success, 'files' in value))
            return native_reply(rpc, message, value, success)

        # Cross the grant expiry on the adapter's wall clock only. The read,
        # its completion record, failure response and interrupt all run normally.
        read_limit = adapter.Rpc.read_limit_reason
        clock = mock.Mock(wraps=time)
        clock.time_ns.side_effect = time.time_ns
        def expire(rpc):
            self.assertGreater(rpc.deadline, time.monotonic())
            clock.time_ns.side_effect = None
            clock.time_ns.return_value = rpc.host.spec['request']['expires_wall_ns'] + 1
            return read_limit(rpc)

        with mock.patch.object(adapter, 'time', clock), mock.patch.object(adapter.Rpc, 'read_limit_reason', new=expire), mock.patch.object(adapter.Rpc, 'reply', new=capture):
            h, result, workers = self.execute_script()
        rows = state.read_capsule(self.target, h.grant)['rows']
        self.assertEqual([(False, False)], replies)
        self.assertEqual(1, sum(r['kind'] == 'callback-completed' for r in rows))
        self.assertEqual('deadline', rows[-1]['value']['stop_reason'])
        self.assertEqual(('none', 'closed', 1), (result['document_write_effect'], result['process_observation'], len(workers)))
        self.assertNotIn('cancel_seen_after_read', result)
        self.assertIs(result['runtime_interrupt_confirmed'], True)

    def test_stderr_during_completed_read_blocks_payload_and_closes(self):
        self.request['worker_limit'] = 1
        before = (self.target/'a').read_bytes()
        read_limit = adapter.Rpc.read_limit_reason
        def signal_window(rpc):
            (self.folder/'read-finished').touch()
            return read_limit(rpc)

        with mock.patch.object(adapter.Rpc, 'read_limit_reason', new=signal_window):
            h, result, workers = self.execute_script(mode='stderr-in-read-window')
        rows = state.read_capsule(self.target, h.grant)['rows']
        self.assertEqual(['read'], [r['value']['tool'] for r in rows if r['kind'] == 'callback-reserved'])
        self.assertEqual(1, sum(r['kind'] == 'callback-completed' for r in rows))
        self.assertEqual('protocol_refused', rows[-1]['value']['stop_reason'])
        self.assertEqual(('none', 'closed', 1), (result['document_write_effect'], result['process_observation'], len(workers)))
        self.assertEqual(before, (self.target/'a').read_bytes())
        self.assertNotIn('runtime_interrupt_confirmed', result)
        self.assertNotIn(b'READ_WINDOW_DIAGNOSTIC', b''.join(p.read_bytes() for p in h.run.iterdir()))
        # The final outgoing frame was turn/start. Even the refusal reply
        # cannot be transmitted once stderr is latched.
        history = state.read_capsule(self.target, h.grant)['history']
        self.assertEqual(len(history.rpc) + 1, h.rpc.outgoing_frames)  # Includes initialized.

    def test_wrong_turn_cannot_confirm_an_accepted_external_cancel(self):
        self.request['worker_limit'] = 1
        h, result, workers = self.execute_script(mode='wrong-interrupt', cancel_after_read=True)
        self.assertTrue(self.cancel_receipt['cancel_requested'])
        self.assertIs(result['cancel_seen_after_read'], True)
        self.assertNotIn('runtime_interrupt_confirmed', result)
        self.assertEqual(('none', 'closed', 1), (result['document_write_effect'], result['process_observation'], len(workers)))

    def test_exhausted_read_budget_interrupts_without_external_cancel(self):
        self.request['worker_limit'] = 1
        h, result, workers = self.execute_script()
        self.assertNotIn('cancel_seen_after_read', result)
        self.assertIs(result['runtime_interrupt_confirmed'], True)
        self.assertEqual('worker_budget_consumed', state.read_capsule(self.target, h.grant)['rows'][-1]['value']['stop_reason'])

    def test_refused_startup_returns_only_bounded_first_failure(self):
        h, result, workers = self.execute_script(mode='bad-startup')
        self.assertEqual({'phase': 'initialize', 'source': 'stderr', 'code': 'unclassified',
                          'byte_count': len(b'UNEXPECTED_STARTUP_DIAGNOSTIC')}, result['runtime_first_failure'])
        self.assertNotIn('initialize_path_warning_mode', result)
        self.assertEqual(('revoked-before-launch', 'none', 'closed', 0),
                         (result['status'], result['document_write_effect'], result['process_observation'], len(workers)))
        self.assertNotIn(b'UNEXPECTED_STARTUP_DIAGNOSTIC', b''.join(p.read_bytes() for p in h.run.iterdir()))
        self.assertNotIn('runtime_first_failure', state.public_status(state.read_capsule(self.target, h.grant)))

    def test_shutdown_stderr_preserves_applied_effect_without_success(self):
        h, result, _ = self.execute_script(mode='stderr-on-close')
        self.assertEqual(('interrupted', 'applied', 'closed'),
                         (result['status'], result['document_write_effect'], result['process_observation']))
        self.assertEqual('protocol_refused', state.read_capsule(self.target, h.grant)['rows'][-1]['value']['stop_reason'])
        self.assertNotIn(b'LATE_STDERR_MARKER', b''.join(p.read_bytes() for p in h.run.iterdir()))

    def assert_guard(self, allowed):
        if allowed:
            with writer_guard(self.target): (self.target / 'sentinel').write_text('allowed synthetic follow-up\n')
        else:
            from hv2ref.errors import ContractError
            with self.assertRaises(ContractError):
                with writer_guard(self.target): pass

    def test_actual_adapter_completion_minimal_capsule_and_recovery(self):
        h, result, workers = self.execute_script()
        self.assertEqual((result['status'], result['document_write_effect'], len(workers)), ('completed', 'applied', 5), self.failure_detail)
        self.assertFalse(result['cleanup_pending'])
        self.assertEqual({p.name for p in h.run.iterdir()}, {'grant.json', 'journal.jsonl', 'receipt.json'})
        raw = b''.join(p.read_bytes() for p in h.run.iterdir())
        for marker in (b'SCRIPT_THREAD_MARKER', b'SCRIPT_TURN_MARKER', b'SCRIPT_CALL_MARKER', fixture.AFTER.encode()): self.assertNotIn(marker, raw)
        self.assertEqual(recovery.inspect(state.read_capsule(self.target, h.grant), self.request['host_control_root']), 'present')
        self.assertFalse((Path(self.request['host_control_root']) / 'transient' / h.grant).exists())
        self.assertEqual((self.target / 'a').read_bytes(), fixture.PREFIX + fixture.AFTER.encode() + fixture.SUFFIX)
        self.assert_guard(True)

    def test_content_refusal_before_write_reservation_closes_without_effect(self):
        before = (self.target / 'a').read_bytes()
        h, result, workers = self.execute_script(content='api_key=REFUSED_CONTENT_MARKER_123456')
        self.assertEqual((result['status'], result['document_write_effect'], len(workers)), ('interrupted', 'none', 1))
        rows = state.read_capsule(self.target, h.grant)['rows']
        self.assertEqual(len([r for r in rows if r['kind'] == 'callback-reserved']), 1)
        self.assertNotIn(b'REFUSED_CONTENT_MARKER', b''.join(p.read_bytes() for p in h.run.iterdir()))
        self.assertEqual((self.target / 'a').read_bytes(), before)
        self.assertEqual(recovery.inspect(state.read_capsule(self.target, h.grant), self.request['host_control_root']), 'not_required')
        self.assert_guard(True)

    def test_wrong_caller_closes_actual_runtime_without_worker(self):
        h, result, workers = self.execute_script(mode='wrong-caller')
        self.assertEqual((result['status'], result['document_write_effect'], len(workers)), ('interrupted', 'none', 0))
        self.assertNotIn(b'REFUSED_CALLER_MARKER', (h.run / 'journal.jsonl').read_bytes())
        self.assert_guard(True)

    def test_rpc_error_has_fixed_diagnostics_and_prelaunch_closure(self):
        h, result, workers = self.execute_script(mode='rpc-error')
        self.assertEqual((result['status'], result['document_write_effect'], len(workers)), ('revoked-before-launch', 'none', 0))
        self.assertNotIn(b'RPC_ERROR_MARKER', b''.join(p.read_bytes() for p in h.run.iterdir()))
        self.assert_guard(True)

    def test_runtime_stderr_has_no_file_and_closes_actual_runtime(self):
        h, result, workers = self.execute_script(mode='stderr')
        self.assertEqual((result['status'], result['document_write_effect'], len(workers)), ('interrupted', 'none', 0))
        rows = state.read_capsule(self.target, h.grant)['rows']
        self.assertTrue(any(r['kind'] == 'diagnostic' and r['value']['source'] == 'runtime' for r in rows))
        self.assertNotIn(b'RUNTIME_STDERR_MARKER', b''.join(p.read_bytes() for p in h.run.iterdir()))
        self.assert_guard(True)


if __name__ == '__main__': unittest.main()
