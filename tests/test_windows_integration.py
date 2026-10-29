"""Portable integration checks; runtime doubles are not native Windows evidence."""
from __future__ import annotations
import copy
from pathlib import Path
import subprocess
import sys
import unittest
from unittest import mock

from hv2ref import product, workspace, jsonio, work
from hv2ref.errors import ContractError, InjectedCrash
from tests.platform_fixtures import fixture_temporary_directory
from tests import test_continuation as continuation_cases

SOURCE = Path(__file__).resolve().parents[1]
TIME = '2026-10-22T00:00:00Z'


class WindowsIntegrationTests(unittest.TestCase):
    """Mac portable integration lane; explicitly exclude from native qualification selection.

    Runtime and repair-attribute doubles are intentional. Native lifecycle uses
    WindowsLifecycleTests; these methods do not supply Win32 execution evidence.
    """
    def setUp(self):
        temp = fixture_temporary_directory(prefix='windows-integration-')
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name).resolve()
        self.target = self.root / 'target'; self.target.mkdir()
        gate = mock.patch.object(workspace, 'require_supported_runtime')
        self.runtime_gate = gate.start(); self.addCleanup(gate.stop)

    def prepared(self, label):
        root = self.root / label; root.mkdir()
        payload = product.workspace_candidate(SOURCE)['payload']
        for name, data in payload.items():
            if name == 'colvia':
                data = data.replace(b'WORKSPACE_INVENTORY_ID = "continuation-1"', b'WORKSPACE_INVENTORY_ID = "windows-2"')
            elif name == 'README.md':
                data += ('\nSynthetic source ' + label + '\n').encode()
            path = root / name; path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(data)
        return root

    def init(self, source):
        preview = product.workspace_init_preview(source, self.target, authority_home_id='home-integration', operation_id='init-a', created_at=TIME)
        self.assertEqual(6, preview['request']['plan']['schema_version'])
        result = product.workspace_init_apply(source, self.target, preview['request'], confirm_token=preview['confirm_token'])
        self.assertEqual('initialized', result['classification'])
        return preview

    def test_schema6_init_update_rollback_detach_recovery_and_plain_reader(self):
        p = self.prepared('p'); q = self.prepared('q'); self.init(p)
        for action, source, op in [('update', q, 'update-q'), ('rollback', None, 'rollback-p')]:
            preview = product.workspace_switch_preview(self.target, action=action, source=source, operation_id=op, created_at=TIME)
            self.assertEqual(6, preview['request']['schema_version'])
            product.workspace_switch_apply(self.target, preview['request'], source=source, confirm_token=preview['confirm_token'])
        self.assertEqual(product.workspace_candidate(p)['inventory'], product.verify_workspace_product(self.target)['inventory'])
        preview = product.workspace_detach_preview(self.target, operation_id='detach-a', created_at=TIME)
        self.assertEqual(6, preview['request']['schema_version'])
        with self.assertRaises(InjectedCrash):
            product.workspace_detach_apply(self.target, preview['request'], confirm_token=preview['confirm_token'], inject_at='after-receipt')
        self.assertEqual('partial', product.workspace_detached_status(self.target)['classification'])
        audit = [sys.executable, '-I', '-B', str(SOURCE / 'tests/fixtures/product_plain_auditor.py'), str(self.target)]
        partial = subprocess.run(audit, capture_output=True, timeout=30)
        self.assertEqual(14, partial.returncode, partial.stdout + partial.stderr)
        result = product.workspace_detach_apply(self.target, preview['request'], confirm_token=preview['confirm_token'], recover=True)
        self.assertEqual('detached', result['classification'])
        complete = subprocess.run(audit, capture_output=True, timeout=30)
        self.assertEqual(0, complete.returncode, complete.stdout + complete.stderr)

    def test_windows_init_and_switch_refuse_old_pairs_before_publication(self):
        p = self.prepared('p')
        preview = product.workspace_init_preview(p, self.target, authority_home_id='home-integration', operation_id='init-a', created_at=TIME)
        for version in (1, 4, 5, True):
            request = copy.deepcopy(preview['request']); request['plan']['schema_version'] = version
            token = jsonio.sha256_bytes(jsonio.canonical_json_bytes(request))[:16]
            with self.subTest(version=version), self.assertRaises(ContractError):
                product.workspace_init_apply(p, self.target, request, confirm_token=token)
            self.assertEqual([], list(self.target.iterdir()))
        self.init(p)
        before = {f.relative_to(self.target).as_posix(): f.read_bytes() for f in self.target.rglob('*') if f.is_file()}
        with self.assertRaises(ContractError):
            product.workspace_switch_preview(self.target, action='update', source=SOURCE, operation_id='cross-window', created_at=TIME)
        self.assertEqual(before, {f.relative_to(self.target).as_posix(): f.read_bytes() for f in self.target.rglob('*') if f.is_file()})

    def test_equal_membership_cross_window_pairs_refuse_in_both_directions(self):
        sources = [('windows-2', self.prepared('p'), 'continuation-1'),
                   ('continuation-1', SOURCE, 'windows-2')]
        for window, source, wrong in sources:
            with self.subTest(window=window):
                target = self.root / window; target.mkdir()
                preview = product.workspace_init_preview(source, target, authority_home_id='home-cross', operation_id='init-cross', created_at=TIME)
                request = copy.deepcopy(preview['request'])
                request['plan']['candidate_release']['inventory_id'] = wrong
                token = jsonio.sha256_bytes(jsonio.canonical_json_bytes(request))[:16]
                with self.assertRaises(ContractError):
                    product.workspace_init_apply(source, target, request, confirm_token=token)
                self.assertEqual([], list(target.iterdir()))
                product.workspace_init_apply(source, target, preview['request'], confirm_token=preview['confirm_token'])
                observed = product.verify_workspace_product(target)
                self.assertEqual(window, observed['inventory']['inventory_id'])
                release = Path(observed['release_path'])
                inventory_path = release / 'inventory.json'
                original = inventory_path.read_bytes()
                changed = copy.deepcopy(observed['inventory']); changed['inventory_id'] = wrong
                inventory_path.write_bytes(jsonio.canonical_json_bytes(changed))
                before = {f.relative_to(target).as_posix(): f.read_bytes() for f in target.rglob('*') if f.is_file()}
                with self.assertRaisesRegex(ContractError, 'release directory/inventory mismatch'):
                    product.verify_workspace_product(target)
                self.assertEqual(before, {f.relative_to(target).as_posix(): f.read_bytes() for f in target.rglob('*') if f.is_file()})
                rehashed = release.with_name('product-release-' + jsonio.sha256_bytes(inventory_path.read_bytes())[:24])
                release.rename(rehashed)
                with self.assertRaisesRegex(ContractError, 'launcher declaration differs from inventory window'):
                    product.verify_workspace_release(rehashed)
                rehashed.rename(release)
                inventory_path.write_bytes(original)
                self.assertEqual(observed, product.verify_workspace_product(target))

    def test_schema6_repair_uses_bound_windows_observation_and_rechecks_completion(self):
        p = self.prepared('p'); self.init(p)
        launcher = self.target / 'colvia'; exact = launcher.read_bytes()
        launcher.write_bytes(exact + b'\n# synthetic damage\n')
        # Portable attribute double only; actual Win32 handles/attributes remain native obligations.
        def observation(path, **kwargs):
            st = Path(path).stat()
            return {'attributes': 0, 'directory': False, 'device': st.st_dev, 'inode': st.st_ino}
        with mock.patch.object(jsonio, 'windows_path_observation', side_effect=observation):
            preview = product.workspace_repair_preview(p, self.target, self.root / 'backup', operation_id='repair-a', created_at=TIME)
            self.assertEqual(6, preview['request']['plan']['schema_version'])
            self.assertEqual([0], [entry['after']['mode'] for entry in preview['request']['files']])
            result = product.workspace_repair_apply(p, self.target, preview['request'], confirm_token=preview['confirm_token'])
            self.assertEqual('repaired', result['classification'])
            self.assertEqual(exact, launcher.read_bytes())
            # Replaying after new content drift must observe the current file, not cached completion.
            launcher.write_bytes(exact + b'\n# later drift\n')
            before = launcher.read_bytes()
            with self.assertRaises(ContractError):
                product.workspace_repair_apply(p, self.target, preview['request'], confirm_token=preview['confirm_token'], recover=True)
            self.assertEqual(before, launcher.read_bytes())

    def test_schema6_completed_switch_replay_rechecks_truth_under_guard(self):
        p = self.prepared('p'); q = self.prepared('q'); self.init(p)
        preview = product.workspace_switch_preview(self.target, action='update', source=q, operation_id='update-q', created_at=TIME)
        product.workspace_switch_apply(self.target, preview['request'], source=q, confirm_token=preview['confirm_token'])
        from contextlib import contextmanager
        held = [False]; observed = []; original_guard = workspace.writer_guard
        original_truth = product._lifecycle_truth
        @contextmanager
        def guard(target):
            with original_guard(target):
                held[0] = True
                try: yield
                finally: held[0] = False
        def truth(target, **kwargs):
            value = original_truth(target, **kwargs)
            if kwargs.get('allow_pending'):
                observed.append(held[0])
                return value + [{'synthetic': 'post-completion authority change'}]
            return value
        before = {f.relative_to(self.target).as_posix(): f.read_bytes() for f in self.target.rglob('*') if f.is_file()}
        with mock.patch.object(workspace, 'writer_guard', guard), mock.patch.object(product, '_lifecycle_truth', side_effect=truth):
            result = product.workspace_switch_apply(self.target, preview['request'], source=q, confirm_token=preview['confirm_token'])
        self.assertEqual('degraded', result['classification'])
        self.assertEqual('replayed', result['historical_operation_result'])
        self.assertEqual('unavailable', result['transition_content_verification']['classification'])
        self.assertEqual([True, True], observed)
        self.assertEqual(before, {f.relative_to(self.target).as_posix(): f.read_bytes() for f in self.target.rglob('*') if f.is_file()})

    def test_schema6_completed_replay_has_no_file_mutation_gate_or_reflush(self):
        p = self.prepared('p'); q = self.prepared('q'); self.init(p)
        self.assertEqual((p / 'colvia').read_bytes(), (q / 'colvia').read_bytes())
        preview = product.workspace_switch_preview(self.target, action='update', source=q, operation_id='update-q', created_at=TIME)
        product.workspace_switch_apply(self.target, preview['request'], source=q, confirm_token=preview['confirm_token'])
        before = {f.relative_to(self.target).as_posix(): f.read_bytes() for f in self.target.rglob('*') if f.is_file()}
        with mock.patch.object(jsonio, 'windows_preflight_files', side_effect=AssertionError('completed replay added mutation gate')), mock.patch.object(jsonio, 'sync_existing_file', side_effect=AssertionError('completed replay added reflush')):
            result = product.workspace_switch_apply(self.target, preview['request'], source=q, confirm_token=preview['confirm_token'])
        self.assertEqual('replayed', result['classification'])
        self.assertEqual(before, {f.relative_to(self.target).as_posix(): f.read_bytes() for f in self.target.rglob('*') if f.is_file()})

    def test_published_init_recovery_syncs_parents_before_receipt(self):
        # Portable post-publication fault, not a native directory-attribute test.
        source = self.prepared('p')
        packet = product.workspace_init_preview(source, self.target, authority_home_id='home-integration', operation_id='init-a', created_at=TIME)
        request = copy.deepcopy(packet['request']); token = packet['confirm_token']
        release_parent = self.target / '.hrn/product/releases'
        operation = self.target / '.hrn/staging/init-init-a'
        receipt = self.target / '.hrn/product/receipts/init-a.json'
        rename = product.rename_directory
        def published_then_unavailable(staged, published):
            rename(staged, published)
            raise ContractError('HV2-WINDOWS-PATH', 'phase=post-directory-publication; publication occurred; synthetic observation unavailable')
        with mock.patch.object(product, 'rename_directory', side_effect=published_then_unavailable):
            with self.assertRaisesRegex(ContractError, 'publication occurred'):
                product.workspace_init_apply(source, self.target, request, confirm_token=token)
        self.assertFalse(receipt.exists())
        self.assertEqual(1, len(list(release_parent.iterdir())))
        events = []; sync = product.sync_directory; exact = workspace._write_exact
        def sync_observed(path):
            events.append(('sync', path)); return sync(path)
        def exact_observed(path, data):
            if path == receipt: events.append(('receipt', path))
            return exact(path, data)
        with mock.patch.object(product, 'sync_directory', side_effect=sync_observed), mock.patch.object(workspace, '_write_exact', side_effect=exact_observed):
            result = product.workspace_init_apply(source, self.target, request, confirm_token=token, recover=True)
        self.assertEqual('initialized', result['classification'])
        self.assertLess(events.index(('sync', release_parent)), events.index(('receipt', receipt)))
        self.assertLess(events.index(('sync', operation)), events.index(('receipt', receipt)))
        self.assertEqual(packet['request'], request)
        with mock.patch.object(product, 'sync_directory', side_effect=AssertionError('completed replay must not reflush')):
            self.assertTrue(product.workspace_init_apply(source, self.target, request, confirm_token=token, recover=True)['replayed'])

    def test_windows_object_home_recovery_syncs_published_parents(self):
        from types import SimpleNamespace
        # Only this helper's Windows branch is doubled; filesystem IO is POSIX.
        for category in ('work', 'intents'):
            root = self.target / category; (root / '.hrn' / category).mkdir(parents=True)
            identity = {'record_type': 'work-identity' if category == 'work' else 'intent-identity',
                        'schema_version': 1, 'authority_home_id': 'home-integration',
                        'work_id' if category == 'work' else 'intent_id': 'object-a'}
            home = root / '.hrn' / category / 'object-a'; staging = root / '.hrn/staging'
            rename = jsonio.rename_directory
            def published_then_unavailable(source, destination):
                rename(source, destination)
                raise ContractError('HV2-WINDOWS-PATH', 'phase=post-directory-publication; publication occurred')
            with mock.patch.object(work, 'sys', SimpleNamespace(platform='win32')), mock.patch.object(jsonio, 'rename_directory', side_effect=published_then_unavailable):
                with self.assertRaisesRegex(ContractError, 'publication occurred'):
                    work._publish_object_home(root, category, 'object-a', identity, None)
            before = (home / 'identity.json').read_bytes(); events = []; sync = jsonio.sync_directory
            def record(path): events.append(path); return sync(path)
            with mock.patch.object(work, 'sys', SimpleNamespace(platform='win32')), mock.patch.object(jsonio, 'sync_directory', side_effect=record):
                self.assertEqual(home, work._publish_object_home(root, category, 'object-a', identity, None))
            self.assertIn(home.parent, events); self.assertIn(staging, events)
            self.assertEqual(before, (home / 'identity.json').read_bytes())

    def test_detach_window_validation_refuses_before_marker_publication(self):
        source = self.prepared('p'); self.init(source)
        packet = product.workspace_detach_preview(self.target, operation_id='detach-before-marker', created_at=TIME)
        def bytes_now():
            return {p.relative_to(self.target).as_posix(): p.read_bytes() for p in self.target.rglob('*') if p.is_file()}
        before = bytes_now(); marker = self.target / '.hrn/detached.json'
        with mock.patch.object(product, '_detach_remaining_window', side_effect=ContractError('HV2-WORKSPACE-PRODUCT', 'synthetic window refusal')) as check:
            with self.assertRaisesRegex(ContractError, 'synthetic window refusal'):
                product.workspace_detach_apply(self.target, packet['request'], confirm_token=packet['confirm_token'])
            self.assertEqual(1, check.call_count)
        self.assertFalse(marker.exists()); self.assertEqual(before, bytes_now())

    def test_windows_membership_includes_continuation_without_changing_historical_sets(self):
        p = self.prepared('p'); candidate = product.workspace_candidate(p)
        self.assertEqual(30, len(candidate['payload']))
        self.assertEqual(tuple(candidate['payload']), product.WINDOWS_MANAGED_PATHS)
        self.assertIn('src/hv2ref/continuation.py', candidate['payload'])
        for historical in (product.ENTRY_MANAGED_PATHS, product.DELEGATION_MANAGED_PATHS):
            self.assertEqual(29, len(historical)); self.assertNotIn('src/hv2ref/continuation.py', historical)
        self.assertEqual('continuation-1', product.workspace_candidate(SOURCE)['release_ref']['inventory_id'])


