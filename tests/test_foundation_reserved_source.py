"""Reservation-time source agreement; retained-result recovery, not new consent."""
import io,json,unittest
from contextlib import redirect_stdout
from unittest.mock import patch,Mock
from colvia.codec import RecordError
from colvia.effects import PENDING
from colvia.records import link
from colvia.platforms.exclusive import available
from colvia.storage.sqlite import ValidationView
from colvia.work import work_key
from colvia.connection import workspace_key
from colvia.worker import grant_key
from test_foundation_worker import WorkerFixture

@unittest.skipUnless(available(),'Darwin source effects unavailable')
class ReservedSourceTests(WorkerFixture,unittest.TestCase):
    def test_changed_source_before_execute_refuses_without_staging(self):
        self.source_result();preview=self.prepare();(self.child/'report.md').write_bytes(b'new unreviewed')
        with self.assertRaisesRegex(RecordError,'worker-source-files-changed'):self.execute(preview)
        self.assertIsNone(self.store.head(PENDING));self.assertFalse((self.authority/'effects').exists())
        self.assertEqual(b'synthetic report\n',(self.root/'report.md').read_bytes())

    def test_removed_source_before_execute_refuses_without_staging(self):
        self.source_result();preview=self.prepare();self.command('worktree','remove','--force',str(self.child))
        with self.assertRaises(FileNotFoundError):self.execute(preview)
        self.assertIsNone(self.store.head(PENDING));self.assertFalse((self.authority/'effects').exists())

    def test_source_change_during_prepare_refuses_reservation_preserves_stage(self):
        from colvia.platforms.effects_port import effects
        self.source_result();preview=self.prepare();port=effects(self.destination.root,self.authority);prepare=port.prepare
        def change(*args,**kw):
            result=prepare(*args,**kw);(self.child/'report.md').write_bytes(b'changed between checks');return result
        with patch.object(self.worker,'port_factory',return_value=port),patch.object(port,'prepare',side_effect=change):
            with self.assertRaisesRegex(RecordError,'worker-source-files-changed'):self.execute(preview)
        self.assertIsNone(self.store.head(PENDING));self.assertTrue((self.authority/'effects/apply-report/000000.post').is_file())
        self.assertEqual(b'synthetic report\n',(self.root/'report.md').read_bytes())

    def test_recreated_source_path_never_replaces_reserved_result(self):
        self.source_result();self.interrupt();self.command('worktree','remove','--force',str(self.child))
        self.child.mkdir();(self.child/'report.md').write_bytes(b'foreign replacement')
        self.assertIsNone(self.worker.view('apply-report')['blocked'])
        self.worker.resume(operation='recreated-source',application='apply-report')
        self.assertEqual(b'worker result\n',(self.root/'report.md').read_bytes())
        self.assertEqual(b'foreign replacement',(self.child/'report.md').read_bytes())
        self.assertEqual('completed',self.source._head('source')[1].payload['phase'])

    def test_injected_source_and_registration_heads_still_refuse(self):
        self.source_result();self.interrupt();pending=self.store.head(PENDING);head=ValidationView.head
        for key in (work_key('source'),workspace_key(self.child_id),workspace_key(self.destination.workspace)):
            def changed(view,name):return None if name==key else head(view,name)
            with self.subTest(key=key),patch.object(ValidationView,'head',changed):
                with self.assertRaisesRegex(RecordError,'worker-source-selection-changed|worker-connection-changed'):
                    self.worker.resume(operation='head-change',application='apply-report')
            self.assertEqual(pending,self.store.head(PENDING));self.assertEqual('review',self.source._head('source')[1].payload['phase'])
            self.assertEqual(b'synthetic report\n',(self.root/'report.md').read_bytes())

    def test_injected_live_grant_change_refuses_without_acceptance(self):
        self.source_result();self.worker.grant(operation='grant',work='source',owner='owner',delegate='helper',statement='exact result')
        def stop(stage):
            if stage=='reserved':raise RuntimeError('stop')
        with self.assertRaises(RuntimeError):self.execute(actor='helper',authority='delegated',event=stop)
        original=ValidationView.head;pending=self.store.head(PENDING)
        def changed(view,key):return None if key==grant_key('source') else original(view,key)
        with patch.object(ValidationView,'head',changed),self.assertRaisesRegex(RecordError,'worker-grant-changed'):
            self.worker.resume(operation='changed-grant',application='apply-report')
        self.assertEqual(pending,self.store.head(PENDING));self.assertEqual('review',self.source._head('source')[1].payload['phase'])

    def test_staged_post_corruption_stays_pending(self):
        self.source_result();self.interrupt();(self.authority/'effects/apply-report/000000.post').write_bytes(b'corrupt')
        with self.assertRaisesRegex(RecordError,'effect-staged-file-changed'):self.worker.resume(operation='corrupt-post',application='apply-report')
        self.assertIsNotNone(self.store.head(PENDING));self.assertEqual('review',self.source._head('source')[1].payload['phase'])
        self.assertEqual(b'synthetic report\n',(self.root/'report.md').read_bytes())

    def test_retained_record_corruption_stays_pending(self):
        self.source_result();self.interrupt();effect=self.source._object(self.store.head(PENDING))
        binding=self.source._object(link(effect,'binding'));bad=link(binding,'result');load=self.store.load
        def corrupt(ref):return b'corrupt retained object' if ref==bad else load(ref)
        with patch.object(self.store,'load',side_effect=corrupt),self.assertRaisesRegex(RecordError,'object-identity-mismatch'):
            self.worker.resume(operation='corrupt-record',application='apply-report')
        self.assertIsNotNone(self.store.head(PENDING));self.assertEqual('review',self.source._head('source')[1].payload['phase'])

    def test_import_activation_gate_refuses_real_reserved_effect(self):
        from colvia.restore_manager import RestoreManager
        self.source_result();self.interrupt();pending=self.store.head(PENDING)
        with self.assertRaisesRegex(RecordError,'imported-effect-inspection-only'):
            RestoreManager._target(dict(target_root=self.store.root().ref.as_dict()),self.store)
        self.assertEqual(pending,self.store.head(PENDING));self.assertEqual('review',self.source._head('source')[1].payload['phase'])

    def test_destination_verification_remains_required_after_source_removal(self):
        self.source_result();self.interrupt();self.command('worktree','remove','--force',str(self.child))
        with patch.object(self.destination,'verify',side_effect=RecordError('destination-changed')) as verify:
            with self.assertRaisesRegex(RecordError,'destination-changed'):self.worker.resume(operation='bad-destination',application='apply-report')
        verify.assert_called();self.assertIsNotNone(self.store.head(PENDING))

    def test_review_cli_reentry_uses_explicit_authority_and_destination_locator(self):
        from colvia.cli import main,read_locator
        self.source_result();self.interrupt('after-install');self.command('worktree','remove','--force',str(self.child))
        effect=self.source._object(self.store.head(PENDING));wrapper=Mock();wrapper.store.return_value=self.store
        args=['--source-development','--authority',str(self.authority),'--project',self.store.project,
              '--workspace',self.child_id,'--root',str(self.child),'--git',str(self.git.executable),'--json',
              '--operation','cli-review-resume','worker','--destination',self.destination.workspace,'resume','apply-report']
        with patch('colvia.cli.Authority',return_value=wrapper) as authority,patch('colvia.cli.Git',return_value=self.git) as git,patch('colvia.cli.read_locator',wraps=read_locator) as locator,patch.object(self.store,'close'),redirect_stdout(io.StringIO()) as output:
            result=main(args)
        authority.assert_called_once_with(self.authority,project=self.store.project)
        git.assert_called_once_with(self.git.executable)
        self.assertTrue(locator.call_args_list);self.assertTrue(all(call.args==(str(self.root),self.git) or call.args==(self.root,self.git) for call in locator.call_args_list))
        self.assertEqual(0,result,output.getvalue());self.assertEqual('completed',json.loads(output.getvalue())['state'])
        decision=self.source._object(link(self.source._head('source')[1],'decision'))
        self.assertEqual(link(effect,'authorization'),link(decision,'authorization'));self.assertIsNone(self.store.head(PENDING))

    def test_composition_child_completes_after_reserved_source_removal(self):
        from colvia.composition import CompositionService
        for name,path in (('parent','integration.md'),('source','report.md')):
            self.source.plan(operation='plan-'+name,work=name,title=name,goal='result',scope=[path],checks=['check'])
        CompositionService(self.source).declare(operation='declare',parent='parent',children=['source'],document='integration.md',checks=['check'],statement='compose')
        self.source.approve(operation='approve-child',work='source',receipt=self.source.plan_review('source')['receipt'],statement='go')
        self.source.start(operation='start-child',work='source');(self.child/'report.md').write_bytes(b'child result')
        self.source.submit(operation='submit-child',work='source',summary='result',checks=[dict(name='check',status='passed',detail='checked')])
        self.interrupt('after-evacuate');self.command('worktree','remove','--force',str(self.child))
        self.worker.resume(operation='resume-child',application='apply-report')
        self.assertEqual('completed',self.source._head('source')[1].payload['phase'])
        self.assertEqual('planned',self.source._head('parent')[1].payload['phase'])
        self.assertEqual(b'child result',(self.root/'report.md').read_bytes())

    def test_dependencies_rechecked_at_terminal_publication(self):
        original=ValidationView.head
        for i,kind in enumerate(('registration','grant','destination')):
            with self.subTest(kind=kind):
                if i:self.tearDown();self.setUp()
                self.source_result();self.worker.grant(operation='grant',work='source',owner='owner',delegate='helper',statement='exact result')
                ready=False;destination_verify=self.destination.verify
                def checkpoint(stage):
                    nonlocal ready
                    if stage=='before-completion':ready=True
                def changed(view,key):
                    selected=workspace_key(self.child_id) if kind=='registration' else grant_key('source')
                    return None if ready and kind!='destination' and key==selected else original(view,key)
                def verify():
                    if ready and kind=='destination':raise RecordError('terminal-destination-changed')
                    return destination_verify()
                expected={'registration':'workspace-location-index-mismatch','grant':'worker-grant-changed','destination':'terminal-destination-changed'}[kind]
                with patch.object(ValidationView,'head',changed),patch.object(self.destination,'verify',side_effect=verify):
                    with self.assertRaisesRegex(RecordError,expected):self.execute(actor='helper',authority='delegated',event=checkpoint)
                self.assertTrue(ready);self.assertIsNotNone(self.store.head(PENDING))
                self.assertEqual('review',self.source._head('source')[1].payload['phase'])
                self.assertEqual(b'worker result\n',(self.root/'report.md').read_bytes())

    def test_source_folder_loss_with_stale_git_metadata_stays_pending(self):
        self.source_result();self.interrupt('after-evacuate')
        # Preserve the fixture contents outside the registered name, without
        # pruning Git metadata: the same stale-registration case as folder loss.
        self.child.rename(self.home/'retained-source-folder')
        with self.assertRaisesRegex(RecordError,'stale-or-bare-worktree'):
            self.worker.resume(operation='stale-source-registration',application='apply-report')
        self.assertIsNotNone(self.store.head(PENDING));self.assertEqual('review',self.source._head('source')[1].payload['phase'])
        self.assertEqual(b'synthetic report\n',(self.authority/'effects/apply-report/000000.original').read_bytes())
