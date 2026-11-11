"""Memory-pipe protocol double: no native Windows child or model invocation."""
import queue,unittest
from colvia.codec import RecordError
from colvia.platforms.windows_process import run

class Job:
    def __init__(self,api):self.api=api;self.stopped=False;self.closed=False
    def exited(self):return self.api.mode=='complete' or self.stopped
    def active(self):return 0 if self.exited() else 1
    def code(self):return 0
    def stop(self):
        if self.api.mode=='stop-fails':raise OSError('synthetic stop failure')
        self.stopped=True;self.api.eof()
    def close(self):self.closed=True;self.api.eof()

class Pipes:
    def __init__(self,mode='complete',out=b'output',err=b''):
        self.mode=mode;self.out=out;self.err=err;self.queues={};self.input=bytearray();self.created=0;self.closed=[]
    def pipe(self):
        n=len(self.queues)*2+10;self.queues[n]=queue.Queue();return n,n+1
    def start(self,*args,**kwargs):
        self.created+=1;self.job=Job(self)
        keys=list(self.queues);self.outputs=(keys[1],keys[2])
        if self.out:self.queues[self.outputs[0]].put(self.out)
        if self.err:self.queues[self.outputs[1]].put(self.err)
        if self.mode=='complete':self.eof()
        return self.job
    def eof(self):
        for h in self.outputs:self.queues[h].put(b'')
    def read_pipe(self,h,limit):return self.queues[h].get(timeout=2)
    def write_pipe(self,h,raw):self.input.extend(raw);return len(raw)
    def close(self,h):self.closed.append(h)

class WindowsProcessTests(unittest.TestCase):
    def run_with(self,api,**kwargs):return run([r'C:\tools\git.exe','status'],cwd=r'C:\project',env={},api=api,**kwargs)
    def test_exact_bytes_input_and_ownership_close(self):
        api=Pipes(out=b'raw\0output',err=b'diagnostic');result=self.run_with(api,input_bytes=b'input\0')
        self.assertEqual(b'raw\0output',result.stdout);self.assertEqual(b'diagnostic',result.stderr)
        self.assertEqual(b'input\0',api.input);self.assertTrue(api.job.closed);self.assertFalse(api.job.stopped)
        self.assertEqual(6,len(set(api.closed)));self.assertEqual(1,api.created)
    def test_combined_output_budget_failure_never_becomes_success(self):
        api=Pipes(out=b'x'*8,err=b'y'*8)
        with self.assertRaisesRegex(RecordError,'process-output-limit'):self.run_with(api,output_limit=10)
        self.assertTrue(api.job.closed);self.assertEqual(1,api.created)
    def test_deadline_closes_owned_job_and_unblocks_pipes(self):
        api=Pipes(mode='running',out=b'')
        with self.assertRaisesRegex(RecordError,'process-timeout'):self.run_with(api,seconds=.01)
        self.assertTrue(api.job.stopped);self.assertTrue(api.job.closed)
    def test_stop_failure_is_unknown_not_absent(self):
        api=Pipes(mode='stop-fails',out=b'')
        with self.assertRaisesRegex(RecordError,'closure-unknown'):self.run_with(api,seconds=.01)
        self.assertTrue(api.job.closed);self.assertEqual(1,api.created)

if __name__=='__main__':unittest.main()
