"""Umbrella pure contracts backed by actual schema1 writer graphs.

The runtime seam is a double. These tests do not qualify an installed umbrella
release, schema2 dispatch, parent writer enforcement or live document bytes.
"""
from __future__ import annotations
import copy
import unittest

from hv2ref.errors import ContractError, InjectedCrash
from hv2ref.intent import workspace_intents
from hv2ref.work import read_work, record_ref
from hv2ref.umbrella import (capture, check_history, evaluate, validate_composition, validate_evidence,
                             check_intent_role, check_baseline_binding)
import test_general_work_invariants as intent_fixtures


class UmbrellaReferenceTests(unittest.TestCase):
    proposal = intent_fixtures.IntentWriterTests.proposal
    publish = intent_fixtures.IntentWriterTests.publish
    prepare = intent_fixtures.IntentWriterTests.prepare
    apply = intent_fixtures.IntentWriterTests.apply
    bytes = intent_fixtures.IntentWriterTests.bytes
    draft = intent_fixtures.IntentWriterTests.draft
    accept = intent_fixtures.IntentWriterTests.accept
    iprepare = intent_fixtures.IntentWriterTests.iprepare
    iapply = intent_fixtures.IntentWriterTests.iapply

    def setUp(self):
        intent_fixtures.IntentWriterTests.setUp(self)
        self.accept()
        self.identity['work_id'] = 'parent'
        self.publish(self.proposal())
        for wid in ('child-a', 'child-b'):
            self.identity = {**self.identity, 'work_id': wid}
            for operation in ('start', 'submit-result'):
                if operation == 'submit-result':
                    (self.target/'a').write_text(wid+'\n')
                proposal = self.proposal(operation)
                proposal[0]['relations'] = [{'relation':'parent', 'target':self.q('work','parent')}]
                self.publish(proposal)
            self.apply(self.prepare())
        self.composition = {'parent':self.q('work','parent'), 'required_children':[
            {'work':self.q('work',wid), 'intent':self.q('intent','intent-a')} for wid in ('child-a','child-b')]}
        self.works = self.store._all(); self.intents_graph = workspace_intents(self.target)
        self.evidence = {'children':capture(self.composition,self.works,self.intents_graph)['children'], 'integration_document':'report.md'}
        self.documents = [{'path':'report.md','sha256':'a'*64,'required':True,'role':'result'}]
        self.execution = [{'path':'receipt.txt','sha256':'b'*64,'required':True,'verification':'control-required'}]

    @staticmethod
    def q(kind, identifier):
        return {'authority_home_id':'home-a','kind':kind,'id':identifier}

    def outcome(self, **changes):
        args={'composition':self.composition,'evidence':self.evidence,'works':self.works,'intents':self.intents_graph,
              'document_refs':self.documents,'evidence_refs':self.execution}
        args.update(changes)
        return evaluate(**args)

    def test_two_sequential_results_reference_predicate_is_read_only(self):
        before=self.bytes(); graphs=copy.deepcopy((self.works,self.intents_graph))
        self.assertTrue(self.outcome()['ready'])
        self.assertEqual(before,self.bytes());self.assertEqual(graphs,(self.works,self.intents_graph))
        # First child result bytes differ from the current file by design.
        self.assertEqual('child-b\n',(self.target/'a').read_text())

    def test_missing_child_and_partial_capture_never_ready(self):
        works=dict(self.works);del works['child-b']
        observed=capture(self.composition,works,self.intents_graph)
        self.assertEqual(1,len(observed['children']));self.assertEqual(1,len(observed['unavailable']))
        self.assertFalse(self.outcome(works=works)['ready'])
        evidence={**self.evidence,'children':self.evidence['children'][:1]}
        self.assertFalse(self.outcome(evidence=evidence)['ready'])

    def test_spliced_existing_revision_is_not_accepted_result(self):
        evidence=copy.deepcopy(self.evidence)
        graph=self.works['child-a']
        start=next(r for r in graph['revisions'].values() if r['operation']=='start')
        evidence['children'][0]['revision_ref']=record_ref(start)
        self.assertFalse(self.outcome(evidence=evidence)['ready'])

    def test_cross_child_good_result_cannot_replace_required_identity(self):
        evidence=copy.deepcopy(self.evidence)
        evidence['children'][0]={**evidence['children'][1],'work':self.q('work','child-a')}
        self.assertFalse(self.outcome(evidence=evidence)['ready'])

    def test_intent_drift_blocks_current_but_not_historical_acceptance(self):
        prior=self.intents_graph['intent-a']['drafts']['draft-1']
        self.accept(self.draft(2,prior=prior))
        intents=workspace_intents(self.target)
        self.assertFalse(self.outcome(intents=intents)['ready'])
        check_history(self.composition,self.evidence,self.works,intents,submitted=True)

    def test_revoke_blocks_current_and_preserves_history(self):
        self.identity={**self.identity,'work_id':'child-a'}
        graph=read_work(self.target,'child-a');selected=graph['selections'][graph['current']['selection_ref']['id']]
        self.apply(self.prepare('revoke',supersedes=selected['decision_ref']))
        works=self.store._all()
        self.assertFalse(self.outcome(works=works)['ready'])
        check_history(self.composition,self.evidence,works,self.intents_graph,submitted=True)

    def test_pending_revoke_cannot_appear_ready(self):
        self.identity={**self.identity,'work_id':'child-a'}
        graph=read_work(self.target,'child-a');selected=graph['selections'][graph['current']['selection_ref']['id']]
        with self.assertRaises(InjectedCrash):
            self.apply(self.prepare('revoke',supersedes=selected['decision_ref']),inject_at='after-decision')
        self.assertFalse(self.outcome(works=self.store._all())['ready'])

    def test_drop_does_not_require_rewriting_completed_child_relation(self):
        composition={**self.composition,'required_children':self.composition['required_children'][1:]}
        evidence={**self.evidence,'children':self.evidence['children'][1:]}
        before=self.bytes();self.assertTrue(self.outcome(composition=composition,evidence=evidence)['ready'])
        self.assertEqual(before,self.bytes())

    def test_missing_required_report_or_execution_reference_blocks(self):
        for changes in ({'document_refs':[]},{'evidence_refs':[]},
                        {'document_refs':[{**self.documents[0],'required':False}]},
                        {'evidence_refs':[{**self.execution[0],'verification':'worker-observed'}]}):
            with self.subTest(changes=changes):self.assertFalse(self.outcome(**changes)['ready'])

    def test_composition_rejects_empty_self_foreign_alias_and_unknown(self):
        variants=[]
        empty=copy.deepcopy(self.composition);empty['required_children']=[];variants.append(empty)
        own=copy.deepcopy(self.composition);own['required_children'][0]['work']=self.q('work','parent');variants.append(own)
        foreign=copy.deepcopy(self.composition);foreign['required_children'][0]['intent']['authority_home_id']='other';variants.append(foreign)
        alias=copy.deepcopy(self.composition);alias['required_children'][1]['work']['id']='CHILD-A';variants.append(alias)
        extra=copy.deepcopy(self.composition);extra['ready']=True;variants.append(extra)
        order=copy.deepcopy(self.composition);order['required_children'].reverse();variants.append(order)
        for value in variants:
            with self.subTest(value=value), self.assertRaises(ContractError):validate_composition(value,'home-a')

    def test_evidence_unknown_duplicate_and_missing_document_refuse(self):
        for edit in ('unknown','duplicate','document'):
            evidence=copy.deepcopy(self.evidence)
            if edit=='unknown':evidence['accepted']=True
            elif edit=='duplicate':evidence['children'].append(evidence['children'][0])
            else:evidence['integration_document']=None
            with self.subTest(edit=edit),self.assertRaises(ContractError):validate_evidence(evidence,'home-a',submitted=True)

    def test_capture_returns_copies_not_mutable_authority_aliases(self):
        observed=capture(self.composition,self.works,self.intents_graph)
        observed['children'][0]['intent_ref']['id']='altered'
        self.assertTrue(self.outcome()['ready'])

    def parent_revision(self, operation="start", evidence=None):
        graph = self.works["parent"]
        old = graph["revisions"][graph["selections"][graph["current"]["selection_ref"]["id"]]["revision_ref"]["id"]]
        value = copy.deepcopy(old)
        value.update(schema_version=2, operation=operation,
                     umbrella_evidence=copy.deepcopy(evidence if evidence is not None else {
                         "children":self.evidence["children"],"integration_document":None}),
                     document_refs=copy.deepcopy(self.documents), evidence_refs=copy.deepcopy(self.execution))
        return value

    def check_parent(self, revision, prior=None, **kw):
        check_baseline_binding(self.composition,revision,prior,self.works,self.intents_graph,**kw)

    def test_baseline_capture_must_match_current_children(self):
        baseline=self.parent_revision();self.check_parent(baseline,current=True)
        baseline["umbrella_evidence"]["children"]=[]
        with self.assertRaisesRegex(ContractError,"capture changed"):
            self.check_parent(baseline,current=True)
        # Historical partial captures remain valid after children complete.
        self.check_parent(baseline,current=False)

    def test_submit_cannot_replace_old_baseline_with_new_child_refs(self):
        baseline=self.parent_revision();baseline["umbrella_evidence"]["children"]=[]
        submitted=self.parent_revision("submit-result",self.evidence)
        with self.assertRaisesRegex(ContractError,"selected baseline"):
            self.check_parent(submitted,baseline,current=True)
        refreshed=self.parent_revision("rebind")
        self.check_parent(refreshed,baseline,current=True)
        self.check_parent(submitted,refreshed,current=True)

    def test_checkpoint_cannot_absorb_new_child_capture(self):
        baseline=self.parent_revision();baseline["umbrella_evidence"]["children"]=[]
        for operation in ("checkpoint","rework"):
            value=self.parent_revision(operation)
            with self.subTest(operation=operation),self.assertRaisesRegex(ContractError,"selected baseline"):
                self.check_parent(value,baseline,current=True)
            value["umbrella_evidence"]["children"]=[]
            self.check_parent(value,baseline,current=True)

    def test_parent_history_survives_child_drift_but_current_gate_refuses(self):
        baseline=self.parent_revision();submitted=self.parent_revision("submit-result",self.evidence)
        first=self.intents_graph['intent-a']['drafts']['draft-1']
        self.accept(self.draft(2,prior=first));self.intents_graph=workspace_intents(self.target)
        self.check_parent(submitted,baseline,current=False)
        with self.assertRaises(ContractError):self.check_parent(submitted,baseline,current=True)

    def test_parent_role_cannot_downgrade_schema_or_rebind_ordinary(self):
        baseline=self.parent_revision();ordinary=copy.deepcopy(baseline)
        ordinary['schema_version']=1;del ordinary['umbrella_evidence']
        for composition,value in ((None,ordinary),(self.composition,ordinary),(None,baseline)):
            with self.subTest(composition=composition),self.assertRaises(ContractError):
                check_baseline_binding(composition,value,baseline,self.works,self.intents_graph,current=True)
        check_baseline_binding(None,ordinary,None,self.works,self.intents_graph,current=True)

    def test_intent_role_is_accepted_history_not_latest_draft(self):
        ordinary=self.draft();parent={**ordinary,'schema_version':2,'composition':self.composition}
        check_intent_role(None,ordinary);check_intent_role(ordinary,parent)
        check_intent_role(parent,copy.deepcopy(parent))
        with self.assertRaises(ContractError):check_intent_role(parent,ordinary)
        changed=copy.deepcopy(parent);changed['composition']['parent']['id']='other-parent'
        with self.assertRaises(ContractError):check_intent_role(parent,changed)
        dropped=copy.deepcopy(parent);dropped['composition']['required_children']=dropped['composition']['required_children'][:1]
        check_intent_role(parent,dropped)
