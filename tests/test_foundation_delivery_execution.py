"""Nested ownership uses synthetic process history, not a model/runner."""
import time,unittest
from colvia.codec import RecordError
from colvia.effects import PENDING
from colvia.records import link
from colvia.delivery.service import DeliveryService,OUTSTANDING
from colvia.execution.journal import prepared_key
from test_foundation_execution_store import JournalFixture
from test_foundation_execution_history import Chain,BIRTH
from test_foundation_delivery import EffectsDouble

class NestedTests(JournalFixture,unittest.TestCase):
    def parent(self):
        self.execution_preview=self.prepare();self.delivery=DeliveryService(self.service);self.effects=EffectsDouble(self.root)
        self.grant=self.store.head(prepared_key('run'))
        preview=self.delivery.prepare(operation='delivery-prepare',delivery='handoff',work='synthetic-work',action='execute',
            deadline_ns=self.contract['scope']['limits']['expires_wall_ns']+10**9,grant=self.grant)
        self.delivery.start(operation='delivery-start',delivery='handoff',receipt=preview['receipt'],statement='Run the approved document step')
        self.delivery.claim(operation='delivery-claim',delivery='handoff',effects=self.effects)
        self.parent_owner=self.store.head(PENDING)
    def child(self):
        self.parent();self.journal.start(operation='child-start',run='run',receipt=self.execution_preview['receipt'],statement='Execute this grant',parent=self.parent_owner)
    def test_closed_child_returns_to_exact_parent_then_delivery_releases(self):
        self.child();self.assertNotEqual(self.parent_owner,self.store.head(PENDING))
        chain=Chain(self.contract);chain.terminal('revoked-before-launch');self.publish(chain)
        self.assertEqual(self.parent_owner,self.store.head(PENDING));self.assertIsNotNone(self.store.head(OUTSTANDING))
        self.delivery.finish_execution(operation='finish',delivery='handoff',run='run',effects=self.effects)
        self.assertIsNone(self.store.head(PENDING));self.assertIsNone(self.store.head(OUTSTANDING))
        self.assertEqual('active',self.service.view('synthetic-work')['state'])
        state,_=self.delivery.read('handoff');outcome=self.delivery.obj(link(state,'outcome'))
        self.assertEqual('executed',outcome.payload['kind'])
    def test_parent_cancel_blocks_new_child_admission_but_allows_closure_evidence(self):
        self.child();child_owner=self.store.head(PENDING)
        self.delivery.cancel(operation='cancel',delivery='handoff',statement='Stop')
        self.assertTrue(self.journal.cancel_requested('run'))
        with self.assertRaisesRegex(RecordError,'delivery-cancelled'):
            self.journal.append(operation='late',run='run',kind='runtime-reserved',value=dict(ordinal=1,host_pid=9000,host_birth=BIRTH))
        self.assertEqual(child_owner,self.store.head(PENDING))
        chain=Chain(self.contract);chain.terminal('revoked-before-launch');self.publish(chain)
        self.delivery.finish_execution(operation='finish',delivery='handoff',run='run',effects=self.effects)
        self.assertEqual('finished',self.delivery.status('handoff')['state']);self.assertIsNone(self.store.head(PENDING))
    def test_unknown_child_cannot_be_cleared_by_parent_completion(self):
        self.child();owner=self.store.head(PENDING);chain=Chain(self.contract)
        chain.add('runtime-reserved',ordinal=1,host_pid=9000,host_birth=BIRTH);chain.terminal('unknown');self.publish(chain)
        with self.assertRaisesRegex(RecordError,'unclosed-execution'):
            self.delivery.finish_execution(operation='finish',delivery='handoff',run='run',effects=self.effects)
        self.assertEqual(owner,self.store.head(PENDING));self.assertIsNotNone(self.store.head(OUTSTANDING))
    def test_parent_cancel_before_child_prevents_transfer(self):
        self.parent();self.delivery.cancel(operation='cancel',delivery='handoff',statement='Stop')
        with self.assertRaisesRegex(RecordError,'delivery-cancelled'):
            self.journal.start(operation='late',run='run',receipt=self.execution_preview['receipt'],statement='Run',parent=self.parent_owner)
        self.assertEqual(self.parent_owner,self.store.head(PENDING))
    def test_grant_expiry_cannot_outlive_parent_request(self):
        preview=self.prepare();delivery=DeliveryService(self.service)
        with self.assertRaisesRegex(RecordError,'grant-mismatch'):
            delivery.prepare(operation='short',delivery='short',work='synthetic-work',action='execute',deadline_ns=time.time_ns()+30*10**9,
                grant=self.store.head(prepared_key('run')))
        self.assertIsNone(self.store.head(PENDING))

    def test_started_child_cannot_use_unstarted_cancellation_escape(self):
        self.child();owner=self.store.head(PENDING)
        self.delivery.cancel(operation='cancel',delivery='handoff',statement='Stop')
        with self.assertRaises(RecordError):self.delivery.cancel_unstarted(operation='close',delivery='handoff',effects=self.effects)
        self.assertEqual(owner,self.store.head(PENDING))

    def test_claim_after_parentless_run_refuses_without_seizing_project_barrier(self):
        preview=self.prepare();delivery=DeliveryService(self.service);effects=EffectsDouble(self.root)
        grant=self.store.head(prepared_key('run'))
        request=delivery.prepare(operation='prepare-delivery',delivery='handoff',work='synthetic-work',action='execute',
            deadline_ns=self.contract['scope']['limits']['expires_wall_ns']+10**9,grant=grant)
        delivery.start(operation='start-delivery',delivery='handoff',receipt=request['receipt'],statement='Run once')
        self.journal.start(operation='outside-start',run='run',receipt=preview['receipt'],statement='Standalone run')
        chain=Chain(self.contract);chain.terminal('revoked-before-launch');self.publish(chain)
        self.assertIsNone(self.store.head(PENDING))
        with self.assertRaisesRegex(RecordError,'delivery-child-already-started'):
            delivery.claim(operation='late-claim',delivery='handoff',effects=effects)
        self.assertEqual('queued',delivery.status('handoff')['state']);self.assertIsNone(self.store.head(PENDING))
        delivery.cancel(operation='cancel-queued',delivery='handoff',statement='Cancel this stale request')
        self.assertIsNone(self.store.head(OUTSTANDING));self.assertIsNone(self.store.head(PENDING))

    def test_parent_cancel_blocks_sealed_completed_terminal_publication(self):
        from colvia.execution.callbacks import CallbackGate
        from test_foundation_execution_callbacks import NativeDouble
        from test_foundation_execution_supervisor import SupervisorTests
        from colvia.codec import PublicationRefused
        self.child();self.gate=CallbackGate(self.journal,'run',NativeDouble())
        self.gate.append('runtime-reserved',dict(ordinal=1,host_pid=9000,host_birth=BIRTH))
        self.gate.append('runtime-started',dict(ordinal=1,pid=9100,birth=BIRTH))
        SupervisorTests.complete_document(self)
        h=self.journal.read('run')[-1]
        self.gate.append('processes-closed',dict(runtime_ref=h.runtime_start['seq'],group_absent=True,final_scan_confirmed=True,children=[]))
        h=self.journal.read('run')[-1]
        self.delivery.cancel(operation='parent-last-cancel',delivery='handoff',statement='Stop')
        before=self.store.root()
        with self.assertRaises(PublicationRefused):self.gate.append('terminal',dict(status='completed',stop_reason=None,document_write_effect=h.effect(),effect_refs=h.effect_refs(),closure_refs=h.closure_refs()))
        self.assertEqual(before,self.store.root());self.assertFalse(self.gate.failed)
        self.gate.append('revoked',dict(reason='cancelled'));h=self.journal.read('run')[-1]
        self.gate.append('terminal',dict(status='interrupted',stop_reason='cancelled',document_write_effect=h.effect(),effect_refs=h.effect_refs(),closure_refs=h.closure_refs()))
        self.assertEqual(self.parent_owner,self.store.head(PENDING))
