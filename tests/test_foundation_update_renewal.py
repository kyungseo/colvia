"""Recovery composition doubles; fixed signed metadata lives in TrustTests."""
import copy,hashlib,unittest
from unittest.mock import patch
from colvia.codec import RecordError,canonical_bytes
from colvia.updates.installation import FirstInstall
from colvia.updates.reauthentication import effective
import test_foundation_release_update as release_fixture
import test_foundation_installation as install_fixture

class RenewalTests(unittest.TestCase):
    setUp=release_fixture.ReleaseUpdateTests.setUp
    tearDown=release_fixture.ReleaseUpdateTests.tearDown
    archive=release_fixture.ReleaseUpdateTests.archive
    slot=release_fixture.ReleaseUpdateTests.slot
    def prepare(self,name='update'):
        self.trust.target['path']='release.zip'
        return self.updater.prepare(operation=name,target='release.zip')
    def test_renewal_preserves_plan_and_does_not_download_or_select(self):
        preview=self.prepare();area=self.home.root/'operations/update'
        original=(area/'release.json').read_bytes();selection=self.manager.selection()[0]
        self.trust.expired=True
        with self.assertRaisesRegex(RecordError,'expired'):self.updater.resume(operation='update',receipt=preview['receipt'])
        self.trust.expired=False
        renewal=self.updater.refresh(operation='update',receipt=preview['receipt'],renewal='fresh')
        self.assertEqual(original,(area/'release.json').read_bytes());self.assertEqual(selection,self.manager.selection()[0])
        self.assertFalse((area/'renewal-fresh/never-download').exists())
        result=self.updater.resume(operation='update',receipt=preview['receipt'],renewal=renewal['renewal'])
        self.assertEqual('updated',result['state']);self.assertEqual(2,self.trust.calls)
    def test_selected_release_finishes_without_refreshing_retired_target(self):
        preview=self.prepare()
        def stop(phase):
            if phase=='activated':raise RuntimeError('lost activation ack')
        with self.assertRaises(RuntimeError):self.updater.apply(operation='update',receipt=preview['receipt'],checkpoint=stop)
        self.trust.expired=True;self.trust.target=dict(self.trust.target,sha256='0'*64);calls=self.trust.calls
        self.assertEqual('updated',self.updater.resume(operation='update',receipt=preview['receipt'])['state'])
        self.assertEqual(calls,self.trust.calls)
    def test_changed_target_never_fetches_or_writes_a_renewal(self):
        preview=self.prepare();original=copy.deepcopy(self.trust.target)
        for i,(key,value) in enumerate((('path','else.zip'),('sha256','0'*64),('length',1),('custom',{'new':True}))):
            self.trust.target=dict(original,**{key:value})
            with self.assertRaisesRegex(RecordError,'renewal-target-changed'):
                self.updater.refresh(operation='update',receipt=preview['receipt'],renewal='bad-'+str(i))
            area=self.home.root/'operations/update'/('renewal-bad-'+str(i))
            self.assertTrue((area/'intent.json').exists());self.assertFalse((area/'renewed.json').exists())
            self.assertFalse((area/'never-download').exists())
    def test_wrong_preparation_or_renewal_receipt_refuses(self):
        preview=self.prepare();renewal=self.updater.refresh(operation='update',receipt=preview['receipt'],renewal='fresh')
        plan,_=self.updater._read('update')
        with self.assertRaisesRegex(RecordError,'preparation-mismatch'):
            effective(self.home,self.trust,operation='update',original='0'*64,download=plan['download'],renewal=renewal['renewal'])
        with self.assertRaisesRegex(RecordError,'receipt-changed'):
            self.updater.resume(operation='update',receipt=preview['receipt'],renewal='fresh@'+'0'*64)
        with self.assertRaisesRegex(RecordError,'review-changed'):
            self.updater.refresh(operation='update',receipt='wrong',renewal='another')
    def test_rollback_between_resume_locks_blocks_live_activation(self):
        preview=self.prepare();before=self.manager.selection()[0];advance=self.home.update
        def race(**kwargs):
            self.home.files.create(self.home.root/'operations/update/rollback.json',canonical_bytes({'version':1}))
            return advance(**kwargs)
        with patch.object(self.home,'update',side_effect=race),self.assertRaisesRegex(RecordError,'rollback-started'):
            self.updater.resume(operation='update',receipt=preview['receipt'])
        self.assertEqual(before,self.manager.selection()[0])
        with self.assertRaisesRegex(RecordError,'rollback-started'):
            self.updater.refresh(operation='update',receipt=preview['receipt'],renewal='fresh')
        with self.assertRaisesRegex(RecordError,'rollback-started'):
            self.updater.apply(operation='update',receipt=preview['receipt'])

