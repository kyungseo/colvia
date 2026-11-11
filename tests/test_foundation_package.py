"""Synthetic regular-file release bundles, without installation or Python launch."""
import hashlib,io,stat,tempfile,unittest,zipfile
from pathlib import Path
from colvia.codec import RecordError,canonical_bytes
from colvia.updates.slots import RuntimeSlots,pointer
from colvia.updates.package import stage_archive,descriptor

class PackageTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='package-');self.base=Path(self.tmp.name)
        self.runtime=RuntimeSlots.create(self.base/'managed',os_name='macos',architecture='arm64')
        self.content={'bin/python':b'fixture executable','manager.py':b'fixture manager','product.py':b'fixture product'}
        self.manifest=dict(version=1,release='release-one',sequence=1,os='macos',architecture='arm64',python_version='3.14.7',
            sqlite_version='3.54.0',python='bin/python',manager='manager.py',product='product.py',read_capabilities=['foundation-v1'],
            write_capabilities=['foundation-v1'],features=[],inventory=[dict(path=p,kind='regular',mode='100755' if p=='bin/python' else '100644',
                size=len(b),sha256=hashlib.sha256(b).hexdigest()) for p,b in sorted(self.content.items())])
    def tearDown(self):self.tmp.cleanup()
    def archive(self,extra=(),mutate=lambda name,raw:raw):
        raw=canonical_bytes(self.manifest);self.content['manifest.json']=raw;out=self.base/'bundle.zip'
        with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED) as z:
            for name,b in self.content.items():z.writestr(name,mutate(name,b))
            for name,b,mode in extra:
                i=zipfile.ZipInfo(name);i.external_attr=mode<<16;z.writestr(i,b)
        blob=out.read_bytes();target=dict(length=len(blob),sha256=hashlib.sha256(blob).hexdigest(),custom={'colvia':dict(version=1,channel='preview',
            os='macos',architecture='arm64',release='release-one',sequence=1,manifest_sha256=hashlib.sha256(raw).hexdigest())})
        return out,target
    def stage(self,out,target,**kwargs):return stage_archive(out,root=self.runtime.root,slot='candidate',target=target,channel='preview',os_name='macos',architecture='arm64',**kwargs)
    def test_verified_staging_is_not_activation(self):
        out,target=self.archive();slot=self.stage(out,target)
        self.assertEqual('release-one',slot.release);self.assertFalse((self.runtime.root/'runtime.json').exists())
        self.runtime.initialize(pointer(slot));self.assertTrue(self.runtime.launch(read_requirements=[])[0].endswith('/bin/python'))
    def test_archive_change_refuses_before_slot_creation(self):
        out,target=self.archive();out.write_bytes(out.read_bytes()+b'changed')
        with self.assertRaisesRegex(RecordError,'package-file-mismatch'):self.stage(out,target)
        self.assertFalse((self.runtime.root/'slots/candidate').exists())
    def test_signed_bundle_with_wrong_inner_body_does_not_publish(self):
        out,target=self.archive(mutate=lambda name,raw:b'changed manager' if name=='manager.py' else raw)
        with self.assertRaisesRegex(RecordError,'package-file-length-mismatch|package-content-mismatch'):self.stage(out,target)
        self.assertFalse((self.runtime.root/'runtime.json').exists())
    def test_path_escape_symlink_alias_and_reserved_name_rejected(self):
        for n,(name,mode) in enumerate((('../escape',stat.S_IFREG|0o644),('link',stat.S_IFLNK|0o777),('BIN/other',stat.S_IFREG|0o644),('CON.txt',stat.S_IFREG|0o644))):
            with self.subTest(name=name):
                out,target=self.archive(extra=[(name,b'bad',mode)])
                with self.assertRaises(RecordError):self.stage(out,target)
                self.assertFalse((self.runtime.root/'slots/candidate').exists());out.unlink()
    def test_channel_platform_and_manifest_identity_are_signed_inputs(self):
        out,target=self.archive();target['custom']['colvia']['architecture']='x64'
        with self.assertRaisesRegex(RecordError,'release-descriptor-mismatch'):self.stage(out,target)
        self.assertFalse((self.runtime.root/'slots/candidate').exists())
    def test_cancelled_staging_never_changes_runtime_binding(self):
        out,target=self.archive();calls=0
        def cancelled():
            nonlocal calls
            calls+=1;return calls>=4
        with self.assertRaisesRegex(RecordError,'package-cancelled'):self.stage(out,target,cancelled=cancelled)
        self.assertFalse((self.runtime.root/'runtime.json').exists())
