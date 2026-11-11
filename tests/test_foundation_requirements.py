from pathlib import Path
import tempfile,unittest
from colvia.codec import RecordError,encode_envelope
from colvia.storage.sqlite import GenerationStore,runtime_capabilities

class RequirementsTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='requirements-');self.path=Path(self.tmp.name)/'state.sqlite3';self.handles=[]
        self.options=dict(project='synthetic',instance='local',generation='one',active_check=lambda:None)
        self.current=runtime_capabilities();self.future=self.current|{'schema:future.decision:1'}
        self.writer=GenerationStore.create(self.path,reader_capabilities=self.future,writer_capabilities=self.future,**self.options);self.handles.append(self.writer)
    def tearDown(self):
        for h in self.handles:h.close()
        self.tmp.cleanup()
    def open(self,**capabilities):
        value=GenerationStore(self.path,**self.options,**capabilities);self.handles.append(value);return value
    def publish(self):
        pair=encode_envelope('future.decision',1,dict(links={},action='revoked'))
        self.writer.commit_heads(operation='future',expected={'decision':None},changes={'decision':pair[0]},objects=[pair],validate=lambda _:None)
    def test_open_and_existing_read_handle_refuse_unknown_new_semantics(self):
        old=self.open(readonly=True);self.publish()
        with self.assertRaisesRegex(RecordError,'store-reader-capability-unavailable'):old.root()
        with self.assertRaisesRegex(RecordError,'store-reader-capability-unavailable'):self.open(readonly=True)
        self.assertIn('schema:future.decision:1',self.writer.requirements()['read'])
    def test_reader_can_inspect_without_write_capability(self):
        self.publish();limited=self.open(reader_capabilities=self.future,writer_capabilities=self.current)
        self.assertIsNotNone(limited.head('decision'))
        with self.assertRaisesRegex(RecordError,'store-writer-capability-unavailable'):limited.begin_import('later','owner')
        self.assertEqual(self.writer.root(),limited.root())
    def test_unknown_publication_is_refused_atomically(self):
        old=self.open();before=old.root();pair=encode_envelope('future.decision',1,dict(links={},action='revoked'))
        with self.assertRaisesRegex(RecordError,'publication-capability-unavailable'):
            old.commit_heads(operation='bad',expected={'decision':None},changes={'decision':pair[0]},objects=[pair],validate=lambda _:None)
        self.assertEqual(before,old.root());self.assertNotIn('schema:future.decision:1',old.requirements()['read'])
    def test_removing_current_selection_does_not_lower_reader_requirements(self):
        self.publish();before=self.writer.head('decision')
        self.writer.commit_heads(operation='remove',expected={'decision':before},changes={'decision':None},validate=lambda _:None)
        self.assertIn('schema:future.decision:1',self.writer.requirements()['read'])
        with self.assertRaisesRegex(RecordError,'store-reader-capability-unavailable'):self.open(readonly=True)
