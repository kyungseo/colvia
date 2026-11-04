"""Default View summary, with synthetic observations and actual payload consumers."""
from __future__ import annotations

import copy
import sys
from pathlib import Path
import unittest
from unittest.mock import patch

from hv2ref import view
from hv2ref.product import verify_workspace_product, workspace_candidate
import test_productization_safety as fixtures



def label_graph(goal, *, goal_status="known", newer=False):
    """In-memory exact references, including an optional newer accepted goal."""
    from hv2ref.work import record_ref
    draft = {"revision_id": "draft-old", "acceptance_authority": "owner",
             "facets": {"goal": {"status": goal_status, "value": goal}}}
    accepted = {"id": "accepted-old", "sha256": "a" * 64}
    selection = {"selection_id": "intent-old", "revision_ref": record_ref(draft, "revision_id"), "acceptance_ref": accepted}
    selected = record_ref(selection, "selection_id")
    ref = {"authority_home_id": "home-a", "kind": "intent", "id": "intent-a",
           "selection_ref": selected, "revision_ref": selection["revision_ref"], "acceptance_ref": accepted}
    intent = {"identity": {"authority_home_id": "home-a"}, "current": {"selection_ref": selected},
              "chain": ["intent-old"], "selections": {"intent-old": selection}, "drafts": {"draft-old": draft}}
    if newer:
        latest = {"revision_id": "draft-new", "facets": {"goal": {"status": "known", "value": "UNRELATED NEW GOAL"}}}
        new_selection = {"selection_id": "intent-new", "revision_ref": record_ref(latest, "revision_id"), "acceptance_ref": accepted}
        intent["drafts"]["draft-new"] = latest
        intent["selections"]["intent-new"] = new_selection
        intent["chain"].append("intent-new")
        intent["current"] = {"selection_ref": record_ref(new_selection, "selection_id")}
    revision = {"record_id": "revision-a", "intent_ref": ref, "scope": ["docs/guide.md", "docs/faq.md"]}
    work_selection = {"record_id": "selection-a", "revision_ref": record_ref(revision)}
    work = {"current": {"selection_ref": record_ref(work_selection)}, "selections": {"selection-a": work_selection},
            "revisions": {"revision-a": revision}, "state": "review", "pending_decisions": [], "pending_selections": [],
            "continuation": {"effective_choice": None, "pending": [], "usage": {}}}
    return work, {"intent-a": intent}


class WorkLabelTests(unittest.TestCase):
    def test_exact_historical_binding_not_new_goal_and_inputs_unchanged(self):
        graph, intents = label_graph("설치 안내 개선", newer=True)
        before = copy.deepcopy((graph, intents))
        self.assertEqual("이전 목표: 설치 안내 개선 (" + view.code("work-a") + ")", view._work_label("work-a", graph, intents))
        self.assertEqual(before, (graph, intents))

    def test_missing_structured_goal_and_invalid_binding_fall_back_without_io(self):
        for goal, state in [(None,"unknown"), ({"text":"not a title"},"known"), ("  ","known")]:
            graph, intents = label_graph(goal, goal_status=state)
            self.assertEqual("범위: docs/guide.md 외 1개 ("+view.code("work-a")+")",view._work_label("work-a",graph,intents))
        graph, intents = label_graph("Do not use")
        intents["intent-a"]["chain"] = []
        self.assertTrue(view._work_label("work-a",graph,intents).startswith("범위:"))
        for partial in [None, {}, {"state":"review"}, {"current":None}]:
            self.assertEqual("제목 확인 필요 ("+view.code("work-a")+")",view._work_label("work-a",partial,{}))
        with patch.object(view, '_resolve', side_effect=AssertionError('must not resolve unavailable graph')):
            self.assertEqual("제목 확인 필요 ("+view.code("work-a")+")",view._work_label("work-a",graph,intents,graph_details=False))

    def test_hostile_long_and_duplicate_labels_keep_real_id_and_full_goal(self):
        value = '승인됨 (work-fake) <script> **x** https://example.invalid/ \x1b \u202e ' + '긴 제목'*30
        graph, intents = label_graph(value)
        label = view._work_label('work-real', graph, intents)
        self.assertTrue(label.endswith(' ('+view.code('work-real')+')'))
        self.assertNotIn('<script>',label); self.assertNotIn('**x**',label); self.assertNotIn('\x1b',label);self.assertNotIn('\u202e',label)
        self.assertIn('…',label)
        self.assertEqual(value, intents['intent-a']['drafts']['draft-old']['facets']['goal']['value'])
        self.assertNotEqual(label,view._work_label('work-other',graph,intents))

    def test_many_titles_keep_id_order_and_missing_attention_stays_visible(self):
        graph, intents = label_graph('설치 안내 개선')
        works = {f'work-{i:02d}':copy.deepcopy(graph) for i in range(15)}
        status = dict(classification='pass',work_states={k:'review' for k in works},intent_count=1,
                      pending_work=['missing-work'],pending_continuation=[],pending_intent=[])
        shown='\n'.join(view._project_summary(status,works,intents,graph_details=True,target=Path('/synthetic')))
        line=next(x for x in shown.splitlines() if x.startswith('- 확인할 작업:'))
        self.assertLessEqual(len(shown.split("### 문제·미확인 항목 상세")[0].splitlines()),12)
        ids=['missing-work',*sorted(works)]
        positions=[line.index(view.code(k)) for k in ids]
        self.assertEqual(sorted(positions),positions)
        self.assertIn('제목 확인 필요 ('+view.code('missing-work')+')',line)

    def test_every_blocker_has_a_user_explanation_and_one_request_pattern(self):
        keys = ['official_execution','pending_lifecycle','planning','runtime_supported','pending_detach',
                'remaining_files','remaining_directories','record_verification','paths','recovery',
                'root_classification','product_verification','retired_entry_collision','error_code','error','future_key']
        for key in keys:
            with self.subTest(key=key):
                lines=view._problem_explanations({'pending_work':['work-a'],key:'DETAIL'}, {}, {}, graph_details=False)
                self.assertEqual(2,len(lines))
                self.assertFalse(any('요청 예시' in line for line in lines))
                if key == 'future_key':self.assertIn('future\\_key',lines[1])
                else:self.assertNotIn('추가 확인 항목이 있습니다:',lines[1])
        graph,intents=label_graph('작업 진행 화면 개선')
        graph.update(continuation={'effective_choice':None,'pending':[],'usage':{}})
        intent=intents['intent-a'];intent.update(pending_acceptances=[],pending_selections=[])
        works={f'work-{i:02d}':copy.deepcopy(graph) for i in range(15)}
        status=dict(classification='pass',work_states={k:'review' for k in works},intent_count=1,
                    pending_work=[],pending_intent=[],pending_continuation=[])
        with patch.object(view,'safe_target',return_value=Path('/synthetic')), \
             patch.object(view,'_observe',return_value=(status,works,intents)), \
             patch.object(view,'_product',return_value=None), \
             patch.object(view,'render_candidates',return_value=([],None)):
            shown,exit_code=view.render_view('/synthetic')
        self.assertEqual(0,exit_code)
        self.assertEqual(1,shown.count('더 알아보기 ·'))
        self.assertNotIn('- 요청 예시:',shown)
        self.assertNotIn('후속 목표:',shown)
        self.assertIn('- 후속 기록 조회 — 작업 진행 화면 개선',shown)
        self.assertIn('- 작업 조회 — 작업 진행 화면 개선',shown)
        self.assertNotIn('진단 상세',shown.split('## 프로젝트 세부 정보')[0])
        self.assertLess(shown.index('더 알아보기 ·'),shown.index('## 프로젝트 세부 정보'))
        for wid in works:
            self.assertIn(view.code(wid),shown)
            self.assertIn(view.code(view._view_command(Path('/synthetic'),False,'work',wid)),shown)

    def test_explanation_precedes_preserved_raw_diagnostics(self):
        graph,intents=label_graph('설치 안내 개선')
        status=dict(classification='degraded',work_states={'work-a':'review'},intent_count=1,
                    continuation_unavailable={'work-a':{'message':'EXACT CAUSE'}},pending_work=[],pending_intent=[],
                    pending_continuation=None,lifecycle_ready=False)
        shown='\n'.join(view._project_summary(status,{'work-a':graph},intents,graph_details=True,target=Path('/synthetic')))
        self.assertLess(shown.index('후속 계획·선택 기록을 읽을 수 없습니다'),shown.index('#### 진단 상세'))
        self.assertLess(shown.index('다음 확인 방법을 물어보세요'),shown.index('#### 진단 상세'))
        self.assertIn('EXACT CAUSE',shown); self.assertIn('pending\\_continuation: 확인 불가',shown)
        self.assertIn('lifecycle\\_ready: False',shown)


