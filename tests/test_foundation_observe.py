from pathlib import Path
import os,tempfile,unittest
from colvia.codec import RecordError
from colvia.observe import observe
from colvia.observation import verify_scope
from colvia.platforms.posix import ObservationBudget
from test_foundation_git import GitFixture


class GitObservationTests(GitFixture,unittest.TestCase):
    # Reuse only the fixture setup/helpers, not inherited unrelated test methods.
    def test_tracked_ignored_and_untracked_have_complete_protected_membership(self):
        (self.root/'.gitignore').write_bytes(b'report.md\nhidden\n')
        (self.root/'hidden').write_bytes(b'ignored');(self.root/'new').write_bytes(b'included')
        result=observe(self.root,ObservationBudget(100,1024*1024),git=self.git)
        self.assertEqual({'.gitignore','report.md','new'},{e['path'] for e in result.snapshot.entries})

    def test_same_policy_new_orphan_inside_previous_container_refuses(self):
        parent=self.root/'.claude/worktrees';parent.mkdir(parents=True)
        self.command('worktree','add','-q','-b','child',str(parent/'child'))
        topology=self.git.topology(self.root);registered=self.registrations(topology)
        first=observe(self.root,ObservationBudget(100,1024*1024),git=self.git,registrations=registered)
        with (self.root/'.git/info/exclude').open('ab') as out:out.write(b'.claude/worktrees/\n')
        second=observe(self.root,ObservationBudget(100,1024*1024),git=self.git,registrations=registered,
                       previous_policy=first.policy,previous_containers=first.structural.containers,
                       protected=frozenset(e['path'] for e in first.snapshot.entries))
        (parent/'.orphan').mkdir()
        with self.assertRaisesRegex(RecordError,'structural-container-changed'):
            observe(self.root,ObservationBudget(100,1024*1024),git=self.git,registrations=registered,
                    previous_policy=second.policy,previous_containers=second.structural.containers)

    def test_policy_edit_cannot_hide_an_outside_scope_edit(self):
        (self.root/'.gitignore').write_bytes(b'')
        (self.root/'reference').write_bytes(b'protected')
        first=observe(self.root,ObservationBudget(100,1024*1024),git=self.git)
        (self.root/'.gitignore').write_bytes(b'reference\n');(self.root/'reference').write_bytes(b'changed')
        second=observe(self.root,ObservationBudget(100,1024*1024),git=self.git,previous_policy=first.policy,
                       protected=frozenset(e['path'] for e in first.snapshot.entries),approved_policy_paths={'.gitignore'})
        with self.assertRaisesRegex(RecordError,'outside-scope-change'):
            verify_scope(first.snapshot.entries,second.snapshot.entries,frozenset({'.gitignore'}))

    def test_unregistered_nested_repository_is_not_silently_ignored(self):
        child=self.root/'foreign';child.mkdir();self.command('init','-q',root=child)
        with (self.root/'.git/info/exclude').open('ab') as out:out.write(b'foreign/\n')
        with self.assertRaisesRegex(RecordError,'unregistered-nested-git'):
            observe(self.root,ObservationBudget(100,1024*1024),git=self.git)


class PlainObservationTests(unittest.TestCase):
    def test_plain_without_git_and_git_marker_appearance(self):
        with tempfile.TemporaryDirectory(prefix='plain-') as temporary:
            root=Path(temporary);(root/'report').write_bytes(b'plain')
            result=observe(root,ObservationBudget(10,1024))
            self.assertEqual('plain',result.topology.kind)
            (root/'.git').write_text('broken marker')
            with self.assertRaisesRegex(RecordError,'git-prerequisite-required'):
                observe(root,ObservationBudget(10,1024))

if __name__=='__main__':unittest.main()
