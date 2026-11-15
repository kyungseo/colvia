"""Refusal ownership and nested project regressions; synthetic stores only."""
import time,unittest
from unittest.mock import patch

from colvia.codec import RecordError,PublicationRefused,canonical_bytes,object_ref
from colvia.connection import Connections
from colvia.connection_boundary import ConnectionBoundaryError,workspace_topology
from colvia.delivery.service import DeliveryService
from colvia.platforms.posix import ObservationBudget,snapshot
from colvia.platforms.windows_observation import Observer
from colvia.storage.sqlite import StorageError
from colvia.workspace import LocalWorkspace
from test_foundation_work import WorkFixture
from test_foundation_work_git import GitWorkFixture
from test_foundation_windows_observation import FilesDouble


class RefusalTests(WorkFixture,unittest.TestCase):
    def row(self,op):
        row=self.store.db.execute('SELECT owner,state FROM imports WHERE id=?',(op,)).fetchone()
        return tuple(row) if row else None
    def counts(self):
        return tuple(self.store.db.execute('SELECT count(*) FROM '+table).fetchone()[0]
                     for table in ('imports','claims','objects','operations'))
    def checks(self):return [dict(name=n,status='passed',detail='synthetic') for n in ('원본 보존','집계 대조')]
    def ready(self):self.start();(self.root/'report.md').write_text('synthetic report')
    def test_bad_input_stages_nothing_and_same_operation_can_submit(self):
        self.ready();before=self.counts();head=self.store.root().ref
        invalid=[None,{},[None],[dict(name='bad',status='passed',detail='x')],[],self.checks()[:1],
                 self.checks()+self.checks()[:1],[self.checks()[0],self.checks()[0]],
                 [dict(name='원본 보존',status='invented',detail='x')],
                 [dict(name=[],status='passed',detail='x')]]
        for checks in invalid:
            with self.subTest(checks=checks):
                with self.assertRaises(RecordError):
                    self.service.submit(operation='attempt',work='report',summary='synthetic',checks=checks)
                self.assertEqual(before,self.counts());self.assertEqual(head,self.store.root().ref)
                self.assertFalse(self.store.has_active_imports())
        with self.assertRaises(RecordError):
            self.service.submit(operation='attempt',work='report',summary=None,checks=self.checks())
        self.assertEqual(before,self.counts())
        self.assertEqual('review',self.submit(operation='attempt')['state'])
        self.assertEqual(('ordinary-result','published'),self.row('attempt'))
    def test_late_refusal_preserves_chunks_and_claims_and_corrected_submit(self):
        self.ready();root=self.store.root().ref
        with patch.object(self.service,'_recheck_observation',side_effect=RecordError('synthetic-late-refusal')):
            with self.assertRaisesRegex(PublicationRefused,'synthetic-late-refusal'):self.submit(operation='late')
        self.assertEqual(root,self.store.root().ref);self.assertFalse(self.store.has_active_imports())
        self.assertEqual(('ordinary-result','abandoned'),self.row('late'))
        claims=[tuple(r) for r in self.store.db.execute("SELECT digest FROM claims WHERE import_id='late'")]
        self.assertTrue(claims)
        with self.assertRaisesRegex(RecordError,'import-already-exists'):self.submit(operation='late')
        self.assertEqual('review',self.submit(operation='corrected')['state'])
        self.assertEqual(claims,[tuple(r) for r in self.store.db.execute("SELECT digest FROM claims WHERE import_id='late'")])
        for (digest,) in claims:self.assertEqual(1,self.store.db.execute('SELECT published FROM objects WHERE digest=?',(digest,)).fetchone()[0])
    def test_unproven_failures_keep_active_import(self):
        self.ready();root=self.store.root().ref
        for number,error in enumerate((RecordError('store-outcome-unknown'),StorageError('store-io-unavailable',{}),OSError('synthetic'),KeyboardInterrupt())):
            op='unknown-'+str(number)
            with self.subTest(kind=type(error).__name__),patch.object(self.store,'commit_heads',side_effect=error):
                with self.assertRaises(type(error)):self.submit(operation=op)
                self.assertEqual(('ordinary-result','active'),self.row(op));self.assertEqual(root,self.store.root().ref)
    def test_validation_engine_error_does_not_attempt_close(self):
        self.ready();before=self.store.root().ref
        with patch.object(self.service,'_recheck_observation',side_effect=StorageError('store-corrupt',{})),patch.object(self.store,'_abandon_current_import') as close:
            with self.assertRaisesRegex(StorageError,'store-corrupt'):self.submit(operation='engine')
        close.assert_not_called()
        self.assertEqual(before,self.store.root().ref);self.assertEqual(('ordinary-result','active'),self.row('engine'))

    def test_existing_import_and_published_operation_never_abandoned(self):
        self.ready();self.store.begin_import('foreign','other-owner')
        with self.assertRaisesRegex(RecordError,'import-already-exists'):self.submit(operation='foreign')
        self.assertEqual(('other-owner','active'),self.row('foreign'))
        with self.assertRaisesRegex(RecordError,'operation-already-recorded'):self.submit(operation='report-start')
        self.assertIsNone(self.row('report-start'))
    def test_post_commit_error_never_demotes_published_import(self):
        self.ready();commit=self.store.commit_heads
        def committed(**kw):commit(**kw);raise RecordError('synthetic-after-commit')
        with patch.object(self.store,'commit_heads',side_effect=committed):
            with self.assertRaisesRegex(RecordError,'synthetic-after-commit') as caught:self.submit(operation='committed')
        self.assertEqual('published',caught.exception.preparation_state)
        self.assertEqual(('ordinary-result','published'),self.row('committed'))
        self.assertEqual('review',self.service.view('report')['state'])
    def test_guard_failure_keeps_original_error_and_active_import(self):
        self.ready();guard=self.store.write_check
        def refuse(*_):
            self.store.write_check=lambda:(_ for _ in ()).throw(RecordError('synthetic-guard'))
            raise RecordError('synthetic-refusal')
        try:
            with patch.object(self.service,'_recheck_observation',side_effect=refuse):
                with self.assertRaisesRegex(RecordError,'synthetic-refusal') as caught:self.submit(operation='guarded')
            self.assertEqual('unconfirmed',caught.exception.preparation_state)
            self.assertEqual(('ordinary-result','active'),self.row('guarded'))
        finally:self.store.write_check=guard
    def test_shared_chunk_other_import_is_not_changed(self):
        self.ready();raw=b'shared synthetic';chunk=object_ref('body.chunk',1,raw)
        self.store.begin_import('peer','peer-owner');self.store.stage('peer',[(chunk,raw)])
        with self.assertRaisesRegex(RecordError,'synthetic-stop'):
            with self.store.import_attempt('own','ordinary-result'):
                self.store.stage('own',[(chunk,raw)]);raise RecordError('synthetic-stop')
        self.assertEqual(('peer-owner','active'),self.row('peer'));self.assertEqual(('ordinary-result','abandoned'),self.row('own'))
        self.assertEqual(raw,self.store.load(chunk,import_id='peer'))
        self.assertEqual(2,self.store.db.execute('SELECT count(*) FROM claims WHERE digest=?',(chunk.sha256,)).fetchone()[0])
    def test_delivery_input_and_late_refusal_use_same_boundary(self):
        self.ready();delivery=DeliveryService(self.service);before=self.counts();root=self.store.root().ref
        kw=dict(operation='delivery',delivery='handoff',work='report',action='submit',deadline_ns=time.time_ns()+600*10**9,summary='synthetic',checks=self.checks())
        with self.assertRaisesRegex(RecordError,'delivery-action-input'):delivery.prepare(**kw,grant='not-allowed')
        with self.assertRaises(RecordError):delivery.prepare(**{**kw,'checks':None})
        self.assertEqual(before,self.counts())
        with patch.object(self.service,'_recheck_observation',side_effect=RecordError('synthetic-delivery-refusal')):
            with self.assertRaisesRegex(RecordError,'synthetic-delivery-refusal'):delivery.prepare(**kw)
        self.assertEqual(root,self.store.root().ref);self.assertEqual(('ordinary-result','abandoned'),self.row('delivery'))
        self.assertFalse(self.store.has_active_imports())
        self.assertEqual('prepared',delivery.prepare(**{**kw,'operation':'delivery-corrected'})['state'])


