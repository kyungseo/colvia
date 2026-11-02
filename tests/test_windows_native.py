"""Native primitive evidence and portable import/runtime refusal checks.

WindowsNativeTests require a real admitted Windows interpreter and filesystem.
PortableNativeTests do not claim native Windows execution.
"""
import ast
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from unittest import mock

from hv2ref.errors import ContractError
from hv2ref import jsonio, workspace

SOURCE = Path(__file__).resolve().parents[1]


class PortableNativeTests(unittest.TestCase):

    def test_runtime_report_refuses_historical_windows_writer_baseline(self):
        with mock.patch.object(workspace.sys, 'platform', 'win32'):
            for window in (None, 'human-1', 'entry-1', 'delegation-1', 'continuation-1', 'windows-1'):
                self.assertFalse(workspace.runtime_supported(window))
            with mock.patch.object(workspace, 'windows_runtime_observation', return_value={'supported': True}) as observed:
                self.assertTrue(workspace.runtime_supported('windows-2')); observed.assert_called_once_with()

    def test_windows_publication_failure_diagnostics_preserve_actual_prefix(self):
        # Portable error injection; native path/volume guarantees are separate.
        with tempfile.TemporaryDirectory() as root:
            root = Path(root); stage = root / 'stage'; stage.mkdir(); (stage / 'bytes').write_bytes(b'original')
            destination = root / 'published'; leaf = root / 'leaf'; leaf.write_bytes(b'keep')
            def observe(path, **kwargs):
                exists = path.exists(); info = path.stat() if exists else path.parent.stat()
                return {'exists': exists, 'directory': path.is_dir(), 'volume': info.st_dev,
                        'identity': (info.st_dev, info.st_ino), 'attributes': 0}
            error = OSError('synthetic sharing violation'); error.winerror = 32
            with mock.patch.object(jsonio.sys, 'platform', 'win32'), mock.patch.object(jsonio, 'windows_path_observation', side_effect=observe):
                with mock.patch.object(os, 'rename', side_effect=error) as rename:
                    with self.assertRaisesRegex(ContractError, 'phase=directory-publication; winerror=32.*staged=directory; published=missing'):
                        jsonio.rename_directory(stage, destination)
                    rename.assert_called_once_with(stage, destination)
                self.assertEqual(b'original', (stage / 'bytes').read_bytes()); self.assertFalse(destination.exists())
                jsonio.rename_directory(stage, destination)
                self.assertEqual(b'original', (destination / 'bytes').read_bytes()); self.assertFalse(stage.exists())
                late_stage = root / 'late-stage'; late_stage.mkdir(); (late_stage / 'bytes').write_bytes(b'published')
                late_target = root / 'late-target'
                def unavailable_after_publication(path, **kwargs):
                    if path == late_target and path.exists(): raise PermissionError('post-publication observation unavailable')
                    return observe(path, **kwargs)
                with mock.patch.object(jsonio, 'windows_path_observation', side_effect=unavailable_after_publication):
                    with self.assertRaisesRegex(ContractError, 'phase=post-directory-publication; publication occurred'):
                        jsonio.rename_directory(late_stage, late_target)
                self.assertFalse(late_stage.exists()); self.assertEqual(b'published', (late_target / 'bytes').read_bytes())
                with mock.patch.object(Path, 'unlink', side_effect=error) as unlink:
                    with self.assertRaisesRegex(ContractError, 'phase=file-removal; winerror=32.*target=file'):
                        jsonio.remove_path(leaf)
                    self.assertEqual(1, unlink.call_count)
                self.assertEqual(b'keep', leaf.read_bytes())
                with mock.patch.object(Path, 'unlink', side_effect=error), mock.patch.object(jsonio, 'windows_path_observation', side_effect=PermissionError('unavailable')):
                    with self.assertRaisesRegex(ContractError, 'target=unavailable'):
                        jsonio.remove_path(leaf)
                jsonio.remove_path(leaf); self.assertFalse(leaf.exists())
                empty = root / 'empty'; empty.mkdir()
                with mock.patch.object(Path, 'rmdir', side_effect=error):
                    with self.assertRaisesRegex(ContractError, 'phase=directory-removal; winerror=32.*target=directory'):
                        jsonio.remove_path(empty, directory=True)
                self.assertTrue(empty.is_dir()); jsonio.remove_path(empty, directory=True); self.assertFalse(empty.exists())


    def test_detach_read_handle_transfers_once_and_closes_on_failure(self):
        from types import SimpleNamespace
        target, parent, leaf, outside, opened, overrides, closed = self._detach_read_fixture()
        fds = []; closed_fds = []; actual_close = os.close
        def adopt(handle, flags):
            fd = os.open(handle, flags); fds.append(fd); return fd
        def close(fd):
            closed_fds.append(fd); actual_close(fd)
        with mock.patch.dict(sys.modules, {"msvcrt": SimpleNamespace(open_osfhandle=adopt)}), \
             mock.patch.object(os, "close", side_effect=close):
            with jsonio._windows_detach_read_scope(target, capture_serial=True):
                for error in (False, True):
                    try:
                        with jsonio._windows_open_read(leaf) as (native, fd):
                            self.assertTrue(native["exists"])
                            self.assertEqual(b"first", os.read(fd, 10))
                            if error: raise PermissionError("after transfer")
                    except PermissionError:
                        self.assertTrue(error)
        self.assertEqual(fds, closed_fds)
        self.assertEqual(2, opened.count(leaf))
        self.assertNotIn(leaf, closed)  # The descriptor owns these handles.
        self.assertIsNone(jsonio._windows_detach_read_observation.get())

    def test_detach_read_handle_failed_transfer_closes_native_handle(self):
        from types import SimpleNamespace
        target, parent, leaf, outside, opened, overrides, closed = self._detach_read_fixture()
        def denied(*args): raise OSError("descriptor transfer denied")
        with mock.patch.dict(sys.modules, {"msvcrt": SimpleNamespace(open_osfhandle=denied)}):
            with self.assertRaisesRegex(OSError, "descriptor transfer denied"):
                with jsonio._windows_detach_read_scope(target, capture_serial=True):
                    with jsonio._windows_open_read(leaf): self.fail("must not yield")
        self.assertEqual(1, closed.count(leaf))
        self.assertEqual(len(opened), len(closed))
        self.assertIsNone(jsonio._windows_detach_read_observation.get())

    def test_detach_read_handle_rejects_alias_before_transfer(self):
        from types import SimpleNamespace
        target, parent, leaf, outside, opened, overrides, closed = self._detach_read_fixture()
        overrides[leaf] = {"final_name": str(outside)}
        adopt = mock.Mock()
        with mock.patch.dict(sys.modules, {"msvcrt": SimpleNamespace(open_osfhandle=adopt)}):
            with self.assertRaisesRegex(ContractError, "alias or changed"):
                with jsonio._windows_detach_read_scope(target, capture_serial=True):
                    with jsonio._windows_open_read(leaf): self.fail("must not yield")
        adopt.assert_not_called()
        self.assertEqual(len(opened), len(closed))

    def test_detach_batch_bounds_workers_inherits_scope_and_keeps_order(self):
        import threading
        from contextvars import ContextVar
        target, parent, leaf, outside, opened, overrides, closed = self._detach_read_fixture()
        marker = ContextVar("test_detach_batch_marker", default=None)
        token = marker.set("caller")
        self.addCleanup(marker.reset, token)
        barrier = threading.Barrier(4, timeout=3)
        threads = set()
        with jsonio._windows_detach_read_scope(target, capture_serial=True):
            scope = jsonio._windows_detach_read_observation.get()
            def read(number):
                self.assertIs(scope, jsonio._windows_detach_read_observation.get())
                self.assertEqual("caller", marker.get())
                threads.add(threading.get_ident())
                barrier.wait()
                jsonio.windows_path_observation(leaf)
                return number, leaf.read_bytes()
            self.assertEqual([(n, b"first") for n in range(8)], scope.read_batch(read, range(8)))
            self.assertEqual(4, len(threads))
            leaf.write_bytes(b"changed")
            self.assertEqual([(n, b"changed") for n in range(8)], scope.read_batch(read, range(8)))
            self.assertEqual(16, opened.count(leaf))
        self.assertTrue(scope.closed)
        self.assertIsNone(scope._executor)
        self.assertFalse(any(t.name.startswith("colvia-detach-read") for t in threading.enumerate()))
        self.assertIsNone(jsonio._windows_detach_read_observation.get())
        self.assertEqual(len(opened), len(closed))

    def test_detach_batch_error_joins_sibling_and_closes_scope(self):
        import threading
        target, parent, leaf, outside, opened, overrides, closed = self._detach_read_fixture()
        started, finished = threading.Event(), threading.Event()
        def read(number):
            if number == 0:
                self.assertTrue(started.wait(3))
                raise PermissionError("current content unavailable")
            started.set()
            try:
                time.sleep(.05)
                return leaf.read_bytes()
            finally:
                finished.set()
        with self.assertRaisesRegex(PermissionError, "current content unavailable"):
            with jsonio._windows_detach_read_scope(target, capture_serial=True):
                scope = jsonio._windows_detach_read_observation.get()
                scope.read_batch(read, [0, 1])
        self.assertTrue(finished.is_set())
        self.assertTrue(scope.closed)
        self.assertIsNone(scope._executor)
        self.assertFalse(any(t.name.startswith("colvia-detach-read") for t in threading.enumerate()))
        self.assertIsNone(jsonio._windows_detach_read_observation.get())
        with self.assertRaisesRegex(ContractError, "invalid detach read batch"):
            scope.read_batch(lambda value: value, [1, 2])
        with jsonio._windows_detach_read_scope(target, capture_serial=True):
            self.assertEqual([b"first", b"first"], jsonio._windows_detach_read_observation.get().read_batch(lambda p: p.read_bytes(), [leaf, leaf]))

    def test_detach_batch_concurrent_ancestor_conflict_is_not_overwritten(self):
        import threading
        target, parent, leaf, outside, opened, overrides, closed = self._detach_read_fixture()
        barrier = threading.Barrier(2, timeout=3)
        with self.assertRaisesRegex(ContractError, "ancestor changed"):
            with jsonio._windows_detach_read_scope(target, capture_serial=True):
                scope = jsonio._windows_detach_read_observation.get()
                def observe(identity):
                    barrier.wait()
                    scope.remember(parent, {"directory": True, "identity": identity, "attributes": 16, "final_name": str(parent)})
                scope.read_batch(observe, [1, 2])
        self.assertTrue(scope.closed)
        self.assertEqual({}, scope.directories)
        self.assertIsNone(jsonio._windows_detach_read_observation.get())

    def test_detach_parallel_snapshot_keeps_post_read_signature_guard(self):
        import hashlib
        from types import SimpleNamespace
        from hv2ref import work
        target, parent, leaf, outside, opened, overrides, closed = self._detach_read_fixture()
        root = target / ".hrn"; root.mkdir()
        for name in ("format.json", ".gitignore"):
            (root / name).write_bytes(b"original")
        observation = work._LifecycleVisibility.__new__(work._LifecycleVisibility)
        observation.target = target; observation._detach_topology = object()
        def stable(path):
            data = path.read_bytes()
            if path.name == "format.json": path.write_bytes(b"changed length")
            return hashlib.sha256(data).hexdigest(), len(data), "100644"
        with mock.patch.object(work, "sys", SimpleNamespace(platform="win32")), mock.patch.object(work, "_stable_file", side_effect=stable):
            with self.assertRaisesRegex(ContractError, "unstable lifecycle observation member"):
                with jsonio._windows_detach_read_scope(target, capture_serial=True):
                    observation._snapshot()
        self.assertIsNone(jsonio._windows_detach_read_observation.get())

    def test_switch_preflight_does_not_capture_detach_serial_bytes(self):
        import hashlib
        from contextlib import nullcontext
        from types import SimpleNamespace
        from hv2ref import product, work
        target, parent, leaf, outside, opened, overrides, closed = self._detach_read_fixture()
        calls = []
        def stable(path, **kwargs):
            calls.append(kwargs); self.assertFalse(kwargs)
            data = path.read_bytes(); return (hashlib.sha256(data).hexdigest(), len(data), '100644')
        def records(*args, **kwargs):
            self.assertFalse(jsonio._windows_detach_read_observation.get().capture_serial)
            return product._serial_file(leaf)
        with mock.patch.object(product, 'sys', SimpleNamespace(platform='win32')), \
             mock.patch.object(work, '_lifecycle_git_observation', side_effect=lambda root: nullcontext()), \
             mock.patch.object(product, '_switch_preflight_records', side_effect=records), \
             mock.patch.object(work, '_stable_file', side_effect=stable):
            self.assertEqual(b'first', product._switch_preflight(target, {}, recover=False))
            with jsonio._windows_detach_read_scope(target): self.assertEqual(b'first', product._serial_file(leaf))
        self.assertEqual([{}, {}, {}, {}], calls)
        self.assertIsNone(jsonio._windows_detach_read_observation.get())


    def test_detach_serial_bytes_scope_and_fallback_are_independent(self):
        import hashlib
        from hv2ref import product, work
        target, parent, leaf, outside, opened, overrides, closed = self._detach_read_fixture()
        calls = []
        def stable(path, **kwargs):
            data = path.read_bytes(); evidence = (hashlib.sha256(data).hexdigest(), len(data), "100644")
            calls.append((path, kwargs))
            return (evidence, data) if kwargs.get('_capture_bytes') else evidence
        with mock.patch.object(work, '_stable_file', side_effect=stable), mock.patch.object(sys, 'platform', 'win32'):
            with jsonio._windows_detach_read_scope(target, capture_serial=True):
                self.assertEqual(b'first', product._serial_file(leaf))
                leaf.write_bytes(b'new bytes')
                self.assertEqual(b'new bytes', product._serial_file(leaf))
                self.assertEqual(b'other', product._serial_file(outside))
            self.assertEqual(b'new bytes', product._serial_file(leaf))
        self.assertEqual([{'_capture_bytes': True}, {'_capture_bytes': True}, {}, {}, {}, {}],
                         [kwargs for _, kwargs in calls])
        self.assertIsNone(jsonio._windows_detach_read_observation.get())

    def test_detach_serial_captured_bytes_are_still_bound_to_evidence(self):
        from hv2ref import product, work
        target, parent, leaf, outside, opened, overrides, closed = self._detach_read_fixture()
        with mock.patch.object(sys, 'platform', 'win32'):
            for result in [(('0' * 64, 5, '100644'), b'first'), PermissionError('unavailable')]:
                with self.subTest(result=type(result).__name__):
                    def stable(*args, **kwargs):
                        if isinstance(result, Exception): raise result
                        return result
                    with mock.patch.object(work, '_stable_file', side_effect=stable):
                        with self.assertRaises((ContractError, PermissionError)):
                            with jsonio._windows_detach_read_scope(target, capture_serial=True): product._serial_file(leaf)
                    self.assertIsNone(jsonio._windows_detach_read_observation.get())

    def test_detach_serial_capture_keeps_repeated_binary_observation(self):
        from types import SimpleNamespace
        from hv2ref import product
        target, parent, leaf, outside, opened, overrides, closed = self._detach_read_fixture()
        payload = b'one\r\ntwo\x1athree\x00last'; leaf.write_bytes(payload)
        actual_read = os.read; chunks = []
        def read(fd, size):
            data = actual_read(fd, size); chunks.append(data); return data
        with mock.patch.dict(sys.modules, {'msvcrt': SimpleNamespace(get_osfhandle=lambda fd: fd, open_osfhandle=lambda handle, flags: os.open(handle, flags))}), \
             mock.patch.object(sys, 'platform', 'win32'), \
             mock.patch.object(jsonio, 'windows_verify_handle'), mock.patch.object(os, 'read', side_effect=read):
            with jsonio._windows_detach_read_scope(target, capture_serial=True):
                self.assertEqual(payload, product._serial_file(leaf))
        self.assertEqual([payload, payload], [c for c in chunks if c])
        self.assertIsNone(jsonio._windows_detach_read_observation.get())

    def test_detach_serial_capture_refuses_same_size_content_change(self):
        from types import SimpleNamespace
        from hv2ref import product
        target, parent, leaf, outside, opened, overrides, closed = self._detach_read_fixture()
        before = leaf.stat(); actual_read = os.read; changed = False
        def read(fd, size):
            nonlocal changed
            data = actual_read(fd, size)
            if data and not changed:
                changed = True; leaf.write_bytes(b'other')
                os.utime(leaf, ns=(before.st_atime_ns, before.st_mtime_ns))
            return data
        with mock.patch.dict(sys.modules, {'msvcrt': SimpleNamespace(get_osfhandle=lambda fd: fd, open_osfhandle=lambda handle, flags: os.open(handle, flags))}), \
             mock.patch.object(sys, 'platform', 'win32'), \
             mock.patch.object(jsonio, 'windows_verify_handle'), mock.patch.object(os, 'read', side_effect=read):
            with self.assertRaisesRegex(ContractError, 'repeated content observation'):
                with jsonio._windows_detach_read_scope(target, capture_serial=True): product._serial_file(leaf)
        self.assertTrue(changed); self.assertEqual(b'other', leaf.read_bytes())
        self.assertIsNone(jsonio._windows_detach_read_observation.get())


    def _detach_read_fixture(self):
        from contextlib import ExitStack
        from types import SimpleNamespace
        stack = ExitStack(); self.addCleanup(stack.close)
        root = Path(stack.enter_context(tempfile.TemporaryDirectory())).resolve()
        target = root / "target"; target.mkdir()
        parent = target / "parent"; parent.mkdir()
        leaf = parent / "file"; leaf.write_bytes(b"first")
        outside = root / "outside"; outside.mkdir(); (outside / "file").write_bytes(b"other")
        opened = []; overrides = {}; closed = []
        def open_path(path, **kwargs):
            path = Path(path); opened.append(path)
            if not path.exists():
                error = FileNotFoundError(str(path)); error.winerror = 2; raise error
            return path
        def state(path, **kwargs):
            value = {"identity": (1, str(path)), "attributes": 16 if path.is_dir() else 0,
                     "directory": path.is_dir(), "links": 1, "final_name": "\\\\?\\" + str(path),
                     "content_signature": (0, 0, 0, 0)}
            if isinstance(overrides.get(path), Exception): raise overrides[path]
            value.update(overrides.get(path, {})); return value
        api = SimpleNamespace(close=lambda h: closed.append(h), GetDriveTypeW=lambda drive: 3,
                              failure=lambda *args: ContractError('HV2-WINDOWS-IO', 'fixture unavailable'))
        stack.enter_context(mock.patch.object(jsonio, '_windows_absolute', side_effect=lambda p: Path(p).absolute()))
        stack.enter_context(mock.patch.object(jsonio, '_windows_api', return_value=api))
        stack.enter_context(mock.patch.object(jsonio, '_windows_open', side_effect=open_path))
        stack.enter_context(mock.patch.object(jsonio, '_windows_handle_state', side_effect=state))
        return target, parent, leaf, outside / 'file', opened, overrides, closed

    def test_detach_read_scope_reopens_leaves_ancestors_and_next_sweep(self):
        target, parent, leaf, outside, opened, overrides, closed = self._detach_read_fixture()
        for sweep in range(2):
            opened.clear(); closed.clear()
            with jsonio._windows_detach_read_scope(target):
                for _ in range(3): jsonio.windows_path_observation(leaf)
                self.assertEqual(1, opened.count(parent))
                self.assertEqual(3, opened.count(leaf))
            self.assertEqual(2, opened.count(parent))
            self.assertEqual(len(opened), len(closed))
            self.assertIsNone(jsonio._windows_detach_read_observation.get())

    def test_detach_read_scope_hot_prefix_keeps_leaf_fresh_and_exact_chain(self):
        target, parent, leaf, outside, opened, overrides, closed = self._detach_read_fixture()
        with jsonio._windows_detach_read_scope(target):
            first = jsonio.windows_path_observation(leaf)
            scope = jsonio._windows_detach_read_observation.get()
            self.assertIn(str(parent), scope.prefixes)
            overrides[leaf] = {"identity": (2, "new-leaf"), "content_signature": (1, 2, 3, 4)}
            current = jsonio.windows_path_observation(leaf)
            self.assertEqual(first["chain"][:-1], current["chain"][:-1])
            self.assertEqual((2, "new-leaf"), current["identity"])
            self.assertEqual((1, 2, 3, 4), current["content_signature"])
            self.assertEqual(2, opened.count(leaf))
            self.assertEqual(1, opened.count(parent))
        self.assertEqual(2, opened.count(parent))
        self.assertEqual({}, scope.prefixes)
        self.assertEqual({}, scope.lexical)
        self.assertEqual({}, scope.spellings)
        self.assertEqual(set(), scope.accepted)

    def test_detach_hot_spelling_still_opens_and_checks_leaf_failures(self):
        target, parent, leaf, outside, opened, overrides, closed = self._detach_read_fixture()
        with self.assertRaisesRegex(ContractError, 'fresh leaf failure'):
            with jsonio._windows_detach_read_scope(target):
                jsonio.windows_path_observation(leaf)
                scope = jsonio._windows_detach_read_observation.get()
                self.assertIn(str(leaf), scope.spellings)
                overrides[leaf] = ContractError('HV2-WINDOWS-IO', 'fresh leaf failure')
                jsonio.windows_path_observation(leaf)
        self.assertEqual(2, opened.count(leaf))
        self.assertEqual(len(opened), len(closed))
        self.assertEqual({}, scope.spellings)
        self.assertIsNone(jsonio._windows_detach_read_observation.get())

    def test_detach_hot_prefix_preserves_requested_windows_case_spelling(self):
        from pathlib import PureWindowsPath
        from types import SimpleNamespace
        root = PureWindowsPath("C:/root")
        paths = [root / "Dir/file", PureWindowsPath("C:/ROOT/DIR/file")]
        def observed(path, **kwargs):
            return {"identity": (1, str(path).casefold()), "attributes": 0 if path.name == "file" else 16,
                    "directory": path.name != "file", "links": 1,
                    "final_name": "\\\\?\\" + str(path), "content_signature": (0, 0, 0, 0)}
        api = SimpleNamespace(close=lambda h: None)
        with mock.patch.object(jsonio, "Path", PureWindowsPath), \
             mock.patch.object(jsonio, "_windows_absolute", side_effect=PureWindowsPath), \
             mock.patch.object(jsonio, "_windows_api", return_value=api), \
             mock.patch.object(jsonio, "_windows_open", side_effect=lambda p: p), \
             mock.patch.object(jsonio, "_windows_handle_state", side_effect=observed):
            with jsonio._windows_detach_read_scope(root):
                for path in paths:
                    result = jsonio.windows_path_observation(path)
                    self.assertEqual(tuple(str(p) for p in reversed((path, *path.parents))),
                                     tuple(row[0] for row in result["chain"]))

    def test_detach_read_scope_hot_prefix_rechecks_missing_parent(self):
        target, parent, leaf, outside, opened, overrides, closed = self._detach_read_fixture()
        with self.assertRaisesRegex(ContractError, "ancestor drift"):
            with jsonio._windows_detach_read_scope(target):
                jsonio.windows_path_observation(leaf)
                overrides[parent] = {"identity": (2, "changed-parent")}
                jsonio.windows_path_observation(parent / "missing", allow_missing=True)
        self.assertIsNone(jsonio._windows_detach_read_observation.get())
        self.assertEqual(len(opened) - 1, len(closed))  # Failed missing-leaf open has no handle.

    def test_detach_read_scope_spelling_cache_does_not_cache_relative_or_other_spelling(self):
        target, parent, leaf, outside, opened, overrides, closed = self._detach_read_fixture()
        original = jsonio._windows_absolute
        with mock.patch.object(jsonio, "_windows_absolute", wraps=original) as normalize:
            with jsonio._windows_detach_read_scope(target):
                jsonio.windows_path_observation(leaf)
                count = normalize.call_count
                jsonio.windows_path_observation(leaf)
                self.assertEqual(count, normalize.call_count)
                with mock.patch.object(jsonio, "_windows_absolute", side_effect=ContractError("HV2-WINDOWS-PATH", "invalid spelling")):
                    with self.assertRaisesRegex(ContractError, "invalid spelling"):
                        jsonio.windows_path_observation(parent / "file.")
                scope = jsonio._windows_detach_read_observation.get()
                relative = Path(os.path.relpath(leaf))
                scope.absolute(relative); scope.absolute(relative)
                self.assertNotIn(os.fspath(relative), scope.lexical)
                self.assertEqual(count + 2, normalize.call_count)

    def test_detach_read_scope_refuses_final_or_direct_ancestor_drift(self):
        target, parent, leaf, outside, opened, overrides, closed = self._detach_read_fixture()
        for direct in (False, True):
            overrides.clear()
            with self.subTest(direct=direct), self.assertRaisesRegex(ContractError, 'ancestor changed'):
                with jsonio._windows_detach_read_scope(target):
                    jsonio.windows_path_observation(leaf)
                    overrides[parent] = {'identity': (2, 'replacement')}
                    if direct: jsonio.windows_path_observation(parent)
            self.assertIsNone(jsonio._windows_detach_read_observation.get())
        overrides.clear()
        with jsonio._windows_detach_read_scope(target): jsonio.windows_path_observation(leaf)

    def test_detach_read_scope_does_not_share_mutation_or_outside_paths(self):
        target, parent, leaf, outside, opened, overrides, closed = self._detach_read_fixture()
        with jsonio._windows_detach_read_scope(target):
            jsonio.windows_path_observation(leaf)
            count = opened.count(parent)
            jsonio.windows_path_observation(leaf, mutation=True)
            jsonio.windows_path_observation(leaf, mutation=True)
            self.assertEqual(count + 2, opened.count(parent))
            jsonio.windows_path_observation(outside); jsonio.windows_path_observation(outside)
            self.assertEqual(2, opened.count(outside.parent))

    def test_detach_read_scope_absence_and_failure_do_not_escape_validation(self):
        target, parent, leaf, outside, opened, overrides, closed = self._detach_read_fixture()
        with self.assertRaisesRegex(ContractError, 'unsafe ancestor'):
            with jsonio._windows_detach_read_scope(target):
                jsonio.windows_path_observation(leaf)
                overrides[parent] = ContractError('HV2-WINDOWS-PATH', 'unsafe ancestor')
                jsonio.windows_path_observation(parent / 'missing', allow_missing=True)
        self.assertIsNone(jsonio._windows_detach_read_observation.get())
        overrides.clear()
        with jsonio._windows_detach_read_scope(target):
            with self.assertRaisesRegex(ContractError, 'nested'):
                with jsonio._windows_detach_read_scope(target): pass
            self.assertFalse(jsonio.windows_path_observation(parent / 'missing', allow_missing=True)['exists'])
        with self.assertRaisesRegex(RuntimeError, 'fixture abort'):
            with jsonio._windows_detach_read_scope(target): raise RuntimeError('fixture abort')
        self.assertIsNone(jsonio._windows_detach_read_observation.get())

    def test_detach_initial_read_rechecks_drift_and_clears_before_next_checkpoint(self):
        from contextlib import nullcontext
        from types import SimpleNamespace
        from hv2ref import product, work
        target, parent, leaf, outside, opened, overrides, closed = self._detach_read_fixture()
        def read(root):
            jsonio.windows_path_observation(leaf)
            return leaf.read_bytes()
        with mock.patch.object(product, "sys", SimpleNamespace(platform="win32")), \
             mock.patch.object(work, "_lifecycle_git_observation", side_effect=lambda root: nullcontext()):
            self.assertEqual(b"first", product._detach_initial_read(target, read))
            self.assertIsNone(jsonio._windows_detach_read_observation.get())
            leaf.write_bytes(b"second")
            self.assertEqual(b"second", product._detach_initial_read(target, read))
            def drift(root):
                result = read(root)
                overrides[parent] = {"identity": (9, "replacement")}
                return result
            with self.assertRaises(ContractError):
                product._detach_initial_read(target, drift)
            self.assertIsNone(jsonio._windows_detach_read_observation.get())

    def test_detach_two_sweeps_use_distinct_scopes_and_discard_failed_observation(self):
        from contextlib import nullcontext
        from types import SimpleNamespace
        from hv2ref import product, work
        target, parent, leaf, outside, opened, overrides, closed = self._detach_read_fixture()
        reads = []
        scopes = []
        class Topology:
            def __init__(self, root): self.closed = False
            def finish(self): self.closed = True
            def close(self): self.closed = True
        def read(root, observation):
            scope = jsonio._windows_detach_read_observation.get()
            self.assertIsNotNone(scope)
            scopes.append(scope)
            jsonio.windows_path_observation(leaf)
            reads.append(leaf.read_bytes())
            return {"classification": "partial", "receipt": reads[-1].decode()}
        with mock.patch.object(product, "sys", SimpleNamespace(platform="win32")), \
             mock.patch.object(work, "_detach_git_observation", side_effect=lambda *args: nullcontext()), \
             mock.patch.object(workspace, "_DetachTopologyObservation", Topology), \
             mock.patch.object(workspace, "classify_target", return_value={"target":str(target)}), \
             mock.patch.object(product, "_detach_observe_records", side_effect=read):
            self.assertEqual("partial", product.workspace_detached_status(target)["classification"])
            self.assertEqual(2, len(scopes))
            self.assertIsNot(scopes[0], scopes[1])
            self.assertIsNone(jsonio._windows_detach_read_observation.get())
            def drift(root, observation):
                result = read(root, observation)
                leaf.write_bytes(b"next sweep sees changed receipt")
                return result
            with mock.patch.object(product, "_detach_observe_records", side_effect=drift):
                with self.assertRaisesRegex(ContractError, "unstable detached state"):
                    product.workspace_detached_status(target)
            self.assertIsNone(jsonio._windows_detach_read_observation.get())

    def test_detach_initial_read_posix_keeps_existing_path(self):
        from types import SimpleNamespace
        from hv2ref import product, work
        value = object()
        with mock.patch.object(product, "sys", SimpleNamespace(platform="darwin")), \
             mock.patch.object(jsonio, "_windows_detach_read_scope", side_effect=AssertionError("native scope on POSIX")), \
             mock.patch.object(work, "_lifecycle_git_observation", side_effect=AssertionError("new Git scope on POSIX")):
            self.assertIs(value, product._detach_initial_read(Path("target"), lambda target: value))

    def test_switch_preflight_shares_only_ancestors_within_each_checkpoint(self):
        from contextlib import nullcontext
        from types import SimpleNamespace
        from hv2ref import product, work
        target, parent, leaf, outside, opened, overrides, closed = self._detach_read_fixture()
        def records(root, plan, *, recover):
            self.assertEqual(target, root); self.assertTrue(recover)
            for _ in range(3): jsonio.windows_path_observation(leaf)
            return ({'current': leaf.read_bytes()}, False)
        with mock.patch.object(product, 'sys', SimpleNamespace(platform='win32')), \
             mock.patch.object(work, '_lifecycle_git_observation', side_effect=lambda root: nullcontext()), \
             mock.patch.object(product, '_switch_preflight_records', side_effect=records):
            for expected in (b'first', b'changed'):
                leaf.write_bytes(expected); opened.clear(); closed.clear()
                self.assertEqual(({'current': expected}, False), product._switch_preflight(target, {}, recover=True))
                self.assertEqual(2, opened.count(parent))
                self.assertEqual(3, opened.count(leaf))
                self.assertEqual(len(opened), len(closed))
                self.assertIsNone(jsonio._windows_detach_read_observation.get())

    def test_switch_preflight_final_drift_or_error_prevents_next_publication(self):
        from contextlib import nullcontext
        from types import SimpleNamespace
        from hv2ref import product, work
        target, parent, leaf, outside, opened, overrides, closed = self._detach_read_fixture()
        published = []
        for failure in ('identity', 'attributes', 'final_name', 'read-error'):
            overrides.clear()
            def records(root, plan, *, recover):
                jsonio.windows_path_observation(leaf)
                if failure == 'read-error': raise ContractError('HV2-WINDOWS-PATH', 'read failure')
                overrides[parent] = {failure: {'identity': (2, 'new'), 'attributes': 17, 'final_name': 'other'}[failure]}
                return ({}, False)
            with self.subTest(failure=failure), \
                 mock.patch.object(product, 'sys', SimpleNamespace(platform='win32')), \
                 mock.patch.object(work, '_lifecycle_git_observation', side_effect=lambda root: nullcontext()), \
                 mock.patch.object(product, '_switch_preflight_records', side_effect=records):
                with self.assertRaises(ContractError):
                    product._switch_preflight(target, {}, recover=True)
                    published.append('must not reach next write')
                self.assertEqual([], published)
                self.assertIsNone(jsonio._windows_detach_read_observation.get())
                self.assertEqual(b'first', leaf.read_bytes())

    def test_switch_preflight_posix_keeps_existing_observation_path(self):
        from contextlib import nullcontext
        from types import SimpleNamespace
        from hv2ref import product, work
        value = ({'binding_ref': {'id': 'fixed'}}, False)
        with mock.patch.object(product, 'sys', SimpleNamespace(platform='darwin')), \
             mock.patch.object(jsonio, '_windows_detach_read_scope', side_effect=AssertionError('native scope on POSIX')), \
             mock.patch.object(work, '_lifecycle_git_observation', side_effect=lambda root: nullcontext()), \
             mock.patch.object(product, '_switch_preflight_records', return_value=value) as records:
            self.assertIs(value, product._switch_preflight(Path('target'), {}, recover=False))
            records.assert_called_once_with(Path('target'), {}, recover=False)

    def _final_name_api(self, replies):
        # API doubles use explicit UTF-16 counts; host wchar layout is not
        # native Windows evidence. No real file handle is opened here.
        import ctypes
        from types import SimpleNamespace
        calls = []
        values = iter(replies)
        def query(handle, buffer, capacity, flags):
            calls.append((handle, capacity, flags))
            length, value = next(values)
            if value is not None:
                buffer.value = value
            return length
        api = SimpleNamespace(C=ctypes, GetFinalPathNameByHandleW=query,
                              failure=lambda name, phase: ContractError('HV2-WINDOWS-IO', name + '; ' + phase))
        return api, calls

    def test_final_name_fast_path_keeps_flags_and_normalized_output(self):
        for flags, value in ((0, r'\\?\C:\fixture\leaf'), (1, r'\\?\Volume{fixture}\leaf')):
            api, calls = self._final_name_api([(len(value), value)])
            with self.subTest(flags=flags), mock.patch.object(jsonio, '_windows_api', return_value=api):
                self.assertEqual(value, jsonio._windows_final_name(73, flags))
            self.assertEqual([(73, 512, flags)], calls)

    def test_final_name_insufficient_buffer_retries_once(self):
        value = 'x' * 600
        api, calls = self._final_name_api([(601, None), (600, value)])
        with mock.patch.object(jsonio, '_windows_api', return_value=api):
            self.assertEqual(value, jsonio._windows_final_name(73, 1))
        self.assertEqual([(73, 512, 1), (73, 601, 1)], calls)

    def test_final_name_initial_failure_is_not_retried(self):
        api, calls = self._final_name_api([(0, None)])
        with mock.patch.object(jsonio, '_windows_api', return_value=api):
            with self.assertRaisesRegex(ContractError, 'GetFinalPathNameByHandleW; path-observation'):
                jsonio._windows_final_name(73)
        self.assertEqual([(73, 512, 0)], calls)

    def test_final_name_fallback_failure_is_not_hidden(self):
        api, calls = self._final_name_api([(700, None), (0, None)])
        with mock.patch.object(jsonio, '_windows_api', return_value=api):
            with self.assertRaises(ContractError):
                jsonio._windows_final_name(73)
        self.assertEqual(2, len(calls))

    def test_final_name_repeated_growth_or_oversize_refuses(self):
        for replies, count in (([(600, None), (600, None)], 2),
                               ([(600, None), (700, None)], 2),
                               ([(32769, None)], 1)):
            api, calls = self._final_name_api(replies)
            with self.subTest(replies=replies), mock.patch.object(jsonio, '_windows_api', return_value=api):
                with self.assertRaises(ContractError):
                    jsonio._windows_final_name(73)
            self.assertEqual(count, len(calls))

    def test_final_name_utf16_and_capacity_boundaries(self):
        for value in ('한글-🙂', 'x' * 511, 'x' * 32767):
            units = len(value.encode('utf-16-le')) // 2
            replies = [(units, value)] if units < 512 else [(units + 1, None), (units, value)]
            api, calls = self._final_name_api(replies)
            with self.subTest(units=units), mock.patch.object(jsonio, '_windows_api', return_value=api):
                self.assertEqual(value, jsonio._windows_final_name(73))
            self.assertEqual(1 if units < 512 else 2, len(calls))
            self.assertLessEqual(max(c[1] for c in calls), 32768)

    def test_non_ntfs_mutation_is_classified_before_native_identity_query(self):
        # API doubles verify refusal ordering; native FAT32 evidence is separate.
        import ctypes as C
        from types import SimpleNamespace
        for filesystem, volume_available in [('FAT32', True), ('exFAT', True), ('NTFS', True), ('NTFS', False)]:
            with self.subTest(filesystem=filesystem, volume_available=volume_available):
                def volume(_handle, _label, _label_size, _serial, _maximum, _flags, fs, _size):
                    fs.value = filesystem
                    return volume_available
                native_error = ContractError('HV2-WINDOWS-IO', 'synthetic native observation unavailable')
                api = SimpleNamespace(C=C, AttributeTag=C.c_int, FileId=C.c_int, Standard=C.c_int, Basic=C.c_int,
                                      GetVolumeInformationByHandleW=mock.Mock(side_effect=volume),
                                      GetFileInformationByHandleEx=mock.Mock(return_value=False),
                                      failure=mock.Mock(return_value=native_error))
                with mock.patch.object(jsonio, '_windows_api', return_value=api):
                    with self.assertRaises(ContractError) as caught:
                        jsonio._windows_handle_state(1, mutation=True)
                rejected = volume_available and filesystem != 'NTFS'
                self.assertEqual('HV2-WINDOWS-FILESYSTEM' if rejected else 'HV2-WINDOWS-IO', caught.exception.code)
                if rejected or not volume_available:
                    api.GetFileInformationByHandleEx.assert_not_called()
                else:
                    api.GetFileInformationByHandleEx.assert_called_once()
                if not rejected:
                    self.assertIs(native_error, caught.exception)

    def test_mutation_entries_reject_non_ntfs_before_read_identity(self):
        # Reproduce the early read failure without adding unsupported FS support.
        from types import SimpleNamespace
        from hv2ref import product
        target = Path('unsupported-target')
        def observe(_path, *, mutation=False, **_kwargs):
            code = 'HV2-WINDOWS-FILESYSTEM' if mutation else 'HV2-WINDOWS-IO'
            raise ContractError(code, 'synthetic unsupported filesystem')
        actions = (
            ('target', lambda: workspace.classify_target(target, mutation=True), 'HV2-WINDOWS-FILESYSTEM'),
            ('backup', lambda: product._repair_backup_path(target / 'backup', Path('ntfs-target'), Path('source')), 'HV2-WINDOWS-FILESYSTEM'),
            ('read-only', lambda: workspace.safe_target(target), 'HV2-WINDOWS-IO'),
        )
        for role, action, expected in actions:
            with self.subTest(role=role), mock.patch.object(workspace, 'sys', SimpleNamespace(platform='win32')):
                with mock.patch.object(jsonio, '_windows_absolute', side_effect=lambda path: Path(path)):
                    with mock.patch.object(jsonio, 'windows_path_observation', side_effect=observe):
                        with self.assertRaises(ContractError) as caught:
                            action()
                self.assertEqual(expected, caught.exception.code)

    def test_backend_is_not_loaded_by_posix_import(self):
        if sys.platform == "win32":
            self.assertIsNone(jsonio.fcntl)
        else:
            self.assertIsNotNone(jsonio.fcntl)
            with self.assertRaises(ContractError):
                jsonio._WindowsAPI()

    def test_replace_post_observation_failure_reports_publication_without_retry(self):
        from types import SimpleNamespace
        source, target = Path('source'), Path('target')
        before = {'volume': 'same', 'identity': 'source-id', 'attributes': 0}
        prior = {'volume': 'same', 'identity': 'prior-id', 'attributes': 0}
        error = OSError('synthetic observation IO'); error.winerror = 5
        failures = [ContractError('HV2-WINDOWS-IO', 'phase=path-observation; winerror=5'),
                    ContractError('HV2-WINDOWS-PATH', 'synthetic alias'), error]
        for failure in failures:
            with self.subTest(error=type(failure).__name__), mock.patch.object(jsonio, 'sys', SimpleNamespace(platform='win32')):
                with mock.patch.object(jsonio, 'windows_preflight_files'), mock.patch.object(jsonio, 'windows_path_observation', side_effect=[before, prior, failure]), mock.patch.object(os, 'replace') as replace:
                    with self.assertRaisesRegex(ContractError, 'phase=post-publication; publication occurred; preserve prefix') as caught:
                        jsonio.replace_file(source, target)
                    self.assertIs(failure, caught.exception.__cause__)
                    self.assertEqual(getattr(failure, 'code', 'HV2-WINDOWS-IO'), caught.exception.code)
                    replace.assert_called_once_with(source, target)
        with mock.patch.object(jsonio, 'sys', SimpleNamespace(platform='win32')), mock.patch.object(jsonio, 'windows_preflight_files'), mock.patch.object(os, 'replace') as replace:
            with mock.patch.object(jsonio, 'windows_path_observation', side_effect=[before, prior, before]):
                self.assertIsNone(jsonio.replace_file(source, target))
            replace.assert_called_once_with(source, target); replace.reset_mock()
            with mock.patch.object(jsonio, 'windows_path_observation', side_effect=failures[0]):
                with self.assertRaises(ContractError) as caught: jsonio.replace_file(source, target)
                self.assertIs(failures[0], caught.exception); replace.assert_not_called()
            with mock.patch.object(jsonio, 'windows_path_observation', side_effect=[before, prior, prior]):
                with self.assertRaisesRegex(ContractError, 'phase=post-publication; post-replace identity changed'):
                    jsonio.replace_file(source, target)
            replace.assert_called_once_with(source, target)

    def test_drive_relative_refused_before_os_path_resolution(self):
        for value in ("C:leaf", "C:"):
            with self.subTest(value=value), mock.patch.object(jsonio.os.path, "abspath", side_effect=AssertionError("must refuse before resolution")):
                with self.assertRaisesRegex(ContractError, "drive-relative"):
                    jsonio._windows_absolute(value)

    def test_reserved_spelling_refused_before_native_normalization(self):
        for value in (r"C:\safe\trailing.", r"C:\safe\trailing ", r"C:\safe\NUL.txt", r"C:\safe\file:stream"):
            with self.subTest(value=value), mock.patch.object(jsonio.os.path, "abspath", side_effect=AssertionError("must refuse before normalization")):
                with self.assertRaisesRegex(ContractError, "unsupported path component"):
                    jsonio._windows_absolute(value)

    def test_overlong_spelling_refused_before_native_resolution(self):
        for tail in ("x" * 245, "🙂" * 123):
            value = "C:/" + tail
            with self.subTest(units=len(value.encode("utf-16-le")) // 2), mock.patch.object(jsonio.os.path, "abspath", side_effect=AssertionError("must refuse before resolution")):
                with self.assertRaisesRegex(ContractError, "247 UTF-16"):
                    jsonio._windows_absolute(value)

    def test_windows_runtime_wrong_os_is_observed_without_write(self):
        with mock.patch.object(workspace.sys, "platform", "linux"):
            observed = workspace.windows_runtime_observation()
            self.assertFalse(observed["supported"])
            self.assertEqual("unsupported", observed["classification"])
            with self.assertRaisesRegex(ContractError, "windows-2 runtime unsupported"):
                workspace.require_supported_runtime("windows-2")

    def test_windows_runtime_tuple_policy_with_explicit_api_doubles(self):
        # These typed API doubles exercise policy branches; they are not real
        # x64/32-bit/emulated runtime observations or qualification evidence.
        import ctypes as C
        from ctypes import wintypes as W
        from types import SimpleNamespace
        from collections import namedtuple
        version_type = namedtuple("version_info", "major minor micro releaselevel serial")
        cpython_identity = SimpleNamespace(**{**vars(sys.implementation), "name": "cpython"})
        original_sizeof = C.sizeof
        cases = (
            ('native-arm64', 0, 0xAA64, 64, 10, 26100, 1, 0, 'supported'),
            ('native-x64', 0, 0x8664, 64, 10, 26100, 1, 0, 'supported'),
            ('emulated-x64-arm64', 0x8664, 0xAA64, 64, 10, 26100, 1, 0, 'unsupported'),
            ('emulated-x64-unknown-arm64', 0, 0xAA64, 64, 10, 26100, 1, 0, 'unsupported'),
            ('emulated-x86-x64', 0x014C, 0x8664, 32, 10, 26100, 1, 0, 'unsupported'),
            ('unknown-machine', 0, 0xFFFF, 64, 10, 26100, 1, 0, 'unsupported'),
            ('native-32-bit', 0, 0x8664, 32, 10, 26100, 1, 0, 'unsupported'),
            ('server', 0, 0xAA64, 64, 10, 26100, 3, 0, 'unsupported'),
            ('pre-windows11', 0, 0xAA64, 64, 10, 19045, 1, 0, 'unsupported'),
            ('older-major', 0, 0xAA64, 64, 6, 26100, 1, 0, 'unsupported'),
            ('version-unavailable', 0, 0xAA64, 64, 10, 26100, 1, 1, 'unknown'),
        )
        for label, process_code, native_code, bits, major, build, kind, status, expected in cases:
            with self.subTest(tuple=label):
                def machine(_handle, process_pointer, native_pointer):
                    C.cast(process_pointer, C.POINTER(W.USHORT)).contents.value = process_code
                    C.cast(native_pointer, C.POINTER(W.USHORT)).contents.value = native_code
                    return True
                query = mock.Mock()
                def version(pointer):
                    value = C.cast(pointer, query.argtypes[0]).contents
                    value.major, value.minor, value.build, value.product_type = major, 0, build, kind
                    return status
                query.side_effect = version
                kernel = SimpleNamespace(GetCurrentProcess=mock.Mock(return_value=1), IsWow64Process2=mock.Mock(side_effect=machine))
                libraries = {'kernel32': kernel, 'ntdll': SimpleNamespace(RtlGetVersion=query)}
                def sizeof(value):
                    return bits // 8 if value is C.c_void_p else original_sizeof(value)
                process_platform = 'win-amd64' if 'x64' in label or native_code == 0x8664 else 'win-arm64'
                with mock.patch.object(workspace.sys, 'platform', 'win32'), mock.patch.object(workspace.sys, 'version_info', version_type(3, 14, 7, 'final', 0)), mock.patch.object(workspace.sys, 'implementation', cpython_identity), mock.patch.object(C, 'WinDLL', side_effect=lambda name, **kw: libraries[name], create=True), mock.patch.object(C, 'sizeof', side_effect=sizeof), mock.patch('sysconfig.get_platform', return_value=process_platform), mock.patch('sysconfig.get_config_var', return_value=0):
                    result = workspace.windows_runtime_observation()
                    if expected == 'supported':
                        with mock.patch.object(workspace.sys, 'version_info', version_type(3, 14, 10, 'final', 0)):
                            newer = workspace.windows_runtime_observation()
                        self.assertFalse(newer['supported'])
                        self.assertEqual('unsupported', newer['classification'])
                self.assertEqual(expected, result['classification'], result)
                self.assertEqual(expected == 'supported', result['supported'])
                if status:
                    self.assertEqual(status, result['ntstatus'])
                else:
                    self.assertEqual((process_code, native_code, bits), (result['process_machine'], result['native_machine'], result['pointer_bits']))
        with mock.patch.object(workspace.sys, 'platform', 'win32'), mock.patch.object(C, 'WinDLL', side_effect=OSError('synthetic observation unavailable'), create=True):
            result = workspace.windows_runtime_observation()
        self.assertFalse(result['supported']); self.assertEqual('unknown', result['classification'])

    def test_windows_mutation_requires_each_interpreter_flag(self):
        from types import SimpleNamespace
        for isolated, no_bytecode in ((False, True), (True, False), (True, True)):
            with self.subTest(isolated=isolated, no_bytecode=no_bytecode):
                identity = SimpleNamespace(platform='win32', flags=SimpleNamespace(isolated=isolated), dont_write_bytecode=no_bytecode)
                with mock.patch.object(workspace, 'sys', identity), mock.patch.object(workspace, 'windows_runtime_observation', return_value={'supported': True}):
                    if isolated and no_bytecode:
                        workspace.require_supported_runtime('windows-2')
                    else:
                        with self.assertRaisesRegex(ContractError, 'explicit allowed Python -I -B'):
                            workspace.require_supported_runtime('windows-2')

    def test_window_runtime_cannot_be_inferred_from_os(self):
        with mock.patch.object(workspace.sys, "platform", "win32"):
            with self.assertRaisesRegex(ContractError, "verified windows-2"):
                workspace.require_supported_runtime()

    def test_launcher_runtime_probe_matches_shared_policy(self):
        launcher = ast.parse((SOURCE / "colvia").read_bytes())
        common = ast.parse((SOURCE / "src/hv2ref/workspace.py").read_bytes())
        def probe(tree):
            return next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "windows_runtime_observation")
        self.assertEqual(ast.dump(probe(launcher), include_attributes=False),
                         ast.dump(probe(common), include_attributes=False))

    def test_prepared_launcher_refuses_wrong_os_before_product_import(self):
        if sys.platform == "win32":
            # Native supported entry is covered by WindowsNativeTests; this case
            # explicitly injects only the platform identity in the bootstrap.
            prefix = "import sys,runpy;sys.platform='linux';sys.argv=sys.argv[1:];runpy.run_path(sys.argv[0],run_name='__main__')"
        else:
            prefix = "import sys,runpy;sys.argv=sys.argv[1:];runpy.run_path(sys.argv[0],run_name='__main__')"
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            script = root / "colvia"
            original = (SOURCE / "colvia").read_bytes()
            self.assertEqual(1, original.count(b'WORKSPACE_INVENTORY_ID = "continuation-1"'))
            script.write_bytes(original.replace(b'WORKSPACE_INVENTORY_ID = "continuation-1"', b'WORKSPACE_INVENTORY_ID = "windows-2"'))
            result = subprocess.run([sys.executable, "-I", "-B", "-c", prefix, str(script), "--source-checkout", "init"],
                                    cwd=root, capture_output=True, timeout=10)
            self.assertEqual(65, result.returncode, result.stderr)
            value = json.loads(result.stdout)
            self.assertEqual("unsupported", value["classification"])
            self.assertEqual([script], list(root.iterdir()))

    def test_explicit_preparation_changes_only_declared_managed_bytes(self):
        from hv2ref.product import workspace_candidate, WINDOWS_MANAGED_PATHS
        with tempfile.TemporaryDirectory() as name:
            output = Path(name) / "prepared"
            original = workspace_candidate(SOURCE)
            result = subprocess.run([sys.executable, "-I", "-B", str(SOURCE / "scripts/prepare-windows.py"),
                                     "--source", str(SOURCE), "--output", str(output)],
                                    capture_output=True, timeout=30)
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            prepared = workspace_candidate(output)
            self.assertEqual("windows-2", prepared["release_ref"]["inventory_id"])
            self.assertEqual(list(WINDOWS_MANAGED_PATHS), list(prepared["payload"]))
            self.assertEqual(["colvia"], [p for p in original["payload"] if original["payload"][p] != prepared["payload"][p]])
            self.assertEqual(original, workspace_candidate(SOURCE))
            report = json.loads((output / "preparation.json").read_bytes())
            self.assertEqual(prepared["release_ref"], report["output_release"])
            again = subprocess.run([sys.executable, "-I", "-B", str(SOURCE / "scripts/prepare-windows.py"),
                                    "--source", str(SOURCE), "--output", str(output)],
                                   capture_output=True, timeout=30)
            self.assertNotEqual(0, again.returncode)
            self.assertEqual(prepared, workspace_candidate(output))

    def test_source_profile_cannot_relabel_common_source(self):
        with tempfile.TemporaryDirectory() as name:
            target = Path(name)
            result = subprocess.run([sys.executable, "-I", "-B", str(SOURCE / "colvia"),
                                     "--source-checkout", "init", "--profile", "windows-2",
                                     "--target", str(target)], capture_output=True, timeout=15)
            self.assertEqual(65, result.returncode, result.stdout + result.stderr)
            self.assertIn("matching the prepared source", json.loads(result.stdout)["message"])
            self.assertEqual([], list(target.iterdir()))

    def test_windows_preview_wrong_os_refuses_without_publication(self):
        from hv2ref.product import workspace_init_preview
        with tempfile.TemporaryDirectory() as name:
            root = Path(name); prepared = root / "prepared"; target = root / "target"; target.mkdir()
            preparation = subprocess.run([sys.executable, "-I", "-B", str(SOURCE / "scripts/prepare-windows.py"),
                            "--source", str(SOURCE), "--output", str(prepared)], capture_output=True, timeout=30)
            self.assertEqual(0, preparation.returncode, preparation.stdout + preparation.stderr)
            # A process-wide sys.platform patch also switches file-observation
            # semantics on real Windows. Inject only the admission observation.
            unsupported = {"supported": False, "classification": "unsupported", "reason": "fixture wrong OS"}
            with mock.patch.object(workspace, "windows_runtime_observation", return_value=unsupported), self.assertRaisesRegex(ContractError, "windows-2 runtime unsupported"):
                workspace_init_preview(prepared, target, authority_home_id="fixture", operation_id="init-fixture", created_at="2026-01-01T00:00:00Z")
            self.assertEqual([], list(target.iterdir()))

    def test_parent_and_replace_preserve_posix_behavior(self):
        with tempfile.TemporaryDirectory() as name:
            path = Path(name) / "a" / "b.json"
            jsonio.write_new_json(path, {"one": 1})
            self.assertEqual({"one": 1}, jsonio.load_json(path, require_canonical=True))
            jsonio.replace_json(path, {"two": 2})
            self.assertEqual({"two": 2}, jsonio.load_json(path, require_canonical=True))
            self.assertEqual("pass", jsonio.sync_existing_file(path)["fsync"])
            self.assertEqual([path], list(path.parent.iterdir()))


