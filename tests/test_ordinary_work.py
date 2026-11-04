"""Ordinary file-edit shortcuts over the same immutable intent and Work graphs."""
import unittest
from unittest.mock import patch

from tests import test_general_work_recovery as fixtures
from hv2ref.cli import workspace_parser
from hv2ref.errors import ContractError
from hv2ref.work import ordinary_command, read_work


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
        self.plan("notes.md", name="notes")
        with self.assertRaises(ContractError):
            self.call("approve", "--receipt", first["receipt"], name="notes")
        (self.target / "Reports").mkdir()
        for path in ("reports/new.md", "Reports", "*.md", ".hrn/abc", "colvia"):
            with self.subTest(path=path), self.assertRaises(ContractError):
                self.plan(path, name="invalid")
