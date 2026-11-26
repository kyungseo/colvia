"""Grouped decisions on synthetic local Git worktrees and private authorities."""
import sys, unittest, uuid
from pathlib import Path
from colvia.binding import Locator, ProjectBinding, WorkspaceRegistration
from colvia.codec import RecordError, canonical_bytes
from colvia.connection import Connections
from colvia.workspace import LocalWorkspace
from colvia.work import WorkService, work_key
from colvia.storage.authority import Authority
from colvia.group import GroupService
from colvia.records import link, application_registry, head_summary
from colvia.backup_service import export_backup
from colvia.graph import AuditBudget
from colvia.effects import PENDING
from colvia.maps import map_get
from colvia.platforms.exclusive import available
from test_foundation_git import GitFixture
from test_foundation_binding import P,I,W


class GroupCandidateReuseTests(unittest.TestCase):
    def test_candidate_reuse_is_exact_success_only_and_local_to_one_view(self):
        from unittest.mock import patch
        from colvia import group_records as gr
        from colvia.codec import ObjectRef

        first = ObjectRef('group.candidate',2,1,'a'*64)
        second = ObjectRef('group.candidate',3,1,'a'*64)
        view, other = object(), object()
        parts = ('candidate','approval','plan','baseline',['before'],['after'],(),{'file':'body'},['member'])
        with patch.object(gr,'_candidate_parts',side_effect=[parts,RecordError('missing'),parts,parts,parts]) as derive:
            with gr.reuse_candidate_parts(view):
                received = gr.candidate_parts(first,view)
                received[4].clear()
                received[5].clear()
                received[7].clear()
                received[8].clear()
                self.assertEqual(parts,gr.candidate_parts(first,view))
                with self.assertRaisesRegex(RecordError,'missing'):
                    gr.candidate_parts(second,view)
                self.assertEqual(parts,gr.candidate_parts(second,view))
                self.assertEqual(parts,gr.candidate_parts(second,other))
                self.assertEqual(parts,gr.candidate_parts(second,view))
            self.assertEqual(parts,gr.candidate_parts(second,view))
            self.assertEqual([(first,view),(second,view),(second,view),(second,other),(second,view)],
                             [call.args for call in derive.call_args_list])


class WindowsGroupRecordTests(unittest.TestCase):
    def test_native_x64_group_uses_the_grouped_windows_effect_port(self):
        from types import SimpleNamespace
        from unittest.mock import patch
        from colvia.group_records import WINDOWS_GROUP_VERSION

        store=SimpleNamespace(project=P, instance=I, generation='test')
        destination=SimpleNamespace(store=store, root=Path('destination'))
        group=GroupService(store,destination,authority=Path('authority'))
        with patch('colvia.platforms.windows_architecture.native_x64', return_value=True), \
             patch('colvia.platforms.effects_port.sys', SimpleNamespace(platform='win32')), \
             patch('colvia.platforms.windows_effects.WindowsEffects') as port:
            self.assertIs(group._port(version=WINDOWS_GROUP_VERSION),port.return_value)
        port.assert_called_once_with(destination.root,group.authority,native_entries=False,grouped=True)

    def test_native_paths_refuse_escape_and_windows_aliases(self):
        from colvia.group_records import windows_path
        samples=(r'a\..\b','control'+chr(1),'C:drive','/absolute','x/../y','x/a:stream',
                 'x/trailing.','x/trailing ','NUL.txt','COM¹.txt','x/FILE~1.txt')
        for path in samples:
            with self.subTest(path=path), self.assertRaises(RecordError):
                windows_path(path)
        self.assertEqual('tables/견적.csv',windows_path('tables/견적.csv'))

    def test_only_matching_decision_families_and_runtime_bound_evidence(self):
        from colvia.codec import ObjectRef
        from colvia.records import record
        registry=application_registry()
        def ref(kind, version): return ObjectRef(kind,version,0,'a'*64)
        for decision,authorization,allowed in ((2,1,True),(3,2,True),(4,3,True),(4,2,False),(3,3,False)):
            with self.subTest(decision=decision,authorization=authorization):
                pair=record('work.decision',dict(work='member',workspace=W,action='accept',statement='Accept'),
                    dict(result=('decision',ref('work.submission',1)),
                         authorization=('decision',ref('group.authorization',authorization))),version=decision)
                if allowed:
                    registry.inspect(*pair,required=True)
                else:
                    with self.assertRaisesRegex(RecordError,'group-decision-version-required'):
                        registry.inspect(*pair,required=True)
        links=dict(candidate=('decision',ref('group.candidate',3)),
                   stdout=('integrity',ref('body.complete',1)),stderr=('integrity',ref('body.complete',1)))
        evidence=dict(name='file check',definition='f'*64,outcome='exited',exit_code=0,elapsed_ns=1,
                      tree_unchanged=True,environment_inputs='system runtime and approved environment; ignored and opaque files excluded')
        pair=record('group.evidence',evidence,links,version=2)
        with self.assertRaisesRegex(RecordError,'group-record-version-mismatch'):
            registry.inspect(*pair,required=True)
        pair=record('group.evidence',dict(evidence,runtime=None),links,version=3)
        with self.assertRaisesRegex(RecordError,'group-check-runtime-evidence-required'):
            registry.inspect(*pair,required=True)


