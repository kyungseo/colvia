"""Native managed-file effects in synthetic folders only; no installed integration."""
import tempfile,unittest
from pathlib import Path
from colvia.codec import RecordError
from colvia.binding import Locator,ProjectBinding,Topology,WorkspaceRegistration
from colvia.connection import Connections,PROJECT_KEY
from colvia.effects import PENDING
from colvia.lifecycle import Detach,owned_block
from colvia.platforms.darwin_detach import DarwinDetach
from colvia.platforms.exclusive import available
from colvia.platforms.posix import location
from colvia.storage.authority import Authority
from test_foundation_binding import P,I,W

@unittest.skipUnless(available(),'Native APFS effect adapter unavailable')
class DetachTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='detach-');self.base=Path(self.tmp.name)
        self.project=self.base/'project';self.project.mkdir();self.route=self.base/'routing';self.route.mkdir()
        self.authority=Authority.create(self.base/'authority',project=P,instance=I,generation='initial');self.store=self.authority.store()
        self.locator=Locator(P,I,1,'a'*64,W);top=Topology('plain',location(self.project))
        Connections(self.store).connect(operation='connect',binding=ProjectBinding(self.locator,'plain',top.root),observed=top,
            workspace=WorkspaceRegistration(W,top.root,None),verify_topology=lambda:top)
        self.block=b'<!-- Colvia start -->\nmanaged entry\n<!-- Colvia end -->\n'
        entry=b'User rules before\n'+self.block+b'User rules after\n'
        self.changes=[dict(role='routing',root='routing',path='route.json',before=b'connected',after=None),
                      dict(role='entry',root='project',path='AGENTS.md',before=entry,after=owned_block(entry,self.block)),
                      dict(role='locator',root='project',path='colvia-locator.json',before=b'exact locator',after=None)]
        for c in self.changes:
            root=self.route if c['root']=='routing' else self.project;(root/c['path']).write_bytes(c['before'])
        self.port=DarwinDetach(self.authority.root,dict(project=self.project,routing=self.route));self.service=Detach(self.store,self.port)
    def tearDown(self):self.store.close();self.tmp.cleanup()
    def start(self):
        preview=self.service.preview(self.changes)
        return self.service.begin(operation='detach',changes=self.changes,receipt=preview['receipt'],statement='Detach this project, keep history')
    def test_order_and_history_preservation(self):
        before=self.store.root().ref;self.start()
        self.service.advance('detach');self.assertFalse((self.route/'route.json').exists());self.assertTrue((self.project/'colvia-locator.json').exists())
        self.service.advance('detach');self.assertEqual(b'User rules before\nUser rules after\n',(self.project/'AGENTS.md').read_bytes())
        self.assertIsNotNone(self.store.head(PROJECT_KEY));self.service.advance('detach')
        self.assertIsNone(self.store.head(PROJECT_KEY));self.assertIsNone(self.store.head(PENDING))
        self.assertIsNotNone(self.store.load(before));self.assertIsNotNone(self.store.operation_result('connect'))
        self.assertEqual('detached',self.service.advance('detach')['state'])
        self.assertEqual(3,len(list((self.authority.root/'effects').glob('*/*.original'))))
    def test_stale_preview_and_changed_owned_block_refuse(self):
        preview=self.service.preview(self.changes);(self.project/'AGENTS.md').write_bytes(b'user replacement')
        with self.assertRaisesRegex(RecordError,'detach-files-changed'):
            self.service.begin(operation='detach',changes=self.changes,receipt=preview['receipt'],statement='Detach')
        self.assertIsNone(self.store.head(PENDING))
        with self.assertRaisesRegex(RecordError,'detach-entry-edited-or-ambiguous'):owned_block(b'user replacement',self.block)
    def test_crash_after_evacuation_resumes_exact_intent(self):
        self.start()
        def crash(name):
            if name=='after-evacuate':raise RuntimeError('synthetic interruption')
        with self.assertRaises(RuntimeError):self.service.advance('detach',event=crash)
        self.assertIsNotNone(self.store.head(PENDING));self.assertTrue((self.project/'colvia-locator.json').exists())
        self.service.advance('detach');self.service.advance('detach');self.service.advance('detach')
        self.assertIsNone(self.store.head(PENDING));self.assertIsNone(self.store.head(PROJECT_KEY))
    def test_change_to_later_file_blocks_without_clobbering(self):
        self.start();self.service.advance('detach');entry=self.project/'AGENTS.md';entry.write_bytes(b'new user edit')
        with self.assertRaisesRegex(RecordError,'effect-path-unknown|detach-files-changed'):self.service.advance('detach')
        self.assertEqual(b'new user edit',entry.read_bytes());self.assertTrue((self.project/'colvia-locator.json').exists())
        self.assertIsNotNone(self.store.head(PENDING));self.assertIsNotNone(self.store.head(PROJECT_KEY))
    def test_pending_other_effect_blocks_before_staging(self):
        binding=self.store.head(PROJECT_KEY)
        self.store.commit_heads(operation='other',expected={PENDING:None},changes={PENDING:binding},objects=[],validate=lambda _:None)
        with self.assertRaisesRegex(RecordError,'external-effect-pending'):self.start()
        self.assertFalse((self.authority.root/'effects').exists())
    def test_order_cannot_remove_locator_before_entry(self):
        self.changes.reverse()
        with self.assertRaisesRegex(RecordError,'invalid-detach-order'):self.service.preview(self.changes)

    def test_staging_port_cannot_change_the_approved_transformation(self):
        from unittest.mock import patch
        original=self.port.prepare
        def changed(operation,changes):
            altered=[dict(c) for c in changes];altered[1]['after']=b'unapproved rewrite'
            return original(operation,altered)
        preview=self.service.preview(self.changes)
        with patch.object(self.port,'prepare',changed):
            with self.assertRaisesRegex(RecordError,'detach-preview-manifest-mismatch'):
                self.service.begin(operation='detach',changes=self.changes,receipt=preview['receipt'],statement='Detach')
        self.assertIsNone(self.store.head(PENDING));self.assertEqual(self.changes[1]['before'],(self.project/'AGENTS.md').read_bytes())
