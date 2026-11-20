"""Isolated worker effects use real local synthetic Git worktrees only."""
from pathlib import Path
import unittest,uuid
from colvia.binding import WorkspaceRegistration
from colvia.codec import RecordError
from colvia.connection import Connections
from colvia.records import link,record
from colvia.workspace import LocalWorkspace
from colvia.work import WorkService,work_key
from colvia.worker import WorkerService,application_key
from colvia.effects import PENDING
from colvia.platforms.exclusive import available
from test_foundation_work_git import GitWorkFixture


class WorkerFixture(GitWorkFixture):
    def setUp(self):
        super().setUp();self.destination=self.service.workspace
        from colvia.codec import canonical_bytes
        locator=self.root/'.git/colvia/connection.json';locator.parent.mkdir()
        locator.write_bytes(canonical_bytes(self.locator.payload()))
        self.child=self.home/'worker';self.command('worktree','add','-q','-b','worker',str(self.child))
        top=self.git.topology(self.child);connections=Connections(self.store);self.child_id=str(uuid.uuid4())
        connections.register(operation='register-worker',locator=self.locator,observed=top,
            workspace=WorkspaceRegistration(self.child_id,top.root,top.gitdir),registrations=connections.registrations(top),verify_topology=lambda:self.git.topology(self.child))
        self.source=WorkService(self.store,LocalWorkspace(self.store,self.child,self.child_id,git=self.git,locator_reader=lambda:self.locator))
        self.authority=self.home/'effect-authority';self.authority.mkdir(mode=0o700)
        self.worker=WorkerService(self.source,self.destination,authority=self.authority)
    def source_result(self,scope=('report.md',),changes=None):
        plan=self.source.plan(operation='source-plan',work='source',title='격리 보고서',goal='내용을 고친다',scope=scope,checks=['본문 검사'])
        self.source.approve(operation='source-approve',work='source',receipt=plan['receipt'],statement='진행')
        self.source.start(operation='source-start',work='source')
        for name,raw in (changes or {'report.md':b'worker result\n'}).items():
            path=self.child/name
            if raw is None:path.unlink()
            else:path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw)
        return self.source.submit(operation='source-submit',work='source',summary='격리 결과',checks=[dict(name='본문 검사',status='passed',detail='확인')])
    def prepare(self):return self.worker.prepare(operation='prepare',application='apply-report',work='source')
    def execute(self,preview=None,**options):
        preview=preview or self.prepare()
        return self.worker.execute(operation='execute',application='apply-report',receipt=preview['receipt'],statement='이 결과를 적용하고 수락해',**options)
    def interrupt(self,stage='reserved',preview=None):
        def stop(actual):
            if actual==stage:raise RuntimeError('synthetic interruption')
        with self.assertRaisesRegex(RuntimeError,'synthetic interruption'):self.execute(preview,event=stop)


