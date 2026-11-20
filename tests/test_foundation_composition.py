"""Composition gates through both the dedicated service and ordinary Work API."""
import unittest
from colvia.codec import RecordError,decode_envelope
from colvia.composition import CompositionService,declaration_key,membership_key
from colvia.records import link,record
from colvia.work import work_key
from test_foundation_work import WorkFixture


class CompositionTests(WorkFixture,unittest.TestCase):
    def setUp(self):
        super().setUp();self.composition=CompositionService(self.service)
    def declare(self,children=('child',)):
        self.plan('parent',('integration.md',))
        for child in children:self.plan(child,('report.md',))
        return self.composition.declare(operation='declare',parent='parent',children=children,document='integration.md',
            checks=['집계 대조'],statement='이 하위 작업들을 통합한다')
    def begin(self,work):
        plan=self.service.plan_review(work)
        self.service.approve(operation=work+'-approve',work=work,receipt=plan['receipt'],statement='진행')
        self.service.start(operation=work+'-start',work=work)
    def accept_child(self,child='child'):
        (self.root/'report.md').write_text(child+' result')
        review=self.submit(child)
        self.service.accept(operation=child+'-accept',work=child,receipt=review['receipt'],statement='결과 수락')
    def bind(self,operation='rebind'):
        preview=self.composition.rebind_preview('parent')
        return self.composition.rebind(operation=operation,parent='parent',receipt=preview['receipt'],statement='이 결과를 연결해 통합하자')
    def ready_parent(self):
        self.declare();self.begin('child');self.accept_child();self.bind();self.begin('parent')
        (self.root/'integration.md').write_text('Integrated conclusion')
        return self.submit('parent')

    def test_child_acceptance_is_not_parent_acceptance(self):
        review=self.ready_parent()
        self.assertEqual('review',self.service.view('parent')['state'])
        self.assertEqual('completed',self.service.view('child')['state'])
        from colvia.work_dependencies import show
        self.assertEqual({'bound':1,'waiting':0,'rebind':0},show(self.store,'parent')['parent_submission'])
        self.service.accept(operation='parent-accept',work='parent',receipt=review['receipt'],statement='통합 결과 수락')
        self.assertEqual('completed',self.service.view('parent')['state'])

    def test_roles_atomically_bound_and_old_approval_receipt_stale(self):
        self.plan('parent',('integration.md',));old=self.plan('child')
        self.composition.declare(operation='declare',parent='parent',children=['child'],document='integration.md',checks=['집계 대조'],statement='연결')
        ch=self.service._head('child')[1];ph=self.service._head('parent')[1]
        self.assertEqual(link(ch,'context'),self.store.head(membership_key('child')))
        self.assertEqual('composition.binding',link(ph,'context').kind)
        with self.assertRaisesRegex(RecordError,'stale-plan-receipt'):
            self.service.approve(operation='old-approval',work='child',receipt=old['receipt'],statement='진행')

    def test_ordinary_plan_replacement_cannot_drop_parent_or_child_role(self):
        self.declare()
        for work in ('child','parent'):
            old=self.store.root().ref;scope=self.service.plan_review(work)['scope']
            with self.assertRaisesRegex(RecordError,'composition-(parent-mismatch|membership-mismatch|rebind-required)'):
                self.service.plan(operation='replace-'+work,work=work,title='other',goal='other',scope=scope,checks=['check'],
                                  replace_receipt=self.service.plan_review(work)['receipt'])
            self.assertEqual(old,self.store.root().ref)

    def test_common_publisher_refuses_context_stripping(self):
        self.declare();ref,head=self.service._head('parent');plan=self.service._object(link(head,'plan'))
        forged=self.service._head_record(plan.ref,plan.payload,'planned',previous=ref,context=None)
        with self.assertRaisesRegex(RecordError,'composition-transition-required'):
            self.service._publish('strip','parent',ref,forged)
        self.assertEqual(ref,self.store.head(work_key('parent')))

    def test_incomplete_children_block_parent_submission(self):
        self.declare();self.begin('parent');(self.root/'integration.md').write_text('premature')
        with self.assertRaisesRegex(RecordError,'composition-required-child-missing'):self.submit('parent')
        self.assertEqual('active',self.service.view('parent')['state'])

    def test_capture_requires_explicit_rebind_new_plan_approval(self):
        self.declare();self.begin('child');self.accept_child();old=self.store.head(work_key('parent'))
        from colvia.work_dependencies import show
        self.assertEqual({'waiting':0,'rebind':1,'bound':0},show(self.store,'parent')['parent_submission'])
        planned=self.bind();head=self.service._head('parent')[1]
        self.assertEqual(old,link(head,'previous'));self.assertIsNone(link(head,'approval'))
        self.assertEqual('planned',planned['state'])
        with self.assertRaisesRegex(RecordError,'plan-approval-required'):
            self.service.start(operation='no-approval',work='parent')
        self.assertEqual('completed',self.service.view('child')['state'])

    def test_archive_alone_does_not_invalidate_capture(self):
        review=self.ready_parent()
        self.service.archive(operation='archive-child',work='child',archived=True)
        self.service.accept(operation='parent-accept',work='parent',receipt=review['receipt'],statement='통합 수락')
        self.assertEqual('completed',self.service.view('parent')['state'])

    def test_child_reopened_after_parent_review_blocks_parent_acceptance(self):
        review=self.ready_parent();child=self.service.view('child')
        self.service.revise(operation='child-reopen',work='child',receipt=child['reopen_receipt'],statement='하위 작업 수정')
        with self.assertRaisesRegex(RecordError,'composition-child-changed'):
            self.service.accept(operation='parent-accept',work='parent',receipt=review['receipt'],statement='수락')
        self.assertEqual('review',self.service.view('parent')['state'])
        self.assertEqual('Integrated conclusion',self.service.result_content('parent','integration.md')['after']['text'])

    def test_rebind_after_child_reopen_keeps_old_parent_history(self):
        review=self.ready_parent();old_parent=self.store.head(work_key('parent'))
        self.service.accept(operation='parent-accept',work='parent',receipt=review['receipt'],statement='통합 수락')
        accepted=self.store.head(work_key('parent'));child=self.service.view('child')
        self.service.revise(operation='child-reopen',work='child',receipt=child['reopen_receipt'],statement='추가 수정')
        from colvia import work_dependencies as dep
        self.plan('consumer',('consumer.md',))
        basis = dep.preview(self.store,'consumer',None,'parent')['basis']
        dep.apply(self.store,'consumer',None,'parent',basis=basis,request='통합 결과 필요',recorder='agent',operation='link')
        outcome = dep.show(self.store,'consumer')['items'][0]['result']
        self.assertEqual('recheck',outcome['status'])
        parent_decision = link(self.service._head('parent')[1], 'decision')
        self.assertEqual(parent_decision.sha256, outcome['decision'])
        # No new child edge: rebinding must not need to open the advisory graph.
        from unittest.mock import patch
        with patch.object(dep,'check_graph',side_effect=AssertionError('unrelated graph scan')):
            self.bind('rebind-incomplete')
        head=self.service._head('parent')[1]
        self.assertEqual(accepted,link(head,'previous'));self.assertIsNone(link(head,'result'));self.assertIsNone(link(head,'decision'))
        self.service._validate_head(accepted,self.store.load)
        self.assertEqual('review',decode_envelope(old_parent,self.store.load(old_parent)).payload['phase'])

    def test_child_change_invalidates_rebind_preview(self):
        self.declare();preview=self.composition.rebind_preview('parent');self.begin('child')
        with self.assertRaisesRegex(RecordError,'stale-composition-rebind-receipt'):
            self.composition.rebind(operation='stale',parent='parent',receipt=preview['receipt'],statement='다시 연결')

    def test_self_duplicate_and_nested_compositions_refuse(self):
        self.declare();self.plan('other',('other.md',))
        for children in (['other'],['child','child'],['parent']):
            old=self.store.root().ref
            with self.assertRaises(RecordError):
                self.composition.declare(operation='bad'+str(len(children)),parent='other',children=children,document='other.md',checks=['집계 대조'],statement='연결')
            self.assertEqual(old,self.store.root().ref)

    def test_report_path_and_check_must_belong_to_parent_plan(self):
        self.plan('parent',('integration.md',));self.plan('child')
        old=self.store.root().ref
        for document,checks in [('other.md',['집계 대조']),('integration.md',['unknown'])]:
            with self.assertRaisesRegex(RecordError,'composition-integration-scope'):
                self.composition.declare(operation='bad-'+document,parent='parent',children=['child'],document=document,checks=checks,statement='연결')
            self.assertEqual(old,self.store.root().ref)

    def test_missing_retained_report_refuses_submission(self):
        self.declare();self.begin('child');self.accept_child();self.bind();self.begin('parent')
        with self.assertRaisesRegex(RecordError,'composition-report-required'):self.submit('parent')

    def test_failed_integration_check_refuses_submission(self):
        self.declare();self.begin('child');self.accept_child();self.bind();self.begin('parent')
        (self.root/'integration.md').write_text('integrated')
        with self.assertRaisesRegex(RecordError,'composition-integration-check-failed'):
            self.service.submit(operation='failed-check',work='parent',summary='report',checks=[
                dict(name='원본 보존',status='passed',detail='same'),dict(name='집계 대조',status='failed',detail='mismatch')])

    def test_two_children_keep_distinct_accepted_results(self):
        self.declare(('a','b'));self.begin('a');self.begin('b');self.accept_child('a');self.accept_child('b');self.bind();self.begin('parent')
        (self.root/'integration.md').write_text('a and b integrated');review=self.submit('parent')
        self.assertEqual('review',review['state'])
        self.assertEqual('a result',self.service.result_content('a','report.md')['after']['text'])
        self.assertEqual('b result',self.service.result_content('b','report.md')['after']['text'])

    def test_explicit_child_replacement_preserves_old_results_and_decisions(self):
        self.ready_parent();old=self.service._head('child')[1];self.plan('replacement',('new.md',))
        preview=self.composition.rebind_preview('parent',['replacement'])
        self.assertEqual(['child'],[v['work'] for v in preview['removed']])
        self.composition.rebind(operation='replace-child',parent='parent',children=['replacement'],receipt=preview['receipt'],statement='새 범위의 작업으로 교체')
        released=self.service._head('child')[1]
        self.assertEqual(link(old,'result'),link(released,'result'));self.assertEqual(link(old,'decision'),link(released,'decision'))
        self.assertIsNone(link(released,'context'));self.assertIsNone(self.store.head(membership_key('child')))
        self.assertEqual('planned',self.service.view('parent')['state'])
        self.assertEqual('child result',self.service.result_content('child','report.md')['after']['text'])
        member=self.service._head('replacement')[1];self.assertEqual('composition.membership',link(member,'context').kind)

    def test_child_selection_itself_is_bound_to_rebind_receipt(self):
        self.declare();preview=self.composition.rebind_preview('parent');self.plan('replacement',('new.md',))
        with self.assertRaisesRegex(RecordError,'stale-composition-rebind-receipt'):
            self.composition.rebind(operation='not-shown',parent='parent',children=['replacement'],receipt=preview['receipt'],statement='다른 구성')
        self.assertIsNotNone(self.store.head(membership_key('child')))

    def test_new_child_cannot_belong_to_another_parent(self):
        self.declare();self.plan('other-parent',('other.md',));self.plan('other-child',('more.md',))
        self.composition.declare(operation='declare-other',parent='other-parent',children=['other-child'],document='other.md',checks=['집계 대조'],statement='별도 통합')
        for child in ('other-parent','other-child'):
            with self.assertRaisesRegex(RecordError,'composition-child-already-bound'):
                self.composition.rebind_preview('parent',[child])

    def test_empty_selection_cannot_remove_parent_role(self):
        self.declare()
        with self.assertRaisesRegex(RecordError,'composition-self-or-alias'):self.composition.rebind_preview('parent',[])

    def test_capture_does_not_depend_on_optional_observed_head(self):
        self.ready_parent();parent=self.service._head('parent')[1]
        binding=self.service._object(link(parent,'context'))
        from colvia.composition import refs
        cap=self.service._object(refs(binding,'captures')[0]);observed=link(cap,'observed')
        def without_provenance(ref):
            if ref==observed:raise RuntimeError('optional provenance was read')
            return self.store.load(ref)
        self.service._validate_head(parent.ref,without_provenance)

    def test_forged_child_change_claim_is_not_validated_by_links_alone(self):
        from colvia.codec import Edge,encode_envelope
        from colvia.composition import refs
        self.ready_parent();parent=self.service._head('parent')[1];binding=self.service._object(link(parent,'context'))
        cap=self.service._object(refs(binding,'captures')[0]);result=self.service._object(link(cap,'result'));decision=self.service._object(link(cap,'decision'))
        objects={}
        def altered(obj,*,payload=None,replacements=None):
            edges=tuple(Edge(edge.role,(replacements or {}).get(edge.ref,edge.ref)) for edge in obj.edges)
            ref,raw=encode_envelope(obj.ref.kind,obj.ref.version,payload or obj.payload,edges);objects[ref]=raw;return ref
        bad_result=altered(result,payload={**result.payload,'changed':['unrelated.md']})
        bad_decision=altered(decision,replacements={result.ref:bad_result})
        bad_cap=altered(cap,replacements={result.ref:bad_result,decision.ref:bad_decision})
        bad_binding=altered(binding,replacements={cap.ref:bad_cap});bad_parent=altered(parent,replacements={binding.ref:bad_binding})
        def load(ref):return objects[ref] if ref in objects else self.store.load(ref)
        with self.assertRaisesRegex(RecordError,'submission-change-mismatch'):self.service._validate_head(bad_parent,load)

    def test_pending_effect_blocks_declaration_before_any_head_change(self):
        self.plan('parent',('integration.md',));self.plan('child')
        self.store.reader_capabilities |= {'schema:fixture.effect:1'}
        self.store.writer_capabilities |= {'schema:fixture.effect:1'}
        effect=record('fixture.effect',{'state':'pending'},{})
        self.store.commit_heads(operation='fixture',expected={'effect:pending':None},changes={'effect:pending':effect[0]},objects=[effect],validate=lambda view:None)
        root=self.store.root().ref
        with self.assertRaisesRegex(RecordError,'external-effect-pending'):
            self.composition.declare(operation='declare',parent='parent',children=['child'],document='integration.md',checks=['집계 대조'],statement='연결')
        self.assertEqual(root,self.store.root().ref)

if __name__=='__main__':unittest.main()
