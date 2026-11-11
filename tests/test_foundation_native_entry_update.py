"""macOS APFS source fixtures; native binaries are inert bytes, never launched."""
import hashlib,unittest
from colvia.codec import RecordError
from colvia.updates.release import ReleaseUpdate
from test_foundation_installation import InstallationTests
from test_foundation_release_update import DownloadDouble

class NativeEntryTests(unittest.TestCase):
    setUp=InstallationTests.setUp
    tearDown=InstallationTests.tearDown
    archive=InstallationTests.archive
    slot=InstallationTests.slot
    install=InstallationTests.install
    def update_fixture(self):
        self.install();self.original=self.content['bin/colvia'];self.content['bin/colvia']=b'new inert v1 native entry'
        self.manifest['sequence']=2
        self.manifest['inventory']=[dict(path=p,kind='regular',mode='100755' if p.startswith('bin/') else '100644',size=len(b),
            sha256=hashlib.sha256(b).hexdigest()) for p,b in sorted(self.content.items()) if p!='manifest.json']
        archive,target=self.archive();target['path']=self.config['target'];target['custom']['colvia']['sequence']=2
        self.trust=DownloadDouble(archive,target);self.updater=ReleaseUpdate(self.home,self.trust,channel='preview')
        self.preview=self.updater.prepare(operation='update',target='release.zip');self.before=self.manager.selection()[0]
    def apply(self,**kwargs):return self.updater.apply(operation='update',receipt=self.preview['receipt'],**kwargs)
    def resume(self,**kwargs):return self.updater.resume(operation='update',receipt=self.preview['receipt'],**kwargs)
    def test_unpublished_preparation_area_is_preserved_and_fresh_attempt_can_complete(self):
        self.update_fixture();orphan=self.home.root/'operations/update-entry';orphan.mkdir(mode=0o700)
        (orphan/'partial').write_bytes(b'interrupted staging')
        self.apply();self.assertEqual(b'interrupted staging',(orphan/'partial').read_bytes())
        self.assertEqual('update',self.manager.selection()[1]['selected']['slot'])
        self.assertTrue(list((self.home.root/'operations').glob('update-entry-*/completed.json')))
    def test_release_status_returns_receipt_and_activation_evidence(self):
        self.update_fixture()
        from colvia.updates.release import inspect_release
        before=inspect_release(self.home,'update');self.assertEqual(self.preview['receipt'],before['receipt'])
        self.assertEqual('prepared',before['state']);self.apply()
        after=inspect_release(self.home,'update');self.assertEqual('updated',after['state']);self.assertEqual(1,len(after['activations']))
    def test_both_aliases_updated_originals_retained_no_other_files(self):
        self.update_fixture();self.apply()
        for n in ('colvia','colvia-manage'):self.assertEqual(self.content['bin/colvia'],(self.home.root/'bin'/n).read_bytes())
        originals=list((self.home.root/'operations/update-entry').rglob('*.original'))
        self.assertEqual(2,len(originals));self.assertTrue(all(p.read_bytes()==self.original for p in originals))
        self.assertFalse((self.home.root/'native-update.json').exists());self.assertEqual('update',self.manager.selection()[1]['selected']['slot'])
    def test_partial_alias_update_requires_explicit_exact_resume(self):
        self.update_fixture()
        def stop(phase):
            if phase=='native-entry-after-evacuate':raise RuntimeError('synthetic stop')
        with self.assertRaisesRegex(RuntimeError,'synthetic stop'):self.apply(checkpoint=stop)
        self.assertEqual(self.before,self.manager.selection()[0]);self.assertTrue((self.home.root/'native-update.json').exists())
        with self.assertRaisesRegex(RecordError,'native-entry-update-pending'):self.updater.prepare(operation='other',target='release.zip')
        self.assertEqual('updated',self.resume()['state']);self.assertFalse((self.home.root/'native-update.json').exists())
        self.assertEqual(self.content['bin/colvia'],(self.home.root/'bin/colvia').read_bytes())
        self.assertTrue((self.home.root/'backups/update-activate').exists())
    def test_changed_alias_refuses_before_live_mutation(self):
        self.update_fixture();(self.home.root/'bin/colvia-manage').write_bytes(b'foreign edit')
        with self.assertRaisesRegex(RecordError,'native-entry-changed'):self.apply()
        self.assertEqual(self.before,self.manager.selection()[0]);self.assertEqual(self.original,(self.home.root/'bin/colvia').read_bytes())
    def test_post_activation_interruption_only_finishes_pending_barrier(self):
        self.update_fixture()
        def stop(phase):
            if phase=='activated':raise RuntimeError('synthetic stop')
        with self.assertRaises(RuntimeError):self.apply(checkpoint=stop)
        self.assertEqual('update',self.manager.selection()[1]['selected']['slot']);self.assertTrue((self.home.root/'native-update.json').exists())
        backups=list((self.home.root/'backups').iterdir());self.resume()
        self.assertEqual(backups,list((self.home.root/'backups').iterdir()));self.assertFalse((self.home.root/'native-update.json').exists())
    def test_expiry_during_partial_update_blocks_resume_preserves_bytes(self):
        self.update_fixture()
        def stop(phase):
            if phase=='native-entry-after-install':raise RuntimeError('synthetic stop')
        with self.assertRaises(RuntimeError):self.apply(checkpoint=stop)
        self.trust.expired=True
        with self.assertRaisesRegex(RecordError,'preparation-expired'):self.resume()
        self.assertEqual(self.before,self.manager.selection()[0]);self.assertTrue((self.home.root/'native-update.json').exists())
    def test_competing_file_at_evacuated_name_is_not_overwritten(self):
        self.update_fixture()
        def stop(phase):
            if phase=='native-entry-after-evacuate':raise RuntimeError('synthetic stop')
        with self.assertRaises(RuntimeError):self.apply(checkpoint=stop)
        (self.home.root/'bin/colvia').write_bytes(b'competing entry')
        with self.assertRaisesRegex(RecordError,'effect-path-unknown'):self.resume()
        self.assertEqual(b'competing entry',(self.home.root/'bin/colvia').read_bytes());self.assertEqual(self.before,self.manager.selection()[0])

if __name__=='__main__':unittest.main()
