"""Installed schema2 round trip and exact old/new inventory membership.

Synthetic private fixture only. The plain readers verify a bounded reference
chain/byte subset, not the complete umbrella acceptance contract.
"""
from __future__ import annotations
from test_productization_safety import verified_inventory_id
import copy
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import unittest
from hv2ref.errors import ContractError
from hv2ref.jsonio import canonical_json_bytes
from hv2ref.intent import workspace_intents
from hv2ref.product import (ENTRY_MANAGED_PATHS, SERIAL_MANAGED_PATHS, UMBRELLA_MANAGED_PATHS, LEGACY_MANAGED_PATHS, _serial_inventory,
                           _launcher_inventory_window, verify_workspace_product, _switch_binding_receipt)
from hv2ref.work import WorkStore, read_work, record_ref, snapshot, make_manifest
from hv2ref.umbrella import capture
import test_productization_safety as fixtures
import test_general_work_invariants as intent_fixtures


def digest(value):return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


class UmbrellaInventoryTests(unittest.TestCase):
    def test_windows_require_their_own_exact_membership(self):
        for window,paths in [('human-1',LEGACY_MANAGED_PATHS),('worker-1',LEGACY_MANAGED_PATHS),('umbrella-1',UMBRELLA_MANAGED_PATHS),('planning-1',SERIAL_MANAGED_PATHS),('checkout-1',SERIAL_MANAGED_PATHS),('entry-1',ENTRY_MANAGED_PATHS),('delegation-1',ENTRY_MANAGED_PATHS)]:
            value={'record_type':'release-inventory','schema_version':1,'inventory_id':window,
                   'entries':[{'path':p,'sha256':'a'*64,'size_bytes':1} for p in paths]}
            self.assertEqual(value,_serial_inventory(value))
            wrong=copy.deepcopy(value)
            wrong['inventory_id']='worker-1' if window in ('umbrella-1','planning-1','checkout-1','entry-1','delegation-1') else 'planning-1'
            with self.assertRaises(ContractError):_serial_inventory(wrong)
        self.assertEqual(27,len(LEGACY_MANAGED_PATHS));self.assertEqual(28,len(UMBRELLA_MANAGED_PATHS));self.assertEqual(29,len(SERIAL_MANAGED_PATHS))

    def test_old_window_is_read_only_and_all_downgrades_refuse(self):
        self.assertEqual('worker-1',_launcher_inventory_window(b'WORKSPACE_INVENTORY_ID = "worker-1"',allow_legacy=True))
        with self.assertRaises(ContractError):_launcher_inventory_window(b'WORKSPACE_INVENTORY_ID = "worker-1"')
        for old,new in [('delegation-1','entry-1'),('entry-1','checkout-1'),('delegation-1','checkout-1'),('checkout-1','planning-1'),('planning-1','umbrella-1'),('planning-1','worker-1'),('worker-1','human-1'),('umbrella-1','worker-1'),('umbrella-1','human-1')]:
            prior={'record_type':'product-binding','schema_version':1,'authority_home_id':'home-a','operation_id':'p',
                   'active_release':{'id':'product-release-'+'a'*24,'sha256':'a'*64,'inventory_id':old},'prior_release':None}
            plan={'expected_binding_ref':record_ref(prior,'operation_id'),'candidate_release':{'id':'product-release-'+'b'*24,'sha256':'b'*64,'inventory_id':new},'action':'update','authority_home_id':'home-a','operation_id':'q'}
            with self.assertRaisesRegex(ContractError,'cannot downgrade'):_switch_binding_receipt(plan,prior)


