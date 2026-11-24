"""Bounded member sets, versioned continuation and atomic synthetic effects."""
import sys,unittest
from types import SimpleNamespace
from unittest.mock import patch
from colvia.codec import RecordError
from colvia.records import record,link,head_summary,application_registry
from colvia.maps import map_get,build_map
from colvia.group import GroupService,ACTIVATION,ACTIVATION_V2
from colvia import group_records as gr
from colvia.effects import PENDING
from colvia.work import work_key
from colvia.storage.sqlite import runtime_capabilities
from colvia.platforms.exclusive import available
import test_grouped_acceptance as paired


class MultiFixture(paired.GroupFixture):
    member_count=3
    def setUp(self):
        super().setUp()
        self.works=['member'+str(i) for i in range(self.member_count)]
        self.changes=[(f'part-{i}.txt',f'member {i}\n'.encode()) for i in range(self.member_count)]
        checks='; '.join(f"assert Path({path!r}).read_bytes()=={raw!r}" for path,raw in self.changes)
        self.checks[0]['argv']=[sys.executable,'-B','-c','from pathlib import Path; '+checks]
    def plans(self):
        for i,(path,_) in enumerate(self.changes):
            self.sources[i].plan(operation=self.op(),work=self.works[i],title='Member '+str(i),goal='Own file',scope=[path],checks=['local check'])
    def create(self,backup=True):
        if backup:self.backup()
        return self.group.create(operation=self.op(),group='pair',works=self.works,checks=self.checks,
            acknowledgement='I preserved working files; v2 blocks older runtimes, including their v1 recovery.')
    def approve(self):
        self.plans();shown=self.create()
        return self.group.approve(operation=self.op(),group='pair',receipt=shown['receipt'],statement='Approve all exact plans')
    def submit_member(self,i):
        self.sources[i].start(operation=self.op(),work=self.works[i])
        path,raw=self.changes[i];(self.paths[i]/path).write_bytes(raw)
        return self.sources[i].submit(operation=self.op(),work=self.works[i],summary='Exact member result',
            checks=[dict(name='local check',status='passed',detail='bytes inspected')])
    def results(self):
        self.approve()
        for i in range(self.member_count):self.submit_member(i)
        self.group.candidate(operation=self.op(),group='pair')
        return self.group.check(operation=self.op(),group='pair')
    def accepted(self):
        root=self.store.root()
        return sum(head_summary(map_get(root.heads,work_key(work),self.store.load),self.store.load)[0].payload['phase']=='completed' for work in self.works)
    reopen=paired.GroupTests.reopen


def assert_group_dependency_consumers(case):
    from colvia import work_dependencies as dep
    from colvia.project_status import project_status
    from colvia.work_history import history
    case.sources[0].plan(operation=case.op(),work='consumer',title='Consumer',goal='Use accepted result',scope=['report.md'],checks=['review'])
    shown=dep.preview(case.store,'consumer',None,'member0')
    dep.apply(case.store,'consumer',None,'member0',basis=shown['basis'],request='Use exact accepted result',recorder='operator',operation=case.op())
    root=case.store.root().ref
    dependency=dep.show(case.store,'consumer')
    case.assertEqual('accepted',dependency['items'][0]['result']['status'])
    status=project_status(case.store,case.sources[0].workspace.workspace)
    consumer=next(row for row in status['items'] if row['work']=='consumer')
    case.assertEqual('accepted',consumer['dependencies']['items'][0]['result']['status'])
    # Ordinary view reads the same selected group result without accepting again.
    page=case.sources[0].view('member0');case.assertEqual('completed',page['state'])
    case.assertIsNone(history(case.store,'member0')['unavailable'])
    case.assertEqual(root,case.store.root().ref)

