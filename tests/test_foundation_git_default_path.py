"""Default ignore-path resolution; no Git writes or synthetic commits."""
from pathlib import Path,PureWindowsPath
from types import SimpleNamespace
from unittest.mock import Mock,patch
import os,subprocess,tempfile,unittest
from colvia.adapters.git import Git
from colvia.codec import RecordError

class GitDefaultPathTests(unittest.TestCase):
    def adapter(self,environment,configured=None,expanded=b'/git-home/.config/git/ignore\0'):
        g=object.__new__(Git);g.env=environment
        first=SimpleNamespace(code=1,stdout=b'') if configured is None else SimpleNamespace(code=0,stdout=configured)
        g._run=Mock(side_effect=[first,SimpleNamespace(code=0,stdout=expanded)])
        return g
    def resolve(self,g,platform='win32'):
        with patch('colvia.adapters.git.sys.platform',platform):
            return g._global_ignore_path(Path('/project'))
    def test_configured_relative_path_ending_in_n_keeps_precedence(self):
        g=self.adapter({'XDG_CONFIG_HOME':'/other'},b'local-pattern\0')
        self.assertEqual(Path('/project/local-pattern'),self.resolve(g));self.assertEqual(1,g._run.call_count)
    def test_configured_cr_is_not_silently_stripped(self):
        with self.assertRaisesRegex(RecordError,'git-path-encoding-unavailable'):
            self.resolve(self.adapter({},b'/custom/ignore\r\0'),'darwin')
    def test_xdg_has_precedence_and_home_is_used_otherwise(self):
        for env,expected in (({'XDG_CONFIG_HOME':'/xdg','HOME':'/home'},'/xdg/git/ignore'),
                             ({'XDG_CONFIG_HOME':'','HOME':'/home'},'/home/.config/git/ignore')):
            g=self.adapter(env)
            self.assertEqual(Path(expected),self.resolve(g));self.assertEqual(1,g._run.call_count)
    def test_windows_missing_or_empty_home_uses_guarded_git_query(self):
        for env in ({},{'HOME':'','XDG_CONFIG_HOME':''},{'USERPROFILE':'/do-not-infer'}):
            original=dict(env);g=self.adapter(env,expanded=b'/git-home/.config/git/ignore\0')
            self.assertEqual(Path('/git-home/.config/git/ignore'),self.resolve(g))
            g._run.assert_called_with(Path('/project'),('config','-z','--path','--default','~/.config/git/ignore','--get','core.excludesfile'),limit=32768)
            self.assertEqual(original,g.env)
    def test_windows_config_snapshot_without_home_keeps_git_default_query(self):
        g=self.adapter({'USERPROFILE':'/do-not-infer'})
        g._run.side_effect=[SimpleNamespace(code=0,stdout=b'C:/git-home/.config/git/ignore\0')]
        root=PureWindowsPath('C:/project')
        with patch('colvia.adapters.git.sys.platform','win32'),patch('colvia.adapters.git.Path',PureWindowsPath):
            self.assertEqual(PureWindowsPath('C:/git-home/.config/git/ignore'),
                             g._global_ignore_path(root,has_configured_excludes=False))
        g._run.assert_called_once_with(root,('config','-z','--path','--default','~/.config/git/ignore','--get','core.excludesfile'),limit=32768)

    def test_relative_xdg_or_home_remains_rejected(self):
        for env in ({'XDG_CONFIG_HOME':'relative'},{'HOME':'relative'}):
            g=self.adapter(env)
            with self.assertRaisesRegex(RecordError,'git-global-ignore-location-unavailable'):self.resolve(g)
            self.assertEqual(1,g._run.call_count)
    def test_relative_or_empty_git_expansion_is_rejected(self):
        for raw in (b'relative/ignore\0',b'\0'):
            with self.assertRaisesRegex(RecordError,'git-global-ignore-location-unavailable'):
                self.resolve(self.adapter({},expanded=raw))
    def test_extra_or_malformed_lines_are_rejected_in_both_branches(self):
        for raw in (b'/p\n\0',b'/p\r\0',b'/p\0\0',b'/p',b'/\xff\0'):
            for configured in (True,False):
                g=self.adapter({},configured=raw if configured else None,expanded=raw)
                with self.assertRaisesRegex(RecordError,'git-path-encoding-unavailable'):self.resolve(g)
    def test_git_query_failure_does_not_guess_userprofile(self):
        g=self.adapter({'USERPROFILE':'/profile'})
        g._run.side_effect=[SimpleNamespace(code=1,stdout=b''),RecordError('git-observation-unavailable')]
        with self.assertRaisesRegex(RecordError,'git-observation-unavailable'):self.resolve(g)
    def test_non_windows_missing_home_stays_fail_closed(self):
        g=self.adapter({'USERPROFILE':'/profile'})
        with self.assertRaisesRegex(RecordError,'git-global-ignore-location-unavailable'):self.resolve(g,'darwin')
        self.assertEqual(1,g._run.call_count)
    def test_windows_drive_and_rooted_path_semantics(self):
        for raw,valid in ((b'C:/git-home/.config/git/ignore\0',True),
                          (b'/.config/git/ignore\0',False),(b'C:relative/ignore\0',False)):
            g=self.adapter({},expanded=raw)
            with patch('colvia.adapters.git.sys.platform','win32'),patch('colvia.adapters.git.Path',PureWindowsPath):
                if valid:self.assertEqual(PureWindowsPath('C:/git-home/.config/git/ignore'),g._global_ignore_path(PureWindowsPath('C:/project')))
                else:
                    with self.assertRaisesRegex(RecordError,'git-global-ignore-location-unavailable'):
                        g._global_ignore_path(PureWindowsPath('C:/project'))
    def test_windows_case_insensitive_environment_preserves_xdg(self):
        g=self.adapter({'xdg_config_home':'/custom','home':'/home'})
        self.assertEqual(Path('/custom/git/ignore'),self.resolve(g));self.assertEqual(1,g._run.call_count)
        with self.assertRaisesRegex(RecordError,'git-global-ignore-location-unavailable'):
            self.resolve(self.adapter({'HOME':'/one','home':'/two'}))
    def test_actual_git_default_path_query_is_read_only(self):
        exe=Path('/Library/Developer/CommandLineTools/usr/bin/git')
        if not exe.is_file():self.skipTest('qualified POSIX Git not present')
        with tempfile.TemporaryDirectory(prefix='git-default-query-') as d:
            root=Path(d);env={k:v for k,v in os.environ.items() if not k.startswith('GIT_')}
            env.update(HOME=d,GIT_CONFIG_NOSYSTEM='1',GIT_CONFIG_GLOBAL=os.devnull,GIT_CONFIG_SYSTEM=os.devnull)
            env.pop('XDG_CONFIG_HOME',None)
            p=subprocess.run([str(exe),'-C',d,'config','-z','--path','--default','~/.config/git/ignore','--get','core.excludesfile'],
                             env=env,capture_output=True,timeout=10,check=True)
            self.assertEqual(str(root/'.config/git/ignore'),p.stdout.removesuffix(b'\0').decode())
            self.assertEqual([],list(root.iterdir()))

if __name__=='__main__':unittest.main()