class SummaryObservationTests(unittest.TestCase):
    def status(self, **changes):
        return dict(classification='pass', authoritative_control=True,
                    work_states={}, intent_count=0, pending_work=[], pending_intent=[],
                    pending_continuation=[], **changes)

    def summary(self, status, works=None, intents=None, *, graph_details=True):
        works = {} if works is None else works
        intents = {} if intents is None else intents
        before = copy.deepcopy((status, works, intents))
        result = '\n'.join(view._project_summary(status, works, intents, graph_details=graph_details, target=Path("/synthetic/worktree")))
        self.assertEqual(before, (status, works, intents))
        return result

    def test_detached_parent_shows_planned_child_before_registration(self):
        from hv2ref.work import record_ref
        graph, intents = label_graph("예약 정책")
        draft = intents["intent-a"]["drafts"]["draft-old"]
        draft["composition"] = {"required_children": [{"work": {"id": "not-started"}}]}
        revision = graph["revisions"]["revision-a"]
        revision["schema_version"] = 2
        revision["intent_ref"]["revision_ref"] = record_ref(draft, "revision_id")
        selection = graph["selections"]["selection-a"]
        selection["revision_ref"] = record_ref(revision)
        graph["current"]["selection_ref"] = record_ref(selection)
        graph["state"] = "active"
        status = self.status()
        status.update(classification="detached", work_states={"parent": "active"})
        lines = view._project_summary(status, {"parent": graph}, intents,
                                      graph_details=True, target=Path("/synthetic"), compact=True)
        self.assertTrue(any("계획에 포함된 하위 작업" in line for line in lines))
        self.assertTrue(any("not-started" in line and "등록 전" in line for line in lines))

    def test_empty_known_records_and_unknown_records_are_distinct(self):
        known = self.summary(self.status())
        self.assertIn('작업 0개 / 목표 0개', known)
        self.assertIn('설치·기록 점검: 설치와 작업 기록의 기본 점검을 통과했습니다.', known)
        self.assertIn('원하는 작업을 설명하고 목표와 범위를 정리해 달라고 요청하세요',known)
        self.assertNotIn('작업 제목이나 ID를 넣어',known)
        self.assertNotIn('진단 상세',known)
        with_goal=self.status();with_goal['intent_count']=1
        self.assertIn('등록된 목표를 바탕으로',self.summary(with_goal))
        self.assertNotIn('관측 상태', known)
        self.assertNotIn('pass', known)
        unknown = self.summary({'classification':'degraded', 'message':'unreadable'})
        self.assertIn('작업 확인 불가 / 목표 확인 불가', unknown)
        self.assertNotIn('작업 0개', unknown)
        self.assertIn('unreadable', unknown)
        self.assertNotIn('기본 점검을 통과', unknown)

    def test_root_damage_paths_and_unrun_verification_are_visible(self):
        shown=self.summary({'classification':'degraded', 'error':'HV2-WORKSPACE-UNKNOWN',
                            'paths':['.gitignore', 'format.json'], 'record_verification':'not-run',
                            'root_classification':'integrity-failure'})
        for marker in ['HV2-WORKSPACE-UNKNOWN','.gitignore','format.json','not-run','integrity-failure']:
            self.assertIn(marker,shown)
        self.assertNotIn('기본 점검을 통과',shown)

    def test_multiple_works_do_not_select_a_task_or_promote_historical_action(self):
        status = self.status()
        status.update(work_states={'work-a':'completed', 'work-b':'review'}, intent_count=2,
                      next_action='FORGED EXECUTE NOW')
        shown = self.summary(status, {'work-a':{'state':'completed'}, 'work-b':{'state':'review'}})
        self.assertIn('작업 2개 / 목표 2개', shown)
        self.assertIn('결과 검토 대기 1개', shown)
        self.assertIn('결과 수락 완료 1개', shown)
        self.assertIn('확인할 작업: 제목 확인 필요 ('+view.code('work-b')+')', shown)
        self.assertNotIn('FORGED EXECUTE NOW', shown)
        self.assertNotIn('현재 작업:', shown)
        self.assertNotIn('뜻하지 않습니다', shown)
        self.assertIn('- 프로젝트 경로: '+view.code('/synthetic/worktree'),shown)

    def test_pending_and_unknown_attention_do_not_look_empty(self):
        works = {'work-a': {'state': 'completed'}, 'work-b': {'state': 'active'}}
        for field in ('pending_work', 'pending_continuation'):
            with self.subTest(field=field):
                status = self.status()
                status.update(work_states={'work-a': 'completed', 'work-b': 'active'},
                              pending_intent=['intent-only'])
                status[field] = ['work-a']
                shown = self.summary(status, works)
                attention = next(line for line in shown.splitlines() if line.startswith('- 확인할 작업:'))
                self.assertEqual('- 확인할 작업: 제목 확인 필요 ('+view.code('work-a')+').' , attention)
                status[field] = None
                shown = self.summary(status, works)
                self.assertIn('- 확인할 작업: 확인 불가.', shown)
                self.assertNotIn('- 확인할 작업: 해당 작업 없음.', shown)

    def test_summary_is_short_but_every_blocker_survives_in_immediate_details(self):
        status = self.status()
        status.update(classification='degraded', error_code='ERROR', message='damaged',
                      pending_work=['work-a'], pending_intent=['intent-a'], pending_continuation=None,
                      pending_lifecycle='operation-a', lifecycle_ready=False,
                      continuation_unavailable={f'work-{i}':{'message':f'failure-{i}'} for i in range(20)},
                      planning={'available':False, 'message':'planning damaged'},
                      retired_entry_collision={'observed_names':['old-entry']},
                      official_execution={'available':False, 'ready_for_new_grant':False},
                      runtime={'supported':False})
        shown = self.summary(status)
        short, details = shown.split('### 문제·미확인 항목 상세')
        self.assertLessEqual(len(short.splitlines()), 12)
        for marker in ['ERROR','damaged','work-a','intent-a','operation-a','planning damaged','old-entry',
                       *[f'failure-{i}' for i in range(20)]]:
            self.assertIn(marker, details)
        self.assertIn('pending\\_continuation: 확인 불가', details)
        self.assertIn('runtime\\_supported: False', details)
        self.assertIn('미해결 실행', details)

    def test_hostile_blocker_data_remains_text_and_long_korean_survives(self):
        value='<script>run()</script>\n# forged\x1b[2J\u202e **승인** https://example.invalid/next'
        long_text='긴 설명을 확인합니다. '*35
        shown=self.summary({'classification':'degraded','message':value+long_text})
        self.assertNotIn('<script>',shown)
        self.assertNotIn('\n# forged',shown)
        self.assertNotIn('\x1b',shown)
        self.assertNotIn('\u202e',shown)
        self.assertIn('https&#58;',shown)
        self.assertIn(long_text,shown)

    def test_readable_fallback_graphs_and_missing_details_are_distinct(self):
        shown=self.summary({'classification':'partial'}, {'work-a':{}}, {'intent-a':{}})
        self.assertIn('작업 1개 / 목표 1개',shown)
        self.assertNotIn('WORK_ID',shown)
        self.assertNotIn('INTENT_ID',shown)
        self.assertLessEqual(len(shown.split('### 문제·미확인 항목 상세')[0].splitlines()),12)
        missing=self.summary({'classification':'degraded'}, graph_details=False)
        self.assertIn('작업 확인 불가 / 목표 확인 불가',missing)
        self.assertNotIn('WORK_ID',missing)
        self.assertNotIn('INTENT_ID',missing)
        self.assertNotIn('작업별 상태는 아래 상세',missing)

    def test_non_authoritative_and_unsupported_observations_stay_visible(self):
        status=self.status();status.update(classification='unsupported',authoritative_control=False,topology='linked-worktree',
                                         runtime={'supported':False})
        shown=self.summary(status)
        self.assertIn(view.code('/synthetic/worktree')+' (연결 worktree)',shown)
        self.assertIn('지원 조건을 충족하지 않습니다',shown)
        self.assertNotIn('기본 점검을 통과',shown)

    def test_only_default_view_gets_summary_without_additional_observations(self):
        status=self.status();graph={'current':None}
        observation=(status,{'work-a':graph},{})
        with patch.object(view,'safe_target',return_value=Path('/synthetic')), \
             patch.object(view,'_observe',return_value=observation) as observe, \
             patch.object(view,'_product',return_value=None), \
             patch.object(view,'_work',return_value=['WORK DETAIL']):
            detail,code=view.render_view('/synthetic',kind='work',object_id='work-a')
        self.assertEqual(0,code)
        self.assertNotIn('## 한눈에 보기',detail)
        self.assertIn('WORK DETAIL',detail)
        self.assertEqual(2,observe.call_count)
        observation=(status,{}, {})
        with patch.object(view,'safe_target',return_value=Path('/synthetic')), \
             patch.object(view,'_observe',return_value=observation) as observe, \
             patch.object(view,'_product',return_value=None), \
             patch.object(view,'render_candidates',return_value=(['CANDIDATE DETAIL'],None)):
            default,code=view.render_view('/synthetic')
        self.assertEqual(0,code)
        self.assertEqual(2,observe.call_count)
        self.assertLess(default.index('## 한눈에 보기'),default.index('## 프로젝트 세부 정보'))
        self.assertIn('CANDIDATE DETAIL',default)
        self.assertIn('## Intents',default)
        self.assertIn('## Works',default)

    def test_unstable_observation_discards_summary_and_preserves_exit(self):
        states=[({'classification':x}, {}, {}) for x in ['degraded','partial','degraded','partial']]
        with patch.object(view,'safe_target',return_value=Path('/synthetic')), \
             patch.object(view,'_observe',side_effect=states) as observe, \
             patch.object(view,'_product',return_value=None):
            shown,code=view.render_view('/synthetic')
        self.assertEqual(10,code)
        self.assertEqual(4,observe.call_count)
        self.assertIn('Observation unstable',shown)
        self.assertNotIn('## 한눈에 보기',shown)

    def test_nonpass_exit_codes_survive_summary(self):
        for classification,expected in view.EXITS.items():
            with self.subTest(classification=classification), \
                 patch.object(view,'safe_target',return_value=Path('/synthetic')), \
                 patch.object(view,'_observe',return_value=({'classification':classification},{},{})), \
                 patch.object(view,'_product',return_value=None), \
                 patch.object(view,'render_candidates',return_value=([],None)):
                shown,code=view.render_view('/synthetic')
                self.assertEqual(expected,code)
                self.assertIn(classification,shown)
                self.assertNotIn('기본 점검을 통과',shown)


    def test_problem_classifications_never_say_no_problem(self):
        for classification in ('conflict','stale','partial','degraded'):
            status=self.status();status['classification']=classification
            shown=self.summary(status)
            self.assertIn('- 먼저 확인:',shown)
            self.assertNotIn('발견된 문제는 없습니다',shown)
            self.assertNotIn('기본 점검을 통과',shown)
            self.assertLess(shown.index('- 먼저 확인:'),shown.index('- 작업 진행'))

    def test_complete_commands_preserve_arguments_for_cli_and_shell(self):
        import shlex
        from hv2ref.cli import parser, workspace_parser
        target=Path("/synthetic/project with 'quote' $(literal)")
        for installed in (False,True):
            for kind in ('work','continuation','intent'):
                with patch.object(view.sys,'platform','darwin'):
                    command=view._view_command(target,installed,kind,'work_a')
                args=shlex.split(command)
                if installed:
                    self.assertEqual(str(target/'colvia'),args[0])
                    parsed=workspace_parser(target).parse_args(args[1:])
                else:
                    self.assertEqual(str(Path(view.__file__).parents[2]/'colvia'),args[0])
                    self.assertEqual('--source-checkout',args[1])
                    parsed=parser().parse_args(args[2:])
                self.assertEqual(kind,parsed.kind)
                self.assertEqual('work_a',parsed.object_id)
                self.assertEqual(str(target),str(parsed.target))


