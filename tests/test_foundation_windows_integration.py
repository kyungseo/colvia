"""Shared integration contract with explicit native-effect doubles."""
import unittest
from colvia.codec import RecordError
from colvia.platforms.windows_connect import WindowsConnect,WindowsDetach,WindowsRebind
import test_foundation_windows_effects as fixture

class WindowsIntegrationTests(unittest.TestCase):
    setUp=fixture.WindowsEffectsTests.setUp
    tearDown=fixture.WindowsEffectsTests.tearDown
    def effects(self,root,authority):return self.port
    def test_only_explicit_rebind_can_replace_the_existing_locator(self):
        (self.root/'.colvia-link.json').write_bytes(b'old locator')
        changes=[dict(role='locator',root='project',path='.colvia-link.json',before=b'old locator',after=b'new locator',mode='100644')]
        connect=WindowsConnect(self.authority,dict(project=self.root),files=self.files,effects=self.effects)
        with self.assertRaisesRegex(RecordError,'locator-already-present'):connect.preview(changes)
        rebind=WindowsRebind(self.authority,dict(project=self.root),files=self.files,effects=self.effects)
        with rebind.exclusion():
            m=rebind.prepare('rebind',changes);rebind.apply(m,0,before_effect=lambda:None,event=lambda _:None)
            self.assertEqual('post',rebind.state(m,0))
        self.assertEqual(b'new locator',(self.root/'.colvia-link.json').read_bytes())
        self.assertEqual(b'old locator',(self.authority/'effects/rebind-0/000000.original').read_bytes())

    def test_connect_then_detach_preserves_owned_originals(self):
        (self.root/'AGENTS.md').write_bytes(b'existing rules\n')
        changes=[dict(role='entry',root='project',path='AGENTS.md',before=b'existing rules\n',after=b'existing rules\nColvia\n',mode='100644'),
                 dict(role='locator',root='project',path='.colvia-link.json',before=None,after=b'locator',mode='100644')]
        connect=WindowsConnect(self.authority,dict(project=self.root),files=self.files,effects=self.effects)
        with connect.exclusion():
            m=connect.prepare('connect',changes)
            for i in range(2):connect.apply(m,i,before_effect=lambda:None,event=lambda _:None)
            self.assertEqual(['post','post'],[connect.state(m,i) for i in range(2)])
        detach=WindowsDetach(self.authority,dict(project=self.root),files=self.files,effects=self.effects)
        removal=[dict(role=c['role'],root=c['root'],path=c['path'],before=c['after'],after=c['before']) for c in changes]
        with detach.exclusion():
            m=detach.prepare('detach',removal)
            for i in range(2):detach.apply(m,i,before_effect=lambda:None,event=lambda _:None)
            self.assertEqual(['post','post'],[detach.state(m,i) for i in range(2)])
        self.assertEqual(b'existing rules\n',(self.root/'AGENTS.md').read_bytes());self.assertFalse((self.root/'.colvia-link.json').exists())
        self.assertEqual(b'existing rules\nColvia\n',(self.authority/'effects/detach-0/000000.original').read_bytes())

if __name__=='__main__':unittest.main()
