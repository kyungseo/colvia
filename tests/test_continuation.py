"""Continuation contracts. The serial runtime verifier is an explicit test double."""
from __future__ import annotations
import copy
import hashlib
from pathlib import Path
import unittest
from unittest.mock import patch

from hv2ref.continuation import (ContinuationStore, current_record, current_snapshot, graph,
                                read_continuation, records, validate_ticket)
from hv2ref.errors import ContractError, InjectedCrash
from hv2ref.work import WorkStore, read_work, record_ref
from tests import test_general_work_recovery as serial


class ContinuationTests(unittest.TestCase):
    accept_intent = serial.SerialWriterTests.accept_intent
    proposal = serial.SerialWriterTests.proposal
    publish = serial.SerialWriterTests.publish
    bytes = serial.SerialWriterTests.bytes

    def setUp(self):
        serial.SerialWriterTests.setUp(self)
        self.runtime = lambda target: {"binding_ref": copy.deepcopy(self.binding),
                                      "launcher_sha256": None, "inventory_id": "continuation-1"}
        self.store = WorkStore(self.target, self.runtime)
        self.cont = ContinuationStore(self.target, self.runtime)
        self.publish(self.proposal())
        self.requests = 0

    def prepare_cont(self, choice=None, *, action="select", **kwargs):
        self.requests += 1
        values = dict(action=action, actor="owner", owner_statement="Synthetic Owner selection",
                      reason="Continue a bounded task", request_id="cont-" + str(self.requests),
                      observed_at=serial.TIME, choice=({"kind": "none"} if choice is None and action == "select" else choice))
        values.update(kwargs)
        return self.cont.prepare("work-a", **values)

    def apply_cont(self, prepared, **kwargs):
        return self.cont.apply(prepared["ticket"], confirm_token=prepared["confirm_token"], **kwargs)

    def state(self):
        return read_continuation(self.target, "work-a")

    def lifecycle_bytes(self):
        return {key: value for key, value in self.bytes().items()
                if key.startswith(".hrn/work/") and "/continuation/" not in key}

    def another(self, wid="work-b"):
        identity = self.identity
        self.identity = {**identity, "work_id": wid}
        try:
            self.publish(self.proposal())
        finally:
            self.identity = identity

    def test_prepare_and_read_are_read_only_and_show_quota(self):
        before = self.bytes()
        self.assertIsNone(self.state()["effective_choice"])
        prepared = self.prepare_cont()
        self.assertEqual({"normal_limit": 256, "normal_used": 0, "normal_remaining": 256}, prepared["usage"])
        self.assertEqual(1, prepared["prospective_usage"]["normal_used"])
        self.assertEqual(255, prepared["prospective_usage"]["normal_remaining"])
        self.assertEqual(before, self.bytes())
        self.assertFalse((self.target / ".hrn/work/work-a/continuation").exists())

    def test_proposal_none_withdraw_are_distinct_and_keep_source_result(self):
        before = self.lifecycle_bytes()
        proposal = {"kind": "proposal", "goal": "Follow up", "scope": "One document",
                    "next_step": "Prepare intent", "decision_needed": "Approve intent"}
        self.assertEqual(proposal, self.apply_cont(self.prepare_cont(proposal))["effective_choice"])
        self.assertEqual({"kind": "none"}, self.apply_cont(self.prepare_cont())["effective_choice"])
        state = self.apply_cont(self.prepare_cont(action="withdraw"))
        self.assertIsNone(state["effective_choice"])
        self.assertEqual(3, state["usage"]["normal_used"])
        with self.assertRaisesRegex(ContractError, "already-undecided"):
            self.prepare_cont(action="withdraw")
        self.assertEqual(before, self.lifecycle_bytes())
        self.assertEqual({"work-a"}, set(self.store._all()))

    def test_exact_retry_and_late_replay_never_reselect_or_spend_quota(self):
        first = self.prepare_cont()
        self.apply_cont(first)
        self.apply_cont(self.prepare_cont(action="withdraw"))
        before = self.bytes()
        self.assertEqual("resolved", self.apply_cont(first)["replay"])
        self.assertIsNone(self.state()["effective_choice"])
        self.assertEqual(2, self.state()["usage"]["normal_used"])
        self.assertEqual(before, self.bytes())

    def test_stale_competitor_has_no_new_authority_writes(self):
        first, second = self.prepare_cont(), self.prepare_cont()
        self.apply_cont(first)
        before = self.bytes()
        with self.assertRaisesRegex(ContractError, "stale"):
            self.apply_cont(second)
        self.assertEqual(before, self.bytes())

    def test_source_drift_refuses_new_publication(self):
        prepared = self.prepare_cont()
        self.publish(self.proposal("checkpoint"))
        before = self.bytes()
        with self.assertRaisesRegex(ContractError, "source Work selection changed"):
            self.apply_cont(prepared)
        self.assertEqual(before, self.bytes())

    def test_owner_and_new_window_required(self):
        before = self.bytes()
        with self.assertRaisesRegex(ContractError, "Owner"):
            self.prepare_cont(actor="delegate")
        older = ContinuationStore(self.target, lambda target: {**self.runtime(target), "inventory_id": "delegation-1"})
        with self.assertRaisesRegex(ContractError, "requires continuation-1"):
            older.prepare("work-a", action="select", actor="owner", owner_statement="Owner", reason="r",
                          request_id="old", observed_at=serial.TIME, choice={"kind": "none"})
        self.assertEqual(before, self.bytes())

    def test_exact_shapes_text_bytes_timestamp_and_document_bounds(self):
        prepared = self.prepare_cont()
        values = []
        for key, value in (("schema_version", True), ("observed_at", "2026-02-30T00:00:00Z"),
                           ("request_id", "x" * 97), ("reason", "가" * 1366),
                           ("owner_statement", ""), ("action", "execute")):
            ticket = copy.deepcopy(prepared["ticket"]); ticket[key] = value; values.append(ticket)
        extra = copy.deepcopy(prepared["ticket"]); extra["extra"] = 1; values.append(extra)
        for path in ("colvia", ".hrn/secret", "../outside", "a/../b", "a\\b"):
            ticket = copy.deepcopy(prepared["ticket"])
            ticket["document_refs"] = [{"path": path, "sha256": "a" * 64, "role": "input", "required": True}]
            values.append(ticket)
        before = self.bytes()
        for ticket in values:
            with self.subTest(ticket=ticket), self.assertRaises(ContractError):
                validate_ticket(ticket)
        self.assertEqual(before, self.bytes())

    def test_required_document_drift_and_optional_observation(self):
        path = self.target / "plan.md"; path.write_text("one\n")
        ref = {"path": "plan.md", "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
               "role": "plan", "required": True}
        prepared = self.prepare_cont(document_refs=[ref])
        path.write_text("two\n"); before = self.bytes()
        with self.assertRaisesRegex(ContractError, "stale"):
            self.apply_cont(prepared)
        self.assertEqual(before, self.bytes())
        ref["required"] = False
        self.apply_cont(self.prepare_cont(document_refs=[ref]))
        self.assertEqual([ref], self.state()["effective_ticket"]["document_refs"])

    def test_same_home_target_snapshot_and_nonrecursive_cycles(self):
        self.another()
        first = self.prepare_cont({"kind": "work", "target_work_id": "work-b"})
        self.apply_cont(first)
        second = self.cont.prepare("work-b", action="select", actor="owner", owner_statement="Synthetic Owner",
            reason="Return to source", request_id="cycle-b", observed_at=serial.TIME,
            choice={"kind": "work", "target_work_id": "work-a"})
        self.apply_cont(second)
        before = self.bytes()
        self.assertEqual("work-b", self.state()["effective_choice"]["target"]["object"]["id"])
        self.assertEqual("work-a", read_work(self.target, "work-b")["continuation"]["effective_choice"]["target"]["object"]["id"])
        self.assertEqual(before, self.bytes())

    def test_review_source_preserved_and_long_target_chain_is_nonrecursive(self):
        self.publish(self.proposal("submit-result"))
        before = self.lifecycle_bytes()
        self.apply_cont(self.prepare_cont())
        self.apply_cont(self.prepare_cont(action="withdraw"))
        self.assertEqual("review", read_work(self.target, "work-a")["state"])
        self.assertEqual(before, self.lifecycle_bytes())
        names = ["work-a"] + ["chain-" + str(i) for i in range(16)]
        for wid in names[1:]:
            self.another(wid)
        bases = {wid: read_work(self.target, wid, _with_continuation=False) for wid in names}
        template = self.prepare_cont()["ticket"]
        # Exact canonical retained fixture records; no product writer is bypassed in a live project.
        for number, wid in enumerate(names[1:]):
            ticket = copy.deepcopy(template)
            target = names[number + 2] if number + 2 < len(names) else "work-a"
            ticket.update(source=current_snapshot(bases[wid]), request_id="chain-choice-" + str(number),
                          expected_continuation_selection_ref=None,
                          choice={"kind": "work", "target": current_snapshot(bases[target])})
            choice, selection = records(ticket)
            root = self.target / ".hrn/work" / wid / "continuation"
            serial.put(root / "choices" / (choice["record_id"] + ".json"), choice)
            serial.put(root / "selections" / (selection["record_id"] + ".json"), selection)
            serial.put(root / "current.json", current_record(bases[wid]["identity"], record_ref(selection)))
        self.apply_cont(self.prepare_cont({"kind": "work", "target_work_id": names[1]}))
        before = self.bytes()
        import hv2ref.work as work_module
        native = work_module.read_work
        calls = []
        def observe(target, wid, **kwargs):
            calls.append((wid, kwargs))
            return native(target, wid, **kwargs)
        with patch.object(work_module, "read_work", observe):
            state = self.state()
        self.assertEqual(names[1], state["effective_choice"]["target"]["object"]["id"])
        self.assertEqual({"work-a", names[1]}, {wid for wid, _ in calls})
        self.assertTrue(all(kwargs.get("_with_continuation") is False for _, kwargs in calls))
        self.assertEqual(before, self.bytes())

    def test_continuation_tree_changed_during_read_is_unavailable(self):
        import hv2ref.continuation as module
        self.apply_cont(self.prepare_cont())
        raw = module._tree(self.target / ".hrn/work/work-a/continuation")
        changed = {**raw, "current.json": raw["current.json"] + b" "}
        before = self.bytes()
        with patch.object(module, "_tree", side_effect=[raw, changed]):
            with self.assertRaisesRegex(ContractError, "continuation changed while reading"):
                self.state()
        self.assertEqual(before, self.bytes())

    def test_pending_blocks_work_intent_and_candidate_writers(self):
        from hv2ref.candidates import CandidateStore
        from hv2ref.intent import WorkspaceIntentStore
        prepared = self.prepare_cont()
        with self.assertRaises(InjectedCrash):
            self.apply_cont(prepared, inject_at="after-choice")
        before = self.bytes()
        with self.assertRaisesRegex(ContractError, "pending"):
            self.publish(self.proposal("checkpoint"))
        intents = WorkspaceIntentStore(self.target, self.runtime)
        with self.assertRaisesRegex(ContractError, "pending"):
            intents._guard_pending()
        from tests.test_candidates import proposal
        candidates = CandidateStore(self.target, self.runtime)
        with self.assertRaisesRegex(ContractError, "pending"):
            candidates.mutate(proposal(self.target))
        self.assertEqual(before, self.bytes())

    def test_missing_current_unknown_and_torn_records_remain_unavailable(self):
        self.apply_cont(self.prepare_cont())
        home = self.target / ".hrn/work/work-a/continuation"
        current = (home / "current.json").read_bytes()
        (home / "current.json").unlink()
        before = self.bytes()
        with self.assertRaisesRegex(ContractError, "unavailable-current"):
            self.state()
        self.assertEqual(before, self.bytes())
        (home / "current.json").write_bytes(current)
        (home / "unknown.json").write_text("{}\n")
        before = self.bytes()
        with self.assertRaisesRegex(ContractError, "unknown continuation member"):
            self.store._all()
        self.assertEqual(before, self.bytes())
        (home / "unknown.json").unlink()
        choice = next((home / "choices").iterdir())
        choice.write_bytes(b"{")
        before = self.bytes()
        with self.assertRaises(ContractError):
            self.prepare_cont()
        self.assertEqual(before, self.bytes())

    def test_quota_includes_cancelled_normal_and_exact_last_cancellation(self):
        template = self.prepare_cont()["ticket"]
        base = read_work(self.target, "work-a")
        data = {"current.json": current_record(base["identity"], None)}
        final_ticket = None
        for i in range(256):
            ticket = copy.deepcopy(template)
            ticket["request_id"] = "quota-" + str(i)
            ticket["expected_continuation_selection_ref"] = data["current.json"]["selection_ref"]
            choice, selection = records(ticket)
            data["choices/" + choice["record_id"] + ".json"] = choice
            if i < 255:
                data["selections/" + selection["record_id"] + ".json"] = selection
                data["current.json"] = current_record(base["identity"], record_ref(selection))
            else:
                final_ticket = ticket
        self.assertEqual(0, graph(base["identity"], data)["usage"]["normal_remaining"])
        home = self.target / ".hrn/work/work-a/continuation"
        for name, record in data.items():
            serial.put(home / name, record)
        before = self.bytes()
        with self.assertRaises(ContractError):
            self.prepare_cont()
        self.assertEqual(before, self.bytes())
        original, _ = records(final_ticket)
        cancel = self.prepare_cont(action="cancel-pending", supersedes_choice_ref=record_ref(original))
        state = self.apply_cont(cancel)
        self.assertEqual({"normal_limit": 256, "normal_used": 256, "normal_remaining": 0}, state["usage"])
        self.assertEqual({"kind": "none"}, state["effective_choice"])
        from hv2ref.view import _continuation
        base = read_work(self.target, "work-a")
        display = "\n".join(_continuation(self.target, base, {"work-a": base}))
        self.assertIn("256회 한도에 도달", display)
        self.assertIn(r"normal\_remaining: 0", display)
        self.assertIn("초기화하지 마세요", display)
        with self.assertRaisesRegex(ContractError, "quota"):
            self.prepare_cont(action="withdraw")

    def test_current_is_not_reconstructed_from_newer_timestamp(self):
        first = self.prepare_cont()
        self.apply_cont(first)
        second = self.prepare_cont(action="withdraw", observed_at="2025-01-01T00:00:00Z")
        self.apply_cont(second)
        self.assertIsNone(self.state()["effective_choice"])
        home = self.target / ".hrn/work/work-a/continuation"
        state = self.state()
        bad = copy.deepcopy(state["data"])
        bad["current.json"]["selection_ref"]["sha256"] = "0" * 64
        serial.put(home / "current.json", bad["current.json"])
        with self.assertRaises(ContractError):
            self.state()

    def test_request_reuse_and_cross_home_refs_are_refused(self):
        first = self.prepare_cont()
        self.apply_cont(first)
        with self.assertRaisesRegex(ContractError, "request ID"):
            self.prepare_cont(request_id=first["ticket"]["request_id"])
        self.another()
        prepared = self.prepare_cont({"kind": "work", "target_work_id": "work-b"})
        changed = copy.deepcopy(prepared["ticket"])
        changed["choice"]["target"]["object"]["authority_home_id"] = "other"
        with self.assertRaises(ContractError):
            validate_ticket(changed)

    def test_reader_ignores_access_time_but_refuses_changed_content_metadata(self):
        from types import SimpleNamespace
        from hv2ref.continuation import _read_file
        path = self.target / "observation.json"
        path.write_bytes(b"{}\n")
        original = Path.lstat
        calls = [0]
        def changing(field):
            def observed(value):
                result = original(value)
                attributes = {name: getattr(result, name) for name in dir(result) if name.startswith("st_")}
                calls[0] += 1
                attributes[field] += calls[0]
                return SimpleNamespace(**attributes)
            return observed
        with patch.object(Path, "lstat", changing("st_atime_ns")):
            self.assertEqual(b"{}\n", _read_file(path, 4096))
        with patch.object(Path, "lstat", changing("st_mtime_ns")):
            with self.assertRaisesRegex(ContractError, "descriptor changed"):
                _read_file(path, 4096)
