"""Windows logical modes: real Git classification and native file observations.

Portable cases exercise Git/parser/feasibility policy only. Native cases require
actual Windows and retain fixture paths in the selected batch result directory.
"""
from __future__ import annotations
import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

from hv2ref import work
from hv2ref.errors import ContractError


class ContentFixture:
    def setUp(self):
        if sys.platform == 'win32':
            self.root = Path(os.environ['COLVIA_NATIVE_TEST_ROOT']) / ('c' + hashlib.sha256(self.id().encode()).hexdigest()[:10])
            self.root.mkdir(parents=True, exist_ok=False)
        else:
            temporary = tempfile.TemporaryDirectory()
            self.addCleanup(temporary.cleanup)
            self.root = Path(temporary.name)
        self.target = self.root / 'p'; self.target.mkdir()

    def tearDown(self):
        if sys.platform == 'win32':
            print('NATIVE_CONTENT_FIXTURE ' + json.dumps({'test': self.id(), 'root': str(self.root)}), flush=True)

    def git(self, *args):
        result = subprocess.run(['git', '-c', 'user.name=Synthetic Test', '-c', 'user.email=fixture@example.invalid', '-C', str(self.target), *args],
                                capture_output=True, timeout=15)
        self.assertEqual(0, result.returncode, result.stderr.decode(errors='replace'))
        return result.stdout

    def repository(self):
        self.git('init')
        (self.target / 'plain').write_bytes(b'before\r\n')
        (self.target / 'program').write_bytes(b'executable bytes\n')
        self.git('add', 'plain', 'program')
        self.git('update-index', '--chmod=+x', 'program')

    def entry(self, path, mode='100644', data=b'before\r\n'):
        return {'path': path, 'mode': mode, 'sha256': hashlib.sha256(data).hexdigest(), 'size_bytes': len(data)}

    def tree(self, entries):
        value = {'policy_version': 1, 'ignore_fingerprint': 'a' * 64,
                 'entries': sorted(entries, key=lambda e: e['path'].encode())}
        value['sha256'] = work._digest(value)
        return work.validate_tree(value)

    def manifest(self, before, after):
        return work.make_manifest(self.tree(before), self.tree(after), scope=sorted({e['path'] for e in before + after}))

    def predict(self, manifest):
        # Only policy dispatch is injected. Actual Git classification/ignore
        # probes run unchanged. This is not native Win32 execution evidence.
        with mock.patch.object(work, '_windows_content_policy', return_value=True):
            return work._windows_worker_modes(self.target, manifest, 'windows-2')

    def native_snapshot(self):
        return work.snapshot(self.target, verified_inventory_id='windows-2')


