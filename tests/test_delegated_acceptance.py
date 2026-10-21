"""Synthetic Core delegation contract; this is not host authentication evidence."""
from __future__ import annotations
import copy
import hashlib
import json
import os
from pathlib import Path
import threading
import unittest
from unittest import mock
import test_worktree_execution as worker_fixtures
import test_general_work_recovery as serial_fixtures
from hv2ref.errors import ContractError, InjectedCrash
from hv2ref.intent import WorkspaceIntentStore, read_workspace_intent_graph, workspace_intents, workspace_intent_graph
from hv2ref.work import WorkStore, make_manifest, snapshot, read_work, record_ref, work_graph
from hv2ref.jsonio import canonical_json_bytes
from test_productization_safety import exact_snapshot

TIME = serial_fixtures.TIME

def digest(value):
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


class DelegatedAcceptanceTests(unittest.TestCase):
    git = worker_fixtures.WorkerPublicationTests.git
    commit_control = worker_fixtures.WorkerPublicationTests.commit_control
    bind = worker_fixtures.WorkerPublicationTests.bind
    accept_intent = serial_fixtures.SerialWriterTests.accept_intent
    publish = serial_fixtures.SerialWriterTests.publish
    apply = serial_fixtures.SerialWriterTests.apply
    bytes = serial_fixtures.SerialWriterTests.bytes

    def setUp(self):
        # accept_intent reads an existing self.intent to extend a graph. Each
        # fresh target starts its own graph, including same-object subcases.
        self.intent = None
        worker_fixtures.WorkerPublicationTests.setUp(self)
        self.base = self.target.parent
        (self.target / 'b').write_bytes(b'before-b\n')
        self.store = WorkStore(self.target, lambda target: {'binding_ref': copy.deepcopy(self.binding),
            'launcher_sha256': None, 'inventory_id': 'delegation-1'})
        self.istore = WorkspaceIntentStore(self.target, self.store.runtime_check)
        self.grant_number = 1

    def proposal(self, operation='start', **kw):
        result = serial_fixtures.SerialWriterTests.proposal(self, operation, **kw)
        result[0]['scope'] = ['a', 'b']
        return result

    def draft(self, grant=True):
        graph = read_workspace_intent_graph(self.target, 'intent-a')
        old = max(graph['drafts'].values(), key=lambda d:d['sequence'])
        value = copy.deepcopy(old)
        value.update(schema_version=3 if grant else 1, revision_id='draft-'+str(old['sequence']+1),
                     sequence=old['sequence']+1, prior_revision_ref=record_ref(old, 'revision_id'))
        value.pop('acceptance_delegation', None)
        if grant:
            value['acceptance_delegation'] = {'action':'accept', 'delegate_actor':'delegate-1',
                'execution_mode':'isolated-worktree', 'scope':['a','b'],
                'work':{'authority_home_id':'home-a','kind':'work','id':'work-a'}}
        return value

    def grant(self, value=None, *, select=True):
        value = self.draft() if value is None else value
        self.istore.publish_draft(value)
        if not select: return value
        self.select(value)
        return value

    def select(self, value):
        self.grant_number += 1
        packet = self.istore.prepare('intent-a', record_ref(value, 'revision_id'), actor='owner',
            reason='synthetic explicit grant',request_id='intent-'+str(self.grant_number),observed_at=TIME)
        graph = self.istore.apply(packet['ticket'], confirm_token=packet['confirm_token'])
        chosen = graph['selections'][graph['current']['selection_ref']['id']]
        self.intent = {'authority_home_id':'home-a','kind':'intent','id':'intent-a',
            'revision_ref':chosen['revision_ref'],'acceptance_ref':chosen['acceptance_ref'],
            'selection_ref':graph['current']['selection_ref']}
        return graph

    def baseline(self, operation='start'):
        oid=self.commit_control(); tree=snapshot(self.target)
        manifest=make_manifest(tree,tree,scope=['a','b'],base_commit=oid,candidate_commit=oid,
            base_retention_ref='refs/heads/retained-base',candidate_retention_ref='refs/heads/retained-base')
        return self.bind(self.proposal(operation,old_intent=self.intent if operation=='rebind' else None),manifest)

    def submit(self, *, change_b=True, fresh=True, evidence_refs=None):
        if fresh: self.publish(self.baseline())
        graph=read_work(self.target,'work-a')
        rev=graph['revisions'][graph['selections'][graph['current']['selection_ref']['id']]['revision_ref']['id']]
        base=graph['manifests'][rev['result_refs']['manifest']['id']]
        branch='candidate-'+str(self.serial)
        self.worker=self.base/('worker-'+str(self.serial))
        self.git(self.target,'worktree','add','-q','-b',branch,str(self.worker),base['candidate_commit'])
        (self.worker/'a').write_bytes(b'result-'+str(self.serial).encode()+b'\n')
        if change_b: (self.worker/'b').write_bytes(b'result-b-'+str(self.serial).encode()+b'\n')
        self.git(self.worker,'add','a','b');self.git(self.worker,'commit','-qm','synthetic delegated result')
        manifest=make_manifest(base['result'],snapshot(self.worker),scope=['a','b'],base_commit=base['candidate_commit'],
            candidate_commit=self.git(self.worker,'rev-parse','HEAD'),base_retention_ref=base['candidate_retention_ref'],
            candidate_retention_ref='refs/heads/'+branch)
        proposal=self.bind(self.proposal('submit-result'),manifest)
        if evidence_refs is not None: proposal[0]['evidence_refs']=copy.deepcopy(evidence_refs)
        return self.publish(proposal,worker=self.worker)

    def prepare(self, action='accept', *, actor='delegate-1', request_id=None, **kw):
        return self.store.prepare('work-a',action=action,actor=actor,reason='synthetic decision',
            request_id=request_id or actor+'-'+action,observed_at=TIME,**kw)

    def pure(self, graph, *, decisions=None, revisions=None, selections=None):
        return work_graph(graph['identity'],revisions or graph['revisions'],
            graph['decisions'] if decisions is None else decisions,
            graph['selections'] if selections is None else selections,graph['manifests'],graph['current'],
            intent_graphs=workspace_intents(self.target))

    def refusal(self, action, reason=None, *, new_lock=False, code=None):
        before=exact_snapshot(self.target)
        # Only named first-guard refusals admit the normal scratch anchor.
        # mkdir uses 0777 & umask; bind that expectation without changing the runner.
        prior_umask=os.umask(0o077) if new_lock else None
        try:
            with self.assertRaisesRegex(ContractError,reason or ".*") as caught: action()
        finally:
            if prior_umask is not None: os.umask(prior_umask)
        if code is not None:
            self.assertEqual(code,caught.exception.code)
            self.assertEqual(reason,caught.exception.message)
        after=exact_snapshot(self.target)
        additions={}
        if new_lock and '.hrn/locks/writer.lock' not in before:
            additions['.hrn/locks/writer.lock']=('file',hashlib.sha256(b'').hexdigest(),0o600)
            if '.hrn/locks' not in before: additions['.hrn/locks']=('directory',0o700)
        self.assertEqual(before | additions,after)

    def refresh(self, *, old_intent=None):
        proposal=self.baseline('rebind')
        if old_intent is not None: proposal[0]['rebind_from']=old_intent
        self.publish(proposal)
        packet=self.prepare('rebind',actor='owner',request_id='refresh-'+str(self.serial),revision_ref=record_ref(proposal[0]))
        self.apply(packet)
        return self.submit(fresh=False)

    def parent_fixture(self):
        from hv2ref.umbrella import capture
        parent={'authority_home_id':'home-a','kind':'work','id':'parent'}
        child_identity=copy.deepcopy(self.identity)
        self.identity={**child_identity,'work_id':'parent'}
        initial=self.proposal();self.publish(initial)
        self.identity=child_identity
        self.grant()
        baseline=self.baseline();baseline[0]['relations']=[{'relation':'parent','target':parent}]
        self.publish(baseline)
        original=self.proposal
        def child_proposal(*args,**kw):
            proposal=original(*args,**kw)
            proposal[0]['relations']=[{'relation':'parent','target':parent}]
            return proposal
        self.proposal=child_proposal
        try:
            self.submit(fresh=False)
        finally:
            self.proposal=original
        child_packet=self.prepare();self.apply(child_packet)
        composition={'parent':parent,'required_children':[{'work':{'authority_home_id':'home-a','kind':'work','id':'work-a'},
            'intent':{'authority_home_id':'home-a','kind':'intent','id':'intent-a'}}]}
        draft=copy.deepcopy(read_workspace_intent_graph(self.target,'intent-a')['drafts']['draft-1'])
        draft.update(intent_id='parent-intent',revision_id='parent-draft-1',sequence=1,
            prior_revision_ref=None,schema_version=2,composition=composition)
        self.istore.publish_draft(draft)
        packet=self.istore.prepare('parent-intent',record_ref(draft,'revision_id'),actor='owner',
            reason='synthetic composition promotion',request_id='parent-intent-accept',observed_at=TIME)
        ig=self.istore.apply(packet['ticket'],confirm_token=packet['confirm_token'])
        chosen=ig['selections'][ig['current']['selection_ref']['id']]
        pref={'authority_home_id':'home-a','kind':'intent','id':'parent-intent',
            'revision_ref':chosen['revision_ref'],'acceptance_ref':chosen['acceptance_ref'],
            'selection_ref':ig['current']['selection_ref']}
        self.identity={**child_identity,'work_id':'parent'}
        try:
            promotion=self.proposal('rebind',intent=pref,old_intent=initial[0]['intent_ref'])
            promotion[0]['schema_version']=2
            children=capture(composition,self.store._all(),workspace_intents(self.target))['children']
            promotion[0]['umbrella_evidence']={'children':children,'integration_document':None}
            self.publish(promotion)
            packet=self.store.prepare('parent',action='rebind',actor='owner',reason='promote parent',
                request_id='promote-parent',observed_at=TIME,revision_ref=record_ref(promotion[0]))
            self.apply(packet)
            submitted=self.proposal('submit-result',intent=pref)
            submitted[0]['schema_version']=2
            submitted[0]['umbrella_evidence']={'children':children,'integration_document':'a'}
            sha=hashlib.sha256((self.target/'a').read_bytes()).hexdigest()
            submitted[0]['document_refs']=[{'path':'a','sha256':sha,'required':True,'role':'result'}]
            submitted[0]['evidence_refs']=[{'path':'a','sha256':sha,'required':True,'verification':'control-required'}]
            parent_graph=self.publish(submitted)
        finally:
            self.identity=child_identity
        return composition,parent_graph,child_packet,pref

    def delegation_view(self):
        from hv2ref import view
        graph=read_work(self.target,'work-a');intents=workspace_intents(self.target);works=self.store._all()
        revision=graph['revisions'][graph['selections'][graph['current']['selection_ref']['id']]['revision_ref']['id']]
        before=exact_snapshot(self.target)
        result=view._delegation_observation(self.target,graph,revision,intents,works)
        lines=view._work(self.target,graph,None,None,intents,works)
        self.assertEqual(before,exact_snapshot(self.target))
        self.assertIn(r'- current\_delegation\_conditions:',lines)
        return result

    def test_v01_owner_history(self):
        self.submit();self.refusal(self.prepare)
        graph=self.apply(self.prepare(actor='owner'))
        self.assertEqual('completed',graph['state'])
        # The pure Work graph has no filesystem continuation input.
        self.assertEqual({key:value for key,value in graph.items() if key != 'continuation'},
                         self.pure(graph))
        self.assertEqual({'choices': {}, 'selections': {}, 'current': None, 'chain': [],
                          'pending': None, 'cancelled': {}, 'effective_choice': None,
                          'effective_ticket': None,
                          'usage': {'normal_limit': 256, 'normal_used': 0, 'normal_remaining': 256},
                          'data': {}}, graph['continuation'])

    def test_v02_exact_grant(self):
        self.grant();self.submit(change_b=False)
        head=self.git(self.target,'rev-parse','HEAD');index=(self.target/'.git/index').read_bytes()
        graph=self.apply(self.prepare())
        self.assertEqual('completed',graph['state'])
        self.assertEqual((self.worker/'a').read_bytes(),(self.target/'a').read_bytes())
        self.assertEqual(b'before-b\n',(self.target/'b').read_bytes())
        self.assertEqual(head,self.git(self.target,'rev-parse','HEAD'));self.assertEqual(index,(self.target/'.git/index').read_bytes())
        self.assertEqual('delegate-1',next(iter(graph['decisions'].values()))['confirmation']['actor'])

    def test_v03_actor_home_work(self):
        value=self.draft();value['acceptance_delegation']['work']['authority_home_id']='foreign'
        self.refusal(lambda:self.grant(value),'cross-home delegation',new_lock=True,code='HV2-WORK-RECORD')
        value=self.draft();value['acceptance_delegation']['work']['id']='another-work'
        self.grant(value);self.submit();self.refusal(self.prepare)
        self.refusal(lambda:self.prepare(actor='another-agent'))
        self.assertEqual('completed',self.apply(self.prepare(actor='owner'))['state'])

    def test_v04_scope_mode(self):
        value=self.draft();value['acceptance_delegation']['scope']=['a']
        self.grant(value);self.submit()
        self.refusal(self.prepare,'delegated Work scope/mode/role differs',code='HV2-WORK-RECORD')
        self.setUp();self.grant();self.publish(self.proposal());self.publish(self.proposal('submit-result'))
        self.refusal(self.prepare,'delegated Work scope/mode/role differs',code='HV2-WORK-RECORD')

        with self.subTest(boundary='schema2-target-pure-graph'):
            self.setUp();self.grant();graph=self.submit();packet=self.prepare()
            revisions={};selections={};chain=[]
            cursor=graph['current']['selection_ref']
            while cursor is not None:
                selected=graph['selections'][cursor['id']];chain.append(selected)
                cursor=selected['parent_selection_ref']
            self.assertEqual(len(graph['selections']),len(chain))
            for selection in reversed(chain):
                revision=copy.deepcopy(graph['revisions'][selection['revision_ref']['id']])
                prior=revision['expected_prior_selection']
                revision['expected_prior_selection']=record_ref(selections[prior['id']]) if prior else None
                revision['schema_version']=2
                revision['umbrella_evidence']={'children':[],
                    'integration_document':'a' if revision['operation']=='submit-result' else None}
                revisions[revision['record_id']]=revision
                selected=copy.deepcopy(selection);selected['revision_ref']=record_ref(revision)
                selected['parent_selection_ref']=revision['expected_prior_selection']
                selections[selected['record_id']]=selected
            ticket=copy.deepcopy(packet['ticket'])
            ticket['target_revision_ref']=record_ref(revisions[ticket['target_revision_ref']['id']])
            ticket['expected_selection_ref']=record_ref(selections[ticket['expected_selection_ref']['id']])
            decision=self.store._decision(ticket)
            current={**graph['current'],'selection_ref':ticket['expected_selection_ref']}
            self.refusal(lambda:work_graph(graph['identity'],revisions,{decision['record_id']:decision},
                selections,graph['manifests'],current,intent_graphs=workspace_intents(self.target)),
                'delegated Work scope/mode/role differs',code='HV2-WORK-RECORD')

    def test_v05_actions(self):
        self.grant();self.submit()
        for action in ('reject','revoke','rebind'):
            with self.subTest(action=action):self.refusal(lambda:self.prepare(action))
        packet=self.prepare();self.apply(packet)
        self.refusal(lambda:self.prepare('revoke'))
        revoke=self.prepare('revoke',actor='owner',supersedes=record_ref(self.store._decision(packet['ticket'])))
        self.assertEqual('revoked',self.apply(revoke)['state'])

    def test_v06_current_vs_history(self):
        old=self.grant();self.submit();packet=self.prepare()
        self.grant(self.draft(grant=False));self.refusal(lambda:self.apply(packet))
        self.setUp();self.grant();self.submit();packet=self.prepare();graph=self.apply(packet)
        self.grant(self.draft(grant=False))
        before=self.bytes();self.assertEqual(graph,self.apply(packet));self.assertEqual(before,self.bytes())
        self.assertEqual('completed',read_work(self.target,'work-a')['state'])

    def test_v07_evidence(self):
        self.grant();self.submit();packet=self.prepare()
        (self.target/'evidence').write_bytes(b'protected oracle\n')
        # New outside-scope content invalidates the complete baseline even though
        # grant, actor and manifest remain syntactically valid.
        self.refusal(lambda:self.apply(packet))

        for changed,reason in (('missing','required reference missing or aliased'),
                               ('replaced','required reference is stale')):
            with self.subTest(required_evidence=changed):
                self.setUp();self.grant();evidence=self.target/'evidence'
                evidence.write_bytes(b'protected required oracle\n')
                refs=[{'path':'evidence','sha256':hashlib.sha256(evidence.read_bytes()).hexdigest(),
                    'required':True,'verification':'control-required'}]
                self.submit(evidence_refs=refs);packet=self.prepare()
                if changed=='missing':evidence.unlink()
                else:evidence.write_bytes(b'replaced oracle\n')
                self.refusal(lambda:self.apply(packet),reason,code='HV2-WORK-RECORD')
        with self.subTest(required_evidence='worker-only-claim'):
            self.setUp();self.grant();self.submit(change_b=False)
            proposal=self.proposal('submit-result')
            proposal[0]['evidence_refs']=[{'path':'a','sha256':hashlib.sha256((self.worker/'a').read_bytes()).hexdigest(),
                'required':True,'verification':'worker-observed'}]
            self.refusal(lambda:self.publish(proposal),
                'required evidence must be accessible on control',code='HV2-WORK-RECORD')

    def test_v08_prepare_apply_drift(self):
        self.grant();self.submit();packet=self.prepare()
        for field,value in (('actor','impostor'),('request_id','changed'),('product_binding_ref',{'id':'wrong','sha256':'0'*64})):
            altered=copy.deepcopy(packet);altered['ticket'][field]=value
            with self.subTest(field=field):self.refusal(lambda:self.apply(altered),"confirmation token mismatch")
        for field,value,reason in (('actor','impostor','actor/action outside delegation'),('product_binding_ref',{'id':'wrong','sha256':'0'*64},'active binding changed')):
            altered=copy.deepcopy(packet);altered['ticket'][field]=value;altered['confirm_token']=digest(altered['ticket'])[:16]
            with self.subTest(valid_token_field=field):self.refusal(lambda:self.apply(altered),reason)
        (self.target/'a').write_bytes(b'foreign\n');self.refusal(lambda:self.apply(packet))

    def test_v09_duplicate_k(self):
        self.grant();self.submit();packet=self.prepare();graph=self.apply(packet)
        ticket=copy.deepcopy(packet['ticket']);ticket['request_id']='second-use'
        decision=self.store._decision(ticket)
        with self.assertRaisesRegex(ContractError,'already consumed'):
            self.pure(graph,decisions=graph['decisions']|{decision['record_id']:decision})
        self.assertEqual(graph,read_work(self.target,'work-a'))

        # The actual writer must reject a second valid request before selecting
        # the first decision, so stale-current rejection cannot mask K reuse.
        self.setUp();self.grant();self.submit();first=self.prepare(request_id='first');second=self.prepare(request_id='second')
        with self.assertRaises(InjectedCrash):self.apply(first,inject_at='after-decision')
        self.refusal(lambda:self.apply(second),'delegation already consumed')
        changed=copy.deepcopy(first);changed['ticket']['reason']='different request body';changed['confirm_token']=digest(changed['ticket'])[:16]
        self.refusal(lambda:self.apply(changed),'request ID reused with different ticket')
        self.assertEqual('completed',self.apply(first)['state'])

    def test_v10_reselection(self):
        draft=self.grant();self.submit();packet=self.prepare()
        with self.assertRaises(InjectedCrash):self.apply(packet,inject_at='after-decision')
        cancel=self.prepare('reject',actor='owner',supersedes=record_ref(self.store._decision(packet['ticket'])))
        self.apply(cancel);self.select(draft);self.refresh(old_intent=packet['ticket']['intent_ref'])
        self.refusal(lambda:self.prepare(request_id='reselected-grant'),
            'delegation already consumed',code='HV2-WORK-RECORD')

    def test_v11_reactivation(self):
        draft=self.grant();self.grant(self.draft(grant=False));self.select(draft)
        self.submit();packet=self.prepare(actor='owner');completed=self.apply(packet)
        proposed=self.baseline('rebind')
        self.refusal(lambda:self.publish(proposed),
            'completed Work requires human revoke before new revision',code='HV2-WORK-RECORD')
        # Reuse the unrecorded proposal: a second baseline commit has no changes.
        # CAS cannot publish a rebind against the pre-accept selection.
        cas=copy.deepcopy(proposed);cas[0]['expected_prior_selection']=packet['ticket']['expected_selection_ref']
        self.refusal(lambda:self.publish(cas),'stale expected selection',code='HV2-WORK-RECORD')
        self.assertEqual(completed['current'],read_work(self.target,'work-a')['current'])
        for cancellation in (False,True):
            with self.subTest(owner_cancel=cancellation):
                self.setUp();self.grant();self.submit()
                if cancellation:
                    packet=self.prepare(actor='owner')
                    with self.assertRaises(InjectedCrash):self.apply(packet,inject_at='after-decision')
                    rejection=self.prepare('reject',actor='owner',supersedes=record_ref(self.store._decision(packet['ticket'])))
                else:rejection=self.prepare('reject',actor='owner')
                self.apply(rejection);self.refresh()
                self.assertEqual('completed',self.apply(self.prepare(request_id='unused-grant'))['state'])

    def test_v12_all_pre_cancel(self):
        self.grant();self.submit();packet=self.prepare()
        with self.assertRaises(InjectedCrash):self.apply(packet,inject_at='after-decision')
        self.assertEqual(b'before\n',(self.target/'a').read_bytes());self.assertEqual(b'before-b\n',(self.target/'b').read_bytes())
        supersedes=record_ref(self.store._decision(packet['ticket']))
        self.refusal(lambda:self.prepare('reject',supersedes=supersedes))
        self.apply(self.prepare('reject',actor='owner',supersedes=supersedes))
        self.refusal(lambda:self.apply(packet));self.refresh()
        self.refusal(lambda:self.prepare(request_id='cancelled-grant'),
            'delegation already consumed',code='HV2-WORK-RECORD')

    def test_v13_mixed_recovery(self):
        self.grant();self.submit();packet=self.prepare()
        with self.assertRaises(InjectedCrash):self.apply(packet,inject_at='after-file')
        self.assertEqual((self.worker/'a').read_bytes(),(self.target/'a').read_bytes())
        self.assertEqual(b'before-b\n',(self.target/'b').read_bytes())
        self.refusal(lambda:self.prepare('reject',actor='owner',supersedes=record_ref(self.store._decision(packet['ticket']))))
        graph=self.apply(packet);self.assertEqual('completed',graph['state']);self.assertEqual(1,len(graph['decisions']))
        self.assertEqual((self.worker/'b').read_bytes(),(self.target/'b').read_bytes())

    def test_v14_late_cutpoints(self):
        for point in ('after-staged-file','after-selection','after-staged-current','after-current'):
            with self.subTest(point=point):
                self.setUp();self.grant();self.submit();packet=self.prepare()
                with self.assertRaises(InjectedCrash):self.apply(packet,inject_at=point)
                graph=self.apply(packet);self.assertEqual('completed',graph['state']);self.assertEqual(1,len(graph['decisions']))
                before=self.bytes();self.assertEqual(graph,self.apply(packet));self.assertEqual(before,self.bytes())

    def test_v15_unavailable_drift(self):
        self.grant();self.submit();packet=self.prepare()
        with self.assertRaises(InjectedCrash):self.apply(packet,inject_at='after-file')
        (self.target/'b').write_bytes(b'neither\n');self.refusal(lambda:self.apply(packet))
        (self.target/'b').write_bytes(b'before-b\n')
        self.git(self.target,'update-ref','-d','refs/heads/candidate-1')
        self.refusal(lambda:self.apply(packet))

    def test_v16_pending_mutation(self):
        self.grant();self.submit();packet=self.prepare()
        with self.assertRaises(InjectedCrash):self.apply(packet,inject_at='after-decision')
        self.refusal(lambda:self.istore.publish_draft(self.draft(grant=False)),
            'pending Work blocks intent mutation',code='HV2-WORK-RECORD')
        self.refusal(lambda:self.prepare(request_id='competing'))
        self.assertEqual('completed',self.apply(packet)['state'])

        for category,field in (('intent','actor'),('work','author')):
            with self.subTest(out_of_band=category):
                self.setUp();self.grant();self.submit();packet=self.prepare()
                with self.assertRaises(InjectedCrash):self.apply(packet,inject_at='after-decision')
                ref=packet['ticket']['intent_ref']['revision_ref'] if category=='intent' else packet['ticket']['target_revision_ref']
                path=(self.target/'.hrn/intents/intent-a/drafts' if category=='intent' else
                      self.target/'.hrn/work/work-a/revisions')/(ref['id']+'.json')
                value=json.loads(path.read_bytes());value[field]='out-of-band-change'
                path.write_bytes(canonical_json_bytes(value))
                self.refusal(lambda:self.apply(packet),
                    'missing or changed referenced record',code='HV2-WORK-RECORD')

    def test_v17_revoke_barrier(self):
        for actor in ('owner','delegate-1'):
            with self.subTest(prior_actor=actor):
                self.setUp();self.grant();self.submit();packet=self.prepare(actor=actor);self.apply(packet)
                revoke=self.prepare('revoke',actor='owner',supersedes=record_ref(self.store._decision(packet['ticket'])))
                self.apply(revoke);self.refresh()
                reason=('selected revoke bars this delegation draft' if actor=='owner'
                    else 'delegation already consumed')
                self.refusal(lambda:self.prepare(request_id='revoked-grant'),reason,code='HV2-WORK-RECORD')
                old=self.intent;self.grant();self.refresh(old_intent=old)
                self.assertEqual('completed',self.apply(self.prepare(request_id='fresh-k'))['state'])

    def test_v18_concurrent_requests(self):
        self.grant();self.submit();packets=[self.prepare(request_id='race-'+str(i)) for i in range(2)]
        barrier=threading.Barrier(3,timeout=10);results=[]
        def apply(packet):
            barrier.wait()
            try: results.append(('ok',self.apply(packet)['state']))
            except ContractError as exc:results.append(('refused',exc.code,exc.message))
        threads=[threading.Thread(target=apply,args=(packet,)) for packet in packets]
        for thread in threads:thread.start()
        barrier.wait()
        for thread in threads:thread.join(30);self.assertFalse(thread.is_alive())
        self.assertEqual(1,sum(x[0]=='ok' for x in results));self.assertEqual(1,sum(x[0]=='refused' for x in results))
        self.assertIn(('refused','HV2-WORK-RECORD','stale confirmation selection'),results)
        self.assertEqual(1,len(read_work(self.target,'work-a')['decisions']))

    def test_v19_prospective_context(self):
        self.grant();graph=self.submit();packet=self.prepare();decision=self.store._decision(packet['ticket'])
        prospective=graph['decisions']|{decision['record_id']:decision}
        with self.assertRaisesRegex(ContractError,'intent context'):
            work_graph(graph['identity'],graph['revisions'],prospective,graph['selections'],graph['manifests'],graph['current'])
        self.assertEqual([decision['record_id']],self.pure(graph,decisions=prospective)['pending_decisions'])
        for window in ('entry-1','checkout-1',None,'unknown'):
            other=WorkStore(self.target,lambda target,w=window:{'binding_ref':self.binding,'launcher_sha256':None,**({'inventory_id':w} if w else {})})
            with self.subTest(window=window):self.refusal(lambda:other.apply(packet['ticket'],confirm_token=packet['confirm_token']))

    def test_v20_shared_readers(self):
        from hv2ref import view
        self.grant();self.submit();self.apply(self.prepare())
        graph=read_work(self.target,'work-a');intents=workspace_intents(self.target)
        lines=view._work(self.target,graph,None,None,intents,{'work-a':graph})
        self.assertIn('delegate-1','\n'.join(lines))
        self.assertIn(r'- acceptance\_delegation:',lines)
        self.assertEqual(graph,read_work(self.target,'work-a',_intent_graph_reader=lambda iid:intents[iid]))
        malformed=copy.deepcopy(intents['intent-a']['data'])
        selected=self.intent['revision_ref']['id'];malformed['drafts/'+selected+'.json']['acceptance_delegation']['action']='revoke'
        with self.assertRaises(ContractError):workspace_intent_graph(malformed,'intent-a','home-a')

        for state in ('eligible','consumed','owner-revoked','pending','stale'):
            with self.subTest(view_state=state):
                self.setUp();self.grant();self.submit();packet=self.prepare(actor='owner' if state=='owner-revoked' else 'delegate-1')
                if state in ('consumed','owner-revoked'):self.apply(packet)
                if state=='owner-revoked':
                    self.apply(self.prepare('revoke',actor='owner',supersedes=record_ref(self.store._decision(packet['ticket']))))
                    self.refresh()
                if state=='pending':
                    with self.assertRaises(InjectedCrash):self.apply(packet,inject_at='after-decision')
                if state=='stale':self.grant(self.draft(grant=False))
                observed=self.delegation_view()
                self.assertEqual(state in ('consumed','pending'),bool(observed['consumed_decisions']))
                self.assertEqual(state=='owner-revoked',bool(observed['selected_revoke_barriers']))
                self.assertEqual('no recorded blocker observed' if state=='eligible' else 'blocked',observed['current_record_conditions'])
                expected={'consumed':'delegation already consumed','owner-revoked':'selected revoke bars this delegation draft',
                    'pending':'Work publication pending','stale':'stale intent selection'}
                if state in expected:self.assertIn(expected[state],observed['blockers'])

    def test_v21_child_parent(self):
        from hv2ref import view
        from hv2ref.umbrella import capture,check_history,evaluate
        self.setUp();composition,parent_graph,child_packet,parent_intent=self.parent_fixture()
        works=self.store._all();intents=workspace_intents(self.target)
        captured=capture(composition,works,intents)
        self.assertEqual([],captured['unavailable']);self.assertEqual(1,len(captured['children']))
        rid=parent_graph['selections'][parent_graph['current']['selection_ref']['id']]['revision_ref']['id']
        revision=parent_graph['revisions'][rid];evidence=revision['umbrella_evidence']
        self.assertTrue(evaluate(composition,evidence,works,intents,
            document_refs=revision['document_refs'],evidence_refs=revision['evidence_refs'])['ready'])
        before=exact_snapshot(self.target)
        lines=view._work(self.target,parent_graph,None,None,intents,works)
        self.assertIn(r'    - actual\_acceptance\_actor: delegate-1',lines)
        self.assertIn('    - Owner: owner',lines)
        grant_start=lines.index(r'    - grant\_ref:')
        grant_end=lines.index(r'    - acceptance\_delegation:',grant_start)
        revision_line=lines.index(r'      - revision\_ref:',grant_start,grant_end)
        self.assertEqual(['        - id: '+self.intent['revision_ref']['id'],
            '        - sha256: '+view.code(self.intent['revision_ref']['sha256'])],
            lines[revision_line+1:revision_line+3])
        self.assertEqual(before,exact_snapshot(self.target))
        def parent_prepare(actor):
            return self.store.prepare('parent',action='accept',actor=actor,reason='synthetic parent review',
                request_id='parent-'+actor,observed_at=TIME)
        owner_parent_packet=parent_prepare('owner')
        self.assertEqual('owner',owner_parent_packet['ticket']['actor'])
        self.refusal(lambda:parent_prepare('delegate-1'),'no grant for this Work',code='HV2-WORK-RECORD')
        # The accepted parent cannot regain ordinary eligibility via a different
        # schema3 intent naming the same Work ID. The earlier non-downgrade guard
        # dominates the redundant delegation ancestry guard in a full graph.
        with self.subTest(boundary='promoted-parent-same-work-grant'):
            value=self.draft();value['acceptance_delegation']['work']['id']='parent';self.grant(value)
            child_identity=self.identity;self.identity={**child_identity,'work_id':'parent'}
            try:proposal=self.proposal('rebind',intent=self.intent,old_intent=parent_intent)
            finally:self.identity=child_identity
            parent_identity={**child_identity,'work_id':'parent'}
            self.refusal(lambda:self.store.publish(parent_identity,*proposal[:2],selection_id=proposal[2],operation_id=proposal[3]),
                'selected parent cannot downgrade record schema',code='HV2-WORK-RECORD')
            self.refusal(lambda:parent_prepare('delegate-1'),'no grant for this Work',code='HV2-WORK-RECORD')
            # Exercise apply with an internally valid token; token possession
            # cannot transfer the ordinary grant onto a composition revision.
            forged=copy.deepcopy(owner_parent_packet)
            forged['ticket']['actor']='delegate-1';forged['ticket']['request_id']='parent-delegate-apply'
            forged['confirm_token']=digest(forged['ticket'])[:16]
            self.refusal(lambda:self.apply(forged),'no grant for this Work',code='HV2-WORK-RECORD')
        for state,reason in (('stale','child intent changed'),('revoked','child accepted chain differs'),
                             ('pending','child publication pending')):
            with self.subTest(child_state=state):
                self.setUp();composition,parent_graph,child_packet,_=self.parent_fixture()
                rid=parent_graph['selections'][parent_graph['current']['selection_ref']['id']]['revision_ref']['id']
                revision=parent_graph['revisions'][rid];evidence=revision['umbrella_evidence']
                if state=='stale':self.grant(self.draft(grant=False))
                else:
                    revoke=self.prepare('revoke',actor='owner',supersedes=record_ref(self.store._decision(child_packet['ticket'])))
                    if state=='revoked':self.apply(revoke)
                    else:
                        with self.assertRaises(InjectedCrash):self.apply(revoke,inject_at='after-decision')
                before=exact_snapshot(self.target);works=self.store._all();intents=workspace_intents(self.target)
                captured=capture(composition,works,intents)
                self.assertEqual([],captured['children'])
                self.assertEqual([{'work':composition['required_children'][0]['work'],
                    'reason':'HV2-WORK-RECORD: '+reason}],captured['unavailable'])
                evaluated=evaluate(composition,evidence,works,intents,
                    document_refs=revision['document_refs'],evidence_refs=revision['evidence_refs'])
                self.assertFalse(evaluated['ready'])
                self.assertEqual(['HV2-WORK-RECORD: required child is not currently eligible'],evaluated['reasons'])
                check_history(composition,evidence,works,intents,submitted=True)
                self.assertEqual(before,exact_snapshot(self.target))
        self.setUp();value=self.draft();value['composition']=composition
        self.refusal(lambda:self.istore.publish_draft(value),'unknown or missing content fields',
            new_lock=True,code='HV2-WORK-CONTENT')

    def test_v25_malformed_grant(self):
        from hv2ref.intent import validate_delegation
        good=self.draft()['acceptance_delegation']
        invalid=[None,{},dict(good,extra=True),dict(good,scope=[]),dict(good,scope=['a','a']),
            dict(good,scope=['a','A']),dict(good,scope=['../escape']),dict(good,delegate_actor='owner'),
            dict(good,delegate_actor='OWNER'),dict(good,delegate_actor='에이전트'),dict(good,delegate_actor='x\n'),
            dict(good,action='reject'),dict(good,execution_mode='local'),dict(good,scope=[123]),
            dict(good,scope=['a','a/child']),dict(good,scope=['.hrn/work']),dict(good,scope=['.git/config']),
            dict(good,delegate_actor=1),dict(good,delegate_actor='a'*97),
            dict(good,work={**good['work'],'kind':'intent'}),dict(good,work={**good['work'],'extra':True})]
        for index,grant in enumerate(invalid):
            with self.subTest(index=index),self.assertRaises(ContractError):validate_delegation(grant,'home-a','owner')
        self.assertEqual(good,validate_delegation(good,'home-a','소유자'))
        for version,code,reason in ((True,'HV2-WORK-RECORD','unsupported intent record version'),
                (2,'HV2-WORK-CONTENT','unknown or missing content fields'),
                (1,'HV2-WORK-CONTENT','unknown or missing content fields'),
                (4,'HV2-WORK-RECORD','unsupported intent record version')):
            value=self.draft();value['schema_version']=version
            with self.subTest(version=version):
                self.refusal(lambda:self.istore.publish_draft(value),reason,new_lock=True,code=code)

        # A retained/absent/unknown verifier cannot write a home containing even
        # an unselected schema3 grant. Check each real store entry separately.
        self.grant();self.submit();work_packet=self.prepare(actor='owner')
        draft=self.draft();self.istore.publish_draft(draft)
        intent_packet=self.istore.prepare('intent-a',record_ref(draft,'revision_id'),actor='owner',reason='fresh grant',request_id='new-grant',observed_at=TIME)
        revision,manifest,_,_=self.baseline('rebind')
        from hv2ref.candidates import CandidateStore
        import test_candidates as candidate_fixtures
        for window in ('entry-1','checkout-1',None,'unknown'):
            runtime=lambda target,w=window:{'binding_ref':copy.deepcopy(self.binding),'launcher_sha256':None,**({'inventory_id':w} if w else {})}
            wrong_work=WorkStore(self.target,runtime);wrong_intent=WorkspaceIntentStore(self.target,runtime)
            actions=[lambda:wrong_intent.publish_draft(self.draft(grant=False)),
                lambda:wrong_intent.prepare('intent-a',record_ref(draft,'revision_id'),actor='owner',reason='unsupported',request_id='unsupported',observed_at=TIME),
                lambda:wrong_intent.apply(intent_packet['ticket'],confirm_token=intent_packet['confirm_token']),
                lambda:wrong_work.publish(self.identity,revision,manifest,selection_id='unsupported',operation_id='unsupported'),
                lambda:wrong_work.prepare('work-a',action='accept',actor='owner',reason='unsupported',request_id='unsupported',observed_at=TIME),
                lambda:wrong_work.apply(work_packet['ticket'],confirm_token=work_packet['confirm_token']),
                lambda:CandidateStore(self.target,runtime).mutate(candidate_fixtures.proposal(self.target,cid='unsupported'))]
            for index,action in enumerate(actions):
                with self.subTest(window=window,writer=index):self.refusal(action)
