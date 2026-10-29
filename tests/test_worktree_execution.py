"""Worker publication fixtures; serial runtime double and installed entry separated."""
from __future__ import annotations
from tests.platform_fixtures import (
    fixture_directory_link,
    fixture_is_link,
    fixture_snapshot,
    fixture_unlink,
)
from test_productization_safety import verified_inventory_id
import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest

from hv2ref.errors import ContractError, InjectedCrash
from hv2ref.work import make_manifest, snapshot, record_ref, read_work
from hv2ref.workspace import git_environment
import test_general_work_recovery
from test_general_work_recovery import digest, TIME
import test_productization_safety
from test_productization_safety import canonical_json_bytes, exact_snapshot


class WorkerPublicationTests(unittest.TestCase):
    accept_intent=test_general_work_recovery.SerialWriterTests.accept_intent
    proposal=test_general_work_recovery.SerialWriterTests.proposal
    publish=test_general_work_recovery.SerialWriterTests.publish
    prepare=test_general_work_recovery.SerialWriterTests.prepare
    apply=test_general_work_recovery.SerialWriterTests.apply
    bytes=test_general_work_recovery.SerialWriterTests.bytes

    def setUp(self):
        test_general_work_recovery.SerialWriterTests.setUp(self)
        self.git(self.target,"init","-q")
        self.git(self.target,"config","user.name","Fixture")
        self.git(self.target,"config","user.email","fixture@example.invalid")
        self.worker=self.target.parent/"worker"

    def git(self,target,*args):
        if args and args[0] == "commit":
            args = ("-c", "maintenance.auto=false", "-c", "gc.auto=0", *args)
        # Synthetic fixtures retain canonical LF bytes across checkout/clone on Windows.
        config = ["-c", "core.autocrlf=false", "-c", "core.eol=lf"] if sys.platform == "win32" else []
        return subprocess.run(["git",*config,"-C",str(target),*args],capture_output=True,check=True,env=git_environment(),timeout=30).stdout.strip().decode()

    def commit_control(self):
        self.git(self.target,"add",".");self.git(self.target,"commit","-qm","synthetic baseline")
        oid=self.git(self.target,"rev-parse","HEAD")
        self.git(self.target,"branch","-f","retained-base",oid)
        return oid

    def bind(self,proposal,manifest):
        r,_,s,o=proposal;r["execution_context"]["mode"]="isolated-worktree"
        r["result_refs"]["manifest"]={"id":digest(manifest),"sha256":digest(manifest)}
        return r,manifest,s,o

    def baseline(self,operation="start"):
        oid=self.commit_control();tree=fixture_snapshot(self.target)
        m=make_manifest(tree,tree,scope=["a"],base_commit=oid,candidate_commit=oid,base_retention_ref="refs/heads/retained-base",candidate_retention_ref="refs/heads/retained-base")
        p=self.bind(self.proposal(operation,old_intent=self.intent if operation=="rebind" else None),m)
        return p

    def start_and_result(self):
        start=self.baseline();self.publish(start)
        self.git(self.target,"worktree","add","-q","-b","retained-candidate",str(self.worker),start[1]["base_commit"])
        (self.worker/"a").write_bytes(b"worker result\n")
        self.git(self.worker,"add","a");self.git(self.worker,"commit","-qm","synthetic result")
        m=make_manifest(start[1]["base"],fixture_snapshot(self.worker),scope=["a"],base_commit=start[1]["base_commit"],candidate_commit=self.git(self.worker,"rev-parse","HEAD"),base_retention_ref="refs/heads/retained-base",candidate_retention_ref="refs/heads/retained-candidate")
        return self.bind(self.proposal("submit-result"),m)

    def test_worker_checkpoint_cannot_absorb_submitted_result(self):
        from hv2ref.work import work_graph
        submitted=self.start_and_result();graph=self.publish(submitted,worker=self.worker)
        (self.target/"a").write_bytes((self.worker/"a").read_bytes())
        tree=fixture_snapshot(self.target);oid=submitted[1]["candidate_commit"]
        manifest=make_manifest(tree,tree,scope=["a"],base_commit=oid,candidate_commit=oid,base_retention_ref="refs/heads/retained-candidate",candidate_retention_ref="refs/heads/retained-candidate")
        proposal=self.bind(self.proposal("checkpoint"),manifest)
        # Even an unselected revision is rejected by the pure graph reader.
        with self.assertRaisesRegex(ContractError,"worker checkpoint cannot absorb submitted result"):
            work_graph(graph["identity"],graph["revisions"] | {proposal[0]["record_id"]:proposal[0]},graph["decisions"],graph["selections"],graph["manifests"] | {digest(manifest):manifest},graph["current"])
        before=self.bytes()
        with self.assertRaisesRegex(ContractError,"worker checkpoint cannot absorb submitted result"):
            self.publish(proposal)
        self.assertEqual(before,self.bytes())
        self.assertEqual(graph,read_work(self.target,"work-a"))
        # A submitted result can only become a new baseline through a human decision.
        refresh=self.baseline("rebind");self.publish(refresh)
        self.assertEqual(graph["current"],read_work(self.target,"work-a")["current"])
        prepared=self.prepare("rebind",revision_ref=record_ref(refresh[0]))
        refreshed=self.apply(prepared)
        self.assertEqual("active",refreshed["state"])
        self.assertEqual(1,len(refreshed["decisions"]))

    def test_worker_checkpoint_before_submission_remains_available(self):
        baseline=self.baseline();self.publish(baseline)
        checkpoint=self.bind(self.proposal("checkpoint"),baseline[1])
        self.assertEqual("active",self.publish(checkpoint)["state"])

    def test_worker_submit_records_review_without_applying_content(self):
        p=self.start_and_result()
        p[0]["document_refs"]=[{"path":"a","sha256":hashlib.sha256(b"worker result\n").hexdigest(),"required":True,"role":"result"}]
        head=self.git(self.target,"rev-parse","HEAD");index=(self.target/".git/index").read_bytes()
        graph=self.publish(p,worker=self.worker)
        self.assertEqual("review",graph["state"]);self.assertEqual(b"before\n",(self.target/"a").read_bytes())
        self.assertEqual(head,self.git(self.target,"rev-parse","HEAD"));self.assertEqual(index,(self.target/".git/index").read_bytes())
        before=self.bytes();self.assertEqual(graph,self.publish(p,worker=self.worker));self.assertEqual(before,self.bytes())
        before=self.bytes();self.prepare();self.assertEqual(before,self.bytes())

    def test_missing_wrong_dirty_worker_and_control_drift_leave_no_truth(self):
        p=self.start_and_result()
        for worker in [None,self.target]:
            before=self.bytes()
            with self.assertRaises(ContractError):self.publish(p,worker=worker)
            self.assertEqual(before,self.bytes())
        (self.worker/"a").write_bytes(b"uncommitted\n");before=self.bytes()
        with self.assertRaisesRegex(ContractError,"worker bytes"):self.publish(p,worker=self.worker)
        self.assertEqual(before,self.bytes());(self.worker/"a").write_bytes(b"worker result\n")
        (self.target/"a").write_bytes(b"outside drift\n");before=self.bytes()
        with self.assertRaisesRegex(ContractError,"baseline"):self.publish(p,worker=self.worker)
        self.assertEqual(before,self.bytes())

    def test_foreign_missing_and_diverged_worker_refuse_without_control_writes(self):
        p=self.start_and_result()
        foreign=self.target.parent/"foreign"
        self.git(self.target,"clone","--no-hardlinks","-q",str(self.target),str(foreign))
        foreign_worker=self.target.parent/"foreign-worker"
        self.git(foreign,"worktree","add","-q","-b","foreign-linked",str(foreign_worker),"HEAD")
        before=self.bytes()
        with self.assertRaisesRegex(ContractError,"another repository"):
            self.publish(p,worker=foreign_worker)
        self.assertEqual(before,self.bytes())
        moved=self.worker.with_name("worker-moved")
        self.worker.rename(moved)
        before=self.bytes()
        with self.assertRaises(ContractError):self.publish(p,worker=self.worker)
        self.assertEqual(before,self.bytes())
        moved.rename(self.worker)
        self.git(self.worker,"commit","--allow-empty","-qm","diverged worker HEAD")
        before=self.bytes()
        with self.assertRaisesRegex(ContractError,"HEAD differs"):
            self.publish(p,worker=self.worker)
        self.assertEqual(before,self.bytes())

    def test_distinct_worker_proposals_stale_loser_preserves_selected_result(self):
        first=self.start_and_result()
        other=self.target.parent/"competing-worker"
        self.git(self.target,"worktree","add","-q","-b","competing-result",str(other),first[1]["base_commit"])
        (other/"a").write_bytes(b"different worker result\n")
        self.git(other,"add","a");self.git(other,"commit","-qm","competing result")
        manifest=make_manifest(first[1]["base"],fixture_snapshot(other),scope=["a"],base_commit=first[1]["base_commit"],candidate_commit=self.git(other,"rev-parse","HEAD"),base_retention_ref="refs/heads/retained-base",candidate_retention_ref="refs/heads/competing-result")
        second=self.bind(self.proposal("submit-result"),manifest)
        self.assertNotEqual(first[1]["candidate_commit"],second[1]["candidate_commit"])
        self.assertNotEqual(first[1]["result"],second[1]["result"])
        self.assertNotEqual(first[0]["record_id"],second[0]["record_id"])
        self.assertEqual(first[0]["expected_prior_selection"],second[0]["expected_prior_selection"])
        selected=self.publish(first,worker=self.worker);before=self.bytes()
        with self.assertRaisesRegex(ContractError,"stale expected selection"):
            self.publish(second,worker=other)
        self.assertEqual(before,self.bytes())
        self.assertEqual(selected["current"],read_work(self.target,"work-a")["current"])
        self.assertEqual(b"before\n",(self.target/"a").read_bytes())

    def test_required_work_reference_must_match_retained_post(self):
        p=self.start_and_result();p[0]["evidence_refs"]=[{"path":"a","sha256":"0"*64,"required":True,"verification":"control-required"}]
        before=self.bytes()
        with self.assertRaisesRegex(ContractError,"retained post"):self.publish(p,worker=self.worker)
        self.assertEqual(before,self.bytes())

    def test_bound_intent_input_overlap_is_refused(self):
        from hv2ref.intent import WorkspaceIntentStore
        store=WorkspaceIntentStore(self.target,self.store.runtime_check)
        prepared=store.prepare("intent-a",self.intent["revision_ref"],actor="owner",reason="required input",request_id="new-input",observed_at=TIME,document_refs=[{"path":"a","sha256":hashlib.sha256(b"before\n").hexdigest(),"required":True,"role":"plan"}])
        graph=store.apply(prepared["ticket"],confirm_token=prepared["confirm_token"])
        selected=graph["selections"][graph["current"]["selection_ref"]["id"]]
        self.intent={"authority_home_id":"home-a","kind":"intent","id":"intent-a","revision_ref":selected["revision_ref"],"acceptance_ref":selected["acceptance_ref"],"selection_ref":graph["current"]["selection_ref"]}
        p=self.start_and_result();before=self.bytes()
        with self.assertRaisesRegex(ContractError,"required intent input"):self.publish(p,worker=self.worker)
        self.assertEqual(before,self.bytes())

    def test_human_baseline_refresh_crash_drift_resume_and_replay(self):
        self.publish(self.baseline());old=read_work(self.target,"work-a")["current"]
        (self.target/"a").write_bytes(b"new baseline\n");proposal=self.baseline("rebind")
        self.publish(proposal);self.assertEqual(old,read_work(self.target,"work-a")["current"])
        prepared=self.prepare("rebind",revision_ref=record_ref(proposal[0]))
        before_head=self.git(self.target,"rev-parse","HEAD");before_index=(self.target/".git/index").read_bytes()
        with self.assertRaises(InjectedCrash):self.apply(prepared,inject_at="after-decision")
        pending=read_work(self.target,"work-a");self.assertEqual(old,pending["current"]);self.assertEqual(1,len(pending["pending_decisions"]))
        (self.target/"a").write_bytes(b"drift\n");before=self.bytes()
        with self.assertRaises(ContractError):self.apply(prepared)
        self.assertEqual(before,self.bytes());(self.target/"a").write_bytes(b"new baseline\n")
        result=self.apply(prepared);self.assertEqual("active",result["state"]);self.assertEqual([],result["pending_decisions"])
        self.assertEqual(before_head,self.git(self.target,"rev-parse","HEAD"));self.assertEqual(before_index,(self.target/".git/index").read_bytes())
        before=self.bytes();self.assertEqual(result,self.apply(prepared));self.assertEqual(before,self.bytes())


