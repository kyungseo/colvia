"""Regression counterexamples from the bounded P1 static review."""
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from colvia.codec import Edge, RecordError, decode_envelope, encode_envelope
from colvia.storage.authority import Authority
from colvia.storage.sqlite import runtime_capabilities
TEST_CAPS=runtime_capabilities()|{'schema:test.value:1'}
from colvia.storage.sqlite import GenerationStore, _sql_error


class ReviewTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='review-')
        self.authority = Authority.create(Path(self.tmp.name)/'authority', project='p', instance='i', generation='g1',reader_capabilities=TEST_CAPS,writer_capabilities=TEST_CAPS)
        self.store = self.authority.store()
        self.other = self.authority.store()
    def tearDown(self):
        self.other.close(); self.store.close(); self.tmp.cleanup()
    def publish(self, op, key, value, *, store=None, expected=None, validate=None):
        ref, raw = encode_envelope('test.value', 1, dict(links={}, value=value))
        return (store or self.store).commit_heads(operation=op, expected={key:expected}, changes={key:ref},
            objects=[(ref,raw)], validate=validate or (lambda load: decode_envelope(ref,load(ref))))

    def test_same_instance_generation_cannot_forget_completed_operations(self):
        self.publish('done', 'a', 'kept')
        before = self.store.root().ref
        target = self.authority.prepare_empty('g2'); target.close()
        with self.assertRaisesRegex(RecordError, 'generation-state-not-preserved'):
            self.authority.activate('switch', target_generation='g2', expected_root=before,
                validate_target=lambda _:None, validate_effects=lambda _:None)
        self.assertEqual('g1', self.authority.pointer_value()['generation'])
        self.assertFalse((self.authority.root/'pending.json').exists())
        self.assertEqual(before, self.store.root().ref)


    def test_completion_receipt_survives_preserving_generation_activation(self):
        before = self.store.root().ref
        self.publish('done', 'work', 'kept')
        after = self.store.root().ref
        target = self.authority.prepare_empty('g2')
        # Fixture import of immutable logical bytes, not a production restore API.
        try:
            with target._transaction(write=True):
                from colvia.codec import ObjectRef
                for row in self.store.db.execute('SELECT * FROM objects WHERE published=1'):
                    ref=ObjectRef(row['kind'],row['version'],row['size'],row['digest'])
                    target._put(ref,bytes(row['data']),published=True)
                target.db.execute('UPDATE current_root SET digest=?',(after.sha256,))
                target.db.executemany('INSERT OR IGNORE INTO requirements VALUES(?,?)',[tuple(row) for row in self.store.db.execute('SELECT * FROM requirements')])
                target.db.executemany('INSERT INTO operations VALUES(?,?,?)',
                    [tuple(row) for row in self.store.db.execute('SELECT * FROM operations')])
        finally: target.close()
        self.authority.activate('switch',target_generation='g2',expected_root=after,
                                validate_target=lambda _:None,validate_effects=lambda _:None)
        active=self.authority.store()
        try:
            self.assertEqual((before,after),active.operation_result('done'))
            with self.assertRaisesRegex(RecordError,'operation-already-recorded'):
                self.publish('done','other','replayed',store=active)
        finally: active.close()

    def test_operation_lookup_verifies_older_lineage_without_holding_long_read(self):
        before=self.store.root().ref
        first=self.publish('first','a','A').ref
        for n in range(12): self.publish(f'later-{n}',f'b-{n}',str(n))
        self.assertEqual((before,first),self.store.operation_result('first'))

    def test_validator_dependency_read_is_cas_protected(self):
        self.publish('dependency', 'policy', 'first')
        old = self.store.head('policy')
        def validate(load):
            self.assertEqual(old, self.store.head('policy'))
            self.publish('changed', 'policy', 'second', store=self.other, expected=old)
        with self.assertRaisesRegex(RecordError, 'head-conflict'):
            self.publish('decision', 'work', 'result', validate=validate)
        self.assertIsNone(self.store.head('work'))

    def test_validator_rebases_unrelated_head_and_reads_fixed_snapshot(self):
        self.publish('dependency', 'policy', 'first')
        old = self.store.head('policy')
        def validate(load):
            self.assertEqual(old, self.store.head('policy'))
            self.publish('unrelated', 'other', 'separate', store=self.other)
            self.assertEqual(old, self.store.head('policy'))
        self.publish('decision', 'work', 'result', validate=validate)
        self.assertIsNotNone(self.store.head('other')); self.assertIsNotNone(self.store.head('work'))

    def test_validator_full_root_read_protects_full_root(self):
        def validate(load):
            self.store.root()
            self.publish('unrelated', 'other', 'separate', store=self.other)
        with self.assertRaisesRegex(RecordError, 'validation-root-conflict'):
            self.publish('decision', 'work', 'result', validate=validate)
        self.assertIsNone(self.store.head('work'))

    def test_projection_cannot_select_a_self_described_off_branch_root(self):
        before = self.store.root().ref
        actual = self.publish('operation', 'a', 'actual')
        original = decode_envelope(actual.ref, self.store.load(actual.ref))
        fake_payload = dict(original.payload)
        old = decode_envelope(before, self.store.load(before))
        fake_edges = (Edge('integrity',old.edges[0].ref), *original.edges[1:])
        fake, raw = encode_envelope('state.root', 1, fake_payload, fake_edges)
        with self.store._transaction(write=True):
            self.store._put(fake, raw, published=True)
            self.store.db.execute('UPDATE operations SET after_root=? WHERE id=?', (fake.sha256,'operation'))
        with self.assertRaisesRegex(RecordError, 'operation-index-mismatch'):
            self.store.operation_result('operation')
        self.assertEqual(before, original.edges[2].ref)

    def test_readonly_error_classification_uses_sqlite_code_not_journal_presence(self):
        journal = Path(str(self.store.path)+'-journal'); journal.write_bytes(b'not a hot journal')
        try:
            for name, code in [('SQLITE_READONLY','store-io-unavailable'),
                               ('SQLITE_READONLY_DBMOVED','store-file-replaced'),
                               ('SQLITE_READONLY_ROLLBACK','recovery-required')]:
                exc = sqlite3.OperationalError('synthetic'); exc.sqlite_errorname = name
                self.assertEqual(code, _sql_error(exc,self.store.path).code)
        finally: journal.unlink()

    def test_commit_busy_with_confirmed_rollback_is_not_unknown(self):
        # A raw read transaction deliberately holds a SHARED lock in another
        # connection; unlike normal application reads it stays open for this cell.
        blocker = sqlite3.connect(self.store.path,isolation_level=None)
        try:
            blocker.execute('BEGIN'); blocker.execute('SELECT * FROM current_root').fetchone()
            with patch('colvia.storage.sqlite.BUSY_SECONDS', .03), self.assertRaisesRegex(RecordError, '^store-busy$'):
                self.store.begin_import('blocked-commit','owner')
            blocker.execute('ROLLBACK')
            self.assertIsNone(self.store.db.execute("SELECT id FROM imports WHERE id='blocked-commit'").fetchone())
        finally: blocker.close()

if __name__ == '__main__': unittest.main()
