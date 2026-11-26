"""Git writes below are explicitly synthetic fixture preparation only."""
from pathlib import Path
import os,subprocess,tempfile,unittest,uuid

from colvia.adapters.git import Git,discover
from colvia.binding import WorkspaceRegistration
from colvia.codec import RecordError
from colvia.platforms.posix import ObservationBudget,snapshot,location
from colvia.platforms.structural import prove

EXECUTABLE=Path('/Library/Developer/CommandLineTools/usr/bin/git')


class GitFixture:
    def setUp(self):
        if not EXECUTABLE.is_file():self.skipTest('qualified fixture Git unavailable')
        self.tmp=tempfile.TemporaryDirectory(prefix='git-observation-')
        self.home=Path(self.tmp.name);self.root=self.home/'project';self.root.mkdir()
        self.empty_hooks=self.home/'empty-hooks';self.empty_hooks.mkdir()
        self.env={k:v for k,v in os.environ.items() if not k.startswith('GIT_')}
        self.env.update(GIT_CONFIG_NOSYSTEM='1',GIT_CONFIG_GLOBAL='/dev/null',GIT_CONFIG_SYSTEM='/dev/null',
                        GIT_AUTHOR_NAME='Synthetic Owner',GIT_AUTHOR_EMAIL='owner@example.invalid',
                        GIT_COMMITTER_NAME='Synthetic Owner',GIT_COMMITTER_EMAIL='owner@example.invalid')
        self.command('init','-q')
        (self.root/'report.md').write_bytes(b'synthetic report\n')
        self.command('add','report.md');self.command('commit','-qm','Synthetic fixture baseline')
        self.git=Git(EXECUTABLE,environment=self.env)
    def tearDown(self):self.tmp.cleanup()
    def command(self,*args,root=None):
        return subprocess.run([str(EXECUTABLE),'-c','core.hooksPath='+str(self.empty_hooks),'-C',str(root or self.root),*args],
            env=self.env,check=True,capture_output=True,timeout=10).stdout
    def registrations(self,topology):
        return tuple(WorkspaceRegistration(str(uuid.uuid4()),m.root,m.gitdir) for m in topology.members)


