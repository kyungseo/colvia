"""Portable refusal checks; no native Windows qualification is claimed here."""
from contextlib import contextmanager, nullcontext
import ctypes
from pathlib import Path
import sys,unittest
from unittest.mock import Mock, patch
from colvia.codec import RecordError
from colvia.storage.windows import API, WindowsFiles, local_path

class WindowsStorageContractTests(unittest.TestCase):
    def test_portable_path_rejects_remote_devices_ads_aliases_and_normalization(self):
        for path in ('C:relative',r'\\server\share\record',r'\\?\C:\record',r'C:\record:stream',r'C:\NUL.txt',
                     'C:\\trailing.\\record',r'C:\a\..\b',r'C:\a\.\b',r'C:\a\\b','C:\\'+'x'*248):
            with self.subTest(path=path),self.assertRaises(RecordError):local_path(path)
        self.assertEqual(r'C:\Users\Example\Colvia\state.sqlite3',local_path(r'C:\Users\Example\Colvia\state.sqlite3'))
    def test_native_unicode_spelling_is_preserved_not_renamed(self):
        native='C:\\e\u0301\\record'
        self.assertEqual(native,local_path(native))
        self.assertNotEqual('C:\\é\\record',local_path(native))

    def test_visible_wsl_marker_refuses_before_loading_windows_authority(self):
        import os
        from colvia.managed_entry import current_platform
        with patch('colvia.managed_entry.sys.platform','win32'),patch.dict(os.environ,{'WSL_INTEROP':'synthetic'}):
            with self.assertRaisesRegex(RecordError,'wsl-native-interop-unqualified'):current_platform()

    def test_non_windows_never_loads_native_dll_or_uses_posix_fallback(self):
        with patch('colvia.storage.windows.sys.platform','darwin'):
            with self.assertRaisesRegex(RecordError,'windows-native-unavailable'):API()
    def test_windows_platform_selection_cannot_fall_back_to_posix(self):
        with patch('colvia.storage.files.sys.platform','win32'),patch('colvia.storage.windows.WindowsFiles',side_effect=RecordError('unavailable')):
            from colvia.storage.files import platform_files
            with self.assertRaisesRegex(RecordError,'unavailable'):platform_files()

    def test_final_path_uses_small_buffer_and_preserves_refusal_on_retry(self):
        path = r'C:\project\report'
        expected = '\\\\?\\' + path
        api = object.__new__(API)

        def reply(value):
            def query(handle, buffer, size, flags):
                self.assertEqual((1, 0), (handle, flags))
                buffer.value = value
                return len(value)

            return query

        api.GetFinalPathNameByHandleW = Mock(side_effect=reply(expected))
        api.check_final_path(1, path)
        self.assertEqual([260], [call.args[2] for call in api.GetFinalPathNameByHandleW.call_args_list])

        boundary = expected.ljust(259, 'x')
        api.GetFinalPathNameByHandleW = Mock(side_effect=reply(boundary))
        with self.assertRaisesRegex(RecordError, 'windows-final-path-mismatch'):
            api.check_final_path(1, path)
        self.assertEqual([260], [call.args[2] for call in api.GetFinalPathNameByHandleW.call_args_list])

        api.GetFinalPathNameByHandleW = Mock(
            side_effect=lambda h, b, n, f: 260 if n == 260 else reply(boundary)(h, b, n, f))
        with self.assertRaisesRegex(RecordError, 'windows-final-path-mismatch'):
            api.check_final_path(1, path)
        self.assertEqual([260, 32768], [call.args[2] for call in api.GetFinalPathNameByHandleW.call_args_list])

        wrong_path = expected + 'x' * 300
        api.GetFinalPathNameByHandleW = Mock(
            side_effect=lambda h, b, n, f: len(wrong_path) + 1 if n == 260 else reply(wrong_path)(h, b, n, f))
        with self.assertRaisesRegex(RecordError, 'windows-final-path-mismatch'):
            api.check_final_path(1, path)
        self.assertEqual([260, 32768], [call.args[2] for call in api.GetFinalPathNameByHandleW.call_args_list])

        api.GetFinalPathNameByHandleW = Mock(return_value=0)
        with self.assertRaisesRegex(RecordError, 'windows-final-path-mismatch'):
            api.check_final_path(1, path)
        api.GetFinalPathNameByHandleW.assert_called_once()

    def test_reopening_empty_lock_uses_the_same_final_file(self):
        path = Path('authority') / 'detach.lock'
        contents = {}
        api = Mock()
        api.ancestors.return_value = nullcontext()
        api.security.return_value = nullcontext(object())
        api.Overlapped = ctypes.c_uint32

        @contextmanager
        def opened(target, *, disposition=3, **kwargs):
            self.assertEqual(path, target)
            if disposition == 1:
                if target in contents:
                    raise FileExistsError(target)
                contents[target] = b''
            yield target

        api.opened = opened
        api.state.side_effect = lambda handle, target: dict(directory=False, links=1, size=len(contents[target]))
        files = WindowsFiles(api=api)
        with patch.object(files, 'private_directory'), patch.object(files, 'sync_directory') as sync:
            for _ in range(3):
                with files.empty_lock(path):
                    self.assertEqual({path: b''}, contents)
            sync.assert_called_once_with(path.parent)
            contents[path] = b'user data'
            with self.assertRaisesRegex(RecordError, 'detach-lock-invalid'), files.empty_lock(path):
                self.fail('nonempty lock admitted')
            self.assertEqual(b'user data', contents[path])
        self.assertEqual(3, api.LockFileEx.call_count)
        self.assertEqual(3, api.UnlockFileEx.call_count)
        api.MoveFileExW.assert_not_called()