class SummaryPayloadConsumerTests(unittest.TestCase):
    def test_current_guidance_and_view_survive_update_repair_detach(self):
        f=fixtures.ActualWorkspaceInitTests();f.setUp();self.addCleanup(f.doCleanups)
        changed=('adapters/colvia-work/SKILL.md','docs/REFERENCE.md','src/hv2ref/view.py','src/hv2ref/cli.py','AGENTS.md','README.md','docs/README.md','docs/CONCEPTS.md','docs/GETTING-STARTED.md')
        previous=f.switch_candidate()
        # Synthetic previous payload: byte differences, not a claimed historic release.
        for name in changed:
            with (previous/name).open('a') as stream:
                stream.write('\n# Synthetic previous payload marker.\n')
        f.apply_init(f.preview(source=previous),source=previous)
        f.candidate=f.source
        f.switch_apply(f.switch_preview(installed=True),installed=True)
        candidate=workspace_candidate(f.source)
        def check_payload():
            product=verify_workspace_product(f.target)
            self.assertEqual(candidate['inventory'],product['inventory'])
            root=Path(product['release_path'])/'payload'
            for name in changed:self.assertEqual((f.source/name).read_bytes(),(root/name).read_bytes())
            before=fixtures.exact_snapshot(f.target)
            default=f.installed(['view']).stdout.decode()
            self.assertEqual(before,fixtures.exact_snapshot(f.target))
            self.assertIn('## 한눈에 보기',default)
            self.assertIn(view.code(str(f.target)),default.split('## 프로젝트 세부 정보')[0])
            self.assertIn('작업 0개 / 목표 0개',default)
            self.assertNotIn('natural_language_adapter:',default)
            detailed=f.installed(['view','--details']).stdout.decode()
            self.assertIn('### 안내 문서',detailed)
            self.assertIn('natural_language_adapter:',detailed)
            self.assertEqual(before,fixtures.exact_snapshot(f.target))
            self.assertIn('## Continue After A Progress Report',(root/changed[0]).read_text())
            return root
        active=check_payload()
        with (active/changed[0]).open('a') as stream:stream.write('\nDAMAGED\n')
        f.repair_apply(f.repair_preview())
        check_payload()
        f.detach_apply(f.detach_preview())
        before=fixtures.exact_snapshot(f.target)
        detached=f.call(['view','--target',f.target]).stdout.decode()
        self.assertEqual(before,fixtures.exact_snapshot(f.target))
        self.assertIn('## 한눈에 보기',detached)
        self.assertIn('작업 확인 불가 / 목표 확인 불가',detached)
        self.assertNotIn('natural_language_adapter',detached.replace('\\_', '_'))
        self.assertFalse((f.target/'colvia').exists())


