"""Installed lifecycle plus explicit Host unit seams; no model/credential access."""
from pathlib import Path
import copy,hashlib,json,os,shutil,subprocess,sys,tempfile,time,unittest
from unittest import mock
from hv2ref import official_state as state, official_entry as entry, official_host as hostmod, product
from hv2ref.official_documents import EffectJournal
from hv2ref.errors import ContractError, InjectedCrash
from hv2ref.jsonio import canonical_json_bytes

SOURCE=Path(__file__).resolve().parents[1]
TIME='2026-01-01T00:00:00Z'
PREFIX=b'# Guide\n\n';BEFORE=b'Before.\n';AFTER='Approved fact.\n';SUFFIX=b'\nTail.\n'

class OfficialExecutionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory();cls.root=Path(cls.tmp.name).resolve()
        cls.candidate=cls.root/'candidate'
        completed=subprocess.run([sys.executable,'-I','-S','-B',str(SOURCE/'scripts/prepare-official.py'),'--output',str(cls.candidate)],capture_output=True,timeout=45)
        if completed.returncode:raise RuntimeError((completed.stdout+completed.stderr).decode())

    @classmethod
    def tearDownClass(cls):cls.tmp.cleanup()

    def setUp(self):
        self.folder=self.root/self._testMethodName;self.folder.mkdir()
        self.target=self.folder/'project';self.target.mkdir()
        (self.target/'a').write_bytes(PREFIX+BEFORE+SUFFIX)
        (self.target/'b').write_text('# Policy\n\nApproved fact.\n')
        (self.target/'sentinel').write_text('protected synthetic\n')
        packet=product.workspace_init_preview(self.candidate,self.target,authority_home_id='home-a',operation_id='init-a',created_at=TIME)
        product.workspace_init_apply(self.candidate,self.target,packet['request'],confirm_token=packet['confirm_token'])
        seed=subprocess.run([sys.executable,'-I','-S','-B',str(SOURCE/'tests/fixtures/official_fixture.py'),str(self.target)],capture_output=True,timeout=60)
        if seed.returncode:self.fail((seed.stdout+seed.stderr).decode())
        self.runtime=product.verify_workspace_product(self.target)
        self.runtime['inventory_id']=state.WINDOW
        self.binding_patch=mock.patch.object(product,'require_workspace_runtime',return_value=self.runtime)
        self.binding_patch.start();self.addCleanup(self.binding_patch.stop)
        # Offline unit seam only. Installed CLI provenance is tested separately; live admission remains unmodified.
        self.input_patch=mock.patch.object(entry,'runtime_input',return_value={})
        self.input_patch.start();self.addCleanup(self.input_patch.stop)
        runtime=self.folder/'runtime';runtime.mkdir(mode=0o700)
        self.request={'work_id':'official-work','worker_root':str(self.target),'documents':{
            'files':{'Editable':{'path':str(self.target/'a'),'view':{'kind':'replace-range','ranges':[[len(PREFIX),len(PREFIX+BEFORE)]]}},
                     'Reference':{'path':str(self.target/'b'),'view':{'kind':'full'}}},
            'output':'Editable','claims':{'Editable':{'required':['Approved fact.'],'forbidden':['Unapproved'],
                'evidence':[{'file_id':'Reference','quote':'Approved fact.'}]}},'approved_external_links':[]},
            'read_ids':['Editable','Reference'],'prompt':'Read, replace with Approved fact., then verify.',
            'owner_statement':'Synthetic bounded execution authorization','runtime':{},'runtime_root':str(runtime),
            'expires_wall_ns':time.time_ns()+600*10**9,'seconds':90,'worker_limit':5}

    def prepare(self,request=None):return entry.prepare(self.target,request or self.request)
    def new_host(self,request=None):
        value=self.prepare(request);h=hostmod.Host(value['spec'],value['confirm_token']);h.bind('thread','turn');self.addCleanup(h.close);return h
    def envelope(self,call='read',tool='u2_read_file',args=None):
        return {'threadId':'thread','turnId':'turn','callId':call,'tool':tool,'arguments':args or {'file_ids':['Editable','Reference']}}
    def truth(self):
        return {str(p.relative_to(self.target)):p.read_bytes() for p in self.target.rglob('*') if p.is_file() and '.hrn/locks/' not in str(p)}
    def installed(self,*args):
        return subprocess.run([sys.executable,'-I','-B',str(self.target/'colvia'),*args],capture_output=True,timeout=30)

    def test_preview_no_effect_and_binding(self):
        before=self.truth();p=self.prepare()
        self.assertEqual(before,self.truth());self.assertEqual(p['effects'],'none')
        self.assertEqual(p['spec']['work']['product_ref'],self.runtime['binding_ref'])
        self.assertIn('intent_ref',p['spec']['work'])
        self.assertEqual(p['confirm_token'],state.digest(state.canonical(p['spec'])))

    def test_wrong_work_scope_and_expiry_refuse(self):
        for field,value in [('work_id','other'),('worker_limit',2),('expires_wall_ns',1),('seconds',601)]:
            bad=copy.deepcopy(self.request);bad[field]=value
            with self.subTest(field=field),self.assertRaises((ContractError,KeyError)):self.prepare(bad)
        bad=copy.deepcopy(self.request);bad['documents']['files']['Editable']['path']=str(self.target/'sentinel')
        with self.assertRaisesRegex(ContractError,'output-outside-work-scope'):self.prepare(bad)
        self.assertFalse((self.target/'.hrn/executions').exists())

    def test_claims_and_read_order_refuse_before_grant(self):
        bad=copy.deepcopy(self.request);bad['read_ids'].reverse()
        with self.assertRaisesRegex(ContractError,'single-ordered-read-pack'):self.prepare(bad)
        bad=copy.deepcopy(self.request);bad['documents']['claims']['Editable']['evidence'][0]['quote']='missing fact'
        with self.assertRaisesRegex(ContractError,'claim-evidence-missing'):self.prepare(bad)
        self.assertFalse((self.target/'.hrn/executions').exists())

    def test_stale_confirmation_before_capsule(self):
        p=self.prepare();(self.target/'a').write_bytes(PREFIX+b'Changed\n'+SUFFIX)
        with self.assertRaisesRegex(ContractError,'stale-execution-confirmation'):
            entry.execute(self.target,p['spec'],p['confirm_token'])
        self.assertFalse((self.target/'.hrn/executions').exists())

    def test_missing_confirmation_before_capsule(self):
        p=self.prepare()
        with self.assertRaisesRegex(ContractError,'stale-execution-confirmation'):entry.execute(self.target,p['spec'],'wrong')
        self.assertFalse((self.target/'.hrn/executions').exists())

    def test_consumed_grant_and_open_capsule_block_new_prepare(self):
        h=self.new_host()
        with self.assertRaisesRegex(ContractError,'unresolved-execution'):self.prepare()
        h.finish('revoked-before-launch')
        with self.assertRaisesRegex(ContractError,'grant-already-consumed'):self.prepare()

    def test_cancel_request_is_not_stopped_and_callback_refused(self):
        h=self.new_host();before=(self.target/'a').read_bytes()
        result=state.cancel(self.target,h.grant,'stop')
        self.assertTrue(result['cancel_requested']);self.assertFalse(result['effects_stopped'])
        with mock.patch.object(h.controller,'dispatch',side_effect=AssertionError('worker must not run')):
            answer=h.dispatch(self.envelope())
        self.assertFalse(answer['ok']);self.assertFalse(answer['worker_admitted'])
        self.assertEqual(before,(self.target/'a').read_bytes())
        self.assertEqual(state.read_capsule(self.target,h.grant)['status'],'incomplete')

    def test_cancel_marker_immutable_and_malformed_fail_closed(self):
        h=self.new_host();state.cancel(self.target,h.grant,'stop')
        with self.assertRaisesRegex(ContractError,'cancel-request-differs'):state.cancel(self.target,h.grant,'different')
        (h.run/'cancel.json').write_text('{')
        with self.assertRaises(ContractError):state.read_capsule(self.target,h.grant)

    def test_other_thread_and_tool_order_refused(self):
        h=self.new_host();bad=self.envelope();bad['threadId']='other'
        self.assertFalse(h.dispatch(bad)['worker_admitted'])
        self.assertTrue(h.revoked)
        self.assertFalse(h.dispatch(self.envelope('new'))['worker_admitted'])

    def test_duplicate_callback_refused(self):
        h=self.new_host()
        with mock.patch.object(h.controller,'dispatch',return_value={'files':[]}):self.assertTrue(h.dispatch(self.envelope())['ok'])
        result=h.dispatch(self.envelope())
        self.assertFalse(result['ok']);self.assertFalse(result['worker_admitted'])

    def test_admitted_baseexception_preserves_unknown(self):
        h=self.new_host()
        with mock.patch.object(h.controller,'dispatch',side_effect=KeyboardInterrupt),self.assertRaises(KeyboardInterrupt):
            h.dispatch(self.envelope())
        value=state.read_capsule(self.target,h.grant)
        self.assertEqual(value['pending'],'read');self.assertTrue(value['revoked'])
        with self.assertRaisesRegex(ContractError,'terminal-pending-effect'):h.finish('interrupted')

    def test_pending_and_unknown_block_writer(self):
        from hv2ref.workspace import writer_guard
        h=self.new_host();h.fail(RuntimeError('synthetic'))
        with self.assertRaisesRegex(ContractError,'unresolved-execution'):
            with writer_guard(self.target):pass
        with self.assertRaisesRegex(ContractError,'unresolved-execution'):
            product.workspace_detach_preview(self.target,operation_id='detach',created_at=TIME)

    def test_resolution_preserves_grant_documents_and_closes_only_unknown(self):
        h=self.new_host();h.fail(RuntimeError('synthetic'))
        before=(h.run/'grant.json').read_bytes(),(self.target/'a').read_bytes()
        p=state.resolution_preview(self.target,h.grant)
        result=state.resolve(self.target,h.grant,p['confirm_token'])
        self.assertEqual(result['status'],'operator-resolved-unknown')
        self.assertEqual(before,((h.run/'grant.json').read_bytes(),(self.target/'a').read_bytes()))
        self.assertNotEqual(result['head'],p['observation']['journal_head'])
        with self.assertRaisesRegex(ContractError,'resolution-requires'):state.resolution_preview(self.target,h.grant)

    def test_resolution_stale_digest_refused(self):
        h=self.new_host();h.fail(RuntimeError('synthetic'));p=state.resolution_preview(self.target,h.grant)
        (self.target/'a').write_text('changed current bytes\n')
        with self.assertRaisesRegex(ContractError,'stale-resolution'):state.resolve(self.target,h.grant,p['confirm_token'])

    def test_unknown_spawn_gap_cannot_resolve(self):
        h=self.new_host();h.journal.append('runtime-reserved',{'app_server':1});h.fail(RuntimeError('spawn gap'))
        with self.assertRaisesRegex(ContractError,'process-identity-unavailable'):state.resolution_preview(self.target,h.grant)

    def test_expired_status_still_readable(self):
        request=copy.deepcopy(self.request);request['expires_wall_ns']=time.time_ns()+10**9
        h=self.new_host(request)
        with mock.patch.object(time,'time_ns',return_value=request['expires_wall_ns']+1):
            self.assertEqual(state.read_capsule(self.target,h.grant)['status'],'incomplete')
            with self.assertRaisesRegex(ContractError,'authority-expired'):h.authority()

    def test_project_and_reference_drift_refused(self):
        h=self.new_host();(self.target/'sentinel').write_text('changed\n')
        with self.assertRaisesRegex(ContractError,'outside-output-project-drift'):h.authority()

    def test_actual_installed_status_cancel_and_help(self):
        h=self.new_host()
        result=self.installed('run','status','--grant',h.grant)
        self.assertEqual(result.returncode,0,result.stderr.decode()+result.stdout.decode())
        self.assertEqual(json.loads(result.stdout)['status'],'incomplete')
        result=self.installed('run','cancel','--grant',h.grant,'--reason','separate CLI')
        self.assertEqual(result.returncode,0,result.stderr.decode()+result.stdout.decode())
        self.assertTrue(h.cancelled())
        self.assertIn(b'execute',self.installed('run','--help').stdout)

    def test_installed_cli_rejects_irrelevant_action_options(self):
        for args in (('prepare','--grant','0'*64),('prepare','--confirm','0'*64),
                     ('status','--grant','0'*64,'--input','unexpected.json'),
                     ('execute','--confirm','0'*64,'--reason','ignored')):
            with self.subTest(args=args):
                before=self.truth();result=self.installed('run',*args)
                self.assertNotEqual(0,result.returncode)
                self.assertIn(b'HV2-OFFICIAL-OPTIONS',result.stdout+result.stderr)
                self.assertEqual(before,self.truth())

    def test_cancel_is_published_atomically_and_failure_leaves_no_marker(self):
        h=self.new_host();native=state.rename_exclusive;observed=[]
        def inspect(source,destination):
            observed.append(not destination.exists() and state.load(source)['grant']==h.grant)
            return native(source,destination)
        with mock.patch.object(state,'rename_exclusive',side_effect=inspect):state.cancel(self.target,h.grant,'atomic')
        self.assertEqual([True],observed);self.assertTrue(h.cancelled())
        self.assertEqual([],list((self.target/'.hrn/locks').glob('cancel-*.json')))

    def test_cancel_publication_failure_does_not_expose_partial_marker(self):
        h=self.new_host()
        with mock.patch.object(state,'rename_exclusive',side_effect=OSError('synthetic rename failure')),self.assertRaises(OSError):
            state.cancel(self.target,h.grant,'cancel')
        self.assertFalse(h.cancelled());self.assertEqual('incomplete',state.read_capsule(self.target,h.grant)['status'])
        self.assertEqual([],list((self.target/'.hrn/locks').glob('cancel-*.json')))

    def test_capsule_prepublication_failure_does_not_poison_project_truth(self):
        p=self.prepare()
        with mock.patch.object(state,'rename_exclusive',side_effect=OSError('synthetic publication failure')),self.assertRaises(OSError):
            hostmod.Host(p['spec'],p['confirm_token'])
        self.assertEqual([],state.capsules(self.target));state.require_no_open(self.target)
        with self.assertRaisesRegex(ContractError,'grant-already-consumed'):self.prepare()
        request=copy.deepcopy(self.request);request['owner_statement']+=' fresh'
        self.assertNotEqual(p['confirm_token'],self.prepare(request)['confirm_token'])

    def test_cancel_during_rpc_authority_check_has_no_phantom_runtime(self):
        from hv2ref import official_adapter as adapter
        preview=self.prepare();h=hostmod.Host(preview['spec'],preview['confirm_token']);self.addCleanup(h.close)
        with mock.patch.object(adapter,'launch_spec',return_value={'argv':[],'cwd':str(self.folder),'env':{}}),mock.patch.object(h,'authority',side_effect=ContractError('HV2-OFFICIAL-EXECUTION','cancel-requested')),mock.patch.object(h,'cancelled',side_effect=[False,True,True]),mock.patch.object(adapter.subprocess,'Popen') as spawn:
            result=adapter.run(h)
        self.assertEqual('revoked-before-launch',result['status'])
        self.assertFalse(state.read_capsule(self.target,h.grant)['runtime_reserved']);spawn.assert_not_called()

    def test_spawn_failure_is_readable_and_explicitly_resolvable(self):
        from hv2ref import official_adapter as adapter
        h=self.new_host();spec={'argv':['nonexistent'],'cwd':str(self.folder),'env':{}}
        with mock.patch.object(h,'authority'),mock.patch.object(state,'process_birth',return_value='synthetic-host'),mock.patch.object(adapter.subprocess,'Popen',side_effect=OSError('synthetic exec failure')),self.assertRaises(OSError):adapter.Rpc(spec,h)
        closed=h.rpc.close();self.assertTrue(closed['observed_tree_absent']);self.assertEqual(closed,h.rpc.close())
        h.fail(RuntimeError('failed runtime'))
        value=state.read_capsule(self.target,h.grant);self.assertTrue(value['spawn_failed']);self.assertEqual('unknown',value['status'])
        p=state.resolution_preview(self.target,h.grant);self.assertEqual('operator-resolved-unknown',state.resolve(self.target,h.grant,p['confirm_token'])['status'])

    def test_unavailable_birth_with_confirmed_close_can_resolve(self):
        import io
        from types import SimpleNamespace
        from hv2ref import official_adapter as adapter
        h=self.new_host();p=SimpleNamespace(pid=23456,returncode=0,stdin=io.BytesIO(),stdout=io.BytesIO(),stderr=io.BytesIO(),wait=mock.Mock(return_value=0))
        with mock.patch.object(h,'authority'),mock.patch.object(adapter.subprocess,'Popen',return_value=p),mock.patch.object(state,'process_birth',return_value=''),self.assertRaisesRegex(ContractError,'runtime-birth-unavailable'):
            adapter.Rpc({'argv':[],'cwd':str(self.folder),'env':{}},h)
        with mock.patch.object(h.rpc,'descendants'),mock.patch.object(state,'group_absent',return_value=True):self.assertTrue(h.rpc.close()['observed_tree_absent'])
        h.fail(RuntimeError('unavailable birth'))
        with mock.patch.object(state,'process_birth',return_value=''),mock.patch.object(state,'group_absent',return_value=True):
            p=state.resolution_preview(self.target,h.grant);self.assertEqual('operator-resolved-unknown',state.resolve(self.target,h.grant,p['confirm_token'])['status'])

    def test_worker_sync_spawn_failure_resolves_but_interrupted_spawn_stays_unknown(self):
        from hv2ref import official_documents as docs
        for index,error in enumerate((OSError('synthetic spawn'),subprocess.SubprocessError('synthetic preexec'),KeyboardInterrupt())):
            with self.subTest(error=type(error).__name__):
                request=copy.deepcopy(self.request);request['owner_statement']+=' '+str(index)
                h=self.new_host(request)
                with mock.patch.object(h,'authority'),mock.patch.object(docs.subprocess,'Popen',side_effect=error),self.assertRaises(type(error)):
                    h.dispatch(self.envelope())
                h.fail(error)
                value=state.read_capsule(self.target,h.grant);self.assertEqual('unknown',value['status'])
                if isinstance(error,Exception):
                    preview=state.resolution_preview(self.target,h.grant)
                    self.assertEqual('operator-resolved-unknown',state.resolve(self.target,h.grant,preview['confirm_token'])['status'])
                else:
                    with self.assertRaisesRegex(ContractError,'worker-spawn-identity-unavailable'):
                        state.resolution_preview(self.target,h.grant)

    def test_worker_birth_failure_with_confirmed_group_close_is_resolvable(self):
        import io
        from types import SimpleNamespace
        from hv2ref import official_documents as docs
        h=self.new_host()
        worker=SimpleNamespace(pid=23456,returncode=0,stdin=io.BytesIO(),stdout=io.BytesIO())
        with mock.patch.object(h,'authority'),mock.patch.object(docs.subprocess,'Popen',return_value=worker),mock.patch.object(state,'process_birth',side_effect=OSError('synthetic observer failure')),mock.patch.object(docs,'end_process',return_value={'exit_code':0,'process_group_absent':True}),self.assertRaises(OSError):
            h.dispatch(self.envelope())
        h.fail(RuntimeError('observed worker exit'))
        preview=state.resolution_preview(self.target,h.grant)
        self.assertEqual('operator-resolved-unknown',state.resolve(self.target,h.grant,preview['confirm_token'])['status'])

    def test_history_headroom_refuses_next_grant_without_blocking_readers(self):
        h=self.new_host();h.finish('revoked-before-launch')
        request=copy.deepcopy(self.request);request['owner_statement']+=' fresh'
        with mock.patch.object(state,'HISTORY_FILES',state.MAX_CAPSULE_FILES):
            with self.assertRaisesRegex(ContractError,'execution-history-capacity'):self.prepare(request)
            self.assertEqual('revoked-before-launch',state.read_capsule(self.target,h.grant)['status'])
            self.assertTrue(product.workspace_detach_preview(self.target,operation_id='capacity-detach',created_at=TIME))

    def test_resolution_journal_head_is_validated(self):
        h=self.new_host();h.fail(RuntimeError('synthetic'))
        p=state.resolution_preview(self.target,h.grant);bad=p['observation'];bad['journal_head']='0'*64
        h.journal.append('operator-resolved-unknown',bad)
        with self.assertRaisesRegex(ContractError,'resolution-state'):state.read_capsule(self.target,h.grant)

    def exercise_actual_installed_payload_workers_read_write_verify_and_seal(self):
        # Explicit native Host runner only: macOS disallows nesting sandbox-exec.
        # Actual payload worker, policy, process observation and document effects.
        h=self.new_host()
        try:
            self.assertTrue(h.dispatch(self.envelope())['ok'])
            written=h.dispatch(self.envelope('write','u2_write_file',{'file_id':'Editable','expected_sha256':h.spec['documents']['source_digests']['Editable'],'content':AFTER}))
            self.assertTrue(written['ok'])
            for index,verifier in enumerate(('DOC-LINKS','DOC-GFM','DOC-CLAIMS')):
                result=h.dispatch(self.envelope('verify-'+str(index),'u2_verify',{'verifier_id':verifier}))
                self.assertTrue(result['ok']);self.assertTrue(result['result']['pass'])
            h.seal();self.assertEqual('completed',h.finish('completed')['status'])
            self.assertEqual(5,h.workers);self.assertEqual(PREFIX+AFTER.encode()+SUFFIX,(self.target/'a').read_bytes())
            files=state.execution_truth(self.target);self.assertLessEqual(len(files),state.MAX_CAPSULE_FILES)
            self.assertLessEqual(sum((self.target/'.hrn'/v['path']).stat().st_size for v in files),state.MAX_CAPSULE_BYTES)
        except BaseException:
            destination=Path(os.environ['COLVIA_TEST_ROOT']).parent/'failed-worker-capsule'
            shutil.copytree(h.run,destination)
            for original in h.run.rglob('*'):
                if original.is_file():
                    saved=destination/original.relative_to(h.run)
                    if saved.read_bytes()!=original.read_bytes():raise RuntimeError('failure evidence copy mismatch')
            raise

    def test_closed_host_reconstruction_refuses_same_and_new_calls_without_effects(self):
        h=self.new_host();h.revoke('test');h.finish('interrupted');before=self.truth()
        restored=hostmod.Host.restore_closed(self.target,h.grant)
        with mock.patch.object(hostmod,'DocumentController',side_effect=AssertionError('no restored worker')):
            for call in ('same','new'):
                result=restored.dispatch(self.envelope(call))
                self.assertFalse(result['ok']);self.assertFalse(result['worker_admitted'])
        self.assertEqual('interrupted',restored.status()['status']);self.assertEqual(before,self.truth())

    def test_payload_integrity_and_default_window(self):
        self.assertEqual(len(product.workspace_candidate(self.candidate)['payload']),44)
        self.assertEqual(len(product.workspace_candidate(SOURCE)['payload']),30)
        self.assertEqual(product.workspace_candidate(SOURCE)['release_ref']['inventory_id'],'continuation-1')
        p=Path(self.runtime['release_path'])/'payload/runtime/official/worker.sb.in';p.write_bytes(p.read_bytes()+b'\n')
        result=self.installed('run','status','--grant','0'*64)
        self.assertNotEqual(result.returncode,0)

    def process(self, mode, folder):
        out=(folder/'stdout.log').open('xb');err=(folder/'stderr.log').open('xb')
        self.addCleanup(out.close);self.addCleanup(err.close)
        child=subprocess.Popen([sys.executable,'-I','-S','-B',str(SOURCE/'tests/fixtures/official_process.py'),str(self.target),str(folder),mode],stdout=out,stderr=err)
        def cleanup():
            if child.poll() is None:child.kill()
            child.wait(timeout=5)
        self.addCleanup(cleanup)
        return child

    def wait_record(self, child, folder, name):
        deadline=time.monotonic()+20
        while not (folder/(name+'.json')).exists():
            if child.poll() is not None:self.fail((folder/'stdout.log').read_text()+(folder/'stderr.log').read_text())
            self.assertLess(time.monotonic(),deadline,'process observation timeout')
            time.sleep(.01)
        return state.load(folder/(name+'.json'))

    def process_host(self):
        p=self.prepare();folder=self.folder/'host';folder.mkdir()
        state.publish(folder/'preview.json',p);state.publish(folder/'spec.json',p['spec'])
        child=self.process('host',folder);ready=self.wait_record(child,folder,'ready')
        return child,folder,ready

    def test_real_process_cancel_and_writer_exclusion(self):
        child,folder,ready=self.process_host()
        other=self.folder/'writer';other.mkdir();writer=self.process('writer',other)
        self.wait_record(writer,other,'attempt');time.sleep(.1)
        self.assertFalse((other/'acquired.json').exists())
        before=(self.target/'a').read_bytes()
        result=self.installed('run','cancel','--grant',ready['grant'],'--reason','actual separate process')
        self.assertEqual(result.returncode,0,result.stdout.decode()+result.stderr.decode())
        self.assertEqual(child.wait(timeout=15),0,(folder/'stdout.log').read_text()+(folder/'stderr.log').read_text())
        self.assertEqual(writer.wait(timeout=15),0,(other/'stderr.log').read_text())
        self.assertTrue((other/'acquired.json').exists())
        self.assertTrue(state.load(folder/'late.json')['all_refused_before_worker'])
        self.assertEqual(before,(self.target/'a').read_bytes())
        self.assertEqual(state.read_capsule(self.target,ready['grant'])['status'],'interrupted')

    def test_actual_host_death_blocks_writer_then_explicit_resolution(self):
        child,folder,ready=self.process_host();child.kill();child.wait(timeout=5)
        other=self.folder/'writer';other.mkdir();writer=self.process('writer',other)
        self.assertEqual(writer.wait(timeout=15),65,(other/'stderr.log').read_text())
        self.assertFalse((other/'acquired.json').exists());self.assertTrue((other/'refused.json').exists())
        observed=self.installed('run','resolve','--grant',ready['grant'])
        self.assertEqual(observed.returncode,0,observed.stdout.decode()+observed.stderr.decode())
        p=json.loads(observed.stdout)
        resolved=self.installed('run','resolve','--grant',ready['grant'],'--confirm',p['confirm_token'])
        self.assertEqual(resolved.returncode,0,resolved.stdout.decode()+resolved.stderr.decode())
        self.assertEqual(json.loads(resolved.stdout)['status'],'operator-resolved-unknown')

    def test_detach_preserves_execution_capsule(self):
        h=self.new_host();h.finish('revoked-before-launch');h.close()
        raw={p.relative_to(h.run).as_posix():p.read_bytes() for p in h.run.rglob('*') if p.is_file()}
        packet=product.workspace_detach_preview(self.target,operation_id='detach-a',created_at=TIME)
        product.workspace_detach_apply(self.target,packet['request'],confirm_token=packet['confirm_token'])
        self.assertFalse((self.target/'colvia').exists())
        self.assertEqual(raw,{p.relative_to(h.run).as_posix():p.read_bytes() for p in h.run.rglob('*') if p.is_file()})
        with self.assertRaises(ContractError):product.workspace_init_preview(self.candidate,self.target,authority_home_id='new',operation_id='new',created_at=TIME)

if __name__=='__main__':unittest.main()
