"""V2 fault injection through the actual offline adapter and real worker children."""
from contextlib import ExitStack, contextmanager
from pathlib import Path
import json
import os
import subprocess
import sys
import unittest
from unittest import mock

import test_official_execution as fixture
from hv2ref import official_adapter as adapter, official_host as hostmod, official_state as state
from hv2ref import official_controller as controller, official_recovery as recovery, official_os
from hv2ref.errors import ContractError
from hv2ref.workspace import writer_guard


class FaultV2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):fixture.OfficialExecutionTests.setUpClass.__func__(cls)
    @classmethod
    def tearDownClass(cls):fixture.OfficialExecutionTests.tearDownClass.__func__(cls)
    def setUp(self):fixture.OfficialExecutionTests.setUp(self)
    prepare=fixture.OfficialExecutionTests.prepare

    def execute(self,*,mode='normal',content=fixture.AFTER,patches=(),worker_fault=None):
        scenario=self.folder/'scenario.json';scenario.write_text(json.dumps({'mode':mode,'content':content}))
        p=self.prepare();h=hostmod.Host(p['spec'],p['confirm_token']);self.addCleanup(h.close)
        launch={'argv':[sys.executable,'-I','-S','-B',str(fixture.SOURCE/'tests/fixtures/official_scripted_server.py'),str(scenario)],
                'env':dict(os.environ),'cwd':str(self.folder),'policy_sha256':'a'*64,'tools':[]}
        native=subprocess.Popen;self.started=[];self.error=None;self.callbacks=[];self.replies=[]
        dispatch=h.dispatch
        def capture(value):
            self.callbacks.append(value);result=dispatch(value);self.replies.append(result);return result
        def spawn(argv,**kwargs):
            if argv[0]=='/usr/bin/sandbox-exec' and '--spec' in argv:
                argv=argv[argv.index('-f')+2:];self.started.append(list(argv))
                if worker_fault is not None and len(self.started)==worker_fault[0]:
                    argv=[sys.executable,'-I','-S','-B',str(fixture.SOURCE/'tests/fixtures/official_fault_worker.py'),worker_fault[1]]
            return native(argv,**kwargs)
        with ExitStack() as stack:
            stack.enter_context(mock.patch.object(adapter,'launch_spec',return_value=launch))
            stack.enter_context(mock.patch.object(subprocess,'Popen',side_effect=spawn))
            stack.enter_context(mock.patch.object(h,'dispatch',side_effect=capture))
            for patch in patches:stack.enter_context(patch)
            try:self.result=adapter.run(h)
            except BaseException as error:self.error=error;self.result=None
        return h

    def oracle(self,h,status,effect,allowed):
        value=state.read_capsule(self.target,h.grant)
        self.assertEqual((status,effect),(value['status'],value['document_write_effect']),repr(self.error))
        if allowed:
            with writer_guard(self.target):pass
        else:
            with self.assertRaises(ContractError):
                with writer_guard(self.target):self.fail('unresolved history entered writer')
        # Actual runtime observation, not a test-provided absence verdict.
        if h.rpc is not None and h.rpc.p is not None:
            self.assertIsNotNone(h.rpc.p.poll());self.assertTrue(state.group_absent(h.rpc.p.pid))
        return value

    @contextmanager
    def append_fault(self,kind,*,role=None,torn=False,after=False):
        native=official_os.MacExecution.append_journal;seen=[]
        def fault(bound,path,raw,*args):
            row=json.loads(raw)
            match=row['kind']==kind and (role is None or row['value'].get('tool')==role or row['value'].get('worker_ordinal')==role)
            if match and not seen:
                seen.append(row)
                if after:native(bound,path,raw,*args)
                elif torn:
                    with Path(path).open('ab') as stream:stream.write(raw[:len(raw)//2]);stream.flush();os.fsync(stream.fileno())
                raise OSError('SYNTHETIC_JOURNAL_ERROR_MARKER')
            return native(bound,path,raw,*args)
        with mock.patch.object(official_os.MacExecution,'append_journal',new=fault):yield seen
        self.assertEqual(1,len(seen),'fault path was not reached')

    def test_actual_entry_holds_common_guard_and_returns_closed_result(self):
        import fcntl
        from hv2ref import official_entry as entry
        scenario=self.folder/'entry-scenario.json';scenario.write_text(json.dumps({'mode':'normal','content':fixture.AFTER}))
        prepared=self.prepare();hosts=[];original_host=hostmod.Host;native=subprocess.Popen;workers=[]
        launch={'argv':[sys.executable,'-I','-S','-B',str(fixture.SOURCE/'tests/fixtures/official_scripted_server.py'),str(scenario)],
                'env':dict(os.environ),'cwd':str(self.folder),'policy_sha256':'a'*64,'tools':[]}
        def construct(*args,**kwargs):
            with (self.target/'.hrn/locks/writer.lock').open('rb') as lock:
                with self.assertRaises(BlockingIOError):fcntl.flock(lock.fileno(),fcntl.LOCK_EX|fcntl.LOCK_NB)
            h=original_host(*args,**kwargs);hosts.append(h);return h
        def spawn(argv,**kwargs):
            if argv[0]=='/usr/bin/sandbox-exec' and '--spec' in argv:
                argv=argv[argv.index('-f')+2:];workers.append(argv)
            return native(argv,**kwargs)
        with mock.patch.object(hostmod,'Host',side_effect=construct),mock.patch.object(adapter,'launch_spec',return_value=launch),mock.patch.object(subprocess,'Popen',side_effect=spawn):
            result=entry.execute(self.target,prepared['spec'],prepared['confirm_token'])
        self.assertEqual(('completed','applied',5),(result['status'],result['document_write_effect'],len(workers)))
        self.assertEqual(1,len(hosts));self.assertIsNone(hosts[0].lock);self.assertIsNotNone(hosts[0].rpc.p.poll())
        with writer_guard(self.target):pass

    def test_actual_synchronous_exec_failure_has_no_write_effect(self):
        native = controller.Controller.materialize
        def missing(bound, tool, args, ordinal):
            slot, swap, argv = native(bound, tool, args, ordinal)
            if tool == 'u2_write_file': argv = [str(slot / 'absent-executable')]
            return slot, swap, argv
        before = (self.target / 'a').read_bytes()
        h = self.execute(patches=[mock.patch.object(controller.Controller, 'materialize', new=missing)])
        value = self.oracle(h, 'interrupted', 'none', True)
        worker = value['history'].workers[2]
        self.assertIsNotNone(worker['failure']); self.assertIsNone(worker['start'])
        self.assertEqual(before, (self.target / 'a').read_bytes())

    def test_actual_resolution_guard_rejects_bad_observation_before_append(self):
        with self.append_fault('worker-result', role=2): h = self.execute()
        self.oracle(h, 'incomplete', 'unknown', False)
        path = h.run / 'journal.jsonl'; before = path.read_bytes()
        native = recovery.document_observation
        def invalid(*args, **kwargs):
            observed, raw = native(*args, **kwargs)
            if observed is not None: observed['nlink'] = 2
            return observed, raw
        with mock.patch.object(recovery, 'document_observation', side_effect=invalid):
            preview = state.resolution_preview(self.target, h.grant)
            with self.assertRaises(ContractError):
                state.resolve(self.target, h.grant, preview['confirm_token'])
        self.assertEqual(before, path.read_bytes())
        self.oracle(h, 'incomplete', 'unknown', False)

    def test_recovery_fsync_failure_prevents_write_and_preserves_orphan(self):
        native=recovery.publish_private;seen=[]
        def fail(path,raw):
            if Path(path).name=='manifest.json':
                seen.append(path)
                with mock.patch.object(recovery.os,'fsync',side_effect=OSError('RECOVERY_FSYNC_MARKER')):return native(path,raw)
            return native(path,raw)
        h=self.execute(patches=[mock.patch.object(recovery,'publish_private',side_effect=fail)])
        value=self.oracle(h,'interrupted','none',True);self.assertEqual(1,len(seen));self.assertEqual(1,len(self.started))
        self.assertEqual('orphan_candidate',recovery.inspect(value,self.request['host_control_root']))
        self.assertNotIn(b'RECOVERY_FSYNC_MARKER',(h.run/'journal.jsonl').read_bytes())

    def test_document_drift_after_reservation_aborts_before_intent(self):
        native=controller.Controller.preflight;seen=[]
        def drift(bound,tool,args):
            if tool=='u2_write_file':
                seen.append(tool)
                if len(seen)==2:(self.target/'a').write_text('External drift marker\n')
            return native(bound,tool,args)
        h=self.execute(patches=[mock.patch.object(controller.Controller,'preflight',new=drift)])
        value=self.oracle(h,'interrupted','none',True)
        self.assertEqual(2,len(seen));self.assertEqual(1,len(self.started));self.assertIsNone(value['pending'])
        self.assertTrue(any(r['kind']=='callback-aborted-before-spawn' for r in value['rows']))

    def test_committed_reservation_then_crash_keeps_pending_without_write_intent(self):
        with self.append_fault('callback-reserved',role='write',after=True):h=self.execute()
        value=self.oracle(h,'incomplete','none',False);self.assertEqual(2,value['pending']);self.assertEqual(1,len(self.started))
        self.assertEqual('present',recovery.inspect(value,self.request['host_control_root']))

    def test_worker_closure_observation_failure_keeps_known_effect_but_blocks(self):
        native=state.group_absent;seen=[]
        def observe(pid):
            absent=native(pid)
            # The actual runtime is the first started process; only worker checks
            # inject unavailable absence, without fabricating a positive result.
            if absent and len(self.started)>0 and not seen:
                seen.append(pid);return False
            return absent
        h=self.execute(patches=[mock.patch.object(state,'group_absent',side_effect=observe)])
        value=self.oracle(h,'unknown','none',False);self.assertEqual(1,len(seen));self.assertIsNotNone(value['pending'])

    def test_missing_original_after_completion_does_not_change_effect_or_guard(self):
        h=self.execute();value=self.oracle(h,'completed','applied',True)
        root=Path(self.request['host_control_root']);original=root/'recovery'/h.grant/'1/original.bin'
        original.rename(root/'synthetic-missing-original.bin')
        self.assertEqual('missing',recovery.inspect(value,root));self.oracle(h,'completed','applied',True)

    def test_pre_intent_controller_exception_aborts_pending(self):
        native=controller.Controller.materialize;seen=[]
        def fail(bound,tool,args,ordinal):
            if tool=='u2_write_file':seen.append(tool);raise OSError('PRE_INTENT_MARKER')
            return native(bound,tool,args,ordinal)
        h=self.execute(patches=[mock.patch.object(controller.Controller,'materialize',new=fail)])
        value=self.oracle(h,'interrupted','none',True);self.assertEqual(1,len(seen));self.assertEqual(1,len(self.started))
        self.assertFalse(self.replies[-1]['worker_admitted'])
        self.assertNotIn(b'PRE_INTENT_MARKER',b''.join(p.read_bytes() for p in h.run.iterdir()))
        self.assertIsNone(value['pending']);self.assertTrue(any(r['kind']=='callback-aborted-before-spawn' for r in value['rows']))

    def test_reservation_torn_append_never_spawns_write(self):
        with self.append_fault('callback-reserved',role='write',torn=True):h=self.execute()
        self.assertEqual(1,len(self.started))
        with self.assertRaises(Exception):state.read_capsule(self.target,h.grant)
        with self.assertRaises(Exception):
            with writer_guard(self.target):self.fail('torn journal entered writer')

    def test_spawn_intent_committed_then_host_exception_keeps_unknown(self):
        with self.append_fault('worker-spawn-intent',role=2,after=True):h=self.execute()
        value=self.oracle(h,'incomplete','unknown',False);self.assertEqual(1,len(self.started))
        with self.assertRaisesRegex(ContractError,'identity-unavailable'):state.resolution_preview(self.target,h.grant)

    def test_write_result_append_failure_does_not_infer_from_changed_bytes(self):
        with self.append_fault('worker-result',role=2):h=self.execute()
        self.oracle(h,'incomplete','unknown',False)
        self.assertEqual(fixture.PREFIX+fixture.AFTER.encode()+fixture.SUFFIX,(self.target/'a').read_bytes())

    def test_terminal_append_failure_keeps_valid_prefix_blocked(self):
        with self.append_fault('terminal'):h=self.execute(mode='wrong-caller')
        self.oracle(h,'incomplete','none',False);self.assertEqual(0,len(self.started))

    def test_refusal_append_failure_keeps_prefix_blocked(self):
        with self.append_fault('callback-refused'):h=self.execute(mode='wrong-caller')
        self.oracle(h,'incomplete','none',False);self.assertEqual(0,len(self.started))

    def test_ready_append_success_then_crash_keeps_original_without_reservation(self):
        with self.append_fault('recovery-ready',after=True):h=self.execute()
        value=self.oracle(h,'incomplete','none',False);self.assertEqual(1,len(self.started))
        self.assertEqual('present',recovery.inspect(value,self.request['host_control_root']))

    def test_runtime_intent_append_success_then_crash_has_no_inferred_pid(self):
        with self.append_fault('runtime-reserved',after=True):h=self.execute()
        self.oracle(h,'incomplete','none',False)
        with self.assertRaisesRegex(ContractError,'identity-unavailable'):state.resolution_preview(self.target,h.grant)

    def test_later_callback_rejection_keeps_applied(self):
        native=controller.Controller.preflight;seen=[]
        def refuse(bound,tool,args):
            if tool=='u2_verify':seen.append(tool);raise ContractError('HV2-OFFICIAL-EXECUTION','scope_mismatch')
            return native(bound,tool,args)
        h=self.execute(patches=[mock.patch.object(controller.Controller,'preflight',new=refuse)])
        self.oracle(h,'interrupted','applied',True);self.assertEqual(1,len(seen));self.assertEqual(2,len(self.started))

    def test_verifier_failure_preserves_applied_and_never_seals(self):
        h=self.execute(content='Unapproved\n')
        value=self.oracle(h,'interrupted','applied',True)
        self.assertFalse(value['sealed']);self.assertEqual(5,len(self.started))
        self.assertTrue(any(r['kind']=='worker-result' and r['value']['reason']=='verifier_failed' for r in value['rows']))

    def test_read_result_binding_refusal_completes_known_failure(self):
        native=controller.Controller.validate_result;seen=[]
        def fail(bound,tool,args,result,prior,swap):
            if tool=='u2_read_file':seen.append(result);raise ContractError('HV2-OFFICIAL-EXECUTION','content_rejected')
            return native(bound,tool,args,result,prior,swap)
        h=self.execute(patches=[mock.patch.object(controller.Controller,'validate_result',new=fail)])
        value=self.oracle(h,'interrupted','none',True);self.assertEqual(1,len(seen));self.assertIsNone(value['pending'])

    def test_started_write_lost_response_is_unknown_even_with_original_bytes(self):
        native=controller.Controller.exchange;seen=[]
        def fail(bound,request,timeout):
            if request['tool']=='u2_write_file':
                seen.append(request);raise OSError('WRITE_RESPONSE_LOST_MARKER')
            return native(bound,request,timeout)
        before=(self.target/'a').read_bytes()
        h=self.execute(patches=[mock.patch.object(controller.Controller,'exchange',new=fail)])
        self.oracle(h,'unknown','unknown',False);self.assertEqual(1,len(seen))
        self.assertEqual(before,(self.target/'a').read_bytes());self.assertEqual(2,len(self.started))

    def test_worker_stderr_reaches_diagnostic_without_persisting_raw(self):
        h=self.execute(worker_fault=(1,'stderr'))
        value=self.oracle(h,'interrupted','none',True);self.assertEqual(1,len(self.started))
        diagnostic=[r for r in value['rows'] if r['kind']=='diagnostic' and r['value']['source']=='worker']
        self.assertEqual(sum(r['value']['byte_count'] for r in diagnostic),len(b'WORKER_STDERR_SECRET_MARKER\n'))
        raw=b''.join(p.read_bytes() for p in h.run.iterdir())
        self.assertNotIn(b'WORKER_STDERR_SECRET_MARKER',raw);self.assertNotIn(b'WORKER_RESPONSE_SECRET_MARKER',raw)

    def test_started_write_actual_nonzero_is_unknown_without_byte_change(self):
        before=(self.target/'a').read_bytes();h=self.execute(worker_fault=(2,'nonzero'))
        value=self.oracle(h,'unknown','unknown',False);self.assertEqual(before,(self.target/'a').read_bytes())
        self.assertTrue(any(r['kind']=='worker-closed' and r['value']['returncode']==17 for r in value['rows']))

    def test_started_write_actual_false_response_is_unknown_without_byte_change(self):
        before=(self.target/'a').read_bytes();h=self.execute(worker_fault=(2,'false'))
        self.oracle(h,'unknown','unknown',False);self.assertEqual(before,(self.target/'a').read_bytes())
        self.assertNotIn(b'WORKER_RESPONSE_SECRET_MARKER',b''.join(p.read_bytes() for p in h.run.iterdir()))

    def test_deadline_with_known_no_effect_and_actual_runtime_close_interrupts(self):
        import time
        seen=[]
        def deadline(bound,*args,**kwargs):
            seen.append(True);bound.host.deadline=time.monotonic()-1;raise TimeoutError('synthetic poll timeout')
        h=self.execute(patches=[mock.patch.object(adapter.Rpc,'event',new=deadline)])
        value=self.oracle(h,'interrupted','none',True);self.assertEqual([True],seen)
        self.assertEqual('deadline',value['rows'][-1]['value']['stop_reason'])

    def test_cleanup_failure_keeps_closed_and_external_pending_marker(self):
        native=Path.unlink;seen=[]
        def fail(path,*args,**kwargs):
            if path.name=='worker.sb' and 'transient' in path.parts:
                seen.append(path);raise OSError('CLEANUP_FAILURE_MARKER')
            return native(path,*args,**kwargs)
        h=self.execute(mode='normal',patches=[mock.patch.object(Path,'unlink',new=fail)])
        self.oracle(h,'completed','applied',True);self.assertEqual(1,len(seen));self.assertTrue(self.result['cleanup_pending'])
        self.assertTrue((Path(self.request['host_control_root'])/'transient'/h.grant/'cleanup.json').is_file())


    def test_partial_receipt_publication_preserves_readable_closed_history(self):
        native=state.publish;seen=[]
        def partial(path,value):
            if Path(path).name=='receipt.json' or Path(path).name.startswith('receipt-'):
                seen.append(Path(path))
                Path(path).write_bytes(b'{');Path(path).chmod(0o600)
                raise OSError('RECEIPT_PARTIAL_MARKER')
            return native(path,value)
        h=self.execute(patches=[mock.patch.object(state,'publish',side_effect=partial)])
        value=self.oracle(h,'interrupted','applied',True)
        self.assertTrue(value['sealed']);self.assertEqual(1,len(seen));self.assertFalse((h.run/'receipt.json').exists())
        self.assertNotIn(b'RECEIPT_PARTIAL_MARKER',b''.join(p.read_bytes() for p in h.run.iterdir()))

    def test_receipt_post_rename_failure_leaves_complete_readable_receipt(self):
        native=state.rename_exclusive;seen=[]
        def after(source,destination):
            native(source,destination)
            if Path(destination).name=='receipt.json':seen.append(destination);raise OSError('RECEIPT_SYNC_MARKER')
        h=self.execute(patches=[mock.patch.object(state,'rename_exclusive',side_effect=after)])
        value=self.oracle(h,'interrupted','applied',True)
        self.assertEqual(1,len(seen));self.assertEqual(h.grant,state.load(h.run/'receipt.json')['grant']);self.assertTrue(value['sealed'])

    def test_started_write_actual_empty_pipe_is_unknown_without_byte_change(self):
        before=(self.target/'a').read_bytes();h=self.execute(worker_fault=(2,'lost'))
        value=self.oracle(h,'unknown','unknown',False);self.assertEqual(before,(self.target/'a').read_bytes())
        self.assertEqual(2,len(self.started))
        self.assertTrue(any(r['kind']=='worker-closed' and r['value']['returncode']==0 for r in value['rows']))

    def test_explicit_root_status_reports_terminal_transient_without_mutation(self):
        from argparse import Namespace
        from hv2ref import official_entry as entry
        h=self.execute(patches=[mock.patch.object(recovery,'cleanup_transient',return_value=False)])
        self.oracle(h,'completed','applied',True)
        root=Path(self.request['host_control_root']);base=root/'transient'/h.grant
        self.assertTrue(base.is_dir());self.assertFalse((base/'cleanup.json').exists())
        args=Namespace(action='status',grant=h.grant,host_control_root=None)
        self.assertEqual('not_checked',entry.cli(self.target,args)['transient_presence'])
        args.host_control_root=str(root)
        before={str(p):p.read_bytes() for top in (h.run,root) for p in top.rglob('*') if p.is_file()}
        result=entry.cli(self.target,args)
        self.assertEqual(('present','absent'),(result['transient_presence'],result['cleanup_marker_presence']))
        self.assertEqual(before,{str(p):p.read_bytes() for top in (h.run,root) for p in top.rglob('*') if p.is_file()})
        state.publish(base/'cleanup.json',{'schema_version':1,'grant':h.grant,'pending_ordinals':[1,2,3,4,5],'reason':'storage_failed'})
        result=entry.cli(self.target,args)
        self.assertEqual(('completed','applied','present'),(result['status'],result['document_write_effect'],result['cleanup_marker_presence']))


if __name__=='__main__':unittest.main()
