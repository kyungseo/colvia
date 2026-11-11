from dataclasses import replace
import unittest
from colvia.binding import (Locator, Membership, NativeLocation, ProjectBinding, Topology,
                            WorkspaceRegistration, require_connection_root, require_registered, resolve)
from colvia.codec import RecordError, canonical_bytes

P='00000000-0000-4000-8000-000000000001'
I='00000000-0000-4000-8000-000000000002'
W='00000000-0000-4000-8000-000000000003'
W2='00000000-0000-4000-8000-000000000004'


def location(path,number): return NativeLocation(path,'synthetic-volume',str(number))


class BindingTests(unittest.TestCase):
    def setUp(self):
        self.root=location('/workspace/main',1);self.common=location('/workspace/main/.git',2)
        self.sibling=location('/workspace/sibling',3);self.sibling_git=location('/workspace/main/.git/worktrees/sibling',4)
        self.members=(Membership(self.root,self.common),Membership(self.sibling,self.sibling_git))
        self.git=Topology('git',self.root,self.common,self.common,self.members)
        self.loc=Locator(P,I,1,'a'*64)
        self.binding=ProjectBinding(self.loc,'git',self.common)
        self.registration=WorkspaceRegistration(W,self.root,self.common)

    def test_primary_and_sibling_share_project_not_workspace(self):
        first=resolve(self.loc,self.binding,self.git,(self.registration,))
        self.assertEqual(W,require_registered(first))
        sibling=Topology('git',self.sibling,self.common,self.sibling_git,self.members)
        second=resolve(self.loc,self.binding,sibling,(self.registration,))
        self.assertEqual(P,second.project);self.assertTrue(second.registration_required)
        with self.assertRaisesRegex(RecordError,'workspace-registration-required'):require_registered(second)
        registered=WorkspaceRegistration(W2,self.sibling,self.sibling_git)
        self.assertEqual(W2,require_registered(resolve(self.loc,self.binding,sibling,(self.registration,registered))))

    def test_copy_and_move_never_claim_original_history_is_current(self):
        for common in (replace(self.common,path='/copy/.git'),replace(self.common,file_id='new')):
            observed=Topology('git',self.root,common,common,(Membership(self.root,common),))
            with self.assertRaisesRegex(RecordError,'project-location-changed'):
                resolve(self.loc,self.binding,observed,(self.registration,))
        for loc in (replace(self.loc,epoch=2),replace(self.loc,nonce='b'*64),replace(self.loc,instance=W2)):
            with self.assertRaisesRegex(RecordError,'stale-or-foreign-binding'):
                resolve(loc,self.binding,self.git,(self.registration,))

    def test_plain_folder_copy_and_git_transition_refuse(self):
        locator=replace(self.loc,workspace=W)
        binding=ProjectBinding(locator,'plain',self.root)
        plain=Topology('plain',self.root)
        registration=WorkspaceRegistration(W,self.root,None)
        self.assertEqual(W,require_registered(resolve(locator,binding,plain,(registration,))))
        with self.assertRaisesRegex(RecordError,'project-location-changed'):
            resolve(locator,binding,Topology('plain',replace(self.root,path='/copy')),(registration,))
        with self.assertRaisesRegex(RecordError,'project-topology-changed'):
            resolve(locator,binding,self.git,(registration,))
        with self.assertRaisesRegex(RecordError,'project-topology-changed'):
            resolve(self.loc,self.binding,plain,(self.registration,))

    def test_foreign_or_missing_git_membership_refuses(self):
        with self.assertRaisesRegex(RecordError,'workspace-not-in-git-membership'):
            Topology('git',self.sibling,self.common,self.sibling_git,(self.members[0],))
        with self.assertRaisesRegex(RecordError,'workspace-location-changed'):
            resolve(self.loc,self.binding,self.git,(replace(self.registration,gitdir=self.sibling_git),))

    def test_locator_exact_shape_and_root_only_connection(self):
        self.assertEqual(self.loc,Locator.parse(canonical_bytes(self.loc.payload()),kind='git'))
        value=self.loc.payload();value['workspace_uuid']=W
        with self.assertRaisesRegex(RecordError,'invalid-locator'): Locator.parse(canonical_bytes(value),kind='git')
        with self.assertRaisesRegex(RecordError,'invalid-binding-epoch'):replace(self.loc,epoch=True)
        require_connection_root(self.root,self.git)
        with self.assertRaisesRegex(RecordError,'connect-workspace-root-required'):
            require_connection_root(location('/workspace/main/subfolder',5),self.git)

    def test_nested_app_workspace_requires_membership_and_distinct_registration(self):
        nested=location('/workspace/main/.agent/worktrees/task',6)
        gitdir=location('/workspace/main/.git/worktrees/task',7)
        observed=Topology('git',nested,self.common,gitdir,(*self.members,Membership(nested,gitdir)))
        result=resolve(self.loc,self.binding,observed,(self.registration,))
        self.assertTrue(result.registration_required)
        self.assertIsNone(result.workspace)


if __name__=='__main__':unittest.main()
