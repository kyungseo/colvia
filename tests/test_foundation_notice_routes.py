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
    def test_execution_history_is_read_through_the_native_detail_route(self):
        from colvia.execution.journal import prepared_key
        from test_foundation_execution_store import JournalFixture
        from test_foundation_execution_history import Chain

        import hashlib
        first=self.emit()
        path=self.routes.root/(first+'.json')
        digest=hashlib.sha256(path.read_bytes()).hexdigest()
        with patch.object(WorkService,'view',side_effect=AssertionError('live read during original')):
            original=self.routes.details(first,self.entry,original_only=True,route_digest=digest)
        self.assertEqual('Ready for review',original['summary'])
        JournalFixture.initialize_execution_fixture(self)
        grant = JournalFixture.prepare(self)
        key = 'execution-notice'
        preview = self.delivery.prepare(
            operation='queue-inspection', delivery=key, work='synthetic-work', action='execute',
            deadline_ns=self.contract['scope']['limits']['expires_wall_ns'] + 10**9,
            grant=self.store.head(prepared_key('run')), receiver={'id': 'synthetic-receiver', 'version': 1})
        self.delivery.start(operation='authorize-run', delivery=key, receipt=preview['receipt'], statement='Run fixture')
        self.delivery.claim(operation='claim-run', delivery=key, effects=self.effects)
        from colvia.effects import PENDING
        self.journal.start(operation='begin-child', run='run', receipt=grant['receipt'],
                           statement='Exercise execution history', parent=self.store.head(PENDING))
        chain = Chain(self.contract)
        chain.terminal('revoked-before-launch')
        JournalFixture.publish(self, chain)
        self.delivery.finish_execution(operation='finish-child', delivery=key, run='run', effects=self.effects)
        self.notices.emit(operation='show-execution', delivery=key, port=RoutedReceiver(self.routes, self.receiver))
        before = self.store.root().ref
        result = self.routes.details(self.receiver.calls[-1], self.entry)
        self.assertEqual(before, self.store.root().ref)
        self.assertEqual('executed', result['original']['kind'])
        self.assertEqual('revoked-before-launch', result['original']['status'])
        self.assertFalse(result['original']['work_submitted'])
        other=self.routes.root/(self.receiver.calls[-1]+'.json')
        path.write_bytes(other.read_bytes())
        for original_only in (True,False):
            with self.assertRaisesRegex(RecordError,'notice-route-changed'):
                self.routes.details(first,self.entry,original_only=original_only,route_digest=digest)
        self.assertFalse(result['click_accepts'])

    def test_emitted_digest_identifies_the_route_saved_for_the_click(self):
        import hashlib
        class BoundReceiver(ReceiverDouble):
            def emit_bound(self, event, digest):
                self.calls.append((event, digest))
                return 'emitted'
        port = BoundReceiver()
        self.notices.emit(operation='send-bound', delivery='handoff', port=RoutedReceiver(self.routes,port))
        event, digest = port.calls[0]
        self.assertEqual(hashlib.sha256((self.routes.root/(event+'.json')).read_bytes()).hexdigest(), digest)
        original = self.routes.details(event,self.entry,original_only=True,route_digest=digest)
        self.assertEqual('Ready for review', original['summary'])

    def test_changed_stored_summary_is_refused_before_first_paint(self):
        import hashlib
        event = self.emit()
        digest = hashlib.sha256((self.routes.root/(event+'.json')).read_bytes()).hexdigest()
        rows = self.store.db.execute("SELECT digest,data FROM objects WHERE instr(data,?)>0", (b'Ready for review',)).fetchall()
        self.assertTrue(rows)
        self.store.db.execute('DROP TRIGGER object_bytes_immutable')
        for key, raw in rows:
            self.store.db.execute('UPDATE objects SET data=? WHERE digest=?',
                                  (raw.replace(b'Ready for review', b'Wrong other work'), key))
        self.store.db.commit()
        with self.assertRaises(RecordError):
            self.routes.details(event,self.entry,original_only=True,route_digest=digest)

    def test_record_snapshot_lifetime_and_readonly_boundary(self):
        ref = self.store.root().ref
        with self.assertRaisesRegex(RecordError, 'record-snapshot-readonly-required'):
            with self.store.read_snapshot():
                self.fail('Writable handle admitted')
        reader = self.authority.store(readonly=True)
        try:
            with reader.read_snapshot() as records:
                self.assertEqual(self.store.project, records.project)
                self.assertTrue(records.load(ref))
                with self.assertRaisesRegex(RecordError, 'record-snapshot-already-open'):
                    with reader.read_snapshot():
                        self.fail('Nested transaction admitted')
                self.assertTrue(reader.db.in_transaction)
            self.assertFalse(reader.db.in_transaction)
            with self.assertRaisesRegex(RecordError, 'record-snapshot-closed'):
                records.load(ref)
            with self.assertRaisesRegex(RecordError, 'record-snapshot-closed'):
                records.head('work:report')
        finally:
            reader.close()

    def test_concurrent_writer_publishes_after_the_read_snapshot(self):
        import threading
        start = threading.Event()
        done = threading.Event()
        errors = []
        ref = self.store.head('work:report')
        def publish():
            try:
                start.set()
                writer = self.authority.store()
                try:
                    writer.commit_heads(operation='concurrent-result', expected={'probe': None},
                                        changes={'probe': ref}, validate=lambda view: view(ref))
                finally:
                    writer.close()
            except Exception as error:
                errors.append(error)
            finally:
                done.set()
        reader = self.authority.store(readonly=True)
        worker = threading.Thread(target=publish)
        try:
            with reader.read_snapshot() as snapshot:
                self.assertIsNone(snapshot.head('probe'))
                worker.start()
                self.assertTrue(start.wait(2))
                self.assertFalse(done.wait(.08))
                self.assertTrue(worker.is_alive())
                self.assertIsNone(snapshot.head('probe'))
            self.assertTrue(done.wait(5))
            self.assertEqual([], errors)
            self.assertEqual(ref, reader.head('probe'))
        finally:
            if worker.ident is not None:
                worker.join(5)
            reader.close()

    def test_current_file_read_starts_after_snapshot_and_sees_new_decision(self):
        event = self.emit()
        original = WorkService.view
        submitted_title = self.service.view('report')['title']
        updated = False
        def accept_before_current_view(service, work):
            nonlocal updated
            self.assertFalse(service.store.db.in_transaction)
            if not updated:
                updated = True
                review = self.service.review('report')
                self.service.accept(operation='later-decision', work='report',
                                    receipt=review['receipt'], statement='Accept fixture')
            return original(service, work)
        with patch.object(WorkService, 'view', accept_before_current_view):
            result = self.routes.details(event, self.entry)
        self.assertTrue(updated)
        self.assertEqual(submitted_title, result['original']['title'])
        self.assertEqual('review', result['original']['state'])
        self.assertEqual('completed', result['current']['state'])
        self.assertFalse(result['click_accepts'])

    def test_retirement_during_live_read_refuses_the_entire_result(self):
        event = self.emit()
        root = self.store.root().ref
        def retire_during_view(service, work):
            self.assertFalse(service.store.db.in_transaction)
            self.store.quiesce('retire-test', root, lambda _: None)
            self.store.retire('retire-test', root)
            raise RecordError('workspace-access-unavailable')
        with patch.object(WorkService, 'view', retire_during_view):
            with self.assertRaisesRegex(RecordError, 'generation-retired'):
                self.routes.details(event, self.entry)

    def test_receiver_mismatch_and_runtime_tamper_refuse_detail(self):
        event = self.emit()
        path = self.routes.root / (event + '.json')
        raw = path.read_bytes()
        route = self.routes.read(event)
        route['receiver']['id'] = 'another-receiver'
        path.write_bytes(canonical_bytes(route))
        with self.assertRaisesRegex(RecordError, 'notice-receiver-mismatch'):
            self.routes.details(event, self.entry)
        path.write_bytes(raw)
        entry_point = self.manager.root / 'slots' / self.one['slot'] / 'python'
        original = entry_point.read_bytes()
        self.assertTrue(original)
        entry_point.write_bytes(bytes([original[0] ^ 1]) + original[1:])
        with self.assertRaisesRegex(RecordError, 'slot-inventory-mismatch'):
            self.routes.details(event, self.entry)

    def test_route_failure_after_emission_intent_never_calls_receiver_or_retries(self):
        with patch.object(self.routes,'persist',side_effect=OSError('synthetic disk failure')):
            result=self.notices.emit(operation='send',delivery='handoff',port=RoutedReceiver(self.routes,self.receiver))
        self.assertEqual('unknown',result['notification']);self.assertEqual([],self.receiver.calls)
        with self.assertRaisesRegex(RecordError,'already-attempted'):self.emit()
    def test_invalid_identifier_cannot_open_arbitrary_path(self):
        for event in ('../home','A'*32,'a'*31,'a'*33):
            with self.assertRaisesRegex(RecordError,'event-id-invalid'):self.routes.read(event)

if __name__=='__main__':unittest.main()
