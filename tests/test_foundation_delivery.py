"""Real authority/submission tests, with a named filesystem-lock double.

EffectsDouble checks no process or OS isolation capability; native lock mechanics
are covered separately. No notification or external runner is invoked here.
"""
import time,unittest
from contextlib import nullcontext
from unittest.mock import patch
from colvia.codec import RecordError
from colvia.effects import PENDING
from colvia.records import link
from colvia.work import work_key
from colvia.delivery.service import DeliveryService,key,OUTSTANDING,notice_key
from test_foundation_work import WorkFixture

class EffectsDouble:
    def __init__(self,root):self.root=root;self.locked=True
    def _root(self):return nullcontext()
    def _authority(self):return nullcontext()

class DeliveryTests(WorkFixture,unittest.TestCase):
    def ready(self,*,action='submit',delivery='handoff',notice=False):
        self.start();(self.root/'report.md').write_text('prepared report')
        self.delivery=DeliveryService(self.service);self.effects=EffectsDouble(self.root)
        options=dict(summary='Ready for review',checks=[dict(name=name,status='passed',detail='Synthetic check') for name in ('원본 보존','집계 대조')]) if action=='submit' else {}
        prepared=self.delivery.prepare(operation='prepare-'+delivery,delivery=delivery,work='report',action=action,
            deadline_ns=time.time_ns()+600*10**9,receiver={'id':'synthetic-receiver','version':1} if notice else None,**options)
        self.delivery.start(operation='start-'+delivery,delivery=delivery,receipt=prepared['receipt'],statement='Do this step and requested notification')
        return prepared
    def claim(self):return self.delivery.claim(operation='claim',delivery='handoff',effects=self.effects)
    def test_preparation_and_claim_do_not_submit_or_accept(self):
        self.ready();self.assertEqual('active',self.service.view('report')['state'])
        self.assertIsNone(self.store.head(PENDING));self.claim()
        self.assertIsNotNone(self.store.head(PENDING));self.assertEqual('active',self.service.view('report')['state'])
    def test_submission_and_original_notice_are_one_exact_publication(self):
        self.ready(notice=True);self.claim();before=self.store.root().sequence
        result=self.delivery.submit(operation='publish',delivery='handoff',effects=self.effects)
        self.assertEqual('finished',result['state']);self.assertEqual(before+1,self.store.root().sequence)
        self.assertEqual('review',self.service.view('report')['state']);self.assertIsNone(self.store.head(PENDING));self.assertIsNone(self.store.head(OUTSTANDING))
        state,request=self.delivery.read('handoff');outcome=self.delivery.obj(link(state,'outcome'))
        self.assertEqual(self.store.head(work_key('report')),link(outcome,'head'))
        event=self.delivery.obj(self.store.head(notice_key('handoff')));self.assertEqual(outcome.ref,link(event,'outcome'))
        self.assertEqual(self.store.instance,event.payload['instance']);self.assertFalse(result['accepted'])
    def test_after_prepare_drift_preserves_active_owner_and_unsubmitted_work(self):
        self.ready();self.claim();owner=self.store.head(PENDING);(self.root/'report.md').write_text('later change')
        with self.assertRaisesRegex(RecordError,'prepared-files-changed'):self.delivery.submit(operation='publish',delivery='handoff',effects=self.effects)
        self.assertEqual(owner,self.store.head(PENDING));self.assertEqual('active',self.service.view('report')['state'])
        self.assertIsNone(self.store.head(notice_key('handoff')))
    def test_outside_scope_change_refuses_at_preparation(self):
        self.start();(self.root/'report.md').write_text('report');(self.root/'source.csv').write_text('changed')
        delivery=DeliveryService(self.service)
        with self.assertRaisesRegex(RecordError,'outside-scope-change'):delivery.prepare(operation='bad',delivery='bad',work='report',action='submit',
            deadline_ns=time.time_ns()+60*10**9,summary='bad',checks=[])
        self.assertEqual('active',self.service.view('report')['state'])
    def test_ordinary_submit_cannot_bypass_a_claimed_delivery(self):
        self.ready();self.claim()
        with self.assertRaisesRegex(RecordError,'external-effect-pending'):self.submit(operation='ordinary-bypass')
        self.assertEqual('active',self.service.view('report')['state'])
    def test_failed_final_publication_does_not_separate_result_from_delivery(self):
        self.ready(notice=True);self.claim();before=self.store.root().ref
        with patch.object(self.store,'commit_heads',side_effect=OSError('synthetic publication failure')):
            with self.assertRaises(OSError):self.delivery.submit(operation='publish',delivery='handoff',effects=self.effects)
        self.assertEqual(before,self.store.root().ref);self.assertEqual('active',self.service.view('report')['state'])
        self.assertEqual('active',self.delivery.status('handoff')['state']);self.assertIsNone(self.store.head(notice_key('handoff')))
    def test_inspect_takes_no_effect_ownership_and_preserves_exact_snapshot(self):
        self.ready(action='inspect');self.assertIsNone(self.store.head(PENDING))
        before=self.store.head(work_key('report'));value=self.delivery.inspect(operation='inspect',delivery='handoff')
        self.assertEqual('finished',value['state']);self.assertIsNone(self.store.head(PENDING))
        state,_=self.delivery.read('handoff');self.assertEqual(before,link(self.delivery.obj(link(state,'outcome')),'head'))
        self.assertEqual('active',self.service.view('report')['state'])
    def test_cancel_started_request_does_not_clear_ownership(self):
        self.ready();self.claim();owner=self.store.head(PENDING)
        value=self.delivery.cancel(operation='cancel',delivery='handoff',statement='Stop this attempt')
        self.assertTrue(value['cancel_requested']);self.assertEqual(owner,self.store.head(PENDING))
        with self.assertRaisesRegex(RecordError,'delivery-cancelled'):self.delivery.submit(operation='late',delivery='handoff',effects=self.effects)
        self.assertEqual('active',self.service.view('report')['state'])
    def test_claim_requires_lock_and_second_claim_is_not_a_retry(self):
        self.ready();self.effects.locked=False
        with self.assertRaisesRegex(RecordError,'lock-required'):self.claim()
        self.effects.locked=True;self.claim()
        with self.assertRaisesRegex(RecordError,'not-claimable'):self.delivery.claim(operation='second',delivery='handoff',effects=self.effects)
    def test_single_outstanding_request_and_stale_receipt(self):
        self.ready();p=self.delivery.prepare(operation='prepare-other',delivery='other',work='report',action='inspect',deadline_ns=time.time_ns()+60*10**9)
        with self.assertRaisesRegex(RecordError,'stale-receipt'):self.delivery.start(operation='wrong',delivery='other',receipt='wrong',statement='Start')
        with self.assertRaises(RecordError):self.delivery.start(operation='other',delivery='other',receipt=p['receipt'],statement='Start')
        self.assertIsNone(self.store.head(key('other')))

    def test_cancel_claimed_but_unstarted_submit_keeps_files_and_releases(self):
        self.ready();self.claim();before=(self.root/'report.md').read_bytes()
        self.delivery.cancel(operation='cancel',delivery='handoff',statement='Stop')
        self.delivery.cancel_unstarted(operation='close',delivery='handoff',effects=self.effects)
        self.assertIsNone(self.store.head(PENDING));self.assertEqual(before,(self.root/'report.md').read_bytes())
        self.assertEqual('active',self.service.view('report')['state'])