class PortableWindowsContentTests(ContentFixture, unittest.TestCase):
    def test_worker_registration_uses_git_windows_separators_without_alias_relaxation(self):
        from pathlib import PurePosixPath, PureWindowsPath
        from types import SimpleNamespace
        windows = PureWindowsPath(r'C:\fixture\한글 worker')
        posix = PurePosixPath('/fixture/한글 worker' + chr(92) + 'literal')
        cases = [
            ('win32', windows, os.fsencode(windows.as_posix()), True),
            ('win32', windows, os.fsencode(windows), False),
            ('win32', windows, os.fsencode(windows.as_posix().replace('worker', 'Worker')), False),
            ('win32', windows, os.fsencode(windows.as_posix() + '-other'), False),
            ('win32', windows, b'', False),
            ('darwin', posix, os.fsencode(posix), True),
            ('darwin', posix, os.fsencode(str(posix).replace(chr(92), '/')), False),
        ]
        manifest = {'base': {'sha256': 'base'}, 'result': {'sha256': 'result'},
                    'candidate_commit': 'a' * 40}
        for platform, worker, registration, accepted in cases:
            def git(target, *args):
                if args == ('rev-parse', '--path-format=absolute', '--git-common-dir'):
                    return SimpleNamespace(stdout=b'common\n')
                if args == ('worktree', 'list', '--porcelain', '-z'):
                    return SimpleNamespace(stdout=b'worktree ' + registration + b'\0HEAD ' + b'a' * 40 + b'\0\0')
                self.assertEqual(('rev-parse', '--verify', 'HEAD'), args)
                return SimpleNamespace(stdout=b'a' * 40 + b'\n')
            with self.subTest(platform=platform, registration=registration), \
                    mock.patch.object(work, 'sys', SimpleNamespace(platform=platform)), \
                    mock.patch.object(work, 'classify_target', side_effect=[{'kind': 'primary'}, {'kind': 'linked-worktree'}]), \
                    mock.patch.object(work, 'safe_target', return_value=worker), \
                    mock.patch.object(work, 'snapshot', side_effect=[manifest['base'], manifest['result']]), \
                    mock.patch.object(work, 'verify_worker_sources', return_value={}), \
                    mock.patch.object(work, '_git', side_effect=git), \
                    mock.patch.object(work, 'preflight_changed_paths', return_value={'sample.txt': 'pre'}), \
                    mock.patch.object(work, '_worker_required_refs') as references:
                if accepted:
                    work._worker_record_preflight(self.target, {'operation': 'submit-result'}, manifest, None,
                                                  verified_inventory_id='windows-2' if platform == 'win32' else None,
                                                  worker=worker)
                    references.assert_called_once()
                else:
                    with self.assertRaisesRegex(ContractError, 'worker registration is missing'):
                        work._worker_record_preflight(self.target, {'operation': 'submit-result'}, manifest, None,
                                                      verified_inventory_id='windows-2' if platform == 'win32' else None,
                                                      worker=worker)
                    references.assert_not_called()

    def test_real_git_debug_shape_and_logical_index_modes(self):
        self.repository()
        (self.target / 'new.exe').write_bytes(b'untracked')
        state = work._windows_git_state(self.target)
        self.assertEqual({'plain': '100644', 'program': '100755'}, state['tracked'])
        self.assertEqual({'new.exe'}, state['untracked'])
        self.assertEqual(set(), state['ignored'])
        self.assertEqual(state, work._windows_git_state(self.target))

    def test_special_index_flags_never_become_default_modes(self):
        self.repository()
        for enable, disable in (('--assume-unchanged', '--no-assume-unchanged'), ('--skip-worktree', '--no-skip-worktree')):
            self.git('update-index', enable, 'plain')
            with self.assertRaisesRegex(ContractError, 'special flags'):
                work._windows_git_state(self.target)
            self.git('update-index', disable, 'plain')
            self.assertEqual('100644', work._windows_git_state(self.target)['tracked']['plain'])
        (self.target / 'intent').write_bytes(b'not staged')
        self.git('add', '-N', 'intent')
        with self.assertRaisesRegex(ContractError, 'special flags'):
            work._windows_git_state(self.target)

    def test_index_parser_refuses_unknown_shape_modes_and_duplicates(self):
        self.repository()
        raw = work._windows_git_state(self.target)['raw'][0]
        invalid = [raw[:-1], raw.replace(b'  ctime:', b'  future:'), raw.replace(b'100644 ', b'120000 ', 1),
                   raw.replace(b' 0\t', b' 2\t', 1), raw + raw, raw.replace(b'flags: 0', b'flags: 2000', 1)]
        for value in invalid:
            with self.subTest(digest=hashlib.sha256(value).hexdigest()), self.assertRaises(ContractError):
                work._windows_index_modes(value)

    def test_common_worker_condition_accepts_reproducible_modes_and_deletion(self):
        self.repository()
        before = [self.entry('plain'), self.entry('program', '100755', b'executable bytes\n')]
        after = [self.entry('program', '100755', b'changed executable bytes\n'), self.entry('new.txt', data=b'new')]
        manifest = self.manifest(before, after)
        index = (self.target / '.git/index').read_bytes()
        self.predict(manifest)
        self.assertEqual(index, (self.target / '.git/index').read_bytes())
        self.assertEqual(b'before\r\n', (self.target / 'plain').read_bytes())
        self.assertFalse((self.target / 'new.txt').exists())

    def test_common_worker_condition_refuses_unreproducible_and_ignored_post(self):
        self.repository()
        before = [self.entry('plain')]
        cases = [self.manifest(before, [self.entry('plain', '100755')]),
                 self.manifest(before, before + [self.entry('new.exe', '100755')])]
        for manifest in cases:
            with self.subTest(changes=manifest['changes']), self.assertRaises(ContractError):
                self.predict(manifest)
        (self.target / '.gitignore').write_text('generated.*\n')
        with self.assertRaisesRegex(ContractError, 'ignored'):
            self.predict(self.manifest(before, before + [self.entry('generated.txt')]))

    def test_common_worker_condition_checks_unchanged_union_and_index_drift(self):
        self.repository()
        # A retained manifest expects a different mode on an unchanged path.
        manifest = self.manifest([self.entry('program')], [self.entry('program')])
        with self.assertRaisesRegex(ContractError, 'post mode'):
            self.predict(manifest)
        state = work._windows_git_state(self.target); changed = copy.deepcopy(state)
        changed['raw'] = (state['raw'][0] + b'drift', *state['raw'][1:])
        manifest = self.manifest([self.entry('plain')], [self.entry('plain', data=b'new')])
        with mock.patch.object(work, '_windows_git_state', side_effect=[state, changed]), self.assertRaisesRegex(ContractError, 'changed during'):
            self.predict(manifest)

    def test_non_git_historical_executable_mode_mutation_is_unsupported(self):
        manifest = self.manifest([self.entry('legacy', '100755')], [self.entry('legacy')])
        original = copy.deepcopy(manifest)
        with mock.patch.object(work, '_windows_content_policy', return_value=True), self.assertRaisesRegex(ContractError, 'retained 100755'):
            work._windows_non_git_manifest(self.target, manifest, 'windows-2')
        self.assertEqual(original, manifest)
        self.assertEqual([], list(self.target.iterdir()))


