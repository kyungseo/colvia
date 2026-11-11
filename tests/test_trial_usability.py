"""Scoped display and argument requests; no relaxed Core authority checks."""
import copy
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from hv2ref import view, candidates
from hv2ref.errors import ContractError
from hv2ref.jsonio import canonical_json_bytes, decode_json_bytes
from hv2ref.cli import workspace_parser
from tests import test_candidates as fixtures


class ScopedDisplayTests(unittest.TestCase):
    def observe(self, current, *, scope=('report.md',), policy='a', changes=()):
        tree = dict(policy_version=1, ignore_fingerprint='a', sha256='stored', entries=[dict(path='report.md', sha256='old')])
        manifest = dict(result=tree, changes=list(changes))
        actual = dict(policy_version=1, ignore_fingerprint=policy, sha256='current', entries=current)
        with patch.object(view, 'snapshot', return_value=actual):
            return view._live(Path('/synthetic'), manifest, dict(launcher_sha256='x', inventory=dict(inventory_id='continuation-1')), scope)

    def test_other_change_does_not_relabel_accepted_file(self):
        obs = self.observe([dict(path='report.md',sha256='old'),dict(path='later.py',sha256='new')])
        self.assertTrue(obs.startswith('stale'))  # Whole-tree advisory is unchanged.
        self.assertEqual((), obs.changed)
        self.assertEqual(('later.py',), obs.other)
        lines = '\n'.join(view._file_summary(obs))
        self.assertIn('제출할 때와 같음', lines)
        self.assertIn('적용 허가가 아닙니다', lines)
        graph = dict(state='completed',continuation=dict(pending=False))
        self.assertEqual('수락한 결과와 후속 계획 확인', view._resume_next('w',graph,{},obs))
        graph['state']='review'
        self.assertIn('새 수락·적용 전에', view._resume_next('w',graph,{},obs))

    def test_edit_delete_and_rename_remain_visible(self):
        for current in ([dict(path='report.md',sha256='new')], [], [dict(path='renamed.md',sha256='old')]):
            with self.subTest(current=current):
                self.assertEqual(('report.md',), self.observe(current).changed)

    def test_manifest_changes_cannot_be_hidden_by_smaller_scope(self):
        obs=self.observe([],scope=(),changes=[dict(path='report.md')])
        self.assertEqual(('report.md',),obs.changed)

    def test_policy_change_and_failed_snapshot_do_not_claim_match(self):
        obs=self.observe([dict(path='report.md',sha256='old')],policy='different')
        self.assertIn('확인이 필요', '\n'.join(view._file_summary(obs)))
        with patch.object(view,'snapshot',side_effect=OSError('unsafe')):
            obs=view._live(Path('/synthetic'),{},dict(launcher_sha256='x',inventory=dict(inventory_id='x')),['report.md'])
        self.assertTrue(obs.startswith('unavailable'))


    def test_unknown_snapshot_metadata_does_not_claim_scope_match(self):
        tree=dict(policy_version=1, ignore_fingerprint='a', sha256='stored', entries=[])
        with patch.object(view,'snapshot',return_value=dict(tree, truncated=True)):
            obs=view._live(Path('/synthetic'),dict(result=tree,changes=[]),
                dict(launcher_sha256='x',inventory=dict(inventory_id='continuation-1')),[])
        self.assertFalse(obs.policy_matches)
        self.assertNotIn('제출할 때와 같음','\n'.join(view._file_summary(obs)))


