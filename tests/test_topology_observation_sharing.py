"""Persistent topology/visibility oracles for observation-local raw probe sharing."""
from __future__ import annotations
from tests.platform_fixtures import (
    fixture_directory_link,
    fixture_is_link,
    fixture_unlink,
)
import sys

import copy
from contextlib import contextmanager, ExitStack
import inspect
from pathlib import Path
import subprocess
import unittest
from unittest.mock import patch

from hv2ref import intent, product, view, work, workspace
from hv2ref.errors import ContractError
import test_intent_observation_sharing as intent_fixtures
import test_productization_safety as fixtures


class TopologyObservationSharingTests(unittest.TestCase):
    def setUp(self):
        self.h = intent_fixtures.IntentObservationSharingTests()
        self.h.setUp(); self.addCleanup(self.h.doCleanups)
        self.f = self.h.f; self.target = self.h.target
        subprocess.run(['git', 'init', '-q', str(self.target)], check=True, capture_output=True, timeout=45)
        fixtures.git_commit_all(self.target, 'topology observation fixture')

    @contextmanager
    def after_first_work(self, mutation):
        original = work.read_work; fired = []; mutated = []
        def read(target, name, **kwargs):
            result = original(target, name, **kwargs)
            if not fired:
                fired.append(name); mutation(name); mutated.append(fixtures.exact_snapshot(self.target))
            return result
        with patch.object(work, 'read_work', read):
            yield fired
        self.assertEqual(1, len(fired))
        self.assertEqual(mutated[0], fixtures.exact_snapshot(self.target))

    def test_primary_stationary_parity_and_probe_scope(self):
        before = fixtures.exact_snapshot(self.target)
        current = []; scoped_probes = []; ignores = []
        raw = workspace._topology_probe; probe = workspace._TopologyObservation._probe; git = work._git
        def track_raw(target, env):
            if current: scoped_probes.append(('final' if current[-1]._finishing else 'initial', id(current[-1])))
            return raw(target, env)
        def track_probe(ctx, *args, **kwargs):
            current.append(ctx)
            try: return probe(ctx, *args, **kwargs)
            finally: current.pop()
        def track_git(target, *args, **kwargs):
            if args and args[0] == 'check-ignore': ignores.append((args, kwargs.get('input_data')))
            return git(target, *args, **kwargs)
        with patch.object(workspace, '_topology_probe', track_raw), \
             patch.object(workspace._TopologyObservation, '_probe', track_probe), patch.object(work, '_git', track_git):
            actual = product._workspace_status_observation(self.target)
        actual_ignores = list(ignores); ignores.clear()
        self.assertEqual(['initial', 'final'], [x[0] for x in scoped_probes])
        self.assertEqual(1, len({x[1] for x in scoped_probes}))
        # Keep the existing intent sharing while disabling only raw reuse in this
        # stationary in-process comparator; it is not installed-runtime evidence.
        def always_fresh(ctx, target, env, *, mutation): return raw(target, env)
        with patch.object(workspace._TopologyObservation, '_probe', always_fresh), patch.object(work, '_git', track_git):
            expected = product._workspace_status_observation(self.target)
        self.assertEqual(expected, actual)
        self.assertEqual(actual_ignores, ignores)
        self.assertTrue(ignores)
        self.assertEqual(product._workspace_status_observation(self.target, _share_intents=False), actual)
        self.assertEqual('pass', actual[0]['classification'])
        self.assertEqual(before, fixtures.exact_snapshot(self.target))

    def test_persistent_separate_git_transition_discards_primary(self):
        before = fixtures.exact_snapshot(self.target)
        metadata = self.f.base / 'separate-metadata'
        dotgit = self.target / '.git'
        def move(_):
            dotgit.rename(metadata)
            dotgit.write_text('gitdir: ' + str(metadata) + '\n')
        try:
            with self.after_first_work(move):
                observed = product._workspace_status_observation(self.target)
            # This is a settled post-mutation oracle, not the old runtime with
            # the same mid-observation race (which can retain entry topology).
            settled = fixtures.exact_snapshot(self.target)
            expected = product._workspace_status_observation(self.target, _share_intents=False)
            self.assertEqual('separate-git-dir', observed[0]['topology'], 'final topology must discard stale primary')
            self.assertFalse(observed[0]['authoritative_control'])
            self.assertEqual(expected, observed)
            self.assertEqual(settled, fixtures.exact_snapshot(self.target))
        finally:
            if metadata.exists():
                dotgit.unlink(); metadata.rename(dotgit)
            self.assertEqual(before, fixtures.exact_snapshot(self.target))

    def test_effective_ignore_changes_remain_visible(self):
        for location in ['.git/info/exclude', '.hrn/.gitignore']:
            path = self.target / location; saved = (path.read_bytes(), path.stat().st_mode & 0o777)
            before = fixtures.exact_snapshot(self.target)
            def hide(first):
                other = next(iter({'work-a', 'work-b'} - {first}))
                path.write_bytes(saved[0] + ('\n' + ('.hrn/work/' if location.startswith('.git/') else 'work/') + other + '/\n').encode())
            with self.subTest(location=location):
                try:
                    with self.after_first_work(hide):
                        observed = product._workspace_status_observation(self.target)
                    self.assertEqual('degraded', observed[0]['classification'], 'fresh ignore check must expose hidden Work truth')
                    self.assertIsNone(observed[1])
                    self.assertEqual(product._workspace_status_observation(self.target, _share_intents=False), observed)
                finally:
                    path.write_bytes(saved[0]); path.chmod(saved[1])
                    self.assertEqual(before, fixtures.exact_snapshot(self.target))

    def test_final_intent_read_stays_independent(self):
        home = self.target / '.hrn/intents/intent-a'
        removed = [home / 'current.json', *sorted((home / 'selections').iterdir()), *sorted((home / 'acceptances').iterdir())]
        identity = home / 'identity.json'; saved = {p: (p.read_bytes(), p.stat().st_mode & 0o777) for p in [*removed, identity]}
        before = fixtures.exact_snapshot(self.target)
        for point in self.h.POINTS:
            for damage in ['draft-only', 'malformed']:
                def mutate():
                    if damage == 'draft-only':
                        for p in removed: p.unlink()
                        graph = intent.read_workspace_intent_graph(self.target, 'intent-a')
                        self.assertIsNone(graph['current']); self.assertFalse(graph['pending_acceptances']); self.assertFalse(graph['pending_selections'])
                    else: identity.write_bytes(b'{}\n')
                calls = []; all_works = work.WorkStore._all
                def record_all(store, **kwargs):
                    calls.append(any(kwargs.get(key) is not None for key in ('_intent_graph_reader', '_topology_observation'))); return all_works(store, **kwargs)
                with self.subTest(point=point, damage=damage):
                    try:
                        with patch.object(work.WorkStore, '_all', record_all), self.h.injection(point, mutate):
                            observed = product._workspace_status_observation(self.target)
                        self.assertEqual('degraded', observed[0]['classification'])
                        self.assertIsNone(observed[1]); self.assertEqual([True, False], calls)
                        self.assertEqual(product._workspace_status_observation(self.target, _share_intents=False), observed)
                    finally:
                        for p, (data, mode) in saved.items(): p.write_bytes(data); p.chmod(mode)
                        self.assertEqual(before, fixtures.exact_snapshot(self.target))

    def test_before_after_and_repeated_calls_do_not_share(self):
        before = fixtures.exact_snapshot(self.target); contexts = []
        initialize = workspace._TopologyObservation.__init__
        def init(ctx, target): initialize(ctx, target); contexts.append(ctx)
        with patch.object(workspace._TopologyObservation, '__init__', init):
            first = product._workspace_status_observation(self.target)
            snapshot = copy.deepcopy(first)
            first[1][1]['intent-a']['data']['identity.json']['intent_id'] = 'consumer-change'
            second = product._workspace_status_observation(self.target)
            output, code = view.render_view(self.target)
        self.assertEqual(snapshot, second); self.assertEqual(0, code, output)
        self.assertEqual(4, len(contexts)); self.assertEqual(4, len({id(c) for c in contexts}))
        self.assertTrue(all(c._closed and c._raw is None for c in contexts))
        self.assertEqual(before, fixtures.exact_snapshot(self.target))

    def test_final_error_discards_context_and_preserves_fallback_paths(self):
        before = fixtures.exact_snapshot(self.target)
        for point in ['first-probe', 'finish', 'final-intents', 'nonpass-fallback-entry']:
            calls = []; contexts = []; fired = []
            original = product._workspace_status_observation; probe = workspace._TopologyObservation._probe
            finish = workspace._TopologyObservation.finish; collection = intent.workspace_intents
            classify = workspace.classify_target; initialize = workspace._TopologyObservation.__init__
            def status(target, **kwargs):
                calls.append(kwargs.get('_share_intents', True)); return original(target, **kwargs)
            def init(ctx, target): initialize(ctx, target); contexts.append(ctx)
            def inject():
                fired.append(point); raise ContractError('HV2-WORKSPACE-TARGET', 'synthetic observation failure')
            def first(ctx, *args, **kwargs):
                if not fired: inject()
                return probe(ctx, *args, **kwargs)
            def last(ctx): inject()
            def final(target, **kwargs):
                if not kwargs and not fired: inject()
                return collection(target, **kwargs)
            entries = []
            def entry(target, **kwargs):
                if inspect.currentframe().f_back.f_code.co_name == '_workspace_status_observation':
                    entries.append(True)
                    if len(entries) == 2: inject()
                return classify(target, **kwargs)
            with self.subTest(point=point), ExitStack() as outer:
                if point == 'nonpass-fallback-entry': outer.enter_context(patch.object(workspace, 'runtime_supported', return_value=False))
                with ExitStack() as stack:
                    stack.enter_context(patch.object(product, '_workspace_status_observation', status))
                    stack.enter_context(patch.object(workspace._TopologyObservation, '__init__', init))
                    if point == 'first-probe': stack.enter_context(patch.object(workspace._TopologyObservation, '_probe', first))
                    elif point == 'finish': stack.enter_context(patch.object(workspace._TopologyObservation, 'finish', last))
                    elif point == 'final-intents': stack.enter_context(patch.object(intent, 'workspace_intents', final))
                    else: stack.enter_context(patch.object(workspace, 'classify_target', entry))
                    observed = product._workspace_status_observation(self.target)
                self.assertEqual([True, False, False] if point == 'nonpass-fallback-entry' else [True, False], calls)
                self.assertEqual([point], fired); self.assertEqual(1, len(contexts))
                self.assertTrue(contexts[0]._closed)
                self.assertEqual(original(self.target, _share_intents=False), observed)
                self.assertEqual(before, fixtures.exact_snapshot(self.target))

    def fresh_parity(self, target=None):
        target = target or self.target
        before = fixtures.exact_snapshot(target)
        observed = product._workspace_status_observation(target)
        self.assertEqual(product._workspace_status_observation(target, _share_intents=False), observed)
        self.assertEqual(before, fixtures.exact_snapshot(target))
        return observed

    def git(self, target, *args):
        config = ['-c', 'core.autocrlf=false', '-c', 'core.eol=lf'] if sys.platform == 'win32' and args[:2] == ('worktree', 'add') else []
        return subprocess.run(['git', *config, '-C', str(target), *args], check=True, capture_output=True,
                              env=workspace.git_environment(), timeout=45).stdout

    def test_raw_probe_same_kind_change_requires_fallback(self):
        before = fixtures.exact_snapshot(self.target)
        for variant in ('stdout-path-spelling', 'success-stderr'):
            with self.subTest(variant=variant):
                finish = workspace._TopologyObservation.finish; raw = workspace._topology_probe
                original = product._workspace_status_observation; calls = []; altered = []
                def status(target, **kw):
                    calls.append(kw.get('_share_intents', True)); return original(target, **kw)
                def changed(target, env):
                    rc, out, err = raw(target, env)
                    if variant == 'stdout-path-spelling':
                        lines = out.splitlines(); lines[0] += b'/.'; out = b'\n'.join(lines) + b'\n'
                    else: err += b'synthetic harmless warning\n'
                    altered.append((rc, out, err)); return rc, out, err
                def final(ctx):
                    with patch.object(workspace, '_topology_probe', changed): return finish(ctx)
                with patch.object(product, '_workspace_status_observation', status), \
                     patch.object(workspace._TopologyObservation, 'finish', final):
                    observed = product._workspace_status_observation(self.target)
                self.assertEqual([True, False], calls); self.assertEqual(1, len(altered))
                with patch.object(workspace, '_topology_probe', return_value=altered[0]):
                    public = workspace.classify_target(self.target)
                self.assertEqual({'kind': 'primary', 'target': str(self.target)}, public)
                self.assertEqual(original(self.target, _share_intents=False), observed)
                self.assertEqual(before, fixtures.exact_snapshot(self.target))

    def test_persistent_linked_non_git_and_git_error(self):
        dotgit = self.target / '.git'; saved = self.f.base / 'non-git-metadata'
        before = fixtures.exact_snapshot(self.target)
        with self.subTest(variant='real-persistent-non-git'):
            try:
                with self.after_first_work(lambda _: dotgit.rename(saved)):
                    observed = product._workspace_status_observation(self.target)
                self.assertEqual('non-git', observed[0]['topology'])
                self.assertEqual(product._workspace_status_observation(self.target, _share_intents=False), observed)
            finally:
                saved.rename(dotgit); self.assertEqual(before, fixtures.exact_snapshot(self.target))
        linked = self.f.base / 'linked-reader'
        self.git(self.target, 'worktree', 'add', '-q', '--detach', str(linked), 'HEAD')
        try:
            linked_raw = workspace._topology_probe(linked, workspace.git_environment())
            lines = linked_raw[1].splitlines(); lines[0] = str(self.target).encode()
            synthetic_linked = (0, b'\n'.join(lines) + b'\n', linked_raw[2])
            variants = {'missing-git': FileNotFoundError('synthetic Git unavailable'),
                        'nonzero': (128, b'', b'synthetic Git failure'),
                        'malformed': (0, b'not topology\n', b''), 'synthetic-linked': synthetic_linked}
            for variant, failure in variants.items():
                with self.subTest(variant=variant):
                    finish = workspace._TopologyObservation.finish; contexts = []; calls = []
                    original = product._workspace_status_observation
                    def status(target, **kw):
                        calls.append(kw.get('_share_intents', True)); return original(target, **kw)
                    def final(ctx):
                        contexts.append(ctx)
                        kw = {'side_effect': failure} if isinstance(failure, Exception) else {'return_value': failure}
                        with patch.object(workspace, '_topology_probe', **kw): return finish(ctx)
                    before = fixtures.exact_snapshot(self.target)
                    with patch.object(workspace._TopologyObservation, 'finish', final), \
                         patch.object(product, '_workspace_status_observation', status):
                        observed = product._workspace_status_observation(self.target)
                    self.assertEqual([True, False], calls); self.assertEqual(1, len(contexts))
                    self.assertTrue(contexts[0]._closed); self.assertIsNone(contexts[0]._raw)
                    self.assertEqual(original(self.target, _share_intents=False), observed)
                    self.assertEqual(before, fixtures.exact_snapshot(self.target))
                    if variant == 'synthetic-linked':
                        with patch.object(workspace, '_topology_probe', return_value=failure):
                            self.assertEqual('linked-worktree', workspace.classify_target(self.target)['kind'])
            with self.subTest(variant='real-initial-linked'), \
                 patch.object(workspace._TopologyObservation, '__init__', side_effect=AssertionError('linked context')):
                observed = self.fresh_parity(linked)
                self.assertEqual('linked-worktree', observed[0]['topology'])
                self.assertFalse(observed[0]['authoritative_control'])
                self.assertIn('work-a', observed[1][0])
        finally:
            # The linked checkout is a reproducible fixture; no test writes into it.
            self.git(self.target, 'worktree', 'remove', str(linked))

    def test_path_and_authority_checks_are_not_shared(self):
        for variant in ('ancestor-authority', 'target-symlink', 'ancestor-symlink', 'metadata-resolve'):
            ctx = workspace._TopologyObservation(self.target)
            workspace.classify_target(self.target, _topology_observation=ctx)
            before = fixtures.exact_snapshot(self.f.base)
            authority = self.f.base / '.hrn'; saved = self.f.base / 'saved-target'
            saved_base = self.f.base.with_name(self.f.base.name + '-saved-ancestor')
            metadata = self.f.base / 'saved-git'
            self.assertFalse(saved_base.exists())
            with self.subTest(variant=variant):
                try:
                    if variant == 'ancestor-authority': authority.mkdir()
                    elif variant == 'target-symlink':
                        self.target.rename(saved); fixture_directory_link(self.target, saved)
                    elif variant == 'ancestor-symlink':
                        self.f.base.rename(saved_base); fixture_directory_link(self.f.base, saved_base)
                    else:
                        (self.target / '.git').rename(metadata)
                        fixture_directory_link(self.target / '.git', self.f.base / 'absent-metadata')
                    mutated = fixtures.exact_snapshot(saved_base if variant == 'ancestor-symlink' else self.f.base)
                    with self.assertRaises(ContractError) as cached:
                        workspace.classify_target(self.target, _topology_observation=ctx)
                    with self.assertRaises(ContractError) as fresh: workspace.classify_target(self.target)
                    expected_code = 'HV2-WORKSPACE-CONTRACT' if variant in ('target-symlink', 'ancestor-symlink') else 'HV2-WORKSPACE-TARGET'
                    self.assertEqual('HV2-WINDOWS-PATH' if sys.platform == 'win32' and variant != 'ancestor-authority' else expected_code, cached.exception.code)
                    self.assertEqual(fresh.exception.code, cached.exception.code)
                    self.assertEqual(mutated, fixtures.exact_snapshot(saved_base if variant == 'ancestor-symlink' else self.f.base))
                finally:
                    ctx.close()
                    if variant == 'ancestor-authority': authority.rmdir()
                    elif variant == 'target-symlink': fixture_unlink(self.target); saved.rename(self.target)
                    elif variant == 'ancestor-symlink': fixture_unlink(self.f.base); saved_base.rename(self.f.base)
                    else: fixture_unlink(self.target / '.git'); metadata.rename(self.target / '.git')
                    self.assertEqual(before, fixtures.exact_snapshot(self.f.base))

    def test_pending_unsupported_nonprimary_use_fresh_path(self):
        import json
        from hv2ref.jsonio import canonical_json_bytes
        def check(expected, *, no_context=False, target=None):
            target = target or self.target; contexts = []; init = workspace._TopologyObservation.__init__
            def initialize(ctx, path): init(ctx, path); contexts.append(ctx)
            before = fixtures.exact_snapshot(target)
            with patch.object(workspace._TopologyObservation, '__init__', initialize):
                observed = product._workspace_status_observation(target)
            self.assertEqual(expected, observed[0]['classification']); self.assertIsNone(observed[1])
            self.assertEqual(0 if no_context else 1, len(contexts))
            self.assertTrue(all(c._closed and c._raw is None for c in contexts))
            self.assertEqual(product._workspace_status_observation(target, _share_intents=False), observed)
            self.assertEqual(before, fixtures.exact_snapshot(target))
        with self.subTest(variant='unsupported'), patch.object(workspace, 'runtime_supported', return_value=False):
            check('unsupported')
        selector = self.target / '.hrn/work/work-a/current.json'; original = selector.read_bytes()
        g = work.read_work(self.target, 'work-a'); current = json.loads(original)
        current['selection_ref'] = g['selections'][current['selection_ref']['id']]['parent_selection_ref']
        with self.subTest(variant='pending-work'):
            try: selector.write_bytes(canonical_json_bytes(current)); check('partial')
            finally: selector.write_bytes(original)
        selector = self.target / '.hrn/intents/intent-a/current.json'; original = selector.read_bytes()
        self.h.accept(self.h.next_draft())
        final = selector.read_bytes()
        with self.subTest(variant='pending-intent'):
            try: selector.write_bytes(original); check('partial')
            finally: selector.write_bytes(final)
        dotgit = self.target / '.git'; saved = self.f.base / 'moved-metadata'
        for variant in ('non-git', 'separate-git-dir'):
            with self.subTest(variant=variant):
                try:
                    dotgit.rename(saved)
                    if variant == 'separate-git-dir': dotgit.write_text('gitdir: ' + str(saved) + '\n')
                    with patch.object(workspace._TopologyObservation, '__init__', side_effect=AssertionError('nonprimary context')):
                        observed = self.fresh_parity()
                    self.assertEqual(variant, observed[0]['topology'])
                finally:
                    if dotgit.exists(): dotgit.unlink()
                    saved.rename(dotgit)
        # Commit the deliberately newer, valid intent before creating the transport fixture.
        fixtures.git_commit_all(self.target, 'pending oracle restored')
        linked = self.f.base / 'pending-linked'
        self.git(self.target, 'worktree', 'add', '-q', '--detach', str(linked), 'HEAD')
        try:
            with self.subTest(variant='linked-worktree'), \
                 patch.object(workspace._TopologyObservation, '__init__', side_effect=AssertionError('linked context')):
                observed = self.fresh_parity(linked)
                self.assertEqual('linked-worktree', observed[0]['topology'])
                self.assertFalse(observed[0]['authoritative_control'])
                self.assertIn('work-a', observed[1][0])
        finally: self.git(self.target, 'worktree', 'remove', str(linked))

    def test_schema2_and_worker_status_keep_full_checks(self):
        import test_umbrella_lifecycle as umbrella_fixtures
        import test_worktree_execution as worker_fixtures
        parent = umbrella_fixtures.InstalledUmbrellaLifecycleTests()
        parent.setUp(); self.addCleanup(parent.doCleanups)
        self.git(parent.target, 'init', '-q')
        parent.apply_init(parent.preview()); child = parent.accept(parent.draft())
        parent.composition = {'parent': parent.q('work', 'parent'), 'required_children': [
            {'work': parent.q('work', 'child-a'), 'intent': parent.q('intent', 'intent-a')}]}
        bound = parent.accept({**parent.draft(intent_id='parent-intent'), 'schema_version': 2,
                               'composition': parent.composition})
        parent.publish('parent', bound, 'start', parent=True)
        parent.publish('child-a', child, 'start')
        parent.accept(parent.draft(intent_id='unreferenced'))
        fixtures.git_commit_all(parent.target, 'schema2 topology oracle')
        def observe(target):
            calls = []; contexts = []; raw_calls = []
            graph = intent.read_workspace_intent_graph; init = workspace._TopologyObservation.__init__
            probe = workspace._TopologyObservation._probe; raw = workspace._topology_probe; active = []
            def initialize(ctx, path): init(ctx, path); contexts.append(ctx)
            def reader(path, name, **kw):
                calls.append((name, kw.get('_topology_observation'))); return graph(path, name, **kw)
            def scoped(ctx, *a, **kw):
                active.append(ctx)
                try: return probe(ctx, *a, **kw)
                finally: active.pop()
            def raw_read(*a, **kw):
                if active: raw_calls.append(active[-1])
                return raw(*a, **kw)
            before = fixtures.exact_snapshot(target)
            with patch.object(intent, 'read_workspace_intent_graph', reader), \
                 patch.object(workspace._TopologyObservation, '__init__', initialize), \
                 patch.object(workspace._TopologyObservation, '_probe', scoped), \
                 patch.object(workspace, '_topology_probe', raw_read):
                result = product._workspace_status_observation(target)
            self.assertEqual(product._workspace_status_observation(target, _share_intents=False), result)
            self.assertEqual(before, fixtures.exact_snapshot(target))
            self.assertTrue(all(c._closed and c._raw is None for c in contexts))
            return result, calls, contexts, raw_calls
        with self.subTest(variant='schema2-unreferenced-intent'):
            result, calls, contexts, raw_calls = observe(parent.target)
            self.assertEqual('pass', result[0]['classification']); self.assertEqual(1, len(contexts))
            shared = [name for name, ctx in calls if ctx is contexts[0]]
            independent = [name for name, ctx in calls if ctx is None]
            self.assertEqual(['intent-a', 'parent-intent', 'unreferenced'], sorted(shared))
            self.assertEqual(sorted(shared), sorted(independent))
            self.assertEqual(2, len(raw_calls))
            self.assertEqual(len(result[1][0]) + len(shared) - 1, contexts[0]._reused)
        path = parent.target / '.hrn/work/child-a/identity.json'; original = path.read_bytes()
        with self.subTest(variant='child-record-drift'):
            try:
                path.write_bytes(b'{}\n'); self.assertEqual('degraded', observe(parent.target)[0][0]['classification'])
            finally: path.write_bytes(original)
        path = parent.target / '.hrn/work/parent/current.json'; original = path.read_bytes()
        with self.subTest(variant='pending-parent'):
            try:
                path.unlink(); result = observe(parent.target)[0]
                self.assertEqual('partial', result[0]['classification']); self.assertIsNone(result[1])
            finally: path.write_bytes(original)
        parent.success = True
        worker = worker_fixtures.InstalledWorkerPublicationTests()
        worker.setUp(); self.addCleanup(worker.doCleanups)
        worker.prepare_worker_result()
        with self.subTest(variant='worker-control'):
            result, calls, contexts, raw_calls = observe(worker.target)
            self.assertEqual('pass', result[0]['classification']); self.assertEqual(1, len(contexts))
            self.assertEqual('review', result[1][0]['work-a']['state']); self.assertEqual(2, len(raw_calls))

    def test_default_readers_and_writers_do_not_receive_context(self):
        import test_general_work_invariants as writer_fixtures
        labels = []; current = []; raw_calls = []; visible = work._visible_truth; raw = workspace._topology_probe
        def truth(target, paths, **kw):
            labels.append((current[-1], kw.get('_topology_observation'))); return visible(target, paths, **kw)
        def raw_read(*a, **kw): raw_calls.append(current[-1]); return raw(*a, **kw)
        def run(label, operation):
            current.append(label)
            try: return operation()
            finally: current.pop()
        before = fixtures.exact_snapshot(self.target)
        with patch.object(work, '_visible_truth', truth), patch.object(workspace, '_topology_probe', raw_read), \
             patch.object(workspace._TopologyObservation, '__init__', side_effect=AssertionError('default context')):
            run('default-work', lambda: work.read_work(self.target, 'work-a'))
            run('default-intent', lambda: intent.read_workspace_intent_graph(self.target, 'intent-a'))
        self.assertEqual(before, fixtures.exact_snapshot(self.target))
        seam = writer_fixtures.IntentWriterTests(); seam.setUp(); self.addCleanup(seam.doCleanups)
        self.git(seam.target, 'init', '-q'); seam.accept()
        with patch.object(work, '_visible_truth', truth), patch.object(workspace, '_topology_probe', raw_read), \
             patch.object(workspace._TopologyObservation, '__init__', side_effect=AssertionError('writer context')):
            run('double-publish', seam.submitted)
            before_prepare = fixtures.exact_snapshot(seam.target)
            prepared = run('double-prepare', seam.prepare)
            self.assertEqual(before_prepare, fixtures.exact_snapshot(seam.target))
            graph = run('double-apply', lambda: seam.apply(prepared))
            self.assertEqual('completed', graph['state'])
        expected = {'default-work', 'default-intent', 'double-publish', 'double-prepare', 'double-apply'}
        self.assertEqual(expected, set(label for label, ctx in labels)); self.assertEqual(expected, set(raw_calls))
        self.assertTrue(all(ctx is None for label, ctx in labels))
        # The verifier double above is not installed-runtime evidence. Real bound
        # child writer success is covered separately by unmodified CLI fixtures.

    def test_context_rejects_target_environment_and_mutation_reuse(self):
        other = self.f.base / 'other-context-target'; other.mkdir()
        before = fixtures.exact_snapshot(self.f.base)
        for variant in ('target', 'environment', 'mutation', 'closed'):
            with self.subTest(variant=variant):
                ctx = workspace._TopologyObservation(self.target)
                workspace.classify_target(self.target, _topology_observation=ctx)
                try:
                    with ExitStack() as stack:
                        if variant == 'environment':
                            env = workspace.git_environment(); env['HV2_SYNTHETIC_CONTEXT'] = 'changed'
                            stack.enter_context(patch.object(workspace, 'git_environment', return_value=env))
                        if variant == 'closed': ctx.close()
                        with self.assertRaises(ContractError) as caught:
                            workspace.classify_target(other if variant == 'target' else self.target,
                                mutation=variant == 'mutation', _topology_observation=ctx)
                        self.assertEqual('HV2-WORKSPACE-TARGET', caught.exception.code)
                finally: ctx.close()
                self.assertTrue(ctx._closed); self.assertIsNone(ctx._raw)
        closed = workspace._TopologyObservation(self.target); closed.close()
        def invalid_context(target, paths, **kw): workspace.classify_target(target, _topology_observation=closed)
        with self.subTest(variant='product-degraded-boundary'), patch.object(work, '_visible_truth', invalid_context):
            status, graphs = product._workspace_status_observation(self.target)
            self.assertEqual('degraded', status['classification']); self.assertEqual('HV2-WORKSPACE-TARGET', status['error_code'])
            self.assertIsNone(graphs); text, code = view.render_view(self.target)
            self.assertEqual(10, code, text)
        with self.subTest(variant='view-unavailable-boundary'), patch.object(view, '_observe', side_effect=ContractError('HV2-WORKSPACE-TARGET', 'invalid topology observation use')):
            text, code = view.render_view(self.target); self.assertEqual(65, code, text)
        self.assertEqual(before, fixtures.exact_snapshot(self.f.base))

    def test_empty_work_and_failed_context_leave_no_state(self):
        raw = workspace._topology_probe
        before = fixtures.exact_snapshot(self.target)
        for eligible, count in ((0, 0), (1, 1), (2, 2)):
            with self.subTest(variant='eligible-count', eligible=eligible), patch.object(workspace, '_topology_probe', wraps=raw) as calls:
                ctx = workspace._TopologyObservation(self.target)
                for _ in range(eligible): workspace.classify_target(self.target, _topology_observation=ctx)
                ctx.finish(); self.assertEqual(count, calls.call_count)
                self.assertTrue(ctx._closed); self.assertIsNone(ctx._raw)
        empty = fixtures.ActualWorkspaceInitTests(); empty.setUp(); self.addCleanup(empty.doCleanups)
        self.git(empty.target, 'init', '-q'); empty.apply_init(empty.preview())
        contexts = []; init = workspace._TopologyObservation.__init__
        def initialize(ctx, target): init(ctx, target); contexts.append(ctx)
        with self.subTest(variant='real-empty-work'), patch.object(workspace._TopologyObservation, '__init__', initialize):
            observed = self.fresh_parity(empty.target)
            self.assertEqual('pass', observed[0]['classification']); self.assertEqual(({}, {}), observed[1])
        self.assertEqual(1, len(contexts)); self.assertEqual(0, contexts[0]._reused)
        self.assertTrue(contexts[0]._closed)
        with self.subTest(variant='failed-first-then-new-context'):
            failed = workspace._TopologyObservation(self.target)
            try:
                with patch.object(workspace, '_topology_probe', side_effect=FileNotFoundError('synthetic')):
                    with self.assertRaises(ContractError): workspace.classify_target(self.target, _topology_observation=failed)
            finally: failed.close()
            with self.assertRaises(ContractError): workspace.classify_target(self.target, _topology_observation=failed)
            healthy = workspace._TopologyObservation(self.target)
            self.assertIsNot(healthy, failed)
            try: self.assertEqual('primary', workspace.classify_target(self.target, _topology_observation=healthy)['kind'])
            finally: healthy.close()
            self.assertIsNone(failed._raw); self.assertIsNone(healthy._raw)
        self.assertEqual(before, fixtures.exact_snapshot(self.target))
