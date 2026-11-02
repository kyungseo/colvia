"""Actual offline processes + production adapter/closure; no native sandbox claim."""
from pathlib import Path
import json
import os
import subprocess
import sys
import unittest
from unittest import mock

import test_official_execution as fixture
from hv2ref import official_adapter as adapter, official_state as state, official_host as hostmod
from hv2ref import official_recovery as recovery
from hv2ref.workspace import writer_guard


class AdapterV2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): fixture.OfficialExecutionTests.setUpClass.__func__(cls)
    @classmethod
    def tearDownClass(cls): fixture.OfficialExecutionTests.tearDownClass.__func__(cls)
    def setUp(self): fixture.OfficialExecutionTests.setUp(self)
    prepare = fixture.OfficialExecutionTests.prepare

    def execute_script(self, mode='normal', content=fixture.AFTER):
        scenario = self.folder / 'scenario.json'
        scenario.write_text(json.dumps({'mode': mode, 'content': content}))
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
        with mock.patch.object(adapter, 'launch_spec', return_value=spec), mock.patch.object(subprocess, 'Popen', side_effect=offline_popen), mock.patch.object(adapter, 'reason_code', side_effect=capture_reason), mock.patch.object(hostmod, 'reason_code', side_effect=capture_reason):
            result = adapter.run(h)
        self.failure_detail = json.dumps({'result': result, 'errors': errors, 'rows': state.read_capsule(self.target,h.grant)['rows']})
        return h, result, admitted

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
