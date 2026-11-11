"""Bounded second-result-review recovery counterexamples; synthetic fixtures."""
import os,unittest
from colvia.codec import RecordError
from colvia.effects import PENDING
from colvia.records import link
from colvia.platforms.exclusive import available
from colvia.presentation import human
from test_foundation_worker import WorkerFixture

@unittest.skipUnless(available(),'Darwin source effects unavailable')
class CorrectionTests(WorkerFixture,unittest.TestCase):
    def test_case_variant_policy_transition_refuses_before_effect(self):
        self.source_result(scope=('.GITIGNORE',),changes={'.GITIGNORE':b'ignored/\n'})
        root=self.store.root().ref
        with self.assertRaisesRegex(RecordError,'worker-policy-edit-unsupported'):self.prepare()
        self.assertEqual(root,self.store.root().ref);self.assertIsNone(self.store.head(PENDING))
        self.assertFalse((self.authority/'effects').exists())

    def test_evacuated_original_late_edit_is_preserved_when_resuming(self):
        self.source_result();fd=os.open(self.root/'report.md',os.O_RDWR)
        try:
            self.interrupt('before-install');os.ftruncate(fd,0);os.write(fd,b'late retained edit');os.fsync(fd)
        finally:os.close(fd)
        shown=self.worker.view('apply-report')
        self.assertEqual('evacuated',shown['paths'][0]['state'])
        self.worker.resume(operation='resume-evacuated-edit',application='apply-report')
        self.assertIsNone(self.store.head(PENDING));self.assertEqual(b'worker result\n',(self.root/'report.md').read_bytes())
        self.assertEqual(b'late retained edit',(self.authority/'effects/apply-report/000000.original').read_bytes())
        self.assertIn('추가 편집',human(self.worker.view('apply-report')))

    def test_accepted_source_removed_mid_application_uses_retained_result(self):
        review=self.source_result(scope=('report.md','second.md'),changes={'report.md':b'first','second.md':b'second'})
        self.source.accept(operation='accept-first',work='source',receipt=review['receipt'],statement='accept')
        decision=link(self.source._head('source')[1],'decision')
        self.interrupt('progress-published');self.command('worktree','remove','--force',str(self.child))
        self.worker.resume(operation='resume-without-source',application='apply-report')
        self.assertIsNone(self.store.head(PENDING));self.assertEqual(decision,link(self.source._head('source')[1],'decision'))
        self.assertEqual(b'first',(self.root/'report.md').read_bytes());self.assertEqual(b'second',(self.root/'second.md').read_bytes())

    def test_review_source_removed_mid_application_completes_reserved_result(self):
        self.source_result(scope=('report.md','second.md'),changes={'report.md':b'first','second.md':b'second'})
        self.interrupt('progress-published');self.command('worktree','remove','--force',str(self.child))
        effect=self.source._object(self.store.head(PENDING));binding=self.source._object(link(effect,'binding'))
        shown=self.worker.view('apply-report');self.assertIsNone(shown['blocked'])
        with self.assertRaisesRegex(RecordError,'worker-cancel-requires-all-pre'):
            self.worker.cancel(operation='review-cannot-cancel',application='apply-report')
        self.worker.resume(operation='review-missing-source',application='apply-report')
        self.assertIsNone(self.store.head(PENDING));self.assertEqual('completed',self.source._head('source')[1].payload['phase'])
        decision=self.source._object(link(self.source._head('source')[1],'decision'))
        self.assertEqual(link(binding,'result'),link(decision,'result'));self.assertEqual(link(effect,'authorization'),link(decision,'authorization'))
        self.assertEqual(b'first',(self.root/'report.md').read_bytes());self.assertEqual(b'second',(self.root/'second.md').read_bytes())
        self.assertEqual(b'synthetic report\n',(self.authority/'effects/apply-report/000000.original').read_bytes())

    def test_completed_human_view_reports_retained_edit(self):
        message=human(dict(application='a',state='completed',retained_original_modified=['report.md']))
        self.assertIn('추가 편집',message);self.assertIn('report.md',message)

    def test_cancel_message_describes_present_state_not_no_effect_history(self):
        message=human(dict(application='a',state='cancelled'))
        self.assertNotIn('파일을 적용하지 않고',message);self.assertIn('적용 전',message)

    def test_actual_cli_resume_uses_destination_locator_after_accepted_source_removal(self):
        import io,json
        from unittest.mock import patch,Mock
        from contextlib import redirect_stdout
        from colvia.cli import main
        review=self.source_result();self.source.accept(operation='accept-before-cli',work='source',receipt=review['receipt'],statement='accept')
        self.interrupt('after-install');self.command('worktree','remove','--force',str(self.child))
        wrapper=Mock();wrapper.store.return_value=self.store
        args=['--source-development','--authority',str(self.authority),'--project',self.store.project,
              '--workspace',self.child_id,'--root',str(self.child),'--git',str(self.git.executable),'--json',
              '--operation','cli-resume','worker','--destination',self.destination.workspace,'resume','apply-report']
        with patch('colvia.cli.Authority',return_value=wrapper),patch('colvia.cli.Git',return_value=self.git),patch.object(self.store,'close'),redirect_stdout(io.StringIO()) as output:
            result=main(args)
        self.assertEqual(0,result,output.getvalue());self.assertEqual('completed',json.loads(output.getvalue())['state'])
        self.assertIsNone(self.store.head(PENDING));self.assertEqual(b'worker result\n',(self.root/'report.md').read_bytes())
