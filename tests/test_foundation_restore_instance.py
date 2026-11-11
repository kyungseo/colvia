"""Restore older history as a new instance, never erase the later decisions."""
import io,tempfile,unittest,uuid
from pathlib import Path
from colvia.backup import ImportedSnapshot,ExportBudget,supported_requirements
from colvia.backup_service import export_backup
from colvia.binding import Locator,ProjectBinding,Topology,WorkspaceRegistration
from colvia.codec import RecordError,encode_envelope
from colvia.connection import Connections,PROJECT_KEY
from colvia.graph import AuditBudget
from colvia.platforms.posix import location
from colvia.records import application_registry
from colvia.storage.authority import Authority
from colvia.work import WorkService
from colvia.workspace import LocalWorkspace
from test_foundation_binding import P,I,W

class RestoreInstanceTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='restore-instance-');self.base=Path(self.tmp.name)
        self.project=self.base/'project';self.project.mkdir()
        self.authority=Authority.create(self.base/'authority',project=P,instance=I,generation='initial')
        self.store=self.authority.store();self.locator=Locator(P,I,1,'a'*64,W)
        self.topology=Topology('plain',location(self.project))
        Connections(self.store).connect(operation='connect',binding=ProjectBinding(self.locator,'plain',self.topology.root),
            observed=self.topology,workspace=WorkspaceRegistration(W,self.topology.root,None),verify_topology=lambda:self.topology)
        self.old_binding=self.store.head(PROJECT_KEY)
        self.snapshot=None;self.new_instance=str(uuid.uuid4())
    def tearDown(self):
        self.store.close()
        if self.snapshot:self.snapshot.close()
        self.tmp.cleanup()
    def save(self):
        scratch=self.base/'scratch';scratch.mkdir();out=self.base/'saved.backup';reg=application_registry()
        export_backup(self.authority,destination=out,scratch=scratch,operation='save',graph_budget=AuditBudget(10000,20000,32*1024**2),registry=reg)
        caps=supported_requirements(reg)
        self.snapshot=ImportedSnapshot(self.base/'import.sqlite3',io.BytesIO(out.read_bytes()),budget=ExportBudget(10000,32*1024**2),
            graph_budget=AuditBudget(10000,20000,32*1024**2),registry=reg,capabilities=caps,writable_capabilities=caps)
        self.saved=self.store.root().ref
        self.authority.import_candidate('restored',self.snapshot,operation='import',instance=self.new_instance)
    def switch(self,checkpoint=lambda _:None):
        return self.authority.activate_restore('restore',target_generation='restored',instance=self.new_instance,
            expected_root=self.store.root().ref,target_root=self.saved,validate_effects=lambda _:None,validate_target=lambda _:None,checkpoint=checkpoint)
    def test_old_snapshot_is_new_instance_and_later_history_remains_readable(self):
        self.save()
        from colvia.configuration import Configuration
        config=Configuration(self.store);p=config.preview(['official-execution'])
        config.apply(operation='later',features=['official-execution'],receipt=p['receipt'],statement='Enable')
        later=self.store.root().ref;self.switch()
        active=self.authority.store()
        try:
            self.assertEqual(self.saved,active.root().ref);self.assertTrue(active.needs_rebind())
            with self.assertRaisesRegex(RecordError,'instance-rebind-required'):active.begin_import('blocked','test')
            historical=self.authority.historical_store('restore')
            try:
                self.assertEqual(later,historical.root().ref);self.assertIsNotNone(historical.operation_result('later'))
                with self.assertRaisesRegex(RecordError,'store-readonly'):historical.begin_import('not-live','test')
            finally:historical.close()
        finally:active.close()
    def test_explicit_rebind_records_fresh_identity_and_permits_new_work(self):
        self.save();self.switch();active=self.authority.store()
        try:
            work_id=str(uuid.uuid4());locator=Locator(P,self.new_instance,2,'b'*64,work_id)
            connection=Connections(active)
            connection.rebind_restored(operation='rebind',binding=ProjectBinding(locator,'plain',self.topology.root),
                observed=self.topology,workspace=WorkspaceRegistration(work_id,self.topology.root,None),statement='Reconnect this restored project',
                expected_binding=self.old_binding,verify_topology=lambda:self.topology)
            self.assertFalse(active.needs_rebind());self.assertEqual(self.new_instance,connection.binding()[1].locator.instance)
            self.assertIsNotNone(active.head('restore:rebind'))
            workspace=LocalWorkspace(active,self.project,work_id,locator_reader=lambda:locator)
            result=WorkService(active,workspace).plan(operation='new-plan',work='new',title='New work',goal='Continue with restored history',
                scope=['report.md'],checks=['check output'],excludes=[])
            self.assertEqual('planned',result['state'])
        finally:active.close()
    def test_stale_epoch_or_old_nonce_cannot_rebind(self):
        self.save();self.switch();active=self.authority.store()
        try:
            for epoch,nonce in ((1,'b'*64),(2,'a'*64)):
                wid=str(uuid.uuid4());locator=Locator(P,self.new_instance,epoch,nonce,wid)
                with self.assertRaisesRegex(RecordError,'invalid-restore-rebind'):
                    Connections(active).rebind_restored(operation='bad',binding=ProjectBinding(locator,'plain',self.topology.root),
                        observed=self.topology,workspace=WorkspaceRegistration(wid,self.topology.root,None),statement='Reconnect',
                        expected_binding=self.old_binding,verify_topology=lambda:self.topology)
            self.assertTrue(active.needs_rebind());self.assertEqual(self.saved,active.root().ref)
        finally:active.close()
    def test_interruption_after_fence_recovers_new_instance_still_read_only(self):
        self.save()
        def checkpoint(phase):
            if phase=='fenced':raise RuntimeError('synthetic crash')
        with self.assertRaises(RuntimeError):self.switch(checkpoint)
        self.authority.recover('restore',complete=True,validate_effects=lambda _:None,validate_target=lambda _:None)
        active=self.authority.store()
        try:self.assertTrue(active.needs_rebind());self.assertEqual(self.saved,active.root().ref)
        finally:active.close()

    def test_accepted_body_is_readable_after_restore_and_rebind(self):
        service=WorkService(self.store,LocalWorkspace(self.store,self.project,W,locator_reader=lambda:self.locator))
        p=service.plan(operation='plan',work='report',title='Report',goal='Retain exact reviewed content',scope=['report.md'],checks=['body'],excludes=[])
        service.approve(operation='approve',work='report',receipt=p['receipt'],statement='Proceed');service.start(operation='start',work='report')
        (self.project/'report.md').write_bytes(b'Accepted report\n')
        r=service.submit(operation='submit',work='report',summary='Report ready',checks=[dict(name='body',status='passed',detail='Exact content')])
        service.accept(operation='accept',work='report',receipt=r['receipt'],statement='Accept this report')
        self.save();self.switch();active=self.authority.store()
        try:
            wid=str(uuid.uuid4());locator=Locator(P,self.new_instance,2,'b'*64,wid)
            Connections(active).rebind_restored(operation='rebind',binding=ProjectBinding(locator,'plain',self.topology.root),
                observed=self.topology,workspace=WorkspaceRegistration(wid,self.topology.root,None),statement='Reconnect',
                expected_binding=self.old_binding,verify_topology=lambda:self.topology)
            current=WorkService(active,LocalWorkspace(active,self.project,wid,locator_reader=lambda:locator))
            self.assertEqual('completed',current.view('report')['state'])
            self.assertEqual('Accepted report\n',current.result_content('report','report.md')['after']['text'])
            self.assertIsNone(current.view('report')['current_matches'])
        finally:active.close()
    def test_imported_pending_effect_is_inspection_only_and_never_replayed(self):
        self.store.commit_heads(operation='fixture-pending',expected={'effect:pending':None},changes={'effect:pending':self.old_binding},objects=[],validate=lambda _:None)
        self.save()
        self.store.commit_heads(operation='fixture-clear-live',expected={'effect:pending':self.old_binding},changes={'effect:pending':None},objects=[],validate=lambda _:None)
        before=self.authority.pointer_value()
        with self.assertRaisesRegex(RecordError,'imported-effect-inspection-only'):self.switch()
        self.assertEqual(before,self.authority.pointer_value());self.assertFalse((self.authority.root/'pending.json').exists())

    def test_same_state_update_cannot_clear_pending_rebind(self):
        self.save();self.switch()
        self.authority.import_candidate('updated',self.snapshot,operation='update-copy')
        active=self.authority.store(readonly=True)
        try:root=active.root().ref
        finally:active.close()
        self.authority.activate('update',target_generation='updated',expected_root=root,
            validate_effects=lambda _:None,validate_target=lambda _:None)
        active=self.authority.store()
        try:
            self.assertTrue(active.needs_rebind())
            with self.assertRaisesRegex(RecordError,'instance-rebind-required'):active.begin_import('still-blocked','test')
            historical=self.authority.historical_store('restore')
            try:self.assertEqual(self.saved,historical.root().ref)
            finally:historical.close()
        finally:active.close()
