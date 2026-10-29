"""Offline admission/cleanup counterexamples; no RPC transport is launched."""
from pathlib import Path
import io, tempfile, unittest
from types import SimpleNamespace
from unittest import mock
from hv2ref import official_adapter as adapter, official_admission as admission, official_state as state
from hv2ref.errors import ContractError

class OfficialAdmissionTests(unittest.TestCase):
    def test_failed_descendant_scan_cannot_be_hidden_by_cleanup_return(self):
        with tempfile.TemporaryDirectory() as name:
            rpc=adapter.Rpc.__new__(adapter.Rpc);rpc.closed=False
            rpc.p=SimpleNamespace(pid=123,returncode=0,stdin=io.BytesIO(),stdout=io.BytesIO(),stderr=io.BytesIO(),wait=mock.Mock(return_value=0))
            rpc.known_children={};rpc.sel=mock.Mock();rpc.trace=io.BytesIO()
            rpc.host=SimpleNamespace(run=Path(name).resolve(),journal=mock.Mock())
            rpc.descendants=mock.Mock(side_effect=OSError('synthetic unavailable scan'))
            with mock.patch.object(state,'group_absent',return_value=True):result=rpc.close()
            self.assertFalse(result['observed_tree_absent']);self.assertFalse(result['final_descendant_scan_confirmed'])
            rpc.host.journal.append.assert_not_called()
            self.assertEqual(result,rpc.close())

    def test_evidence_writers_reject_oversize_before_creating_file(self):
        from hv2ref.official_documents import durable_private
        with tempfile.TemporaryDirectory() as name:
            root=Path(name).resolve()
            for member,size in (('spec.json',1048576),('request.json',131072),('failure.json',65536)):
                with self.assertRaises(Exception):durable_private(root/member,{'value':'x'*size})
                self.assertFalse((root/member).exists())
            with self.assertRaisesRegex(ContractError,'published-record-size'):
                state.publish(root/'grant.json',{'value':'x'*(2*1024*1024)})
            self.assertFalse((root/'grant.json').exists())

    def test_broken_stdin_flush_does_not_skip_process_cleanup(self):
        with tempfile.TemporaryDirectory() as name:
            rpc=adapter.Rpc.__new__(adapter.Rpc);rpc.closed=False
            stream=mock.Mock();stream.closed=False;stream.close.side_effect=BrokenPipeError('synthetic closed pipe')
            waited=mock.Mock(return_value=0)
            rpc.p=SimpleNamespace(pid=123,returncode=0,stdin=stream,stdout=io.BytesIO(),stderr=io.BytesIO(),wait=waited)
            rpc.known_children={};rpc.sel=mock.Mock();rpc.trace=io.BytesIO();rpc.descendants=mock.Mock()
            rpc.host=SimpleNamespace(run=Path(name).resolve(),journal=mock.Mock())
            with mock.patch.object(state,'group_absent',return_value=True):result=rpc.close()
            waited.assert_called_once();self.assertTrue(result['observed_tree_absent'])
            self.assertTrue((Path(name)/'termination.json').exists())

    def test_failed_child_observation_does_not_skip_remaining_children(self):
        with tempfile.TemporaryDirectory() as name:
            rpc=adapter.Rpc.__new__(adapter.Rpc);rpc.closed=False
            rpc.p=SimpleNamespace(pid=123,returncode=0,stdin=io.BytesIO(),stdout=io.BytesIO(),stderr=io.BytesIO(),wait=mock.Mock(return_value=0))
            rpc.known_children={124:'birth-a',125:'birth-b'};rpc.sel=mock.Mock();rpc.trace=io.BytesIO();rpc.descendants=mock.Mock()
            rpc.host=SimpleNamespace(run=Path(name).resolve(),journal=mock.Mock())
            def birth(pid):
                if pid==124:raise OSError('synthetic observer unavailable')
                return ''
            with mock.patch.object(state,'group_absent',return_value=True),mock.patch.object(state,'process_birth',side_effect=birth):result=rpc.close()
            self.assertFalse(result['observed_tree_absent']);self.assertEqual([False,True],[x['absent'] for x in result['children']])

    def test_worker_process_limits_are_fixed_without_changing_parent(self):
        from hv2ref import official_documents as docs
        with mock.patch.object(docs.resource,'setrlimit') as limit:docs.worker_file_limit()
        self.assertEqual([mock.call(docs.resource.RLIMIT_FSIZE,(1048576,1048576)),mock.call(docs.resource.RLIMIT_CORE,(0,0))],limit.call_args_list)

    def test_single_use_rpc_reservation(self):
        rpc=adapter.Rpc.__new__(adapter.Rpc);rpc.consumed=set();rpc.seq=0
        rpc.host=SimpleNamespace(journal=mock.Mock());rpc.send=mock.Mock();rpc.log=mock.Mock()
        rpc.next=mock.Mock(return_value={'id':1,'result':{'account':{'type':'chatgpt'}}})
        rpc.request('account/read',{'refreshToken':False})
        with self.assertRaisesRegex(ContractError,'already-consumed'):rpc.request('account/read',{'refreshToken':False})
        self.assertEqual(rpc.send.call_count,1);self.assertEqual(rpc.host.journal.append.call_count,1)

    def test_warning_allowlist_is_exact_and_single_use(self):
        rpc=adapter.Rpc.__new__(adapter.Rpc);rpc.log=mock.Mock();rpc.direct_fallback_seen=False
        exact={'method':'warning','params':{'message':admission.DIRECT_FALLBACK,'threadId':'thread'}}
        self.assertIsNone(rpc.notification(exact))
        with self.assertRaisesRegex(ContractError,'duplicate-fallback'):rpc.notification(exact)
        rpc.direct_fallback_seen=False
        for value in ('another warning',admission.DIRECT_FALLBACK+' changed'):
            with self.assertRaisesRegex(ContractError,'runtime-diagnostic'):rpc.notification({'method':'warning','params':{'message':value,'threadId':'thread'}})

    def test_native_item_and_remote_control_refused(self):
        rpc=adapter.Rpc.__new__(adapter.Rpc);rpc.log=mock.Mock()
        for message in ({'method':'item/started','params':{'item':{'type':'commandExecution'}}},
                        {'method':'remoteControl/status/changed','params':{'status':'enabled'}},
                        {'id':77,'method':'arbitrary/tool','params':{}}):
            with self.subTest(message=message),self.assertRaises(ContractError):rpc.notification(message)

    def test_admission_does_not_retain_account_details(self):
        with tempfile.TemporaryDirectory() as name:
            config={'features':{**{k:False for k in admission.DISABLED_FEATURES},'code_mode_host':True,'skip_host_skill_discovery':True},
                    'web_search':'disabled','project_doc_max_bytes':0,'notify':[],'default_permissions':admission.PROFILE,'mcp_servers':{}}
            responses={'initialize':{'platformFamily':'unix','platformOs':'macos'},'config/read':{'config':config},
                       'account/read':{'account':{'type':'chatgpt','email':'synthetic-private@example.invalid'}},
                       'model/list':{'data':[{'model':admission.MODEL,'supportedReasoningEfforts':[{'reasoningEffort':'low'}]}]}}
            rpc=SimpleNamespace(host=SimpleNamespace(run=Path(name).resolve()),spec={'cwd':name},send=mock.Mock(),
                                request=mock.Mock(side_effect=lambda method,params:responses[method]))
            admission.preflight(rpc)
            raw=(Path(name)/'admission.json').read_text()
            self.assertNotIn('synthetic-private',raw);self.assertNotIn('email',raw)
            self.assertTrue(state.load(Path(name).resolve()/'admission.json')['catalog_is_not_entitlement_proof'])
            config['features']['shell_tool']=True
            with self.assertRaisesRegex(ContractError,'effective-feature'):admission.preflight(rpc)

