"""Abrupt installed-worker death at observed durable prefixes, then exact retry.

Barriers wrap original calls in memory; product bytes and installed checks stay
unchanged. These tests establish process death, not power-loss durability.
"""
from __future__ import annotations
import fcntl
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tarfile
import time
import unittest

from hv2ref.jsonio import canonical_json_bytes
from hv2ref.work import read_work, verify_worker_sources
from hv2ref.product import verify_workspace_product
from test_productization_safety import exact_snapshot
import test_worktree_execution as fixtures


CHILD = r"""
import builtins, contextlib, json, os, runpy, sys, time
from pathlib import Path
target, evidence, phase, token = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3], sys.argv[4]
held=False
def emit(name, **extra):
    value={'event':name,'pid':os.getpid(),'pgid':os.getpgrp(),'monotonic_ns':time.monotonic_ns(),'guard_held':held,**extra}
    temporary=evidence/(name+'.writing')
    with temporary.open('x') as f:json.dump(value,f)
    os.replace(temporary,evidence/(name+'.json'))
def pause(point, path):
    if point!=phase:return
    if not held:raise RuntimeError('barrier outside actual writer guard')
    emit('barrier',point=point,path=str(path.relative_to(target)))
    deadline=time.monotonic()+180
    while time.monotonic()<deadline:time.sleep(.01)
    raise TimeoutError('kill barrier not consumed')
original_import=builtins.__import__
workspace_patched=False;work_patched=False
def instrument(name, globals=None, locals=None, fromlist=(), level=0):
    global workspace_patched,work_patched
    module=original_import(name,globals,locals,fromlist,level)
    workspace=sys.modules.get('hv2ref.workspace')
    if not workspace_patched and workspace is not None and hasattr(workspace,'writer_guard'):
        workspace_patched=True;original_guard=workspace.writer_guard
        @contextlib.contextmanager
        def guard(*args,**kwargs):
            global held
            with original_guard(*args,**kwargs):
                held=True;emit('acquired')
                try:yield
                finally:emit('leaving');held=False
            emit('released')
        workspace.writer_guard=guard
    work=sys.modules.get('hv2ref.work')
    if not work_patched and work is not None and hasattr(work,'WorkStore'):
        work_patched=True
        original_publish=work._publish_immutable;original_path=work._apply_worker_path
        def publish(path,value):
            original_publish(path,value)
            kind=value.get('record_type')
            if kind=='work-decision':pause('after-decision',path)
            if kind=='work-selection':pause('after-selection',path)
        def apply_path(target,change,*args,**kwargs):
            original_path(target,change,*args,**kwargs)
            pause('after-file',target/change['path'])
        work._publish_immutable=publish;work._apply_worker_path=apply_path
    return module
builtins.__import__=instrument
sys.argv=[str(target/'hv2'),'work','apply','--input','-','--confirm',token]
runpy.run_path(str(target/'hv2'),run_name='__main__')
"""


