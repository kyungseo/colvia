"""Portable export protocol checks; explicitly not native Windows qualification."""
from contextlib import contextmanager
import os,shutil,unittest,json
from types import SimpleNamespace
from unittest.mock import patch
from colvia.codec import RecordError,require
from colvia.graph import AuditBudget
from colvia.windows_backup import export_backup
from colvia.storage.files import PosixFiles
from colvia.platforms.posix import open_directory
from colvia.platforms import exclusive
import test_foundation_backup_service as fixture


class DestinationDouble:
    """POSIX exclusive fixture provides the Windows protocol's interface only."""
    def __init__(self,parent):self.parent=parent;self.files=PosixFiles()
    def __enter__(self):return self
    def __exit__(self,*exc):pass
    def exists(self,name):return os.path.lexists(self.parent/name)
    def free_bytes(self):return shutil.disk_usage(self.parent).free
    def stamp(self,name):
        s=(self.parent/name).lstat()
        return dict(identity=(s.st_dev,s.st_ino),size=s.st_size,write=s.st_mtime_ns,change=s.st_ctime_ns)
    def create(self,name):return self.files.create_stream(self.parent/name)
    def read(self,name,limit):return self.files.read_stream(self.parent/name,limit)
    def publish(self,prepared,name,expected):
        require(self.stamp(prepared)==expected,'backup-file-changed')
        fd=open_directory(self.parent)
        try:exclusive.rename(fd,prepared,fd,name)
        finally:os.close(fd)


class WindowsBackupTests(unittest.TestCase):
    setUp=fixture.BackupServiceTests.setUp
    tearDown=fixture.BackupServiceTests.tearDown
    import_snapshot=fixture.BackupServiceTests.import_snapshot
    def export(self,**kwargs):
        return export_backup(self.authority,destination=self.destination,scratch=self.scratch,operation=kwargs.pop('operation','backup'),
            graph_budget=AuditBudget(10000,10000,32*1024*1024),registry=self.registry,port=DestinationDouble,**kwargs)

    test_exact_body_and_receipt=fixture.BackupServiceTests.test_published_exact_retained_body_with_read_only_restore_and_local_receipt
    test_no_replace=fixture.BackupServiceTests.test_existing_destination_is_never_replaced_or_relabelled_verified
    test_competing_destination=fixture.BackupServiceTests.test_competing_publication_refuses_and_preserves_other_file
    test_cancel_preserves_unpublished=fixture.BackupServiceTests.test_cancel_after_verification_never_publishes
    test_failed_receipt_separate=fixture.BackupServiceTests.test_failed_receipt_reports_successful_file_separately
    test_changed_prepared_refuses=fixture.BackupServiceTests.test_changed_file_after_full_readback_refuses_publication
    test_new_history_keeps_pinned_root=fixture.BackupServiceTests.test_advancing_history_does_not_invalidate_pinned_backup_or_hide_newer_data

    def test_insufficient_space_preserves_existing_history(self):
        with patch.object(DestinationDouble,'free_bytes',return_value=0),self.assertRaisesRegex(RecordError,'backup-insufficient-space'):
            self.export()
        self.assertFalse(self.destination.exists())
        store=self.authority.store(readonly=True)
        try:self.assertEqual(self.before,store.root().ref)
        finally:store.close()

    def test_long_operation_does_not_lengthen_scratch_names(self):
        operation='long-'+('a'*90);seen=[]
        original=DestinationDouble.create
        def create(files,name):seen.append(name);return original(files,name)
        with patch.object(DestinationDouble,'create',create):self.export(operation=operation)
        self.assertEqual([31],list(map(len,seen)))
        self.assertTrue(all(len(p.name)==21 for p in self.scratch.iterdir()))
        receipt=json.loads(self.authority.files.read(self.authority.root/'last-export.json'))
        self.assertEqual(operation,receipt['operation'])

    def test_audit_name_collision_preserves_prior_bytes_without_retry(self):
        retained=self.scratch/('a-'+16*'a'+'.db');retained.write_bytes(b'prior audit')
        with patch('colvia.windows_backup.uuid.uuid4',return_value=SimpleNamespace(hex='a'*32)),self.assertRaises(FileExistsError):self.export()
        self.assertEqual(b'prior audit',retained.read_bytes());self.assertFalse(self.destination.exists())


if __name__=='__main__':unittest.main()
