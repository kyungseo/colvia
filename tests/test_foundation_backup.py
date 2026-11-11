from io import BytesIO
from pathlib import Path
import tempfile
import unittest

from colvia.backup import ExportBudget, ExportReader, write_export
from colvia.codec import Edge, RecordError, encode_envelope, object_ref
from colvia.graph import AuditBudget, GraphAudit, Registry


class ShortIO(BytesIO):
    def read(self,n=-1): return super().read(min(n,7) if n>=0 else 7)
    def write(self,b): return super().write(b[:11])


class BackupTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='backup-')
        self.chunk=object_ref('body.chunk',1,bytes(range(256)))
        self.root,raw=encode_envelope('future.saved',3,{'opaque':'preserve'},(Edge('provenance',self.chunk),))
        self.values={self.root:raw,self.chunk:bytes(range(256))}
        self.audit=GraphAudit(Path(self.tmp.name)/'audit.sqlite3',AuditBudget(20,20,10000))
        self.audit.run(self.root,self.values.__getitem__,Registry([]))
    def tearDown(self): self.audit.close(); self.tmp.cleanup()
    def output(self,stream=None):
        stream=stream if stream is not None else BytesIO()
        write_export(stream,project='synthetic-project',audit=self.audit,
                     load=self.values.__getitem__)
        return stream.getvalue()
    def reader(self,raw,**budget): return ExportReader(BytesIO(raw),ExportBudget(**(dict(objects=20,total_bytes=10000)|budget)))

    def test_exact_bytes_unknown_extension_and_short_io_roundtrip(self):
        raw=self.output(ShortIO()); self.assertEqual(self.output(),raw)
        reader=ExportReader(ShortIO(raw),ExportBudget(2,len(raw)))
        self.assertEqual(self.values,dict(reader.objects()))
        self.assertTrue(reader.complete); self.assertEqual(self.root,reader.root)
        self.assertEqual(['foundation-v1','schema:future.saved:3'],reader.header['read_requirements'])
        self.assertEqual(reader.header['read_requirements'],reader.header['write_requirements'])

    def test_truncation_corruption_trailing_bytes_and_false_manifest(self):
        raw=self.output()
        variants=[raw[:n] for n in (0,5,30,len(raw)-1)]
        variants += [raw+b'x',raw.replace(b'preserve',b'changed!'),raw.replace(b'"objects": 2',b'"objects": 3')]
        for value in variants:
            with self.subTest(size=len(value)),self.assertRaises(RecordError):
                reader=self.reader(value); list(reader.objects())

    def test_limit_and_partial_iteration_are_not_success(self):
        raw=self.output()
        for budget in [dict(objects=1),dict(total_bytes=len(raw)-1)]:
            reader=self.reader(raw,**budget)
            with self.assertRaises(RecordError): list(reader.objects())
            self.assertFalse(reader.complete)
        reader=self.reader(raw); iterator=reader.objects(); next(iterator)
        self.assertFalse(reader.complete); iterator.close()
        with self.assertRaisesRegex(RecordError,'export-already-read'): list(reader.objects())

    def test_changed_loader_and_cancel_do_not_create_complete_export(self):
        out=BytesIO()
        with self.assertRaisesRegex(RecordError,'object-identity-mismatch'):
            write_export(out,project='synthetic',audit=self.audit,load=lambda r:b'changed')
        with self.assertRaises(RecordError): list(self.reader(out.getvalue()).objects())
        with self.assertRaisesRegex(RecordError,'export-cancelled'):
            write_export(BytesIO(),project='synthetic',audit=self.audit,
                         load=self.values.__getitem__,cancelled=lambda:True)

    def test_reordered_duplicate_frames_refused(self):
        raw=self.output(); header_end=len(b'COLVIA\x00EXPORT\x00\x01')
        header_end+=4+int.from_bytes(raw[header_end:header_end+4],'big')
        pos=header_end; frames=[]
        while raw[pos:pos+1]==b'O':
            start=pos; size=int.from_bytes(raw[pos+1:pos+5],'big')
            import json
            ref=json.loads(raw[pos+5:pos+5+size]); pos+=5+size+ref['byte_length']
            frames.append(raw[start:pos])
        for sequence in [list(reversed(frames)),[frames[0],frames[0],frames[1]]]:
            bad=raw[:header_end]+b''.join(sequence)+raw[pos:]
            with self.assertRaisesRegex(RecordError,'export-order-or-duplicate'):
                list(self.reader(bad).objects())

    def test_caller_cannot_understate_requirements(self):
        with self.assertRaisesRegex(RecordError,'export-requirements-mismatch'):
            write_export(BytesIO(),project='synthetic',audit=self.audit,load=self.values.__getitem__,read_requirements=[])



if __name__=='__main__': unittest.main()
