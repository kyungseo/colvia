"""Deterministic read counters for ordinary writes and independently guarded views."""
from collections import Counter
from contextlib import contextmanager
from hashlib import sha256
import unittest
from unittest.mock import patch

from colvia import connection_identity
from colvia.adapters import git
from colvia.bodies import validate_body
from colvia.codec import CHUNK_LIMIT, RecordError, encode_envelope, object_ref
from colvia.graph import ClosurePolicy, Registry, validate_closure
from colvia.storage.sqlite import SnapshotBudget, ValidationView
import test_foundation_store as store_fixture
from test_foundation_work import WorkFixture
from test_foundation_work_git import GitWorkFixture


class OrdinaryReadBudgets(WorkFixture, unittest.TestCase):
    @staticmethod
    def _read_transactions(counter):
        return sum(not call.kwargs.get('write', False) for call in counter.call_args_list)

    def test_large_workspace_acceptance_has_bounded_guarded_reads(self):
        for number in range(3000):
            folder = self.root / f'd{number % 20}'
            folder.mkdir(exist_ok=True)
            (folder / f'f{number}.txt').write_text(f'row {number}\n')
        self.start()
        (self.root / 'report.md').write_text('ordinary acceptance\n')
        review = self.submit()
        with patch.object(self.store, '_transaction_inner', wraps=self.store._transaction_inner) as tx:
            accepted = self.service.accept(operation='accept', work='report', receipt=review['receipt'], statement='complete')
        self.assertEqual('completed', accepted['state'])
        self.assertGreater(self._read_transactions(tx), 0)
        self.assertLessEqual(self._read_transactions(tx), 65)

    def test_verify_retries_when_root_advances_after_the_snapshot(self):
        expected = self.workspace.verify()
        snapshots = self.store._read_snapshot
        calls = 0

        @contextmanager
        def changed_snapshot(*args, **kwargs):
            nonlocal calls
            calls += 1
            with snapshots(*args, **kwargs) as records:
                yield records
            if calls == 2:
                self.store.commit_heads(operation='other-operation', expected={}, changes={}, validate=lambda _: None)

        topology = self.workspace.topology

        def observed_without_read_transaction():
            self.assertFalse(self.store.db.in_transaction)
            return topology()

        with patch.object(self.store, '_read_snapshot', changed_snapshot), patch.object(
                self.workspace, 'topology', side_effect=observed_without_read_transaction) as observed:
            self.assertEqual(expected, self.workspace.verify())
        self.assertEqual(2, observed.call_count)

    def test_verify_in_publication_keeps_connection_heads_in_its_cas_view(self):
        from colvia.connection import PROJECT_KEY, workspace_key
        from colvia.connection_identity import PROJECT_IDENTITY

        def validate(view):
            self.workspace.verify()
            self.assertLessEqual({PROJECT_KEY, PROJECT_IDENTITY, workspace_key(self.workspace.workspace)},
                                 set(view.reads))

        with patch.object(self.store, '_read_snapshot', side_effect=AssertionError('separate view during publication')):
            result = self.store.commit_heads(operation='verify-in-publication', expected={}, changes={}, validate=validate)
        self.assertEqual(result.ref, self.store.root().ref)

    def test_verify_retries_with_a_live_view_if_the_snapshot_budget_is_exhausted(self):
        expected = self.workspace.verify()
        with patch.object(self.store, '_read_snapshot', side_effect=SnapshotBudget) as bounded:
            self.assertEqual(expected, self.workspace.verify())
        bounded.assert_called_once_with(bounded=True)

    def test_read_only_view_keeps_its_guards_and_its_read_budget(self):
        self.start()
        (self.root / 'report.md').write_text('ordinary review\n')
        self.submit()
        with self.store.reuse_operation_reads(), patch.object(
                self.store, '_transaction_inner', wraps=self.store._transaction_inner) as tx:
            self.assertEqual('review', self.service.view('report')['state'])
        nested = self._read_transactions(tx)
        with patch.object(self.store, '_transaction_inner', wraps=self.store._transaction_inner) as tx:
            self.assertEqual('review', self.service.view('report')['state'])
        self.assertEqual(nested, self._read_transactions(tx))
        self.assertGreater(nested, 0)
        self.assertLessEqual(nested, 105)

    def test_32_mib_body_verification_has_a_read_budget(self):
        def write_body(changed=False):
            with (self.root / 'report.md').open('wb') as body:
                for number in range(32):
                    byte = number + 32 if changed and number >= 16 else number
                    body.write(bytes([byte]) * CHUNK_LIMIT)
        write_body()
        self.start()
        write_body(changed=True)
        review = self.submit()
        with patch.object(self.store, '_load', wraps=self.store._load) as loads:
            accepted = self.service.accept(operation='accept', work='report', receipt=review['receipt'], statement='complete')
        self.assertEqual('completed', accepted['state'])
        loaded = sum(call.args[0].byte_length for call in loads.call_args_list if call.args[0].kind == 'body.chunk')
        self.assertGreaterEqual(loaded, 64 * CHUNK_LIMIT)
        self.assertLessEqual(loaded, 128 * CHUNK_LIMIT)


