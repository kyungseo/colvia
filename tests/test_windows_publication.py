"""Native publication through installed entry and explicit crash-test doubles.

The installed subprocess checks real bound-entry behavior. Only injected crash
cases use a labelled runtime verifier double; their filesystem APIs remain real.
"""
from __future__ import annotations
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import unittest
import types

import test_umbrella_lifecycle as umbrella_fixtures

from hv2ref import product, work
from hv2ref.candidates import CandidateStore
from hv2ref.errors import ContractError, InjectedCrash
from hv2ref.intent import WorkspaceIntentStore
from test_candidates import proposal as candidate_request
import test_productization_safety as product_fixtures
from test_windows_lifecycle import (NativeLifecycleFixture, TIME, canonical, physical, sha, fail_native_flush_for,
                                    fail_native_replace_for, record_native_publication, assert_native_reflush_before,
                                    assert_native_staging_flush_before_replace)



def assert_fixture_worker_content(case, target, expected):
    """Observe the fixed synthetic namespace without product snapshot/parsers.

    expected maps result paths to (literal bytes, logical index/default mode).
    Authority, Git metadata, and the installed launcher have separate oracles.
    This fixture has no ignored user content or nested content directories.
    """
    raw = physical(target)
    content = {name: value for name, value in raw.items()
               if name.split('/')[0] not in {'.git', '.hrn', 'colvia'}}
    case.assertEqual(set(expected), set(content), 'independent content membership')
    result = subprocess.run(['git', '-C', str(target), 'ls-files', '--stage', '-z'],
                            capture_output=True, timeout=30)
    case.assertEqual(0, result.returncode, result.stderr)
    tracked = {}
    for row in result.stdout.split(b'\0'):
        if not row:
            continue
        header, name = row.split(b'\t', 1)
        mode, _oid, stage = header.split(b' ')
        case.assertEqual(b'0', stage)
        case.assertIn(mode, (b'100644', b'100755'))
        name = name.decode('utf-8')
        case.assertNotIn(name, tracked)
        tracked[name] = mode.decode('ascii')
    entries = []
    for name in sorted(expected, key=lambda value: value.encode('utf-8')):
        data, mode = expected[name]
        case.assertEqual('file', content[name][0], name)
        case.assertEqual(data, content[name][1], name)
        case.assertEqual(mode, tracked.get(name, '100644'), name)
        entries.append({'path': name, 'mode': mode, 'sha256': sha(data), 'size_bytes': len(data)})
    return entries


class PortablePublicationOracleTests(unittest.TestCase):
    def test_fixed_result_oracle_detects_membership_bytes_absence_and_index_mode(self):
        from pathlib import Path
        from tests.platform_fixtures import fixture_temporary_directory
        with fixture_temporary_directory() as temporary:
            target = Path(temporary)
            def git(*args):
                result = subprocess.run(['git', '-C', str(target), *args], capture_output=True, timeout=30)
                self.assertEqual(0, result.returncode, result.stderr)
            git('init', '-q')
            path = target / 'sample.txt'; path.write_bytes(b'changed\r\n')
            git('add', 'sample.txt')
            expected = {'sample.txt': (b'changed\r\n', '100644')}
            self.assertEqual(['sample.txt'], [e['path'] for e in assert_fixture_worker_content(self, target, expected)])
            extra = target / 'extra.txt'; extra.write_bytes(b'unexpected')
            with self.assertRaises(AssertionError): assert_fixture_worker_content(self, target, expected)
            extra.unlink(); path.write_bytes(b'different')
            with self.assertRaises(AssertionError): assert_fixture_worker_content(self, target, expected)
            path.unlink()
            with self.assertRaises(AssertionError): assert_fixture_worker_content(self, target, expected)
            path.write_bytes(b'changed\r\n'); git('update-index', '--chmod=+x', 'sample.txt')
            with self.assertRaises(AssertionError): assert_fixture_worker_content(self, target, expected)
            expected['sample.txt'] = (b'changed\r\n', '100755')
            assert_fixture_worker_content(self, target, expected)


