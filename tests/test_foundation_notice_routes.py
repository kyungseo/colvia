"""Real synthetic manager/store routing; receiver never invokes the OS."""
import unittest,uuid
from unittest.mock import patch
from colvia.codec import RecordError,canonical_bytes
from colvia.notice_routes import NoticeRoutes,RoutedReceiver,detail_text
from colvia.delivery.notices import Notices
from colvia.delivery.service import notice_key
from colvia.work import WorkService
from colvia.managed_entry import ManagedEntry
from test_foundation_managed_entry import ManagedEntryTests
from test_foundation_work import WorkFixture
from test_foundation_delivery import DeliveryTests

class ReceiverDouble:
    def __init__(self):self.calls=[]
    def check(self,identity):
        if identity!={'id':'synthetic-receiver','version':1}:raise RecordError('receiver-not-qualified')
    def emit(self,event):self.calls.append(event);return 'emitted'

class NoticeRouteTests(unittest.TestCase):
    slot=ManagedEntryTests.slot
    plan=WorkFixture.plan;start=WorkFixture.start
    ready=DeliveryTests.ready;claim=DeliveryTests.claim
    def setUp(self):
        ManagedEntryTests.setUp(self)
        _,self.store,self.workspace=self.entry.workspace(self.root,readonly=False)
        self.service=WorkService(self.store,self.workspace)
        (self.root/'source.csv').write_text('type,count\nrefund,5\n')
        self.ready(notice=True);self.claim();self.delivery.submit(operation='publish',delivery='handoff',effects=self.effects)
        self.notices=Notices(self.delivery);self.routes=NoticeRoutes(self.home);self.receiver=ReceiverDouble()
    def tearDown(self):self.store.close();ManagedEntryTests.tearDown(self)
    def emit(self):
        self.notices.emit(operation='send',delivery='handoff',port=RoutedReceiver(self.routes,self.receiver))
        return self.receiver.calls[0]
    def test_opaque_event_resolves_original_and_current_without_acceptance(self):
        event=self.emit();self.assertRegex(event,'^[0-9a-f]{32}$')
        before=self.store.root().ref;details=self.routes.details(event,self.entry)
        self.assertEqual(before,self.store.root().ref);self.assertEqual('review',details['current']['state'])
        self.assertEqual(['report.md'],details['original']['files']);self.assertFalse(details['click_accepts'])
        self.assertNotIn('report.md',(self.routes.root/(event+'.json')).read_text())
        review=self.service.review('report');self.service.accept(operation='accepted',work='report',receipt=review['receipt'],statement='마무리')
        details=self.routes.details(event,self.entry)
        self.assertEqual('review',details['original']['state']);self.assertEqual('completed',details['current']['state'])
        self.assertIn('결과 수락 완료',detail_text(details))
    def test_missing_connection_preserves_original_and_has_reconnect_guidance(self):
        event=self.emit();(self.root/'.colvia-link.json').unlink()
        details=self.routes.details(event,self.entry)
        self.assertEqual('Ready for review',details['original']['summary']);self.assertFalse(details['workspace_connected'])
        self.assertIsNone(details['current']['current_matches']);self.assertIn('연결을 확인',detail_text(details))
    def test_foreign_instance_and_event_reference_refuse(self):
        event=self.emit();path=self.routes.root/(event+'.json');value=self.routes.read(event)
        value['instance']=str(uuid.uuid4());path.write_bytes(canonical_bytes(value))
        with self.assertRaisesRegex(RecordError,'notice-instance-changed'):self.routes.details(event,self.entry)
        value['instance']=self.store.instance;value['event']['sha256']='0'*64;path.write_bytes(canonical_bytes(value))
        with self.assertRaises(RecordError):self.routes.details(event,self.entry)
    def test_route_failure_after_emission_intent_never_calls_receiver_or_retries(self):
        with patch.object(self.routes,'persist',side_effect=OSError('synthetic disk failure')):
            result=self.notices.emit(operation='send',delivery='handoff',port=RoutedReceiver(self.routes,self.receiver))
        self.assertEqual('unknown',result['notification']);self.assertEqual([],self.receiver.calls)
        with self.assertRaisesRegex(RecordError,'already-attempted'):self.emit()
    def test_invalid_identifier_cannot_open_arbitrary_path(self):
        for event in ('../home','A'*32,'a'*31,'a'*33):
            with self.assertRaisesRegex(RecordError,'event-id-invalid'):self.routes.read(event)

if __name__=='__main__':unittest.main()
