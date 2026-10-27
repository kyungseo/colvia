"""Bounded integration checks for the approved v58 repair.

Real FreshCodexSession, LiveClient pipes, FD registration, Host and reducers.
Only the provider/launch admission, notification schema and process inventory
are synthetic; exactly three local Python children, no socket/auth/network.
"""
from copy import deepcopy
import json
import os
import signal
from pathlib import Path
import sys
import threading
import time
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from tests.test_u2_adapters import host, common, ReadHostTests
from tests.test_u2_fresh import fresh, native, policy, ops, FIXTURE

ROOT = Path(__file__).resolve().parents[1]
TOOLS = json.loads(
    (ROOT/'docs/development/verification/u2-host/tool-profile-v2.json').read_bytes())
LOCAL_CHILD = ROOT/'tests/fixtures/u2_fresh_native.py'


class RepairTests(ReadHostTests):
    def fixture_budget(self, root):
        root.mkdir()
        f=json.loads(FIXTURE.read_bytes());a=deepcopy(f['anchor']);docs=f['documents']
        def publish(name,value):
            p=root/(name+'.json');common.durable_private(p,value)
            return {'path':str(p),'sha256':common.digest(common.canonical(value))}
        a['read_scope']={'core_snapshot_sha256':self.cfg['core_snapshot_sha256'],
                         'identity_sha256':self.cfg['identity_sha256'],
                         'files':{k:v['sha256'] for k,v in self.cfg['documents']['files'].items()}}
        a['run_directory']=str(root/'run')
        a['execution_template']=publish('template',docs[a['execution_template']['path']])
        snapshot=deepcopy(docs[a['accounting_snapshot']['path']])
        snapshot['record']=publish('prior',docs[snapshot['record']['path']])
        a['accounting_snapshot']=publish('snapshot',snapshot)
        activation=deepcopy(docs[a['activation']['path']])
        for key in set(activation)&set(a):
            activation[key]=deepcopy(a[key])
        activation['snapshot_sha256']=a['accounting_snapshot']['sha256']
        a['activation']=publish('activation',activation)
        a['consumption']={'path':str(root/'consumption.json'),'sha256':'0'*64}
        lock=root/'controller.lock';common.durable_private(lock,{'version':1})
        ledger=common.EffectJournal(root/'task-ledger.jsonl',create=True)
        ledger.append('v58-parent-reservation',{'reservation_id':activation['reservation_id'],
            'snapshot_sha256':a['accounting_snapshot']['sha256'],'allocation':policy.ALLOCATION,
            'owner_message_id':activation['owner_message_id'],'parent':'C-Codex-live',
            'counts_before':snapshot['counts'],'limits':snapshot['limits']})
        admitted={'version':1,'template_sha256':policy.TEMPLATE_SHA256,
            'activation_sha256':a['activation']['sha256'],'candidate':a['candidate'],
            'source_identity':a['source_identity'],'input_identity':a['input_identity'],
            'platform':'darwin','profile':'u2','C_live_authorized':True}
        return fresh.consume_activation(a,ledger_path=ledger.path,controller_lock_path=lock,
                                        admission=lambda:admitted)

    def controller(self, budget, root):
        root.mkdir()
        budget.reserve('proxy-start',{'slot':'s4','start_id':'v58-'+budget.anchor['run_id']})
        c=object.__new__(native.PreparedFdController)
        c.budget=budget;c.root=root;c.slot='s4';c.socket_path=root/'unused-socket'
        c.selected_peer='104.18.32.47';c.nonce='a'*64;c.reservation=budget.read()['prev']
        c.max_requests=12;c.closed=False;c.failed=None;c.bindings={};c.leases={};c.lease_bindings={}
        c.condition=threading.Condition(threading.RLock())
        c.proxy=SimpleNamespace(pid=77,poll=lambda:None)
        c.thread=SimpleNamespace(is_alive=lambda:True)
        c.log_fd=os.open(root/'fd-events.jsonl',os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
        self.addCleanup(os.close,c.log_fd)
        def close():
            c.closed=True;c.proxy=None;c.thread=None
        c.close=close
        return c

    def session(self,budget,controller,gate,root,start):
        root.mkdir()
        for name in ('home','cwd','config','tmp'):
            (root/name).mkdir()
        binding={'launch_mode':budget.anchor['launch_mode'],
            'launch_contract_sha256':budget.anchor['launch_contract_sha256'],
            'epoch_sha256':budget.anchor_sha256,'approval':budget.anchor['approval'],
            'direct_tool_policy':budget.anchor['direct_tool_policy']}
        spec={'phase':'synthetic','start':start,'profile':'u2','root':str(root),
            'expires_unix_ms':1_301_000,'dynamic_tools':TOOLS,'auth_home':str(root/'not-a-credential-home'),
            'input_template_identity':'4'*64}
        receipt=fresh.materialize_runtime(budget,spec,root/'spec.json',controller.runtime_transport())
        owner=root/'owner.txt';owner.write_bytes(b'Synthetic exact input.\n');owner.chmod(0o600)
        envelope={'entries':[],'model_specs':[],'tool_mode':'direct','namespaces':[],
                  'policy':{'expose_additional_permissions':False,'require_managed_sandbox':False,
                    'require_unified_exec':False,'allowed_tools':[{'namespace':None,'name':t['name']} for t in TOOLS]}}
        for tool in TOOLS:
            model={'type':'function','name':tool['name'],'description':tool['description'],'strict':False,
                   'parameters':native.native_document_schema(tool['inputSchema'])}
            envelope['entries'].append({'name':tool['name'],'origin':'dynamic','namespace':'functions',
                'exposure':'direct','implementation':'synthetic::DynamicToolHandler','spec':model})
            envelope['model_specs'].append(model)
        child={'evidence':str(root/'child-observation.json'),'start':start,'journal':str(budget.path),
               'journal_lock':str(budget.lock_path),'now_ms':1_001_000,'source_identity':budget.anchor['source_identity'],
               'input_template_identity':'4'*64,'execution_binding':binding,'tool_envelope':envelope,
               **{k:budget.anchor[k] for k in ('approval','work','candidate')}}
        common.durable_private(root/'child-config.json',child)
        runtime={'binary':sys.executable,'binary_sha256':'a'*64,'spec':receipt['path'],
                 'spec_sha256':receipt['sha256'],'launch_mode':'trusted-native-runtime',
                 'launch_contract':str(root/'synthetic-contract.json'),
                 'launch_contract_sha256':budget.anchor['launch_contract_sha256']}
        outer={'phase':'synthetic','start':start,'runtime':runtime,'owner_input':str(owner),
               'owner_input_sha256':common.digest(owner.read_bytes()),'documents':{'allowed_identifiers':[]}}
        session=fresh.FreshCodexSession(outer,budget,root,gate=gate,fd_controller=controller)
        def cleanup():
            process=session.spawned_process
            try:
                if process is not None and not session.closed:
                    session.close()
            finally:
                if process is not None:
                    if process.poll() is None:
                        try:os.killpg(process.pid,signal.SIGKILL)
                        except ProcessLookupError:pass
                    process.wait(timeout=10)
                    for name in ('stdin','stdout','stderr'):
                        getattr(process,name).close()
        self.addCleanup(cleanup)
        return session

    @staticmethod
    def fake_launch(runtime,spec,anchor,anchor_sha,env):
        root=Path(spec['root'])
        return [sys.executable,'-I','-S','-B',str(LOCAL_CHILD),str(root/'child-config.json')], \
            {'cwd':str(root/'cwd')},{'network':{'host':'chatgpt.com','port':443,'peer':'104.18.32.47'}}

    @staticmethod
    def observed_local_only(process,known):
        # This fixture has no child-spawn code. Production ps discovery is not mocked evidence.
        if process.poll() is not None:
            return {}
        row={'ppid':os.getpid(),'pgid':process.pid,'birth':'fixed-local-fixture'}
        known[process.pid]=row
        return {process.pid:row}

    def patches(self):
        for target,name,value in [
            (native.Budget,'_clock',lambda self:1_001_000),
            (ops.time,'time_ns',lambda:1_001_000_000_000),
            (native,'validate_native_launch',self.fake_launch),
            (native,'protected_auth_metadata',lambda home:{'synthetic-only':True}),
            (native,'bind_native_notifications',lambda client,*args:setattr(client,'fixture_flow',Mock())),
            (ops.MacExecution,'observe_owned',lambda this,process,known:self.observed_local_only(process,known))]:
            context=patch.object(target,name,value);context.start();self.addCleanup(context.stop)

    def test_policy_admission_two_fresh_initializations(self):
        self.patches()
        # A no-turn close cannot qualify the next slot; use two independent epochs.
        for index,classification in enumerate(('applied','known-not-applicable')):
            with self.subTest(classification=classification):
                budget=self.fixture_budget(self.root/('budget-'+str(index)))
                controller=self.controller(budget,self.root/('controller-'+str(index)))
                gate=self.create('host-'+str(index))
                s=self.session(budget,controller,gate,self.root/('native-'+str(index)),'synthetic-01')
                cp=s.run/'child-config.json';config=json.loads(cp.read_text())
                config['policy_classification']=classification
                cp.write_bytes(common.canonical(config))
                s.launch()
                self.assertIn(s.start,controller.bindings)
                self.assertTrue(s.thread)
                before=budget.read()
                self.assertEqual(before['slots'][s.start]['policy'],classification)
                self.assertEqual(before['slots'][s.start]['controls'],{'models','accounts'} if index else {'policy','models','accounts'})
                self.assertEqual(before['counts']['policy-admission'],1)
                s.close()
                self.assertTrue(s.cleanup['process_group_absent'])
                with self.assertRaises(ProcessLookupError):os.killpg(s.spawned_process.pid,0)
                self.assertEqual(json.loads((s.run/'child-observation.json').read_text())['messages'],['initialize','initialized','account/read','thread/start'])
                recovery=gate.recovery()
                self.assertEqual(recovery['pending'],None)
                self.assertEqual(recovery['effects'],0)
                self.assertFalse(budget.read()['slots'][s.start]['ended'])
                event=fresh.stop_execution(budget,controller,[s],'initialization-only-complete')
                self.assertEqual(event['kind'],'execution-stop')
                state=budget.read()
                self.assertTrue(state['stopped'])
                self.assertEqual(state['pending'],[])
                self.assertTrue(all(state['counts'].get(k,0)==0 for k in ('turn','generation','dispatch','host-dispatch')))

    def test_real_launch_register_refusal_and_two_slots(self):
        self.patches()
        self.cfg['effect_limit']=2
        budget=self.fixture_budget(self.root/'budget')
        controller=self.controller(budget,self.root/'controller')
        sessions=[]
        for index in (1,2):
            gate=self.create('host',resume=index==2)
            s=self.session(budget,controller,gate,self.root/('native-'+str(index)),'synthetic-0'+str(index))
            sessions.append(s)
            s.launch()
            self.assertIn(s.start,controller.bindings)
            start=next(e for e in budget.read()['events'] if e['kind']=='start' and e['start']==s.start)
            self.assertEqual(start['subject']['runtime_spec_sha256'],s.spec['runtime']['spec_sha256'])
            # Actual registration refuses spec replacement and re-registration without another child.
            bad=dict(s.spec['runtime'],spec_sha256='0'*64)
            with self.assertRaises(common.HostRefusal):controller.register_runtime(bad,s.client.process)
            with self.assertRaises(common.HostRefusal):controller.register_runtime(s.spec['runtime'],s.client.process)
            inputs=[{'type':'text','text':'Synthetic exact input.'}]
            self.assertEqual(s.turn(inputs),s.start+'-turn-1')
            sent=[]
            real_send=s.client.send
            def track(value):
                sent.append(deepcopy(value));return real_send(value)
            s.client.send=track
            self.assertEqual(s.turn(inputs),{'status':'rejected-terminated'})
            self.assertTrue(s.cleanup['process_group_absent'])
            with self.assertRaises(ProcessLookupError):os.killpg(s.spawned_process.pid,0)
            # Only the two planned requests precede refusal; no result/error/interrupt response follows.
            self.assertEqual([m.get('method') for m in sent],['turn/prepare','turn/startPrepared'])
            observed=json.loads((s.run/'child-observation.json').read_text())
            self.assertTrue(observed['refusal_wait']);self.assertEqual(observed['refusal_bytes'],0)
            state=budget.read()
            self.assertTrue(state['slots'][s.start]['ended'])
            terminal=next(row for row in reversed(gate.journal.rows) if row['kind']=='refused')
            refusal=next(row for row in state['events'] if row['kind']=='host-refusal' and row['start']==s.start)
            self.assertEqual(terminal['value']['code'],'file-scope')
            self.assertEqual(refusal['subject']['reason'],'file-scope')
            self.assertEqual(refusal['subject']['host_terminal_sha256'],terminal['sha256'])
            self.assertEqual(refusal['subject']['effects'],0)
            self.assertEqual([e['subject']['generation'] for e in state['events']
                if e['kind']=='generation' and e['start']==s.start],[1,2,1])
            recovery=gate.recovery()
            self.assertEqual(recovery['pending'],None)
            self.assertEqual(recovery['effects'],index)
        event=fresh.stop_execution(budget,controller,sessions,'completed')
        self.assertEqual(event['kind'],'execution-stop')
        self.assertTrue(budget.read()['stopped'])
        with self.assertRaises(common.HostRefusal):sessions[-1].launch()

    def test_spawn_registration_failure_has_positive_cleanup(self):
        self.patches()
        budget=self.fixture_budget(self.root/'budget')
        controller=self.controller(budget,self.root/'controller')
        gate=self.create('host')
        s=self.session(budget,controller,gate,self.root/'native-failed','synthetic-01')
        actual=controller.register_runtime
        def fail(runtime,process):
            actual(runtime,process)
            raise common.HostRefusal('synthetic on_spawn failure')
        controller.register_runtime=fail
        with self.assertRaisesRegex(common.HostRefusal,'synthetic on_spawn failure'):s.launch()
        self.assertIsNone(s.client)
        self.assertIsNotNone(s.spawned_process)
        self.assertIsNotNone(s.spawned_process.poll())
        failure=json.loads((s.run/'startup-failure-metadata.json').read_text())
        self.assertTrue(failure['process_group_absent'])
        s.close()
        self.assertTrue(s.cleanup['observed_descendants_absent'])
        with self.assertRaises(ProcessLookupError):os.killpg(s.spawned_process.pid,0)
        # No false completed-slot event; execution may stop only after the positive cleanup.
        self.assertFalse(budget.read()['slots'][s.start]['ended'])
        s.cleanup={}
        with self.assertRaisesRegex(common.HostRefusal,'v58-final-native-unknown'):
            fresh.stop_execution(budget,controller,[s],'failed')
        self.assertFalse(budget.read()['stopped'])
        self.assertFalse(any(e['kind']=='execution-stop' for e in budget.read()['events']))
        s.cleanup={'process_group_absent':True,'observed_descendants_absent':True}
        fresh.stop_execution(budget,controller,[s],'failed')
        self.assertTrue(budget.read()['stopped'])

    def test_pre_effect_deviation_inventory_and_preflight(self):
        gate=self.create('deviation')
        budget=Mock()
        spec={'dynamic_tools':TOOLS,'source_identity':'b'*64,'candidate':'a'*64,'input_template_identity':'4'*64}
        a=fresh.ReadAdmission(gate.cfg,spec,budget,'synthetic-01')
        a.thread='thread';a.turn='turn';a.plan='plan';a.completed=False
        budget.read.return_value={'slots':{'synthetic-01':{'plans':['plan']}}}
        params={'threadId':'thread','turnId':'turn','callId':'call','namespace':None,
                'tool':'u2_verify','arguments':{'verifier_id':'DOC-GFM'}}
        with self.assertRaisesRegex(common.HostRefusal,'unexpected-tool-before-effect'):a.callback(params)
        budget.reserve.assert_not_called();gate.controller.dispatch.assert_not_called()
        budget.read.return_value={'slots':{'synthetic-01':{'plans':['first','plan']}}}
        params.update(tool='u2_read_file',arguments={'file_ids':['Reference']})
        with self.assertRaisesRegex(common.HostRefusal,'unexpected-valid-read-before-effect'):a.callback(params)
        budget.reserve.assert_not_called();gate.controller.dispatch.assert_not_called()
        with self.assertRaisesRegex(common.HostRefusal,'four-tool-inventory'):
            fresh.ReadAdmission(gate.cfg,{**spec,'dynamic_tools':TOOLS[:3]},budget,'synthetic-01')
        with patch.object(ops.Path,'is_file',return_value=False):
            with self.assertRaisesRegex(common.HostRefusal,'execution-observation-unavailable'):
                ops.MacExecution(common.require).preflight('codex-v58')

    def test_peer_selection_and_v57_unchanged(self):
        addresses=['1.1.1.1','104.18.32.47']
        evidence={'host':'chatgpt.com','addresses':addresses,'resolution_count':1,'selected_peer':'104.18.32.47'}
        for version in (57,58):
            self.assertEqual(native.frozen_network_peer(version,addresses,evidence),'104.18.32.47')
            for ips,ev in [
                (['1.1.1.1'],{'host':'chatgpt.com','addresses':['1.1.1.1'],'resolution_count':1}),
                (addresses,{k:v for k,v in evidence.items() if k!='selected_peer'}),
                (addresses,{**evidence,'selected_peer':'1.1.1.1'})]:
                with self.assertRaises(common.HostRefusal):native.frozen_network_peer(version,ips,ev)
        old={'host':'chatgpt.com','addresses':['1.1.1.1'],'resolution_count':1}
        self.assertEqual(native.frozen_network_peer(1,['1.1.1.1'],old),'1.1.1.1')

    def test_start_field_repair_vectors_no_model_events(self):
        f=json.loads(FIXTURE.read_bytes())
        budget=SimpleNamespace(anchor=f['anchor'],anchor_sha256=f['anchor_sha256'])
        selected=[c for c in f['journal_cases'] if c['name'].startswith('start-') and 'spec' in c['name']]
        self.assertEqual(len(selected),2)
        for case in selected:
            self.assertEqual(case['simulated_turns'],0)
            with self.assertRaises(common.HostRefusal):
                policy.budget_state(budget,case['rows'],case['now_ms'],validate_contract=False)


    def test_fd_start_record_and_peer_binding_refuse_before_spawn(self):
        self.patches()
        budget=self.fixture_budget(self.root/'budget')
        controller=self.controller(budget,self.root/'controller')
        gate=self.create('host')
        s=self.session(budget,controller,gate,self.root/'never-spawn','synthetic-01')
        controller.selected_peer='1.1.1.1'
        with self.assertRaisesRegex(common.HostRefusal,'controller-contract-peer'):s.launch()
        self.assertIsNone(s.spawned_process)
        self.assertEqual(gate.runtime_counts['native-start'],0)
        controller.selected_peer='104.18.32.47'
        binding={'launch_mode':budget.anchor['launch_mode'],
                 'launch_contract_sha256':budget.anchor['launch_contract_sha256'],
                 'epoch_sha256':budget.anchor_sha256,'approval':budget.anchor['approval'],
                 'direct_tool_policy':budget.anchor['direct_tool_policy']}
        budget.reserve('start',{'execution_binding':binding,'proxy_identity_sha256':s.proxy_identity(),
            'runtime_spec_sha256':s.spec['runtime']['spec_sha256']},s.phase,s.start)
        original=budget.read()
        start=next(e for e in original['events'] if e['kind']=='start')
        process=Mock();process.poll.return_value=None
        for events in [
            [e for e in original['events'] if e['kind']!='start'],
            original['events']+[start],
            [({**e,'subject':{**e['subject'],'runtime_spec_sha256':'0'*64}} if e['kind']=='start' else e)
             for e in original['events']]]:
            state={**original,'events':events}
            with patch.object(budget,'read',return_value=state):
                with self.assertRaises(common.HostRefusal):
                    controller.register_runtime(s.spec['runtime'],process)
        self.assertEqual(controller.bindings,{})
        # A reserved start with no process observation is unknown, not absent.
        s.close=Mock()
        with self.assertRaisesRegex(common.HostRefusal,'final-native-unknown'):
            fresh.stop_execution(budget,controller,[s],'unobserved')
        self.assertFalse(budget.read()['stopped'])
