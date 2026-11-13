import contextlib,hashlib,io,json,unittest
from pathlib import Path
from unittest.mock import patch
from colvia.codec import canonical_bytes,RecordError
from colvia.manager_entry import main,parser,run,finish,update_configuration
import test_foundation_managed_entry as managed_fixture

class ManagerEntryTests(unittest.TestCase):
    slot=managed_fixture.ManagedEntryTests.slot
    setUp=managed_fixture.ManagedEntryTests.setUp
    tearDown=managed_fixture.ManagedEntryTests.tearDown
    def call(self,*args):
        prefix=['--management-root',str(self.home.root),'--runtime-slot','one','--runtime-manifest-sha256',self.one['manifest_sha256'],'--json']
        stream=io.StringIO()
        with patch('colvia.managed_entry.process_runtime',return_value=self.runtime),contextlib.redirect_stdout(stream):code=main(prefix+list(args))
        self.assertEqual(0,code,stream.getvalue());return json.loads(stream.getvalue())
    def entry_binary(self):
        (self.home.root/'bin').mkdir(mode=0o700);raw=b'synthetic entry; never executed'
        path=self.home.root/'bin/colvia';path.write_bytes(raw);path.chmod(0o700)
        (self.home.root/'entry.json').write_bytes(canonical_bytes(dict(version=1,sha256=hashlib.sha256(raw).hexdigest(),os='macos',architecture='arm64')))
    def test_status_requires_same_dedicated_runtime(self):
        result=self.call('status');self.assertEqual(1,result['projects']);self.assertEqual('ready',result['state'])
    def test_connect_and_detach_complete_distinct_steps_under_single_decision(self):
        self.entry_binary();root=self.base/'new';root.mkdir();(root/'AGENTS.md').write_bytes(b'User rules\n')
        preview=self.call('connect-preview',str(root));plan=self.base/'plan.json';plan.write_bytes(canonical_bytes(preview))
        result=self.call('connect','--plan',str(plan),'--receipt',preview['receipt'],'--statement','적용','--operation','add')
        self.assertEqual('connected',result['state']);self.assertTrue((root/'.colvia-link.json').exists())
        project=preview['plan']['project'];preview=self.call('detach-preview',project,str(root))
        result=self.call('detach',project,str(root),'--receipt',preview['receipt'],'--statement','해제','--operation','remove')
        self.assertEqual('detached',result['state']);self.assertEqual(b'User rules\n',(root/'AGENTS.md').read_bytes())
        self.assertFalse((root/'colvia').exists());self.assertFalse((root/'.colvia-link.json').exists())
        self.assertEqual('detached',self.call('detach-resume','remove')['state'])
        self.assertIn(project,self.home.projects())
    def test_bootstrap_resume_is_explicit_and_passes_only_fixed_inputs(self):
        stream=io.StringIO()
        with patch('colvia.updates.installation.bootstrap',return_value={'state':'installed'}) as resume,contextlib.redirect_stdout(stream):
            self.assertEqual(0,main(['bootstrap-resume-install','--management-root',str(self.home.root),
                '--bootstrap-stage',str(self.base/'verified-stage'),'--bootstrap-manifest-sha256','0'*64,'--operation','first']))
        resume.assert_called_once_with(self.home.root,self.base/'verified-stage','0'*64,resume_operation='first',repair_operation=None)

    def test_new_recovery_commands_pass_exact_bound_inputs(self):
        cases=[('bootstrap-quarantine-preview',['--operation','first'],{'quarantine_operation':'first','quarantine_receipt':None}),
            ('bootstrap-replace-install',['--operation','first','--receipt','c'*64],{'quarantine_operation':'first','quarantine_receipt':'c'*64}),
            ('bootstrap-install-status',[],{'inspect_initial':True}),('bootstrap-retry-install',['--operation','first'],{'retry_operation':'first'}),
            ('bootstrap-refresh-install',['--operation','first','--receipt','a'*64,'--renewal','fresh'],{'refresh_operation':'first','refresh_receipt':'a'*64,'renewal':'fresh'}),
            ('bootstrap-rollback',['--operation','update','--receipt','a'*64,'--rollback-receipt','b'*64],{'rollback_operation':'update','release_receipt':'a'*64,'rollback_receipt':'b'*64})]
        for command,extra,expected in cases:
            with patch('colvia.updates.installation.bootstrap',return_value={'state':'synthetic'}) as recovery,contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(0,main([command,'--management-root',str(self.home.root),'--bootstrap-stage',str(self.base/'stage'),
                    '--bootstrap-manifest-sha256','0'*64,*extra]))
            self.assertEqual({**expected,'resume_operation':None,'repair_operation':None},recovery.call_args.kwargs)

    def test_bootstrap_repair_resume_is_explicit(self):
        with patch('colvia.updates.installation.bootstrap',return_value={'state':'updated'}) as repair,contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(0,main(['bootstrap-resume-repair','--management-root',str(self.home.root),
                '--bootstrap-stage',str(self.base/'verified-stage'),'--bootstrap-manifest-sha256','0'*64,'--operation','repair']))
        self.assertTrue(repair.call_args.kwargs['repair_resume']);self.assertEqual('repair',repair.call_args.kwargs['repair_operation'])
    def test_failed_update_reports_operation_in_machine_output(self):
        prefix=['--management-root',str(self.home.root),'--runtime-slot','one','--runtime-manifest-sha256',self.one['manifest_sha256'],'--json']
        stream=io.StringIO()
        with patch('colvia.managed_entry.process_runtime',return_value=self.runtime),patch('colvia.manager_entry.run',side_effect=RecordError('synthetic-interruption')),contextlib.redirect_stdout(stream):
            self.assertEqual(2,main(prefix+['update']))
        result=json.loads(stream.getvalue());self.assertTrue(result['operation'].startswith('update-'));self.assertEqual('synthetic-interruption',result['error'])
    def test_bootstrap_repair_does_not_request_reconnection(self):
        stream=io.StringIO()
        with patch('colvia.updates.installation.bootstrap',return_value={'state':'updated'}) as repair,contextlib.redirect_stdout(stream):
            self.assertEqual(0,main(['bootstrap-repair-runtime','--management-root',str(self.home.root),
                '--bootstrap-stage',str(self.base/'verified-stage'),'--bootstrap-manifest-sha256','0'*64,'--operation','repair']))
        repair.assert_called_once_with(self.home.root,self.base/'verified-stage','0'*64,resume_operation=None,repair_operation='repair')
        self.assertIn('복구했습니다',stream.getvalue());self.assertNotIn('연결해',stream.getvalue())

    def test_failure_is_not_retried_by_step_loop(self):
        calls=[]
        def fail(operation):calls.append(operation);raise RecordError('synthetic-failure')
        with self.assertRaisesRegex(RecordError,'synthetic-failure'):finish(fail,'one')
        self.assertEqual(['one'],calls)
    def test_project_file_cannot_redirect_update_configuration(self):
        (self.root/'updates.json').write_text('{}')
        with self.assertRaises(FileNotFoundError):update_configuration(self.home)
        (self.home.root/'updates.json').write_bytes(canonical_bytes(dict(version=1,channel='preview',metadata_url='http://bad/',target_url='https://example.invalid/',target='release.zip')))
        with self.assertRaises(RecordError):update_configuration(self.home)

    def test_explicit_update_resume_reuses_receipt_without_preparing_download(self):
        from unittest.mock import MagicMock
        config=dict(channel='preview',metadata_url='https://example.invalid/meta/',target_url='https://example.invalid/targets/',target='release.zip')
        fetcher=MagicMock();release=MagicMock();release.resume.return_value=dict(state='updated')
        with patch('colvia.manager_entry.update_configuration',return_value=config),patch('colvia.manager_entry.https_fetcher',return_value=fetcher),patch('colvia.manager_entry.Trust'),patch('colvia.manager_entry.ReleaseUpdate',return_value=release):
            self.assertEqual('updated',self.call('update-resume','old-attempt','--receipt','exact-receipt')['state'])
        release.prepare.assert_not_called();release.resume.assert_called_once_with(operation='old-attempt',receipt='exact-receipt');fetcher.close.assert_called_once()

    def test_rollback_routing_does_not_open_trust_or_fetcher(self):
        from unittest.mock import MagicMock
        config=dict(channel='preview');release=MagicMock();release.rollback_preview.return_value=dict(state='rollback-review')
        with patch('colvia.manager_entry.update_configuration',return_value=config),patch('colvia.manager_entry.https_fetcher') as fetch,patch('colvia.manager_entry.Trust') as trust,patch('colvia.manager_entry.ReleaseUpdate',return_value=release):
            self.assertEqual('rollback-review',self.call('update-rollback-preview','operation','--receipt','receipt')['state'])
        fetch.assert_not_called();trust.assert_not_called()

    def test_receiver_source_and_explicit_registration_routing(self):
        from unittest.mock import MagicMock
        port=MagicMock();port.change.return_value=dict(state='enabled');port.identity.return_value=dict(app='synthetic.app',cls='{synthetic}')
        with patch('colvia.notice_manager.receiver',return_value=port):
            self.assertEqual('enabled',self.call('notice-enable')['state'])
            self.assertEqual('synthetic.app',self.call('--receiver-source',str(self.base/'retained.exe'),'notice-identity')['app'])
        port.change.assert_called_once_with(enable=True);port.identity.assert_called_once_with(self.base/'retained.exe')

    def test_os_failure_reports_numbers_without_private_exception_text(self):
        prefix=['--management-root',str(self.home.root),'--runtime-slot','one','--runtime-manifest-sha256',self.one['manifest_sha256'],'--json']
        error=OSError(22,'private path must not appear');error.winerror=87
        stream=io.StringIO()
        with patch('colvia.managed_entry.process_runtime',return_value=self.runtime),patch('colvia.manager_entry.run',side_effect=error),contextlib.redirect_stdout(stream):
            self.assertEqual(2,main(prefix+['status']))
        value=json.loads(stream.getvalue());self.assertEqual({'errno':22,'winerror':87},value['diagnostic'])
        self.assertNotIn('private path',stream.getvalue())

    def test_space_failure_reports_bytes_and_operation(self):
        from colvia.updates.space import SpaceError
        error=SpaceError('update-space-insufficient',self.base,'target-download',required=100,available=99)
        stream=io.StringIO()
        prefix=['--management-root',str(self.home.root),'--runtime-slot','one',
                '--runtime-manifest-sha256',self.one['manifest_sha256'],'--json']
        with patch('colvia.managed_entry.process_runtime',return_value=self.runtime), \
             patch('colvia.manager_entry.run',side_effect=error),contextlib.redirect_stdout(stream):
            self.assertEqual(2,main(prefix+['update','--operation','low-space']))
        result=json.loads(stream.getvalue())
        self.assertEqual('low-space',result['operation'])
        self.assertEqual('update-space-insufficient',result['error'])
        self.assertEqual({'phase':'target-download','volume':self.base.anchor,
                          'required_bytes':100,'available_bytes':99},result['diagnostic'])
        self.assertIn('필요 100바이트',result['message'])
        self.assertNotIn(str(self.base),stream.getvalue())

if __name__=='__main__':unittest.main()
