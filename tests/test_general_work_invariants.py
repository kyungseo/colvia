"""New intent writer and real intent-to-Work integration; runtime seam is a double."""
from __future__ import annotations
import copy
import hashlib
from pathlib import Path
import tempfile
import unittest
from unittest import mock

import hv2ref.jsonio as jsonio

from hv2ref.errors import ContractError, InjectedCrash
from hv2ref.jsonio import canonical_json_bytes, decode_json_bytes, exclusive_file_lock, replace_bytes
from hv2ref.workspace import bootstrap_root, target_fingerprint
from hv2ref.work import WorkStore, read_work, record_ref
from hv2ref.intent import WorkspaceIntentStore, read_workspace_intent, read_workspace_intent_graph
import test_general_work_recovery as serial_fixtures
from test_general_work_recovery import digest, TIME


class IntentWriterTests(unittest.TestCase):
    proposal = serial_fixtures.SerialWriterTests.proposal
    publish = serial_fixtures.SerialWriterTests.publish
    submitted = serial_fixtures.SerialWriterTests.submitted
    prepare = serial_fixtures.SerialWriterTests.prepare
    apply = serial_fixtures.SerialWriterTests.apply
    bytes = serial_fixtures.SerialWriterTests.bytes

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="intent-writer-");self.addCleanup(self.temp.cleanup)
        self.target = Path(self.temp.name).resolve()/"project";self.target.mkdir();(self.target/"a").write_bytes(b"before\n")
        fmt={"record_type":"workspace-format","format_version":1,"authority_home_id":"home-a","created_at":TIME,"lineage":None}
        self.binding={"id":"binding-a","sha256":"b"*64}
        plan={"record_type":"lifecycle-plan","schema_version":1,"operation_id":"init-a","action":"init","target_fingerprint":target_fingerprint(self.target),"authority_home_id":"home-a","expected_binding_ref":None,"candidate_release":{"id":"product-release-"+"a"*24,"sha256":"a"*64,"inventory_id":"human-1"},"format_sha256":digest(fmt),"truth_refs":[],"remove":[],"preserve":[],"created_at":TIME}
        bootstrap_root(self.target,plan,fmt)
        runtime=lambda target:{"binding_ref":copy.deepcopy(self.binding),"launcher_sha256":None}
        self.store=WorkStore(self.target,runtime);self.intents=WorkspaceIntentStore(self.target,runtime)
        self.identity={"record_type":"work-identity","schema_version":1,"authority_home_id":"home-a","work_id":"work-a","work_type":"change","created_at":TIME,"acceptance_authority":"owner","lineage":None}
        self.serial=0;self.intent=None

    def draft(self,n=1,*,intent_id="intent-a",prior=None,authority="owner"):
        return {"record_type":"intent-draft","schema_version":1,"authority_home_id":"home-a","intent_id":intent_id,"revision_id":f"draft-{n}","sequence":n,"prior_revision_ref":record_ref(prior,"revision_id") if prior else None,"actor":"agent","acceptance_authority":authority,"observed_at":TIME,"facets":{k:{"status":"known","value":"fixture"} for k in ["acceptance_oracle","destination","expected_outcome","forbidden_scope","goal","scope"]},"gaps":[],"statements":[],"route":"direct-entry"}

    def iprepare(self,draft,**kw):
        return self.intents.prepare(draft["intent_id"],record_ref(draft,"revision_id"),actor=kw.pop("actor","owner"),reason="fixture accept",request_id=kw.pop("request_id","accept-"+draft["intent_id"]+"-"+draft["revision_id"]),observed_at=TIME,**kw)

    def iapply(self,prepared,**kw):
        return self.intents.apply(prepared["ticket"],confirm_token=prepared["confirm_token"],**kw)

    def accept(self,draft=None):
        draft=draft or self.draft();self.intents.publish_draft(draft);graph=self.iapply(self.iprepare(draft))
        selection=graph["selections"][graph["current"]["selection_ref"]["id"]]
        self.intent={"authority_home_id":"home-a","kind":"intent","id":draft["intent_id"],"revision_ref":selection["revision_ref"],"acceptance_ref":selection["acceptance_ref"],"selection_ref":graph["current"]["selection_ref"]}
        return graph

    def test_real_intent_to_work_completion_without_direct_record_fixture(self):
        self.accept();self.submitted();self.assertEqual(self.apply(self.prepare())["state"],"completed")
        self.assertTrue(read_workspace_intent(self.target,"intent-a",self.intent)["is_current"])

    def test_draft_does_not_grant_acceptance(self):
        graph=self.intents.publish_draft(self.draft());self.assertIsNone(graph["current"])
        self.assertEqual(graph["acceptances"],{})

    def test_authority_cannot_change_across_unaccepted_drafts(self):
        first=self.draft();self.intents.publish_draft(first);before=self.bytes()
        with self.assertRaises(ContractError):self.intents.publish_draft(self.draft(2,prior=first,authority="agent"))
        self.assertEqual(before,self.bytes())

    def test_material_gap_blocks_accept_but_can_be_resolved_in_next_draft(self):
        first=self.draft();first["gaps"]=[{"gap_id":"gap-a","depends_on":[],"owner":"owner","material":True,"status":"unresolved"}];first["route"]="bounded-clarification"
        self.intents.publish_draft(first)
        with self.assertRaises(ContractError):self.iprepare(first)
        nextdraft=self.draft(2,prior=first);self.accept(nextdraft)

    def test_wrong_actor_and_wrong_confirmation_token_refuse_without_writes(self):
        draft=self.draft();self.intents.publish_draft(draft);before=self.bytes()
        with self.assertRaises(ContractError):self.iprepare(draft,actor="agent")
        prepared=self.iprepare(draft)
        with self.assertRaises(ContractError):self.intents.apply(prepared["ticket"],confirm_token="wrong")
        self.assertEqual(before,self.bytes())

    def test_draft_identity_and_unknown_keys_refuse_before_home(self):
        for field,value in [("schema_version",True),("authority_home_id","foreign"),("accepted",True),("route","wrong")]:
            with self.subTest(field=field):
                draft=self.draft();draft[field]=value
                with self.assertRaises(ContractError):self.intents.publish_draft(draft)
                self.assertFalse((self.target/".hrn/intents/intent-a").exists())

    def test_draft_staging_prefixes_resume(self):
        for point in ("after-staged-identity","after-home","after-draft"):
            with self.subTest(point=point):
                draft=self.draft(intent_id="intent-"+point)
                with self.assertRaises(InjectedCrash):self.intents.publish_draft(draft,inject_at=point)
                graph=self.intents.publish_draft(draft);self.assertEqual(len(graph["drafts"]),1)
                self.assertIsNotNone(self.iapply(self.iprepare(draft))["current"])

    def test_acceptance_prefixes_resume_without_duplicate_records(self):
        for point in ("after-acceptance","after-selection","after-staged-current","after-current"):
            with self.subTest(point=point):
                draft=self.draft(intent_id="intent-"+point);self.intents.publish_draft(draft);prepared=self.iprepare(draft)
                with self.assertRaises(InjectedCrash):self.iapply(prepared,inject_at=point)
                graph=self.iapply(prepared);self.assertEqual(len(graph["acceptances"]),1);self.assertEqual(len(graph["selections"]),1)
                self.assertEqual(graph["pending_acceptances"]+graph["pending_selections"],[])

    def test_pending_work_decision_blocks_draft_and_intent_accept(self):
        first=self.draft();self.accept(first);second=self.draft(2,prior=first);self.intents.publish_draft(second);prepared=self.iprepare(second)
        self.submitted();work_ticket=self.prepare()
        with self.assertRaises(InjectedCrash):self.apply(work_ticket,inject_at="after-decision")
        before=self.bytes()
        with self.assertRaises(ContractError):self.intents.publish_draft(self.draft(intent_id="other"))
        with self.assertRaises(ContractError):self.iprepare(second)
        with self.assertRaises(ContractError):self.iapply(prepared)
        self.assertEqual(before,self.bytes());self.apply(work_ticket);self.iapply(prepared)

    def test_pending_work_agent_selection_blocks_intent_mutation(self):
        self.accept();proposal=self.proposal()
        with self.assertRaises(InjectedCrash):self.publish(proposal,inject_at="after-selection")
        with self.assertRaises(ContractError):self.intents.publish_draft(self.draft(intent_id="other"))
        self.publish(proposal);self.intents.publish_draft(self.draft(intent_id="other"))

    def test_pending_intent_blocks_other_intent_and_work(self):
        self.accept();self.submitted();work_ticket=self.prepare()
        other=self.draft(intent_id="other");self.intents.publish_draft(other);ticket=self.iprepare(other)
        with self.assertRaises(InjectedCrash):self.iapply(ticket,inject_at="after-acceptance")
        before=self.bytes()
        with self.assertRaises(ContractError):self.apply(work_ticket)
        with self.assertRaises(ContractError):self.prepare()
        with self.assertRaises(ContractError):self.publish(self.proposal("checkpoint"))
        with self.assertRaises(ContractError):self.intents.publish_draft(self.draft(intent_id="third"))
        self.assertEqual(before,self.bytes());self.iapply(ticket);self.apply(work_ticket)

    def test_competing_tickets_cannot_add_second_acceptance(self):
        draft=self.draft();self.intents.publish_draft(draft);one=self.iprepare(draft);two=self.iprepare(draft,request_id="second")
        with self.assertRaises(InjectedCrash):self.iapply(one,inject_at="after-acceptance")
        before=self.bytes()
        with self.assertRaises(ContractError):self.iapply(two)
        with self.assertRaises(ContractError):self.iprepare(draft,request_id="second")
        self.assertEqual(before,self.bytes());self.iapply(one)

    def test_historical_replay_never_promotes_old_selection(self):
        first=self.draft();self.intents.publish_draft(first);one=self.iprepare(first);self.iapply(one)
        second=self.draft(2,prior=first);self.accept(second);before=self.bytes()
        current=read_workspace_intent_graph(self.target,"intent-a")["current"]
        self.assertEqual(self.iapply(one)["current"],current);self.intents.publish_draft(first)
        self.assertEqual(before,self.bytes())

    def test_required_reference_stale_after_durable_acceptance_requires_restoration(self):
        draft=self.draft();self.intents.publish_draft(draft)
        refs=[{"path":"a","sha256":hashlib.sha256(b"before\n").hexdigest(),"role":"brief","required":True}]
        prepared=self.iprepare(draft,document_refs=refs)
        with self.assertRaises(InjectedCrash):self.iapply(prepared,inject_at="after-acceptance")
        (self.target/"a").write_bytes(b"changed\n")
        with self.assertRaises(ContractError):self.iapply(prepared)
        self.assertIsNone(read_workspace_intent_graph(self.target,"intent-a")["current"])
        (self.target/"a").write_bytes(b"before\n");self.iapply(prepared)

    def test_binding_drift_cannot_publish_prepared_ticket(self):
        draft=self.draft();self.intents.publish_draft(draft);prepared=self.iprepare(draft);before=self.bytes()
        self.binding={"id":"binding-b","sha256":"c"*64}
        with self.assertRaises(ContractError):self.iapply(prepared)
        self.assertEqual(before,self.bytes())

    def test_real_rebind_accepts_new_intent_but_not_ignore_policy_drift(self):
        import subprocess
        subprocess.run(["git","-C",str(self.target),"init","-q"],check=True)
        (self.target/".gitignore").write_text("build/\n")
        first=self.draft();self.accept(first);self.publish(self.proposal());old=self.intent
        self.accept(self.draft(2,prior=first));(self.target/".gitignore").write_text("cache/\n")
        proposal=self.proposal("rebind",old_intent=old);before=self.bytes()
        with self.assertRaises(ContractError):self.publish(proposal)
        self.assertEqual(before,self.bytes());(self.target/".gitignore").write_text("build/\n")
        proposal=self.proposal("rebind",old_intent=old);self.publish(proposal)
        self.apply(self.prepare("rebind",revision_ref=record_ref(proposal[0])))
        self.publish(self.proposal("submit-result"));self.assertEqual(self.apply(self.prepare())["state"],"completed")

    def test_prepare_and_graph_reader_are_read_only(self):
        draft=self.draft();self.intents.publish_draft(draft);before=self.bytes()
        self.iprepare(draft);read_workspace_intent_graph(self.target,"intent-a");self.assertEqual(before,self.bytes())

    def test_ignored_truth_refuses_before_publication(self):
        import subprocess
        subprocess.run(["git","-C",str(self.target),"init","-q"],check=True)
        (self.target/".gitignore").write_text(".hrn/intents/\n")
        with self.assertRaises(ContractError):self.intents.publish_draft(self.draft())
        self.assertFalse((self.target/".hrn/intents/intent-a").exists())

    def test_staging_residue_does_not_poison_work(self):
        self.accept();other=self.draft(intent_id="other")
        with self.assertRaises(InjectedCrash):self.intents.publish_draft(other,inject_at="after-staged-identity")
        self.submitted();self.assertEqual(self.apply(self.prepare())["state"],"completed")

    def test_request_and_draft_id_reuse_preserves_existing_bytes(self):
        first=self.draft();self.accept(first);changed=copy.deepcopy(first);changed["actor"]="other";before=self.bytes()
        with self.assertRaises(ContractError):self.intents.publish_draft(changed)
        self.assertEqual(before,self.bytes())
        second=self.draft(2,prior=first);self.intents.publish_draft(second)
        with self.assertRaises(ContractError):self.iprepare(second,request_id="accept-intent-a-draft-1")


    def test_case_only_draft_id_collision_is_refused_before_write(self):
        first=self.draft();self.intents.publish_draft(first)
        another=self.draft(2,prior=first);another["revision_id"]="DRAFT-1";before=self.bytes()
        with self.assertRaises(ContractError):self.intents.publish_draft(another)
        self.assertEqual(before,self.bytes())

    def test_vacuous_intent_is_not_accepted(self):
        draft=self.draft();draft["facets"]={k:{"status":"unknown","owner":"owner"} for k in draft["facets"]}
        self.intents.publish_draft(draft);before=self.bytes()
        with self.assertRaises(ContractError):self.iprepare(draft)
        self.assertEqual(before,self.bytes())

    def test_draft_forks_and_second_root_are_refused(self):
        first=self.draft();self.intents.publish_draft(first)
        second=self.draft(2,prior=first);self.intents.publish_draft(second)
        for candidate in (self.draft(2,prior=first),self.draft()):
            candidate["revision_id"]="alternative-"+str(candidate["sequence"]);before=self.bytes()
            with self.assertRaises(ContractError):self.intents.publish_draft(candidate)
            self.assertEqual(before,self.bytes())

    def test_malformed_prior_sequence_is_typed_independent_of_order(self):
        from hv2ref.intent import workspace_intent_graph
        first=self.draft();self.intents.publish_draft(first)
        identity=read_workspace_intent_graph(self.target,"intent-a")["identity"]
        for value in ("1",None,True,-1,0):
            malformed=copy.deepcopy(first);malformed["sequence"]=value
            child=self.draft(2,prior=malformed)
            data={"identity.json":identity,"drafts/child.json":{**child,"revision_id":"child"},"drafts/draft-1.json":malformed}
            with self.assertRaises(ContractError):workspace_intent_graph(data,"intent-a","home-a")

    def test_completed_work_replay_is_noop_during_pending_intent(self):
        self.accept();self.submitted();ticket=self.prepare();self.apply(ticket)
        other=self.draft(intent_id="other");self.intents.publish_draft(other);iticket=self.iprepare(other)
        with self.assertRaises(InjectedCrash):self.iapply(iticket,inject_at="after-acceptance")
        before=self.bytes();self.assertEqual(self.apply(ticket)["state"],"completed");self.assertEqual(before,self.bytes())
        self.iapply(iticket)

    def test_pending_intent_binding_drift_requires_exact_restoration(self):
        draft=self.draft();self.intents.publish_draft(draft);ticket=self.iprepare(draft)
        with self.assertRaises(InjectedCrash):self.iapply(ticket,inject_at="after-acceptance")
        original=self.binding;self.binding={"id":"binding-b","sha256":"c"*64};before=self.bytes()
        with self.assertRaises(ContractError):self.iapply(ticket)
        self.assertEqual(before,self.bytes());self.binding=original;self.iapply(ticket)


    def changing_runtime(self):
        count = 0
        def check(target):
            nonlocal count
            count += 1
            return {"binding_ref":copy.deepcopy(self.binding) if count == 1 else {"id":"changed","sha256":"c"*64},"launcher_sha256":None}
        return check

    def test_work_publish_rechecks_runtime_before_truth_write(self):
        self.accept();proposal=self.proposal();before=self.bytes()
        self.store.runtime_check=self.changing_runtime()
        with self.assertRaisesRegex(ContractError,"bound runtime changed"):
            self.publish(proposal)
        self.assertEqual(before,self.bytes())

    def test_intent_publish_rechecks_runtime_before_truth_write(self):
        from hv2ref.workspace import writer_guard
        with writer_guard(self.target): pass  # Existing stable lock is not truth publication.
        before=self.bytes();self.intents.work_store.runtime_check=self.changing_runtime()
        with self.assertRaisesRegex(ContractError,"bound runtime changed"):
            self.intents.publish_draft(self.draft())
        self.assertEqual(before,self.bytes())





    def test_port_nonconsequential_entry_is_pure(self):
        from hv2ref.intent import classify_entry
        before=self.bytes()
        self.assertEqual({"artifact_required":False,"route":"non-consequential"},classify_entry("non-consequential",[]))
        self.assertEqual(before,self.bytes())

    def test_port_gap_graph_routes_and_invalid_dependencies(self):
        def gap(name,dependencies=()):
            return {"gap_id":name,"depends_on":list(dependencies),"owner":"owner","material":True,"status":"unresolved"}
        for name,gaps,route in [
            ("bounded",[gap("a"),gap("b")],"bounded-clarification"),
            ("ordered",[gap("a"),gap("b",["a"])],"dependency-ordered-clarification"),
        ]:
            with self.subTest(name=name):
                draft=self.draft(intent_id=name);draft.update(gaps=gaps,route=route)
                graph=self.intents.publish_draft(draft)
                self.assertEqual(route,graph["drafts"]["draft-1"]["route"])
                self.assertIsNone(graph["current"])
                wrong=self.draft(intent_id="wrong-"+name);wrong.update(gaps=gaps,route="bounded-clarification" if route=="dependency-ordered-clarification" else "dependency-ordered-clarification")
                before=self.bytes()
                with self.assertRaisesRegex(ContractError,"intent route does not follow gap graph"):self.intents.publish_draft(wrong)
                self.assertEqual(before,self.bytes())
        nonmaterial=gap("note");nonmaterial["material"]=False
        for name,gaps,route in [("direct",[],"direct-entry"),("nonmaterial",[nonmaterial],"direct-entry")]:
            with self.subTest(name=name):
                draft=self.draft(intent_id=name);draft.update(gaps=gaps,route=route)
                self.intents.publish_draft(draft)
                for number,wrong_route in enumerate(("bounded-clarification","dependency-ordered-clarification")):
                    wrong=self.draft(intent_id=f"wrong-{name}-{number}");wrong.update(gaps=gaps,route=wrong_route)
                    before=self.bytes()
                    with self.assertRaisesRegex(ContractError,"intent route does not follow gap graph"):self.intents.publish_draft(wrong)
                    self.assertEqual(before,self.bytes())
        for name,gaps in [("material-direct",[gap("a")]),("ordered-direct",[gap("a"),gap("b",["a"])])]:
            wrong=self.draft(intent_id=name);wrong.update(gaps=gaps,route="direct-entry");before=self.bytes()
            with self.assertRaisesRegex(ContractError,"intent route does not follow gap graph"):self.intents.publish_draft(wrong)
            self.assertEqual(before,self.bytes())
        for name,gaps in [("cycle",[gap("a",["b"]),gap("b",["a"])]),("missing",[gap("a",["absent"])])]:
            with self.subTest(name=name):
                draft=self.draft(intent_id=name);draft.update(gaps=gaps,route="dependency-ordered-clarification")
                before=self.bytes()
                with self.assertRaises(ContractError):self.intents.publish_draft(draft)
                self.assertEqual(before,self.bytes())
                self.assertFalse((self.target/".hrn/intents"/name).exists())

    def test_port_missing_facet_and_ownerless_unknown_refuse(self):
        from hv2ref.workspace import writer_guard
        with writer_guard(self.target): pass  # Stable lock scratch is not truth publication.
        for name in ("missing","ownerless"):
            with self.subTest(name=name):
                draft=self.draft(intent_id=name)
                if name=="missing":del draft["facets"]["acceptance_oracle"]
                else:draft["facets"]["goal"]={"status":"unknown"}
                before=self.bytes()
                with self.assertRaises(ContractError):self.intents.publish_draft(draft)
                self.assertEqual(before,self.bytes())
                self.assertFalse((self.target/".hrn/intents"/name).exists())

    def test_port_interrupted_draft_is_unaccepted_after_exact_retry(self):
        draft=self.draft()
        with self.assertRaises(InjectedCrash):self.intents.publish_draft(draft,inject_at="after-draft")
        for graph in (read_workspace_intent_graph(self.target,"intent-a"),self.intents.publish_draft(draft)):
            self.assertEqual({"draft-1"},set(graph["drafts"]))
            self.assertIsNone(graph["current"])
            self.assertEqual({},graph["acceptances"])
            self.assertEqual({},graph["selections"])

    def test_port_wrong_revision_digest_refuses(self):
        draft=self.draft();self.intents.publish_draft(draft);before=self.bytes()
        with self.assertRaises(ContractError):
            self.intents.prepare("intent-a",{"id":"draft-1","sha256":"0"*64},actor="owner",reason="fixture",request_id="wrong",observed_at=TIME)
        self.assertEqual(before,self.bytes())

    def test_port_named_revision_recency_and_exact_prior_confirmation(self):
        first=self.draft();self.intents.publish_draft(first)
        second=self.draft(2,prior=first);self.intents.publish_draft(second)
        graph=read_workspace_intent_graph(self.target,"intent-a")
        self.assertEqual({"draft-1","draft-2"},set(graph["drafts"]))
        self.assertIsNone(graph["current"])
        stale=self.iprepare(second,request_id="pre-first")
        graph=self.iapply(self.iprepare(first))
        self.assertEqual(record_ref(first,"revision_id"),graph["selections"][graph["current"]["selection_ref"]["id"]]["revision_ref"])
        before=self.bytes()
        with self.assertRaises(ContractError):self.iapply(stale)
        self.assertEqual(before,self.bytes())
        fresh=self.iprepare(second,request_id="post-first")
        self.assertEqual(graph["current"]["selection_ref"],fresh["ticket"]["expected_selection_ref"])
        graph=self.iapply(fresh)
        self.assertEqual(record_ref(second,"revision_id"),graph["selections"][graph["current"]["selection_ref"]["id"]]["revision_ref"])

    def test_port_acceptance_prefix_preserves_prior_current_and_pending_gate(self):
        for prior_exists in (False,True):
            for point in ("after-acceptance","after-selection","after-staged-current"):
                with self.subTest(prior_exists=prior_exists,point=point):
                    name="prefix-"+str(prior_exists)+"-"+point
                    first=self.draft(intent_id=name);self.intents.publish_draft(first)
                    prior=self.iapply(self.iprepare(first))["current"] if prior_exists else None
                    draft=self.draft(2,intent_id=name,prior=first) if prior_exists else first
                    self.intents.publish_draft(draft);ticket=self.iprepare(draft)
                    with self.assertRaises(InjectedCrash):self.iapply(ticket,inject_at=point)
                    graph=read_workspace_intent_graph(self.target,name)
                    self.assertEqual(prior,graph["current"])
                    ticket_digest=hashlib.sha256(canonical_json_bytes(ticket["ticket"])).hexdigest()
                    self.assertEqual(["acceptance-"+ticket_digest] if point=="after-acceptance" else [],graph["pending_acceptances"])
                    self.assertEqual([] if point=="after-acceptance" else ["selection-"+ticket_digest],graph["pending_selections"])
                    before=self.bytes()
                    with self.assertRaises(ContractError):self.iprepare(draft,request_id="competing-"+name)
                    self.assertEqual(before,self.bytes())
                    graph=self.iapply(ticket)
                    self.assertEqual([],graph["pending_acceptances"]+graph["pending_selections"])
                    self.assertEqual(record_ref(draft,"revision_id"),graph["selections"][graph["current"]["selection_ref"]["id"]]["revision_ref"])
                    self.assertEqual(2 if prior_exists else 1,len(graph["acceptances"]))

    def test_port_whole_acceptance_unknown_fields_and_digest_tamper(self):
        graph=self.accept();home=self.target/".hrn/intents/intent-a"
        acceptance=next(iter(graph["acceptances"].values()));path=home/"acceptances"/(acceptance["acceptance_id"]+".json")
        original=path.read_bytes()
        for alteration in ("partial","digest"):
            value=copy.deepcopy(acceptance)
            if alteration=="partial":value["accepted_facets"]=["goal"]
            else:value["confirmation"]["target_revision_ref"]["sha256"]="0"*64
            path.write_bytes(canonical_json_bytes(value))
            with self.assertRaises(ContractError):read_workspace_intent_graph(self.target,"intent-a")
            path.write_bytes(original)
        extra=home/"latest.json";extra.write_bytes(b"{}\n")
        with self.assertRaises(ContractError):read_workspace_intent_graph(self.target,"intent-a")
        self.assertEqual(b"{}\n",extra.read_bytes())

    def test_port_symlinked_intent_member_refuses(self):
        external=self.target.parent/"external";external.mkdir();(external/"sentinel").write_bytes(b"preserve\n")
        alias=self.target/".hrn/intents/alias";alias.symlink_to(external,target_is_directory=True)
        with self.assertRaises(ContractError):self.intents.publish_draft(self.draft(intent_id="alias"))
        self.assertEqual(["sentinel"],sorted(p.name for p in external.iterdir()))
        self.assertEqual(b"preserve\n",(external/"sentinel").read_bytes())
        self.assertTrue(alias.is_symlink())

    def test_port_intent_does_not_change_work_or_project(self):
        first=self.draft();self.accept(first);self.submitted()
        def work_bytes():return {str(p.relative_to(self.target)):p.read_bytes() for p in (self.target/".hrn/work").rglob("*") if p.is_file()}
        before=work_bytes();self.assertTrue(before);project=(self.target/"a").read_bytes()
        self.accept(self.draft(2,prior=first))
        self.assertEqual(before,work_bytes());self.assertEqual(project,(self.target/"a").read_bytes())

    def test_port_same_draft_input_is_canonical_and_byte_deterministic(self):
        draft=self.draft();self.intents.publish_draft(draft)
        path=self.target/".hrn/intents/intent-a/drafts/draft-1.json";expected=path.read_bytes()
        self.assertEqual(canonical_json_bytes(draft),expected)
        other=self.target.parent/"second";other.mkdir()
        import shutil
        shutil.copytree(self.target/".hrn",other/".hrn")
        shutil.rmtree(other/".hrn/intents/intent-a")
        store=WorkspaceIntentStore(other,lambda target:{"binding_ref":copy.deepcopy(self.binding),"launcher_sha256":None})
        store.publish_draft(draft)
        self.assertEqual(expected,(other/".hrn/intents/intent-a/drafts/draft-1.json").read_bytes())


