"""Native effect fault injection. All files live in an owned synthetic fixture."""
from pathlib import Path
import hashlib,os,tempfile,unittest
from colvia.codec import RecordError
from colvia.platforms.exclusive import available
from colvia.platforms.darwin_effects import DarwinEffects


def entry(path,raw,mode='100644'):
    return None if raw is None else dict(path=path,kind='regular',mode=mode,size=len(raw),sha256=hashlib.sha256(raw).hexdigest())


@unittest.skipUnless(available(),'Darwin writer unavailable')
class DarwinEffectTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='effects-');self.base=Path(self.tmp.name)
        self.root=self.base/'project';self.root.mkdir();self.authority=self.base/'authority';self.authority.mkdir(mode=0o700)
        self.port=DarwinEffects(self.root,self.authority)
    def tearDown(self):self.tmp.cleanup()
    def prepare(self,*,path='report.md',before=b'original',after=b'new\x00\xff',mode='100644'):
        if before is not None:
            target=self.root/path;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(before)
        changes=[dict(path=path,pre=entry(path,before),post=entry(path,after,mode))]
        return self.port.prepare('application',changes,lambda _:iter([after]) if after is not None else iter(()))
    def originals(self):return list((self.authority/'effects'/'application').glob('*.original'))

    def test_regular_replace_preserves_original_and_binary_mode(self):
        with self.port.exclusion():
            manifest=self.prepare(mode='100755');self.assertEqual('pre',self.port.state(manifest,0))
            self.port.apply_one(manifest,0);self.assertEqual('post',self.port.state(manifest,0))
            self.assertEqual(b'new\x00\xff',(self.root/'report.md').read_bytes());self.assertEqual(b'original',self.originals()[0].read_bytes())
            self.assertEqual(0o755,(self.root/'report.md').stat().st_mode&0o777)

    def test_add_nested_directories_then_resume_same_result(self):
        with self.port.exclusion():
            manifest=self.prepare(path='docs/nested/new.md',before=None,after=b'new')
            self.port.apply_one(manifest,0);self.port.apply_one(manifest,0)
            self.assertEqual(b'new',(self.root/'docs/nested/new.md').read_bytes());self.assertEqual([],self.originals())

    def test_delete_evacuates_instead_of_unlinking(self):
        with self.port.exclusion():
            manifest=self.prepare(after=None);self.port.apply_one(manifest,0)
            self.assertFalse((self.root/'report.md').exists());self.assertEqual(b'original',self.originals()[0].read_bytes())
            self.assertEqual('post',self.port.state(manifest,0))

    def test_crash_after_evacuation_resumes_only_original_intent(self):
        with self.port.exclusion():
            manifest=self.prepare()
            def crash(name):
                if name=='after-evacuate':raise RuntimeError('injected interruption')
            with self.assertRaises(RuntimeError):self.port.apply_one(manifest,0,event=crash)
            self.assertEqual('evacuated',self.port.state(manifest,0));self.assertFalse((self.root/'report.md').exists())
        fresh=DarwinEffects(self.root,self.authority)
        with fresh.exclusion():fresh.apply_one(manifest,0);self.assertEqual('post',fresh.state(manifest,0))

    def test_crash_after_install_recognizes_actual_post(self):
        with self.port.exclusion():
            manifest=self.prepare()
            def crash(name):
                if name=='after-install':raise RuntimeError('injected interruption')
            with self.assertRaises(RuntimeError):self.port.apply_one(manifest,0,event=crash)
            self.assertEqual('post',self.port.state(manifest,0));self.port.apply_one(manifest,0)
            self.assertEqual(b'original',self.originals()[0].read_bytes())

    def test_new_user_occupant_never_overwritten(self):
        with self.port.exclusion():
            manifest=self.prepare()
            def race(name):
                if name=='before-install':(self.root/'report.md').write_bytes(b'user arrived')
            with self.assertRaisesRegex(RecordError,'effect-destination-occupied'):self.port.apply_one(manifest,0,event=race)
            self.assertEqual(b'user arrived',(self.root/'report.md').read_bytes());self.assertEqual(b'original',self.originals()[0].read_bytes())
            with self.assertRaisesRegex(RecordError,'effect-path-unknown'):self.port.state(manifest,0)

    def test_racing_edit_is_returned_without_losing_new_bytes(self):
        with self.port.exclusion():
            manifest=self.prepare()
            def race(name):
                if name=='before-evacuate':(self.root/'report.md').write_bytes(b'user changed')
            with self.assertRaisesRegex(RecordError,'effect-evacuated-file-changed'):self.port.apply_one(manifest,0,event=race)
            self.assertEqual(b'user changed',(self.root/'report.md').read_bytes())
            self.assertEqual([],self.originals())

    def test_restore_collision_keeps_both_user_files(self):
        with self.port.exclusion():
            manifest=self.prepare()
            def race(name):
                if name=='before-evacuate':(self.root/'report.md').write_bytes(b'first edit')
                if name=='after-evacuate':(self.root/'report.md').write_bytes(b'second edit')
            with self.assertRaisesRegex(RecordError,'effect-evacuated-file-changed'):self.port.apply_one(manifest,0,event=race)
            self.assertEqual(b'second edit',(self.root/'report.md').read_bytes());self.assertEqual(b'first edit',self.originals()[0].read_bytes())

    def test_held_fd_edit_after_install_is_preserved_not_cleaned(self):
        with self.port.exclusion():
            manifest=self.prepare();fd=os.open(self.root/'report.md',os.O_WRONLY|os.O_APPEND)
            try:self.port.apply_one(manifest,0);os.write(fd,b' late edit');os.fsync(fd)
            finally:os.close(fd)
            self.assertEqual(dict(state='post',retained_original_modified=True),self.port.inspect_state(manifest,0))
            self.port.sync(manifest,0)
            self.assertEqual(b'original late edit',self.originals()[0].read_bytes());self.assertEqual(b'new\x00\xff',(self.root/'report.md').read_bytes())

    def test_replaced_retained_original_identity_still_refuses(self):
        with self.port.exclusion():
            manifest=self.prepare();self.port.apply_one(manifest,0)
            original=self.originals()[0];saved=original.with_name('preserved-identity');os.rename(original,saved)
            original.write_bytes(saved.read_bytes())
            with self.assertRaisesRegex(RecordError,'effect-evacuated-file-changed'):self.port.state(manifest,0)
            self.assertEqual(b'original',saved.read_bytes())

    def test_staging_name_cannot_be_reused_or_overwritten(self):
        with self.port.exclusion():
            manifest=self.prepare()
            with self.assertRaisesRegex(RecordError,'effect-staging-already-exists'):self.port.prepare('application',manifest['items'],lambda _:iter([b'bad']))
            self.assertEqual(b'new\x00\xff',(self.authority/'effects/application/000000.post').read_bytes())

    def test_symlink_ancestor_and_case_alias_refuse(self):
        outside=self.base/'outside';outside.mkdir();(self.root/'alias').symlink_to(outside,target_is_directory=True)
        with self.port.exclusion():
            with self.assertRaisesRegex(RecordError,'unsafe-effect-ancestor'):
                self.port.prepare('symlink',[dict(path='alias/new',pre=None,post=entry('alias/new',b'x'))],lambda _:iter([b'x']))
            (self.root/'Report.md').write_bytes(b'keep')
            with self.assertRaisesRegex(RecordError,'worker-path-alias'):
                self.port.prepare('case',[dict(path='report.md',pre=None,post=entry('report.md',b'x'))],lambda _:iter([b'x']))
        self.assertEqual([],list(outside.iterdir()));self.assertEqual(b'keep',(self.root/'Report.md').read_bytes())

    def test_hardlink_preimage_refused_without_mutation(self):
        (self.root/'report.md').write_bytes(b'original');os.link(self.root/'report.md',self.base/'other')
        with self.port.exclusion():
            with self.assertRaisesRegex(RecordError,'effect-file-not-single-regular'):
                self.port.prepare('hardlink',[dict(path='report.md',pre=entry('report.md',b'original'),post=entry('report.md',b'x'))],lambda _:iter([b'x']))
        self.assertEqual(b'original',(self.base/'other').read_bytes())

    def test_missing_evacuation_is_not_recreated_from_record(self):
        with self.port.exclusion():
            manifest=self.prepare();self.port.apply_one(manifest,0);self.originals()[0].unlink()
            with self.assertRaisesRegex(RecordError,'effect-evacuated-file-missing'):self.port.state(manifest,0)

    def test_lock_excludes_another_port_instance(self):
        other=DarwinEffects(self.root,self.authority)
        with self.port.exclusion():
            with self.assertRaisesRegex(RecordError,'effect-busy'):
                with other.exclusion():pass
        with other.exclusion():pass

    def test_parent_moved_between_checks_is_not_followed_outside_workspace(self):
        with self.port.exclusion():
            manifest=self.prepare(path='docs/report.md')
            def race(stage):
                if stage=='before-evacuate':
                    (self.root/'docs').rename(self.base/'moved-docs');(self.root/'docs').mkdir()
            with self.assertRaisesRegex(RecordError,'effect-ancestor-changed'):self.port.apply_one(manifest,0,event=race)
            self.assertEqual(b'original',(self.base/'moved-docs/report.md').read_bytes())
            self.assertEqual([],list((self.root/'docs').iterdir()));self.assertEqual([],self.originals())

    def test_decomposed_native_filename_uses_its_exact_existing_entry(self):
        import unicodedata
        logical='한글/보고서.md';native=unicodedata.normalize('NFD',logical)
        target=self.root/native;target.parent.mkdir();target.write_bytes(b'original')
        changes=[dict(path=logical,pre=entry(logical,b'original'),post=entry(logical,b'new'))]
        with self.port.exclusion():
            manifest=self.port.prepare('application',changes,lambda _:iter([b'new']))
            self.port.apply_one(manifest,0);self.assertEqual('post',self.port.state(manifest,0))
        self.assertEqual(b'new',target.read_bytes());self.assertEqual(1,len(list(target.parent.iterdir())))

    def test_process_lock_refuses_second_process_and_releases_on_exit(self):
        import subprocess,sys
        code="""import sys
sys.path.insert(0,sys.argv[1])
from colvia.platforms.darwin_effects import DarwinEffects
from colvia.codec import RecordError
p=DarwinEffects(sys.argv[2],sys.argv[3])
try:
 with p.exclusion(): print('acquired')
except RecordError as e:
 if e.code!='effect-busy': raise
 print('busy')
"""
        args=[sys.executable,'-I','-B','-c',code,str(Path(__file__).resolve().parents[1]/'src'),str(self.root),str(self.authority)]
        with self.port.exclusion():
            result=subprocess.run(args,capture_output=True,text=True,timeout=10)
            self.assertEqual(0,result.returncode,result.stderr);self.assertEqual('busy',result.stdout.strip())
        result=subprocess.run(args,capture_output=True,text=True,timeout=10)
        self.assertEqual(0,result.returncode,result.stderr);self.assertEqual('acquired',result.stdout.strip())

    def test_effect_requires_lock_and_staging_outside_project(self):
        with self.assertRaisesRegex(RecordError,'effect-lock-required'):self.prepare()
        nested=self.root/'private';nested.mkdir(mode=0o700)
        with self.assertRaisesRegex(RecordError,'effect-staging-overlaps-workspace'):DarwinEffects(self.root,nested)

if __name__=='__main__':unittest.main()