class SummaryRetainedStateTests(unittest.TestCase):
    def setUp(self):
        self.f=fixtures.ActualWorkspaceInitTests();self.f.setUp();self.addCleanup(self.f.doCleanups)

    def screen(self, expected):
        before=fixtures.exact_snapshot(self.f.target)
        shown,code=view.render_view(self.f.target)
        self.assertEqual(expected,code,shown)
        self.assertEqual(before,fixtures.exact_snapshot(self.f.target))
        return shown

    def test_actual_pending_update_partial_detach_and_retained_graph_counts(self):
        f=self.f;f.apply_init(f.preview());f.complete_work()
        f.candidate=f.switch_candidate();up=f.switch_preview()
        f.switch_apply(up,point='after-receipt',expected=75)
        pending=self.screen(14)
        self.assertIn('작업 1개 / 목표 1개',pending)
        self.assertIn('work: work-a',pending)
        self.assertIn('pending\\_lifecycle: switch-a',pending)
        f.switch_apply(up,recover=True)
        detach=f.detach_preview();f.detach_apply(detach,point='after-receipt',expected=75)
        partial=self.screen(14)
        self.assertIn('작업 1개 / 목표 1개',partial)
        self.assertIn('Colvia 제거가 진행 중',partial)
        self.assertIn('pending\\_detach: detach-a',partial)
        self.assertIn('remaining\\_files',partial)
        self.assertIn('- 프로젝트 경로: '+view.code(str(f.target)),partial)
        f.detach_apply(detach,recover=True)
        retained=self.screen(0)
        self.assertIn('작업 1개 / 목표 1개',retained)
        self.assertIn('work: work-a',retained)
        self.assertIn('Colvia가 제거된 상태입니다',retained)
        self.assertIn('- 프로젝트 경로: '+view.code(str(f.target)),retained)
        self.assertIn('### fixture ('+view.code('work-a')+')',retained)
        self.assertEqual(1,retained.count('더 알아보기 ·'))
        self.assertNotIn('- 요청 예시:',retained)
        self.assertLess(retained.index('더 알아보기 ·'),retained.index('## 프로젝트 세부 정보'))
        self.assertIn(view.code(view._view_command(f.target,False,'work','work-a')),retained)

    def test_actual_partial_bootstrap_never_presents_empty_as_verified_zero(self):
        f=self.f;f.apply_init(f.preview(),point='after-plan',expected=75)
        self.assertFalse((f.target/'.hrn/format.json').exists())
        shown=self.screen(14)
        self.assertIn('작업 확인 불가 / 목표 확인 불가',shown)
        self.assertIn('작업 목록을 확인할 수 없습니다',shown)
        self.assertIn('목표 목록을 확인할 수 없습니다',shown)
        self.assertNotIn('No Work.',shown)
        self.assertNotIn('No accepted intent',shown)
        self.assertNotIn('WORK_ID',shown)

    def test_actual_root_and_continuation_damage_keep_cause_and_available_records(self):
        f=self.f;f.apply_init(f.preview());f.complete_work()
        ignore=f.target/'.hrn/.gitignore';original=ignore.read_bytes();ignore.write_bytes(b'changed\n')
        broken=self.screen(10)
        self.assertIn('.gitignore',broken)
        self.assertIn('preserve bytes; do not overwrite a torn or modified file',broken)
        self.assertIn('작업 확인 불가 / 목표 확인 불가',broken)
        self.assertNotIn('view work WORK_ID',broken)
        ignore.write_bytes(original)
        home=f.target/'.hrn/work/work-a/continuation';home.mkdir(exist_ok=True)
        (home/'unknown.json').write_bytes(b'{}\n')
        continuation=self.screen(10)
        self.assertIn('작업 1개 / 목표 1개',continuation)
        self.assertIn('continuation\\_unavailable',continuation)
        self.assertIn('pending\\_continuation: 확인 불가',continuation)
        self.assertIn('work: work-a',continuation)
        self.assertIn('- fixture ('+view.code('work-a')+'): 후속 계획·선택 기록을 읽을 수 없습니다.',continuation)
        self.assertNotIn('- 확인할 작업: 해당 작업 없음.',continuation)
        self.assertIn('후속 계획·선택 기록을 읽을 수 없습니다',continuation)
        self.assertEqual(1,continuation.count('더 알아보기 ·'))


