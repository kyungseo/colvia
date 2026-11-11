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