class GitReadBudgets(GitWorkFixture, unittest.TestCase):
    def test_one_verify_keeps_git_checks_and_resolves_each_anchor_once(self):
        with patch.object(connection_identity, 'effective', wraps=connection_identity.effective) as resolve, patch.object(
                git, 'run', wraps=git.run) as processes, patch.object(
                self.store, '_transaction_inner', wraps=self.store._transaction_inner) as tx:
            self.service.workspace.verify()
        self.assertEqual(3, tx.call_count)
        identities = Counter(call.args[0] for call in resolve.call_args_list)
        self.assertTrue(identities)
        self.assertTrue(all(count == 1 for count in identities.values()), identities)
        self.assertEqual(3, processes.call_count)
        with patch.object(connection_identity, 'effective', wraps=connection_identity.effective) as resolve:
            self.service.workspace.verify()
        self.assertEqual(identities, Counter(call.args[0] for call in resolve.call_args_list))


class OperationReuseGuards(unittest.TestCase):
    def setUp(self):
        self.fixture = store_fixture.StoreTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.tearDown)
        self.store = self.fixture.store

    def test_cached_read_is_handle_local_and_revalidated_before_success(self):
        ref = self.fixture.publish('seed', 'value', 'exact')
        other = self.fixture.open(readonly=True)
        with patch.object(self.store, '_load_guarded', wraps=self.store._load_guarded) as loads:
            with self.store.reuse_operation_reads():
                self.assertEqual(self.store.load(ref), self.store.load(ref))
                self.assertEqual(1, loads.call_count)
                with patch.object(other, '_load_guarded', wraps=other._load_guarded) as other_loads:
                    self.assertEqual(other.load(ref), other.load(ref))
                self.assertEqual(2, other_loads.call_count)
            self.store.load(ref)
            self.assertEqual(2, loads.call_count)

        with self.assertRaisesRegex(RecordError, 'active-generation-changed'):
            with self.store.reuse_operation_reads():
                self.store.load(ref)
                self.fixture.active = 'generation-2'
                self.store.load(ref)
        self.fixture.active = 'generation-1'
        self.assertEqual(ref, self.store.head('value'))


    def test_nested_reuse_does_not_add_a_guard_after_a_live_publication(self):
        seeded = self.fixture.publish('seed', 'value', 'exact')
        with patch.object(self.store, '_load_guarded', wraps=self.store._load_guarded) as reads:
            with self.store.reuse_operation_reads():
                self.store.load(seeded)
                with self.store.reuse_operation_reads():
                    self.store.load(seeded)
                self.assertEqual(1, reads.call_count)
                applied = self.fixture.publish('apply', 'target', 'completed')
                self.fixture.active = 'generation-2'
        self.fixture.active = 'generation-1'
        self.assertEqual(applied, self.store.head('target'))
        self.assertIsNotNone(self.store.operation_result('apply'))

    def test_closed_store_does_not_recheck_a_discarded_scope(self):
        seeded = self.fixture.publish('seed', 'value', 'exact')
        with self.store.reuse_operation_reads():
            self.store.load(seeded)
            self.store.load(seeded)
            self.store.close()

    def test_failed_publication_does_not_share_an_incoming_body_proof(self):
        self.fixture.publish('seed', 'present', 'already selected')
        body, raw = encode_envelope('body.complete', 1,
                                    dict(size=0, sha256=sha256(b'').hexdigest(), links={'chunks': []}))
        checked = []

        def inspect_again(view):
            with self.assertRaisesRegex(RecordError, 'object-unavailable'):
                validate_body(body, view)
            checked.append(body)
            raise RecordError('second-validation-refused')

        with self.store.reuse_operation_reads():
            with self.assertRaisesRegex(RecordError, 'head-conflict'):
                self.store.commit_heads(operation='refused', expected={'present': None},
                                        changes={'present': body}, objects=[(body, raw)],
                                        validate=lambda view: validate_body(body, view))
            with self.assertRaisesRegex(RecordError, 'second-validation-refused'):
                self.store.commit_heads(operation='second', expected={'missing': None},
                                        changes={'missing': body}, validate=inspect_again)
        self.assertEqual([body], checked)
        self.assertIsNone(self.store.head('missing'))

    def test_chunk_fast_path_preserves_required_version_and_load_error_order(self):
        raw = b'synthetic optional chunk version'
        ref = object_ref('body.chunk', 2, raw)
        registry = Registry([])
        policy = ClosurePolicy({})

        def unavailable(_):
            raise RecordError('object-unavailable')

        for loader, expected in ((lambda _: raw, 'unknown-required-kind'),
                                 (unavailable, 'object-unavailable')):
            view = ValidationView(None, loader)
            with self.subTest(expected=expected):
                with self.assertRaisesRegex(RecordError, expected):
                    validate_closure([ref], view, registry, policy)
                with view.reuse_immutable_objects(), self.assertRaisesRegex(RecordError, expected):
                    validate_closure([ref], view, registry, policy)
