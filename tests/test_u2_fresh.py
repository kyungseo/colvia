"""Bounded v58 parity and changed OS-boundary checks. Native agents are never launched."""
from copy import deepcopy
import importlib
import json
import io
import os
from pathlib import Path
import selectors
import signal
import sys
import tempfile
import time
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from tests.test_u2_adapters import host, common, ReadHostTests
policy = host.fresh_codex.policy
fresh = host.fresh_codex
native = host.codex
ops = importlib.import_module(host._package_name + '._macos_execution')
selection = importlib.import_module(host._package_name + '.execution_os')
FIXTURE = Path(__file__).parent / 'fixtures/u2-fresh-v58.json'


class FreshContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture = json.loads(FIXTURE.read_bytes())

    def bound(self, documents, ref):
        value = documents[ref['path']]
        common.require(common.digest(common.canonical(value)) == ref['sha256'], 'fixture-digest')
        return value

    def test_shared_contract_vectors(self):
        for case in self.fixture['contract_cases']:
            with self.subTest(case=case['name']):
                call = lambda: policy.contract(case['anchor'], lambda r:self.bound(case['documents'],r))
                if case['accepted']:
                    call()
                else:
                    with self.assertRaises((common.HostRefusal,KeyError,TypeError)):
                        call()

    def test_policy_admission_prefix_vectors(self):
        f = self.fixture
        self.assertEqual(len(f['policy_cases']),20)
        b = SimpleNamespace(anchor=f['anchor'], anchor_sha256=f['anchor_sha256'])
        for case in f['policy_cases']:
            with self.subTest(case=case['name']):
                self.assertTrue(all(r['event']['kind'] not in ('turn','generation','dispatch') for r in case['rows']))
                call = lambda: policy.budget_state(b,case['rows'],case['now_ms'],validate_contract=False)
                if case['accepted']:
                    state=call()
                    self.assertFalse(state['stopped'])
                    self.assertEqual(state['counts'],case['expected_counts'])
                    self.assertEqual(state['pending'],[])
                else:
                    with self.assertRaises(common.HostRefusal):call()

    def test_shared_journal_vectors(self):
        f = self.fixture
        b = SimpleNamespace(anchor=f['anchor'], anchor_sha256=f['anchor_sha256'])
        for case in f['journal_cases']:
            with self.subTest(case=case['name']):
                call = lambda: policy.budget_state(b,case['rows'],case['now_ms'],validate_contract=False)
                if case['accepted']:
                    state = call()
                    self.assertTrue(state['stopped'])
                    self.assertEqual(state['counts'], f['expected_counts'])
                    self.assertEqual(state['pending'], [])
                else:
                    with self.assertRaises(common.HostRefusal):
                        call()

    def test_clock_and_legacy_fields(self):
        f = self.fixture
        b = object.__new__(native.Budget)
        b.anchor = f['anchor']
        b.os = Mock()
        for case in f['clock_cases']:
            b.os.continuous_ns.return_value = case['mono']
            with self.subTest(case=case['name']), patch.object(native.time,'time_ns',return_value=case['now'] * 1_000_000):
                if case['accepted']:
                    self.assertEqual(b._clock(),case['now'])
                else:
                    with self.assertRaises(common.HostRefusal):b._clock()
        self.assertEqual(b.execution_reserve_ms(),1_800_000)
        for version in (31,57):
            deadline = native.u2_allocation(version)['run_deadline_ms']
            a = {'version':version,'approval':'synthetic-legacy','work':'synthetic-legacy','candidate':'candidate',
                'source_identity':'source','total_deadline_ms':deadline,'origin_wall_ms':deadline-10000,'origin_monotonic_ns':1,
                'input_identity':'input','recovery':{},'activity_clock':'mach_continuous_time_ns','launch_mode':'trusted-native-runtime',
                'launch_contract_sha256':'contract','approval_wall_ms':1,'run_deadline_ms':deadline,
                'direct_tool_policy':{'version':1,'mode':'direct','model':'gpt-6-astra','profiles':['clock','u2'],'approval':'synthetic-legacy'}}
            native.Budget._anchor_fields(a)
            b.anchor = a
            self.assertEqual(b.execution_reserve_ms(),2_058_141)
            a['activity_clock'] = 'unqualified'
            with self.assertRaises(common.HostRefusal):native.Budget._anchor_fields(a)

    def test_private_bound_io_and_no_replace(self):
        with tempfile.TemporaryDirectory(prefix='v58-private-') as name:
            root = Path(name).resolve()
            path = root / 'input.json'
            common.durable_private(path, {'synthetic':True})
            reference = {'path':str(path),'sha256':common.digest(path.read_bytes())}
            self.assertEqual(native.Budget.fresh_bound(reference),{'synthetic':True})
            with self.assertRaises(FileExistsError):common.durable_private(path, {'synthetic':False})
            with self.assertRaises(common.HostRefusal):native.Budget.fresh_bound({**reference,'sha256':'0'*64})
            alias = root / 'alias.json';alias.symlink_to(path)
            with self.assertRaises(common.HostRefusal):native.Budget.fresh_bound({**reference,'path':str(alias)})
            os.link(path,root/'hardlink.json')
            with self.assertRaises(common.HostRefusal):native.Budget.fresh_bound(reference)


