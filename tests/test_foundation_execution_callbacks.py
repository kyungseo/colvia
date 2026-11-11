"""Journal-backed gate with an explicit non-native observation double."""
import copy,unittest
from unittest.mock import patch
from colvia.codec import RecordError
from colvia.execution.callbacks import CallbackGate
from test_foundation_execution_store import JournalFixture
from test_foundation_execution_history import BIRTH

class NativeDouble:
    def __init__(self):self.held=True;self.drift=False;self.checks=0
    def assert_held(self,grant,owner):
        if not self.held:raise RecordError('effect-lock-required')
    def preflight(self,grant,history):
        self.checks+=1
        if self.drift:raise RecordError('outside-output-project-drift')
    def startup(self,grant,history,deadline):self.preflight(grant,history)
    def callback_preflight(self,*args):pass
    def save_original(self,grant,history):
        scope=grant.payload['contract']['scope'];identity=scope['documents']['Output']['original_identity']
        return dict(output_id='Output',recovery_ordinal=1,original_identity=identity,
            original_sha256=identity['sha256'],byte_count=identity['size'])

class CallbackTests(JournalFixture,unittest.TestCase):
    def ready(self):
        chain=self.launch();self.native=NativeDouble();self.gate=CallbackGate(self.journal,'run',self.native)
        chain.launch()
        # The live binding records its own bound event after runtime admission.
        for row in chain.rows[1:-1]:self.gate.append(row['kind'],row['value'])
        self.gate.bind('thread','turn')
        self.envelope=dict(threadId='thread',turnId='turn',callId='first',tool='document_read',arguments={'file_ids':['Output','Reference']})
    def read_evidence(self,skip_intent=False):
        for kind,value in (
            ('worker-spawn-intent',dict(callback_id=1,worker_ordinal=1,role='read',code_identity='a'*64)),
            ('worker-started',dict(worker_ordinal=1,pid=9011,birth=BIRTH)),
            ('worker-result',dict(worker_ordinal=1,success=True,effect='none',before=None,after=None,verifier_id=None,verifier_pass=None,reason=None)),
            ('worker-closed',dict(worker_ordinal=1,returncode=0,group_absent=True,birth_absent=True))):
            if not (skip_intent and kind=='worker-spawn-intent'):self.gate.append(kind,value)
    def test_fresh_live_binding_and_exact_callback(self):
        self.ready();reserved=self.gate.reserve(self.envelope)
        self.assertEqual(1,reserved['callback_id']);self.assertGreater(self.native.checks,0)
        with self.assertRaisesRegex(RecordError,'live-restore-refused'):CallbackGate(self.journal,'run',self.native)
        with self.assertRaisesRegex(RecordError,'order_mismatch'):self.gate.reserve(self.envelope)
        self.read_evidence();self.assertTrue(self.gate.complete())
        self.assertEqual({'ok':True},self.gate.checked_reply({'ok':True}))
        self.assertEqual('active',self.service._head('synthetic-work')[1].payload['phase'])
    def test_wrong_caller_scope_tool_or_secret_never_reserves(self):
        self.ready()
        for change in (dict(threadId='other'),dict(namespace='shell'),dict(tool='shell'),
                dict(arguments={'file_ids':['Output']}),dict(callId='sk-'+('Z'*40))):
            with self.subTest(change=list(change)):
                envelope=dict(self.envelope,**change);before=len(self.journal.read('run')[-1].rows)
                with self.assertRaises(RecordError):self.gate.reserve(envelope)
                self.assertEqual(before,len(self.journal.read('run')[-1].rows))
    def test_cancel_preserves_evidence_but_suppresses_reply(self):
        self.ready();self.gate.reserve(self.envelope)
        self.gate.append('worker-spawn-intent',dict(callback_id=1,worker_ordinal=1,role='read',code_identity='a'*64))
        self.journal.cancel(operation='cancel',run='run',reason='cancelled')
        self.read_evidence(skip_intent=True);self.assertTrue(self.gate.complete())
        with self.assertRaisesRegex(RecordError,'cancelled'):self.gate.checked_reply({'files':[]})
        self.assertEqual(1,len(self.journal.read('run')[-1].completed_refs))
    def test_lock_and_whole_project_rechecked_before_reservation(self):
        self.ready();self.native.held=False
        with self.assertRaisesRegex(RecordError,'lock-required'):self.gate.reserve(self.envelope)
        self.native.held=True;self.native.drift=True
        with self.assertRaisesRegex(RecordError,'outside-output-project-drift'):self.gate.reserve(self.envelope)
        self.assertIsNone(self.journal.read('run')[-1].pending)
    def test_publication_uncertainty_latches_without_replaying(self):
        self.ready()
        with patch.object(self.journal,'append',side_effect=OSError('synthetic storage failure')):
            with self.assertRaises(OSError):self.gate.reserve(self.envelope)
        with self.assertRaisesRegex(RecordError,'publication-uncertain'):self.gate.reserve(self.envelope)
    def test_refusal_preserves_already_admitted_pending_callback(self):
        self.ready();self.gate.reserve(self.envelope)
        value=self.gate.refuse('caller_mismatch')
        self.assertEqual('not_started',value['effect_status'])
        self.assertEqual(1,self.journal.read('run')[-1].pending)
        self.assertTrue(self.journal.read('run')[-1].revoked)

    def test_validation_cancel_is_not_an_unknown_publication(self):
        self.ready();self.journal.cancel(operation='cancel-race',run='run',reason='cancelled')
        before=self.store.root()
        with self.assertRaisesRegex(RecordError,'execution-cancel-requested'):
            self.gate.append('callback-reserved',dict(callback_id=1,ordinal=1,tool='read',file_ids=self.gate.scope['read_ids'],verifier_id=None,expected_identity=None))
        self.assertFalse(self.gate.failed);self.assertEqual(before,self.store.root())
        self.gate.append('revoked',dict(reason='cancelled'))