class GitTests(GitFixture,unittest.TestCase):
    def test_root_subfolder_and_sibling_resolve_same_common_distinct_workspace(self):
        (self.root/'sub').mkdir();primary=self.git.topology(self.root/'sub')
        self.assertEqual(str(self.root),primary.root.path)
        sibling=self.home/'sibling';self.command('worktree','add','-q','-b','sibling',str(sibling))
        other=self.git.topology(sibling)
        self.assertEqual(primary.common,other.common);self.assertNotEqual(primary.gitdir,other.gitdir)
        self.assertEqual(2,len(other.members))

    def test_batched_topology_uses_git_exclude_path_in_primary_and_linked_roots(self):
        sibling = self.home / 'sibling'
        self.command('worktree', 'add', '-q', '-b', 'sibling', str(sibling))
        nested = sibling / 'nested'
        nested.mkdir()
        for root in (self.root, nested):
            with self.subTest(root=root):
                top, exclude = discover(root, self.git, with_exclude=True)
                standalone = self.command('rev-parse', '--path-format=absolute', '--git-path', 'info/exclude', root=root)
                self.assertEqual(self.git.topology(root), top)
                self.assertEqual(Path(os.fsdecode(standalone.rstrip(b'\n'))), exclude)
                self.assertEqual(self.git.policy(top, ()), self.git.policy(top, (), info_path=exclude))

    def test_batched_policy_preserves_config_origins_order_and_git_path_expansion(self):
        from unittest.mock import patch

        global_config = self.home / 'config'
        user_config = self.home / '.gitconfig'
        self.git.env.update(HOME=str(self.home), XDG_CONFIG_HOME=str(global_config))
        self.git.env.pop('GIT_CONFIG_GLOBAL', None)
        user_config.write_text('[core]\nexcludesFile = global-ignore\n')
        self.command('config', 'core.excludesfile', 'repository-ignore')
        (self.root / 'repository-ignore').write_text('repository-only\n')
        top = self.git.topology(self.root)
        before = self.git._global_ignore_path(self.root)
        with patch.object(self.git, '_run', wraps=self.git._run) as run:
            policy = self.git.policy(top, ())
        self.assertEqual(self.root / 'repository-ignore', before)
        self.assertEqual([('file:' + str(user_config) + ' core.excludesfile', 'global-ignore'),
                          ('file:' + str(self.root / '.git/config') + ' core.excludesfile', 'repository-ignore')],
                         [entry for entry in policy.config if entry[0].endswith(' core.excludesfile')])
        self.assertEqual('global:' + str(before), policy.sources[0].origin)
        typed = [call for call in run.call_args_list if '--path' in call.args[1]]
        self.assertEqual(1, len(typed))

        self.command('config', 'core.excludesfile', '~/expanded-ignore')
        self.assertEqual('global:' + str(self.home / 'expanded-ignore'),
                         self.git.policy(top, ()).sources[0].origin)

    def test_batched_topology_with_ambiguous_budget_uses_original_queries(self):
        from unittest.mock import patch
        from colvia.platforms.process import ProcessResult

        run = self.git._run

        def with_large_warning(root, argv, **kwargs):
            result = run(root, argv, **kwargs)
            if '--show-toplevel' in argv and '--git-path' in argv:
                return ProcessResult(0, result.stdout, b'warning ' * 4096)
            return result

        top = self.git.topology(self.root)
        info = self.git._info_exclude_path(self.root)
        with patch.object(self.git, '_run', side_effect=with_large_warning) as process:
            self.assertEqual((top, info), discover(self.root, self.git, with_exclude=True))
        self.assertEqual(5, process.call_count)

    def test_any_explicit_ignore_path_is_interpreted_by_pinned_git(self):
        from unittest.mock import patch
        from colvia.platforms.process import ProcessResult

        # The full runner intentionally does not inherit the account's HOME.
        # Git still parses repository configuration during the real rev-parse.
        self.git.env['HOME'] = str(self.home)
        top = self.git.topology(self.root)
        run = self.git._run

        def pinned_path(root, argv, **kwargs):
            if '--path' in argv:
                return ProcessResult(0, b'expected-ignore\0', b'')
            return run(root, argv, **kwargs)

        for raw in ('ordinary', '~/ignore', '%(prefix)/ignore', ':(optional)ignore', '/etc/ignore', ''):
            self.command('config', '--replace-all', 'core.excludesfile', raw)
            with self.subTest(raw=raw), patch.object(self.git, '_run', side_effect=pinned_path) as process:
                policy = self.git.policy(top, ())
                self.assertEqual('global:' + str(self.root / 'expected-ignore'), policy.sources[0].origin)
                self.assertEqual(1, sum('--path' in call.args[1] for call in process.call_args_list))

    def test_empty_plain_needs_no_git_and_git_transition_never_falls_back(self):
        plain=self.home/'plain';plain.mkdir()
        self.assertEqual('plain',discover(plain,None).kind)
        self.command('init','-q',root=plain)
        with self.assertRaisesRegex(RecordError,'git-prerequisite-required'):discover(plain,None)
        self.assertEqual('git',discover(plain,self.git).kind)

    def test_index_ignored_tracked_and_unmerged(self):
        (self.root/'.gitignore').write_text('report.md\nhidden\n')
        (self.root/'hidden').write_bytes(b'ignored')
        index=self.git.index(self.root)
        self.assertIn('report.md',index)
        self.assertEqual(frozenset({'report.md','hidden'}),self.git.ignored(self.root,['report.md','hidden','new']))
        self.assertFalse((self.root/'.git/index.lock').exists())

    def test_nested_registry_and_container_are_proved_not_name_guessed(self):
        parent=self.root/'.claude/worktrees';parent.mkdir(parents=True)
        for name in ('one','two'):self.command('worktree','add','-q','-b',name,str(parent/name))
        topology=self.git.topology(self.root);registered=self.registrations(topology)
        proof=prove(topology,registered)
        self.assertEqual(frozenset({'.claude/worktrees'}),proof.containers)
        result=snapshot(self.root,ObservationBudget(100,1024*1024),boundaries=proof.boundaries)
        self.assertEqual(['report.md'],[e['path'] for e in result.entries])
        with self.assertRaisesRegex(RecordError,'nested-workspace-registration-required'):
            prove(topology,registered[:1])
        (parent/'.hidden').write_bytes(b'not a workspace')
        nextproof=prove(topology,registered)
        self.assertNotIn('.claude/worktrees',nextproof.containers)

    def test_previous_container_with_new_sibling_is_unavailable_even_without_policy_change(self):
        parent=self.root/'.claude/worktrees';parent.mkdir(parents=True)
        self.command('worktree','add','-q','-b','child',str(parent/'child'))
        topology=self.git.topology(self.root);registered=self.registrations(topology)
        before=prove(topology,registered)
        (parent/'orphan').mkdir()
        with self.assertRaisesRegex(RecordError,'structural-container-changed'):
            prove(topology,registered,previous_containers=before.containers)

    def test_empty_former_container_after_explicit_fixture_reconciliation(self):
        parent=self.root/'.claude/worktrees';parent.mkdir(parents=True)
        self.command('worktree','add','-q','-b','child',str(parent/'child'))
        topology=self.git.topology(self.root);before=prove(topology,self.registrations(topology))
        self.command('worktree','remove',str(parent/'child'))
        current=self.git.topology(self.root)
        self.assertIn('.claude/worktrees',prove(current,self.registrations(current),previous_containers=before.containers).containers)
        self.assertFalse(prove(current,self.registrations(current)).containers)

    def test_protected_baseline_cannot_be_swallowed_by_new_nested_workspace(self):
        parent=self.root/'nested';self.command('worktree','add','-q','-b','child',str(parent))
        topology=self.git.topology(self.root)
        with self.assertRaisesRegex(RecordError,'boundary-swallows-protected'):
            prove(topology,self.registrations(topology),protected={'nested/report.md'})

if __name__=='__main__':unittest.main()
