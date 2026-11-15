"""Inert APFS alias/app recovery; no actual install, runtime or notification."""
import unittest
from colvia.codec import RecordError
from colvia.updates.release import ReleaseUpdate,inspect_release
import test_foundation_native_entry_update as native_fixture
import test_foundation_notice_app as app_fixture

class WindowsRollbackOrderTests(unittest.TestCase):
    def test_reversed_native_journal_has_no_authority(self):
        from pathlib import Path
        from types import SimpleNamespace
        from unittest.mock import patch
        from colvia.codec import canonical_bytes
        from colvia.updates.rollback import ReleaseRollback

        home=Path('/synthetic-manager')
        area=home/'operations/entry'
        pending=home/'native-update.json'
        rows=[dict(path=name,size=1) for name in ('colvia.exe','colvia-manage.exe')]
        components=dict(name='entry',forward=SimpleNamespace(pending=pending,area=area,
                        pending_token=lambda: b'journal-token'),old=rows,new=rows,
                        before=b'before',after=b'after',description='entry.json')
        items=[dict(path=row['path'],pre=row,post=row) for row in rows]
        prepared=dict(version=1,target='current',before='before',after='after',effects=dict(items=items))
        manifest=area/'prepared.json'
        contents={pending:b'journal-token',manifest:canonical_bytes(prepared),home/'entry.json':b'before'}
        files=SimpleNamespace(exists=lambda path: path in contents,read=lambda path,*_:contents[path])
        service=ReleaseRollback(SimpleNamespace(home=SimpleNamespace(root=home,files=files)))
        with patch.object(service,'components',side_effect=lambda _: [components.copy()]):
            self.assertEqual(items,service.bind(dict(target='current'))[0]['manifest']['items'])
            prepared['effects']['items']=list(reversed(items))
            contents[manifest]=canonical_bytes(prepared)
            with self.assertRaisesRegex(RecordError,'rollback-effects-not-authenticated'):
                service.bind(dict(target='current'))


class RollbackTests(unittest.TestCase):
    setUp=native_fixture.NativeEntryTests.setUp
    tearDown=native_fixture.NativeEntryTests.tearDown
    archive=native_fixture.NativeEntryTests.archive
    slot=native_fixture.NativeEntryTests.slot
    install=native_fixture.NativeEntryTests.install
    update_fixture=native_fixture.NativeEntryTests.update_fixture
    apply=native_fixture.NativeEntryTests.apply
    def interrupt(self,phase):
        self.update_fixture()
        def stop(current):
            if current==phase:raise RuntimeError('synthetic forward interruption')
        with self.assertRaises(RuntimeError):self.apply(checkpoint=stop)
        self.trust.expired=True # Restoring the authenticated old runtime needs no new target trust.
    def preview_rollback(self):return self.updater.rollback_preview(operation='update',receipt=self.preview['receipt'])
    def rollback(self,preview,**kwargs):return self.updater.rollback(operation='update',receipt=self.preview['receipt'],rollback_receipt=preview['rollback_receipt'],**kwargs)
    def test_partial_post_restore_preserves_original_and_blocks_old_receipt(self):
        self.interrupt('native-entry-after-install');preview=self.preview_rollback();calls=self.trust.calls
        result=self.rollback(preview);self.assertEqual('rolled-back',result['state']);self.assertEqual(calls,self.trust.calls)
        self.assertEqual(self.before,self.manager.selection()[0])
        self.assertTrue(all((self.home.root/'bin'/n).read_bytes()==self.original for n in ('colvia','colvia-manage')))
        self.assertFalse((self.home.root/'native-update.json').exists())
        self.assertEqual('rolled-back',inspect_release(self.home,'update')['state'])
        with self.assertRaisesRegex(RecordError,'rollback-started'):self.updater.resume(operation='update',receipt=self.preview['receipt'])
        self.assertEqual('rolled-back',self.rollback(preview)['state']) # lost response is exact completion only
        self.assertTrue(list((self.home.root/'operations/update-entry').rglob('*.original')))
    def test_evacuated_alias_restores_absence_without_overwrite(self):
        self.interrupt('native-entry-after-evacuate');self.assertFalse((self.home.root/'bin/colvia').exists())
        self.rollback(self.preview_rollback());self.assertEqual(self.original,(self.home.root/'bin/colvia').read_bytes())
    def test_foreign_live_entry_or_modified_retained_original_refuses(self):
        self.interrupt('native-entry-after-install');preview=self.preview_rollback()
        (self.home.root/'bin/colvia').write_bytes(b'foreign')
        with self.assertRaisesRegex(RecordError,'effect-path-unknown'):self.rollback(preview)
        self.assertEqual(b'foreign',(self.home.root/'bin/colvia').read_bytes());self.assertEqual(self.before,self.manager.selection()[0])
        self.assertFalse((self.home.root/'operations/update/rollback.json').exists())
    def test_changed_retained_original_before_apply_does_not_latch_rollback(self):
        self.interrupt('native-entry-after-install');preview=self.preview_rollback()
        original=next((self.home.root/'operations/update-entry').rglob('*.original'));original.write_bytes(b'late write')
        with self.assertRaisesRegex(RecordError,'rollback-original-changed'):self.rollback(preview)
        self.assertFalse((self.home.root/'operations/update/rollback.json').exists())
    def test_later_update_pending_does_not_change_completed_rollback_status(self):
        from colvia.codec import canonical_bytes
        self.interrupt('native-entry-after-install');self.rollback(self.preview_rollback())
        self.home.files.create(self.home.root/'native-update.json',canonical_bytes(dict(operation='later')))
        status=inspect_release(self.home,'update');self.assertEqual('rolled-back',status['state']);self.assertFalse(status['native_pending'])
        self.assertTrue(status['other_or_changed_pending'])

    def test_reverse_interruption_resumes_exact_staged_original(self):
        self.interrupt('native-entry-after-install');preview=self.preview_rollback()
        def stop(phase):
            if phase=='rollback-after-evacuate':raise RuntimeError('synthetic reverse interruption')
        with self.assertRaises(RuntimeError):self.rollback(preview,checkpoint=stop)
        self.assertTrue((self.home.root/'native-update.json').exists())
        self.assertEqual('rolled-back',self.rollback(preview)['state'])
    def test_completion_before_marker_clear_is_recoverable(self):
        self.interrupt('native-entry-described');preview=self.preview_rollback()
        def stop(phase):
            if phase=='rollback-completed':raise RuntimeError('lost completion')
        with self.assertRaises(RuntimeError):self.rollback(preview,checkpoint=stop)
        self.assertTrue((self.home.root/'native-update.json').exists())
        self.rollback(preview);self.assertFalse((self.home.root/'native-update.json').exists())
    def test_reverse_staging_failure_preserves_orphan_and_starts_no_effect(self):
        from unittest.mock import patch
        self.interrupt('native-entry-after-install');preview=self.preview_rollback()
        path=self.home.root/'operations/update/rollback-prepared.json';create=self.home.files.create
        def stop(name,*args,**kwargs):
            if name==path:raise OSError('synthetic publication failure')
            return create(name,*args,**kwargs)
        with patch.object(self.home.files,'create',side_effect=stop),self.assertRaises(OSError):self.rollback(preview)
        orphans=list(path.parent.glob('reverse-*'));self.assertEqual(1,len(orphans))
        self.rollback(preview);self.assertTrue(orphans[0].is_dir());self.assertEqual(2,len(list(path.parent.glob('reverse-*'))))
    def test_changed_retained_original_blocks_rollback_after_reverse_prepared(self):
        self.interrupt('native-entry-after-install');preview=self.preview_rollback()
        def stop(phase):
            if phase=='rollback-prepared':raise RuntimeError('synthetic preparation stop')
        with self.assertRaises(RuntimeError):self.rollback(preview,checkpoint=stop)
        old=next((self.home.root/'operations/update-entry').rglob('*.original'));old.write_bytes(b'late original edit')
        with self.assertRaisesRegex(RecordError,'rollback-original-changed'):self.rollback(preview)
        self.assertEqual(b'late original edit',old.read_bytes())

    def test_activated_runtime_cannot_be_rolled_back_by_this_path(self):
        self.interrupt('activated')
        with self.assertRaisesRegex(RecordError,'selection-changed'):self.preview_rollback()
    def test_wrong_rollback_receipt_does_not_create_intent(self):
        self.interrupt('native-entry-after-install')
        with self.assertRaisesRegex(RecordError,'review-changed'):self.rollback({'rollback_receipt':'0'*64})
        self.assertFalse((self.home.root/'operations/update/rollback.json').exists())

