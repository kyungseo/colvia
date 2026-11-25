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

    def test_both_git_launch_paths_hold_the_selected_executable_guard(self):
        from dataclasses import asdict
        from colvia.adapters import git
        from colvia.platforms.git_candidate import GitCandidate

        raw = bytearray(128)
        raw[:2] = b'MZ'
        raw[60:64] = (80).to_bytes(4, 'little')
        raw[80:84] = b'PE\x00\x00'
        executable = self.root / 'selected.exe'
        executable.write_bytes(raw)
        os.link(executable, self.root / 'other-name.exe')
        tool = git.Git.__new__(git.Git)
        tool.executable, tool.env = executable, {}
        native_guard = self.port.opened_git_executable
        with native_guard(executable) as observed:
            tool.stamp, tool.sha256 = observed

        active = []
        launches = []

        @contextmanager
        def tracked(path):
            with native_guard(path) as observed:
                active.append(observed)
                try:
                    yield observed
                finally:
                    active.pop()

        def launch(argv, **_):
            self.assertEqual([(tool.stamp, tool.sha256)], active)
            self.assertEqual(str(executable), argv[0])
            launches.append(argv)
            return SimpleNamespace(code=0)

        candidate = GitCandidate()
        candidate.root, candidate.scratch, candidate.git = self.root, self.base / 'scratch', tool
        candidate.env = {}
        candidate.children = SimpleNamespace(run=launch)
        (candidate.scratch / 'hooks').mkdir(parents=True)
        root_location = self.port.location(self.root)
        candidate.root_identity = asdict(root_location)

        with (patch.object(git.sys, 'platform', 'win32'),
              patch('colvia.platforms.windows_observation.Observer', return_value=self.port),
              patch.object(self.port, 'opened_git_executable', side_effect=tracked),
              patch.object(git, 'file_stamp', return_value=tool.stamp),
              patch.object(git, 'run', side_effect=launch),
              patch('colvia.platforms.git_candidate.location', return_value=root_location)):
            tool._run(self.root, ('--version',))
            candidate.command(['--version'])
            self.assertEqual(2, len(launches))
            self.assertFalse(active)

            replacement = self.root / 'replacement.exe'
            replacement.write_bytes(raw)
            os.replace(replacement, executable)
            for command in (lambda: tool._run(self.root, ('--version',)),
                            lambda: candidate.command(['--version'])):
                with self.assertRaisesRegex(RecordError, 'git-executable-changed'):
                    command()
            self.assertEqual(2, len(launches))
            self.assertFalse(active)

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

    def test_strict_nested_git_marker_comparison_is_case_insensitive(self):
        for index, name in enumerate(('.git', '.GIT', '.GiT')):
            with self.subTest(name=name):
                root = self.root / str(index)
                marker = root / 'nested' / name
                marker.mkdir(parents=True)
                (marker / 'item').write_bytes(b'synthetic')
                (root / '.gitignore').write_bytes(b'ordinary')
                self.assertEqual(['.gitignore', f'nested/{name}/item'],
                                 [e['path'] for e in self.port.snapshot(root, self.budget).entries])
                with self.assertRaisesRegex(RecordError, 'unregistered-nested-git'):
                    self.port.snapshot(root, self.budget, reject_nested_git=True)
                with self.assertRaisesRegex(RecordError, 'progress-nested-project'):
                    self.port.selected(root, [f'nested/{name}/item'], byte_limit=100, verify_path=True)

    def test_strict_root_git_marker_keeps_only_proved_boundary(self):
        marker = self.root / '.GIT'
        marker.mkdir()
        (marker / 'internal').write_bytes(b'synthetic')
        native = self.port.location(marker)
        proof = (native.volume, native.file_id)
        options = dict(reject_nested_git=True, boundaries={'.git': proof})
        self.assertEqual(['report.md'], [e['path'] for e in self.snapshot(**options).entries])
        self.assertEqual(['report.md'], [e['path'] for e in self.snapshot(
            reject_nested_git=True, boundaries={'.GIT': proof, '.git': ('other', 'other')}).entries])
        with self.assertRaisesRegex(RecordError, 'boundary-swallows-protected'):
            self.snapshot(protected={'.Git/config'}, **options)
        with self.assertRaisesRegex(RecordError, 'unregistered-nested-git'):
            self.snapshot(reject_nested_git=True)
        with self.assertRaisesRegex(RecordError, 'structural-boundary-changed'):
            self.snapshot(reject_nested_git=True, boundaries={'.git': ('other', 'other')})

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