class OverviewHelpTests(unittest.TestCase):
    def fixture(self):
        graph, intents = label_graph("작업 진행 화면 개선")
        intents["intent-a"].update(pending_acceptances=[], pending_selections=[])
        graph["continuation"]["usage"] = {"normal_remaining": 256}
        status = dict(classification="pass", authoritative_control=True, work_states={"work-a":"review"},
                      intent_count=1, pending_work=[], pending_intent=[], pending_continuation=[],
                      runtime={"supported":True}, planning={"available":True}, next_action="EXACT ACTION")
        product = dict(release_path="/synthetic/.hrn/product/releases/test", inventory={"inventory_id":"continuation-1"})
        return status, {"work-a":graph}, intents, product

    def render(self, status, works, intents, product, **kwargs):
        with patch.object(view, "safe_target", return_value=Path("/synthetic")), \
             patch.object(view, "_observe", return_value=(status,works,intents)) as observe, \
             patch.object(view, "_product", return_value=product), \
             patch.object(view, "render_candidates", return_value=(["EXACT CANDIDATES"], {"present":False})):
            result = view.render_view("/synthetic", **kwargs)
            self.assertEqual(2, observe.call_count)
            return result

    def test_decision_precedes_counts_and_limits_the_first_screen(self):
        status, works, intents, product = self.fixture()
        for index in range(4):
            works[f'work-b{index}'] = copy.deepcopy(works['work-a'])
        status['work_states'] = dict.fromkeys(works, 'review')
        shown, code = self.render(status, works, intents, product)
        self.assertEqual(0, code)
        top = shown.split('- 프로젝트 경로:', 1)[0]
        self.assertLess(top.index('작업 진행 화면 개선 (' + view.code('work-a')), top.index('작업 5개'))
        self.assertEqual(top.count('수락할지 보완을 요청할지'), 3)
        self.assertIn('그 밖에 확인할 항목 2건', top)
        self.assertNotIn(view.code('work-b3'), top)
        self.assertIn(view.code('work-b3'), shown)

    def test_partial_record_and_active_work_do_not_request_acceptance(self):
        status, works, intents, product = self.fixture()
        works['work-a']['state'] = status['work_states']['work-a'] = 'active'
        shown, _ = self.render(status, works, intents, product)
        top = shown.split('- 프로젝트 경로:', 1)[0]
        self.assertIn('진행 중: 작업 진행 화면 개선', top)
        self.assertNotIn('결정해 주세요', top)
        status.update(continuation_unavailable={'work-a': {}}, pending_continuation=None)
        works['work-a']['state'] = status['work_states']['work-a'] = 'review'
        top = self.render(status, works, intents, product)[0].split('- 프로젝트 경로:', 1)[0]
        self.assertIn('후속 계획을 읽을 수 없습니다', top)
        self.assertIn('전체 판단 대상을 집계할 수 없습니다', top)
        self.assertNotIn('수락할지', top)

    def test_execution_summary_keeps_recorded_target_separate_from_current_result(self):
        status, works, intents, product = self.fixture()
        record = dict(schema_version=2, work_id='work-a', grant='run-1', status='unknown',
                      document_write_effect='unknown', process_observation='closed',
                      effect_refs=[], closure_refs=[])
        status['official_execution'] = dict(available=True, ready_for_new_grant=False, records=[record])
        shown, _ = self.render(status, works, intents, product)
        top = shown.split('- 프로젝트 경로:', 1)[0]
        self.assertIn('실행 당시 작업 (' + view.code('work-a') + ') · 문서 반영 여부가 불명확', top)
        self.assertNotIn('수락할지', top)
        self.assertNotIn('작업 진행 화면 개선', top)
        record['process_observation'] = 'unconfirmed'
        top = self.render(status, works, intents, product)[0].split('- 프로젝트 경로:', 1)[0]
        self.assertIn('실행이 끝났는지', top)
        record.update(status='operator-resolved-unknown', process_observation='closed')
        status['official_execution']['ready_for_new_grant'] = True
        top = self.render(status, works, intents, product)[0].split('- 프로젝트 경로:', 1)[0]
        self.assertNotIn('실행 당시 작업', top)
        self.assertIn('수락할지', top)
        details, _ = self.render(status, works, intents, product, details=True)
        self.assertIn('정리된 실행', details)
        self.assertIn(view.code('run-1'), details)

    def test_decision_fallback_does_not_invent_current_state(self):
        status, works, intents, product = self.fixture()
        status.update(pending_work=['unknown-id'], planning={'available': False})
        first = self.render(status, works, intents, product)[0].split('- 프로젝트 경로:', 1)[0]
        self.assertIn('제목 확인 필요 (' + view.code('unknown-id') + ') · 작업 기록을 읽을 수 없습니다', first)
        self.assertNotIn('수락할지', first)
        status, works, intents, product = self.fixture()
        status['official_execution'] = dict(available=False, ready_for_new_grant=False)
        first = self.render(status, works, intents, product)[0].split('- 프로젝트 경로:', 1)[0]
        self.assertIn('실행 기록을 읽을 수 없습니다', first)
        self.assertNotIn('수락할지', first)

    def test_partial_counts_keep_each_unlinked_execution(self):
        status, works, intents, product = self.fixture()
        status.update(pending_continuation=None, official_execution=dict(available=True,
                      ready_for_new_grant=False, records=[dict(grant=f"run-{n}", status="incomplete")
                                                         for n in range(4)]))
        first = self.render(status, works, intents, product)[0].split('- 프로젝트 경로:', 1)[0]
        self.assertEqual(3, first.count('작업 연결을 확인할 실행'))
        self.assertIn('확인된 범위에서 추가로 확인할 항목 2건', first)
        self.assertIn('전체 판단 대상을 집계할 수 없습니다', first)

    def test_incomplete_runtime_information_and_historical_goal(self):
        status, works, intents, product = self.fixture()
        status['runtime'] = None
        shown, _ = self.render(status, works, intents, product)
        self.assertIn('실행 환경 정보를 읽을 수 없습니다', shown)
        self.assertNotIn('수락할지', shown.split('- 프로젝트 경로:', 1)[0])
        status, works, intents, product = self.fixture()
        graph, history = label_graph('설치 안내 정리', newer=True)
        intents['intent-a'].update(history['intent-a'])
        works['work-a'].update(graph)
        status['official_execution'] = dict(available=True, ready_for_new_grant=False, records=[])
        first = self.render(status, works, intents, product)[0].split('- 프로젝트 경로:', 1)[0]
        self.assertIn('실행 기록과 아래 진단 상세를 확인', first)
        self.assertIn('이전 목표: 설치 안내 정리', first)
        self.assertNotIn('UNRELATED NEW GOAL', first)

    def test_clean_default_and_explicit_details_preserve_order_and_information(self):
        values=self.fixture(); shown,code=self.render(*values)
        self.assertEqual(0,code)
        self.assertIn("### 작업 진행 화면 개선 ("+view.code("work-a")+")",shown)
        self.assertIn("후속 계획: 아직 정하지 않음",shown)
        self.assertIn("등록된 다음 작업 후보는 아직 없습니다. 필요하면 다음 할 일을 함께 정리할 수 있습니다.",shown)
        self.assertNotIn("이 작업 공간에 기록된 다음 작업 후보가 없습니다.",shown)
        self.assertNotIn("## Intents",shown);self.assertNotIn("stored\\_state",shown)
        self.assertNotIn("EXACT ACTION",shown)
        self.assertLess(shown.index("### 작업"),shown.index("더 알아보기"))
        self.assertNotIn("natural_language_adapter",shown)
        self.assertIn("독립된 소스",shown)
        detailed,code=self.render(*values,details=True)
        for marker in ("## Intents", "## Works", "EXACT ACTION", "직접 조회 명령"):
            self.assertIn(marker,detailed)
        self.assertLess(detailed.index("더 알아보기"),detailed.index("## Intents"))
        self.assertNotIn("먼저 확인",detailed)
        self.assertIn("natural_language_adapter",detailed)
        self.assertLess(detailed.index("## 프로젝트 세부 정보"),detailed.index("### 안내 문서"))
        self.assertNotIn("기술 상세·안내 문서:",detailed)

    def test_empty_candidate_copy_requires_absence_without_error(self):
        status,works,intents,product=self.fixture()
        message="등록된 다음 작업 후보는 아직 없습니다. 필요하면 다음 할 일을 함께 정리할 수 있습니다."
        for observed in ({"present":False,"error_code":"unavailable"},{"present":True},{"error_code":"unknown"}):
            with self.subTest(observed=observed), patch.object(view,"safe_target",return_value=Path("/synthetic")), patch.object(view,"_observe",return_value=(status,works,intents)), patch.object(view,"_product",return_value=product), patch.object(view,"render_candidates",return_value=(["CANDIDATE DETAIL"],observed)):
                shown,_=view.render_view("/synthetic")
                self.assertNotIn(message,shown)
                self.assertIn("CANDIDATE DETAIL",shown)

    def test_non_normal_observations_keep_raw_reason_and_next_action(self):
        for changes in ({"authoritative_control":False},{"runtime":{}},{"planning":{"available":False}},
                        {"official_execution":{"available":False}}, {"pending_intent":["intent-a"]},
                        {"classification":"detached"}, {"pending_work":None}, {"error":"unexpected"}, {"pending_lifecycle":"op-a"}):
            with self.subTest(changes=changes):
                status,works,intents,product=self.fixture();status.update(changes)
                shown,_=self.render(status,works,intents,product)
                self.assertIn("EXACT ACTION",shown);self.assertIn("## Intents",shown)
                if status["classification"] == "pass":self.assertIn("먼저 확인",shown)
                self.assertIn("natural_language_adapter",shown)
                self.assertLess(shown.index("## 프로젝트 세부 정보"),shown.index("### 안내 문서"))
                self.assertNotIn("기술 상세·안내 문서:",shown)

    def test_follow_up_states_usage_pending_and_stale_are_distinct(self):
        status,works,intents,product=self.fixture();graph=works["work-a"];state=graph["continuation"]
        choices=[(None,"아직 정하지 않음"),({"kind":"none"},"후속 작업 없음으로 선택됨"),
                 ({"kind":"proposal","goal":"다음 개선"},"제안 — 다음 개선"),
                 ({"kind":"work","target":{"object":{"id":"work-b"}}},"작업 연결 기록")]
        for choice,label in choices:
            state["effective_choice"]=choice
            self.assertIn(label,"\n".join(view._work_overview("work-a",graph,intents,works)))
        state.update(pending="pending-a", usage={}, effective_ticket={"source":{}})
        shown="\n".join(view._work_overview("work-a",graph,intents,works))
        self.assertIn("남은 횟수를 확인할 수 없습니다",shown);self.assertIn("기록 처리가 끝나지",shown)
        self.assertIn("일치 여부를 확인할 수 없습니다",shown)
        state["usage"]={"normal_remaining":0}
        self.assertIn("횟수를 모두 사용", "\n".join(view._work_overview("work-a",graph,intents,works)))
        graph.update(continuation=None,pending_decisions=["decision-a"])
        shown="\n".join(view._work_overview("work-a",graph,intents,works))
        self.assertIn("기록을 읽을 수 없습니다",shown);self.assertIn("작업 기록 처리가 끝나지",shown)
        self.assertNotIn("아직 정하지 않음",shown)

    def test_details_invalid_combinations_do_not_consume_input_or_observe(self):
        from hv2ref.cli import parser
        for args in (["view","confirmation","--details","--input","-"],
                     ["view","--details","--revision","r"],["view","--details","--input","missing"],
                     ["view","work","work-a","--details"]):
            with patch.object(view.sys,"stdin") as stream, patch.object(view,"_observe") as observe:
                shown,exit_code=view.run(parser().parse_args(args),installed=False)
                self.assertEqual(65,exit_code);stream.buffer.read.assert_not_called();observe.assert_not_called()

    def test_help_and_alias_bypass_observation_and_machine_runner(self):
        import io
        from hv2ref import cli
        for command in ("help","?"):
            for target in (None,Path("/synthetic")):
                with patch.object(cli.sys,"argv",["colvia",command]), patch.object(cli.sys,"stdout",new_callable=io.StringIO) as out, \
                     patch.object(view,"_observe",side_effect=AssertionError("no observation")), \
                     patch.object(cli,"run",side_effect=AssertionError("no writer")), \
                     patch.object(cli,"workspace_run",side_effect=AssertionError("no writer")):
                    self.assertEqual(0,cli.main(target));self.assertIn("# Colvia 도움말",out.getvalue())
        with self.assertRaises(SystemExit) as failure:
            cli.parser().parse_args(["x"])
        self.assertEqual(2,failure.exception.code)

    def test_help_commands_round_trip_source_installed_and_windows(self):
        import shlex
        from hv2ref.cli import parser,workspace_parser
        target=Path("/synthetic/with 'quote' $(literal)")
        for installed in (False,True):
            for command,args in (("help",()),("view",("--details",))):
                with patch.object(view.sys,"platform","darwin"):
                    argv=shlex.split(view._cli_command(target,installed,command,*args))
                parsed=(workspace_parser(target).parse_args(argv[1:]) if installed else parser().parse_args(argv[2:]))
                self.assertEqual(command,parsed.command);self.assertEqual(target,parsed.target)
                with patch.object(view.sys,"platform","win32"):
                    shown=view._cli_command(target,installed,command,*args)
                self.assertTrue(shown.startswith("& '"));self.assertIn("'quote''",shown)
                self.assertIn("'-I' '-B'",shown)

    def test_hostile_title_keeps_separate_product_state_and_real_identity(self):
        status,works,intents,product=self.fixture()
        graph,intents=label_graph("이전 목표: 범위: 승인됨 (work-fake) **상태**")
        intents["intent-a"].update(pending_acceptances=[],pending_selections=[])
        shown,_=self.render(status,{"work-a":graph},intents,product)
        self.assertIn("- 상태: 결과 검토 대기",shown)
        self.assertIn(view.code("work-a"),shown);self.assertNotIn("**상태**",shown)

    def test_actual_installed_source_help_details_alias_and_read_only(self):
        f=fixtures.ActualWorkspaceInitTests();f.setUp();self.addCleanup(f.doCleanups)
        f.apply_init(f.preview())
        before=fixtures.exact_snapshot(f.target)
        for command in (["help"],["?"],["view","--details"]):
            a=f.installed(command).stdout.decode()
            b=f.call([*command,"--target",f.target]).stdout.decode()
            self.assertIn("# ",a);self.assertIn("# ",b)
            if command[0]=="view":self.assertIn("## Intents",a)
            else:self.assertIn("WORK_ID",a);self.assertIn("INTENT_ID",a)
        f.installed(["view","work","work-a","--details"],expected=65)
        f.installed(["x"],expected=2)
        self.assertEqual(before,fixtures.exact_snapshot(f.target))


