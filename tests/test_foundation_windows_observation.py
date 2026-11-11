"""Portable Windows observation algorithm cases, not native handle qualification."""
from pathlib import Path
from contextlib import contextmanager
import os,stat,tempfile,unittest,hashlib
from unittest.mock import patch
from types import SimpleNamespace
from colvia.codec import RecordError,require
from colvia.platforms.windows_observation import Observer
from colvia.platforms.posix import ObservationBudget
from colvia.storage.authority import Authority
from colvia.bodies import body_bytes


class IdentityDouble:
    @contextmanager
    def ancestors(self,path):
        for p in Path(path).parents:require(not p.is_symlink(),'windows-reparse-or-changing-file')
        yield
    @contextmanager
    def opened(self,path,**kwargs):
        Path(path).lstat();yield Path(path)
    def state(self,h,path,*,opaque_symlink=False):
        s=h.lstat();link=stat.S_ISLNK(s.st_mode)
        require(not link or opaque_symlink,'windows-reparse-or-changing-file')
        return dict(identity=(s.st_dev,str(s.st_ino),0),directory=stat.S_ISDIR(s.st_mode),symlink=link,
                    links=s.st_nlink,size=s.st_size,write=s.st_mtime_ns,change=s.st_ctime_ns)


class FilesDouble:
    api=IdentityDouble()
    @contextmanager
    def _stream_handle(self,handle):
        with handle.open('rb') as stream:yield stream


class WindowsObservationTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='windows-observe-');self.base=Path(self.tmp.name)
        self.root=self.base/'project';self.root.mkdir();(self.root/'report.md').write_bytes(b'unchanged\r\n')
        self.port=Observer(files=FilesDouble());self.budget=ObservationBudget(100,100000)
    def tearDown(self):self.tmp.cleanup()
    def snapshot(self,**kw):return self.port.snapshot(self.root,self.budget,**kw)

    def test_regular_bytes_git_modes_and_selected_match(self):
        modes={'report.md':'100755'};view=self.snapshot(modes=modes,git_algorithm='sha1')
        expected=dict(path='report.md',kind='regular',mode='100755',size=11,sha256=hashlib.sha256(b'unchanged\r\n').hexdigest())
        self.assertEqual((expected,),view.entries)
        self.assertEqual(view.entries,self.port.selected(self.root,{'report.md','absent'},byte_limit=100,modes=modes))
        self.assertEqual(hashlib.sha1(b'blob 11\0unchanged\r\n').hexdigest(),view.git_blobs[0][1])

    def test_distinct_native_unicode_aliases_refuse_logical_collapse(self):
        @contextmanager
        def aliases(_):yield iter([SimpleNamespace(name='é.txt'),SimpleNamespace(name='e\u0301.txt')])
        with patch('colvia.platforms.windows_observation.os.scandir',aliases),self.assertRaisesRegex(RecordError,'path-collision'):self.snapshot()

    def test_metadata_is_bounded_and_rejects_hardlink(self):
        path=self.root/'report.md'
        self.assertEqual(b'unchanged\r\n',self.port.read_file(path,100))
        with self.assertRaisesRegex(RecordError,'unsafe-metadata-file'):self.port.read_file(path,1)
        os.link(path,self.root/'alias')
        with self.assertRaisesRegex(RecordError,'unsafe-metadata-file'):self.port.read_file(path,100)

    def test_ignore_cannot_hide_previously_protected_path(self):
        self.assertEqual((),self.snapshot(admit=lambda _:False).entries)
        self.assertEqual(1,len(self.snapshot(admit=lambda _:False,protected={'report.md'}).entries))

    def test_exact_boundary_and_protected_conflict(self):
        nested=self.root/'nested';nested.mkdir();(nested/'.git').write_text('synthetic')
        identity=self.port.location(nested);boundary={'nested':(identity.volume,identity.file_id)}
        view=self.snapshot(boundaries=boundary,reject_nested_git=True);self.assertEqual(1,len(view.entries))
        with self.assertRaisesRegex(RecordError,'boundary-swallows-protected'):self.snapshot(boundaries=boundary,protected={'nested/keep'})
        with self.assertRaisesRegex(RecordError,'structural-boundary-changed'):self.snapshot(boundaries={'nested':('wrong','wrong')})
        with self.assertRaisesRegex(RecordError,'unregistered-nested-git'):self.snapshot(reject_nested_git=True)

    def test_symlink_leaf_is_opaque_and_ancestor_never_followed(self):
        outside=self.base/'outside';outside.mkdir();(outside/'secret').write_text('never read')
        (self.root/'link').symlink_to(outside)
        view=self.snapshot();self.assertEqual({'report.md','link'},{e['path'] for e in view.entries})
        self.assertEqual('symlink',next(e for e in view.entries if e['path']=='link')['kind'])
        with self.assertRaisesRegex(RecordError,'windows-reparse-or-changing-file'):
            self.port.selected(self.root,{'link/secret'},byte_limit=100)

    def test_alias_collision_and_limits_refuse(self):
        @contextmanager
        def aliased(_):yield iter([SimpleNamespace(name='report.md'),SimpleNamespace(name='REPORT.md')])
        with patch('colvia.platforms.windows_observation.os.scandir',aliased),self.assertRaisesRegex(RecordError,'path-collision'):self.snapshot()
        with self.assertRaisesRegex(RecordError,'observation-byte-limit'):
            self.port.snapshot(self.root,ObservationBudget(100,1))
        with self.assertRaisesRegex(RecordError,'observation-cancelled'):self.snapshot(cancelled=lambda:True)

    def test_changed_file_during_read_refuses(self):
        class Changed(FilesDouble):
            @contextmanager
            def _stream_handle(inner,handle):
                with handle.open('rb') as stream:yield stream
                handle.write_bytes(b'changed concurrently')
        with self.assertRaisesRegex(RecordError,'file-observation-changed'):
            Observer(files=Changed()).snapshot(self.root,self.budget)

    def test_capture_retains_exact_body_and_refuses_wrong_digest(self):
        observed=self.snapshot().entries[0]
        authority=Authority.create(self.base/'authority',project='synthetic',instance='local',generation='one');store=authority.store()
        try:
            store.begin_import('capture','fixture')
            ref,raw=self.port.capture(self.root,'report.md',observed,store,'capture')
            # Ingested chunks remain unpublished until the Work's atomic root commit.
            self.assertEqual('body.complete',ref.kind)
            self.assertEqual(b'unchanged\r\n',b''.join(body_bytes(ref,lambda r:raw if r==ref else store.load(r,import_id='capture'))))
            with self.assertRaises(RecordError):self.port.capture(self.root,'report.md',dict(observed,sha256='0'*64),store,'capture')
        finally:store.close()


if __name__=='__main__':unittest.main()
