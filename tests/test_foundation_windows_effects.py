"""Windows effect protocol against explicit APFS doubles; not native tests."""
from contextlib import contextmanager
from pathlib import Path
import hashlib,os,stat,tempfile,unittest
from colvia.codec import RecordError,require
from colvia.storage.files import PosixFiles
from colvia.platforms.windows_effects import WindowsEffects
from colvia.platforms.windows_observation import Observer
from colvia.platforms.exclusive import rename
from colvia.platforms.posix import open_directory

class API:
    @contextmanager
    def ancestors(self,path):
        for p in Path(path).parents:require(not p.is_symlink(),'unsafe-ancestor')
        yield
    @contextmanager
    def opened(self,path,**kw):
        path=Path(path);path.lstat();require(not path.is_symlink(),'unsafe-file');yield path
    def state(self,h,path,**kw):
        s=Path(path).lstat();require(not stat.S_ISLNK(s.st_mode),'unsafe-file')
        return dict(identity=(s.st_dev,s.st_ino.to_bytes(16,'little').hex(),int(s.st_birthtime*1_000_000_000)),directory=stat.S_ISDIR(s.st_mode),
                    links=s.st_nlink,size=s.st_size,write=s.st_mtime_ns,change=s.st_ctime_ns)
    def ok(self,x):return x
    def CreateDirectoryW(self,path,_):Path(path).mkdir();return 1
    def FlushFileBuffers(self,h):return 1

class Files(PosixFiles):
    def __init__(self):super().__init__();self.api=API()
    @contextmanager
    def _stream_handle(self,h):
        with h.open('rb') as stream:yield stream

class Move:
    def __init__(self,api):self.api=api;self.count=0
    def move(self,source,target,*,expected,before_effect,event,inherited_creation=None,gate_intent=None):
        source,target=Path(source),Path(target);raw=source.read_bytes();s=self.api.state(source,source)
        require(expected==dict(identity=list(s['identity']),size=len(raw),sha256=hashlib.sha256(raw).hexdigest()),'windows-rename-source-changed')
        before_effect();event('before-native-move');self.count+=1
        a,b=open_directory(source.parent),open_directory(target.parent)
        try:rename(a,source.name,b,target.name)
        finally:os.close(a);os.close(b)
        event('after-native-move')
        if gate_intent is not None:
            current=self.api.state(target,target);return dict(identity=list(current['identity']),size=len(raw),sha256=hashlib.sha256(raw).hexdigest())

class WindowsEffectsTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='windows-effects-');base=Path(self.temp.name)
        self.root=base/'project';self.authority=base/'authority';self.root.mkdir();self.authority.mkdir(mode=0o700)
        self.files=Files();self.mover=Move(self.files.api)
        self.port=WindowsEffects(self.root,self.authority,files=self.files,observer=Observer(files=self.files),mover=self.mover)
    def tearDown(self):self.temp.cleanup()
    def entry(self,path,raw):return None if raw is None else dict(path=path,kind='regular',mode='100644',size=len(raw),sha256=hashlib.sha256(raw).hexdigest())
    def prepare(self,before=b'old',after=b'new',path='report.md'):
        if before is not None:(self.root/path).write_bytes(before)
        with self.port.exclusion():
            return self.port.prepare('apply',[dict(path=path,pre=self.entry(path,before),post=self.entry(path,after))],lambda _:iter([after]))
    def test_creation_time_exception_is_scoped_to_native_alias_with_exact_id(self):
        port=WindowsEffects(self.root,self.authority,files=self.files,observer=Observer(files=self.files),
                            mover=self.mover,native_entries=True)
        before=[4,'a'*32,70];after=[4,'b'*32,80];inherited=[4,'b'*32,70]
        for name in ('colvia.exe','colvia-manage.exe'):
            item=dict(path=name,pre_native=before,post_native=after)
            self.assertTrue(port.published_identity(item,inherited))
            self.assertFalse(self.port.published_identity(item,inherited))
            self.assertFalse(port.published_identity(item,[4,'a'*32,70]))
            self.assertFalse(port.published_identity(item,[5,'b'*32,70]))
            self.assertFalse(port.published_identity(dict(item,path='nested/'+name),inherited))
            self.assertFalse(port.published_identity(dict(item,pre_native=None),inherited))
    def test_replace_preserves_original_and_repeated_inspection_does_not_move(self):
        m=self.prepare()
        with self.port.exclusion():
            self.assertEqual('pre',self.port.state(m,0));self.port.apply_one(m,0);self.assertEqual('post',self.port.state(m,0))
            self.port.apply_one(m,0);self.assertEqual(2,self.mover.count)
        self.assertEqual(b'new',(self.root/'report.md').read_bytes())
        self.assertEqual(b'old',(self.authority/'effects/apply/000000.original').read_bytes())
    def test_retained_original_can_be_checked_after_current_entry_changes(self):
        m=self.prepare()
        with self.port.exclusion():
            self.port.apply_one(m,0);self.assertTrue(self.port.retained_original_matches(m,0))
            (self.root/'report.md').write_bytes(b'separate reverse result')
            self.assertTrue(self.port.retained_original_matches(m,0))
            (self.authority/'effects/apply/000000.original').write_bytes(b'late write')
            self.assertFalse(self.port.retained_original_matches(m,0))

    def test_crash_after_evacuate_inspects_then_explicit_continuation(self):
        m=self.prepare()
        def crash(name):
            if name=='after-native-move':raise RuntimeError('synthetic crash')
        with self.port.exclusion():
            with self.assertRaises(RuntimeError):self.port.apply_one(m,0,event=crash)
            self.assertEqual('evacuated',self.port.state(m,0));self.assertEqual(1,self.mover.count)
            self.port.apply_one(m,0);self.assertEqual('post',self.port.state(m,0))
    def test_competing_destination_and_original_remain(self):
        m=self.prepare()
        def race(name):
            if name=='after-native-move':(self.root/'report.md').write_bytes(b'other editor')
        with self.port.exclusion():
            with self.assertRaisesRegex(RecordError,'destination-occupied'):self.port.apply_one(m,0,event=race)
            with self.assertRaisesRegex(RecordError,'effect-path-unknown'):self.port.state(m,0)
        self.assertEqual(b'other editor',(self.root/'report.md').read_bytes())
        self.assertEqual(b'old',(self.authority/'effects/apply/000000.original').read_bytes())
        self.assertEqual(b'new',(self.authority/'effects/apply/000000.post').read_bytes())
    def test_changed_original_after_crash_blocks_completion(self):
        m=self.prepare()
        def crash(name):
            if name=='after-native-move':raise RuntimeError('crash')
        with self.port.exclusion():
            with self.assertRaises(RuntimeError):self.port.apply_one(m,0,event=crash)
            (self.authority/'effects/apply/000000.original').write_bytes(b'late write')
            self.assertTrue(self.port.inspect_state(m,0)['retained_original_modified'])
            with self.assertRaisesRegex(RecordError,'evacuated-file-changed'):self.port.apply_one(m,0)
        self.assertEqual(1,self.mover.count)
    def test_create_nested_and_delete_keep_distinct_states(self):
        m=self.prepare(before=None,path='new/report.md')
        with self.port.exclusion():self.port.apply_one(m,0);self.assertEqual('post',self.port.state(m,0))
        self.assertEqual(b'new',(self.root/'new/report.md').read_bytes())
    def test_delete_retains_original(self):
        m=self.prepare(after=None)
        with self.port.exclusion():self.port.apply_one(m,0);self.assertEqual('post',self.port.state(m,0))
        self.assertFalse((self.root/'report.md').exists());self.assertEqual(1,self.mover.count)
    def test_changed_target_refuses_before_any_move(self):
        m=self.prepare();(self.root/'report.md').write_bytes(b'changed')
        with self.port.exclusion(),self.assertRaisesRegex(RecordError,'effect-path-unknown'):self.port.apply_one(m,0)
        self.assertEqual(0,self.mover.count)
    def test_executable_mode_never_silently_collapsed(self):
        post={**self.entry('script',b'new'),'mode':'100755'}
        with self.port.exclusion(),self.assertRaisesRegex(RecordError,'mode-unavailable'):
            self.port.prepare('bad',[dict(path='script',pre=None,post=post)],lambda _:iter([b'new']))
    def test_symlink_ancestor_refuses(self):
        (self.root/'link').symlink_to(self.authority)
        with self.port.exclusion(),self.assertRaisesRegex(RecordError,'unsafe-file'):
            self.port.prepare('bad',[dict(path='link/a',pre=None,post=self.entry('link/a',b'new'))],lambda _:iter([b'new']))

if __name__=='__main__':unittest.main()
