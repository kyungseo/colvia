"""Two real synthetic workers, then human-confirmed serial integration.

Compute is a deterministic fixture transformation, not an agent or application
benchmark. All commits and rebase are operator fixture actions outside Work apply.
"""
from __future__ import annotations
from tests.platform_fixtures import (
    fixture_pgid,
)
from test_productization_safety import verified_inventory_id
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile
import time
import unittest

from hv2ref.jsonio import canonical_json_bytes
from hv2ref.product import verify_workspace_product
from hv2ref.work import make_manifest,snapshot,record_ref,read_work,git_environment
from test_productization_safety import exact_snapshot
import test_worktree_execution as fixtures

WORKER=r"""
import json,os,sys,time
from pathlib import Path
root,signals,identity=Path(sys.argv[1]),Path(sys.argv[2]),sys.argv[3]
mine=signals/identity
def emit(event):
    p=mine/(event+'.writing')
    p.write_text(json.dumps({'event':event,'pid':os.getpid(),'pgid':None if sys.platform == 'win32' else os.getpgrp(),'monotonic_ns':time.monotonic_ns()}))
    os.replace(p,mine/(event+'.json'))
def wait(name):
    deadline=time.monotonic()+180
    while not (signals/name).exists():
        if time.monotonic()>deadline:raise TimeoutError(name)
        time.sleep(.01)
emit('ready');wait('compute')
p=root/'a';s=p.read_text();old=identity+' = 0';new=identity+' = 1'
assert s.count(old)==1
p.write_text(s.replace(old,new), newline='\n');emit('computed');wait('finish')
"""
RETEST="""from pathlib import Path
import sys
assert (Path(sys.argv[1])/'a').read_bytes()==Path(sys.argv[2]).read_bytes()
print('synthetic combined content verified')
"""


