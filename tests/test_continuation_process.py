"""Real process contention/death, with unmodified installed product bytes."""
from __future__ import annotations
import copy
import fcntl
import hashlib
import json
import os
import signal
import subprocess
import sys
import time
import unittest
from hv2ref.continuation import read_continuation,records
from hv2ref.jsonio import canonical_json_bytes
from hv2ref.work import record_ref,read_work
import test_continuation_view as fixtures
import test_productization_safety as installed


class ContinuationProcessTests(unittest.TestCase):
    TIME=fixtures.ContinuationInstalledTests.TIME
    call=fixtures.ContinuationInstalledTests.call
    preview=fixtures.ContinuationInstalledTests.preview
    apply_init=fixtures.ContinuationInstalledTests.apply_init
    installed=fixtures.ContinuationInstalledTests.installed
    draft=fixtures.ContinuationInstalledTests.draft
    accept_intent=fixtures.ContinuationInstalledTests.accept_intent
    complete_work=fixtures.ContinuationInstalledTests.complete_work
    seed=fixtures.ContinuationInstalledTests.seed
    prepare_cont=fixtures.ContinuationInstalledTests.prepare_cont
    apply_cont=fixtures.ContinuationInstalledTests.apply_cont

    def setUp(self):
        fixtures.ContinuationInstalledTests.setUp(self)
        self.children=[];self.handles=[];self.sequence=0
        self.evidence=self.base.parent/("continuation-process-"+self.base.name)
        self.evidence.mkdir()
        self.addCleanup(self.cleanup)
        self.seed()

    def cleanup(self):
        for child in self.children:
            if child.poll() is None:
                child.terminate()
                try:child.wait(timeout=5)
                except subprocess.TimeoutExpired:child.kill();child.wait(timeout=5)
            else:child.wait()
        for handle in self.handles:handle.close()
        result={"all_children_joined":all(p.poll() is not None for p in self.children),
                "exit_codes":[p.returncode for p in self.children]}
        (self.evidence/"cleanup.json").write_text(json.dumps(result)+"\n")

    def spawn(self,value,command,*,mode="contend",phase=None,group=None):
        self.sequence+=1
        group=group or self.evidence
        folder=group/str(self.sequence);folder.mkdir(parents=True)
        payload=canonical_json_bytes(value)
        (folder/"input.json").write_bytes(payload)
        config={"command":command,"mode":mode,"phase":phase}
        (folder/"config.json").write_bytes(canonical_json_bytes(config))
        stdin=(folder/"input.json").open("rb");stdout=(folder/"stdout.log").open("xb");stderr=(folder/"stderr.log").open("xb")
        self.handles.extend((stdin,stdout,stderr))
        argv=[sys.executable,"-I","-B",str(self.source/"tests/fixtures/continuation_process.py"),
              str(self.target),str(folder),str(folder/"config.json")]
        process=subprocess.Popen(argv,cwd=self.target,stdin=stdin,stdout=stdout,stderr=stderr)
        self.children.append(process)
        (folder/"invocation.json").write_text(json.dumps({"argv":argv,"pid":process.pid,"pgid":os.getpgid(process.pid),
             "input_sha256":hashlib.sha256(payload).hexdigest()})+"\n")
        return process,folder

    def wait_event(self,child,folder,event):
        deadline=time.monotonic()+120
        while not (folder/(event+".json")).is_file():
            if child.poll() is not None:
                self.fail((folder/"stdout.log").read_text()+(folder/"stderr.log").read_text())
            self.assertLess(time.monotonic(),deadline,"event deadline: "+event)
            time.sleep(.01)
        value=json.loads((folder/(event+".json")).read_bytes())
        self.assertEqual(child.pid,value["pid"])
        return value

    def truth(self):
        return {str(path.relative_to(self.target)):path.read_bytes()
                for path in (self.target/".hrn").rglob("*.json")
                if "/continuation/" not in str(path) and not path.is_relative_to(self.target/".hrn/staging")}

    def run_contention(self,competing):
        p=self.prepare_cont()
        tickets=[p["ticket"],copy.deepcopy(p["ticket"])]
        if competing:tickets[1]["request_id"]="cont-competing"
        process=[]
        for ticket in tickets:
            token=hashlib.sha256(canonical_json_bytes(ticket)).hexdigest()[:16]
            process.append(self.spawn(ticket,["continuation","apply","--confirm",token]))
        for child,folder in process:self.wait_event(child,folder,"waiting")
        self.assertNotEqual(process[0][0].pid,process[1][0].pid)
        (self.evidence/"start").write_text("start")
        for child,folder in process:self.wait_event(child,folder,"lock-attempting")
        deadline=time.monotonic()+120
        while not any((folder/"acquired.json").exists() for _,folder in process):
            self.assertLess(time.monotonic(),deadline);time.sleep(.01)
        first=next(i for i,(_,folder) in enumerate(process) if (folder/"acquired.json").exists())
        second=1-first
        self.assertFalse((process[second][1]/"acquired.json").exists())
        original=self.truth()
        (process[first][1]/"permit").write_text("apply")
        self.assertEqual(0,process[first][0].wait(timeout=120))
        second_event=self.wait_event(*process[second],"acquired")
        first_event=json.loads((process[first][1]/"leaving.json").read_bytes())
        self.assertGreaterEqual(second_event["monotonic_ns"],first_event["monotonic_ns"])
        after=installed.exact_snapshot(self.target)
        (process[second][1]/"permit").write_text("apply")
        self.assertEqual(65 if competing else 0,process[second][0].wait(timeout=120))
        self.assertEqual(after,installed.exact_snapshot(self.target))
        self.assertEqual(original,self.truth())
        state=read_continuation(self.target,"work-a")
        self.assertEqual(1,len(state["choices"]));self.assertEqual(1,len(state["selections"]))
        self.assertEqual(1,state["usage"]["normal_used"])
        if competing:self.assertIn("stale continuation",json.loads((process[second][1]/"stdout.log").read_bytes())["message"])

    def test_same_ticket_processes_select_once(self):
        self.run_contention(False)

    def test_competing_processes_one_wins_stale_other_writes_nothing(self):
        self.run_contention(True)

    def kill_prefix(self,packet,phase):
        child,folder=self.spawn(packet["ticket"],["continuation","apply","--confirm",packet["confirm_token"]],
                                mode="crash",phase=phase)
        event=self.wait_event(child,folder,"barrier")
        self.assertTrue(event["guard_held"]);self.assertEqual(phase,event["point"])
        lock=self.target/".hrn/locks/writer.lock"
        with lock.open("rb") as stream:
            with self.assertRaises(BlockingIOError):fcntl.flock(stream,fcntl.LOCK_EX|fcntl.LOCK_NB)
        prefix=read_continuation(self.target,"work-a")
        (folder/"prefix.json").write_bytes(canonical_json_bytes(prefix))
        child.kill();self.assertEqual(-signal.SIGKILL,child.wait(timeout=10))
        self.assertFalse((folder/"leaving.json").exists());self.assertFalse((folder/"released.json").exists())
        with lock.open("rb") as stream:
            fcntl.flock(stream,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(stream,fcntl.LOCK_UN)
        self.assertEqual(prefix,read_continuation(self.target,"work-a"))
        (folder/"death.json").write_text(json.dumps({"signal":"SIGKILL","exit_code":child.returncode,
            "guard_held_before":True,"lock_released_by_process_death":True,"prefix_unchanged":True})+"\n")
        return prefix

    def test_actual_death_choice_selection_and_current_resume_or_replay(self):
        for index,phase in enumerate(("after-initial-current","after-choice","after-selection","after-staged-current","after-current")):
            with self.subTest(phase=phase):
                packet=self.prepare_cont(request_id="kill-"+str(index))
                original=self.truth()
                prefix=self.kill_prefix(packet,phase)
                self.apply_cont(packet)
                state=read_continuation(self.target,"work-a")
                self.assertIsNone(state["pending"]);self.assertEqual(index+1,state["usage"]["normal_used"])
                self.assertEqual(original,self.truth())
                before=installed.exact_snapshot(self.target)
                self.assertEqual("resolved",self.apply_cont(packet)["replay"])
                self.assertEqual(before,installed.exact_snapshot(self.target))

    def test_actual_death_during_cancellation_keeps_prior_choice(self):
        first=self.prepare_cont();self.apply_cont(first)
        original=self.prepare_cont(request_id="withdraw",action="withdraw",choice=None)
        self.kill_prefix(original,"after-selection")
        choice,_=records(original["ticket"])
        cancel=self.prepare_cont(request_id="cancel",action="cancel-pending",choice=None,supersedes_choice_ref=record_ref(choice))
        prefix=self.kill_prefix(cancel,"after-choice")
        self.assertEqual({"kind":"none"},prefix["effective_choice"])
        frozen=installed.exact_snapshot(self.target)
        self.assertEqual("cancelled",self.apply_cont(original)["replay"])
        self.assertEqual(frozen,installed.exact_snapshot(self.target))
        self.apply_cont(cancel)
        state=read_continuation(self.target,"work-a")
        self.assertIsNone(state["pending"]);self.assertEqual(first["ticket"],state["effective_ticket"])

    def test_waiting_work_writer_revalidates_pending_after_real_lock(self):
        packet=self.prepare_cont()
        work=read_work(self.target,"work-a")
        selected=work["selections"][work["current"]["selection_ref"]["id"]]
        revoke=json.loads(self.installed(["work","prepare"],{"work_id":"work-a","action":"revoke","actor":"owner",
            "reason":"synthetic","request_id":"revoke-a","observed_at":self.TIME,"revision_ref":None,"supersedes":selected["decision_ref"]}).stdout)
        first,folder=self.spawn(packet["ticket"],["continuation","apply","--confirm",packet["confirm_token"]],
                                mode="crash",phase="after-choice")
        self.wait_event(first,folder,"barrier")
        second,waiting=self.spawn(revoke["ticket"],["work","apply","--confirm",revoke["confirm_token"]],mode="observe")
        self.wait_event(second,waiting,"lock-attempting")
        self.assertFalse((waiting/"acquired.json").exists())
        before=self.truth()
        first.kill();self.assertEqual(-signal.SIGKILL,first.wait(timeout=10))
        self.assertEqual(65,second.wait(timeout=120))
        acquired=self.wait_event(second,waiting,"acquired")
        self.assertTrue(acquired["guard_held"])
        self.assertEqual(before,self.truth())
        self.assertIn("pending",json.loads((waiting/"stdout.log").read_bytes())["message"])
        self.apply_cont(packet)
