"""Native no-replace backup source checks; no install or live authority changes."""
from io import BytesIO
from pathlib import Path
import hashlib,json,tempfile,unittest
from unittest.mock import patch
from colvia.backup import ImportedSnapshot,ExportBudget,supported_requirements,MAGIC
from colvia.backup_service import export_backup,backup_status
from colvia.bodies import ingest_body,body_bytes
from colvia.codec import RecordError,canonical_bytes
from colvia.graph import AuditBudget
from colvia.schemas import foundation_registry
from colvia.storage.authority import Authority

class BackupServiceTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='backup-service-');self.base=Path(self.tmp.name)
        self.authority=Authority.create(self.base/'authority',project='synthetic',instance='local',generation='one')
        self.registry=foundation_registry();self.scratch=self.base/'scratch';self.scratch.mkdir()
        self.store=self.authority.store();self.store.begin_import('body','fixture')
        self.raw=b'kept\r\n'+bytes(range(256))*4096
        self.body=ingest_body(BytesIO(self.raw),self.store,'body')
        self.store.commit_heads(operation='save',expected={'body':None},changes={'body':self.body[0]},objects=[self.body],import_id='body',validate=lambda _:None)
        self.before=self.store.root().ref;self.store.close();self.destination=self.base/'project.colvia-backup'
    def tearDown(self):self.tmp.cleanup()
    def export(self,**kw):
        return export_backup(self.authority,destination=self.destination,scratch=self.scratch,operation=kw.pop('operation','backup'),
                             graph_budget=AuditBudget(10000,10000,32*1024*1024),registry=self.registry,**kw)
    def import_snapshot(self,raw,name='import'):
        return ImportedSnapshot(self.base/(name+'.sqlite3'),BytesIO(raw),budget=ExportBudget(10000,32*1024*1024),
            graph_budget=AuditBudget(10000,10000,32*1024*1024),registry=self.registry,capabilities=supported_requirements(self.registry))
    def test_published_exact_retained_body_with_read_only_restore_and_local_receipt(self):
        value=self.export();self.assertTrue(value['published']);self.assertTrue(value['receipt_saved'])
        snapshot=self.import_snapshot(self.destination.read_bytes())
        try:
            self.assertEqual(self.before,snapshot.audit.root);self.assertEqual(self.raw,b''.join(body_bytes(self.body[0],snapshot.load)))
            self.assertFalse(snapshot.writable);self.assertEqual(snapshot.header['read_requirements'],snapshot.header['write_requirements'])
        finally:snapshot.close()
        state=backup_status(self.authority);self.assertTrue(state['same_instance']);self.assertFalse(state['different_root'])
        self.assertEqual('not_checked',state['destination_availability'])
        store=self.authority.store(readonly=True)
        try:self.assertEqual(self.before,store.root().ref)
        finally:store.close()
    def test_existing_destination_is_never_replaced_or_relabelled_verified(self):
        self.destination.write_bytes(b'prior valid backup')
        with self.assertRaisesRegex(RecordError,'backup-destination-exists'):self.export()
        self.assertEqual(b'prior valid backup',self.destination.read_bytes())
        self.assertEqual({'verified_export_recorded':False},backup_status(self.authority))
    def test_competing_publication_refuses_and_preserves_other_file(self):
        def checkpoint(phase):
            if phase=='verified':self.destination.write_bytes(b'concurrent winner')
        with self.assertRaisesRegex(RecordError,'effect-destination-occupied'):self.export(checkpoint=checkpoint)
        self.assertEqual(b'concurrent winner',self.destination.read_bytes());self.assertFalse(backup_status(self.authority)['verified_export_recorded'])
    def test_cancel_after_verification_never_publishes(self):
        stop=[False]
        def checkpoint(phase):
            if phase=='verified':stop[0]=True
        with self.assertRaisesRegex(RecordError,'export-cancelled'):self.export(checkpoint=checkpoint,cancelled=lambda:stop[0])
        self.assertFalse(self.destination.exists());self.assertFalse(backup_status(self.authority)['verified_export_recorded'])
    def test_failed_receipt_reports_successful_file_separately(self):
        def checkpoint(phase):
            if phase=='receipt':raise OSError('injected local receipt failure')
        value=self.export(checkpoint=checkpoint);self.assertTrue(value['published']);self.assertFalse(value['receipt_saved'])
        snapshot=self.import_snapshot(self.destination.read_bytes());snapshot.close()
        self.assertFalse(backup_status(self.authority)['verified_export_recorded'])
    def test_sync_failure_does_not_replace_old_backup(self):
        old=self.base/'previous.backup';old.write_bytes(b'previous retained bytes')
        with patch('colvia.platforms.darwin_effects._flush',side_effect=OSError('synthetic disk full')),self.assertRaises(OSError):self.export()
        self.assertFalse(self.destination.exists());self.assertEqual(b'previous retained bytes',old.read_bytes())
        self.assertFalse(backup_status(self.authority)['verified_export_recorded'])
    def test_changed_file_after_full_readback_refuses_publication(self):
        def checkpoint(phase):
            if phase=='verified':
                staged=next(self.base.glob('.colvia-export-*'));staged.write_bytes(b'changed')
        with self.assertRaisesRegex(RecordError,'backup-file-changed'):self.export(checkpoint=checkpoint)
        self.assertFalse(self.destination.exists())
    def test_advancing_history_does_not_invalidate_pinned_backup_or_hide_newer_data(self):
        def checkpoint(phase):
            if phase=='verified':
                store=self.authority.store()
                try:store.commit_heads(operation='later',expected={'later':None},changes={'later':self.body[0]},validate=lambda _:None)
                finally:store.close()
        self.export(checkpoint=checkpoint);self.assertTrue(backup_status(self.authority)['different_root'])
        snapshot=self.import_snapshot(self.destination.read_bytes())
        try:self.assertEqual(self.before,snapshot.audit.root)
        finally:snapshot.close()
    def test_forged_understated_requirements_refuse_even_with_recomputed_manifest(self):
        self.export();raw=self.destination.read_bytes();offset=len(MAGIC);size=int.from_bytes(raw[offset:offset+4],'big')
        header=json.loads(raw[offset+4:offset+4+size]);header['read_requirements']=['foundation-v1'];header['write_requirements']=['foundation-v1']
        pos=offset+4+size;frames=[]
        while raw[pos:pos+1]==b'O':
            count=int.from_bytes(raw[pos+1:pos+5],'big');ref=json.loads(raw[pos+5:pos+5+count]);end=pos+5+count+ref['byte_length']
            frames.append(raw[pos:end]);pos=end
        encoded=canonical_bytes(header);prefix=MAGIC+len(encoded).to_bytes(4,'big')+encoded+b''.join(frames)
        final=canonical_bytes(dict(objects=len(frames),bytes=len(prefix),sha256=hashlib.sha256(prefix).hexdigest()))
        forged=prefix+b'M'+len(final).to_bytes(4,'big')+final
        with self.assertRaisesRegex(RecordError,'import-requirements-mismatch'):self.import_snapshot(forged)
