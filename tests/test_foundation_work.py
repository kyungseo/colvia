from pathlib import Path
import tempfile,unittest

from colvia.binding import Locator,ProjectBinding,WorkspaceRegistration,Topology
from colvia.bodies import body_bytes
from colvia.codec import RecordError,decode_envelope
from colvia.connection import Connections
from colvia.maps import map_get
from colvia.platforms.posix import location
from colvia.records import link
from colvia.storage.sqlite import GenerationStore
from colvia.work import WorkService,work_key
from colvia.workspace import LocalWorkspace
from test_foundation_binding import P,I,W


class WorkFixture:
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='ordinary-')
        self.root=Path(self.tmp.name)/'project';self.root.mkdir()
        self.store=GenerationStore.create(Path(self.tmp.name)/'state.sqlite3',project=P,instance=I,generation='g',active_check=lambda:None)
        self.locator=Locator(P,I,1,'a'*64,W);topology=Topology('plain',location(self.root))
        binding=ProjectBinding(self.locator,'plain',topology.root)
        Connections(self.store).connect(operation='connect',binding=binding,observed=topology,
            workspace=WorkspaceRegistration(W,topology.root,None),verify_topology=lambda:Topology('plain',location(self.root)))
        self.workspace=LocalWorkspace(self.store,self.root,W,locator_reader=lambda:self.locator)
        self.service=WorkService(self.store,self.workspace)
        (self.root/'source.csv').write_bytes(b'type,count\r\nrefund,5\r\n')
    def tearDown(self):self.store.close();self.tmp.cleanup()
    def plan(self,work='report',scope=('report.md',)):
        return self.service.plan(operation=work+'-plan',work=work,title='팀 회의 보고서',goal='문의 내용을 비교한다',scope=scope,
                                 checks=['원본 보존','집계 대조'],excludes=['우선순위 선택'])
    def start(self,work='report',scope=('report.md',)):
        planned=self.plan(work,scope)
        self.service.approve(operation=work+'-approve',work=work,receipt=planned['receipt'],statement='그 범위로 진행해')
        self.service.start(operation=work+'-start',work=work)
    def submit(self,work='report',operation=None):
        return self.service.submit(operation=operation or work+'-submit',work=work,summary='회의용 비교를 작성했습니다.',checks=[
            dict(name='원본 보존',status='passed',detail='원본 bytes가 같습니다.'),
            dict(name='집계 대조',status='passed',detail='유형별 합계를 대조했습니다.')])
    def result(self):
        head=decode_envelope(self.store.head(work_key('report')),self.store.load(self.store.head(work_key('report'))))
        result_ref=link(head,'result');return decode_envelope(result_ref,self.store.load(result_ref))


