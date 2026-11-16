"""Use a synthetic installed home and an explicitly named download double."""

from contextlib import closing
import unittest
from unittest.mock import patch

from colvia.binding import Locator, ProjectBinding, Topology, WorkspaceRegistration
from colvia.codec import RecordError, canonical_bytes
from colvia.connection import Connections
from colvia.platforms.posix import location
from colvia.storage.authority import Authority
from colvia.storage.sqlite import runtime_capabilities
from colvia.updates.installation import bootstrap
from colvia.updates.lease import RuntimeLease
from colvia.updates.release import ReleaseUpdate
from colvia.updates.uninstall import Uninstall
from colvia.work import WorkService, work_key
from colvia.workspace import LocalWorkspace
from test_foundation_binding import I, P, W
from test_foundation_installation import InstallationTests as InstallFixture
from test_foundation_release_update import DownloadDouble


class UninstallTests(unittest.TestCase):
    archive = InstallFixture.archive
    install = InstallFixture.install
    tearDown = InstallFixture.tearDown

    def setUp(self):
        InstallFixture.setUp(self)
        self.manifest['features'] = ['managed-uninstall']
        capabilities = sorted(runtime_capabilities())
        self.manifest['read_capabilities'] = capabilities
        self.manifest['write_capabilities'] = capabilities
        archive, target = self.archive()
        self.versions = dict(root=1, snapshot=2, targets=2, timestamp=3)
        target.update(path=self.config['target'], versions=self.versions)
        self.trust = DownloadDouble(archive, target)
        self.install()
        self.home.files.create(self.home.root / 'updates.json', canonical_bytes({
            key: self.config[key] for key in ('version', 'channel', 'metadata_url', 'target_url', 'target')
        }))
        trust = self.home.root / 'trust'
        self.home.files.create_directory(trust)
        self.home.files.create(trust / 'state.json', canonical_bytes(dict(versions=self.versions)))
        self.addCleanup(patch.stopall)
        patch('colvia.updates.uninstall.require_default_home', return_value=None).start()
        self.removal = Uninstall(self.home)
        self.project = self.base / 'project'
        self.project.mkdir()
        locator = self.locator = Locator(P, I, 1, 'a' * 64, W)
        topology = Topology('plain', location(self.project))
        self.authority = Authority.create(self.home.root / 'authorities' / P,
                                          project=P, instance=I, generation='first')
        with closing(self.authority.store()) as store:
            Connections(store).connect(operation='connect', binding=ProjectBinding(locator, 'plain', topology.root),
                                       observed=topology, workspace=WorkspaceRegistration(W, topology.root, None),
                                       verify_topology=lambda: topology)
            service = WorkService(store, LocalWorkspace(store, self.project, W, locator_reader=lambda: locator))
            result = service.plan(operation='plan', work='report', title='Report', goal='One change',
                                  scope=['report.md'], checks=['one check'])
            service.approve(operation='approve', work='report', receipt=result['receipt'], statement='Proceed')
            service.start(operation='start', work='report')
            (self.project / 'report.md').write_text('retained body', encoding='utf-8')
            review = service.submit(operation='submit', work='report', summary='One change written',
                                    checks=[dict(name='one check', status='passed', detail='body confirmed')])
            service.accept(operation='accept', work='report', receipt=review['receipt'], statement='Accept')
            self.root_before = store.root().ref
            self.work_before = store.head(work_key('report'))

    def test_remove_then_reinstall_resumes_without_redownload_or_record_loss(self):
        def stop_after_move(phase):
            if phase == 'uninstall-after-move':
                raise RuntimeError('removed one owned file')

        receipt = self.removal.preview('remove-test')['receipt']
        with self.assertRaisesRegex(RuntimeError, 'one owned file'):
            self.removal.apply('remove-test', receipt, checkpoint=stop_after_move)
        with self.assertRaisesRegex(RecordError, 'uninstall-transition-pending'):
            RuntimeLease(self.home.slots)
        with self.assertRaisesRegex(RecordError, 'uninstall-not-complete'):
            self.removal.prepare_reinstall()
        self.assertEqual('removed', self.removal.apply('remove-test', receipt, resume=True)['state'])
        self.assertFalse((self.home.root / 'bin').exists())
        self.assertFalse((self.home.slots.root / 'slots/first').exists())
        self.assertTrue((self.home.root / 'trust/state.json').is_file())
        self.assertEqual('retained body', (self.project / 'report.md').read_text())

        binding, operation, _ = self.removal.prepare_reinstall()
        transition = ReleaseUpdate(self.home, self.trust, channel='preview', replacement=True,
                                   reinstall=(self.removal, binding))
        prepared = transition.prepare(operation=operation, target=self.config['target'])
        count = self.trust.calls

        def stop_during_aliases(phase):
            if phase == 'initial-after-publish':
                raise RuntimeError('published one node')

        with self.assertRaisesRegex(RuntimeError, 'published one node'):
            transition.apply(operation=operation, receipt=prepared['receipt'], checkpoint=stop_during_aliases)
        with self.assertRaisesRegex(RecordError, 'uninstall-transition-pending'):
            RuntimeLease(self.home.slots)
        transition.resume(operation=operation, receipt=prepared['receipt'])
        self.assertEqual(count, self.trust.calls)
        self.assertFalse((self.home.root / 'uninstall.json').exists())
        self.assertEqual(1, self.home.slots.selection()[1]['high_sequence'])
        self.assertEqual(operation, RuntimeLease(self.home.slots).verified.slot)
        self.assertEqual(self.content['bin/colvia'], (self.home.root / 'bin/colvia-manage').read_bytes())
        with closing(self.authority.store(readonly=True)) as store:
            self.assertEqual(self.root_before, store.root().ref)
            self.assertEqual(self.work_before, store.head(work_key('report')))

    def test_unowned_path_and_existing_pending_operation_block_before_any_move(self):
        foreign = self.home.root / 'bin/other.txt'
        foreign.write_bytes(b'other')
        with self.assertRaisesRegex(RecordError, 'uninstall-extra-installed-file'):
            self.removal.preview('remove-test')
        self.assertEqual(b'other', foreign.read_bytes())
        foreign.unlink()

        receipt = self.removal.preview('remove-test')['receipt']
        (self.home.root / 'notice-app.pending').write_bytes(b'pending')
        with self.assertRaisesRegex(RecordError, 'uninstall-other-operation-pending'):
            self.removal.apply('remove-test', receipt)
        self.assertFalse((self.home.root / 'uninstall.json').exists())
        self.assertTrue((self.home.root / 'bin/colvia').is_file())

    def test_refused_plan_cannot_publish_an_uninstall_marker(self):
        receipt = self.removal.preview('remove-test')['receipt']
        with patch.object(self.removal, '_validate_paths', side_effect=RecordError('uninstall-intent-invalid')):
            with self.assertRaisesRegex(RecordError, 'uninstall-intent-invalid'):
                self.removal.apply('remove-test', receipt)
        self.assertFalse((self.home.root / 'uninstall.json').exists())
        self.assertFalse((self.home.root / 'operations/remove-test').exists())
        self.assertEqual('first', RuntimeLease(self.home.slots).verified.slot)

    def test_active_work_refuses_removal_before_writing_a_receipt(self):
        with closing(self.authority.store()) as store:
            workspace = LocalWorkspace(store, self.project, W, locator_reader=lambda: self.locator)
            service = WorkService(store, workspace)
            result = service.plan(operation='plan-second', work='report-two', title='Second report',
                                  goal='A second change', scope=['second.md'], checks=['one check'])
            service.approve(operation='approve-second', work='report-two',
                            receipt=result['receipt'], statement='Proceed')
            service.start(operation='start-second', work='report-two')
        with self.assertRaisesRegex(RecordError, 'uninstall-active-work'):
            self.removal.preview('remove-test')
        self.assertFalse((self.home.root / 'uninstall.json').exists())

    def test_restore_partial_removal_requires_the_exact_review_receipt(self):
        def interrupt(phase):
            if phase == 'uninstall-after-move':
                raise RuntimeError('interrupted after move')

        receipt = self.removal.preview('remove-test')['receipt']
        with self.assertRaisesRegex(RuntimeError, 'interrupted after move'):
            self.removal.apply('remove-test', receipt, checkpoint=interrupt)
        with self.assertRaisesRegex(RecordError, 'uninstall-review-changed'):
            self.removal.restore('remove-test', 'a' * 64)
        self.assertEqual('removal-restored', self.removal.restore('remove-test', receipt)['state'])
        self.assertFalse((self.home.root / 'uninstall.json').exists())
        self.assertTrue((self.home.root / 'operations/remove-test/restore-removal-complete.json').is_file())
        self.assertEqual('first', RuntimeLease(self.home.slots).verified.slot)
        self.assertEqual(self.content['bin/colvia'], (self.home.root / 'bin/colvia-manage').read_bytes())
        with closing(self.authority.store(readonly=True)) as store:
            self.assertEqual(self.root_before, store.root().ref)
            self.assertEqual(self.work_before, store.head(work_key('report')))

    def test_resume_before_release_preparation_preserves_old_attempt(self):
        receipt = self.removal.preview('remove-test')['receipt']
        self.removal.apply('remove-test', receipt)
        binding, old, resume = self.removal.prepare_reinstall()
        self.assertFalse(resume)
        evidence = self.home.root / 'operations' / old
        self.home.files.create_directory(evidence)
        self.home.files.create(evidence / 'download-intent.json', b'original partial evidence')
        with self.assertRaisesRegex(RecordError, 'uninstall-reinstall-resume-required'):
            self.removal.prepare_reinstall()
        rebound, new, resume = self.removal.prepare_reinstall(resume=True)
        self.assertEqual(binding, rebound)
        self.assertNotEqual(old, new)
        self.assertFalse(resume)
        self.assertEqual(b'original partial evidence', (evidence / 'download-intent.json').read_bytes())
        with self.assertRaisesRegex(RecordError, 'uninstall-reinstall-intent-changed'):
            self.removal.reinstall_guard(binding, old)

    def test_unknown_removal_does_not_delegate_or_initialize_home(self):
        (self.home.root / 'uninstall.json').write_bytes(b'not a receipt')
        staged = self.base / 'bad-stage'
        staged.mkdir(mode=0o700)
        (staged / 'manifest.json').write_bytes(b'bad candidate')
        with patch('colvia.updates.installation.current_platform', return_value=('macos', 'arm64')):
            with self.assertRaisesRegex(RecordError, 'manifest-mismatch'):
                bootstrap(self.home.root, staged, '0' * 64,
                          launch=lambda *args: self.fail('existing manager must not be invoked'))
        self.assertEqual(b'not a receipt', (self.home.root / 'uninstall.json').read_bytes())
        self.assertTrue((self.home.root / 'bin/colvia').is_file())
