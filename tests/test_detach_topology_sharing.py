"""Detach probe sharing retains fresh boundaries and preservation refusals."""
from pathlib import Path
import subprocess
import unittest
from unittest.mock import patch

from hv2ref import product, work, workspace
from hv2ref.errors import ContractError, InjectedCrash
import test_productization_safety as fixtures


class DetachTopologySharingTests(unittest.TestCase):
    def setUp(self):
        self.f = fixtures.ActualWorkspaceInitTests()
        self.f.setUp(); self.addCleanup(self.f.doCleanups)
        self.base = self.f.base; self.target = self.f.target
        self.f.apply_init(self.f.preview()); self.f.complete_work()
        self.preview = product.workspace_detach_preview(self.target, operation_id='detach-a', created_at=self.f.TIME)
        with self.assertRaises(InjectedCrash):
            product.workspace_detach_apply(self.target, self.preview['request'],
                confirm_token=self.preview['confirm_token'], inject_at='after-receipt')

    def git_init(self):
        subprocess.run(['git', 'init', '-q', str(self.target)], capture_output=True, check=True, timeout=45)

    def parity(self, primary):
        if primary: self.git_init()
        before = fixtures.exact_snapshot(self.target)
        raw = workspace._topology_probe; git = work._git
        ignores = []
        def track(target, *args, **kwargs):
            if args[0] == 'check-ignore': ignores.append((args, kwargs.get('input_data')))
            return git(target, *args, **kwargs)
        with patch.object(workspace, '_topology_probe', wraps=raw) as probes, patch.object(work, '_git', track):
            actual = product.workspace_detached_status(self.target)
        self.assertEqual(5, probes.call_count)
        shared_ignores = list(ignores); ignores.clear()
        def fresh(ctx, target, env, *, mutation): return raw(target, env)
        with patch.object(workspace._DetachTopologyObservation, '_probe', fresh), patch.object(work, '_git', track):
            expected = product.workspace_detached_status(self.target)
        self.assertEqual(expected, actual); self.assertEqual(shared_ignores, ignores)
        self.assertEqual(bool(primary), bool(ignores))
        self.assertEqual(before, fixtures.exact_snapshot(self.target))

    def test_nongit_stationary_parity_and_five_probes(self): self.parity(False)

    def test_primary_stationary_parity_and_unchanged_ignore_checks(self): self.parity(True)

    def test_missing_git_keeps_fresh_nongit_reads(self):
        before = fixtures.exact_snapshot(self.target)
        expected = product.workspace_detached_status(self.target)
        with patch.object(workspace, '_topology_probe', side_effect=FileNotFoundError) as calls:
            actual = product.workspace_detached_status(self.target)
        self.assertEqual(expected, actual); self.assertGreater(calls.call_count, 5)
        self.assertEqual(before, fixtures.exact_snapshot(self.target))

    def final_probe_change(self, change):
        probe = workspace._topology_probe; count = []; observed = []
        def raw(target, env):
            count.append(1)
            if len(count) == 2:
                change(); observed.append(fixtures.exact_snapshot(self.target))
            return probe(target, env)
        with patch.object(workspace, '_topology_probe', raw), self.assertRaises(ContractError):
            product._detach_observe_once(self.target)
        self.assertEqual(2, len(count)); self.assertEqual(observed[0], fixtures.exact_snapshot(self.target))

    def test_final_probe_detects_nongit_to_primary(self):
        self.final_probe_change(self.git_init)

    def test_final_probe_detects_primary_to_nongit(self):
        self.git_init()
        self.final_probe_change(lambda: (self.target / '.git').rename(self.base / 'saved-metadata'))

    def test_git_disappearance_after_cached_probe_is_refused(self):
        raw = workspace._topology_probe; calls = []
        before = fixtures.exact_snapshot(self.target)
        def probe(target, env):
            calls.append(1)
            if len(calls) == 2: raise FileNotFoundError
            return raw(target, env)
        with patch.object(workspace, '_topology_probe', probe), self.assertRaisesRegex(ContractError, 'Git unavailable'):
            product._detach_observe_once(self.target)
        self.assertEqual(2, len(calls)); self.assertEqual(before, fixtures.exact_snapshot(self.target))

    def test_second_pass_detects_preserved_byte_change(self):
        observe = product._detach_observe_once; calls = []; changed = []
        def once(target):
            result = observe(target); calls.append(1)
            if len(calls) == 1:
                (target / '.hrn/.gitignore').write_text('changed after first pass\n')
                changed.append(fixtures.exact_snapshot(target))
            return result
        with patch.object(product, '_detach_observe_once', once), self.assertRaisesRegex(ContractError, 'preserved bytes changed'):
            product.workspace_detached_status(self.target)
        self.assertEqual(changed[0], fixtures.exact_snapshot(self.target))

    def test_between_removals_unknown_member_stops_before_next_unlink(self):
        unlink = Path.unlink; removed = []; changed = []
        def remove(path, *args, **kwargs):
            result = unlink(path, *args, **kwargs)
            if path == self.target / 'hv2':
                removed.append(str(path))
                (self.target / '.hrn/product/unplanned').write_text('preserve me\n')
                changed.append(fixtures.exact_snapshot(self.target))
            return result
        with patch.object(Path, 'unlink', remove), self.assertRaisesRegex(ContractError, 'unknown detach member'):
            product.workspace_detach_apply(self.target, self.preview['request'],
                confirm_token=self.preview['confirm_token'], recover=True)
        self.assertEqual(1, len(removed)); self.assertEqual(changed[0], fixtures.exact_snapshot(self.target))

    def test_contexts_close_after_success_and_failure(self):
        contexts = []; init = workspace._DetachTopologyObservation.__init__
        def initialize(ctx, target): init(ctx, target); contexts.append(ctx)
        with patch.object(workspace._DetachTopologyObservation, '__init__', initialize):
            product.workspace_detached_status(self.target)
            (self.target / '.hrn/product/unknown').write_text('keep\n')
            before = fixtures.exact_snapshot(self.target)
            with self.assertRaises(ContractError): product.workspace_detached_status(self.target)
        self.assertEqual(3, len(contexts)); self.assertEqual(3, len({id(c) for c in contexts}))
        self.assertTrue(all(c._closed and c._raw is None for c in contexts))
        self.assertEqual(before, fixtures.exact_snapshot(self.target))

    def test_variable_diagnostics_do_not_replace_classification_checks(self):
        raw = workspace._topology_probe; calls = []
        before = fixtures.exact_snapshot(self.target)
        def probe(target, env):
            code, out, err = raw(target, env); calls.append(1)
            return code, out, err + ('diagnostic-' + str(len(calls))).encode()
        with patch.object(workspace, '_topology_probe', probe):
            self.assertEqual('partial', product.workspace_detached_status(self.target)['classification'])
        self.assertEqual(5, len(calls)); self.assertEqual(before, fixtures.exact_snapshot(self.target))

    def test_detach_observation_cannot_admit_mutation_or_outlive_scope(self):
        context = workspace._DetachTopologyObservation(self.target)
        with self.assertRaisesRegex(ContractError, 'invalid topology observation use'):
            workspace.classify_target(self.target, mutation=True, _topology_observation=context)
        context.close()
        with self.assertRaisesRegex(ContractError, 'invalid topology observation use'):
            workspace.classify_target(self.target, _topology_observation=context)
