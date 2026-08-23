from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from hv2ref.errors import ContractError
from hv2ref.jsonio import load_json
from hv2ref.product import ProductStore, source_root

from tests.test_productization import candidate_copy, git_commit_all, git_init, snapshot


class ProductizationSafetyTests(unittest.TestCase):
    def test_tracked_binding_survives_clone_and_worktree_without_runtime_staging(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            base = Path(raw)
            origin = base / "origin"
            clone = base / "clone"
            worktree = base / "worktree"
            git_init(origin)
            ProductStore(origin).init(source_root(), apply=True)
            (origin / ".gitignore").write_text(".harness-v2-product/staging/\n", encoding="utf-8")
            git_commit_all(origin)
            subprocess.run(["git", "clone", str(origin), str(clone)], check=True, capture_output=True)
            subprocess.run(
                ["git", "worktree", "add", "-b", "fixture/product-worktree", str(worktree)],
                cwd=origin,
                check=True,
                capture_output=True,
            )

            for name, target in (("clone", clone), ("worktree", worktree)):
                with self.subTest(target=name):
                    self.assertFalse((target / ".harness-v2-product/staging").exists())
                    store = ProductStore(target)
                    self.assertEqual("pass", store.status()["classification"])
                    active = load_json(target / ".harness-v2-product/active-release.json", require_canonical=True)
                    release_launcher = (
                        target / ".harness-v2-product/releases" / active["release_ref"]["id"] / "hv2"
                    )
                    launcher = target / "hv2"
                    self.assertTrue(launcher.is_file())
                    self.assertFalse(launcher.is_symlink())
                    self.assertNotEqual(0, launcher.stat().st_mode & 0o111)
                    self.assertEqual(release_launcher.read_bytes(), launcher.read_bytes())
                    candidate = candidate_copy(base / f"candidate-{name}", marker=f"\n{name}\n".encode())
                    self.assertEqual("pass", store.update(candidate, apply=True)["classification"])
                    self.assertEqual("detached", store.detach(apply=True)["classification"])

    def test_staging_and_differing_detach_receipt_have_bounded_recovery_actions(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            base = Path(raw)
            staging_target = base / "staging-target"
            git_init(staging_target)
            staging_store = ProductStore(staging_target)
            staging_store.init(source_root(), apply=True)
            scratch = staging_target / ".harness-v2-product/staging/torn-candidate"
            scratch.mkdir()
            (scratch / "partial").write_text("torn\n", encoding="utf-8")
            staging_status = staging_store.status()
            self.assertEqual("HV2-PRODUCT-STAGING", staging_status["error_code"])
            self.assertEqual(str(scratch.resolve()), staging_status["message"])
            self.assertIn("OPERATIONS.md", staging_status["next_action"])
            self.assertIn("active writer", staging_status["next_action"])

            linked_target = base / "linked-staging-target"
            git_init(linked_target)
            linked_store = ProductStore(linked_target)
            linked_store.init(source_root(), apply=True)
            linked_staging = linked_target / ".harness-v2-product/staging"
            linked_staging.rmdir()
            linked_staging.symlink_to(base, target_is_directory=True)
            linked_status = linked_store.status()
            self.assertEqual("degraded", linked_status["classification"])
            self.assertEqual("HV2-PRODUCT-STAGING", linked_status["error_code"])

            receipt_target = base / "receipt-target"
            git_init(receipt_target)
            receipt_store = ProductStore(receipt_target)
            receipt_store.init(source_root(), apply=True)
            (receipt_target / ".harness-v2-detached.json").write_text("{}\n", encoding="utf-8")
            receipt_status = receipt_store.status()
            self.assertEqual("degraded", receipt_status["classification"])
            self.assertEqual("HV2-PRODUCT-IMMUTABLE-CONTRADICTION", receipt_status["error_code"])
            self.assertIn("do not delete", receipt_status["next_action"])
    def test_existing_authority_requires_explicit_attach_contract(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            target = Path(raw) / "target"
            git_init(target)
            (target / ".harness-v2").mkdir()
            before = snapshot(target)
            with self.assertRaisesRegex(ContractError, "HV2-PRODUCT-ATTACH-REQUIRED"):
                ProductStore(target).init(source_root(), apply=True)
            self.assertEqual(before, snapshot(target))

    def test_launcher_collision_and_symlink_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            base = Path(raw)
            collision = base / "collision"
            git_init(collision)
            (collision / "hv2").write_text("project owned\n", encoding="utf-8")
            with self.assertRaisesRegex(ContractError, "HV2-PRODUCT-COLLISION"):
                ProductStore(collision).init(source_root(), apply=True)
            linked = base / "linked"
            git_init(linked)
            (linked / "hv2").symlink_to(collision / "hv2")
            with self.assertRaisesRegex(ContractError, "HV2-PRODUCT-COLLISION"):
                ProductStore(linked).init(source_root(), apply=True)

    def test_source_parent_symlink_is_rejected_before_external_read(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            base = Path(raw)
            target = base / "target"
            git_init(target)
            candidate = base / "candidate"
            shutil.copytree(source_root(), candidate, ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc"))
            shutil.rmtree(candidate / "docs")
            (candidate / "docs").symlink_to(source_root() / "docs", target_is_directory=True)
            with self.assertRaisesRegex(ContractError, "HV2-PRODUCT-SOURCE-DIRECTORY"):
                ProductStore(target).init(candidate, apply=True)
            self.assertEqual({}, snapshot(target))

    def test_installed_release_cannot_initialize_another_project(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            base = Path(raw)
            installed = base / "installed"
            target = base / "target"
            git_init(installed)
            git_init(target)
            ProductStore(installed).init(source_root(), apply=True)
            before = snapshot(target)
            result = subprocess.run(
                [str(installed / "hv2"), "init", "--target", str(target), "--apply"],
                cwd=installed,
                check=False,
                text=True,
                capture_output=True,
            )
            self.assertEqual(65, result.returncode)
            self.assertEqual("HV2-PRODUCT-INSTALLED-SOURCE", json.loads(result.stdout)["code"])
            self.assertEqual(before, snapshot(target))

    def test_home_and_filesystem_root_are_never_targets(self) -> None:
        with self.assertRaisesRegex(ContractError, "HV2-PRODUCT-TARGET"):
            ProductStore(Path.home())
        with self.assertRaisesRegex(ContractError, "HV2-PRODUCT-TARGET"):
            ProductStore(Path("/"))

    def test_status_degrades_on_release_tamper_and_unexpected_product_file(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            target = Path(raw) / "target"
            git_init(target)
            store = ProductStore(target)
            initialized = store.init(source_root(), apply=True)
            release = target / ".harness-v2-product/releases" / initialized["release_ref"]["id"]
            (release / "README.md").write_text("tamper\n", encoding="utf-8")
            self.assertEqual("degraded", store.status()["classification"])
        with tempfile.TemporaryDirectory() as raw:
            target = Path(raw) / "target"
            git_init(target)
            store = ProductStore(target)
            store.init(source_root(), apply=True)
            (target / ".harness-v2-product/unowned.txt").write_text("no\n", encoding="utf-8")
            status = store.status()
            self.assertEqual("degraded", status["classification"])
            self.assertEqual("HV2-PRODUCT-ROOT-TREE", status["error_code"])

    def test_launcher_drift_blocks_rollback_before_selector_switch(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            base = Path(raw)
            target = base / "target"
            git_init(target)
            store = ProductStore(target)
            store.init(source_root(), apply=True)
            store.update(candidate_copy(base / "candidate"), apply=True)
            active_before = (target / ".harness-v2-product/active-release.json").read_bytes()
            (target / "hv2").write_text("tamper\n", encoding="utf-8")
            with self.assertRaisesRegex(ContractError, "HV2-PRODUCT-LAUNCHER-DRIFT"):
                store.rollback(None, apply=True)
            self.assertEqual(active_before, (target / ".harness-v2-product/active-release.json").read_bytes())

    def test_unrelated_secret_named_file_is_never_read_or_changed(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            target = Path(raw) / "target"
            git_init(target)
            secret = target / "customer-production-secret.txt"
            secret.write_bytes(b"sentinel-do-not-read-or-change\n")
            before = secret.read_bytes()
            ProductStore(target).init(source_root(), apply=False)
            ProductStore(target).init(source_root(), apply=True)
            self.assertEqual(before, secret.read_bytes())


if __name__ == "__main__":
    unittest.main()