class WorkerApplicationTests(unittest.TestCase):
    # Reuse fixtures without collecting the publication tests a second time.
    setUp=WorkerPublicationTests.setUp
    git=WorkerPublicationTests.git
    commit_control=WorkerPublicationTests.commit_control
    bind=WorkerPublicationTests.bind
    baseline=WorkerPublicationTests.baseline
    start_and_result=WorkerPublicationTests.start_and_result
    accept_intent=WorkerPublicationTests.accept_intent
    proposal=WorkerPublicationTests.proposal
    publish=WorkerPublicationTests.publish
    prepare=WorkerPublicationTests.prepare
    apply=WorkerPublicationTests.apply
    bytes=WorkerPublicationTests.bytes

    def _local_pending_blocks_worker_content(self, point):
        worker_identity=self.identity;self.identity={**worker_identity,"work_id":"local-x"}
        self.publish(self.proposal());self.publish(self.proposal("submit-result"))
        local=self.prepare(request_id="local-accept")
        self.identity=worker_identity;self.result();worker=self.prepare(request_id="worker-accept")
        with self.assertRaises(InjectedCrash):self.apply(local,inject_at=point)
        graph=read_work(self.target,"local-x")
        self.assertTrue(graph["pending_decisions"] or graph["pending_selections"])
        before=self.bytes()
        with self.assertRaisesRegex(ContractError,"pending Work blocks worker content application"):
            self.prepare(request_id="worker-accept-after-local-pending")
        with self.assertRaisesRegex(ContractError,"pending Work blocks worker content application"):
            self.apply(worker)
        self.assertEqual(before,self.bytes())
        self.assertEqual("completed",self.apply(local)["state"])
        self.assertEqual("completed",self.apply(worker)["state"])
        self.assertEqual(b"worker result\n",(self.target/"a").read_bytes())
        # Completed historical replay remains read-only despite later local pending.
        self.identity={**worker_identity,"work_id":"local-later"}
        self.publish(self.proposal());self.publish(self.proposal("submit-result"))
        later=self.prepare(request_id="later-local-accept")
        with self.assertRaises(InjectedCrash):self.apply(later,inject_at=point)
        before=self.bytes();self.assertEqual("completed",self.apply(worker)["state"])
        self.assertEqual(before,self.bytes())
        self.assertEqual("completed",self.apply(later)["state"])

    def test_local_pending_decision_blocks_worker_prepare_and_apply(self):
        self._local_pending_blocks_worker_content("after-decision")

    def test_local_pending_selection_blocks_worker_prepare_and_apply(self):
        self._local_pending_blocks_worker_content("after-selection")

    def test_file_crash_hooks_are_only_worker_acceptance(self):
        proposal=self.proposal()
        for point in ["after-staged-file","after-file"]:
            before=self.bytes()
            with self.assertRaisesRegex(ContractError,"unknown crash point"):self.publish(proposal,inject_at=point)
            self.assertEqual(before,self.bytes())
        self.publish(proposal);(self.target/"a").write_bytes(b"local result\n")
        self.publish(self.proposal("submit-result"));prepared=self.prepare()
        for point in ["after-staged-file","after-file"]:
            before=self.bytes()
            with self.assertRaisesRegex(ContractError,"file crash point requires worker acceptance"):self.apply(prepared,inject_at=point)
            self.assertEqual(before,self.bytes())

    def result(self, *, multiple=False):
        if not multiple:
            proposal=self.start_and_result()
        else:
            (self.target/"b").write_bytes(b"delete me\n")
            start=self.baseline()
            start[0]["scope"]=["a","b","new/run"]
            start=self.bind(start,make_manifest(start[1]["base"],start[1]["result"],scope=start[0]["scope"],base_commit=start[1]["base_commit"],candidate_commit=start[1]["base_commit"],base_retention_ref="refs/heads/retained-base",candidate_retention_ref="refs/heads/retained-base"))
            self.publish(start)
            self.git(self.target,"worktree","add","-q","-b","retained-candidate",str(self.worker),start[1]["base_commit"])
            (self.worker/"a").write_bytes(b"worker result\n")
            (self.worker/"b").unlink();(self.worker/"new").mkdir()
            (self.worker/"new/run").write_bytes(b"executable result\n");(self.worker/"new/run").chmod(0o755)
            self.git(self.worker,"add",".")
            if sys.platform == "win32":
                # Native execute intent is a Git mode, not a chmod side effect.
                self.git(self.worker,"update-index","--chmod=+x","new/run")
            self.git(self.worker,"commit","-qm","synthetic multi-path result")
            if sys.platform == "win32":
                blob=self.git(self.worker,"rev-parse","HEAD:new/run")
                self.git(self.target,"update-index","--add","--cacheinfo","100755,"+blob+",new/run")
                self.assertFalse((self.target/"new/run").exists())
            proposal=self.proposal("submit-result");proposal[0]["scope"]=start[0]["scope"]
            proposal=self.bind(proposal,make_manifest(start[1]["base"],fixture_snapshot(self.worker),scope=start[0]["scope"],base_commit=start[1]["base_commit"],candidate_commit=self.git(self.worker,"rev-parse","HEAD"),base_retention_ref="refs/heads/retained-base",candidate_retention_ref="refs/heads/retained-candidate"))
        proposal[0]["document_refs"]=[{"path":"a","sha256":hashlib.sha256(b"worker result\n").hexdigest(),"required":True,"role":"result"}]
        self.publish(proposal,worker=self.worker)
        return proposal

    def test_accept_applies_add_delete_mode_without_git_changes_and_replay(self):
        proposal=self.result(multiple=True);prepared=self.prepare()
        git_before={str(p.relative_to(self.target/".git")):p.read_bytes() for p in (self.target/".git").rglob("*") if p.is_file()}
        self.assertEqual("completed",self.apply(prepared)["state"])
        self.assertEqual(proposal[1]["result"],fixture_snapshot(self.target))
        self.assertFalse((self.target/"b").exists())
        if sys.platform == "win32":
            self.assertEqual("100755",next(e["mode"] for e in fixture_snapshot(self.target)["entries"] if e["path"] == "new/run"))
        else:
            self.assertTrue((self.target/"new/run").stat().st_mode & 0o100)
        self.assertEqual(git_before,{str(p.relative_to(self.target/".git")):p.read_bytes() for p in (self.target/".git").rglob("*") if p.is_file()})
        (self.target/"a").write_bytes(b"later unrelated bytes\n")
        before=self.bytes();self.assertEqual("completed",self.apply(prepared)["state"]);self.assertEqual(before,self.bytes())

    def test_after_decision_recovers_without_worker_directory(self):
        self.result();prepared=self.prepare()
        with self.assertRaises(InjectedCrash):self.apply(prepared,inject_at="after-decision")
        self.worker.rename(self.worker.with_name("worker-unavailable"))
        self.assertEqual("completed",self.apply(prepared)["state"])

    def test_staged_file_crash_preserves_pre_and_resumes(self):
        self.result();prepared=self.prepare()
        with self.assertRaises(InjectedCrash):self.apply(prepared,inject_at="after-staged-file")
        self.assertEqual(b"before\n",(self.target/"a").read_bytes())
        staged=list((self.target/".hrn/staging").glob("worker-content-*"));self.assertEqual(1,len(staged))
        self.assertEqual("completed",self.apply(prepared)["state"])
        self.assertTrue(staged[0].exists())  # No implicit evidence cleanup.

    def test_mixed_refuses_cancel_outside_drift_and_neither_then_resumes(self):
        proposal=self.result(multiple=True);prepared=self.prepare()
        with self.assertRaises(InjectedCrash):self.apply(prepared,inject_at="after-file")
        graph=read_work(self.target,"work-a");old=graph["decisions"][graph["pending_decisions"][0]]
        self.assertEqual(b"worker result\n",(self.target/"a").read_bytes());self.assertTrue((self.target/"b").exists())
        with self.assertRaisesRegex(ContractError,"every changed path still pre"):self.prepare("reject",supersedes=record_ref(old))
        (self.target/"outside").write_bytes(b"preserve\n");before=self.bytes()
        with self.assertRaisesRegex(ContractError,"outside drift"):self.apply(prepared)
        self.assertEqual(before,self.bytes());(self.target/"outside").unlink()
        (self.target/"b").write_bytes(b"neither\n");before=self.bytes()
        with self.assertRaises(ContractError):self.apply(prepared)
        self.assertEqual(before,self.bytes());(self.target/"b").write_bytes(b"delete me\n")
        self.assertEqual("completed",self.apply(prepared)["state"]);self.assertEqual(proposal[1]["result"],fixture_snapshot(self.target))

    def test_all_pre_cancellation_allows_outside_and_stale_intent_only(self):
        self.result();prepared=self.prepare()
        with self.assertRaises(InjectedCrash):self.apply(prepared,inject_at="after-decision")
        graph=read_work(self.target,"work-a");old=graph["decisions"][graph["pending_decisions"][0]]
        (self.target/"outside").write_bytes(b"preserve\n");self.intent=self.accept_intent(2)
        cancel=self.prepare("reject",supersedes=record_ref(old))
        with self.assertRaises(InjectedCrash):self.apply(cancel,inject_at="after-decision")
        self.assertEqual("rejected",self.apply(cancel)["state"])
        self.assertEqual(b"before\n",(self.target/"a").read_bytes());self.assertEqual(b"preserve\n",(self.target/"outside").read_bytes())
        with self.assertRaises(ContractError):self.apply(prepared)

    def test_selection_crash_refuses_changed_result_then_resumes(self):
        self.result();prepared=self.prepare()
        with self.assertRaises(InjectedCrash):self.apply(prepared,inject_at="after-selection")
        graph=read_work(self.target,"work-a");self.assertEqual("review",graph["state"]);self.assertEqual(1,len(graph["pending_selections"]))
        old=next(iter(graph["decisions"].values()))
        with self.assertRaises(ContractError):self.prepare("reject",supersedes=record_ref(old))
        (self.target/"a").write_bytes(b"before\n");before=self.bytes()
        with self.assertRaisesRegex(ContractError,"not fully applied"):self.apply(prepared)
        self.assertEqual(before,self.bytes());(self.target/"a").write_bytes(b"worker result\n")
        self.assertEqual("completed",self.apply(prepared)["state"])

    def test_new_accept_refuses_preapplied_result_and_lost_ref(self):
        self.result();prepared=self.prepare();(self.target/"a").write_bytes(b"worker result\n");before=self.bytes()
        with self.assertRaisesRegex(ContractError,"exact baseline"):self.apply(prepared)
        self.assertEqual(before,self.bytes());(self.target/"a").write_bytes(b"before\n")
        self.git(self.target,"update-ref","refs/heads/retained-candidate",self.git(self.target,"rev-parse","retained-base"));before=self.bytes()
        with self.assertRaises(ContractError):self.apply(prepared)
        self.assertEqual(before,self.bytes())

    def test_cancel_then_human_refresh_new_result_and_late_ticket_refusal(self):
        self.result();old_ticket=self.prepare()
        with self.assertRaises(InjectedCrash):self.apply(old_ticket,inject_at="after-decision")
        graph=read_work(self.target,"work-a")
        old=graph["decisions"][graph["pending_decisions"][0]]
        self.assertEqual("rejected",self.apply(self.prepare("reject",supersedes=record_ref(old)))["state"])
        refresh=self.baseline("rebind");prior=read_work(self.target,"work-a")["current"]
        self.publish(refresh)
        self.assertEqual(prior,read_work(self.target,"work-a")["current"])
        self.assertEqual("active",self.apply(self.prepare("rebind",revision_ref=record_ref(refresh[0])))["state"])
        worker=self.target.parent/"replacement-worker"
        self.git(self.target,"worktree","add","-q","-b","replacement-result",str(worker),refresh[1]["base_commit"])
        (worker/"a").write_bytes(b"replacement result\n")
        self.git(worker,"add","a");self.git(worker,"commit","-qm","replacement result")
        m=make_manifest(refresh[1]["base"],fixture_snapshot(worker),scope=["a"],base_commit=refresh[1]["base_commit"],candidate_commit=self.git(worker,"rev-parse","HEAD"),base_retention_ref="refs/heads/retained-base",candidate_retention_ref="refs/heads/replacement-result")
        self.publish(self.bind(self.proposal("submit-result"),m),worker=worker)
        git_before=exact_snapshot(self.target/".git")
        self.assertEqual("completed",self.apply(self.prepare(request_id="replacement-accept"))["state"])
        self.assertEqual(b"replacement result\n",(self.target/"a").read_bytes())
        self.assertEqual(git_before,exact_snapshot(self.target/".git"))
        before=self.bytes()
        with self.assertRaises(ContractError):self.apply(old_ticket)
        self.assertEqual(before,self.bytes())

    def test_ignored_added_occupant_and_symlink_ancestor_refuse_writer_unchanged(self):
        (self.target/".gitignore").write_bytes(b"*.cache\n")
        start=self.baseline();scope=["a","dir/new.cache"]
        start_manifest=make_manifest(start[1]["base"],start[1]["result"],scope=scope,base_commit=start[1]["base_commit"],candidate_commit=start[1]["candidate_commit"],base_retention_ref="refs/heads/retained-base",candidate_retention_ref="refs/heads/retained-base")
        start[0]["scope"]=scope;self.publish(self.bind(start,start_manifest))
        self.git(self.target,"worktree","add","-q","-b","retained-candidate",str(self.worker),start_manifest["base_commit"])
        (self.worker/"dir").mkdir();(self.worker/"dir/new.cache").write_bytes(b"accepted addition\n")
        self.git(self.worker,"add","-f","dir/new.cache");self.git(self.worker,"commit","-qm","add ignored candidate")
        result=make_manifest(start_manifest["base"],fixture_snapshot(self.worker),scope=scope,base_commit=start_manifest["base_commit"],candidate_commit=self.git(self.worker,"rev-parse","HEAD"),base_retention_ref="refs/heads/retained-base",candidate_retention_ref="refs/heads/retained-candidate")
        proposal=self.proposal("submit-result");proposal[0]["scope"]=scope
        self.publish(self.bind(proposal,result),worker=self.worker)
        if sys.platform == "win32":
            # Ignored new paths are refused before an application ticket exists.
            before=exact_snapshot(self.target)
            with self.assertRaisesRegex(ContractError,"Windows worker post path is ignored"):
                self.prepare()
            self.assertEqual(before,exact_snapshot(self.target))
            self.assertEqual("review",read_work(self.target,"work-a")["state"])
            attempt_acceptance=self.prepare
        else:
            prepared=self.prepare()
            attempt_acceptance=lambda:self.apply(prepared)
        (self.target/"dir").mkdir();(self.target/"dir/new.cache").write_bytes(b"unreviewed occupant\n")
        before=exact_snapshot(self.target)
        with self.assertRaises(ContractError):attempt_acceptance()
        self.assertEqual(before,exact_snapshot(self.target));self.assertEqual("review",read_work(self.target,"work-a")["state"])
        (self.target/"dir/new.cache").unlink();(self.target/"dir").rmdir()
        outside=self.target.parent/"outside";outside.mkdir();(outside/"new.cache").write_bytes(b"outside evidence\n")
        fixture_directory_link(self.target/"dir", outside)
        before=exact_snapshot(self.target);external=exact_snapshot(outside)
        with self.assertRaises(ContractError):attempt_acceptance()
        self.assertEqual(before,exact_snapshot(self.target));self.assertEqual(external,exact_snapshot(outside))
        self.assertEqual("review",read_work(self.target,"work-a")["state"])

    def test_cancel_rechecks_changed_path_after_prepare(self):
        self.result();prepared=self.prepare()
        with self.assertRaises(InjectedCrash):self.apply(prepared,inject_at="after-decision")
        graph=read_work(self.target,"work-a");old=graph["decisions"][graph["pending_decisions"][0]]
        cancel=self.prepare("reject",supersedes=record_ref(old))
        (self.target/"a").write_bytes(b"worker result\n");before=self.bytes()
        with self.assertRaisesRegex(ContractError,"every changed path still pre"):self.apply(cancel)
        self.assertEqual(before,self.bytes())



