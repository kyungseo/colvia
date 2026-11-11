from contextlib import closing
import hashlib,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from colvia.codec import RecordError,canonical_bytes
from colvia.management import ManagerHome
from colvia.project_setup import ProjectSetup,BLOCK
from colvia.effects import PENDING
from colvia.connection import PROJECT_KEY
from test_foundation_git import GitFixture

class SetupFixture:
    def manager_fixture(self,base,git=None):
        self.manager=ManagerHome.create(base/'manager',os_name='macos',architecture='arm64')
        (self.manager.root/'bin').mkdir(mode=0o700);raw=b'Synthetic native entry; never execute'
        entry=self.manager.root/'bin/colvia';entry.write_bytes(raw);entry.chmod(0o700)
        (self.manager.root/'entry.json').write_bytes(canonical_bytes(dict(version=1,os='macos',architecture='arm64',sha256=hashlib.sha256(raw).hexdigest())))
        self.setup=ProjectSetup(self.manager,git)
    def begin(self):
        self.preview=self.setup.preview(self.root)
        self.setup.start(operation='connect',plan=self.preview['plan'],receipt=self.preview['receipt'],statement='이 폴더에 적용')
    def finish(self):
        value=None
        for _ in range(4):value=self.setup.resume('connect')
        self.assertEqual('connected',value['state']);return value

