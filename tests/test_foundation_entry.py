import unittest
from dataclasses import replace
from colvia.codec import RecordError
from colvia.entry import RuntimeBinding,AccessEvidence,entry_check

class EntryTests(unittest.TestCase):
    def setUp(self):
        self.binding=RuntimeBinding('synthetic-release','/synthetic/runtime/python','a'*64,frozenset({'ordinary'}))
        self.access=AccessEvidence(True,True,True,True,'synthetic-host-context')
    def test_cli_and_app_share_verified_binding_without_path_fallback(self):
        for context in ('cli-primary','desktop-sibling','desktop-nested'):
            result=entry_check(self.binding,verify_binding=lambda _:True,access=replace(self.access,context=context),required=frozenset({'ordinary'}),write=True)
            self.assertTrue(result['ready']);self.assertEqual(self.binding.release,result['release'])
        with self.assertRaisesRegex(RecordError,'managed-runtime-binding-unverified'):
            entry_check(self.binding,verify_binding=lambda _:False,access=self.access,required=frozenset(),write=True)
    def test_read_and_write_permissions_are_separate_and_short(self):
        denied=replace(self.access,authority_writable=False)
        self.assertTrue(entry_check(self.binding,verify_binding=lambda _:True,access=denied,required=frozenset(),write=False)['ready'])
        result=entry_check(self.binding,verify_binding=lambda _:True,access=denied,required=frozenset(),write=True)
        self.assertEqual('authority-access',result['reason']);self.assertNotIn('full access',result['message'])
    def test_missing_capability_never_selects_another_python(self):
        with self.assertRaisesRegex(RecordError,'runtime-capability-unavailable'):
            entry_check(self.binding,verify_binding=lambda _:True,access=self.access,required=frozenset({'future'}),write=True)

if __name__=='__main__':unittest.main()
