"""Cross-layer retention and coherent read checks for ordinary Work."""
from io import BytesIO
from pathlib import Path
import unittest
from colvia.backup import ExportReader,ExportBudget,write_export
from colvia.bodies import body_bytes
from colvia.codec import RecordError
from colvia.graph import AuditBudget,GraphAudit
from colvia.maps import map_get
from colvia.planning import Planning
from colvia.records import application_registry,link
from colvia.tree import build_tree,entry_at
from test_foundation_tree import regular
from test_foundation_work import WorkFixture

class IntegrityTests(WorkFixture,unittest.TestCase):
    def test_completed_archived_work_exports_original_and_submitted_bytes(self):
        original=b'original\r\n\x00\xff';submitted=b'new\r\n\x00\xfe'
        (self.root/'report.md').write_bytes(original);self.start()
        (self.root/'report.md').write_bytes(submitted);review=self.submit()
        self.service.accept(operation='accept',work='report',receipt=review['receipt'],statement='수락')
        self.service.archive(operation='archive',work='report',archived=True)
        result=self.result();plan=self.service._object(link(result,'plan'))
        before=map_get(link(plan,'before'),'report.md',self.store.load)
        after=map_get(link(result,'after'),'report.md',self.store.load)
        audit=GraphAudit(Path(self.tmp.name)/'full-audit.sqlite3',AuditBudget(10000,10000,32*1024*1024))
        try:
            audit.run(self.store.root().ref,self.store.load,application_registry())
            stream=BytesIO();write_export(stream,project=self.store.project,audit=audit,load=self.store.load)
            reader=ExportReader(BytesIO(stream.getvalue()),ExportBudget(10000,32*1024*1024));objects=dict(reader.objects())
            self.assertTrue(reader.complete)
            self.assertEqual(original,b''.join(body_bytes(before,objects.__getitem__)))
            self.assertEqual(submitted,b''.join(body_bytes(after,objects.__getitem__)))
        finally:audit.close()
    def test_candidate_page_refuses_mid_page_head_change(self):
        planning=Planning(self.store)
        planning.save_candidate(operation='one',candidate='one',title='하나',reason='후보')
        original=planning.candidate;changed=[False]
        def read(candidate):
            value=original(candidate)
            if not changed[0]:
                changed[0]=True
                Planning(self.store).save_candidate(operation='two',candidate='two',title='둘',reason='추가')
            return value
        planning.candidate=read
        with self.assertRaisesRegex(RecordError,'list-changed'):planning.candidates()
    def test_selected_tree_lookup_is_bounded_and_checks_the_path(self):
        entries=[regular(f'file-{i}') for i in range(3000)];tree=build_tree(entries);objects=dict(tree.objects);reads=[]
        def load(ref):reads.append(ref);return objects[ref]
        self.assertEqual(entries[71],entry_at(tree.root,'file-71',load))
        self.assertLessEqual(len(reads),9);self.assertLess(len(reads),len(objects))
        self.assertIsNone(entry_at(tree.root,'absent',objects.__getitem__))
        corrupted=dict(objects);corrupted[reads[-1]]=b'corrupt'
        with self.assertRaises(RecordError):entry_at(tree.root,'file-71',corrupted.__getitem__)

if __name__=='__main__':unittest.main()
