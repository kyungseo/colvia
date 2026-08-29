from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from hv2ref.errors import ContractError, InjectedCrash
from hv2ref.jsonio import load_json, replace_json
from hv2ref.parallel import ParallelStateStore
from hv2ref.product import MANAGED_PATHS, ProductStore, source_root
from hv2ref.state import StateStore


def git_init(path: Path) -> None:
    path.mkdir()
    subprocess.run(["git", "init", "-b", "main"], cwd=path, check=True, capture_output=True)


def git_commit_all(path: Path, message: str = "fixture: persist product binding") -> None:
    subprocess.run(["git", "config", "user.name", "Harness v2 Product Fixture"], cwd=path, check=True)
    subprocess.run(
        ["git", "config", "user.email", "harness-v2-product@example.invalid"], cwd=path, check=True
    )
    subprocess.run(["git", "add", "-A"], cwd=path, check=True)
    subprocess.run(["git", "commit", "-m", message], cwd=path, check=True, capture_output=True)


def snapshot(root: Path) -> dict[str, tuple[str, int]]:
    result: dict[str, tuple[str, int]] = {}
    for path in sorted(root.rglob("*")):
        if path.is_file() and ".git" not in path.relative_to(root).parts:
            result[path.relative_to(root).as_posix()] = (
                hashlib.sha256(path.read_bytes()).hexdigest(),
                path.stat().st_mode & 0o777,
            )
    return result


def candidate_copy(destination: Path, marker: bytes = b"\nD1 update fixture.\n") -> Path:
    for relative in MANAGED_PATHS:
        source = source_root() / relative
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    with (destination / "docs/MAINTAINING.md").open("ab") as handle:
        handle.write(marker)
    os.chmod(destination / "hv2", 0o755)
    return destination


