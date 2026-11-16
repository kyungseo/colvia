"""Per-user registry protocol double; no OS registration, consent or toast."""
import copy,unittest
from colvia.codec import RecordError
from colvia.platforms.windows_notices import WindowsNotices
from test_foundation_installation import InstallationTests

class RegistryDouble:
    def __init__(self):self.values={};self.fail=False;self.writes=0
    def read(self,key):return copy.deepcopy(self.values.get(key))
    def write(self,key,value):
        self.writes+=1
        if value is None:
            self.values.pop(key,None)
            parent=key.rsplit('\\',1)[0]
            if parent in self.values:self.values[parent]['children']=[]
        else:
            old=self.values.get(key,dict(children=[]));self.values[key]=dict(children=old['children'],values=copy.deepcopy(value))
            if key.endswith('\\LocalServer32'):
                self.values[key.rsplit('\\',1)[0]]['children']=['LocalServer32']
                if self.fail:self.fail=False;raise OSError('synthetic registry interruption')

class WindowsNoticeTests(unittest.TestCase):
    setUp=InstallationTests.setUp
    tearDown=InstallationTests.tearDown
    archive=InstallationTests.archive
    slot=InstallationTests.slot
    install=InstallationTests.install
    def port(self):
        self.install();self.registry=RegistryDouble();self.notices=WindowsNotices(self.home,registry=self.registry);return self.notices
    def test_orphan_registration_is_inspectable_but_not_adopted_or_deleted(self):
        port=self.port();self.registry.values[port.keys[0]]=dict(children=[],values={'DisplayName':['old installation',1]})
        before=copy.deepcopy(self.registry.values);writes=self.registry.writes
        result=port.inspect();self.assertEqual('ownership-unconfirmed',result['state'])
        self.assertEqual(writes,self.registry.writes);self.assertEqual(before,self.registry.values)
        self.assertFalse(result['automatic_cleanup'])
        with self.assertRaisesRegex(RecordError,'foreign'):port.change(enable=True)
    def test_enable_retains_callback_binary_and_exact_identity(self):
        port=self.port();self.assertEqual('enabled',port.change(enable=True)['state'])
        target=port.current();path=port.executable(target)
        self.assertEqual(self.content['bin/colvia'],path.read_bytes());self.assertEqual(port.app,port.identity(path)['app'])
        before=self.registry.writes;self.assertFalse(port.change(enable=True)['changed']);self.assertEqual(before,self.registry.writes)
        command=port.state()[2]['values'][''][0];self.assertIn('notice-activate',command);self.assertIn('--management-root',command)
    def test_interruption_keeps_journal_and_only_explicit_resume_continues(self):
        port=self.port();self.registry.fail=True
        with self.assertRaisesRegex(OSError,'synthetic registry'):port.change(enable=True)
        self.assertTrue((self.home.root/'notice-registration.pending').exists());writes=self.registry.writes
        with self.assertRaisesRegex(RecordError,'pending'):port.change(enable=True)
        self.assertEqual(writes,self.registry.writes);self.assertEqual('enabled',port.resume()['state'])
        self.assertFalse((self.home.root/'notice-registration.pending').exists());self.assertIsNotNone(port.current())
    def test_foreign_value_during_partial_transition_is_preserved(self):
        port=self.port();self.registry.fail=True
        with self.assertRaises(OSError):port.change(enable=True)
        self.registry.values[port.keys[2]]['values']['']=['foreign command',1];writes=self.registry.writes
        with self.assertRaisesRegex(RecordError,'foreign'):port.resume()
        self.assertEqual(writes,self.registry.writes);self.assertEqual(['foreign command',1],self.registry.values[port.keys[2]]['values'][''])
    def test_disable_removes_only_owned_keys_retains_evidence_binary(self):
        port=self.port();port.change(enable=True);path=port.executable(port.current())
        self.assertEqual('disabled',port.change(enable=False)['state']);self.assertIsNone(port.current());self.assertTrue(path.exists())
        self.assertEqual([None,None,None],port.state());self.assertEqual(2,len(list((self.home.root/'operations').glob('notice-*'))))
    def test_uninstall_disable_is_bound_to_its_operation_and_preserves_foreign_keys(self):
        port=self.port()
        port.change(enable=True)
        target=port.current()
        self.registry.values['foreign-key']=dict(children=[],values={'foreign':['keep',1]})
        with self.home.files.exclusion(self.home.root/'management.lock'):
            port.disable_for_uninstall('remove-test',target)
            before=self.registry.writes
            port.disable_for_uninstall('remove-test',target)
            self.assertEqual(before,self.registry.writes)
        self.assertIsNone(port.current())
        self.assertEqual(['keep',1],self.registry.values['foreign-key']['values']['foreign'])

    def test_changed_receiver_or_foreign_source_never_opens_identity(self):
        port=self.port();port.change(enable=True);path=port.executable(port.current())
        with self.assertRaisesRegex(RecordError,'source-mismatch'):port.identity(self.base/'foreign.exe')
        path.write_bytes(b'changed')
        with self.assertRaisesRegex(RecordError,'file-changed'):port.identity(path)

    def test_emission_uses_fixed_script_and_unknown_exit_never_retries(self):
        from types import SimpleNamespace
        port=self.port();port.change(enable=True);calls=[]
        def runner(args,**kwargs):calls.append((args,kwargs));return SimpleNamespace(code=1)
        self.assertEqual('unknown',port.emit('a'*32,runner=runner,system_directory=self.base/'system'))
        self.assertEqual(1,len(calls));self.assertIn('-NoProfile',calls[0][0]);self.assertIn('b:'+'a'*32,calls[0][0][-1])
        with self.assertRaisesRegex(RecordError,'event-id-invalid'):port.emit("'; bad",runner=runner,system_directory=self.base/'system')
        self.assertEqual(1,len(calls));self.assertFalse(port.check(port.receiver_identity)['os_consent_verified'])

if __name__=='__main__':unittest.main()

