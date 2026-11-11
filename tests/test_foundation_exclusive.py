"""Actual no-replace primitive on isolated native fixture directories."""
import os,tempfile,unittest
from pathlib import Path
from colvia.codec import RecordError
from colvia.platforms.exclusive import available,rename
from colvia.platforms.posix import open_directory


@unittest.skipUnless(available(),'Darwin exclusive rename unavailable')
class ExclusiveRenameTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='exclusive-');self.root=Path(self.tmp.name)
        self.source=self.root/'source';self.dest=self.root/'dest';self.source.mkdir();self.dest.mkdir()
        self.s=open_directory(self.source);self.d=open_directory(self.dest)
    def tearDown(self):os.close(self.s);os.close(self.d);self.tmp.cleanup()
    def test_existing_destination_bytes_never_overwritten(self):
        (self.source/'new').write_bytes(b'proposed');(self.dest/'report').write_bytes(b'user')
        with self.assertRaisesRegex(RecordError,'effect-destination-occupied'):rename(self.s,'new',self.d,'report')
        self.assertEqual(b'user',(self.dest/'report').read_bytes());self.assertEqual(b'proposed',(self.source/'new').read_bytes())
    def test_success_preserves_inode_mode_and_bytes(self):
        p=self.source/'new';p.write_bytes(b'\x00\xff');p.chmod(0o755);identity=p.stat().st_ino
        rename(self.s,'new',self.d,'report')
        self.assertFalse(p.exists());q=self.dest/'report';self.assertEqual(identity,q.stat().st_ino)
        self.assertEqual(0o755,q.stat().st_mode&0o777);self.assertEqual(b'\x00\xff',q.read_bytes())
    def test_symlink_destination_is_not_followed_or_overwritten(self):
        (self.source/'new').write_bytes(b'proposed');(self.root/'outside').write_bytes(b'keep')
        (self.dest/'report').symlink_to(self.root/'outside')
        with self.assertRaisesRegex(RecordError,'effect-destination-occupied'):rename(self.s,'new',self.d,'report')
        self.assertEqual(b'keep',(self.root/'outside').read_bytes());self.assertTrue((self.dest/'report').is_symlink())
    def test_path_components_cannot_escape_handle(self):
        (self.source/'new').write_bytes(b'proposed')
        for path in ('../outside','/absolute','a/b','..',''):
            with self.assertRaisesRegex(RecordError,'invalid-native-component'):rename(self.s,'new',self.d,path)
        self.assertEqual(b'proposed',(self.source/'new').read_bytes())

if __name__=='__main__':unittest.main()
