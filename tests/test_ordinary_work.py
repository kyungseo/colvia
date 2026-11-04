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
        self.assertEqual(self.call("submit", *args)["state"], "review")
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
        self.assertEqual(len(read_work(self.target, "report")["decisions"]), 1)

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
        self.assertIn("resume-revision", self.call("status")["next"])
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
            with patch.object(continuation, "_delivery_command"):
                handoff("start", token, value=packet)
            with patch.object(continuation, "_click_receiver", return_value=None), patch.object(continuation, "_delivery_notify") as generic:
                self.assertEqual(handoff("_step", token, "--epoch", "1")["status"], "recorded")
                generic.assert_not_called()
            received = handoff("show", token)
            self.assertEqual((received["status"], received["notification"]), ("done", "unavailable"))
            self.assertEqual(self.call("review")["review"]["summary"], "Ready")
            self.assertEqual(handoff("start", token, value=packet), received)


    def test_prepared_worker_refuses_changed_files(self):
        args = self.edited_draft()
        runtime = WorkStore(self.target)._runtime()
        with patch("hv2ref.product.require_workspace_runtime", return_value=dict(runtime, inventory_id="continuation-1")):
            packet = self.call("prepare-delivery", *args, "--expires", str(int(time.time()) + 600))
            (self.target / "report.md").write_text("Changed after preview")
            with self.assertRaises(ContractError):
                continuation._delivery_report(self.target, packet["plan"])
            self.assertEqual(self.call("status")["state"], "active")

    def test_resume_after_only_the_rejection_record_was_written(self):
        self.call("submit", *self.edited_draft())
        receipt = self.call("review")["receipt"]
        original = WorkStore.apply
        def stop_after_decision(store, ticket, **kwargs):
            return original(store, ticket, inject_at="after-decision", **kwargs)
        with patch.object(WorkStore, "apply", stop_after_decision):
            with self.assertRaises(InjectedCrash):
                self.call("revise", "--receipt", receipt, "--reason", "Clarify the last step")
        self.assertIn("resume-revision", self.call("status")["next"])
        self.assertEqual(self.call("resume-revision")["state"], "active")
        self.assertEqual(len(read_work(self.target, "report")["decisions"]), 1)