@unittest.skipUnless(sys.platform == 'win32', 'native Windows content observation; excluded from POSIX execution matrix')
class WindowsContentTests(ContentFixture, unittest.TestCase):
    def test_non_git_defaults_ignore_executable_extension_and_readonly(self):
        for name in ('plain', 'program.exe', 'script.cmd', 'script.bat', 'program.com'):
            (self.target / name).write_bytes(b'same\r\n')
        os.chmod(self.target / 'program.exe', 0o444)
        result = self.native_snapshot()
        self.assertEqual(5, len(result['entries']))
        self.assertEqual({'100644'}, {e['mode'] for e in result['entries']})
        self.assertEqual({hashlib.sha256(b'same\r\n').hexdigest()}, {e['sha256'] for e in result['entries']})

    def test_tracked_index_mode_and_unstaged_bytes_with_real_deletion(self):
        self.repository()
        (self.target / 'program').write_bytes(b'unstaged bytes\r\n')
        index = (self.target / '.git/index').read_bytes()
        result = self.native_snapshot(); entries = {e['path']: e for e in result['entries']}
        self.assertEqual('100755', entries['program']['mode'])
        self.assertEqual(hashlib.sha256(b'unstaged bytes\r\n').hexdigest(), entries['program']['sha256'])
        (self.target / 'plain').unlink()
        after = self.native_snapshot()
        self.assertEqual(['program'], [e['path'] for e in after['entries']])
        self.assertEqual(index, (self.target / '.git/index').read_bytes())
        manifest = work.make_manifest(result, after, scope=['plain'])
        self.assertEqual({'plain': 'post'}, work.preflight_changed_paths(self.target, manifest, verified_inventory_id='windows-2'))

    def test_mode_source_is_reobserved_when_file_enters_and_leaves_index(self):
        self.git('init')
        (self.target / 'new.exe').write_bytes(b'new')
        untracked = self.native_snapshot()
        self.git('add', 'new.exe'); self.git('update-index', '--chmod=+x', 'new.exe')
        tracked = self.native_snapshot()
        self.git('rm', '--cached', '-f', '--', 'new.exe')
        restored = self.native_snapshot()
        self.assertEqual('100644', untracked['entries'][0]['mode'])
        self.assertEqual('100755', tracked['entries'][0]['mode'])
        self.assertEqual(untracked, restored)
        self.assertEqual(['new.exe'], [x['path'] for x in work.make_manifest(untracked, tracked, scope=['new.exe'])['changes']])

    def test_native_snapshot_refuses_special_flags_and_unverified_window(self):
        self.repository(); self.git('update-index', '--skip-worktree', 'plain')
        (self.target / 'plain').unlink()
        with self.assertRaisesRegex(ContractError, 'special flags'):
            self.native_snapshot()
        with self.assertRaises(ContractError):
            work.snapshot(self.target)

    def test_ignored_physical_occupant_is_not_a_missing_or_applicable_post(self):
        self.repository(); (self.target / '.gitignore').write_text('new.txt\n')
        base = self.native_snapshot(); result = copy.deepcopy(base)
        result['entries'].append(self.entry('new.txt', data=b'new'))
        result['entries'].sort(key=lambda e: e['path'].encode())
        result['sha256'] = work._digest({k: v for k, v in result.items() if k != 'sha256'})
        manifest = work.make_manifest(base, result, scope=['new.txt'])
        self.assertEqual({'new.txt': 'pre'}, work.preflight_changed_paths(self.target, manifest, verified_inventory_id='windows-2'))
        (self.target / 'new.txt').write_bytes(b'new')
        self.assertEqual({'new.txt': 'neither'}, work.preflight_changed_paths(self.target, manifest, verified_inventory_id='windows-2'))
        self.assertEqual(base, self.native_snapshot())
