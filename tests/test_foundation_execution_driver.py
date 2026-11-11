"""Live driver ownership with durable synthetic records and no OS/model process."""
import unittest
from contextlib import contextmanager,nullcontext
from types import SimpleNamespace
from unittest.mock import patch
from colvia.codec import RecordError
from colvia.effects import PENDING
from colvia.execution.driver import DocumentExecution
from colvia.execution.journal import prepared_key
from test_foundation_execution_store import JournalFixture
from test_foundation_execution_supervisor import Launch,Policy,Channel
import test_foundation_execution_supervisor as supervisor_fixture
from test_foundation_execution_callbacks import NativeDouble
from test_foundation_execution_worker import ProcessDouble

class Held:
    def __init__(self,root=None):self.locked=False;self.root=root;self.checks=0
    @contextmanager
    def hold(self):
        if self.locked:raise AssertionError('unexpected reentrant source fixture')
        self.locked=True;self.checks+=1
        try:yield
        finally:self.locked=False
    def exclusion(self,**kwargs):return self.hold()
    def _root(self):return nullcontext()
    def _authority(self):return nullcontext()

class DriverTests(JournalFixture,unittest.TestCase):
    def driver(self,*,cancel=False):
        fixture=self;self.lease=Held();self.effects=Held(self.root);self.processes=ProcessDouble()
        backend=NativeDouble();backend.journal=self.journal
        class Session:
            failed=False;thread=None;turn=None
            def __init__(self,gate,*a,**k):fixture.gate=gate
            def run(self,controller):
                fixture.assertTrue(fixture.lease.locked and fixture.effects.locked)
                supervisor_fixture.SupervisorTests.complete_document(fixture)
                if cancel:fixture.journal.cancel(operation='cancel',run='run',reason='cancelled')
                return 'completed'
        class Adapter:
            def qualify(self):fixture.assertTrue(fixture.lease.locked)
            def material(self,contract,request):
                return dict(bodies=fixture.bodymap,objects=fixture.objects,import_id='body-import')
            def ports(self,grant):
                fixture.assertTrue(fixture.effects.locked)
                return dict(backend=backend,launch=Launch(),policy=Policy(),runtime_processes=fixture.processes,
                    worker_processes=ProcessDouble(),channel_factory=Channel,session_factory=Session,worker_exchange=lambda *a,**k:None)
        self.adapter=Adapter();self.controller=DocumentExecution(self.journal,lease=self.lease,effects=self.effects,adapter=self.adapter)
        prepared=self.controller.prepare(operation='prepare',run='run',contract=self.contract,request=self.request)
        self.receipt=prepared['receipt'];return self.controller
    def start_driver(self):return self.controller.start(operation='start',run='run',receipt=self.receipt,statement='Run this exact grant')
    def test_preparation_and_start_hold_both_locks_until_terminal(self):
        self.driver();value=self.start_driver()
        self.assertEqual('completed',value['status']);self.assertFalse(value['accepted']);self.assertIsNone(self.store.head(PENDING))
        self.assertFalse(self.lease.locked or self.effects.locked)
        with self.assertRaisesRegex(RecordError,'live-restore-refused'):self.start_driver()
        self.assertEqual(1,self.processes.launches)
    def test_unqualified_or_stale_runtime_refuses_before_claim(self):
        self.driver();before=self.store.root().ref
        with patch.object(self.adapter,'qualify',side_effect=RecordError('unqualified')),self.assertRaises(RecordError):self.start_driver()
        self.assertEqual(before,self.store.root().ref);self.assertIsNone(self.store.head(PENDING));self.assertEqual(0,self.processes.launches)
    def test_native_preflight_failure_has_no_claim_or_process(self):
        self.driver();before=self.store.root().ref
        with patch.object(self.adapter,'ports',side_effect=RecordError('drift')),self.assertRaises(RecordError):self.start_driver()
        self.assertEqual(before,self.store.root().ref);self.assertEqual(0,self.processes.launches)
    def test_lost_start_ack_does_not_run_or_repeat(self):
        self.driver();start=self.journal.start
        def lose(**kw):start(**kw);raise OSError('lost start ack')
        with patch.object(self.journal,'start',side_effect=lose),self.assertRaises(OSError):self.start_driver()
        self.assertEqual(0,self.processes.launches);self.assertIsNotNone(self.store.head(PENDING))
        with self.assertRaisesRegex(RecordError,'live-restore-refused'):self.start_driver()
    def test_cancel_after_write_retains_effect_without_acceptance(self):
        self.driver(cancel=True);value=self.start_driver()
        self.assertEqual('interrupted',value['status']);self.assertEqual('applied',value['document_write_effect']);self.assertFalse(value['accepted'])
    def test_delivery_uses_approved_grant_then_releases_parent(self):
        from colvia.delivery.service import DeliveryService,OUTSTANDING
        self.driver();delivery=DeliveryService(self.service)
        prepared=delivery.prepare(operation='handoff-prepare',delivery='handoff',work='synthetic-work',action='execute',
            deadline_ns=self.contract['scope']['limits']['expires_wall_ns']+10**9,grant=self.store.head(prepared_key('run')))
        delivery.start(operation='handoff-start',delivery='handoff',receipt=prepared['receipt'],statement='Run this exact step')
        result=self.controller.delivery(operation='handoff-run',delivery='handoff')
        self.assertEqual('completed',result['status']);self.assertIsNone(self.store.head(PENDING));self.assertIsNone(self.store.head(OUTSTANDING))
        self.assertEqual('active',self.service.view('synthetic-work')['state'])

    def test_parent_finishes_closed_child_after_lost_terminal_reply_without_restart(self):
        from colvia.delivery.service import DeliveryService
        self.driver();delivery=DeliveryService(self.service)
        preview=delivery.prepare(operation='handoff-prepare',delivery='handoff',work='synthetic-work',action='execute',
            deadline_ns=self.contract['scope']['limits']['expires_wall_ns']+10**9,grant=self.store.head(prepared_key('run')))
        delivery.start(operation='handoff-start',delivery='handoff',receipt=preview['receipt'],statement='Run this step')
        append=self.journal.append
        def lose(**kw):
            value=append(**kw)
            if kw['kind']=='terminal':raise OSError('lost terminal reply')
            return value
        with patch.object(self.journal,'append',side_effect=lose),self.assertRaises(OSError):
            self.controller.delivery(operation='handoff-run',delivery='handoff')
        self.assertIsNone(self.store.head(PENDING));self.assertEqual(1,self.processes.launches)
        self.assertEqual('finished',delivery.status('handoff')['state'])

    def queued_delivery(self):
        from colvia.delivery.service import DeliveryService
        self.driver();service=DeliveryService(self.service)
        preview=service.prepare(operation='handoff-prepare',delivery='handoff',work='synthetic-work',action='execute',
            deadline_ns=self.contract['scope']['limits']['expires_wall_ns']+10**9,grant=self.store.head(prepared_key('run')))
        service.start(operation='handoff-start',delivery='handoff',receipt=preview['receipt'],statement='Run this exact step')
        return service
    def test_cancel_between_claim_and_start_closes_without_child(self):
        from colvia.delivery.service import DeliveryService
        service=self.queued_delivery();claim=DeliveryService.claim
        def cancel_after(obj,**kw):
            result=claim(obj,**kw);obj.cancel(operation='cancel-claimed',delivery='handoff',statement='Stop');return result
        with patch.object(DeliveryService,'claim',cancel_after),self.assertRaisesRegex(RecordError,'cancelled'):
            self.controller.delivery(operation='run-handoff',delivery='handoff')
        self.assertEqual('cancelled',service.status('handoff')['state']);self.assertIsNone(self.store.head(PENDING));self.assertEqual(0,self.processes.launches)
    def test_refused_start_after_claim_finishes_failed_without_child(self):
        service=self.queued_delivery()
        with patch.object(self.journal,'start',side_effect=RecordError('execution-deadline')),self.assertRaises(RecordError):
            self.controller.delivery(operation='run-handoff',delivery='handoff')
        self.assertEqual('failed',service.status('handoff')['state']);self.assertIsNone(self.store.head(PENDING));self.assertEqual(0,self.processes.launches)
    def test_lost_claim_ack_requires_explicit_finish_and_does_not_launch(self):
        from colvia.delivery.service import DeliveryService
        service=self.queued_delivery();claim=DeliveryService.claim
        def lose(obj,**kw):claim(obj,**kw);raise OSError('lost claim ack')
        with patch.object(DeliveryService,'claim',lose),self.assertRaises(OSError):
            self.controller.delivery(operation='run-handoff',delivery='handoff')
        self.assertEqual('active',service.status('handoff')['state']);self.assertIsNotNone(self.store.head(PENDING))
        value=self.controller.finish_delivery(operation='finish-no-child',delivery='handoff')
        self.assertEqual('failed',value['state']);self.assertIsNone(self.store.head(PENDING));self.assertEqual(0,self.processes.launches)
    def test_active_no_child_run_closes_without_launch(self):
        service=self.queued_delivery()
        with self.effects.exclusion():service.claim(operation='claim',delivery='handoff',effects=self.effects)
        value=self.controller.delivery(operation='run-handoff',delivery='handoff')
        self.assertEqual('failed',value['state']);self.assertEqual(0,self.processes.launches)
    def test_finish_refuses_an_unclosed_child(self):
        service=self.queued_delivery()
        with self.effects.exclusion():
            service.claim(operation='claim',delivery='handoff',effects=self.effects)
            self.journal.start(operation='start',run='run',receipt=self.receipt,statement='Run',parent=self.store.head(PENDING))
        with self.assertRaisesRegex(RecordError,'unclosed-execution'):
            self.controller.finish_delivery(operation='finish',delivery='handoff')
        self.assertIsNotNone(self.store.head(PENDING));self.assertEqual(0,self.processes.launches)
    def test_lost_start_ack_uses_existing_exact_human_resolution(self):
        from colvia.execution.resolution import Resolution
        from test_foundation_execution_resolution import Observer
        self.driver();start=self.journal.start
        def lose(**kw):start(**kw);raise OSError('lost start ack')
        with patch.object(self.journal,'start',side_effect=lose),self.assertRaises(OSError):self.start_driver()
        resolution=Resolution(self.journal,Observer(self.contract));preview=resolution.preview('run')
        value=resolution.apply(operation='resolve-fresh',run='run',receipt=preview['receipt'],statement='Record this unresolved run; do not restart')
        self.assertEqual('operator-resolved-unknown',value['status']);self.assertFalse(value['accepted'])
        self.assertIsNone(self.store.head(PENDING));self.assertEqual(0,self.processes.launches)

    def test_managed_resolution_uses_existing_observer_and_exact_receipt(self):
        from colvia.managed_entry import ManagedEntry
        from test_foundation_execution_resolution import Observer
        self.driver();self.journal.start(operation='start',run='run',receipt=self.receipt,statement='Run')
        entry=SimpleNamespace(lease=Held());observer=Observer(self.contract);authority=SimpleNamespace(root=self.root.parent)
        args=SimpleNamespace(action='resolve-preview',run='run')
        with patch('colvia.platforms.effects_port.effects',return_value=object()),patch('colvia.platforms.darwin_execution.DarwinExecutionObservation',return_value=observer):
            preview=ManagedEntry.document_resolution(entry,args,self.store,self.service.workspace,authority)
            self.assertIsNotNone(self.store.head(PENDING))
            args=SimpleNamespace(action='resolve',run='run',operation='resolve',receipt=preview['receipt'],statement='Record unresolved; do not resume')
            value=ManagedEntry.document_resolution(entry,args,self.store,self.service.workspace,authority)
        self.assertEqual('operator-resolved-unknown',value['status']);self.assertFalse(value['accepted']);self.assertEqual(0,self.processes.launches)

    def test_delivery_lost_start_ack_resolution_then_finish_preserves_parent(self):
        from colvia.execution.resolution import Resolution
        from test_foundation_execution_resolution import Observer
        from colvia.records import link
        service=self.queued_delivery();start=self.journal.start
        def lose(**kw):start(**kw);raise OSError('lost child start ack')
        with patch.object(self.journal,'start',side_effect=lose),self.assertRaises(OSError):
            self.controller.delivery(operation='run-handoff',delivery='handoff')
        parent=link(service.read('handoff')[0],'owner')
        resolution=Resolution(self.journal,Observer(self.contract));preview=resolution.preview('run')
        value=resolution.apply(operation='resolve-child',run='run',receipt=preview['receipt'],statement='Record unresolved; no replay')
        self.assertEqual('operator-resolved-unknown',value['status']);self.assertEqual(parent,self.store.head(PENDING))
        result=self.controller.finish_delivery(operation='finish-resolved-child',delivery='handoff')
        self.assertEqual('finished',result['state']);self.assertIsNone(self.store.head(PENDING));self.assertEqual(0,self.processes.launches)

    def test_no_child_finish_rejects_cancel_race_without_replaying(self):
        from colvia.delivery.service import DeliveryService
        service=self.queued_delivery()
        with self.effects.exclusion():service.claim(operation='claim',delivery='handoff',effects=self.effects)
        finish=DeliveryService._finish
        def race(obj,**kw):
            obj.cancel(operation='racing-cancel',delivery='handoff',statement='Stop')
            return finish(obj,**kw)
        with patch.object(DeliveryService,'_finish',race),self.assertRaises(RecordError):
            self.controller.finish_delivery(operation='finish',delivery='handoff')
        self.assertEqual('active',service.status('handoff')['state']);self.assertIsNotNone(self.store.head(PENDING));self.assertEqual(0,self.processes.launches)