@unittest.skipUnless(sys.platform=='darwin' and available(),'macOS group effects unavailable')
class MultiTests(MultiFixture,unittest.TestCase):
    def test_three_four_eight_whole_review_acceptance_and_replay(self):
        from colvia.presentation import human
        for n in (3,4,8):
            with self.subTest(members=n):
                if n!=3:self.tearDown();self.member_count=n;self.setUp()
                shown=self.results();self.assertEqual(n,shown['member_count']);self.assertEqual(n,len(shown['members']))
                text=human(shown)
                for i,member in enumerate(shown['members']):
                    self.assertIn('Member '+str(i),text);self.assertIn(str(self.paths[i]),text)
                    self.assertIn(self.changes[i][0],text);self.assertEqual(1,member['revision'])
                    self.assertEqual(1,member['submitted_file_count']);self.assertEqual(1,len(member['files']))
                self.assertEqual(n,text.count('변경 파일 · 1개'));self.assertEqual(n,text.count('제출본 1판'))
                self.assertEqual(0,self.accepted());self.assertEqual(n,self.execute(shown)['accepted']);self.assertEqual(n,self.accepted())
                root=self.store.root().ref;self.assertEqual(n,self.execute(shown)['accepted']);self.assertEqual(root,self.store.root().ref)
                for path,raw in self.changes:self.assertEqual(raw,(self.root/path).read_bytes())
                effect=self.group._selected('pair');self.assertEqual(2,effect.ref.version)
                for work in self.works:
                    decision=head_summary(self.store.head(work_key(work)),self.store.load)[3]
                    self.assertEqual(3,decision.ref.version);self.assertEqual(link(effect,'authorization'),link(decision,'authorization'))
                self.assertIsNone(self.store.head(PENDING))
    def test_eight_member_finalization_has_a_guarded_read_budget(self):
        self.tearDown();self.member_count=8;self.setUp()
        shown=self.results(); marks={}
        with patch.object(self.store,'_transaction_inner',wraps=self.store._transaction_inner) as tx:
            def event(stage):
                if stage in ('before-completion','completed'):
                    marks[stage]=sum(not call.kwargs.get('write',False) for call in tx.call_args_list)
            self.assertEqual(8,self.execute(shown,event=event)['accepted'])
        self.assertLess(marks['before-completion'],marks['completed'])
        self.assertLessEqual(marks['completed']-marks['before-completion'],1100)
        self.assertEqual(8,self.accepted())

    def test_managed_cli_create_three_and_refuse_nine(self):
        import json
        from colvia.cli import parser,dispatch
        self.plans();self.backup();checks=self.home/'checks.json';checks.write_text(json.dumps(self.checks))
        def args(works,name):
            return parser(managed=True).parse_args(['--json','group','--destination',self.destination.workspace,'create',name,
                *[arg for work in works for arg in ('--work',work)],'--checks',str(checks),'--acknowledgement','Exact backup and old-runtime consequence'])
        shown=dispatch(args(self.works,'pair'),self.store,self.destination,self.authority)
        self.assertEqual(3,shown['member_count']);self.assertEqual(self.works,[m['work'] for m in shown['members']])
        root=self.store.root().ref
        with self.assertRaisesRegex(RecordError,'group-member-count-unsupported'):
            dispatch(args(['w'+str(i) for i in range(9)],'too-many'),self.store,self.destination,self.authority)
        self.assertEqual(root,self.store.root().ref)
    def test_human_changed_list_excludes_unchanged_scope_and_history_reads_group_decision(self):
        from colvia.cli import parser,dispatch
        from colvia.presentation import human
        for i,(path,_) in enumerate(self.changes):
            self.sources[i].plan(operation=self.op(),work=self.works[i],title='Member '+str(i),goal='Own file',
                scope=[path,'report.md'] if i==0 else [path],checks=['local check'])
        shown=self.create();self.group.approve(operation=self.op(),group='pair',receipt=shown['receipt'],statement='All exact scopes')
        for i in range(3):self.submit_member(i)
        self.group.candidate(operation=self.op(),group='pair');shown=self.group.check(operation=self.op(),group='pair');text=human(shown)
        changes=[line for line in text.splitlines() if line.startswith('변경 · ')]
        self.assertEqual(3,len(changes));self.assertFalse(any('report.md' in line for line in changes));self.assertIn('report.md',text)
        for path,_ in self.changes:self.assertTrue(any(path in line for line in changes))
        self.execute(shown)
        for i,work in enumerate(self.works):
            args=parser(managed=True).parse_args(['--json','ordinary','history',work])
            page=dispatch(args,self.store,self.sources[i].workspace,self.authority)
            self.assertIsNone(page['unavailable']);accepts=[x for x in page['items'] if x['kind']=='accept']
            self.assertEqual(1,len(accepts));self.assertEqual('pair',accepts[0]['work_group']);self.assertEqual('human',accepts[0]['authority'])
            self.assertEqual(1,accepts[0]['revision']);self.assertIn('묶음 수락',human(page));self.assertNotIn('위임 수락',human(page))
        assert_group_dependency_consumers(self)
    def test_extra_map_key_and_crossed_completed_members_refuse(self):
        from colvia.graph import validate_closure
        self.execute(self.results());effect=self.group._selected('pair');plan=gr.plan_for(effect.ref,self.store.load)
        refs=gr.member_refs(effect,'completed',plan,self.store.load)
        for entries,code in (([*zip(self.works,refs),('foreign',refs[0])],'map-entry-limit'),
                             (list(zip(self.works,[refs[1],refs[0],refs[2]])),'group-completion-pair-mismatch')):
            mapping=build_map(entries)
            links={name:(role,link(effect,name)) for name,role in [('authorization','decision'),('manifest','integrity'),('progress','integrity'),('previous','provenance')]}
            links['completed']=('decision',mapping.root)
            bad=record('group.effect',dict(application='group-pair',state='completed'),links,version=2)
            objects=dict([*mapping.objects,bad]);load=lambda ref:objects[ref] if ref in objects else self.store.load(ref)
            with self.assertRaisesRegex(RecordError,'^'+code+'$'):
                validate_closure([bad[0]],load,self.group.work.registry,self.group.work.closure)
    def test_manifest_estimate_bounds_actual_prepared_bytes(self):
        captured=[];original=gr.record
        def retain(kind,payload,links,**kwargs):
            value=original(kind,payload,links,**kwargs)
            if kind=='worker.manifest':captured.append(value[1])
            return value
        with patch.object(gr,'record',side_effect=retain):shown=self.results()
        def stop(stage):
            if stage=='reserved':raise RuntimeError('reserved')
        with self.assertRaisesRegex(RuntimeError,'reserved'):self.execute(shown,event=stop)
        effect=self.group._selected('pair');actual=self.store.load(link(effect,'manifest'))
        self.assertTrue(captured);self.assertGreaterEqual(min(map(len,captured)),len(actual))
        import json
        from colvia.storage.sqlite import _token, MAX_TOKEN_LENGTH
        self.assertEqual(MAX_TOKEN_LENGTH,len(json.loads(captured[0])['payload']['application']))
        _token('x'*MAX_TOKEN_LENGTH)
        with self.assertRaisesRegex(RecordError,'invalid-store-id'):_token('x'*(MAX_TOKEN_LENGTH+1))
        self.assertEqual(0,self.accepted());self.assertEqual(3,self.execute(shown)['accepted'])

    def test_invalid_counts_and_duplicate_members_publish_nothing(self):
        self.plans();self.backup();before=self.store.root().ref
        for works in ([],['member0'],['member0']*2,['x'+str(i) for i in range(9)]):
            with self.subTest(works=works),self.assertRaisesRegex(RecordError,'group-member-count-unsupported'):
                self.group.create(operation=self.op(),group='bad',works=works,checks=self.checks,acknowledgement='exact')
            self.assertEqual(before,self.store.root().ref)
        self.assertFalse((self.authority.root/'effects').exists());self.assertIsNone(self.store.head(PENDING))
    def test_missing_middle_submission_cannot_create_candidate(self):
        self.approve();self.submit_member(0);self.submit_member(2);root=self.store.root().ref
        with self.assertRaisesRegex(RecordError,'group-all-submissions-required'):self.group.candidate(operation=self.op(),group='pair')
        self.assertEqual(root,self.store.root().ref);self.assertEqual(0,self.accepted())
    def test_every_member_revision_invalidates_review_without_acceptance_offer(self):
        from colvia.presentation import human
        shown=self.results()
        for i in range(self.member_count):
            review=self.sources[i].review(self.works[i])
            self.sources[i].revise(operation=self.op(),work=self.works[i],receipt=review['receipt'],statement='Revise this member')
            with self.assertRaisesRegex(RecordError,'group-submission-changed'):self.execute(shown)
            stale=self.group.view('pair');self.assertNotIn('receipt',stale);self.assertTrue(stale['stale'])
            self.assertNotIn('수락과 원래 폴더 반영을 함께 결정',human(stale));self.assertEqual(0,self.accepted())
            self.sources[i].submit(operation=self.op(),work=self.works[i],summary='Revised member',checks=[dict(name='local check',status='passed',detail='checked')])
            self.group.candidate(operation=self.op(),group='pair');shown=self.group.check(operation=self.op(),group='pair')
    def test_middle_file_interruption_reopens_to_zero_or_all(self):
        shown=self.results();installs=0
        def stop(stage):
            nonlocal installs
            if stage=='after-install':
                installs+=1
                if installs==2:raise RuntimeError('middle manifest entry')
        with self.assertRaisesRegex(RuntimeError,'middle manifest entry'):self.execute(shown,event=stop)
        self.assertEqual(0,self.accepted())
        self.assertTrue((self.root/self.changes[0][0]).exists());self.assertTrue((self.root/self.changes[1][0]).exists())
        self.assertFalse((self.root/self.changes[2][0]).exists())
        self.reopen();self.assertEqual(3,self.execute(shown)['accepted']);self.assertEqual(3,self.accepted())
    def test_group_decision_can_archive_but_cannot_reopen_member(self):
        self.execute(self.results())
        for i,work in enumerate(self.works):
            service=self.sources[i];shown=service.view(work)
            self.assertNotIn('reopen_receipt',shown)
            with self.assertRaisesRegex(RecordError,'group-completed-new-work-required'):
                ref=service._head(work)[0]
                service.revise(operation=self.op(),work=work,receipt=service._receipt('reopen',work,ref),statement='Reopen')
            self.assertTrue(service.archive(operation=self.op(),work=work,archived=True)['archived'])
        self.assertEqual(3,self.group.view('pair')['accepted'])
    def test_backup_restores_every_decision_and_exact_member_body(self):
        from io import BytesIO
        from pathlib import Path
        from colvia.backup import ImportedSnapshot,ExportBudget,supported_requirements
        from colvia.graph import AuditBudget
        from colvia.bodies import body_bytes
        self.execute(self.results());saved=self.store.root().ref;exported=self.backup()
        registry=application_registry();caps=supported_requirements(registry)
        snapshot=ImportedSnapshot(self.home/'restored.sqlite3',BytesIO(Path(exported['destination']).read_bytes()),
            budget=ExportBudget(20000,64*1024**2),graph_budget=AuditBudget(20000,40000,64*1024**2),registry=registry,capabilities=caps,writable_capabilities=caps)
        try:
            root=self.authority.import_candidate('restored',snapshot,operation=self.op());self.assertEqual(saved,root)
            self.authority.activate(self.op(),target_generation='restored',expected_root=root,validate_effects=lambda _:None,validate_target=lambda store:self.assertEqual(saved,store.root().ref))
            self.reopen();self.assertEqual(3,self.accepted())
            for work,(path,raw) in zip(self.works,self.changes):
                _,_,result,decision=head_summary(self.store.head(work_key(work)),self.store.load)
                self.assertEqual(3,decision.ref.version)
                body=map_get(link(result,'after'),path,self.store.load)
                self.assertEqual(raw,b''.join(body_bytes(body,self.store.load)))
        finally:snapshot.close()
    def test_truncated_logs_have_exact_sizes_and_hashes(self):
        self.checks[0]['output_bytes']=8192;self.checks[0]['argv']=[sys.executable,'-B','-c',"print('x'*5000)"]
        shown=self.results();check=shown['checks'][0]
        self.assertEqual(4096,len(check['logs']['stdout']));self.assertEqual(5001,check['log_metadata']['stdout']['size'])
        self.assertTrue(check['log_metadata']['stdout']['truncated']);self.assertFalse(check['log_metadata']['stderr']['truncated'])
        from colvia.presentation import human
        self.assertIn('전체 5001바이트 중 앞 4096바이트 표시',human(shown))
    def test_approval_failure_never_publishes_a_subset(self):
        self.plans();shown=self.create();before=self.store.root().ref;original=self.group.work._validate_head
        def fail(ref,load=None):
            if head_summary(ref,load or self.store.load)[0].payload['work']=='member1':raise RecordError('middle-validation-failed')
            return original(ref,load)
        with patch.object(self.group.work,'_validate_head',side_effect=fail),self.assertRaisesRegex(RecordError,'middle-validation-failed'):
            self.group.approve(operation=self.op(),group='pair',receipt=shown['receipt'],statement='all')
        self.assertEqual(before,self.store.root().ref)
        self.assertEqual(['planned']*3,[s.view(w)['state'] for s,w in zip(self.sources,self.works)])
    def test_foreign_or_missing_map_member_refuses_full_candidate(self):
        from colvia.graph import validate_closure
        shown=self.results();review=self.group._selected('pair');candidate=self.group._object(link(review,'candidate'));plan=gr.plan_for(candidate.ref,self.store.load)
        refs=gr.member_refs(candidate,'head',plan,self.store.load)
        for entries in (list(zip(self.works[:-1],refs[:-1])),[(self.works[0],refs[0]),(self.works[1],refs[1]),('foreign',refs[2])]):
            mapping=build_map(entries);bad=record('group.candidate',dict(group='pair'),dict(approval=('decision',link(candidate,'approval')),heads=('decision',mapping.root),tree=('integrity',link(candidate,'tree')),after=('integrity',link(candidate,'after'))),version=2)
            objects=dict([*mapping.objects,bad]);load=lambda ref:objects[ref] if ref in objects else self.store.load(ref)
            with self.assertRaisesRegex(RecordError,'group-member-map-mismatch'):validate_closure([bad[0]],load,self.group.work.registry,self.group.work.closure)
        self.assertEqual(0,self.accepted());self.assertIsNone(self.store.head(PENDING))
    def test_crossed_approval_member_map_refuses(self):
        from colvia.graph import validate_closure
        self.approve();approval=self.group._selected('pair');plan=gr.plan_for(approval.ref,self.store.load)
        refs=gr.member_refs(approval,'approval',plan,self.store.load);refs[0],refs[1]=refs[1],refs[0]
        links,objects=gr.member_links(2,'approval',self.works,refs)
        bad=record('group.approval',dict(statement=approval.payload['statement']),dict(links,plan=('decision',plan.ref)),version=2)
        objects=dict([*objects,bad]);load=lambda ref:objects[ref] if ref in objects else self.store.load(ref)
        with self.assertRaisesRegex(RecordError,'group-approval-mismatch'):validate_closure([bad[0]],load,self.group.work.registry,self.group.work.closure)
    def test_partial_completion_map_and_version_crossing_refuse(self):
        from colvia.graph import validate_closure
        self.execute(self.results());effect=self.group._selected('pair');plan=gr.plan_for(effect.ref,self.store.load)
        refs=gr.member_refs(effect,'completed',plan,self.store.load);mapping=build_map(zip(self.works[:-1],refs[:-1]))
        links={name:(edge_role,link(effect,name)) for name,edge_role in [('authorization','decision'),('manifest','integrity'),('progress','integrity'),('previous','provenance')]}
        links['completed']=('decision',mapping.root)
        bad=record('group.effect',dict(application='group-pair',state='completed'),links,version=2)
        objects=dict([*mapping.objects,bad]);load=lambda ref:objects[ref] if ref in objects else self.store.load(ref)
        with self.assertRaisesRegex(RecordError,'group-member-map-mismatch'):validate_closure([bad[0]],load,self.group.work.registry,self.group.work.closure)
        auth=link(effect,'authorization');decision=head_summary(refs[0],self.store.load)[3]
        payload={k:v for k,v in decision.payload.items() if k!='links'}
        bad=record('work.decision',payload,dict(result=('decision',link(decision,'result')),authorization=('decision',auth)),version=2)
        with self.assertRaisesRegex(RecordError,'group-decision-version-required'):application_registry().inspect(*bad,required=True)


