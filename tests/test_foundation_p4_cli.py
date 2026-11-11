"""Source-only CLI wiring and concise rendering for composed/worker operations."""
import unittest
from colvia.cli import parser,dispatch
from colvia.presentation import human,failure
from colvia.platforms.exclusive import available
from test_foundation_worker import WorkerFixture
from test_foundation_cli import CLITests


class CompositionProcessTests(unittest.TestCase):
    setUp=CLITests.setUp;tearDown=CLITests.tearDown;call=CLITests.call;plan=CLITests.plan
    def test_process_entry_preserves_roles_without_tokens_in_default_output(self):
        self.plan('parent');self.plan('child')
        declared=self.call('composition','declare','parent','--child','child','--document','parent.md','--check','집계 대조','--statement','하위 결과를 통합하자')
        self.assertEqual('planned',declared['state'])
        value=self.call('composition','rebind-preview','parent');self.assertEqual('child',value['children'][0]['work'])
        shown=self.call('composition','rebind-preview','parent',machine=False)
        for internal in ('receipt','sha256',str(self.home),'SKILL.md'):self.assertNotIn(internal,shown)
        self.assertIn('결과 수락 전',shown)
        rebound=self.call('composition','rebind','parent','--receipt',value['receipt'],'--statement','현재 결과로 새 계획')
        self.assertEqual('planned',rebound['state'])


@unittest.skipUnless(available(),'Darwin source effects unavailable')
class WorkerCommandTests(WorkerFixture,unittest.TestCase):
    def command_args(self,*tail):
        return parser().parse_args(['--source-development','--authority',str(self.authority),'--project',self.store.project,
            '--workspace',self.child_id,'--root',str(self.child),'worker','--destination',self.destination.workspace,*tail])
    def test_dispatch_prepares_and_applies_without_handwritten_scripts(self):
        self.source_result()
        value=dispatch(self.command_args('prepare','apply-report','--work','source'),self.store,self.source.workspace)
        shown=human(value)
        for internal in ('receipt','sha256',str(self.home),'SKILL.md',self.child_id):self.assertNotIn(internal,shown)
        done=dispatch(self.command_args('execute','apply-report','--receipt',value['receipt'],'--statement','이대로 적용하고 수락해'),self.store,self.source.workspace)
        self.assertEqual('completed',done['state']);self.assertLess(len(human(done).splitlines()),3)
        self.assertEqual(b'worker result\n',(self.root/'report.md').read_bytes())
    def test_managed_worker_view_uses_resolved_authority_not_missing_cli_flag(self):
        import contextlib,io,json
        from types import SimpleNamespace
        from colvia.cli import main
        self.source_result();self.prepare()
        entry=SimpleNamespace(workspace=lambda root,readonly:(SimpleNamespace(root=self.authority),self.store,self.source.workspace))
        output=io.StringIO()
        with contextlib.redirect_stdout(output):code=main(['--root',str(self.child),'--json','worker','--destination',self.destination.workspace,'view','apply-report'],entry=entry)
        self.assertEqual(0,code,output.getvalue());self.assertEqual('apply-report',json.loads(output.getvalue())['application'])

    def test_recovery_guidance_does_not_claim_rollback_or_show_internal_paths(self):
        for code in ('effect-path-unknown','effect-destination-occupied','worker-outside-scope-change','worker-cancel-requires-all-pre'):
            text=failure(code);self.assertLess(len(text),180);self.assertNotIn(code,text);self.assertNotIn('/Users/',text)
        text=human(dict(work='source',delegation=True,state='active'))
        self.assertIn('아직 파일을 적용하지 않았습니다',text)

if __name__=='__main__':unittest.main()