class ProductizationLifecycleTests(unittest.TestCase):
    def test_preview_is_zero_mutation_and_release_is_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            base = Path(raw)
            first, second = base / "first", base / "second"
            git_init(first)
            git_init(second)
            before = snapshot(first)
            first_preview = ProductStore(first).init(source_root(), apply=False)
            second_preview = ProductStore(second).init(source_root(), apply=False)
            self.assertEqual("preview", first_preview["classification"])
            self.assertEqual(0, first_preview["mutation"])
            self.assertEqual(before, snapshot(first))
            self.assertEqual(first_preview["release_ref"], second_preview["release_ref"])

    def test_init_is_idempotent_and_owns_only_product_binding(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            target = Path(raw) / "target"
            git_init(target)
            store = ProductStore(target)
            result = store.init(source_root(), apply=True)
            again = store.init(source_root(), apply=True)
            self.assertEqual("pass", result["classification"])
            self.assertEqual("already-initialized", again["result"])
            plan = load_json(target / ".harness-v2-product/init-plan.json", require_canonical=True)
            state = load_json(target / ".harness-v2/authority.json", require_canonical=True)
            intent = load_json(target / ".harness-v2-intents/authority.json", require_canonical=True)
            self.assertEqual(plan["state_authority_home_id"], state["authority_home_id"])
            self.assertEqual(plan["intent_authority_home_id"], intent["authority_home_id"])
            self.assertNotEqual(state["authority_home_id"], intent["authority_home_id"])

    def test_status_and_doctor_are_read_only(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            target = Path(raw) / "target"
            git_init(target)
            store = ProductStore(target)
            store.init(source_root(), apply=True)
            before = snapshot(target)
            status = store.status()
            doctor = store.doctor()
            self.assertEqual("pass", status["classification"])
            self.assertEqual("pass", doctor["classification"])
            self.assertTrue((target / status["documentation_root"] / "GETTING-STARTED.md").is_file())
            self.assertEqual(before, snapshot(target))

    def test_init_interruption_retries_to_one_binding(self) -> None:
        for point in ("after-release", "after-plan", "after-state", "after-intent", "after-launcher", "after-switch"):
            with self.subTest(point=point), tempfile.TemporaryDirectory() as raw:
                target = Path(raw) / "target"
                git_init(target)
                store = ProductStore(target)
                with self.assertRaises(InjectedCrash):
                    store.init(source_root(), apply=True, inject_at=point)
                recovered = store.init(source_root(), apply=True)
                self.assertEqual("pass", recovered["classification"])
                self.assertEqual("pass", store.status()["classification"])

    def test_update_and_rollback_do_not_rewrite_project_truth(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            base = Path(raw)
            target = base / "target"
            git_init(target)
            store = ProductStore(target)
            initial = store.init(source_root(), apply=True)["release_ref"]
            truth_before = snapshot(target / ".harness-v2") | snapshot(target / ".harness-v2-intents")
            candidate = candidate_copy(base / "candidate")
            preview_before = snapshot(target)
            preview = store.update(candidate, apply=False)
            self.assertEqual("preview", preview["classification"])
            self.assertEqual(preview_before, snapshot(target))
            updated = store.update(candidate, apply=True)
            self.assertNotEqual(initial, updated["release_ref"])
            self.assertEqual(1, updated["mutation"])
            self.assertEqual("committed", updated["result"])
            self.assertEqual(updated["classification"], updated["status"]["classification"])
            self.assertEqual(initial, updated["prior_release_ref"])
            self.assertEqual(truth_before, snapshot(target / ".harness-v2") | snapshot(target / ".harness-v2-intents"))
            rolled_back = store.rollback(None, apply=True)
            self.assertEqual(initial, rolled_back["release_ref"])
            self.assertEqual(1, rolled_back["mutation"])
            self.assertEqual("committed", rolled_back["result"])
            self.assertEqual(rolled_back["classification"], rolled_back["status"]["classification"])
            self.assertEqual(updated["release_ref"], rolled_back["prior_release_ref"])
            self.assertEqual(truth_before, snapshot(target / ".harness-v2") | snapshot(target / ".harness-v2-intents"))

    def test_generation_two_binding_is_admitted_and_unregistered_plan_item_fails_before_switch(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            base = Path(raw)
            target = base / "target"
            git_init(target)
            store = ProductStore(target)
            initial = store.init(source_root(), apply=True)["release_ref"]
            git_commit_all(target)
            base_commit = subprocess.run(
                ["git", "rev-parse", "HEAD"], cwd=target, check=True, text=True, capture_output=True
            ).stdout.strip()
            base_tree = subprocess.run(
                ["git", "rev-parse", "HEAD^{tree}"], cwd=target, check=True, text=True, capture_output=True
            ).stdout.strip()
            ParallelStateStore(target).activate_parallel(
                repository_id="REPOSITORY-PRODUCT-FIXTURE",
                item_id="item-0001",
                finalizer="ACTOR-PRODUCT-FINALIZER",
                worktree_id="integration-main",
                branch="main",
                base_commit=base_commit,
                base_tree=base_tree,
                observed_at="2026-08-23T00:00:00Z",
                worktree_root=target,
            )
            self.assertEqual("pass", store.status()["classification"])

            candidate = candidate_copy(base / "candidate")
            update_process = subprocess.run(
                [str(target / "hv2"), "update", "--source", str(candidate), "--apply"],
                cwd=target,
                check=False,
                text=True,
                capture_output=True,
            )
            self.assertEqual(0, update_process.returncode)
            updated = json.loads(update_process.stdout)
            self.assertEqual("pass", updated["classification"])
            self.assertEqual(1, updated["mutation"])
            self.assertEqual("committed", updated["result"])
            rollback_process = subprocess.run(
                [str(target / "hv2"), "rollback", "--apply"],
                cwd=target,
                check=False,
                text=True,
                capture_output=True,
            )
            self.assertEqual(0, rollback_process.returncode)
            rolled_back = json.loads(rollback_process.stdout)
            self.assertEqual("pass", rolled_back["classification"])
            self.assertEqual(initial, rolled_back["release_ref"])

            plan_path = target / ".harness-v2-product/init-plan.json"
            plan = load_json(plan_path, require_canonical=True)
            plan["item_id"] = "item-unregistered"
            replace_json(plan_path, plan)
            active_before = (target / ".harness-v2-product/active-release.json").read_bytes()
            second_candidate = candidate_copy(base / "second-candidate", marker=b"\nsecond candidate\n")
            with self.assertRaisesRegex(ContractError, "HV2-PRODUCT-STATE-BINDING"):
                store.update(second_candidate, apply=True)
            self.assertEqual(active_before, (target / ".harness-v2-product/active-release.json").read_bytes())

    def test_new_generation_one_records_use_project_local_identity_vocabulary(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            target = Path(raw) / "target"
            git_init(target)
            store = StateStore(target)
            store.initialize("authority-product-fixture", "item-0001", "2026-08-23T00:00:00Z")
            values = store._values_for("update", 1, None, None, None, None)
            self.assertEqual("PROJECT-LOCAL-EVIDENCE-001", values["evidence"]["production_identity_series"])
            self.assertEqual("PROJECT-LOCAL-FINALIZER-001", values["ownership"]["finalizer"])
            self.assertEqual("PROJECT-LOCAL-WRITER-001", values["ownership"]["writer"])

    def test_update_interruption_preserves_or_completes_selector(self) -> None:
        for point in ("after-release", "after-receipt", "after-switch"):
            with self.subTest(point=point), tempfile.TemporaryDirectory() as raw:
                base = Path(raw)
                target = base / "target"
                git_init(target)
                store = ProductStore(target)
                initial = store.init(source_root(), apply=True)["release_ref"]
                candidate = candidate_copy(base / "candidate", marker=f"\n{point}\n".encode())
                with self.assertRaises(InjectedCrash):
                    store.update(candidate, apply=True, inject_at=point)
                status = store.status()
                self.assertEqual("pass", status["classification"])
                if point == "after-switch":
                    self.assertNotEqual(initial, status["release_ref"])
                else:
                    self.assertEqual(initial, status["release_ref"])
                    self.assertEqual("pass", store.update(candidate, apply=True)["classification"])


if __name__ == "__main__":
    unittest.main()
