"""Real installed processes with test-only guard observation barriers.

No product bytes or guard semantics are replaced. The in-memory wrapper delays
entry/yield for deterministic observation; these are instrumented CLI tests.
"""
from __future__ import annotations
from tests.platform_fixtures import (
    fixture_pgid,
)
import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile
import time
import unittest

from hv2ref.jsonio import canonical_json_bytes
from hv2ref.work import read_work
from test_productization_safety import exact_snapshot
import test_worktree_execution as fixtures


CHILD = r"""
import builtins, contextlib, json, os, runpy, sys, time
from pathlib import Path
target, signals, identity, token = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3], sys.argv[4]
mine = signals / identity
def emit(name):
    with (mine / (name + '.json')).open('x') as f:
        json.dump({'event':name,'pid':os.getpid(),'pgid':None if sys.platform == 'win32' else os.getpgrp(),'monotonic_ns':time.monotonic_ns()},f)
def wait_for(path):
    deadline=time.monotonic()+180
    while not path.exists():
        if time.monotonic()>deadline:raise TimeoutError('test barrier deadline: '+path.name)
        time.sleep(.01)
if sys.platform != 'win32':
    import fcntl
    original_flock=fcntl.flock
    def observed_flock(fd, operation):
        if operation == fcntl.LOCK_EX:emit('lock-attempting')
        return original_flock(fd, operation)
    fcntl.flock=observed_flock
original_import = builtins.__import__
patched = False
native_lock_patched = False
def instrument(name, globals=None, locals=None, fromlist=(), level=0):
    global patched, native_lock_patched
    module=original_import(name, globals, locals, fromlist, level)
    jsonio=sys.modules.get('hv2ref.jsonio')
    if sys.platform == 'win32' and not native_lock_patched and jsonio is not None and hasattr(jsonio,'_windows_api'):
        native_lock_patched=True
        api=jsonio._windows_api();original_lock=api.LockFileEx
        def observed_native_lock(*args):
            emit('lock-attempting')
            return original_lock(*args)
        api.LockFileEx=observed_native_lock
    workspace=sys.modules.get('hv2ref.workspace')
    if not patched and workspace is not None and hasattr(workspace,'writer_guard'):
        patched=True
        original_guard=workspace.writer_guard
        @contextlib.contextmanager
        def observed_guard(*args,**kwargs):
            emit('waiting');wait_for(signals/'start')
            emit('attempting')
            with original_guard(*args,**kwargs):
                emit('acquired');wait_for(mine/'permit')
                try:yield
                finally:emit('leaving')
            emit('released')
        workspace.writer_guard=observed_guard
    return module
builtins.__import__=instrument
sys.argv=[str(target/'colvia'),'work','apply','--input','-','--confirm',token]
runpy.run_path(str(target/'colvia'),run_name='__main__')
"""


