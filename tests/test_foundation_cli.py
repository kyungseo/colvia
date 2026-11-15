"""Source-only process journeys; no installed runtime or host qualification."""
from pathlib import Path
import json,os,subprocess,sys,tempfile,unittest
from colvia.binding import Locator,ProjectBinding,WorkspaceRegistration,Topology
from colvia.codec import canonical_bytes
from colvia.connection import Connections
from colvia.platforms.posix import location
from colvia.storage.authority import Authority
from test_foundation_binding import P,I,W

class CLITests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='source-cli-');self.home=Path(self.tmp.name)
        self.root=self.home/'project';self.root.mkdir();self.authority=self.home/'authority'
        authority=Authority.create(self.authority,project=P,instance=I,generation='g')
        locator=Locator(P,I,1,'a'*64,W)
        (self.root/'.colvia-link.json').write_bytes(canonical_bytes(locator.payload()))
        topology=Topology('plain',location(self.root));store=authority.store()
        try:Connections(store).connect(operation='connect',binding=ProjectBinding(locator,'plain',topology.root),observed=topology,
            workspace=WorkspaceRegistration(W,topology.root,None),verify_topology=lambda:Topology('plain',location(self.root)))
        finally:store.close()
        (self.root/'source.csv').write_bytes(b'type,count\nrefund,5\n')
        self.prefix=[sys.executable,'-I','-B','-c',"import sys;sys.path.insert(0,sys.argv.pop(1));from colvia.cli import main;raise SystemExit(main())",str(Path(__file__).resolve().parents[1]/'src'),
            '--source-development','--authority',str(self.authority),'--project',P,'--workspace',W,'--root',str(self.root)]
    def tearDown(self):self.tmp.cleanup()
    def call(self,*args,machine=True,code=0):
        result=subprocess.run(self.prefix+(['--json'] if machine else [])+list(args),capture_output=True,text=True,timeout=20)
        self.assertEqual(code,result.returncode,result.stdout+'\n'+result.stderr)
        self.assertNotIn('Traceback',result.stderr)
        return json.loads(result.stdout) if machine else result.stdout
    def plan(self,work='report'):
        return self.call('ordinary','plan',work,'--title','회의 보고서','--goal','문의 비교','--path',work+'.md',
                         '--check','원본 보존','--check','집계 대조','--exclude','우선순위','--exclude','외부 게시')
    def test_process_restart_submit_and_single_acceptance_without_internal_human_output(self):
        plan=self.plan()
        self.call('ordinary','approve','report','--receipt',plan['receipt'],'--statement','그 범위로 진행해')
        self.call('ordinary','start','report');(self.root/'report.md').write_text('# 보고서\n환불 5건\n')
        self.call('ordinary','submit','report','--summary','문의 유형을 비교했습니다.','--passed','원본 보존::원본 동일','--passed','집계 대조::5건 대조')
        shown=self.call('ordinary','review','report',machine=False)
        for private in ('receipt','sha256','SKILL.md',str(self.home),'revision'):self.assertNotIn(private,shown)
        review=self.call('ordinary','review','report')
        final=self.call('ordinary','accept','report','--receipt',review['receipt'],'--statement','이대로 마무리하자',machine=False)
        self.assertIn('마무리했습니다',final);self.assertLess(len(final.splitlines()),4)
        self.assertEqual('completed',self.call('ordinary','view','report')['state'])
        refused=self.call('ordinary','review','report',code=2)
        self.assertEqual('result-not-awaiting-review',refused['error'])
        self.assertIn('검토를 기다리는 상태가 아닙니다',refused['message'])
        self.assertNotIn('현재 상태를 확인하지 못해',refused['message'])
        self.assertEqual('completed',self.call('ordinary','view','report')['state'])
    def test_file_read_denial_does_not_claim_record_folder_or_lose_work(self):
        plan=self.plan()
        self.call('ordinary','approve','report','--receipt',plan['receipt'],'--statement','진행')
        self.call('ordinary','start','report')
        (self.root/'report.md').write_text('draft')
        before=self.call('ordinary','view','report')
        script="""import sys,os,errno
from unittest.mock import patch
sys.path.insert(0,sys.argv.pop(1))
from colvia.cli import main
original=os.open
def guarded(path,*args,**kwargs):
    if path=='source.csv' and kwargs.get('dir_fd') is not None:
        raise PermissionError(errno.EACCES,'fixture denied',path)
    return original(path,*args,**kwargs)
with patch('colvia.platforms.posix.os.open',side_effect=guarded):
    raise SystemExit(main())
"""
        prefix=list(self.prefix);prefix[4]=script
        for machine in (True,False):
            result=subprocess.run(prefix+(['--json'] if machine else [])+[
                'ordinary','submit','report','--summary','draft',
                '--passed','원본 보존::same','--passed','집계 대조::five'],
                capture_output=True,text=True,timeout=20)
            self.assertEqual(2,result.returncode,result.stdout+result.stderr)
            self.assertNotIn('Traceback',result.stderr)
            message=json.loads(result.stdout)['message'] if machine else result.stdout
            if machine:self.assertEqual('access-denied',json.loads(result.stdout)['error'])
            for misleading in ('기록 폴더','허용해 주세요','변경하지 않았','작업이 없습니다',str(self.home),'fixture denied'):
                self.assertNotIn(misleading,message)
            self.assertIn('현재 상태',message)
            self.assertEqual(before,self.call('ordinary','view','report'))
        self.assertEqual('draft',(self.root/'report.md').read_text())
        self.assertEqual(b'type,count\nrefund,5\n',(self.root/'source.csv').read_bytes())

    def test_repeat_options_and_candidate_pagination(self):
        self.plan();plan=self.call('ordinary','plan-review','report')
        self.assertEqual(['원본 보존','집계 대조'],plan['checks'])
        self.assertEqual(['우선순위','외부 게시'],plan['excludes'])
        for name in ('a','b','c'):
            self.call('candidate','save',name,'--title',name,'--reason','후속 후보')
        first=self.call('candidate','list','--limit','2');self.assertEqual(2,len(first['items']))
        second=self.call('candidate','list','--limit','2','--cursor',json.dumps(first['next']))
        self.assertEqual(1,len(second['items']))
        self.assertEqual({'a','b','c'},{v['candidate'] for page in (first,second) for v in page['items']})
        self.call('candidate','save','d','--title','d','--reason','추가')
        refused=self.call('candidate','list','--cursor',json.dumps(first['next']),code=2)
        self.assertEqual('list-changed-or-invalid-cursor',refused['error'])
    def test_stored_result_remains_readable_after_project_disappears(self):
        plan=self.plan();self.call('ordinary','approve','report','--receipt',plan['receipt'],'--statement','진행')
        self.call('ordinary','start','report');(self.root/'report.md').write_text('preserved')
        self.call('ordinary','submit','report','--summary','완료','--passed','원본 보존::동일','--passed','집계 대조::대조')
        self.root.rename(self.home/'project-moved')
        review=self.call('ordinary','review','report');self.assertIsNone(review['current_matches'])
        self.assertIn('receipt',review)
        content=self.call('ordinary','content','report','report.md');self.assertEqual('preserved',content['after']['text'])
        self.call('ordinary','accept','report','--receipt',review['receipt'],'--statement','수락',code=2)

    def test_unknown_failure_names_operation_and_can_be_inspected_without_retry(self):
        from contextlib import redirect_stdout
        from io import StringIO
        from unittest.mock import patch
        from colvia.cli import main
        output=StringIO()
        with patch('colvia.cli.dispatch',side_effect=RuntimeError('internal detail')),redirect_stdout(output):
            status=main(self.prefix[6:]+['--json','--operation','known-operation','ordinary','view','missing'])
        value=json.loads(output.getvalue());self.assertEqual(2,status)
        self.assertEqual('command-outcome-unknown',value['error']);self.assertEqual('known-operation',value['operation'])
        self.assertNotIn('internal detail',output.getvalue())
        self.assertFalse(self.call('operation','known-operation')['recorded'])
        self.assertTrue(self.call('operation','connect')['recorded'])

    def test_check_mismatch_explains_and_preserves_truthful_unresolved_checks(self):
        plan=self.plan();self.call('ordinary','approve','report','--receipt',plan['receipt'],'--statement','진행')
        self.call('ordinary','start','report');(self.root/'report.md').write_text('검토용 본문')
        original=(self.root/'source.csv').read_bytes()
        for label,flags in (
            ('missing',['--failed','원본 보존::검사 실패']),
            ('extra',['--failed','원본 보존::검사 실패','--unavailable','집계 대조::미실행','--unavailable','렌더링::미실행'])):
            for machine in (True,False):
                operation=label+str(machine)
                value=self.call('--operation',operation,'ordinary','submit','report','--summary','검토용',*flags,
                                machine=machine,code=2)
                message=value['message'] if machine else value
                if machine:self.assertEqual('check-report-mismatch',value['error'])
                self.assertIn('항목 이름 또는 개수',message);self.assertIn('실패·미실행 검사도 그대로',message)
                self.assertIn('조회·수락',message);self.assertNotIn('현재 상태를 확인하지 못해',message)
                self.assertFalse(self.call('operation',operation)['recorded'])
                self.assertEqual('active',self.call('ordinary','view','report')['state'])
        # Invalid report input now refuses before creating an import. Prove
        # there is nothing to abandon, then reuse that never-started ID.
        store=Authority(self.authority,project=P).store(readonly=True)
        try:
            for label in ('missingTrue','missingFalse','extraTrue','extraFalse'):
                self.assertIsNone(store.db.execute('SELECT id FROM imports WHERE id=?',(label,)).fetchone())
                self.assertEqual(0,store.db.execute('SELECT count(*) FROM claims WHERE import_id=?',(label,)).fetchone()[0])
        finally:store.close()
        review=self.call('--operation','missingTrue','ordinary','submit','report','--summary','수정한 검사 결과',
                         '--failed','원본 보존::검사 실패','--unavailable','집계 대조::미실행')
        self.assertTrue(self.call('operation','missingTrue')['recorded'])
        self.assertEqual('review',review['state'])
        self.assertEqual(['failed','unavailable'],[check['status'] for check in review['checks']])
        human=self.call('ordinary','review','report',machine=False)
        self.assertIn('원본 보존',human);self.assertIn('집계 대조',human)
        self.assertEqual(original,(self.root/'source.csv').read_bytes())
        self.assertEqual('검토용 본문',(self.root/'report.md').read_text())

    def test_missing_work_and_invalid_cursor_are_short_failures(self):
        value=self.call('ordinary','view','missing',code=2);self.assertEqual('work-not-found',value['error'])
        value=self.call('ordinary','list','--cursor','not-json',code=2)
        self.assertEqual('list-changed-or-invalid-cursor',value['error'])

    def test_followup_display_distinguishes_recorded_choices_and_preserves_read_state(self):
        self.plan()
        command=('followup','report')
        missing={'work':'report','choice':'undecided','recorded':False,'target':None}
        self.assertEqual(missing,self.call(*command))
        self.assertIn('기록한 적이 없습니다',self.call(*command,machine=False))
        store=Authority(self.authority,project=P).store(readonly=True)
        self.addCleanup(store.close)
        prior=store.root().ref
        for choice,label in [('none','후속 작업 없음'),('undecided','후속 결정을 미뤘습니다')]:
            self.assertEqual(dict(missing,choice=choice,recorded=True,statement='확인'),
                             self.call(*command,'--choice',choice,'--statement','확인'))
            current=store.root().ref
            self.assertNotEqual(prior,current)
            schema=(store.db.execute('PRAGMA schema_version').fetchone()[0],
                    store.db.execute('PRAGMA user_version').fetchone()[0])
            self.assertIn(label,self.call(*command,machine=False))
            self.assertIn(label,self.call('ordinary','view','report',machine=False))
            self.assertIn(label,self.call('ordinary','list',machine=False))
            self.assertEqual(current,store.root().ref)
            self.assertEqual(schema,(store.db.execute('PRAGMA schema_version').fetchone()[0],
                                     store.db.execute('PRAGMA user_version').fetchone()[0]))
            prior=current
        from colvia.codec import RecordError
        from colvia.planning import _followup
        with self.assertRaisesRegex(RecordError,'invalid-followup-choice'):
            _followup(dict(work='report',choice='future',target=None,statement='확인',links={}))

    def test_followup_and_candidate_show_recorded_target_and_refuse_false_current_status(self):
        source=self.plan()
        target=self.plan('next')
        self.call('candidate','save','option','--title','당시 후보\n\x1b[31m','--reason','검토')
        self.call('followup','report','--choice','candidate','--target','option','--statement','기록')
        shown=self.call('followup','report',machine=False)
        self.assertIn('당시 후보\\u000a\\u001b[31m',shown)
        self.assertEqual(1,len(shown.splitlines()))
        self.call('candidate','save','option','--title','수정된 후보','--reason','변경','--work','next')
        shown=self.call('ordinary','view','report',machine=False)
        self.assertIn('이후 후보 기록이 변경됨',shown)
        self.assertNotIn('수정된 후보',shown)
        self.assertIn('관련 Work "회의 보고서" (next) · 계획',self.call('candidate','list',machine=False))
        self.call('followup','report','--choice','work','--target','next','--statement','선택 변경')
        self.assertEqual({'work':'report','choice':'work','target':'next','recorded':True,'statement':'선택 변경'},
                         self.call('followup','report'))
        self.assertIn('후속 Work "회의 보고서" (next) · 계획',self.call('ordinary','list',machine=False))
        # Replacing either recorded plan invalidates the
        # association to its newer plan without losing the old decision.
        def replace(work,plan):
            return self.call('ordinary','plan',work,'--title','다른 범위','--goal','보강','--path',work+'.md',
                             '--check','검사','--replace-receipt',plan['receipt'])
        replace('next',target)
        replace('report',source)
        shown=self.call('followup','report',machine=False)
        self.assertIn('이전 계획에 남긴 선택',shown)
        self.assertIn('후속 Work "회의 보고서" (next) · 이전 계획',shown)
        self.assertNotIn('다른 범위',shown)
        self.assertIn('이전 계획에 대한 연결',self.call('candidate','list',machine=False))

    def test_followup_projection_refuses_changed_page_before_printing(self):
        from contextlib import redirect_stderr,redirect_stdout
        from io import StringIO
        from unittest.mock import patch
        from colvia.cli import main
        from colvia.planning import Planning
        self.plan()
        self.plan('second')
        self.call('followup','report','--choice','none','--statement','현재 결정')
        first=self.call('ordinary','list','--limit','1')
        self.assertEqual({'items','next'},set(first))
        self.assertEqual({'work','title','state','workspace','archived'},set(first['items'][0]))
        self.assertEqual({'root','offset'},set(first['next']))
        self.assertEqual('second',self.call('ordinary','list','--cursor',json.dumps(first['next']))['items'][0]['work'])
        lookup=Planning.followup
        out,err=StringIO(),StringIO()
        def edit_during_read(planning,*args,**kwargs):
            result=lookup(planning,*args,**kwargs)
            self.call('candidate','save','other','--title','다른 후보','--reason','상태 변경')
            return result
        with patch.object(Planning,'followup',edit_during_read),redirect_stdout(out),redirect_stderr(err):
            status=main(self.prefix[6:]+['ordinary','list','--limit','1'])
        self.assertEqual(2,status)
        self.assertEqual('목록을 읽는 동안 상태가 바뀌었습니다. 목록을 다시 열어 주세요.',out.getvalue().strip())
        self.assertEqual('',err.getvalue())


    def test_followup_detail_and_corrupt_relation_refuse_without_partial_output(self):
        from contextlib import redirect_stderr,redirect_stdout
        from io import StringIO
        from unittest.mock import patch
        from colvia.cli import main
        from colvia.codec import RecordError
        from colvia.planning import Planning
        self.plan()
        self.call('followup','report','--choice','none','--statement','확인')
        lookup=Planning.followup

        def advance_root(planning,*args,**kwargs):
            value=lookup(planning,*args,**kwargs)
            self.call('candidate','save','new','--title','후보','--reason','상태 변경')
            return value

        def invalid_relation(*args,**kwargs):
            raise RecordError('wrong-followup-target')

        cases=[
            (['followup','report'],advance_root,'후속 기록을 읽는 동안 상태가 바뀌었습니다.'),
            (['ordinary','view','report'],advance_root,'후속 기록을 읽는 동안 상태가 바뀌었습니다.'),
            (['ordinary','list'],invalid_relation,None),
        ]
        for args,resolve,message in cases:
            out,err=StringIO(),StringIO()
            with self.subTest(args=args),patch.object(Planning,'followup',resolve),redirect_stdout(out),redirect_stderr(err):
                status=main(self.prefix[6:]+args)
            self.assertEqual(2,status)
            if message is not None:self.assertIn(message,out.getvalue())
            self.assertNotIn('회의 보고서',out.getvalue())
            self.assertNotIn('등록된 항목이 없습니다',out.getvalue())
            self.assertEqual('',err.getvalue())

if __name__=='__main__':unittest.main()
