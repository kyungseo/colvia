"""Adversarial proof, bounded discovery and live/sealed parity regressions."""
from pathlib import Path
import unittest
from unittest.mock import patch
from colvia.codec import RecordError
from colvia.records import link,record,application_registry
from colvia.rework import PathIndex,attribution,SubmissionBlocked
from colvia.maps import build_map,read_map
from colvia.graph import GraphAudit,AuditBudget
from colvia.work import WorkService
from test_foundation_work import WorkFixture
import test_foundation_rework as ordinary_fixture
import test_foundation_work_git as git_fixture


def links_of(obj):
    return {name:(obj.edges[indices[0]].role,obj.edges[indices[0]].ref) if indices else ('provenance',None)
            for name,indices in obj.payload['links'].items()}


class ReworkIntegrityTests(WorkFixture,unittest.TestCase):
    scenario=ordinary_fixture.ReworkTests.scenario

    def test_revised_peer_second_addition_is_blocked_in_view_and_submit(self):
        self.start();(self.root/'report.md').write_text('first');first=self.submit()
        self.start('other',('other.md','later.md'));(self.root/'other.md').write_text('peer');peer=self.submit('other')
        self.service.revise(operation='revise-a',work='report',receipt=first['receipt'],statement='확인 후 재제출')
        second=self.submit(operation='second-a')
        self.service.revise(operation='revise-b',work='other',receipt=peer['receipt'],statement='두 번째 파일 작성')
        (self.root/'later.md').write_text('later');self.submit('other',operation='second-b')
        self.service.revise(operation='revise-a-again',work='report',receipt=second['receipt'],statement='한 줄 추가')
        (self.root/'report.md').write_text('first plus line');before=self.store.root().ref
        shown=self.service.view('report')['rework']['submission_check']
        self.assertEqual('blocked',shown['status']);self.assertEqual('attribution-peer-ambiguous',shown['error'])
        with self.assertRaisesRegex(RecordError,'attribution-peer-ambiguous'):self.submit(operation='third-a')
        self.assertEqual(before,self.store.root().ref)

    def test_forged_publisher_cannot_ignore_reverted_peer_scope(self):
        original=(self.root/'source.csv').read_bytes()
        self.start();(self.root/'report.md').write_text('first');first=self.submit()
        self.start('other',('other.md','source.csv'));(self.root/'other.md').write_text('peer')
        (self.root/'source.csv').write_text('peer changed source');self.submit('other')
        # Deliberately conflicting peer proof, not an example of truthful checks.
        peer=self.service._head('other')[1];peer_result=link(peer,'result')
        (self.root/'source.csv').write_bytes(original)
        self.service.revise(operation='revise-a',work='report',receipt=first['receipt'],statement='한 줄')
        (self.root/'report.md').write_text('first plus line')
        plan=self.service._object(link(self.service._head('report')[1],'plan'))
        _,base,current=self.service._observe_from_plan(plan)
        added=next(e for e in current.snapshot.entries if e['path']=='other.md')
        from colvia.tree import canonical_entries
        before=self.store.root().ref
        with patch('colvia.rework.select',return_value=(canonical_entries([*base,added]),{'other.md':peer_result},{},None)):
            with self.assertRaisesRegex(RecordError,'attribution-peer-scope-changed'):self.submit(operation='forged')
        self.assertEqual(before,self.store.root().ref)

    def test_audit_rejects_hidden_v2_v1_v2_downgrade(self):
        self.scenario();first=self.result();self.submit(operation='second');second=self.result()
        payload={k:v for k,v in first.payload.items() if k!='links'};payload['revision']=3
        links=links_of(first);links['previous']=('provenance',second.ref)
        fake_v1,raw1=record('work.submission',payload,links)
        payload={k:v for k,v in second.payload.items() if k!='links'};payload['revision']=4
        links=links_of(second);links['previous']=('provenance',fake_v1)
        fake_v2,raw2=record('work.submission',payload,links,version=2)
        objects={fake_v1:raw1,fake_v2:raw2};load=lambda ref:objects[ref] if ref in objects else self.store.load(ref)
        audit=GraphAudit(Path(self.tmp.name)/'forged-audit.sqlite3',AuditBudget(10000,10000,32*1024*1024))
        try:
            with self.assertRaisesRegex(RecordError,'attribution-protection-removed'):audit.run(fake_v2,load,application_registry())
        finally:audit.close()

    def test_attribution_map_stops_before_reading_all_oversized_entries(self):
        self.scenario();self.submit(operation='second');result=self.result();peer=next(iter(attribution(result,self.store.load).values()))
        mapping=build_map((f'entry-{i}.md',peer) for i in range(3000));objects=dict(mapping.objects)
        links=links_of(result);links['attribution']=('decision',mapping.root)
        ref,raw=record('work.submission',{k:v for k,v in result.payload.items() if k!='links'},links,version=2)
        obj=application_registry().inspect(ref,raw,required=True);reads=[]
        def load(target):reads.append(target);return objects[target] if target in objects else self.store.load(target)
        with self.assertRaisesRegex(RecordError,'map-entry-limit'):attribution(obj,load)
        self.assertLess(len(reads),len(objects));self.assertLess(len(reads),1000)

    def test_path_overlap_index_covers_large_scope_and_case_ancestors(self):
        index=PathIndex(f'directory/item-{i}.md' for i in range(20000))
        self.assertTrue(index.overlaps('DIRECTORY'));self.assertTrue(index.overlaps('Directory/item-19999.md/child'))
        self.assertFalse(index.overlaps('directory/item-20000.md'));self.assertFalse(index.overlaps('other'))

    def test_candidate_tree_scan_is_bounded_before_validation(self):
        self.scenario();before=self.store.root().ref
        with patch('colvia.rework.MAX_CANDIDATES',0):
            with self.assertRaisesRegex(RecordError,'attribution-discovery-limit'):self.submit(operation='candidate-cap')
        self.assertEqual(before,self.store.root().ref)

    def test_new_work_head_race_refuses_without_publishing_result(self):
        self.scenario();before=self.service._head('report')[0];original=self.service._publish
        def publish(*args,**kwargs):
            if args[1]=='report':self.plan('new-peer',('other.md',))
            return original(*args,**kwargs)
        with patch.object(self.service,'_publish',side_effect=publish):
            with self.assertRaisesRegex(RecordError,'attribution-heads-changed'):self.submit(operation='phantom')
        self.assertEqual(before,self.service._head('report')[0]);self.assertEqual('active',self.service.view('report')['state'])

    def test_carried_file_diagnostic_names_peer_and_requires_exact_agreement(self):
        from colvia.presentation import human
        self.scenario();second=self.submit(operation='second')
        self.service.revise(operation='again',work='report',receipt=second['receipt'],statement='한 줄 더')
        (self.root/'other.md').write_text('different')
        value=self.service.view('report');item=value['rework']['submission_check']['items'][0]
        self.assertTrue(item['attributed']);self.assertEqual('other',item['peer_work']);self.assertEqual('other.md',item['path'])
        self.assertIn(item['peer_title'],human(value));self.assertIn('자동 복원하지',human(value))
        self.assertIn('다시 일치',human(value))

    def test_known_local_instruction_is_not_an_attributable_addition(self):
        self.scenario();(self.root/'CLAUDE.local.md').write_text('local instruction')
        with self.assertRaises(SubmissionBlocked) as failure:self.submit(operation='local-instruction')
        self.assertEqual(['CLAUDE.local.md'],[i['path'] for i in failure.exception.details['items']])

    def test_mixed_baseline_and_carried_change_have_distinct_requirements(self):
        from colvia.presentation import human
        self.scenario();second=self.submit(operation='second')
        self.service.revise(operation='again',work='report',receipt=second['receipt'],statement='한 줄 더')
        (self.root/'other.md').write_text('changed peer');(self.root/'source.csv').write_text('changed baseline')
        value=self.service.view('report');items={i['path']:i for i in value['rework']['submission_check']['items']}
        self.assertEqual('match-peer-submission',items['other.md']['requirement'])
        self.assertEqual('unchanged-from-original',items['source.csv']['requirement'])
        shown=human(value);line=next(l for l in shown.splitlines() if l.startswith('source.csv'))
        self.assertIn('원래 작업 기준',line);self.assertNotIn('제출본',line)
        with self.assertRaises(SubmissionBlocked):self.submit(operation='blocked')

    def test_changed_registered_boundary_has_causal_paths(self):
        from dataclasses import replace
        self.scenario();second=self.submit(operation='second')
        self.service.revise(operation='again',work='report',receipt=second['receipt'],statement='한 줄 더')
        observe=self.workspace.observe
        def changed(*args,**kwargs):
            registration,current=observe(*args,**kwargs)
            structural=replace(current.structural,containers=frozenset({'nested-parent'}),nested=frozenset({'nested-parent/registered-worktree'}))
            return registration,replace(current,structural=structural)
        with patch.object(self.workspace,'observe',side_effect=changed):
            diagnostic=self.service.view('report')['rework']['submission_check']
            self.assertEqual('attribution-context-changed',diagnostic['error'])
            self.assertEqual({'nested-parent','nested-parent/registered-worktree'},{i['path'] for i in diagnostic['items']})
            with self.assertRaises(SubmissionBlocked):self.submit(operation='structural-change')

    def test_sealed_adopted_paths_reject_alias_and_ancestor_collisions(self):
        from colvia.rework import effective_entries
        self.scenario();self.submit(operation='second');result=self.result();peer=next(iter(attribution(result,self.store.load).values()))
        plan=self.service._object(link(result,'plan'))
        for paths in [('Case.md','case.md'),('directory','directory/child.md')]:
            mapping=build_map((p,peer) for p in paths);objects=dict(mapping.objects)
            links=links_of(result);links['attribution']=('decision',mapping.root)
            ref,raw=record('work.submission',{k:v for k,v in result.payload.items() if k!='links'},links,version=2)
            obj=application_registry().inspect(ref,raw,required=True)
            load=lambda ref:objects[ref] if ref in objects else self.store.load(ref)
            with self.assertRaisesRegex(RecordError,'attribution-path-overlap'):effective_entries(self.service,plan,obj,load)

    def _subdirectory_addition(self,existing):
        parent=self.root/'notes'
        if existing:parent.mkdir()
        self.start();(self.root/'report.md').write_text('first');first=self.submit()
        self.start('other',('notes/other.md',));parent.mkdir(exist_ok=True)
        (parent/'other.md').write_text('peer');self.submit('other')
        self.service.revise(operation='revise-a',work='report',receipt=first['receipt'],statement='한 줄 더')
        (self.root/'report.md').write_text('second');second=self.submit(operation='second')
        self.assertEqual('review',second['state']);self.assertEqual({'notes/other.md'},set(attribution(self.result(),self.store.load)))
    def test_peer_file_in_existing_subdirectory(self):self._subdirectory_addition(True)
    def test_peer_file_in_new_subdirectory(self):self._subdirectory_addition(False)

    def test_v1_rework_does_not_claim_all_checks_must_pass(self):
        self.start();(self.root/'report.md').write_text('first');first=self.submit()
        self.service.revise(operation='again',work='report',receipt=first['receipt'],statement='한 줄 더')
        self.assertFalse(self.service.view('report')['rework']['submission_check']['all_checks_must_pass'])


