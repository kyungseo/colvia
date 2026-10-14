"""Schema2 writer and local recovery tests; bound runtime is a fixture double."""
from __future__ import annotations
import copy
import hashlib
import unittest
from hv2ref.errors import ContractError, InjectedCrash
from hv2ref.intent import WorkspaceIntentStore, workspace_intents
from hv2ref.work import WorkStore, read_work, record_ref
from hv2ref.umbrella import capture
import test_general_work_invariants as fixtures


class UmbrellaWriterTests(unittest.TestCase):
    proposal=fixtures.IntentWriterTests.proposal
    publish=fixtures.IntentWriterTests.publish
    prepare=fixtures.IntentWriterTests.prepare
    apply=fixtures.IntentWriterTests.apply
    bytes=fixtures.IntentWriterTests.bytes
    draft=fixtures.IntentWriterTests.draft
    accept=fixtures.IntentWriterTests.accept
    iprepare=fixtures.IntentWriterTests.iprepare
    iapply=fixtures.IntentWriterTests.iapply

    def setUp(self):
        fixtures.IntentWriterTests.setUp(self)
        runtime=lambda target:{'binding_ref':copy.deepcopy(self.binding),'launcher_sha256':None,'inventory_id':'umbrella-1'}
        self.store=WorkStore(self.target,runtime);self.intents=WorkspaceIntentStore(self.target,runtime)
        self.accept();self.child_intent=copy.deepcopy(self.intent)
        self.composition={'parent':self.q('work','parent'),'required_children':[
            {'work':self.q('work',wid),'intent':self.q('intent','intent-a')} for wid in ('child-a','child-b')]}
        self.parent_draft={**self.draft(intent_id='parent-intent'),'schema_version':2,'composition':self.composition}
        self.accept(self.parent_draft);self.parent_intent=copy.deepcopy(self.intent)
        self.identity={**self.identity,'work_id':'parent'}
        self.publish(self.parent_proposal())

    @staticmethod
    def q(kind,name):return {'authority_home_id':'home-a','kind':kind,'id':name}

    def choose(self,wid):
        self.identity={**self.identity,'work_id':wid}
        self.intent=copy.deepcopy(self.parent_intent if wid=='parent' else self.child_intent)

    def parent_proposal(self,op='start',**kw):
        value=self.proposal(op,**kw);r=value[0];r['schema_version']=2
        if op in ('start','rebind'):
            children=capture(self.composition,self.store._all(),workspace_intents(self.target))['children']
        else:
            g=read_work(self.target,'parent');old=g['revisions'][g['selections'][g['current']['selection_ref']['id']]['revision_ref']['id']]
            children=old['umbrella_evidence']['children']
        r['umbrella_evidence']={'children':copy.deepcopy(children),'integration_document':'a' if op=='submit-result' else None}
        if op=='submit-result':
            sha=hashlib.sha256((self.target/'a').read_bytes()).hexdigest()
            r['document_refs']=[{'path':'a','sha256':sha,'required':True,'role':'result'}]
            r['evidence_refs']=[{'path':'a','sha256':sha,'required':True,'verification':'control-required'}]
        return value

    def children(self):
        for wid in ('child-a','child-b'):
            self.choose(wid)
            for op in ('start','submit-result'):
                if op=='submit-result':(self.target/'a').write_text(wid+' result\n')
                p=self.proposal(op);p[0]['relations']=[{'relation':'parent','target':self.q('work','parent')}];self.publish(p)
            self.apply(self.prepare())
        self.choose('parent')

    def refresh(self):
        old=copy.deepcopy(self.parent_intent)
        draft={**self.draft(2,intent_id='parent-intent',prior=self.parent_draft),'schema_version':2,'composition':self.composition}
        self.accept(draft);self.parent_intent=copy.deepcopy(self.intent)
        p=self.parent_proposal('rebind',old_intent=old);self.publish(p)
        self.apply(self.prepare('rebind',revision_ref=record_ref(p[0])))
        return p

    def submitted_parent(self):
        self.children();self.refresh();self.publish(self.parent_proposal('submit-result'))

    def test_schema2_parent_completes_with_v1_selector_and_ticket(self):
        self.submitted_parent();p=self.prepare();self.assertEqual(1,p['ticket']['schema_version'])
        g=self.apply(p);self.assertEqual('completed',g['state'])
        self.assertEqual({1},{s['schema_version'] for s in g['selections'].values()})
        self.assertEqual(1,g['current']['schema_version']);before=self.bytes();self.apply(p);self.assertEqual(before,self.bytes())

    def test_missing_children_and_replaced_baseline_refuse_before_writes(self):
        before=self.bytes()
        with self.assertRaises(ContractError):self.publish(self.parent_proposal('submit-result'))
        self.assertEqual(before,self.bytes());self.children()
        p=self.parent_proposal('submit-result');p[0]['umbrella_evidence']['children']=capture(self.composition,self.store._all(),workspace_intents(self.target))['children']
        before=self.bytes()
        with self.assertRaises(ContractError):self.publish(p)
        self.assertEqual(before,self.bytes())

    def test_schema1_cannot_hide_composition_or_parent_role(self):
        p=self.proposal('checkpoint');before=self.bytes()
        with self.assertRaises(ContractError):self.publish(p)
        self.assertEqual(before,self.bytes())
        ordinary=self.draft(2,intent_id='parent-intent',prior=self.parent_draft)
        self.intents.publish_draft(ordinary);before=self.bytes()
        with self.assertRaises(ContractError):self.iprepare(ordinary)
        self.assertEqual(before,self.bytes())

    def test_ordinary_rebind_cannot_erase_selected_parent(self):
        p=self.proposal('rebind',intent=self.child_intent,old_intent=self.parent_intent);before=self.bytes()
        with self.assertRaises(ContractError):self.publish(p)
        self.assertEqual(before,self.bytes())

    def test_prepare_apply_child_intent_drift_refuses_and_reject_still_works(self):
        self.submitted_parent();p=self.prepare()
        first=workspace_intents(self.target)['intent-a']['drafts']['draft-1']
        self.accept(self.draft(2,prior=first));self.choose('parent');before=self.bytes()
        with self.assertRaises(ContractError):self.apply(p)
        self.assertEqual(before,self.bytes());self.assertEqual('rejected',self.apply(self.prepare('reject'))['state'])

    def test_parent_acceptance_prefixes_resume_and_block_other_local_writer(self):
        self.submitted_parent();p=self.prepare()
        for point in ('after-decision','after-selection','after-staged-current','after-current'):
            if point!='after-current':
                with self.assertRaises(InjectedCrash):self.apply(p,inject_at=point)
                self.choose('other');q=self.proposal();before=self.bytes()
                with self.assertRaises(ContractError):self.publish(q)
                self.assertEqual(before,self.bytes());self.choose('parent')
            else:
                with self.assertRaises(InjectedCrash):self.apply(p,inject_at=point)
        self.assertEqual('completed',self.apply(p)['state'])

    def test_pending_accept_can_cancel_before_selection_and_cannot_revive(self):
        self.submitted_parent();p=self.prepare()
        with self.assertRaises(InjectedCrash):self.apply(p,inject_at='after-decision')
        g=read_work(self.target,'parent');d=g['decisions'][g['pending_decisions'][0]]
        self.assertEqual('rejected',self.apply(self.prepare('reject',supersedes=record_ref(d)))['state'])
        before=self.bytes()
        with self.assertRaises(ContractError):self.apply(p)
        self.assertEqual(before,self.bytes())

    def test_history_keeps_completed_parent_after_child_revoke(self):
        self.submitted_parent();p=self.prepare();self.apply(p)
        self.choose('child-a');g=read_work(self.target,'child-a');s=g['selections'][g['current']['selection_ref']['id']]
        self.apply(self.prepare('revoke',supersedes=s['decision_ref']))
        self.assertEqual('completed',self.store._all()['parent']['state']);self.choose('parent')
        before=self.bytes();self.apply(p);self.assertEqual(before,self.bytes())

    def test_old_window_cannot_write_schema2_draft(self):
        old=WorkspaceIntentStore(self.target,lambda t:{'binding_ref':self.binding,'launcher_sha256':None})
        d={**self.draft(intent_id='new-parent'),'schema_version':2,'composition':self.composition};before=self.bytes()
        with self.assertRaisesRegex(ContractError,'umbrella-1'):old.publish_draft(d)
        self.assertEqual(before,self.bytes())

    def test_local_pending_parent_publication_blocks_other_work(self):
        p=self.parent_proposal('checkpoint')
        with self.assertRaises(InjectedCrash):self.publish(p,inject_at='after-selection')
        self.choose('other');before=self.bytes()
        with self.assertRaises(ContractError):self.publish(self.proposal())
        self.assertEqual(before,self.bytes());self.choose('parent');self.publish(p)
        self.choose('other');self.publish(self.proposal())

    def test_parent_pending_decision_and_selection_block_child_intent_accept(self):
        self.submitted_parent();p=self.prepare()
        first=workspace_intents(self.target)['intent-a']['drafts']['draft-1']
        draft=self.draft(2,prior=first);self.intents.publish_draft(draft);ip=self.iprepare(draft)
        for point in ('after-decision','after-selection'):
            with self.assertRaises(InjectedCrash):self.apply(p,inject_at=point)
            before=self.bytes()
            with self.assertRaisesRegex(ContractError,'pending Work blocks intent mutation'):self.iapply(ip)
            with self.assertRaisesRegex(ContractError,'pending Work blocks intent mutation'):self.iprepare(draft)
            self.assertEqual(before,self.bytes())
        self.assertEqual('completed',self.apply(p)['state'])

    def test_parent_accept_refuses_start_checkpoint_and_rework(self):
        for op in ('start','checkpoint','rework'):
            if op=='checkpoint':self.publish(self.parent_proposal(op))
            if op=='rework':
                self.submitted_parent();self.apply(self.prepare('reject'));self.publish(self.parent_proposal(op))
            before=self.bytes()
            with self.assertRaisesRegex(ContractError,'undecided submitted result'):self.prepare()
            self.assertEqual(before,self.bytes())

    def test_ordinary_writer_preserves_home_when_unrelated_intent_is_damaged(self):
        draft=self.draft(intent_id='unrelated');self.intents.publish_draft(draft)
        self.choose('ordinary');value=self.proposal()
        (self.target/'.hrn/intents/unrelated/drafts/draft-1.json').write_bytes(b'{damaged')
        before=self.bytes()
        with self.assertRaises(ContractError):self.publish(value)
        self.assertEqual(before,self.bytes())

    def test_entry_window_parent_capability_keeps_schema2_completion(self):
        # Capability double only; native entry execution has independent factory cases.
        runtime=lambda target:{'binding_ref':copy.deepcopy(self.binding),'launcher_sha256':None,'inventory_id':'entry-1'}
        self.store.runtime_check=runtime;self.intents.work_store.runtime_check=runtime
        self.test_schema2_parent_completes_with_v1_selector_and_ticket()


