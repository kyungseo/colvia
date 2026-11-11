"""Counterexamples raised by independent P4 result review; synthetic only."""
import os,unittest
from colvia.codec import RecordError
from colvia.effects import PENDING
from colvia.records import link
from colvia.platforms.exclusive import available
from test_foundation_worker import WorkerFixture
import test_foundation_composition as composition_fixture

@unittest.skipUnless(available(),'Darwin source effects unavailable')
class ReviewRecoveryTests(WorkerFixture,unittest.TestCase):
    def test_policy_edit_refuses_before_pending_or_file_effect(self):
        self.source_result(scope=('.gitignore','report.md'),changes={'.gitignore':b'ignored/\n','report.md':b'updated'})
        before=self.store.root().ref
        with self.assertRaisesRegex(RecordError,'worker-policy-edit-unsupported'):self.prepare()
        self.assertEqual(before,self.store.root().ref);self.assertIsNone(self.store.head(PENDING))
        self.assertFalse((self.authority/'effects').exists());self.assertFalse((self.root/'.gitignore').exists())

    def test_cancel_ignores_unrelated_destination_edit(self):
        self.source_result();self.interrupt();(self.root/'notes.md').write_text('keep unrelated note')
        self.worker.cancel(operation='cancel-unrelated',application='apply-report')
        self.assertIsNone(self.store.head(PENDING));self.assertEqual('keep unrelated note',(self.root/'notes.md').read_text())
        self.assertEqual('review',self.source.view('source')['state'])

    def test_cancel_accepts_same_pre_bytes_after_safe_save(self):
        self.source_result();self.interrupt();target=self.root/'report.md';before=target.read_bytes()
        replacement=self.root/'replacement';replacement.write_bytes(before);os.replace(replacement,target)
        self.worker.cancel(operation='cancel-new-inode',application='apply-report')
        self.assertIsNone(self.store.head(PENDING));self.assertEqual(before,target.read_bytes())

    def test_cancel_does_not_need_removed_source_checkout(self):
        self.source_result();self.interrupt();self.command('worktree','remove','--force',str(self.child))
        self.worker.cancel(operation='cancel-removed-source',application='apply-report')
        self.assertIsNone(self.store.head(PENDING));self.assertEqual(b'synthetic report\n',(self.root/'report.md').read_bytes())

    def test_retained_original_late_edit_does_not_invalidate_exact_post(self):
        self.source_result();fd=os.open(self.root/'report.md',os.O_RDWR)
        try:
            self.interrupt('after-install');os.ftruncate(fd,0);os.write(fd,b'late original note');os.fsync(fd)
        finally:os.close(fd)
        self.worker.resume(operation='resume-preserved-edit',application='apply-report')
        self.assertIsNone(self.store.head(PENDING));self.assertEqual('completed',self.source.view('source')['state'])
        self.assertEqual(b'worker result\n',(self.root/'report.md').read_bytes())
        self.assertEqual(b'late original note',(self.authority/'effects/apply-report/000000.original').read_bytes())
        self.assertEqual(['report.md'],self.worker.view('apply-report')['retained_original_modified'])

    def test_operation_length_refuses_before_reservation(self):
        self.source_result();preview=self.prepare();before=(self.root/'report.md').read_bytes()
        with self.assertRaises(RecordError):
            self.worker.execute(operation='x'*150,application='apply-report',receipt=preview['receipt'],statement='apply')
        self.assertIsNone(self.store.head(PENDING));self.assertEqual(before,(self.root/'report.md').read_bytes())
        self.assertFalse((self.authority/'effects').exists())

    def test_current_view_classifies_mixed_state_and_resume(self):
        self.source_result(scope=('report.md','second.md'),changes={'report.md':b'first','second.md':b'second'})
        self.interrupt('progress-published')
        shown=self.worker.view('apply-report');self.assertEqual(['post','pre'],[p['state'] for p in shown['paths']])
        with self.assertRaisesRegex(RecordError,'worker-cancel-requires-all-pre'):
            self.worker.cancel(operation='mixed-cancel',application='apply-report')
        self.worker.resume(operation='mixed-resume',application='apply-report')
        self.assertEqual(b'first',(self.root/'report.md').read_bytes());self.assertEqual(b'second',(self.root/'second.md').read_bytes())

    def test_already_accepted_source_can_use_retained_body_after_later_edit(self):
        review=self.source_result();self.source.accept(operation='accept-source',work='source',receipt=review['receipt'],statement='accept')
        (self.child/'report.md').write_bytes(b'later unaccepted edit');self.execute()
        self.assertEqual(b'worker result\n',(self.root/'report.md').read_bytes());self.assertEqual(b'later unaccepted edit',(self.child/'report.md').read_bytes())


    def test_staging_conflict_preserves_request_and_gives_specific_refusal(self):
        from unittest.mock import patch
        from colvia.planning import Planning
        self.source_result();preview=self.prepare();original=self.store.commit_heads;triggered=[False]
        def race(**kw):
            if kw['operation']=='execute-reserve':
                check=kw['validate']
                def validate(view):
                    check(view)
                    if not triggered[0]:
                        triggered[0]=True
                        __import__('contextvars').Context().run(lambda: Planning(self.store).save_candidate(operation='unrelated-candidate',candidate='later',title='later',reason='candidate'))
                kw['validate']=validate
            return original(**kw)
        with patch.object(self.store,'commit_heads',side_effect=race):
            with self.assertRaisesRegex(RecordError,'validation-root-conflict'):self.execute(preview)
        self.assertIsNone(self.store.head(PENDING));before=(self.authority/'effects/apply-report/000000.post').read_bytes()
        with self.assertRaisesRegex(RecordError,'effect-staging-already-exists'):self.execute(preview)
        self.assertEqual(before,(self.authority/'effects/apply-report/000000.post').read_bytes())
        self.assertEqual(b'synthetic report\n',(self.root/'report.md').read_bytes())

    def test_second_application_cannot_reserve_while_first_is_pending(self):
        self.source_result();first=self.prepare();second=self.worker.prepare(operation='second-prepare',application='second',work='source')
        self.interrupt(preview=first);root=self.store.root().ref
        with self.assertRaisesRegex(RecordError,'external-effect-pending'):
            self.worker.execute(operation='second-execute',application='second',receipt=second['receipt'],statement='apply')
        self.assertEqual(root,self.store.root().ref);self.assertFalse((self.authority/'effects/second').exists())

    def test_cancel_keeps_empty_created_ancestors(self):
        self.source_result(scope=('new/folder/file.md',),changes={'new/folder/file.md':b'new'})
        self.interrupt('before-install');self.assertTrue((self.root/'new/folder').is_dir())
        self.worker.cancel(operation='cancel-empty-ancestors',application='apply-report')
        self.assertTrue((self.root/'new/folder').is_dir());self.assertIsNone(self.store.head(PENDING))

    def test_cancel_refuses_changed_pre_bytes(self):
        self.source_result();self.interrupt();(self.root/'report.md').write_bytes(b'unaccepted target edit')
        with self.assertRaisesRegex(RecordError,'worker-cancel-requires-all-pre'):
            self.worker.cancel(operation='cannot-discard',application='apply-report')
        self.assertIsNotNone(self.store.head(PENDING));self.assertEqual(b'unaccepted target edit',(self.root/'report.md').read_bytes())

    def test_ignore_policy_drift_blocks_resume_but_not_no_effect_cancel(self):
        self.source_result();self.interrupt()
        with (self.root/'.git/info/exclude').open('ab') as out:out.write(b'additional-hidden\n')
        with self.assertRaises(RecordError):self.worker.resume(operation='changed-ignore',application='apply-report')
        self.assertIsNotNone(self.store.head(PENDING));self.worker.cancel(operation='cancel-ignore',application='apply-report')
        self.assertIsNone(self.store.head(PENDING))

    def test_pending_registration_refuses_without_new_workspace_record(self):
        from colvia.connection import Connections,workspace_key
        from colvia.binding import WorkspaceRegistration
        import uuid
        self.source_result();self.interrupt();other=self.home/'other'
        self.command('worktree','add','-q','-b','other',str(other));top=self.git.topology(other)
        connections=Connections(self.store);identifier=str(uuid.uuid4());root=self.store.root().ref
        with self.assertRaisesRegex(RecordError,'external-effect-pending'):
            connections.register(operation='blocked-registration',locator=self.locator,observed=top,
                workspace=WorkspaceRegistration(identifier,top.root,top.gitdir),registrations=connections.registrations(top),
                verify_topology=lambda:self.git.topology(other))
        self.assertIsNone(self.store.head(workspace_key(identifier)));self.assertEqual(root,self.store.root().ref)

    def test_parent_cannot_grant_or_apply_worker_acceptance(self):
        from colvia.composition import CompositionService
        for work,scope in (('source',['integration.md']),('child',['report.md'])):
            self.source.plan(operation='plan-'+work,work=work,title=work,goal='integrate',scope=scope,checks=['integration'])
        composition=CompositionService(self.source)
        composition.declare(operation='declare',parent='source',children=['child'],document='integration.md',checks=['integration'],statement='integrate')
        def begin(work):
            self.source.approve(operation='approve-'+work,work=work,receipt=self.source.plan_review(work)['receipt'],statement='proceed')
            self.source.start(operation='start-'+work,work=work)
        def submit(work):return self.source.submit(operation='submit-'+work,work=work,summary='result',checks=[dict(name='integration',status='passed',detail='checked')])
        begin('child');(self.child/'report.md').write_text('child result');review=submit('child')
        self.source.accept(operation='accept-child',work='child',receipt=review['receipt'],statement='accept')
        composition.rebind(operation='rebind-parent',parent='source',receipt=composition.rebind_preview('source')['receipt'],statement='bind')
        begin('source');(self.child/'integration.md').write_text('combined result');submit('source')
        before=self.store.root().ref
        with self.assertRaisesRegex(RecordError,'worker-parent-grant-refused'):
            self.worker.grant(operation='no-parent-grant',work='source',owner='owner',delegate='helper',statement='grant')
        with self.assertRaisesRegex(RecordError,'worker-parent-result-not-supported'):self.prepare()
        self.assertEqual(before,self.store.root().ref);self.assertIsNone(self.store.head(PENDING))


    def test_view_does_not_recreate_missing_process_lock(self):
        self.source_result();self.interrupt();lock=self.authority/'effect.lock';lock.unlink();root=self.store.root().ref
        shown=self.worker.view('apply-report')
        self.assertEqual('pending',shown['state']);self.assertIsNotNone(shown['blocked'])
        self.assertFalse(lock.exists());self.assertEqual(root,self.store.root().ref)

    def test_cancel_rejects_symlink_ancestor_even_when_file_is_absent(self):
        self.source_result(scope=('folder/file.md',),changes={'folder/file.md':b'result'});self.interrupt()
        outside=self.home/'outside';outside.mkdir();(self.root/'folder').symlink_to(outside,target_is_directory=True)
        with self.assertRaisesRegex(RecordError,'unsafe-effect-ancestor'):
            self.worker.cancel(operation='cannot-traverse',application='apply-report')
        self.assertIsNotNone(self.store.head(PENDING));self.assertFalse((outside/'file.md').exists())

    def test_cancel_accepts_replaced_regular_parent_with_exact_preimage(self):
        for root in (self.root,self.child):(root/'folder').mkdir();(root/'folder/file.md').write_bytes(b'original')
        self.source_result(scope=('folder/file.md',),changes={'folder/file.md':b'result'});self.interrupt()
        os.rename(self.root/'folder',self.home/'preserved-folder');(self.root/'folder').mkdir();(self.root/'folder/file.md').write_bytes(b'original')
        self.worker.cancel(operation='cancel-safe-parent',application='apply-report')
        self.assertIsNone(self.store.head(PENDING));self.assertEqual(b'original',(self.home/'preserved-folder/file.md').read_bytes())

    def test_cli_pending_failure_points_to_exact_application_not_parent_operation(self):
        import io,json
        from contextlib import redirect_stdout
        from unittest.mock import patch,Mock
        from colvia.cli import main
        self.source_result();self.interrupt();wrapper=Mock();wrapper.store.return_value=self.store
        args=['--source-development','--authority',str(self.authority),'--project',self.store.project,
              '--workspace',self.child_id,'--root',str(self.child),'--json','--operation','outer',
              'worker','--destination',self.destination.workspace,'resume','apply-report']
        with patch('colvia.cli.Authority',return_value=wrapper),patch('colvia.cli.dispatch',side_effect=RecordError('effect-outcome-unknown')),patch.object(self.store,'close'),redirect_stdout(io.StringIO()) as output:
            self.assertEqual(2,main(args))
        value=json.loads(output.getvalue());self.assertTrue(value['pending']);self.assertNotIn('operation',value)
        self.assertEqual('worker --destination '+self.destination.workspace+' view apply-report',value['recovery_command'])
        self.assertIn('아직 끝나지 않았습니다',value['message'])

