"""Native isolated document workers with synthetic runtime admission.

No model is launched and no installed release is qualified. Runtime admission
rows are an explicit fixture. Five real sandboxed document operations are tested.
A failing fixture is retained for diagnosis instead of removing its evidence.
"""
import hashlib,sys,unittest
from pathlib import Path
from distribution.document_worker import build
from colvia.execution.callbacks import CallbackGate
from colvia.execution.worker import DocumentController
from colvia.platforms.darwin_effects import DarwinEffects
from colvia.platforms.darwin_execution import DarwinExecutionObservation
from colvia.platforms.darwin_execution_inputs import resource_digest
from colvia.platforms.darwin_document_backend import DarwinDocumentBackend
from colvia.platforms.darwin_processes import DarwinProcesses
from colvia.platforms.worker_stdio import exchange
from test_foundation_execution_store import JournalFixture
from test_foundation_execution_history import Chain

@unittest.skipUnless(sys.platform=='darwin','native sandboxed worker')
class NativeExecutionTests(JournalFixture,unittest.TestCase):
    def setUp(self):super().setUp();self.preserve=False
    def tearDown(self):
        if self.preserve:
            self.store.close();self.tmp._finalizer.detach()
        else:super().tearDown()
    def test_read_write_and_three_verifiers_retain_result_without_accepting_work(self):
        try:self.flow()
        except BaseException:
            self.preserve=True
            raise
    def flow(self):
        source=Path(__file__).resolve().parents[1];area=self.root.parent
        authority=area/'effects';authority.mkdir(mode=0o700);archive=area/'worker.pyz';build(source/'src',archive)
        marker=area/'synthetic-runtime';marker.write_bytes(b'NO MODEL - synthetic runtime admission only')
        resources=dict(python_digest=Path(sys.executable).resolve(),worker_digest=archive,
            parser_digest=source/'runtime/official/marked.umd.js',profile_digest=source/'runtime/official/worker.sb.in',runtime_digest=marker)
        for name,path in resources.items():self.contract['scope']['resources'][name]=resource_digest(path)
        effects=DarwinEffects(self.root,authority);observer=DarwinExecutionObservation(self.journal,effects)
        with effects.exclusion():
            for item in self.contract['scope']['documents'].values():item['original_identity']=observer.document(item['path'])
        self.launch();backend=DarwinDocumentBackend(self.journal,observer,resources,Path(sys.prefix).resolve())
        with effects.exclusion(create=False):
            gate=CallbackGate(self.journal,'run',backend);chain=Chain(self.contract).launch()
            for row in chain.rows[1:-1]:gate.append(row['kind'],row['value'])
            gate.bind('synthetic-thread','synthetic-turn')
            controller=DocumentController(gate,backend,DarwinProcesses(),exchange)
            for number,(tool,args) in enumerate((
                ('document_read',{'file_ids':['Output','Reference']}),
                ('document_write',dict(file_id='Output',expected_sha256=hashlib.sha256(self.raw).hexdigest(),content='new synthetic text!!')),
                ('document_verify',{'verifier_id':'DOC-LINKS'}),
                ('document_verify',{'verifier_id':'DOC-GFM'}),
                ('document_verify',{'verifier_id':'DOC-CLAIMS'})),1):
                envelope=dict(threadId='synthetic-thread',turnId='synthetic-turn',callId='call-'+str(number),tool=tool,arguments=args)
                reply=controller.dispatch(gate.reserve(envelope))
                if tool=='document_read':self.assertEqual(self.raw.decode(),reply['files'][0]['content'])
                if tool=='document_verify':self.assertTrue(reply['pass'])
            history=self.journal.read('run')[-1]
            self.assertEqual(5,len(history.completed_refs));self.assertEqual('applied',history.effect())
            self.assertTrue(all(w['close'] is not None for w in history.workers.values()))
            self.assertIsNone(history.terminal)
            self.assertEqual(b'new synthetic text!!',(self.root/'output.md').read_bytes())
            self.assertEqual(self.raw,(self.root/'reference.md').read_bytes())
            self.assertEqual('active',self.service._head('synthetic-work')[1].payload['phase'])
            self.assertEqual('present',backend.recovery.inspect(gate.grant,history))
