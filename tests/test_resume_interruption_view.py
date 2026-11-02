"""Read-only resume choices and historical execution attribution."""
import copy
import json
import unittest
from pathlib import Path
from unittest.mock import patch
from hv2ref import view, official_state as state
from test_view_summary import label_graph
from test_official_v2 import Chain, SHA


def public(chain):
    value = chain.read().summary()
    value['cancel_requested'] = False
    return state.public_status(value)


def status(*records):
    return {'official_execution': {'available': True, 'records': list(records),
                                  'ready_for_new_grant': all(r['status'] in state.TERMINAL for r in records)}}


class ExecutionProjectionTests(unittest.TestCase):
    def test_no_process_and_spawn_failure_are_not_completed_processes(self):
        chain = Chain()
        self.assertEqual('not_requested', public(chain)['process_observation'])
        chain.add('runtime-reserved', ordinal=1, host_pid=9000, host_birth='Sat Oct 31 12:00:00 2026')
        self.assertEqual('unconfirmed', public(chain)['process_observation'])
        chain.add('runtime-spawn-failed', ordinal=1, reason='spawn_failed', reaped=True)
        self.assertEqual('not_started', public(chain)['process_observation'])

    def test_runtime_closed_is_not_all_workers_closed(self):
        chain = Chain().launch(); chain.successful(1)
        role = chain.reserve(2); chain.intent(2, role); chain.close_runtime()
        result = public(chain)
        self.assertTrue(result['closure_refs'])
        self.assertEqual('unknown', result['document_write_effect'])
        self.assertEqual('unconfirmed', result['process_observation'])

    def test_applied_is_independent_of_runtime_closure(self):
        chain = Chain().launch().successful(1).successful(2)
        result = public(chain)
        self.assertEqual('applied', result['document_write_effect'])
        self.assertEqual('unconfirmed', result['process_observation'])
        chain.close_runtime()
        self.assertEqual('closed', public(chain)['process_observation'])

    def test_allowlist_and_readonly_projection(self):
        chain = Chain().launch().successful(1).successful(2)
        before = copy.deepcopy(chain.rows)
        result = public(chain); encoded = json.dumps(result)
        self.assertEqual('synthetic-work', result['work_id'])
        for forbidden in ('/synthetic/project', 'recovery_locator', 'recovery_store_id', 'documents', 'Output', 'runtime_started', 'rows', 'scope', 'revision_ref', 'intent_ref'):
            self.assertNotIn(forbidden, encoded)
        self.assertEqual(before, chain.rows)
        self.assertEqual('not_checked', result['recovery_availability'])

    def test_v1_keeps_its_existing_fields(self):
        value = dict(grant=SHA, head=SHA, status='incomplete', completed=0, pending=None,
                     revoked=False, sealed=False, cancel_requested=False, schema_version=1)
        self.assertEqual(set(value)-{'schema_version'}, set(state.public_status(value)))


