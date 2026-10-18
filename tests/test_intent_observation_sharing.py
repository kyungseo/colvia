"""Exact intent bindings and independent final reads on installed writer data."""
from __future__ import annotations

import copy
from contextlib import contextmanager
import json
from pathlib import Path
import subprocess
import unittest
from unittest.mock import call, patch

from hv2ref import intent, product, view, work, workspace
from hv2ref.errors import ContractError
from hv2ref.work import record_ref
import test_productization_safety as fixtures
import test_umbrella_lifecycle as umbrella_fixtures


class IntentObservationSharingTests(unittest.TestCase):
    POINTS = ('first-intent', 'between-works', 'before-final')

    def setUp(self):
        self.f = fixtures.ActualWorkspaceInitTests()
        self.f.setUp(); self.addCleanup(self.f.doCleanups)
        self.target = self.f.target
        (self.target / 'a').write_bytes(b'after\n')
        self.f.apply_init(self.f.preview())
        self.ref = self.f.accept_intent()
        self.f.complete_work(intent_ref=self.ref)
        self.f.complete_work('work-b', intent_ref=self.ref)

    def accept(self, draft):
        self.f.installed(['intent', 'draft'], draft)
        request = {'intent_id': draft['intent_id'], 'revision_ref': record_ref(draft, 'revision_id'),
                   'actor': 'owner', 'reason': 'fixture', 'request_id': 'accept-' + draft['intent_id'] + '-' + draft['revision_id'],
                   'observed_at': self.f.TIME}
        prepared = json.loads(self.f.installed(['intent', 'prepare'], request).stdout)
        graph = json.loads(self.f.installed(['intent', 'apply', '--confirm', prepared['confirm_token']], prepared['ticket']).stdout)
        selected = graph['selections'][graph['current']['selection_ref']['id']]
        return {'authority_home_id': 'home-a', 'kind': 'intent', 'id': draft['intent_id'],
                'revision_ref': selected['revision_ref'], 'acceptance_ref': selected['acceptance_ref'],
                'selection_ref': graph['current']['selection_ref']}

    def next_draft(self):
        first = self.f.draft()
        return {**first, 'revision_id': 'draft-b', 'sequence': 2,
                'prior_revision_ref': record_ref(first, 'revision_id')}

    def parity(self, target=None):
        target = target or self.target
        before = fixtures.exact_snapshot(target)
        actual = product._workspace_status_observation(target)
        expected = product._workspace_status_observation(target, _share_intents=False)
        self.assertEqual(expected, actual)
        self.assertEqual(before, fixtures.exact_snapshot(target))
        return actual

    @contextmanager
    def injection(self, point, mutation):
        graph_reader = intent.read_workspace_intent_graph
        work_reader = work.read_work
        collection_reader = intent.workspace_intents
        fired = []
        snapshots = []
        def change():
            if not fired:
                fired.append(point)
                mutation()
                snapshots.append(fixtures.exact_snapshot(self.target))
        def graph(target, name, **kwargs):
            result = graph_reader(target, name, **kwargs)
            if name == 'intent-a' and point == 'first-intent': change()
            return result
        def read_work(target, name, **kwargs):
            result = work_reader(target, name, **kwargs)
            if point == 'between-works': change()
            return result
        def collection(target, **kwargs):
            if not kwargs and point == 'before-final': change()
            return collection_reader(target, **kwargs)
        with patch.object(intent, 'read_workspace_intent_graph', graph), \
             patch.object(work, 'read_work', read_work), \
             patch.object(intent, 'workspace_intents', collection):
            yield fired
        self.assertEqual([point], fired)
        self.assertEqual(snapshots[0], fixtures.exact_snapshot(self.target))

    def test_reuses_graph_but_resolves_every_revision_and_rechecks_at_end(self):
        with patch.object(intent, 'read_workspace_intent_graph', wraps=intent.read_workspace_intent_graph) as reads, \
             patch.object(intent, '_resolve_workspace_intent', wraps=intent._resolve_workspace_intent) as bindings:
            status, graphs = product._workspace_status_observation(self.target)
        self.assertEqual('pass', status['classification'])
        self.assertEqual({'work-a', 'work-b'}, set(graphs[0]))
        self.assertEqual(2, reads.call_count)  # First read plus independent final read.
        self.assertEqual(4, bindings.call_count)  # Two revisions in each Work.
        with patch.object(intent, 'read_workspace_intent_graph', wraps=intent.read_workspace_intent_graph) as reads:
            legacy = product._workspace_status_observation(self.target, _share_intents=False)
        self.assertEqual((status, graphs), legacy)
        self.assertEqual(3, reads.call_count)  # One graph per Work, then an independent final read.
        self.assertEqual([call(self.target, 'intent-a')] * 3, reads.call_args_list)

    def test_different_intents_are_never_conflated(self):
        other = self.accept({**self.f.draft(), 'intent_id': 'intent-b'})
        self.f.complete_work('work-c', intent_ref=other)
        with patch.object(intent, 'read_workspace_intent_graph', wraps=intent.read_workspace_intent_graph) as reads:
            status, graphs = product._workspace_status_observation(self.target)
        self.assertEqual('pass', status['classification'])
        self.assertEqual({'intent-a', 'intent-b'}, set(graphs[1]))
        self.assertEqual(4, reads.call_count)
        self.parity()

    def test_historical_bindings_remain_exact_after_new_acceptance(self):
        newer = self.accept(self.next_draft())
        self.f.complete_work('work-c', intent_ref=newer)
        status, graphs = self.parity()
        self.assertEqual('pass', status['classification'])
        graph = graphs[1]['intent-a']
        old, _ = intent._resolve_workspace_intent(graph, 'intent-a', self.ref)
        current, _ = intent._resolve_workspace_intent(graph, 'intent-a', newer)
        self.assertFalse(old['is_current']); self.assertTrue(current['is_current'])
        for key in ('revision_ref', 'acceptance_ref', 'selection_ref'):
            bad = copy.deepcopy(self.ref); bad[key]['sha256'] = '0' * 64
            with self.subTest(key=key), self.assertRaises(ContractError):
                intent._resolve_workspace_intent(graph, 'intent-a', bad)
        with self.assertRaisesRegex(ContractError, 'stale intent selection'):
            intent.read_workspace_intent(self.target, 'intent-a', self.ref)

    def test_default_readers_and_current_live_checks_stay_fresh(self):
        product.workspace_status(self.target)
        with patch.object(intent, 'read_workspace_intent_graph', wraps=intent.read_workspace_intent_graph) as reads, \
             patch.object(intent, '_resolve_workspace_intent', wraps=intent._resolve_workspace_intent) as bindings:
            work.WorkStore(self.target)._all()
        self.assertEqual(2, reads.call_count)  # Fresh graph for each Work; no cross-Work cache.
        self.assertEqual([call(self.target, 'intent-a')] * 2, reads.call_args_list)
        self.assertEqual(4, bindings.call_count)  # Every revision still resolves its exact binding.
        with patch.object(work, '_live_external_refs', wraps=work._live_external_refs) as live:
            intent.read_workspace_intent(self.target, 'intent-a', self.ref)
        self.assertEqual(1, live.call_count)
        path = self.target / '.hrn/intents/intent-a/current.json'
        path.write_bytes(b'{}\n')
        with self.assertRaises(ContractError):
            intent.read_workspace_intent(self.target, 'intent-a', self.ref)
        request = {'work_id': 'work-a', 'action': 'revoke', 'actor': 'owner', 'reason': 'fixture',
                   'request_id': 'fresh-writer', 'observed_at': self.f.TIME, 'revision_ref': None, 'supersedes': None}
        before = fixtures.exact_snapshot(self.target)
        result = self.f.installed(['work', 'prepare'], request, expected=None)
        self.assertNotEqual(0, result.returncode)
        self.assertEqual(before, fixtures.exact_snapshot(self.target))

    def test_observations_targets_and_returned_graphs_are_independent(self):
        first = product._workspace_status_observation(self.target)
        saved = copy.deepcopy(first)
        first[1][1]['intent-a']['data']['identity.json']['intent_id'] = 'consumer-tamper'
        self.assertEqual(saved, product._workspace_status_observation(self.target))
        other = fixtures.ActualWorkspaceInitTests(); other.setUp(); self.addCleanup(other.doCleanups)
        other.apply_init(other.preview()); other.accept_intent()
        (other.target / '.hrn/intents/intent-a/identity.json').write_bytes(b'{}\n')
        self.assertEqual('degraded', product.workspace_status(other.target)['classification'])
        self.assertEqual(saved, product._workspace_status_observation(self.target))

    def test_schema2_collection_uses_same_graphs_without_skipping_history(self):
        parent = umbrella_fixtures.InstalledUmbrellaLifecycleTests()
        parent.setUp(); self.addCleanup(parent.doCleanups)
        parent.apply_init(parent.preview()); parent.accept(parent.draft())
        parent.composition = {'parent': parent.q('work', 'parent'), 'required_children': [
            {'work': parent.q('work', 'child-a'), 'intent': parent.q('intent', 'intent-a')}]}
        ref = parent.accept({**parent.draft(intent_id='parent-intent'), 'schema_version': 2,
                             'composition': parent.composition})
        parent.publish('parent', ref, 'start', parent=True)
        with patch.object(intent, 'read_workspace_intent_graph', wraps=intent.read_workspace_intent_graph) as reads:
            status, graphs = product._workspace_status_observation(parent.target)
        self.assertEqual('pass', status['classification']); self.assertEqual(4, reads.call_count)
        self.assertEqual((status, graphs), product._workspace_status_observation(parent.target, _share_intents=False))
        (parent.target / '.hrn/intents/intent-a/identity.json').write_bytes(b'{}\n')
        self.assertEqual('degraded', product.workspace_status(parent.target)['classification'])
        parent.success = True

    def test_unreferenced_intent_damage_and_multiple_error_order_are_preserved(self):
        self.accept({**self.f.draft(), 'intent_id': 'unreferenced'})
        (self.target / '.hrn/intents/unreferenced/identity.json').write_bytes(b'{}\n')
        self.assertEqual('degraded', self.parity()[0]['classification'])
        (self.target / '.hrn/work/work-b/identity.json').write_bytes(b'{}\n')
        self.assertEqual('degraded', self.parity()[0]['classification'])

    def test_pending_and_unsupported_use_one_unshared_fallback(self):
        original = work.WorkStore._all
        calls = []
        def all_works(store, **kwargs):
            calls.append(bool(kwargs)); return original(store, **kwargs)
        with patch.object(workspace, 'runtime_supported', return_value=False), patch.object(work.WorkStore, '_all', all_works):
            status, graphs = product._workspace_status_observation(self.target)
        self.assertEqual('unsupported', status['classification']); self.assertIsNone(graphs)
        self.assertEqual([True, False], calls)
        self.f.installed(['intent', 'draft'], self.next_draft())
        prepared = json.loads(self.f.installed(['intent', 'prepare'], {
            'intent_id': 'intent-a', 'revision_ref': record_ref(self.next_draft(), 'revision_id'),
            'actor': 'owner', 'reason': 'fixture', 'request_id': 'pending', 'observed_at': self.f.TIME}).stdout)
        selector = self.target / '.hrn/intents/intent-a/current.json'
        previous = selector.read_bytes()
        self.f.installed(['intent', 'apply', '--confirm', prepared['confirm_token']], prepared['ticket'])
        # Restore the actual earlier selector to observe a durable pending selection.
        selector.write_bytes(previous)
        status, graphs = self.parity()
        self.assertEqual('partial', status['classification']); self.assertIsNone(graphs)

    def test_persistent_record_damage_at_every_reuse_boundary(self):
        paths = [self.target / '.hrn/intents/intent-a' / name for name in
                 ('identity.json', 'drafts/draft-a.json', 'current.json')]
        paths += [next((self.target / '.hrn/intents/intent-a/acceptances').iterdir())]
        for path in paths:
            old = path.read_bytes()
            for point in self.POINTS:
                with self.subTest(path=str(path.relative_to(self.target)), point=point):
                    with self.injection(point, lambda: path.write_bytes(b'{}\n')):
                        status, graphs = product._workspace_status_observation(self.target)
                    self.assertEqual('degraded', status['classification']); self.assertIsNone(graphs)
                    self.assertEqual(status, product.workspace_status(self.target))
                    path.write_bytes(old)

    def test_format_and_intent_path_replacement_do_not_pass(self):
        path = self.target / '.hrn/format.json'; old = path.read_bytes()
        for point in self.POINTS:
            with self.subTest(point=point), self.injection(point, lambda: path.write_bytes(b'{}\n')):
                status, graphs = product._workspace_status_observation(self.target)
            self.assertEqual('degraded', status['classification']); self.assertIsNone(graphs)
            path.write_bytes(old)
        home = self.target / '.hrn/intents/intent-a'; saved = self.f.base / 'saved-intent'
        def replace():
            home.rename(saved); home.symlink_to(saved, target_is_directory=True)
        with self.injection('first-intent', replace):
            status, graphs = product._workspace_status_observation(self.target)
        self.assertEqual('degraded', status['classification']); self.assertIsNone(graphs)

    def test_effective_ignore_changes_are_rechecked(self):
        subprocess.run(['git', 'init', '-q', str(self.target)], check=True, capture_output=True)
        local = self.target / '.git/info/exclude'
        external = self.f.base / 'external-excludes'; external.write_bytes(b'')
        subprocess.run(['git', '-C', str(self.target), 'config', 'core.excludesFile', str(external)], check=True)
        for path in (local, external):
            old = path.read_bytes()
            for point in self.POINTS:
                with self.subTest(path=path.name, point=point):
                    with self.injection(point, lambda: path.write_bytes(old + b'\n.hrn/intents/intent-a/\n')):
                        status, graphs = product._workspace_status_observation(self.target)
                    self.assertEqual('degraded', status['classification']); self.assertIsNone(graphs)
                    self.assertIn('ignore', status['message'])
                    path.write_bytes(old)
        self.assertEqual('pass', self.parity()[0]['classification'])

    def test_valid_draft_only_transition_requires_value_mismatch_fallback(self):
        home = self.target / '.hrn/intents/intent-a'
        removed = {p: (p.read_bytes(), p.stat().st_mode & 0o777) for p in [home / 'current.json',
                   *sorted((home / 'selections').iterdir()),
                   *sorted((home / 'acceptances').iterdir())]}
        self.assertEqual(3, len(removed))
        initial = fixtures.exact_snapshot(self.target)
        for point in self.POINTS:
            calls = []
            original = work.WorkStore._all
            def all_works(store, **kwargs):
                calls.append(bool(kwargs)); return original(store, **kwargs)
            def draft_only():
                for path in removed: path.unlink()
                # Valid graph, not a final-read error or missing intent ID.
                final = intent.read_workspace_intent_graph(self.target, 'intent-a')
                self.assertIsNone(final['current'])
                self.assertEqual({}, final['acceptances'])
                self.assertEqual({}, final['selections'])
                self.assertEqual([], final['pending_acceptances'])
                self.assertEqual([], final['pending_selections'])
                self.assertEqual({'draft-a'}, set(final['drafts']))
            with self.subTest(point=point):
                try:
                    with patch.object(work.WorkStore, '_all', all_works), self.injection(point, draft_only):
                        status, graphs = product._workspace_status_observation(self.target)
                    self.assertEqual('degraded', status['classification'])
                    self.assertIsNone(graphs)
                    self.assertEqual([True, False], calls)
                    self.assertEqual(status, product._workspace_status_observation(
                        self.target, _share_intents=False)[0])
                finally:
                    for path, (data, mode) in removed.items():
                        path.write_bytes(data); path.chmod(mode)
                    self.assertEqual(initial, fixtures.exact_snapshot(self.target))

    def test_valid_transition_discards_old_graph_and_uses_fresh_state(self):
        calls = []
        original = work.WorkStore._all
        def all_works(store, **kwargs):
            calls.append(bool(kwargs)); return original(store, **kwargs)
        with patch.object(work.WorkStore, '_all', all_works), \
             self.injection('first-intent', lambda: self.accept(self.next_draft())):
            observed = product._workspace_status_observation(self.target)
        self.assertEqual([True, False], calls)
        self.assertEqual('pass', observed[0]['classification'])
        self.assertEqual(observed, product._workspace_status_observation(self.target, _share_intents=False))
        self.assertEqual(2, len(observed[1][1]['intent-a']['drafts']))

    def test_unselected_work_damage_is_still_visible_in_individual_view(self):
        path = self.target / '.hrn/work/work-b/revisions/revision-2.json'
        with self.injection('before-final', lambda: path.write_bytes(b'{}\n')):
            output, code = view.render_view(self.target, kind='work', object_id='work-a')
        self.assertEqual(10, code, output)
        self.assertIn('classification: degraded', output)
        self.assertNotIn('Observation unstable', output)

    def test_missing_intent_at_final_read_cannot_reuse_old_success(self):
        home = self.target / '.hrn/intents/intent-a'; saved = self.f.base / 'missing-intent'
        with self.injection('before-final', lambda: home.rename(saved)):
            status, graphs = product._workspace_status_observation(self.target)
        self.assertEqual('degraded', status['classification']); self.assertIsNone(graphs)

    def test_same_target_view_keeps_exact_output_and_read_only(self):
        original = product._workspace_status_observation
        for kind, object_id in [(None, None), ('work', 'work-a'), ('intent', 'intent-a')]:
            before = fixtures.exact_snapshot(self.target)
            actual = view.render_view(self.target, kind=kind, object_id=object_id)
            with patch.object(view, '_workspace_status_observation', lambda t: original(t, _share_intents=False)):
                expected = view.render_view(self.target, kind=kind, object_id=object_id)
            self.assertEqual(expected, actual); self.assertEqual(0, actual[1])
            self.assertEqual(before, fixtures.exact_snapshot(self.target))
