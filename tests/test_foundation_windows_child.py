"""Owned-child protocol without launching processes or invoking Windows APIs."""
from pathlib import Path
import json,tempfile,unittest
from colvia.codec import RecordError
from colvia.platforms.windows_child import WindowsChild,WindowsGitChild
from colvia.storage.files import PosixFiles
from test_foundation_windows_observation import IdentityDouble


class Files(PosixFiles):
    def identity(self,path):
        s=Path(path).stat();return (s.st_dev,str(s.st_ino),0)

class Child:
    pid=100
    def __init__(self,api):self.api=api;self.stopped=False;self.closed=False
    def exited(self):return self.api.mode=='complete' or self.stopped
    def active(self):return 0 if self.exited() else 1
    def code(self):return 0
    def stop(self):
        if self.api.mode=='unclosed':raise OSError('synthetic stop refused')
        self.stopped=True
    def close(self):self.closed=True

class API(IdentityDouble):
    def __init__(self,mode='complete',output=b'synthetic output'):self.mode=mode;self.output=output;self.calls=0
    def private(self,h):pass
    def ok(self,value):return value
    def FlushFileBuffers(self,h):return 1
    def start(self,args,cwd,env,streams,*,created):
        self.calls+=1;created(100);streams[1].write_bytes(self.output);self.child=Child(self);return self.child

class Clock:
    def __init__(self):self.value=0
    def __call__(self):self.value+=0.1;return self.value

class WindowsChildTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='windows-child-');self.root=Path(self.tmp.name)
    def tearDown(self):self.tmp.cleanup()
    def run_child(self,api,**options):
        return WindowsChild(self.root,files=Files(),api=api,clock=Clock(),sleep=lambda _:None).run(
            [r'C:\tools\git.exe','status'],cwd=r'C:\project',env={},**options)
    def area(self):return next(p for p in self.root.iterdir() if p.is_dir())
    def test_success_keeps_exact_output_and_closure_record(self):
        api=API();result=self.run_child(api)
        self.assertEqual(b'synthetic output',result.stdout);self.assertEqual(0,result.code);self.assertTrue(api.child.closed)
        self.assertEqual(1,api.calls);self.assertEqual(0,json.loads((self.area()/'closed.json').read_text())['job_active'])
    def test_private_staged_input_is_used_without_an_extra_copy(self):
        source=self.root/'body';source.write_bytes(b'x'*1000);api=API()
        result=self.run_child(api,input_path=source)
        self.assertEqual(0,result.code);self.assertFalse((self.area()/'stdin').exists());self.assertEqual(b'x'*1000,source.read_bytes())
    def test_foreign_input_refuses_before_process_or_job_creation(self):
        api=API()
        with self.assertRaisesRegex(RecordError,'input-outside-staging'):
            self.run_child(api,input_path=self.root.parent.parent/'foreign-input')
        self.assertEqual(0,api.calls)
    def test_git_adapter_keeps_area_reference_and_durable_job_closure(self):
        api=API();port=WindowsGitChild(self.root,files=Files(),api=api,clock=Clock(),sleep=lambda _:None);events=[]
        port.run([r'C:\tools\git.exe'],cwd=r'C:\project',env={},event=lambda *row:events.append(row))
        self.assertEqual(['spawn-intent','started','exited'],[row[0] for row in events])
        self.assertEqual(1,len({row[1] for row in events}));self.assertTrue(port.closed(self.area()))
        (self.area()/'closed.json').unlink();self.assertFalse(port.closed(self.area()))
    def test_git_adapter_unknown_closure_never_becomes_closed(self):
        api=API('unclosed');port=WindowsGitChild(self.root,files=Files(),api=api,clock=Clock(),sleep=lambda _:None)
        with self.assertRaisesRegex(RecordError,'closure-unknown'):
            port.run([r'C:\tools\git.exe'],cwd=r'C:\project',env={},seconds=0.1)
        self.assertFalse(port.closed(self.area()))

    def test_deadline_stops_exact_job_but_never_claims_no_effect(self):
        api=API('running')
        with self.assertRaisesRegex(RecordError,'process-timeout'):self.run_child(api,seconds=0.1)
        self.assertTrue(api.child.stopped);self.assertTrue(api.child.closed);self.assertEqual(1,api.calls)
        self.assertEqual('unknown',json.loads((self.area()/'stopped.json').read_text())['external_effect'])
        self.assertFalse((self.area()/'closed.json').exists())
    def test_output_overflow_preserves_failure_and_does_not_retry(self):
        api=API('running',b'x'*20)
        with self.assertRaisesRegex(RecordError,'process-output-limit'):self.run_child(api,limit=10)
        self.assertEqual(b'x'*20,(self.area()/'stdout').read_bytes());self.assertTrue(api.child.stopped);self.assertEqual(1,api.calls)
    def test_failed_stop_leaves_unknown_and_closes_exact_owned_handle(self):
        api=API('unclosed')
        with self.assertRaisesRegex(RecordError,'closure-unknown'):self.run_child(api,seconds=0.1)
        self.assertEqual('unproven',json.loads((self.area()/'unknown.json').read_text())['closure'])
        self.assertTrue(api.child.closed);self.assertEqual(1,api.calls)

if __name__=='__main__':unittest.main()