class InstalledWorkerPublicationTests(unittest.TestCase):
    setUp=test_productization_safety.ActualWorkspaceInitTests.setUp
    TIME=test_productization_safety.ActualWorkspaceInitTests.TIME
    draft=test_productization_safety.ActualWorkspaceInitTests.draft
    accept_intent=test_productization_safety.ActualWorkspaceInitTests.accept_intent
    installed=test_productization_safety.ActualWorkspaceInitTests.installed
    preview=test_productization_safety.ActualWorkspaceInitTests.preview
    apply_init=test_productization_safety.ActualWorkspaceInitTests.apply_init

    def call(self,command,value=None,*,env=None,launcher=None,expected=0):
        args=[sys.executable,"-I","-B",str(launcher or self.source/"colvia"),*(["--source-checkout"] if launcher is None else []),*map(str,command)]
        p=subprocess.run(args,input=canonical_json_bytes(value) if value is not None else None,capture_output=True,cwd=self.target,env=env,timeout=120)
        if expected is not None:self.assertEqual(expected,p.returncode,(p.stdout+p.stderr).decode(errors="replace"))
        return p

    git=WorkerPublicationTests.git

    def prepare_worker_result(self, *, two_files=False):
        scope=["a","b"] if two_files else ["a"]
        if two_files:(self.target/"b").write_bytes(b"second before\n")
        self.git(self.target,"init","-q");self.git(self.target,"config","user.name","Fixture");self.git(self.target,"config","user.email","fixture@example.invalid")
        self.apply_init(self.preview());intent=self.accept_intent()
        self.git(self.target,"add",".")
        if sys.platform == "win32":
            # Preserve the existing commit oracle's managed-launcher mode explicitly.
            self.git(self.target,"update-index","--chmod=+x","colvia")
        self.git(self.target,"commit","-qm","synthetic installed baseline")
        oid=self.git(self.target,"rev-parse","HEAD");self.git(self.target,"branch","retained-base",oid)
        from hv2ref.product import verify_workspace_product
        sha=verify_workspace_product(self.target)["launcher_sha256"];tree=snapshot(self.target,verified_launcher_sha256=sha, verified_inventory_id=verified_inventory_id(self.target))
        identity={"record_type":"work-identity","schema_version":1,"authority_home_id":"home-a","work_id":"work-a","work_type":"change","created_at":TIME,"acceptance_authority":"owner","lineage":None}
        m=make_manifest(tree,tree,scope=scope,base_commit=oid,candidate_commit=oid,base_retention_ref="refs/heads/retained-base",candidate_retention_ref="refs/heads/retained-base")
        r={"record_type":"work-revision","schema_version":1,"authority_home_id":"home-a","work_id":"work-a","record_id":"start","observed_at":TIME,"observed_scope":[],"unavailable_scope":[],"author":"agent","operation":"start","expected_prior_selection":None,"intent_ref":intent,"scope":scope,"document_refs":[],"evidence_refs":[],"result_refs":{"manifest":{"id":digest(m),"sha256":digest(m)}},"progress":"active","next_action":"compute","relations":[],"rebind_from":None,"execution_context":{"mode":"isolated-worktree","attempt_id":"attempt-a"}}
        request={"identity":identity,"revision":r,"manifest":m,"selection_id":"start-s","operation_id":"start-op"}
        graph=json.loads(self.installed(["work","publish"],request).stdout)
        worker=self.base/"worker";self.git(self.target,"worktree","add","-q","-b","candidate",str(worker),oid)
        (worker/"a").write_bytes(b"installed worker result\n")
        if two_files:(worker/"b").write_bytes(b"second result\n")
        self.git(worker,"add",*scope);self.git(worker,"commit","-qm","synthetic installed result")
        m=make_manifest(tree,snapshot(worker,verified_launcher_sha256=sha, verified_inventory_id=verified_inventory_id(self.target)),scope=scope,base_commit=oid,candidate_commit=self.git(worker,"rev-parse","HEAD"),base_retention_ref="refs/heads/retained-base",candidate_retention_ref="refs/heads/candidate")
        r=copy.deepcopy(r);r.update(record_id="result",operation="submit-result",expected_prior_selection=graph["current"]["selection_ref"],progress="review",result_refs={"manifest":{"id":digest(m),"sha256":digest(m)}})
        request={"identity":identity,"revision":r,"manifest":m,"selection_id":"result-s","operation_id":"result-op"}
        before=exact_snapshot(self.target)
        refused=self.call(["work","publish","--target",self.target,"--worker",worker],request,launcher=worker/"colvia",expected=65)
        self.assertEqual(before,exact_snapshot(self.target))
        graph=json.loads(self.installed(["work","publish","--worker",worker],request).stdout)
        self.assertEqual("review",graph["state"]);self.assertEqual(b"before\n",(self.target/"a").read_bytes())
        prepared=json.loads(self.installed(["work","prepare"],{"work_id":"work-a","action":"accept","actor":"owner","reason":"installed worker result","request_id":"accept-worker","observed_at":TIME,"revision_ref":None,"supersedes":None}).stdout)
        import html,re
        before=exact_snapshot(self.target)
        review=self.installed(["view","work","work-a"]).stdout.decode()
        review+='\n'+self.installed(["view","confirmation","--input","-"],prepared["ticket"]).stdout.decode()
        review=re.sub(r"\\([\\`*_{}\[\]()!|#~])",r"\1",html.unescape(review))
        self.assertEqual(before,exact_snapshot(self.target))
        self.assertIn("control matches baseline; candidate is not yet applied",review)
        self.assertIn("whole_base_matches: True",review)
        self.assertNotIn("local Work decision required",review)

        return prepared

    def test_installed_checkpoint_cannot_absorb_submitted_worker_result(self):
        self.prepare_worker_result();graph=read_work(self.target,"work-a")
        selected=graph["selections"][graph["current"]["selection_ref"]["id"]]
        revision=copy.deepcopy(graph["revisions"][selected["revision_ref"]["id"]])
        prior=graph["manifests"][revision["result_refs"]["manifest"]["id"]]
        (self.target/"a").write_bytes((self.base/"worker/a").read_bytes())
        from hv2ref.product import verify_workspace_product
        tree=snapshot(self.target,verified_launcher_sha256=verify_workspace_product(self.target)["launcher_sha256"], verified_inventory_id=verified_inventory_id(self.target))
        oid=prior["candidate_commit"]
        manifest=make_manifest(tree,tree,scope=["a"],base_commit=oid,candidate_commit=oid,base_retention_ref="refs/heads/candidate",candidate_retention_ref="refs/heads/candidate")
        revision.update(record_id="checkpoint",operation="checkpoint",expected_prior_selection=graph["current"]["selection_ref"],progress="active",result_refs={"manifest":{"id":digest(manifest),"sha256":digest(manifest)}})
        request={"identity":graph["identity"],"revision":revision,"manifest":manifest,"selection_id":"checkpoint-s","operation_id":"checkpoint-op"}
        before=exact_snapshot(self.target)
        refused=self.installed(["work","publish"],request,expected=65)
        self.assertIn(b"worker checkpoint cannot absorb submitted result",refused.stdout)
        self.assertEqual(b"",refused.stderr)
        self.assertEqual(before,exact_snapshot(self.target))

    def test_installed_local_pending_protects_worker_apply_and_view(self):
        worker=self.prepare_worker_result();graph=read_work(self.target,"work-a")
        from hv2ref.product import verify_workspace_product
        from hv2ref.work import WorkStore
        tree=snapshot(self.target,verified_launcher_sha256=verify_workspace_product(self.target)["launcher_sha256"], verified_inventory_id=verified_inventory_id(self.target))
        identity={**graph["identity"],"work_id":"local-x"}
        revision=copy.deepcopy(graph["revisions"]["start"])
        manifest=make_manifest(tree,tree,scope=["a"])
        revision.update(work_id="local-x",record_id="local-start",execution_context={"mode":"local","attempt_id":"local-a"},result_refs={"manifest":{"id":digest(manifest),"sha256":digest(manifest)}})
        request={"identity":identity,"revision":revision,"manifest":manifest,"selection_id":"local-start-s","operation_id":"local-start-op"}
        local_graph=json.loads(self.installed(["work","publish"],request).stdout)
        revision.update(record_id="local-result",operation="submit-result",progress="review",expected_prior_selection=local_graph["current"]["selection_ref"])
        request.update(selection_id="local-result-s",operation_id="local-result-op")
        self.installed(["work","publish"],request)
        local=json.loads(self.installed(["work","prepare"],{"work_id":"local-x","action":"accept","actor":"owner","reason":"local result","request_id":"local-accept","observed_at":TIME,"revision_ref":None,"supersedes":None}).stdout)
        # Controlled prefix via verified-product fixture seam; subsequent checks use installed CLI.
        with self.assertRaises(InjectedCrash):
            WorkStore(self.target,lambda target:(lambda observed:{"binding_ref":observed["binding_ref"],"launcher_sha256":observed["launcher_sha256"],"inventory_id":observed["inventory"]["inventory_id"]})(verify_workspace_product(target))).apply(local["ticket"],confirm_token=local["confirm_token"],inject_at="after-selection")
        self.assertTrue(read_work(self.target,"local-x")["pending_selections"])
        before=exact_snapshot(self.target)
        refused=self.installed(["work","apply","--confirm",worker["confirm_token"]],worker["ticket"],expected=65)
        self.assertIn(b"pending Work blocks worker content application",refused.stdout)
        self.assertEqual(b"",refused.stderr)
        refused=self.installed(["work","prepare"],{"work_id":"work-a","action":"accept","actor":"owner","reason":"retry","request_id":"worker-retry","observed_at":TIME,"revision_ref":None,"supersedes":None},expected=65)
        self.assertIn(b"pending Work blocks worker content application",refused.stdout)
        self.assertEqual(b"",refused.stderr)
        rendered=self.installed(["view","confirmation","--input","-"],worker["ticket"],expected=14).stdout
        self.assertIn(b"pending Work blocks worker content application",rendered)
        self.assertEqual(before,exact_snapshot(self.target))
        self.installed(["work","apply","--confirm",local["confirm_token"]],local["ticket"])
        complete=json.loads(self.installed(["work","apply","--confirm",worker["confirm_token"]],worker["ticket"]).stdout)
        self.assertEqual("completed",complete["state"])

    def test_installed_entry_publishes_worker_result_and_worker_entry_refuses(self):
        prepared=self.prepare_worker_result()
        graph=json.loads(self.installed(["work","apply","--confirm",prepared["confirm_token"]],prepared["ticket"]).stdout)
        self.assertEqual("completed",graph["state"]);self.assertEqual(b"installed worker result\n",(self.target/"a").read_bytes())



if __name__ == "__main__":
    unittest.main()