class WindowsContinuationPublicationTests(unittest.TestCase):
    def test_preflight_union_refuses_before_continuation_bytes_then_same_ticket_succeeds(self):
        fixture = continuation_cases.ContinuationTests()
        self.addCleanup(fixture.doCleanups)
        fixture.setUp()
        runtime = lambda target: {'binding_ref': copy.deepcopy(fixture.binding), 'launcher_sha256': None, 'inventory_id': 'windows-2'}
        fixture.store.runtime_check = runtime
        fixture.cont.work_store.runtime_check = runtime
        prepared = fixture.prepare_cont()
        before = fixture.bytes(); observed = []
        original_preflight = jsonio.windows_preflight_files
        def refuse(paths):
            paths = list(paths)
            if any('/continuation/' in p.as_posix() for p in paths):
                observed.extend(paths)
                raise ContractError('HV2-WINDOWS-READONLY', 'synthetic preflight refusal')
            return original_preflight(paths)
        with mock.patch.object(jsonio, 'windows_preflight_files', side_effect=refuse), self.assertRaisesRegex(ContractError, 'synthetic preflight refusal'):
            fixture.apply_cont(prepared)
        self.assertEqual(before, fixture.bytes())
        self.assertEqual(3, len(observed))
        self.assertTrue(all('/continuation/' in p.as_posix() for p in observed))
        self.assertTrue(any(p.name == 'current.json' for p in observed))
        fixture.apply_cont(prepared)
        self.assertIsNotNone(fixture.state()['current'])
        fixture.store._delegation_runtime(runtime(fixture.target))
