"""Native file/resource/whole-project checks; no model or worker launch."""
import hashlib,sys,unittest
from colvia.codec import RecordError
from colvia.platforms.darwin_effects import DarwinEffects
from colvia.platforms.darwin_execution import DarwinExecutionObservation
from colvia.platforms.darwin_execution_inputs import DarwinExecutionInputs,resource_digest
from test_foundation_execution_store import JournalFixture

@unittest.skipUnless(sys.platform=='darwin','native input observer')
class InputTests(JournalFixture,unittest.TestCase):
    def native(self,resource_values=None):
        authority=self.root.parent/'effects';authority.mkdir(mode=0o700)
        effects=DarwinEffects(self.root,authority)
        observer=DarwinExecutionObservation(self.journal,effects)
        resources={};runtime=self.root.parent/'runtime';runtime.mkdir()
        for name in self.contract['scope']['resources']:
            path=runtime/name;path.write_bytes((resource_values or {}).get(name,b'synthetic runtime resource'))
            resources[name]=path;self.contract['scope']['resources'][name]=resource_digest(path)
        with effects.exclusion():
            for item in self.contract['scope']['documents'].values():item['original_identity']=observer.document(item['path'])
        self.launch();_,grant,_,owner,history=self.journal.read('run')
        native=DarwinExecutionInputs(self.journal,observer,resources)
        return effects,native,grant,owner,history
    def test_exact_resources_and_all_files_current(self):
        effects,native,grant,owner,history=self.native()
        with effects.exclusion(create=False):
            native.assert_held(grant,owner);native.preflight(grant,history)
            import time
            native.startup(grant,history,time.monotonic()+5)
            self.assertEqual({'Output':self.raw,'Reference':self.raw},native.retained(grant))
            with self.assertRaisesRegex(RecordError,'recovery_unavailable'):native.save_original(grant,history)
    def test_outside_scope_change_refuses_even_with_unchanged_named_inputs(self):
        effects,native,grant,owner,history=self.native();(self.root/'source.csv').write_bytes(b'outside change')
        with effects.exclusion(create=False),self.assertRaisesRegex(RecordError,'outside-output-project-drift'):
            native.preflight(grant,history)
    def test_output_edit_and_same_bytes_new_inode_refuse(self):
        effects,native,grant,owner,history=self.native();path=self.root/'output.md'
        old=path.with_suffix('.old');path.rename(old);path.write_bytes(self.raw);old.unlink()
        with effects.exclusion(create=False),self.assertRaisesRegex(RecordError,'document-drift'):native.preflight(grant,history)
    def test_resource_edit_and_resource_symlink_refuse(self):
        effects,native,grant,owner,history=self.native();path=native.resources['worker_digest']
        path.write_bytes(b'changed worker')
        with effects.exclusion(create=False),self.assertRaisesRegex(RecordError,'resource-drift'):native.preflight(grant,history)
        path.unlink();path.symlink_to(native.resources['parser_digest'])
        with effects.exclusion(create=False),self.assertRaises(OSError):native.preflight(grant,history)
    def test_missing_resource_never_falls_back_to_path(self):
        effects,native,grant,owner,history=self.native();native.resources.pop('python_digest')
        with effects.exclusion(create=False),self.assertRaisesRegex(RecordError,'resource-set'):native.preflight(grant,history)
