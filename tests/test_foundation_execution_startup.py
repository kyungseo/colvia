"""Fresh-constructor failure closure: durable synthetic store, no process/model."""
import unittest
from types import SimpleNamespace
from unittest.mock import patch
from colvia.codec import RecordError,PublicationRefused
from colvia.effects import PENDING
from colvia.execution.host import run_document_host
from colvia.execution.unstarted import close_unstarted
from test_foundation_execution_store import JournalFixture
from test_foundation_execution_history import BIRTH

class StartupTests(JournalFixture,unittest.TestCase):
    def fresh(self):
        self.launch();state,grant,_,owner,_=self.journal.read('run')
        self.claim=(state.ref,grant.ref,owner.ref);self.lock=SimpleNamespace(locked=True)
    def close(self):
        return close_unstarted(self.journal,'run',claim=self.claim,lock=self.lock,error=RecordError('synthetic_startup'))
    def test_known_unstarted_failure_closes_without_accepting(self):
        self.fresh();self.close()
        self.assertIsNone(self.store.head(PENDING))
        self.assertEqual('revoked-before-launch',self.journal.status('run')['status'])
        self.assertFalse(self.journal.status('run')['accepted'])
        self.assertEqual('active',self.service._head('synthetic-work')[1].payload['phase'])
    def test_stale_claim_and_unheld_lock_do_not_publish(self):
        self.fresh();root=self.store.root().ref;claim=self.claim
        self.claim=('0'*64,*claim[1:])
        with self.assertRaisesRegex(RecordError,'owner-changed'):self.close()
        self.claim=claim;self.lock.locked=False
        with self.assertRaisesRegex(RecordError,'lock-required'):self.close()
        self.assertEqual(root,self.store.root().ref)
    def test_existing_runtime_intent_is_never_closed_as_unstarted(self):
        self.fresh();self.journal.append(operation='reserve',run='run',kind='runtime-reserved',value=dict(ordinal=1,host_pid=9000,host_birth=BIRTH))
        state,grant,_,owner,_=self.journal.read('run');self.claim=(state.ref,grant.ref,owner.ref);root=self.store.root().ref
        with self.assertRaisesRegex(RecordError,'not-fresh'):self.close()
        self.assertEqual(root,self.store.root().ref);self.assertIsNotNone(self.store.head(PENDING))
    def test_revocation_lost_ack_never_replays_or_publishes_terminal(self):
        self.fresh();append=self.journal.append;calls=[]
        def lose(**kw):
            calls.append(kw['kind']);append(**kw);raise OSError('lost ack')
        with patch.object(self.journal,'append',side_effect=lose),self.assertRaises(OSError):self.close()
        self.assertEqual(['revoked'],calls);self.assertIsNotNone(self.store.head(PENDING))
        self.assertIsNone(self.journal.read('run')[-1].terminal)
    def test_terminal_lost_ack_reports_uncertainty_without_undoing_commit(self):
        self.fresh();append=self.journal.append;calls=[]
        def lose(**kw):
            calls.append(kw['kind']);result=append(**kw)
            if kw['kind']=='terminal':raise OSError('lost ack')
            return result
        with patch.object(self.journal,'append',side_effect=lose),self.assertRaises(OSError):self.close()
        self.assertEqual(['revoked','terminal'],calls);self.assertIsNone(self.store.head(PENDING))
        self.assertEqual('revoked-before-launch',self.journal.status('run')['status'])
    def test_proved_publication_refusal_is_not_retried(self):
        self.fresh();root=self.store.root().ref
        with patch.object(self.journal,'append',side_effect=PublicationRefused('conflict')) as append,self.assertRaises(PublicationRefused):self.close()
        self.assertEqual(1,append.call_count);self.assertEqual(root,self.store.root().ref)
    def test_constructor_failure_closes_and_preserves_primary_error(self):
        self.fresh();error=RecordError('constructor_failure')
        with patch('colvia.execution.host.DocumentHost',side_effect=error),self.assertRaises(RecordError) as caught:
            run_document_host(self.journal,'run',claim=self.claim,lock=self.lock)
        self.assertIs(error,caught.exception);self.assertIsNone(self.store.head(PENDING))
    def test_runtime_failure_is_not_treated_as_constructor_failure(self):
        self.fresh();host=SimpleNamespace(run=lambda:(_ for _ in ()).throw(RecordError('runtime_failure')))
        with patch('colvia.execution.host.DocumentHost',return_value=host),patch('colvia.execution.unstarted.close_unstarted') as close,self.assertRaises(RecordError):
            run_document_host(self.journal,'run',claim=self.claim,lock=self.lock)
        close.assert_not_called();self.assertIsNotNone(self.store.head(PENDING))

    def test_cancel_before_constructor_closure_has_consistent_reason(self):
        self.fresh();self.journal.cancel(operation='cancel',run='run',reason='cancelled');self.close()
        h=self.journal.read('run')[-1]
        self.assertEqual('cancelled',h.rows[-2]['value']['reason']);self.assertEqual('cancelled',h.rows[-1]['value']['stop_reason'])
    def test_pending_owner_mismatch_refuses_without_publication(self):
        self.fresh();head=self.store.head;before=self.store.root().ref
        with patch.object(self.store,'head',side_effect=lambda k:None if k==PENDING else head(k)),self.assertRaisesRegex(RecordError,'owner-changed'):self.close()
        self.assertEqual(before,self.store.root().ref)
    def test_real_constructor_mismatch_closes_exact_fresh_claim(self):
        self.fresh()
        ports=dict(backend=SimpleNamespace(journal=object()),launch=None,policy=None,runtime_processes=None,worker_processes=None,channel_factory=None,session_factory=None,worker_exchange=None)
        with self.assertRaisesRegex(RecordError,'journal-mismatch'):
            run_document_host(self.journal,'run',claim=self.claim,lock=self.lock,**ports)
        h=self.journal.read('run')[-1];self.assertEqual(['granted','revoked','terminal'],[r['kind'] for r in h.rows]);self.assertEqual('revoked-before-launch',h.terminal)
    def test_constructor_unknown_cleanup_is_not_hidden(self):
        self.fresh();append=self.journal.append;original=RecordError('constructor_failure');prior=ValueError('prior');original.__cause__=prior
        def lose(**kw):append(**kw);raise OSError('lost revocation ack')
        with patch('colvia.execution.host.DocumentHost',side_effect=original),patch.object(self.journal,'append',side_effect=lose),self.assertRaisesRegex(RecordError,'closure-unknown') as caught:
            run_document_host(self.journal,'run',claim=self.claim,lock=self.lock)
        self.assertIs(original,caught.exception.__cause__);self.assertIs(prior,original.__cause__);self.assertIsNotNone(self.store.head(PENDING))
    def test_constructor_terminal_refusal_after_revocation_is_unknown(self):
        self.fresh();append=self.journal.append
        def refuse(**kw):
            if kw['kind']=='terminal':raise PublicationRefused('conflict')
            return append(**kw)
        with patch('colvia.execution.host.DocumentHost',side_effect=RecordError('constructor_failure')),patch.object(self.journal,'append',side_effect=refuse),self.assertRaisesRegex(RecordError,'closure-unknown'):
            run_document_host(self.journal,'run',claim=self.claim,lock=self.lock)
        self.assertIsNone(self.journal.read('run')[-1].terminal);self.assertIsNotNone(self.store.head(PENDING))

    def test_cancellation_between_revoke_and_terminal_uses_one_observation(self):
        self.fresh();append=self.journal.append
        def race(**kw):
            value=append(**kw)
            if kw['kind']=='revoked':self.journal.cancel(operation='late-cancel',run='run',reason='cancelled')
            return value
        with patch.object(self.journal,'append',side_effect=race):self.close()
        history=self.journal.read('run')[-1]
        self.assertEqual(history.rows[-2]['value']['reason'],history.rows[-1]['value']['stop_reason'])
