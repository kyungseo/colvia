"""Actual harmless child/group observations, not a model or daemon-proof claim."""
import os,select,signal,subprocess,sys,tempfile,time,unittest
from pathlib import Path
from unittest.mock import patch
from colvia.codec import RecordError
from colvia.platforms.darwin_processes import DarwinProcesses

@unittest.skipUnless(sys.platform=='darwin','qualified Darwin process port')
class ProcessPortTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='execution-process-');self.port=DarwinProcesses();self.children=[]
    def tearDown(self):
        for child in self.children:
            try:os.killpg(child.pid,signal.SIGKILL)
            except ProcessLookupError:pass
            child.communicate(timeout=5)
        self.tmp.cleanup()
    def start(self,code):
        p=self.port.launch([sys.executable,'-I','-B','-c',code],cwd=self.tmp.name,env={'PATH':'/usr/bin:/bin'})
        self.children.append(p);ready,_,_=select.select([p.stdout],[],[],5);self.assertTrue(ready)
        self.assertEqual(b'ready\n',p.stdout.readline());return p
    def known(self,p):
        identity=self.port.identity(p);self.assertIsNotNone(identity['birth'])
        return {p.pid:dict(birth=identity['birth'],ppid=os.getpid(),pgid=p.pid)}
    def test_live_child_is_observed_then_reaped_with_group_absence(self):
        p=self.start('import time;print("ready",flush=True);time.sleep(30)');known=self.known(p)
        rows=self.port.observe(p,known);self.assertIn(p.pid,rows)
        result=self.port.stop(p,known,seconds=4)
        self.assertTrue(result['group_absent']);self.assertTrue(result['final_scan_confirmed'])
        self.assertIsNotNone(p.poll())
    def test_reaped_parent_does_not_hide_live_group_child(self):
        # Parent creates a harmless same-group child and exits only on stdin.
        code='import subprocess,sys,time; c=subprocess.Popen([sys.executable,"-I","-B","-c","import time;time.sleep(30)"]); print("ready",flush=True);sys.stdin.read(1)'
        p=self.start(code);known=self.known(p);rows=self.port.observe(p,known)
        self.assertGreaterEqual(len(known),2)
        p.stdin.write(b'x');p.stdin.flush();p.wait(timeout=5)
        self.assertTrue(any(pid!=p.pid for pid in known))
        result=self.port.stop(p,known,seconds=4)
        self.assertTrue(result['children']);self.assertTrue(all(c['absent'] for c in result['children']))
    def test_missing_identity_refuses_without_sending_signal(self):
        p=self.start('import time;print("ready",flush=True);time.sleep(30)')
        with patch('colvia.platforms.darwin_processes.os.killpg') as kill,self.assertRaisesRegex(RecordError,'runtime-identity-unavailable'):
            self.port.stop(p,{},seconds=1)
        kill.assert_not_called();self.assertIsNone(p.poll())
    def test_pid_reuse_and_scan_failure_never_claim_closure(self):
        p=self.start('import time;print("ready",flush=True);time.sleep(30)');known=self.known(p)
        original=self.port.scan;rows=original();rows[p.pid]['birth']='Sat Oct 31 12:00:00 2026'
        with patch.object(self.port,'scan',return_value=rows),self.assertRaisesRegex(RecordError,'pid-reuse'):
            self.port.stop(p,known,seconds=1)
        with patch.object(self.port,'scan',side_effect=RecordError('scan-unavailable')),self.assertRaisesRegex(RecordError,'scan-unavailable'):
            self.port.stop(p,known,seconds=1)
        self.assertIsNone(p.poll())

    def test_group_number_alone_cannot_adopt_unrelated_processes(self):
        from types import SimpleNamespace
        known={9000:dict(birth='Sat Oct 31 12:00:00 2026',ppid=1,pgid=9000)}
        rows={9001:dict(birth='Sun Nov  1 12:00:00 2026',ppid=1,pgid=9000)}
        with patch.object(self.port,'scan',return_value=rows),self.assertRaisesRegex(RecordError,'group-identity-unavailable'):
            self.port.observe(SimpleNamespace(pid=9000),known)
        self.assertEqual({9000},set(known))

    def test_owned_abort_reaps_child_without_birth_or_group_adoption(self):
        p=self.start('import time;print("ready",flush=True);time.sleep(30)')
        with patch('colvia.platforms.darwin_processes.os.killpg') as kill:
            self.port.abort_owned(p,seconds=2)
        kill.assert_not_called();self.assertIsNotNone(p.returncode)

    def test_launch_owns_unbuffered_pipes_and_closes_after_reaping(self):
        import io
        p=self.start('import time;print("ready",flush=True);time.sleep(30)')
        self.port.admit_io(p);self.assertTrue(all(type(s) is io.FileIO for s in (p.stdin,p.stdout,p.stderr)))
        self.port.stop(p,self.known(p),seconds=4);self.port.close_io(p)
        self.assertTrue(all(s.closed for s in (p.stdin,p.stdout,p.stderr)));self.children.remove(p)
    def test_replaced_stream_is_not_closed_as_an_owned_pipe(self):
        import io
        p=self.start('import time;print("ready",flush=True);time.sleep(30)');original=p.stdin;foreign=io.BytesIO()
        p.stdin=foreign
        try:
            with self.assertRaisesRegex(RecordError,'owned-pipes-required'):self.port.admit_io(p)
            self.assertFalse(foreign.closed);self.assertFalse(original.closed)
            # Cleanup owns the retained pipes, even after the public attributes change.
            self.port.stop(p,self.known(p),seconds=4);self.children.remove(p)
            self.port.close_io(p)
            self.assertFalse(foreign.closed)
            self.assertTrue(all(s.closed for s in (original,p.stdout,p.stderr)))
            with self.assertRaisesRegex(RecordError,'owned-pipes-required'):self.port.close_io(p)
            self.assertFalse(foreign.closed)
        finally:p.stdin=original;foreign.close()

    def test_signal_permission_denial_never_claims_closure(self):
        p=self.start('import time;print("ready",flush=True);time.sleep(30)');known=self.known(p)
        with patch('colvia.platforms.darwin_processes.os.killpg',side_effect=PermissionError(1,'synthetic signal denial')),self.assertRaises(PermissionError):
            self.port.stop(p,known,seconds=4)
        self.assertIsNone(p.poll())
        closed=self.port.stop(p,known,seconds=4)
        self.assertTrue(closed['group_absent']);self.assertTrue(closed['final_scan_confirmed'])
        self.port.close_io(p);self.children.remove(p)

    def wait_zombie_without_reaping(self,p):
        deadline=time.monotonic()+5
        while time.monotonic()<deadline:
            state=subprocess.run(['/bin/ps','-p',str(p.pid),'-o','stat='],capture_output=True,text=True,timeout=2)
            if 'Z' in state.stdout:return
            time.sleep(.01)
        self.fail('owned child did not reach observable zombie state')

    def test_exited_unreaped_root_closes_without_signal_permission_error(self):
        p=self.start('import sys;print("ready",flush=True);sys.stdin.read(1)');known=self.known(p)
        p.stdin.write(b'x');p.stdin.flush();self.wait_zombie_without_reaping(p)
        self.assertIsNone(p.returncode)
        result=self.port.stop(p,known,seconds=4)
        self.assertTrue(result['group_absent']);self.assertTrue(result['final_scan_confirmed'])
        self.assertEqual(result['returncode'],0)
        self.port.close_io(p);self.children.remove(p)

    def test_zombie_root_does_not_hide_live_group_descendant(self):
        code='import subprocess,sys; subprocess.Popen([sys.executable,"-I","-B","-c","import time;time.sleep(30)"]); print("ready",flush=True);sys.stdin.read(1)'
        p=self.start(code);known=self.known(p);self.port.observe(p,known);self.assertGreaterEqual(len(known),2)
        p.stdin.write(b'x');p.stdin.flush();self.wait_zombie_without_reaping(p)
        self.assertIsNone(p.returncode)
        result=self.port.stop(p,known,seconds=4)
        self.assertTrue(result['group_absent']);self.assertTrue(result['final_scan_confirmed'])
        self.assertTrue(result['children']);self.assertTrue(all(c['absent'] for c in result['children']))
        self.port.close_io(p);self.children.remove(p)
