import contextlib,io,shutil,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from colvia.codec import RecordError,canonical_bytes
from colvia.management import ManagerHome
from colvia.managed_entry import ManagedEntry
from colvia.storage.authority import Authority
from colvia.storage.sqlite import runtime_capabilities
from colvia.binding import Locator,ProjectBinding,WorkspaceRegistration,Topology
from colvia.connection import Connections
from colvia.platforms.posix import location
from colvia.work import WorkService
from colvia.cli import main
import test_foundation_slots as slot_fixture
from test_foundation_binding import P,I,W

class ManagedEntryTests(unittest.TestCase):
    slot=slot_fixture.SlotTests.slot
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='managed-entry-');self.base=Path(self.tmp.name)
        self.home=ManagerHome.create(self.base/'home',os_name='macos',architecture='arm64');self.manager=self.home.slots
        caps=tuple(c for c in runtime_capabilities() if c!='foundation-v1')
        self.one=self.slot('one',1,extra=caps);self.two=self.slot('two',2,extra=caps);self.manager.initialize(self.one)
        self.authority=Authority.create(self.home.root/'authorities'/P,project=P,instance=I,generation='first')
        self.root=self.base/'project';self.root.mkdir();self.locator=Locator(P,I,1,'a'*64,W)
        (self.root/'.colvia-link.json').write_bytes(canonical_bytes(self.locator.payload()))
        topology=Topology('plain',location(self.root));store=self.authority.store()
        try:
            Connections(store).connect(operation='connect',binding=ProjectBinding(self.locator,'plain',topology.root),observed=topology,
                workspace=WorkspaceRegistration(W,topology.root,None),verify_topology=lambda:Topology('plain',location(self.root)))
        finally:store.close()
        self.runtime=(str(self.manager.root/'slots/one/python'),'3.14.7','3.54.0')
        with patch('colvia.managed_entry.process_runtime',return_value=self.runtime):
            self.entry=ManagedEntry(self.home.root,pointer=self.one)
    def tearDown(self):self.tmp.cleanup()
    @contextlib.contextmanager
    def readiness_boundary(self,entry):
        with contextlib.ExitStack() as stack:
            for target in ('colvia.managed_entry.discover','colvia.managed_entry.Git','colvia.cli.read_locator','subprocess.Popen','socket.socket','os.posix_spawn','os.fork','os.execve'):
                stack.enter_context(patch(target,side_effect=AssertionError('readiness side effect: '+target)))
            stack.enter_context(patch.object(entry,'workspace',side_effect=AssertionError('no project open')))
            yield

    def test_unqualified_execution_refuses_before_workspace_or_input_access(self):
        for arguments in (['prepare','run','--request','/unavailable/request'],['start','run','--receipt','unused','--statement','Run']):
            with self.readiness_boundary(self.entry):
                out=io.StringIO()
                with contextlib.redirect_stdout(out):code=main(['--json','execution',*arguments],entry=self.entry)
                self.assertEqual(2,code);self.assertIn('execution-qualified-runtime-required',out.getvalue())
    def test_managed_parser_refuses_abbreviations_and_port_injection(self):
        from colvia.cli import parser
        for args in (['execution','start','run','--rece','unused','--statement','Run'],
                     ['execution','start','run','--receipt','unused','--statement','Run','--factory','arbitrary.module']):
            with contextlib.redirect_stderr(io.StringIO()),self.assertRaises(SystemExit):parser(managed=True).parse_args(args)
    def test_execution_readiness_never_opens_project_or_starts_process(self):
        import json,subprocess,socket,os
        from contextlib import ExitStack
        def snapshot():return {str(p.relative_to(self.home.root)):(p.read_bytes(),p.stat().st_mtime_ns) for p in self.home.root.rglob('*') if p.is_file()}
        before=snapshot()
        with ExitStack() as stack:
            for target in ('colvia.managed_entry.discover','colvia.managed_entry.Git','colvia.cli.read_locator','subprocess.Popen','socket.socket','os.posix_spawn','os.fork','os.execve'):
                stack.enter_context(patch(target,side_effect=AssertionError('readiness must not call '+target)))
            stack.enter_context(patch.object(self.entry,'workspace',side_effect=AssertionError('must not open records')))
            out=io.StringIO()
            with contextlib.redirect_stdout(out):code=main(['--root','/inaccessible-project','--json','execution','readiness'],entry=self.entry)
        self.assertEqual(0,code,out.getvalue());r=json.loads(out.getvalue());self.assertEqual('absent',r['state']);self.assertFalse(r['dispatch_available'])
        self.assertEqual(before,snapshot());self.assertEqual(frozenset(),self.entry.optional_features())

    def test_prepared_assets_keep_managed_execution_disabled_and_corruption_is_explicit(self):
        import hashlib,json
        from colvia.codec import decode_canonical
        from colvia.execution.assets import ASSETS,DESCRIPTOR
        from colvia.platforms.posix import snapshot,ObservationBudget
        target=self.slot('assets',3,extra=tuple(c for c in runtime_capabilities() if c!='foundation-v1'))
        slot=self.manager.root/'slots/assets';resources={}
        for role,(name,_) in ASSETS.items():
            path=slot/name;path.parent.mkdir(exist_ok=True);raw=(role+' fixture').encode();path.write_bytes(raw);path.chmod(0o600)
            resources[role]=dict(path=name,size=len(raw),sha256=hashlib.sha256(raw).hexdigest(),mode='100644')
        (slot/DESCRIPTOR).write_bytes(canonical_bytes(dict(version=1,os='macos',architecture='arm64',resources=resources)))
        manifest=decode_canonical((slot/'manifest.json').read_bytes());manifest['inventory']=[e for e in snapshot(slot,ObservationBudget(100,100000)).entries if e['path']!='manifest.json']
        raw=canonical_bytes(manifest);(slot/'manifest.json').write_bytes(raw);target['manifest_sha256']=hashlib.sha256(raw).hexdigest()
        old,_=self.manager.selection();self.manager.activate(target,expected_selection=old,read_requirements=runtime_capabilities())
        with patch('colvia.managed_entry.process_runtime',return_value=(str(slot/'python'),'3.14.7','3.54.0')):
            entry=ManagedEntry(self.home.root,pointer=target)
        with self.readiness_boundary(entry):
            out=io.StringIO()
            with contextlib.redirect_stdout(out):code=main(['--json','execution','readiness'],entry=entry)
            self.assertEqual(0,code,out.getvalue());self.assertEqual('prepared-dispatch-unavailable',json.loads(out.getvalue())['state'])
            self.assertEqual(frozenset(),entry.optional_features())
            (slot/ASSETS['worker'][0]).unlink()
            out=io.StringIO()
            with contextlib.redirect_stdout(out):code=main(['--json','execution','readiness'],entry=entry)
            self.assertEqual(2,code);self.assertEqual('document-assets-changed',json.loads(out.getvalue())['error'])

    def test_readiness_checks_current_selection_and_manifest(self):
        old,_=self.manager.selection();self.manager.activate(self.two,expected_selection=old,read_requirements=runtime_capabilities())
        with self.assertRaisesRegex(RecordError,'runtime-selection-changed'):self.entry.document_execution_readiness()

    def test_manifest_mismatch_and_deleted_cwd_are_read_only(self):
        import json
        with self.readiness_boundary(self.entry),patch('pathlib.Path.cwd',side_effect=FileNotFoundError('deleted cwd')):
            out=io.StringIO()
            with contextlib.redirect_stdout(out):code=main(['--json','execution','readiness'],entry=self.entry)
            self.assertEqual(0,code,out.getvalue())
        manifest=self.manager.root/'slots/one/manifest.json';manifest.write_bytes(manifest.read_bytes()+b' ')
        with self.assertRaisesRegex(RecordError,'slot-manifest-mismatch'):self.entry.document_execution_readiness()
    def test_unexpected_readiness_failure_does_not_claim_uncertain_write(self):
        import json
        with self.readiness_boundary(self.entry),patch.object(self.entry,'document_execution_readiness',side_effect=KeyError('inventory')):
            out=io.StringIO()
            with contextlib.redirect_stdout(out):code=main(['--json','execution','readiness'],entry=self.entry)
        value=json.loads(out.getvalue());self.assertEqual(2,code);self.assertEqual('document-assets-inspection-failed',value['error'])
        self.assertNotIn('operation',value);self.assertIn('실행이나 기록 변경은 하지 않았습니다',value['message'])

    def test_readiness_os_error_is_not_a_workspace_failure(self):
        import json
        for error,expected in ((OSError('scan failed'),'document-assets-inspection-failed'),(PermissionError('blocked'),'access-denied')):
            with self.subTest(expected=expected),self.readiness_boundary(self.entry),patch.object(self.entry,'document_execution_readiness',side_effect=error):
                out=io.StringIO()
                with contextlib.redirect_stdout(out):code=main(['--json','execution','readiness'],entry=self.entry)
                value=json.loads(out.getvalue());self.assertEqual(2,code);self.assertEqual(expected,value['error']);self.assertNotIn('operation',value)

    def test_mac_candidate_runtime_still_requires_exact_process_tuple(self):
        import hashlib
        from colvia.codec import decode_canonical
        caps=tuple(c for c in runtime_capabilities() if c!='foundation-v1')
        target=self.slot('mac-runtime',3,extra=caps);file=self.manager.root/'slots/mac-runtime/manifest.json'
        m=decode_canonical(file.read_bytes());m.update(python_version='3.14.10',sqlite_version='3.53.1')
        raw=canonical_bytes(m);file.write_bytes(raw);target['manifest_sha256']=hashlib.sha256(raw).hexdigest()
        before,_=self.manager.selection();self.manager.activate(target,expected_selection=before,read_requirements=runtime_capabilities())
        exact=(str(self.manager.root/'slots/mac-runtime/python'),'3.14.10','3.53.1')
        with patch('colvia.managed_entry.process_runtime',return_value=exact):ManagedEntry(self.home.root,pointer=target)
        for actual in ((exact[0],'3.14.7',exact[2]),(exact[0],exact[1],'3.53.2'),('/wrong/python',*exact[1:])):
            with patch('colvia.managed_entry.process_runtime',return_value=actual),self.assertRaisesRegex(RecordError,'dedicated-runtime-mismatch'):
                ManagedEntry(self.home.root,pointer=target)

    def test_guide_needs_no_project_authority_and_missing_payload_is_explicit(self):
        with patch.object(self.entry,'workspace',side_effect=AssertionError('guide must not open records')):
            with patch.object(self.entry,'guide',return_value='Bundled guidance'):
                output=io.StringIO()
                with contextlib.redirect_stdout(output):code=main(['guide'],entry=self.entry)
                self.assertEqual(0,code);self.assertIn('Bundled guidance',output.getvalue())
        with self.assertRaisesRegex(RecordError,'managed-guide-unavailable'):self.entry.guide()
    def test_invalid_topic_stays_out_of_output_and_old_slot_cannot_serve_a_loose_file(self):
        import json
        directory = self.manager.root/'slots/one/adapters/colvia-work'
        directory.mkdir(parents=True)
        (directory/'work.md').write_text('unlisted guide')
        with self.assertRaisesRegex(RecordError, 'managed-guide-unavailable'):
            self.entry.guide('work')
        for bad in (['WORK'], [''], ['../private'], ['--private'], ['work', 'private']):
            for prefix in ([], ['--json']):
                output = io.StringIO()
                with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
                    self.assertEqual(2, main(prefix + ['guide', *bad], entry=self.entry))
                self.assertNotIn('private', output.getvalue())
                self.assertIn('recovery', output.getvalue())
                if prefix:
                    self.assertEqual('invalid-guide-topic', json.loads(output.getvalue())['error'])

    def test_project_launcher_manager_is_bound_without_opening_work_records(self):
        with patch.object(self.entry,'workspace',side_effect=AssertionError('must not open Work records')):
            output=io.StringIO()
            with contextlib.redirect_stdout(output):code=main(['--root',str(self.root),'--json','manage','status'],entry=self.entry)
            self.assertEqual(0,code);self.assertIn('ready',output.getvalue())
            with contextlib.redirect_stdout(io.StringIO()) as help_out,self.assertRaises(SystemExit) as help_exit:
                main(['manage','--help'],entry=self.entry)
            self.assertEqual(0,help_exit.exception.code);self.assertIn('notice-check',help_out.getvalue());self.assertNotIn('--management-root',help_out.getvalue())
            with contextlib.redirect_stderr(io.StringIO()),self.assertRaises(SystemExit):
                main(['manage','--management-root',str(self.base/'foreign'),'status'],entry=self.entry)
    def test_project_notification_resolves_own_project_without_reading_locator_manually(self):
        with patch('colvia.notice_manager.send',return_value=dict(delivery='ready',notification='emitted',accepted=False)) as send:
            with contextlib.redirect_stdout(io.StringIO()):code=main(['--root',str(self.root),'delivery','notify','ready'],entry=self.entry)
            self.assertEqual(0,code);send.assert_called_once_with(self.entry,P,'ready')
    def test_real_process_cannot_claim_fixture_python(self):
        with self.assertRaisesRegex(RecordError,'dedicated-runtime-mismatch'):ManagedEntry(self.home.root,pointer=self.one)
    def test_cli_routes_without_authority_id_or_user_python(self):
        with patch.dict('os.environ',{'PATH':'/not-a-python-path','PYTHONHOME':'/not-a-python-home'}):
            output=io.StringIO()
            with contextlib.redirect_stdout(output):code=main(['--root',str(self.root),'--json','ordinary','list'],entry=self.entry)
            self.assertEqual(0,code,output.getvalue());self.assertNotIn(str(self.home.root),output.getvalue())
    def test_plan_and_accept_use_same_managed_store(self):
        authority,store,workspace=self.entry.workspace(self.root,readonly=False)
        try:
            work=WorkService(store,workspace);plan=work.plan(operation='p',work='report',title='보고서',goal='문의 비교',scope=['report.md'],checks=['원본 보존'])
            work.approve(operation='a',work='report',receipt=plan['receipt'],statement='진행');work.start(operation='s',work='report')
            (self.root/'report.md').write_bytes(b'report')
            review=work.submit(operation='r',work='report',summary='보고서',checks=[dict(name='원본 보존',status='passed',detail='원본 없음')])
            result=work.accept(operation='accept',work='report',receipt=review['receipt'],statement='마무리')
            self.assertEqual('completed',result['state'])
        finally:store.close()
    def test_managed_delivery_submits_with_resolved_authority(self):
        import json,time
        from colvia.delivery.service import DeliveryService
        authority,store,workspace=self.entry.workspace(self.root,readonly=False)
        try:
            work=WorkService(store,workspace)
            p=work.plan(operation='p',work='report',title='보고서',goal='집계',scope=['report.md'],checks=['원본 보존'])
            work.approve(operation='a',work='report',receipt=p['receipt'],statement='진행');work.start(operation='s',work='report')
            (self.root/'report.md').write_text('ready report')
            delivery=DeliveryService(work)
            prepared=delivery.prepare(operation='dp',delivery='ready',work='report',action='submit',deadline_ns=time.time_ns()+600*10**9,
                summary='검토할 보고서',checks=[dict(name='원본 보존',status='passed',detail='합성 원본 없음')])
            delivery.start(operation='ds',delivery='ready',receipt=prepared['receipt'],statement='제출까지 진행')
        finally:store.close()
        output=io.StringIO()
        with contextlib.redirect_stdout(output):code=main(['--root',str(self.root),'--json','delivery','run','ready'],entry=self.entry)
        self.assertEqual(0,code,output.getvalue());self.assertEqual('finished',json.loads(output.getvalue())['state'])
        _,store,workspace=self.entry.workspace(self.root,readonly=True)
        try:self.assertEqual('review',WorkService(store,workspace).view('report')['state'])
        finally:store.close()

    def test_managed_optional_execution_refuses_enabling_but_keeps_history_readable(self):
        import json
        from colvia.configuration import Configuration,enabled
        for action in ('preview','apply'):
            output=io.StringIO();tail=[] if action=='preview' else ['--receipt','unused','--statement','활성화']
            with contextlib.redirect_stdout(output):code=main(['--root',str(self.root),'--json','configuration',action,'--enable','official-execution',*tail],entry=self.entry)
            self.assertEqual(2,code);self.assertEqual('runtime-feature-unavailable',json.loads(output.getvalue())['error'])
        # A retained source API configuration remains readable and can be disabled.
        _,store,_=self.entry.workspace(self.root,readonly=False)
        try:
            config=Configuration(store);p=config.preview(['official-execution'])
            config.apply(operation='source-config',features=['official-execution'],receipt=p['receipt'],statement='합성 과거 설정')
        finally:store.close()
        output=io.StringIO()
        with contextlib.redirect_stdout(output):code=main(['--root',str(self.root),'--json','configuration','show'],entry=self.entry)
        self.assertEqual(0,code);self.assertEqual(['official-execution'],json.loads(output.getvalue())['enabled'])
        output=io.StringIO()
        with contextlib.redirect_stdout(output):code=main(['--root',str(self.root),'--json','configuration','preview'],entry=self.entry)
        self.assertEqual(0,code);receipt=json.loads(output.getvalue())['receipt']
        with contextlib.redirect_stdout(io.StringIO()):code=main(['--root',str(self.root),'configuration','apply','--receipt',receipt,'--statement','실행 비활성화'],entry=self.entry)
        self.assertEqual(0,code)

    def test_managed_worker_refusal_keeps_recovery_in_the_connected_project(self):
        import json
        output=io.StringIO()
        with contextlib.redirect_stdout(output):code=main(['--root',str(self.root),'--json','worker','--destination',W,'view','missing'],entry=self.entry)
        value=json.loads(output.getvalue())
        self.assertEqual(2,code);self.assertNotEqual('command-outcome-unknown',value['error'])
        self.assertEqual('Use the same connected project folder and managed launcher.',value['recovery_context'])
        self.assertNotIn('--authority',value['recovery_command'])

    def test_update_between_launch_and_open_refuses_old_python(self):
        before,_=self.manager.selection();self.manager.activate(self.two,expected_selection=before,read_requirements=runtime_capabilities())
        with self.assertRaisesRegex(RecordError,'runtime-selection-changed'):self.entry.workspace(self.root,readonly=True)
        with patch('colvia.managed_entry.process_runtime',return_value=self.runtime),self.assertRaisesRegex(RecordError,'entry-selection-changed'):
            ManagedEntry(self.home.root,pointer=self.one)
    def test_open_authority_rechecks_exact_launch_pointer(self):
        authority,store,_=self.entry.workspace(self.root,readonly=True);store.close()
        before,_=self.manager.selection();self.manager.activate(self.two,expected_selection=before,read_requirements=runtime_capabilities())
        with self.assertRaisesRegex(RecordError,'entry-selection-changed'):authority.store()
    def test_copied_locator_does_not_show_original_as_current(self):
        copied=self.base/'copy';shutil.copytree(self.root,copied)
        with self.assertRaisesRegex(RecordError,'project-location-changed'):self.entry.workspace(copied,readonly=True)
    def test_ignored_user_tool_environment_is_not_a_git_registration(self):
        (self.root/'.git').mkdir()
        with patch.dict('os.environ',{'GIT_EXEC_PATH':'/untrusted','PATH':'/untrusted'}),self.assertRaisesRegex(RecordError,'git-prerequisite-required'):
            self.entry.workspace(self.root,readonly=True)

