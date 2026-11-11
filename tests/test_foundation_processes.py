from pathlib import Path
import json
import subprocess
import sys
import tempfile
import time
import unittest
from colvia.storage.authority import Authority
from colvia.storage.sqlite import runtime_capabilities
TEST_CAPS=runtime_capabilities()|{'schema:test.value:1'}


class ProcessTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='processes-'); self.root=Path(self.tmp.name)
        self.authority=Authority.create(self.root/'authority',project='p',instance='i',generation='g1',reader_capabilities=TEST_CAPS,writer_capabilities=TEST_CAPS)
        self.children=[]
    def tearDown(self):
        for p in self.children:
            if p.poll() is None: p.kill()
            p.communicate()
        self.tmp.cleanup()
    def start(self,mode,name,key='work'):
        p=subprocess.Popen([sys.executable,'-I','-B',str(Path(__file__).with_name('foundation_process_helper.py')),
                            str(self.root),mode,name,key],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        self.children.append(p); return p
    def ready(self,*names):
        deadline=time.monotonic()+10
        while not all((self.root/(name+'.ready')).exists() for name in names):
            self.assertTrue(all(p.poll() is None for p in self.children),'child exited before barrier')
            self.assertLess(time.monotonic(),deadline,'barrier timeout'); time.sleep(.01)
    def result(self,p):
        out,err=p.communicate(timeout=10); self.assertEqual(0,p.returncode,err)
        return json.loads(out)

    def test_two_process_unrelated_heads_preserve_both(self):
        a=self.start('cas','operation-a','a'); b=self.start('cas','operation-b','b'); self.ready('operation-a','operation-b')
        (self.root/'go').write_text('go')
        self.assertEqual(['committed','committed'],[self.result(p)['status'] for p in (a,b)])
        store=self.authority.store(readonly=True)
        try:
            self.assertIsNotNone(store.head('a')); self.assertIsNotNone(store.head('b'))
            self.assertEqual(2,store.root().sequence)
        finally: store.close()

    def test_two_process_same_head_one_refuses_without_lost_update(self):
        a=self.start('cas','operation-a'); b=self.start('cas','operation-b'); self.ready('operation-a','operation-b')
        (self.root/'go').write_text('go')
        results=[self.result(p) for p in (a,b)]
        self.assertEqual(['committed','refused'],sorted(r['status'] for r in results))
        self.assertEqual(['head-conflict'],[r['code'] for r in results if r['status']=='refused'])
        store=self.authority.store(readonly=True)
        try: self.assertEqual(1,store.root().sequence)
        finally: store.close()

    def test_open_peer_cannot_read_retired_generation(self):
        peer=self.start('hold','peer'); self.ready('peer')
        candidate=self.authority.prepare_empty('g2'); candidate.close()
        store=self.authority.store(readonly=True)
        try: root=store.root().ref
        finally: store.close()
        self.authority.activate('activate',target_generation='g2',expected_root=root,
                                validate_effects=lambda _:None,validate_target=lambda _:None)
        (self.root/'go').write_text('go')
        self.assertEqual({'status':'refused','code':'active-generation-changed'},self.result(peer))


if __name__=='__main__': unittest.main()
