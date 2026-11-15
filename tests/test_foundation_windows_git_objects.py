"""Retained object pack protocol; native Windows qualification is separate."""
from contextlib import contextmanager
from pathlib import Path
from unittest.mock import patch
import copy,hashlib,os,stat,unittest,shutil,subprocess
from colvia.codec import RecordError,decode_canonical,canonical_bytes
from colvia.effects import PENDING
from colvia.platforms import windows_git_objects as objects
from test_foundation_windows_git import WindowsFixture

class ObjectDurabilityTests(WindowsFixture,unittest.TestCase):
    def manifest(self):return decode_canonical(self.files.read(self.scratch/'integrate/manifest'))
    def state(self):return (self.command('rev-parse','HEAD'),(self.root/'.git/index').read_bytes(),self.store.head(PENDING),self.mover.count)
    def test_readonly_objects_stay_identical_and_are_never_opened_for_write(self):
        opened=self.files.api.opened;seen=[]
        @contextmanager
        def guard(path,**kw):
            p=Path(path)
            if p.is_file() and '.git/objects/' in p.as_posix():
                seen.append((str(p),kw.get('access',0)))
                if kw.get('access',0)&(0x40000000|2|4|0x100|0x10000|0x40000|0x80000):raise AssertionError('immutable object reopened writable')
            with opened(path,**kw) as h:yield h
        before={str(p): (p.read_bytes(),p.stat().st_mode) for p in (self.root/'.git/objects').glob('*/*') if p.is_file()}
        with patch.object(self.files.api,'opened',side_effect=guard):
            preview=self.prepare();m=self.manifest();self.port.verify_objects(m)
            self.assertEqual('completed',self.integration.apply('integrate',receipt=preview['receipt'],statement='synthetic')['state'])
        self.assertTrue(seen)
        for path,value in before.items():self.assertEqual(value,(Path(path).read_bytes(),Path(path).stat().st_mode))
        self.assertEqual({'pack','idx'},set(m['context']['native_objects']['files']))
    def test_pack_discovery_works_with_corrupt_readonly_duplicate_and_stale_midx(self):
        # Existing packed baseline/MIDX precedes our retained pack.
        self.command('repack','-a','-d');self.command('multi-pack-index','write')
        self.prepare();m=self.manifest();r=m['context']['native_objects']
        target=self.home/'duplicate-store';shutil.copytree(self.root/'.git/objects',target)
        raw,items,total=objects.inventory(self.port,m)
        # In a new isolated object store create a corrupt duplicate from scratch;
        # never modify the source object's bytes or READONLY protection.
        source_blob=next(oid for oid,(kind,size) in items.items() if kind=='blob')
        duplicates=[];saved=self.home/'saved-valid-loose';saved.mkdir()
        for oid in items:
            loose=target/oid[:2]/oid[2:]
            if loose.exists():loose.rename(saved/oid)
            loose.parent.mkdir(exist_ok=True);loose.write_bytes(b'');loose.chmod(0o444);duplicates.append(loose)
        env=dict(self.env,GIT_OBJECT_DIRECTORY=str(target))
        commands=[['cat-file','blob',source_blob],['rev-list','--objects',m['new']],
                  ['log','--oneline',m['new']],['diff-tree','--no-commit-id','-r','-p',m['context']['ref'],m['new']]]
        for args in commands:
            result=subprocess.run([str(self.git.executable),'-C',str(self.root),*args],env=env,capture_output=True,timeout=10)
            self.assertEqual(0,result.returncode,result.stderr)
        for loose in duplicates:
            self.assertEqual(b'',loose.read_bytes());self.assertEqual(0,loose.stat().st_mode&0o222)
        index=self.home/'checkout-index';checkout=self.home/'checkout';checkout.mkdir()
        env['GIT_INDEX_FILE']=str(index)
        for args in (['read-tree',m['new']],['checkout-index','-a','--prefix='+str(checkout)+'/']):
            result=subprocess.run([str(self.git.executable),'-C',str(self.root),*args],env=env,capture_output=True,timeout=10)
            self.assertEqual(0,result.returncode,result.stderr)
        self.assertEqual(b'reviewed result\n',(checkout/'report.md').read_bytes())
        # Pack-only path uses the same retained pack, without modifying originals.
        corrupt=self.home/'preserved-corrupt-loose';corrupt.mkdir()
        for loose in duplicates:loose.rename(corrupt/(loose.parent.name+loose.name))
        result=subprocess.run([str(self.git.executable),'-C',str(self.root),'cat-file','blob',source_blob],env=env,capture_output=True,timeout=10)
        self.assertEqual(0,result.returncode,result.stderr)

    def test_ref_update_interruption_recovers_with_exact_object_receipt(self):
        preview=self.prepare()
        def crash(phase):
            if phase=='ref-observed':raise RuntimeError('synthetic after ref')
        with self.assertRaisesRegex(RuntimeError,'after ref'):self.integration.apply('integrate',receipt=preview['receipt'],statement='synthetic',event=crash)
        self.assertIsNotNone(self.store.head(PENDING))
        self.assertEqual('completed',self.integration.recover('integrate',statement='synthetic resume')['state'])
        self.assertIsNone(self.store.head(PENDING))


    def test_legacy_receipt_refuses_without_effect(self):
        self.prepare();m=self.manifest();del m['context']['native_objects'];before=self.state()
        with self.assertRaisesRegex(RecordError,'receipt-missing'):self.port.verify_objects(m)
        self.assertEqual(before,self.state())
    def test_unknown_child_refuses_without_effect(self):
        self.prepare();m=self.manifest();r=m['context']['native_objects'];before=self.state()
        child=self.scratch/'children'/r['child'];self.files.create(child/'unknown.json',b'{}\n')
        with self.assertRaisesRegex(RecordError,'child-unconfirmed'):self.port.verify_objects(m)
        self.assertEqual(before,self.state())
    def test_changed_receipt_and_file_refuse(self):
        self.prepare();m=self.manifest();before=self.state();bad=copy.deepcopy(m)
        bad['context']['native_objects']['files']['idx']['sha256']='0'*64
        with self.assertRaisesRegex(RecordError,'file-changed'):self.port.verify_objects(bad)
        self.assertEqual(before,self.state())
    def test_fsync_failure_never_makes_authority_or_moves_ref(self):
        before=self.state();sync=self.files.sync_directory
        def fail(path):
            if str(path).endswith('/objects/pack'):raise OSError('synthetic fsync failure')
            return sync(path)
        with patch.object(self.files,'sync_directory',side_effect=fail),self.assertRaisesRegex(OSError,'fsync failure'):self.prepare()
        self.assertEqual(before,self.state());self.assertNotIn('native_objects',self.manifest()['context'])
    def test_git_environment_injections_are_rejected_before_spawn(self):
        for key in ('GIT_TEST_FSYNC','git_test_fsync','GIT_OBJECT_DIRECTORY','GIT_ALTERNATE_OBJECT_DIRECTORIES','GIT_CONFIG_COUNT','GIT_ASK_YESNO','GIT_TEST_WRITE_REV_INDEX'):
            with self.subTest(key=key),patch.dict(self.port.env,{key:'1'}),patch.object(self.port.children,'run') as run:
                with self.assertRaisesRegex(RecordError,'durability-environment'):self.port.command(['version'])
                run.assert_not_called()
    def test_missing_pack_refuses_without_rebuilding(self):
        self.prepare();m=self.manifest();r=m['context']['native_objects'];p=self.root/'.git/objects/pack'/(r['prefix']+'-'+r['hash']+'.pack')
        # Preserve the test pack, only move its name in this disposable fixture.
        p.rename(self.home/'preserved-pack');before=self.state()
        with self.assertRaisesRegex(RecordError,'pack-gone'):self.port.verify_objects(m)
        self.assertEqual(before,self.state());self.assertFalse(p.exists())