class SetupTests(SetupFixture,unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='project-setup-');self.base=Path(self.tmp.name)
        self.root=self.base/'project';self.root.mkdir();self.manager_fixture(self.base)
    def tearDown(self):self.tmp.cleanup()
    def test_empty_project_connects_locator_last_with_retained_records(self):
        self.begin();self.assertFalse((self.root/'.colvia-link.json').exists())
        for _ in range(3):self.assertEqual('pending',self.setup.resume('connect')['state'])
        self.assertFalse((self.root/'.colvia-link.json').exists())
        self.assertEqual('connected',self.setup.resume('connect')['state'])
        self.assertTrue((self.root/'.colvia-link.json').is_file())
        authority=self.manager.authority(self.preview['plan']['project']);store=authority.store()
        try:self.assertIsNone(store.head(PENDING));self.assertIsNotNone(store.head(PROJECT_KEY))
        finally:store.close()
        self.assertEqual('connected',self.setup.resume('connect')['state'])
    def test_existing_project_rules_preserved_and_not_committed(self):
        (self.root/'AGENTS.md').write_bytes(b'User rules without newline');(self.root/'report.md').write_bytes(b'Existing report')
        self.begin();self.finish()
        self.assertEqual(b'User rules without newline\n'+BLOCK,(self.root/'AGENTS.md').read_bytes())
        self.assertEqual(b'Existing report',(self.root/'report.md').read_bytes())
        self.assertFalse((self.root/'.git').exists())
    def test_changed_preview_refuses_before_authority_creation(self):
        p=self.setup.preview(self.root);(self.root/'AGENTS.md').write_bytes(b'New rule')
        with self.assertRaisesRegex(RecordError,'review-changed'):
            self.setup.start(operation='connect',plan=p['plan'],receipt=p['receipt'],statement='적용')
        self.assertEqual((),self.manager.projects());self.assertFalse((self.manager.root/'operations/connect').exists())
    def test_interrupted_first_effect_can_be_observed_and_finished(self):
        self.begin()
        def interrupt(phase):
            if phase=='after-install':raise RuntimeError('synthetic interruption')
        # The port exposes effect callback names; stop after the service observes
        # an applied step to exercise commit-before-record recovery precisely.
        def after(phase):
            if phase=='applied':raise RuntimeError('synthetic interruption')
        with self.assertRaises(RuntimeError):self.setup.resume('connect',event=after)
        self.finish()
    def test_later_user_edit_stops_without_clobbering(self):
        self.begin();self.setup.resume('connect');(self.root/'CLAUDE.md').write_bytes(b'New private rules')
        with self.assertRaisesRegex(RecordError,'effect-path-unknown|files-changed'):self.setup.resume('connect')
        self.assertEqual(b'New private rules',(self.root/'CLAUDE.md').read_bytes());self.assertFalse((self.root/'.colvia-link.json').exists())
    def test_detach_reads_owned_configuration_preserves_rules_and_history(self):
        (self.root/'AGENTS.md').write_bytes(b'User rules\n');self.begin();self.finish()
        project=self.preview['plan']['project'];(self.root/'AGENTS.md').write_bytes((self.root/'AGENTS.md').read_bytes()+b'Later user rule\n')
        authority,store,service,changes=self.setup.detach_context(project,self.root)
        try:
            old=store.root().ref;integration=store.head('project:integration');self.assertIsNotNone(integration)
            preview=service.preview(changes);service.begin(operation='detach',changes=changes,receipt=preview['receipt'],statement='연결 해제')
            for _ in changes:result=service.advance('detach')
            self.assertEqual('detached',result['state']);self.assertIsNone(store.head(PROJECT_KEY));self.assertIsNotNone(store.load(old))
            self.assertIsNotNone(store.load(integration));self.assertFalse((self.root/'colvia').exists())
            self.assertEqual(b'User rules\nLater user rule\n',(self.root/'AGENTS.md').read_bytes())
            self.assertFalse((self.root/'CLAUDE.md').exists());self.assertFalse((self.root/'.colvia-link.json').exists())
        finally:store.close()
        with self.assertRaisesRegex(RecordError,'reconnect-or-move-review-required'):self.setup.preview(self.root)

    def test_existing_launcher_or_binding_requires_explicit_repair(self):
        (self.root/'colvia').write_bytes(b'Existing launcher')
        with self.assertRaisesRegex(RecordError,'launcher-already-present'):self.setup.preview(self.root)
        self.assertEqual(b'Existing launcher',(self.root/'colvia').read_bytes())

    def connect(self, root, operation):
        p = self.setup.preview(root)
        self.setup.start(operation=operation, plan=p['plan'], receipt=p['receipt'], statement='Synthetic connection')
        for _ in p['plan']['changes']:
            result = self.setup.resume(operation)
        self.assertEqual('connected', result['state'])
        return p['plan']['project']

    def test_overlap_in_either_order_including_stale_apply(self):
        for index, first_parent in enumerate((True, False)):
            with self.subTest(first_parent=first_parent):
                parent = self.base / f'parent-{index}'
                child = parent / 'child'
                child.mkdir(parents=True)
                first, second = (parent, child) if first_parent else (child, parent)
                sentinel = second / 'report.md'
                sentinel.write_bytes(b'User report\n')
                stale = self.setup.preview(second)
                project = self.connect(first, f'first-{index}')
                projects = self.manager.projects()
                locator = first / '.colvia-link.json'
                initial = locator.read_bytes()
                with closing(self.manager.authority(project).store(readonly=True)) as store:
                    before = store.root().ref
                with self.assertRaisesRegex(RecordError, 'connect-project-overlap') as error:
                    self.setup.preview(second)
                self.assertEqual(str(first), error.exception.directory)
                with self.assertRaisesRegex(RecordError, 'connect-project-overlap'):
                    self.setup.start(operation='refused', plan=stale['plan'], receipt=stale['receipt'], statement='Synthetic connection')
                with closing(self.manager.authority(project).store(readonly=True)) as store:
                    self.assertEqual(before, store.root().ref)
                self.assertEqual(projects, self.manager.projects())
                self.assertFalse((self.manager.root / 'operations/refused').exists())
                self.assertEqual(initial, locator.read_bytes())
                self.assertEqual(b'User report\n', sentinel.read_bytes())

    def test_same_root_blocks_but_siblings_with_same_prefix_connect(self):
        self.connect(self.root, 'original')
        stale_root = self.base / 'project-sibling'
        stale_root.mkdir()
        with self.assertRaisesRegex(RecordError, 'connect-project-overlap'):
            self.setup.preview(self.root)
        self.connect(stale_root, 'sibling')
        self.assertEqual(2, len(self.manager.projects()))

    def test_binding_without_integration_or_locator_occupies_plain_root(self):
        child = self.root / 'child'
        child.mkdir()
        from colvia.project_setup import record
        def interrupted(kind, *args):
            if kind == 'project.integration':
                raise RuntimeError('after binding')
            return record(kind, *args)
        with patch('colvia.project_setup.record', side_effect=interrupted):
            with self.assertRaisesRegex(RuntimeError, 'after binding'):
                self.begin()
        self.assertFalse((self.root / '.colvia-link.json').exists())
        with self.assertRaisesRegex(RecordError, 'connect-project-overlap'):
            self.setup.preview(child)
        sibling = self.base / 'sibling'
        sibling.mkdir()
        self.connect(sibling, 'sibling')

    def test_pending_resume_preserves_conflict_until_other_connection_detaches(self):
        self.begin()
        child = self.root / 'child'
        child.mkdir()
        # Emulate a conflicting connection made by an earlier product build.
        with patch('colvia.project_setup.check_connection_boundary'):
            other = self.connect(child, 'older-child')
        authority = self.manager.authority(self.preview['plan']['project'])
        with closing(authority.store(readonly=True)) as store:
            before = store.root().ref
        child_locator = (child / '.colvia-link.json').read_bytes()
        with self.assertRaisesRegex(RecordError, 'connect-resume-project-overlap'):
            self.setup.resume('connect')
        with closing(authority.store(readonly=True)) as store:
            self.assertEqual(before, store.root().ref)
        self.assertFalse((self.root / 'AGENTS.md').exists())
        self.assertEqual(child_locator, (child / '.colvia-link.json').read_bytes())
        # Readback of the already completed child operation has no file effects.
        self.assertEqual('connected', self.setup.resume('older-child')['state'])
        _, store, detach, changes = self.setup.detach_context(other, child)
        try:
            p = detach.preview(changes)
        finally:
            store.close()
        self.setup.detach_begin(operation='detach-child', project=other, root=child,
                                receipt=p['receipt'], statement='Synthetic detach')
        for _ in changes:
            result = self.setup.detach_resume('detach-child')
        self.assertEqual('detached', result['state'])
        self.finish()

    def test_detached_descendant_does_not_occupy_parent(self):
        child = self.root / 'child'
        child.mkdir()
        project = self.connect(child, 'connect-child')
        _, store, detach, changes = self.setup.detach_context(project, child)
        try:
            p = detach.preview(changes)
        finally:
            store.close()
        self.setup.detach_begin(operation='detach-child', project=project, root=child,
                                receipt=p['receipt'], statement='Synthetic detach')
        for _ in changes:
            self.setup.detach_resume('detach-child')
        with self.assertRaisesRegex(RecordError, 'project-reconnect-or-move-review-required'):
            self.setup.preview(child)
        self.connect(self.root, 'connect-parent')

    def test_known_ancestor_marker_and_unverifiable_live_root_refuse(self):
        child = self.root / 'child'
        child.mkdir()
        marker = self.root / '.colvia-link.json'
        marker.write_bytes(b'unknown connection\n')
        with self.assertRaisesRegex(RecordError, 'connect-ancestor-marker') as error:
            self.setup.preview(child)
        self.assertEqual(str(self.root), error.exception.directory)
        self.assertEqual(b'unknown connection\n', marker.read_bytes())
        marker.unlink()
        self.connect(self.root, 'original')
        self.root.rename(self.base / 'moved')
        self.root.mkdir()
        (self.root / 'child').mkdir()
        with self.assertRaisesRegex(RecordError, 'connect-boundary-unavailable'):
            self.setup.preview(child)

    def test_native_identity_catches_different_unicode_spelling(self):
        root = self.base / 'caf\u00e9'
        root.mkdir()
        alternate = self.base / 'cafe\u0301'
        if not alternate.is_dir() or not root.samefile(alternate):
            self.skipTest('filesystem distinguishes Unicode spellings')
        (root / 'child').mkdir()
        self.connect(root, 'composed')
        with self.assertRaisesRegex(RecordError, 'connect-project-overlap'):
            self.setup.preview(alternate / 'child')


