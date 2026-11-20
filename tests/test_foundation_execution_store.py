"""Durable journal tests use synthetic evidence; no model or OS process is launched."""
import copy,hashlib,io,time,unittest
from contextvars import Context
from unittest.mock import patch
from colvia.codec import RecordError,canonical_bytes
from colvia.bodies import ingest_body
from colvia.maps import build_map
from colvia.records import link
from colvia.effects import PENDING
from colvia.execution.journal import ExecutionJournal,key,cancel_key
from colvia.execution.records import history_bounds,MAX_EVENTS,MAX_HISTORY_BYTES
from test_foundation_work import WorkFixture
from test_foundation_execution_history import grant,Chain,BIRTH

class JournalFixture(WorkFixture):
    def setUp(self):
        super().setUp()
        self.initialize_execution_fixture()

    def initialize_execution_fixture(self):
        from colvia.configuration import Configuration
        config=Configuration(self.store);preview=config.preview(['official-execution'])
        config.apply(operation='fixture-enable',features=['official-execution'],receipt=preview['receipt'],statement='Enable synthetic fixture execution')
        self.raw=b'synthetic contents!!'
        for name in ('output.md','reference.md'):(self.root/name).write_bytes(self.raw)
        self.start(work='synthetic-work',scope=('output.md',))
        self.journal=ExecutionJournal(self.service)
        self.contract=grant(str(self.root))
        self.request=dict(prompt='Revise the approved excerpt.',claims={'Output':dict(required=['synthetic'],forbidden=[],evidence=[dict(file_id='Reference',quote='synthetic')])},approved_external_links=[],link_metadata={})
        self.contract['scope']['limits']['expires_wall_ns']=time.time_ns()+600*10**9
        for item in self.contract['scope']['documents'].values():
            item['original_identity']['sha256']=hashlib.sha256(self.raw).hexdigest()
            item['original_identity']['size']=len(self.raw)
        self.store.begin_import('body-import','test')
        body=ingest_body(io.BytesIO(self.raw),self.store,'body-import')
        mapping=build_map([(name,body[0]) for name in self.contract['scope']['documents']])
        self.bodymap=mapping.root;self.objects=[body,*mapping.objects]
    def prepare(self):
        return self.journal.prepare(operation='prepare',run='run',contract=self.contract,request=self.request,
            bodies=self.bodymap,objects=self.objects,import_id='body-import')
    def launch(self):
        receipt=self.prepare()['receipt']
        self.journal.start(operation='run-start',run='run',receipt=receipt,statement='Run this bounded task')
        return Chain(self.contract)
    def publish(self,chain,start=1):
        for row in chain.rows[start:]:
            self.journal.append(operation='event-'+str(row['seq']),run='run',kind=row['kind'],value=row['value'])