class InstalledUmbrellaLifecycleTests(unittest.TestCase):
    TIME=fixtures.ActualWorkspaceInitTests.TIME
    preview=fixtures.ActualWorkspaceInitTests.preview
    apply_init=fixtures.ActualWorkspaceInitTests.apply_init
    installed=fixtures.ActualWorkspaceInitTests.installed
    draft=intent_fixtures.IntentWriterTests.draft

    def setUp(self):
        fixtures.ActualWorkspaceInitTests.setUp(self)
        self.serial=0;self.log=[];self.success=False
        self.evidence=self.base.parent/('umbrella-installed-evidence-'+self.base.name);self.evidence.mkdir()
        self.addCleanup(self.preserve)

    def preserve(self):
        (self.evidence/'commands.json').write_text(json.dumps(self.log,indent=2)+'\n')
        with tarfile.open(self.evidence/'fixture.tar.gz','w:gz') as t:t.add(self.base,arcname='fixture')
        (self.evidence/'outcome.json').write_text(json.dumps({'success':self.success,'commands':len(self.log)})+'\n')

    def call(self,args,value=None,**kw):
        p=fixtures.ActualWorkspaceInitTests.call(self,args,value,expected=None,**{k:v for k,v in kw.items() if k!='expected'})
        n=str(len(self.log));(self.evidence/(n+'.stdout')).write_bytes(p.stdout);(self.evidence/(n+'.stderr')).write_bytes(p.stderr)
        if value is not None:(self.evidence/(n+'.input.json')).write_bytes(canonical_json_bytes(value))
        self.log.append({'args':list(map(str,p.args)),'exit':p.returncode})
        self.assertEqual(kw.get('expected',0),p.returncode,(p.stdout+p.stderr).decode(errors='replace'))
        return p

    @staticmethod
    def q(kind,name):return {'authority_home_id':'home-a','kind':kind,'id':name}

    def accept(self,draft):
        self.installed(['intent','draft'],draft)
        request={'intent_id':draft['intent_id'],'revision_ref':record_ref(draft,'revision_id'),'actor':'owner','reason':'fixture','request_id':'accept-'+draft['intent_id']+'-'+draft['revision_id'],'observed_at':self.TIME}
        p=json.loads(self.installed(['intent','prepare'],request).stdout)
        g=json.loads(self.installed(['intent','apply','--confirm',p['confirm_token']],p['ticket']).stdout)
        s=g['selections'][g['current']['selection_ref']['id']]
        return {**self.q('intent',draft['intent_id']),'revision_ref':s['revision_ref'],'acceptance_ref':s['acceptance_ref'],'selection_ref':g['current']['selection_ref']}

    def publish(self,wid,intent,operation,*,parent=False,old_intent=None):
        self.serial+=1;rid='revision-'+str(self.serial)
        g=read_work(self.target,wid) if (self.target/'.hrn/work'/wid).exists() else None
        prior=g['current']['selection_ref'] if g and g['current'] else None
        old=g['revisions'][g['selections'][prior['id']]['revision_ref']['id']] if prior else None
        sha=verify_workspace_product(self.target)['launcher_sha256'];tree=snapshot(self.target,verified_launcher_sha256=sha, verified_inventory_id=verified_inventory_id(self.target))
        base=g['manifests'][old['result_refs']['manifest']['id']]['result'] if operation=='submit-result' else tree
        scope=['report.md'] if parent else ['a'];m=make_manifest(base,tree,scope=scope)
        identity={'record_type':'work-identity','schema_version':1,'authority_home_id':'home-a','work_id':wid,'work_type':'integration' if parent else 'change','created_at':self.TIME,'acceptance_authority':'owner','lineage':None}
        r={'record_type':'work-revision','schema_version':2 if parent else 1,'authority_home_id':'home-a','work_id':wid,'record_id':rid,'observed_at':self.TIME,'observed_scope':[],'unavailable_scope':[],'author':'agent','operation':operation,'expected_prior_selection':prior,'intent_ref':intent,'scope':scope,'document_refs':[],'evidence_refs':[],'result_refs':{'manifest':{'id':digest(m),'sha256':digest(m)}},'progress':'review' if operation=='submit-result' else 'active','next_action':'owner review','relations':[] if parent else [{'relation':'parent','target':self.q('work','parent')}],'rebind_from':old_intent,'execution_context':{'mode':'local','attempt_id':rid}}
        if parent:
            children=capture(self.composition,WorkStore(self.target)._all(),workspace_intents(self.target))['children'] if operation in ('start','rebind') else old['umbrella_evidence']['children']
            r['umbrella_evidence']={'children':children,'integration_document':'report.md' if operation=='submit-result' else None}
            if operation=='submit-result':
                sha=hashlib.sha256((self.target/'report.md').read_bytes()).hexdigest()
                r['document_refs']=[{'path':'report.md','sha256':sha,'required':True,'role':'result'}]
                r['evidence_refs']=[{'path':'report.md','sha256':sha,'required':True,'verification':'control-required'}]
        g=json.loads(self.installed(['work','publish'],{'identity':identity,'revision':r,'manifest':m,'selection_id':'s-'+rid,'operation_id':'o-'+rid}).stdout)
        return r,g

    def prepare(self,wid,action='accept',revision=None):
        self.serial+=1
        request={'work_id':wid,'action':action,'actor':'owner','reason':'fixture explicit acceptance','request_id':'human-'+str(self.serial),'observed_at':self.TIME,'revision_ref':record_ref(revision) if revision else None,'supersedes':None}
        return json.loads(self.installed(['work','prepare'],request).stdout)

    def apply(self,p,expected=0):
        return json.loads(self.installed(['work','apply','--confirm',p['confirm_token']],p['ticket'],expected=expected).stdout)

    def test_q_created_parent_on_p_then_detach_plain_refs_and_korean_view(self):
        (self.target/'report.md').write_text('pending verification\n')
        self.apply_init(self.preview());p_release=verify_workspace_product(self.target)['inventory']
        q=self.base/'candidate'
        for name in ENTRY_MANAGED_PATHS:
            dest=q/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(self.source/name,dest)
        with (q/'README.md').open('a') as f:f.write('\nSynthetic Q.\n')
        up=json.loads(self.installed(['update','--source',q,'--operation-id','up-q','--observed-at',self.TIME]).stdout)
        self.installed(['update','--source',q,'--apply','--input','-','--confirm',up['confirm_token']],up['request'])
        child=self.accept(self.draft())
        self.composition={'parent':self.q('work','parent'),'required_children':[{'work':self.q('work',n),'intent':self.q('intent','intent-a')} for n in ('child-a','child-b')]}
        draft={**self.draft(intent_id='parent-intent'),'schema_version':2,'composition':self.composition};parent=self.accept(draft)
        self.publish('parent',parent,'start',parent=True)
        for wid in ('child-a','child-b'):
            self.publish(wid,child,'start');(self.target/'a').write_text(wid+' result\n')
            self.publish(wid,child,'submit-result');self.apply(self.prepare(wid))
        second={**self.draft(2,intent_id='parent-intent',prior=draft),'schema_version':2,'composition':self.composition}
        refreshed=self.accept(second);r,g=self.publish('parent',refreshed,'rebind',parent=True,old_intent=parent)
        self.apply(self.prepare('parent','rebind',r))
        verify=subprocess.run([sys.executable,'-I','-B','-c','from pathlib import Path; import sys; assert Path(sys.argv[1]).read_text() == "child-b result\\n"; print("combined fixture content verified")',str(self.target/'a')],capture_output=True,timeout=20)
        self.assertEqual(0,verify.returncode,verify.stderr)
        children=capture(self.composition,WorkStore(self.target)._all(),workspace_intents(self.target))['children']
        (self.target/'report.md').write_text('# 통합 검증\n\n'+verify.stdout.decode()+'\n'+json.dumps({'command':verify.args,'exit':verify.returncode,'children':children},ensure_ascii=False,indent=2)+'\n')
        self.publish('parent',refreshed,'submit-result',parent=True);old_ticket=self.prepare('parent')
        down=json.loads(self.installed(['rollback','--operation-id','back-p','--observed-at',self.TIME]).stdout)
        self.installed(['rollback','--apply','--input','-','--confirm',down['confirm_token']],down['request'])
        self.assertEqual(p_release,verify_workspace_product(self.target)['inventory'])
        before=fixtures.exact_snapshot(self.target);self.apply(old_ticket,expected=65);self.assertEqual(before,fixtures.exact_snapshot(self.target))
        fresh=self.prepare('parent');g=self.apply(fresh);self.assertEqual('completed',g['state'])
        self.assertTrue(all(s['schema_version']==1 for s in g['selections'].values()))
        before=fixtures.exact_snapshot(self.target);view=self.installed(['view','work','parent']).stdout.decode()
        self.assertIn('상위 작업과 필수 하위 작업',view);self.assertIn('충족',view);self.assertIn('child-a',view);self.assertEqual(before,fixtures.exact_snapshot(self.target))
        self.installed(['view','confirmation','--input','-'],fresh['ticket'])
        preview=json.loads(self.installed(['detach','--operation-id','detach-p','--observed-at',self.TIME]).stdout)
        self.installed(['detach','--apply','--input','-','--confirm',preview['confirm_token']],preview['request'])
        self.assertEqual('completed',WorkStore(self.target)._all()['parent']['state'])
        for script,args in [('intent_plain_auditor.py',[str(self.target),'parent-intent']),('product_plain_auditor.py',[str(self.target)])]:
            result=subprocess.run([sys.executable,'-I','-B',str(self.source/'tests/fixtures'/script),*args],capture_output=True,timeout=30)
            (self.evidence/(script+'.stdout')).write_bytes(result.stdout);(self.evidence/(script+'.stderr')).write_bytes(result.stderr)
            self.assertEqual(0,result.returncode,result.stdout+result.stderr)
        self.success=True


    def test_detach_missing_umbrella_member_refuses_apply_and_resume(self):
        from hv2ref.product import workspace_detach_preview,workspace_detach_apply,workspace_detached_status,_detach_receipt
        from hv2ref.errors import InjectedCrash
        for module,apply_error,recover_error in [('umbrella','detach incomplete removal/binding set','detach incomplete removal/binding set'),('candidates','detach incomplete removal/binding set','detach incomplete removal/binding set')]:
            self.target=self.base/('missing-'+module);self.target.mkdir();self.apply_init(self.preview())
            preview=workspace_detach_preview(self.target,operation_id='detach-membership',created_at=self.TIME)
            plan=preview['request'];bad=copy.deepcopy(plan)
            bad['remove']=[entry for entry in bad['remove'] if not entry['path'].endswith('/payload/src/hv2ref/'+module+'.py')]
            before=fixtures.exact_snapshot(self.target)
            with self.assertRaisesRegex(ContractError,apply_error):
                workspace_detach_apply(self.target,bad,confirm_token=digest(bad)[:16])
            self.assertEqual(before,fixtures.exact_snapshot(self.target))
            with self.assertRaises(InjectedCrash):
                workspace_detach_apply(self.target,plan,confirm_token=preview['confirm_token'],inject_at='after-receipt')
            # Deliberately damaged synthetic receipt: a required module is unplanned.
            (self.target/'.hrn/detached.json').write_bytes(canonical_json_bytes(_detach_receipt(bad)))
            before=fixtures.exact_snapshot(self.target)
            with self.assertRaisesRegex(ContractError,recover_error):workspace_detached_status(self.target)
            with self.assertRaisesRegex(ContractError,recover_error):
                workspace_detach_apply(self.target,bad,confirm_token=digest(bad)[:16],recover=True)
            self.assertEqual(before,fixtures.exact_snapshot(self.target))
        self.success=True