class WorkTests(WorkFixture,unittest.TestCase):
    def test_one_approval_submission_prepares_review_and_one_acceptance(self):
        self.start();(self.root/'report.md').write_bytes(b'# Report\ncomparison\n')
        review=self.submit();self.assertTrue(review['current_matches']);self.assertEqual('review',review['state'])
        before=(self.root/'report.md').read_bytes()
        final=self.service.accept(operation='accept',work='report',receipt=review['receipt'],statement='이대로 마무리하자')
        self.assertEqual('completed',final['state']);self.assertEqual(before,(self.root/'report.md').read_bytes())
        old=self.store.root().ref
        self.service.accept(operation='duplicate-accept',work='report',receipt=review['receipt'],statement='마무리')
        self.assertEqual(old,self.store.root().ref)

    def test_check_name_mismatch_preserves_head_and_corrected_submit_stays_first_revision(self):
        variants={'missing':['원본 보존'],'extra':['원본 보존','집계 대조','추가 검사'],
                  'duplicate':['원본 보존','집계 대조','원본 보존']}
        for label,names in variants.items():
            with self.subTest(label=label):
                self.start(label,(label+'.md',));(self.root/(label+'.md')).write_text('report')
                before=self.store.root().ref;original=(self.root/'source.csv').read_bytes()
                with self.assertRaisesRegex(RecordError,'check-report-mismatch'):
                    self.service.submit(operation=label+'-refused',work=label,summary='검토용',checks=[
                        dict(name=name,status='unavailable',detail='미실행') for name in names])
                self.assertEqual(before,self.store.root().ref)
                self.assertEqual('active',self.service.view(label)['state'])
                self.assertEqual(original,(self.root/'source.csv').read_bytes())
                self.assertEqual('report',(self.root/(label+'.md')).read_text())
                review=self.submit(label);self.assertEqual('review',review['state'])
                head=decode_envelope(self.store.head(work_key(label)),self.store.load(self.store.head(work_key(label))))
                result=decode_envelope(link(head,'result'),self.store.load(link(head,'result')))
                self.assertEqual(1,result.payload['revision'])

    def test_plan_refuses_duplicate_check_names(self):
        before=self.store.root().ref
        with self.assertRaisesRegex(RecordError,'invalid-plan-criteria'):
            self.service.plan(operation='duplicate-plan',work='report',title='보고서',goal='비교',scope=['report.md'],
                              checks=['대조','대조'])
        self.assertEqual(before,self.store.root().ref)

    def test_outside_scope_change_never_enters_submission(self):
        self.start();(self.root/'report.md').write_text('report');(self.root/'source.csv').write_text('changed')
        before=self.store.root().ref
        with self.assertRaisesRegex(RecordError,'outside-scope-change'):self.submit()
        self.assertEqual(before,self.store.root().ref);self.assertEqual('active',self.service.view('report')['state'])

    def test_changed_file_after_review_refuses_same_receipt(self):
        self.start();(self.root/'report.md').write_text('reviewed');review=self.submit()
        (self.root/'report.md').write_text('different')
        self.assertFalse(self.service.review('report')['current_matches'])
        with self.assertRaisesRegex(RecordError,'reviewed-files-changed'):
            self.service.accept(operation='accept',work='report',receipt=review['receipt'],statement='수락')
        self.assertEqual('review',self.service.view('report')['state'])

    def test_rework_retains_old_body_and_old_receipt_is_stale(self):
        (self.root/'report.md').write_bytes(b'original\r\n\x00\xff');self.start()
        (self.root/'report.md').write_bytes(b'first result\r\n');review=self.submit();first=self.result()
        body=map_get(link(first,'after'),'report.md',self.store.load)
        self.service.revise(operation='revise',work='report',receipt=review['receipt'],statement='표현을 고쳐줘')
        (self.root/'report.md').write_bytes(b'second result\n');second=self.submit(operation='submit-again')
        self.assertEqual(b'first result\r\n',b''.join(body_bytes(body,self.store.load)))
        with self.assertRaisesRegex(RecordError,'stale-result-receipt'):
            self.service.accept(operation='stale',work='report',receipt=review['receipt'],statement='수락')
        self.assertEqual('completed',self.service.accept(operation='current',work='report',receipt=second['receipt'],statement='수락')['state'])

    def test_new_service_resumes_exact_pending_result(self):
        self.start();(self.root/'report.md').write_text('report');review=self.submit()
        fresh=WorkService(self.store,LocalWorkspace(self.store,self.root,W,locator_reader=lambda:self.locator))
        self.assertEqual(review,fresh.review('report'))
        self.assertEqual('completed',fresh.accept(operation='new-session-accept',work='report',receipt=review['receipt'],statement='수락')['state'])

    def test_two_pending_works_keep_separate_decisions(self):
        self.start('one',('one.md',));(self.root/'one.md').write_text('one');one=self.submit('one')
        self.start('two',('two.md',));(self.root/'two.md').write_text('two');two=self.submit('two')
        self.assertEqual('review',self.service.view('one')['state'])
        with self.assertRaisesRegex(RecordError,'stale-result-receipt'):
            self.service.accept(operation='wrong',work='two',receipt=one['receipt'],statement='수락')
        self.service.accept(operation='two-accept',work='two',receipt=two['receipt'],statement='수락')
        self.assertEqual('review',self.service.view('one')['state'])

    def test_plan_drift_and_missing_approval_stop_before_work(self):
        plan=self.plan()
        with self.assertRaisesRegex(RecordError,'plan-approval-required'):self.service.start(operation='early',work='report')
        self.service.approve(operation='approve',work='report',receipt=plan['receipt'],statement='진행')
        (self.root/'source.csv').write_bytes(b'changed before starting')
        with self.assertRaisesRegex(RecordError,'plan-baseline-changed'):self.service.start(operation='late',work='report')

    def test_archive_keeps_decision_body_and_current_file_disagreement(self):
        self.start();(self.root/'report.md').write_text('reviewed');review=self.submit()
        self.service.accept(operation='accept',work='report',receipt=review['receipt'],statement='수락')
        result=self.result();body=map_get(link(result,'after'),'report.md',self.store.load)
        self.service.archive(operation='archive',work='report',archived=True)
        (self.root/'report.md').write_text('later edit')
        view=self.service.view('report');self.assertTrue(view['archived']);self.assertFalse(view['current_matches'])
        self.assertEqual(b'reviewed',b''.join(body_bytes(body,self.store.load)))
        self.assertEqual('completed',view['state'])

    def test_historical_body_survives_rework_archive_and_current_file_removal(self):
        (self.root/'report.md').write_text('original');self.start()
        (self.root/'report.md').write_text('first');review=self.submit()
        self.service.revise(operation='revise',work='report',receipt=review['receipt'],statement='다시 고쳐줘')
        (self.root/'report.md').write_text('second');review=self.submit(operation='second')
        self.service.accept(operation='accept',work='report',receipt=review['receipt'],statement='마무리')
        self.service.archive(operation='archive',work='report',archived=True)
        (self.root/'report.md').unlink()
        old=self.service.result_content('report','report.md',revision=1)
        self.assertEqual('original',old['before']['text']);self.assertEqual('first',old['after']['text'])
        self.assertEqual('second',self.service.result_content('report','report.md')['after']['text'])
        self.assertEqual('too-large',self.service.result_content('report','report.md',text_limit=2)['after']['display'])

    def test_binary_rename_delete_mode_and_exact_before_after(self):
        (self.root/'old.bin').write_bytes(b'\x00\xfforiginal');self.start(scope=('old.bin','new.bin'))
        (self.root/'old.bin').rename(self.root/'new.bin');(self.root/'new.bin').chmod(0o755)
        review=self.submit();self.assertEqual(['new.bin','old.bin'],review['files'])
        old=self.service.result_content('report','old.bin');new=self.service.result_content('report','new.bin')
        self.assertEqual('binary',old['before']['display']);self.assertFalse(old['after']['exists'])
        self.assertFalse(new['before']['exists']);self.assertEqual(old['before']['sha256'],new['after']['sha256'])
        self.service.accept(operation='accept',work='report',receipt=review['receipt'],statement='마무리')

    def test_managed_paths_and_opaque_scope_refuse(self):
        with self.assertRaisesRegex(RecordError,'managed-path-not-editable'):self.plan(scope=('.git/config',))
        (self.root/'link').symlink_to('source.csv')
        with self.assertRaisesRegex(RecordError,'opaque-edit-not-supported'):self.plan(scope=('link',))

if __name__=='__main__':unittest.main()