class JournalTests(JournalFixture,unittest.TestCase):
    def test_known_closure_releases_owner_without_submitting_or_accepting_work(self):
        chain=self.launch();owner=self.store.head(PENDING)
        chain.launch();self.publish(chain)
        self.assertEqual(owner,self.store.head(PENDING))
        old=len(chain.rows);chain.add('revoked',reason='cancelled');chain.close_runtime();chain.terminal('interrupted');self.publish(chain,old)
        self.assertIsNone(self.store.head(PENDING))
        self.assertEqual('interrupted',self.journal.status('run')['status'])
        self.assertFalse(self.journal.status('run')['accepted'])
        self.assertEqual('active',self.service._head('synthetic-work')[1].payload['phase'])
        with self.assertRaisesRegex(RecordError,'already-terminal'):
            self.journal.cancel(operation='late-cancel',run='run',reason='cancelled')

    def test_cancel_blocks_admission_but_not_started_closure_or_terminal_evidence(self):
        chain=self.launch();chain.add('runtime-reserved',ordinal=1,host_pid=9000,host_birth=BIRTH);self.publish(chain)
        owner=self.store.head(PENDING)
        self.journal.cancel(operation='cancel',run='run',reason='cancelled')
        old=len(chain.rows);chain.runtime=chain.add('runtime-started',ordinal=1,pid=9001,birth=BIRTH);self.publish(chain,old)
        self.assertEqual(owner,self.store.head(PENDING))
        with self.assertRaisesRegex(RecordError,'cancel-requested'):
            self.journal.append(operation='late-reservation',run='run',kind='rpc-reserved',value={'method':'initialize'})
        old=len(chain.rows);chain.add('revoked',reason='cancelled');chain.close_runtime();chain.terminal('interrupted');self.publish(chain,old)
        self.assertIsNone(self.store.head(PENDING))
        self.assertTrue(self.journal.status('run')['cancel_requested'])

    def test_expired_grant_still_records_already_started_evidence(self):
        chain=self.launch();chain.add('runtime-reserved',ordinal=1,host_pid=9000,host_birth=BIRTH);self.publish(chain)
        with patch('colvia.execution.journal.time.time_ns',return_value=self.contract['scope']['limits']['expires_wall_ns']+1):
            self.journal.append(operation='started-after-expiry',run='run',kind='runtime-started',value=dict(ordinal=1,pid=9001,birth=BIRTH))
            with self.assertRaisesRegex(RecordError,'deadline'):
                self.journal.append(operation='new-rpc',run='run',kind='rpc-reserved',value={'method':'initialize'})
        self.assertIsNotNone(self.store.head(PENDING))

    def test_same_cancel_idempotent_different_reason_refuses(self):
        self.launch();self.journal.cancel(operation='cancel',run='run',reason='cancelled');root=self.store.root().ref
        result=self.journal.cancel(operation='cancel-again',run='run',reason='cancelled')
        self.assertFalse(result['effects_stopped']);self.assertEqual(root,self.store.root().ref)
        with self.assertRaisesRegex(RecordError,'cancel-request-differs'):
            self.journal.cancel(operation='different',run='run',reason='deadline')

    def test_pending_run_blocks_ordinary_writer_and_second_run(self):
        self.launch()
        with self.assertRaisesRegex(RecordError,'external-effect-pending'):
            self.plan(work='second')
        with self.assertRaises(RecordError):
            self.journal.prepare(operation='second-run',run='second',contract=self.contract,request=self.request,bodies=self.bodymap)
        self.assertIsNotNone(self.store.head(PENDING))

    def test_receipt_and_native_root_are_bound_before_owner_acquisition(self):
        prepared=self.prepare()
        with self.assertRaisesRegex(RecordError,'stale-start-receipt'):
            self.journal.start(operation='wrong-receipt',run='run',receipt='wrong',statement='yes')
        self.assertIsNone(self.store.head(PENDING))
        self.contract['target']='/different'
        for name,item in self.contract['scope']['documents'].items():item['path']='/different/'+name+'.md'
        with self.assertRaisesRegex(RecordError,'target-registration-mismatch'):
            self.journal.prepare(operation='wrong-root',run='wrong-root',contract=self.contract,request=self.request,bodies=self.bodymap)

    def test_output_outside_scope_and_body_mismatch_refuse(self):
        self.contract['scope']['documents']['Output']['path']=str(self.root/'unapproved.md')
        with self.assertRaisesRegex(RecordError,'output-outside-scope'):self.prepare()
        self.contract['scope']['documents']['Output']['path']=str(self.root/'output.md')
        self.contract['scope']['documents']['Output']['original_identity']['sha256']='0'*64
        with self.assertRaisesRegex(RecordError,'input-body-mismatch'):self.prepare()

    def test_caller_boolean_cannot_resolve_unknown_or_clear_owner(self):
        self.launch();owner=self.store.head(PENDING)
        with self.assertRaisesRegex(RecordError,'special-publication-required'):
            self.journal.append(operation='forged-resolution',run='run',kind='operator-resolved-unknown',value={'process_absence':True})
        self.assertEqual(owner,self.store.head(PENDING))

    def test_reopen_reads_evidence_without_starting_effects(self):
        chain=self.launch();chain.launch();self.publish(chain)
        reopened=ExecutionJournal(self.service)
        self.assertEqual('incomplete',reopened.status('run')['status'])
        self.assertEqual(len(chain.rows),len(reopened.read('run')[-1].rows))
        self.assertEqual(self.raw,(self.root/'output.md').read_bytes())

    def test_complete_execution_retains_written_body_without_accepting_work(self):
        from test_foundation_execution_history import semantic_rows,SHA
        self.launch();chain=Chain().launch()
        for step in range(1,6):chain.successful(step)
        h=chain.read();chain.add('seal',result_identity=
            next(w['result']['value']['after'] for w in h.workers.values() if w['intent']['value']['role']=='write'),completed_refs=h.completed_refs)
        chain.close_runtime();chain.terminal('completed')
        after=b'new synthetic text!!';after_digest=hashlib.sha256(after).hexdigest()
        # Pure oracle uses synthetic hashes; bind identities to the retained bytes.
        def bind(value):
            if type(value) is dict:
                for k,v in value.items():
                    if k in ('sha256','original_sha256') and v==SHA:value[k]=hashlib.sha256(self.raw).hexdigest()
                    elif k=='sha256' and v=='c'*64:value[k]=after_digest
                    else:bind(v)
            elif type(value) is list:
                for v in value:bind(v)
        for row in chain.rows[1:]:bind(row['value'])
        from colvia.execution import schema
        chain.rows[0]['value']['scope_sha256']=schema.digest(self.contract['scope'])
        chain.rows=semantic_rows(chain.rows)
        self.store.begin_import('result-body','test')
        body=ingest_body(io.BytesIO(after),self.store,'result-body')
        for row in chain.rows[1:]:
            options={}
            if row['kind']=='worker-result' and row['value']['effect']=='applied':
                # Metadata alone is insufficient to claim a durable applied result.
                with self.assertRaisesRegex(RecordError,'result-body-required'):
                    self.journal.append(operation='missing-body',run='run',kind=row['kind'],value=row['value'])
                options=dict(result_body=body[0],objects=[body],import_id='result-body')
            self.journal.append(operation='complete-event-'+str(row['seq']),run='run',kind=row['kind'],value=row['value'],**options)
        self.assertEqual('completed',self.journal.status('run')['status']);self.assertIsNone(self.store.head(PENDING))
        from colvia.bodies import body_bytes
        self.assertEqual(after,b''.join(body_bytes(body[0],self.store.load)))
        self.assertEqual('active',self.service._head('synthetic-work')[1].payload['phase'])
        self.assertFalse(self.journal.status('run')['accepted'])

    def test_request_is_retained_and_rejected_prompt_never_published(self):
        from colvia.execution.journal import prepared_key
        self.request['prompt']='api_key=syntheticRejectedValue'
        before=self.store.root().ref
        with self.assertRaises(RecordError):self.prepare()
        self.assertEqual(before,self.store.root().ref);self.assertIsNone(self.store.head(prepared_key('run')))
        self.request['prompt']='Revise this excerpt.';self.launch()
        self.assertEqual('Revise this excerpt.',self.journal.read('run')[1].payload['request']['prompt'])

    def test_malformed_request_refuses_before_record_publication(self):
        from colvia.execution.schema import request_record
        for request in (dict(self.request,approved_external_links=[{}]),dict(self.request,claims={'Output':[]}),
                        dict(self.request,prompt='x'*65537)):
            with self.subTest(field=str(type(request))),self.assertRaises(RecordError):request_record(request,self.contract)

    def test_forged_checkpoint_is_rejected_on_read(self):
        from colvia.records import record
        self.launch();state,grant,h,owner,history=self.journal.read('run')
        forged=record('execution.state',dict(run='run',status='completed',effect='none',completed=0),
            {'grant':('decision',grant.ref),'authorization':('decision',link(state,'authorization')),
             'history':('integrity',h.ref),'owner':('decision',owner.ref),'previous':('provenance',state.ref)})
        objects={forged[0]:forged[1]}
        with self.assertRaisesRegex(RecordError,'checkpoint-mismatch'):
            self.journal.read('run',lambda ref:objects[ref] if ref in objects else self.store.load(ref),forged[0])

