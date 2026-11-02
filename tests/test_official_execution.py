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
        control=self.folder/'host-control';control.mkdir(mode=0o700)
        state.publish(control/'store.json',{'schema_version':1,'store_id':'b'*32})
        self.request={'work_id':'official-work','worker_root':str(self.target),'documents':{
            'files':{'Editable':{'path':str(self.target/'a'),'view':{'kind':'replace-range','ranges':[[len(PREFIX),len(PREFIX+BEFORE)]]}},
                     'Reference':{'path':str(self.target/'b'),'view':{'kind':'full'}}},
            'output':'Editable','claims':{'Editable':{'required':['Approved fact.'],'forbidden':['Unapproved'],
                'evidence':[{'file_id':'Reference','quote':'Approved fact.'}]}},'approved_external_links':[]},
            'read_ids':['Editable','Reference'],'prompt':'Read, replace with Approved fact., then verify.',
            'owner_statement':'Synthetic bounded execution authorization','runtime':{'sha256':{'BIN':'a'*64}},'runtime_root':str(runtime),'host_control_root':str(control),
            'expires_wall_ns':time.time_ns()+600*10**9,'seconds':90,'worker_limit':5}

    def prepare(self,request=None):return entry.prepare(self.target,request or self.request)
    def new_host(self,request=None,*,bind=True):
        value=self.prepare(request);h=hostmod.Host(value['spec'],value['confirm_token']);self.addCleanup(h.close)
        if bind:
            # Pure Host state seam. Actual OS closure has separate adapter tests.
            birth='Sat Oct 31 12:00:00 2026'
            h.journal.append('runtime-reserved',{'ordinal':1,'host_pid':2147000000,'host_birth':birth})
            h.journal.append('runtime-started',{'ordinal':1,'pid':2147000001,'birth':birth})
            for method in ('initialize','config/read','account/read','model/list'):h.journal.append('rpc-reserved',{'method':method})
            h.journal.append('admission',{'pass':True,'account_type':'chatgpt','model_id':'gpt-6.1-sol','effort':'low','policy_digest':'a'*64})
            for method in ('thread/start','turn/start'):h.journal.append('rpc-reserved',{'method':method})
            h.bind('thread','turn')
        return h
    def close_host(self,h,status='interrupted'):
        history=h.journal.history()
        if history.runtime_start is not None and history.runtime_close is None:
            h.journal.append('processes-closed',{'runtime_ref':history.runtime_start['seq'],'group_absent':True,'final_scan_confirmed':True,'children':[]})
        return h.finish(status)
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
        h=self.new_host(bind=False)
        with self.assertRaisesRegex(ContractError,'unresolved-execution'):self.prepare()
        h.revoke('cancelled');h.finish('revoked-before-launch')
        with self.assertRaisesRegex(ContractError,'grant-already-consumed'):self.prepare()

    def test_cancel_request_is_not_stopped_and_callback_refused(self):
        h=self.new_host();before=(self.target/'a').read_bytes()
        result=state.cancel(self.target,h.grant,'cancelled')
        self.assertTrue(result['cancel_requested']);self.assertFalse(result['effects_stopped'])
        with mock.patch.object(h.controller,'dispatch',side_effect=AssertionError('worker must not run')):
            answer=h.dispatch(self.envelope())
        self.assertFalse(answer['ok']);self.assertFalse(answer['worker_admitted'])
        self.assertEqual(before,(self.target/'a').read_bytes())
        self.assertEqual(state.read_capsule(self.target,h.grant)['status'],'incomplete')

    def test_cancel_marker_immutable_and_malformed_fail_closed(self):
        h=self.new_host();state.cancel(self.target,h.grant,'cancelled')
        with self.assertRaisesRegex(ContractError,'v2-enum'):state.cancel(self.target,h.grant,'different')
        (h.run/'cancel.json').write_text('{')
        with self.assertRaises(ContractError):state.read_capsule(self.target,h.grant)

    def test_other_thread_and_tool_order_refused(self):
        h=self.new_host();bad=self.envelope();bad['threadId']='other'
        self.assertFalse(h.dispatch(bad)['worker_admitted'])
        self.assertTrue(h.revoked)
        self.assertFalse(h.dispatch(self.envelope('new'))['worker_admitted'])

    def test_duplicate_callback_refused(self):
        h=self.new_host();h.seen.add('read')
        with mock.patch.object(h.controller,'dispatch',side_effect=AssertionError('duplicate may not spawn')):
            result=h.dispatch(self.envelope())
        self.assertFalse(result['ok']);self.assertFalse(result['worker_admitted'])
        self.assertEqual(0,h.workers);self.assertEqual('caller_mismatch',result['reason'])

    def test_admitted_baseexception_before_intent_closes_reservation(self):
        h=self.new_host()
        with mock.patch.object(h.controller,'dispatch',side_effect=KeyboardInterrupt),self.assertRaises(KeyboardInterrupt):
            h.dispatch(self.envelope())
        value=state.read_capsule(self.target,h.grant)
        self.assertIsNone(value['pending']);self.assertTrue(value['revoked'])
        self.assertEqual('none',value['document_write_effect'])
        self.assertEqual('interrupted',self.close_host(h)['status'])

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
        # This pure Host fixture has synthetic PIDs; actual absence is tested separately.
        self.enterContext(mock.patch.object(state,'process_birth',return_value=''))
        self.enterContext(mock.patch.object(state,'group_absent',return_value=True))
        p=state.resolution_preview(self.target,h.grant)
        result=state.resolve(self.target,h.grant,p['confirm_token'])
        self.assertEqual(result['status'],'operator-resolved-unknown')
        self.assertEqual(before,((h.run/'grant.json').read_bytes(),(self.target/'a').read_bytes()))
        self.assertNotEqual(result['head'],p['observation']['journal_head'])
        with self.assertRaisesRegex(ContractError,'resolution-requires'):state.resolution_preview(self.target,h.grant)

    def test_resolution_stale_digest_refused(self):
        h=self.new_host();h.fail(RuntimeError('synthetic'))
        self.enterContext(mock.patch.object(state,'process_birth',return_value=''))
        self.enterContext(mock.patch.object(state,'group_absent',return_value=True))
        p=state.resolution_preview(self.target,h.grant)
        (self.target/'a').write_text('changed current bytes\n')
        with self.assertRaisesRegex(ContractError,'stale-resolution'):state.resolve(self.target,h.grant,p['confirm_token'])

    def test_unknown_spawn_gap_cannot_resolve(self):
        h=self.new_host(bind=False)
        h.journal.append('runtime-reserved',{'ordinal':1,'host_pid':2147000000,'host_birth':'Sat Oct 31 12:00:00 2026'})
        h.fail(RuntimeError('spawn gap'))
        with self.assertRaisesRegex(ContractError,'identity-unavailable'):state.resolution_preview(self.target,h.grant)

    def test_expired_status_still_readable(self):
        request=copy.deepcopy(self.request);request['expires_wall_ns']=time.time_ns()+10**9
        h=self.new_host(request)
        with mock.patch.object(time,'time_ns',return_value=request['expires_wall_ns']+1):
            self.assertEqual(state.read_capsule(self.target,h.grant)['status'],'incomplete')
            with self.assertRaisesRegex(ContractError,'deadline'):h.authority()

    def test_project_and_reference_drift_refused(self):
        h=self.new_host();(self.target/'sentinel').write_text('changed\n')
        with self.assertRaisesRegex(ContractError,'outside-output-project-drift'):h.authority()

    def test_actual_installed_status_cancel_and_help(self):
        h=self.new_host()
        result=self.installed('run','status','--grant',h.grant)
        self.assertEqual(result.returncode,0,result.stderr.decode()+result.stdout.decode())
        self.assertEqual(json.loads(result.stdout)['status'],'incomplete')
        result=self.installed('run','cancel','--grant',h.grant,'--reason','cancelled')
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
        with mock.patch.object(state,'rename_exclusive',side_effect=inspect):state.cancel(self.target,h.grant,'cancelled')
        self.assertEqual([True],observed);self.assertTrue(h.cancelled())
        self.assertEqual([],list((self.target/'.hrn/locks').glob('cancel-*.json')))

    def test_cancel_publication_failure_does_not_expose_partial_marker(self):
        h=self.new_host()
        with mock.patch.object(state,'rename_exclusive',side_effect=OSError('synthetic rename failure')),self.assertRaises(OSError):
            state.cancel(self.target,h.grant,'cancelled')
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

    def test_spawn_failure_is_readable_and_automatically_closed(self):
        from hv2ref import official_adapter as adapter
        h=self.new_host(bind=False);spec={'argv':['nonexistent'],'cwd':str(self.folder),'env':{}}
        with mock.patch.object(h,'authority'),mock.patch.object(state,'process_birth',return_value='Sat Oct 31 12:00:00 2026'),mock.patch.object(adapter.subprocess,'Popen',side_effect=OSError('synthetic exec failure')),self.assertRaises(OSError):adapter.Rpc(spec,h)
        closed=h.rpc.close();self.assertTrue(closed['observed_tree_absent']);self.assertEqual(closed,h.rpc.close())
        result=h.fail(RuntimeError('failed runtime'))
        self.assertEqual('revoked-before-launch',result['status']);self.assertEqual('none',result['document_write_effect'])
        state.require_no_open(self.target)

    def test_unavailable_birth_cannot_resolve_despite_confirmed_group_absence(self):
        import io
        from types import SimpleNamespace
        from hv2ref import official_adapter as adapter
        h=self.new_host(bind=False)
        p=SimpleNamespace(pid=23456,returncode=0,stdin=io.BytesIO(),stdout=io.BytesIO(),stderr=io.BytesIO(),wait=mock.Mock(return_value=0))
        with mock.patch.object(h,'authority'),mock.patch.object(adapter.subprocess,'Popen',return_value=p),mock.patch.object(state,'process_birth',side_effect=['Sat Oct 31 12:00:00 2026','']),self.assertRaisesRegex(ContractError,'runtime-birth-unavailable'):
            adapter.Rpc({'argv':[],'cwd':str(self.folder),'env':{}},h)
        with mock.patch.object(h.rpc,'descendants'),mock.patch.object(state,'group_absent',return_value=True),self.assertRaises(ContractError):h.rpc.close()
        h.fail(RuntimeError('unavailable birth'))
        with mock.patch.object(state,'process_birth',return_value=''),mock.patch.object(state,'group_absent',return_value=True),self.assertRaisesRegex(ContractError,'identity-unavailable'):
            state.resolution_preview(self.target,h.grant)

    def test_worker_sync_spawn_failure_closes_but_interrupted_spawn_stays_unknown(self):
        from hv2ref import official_controller as controller
        for index,error in enumerate((OSError('synthetic spawn'),subprocess.SubprocessError('synthetic preexec'),KeyboardInterrupt())):
            with self.subTest(error=type(error).__name__):
                request=copy.deepcopy(self.request);request['owner_statement']+=' '+str(index)
                h=self.new_host(request)
                with mock.patch.object(h,'authority'),mock.patch.object(controller.subprocess,'Popen',side_effect=error):
                    if isinstance(error,Exception):
                        result=h.dispatch(self.envelope());self.assertFalse(result['ok']);self.assertIsNone(h.pending)
                    else:
                        with self.assertRaises(KeyboardInterrupt):h.dispatch(self.envelope())
                if isinstance(error,Exception):
                    result=self.close_host(h);self.assertEqual('interrupted',result['status']);self.assertEqual('none',result['document_write_effect'])
                else:
                    h.fail(error)
                    with self.assertRaisesRegex(ContractError,'identity-unavailable'):state.resolution_preview(self.target,h.grant)

    def test_worker_birth_failure_cannot_resolve_despite_group_close(self):
        import io
        from types import SimpleNamespace
        from hv2ref import official_controller as controller
        h=self.new_host()
        worker=SimpleNamespace(pid=23456,returncode=0,stdin=io.BytesIO(),stdout=io.BytesIO(),stderr=io.BytesIO())
        with mock.patch.object(h,'authority'),mock.patch.object(controller.subprocess,'Popen',return_value=worker),mock.patch.object(state,'process_birth',side_effect=OSError('synthetic observer failure')),mock.patch.object(controller,'end_process',return_value={'exit_code':0,'process_group_absent':True}):
            result=h.dispatch(self.envelope());self.assertFalse(result['ok'])
        h.controller.active=None # Synthetic process: no live child exists in this unit seam.
        h.fail(RuntimeError('observed worker exit'))
        with self.assertRaisesRegex(ContractError,'identity-unavailable'):state.resolution_preview(self.target,h.grant)

    def test_history_headroom_refuses_next_grant_without_blocking_readers(self):
        h=self.new_host(bind=False);h.revoke('cancelled');h.finish('revoked-before-launch')
        request=copy.deepcopy(self.request);request['owner_statement']+=' fresh'
        with mock.patch.object(state,'HISTORY_FILES',state.MAX_CAPSULE_FILES):
            with self.assertRaisesRegex(ContractError,'execution-history-capacity'):self.prepare(request)
            self.assertEqual('revoked-before-launch',state.read_capsule(self.target,h.grant)['status'])
            self.assertTrue(product.workspace_detach_preview(self.target,operation_id='capacity-detach',created_at=TIME))

    def test_resolution_journal_head_is_validated(self):
        # Pure Host fixture: synthetic PIDs are not native process observations.
        self.enterContext(mock.patch.object(state,'process_birth',return_value=''))
        self.enterContext(mock.patch.object(state,'group_absent',return_value=True))
        h=self.new_host();h.fail(RuntimeError('synthetic'))
        p=state.resolution_preview(self.target,h.grant);bad=p['observation'];bad['journal_head']='0'*64
        before=(h.run/'journal.jsonl').read_bytes()
        with self.assertRaises(ContractError):h.journal.append('operator-resolved-unknown',bad)
        self.assertEqual(before,(h.run/'journal.jsonl').read_bytes())
        # A forged durable event must also be rejected by the read-only reducer.
        h.journal.base.append('operator-resolved-unknown',bad)
        with self.assertRaises(ContractError):state.read_capsule(self.target,h.grant)

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
        h=self.new_host();h.revoke('cancelled');self.close_host(h);before=self.truth()
        restored=hostmod.Host.restore_closed(self.target,h.grant)
        with mock.patch.object(hostmod,'Controller',side_effect=AssertionError('no restored worker')):
            for call in ('same','new'):
                result=restored.dispatch(self.envelope(call))
                self.assertFalse(result['ok']);self.assertFalse(result['worker_admitted'])
        self.assertEqual('interrupted',restored.status()['status']);self.assertEqual(before,self.truth())

    def test_payload_integrity_and_default_window(self):
        self.assertEqual(len(product.workspace_candidate(self.candidate)['payload']),48)
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
        result=self.installed('run','cancel','--grant',ready['grant'],'--reason','cancelled')
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
        h=self.new_host(bind=False);h.revoke('cancelled');h.finish('revoked-before-launch');h.close()
        raw={p.relative_to(h.run).as_posix():p.read_bytes() for p in h.run.rglob('*') if p.is_file()}
        packet=product.workspace_detach_preview(self.target,operation_id='detach-a',created_at=TIME)
        product.workspace_detach_apply(self.target,packet['request'],confirm_token=packet['confirm_token'])
        self.assertFalse((self.target/'colvia').exists())
        self.assertEqual(raw,{p.relative_to(h.run).as_posix():p.read_bytes() for p in h.run.rglob('*') if p.is_file()})
        with self.assertRaises(ContractError):product.workspace_init_preview(self.candidate,self.target,authority_home_id='new',operation_id='new',created_at=TIME)


    def linked_request(self, count=1, *, anchored=False):
        request=copy.deepcopy(self.request);targets=[];links=[]
        for n in range(count):
            path=self.target/('linked-'+str(n)+'.md')
            path.write_text('# Linked Heading\n\nMETADATA BODY MUST NOT REACH MODEL\n')
            targets.append({'path':str(path),'anchors':['linked-heading'] if anchored else []})
            links.append('[link]('+path.name+('#linked-heading' if anchored else '')+')')
        (self.target/'a').write_bytes(PREFIX+BEFORE+SUFFIX+'\n'.join(links).encode())
        request['documents']['link_targets']=targets
        return request

    def test_link_metadata_seventeen_targets_keep_two_model_documents_and_no_effects(self):
        from hv2ref import official_worker as worker
        from hv2ref.official_documents import parent_identities
        request=self.linked_request(17)
        # Non-UTF8 targets are intentionally opaque when only existence is requested.
        targets={row['path'] for row in request['documents']['link_targets']}
        for path in targets:Path(path).write_bytes(b'\xffopaque metadata only\x00')
        before=self.truth();entries={str(p.relative_to(self.folder)) for p in self.folder.rglob('*')}
        native=os.open
        def guarded(path,*args,**kwargs):
            if str(path) in targets or str(path) in {Path(n).name for n in targets}:raise AssertionError('metadata body opened')
            return native(path,*args,**kwargs)
        p=self.prepare(request)
        # Existing Work snapshot fingerprints project bytes. Restrict this no-body-read
        # assertion to the added metadata admission and shared link verifier, not that snapshot.
        docs=p['spec']['documents']
        import io,builtins
        native_io,native_builtin=io.open,builtins.open
        def guarded_io(path,*args,**kwargs):
            if str(path) in targets:raise AssertionError('metadata body opened through io')
            return native_io(path,*args,**kwargs)
        def guarded_builtin(path,*args,**kwargs):
            if str(path) in targets:raise AssertionError('metadata body opened through builtins')
            return native_builtin(path,*args,**kwargs)
        with mock.patch.object(os,'open',side_effect=guarded), mock.patch.object(io,'open',side_effect=guarded_io), mock.patch.object(builtins,'open',side_effect=guarded_builtin):
            self.assertEqual(docs['link_metadata'],entry.link_inputs(request['documents'],docs['files'],self.target,docs['parser'],docs['parser_sha256']))
            preflight=dict(docs,parents=parent_identities([v['path'] for v in docs['files'].values()]+list(targets)))
            self.assertTrue(worker.verify(preflight,'DOC-LINKS')['pass'])
        self.assertEqual(before,self.truth());self.assertEqual(entries,{str(p.relative_to(self.folder)) for p in self.folder.rglob('*')})
        docs=p['spec']['documents'];self.assertEqual(17,len(docs['link_metadata']))
        self.assertTrue(all(v['sha256'] is None and v['anchors']==[] for v in docs['link_metadata'].values()))
        spec={'version':2,'files':docs['files'],'parents':parent_identities([v['path'] for v in docs['files'].values()]+list(targets)),
              'outputs':docs['outputs'],'swap':{},'parser':docs['parser'],'parser_sha256':docs['parser_sha256'],
              'claims':docs['claims'],'approved_external_links':[],'link_metadata':docs['link_metadata']}
        result=worker.execute(spec,{'tool':'u2_read_file','arguments':{'file_ids':request['read_ids']}})
        self.assertEqual(['Editable','Reference'],[v['file_id'] for v in result['files']])
        self.assertNotIn('opaque metadata',json.dumps(result));self.assertNotIn('opaque metadata',json.dumps(p))

    def test_initial_full_output_links_refuse_missing_scope_even_inside_edit_range(self):
        request=self.linked_request();del request['documents']['link_targets'];before=self.truth()
        with self.assertRaisesRegex(ContractError,'link-target-outside-scope'):self.prepare(request)
        self.assertEqual(before,self.truth());self.assertFalse((self.target/'.hrn/executions').exists())
        (self.target/'a').write_bytes(b'[broken](missing.md)\n')
        request['documents']['files']['Editable']['view']['ranges']=[[0,len((self.target/'a').read_bytes())]]
        with self.assertRaisesRegex(ContractError,'link-target-outside-scope'):self.prepare(request)
        self.assertFalse((self.target/'.hrn/executions').exists())

    def test_link_metadata_rejects_unreferenced_target_anchor_and_empty_list(self):
        request=self.linked_request();extra=self.target/'extra';extra.write_text('private synthetic')
        variants=[]
        bad=copy.deepcopy(request);bad['documents']['link_targets'].append({'path':str(extra),'anchors':[]});variants.append(bad)
        bad=copy.deepcopy(request);bad['documents']['link_targets'][0]['anchors']=['linked-heading'];variants.append(bad)
        bad=copy.deepcopy(request);bad['documents']['link_targets']=[];variants.append(bad)
        for bad,code in zip(variants,('unreferenced-or-missing-link-target-anchor','unreferenced-or-missing-link-target-anchor','link-target-list')):
            with self.subTest(bad=bad['documents']['link_targets']),self.assertRaisesRegex(ContractError,code):self.prepare(bad)
        self.assertFalse((self.target/'.hrn/executions').exists())

    def test_link_metadata_bounds_types_and_duplicate_anchors(self):
        request=self.linked_request(anchored=True)
        for anchors in (['linked-heading']*2, ['x'+str(n) for n in range(33)], ['x'*513], [False], 'linked-heading', ['\x00']):
            bad=copy.deepcopy(request);bad['documents']['link_targets'][0]['anchors']=anchors
            with self.subTest(anchors=anchors),self.assertRaisesRegex(ContractError,'link-anchor-list'):self.prepare(bad)
        bad=copy.deepcopy(request);bad['documents']['link_targets']*=65
        with self.assertRaisesRegex(ContractError,'link-target-list'):self.prepare(bad)
        request=self.linked_request(9,anchored=True)
        with self.assertRaisesRegex(ContractError,'anchored-target-limit'):self.prepare(request)

    def test_link_anchor_binding_matches_url_decoding_and_missing_anchor_refuses(self):
        request=self.linked_request(anchored=True);target=Path(request['documents']['link_targets'][0]['path'])
        target.write_text('# 한글\n\n# 두번째\n')
        request['documents']['link_targets'][0]['anchors']=['한글','두번째']
        (self.target/'a').write_bytes(PREFIX+BEFORE+SUFFIX+b'[a](linked-0.md#%ED%95%9C%EA%B8%80) [b](linked-0.md#%EB%91%90%EB%B2%88%EC%A7%B8)')
        p=self.prepare(request);value=p['spec']['documents']['link_metadata'][str(target)]
        self.assertEqual(sorted(['한글','두번째']),value['anchors']);self.assertEqual(state.digest(target.read_bytes()),value['sha256'])
        target.write_text('# Different\n')
        with self.assertRaisesRegex(ContractError,'link-anchor-missing'):self.prepare(request)

    def test_link_metadata_rejects_aliases_and_document_overlap(self):
        from hv2ref.official_policy import PolicyRefusal
        request=self.linked_request();path=Path(request['documents']['link_targets'][0]['path'])
        symlink=self.target/'symlink';symlink.symlink_to(path)
        hardlink=self.target/'hardlink';os.link(path,hardlink)
        for alias in (symlink,hardlink):
            bad=copy.deepcopy(request);bad['documents']['link_targets'][0]['path']=str(alias)
            (self.target/'a').write_bytes(PREFIX+BEFORE+SUFFIX+('[x]('+alias.name+')').encode())
            with self.subTest(alias=alias.name),self.assertRaises((PolicyRefusal,ContractError)):self.prepare(bad)
        hardlink.unlink();symlink.unlink()
        request=self.linked_request();bad=copy.deepcopy(request);bad['documents']['link_targets']*=2
        with self.assertRaisesRegex(ContractError,'link-target-alias'):self.prepare(bad)
        bad=copy.deepcopy(request);bad['documents']['link_targets']=[{'path':str(self.target/'b'),'anchors':[]}]
        with self.assertRaisesRegex(ContractError,'link-target-alias'):self.prepare(bad)
        # This candidate is macOS-specific. Assert the case-insensitive filesystem precondition,
        # then demonstrate inode overlap rather than silently skipping this boundary.
        case=self.target/'B';self.assertTrue(case.exists(),'case-insensitive qualification filesystem required')
        (self.target/'a').write_bytes(PREFIX+BEFORE+SUFFIX+b'[case](B)')
        bad['documents']['link_targets'][0]['path']=str(case)
        with self.assertRaisesRegex(ContractError,'link-target-alias'):self.prepare(bad)

    def test_link_targets_reject_managed_case_variants_outside_and_directories(self):
        from hv2ref.official_policy import PolicyRefusal
        request=self.linked_request();outside=self.folder/'outside';outside.write_text('outside')
        self.target.joinpath('.GIT').mkdir();self.target.joinpath('.GIT/config').write_text('synthetic')
        directory=self.target/'real-directory';directory.mkdir()
        protected=[(self.target/'.GIT/config','.GIT/config'),(self.target/'.Hrn/format.json','.Hrn/format.json'),
                   (self.target/'Colvia','Colvia'),(outside,'../outside'),(directory,'real-directory')]
        parser=Path(self.runtime['release_path'])/'payload/runtime/official/marked.umd.js'
        for path,href in protected:
            self.assertTrue(path.exists());self.assertEqual(path.is_dir(),path==directory)
            (self.target/'a').write_bytes(PREFIX+BEFORE+SUFFIX+('[protected]('+href+')').encode())
            records={key:dict(entry.file_record(item['path'],limit=131072)[0],view=item['view']) for key,item in request['documents']['files'].items()}
            docs={'output':'Editable','link_targets':[{'path':str(path),'anchors':[]}]}
            # Test the added link admission directly; .GIT must not be refused first by Work topology.
            error,code=(PolicyRefusal,'path-kind') if path==directory else (ContractError,'document-outside-worker')
            with self.subTest(path=path.name),self.assertRaisesRegex(error,code):
                entry.link_inputs(docs,records,self.target,str(parser),state.digest(parser.read_bytes()))

    def test_prepare_rejects_noncanonical_worker_root_and_document_inode_alias(self):
        from hv2ref.official_policy import PolicyRefusal
        bad=copy.deepcopy(self.request);bad['worker_root']=str(self.target)+'/../project'
        with self.assertRaises(PolicyRefusal):self.prepare(bad)
        alias=self.folder/'project-alias';alias.symlink_to(self.target,target_is_directory=True)
        bad['worker_root']=str(alias)
        with self.assertRaises(PolicyRefusal):self.prepare(bad)
        bad=copy.deepcopy(self.request);bad['documents']['files']['Reference']['path']=str(self.target/'A')
        with self.assertRaisesRegex(ContractError,'document-path-alias'):self.prepare(bad)

    def test_metadata_drift_prevents_execute_before_capsule(self):
        request=self.linked_request();p=self.prepare(request);path=Path(request['documents']['link_targets'][0]['path'])
        info=path.stat();os.utime(path,ns=(info.st_atime_ns,info.st_mtime_ns+1000000))
        with self.assertRaisesRegex(ContractError,'stale-execution-confirmation'):entry.execute(self.target,p['spec'],p['confirm_token'])
        self.assertFalse((self.target/'.hrn/executions').exists())

    def test_anchor_content_drift_with_preserved_size_mtime_prevents_execute(self):
        request=self.linked_request(anchored=True);p=self.prepare(request);path=Path(request['documents']['link_targets'][0]['path'])
        info=path.stat();path.write_bytes(path.read_bytes().replace(b'METADATA',b'CHANGED!'));os.utime(path,ns=(info.st_atime_ns,info.st_mtime_ns))
        with self.assertRaisesRegex(ContractError,'stale-execution-confirmation'):entry.execute(self.target,p['spec'],p['confirm_token'])
        self.assertFalse((self.target/'.hrn/executions').exists())

    def test_metadata_drift_blocks_worker_but_status_cancel_resolve_restore_survive(self):
        # Pure Host fixture: synthetic PIDs are not native process observations.
        self.enterContext(mock.patch.object(state,'process_birth',return_value=''))
        self.enterContext(mock.patch.object(state,'group_absent',return_value=True))
        from hv2ref.official_documents import HostRefusal
        request=self.linked_request();h=self.new_host(request);path=Path(request['documents']['link_targets'][0]['path'])
        path.unlink()
        slots=list(Path(h.spec['host_control']['path']).glob('transient/*/worker-*'));result=h.dispatch(self.envelope())
        self.assertFalse(result['worker_admitted']);self.assertEqual('not_started',result['effect_status'])
        self.assertEqual(slots,list(Path(h.spec['host_control']['path']).glob('transient/*/worker-*')));self.assertEqual(0,h.workers)
        self.assertEqual('incomplete',state.read_capsule(self.target,h.grant)['status'])
        self.assertTrue(state.cancel(self.target,h.grant,'cancelled')['cancel_requested'])
        h.fail(RuntimeError('synthetic metadata drift'));p=state.resolution_preview(self.target,h.grant)
        result=state.resolve(self.target,h.grant,p['confirm_token']);self.assertEqual('operator-resolved-unknown',result['status'])
        restored=hostmod.Host.restore_closed(self.target,h.grant)
        self.assertFalse(restored.dispatch(self.envelope())['worker_admitted'])

    def test_link_profile_literals_only_grant_data_read_for_anchors(self):
        from hv2ref import official_documents as documents
        request=self.linked_request(2);path=Path(request['documents']['link_targets'][1]['path'])
        request['documents']['link_targets'][1]['anchors']=['linked-heading']
        (self.target/'a').write_bytes(PREFIX+BEFORE+SUFFIX+b'[opaque](linked-0.md) [anchor](linked-1.md#linked-heading)')
        h=self.new_host(request)
        # Materialize only; no worker intent or process execution in this profile check.
        slot,_,_=h.controller.materialize('u2_read_file',{'file_ids':request['read_ids']},1)
        self.assertEqual(0,h.workers)
        profile=(slot/'worker.sb').read_text()
        opaque=request['documents']['link_targets'][0]['path']
        self.assertFalse(Path(opaque).is_relative_to(Path(h.spec['documents']['python']).parent.parent),'PYROOT must not cover metadata target')
        metadata=next(line for line in profile.splitlines() if line.startswith('(allow file-read-metadata ') and opaque in line)
        data=next(line for line in profile.splitlines() if line.startswith('(allow file-read* ') and str(path) in line)
        self.assertIn(documents.sb_literal(opaque),metadata);self.assertNotIn(documents.sb_literal(opaque),data)
        import re
        for line in profile.splitlines():
            if line.startswith('(allow file-read* ') or line.startswith('(allow file-read-data '):
                self.assertNotIn(documents.sb_literal(opaque),line)
            for root in re.findall(r'\(subpath "([^"\n]+)"\)',line):
                self.assertFalse(Path(opaque).is_relative_to(root),'broad subpath covers opaque target')
        spec=json.loads((slot/'spec.json').read_text())
        self.assertEqual(h.spec['documents']['link_metadata'],spec['link_metadata'])
        # Exercise the exact generated worker verifier contract in-process; no native process claim.
        from hv2ref.official_worker import verify
        self.assertTrue(verify(spec,'DOC-LINKS')['pass'])

    def exercise_previous_reader_compatibility(self):
        self.assertTrue(os.environ.get('COLVIA_PREVIOUS_OFFICIAL_SOURCE'),'explicit previous artifact is required for compatibility qualification')
        previous=Path(os.environ['COLVIA_PREVIOUS_OFFICIAL_SOURCE'])
        helper=SOURCE/'tests/fixtures/official_reader_compat.py'
        def call(action,request=None,grant=None):
            run=subprocess.run([sys.executable,'-I','-S','-B',str(helper),str(previous),str(self.target),action],
                               input=state.canonical({'request':request,'grant':grant}),capture_output=True,timeout=30)
            self.assertEqual(0,run.returncode,run.stdout+run.stderr);return json.loads(run.stdout)
        # Legacy success has an exactly equal spec/grant across previous and current entry.
        current=self.prepare();old=call('prepare',self.request);self.assertEqual(current,old)
        old_grant=call('closed',self.request)['grant']
        self.assertEqual('revoked-before-launch',state.read_capsule(self.target,old_grant)['status'])
        request=self.linked_request();h=self.new_host(request);path=Path(request['documents']['link_targets'][0]['path'])
        h.fail(RuntimeError('synthetic unstarted failure'));path.unlink()
        self.assertEqual('unknown',call('status',grant=h.grant)['status'])
        preview=call('resolve-preview',grant=h.grant)
        self.assertIn('confirm_token',preview)
        state.resolve(self.target,h.grant,preview['confirm_token'])
        self.assertEqual('operator-resolved-unknown',call('restore',grant=h.grant)['status'])



    def test_preflight_active_html_cleanup_retained_and_link_errors_classified(self):
        from hv2ref.official_documents import parent_identities
        from hv2ref.official_worker import verify
        request=copy.deepcopy(self.request);raw=b'<script>alert(1)</script>\n'
        (self.target/'a').write_bytes(raw);request['documents']['files']['Editable']['view']['ranges']=[[0,len(raw)]]
        p=self.prepare(request);docs=p['spec']['documents']
        full=verify(dict(docs,parents=parent_identities([v['path'] for v in docs['files'].values()])),'DOC-LINKS')
        self.assertFalse(full['pass']);self.assertEqual(['active-html'],[f['code'] for f in full['findings']])
        for raw,code in [(b'[x](b?q=1)\n','link-target-outside-scope'),(b'[x](/absolute)\n','link-target-outside-scope'),
                         (b'[x](https://example.invalid/)\n','initial-document-links-failed'),(b'[x](b#missing)\n','initial-document-links-failed')]:
            (self.target/'a').write_bytes(raw);request['documents']['files']['Editable']['view']['ranges']=[[0,len(raw)]]
            with self.subTest(raw=raw),self.assertRaisesRegex(ContractError,code):self.prepare(request)
        self.assertFalse((self.target/'.hrn/executions').exists())

    def test_anchor_encoding_and_required_link_input_digest_refuse(self):
        request=self.linked_request(anchored=True);target=Path(request['documents']['link_targets'][0]['path'])
        target.write_bytes(b'\xff')
        with self.assertRaisesRegex(ContractError,'link-anchor-encoding'):self.prepare(request)
        target.write_text('# Linked Heading\n');p=self.prepare(request);docs=p['spec']['documents'];native=state.regular
        def changed(path,*args,**kwargs):
            if str(path)==str(self.target/'a'):return b'different body\n'
            return native(path,*args,**kwargs)
        with mock.patch.object(state,'regular',side_effect=changed),self.assertRaisesRegex(ContractError,'output-link-input-drift'):
            entry.link_inputs(request['documents'],docs['files'],self.target,docs['parser'],docs['parser_sha256'])

    def test_nested_metadata_and_parent_relative_links_share_worker_resolution(self):
        from hv2ref.official_documents import parent_identities
        from hv2ref.official_worker import verify
        request=self.linked_request(anchored=True);old=Path(request['documents']['link_targets'][0]['path'])
        nested=self.target/'nested';nested.mkdir();target=nested/'x.md';old.rename(target)
        request['documents']['link_targets'][0]['path']=str(target)
        (self.target/'a').write_bytes(PREFIX+BEFORE+SUFFIX+b'[nested](nested/x.md#linked-heading)')
        p=self.prepare(request);docs=p['spec']['documents']
        spec=dict(docs,parents=parent_identities([v['path'] for v in docs['files'].values()]+list(docs['link_metadata'])))
        self.assertTrue(verify(spec,'DOC-LINKS')['pass'])
        # Unit link contract for an output in a subdirectory; does not fabricate Work scope.
        output=nested/'output.md';output.write_text('[parent](../b#policy)\n')
        records={'Editable':dict(entry.file_record(output,limit=131072)[0],view={'kind':'full'})}
        metadata=entry.link_inputs({'output':'Editable','link_targets':[{'path':str(self.target/'b'),'anchors':['policy']}]},
                                   records,self.target,docs['parser'],docs['parser_sha256'])
        spec.update(files=records,link_metadata=metadata,parents=parent_identities([str(output),str(self.target/'b')]))
        self.assertTrue(verify(spec,'DOC-LINKS')['pass'])

    def test_host_refuses_unclassified_missing_file_before_worker_and_can_resolve(self):
        # Pure Host fixture: synthetic PIDs are not native process observations.
        self.enterContext(mock.patch.object(state,'process_birth',return_value=''))
        self.enterContext(mock.patch.object(state,'group_absent',return_value=True))
        h=self.new_host(self.linked_request());slots=list(Path(h.spec['host_control']['path']).glob('transient/*/worker-*'))
        # Inject the existing metadata stat exception after the independent Work observation.
        with mock.patch.object(h.controller,'check_files',side_effect=FileNotFoundError('synthetic metadata stat')):
            result=h.dispatch(self.envelope())
        self.assertEqual('internal_error',result['reason']);self.assertFalse(result['worker_admitted'])
        self.assertEqual('not_started',result['effect_status']);self.assertEqual(slots,list(Path(h.spec['host_control']['path']).glob('transient/*/worker-*')))
        self.assertEqual('incomplete',state.read_capsule(self.target,h.grant)['status'])
        h.fail(FileNotFoundError('synthetic metadata stat'));p=state.resolution_preview(self.target,h.grant)
        self.assertEqual('operator-resolved-unknown',state.resolve(self.target,h.grant,p['confirm_token'])['status'])

    def test_anchor_drift_after_capsule_refuses_host_before_worker(self):
        # Pure Host fixture: synthetic PIDs are not native process observations.
        self.enterContext(mock.patch.object(state,'process_birth',return_value=''))
        self.enterContext(mock.patch.object(state,'group_absent',return_value=True))
        request=self.linked_request(anchored=True);h=self.new_host(request);target=Path(request['documents']['link_targets'][0]['path'])
        info=target.stat();target.write_bytes(target.read_bytes().replace(b'METADATA',b'CHANGED!'));os.utime(target,ns=(info.st_atime_ns,info.st_mtime_ns))
        result=h.dispatch(self.envelope());self.assertFalse(result['worker_admitted']);self.assertEqual('not_started',result['effect_status'])
        self.assertEqual([],list(Path(h.spec['host_control']['path']).glob('transient/*/worker-*')));self.assertEqual(0,h.workers)
        h.fail(RuntimeError('synthetic anchored drift'));p=state.resolution_preview(self.target,h.grant)
        self.assertEqual('operator-resolved-unknown',state.resolve(self.target,h.grant,p['confirm_token'])['status'])


    def test_cli_error_phase_preserves_fixed_codes_and_status_guidance(self):
        from argparse import Namespace
        from hv2ref import cli
        for action in ('prepare','execute','status','cancel','resolve'):
            args=Namespace(command='run',action=action,target=self.target,input='-',reason='cancelled',host_control_root=None,
                           confirm='a'*64 if action=='execute' else None,grant='a'*64 if action in ('status','cancel','resolve') else None)
            with self.subTest(action=action),mock.patch.object(cli,'_workspace_input',return_value={}), \
                 mock.patch.object(entry,'cli',side_effect=RuntimeError('SYNTHETIC_PRIVATE_FAILURE_MARKER')):
                with self.assertRaises(ContractError) as caught:cli.workspace_run(args)
                message=str(caught.exception)
                self.assertIn('input_shape' if action=='prepare' else 'internal_error',message)
                self.assertNotIn('SYNTHETIC_PRIVATE_FAILURE_MARKER',message)
                if action=='execute':self.assertIn('run status',message)
        for message in ('worker closure unavailable','process-present-or-unconfirmed','observed-child-present'):
            with self.subTest(message=message):self.assertEqual('closure_unconfirmed',hostmod.reason_code(ContractError('HV2-OFFICIAL-EXECUTION',message)))

    def test_late_refusal_preserves_original_stop_reason(self):
        h=self.new_host();h.revoke('worker_budget_consumed')
        h.refuse(reason='cancelled')
        self.close_host(h)
        value=state.read_capsule(self.target,h.grant)
        self.assertEqual('worker_budget_consumed',value['rows'][-1]['value']['stop_reason'])

    def test_repeated_revoke_preserves_first_reason(self):
        h=self.new_host();h.revoke('worker_budget_consumed');h.revoke('cancelled')
        self.close_host(h)
        value=state.read_capsule(self.target,h.grant)
        self.assertEqual('worker_budget_consumed',value['rows'][-1]['value']['stop_reason'])
        self.assertEqual(1,sum(row['kind']=='revoked' for row in value['rows']))

    def test_error_path_cannot_choose_reason_code(self):
        from hv2ref.official_documents import HostRefusal
        for word in ('cancel','recovery','drift','timeout','closure unavailable'):
            for error in (OSError(2,'missing','/synthetic/'+word),RuntimeError(word)):
                with self.subTest(kind=type(error).__name__,word=word):
                    self.assertEqual('internal_error',hostmod.reason_code(error))
                    self.assertEqual('worker_failed',hostmod.reason_code(error,'worker_failed'))
        self.assertEqual('deadline',hostmod.reason_code(TimeoutError('/synthetic/cancel')))
        self.assertEqual('content_rejected',hostmod.reason_code(HostRefusal('credential-like document content')))


if __name__=='__main__':unittest.main()