class SharedJsonDurabilityTests(unittest.TestCase):
    """Shared byte and filesystem contracts without a retired-generation fixture."""

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="json-contract-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()

    def test_advisory_lock_anchor_rejects_symlink_and_wrong_type(self) -> None:
        lock_path = self.root / "staging/locks/active-integration.switch.lock"
        lock_path.parent.mkdir(parents=True)
        outside = self.root / "outside-lock"
        outside.write_bytes(b"")
        lock_path.symlink_to(outside)
        with self.assertRaisesRegex(ContractError, "HV2-LOCK-ANCHOR"):
            with exclusive_file_lock(lock_path):
                self.fail("symlink lock anchor was admitted")
        lock_path.unlink()
        lock_path.mkdir()
        with self.assertRaisesRegex(ContractError, "HV2-LOCK-ANCHOR"):
            with exclusive_file_lock(lock_path):
                self.fail("directory lock anchor was admitted")

    def test_unserializable_json_is_stable_contract_error(self) -> None:
        with self.assertRaisesRegex(ContractError, "HV2-JSON-EMISSION"):
            canonical_json_bytes({"value": object()})

    def test_duplicate_key_is_red(self) -> None:
        with self.assertRaisesRegex(ContractError, "HV2-JSON-DUPLICATE-KEY"):
            decode_json_bytes(b'{"a": 1, "a": 2}\n')

    def test_bom_is_red(self) -> None:
        with self.assertRaisesRegex(ContractError, "HV2-JSON-BOM"):
            decode_json_bytes(b"\xef\xbb\xbf{}\n")

    def test_missing_or_double_eof_lf_is_red(self) -> None:
        for data in (b"{}", b"{}\n\n"):
            with self.subTest(data=data), self.assertRaisesRegex(ContractError, "HV2-JSON-EOF"):
                decode_json_bytes(data)

    def test_nonfinite_json_is_red(self) -> None:
        with self.assertRaisesRegex(ContractError, "HV2-JSON-NONFINITE"):
            decode_json_bytes(b'{"value": NaN}\n')

    def test_writer_rejects_nonfinite_and_reader_normalizes_limits(self) -> None:
        with self.assertRaisesRegex(ContractError, "HV2-JSON-EMISSION"):
            canonical_json_bytes({"value": float("inf")})
        huge_integer = b'{"value": ' + b"9" * 1100 + b"}\n"
        with self.assertRaisesRegex(ContractError, "HV2-JSON-LIMIT"):
            decode_json_bytes(huge_integer)
        deep = ("[" * 140 + "0" + "]" * 140 + "\n").encode()
        with self.assertRaisesRegex(ContractError, "HV2-JSON-LIMIT"):
            decode_json_bytes(deep)

    def test_fullfsync_classification_is_explicit(self) -> None:
        with (
            mock.patch.object(jsonio.sys, "platform", "darwin"),
            mock.patch.object(jsonio.os, "fsync"),
            mock.patch.object(jsonio.fcntl, "F_FULLFSYNC", 51, create=True),
            mock.patch.object(jsonio.fcntl, "fcntl") as fullfsync,
        ):
            self.assertEqual("pass", jsonio._sync_fd(7)["fullfsync"])
            fullfsync.side_effect = OSError(5, "io")
            self.assertEqual("error:5", jsonio._sync_fd(7)["fullfsync"])
        with (
            mock.patch.object(jsonio.sys, "platform", "darwin"),
            mock.patch.object(jsonio.os, "fsync"),
            mock.patch.object(jsonio.fcntl, "F_FULLFSYNC", None, create=True),
        ):
            self.assertEqual("unavailable", jsonio._sync_fd(7)["fullfsync"])

    def test_new_ancestor_chain_is_directory_synced(self) -> None:
        destination = self.root / "ancestor-a/ancestor-b/ancestor-c/value.json"
        with mock.patch.object(jsonio, "sync_directory", return_value="pass") as sync:
            jsonio._ensure_parent(destination)
        expected = [
            mock.call(self.root),
            mock.call(self.root / "ancestor-a"),
            mock.call(self.root / "ancestor-a"),
            mock.call(self.root / "ancestor-a/ancestor-b"),
            mock.call(self.root / "ancestor-a/ancestor-b"),
            mock.call(self.root / "ancestor-a/ancestor-b/ancestor-c"),
        ]
        self.assertEqual(expected, sync.call_args_list)

    def test_replace_temp_is_created_in_destination_parent(self) -> None:
        destination = self.root / "same-parent/value.txt"
        destination.parent.mkdir()
        destination.write_bytes(b"old\n")
        original_replace = jsonio.os.replace
        observed: list[tuple[Path, Path]] = []

        def capture(source, target):
            observed.append((Path(source), Path(target)))
            return original_replace(source, target)

        with (
            mock.patch.object(jsonio, "_sync_fd", return_value={"fsync": "pass", "fullfsync": "not-applicable"}),
            mock.patch.object(jsonio, "sync_directory", return_value="pass"),
            mock.patch.object(jsonio.os, "replace", side_effect=capture),
        ):
            replace_bytes(destination, b"new\n")
        self.assertEqual(1, len(observed))
        self.assertEqual(observed[0][0].parent, observed[0][1].parent)
        self.assertEqual(destination.parent, observed[0][0].parent)

    def test_numeric_overflow_is_nonfinite_in_both_reader_modes(self):
        for literal in (b"1e999", b"-1e999", b"NaN", b"Infinity", b"-Infinity"):
            for canonical in (False, True):
                with self.subTest(literal=literal, canonical=canonical):
                    with self.assertRaisesRegex(ContractError, "HV2-JSON-NONFINITE"):
                        decode_json_bytes(b'{"nested": [0, {"value": ' + literal + b'}]}\n', require_canonical=canonical)
        self.assertEqual(decode_json_bytes(b'{"value": 1e300}\n')["value"], 1e300)