class JournalRaceTests(JournalFixture,unittest.TestCase):
    def interleave_cancel(self,**kw):
        validate=kw['validate']
        def race(view):
            validate(view)
            # Independent caller context advances only cancellation, never run/owner.
            # Sharing the validator ContextVar would falsely attach cancel reads
            # to the evidence publication, unlike another process/thread.
            with patch.object(self.store,'commit_heads',self.original_commit):
                Context().run(self.journal.cancel,operation='racing-cancel',run='run',reason='cancelled')
        kw['validate']=race
        return self.original_commit(**kw)

    def test_evidence_survives_cancel_after_validation_without_replaying_effect(self):
        chain=self.launch();chain.add('runtime-reserved',ordinal=1,host_pid=9000,host_birth=BIRTH);self.publish(chain)
        self.original_commit=self.store.commit_heads
        with patch.object(self.store,'commit_heads',side_effect=self.interleave_cancel):
            self.journal.append(operation='started-race',run='run',kind='runtime-started',value=dict(ordinal=1,pid=9001,birth=BIRTH))
        history=self.journal.read('run')[-1]
        self.assertEqual(3,len(history.rows));self.assertTrue(self.journal.status('run')['cancel_requested'])
        self.assertEqual('runtime-started',history.rows[-1]['kind'])

    def test_reservation_loses_cas_when_cancel_arrives_after_validation(self):
        self.launch();self.original_commit=self.store.commit_heads
        with patch.object(self.store,'commit_heads',side_effect=self.interleave_cancel),self.assertRaisesRegex(RecordError,'head-conflict'):
            self.journal.append(operation='reservation-race',run='run',kind='runtime-reserved',value=dict(ordinal=1,host_pid=9000,host_birth=BIRTH))
        self.assertEqual(1,len(self.journal.read('run')[-1].rows))
        self.assertIsNotNone(self.store.head(cancel_key('run')))
        self.assertIsNotNone(self.store.head(PENDING))

class JournalBounds(unittest.TestCase):
    def test_explicit_history_count_and_bytes_boundaries(self):
        history_bounds(MAX_EVENTS,MAX_HISTORY_BYTES)
        for count,size in ((MAX_EVENTS+1,1),(1,MAX_HISTORY_BYTES+1),(0,1),(True,1),(1,0)):
            with self.subTest(count=count,size=size),self.assertRaises(RecordError):history_bounds(count,size)
