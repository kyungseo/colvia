from contextlib import closing
import tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from colvia.codec import RecordError
from colvia.project_setup import ProjectSetup,BLOCK
from colvia.restored_setup import RestoredSetup
from colvia.restore_manager import RestoreManager
from colvia.storage.sqlite import runtime_capabilities
from colvia.backup_service import export_backup
from colvia.graph import AuditBudget
from colvia.records import application_registry
from colvia.cli import read_locator
from colvia.connection import Connections
from colvia.workspace import LocalWorkspace
from colvia.work import WorkService
import test_foundation_project_setup as setup_fixture
import test_foundation_slots as slot_fixture

class RestoredSetupTests(unittest.TestCase):
    slot=slot_fixture.SlotTests.slot
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='restored-setup-');self.base=Path(self.tmp.name);self.root=self.base/'project';self.root.mkdir()
        (self.root/'AGENTS.md').write_bytes(b'User rules\n')
        setup_fixture.SetupFixture.manager_fixture(self,self.base)
        self.home=self.manager;self.manager=self.home.slots
        caps=tuple(c for c in runtime_capabilities() if c!='foundation-v1');self.one=self.slot('one',1,extra=caps);self.manager.initialize(self.one)
        p=self.setup.preview(self.root);self.project=p['plan']['project'];self.setup.start(operation='connect',plan=p['plan'],receipt=p['receipt'],statement='적용')
        for _ in range(4):self.setup.resume('connect')
        self.authority=self.home.authority(self.project);store=self.authority.store()
        try:
            locator=read_locator(self.root,None);workspace=LocalWorkspace(store,self.root,locator.workspace,locator_reader=lambda:read_locator(self.root,None))
            service=WorkService(store,workspace);p=service.plan(operation='plan',work='report',title='보고서',goal='본문 보존',scope=['report.md'],checks=['확인'])
            service.approve(operation='approve',work='report',receipt=p['receipt'],statement='진행');service.start(operation='start',work='report')
            (self.root/'report.md').write_bytes(b'Accepted report\n');r=service.submit(operation='submit',work='report',summary='완료',checks=[dict(name='확인',status='passed',detail='본문')])
            service.accept(operation='accept',work='report',receipt=r['receipt'],statement='수락')
            self.old_root=store.root().ref
        finally:store.close()
        scratch=self.base/'scratch';scratch.mkdir();backup=self.base/'saved.export'
        export_backup(self.authority,destination=backup,scratch=scratch,operation='save',graph_budget=AuditBudget(10000,20000,32*1024**2),registry=application_registry())
        restore=RestoreManager(self.home);p=restore.prepare(operation='restore',archive=backup);restore.apply(operation='restore',receipt=p['receipt'])
        self.rebind=RestoredSetup(self.home)
    def tearDown(self):self.tmp.cleanup()
    def finish(self,p,root):
        self.rebind.start(operation='rebind',plan=p['plan'],receipt=p['receipt'],statement='복원 연결')
        for _ in p['plan']['changes']:result=self.rebind.resume('rebind')
        self.assertEqual('connected',result['state']);locator=read_locator(root,None);store=self.authority.store()
        try:
            self.assertFalse(store.needs_rebind());self.assertEqual(locator,Connections(store).binding()[1].locator)
            service=WorkService(store,LocalWorkspace(store,root,locator.workspace,locator_reader=lambda:read_locator(root,None)))
            self.assertEqual('completed',service.view('report')['state'])
            self.assertEqual('Accepted report\n',service.result_content('report','report.md')['after']['text'])
            self.assertIsNone(service.view('report')['current_matches'])
            result=service.plan(operation='next-plan',work='next',title='다음',goal='복원 뒤 새 작업',scope=['next.md'],checks=['확인'])
            self.assertEqual('planned',result['state'])
        finally:store.close()
    def test_existing_folder_replaces_only_locator_not_report_or_user_rules(self):
        before=(self.root/'AGENTS.md').read_bytes();p=self.rebind.preview(self.project,self.root)
        self.assertEqual(['.colvia-link.json'],p['files']);self.finish(p,self.root)
        self.assertEqual(before,(self.root/'AGENTS.md').read_bytes());self.assertEqual(b'Accepted report\n',(self.root/'report.md').read_bytes())
        authority,store,service,changes=ProjectSetup(self.home).detach_context(self.project,self.root)
        try:self.assertEqual(4,len(changes))
        finally:store.close()
    def test_new_folder_gains_owned_integration_but_not_restored_report_bytes(self):
        root=self.base/'new';root.mkdir();p=self.rebind.preview(self.project,root);self.finish(p,root)
        self.assertFalse((root/'report.md').exists());self.assertEqual(BLOCK,(root/'AGENTS.md').read_bytes())
        self.assertTrue((self.root/'report.md').exists())
    def test_rule_change_invalidates_preview_before_binding_decision(self):
        p=self.rebind.preview(self.project,self.root);(self.root/'AGENTS.md').write_bytes((self.root/'AGENTS.md').read_bytes()+b'New rule\n')
        with self.assertRaisesRegex(RecordError,'review-changed'):
            self.rebind.start(operation='rebind',plan=p['plan'],receipt=p['receipt'],statement='복원 연결')
        store=self.authority.store()
        try:self.assertTrue(store.needs_rebind());self.assertEqual(self.old_root,store.root().ref)
        finally:store.close()

    def connect_independent(self, target):
        p = self.setup.preview(target)
        self.setup.start(operation='independent', plan=p['plan'], receipt=p['receipt'], statement='Synthetic connection')
        for _ in p['plan']['changes']:
            state = self.setup.resume('independent')
        self.assertEqual('connected', state['state'])

    def test_rebind_checks_stale_preview_and_same_root(self):
        parent = self.base / 'target'
        child = parent / 'child'
        child.mkdir(parents=True)
        p = self.rebind.preview(self.project, parent)
        self.connect_independent(child)
        for target in (child, parent):
            with self.assertRaisesRegex(RecordError, 'rebind-project-overlap'):
                self.rebind.preview(self.project, target)
        with self.assertRaisesRegex(RecordError, 'rebind-project-overlap'):
            self.rebind.start(operation='refused', plan=p['plan'], receipt=p['receipt'], statement='Synthetic rebind')
        self.assertFalse((self.home.root / 'operations/refused').exists())
        with closing(self.authority.store(readonly=True)) as store:
            self.assertTrue(store.needs_rebind())
            self.assertEqual(self.old_root, store.root().ref)

    def test_interrupted_rebind_before_binding_rechecks_and_allows_another_target(self):
        parent = self.base / 'target'
        child = parent / 'child'
        child.mkdir(parents=True)
        p = self.rebind.preview(self.project, parent)
        with patch.object(self.rebind, '_prepare', side_effect=RuntimeError('after journal')):
            with self.assertRaisesRegex(RuntimeError, 'after journal'):
                self.rebind.start(operation='interrupted', plan=p['plan'], receipt=p['receipt'], statement='Synthetic rebind')
        journal = self.home.root / 'operations/interrupted/rebind.json'
        original = journal.read_bytes()
        self.connect_independent(child)
        child_locator = (child / '.colvia-link.json').read_bytes()
        with self.assertRaisesRegex(RecordError, 'rebind-project-overlap'):
            self.rebind.resume('interrupted')
        with closing(self.authority.store(readonly=True)) as store:
            self.assertTrue(store.needs_rebind())
            self.assertEqual(self.old_root, store.root().ref)
        self.assertEqual(original, journal.read_bytes())
        self.assertEqual(child_locator, (child / '.colvia-link.json').read_bytes())
        self.assertFalse((parent / 'AGENTS.md').exists())
        alternative = self.base / 'alternative'
        alternative.mkdir()
        self.finish(self.rebind.preview(self.project, alternative), alternative)
        with self.assertRaisesRegex(RecordError, 'restore-rebind-review-changed'):
            self.rebind.resume('interrupted')
        self.assertEqual(original, journal.read_bytes())

    def test_published_rebind_without_integration_reserves_new_workspace(self):
        parent = self.base / 'target'
        child = parent / 'child'
        child.mkdir(parents=True)
        p = self.rebind.preview(self.project, parent)
        stale = self.setup.preview(child)
        from colvia.restored_setup import record
        def interrupted(kind, *args):
            if kind == 'project.integration':
                raise RuntimeError('after binding')
            return record(kind, *args)
        with patch('colvia.restored_setup.record', side_effect=interrupted):
            with self.assertRaisesRegex(RuntimeError, 'after binding'):
                self.rebind.start(operation='interrupted', plan=p['plan'], receipt=p['receipt'], statement='Synthetic rebind')
        self.assertFalse((parent / '.colvia-link.json').exists())
        with closing(self.authority.store(readonly=True)) as store:
            self.assertFalse(store.needs_rebind())
        with self.assertRaisesRegex(RecordError, 'connect-project-overlap'):
            self.setup.preview(child)
        with self.assertRaisesRegex(RecordError, 'connect-project-overlap'):
            self.setup.start(operation='refused', plan=stale['plan'], receipt=stale['receipt'],
                             statement='Synthetic connection')
        self.assertFalse((self.home.root / 'operations/refused').exists())
        for _ in p['plan']['changes']:
            result = self.rebind.resume('interrupted')
        self.assertEqual('connected', result['state'])


if __name__=='__main__':unittest.main()