class GitReworkTests(git_fixture.GitWorkFixture,unittest.TestCase):
    def submit_named(self,work,operation):
        return self.service.submit(operation=operation,work=work,summary='합성 본문 확인',checks=[dict(name='본문 확인',status='passed',detail='합성 대조')])
    def setup_attributed(self):
        (self.root/'.gitignore').write_text('');self.start(('report.md','.gitignore'))
        (self.root/'report.md').write_text('first');first=self.submit()
        p=self.service.plan(operation='peer-plan',work='other',title='다른 안내',goal='별도 안내',scope=['other.md'],checks=['본문 확인'])
        self.service.approve(operation='peer-approve',work='other',receipt=p['receipt'],statement='진행');self.service.start(operation='peer-start',work='other')
        (self.root/'other.md').write_text('peer');self.submit_named('other','peer-submit')
        self.service.revise(operation='revise',work='report',receipt=first['receipt'],statement='한 줄 수정')
        (self.root/'report.md').write_text('second');return self.submit_named('report','second')
    def test_git_attributed_rework_and_scope_only_candidate(self):
        from colvia.git_integration import GitIntegration
        second=self.setup_attributed();self.service.accept(operation='accept',work='report',receipt=second['receipt'],statement='수락')
        selected=GitIntegration(self.store,self.service.workspace,None)._selected(['report'])
        self.assertEqual({'report.md'},set(selected[1]));self.assertEqual('peer',(self.root/'other.md').read_text())
    def test_carried_only_policy_edit_is_blocked_consistently(self):
        second=self.setup_attributed();self.service.revise(operation='again',work='report',receipt=second['receipt'],statement='승인 범위의 제외 파일 주석 변경')
        (self.root/'.gitignore').write_text('# approved comment\n')
        diagnostic=self.service.view('report')['rework']['submission_check']
        self.assertEqual('blocked',diagnostic['status']);self.assertEqual('attribution-policy-changed',diagnostic['error'])
        self.assertEqual('.gitignore',diagnostic['items'][0]['path'])
        with self.assertRaisesRegex(RecordError,'attribution-policy-changed'):self.submit_named('report','policy-submit')

    def _subdirectory_addition(self,existing):
        parent=self.root/'notes'
        if existing:parent.mkdir()
        self.start();(self.root/'report.md').write_text('first');first=self.submit()
        p=self.service.plan(operation='peer-plan',work='other',title='별도 안내',goal='파일 추가',scope=['notes/other.md'],checks=['본문 확인'])
        self.service.approve(operation='peer-approve',work='other',receipt=p['receipt'],statement='진행');self.service.start(operation='peer-start',work='other')
        parent.mkdir(exist_ok=True);(parent/'other.md').write_text('peer');self.submit_named('other','peer-submit')
        self.service.revise(operation='revise',work='report',receipt=first['receipt'],statement='한 줄 더')
        (self.root/'report.md').write_text('second');second=self.submit_named('report','second')
        self.assertEqual('review',second['state'])
        result=self.service._object(link(self.service._head('report')[1],'result'))
        self.assertEqual({'notes/other.md'},set(attribution(result,self.store.load)))
    def test_git_peer_file_in_existing_subdirectory(self):self._subdirectory_addition(True)
    def test_git_peer_file_in_new_subdirectory(self):self._subdirectory_addition(False)

if __name__=='__main__':unittest.main()
