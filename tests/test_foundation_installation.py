"""First-install composition uses a named verifier double, never a real install.

No process, network request, OS permission or signing key is created by these
fixtures. Real signatures are covered separately by the fixed TUF input.
"""
import hashlib,os,unittest
from pathlib import Path
from unittest.mock import patch
from colvia.codec import RecordError,canonical_bytes
from colvia.management import ManagerHome
from colvia.updates.installation import FirstInstall,bootstrap,existing_manager
import test_foundation_package as package_fixture
import test_foundation_slots as slot_fixture
from test_foundation_release_update import DownloadDouble

class InstallationTests(unittest.TestCase):
    archive=package_fixture.PackageTests.archive
    slot=slot_fixture.SlotTests.slot
    tearDown=package_fixture.PackageTests.tearDown
    def setUp(self):
        package_fixture.PackageTests.setUp(self)
        self.config=dict(version=1,channel='preview',metadata_url='https://updates.example.invalid/metadata/',target_url='https://updates.example.invalid/targets/',
            target='release.zip',anchor='root.json',native_entry='bin/colvia')
        self.content.update({'installation.json':canonical_bytes(self.config),'root.json':b'fixture anchor not used as real signature',
                             'bin/colvia':b'fixture native entry never executed'})
        self.manifest['inventory']=[dict(path=p,kind='regular',mode='100755' if p.startswith('bin/') else '100644',size=len(b),
            sha256=hashlib.sha256(b).hexdigest()) for p,b in sorted(self.content.items())]
        archive,target=self.archive();target['path']=self.config['target'];self.trust=DownloadDouble(archive,target)
        self.home=ManagerHome.create(self.base/'home',os_name='macos',architecture='arm64');self.manager=self.home.slots
    def install(self,**kwargs):return FirstInstall(self.home,self.trust,self.config).perform(operation='first',**kwargs)
    def test_first_install_selects_only_complete_verified_runtime(self):
        result=self.install();self.assertEqual('installed',result['state']);self.assertTrue(result['project_connection_required'])
        self.assertEqual('first',self.manager.selection()[1]['selected']['slot'])
        self.assertEqual(self.content['bin/colvia'],(self.home.root/'bin/colvia').read_bytes())
        self.assertEqual((self.home.root/'bin/colvia').read_bytes(),(self.home.root/'bin/colvia-manage').read_bytes())
        self.assertTrue((self.home.root/'operations/first/completed.json').is_file());self.assertEqual((),self.home.projects())
    def test_expired_after_entry_preparation_does_not_activate(self):
        def expire(phase):
            if phase=='entry-prepared':self.trust.expired=True
        with self.assertRaisesRegex(RecordError,'preparation-expired'):self.install(checkpoint=expire)
        self.assertFalse((self.manager.root/'runtime.json').exists());self.assertTrue((self.home.root/'entry.json').is_file())
        with self.assertRaisesRegex(RecordError,'repair-required'):existing_manager(self.home.root,os_name='macos',architecture='arm64')
    def test_changed_manager_alias_does_not_activate(self):
        def alter(phase):
            if phase=='entry-prepared':(self.home.root/'bin/colvia-manage').write_bytes(b'changed')
        with self.assertRaisesRegex(RecordError,'native-entry-changed'):self.install(checkpoint=alter)
        self.assertFalse((self.manager.root/'runtime.json').exists())

    def test_prepared_resume_reuses_exact_entries_without_redownload(self):
        def stop(phase):
            if phase=='entry-prepared':raise RuntimeError('simulated stop')
        with self.assertRaisesRegex(RuntimeError,'simulated stop'):self.install(checkpoint=stop)
        original=(self.home.root/'bin/colvia').stat().st_ino
        with patch.object(self.trust,'stage',side_effect=AssertionError('no redownload')):
            result=FirstInstall(self.home,self.trust,self.config).resume(operation='first')
        self.assertEqual('installed',result['state']);self.assertEqual(original,(self.home.root/'bin/colvia').stat().st_ino)
    def test_resume_after_activation_before_completion_is_exact(self):
        def stop(phase):
            if phase=='activated':raise RuntimeError('simulated stop')
        with self.assertRaisesRegex(RuntimeError,'simulated stop'):self.install(checkpoint=stop)
        before=self.manager.selection()[0]
        FirstInstall(self.home,self.trust,self.config).resume(operation='first')
        self.assertEqual(before,self.manager.selection()[0]);self.assertTrue((self.home.root/'operations/first/completed.json').exists())
    def test_resume_refuses_expired_or_changed_entries_without_erasing(self):
        def stop(phase):
            if phase=='entry-prepared':raise RuntimeError('simulated stop')
        with self.assertRaises(RuntimeError):self.install(checkpoint=stop)
        self.trust.expired=True
        with self.assertRaisesRegex(RecordError,'preparation-expired'):FirstInstall(self.home,self.trust,self.config).resume(operation='first')
        self.trust.expired=False;entry=self.home.root/'bin/colvia';entry.write_bytes(b'partial')
        with self.assertRaisesRegex(RecordError,'native-entry-changed'):FirstInstall(self.home,self.trust,self.config).resume(operation='first')
        self.assertEqual(b'partial',entry.read_bytes());self.assertFalse((self.manager.root/'runtime.json').exists())

    def test_resume_cross_checks_signed_descriptor_with_prepared_slot(self):
        import json
        def stop(phase):
            if phase=='entry-prepared':raise RuntimeError('simulated stop')
        with self.assertRaises(RuntimeError):self.install(checkpoint=stop)
        path=self.home.root/'operations/first/prepared.json';value=json.loads(path.read_text())
        value['download']['custom']['colvia']['manifest_sha256']='0'*64;path.write_bytes(canonical_bytes(value))
        with self.assertRaisesRegex(RecordError,'release-description-changed'):
            FirstInstall(self.home,self.trust,self.config).resume(operation='first')
        self.assertFalse((self.manager.root/'runtime.json').exists())

    def test_signed_release_cannot_redirect_bootstrap_channel(self):
        config=dict(self.config,target='different.zip')
        with self.assertRaisesRegex(RecordError,'channel-changed'):FirstInstall(self.home,self.trust,config).perform(operation='first')
        self.assertFalse((self.manager.root/'runtime.json').exists());self.assertFalse((self.home.root/'bin').exists())
    def test_existing_install_uses_own_manager_without_importing_new_bootstrap(self):
        self.install();commands=[]
        with patch('colvia.updates.installation.current_platform',return_value=('macos','arm64')):
            bootstrap(self.home.root,self.base/'untrusted-absent-stage','0'*64,launch=lambda file,args:commands.append((file,args)))
        self.assertEqual(1,len(commands));self.assertEqual('update',commands[0][1][-1])
        self.assertIn(str(self.manager.root/'slots/first/manager.py'),commands[0][1])
        self.assertNotIn('untrusted-absent-stage',' '.join(commands[0][1]))
    def test_partial_home_never_treated_as_fresh_or_overwritten(self):
        before=(self.home.root/'home.json').read_bytes();calls=[]
        with patch('colvia.updates.installation.current_platform',return_value=('macos','arm64')),self.assertRaisesRegex(RecordError,'repair-required'):
            bootstrap(self.home.root,self.base/'ignored','0'*64,launch=lambda *args:calls.append(args))
        self.assertEqual([],calls);self.assertEqual(before,(self.home.root/'home.json').read_bytes())
    def test_resume_requires_verified_bootstrap_before_opening_existing_home(self):
        before=(self.home.root/'home.json').read_bytes();stage=self.base/'stage';stage.mkdir(mode=0o700)
        (stage/'manifest.json').write_bytes(b'wrong')
        with patch('colvia.updates.installation.current_platform',return_value=('macos','arm64')),self.assertRaisesRegex(RecordError,'manifest-mismatch'):
            bootstrap(self.home.root,stage,'0'*64,resume_operation='first')
        self.assertEqual(before,(self.home.root/'home.json').read_bytes())

    def test_unverified_stage_refuses_before_home_creation(self):
        stage=self.base/'stage';stage.mkdir(mode=0o700);(stage/'manifest.json').write_bytes(b'wrong')
        target=self.base/'absent-home'
        with patch('colvia.updates.installation.current_platform',return_value=('macos','arm64')),self.assertRaisesRegex(RecordError,'manifest-mismatch'):
            bootstrap(target,stage,'0'*64)
        self.assertFalse(target.exists())

if __name__=='__main__':unittest.main()
