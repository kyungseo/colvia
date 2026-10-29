"""Read-only projection, exact installed CLI and consumer boundaries."""
from __future__ import annotations
import copy
import hashlib
import html
import json
import subprocess
import sys
import unittest
from unittest.mock import patch
from hv2ref.continuation import records
from hv2ref.errors import ContractError
from hv2ref.jsonio import canonical_json_bytes
from hv2ref.product import (workspace_switch_preview, workspace_detach_preview,
                           workspace_repair_preview, workspace_repair_apply)
from hv2ref.view import _continuation
from hv2ref.work import read_work, record_ref
import test_continuation as core
import test_human_view as human
import test_productization_safety as fixtures


def readable(value):
    return html.unescape(value).replace("\\","")


class ContinuationProjectionTests(unittest.TestCase):
    setUp=core.ContinuationTests.setUp
    accept_intent=core.ContinuationTests.accept_intent
    proposal=core.ContinuationTests.proposal
    publish=core.ContinuationTests.publish
    bytes=core.ContinuationTests.bytes
    prepare_cont=core.ContinuationTests.prepare_cont
    apply_cont=core.ContinuationTests.apply_cont
    state=core.ContinuationTests.state
    another=core.ContinuationTests.another

    def screen(self):
        before=self.bytes();works=self.store._all()
        with patch.object(self.cont.__class__,"prepare",side_effect=AssertionError("view prepares")),\
             patch.object(self.cont.__class__,"apply",side_effect=AssertionError("view applies")):
            result="\n".join(_continuation(self.target,works["work-a"],works))
        self.assertEqual(before,self.bytes())
        return readable(result)

    def test_distinct_choices_quota_source_progress_and_document_observations(self):
        self.assertIn("상태: 미정",self.screen())
        self.apply_cont(self.prepare_cont())
        self.assertIn("후속 작업 없음",self.screen())
        self.assertIn("normal_used: 1",self.screen());self.assertIn("normal_remaining: 255",self.screen())
        self.publish(self.proposal("checkpoint"))
        self.assertIn("source_selection: historical/stale",self.screen())
        path=self.target/"plan.md";path.write_bytes(b"old")
        ref={"path":"plan.md","role":"plan","required":True,"sha256":hashlib.sha256(b"old").hexdigest()}
        packet=self.prepare_cont({"kind":"proposal","goal":"Follow up","scope":"One document",
            "next_step":"Prepare intent","decision_needed":"Owner accepts intent"},document_refs=[ref])
        self.apply_cont(packet)
        path.write_bytes(b"new")
        screen=self.screen()
        self.assertIn("후속 제안",screen);self.assertIn("changed_required_refs",screen)
        self.assertIn("observation: stale",screen)
        self.apply_cont(self.prepare_cont(action="withdraw"))
        self.assertIn("상태: 미정",self.screen())

    def test_changed_target_scope_is_changed_purpose_without_reselection(self):
        self.another()
        self.apply_cont(self.prepare_cont({"kind":"work","target_work_id":"work-b"}))
        selected = copy.deepcopy(self.state()["current"])
        original = self.identity
        self.identity = {**original, "work_id":"work-b"}
        revision, manifest, sid, oid = self.proposal("checkpoint")
        revision["scope"] = ["a", "additional.md"]
        self.store.publish(self.identity, revision, manifest, selection_id=sid, operation_id=oid)
        self.identity = original
        self.assertIn("target_observation: target-purpose-changed", self.screen())
        self.assertEqual(selected, self.state()["current"])

    def test_target_progress_same_purpose_then_intent_change_are_distinct(self):
        self.another()
        self.apply_cont(self.prepare_cont({"kind":"work","target_work_id":"work-b"}))
        self.assertIn("target_observation: selection-current",self.screen())
        identity=self.identity;self.identity={**identity,"work_id":"work-b"}
        self.publish(self.proposal("checkpoint"))
        self.assertIn("target_observation: target-progressed",self.screen())
        self.publish(self.proposal("submit-result"))
        p=self.store.prepare("work-b",action="reject",actor="owner",reason="fixture",request_id="reject-b",observed_at="2026-01-01T00:00:00Z")
        self.store.apply(p["ticket"],confirm_token=p["confirm_token"])
        self.assertIn("target_state: rejected",self.screen())
        old=copy.deepcopy(self.intent);self.intent=self.accept_intent(2)
        r,m,s,o=self.proposal("rebind",old_intent=old)
        self.store.publish(self.identity,r,m,selection_id=s,operation_id=o)
        p=self.store.prepare("work-b",action="rebind",actor="owner",reason="fixture",request_id="rebind-b",
                             observed_at="2026-01-01T00:00:00Z",revision_ref=record_ref(r))
        self.store.apply(p["ticket"],confirm_token=p["confirm_token"])
        self.identity=identity
        screen=self.screen()
        self.assertIn("target_observation: target-purpose-changed",screen)
        self.assertIn("source_bound_intent_current: False",screen)


