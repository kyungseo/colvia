"""Asset inspection only: inert contents, no process/model or authority writes."""
import copy,hashlib,json,shutil,tempfile,unittest
from pathlib import Path
from colvia.codec import RecordError,canonical_bytes
from colvia.storage.files import PosixFiles
from colvia.execution.assets import ASSETS,DESCRIPTOR,inspect_assets

class AssetTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='document-assets-');self.root=Path(self.tmp.name)
        self.files=PosixFiles();self.content={p:(role+' inert content').encode() for role,(p,_) in ASSETS.items()}
        self.resources={role:dict(path=p,size=len(self.content[p]),sha256=hashlib.sha256(self.content[p]).hexdigest(),mode='100644') for role,(p,_) in ASSETS.items()}
        self.descriptor=dict(version=1,os='macos',architecture='arm64',resources=self.resources)
        self.publish()
    def tearDown(self):self.tmp.cleanup()
    def publish(self):
        self.content[DESCRIPTOR]=canonical_bytes(self.descriptor)
        for p,raw in self.content.items():
            f=self.root/p;f.parent.mkdir(exist_ok=True);f.write_bytes(raw);f.chmod(0o600)
        self.manifest=dict(os='macos',architecture='arm64',inventory=[dict(path=p,kind='regular',mode='100644',size=len(raw),sha256=hashlib.sha256(raw).hexdigest()) for p,raw in sorted(self.content.items())])
    def inspect(self):return inspect_assets(self.root,self.manifest,self.files,platform=('macos','arm64'))
    def test_valid_assets_are_explicitly_unavailable_for_dispatch(self):
        r=self.inspect();self.assertEqual('prepared-dispatch-unavailable',r['state']);self.assertFalse(r['dispatch_available'])
    def test_absent_and_windows_absent_are_informational(self):
        shutil.rmtree(self.root/'execution');self.manifest['inventory']=[];self.assertEqual('absent',self.inspect()['state'])
        self.manifest.update(os='windows',architecture='x64')
        r=inspect_assets(self.root,self.manifest,self.files,platform=('windows','x64'));self.assertEqual('platform-dispatch-unavailable',r['reason'])
    def test_partial_extra_and_case_alias_are_not_absent(self):
        rows=self.manifest['inventory']
        for altered in (rows[:-1],rows+[dict(rows[0],path='execution/extra')],[dict(rows[0],path='Execution/assets.json')]):
            with self.subTest(rows=altered):
                self.manifest['inventory']=altered
                with self.assertRaisesRegex(RecordError,'document-assets-invalid'):self.inspect()
    def test_wrong_platform_is_corruption(self):
        self.manifest.update(os='windows',architecture='arm64')
        with self.assertRaisesRegex(RecordError,'document-assets-platform'):inspect_assets(self.root,self.manifest,self.files,platform=('windows','arm64'))
    def test_unknown_descriptor_fields_version_and_roles(self):
        original=copy.deepcopy(self.descriptor)
        variants=[dict(original,version=2),dict(original,version=True),dict(original,extra='x'),dict(original,resources={}),dict(original,resources={**original['resources'],'other':{}})]
        for value in variants:
            self.descriptor=value;self.publish()
            with self.assertRaisesRegex(RecordError,'document-assets-invalid'):self.inspect()
    def test_descriptor_paths_and_modes_cannot_redirect_reads(self):
        original=copy.deepcopy(self.descriptor)
        for path in ('/outside','../outside',r'execution\worker','Execution/document-worker.pyz','execution/marked.umd.js'):
            self.descriptor=copy.deepcopy(original);self.descriptor['resources']['worker']['path']=path;self.publish()
            with self.assertRaisesRegex(RecordError,'document-assets-invalid'):self.inspect()
        self.descriptor=copy.deepcopy(original);self.descriptor['resources']['parser']['mode']='100755';self.publish()
        with self.assertRaisesRegex(RecordError,'document-assets-invalid'):self.inspect()
    def test_missing_changed_symlink_hardlink_and_mode_refuse(self):
        path=self.root/ASSETS['worker'][0];raw=path.read_bytes()
        twin=self.root/'worker-copy';twin.write_bytes(raw);twin.chmod(0o600)
        mutations=[lambda:path.unlink(),lambda:path.write_bytes(b'bad'),lambda:(path.unlink(),path.symlink_to(twin)),lambda:(path.unlink(),path.hardlink_to(twin)),lambda:path.chmod(0o700)]
        for change in mutations:
            if path.exists() or path.is_symlink():path.unlink()
            path.write_bytes(raw);path.chmod(0o600);change()
            with self.assertRaisesRegex(RecordError,'document-assets-changed'):self.inspect()
    def test_bad_descriptor_bytes_are_corruption(self):
        path=self.root/DESCRIPTOR;path.write_bytes(b'{broken')
        with self.assertRaisesRegex(RecordError,'document-assets-changed'):self.inspect()
        raw=b'{"version":1,"version":1}';path.write_bytes(raw)
        for row in self.manifest['inventory']:
            if row['path']==DESCRIPTOR:row.update(size=len(raw),sha256=hashlib.sha256(raw).hexdigest())
        with self.assertRaisesRegex(RecordError,'document-assets-invalid'):self.inspect()
    def test_permission_denial_remains_access_failure(self):
        from unittest.mock import patch
        with patch.object(self.files,'read',side_effect=PermissionError('synthetic denied')):
            with self.assertRaises(PermissionError):self.inspect()

    def test_untracked_namespace_and_nested_directory_refuse(self):
        extra=self.root/'execution/extra'
        extra.write_bytes(b'not in inventory')
        with self.assertRaisesRegex(RecordError,'document-assets-invalid'):self.inspect()
        extra.unlink();extra.mkdir()
        with self.assertRaisesRegex(RecordError,'document-assets-invalid'):self.inspect()
        extra.rmdir();self.manifest['inventory']=[]
        with self.assertRaisesRegex(RecordError,'document-assets-invalid'):self.inspect()
    def test_descriptor_identical_symlink_refuses(self):
        path=self.root/DESCRIPTOR;twin=self.root/'descriptor-copy';twin.write_bytes(path.read_bytes())
        path.unlink();path.symlink_to(twin)
        with self.assertRaisesRegex(RecordError,'document-assets-changed'):self.inspect()
    def test_namespace_symlink_refuses(self):
        target=self.root/'relocated';(self.root/'execution').rename(target);(self.root/'execution').symlink_to(target)
        with self.assertRaisesRegex(RecordError,'document-assets-invalid'):self.inspect()