class InstalledTwoWorkerIntegrationTests(unittest.TestCase):
    TIME=fixtures.InstalledWorkerPublicationTests.TIME
    installed=fixtures.InstalledWorkerPublicationTests.installed
    preview=fixtures.InstalledWorkerPublicationTests.preview
    apply_init=fixtures.InstalledWorkerPublicationTests.apply_init
    draft=fixtures.InstalledWorkerPublicationTests.draft
    accept_intent=fixtures.InstalledWorkerPublicationTests.accept_intent

    def setUp(self):
        fixtures.InstalledWorkerPublicationTests.setUp(self)
        self.evidence=self.base.parent/('worker-integration-evidence-'+self.base.name);self.evidence.mkdir()
        self.commands=[];self.events={};self.children=[];self.handles=[];self.success=False;self.serial=0
        self.addCleanup(self.preserve)

    def preserve(self):
        for p in self.children:
            if p.poll() is None:
                p.terminate()
                try:p.wait(timeout=5)
                except subprocess.TimeoutExpired:p.kill();p.wait(timeout=5)
        for f in self.handles:f.close()
        if not self.success:
            with tarfile.open(self.evidence/'failed-fixture.tar.gz','w:gz') as archive:archive.add(self.base,arcname='fixture')
        receipt={'success':self.success,'commands':self.commands,'events':self.events,'child_exit_codes':[p.returncode for p in self.children],'all_children_joined':all(p.poll() is not None for p in self.children)}
        (self.evidence/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
        print(json.dumps({'two_worker_integration':self.success,'commands':len(self.commands),'child_exit_codes':receipt['child_exit_codes']}),flush=True)

    def record(self,result,kind,*,data=None,cwd=None,seconds=None):
        stem=f'{len(self.commands):03d}'
        for stream in ('stdout','stderr'):(self.evidence/(stem+'.'+stream)).write_bytes(getattr(result,stream))
        item={'kind':kind,'argv':list(map(str,result.args)),'cwd':str(cwd or self.target),'exit':result.returncode,'seconds':seconds,'stdout_sha256':hashlib.sha256(result.stdout).hexdigest(),'stderr_sha256':hashlib.sha256(result.stderr).hexdigest()}
        if data is not None:
            (self.evidence/(stem+'.input.json')).write_bytes(data);item['input_sha256']=hashlib.sha256(data).hexdigest()
        self.commands.append(item)

    def call(self,command,value=None,*,env=None,launcher=None,expected=0):
        start=time.monotonic();p=fixtures.InstalledWorkerPublicationTests.call(self,command,value,env=env,launcher=launcher,expected=None)
        self.record(p,'cli',data=canonical_json_bytes(value) if value is not None else None,seconds=round(time.monotonic()-start,6))
        if expected is not None:self.assertEqual(expected,p.returncode,(p.stdout+p.stderr).decode(errors='replace'))
        return p

    def git(self,target,*args):
        if args and args[0] == "commit":
            args = ("-c", "maintenance.auto=false", "-c", "gc.auto=0", *args)
        config = ['-c', 'core.autocrlf=false', '-c', 'core.eol=lf'] if sys.platform == 'win32' else []
        start=time.monotonic();p=subprocess.run(['git',*config,'-C',str(target),*args],capture_output=True,env=git_environment(),timeout=30)
        self.record(p,'operator-git',cwd=target,seconds=round(time.monotonic()-start,6));self.assertEqual(0,p.returncode,p.stderr.decode(errors='replace'))
        return p.stdout.strip().decode()

    def publish(self,wid,operation,manifest,*,worker=None):
        self.serial+=1;rid=f'revision-{self.serial}'
        graph=read_work(self.target,wid) if (self.target/'.hrn/work'/wid).exists() else None
        prior=graph['current']['selection_ref'] if graph else None
        identity={'record_type':'work-identity','schema_version':1,'authority_home_id':'home-a','work_id':wid,'work_type':'change','created_at':self.TIME,'acceptance_authority':'owner','lineage':None}
        h=hashlib.sha256(canonical_json_bytes(manifest)).hexdigest()
        revision={'record_type':'work-revision','schema_version':1,'authority_home_id':'home-a','work_id':wid,'record_id':rid,'observed_at':self.TIME,'observed_scope':[],'unavailable_scope':[],'author':'agent','operation':operation,'expected_prior_selection':prior,'intent_ref':self.intent,'scope':['a'],'document_refs':[],'evidence_refs':[],'result_refs':{'manifest':{'id':h,'sha256':h}},'progress':'review' if operation=='submit-result' else 'active','next_action':'owner review','relations':[],'rebind_from':self.intent if operation=='rebind' else None,'execution_context':{'mode':'isolated-worktree','attempt_id':rid}}
        args=['work','publish']+(['--worker',worker] if worker is not None else [])
        value={'identity':identity,'revision':revision,'manifest':manifest,'selection_id':f'selection-{self.serial}','operation_id':f'operation-{self.serial}'}
        output=json.loads(self.installed(args,value).stdout)
        return revision,output

    def prepare(self,wid,action='accept',revision=None):
        self.serial+=1
        request={'work_id':wid,'action':action,'actor':'owner','reason':'synthetic explicit review','request_id':f'human-{self.serial}','observed_at':self.TIME,'revision_ref':record_ref(revision) if revision else None,'supersedes':None}
        return json.loads(self.installed(['work','prepare'],request).stdout)

    def apply(self,prepared,*,expected=0):
        before=exact_snapshot(self.target/'.git')
        result=self.installed(['work','apply','--confirm',prepared['confirm_token']],prepared['ticket'],expected=expected)
        self.assertEqual(before,exact_snapshot(self.target/'.git'))
        return json.loads(result.stdout)

    def observe(self,target):return snapshot(target,verified_launcher_sha256=self.sha, verified_inventory_id=verified_inventory_id(self.target))

    def manifest(self,base,result,base_commit,candidate_commit,base_ref,candidate_ref):
        return make_manifest(base,result,scope=['a'],base_commit=base_commit,candidate_commit=candidate_commit,base_retention_ref='refs/heads/'+base_ref,candidate_retention_ref='refs/heads/'+candidate_ref)

    def test_two_workers_same_file_stale_refresh_rebase_and_record_only_commit(self):
        initial='alpha = 0\n'+''.join(f'unchanged {i}\n' for i in range(20))+'beta = 0\n'
        (self.target/'a').write_text(initial, newline='\n')
        self.git(self.target,'init','-q');self.git(self.target,'config','user.name','Fixture');self.git(self.target,'config','user.email','fixture@example.invalid')
        self.apply_init(self.preview());self.intent=self.accept_intent()
        self.git(self.target,'add','.')
        if sys.platform == 'win32':
            self.git(self.target,'update-index','--chmod=+x','colvia')
        self.git(self.target,'commit','-qm','synthetic shared base')
        base_oid=self.git(self.target,'rev-parse','HEAD');self.git(self.target,'branch','base-start',base_oid)
        self.sha=verify_workspace_product(self.target)['launcher_sha256'];base=self.observe(self.target)
        baseline=self.manifest(base,base,base_oid,base_oid,'base-start','base-start')
        for wid in ('work-a','work-b'):self.publish(wid,'start',baseline)
        workers={name:self.base/('worker-'+name) for name in ('alpha','beta')}
        for name,worker in workers.items():self.git(self.target,'worktree','add','-q','-b','worker-'+name,str(worker),base_oid)
        signals=self.evidence/'signals';signals.mkdir();script=self.evidence/'worker.py';script.write_text(WORKER)
        authority={name:exact_snapshot(worker/'.hrn') for name,worker in workers.items()}
        control_before_compute=exact_snapshot(self.target)
        for name,worker in workers.items():
            (signals/name).mkdir();out=(self.evidence/(name+'.stdout')).open('xb');err=(self.evidence/(name+'.stderr')).open('xb');self.handles.extend([out,err])
            argv=[sys.executable,'-I','-B',str(script),str(worker),str(signals),name]
            p=subprocess.Popen(argv,cwd=worker,stdout=out,stderr=err);self.children.append(p)
            self.events[name]={'argv':argv,'pid':p.pid,'pgid':fixture_pgid(p.pid)}
        def await_both(event):
            deadline=time.monotonic()+180
            while not all((signals/name/(event+'.json')).exists() for name in workers):
                self.assertTrue(all(p.poll() is None for p in self.children));self.assertLess(time.monotonic(),deadline);time.sleep(.01)
            self.assertTrue(all(p.poll() is None for p in self.children))
        await_both('ready');self.assertNotEqual(self.children[0].pid,self.children[1].pid)
        (signals/'compute').write_text('go');await_both('computed');(signals/'finish').write_text('finish')
        for p in self.children:self.assertEqual(0,p.wait(timeout=10))
        self.assertEqual(control_before_compute,exact_snapshot(self.target))
        for name,worker in workers.items():
            self.events[name]['signals']={event:json.loads((signals/name/(event+'.json')).read_text()) for event in ('ready','computed')}
            self.assertEqual(authority[name],exact_snapshot(worker/'.hrn'))
            self.git(worker,'add','a');self.git(worker,'commit','-qm','synthetic independent '+name)
            self.assertEqual('',self.git(worker,'status','--porcelain','--untracked-files=all'))
            oid=self.git(worker,'rev-parse','HEAD');self.git(self.target,'branch','candidate-'+name+'-v1',oid)
            manifest=self.manifest(base,self.observe(worker),base_oid,oid,'base-start','candidate-'+name+'-v1')
            self.publish('work-a' if name=='alpha' else 'work-b','submit-result',manifest,worker=worker)
        tickets={wid:self.prepare(wid) for wid in ('work-a','work-b')}
        completed_a=self.apply(tickets['work-a']);self.assertEqual('completed',completed_a['state'])
        self.assertEqual(initial.replace('alpha = 0','alpha = 1'),(self.target/'a').read_text())
        before=exact_snapshot(self.target);error=self.apply(tickets['work-b'],expected=65)
        self.assertEqual('HV2-WORK-RECORD',error['code']);self.assertIn('worker recovery blocked',error['message'])
        self.assertEqual(before,exact_snapshot(self.target));self.assertEqual('review',read_work(self.target,'work-b')['state'])
        self.git(self.target,'add','.');self.git(self.target,'commit','-qm','operator records accepted A')
        after_a_oid=self.git(self.target,'rev-parse','HEAD');self.git(self.target,'branch','base-after-a',after_a_oid)
        after_a=self.observe(self.target)
        refresh=self.manifest(after_a,after_a,after_a_oid,after_a_oid,'base-after-a','base-after-a')
        b_before=read_work(self.target,'work-b')['current'];revision,_=self.publish('work-b','rebind',refresh)
        self.assertEqual(b_before,read_work(self.target,'work-b')['current'])
        review=self.installed(['view','work','work-b']).stdout.decode();self.assertIn('baseline',review.lower())
        refresh_ticket=self.prepare('work-b','rebind',revision);refreshed=self.apply(refresh_ticket)
        self.assertEqual('active',refreshed['state']);self.assertEqual(after_a,self.observe(self.target))
        # This separate operator commit contains only records. Content equality,
        # not HEAD equality, must govern the later worker result acceptance.
        self.git(self.target,'add','.');self.git(self.target,'commit','-qm','operator records B baseline review')
        records_oid=self.git(self.target,'rev-parse','HEAD');self.assertNotEqual(after_a_oid,records_oid)
        self.assertEqual(after_a,self.observe(self.target))
        beta=workers['beta'];self.git(beta,'-c','maintenance.auto=false','-c','gc.auto=0','rebase','--onto',after_a_oid,base_oid)
        expected=initial.replace('alpha = 0','alpha = 1').replace('beta = 0','beta = 1')
        self.assertEqual(expected,(beta/'a').read_text())
        expected_path=self.evidence/'expected-result.txt';expected_path.write_text(expected, newline='\n')
        retest=self.evidence/'retest.py';retest.write_text(RETEST)
        command=[sys.executable,'-I','-B',str(retest),str(beta),str(expected_path)]
        checked=subprocess.run(command,capture_output=True,cwd=beta,timeout=30);self.record(checked,'synthetic-retest',cwd=beta);self.assertEqual(0,checked.returncode)
        candidate=self.git(beta,'rev-parse','HEAD');self.git(self.target,'branch','candidate-beta-v2',candidate)
        revised=self.manifest(after_a,self.observe(beta),after_a_oid,candidate,'base-after-a','candidate-beta-v2')
        self.publish('work-b','submit-result',revised,worker=beta)
        before=exact_snapshot(self.target);obsolete=self.apply(tickets['work-b'],expected=65)
        self.assertIn('stale confirmation selection',obsolete['message']);self.assertEqual(before,exact_snapshot(self.target))
        fresh=self.prepare('work-b');completed_b=self.apply(fresh);self.assertEqual('completed',completed_b['state'])
        self.assertEqual(expected,(self.target/'a').read_text());self.assertEqual(self.observe(beta),self.observe(self.target))
        self.assertEqual(records_oid,self.git(self.target,'rev-parse','HEAD'))
        self.assertEqual(completed_a,read_work(self.target,'work-a'))
        before=exact_snapshot(self.target);self.apply(tickets['work-a']);self.apply(fresh)
        self.assertEqual(before,exact_snapshot(self.target))
        self.events['outcome']={'base_commit':base_oid,'after_a_commit':after_a_oid,'record_only_commit':records_oid,'candidate_b_commit':candidate,'same_file':'a','worker_authority_unchanged':True,'control_unchanged_during_compute':True,'workers_clean_after_commit':True,'stale_apply_refused':True,'refresh_not_auto_selected':True,'record_only_continuation':True,'a_history_preserved':True,'git_unchanged_by_apply':True,'replay_unchanged':True,'final_content_sha256':hashlib.sha256(expected.encode()).hexdigest()}
        (self.evidence/'final-graphs.json').write_text(json.dumps({'a':completed_a,'b':completed_b},indent=2)+'\n')
        self.success=True