class ArchiveReviewTests(unittest.TestCase):
    def setUp(self):
        composition_fixture.WorkFixture.setUp(self)
        self.composition=composition_fixture.CompositionService(self.service)
    tearDown=composition_fixture.CompositionTests.tearDown
    plan=composition_fixture.CompositionTests.plan
    submit=composition_fixture.CompositionTests.submit
    declare=composition_fixture.CompositionTests.declare
    begin=composition_fixture.CompositionTests.begin
    accept_child=composition_fixture.CompositionTests.accept_child
    bind=composition_fixture.CompositionTests.bind
    ready_parent=composition_fixture.CompositionTests.ready_parent
    def test_completed_parent_archive_after_child_reopen_preserves_decision(self):
        review=self.ready_parent();self.service.accept(operation='parent-accept',work='parent',receipt=review['receipt'],statement='accept')
        old=self.service._head('parent')[1];child=self.service.view('child')
        self.service.revise(operation='reopen-child',work='child',receipt=child['reopen_receipt'],statement='revise')
        self.service.archive(operation='archive-parent',work='parent',archived=True)
        new=self.service._head('parent')[1]
        self.assertEqual(link(old,'decision'),link(new,'decision'));self.assertEqual(link(old,'result'),link(new,'result'))
        self.assertTrue(new.payload['archived'])
