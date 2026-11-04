"""Ordinary file-edit shortcuts over the same immutable intent and Work graphs."""
import time
import unittest
from unittest.mock import patch

from tests import test_general_work_recovery as fixtures
from hv2ref.cli import workspace_parser
from hv2ref import continuation
from hv2ref.errors import ContractError, InjectedCrash
from hv2ref.work import WorkStore, ordinary_command, read_work


class OrdinaryFlowTests(unittest.TestCase):
    def setUp(self):
        fixture = fixtures.SerialWriterTests()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        self.target = fixture.target
        self.parser = workspace_parser(self.target)
        verifier = patch("hv2ref.product.require_workspace_runtime", fixture.store.runtime_check)
        verifier.start()
        self.addCleanup(verifier.stop)

    def call(self, action, *argv, name="report"):
        args = self.parser.parse_args(["ordinary", action, name, *argv])
        return ordinary_command(self.target, args)

    def plan(self, *paths, name="report"):
        files = [arg for path in paths for arg in ("--file", path)]
        return self.call("plan", "--owner", "owner", "--goal", "Write report", "--check",
                         "Match the source", "--exclude", "Keep the source", *files, name=name)

    def test_review_then_single_decision_and_replay(self):
        plan = self.plan("report.md")
        with self.assertRaises(ContractError):
            self.call("start", "--approval", "0"*64)
        approval = self.call("approve", "--receipt", plan["receipt"])
        self.assertEqual(approval, self.call("approve", "--receipt", plan["receipt"]))
        self.assertEqual(approval, self.call("status"))
        with self.assertRaises(ContractError):
            self.call("plan-review")
        baseline = self.call("start", "--approval", approval["selection"])
        self.assertEqual(self.call("status")["selection"], baseline["selection"])
        (self.target / "report.md").write_text("result")
        args = ("--baseline", baseline["selection"], "--summary", "Ready", "--checked", "Source matches")
        extra = self.target / "b"
        extra.write_text("outside")
        with self.assertRaises(ContractError):
            self.call("submit", *args)
        extra.unlink()
        submitted = self.call("submit", *args)
        self.assertEqual(submitted["state"], "review")
        review = self.call("review")
        self.assertEqual(review["review"]["files"], ["report.md"])
        self.assertIn("마무리", review["question"])
        self.assertFalse(read_work(self.target, "report")["decisions"])
        (self.target / "report.md").write_text("later")
        with self.assertRaises(ContractError):
            self.call("accept", "--receipt", review["receipt"])
        (self.target / "report.md").write_text("result")
        done = self.call("accept", "--receipt", review["receipt"])
        self.assertEqual(done["state"], "completed")
        self.assertEqual(done, self.call("accept", "--receipt", review["receipt"]))
        historical = self.call("review", "--selection", submitted["selection"])
        self.assertEqual(historical["state"], "completed")
        self.assertNotIn("receipt", historical)
        self.assertEqual(len(read_work(self.target, "report")["decisions"]), 1)

    def test_plan_checks_record_size_before_writing(self):
        from hv2ref.jsonio import canonical_json_bytes
        from hv2ref.work import _ordinary_manifest_size
        size = len(canonical_json_bytes({"example": "three"}))
        for limit in (size + 1, size, size - 1):
            with self.subTest(limit=limit), patch("hv2ref.jsonio.MAX_JSON_BYTES", limit):
                if limit >= size:
                    self.assertEqual(_ordinary_manifest_size({"example": "three"}), size)
                else:
                    with self.assertRaises(ContractError) as refusal:
                        _ordinary_manifest_size({"example": "three"})
                    self.assertEqual(refusal.exception.code, "HV2-JSON-LIMIT")
        with patch("hv2ref.work._ordinary_manifest_size", side_effect=ContractError("HV2-JSON-LIMIT", "size")):
            with self.assertRaises(ContractError):
                self.plan("report.md")
        self.assertFalse((self.target / ".hrn/intents/report").exists())
        self.assertFalse((self.target / ".hrn/work/report").exists())
        from hv2ref.jsonio import MAX_JSON_BYTES
        with patch("hv2ref.work._ordinary_manifest_size", return_value=MAX_JSON_BYTES - 8):
            plan = self.plan("report.md")
        self.assertIn("8바이트", plan["size_notice"])

    def test_change_counts_keep_distinct_paths_for_moves(self):
        from hv2ref.work import _ordinary_change_summary
        changes = [{"path": f"src/{i}/a", "pre": {}, "post": {}} for i in range(6)]
        changes.extend([{"path": "old", "pre": {}, "post": None},
                        {"path": "new", "pre": None, "post": {}}])
        summary = _ordinary_change_summary(changes)
        self.assertEqual((summary["added"], summary["modified"], summary["deleted"], summary["total"]), (1, 6, 1, 8))
        self.assertEqual(summary["top_folders"]["."], 2)
        self.assertEqual(summary["other_folders"], 2)

    def test_explicit_work_and_scope(self):
        first = self.plan("brief.md")
        multiple = self.call("plan", "--goal", "Review notes", "--owner", "owner", "--file", "notes.md",
                             "--check", "Totals", "--check", "Layout", "--exclude", "CSV", "--exclude", "Pricing",
                             name="notes")
        self.assertIn("Totals\nLayout", multiple["review"].values())
        self.assertIn("CSV\nPricing", multiple["review"].values())
        with self.assertRaises(ContractError):
            self.call("approve", "--receipt", first["receipt"], name="notes")
        (self.target / "Reports").mkdir()
        for path in ("reports/new.md", "Reports", "*.md", ".hrn/abc", "colvia"):
            with self.subTest(path=path), self.assertRaises(ContractError):
                self.plan(path, name="invalid")

    def edited_draft(self):
        plan = self.plan("report.md")
        approval = self.call("approve", "--receipt", plan["receipt"])
        baseline = self.call("start", "--approval", approval["selection"])
        (self.target / "report.md").write_text("Draft")
        return ["--baseline", baseline["selection"], "--summary", "Ready", "--checked", "Checked"]

    def test_correction_bound_to_review_and_recovery(self):
        self.call("submit", *self.edited_draft())
        receipt = self.call("review")["receipt"]
        change = ("revise", "--receipt", receipt, "--reason", "Clarify the last step")
        doc = self.target / "report.md"
        doc.write_text("Unreviewed")
        with self.assertRaises(ContractError):
            self.call(*change)
        self.assertFalse(read_work(self.target, "report")["decisions"])
        doc.write_text("Draft")
        with patch.object(WorkStore, "publish", side_effect=OSError("interrupted before baseline")):
            with self.assertRaises(OSError):
                self.call(*change)
        self.assertEqual(self.call("status")["state"], "rejected")
        with self.assertRaises(ContractError):
            self.call(*change[:-1], "Replace the whole draft")
        self.assertEqual(self.call("status")["recovery_action"], "resume-revision")
        baseline = self.call("resume-revision")
        self.assertEqual(self.call(*change), baseline)
        doc.write_text("Clarified")
        args = ("--baseline", baseline["selection"], "--checked", "Checked", "--summary", "Clarified")
        other = self.target / "other"
        other.write_text("out of scope")
        with self.assertRaises(ContractError):
            self.call("submit", *args)
        other.unlink()
        self.assertEqual(self.call("submit", *args)["state"], "review")
        for old in [change, ("accept", "--receipt", receipt)]:
            with self.assertRaises(ContractError):
                self.call(*old)
        new = self.call("review")["receipt"]
        self.assertEqual(self.call("accept", "--receipt", new)["state"], "completed")
        with self.assertRaises(ContractError):
            self.call("revise", "--receipt", new, "--reason", "Again")

    def test_clickable_delivery_and_failed_receiver_preserve_result(self):
        args = self.edited_draft()
        def handoff(action, token, *options, value=None):
            parsed = self.parser.parse_args(["handoff", action, token, *options])
            return continuation.delivery_command(self.target, parsed, value)
        runtime = WorkStore(self.target)._runtime()
        with patch("hv2ref.product.require_workspace_runtime", return_value=dict(runtime, inventory_id="continuation-1")):
            packet = self.call("prepare-delivery", *args, "--expires", str(int(time.time()) + 600))
            self.assertEqual(self.call("status")["state"], "active")
            self.assertFalse(continuation._delivery_rows(self.target, "report"))
            self.assertIsInstance(packet["preview"]["receiver_available_at_preview"], bool)
            token = packet["confirm_token"]
            with self.assertRaises(ContractError):
                handoff("start", token, value=dict(packet, preview={}))
            competing = self.call("prepare-delivery", *args, "--expires", str(int(time.time()) + 900))
            with patch.object(continuation, "_delivery_command") as worker:
                handoff("start", token, value=packet)
                with self.assertRaises(ContractError):
                    handoff("start", competing["confirm_token"], value=competing)
                worker.assert_called_once()
            from hv2ref.workspace import guard_delivery_transition
            with self.assertRaises(ContractError):
                guard_delivery_transition(self.target)
            with patch.object(continuation, "_click_receiver", return_value=None), patch.object(continuation, "_delivery_notify") as generic:
                self.assertEqual(handoff("_step", token, "--epoch", "1")["status"], "recorded")
                generic.assert_not_called()
            received = handoff("show", token)
            self.assertEqual((received["status"], received["notification"]), ("done", "unavailable"))
            self.assertEqual(self.call("review")["review"]["summary"], "Ready")
            self.assertEqual(handoff("start", token, value=packet), received)
            first = received["result"]["selection"]["sha256"]
            reviewed = self.call("review", "--selection", first)
            baseline = self.call("revise", "--receipt", reviewed["receipt"], "--reason", "Clarify timing")
            (self.target / "report.md").write_text("Clarified timing")
            revised = self.call("prepare-delivery", "--baseline", baseline["selection"], "--summary", "Clarified",
                                "--checked", "Checked", "--expires", str(int(time.time()) + 600))
            second = revised["confirm_token"]
            self.assertNotEqual(second, token)
            with patch.object(continuation, "_delivery_command"):
                handoff("start", second, value=revised)
            with patch.object(continuation, "_click_receiver", return_value=None):
                handoff("_step", second, "--epoch", "1")
            self.assertEqual(handoff("show", token)["result"], received["result"])
            self.assertNotEqual(handoff("show", second)["result"]["selection"]["sha256"], first)
            with self.assertRaises(ContractError):
                self.call("review", "--selection", first)
            self.assertEqual(self.call("review")["review"]["summary"], "Clarified")



    def test_handoff_exact_size_limit(self):
        from hv2ref.jsonio import canonical_json_bytes
        request = dict(work_id="report", action="summary", payload=None, expires=int(time.time()) + 600,
                       ask=False, notify=False)
        source = {"label": ""}
        with patch.object(continuation, "_delivery_observe", return_value=(source, {})):
            overhead = len(canonical_json_bytes(continuation._delivery_validate(self.target, request)))
            for size in (2**20 - 1, 2**20, 2**20 + 1):
                source["label"] = "a" * (size - overhead)
                if size <= 2**20:
                    plan = continuation._delivery_validate(self.target, request)
                    self.assertEqual(len(canonical_json_bytes(plan)), size)
                else:
                    with self.assertRaises(ContractError) as refusal:
                        continuation._delivery_validate(self.target, request)
                    self.assertEqual(refusal.exception.code, "COLVIA-DELIVERY")

    def test_compact_delivery_recovers_after_publish_before_receipt(self):
        args = self.edited_draft()
        runtime = WorkStore(self.target)._runtime()
        def handoff(action, token, *options, value=None):
            parsed = self.parser.parse_args(["handoff", action, token, *options])
            return continuation.delivery_command(self.target, parsed, value)
        original = WorkStore.publish
        def interrupt_after_publish(store, *args, **kwargs):
            return original(store, *args, **kwargs, inject_at="after-current")
        with patch("hv2ref.product.require_workspace_runtime", return_value=dict(runtime, inventory_id="continuation-1")):
            packet = self.call("prepare-delivery", *args, "--expires", str(int(time.time()) + 600))
            token = packet["confirm_token"]
            with patch.object(continuation, "_delivery_command"):
                handoff("start", token, value=packet)
            with patch.object(WorkStore, "publish", interrupt_after_publish), patch.object(continuation, "_click_receiver", return_value=None):
                handoff("_step", token, "--epoch", "1")
            self.assertEqual(handoff("show", token)["status"], "reconcile")
            result = handoff("inspect", token)
            self.assertEqual(result["status"], "done")
            self.assertEqual(result["result"]["selection"]["sha256"], self.call("status")["selection"])
            self.assertEqual(handoff("start", token, value=packet), result)

    def test_prepared_worker_refuses_changed_files(self):
        args = self.edited_draft()
        runtime = WorkStore(self.target)._runtime()
        with patch("hv2ref.product.require_workspace_runtime", return_value=dict(runtime, inventory_id="continuation-1")):
            packet = self.call("prepare-delivery", *args, "--expires", str(int(time.time()) + 600))
            (self.target / "report.md").write_text("Changed after preview")
            with self.assertRaises(ContractError):
                continuation._delivery_report(self.target, packet["plan"])
            self.assertEqual(self.call("status")["state"], "active")

    def test_interrupted_decision_preserves_only_the_recorded_choice(self):
        for point in ("after-decision", "after-selection", "after-staged-current"):
            for action in ("accept", "revise"):
                with self.subTest(point=point, action=action):
                    fixture = OrdinaryFlowTests()
                    fixture.setUp()
                    try:
                        fixture.call("submit", *fixture.edited_draft())
                        receipt = fixture.call("review")["receipt"]
                        args = ["--receipt", receipt]
                        if action == "revise":
                            args += ["--reason", "Clarify timing"]
                        original = WorkStore.apply
                        def interrupt(store, ticket, **kwargs):
                            return original(store, ticket, inject_at=point, **kwargs)
                        with patch.object(WorkStore, "apply", interrupt), self.assertRaises(InjectedCrash):
                            fixture.call(action, *args)
                        with self.assertRaises(ContractError):
                            fixture.call("review")
                        if action == "revise":
                            self.assertEqual(fixture.call("status")["recovery_action"], "resume-revision")
                            self.assertEqual(fixture.call("resume-revision")["state"], "active")
                        else:
                            with self.assertRaises(ContractError):
                                fixture.call("revise", "--receipt", receipt, "--reason", "Different decision")
                            self.assertEqual(fixture.call("status")["recovery_action"], "resume-accept")
                            with self.assertRaises(ContractError):
                                fixture.call("resume-revision")
                            doc = fixture.target / "report.md"
                            doc.write_text("Human change")
                            with self.assertRaises(ContractError):
                                fixture.call("resume-accept")
                            self.assertEqual(doc.read_text(), "Human change")
                            doc.write_text("Draft")
                            self.assertEqual(fixture.call("resume-accept")["state"], "completed")
                            self.assertEqual(fixture.call(action, *args)["state"], "completed")
                        self.assertEqual(len(read_work(fixture.target, "report")["decisions"]), 1)
                    finally:
                        fixture.doCleanups()