class AdmissionTests(WindowsFixture,unittest.TestCase):
    def state(self):return (self.command('rev-parse','HEAD'),(self.root/'.git/index').read_bytes(),self.store.head(PENDING),self.mover.count)
    def manifest(self):return decode_canonical(self.files.read(self.scratch/'integrate/manifest'))
    def setup_case(self,kind,recovery):
        if kind=='legacy':
            prepare=self.port.prepare
            def old_manifest(*a,**k):
                m=prepare(*a,**k);raw=canonical_bytes(m);del m['context']['native_objects']
                self.files.replace(self.scratch/'integrate/manifest',canonical_bytes(m),raw);return m
            # Explicit historical-record fixture creation only, not product bypass.
            with patch.object(self.port,'prepare',side_effect=old_manifest),patch.object(self.port,'verify_objects'),patch.object(self.port,'check'):
                preview=self.prepare()
        else:preview=self.prepare()
        if recovery:
            def stop(phase):
                if phase=='lock-intent':raise RuntimeError('planned pre-effect stop')
            if kind=='legacy':
                with patch.object(self.port,'verify_objects'),patch.object(self.port,'check'),self.assertRaises(RuntimeError):
                    self.integration.apply('integrate',receipt=preview['receipt'],statement='fixture',event=stop)
            else:
                with self.assertRaises(RuntimeError):self.integration.apply('integrate',receipt=preview['receipt'],statement='fixture',event=stop)
        m=self.manifest()
        if kind=='missing':
            r=m['context']['native_objects'];p=self.root/'.git/objects/pack'/(r['prefix']+'-'+r['hash']+'.pack');p.rename(self.home/'preserved-pack')
        elif kind=='unknown':
            self.files.create(self.scratch/'children'/m['context']['native_objects']['child']/'unknown.json',b'{}\n')
        before=self.state()
        with self.assertRaisesRegex(RecordError,{'legacy':'receipt-missing','missing':'pack-gone','unknown':'child-unconfirmed'}[kind]):
            if recovery:self.integration.recover('integrate',statement='test refusal')
            else:self.integration.apply('integrate',receipt=preview['receipt'],statement='test refusal')
        self.assertEqual(before,self.state())
    def test_apply_legacy(self):self.setup_case('legacy',False)
    def test_recover_legacy(self):self.setup_case('legacy',True)
    def test_apply_missing_pack(self):self.setup_case('missing',False)
    def test_recover_missing_pack(self):self.setup_case('missing',True)
    def test_apply_unknown_child(self):self.setup_case('unknown',False)
    def test_recover_unknown_child(self):self.setup_case('unknown',True)
    def test_actual_child_argv_without_fsync_is_refused_before_manifest(self):
        before=self.state();run=self.port.children.run
        def changed(args,**kwargs):
            args=list(args)
            if 'pack-objects' in args:
                n=args.index('core.fsync=all');del args[n-1:n+1]
            return run(args,**kwargs)
        with patch.object(self.port.children,'run',side_effect=changed),self.assertRaisesRegex(RecordError,'child-unconfirmed'):
            self.prepare()
        self.assertEqual(before,self.state());self.assertNotIn('native_objects',self.manifest()['context'])
    def test_manifest_replace_interruption_leaves_no_authority(self):
        before=self.state();replace=self.files.replace
        def crash(path,*a,**k):
            if path.name=='manifest':raise RuntimeError('before manifest replacement')
            return replace(path,*a,**k)
        with patch.object(self.files,'replace',side_effect=crash),self.assertRaisesRegex(RuntimeError,'before manifest'):
            self.prepare()
        self.assertEqual(before,self.state());self.assertNotIn('native_objects',self.manifest()['context'])
        self.assertTrue(list((self.root/'.git/objects/pack').glob('pack-colvia-*.pack')))

if __name__=='__main__':unittest.main()
