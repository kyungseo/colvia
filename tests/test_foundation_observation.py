from pathlib import Path
import base64,hashlib,os,tempfile,unittest
from unittest.mock import patch
from colvia.codec import RecordError
from colvia.platforms.posix import ObservationBudget,identity,location,snapshot


@unittest.skipUnless(os.name=='posix','POSIX adapter fixtures')
class ObservationTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='observation-');self.root=Path(self.tmp.name)/'project';self.root.mkdir()
        self.budget=ObservationBudget(100,8*1024*1024)
    def tearDown(self):self.tmp.cleanup()
    def test_plain_bytes_names_and_modes_preserved(self):
        data=b'\xef\xbb\xbfHello\r\n\x00\xff';(self.root/'문서.bin').write_bytes(data)
        script=self.root/'run.sh';script.write_bytes(b'exit 0\n');script.chmod(0o755)
        result=snapshot(self.root,self.budget);values={e['path']:e for e in result.entries}
        self.assertEqual(hashlib.sha256(data).hexdigest(),values['문서.bin']['sha256'])
        self.assertEqual('100755',values['run.sh']['mode']);self.assertEqual(location(self.root),result.root)
    def test_symlink_is_opaque_and_parent_links_are_not_followed(self):
        outside=Path(self.tmp.name)/'outside';outside.mkdir();(outside/'private').write_bytes(b'not observed')
        (self.root/'link').symlink_to(outside)
        result=snapshot(self.root,self.budget)
        self.assertEqual(['link'],[e['path'] for e in result.entries]);self.assertEqual(0,result.bytes_read)
        self.assertEqual(base64.b64encode(os.fsencode(str(outside))).decode(),result.entries[0]['target'])
        with self.assertRaises(OSError):snapshot(self.root/'link',self.budget)
    def test_ignored_old_protected_file_still_observed(self):
        (self.root/'old.txt').write_bytes(b'protected')
        self.assertEqual((),snapshot(self.root,self.budget,admit=lambda _:False).entries)
        result=snapshot(self.root,self.budget,admit=lambda _:False,protected=frozenset({'old.txt'}))
        self.assertEqual('old.txt',result.entries[0]['path'])
    def test_structural_boundary_cannot_swallow_old_content(self):
        child=self.root/'nested';child.mkdir();(child/'file').write_bytes(b'child')
        boundaries={'nested':identity(child.stat())}
        self.assertEqual((),snapshot(self.root,self.budget,boundaries=boundaries).entries)
        with self.assertRaisesRegex(RecordError,'boundary-swallows-protected'):
            snapshot(self.root,self.budget,boundaries=boundaries,protected={'nested/file'})
        with self.assertRaisesRegex(RecordError,'structural-boundary-changed'):
            snapshot(self.root,self.budget,boundaries={'nested':('other','other')})
    def test_file_changed_while_hashing_is_unavailable(self):
        path=self.root/'changing';path.write_bytes(b'old');original=os.read;changed=False
        def read(fd,n):
            nonlocal changed
            data=original(fd,n)
            if data and not changed:path.write_bytes(b'new long contents');changed=True
            return data
        with patch('colvia.platforms.posix.os.read',read),self.assertRaisesRegex(RecordError,'file-observation-changed'):
            snapshot(self.root,self.budget)
    def test_bounds_and_unsupported_file_type(self):
        (self.root/'a').write_bytes(b'1234')
        snapshot(self.root,ObservationBudget(1,4))
        with self.assertRaisesRegex(RecordError,'observation-byte-limit'):snapshot(self.root,ObservationBudget(1,3))
        (self.root/'b').write_bytes(b'')
        with self.assertRaisesRegex(RecordError,'observation-entry-limit'):snapshot(self.root,ObservationBudget(1,4))
        os.mkfifo(self.root/'pipe')
        with self.assertRaisesRegex(RecordError,'unsupported-entry-type'):snapshot(self.root,self.budget)


if __name__=='__main__':unittest.main()
