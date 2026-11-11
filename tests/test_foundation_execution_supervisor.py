"""Real store/gate with synthetic runtime ports; never starts an OS process."""
import copy,hashlib,io,unittest
from types import SimpleNamespace
from unittest.mock import patch
from colvia.codec import RecordError
from colvia.bodies import ingest_body
from colvia.effects import PENDING
from colvia.execution.callbacks import CallbackGate
from colvia.execution.supervisor import RuntimeSupervisor
from test_foundation_execution_store import JournalFixture
from test_foundation_execution_history import BIRTH,Chain,SHA
from test_foundation_execution_callbacks import NativeDouble
from test_foundation_execution_worker import ProcessDouble

class Launch:
    def __init__(self):self.bad=False
    def prepare(self,*args):return SimpleNamespace(argv=('synthetic',),cwd='/synthetic',env={})
    def verify(self,*args):
        if self.bad:raise RecordError('execution-resource-drift')
    def host_identity(self):return dict(pid=9000,birth=BIRTH)
class Policy:
    def bind(self,contract):pass
class Channel:
    def __init__(self,*args,**kwargs):self.closed=False
    def close(self):self.closed=True

class SupervisorTests(JournalFixture,unittest.TestCase):
    def ready(self,mode='fail'):
        self.launch();self.native=NativeDouble();self.gate=CallbackGate(self.journal,'run',self.native)
        self.port=ProcessDouble();self.launch_port=Launch();self.mode=mode;self.sessions=0;fixture=self
        class Session:
            failed=False;thread=None;turn=None
            def __init__(self,gate,policy,channel,**kwargs):fixture.sessions+=1
            def run(self,controller):
                if fixture.mode=='fail':raise RecordError('protocol_refused')
                if fixture.mode=='unsealed':return 'completed'
                fixture.complete_document()
                if fixture.mode=='cancel':fixture.journal.cancel(operation='last-cancel',run='run',reason='cancelled')
                return 'completed'
        self.supervisor=RuntimeSupervisor(self.gate,self.launch_port,self.port,Channel,Session)
    def run_supervisor(self):return self.supervisor.run(Policy(),None)
    def complete_document(self):
        chain=Chain().launch()
        for step in range(1,6):chain.successful(step)
        h=chain.read();chain.add('seal',completed_refs=h.completed_refs,result_identity=h.workers[2]['result']['value']['after'])
        after=b'new synthetic text!!';digest=hashlib.sha256(after).hexdigest()
        def bind(value):
            if type(value) is dict:
                for key,item in value.items():
                    if key in ('sha256','original_sha256') and item==SHA:value[key]=hashlib.sha256(self.raw).hexdigest()
                    elif key=='sha256' and item=='c'*64:value[key]=digest
                    else:bind(item)
            elif type(value) is list:
                for item in value:bind(item)
        self.store.begin_import('supervisor-body','test');body=ingest_body(io.BytesIO(after),self.store,'supervisor-body')
        for row in chain.rows[3:]:
            value=copy.deepcopy(row['value']);bind(value);options={}
            if row['kind']=='worker-result' and value['effect']=='applied':options=dict(result_body=body[0],objects=[body],import_id='supervisor-body')
            self.gate.append(row['kind'],value,**options)
    def test_secondary_pipe_cleanup_failure_does_not_rewrite_completed(self):
        self.ready('complete')
        with patch.object(self.port,'close_io',side_effect=OSError('pipe cleanup')):
            value=self.run_supervisor()
        self.assertEqual('completed',value['status']);self.assertEqual(['owned-io-cleanup-failed'],value['diagnostics'])
        self.assertEqual('completed',self.journal.status('run')['status']);self.assertIsNone(self.store.head(PENDING))
    def test_unowned_pipe_never_admits_session_or_reports_closure(self):
        self.ready()
        with patch.object(self.port,'admit_io',side_effect=RecordError('execution-owned-pipes-required')),self.assertRaises(RecordError):
            self.run_supervisor()
        self.assertEqual(0,self.sessions);self.assertEqual([9100],self.port.aborts)
        self.assertEqual('unknown',self.journal.status('run')['status']);self.assertIsNotNone(self.store.head(PENDING))
    def test_success_closes_and_retains_result_without_accepting_work(self):
        self.ready('complete');result=self.run_supervisor()
        self.assertEqual('completed',result['status']);self.assertFalse(result['accepted'])
        self.assertEqual('active',self.service._head('synthetic-work')[1].payload['phase'])
        self.assertIsNone(self.store.head(PENDING));self.assertEqual(1,self.port.launches)
        with self.assertRaisesRegex(RecordError,'supervisor-consumed'):self.run_supervisor()
    def test_closed_protocol_failure_keeps_original_error_and_not_acceptance(self):
        self.ready()
        with self.assertRaisesRegex(RecordError,'protocol_refused'):self.run_supervisor()
        self.assertEqual('interrupted',self.journal.status('run')['status']);self.assertIsNone(self.store.head(PENDING))
        self.assertEqual(1,len(self.port.stops))
    def test_drift_before_reservation_never_spawns(self):
        self.ready();self.launch_port.bad=True
        with self.assertRaisesRegex(RecordError,'resource-drift'):self.run_supervisor()
        self.assertEqual(0,self.port.launches);self.assertIsNone(self.journal.read('run')[-1].runtime_intent)
    def test_cancel_before_reservation_never_spawns(self):
        self.ready();self.journal.cancel(operation='cancel-before',run='run',reason='cancelled')
        with self.assertRaisesRegex(RecordError,'cancelled'):self.run_supervisor()
        self.assertEqual(0,self.port.launches);self.assertIsNone(self.journal.read('run')[-1].runtime_intent)
    def test_known_spawn_failure_is_closed_without_repeating(self):
        self.ready();self.port.spawn_failure=True
        with self.assertRaises(OSError):self.run_supervisor()
        self.assertEqual('revoked-before-launch',self.journal.status('run')['status']);self.assertIsNone(self.store.head(PENDING))
        self.assertEqual(0,self.sessions)
    def test_ambiguous_spawn_keeps_barrier(self):
        self.ready()
        with patch.object(self.port,'launch',side_effect=RuntimeError('uncertain spawn')),self.assertRaises(RuntimeError):self.run_supervisor()
        self.assertEqual('unknown',self.journal.status('run')['status']);self.assertIsNotNone(self.store.head(PENDING))
        self.assertIsNone(self.journal.read('run')[-1].runtime_failure)
    def test_missing_process_identity_never_admits_session_or_claims_closure(self):
        self.ready()
        with patch.object(self.port,'identity',return_value=dict(pid=9100,birth=None)),self.assertRaisesRegex(RecordError,'identity-unavailable'):self.run_supervisor()
        self.assertEqual(0,self.sessions);self.assertEqual([],self.port.stops);self.assertIsNotNone(self.store.head(PENDING))
        self.assertIsNone(self.journal.read('run')[-1].runtime_close)
    def test_secondary_io_failure_keeps_original_cause_chain(self):
        self.ready();self.port.close_failure=True
        with patch.object(self.port,'close_io',side_effect=OSError('cleanup')),self.assertRaisesRegex(RecordError,'closure_unconfirmed') as caught:
            self.run_supervisor()
        self.assertEqual('protocol_refused',caught.exception.__cause__.code)
        self.assertIn('owned-io-cleanup-failed',caught.exception.__notes__)
        self.assertIsNotNone(self.store.head(PENDING))

    def test_closure_failure_preserves_primary_error_and_barrier(self):
        self.ready();self.port.close_failure=True
        with self.assertRaisesRegex(RecordError,'closure_unconfirmed') as caught:self.run_supervisor()
        self.assertEqual('protocol_refused',caught.exception.__cause__.code)
        self.assertEqual('unknown',self.journal.status('run')['status']);self.assertIsNotNone(self.store.head(PENDING))
    def test_lost_started_ack_closes_only_known_process_and_preserves_store_uncertainty(self):
        self.ready();append=self.journal.append
        def lose(**kwargs):
            result=append(**kwargs)
            if kwargs['kind']=='runtime-started':raise OSError('lost ack')
            return result
        with patch.object(self.journal,'append',side_effect=lose),self.assertRaises(OSError):self.run_supervisor()
        self.assertEqual(1,len(self.port.stops));self.assertTrue(self.gate.failed)
        self.assertIsNotNone(self.store.head(PENDING));self.assertIsNone(self.journal.read('run')[-1].runtime_close)
    def test_child_closure_must_match_all_observed_processes(self):
        self.ready();stop=self.port.stop
        def inconsistent(*args,**kwargs):
            result=stop(*args,**kwargs);result['children']=[dict(pid=9200,birth=BIRTH,absent=True)];return result
        with patch.object(self.port,'stop',side_effect=inconsistent),self.assertRaisesRegex(RecordError,'child-closure-mismatch'):self.run_supervisor()
        self.assertIsNotNone(self.store.head(PENDING));self.assertIsNone(self.journal.read('run')[-1].runtime_close)
    def test_new_observed_child_is_recorded_before_closure(self):
        self.ready();stop=self.port.stop
        def observed(process,known,**kwargs):
            result=stop(process,known,**kwargs);known[9200]={'birth':BIRTH};result['children']=[dict(pid=9200,birth=BIRTH,absent=True)];return result
        with patch.object(self.port,'stop',side_effect=observed),self.assertRaisesRegex(RecordError,'protocol_refused'):self.run_supervisor()
        h=self.journal.read('run')[-1];self.assertEqual([dict(pid=9200,birth=BIRTH)],h.children);self.assertIsNotNone(h.runtime_close)
    def test_late_cancel_cannot_publish_completed(self):
        self.ready('cancel');self.assertEqual('interrupted',self.run_supervisor()['status']);self.assertIsNone(self.store.head(PENDING))
    def test_runtime_claim_without_document_seal_is_not_completed(self):
        self.ready('unsealed')
        with self.assertRaisesRegex(RecordError,'premature_completion'):self.run_supervisor()
        self.assertEqual('interrupted',self.journal.status('run')['status'])

    def test_invalid_identities_are_recorded_and_owned_handle_aborted(self):
        self.ready()
        with patch.object(self.port,'identity',return_value=dict(pid=9999,birth=BIRTH)),self.assertRaises(RecordError):self.run_supervisor()
        self.assertEqual([9100],self.port.aborts)
        self.assertEqual(dict(ordinal=1,pid=9100,birth=None),self.journal.read('run')[-1].runtime_start['value'])
        self.assertEqual('unknown',self.journal.status('run')['status']);self.assertEqual(0,self.sessions)
    def test_malformed_birth_is_recorded_without_session(self):
        self.ready()
        with patch.object(self.port,'identity',return_value=dict(pid=9100,birth='bad')),self.assertRaises(RecordError):self.run_supervisor()
        self.assertEqual([9100],self.port.aborts);self.assertIsNone(self.journal.read('run')[-1].runtime_start['value']['birth'])
    def test_identity_observation_failure_aborts_owned_handle(self):
        self.ready()
        with patch.object(self.port,'identity',side_effect=OSError('identity unavailable')),self.assertRaises(RecordError):self.run_supervisor()
        self.assertEqual([9100],self.port.aborts);self.assertEqual(0,self.sessions)
    def test_children_observed_before_failed_stop_remain_in_history(self):
        self.ready()
        def failed(process,known,**kwargs):
            known[9200]={'birth':BIRTH};raise RecordError('closure_unconfirmed')
        with patch.object(self.port,'stop',side_effect=failed),self.assertRaises(RecordError):self.run_supervisor()
        self.assertEqual([dict(pid=9200,birth=BIRTH)],self.journal.read('run')[-1].children)
        self.assertEqual([9100],self.port.aborts);self.assertIsNotNone(self.store.head(PENDING))
    def test_reserved_then_drift_never_spawns(self):
        self.ready();append=self.journal.append
        def drift(**kwargs):
            result=append(**kwargs)
            if kwargs['kind']=='runtime-reserved':self.launch_port.bad=True
            return result
        with patch.object(self.journal,'append',side_effect=drift),self.assertRaisesRegex(RecordError,'resource-drift'):self.run_supervisor()
        self.assertEqual(0,self.port.launches);self.assertEqual('revoked-before-launch',self.journal.status('run')['status'])
    def test_post_spawn_drift_closes_before_session(self):
        self.ready();launch=self.port.launch
        def drift(*args,**kwargs):
            result=launch(*args,**kwargs);self.launch_port.bad=True;return result
        with patch.object(self.port,'launch',side_effect=drift),self.assertRaisesRegex(RecordError,'resource-drift'):self.run_supervisor()
        self.assertEqual(0,self.sessions);self.assertEqual(1,len(self.port.stops));self.assertIsNone(self.store.head(PENDING))
    def test_cancel_between_terminal_read_and_publication_is_interrupted(self):
        self.ready('complete');append=self.journal.append;injected=False
        def cancel(**kwargs):
            nonlocal injected
            if kwargs['kind']=='terminal' and kwargs['value']['status']=='completed' and not injected:
                injected=True;self.journal.cancel(operation='terminal-race',run='run',reason='cancelled')
            return append(**kwargs)
        with patch.object(self.journal,'append',side_effect=cancel):result=self.run_supervisor()
        self.assertEqual('interrupted',result['status']);self.assertFalse(self.gate.failed);self.assertIsNone(self.store.head(PENDING))
    def test_clean_cancel_before_start_releases_known_no_effect_owner(self):
        self.ready();self.journal.cancel(operation='cancelled-before',run='run',reason='cancelled')
        with self.assertRaisesRegex(RecordError,'cancelled'):self.run_supervisor()
        self.assertEqual('revoked-before-launch',self.journal.status('run')['status']);self.assertIsNone(self.store.head(PENDING))

    def test_cancel_after_terminal_validation_is_caught_by_final_cas(self):
        self.ready('complete');commit=self.store.commit_heads;injected=False
        def race(**kwargs):
            nonlocal injected
            original=kwargs['validate']
            def validate(view):
                nonlocal injected
                original(view)
                from colvia.codec import decode_envelope
                from colvia.execution.journal import key
                incoming=dict(kwargs.get('objects',()))
                ref=kwargs['changes'].get(key('run'))
                if ref in incoming and decode_envelope(ref,incoming[ref]).payload.get('status')=='completed' and not injected:
                    injected=True;self.journal.cancel(operation='cancel-after-validation',run='run',reason='cancelled')
            return commit(**dict(kwargs,validate=validate))
        with patch.object(self.store,'commit_heads',side_effect=race):result=self.run_supervisor()
        self.assertTrue(injected);self.assertEqual('interrupted',result['status']);self.assertFalse(self.gate.failed);self.assertIsNone(self.store.head(PENDING))

