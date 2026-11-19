"""Recording/failing ports only: no OS notification is sent."""
import unittest
from unittest.mock import patch
from colvia.codec import RecordError
from colvia.records import link
from colvia.delivery.notices import Notices,emission_key
from colvia.delivery.service import notice_key
from test_foundation_work import WorkFixture
import test_foundation_delivery as delivery_tests

class RecordingPort:
    def __init__(self,*,fail=False):self.calls=[];self.fail=fail
    def check(self,receiver):
        if receiver!={'id':'synthetic-receiver','version':1}:raise RecordError('receiver-unavailable')
    def emit(self,route):
        self.calls.append(route)
        if self.fail:raise OSError('synthetic unknown acknowledgement')
        return 'emitted'

class NoticeTests(WorkFixture,unittest.TestCase):
    ready=delivery_tests.DeliveryTests.ready
    claim=delivery_tests.DeliveryTests.claim
    def finish(self):
        self.ready(notice=True);self.claim();self.delivery.submit(operation='publish',delivery='handoff',effects=self.effects)
        self.notices=Notices(self.delivery);self.event=self.store.head(notice_key('handoff'))
    def details(self,**kwargs):
        return self.notices.details('handoff',**dict(project=self.store.project,instance=self.store.instance,event_ref=self.event,**kwargs))
    def test_original_submission_stays_distinct_from_later_acceptance(self):
        self.finish();review=self.service.review('report')
        self.service.accept(operation='accept',work='report',receipt=review['receipt'],statement='Accept this report')
        details=self.details();self.assertEqual('review',details['original']['state']);self.assertEqual('completed',details['current']['state'])
        self.assertFalse(details['click_accepts']);self.assertEqual(['report.md'],details['original']['files'])
    def test_old_notification_after_pause_and_discard_is_read_only(self):
        from colvia import work_lifecycle
        self.finish()
        for action,state in [('pause','paused'),('discard','discarded')]:
            args=(self.service,'report',action,'new decision','','')
            receipt=work_lifecycle.proposal(*args)[0]['receipt']
            work_lifecycle.apply(*args,receipt,action)
            root=self.store.root().ref
            details=self.details()
            self.assertFalse(details['click_accepts'])
            self.assertEqual('review',details['original']['state'])
            self.assertEqual(state,details['current']['state'])
            self.assertEqual(root,self.store.root().ref)

    def test_route_cannot_alias_same_label_in_another_project_instance(self):
        self.finish()
        for project,instance in (('0'*32,self.store.instance),(self.store.project,'0'*32)):
            with self.assertRaisesRegex(RecordError,'route-mismatch'):self.notices.details('handoff',project=project,instance=instance,event_ref=self.event)
    def test_emission_once_keeps_result_and_has_no_document_content(self):
        self.finish();port=RecordingPort();value=self.notices.emit(operation='notice',delivery='handoff',port=port)
        self.assertEqual('emitted',value['notification']);self.assertEqual(1,len(port.calls));self.assertNotIn('summary',port.calls[0])
        with self.assertRaisesRegex(RecordError,'already-attempted'):self.notices.emit(operation='again',delivery='handoff',port=port)
        self.assertEqual(1,len(port.calls));self.assertEqual('review',self.service.view('report')['state'])
    def test_unknown_emission_never_resends_or_rolls_back_submission(self):
        self.finish();port=RecordingPort(fail=True);value=self.notices.emit(operation='notice',delivery='handoff',port=port)
        self.assertEqual('unknown',value['notification']);self.assertEqual('review',self.service.view('report')['state'])
        with self.assertRaisesRegex(RecordError,'already-attempted'):self.notices.emit(operation='retry',delivery='handoff',port=port)
        self.assertEqual(1,len(port.calls))
    def test_lost_intent_ack_means_no_emitter_call(self):
        self.finish();port=RecordingPort();commit=self.store.commit_heads
        def lose(**kwargs):
            result=commit(**kwargs)
            if kwargs['operation'].endswith('-intent'):raise OSError('synthetic lost ack')
            return result
        with patch.object(self.store,'commit_heads',side_effect=lose),self.assertRaises(OSError):self.notices.emit(operation='notice',delivery='handoff',port=port)
        self.assertEqual([],port.calls);state=self.delivery.obj(self.store.head(emission_key('handoff')));self.assertEqual('intent',state.payload['phase'])
        with self.assertRaisesRegex(RecordError,'already-attempted'):self.notices.emit(operation='again',delivery='handoff',port=port)
    def test_detached_workspace_keeps_original_result_but_changes_guidance(self):
        self.finish()
        with patch.object(self.service.workspace,'verify',side_effect=RecordError('detached')):details=self.details()
        self.assertFalse(details['workspace_connected']);self.assertEqual('reconnect_project',details['next_action'])
        self.assertEqual('review',details['original']['state'])
