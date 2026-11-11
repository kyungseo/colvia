"""Isolated SQLite store fixtures, all beneath the runner's durable TMPDIR."""
from pathlib import Path
import sqlite3
import tempfile
import unittest

from colvia.codec import Edge, RecordError, decode_envelope, encode_envelope, object_ref
from colvia.storage.sqlite import GenerationStore, runtime_capabilities


class StoreTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='store-')
        self.path=Path(self.tmp.name)/'state.sqlite3'
        self.active='generation-1'
        def guard():
            if self.active!='generation-1': raise RecordError('active-generation-changed')
        self.guard=guard
        self.store=GenerationStore.create(self.path,project='project-1',instance='instance-1',generation='generation-1',active_check=guard,reader_capabilities=runtime_capabilities()|{'schema:test.value:1','schema:test.result:1'},writer_capabilities=runtime_capabilities()|{'schema:test.value:1','schema:test.result:1'})
        self.handles=[self.store]
    def tearDown(self):
        for handle in self.handles: handle.close()
        self.tmp.cleanup()
    def open(self,readonly=False):
        handle=GenerationStore(self.path,project='project-1',instance='instance-1',generation='generation-1',readonly=readonly,active_check=self.guard,reader_capabilities=runtime_capabilities()|{'schema:test.value:1','schema:test.result:1'},writer_capabilities=runtime_capabilities()|{'schema:test.value:1','schema:test.result:1'})
        self.handles.append(handle); return handle
    def value(self, label): return encode_envelope('test.value',1,dict(links={},label=label))
    def publish(self,op,key,label,expected=None,store=None):
        ref,raw=self.value(label)
        (store or self.store).commit_heads(operation=op,expected={key:expected},changes={key:ref},objects=[(ref,raw)],
                                          validate=lambda load:decode_envelope(ref,load(ref)))
        return ref

    def test_durability_settings_and_selected_heads(self):
        self.assertEqual(0,self.store.root().sequence)
        ref=self.publish('op-1','work-a','draft')
        self.assertEqual(ref,self.open(readonly=True).head('work-a'))
        self.assertIsNone(self.store.head('other'))
        self.assertEqual(3,self.store.db.execute('PRAGMA synchronous').fetchone()[0])
        self.assertEqual('delete',self.store.db.execute('PRAGMA journal_mode').fetchone()[0])

    def test_unrelated_updates_survive_but_same_head_cas_refuses(self):
        second=self.open()
        a=self.publish('op-a','a','A')
        b=self.publish('op-b','b','B',store=second)
        self.assertEqual(a,second.head('a')); self.assertEqual(b,self.store.head('b'))
        before=self.store.root()
        with self.assertRaisesRegex(RecordError,'head-conflict'): self.publish('op-bad','a','lost',store=second)
        self.assertEqual(before,self.store.root())
        replacement=self.publish('op-c','a','C',expected=a)
        self.assertEqual(replacement,second.head('a')); self.assertEqual(b,second.head('b'))

    def test_validator_failure_is_atomic_and_replay_explicit(self):
        ref,raw=self.value('rejected'); before=self.store.root()
        def refuse(load): raise RecordError('semantic-refusal')
        with self.assertRaisesRegex(RecordError,'semantic-refusal'):
            self.store.commit_heads(operation='refuse',expected={'x':None},changes={'x':ref},objects=[(ref,raw)],validate=refuse)
        self.assertEqual(before,self.store.root())
        with self.assertRaisesRegex(RecordError,'object-unavailable'): self.store.load(ref)
        self.publish('once','x','accepted')
        with self.assertRaisesRegex(RecordError,'operation-already-recorded'): self.publish('once','y','duplicate')
        self.assertIsNone(self.store.head('y'))

    def test_operation_projection_cannot_hide_a_completed_operation(self):
        before=self.store.root().ref
        self.publish('completed','a','A')
        after=self.store.root().ref
        self.assertEqual((before,after),self.store.operation_result('completed'))
        self.store.db.execute("DELETE FROM operations WHERE id='completed'")
        with self.assertRaisesRegex(RecordError,'operation-index-unavailable'):
            self.store.operation_result('completed')
        with self.assertRaisesRegex(RecordError,'operation-already-recorded'):
            self.publish('completed','b','B')
        self.assertIsNone(self.store.head('b'))

    def test_staging_not_visible_and_claims_are_many_to_many(self):
        raw=b'synthetic body'; chunk=object_ref('body.chunk',1,raw)
        for i in ('import-1','import-2'):
            self.store.begin_import(i,'owner')
            self.store.stage(i,[(chunk,raw)])
        self.assertEqual(2,self.store.db.execute('SELECT count(*) FROM claims').fetchone()[0])
        with self.assertRaisesRegex(RecordError,'object-unpublished'): self.store.load(chunk)
        ref,data=encode_envelope('test.result',1,dict(links={'body':[0]}),(Edge('integrity',chunk),))
        self.store.commit_heads(operation='body-op',expected={'x':None},changes={'x':ref},objects=[(ref,data)],import_id='import-1',validate=lambda load:self.assertEqual(raw,load(chunk)))
        self.assertEqual(raw,self.open(readonly=True).load(chunk))
        self.assertEqual(1,self.store.db.execute('SELECT count(*) FROM claims').fetchone()[0])
        with self.assertRaisesRegex(RecordError,'import-not-active'): self.store.stage('import-1',[(chunk,raw)])

    def test_missing_dependency_and_unowned_staging_cannot_publish(self):
        chunk=object_ref('body.chunk',1,b'x')
        self.store.begin_import('import-1','owner'); self.store.stage('import-1',[(chunk,b'x')])
        ref,raw=encode_envelope('test.result',1,dict(links={'body':[0]}),(Edge('integrity',chunk),))
        with self.assertRaisesRegex(RecordError,'object-unpublished'):
            self.store.commit_heads(operation='bad',expected={'x':None},changes={'x':ref},objects=[(ref,raw)],validate=lambda _:None)
        self.assertIsNone(self.store.head('x'))
        with self.assertRaisesRegex(RecordError,'object-unavailable'): self.store.load(ref)

    def test_published_objects_and_generation_identity_are_immutable(self):
        ref=self.publish('op-1','x','kept')
        for query,args in [('DELETE FROM objects WHERE digest=?',(ref.sha256,)),
                           ('UPDATE objects SET data=? WHERE digest=?',(b'bad',ref.sha256)),
                           ("UPDATE generation SET generation='other'",())]:
            with self.assertRaises(sqlite3.IntegrityError): self.store.db.execute(query,args)
        self.assertEqual(ref,self.store.head('x'))

    def test_fence_active_pointer_and_replaced_file_refuse(self):
        self.active='generation-2'
        with self.assertRaisesRegex(RecordError,'active-generation-changed'): self.store.root()
        self.active='generation-1'
        self.store.db.execute("UPDATE generation SET fence='activation-1'")
        with self.assertRaisesRegex(RecordError,'generation-retired'): self.store.root()
        with self.assertRaises(sqlite3.IntegrityError): self.store.db.execute('UPDATE generation SET fence=NULL')

    def test_readonly_and_schema_mismatch_refuse(self):
        reader=self.open(readonly=True)
        with self.assertRaisesRegex(RecordError,'store-readonly'): reader.begin_import('x','owner')
        self.store.db.execute('DROP TRIGGER published_no_delete')
        with self.assertRaisesRegex(RecordError,'store-schema-mismatch'): self.open()

    def test_confirmed_refusal_type_never_claims_unknown_outcome_is_safe(self):
        from colvia.codec import PublicationRefused
        before=self.store.root()
        with self.assertRaises(PublicationRefused):
            with self.store._transaction(write=True):
                self.store.db.execute("INSERT INTO imports VALUES('rollback-test','test','active')")
                raise RecordError('synthetic-refusal')
        self.assertIsNone(self.store.db.execute("SELECT 1 FROM imports WHERE id='rollback-test'").fetchone());self.assertEqual(before,self.store.root())
        with self.assertRaises(RecordError) as caught:
            with self.store._transaction(write=True):raise RecordError('store-outcome-unknown')
        self.assertNotIsInstance(caught.exception,PublicationRefused)


if __name__=='__main__': unittest.main()
