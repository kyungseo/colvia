"""Composition oracle with an explicit download double; not signature evidence.

Real pinned-TUF signature/expiry checks have their separate fixed signed fixture.
No signature or key is generated to make a package fixture appear authenticated.
"""
import hashlib,shutil,tempfile,unittest
from pathlib import Path
from colvia.codec import RecordError,require
from colvia.management import ManagerHome
from colvia.updates.release import ReleaseUpdate
from colvia.updates.slots import pointer
import test_foundation_package as package_fixture
import test_foundation_slots as slot_fixture

class DownloadDouble:
    def __init__(self,archive,target):self.archive=archive;self.target=target;self.expired=False;self.calls=0
    def stage(self,target,*,destination,cancelled,already_present=lambda _:False):
        self.calls+=1;require(not cancelled(),'update-cancelled')
        if already_present(self.target):return dict(self.target,staged=None,synthetic_verifier_double=True)
        shutil.copyfile(self.archive,destination)
        return dict(self.target,staged=str(destination),synthetic_verifier_double=True)
    def activation_check(self,download):require(not self.expired,'update-preparation-expired')

class ReleaseUpdateTests(unittest.TestCase):
    archive=package_fixture.PackageTests.archive
    slot=slot_fixture.SlotTests.slot
    def setUp(self):
        package_fixture.PackageTests.setUp(self)
        self.home=ManagerHome.create(self.base/'home',os_name='macos',architecture='arm64');self.manager=self.home.slots
        self.old=self.slot('old',1);self.manager.initialize(self.old)
        self.manifest['sequence']=2;archive,target=self.archive();target['custom']['colvia']['sequence']=2
        self.trust=DownloadDouble(archive,target);self.updater=ReleaseUpdate(self.home,self.trust,channel='preview')
    tearDown=package_fixture.PackageTests.tearDown
    def test_preparation_does_not_activate_then_one_apply_switches_runtime(self):
        before=self.manager.selection()[0];preview=self.updater.prepare(operation='update',target='release.zip')
        self.assertEqual(before,self.manager.selection()[0]);self.assertEqual(1,self.trust.calls)
        result=self.updater.apply(operation='update',receipt=preview['receipt'])
        self.assertEqual('updated',result['state']);self.assertEqual('update',self.manager.selection()[1]['selected']['slot'])
        self.assertEqual(self.old,self.manager.selection()[1]['recovery']);self.assertEqual(1,self.trust.calls)
    def test_authenticated_replacement_stages_fresh_copy_and_keeps_old_bytes(self):
        (self.home.slots.root/'slots/old/python').write_bytes(b'broken')
        updater=ReleaseUpdate(self.home,self.trust,channel='preview',replacement=True)
        preview=updater.prepare(operation='repair',target='release.zip')
        self.assertEqual('prepared',preview['state'])
        result=updater.apply(operation='repair',receipt=preview['receipt'])
        self.assertTrue(result['records_preserved']);self.assertTrue(result['settings_preserved'])
        self.assertEqual('repair',self.home.slots.selection()[1]['selected']['slot'])
        self.assertEqual(b'broken',(self.home.slots.root/'slots/old/python').read_bytes())
        self.assertTrue((self.home.root/'backups/repair-activate').is_dir())
    def test_repair_can_resume_exact_prepared_target_after_backup_interruption(self):
        (self.home.slots.root/'slots/old/python').write_bytes(b'broken')
        service=ReleaseUpdate(self.home,self.trust,channel='preview',replacement=True)
        preview=service.prepare(operation='repair',target='release.zip');calls=self.trust.calls
        def stop(phase):
            if phase=='backed-up':raise RuntimeError('synthetic repair interruption')
        with self.assertRaises(RuntimeError):service.apply(operation='repair',receipt=preview['receipt'],checkpoint=stop)
        self.assertEqual('updated',service.resume(operation='repair',receipt=preview['receipt'])['state'])
        self.assertEqual(calls,self.trust.calls);self.assertEqual(b'broken',(self.home.slots.root/'slots/old/python').read_bytes())
        self.assertTrue((self.home.root/'operations/repair-activate/intent.json').exists())
    def test_replacement_request_does_not_redownload_a_healthy_install(self):
        updater=ReleaseUpdate(self.home,self.trust,channel='preview',replacement=True)
        with self.assertRaisesRegex(RecordError,'replacement-not-required'):updater.prepare(operation='repair',target='release.zip')
        self.assertEqual(0,self.trust.calls)

    def test_expiry_during_backup_blocks_activation(self):
        preview=self.updater.prepare(operation='update',target='release.zip');before=self.manager.selection()[0]
        def expire(phase):
            if phase=='backed-up':self.trust.expired=True
        with self.assertRaisesRegex(RecordError,'preparation-expired'):
            self.updater.apply(operation='update',receipt=preview['receipt'],checkpoint=expire)
        self.assertEqual(before,self.manager.selection()[0]);self.assertTrue((self.home.root/'operations/update-activate/prepared.json').is_file())
    def test_same_signed_release_is_current_without_switch_or_backup(self):
        first=self.updater.prepare(operation='first-update',target='release.zip');self.updater.apply(operation='first-update',receipt=first['receipt'])
        selected=self.manager.selection()[0]
        again=self.updater.prepare(operation='again',target='release.zip');self.assertEqual('current',again['state'])
        result=self.updater.apply(operation='again',receipt=again['receipt'])
        self.assertEqual('current',result['state']);self.assertEqual(selected,self.manager.selection()[0])
        self.assertFalse((self.home.root/'backups/again-activate').exists())
        self.assertFalse((self.manager.root/'slots/again').exists())
        self.assertFalse((self.home.root/'operations/again/release.zip').exists())

    def test_wrong_receipt_and_changed_selection_refuse(self):
        preview=self.updater.prepare(operation='update',target='release.zip');before=self.manager.selection()[0]
        with self.assertRaisesRegex(RecordError,'review-changed'):self.updater.apply(operation='update',receipt='wrong')
        new=self.slot('other',3);self.manager.activate(new,expected_selection=before,read_requirements=[])
        with self.assertRaisesRegex(RecordError,'selection-changed'):self.updater.apply(operation='update',receipt=preview['receipt'])
        self.assertEqual(new,self.manager.selection()[1]['selected'])

if __name__=='__main__':unittest.main()