class AppRollbackTests(unittest.TestCase):
    setUp=app_fixture.NoticeAppTests.setUp
    tearDown=app_fixture.NoticeAppTests.tearDown
    archive=app_fixture.NoticeAppTests.archive
    slot=app_fixture.NoticeAppTests.slot
    install=app_fixture.NoticeAppTests.install
    repack=app_fixture.NoticeAppTests.repack
    def test_partial_app_and_native_files_restore_together(self):
        self.install();before=self.manager.selection()[0]
        from colvia.updates.notice_app import PREFIX
        old=(self.home.root/'receiver.json').read_bytes();native=(self.home.root/'entry.json').read_bytes()
        self.content['bin/colvia']=b'new inert entry';self.content[PREFIX+'Contents/Resources/Colvia.icns']=b'new inert icon';self.repack(2)
        service=ReleaseUpdate(self.home,self.trust,channel='preview');preview=service.prepare(operation='update',target='release.zip')
        def stop(phase):
            if phase=='notice-app-after-install':raise RuntimeError('synthetic stop')
        with self.assertRaises(RuntimeError):service.apply(operation='update',receipt=preview['receipt'],checkpoint=stop)
        self.trust.expired=True
        from unittest.mock import patch
        from colvia.updates.rollback import ReleaseRollback
        rollback_service=ReleaseRollback(service);plan,_=service._read('update');components=rollback_service.components(plan)
        with patch.object(rollback_service,'components',return_value=[c for c in components if c['name']=='app']),self.assertRaisesRegex(RecordError,'other-pending'):
            rollback_service.bind(plan)
        rollback=service.rollback_preview(operation='update',receipt=preview['receipt'])
        service.rollback(operation='update',receipt=preview['receipt'],rollback_receipt=rollback['rollback_receipt'])
        self.assertEqual(before,self.manager.selection()[0]);self.assertEqual(old,(self.home.root/'receiver.json').read_bytes())
        self.assertEqual(native,(self.home.root/'entry.json').read_bytes());self.assertFalse((self.home.root/'notice-app.pending').exists())