class WorkerBaselineGraphTests(unittest.TestCase):
    """Pure persisted semantics; no runtime, actor identity or Git execution proof."""
    def setUp(self):
        from hv2ref.work import make_manifest, record_ref
        self.identity={"record_type":"work-identity","schema_version":1,"authority_home_id":"home-a","work_id":"work-a","work_type":"change","created_at":"fixture","acceptance_authority":"owner","lineage":None}
        from hv2ref.intent import FACET_KEYS, workspace_intent_graph
        base={"schema_version":1,"authority_home_id":"home-a","intent_id":"intent-a"}
        draft={**base,"record_type":"intent-draft","revision_id":"r","sequence":1,"prior_revision_ref":None,"actor":"agent","acceptance_authority":"owner","observed_at":"fixture","facets":{k:{"status":"known","value":"fixture"} for k in FACET_KEYS},"gaps":[],"statements":[],"route":"direct-entry"}
        ticket={"record_type":"confirmation-ticket","schema_version":1,"authority_home_id":"home-a","object":{"authority_home_id":"home-a","kind":"intent","id":"intent-a"},"action":"accept","actor":"owner","reason":"fixture acceptance","request_id":"intent-request","observed_at":"fixture","target_fingerprint":"a"*64,"target_revision_ref":record_ref(draft,"revision_id"),"expected_selection_ref":None,"intent_ref":None,"product_binding_ref":{"id":"binding","sha256":"b"*64},"document_refs":[],"evidence_refs":[],"execution_mode":None,"supersedes_decision_ref":None}
        accepted={**base,"record_type":"intent-acceptance","acceptance_id":"acceptance-"+digest(ticket),"confirmation":ticket}
        selected={**base,"record_type":"intent-selection","selection_id":"s","revision_ref":record_ref(draft,"revision_id"),"acceptance_ref":record_ref(accepted,"acceptance_id"),"prior_selection_ref":None}
        data={"identity.json":{**base,"record_type":"intent-identity"},"drafts/r.json":draft,"acceptances/"+accepted["acceptance_id"]+".json":accepted,"selections/s.json":selected,"current.json":{**base,"record_type":"intent-current","selection_ref":record_ref(selected,"selection_id")}}
        self.intent_graphs={"intent-a":workspace_intent_graph(data,"intent-a","home-a")}
        self.intent={"authority_home_id":"home-a","kind":"intent","id":"intent-a","revision_ref":selected["revision_ref"],"acceptance_ref":selected["acceptance_ref"],"selection_ref":record_ref(selected,"selection_id")}
        self.tree={"policy_version":1,"ignore_fingerprint":"d"*64,"entries":[]}
        self.tree["sha256"]=digest(self.tree)
        self.manifest=make_manifest(self.tree,self.tree,scope=[],base_commit="e"*40,candidate_commit="e"*40,base_retention_ref="refs/heads/base",candidate_retention_ref="refs/heads/base")
        self.start={"record_type":"work-revision","schema_version":1,"authority_home_id":"home-a","work_id":"work-a","record_id":"start","observed_at":"fixture","observed_scope":[],"unavailable_scope":[],"author":"agent","operation":"start","expected_prior_selection":None,"intent_ref":self.intent,"scope":[],"document_refs":[],"evidence_refs":[],"result_refs":{"manifest":{"id":digest(self.manifest),"sha256":digest(self.manifest)}},"progress":"active","next_action":"fixture","relations":[],"rebind_from":None,"execution_context":{"mode":"isolated-worktree","attempt_id":"same-advisory-id"}}
        self.selection={"record_type":"work-selection","schema_version":1,"authority_home_id":"home-a","work_id":"work-a","record_id":"selected","observed_at":"fixture","observed_scope":[],"unavailable_scope":[],"parent_selection_ref":None,"revision_ref":record_ref(self.start),"decision_ref":None,"operation_id":"start"}
        self.current={"record_type":"work-current","schema_version":1,"authority_home_id":"home-a","work_id":"work-a","selection_ref":record_ref(self.selection)}
        self.refresh=copy.deepcopy(self.start);self.refresh.update(record_id="refresh",operation="rebind",expected_prior_selection=record_ref(self.selection),rebind_from=copy.deepcopy(self.intent))

    def graph(self):
        from hv2ref.work import work_graph
        return work_graph(self.identity,{"start":self.start,"refresh":self.refresh},{},{"selected":self.selection},{digest(self.manifest):self.manifest},self.current)

    def test_same_intent_worker_refresh_is_proposal_only(self):
        graph=self.graph()
        self.assertEqual("active",graph["state"])
        self.assertEqual(self.current,graph["current"])
        self.assertEqual("start",graph["selections"]["selected"]["revision_ref"]["id"])

    def test_local_same_intent_refresh_remains_refused(self):
        from hv2ref.work import make_manifest, record_ref
        self.manifest=make_manifest(self.tree,self.tree,scope=[])
        for r in [self.start,self.refresh]:
            r["execution_context"]["mode"]="local";r["result_refs"]["manifest"]={"id":digest(self.manifest),"sha256":digest(self.manifest)}
        self.selection["revision_ref"]=record_ref(self.start);self.current["selection_ref"]=record_ref(self.selection);self.refresh["expected_prior_selection"]=record_ref(self.selection)
        with self.assertRaisesRegex(ContractError,"local rebind"):self.graph()

    def test_refresh_scope_progress_and_provenance_cannot_change(self):
        for field,value in [("scope",["other"]),("progress","planned"),("rebind_from",dict(self.intent,id="other"))]:
            with self.subTest(field=field):
                old=copy.deepcopy(self.refresh);self.refresh[field]=value
                with self.assertRaises(ContractError):self.graph()
                self.refresh=old

    def test_worker_direct_rework_is_refused(self):
        self.refresh.update(operation="rework",rebind_from=None)
        with self.assertRaisesRegex(ContractError,"human baseline refresh"):self.graph()

    def test_refresh_one_commit_is_required_even_with_identical_content(self):
        from hv2ref.work import record_ref
        self.manifest["candidate_commit"]="f"*40
        for r in [self.start,self.refresh]:r["result_refs"]["manifest"]={"id":digest(self.manifest),"sha256":digest(self.manifest)}
        self.selection["revision_ref"]=record_ref(self.start);self.current["selection_ref"]=record_ref(self.selection);self.refresh["expected_prior_selection"]=record_ref(self.selection)
        with self.assertRaisesRegex(ContractError,"one commit"):self.graph()

    def test_worker_to_local_mode_change_is_refused(self):
        from hv2ref.work import make_manifest, work_graph
        local=make_manifest(self.tree,self.tree,scope=[])
        self.refresh["execution_context"]["mode"]="local";self.refresh["intent_ref"]=dict(self.intent,id="new-intent")
        self.refresh["result_refs"]["manifest"]={"id":digest(local),"sha256":digest(local)}
        with self.assertRaisesRegex(ContractError,"execution mode"):
            work_graph(self.identity,{"start":self.start,"refresh":self.refresh},{},{"selected":self.selection},{digest(self.manifest):self.manifest,digest(local):local},self.current)

    def test_human_refresh_selects_baseline_but_never_completes_work(self):
        from hv2ref.work import WorkStore, work_graph, record_ref
        ticket={"record_type":"confirmation-ticket","schema_version":1,"authority_home_id":"home-a","object":{"authority_home_id":"home-a","kind":"work","id":"work-a"},"action":"rebind","actor":"owner","reason":"baseline only","request_id":"human-refresh","observed_at":"fixture","target_fingerprint":"a"*64,"target_revision_ref":record_ref(self.refresh),"expected_selection_ref":record_ref(self.selection),"intent_ref":self.intent,"product_binding_ref":{"id":"binding","sha256":"b"*64},"document_refs":[],"evidence_refs":[],"execution_mode":"isolated-worktree","supersedes_decision_ref":None}
        decision=WorkStore._decision(ticket)
        revisions={"start":self.start,"refresh":self.refresh};decisions={decision["record_id"]:decision};manifests={digest(self.manifest):self.manifest}
        pending=work_graph(self.identity,revisions,decisions,{"selected":self.selection},manifests,self.current)
        self.assertEqual([decision["record_id"]],pending["pending_decisions"])
        self.assertEqual(self.current,pending["current"])
        selected=copy.deepcopy(self.selection);selected.update(record_id="human-selected",parent_selection_ref=record_ref(self.selection),revision_ref=record_ref(self.refresh),decision_ref=record_ref(decision),operation_id="human-refresh")
        current=dict(self.current,selection_ref=record_ref(selected))
        done=work_graph(self.identity,revisions,decisions,{"selected":self.selection,"human-selected":selected},manifests,current)
        self.assertEqual("active",done["state"]);self.assertEqual([],done["pending_decisions"])
        wrong=copy.deepcopy(ticket);wrong["actor"]="agent";wrong_decision=WorkStore._decision(wrong)
        inputs=(self.identity,revisions,{wrong_decision["record_id"]:wrong_decision},{"selected":self.selection},manifests,self.current)
        before=copy.deepcopy((inputs,self.intent_graphs))
        for context,message in ((None,"delegated decision requires complete verified intent context"),(self.intent_graphs,"no grant for this Work")):
            with self.subTest(context_present=context is not None), self.assertRaises(ContractError) as caught:
                work_graph(*inputs,intent_graphs=context)
            self.assertEqual("HV2-WORK-RECORD",caught.exception.code)
            self.assertEqual(message,caught.exception.message)
            self.assertEqual(before,(inputs,self.intent_graphs))

    def test_agent_cannot_select_refresh_without_human_decision(self):
        from hv2ref.work import work_graph, record_ref
        selected=copy.deepcopy(self.selection);selected.update(record_id="agent-refresh",parent_selection_ref=record_ref(self.selection),revision_ref=record_ref(self.refresh),operation_id="agent-refresh")
        with self.assertRaisesRegex(ContractError,"agent selection"):
            work_graph(self.identity,{"start":self.start,"refresh":self.refresh},{},{"selected":self.selection,"agent-refresh":selected},{digest(self.manifest):self.manifest},self.current)


if __name__ == "__main__":
    unittest.main()