class GroupFixture(GitFixture):
    def setUp(self):
        super().setUp()
        self.authority=Authority.create(self.home/'authority',project=P,instance=I,generation='g')
        self.store=self.authority.store(); top=self.git.topology(self.root); self.locator=Locator(P,I,1,'a'*64)
        connections=Connections(self.store)
        connections.connect(operation='connect',binding=ProjectBinding(self.locator,'git',top.common),observed=top,
            workspace=WorkspaceRegistration(W,top.root,top.gitdir),verify_topology=lambda:self.git.topology(self.root))
        marker=self.root/'.git/colvia/connection.json'; marker.parent.mkdir(); marker.write_bytes(canonical_bytes(self.locator.payload()))
        self.destination=LocalWorkspace(self.store,self.root,W,git=self.git,locator_reader=lambda:self.locator)
        self.sources=[]; self.paths=[]
        for i in range(getattr(self,'member_count',2)):
            path=self.home/('source-'+str(i)); self.command('worktree','add','-q','-b','source-'+str(i),str(path))
            top=self.git.topology(path); wid=str(uuid.uuid4())
            connections.register(operation='register-'+str(i),locator=self.locator,observed=top,
                workspace=WorkspaceRegistration(wid,top.root,top.gitdir),registrations=connections.registrations(top),verify_topology=lambda path=path:self.git.topology(path))
            self.sources.append(WorkService(self.store,LocalWorkspace(self.store,path,wid,git=self.git,locator_reader=lambda:self.locator)))
            self.paths.append(path)
        self.group=GroupService(self.store,self.destination,authority=self.authority.root,lifecycle_authority=self.authority)
        self.scratch=self.home/'backup-scratch'; self.scratch.mkdir()
        self.checks=[dict(name='union check',argv=[sys.executable,'-B','-c',"from pathlib import Path; assert Path('report.md').read_bytes()==b'backend\\n'; assert Path('web/index.html').read_bytes()==b'button\\n'"],cwd='.',env={'PYTHONDONTWRITEBYTECODE':'1'},timeout_seconds=10,output_bytes=4096)]
        self.serial=0

    def tearDown(self):
        self.store.close(); super().tearDown()

    def op(self): self.serial+=1; return 'op-'+str(self.serial)

    def plans(self):
        for i,scope in enumerate((['report.md'],['web/index.html'])):
            self.sources[i].plan(operation=self.op(),work='member'+str(i),title='Member '+str(i),goal='Change own file',scope=scope,checks=['local check'])

    def backup(self):
        return export_backup(self.authority,destination=self.home/(self.op()+'.backup'),scratch=self.scratch,operation=self.op(),
                             graph_budget=AuditBudget(10000,10000,32*1024*1024),registry=application_registry())

    def create(self,backup=True):
        if backup:self.backup()
        return self.group.create(operation=self.op(),group='pair',works=['member0','member1'],checks=self.checks,acknowledgement='I preserved working files separately; older runtimes cannot open the upgraded records.')

    def results(self):
        self.plans(); shown=self.create(); self.group.approve(operation=self.op(),group='pair',receipt=shown['receipt'],statement='Approve both exact plans')
        for i,(path,raw) in enumerate((('report.md',b'backend\n'),('web/index.html',b'button\n'))):
            self.sources[i].start(operation=self.op(),work='member'+str(i))
            file=self.paths[i]/path;file.parent.mkdir(parents=True,exist_ok=True); file.write_bytes(raw)
            self.sources[i].submit(operation=self.op(),work='member'+str(i),summary='Exact result',checks=[dict(name='local check',status='passed',detail='read')])
        self.group.candidate(operation=self.op(),group='pair')
        return self.group.check(operation=self.op(),group='pair')

    def execute(self,shown=None,event=lambda _:None,**kwargs):
        shown=shown or self.group.view('pair')
        return self.group.execute(operation=self.op(),group='pair',application='group-pair',request='accept-pair',receipt=shown['receipt'],statement='Accept both and apply',event=event,**kwargs)

    def accepted(self):
        root=self.store.root()
        return sum(head_summary(map_get(root.heads,work_key('member'+str(i)),self.store.load),self.store.load)[0].payload['phase']=='completed' for i in range(2))