class AdapterFlowTests(unittest.TestCase):
    def harness(self, folder, events, *, refused=False):
        import time
        host=SimpleNamespace(run=folder,deadline=time.monotonic()+120,rpc=None,turn=None,thread=None,
            revoked=False,sealed=not refused,completed=0,pending=None,spec={'request':{'prompt':'synthetic'}},terminal=False)
        host.cancelled=mock.Mock(return_value=False);host.revoke=mock.Mock();host.fail=mock.Mock()
        def bind(thread,turn):host.thread=thread;host.turn=turn
        host.bind=bind;host.finish=mock.Mock(side_effect=lambda status:{'status':status})
        host.dispatch=mock.Mock(return_value={'ok':False,'worker_admitted':False,'effect_status':'not_started'})
        rpc=SimpleNamespace(consumed=set(),request=mock.Mock(side_effect=[{'model':admission.MODEL,'thread':{'id':'t'}},{'turn':{'id':'u'}}]),
            next=mock.Mock(side_effect=TimeoutError),event=mock.Mock(side_effect=events),notification=mock.Mock(return_value={'id':'u','status':'completed'}),
            reply=mock.Mock(),interrupt=mock.Mock(),close=mock.Mock(return_value={'observed_tree_absent':True}))
        return host,rpc

    def test_idle_poll_does_not_consume_retry_or_end_turn(self):
        with tempfile.TemporaryDirectory() as name:
            host,rpc=self.harness(Path(name).resolve(),[TimeoutError(),{'method':'turn/completed'}])
            with mock.patch.object(adapter,'launch_spec',return_value={'cwd':name,'tools':[]}),mock.patch.object(adapter,'Rpc',return_value=rpc),mock.patch.object(adapter,'preflight'):
                self.assertEqual({'status':'completed'},adapter.run(host))
            self.assertEqual(2,rpc.event.call_count);self.assertEqual(2,rpc.request.call_count);rpc.interrupt.assert_not_called()

    def test_unadmitted_callback_refusal_interrupts(self):
        with tempfile.TemporaryDirectory() as name:
            host,rpc=self.harness(Path(name).resolve(),[{'id':9,'method':'item/tool/call','params':{}}],refused=True)
            with mock.patch.object(adapter,'launch_spec',return_value={'cwd':name,'tools':[]}),mock.patch.object(adapter,'Rpc',return_value=rpc),mock.patch.object(adapter,'preflight'):
                self.assertEqual({'status':'interrupted'},adapter.run(host))
            rpc.interrupt.assert_called_once();host.fail.assert_not_called()

    def test_cancel_before_launch_is_terminal_without_spawn(self):
        with tempfile.TemporaryDirectory() as name:
            host,_=self.harness(Path(name).resolve(),[]);host.cancelled.return_value=True
            def finish(status):host.terminal=True;return {'status':status}
            host.finish.side_effect=finish
            with mock.patch.object(adapter,'Rpc') as runtime,mock.patch.object(adapter,'launch_spec') as launch:
                self.assertEqual({'status':'revoked-before-launch'},adapter.run(host))
            launch.assert_not_called();runtime.assert_not_called();host.finish.assert_called_once()

    def test_cleanup_and_finish_errors_fall_back_to_unknown_record(self):
        for phase in ('close','finish'):
            with self.subTest(phase=phase),tempfile.TemporaryDirectory() as name:
                host,rpc=self.harness(Path(name).resolve(),[{'method':'turn/completed'}])
                failure=OSError('synthetic '+phase)
                (rpc.close if phase=='close' else host.finish).side_effect=failure
                with mock.patch.object(adapter,'launch_spec',return_value={'cwd':name,'tools':[]}),mock.patch.object(adapter,'Rpc',return_value=rpc),mock.patch.object(adapter,'preflight'),self.assertRaises(OSError):
                    adapter.run(host)
                host.fail.assert_called_once_with(failure)

    def test_leader_wait_timeout_keeps_absence_unconfirmed(self):
        import subprocess
        with tempfile.TemporaryDirectory() as name:
            rpc=adapter.Rpc.__new__(adapter.Rpc);rpc.closed=False
            rpc.p=SimpleNamespace(pid=123,returncode=None,stdin=io.BytesIO(),stdout=io.BytesIO(),stderr=io.BytesIO(),wait=mock.Mock(side_effect=subprocess.TimeoutExpired('synthetic',2)))
            rpc.known_children={};rpc.sel=mock.Mock();rpc.trace=io.BytesIO()
            rpc.host=SimpleNamespace(run=Path(name).resolve(),journal=mock.Mock());rpc.descendants=mock.Mock()
            with mock.patch.object(state,'group_absent',return_value=True),mock.patch.object(adapter,'signal_owned',return_value=False):
                self.assertFalse(rpc.close()['observed_tree_absent'])
            self.assertTrue((Path(name)/'termination.json').exists());rpc.host.journal.append.assert_not_called()

    def test_late_callback_refusal_is_journaled_before_reply(self):
        import time
        rpc=adapter.Rpc.__new__(adapter.Rpc);rpc.host=SimpleNamespace(thread='t',turn='u',journal=mock.Mock())
        rpc.deadline=time.monotonic()+30;rpc.request=mock.Mock();rpc.reply=mock.Mock();rpc.log=mock.Mock()
        rpc.event=mock.Mock(side_effect=[{'id':9,'method':'item/tool/call','params':{'callId':'late'}},{'method':'turn/completed'}])
        rpc.notification=mock.Mock(return_value={'id':'u','status':'interrupted'})
        rpc.interrupt()
        rpc.host.journal.append.assert_called_once_with('refused',{'callId':'late','late':True,'effect_status':'not_started'})
        rpc.reply.assert_called_once()

    def test_signal_exit_race_is_not_a_cleanup_exception(self):
        with mock.patch.object(adapter.os,'killpg',side_effect=ProcessLookupError):self.assertTrue(adapter.signal_owned(123,15,group=True))
        with mock.patch.object(adapter.os,'kill',side_effect=PermissionError):self.assertFalse(adapter.signal_owned(123,15))

