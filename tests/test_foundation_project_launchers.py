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
        self.assertIn(b'--management-root "%LOCALAPPDATA%\\Colvia"',raw)
        for forbidden in (b'python',b'powershell',b'chcp'):self.assertNotIn(forbidden,raw)
    def test_standard_profile_uses_trusted_userprofile_with_redirected_environment(self):
        profile=r'C:\Users\홍길동'
        base=profile+r'\AppData\Local'
        home=base+r'\Colvia'
        arguments=dict(known_local_appdata=base,environment_local_appdata=r'C:\app-cache',
                       known_user_profile=profile,environment_user_profile=profile)
        _,_,raw=project_launcher(home+r'\bin\colvia.exe',home,'windows',**arguments)
        self.assertIn(b'"%USERPROFILE%\\AppData\\Local\\Colvia\\bin\\colvia.exe"',raw)
        self.assertIn(b'--management-root "%USERPROFILE%\\AppData\\Local\\Colvia"',raw)
        self.assertTrue(raw.isascii());self.assertNotIn(b'LOCALAPPDATA',raw)
        arguments['environment_user_profile']=r'C:\different'
        with self.assertRaisesRegex(RecordError,'windows-user-profile-environment-mismatch'):
            project_launcher(home+r'\bin\colvia.exe',home,'windows',**arguments)
    def test_standard_location_rejects_environment_or_entry_drift(self):
        base=r'C:\Users\demo\AppData\Local';home=base+r'\Colvia'
        with self.assertRaisesRegex(RecordError,'environment-mismatch'):
            project_launcher(home+r'\bin\colvia.exe',home,'windows',known_local_appdata=base,environment_local_appdata=r'C:\other')
        with self.assertRaisesRegex(RecordError,'entry-mismatch'):
            project_launcher(home+r'\other.exe',home,'windows',known_local_appdata=base,environment_local_appdata=base)
    def test_windows_block_points_to_its_actual_launcher(self):
        self.assertEqual(b'.\\colvia.cmd guide; .\\colvia.cmd ordinary list',project_block(b'./colvia guide; ./colvia ordinary list','windows'))

class VerifiedEntryArgumentTests(unittest.TestCase):
    def test_direct_python_entries_refuse_duplicate_selections_before_opening_a_home(self):
        from contextlib import redirect_stderr
        from io import StringIO
        from unittest.mock import patch
        from colvia import managed_entry, manager_entry

        trusted = ['--management-root', '/synthetic', '--runtime-slot', 'one',
                   '--runtime-manifest-sha256', 'a' * 64]
        cases = (
            (managed_entry.main, trusted + ['guide', '--runtime-slot=two']),
            (manager_entry.main, trusted + ['--management-root=/synthetic', 'status']),
            (manager_entry.main, trusted + ['--repair', '--repair', 'repair-preview']),
            (manager_entry.main, ['bootstrap-install-or-update', '--management-root', '/synthetic',
                                  '--bootstrap-stage', '/stage', '--bootstrap-manifest-sha256', '1' * 64,
                                  '--bootstrap-manifest-sha256', '2' * 64]),
        )
        with patch.object(managed_entry, 'ManagerHome', side_effect=AssertionError('opened home')):
            for entry, args in cases:
                with self.subTest(args=args), redirect_stderr(StringIO()) as stderr:
                    with self.assertRaises(SystemExit) as failure:
                        entry(args)
                    self.assertEqual(2, failure.exception.code)
                    self.assertIn('duplicate runtime option', stderr.getvalue())


if __name__=='__main__':unittest.main()