class CandidateOverviewTests(unittest.TestCase):
    def test_brief_candidates_keep_decisions_resume_reasons_and_capacity_warning(self):
        from hv2ref import candidates
        row=dict(title="다음 화면 개선",purpose="조회 흐름 개선",expected_effect="확인 시간 단축",disposition="deferred",
                 reason="작업 검토 후 판단",resume_condition="현재 결과 수락 후",links=[],related_candidates=[])
        store=dict(candidates={"candidate-a":row},decisions=[],selected=None,authority_home_id="home-a")
        observed=dict(present=True,sha256="a"*64,store=store)
        with patch.object(candidates,"read_candidates",return_value=observed),patch.object(candidates,"MAX_CANDIDATES",1):
            brief,_=view.render_candidates(Path("/synthetic"),works={},intents={},brief=True)
            full,_=view.render_candidates(Path("/synthetic"),works={},intents={})
        brief="\n".join(brief);full="\n".join(full)
        for marker in ("작업 검토 후 판단","현재 결과 수락 후","한도 근접","candidate-a"):
            self.assertIn(marker,brief);self.assertIn(marker,full)
        self.assertIn("### 다음 화면 개선 ("+view.code("candidate-a")+")",brief)
        self.assertIn("상태: 보류",brief);self.assertNotIn("digest",brief)
        self.assertIn("후보 기록 digest",full);self.assertIn("후보 처분: deferred",full)


