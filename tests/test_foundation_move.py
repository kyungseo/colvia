"""Source qualification of same-directory moves on synthetic authority records."""
from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
from io import BytesIO
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

from colvia.adapters.git import discover
from colvia.backup import ExportBudget, ImportedSnapshot, supported_requirements
from colvia.backup_service import export_backup
from colvia.binding import NativeLocation, WorkspaceRegistration
from colvia.cli import read_locator
from colvia.codec import RecordError, decode_envelope
from colvia.connection import Connections, PROJECT_KEY
from colvia.connection_identity import PROJECT_IDENTITY, same_directory
from colvia.effects import PENDING
from colvia.graph import AuditBudget
from colvia.move_setup import MoveSetup
from colvia.records import application_registry, link
from colvia.storage.authority import Authority
from colvia.work import WorkService, work_key
from colvia.workspace import LocalWorkspace
from test_foundation_git import GitFixture
from test_foundation_project_setup import SetupFixture


class MoveFixture(SetupFixture):
    def connect(self):
        self.begin()
        self.finish()
        self.project = self.preview['plan']['project']
        self.workspace = self.preview['plan']['workspace']
        self.authority = self.manager.authority(self.project)
        self.mover = MoveSetup(self.manager, self.setup.git)

    def work(self, store, root=None):
        root = root or self.root
        git = self.setup.git
        return WorkService(store, LocalWorkspace(store, root, self.workspace, git=git,
                           locator_reader=lambda: read_locator(root, git)))

    def active(self):
        with closing(self.authority.store()) as store:
            work = self.work(store)
            proposal = work.plan(operation='plan', work='report', title='Report', goal='One edit',
                                 scope=['report.md'], checks=['content'], excludes=[])
            work.approve(operation='approve', work='report', receipt=proposal['receipt'], statement='Owner approved')
            work.start(operation='start', work='report')
            head = store.head(work_key('report'))
            return head, link(decode_envelope(head, store.load(head)), 'approval')

    def relocate(self):
        self.destination = self.root.with_name('moved')
        self.root.rename(self.destination)
        return self.mover.preview(self.project, self.destination)

    def apply(self, review, operation='move-one', checkpoint=lambda _: None):
        return self.mover.start(operation=operation, plan=review['plan'], receipt=review['receipt'],
                                statement='Owner confirmed the new location', checkpoint=checkpoint)

    def assert_managed_view_after_move(self):
        from contextlib import redirect_stdout
        from io import StringIO
        from types import SimpleNamespace
        from colvia.cli import main
        from colvia.managed_entry import ManagedEntry
        import json

        self.active()
        self.apply(self.relocate())
        entry = ManagedEntry.__new__(ManagedEntry)
        entry.home = self.manager
        entry.lease = SimpleNamespace(check=lambda: None)
        entry.pointer = None
        entry.git = lambda: self.setup.git
        output = StringIO()
        with (patch('colvia.managed_entry.ManagedAuthority', return_value=self.authority),
              redirect_stdout(output)):
            code = main(['--root', str(self.destination), '--json', 'ordinary', 'view', 'report'], entry=entry)
        self.assertEqual(0, code, output.getvalue())
        self.assertEqual('active', json.loads(output.getvalue())['state'])

    def submit(self, work, operation):
        return work.submit(operation=operation, work='report', summary='Edited',
                           checks=[dict(name='content', status='passed', detail='Read all bytes')])


