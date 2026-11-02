"""Whole capsule/truth/index scans with positive controls for each payload path."""
from pathlib import Path
import json
import subprocess
import unittest
from unittest import mock

import test_official_execution as fixture
import test_official_faults_v2 as faults
from hv2ref import official_adapter as adapter, official_controller as controller, official_state as state


class PayloadV2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):fixture.OfficialExecutionTests.setUpClass.__func__(cls)
    @classmethod
    def tearDownClass(cls):fixture.OfficialExecutionTests.tearDownClass.__func__(cls)
    def setUp(self):fixture.OfficialExecutionTests.setUp(self)
    prepare=fixture.OfficialExecutionTests.prepare
    execute=faults.FaultV2Tests.execute
    oracle=faults.FaultV2Tests.oracle
    installed=fixture.OfficialExecutionTests.installed

    def scan(self,h,markers):
        # Scan all durable project truth, not only selected grant fields.
        raw=b''.join(p.read_bytes() for p in (self.target/'.hrn').rglob('*') if p.is_file())
        for marker in markers:self.assertNotIn(marker.encode(),raw,marker)
        subprocess.run(['git','-C',str(self.target),'init','-q'],capture_output=True,check=True,timeout=30)
        subprocess.run(['git','-C',str(self.target),'add','--','.hrn/executions'],capture_output=True,check=True,timeout=30)
        staged=subprocess.run(['git','-C',str(self.target),'ls-files','-s','-z'],capture_output=True,check=True,timeout=30).stdout
        self.assertTrue(staged)
        for entry in staged.split(b'\0'):
            if not entry:continue
            sha=entry.split()[1].decode()
            blob=subprocess.run(['git','-C',str(self.target),'cat-file','blob',sha],capture_output=True,check=True,timeout=30).stdout
            for marker in markers:self.assertNotIn(marker.encode(),blob,marker)
        self.assertEqual({'grant.json','journal.jsonl','receipt.json'} if state.read_capsule(self.target,h.grant)['sealed'] else {'grant.json','journal.jsonl'},set(p.name for p in h.run.iterdir()))

    def test_all_live_payload_families_reach_boundary_but_not_truth_or_index(self):
        markers={name:name+'_UNIQUE_PAYLOAD_MARKER' for name in ('PROMPT','OWNER','REQUIRED','FORBIDDEN','EVIDENCE','NEWCONTENT','HIDDEN')}
        prefix=('# '+markers['HIDDEN']+'\n\n').encode();before=b'Before.\n'
        anchor='anchor-unique-payload-marker';link='https://example.invalid/EXTERNAL_LINK_UNIQUE_PAYLOAD_MARKER'
        suffix=('\n[metadata](linked.md#'+anchor+') [external]('+link+')\n').encode()
        (self.target/'a').write_bytes(prefix+before+suffix)
        (self.target/'b').write_text('# Reference\nApproved fact. '+markers['EVIDENCE']+' '+markers['REQUIRED']+'\n')
        (self.target/'linked.md').write_text('# '+anchor+'\nLINK_BODY_PRIVATE_MARKER\n')
        docs=self.request['documents'];docs['files']['Editable']['view']['ranges']=[[len(prefix),len(prefix+before)]]
        docs['link_targets']=[{'path':str(self.target/'linked.md'),'anchors':[anchor]}];docs['approved_external_links']=[link]
        rule=docs['claims']['Editable'];rule['required']=['Approved fact.',markers['REQUIRED']];rule['forbidden']=[markers['FORBIDDEN']]
        rule['evidence']=[{'file_id':'Reference','quote':markers['EVIDENCE']}]
        self.request['prompt']=markers['PROMPT'];self.request['owner_statement']=markers['OWNER']
        observed={'specs':[],'reads':[],'prompts':[]};exchange=controller.Controller.exchange;request=adapter.Rpc.request
        def capture(bound,value,timeout):
            specs=list(bound.transient.glob('worker-*/spec.json'));observed['specs'].append(specs[-1].read_text())
            out,err=exchange(bound,value,timeout)
            if value['tool']=='u2_read_file':observed['reads'].append(json.loads(out)['result'])
            return out,err
        def rpc(bound,method,params,*args,**kwargs):
            if method=='turn/start':observed['prompts'].append(params['input'][0]['text'])
            return request(bound,method,params,*args,**kwargs)
        content='Approved fact. '+markers['REQUIRED']+' '+markers['NEWCONTENT']+'\n'
        h=self.execute(content=content,patches=[mock.patch.object(controller.Controller,'exchange',new=capture),mock.patch.object(adapter.Rpc,'request',new=rpc)])
        self.oracle(h,'completed','applied',True)
        self.assertEqual([markers['PROMPT']],observed['prompts']);self.assertEqual(markers['OWNER'],h.spec['request']['owner_statement'])
        self.assertEqual(content,self.callbacks[1]['arguments']['content'])
        self.assertEqual('Before.\n',observed['reads'][0]['files'][0]['content'])
        spec=''.join(observed['specs'])
        for name in ('REQUIRED','FORBIDDEN','EVIDENCE'):self.assertIn(markers[name],spec)
        self.assertIn(anchor,spec);self.assertIn(link,spec)
        original=Path(self.request['host_control_root'])/'recovery'/h.grant/'1/original.bin'
        self.assertEqual(prefix+before+suffix,original.read_bytes())
        self.assertNotIn(markers['HIDDEN'],json.dumps(observed['reads']))
        self.assertFalse((Path(self.request['host_control_root'])/'transient'/h.grant).exists())
        self.scan(h,[*markers.values(),anchor,link,'LINK_BODY_PRIVATE_MARKER','SCRIPT_THREAD_MARKER','SCRIPT_TURN_MARKER','SCRIPT_CALL_MARKER','CALLBACK_ENVELOPE_MARKER'])

    def test_refused_content_positive_control_and_no_storage(self):
        marker='REFUSED_CONTENT_UNIQUE_MARKER';content='api_key='+marker
        h=self.execute(content=content);self.oracle(h,'interrupted','none',True)
        self.assertEqual(content,self.callbacks[1]['arguments']['content'])
        self.scan(h,[marker])

    def test_rpc_error_positive_control_and_no_storage(self):
        observed=[];native=adapter.Rpc.log
        def capture(bound,kind,value):
            if kind=='rpc-error':observed.append(value)
            return native(bound,kind,value)
        h=self.execute(mode='rpc-error',patches=[mock.patch.object(adapter.Rpc,'log',new=capture)])
        self.oracle(h,'revoked-before-launch','none',True)
        self.assertEqual([{'code':-1,'message':'RPC_ERROR_MARKER'}],observed);self.scan(h,['RPC_ERROR_MARKER'])

    def test_runtime_stderr_positive_control_and_no_storage(self):
        observed=[];native=adapter.Rpc.err
        def capture(bound,raw):observed.append(raw);return native(bound,raw)
        h=self.execute(mode='stderr',patches=[mock.patch.object(adapter.Rpc,'err',new=capture)])
        self.oracle(h,'interrupted','none',True)
        self.assertEqual(b'RUNTIME_STDERR_MARKER\n',b''.join(observed));self.scan(h,['RUNTIME_STDERR_MARKER'])


if __name__=='__main__':unittest.main()