class GitSetupTests(SetupFixture,GitFixture,unittest.TestCase):
    def setUp(self):
        GitFixture.setUp(self);self.manager_fixture(self.home,self.git)
    def test_git_connection_only_at_root_and_no_git_commit(self):
        old=self.command('rev-parse','HEAD');(self.root/'sub').mkdir()
        with self.assertRaisesRegex(RecordError,'root-required'):self.setup.preview(self.root/'sub')
        self.begin();self.finish();self.assertEqual(old,self.command('rev-parse','HEAD'))
        self.assertTrue((self.root/'.git/colvia/connection.json').is_file());self.assertFalse((self.root/'.colvia-link.json').exists())
    def test_second_worktree_cannot_create_second_authority(self):
        self.begin();self.finish();sibling=self.home/'sibling';self.command('worktree','add','-q','-b','sibling',str(sibling))
        with self.assertRaisesRegex(RecordError,'connect-project-overlap'):self.setup.preview(sibling)
        self.assertEqual(1,len(self.manager.projects()))

    def test_unregistered_linked_workspace_cannot_share_pending_git_locator(self):
        sibling = self.home / 'linked'
        self.command('worktree', 'add', '-q', '-b', 'linked', str(sibling))
        stale = self.setup.preview(sibling)
        self.begin()
        self.assertFalse((self.root / '.git/colvia/connection.json').exists())
        with self.assertRaisesRegex(RecordError, 'connect-project-overlap'):
            self.setup.preview(sibling)
        with self.assertRaisesRegex(RecordError, 'connect-project-overlap'):
            self.setup.start(operation='refused', plan=stale['plan'], receipt=stale['receipt'],
                             statement='Synthetic connection')
        self.assertEqual(1, len(self.manager.projects()))
        self.assertFalse((self.manager.root / 'operations/refused').exists())
        self.finish()

    def test_unavailable_git_registration_reports_the_affected_root(self):
        self.begin()
        self.finish()
        self.root.rename(self.home / 'moved')
        sibling = self.home / 'unrelated'
        sibling.mkdir()
        with self.assertRaisesRegex(RecordError, 'connect-boundary-unavailable') as error:
            self.setup.preview(sibling)
        self.assertEqual(str(self.root), error.exception.directory)

    def test_registered_linked_workspace_is_an_occupied_root(self):
        from colvia.adapters.git import discover
        from colvia.binding import WorkspaceRegistration
        from colvia.connection import Connections
        import uuid

        self.begin()
        self.finish()
        container = self.home / 'container'
        container.mkdir()
        linked = container / 'linked'
        self.command('worktree', 'add', '-q', '-b', 'linked', str(linked))
        topology = discover(linked, self.git)
        authority = self.manager.authority(self.preview['plan']['project'])
        with closing(authority.store()) as store:
            connections = Connections(store)
            _, binding = connections.binding()
            connections.register(operation='linked-registration', locator=binding.locator, observed=topology,
                                 workspace=WorkspaceRegistration(str(uuid.uuid4()), topology.root, topology.gitdir),
                                 registrations=connections.registrations(topology),
                                 verify_topology=lambda: discover(linked, self.git))
        with self.assertRaisesRegex(RecordError, 'connect-project-overlap') as error:
            self.setup.preview(container)
        self.assertEqual(str(linked), error.exception.directory)

    def test_published_git_binding_before_integration_is_visible(self):
        from colvia.project_setup import record
        def interrupted(kind, *args):
            if kind == 'project.integration':
                raise RuntimeError('after binding')
            return record(kind, *args)
        with patch('colvia.project_setup.record', side_effect=interrupted):
            with self.assertRaisesRegex(RuntimeError, 'after binding'):
                self.begin()
        self.assertFalse((self.root / '.git/colvia/connection.json').exists())
        with self.assertRaisesRegex(RecordError, 'connect-project-overlap') as error:
            self.setup.preview(self.home)
        self.assertEqual(str(self.root), error.exception.directory)


if __name__=='__main__':unittest.main()