class UmbrellaWorkerRecoveryTests(unittest.TestCase):
    """Real Git worker content/prefixes; runtime verifier is a fixture double."""
    proposal=UmbrellaWriterTests.proposal
    publish=UmbrellaWriterTests.publish
    prepare=UmbrellaWriterTests.prepare
    apply=UmbrellaWriterTests.apply
    bytes=UmbrellaWriterTests.bytes
    draft=UmbrellaWriterTests.draft
    accept=UmbrellaWriterTests.accept
    iprepare=UmbrellaWriterTests.iprepare
    iapply=UmbrellaWriterTests.iapply
    q=staticmethod(UmbrellaWriterTests.q)
    choose=UmbrellaWriterTests.choose
    children=UmbrellaWriterTests.children
    def setUp(self):
        if self._testMethodName.startswith('test_worker_child_'):
            self.parent_scope=['a','input.md']
        UmbrellaWriterTests.setUp(self)
        self.addCleanup(self.preserve_fixture)

    def preserve_fixture(self):
        import tarfile
        evidence=self.target.parent.parent/('umbrella-worker-evidence-'+self.target.parent.name)
        evidence.mkdir()
        with tarfile.open(evidence/'fixture.tar.gz','w:gz') as archive:
            archive.add(self.target.parent,arcname='fixture')

    def git(self,*args,cwd=None):
        if args and args[0] == "commit":
            args = ("-c", "maintenance.auto=false", "-c", "gc.auto=0", *args)
        import subprocess
        from hv2ref.work import git_environment
        return subprocess.run(['git','-C',str(cwd or self.target),*args],capture_output=True,check=True,env=git_environment(),timeout=30).stdout.strip().decode()

    def parent_proposal(self,operation='start',**kw):
        from hv2ref.work import snapshot,make_manifest
        from test_general_work_recovery import digest
        if not (self.target/'.git').exists():
            self.git('init','-q');self.git('config','user.name','Fixture');self.git('config','user.email','fixture@example.invalid')
        value=UmbrellaWriterTests.parent_proposal(self,operation,**kw);r=value[0]
        r['execution_context']['mode']='isolated-worktree'
        r['scope']=getattr(self,'parent_scope',['a'])
        if operation in ('start','rebind'):
            self.git('add','.');self.git('commit','--allow-empty','-qm','synthetic parent baseline')
            oid=self.git('rev-parse','HEAD');ref='refs/heads/base-'+r['record_id'];self.git('branch',ref[11:],oid)
            tree=snapshot(self.target);m=make_manifest(tree,tree,scope=getattr(self,'parent_scope',['a']),base_commit=oid,candidate_commit=oid,base_retention_ref=ref,candidate_retention_ref=ref)
        else:
            m=self.candidate_manifest
            sha=hashlib.sha256((self.worker/'a').read_bytes()).hexdigest()
            r['document_refs']=[{'path':'a','sha256':sha,'required':True,'role':'result'}]
            r['evidence_refs']=[{'path':'a','sha256':sha,'required':True,'verification':'control-required'}]
        r['result_refs']['manifest']={'id':digest(m),'sha256':digest(m)}
        return r,m,value[2],value[3]

    def submitted_worker(self):
        from hv2ref.work import snapshot,make_manifest
        self.children()
        # Same accepted intent: the existing human worker baseline refresh.
        value=self.parent_proposal('rebind',old_intent=self.parent_intent);self.publish(value)
        self.apply(self.prepare('rebind',revision_ref=record_ref(value[0])))
        baseline=value[1];self.worker=self.target.parent/'parent-worker'
        self.git('worktree','add','-q','-b','parent-result',str(self.worker),baseline['base_commit'])
        self.assertEqual('child-b result\n',(self.worker/'a').read_text())
        (self.worker/'a').write_text('fixture integration result and evidence\n')
        self.git('add','a',cwd=self.worker);self.git('commit','-qm','synthetic parent report',cwd=self.worker)
        self.candidate_manifest=make_manifest(baseline['result'],snapshot(self.worker),scope=['a'],base_commit=baseline['base_commit'],candidate_commit=self.git('rev-parse','HEAD',cwd=self.worker),base_retention_ref=baseline['base_retention_ref'],candidate_retention_ref='refs/heads/parent-result')
        self.publish(self.parent_proposal('submit-result'),worker=self.worker)
        return self.prepare()

    def test_worker_parent_exact_file_application_and_prefix_resume(self):
        p=self.submitted_worker()
        for point in ('after-decision','after-staged-file','after-file','after-selection','after-staged-current','after-current'):
            with self.assertRaises(InjectedCrash):self.apply(p,inject_at=point)
            if point!='after-current':
                self.choose('other');before=self.bytes()
                with self.assertRaises(ContractError):self.publish(self.proposal())
                self.assertEqual(before,self.bytes());self.choose('parent')
        self.assertEqual('completed',self.apply(p)['state'])
        self.assertEqual('fixture integration result and evidence\n',(self.target/'a').read_text())

    def test_worker_cancel_refused_after_file(self):
        p=self.submitted_worker()
        with self.assertRaises(InjectedCrash):self.apply(p,inject_at='after-file')
        g=read_work(self.target,'parent');d=g['decisions'][g['pending_decisions'][0]];before=self.bytes()
        with self.assertRaises(ContractError):self.prepare('reject',supersedes=record_ref(d))
        self.assertEqual(before,self.bytes());self.assertEqual('completed',self.apply(p)['state'])

    def test_worker_required_child_input_drift_refuses_before_decision(self):
        p=self.submitted_worker();first=workspace_intents(self.target)['intent-a']['drafts']['draft-1']
        self.accept(self.draft(2,prior=first));self.choose('parent');before=self.bytes()
        with self.assertRaises(ContractError):self.apply(p)
        self.assertEqual(before,self.bytes())

    def test_worker_cancel_before_file_preserves_control_result(self):
        p=self.submitted_worker()
        with self.assertRaises(InjectedCrash):self.apply(p,inject_at='after-decision')
        g=read_work(self.target,'parent');d=g['decisions'][g['pending_decisions'][0]]
        self.assertEqual('rejected',self.apply(self.prepare('reject',supersedes=record_ref(d)))['state'])
        self.assertEqual('child-b result\n',(self.target/'a').read_text())

    def candidate_with_child_input(self, *, evidence=False):
        from hv2ref.work import snapshot,make_manifest
        self.parent_scope=['a','input.md']
        (self.target/'input.md').write_text('accepted child input\n')
        first=workspace_intents(self.target)['intent-a']['drafts']['draft-1']
        draft=self.draft(2,prior=first);self.intents.publish_draft(draft)
        ref={'path':'input.md','sha256':hashlib.sha256((self.target/'input.md').read_bytes()).hexdigest(),'required':True,'role':'brief'}
        refs={'evidence_refs':[{k:v for k,v in ref.items() if k!='role'}|{'verification':'control-required'}]} if evidence else {'document_refs':[ref]}
        g=self.iapply(self.iprepare(draft,**refs));selected=g['selections'][g['current']['selection_ref']['id']]
        self.child_intent={'authority_home_id':'home-a','kind':'intent','id':'intent-a','revision_ref':selected['revision_ref'],'acceptance_ref':selected['acceptance_ref'],'selection_ref':g['current']['selection_ref']}
        self.children()
        value=self.parent_proposal('rebind',old_intent=self.parent_intent);self.publish(value);self.apply(self.prepare('rebind',revision_ref=record_ref(value[0])))
        baseline=value[1];self.worker=self.target.parent/'parent-worker'
        self.git('worktree','add','-q','-b','parent-result',str(self.worker),baseline['base_commit'])
        (self.worker/'a').write_text('fixture integration result and evidence\n')
        (self.worker/'input.md').write_text('parent overwrote child input\n')
        self.git('add','a','input.md',cwd=self.worker);self.git('commit','-qm','synthetic overlapping report',cwd=self.worker)
        self.candidate_manifest=make_manifest(baseline['result'],snapshot(self.worker),scope=['a','input.md'],base_commit=baseline['base_commit'],candidate_commit=self.git('rev-parse','HEAD',cwd=self.worker),base_retention_ref=baseline['base_retention_ref'],candidate_retention_ref='refs/heads/parent-result')
        return self.parent_proposal('submit-result')


    def test_worker_child_required_input_overlap_refused_before_publication(self):
        value=self.candidate_with_child_input();before=self.bytes()
        with self.assertRaisesRegex(ContractError,'overlaps required intent input'):self.publish(value,worker=self.worker)
        self.assertEqual(before,self.bytes())
        self.assertEqual('accepted child input\n',(self.target/'input.md').read_text())
        self.assertEqual([],read_work(self.target,'parent')['pending_decisions'])

    def test_worker_child_required_evidence_overlap_refused_before_publication(self):
        value=self.candidate_with_child_input(evidence=True);before=self.bytes()
        with self.assertRaisesRegex(ContractError,'overlaps required intent input'):self.publish(value,worker=self.worker)
        self.assertEqual(before,self.bytes())
        self.assertEqual('accepted child input\n',(self.target/'input.md').read_text())
        self.assertEqual([],read_work(self.target,'parent')['pending_decisions'])


    def child_work_ref_overlap_and_resume(self, *, evidence=False):
        from hv2ref.work import snapshot, make_manifest
        old_text = 'historically accepted child result\n'
        new_text = 'parent integration replaces the historical result\n'
        (self.target / 'input.md').write_text(old_text)
        old_sha = hashlib.sha256(old_text.encode()).hexdigest()
        category = 'evidence_refs' if evidence else 'document_refs'
        ref = {'path': 'input.md', 'sha256': old_sha, 'required': True}
        ref.update({'verification': 'control-required'} if evidence else {'role': 'result'})
        for wid in ('child-a', 'child-b'):
            self.choose(wid)
            for operation in ('start', 'submit-result'):
                if operation == 'submit-result':
                    (self.target / 'a').write_text(wid + ' result\n')
                value = self.proposal(operation)
                value[0]['relations'] = [{'relation': 'parent', 'target': self.q('work', 'parent')}]
                if operation == 'submit-result':
                    value[0][category] = [copy.deepcopy(ref)]
                self.publish(value)
            self.assertEqual('completed', self.apply(self.prepare())['state'])
        child_history = {wid: read_work(self.target, wid) for wid in ('child-a', 'child-b')}
        intents_before = workspace_intents(self.target)
        acceptance = intents_before['intent-a']['acceptances'][self.child_intent['acceptance_ref']['id']]['confirmation']
        self.assertEqual([], acceptance['document_refs'] + acceptance['evidence_refs'])
        for graph in child_history.values():
            selected = graph['selections'][graph['current']['selection_ref']['id']]
            revision = graph['revisions'][selected['revision_ref']['id']]
            self.assertEqual([ref], revision[category])
        self.choose('parent')
        value = self.parent_proposal('rebind', old_intent=self.parent_intent)
        self.publish(value);self.apply(self.prepare('rebind', revision_ref=record_ref(value[0])))
        baseline = value[1];self.worker = self.target.parent / 'parent-worker'
        self.git('worktree', 'add', '-q', '-b', 'parent-result', str(self.worker), baseline['base_commit'])
        (self.worker / 'input.md').write_text(new_text)
        self.git('add', 'input.md', cwd=self.worker)
        self.git('commit', '-qm', 'synthetic child historical result replacement', cwd=self.worker)
        self.candidate_manifest = make_manifest(baseline['result'], snapshot(self.worker), scope=['a', 'input.md'], base_commit=baseline['base_commit'], candidate_commit=self.git('rev-parse', 'HEAD', cwd=self.worker), base_retention_ref=baseline['base_retention_ref'], candidate_retention_ref='refs/heads/parent-result')
        self.assertEqual(['input.md'], [c['path'] for c in self.candidate_manifest['changes']])
        self.publish(self.parent_proposal('submit-result'), worker=self.worker)
        self.assertEqual('review', read_work(self.target, 'parent')['state'])
        prepared = self.prepare()
        self.assertEqual(old_text, (self.target / 'input.md').read_text())
        with self.assertRaises(InjectedCrash):
            self.apply(prepared, inject_at='after-file')
        self.assertEqual(new_text, (self.target / 'input.md').read_text())
        self.assertEqual(1, len(read_work(self.target, 'parent')['pending_decisions']))
        result = self.apply(prepared)
        self.assertEqual('completed', result['state'])
        self.assertEqual([], result['pending_decisions'])
        self.assertEqual(self.candidate_manifest['result'], snapshot(self.target))
        self.assertEqual(child_history, {wid: read_work(self.target, wid) for wid in child_history})
        self.assertEqual(intents_before, workspace_intents(self.target))
        self.assertNotEqual(old_sha, hashlib.sha256((self.target / 'input.md').read_bytes()).hexdigest())
        before = self.bytes();self.assertEqual(result, self.apply(prepared));self.assertEqual(before, self.bytes())

    def test_worker_child_work_document_ref_overlap_preserves_history_and_resumes(self):
        self.child_work_ref_overlap_and_resume()

    def test_worker_child_work_evidence_ref_overlap_preserves_history_and_resumes(self):
        self.child_work_ref_overlap_and_resume(evidence=True)
