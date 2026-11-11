"""Bounded pipe transport with harmless local peers, never a model runtime."""
import json,os,subprocess,sys,tempfile,time,unittest
from pathlib import Path
from colvia.codec import RecordError
from colvia.adapters.bounded_rpc import JsonLines
from colvia.platforms.worker_stdio import exchange

class DecoderTests(unittest.TestCase):
    def test_partial_multiple_and_blank_frames(self):
        stream=JsonLines();stream.feed(b'{"id":1,');self.assertIsNone(stream.pop())
        stream.feed(b'"result":{}}\n\n{"method":"turn/completed"}\n')
        self.assertEqual({'id':1,'result':{}},stream.pop());self.assertEqual({'method':'turn/completed'},stream.pop());stream.finish()
        with self.assertRaises(RecordError):stream.feed(b'{}\n')
    def test_duplicate_nonfinite_deep_nonobject_and_surrogate_refuse(self):
        for raw in (b'{"a":1,"a":2}\n',b'{"a":NaN}\n',b'[]\n',b'{"a":"\\ud800"}\n',
                b'{"a":'+b'['*17+b'0'+b']'*17+b'}\n'):
            with self.subTest(raw=raw[:18]):
                stream=JsonLines()
                with self.assertRaises(RecordError):stream.feed(raw)
                with self.assertRaises(RecordError):stream.pop()
    def test_size_queue_and_truncated_eof_latch(self):
        for stream,raw in ((JsonLines(limit=32),b'{"a":"'+b'x'*26),
                (JsonLines(queue_limit=1),b'{}\n{}\n')):
            with self.assertRaises(RecordError):stream.feed(raw)
            with self.assertRaises(RecordError):stream.feed(b'{}\n')
        stream=JsonLines();stream.feed(b'{')
        with self.assertRaisesRegex(RecordError,'truncated'):stream.finish()

class PipeTests(unittest.TestCase):
    def peer(self,code):
        root=Path(self.tmp.name)
        return subprocess.Popen([sys.executable,'-I','-B','-c',code],cwd=root,
            env={'PATH':os.environ.get('PATH',''),'TMPDIR':str(root)},stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    def setUp(self):self.tmp=tempfile.TemporaryDirectory(prefix='transport-');self.peers=[]
    def tearDown(self):
        for p in self.peers:
            if p.poll() is None:p.kill()
            p.wait(timeout=3)
            for stream in (p.stdin,p.stdout,p.stderr):
                if not stream.closed:stream.close()
        self.tmp.cleanup()
    def start(self,code):
        p=self.peer(code);self.peers.append(p);return p
    def test_duplex_drain_counts_stderr_and_preserves_exact_input(self):
        p=self.start('import sys; sys.stderr.write("e"*90000);sys.stderr.flush();raw=sys.stdin.buffer.read();sys.stdout.buffer.write(raw)')
        raw=b'x'*90000;out,err=exchange(p,raw,deadline=time.monotonic()+5)
        self.assertEqual(raw,out);self.assertEqual(90000,err);self.assertEqual(0,p.returncode)
    def test_output_limit_and_cancel_do_not_claim_process_closure(self):
        p=self.start('import sys,time;sys.stdout.buffer.write(b"x"*131073);sys.stdout.flush();time.sleep(3)')
        with self.assertRaisesRegex(RecordError,'output_limit'):exchange(p,b'{}',deadline=time.monotonic()+2)
        p=self.start('import time;time.sleep(3)')
        with self.assertRaisesRegex(RecordError,'cancelled'):exchange(p,b'{}',deadline=time.monotonic()+2,cancelled=lambda:True)
        self.assertIsNone(p.poll())
    def test_unresponsive_peer_has_bounded_wait(self):
        p=self.start('import time;time.sleep(3)');start=time.monotonic()
        with self.assertRaises(TimeoutError):exchange(p,b'x'*131072,deadline=start+.15)
        self.assertLess(time.monotonic()-start,1)
