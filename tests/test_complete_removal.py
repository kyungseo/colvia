"""Run complete removal only on isolated user-owned installation fixtures."""
import os
import multiprocessing
import unittest
from unittest.mock import patch

from colvia.codec import RecordError
from colvia.project_setup import ProjectSetup
from colvia.updates.purge import CompleteRemoval
from colvia.updates.lease import RuntimeLease
import test_foundation_uninstall as uninstall_fixture


def run_until_checkpoint(root, receipt, stage, resume):
    from colvia.storage.files import platform_files
    with patch('colvia.updates.purge.standard_account'):
        purge = CompleteRemoval(root, platform_files(), 'macos', 'arm64', 'test-cleanup')
    def interrupt(phase):
        if phase == stage:
            os._exit(77)
    result = purge.apply(receipt, resume=resume, exclude=not resume, checkpoint=interrupt)
    if result['state'] != 'account-removed':
        raise AssertionError(result['state'])


@unittest.skipUnless(os.name=='posix' and __import__('sys').platform=='darwin', 'APFS installation fixtures')
class RemovalTests(unittest.TestCase):
    def setUp(self):
        self.fixture = uninstall_fixture.UninstallTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.addCleanup(self.fixture.tearDown)
        self.home = self.fixture.home
        self.root = self.fixture.base/'second'
        self.root.mkdir()
        self.rules = self.root/'AGENTS.md'
        self.rules.write_bytes(b'User rules.\n')
        setup = ProjectSetup(self.home)
        choice = setup.preview(self.root)
        setup.start(operation='join', plan=choice['plan'], receipt=choice['receipt'], statement='Connect')
        for _ in choice['plan']['changes']:
            setup.resume('join')
        self.assertNotEqual(0, os.getuid())
        with patch('colvia.updates.purge.standard_account') as guard:
            self.purge = CompleteRemoval(self.home.root, self.home.files, 'macos', 'arm64','test-cleanup')
            guard.assert_called_once()

    def test_first_preview_exclusion_and_resume_after_db(self):
        previous = self.home.root.parent/'Colvia-bootstrap-old'
        previous.mkdir()
        self.assertIn(str(previous), self.purge.preview()['retained_preparation_paths'])
        self.assertIsNone(self.purge.preview()['receipt'])
        view = self.purge.preview(True)
        self.assertEqual({'connected','excluded'}, {p['state'] for p in view['projects']})
        with self.assertRaisesRegex(RecordError, 'review-changed'):
            self.purge.apply('0'*64, exclude=True)
        def stop(phase):
            if phase == 'after-db':
                raise InterruptedError()
        with self.assertRaises(InterruptedError):
            self.purge.apply(view['receipt'], exclude=True, checkpoint=stop)
        self.assertTrue(self.purge.held.is_dir())
        self.assertEqual(b'User rules.\n', self.rules.read_bytes())
        self.assertFalse((self.root/'colvia').exists())
        self.home.root.mkdir(mode=0o700)
        fresh = self.home.root/'home.json'
        fresh.write_bytes(b'new installation')
        ident = fresh.stat().st_ino
        result = self.purge.apply(view['receipt'], resume=True)
        self.assertEqual('account-removed', result['state'])
        self.assertEqual(1, len(result['excluded']))
        self.assertEqual((ident,b'new installation'),(fresh.stat().st_ino,fresh.read_bytes()))
        self.assertFalse(self.purge.journal.exists())
        self.assertTrue(previous.is_dir())

    def test_record_preserving_uninstall_routes_to_manual_cleanup(self):
        ordinary = self.fixture.removal
        receipt = ordinary.preview('keep-records')['receipt']
        ordinary.apply('keep-records', receipt)
        before = (self.home.root/'uninstall.json').read_bytes()
        preview = self.purge.preview()
        self.assertEqual('records-retained-after-uninstall', preview['state'])
        self.assertIsNone(preview['receipt'])
        self.assertEqual(before, (self.home.root/'uninstall.json').read_bytes())

    def test_writer_and_unclaimed_file_stop_before_detach(self):
        view = self.purge.preview(True)
        with self.home.files.exclusion(self.home.slots.root/'runtime.lock', shared=True):
            with self.assertRaisesRegex(RecordError,'busy'):
                self.purge.apply(view['receipt'],exclude=True)
        path = self.home.root/'personal-notes'
        path.write_bytes(b'private bytes')
        with self.assertRaisesRegex(RecordError,'unclaimed-account-item'):
            self.purge.apply(view['receipt'],exclude=True)
        self.assertTrue((self.root/'colvia').exists())
        self.assertEqual(b'private bytes',path.read_bytes())

    def test_resume_from_partial_project_and_block_old_writer(self):
        view = self.purge.preview(True)
        def stop(phase):
            if phase == 'project-step':
                raise InterruptedError()
        with self.assertRaises(InterruptedError):
            self.purge.apply(view['receipt'],exclude=True,checkpoint=stop)
        with self.assertRaisesRegex(RecordError,'uninstall-transition-pending'):
            RuntimeLease(self.home.slots)
        self.assertEqual('account-removed',self.purge.apply(view['receipt'],resume=True)['state'])

    def test_review_fence_blocks_other_maintenance(self):
        from colvia.updates.uninstall import Uninstall, MARKER
        view = self.purge.preview(True)
        receipt = view['receipt']
        def interrupt(phase):
            if phase == 'fenced':
                raise InterruptedError()
        with self.assertRaises(InterruptedError):
            self.purge.apply(receipt, exclude=True, checkpoint=interrupt)
        fence = self.home.root / MARKER
        before = fence.read_bytes()
        other = Uninstall(self.home)
        for action in (lambda: other.restore('test-cleanup', receipt),
                       lambda: other.apply('test-cleanup', receipt, resume=True),
                       other.check_reinstall):
            with self.assertRaises(RecordError):
                action()
            self.assertEqual(before, fence.read_bytes())
        self.assertEqual('account-removed', self.purge.apply(receipt, resume=True)['state'])

    def test_resume_between_final_inventory_and_seal(self):
        view = self.purge.preview(True)
        def interrupt(phase):
            if phase == 'inventory-saved':
                raise InterruptedError()
        with self.assertRaises(InterruptedError):
            self.purge.apply(view['receipt'], exclude=True, checkpoint=interrupt)
        self.assertEqual(b'User rules.\n', self.rules.read_bytes())
        result = self.purge.apply(view['receipt'], resume=True)
        self.assertEqual('account-removed', result['state'])

    def test_process_exit_at_each_journal_boundary(self):
        # One approval, several separate processes. os._exit deliberately skips
        # Python cleanup and the platform releases the dead process's locks.
        receipt = self.purge.preview(True)['receipt']
        stages = ('publish-fence', 'fenced', 'journal-created', 'publish-approval',
                  'publish-inventory', 'publish-seal', 'publish-retirement', 'publish-completion')
        for index, stage in enumerate((*stages, None)):
            child = multiprocessing.get_context('spawn').Process(
                target=run_until_checkpoint, args=(self.home.root, receipt, stage, index > 0))
            child.start()
            child.join(45)
            if child.is_alive():
                child.kill()
                child.join()
            self.assertEqual(77 if stage else 0, child.exitcode, stage)
        self.assertEqual(b'User rules.\n', self.rules.read_bytes())
        self.assertFalse(self.home.root.exists())
        self.assertFalse(self.purge.journal.exists())
        self.assertFalse(self.purge.held.exists())
        self.assertEqual([], list(self.home.root.parent.glob('Colvia-removal-*')))

    def test_resume_requires_started_operation(self):
        receipt = self.purge.preview(True)['receipt']
        with self.assertRaisesRegex(RecordError, 'purge-operation-not-started'):
            self.purge.apply(receipt, resume=True)
        self.assertEqual(receipt, self.purge.preview(True)['receipt'])
        self.assertFalse(self.purge.journal.exists())

    def test_unknown_pending_bytes_are_preserved(self):
        from colvia.updates.purge_progress import pending_path
        receipt = self.purge.preview(True)['receipt']
        def interrupt(phase):
            if phase == 'publish-approval':
                raise InterruptedError()
        with self.assertRaises(InterruptedError):
            self.purge.apply(receipt, exclude=True, checkpoint=interrupt)
        path = pending_path(self.purge.journal, receipt, 'approval')
        original = path.read_bytes()
        for body in (original, b'unrelated content', b''):
            with self.subTest(same_bytes=(body == original), length=len(body)):
                # Keep the prior inode alive so its number cannot be recycled.
                path.rename(self.fixture.base/('preserved-' + str(len(body))))
                path.write_bytes(body)
                old = path.stat().st_ino
                with self.assertRaises(RecordError):
                    self.purge.apply(receipt, resume=True)
                self.assertEqual((old, body), (path.stat().st_ino, path.read_bytes()))
        self.assertTrue((self.root/'colvia').exists())

    def test_git_partial_staging_and_previously_unavailable_folder(self):
        from test_foundation_git import GitFixture
        git = GitFixture()
        git.setUp()
        self.addCleanup(git.tearDown)
        setup = ProjectSetup(self.home, git.git)
        plan = setup.preview(git.root)
        setup.start(operation='join-git', plan=plan['plan'], receipt=plan['receipt'], statement='Connect')
        for _ in plan['plan']['changes']:
            setup.resume('join-git')
        report = git.root/'report.md'
        report.write_text('staged text')
        git.command('add','report.md')
        report.write_text('unstaged text')
        index = git.root/'.git/index'
        before = index.read_bytes()
        self.root.rename(self.fixture.base/'moved')
        with patch('colvia.updates.purge.configured_git',return_value=git.git):
            view = self.purge.preview(True)
            self.assertEqual(2,sum(p['state']=='excluded' for p in view['projects']))
            def stop(phase):
                if phase=='project-step':
                    raise InterruptedError()
            with self.assertRaises(InterruptedError):
                self.purge.apply(view['receipt'], exclude=True, checkpoint=stop)
            self.root.mkdir()
            sample = self.root/'colvia'
            sample.write_bytes(b'user replacement')
            self.purge.apply(view['receipt'],resume=True)
        self.assertEqual(b'user replacement',sample.read_bytes())
        self.assertEqual(before,index.read_bytes())
        self.assertEqual('unstaged text',report.read_text())
        self.assertFalse((git.root/'.git/colvia/connection.json').exists())
