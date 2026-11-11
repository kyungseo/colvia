"""Windows worktree proof with portable identity double, no Git/OS effects."""
from pathlib import Path
import tempfile,unittest,uuid
from colvia.binding import Topology,Membership,WorkspaceRegistration
from colvia.codec import RecordError
from colvia.platforms.windows_observation import Observer
from colvia.platforms.windows_structural import prove
from test_foundation_windows_observation import FilesDouble

class WindowsStructuralTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='windows-structure-');self.root=Path(self.tmp.name)
        (self.root/'.git').mkdir();self.container=self.root/'.claude/worktrees';self.container.mkdir(parents=True)
        self.port=Observer(files=FilesDouble());self.members=[];self.registrations=[]
        for name in ('one','two'):
            folder=self.container/name;folder.mkdir();meta=self.root/'.git'/name;meta.mkdir()
            member=Membership(self.port.location(folder),self.port.location(meta));self.members.append(member)
            self.registrations.append(WorkspaceRegistration(str(uuid.uuid4()),member.root,member.gitdir))
        self.primary=Membership(self.port.location(self.root),self.port.location(self.root/'.git'))
        self.top=Topology('git',self.primary.root,self.primary.gitdir,self.primary.gitdir,(self.primary,*self.members))
    def tearDown(self):self.tmp.cleanup()
    def check(self,**kwargs):return prove(self.top,tuple(self.registrations),observer=self.port,**kwargs)
    def test_parent_container_only_contains_registered_roots(self):
        result=self.check();self.assertEqual(frozenset({'.claude/worktrees'}),result.containers)
        self.assertIn('.git',result.boundaries);self.assertIn('.claude/worktrees',result.boundaries)
        self.assertNotIn('.claude/worktrees/one',result.boundaries)
    def test_unregistered_sibling_cannot_hide_under_old_parent(self):
        (self.container/'unregistered').mkdir()
        with self.assertRaisesRegex(RecordError,'structural-container-changed'):self.check(previous_containers={'.claude/worktrees'})
        result=self.check();self.assertFalse(result.containers);self.assertIn('.claude/worktrees/one',result.boundaries)
    def test_registration_and_protected_paths_remain_required(self):
        self.registrations.pop()
        with self.assertRaisesRegex(RecordError,'registration-required'):self.check()
        self.registrations.append(WorkspaceRegistration(str(uuid.uuid4()),self.members[-1].root,self.members[-1].gitdir))
        with self.assertRaisesRegex(RecordError,'boundary-swallows-protected'):self.check(protected={'.claude/worktrees/one/keep'})
    def test_empty_previous_container_can_remain_equivalent(self):
        for member in self.members:Path(member.root.path).rmdir()
        self.top=Topology('git',self.top.root,self.top.common,self.top.gitdir,(self.primary,))
        result=self.check(previous_containers={'.claude/worktrees'})
        self.assertEqual(frozenset({'.claude/worktrees'}),result.containers)

if __name__=='__main__':unittest.main()
