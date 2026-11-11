"""Portable lifecycle contract regression; native ACL qualification stays separate."""
import tempfile, unittest
from pathlib import Path
from colvia.codec import RecordError
from colvia.storage.files import PosixFiles
from colvia.updates.slots import RuntimeSlots

class PrivateCreationFiles(PosixFiles):
    def __init__(self, parent, fail=None):
        super().__init__(); self.created={parent}; self.fail=fail
    def create_directory(self, path):
        path=Path(path)
        if path.parent not in self.created: raise RecordError('unqualified-parent')
        if path.name==self.fail: raise RecordError('synthetic-directory-refusal')
        super().create_directory(path); self.created.add(path)
    def create(self, path, *args, **kwargs):
        if path.parent not in self.created: raise RecordError('unqualified-parent')
        return super().create(path, *args, **kwargs)

class RuntimeCreationTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='runtime-creation-')
        self.base=Path(self.tmp.name).resolve(); self.root=self.base/'runtime'
    def tearDown(self): self.tmp.cleanup()
    def test_all_runtime_directories_have_private_creation_provenance(self):
        files=PrivateCreationFiles(self.base)
        runtime=RuntimeSlots.create(self.root,os_name='windows',architecture='arm64',files=files)
        self.assertEqual({self.base,self.root,self.root/'slots'},files.created)
        for path in [self.root,*self.root.rglob('*')]:
            if path.is_dir():
                self.assertIn(path,files.created); files.private_directory(path)
        self.assertTrue((runtime.root/'runtime.lock').is_file())
        self.assertTrue((runtime.root/'first-install.json').is_file())
    def test_second_directory_failure_preserves_partial_without_claim(self):
        files=PrivateCreationFiles(self.base,fail='slots')
        with self.assertRaisesRegex(RecordError,'synthetic-directory-refusal'):
            RuntimeSlots.create(self.root,os_name='windows',architecture='arm64',files=files)
        self.assertTrue(self.root.is_dir()); self.assertEqual([],list(self.root.iterdir()))
    def test_existing_root_is_never_adopted(self):
        self.root.mkdir(); sentinel=self.root/'preserved'; sentinel.write_bytes(b'original')
        with self.assertRaises(FileExistsError):
            RuntimeSlots.create(self.root,os_name='macos',architecture='arm64')
        self.assertEqual([sentinel],list(self.root.iterdir())); self.assertEqual(b'original',sentinel.read_bytes())
    def test_symlink_ancestor_refuses_without_writes(self):
        actual=self.base/'actual'; actual.mkdir(); alias=self.base/'alias'; alias.symlink_to(actual,target_is_directory=True)
        with self.assertRaisesRegex(RecordError,'runtime-root-symlink'):
            RuntimeSlots.create(alias/'runtime',os_name='macos',architecture='arm64')
        self.assertEqual([],list(actual.iterdir()))

if __name__=='__main__': unittest.main()
