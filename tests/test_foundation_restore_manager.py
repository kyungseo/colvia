from contextlib import contextmanager
import unittest
from unittest.mock import patch
from colvia.codec import RecordError
from colvia.backup_service import export_backup
from colvia.graph import AuditBudget
from colvia.records import application_registry
from colvia.restore_manager import RestoreManager
from colvia.configuration import Configuration
import test_foundation_management as fixture

class RestoreManagerTests(unittest.TestCase):
    slot=fixture.ManagementTests.slot
    setUp=fixture.ManagementTests.setUp
    tearDown=fixture.ManagementTests.tearDown
    def saved(self):
        scratch=self.base/'scratch';scratch.mkdir();out=self.base/'saved.export'
        export_backup(self.authority,destination=out,scratch=scratch,operation='save',graph_budget=AuditBudget(10000,20000,32*1024**2),registry=application_registry())
        return out
    def change(self):
        store=self.authority.store()
        try:
            config=Configuration(store);p=config.preview([]);config.apply(operation='later',features=[],receipt=p['receipt'],statement='변경')
            return store.root().ref
        finally:store.close()
    def test_restore_keeps_later_history_and_requires_project_rebind(self):
        out=self.saved();later=self.change();service=RestoreManager(self.home)
        preview=service.prepare(operation='restore',archive=out);before=self.authority.pointer_value()
        self.assertEqual('not-activated',service.inspect('restore')['state']);self.assertEqual(before,self.authority.pointer_value())
        result=service.apply(operation='restore',receipt=preview['receipt']);self.assertEqual('restored-needs-rebind',result['state'])
        self.assertFalse(result['workspace_files_changed']);self.assertNotEqual(before,self.authority.pointer_value())
        active=self.authority.store()
        try:self.assertEqual(self.root,active.root().ref);self.assertTrue(active.needs_rebind())
        finally:active.close()
        historical=self.authority.historical_store('restore-switch')
        try:self.assertEqual(later,historical.root().ref)
        finally:historical.close()
        self.assertTrue((self.home.root/'backups/restore.colvia-export').is_file())
    def test_later_decision_invalidates_restore_preview(self):
        service=RestoreManager(self.home);preview=service.prepare(operation='restore',archive=self.saved());self.change()
        with self.assertRaisesRegex(RecordError,'source-changed'):service.apply(operation='restore',receipt=preview['receipt'])
        self.assertEqual('not-activated',service.inspect('restore')['state'])
    def test_truncated_backup_does_not_create_authority_candidate(self):
        out=self.saved();out.write_bytes(out.read_bytes()[:-10]);before=self.authority.pointer_value()
        with self.assertRaises(RecordError):RestoreManager(self.home).prepare(operation='broken',archive=out)
        self.assertEqual(before,self.authority.pointer_value());self.assertFalse((self.authority.root/'stores/restore-broken').exists())
    def test_restore_waits_for_final_archive_check_before_publishing_candidate(self):
        archive=self.saved()
        read_stream=self.home.files.read_stream

        @contextmanager
        def refused_on_exit(path,limit):
            with read_stream(path,limit) as stream:
                yield stream
            raise RecordError('lifecycle-file-changed')

        before=self.authority.pointer_value()
        with patch.object(self.home.files,'read_stream',refused_on_exit):
            with self.assertRaisesRegex(RecordError,'lifecycle-file-changed'):
                RestoreManager(self.home).prepare(operation='changed-archive',archive=archive)
        self.assertEqual(before,self.authority.pointer_value())
        self.assertFalse((self.authority.root/'stores/restore-changed-archive').exists())
        self.assertFalse((self.home.root/'operations/changed-archive/restore.json').exists())

    def test_interruption_after_fence_is_reported_without_automatic_reexecution(self):
        service=RestoreManager(self.home);preview=service.prepare(operation='restore',archive=self.saved())
        def stop(phase):
            if phase=='fenced':raise RuntimeError('synthetic stop')
        with self.assertRaises(RuntimeError):service.apply(operation='restore',receipt=preview['receipt'],checkpoint=stop)
        self.assertEqual('recovery-required',service.inspect('restore')['state'])
        self.assertEqual('restored-needs-rebind',service.resume(operation='restore',receipt=preview['receipt'])['state'])
        self.assertEqual('restored-needs-rebind',service.resume(operation='restore',receipt=preview['receipt'])['state'])
        self.assertTrue((self.home.root/'backups/restore.colvia-export').is_file())

if __name__=='__main__':unittest.main()