class NestedProjectTests(WorkFixture,unittest.TestCase):
    def marker(self):
        (self.root/'.colvia-link.json').write_bytes(canonical_bytes(self.locator.payload()))
    def test_moved_child_and_parent_refuse_and_preserve_both_works(self):
        self.marker();self.start();(self.root/'report.md').write_text('A draft')
        other=WorkFixture()
        with patch('test_foundation_work.P','22222222-2222-4222-8222-222222222222'),patch('test_foundation_work.I','33333333-3333-4333-8333-333333333333'),patch('test_foundation_work.W','44444444-4444-4444-8444-444444444444'):
            other.setUp()
        try:
            (other.root/'.colvia-link.json').write_bytes(canonical_bytes(other.locator.payload()))
            other.start();(other.root/'report.md').write_text('B draft')
            aroot=self.store.root().ref;broot=other.store.root().ref
            moved=other.root/'A';self.root.rename(moved);self.workspace.root=moved
            with self.assertRaisesRegex(ConnectionBoundaryError,'workspace-ancestor-project') as caught:self.workspace.verify()
            self.assertEqual(str(other.root),caught.exception.directory);self.assertEqual(str(moved),caught.exception.workspace)
            for run in (lambda:other.plan('new',('A/report.md',)),lambda:other.submit()):
                with self.assertRaisesRegex(ConnectionBoundaryError,'workspace-nested-project') as caught:run()
                self.assertEqual(str(moved),caught.exception.directory);self.assertEqual(str(other.root),caught.exception.workspace)
            self.assertEqual(aroot,self.store.root().ref);self.assertEqual(broot,other.store.root().ref)
            self.assertEqual('A draft',(moved/'report.md').read_text());self.assertEqual('B draft',(other.root/'report.md').read_text())
            self.assertFalse(self.store.has_active_imports());self.assertFalse(other.store.has_active_imports())
        finally:other.tearDown()
    def test_disjoint_move_or_copy_does_not_rebind(self):
        import shutil
        self.marker();self.start();before=self.store.root().ref
        copy=self.root.parent/'copy';shutil.copytree(self.root,copy)
        for path in (copy,self.root.parent/'moved'):
            if not path.exists():self.root.rename(path)
            workspace=LocalWorkspace(self.store,path,self.workspace.workspace,locator_reader=lambda:self.locator)
            with self.assertRaisesRegex(RecordError,'project-location-changed'):workspace.verify()
            self.assertEqual(before,self.store.root().ref)
    def test_sibling_marker_does_not_block_current_workspace(self):
        self.marker();sibling=self.root.parent/'sibling';sibling.mkdir();(sibling/'.colvia-link.json').write_text('{}')
        self.start();(self.root/'report.md').write_text('synthetic');self.assertEqual('review',self.submit()['state'])
    def test_marker_inserted_after_preparation_refuses_publication_and_closes_import(self):
        self.marker();self.start();(self.root/'report.md').write_text('synthetic');before=self.store.root().ref
        publish=self.service._publish
        def changed(*args,**kwargs):
            child=self.root/'new-child';child.mkdir();(child/'.colvia-link.json').write_text('{}')
            return publish(*args,**kwargs)
        with patch.object(self.service,'_publish',side_effect=changed):
            with self.assertRaisesRegex(RecordError,'workspace-nested-project') as caught:self.submit(operation='changed')
        self.assertEqual(str(self.root/'new-child'),caught.exception.directory)
        self.assertEqual(before,self.store.root().ref);self.assertFalse(self.store.has_active_imports())
        self.assertEqual('abandoned',self.store.db.execute("SELECT state FROM imports WHERE id='changed'").fetchone()[0])
    def test_plain_subdirectory_points_to_parent_without_claiming_independent_move(self):
        self.marker();child=self.root/'ordinary-subdir';child.mkdir()
        with self.assertRaisesRegex(ConnectionBoundaryError,'workspace-parent-project') as caught:workspace_topology(child,None)
        self.assertEqual(str(self.root),caught.exception.directory);self.assertEqual(str(child),caught.exception.workspace)

    def test_unavailable_ancestor_is_a_workspace_diagnostic(self):
        self.marker();marker=self.root.parent/'.git';marker.write_text('invalid git marker')
        with self.assertRaisesRegex(ConnectionBoundaryError,'workspace-boundary-unavailable') as caught:workspace_topology(self.root,None)
        self.assertEqual(str(self.root.parent),caught.exception.directory);self.assertEqual(str(self.root),caught.exception.workspace)

    def test_native_walk_contract_rejects_hidden_alias_directory_and_link_markers(self):
        budget=ObservationBudget(100,100000);ports=(lambda **kw:snapshot(self.root,budget,**kw),lambda **kw:Observer(files=FilesDouble()).snapshot(self.root,budget,**kw))
        for kind in ('file','directory','symlink','alias'):
            child=self.root/kind;child.mkdir();name='.COLVIA-LINK.JSON' if kind=='alias' else '.colvia-link.json';marker=child/name
            if kind=='directory':marker.mkdir()
            elif kind=='symlink':marker.symlink_to('absent')
            else:marker.write_text('{}')
            for port in ports:
                with self.subTest(kind=kind,port=port),self.assertRaisesRegex(ConnectionBoundaryError,'workspace-nested-project'):
                    port(admit=lambda _:False,reject_nested_colvia=True)
            if kind=='directory':marker.rmdir()
            else:marker.unlink()
            child.rmdir()
        child=self.root/'git-child';child.mkdir();marker=child/'.git';marker.mkdir()
        for port in ports:
            with self.assertRaisesRegex(ConnectionBoundaryError,'unregistered-nested-git') as caught:
                port(reject_nested_git=True,reject_nested_colvia=True)
            self.assertEqual(str(child),caught.exception.directory);self.assertEqual(str(self.root),caught.exception.workspace)
        marker.rmdir();child.rmdir()
        root_marker=self.root/'.COLVIA-LINK.JSON';root_marker.write_text('{}')
        for port in ports:
            with self.assertRaisesRegex(ConnectionBoundaryError,'workspace-nested-project'):port(reject_nested_colvia=True)


