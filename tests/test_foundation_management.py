import tempfile,unittest
from pathlib import Path
from colvia.codec import RecordError
from colvia.management import ManagerHome
from colvia.storage.authority import Authority
from colvia.storage.sqlite import runtime_capabilities
from colvia.configuration import Configuration,KEY
from colvia.effects import PENDING
import test_foundation_slots as slot_fixture
from test_foundation_binding import P,I

class ManagementTests(unittest.TestCase):
    slot=slot_fixture.SlotTests.slot
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='management-');self.base=Path(self.tmp.name)
        self.home=ManagerHome.create(self.base/'home',os_name='macos',architecture='arm64');self.manager=self.home.slots
        caps=tuple(c for c in runtime_capabilities() if c!='foundation-v1')
        self.one=self.slot('one',1,extra=caps);self.two=self.slot('two',2,extra=caps);self.manager.initialize(self.one)
        self.authority=Authority.create(self.home.root/'authorities'/P,project=P,instance=I,generation='first')
        store=self.authority.store()
        try:
            config=Configuration(store);preview=config.preview(['official-execution'])
            config.apply(operation='enable',features=['official-execution'],receipt=preview['receipt'],statement='선택')
            self.root=store.root().ref
        finally:store.close()
    def tearDown(self):self.tmp.cleanup()
    def test_update_preserves_record_settings_and_published_backup(self):
        selection,_=self.manager.selection();old=self.home.store(P)
        try:
            result=self.home.update(operation='update',target=self.two,expected_selection=selection)
            self.assertTrue(result['records_preserved']);self.assertTrue(result['settings_preserved'])
            with self.assertRaisesRegex(RecordError,'runtime-selection-changed'):old.root()
        finally:old.close()
        fresh=self.home.store(P)
        try:self.assertEqual(self.root,fresh.root().ref);self.assertIsNotNone(fresh.head(KEY))
        finally:fresh.close()
        self.assertTrue((self.home.root/'backups/update'/ (P+'.colvia-export')).is_file())
        self.assertEqual('completed',self.home.inspect_update('update')['state'])
    def test_crash_before_activation_preserves_current_and_backup(self):
        before,_=self.manager.selection()
        def fail(phase):
            if phase=='backed-up':raise RuntimeError('synthetic interruption')
        with self.assertRaises(RuntimeError):self.home.update(operation='interrupted',target=self.two,expected_selection=before,checkpoint=fail)
        self.assertEqual(before,self.manager.selection()[0]);self.assertEqual('not-activated',self.home.inspect_update('interrupted')['state'])
        self.assertTrue((self.home.root/'backups/interrupted'/ (P+'.colvia-export')).is_file())
    def test_crash_after_pointer_is_observed_not_reexecuted(self):
        before,_=self.manager.selection()
        def fail(phase):
            if phase=='activated':raise RuntimeError('synthetic interruption')
        with self.assertRaises(RuntimeError):self.home.update(operation='interrupted',target=self.two,expected_selection=before,checkpoint=fail)
        self.assertEqual('activated-unrecorded',self.home.inspect_update('interrupted')['state'])
        self.assertEqual(self.two,self.manager.selection()[1]['selected'])
    def test_incompatible_runtime_does_not_activate_or_create_backup(self):
        incompatible=self.slot('small',3);before,_=self.manager.selection()
        with self.assertRaisesRegex(RecordError,'runtime-capability-unavailable'):
            self.home.update(operation='incompatible',target=incompatible,expected_selection=before)
        self.assertEqual(before,self.manager.selection()[0]);self.assertFalse((self.home.root/'backups/incompatible').exists())
    def test_pending_external_effect_blocks_update(self):
        store=self.authority.store()
        try:store.commit_heads(operation='synthetic-pending',expected={PENDING:None},changes={PENDING:store.head(KEY)},validate=lambda _:None)
        finally:store.close()
        before,_=self.manager.selection()
        with self.assertRaisesRegex(RecordError,'project-effect-pending'):
            self.home.update(operation='blocked',target=self.two,expected_selection=before)
        self.assertEqual(before,self.manager.selection()[0])

if __name__=='__main__':unittest.main()
