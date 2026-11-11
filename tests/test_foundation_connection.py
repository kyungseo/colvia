from pathlib import Path
import tempfile,unittest
from dataclasses import replace
from colvia.binding import Locator,NativeLocation,Membership,ProjectBinding,WorkspaceRegistration,Topology
from colvia.codec import RecordError
from colvia.connection import Connections
from colvia.storage.sqlite import GenerationStore
from test_foundation_binding import P,I,W,W2


class ConnectionTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='connections-')
        self.store=GenerationStore.create(Path(self.tmp.name)/'state.sqlite3',project=P,instance=I,generation='g',active_check=lambda:None)
        self.service=Connections(self.store)
        self.root=NativeLocation('/synthetic/root','v','1');self.common=NativeLocation('/synthetic/root/.git','v','2')
        self.sibling=NativeLocation('/synthetic/sibling','v','3');self.childgit=NativeLocation('/synthetic/root/.git/worktrees/sibling','v','4')
        self.members=(Membership(self.root,self.common),Membership(self.sibling,self.childgit))
        self.top=Topology('git',self.root,self.common,self.common,self.members)
        self.locator=Locator(P,I,1,'a'*64);self.bound=ProjectBinding(self.locator,'git',self.common)
        self.primary=WorkspaceRegistration(W,self.root,self.common)
        self.service.connect(operation='connect',binding=self.bound,observed=self.top,workspace=self.primary,verify_topology=lambda:self.top)
    def tearDown(self):self.store.close();self.tmp.cleanup()
    def test_first_connect_and_selected_workspace_read(self):
        _,record,binding=self.service.workspace(W)
        self.assertEqual(self.primary,record);self.assertEqual(self.bound,binding)
        with self.assertRaisesRegex(RecordError,'head-conflict'):
            self.service.connect(operation='duplicate',binding=self.bound,observed=self.top,workspace=self.primary,verify_topology=lambda:self.top)
    def test_sibling_registration_keeps_distinct_workspace_and_same_project(self):
        observed=Topology('git',self.sibling,self.common,self.childgit,self.members)
        child=WorkspaceRegistration(W2,self.sibling,self.childgit)
        self.service.register(operation='child',locator=self.locator,observed=observed,workspace=child,registrations=(self.primary,),verify_topology=lambda:observed)
        self.assertEqual(child,self.service.workspace(W2)[1]);self.assertEqual(self.primary,self.service.workspace(W)[1])
        another=replace(child,workspace='00000000-0000-4000-8000-000000000099')
        with self.assertRaisesRegex(RecordError,'head-conflict'):
            self.service.register(operation='racing-child',locator=self.locator,observed=observed,workspace=another,registrations=(self.primary,),verify_topology=lambda:observed)
    def test_stale_locator_or_replaced_worktree_refuses_before_recording(self):
        child=WorkspaceRegistration(W2,self.sibling,self.childgit)
        observed=Topology('git',self.sibling,self.common,self.childgit,self.members)
        with self.assertRaisesRegex(RecordError,'stale-or-foreign-binding'):
            self.service.register(operation='bad',locator=replace(self.locator,epoch=2),observed=observed,workspace=child,registrations=(self.primary,),verify_topology=lambda:observed)
        with self.assertRaisesRegex(RecordError,'workspace-location-changed'):
            self.service.register(operation='replaced',locator=self.locator,observed=observed,workspace=replace(child,root=replace(self.sibling,file_id='other')),registrations=(self.primary,),verify_topology=lambda:observed)

if __name__=='__main__':unittest.main()
