"""Launcher byte generation only; Windows cmd execution is a native follow-up."""
from pathlib import Path
import unittest
from colvia.codec import RecordError
from colvia.platforms.project_launcher import project_launcher,project_block

class ProjectLauncherTests(unittest.TestCase):
    def test_mac_keeps_exact_root_and_arguments(self):
        name,mode,raw=project_launcher(Path('/Users/example/a b/bin/colvia'),Path('/Users/example/a b'),'macos')
        self.assertEqual(('colvia','100755'),(name,mode));self.assertIn(b"exec '/Users/example/a b/bin/colvia'",raw)
        self.assertIn(b'--root "$project_root" "$@"',raw);self.assertNotIn(b'python',raw)
    def test_windows_calls_exact_native_entry_not_python_or_path(self):
        name,mode,raw=project_launcher(r'C:\Users\demo!\100%\bin\colvia.exe',r'C:\Users\demo!\100%','windows')
        self.assertEqual(('colvia.cmd','100644'),(name,mode));self.assertTrue(raw.isascii())
        self.assertIn(b'setlocal DisableDelayedExpansion',raw);self.assertIn(b'100%%',raw)
        self.assertIn(b'%~dp0.',raw);self.assertIn(b' %*\r\n',raw);self.assertIn(b'exit /b %errorlevel%',raw)
        self.assertNotIn(b'python',raw);self.assertNotIn(b'powershell',raw);self.assertNotIn(b'chcp',raw)
    def test_unqualified_unicode_never_silently_writes_broken_batch(self):
        with self.assertRaisesRegex(RecordError,'unicode-path-unavailable'):
            project_launcher('C:\\Users\\홍길동\\bin\\colvia.exe','C:\\Users\\홍길동','windows')
    def test_unicode_standard_location_uses_ascii_known_folder_entry(self):
        base='C:\\Users\\홍길동!\\AppData\\Local';home=base+'\\Colvia'
        name,mode,raw=project_launcher(home+'\\bin\\colvia.exe',home,'windows',
            known_local_appdata=base,environment_local_appdata=base)
        self.assertTrue(raw.isascii());self.assertIn(b'"%LOCALAPPDATA%\\Colvia\\bin\\colvia.exe"',raw)
        self.assertNotIn(b'--management-root',raw)
        for forbidden in (b'python',b'powershell',b'chcp'):self.assertNotIn(forbidden,raw)
    def test_standard_location_rejects_environment_or_entry_drift(self):
        base=r'C:\Users\demo\AppData\Local';home=base+r'\Colvia'
        with self.assertRaisesRegex(RecordError,'environment-mismatch'):
            project_launcher(home+r'\bin\colvia.exe',home,'windows',known_local_appdata=base,environment_local_appdata=r'C:\other')
        with self.assertRaisesRegex(RecordError,'entry-mismatch'):
            project_launcher(home+r'\other.exe',home,'windows',known_local_appdata=base,environment_local_appdata=base)
    def test_windows_block_points_to_its_actual_launcher(self):
        self.assertEqual(b'.\\colvia.cmd guide; .\\colvia.cmd ordinary list',project_block(b'./colvia guide; ./colvia ordinary list','windows'))

if __name__=='__main__':unittest.main()
