"""APFS app-file lifecycle with inert bodies; no codesign, launch or registration."""
import hashlib,plistlib,unittest
from types import SimpleNamespace
from colvia.codec import RecordError
from colvia.updates.notice_app import PREFIX,PARTS
from colvia.updates.release import ReleaseUpdate
from colvia.platforms.darwin_notices import DarwinNotices
import test_foundation_installation as fixture
from test_foundation_release_update import DownloadDouble

class NoticeAppTests(unittest.TestCase):
    archive=fixture.InstallationTests.archive
    slot=fixture.InstallationTests.slot
    install=fixture.InstallationTests.install
    tearDown=fixture.InstallationTests.tearDown
    def setUp(self):
        fixture.InstallationTests.setUp(self)
        for part in PARTS:self.content[PREFIX+part]=b'inert '+part.encode()
        self.content[PREFIX+'Contents/Info.plist']=plistlib.dumps(dict(CFBundleIdentifier='org.colvia.work.notice',CFBundleExecutable='ColviaWork',CFBundlePackageType='APPL',CFBundleVersion='3'))
        self.repack(1)
    def repack(self,sequence):
        self.manifest['sequence']=sequence
        self.manifest['inventory']=[dict(path=p,kind='regular',mode='100755' if p.startswith('bin/') or p.endswith('/MacOS/ColviaWork') else '100644',size=len(b),
            sha256=hashlib.sha256(b).hexdigest()) for p,b in sorted(self.content.items()) if p!='manifest.json']
        archive,target=self.archive();target['path']=self.config['target'];target['custom']['colvia']['sequence']=sequence;self.trust=DownloadDouble(archive,target)
    def test_unpublished_app_preparation_survives_first_install_resume(self):
        orphan=self.home.root/'operations/first-notice-app';orphan.mkdir(mode=0o700)
        (orphan/'partial').write_bytes(b'interrupted staging')
        self.install();self.assertEqual(b'interrupted staging',(orphan/'partial').read_bytes())
        self.assertTrue((self.home.root/'operations/first/publication.json').is_file())
    def test_first_install_stages_app_without_os_registration_or_consent(self):
        self.install();self.assertTrue((self.home.root/'bin/ColviaWork.app/Contents/Info.plist').is_file())
        self.assertFalse((self.home.root/'notice-choice.json').exists());self.assertFalse((self.home.root/'notice-app.pending').exists())
    def test_interrupted_first_app_publication_resumes_exact_prepared_install(self):
        def stop(phase):
            if phase=='initial-after-publish':raise RuntimeError('synthetic stop')
        with self.assertRaises(RuntimeError):self.install(checkpoint=stop)
        self.assertFalse((self.manager.root/'runtime.json').exists());self.assertTrue((self.home.root/'operations/first/publication.json').exists())
        from colvia.updates.installation import FirstInstall
        FirstInstall(self.home,self.trust,self.config).resume(operation='first')
        self.assertFalse((self.home.root/'notice-app.pending').exists())
    def test_update_retains_app_originals_and_does_not_register_or_send(self):
        self.install();old=(self.home.root/'bin/ColviaWork.app/Contents/Resources/Colvia.icns').read_bytes()
        self.content[PREFIX+'Contents/Resources/Colvia.icns']=b'new inert icon';self.repack(2)
        service=ReleaseUpdate(self.home,self.trust,channel='preview');preview=service.prepare(operation='update',target='release.zip')
        service.apply(operation='update',receipt=preview['receipt'])
        self.assertEqual(b'new inert icon',(self.home.root/'bin/ColviaWork.app/Contents/Resources/Colvia.icns').read_bytes())
        self.assertIn(old,[p.read_bytes() for p in (self.home.root/'operations/update-notice-app').rglob('*.original')])
        self.assertFalse((self.home.root/'notice-choice.json').exists())
    def test_receiver_uses_packaged_app_and_only_opaque_event_argument(self):
        self.install();calls=[]
        def runner(args,**kwargs):calls.append(args);return SimpleNamespace(code=0)
        port=DarwinNotices(self.home,runner=runner,root_provider=lambda:self.home.root)
        with self.assertRaisesRegex(RecordError,'registration-required'):port.check(port.receiver_identity)
        port.change(enable=True);port.check(port.receiver_identity);self.assertEqual('emitted',port.emit('a'*32))
        self.assertEqual([['--authorize'],['--check-receiver'],['--post','a'*32]],[row[1:] for row in calls])
        self.assertTrue(all(row[0].endswith('/ColviaWork.app/Contents/MacOS/ColviaWork') for row in calls))
        port.change(enable=False)
        with self.assertRaisesRegex(RecordError,'registration-required'):port.emit('b'*32)
        self.assertEqual(3,len(calls))
    def test_extra_app_file_blocks_emission_before_native_process(self):
        self.install();(self.home.root/'bin/ColviaWork.app/extra').write_bytes(b'foreign');calls=[]
        port=DarwinNotices(self.home,runner=lambda *a,**kw:calls.append(a),root_provider=lambda:self.home.root)
        with self.assertRaisesRegex(RecordError,'inventory-changed'):port.change(enable=True)
        self.assertEqual([],calls)

if __name__=='__main__':unittest.main()
