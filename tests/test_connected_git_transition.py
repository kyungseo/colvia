"""Connected-folder conversion uses real Git and an isolated manager."""
from contextlib import closing
from pathlib import Path
import os
import subprocess
import tempfile
import unittest

from colvia.adapters.git import Git
from colvia.cli import read_locator
from colvia.codec import RecordError
from colvia.connection import Connections
from colvia.effects import PENDING
from colvia.git_transition import GitTransition
from colvia.git_transition_record import KEY
from test_foundation_git import EXECUTABLE
from test_foundation_move import MoveFixture


class GitTransitionTests(MoveFixture, unittest.TestCase):
    def setUp(self):
        if not EXECUTABLE.is_file():
            self.skipTest('native Git fixture unavailable')
        area = tempfile.TemporaryDirectory()
        self.addCleanup(area.cleanup)
        self.base = Path(area.name).resolve()
        self.root = self.base/'docs'
        self.root.mkdir()
        self.report = self.root/'report.md'
        self.report.write_text('original')
        self.manager_fixture(self.base, Git(EXECUTABLE, environment=dict(os.environ, GIT_CONFIG_NOSYSTEM='1')))
        self.connect()
        self.converter = GitTransition(self.manager, self.setup.git)

    def git(self, *args):
        return subprocess.check_output([str(EXECUTABLE), '-C', str(self.root), *args], env=self.setup.git.env)

    def start_transition(self, checkpoint=lambda _: None):
        review = self.converter.preview(self.project, self.root)
        return self.converter.start(operation='convert', plan=review['plan'], receipt=review['receipt'],
                                    statement='Keep my work and use Git', checkpoint=checkpoint)

    def test_new_repository_resumes_after_publication(self):
        def interrupt(phase):
            if phase == 'repository-published':
                raise InterruptedError()
        with self.assertRaises(InterruptedError):
            self.start_transition(interrupt)
        with closing(self.authority.store()) as store:
            self.assertEqual(store.head(PENDING), store.head(KEY))
        # A crash in a private native publish can leave unpublished temp bytes.
        abandoned = self.manager.root/'operations'/'convert'/'new-locator-0'
        abandoned.mkdir(mode=0o700)
        (abandoned/'connection.json.prepared-example').write_bytes(b'unpublished')
        self.assertEqual('converted', self.converter.resume('convert')['state'])
        self.assertEqual({'connection.json'}, {p.name for p in (self.root/'.git/colvia').iterdir()})
        self.assertTrue((abandoned/'connection.json.prepared-example').exists())
        self.assertEqual('converted', self.converter.resume('convert')['state'])
        self.assertEqual(b'', self.git('ls-files'))
        self.assertEqual('original', self.report.read_text())
        self.assertFalse((self.root/'.colvia-link.json').exists())
        self.assertEqual(self.project, read_locator(self.root, self.setup.git).project)
        with closing(self.authority.store()) as store:
            self.assertIsNone(store.head(PENDING))
            self.assertEqual('git', Connections(store).workspace(self.workspace)[2].kind)
            result = self.work(store).plan(operation='next', work='new', title='New', goal='Edit',
                                           scope=['report.md'], checks=['read'], excludes=[])
            self.assertIn('receipt', result)

    def test_adopt_staged_and_unstaged_with_existing_commit(self):
        self.git('init','--quiet')
        self.git('add','report.md')
        self.git('-c','user.name=Local','-c','user.email=test@example.invalid','commit','--quiet','-m','Base')
        self.report.write_text('staged')
        self.git('add','report.md')
        self.report.write_text('unstaged')
        before = (self.root/'.git/index').read_bytes()
        head = self.git('rev-parse','HEAD')
        self.assertEqual('converted', self.start_transition()['state'])
        self.assertEqual(before, (self.root/'.git/index').read_bytes())
        self.assertEqual(head, self.git('rev-parse','HEAD'))
        self.assertEqual(b'staged', self.git('show',':report.md'))
        self.assertEqual('unstaged', self.report.read_text())

    def test_active_work_refuses_both_topologies(self):
        self.active()
        for existing in (False, True):
            if existing:
                self.git('init','--quiet')
            with self.assertRaisesRegex(RecordError, 'git-transition-unfinished-work'):
                self.converter.preview(self.project, self.root)
            with closing(self.authority.store()) as store:
                self.assertIsNone(store.head(PENDING))
                self.assertIsNone(store.head(KEY))


    def test_post_retirement_interruption_with_accepted_history_and_backup(self):
        from io import BytesIO
        from colvia.backup import ExportBudget, ImportedSnapshot, supported_requirements
        from colvia.backup_service import export_backup
        from colvia.codec import decode_envelope
        from colvia.graph import AuditBudget
        from colvia.records import application_registry, link
        from colvia.storage.restore import fill_candidate
        from colvia.storage.sqlite import GenerationStore

        self.active()
        self.report.write_text('accepted text')
        with closing(self.authority.store()) as store:
            svc = self.work(store)
            self.submit(svc, 'submitted')
            review = svc.review('report')
            svc.accept(operation='accept', work='report', receipt=review['receipt'], statement='Keep this')
            head = store.head('work:report')
            original = decode_envelope(head, store.load(head))
            refs = [head] + [link(original, name) for name in ('plan','approval','result','decision')]
            raw = [store.load(r) for r in refs]
        self.git('init', '--quiet')
        self.git('add', 'report.md')
        self.report.write_text('later text')
        index = (self.root/'.git/index').read_bytes()
        def stop(stage):
            if stage == 'plain-locator-retired':
                raise InterruptedError()
        with self.assertRaises(InterruptedError):
            self.start_transition(stop)
        self.assertEqual('converted', self.converter.resume('convert')['state'])
        self.assertEqual(index, (self.root/'.git/index').read_bytes())
        self.assertEqual('later text', self.report.read_text())
        with closing(self.authority.store()) as store:
            self.assertEqual(raw, [store.load(r) for r in refs])
            self.assertEqual(head, store.head('work:report'))
            svc = self.work(store)
            view = svc.view('report')
            self.assertEqual('completed', view['state'])
            with self.assertRaisesRegex(RecordError, 'git-transition-new-work-required'):
                svc.revise(operation='revise', work='report', receipt=view['reopen_receipt'], statement='Try again')
            final = store.root().ref
        registry = application_registry()
        caps = supported_requirements(registry)
        old = caps - {'schema:connection.git-transition:1'}
        scratch = self.base/'scratch'
        scratch.mkdir()
        archive = self.base/'after.backup'
        budget = AuditBudget(20000, 50000, 48*1024**2)
        export_backup(self.authority, destination=archive, scratch=scratch, operation='export',
                      graph_budget=budget, registry=registry)
        options = dict(budget=ExportBudget(20000, 48*1024**2), graph_budget=budget, registry=registry)
        with self.assertRaisesRegex(RecordError, 'import-capability-unavailable'):
            ImportedSnapshot(self.base/'old', BytesIO(archive.read_bytes()), capabilities=old, **options)
        with closing(ImportedSnapshot(self.base/'current', BytesIO(archive.read_bytes()), capabilities=caps,
                                      writable_capabilities=caps, **options)) as archive_view:
            db = self.base/'restored'
            db.mkdir(mode=0o700)
            with closing(GenerationStore.create(db/'records', project=self.project, instance='restored',
                         generation='restored', active_check=lambda: None, reader_capabilities=caps,
                         writer_capabilities=caps)) as copy:
                fill_candidate(copy, archive_view, operation='restore', unselected=lambda:None)
                self.assertEqual(final, copy.root().ref)
                self.assertEqual(head, copy.head('work:report'))
                self.assertEqual(raw, [copy.load(r) for r in refs])

    def test_changed_user_file_or_index_requires_fresh_preview(self):
        self.git('init','--quiet')
        for stage in (False, True):
            review = self.converter.preview(self.project, self.root)
            if stage:
                self.git('add','report.md')
            else:
                self.report.write_text('Changed since review')
            with self.assertRaisesRegex(RecordError, 'git-transition-review-changed'):
                self.converter.start(operation='stale', plan=review['plan'], receipt=review['receipt'], statement='Old')
            self.assertTrue((self.root/'.colvia-link.json').is_file())
            with closing(self.authority.store()) as store:
                self.assertIsNone(store.head(PENDING))

    def test_reconfirm_user_changes_after_git_creation(self):
        def stop(phase):
            if phase == 'repository-published':
                raise InterruptedError()
        with self.assertRaises(InterruptedError):
            self.start_transition(stop)
        self.git('add', 'report.md')
        self.report.write_text('working copy after staging')
        with self.assertRaises(RecordError):
            self.converter.resume('convert')
        before = (self.root/'.git/index').read_bytes()
        review = self.converter.resume('convert', preview=True)
        changes = review['changes_since_first_review']
        self.assertIn('report.md', changes['examples'])
        self.assertIn('report.md', changes['staged_examples'])
        self.assertTrue(changes['working_files'])
        self.report.write_text('newer working copy')
        with self.assertRaisesRegex(RecordError, 'git-transition-review-changed'):
            self.converter.resume('convert', receipt=review['receipt'], statement='Stale review')
        review = self.converter.resume('convert', preview=True)
        self.assertEqual('converted', self.converter.resume('convert', receipt=review['receipt'],
                         statement='Keep the current files and staging')['state'])
        self.assertEqual(before, (self.root/'.git/index').read_bytes())
        self.assertEqual('newer working copy', self.report.read_text())

    def test_manager_preview_apply_and_resume_with_old_git_init(self):
        from types import SimpleNamespace
        from colvia.updates.lease import RuntimeLease
        from test_foundation_slots import SlotTests
        from colvia.codec import canonical_bytes
        from colvia.manager_entry import parser, run
        from colvia.storage.sqlite import runtime_capabilities
        caps = runtime_capabilities()
        slots = self.manager.slots
        helper = SimpleNamespace(manager=slots)
        pointer = SlotTests.slot(helper, 'compatible', 1, extra=caps - {'foundation-v1'})
        slots.initialize(pointer)
        lease = RuntimeLease(slots)
        entry = SimpleNamespace(home=self.manager, git=lambda:self.setup.git, lease=lease)
        def manager(*args):
            return run(parser(bound=True).parse_args(args), entry)
        self.git('init', '--quiet')
        review = manager('git-transition-preview', str(self.root))
        path = self.base/'approved.json'
        self.manager.files.create(path, canonical_bytes(review))
        result = manager('git-transition-apply','--plan',str(path),'--receipt',review['receipt'],
                         '--statement','Use the repository','--operation','via-manager')
        self.assertEqual('converted', result['state'])
        self.assertEqual(result, manager('git-transition-resume', 'via-manager'))

    def test_external_init_after_reservation_cancel_then_adopt(self):
        def interrupt(phase):
            if phase == 'reserved':
                raise InterruptedError()
        with self.assertRaises(InterruptedError):
            self.start_transition(interrupt)
        self.git('init','--quiet')
        self.git('add','report.md')
        before = (self.root/'.git/index').read_bytes()
        with self.assertRaisesRegex(RecordError, 'git-transition-external-init'):
            self.converter.resume('convert', preview=True)
        self.assertEqual('cancelled', self.converter.resume('convert', cancel=True)['state'])
        self.assertEqual('cancelled', self.converter.resume('convert', cancel=True)['state'])
        with self.assertRaisesRegex(RecordError, 'git-transition-cancelled'):
            self.converter.resume('convert')
        with closing(self.authority.store()) as store:
            self.assertIsNone(store.head(PENDING))
            self.assertIsNone(store.head(KEY))
        again = self.converter.preview(self.project, self.root)
        self.converter.start(operation='adopt', plan=again['plan'], receipt=again['receipt'], statement='Adopt this Git')
        self.assertEqual(before, (self.root/'.git/index').read_bytes())

    def test_cannot_cancel_after_publishing_owned_repository(self):
        def stop(stage):
            if stage == 'repository-published':
                raise InterruptedError()
        with self.assertRaises(InterruptedError):
            self.start_transition(stop)
        with self.assertRaisesRegex(RecordError, 'git-transition-cancel-too-late'):
            self.converter.resume('convert', cancel=True)
        self.assertEqual('converted', self.converter.resume('convert')['state'])

    def test_new_work_can_be_accepted_and_then_committed(self):
        from colvia.git_integration import GitIntegration
        from colvia.platforms.darwin_git import DarwinGit
        from test_foundation_git_candidate import AUTHOR
        self.git('init','--quiet')
        self.git('add','report.md')
        self.git('-c','user.name=Local','-c','user.email=example@example.invalid','commit','--quiet','-m','Base')
        self.start_transition()
        self.active()
        self.report.write_text('approved git change')
        scratch = self.base/'git-integration'
        scratch.mkdir(mode=0o700)
        with closing(self.authority.store()) as store:
            service = self.work(store)
            self.submit(service, 'submit')
            service.accept(operation='accept', work='report', receipt=service.review('report')['receipt'],
                           statement='Accept the submitted result')
            integration = GitIntegration(store, service.workspace, DarwinGit(self.root, scratch, self.setup.git))
            preview = integration.prepare(operation='approved-git', works=['report'], message='Reviewed change',
                                          identity=AUTHOR)
            self.assertEqual('completed', integration.apply('approved-git', receipt=preview['receipt'],
                             statement='Commit this result')['state'])
        self.assertEqual(b'approved git change', self.git('show','HEAD:report.md'))

    def test_another_workspace_registration_blocks_conversion(self):
        with closing(self.authority.store()) as store:
            alias = 'workspace:11111111-1111-4111-8111-111111111111'
            store.commit_heads(operation='unexpected-registration', expected={alias:None},
                               changes={alias:store.head('workspace:'+self.workspace)}, validate=lambda _:None)
        with self.assertRaisesRegex(RecordError, 'git-transition-single-root-required'):
            self.converter.preview(self.project,self.root)

    def test_reserved_fence_rejects_open_old_writer_before_project_effect(self):
        from colvia.storage.authority import Authority
        from colvia.storage.sqlite import runtime_capabilities
        old_caps = runtime_capabilities() - {'schema:connection.git-transition:1'}
        old = Authority(self.authority.root, project=self.project, reader_capabilities=old_caps,
                        writer_capabilities=old_caps)
        with closing(old.store()) as existing:
            def stop(stage):
                if stage == 'reserved':
                    self.assertFalse((self.root/'.git').exists())
                    with self.assertRaisesRegex(RecordError, 'store-reader-capability-unavailable'):
                        existing.begin_import('stale-process','ordinary-plan')
                    with self.assertRaisesRegex(RecordError, 'store-reader-capability-unavailable'):
                        old.store()
                    raise InterruptedError()
            with self.assertRaises(InterruptedError):
                self.start_transition(stop)
        self.assertEqual('converted', self.converter.resume('convert')['state'])