class ResumeViewTests(unittest.TestCase):
    def graph(self, state_name='active'):
        graph, intents = label_graph('설치 안내 개선')
        graph['state'] = state_name
        graph['continuation']['usage']['normal_remaining'] = 10
        return graph, intents

    def execution(self, effect='unknown', terminal=False, process='closed', wid='work-a', grant=SHA):
        return dict(grant=grant, schema_version=2, status='operator-resolved-unknown' if terminal else 'incomplete',
                    work_id=wid, document_write_effect=effect, process_observation=process, effect_refs=[3], closure_refs=[4])

    def test_fallback_without_narrative_and_no_approval_from_scope(self):
        graph, intents = self.graph()
        graph['revisions']['revision-a']['next_action'] = 'FORGED EXECUTE NOW'
        from hv2ref.work import record_ref
        graph['selections']['selection-a']['revision_ref'] = record_ref(graph['revisions']['revision-a'])
        graph['current']['selection_ref'] = record_ref(graph['selections']['selection-a'])
        before = copy.deepcopy((graph,intents))
        shown = '\n'.join(view._work_overview('work-a', graph, intents, {'work-a':graph}, include_scope=True))
        self.assertIn('다음: 현재 계획과 남은 작업 확인',shown)
        self.assertIn('기록된 범위:',shown)
        self.assertNotIn('FORGED',shown)
        self.assertNotIn('유지할 조건',shown)
        self.assertEqual(before,(graph,intents))

    def test_active_baseline_is_not_called_a_submission(self):
        graph, intents = self.graph()
        shown = '\n'.join(view._work_overview('work-a', graph, intents, {'work-a':graph}, current_files='stale: changed'))
        self.assertIn('기준 기록과 달라진 현재 파일 확인', shown)
        self.assertNotIn('제출본', shown)

    def test_priority_pending_then_closure_then_files_then_acceptance(self):
        graph, _ = self.graph('review'); ex=status(self.execution(process='unconfirmed'))
        graph['pending_decisions']=['pending']
        self.assertIn('처리가 남은',view._resume_next('work-a',graph,ex,'stale: files differ'))
        graph['pending_decisions']=[]
        self.assertEqual('실행 종료 여부 확인',view._resume_next('work-a',graph,ex,'stale: files differ'))
        self.assertEqual('제출본과 달라진 현재 파일 확인',view._resume_next('work-a',graph,{},'stale: files differ'))
        self.assertIn('수락 또는 보완 결정',view._resume_next('work-a',graph,{},'matches stored result'))

    def test_terminal_unknown_never_reblocks_current_work(self):
        graph, _ = self.graph('review'); ex=status(self.execution(terminal=True))
        self.assertTrue(ex['official_execution']['ready_for_new_grant'])
        self.assertIn('수락 또는 보완',view._resume_next('work-a',graph,ex))
        shown='\n'.join(view._execution_overview(ex))
        self.assertIn('정리된 실행',shown); self.assertIn('문서 반영 여부가 불명확',shown)
        self.assertIn('미해결 실행: 0건',shown); self.assertNotIn('- 다음:',shown)

    def test_historical_target_never_borrows_current_title_or_revision(self):
        graph, intents=self.graph('review'); ex=status(self.execution())
        shown='\n'.join(view._execution_overview(ex,work_id='work-a',details=True))
        self.assertNotIn('설치 안내 개선',shown);self.assertNotIn('revision-a',shown)
        self.assertIn('현재 작업 기록과의 관계: 미확인',shown)
        self.assertIn('문서 효과 근거',shown)

    def test_multiple_grants_are_stable_and_other_work_is_excluded(self):
        a=self.execution(grant='a'*64); b=self.execution(grant='b'*64); other=self.execution(wid='work-b',grant='c'*64)
        first='\n'.join(view._execution_overview(status(b,other,a),work_id='work-a'))
        second='\n'.join(view._execution_overview(status(a,b,other),work_id='work-a'))
        self.assertEqual(first,second); self.assertNotIn('c'*64,first)
        self.assertLess(first.index('a'*64),first.index('b'*64))
        self.assertIn('미해결 실행: 2건',first)

    def test_view_text_escapes_work_id_and_keeps_v1_without_effect(self):
        record=self.execution(wid='work-<script>**x**')
        shown='\n'.join(view._execution_overview(status(record)))
        self.assertIn(view.code(record['work_id']),shown)
        v1=dict(grant='d'*64,status='incomplete')
        legacy='\n'.join(view._execution_overview(status(v1)))
        self.assertNotIn('문서 반영:',legacy)
        self.assertIn('기존 실행 상세',legacy)

    def test_isolated_control_baseline_is_not_called_stale_submission(self):
        observed={'content':{'whole_base_matches':True,'whole_result_matches':False}}
        with patch.object(view,'_worker_inspection',return_value=observed) as inspect:
            pair=view._work_files(Path('/synthetic'),{'execution_context':{'mode':'isolated-worktree'}},{},None)
        self.assertEqual((observed,'isolated-observed'),pair);inspect.assert_called_once()


