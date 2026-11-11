import os,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from colvia.codec import RecordError
from colvia.storage.files import PosixFiles
from colvia.platforms.exclusive import available

@unittest.skipUnless(available(),'exclusive native publication unavailable')
class LifecycleFileTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='lifecycle-files-');self.root=Path(self.tmp.name);self.files=PosixFiles()
    def tearDown(self):self.tmp.cleanup()
    def test_short_write_failure_does_not_publish_partial_final_marker(self):
        path=self.root/'pending.json';write=os.write;calls=0
        def partial(fd,data):
            nonlocal calls
            calls+=1
            if calls>1:raise OSError('synthetic write failure')
            return write(fd,data[:4])
        with patch('colvia.storage.files.os.write',partial),self.assertRaises(OSError):self.files.create(path,b'complete marker bytes')
        self.assertFalse(path.exists());prepared=list(self.root.glob('pending.json.prepared-*'));self.assertEqual(1,len(prepared))
        self.assertEqual(b'comp',prepared[0].read_bytes())
    def test_executable_is_published_only_after_complete_write_with_owner_mode(self):
        path=self.root/'colvia';write=os.write;calls=0
        def partial(fd,data):
            nonlocal calls
            calls+=1
            if calls>1:raise OSError('synthetic executable interruption')
            return write(fd,data[:3])
        with patch('colvia.storage.files.os.write',partial),self.assertRaises(OSError):
            self.files.create(path,b'complete executable',executable=True)
        self.assertFalse(path.exists());self.assertEqual(1,len(list(self.root.glob('colvia.prepared-*'))))
        self.files.create(path,b'complete executable',executable=True)
        self.assertEqual(b'complete executable',path.read_bytes());self.assertEqual(0o700,path.stat().st_mode&0o777)
    def test_existing_target_is_never_replaced_by_create(self):
        path=self.root/'record.json';self.files.create(path,b'first')
        with self.assertRaises(FileExistsError):self.files.create(path,b'second')
        self.assertEqual(b'first',self.files.read(path))
    def test_after_rename_sync_failure_is_explicitly_unknown(self):
        path=self.root/'active.json';self.files.create(path,b'old');original=self.files.sync_directory;calls=0
        def sync(parent):
            nonlocal calls
            calls+=1
            if calls==2:raise OSError('synthetic sync failure')
            original(parent)
        with patch.object(self.files,'sync_directory',sync),self.assertRaisesRegex(RecordError,'lifecycle-replace-durability-unknown'):
            self.files.replace(path,b'new',b'old')
        self.assertEqual(b'new',path.read_bytes())
    def test_existence_does_not_turn_permission_denial_into_absence(self):
        with patch.object(self.files,'read',side_effect=PermissionError('synthetic denied')):
            with self.assertRaises(PermissionError):self.files.exists(self.root/'pending.json')

    def test_stream_source_change_is_detected_and_no_follow_is_preserved(self):
        source=self.root/'source';source.write_bytes(b'first')
        with self.assertRaisesRegex(RecordError,'file-changed'):
            with self.files.read_stream(source,100) as stream:
                self.assertEqual(b'first',stream.read());source.write_bytes(b'later')
        alias=self.root/'alias';alias.symlink_to(source.name)
        with self.assertRaises(OSError):
            with self.files.read_stream(alias,100):pass
    def test_stream_partial_destination_remains_only_at_explicit_staging_path(self):
        destination=self.root/'prepared-body'
        with self.assertRaisesRegex(OSError,'synthetic'):
            with self.files.create_stream(destination) as stream:
                stream.write(b'partial');raise OSError('synthetic interrupt')
        self.assertEqual(b'partial',destination.read_bytes())
        with self.assertRaises(FileExistsError):
            with self.files.create_stream(destination):pass