class FollowupLabelTests(unittest.TestCase):
    def test_link_label_uses_recorded_selection_and_reports_later_target_change(self):
        from hv2ref.continuation import current_snapshot
        from hv2ref.work import record_ref
        source,intents=label_graph("원래 작업")
        target,goals=label_graph("연결 당시 작업",newer=True)
        source["identity"]={"authority_home_id":"home-a","work_id":"work-a"}
        target["identity"]={"authority_home_id":"home-a","work_id":"work-b"}
        selected=current_snapshot(target)
        source["continuation"].update(effective_choice={"kind":"work","target":selected},
                                     effective_ticket={"source":current_snapshot(source)},usage={"normal_remaining":255})
        before=copy.deepcopy(target)
        new_selection={**target["selections"]["selection-a"],"record_id":"selection-new"}
        target["selections"]["selection-new"]=new_selection
        target["current"]={"selection_ref":record_ref(new_selection)}
        shown="\n".join(view._work_overview("work-a",source,goals,{"work-a":source,"work-b":target}))
        self.assertIn("이전 목표: 연결 당시 작업 ("+view.code("work-b")+")",shown)
        self.assertNotIn("UNRELATED NEW GOAL",shown)
        self.assertIn("연결된 작업의 현재 기록을 다시 확인",shown)
        self.assertEqual(before["selections"]["selection-a"],target["selections"]["selection-a"])


