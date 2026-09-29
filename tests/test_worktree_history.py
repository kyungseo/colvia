"""Installed P -> Q -> P with Q-created worker and local records.

Q differs only in a managed document; this tests the present window contract,
not compatibility with an arbitrary future release.
"""
from __future__ import annotations
import copy
import hashlib
import json
import unittest
from hv2ref.jsonio import canonical_json_bytes
from hv2ref.product import verify_workspace_product
from hv2ref.work import make_manifest,read_work,snapshot
from test_productization_safety import exact_snapshot
import test_worktree_execution as execution
import test_worktree_integration as integration
import test_worktree_pending_lifecycle as pending


class InstalledWorkerHistoryTests(unittest.TestCase):
    TIME=execution.InstalledWorkerPublicationTests.TIME
    setUp=integration.InstalledTwoWorkerIntegrationTests.setUp
    preserve=integration.InstalledTwoWorkerIntegrationTests.preserve
    record=integration.InstalledTwoWorkerIntegrationTests.record
    call=integration.InstalledTwoWorkerIntegrationTests.call
    git=integration.InstalledTwoWorkerIntegrationTests.git
    installed=execution.InstalledWorkerPublicationTests.installed
    preview=execution.InstalledWorkerPublicationTests.preview
    draft=execution.InstalledWorkerPublicationTests.draft
    accept_intent=execution.InstalledWorkerPublicationTests.accept_intent
    apply_init=pending.InstalledPendingLifecycleTests.apply_init
    prepare_worker_result=execution.InstalledWorkerPublicationTests.prepare_worker_result
    prepare=integration.InstalledTwoWorkerIntegrationTests.prepare
    apply=integration.InstalledTwoWorkerIntegrationTests.apply

    def truth(self):
        return {name:exact_snapshot(self.target/'.hrn'/name) for name in ['intents','work']}

    def local_review(self):
        worker=read_work(self.target,'work-a')
        identity=copy.deepcopy(worker['identity']);identity['work_id']='local-q'
        sha=verify_workspace_product(self.target)['launcher_sha256']
        tree=snapshot(self.target,verified_launcher_sha256=sha)
        manifest=make_manifest(tree,tree,scope=[])
        digest=hashlib.sha256(canonical_json_bytes(manifest)).hexdigest();prior=None
        for number,operation in [(1,'start'),(2,'submit-result')]:
            revision=copy.deepcopy(worker['revisions']['start'])
            revision.update(work_id='local-q',record_id='local-'+str(number),operation=operation,expected_prior_selection=prior,scope=[],progress='active' if number==1 else 'review',execution_context={'mode':'local','attempt_id':'local-'+str(number)},result_refs={'manifest':{'id':digest,'sha256':digest}})
            result=json.loads(self.installed(['work','publish'],{'identity':identity,'revision':revision,'manifest':manifest,'selection_id':'local-s-'+str(number),'operation_id':'local-op-'+str(number)}).stdout)
            prior=result['current']['selection_ref']
        return result

    def test_q_created_worker_and_local_survive_rollback_and_continue_before_detach(self):
        old_worker_ticket=self.prepare_worker_result()  # Includes real P -> Q.
        binding_q=json.loads((self.target/'.hrn/product/binding.json').read_text())
        self.assertEqual('worker-1',binding_q['active_release']['inventory_id'])
        local_q=self.local_review();worker_q=read_work(self.target,'work-a')
        truth_q=self.truth();git_q=exact_snapshot(self.target/'.git')
        preview=json.loads(self.installed(['rollback','--operation-id','back-to-p','--observed-at',self.TIME]).stdout)
        self.installed(['rollback','--apply','--input','-','--confirm',preview['confirm_token']],preview['request'])
        binding_p=json.loads((self.target/'.hrn/product/binding.json').read_text())
        self.assertEqual(binding_q['prior_release'],binding_p['active_release'])
        self.assertEqual(truth_q,self.truth());self.assertEqual(git_q,exact_snapshot(self.target/'.git'))
        self.assertEqual(local_q,read_work(self.target,'local-q'));self.assertEqual(worker_q,read_work(self.target,'work-a'))
        before=exact_snapshot(self.target)
        for wid in ['work-a','local-q']:
            view=self.installed(['view','work',wid]).stdout.decode();self.assertIn(wid,view)
        self.assertEqual('pass',json.loads(self.installed(['status']).stdout)['classification'])
        self.assertEqual(before,exact_snapshot(self.target))
        error=self.apply(old_worker_ticket,expected=65)
        self.assertIn('active binding changed',error['message']);self.assertEqual(before,exact_snapshot(self.target))
        local_ticket=self.prepare('local-q');completed_local=self.apply(local_ticket)
        self.assertEqual('completed',completed_local['state'])
        fresh=self.prepare('work-a');completed_worker=self.apply(fresh)
        self.assertEqual('completed',completed_worker['state']);self.assertEqual(b'installed worker result\n',(self.target/'a').read_bytes())
        self.assertEqual(completed_local,read_work(self.target,'local-q'))
        before=exact_snapshot(self.target);self.apply(local_ticket);self.apply(fresh)
        self.assertEqual(before,exact_snapshot(self.target));self.assertEqual(git_q,exact_snapshot(self.target/'.git'))
        truth_p=self.truth();content=(self.target/'a').read_bytes()
        preview=json.loads(self.installed(['detach','--operation-id','detach-p','--observed-at',self.TIME]).stdout)
        self.installed(['detach','--apply','--input','-','--confirm',preview['confirm_token']],preview['request'])
        self.assertEqual(truth_p,self.truth());self.assertEqual(content,(self.target/'a').read_bytes())
        self.assertEqual(git_q,exact_snapshot(self.target/'.git'))
        self.assertEqual(completed_local,read_work(self.target,'local-q'));self.assertEqual(completed_worker,read_work(self.target,'work-a'))
        status=json.loads(self.call(['status','--target',self.target]).stdout)
        self.assertEqual('detached',status['classification'])
        self.events['history']={'q_active':binding_q['active_release'],'p_active':binding_p['active_release'],'truth_unchanged_by_rollback':True,'old_binding_ticket_refused':True,'q_local_completed_on_p':True,'q_worker_completed_on_p':True,'historical_replay_unchanged':True,'git_unchanged':True,'detach_truth_preserved':True,'detached_graphs_readable':True,'q_change':'managed document only'}
        (self.evidence/'final-graphs.json').write_text(json.dumps({'local':completed_local,'worker':completed_worker},indent=2)+'\n')
        self.success=True