class InstalledWorkerProcessTests(unittest.TestCase):
    setUp=fixtures.InstalledWorkerPublicationTests.setUp
    TIME=fixtures.InstalledWorkerPublicationTests.TIME
    call=fixtures.InstalledWorkerPublicationTests.call
    git=fixtures.InstalledWorkerPublicationTests.git
    installed=fixtures.InstalledWorkerPublicationTests.installed
    preview=fixtures.InstalledWorkerPublicationTests.preview
    apply_init=fixtures.InstalledWorkerPublicationTests.apply_init
    accept_intent=fixtures.InstalledWorkerPublicationTests.accept_intent
    draft=fixtures.InstalledWorkerPublicationTests.draft
    prepare_worker_result=fixtures.InstalledWorkerPublicationTests.prepare_worker_result

    def run_contention(self, *, competing):
        prepared=self.prepare_worker_result()
        lock=self.target/'.hrn/locks/writer.lock';lock_before=lock.read_bytes()
        tickets=[prepared['ticket'],copy.deepcopy(prepared['ticket'])]
        if competing:tickets[1]['request_id']='competing-acceptance'
        # Evidence is outside project content. The runner retains this directory.
        fallback=self.base.parent/('worker-process-evidence-'+self.base.name)
        evidence=Path(os.environ.get('HV2_PROCESS_EVIDENCE',str(fallback)))/self._testMethodName
        evidence.mkdir(parents=True)
        script=evidence/'child.py';script.write_text(CHILD)
        signals=evidence/'signals';signals.mkdir()
        git_before=exact_snapshot(self.target/'.git')
        processes=[];handles=[];commands=[];codes=[];success=False
        def observe(name,index):return signals/str(index)/(name+'.json')
        def await_state(predicate, detail, timeout=180):
            deadline=time.monotonic()+timeout
            while not predicate():
                if any(p.poll() is not None for p in processes):
                    self.fail(detail+': child exited before barrier')
                if time.monotonic()>deadline:self.fail(detail+': barrier deadline')
                time.sleep(.01)
        try:
            for i,ticket in enumerate(tickets):
                mine=signals/str(i);mine.mkdir()
                data=canonical_json_bytes(ticket);token=hashlib.sha256(data).hexdigest()[:16]
                input_path=evidence/f'input-{i}.json';input_path.write_bytes(data)
                stdin=input_path.open('rb');out=(evidence/f'stdout-{i}.log').open('xb');err=(evidence/f'stderr-{i}.log').open('xb');handles.extend([stdin,out,err])
                command=[sys.executable,'-I','-B',str(script),str(self.target),str(signals),str(i),token]
                p=subprocess.Popen(command,cwd=self.target,stdin=stdin,stdout=out,stderr=err)
                processes.append(p);commands.append({'argv':command,'pid':p.pid,'pgid':fixture_pgid(p.pid),'input_sha256':hashlib.sha256(data).hexdigest()})
            await_state(lambda:all(observe('waiting',i).exists() for i in range(2)),'both started')
            self.assertNotEqual(processes[0].pid,processes[1].pid)
            (signals/'start').write_text('go')
            await_state(lambda:all(observe('lock-attempting',i).exists() for i in range(2)),'both at OS lock boundary')
            await_state(lambda:any(observe('acquired',i).exists() for i in range(2)),'first acquisition')
            acquired=[i for i in range(2) if observe('acquired',i).exists()]
            self.assertEqual(1,len(acquired));first=acquired[0];second=1-first
            before_graph=read_work(self.target,'work-a');self.assertEqual('review',before_graph['state']);self.assertEqual({},before_graph['decisions'])
            (signals/str(first)/'permit').write_text('apply')
            first_code=processes[first].wait(timeout=240);self.assertEqual(0,first_code)
            # The second process now holds the real guard but cannot execute yet.
            deadline=time.monotonic()+180
            while not observe('acquired',second).exists():
                self.assertIsNone(processes[second].poll())
                self.assertLess(time.monotonic(),deadline);time.sleep(.01)
            after_first=exact_snapshot(self.target,writer_lock_held=True)
            first_leave=json.loads(observe('leaving',first).read_text())
            second_acquire=json.loads(observe('acquired',second).read_text())
            self.assertGreaterEqual(second_acquire['monotonic_ns'],first_leave['monotonic_ns'])
            (signals/str(second)/'permit').write_text('apply')
            second_code=processes[second].wait(timeout=240)
            self.assertEqual(65 if competing else 0,second_code)
            self.assertEqual(after_first,exact_snapshot(self.target,writer_lock_held=True))
            self.assertEqual(lock_before,lock.read_bytes())
            graph=read_work(self.target,'work-a');self.assertEqual('completed',graph['state'])
            self.assertEqual(1,len(graph['decisions']))
            self.assertEqual(1,sum(s['decision_ref'] is not None for s in graph['selections'].values()))
            self.assertEqual([],graph['pending_decisions']);self.assertEqual([],graph['pending_selections'])
            self.assertEqual(b'installed worker result\n',(self.target/'a').read_bytes())
            self.assertEqual(git_before,exact_snapshot(self.target/'.git'))
            if competing:
                error=json.loads((evidence/f'stdout-{second}.log').read_bytes())
                self.assertEqual('HV2-WORK-RECORD',error['code'])
                self.assertIn('stale confirmation selection',error['message'])
            success=True
        finally:
            for p in processes:
                if p.poll() is None:
                    p.terminate()
                    try:p.wait(timeout=5)
                    except subprocess.TimeoutExpired:p.kill();p.wait(timeout=5)
                codes.append(p.returncode)
            for handle in handles:handle.close()
            if not success:
                with tarfile.open(evidence/'failed-target.tar.gz','w:gz') as archive:archive.add(self.target,arcname='target')
            events={str(p.relative_to(signals)):json.loads(p.read_text()) for p in signals.rglob('*.json')}
            receipt={'kind':'instrumented installed CLI with unmodified product files and original guard','success':success,'competing':competing,'commands':commands,'exit_codes':codes,'all_children_joined':all(p.poll() is not None for p in processes),'events':events}
            (evidence/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
            print(json.dumps({'process_case':self._testMethodName,'success':success,'exit_codes':codes,'pids':[p.pid for p in processes]}),flush=True)

    def test_same_ticket_two_processes_select_once_then_read_only_replay(self):
        self.run_contention(competing=False)

    def test_competing_tickets_one_selection_and_stale_loser_no_mutation(self):
        self.run_contention(competing=True)
