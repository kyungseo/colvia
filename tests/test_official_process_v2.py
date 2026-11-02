"""Real OS liveness/absence observations with synthetic journal authority."""
from pathlib import Path
from types import SimpleNamespace
import os
import selectors
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

import test_official_v2 as fixture
from hv2ref import official_state as state, official_adapter as adapter
from hv2ref.errors import ContractError
from hv2ref.official_documents import canonical


class ProcessV2Tests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.target=Path(self.temp.name).resolve()
        self.root=self.target/'.hrn/executions'/fixture.SHA;self.root.mkdir(parents=True,mode=0o700)
        (self.target/'output.md').write_text('synthetic output\n');(self.target/'reference.md').write_text('synthetic reference\n')
    def child(self):
        p=subprocess.Popen([sys.executable,'-I','-S','-B','-c','import time; print("ready", flush=True); time.sleep(60)'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,start_new_session=True)
        def cleanup():
            if p.poll() is None:p.kill()
            p.wait(timeout=5)
            for stream in (p.stdin,p.stdout,p.stderr):
                if not stream.closed:stream.close()
        self.addCleanup(cleanup)
        self.assertEqual(b'ready\n',p.stdout.readline());birth=state.process_birth(p.pid);self.assertTrue(birth)
        return p,birth
    def write(self,chain):
        for name,raw in (('grant.json',state.canonical(chain.grant)),('journal.jsonl',b''.join(canonical(r) for r in chain.rows))):
            path=self.root/name;path.write_bytes(raw);path.chmod(0o600)
    def chain(self,p,birth):
        c=fixture.Chain(fixture.grant(str(self.target)))
        c.add('runtime-reserved',ordinal=1,host_pid=os.getpid(),host_birth=state.process_birth(os.getpid()))
        c.add('runtime-started',ordinal=1,pid=p.pid,birth=birth);return c

    def test_live_runtime_refuses_resolution_then_actual_absence_allows_preview(self):
        p,birth=self.child();c=self.chain(p,birth);self.write(c)
        with self.assertRaisesRegex(ContractError,'process-present-or-unconfirmed'):state.resolution_preview(self.target,fixture.SHA)
        with self.assertRaises(ContractError):state.require_no_open(self.target)
        self.assertIsNone(p.poll());self.assertEqual(birth,state.process_birth(p.pid));self.assertFalse(state.group_absent(p.pid))
        p.kill();p.wait(timeout=5);self.assertTrue(state.group_absent(p.pid))
        preview=state.resolution_preview(self.target,fixture.SHA)
        self.assertTrue(preview['observation']['process_absence']);self.assertEqual('incomplete',preview['observation']['previous_status'])

    def test_observed_child_still_live_prevents_resolution_after_runtime_exit(self):
        p,birth=self.child();child,child_birth=self.child();c=self.chain(p,birth)
        c.add('runtime-child',pid=child.pid,birth=child_birth);self.write(c)
        p.kill();p.wait(timeout=5)
        with self.assertRaisesRegex(ContractError,'observed-child-present'):state.resolution_preview(self.target,fixture.SHA)
        self.assertIsNone(child.poll());child.kill();child.wait(timeout=5)
        self.assertTrue(state.resolution_preview(self.target,fixture.SHA)['observation']['process_absence'])

    def test_locale_cannot_hide_observed_live_child(self):
        with mock.patch.dict(os.environ, {'LC_ALL': 'C'}):
            p, birth = self.child(); child, child_birth = self.child(); c = self.chain(p, birth)
        c.add('runtime-child', pid=child.pid, birth=child_birth); self.write(c)
        p.kill(); p.wait(timeout=5)
        for locale, zone in (('ko_KR.UTF-8', 'Asia/Seoul'), ('fr_FR.UTF-8', 'Pacific/Honolulu')):
            with mock.patch.dict(os.environ, {'LC_ALL': locale, 'TZ': zone}):
                with self.subTest(locale=locale, observation='identity'):
                    self.assertEqual(child_birth, state.process_birth(child.pid))
                with self.subTest(locale=locale, observation='resolution'), self.assertRaisesRegex(ContractError, 'observed-child-present'):
                    state.resolution_preview(self.target, fixture.SHA)
                self.assertIsNone(child.poll())

    def test_v1_localized_child_identity_never_proves_absence(self):
        from hv2ref.official_documents import EffectJournal
        p, birth = self.child(); child, _ = self.child()
        localized = subprocess.run(['/bin/ps', '-p', str(child.pid), '-o', 'lstart='],
                                   env={'LC_ALL': 'ko_KR.UTF-8'}, capture_output=True, text=True, check=True).stdout.strip()
        spec = {'target': str(self.target), 'request': {'worker_limit': 5},
                'documents': {'files': {'Output': {'path': str(self.target / 'output.md')}}}}
        grant = state.digest(state.canonical(spec)); root = self.target / '.hrn/executions' / grant
        root.mkdir(mode=0o700)
        state.publish(root / 'grant.json', {'record_type': 'official-execution-grant', 'schema_version': 1, 'grant': grant, 'spec': spec})
        journal = EffectJournal(root / 'journal.jsonl', create=True)
        journal.append('granted', {'grant': grant}); journal.append('runtime-reserved', {})
        journal.append('runtime-started', {'pid': p.pid, 'birth': birth})
        journal.append('runtime-child', {'pid': child.pid, 'birth': localized})
        before = (root / 'journal.jsonl').read_bytes(); p.kill(); p.wait(timeout=5)
        with mock.patch.dict(os.environ, {'LC_ALL': 'C'}), self.assertRaisesRegex(ContractError, 'observed-child-present'):
            state.resolution_preview(self.target, grant)
        self.assertIsNone(child.poll()); self.assertEqual(before, (root / 'journal.jsonl').read_bytes())
        child.kill(); child.wait(timeout=5)
        self.assertTrue(state.resolution_preview(self.target, grant)['observation']['process_absence'])

    def test_unavailable_or_malformed_process_observation_is_not_absence(self):
        for code, out, err in ((0, '', ''), (1, '', 'denied'), (1, fixture.BIRTH, ''), (0, 'unrecognized birth', '')):
            with self.subTest(code=code, out=out, err=err), \
                 mock.patch.object(state.subprocess, 'run', return_value=SimpleNamespace(returncode=code, stdout=out, stderr=err)), \
                 self.assertRaises(ContractError):
                state.process_birth(9001)
        with mock.patch.object(state.subprocess, 'run', return_value=SimpleNamespace(returncode=1, stdout='', stderr='')):
            self.assertEqual('', state.process_birth(9001))

    def test_missing_birth_stays_unresolvable_after_actual_child_exit(self):
        p,birth=self.child();c=self.chain(p,None);self.write(c)
        p.kill();p.wait(timeout=5);self.assertTrue(state.group_absent(p.pid))
        with self.assertRaisesRegex(ContractError,'identity-unavailable'):state.resolution_preview(self.target,fixture.SHA)
        self.assertNotEqual(birth,state.process_birth(p.pid));state.read_capsule(self.target,fixture.SHA)

    def test_runtime_stdin_backpressure_obeys_deadline(self):
        import threading,time
        frame={'id':1,'method':'initialize','params':{'clientInfo':{'name':'x'*200000}}}
        # Validate once before the transport clock. Scanner latency cannot make
        # this backpressure-only oracle pass before any pipe bytes are written.
        raw=adapter.checked_payload(frame,limit=adapter.LIMIT-1,protocol=True)
        p,_=self.child();rpc=adapter.Rpc.__new__(adapter.Rpc);rpc.p=p;rpc.deadline=time.monotonic()+.15
        rpc.outgoing_bytes=rpc.outgoing_frames=0;rpc.outgoing_partial=False
        done=threading.Event();errors=[]
        def send():
            try:
                with mock.patch.object(adapter,'checked_payload',return_value=raw):rpc.send(frame)
            except BaseException as error:errors.append(error)
            finally:done.set()
        thread=threading.Thread(target=send,daemon=True);thread.start()
        try:
            completed=done.wait(1)
        finally:
            if p.poll() is None:p.kill()
            p.wait(timeout=5);thread.join(5)
        self.assertFalse(thread.is_alive());self.assertTrue(completed,'RPC send exceeded deadline while stdin was not consumed')
        self.assertEqual(1,len(errors));self.assertIsInstance(errors[0],TimeoutError)
        self.assertGreater(rpc.outgoing_bytes,0);self.assertTrue(rpc.outgoing_partial)

    def test_real_surviving_runtime_cannot_emit_closed_evidence(self):
        p,birth=self.child();rpc=adapter.Rpc.__new__(adapter.Rpc)
        rpc.p=p;rpc.closed=False;rpc.runtime_ref=3;rpc.known_children={};rpc.sel=selectors.DefaultSelector()
        rpc.host=SimpleNamespace(journal=mock.Mock())
        # Inject denied signalling only; process/group/descendant observers are real.
        with mock.patch.object(adapter,'signal_owned',return_value=False):result=rpc.close()
        self.assertFalse(result['observed_tree_absent']);rpc.host.journal.append.assert_not_called()
        self.assertIsNone(p.poll());self.assertEqual(birth,state.process_birth(p.pid));self.assertFalse(state.group_absent(p.pid))


if __name__=='__main__':unittest.main()
