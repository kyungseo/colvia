"""Native source tests; every authority and Work is a synthetic fixture."""
from contextlib import closing
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

from colvia import connection_identity as identities
from colvia.binding import NativeLocation, WorkspaceRegistration, resolve
from colvia.codec import RecordError, canonical_bytes, decode_canonical
from colvia.connection import Connections, location_key, workspace_key
from colvia.graph import validate_closure
from colvia.identity_setup import IdentitySetup
from colvia.platforms import posix
from colvia.records import application_registry, operation_closure
from colvia.storage.authority import Authority
from colvia.storage.sqlite import runtime_capabilities
from colvia.work import WorkService, work_key
from colvia.workspace import LocalWorkspace
from colvia.cli import read_locator
from colvia.adapters.git import discover
from test_foundation_git import GitFixture
from test_foundation_project_setup import SetupFixture
import test_foundation_project_setup as setup_tests
from test_foundation_work import WorkFixture


def old_location(fd, info):
    # A different device number models the observed failure. The inode is real.
    return '1', str(info.st_ino)


@unittest.skipUnless(sys.platform == 'darwin', 'Darwin native location tests')
class IdentityTests(SetupFixture, unittest.TestCase):
    setUp = setup_tests.SetupTests.setUp
    tearDown = setup_tests.SetupTests.tearDown
    connect = setup_tests.SetupTests.connect
    start_work = WorkFixture.start
    plan = WorkFixture.plan
    submit = WorkFixture.submit

    def legacy(self, name):
        root = self.base/name
        root.mkdir()
        with patch('colvia.platforms.darwin_location.persistent_identity', old_location):
            return root, self.connect(root, 'connect-'+name)

    def test_exact_batch_restores_connection_and_old_work_after_interruption(self):
        entries = [self.legacy('old'+str(i)) for i in range(6)]
        root, project = entries[0]
        target = self.base/'independent'
        target.mkdir()
        with self.assertRaisesRegex(RecordError, 'connection-identity-review-required'):
            self.setup.preview(target)
        manager = IdentitySetup(self.manager)
        authority = self.manager.authority(project)
        locator = read_locator(root,None)
        old_caps = runtime_capabilities()-{'schema:connection.identity:1','schema:observation.snapshot:2'}
        with closing(Authority(authority.root,project=project,reader_capabilities=old_caps,
                               writer_capabilities=old_caps).store()) as old, closing(authority.store()) as self.store:
            ws = LocalWorkspace(self.store, root, locator.workspace, locator_reader=lambda: locator)
            self.service = WorkService(self.store, ws)
            with patch('colvia.platforms.darwin_location.persistent_identity', old_location):
                self.start_work('history', ('history.md',))
                (root/'history.md').write_text('Historical result\n')
                self.submit('history')
                self.start_work()
            history = self.store.head(work_key('history'))
            history_raw = self.store.load(history)
            active = self.store.head(work_key('report'))
            binding = Connections(self.store).binding_record()[0]
            wref, original = Connections(self.store).workspace_record(locator.workspace)
            ids = [p for _, p in entries]
            before = self.store.root().ref
            preview = manager.preview(ids)
            self.assertEqual(before, self.store.root().ref)
            with patch.object(manager, '_apply', side_effect=RuntimeError('after journal')):
                with self.assertRaisesRegex(RuntimeError, 'after journal'):
                    manager.start(operation='approved-batch', plan=preview['plan'],
                                  receipt=preview['receipt'], statement='Confirm these exact folders')
            value = manager._journal('approved-batch')
            def interrupted(_):
                raise RuntimeError('after first commit')
            with manager.management():
                with self.assertRaisesRegex(RuntimeError, 'after first commit'):
                    manager._apply(value, checkpoint=interrupted)
            progress = manager.status('approved-batch')
            self.assertEqual(1, len(progress['completed']))
            self.assertEqual(5, len(progress['remaining']))
            blocked_root=next(path for path,p in entries if p in progress['remaining'])
            moved=blocked_root.with_name('temporarily-missing')
            blocked_root.rename(moved)
            try:
                self.assertEqual(progress,manager.status('approved-batch'))
                with self.assertRaises(OSError):manager.resume('approved-batch')
            finally:moved.rename(blocked_root)
            finished = manager.resume('approved-batch')
            self.assertEqual(sorted(ids), finished['completed'])
            self.assertEqual(finished,manager.resume('approved-batch'))
            self.assertEqual(active, self.store.head(work_key('report')))
            self.assertEqual(history_raw,self.store.load(history))
            self.assertEqual(binding,Connections(self.store).binding_record()[0])
            self.assertEqual(wref,self.store.head(location_key(original.root)))
            self.assertEqual(wref,self.store.head(location_key(posix.location(root))))
            with self.assertRaisesRegex(RecordError, 'store-reader-capability-unavailable'):
                old.root()
            self.setup.preview(target)
            child=root/'child';child.mkdir()
            with self.assertRaisesRegex(RecordError,'connect-project-overlap'):
                self.setup.preview(child)
            # Identity migration invalidates the location pinned by this handle.
            migrated = self.store.root().ref
            with self.assertRaisesRegex(RecordError, 'workspace-location-changed'):
                self.submit(operation='stale-handle-submit')
            self.assertEqual(migrated, self.store.root().ref)
            self.assertEqual(active, self.store.head(work_key('report')))
            # Reopen as a new command would, preserving the original Work records.
            with closing(authority.store()) as self.store:
                fresh_locator = read_locator(root, None)
                fresh_workspace = LocalWorkspace(self.store, root, fresh_locator.workspace,
                                                 locator_reader=lambda: fresh_locator)
                self.service = WorkService(self.store, fresh_workspace)
                self.assertEqual(active, self.store.head(work_key('report')))
                self.assertEqual(history_raw, self.store.load(history))
                (root/'report.md').write_text('Approved result\n')
                (root/'outside.md').write_text('Unapproved result\n')
                with self.assertRaisesRegex(RecordError, 'outside-scope-change'):
                    self.submit(operation='blocked-submit')
                self.assertEqual(active,self.store.head(work_key('report')))
                (root/'outside.md').unlink()
                result=self.submit()
                self.assertTrue(result['current_matches'])
                final=self.service.accept(operation='accept',work='report',receipt=result['receipt'],statement='Accept')
                self.assertEqual('completed',final['state'])
                registry=application_registry()
                validate_closure([self.store.head(work_key('report')),history],self.store.load,registry,operation_closure(registry))
                self.assertEqual(history_raw,self.store.load(history))

    def test_plan_drift_and_unknown_roots_refuse_without_publication(self):
        root, project = self.legacy('first')
        other, second = self.legacy('second')
        manager=IdentitySetup(self.manager)
        with self.assertRaisesRegex(RecordError,'connection-identity-review-required'):
            manager.preview([project])
        plan=manager.preview([project,second])
        locator=root/'.colvia-link.json';original=locator.read_bytes()
        changed=decode_canonical(original);changed['binding_epoch']+=1
        locator.write_bytes(canonical_bytes(changed))
        self.assertNotEqual(original,locator.read_bytes())
        with self.assertRaisesRegex(RecordError,'stale-or-foreign-binding'):
            manager.start(operation='drift',plan=plan['plan'],receipt=plan['receipt'],statement='Old preview')
        with closing(self.manager.authority(project).store()) as store:
            self.assertIsNone(store.head(identities.PROJECT_IDENTITY))
        self.assertFalse((self.manager.root/'operations/drift').exists())

    def test_native_identity_differs_for_replaced_root_and_keeps_live_pair(self):
        loc, live=posix.directory_location(self.root)
        self.assertEqual(str(self.root.stat().st_dev),live[0])
        self.assertEqual(str(self.root.stat().st_ino),live[1])
        self.assertEqual(live[1],loc.file_id.split(':')[0])
        self.assertNotEqual(loc.volume,live[0])
        self.root.rename(self.root.with_name('retained'))
        self.root.mkdir()
        self.assertNotEqual(loc,posix.location(self.root))

    def test_unqualified_filesystem_does_not_fall_back_to_device_number(self):
        from types import SimpleNamespace
        with patch('colvia.platforms.darwin_location.filesystem',
                   return_value=SimpleNamespace(fstype=b'nfs',flags=0)):
            with self.assertRaisesRegex(RecordError,'persistent-location-unavailable'):
                posix.location(self.root)

    def test_selected_legacy_root_cannot_overlap_a_reserved_project(self):
        root,project=self.legacy('outer')
        child=root/'child';child.mkdir()
        # Model a pre-existing conflicting reservation directly, without
        # defeating the actual setup command's overlap check.
        import uuid
        from colvia.binding import Locator,ProjectBinding,Topology
        other,instance,workspace=(str(uuid.uuid4()) for _ in range(3))
        authority=Authority.create(self.manager.root/'authorities'/other,project=other,
                                   instance=instance,generation='initial',files=self.manager.files)
        top=Topology('plain',posix.location(child))
        with closing(authority.store()) as store:
            Connections(store).connect(operation='reserved',binding=ProjectBinding(
                Locator(other,instance,1,'f'*64,workspace),'plain',top.root),observed=top,
                workspace=WorkspaceRegistration(workspace,top.root,None),verify_topology=lambda:top)
        with self.assertRaisesRegex(RecordError,'identity-project-overlap'):
            IdentitySetup(self.manager).preview([project])

    def test_creation_time_drift_stops_without_equating_same_inode(self):
        import os
        project=self.connect(self.root,'original')
        locator=read_locator(self.root,None)
        other=self.base/'independent';other.mkdir()
        old,live=posix.directory_location(self.root)
        earlier=int(old.file_id.split(':')[1])-86400
        os.utime(self.root,(earlier,earlier))
        current,now=posix.directory_location(self.root)
        self.assertEqual(live,now)
        if old==current:
            self.skipTest('this filesystem keeps birth time when backdating mtime')
        with closing(self.manager.authority(project).store()) as store:
            state=store.root().ref
            ws=LocalWorkspace(store,self.root,locator.workspace,locator_reader=lambda:locator)
            with self.assertRaisesRegex(RecordError,'connection-creation-identity-changed'):ws.verify()
            with self.assertRaisesRegex(RecordError,'connection-creation-identity-changed'):self.setup.preview(other)
            self.assertEqual(state,store.root().ref)

    def test_apply_rechecks_live_pair_when_persistent_identity_matches(self):
        _,project=self.legacy('first')
        manager=IdentitySetup(self.manager)
        preview=manager.preview([project])
        def changed(path):
            loc,live=posix.directory_location(path)
            return loc,(str(int(live[0])+1),live[1])
        with patch('colvia.identity_setup.directory_location',changed):
            with self.assertRaisesRegex(RecordError,'identity-review-changed'):
                manager.start(operation='changed-mount',plan=preview['plan'],receipt=preview['receipt'],statement='Old preview')
        self.assertFalse((self.manager.root/'operations/changed-mount').exists())

    def test_missing_independent_legacy_root_is_still_an_unresolved_boundary(self):
        _,project=self.legacy('first')
        root,_=self.legacy('missing')
        root.rename(self.base/'moved-away')
        with self.assertRaisesRegex(RecordError,'connect-boundary-unavailable'):
            IdentitySetup(self.manager).preview([project])

    def test_same_inode_without_applicable_anchor_is_not_equivalence(self):
        loc=posix.location(self.root)
        legacy=NativeLocation(loc.path,'1',loc.file_id.split(':')[0])
        from dataclasses import asdict,replace
        from colvia.binding import revalidates
        self.assertTrue(revalidates(legacy,loc))
        self.assertFalse(revalidates(legacy,replace(loc,path=loc.path+'/copy')))
        self.assertFalse(identities.equivalent(None,None,None,asdict(legacy),asdict(loc),'root'))