class GitNestedProjectTests(GitWorkFixture,unittest.TestCase):
    def test_registered_worktree_remains_opaque_and_child_verifies(self):
        parent=self.nested();child=parent/'child';(child/'.colvia-link.json').write_text('{}')
        # Parent's exact registered structural boundary still prevents collection.
        view=self.service.workspace.observe()[1]
        self.assertFalse(any(e['path'].startswith('.claude/worktrees/') for e in view.snapshot.entries))
        (child/'.colvia-link.json').unlink()
        connections=Connections(self.store);top=self.git.topology(child)
        registration=next(r for r in connections.registrations(top) if r.root==top.root)
        local=LocalWorkspace(self.store,child,registration.workspace,git=self.git,locator_reader=lambda:self.locator)
        local.verify()
    def test_ignored_independent_plain_child_is_not_absorbed(self):
        child=self.root/'independent';child.mkdir();(child/'.colvia-link.json').write_text('{}')
        (self.root/'.gitignore').write_text('independent/\n')
        with self.assertRaisesRegex(RecordError,'workspace-nested-project'):self.service.workspace.observe()
    def test_independent_git_child_and_parent_both_report_conflict_paths(self):
        directory=self.root/'.git/colvia';directory.mkdir();(directory/'connection.json').write_text('{}')
        child=self.root/'independent-git';child.mkdir();self.command('init','-q',root=child)
        with self.assertRaisesRegex(ConnectionBoundaryError,'workspace-ancestor-project') as caught:workspace_topology(child,self.git)
        self.assertEqual(str(self.root),caught.exception.directory);self.assertEqual(str(child),caught.exception.workspace)
        with self.assertRaisesRegex(RecordError,'unregistered-nested-git') as caught:self.service.workspace.observe()
        self.assertEqual(str(child),caught.exception.directory);self.assertEqual(str(self.root),caught.exception.workspace)

    def test_git_root_does_not_absorb_plain_connection_marker(self):
        (self.root/'.colvia-link.json').write_text('{}')
        with self.assertRaisesRegex(ConnectionBoundaryError,'workspace-connection-kind-changed'):self.service.workspace.verify()

    def test_plain_child_of_connected_git_root_is_not_redirected_to_parent(self):
        directory=self.root/'.git/colvia';directory.mkdir();(directory/'connection.json').write_text('{}')
        child=self.root/'independent';child.mkdir();(child/'.colvia-link.json').write_text('{}')
        with self.assertRaisesRegex(ConnectionBoundaryError,'workspace-ancestor-project') as caught:workspace_topology(child,self.git)
        self.assertEqual(str(child),caught.exception.workspace);self.assertEqual(str(self.root),caught.exception.directory)