class PlainMoveTests(MoveFixture, unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='verified-move-')
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.root = self.base/'project'
        self.root.mkdir()
        (self.root/'report.md').write_bytes(b'original\n')
        self.manager_fixture(self.base)
        self.connect()

    def test_active_work_survives_move_and_reverse_with_exact_scope(self):
        head, approval = self.active()
        review = self.relocate()
        owned = {p.name: p.read_bytes() for p in self.destination.iterdir()}
        self.assertEqual('moved', self.apply(review)['state'])
        self.assertEqual(owned, {p.name: p.read_bytes() for p in self.destination.iterdir()})
        with closing(self.authority.store()) as store:
            self.assertEqual(head, store.head(work_key('report')))
            work = self.work(store, self.destination)
            (self.destination/'report.md').write_bytes(b'revised\n')
            foreign = self.destination/'not-approved.md'
            foreign.write_bytes(b'foreign')
            with self.assertRaisesRegex(RecordError, 'outside-scope-change'):
                self.submit(work, 'rejected')
            self.assertEqual(head, store.head(work_key('report')))
            self.assertFalse(store.has_active_imports())
            foreign.unlink()
            self.submit(work, 'submitted')
            updated = store.head(work_key('report'))
            approved = link(decode_envelope(updated, store.load(updated)), 'approval')
            self.assertEqual(approval, approved)
        with closing(self.authority.store(readonly=True)) as store:
            manual = self.work(store, self.destination)
            self.assertEqual('review', manual.view('report')['state'])
            self.assertTrue(manual.view('report')['current_matches'])
        self.destination.rename(self.root)
        again = self.mover.preview(self.project, self.root)
        self.assertEqual('moved', self.apply(again, 'move-back')['state'])
        self.assertEqual('subsequently-changed', self.mover.resume('move-one')['state'])
        with closing(self.authority.store(readonly=True)) as store:
            self.assertTrue(self.work(store).view('report')['current_matches'])

    def test_handed_off_approval_can_resume_once_before_and_after_publication(self):
        first = self.relocate()
        def interrupted(point):
            def checkpoint(current):
                if point == current:
                    raise RuntimeError('interrupted')
            return checkpoint
        with self.assertRaises(RuntimeError):
            self.apply(first, checkpoint=interrupted('intent'))
        self.assertEqual('pending', self.mover.status('move-one')['state'])
        self.assertTrue(self.destination.is_dir())
        with self.assertRaises(RuntimeError):
            self.mover.resume('move-one', checkpoint=interrupted('published'))
        self.assertEqual('moved', self.mover.status('move-one')['state'])
        self.assertEqual('moved', self.mover.resume('move-one')['state'])
        with closing(self.authority.store(readonly=True)) as store:
            self.assertIsNotNone(store.operation_result('move-one'))

    def test_copy_and_occupied_or_unavailable_original_refuse(self):
        copied = self.root.with_name('copy')
        shutil.copytree(self.root, copied)
        with self.assertRaisesRegex(RecordError, 'connection-move-identity-changed'):
            self.mover.preview(self.project, copied)
        review = self.relocate()
        self.root.mkdir()
        with self.assertRaisesRegex(RecordError, 'connection-move-original-present'):
            self.apply(review)
        self.root.rmdir()
        from colvia.move_setup import location
        def denied(path):
            if path == self.root:
                raise PermissionError('synthetic unreadable original')
            return location(path)
        with patch('colvia.move_setup.location', side_effect=denied), self.assertRaises(PermissionError):
            self.apply(review)
        self.assertFalse((self.manager.root/'operations/move-one').exists())

    def test_new_nested_project_marker_invalidates_preview(self):
        review = self.relocate()
        inner = self.destination/'nested'
        inner.mkdir()
        (inner/'.colvia-link.json').write_bytes(b'foreign locator')
        with self.assertRaisesRegex(RecordError, 'workspace-nested-project'):
            self.apply(review)
        self.assertFalse((self.manager.root/'operations/move-one').exists())
        self.assertEqual(b'foreign locator', (inner/'.colvia-link.json').read_bytes())

    def test_pending_import_blocks_move(self):
        review = self.relocate()
        with closing(self.authority.store()) as store:
            store.begin_import('waiting-git-object', 'git-candidate')
        with self.assertRaisesRegex(RecordError, 'connection-move-work-pending'):
            self.apply(review)
        self.assertFalse((self.manager.root/'operations/move-one').exists())
        self.destination.rename(self.root)
        with closing(self.authority.store()) as store:
            self.assertIsNone(store.head(PENDING))

    def test_effect_reservation_wins_after_move_validation(self):
        review = self.relocate()
        prepare = self.mover._candidate
        def reserve():
            with closing(self.authority.store()) as writer:
                binding = writer.head(PROJECT_KEY)
                writer.commit_heads(operation='reserve', expected={PENDING:None}, changes={PENDING:binding},
                                    validate=lambda _: None)
        with ThreadPoolExecutor() as executor:
            def candidate(authority, store, root):
                value = prepare(authority, store, root)
                if (self.manager.root/'operations/move-one/move.json').exists():
                    executor.submit(reserve).result(timeout=12)
                return value
            with patch.object(self.mover, '_candidate', side_effect=candidate):
                with self.assertRaisesRegex(RecordError, 'validation-root-conflict|head-conflict'):
                    self.apply(review)
        with closing(self.authority.store(readonly=True)) as store:
            self.assertIsNotNone(store.head(PENDING))
            self.assertIsNone(store.operation_result('move-one'))

    def test_move_wins_after_writer_validated_and_before_writer_commit(self):
        with closing(self.authority.store()) as writer, ThreadPoolExecutor() as executor:
            self.work(writer).workspace.verify()
            binding = writer.head(PROJECT_KEY)
            review = self.relocate()
            def pause(view):
                self.assertIsNone(view.head('writer'))
                result = executor.submit(self.apply, review).result(timeout=12)
                self.assertEqual('moved', result['state'])
            with self.assertRaisesRegex(RecordError, 'workspace-location-changed'):
                writer.commit_heads(operation='stale-write', expected={'writer':None}, changes={'writer':binding},
                                    validate=pause)
            self.assertIsNone(writer.head('writer'))
            with self.assertRaisesRegex(RecordError, 'workspace-location-changed'):
                writer.begin_import('late-effect-start', 'git-candidate')

    def test_moved_store_and_backup_require_new_reader_but_preserve_existing_work(self):
        work_head, _ = self.active()
        registry = application_registry()
        caps = supported_requirements(registry)
        old = caps - {'schema:connection.identity:2'}
        with closing(self.authority.store(readonly=True)) as store:
            self.assertLessEqual(set(store.requirements()['read']), old)
        self.apply(self.relocate())
        old_authority = Authority(self.authority.root, project=self.project, reader_capabilities=old)
        with self.assertRaisesRegex(RecordError, 'store-reader-capability-unavailable'):
            old_authority.store(readonly=True)
        scratch = self.base/'backup-scratch'
        scratch.mkdir()
        destination = self.base/'moved.backup'
        budget = AuditBudget(10000, 10000, 32*1024*1024)
        export_backup(self.authority, destination=destination, scratch=scratch, operation='backup-move',
                      graph_budget=budget, registry=registry)
        options = dict(budget=ExportBudget(10000, 32*1024*1024), graph_budget=budget, registry=registry)
        with self.assertRaisesRegex(RecordError, 'import-capability-unavailable'):
            ImportedSnapshot(self.base/'old-reader.sqlite3', BytesIO(destination.read_bytes()), capabilities=old, **options)
        with closing(ImportedSnapshot(self.base/'compatible.sqlite3', BytesIO(destination.read_bytes()),
                                      capabilities=caps, writable_capabilities=caps, **options)) as restore:
            self.assertTrue(restore.writable)
            moved_root = restore.audit.root
            self.authority.import_candidate('restored', restore, operation='restore-move')
            self.authority.activate('activate-copy', target_generation='restored', expected_root=moved_root,
                                    validate_effects=lambda _: None, validate_target=lambda _: None)
        with closing(self.authority.store(readonly=True)) as store:
            self.assertEqual(work_head, store.head(work_key('report')))
            self.assertIsNotNone(store.head(PROJECT_IDENTITY))

    def test_plain_managed_view_uses_effective_location(self):
        self.assert_managed_view_after_move()

    def test_nonterminal_execution_and_delivery_preparations_block_move(self):
        from colvia.move_setup import _check_idle
        from colvia.records import record
        from uuid import uuid4

        cases = (
            ('execution', 'execution.grant', 'status', 'incomplete', 'completed'),
            ('delivery', 'delivery.request', 'phase', 'active', 'finished'),
        )
        with closing(self.authority.store()) as store:
            for namespace, grant_kind, field, open_value, closed_value in cases:
                token = uuid4().hex
                prepared_name = f'{namespace}-prepared:{token}'
                state_name = f'{namespace}:{token}'
                grant = record(grant_kind, {}, {})
                active = record(namespace+'.state', {field:open_value}, {})
                closed = record(namespace+'.state', {field:closed_value}, {})
                store.commit_heads(operation=token, expected={prepared_name:None,state_name:None},
                                   changes={prepared_name:grant[0],state_name:active[0]},
                                   objects=[grant,active],validate=lambda _:None)
                with self.assertRaisesRegex(RecordError,'connection-move-work-pending'):
                    _check_idle(store)
                store.commit_heads(operation=token+'-finish',expected={state_name:active[0]},
                                   changes={state_name:closed[0]},objects=[closed],validate=lambda _:None)
                _check_idle(store)

    def test_three_distinct_paths_retain_the_original_work(self):
        head, _ = self.active()
        self.apply(self.relocate())
        third = self.root.with_name('third')
        self.destination.rename(third)
        self.apply(self.mover.preview(self.project, third), 'move-two')
        with closing(self.authority.store()) as store:
            self.assertEqual(head, store.head(work_key('report')))
            work = self.work(store, third)
            (third/'report.md').write_bytes(b'after two moves\n')
            self.assertEqual('review',self.submit(work, 'submit-after-two-moves')['state'])

    def test_pre_move_backup_requires_explicit_rebind(self):
        work_head, _ = self.active()
        registry = application_registry()
        caps = supported_requirements(registry)
        scratch = self.base/'scratch'
        scratch.mkdir()
        archive = self.base/'before.backup'
        budget = AuditBudget(10000, 10000, 32*1024*1024)
        export_backup(self.authority, destination=archive, scratch=scratch, operation='backup-before',
                      graph_budget=budget, registry=registry)
        self.apply(self.relocate())
        with closing(self.authority.store(readonly=True)) as store:
            current = store.root().ref
        from uuid import uuid4
        instance = str(uuid4())
        with closing(ImportedSnapshot(self.base/'before-reader.sqlite3', BytesIO(archive.read_bytes()),
                                      budget=ExportBudget(10000, 32*1024*1024), graph_budget=budget,
                                      registry=registry, capabilities=caps, writable_capabilities=caps)) as source:
            self.authority.import_candidate('before-copy', source, operation='restore-copy', instance=instance)
            self.authority.activate_restore('switch', target_generation='before-copy', instance=instance,
                                            expected_root=current, target_root=source.audit.root,
                                            validate_effects=lambda _: None, validate_target=lambda _: None)
        with closing(self.authority.store()) as store:
            self.assertEqual(work_head, store.head(work_key('report')))
            self.assertTrue(store.needs_rebind())
            with self.assertRaisesRegex(RecordError, 'authority-binding-mismatch'):
                self.work(store, self.destination).workspace.verify()
        from colvia.restored_setup import RestoredSetup
        rebind = RestoredSetup(self.manager)
        p = rebind.preview(self.project, self.destination)
        self.assertEqual(['.colvia-link.json'], p['files'])
        rebind.start(operation='explicit', plan=p['plan'], receipt=p['receipt'], statement='Confirm restored connection')
        self.assertEqual('connected', rebind.resume('explicit')['state'])
        with closing(self.authority.store(readonly=True)) as store:
            self.assertEqual(work_head, store.head(work_key('report')))
            self.assertFalse(store.needs_rebind())


