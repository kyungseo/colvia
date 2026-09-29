"""Installed pending-worker admission and exact active-release repair boundary."""
from __future__ import annotations
import copy
import hashlib
import json
from pathlib import Path
import shutil
import unittest

from hv2ref.jsonio import canonical_json_bytes
from hv2ref.product import SERIAL_MANAGED_PATHS, verify_workspace_product
from hv2ref.work import read_work
from test_productization_safety import exact_snapshot
import test_worktree_execution as fixtures
import test_worktree_process_recovery as crash


class InstalledPendingLifecycleTests(unittest.TestCase):
    TIME=fixtures.InstalledWorkerPublicationTests.TIME
    git=fixtures.InstalledWorkerPublicationTests.git
    installed=fixtures.InstalledWorkerPublicationTests.installed
    preview=fixtures.InstalledWorkerPublicationTests.preview
    accept_intent=fixtures.InstalledWorkerPublicationTests.accept_intent
    draft=fixtures.InstalledWorkerPublicationTests.draft
    prepare_worker_result=fixtures.InstalledWorkerPublicationTests.prepare_worker_result
    run_interruption=crash.InstalledWorkerInterruptionTests.run_interruption

    def setUp(self):
        fixtures.InstalledWorkerPublicationTests.setUp(self)
        self.command_evidence=self.base.parent/('worker-pending-evidence-'+self.base.name)
        self.command_evidence.mkdir();self.command_records=[]
        self.addCleanup(self.preserve_commands)

    def preserve_commands(self):
        (self.command_evidence/'commands.json').write_text(json.dumps(self.command_records,indent=2)+'\n')
        backup=self.base/'repair-backup'
        if backup.exists():shutil.copytree(backup,self.command_evidence/'repair-backup')
        self.assertTrue(all(r['returncode'] in (0,65) for r in self.command_records))

    def call(self,command,value=None,*,env=None,launcher=None,expected=0):
        result=fixtures.InstalledWorkerPublicationTests.call(self,command,value,env=env,launcher=launcher,expected=None)
        index=len(self.command_records);stem=f'{index:02d}'
        (self.command_evidence/(stem+'.stdout')).write_bytes(result.stdout)
        (self.command_evidence/(stem+'.stderr')).write_bytes(result.stderr)
        record={'argv':list(map(str,result.args)),'cwd':str(self.target),'returncode':result.returncode,
                'stdout_sha256':hashlib.sha256(result.stdout).hexdigest(),'stderr_sha256':hashlib.sha256(result.stderr).hexdigest()}
        if value is not None:
            data=canonical_json_bytes(value);(self.command_evidence/(stem+'.input.json')).write_bytes(data)
            record['input_sha256']=hashlib.sha256(data).hexdigest()
        self.command_records.append(record)
        if expected is not None:self.assertEqual(expected,result.returncode,(result.stdout+result.stderr).decode(errors='replace'))
        return result

    def apply_init(self,preview):
        result=fixtures.InstalledWorkerPublicationTests.apply_init(self,preview)
        self.qsource=self.base/'source-q'
        for name in SERIAL_MANAGED_PATHS:
            dest=self.qsource/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(self.source/name,dest)
        with (self.qsource/'docs/REFERENCE.md').open('a') as f:f.write('\nFixture Q documentation marker.\n')
        preview=json.loads(self.installed(['update','--source',self.qsource,'--operation-id','install-q','--observed-at',self.TIME]).stdout)
        self.installed(['update','--source',self.qsource,'--apply','--input','-','--confirm',preview['confirm_token']],preview['request'])
        binding=json.loads((self.target/'.hrn/product/binding.json').read_text())
        self.assertIsNotNone(binding['prior_release']);self.assertNotEqual(binding['prior_release'],binding['active_release'])
        return result

    def before_pending(self,prepared):
        self.lifecycle_previews={}
        before=exact_snapshot(self.target)
        for action in ('update','rollback','detach'):
            args=[action,'--operation-id','pending-'+action,'--observed-at',self.TIME]
            if action=='update':args+=['--source',self.source]
            preview=json.loads(self.installed(args).stdout)
            self.assertEqual('preview',preview['classification'])
            self.lifecycle_previews[action]=(args,preview)
        self.assertEqual(before,exact_snapshot(self.target))

    def after_pending(self,prepared,observations):
        refused=[]
        def refuse(name,args,value=None,*,message,source=False):
            before=exact_snapshot(self.target)
            result=self.call(args,value,expected=65) if source else self.installed(args,value,expected=65)
            error=json.loads(result.stdout)
            self.assertEqual(before,exact_snapshot(self.target))
            self.assertIn(message,error['message'])
            refused.append({'operation':name,'code':error['code'],'message':error['message'],'target_unchanged':True})
        graph=read_work(self.target,'work-a')
        identity=copy.deepcopy(graph['identity']);identity['work_id']='work-b'
        revision=copy.deepcopy(graph['revisions']['start']);revision['work_id']='work-b'
        manifest=graph['manifests'][revision['result_refs']['manifest']['id']]
        refuse('new-work',['work','publish'],{'identity':identity,'revision':revision,'manifest':manifest,'selection_id':'other-start-s','operation_id':'other-start-op'},message='worker publication pending' if graph['pending_selections'] else 'worker pending blocks project mutation')
        draft=self.draft();draft.update(intent_id='intent-b',revision_id='draft-b')
        refuse('new-intent',['intent','draft'],draft,message='pending Work blocks intent mutation')
        for action,(args,preview) in self.lifecycle_previews.items():
            refuse(action+'-preview',args,message='pending Work blocks lifecycle')
            apply=[action,'--apply','--input','-','--confirm',preview['confirm_token']]
            if action=='update':apply+=['--source',self.source]
            refuse(action+'-apply',apply,preview['request'],message='pending Work blocks lifecycle')
        observations['pending_refusals']=refused
        healthy=exact_snapshot(self.target)
        binding=(self.target/'.hrn/product/binding.json').read_bytes()
        truth={'work':exact_snapshot(self.target/'.hrn/work'),'intents':exact_snapshot(self.target/'.hrn/intents')}
        product=verify_workspace_product(self.target)
        damaged=Path(product['release_path'])/'payload/docs/REFERENCE.md';original=damaged.read_bytes()
        damaged.write_bytes(b'fixture managed document damage\n')
        refuse('wrong-release-repair',['repair','--target',self.target,'--source',self.source,'--backup',self.base/'wrong-backup','--operation-id','wrong-repair','--observed-at',self.TIME],message='repair requires the exact active release',source=True)
        self.assertFalse((self.base/'wrong-backup').exists())
        preview=json.loads(self.call(['repair','--target',self.target,'--source',self.qsource,'--backup',self.base/'repair-backup','--operation-id','exact-repair','--observed-at',self.TIME]).stdout)
        self.assertEqual('preview',preview['classification'])
        request=preview['request'];self.assertEqual(1,len(request['files']))
        repaired=json.loads(self.call(['repair','--target',self.target,'--source',self.qsource,'--apply','--input','-','--confirm',preview['confirm_token']],request).stdout)
        self.assertEqual('repaired',repaired['classification'])
        self.assertEqual(original,damaged.read_bytes());self.assertEqual(binding,(self.target/'.hrn/product/binding.json').read_bytes())
        self.assertEqual(truth,{'work':exact_snapshot(self.target/'.hrn/work'),'intents':exact_snapshot(self.target/'.hrn/intents')})
        self.assertEqual(healthy,exact_snapshot(self.target));self.assertEqual(product,verify_workspace_product(self.target))
        saved=self.base/'repair-backup/original'/damaged.relative_to(self.target)
        self.assertEqual(b'fixture managed document damage\n',saved.read_bytes())
        repair_receipt=json.loads((self.base/'repair-backup/receipt.json').read_text())
        self.assertEqual(repair_receipt['prior_binding_ref'],repair_receipt['result_binding_ref'])
        observations['exact_repair']={'same_binding':True,'truth_unchanged':True,'target_restored':True,'original_damage_backed_up':True,'different_release_refused':True}
        # The shared interruption fixture resumes this same ticket and checks
        # completion, exact bytes, replay and the complete Git snapshot afterward.

    def test_pending_selection_blocks_other_writers_and_exact_repair_preserves_ticket(self):
        self.run_interruption('after-selection')

    def test_pending_worker_blocks_other_writers_and_exact_repair_preserves_ticket(self):
        self.run_interruption('after-decision')
