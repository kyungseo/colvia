"""Deterministic interruption prefixes; process death is covered separately."""
from __future__ import annotations
import copy
import hashlib
import os
import unittest
from unittest.mock import patch
from hv2ref.errors import ContractError, InjectedCrash
from hv2ref.continuation import current_record, graph, records
from hv2ref.work import read_work, record_ref
import test_continuation as core


class ContinuationRecoveryTests(unittest.TestCase):
    def setUp(self):
        # Each prefix needs a fresh home and no reference from a prior subtest.
        self.__dict__.pop("intent", None)
        core.ContinuationTests.setUp(self)
    accept_intent = core.ContinuationTests.accept_intent
    proposal = core.ContinuationTests.proposal
    publish = core.ContinuationTests.publish
    bytes = core.ContinuationTests.bytes
    prepare_cont = core.ContinuationTests.prepare_cont
    apply_cont = core.ContinuationTests.apply_cont
    state = core.ContinuationTests.state
    lifecycle_bytes = core.ContinuationTests.lifecycle_bytes
    another = core.ContinuationTests.another

    def test_all_publication_prefixes_retry_once_preserving_source(self):
        for phase in ("after-directories", "after-initial-current", "after-choice",
                      "after-selection", "after-staged-current", "after-current"):
            with self.subTest(phase=phase):
                self.setUp()
                before = self.lifecycle_bytes()
                packet = self.prepare_cont()
                with self.assertRaises(InjectedCrash):
                    self.apply_cont(packet, inject_at=phase)
                state = self.state()
                if phase in ("after-directories", "after-initial-current"):
                    self.assertIsNone(state["pending"]); self.assertEqual(0, state["usage"]["normal_used"])
                    self.assertIsNone(state["effective_choice"])
                elif phase == "after-current":
                    self.assertIsNone(state["pending"]); self.assertEqual({"kind": "none"}, state["effective_choice"])
                else:
                    self.assertIsNotNone(state["pending"]); self.assertIsNone(state["effective_choice"])
                self.apply_cont(packet)
                after = self.bytes()
                self.assertEqual("resolved", self.apply_cont(packet)["replay"])
                self.assertEqual(after, self.bytes()); self.assertEqual(before, self.lifecycle_bytes())
                state = self.state()
                self.assertEqual(1, len(state["choices"])); self.assertEqual(1, len(state["selections"]))
                self.assertEqual(1, state["usage"]["normal_used"]); self.assertIsNone(state["pending"])

    def test_cancellation_prefixes_keep_prior_choice_and_original_bytes(self):
        for original_phase in ("after-choice", "after-selection"):
            for cancel_phase in ("after-choice", "after-selection", "after-staged-current", "after-current"):
                with self.subTest(original=original_phase, cancel=cancel_phase):
                    self.setUp()
                    first = self.prepare_cont()
                    self.apply_cont(first)
                    selected = self.state()["current"]
                    pending = self.prepare_cont(action="withdraw")
                    with self.assertRaises(InjectedCrash):
                        self.apply_cont(pending, inject_at=original_phase)
                    original, original_selection = records(pending["ticket"])
                    cancel = self.prepare_cont(action="cancel-pending", supersedes_choice_ref=record_ref(original))
                    before = self.lifecycle_bytes()
                    with self.assertRaises(InjectedCrash):
                        self.apply_cont(cancel, inject_at=cancel_phase)
                    state = self.state()
                    self.assertEqual({"kind": "none"}, state["effective_choice"])
                    self.assertEqual(first["ticket"], state["effective_ticket"])
                    self.assertIn(original["record_id"], state["cancelled"])
                    frozen = self.bytes()
                    self.assertEqual("cancelled", self.apply_cont(pending)["replay"])
                    self.assertEqual(frozen, self.bytes())
                    if cancel_phase != "after-current":
                        self.assertEqual(selected, state["current"])
                        with self.assertRaisesRegex(ContractError, "pending"):
                            self.prepare_cont()
                    self.apply_cont(cancel)
                    state = self.state()
                    self.assertIsNone(state["pending"]); self.assertEqual(2, state["usage"]["normal_used"])
                    self.assertEqual(original, state["choices"][original["record_id"]])
                    if original_phase == "after-selection":
                        self.assertEqual(original_selection, state["selections"][original_selection["record_id"]])
                    self.assertEqual(before, self.lifecycle_bytes())
                    self.apply_cont(self.prepare_cont(action="withdraw"))
                    self.assertIsNone(self.state()["effective_choice"])

    def test_retained_cancellation_rejects_changed_binding_or_location(self):
        pending = self.prepare_cont()
        with self.assertRaises(InjectedCrash):
            self.apply_cont(pending, inject_at="after-choice")
        original, _ = records(pending["ticket"])
        cancel = self.prepare_cont(action="cancel-pending", supersedes_choice_ref=record_ref(original))
        base = read_work(self.target, "work-a")
        for field in ("product_binding_ref", "target_fingerprint"):
            with self.subTest(field=field):
                ticket = copy.deepcopy(cancel["ticket"])
                if field == "product_binding_ref":
                    ticket[field]["sha256"] = "c" * 64
                else:
                    ticket[field] = "c" * 64
                choice, selection = records(ticket)
                data = copy.deepcopy(self.state()["data"])
                data["choices/" + choice["record_id"] + ".json"] = choice
                data["selections/" + selection["record_id"] + ".json"] = selection
                data["current.json"] = current_record(base["identity"], record_ref(selection))
                with self.assertRaisesRegex(ContractError, "cancellation changed binding/location"):
                    graph(base["identity"], data)

    def test_cancelled_selection_is_neither_current_nor_parent(self):
        self.apply_cont(self.prepare_cont())
        pending = self.prepare_cont(action="withdraw")
        with self.assertRaises(InjectedCrash): self.apply_cont(pending, inject_at="after-selection")
        original, selection = records(pending["ticket"])
        self.apply_cont(self.prepare_cont(action="cancel-pending", supersedes_choice_ref=record_ref(original)))
        base = read_work(self.target, "work-a")
        data = copy.deepcopy(self.state()["data"])
        data["current.json"] = current_record(base["identity"], record_ref(selection))
        with self.assertRaisesRegex(ContractError, "invalid selected continuation"):
            graph(base["identity"], data)
        data = copy.deepcopy(self.state()["data"])
        ticket = copy.deepcopy(pending["ticket"])
        ticket.update(action="select", choice={"kind":"none"}, request_id="illegal-child",
                      expected_continuation_selection_ref=record_ref(selection))
        choice, child = records(ticket)
        data["choices/"+choice["record_id"]+".json"] = choice
        data["selections/"+child["record_id"]+".json"] = child
        data["current.json"] = current_record(base["identity"], record_ref(child))
        with self.assertRaisesRegex(ContractError, "cancelled selection cannot be a parent"):
            graph(base["identity"], data)

    def test_unknown_cancel_duplicate_cancel_and_cancel_of_cancel_refused(self):
        pending = self.prepare_cont()
        with self.assertRaises(InjectedCrash): self.apply_cont(pending, inject_at="after-choice")
        original, _ = records(pending["ticket"])
        cancel = self.prepare_cont(action="cancel-pending", supersedes_choice_ref=record_ref(original))
        with self.assertRaises(InjectedCrash): self.apply_cont(cancel, inject_at="after-choice")
        before = self.bytes()
        with self.assertRaisesRegex(ContractError, "pending"):
            self.prepare_cont(action="cancel-pending", supersedes_choice_ref=record_ref(original))
        cancel_choice, _ = records(cancel["ticket"])
        with self.assertRaisesRegex(ContractError, "cannot cancel cancellation"):
            self.prepare_cont(action="cancel-pending", supersedes_choice_ref=record_ref(cancel_choice))
        with self.assertRaises(ContractError):
            self.prepare_cont(action="cancel-pending", supersedes_choice_ref={"id":"absent","sha256":"a"*64})
        self.assertEqual(before, self.bytes())

    def test_cancellation_survives_required_document_drift_and_binding_refuses(self):
        path = self.target/"plan.md"; path.write_bytes(b"old")
        reference={"path":"plan.md","role":"plan","required":True,"sha256":hashlib.sha256(b"old").hexdigest()}
        packet=self.prepare_cont(document_refs=[reference])
        with self.assertRaises(InjectedCrash): self.apply_cont(packet,inject_at="after-choice")
        path.write_bytes(b"changed")
        before=self.bytes()
        with self.assertRaisesRegex(ContractError,"stale"): self.apply_cont(packet)
        self.assertEqual(before,self.bytes())
        original,_=records(packet["ticket"])
        old_binding=copy.deepcopy(self.binding)
        self.binding["sha256"]="c"*64
        with self.assertRaisesRegex(ContractError,"binding/location"):
            self.prepare_cont(action="cancel-pending",supersedes_choice_ref=record_ref(original))
        self.binding=old_binding
        self.apply_cont(self.prepare_cont(action="cancel-pending",supersedes_choice_ref=record_ref(original)))
        self.assertEqual(b"changed",path.read_bytes())
        self.assertIsNone(self.state()["effective_choice"])

    def restore_work_fixture(self, desired):
        """External fixture edit; never a product cancellation/recovery operation."""
        for name in self.lifecycle_bytes():
            if name not in desired: (self.target/name).unlink()
        for name,value in desired.items():
            path=self.target/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(value)

    def test_source_progress_after_interruption_can_cancel_but_not_resume(self):
        packet=self.prepare_cont()
        before=self.lifecycle_bytes()
        self.publish(self.proposal("checkpoint"))
        future=self.lifecycle_bytes()
        self.restore_work_fixture(before)
        with self.assertRaises(InjectedCrash): self.apply_cont(packet,inject_at="after-selection")
        self.restore_work_fixture(future)
        frozen=self.bytes()
        with self.assertRaisesRegex(ContractError,"source Work selection changed"): self.apply_cont(packet)
        self.assertEqual(frozen,self.bytes())
        original,_=records(packet["ticket"])
        self.apply_cont(self.prepare_cont(action="cancel-pending",supersedes_choice_ref=record_ref(original)))
        self.assertEqual(future,self.lifecycle_bytes())

    def test_target_progress_after_interruption_can_cancel_but_not_resume(self):
        self.another()
        packet=self.prepare_cont({"kind":"work","target_work_id":"work-b"})
        before=self.lifecycle_bytes()
        identity=self.identity;self.identity={**identity,"work_id":"work-b"}
        self.publish(self.proposal("checkpoint"));self.identity=identity
        future=self.lifecycle_bytes()
        self.restore_work_fixture(before)
        with self.assertRaises(InjectedCrash): self.apply_cont(packet,inject_at="after-choice")
        self.restore_work_fixture(future)
        frozen=self.bytes()
        with self.assertRaisesRegex(ContractError,"target Work selection changed"): self.apply_cont(packet)
        self.assertEqual(frozen,self.bytes())
        original,_=records(packet["ticket"])
        self.apply_cont(self.prepare_cont(action="cancel-pending",supersedes_choice_ref=record_ref(original)))
        self.assertEqual(future,self.lifecycle_bytes())

    def test_move_pending_refuses_original_and_cancellation_without_writes(self):
        packet=self.prepare_cont()
        with self.assertRaises(InjectedCrash): self.apply_cont(packet,inject_at="after-choice")
        original,_=records(packet["ticket"])
        moved=self.target.with_name("moved");self.target.rename(moved)
        from hv2ref.continuation import ContinuationStore
        self.target=moved;self.cont=ContinuationStore(moved,self.runtime)
        before=self.bytes()
        with self.assertRaisesRegex(ContractError,"target moved"): self.apply_cont(packet)
        with self.assertRaisesRegex(ContractError,"binding/location"):
            self.prepare_cont(action="cancel-pending",supersedes_choice_ref=record_ref(original))
        self.assertEqual(before,self.bytes())

    def test_member_links_aliases_and_unexplained_orphans_are_unavailable(self):
        self.apply_cont(self.prepare_cont())
        home=self.target/".hrn/work/work-a/continuation"
        target=home/"current.json"
        original=target.read_bytes()
        for kind in ("symlink","hardlink","directory"):
            with self.subTest(kind=kind):
                target.unlink()
                if kind=="symlink": target.symlink_to(self.target/"a")
                elif kind=="hardlink": os.link(self.target/"a",target)
                else: target.mkdir()
                with self.assertRaises(ContractError): self.state()
                if kind=="directory": target.rmdir()
                else: target.unlink()
                target.write_bytes(original)
        data=copy.deepcopy(self.state()["data"])
        base=read_work(self.target,"work-a")
        t=copy.deepcopy(next(iter(data[k] for k in data if k.startswith("choices/")))["confirmation"])
        t["request_id"]="competing"
        choice,_=records(t);data["choices/"+choice["record_id"]+".json"]=choice
        with self.assertRaisesRegex(ContractError,"competing normal"):
            graph(base["identity"],data)

    def test_total_budget_is_checked_before_first_authority_write(self):
        packet=self.prepare_cont()
        before=self.bytes()
        with patch("hv2ref.continuation.TOTAL_BYTES",1):
            with self.assertRaisesRegex(ContractError,"collection limit"):
                self.apply_cont(packet)
        self.assertEqual(before,self.bytes())