@unittest.skipUnless(sys.platform == 'darwin','Darwin native location tests')
class GitIdentityTests(SetupFixture, GitFixture, unittest.TestCase):
    connect = setup_tests.SetupTests.connect

    def setUp(self):
        GitFixture.setUp(self)
        self.manager_fixture(self.home,self.git)

    def test_revalidated_git_preserves_linked_registration_and_accepts_new_members(self):
        sibling=self.home/'sibling'
        self.command('worktree','add','-qb','sibling',str(sibling))
        with patch('colvia.platforms.darwin_location.persistent_identity',old_location):
            project=self.connect(self.root,'legacy-git')
            with closing(self.manager.authority(project).store()) as store:
                con=Connections(store);loc=read_locator(self.root,self.git)
                top=discover(sibling,self.git)
                registered=WorkspaceRegistration('00000000-0000-4000-8000-000000000004',top.root,top.gitdir)
                wref=con.register(operation='legacy-sibling',locator=loc,observed=top,workspace=registered,
                                 registrations=con.registrations(top),verify_topology=lambda:discover(sibling,self.git))
        manager=IdentitySetup(self.manager,self.git);p=manager.preview([project])
        manager.start(operation='revalidate-git',plan=p['plan'],receipt=p['receipt'],statement='Confirm both existing folders')
        with closing(self.manager.authority(project).store()) as store:
            con=Connections(store);_,bound=con.binding()
            top=discover(sibling,self.git)
            self.assertEqual(registered.workspace,resolve(loc,bound,top,con.registrations(top)).workspace)
            self.assertEqual(wref,store.head(workspace_key(registered.workspace)))
            alias=location_key(top.root)
            # Remove the derived alias in this synthetic store only. An
            # independent connect must not mistake the member for unoccupied.
            store.commit_heads(operation='fixture-drop-alias',expected={alias:wref},
                               changes={alias:None},validate=lambda _:None)
            with self.assertRaisesRegex(RecordError,'connect-boundary-unavailable'):
                self.setup.preview(sibling)
            store.commit_heads(operation='fixture-restore-alias',expected={alias:None},
                               changes={alias:wref},validate=lambda _:None)
            fresh=self.home/'fresh'
            self.command('worktree','add','-qb','fresh',str(fresh))
            top=discover(fresh,self.git)
            new=WorkspaceRegistration('00000000-0000-4000-8000-000000000005',top.root,top.gitdir)
            newref=con.register(operation='new-sibling',locator=loc,observed=top,workspace=new,
                                registrations=con.registrations(top),verify_topology=lambda:discover(fresh,self.git))
            self.assertEqual(newref,con.workspace(new.workspace)[0])
            self.assertIsNotNone(con.identity(newref))
        with self.assertRaisesRegex(RecordError,'connect-project-overlap'):
            self.setup.preview(fresh)


    def test_removed_git_member_is_preserved_as_history_without_blocking_primary(self):
        sibling=self.home/'removed-member'
        self.command('worktree','add','-qb','removed',str(sibling))
        with patch('colvia.platforms.darwin_location.persistent_identity',old_location):
            project=self.connect(self.root,'legacy-git-removed')
            with closing(self.manager.authority(project).store()) as store:
                con=Connections(store);loc=read_locator(self.root,self.git)
                top=discover(sibling,self.git)
                registered=WorkspaceRegistration('00000000-0000-4000-8000-000000000004',top.root,top.gitdir)
                wref=con.register(operation='legacy-removed',locator=loc,observed=top,workspace=registered,
                                 registrations=con.registrations(top),verify_topology=lambda:discover(sibling,self.git))
        self.command('worktree','remove',str(sibling))
        manager=IdentitySetup(self.manager,self.git)
        preview=manager.preview([project])
        self.assertEqual([wref.as_dict()],preview['plan']['census'][0]['absent'])
        sibling.mkdir()
        with self.assertRaisesRegex(RecordError,'identity-membership-unverified'):
            manager.start(operation='conflict',plan=preview['plan'],receipt=preview['receipt'],statement='Confirm original')
        sibling.rmdir()
        status=manager.start(operation='recover-primary',plan=preview['plan'],receipt=preview['receipt'],statement='Confirm original')
        self.assertEqual('revalidated',status['state'])
        with closing(self.manager.authority(project).store()) as store:
            con=Connections(store)
            self.assertEqual(wref,store.head(workspace_key(registered.workspace)))
            self.assertIsNone(con.identity(wref))
            top=discover(self.root,self.git)
            self.assertEqual(1,len(con.registrations(top,current_only=True,complete=True)))

    def test_plain_reservation_at_git_common_directory_blocks_linked_root(self):
        import uuid
        from colvia.binding import Locator,ProjectBinding,Topology
        sibling=self.home/'linked-independent'
        self.command('worktree','add','-qb','linked-independent',str(sibling))
        other,instance,workspace=(str(uuid.uuid4()) for _ in range(3))
        authority=Authority.create(self.manager.root/'authorities'/other,project=other,
                                   instance=instance,generation='initial',files=self.manager.files)
        top=Topology('plain',posix.location(self.root/'.git'))
        with closing(authority.store()) as store:
            Connections(store).connect(operation='reserved-common',binding=ProjectBinding(
                Locator(other,instance,1,'f'*64,workspace),'plain',top.root),observed=top,
                workspace=WorkspaceRegistration(workspace,top.root,None),verify_topology=lambda:top)
        with self.assertRaisesRegex(RecordError,'connect-project-overlap'):
            self.setup.preview(sibling)
