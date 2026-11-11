"""Persistent controller ordering with explicit process/native doubles.

Actual process, worker writes, and pipe behavior have separate native checks.
These doubles never establish an installed or OS-isolated execution capability.
"""
import copy,hashlib,io,json,unittest
from types import SimpleNamespace
from unittest.mock import patch
from colvia.codec import RecordError
from colvia.effects import PENDING
from colvia.execution.worker import DocumentController
from test_foundation_execution_store import JournalFixture
from test_foundation_execution_history import BIRTH
import test_foundation_execution_callbacks as callbacks

class NativeDouble(callbacks.NativeDouble):
    def __init__(self,fixture):super().__init__();self.fixture=fixture;self.materialized=0;self.tool=None
    def materialize(self,grant,history,tool,args,ordinal):
        self.materialized+=1;self.tool=tool
        return SimpleNamespace(argv=('synthetic',),cwd='/',env={})
    def verify_plan(self,plan):pass
    def validate_result(self,grant,tool,args,result,plan,deadline):
        if tool=='document_write':
            raw=b'new synthetic text!!';before=grant.payload['contract']['scope']['documents']['Output']['original_identity']
            after=dict(before,ino=77,size=len(raw),sha256=hashlib.sha256(raw).hexdigest())
            return dict(file_id='Output',bytes=len(raw),sha256=after['sha256']),after,raw
        return dict(files=[]),None,None

class ProcessDouble:
    def __init__(self):self.launches=0;self.stops=[];self.aborts=[];self.spawn_failure=False;self.close_failure=False
    def launch(self,*args,**kwargs):
        self.launches+=1
        if self.spawn_failure:raise OSError('synthetic spawn failure')
        return SimpleNamespace(pid=9100,returncode=0,stdin=io.BytesIO(),stdout=io.BytesIO(),stderr=io.BytesIO())
    def admit_io(self,process):
        if not all(type(s) is io.BytesIO for s in (process.stdin,process.stdout,process.stderr)):
            raise RecordError('execution-owned-pipes-required')
    def close_io(self,process):
        self.admit_io(process)
        for stream in (process.stdin,process.stdout,process.stderr):stream.close()
    def identity(self,process):return dict(pid=process.pid,birth=BIRTH)
    def abort_owned(self,process,**kwargs):self.aborts.append(process.pid)
    def stop(self,process,known,**kwargs):
        self.stops.append(copy.deepcopy(known))
        if self.close_failure:raise RecordError('closure_unconfirmed')
        if process.pid not in known:raise RecordError('execution-runtime-identity-unavailable')
        return dict(returncode=0,group_absent=True,final_scan_confirmed=True,children=[])

