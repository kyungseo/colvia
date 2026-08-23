from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from hv2ref.errors import InjectedCrash
from hv2ref.jsonio import canonical_json_bytes
from hv2ref.product import ProductStore, source_root

from tests.test_productization import git_init, snapshot


def run_launcher(target: Path, *args: str) -> dict[str, object]:
    result = subprocess.run(
        [str(target / "hv2"), *args], cwd=target, check=True, text=True, capture_output=True
    )
    return json.loads(result.stdout)


def intent_content() -> dict[str, object]:
    known = lambda value: {"status": "known", "value": value}
    return {
        "acceptance_authority": "OWNER-LOCAL-001",
        "actor": "OWNER-LOCAL-001",
        "facets": {
            "acceptance_oracle": known(["repository-only acceptance passes"]),
            "destination": known("project-local Harness v2 state"),
            "expected_outcome": known(["exact revision is human accepted"]),
            "forbidden_scope": known(["public promotion", "enterprise authority"]),
            "goal": known("exercise the first Guided Intent"),
            "scope": known(["one disposable repository"]),
        },
        "gaps": [],
        "statements": [
            {"kind": "fact", "owner": "repository", "text": "The target is disposable."},
            {"kind": "human-decision", "owner": "OWNER-LOCAL-001", "text": "This exact intent may be accepted."},
        ],
    }


class ProductizationAcceptanceTests(unittest.TestCase):
    def test_installed_launcher_runs_first_intent_end_to_end(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            target = Path(raw) / "target"
            git_init(target)
            ProductStore(target).init(source_root(), apply=True)
            status = run_launcher(target, "status")
            self.assertEqual("pass", status["classification"])
            input_path = target / "intent-input.json"
            input_path.write_bytes(canonical_json_bytes(intent_content()))
            drafted = run_launcher(
                target,
                "create-intent-draft",
                "--target", str(target),
                "--intent-id", "INTENT-001",
                "--sequence", "1",
                "--observed-at", "2026-08-23T12:00:00+09:00",
                "--input", str(input_path),
            )
            accepted = run_launcher(
                target,
                "accept-intent",
                "--target", str(target),
                "--intent-id", "INTENT-001",
                "--revision-id", str(drafted["revision_id"]),
                "--revision-sha256", str(drafted["revision_sha256"]),
                "--acceptance-id", "acceptance-0001",
                "--actor", "OWNER-LOCAL-001",
                "--observed-at", "2026-08-23T12:01:00+09:00",
            )
            verified = run_launcher(target, "verify-intent", "--target", str(target), "--intent-id", "INTENT-001")
            final_status = run_launcher(target, "status")
            self.assertEqual("selection-0001", accepted["selection_ref"]["id"])
            self.assertEqual("pass", verified["classification"])
            self.assertEqual("revision-0001", verified["current_accepted_revision_id"])
            self.assertEqual("pass", final_status["classification"])
            self.assertEqual([], list((target / ".harness-v2-product/releases").rglob("*.pyc")))
            self.assertEqual([], list((target / ".harness-v2-product/releases").rglob("__pycache__")))

    def test_detach_preview_and_plain_auditor_preserve_project_truth(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            target = Path(raw) / "target"
            git_init(target)
            store = ProductStore(target)
            store.init(source_root(), apply=True)
            state_before = snapshot(target / ".harness-v2")
            intent_before = snapshot(target / ".harness-v2-intents")
            whole_before = snapshot(target)
            preview = store.detach(apply=False)
            self.assertEqual("preview", preview["classification"])
            self.assertEqual(whole_before, snapshot(target))
            detached = store.detach(apply=True)
            self.assertEqual("detached", detached["classification"])
            documentation = detached["detach_receipt"]["documentation"]
            self.assertEqual("not-guaranteed", documentation["availability_after_detach"])
            self.assertEqual(detached["detach_receipt"]["active_release_ref"], documentation["release_ref"])
            self.assertIn("docs/MANUAL-OPERATION.md", documentation["required_relative_paths"])
            self.assertEqual(state_before, snapshot(target / ".harness-v2"))
            self.assertEqual(intent_before, snapshot(target / ".harness-v2-intents"))
            auditor = source_root() / "tests/fixtures/product_plain_auditor.py"
            result = subprocess.run([sys.executable, "-B", str(auditor), str(target)], check=True, text=True, capture_output=True)
            self.assertEqual("pass", json.loads(result.stdout)["classification"])

    def test_detach_interruption_is_recoverable(self) -> None:
        for point in ("after-receipt", "after-launcher"):
            with self.subTest(point=point), tempfile.TemporaryDirectory() as raw:
                target = Path(raw) / "target"
                git_init(target)
                store = ProductStore(target)
                store.init(source_root(), apply=True)
                with self.assertRaises(InjectedCrash):
                    store.detach(apply=True, inject_at=point)
                result = store.detach(apply=True)
                self.assertEqual("detached", result["classification"])
                self.assertTrue((target / ".harness-v2-detached.json").is_file())

    def test_repository_document_links_are_local_and_resolvable(self) -> None:
        markdown = [source_root() / "README.md", source_root() / "AGENTS.md", *sorted((source_root() / "docs").glob("*.md"))]
        link_pattern = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
        for document in markdown:
            for link in link_pattern.findall(document.read_text(encoding="utf-8")):
                if "://" in link or link.startswith("#"):
                    continue
                destination = (document.parent / link.split("#", 1)[0]).resolve()
                self.assertTrue(destination.exists(), f"{document.name}: {link}")

    def test_product_help_hides_crash_injection_options(self) -> None:
        for command in ("init", "update", "rollback", "detach"):
            with self.subTest(command=command):
                result = subprocess.run(
                    [str(source_root() / "hv2"), command, "--help"],
                    cwd=source_root(),
                    check=True,
                    text=True,
                    capture_output=True,
                )
                self.assertNotIn("--inject-at", result.stdout)

    def test_product_error_codes_are_documented(self) -> None:
        implementation = "\n".join(
            (source_root() / relative).read_text(encoding="utf-8")
            for relative in ("hv2", "src/hv2ref/product.py")
        )
        codes = sorted(set(re.findall(r"HV2-PRODUCT-[A-Z0-9-]+", implementation)))
        reference = (source_root() / "docs/REFERENCE.md").read_text(encoding="utf-8")
        self.assertGreater(len(codes), 0)
        self.assertEqual([], [code for code in codes if code not in reference])


if __name__ == "__main__":
    unittest.main()