class EntrySeparationTests(unittest.TestCase):
    def test_short_display_keeps_exact_commands_and_source_windows_flags(self):
        import shlex
        from hv2ref.cli import workspace_parser
        target=Path("/synthetic/project with 'quotes' $(literal)")
        for command,args in [('help',()),('view',('--details',)),('view',('work','work-a')),('?',())]:
            with patch.object(view.sys,'platform','darwin'):
                short=view._display_command(target,True,command,*args)
                exact=view._cli_command(target,True,command,*args)
                self.assertEqual(['./colvia',command,*args],shlex.split(short))
                self.assertEqual([str(target/'colvia'),command,*args],shlex.split(exact))
                self.assertEqual(command,workspace_parser(target).parse_args(shlex.split(short)[1:]).command)
                source=view._display_command(target,False,command,*args)
                self.assertIn('--source-checkout',source);self.assertIn('--target',source)
            with patch.object(view.sys,'platform','win32'):
                self.assertEqual(view._cli_command(target,True,command,*args),view._display_command(target,True,command,*args))
                self.assertIn("'-I' '-B'",view._display_command(target,True,command,*args))
        with patch.object(view.sys,'platform','darwin'):
            shown=view.render_help(target,installed=True)
        self.assertEqual(1,shown.count('프로젝트 폴더에서 실행'))
        self.assertNotIn(str(target),shown)

    def test_damaged_or_detached_product_does_not_promise_missing_guide(self):
        fixture=OverviewHelpTests();status,works,intents,product=fixture.fixture()
        for classification in ('degraded','detached'):
            status['classification']=classification
            shown,code=fixture.render(status,works,intents,None,installed=True)
            self.assertNotIn('기술 상세·안내 문서:',shown)
            self.assertNotIn('natural_language_adapter:',shown)
            self.assertNotIn('manual:',shown)
            self.assertEqual(view.EXITS.get(classification,0),code)

    @unittest.skipIf(sys.platform == 'win32', 'POSIX relative launcher execution')
    def test_installed_relative_commands_and_other_cwd_keep_target_context(self):
        import subprocess,shlex
        f=fixtures.ActualWorkspaceInitTests();f.setUp();self.addCleanup(f.doCleanups)
        f.apply_init(f.preview());f.complete_work()
        before=fixtures.exact_snapshot(f.target)
        for command,args in [('help',()),('?',()),('view',()),('view',('--details',)),('view',('work','work-a'))]:
            argv=shlex.split(view._display_command(f.target,True,command,*args))
            result=subprocess.run(argv,cwd=f.target,capture_output=True,timeout=45)
            self.assertEqual(0,result.returncode,(result.stdout+result.stderr).decode())
            if command=='view' and not args:
                default=result.stdout.decode();self.assertIn('프로젝트 폴더에서 실행',default)
                self.assertIn('fixture ('+view.code('work-a')+')',default)
        other=f.base/'other';other.mkdir()
        result=subprocess.run([str(f.target/'colvia'),'view'],cwd=other,capture_output=True,timeout=45)
        self.assertEqual(0,result.returncode,result.stderr.decode())
        shown=result.stdout.decode();self.assertIn(view.code(str(f.target)),shown)
        self.assertIn('프로젝트 폴더에서 실행',shown)
        self.assertIn(view.code('./colvia view --details'),shown)
        self.assertNotIn('natural_language_adapter:',shown)
        self.assertEqual(before,fixtures.exact_snapshot(f.target))