class ControllerTests(JournalFixture,unittest.TestCase):
    ready=callbacks.CallbackTests.ready
    def setup_controller(self):
        self.ready();self.native=NativeDouble(self);self.gate.native=self.native
        self.processes=ProcessDouble()
        self.controller=DocumentController(self.gate,self.native,self.processes,
            lambda *a,**k:(b'{"ok":true,"result":{}}',0))
    def read(self):return self.controller.dispatch(self.gate.reserve(self.envelope))
    def test_success_records_result_and_closure_but_not_acceptance(self):
        self.setup_controller();self.assertEqual({'files':[]},self.read())
        history=self.journal.read('run')[-1];self.assertEqual(1,len(history.completed_refs))
        self.assertIsNotNone(history.workers[1]['result']);self.assertIsNotNone(history.workers[1]['close'])
        self.assertEqual('active',self.service._head('synthetic-work')[1].payload['phase'])
    def test_known_spawn_failure_is_recorded_without_started_claim(self):
        self.setup_controller();self.processes.spawn_failure=True
        with self.assertRaises(OSError):self.read()
        worker=self.journal.read('run')[-1].workers[1]
        self.assertIsNotNone(worker['failure']);self.assertIsNone(worker['start']);self.assertFalse(self.gate.complete())
        self.assertEqual([],self.processes.stops)
    def test_closure_failure_keeps_pending_and_prevents_next_launch(self):
        self.setup_controller();self.processes.close_failure=True
        with self.assertRaisesRegex(RecordError,'closure_unconfirmed'):self.read()
        history=self.journal.read('run')[-1];self.assertIsNotNone(history.workers[1]['result']);self.assertIsNone(history.workers[1]['close'])
        with self.assertRaisesRegex(RecordError,'worker-unavailable'):self.controller.dispatch({})
        self.assertEqual(1,self.processes.launches);self.assertIsNotNone(self.store.head(PENDING))
    def test_lost_started_ack_still_attempts_closure_without_republishing(self):
        self.setup_controller();append=self.journal.append
        def lose_ack(**kwargs):
            result=append(**kwargs)
            if kwargs['kind']=='worker-started':raise OSError('synthetic lost ack')
            return result
        with patch.object(self.journal,'append',side_effect=lose_ack),self.assertRaises(OSError):self.read()
        self.assertTrue(self.gate.failed);self.assertEqual([{9100:{'birth':BIRTH}}],self.processes.stops)
        worker=self.journal.read('run')[-1].workers[1];self.assertIsNotNone(worker['start']);self.assertIsNone(worker['close'])
        self.assertIsNotNone(self.store.head(PENDING))
    def test_cancel_during_worker_keeps_evidence_but_does_not_send_read(self):
        self.setup_controller()
        def exchange(*args,**kwargs):
            self.journal.cancel(operation='during-worker',run='run',reason='cancelled')
            return b'{"ok":true,"result":{}}',0
        self.controller.exchange=exchange
        with self.assertRaisesRegex(RecordError,'cancelled'):self.read()
        self.assertEqual(1,len(self.journal.read('run')[-1].completed_refs))
        self.assertEqual(1,len(self.processes.stops))
    def test_changed_reservation_scope_never_materializes(self):
        self.setup_controller();reservation=self.gate.reserve(self.envelope)
        reservation['arguments']={'file_ids':['Unapproved']}
        with self.assertRaisesRegex(RecordError,'scope_mismatch'):self.controller.dispatch(reservation)
        self.assertEqual(0,self.native.materialized);self.assertEqual(0,self.processes.launches)
    def test_write_result_is_retained_before_successful_callback_completion(self):
        self.setup_controller();self.read()
        envelope=dict(self.envelope,callId='second',tool='document_write',arguments=dict(file_id='Output',
            expected_sha256=hashlib.sha256(self.raw).hexdigest(),content='new synthetic text!!'))
        self.controller.dispatch(self.gate.reserve(envelope))
        history=self.journal.read('run')[-1]
        self.assertEqual('applied',history.effect());self.assertEqual(2,len(history.completed_refs))
        self.assertEqual('active',self.service._head('synthetic-work')[1].payload['phase'])
        self.assertIsNotNone(self.store.head(PENDING))

    def test_stderr_is_counted_without_retaining_or_returning_its_contents(self):
        self.setup_controller();self.controller.exchange=lambda *a,**k:(b'{"ok":true,"result":{}}',23)
        with self.assertRaisesRegex(RecordError,'worker_failed'):self.read()
        history=self.journal.read('run')[-1]
        diagnostics=[row['value'] for row in history.rows if row['kind']=='diagnostic']
        self.assertEqual([dict(source='worker',phase='worker',reason='worker_failed',byte_count=23)],diagnostics)
        self.assertIsNotNone(history.workers[1]['close']);self.assertFalse(history.workers[1]['result']['value']['success'])

    def test_primary_failure_survives_a_separate_closure_failure(self):
        self.setup_controller();self.processes.close_failure=True
        primary=RecordError('synthetic_primary_failure')
        def fail(*args,**kwargs):raise primary
        self.controller.exchange=fail
        with self.assertRaisesRegex(RecordError,'closure_unconfirmed') as caught:self.read()
        self.assertIs(primary,caught.exception.__cause__)
        history=self.journal.read('run')[-1]
        self.assertFalse(history.workers[1]['result']['value']['success'])
        self.assertIsNone(history.workers[1]['close']);self.assertTrue(self.controller.unclosed)
        self.assertIsNotNone(self.store.head(PENDING));self.assertEqual(1,self.processes.launches)

    def test_cancel_during_admitted_write_waits_for_evidence_and_suppresses_reply(self):
        self.setup_controller();self.read()
        envelope=dict(self.envelope,callId='second',tool='document_write',arguments=dict(file_id='Output',
            expected_sha256=hashlib.sha256(self.raw).hexdigest(),content='new synthetic text!!'))
        def exchange(*args,**kwargs):
            self.journal.cancel(operation='cancel-write',run='run',reason='cancelled')
            if kwargs['cancelled']():raise RecordError('cancelled')
            return b'{"ok":true,"result":{}}',0
        self.controller.exchange=exchange
        with self.assertRaisesRegex(RecordError,'cancelled'):self.controller.dispatch(self.gate.reserve(envelope))
        history=self.journal.read('run')[-1]
        self.assertEqual('applied',history.effect());self.assertEqual(2,len(history.completed_refs))
        self.assertIsNotNone(history.workers[2]['close']);self.assertEqual(2,len(self.processes.stops))
        self.assertIsNotNone(self.store.head(PENDING))

    def test_result_publication_error_retains_primary_failure_and_closes(self):
        self.setup_controller();primary=RecordError('primary-exchange-failure');publication=OSError('publication-failed')
        def fail(*a,**k):raise primary
        self.controller.exchange=fail;append=self.gate.append
        def publish(kind,*a,**k):
            if kind=='worker-result':raise publication
            return append(kind,*a,**k)
        with patch.object(self.gate,'append',side_effect=publish),self.assertRaises(OSError) as caught:self.read()
        self.assertIs(publication,caught.exception);self.assertIs(primary,caught.exception.__cause__)
        self.assertEqual(1,len(self.processes.stops));self.assertIsNotNone(self.store.head(PENDING))

    def test_owned_io_warning_does_not_fail_completed_callback(self):
        self.setup_controller()
        with patch.object(self.processes,'close_io',side_effect=OSError('synthetic IO cleanup')):
            self.assertEqual({'files':[]},self.read())
        self.assertEqual(['worker-owned-io-cleanup-failed'],self.controller.diagnostics)
        self.assertEqual(1,len(self.journal.read('run')[-1].completed_refs))
