"""Real local pipes, synthetic process only: no model or OS sandbox qualification."""
import json,subprocess,sys,time,unittest
from colvia.codec import RecordError
from colvia.platforms.runtime_channel import RuntimeChannel

class RuntimeChannelTests(unittest.TestCase):
    def process(self,body):
        p=subprocess.Popen([sys.executable,'-I','-B','-c',body],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        def close():
            if p.poll() is None:p.terminate()
            try:p.wait(timeout=3)
            except subprocess.TimeoutExpired:p.kill();p.wait(timeout=3)
            for s in (p.stdin,p.stdout,p.stderr):
                if not s.closed:s.close()
        self.addCleanup(close);return p
    def channel(self,body):
        p=self.process(body);c=RuntimeChannel(p,deadline=time.monotonic()+5);self.addCleanup(c.close);return c
    def test_roundtrip_preserves_split_frames_and_no_process_ownership(self):
        c=self.channel("import sys,json; r=json.loads(sys.stdin.buffer.readline()); raw=json.dumps({'id':r['id'],'result':{}}).encode()+b'\\n'; sys.stdout.buffer.write(raw[:3]);sys.stdout.buffer.flush();sys.stdout.buffer.write(raw[3:]);sys.stdout.buffer.flush()")
        raw=b'{"id":1}\n';self.assertEqual(len(raw),c.write(raw))
        self.assertEqual({'id':1,'result':{}},c.read(time.monotonic()+3));c.process.wait(timeout=3)
        self.assertEqual(0,c.process.returncode);self.assertEqual(0,c.diagnostic_bytes)
    def test_stderr_refuses_without_retaining_diagnostic_text(self):
        c=self.channel("import sys;sys.stderr.write('synthetic private diagnostic');sys.stderr.flush()")
        with self.assertRaisesRegex(RecordError,'protocol_diagnostic'):c.read(time.monotonic()+3)
        self.assertGreater(c.diagnostic_bytes,0);self.assertTrue(c.failed)
        self.assertFalse(hasattr(c,'stderr'));self.assertFalse(hasattr(c,'diagnostic_text'))
    def test_truncated_or_duplicate_json_latches(self):
        for output in ('{"id":1}', '{"id":1,"id":2}\n'):
            with self.subTest(output=output):
                c=self.channel('import sys;sys.stdout.write('+repr(output)+');sys.stdout.flush()')
                with self.assertRaises(RecordError):c.read(time.monotonic()+3)
                with self.assertRaisesRegex(RecordError,'protocol_refused'):c.write(b'{}\n')
    def test_empty_eof_is_not_a_completion(self):
        c=self.channel('pass')
        with self.assertRaisesRegex(RecordError,'protocol_eof'):c.read(time.monotonic()+3)
    def test_read_deadline_does_not_terminate_process_or_extend_grant(self):
        c=self.channel('import time;time.sleep(3)');original=c.deadline
        with self.assertRaisesRegex(RecordError,'deadline'):c.read(time.monotonic()+.03)
        self.assertIsNone(c.process.poll());self.assertEqual(original,c.deadline);self.assertTrue(c.failed)