@unittest.skipUnless(sys.platform == 'win32', 'native Windows publication; excluded from POSIX execution matrix')
class WindowsPublicationTests(NativeLifecycleFixture, unittest.TestCase):
    TIME = TIME
    draft = product_fixtures.ActualWorkspaceInitTests.draft
    accept_intent = product_fixtures.ActualWorkspaceInitTests.accept_intent

    def installed(self, args, value=None, *, expected=0, env=None, target=None, timeout=300):
        target = target or self.target
        argv = [sys.executable, '-I', '-B', str(target / 'colvia'), *map(str, args)]
        started = time.monotonic()
        print('NATIVE_INSTALLED_START ' + json.dumps({'argv': argv, 'limit_seconds': timeout}), flush=True)
        try:
            result = subprocess.run(argv, input=canonical(value) if value is not None else None,
                                    capture_output=True, cwd=target, env=env, timeout=timeout)
        finally:
            print('NATIVE_INSTALLED_TIMING ' + json.dumps({'argv': argv, 'limit_seconds': timeout,
                  'elapsed_seconds': time.monotonic() - started}), flush=True)
        self.assertEqual(expected, result.returncode, (result.stdout + result.stderr).decode(errors='replace'))
        self.assertEqual(b'', result.stderr)
        return result

    def git(self, target, *args):
        result = subprocess.run(['git', '-c', 'user.name=Synthetic Test', '-c', 'user.email=fixture@example.invalid',
                                 '-c', 'maintenance.auto=false', '-c', 'gc.auto=0', '-C', str(target), *args],
                                capture_output=True, timeout=30)
        self.assertEqual(0, result.returncode, result.stderr.decode(errors='replace'))
        return result.stdout.strip().decode()

    def observed(self, target):
        observed = product.verify_workspace_product(target)
        return {'binding_ref': observed['binding_ref'], 'launcher_sha256': observed['launcher_sha256'],
                'inventory_id': observed['inventory']['inventory_id']}

    def snapshot(self, target=None):
        runtime = self.observed(self.target)
        return work.snapshot(target or self.target, verified_launcher_sha256=runtime['launcher_sha256'], verified_inventory_id=runtime['inventory_id'])

    def assert_independent_worker_result(self, manifest):
        entries = assert_fixture_worker_content(self, self.target, self.worker_expected)
        self.assertEqual(entries, manifest['result']['entries'])
        tree = {name: value for name, value in manifest['result'].items() if name != 'sha256'}
        self.assertEqual(sha(canonical(tree)), manifest['result']['sha256'])

    def request(self, tree, *, mode='local', operation='start', parent=None, manifest=None, scope=None):
        scope = scope or ['sample.txt']
        manifest = manifest or work.make_manifest(tree, tree, scope=scope)
        identity = {'record_type': 'work-identity', 'schema_version': 1, 'authority_home_id': 'home-a',
                    'work_id': 'work-a', 'work_type': 'change', 'created_at': TIME, 'acceptance_authority': 'owner', 'lineage': None}
        revision = {'record_type': 'work-revision', 'schema_version': 1, 'authority_home_id': 'home-a', 'work_id': 'work-a',
                    'record_id': operation, 'observed_at': TIME, 'observed_scope': [], 'unavailable_scope': [],
                    'author': 'agent', 'operation': operation, 'expected_prior_selection': parent, 'intent_ref': self.intent,
                    'scope': scope, 'document_refs': [], 'evidence_refs': [],
                    'result_refs': {'manifest': {'id': sha(canonical(manifest)), 'sha256': sha(canonical(manifest))}},
                    'progress': 'review' if operation == 'submit-result' else 'active', 'next_action': 'synthetic review',
                    'relations': [], 'rebind_from': None, 'execution_context': {'mode': mode, 'attempt_id': 'attempt-a'}}
        return {'identity': identity, 'revision': revision, 'manifest': manifest, 'selection_id': operation + '-s', 'operation_id': operation + '-o'}

    def prepare(self, action='accept', *, expected=0, supersedes=None):
        value = {'work_id': 'work-a', 'action': action, 'actor': 'owner', 'reason': 'synthetic decision',
                 'request_id': action + '-a', 'observed_at': TIME, 'revision_ref': None, 'supersedes': supersedes}
        return json.loads(self.installed(['work', 'prepare'], value, expected=expected).stdout)

    def apply(self, prepared, *, expected=0):
        return json.loads(self.installed(['work', 'apply', '--confirm', prepared['confirm_token']], prepared['ticket'], expected=expected).stdout)

    def worker_result(self, *, new_executable=False, tracked_add=False, existing_executable=False, mode_change=False, relocated=None, executable_delete=False, initial_source=None):
        (self.target / 'b').write_bytes(b'delete\n')
        self.git(self.target, 'init', '-q')
        self.git(self.target, 'config', 'core.autocrlf', getattr(self, 'autocrlf', 'false'))
        if initial_source is None:
            self.init()
        else:
            preview = product.workspace_init_preview(initial_source, self.target,
                authority_home_id='home-a', operation_id='init-a', created_at=TIME)
            product.workspace_init_apply(initial_source, self.target, preview['request'],
                confirm_token=preview['confirm_token'])
        self.intent = self.accept_intent()
        self.git(self.target, 'add', '.')
        # The existing retained-source contract requires this exact Git mode.
        # This is explicit operator fixture setup, never a product index write.
        self.git(self.target, 'update-index', '--chmod=+x', 'colvia')
        if existing_executable: self.git(self.target, 'update-index', '--chmod=+x', 'sample.txt')
        if executable_delete: self.git(self.target, 'update-index', '--chmod=+x', 'b')
        self.git(self.target, 'commit', '-qm', 'synthetic baseline')
        oid = self.git(self.target, 'rev-parse', 'HEAD'); self.git(self.target, 'branch', 'retained-base', oid)
        base = self.snapshot(); scope = ['sample.txt', 'b', 'new.exe']
        if relocated: scope.append('relocated.exe')
        start_manifest = work.make_manifest(base, base, scope=scope, base_commit=oid, candidate_commit=oid,
                                            base_retention_ref='refs/heads/retained-base', candidate_retention_ref='refs/heads/retained-base')
        initial = self.request(base, mode='isolated-worktree', manifest=start_manifest, scope=scope)
        graph = json.loads(self.installed(['work', 'publish'], initial).stdout)
        worker = self.target.with_name(self.target.name + 'w')
        self.git(self.target, 'worktree', 'add', '-q', '-b', 'candidate', str(worker), oid)
        (worker / 'sample.txt').write_bytes(b'changed\r\n'); (worker / 'b').unlink(); (worker / 'new.exe').write_bytes(b'new\n')
        if relocated:
            (worker / 'relocated.exe').write_bytes((worker / 'sample.txt').read_bytes())
            if relocated == 'move': (worker / 'sample.txt').unlink()
        self.git(worker, 'add', '.')
        if relocated and existing_executable: self.git(worker, 'update-index', '--chmod=+x', 'relocated.exe')
        if new_executable or tracked_add: self.git(worker, 'update-index', '--chmod=+x', 'new.exe')
        if mode_change: self.git(worker, 'update-index', '--chmod=+x', 'sample.txt')
        self.git(worker, 'commit', '-qm', 'synthetic result')
        if tracked_add:
            # The operator fixture stages an absent tracked candidate before
            # publication. Product apply must keep this exact index unchanged.
            blob = self.git(worker, 'rev-parse', 'HEAD:new.exe')
            self.git(self.target, 'update-index', '--add', '--cacheinfo', '100755,' + blob + ',new.exe')
        # Fix literal expected bytes/modes from the synthetic mutation, never
        # from the product snapshot or the manifest being checked.
        self.worker_expected = {'new.exe': (b'new\n', '100755' if new_executable or tracked_add else '100644')}
        if relocated != 'move':
            self.worker_expected['sample.txt'] = (b'changed\r\n', '100755' if existing_executable or mode_change else '100644')
        if relocated:
            self.worker_expected['relocated.exe'] = (b'changed\r\n', '100755' if existing_executable else '100644')
        result = work.make_manifest(base, self.snapshot(worker), scope=scope, base_commit=oid,
                                    candidate_commit=self.git(worker, 'rev-parse', 'HEAD'),
                                    base_retention_ref='refs/heads/retained-base', candidate_retention_ref='refs/heads/candidate')
        request = self.request(base, mode='isolated-worktree', operation='submit-result', parent=graph['current']['selection_ref'], manifest=result, scope=scope)
        before = physical(self.target)
        self.installed(['work', 'publish', '--target', self.target, '--worker', worker], request, target=worker, expected=65)
        self.assertEqual(before, physical(self.target))
        review = json.loads(self.installed(['work', 'publish', '--worker', worker], request).stdout)
        self.assertEqual('review', review['state']); self.assertEqual(base, self.snapshot())
        return result, worker

    def test_installed_non_git_work_and_completed_readonly_replay(self):
        self.init(); self.intent = self.accept_intent(); base = self.snapshot()
        initial = self.request(base); graph = json.loads(self.installed(['work', 'publish'], initial).stdout)
        (self.target / 'sample.txt').write_bytes(b'after\r\n')
        manifest = work.make_manifest(base, self.snapshot(), scope=['sample.txt'])
        result = self.request(base, operation='submit-result', parent=graph['current']['selection_ref'], manifest=manifest)
        self.installed(['work', 'publish'], result); prepared = self.prepare()
        self.assertEqual('completed', self.apply(prepared)['state'])
        for p in (self.target / '.hrn/work/work-a').rglob('*.json'): os.chmod(p, 0o444)
        before = physical(self.target)
        self.assertEqual('completed', self.apply(prepared)['state'])
        self.assertEqual(before, physical(self.target))

    def test_installed_non_git_historical_executable_input_is_preserved_and_refused(self):
        import copy
        self.init(); self.intent = self.accept_intent()
        legacy = copy.deepcopy(self.snapshot())
        self.assertEqual(['sample.txt'], [entry['path'] for entry in legacy['entries']])
        legacy['entries'][0]['mode'] = '100755'
        legacy['sha256'] = sha(canonical({key: value for key, value in legacy.items() if key != 'sha256'}))
        request = self.request(legacy)
        retained = self.root / 'historical-input.json'; original = canonical(request)
        retained.write_bytes(original)
        before = physical(self.target)
        failure = json.loads(self.installed(['work', 'publish', '--input', retained], expected=65).stdout)
        self.assertIn('retained 100755', failure['message'])
        self.assertEqual(original, retained.read_bytes()); self.assertEqual(before, physical(self.target))
        self.assertFalse((self.target / '.hrn/work/work-a').exists())

    def test_worker_whole_union_readonly_refused_before_decision_then_exact_apply(self):
        manifest, worker = self.worker_result(); prepared = self.prepare()
        os.chmod(self.target / 'sample.txt', 0o444); before = physical(self.target)
        failure = self.apply(prepared, expected=65)
        self.assertIn('read-only', failure['message'])
        self.assertEqual(before, physical(self.target))
        self.assertEqual({}, work.read_work(self.target, 'work-a')['decisions'])
        os.chmod(self.target / 'sample.txt', 0o666)
        git_before = physical(self.target / '.git')
        self.assertEqual('completed', self.apply(prepared)['state'])
        self.assert_independent_worker_result(manifest)
        self.assertEqual(manifest['result'], self.snapshot())
        self.assertEqual(git_before, physical(self.target / '.git'))
        self.assertFalse((self.target / 'b').exists())
        self.assertEqual('100644', next(e['mode'] for e in self.snapshot()['entries'] if e['path'] == 'new.exe'))

    def test_unreproducible_worker_mode_keeps_review_and_allows_ordinary_reject(self):
        self.worker_result(new_executable=True); before = physical(self.target)
        failure = self.prepare(expected=65)
        self.assertIn('post mode', failure['message'])
        self.assertEqual(before, physical(self.target))
        rejected = self.apply(self.prepare('reject'))
        self.assertEqual('rejected', rejected['state'])
        self.assertEqual(b'before\r\n', (self.target / 'sample.txt').read_bytes())
        self.assertFalse((self.target / 'new.exe').exists())

    def test_worker_each_publication_prefix_recovers_with_independent_whole_result(self):
        for number, point in enumerate(('after-decision', 'after-staged-file', 'after-file', 'after-selection', 'after-staged-current', 'after-current')):
            with self.subTest(point=point):
                self.target = self.root / ('p' + str(number)); self.target.mkdir()
                (self.target / 'sample.txt').write_bytes(b'before\r\n')
                manifest, worker = self.worker_result(); prepared = self.prepare(); git_before = physical(self.target / '.git')
                # Explicit verifier double for injection only; native IO and
                # the full Work state/content machine are not substituted.
                store = work.WorkStore(self.target, self.observed)
                with self.assertRaises(InjectedCrash):
                    store.apply(prepared['ticket'], confirm_token=prepared['confirm_token'], inject_at=point)
                prefix = physical(self.target)
                self.assertEqual('completed', self.apply(prepared)['state'])
                self.assert_independent_worker_result(manifest)
                self.assertEqual(manifest['result'], self.snapshot())
                self.assertEqual(git_before, physical(self.target / '.git'))
                print('NATIVE_WORKER_PREFIX ' + json.dumps({'point': point, 'paths_observed': len(prefix), 'recovered': True}), flush=True)

    def test_worker_required_flush_failure_keeps_decision_prefix_and_original_ticket(self):
        manifest, worker = self.worker_result(); prepared = self.prepare()
        ticket_bytes = canonical(prepared)
        decision_path = self.target / '.hrn/work/work-a/decisions' / ('decision-' + sha(canonical(prepared['ticket'])) + '.json')
        git_before = physical(self.target / '.git')
        store = work.WorkStore(self.target, self.observed)  # Injection-only runtime verifier double.
        with fail_native_flush_for(decision_path) as failures:
            with self.assertRaisesRegex(ContractError, 'created-file-content.*winerror=5'):
                store.apply(prepared['ticket'], confirm_token=prepared['confirm_token'])
        self.assertEqual(1, len(failures)); self.assertTrue(decision_path.is_file())
        decision_bytes = decision_path.read_bytes()
        self.assertEqual(prepared['ticket'], json.loads(decision_bytes)['confirmation'])
        self.assertEqual(b'before\r\n', (self.target / 'sample.txt').read_bytes())
        self.assertEqual(b'delete\n', (self.target / 'b').read_bytes())
        self.assertFalse((self.target / 'new.exe').exists())
        self.assertEqual(git_before, physical(self.target / '.git'))
        with fail_native_replace_for(self.target / 'sample.txt') as replacements, record_native_publication() as events:
            with self.assertRaisesRegex(ContractError, 'replace-publication.*winerror=32'):
                store.apply(prepared['ticket'], confirm_token=prepared['confirm_token'])
        self.assertEqual(1, len(replacements))
        assert_native_reflush_before(self, events, decision_path, self.target / 'b')
        assert_native_staging_flush_before_replace(self, events, self.target / 'sample.txt')
        self.assertEqual('completed', self.apply(prepared)['state'])
        self.assert_independent_worker_result(manifest)
        self.assertEqual(manifest['result'], self.snapshot())
        self.assertEqual(git_before, physical(self.target / '.git'))
        self.assertEqual(decision_bytes, decision_path.read_bytes()); self.assertEqual(ticket_bytes, canonical(prepared))
        print('NATIVE_WORKER_FLUSH_PREFIX ' + json.dumps({'phase': 'created-file-content', 'injected_winerror': 5, 'decision_visible': True, 'original_ticket_resumed': True}), flush=True)

    def test_partial_work_required_reflush_readonly_refuses_without_new_publication(self):
        self.init(); self.intent = self.accept_intent(); initial = self.request(self.snapshot())
        store = work.WorkStore(self.target, self.observed)
        with self.assertRaises(InjectedCrash): store.publish(**initial, inject_at='after-manifest')
        existing = self.target / '.hrn/work/work-a/results' / (sha(canonical(initial['manifest'])) + '.json')
        os.chmod(existing, 0o444); before = physical(self.target)
        with self.assertRaisesRegex(ContractError, 'read-only'): store.publish(**initial)
        self.assertEqual(before, physical(self.target))
        self.assertFalse((self.target / '.hrn/work/work-a/revisions/start.json').exists())
        os.chmod(existing, 0o666)
        self.assertEqual('active', json.loads(self.installed(['work', 'publish'], initial).stdout)['state'])

    def test_intent_reflush_and_planning_replacement_preserve_readonly_bytes(self):
        self.init(); draft = self.draft(); intent_store = WorkspaceIntentStore(self.target, self.observed)
        with self.assertRaises(InjectedCrash): intent_store.publish_draft(draft, inject_at='after-home')
        existing = self.target / '.hrn/intents/intent-a/identity.json'
        os.chmod(existing, 0o444); before = physical(self.target)
        with self.assertRaisesRegex(ContractError, 'read-only'): intent_store.publish_draft(draft)
        self.assertEqual(before, physical(self.target)); os.chmod(existing, 0o666)
        self.intent = self.accept_intent()
        candidates = CandidateStore(self.target, self.observed)
        first = candidate_request(self.target); candidates.mutate(first)
        file = self.target / '.hrn/planning/candidates.json'; os.chmod(file, 0o444)
        before = physical(self.target)
        self.assertEqual('unchanged', candidates.mutate(first)['classification'])
        second = candidate_request(self.target, cid='idea-b')
        with self.assertRaisesRegex(ContractError, 'read-only'): candidates.mutate(second)
        self.assertEqual(before, physical(self.target))
        os.chmod(file, 0o666); self.assertEqual('saved', candidates.mutate(second)['classification'])


    def test_intent_flush_then_current_replace_failure_resumes_original_ticket(self):
        self.init(); draft = self.draft(); self.installed(['intent', 'draft'], draft)
        request = {'intent_id': 'intent-a', 'revision_ref': work.record_ref(draft, 'revision_id'), 'actor': 'owner',
                   'reason': 'synthetic failure prefix', 'request_id': 'intent-accept-a', 'observed_at': TIME}
        prepared = json.loads(self.installed(['intent', 'prepare'], request).stdout); fixed = canonical(prepared)
        home = self.target / '.hrn/intents/intent-a'; acceptance = home / 'acceptances' / ('acceptance-' + sha(canonical(prepared['ticket'])) + '.json')
        store = WorkspaceIntentStore(self.target, self.observed)  # Labelled injection-only runtime verifier.
        with fail_native_flush_for(acceptance) as failures:
            with self.assertRaisesRegex(ContractError, 'created-file-content.*winerror=5'):
                store.apply(prepared['ticket'], confirm_token=prepared['confirm_token'])
        self.assertEqual(1, len(failures)); accepted_bytes = acceptance.read_bytes()
        self.assertEqual(prepared['ticket'], json.loads(accepted_bytes)['confirmation']); self.assertFalse((home / 'current.json').exists())
        with fail_native_replace_for(home / 'current.json') as replacements, record_native_publication() as events:
            with self.assertRaisesRegex(ContractError, 'replace-publication.*winerror=32'):
                store.apply(prepared['ticket'], confirm_token=prepared['confirm_token'])
        assert_native_reflush_before(self, events, acceptance, home / 'current.json')
        assert_native_staging_flush_before_replace(self, events, home / 'current.json')
        self.assertEqual(1, len(replacements)); self.assertFalse((home / 'current.json').exists())
        staged = Path(replacements[0]['source']); staged_bytes = staged.read_bytes()
        self.assertEqual(accepted_bytes, acceptance.read_bytes()); self.assertEqual(b'before\r\n', (self.target / 'sample.txt').read_bytes())
        graph = json.loads(self.installed(['intent', 'apply', '--confirm', prepared['confirm_token']], prepared['ticket']).stdout)
        self.assertEqual([], graph['pending_acceptances'] + graph['pending_selections'])
        self.assertEqual(1, len(graph['acceptances'])); self.assertEqual(1, len(graph['selections']))
        self.assertEqual(staged_bytes, (home / 'current.json').read_bytes()); self.assertEqual(accepted_bytes, acceptance.read_bytes())
        self.assertEqual(fixed, canonical(prepared)); self.assertEqual(b'before\r\n', (self.target / 'sample.txt').read_bytes())

    def test_planning_flush_then_replace_failure_preserves_prior_and_exact_retry(self):
        self.init(); store = CandidateStore(self.target, self.observed)
        first = candidate_request(self.target); store.mutate(first)
        path = self.target / '.hrn/planning/candidates.json'; original = path.read_bytes()
        second = candidate_request(self.target, cid='idea-b'); fixed = canonical(second)
        staging = self.target / '.hrn/staging'
        with fail_native_flush_for(staging, name_prefix='candidate-') as failures:
            with self.assertRaisesRegex(ContractError, 'file-content.*winerror=5'): store.mutate(second)
        self.assertEqual(1, len(failures)); self.assertEqual(original, path.read_bytes())
        failed_flush = {p.name: p.read_bytes() for p in staging.iterdir() if p.is_file()}
        self.assertTrue(any(name.startswith('candidate-') for name in failed_flush))
        with fail_native_replace_for(path) as replacements, record_native_publication() as events:
            with self.assertRaisesRegex(ContractError, 'replace-publication.*winerror=32'): store.mutate(second)
        assert_native_staging_flush_before_replace(self, events, path)
        self.assertEqual(1, len(replacements)); self.assertEqual(original, path.read_bytes())
        pending = Path(replacements[0]['source']); pending_bytes = pending.read_bytes()
        self.assertEqual('saved', json.loads(self.installed(['candidate', 'add'], second).stdout)['classification'])
        self.assertEqual(pending_bytes, path.read_bytes())
        data = json.loads(path.read_bytes()); self.assertEqual([first, second], [d['request'] for d in data['decisions']])
        self.assertEqual(fixed, canonical(second)); self.assertEqual(b'before\r\n', (self.target / 'sample.txt').read_bytes())
        for name, raw in failed_flush.items(): self.assertEqual(raw, (staging / name).read_bytes())
        self.assertEqual(pending_bytes, pending.read_bytes())

    def test_parent_decision_flush_then_selector_replace_retains_original_ticket(self):
        self.init(); (self.target / 'a').write_bytes(b'initial\n'); (self.target / 'report.md').write_bytes(b'pending\n')
        h = types.SimpleNamespace(target=self.target, TIME=TIME, serial=0, installed=self.installed,
                                  q=lambda kind,name: {'authority_home_id':'home-a','kind':kind,'id':name})
        fixture = umbrella_fixtures.InstalledUmbrellaLifecycleTests
        for name in ('draft', 'accept', 'publish', 'prepare', 'apply'): setattr(h, name, types.MethodType(getattr(fixture, name), h))
        child = h.accept(h.draft()); h.composition = {'parent': h.q('work', 'parent'), 'required_children': [
            {'work': h.q('work', 'child-a'), 'intent': h.q('intent', 'intent-a')}]}
        draft = {**h.draft(intent_id='parent-intent'), 'schema_version': 2, 'composition': h.composition}
        parent = h.accept(draft); h.publish('parent', parent, 'start', parent=True)
        h.publish('child-a', child, 'start'); (self.target / 'a').write_bytes(b'child result\n')
        h.publish('child-a', child, 'submit-result'); h.apply(h.prepare('child-a'))
        second = {**h.draft(2, intent_id='parent-intent', prior=draft), 'schema_version': 2, 'composition': h.composition}
        refreshed = h.accept(second); revision, _ = h.publish('parent', refreshed, 'rebind', parent=True, old_intent=parent)
        h.apply(h.prepare('parent', 'rebind', revision)); (self.target / 'report.md').write_bytes(b'Combined child bytes independently checked.\n')
        h.publish('parent', refreshed, 'submit-result', parent=True); prepared = h.prepare('parent'); fixed = canonical(prepared)
        home = self.target / '.hrn/work/parent'; current_bytes = (home / 'current.json').read_bytes()
        decision = home / 'decisions' / ('decision-' + sha(canonical(prepared['ticket'])) + '.json')
        store = work.WorkStore(self.target, self.observed)  # Labelled injection-only runtime verifier.
        with fail_native_flush_for(decision) as failures:
            with self.assertRaisesRegex(ContractError, 'created-file-content.*winerror=5'):
                store.apply(prepared['ticket'], confirm_token=prepared['confirm_token'])
        self.assertEqual(1, len(failures)); decision_bytes = decision.read_bytes()
        self.assertEqual(prepared['ticket'], json.loads(decision_bytes)['confirmation']); self.assertEqual(current_bytes, (home / 'current.json').read_bytes())
        with fail_native_replace_for(home / 'current.json') as replacements, record_native_publication() as events:
            with self.assertRaisesRegex(ContractError, 'replace-publication.*winerror=32'):
                store.apply(prepared['ticket'], confirm_token=prepared['confirm_token'])
        assert_native_reflush_before(self, events, decision, home / 'current.json')
        assert_native_staging_flush_before_replace(self, events, home / 'current.json')
        self.assertEqual(1, len(replacements)); self.assertEqual(current_bytes, (home / 'current.json').read_bytes())
        staged_bytes = Path(replacements[0]['source']).read_bytes()
        for name, expected in {'sample.txt': b'before\r\n', 'a': b'child result\n', 'report.md': b'Combined child bytes independently checked.\n'}.items():
            self.assertEqual(expected, (self.target / name).read_bytes())
        self.assertEqual('completed', h.apply(prepared)['state']); self.assertEqual(staged_bytes, (home / 'current.json').read_bytes())
        self.assertEqual(decision_bytes, decision.read_bytes()); self.assertEqual(fixed, canonical(prepared))
        for name, expected in {'sample.txt': b'before\r\n', 'a': b'child result\n', 'report.md': b'Combined child bytes independently checked.\n'}.items():
            self.assertEqual(expected, (self.target / name).read_bytes())
        self.assertEqual('completed', work.read_work(self.target, 'child-a')['state'])

    def test_tracked_add_and_existing_executable_edit_preserve_control_git(self):
        manifest, worker = self.worker_result(tracked_add=True, existing_executable=True)
        before = physical(self.target / '.git'); prepared = self.prepare()
        self.assertEqual('completed', self.apply(prepared)['state'])
        self.assert_independent_worker_result(manifest)
        self.assertEqual(manifest['result'], self.snapshot())
        modes = {e['path']: e['mode'] for e in self.snapshot()['entries']}
        self.assertEqual('100755', modes['new.exe']); self.assertEqual('100755', modes['sample.txt'])
        self.assertEqual(before, physical(self.target / '.git'))
        os.chmod(self.target / 'new.exe', 0o444)
        preserved = physical(self.target)
        self.assertEqual('completed', self.apply(prepared)['state'])
        self.assertEqual(preserved, physical(self.target))

    def test_existing_mode_change_and_prechanged_control_index_remain_nonpass(self):
        self.worker_result(mode_change=True); before = physical(self.target)
        failure = self.prepare(expected=65)
        self.assertIn('existing-file mode change', failure['message'])
        self.assertEqual(before, physical(self.target))
        self.git(self.target, 'update-index', '--chmod=+x', 'sample.txt')
        before = physical(self.target)
        failure = self.prepare(expected=65)
        self.assertIn('worker recovery blocked', failure['message'])
        self.assertEqual(before, physical(self.target))
        self.assertEqual({}, work.read_work(self.target, 'work-a')['decisions'])

    def test_prepare_index_drift_pending_barrier_and_original_cancel(self):
        self.worker_result(); prepared = self.prepare()
        self.git(self.target, 'update-index', '--assume-unchanged', 'sample.txt')
        before = physical(self.target)
        self.assertIn('special flags', self.apply(prepared, expected=65)['message'])
        self.assertEqual(before, physical(self.target))
        self.assertEqual({}, work.read_work(self.target, 'work-a')['decisions'])
        self.git(self.target, 'update-index', '--no-assume-unchanged', 'sample.txt')
        store = work.WorkStore(self.target, self.observed)
        with self.assertRaises(InjectedCrash):
            store.apply(prepared['ticket'], confirm_token=prepared['confirm_token'], inject_at='after-decision')
        graph = work.read_work(self.target, 'work-a'); decision = graph['decisions'][graph['pending_decisions'][0]]
        before = physical(self.target)
        with self.assertRaisesRegex(ContractError, 'pending transaction'):
            CandidateStore(self.target, self.observed).mutate(candidate_request(self.target))
        self.assertEqual(before, physical(self.target))
        (self.target / 'outside.txt').write_bytes(b'preserved outside drift')
        cancel = self.prepare('reject', supersedes=work.record_ref(decision))
        self.assertEqual('rejected', self.apply(cancel)['state'])
        self.assertEqual(b'before\r\n', (self.target / 'sample.txt').read_bytes())
        self.assertEqual(b'preserved outside drift', (self.target / 'outside.txt').read_bytes())
        before = physical(self.target); self.apply(prepared, expected=65)
        self.assertEqual(before, physical(self.target))


    def switch_candidate(self, action, *, source=None):
        source = self.q if source is None else source
        args = [action, '--operation-id', action + '-compat', '--observed-at', TIME]
        if action == 'update': args += ['--source', source]
        preview = json.loads(self.installed(args).stdout)
        apply_args = [action, '--apply', '--input', '-', '--confirm', preview['confirm_token']]
        if action == 'update': apply_args += ['--source', source]
        # Native repeated release checks exceeded 60s after binding publication.
        # Only lifecycle apply gets this measured allowance; the run stays bounded.
        self.installed(apply_args, preview['request'], timeout=120)

    def assert_both_readers(self, expected_work, expected_state, label):
        program = ("import sys,json;from pathlib import Path;sys.path.insert(0,sys.argv[1]);"
                   "from hv2ref.work import WorkStore;from hv2ref.intent import workspace_intents;"
                   "from hv2ref.candidates import read_candidates;"
                   "t=Path(sys.argv[2]);print(json.dumps({'works':WorkStore(t)._all(),"
                   "'intents':workspace_intents(t),'planning':read_candidates(t)},sort_keys=True))")
        before = physical(self.target); outputs = []
        for reader, source in (('P', self.p), ('Q', self.q)):
            result = subprocess.run([sys.executable, '-I', '-B', '-c', program, str(source / 'src'), str(self.target)],
                                    cwd=self.target, capture_output=True, timeout=60)
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertEqual(b'', result.stderr)
            value = json.loads(result.stdout)
            self.assertEqual(expected_state, value['works'][expected_work]['state'])
            self.assertTrue(value['intents']); self.assertTrue(value['planning']['store']['candidates'])
            self.assertEqual(before, physical(self.target))
            outputs.append(value)
            print('NATIVE_PQ_READER ' + json.dumps({'reader': reader, 'writer_phase': label,
                  'work': expected_work, 'state': expected_state, 'graph_sha256': sha(canonical(value)),
                  'target_unchanged': True}), flush=True)
        self.assertEqual(outputs[0], outputs[1])

    def test_pq_local_and_planning_both_directions(self):
        self.init(); self.intent = self.accept_intent(); base = self.snapshot()
        graph = json.loads(self.installed(['work', 'publish'], self.request(base)).stdout)
        self.installed(['candidate', 'add'], candidate_request(self.target, cid='idea-p'))
        self.assert_both_readers('work-a', 'active', 'P-local-planning')
        self.switch_candidate('update')
        (self.target / 'sample.txt').write_bytes(b'Q result\r\n')
        result = self.request(base, operation='submit-result', parent=graph['current']['selection_ref'],
                              manifest=work.make_manifest(base, self.snapshot(), scope=['sample.txt']))
        self.installed(['work', 'publish'], result); self.apply(self.prepare())
        self.installed(['candidate', 'add'], candidate_request(self.target, cid='idea-q'))
        self.assert_both_readers('work-a', 'completed', 'Q-local-planning')
        self.switch_candidate('rollback'); self.assert_both_readers('work-a', 'completed', 'P-after-Q-rollback')

    def test_q_created_continuation_is_read_by_p_after_native_rollback(self):
        from hv2ref.continuation import read_continuation
        self.init(); self.intent = self.accept_intent(); base = self.snapshot()
        graph = json.loads(self.installed(['work', 'publish'], self.request(base)).stdout)
        request = self.request(base, operation='submit-result', parent=graph['current']['selection_ref'])
        self.installed(['work', 'publish'], request); self.apply(self.prepare())
        self.switch_candidate('update')
        value = {'work_id': 'work-a', 'action': 'select', 'actor': 'owner',
                 'owner_statement': 'Synthetic explicit Owner selection', 'reason': 'Native Q to P read',
                 'request_id': 'q-continuation', 'observed_at': TIME, 'choice': {'kind': 'none'}}
        prepared = json.loads(self.installed(['continuation', 'prepare'], value).stdout)
        product.verify_workspace_product(self.target)
        self.assert_product(self.q_candidate)
        self.installed(['continuation', 'apply', '--confirm', prepared['confirm_token']], prepared['ticket'])
        expected = json.loads(json.dumps(read_continuation(self.target, 'work-a')))
        self.switch_candidate('rollback')
        product.verify_workspace_product(self.target)
        self.assert_product(self.p_candidate)
        program = ("import sys,json;from pathlib import Path;sys.path.insert(0,sys.argv[1]);"
                   "from hv2ref.continuation import read_continuation;"
                   "print(json.dumps(read_continuation(Path(sys.argv[2]),'work-a')))")
        before = physical(self.target)
        for reader in (self.p, self.q):
            result = subprocess.run([sys.executable, '-I', '-B', '-c', program, str(reader / 'src'), str(self.target)],
                                    capture_output=True, cwd=self.target, timeout=60)
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertEqual(expected, json.loads(result.stdout)); self.assertEqual(before, physical(self.target))
        # P/Q differ in managed fixture bytes, not runtime implementation version.

    def test_pq_worker_both_directions_and_ticket_binding(self):
        for label, initial_source, next_source in (('P', None, None), ('Q', self.q, self.p)):
            with self.subTest(writer=label):
                if label == 'Q':
                    self.target = self.root / 'q-project'; self.target.mkdir()
                    (self.target / 'sample.txt').write_bytes(b'before\r\n')
                manifest, worker = self.worker_result(initial_source=initial_source)
                expected = self.p_candidate if label == 'P' else self.q_candidate
                self.assert_product(expected)
                self.installed(['candidate', 'add'], candidate_request(self.target, cid='worker-' + label.lower()))
                self.assert_both_readers('work-a', 'review', label + '-worker')
                git_before = physical(self.target / '.git')
                old_ticket = self.prepare(); self.switch_candidate('update', source=next_source)
                before = physical(self.target)
                self.apply(old_ticket, expected=65); self.assertEqual(before, physical(self.target))
                # Reader compatibility does not remove exact retained-launcher
                # provenance. A new ticket cannot bless mismatched Git sources.
                refused = self.prepare(expected=65)
                self.assertEqual('HV2-WORK-CONTENT', refused['code'])
                self.assertEqual('commit launcher differs from bound runtime', refused['message'])
                self.assertEqual(before, physical(self.target))
                self.assertEqual({}, work.read_work(self.target, 'work-a')['decisions'])
                self.assert_both_readers('work-a', 'review', label + '-worker-after-switch')
                self.switch_candidate('rollback')
                self.assert_product(expected)
                self.assertEqual('completed', self.apply(self.prepare())['state'])
                self.assert_independent_worker_result(manifest)
                self.assertEqual(manifest['result'], self.snapshot())
                self.assertEqual(git_before, physical(self.target / '.git'))
                self.assert_both_readers('work-a', 'completed', label + '-worker-completed')

    def test_pq_parent_both_directions_and_ticket_binding(self):
        self.init(); (self.target / 'a').write_bytes(b'initial\n'); (self.target / 'report.md').write_bytes(b'pending\n')
        h = types.SimpleNamespace(target=self.target, TIME=TIME, serial=0, installed=self.installed,
                                  q=lambda kind,name: {'authority_home_id':'home-a','kind':kind,'id':name})
        fixture = umbrella_fixtures.InstalledUmbrellaLifecycleTests
        for name in ('draft', 'accept', 'publish', 'prepare', 'apply'):
            setattr(h, name, types.MethodType(getattr(fixture, name), h))
        child = h.accept(h.draft())
        h.composition = {'parent':h.q('work','parent'), 'required_children':[
            {'work':h.q('work','child-a'), 'intent':h.q('intent','intent-a')}]}
        draft = {**h.draft(intent_id='parent-intent'), 'schema_version':2, 'composition':h.composition}
        parent = h.accept(draft); h.publish('parent', parent, 'start', parent=True)
        h.publish('child-a', child, 'start'); (self.target / 'a').write_bytes(b'child result\n')
        h.publish('child-a', child, 'submit-result'); h.apply(h.prepare('child-a'))
        self.installed(['candidate', 'add'], candidate_request(self.target, cid='parent-p'))
        self.assert_both_readers('parent', 'active', 'P-parent')
        self.switch_candidate('update')
        second = {**h.draft(2,intent_id='parent-intent',prior=draft), 'schema_version':2, 'composition':h.composition}
        refreshed = h.accept(second); revision, graph = h.publish('parent',refreshed,'rebind',parent=True,old_intent=parent)
        h.apply(h.prepare('parent','rebind',revision))
        (self.target / 'report.md').write_bytes(b'Combined child bytes independently checked.\n')
        self.assertEqual(b'child result\n', (self.target / 'a').read_bytes())
        h.publish('parent',refreshed,'submit-result',parent=True); old_ticket=h.prepare('parent')
        self.assert_both_readers('parent', 'review', 'Q-parent')
        self.switch_candidate('rollback')
        before=physical(self.target); h.apply(old_ticket,expected=65); self.assertEqual(before,physical(self.target))
        self.assertEqual('completed',h.apply(h.prepare('parent'))['state'])
        self.assert_both_readers('parent','completed','P-parent-after-Q')

    def test_worker_autocrlf_true_and_false_preserve_exact_result_and_git(self):
        # Changed sources stay byte-exact. Only this unchanged file exercises
        # the retained-LF/raw-CRLF exception under both operator configurations.
        attributes = b'* -text\nunchanged.bat text eol=crlf\n'
        unchanged_lf = b'@echo off\necho fixture\n'
        unchanged_crlf = b'@echo off\r\necho fixture\r\n'
        for setting in ('true','false'):
            with self.subTest(autocrlf=setting):
                self.target=self.root / setting; self.target.mkdir(); (self.target/'sample.txt').write_bytes(b'before\r\n')
                (self.target / '.gitattributes').write_bytes(attributes)
                (self.target / 'unchanged.bat').write_bytes(unchanged_crlf)
                self.autocrlf=setting; manifest,worker=self.worker_result()
                self.assertEqual(setting, self.git(self.target, 'config', '--get', 'core.autocrlf'))
                self.assertEqual({'sample.txt', 'b', 'new.exe'}, {c['path'] for c in manifest['changes']})
                trees = {name: {e['path']: e for e in manifest[name]['entries']} for name in ('base', 'result')}
                for path, expected in (('.gitattributes', attributes), ('unchanged.bat', unchanged_crlf)):
                    self.assertEqual(trees['base'][path], trees['result'][path])
                    self.assertEqual(expected, (self.target / path).read_bytes())
                    self.assertEqual(expected, (worker / path).read_bytes())
                unchanged_oids = []
                for commit, sample in ((manifest['base_commit'], b'before\r\n'),
                                       (manifest['candidate_commit'], b'changed\r\n')):
                    unchanged_oids.append(self.git(self.target, 'rev-parse', commit + ':unchanged.bat'))
                    for path, expected in (('.gitattributes', attributes), ('unchanged.bat', unchanged_lf),
                                           ('sample.txt', sample)):
                        retained = subprocess.run(['git', '-C', str(self.target), 'cat-file', 'blob', commit + ':' + path],
                                                  capture_output=True, timeout=30)
                        self.assertEqual(0, retained.returncode, retained.stderr)
                        self.assertEqual(b'', retained.stderr)
                        self.assertEqual(expected, retained.stdout, (commit, path))
                    self.assertEqual(['unchanged.bat: text: set', 'unchanged.bat: eol: crlf'],
                                     self.git(self.target, 'check-attr', '--source=' + commit,
                                              'text', 'eol', '--', 'unchanged.bat').splitlines())
                self.assertEqual(unchanged_oids[0], unchanged_oids[1])
                self.worker_expected.update({'.gitattributes': (attributes, '100644'),
                                             'unchanged.bat': (unchanged_crlf, '100644')})
                print('NATIVE_CRLF_PROOF ' + json.dumps({'autocrlf': setting,
                      'retained_lf_sha256': sha(unchanged_lf), 'checkout_crlf_sha256': sha(unchanged_crlf),
                      'unchanged_blob_oid': unchanged_oids[0], 'attributes_sha256': sha(attributes)}), flush=True)
                before=physical(self.target/'.git')
                self.assertEqual('completed',self.apply(self.prepare())['state'])
                self.assert_independent_worker_result(manifest)
                self.assertEqual(manifest['result'],self.snapshot())
                self.assertEqual(b'changed\r\n',(self.target/'sample.txt').read_bytes())
                self.assertEqual(unchanged_crlf, (self.target / 'unchanged.bat').read_bytes())
                self.assertEqual(attributes, (self.target / '.gitattributes').read_bytes())
                self.assertEqual(before,physical(self.target/'.git'))


    def test_worker_move_copy_common_condition_and_executable_deletion(self):
        for kind in ('move','copy'):
            for executable in (False,True):
                with self.subTest(kind=kind,logical_executable=executable):
                    self.target=self.root/(kind+str(int(executable)));self.target.mkdir()
                    (self.target/'sample.txt').write_bytes(b'before\r\n')
                    manifest,worker=self.worker_result(relocated=kind,existing_executable=executable,executable_delete=True)
                    before=physical(self.target);git_before=physical(self.target/'.git')
                    if executable:
                        self.assertIn('post mode',self.prepare(expected=65)['message'])
                        self.assertEqual(before,physical(self.target))
                        self.assertEqual({},work.read_work(self.target,'work-a')['decisions'])
                    else:
                        self.assertEqual('completed',self.apply(self.prepare())['state'])
                        self.assert_independent_worker_result(manifest)
                        self.assertEqual(manifest['result'],self.snapshot())
                        self.assertFalse((self.target/'b').exists())
                        self.assertEqual(b'changed\r\n',(self.target/'relocated.exe').read_bytes())
                        self.assertEqual(kind=='copy',(self.target/'sample.txt').exists())
                    self.assertEqual(git_before,physical(self.target/'.git'))

    def test_existing_untracked_and_index_only_default_worker_paths(self):
        for number, membership in enumerate(('existing-untracked', 'index-only-default')):
            with self.subTest(membership=membership):
                self.target = self.root / ('m' + str(number)); self.target.mkdir()
                (self.target / 'sample.txt').write_bytes(b'before\r\n')
                manifest, worker = self.worker_result()
                if membership == 'existing-untracked':
                    # Explicit operator fixture setup before prepare. The base
                    # and result stay retained, while current control paths are
                    # eligible untracked 100644 content.
                    self.git(self.target, 'rm', '--cached', '--', 'sample.txt', 'b')
                    state = work._windows_git_state(self.target)
                    self.assertTrue({'sample.txt', 'b'} <= state['untracked'])
                    self.assertFalse({'sample.txt', 'b'} & state['tracked'].keys())
                else:
                    blob = self.git(worker, 'rev-parse', 'HEAD:new.exe')
                    self.git(self.target, 'update-index', '--add', '--cacheinfo', '100644,' + blob + ',new.exe')
                    self.assertFalse((self.target / 'new.exe').exists())
                    self.assertEqual('100644', work._windows_git_state(self.target)['tracked']['new.exe'])
                self.assertEqual(manifest['base'], self.snapshot())
                git_before = physical(self.target / '.git')
                prepared = self.prepare()
                self.assertEqual('completed', self.apply(prepared)['state'])
                self.assert_independent_worker_result(manifest)
                self.assertEqual(manifest['result'], self.snapshot())
                self.assertEqual(b'changed\r\n', (self.target / 'sample.txt').read_bytes())
                self.assertFalse((self.target / 'b').exists())
                self.assertEqual(b'new\n', (self.target / 'new.exe').read_bytes())
                self.assertEqual(git_before, physical(self.target / '.git'))
                print('NATIVE_WORKER_MEMBERSHIP ' + json.dumps({'membership': membership,
                      'whole_result_verified': True, 'control_git_unchanged': True}), flush=True)

    def test_pending_worker_mode_drift_refuses_then_original_ticket_resumes(self):
        manifest, worker = self.worker_result(); prepared = self.prepare()
        exact_ticket = canonical(prepared)
        store = work.WorkStore(self.target, self.observed)
        # Only the injection path uses the explicit runtime verifier double;
        # resume and refusal use the real installed subprocess and native IO.
        with self.assertRaises(InjectedCrash):
            store.apply(prepared['ticket'], confirm_token=prepared['confirm_token'], inject_at='after-decision')
        self.git(self.target, 'update-index', '--chmod=+x', 'sample.txt')
        before = physical(self.target)
        self.assertIn('worker recovery blocked', self.apply(prepared, expected=65)['message'])
        self.assertEqual(before, physical(self.target))
        self.assertEqual(exact_ticket, canonical(prepared))
        self.git(self.target, 'update-index', '--chmod=-x', 'sample.txt')
        git_before = physical(self.target / '.git')
        self.assertEqual('completed', self.apply(prepared)['state'])
        self.assert_independent_worker_result(manifest)
        self.assertEqual(manifest['result'], self.snapshot())
        self.assertEqual(git_before, physical(self.target / '.git'))
        self.assertEqual(exact_ticket, canonical(prepared))
        print('NATIVE_WORKER_MODE_RESTORE ' + json.dumps({'pending_drift_refused': True,
              'original_ticket_resumed': True, 'whole_result_verified': True}), flush=True)