class ConversationIntegrationTests(JournalFixture,unittest.TestCase):
    def setup_conversation(self,*,cancel_after_write=False):
        from colvia.adapters.document_session import DocumentSession
        from colvia.execution.worker import DocumentController
        from test_foundation_document_session import ChannelDouble
        from test_foundation_execution_admission import AdmissionTests
        from test_foundation_execution_worker import NativeDouble as WorkerNative
        import json
        self.policy,contract,config,account,models=AdmissionTests().fixture()
        self.contract['capability']=contract['capability'];self.launch();fixture=self
        class Native(WorkerNative):
            def validate_result(self,grant,tool,args,result,plan,deadline):
                if tool=='document_verify':return dict(verifier_id=args['verifier_id'],**{'pass':True}),None,None
                return super().validate_result(grant,tool,args,result,plan,deadline)
        native=Native(self);gate=CallbackGate(self.journal,'run',native);self.runtime=ProcessDouble();workers=ProcessDouble()
        def exchange(*args,**kwargs):
            if cancel_after_write and native.tool=='document_write':fixture.journal.cancel(operation='write-cancel',run='run',reason='cancelled')
            return b'{"ok":true,"result":{}}',0
        controller=DocumentController(gate,native,workers,exchange)
        class Flow(ChannelDouble):
            def __init__(self,*args,**kwargs):
                super().__init__({'initialize':{},'config/read':{'config':config},'account/read':account,
                    'model/list':models,'thread/start':{'model':fixture.policy.model,'thread':{'id':'thread'}},
                    'turn/start':{'turn':{'id':'turn'}},'turn/interrupt':{}})
                requests=[('document_read',{'file_ids':['Output','Reference']}),
                    ('document_write',{'file_id':'Output','expected_sha256':hashlib.sha256(fixture.raw).hexdigest(),'content':'new synthetic text!!'}),
                    *[('document_verify',{'verifier_id':v}) for v in ('DOC-LINKS','DOC-GFM','DOC-CLAIMS')]]
                self.prefix['turn/start']=[dict(id='cb-'+str(i),method='item/tool/call',params=dict(threadId='thread',turnId='turn',callId='call-'+str(i),tool=tool,arguments=value)) for i,(tool,value) in enumerate(requests)]
                self.prefix['turn/interrupt']=[dict(method='turn/completed',params={'threadId':'thread','turn':{'id':'turn','status':'interrupted'}})]
            def write(self,raw):
                result=super().write(raw);value=json.loads(raw)
                if value.get('id')=='cb-4':self.queue.append(dict(method='turn/completed',params={'threadId':'thread','turn':{'id':'turn','status':'completed'}}))
                return result
            def close(self):pass
        self.supervisor=RuntimeSupervisor(gate,Launch(),self.runtime,Flow,DocumentSession)
        self.controller=controller;self.workers=workers
    def test_actual_session_and_controller_connect_five_callbacks_to_host_closure(self):
        self.setup_conversation();result=self.supervisor.run(self.policy,self.controller)
        self.assertEqual('completed',result['status']);self.assertFalse(result['accepted'])
        self.assertEqual(5,self.workers.launches);self.assertEqual(1,self.runtime.launches)
        self.assertIsNone(self.store.head(PENDING));h=self.journal.read('run')[-1]
        self.assertEqual(5,len(h.completed_refs));self.assertIsNotNone(h.seal);self.assertIsNotNone(h.runtime_close)
    def test_cancel_after_write_keeps_applied_evidence_and_never_accepts(self):
        self.setup_conversation(cancel_after_write=True)
        with self.assertRaisesRegex(RecordError,'cancelled'):self.supervisor.run(self.policy,self.controller)
        h=self.journal.read('run')[-1]
        self.assertEqual(('interrupted','applied'),(h.terminal,h.effect()))
        self.assertEqual(2,self.workers.launches);self.assertIn('turn/interrupt',h.rpc)
        self.assertIsNone(self.store.head(PENDING));self.assertEqual('active',self.service._head('synthetic-work')[1].payload['phase'])
