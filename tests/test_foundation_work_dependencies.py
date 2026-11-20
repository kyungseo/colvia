"""Integration checks for user-reported Work dependencies, independent of Work authority."""
from concurrent.futures import ThreadPoolExecutor
import json
from io import BytesIO
from pathlib import Path
from threading import Barrier
from unittest import TestCase
from unittest.mock import patch

from colvia import work_dependencies as dep, work_lifecycle
from colvia.backup import ExportBudget, ImportedSnapshot, supported_requirements, write_export
from colvia.cli import command_readonly, dispatch, parser
from colvia.codec import RecordError
from colvia.composition import CompositionService
from colvia.graph import AuditBudget, GraphAudit, Registry
from colvia.presentation import human
from colvia.project_status import project_status
from colvia.records import application_registry
from colvia.storage.sqlite import GenerationStore
from test_foundation_binding import P, I, W
from test_foundation_work import WorkFixture
from test_foundation_candidate_priority import fill_candidate


class DependencyTests(WorkFixture, TestCase):
    def plan_names(self, *names):
        for n in names:
            self.plan(n, (n+'.md',))

    def command(self, *args, op=None):
        argv = (['--operation',op] if op else []) + ['dependency',*args]
        parsed = parser(managed=True).parse_args(argv)
        self.assertEqual(command_readonly(parsed), args[0]!='apply')
        return dispatch(parsed,self.store,self.workspace)

    def change(self, work, *flags, op, basis=None):
        if basis is None:
            basis = self.command('preview',work,*flags)['basis']
        return self.command('apply',work,*flags,'--basis',basis,'--request','안내 수락 뒤 초대',
                            '--recorder','agent',op=op)

    def detail(self,work,index=0):
        return self.command('show',work)['items'][index]['result']

    def test_bidirectional_reopen_archive_and_no_authority(self):
        self.start('guide',('guide.md',))
        self.plan_names('invite','audit')
        self.plan('trial')
        heads = {w:self.store.head('work:'+w) for w in ('guide','invite','audit','trial')}
        shown = self.command('preview','invite','--add','guide')
        self.assertTrue(shown['first_project_dependency'])
        self.assertIn(shown['basis'], human(shown))
        self.change('invite','--add','guide',op='link')
        self.change('invite','--add','audit',op='second')
        self.assertEqual(heads,{w:self.store.head('work:'+w) for w in heads})
        self.assertEqual([],self.command('show','trial')['items'])
        planned = next(row for row in project_status(self.store,W)['items'] if row['work']=='invite')
        self.assertEqual('planned',planned['state'])
        self.assertEqual('waiting',planned['dependencies']['items'][0]['result']['status'])
        self.assertEqual(['waiting','waiting'],[r['result']['status'] for r in self.command('show','invite')['items']])
        self.service.approve(operation='approve-invite',work='invite',receipt=self.service.plan_review('invite')['receipt'],statement='진행')
        self.service.start(operation='start-invite', work='invite')
        (self.root/'guide.md').write_text('Guide')
        review=self.submit('guide')
        self.assertEqual('review',self.detail('guide')['state'])
        self.service.accept(operation='accept',work='guide',receipt=review['receipt'],statement='수락')
        root=self.store.root().ref
        accepted=self.detail('invite',1)
        self.assertEqual(('accepted',1),(accepted['status'],accepted['revision']))
        self.assertEqual(self.detail('guide'),accepted)
        self.assertEqual(64,len(accepted['decision']))
        page=project_status(self.store,W)
        self.assertIn('필요한 결과',human(page))
        self.assertEqual(root,self.store.root().ref)
        self.service.archive(operation='archive',work='guide',archived=True)
        self.assertEqual(accepted['decision'],self.detail('invite',1)['decision'])
        self.service.archive(operation='restore',work='guide',archived=False)
        v=self.service.view('guide')
        self.service.revise(operation='revise',work='guide',receipt=v['reopen_receipt'],statement='출처 확인')
        self.assertTrue(self.detail('invite',1)['revision_requested'])
        self.assertEqual('active',self.service.view('invite')['state'])
        self.assertIn('선행 결과를 다시 검토 중', human(project_status(self.store,W)))

    def test_changes_evidence_replay_conflict_and_disposition(self):
        self.plan_names('a','b','c')
        args=('b','--add','a')
        preview=self.command('preview',*args)
        first=self.change(*args,op='add',basis=preview['basis'])
        self.assertFalse(first['replayed'])
        life=(self.service,'a','replace','목표 변경','','c')
        work_lifecycle.apply(*life,work_lifecycle.proposal(*life)[0]['receipt'],'replace-work')
        self.assertEqual(('reassign','c'),tuple(self.detail('b')[k] for k in ('status','replacement')))
        self.assertEqual([],self.command('show','c')['items'])
        self.change('b','--remove','a','--add','c',op='replace')
        self.assertEqual('c',self.detail('b')['work'])
        self.change('b','--remove','c',op='clear')
        self.assertTrue(self.change(*args,op='add',basis=preview['basis'])['replayed'])
        self.assertEqual([],self.command('show','b')['items'])
        events=self.command('history','b')['items']
        self.assertEqual(['clear','replace','add'],[e['operation'] for e in events])
        self.assertTrue(all(e['authority']=='reported-dependency-request' and e['recorder']=='agent' for e in events))
        with self.assertRaisesRegex(RecordError,'dependency-operation-conflict'):
            self.change('c','--add','b',op='add',basis=preview['basis'])
        with self.assertRaisesRegex(RecordError,'dependency-work-required'):
            self.command('preview','b','--add','missing')

    def test_stale_interrupted_and_concurrent_opposite_edges(self):
        self.plan_names('a','b','c')
        pa=self.command('preview','a','--add','b')['basis']
        pb=self.command('preview','b','--add','a')['basis']
        before=self.store.root().ref
        with patch.object(self.store,'commit_heads',side_effect=OSError('interrupted')):
            with self.assertRaises(OSError):
                self.change('a','--add','b',op='a1',basis=pa)
        self.assertEqual(before,self.store.root().ref)
        barrier=Barrier(2,timeout=10)
        def write(args):
            work,source,basis=args
            db=GenerationStore(self.store.path,project=P,instance=I,generation='g',active_check=lambda:None)
            try:
                barrier.wait()
                dep.apply(db,work,None,source,basis=basis,request='명시 요청',recorder='agent',operation=work+'1')
                return True
            except RecordError:
                return False
            finally:
                db.close()
        with ThreadPoolExecutor(2) as pool:
            self.assertEqual(1,sum(pool.map(write,[('a','b',pa),('b','a',pb)])))
        stale=self.command('preview','c','--add','a')['basis']
        self.service.approve(operation='approve-c',work='c',receipt=self.service.plan_review('c')['receipt'],statement='진행')
        with self.assertRaisesRegex(RecordError,'dependency-preview-stale'):
            self.change('c','--add','a',op='stale',basis=stale)
        for name in ('c','C'):
            with self.assertRaisesRegex(RecordError,'invalid-dependency-selection'):
                self.command('preview','c','--add',name)

    def test_duplicate_parent_and_mixed_cycle_in_both_write_orders(self):
        self.plan_names('parent','child','third')
        def declare():
            return CompositionService(self.service).declare(operation='declare',parent='parent',children=['child'],
                document='parent.md',checks=['집계 대조'],statement='통합')
        self.change('parent','--add','child',op='dup')
        with self.assertRaisesRegex(RecordError,'composition-dependency-duplicate'):
            declare()
        self.change('parent','--remove','child',op='undup')
        declare()
        with self.assertRaisesRegex(RecordError,'dependency-composition-duplicate'):
            self.command('preview','parent','--add','child')
        self.change('child','--add','third',op='other')
        with self.assertRaisesRegex(RecordError,'dependency-cycle'):
            self.command('preview','third','--add','parent')

    def test_cycle_refused_on_both_apply_and_declaration(self):
        self.plan_names('parent','child','middle')
        self.change('child','--add','middle',op='first')
        self.change('middle','--add','parent',op='second')
        unchanged = self.store.root().ref
        with self.assertRaisesRegex(RecordError,'dependency-cycle'):
            self.change('parent','--add','child',op='loop',basis='irrelevant')
        with self.assertRaisesRegex(RecordError,'dependency-cycle'):
            CompositionService(self.service).declare(operation='invalid',parent='parent',children=['child'],
                document='parent.md',checks=['집계 대조'],statement='통합')
        self.assertEqual(unchanged,self.store.root().ref)

    def test_detail_cursor_and_budgeted_unknown_in_the_overview(self):
        names = ['p%02d' % i for i in range(21)]
        self.plan_names('consumer', *names)
        for name in names:
            self.change('consumer','--add',name,op='add-'+name)
        page = self.command('show','consumer')
        rest = self.command('show','consumer','--cursor',json.dumps(page['next']))
        self.assertEqual(names,[item['work'] for item in page['items']+rest['items']])
        self.assertIsNone(rest['next'])
        with patch.object(dep,'_outcome',side_effect=RecordError('status-detail-limit')):
            page = project_status(self.store,W)
            self.assertTrue(page['partial'])
            self.assertTrue(page['dependency_partial'])
            self.assertIn('확인 불가',human(page))

    def test_pause_and_discard_explain_wait_without_modifying_the_edge(self):
        self.start('source',('source.md',))
        self.plan_names('other')
        self.change('other','--add','source',op='link')
        graph = self.store.head(dep.KEY)
        for action in ('pause','discard'):
            args = (self.service,'source',action,'다른 일 먼저','','')
            preview = work_lifecycle.proposal(*args)[0]
            work_lifecycle.apply(*args,preview['receipt'],action)
            self.assertEqual(graph,self.store.head(dep.KEY))
            details = self.detail('other')
            if action == 'pause':
                self.assertEqual(('waiting','paused'),(details['status'],details['state']))
            else:
                self.assertEqual(('reassign',None),(details['status'],details['replacement']))

    def test_receipt_and_missing_outcome_are_never_approval(self):
        self.plan_names('a','b')
        with self.assertRaisesRegex(RecordError,'dependency-preview-stale'):
            self.change('b','--add','a',op='bad',basis=self.service.plan_review('b')['receipt'])
        self.change('b','--add','a',op='good')
        # First break the captured endpoint, then only the current endpoint.
        missing=self.store.head('work:a')
        load=self.store.load
        def unavailable(ref,*args,**kwargs):
            if ref==missing:
                raise RecordError('object-unavailable')
            return load(ref,*args,**kwargs)
        with patch.object(self.store,'load',unavailable):
            unavailable_page = self.command('show','b')
            self.assertEqual('object-unavailable', unavailable_page['error'])
            self.assertIn('확인할 수 없습니다', human(unavailable_page))
            self.assertEqual('object-unavailable', project_status(self.store,W)['dependency_error'])
        self.service.approve(operation='approve-a',work='a',receipt=self.service.plan_review('a')['receipt'],statement='진행')
        missing=self.store.head('work:a')
        with patch.object(self.store,'load',unavailable):
            self.assertEqual('unknown',self.detail('b')['status'])

    def test_uncertain_return_pages_and_bounds(self):
        self.plan_names('a','b','c','d','e','f')
        args = ('a','--add','b')
        basis = self.command('preview',*args)['basis']
        commit = self.store.commit_heads
        def lost(**kwargs):
            commit(**kwargs)
            raise OSError('return lost')
        with patch.object(self.store,'commit_heads',side_effect=lost), self.assertRaises(OSError):
            self.change(*args,op='lost',basis=basis)
        self.assertTrue(self.change(*args,op='lost',basis=basis)['replayed'])
        for name in ('c','d','e','f'):
            self.change('a','--add',name,op='add-'+name)
        page = project_status(self.store,W)
        source_row = next(r for r in page['items'] if r['work']=='a')
        self.assertTrue(page['dependency_partial'])
        self.assertFalse(page['work_partial'])
        self.assertEqual(4,len(source_row['dependencies']['items']))
        self.assertTrue(source_row['dependencies']['more'])
        self.assertIn('일부 관계',human(page))
        self.assertEqual(5,len(self.command('show','a')['items']))
        with patch.object(dep,'MAX_EDGES',5), self.assertRaisesRegex(RecordError,'dependency-limit'):
            self.command('preview','b','--add','c')
        for i in range(18):
            flag = '--remove' if i%2 == 0 else '--add'
            self.change('a',flag,'f',op='toggle-'+str(i))
        page = dep.history(self.store,'a')
        self.assertEqual(20,len(page['items']))
        self.assertEqual(3,len(self.command('history','a','--cursor',json.dumps(page['next']))['items']))
        self.change('a','--remove','f',op='last')
        with self.assertRaisesRegex(RecordError,'invalid-dependency-cursor'):
            dep.history(self.store,'a',cursor=page['next'])

    def test_relation_backup_restores_and_old_reader_refuses(self):
        self.plan_names('a','b')
        registry=application_registry()
        old=Registry([s for (k,_),s in registry._schemas.items() if k!=dep.KIND])
        caps=supported_requirements(old)
        handle=GenerationStore(self.store.path,project=P,instance=I,generation='g',
                               active_check=lambda:None,reader_capabilities=caps,writer_capabilities=caps)
        self.addCleanup(handle.close)
        before=handle.root().ref
        self.command('show','b')
        self.command('preview','b','--add','a')
        self.assertEqual(before,handle.root().ref)
        self.change('b','--add','a',op='one')
        with self.assertRaisesRegex(RecordError,'store-reader-capability-unavailable'):
            handle.root()
        base=Path(self.tmp.name)
        buf=BytesIO()
        gb=AuditBudget(50000,100000,64*1024**2)
        eb=ExportBudget(50000,64*1024**2)
        audit=GraphAudit(base/'dep.audit',gb)
        try:
            audit.run(self.store.root().ref,self.store.load,registry,require_known=True)
            write_export(buf,project=P,audit=audit,load=self.store.load)
        finally:
            audit.close()
        full=supported_requirements(registry)
        def snapshot(name,reg,supported):
            return ImportedSnapshot(base/name,BytesIO(buf.getvalue()),budget=eb,graph_budget=gb,
                                    registry=reg,capabilities=supported,writable_capabilities=supported)
        with self.assertRaisesRegex(RecordError,'import-capability-unavailable'):
            snapshot('old.import',old,caps)
        snap=snapshot('new.import',registry,full)
        self.addCleanup(snap.close)
        copy=GenerationStore.create(base/'copy.db',project=P,instance='restored',generation='new',
                                    active_check=lambda:None,reader_capabilities=full,writer_capabilities=full)
        self.addCleanup(copy.close)
        fill_candidate(copy,snap,operation='restore',unselected=lambda:None)
        self.assertEqual(self.command('show','b')['items'],dep.show(copy,'b')['items'])
        self.assertEqual(self.command('history','b')['items'],dep.history(copy,'b')['items'])
        with self.assertRaisesRegex(RecordError,'dependency-preview-stale'):
            dep.apply(copy,'b','a',None,basis=self.command('preview','b','--remove','a')['basis'],
                      request='해제',recorder='operator',operation='foreign')
