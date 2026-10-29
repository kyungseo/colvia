"""Focused installed Windows-2 U1/delegation obligations.

P/Q differ in managed fixture bytes, not runtime implementation. Installed CLI
checks exercise native binding verification. Fault injection uses source APIs
with an explicit verifier adapter that observes the real installed product;
those injected cases are not independent installed-CLI or durability proof.
"""
from __future__ import annotations
import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest

from hv2ref import work
from hv2ref.continuation import ContinuationStore, read_continuation, records
from hv2ref.errors import ContractError, InjectedCrash
from hv2ref.intent import WorkspaceIntentStore, read_workspace_intent_graph
from test_windows_lifecycle import (NativeLifecycleFixture, MANAGED, TIME, canonical, sha, physical,
    fail_native_flush_for, fail_native_replace_for, record_native_publication,
    assert_native_reflush_before, assert_native_staging_flush_before_replace)
import test_windows_publication as native_helpers


@unittest.skipUnless(sys.platform == 'win32', 'native Windows only; no portable pass claim')
class WindowsU1DelegationTests(NativeLifecycleFixture, unittest.TestCase):
    TIME = TIME
    installed = native_helpers.WindowsPublicationTests.installed
    git = native_helpers.WindowsPublicationTests.git
    observed = native_helpers.WindowsPublicationTests.observed
    snapshot = native_helpers.WindowsPublicationTests.snapshot
    request = native_helpers.WindowsPublicationTests.request
    prepare = native_helpers.WindowsPublicationTests.prepare
    apply = native_helpers.WindowsPublicationTests.apply
    worker_result = native_helpers.WindowsPublicationTests.worker_result
    assert_independent_worker_result = native_helpers.WindowsPublicationTests.assert_independent_worker_result
    switch_candidate = native_helpers.WindowsPublicationTests.switch_candidate

    def assert_product(self, expected):
        root = self.target / '.hrn/product'; binding = json.loads((root / 'binding.json').read_bytes())
        self.assertEqual(expected['release_ref'], binding['active_release'])
        release_path = root / 'releases' / binding['active_release']['id']
        data = (release_path / 'inventory.json').read_bytes(); inventory = json.loads(data)
        self.assertEqual(binding['active_release']['sha256'], sha(data))
        self.assertEqual(MANAGED, tuple(e['path'] for e in inventory['entries']))
        for entry in inventory['entries']:
            actual = (release_path / 'payload' / entry['path']).read_bytes()
            self.assertEqual((entry['sha256'], entry['size_bytes']), (sha(actual), len(actual)))
            self.assertEqual(expected['payload'][entry['path']], actual)
        self.assertEqual(expected['payload']['colvia'], (self.target / 'colvia').read_bytes())
        expected_sample = self.worker_expected['sample.txt'][0] if hasattr(self, 'worker_expected') else b'before\r\n'
        self.assertEqual(expected_sample, (self.target / 'sample.txt').read_bytes())

    def event(self, phase, **data):
        row = {'test': self.id(), 'phase': phase, **data}
        path = self.root / 'observations.jsonl'
        with path.open('a', encoding='utf-8') as stream:
            stream.write(json.dumps(row, ensure_ascii=False)+'\n')
            stream.flush(); os.fsync(stream.fileno())
        print('NATIVE_OBLIGATION '+json.dumps(row), flush=True)

    def truth(self):
        return {name: value for name, value in physical(self.target).items()
                if name.startswith(('.hrn/intents/', '.hrn/work/')) or name in ('sample.txt', 'b', 'new.exe')}

    def lifecycle_truth(self):
        return {name: value for name, value in self.truth().items() if '/continuation/' not in name and not name.endswith('/continuation')}

    def draft(self):
        value = native_helpers.WindowsPublicationTests.draft(self)
        if getattr(self, 'delegated', False):
            value.update(schema_version=3, acceptance_delegation={
                'action': 'accept', 'delegate_actor': 'delegate-1', 'execution_mode': 'isolated-worktree',
                'scope': ['sample.txt', 'b', 'new.exe'],
                'work': {'authority_home_id': 'home-a', 'kind': 'work', 'id': 'work-a'}})
        return value

    def intent_ref(self, graph):
        chosen = graph['selections'][graph['current']['selection_ref']['id']]
        return {'authority_home_id': 'home-a', 'kind': 'intent', 'id': 'intent-a',
                'revision_ref': chosen['revision_ref'], 'acceptance_ref': chosen['acceptance_ref'],
                'selection_ref': graph['current']['selection_ref']}

    def accept_intent(self):
        if not getattr(self, 'delegated', False):
            return native_helpers.WindowsPublicationTests.accept_intent(self)
        draft = self.draft(); store = WorkspaceIntentStore(self.target, self.observed)
        # A partial draft needs the existing identity reflush before publication.
        with self.assertRaises(InjectedCrash): store.publish_draft(draft, inject_at='after-home')
        home = self.target / '.hrn/intents/intent-a'; retained = home / 'identity.json'
        os.chmod(retained, 0o444); before = physical(self.target)
        error = json.loads(self.installed(['intent', 'draft'], draft, expected=65).stdout)
        self.assertIn('read-only', error['message']); self.assertEqual(before, physical(self.target))
        os.chmod(retained, 0o666); self.installed(['intent', 'draft'], draft)
        request = {'intent_id': 'intent-a', 'revision_ref': work.record_ref(draft, 'revision_id'), 'actor': 'owner',
                   'reason': 'synthetic explicit delegation', 'request_id': 'intent-accept-a', 'observed_at': TIME}
        prepared = json.loads(self.installed(['intent', 'prepare'], request).stdout)
        acceptance = home / 'acceptances' / ('acceptance-'+sha(canonical(prepared['ticket']))+'.json')
        store = WorkspaceIntentStore(self.target, self.observed)
        with fail_native_flush_for(acceptance) as faults:
            with self.assertRaisesRegex(ContractError, 'created-file-content.*winerror=5'):
                store.apply(prepared['ticket'], confirm_token=prepared['confirm_token'])
        self.assertEqual(1, len(faults)); fixed = acceptance.read_bytes()
        self.assertEqual(prepared['ticket'], json.loads(fixed)['confirmation'])
        self.assertFalse((home/'current.json').exists())
        graph = json.loads(self.installed(['intent', 'apply', '--confirm', prepared['confirm_token']], prepared['ticket']).stdout)
        self.assertEqual([], graph['pending_acceptances']+graph['pending_selections'])
        self.assertEqual(1, len(graph['acceptances'])); self.assertEqual(fixed, acceptance.read_bytes())
        self.event('delegated-intent-preflight-and-flush-recovered', injected_faults=faults,
                   installed_retry=True, original_ticket_sha256=sha(canonical(prepared['ticket'])))
        return self.intent_ref(graph)

    def cont_prepare(self, ident):
        value = {'work_id': 'work-a', 'action': 'select', 'actor': 'owner',
                 'owner_statement': 'Synthetic explicit Owner continuation selection',
                 'reason': 'Focused native publication', 'request_id': ident,
                 'observed_at': TIME, 'choice': {'kind': 'none'}}
        return json.loads(self.installed(['continuation', 'prepare'], value).stdout)

    def cont_apply(self, packet, expected=0):
        return json.loads(self.installed(['continuation', 'apply', '--confirm', packet['confirm_token']],
                                         packet['ticket'], expected=expected).stdout)

    def read_pair(self, label):
        code = ('import sys,json;from pathlib import Path;sys.path.insert(0,sys.argv[1]);'
                'from hv2ref.work import WorkStore;from hv2ref.intent import workspace_intents;'
                't=Path(sys.argv[2]);print(json.dumps({"works":WorkStore(t)._all(),"intents":workspace_intents(t)},sort_keys=True))')
        before = physical(self.target); values = []
        for source in (self.p, self.q):
            result = subprocess.run([sys.executable, '-I', '-B', '-c', code, str(source/'src'), str(self.target)],
                                    cwd=self.target, capture_output=True, timeout=60)
            self.assertEqual(0, result.returncode, result.stdout+result.stderr)
            self.assertEqual(b'', result.stderr); values.append(json.loads(result.stdout))
            self.assertEqual(before, physical(self.target))
        self.assertEqual(values[0], values[1])
        self.event(label, reader_pair_equal=True, target_unchanged=True, graph_sha256=sha(canonical(values[0])))
        return values[0]

    def test_u1_p_to_q_readonly_and_flush_exact_recovery(self):
        self.init(); self.intent = self.accept_intent(); base = self.snapshot()
        graph = json.loads(self.installed(['work', 'publish'], self.request(base)).stdout)
        lifecycle = self.lifecycle_truth()
        first = self.cont_prepare('p-choice'); self.cont_apply(first)
        self.assertEqual(1, read_continuation(self.target, 'work-a')['usage']['normal_used'])
        self.read_pair('P-created-U1-before-update')
        truth = self.truth(); self.switch_candidate('update'); self.assert_product(self.q_candidate)
        self.assertEqual(truth, self.truth()); pair = self.read_pair('P-created-U1-read-by-Q-after-update')
        self.assertEqual({'kind': 'none'}, pair['works']['work-a']['continuation']['effective_choice'])
        second = self.cont_prepare('q-readonly-choice'); home = self.target/'.hrn/work/work-a/continuation'
        os.chmod(home/'current.json', 0o444); before = physical(self.target)
        refused = self.cont_apply(second, expected=65)
        self.assertIn('read-only', refused['message']); self.assertEqual(before, physical(self.target))
        os.chmod(home/'current.json', 0o666); self.cont_apply(second)
        self.assertEqual(2, read_continuation(self.target, 'work-a')['usage']['normal_used'])
        third = self.cont_prepare('q-flush-choice'); ticket_bytes = canonical(third)
        choice, selection = records(third['ticket']); choice_path = home/'choices'/(choice['record_id']+'.json')
        prior = (home/'current.json').read_bytes(); store = ContinuationStore(self.target, self.observed)
        with fail_native_flush_for(choice_path) as faults:
            with self.assertRaisesRegex(ContractError, 'created-file-content.*winerror=5'):
                store.apply(third['ticket'], confirm_token=third['confirm_token'])
        self.assertEqual(1, len(faults)); choice_bytes = choice_path.read_bytes()
        self.assertEqual(prior, (home/'current.json').read_bytes())
        pending = read_continuation(self.target, 'work-a')
        self.assertIsNotNone(pending['pending']); self.assertEqual(3, pending['usage']['normal_used'])
        before = physical(self.target)
        with self.assertRaisesRegex(ContractError, 'pending'):
            work.WorkStore(self.target, self.observed).publish(**self.request(base, operation='checkpoint', parent=graph['current']['selection_ref']))
        self.assertEqual(before, physical(self.target))
        with fail_native_replace_for(home/'current.json') as replaces, record_native_publication() as events:
            with self.assertRaisesRegex(ContractError, 'replace-publication.*winerror=32'):
                store.apply(third['ticket'], confirm_token=third['confirm_token'])
        self.assertEqual(1, len(replaces)); self.assertEqual(prior, (home/'current.json').read_bytes())
        assert_native_reflush_before(self, events, choice_path, home/'current.json')
        assert_native_staging_flush_before_replace(self, events, home/'current.json')
        final = self.cont_apply(third); self.assertIsNone(final['pending'])
        self.assertEqual(3, final['usage']['normal_used']); self.assertEqual(choice_bytes, choice_path.read_bytes())
        before = physical(self.target); self.assertEqual('resolved', self.cont_apply(third)['replay'])
        self.assertEqual(before, physical(self.target)); self.assertEqual(ticket_bytes, canonical(third))
        self.assertEqual(lifecycle, self.lifecycle_truth())
        self.event('U1-complete', readonly_prepublication=True, required_flush_faults=faults,
                   injected_replace_faults=replaces, exact_retry_no_extra_quota=True, truth_unchanged=True)

    def test_delegation_pq_native_writers_and_exact_recovery(self):
        self.delegated = True
        manifest, worker = self.worker_result()
        graph = work.read_work(self.target, 'work-a'); self.assertEqual('review', graph['state'])
        self.read_pair('P-created-delegated-intent-and-work')
        value = {'work_id': 'work-a', 'action': 'accept', 'actor': 'other-agent',
                 'reason': 'synthetic out of grant', 'request_id': 'outside-grant', 'observed_at': TIME,
                 'revision_ref': None, 'supersedes': None}
        before = physical(self.target)
        self.installed(['work', 'prepare'], value, expected=65); self.assertEqual(before, physical(self.target))
        value.update(actor='delegate-1', request_id='delegated-native-accept')
        prepared = json.loads(self.installed(['work', 'prepare'], value).stdout)
        ticket_bytes = canonical(prepared); original_git = physical(self.target/'.git')
        os.chmod(self.target/'sample.txt', 0o444); before = physical(self.target)
        refused = self.apply(prepared, expected=65); self.assertIn('read-only', refused['message'])
        self.assertEqual(before, physical(self.target)); self.assertEqual({}, work.read_work(self.target, 'work-a')['decisions'])
        os.chmod(self.target/'sample.txt', 0o666)
        decision_path = self.target/'.hrn/work/work-a/decisions'/('decision-'+sha(canonical(prepared['ticket']))+'.json')
        store = work.WorkStore(self.target, self.observed)
        with fail_native_flush_for(decision_path) as faults:
            with self.assertRaisesRegex(ContractError, 'created-file-content.*winerror=5'):
                store.apply(prepared['ticket'], confirm_token=prepared['confirm_token'])
        self.assertEqual(1, len(faults)); decision_bytes = decision_path.read_bytes()
        self.assertEqual(prepared['ticket'], json.loads(decision_bytes)['confirmation'])
        self.assertEqual(b'before\r\n', (self.target/'sample.txt').read_bytes())
        self.assertEqual(b'delete\n', (self.target/'b').read_bytes()); self.assertFalse((self.target/'new.exe').exists())
        self.assertEqual(original_git, physical(self.target/'.git'))
        before = physical(self.target)
        bad = copy.deepcopy(prepared['ticket']); bad['actor'] = 'other-agent'
        self.installed(['work', 'apply', '--confirm', sha(canonical(bad))[:16]], bad, expected=65)
        self.assertEqual(before, physical(self.target))
        self.assertEqual('completed', self.apply(prepared)['state'])
        self.assert_independent_worker_result(manifest); self.assertEqual(manifest['result'], self.snapshot())
        self.assertEqual(original_git, physical(self.target/'.git')); self.assertEqual(decision_bytes, decision_path.read_bytes())
        self.assertEqual(ticket_bytes, canonical(prepared))
        self.finish_delegation_compatibility()
        self.event('delegation-complete', native_cli_grant_refusal=True, readonly_prepublication=True,
                   required_flush_faults=faults, original_ticket_resumed=True, control_git_preserved=True)

    def finish_delegation_compatibility(self, recovery=None):
        # A bounded continuation can reuse the preserved accepted worker result.
        # It must verify the exact exported prefix before attaching this fixture.
        truth = self.truth(); git_before = physical(self.target/'.git')
        if recovery is None:
            self.switch_candidate('update')
        else:
            packet = canonical(recovery)
            argv = [sys.executable, '-I', '-B', str(self.p/'colvia'), '--source-checkout',
                    'update', '--profile', 'windows-2', '--target', str(self.target), '--source', str(self.q),
                    '--recover', '--apply', '--input', '-', '--confirm', sha(packet)[:16]]
            result = subprocess.run(argv, input=packet, capture_output=True, cwd=self.target, timeout=120)
            self.assertEqual(0, result.returncode, result.stdout+result.stderr)
            self.assertEqual(b'', result.stderr)
            self.event('original-update-recovery', original_plan_sha256=sha(packet), result=json.loads(result.stdout))
        self.assert_product(self.q_candidate)
        self.assertEqual(git_before, physical(self.target/'.git'))
        self.assertEqual(truth, self.truth()); self.read_pair('P-created-delegated-result-read-by-Q')
        # Publish a new delegated intent revision on Q, leaving original Work exact.
        old = self.draft(); newer = copy.deepcopy(old)
        newer.update(revision_id='draft-q', sequence=2, prior_revision_ref=work.record_ref(old, 'revision_id'))
        newer['acceptance_delegation']['work']['id'] = 'work-q'
        self.installed(['intent', 'draft'], newer)
        request = {'intent_id': 'intent-a', 'revision_ref': work.record_ref(newer, 'revision_id'),
                   'actor': 'owner', 'reason': 'synthetic Q grant', 'request_id': 'q-grant', 'observed_at': TIME}
        packet = json.loads(self.installed(['intent', 'prepare'], request).stdout)
        q_intent = json.loads(self.installed(['intent', 'apply', '--confirm', packet['confirm_token']], packet['ticket']).stdout)
        self.intent = self.intent_ref(q_intent)
        # Explicit synthetic fixture commit for Q provenance, not a product Git write.
        self.git(self.target, 'add', '.'); self.git(self.target, 'commit', '-qm', 'synthetic Q baseline')
        oid = self.git(self.target, 'rev-parse', 'HEAD'); self.git(self.target, 'branch', 'retained-q', oid)
        base = self.snapshot(); scope = ['sample.txt', 'b', 'new.exe']
        manifest_q = work.make_manifest(base, base, scope=scope, base_commit=oid, candidate_commit=oid,
            base_retention_ref='refs/heads/retained-q', candidate_retention_ref='refs/heads/retained-q')
        q_work = self.request(base, mode='isolated-worktree', manifest=manifest_q, scope=scope)
        q_work['identity']['work_id'] = 'work-q'; q_work['revision']['work_id'] = 'work-q'
        self.installed(['work', 'publish'], q_work)
        pair = self.read_pair('Q-created-delegated-intent-and-work-before-rollback')
        self.assertEqual('active', pair['works']['work-q']['state'])
        q_git = physical(self.target/'.git')
        truth = self.truth(); self.switch_candidate('rollback'); self.assert_product(self.p_candidate)
        self.assertEqual(truth, self.truth()); self.read_pair('Q-created-delegated-intent-and-work-read-by-P-after-rollback')
        self.assertEqual(q_git, physical(self.target/'.git'))
        self.assertEqual(3, read_workspace_intent_graph(self.target, 'intent-a')['drafts']['draft-q']['schema_version'])
        self.event('delegation-compatibility-complete', recovery_used=recovery is not None, control_git_preserved=True)