class RuntimeInputTests(unittest.TestCase):
    def test_fixed_input_contract_rejects_drift_alias_and_overrides(self):
        import copy, os
        from hv2ref import official_entry as entry
        with tempfile.TemporaryDirectory() as name:
            root=Path(name).resolve();home=root/'home';(home/'.codex/rules').mkdir(parents=True)
            binary=root/'codex';helper=root/'codex-code-mode-host';config=home/'.codex/config.toml'
            paths={'BIN':binary,'CODE_MODE_HOST':helper,'CODEX_CONFIG':config,'CODEX_AUTH':home/'.codex/auth.json',
                   'INSTALLATION_ID':home/'.codex/installation_id','CODEX_RULES_DIR':home/'.codex/rules',
                   'CODEX_RULES_FILE':home/'.codex/rules/default.rules','GLOBAL_INSTRUCTIONS':root/'instructions.md'}
            for key,path in paths.items():
                if key!='CODEX_RULES_DIR':path.write_bytes(b'' if key=='CODEX_CONFIG' else key.encode())
            value={'paths':{k:str(v) for k,v in paths.items()},'sha256':{k:state.digest(paths[k].read_bytes()) for k in entry.PINNED_INPUTS}}
            with mock.patch.object(Path,'home',return_value=home),mock.patch.object(entry,'CLI_SHA256',value['sha256']['BIN']),mock.patch.object(entry,'HELPER_SHA256',value['sha256']['CODE_MODE_HOST']),mock.patch.dict(os.environ,{},clear=True):
                self.assertEqual(value['paths'],entry.runtime_input(value))
                bad=copy.deepcopy(value);bad['sha256']['BIN']='0'*64
                with self.assertRaisesRegex(ContractError,'unqualified-cli-helper'):entry.runtime_input(bad)
                bad=copy.deepcopy(value);bad['sha256'].pop('GLOBAL_INSTRUCTIONS')
                with self.assertRaisesRegex(ContractError,'runtime-pin-set'):entry.runtime_input(bad)
                alias=root/'alias';alias.symlink_to(binary);bad=copy.deepcopy(value);bad['paths']['BIN']=str(alias)
                with self.assertRaises((ContractError,ValueError)):entry.runtime_input(bad)
                paths['GLOBAL_INSTRUCTIONS'].write_bytes(b'drift')
                with self.assertRaisesRegex(ContractError,'runtime-input-drift'):entry.runtime_input(value)
                paths['GLOBAL_INSTRUCTIONS'].write_bytes(b'GLOBAL_INSTRUCTIONS')
                with mock.patch.dict(os.environ,{'CODEX_HOME':str(home/'.codex')}),self.assertRaisesRegex(ContractError,'api-auth-override'):entry.runtime_input(value)
                config.write_bytes(b'model_provider = "custom"\n');changed=copy.deepcopy(value);changed['sha256']['CODEX_CONFIG']=state.digest(config.read_bytes())
                with self.assertRaisesRegex(ContractError,'custom-provider'):entry.runtime_input(changed)

if __name__=='__main__':unittest.main()
