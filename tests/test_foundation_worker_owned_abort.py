"""Shared worker/process lifecycle boundaries using no OS process or model."""
import unittest
from unittest.mock import patch
from colvia.codec import RecordError
from colvia.effects import PENDING
import test_foundation_execution_worker as fixture
from test_foundation_execution_store import JournalFixture
from test_foundation_execution_history import BIRTH

class WorkerOwnedAbortTests(JournalFixture,unittest.TestCase):
    ready=fixture.ControllerTests.ready
    setup_controller=fixture.ControllerTests.setup_controller
    read=fixture.ControllerTests.read
    def test_wrong_pid_records_actual_unidentified_worker_and_aborts_handle(self):
        self.setup_controller()
        with patch.object(self.processes,'identity',return_value=dict(pid=9999,birth=BIRTH)),self.assertRaises(RecordError):self.read()
        self.assertEqual([9100],self.processes.aborts);h=self.journal.read('run')[-1]
        self.assertEqual(9100,h.workers[1]['start']['value']['pid']);self.assertIsNone(h.workers[1]['start']['value']['birth'])
        self.assertIsNone(h.workers[1]['close']);self.assertTrue(self.controller.unclosed);self.assertIsNotNone(self.store.head(PENDING))
    def test_unavailable_birth_still_aborts_owned_handle(self):
        self.setup_controller()
        with patch.object(self.processes,'identity',return_value=dict(pid=9100,birth=None)),self.assertRaises(RecordError):self.read()
        self.assertEqual([9100],self.processes.aborts);self.assertIsNotNone(self.store.head(PENDING))
    def test_stop_failure_keeps_barrier_after_owned_abort(self):
        self.setup_controller();self.processes.close_failure=True
        with self.assertRaises(RecordError):self.read()
        self.assertEqual([9100],self.processes.aborts);self.assertIsNotNone(self.store.head(PENDING));self.assertTrue(self.controller.unclosed)

    def test_cancel_at_worker_intent_closes_only_unspawned_callback(self):
        self.setup_controller();append=self.journal.append
        def cancel(**kwargs):
            if kwargs['kind']=='worker-spawn-intent':self.journal.cancel(operation='worker-intent-cancel',run='run',reason='cancelled')
            return append(**kwargs)
        with patch.object(self.journal,'append',side_effect=cancel),self.assertRaisesRegex(RecordError,'execution-cancel-requested'):self.read()
        h=self.journal.read('run')[-1];self.assertIsNone(h.pending);self.assertEqual({},h.workers)
        self.assertFalse(self.gate.failed);self.assertEqual(0,self.processes.launches)
        self.assertEqual('callback-aborted-before-spawn',h.rows[-1]['kind'])