class MinimumExecutionTests(unittest.TestCase):
    def test_unsupported_and_missing_capability_before_admission(self):
        admission = Mock()
        for platform in ('win32','linux'):
            with self.subTest(platform=platform), patch.object(selection.sys,'platform',platform):
                with self.assertRaisesRegex(common.HostRefusal,'unsupported-execution-platform'):
                    fresh.consume_activation({},ledger_path='unused',controller_lock_path='unused',admission=admission)
        with patch.object(ops.MacExecution,'preflight',side_effect=common.HostRefusal('capability-unavailable')):
            with self.assertRaisesRegex(common.HostRefusal,'capability-unavailable'):
                fresh.consume_activation({},ledger_path='unused',controller_lock_path='unused',admission=admission)
        admission.assert_not_called()

    def test_bounded_lock_and_mutable_checkpoint_are_distinct(self):
        runtime = ops.MacExecution(common.require)
        with patch.object(runtime,'monotonic',side_effect=[0,6]), patch.object(ops.fcntl,'flock') as lock:
            with self.assertRaisesRegex(common.HostRefusal,'v58-journal-lock-deadline'):
                runtime.budget_lock(999,exclusive=True,deadline_ms=time.time_ns()//1_000_000+10000)
            lock.assert_not_called()
        with tempfile.TemporaryDirectory(prefix='v58-checkpoint-') as name:
            root=Path(name).resolve();target=root/'checkpoint.json'
            common.durable_private(target,{'generation':1})
            runtime.replace_checkpoint(root/'partial.json',target,{'generation':2},common.durable_private)
            self.assertEqual(json.loads(target.read_bytes()),{'generation':2})
            self.assertFalse((root/'partial.json').exists())

    def test_two_local_children_graceful_and_deadline_kill(self):
        runtime=ops.MacExecution(common.require)
        script=Path(__file__).parent/'fixtures/u2_stop_child.py'
        for mode,expected in (('graceful',0),('ignore-term',-signal.SIGKILL)):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory(prefix='v58-local-child-') as name:
                process=runtime.launch([sys.executable,'-I','-S','-B',str(script),mode],name,
                    {'PATH':'/usr/bin:/bin','LANG':'en_US.UTF-8','PYTHONDONTWRITEBYTECODE':'1'})
                selector=selectors.DefaultSelector();selector.register(process.stdout,selectors.EVENT_READ)
                known={process.pid:{'ppid':os.getpid(),'pgid':process.pid,'birth':'bounded-local-child'}}
                try:
                    self.assertTrue(selector.select(5),'child readiness deadline')
                    self.assertEqual(process.stdout.readline(),b'ready\n')
                    def snapshot():
                        return {} if process.poll() is not None else deepcopy(known)
                    began=time.monotonic()
                    absent=runtime.stop_owned(process,known,snapshot)
                    elapsed=time.monotonic()-began
                    self.assertTrue(absent)
                    self.assertEqual(process.returncode,expected)
                    if mode=='ignore-term':self.assertGreaterEqual(elapsed,9.9)
                    self.assertLess(elapsed,21)
                    with self.assertRaises(ProcessLookupError):os.killpg(process.pid,0)
                finally:
                    selector.close()
                    if process.poll() is None:
                        os.killpg(process.pid,signal.SIGKILL);process.wait(timeout=10)
                    for stream in (process.stdin,process.stdout,process.stderr):stream.close()


class FreshHostBindingTests(ReadHostTests):
    def session(self, gate):
        s=object.__new__(fresh.FreshCodexSession)
        s.gate=gate;s.phase='synthetic';s.start='synthetic-01';s.thread='thread-new';s.rejected=False
        s.budget=Mock(anchor={'input_identity':'c'*64,'read_scope':{'files':{'Reference':'a'*64}}})
        s.budget.reserve=Mock()
        spec={'source_identity':'s','candidate':'c','input_template_identity':'i','dynamic_tools':[{'name':name} for name in ('u2_read_file','u2_write_file','u2_verify','u2_accept')]}
        s.admission=fresh.ReadAdmission(gate.cfg,spec,s.budget,s.start)
        s.admission.thread=s.thread;s.admission.turn='turn-read';s.admission.plan='plan-read';s.admission.completed=False
        s.budget.read.side_effect=lambda:{'slots':{s.start:{'plans':['plan-read'] if s.admission.plan=='plan-read' else ['plan-read',s.admission.plan]}}}
        return s

    def params(self, s, file_id='Reference'):
        return {'threadId':s.thread,'turnId':s.admission.turn,'callId':'call-'+s.admission.turn,
                'namespace':None,'tool':'u2_read_file','arguments':{'file_ids':[file_id]}}

    def test_completed_and_refused_Host_bindings_no_refusal_reply(self):
        gate=self.create('fresh-binding');s=self.session(gate)
        result=s.callback(self.params(s))
        self.assertTrue(result['success'])
        self.assertEqual(gate.effects,1)
        calls=s.budget.reserve.call_args_list
        self.assertEqual([call.args[0] for call in calls],['host-dispatch','worker-result'])
        self.assertEqual(calls[-1].args[1]['host_terminal_sha256'],gate.journal.rows[-1]['sha256'])
        s.admission.turn='turn-deny';s.admission.plan='plan-deny';s.admission.call=None
        client=object.__new__(native.LiveClient)
        client.failed=False;client.event_counts={};client.events=[];client.rpc_stage='turn/startPrepared'
        client.callback=s.callback;client.send=Mock()
        with self.assertRaises(fresh.RefusedTurn):
            client.event({'method':'item/tool/call','id':90,'params':self.params(s,'Outside')})
        client.send.assert_not_called()
        self.assertTrue(s.rejected)
        self.assertEqual(gate.effects,1)
        self.assertEqual(s.budget.reserve.call_args_list[-1].args[0],'host-refusal')
        self.assertEqual(s.budget.reserve.call_args_list[-1].args[1]['effects'],0)
        gate.controller.dispatch.assert_called_once()

    def test_fsync_failure_leaves_native_reservation_without_worker(self):
        gate=self.create('fresh-fsync');s=self.session(gate)
        with patch.object(common.os,'fsync',side_effect=OSError('synthetic fsync failure')):
            with self.assertRaises(OSError):s.callback(self.params(s))
        self.assertEqual(s.budget.reserve.call_count,1)
        self.assertEqual(s.budget.reserve.call_args.args[0],'host-dispatch')
        gate.controller.dispatch.assert_not_called()

    def test_native_cleanup_survives_Host_stop_failure(self):
        s=object.__new__(fresh.FreshCodexSession)
        s.closed=False;s.rejected=True;s.start='synthetic-01';s.phase='synthetic';s.known={}
        s.gate=Mock();s.gate.stop.side_effect=OSError('synthetic journal failure')
        s.admission=Mock();s.fd_controller=Mock();s.budget=Mock();s.os=Mock()
        s.os.stop_owned.return_value=True
        s.client=Mock();s.client.process.stdin=io.BytesIO();s.client.process.stdout=io.BytesIO();s.client.process.stderr=io.BytesIO()
        s.client.rpc_stage='thread/start';s.client.initialized=True;s.client.failed=False;s.client.rpc_failure=None
        s.check_auth_metadata=Mock();s.run=self.root
        with self.assertRaisesRegex(OSError,'synthetic journal failure'):s.close()
        s.os.stop_owned.assert_called_once()
        s.budget.reserve.assert_not_called()
        self.assertTrue(s.client.process.stdin.closed)


class FreshConsumptionTests(unittest.TestCase):
    def setup_contract(self, root):
        f=json.loads(FIXTURE.read_bytes());a=deepcopy(f['anchor']);documents=f['documents']
        def publish(name, value):
            path=root/(name+'.json');common.durable_private(path,value)
            return {'path':str(path),'sha256':common.digest(common.canonical(value))}
        a['run_directory']=str(root/'run')
        a['execution_template']=publish('template',documents[a['execution_template']['path']])
        snapshot=deepcopy(documents[a['accounting_snapshot']['path']])
        snapshot['record']=publish('previous',documents[snapshot['record']['path']])
        a['accounting_snapshot']=publish('snapshot',snapshot)
        activation=deepcopy(documents[a['activation']['path']])
        activation.update(snapshot_sha256=a['accounting_snapshot']['sha256'],run_directory=a['run_directory'])
        a['activation']=publish('activation',activation)
        a['consumption']={'path':str(root/'consumption.json'),'sha256':'0'*64}
        lock=root/'controller.lock';common.durable_private(lock,{'version':1})
        ledger=common.EffectJournal(root/'task-ledger.jsonl',create=True)
        ledger.append('v58-parent-reservation',{'reservation_id':activation['reservation_id'],
            'snapshot_sha256':a['accounting_snapshot']['sha256'],'allocation':policy.ALLOCATION,
            'owner_message_id':activation['owner_message_id'],'parent':'C-Codex-live',
            'counts_before':snapshot['counts'],'limits':snapshot['limits']})
        admission=Mock(return_value={'version':1,'template_sha256':policy.TEMPLATE_SHA256,'activation_sha256':a['activation']['sha256'],
            'candidate':a['candidate'],'source_identity':a['source_identity'],'input_identity':a['input_identity'],
            'platform':'darwin','profile':'u2','C_live_authorized':True})
        return a,ledger,lock,admission

    def test_one_consumption_replay_and_late_fsync_failure(self):
        with tempfile.TemporaryDirectory(prefix='v58-consumption-') as name:
            root=Path(name).resolve();a,ledger,lock,admission=self.setup_contract(root)
            with patch.object(native.Budget,'_clock',return_value=1001000), patch.object(ops.time,'time_ns',return_value=1001000 * 1_000_000):
                budget=fresh.consume_activation(a,ledger_path=ledger.path,controller_lock_path=lock,admission=admission)
                self.assertEqual(budget.read()['counts'],{'genesis':1})
            with patch.object(native.Budget,'_clock',return_value=1001000), patch.object(ops.time,'time_ns',return_value=1001000 * 1_000_000):
                with patch.object(common.os,'fsync',side_effect=OSError('synthetic native journal fsync')):
                    with self.assertRaises(OSError):
                        budget.reserve('proxy-start',{'slot':'s4','start_id':'v58-'+a['run_id']})
                with self.assertRaisesRegex(common.HostRefusal,'v58-journal-poisoned'):
                    budget.reserve('proxy-start',{'slot':'s4','start_id':'v58-'+a['run_id']})
            receipt=Path(a['consumption']['path']).read_bytes()
            with self.assertRaises(common.HostRefusal):
                fresh.consume_activation(a,ledger_path=ledger.path,controller_lock_path=lock,admission=admission)
            self.assertEqual(Path(a['consumption']['path']).read_bytes(),receipt)
            rows=ledger.read();self.assertEqual([r['kind'] for r in rows],['v58-parent-reservation','v58-consumed'])
            self.assertEqual(rows[-1]['value']['counts_after']['controls'],6)
            self.assertEqual(rows[-1]['value']['counts_after']['authority_apply'],0)
        with tempfile.TemporaryDirectory(prefix='v58-consumption-failure-') as name:
            root=Path(name).resolve();a,ledger,lock,admission=self.setup_contract(root)
            with patch.object(common.os,'fsync',side_effect=OSError('synthetic ledger fsync')):
                with self.assertRaises(OSError):
                    fresh.consume_activation(a,ledger_path=ledger.path,controller_lock_path=lock,admission=admission)
            self.assertFalse(Path(a['run_directory']).exists())
            self.assertFalse(Path(a['consumption']['path']).exists())
            self.assertEqual(ledger.read()[-1]['kind'],'v58-consumed')


class FreshRpcDiagnosticsTests(unittest.TestCase):
    def session(self, root, client=True):
        root.mkdir()
        s=object.__new__(fresh.FreshCodexSession)
        s.closed=False;s.rejected=False;s.start='synthetic-01';s.phase='synthetic';s.known={}
        s.gate=Mock();s.admission=Mock();s.fd_controller=Mock();s.budget=Mock();s.os=Mock()
        s.os.stop_owned.return_value=True
        process=SimpleNamespace(stdin=io.BytesIO(),stdout=io.BytesIO(),stderr=io.BytesIO())
        s.spawned_process=process;s.client=None
        if client:
            s.client=object.__new__(native.LiveClient)
            s.client.process=process;s.client.selector=Mock();s.client.failed=False
            s.client.sequence=0;s.client.initialized=True;s.client.rpc_stage='initialized'
            s.client.send=Mock()
        s.check_auth_metadata=Mock();s.run=root
        return s

    def test_rpc_error_and_identity_mismatch_persist_without_raw_data(self):
        with tempfile.TemporaryDirectory(prefix='v58-rpc-') as name:
            for index,method in enumerate(('account/read','thread/start')):
                s=self.session(Path(name)/str(index))
                response={'id':1 if index==0 else 99,'error':{'code':-32600,'message':'synthetic-private-detail'}}
                s.client.receive=lambda:response
                params={'refreshToken':False} if method=='account/read' else {}
                with self.assertRaisesRegex(common.HostRefusal,'RPC refused or identity drift'):
                    s.client.request(method,params)
                s.client.rpc_failure['raw_untrusted_extra']='synthetic-secret-extra'
                s.close()
                path=s.run/'rpc-metadata.json';raw=path.read_text();data=json.loads(raw)
                self.assertEqual(path.stat().st_mode & 0o777,0o600)
                self.assertEqual(data['stage'],method)
                self.assertEqual(data['rpc_failure']['error_code'],-32600)
                self.assertEqual(data['rpc_failure']['id_matches'],index==0)
                self.assertEqual(data['rpc_failure']['error_message_sha256'],common.digest(b'synthetic-private-detail'))
                self.assertNotIn('synthetic-private-detail',raw);self.assertNotIn('synthetic-secret-extra',raw)
                self.assertEqual(s.client.send.call_count,1)
                s.os.stop_owned.assert_called_once();s.budget.reserve.assert_not_called()
                self.assertTrue(s.cleanup['process_group_absent'])

    def test_diagnostic_write_failure_still_closes_everything(self):
        with tempfile.TemporaryDirectory(prefix='v58-rpc-write-') as name:
            s=self.session(Path(name)/'case');real=fresh.durable_private
            def write(path,value):
                if Path(path).name=='rpc-metadata.json':raise OSError('synthetic diagnostic write failure')
                return real(path,value)
            with patch.object(fresh,'durable_private',side_effect=write):
                with self.assertRaisesRegex(OSError,'synthetic diagnostic write failure'):s.close()
            s.os.stop_owned.assert_called_once();s.gate.close.assert_called_once()
            s.fd_controller.revoke.assert_called_once();s.client.selector.close.assert_called_once()
            self.assertTrue(all(getattr(s.spawned_process,k).closed for k in ('stdin','stdout','stderr')))
            self.assertTrue(json.loads((s.run/'v58-native-close.json').read_text())['process_group_absent'])
            s.client.send.assert_not_called();s.budget.reserve.assert_not_called()

    def test_no_rpc_failure_and_no_client_remain_distinct(self):
        with tempfile.TemporaryDirectory(prefix='v58-rpc-empty-') as name:
            s=self.session(Path(name)/'success');s.close()
            path=s.run/'rpc-metadata.json';before=path.read_bytes()
            self.assertIsNone(json.loads(before)['rpc_failure'])
            s.close();self.assertEqual(path.read_bytes(),before);s.os.stop_owned.assert_called_once()
            t=self.session(Path(name)/'constructor-failed',client=False);t.close()
            self.assertFalse((t.run/'rpc-metadata.json').exists());t.os.stop_owned.assert_called_once()
            self.assertTrue(t.cleanup['process_group_absent'])