class InstalledWorkerInterruptionTests(unittest.TestCase):
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

    def run_interruption(self,phase,*,remove_worker=False):
        fallback=self.base.parent/('worker-crash-evidence-'+self.base.name)
        evidence=Path(os.environ.get('HV2_PROCESS_EVIDENCE',str(fallback)))/self._testMethodName
        evidence.mkdir(parents=True)
        child=None;handles=[];commands=[];success=False;observations={}
        def save(name,value):
            (evidence/(name+'.json')).write_text(json.dumps(value,indent=2)+'\n')
        try:
            prepared=self.prepare_worker_result(two_files=True)
            if hasattr(self,"before_pending"):self.before_pending(prepared)
            data=canonical_json_bytes(prepared['ticket'])
            token=prepared['confirm_token']
            self.assertEqual(hashlib.sha256(data).hexdigest()[:16],token)
            git_before=exact_snapshot(self.target/'.git')
            initial=read_work(self.target,'work-a');current=initial['current']
            script=evidence/'child.py';script.write_text(CHILD)
            request=evidence/'input.json';request.write_bytes(data)
            stdin=request.open('rb');out=(evidence/'child.stdout').open('xb');err=(evidence/'child.stderr').open('xb');handles.extend([stdin,out,err])
            argv=[sys.executable,'-I','-B',str(script),str(self.target),str(evidence),phase,token]
            child=subprocess.Popen(argv,cwd=self.target,stdin=stdin,stdout=out,stderr=err)
            pid=child.pid;pgid=os.getpgid(pid)
            commands.append({'argv':argv,'cwd':str(self.target),'pid':pid,'pgid':pgid,'input_sha256':hashlib.sha256(data).hexdigest()})
            deadline=time.monotonic()+180
            while not (evidence/'barrier.json').exists():
                self.assertIsNone(child.poll(),(evidence/'child.stderr').read_text())
                self.assertLess(time.monotonic(),deadline,'barrier deadline')
                time.sleep(.01)
            barrier=json.loads((evidence/'barrier.json').read_text())
            self.assertEqual(pid,barrier['pid']);self.assertEqual(pgid,barrier['pgid'])
            self.assertTrue(barrier['guard_held']);self.assertEqual(phase,barrier['point'])
            self.assertIsNone(child.poll());self.assertEqual(pgid,os.getpgid(pid))
            lock=self.target/'.hrn/locks/writer.lock'
            with lock.open('rb') as handle:
                with self.assertRaises(BlockingIOError):fcntl.flock(handle,fcntl.LOCK_EX|fcntl.LOCK_NB)
            observations['lock_blocked_while_child_alive']=True
            prefix=read_work(self.target,'work-a');save('prefix-graph',prefix)
            self.assertEqual('review',prefix['state']);self.assertEqual(current,prefix['current'])
            self.assertEqual(1,len(prefix['decisions']))
            human=[s for s in prefix['selections'].values() if s['decision_ref'] is not None]
            self.assertEqual(1 if phase=='after-selection' else 0,len(human))
            self.assertTrue(prefix['pending_decisions'] or prefix['pending_selections'])
            contents={p:(self.target/p).read_bytes() for p in ('a','b')}
            expected={'a':b'before\n','b':b'second before\n'}
            if phase in ('after-file','after-selection'):expected['a']=b'installed worker result\n'
            if phase=='after-selection':expected['b']=b'second result\n'
            self.assertEqual(expected,contents)
            observations['prefix_contents']={k:v.decode() for k,v in contents.items()}
            observations['prefix_current_unchanged']=True
            # Popen owns this exact live child; no external PID lookup or group kill.
            child.kill();self.assertEqual(-signal.SIGKILL,child.wait(timeout=10))
            observations['kill_signal']='SIGKILL';observations['killed_exit_code']=child.returncode
            self.assertFalse((evidence/'leaving.json').exists());self.assertFalse((evidence/'released.json').exists())
            with lock.open('rb') as handle:
                fcntl.flock(handle,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(handle,fcntl.LOCK_UN)
            observations['lock_available_after_death']=True
            self.assertEqual(prefix,read_work(self.target,'work-a'))
            self.assertEqual(contents,{p:(self.target/p).read_bytes() for p in ('a','b')})
            if remove_worker:
                # This explicit fault setup changes registration metadata, not
                # authority. Prove apply/death Git invariance before removal,
                # then compare resume with the post-removal Git snapshot.
                self.assertEqual(git_before,exact_snapshot(self.target/'.git'))
                worker=self.base/'worker'
                revision=prefix['revisions']['result']
                manifest=prefix['manifests'][revision['result_refs']['manifest']['id']]
                product=verify_workspace_product(self.target)
                def verify_sources():
                    verify_worker_sources(self.target,manifest,
                        verified_launcher_sha256=product['launcher_sha256'],
                        verified_inventory_id=product['inventory']['inventory_id'])
                self.assertEqual(manifest['candidate_commit'],self.git(worker,'rev-parse','HEAD'))
                self.assertEqual('',self.git(worker,'status','--porcelain','--untracked-files=all'))
                self.assertEqual('',self.git(worker,'ls-files','--others','--ignored','--exclude-standard'))
                verify_sources()
                refs=self.git(self.target,'for-each-ref','--format=%(refname) %(objectname)')
                authority=exact_snapshot(self.target/'.hrn')
                worker_tree=exact_snapshot(worker)
                self.git(self.target,'worktree','remove',str(worker))
                self.assertFalse(worker.exists())
                self.assertNotIn(str(worker),self.git(self.target,'worktree','list','--porcelain'))
                self.assertEqual(refs,self.git(self.target,'for-each-ref','--format=%(refname) %(objectname)'))
                self.assertEqual(authority,exact_snapshot(self.target/'.hrn'))
                self.assertEqual(contents,{p:(self.target/p).read_bytes() for p in ('a','b')})
                verify_sources()
                git_before=exact_snapshot(self.target/'.git')
                observations['worker_removed_before_resume']=True
                observations['worker_tracked_snapshot_sha256']=hashlib.sha256(canonical_json_bytes(worker_tree)).hexdigest()
                observations['removal_preserved_refs_and_authority']=True
            if hasattr(self,"after_pending"):self.after_pending(prepared,observations)
            def invoke(label,expected_code=0):
                result=self.installed(['work','apply','--confirm',token],prepared['ticket'],expected=None)
                (evidence/(label+'.stdout')).write_bytes(result.stdout);(evidence/(label+'.stderr')).write_bytes(result.stderr)
                commands.append({'argv':list(map(str,result.args)),'cwd':str(self.target),'exit_code':result.returncode,'input_sha256':hashlib.sha256(data).hexdigest()})
                self.assertEqual(expected_code,result.returncode,(result.stdout+result.stderr).decode(errors='replace'))
                return json.loads(result.stdout)
            if phase!='after-decision':
                # A foreign edit after death must not be overwritten or completed.
                (self.target/'a').write_bytes(b'foreign after death\n')
                foreign=exact_snapshot(self.target)
                error=invoke('foreign-refusal',65)
                self.assertEqual(foreign,exact_snapshot(self.target))
                self.assertEqual('review',read_work(self.target,'work-a')['state'])
                observations['foreign_refusal_code']=error['code']
                (self.target/'a').write_bytes(contents['a'])  # fixture owner restores observed prefix
            mtimes={p:(self.target/p).stat().st_mtime_ns for p in ('a','b')}
            graph=invoke('resume')
            if remove_worker:self.assertFalse((self.base/'worker').exists())
            self.assertEqual('completed',graph['state']);self.assertEqual(1,len(graph['decisions']))
            self.assertEqual(1,sum(s['decision_ref'] is not None for s in graph['selections'].values()))
            self.assertEqual([],graph['pending_decisions']);self.assertEqual([],graph['pending_selections'])
            self.assertEqual(b'installed worker result\n',(self.target/'a').read_bytes())
            self.assertEqual(b'second result\n',(self.target/'b').read_bytes())
            already_post=['a','b'] if phase=='after-selection' else ['a'] if phase=='after-file' else []
            for path in already_post:self.assertEqual(mtimes[path],(self.target/path).stat().st_mtime_ns)
            observations['already_post_not_replaced']=already_post
            final=exact_snapshot(self.target);self.assertEqual(graph,invoke('replay'))
            self.assertEqual(final,exact_snapshot(self.target));self.assertEqual(git_before,exact_snapshot(self.target/'.git'))
            save('final-graph',graph);observations['git_unchanged']=True;observations['replay_unchanged']=True
            success=True
        finally:
            if child is not None and child.poll() is None:
                child.terminate()
                try:child.wait(timeout=5)
                except subprocess.TimeoutExpired:child.kill();child.wait(timeout=5)
            for handle in handles:handle.close()
            if not success:
                with tarfile.open(evidence/'failed-target.tar.gz','w:gz') as archive:archive.add(self.target,arcname='target')
            receipt={'kind':'instrumented installed CLI; actual SIGKILL; ordinary installed retry','phase':phase,'success':success,'commands':commands,'child_joined':child is not None and child.poll() is not None,'observations':observations}
            save('receipt',receipt)
            print(json.dumps({'interruption_case':self._testMethodName,'phase':phase,'success':success,'killed_exit':child.returncode if child else None}),flush=True)

    def run_edge_interruption(self,phase):
        evidence=self.base.parent/('worker-edge-evidence-'+self.base.name);evidence.mkdir()
        child=None;success=False;commands=[]
        try:
            prepared=self.prepare_worker_result(two_files=True);initial=exact_snapshot(self.target)
            git_before=exact_snapshot(self.target/'.git');graph_before=read_work(self.target,'work-a')
            # Instrument existing durability calls only in the child process.
            script=CHILD.replace("original_publish(path,value)\n            kind=value.get('record_type')", "kind=value.get('record_type')\n            if kind=='work-decision':pause('before-decision',path)\n            original_publish(path,value)")
            marker="work._publish_immutable=publish;work._apply_worker_path=apply_path"
            replacement=marker+"\n        original_current=work._publish_current\n        def current(target,path,*args,**kwargs):\n            original_current(target,path,*args,**kwargs)\n            pause('after-current',path)\n        work._publish_current=current"
            assert marker in script;script=script.replace(marker,replacement)
            (evidence/'child.py').write_text(script);data=canonical_json_bytes(prepared['ticket']);(evidence/'input.json').write_bytes(data)
            argv=[sys.executable,'-I','-B',str(evidence/'child.py'),str(self.target),str(evidence),phase,prepared['confirm_token']]
            with (evidence/'input.json').open('rb') as inp,(evidence/'stdout').open('xb') as out,(evidence/'stderr').open('xb') as err:
                child=subprocess.Popen(argv,cwd=self.target,stdin=inp,stdout=out,stderr=err)
                commands.append({'argv':argv,'cwd':str(self.target),'pid':child.pid,'pgid':os.getpgid(child.pid),'input_sha256':hashlib.sha256(data).hexdigest()})
                deadline=time.monotonic()+90
                while not (evidence/'barrier.json').exists():
                    self.assertIsNone(child.poll());self.assertLess(time.monotonic(),deadline);time.sleep(.01)
                barrier=json.loads((evidence/'barrier.json').read_text());self.assertEqual(child.pid,barrier['pid']);self.assertTrue(barrier['guard_held']);self.assertEqual(phase,barrier['point'])
                lock=self.target/'.hrn/locks/writer.lock'
                with lock.open('rb') as f:
                    with self.assertRaises(BlockingIOError):fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
                observed=read_work(self.target,'work-a');prefix=exact_snapshot(self.target)
                if phase=='before-decision':self.assertEqual(graph_before,observed);self.assertEqual(initial,prefix)
                else:
                    self.assertEqual('completed',observed['state']);self.assertEqual([],observed['pending_decisions']);self.assertEqual([],observed['pending_selections'])
                child.kill();self.assertEqual(-signal.SIGKILL,child.wait(timeout=10))
            self.assertEqual(prefix,exact_snapshot(self.target))
            with lock.open('rb') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
            retry=self.installed(['work','apply','--confirm',prepared['confirm_token']],prepared['ticket'])
            (evidence/'retry.stdout').write_bytes(retry.stdout);(evidence/'retry.stderr').write_bytes(retry.stderr)
            commands.append({'argv':list(map(str,retry.args)),'cwd':str(self.target),'exit':retry.returncode,'stdout_sha256':hashlib.sha256(retry.stdout).hexdigest(),'stderr_sha256':hashlib.sha256(retry.stderr).hexdigest()})
            if phase=='after-current':self.assertEqual(prefix,exact_snapshot(self.target))
            final=read_work(self.target,'work-a');self.assertEqual('completed',final['state']);self.assertEqual(1,len(final['decisions']))
            self.assertEqual(1,sum(s['decision_ref'] is not None for s in final['selections'].values()))
            self.assertEqual(b'installed worker result\n',(self.target/'a').read_bytes());self.assertEqual(b'second result\n',(self.target/'b').read_bytes());self.assertEqual(git_before,exact_snapshot(self.target/'.git'))
            (evidence/'graphs.json').write_text(json.dumps({'before':graph_before,'prefix':observed,'final':final},indent=2)+'\n');success=True
        finally:
            if child is not None and child.poll() is None:child.kill();child.wait(timeout=10)
            with tarfile.open(evidence/'fixture.tar.gz','w:gz') as archive:archive.add(self.base,arcname='fixture')
            (evidence/'receipt.json').write_text(json.dumps({'phase':phase,'success':success,'commands':commands,'child_pid':child.pid if child else None,'child_exit':child.returncode if child else None,'child_joined':child is not None and child.poll() is not None,'kind':'actual SIGKILL with in-memory barriers; not OS crash'},indent=2)+'\n')

    def test_kill_before_decision_preserves_truth_then_explicit_retry(self):
        self.run_edge_interruption('before-decision')

    def test_kill_after_current_replays_without_mutation(self):
        self.run_edge_interruption('after-current')

    def test_kill_after_decision_preserves_pre_and_resumes(self):
        self.run_interruption('after-decision')

    def test_kill_after_first_file_preserves_mixed_and_refuses_foreign_edit(self):
        self.run_interruption('after-file')

    def test_kill_after_first_file_resumes_without_worker_checkout(self):
        self.run_interruption('after-file',remove_worker=True)

    def test_kill_after_selection_preserves_current_and_refuses_foreign_edit(self):
        self.run_interruption('after-selection')