class GitMoveTests(MoveFixture, GitFixture, unittest.TestCase):
    def setUp(self):
        GitFixture.setUp(self)
        self.manager_fixture(self.home, self.git)
        self.connect()

    def test_git_config_origin_moves_with_single_root_and_later_worktree_can_register(self):
        self.active()
        review = self.relocate()
        self.assertEqual('moved', self.apply(review)['state'])
        with closing(self.authority.store()) as store:
            work = self.work(store, self.destination)
            (self.destination/'report.md').write_bytes(b'Git is still in scope\n')
            self.submit(work, 'git-submitted')
            self.assertTrue(work.view('report')['current_matches'])
        other = self.home/'linked'
        self.command('worktree', 'add', '-q', '-b', 'later', str(other), root=self.destination)
        top = discover(other, self.git)
        from uuid import uuid4
        linked = WorkspaceRegistration(str(uuid4()), top.root, top.gitdir)
        with closing(self.authority.store()) as store:
            con = Connections(store)
            con.register(operation='linked-later', locator=read_locator(other, self.git), observed=top,
                         workspace=linked, registrations=con.registrations(top, complete=True),
                         verify_topology=lambda: discover(other, self.git))
            self.assertEqual(linked, con.workspace(linked.workspace)[1])

    def test_git_managed_view_uses_effective_location(self):
        self.assert_managed_view_after_move()

    def test_git_policy_drift_is_not_an_approved_move(self):
        self.active()
        review = self.relocate()
        self.command('config', 'core.filemode', 'false', root=self.destination)
        with self.assertRaisesRegex(RecordError, 'connection-move-policy-changed'):
            self.apply(review)

    def git_service(self, store):
        from colvia.git_integration import GitIntegration
        from colvia.platforms.darwin_git import DarwinGit
        scratch=self.home/'scratch'
        scratch.mkdir(mode=0o700)
        return GitIntegration(store,self.work(store).workspace,DarwinGit(self.root,scratch,self.git))

    def accepted(self, store):
        work=self.work(store)
        self.active()
        (self.root/'report.md').write_bytes(b'Accepted candidate\n')
        proposal=self.submit(work,'submit')
        work.accept(operation='approve-result',work='report',receipt=proposal['receipt'],statement='Accept this result')

    def test_input_rejection_and_reaped_git_child_do_not_block_move(self):
        from test_foundation_git_candidate import AUTHOR
        with closing(self.authority.store()) as store:
            service=self.git_service(store)
            self.accepted(store)
            with self.assertRaisesRegex(RecordError,'git-author-required'):
                service.prepare(operation='bad-input', works=['report'], message='Prepare', identity={})
            self.assertFalse(store.has_active_imports())
            edited={**AUTHOR, 'date':'definitely not a valid Git date'}
            with self.assertRaisesRegex(RecordError,'git-integration-command-failed'):
                service.prepare(operation='bad-date', works=['report'], message='Prepare', identity=edited)
            self.assertFalse(service.port.child_pending)
            self.assertFalse(store.has_active_imports())
            row=store.db.execute("SELECT state FROM imports WHERE id='bad-date-prepare'").fetchone()
            self.assertEqual('abandoned',row['state'])
        self.assertEqual('review',self.relocate()['state'])

    def test_git_object_preparation_holds_import_before_the_first_write(self):
        from test_foundation_git_candidate import AUTHOR
        with closing(self.authority.store()) as store:
            service=self.git_service(store)
            self.accepted(store)
            port=service.port
            run=port.children.run
            def interrupted(argv, **kwargs):
                if 'hash-object' in argv and '-w' in argv:
                    self.assertTrue(store.has_active_imports())
                    raise RecordError('git-child-outcome-unknown')
                return run(argv, **kwargs)
            with patch.object(port.children,'run',side_effect=interrupted):
                with self.assertRaisesRegex(RecordError,'git-child-outcome-unknown'):
                    service.prepare(operation='git-preparing',works=['report'],message='Prepare',identity=AUTHOR)
            self.assertTrue(port.child_pending)
            self.assertTrue(store.has_active_imports())
        self.destination = self.root.with_name('moved')
        self.root.rename(self.destination)
        with self.assertRaisesRegex(RecordError, 'connection-move-work-pending'):
            self.mover.preview(self.project, self.destination)

    def test_successful_git_preparation_publishes_and_closes_its_attempt(self):
        from test_foundation_git_candidate import AUTHOR
        with closing(self.authority.store()) as store:
            service=self.git_service(store)
            self.accepted(store)
            p=service.prepare(operation='approved-git',works=['report'],message='Approved result',identity=AUTHOR)
            self.assertEqual('prepared',p['state'])
            self.assertFalse(store.has_active_imports())
            self.assertEqual('completed',service.apply('approved-git',receipt=p['receipt'],statement='Apply exact candidate')['state'])
        self.assertEqual('review',self.relocate()['state'])

    def test_linked_worktree_prevents_moving_the_primary(self):
        other = self.home/'linked'
        self.command('worktree', 'add', '-q', '-b', 'other', str(other))
        from colvia.binding import Membership
        top = discover(self.root, self.git)
        extra = Membership(discover(other, self.git).root, discover(other, self.git).gitdir)
        self.assertIn(extra, top.members)
        self.destination = self.root.with_name('moved')
        self.root.rename(self.destination)
        with self.assertRaisesRegex(RecordError, 'connection-move-topology'):
            self.mover.preview(self.project, self.destination)