@unittest.skipUnless(sys.platform=='darwin' and available(),'macOS group effects unavailable')
class LegacyContinuationTests(paired.GroupFixture,unittest.TestCase):
    reopen=paired.GroupTests.reopen
    def create(self,backup=True):
        with patch('colvia.group.CURRENT_VERSION',1):return super().create(backup)
    def test_legacy_plan_continues_without_v2_capabilities(self):
        shown=self.results();self.assertEqual(1,self.group._selected('pair').ref.version)
        outcome=self.execute(shown);self.assertEqual(2,outcome['accepted'])
        self.assertEqual(1,self.group._selected('pair').ref.version)
        self.assertTrue(all(not (c.startswith('schema:group.') and c.endswith(':2')) and c!='schema:work.decision:3' for c in self.store.requirements()['read']))
        for work in ('member0','member1'):self.assertEqual(2,head_summary(self.store.head(work_key(work)),self.store.load)[3].ref.version)
        from colvia.work_history import history
        for work in ('member0','member1'):
            page=history(self.store,work);self.assertIsNone(page['unavailable'])
            self.assertEqual(['pair'],[row['work_group'] for row in page['items'] if row['kind']=='accept'])
        assert_group_dependency_consumers(self)
    def test_legacy_partial_effect_reopens_without_format_upgrade(self):
        shown=self.results()
        def stop(stage):
            if stage=='after-install':raise RuntimeError('old interruption')
        with self.assertRaisesRegex(RuntimeError,'old interruption'):self.execute(shown,event=stop)
        self.reopen();self.assertEqual(2,self.execute(shown)['accepted']);self.assertEqual(1,self.group._selected('pair').ref.version)
    def test_v2_activation_requires_new_backup_and_keeps_v1_activation(self):
        self.plans();shown=self.create();v1=self.store.head(ACTIVATION)
        self.group.dissolve(operation=self.op(),group='pair',receipt=shown['dissolve_receipt'],statement='Release old group')
        before=self.store.root().ref
        with self.assertRaisesRegex(RecordError,'group-pre-feature-backup-required'):
            paired.GroupFixture.create(self,backup=False)
        self.assertEqual(before,self.store.root().ref);self.assertIsNone(self.store.head(ACTIVATION_V2))
        self.backup();backed=self.store.root().ref;shown=paired.GroupFixture.create(self,backup=False)
        self.assertEqual(v1,self.store.head(ACTIVATION));v2=self.group._object(self.store.head(ACTIVATION_V2))
        self.assertEqual(backed,link(v2,'backup_root'));self.assertEqual(2,v2.ref.version)
        self.group.dissolve(operation=self.op(),group='pair',receipt=shown['dissolve_receipt'],statement='Release new group')
        self.assertIn('schema:group.plan:2',self.store.requirements()['read'])
    def test_v2_cannot_reuse_a_reserved_v1_request_identifier(self):
        shown=self.results()
        def stop(stage):
            if stage=='reserved':raise RuntimeError('reserved')
        with self.assertRaisesRegex(RuntimeError,'reserved'):self.execute(shown,event=stop)
        self.group.cancel(operation=self.op(),group='pair');shown=self.group.view('pair')
        self.group.dissolve(operation=self.op(),group='pair',receipt=shown['dissolve_receipt'],statement='Release old members')
        (self.paths[0]/'report.md').write_bytes(b'synthetic report\n');(self.paths[1]/'web/index.html').unlink()
        works=['new0','new1']
        for source,work,path in zip(self.sources,works,('report.md','web/index.html')):
            source.plan(operation=self.op(),work=work,title=work,goal='New group',scope=[path],checks=['local check'])
        self.backup();shown=self.group.create(operation=self.op(),group='new',works=works,checks=self.checks,acknowledgement='V2 backup and compatibility acknowledged')
        self.group.approve(operation=self.op(),group='new',receipt=shown['receipt'],statement='new plans')
        for i,(path,raw) in enumerate((('report.md',b'backend\n'),('web/index.html',b'button\n'))):
            self.sources[i].start(operation=self.op(),work=works[i]);(self.paths[i]/path).write_bytes(raw)
            self.sources[i].submit(operation=self.op(),work=works[i],summary='new',checks=[dict(name='local check',status='passed',detail='read')])
        self.group.candidate(operation=self.op(),group='new');shown=self.group.check(operation=self.op(),group='new');before=self.store.root().ref
        with self.assertRaisesRegex(RecordError,'group-request-mismatch'):
            self.group.execute(operation=self.op(),group='new',application='group-new',request='accept-pair',receipt=shown['receipt'],statement='new exact results')
        self.assertEqual(before,self.store.root().ref);self.assertIsNone(self.store.head(PENDING))
    def test_v1_v2_direct_group_edge_mixing_refuses_structurally(self):
        self.plans();self.create();plan=self.group._selected('pair')
        bad=record('group.member',dict(group='pair',work='member0'),dict(plan=('decision',plan.ref)),version=2)
        with self.assertRaisesRegex(RecordError,'group-record-version-mismatch'):application_registry().inspect(*bad,required=True)


class UnionLimitTests(unittest.TestCase):
    def test_whole_union_path_and_body_limits(self):
        with self.assertRaisesRegex(RecordError,'group-union-path-limit'):gr.union_limits([],[],[],[{}]*100001)
        from colvia.bodies import BODY_LIMIT
        entries=[dict(path=f'part-{i}',kind='regular',size=BODY_LIMIT) for i in range(5)]
        with self.assertRaisesRegex(RecordError,'submission-body-limit'):gr.union_limits([],entries,[e['path'] for e in entries],[])
    def test_v2_schema_rejects_nine_without_any_reference_load(self):
        from uuid import UUID
        works=['m'+str(i) for i in range(9)];sources=[str(UUID(int=i+1)) for i in range(9)]
        p=dict(group='g',works=works,sources=sources,destination=str(UUID(int=99)),checks=[],acknowledgement='exact',links={})
        with self.assertRaisesRegex(RecordError,'group-member-count-unsupported'):gr._plan_v2(p)
