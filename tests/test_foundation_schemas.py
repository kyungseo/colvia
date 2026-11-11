from io import BytesIO
from pathlib import Path
import hashlib
import tempfile
import unittest

from colvia.backup import supported_requirements, ExportBudget, ExportReader, ImportedSnapshot, write_export
from colvia.bodies import ingest_body
from colvia.codec import Edge, RecordError, decode_envelope, encode_envelope
from colvia.graph import AuditBudget, GraphAudit
from colvia.schemas import foundation_registry
from colvia.storage.sqlite import GenerationStore


class SchemaTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='schemas-'); self.handles=[]
        self.store=GenerationStore.create(Path(self.tmp.name)/'generation.sqlite3',project='project',instance='instance',
                                          generation='generation',active_check=lambda:None)
    def tearDown(self):
        for h in self.handles: h.close()
        self.store.close(); self.tmp.cleanup()
    def audit(self,root=None,load=None):
        h=GraphAudit(Path(self.tmp.name)/f'audit-{len(self.handles)}.sqlite3',AuditBudget(10000,10000,16*1024*1024))
        self.handles.append(h)
        return h.run(root or self.store.root().ref,load or self.store.load,foundation_registry())

    def test_published_body_and_retained_old_roots_roundtrip(self):
        before=self.store.root().ref
        self.store.begin_import('import','owner')
        data=b'synthetic\r\n'+bytes(range(256))*100
        ref,raw=ingest_body(BytesIO(data),self.store,'import',expected_size=len(data),expected_sha256=hashlib.sha256(data).hexdigest())
        self.store.commit_heads(operation='publish',expected={'body':None},changes={'body':ref},objects=[(ref,raw)],
                                import_id='import',validate=lambda load:None)
        audit=self.audit(); refs=set(audit.refs())
        self.assertIn(before,refs); self.assertIn(ref,refs)
        out=BytesIO(); write_export(out,project='project',audit=audit,load=self.store.load)
        reader=ExportReader(BytesIO(out.getvalue()),ExportBudget(10000,16*1024*1024))
        imported=dict(reader.objects()); self.assertTrue(reader.complete)
        after=self.audit(reader.root,imported.__getitem__)
        self.assertEqual(refs,set(after.refs()))

    def test_stream_import_preserves_root_and_refuses_missing_capability(self):
        self.store.begin_import('import','owner')
        body,raw=ingest_body(BytesIO(b'preserved synthetic bytes'),self.store,'import')
        self.store.commit_heads(operation='save',expected={'body':None},changes={'body':body},objects=[(body,raw)],
                                import_id='import',validate=lambda load:None)
        audit=self.audit(); stream=BytesIO()
        write_export(stream,project='project',audit=audit,load=self.store.load)
        snapshot=ImportedSnapshot(Path(self.tmp.name)/'import.sqlite3',BytesIO(stream.getvalue()),
                                  budget=ExportBudget(10000,16*1024*1024),
                                  graph_budget=AuditBudget(10000,10000,16*1024*1024),
                                  registry=foundation_registry(),capabilities=supported_requirements(foundation_registry()))
        try:
            self.assertTrue(snapshot.complete)
            self.assertEqual(self.store.root().ref,snapshot.audit.root)
            self.assertEqual({r:self.store.load(r) for r in audit.refs()},dict(snapshot.objects()))
        finally: snapshot.close()
        with self.assertRaisesRegex(RecordError,'import-capability-unavailable'):
            ImportedSnapshot(Path(self.tmp.name)/'refused.sqlite3',BytesIO(stream.getvalue()),
                             budget=ExportBudget(10000,16*1024*1024),
                             graph_budget=AuditBudget(10000,10000,16*1024*1024),
                             registry=foundation_registry(),capabilities=set())
        self.assertEqual(audit.root,self.store.root().ref)

    def test_import_does_not_activate_unknown_required_kind_or_other_project(self):
        self.store.reader_capabilities|={'schema:future.decision:1'};self.store.writer_capabilities|={'schema:future.decision:1'}
        future,raw=encode_envelope('future.decision',1,{'links':{}})
        self.store.commit_heads(operation='save',expected={'x':None},changes={'x':future},objects=[(future,raw)],
                                validate=lambda load:None)
        audit=self.audit(); stream=BytesIO()
        write_export(stream,project='project',audit=audit,load=self.store.load)
        with self.assertRaisesRegex(RecordError,'import-capability-unavailable'):
            ImportedSnapshot(Path(self.tmp.name)/'future.sqlite3',BytesIO(stream.getvalue()),
                             budget=ExportBudget(10000,16*1024*1024),graph_budget=AuditBudget(10000,10000,16*1024*1024),
                             registry=foundation_registry(),capabilities=supported_requirements(foundation_registry()))

    def test_whole_body_digest_is_verified_not_just_chunk_hashes(self):
        self.store.begin_import('import','owner')
        ref,raw=ingest_body(BytesIO(b'synthetic'),self.store,'import')
        obj=decode_envelope(ref,raw); p=dict(obj.payload); p['sha256']='0'*64
        bad,raw=encode_envelope(ref.kind,ref.version,p,obj.edges)
        values={bad:raw}
        def load(r): return values[r] if r in values else self.store.load(r,import_id='import')
        with self.assertRaisesRegex(RecordError,'body-identity-mismatch'): self.audit(bad,load)

    def test_root_semantic_order_does_not_depend_on_import_order(self):
        root=self.store.root(); obj=decode_envelope(root.ref,self.store.load(root.ref))
        bad,raw=encode_envelope('state.root',1,dict(project='project',sequence=2,operation='operation',links={'heads':[0],'operations':[1],'previous':[2]}),
                               (Edge('integrity',root.heads),Edge('integrity',root.operations),Edge('provenance',root.ref)))
        def load(r): return raw if r==bad else self.store.load(r)
        with self.assertRaisesRegex(RecordError,'invalid-root-predecessor'): self.audit(bad,load)


if __name__=='__main__': unittest.main()