class WindowsIdentityTests(unittest.TestCase):
    def test_folder_identity_checks_the_full_file_id_and_creation(self):
        old = NativeLocation(r'C:\one', '314', 'a'*32 + ':567')
        self.assertTrue(same_directory(old, NativeLocation(r'C:\two', '314', 'a'*32 + ':567')))
        self.assertFalse(same_directory(old, NativeLocation(r'C:\two', '314', 'b'*32 + ':567')))
        self.assertFalse(same_directory(old, NativeLocation(r'C:\two', '314', 'a'*32 + ':568')))
        self.assertFalse(same_directory(old, NativeLocation(r'D:\two', '315', 'a'*32 + ':567')))



class ManagedMoveDiagnosisTests(unittest.TestCase):
    def test_windows_case_spelling_uses_existing_binding_and_new_path_needs_review(self):
        from types import SimpleNamespace
        from colvia.binding import Locator, ProjectBinding, Topology
        from colvia.managed_entry import ManagedEntry
        from test_foundation_binding import P, I, W
        root = NativeLocation(r'C:\Users\Probe\Project', '13', 'a'*32 + ':17')
        locator = Locator(P, I, 1, 'a'*64, W)
        store = SimpleNamespace(close=lambda: None)
        authority = SimpleNamespace(pointer_value=lambda: {'instance': I}, store=lambda **_: store)
        entry = SimpleNamespace(lease=SimpleNamespace(check=lambda: None), git=lambda: None,
                                home=SimpleNamespace(root=Path('/manager'), files=None, slots=None), pointer=None)
        connections = SimpleNamespace(binding=lambda: (None, ProjectBinding(locator, 'plain', root)),
                                      registrations=lambda _: (WorkspaceRegistration(W, root, None),))
        alias = Topology('plain', NativeLocation(r'c:\users\probe\PROJECT', root.volume, root.file_id))
        moved = Topology('plain', NativeLocation(r'C:\Users\Probe\Moved', root.volume, root.file_id))
        with (patch('colvia.managed_entry.ManagedAuthority', return_value=authority),
              patch('colvia.managed_entry.Connections', return_value=connections),
              patch('colvia.managed_entry.LocalWorkspace'),
              patch('colvia.cli.read_locator', return_value=locator),
              patch('colvia.connection_boundary.workspace_topology', side_effect=[alias, moved])):
            observed = ManagedEntry.workspace(entry, Path(alias.root.path), readonly=True)
            self.assertIs(store, observed[1])
            with self.assertRaisesRegex(RecordError, 'connection-move-review-required'):
                ManagedEntry.workspace(entry, Path(moved.root.path), readonly=True)


class ManagementArgumentsTests(unittest.TestCase):
    def test_management_root_spelling_and_new_move_command(self):
        from contextlib import redirect_stderr
        from io import StringIO
        from colvia.manager_entry import parser
        standard=['--runtime-slot','slot','--runtime-manifest-sha256','a'*64,'status']
        with self.assertRaises(SystemExit), redirect_stderr(StringIO()):
            parser().parse_args(['--management-r','/manager',*standard])
        self.assertEqual('status',parser().parse_args(['--management-root','/manager',*standard]).command)
        move=parser(bound=True).parse_args(['move-preview','project','/new-location'])
        self.assertEqual(('move-preview','project',Path('/new-location')),(move.command,move.project,move.root))