class CandidateArgumentTests(unittest.TestCase):
    def setUp(self):
        self.fixture=fixtures.CandidateContractTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.target=self.fixture.target
        self.parser=workspace_parser(self.target)

    def args(self, action='add', *extra):
        base=['candidate',action,'--id','idea-a','--request-id','request-a','--writer','agent',
              '--owner-statement','Save this proposal','--reason','Human requested planning']
        if action=='add': base += ['--title','Report','--purpose','Compare options','--effect','Clear next step']
        return self.parser.parse_args(base+list(extra))

    def test_builder_round_trip_and_same_store(self):
        request=candidates.argument_request(self.target,self.args())
        encoded=canonical_json_bytes(request)
        self.assertEqual(request,decode_json_bytes(encoded,require_canonical=True))
        before=fixtures.truth_bytes(self.target)
        self.fixture.candidates.mutate(request)
        self.assertEqual(before,fixtures.truth_bytes(self.target))
        self.assertEqual('Report',candidates.read_candidates(self.target)['store']['candidates']['idea-a']['title'])

    def test_optimistic_lock_still_rejects_concurrent_write(self):
        request=candidates.argument_request(self.target,self.args())
        self.fixture.act(cid='another')
        with self.assertRaisesRegex(ContractError,'STALE'):
            self.fixture.candidates.mutate(request)

    def test_missing_statement_and_wrong_action_options_rejected(self):
        args=self.args();args.owner_statement=None
        with self.assertRaises(ContractError): candidates.argument_request(self.target,args)
        args=self.args('select','--title','Unrelated title')
        with self.assertRaises(ContractError): candidates.argument_request(self.target,args)

    def test_raw_noncanonical_input_is_still_rejected(self):
        request=candidates.argument_request(self.target,self.args())
        import json
        with self.assertRaises(ContractError):
            decode_json_bytes(json.dumps(request).encode(),require_canonical=True)


class InstalledUsabilityTests(unittest.TestCase):
    def setUp(self):
        self.f=fixtures.InstalledCandidateTests()
        self.f.setUp()
        self.addCleanup(self.f.doCleanups)

    def test_argument_cli_and_brief_view_preserve_raw_api_and_authority(self):
        import json
        f=self.f
        before=fixtures.truth_bytes(f.target)
        args=['candidate','add','--id','new-idea','--request-id','req-new','--writer','agent',
              '--owner-statement','Save this idea','--reason','Planning request',
              '--title','Compare options','--purpose','Discuss next week','--effect','Less repetition','--brief']
        result=json.loads(f.installed(args).stdout)
        self.assertEqual('saved',result['classification'])
        self.assertNotIn('store',result)
        brief=f.installed(['view','candidates','--brief']).stdout.decode()
        self.assertIn('Compare options',brief)
        self.assertNotIn('후보 기록 digest',brief)
        self.assertIn('후보 기록 digest',f.installed(['view','candidates']).stdout.decode())
        self.assertIn('작업 실행이나 결과 수락을 뜻하지 않습니다',result['notice'])
        self.assertEqual(before,fixtures.truth_bytes(f.target))

    def test_completed_work_scope_and_other_drift_are_separate(self):
        f=self.f;f.complete_work()
        (f.target/'later.txt').write_text('another task')
        before=fixtures.truth_bytes(f.target)
        brief=f.installed(['view','work','work-a','--brief']).stdout.decode()
        self.assertIn('결과 수락 완료',brief)
        self.assertIn('제출할 때와 같음',brief)
        self.assertIn('later.txt',brief)
        self.assertNotIn('## Selected history',brief)
        full=f.installed(['view','work','work-a']).stdout.decode()
        self.assertIn('stale: current files differ',full)
        self.assertIn('## Selected history',full)
        self.assertEqual(before,fixtures.truth_bytes(f.target))

    def test_linked_completed_candidate_and_bad_revision(self):
        f=self.f;f.act();f.complete_work()
        from hv2ref.work import read_work
        graph=read_work(f.target,'work-a')
        ref=candidates._selected_revision(graph)
        args=['candidate','link','--id','idea-a','--request-id','link-a','--writer','agent',
              '--owner-statement','Link this work','--reason','Same agreed task','--link-work','work-a','--revision',ref['sha256'],'--brief']
        f.installed(args)
        before=fixtures.truth_bytes(f.target)
        text=f.installed(['view','candidates','--brief']).stdout.decode()
        self.assertIn('연결된 작업 · 결과 수락 완료',text)
        self.assertNotIn('선택 소진',text)
        args[-2]='0'*64
        f.installed(args,expected=65)
        self.assertEqual(before,fixtures.truth_bytes(f.target))