@unittest.skipUnless(available(),'Darwin source effects unavailable')
class WorkerTests(WorkerFixture,unittest.TestCase):
    def test_prepare_is_read_only_for_target_and_result_acceptance(self):
        self.source_result();original=(self.root/'report.md').read_bytes();preview=self.prepare()
        self.assertEqual(original,(self.root/'report.md').read_bytes());self.assertEqual('review',self.source.view('source')['state'])
        self.assertEqual(['report.md'],preview['files']);self.assertIsNone(self.store.head(PENDING))
        self.assertFalse((self.authority/'effects').exists())

    def test_apply_and_source_acceptance_complete_atomically(self):
        self.source_result();result=self.execute()
        self.assertEqual('completed',result['state']);self.assertEqual(b'worker result\n',(self.root/'report.md').read_bytes())
        self.assertEqual('completed',self.source.view('source')['state']);self.assertIsNone(self.store.head(PENDING))
        head=self.source._head('source')[1];decision=self.source._object(link(head,'decision'))
        self.assertIsNotNone(link(decision,'authorization'))
        self.assertEqual(b'synthetic report\n',(self.authority/'effects/apply-report/000000.original').read_bytes())

    def test_preaccepted_source_decision_remains_the_same(self):
        review=self.source_result();self.source.accept(operation='human-accept',work='source',receipt=review['receipt'],statement='원본 결과 수락')
        before=self.store.head(work_key('source'));self.execute()
        self.assertEqual(before,self.store.head(work_key('source')));self.assertEqual('completed',self.worker.view('apply-report')['state'])

    def test_unrelated_destination_drift_refuses_before_reservation(self):
        self.source_result();(self.root/'unrelated').write_bytes(b'keep')
        with self.assertRaisesRegex(RecordError,'worker-destination-baseline-changed'):self.prepare()
        self.assertIsNone(self.store.head(PENDING));self.assertIsNone(self.store.head(application_key('apply-report')))
        self.assertEqual(b'synthetic report\n',(self.root/'report.md').read_bytes())

    def test_unbound_linked_worktree_can_pause_before_worker_binding(self):
        from colvia import work_lifecycle as lc
        self.source_result()
        def decide(action,operation):
            args=(self.source,'source',action,'review later','','')
            return lc.apply(*args,lc.proposal(*args)[0]['receipt'],operation)
        self.assertEqual('paused',decide('pause','pause-source')['state'])
        self.assertEqual('review',decide('resume','resume-source')['state'])
        self.prepare()
        with self.assertRaisesRegex(RecordError,'lifecycle-application-prepared'):
            decide('pause','pause-bound')

    def test_paused_destination_still_blocks_worker_application(self):
        from colvia import work_lifecycle
        self.start(scope=('elsewhere.md',))
        args=(self.service,'report','pause','return later','','')
        work_lifecycle.apply(*args,work_lifecycle.proposal(*args)[0]['receipt'],'pause-other')
        self.source_result()
        with self.assertRaisesRegex(RecordError,'worker-destination-has-active-work'):
            self.prepare()

    def test_destination_active_work_refuses_before_application(self):
        self.source_result();p=self.service.plan(operation='dest-plan',work='dest',title='다른 일',goal='대상 폴더 편집',scope=['other'],checks=['확인'])
        self.service.approve(operation='dest-approve',work='dest',receipt=p['receipt'],statement='진행')
        with self.assertRaisesRegex(RecordError,'worker-destination-has-active-work'):self.prepare()
        self.assertIsNone(self.store.head(PENDING))

    def test_source_selection_changes_invalidate_preview(self):
        review=self.source_result();preview=self.prepare()
        self.source.accept(operation='accept-source',work='source',receipt=review['receipt'],statement='수락')
        with self.assertRaisesRegex(RecordError,'worker-source-selection-changed'):self.execute(preview)
        self.assertIsNone(self.store.head(PENDING));self.assertEqual(b'synthetic report\n',(self.root/'report.md').read_bytes())

    def test_reserved_then_cancel_preserves_source_review(self):
        self.source_result();self.interrupt()
        self.assertIsNotNone(self.store.head(PENDING));result=self.worker.cancel(operation='cancel',application='apply-report')
        self.assertEqual('cancelled',result['state']);self.assertIsNone(self.store.head(PENDING))
        self.assertEqual('review',self.source.view('source')['state']);self.assertEqual(b'synthetic report\n',(self.root/'report.md').read_bytes())

    def test_evacuation_interruption_resumes_exact_request(self):
        self.source_result();self.interrupt('after-evacuate')
        self.assertFalse((self.root/'report.md').exists());self.assertEqual('review',self.source.view('source')['state'])
        with self.assertRaisesRegex(RecordError,'worker-cancel-requires-all-pre'):self.worker.cancel(operation='bad-cancel',application='apply-report')
        self.assertIsNotNone(self.store.head(PENDING))
        self.worker.resume(operation='resume',application='apply-report')
        self.assertEqual(b'worker result\n',(self.root/'report.md').read_bytes());self.assertEqual('completed',self.source.view('source')['state'])

    def test_installed_bytes_before_completion_are_not_yet_acceptance(self):
        self.source_result();self.interrupt('before-completion')
        self.assertEqual(b'worker result\n',(self.root/'report.md').read_bytes());self.assertEqual('review',self.source.view('source')['state'])
        self.assertIsNotNone(self.store.head(PENDING));self.worker.resume(operation='resume',application='apply-report')
        self.assertEqual('completed',self.source.view('source')['state'])

    def test_outside_drift_keeps_barrier_until_explicit_prerequisite_restoration(self):
        self.source_result();self.interrupt();(self.root/'extra').write_text('external edit')
        with self.assertRaisesRegex(RecordError,'worker-outside-scope-change'):self.worker.resume(operation='blocked',application='apply-report')
        self.assertIsNotNone(self.store.head(PENDING));self.assertEqual('review',self.source.view('source')['state'])
        # Explicit synthetic user correction, not automatic product cleanup.
        (self.root/'extra').unlink();self.worker.resume(operation='after-user-correction',application='apply-report')
        self.assertEqual('completed',self.source.view('source')['state'])

    def test_pending_blocks_source_revision_and_grant_revocation(self):
        review=self.source_result();self.worker.grant(operation='grant',work='source',owner='owner',delegate='helper',statement='이 격리 작업의 적용과 수락 위임')
        self.interrupt()
        with self.assertRaisesRegex(RecordError,'external-effect-pending'):
            self.source.revise(operation='revise',work='source',receipt=review['receipt'],statement='수정')
        with self.assertRaisesRegex(RecordError,'external-effect-pending'):
            self.worker.grant(operation='revoke',work='source',owner='owner',delegate='helper',statement='철회',revoke=True)

    def test_exact_delegate_applies_but_other_actor_cannot(self):
        self.source_result();self.worker.grant(operation='grant',work='source',owner='owner',delegate='helper',statement='이 격리 결과의 적용과 수락 위임')
        preview=self.prepare()
        with self.assertRaisesRegex(RecordError,'worker-grant-mismatch'):self.execute(preview,authority='delegated',actor='other')
        self.assertFalse((self.authority/'effects').exists())
        self.execute(preview,authority='delegated',actor='helper');self.assertEqual('completed',self.source.view('source')['state'])
        from colvia import work_dependencies
        outcome = work_dependencies._outcome('source', self.store.root().heads, self.store.load)
        self.assertEqual('accepted', outcome['status'])
        decision = self.source._object(link(self.source._head('source')[1], 'decision'))
        self.assertEqual(link(decision,'authorization').sha256, outcome['authorization'])

    def test_revoked_grant_cannot_be_used(self):
        self.source_result();self.worker.grant(operation='grant',work='source',owner='owner',delegate='helper',statement='위임')
        preview=self.prepare();self.worker.grant(operation='revoke',work='source',owner='owner',delegate='helper',statement='철회',revoke=True)
        with self.assertRaisesRegex(RecordError,'worker-grant-mismatch'):self.execute(preview,authority='delegated',actor='helper')
        self.assertIsNone(self.store.head(PENDING));self.assertFalse((self.authority/'effects').exists())

    def test_delete_and_new_binary_are_exact_retained_transitions(self):
        self.source_result(scope=('report.md','docs/new.bin'),changes={'report.md':None,'docs/new.bin':b'\x00\xff'})
        self.execute();self.assertFalse((self.root/'report.md').exists());self.assertEqual(b'\x00\xff',(self.root/'docs/new.bin').read_bytes())
        self.assertEqual('completed',self.source.view('source')['state'])

    def test_failure_after_terminal_commit_is_queryable_without_second_acceptance(self):
        self.source_result();preview=self.prepare();original=self.store.commit_heads
        def uncertain(**args):
            value=original(**args)
            if args['operation'].endswith('-complete'):raise RuntimeError('response lost after commit')
            return value
        self.store.commit_heads=uncertain
        with self.assertRaisesRegex(RuntimeError,'response lost'):self.execute(preview)
        self.store.commit_heads=original
        self.assertEqual('completed',self.worker.view('apply-report')['state'])
        self.assertEqual('completed',self.source.view('source')['state']);self.assertIsNone(self.store.head(PENDING))
        self.assertIsNotNone(self.store.operation_result('execute-complete'))
        root=self.store.root().ref
        with self.assertRaisesRegex(RecordError,'worker-pending-application-required'):
            self.worker.resume(operation='no-duplicate',application='apply-report')
        self.assertEqual(root,self.store.root().ref)

    def test_concurrent_target_creation_leaves_pending_and_all_bytes(self):
        self.source_result()
        def race(stage):
            if stage=='before-install':(self.root/'report.md').write_text('external occupant')
        with self.assertRaisesRegex(RecordError,'effect-destination-occupied'):self.execute(event=race)
        self.assertEqual('external occupant',(self.root/'report.md').read_text())
        self.assertEqual(b'synthetic report\n',(self.authority/'effects/apply-report/000000.original').read_bytes())
        self.assertEqual(b'worker result\n',(self.authority/'effects/apply-report/000000.post').read_bytes())
        self.assertIsNotNone(self.store.head(PENDING));self.assertEqual('review',self.source.view('source')['state'])

    def test_source_files_change_after_reservation_uses_only_reserved_result(self):
        self.source_result();self.interrupt();(self.child/'report.md').write_text('later source edit')
        effect=self.source._object(self.store.head(PENDING));binding=self.source._object(link(effect,'binding'))
        self.worker.resume(operation='source-drift',application='apply-report')
        self.assertEqual(b'worker result\n',(self.root/'report.md').read_bytes());self.assertIsNone(self.store.head(PENDING))
        self.assertEqual('later source edit',(self.child/'report.md').read_text())
        decision=self.source._object(link(self.source._head('source')[1],'decision'))
        self.assertEqual(link(binding,'result'),link(decision,'result'))
        self.assertEqual(link(effect,'authorization'),link(decision,'authorization'))

    def test_staged_post_loss_and_external_source_edit_do_not_prevent_safe_cancel(self):
        self.source_result();self.interrupt()
        (self.authority/'effects/apply-report/000000.post').unlink()
        (self.child/'report.md').write_text('new source edit')
        self.worker.cancel(operation='cancel-safe-preimages',application='apply-report')
        self.assertIsNone(self.store.head(PENDING));self.assertEqual('review',self.source.view('source')['state'])
        self.assertEqual(b'synthetic report\n',(self.root/'report.md').read_bytes())

    def test_sync_failure_after_effect_stays_unknown_until_explicit_resume(self):
        from unittest.mock import patch
        import colvia.platforms.darwin_effects as effects
        self.source_result();preview=self.prepare();original=effects._flush;calls=[0]
        def fail_after_staging(fd):
            calls[0]+=1
            if calls[0]==2:raise OSError('synthetic sync failure')
            return original(fd)
        with patch.object(effects,'_flush',side_effect=fail_after_staging):
            with self.assertRaisesRegex(RecordError,'effect-outcome-unknown'):self.execute(preview)
        self.assertIsNotNone(self.store.head(PENDING));self.assertEqual('review',self.source.view('source')['state'])
        self.assertEqual(b'synthetic report\n',(self.authority/'effects/apply-report/000000.original').read_bytes())
        self.worker.resume(operation='after-sync-diagnosis',application='apply-report')
        self.assertEqual('completed',self.source.view('source')['state'])

    def test_progress_and_terminal_records_share_one_manifest(self):
        self.source_result(scope=('report.md','other.md'),changes={'report.md':b'changed','other.md':b'second'})
        self.execute();ref=self.store.head(application_key('apply-report'));manifests=set();effects=[]
        while ref is not None:
            obj=self.source._object(ref);effects.append(obj);manifests.add(link(obj,'manifest'));ref=link(obj,'previous')
        self.assertEqual(4,len(effects));self.assertEqual(1,len(manifests))
        self.assertTrue(all('manifest' not in obj.payload and obj.ref.byte_length<4096 for obj in effects))

    def test_no_content_change_can_complete_without_file_effect(self):
        self.source_result(changes={'report.md':b'synthetic report\n'});self.execute()
        self.assertEqual('completed',self.source.view('source')['state']);self.assertEqual([],list((self.authority/'effects/apply-report').iterdir()))

    def test_worker_application_leaves_git_refs_and_both_indexes_untouched(self):
        self.source_result();source_top=self.git.topology(self.child)
        paths=[self.root/'.git/HEAD',self.root/'.git/index',Path(source_top.gitdir.path)/'HEAD',Path(source_top.gitdir.path)/'index']
        paths.extend(p for p in (self.root/'.git/refs').rglob('*') if p.is_file())
        before={p:p.read_bytes() for p in paths};self.execute()
        self.assertEqual(before,{p:p.read_bytes() for p in paths})

    def test_same_common_config_origin_is_canonical_across_workspaces(self):
        _,source=self.source.workspace.observe();_,destination=self.destination.observe()
        self.assertEqual(source.policy,destination.policy)
        self.assertTrue(all(not origin.startswith('file:.') for origin,_ in source.policy.config))

    def test_real_worktree_policy_override_is_still_refused(self):
        self.command('config','extensions.worktreeConfig','true')
        self.command('config','--worktree','core.filemode','false',root=self.child)
        self.source_result()
        with self.assertRaisesRegex(RecordError,'worker-policy-context-mismatch'):self.prepare()
        self.assertIsNone(self.store.head(PENDING))

    def test_unsupported_port_refuses_before_any_application_record(self):
        self.source_result()
        def unavailable(*args):raise RecordError('effect-writer-unavailable')
        service=WorkerService(self.source,self.destination,authority=self.authority,port_factory=unavailable)
        root=self.store.root().ref
        with self.assertRaisesRegex(RecordError,'effect-writer-unavailable'):service.prepare(operation='no-port',application='none',work='source')
        self.assertEqual(root,self.store.root().ref);self.assertIsNone(self.store.head(PENDING))

if __name__=='__main__':unittest.main()