class BoundaryCLITests(unittest.TestCase):
    from test_foundation_cli import CLITests as _fixture
    setUp=_fixture.setUp
    tearDown=_fixture.tearDown
    call=_fixture.call

    def test_nested_refusal_explains_both_paths_in_human_and_json_output(self):
        child=self.root/'child';child.mkdir();(child/'.colvia-link.json').write_text('{}')
        args=('ordinary','plan','report','--title','synthetic','--goal','synthetic','--path','report.md','--check','synthetic')
        result=self.call(*args,code=2)
        self.assertEqual('workspace-nested-project',result['error'])
        self.assertEqual(str(child),result['directory']);self.assertEqual(str(self.root),result['workspace'])
        text=self.call(*args,code=2,machine=False)
        self.assertIn(str(child),text);self.assertIn(str(self.root),text)
        self.assertIn('겹치지 않는',text);self.assertIn('지우지',text)

    def test_windows_path_display_keeps_native_separators_and_escapes_controls(self):
        from colvia.presentation import display_path
        path=r'C:\Users\Synthetic\Project With Spaces'
        self.assertEqual('"'+path+'"',display_path(path))
        self.assertNotIn('\x1b',display_path('unsafe\x1b[31m'))
        self.assertNotIn('\n',display_path('line\nbreak'))

    def test_current_location_mismatch_does_not_claim_automatic_reconnection(self):
        from colvia.presentation import failure
        text=failure('project-location-changed')
        self.assertIn('이동인지 복사인지',text);self.assertIn('지원하지',text)


if __name__=='__main__':unittest.main()
