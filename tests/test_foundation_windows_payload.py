"""Algorithm checks using a named POSIX identity double, not Windows evidence."""
from contextlib import contextmanager,nullcontext
from pathlib import Path
import hashlib,stat,tempfile,unittest
from unittest.mock import Mock, patch
from colvia.codec import RecordError,require
from colvia.storage.files import PosixFiles
from colvia.updates.windows_payload import verify_inventory

class NativeIdentityDouble:
    def ancestors(self,path):return nullcontext()
    def opened(self,path,**_):return nullcontext(Path(path))
    def private(self,h):pass # Deliberately no native SID/DACL qualification.
    def state(self,h,path):
        s=Path(path).lstat();require(not stat.S_ISLNK(s.st_mode),'synthetic-reparse-refused')
        return dict(identity=(s.st_dev,s.st_ino),directory=stat.S_ISDIR(s.st_mode),links=s.st_nlink,size=s.st_size,write=s.st_mtime_ns,change=s.st_ctime_ns)
class FileDouble(PosixFiles):
    def _stream_handle(self,h):return h.open("rb")
    api=NativeIdentityDouble()
class WindowsPayloadAlgorithmTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='windows-payload-');self.root=Path(self.tmp.name);self.files=FileDouble()
        self.manifest=b'fixed manifest bytes';(self.root/'manifest.json').write_bytes(self.manifest);(self.root/'runtime').mkdir()
        (self.root/'runtime/python.exe').write_bytes(b'fixture');self.sha=hashlib.sha256(self.manifest).hexdigest()
        self.entries=[dict(path='runtime/python.exe',size=7,sha256=hashlib.sha256(b'fixture').hexdigest(),kind='regular',mode='100755')]
    def tearDown(self):self.tmp.cleanup()
    def verify(self,**kw):verify_inventory(self.root,self.entries,self.manifest,self.sha,self.files,**kw)
    def test_logical_executable_mode_is_not_host_posix_mode(self):self.verify()
    def test_extra_file_and_reparse_refuse(self):
        extra=self.root/'extra';extra.write_bytes(b'x')
        with self.assertRaisesRegex(RecordError,'inventory-mismatch'):self.verify()
        extra.unlink();extra.symlink_to('manifest.json')
        with self.assertRaisesRegex(RecordError,'reparse'):self.verify()
    def test_same_length_tampering_and_cancellation_refuse(self):
        (self.root/'runtime/python.exe').write_bytes(b'changed')
        with self.assertRaisesRegex(RecordError,'inventory-mismatch'):self.verify()
        with self.assertRaisesRegex(RecordError,'cancelled'):self.verify(cancelled=lambda:True)
    def test_missing_file_and_hardlink_refuse(self):
        import os
        path=self.root/'runtime/python.exe';path.unlink()
        with self.assertRaisesRegex(RecordError,'inventory-mismatch'):self.verify()
        path.write_bytes(b'fixture');os.link(path,self.root/'duplicate')
        with self.assertRaisesRegex(RecordError,'inventory-mismatch'):self.verify()

class PinnedPayloadTests(WindowsPayloadAlgorithmTests):
    def verify(self,**kw):
        from colvia.updates.windows_payload import verify_pinned_inventory
        verify_pinned_inventory(self.root,self.entries,self.manifest,self.sha,self.files,**kw)

    def test_retained_proof_detects_membership_and_identity_drift(self):
        retained = Mock()
        self.verify(retain=retained)
        retained.assert_called_once()
        handles, check = retained.call_args.args
        try:
            check()
            extra = self.root/'extra'
            extra.write_bytes(b'added')
            with self.assertRaisesRegex(RecordError, 'slot-(?:directory|file)-changed'):
                check()
            extra.unlink()
            target = self.root/'runtime/python.exe'
            target.write_bytes(b'changed')
            with self.assertRaisesRegex(RecordError, 'slot-file-changed'):
                check()
        finally:
            handles.close()

    def test_repeat_inventory_rejects_extra_entry_without_enumerating_the_rest(self):
        from types import SimpleNamespace

        @contextmanager
        def entries(_):
            def unexpected_then_stop():
                yield SimpleNamespace(name='unexpected')
                self.fail('consumption enumerated beyond a known changed entry')
            yield unexpected_then_stop()

        retained = Mock()
        self.verify(retain=retained)
        handles, check = retained.call_args.args
        try:
            with patch('colvia.updates.windows_payload.os.scandir', entries):
                with self.assertRaisesRegex(RecordError, 'slot-directory-changed'):
                    check()
        finally:
            handles.close()

    def test_retained_proof_rechecks_privacy_and_closes_handles(self):
        real_open = self.files.api.opened
        closed = []

        @contextmanager
        def tracked(path, **options):
            with real_open(path, **options) as handle:
                try:
                    yield handle
                finally:
                    closed.append(path)

        retained = Mock()
        with patch.object(self.files.api, 'opened', side_effect=tracked):
            self.verify(retain=retained)
            self.assertEqual([], closed)
            handles, check = retained.call_args.args
            try:
                with patch.object(self.files.api, 'private', side_effect=RecordError('not-private')):
                    with self.assertRaisesRegex(RecordError, 'not-private'):
                        check()
            finally:
                handles.close()
        self.assertEqual(4, len(closed))

if __name__=='__main__':unittest.main()
