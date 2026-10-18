"""Internal serial writer fixtures; installed runtime verifier is an explicit double."""
from __future__ import annotations
import copy
import hashlib
from pathlib import Path
import tempfile
import unittest

from hv2ref.errors import ContractError, InjectedCrash
from hv2ref.jsonio import canonical_json_bytes
from hv2ref.workspace import bootstrap_root, target_fingerprint
from hv2ref.work import WorkStore, make_manifest, read_work, record_ref, snapshot, validate_work_record
from hv2ref.intent import read_workspace_intent

TIME = "2026-01-01T00:00:00Z"


def digest(value):
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def put(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_json_bytes(value))


class SerialWriterTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="serial-records-")
        self.addCleanup(self.temp.cleanup)
        self.target = Path(self.temp.name).resolve() / "project"
        self.target.mkdir()
        (self.target / "a").write_bytes(b"before\n")
        fmt = {"record_type":"workspace-format","format_version":1,"authority_home_id":"home-a","created_at":TIME,"lineage":None}
        self.binding = {"id":"binding-a","sha256":"b"*64}
        plan = {"record_type":"lifecycle-plan","schema_version":1,"operation_id":"init-a","action":"init","target_fingerprint":target_fingerprint(self.target),"authority_home_id":"home-a","expected_binding_ref":None,"candidate_release":{"id":"product-release-"+"a"*24,"sha256":"a"*64,"inventory_id":"human-1"},"format_sha256":digest(fmt),"truth_refs":[],"remove":[],"preserve":[],"created_at":TIME}
        bootstrap_root(self.target, plan, fmt)
        # This double is deliberately not proof of installed release verification.
        self.store = WorkStore(self.target, lambda target: {"binding_ref":copy.deepcopy(self.binding),"launcher_sha256":None})
        self.intent = self.accept_intent(1)
        self.identity = {"record_type":"work-identity","schema_version":1,"authority_home_id":"home-a","work_id":"work-a","work_type":"change","created_at":TIME,"acceptance_authority":"owner","lineage":None}
        self.serial = 0

    def accept_intent(self, n, *, authority="owner"):
        home = self.target / ".hrn/intents/intent-a"
        base = {"schema_version":1,"authority_home_id":"home-a","intent_id":"intent-a"}
        put(home / "identity.json", {**base,"record_type":"intent-identity"})
        previous = getattr(self, "intent", None)
        draft = {**base,"record_type":"intent-draft","revision_id":f"draft-{n}","sequence":n,"prior_revision_ref":previous["revision_ref"] if previous else None,"actor":"agent","acceptance_authority":authority,"observed_at":TIME,"facets":{k:{"status":"known","value":"fixture"} for k in ["acceptance_oracle","destination","expected_outcome","forbidden_scope","goal","scope"]},"gaps":[],"statements":[],"route":"direct-entry"}
        put(home / "drafts" / (draft["revision_id"]+".json"), draft)
        ticket = {"record_type":"confirmation-ticket","schema_version":1,"authority_home_id":"home-a","object":{"authority_home_id":"home-a","kind":"intent","id":"intent-a"},"action":"accept","actor":authority,"reason":"fixture acceptance","request_id":f"intent-request-{n}","observed_at":TIME,"target_fingerprint":target_fingerprint(self.target),"target_revision_ref":record_ref(draft,"revision_id"),"expected_selection_ref":previous["selection_ref"] if previous else None,"intent_ref":None,"product_binding_ref":self.binding,"document_refs":[],"evidence_refs":[],"execution_mode":None,"supersedes_decision_ref":None}
        acceptance = {**base,"record_type":"intent-acceptance","acceptance_id":"acceptance-"+digest(ticket),"confirmation":ticket}
        selection = {**base,"record_type":"intent-selection","selection_id":f"intent-selection-{n}","revision_ref":record_ref(draft,"revision_id"),"acceptance_ref":record_ref(acceptance,"acceptance_id"),"prior_selection_ref":previous["selection_ref"] if previous else None}
        put(home / "acceptances" / (acceptance["acceptance_id"]+".json"), acceptance)
        put(home / "selections" / (selection["selection_id"]+".json"), selection)
        put(home / "current.json", {**base,"record_type":"intent-current","selection_ref":record_ref(selection,"selection_id")})
        return {"authority_home_id":"home-a","kind":"intent","id":"intent-a","revision_ref":selection["revision_ref"],"acceptance_ref":selection["acceptance_ref"],"selection_ref":record_ref(selection,"selection_id")}

    def proposal(self, operation="start", *, intent=None, old_intent=None):
        self.serial += 1
        try:
            graph = read_work(self.target, self.identity["work_id"])
        except ContractError:
            graph = None
        prior = graph["current"]["selection_ref"] if graph and graph["current"] else None
        tree = snapshot(self.target)
        if operation == "submit-result":
            old = graph["revisions"][graph["selections"][prior["id"]]["revision_ref"]["id"]]
            base = graph["manifests"][old["result_refs"]["manifest"]["id"]]["result"]
        else:
            base = tree
        manifest = make_manifest(base, tree, scope=["a"])
        revision = {"record_type":"work-revision","schema_version":1,"authority_home_id":"home-a","work_id":self.identity["work_id"],"record_id":f"revision-{self.serial}","observed_at":TIME,"observed_scope":[],"unavailable_scope":[],"author":"agent","operation":operation,"expected_prior_selection":prior,"intent_ref":intent or self.intent,"scope":["a"],"document_refs":[],"evidence_refs":[],"result_refs":{"manifest":{"id":digest(manifest),"sha256":digest(manifest)}},"progress":"review" if operation=="submit-result" else "active","next_action":"owner review" if operation=="submit-result" else "edit","relations":[],"rebind_from":old_intent,"execution_context":{"mode":"local","attempt_id":f"attempt-{self.serial}"}}
        return revision, manifest, f"selection-{self.serial}", f"operation-{self.serial}"

    def publish(self, proposal, **kwargs):
        r,m,s,o = proposal
        return self.store.publish(self.identity,r,m,selection_id=s,operation_id=o,**kwargs)

    def submitted(self):
        self.publish(self.proposal())
        (self.target / "a").write_bytes(b"after\n")
        return self.publish(self.proposal("submit-result"))

    def prepare(self, action="accept", **kwargs):
        return self.store.prepare(self.identity["work_id"],action=action,actor="owner",reason="fixture decision",request_id=kwargs.pop("request_id", "human-"+action),observed_at=TIME,**kwargs)

    def apply(self, prepared, **kwargs):
        return self.store.apply(prepared["ticket"],confirm_token=prepared["confirm_token"],**kwargs)

    def bytes(self):
        return {str(p.relative_to(self.target)):p.read_bytes() for p in self.target.rglob("*") if p.is_file() and not p.is_symlink()}

    def test_port_parallel_scope_is_exact_files_without_claim_normalization(self):
        tree = snapshot(self.target)
        before = self.bytes()
        invalid = [[""], ["/absolute"], ["."], ["src/../escape"], ["src\\alias"], [".git/config"], [".hrn/format.json"], ["cafe\u0301.txt"], ["src/Foo", "src/foo"], ["src", "src/module"], ["a", "a"]]
        messages = ["invalid project path", "path must be literal relative NFC", "path must be literal relative NFC", "path must be literal relative NFC", "invalid project path", "metadata path cannot be project content", "metadata path cannot be project content", "path must be literal relative NFC", "case alias in project paths", "file is also a parent directory", "duplicate path"]
        for scope, message in zip(invalid, messages, strict=True):
            with self.subTest(scope=scope), self.assertRaises(ContractError) as caught:
                make_manifest(tree, tree, scope=scope)
            self.assertEqual(caught.exception.code, "HV2-WORK-CONTENT")
            self.assertEqual(caught.exception.message, message)
            self.assertEqual(self.bytes(), before)
        self.assertEqual(make_manifest(tree, tree, scope=[])["changes"], [])
        (self.target / "a").write_bytes(b"changed\n")
        with self.assertRaises(ContractError) as caught:
            make_manifest(tree, snapshot(self.target), scope=[])
        self.assertEqual(caught.exception.code, "HV2-WORK-CONTENT")
        self.assertEqual(caught.exception.message, "result changes exceed exact file scope")

    def test_port_parallel_competing_serial_proposals_and_retries_preserve_truth(self):
        import subprocess
        def git(*args):
            if args and args[0] == "commit":
                args = ("-c", "maintenance.auto=false", "-c", "gc.auto=0", *args)
            result = subprocess.run(["git", *args], cwd=self.target, capture_output=True, check=True)
            return result.stdout
        git("init", "-b", "main"); git("config", "user.name", "Fixture"); git("config", "user.email", "fixture@example.invalid")
        git("add", "a"); git("commit", "-m", "fixture")
        index = git("write-tree")
        self.publish(self.proposal())
        first = self.proposal("checkpoint")
        second = self.proposal("checkpoint")
        self.assertEqual(first[0]["expected_prior_selection"], second[0]["expected_prior_selection"])
        selected = self.publish(first)
        before = self.bytes()
        self.assertEqual(self.publish(first)["current"], selected["current"])
        self.assertEqual(before, self.bytes())
        for observed in (TIME, "2026-01-02T00:00:00Z"):
            second[0]["observed_at"] = observed
            with self.assertRaises(ContractError) as caught:
                self.publish(second)
            self.assertEqual(caught.exception.code, "HV2-WORK-RECORD")
            self.assertIn("stale expected selection", str(caught.exception))
            self.assertEqual(before, self.bytes())
            self.assertEqual(read_work(self.target, "work-a")["current"], selected["current"])
            self.assertEqual(git("write-tree"), index)
            self.assertEqual((self.target / "a").read_bytes(), b"before\n")

    def test_port_parallel_history_read_is_separate_from_live_symlink_validation(self):
        self.submitted()
        prepared = self.prepare()
        original = read_work(self.target, "work-a")["current"]
        outside = self.target.parent / "outside.txt"
        outside.write_bytes(b"outside remains\n")
        (self.target / "later-link").symlink_to(outside)
        before = self.bytes()
        self.assertEqual(read_work(self.target, "work-a")["current"], original)
        for operation in (self.prepare, lambda: self.apply(prepared)):
            with self.assertRaises(ContractError) as caught:
                operation()
            self.assertEqual(caught.exception.code, "HV2-WORK-CONTENT")
            self.assertEqual(before, self.bytes())
            self.assertTrue((self.target / "later-link").is_symlink())
            self.assertEqual(outside.read_bytes(), b"outside remains\n")

    def test_port_parallel_immutable_io_error_is_not_reclassified_as_conflict(self):
        from unittest import mock
        import hv2ref.work as module
        self.publish(self.proposal())
        proposal = self.proposal("checkpoint")
        before = self.bytes()
        original = module._publish_immutable
        injected = ContractError("HV2-TEST-IO", "unrelated immutable publication failure")
        def publish(path, value):
            if path.name == proposal[0]["record_id"] + ".json":
                raise injected
            return original(path, value)
        with mock.patch.object(module, "_publish_immutable", side_effect=publish):
            with self.assertRaises(ContractError) as caught:
                self.publish(proposal)
        self.assertIs(caught.exception, injected)
        self.assertEqual(before, self.bytes())
        self.assertNotIn(proposal[0]["record_id"], read_work(self.target, "work-a")["revisions"])

    def test_port_parallel_rebind_keeps_history_and_human_authority(self):
        graph = self.publish(self.proposal())
        old_intent = self.intent
        old_refs = copy.deepcopy(graph["revisions"])
        self.intent = self.accept_intent(2)
        proposal = self.proposal("rebind", old_intent=old_intent)
        pending = self.publish(proposal)
        self.assertEqual(pending["current"], graph["current"])
        self.assertIn(proposal[0]["record_id"], pending["orphan_revisions"])
        before = self.bytes()
        with self.assertRaises(ContractError) as caught:
            self.store.prepare("work-a", action="rebind", actor="agent", reason="wrong actor", request_id="bad-rebind", observed_at=TIME, revision_ref=record_ref(proposal[0]))
        self.assertEqual(caught.exception.code, "HV2-WORK-RECORD")
        self.assertEqual(caught.exception.message, "no grant for this Work")
        self.assertEqual(self.bytes(), before)
        confirmed = self.apply(self.prepare("rebind", revision_ref=record_ref(proposal[0])))
        self.assertEqual(confirmed["identity"]["acceptance_authority"], "owner")
        for key, value in old_refs.items():
            self.assertEqual(confirmed["revisions"][key], value)
        before = self.bytes()
        self.identity["acceptance_authority"] = "agent"
        with self.assertRaises(ContractError) as caught:
            self.publish(self.proposal("checkpoint"))
        self.assertEqual(caught.exception.code, "HV2-WORK-RECORD")
        self.assertIn("immutable Work identity mismatch", str(caught.exception))
        self.assertEqual(self.bytes(), before)

    def test_port_parallel_exact_accept_replay_and_stale_competitor(self):
        self.submitted()
        first = self.prepare(request_id="winner")
        second = self.prepare(request_id="competitor")
        completed = self.apply(first)
        selected = completed["selections"][completed["current"]["selection_ref"]["id"]]
        self.assertEqual(selected["revision_ref"], first["ticket"]["target_revision_ref"])
        self.assertEqual(completed["decisions"][selected["decision_ref"]["id"]]["confirmation"], first["ticket"])
        before = self.bytes()
        self.assertEqual(self.apply(first)["current"], completed["current"])
        self.assertEqual(before, self.bytes())
        with self.assertRaises(ContractError) as caught:
            self.apply(second)
        self.assertEqual(caught.exception.code, "HV2-WORK-RECORD")
        self.assertIn("stale confirmation selection", str(caught.exception))
        self.assertEqual(before, self.bytes())

    def test_port_parallel_unknown_authority_member_is_preserved_and_refused(self):
        self.publish(self.proposal())
        home = self.target / ".hrn/work/work-a"
        for relative in ("rogue.json", "revisions/rogue.json"):
            with self.subTest(relative=relative):
                extra = home / relative
                extra.write_bytes(b"{}\n")
                before = self.bytes()
                with self.assertRaises(ContractError) as caught:
                    read_work(self.target, "work-a")
                self.assertEqual(caught.exception.code, "HV2-WORK-RECORD")
                self.assertEqual(caught.exception.message, "unknown object member: rogue.json" if relative == "rogue.json" else "unknown Work record type")
                self.assertEqual(before, self.bytes())
                extra.unlink()

    def test_port_parallel_changed_manifest_residual_and_exact_retry(self):
        from unittest import mock
        import hv2ref.work as module
        first = self.publish(self.proposal())
        (self.target / "a").write_bytes(b"new result\n")
        proposal = self.proposal("submit-result")
        before = self.bytes()
        original = module._publish_immutable
        injected = ContractError("HV2-TEST-IO", "revision publication failed after manifest")
        def publish(path, value):
            if path.name == proposal[0]["record_id"] + ".json":
                raise injected
            return original(path, value)
        with mock.patch.object(module, "_publish_immutable", side_effect=publish):
            with self.assertRaises(ContractError) as caught:
                self.publish(proposal)
        self.assertIs(caught.exception, injected)
        after = self.bytes()
        self.assertEqual({key:after[key] for key in before}, before)
        ref = proposal[0]["result_refs"]["manifest"]
        self.assertEqual(set(after) - set(before), {".hrn/work/work-a/results/" + ref["id"] + ".json"})
        self.assertEqual(first["current"], read_work(self.target, "work-a")["current"])
        recovered = self.publish(proposal)
        self.assertEqual("review", recovered["state"])
        self.assertEqual(proposal[0], recovered["revisions"][proposal[0]["record_id"]])
        self.assertEqual(proposal[1], recovered["manifests"][ref["id"]])

    def test_complete_local_cycle_and_no_project_rewrite(self):
        self.submitted()
        prepared = self.prepare()
        before = (self.target / "a").read_bytes()
        graph = self.apply(prepared)
        self.assertEqual(graph["state"], "completed")
        self.assertEqual(before, (self.target / "a").read_bytes())
        self.assertEqual(graph["pending_decisions"], [])
        self.assertEqual(self.apply(prepared)["current"], graph["current"])

    def test_prepare_and_reader_are_read_only(self):
        self.submitted(); before=self.bytes()
        self.prepare(); read_work(self.target,"work-a")
        self.assertEqual(before,self.bytes())

    def test_agent_cannot_set_completion_or_unknown_fields(self):
        proposal=self.proposal()
        for field,value in [("progress","completed"),("outcome","accept"),("schema_version",True)]:
            bad=copy.deepcopy(proposal[0]);bad[field]=value
            with self.assertRaises(ContractError):validate_work_record(bad)

    def test_accept_requires_selected_submitted_result(self):
        self.publish(self.proposal())
        with self.assertRaises(ContractError):self.prepare()

    def test_exact_revision_hash_binds_expected_prior_and_metadata(self):
        self.submitted(); prepared=self.prepare()
        home=self.target/".hrn/work/work-a/revisions/revision-2.json"
        import json
        r=json.loads(home.read_text());r["next_action"]="different reviewed meaning";put(home,r)
        with self.assertRaises(ContractError):self.apply(prepared)

    def test_wrong_actor_token_and_target_are_refused(self):
        self.submitted();prepared=self.prepare()
        with self.assertRaises(ContractError):self.store.apply(prepared["ticket"],confirm_token="0"*16)
        for field,value in [("actor","agent"),("target_fingerprint","0"*64)]:
            ticket={**prepared["ticket"],field:value}
            with self.assertRaises(ContractError):self.store.apply(ticket,confirm_token=digest(ticket)[:16])

    def test_outside_content_drift_blocks_accept(self):
        self.submitted();prepared=self.prepare();(self.target/"outside").write_text("new")
        with self.assertRaises(ContractError):self.apply(prepared)
        self.assertEqual(read_work(self.target,"work-a")["state"],"review")

    def test_binding_changed_after_prepare_refuses_before_decision(self):
        self.submitted();prepared=self.prepare();self.binding={"id":"binding-b","sha256":"c"*64}
        with self.assertRaises(ContractError):self.apply(prepared)
        self.assertEqual(read_work(self.target,"work-a")["decisions"],{})

    def test_stale_intent_refuses_accept_and_new_agent_write(self):
        self.submitted();prepared=self.prepare();self.intent=self.accept_intent(2)
        with self.assertRaises(ContractError):self.apply(prepared)
        with self.assertRaises(ContractError):self.publish(self.proposal("checkpoint"))

    def test_pending_accept_can_cancel_after_result_and_intent_drift(self):
        self.submitted();prepared=self.prepare()
        with self.assertRaises(InjectedCrash):self.apply(prepared,inject_at="after-decision")
        (self.target/"a").write_bytes(b"drift\n")
        self.intent=self.accept_intent(2)
        graph=read_work(self.target,"work-a")
        old=graph["decisions"][graph["pending_decisions"][0]]
        cancel=self.prepare("reject",supersedes=record_ref(old))
        result=self.apply(cancel)
        self.assertEqual(result["state"],"rejected")
        self.assertEqual(result["pending_decisions"],[])
        self.assertEqual((self.target/"a").read_bytes(),b"drift\n")
        with self.assertRaises(ContractError):self.apply(prepared)

    def test_second_pending_accept_and_cancellation_chain_are_bounded(self):
        self.submitted();prepared=self.prepare()
        with self.assertRaises(InjectedCrash):self.apply(prepared,inject_at="after-decision")
        with self.assertRaises(ContractError):self.prepare(request_id="different")
        graph=read_work(self.target,"work-a");old=next(iter(graph["decisions"].values()))
        cancel=self.prepare("reject",supersedes=record_ref(old))
        with self.assertRaises(InjectedCrash):self.apply(cancel,inject_at="after-decision")
        with self.assertRaises(ContractError):self.prepare("reject",request_id="another-cancel",supersedes=record_ref(old))
        self.assertEqual(self.apply(cancel)["state"],"rejected")

    def test_decision_crash_prefixes_resume_without_duplicate_decisions(self):
        for point in ["after-decision","after-selection","after-staged-current","after-current"]:
            with self.subTest(point=point):
                # A distinct Work keeps previous evidence intact.
                self.identity={**self.identity,"work_id":"work-"+point}
                self.submitted();prepared=self.prepare()
                with self.assertRaises(InjectedCrash):self.apply(prepared,inject_at=point)
                graph=self.apply(prepared)
                self.assertEqual(graph["state"],"completed")
                self.assertEqual(len(graph["decisions"]),1)
                self.assertEqual(len(graph["selections"]),3)

    def test_agent_complete_file_prefixes_resume_exactly(self):
        for point in ["after-staged-identity","after-home","after-manifest","after-revision","after-selection","after-staged-current","after-current"]:
            with self.subTest(point=point):
                self.identity={**self.identity,"work_id":"work-"+point}
                proposal=self.proposal()
                with self.assertRaises(InjectedCrash):self.publish(proposal,inject_at=point)
                graph=self.publish(proposal)
                self.assertEqual(graph["state"],"active")
                self.assertEqual(len(graph["revisions"]),1)
                self.assertEqual(len(graph["selections"]),1)

    def test_reject_requires_rework_and_completed_requires_revoke(self):
        self.submitted();self.apply(self.prepare("reject"))
        with self.assertRaises(ContractError):self.prepare()
        with self.assertRaises(ContractError):self.publish(self.proposal("submit-result"))
        self.publish(self.proposal("rework"));self.publish(self.proposal("submit-result"))
        accepted=self.prepare(request_id="new-accept");self.apply(accepted)
        with self.assertRaises(ContractError):self.publish(self.proposal("checkpoint"))
        graph=read_work(self.target,"work-a")
        current=graph["selections"][graph["current"]["selection_ref"]["id"]]
        revoke=self.prepare("revoke",supersedes=current["decision_ref"])
        self.assertEqual(self.apply(revoke)["state"],"revoked")
        old_current=read_work(self.target,"work-a")["current"]
        self.assertEqual(self.apply(accepted)["current"],old_current)
        self.assertEqual(self.publish(self.proposal("rework"))["state"],"active")

    def test_rebind_needs_human_and_preserves_authority(self):
        self.publish(self.proposal());old=self.intent;self.intent=self.accept_intent(2)
        proposal=self.proposal("rebind",old_intent=old)
        graph=self.publish(proposal)
        self.assertIn(proposal[0]["record_id"],graph["orphan_revisions"])
        prepared=self.prepare("rebind",revision_ref=record_ref(proposal[0]))
        self.assertEqual(self.apply(prepared)["state"],"active")
        self.publish(self.proposal("submit-result"))
        self.assertEqual(self.apply(self.prepare())["state"],"completed")

    def test_identity_cannot_claim_another_acceptance_authority(self):
        self.identity["acceptance_authority"]="agent"
        with self.assertRaises(ContractError):self.publish(self.proposal())

    def test_all_records_are_validated_not_only_current_chain(self):
        self.submitted();home=self.target/".hrn/work/work-a/revisions/orphan.json"
        put(home,{"record_type":"work-revision","schema_version":True})
        with self.assertRaises(ContractError):read_work(self.target,"work-a")

    def test_unknown_torn_and_symlink_record_members_preserve_bytes(self):
        self.publish(self.proposal());home=self.target/".hrn/work/work-a"
        extra=home/".DS_Store";extra.write_bytes(b"keep")
        with self.assertRaises(ContractError):read_work(self.target,"work-a")
        self.assertEqual(extra.read_bytes(),b"keep");extra.unlink()
        current=home/"current.json";current.write_bytes(b"")
        with self.assertRaises(ContractError):read_work(self.target,"work-a")
        current.unlink();current.symlink_to(self.target/"a")
        with self.assertRaises(ContractError):read_work(self.target,"work-a")
        self.assertEqual((self.target/"a").read_bytes(),b"before\n")

    def test_intent_authority_gap_and_orphan_acceptance_are_checked(self):
        home=self.target/".hrn/intents/intent-a"
        import json
        draft=home/"drafts/draft-1.json";value=json.loads(draft.read_text())
        value["gaps"]=[{"gap_id":"gap-a","material":True,"owner":"owner","status":"unresolved","depends_on":[]}]
        value["route"]="bounded-clarification";put(draft,value)
        with self.assertRaises(ContractError):read_workspace_intent(self.target,"intent-a",self.intent)

    def test_worker_write_with_local_manifest_remains_refused(self):
        proposal=list(self.proposal());proposal[0]["execution_context"]["mode"]="isolated-worktree"
        with self.assertRaises(ContractError):self.publish(proposal)

    def test_prepare_refuses_live_content_drift_without_ticket(self):
        self.submitted();(self.target/"a").write_bytes(b"not reviewed\n")
        with self.assertRaises(ContractError):self.prepare()

    def test_new_selection_fork_is_not_latest_wins(self):
        graph=self.publish(self.proposal())
        selected=copy.deepcopy(next(iter(graph["selections"].values())))
        selected["record_id"]="fork";selected["operation_id"]="fork-operation"
        put(self.target/".hrn/work/work-a/selections/fork.json",selected)
        with self.assertRaises(ContractError):read_work(self.target,"work-a")

    def test_rolling_current_back_cannot_hide_multiple_publications(self):
        graph=self.submitted();old=next(s for s in graph["selections"].values() if s["parent_selection_ref"] is None)
        self.apply(self.prepare())
        selector={"record_type":"work-current","schema_version":1,"authority_home_id":"home-a","work_id":"work-a","selection_ref":record_ref(old)}
        put(self.target/".hrn/work/work-a/current.json",selector)
        with self.assertRaises(ContractError):read_work(self.target,"work-a")

    def test_relation_cycle_and_nonexistent_target_refuse_before_writes(self):
        self.publish(self.proposal())
        a=copy.deepcopy(self.identity);self.identity={**a,"work_id":"work-b"}
        proposal=self.proposal();proposal[0]["relations"]=[{"relation":"depends_on","target":{"authority_home_id":"home-a","kind":"work","id":"work-a"}}]
        self.publish(proposal)
        self.identity=a;proposal=self.proposal("checkpoint")
        proposal[0]["relations"]=[{"relation":"parent","target":{"authority_home_id":"home-a","kind":"work","id":"work-b"}}]
        before=self.bytes()
        with self.assertRaises(ContractError):self.publish(proposal)
        self.assertEqual(before,self.bytes())

    def test_ignored_new_truth_is_refused_before_first_record(self):
        import subprocess
        subprocess.run(["git","-C",str(self.target),"init","-q"],check=True)
        (self.target/".gitignore").write_text(".hrn/work/\n")
        proposal=self.proposal()
        with self.assertRaises(ContractError):self.publish(proposal)
        self.assertFalse((self.target/".hrn/work/work-a").exists())

    def test_required_document_stale_after_decision_allows_cancel_only(self):
        self.publish(self.proposal());(self.target/"a").write_bytes(b"after\n")
        proposal=self.proposal("submit-result")
        proposal[0]["document_refs"]=[{"path":"a","sha256":hashlib.sha256(b"after\n").hexdigest(),"role":"result","required":True}]
        self.publish(proposal);prepared=self.prepare()
        with self.assertRaises(InjectedCrash):self.apply(prepared,inject_at="after-decision")
        (self.target/"a").write_bytes(b"stale\n")
        with self.assertRaises(ContractError):self.apply(prepared)
        graph=read_work(self.target,"work-a");decision=next(iter(graph["decisions"].values()))
        self.assertEqual(self.apply(self.prepare("reject",supersedes=record_ref(decision)))["state"],"rejected")

    def test_pending_selection_with_result_drift_is_not_completed(self):
        self.submitted();prepared=self.prepare()
        with self.assertRaises(InjectedCrash):self.apply(prepared,inject_at="after-selection")
        (self.target/"a").write_bytes(b"drift\n")
        with self.assertRaises(ContractError):self.apply(prepared)
        graph=read_work(self.target,"work-a")
        self.assertEqual(graph["state"],"review")
        self.assertEqual(len(graph["pending_selections"]),1)
        (self.target/"a").write_bytes(b"after\n")
        self.assertEqual(self.apply(prepared)["state"],"completed")

    def test_changed_orphan_revision_id_is_refused_without_new_evidence(self):
        proposal=self.proposal()
        with self.assertRaises(InjectedCrash):self.publish(proposal,inject_at="after-revision")
        proposal[0]["next_action"]="changed meaning"
        before=self.bytes()
        with self.assertRaises(ContractError):self.publish(proposal)
        self.assertEqual(before,self.bytes())


    def test_agent_pending_selection_blocks_decision_before_durable_write(self):
        self.submitted(); prepared=self.prepare()
        checkpoint=self.proposal("checkpoint")
        with self.assertRaises(InjectedCrash):self.publish(checkpoint,inject_at="after-selection")
        before=self.bytes()
        with self.assertRaises(ContractError):self.prepare()
        with self.assertRaises(ContractError):self.apply(prepared)
        self.assertEqual(before,self.bytes())
        self.assertEqual(self.publish(checkpoint)["pending_selections"],[])

    def test_reject_and_revoke_resume_after_intent_and_required_document_drift(self):
        for action in ("reject","revoke"):
            with self.subTest(action=action):
                self.identity={**self.identity,"work_id":"work-"+action}
                self.publish(self.proposal());(self.target/"a").write_bytes(b"after\n")
                proposal=self.proposal("submit-result")
                proposal[0]["document_refs"]=[{"path":"a","sha256":hashlib.sha256(b"after\n").hexdigest(),"role":"result","required":True}]
                self.publish(proposal)
                kwargs={}
                if action=="revoke":
                    graph=self.apply(self.prepare(request_id="accept-revoke"))
                    kwargs["supersedes"]=graph["selections"][graph["current"]["selection_ref"]["id"]]["decision_ref"]
                prepared=self.prepare(action,**kwargs)
                with self.assertRaises(InjectedCrash):self.apply(prepared,inject_at="after-decision")
                (self.target/"a").write_bytes(b"stale\n")
                self.intent=self.accept_intent(2 if action=="reject" else 3)
                self.assertEqual(self.apply(prepared)["state"],"rejected" if action=="reject" else "revoked")

    def test_checkpoint_cannot_absorb_unreviewed_content_or_policy(self):
        import subprocess
        subprocess.run(["git","-C",str(self.target),"init","-q"],check=True)
        (self.target/".gitignore").write_text("build/\n")
        self.publish(self.proposal())
        for path,value in [("outside",b"unreviewed"),("a",b"edited"),(".gitignore",b"cache/\n")]:
            with self.subTest(path=path):
                f=self.target/path;original=f.read_bytes() if f.exists() else None;f.write_bytes(value)
                proposal=self.proposal("checkpoint");before=self.bytes()
                with self.assertRaises(ContractError):self.publish(proposal)
                self.assertEqual(before,self.bytes())
                if original is None:f.unlink()
                else:f.write_bytes(original)

    def test_rework_cannot_absorb_drift_after_rejection(self):
        self.submitted();self.apply(self.prepare("reject"))
        (self.target/"a").write_bytes(b"unreviewed\n")
        with self.assertRaises(ContractError):self.publish(self.proposal("rework"))

    def test_work_reader_validates_actual_historical_intent(self):
        import json
        self.submitted();self.apply(self.prepare())
        self.intent=self.accept_intent(2)
        self.assertEqual(read_work(self.target,"work-a")["state"],"completed")
        path=self.target/".hrn/intents/intent-a/drafts/draft-1.json"
        value=json.loads(path.read_text());value["acceptance_authority"]="someone-else";put(path,value)
        with self.assertRaises(ContractError):read_work(self.target,"work-a")

    def test_invalid_identity_and_reference_parent_raise_typed_errors(self):
        self.publish(self.proposal());path=self.target/".hrn/work/work-a/identity.json"
        put(path,[])
        with self.assertRaises(ContractError):read_work(self.target,"work-a")
        put(path,self.identity)
        proposal=self.proposal("checkpoint")
        proposal[0]["document_refs"]=[{"path":"a/child","sha256":"a"*64,"role":"result","required":True}]
        with self.assertRaises(ContractError):self.publish(proposal)

    def test_selection_id_collision_does_not_write_orphan_records(self):
        self.publish(self.proposal());checkpoint=self.proposal("checkpoint")
        with self.assertRaises(InjectedCrash):self.publish(checkpoint,inject_at="after-selection")
        changed=list(self.proposal("checkpoint"));changed[2]=checkpoint[2]
        before=self.bytes()
        with self.assertRaises(ContractError):self.publish(changed)
        self.assertEqual(before,self.bytes())
        self.publish(checkpoint)

    def test_historical_agent_retry_during_pending_decision_is_noop(self):
        original=self.proposal();self.publish(original)
        self.publish(self.proposal("submit-result"));prepared=self.prepare()
        with self.assertRaises(InjectedCrash):self.apply(prepared,inject_at="after-decision")
        before=self.bytes();self.publish(original);self.assertEqual(before,self.bytes())

    def test_staging_residue_does_not_block_other_work(self):
        proposal=self.proposal()
        with self.assertRaises(InjectedCrash):self.publish(proposal,inject_at="after-staged-identity")
        residue={str(p):p.read_bytes() for p in (self.target/".hrn/staging").rglob("*") if p.is_file()}
        self.assertTrue(residue)
        self.identity={**self.identity,"work_id":"work-b"}
        self.assertEqual(self.publish(self.proposal())["state"],"active")
        self.assertTrue(all(Path(p).read_bytes()==value for p,value in residue.items()))

    def test_resolved_target_alias_reads_same_intent(self):
        alias=self.target.parent/"alias";alias.symlink_to(self.target,target_is_directory=True)
        # safe_target deliberately rejects a symlink target: no relative_to crash.
        with self.assertRaises(ContractError):read_workspace_intent(alias,"intent-a",self.intent)


    def test_rebind_proposal_does_not_require_unused_selection_keys(self):
        self.publish(self.proposal());old=self.intent;self.intent=self.accept_intent(2)
        r,m,_,_=self.proposal("rebind",old_intent=old)
        graph=self.store.publish(self.identity,r,m)
        self.assertIn(r["record_id"],graph["orphan_revisions"])

    def test_missing_work_and_current_raise_typed_errors(self):
        import shutil
        self.submitted();prepared=self.prepare();home=self.target/".hrn/work/work-a"
        saved=home/"current.json";original=saved.read_bytes();saved.unlink()
        with self.assertRaises(ContractError):self.apply(prepared)
        saved.write_bytes(original);shutil.rmtree(home)
        with self.assertRaises(ContractError):self.apply(prepared)

    def test_historical_intent_ref_cannot_point_to_unpublished_selection(self):
        home=self.target/".hrn/intents/intent-a/current.json";old=home.read_bytes()
        newer=self.accept_intent(2);home.write_bytes(old)
        with self.assertRaises(ContractError):read_workspace_intent(self.target,"intent-a",newer,require_current=False)


    def test_contract_pending_prefix_and_historical_retry_preserve_current(self):
        original=self.proposal();initial=self.publish(original)
        proposal=self.proposal("checkpoint");proposal[0]["observed_at"]="2099-01-01T00:00:00Z"
        for point in ("after-revision","after-selection","after-staged-current"):
            with self.subTest(point=point):
                with self.assertRaises(InjectedCrash):self.publish(proposal,inject_at=point)
                graph=read_work(self.target,"work-a")
                self.assertEqual(graph["current"],initial["current"])
                self.assertEqual(graph["state"],"active")
                self.assertIn(proposal[0]["record_id"],graph["revisions"])
        with self.assertRaises(InjectedCrash):self.publish(proposal,inject_at="after-current")
        graph=self.publish(proposal)
        self.assertEqual(graph["current"]["selection_ref"]["id"],proposal[2])
        before=self.bytes();self.publish(original);self.assertEqual(before,self.bytes())
        self.assertEqual(read_work(self.target,"work-a")["current"],graph["current"])

    def test_contract_pending_missing_or_corrupt_record_cannot_resume(self):
        self.submitted();prepared=self.prepare()
        with self.assertRaises(InjectedCrash):self.apply(prepared,inject_at="after-selection")
        home=self.target/".hrn/work/work-a";prior=(home/"current.json").read_bytes()
        decision=next((home/"decisions").glob("*.json"));original=decision.read_bytes()
        decision.unlink();before=self.bytes()
        with self.assertRaises(ContractError):self.apply(prepared)
        self.assertEqual(before,self.bytes());self.assertFalse(decision.exists())
        decision.write_bytes(original)
        import json
        value=json.loads(original);value["confirmation"]["actor"]="other";put(decision,value)
        before=self.bytes()
        with self.assertRaises(ContractError):self.apply(prepared)
        self.assertEqual(before,self.bytes());self.assertEqual(prior,(home/"current.json").read_bytes())
        decision.write_bytes(original)
        self.assertEqual(self.apply(prepared)["state"],"completed")

    def test_contract_disposable_staging_is_not_required_recovery_authority(self):
        import shutil
        self.submitted();prepared=self.prepare()
        with self.assertRaises(InjectedCrash):self.apply(prepared,inject_at="after-staged-current")
        home=self.target/".hrn/work/work-a";prior=(home/"current.json").read_bytes()
        staged=list((self.target/".hrn/staging").glob("work-current-*"));self.assertTrue(staged)
        for path in staged:path.write_bytes(b"untrusted staging\n")
        self.assertEqual(read_work(self.target,"work-a")["state"],"review")
        self.assertEqual(prior,(home/"current.json").read_bytes())
        shutil.rmtree(self.target/".hrn/staging")
        graph=self.apply(prepared);self.assertEqual(graph["state"],"completed")
        self.assertEqual(len(graph["decisions"]),1);self.assertEqual(len(graph["selections"]),3)
        residue=self.target/".hrn/staging/unrelated";residue.write_bytes(b"damaged residue\n")
        before=self.bytes();self.assertEqual(read_work(self.target,"work-a")["state"],"completed")
        self.assertEqual(self.apply(prepared)["state"],"completed");self.assertEqual(before,self.bytes())

    def test_contract_required_fields_authority_and_residue_preserve_bytes(self):
        self.publish(self.proposal());home=self.target/".hrn/work/work-a"
        proposal=self.proposal("checkpoint")
        variants=[]
        for key,value in (("authority_home_id","foreign"),("record_type","unknown"),("schema_version",2),("extra",True)):
            revision=copy.deepcopy(proposal[0]);revision[key]=value;variants.append(revision)
        revision=copy.deepcopy(proposal[0]);del revision["unavailable_scope"];variants.append(revision)
        for revision in variants:
            with self.subTest(revision=revision):
                before=self.bytes()
                with self.assertRaises(ContractError):self.publish((revision,*proposal[1:]))
                self.assertEqual(before,self.bytes())
        for name in (".current.json.hv2-tmp-deadbeef","current.json.hv2-tmp-deadbeef","unknown.json"):
            extra=home/name;extra.write_bytes(b"preserve\n");before=self.bytes()
            with self.assertRaises(ContractError):read_work(self.target,"work-a")
            with self.assertRaises(ContractError):self.publish(proposal)
            self.assertEqual(before,self.bytes());extra.unlink()

    def test_contract_same_local_id_in_distinct_kinds_and_reuse_boundary(self):
        proposal=list(self.proposal());proposal[0]["record_id"]="shared";proposal[2]="shared"
        graph=self.publish(proposal)
        self.assertIn("shared",graph["revisions"]);self.assertIn("shared",graph["selections"])
        before=self.bytes();self.publish(proposal);self.assertEqual(before,self.bytes())
        saved=self.identity;self.identity={**saved,"work_type":"different"}
        with self.assertRaises(ContractError):self.publish(proposal)
        self.assertEqual(before,self.bytes());self.identity=saved
        changed=list(self.proposal("checkpoint"));changed[0]["record_id"]="shared"
        with self.assertRaises(ContractError):self.publish(changed)
        self.assertEqual(before,self.bytes())
        for identifier in ("", "../escape", "a/b", ".", "a"*97, True):
            changed=list(self.proposal("checkpoint"));changed[0]["record_id"]=identifier
            with self.subTest(identifier=identifier), self.assertRaises(ContractError):self.publish(changed)
            self.assertEqual(before,self.bytes())

    def test_contract_rechained_reject_or_invalid_result_never_completes(self):
        from hv2ref.work import work_graph
        self.submitted();prepared=self.prepare();graph=self.apply(prepared)
        def changed(action="accept", actor="owner", field=None, value=None):
            g=copy.deepcopy(graph);tip=g["selections"][g["current"]["selection_ref"]["id"]]
            reviewed=g["selections"][tip["parent_selection_ref"]["id"]]
            r=g["revisions"][tip["revision_ref"]["id"]]
            if field is not None:r[field]=value
            reviewed["revision_ref"]=record_ref(r)
            ticket=copy.deepcopy(prepared["ticket"])
            ticket.update(action=action,actor=actor,target_revision_ref=record_ref(r),expected_selection_ref=record_ref(reviewed))
            d=self.store._decision(ticket);g["decisions"]={d["record_id"]:d}
            tip.update(parent_selection_ref=record_ref(reviewed),revision_ref=record_ref(r),decision_ref=record_ref(d))
            g["current"]["selection_ref"]=record_ref(tip)
            return g
        def inspect(g,*,intent_graphs=None):return work_graph(g["identity"],g["revisions"],g["decisions"],g["selections"],g["manifests"],g["current"],intent_graphs=intent_graphs)
        self.assertEqual(inspect(changed(action="reject"))["state"],"rejected")
        from hv2ref.intent import workspace_intents
        intents=workspace_intents(self.target);before=self.bytes();unauthorized=changed(actor="agent")
        records_before=copy.deepcopy((unauthorized,intents))
        for context,message in ((None,"delegated decision requires complete verified intent context"),(intents,"no grant for this Work")):
            with self.subTest(context_present=context is not None), self.assertRaises(ContractError) as caught:
                inspect(unauthorized,intent_graphs=context)
            self.assertEqual("HV2-WORK-RECORD",caught.exception.code)
            self.assertEqual(message,caught.exception.message)
            self.assertEqual(records_before,(unauthorized,intents));self.assertEqual(before,self.bytes())
        for field,value in (("progress","failed"),("progress","completed"),("outcome","failed")):
            with self.subTest(field=field,value=value),self.assertRaisesRegex(ContractError,"agent cannot declare completion|unexpected|keys|fields"):
                inspect(changed(field=field,value=value))


if __name__ == "__main__":
    unittest.main()
