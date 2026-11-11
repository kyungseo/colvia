"""Source-only candidate restore, failure isolation and operation-index checks."""
from io import BytesIO
import unittest
from colvia.backup import ImportedSnapshot,ExportBudget,supported_requirements
from colvia.graph import AuditBudget
from colvia.codec import RecordError
from colvia.storage.authority import Authority
from colvia.bodies import body_bytes
from test_foundation_backup_service import BackupServiceTests

class RestoreTests(unittest.TestCase):
    setUp=BackupServiceTests.setUp
    tearDown=BackupServiceTests.tearDown
    export=BackupServiceTests.export
    def snapshot(self,*,writable=True):
        self.export()
        caps=supported_requirements(self.registry)
        return ImportedSnapshot(self.base/'incoming.sqlite3',BytesIO(self.destination.read_bytes()),
            budget=ExportBudget(10000,32*1024*1024),graph_budget=AuditBudget(10000,10000,32*1024*1024),
            registry=self.registry,capabilities=caps,writable_capabilities=caps if writable else ())
    def test_same_state_restore_preserves_history_body_and_old_inode(self):
        snapshot=self.snapshot();old=self.authority.store(readonly=True)
        inode=old.path.stat().st_ino;original_operation=old.operation_result('save')
        try:
            root=self.authority.import_candidate('restored',snapshot,operation='copy')
            self.assertEqual(self.before,root)
            self.assertEqual('one',self.authority.pointer_value()['generation'])
            result=self.authority.activate('switch',target_generation='restored',expected_root=root,
                validate_effects=lambda _:None,validate_target=lambda s:self.assertEqual(root,s.root().ref))
            self.assertEqual(root,result)
            self.assertEqual(inode,old.path.stat().st_ino)
            with self.assertRaisesRegex(RecordError,'active-generation-changed'):old.root()
            active=self.authority.store()
            try:
                self.assertEqual(original_operation,active.operation_result('save'))
                self.assertEqual(self.raw,b''.join(body_bytes(self.body[0],active.load)))
                self.assertEqual(1,active.db.execute('SELECT complete FROM restore_origin').fetchone()[0])
                active.commit_heads(operation='next',expected={'extra':None},changes={'extra':self.body[0]},objects=[],validate=lambda _:None)
                self.assertIsNotNone(active.operation_result('next'))
            finally:active.close()
        finally:old.close();snapshot.close()
    def test_cancelled_candidate_is_quarantined_and_cannot_reuse_name(self):
        snapshot=self.snapshot();cancel=[False];observed=[]
        def checkpoint(phase):
            if phase=='object-batch':
                live=self.authority.store(readonly=True)
                try:observed.append(live.root().ref)
                finally:live.close()
                cancel[0]=True
        try:
            with self.assertRaisesRegex(RecordError,'import-cancelled'):
                self.authority.import_candidate('cancelled',snapshot,operation='copy',cancelled=lambda:cancel[0],checkpoint=checkpoint)
            self.assertEqual([self.before],observed)
            self.assertEqual('one',self.authority.pointer_value()['generation'])
            with self.assertRaises(FileExistsError):self.authority.import_candidate('cancelled',snapshot,operation='again')
            self.assertFalse((self.authority.root/'pending.json').exists())
        finally:snapshot.close()
    def test_read_only_import_cannot_allocate_writable_candidate(self):
        snapshot=self.snapshot(writable=False)
        try:
            with self.assertRaisesRegex(RecordError,'import-not-writable'):
                self.authority.import_candidate('unsupported',snapshot,operation='copy')
            self.assertFalse((self.authority.root/'stores/unsupported').exists())
        finally:snapshot.close()
    def test_other_project_refuses_before_candidate_allocation(self):
        snapshot=self.snapshot()
        other=Authority.create(self.base/'other',project='other',instance='local',generation='one')
        try:
            with self.assertRaisesRegex(RecordError,'import-project-mismatch'):
                other.import_candidate('foreign',snapshot,operation='copy')
            self.assertFalse((other.root/'stores/foreign').exists())
        finally:snapshot.close()
    def test_live_changes_after_export_are_not_rolled_back_by_activation(self):
        snapshot=self.snapshot()
        try:
            self.authority.import_candidate('saved',snapshot,operation='copy')
            active=self.authority.store()
            try:
                active.commit_heads(operation='later',expected={'extra':None},changes={'extra':self.body[0]},objects=[],validate=lambda _:None)
                now=active.root().ref
            finally:active.close()
            with self.assertRaisesRegex(RecordError,'lifecycle-root-conflict'):
                self.authority.activate('switch',target_generation='saved',expected_root=self.before,
                    validate_effects=lambda _:None,validate_target=lambda _:None)
            active=self.authority.store(readonly=True)
            try:self.assertEqual(now,active.root().ref)
            finally:active.close()
            self.assertFalse((self.authority.root/'pending.json').exists())
        finally:snapshot.close()

    def test_incomplete_candidate_bytes_never_receive_complete_origin_or_root(self):
        from unittest.mock import patch
        from colvia.storage.sqlite import GenerationStore
        snapshot=self.snapshot();original=GenerationStore._put
        def lost(store,ref,raw,**kw):
            if ref.kind=='body.chunk':return
            return original(store,ref,raw,**kw)
        try:
            with patch.object(GenerationStore,'_put',lost):
                with self.assertRaisesRegex(RecordError,'object-unavailable'):
                    self.authority.import_candidate('damaged',snapshot,operation='copy')
            self.assertEqual('one',self.authority.pointer_value()['generation'])
            import sqlite3
            db=sqlite3.connect(self.authority.root/'stores/damaged/state.sqlite3')
            try:self.assertEqual(0,db.execute('SELECT complete FROM restore_origin').fetchone()[0])
            finally:db.close()
        finally:snapshot.close()