class ResumeReviewCorrections(unittest.TestCase):
    def test_isolated_errors_precede_acceptance_and_healthy_baseline_is_separate(self):
        graph, intents = label_graph('설치 안내 개선')
        for error in ('source_error','content_error'):
            observed={error:'missing evidence','content':None}
            with patch.object(view,'_worker_inspection',return_value=observed):
                pair=view._work_files(Path('/synthetic'),{'execution_context':{'mode':'isolated-worktree'}},{},None)
            shown='\n'.join(view._work_overview('work-a',graph,intents,{'work-a':graph},current_files=pair[1]))
            self.assertIn('격리 작업 근거를 확인하지 못한 원인 확인',shown)
            self.assertNotIn('수락 또는 보완 결정',shown)
            self.assertIn('원본과 후보',shown)
        self.assertIn('수락 또는 보완',view._resume_next('work-a',graph,{},'isolated-observed'))

    def test_non_normal_environment_has_priority_on_both_views(self):
        graph, intents = label_graph('설치 안내 개선')
        graph.update(orphan_revisions=[])
        for intent in intents.values(): intent.update(pending_acceptances=[], pending_selections=[])
        for status_value in ({'classification':'partial','pending_lifecycle':'x'},
                             {'classification':'pass','authoritative_control':False},
                             {'classification':'degraded','continuation_unavailable':{'work-a':{'message':'missing'}}}):
            status_value.update(work_states={'work-a':'review'},intent_count=1,pending_work=[],pending_intent=[],pending_continuation=[])
            # No additional observation or file access is needed to prioritize environment state.
            with patch.object(view,'safe_target',return_value=Path('/synthetic')),patch.object(view,'_observe',return_value=(status_value,{'work-a':graph},intents)),patch.object(view,'_product',return_value=None),patch.object(view,'render_candidates',return_value=([],None)):
                shown,_=view.render_view('/synthetic')
            self.assertIn('환경·진입 상태 먼저 확인',shown)
            self.assertNotIn('- 다음: 제출 내용을 검토하고 수락',shown)
        shown='\n'.join(view._work_overview('work-a',graph,intents,{'work-a':graph},environment_ready=False))
        self.assertIn('환경·진입 상태 먼저 확인',shown)

    def test_empty_execution_has_no_optional_import(self):
        import builtins
        original=builtins.__import__
        def guarded(name,*a,**kw):
            if name=='official_state':raise AssertionError('optional import')
            return original(name,*a,**kw)
        with patch('builtins.__import__',side_effect=guarded):
            self.assertEqual([],view._execution_overview({'official_execution':{'available':True,'records':[]}}))

    def test_terminal_unconfirmed_no_write_effect_stays_visible_without_reblocking(self):
        from test_official_v2 import BIRTH, identity
        c=Chain().launch();c.reserve(1);c.intent(1,'read');c.add('worker-started',worker_ordinal=1,pid=9011,birth=BIRTH)
        c.add('operator-resolved-unknown',grant=SHA,journal_head=c.rows[-1]['sha256'],previous_status='incomplete',documents={'Output':identity(),'Reference':identity(3)},process_absence=True,recovery_availability='missing',action='record-unknown-resolution')
        record=public(c);self.assertEqual('none',record['document_write_effect']);self.assertEqual('unconfirmed',record['process_observation'])
        shown='\n'.join(view._execution_overview(status(record)))
        self.assertIn('개별 프로세스 종료 근거',shown)
        graph,_=label_graph('title');self.assertIn('수락 또는 보완',view._resume_next('synthetic-work',graph,status(record)))

    def test_unknown_event_status_is_unresolved_even_with_closed_processes(self):
        from test_official_v2 import BIRTH, identity
        c=Chain().launch().successful(1);c.reserve(2);c.intent(2,'write');c.add('worker-started',worker_ordinal=2,pid=9012,birth=BIRTH)
        result=c.add('worker-result',worker_ordinal=2,success=False,effect='unknown',before=identity(),after=identity(),verifier_id=None,verifier_pass=None,reason='worker_failed')
        closed=c.add('worker-closed',worker_ordinal=2,returncode=1,group_absent=True,birth_absent=True)
        c.close_runtime();c.terminal('unknown')
        record=public(c);self.assertNotIn(record['status'],state.TERMINAL)
        self.assertEqual('closed',record['process_observation']);self.assertEqual('unknown',record['document_write_effect'])

    def test_unmapped_v1_attention_and_closed_v1_no_new_action(self):
        record=dict(grant='d'*64,status='incomplete')
        shown='\n'.join(view._execution_overview(status(record),work_id='work-a'))
        self.assertIn('작업 연결을 확인할 미해결 실행 1건',shown)
        self.assertNotIn('기록된 대상',shown)
        record['status']='completed';shown='\n'.join(view._execution_overview(status(record),details=True))
        self.assertNotIn('- 다음:',shown)

    def test_rendered_gfm_does_not_expose_grant_payload(self):
        from hv2ref.official_worker import GFM
        source=Path(__file__).resolve().parents[1]
        parser=GFM(str(source/'runtime/official/marked.umd.js'),'0db7abc826b5ac76f6ed11951ae34074ba50438ce6ea8d52889203779e5cbbad')
        c=Chain().launch().successful(1).successful(2);shown='\n'.join(view._execution_overview(status(public(c)),details=True));html=parser.render(shown)
        for value in ('/synthetic/project','recovery_locator','recovery_store_id','Output','original_identity','<script>'):
            self.assertNotIn(value,html)

    def test_actual_status_preserves_terminal_unknown_readiness_and_historical_view(self):
        # Actual installed v2 read path; the helper's execution seams are not used.
        from test_official_execution import OfficialExecutionTests
        from test_official_v2 import grant, identity, BIRTH
        from hv2ref import product
        from hv2ref.official_documents import canonical
        helper=OfficialExecutionTests('test_preview_no_effect_and_binding')
        helper.setUpClass()
        try:
            helper.setUp()
            g=grant(str(helper.target));g['scope']['work_id']='official-work';c=Chain(g).launch();c.reserve(1);c.intent(1,'read');c.add('worker-started',worker_ordinal=1,pid=9011,birth=BIRTH)
            c.add('operator-resolved-unknown',grant=SHA,journal_head=c.rows[-1]['sha256'],previous_status='incomplete',documents={'Output':identity(),'Reference':identity(3)},process_absence=True,recovery_availability='missing',action='record-unknown-resolution')
            root=helper.target/'.hrn/executions'/SHA;root.mkdir(parents=True,mode=0o700)
            for name,raw in [('grant.json',state.canonical(c.grant)),('journal.jsonl',b''.join(canonical(r) for r in c.rows))]:
                (root/name).write_bytes(raw);(root/name).chmod(0o600)
            before={p.relative_to(root).as_posix():p.read_bytes() for p in root.iterdir()}
            observed=product.workspace_status(helper.target)
            self.assertTrue(observed['official_execution']['ready_for_new_grant'], observed['official_execution'])
            rec=observed['official_execution']['records'][0]
            legacy_keys=('grant','head','status','completed','pending','revoked','sealed','cancel_requested','schema_version','document_write_effect','recovery_availability','transient_presence','cleanup_marker_presence')
            self.assertTrue(set(legacy_keys)<=set(rec));self.assertEqual('official-work',rec['work_id'])
            with patch.object(view,'_live',wraps=view._live) as live:
                current,code=view.render_view(helper.target,kind='work',object_id='official-work')
            self.assertEqual(0,code);live.assert_called_once()
            self.assertIn('# 작업 진행',current)
            from hv2ref.work import WorkStore
            graph=WorkStore(helper.target)._all()['official-work'];rid=view._current_revision(graph)
            historical,code=view.render_view(helper.target,kind='work',object_id='official-work',revision=rid)
            self.assertEqual(0,code);self.assertNotIn('# 작업 진행',historical)
            self.assertIn('Selected revision fields',historical)
            self.assertEqual(before,{p.relative_to(root).as_posix():p.read_bytes() for p in root.iterdir()})
        finally:
            helper.doCleanups();helper.tearDownClass()


if __name__=='__main__': unittest.main()
