"""Portable regressions for cmd spelling; native installed proof is separate."""
from dataclasses import asdict,replace
from pathlib import Path
import tempfile,unittest
from unittest.mock import patch
from colvia.binding import (NativeLocation,Locator,ProjectBinding,WorkspaceRegistration,
                            Topology,resolve,require_registered,same_plain_location,same_plain_path)
from colvia.codec import RecordError,canonical_bytes
from colvia.connection import Connections,location_key,workspace_key
from colvia.storage.sqlite import GenerationStore
from colvia.workspace import LocalWorkspace
from test_foundation_binding import P,I,W,W2

class WindowsPlainLocationTests(unittest.TestCase):
    def setUp(self):
        self.root=NativeLocation(r'C:\Users\Probe\AppData\Local\Trial\project','123','abc:456')
        self.cmd=replace(self.root,path=r'c:\users\probe\appdata\local\trial\project')
        self.loc=Locator(P,I,1,'a'*64,W)
        self.bound=ProjectBinding(self.loc,'plain',self.root)
        self.reg=WorkspaceRegistration(W,self.root,None)
    def test_original_cmd_spelling_resolves_plain_workspace(self):
        self.assertEqual(W,require_registered(resolve(self.loc,self.bound,Topology('plain',self.cmd),(self.reg,))))
    def test_no_serialization_equality_hash_or_index_rewrite(self):
        raw=canonical_bytes(asdict(self.root));key=location_key(self.root)
        self.assertTrue(same_plain_location(self.root,self.cmd))
        self.assertNotEqual(self.root,self.cmd)
        self.assertEqual(2,len({self.root,self.cmd}))
        self.assertEqual(raw,canonical_bytes({'path':self.root.path,'volume':'123','file_id':'abc:456'}))
        self.assertEqual(key,location_key(self.root));self.assertNotEqual(key,location_key(self.cmd))
        self.assertEqual({'path','volume','file_id'},set(asdict(self.root)))
    def test_move_copy_volume_and_creation_changes_refuse(self):
        for value in (replace(self.cmd,path=r'C:\Moved\project'),replace(self.cmd,volume='124'),
                      replace(self.cmd,file_id='def:456'),replace(self.cmd,file_id='abc:457')):
            with self.subTest(value=value),self.assertRaisesRegex(RecordError,'project-location-changed'):
                resolve(self.loc,self.bound,Topology('plain',value),(self.reg,))
    def test_unicode_alias_and_posix_case_are_not_folded(self):
        pairs=[('/work/Main','/work/main'),(r'C:\K','C:\\\u212a'),(r'C:\İ',r'C:\i'),
               ('C:/Trial',r'C:\trial'),(r'\\?\C:\Trial',r'C:\trial'),
               (r'C:\Trial\.',r'C:\trial'),(r'C:\PROGRA~1',r'C:\Program Files'),
               (r'\\Server\Share',r'\\server\share'),(r'C:Trial',r'C:trial'),('\u212a:\\Trial',r'k:\trial')]
        for left,right in pairs:
            with self.subTest(left=left,right=right):
                self.assertFalse(same_plain_location(NativeLocation(left,'v','id'),NativeLocation(right,'v','id')))
    def test_duplicate_plain_registration_refuses(self):
        other=WorkspaceRegistration(W2,self.cmd,None)
        with self.assertRaisesRegex(RecordError,'ambiguous-workspace-registration'):
            resolve(self.loc,self.bound,Topology('plain',self.cmd),(self.reg,other))
    def test_stale_locator_and_git_transition_still_refuse(self):
        for loc in (replace(self.loc,nonce='b'*64),replace(self.loc,epoch=2),replace(self.loc,instance=W2)):
            with self.assertRaisesRegex(RecordError,'stale-or-foreign-binding'):
                resolve(loc,self.bound,Topology('plain',self.cmd),(self.reg,))
        from colvia.binding import Membership
        git=Topology('git',self.cmd,self.cmd,self.cmd,(Membership(self.cmd,self.cmd),))
        with self.assertRaisesRegex(RecordError,'project-topology-changed'):
            resolve(self.loc,self.bound,git,(self.reg,))

class WindowsPlainRecordedLookupTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='windows-plain-location-')
        self.store=GenerationStore.create(Path(self.tmp.name)/'state.sqlite3',project=P,instance=I,generation='g',active_check=lambda:None)
        self.service=Connections(self.store)
        self.root=NativeLocation(r'C:\Users\Probe\Trial\project','123','abc:456')
        self.cmd=replace(self.root,path=r'c:\users\probe\trial\project')
        self.loc=Locator(P,I,1,'a'*64,W);self.bound=ProjectBinding(self.loc,'plain',self.root)
        self.reg=WorkspaceRegistration(W,self.root,None);self.top=Topology('plain',self.root)
        self.service.connect(operation='original',binding=self.bound,observed=self.top,workspace=self.reg,verify_topology=lambda:self.top)
    def tearDown(self):self.store.close();self.tmp.cleanup()
    def test_recorded_workspace_lookup_and_local_verify_preserve_exact_heads(self):
        before=self.store.root();binding=self.service.binding()[0];registration=self.store.head(workspace_key(W))
        observed=Topology('plain',self.cmd)
        self.assertIsNone(self.store.head(location_key(self.cmd)))
        self.assertEqual((self.reg,),self.service.registrations(observed))
        self.assertEqual(W,require_registered(resolve(self.loc,self.bound,observed,self.service.registrations(observed))))
        workspace=LocalWorkspace(self.store,Path(self.cmd.path),W,locator_reader=lambda:self.loc)
        with patch('colvia.workspace.discover',return_value=observed):workspace.verify()
        self.assertEqual(before,self.store.root());self.assertEqual(binding,self.service.binding()[0])
        self.assertEqual(registration,self.store.head(location_key(self.root)))
        self.assertIsNone(self.store.head(location_key(self.cmd)))
    def test_same_spelling_different_identity_is_not_accepted_by_lookup(self):
        top=Topology('plain',replace(self.cmd,file_id='other:456'))
        self.assertEqual((),self.service.registrations(top))
        with self.assertRaisesRegex(RecordError,'project-location-changed'):
            resolve(self.loc,self.bound,top,self.service.registrations(top))
    def test_missing_original_index_refuses_without_rebuilding_it(self):
        original=self.store.head
        with patch.object(self.store,'head',side_effect=lambda key:None if key==location_key(self.root) else original(key)):
            with self.assertRaisesRegex(RecordError,'workspace-location-index-mismatch'):
                self.service.registrations(Topology('plain',self.cmd))
    def test_missing_workspace_head_refuses(self):
        original=self.store.head
        with patch.object(self.store,'head',side_effect=lambda key:None if key==workspace_key(W) else original(key)):
            with self.assertRaisesRegex(RecordError,'workspace-registration-required'):
                self.service.registrations(Topology('plain',self.cmd))
    def test_foreign_original_index_refuses(self):
        original=self.store.head
        with patch.object(self.store,'head',side_effect=lambda key:self.service.binding()[0] if key==location_key(self.root) else original(key)):
            with self.assertRaisesRegex(RecordError,'workspace-location-index-mismatch'):
                self.service.registrations(Topology('plain',self.cmd))
    def test_reconnect_case_spelling_is_not_a_new_path(self):
        self.assertTrue(same_plain_path(self.root.path,self.cmd.path))
        self.assertFalse(same_plain_path(self.root.path,r'C:\Elsewhere'))
    def test_lookup_does_not_scan_all_heads_or_publish_new_records(self):
        with patch.object(self.store,'root',side_effect=AssertionError('no full head scan')),\
             patch.object(self.store,'commit_heads',side_effect=AssertionError('read must not publish')):
            self.assertEqual((self.reg,),self.service.registrations(Topology('plain',self.cmd)))

if __name__=='__main__':unittest.main()
