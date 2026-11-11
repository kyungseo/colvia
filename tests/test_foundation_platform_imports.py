"""Source import boundaries only; not Windows execution or installation."""
from pathlib import Path
import subprocess,sys,unittest
from unittest.mock import patch

class PlatformImportTests(unittest.TestCase):
    def test_common_and_windows_entries_do_not_import_posix_only_modules(self):
        source=str(Path(__file__).resolve().parents[1]/'src')
        code='''import builtins,sys
sys.path.insert(0,SOURCE)
original=builtins.__import__
def checked(name,*a,**kw):
    if name.split('.')[0] in {'fcntl','pwd','pty','resource'}:
        raise ImportError('POSIX-only dependency: '+name)
    return original(name,*a,**kw)
builtins.__import__=checked
import colvia.managed_entry,colvia.manager_entry,colvia.restored_setup
import colvia.platforms.windows_connect,colvia.platforms.windows_child,colvia.platforms.windows_git
import colvia.updates.installation,colvia.updates.repair
assert 'colvia.platforms.darwin_effects' not in sys.modules
colvia.manager_entry.parser()
print('portable-import-boundary-ok')
'''.replace('SOURCE',repr(source))
        result=subprocess.run([sys.executable,'-I','-B','-c',code],capture_output=True,text=True,timeout=15)
        self.assertEqual(0,result.returncode,result.stderr)
        self.assertEqual('portable-import-boundary-ok',result.stdout.strip())

    def test_git_port_selects_only_explicit_platform(self):
        from colvia.platforms.git_port import integration_port
        from colvia.codec import RecordError
        with patch('colvia.platforms.git_port.sys.platform','win32'),patch('colvia.platforms.windows_git.WindowsGit',return_value='windows') as factory:
            self.assertEqual('windows',integration_port('root','scratch','qualified-git',create=False))
        factory.assert_called_once_with('root','scratch','qualified-git',create=False)
        with patch('colvia.platforms.git_port.sys.platform','linux'),self.assertRaisesRegex(RecordError,'platform-unavailable'):
            integration_port('root','scratch','qualified-git',create=False)

    def test_worker_effects_use_native_windows_port_and_refuse_unknown_hosts(self):
        from colvia.platforms.effects_port import effects
        from colvia.codec import RecordError
        with patch('colvia.platforms.effects_port.sys.platform','win32'),patch('colvia.platforms.windows_effects.WindowsEffects',return_value='windows') as factory:
            self.assertEqual('windows',effects('root','authority'))
        factory.assert_called_once_with('root','authority')
        with patch('colvia.platforms.effects_port.sys.platform','linux'),self.assertRaisesRegex(RecordError,'platform-unavailable'):
            effects('root','authority')

if __name__=='__main__':unittest.main()