@unittest.skipUnless(sys.platform == "win32", "native Windows mechanism; excluded from POSIX execution matrix")
class WindowsNativeTests(unittest.TestCase):

    def test_native_directory_publication_and_removal_failure_preserve_prefix(self):
        stage = self.root / 'stage'; stage.mkdir(); jsonio.write_new_bytes(stage / 'bytes', b'original')
        destination = self.root / 'published'; error = OSError('synthetic sharing violation'); error.winerror = 32
        with mock.patch.object(os, 'rename', side_effect=error) as rename:
            with self.assertRaisesRegex(ContractError, 'phase=directory-publication; winerror=32.*staged=directory; published=missing'):
                jsonio.rename_directory(stage, destination)
            rename.assert_called_once_with(stage, destination)
        self.assertEqual(b'original', (stage / 'bytes').read_bytes()); self.assertFalse(destination.exists())
        jsonio.rename_directory(stage, destination); self.assertEqual(b'original', (destination / 'bytes').read_bytes())
        leaf = destination / 'bytes'
        with mock.patch.object(Path, 'unlink', side_effect=error):
            with self.assertRaisesRegex(ContractError, 'phase=file-removal; winerror=32.*target=file'):
                jsonio.remove_path(leaf)
        self.assertEqual(b'original', leaf.read_bytes()); jsonio.remove_path(leaf); self.assertFalse(leaf.exists())
        with mock.patch.object(Path, 'rmdir', side_effect=error):
            with self.assertRaisesRegex(ContractError, 'phase=directory-removal; winerror=32.*target=directory'):
                jsonio.remove_path(destination, directory=True)
        self.assertTrue(destination.is_dir()); jsonio.remove_path(destination, directory=True)


    def test_detach_native_read_handle_is_reused_without_skipping_observations(self):
        import msvcrt
        from hv2ref import work
        leaf = self.root / "read-handle"; leaf.write_bytes(b"one\r\ntwo\x1athree")
        actual_open, actual_adopt = jsonio._windows_open, msvcrt.open_osfhandle
        actual_observe = jsonio.windows_path_observation
        opens = []; descriptors = []; observed = []; raw_opens = []
        def open_native(path, **kwargs):
            if Path(path) == leaf: opens.append(kwargs)
            return actual_open(path, **kwargs)
        def adopt(handle, flags):
            fd = actual_adopt(handle, flags); descriptors.append(fd)
            self.assertFalse(os.get_inheritable(fd))
            return fd
        def observe(path, **kwargs):
            if Path(path) == leaf: observed.append(kwargs)
            return actual_observe(path, **kwargs)
        original_os_open = os.open
        def open_raw(path, *args, **kwargs):
            if Path(path) == leaf: raw_opens.append(path)
            return original_os_open(path, *args, **kwargs)
        with mock.patch.object(jsonio, "_windows_open", side_effect=open_native), \
             mock.patch.object(msvcrt, "open_osfhandle", side_effect=adopt), \
             mock.patch.object(jsonio, "windows_path_observation", side_effect=observe), \
             mock.patch.object(os, "open", side_effect=open_raw):
            with jsonio._windows_detach_read_scope(self.root, capture_serial=True):
                evidence, data = work._stable_file(leaf, _capture_bytes=True)
        self.assertEqual(b"one\r\ntwo\x1athree", data)
        self.assertEqual(4, len(observed))
        self.assertEqual(4, len(opens))
        self.assertEqual({"access": 0x80000000, "share": 3}, opens[0])
        self.assertEqual([{}, {}, {}], opens[1:])
        self.assertEqual([], raw_opens)
        self.assertEqual(1, len(descriptors))
        with self.assertRaises(OSError): os.fstat(descriptors[0])
        self.assertIsNone(jsonio._windows_detach_read_observation.get())

    def test_detach_native_read_handle_transfer_error_closes_all_handles(self):
        import msvcrt
        from hv2ref import work
        leaf = self.root / "read-handle"; leaf.write_bytes(b"preserve")
        api = jsonio._windows_api(); original_open = jsonio._windows_open
        opened = []; closed = []; original_close = api.close
        def open_native(path, **kwargs):
            handle = original_open(path, **kwargs); opened.append(handle); return handle
        def close(handle):
            closed.append(handle); return original_close(handle)
        with mock.patch.object(jsonio, "_windows_open", side_effect=open_native), \
             mock.patch.object(api, "close", side_effect=close), \
             mock.patch.object(msvcrt, "open_osfhandle", side_effect=OSError("transfer denied")):
            with self.assertRaisesRegex(OSError, "transfer denied"):
                with jsonio._windows_detach_read_scope(self.root, capture_serial=True): work._stable_file(leaf)
        from collections import Counter
        self.assertEqual(Counter(opened), Counter(closed))
        self.assertEqual(b"preserve", leaf.read_bytes())
        self.assertIsNone(jsonio._windows_detach_read_observation.get())

    def test_detach_native_read_handle_stat_error_closes_transferred_descriptor(self):
        import msvcrt
        from hv2ref import work
        leaf = self.root / "read-handle"; leaf.write_bytes(b"preserve")
        original_adopt, original_stat = msvcrt.open_osfhandle, Path.lstat
        descriptors = []
        def adopt(handle, flags):
            fd = original_adopt(handle, flags); descriptors.append(fd); return fd
        def stat_path(path, *args, **kwargs):
            if path == leaf and descriptors: raise PermissionError("current metadata unavailable")
            return original_stat(path, *args, **kwargs)
        with mock.patch.object(msvcrt, "open_osfhandle", side_effect=adopt), \
             mock.patch.object(Path, "lstat", stat_path):
            with self.assertRaisesRegex(PermissionError, "current metadata unavailable"):
                with jsonio._windows_detach_read_scope(self.root, capture_serial=True): work._stable_file(leaf)
        self.assertEqual(1, len(descriptors))
        with self.assertRaises(OSError): os.fstat(descriptors[0])
        self.assertEqual(b"preserve", leaf.read_bytes())
        self.assertIsNone(jsonio._windows_detach_read_observation.get())

    def test_detach_parallel_native_reads_are_fresh_and_binary(self):
        import threading
        from hv2ref import product
        paths = [self.root / ("file-" + str(n)) for n in range(8)]
        first = b"one\r\ntwo\x1athree\x00last"
        for path in paths: path.write_bytes(first)
        with jsonio._windows_detach_read_scope(self.root, capture_serial=True):
            scope = jsonio._windows_detach_read_observation.get()
            self.assertEqual([first] * 8, scope.read_batch(product._serial_file, paths))
            for path in paths: path.write_bytes(b"new bytes")
            self.assertEqual([b"new bytes"] * 8, scope.read_batch(product._serial_file, paths))
        self.assertIsNone(jsonio._windows_detach_read_observation.get())
        self.assertFalse(any(t.name.startswith("colvia-detach-read") for t in threading.enumerate()))
        with jsonio._windows_detach_read_scope(self.root, capture_serial=True):
            self.assertEqual([b"new bytes"] * 8, jsonio._windows_detach_read_observation.get().read_batch(product._serial_file, paths))

    def test_detach_parallel_native_read_error_closes_every_fd(self):
        import threading
        import msvcrt
        from collections import Counter
        from hv2ref import product
        paths = [self.root / ("file-" + str(n)) for n in range(8)]
        for path in paths: path.write_bytes(b"preserve")
        actual_open, actual_close, actual_read = os.open, os.close, os.read
        opened, closed, names = [], [], {}
        actual_adopt = msvcrt.open_osfhandle
        def adopt(handle, flags):
            name = Path(jsonio._windows_final_name(handle)[4:])
            fd = actual_adopt(handle, flags); opened.append(fd); names[fd] = name; return fd
        def open_file(path, *args, **kwargs):
            fd = actual_open(path, *args, **kwargs); opened.append(fd); names[fd] = Path(path); return fd
        def close(fd):
            closed.append(fd); names.pop(fd, None); return actual_close(fd)
        def read(fd, count):
            if names.get(fd) == paths[0]: raise PermissionError("current content read denial")
            return actual_read(fd, count)
        with mock.patch.object(msvcrt, "open_osfhandle", side_effect=adopt), mock.patch.object(os, "open", side_effect=open_file), mock.patch.object(os, "close", side_effect=close), mock.patch.object(os, "read", side_effect=read):
            with self.assertRaisesRegex(PermissionError, "current content read denial"):
                with jsonio._windows_detach_read_scope(self.root, capture_serial=True):
                    jsonio._windows_detach_read_observation.get().read_batch(product._serial_file, paths)
        self.assertEqual(Counter(opened), Counter(closed)); self.assertEqual({}, names)
        self.assertIsNone(jsonio._windows_detach_read_observation.get())
        self.assertFalse(any(t.name.startswith("colvia-detach-read") for t in threading.enumerate()))
        self.assertEqual([b"preserve"] * 8, [path.read_bytes() for path in paths])

    def test_detach_serial_native_binary_fresh_and_readonly(self):
        from hv2ref import product
        for name in ('plain', 'program.exe', 'script.cmd'):
            path = self.root / name; payload = b'one\r\ntwo\x1athree\x00last'
            path.write_bytes(payload); path.chmod(0o444)
            try:
                with jsonio._windows_detach_read_scope(self.root, capture_serial=True):
                    self.assertEqual(payload, product._serial_file(path))
            finally: path.chmod(0o666)
            with jsonio._windows_detach_read_scope(self.root, capture_serial=True):
                self.assertEqual(payload, product._serial_file(path))
                path.write_bytes(b'different')
                self.assertEqual(b'different', product._serial_file(path))
        self.assertIsNone(jsonio._windows_detach_read_observation.get())

    def test_detach_serial_native_refuses_content_change_with_restored_mtime(self):
        from hv2ref import product
        path = self.root / 'content'; path.write_bytes(b'original')
        before = path.stat(); actual = os.read; changed = False
        def read(fd, count):
            nonlocal changed
            data = actual(fd, count)
            if data and not changed:
                changed = True; path.write_bytes(b'modified')
                os.utime(path, ns=(before.st_atime_ns, before.st_mtime_ns))
            return data
        with mock.patch.object(os, 'read', side_effect=read), self.assertRaisesRegex(ContractError, 'changed during'):
            with jsonio._windows_detach_read_scope(self.root, capture_serial=True): product._serial_file(path)
        self.assertTrue(changed); self.assertEqual(b'modified', path.read_bytes())
        self.assertEqual(before.st_mtime_ns, path.stat().st_mtime_ns)
        self.assertIsNone(jsonio._windows_detach_read_observation.get())

    def test_detach_serial_native_refuses_path_replacement_and_hardlink(self):
        from hv2ref import product
        path = self.root / 'content'; path.write_bytes(b'original')
        saved = self.root / 'saved'; actual = jsonio.windows_path_observation; count = 0
        def verify(p, **kwargs):
            nonlocal count
            count += 1
            # The first observation and both handle checks precede fd close.
            # Replace at the final path observation, after Windows releases it.
            if count == 4:
                path.rename(saved); path.write_bytes(b'original')
            return actual(p, **kwargs)
        with mock.patch.object(jsonio, 'windows_path_observation', side_effect=verify), self.assertRaises(ContractError):
            with jsonio._windows_detach_read_scope(self.root, capture_serial=True): product._serial_file(path)
        self.assertEqual(b'original', saved.read_bytes()); self.assertEqual(b'original', path.read_bytes())
        alias = self.root / 'alias'; os.link(path, alias)
        with self.assertRaisesRegex(ContractError, 'hardlinked product file'):
            with jsonio._windows_detach_read_scope(self.root, capture_serial=True): product._serial_file(path)
        self.assertEqual(b'original', alias.read_bytes())
        self.assertIsNone(jsonio._windows_detach_read_observation.get())

    def test_detach_serial_native_refuses_ancestor_replacement_and_missing_junction(self):
        from hv2ref import product
        parent = self.root / 'parent'; parent.mkdir(); leaf = parent / 'leaf'; leaf.write_bytes(b'preserve')
        saved = self.root / 'saved'
        with self.assertRaises(ContractError):
            with jsonio._windows_detach_read_scope(self.root, capture_serial=True):
                self.assertEqual(b'preserve', product._serial_file(leaf))
                parent.rename(saved); parent.mkdir(); (parent / 'leaf').write_bytes(b'preserve')
        junction = self.root / 'junction'
        result = subprocess.run(['cmd.exe', '/d', '/c', 'mklink', '/J', str(junction), str(saved)], capture_output=True, timeout=10)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        try:
            with self.assertRaises(ContractError):
                with jsonio._windows_detach_read_scope(self.root, capture_serial=True): product._serial_file(junction / 'leaf')
            with self.assertRaises((ContractError, OSError)):
                with jsonio._windows_detach_read_scope(self.root, capture_serial=True): product._serial_file(junction / 'missing')
        finally: os.rmdir(junction)
        self.assertEqual(b'preserve', (saved / 'leaf').read_bytes())
        self.assertIsNone(jsonio._windows_detach_read_observation.get())

    def test_detach_serial_native_read_error_closes_and_does_not_escape_scope(self):
        from hv2ref import product
        import msvcrt
        path = self.root / 'content'; path.write_bytes(b'preserve'); handles = []
        actual_open = os.open; actual_close = os.close; closed = []
        actual_adopt = msvcrt.open_osfhandle
        def adopt(handle, flags):
            fd = actual_adopt(handle, flags); handles.append(fd); return fd
        def opened(*args, **kwargs):
            fd = actual_open(*args, **kwargs); handles.append(fd); return fd
        def close(fd):
            closed.append(fd); return actual_close(fd)
        with mock.patch.object(msvcrt, 'open_osfhandle', side_effect=adopt), mock.patch.object(os, 'open', side_effect=opened), mock.patch.object(os, 'close', side_effect=close), \
             mock.patch.object(os, 'read', side_effect=PermissionError('injected read denial')):
            with self.assertRaises(PermissionError):
                with jsonio._windows_detach_read_scope(self.root, capture_serial=True): product._serial_file(path)
        self.assertEqual(handles, closed)
        self.assertIsNone(jsonio._windows_detach_read_observation.get())
        with jsonio._windows_detach_read_scope(self.root, capture_serial=True): self.assertEqual(b'preserve', product._serial_file(path))

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)

    def test_switch_preflight_native_scope_checks_current_bytes_and_ancestor_drift(self):
        from contextlib import nullcontext
        from hv2ref import product, work
        parent = self.root / 'scope'; parent.mkdir(); leaf = parent / 'bytes'; leaf.write_bytes(b'first')
        def records(root, plan, *, recover):
            return ({'current': jsonio.windows_bounded_bytes(leaf, 100)}, False)
        with mock.patch.object(work, '_lifecycle_git_observation', side_effect=lambda root: nullcontext()), \
             mock.patch.object(product, '_switch_preflight_records', side_effect=records):
            for expected in (b'first', b'changed'):
                leaf.write_bytes(expected)
                self.assertEqual(({'current': expected}, False), product._switch_preflight(self.root, {}, recover=True))
                self.assertIsNone(jsonio._windows_detach_read_observation.get())
        saved = self.root / 'saved'; published = []
        def replace_parent(root, plan, *, recover):
            result = records(root, plan, recover=recover)
            parent.rename(saved); parent.mkdir(); leaf.write_bytes(b'changed')
            return result
        with mock.patch.object(work, '_lifecycle_git_observation', side_effect=lambda root: nullcontext()), \
             mock.patch.object(product, '_switch_preflight_records', side_effect=replace_parent):
            with self.assertRaisesRegex(ContractError, 'ancestor changed'):
                product._switch_preflight(self.root, {}, recover=True)
                published.append('must not reach next write')
        self.assertEqual([], published)
        self.assertEqual(b'changed', (saved / 'bytes').read_bytes())
        self.assertEqual(b'changed', leaf.read_bytes())
        self.assertIsNone(jsonio._windows_detach_read_observation.get())

    def test_switch_read_phase_reopens_leaves_and_refuses_ancestor_replacement(self):
        from hv2ref import product
        parent = self.root / 'candidate'; parent.mkdir()
        leaf = parent / 'bytes'; leaf.write_bytes(b'first')
        for expected in (b'first', b'changed'):
            leaf.write_bytes(expected)
            with product._switch_read_scope(self.root):
                self.assertFalse(jsonio._windows_detach_read_observation.get().capture_serial)
                self.assertEqual(expected, product._serial_file(leaf))
            self.assertIsNone(jsonio._windows_detach_read_observation.get())
        saved = self.root / 'saved'; published = []
        with self.assertRaisesRegex(ContractError, 'ancestor changed'):
            with product._switch_read_scope(self.root):
                self.assertEqual(b'changed', product._serial_file(leaf))
                parent.rename(saved); parent.mkdir(); leaf.write_bytes(b'replacement')
            published.append('must not reach next write')
        self.assertEqual([], published)
        self.assertEqual(b'changed', (saved / 'bytes').read_bytes())
        self.assertEqual(b'replacement', leaf.read_bytes())
        self.assertIsNone(jsonio._windows_detach_read_observation.get())
        with product._switch_read_scope(self.root):
            self.assertEqual(b'replacement', product._serial_file(leaf))

    def test_completed_switch_read_scope_refreshes_truth_and_refuses_ancestor_change(self):
        import hashlib
        from hv2ref import product, work
        parent = self.root / 'completion'; parent.mkdir()
        leaf = parent / 'bytes'; leaf.write_bytes(b'first')
        plan = {'schema_version': 6, 'remove': [], 'operation_id': 'switch-a'}
        reads = []
        def truth(root, **kwargs):
            reads.append(product._serial_file(leaf))
            return [{'path': 'synthetic', 'sha256': hashlib.sha256(reads[-1]).hexdigest()}]
        def verified(root):
            self.assertFalse(jsonio._windows_detach_read_observation.get().capture_serial)
            product._serial_file(leaf)
            return {'binding_ref': {'id': 'switch-a'}}
        with mock.patch.object(product, 'verify_workspace_product', side_effect=verified), \
             mock.patch.object(product, '_lifecycle_truth', side_effect=truth):
            for content in (b'first', b'later'):
                leaf.write_bytes(content); reads.clear()
                plan['truth_refs'] = [{'path': 'synthetic', 'sha256': hashlib.sha256(content).hexdigest()}]
                result = product._entry_replay_result(self.root, plan, classification='updated')
                self.assertEqual('updated', result['classification'])
                self.assertEqual([content, content], reads)
                self.assertIsNone(jsonio._windows_detach_read_observation.get())
            stamp = leaf.stat(); reads.clear()
            def changed(root, **kwargs):
                if reads:
                    leaf.write_bytes(b'other'); os.utime(leaf, ns=(stamp.st_atime_ns, stamp.st_mtime_ns))
                return truth(root, **kwargs)
            with mock.patch.object(product, '_lifecycle_truth', side_effect=changed):
                with self.assertRaisesRegex(ContractError, 'truth changed during completed transition'):
                    product._entry_replay_result(self.root, plan, classification='updated')
            self.assertEqual([b'later', b'other'], reads)
            self.assertIsNone(jsonio._windows_detach_read_observation.get())
            saved = self.root / 'saved'; returned = []
            def replaced(root):
                value = verified(root)
                parent.rename(saved); parent.mkdir(); leaf.write_bytes(b'other')
                return value
            plan['truth_refs'] = [{'path': 'synthetic', 'sha256': hashlib.sha256(b'other').hexdigest()}]
            with mock.patch.object(product, 'verify_workspace_product', side_effect=replaced):
                with self.assertRaisesRegex(ContractError, 'ancestor changed'):
                    returned.append(product._entry_replay_result(self.root, plan, classification='replayed'))
            self.assertEqual([], returned)
            self.assertEqual(b'other', (saved / 'bytes').read_bytes())
            self.assertEqual(b'other', leaf.read_bytes())
            self.assertIsNone(jsonio._windows_detach_read_observation.get())
            self.assertIsNone(work._lifecycle_visibility.get())

    def test_completed_switch_read_scope_rechecks_git_policy_before_return(self):
        from hv2ref import product, work
        subprocess.run(['git', 'init', '-q', str(self.root)], check=True, capture_output=True, timeout=20)
        subprocess.run(['git', '-C', str(self.root), 'config', 'core.ignorecase', 'false'],
                       check=True, capture_output=True, timeout=20)
        home = self.root / '.hrn'; home.mkdir()
        leaf = home / 'format.json'; leaf.write_bytes(b'{}\n')
        plan = {'schema_version': 6, 'remove': [], 'operation_id': 'switch-a', 'truth_refs': []}
        def changed(root, **kwargs):
            subprocess.run(['git', '-C', str(self.root), 'config', 'core.ignorecase', 'true'],
                           check=True, capture_output=True, timeout=20)
            return []
        returned = []
        with mock.patch.object(product, 'verify_workspace_product', return_value={'binding_ref': {'id': 'switch-a'}}), \
             mock.patch.object(product, '_lifecycle_truth', side_effect=changed):
            with self.assertRaisesRegex(ContractError, 'Git policy changed during checkpoint'):
                returned.append(product._entry_replay_result(self.root, plan, classification='replayed'))
        self.assertEqual([], returned)
        self.assertEqual(b'{}\n', leaf.read_bytes())
        self.assertIsNone(work._lifecycle_visibility.get())
        self.assertIsNone(jsonio._windows_detach_read_observation.get())

    def test_continuation_reader_keeps_binary_canonical_and_identity_bounds(self):
        from hv2ref.continuation import _read_file
        path = self.root / 'continuation.json'; path.write_bytes(b'{}\n')
        self.assertEqual(b'{}\n', _read_file(path, 4096))
        path.write_bytes(b'{}\r\n')
        with self.assertRaises(ContractError): _read_file(path, 4096)
        path.write_bytes(b'{}\n')
        with self.assertRaises(ContractError): _read_file(path, 2)
        linked = self.root / 'hardlink.json'; os.link(path, linked)
        with self.assertRaises(ContractError): _read_file(path, 4096)
        self.assertEqual(b'{}\n', path.read_bytes())

    def test_detach_read_scope_native_reopens_and_keeps_binary_content_checks(self):
        parent = self.root / 'scope'; parent.mkdir(); leaf = parent / 'bytes'
        leaf.write_bytes(b'first\x00\xff')
        original = jsonio._windows_open; opened = []
        def record(path, **kwargs):
            opened.append(Path(path)); return original(path, **kwargs)
        for expected in (b'first\x00\xff', b'changed\x00'):
            leaf.write_bytes(expected); opened.clear()
            with mock.patch.object(jsonio, '_windows_open', side_effect=record):
                with jsonio._windows_detach_read_scope(self.root):
                    for _ in range(2): self.assertEqual(expected, jsonio.windows_bounded_bytes(leaf, 100))
                    self.assertEqual(1, opened.count(parent))
                    self.assertEqual(8, opened.count(leaf))
                self.assertEqual(2, opened.count(parent))
            self.assertIsNone(jsonio._windows_detach_read_observation.get())
        # Exercise the existing byte-race assertions inside the new ancestor
        # scope. Restored mtime must never substitute for fresh content reads.
        with jsonio._windows_detach_read_scope(self.root):
            self.test_bounded_read_callers_refuse_actual_content_change_with_restored_mtime()

    def test_detach_read_scope_native_refuses_replaced_ancestor_and_clears(self):
        parent = self.root / 'scope'; parent.mkdir(); leaf = parent / 'bytes'; leaf.write_bytes(b'unchanged')
        saved = self.root / 'saved'
        with self.assertRaisesRegex(ContractError, 'ancestor changed'):
            with jsonio._windows_detach_read_scope(self.root):
                self.assertEqual(b'unchanged', jsonio.windows_bounded_bytes(leaf, 100))
                parent.rename(saved); parent.mkdir(); leaf.write_bytes(b'unchanged')
        self.assertIsNone(jsonio._windows_detach_read_observation.get())
        self.assertEqual(b'unchanged', (saved / 'bytes').read_bytes())
        with jsonio._windows_detach_read_scope(self.root):
            self.assertEqual(b'unchanged', jsonio.windows_bounded_bytes(leaf, 100))

    def test_detach_read_scope_native_refuses_junction_under_missing_leaf(self):
        parent = self.root / 'scope'; parent.mkdir(); leaf = parent / 'bytes'; leaf.write_bytes(b'preserve')
        saved = self.root / 'saved'
        try:
            with self.assertRaisesRegex(ContractError, 'reparse'):
                with jsonio._windows_detach_read_scope(self.root):
                    self.assertEqual(b'preserve', jsonio.windows_bounded_bytes(leaf, 100))
                    parent.rename(saved)
                    result = subprocess.run(['cmd', '/d', '/c', 'mklink', '/J', str(parent), str(saved)], capture_output=True, timeout=10)
                    self.assertEqual(0, result.returncode, result.stdout + result.stderr)
                    self.assertTrue(parent.is_junction())
                    jsonio.windows_path_observation(parent / 'missing', allow_missing=True)
            self.assertIsNone(jsonio._windows_detach_read_observation.get())
            self.assertEqual(b'preserve', (saved / 'bytes').read_bytes())
        finally:
            if parent.is_junction(): parent.rmdir()
            if saved.exists() and not parent.exists(): saved.rename(parent)

    def child(self, body, *args, **kwargs):
        program = "import sys;sys.path.insert(0," + repr(str(SOURCE / "src")) + ");" + body
        return subprocess.Popen([sys.executable, "-I", "-B", "-c", program, *map(str, args)],
                                cwd=self.root, stdout=subprocess.PIPE, stderr=subprocess.PIPE, **kwargs)

    def test_replace_post_observation_failure_preserves_published_bytes(self):
        source, target = self.root / 'post-source', self.root / 'post-target'
        source.write_bytes(b'new publication'); target.write_bytes(b'prior publication')
        original_replace, original_observation = os.replace, jsonio.windows_path_observation
        published = []; error = ContractError('HV2-WINDOWS-IO', 'phase=path-observation; synthetic winerror=5')
        def replace(left, right, *args, **kwargs):
            result = original_replace(left, right, *args, **kwargs)
            published.append((left, right)); return result
        def observe(path, **kwargs):
            if published and Path(path) == target: raise error
            return original_observation(path, **kwargs)
        with mock.patch.object(os, 'replace', side_effect=replace), mock.patch.object(jsonio, 'windows_path_observation', side_effect=observe):
            with self.assertRaisesRegex(ContractError, 'phase=post-publication; publication occurred; preserve prefix') as caught:
                jsonio.replace_file(source, target)
        self.assertIs(error, caught.exception.__cause__); self.assertEqual('HV2-WINDOWS-IO', caught.exception.code)
        self.assertEqual([(source, target)], published); self.assertFalse(source.exists())
        self.assertEqual(b'new publication', target.read_bytes())
        self.assertTrue(jsonio.windows_path_observation(target, mutation=True)['exists'])

    def test_real_native_runtime_and_local_path(self):
        observed = workspace.windows_runtime_observation()
        self.assertTrue(observed["supported"], observed)
        self.assertEqual(0, observed["process_machine"])
        present = jsonio.windows_path_observation(self.root, mutation=True)
        missing = jsonio.windows_path_observation(self.root / "new" / "leaf", mutation=True, allow_missing=True)
        self.assertTrue(present["exists"])
        self.assertFalse(missing["exists"])
        self.assertEqual(present["identity"], missing["identity"])
        self.assertEqual(present["volume"], missing["volume"])

    def test_binary_stable_read_handles_path_and_fd_metadata(self):
        import hashlib
        from hv2ref.work import _stable_file
        payload = b"one\r\ntwo\x1athree\x00last\r\n"
        for name in ("plain", "program.exe", "script.cmd", "script.bat", "program.com"):
            with self.subTest(name=name):
                path = self.root / name; path.write_bytes(payload)
                self.assertEqual((hashlib.sha256(payload).hexdigest(), len(payload)), _stable_file(path)[:2])
                before = path.lstat()
                with path.open("rb") as handle:
                    opened = os.fstat(handle.fileno())
                print("NATIVE_STAT " + json.dumps({"name": name, "path_ctime_ns": before.st_ctime_ns,
                      "fd_ctime_ns": opened.st_ctime_ns, "path_mode": before.st_mode, "fd_mode": opened.st_mode}), flush=True)
        api = jsonio._windows_api()
        self.assertEqual(40, api.C.sizeof(api.Basic))

    def test_stable_read_refuses_real_change_with_restored_mtime(self):
        from hv2ref.work import _stable_file
        path = self.root / "content"; path.write_bytes(b"original")
        before = path.stat(); original_read = os.read; changed = False
        native_before = jsonio.windows_path_observation(path)["content_signature"]
        def changing_read(fd, count):
            nonlocal changed
            data = original_read(fd, count)
            if data and not changed:
                changed = True
                path.write_bytes(b"modified")
                os.utime(path, ns=(before.st_atime_ns, before.st_mtime_ns))
                native_after = jsonio.windows_path_observation(path)["content_signature"]
                print("NATIVE_CONTENT_CHANGE " + json.dumps({"before": native_before, "after": native_after,
                      "mtime_restored": path.stat().st_mtime_ns == before.st_mtime_ns}), flush=True)
            return data
        with mock.patch.object(os, "read", side_effect=changing_read):
            with self.assertRaisesRegex(ContractError, "changed during"):
                _stable_file(path)
        self.assertTrue(changed)
        self.assertEqual(b"modified", path.read_bytes())
        self.assertEqual(before.st_mtime_ns, path.stat().st_mtime_ns)

    def test_bounded_read_callers_preserve_binary_and_readonly_bytes(self):
        from hv2ref import candidates, view
        payload = b"one\r\ntwo\x1athree\x00last\r\n"
        for name in ("plain", "program.exe", "script.cmd", "script.bat", "program.com"):
            with self.subTest(name=name):
                path = self.root / name; path.write_bytes(payload); path.chmod(0o444)
                try:
                    native = jsonio.windows_path_observation(path)
                    self.assertEqual(payload, candidates._candidate_bytes(path))
                    self.assertEqual(payload, view.bounded_bytes(path))
                    after = jsonio.windows_path_observation(path)
                    self.assertEqual(native["chain"], after["chain"])
                    self.assertEqual(native["content_signature"], after["content_signature"])
                    self.assertTrue(path.stat().st_file_attributes & 1)
                finally:
                    path.chmod(0o666)

    def test_bounded_read_callers_enforce_limits_and_missing_classification(self):
        from hv2ref import candidates, view
        path = self.root / "bounded"
        for reader, limit in ((candidates._candidate_bytes, candidates.MAX_BYTES), (view.bounded_bytes, view.READ_LIMIT)):
            with self.subTest(limit=limit):
                path.write_bytes(b"x" * limit)
                self.assertEqual(limit, len(reader(path)))
                path.write_bytes(b"x" * (limit + 1))
                with self.assertRaisesRegex(ContractError, "LIMIT"):
                    reader(path)
                self.assertEqual(limit + 1, path.stat().st_size)
                with self.assertRaises(FileNotFoundError):
                    reader(self.root / "missing" / "leaf")
        self.assertEqual("missing", view.reference_observation(self.root, {"path": "absent", "sha256": "0" * 64}))

    def test_bounded_read_callers_refuse_hardlinks_and_junctions(self):
        from hv2ref import candidates, view
        original = self.root / "original"; original.write_bytes(b"preserve")
        linked = self.root / "linked"; os.link(original, linked)
        outside = self.root / "outside"; outside.mkdir(); (outside / "content").write_bytes(b"external")
        junction = self.root / "junction"
        result = subprocess.run(["cmd", "/d", "/c", "mklink", "/J", str(junction), str(outside)], capture_output=True, timeout=10)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertTrue(junction.is_junction())
        for reader in (candidates._candidate_bytes, view.bounded_bytes):
            for path in (original, linked, outside, junction, junction / "content"):
                with self.subTest(reader=reader.__name__, path=path.name), self.assertRaises(ContractError):
                    reader(path)
        self.assertEqual(b"preserve", original.read_bytes())
        self.assertEqual(b"external", (outside / "content").read_bytes())

    def test_bounded_read_callers_refuse_actual_content_change_with_restored_mtime(self):
        from hv2ref import candidates, view
        for number, reader in enumerate((candidates._candidate_bytes, view.bounded_bytes)):
            path = self.root / ("changing" + str(number)); path.write_bytes(b"original")
            before = path.stat(); original_read = os.read; changed = False
            def changing_read(fd, count):
                nonlocal changed
                data = original_read(fd, count)
                if data and not changed:
                    changed = True
                    path.write_bytes(b"modified")
                    os.utime(path, ns=(before.st_atime_ns, before.st_mtime_ns))
                return data
            with self.subTest(reader=reader.__name__), mock.patch.object(os, "read", side_effect=changing_read):
                with self.assertRaisesRegex(ContractError, "changed during"):
                    reader(path)
            self.assertTrue(changed)
            self.assertEqual(b"modified", path.read_bytes())
            self.assertEqual(before.st_mtime_ns, path.stat().st_mtime_ns)

    def test_existing_file_is_not_missing_ancestor(self):
        path = self.root / "file"
        path.write_bytes(b"data")
        with self.assertRaises(ContractError):
            jsonio.windows_path_observation(path / "child", mutation=True, allow_missing=True)

    def test_file_flush_replace_and_empty_anchor(self):
        path = self.root / "file"
        result = jsonio.write_new_bytes(path, b"before")
        self.assertEqual("FlushFileBuffers", result["method"])
        self.assertFalse(path.stat().st_file_attributes & 1)
        jsonio.replace_bytes(path, b"after")
        self.assertEqual(b"after", path.read_bytes())
        self.assertEqual("pass", jsonio.sync_existing_file(path)["fsync"])
        lock = self.root / "lock"
        with jsonio.exclusive_file_lock(lock):
            self.assertEqual(0, lock.stat().st_size)
            with self.assertRaises(OSError):
                lock.unlink()
            with self.assertRaises(OSError):
                lock.rename(self.root / "other")
        with jsonio.exclusive_file_lock(lock):
            pass

    def test_whole_union_readonly_refuses_before_new_publication(self):
        first, second, output = (self.root / n for n in ["first", "second", "new"])
        first.write_bytes(b"one"); second.write_bytes(b"two")
        second.chmod(0o444)
        self.addCleanup(second.chmod, 0o666)
        with self.assertRaisesRegex(ContractError, "read-only"):
            jsonio.windows_preflight_files([first, output, second])
            jsonio.write_new_bytes(output, b"must not publish")
        self.assertFalse(output.exists())
        self.assertEqual(b"two", second.read_bytes())
        self.assertTrue(second.stat().st_file_attributes & 1)
        self.assertTrue(jsonio.windows_path_observation(second)["exists"])
        with self.assertRaisesRegex(ContractError, "read-only"):
            jsonio.sync_existing_file(second)

    def test_reparse_junction_and_absent_child_refuse(self):
        outside = self.root / "outside"; outside.mkdir()
        junction = self.root / "junction"
        result = subprocess.run(["cmd", "/d", "/c", "mklink", "/J", str(junction), str(outside)],
                                capture_output=True, timeout=10)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        for path in [junction, junction / "missing"]:
            with self.subTest(path=path), self.assertRaisesRegex(ContractError, "reparse"):
                jsonio.windows_path_observation(path, mutation=True, allow_missing=True)
        self.assertEqual([], list(outside.iterdir()))

    def test_remote_and_reserved_namespace_refuse_before_create(self):
        for value in [self.root.drive + "relative", r"\\localhost\nonexistent\new", str(self.root / "NUL.txt"), str(self.root / "trailing."), str(self.root / "trailing ")]:
            with self.subTest(value=value), self.assertRaises(ContractError):
                jsonio.windows_path_observation(Path(value), mutation=True, allow_missing=True)
        self.assertEqual([], list(self.root.iterdir()))

    def test_lock_contender_waits_and_then_acquires(self):
        lock = self.root / "lock"; started = self.root / "started"; entered = self.root / "entered"
        body = "from pathlib import Path;from hv2ref.jsonio import exclusive_file_lock;Path(sys.argv[2]).write_text('started')\nwith exclusive_file_lock(Path(sys.argv[1])):Path(sys.argv[3]).write_text('entered')"
        child = None
        try:
            with jsonio.exclusive_file_lock(lock):
                child = self.child(body, lock, started, entered)
                until = time.monotonic() + 10
                while not started.exists() and child.poll() is None and time.monotonic() < until:
                    time.sleep(.02)
                self.assertTrue(started.exists())
                time.sleep(.2)
                self.assertIsNone(child.poll())
                self.assertFalse(entered.exists())
            out, err = child.communicate(timeout=10)
            self.assertEqual(0, child.returncode, out + err)
            self.assertEqual("entered", entered.read_text())
        finally:
            if child is not None and child.poll() is None:
                child.kill(); child.wait(timeout=10)

    def test_held_anchor_refuses_delete_replace_and_retains_waiter_until_release(self):
        lock = self.root / "lock"; replacement = self.root / "replacement"
        started = self.root / "started"; entered = self.root / "entered"
        replacement.write_bytes(b"replacement must remain intact\n")
        body = "from pathlib import Path;from hv2ref.jsonio import exclusive_file_lock;Path(sys.argv[2]).write_text('started')\nwith exclusive_file_lock(Path(sys.argv[1])):Path(sys.argv[3]).write_text('entered')"
        child = None; failures = []
        try:
            with jsonio.exclusive_file_lock(lock):
                before = lock.stat(); identity = (before.st_dev, before.st_ino)
                for name, attempt in (("delete", lock.unlink), ("replace", lambda: os.replace(replacement, lock))):
                    with self.assertRaises(OSError) as caught:
                        attempt()
                    observed = {"operation": name, "winerror": caught.exception.winerror}
                    print("NATIVE_LOCK_REFUSAL " + json.dumps(observed), flush=True)
                    self.assertIn(caught.exception.winerror, (5, 32), name)
                    failures.append(observed)
                    self.assertEqual(identity, (lock.stat().st_dev, lock.stat().st_ino))
                    # Byte-range locking also denies reads through a second handle.
                    self.assertEqual(0, lock.stat().st_size)
                    self.assertEqual(b"replacement must remain intact\n", replacement.read_bytes())
                child = self.child(body, lock, started, entered)
                until = time.monotonic() + 10
                while not started.exists() and child.poll() is None and time.monotonic() < until:
                    time.sleep(.02)
                self.assertTrue(started.exists())
                waiting_since = time.monotonic()
                while time.monotonic() - waiting_since < 5:
                    self.assertIsNone(child.poll())
                    self.assertFalse(entered.exists())
                    time.sleep(.05)
                waited = time.monotonic() - waiting_since
                self.assertIsNone(child.poll()); self.assertFalse(entered.exists())
            out, err = child.communicate(timeout=10)
            self.assertEqual(0, child.returncode, out + err)
            self.assertEqual("entered", entered.read_text())
            self.assertEqual(identity, (lock.stat().st_dev, lock.stat().st_ino))
            self.assertEqual(b"", lock.read_bytes())
            lock.unlink()  # Both cooperating handles have actually closed.
            os.replace(replacement, lock)
            self.assertEqual(b"replacement must remain intact\n", lock.read_bytes())
            print("NATIVE_LOCK_ANCHOR " + json.dumps({"failures": failures, "wait_seconds": waited,
                  "same_anchor_after_wait": True, "delete_replace_after_release": True}), flush=True)
        finally:
            if child is not None and child.poll() is None:
                child.kill(); child.communicate(timeout=10)

    def test_wait_interrupt_cancels_and_releases_handle(self):
        lock = self.root / "lock"; outcome = self.root / "outcome"
        body = r'''import ctypes,threading,time
from pathlib import Path
from hv2ref.jsonio import exclusive_file_lock
kernel=ctypes.WinDLL('kernel32',use_last_error=True)
kernel.SetConsoleCtrlHandler.argtypes=[ctypes.c_void_p,ctypes.c_int]
kernel.SetConsoleCtrlHandler.restype=ctypes.c_int
kernel.GenerateConsoleCtrlEvent.argtypes=[ctypes.c_ulong,ctypes.c_ulong]
kernel.GenerateConsoleCtrlEvent.restype=ctypes.c_int
if not kernel.SetConsoleCtrlHandler(None,False):raise ctypes.WinError(ctypes.get_last_error())
def interrupt():
 time.sleep(.5)
 if not kernel.GenerateConsoleCtrlEvent(0,0):raise ctypes.WinError(ctypes.get_last_error())
threading.Thread(target=interrupt,daemon=True).start()
try:
 with exclusive_file_lock(Path(sys.argv[1])):Path(sys.argv[2]).write_text('entered')
except KeyboardInterrupt:Path(sys.argv[2]).write_text('cancelled')
'''
        child = None
        try:
            with jsonio.exclusive_file_lock(lock):
                child = self.child(body, lock, outcome, creationflags=subprocess.CREATE_NEW_CONSOLE)
                out, err = child.communicate(timeout=10)
                self.assertEqual(0, child.returncode, out + err)
                self.assertEqual("cancelled", outcome.read_text())
            with jsonio.exclusive_file_lock(lock):
                pass
            lock.unlink()  # No pending child handle denies deletion.
        finally:
            if child is not None and child.poll() is None:
                child.kill(); child.wait(timeout=10)

    def test_interrupt_acquisition_interleavings_release_anchor(self):
        # Actual Ctrl+C in an isolated console; ordered cases cover both sides.
        # The overlap outcome is observed rather than prescribed by timing.
        body = r'''import ctypes,json,threading,time
from pathlib import Path
from hv2ref.jsonio import exclusive_file_lock
lock,ready,entered,trigger,outcome=map(Path,sys.argv[1:])
kernel=ctypes.WinDLL('kernel32',use_last_error=True)
kernel.SetConsoleCtrlHandler.argtypes=[ctypes.c_void_p,ctypes.c_int]
kernel.SetConsoleCtrlHandler.restype=ctypes.c_int
kernel.GenerateConsoleCtrlEvent.argtypes=[ctypes.c_ulong,ctypes.c_ulong]
kernel.GenerateConsoleCtrlEvent.restype=ctypes.c_int
if not kernel.SetConsoleCtrlHandler(None,False):raise ctypes.WinError(ctypes.get_last_error())
def interrupt():
 while not trigger.exists():time.sleep(.01)
 if not kernel.GenerateConsoleCtrlEvent(0,0):raise ctypes.WinError(ctypes.get_last_error())
threading.Thread(target=interrupt,daemon=True).start()
acquired=False
try:
 ready.write_text('ready')
 with exclusive_file_lock(lock):
  acquired=True;entered.write_text('entered')
  while True:time.sleep(.02)
except KeyboardInterrupt:
 outcome.write_text(json.dumps({'cancelled':True,'acquired':acquired}))
'''
        def wait_file(path, child):
            until = time.monotonic() + 10
            while not path.exists() and child.poll() is None and time.monotonic() < until:
                time.sleep(.01)
            self.assertTrue(path.exists(), (str(path), child.poll()))
        for mode in ('cancel-before-acquire', 'acquire-before-cancel', 'overlap'):
            with self.subTest(mode=mode):
                root = self.root / mode; root.mkdir()
                lock, ready, entered, trigger, outcome = [root / name for name in ('lock', 'ready', 'entered', 'trigger', 'outcome')]
                child = None
                try:
                    with jsonio.exclusive_file_lock(lock):
                        identity = jsonio.windows_path_observation(lock)['identity']
                        child = self.child(body, lock, ready, entered, trigger, outcome,
                                           creationflags=subprocess.CREATE_NEW_CONSOLE)
                        wait_file(ready, child)
                        if mode != 'acquire-before-cancel': trigger.write_text('interrupt')
                        if mode == 'cancel-before-acquire': out, err = child.communicate(timeout=10)
                    if mode == 'acquire-before-cancel':
                        wait_file(entered, child); trigger.write_text('interrupt')
                    if mode != 'cancel-before-acquire': out, err = child.communicate(timeout=10)
                    self.assertEqual(0, child.returncode, out + err)
                    observed = json.loads(outcome.read_text())
                    print('NATIVE_CANCEL_ACQUIRE ' + json.dumps({'mode': mode, **observed}), flush=True)
                    self.assertTrue(observed['cancelled'])
                    if mode != 'overlap': self.assertEqual(mode == 'acquire-before-cancel', observed['acquired'])
                    self.assertEqual(identity, jsonio.windows_path_observation(lock)['identity'])
                    self.assertEqual(b'', lock.read_bytes())
                    with jsonio.exclusive_file_lock(lock): pass
                    lock.unlink()  # No abandoned waiter/owner handle may remain.
                finally:
                    if child is not None and child.poll() is None:
                        child.kill(); child.wait(timeout=10)

    def test_live_child_does_not_inherit_lock_handle(self):
        lock = self.root / "lock"; ready = self.root / "ready"
        child = None
        try:
            with jsonio.exclusive_file_lock(lock):
                child = self.child("import time;from pathlib import Path;Path(sys.argv[1]).write_text('ready');time.sleep(60)", ready, close_fds=False)
                until = time.monotonic() + 10
                while not ready.exists() and child.poll() is None and time.monotonic() < until:
                    time.sleep(.02)
                self.assertTrue(ready.exists())
            self.assertIsNone(child.poll())
            lock.unlink()  # A live inherited deny-delete handle would block this.
            with jsonio.exclusive_file_lock(lock):
                pass
        finally:
            if child is not None:
                if child.poll() is None: child.kill()
                child.communicate(timeout=10)

    def test_terminated_holder_releases_same_empty_anchor(self):
        lock = self.root / "lock"; ready = self.root / "ready"
        body = "import time;from pathlib import Path;from hv2ref.jsonio import exclusive_file_lock\nwith exclusive_file_lock(Path(sys.argv[1])):Path(sys.argv[2]).write_text('held');time.sleep(60)"
        child = self.child(body, lock, ready)
        try:
            until = time.monotonic() + 10
            while not ready.exists() and child.poll() is None and time.monotonic() < until:
                time.sleep(.02)
            self.assertTrue(ready.exists())
            identity = jsonio.windows_path_observation(lock)["identity"]
            child.kill(); child.communicate(timeout=10)
            self.assertNotEqual(0, child.returncode)
            with jsonio.exclusive_file_lock(lock):
                self.assertEqual(identity, jsonio.windows_path_observation(lock)["identity"])
                self.assertEqual(0, lock.stat().st_size)
        finally:
            if child.poll() is None: child.kill(); child.communicate(timeout=10)

    def test_shared_destination_fails_one_replace_and_keeps_staging(self):
        destination = self.root / "destination"
        destination.write_bytes(b"original")
        api = jsonio._windows_api()
        handle = jsonio._windows_open(destination, access=0x80000000, share=1)
        try:
            with mock.patch.object(jsonio.os, "replace", wraps=os.replace) as replace:
                with self.assertRaisesRegex(ContractError, "replace-publication.*winerror=(5|32)"):
                    jsonio.replace_bytes(destination, b"replacement")
                self.assertEqual(1, replace.call_count)
            self.assertEqual(b"original", destination.read_bytes())
            staged = list(self.root.glob(".destination.hv2-tmp-*"))
            self.assertEqual(1, len(staged))
            self.assertEqual(b"replacement", staged[0].read_bytes())
            self.assertFalse(staged[0].stat().st_file_attributes & 1)
        finally:
            api.close(handle)

    def test_injected_required_file_flush_failure_keeps_original(self):
        destination = self.root / "destination"
        destination.write_bytes(b"original")
        api = jsonio._windows_api()
        def fail_flush(handle):
            api.C.set_last_error(5)
            return False
        with mock.patch.object(api, "FlushFileBuffers", side_effect=fail_flush):
            with self.assertRaisesRegex(ContractError, "file-content-before-publication.*winerror=5"):
                jsonio.replace_bytes(destination, b"replacement")
        self.assertEqual(b"original", destination.read_bytes())
        staged = list(self.root.glob(".destination.hv2-tmp-*"))
        self.assertEqual(1, len(staged))
        self.assertEqual(b"replacement", staged[0].read_bytes())

    def test_new_file_flush_failure_reports_visible_created_file(self):
        path = self.root / "created"
        api = jsonio._windows_api()
        def fail_flush(handle):
            api.C.set_last_error(5)
            return False
        with mock.patch.object(api, "FlushFileBuffers", side_effect=fail_flush):
            with self.assertRaisesRegex(ContractError, "result=failed; phase=created-file-content; winerror=5"):
                jsonio.write_new_bytes(path, b"visible but not flushed")
        self.assertEqual(b"visible but not flushed", path.read_bytes())

    def test_injected_directory_flush_errors_keep_narrow_allowlist(self):
        api = jsonio._windows_api()
        for error in (1, 50, 5, 32, 87):
            def fail_flush(handle):
                api.C.set_last_error(error)
                return False
            with self.subTest(error=error), mock.patch.object(api, "FlushFileBuffers", side_effect=fail_flush):
                if error in {1, 50}:
                    self.assertEqual("unavailable:winerror:" + str(error), jsonio.sync_directory(self.root))
                else:
                    with self.assertRaisesRegex(ContractError, "directory-sync.*winerror=" + str(error)):
                        jsonio.sync_directory(self.root)
        self.assertEqual([], list(self.root.iterdir()))

    def test_hardlinked_lock_anchor_is_refused_without_mutation(self):
        lock = self.root / "lock"; alias = self.root / "alias"
        lock.write_bytes(b""); os.link(lock, alias)
        with self.assertRaisesRegex(ContractError, "unsafe native lock anchor"):
            with jsonio.exclusive_file_lock(lock):
                self.fail("must not enter with shared anchor")
        self.assertEqual(b"", lock.read_bytes())
        alias.unlink()
        with jsonio.exclusive_file_lock(lock):
            pass

    def test_real_handle_identity_mismatch_and_attribute_drift_refuse(self):
        first = self.root / "first"; second = self.root / "second"
        first.write_bytes(b"one"); second.write_bytes(b"two")
        api = jsonio._windows_api(); handle = jsonio._windows_open(first)
        try:
            with self.assertRaisesRegex(ContractError, "identity or attributes changed"):
                jsonio.windows_verify_handle(second, handle)
            before = jsonio.windows_path_observation(first, mutation=True)
            first.chmod(0o444)
            try:
                with self.assertRaisesRegex(ContractError, "identity or attributes changed"):
                    jsonio.windows_verify_handle(first, handle, expected=before)
            finally:
                first.chmod(0o666)
        finally:
            api.close(handle)
        self.assertEqual(b"one", first.read_bytes())
        self.assertEqual(b"two", second.read_bytes())

    def test_volume_identity_drift_and_unavailable_observation_preserve_bytes(self):
        # Native handles plus explicitly injected observation faults. This does
        # not claim that an actual volume was remounted or a device failed.
        path = self.root / 'volume-probe'; path.write_bytes(b'preserve native bytes')
        expected = jsonio.windows_path_observation(path, mutation=True)
        api = jsonio._windows_api(); handle = jsonio._windows_open(path)
        try:
            current = dict(expected)
            current['identity'] = (expected['identity'][0] ^ 1, expected['identity'][1])
            with mock.patch.object(jsonio, 'windows_path_observation', return_value=current):
                with self.assertRaisesRegex(ContractError, 'identity or attributes changed'):
                    jsonio.windows_verify_handle(path, handle, expected=expected)
        finally:
            api.close(handle)
        denied = OSError('synthetic native access denied'); denied.winerror = 5
        with mock.patch.object(jsonio, '_windows_open', side_effect=denied):
            with self.assertRaisesRegex(ContractError, 'path-observation.*winerror=5'):
                jsonio.windows_path_observation(path, mutation=True, allow_missing=True)
        self.assertEqual(b'preserve native bytes', path.read_bytes())
        self.assertEqual(['volume-probe'], [p.name for p in self.root.iterdir()])

    def test_product_reads_and_git_metadata_refuse_junctions(self):
        from hv2ref.work import _stable_file, _regular_files
        outside = self.root / "outside"; outside.mkdir(); (outside / "file").write_bytes(b"outside bytes")
        project = self.root / "project"; project.mkdir()
        junction = project / "linked"
        created = subprocess.run(["cmd", "/d", "/c", "mklink", "/J", str(junction), str(outside)], capture_output=True, timeout=10)
        self.assertEqual(0, created.returncode, created.stdout + created.stderr)
        for observe in (lambda: _stable_file(junction / "file"), lambda: _regular_files(project)):
            with self.assertRaisesRegex(ContractError, "reparse"):
                observe()
        metadata = self.root / "metadata-project"; metadata.mkdir()
        created = subprocess.run(["cmd", "/d", "/c", "mklink", "/J", str(metadata / ".git"), str(outside)], capture_output=True, timeout=10)
        self.assertEqual(0, created.returncode, created.stdout + created.stderr)
        with mock.patch.object(workspace, "_topology_probe", side_effect=AssertionError("Git must not follow reparse metadata")):
            with self.assertRaisesRegex(ContractError, "reparse"):
                workspace.classify_target(metadata)
        self.assertEqual(b"outside bytes", (outside / "file").read_bytes())