class FirstRenewalTests(unittest.TestCase):
    setUp=install_fixture.InstallationTests.setUp
    tearDown=install_fixture.InstallationTests.tearDown
    archive=install_fixture.InstallationTests.archive
    slot=install_fixture.InstallationTests.slot
    def test_partial_first_install_with_retired_target_stays_blocked_and_preserved(self):
        service=FirstInstall(self.home,self.trust,self.config)
        def stop(phase):
            if phase=='entry-prepared':raise RuntimeError('synthetic interruption')
        with self.assertRaises(RuntimeError):service.perform(operation='first',checkpoint=stop)
        f=self.home.files;anchor=self.content['root.json'];anchor_hash=hashlib.sha256(anchor).hexdigest()
        saved={k:self.config[k] for k in ('version','channel','metadata_url','target_url','target')}
        f.create(self.home.root/'initial-install.json',canonical_bytes(dict(version=1,operation='first',final_root=str(self.home.root),
            identity=f.directory_identity(self.home.root),payload_sha256='0'*64,config=saved,anchor_sha256=anchor_hash)))
        self.trust.state=lambda:(b'unchanged fixture trust',dict(anchor_sha256=anchor_hash))
        tracked={p:p.read_bytes() for p in self.home.root.rglob('*') if p.is_file()}
        self.trust.expired=True;self.trust.target=dict(self.trust.target,sha256='0'*64)
        with self.assertRaisesRegex(RecordError,'expired'):service.resume(operation='first')
        receipt=hashlib.sha256((self.home.root/'operations/first/prepared.json').read_bytes()).hexdigest()
        with self.assertRaisesRegex(RecordError,'renewal-target-changed'):
            service.refresh(operation='first',receipt=receipt,renewal='retired')
        with self.assertRaisesRegex(RecordError,'live-effects'):
            service.perform(operation='second',retry_of='first',anchor=anchor)
        self.assertFalse((self.manager.root/'runtime.json').exists());self.assertFalse((self.home.root/'operations/second').exists())
        for path,raw in tracked.items():self.assertEqual(raw,path.read_bytes())
        self.assertTrue(service.status(anchor=anchor)['live_files_present'])

    def test_superseded_prepared_first_attempt_cannot_resume(self):
        service=FirstInstall(self.home,self.trust,self.config)
        def stop(phase):
            if phase=='entry-prepared':raise RuntimeError('synthetic stop')
        with self.assertRaises(RuntimeError):service.perform(operation='first',checkpoint=stop)
        self.home.files.create(self.home.root/'operations/first/retried-by.json',canonical_bytes(dict(version=1,previous='first',next='second')))
        with self.assertRaisesRegex(RecordError,'superseded'):service.resume(operation='first')

    def test_selected_first_install_only_completes_matching_files_after_expiry(self):
        service=FirstInstall(self.home,self.trust,self.config)
        def stop(phase):
            if phase=='activated':raise RuntimeError('lost activation ack')
        with self.assertRaises(RuntimeError):service.perform(operation='first',checkpoint=stop)
        self.trust.expired=True;calls=self.trust.calls
        self.assertEqual('installed',service.resume(operation='first')['state']);self.assertEqual(calls,self.trust.calls)
        (self.home.root/'bin/colvia').write_bytes(b'foreign edit')
        with self.assertRaisesRegex(RecordError,'native-entry-changed'):service.resume(operation='first')
    def test_prepared_first_install_can_renew_and_resume_without_another_payload(self):
        service=FirstInstall(self.home,self.trust,self.config)
        def expire(phase):
            if phase=='entry-prepared':self.trust.expired=True
        with self.assertRaisesRegex(RecordError,'expired'):service.perform(operation='first',checkpoint=expire)
        area=self.home.root/'operations/first';original=(area/'prepared.json').read_bytes()
        self.trust.expired=False
        renewal=service.refresh(operation='first',receipt=hashlib.sha256(original).hexdigest(),renewal='fresh')
        self.assertFalse((area/'renewal-fresh/never-download').exists())
        self.assertEqual('installed',service.resume(operation='first',renewal=renewal['renewal'])['state'])
        self.assertEqual(original,(area/'prepared.json').read_bytes());self.assertEqual(2,self.trust.calls)