@unittest.skipUnless(sys.platform=='darwin' and available(),'macOS group effects unavailable')
class GroupTests(GroupFixture,unittest.TestCase):
    def test_backup_gate_before_first_publication(self):
        self.plans(); before=self.store.root().ref
        with self.assertRaisesRegex(RecordError,'group-pre-feature-backup-required'): self.create(backup=False)
        self.assertEqual(before,self.store.root().ref)
        self.assertIsNone(self.store.head('group:pair'))

    def test_shared_approval_blocks_individual_decisions(self):
        self.plans(); shown=self.create()
        with self.assertRaisesRegex(RecordError,'group-'):
            p=self.sources[0].plan_review('member0');self.sources[0].approve(operation=self.op(),work='member0',receipt=p['receipt'],statement='one')
        self.group.approve(operation=self.op(),group='pair',receipt=shown['receipt'],statement='both')
        self.assertEqual(['approved','approved'],[s.view('member'+str(i))['state'] for i,s in enumerate(self.sources)])
        self.sources[0].start(operation=self.op(),work='member0');self.sources[1].start(operation=self.op(),work='member1')
        self.assertEqual(0,self.accepted())

    def test_real_checks_then_two_acceptances_and_same_request_replay(self):
        shown=self.results(); self.assertEqual('review',shown['state'],shown)
        self.assertEqual(b'synthetic report\n',(self.root/'report.md').read_bytes()); self.assertEqual(0,self.accepted())
        outcome=self.execute(shown); self.assertEqual(2,outcome['accepted']); self.assertEqual(2,self.accepted())
        before=self.store.root().ref; self.assertEqual(outcome,self.execute(shown)); self.assertEqual(before,self.store.root().ref)
        self.assertEqual(b'backend\n',(self.root/'report.md').read_bytes()); self.assertEqual(b'button\n',(self.root/'web/index.html').read_bytes())
        self.assertIsNone(self.store.head(PENDING))

    def test_required_check_failure_blocks_application(self):
        self.checks[0]['argv']=[sys.executable,'-c','raise SystemExit(3)']
        shown=self.results(); self.assertEqual('checks-required',shown['state'])
        with self.assertRaisesRegex(RecordError,'group-required-check-not-passed'):
            self.group.execute(operation=self.op(),group='pair',application='group-pair',request='accept-pair',receipt='0'*64,statement='accept')
        self.assertEqual(0,self.accepted()); self.assertIsNone(self.store.head(PENDING))

    def reopen(self):
        self.store.close();self.store=self.authority.store()
        for workspace in [self.destination,*(source.workspace for source in self.sources)]:
            workspace.store=self.store;workspace.connections=Connections(self.store)
        for source in self.sources:source.store=self.store
        self.group=GroupService(self.store,self.destination,authority=self.authority.root,lifecycle_authority=self.authority)

    def fault(self,stage):
        shown=self.results(); seen=[]
        def stop(actual):
            seen.append((actual,self.accepted()))
            if actual==stage:raise RuntimeError('synthetic interruption')
        with self.assertRaisesRegex(RuntimeError,'synthetic interruption'):self.execute(shown,event=stop)
        expected=2 if stage=='completed' else 0
        self.assertEqual(expected,self.accepted());self.assertTrue(all(count in (0,2) for _,count in seen))
        before=self.store.root().ref;self.reopen()
        self.assertEqual(2,self.execute(shown)['accepted']);self.assertEqual(2,self.accepted())
        if stage=='completed':self.assertEqual(before,self.store.root().ref)
        else:self.assertIsNone(self.store.head(PENDING))
        return shown

    def test_interrupt_after_first_file_reopen_same_request(self):self.fault('after-install')
    def test_interrupt_after_all_bytes_before_decisions(self):self.fault('before-completion')
    def test_response_lost_after_terminal_commit(self):self.fault('completed')
    def test_resume_skips_already_published_progress(self):
        self.fault('progress-published')
        effect=self.group._selected('pair');progress=link(effect,'progress');indices=[]
        while progress:
            obj=self.group._object(progress);indices.append(obj.payload['index']);progress=link(obj,'previous')
        self.assertEqual([1,0],indices)

    def test_changed_request_payload_cannot_duplicate_acceptance(self):
        shown=self.results();self.execute(shown);before=self.store.root().ref
        with self.assertRaisesRegex(RecordError,'group-request-mismatch'):
            self.group.execute(operation=self.op(),group='pair',application='group-pair',request='accept-pair',receipt=shown['receipt'],statement='different')
        self.assertEqual(before,self.store.root().ref);self.assertEqual(2,self.accepted())

    def test_retest_invalidates_old_receipt(self):
        shown=self.results();new=self.group.check(operation=self.op(),group='pair')
        self.assertNotEqual(shown['receipt'],new['receipt'])
        with self.assertRaisesRegex(RecordError,'group-stale-receipt'):self.execute(shown)
        self.assertEqual(0,self.accepted());self.assertEqual(2,self.execute(new)['accepted'])

    def test_revision_invalidates_exact_candidate(self):
        shown=self.results();review=self.sources[0].review('member0')
        self.sources[0].revise(operation=self.op(),work='member0',receipt=review['receipt'],statement='change wording')
        with self.assertRaisesRegex(RecordError,'group-submission-changed'):self.execute(shown)
        self.assertTrue(self.group.view('pair')['stale']);self.assertEqual(0,self.accepted())

    def test_no_check_record_cannot_be_replaced_by_submission_pass(self):
        original=self.group.check
        self.group.check=lambda **options:self.group.view(options['group'])
        self.results();self.group.check=original
        with self.assertRaisesRegex(RecordError,'group-tested-review-required'):
            self.group.execute(operation=self.op(),group='pair',application='group-pair',request='request',receipt='0'*64,statement='accept')
        self.assertIsNone(self.store.head(PENDING));self.assertEqual(0,self.accepted())

    def test_check_changes_tested_bytes_cannot_pass(self):
        self.checks[0]['argv']=[sys.executable,'-c',"from pathlib import Path; Path('report.md').write_text('changed by check')"]
        shown=self.results();self.assertEqual('checks-required',shown['state']);self.assertFalse(shown['checks'][0]['tree_unchanged'])
        self.assertEqual(b'synthetic report\n',(self.root/'report.md').read_bytes())

    def test_check_cannot_write_original_folder(self):
        target=str(self.root/'report.md')
        self.checks[0]['argv']=[sys.executable,'-c',"from pathlib import Path\ntry: Path("+repr(target)+").write_text('escape')\nexcept PermissionError: pass\nelse: raise SystemExit('write escaped')"]
        shown=self.results();self.assertEqual('passed',shown['checks'][0]['status'],shown['checks'])
        self.assertEqual(b'synthetic report\n',(self.root/'report.md').read_bytes())

    def test_timeout_is_not_a_pass(self):
        self.checks[0]['timeout_seconds']=1;self.checks[0]['argv']=[sys.executable,'-c','import time; time.sleep(5)']
        shown=self.results();self.assertEqual('timeout',shown['checks'][0]['outcome']);self.assertEqual('checks-required',shown['state'])

    def test_unavailable_check_is_not_a_pass(self):
        self.checks[0]['argv']=['/colvia-synthetic-missing-executable']
        shown=self.results();self.assertEqual('checks-required',shown['state']);self.assertEqual(0,self.accepted())

    def test_pending_blocks_individual_accept_and_lifecycle(self):
        from colvia import work_lifecycle
        shown=self.results()
        def stop(stage):
            if stage=='reserved':raise RuntimeError('stop')
        with self.assertRaises(RuntimeError):self.execute(shown,event=stop)
        with self.assertRaisesRegex(RecordError,'external-effect-pending'):
            review=self.sources[0].review('member0');self.sources[0].accept(operation=self.op(),work='member0',receipt=review['receipt'],statement='one')
        with self.assertRaisesRegex(RecordError,'group-shared-decision-required'):
            work_lifecycle.proposal(self.sources[0],'member0','pause','later')
        self.assertEqual(0,self.accepted())

    def test_all_pre_cancel_keeps_two_in_review_and_refuses_request_reuse(self):
        shown=self.results()
        def stop(stage):
            if stage=='reserved':raise RuntimeError('stop')
        with self.assertRaises(RuntimeError):self.execute(shown,event=stop)
        self.assertEqual('cancelled',self.group.cancel(operation=self.op(),group='pair')['state'])
        with self.assertRaisesRegex(RecordError,'group-request-cancelled'):self.execute(shown)
        self.assertEqual(0,self.accepted());self.assertIsNone(self.store.head(PENDING))
        value=self.group.view('pair')
        self.assertEqual('dissolved',self.group.dissolve(operation=self.op(),group='pair',receipt=value['dissolve_receipt'],statement='dissolve after all-pre cancellation')['state'])
        self.assertIsNone(self.store.head('group-member:member0'));self.assertIsNone(self.store.head('group-member:member1'))

    def test_post_file_cancel_refuses_and_forward_resume_succeeds(self):
        shown=self.results()
        def stop(stage):
            if stage=='after-install':raise RuntimeError('stop')
        with self.assertRaises(RuntimeError):self.execute(shown,event=stop)
        with self.assertRaisesRegex(RecordError,'worker-cancel-requires-all-pre'):self.group.cancel(operation=self.op(),group='pair')
        self.assertEqual(0,self.accepted());self.assertEqual(2,self.execute(shown)['accepted'])

    def test_stage_drift_blocks_until_original_staged_bytes_restored(self):
        shown=self.results()
        def stop(stage):
            if stage=='reserved':raise RuntimeError('stop')
        with self.assertRaises(RuntimeError):self.execute(shown,event=stop)
        path=self.authority.root/'effects/group-pair/000000.post';raw=path.read_bytes();path.write_bytes(b'drift')
        with self.assertRaisesRegex(RecordError,'effect-staged-file-changed'):self.execute(shown)
        self.assertEqual(0,self.accepted());self.assertIsNotNone(self.store.head(PENDING))
        path.write_bytes(raw);self.assertEqual(2,self.execute(shown)['accepted'])

    def test_target_drift_blocks_until_prerequisite_restored(self):
        shown=self.results()
        def stop(stage):
            if stage=='after-install':raise RuntimeError('stop')
        with self.assertRaises(RuntimeError):self.execute(shown,event=stop)
        path=self.root/'report.md';raw=path.read_bytes();path.write_bytes(b'late edit')
        with self.assertRaisesRegex(RecordError,'effect-path-unknown'):self.execute(shown)
        self.assertEqual(0,self.accepted());path.write_bytes(raw);self.assertEqual(2,self.execute(shown)['accepted'])

    def test_status_one_group_and_exact_content(self):
        from colvia.project_status import project_status
        from colvia.group_view import content
        self.results();value=project_status(self.store,W)
        self.assertEqual(1,len(value['items']));self.assertEqual('work-group',value['items'][0]['kind'])
        shown=content(self.group,'pair','member0','report.md')
        self.assertEqual('synthetic report\n',shown['before']['text']);self.assertEqual('backend\n',shown['after']['text'])

    def test_activation_backup_must_match_exact_root(self):
        self.plans();self.backup()
        from colvia.planning import Planning
        # A harmless unrelated publication still makes the pre-feature backup stale.
        ref=self.store.head(work_key('member0'))
        self.store.commit_heads(operation=self.op(),expected={'synthetic-note':None},changes={'synthetic-note':ref},validate=lambda _:None)
        with self.assertRaisesRegex(RecordError,'group-pre-feature-backup-required'):self.create(backup=False)
        self.assertIsNone(self.store.head('group:pair'))

    def test_old_readers_writers_and_monotonic_requirement(self):
        from colvia.storage.sqlite import GenerationStore,runtime_capabilities
        caps={c for c in runtime_capabilities() if not c.startswith('schema:group.') and c!='schema:work.decision:2'}
        self.plans()
        options=dict(project=P,instance=I,generation='g',active_check=lambda:None,reader_capabilities=caps,writer_capabilities=caps)
        old=GenerationStore(self.store.path,readonly=True,**options);writer=GenerationStore(self.store.path,**options)
        try:
            self.assertIsNotNone(old.root());shown=self.create()
            with self.assertRaisesRegex(RecordError,'store-reader-capability-unavailable'):old.root()
            with self.assertRaisesRegex(RecordError,'store-reader-capability-unavailable'):writer.begin_import('old-write','test')
            with self.assertRaisesRegex(RecordError,'store-reader-capability-unavailable'):GenerationStore(self.store.path,readonly=True,**options)
            self.group.dissolve(operation=self.op(),group='pair',receipt=shown['dissolve_receipt'],statement='Return to ordinary work')
            self.assertIn('schema:group.member:2',self.store.requirements()['read'])
            with self.assertRaisesRegex(RecordError,'store-reader-capability-unavailable'):old.root()
            receipt=self.sources[0].plan_review('member0')['receipt']
            self.sources[0].approve(operation=self.op(),work='member0',receipt=receipt,statement='ordinary approval after dissolution')
        finally:old.close();writer.close()

    def test_new_backup_restore_keeps_two_decisions_and_exact_bodies(self):
        from io import BytesIO
        from colvia.backup import ImportedSnapshot,ExportBudget,supported_requirements
        from colvia.bodies import body_bytes
        shown=self.results();self.execute(shown);saved=self.store.root().ref;exported=self.backup()
        registry=application_registry();caps=supported_requirements(registry)
        snapshot=ImportedSnapshot(self.home/'restored.sqlite3',BytesIO(Path(exported['destination']).read_bytes()),
            budget=ExportBudget(20000,64*1024*1024),graph_budget=AuditBudget(20000,40000,64*1024*1024),registry=registry,capabilities=caps,writable_capabilities=caps)
        try:
            root=self.authority.import_candidate('restored',snapshot,operation=self.op());self.assertEqual(saved,root)
            self.authority.activate(self.op(),target_generation='restored',expected_root=root,validate_effects=lambda _:None,validate_target=lambda s:self.assertEqual(saved,s.root().ref))
            self.store.close();self.store=self.authority.store()
            self.assertEqual(2,self.accepted())
            selected=self.store.head('group:pair');self.assertEqual('completed',self.group.work.registry.inspect(selected,self.store.load(selected),required=True).payload['state'])
        finally:snapshot.close()

    def test_live_member_scope_and_worker_grant_refuse(self):
        from colvia import scope_addition,work_lifecycle
        from colvia.worker import WorkerService
        self.plans();shown=self.create();self.group.approve(operation=self.op(),group='pair',receipt=shown['receipt'],statement='both')
        with self.assertRaisesRegex(RecordError,'group-shared-decision-required'):
            scope_addition.review(self.sources[0],'member0',[],['extra.txt'],[],'more')
        with self.assertRaisesRegex(RecordError,'group-shared-decision-required'):
            work_lifecycle.proposal(self.sources[0],'member0','pause','later')
        worker=WorkerService(self.sources[0],self.destination,authority=self.authority.root)
        with self.assertRaisesRegex(RecordError,'group-shared-decision-required'):
            worker.grant(operation=self.op(),work='member0',owner='owner',delegate='worker',statement='delegated')

    def test_alias_scopes_refuse_before_group_publication(self):
        for i,path in enumerate(('Docs/a.txt','docs/b.txt')):
            self.sources[i].plan(operation=self.op(),work='member'+str(i),title='member',goal='create',scope=[path],checks=['check'])
        self.backup();before=self.store.root().ref
        with self.assertRaisesRegex(RecordError,'worker-path-alias'):self.create(backup=False)
        self.assertEqual(before,self.store.root().ref)

    def test_atomic_plan_approval_failure_leaves_both_planned(self):
        from unittest.mock import patch
        self.plans();shown=self.create();before=self.store.root().ref
        original=self.group.work._validate_head;count=[0]
        def failure(ref,load):
            if ref.kind=='work.head':
                count[0]+=1
                if count[0]==2:raise RecordError('synthetic-approval-fault')
            return original(ref,load)
        with patch.object(self.group.work,'_validate_head',side_effect=failure),self.assertRaisesRegex(RecordError,'synthetic-approval-fault'):
            self.group.approve(operation=self.op(),group='pair',receipt=shown['receipt'],statement='both')
        self.assertEqual(before,self.store.root().ref)
        self.assertEqual(['planned','planned'],[source.view('member'+str(i))['state'] for i,source in enumerate(self.sources)])

    def test_target_same_bytes_new_identity_is_not_silently_adopted(self):
        shown=self.results()
        def stop(stage):
            if stage=='reserved':raise RuntimeError('stop')
        with self.assertRaises(RuntimeError):self.execute(shown,event=stop)
        target=self.root/'report.md';saved=self.home/'saved-original';target.rename(saved);target.write_bytes(saved.read_bytes())
        with self.assertRaisesRegex(RecordError,'effect-path-unknown'):self.execute(shown)
        self.assertEqual(0,self.accepted());target.unlink();saved.rename(target)
        self.assertEqual(2,self.execute(shown)['accepted'])

    def test_staging_same_bytes_new_identity_is_not_silently_adopted(self):
        shown=self.results()
        def stop(stage):
            if stage=='reserved':raise RuntimeError('stop')
        with self.assertRaises(RuntimeError):self.execute(shown,event=stop)
        target=self.authority.root/'effects/group-pair/000000.post';saved=self.home/'saved-stage';target.rename(saved);target.write_bytes(saved.read_bytes())
        with self.assertRaisesRegex(RecordError,'effect-staged-file-changed'):self.execute(shown)
        self.assertEqual(0,self.accepted());target.unlink();saved.rename(target)
        self.assertEqual(2,self.execute(shown)['accepted'])

    def test_reserved_request_uses_retained_submission_after_source_edit(self):
        shown=self.results()
        def stop(stage):
            if stage=='reserved':raise RuntimeError('stop')
        with self.assertRaises(RuntimeError):self.execute(shown,event=stop)
        (self.paths[0]/'report.md').write_bytes(b'later unsubmitted edit')
        self.assertEqual(2,self.execute(shown)['accepted'])
        self.assertEqual(b'backend\n',(self.root/'report.md').read_bytes())
        self.assertEqual(b'later unsubmitted edit',(self.paths[0]/'report.md').read_bytes())

    def test_unavailable_member_check_cannot_be_overridden_by_union_pass(self):
        original=self.sources[0].submit
        def unavailable(**options):
            options['checks']=[dict(name='local check',status='unavailable',detail='tool unavailable')]
            return original(**options)
        self.sources[0].submit=unavailable
        shown=self.results();self.assertEqual('checks-required',shown['state'])
        with self.assertRaisesRegex(RecordError,'group-member-required-check-not-passed'):
            self.group.execute(operation=self.op(),group='pair',application='group-pair',request='accept-pair',receipt='0'*64,statement='accept')
        self.assertEqual(0,self.accepted())

    def test_qualified_cli_readonly_and_human_group_review(self):
        from colvia.cli import parser,command_readonly,dispatch
        from colvia.presentation import human
        self.plans();shown=self.create()
        args=parser(managed=True).parse_args(['group','--destination',W,'view','pair'])
        self.assertTrue(command_readonly(args));value=dispatch(args,self.store,self.destination,self.authority)
        self.assertIn('통합 검사 계획',human(value));self.assertEqual(shown['receipt'],value['receipt'])

    def test_status_pages_keep_group_once_without_loading_check_logs(self):
        from unittest.mock import patch
        from colvia.project_status import project_status
        from colvia.maps import read_map
        self.results()
        review=self.group._selected('pair')
        blocked=set()
        for ref in read_map(link(review,'evidence'),self.store.load).values():
            evidence=self.group._object(ref)
            blocked.update(link(evidence,c) for c in ('stdout','stderr'))
        original=self.store.load
        def load(ref):
            self.assertNotIn(ref,blocked,'overview must not load retained output bodies')
            return original(ref)
        items=[]; cursor=None
        with patch('colvia.project_status.WINDOW',3),patch.object(self.store,'load',side_effect=load):
            for _ in range(100):
                page=project_status(self.store,W,limit=1,cursor=cursor);items.extend(page['items']);cursor=page['next']
                if cursor is None:break
            else:self.fail('pagination did not finish')
        self.assertEqual(['pair'],[item['work'] for item in items])
        self.assertEqual('review',items[0]['state'])

    def earlier_application(self,state,*,destination=None):
        from colvia.worker import WorkerService
        source=self.sources[0]
        source.plan(operation=self.op(),work='earlier',title='Earlier task',goal='Earlier result',scope=['report.md'],checks=['local'])
        source.approve(operation=self.op(),work='earlier',receipt=source.plan_review('earlier')['receipt'],statement='approve',start=True)
        (self.paths[0]/'report.md').write_bytes(b'earlier result\n')
        source.submit(operation=self.op(),work='earlier',summary='earlier',checks=[dict(name='local',status='passed',detail='synthetic')])
        worker=WorkerService(source,destination or self.destination,authority=self.authority.root)
        shown=worker.prepare(operation=self.op(),application='earlier',work='earlier')
        if state in ('completed','cancelled','pending'):
            def stop(stage):
                if state in ('cancelled','pending') and stage=='reserved':raise RuntimeError('stop')
            try:worker.execute(operation=self.op(),application='earlier',receipt=shown['receipt'],statement='apply',actor='owner',event=stop)
            except RuntimeError:
                if state=='cancelled':worker.cancel(operation=self.op(),application='earlier')
        # Future plans share current bytes; an old unexecuted binding still retains
        # authority even when today's baseline makes it temporarily stale.
        raw=(self.root/'report.md').read_bytes()
        for path in self.paths:(path/'report.md').write_bytes(raw)
        return worker

    def test_completed_individual_history_allows_new_group(self):
        self.earlier_application('completed');self.plans();self.assertEqual('planned',self.create()['state'])

    def test_cancelled_individual_history_allows_new_group(self):
        self.earlier_application('cancelled');self.plans();self.assertEqual('planned',self.create()['state'])

    def test_unexecuted_individual_binding_still_blocks_group(self):
        self.earlier_application('prepared');self.plans()
        with self.assertRaisesRegex(RecordError,'group-prepared-authority-in-use'):self.create()
        self.assertFalse(self.store.has_active_imports())

    def test_binding_targeting_source_still_blocks_group(self):
        self.earlier_application('prepared',destination=self.sources[1].workspace);self.plans()
        with self.assertRaisesRegex(RecordError,'group-prepared-authority-in-use'):self.create()

    def test_dissolve_uses_records_after_source_registration_changes(self):
        from colvia.connection import workspace_key
        self.plans();shown=self.create();key=workspace_key(self.sources[0].workspace.workspace);old=self.store.head(key)
        # Synthetic removal, leaving the original record recoverable. No files move.
        self.store.commit_heads(operation=self.op(),expected={key:old},changes={key:None},validate=lambda _:None)
        self.assertEqual('dissolved',self.group.dissolve(operation=self.op(),group='pair',receipt=shown['dissolve_receipt'],statement='Release obsolete group')['state'])
        self.store.commit_heads(operation=self.op(),expected={key:None},changes={key:old},validate=lambda _:None)
        source=self.sources[0];source.approve(operation=self.op(),work='member0',receipt=source.plan_review('member0')['receipt'],statement='ordinary')
        self.assertEqual('approved',source.view('member0')['state'])

    def test_cli_view_and_dissolve_after_destination_registration_removed(self):
        from colvia.connection import workspace_key
        from colvia.cli import parser,dispatch
        self.plans();self.create();key=workspace_key(W);old=self.store.head(key)
        self.store.commit_heads(operation=self.op(),expected={key:old},changes={key:None},validate=lambda _:None)
        args=parser(managed=True).parse_args(['group','--destination',W,'view','pair'])
        value=dispatch(args,self.store,self.sources[0].workspace,self.authority)
        self.assertTrue(value['destination_path_retained'])
        args=parser(managed=True).parse_args(['group','--destination',W,'dissolve','pair','--receipt',value['dissolve_receipt'],'--statement','Release obsolete destination'])
        self.assertEqual('dissolved',dispatch(args,self.store,self.sources[0].workspace,self.authority)['state'])

    def test_pending_and_completed_group_cannot_dissolve(self):
        shown=self.results()
        def stop(stage):
            if stage=='reserved':raise RuntimeError('stop')
        with self.assertRaises(RuntimeError):self.execute(shown,event=stop)
        for state in ('pending','completed'):
            value=self.group.view('pair');self.assertNotIn('dissolve_receipt',value)
            with self.assertRaisesRegex(RecordError,'group-application-already-started'):
                self.group.dissolve(operation=self.op(),group='pair',receipt=self.group._receipt('dissolve','pair',self.store.head('group:pair')),statement='dissolve')
            if state=='pending':self.execute(shown)

    def test_unreserved_staging_refuses_same_ids_and_fresh_request_succeeds(self):
        shown=self.results()
        def stop(stage):
            if stage=='staging-prepared':raise RuntimeError('stop')
        with self.assertRaises(RuntimeError):self.execute(shown,event=stop)
        self.assertEqual(0,self.accepted());self.assertIsNone(self.store.head(PENDING))
        self.assertIsNone(self.store.head('group-request:accept-pair'));self.assertIsNone(self.store.head('group-application:group-pair'))
        with self.assertRaisesRegex(RecordError,'group-unreserved-staging-exists'):self.execute(shown)
        self.assertTrue((self.authority.root/'effects/group-pair').is_dir())
        result=self.group.execute(operation=self.op(),group='pair',application='group-fresh',request='fresh',receipt=shown['receipt'],statement='Accept both and apply')
        self.assertEqual(2,result['accepted'])

    def test_completed_member_has_no_reopen_receipt_and_archive_still_works(self):
        shown=self.results();self.execute(shown);source=self.sources[0];view=source.view('member0')
        self.assertNotIn('reopen_receipt',view)
        ref=self.store.head(work_key('member0'))
        with self.assertRaisesRegex(RecordError,'group-completed-new-work-required'):
            source.revise(operation=self.op(),work='member0',receipt=source._receipt('reopen','member0',ref),statement='later change')
        self.assertTrue(source.archive(operation=self.op(),work='member0',archived=True)['archived'])

    def test_other_live_group_cannot_share_workspace_roles(self):
        self.plans();self.create()
        for i,source in enumerate(self.sources):source.plan(operation=self.op(),work='other'+str(i),title='Other',goal='Other',scope=['other'+str(i)+'.txt'],checks=['local'])
        with self.assertRaisesRegex(RecordError,'group-workspace-in-use'):
            self.group.create(operation=self.op(),group='other',works=['other0','other1'],checks=self.checks,acknowledgement='already activated')
        self.assertFalse(self.store.has_active_imports())

    def test_later_individual_application_cannot_target_live_group(self):
        from colvia.worker import WorkerService
        self.plans();self.create();source=self.sources[0]
        source.plan(operation=self.op(),work='later',title='Later',goal='Other task',scope=['later.txt'],checks=['local'])
        source.approve(operation=self.op(),work='later',receipt=source.plan_review('later')['receipt'],statement='approve',start=True)
        (self.paths[0]/'later.txt').write_text('later')
        source.submit(operation=self.op(),work='later',summary='later',checks=[dict(name='local',status='passed',detail='synthetic')])
        worker=WorkerService(source,self.destination,authority=self.authority.root)
        with self.assertRaisesRegex(RecordError,'group-workspace-in-use'):
            worker.prepare(operation=self.op(),application='later',work='later')

    def test_confirmed_check_refusal_abandons_only_current_import(self):
        self.checks[0]['cwd']='missing-folder'
        with self.assertRaisesRegex(RecordError,'group-check-environment-unavailable'):self.results()
        self.assertFalse(self.store.has_active_imports());self.assertEqual('checks-required',self.group.view('pair')['state'])

    def test_member_view_tolerates_unrelated_publication(self):
        from unittest.mock import patch
        self.results();source=self.sources[0];original=source._result_agrees;changed=[]
        def observe(*args):
            if not changed:
                ref=self.store.head(work_key('member0'))
                self.store.commit_heads(operation=self.op(),expected={'synthetic-note':None},changes={'synthetic-note':ref},validate=lambda _:None);changed.append(True)
            return original(*args)
        with patch.object(source,'_result_agrees',side_effect=observe):
            value=source.view('member0')
        self.assertEqual('pair',value['work_group']['group']);self.assertTrue(value['current_matches'])

    def test_unreadable_group_row_preserves_identifier(self):
        from unittest.mock import patch
        from colvia.project_status import project_status
        self.plans();self.create()
        with patch('colvia.group_view.snapshot',side_effect=RecordError('synthetic-unreadable')):
            value=project_status(self.store,W)
        self.assertEqual('pair',value['items'][0]['work']);self.assertEqual('unavailable',value['items'][0]['group'])

    def test_windows_records_reuse_exact_group_publication_with_separate_capability(self):
        from types import SimpleNamespace
        from unittest.mock import patch
        from colvia import group_records as gr
        from colvia.graph import Registry

        self.checks = [dict(name="file check", script="print('verify candidate files')",
                            cwd=".", timeout_seconds=3, output_bytes=1024)]
        pre = self.store.requirements()["read"]
        self.assertNotIn("schema:group.plan:3", pre)
        self.group.windows_runner = object()
        native_port = self.group._port()
        with patch.object(self.group, "_port", return_value=native_port):
            self.plans()
            self.backup()
            with patch("colvia.group.sys", SimpleNamespace(platform="win32")):
                shown = self.create(backup=False)
            plan = self.store.head(gr.key("pair"))
            self.assertEqual(3, plan.version)
            self.assertIn("schema:group.plan:3", self.store.requirements()["read"])
            schemas = application_registry()._schemas
            old = Registry(v for (name, version), v in schemas.items()
                           if not (name.startswith("group.") and version == 3) and (name, version) != ("work.decision",4))
            with self.assertRaisesRegex(RecordError, "unknown-required-kind"):
                old.inspect(plan, self.store.load(plan), required=True)
            self.group.approve(operation=self.op(), group="pair", receipt=shown["receipt"], statement="Approve exact plans")
            for i, path in enumerate(("report.md", "web/index.html")):
                source = self.sources[i]
                source.start(operation=self.op(), work="member"+str(i))
                file = self.paths[i] / path
                file.parent.mkdir(parents=True, exist_ok=True)
                file.write_bytes(("member "+str(i)+"\n").encode())
                source.submit(operation=self.op(), work="member"+str(i), summary="Exact result",
                              checks=[dict(name="local check", status="passed", detail="read")])
            self.group.candidate(operation=self.op(), group="pair")
            self.group.windows_runner = None
            blocked = self.group.check(operation=self.op(), group="pair")
            self.assertEqual("checks-required", blocked["state"])
            self.assertNotIn("receipt", blocked)
            self.assertEqual(0, self.accepted())
            runtime = dict(manifest="a"*64, runner="b"*64, harness="c"*64)
            passed = dict(outcome="exited", exit_code=0, elapsed_ns=1, runtime=runtime), b"verified files", b"", True
            with patch("colvia.group_checks._windows_check", return_value=passed):
                tested = self.group.check(operation=self.op(), group="pair")
            self.assertEqual(2, self.execute(tested)["accepted"])
            self.assertEqual(2, self.execute(tested)["accepted"])
            self.assertIn("schema:work.decision:4", self.store.requirements()["read"])
            self.backup()

    def test_unqualified_group_refuses_before_publication(self):
        from unittest.mock import patch
        self.plans();self.backup();before=self.store.root().ref
        with patch('colvia.group.sys.platform','win32'),self.assertRaisesRegex(RecordError,'group-platform-unqualified'):self.create(backup=False)
        self.assertEqual(before,self.store.root().ref)

    def test_pending_individual_effect_still_blocks_group(self):
        self.plans();worker=self.earlier_application('pending');self.backup()
        with self.assertRaisesRegex(RecordError,'external-effect-pending'):self.create(backup=False)
        self.assertIsNone(self.store.head('group:pair'))
        self.assertIsNotNone(self.store.head(PENDING))

    def test_new_individual_prepare_reserves_group_prefix(self):
        from colvia.worker import WorkerService
        worker=WorkerService(self.sources[0],self.destination,authority=self.authority.root)
        before=self.store.root().ref
        with self.assertRaisesRegex(RecordError,'worker-application-prefix-reserved'):
            worker.prepare(operation=self.op(),application='group-reserved',work='not-created')
        self.assertEqual(before,self.store.root().ref)

    def test_unrelated_publication_during_reservation_has_fresh_attempt_recovery(self):
        from unittest.mock import patch
        import threading
        shown=self.results();original=self.store.commit_heads;inserted=[]
        def commit(**options):
            if options['operation'].endswith('-reserve') and not inserted:
                validate=options['validate']
                def racing(view):
                    validate(view);errors=[]
                    def publication():
                        other=self.authority.store()
                        try:
                            ref=other.head(work_key('member0'))
                            other.commit_heads(operation='unrelated-note',expected={'synthetic-note':None},changes={'synthetic-note':ref},validate=lambda _:None)
                        except BaseException as error:errors.append(error)
                        finally:other.close()
                    thread=threading.Thread(target=publication);thread.start();thread.join(timeout=10)
                    self.assertFalse(thread.is_alive());self.assertEqual([],errors);inserted.append(True)
                options['validate']=racing
            return original(**options)
        with patch.object(self.store,'commit_heads',side_effect=commit),self.assertRaisesRegex(RecordError,'validation-root-conflict'):
            self.execute(shown)
        self.assertEqual(0,self.accepted());self.assertIsNone(self.store.head(PENDING))
        with self.assertRaisesRegex(RecordError,'group-unreserved-staging-exists'):self.execute(shown)
        result=self.group.execute(operation=self.op(),group='pair',application='group-retry',request='retry',receipt=shown['receipt'],statement='Accept both and apply')
        self.assertEqual(2,result['accepted'])



    def test_destination_ordinary_work_blocks_group_acceptance(self):
        shown=self.results();work=WorkService(self.store,self.destination)
        work.plan(operation=self.op(),work='other',title='Other',goal='Edit original',scope=['other.txt'],checks=['check'])
        work.approve(operation=self.op(),work='other',receipt=work.plan_review('other')['receipt'],statement='ordinary work')
        work.start(operation=self.op(),work='other')
        with self.assertRaisesRegex(RecordError,'worker-destination-has-active-work'):self.execute(shown)
        self.assertEqual(0,self.accepted());self.assertIsNone(self.store.head(PENDING))

    def test_baseline_disappears_during_check_preparation_closes_import(self):
        from unittest.mock import patch
        from colvia import group_checks
        for root in (self.root,*self.paths):(root/'keep.txt').write_bytes(b'unchanged')
        self.results();original=group_checks.materialize
        def disappear(*args):
            original_open=group_checks.os.open
            def open_after_unlink(path,*args,**kwargs):
                if path=='keep.txt':(self.root/'keep.txt').unlink()
                return original_open(path,*args,**kwargs)
            with patch.object(group_checks.os,'open',side_effect=open_after_unlink):return original(*args)
        with patch.object(group_checks,'materialize',side_effect=disappear):
            with self.assertRaisesRegex(RecordError,'group-baseline-content-changed'):
                self.group.check(operation=self.op(),group='pair')
        self.assertFalse(self.store.has_active_imports());self.assertEqual(0,self.accepted())

    def test_private_check_directory_error_closes_import(self):
        from unittest.mock import patch
        self.results()
        with patch('colvia.group_checks.open_directory',side_effect=PermissionError('synthetic private directory')):
            with self.assertRaisesRegex(RecordError,'group-check-environment-unavailable'):
                self.group.check(operation=self.op(),group='pair')
        self.assertFalse(self.store.has_active_imports())

    def test_private_candidate_file_error_closes_import(self):
        import os
        from unittest.mock import patch
        self.results();original=os.open
        def refuse(path,*args,**kwargs):
            if isinstance(path,Path) and self.authority.root/'group-checks' in path.parents:raise PermissionError('synthetic private copy')
            return original(path,*args,**kwargs)
        with patch('colvia.group_checks.os.open',side_effect=refuse):
            with self.assertRaisesRegex(RecordError,'group-check-environment-unavailable'):
                self.group.check(operation=self.op(),group='pair')
        self.assertFalse(self.store.has_active_imports())

    def test_cli_view_prefers_effective_registered_path(self):
        from unittest.mock import patch
        from types import SimpleNamespace
        from colvia.cli import parser,dispatch
        self.plans();self.create();resolved=self.home/'effective-original'
        registration=SimpleNamespace(root=SimpleNamespace(path=str(resolved)))
        args=parser(managed=True).parse_args(['group','--destination',W,'view','pair'])
        with patch.object(self.sources[0].workspace.connections,'workspace',return_value=(None,registration,None)):
            value=dispatch(args,self.store,self.sources[0].workspace,self.authority)
        self.assertEqual(str(resolved),value['destination_path']);self.assertFalse(value['destination_path_retained'])

    def assert_backup_preserves(self,refs):
        from io import BytesIO
        from colvia.backup import ImportedSnapshot,ExportBudget,supported_requirements
        saved={ref:self.store.load(ref) for ref in refs};exported=self.backup();registry=application_registry();caps=supported_requirements(registry)
        snapshot=ImportedSnapshot(self.home/(self.op()+'.sqlite3'),BytesIO(Path(exported['destination']).read_bytes()),
            budget=ExportBudget(20000,64*1024*1024),graph_budget=AuditBudget(20000,40000,64*1024*1024),registry=registry,capabilities=caps,writable_capabilities=caps)
        try:
            for ref,raw in saved.items():self.assertEqual(raw,snapshot.load(ref))
        finally:snapshot.close()

    def test_replaced_failed_review_and_logs_remain_in_backup(self):
        from colvia.maps import read_map
        self.checks[0]['argv']=[sys.executable,'-c',"print('retained failure');raise SystemExit(1)"]
        self.results();failed=self.store.head('group:pair');review=self.group._object(failed)
        evidence=next(iter(read_map(link(review,'evidence'),self.store.load).values()))
        stdout=link(self.group._object(evidence),'stdout');candidate=link(review,'candidate');operation=self.op()
        self.group.candidate(operation=operation,group='pair')
        before,_=self.store.operation_result(operation);root=self.group._object(before)
        self.assertEqual(failed,map_get(link(root,'heads'),'group:pair',self.store.load))
        self.assert_backup_preserves([failed,evidence,stdout,candidate])

    def test_replaced_dissolution_remains_in_backup(self):
        self.plans();shown=self.create()
        self.group.dissolve(operation=self.op(),group='pair',receipt=shown['dissolve_receipt'],statement='first')
        first=self.store.head('group-dissolved:pair')
        shown=self.create(backup=False)
        self.group.dissolve(operation=self.op(),group='pair',receipt=shown['dissolve_receipt'],statement='second')
        second=self.store.head('group-dissolved:pair');self.assertNotEqual(first,second)
        self.assert_backup_preserves([first,second])

if __name__=='__main__':unittest.main()
