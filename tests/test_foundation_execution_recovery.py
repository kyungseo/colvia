"""Private recovery preservation with native files and synthetic causal evidence."""
import sys,unittest
from unittest.mock import patch
from colvia.codec import RecordError
from colvia.platforms.darwin_execution_recovery import DarwinExecutionRecovery
import test_foundation_execution_inputs as inputs
from test_foundation_execution_store import JournalFixture
from test_foundation_execution_history import Chain

@unittest.skipUnless(sys.platform=='darwin','native recovery')
class RecoveryTests(JournalFixture,unittest.TestCase):
    native=inputs.InputTests.native
    def ready(self):
        effects,native,grant,owner,history=self.native()
        chain=Chain(self.contract).launch().successful(1);self.publish(chain)
        history=self.journal.read('run')[-1]
        recovery=DarwinExecutionRecovery(self.journal,native.observer)
        return effects,native,grant,history,recovery
    def record_ready(self,metadata):
        self.journal.append(operation='recovery-ready',run='run',kind='recovery-ready',value=metadata)
        return self.journal.read('run')[-1]
    def test_private_copy_bound_to_grant_and_original(self):
        effects,native,grant,history,recovery=self.ready()
        with effects.exclusion(create=False):
            self.assertEqual('not_required',recovery.inspect(grant,history))
            metadata=recovery.save_original(grant,history)
            self.assertEqual('orphan_candidate',recovery.inspect(grant,history))
            current=self.record_ready(metadata);self.assertEqual('present',recovery.inspect(grant,current))
            path=effects.authority/'effects'/recovery.name(grant)/'original.bin'
            self.assertEqual(self.raw,path.read_bytes());self.assertEqual(0,path.stat().st_mode&0o077)
            (self.root/'output.md').write_bytes(b'changed after saving')
            self.assertEqual('present',recovery.inspect(grant,current))
    def test_changed_document_refuses_before_copy(self):
        effects,native,grant,history,recovery=self.ready();(self.root/'output.md').write_bytes(b'changed')
        with effects.exclusion(create=False):
            with self.assertRaisesRegex(RecordError,'document-drift'):recovery.save_original(grant,history)
            self.assertEqual('not_required',recovery.inspect(grant,history))
    def test_partial_manifest_failure_keeps_original_and_cannot_retry(self):
        effects,native,grant,history,recovery=self.ready()
        import colvia.platforms.darwin_execution_recovery as module
        original=module.publish_private
        def fail_manifest(directory,name,raw):
            if name=='manifest.json':raise OSError('synthetic sync failure')
            return original(directory,name,raw)
        with effects.exclusion(create=False):
            with patch.object(module,'publish_private',side_effect=fail_manifest),self.assertRaises(OSError):recovery.save_original(grant,history)
            path=effects.authority/'effects'/recovery.name(grant)/'original.bin'
            self.assertEqual(self.raw,path.read_bytes());self.assertEqual('orphan_candidate',recovery.inspect(grant,history))
            with self.assertRaisesRegex(RecordError,'staging-already-exists'):recovery.save_original(grant,history)
    def test_missing_or_corrupt_copy_does_not_rewrite_execution_history(self):
        effects,native,grant,history,recovery=self.ready()
        with effects.exclusion(create=False):
            current=self.record_ready(recovery.save_original(grant,history));before=self.store.root().ref
            path=effects.authority/'effects'/recovery.name(grant)/'original.bin';path.write_bytes(b'corrupt')
            self.assertEqual('mismatch',recovery.inspect(grant,current));path.unlink()
            self.assertEqual('mismatch',recovery.inspect(grant,current));self.assertEqual(before,self.store.root().ref)