class ContinuationInstalledTests(unittest.TestCase):
    setUp=fixtures.ActualWorkspaceInitTests.setUp
    TIME=fixtures.ActualWorkspaceInitTests.TIME
    call=fixtures.ActualWorkspaceInitTests.call
    preview=fixtures.ActualWorkspaceInitTests.preview
    apply_init=fixtures.ActualWorkspaceInitTests.apply_init
    installed=fixtures.ActualWorkspaceInitTests.installed
    draft=fixtures.ActualWorkspaceInitTests.draft
    accept_intent=fixtures.ActualWorkspaceInitTests.accept_intent
    complete_work=fixtures.ActualWorkspaceInitTests.complete_work
    screen=human.HumanViewInstalledTests.screen

    def seed(self):
        self.apply_init(self.preview());self.complete_work()

    def prepare_cont(self,**overrides):
        value=dict(work_id="work-a",action="select",actor="owner",owner_statement="Synthetic explicit Owner statement",
                   reason="Choose follow-up",request_id="cont-a",observed_at=self.TIME,choice={"kind":"none"})
        value.update(overrides)
        before=fixtures.exact_snapshot(self.target)
        result=self.installed(["continuation","prepare"],value)
        self.assertEqual(before,fixtures.exact_snapshot(self.target))
        return json.loads(result.stdout)

    def apply_cont(self,p):
        return json.loads(self.installed(["continuation","apply","--confirm",p["confirm_token"]],p["ticket"]).stdout)

    def seed_pending(self):
        packet=self.prepare_cont()
        # Explicit deterministic persisted-prefix fixture; process tests use actual CLI death.
        from hv2ref.continuation import current_record
        base=read_work(self.target,"work-a")
        home=self.target/".hrn/work/work-a/continuation";home.mkdir()
        (home/"choices").mkdir();(home/"selections").mkdir()
        choice,_=records(packet["ticket"])
        (home/"current.json").write_bytes(canonical_json_bytes(current_record(base["identity"],None)))
        (home/"choices"/(choice["record_id"]+".json")).write_bytes(canonical_json_bytes(choice))
        return packet,choice

    def test_installed_prepare_confirmation_apply_and_source_has_no_writer(self):
        self.seed()
        old={str(p.relative_to(self.target)):p.read_bytes() for p in (self.target/".hrn/work").rglob("*.json")}
        p=self.prepare_cont()
        view=self.screen(["confirmation","--input","-"],p["ticket"])
        self.assertIn("normal_used: 0",view);self.assertIn("normal_remaining: 255",view)
        self.assertIn("prospective_usage",view);self.assertIn(p["confirm_token"],view)
        self.screen(["confirmation","--input","-"],p,expected=65)
        before=fixtures.exact_snapshot(self.target)
        self.call(["continuation","prepare","--target",self.target],expected=2)
        self.assertEqual(before,fixtures.exact_snapshot(self.target))
        state=self.apply_cont(p)
        self.assertEqual({"kind":"none"},state["effective_choice"])
        self.assertIn("normal_used: 1",self.screen(["work","work-a"]))
        self.assertIn("후속 작업 없음",self.screen(["continuation","work-a"]))
        self.assertIn("already_applied: True",self.screen(["confirmation","--input","-"],p["ticket"]))
        self.assertEqual(old,{name:(self.target/name).read_bytes() for name in old})
        self.assertEqual("completed",read_work(self.target,"work-a")["state"])
        for args in (["continuation"],["continuation","work-a","--revision","revision-1"],["work"]):
            self.screen(args,expected=65)

    def test_pending_status_guards_lifecycle_and_cancel_through_installed_cli(self):
        self.seed();p,choice=self.seed_pending()
        status=json.loads(self.installed(["status"],expected=14).stdout)
        self.assertEqual(["work-a"],status["pending_continuation"])
        view=self.screen(["continuation","work-a"],expected=14)
        self.assertIn("발행 중",view);self.assertIn("normal_used: 1",view)
        before=fixtures.exact_snapshot(self.target)
        for call in (lambda:workspace_switch_preview(self.target,action="update",source=self.source,operation_id="blocked",created_at=self.TIME),
                     lambda:workspace_detach_preview(self.target,operation_id="blocked",created_at=self.TIME)):
            with self.assertRaisesRegex(ContractError,"pending"):call()
        self.assertEqual(before,fixtures.exact_snapshot(self.target))
        cancel=self.prepare_cont(action="cancel-pending",choice=None,request_id="cancel-a",supersedes_choice_ref=record_ref(choice))
        cancellation,_=records(cancel["ticket"])
        home=self.target/".hrn/work/work-a/continuation"
        (home/"choices"/(cancellation["record_id"]+".json")).write_bytes(canonical_json_bytes(cancellation))
        pending=json.loads(self.installed(["status"],expected=14).stdout)
        self.assertIn("already pending cancellation may only resume that cancellation",pending["next_action"])
        self.apply_cont(cancel)
        before=fixtures.exact_snapshot(self.target)
        self.assertEqual("cancelled",self.apply_cont(p)["replay"])
        self.assertEqual(before,fixtures.exact_snapshot(self.target))
        self.assertIn("상태: 미정",self.screen(["continuation","work-a"]))

    def test_unknown_integrity_blocks_repair_and_reports_usage_unavailable(self):
        from hv2ref.product import _workspace_status_observation
        from hv2ref.work import WorkStore
        from hv2ref.continuation import require_no_pending, current_snapshot
        self.seed()
        accepted_intent = current_snapshot(read_work(self.target,"work-a"))["intent_ref"]
        self.complete_work("work-b",intent_ref=accepted_intent)
        self.apply_cont(self.prepare_cont(work_id="work-b",request_id="cont-b",
                                         choice={"kind":"work","target_work_id":"work-a"}))
        self.apply_cont(self.prepare_cont())
        home=self.target/".hrn/work/work-a/continuation"
        (home/"unknown.json").write_bytes(b"{}\n")
        before=fixtures.exact_snapshot(self.target)
        view=self.screen(["continuation","work-a"],source=True,expected=10)
        self.assertIn("확인 불가",view);self.assertNotIn("normal_remaining:",view)
        self.assertIn("source_work_state: completed",view)
        self.assertIn("Stored state: completed",self.screen(["work","work-a"],source=True,expected=10))
        other=self.screen(["continuation","work-b"],source=True,expected=10)
        self.assertIn("target_continuation_pending: unavailable",other)
        self.assertIn("normal_used: 1",other)
        overview=self.screen([],source=True,expected=10)
        self.assertIn("work: work-a",overview);self.assertIn("work: work-b",overview)
        self.assertIn("continuation: unavailable",overview)
        status,observed=_workspace_status_observation(self.target)
        self.assertEqual({"work-a":"completed","work-b":"completed"},status["work_states"])
        self.assertIsNone(status["continuation_usage"]["work-a"])
        self.assertIsNone(status["pending_continuation"])
        self.assertFalse(status["lifecycle_ready"])
        with self.assertRaises(ContractError):WorkStore(self.target)._all()
        with self.assertRaises(ContractError):require_no_pending(self.target,works=observed[0])
        self.installed(["continuation","prepare"],dict(work_id="work-b",action="withdraw",actor="owner",
                       owner_statement="Synthetic Owner",reason="must refuse",request_id="blocked",
                       observed_at=self.TIME),expected=65)
        for call in (lambda:workspace_repair_preview(self.source,self.target,self.base/"backup",operation_id="repair-a",created_at=self.TIME),
                     lambda:workspace_detach_preview(self.target,operation_id="detach-a",created_at=self.TIME)):
            with self.assertRaises(ContractError):call()
        self.assertEqual(before,fixtures.exact_snapshot(self.target));self.assertFalse((self.base/"backup").exists())

    def test_exact_active_repair_preserves_valid_pending_continuation(self):
        self.seed();p,_=self.seed_pending()
        truth={str(path.relative_to(self.target)):path.read_bytes() for path in (self.target/".hrn/work").rglob("*.json")}
        binding=(self.target/".hrn/product/binding.json").read_bytes()
        (self.target/"colvia").write_bytes(b"damaged\n")
        packet=workspace_repair_preview(self.source,self.target,self.base/"backup",operation_id="repair-a",created_at=self.TIME)
        workspace_repair_apply(self.source,self.target,packet["request"],confirm_token=packet["confirm_token"])
        self.assertEqual(binding,(self.target/".hrn/product/binding.json").read_bytes())
        self.assertEqual(truth,{name:(self.target/name).read_bytes() for name in truth})
        self.apply_cont(p);self.assertIn("후속 작업 없음",self.screen(["continuation","work-a"]))

    def test_detach_and_plain_auditor_preserve_selected_continuation(self):
        from hv2ref.product import workspace_detach_apply
        self.seed();self.apply_cont(self.prepare_cont())
        before={str(p.relative_to(self.target)):p.read_bytes() for p in (self.target/".hrn/work").rglob("*.json")}
        packet=workspace_detach_preview(self.target,operation_id="detach-a",created_at=self.TIME)
        self.assertEqual(6 if sys.platform=='win32' else 5,packet["request"]["schema_version"])
        workspace_detach_apply(self.target,packet["request"],confirm_token=packet["confirm_token"])
        result=subprocess.run([sys.executable,"-I","-B",str(self.source/"tests/fixtures/product_plain_auditor.py"),str(self.target)],
                              capture_output=True,timeout=30)
        self.assertEqual(0,result.returncode,result.stdout+result.stderr)
        audit=json.loads(result.stdout)
        self.assertEqual({"kind":"none"},audit["selected"][".hrn/work/work-a/continuation"]["effective_choice"])
        self.assertEqual(before,{name:(self.target/name).read_bytes() for name in before})
        self.assertIn("후속 작업 없음",self.screen(["continuation","work-a"],source=True))