if __name__=='__main__':unittest.main()

class ManagedGitEntryTests(unittest.TestCase):
    """Shared authority routing from ordinary/sibling/app-nested workspaces.

    Only process-runtime identity is mocked; Git and project files are real local
    synthetic fixtures. This does not re-run any desktop permission probe.
    """
    from test_foundation_git import GitFixture
    command=GitFixture.command
    slot=slot_fixture.SlotTests.slot
    def setUp(self):
        self.GitFixture.setUp(self)
        self.fixture_home=self.home
        self.management=ManagerHome.create(self.fixture_home/'manager',os_name='macos',architecture='arm64');self.manager=self.management.slots
        caps=tuple(c for c in runtime_capabilities() if c!='foundation-v1');self.one=self.slot('one',1,extra=caps);self.manager.initialize(self.one)
        (self.management.root/'tools.json').write_bytes(canonical_bytes(dict(version=1,git=dict(path=str(self.git.executable),sha256=self.git.sha256,version=self.git.version))))
        import hashlib
        (self.management.root/'bin').mkdir(mode=0o700);raw=b'synthetic entry not executed'
        path=self.management.root/'bin/colvia';path.write_bytes(raw);path.chmod(0o700)
        (self.management.root/'entry.json').write_bytes(canonical_bytes(dict(version=1,os='macos',architecture='arm64',sha256=hashlib.sha256(raw).hexdigest())))
        from colvia.project_setup import ProjectSetup
        setup=ProjectSetup(self.management,self.git);preview=setup.preview(self.root)
        setup.start(operation='connect',plan=preview['plan'],receipt=preview['receipt'],statement='적용')
        for _ in range(4):setup.resume('connect')
        self.project=preview['plan']['project']
        runtime=(str(self.manager.root/'slots/one/python'),'3.14.7','3.54.0')
        with patch('colvia.managed_entry.process_runtime',return_value=runtime):self.entry=ManagedEntry(self.management.root,pointer=self.one)
    def tearDown(self):self.GitFixture.tearDown(self)
    def test_sibling_and_nested_share_history_but_have_distinct_workspace_identity(self):
        roots=[self.root,self.fixture_home/'sibling',self.root/'.claude/worktrees/nested']
        roots[2].parent.mkdir(parents=True)
        self.command('worktree','add','-q','-b','sibling',str(roots[1]));self.command('worktree','add','-q','-b','nested',str(roots[2]))
        identities=[]
        for n,root in enumerate(roots):
            if n:
                with self.assertRaisesRegex(RecordError,'registration-required'):self.entry.workspace(root,readonly=True)
            authority,store,workspace=self.entry.workspace(root,readonly=False)
            try:
                identities.append(workspace.workspace);self.assertEqual(self.project,authority.project)
            finally:store.close()
        # Establish each authorized folder before the parent observes its nested
        # structural boundary. An unregistered nested checkout is never ignored.
        for n,root in enumerate(roots):
            authority,store,workspace=self.entry.workspace(root,readonly=False)
            try:
                service=WorkService(store,workspace)
                p=service.plan(operation='plan'+str(n),work='work'+str(n),title='합성 작업',goal='서로 다른 폴더의 결과',scope=['result.md'],checks=['확인'])
                self.assertEqual('planned',p['state'])
            finally:store.close()
        self.assertEqual(3,len(set(identities)))
        for root in roots:
            authority,store,workspace=self.entry.workspace(root,readonly=True)
            try:
                service=WorkService(store,workspace)
                for n in range(3):self.assertEqual('planned',service.view('work'+str(n))['state'])
            finally:store.close()

    def test_qualified_availability_still_requires_project_opt_in(self):
        import json
        from colvia.configuration import enabled
        with patch('colvia.execution.managed_factory.qualified_release',return_value={}),patch.object(self.entry,'document_execution_readiness',return_value={'assets_verified':True}):
            self.assertEqual(frozenset({'official-execution'}),self.entry.optional_features())
            _,store,_=self.entry.workspace(self.root,readonly=True)
            try:self.assertEqual(frozenset(),enabled(store))
            finally:store.close()
            output=io.StringIO()
            with contextlib.redirect_stdout(output):code=main(['--root',str(self.root),'--json','configuration','preview','--enable','official-execution'],entry=self.entry)
            self.assertEqual(0,code);receipt=json.loads(output.getvalue())['receipt']
            with contextlib.redirect_stdout(io.StringIO()):code=main(['--root',str(self.root),'--json','configuration','apply','--enable','official-execution','--receipt',receipt,'--statement','Enable exact optional feature'],entry=self.entry)
            self.assertEqual(0,code)
    def test_resolution_command_preview_is_readonly_and_apply_is_explicit(self):
        seen=[]
        def resolve(args,store,workspace,authority):
            seen.append((args.action,store.readonly));return dict(state='synthetic-resolution')
        with patch.object(self.entry,'document_resolution',side_effect=resolve):
            for tail in (['resolve-preview','run'],['resolve','run','--receipt','synthetic','--statement','Record unresolved']):
                with contextlib.redirect_stdout(io.StringIO()):code=main(['--root',str(self.root),'--json','execution',*tail],entry=self.entry)
                self.assertEqual(0,code)
        self.assertEqual([('resolve-preview',True),('resolve',False)],seen)

    def test_broken_optional_runtime_does_not_block_show_or_disable(self):
        import json
        from colvia.configuration import Configuration
        _,store,_=self.entry.workspace(self.root,readonly=False)
        try:
            config=Configuration(store);p=config.preview(['official-execution'])
            config.apply(operation='enable-fixture',features=['official-execution'],receipt=p['receipt'],statement='Synthetic enable')
        finally:store.close()
        with patch.object(self.entry,'optional_features',side_effect=OSError('broken runtime')) as unavailable:
            for action in ('show','preview'):
                out=io.StringIO()
                with contextlib.redirect_stdout(out):code=main(['--root',str(self.root),'--json','configuration',action],entry=self.entry)
                self.assertEqual(0,code)
                if action=='preview':receipt=json.loads(out.getvalue())['receipt']
            with contextlib.redirect_stdout(io.StringIO()):code=main(['--root',str(self.root),'--json','configuration','apply','--receipt',receipt,'--statement','Disable'],entry=self.entry)
            self.assertEqual(0,code);unavailable.assert_not_called()
            with contextlib.redirect_stdout(io.StringIO()):code=main(['--root',str(self.root),'--json','configuration','preview','--enable','official-execution'],entry=self.entry)
            self.assertNotEqual(0,code);unavailable.assert_called_once()

    def test_resolution_nonrecord_failure_is_not_input_error(self):
        import json
        for error in (ValueError('decode'),TypeError('runtime')):
            out=io.StringIO()
            with patch.object(self.entry,'document_resolution',side_effect=error),contextlib.redirect_stdout(out):
                code=main(['--root',str(self.root),'--json','execution','resolve','run','--receipt','x','--statement','Resolve'],entry=self.entry)
            self.assertNotEqual(0,code);self.assertEqual('execution-outcome-unknown',json.loads(out.getvalue())['error'])
