from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import tempfile
import unittest
from unittest import mock
from pathlib import Path

from hv2ref.errors import ContractError, InjectedCrash
from hv2ref.jsonio import canonical_json_bytes, load_json
from hv2ref.product import ProductStore, source_root

from tests.test_productization import candidate_copy, git_commit_all, git_init, snapshot


def exact_snapshot(root: Path) -> dict[str, tuple[object, ...]]:
    paths = [root, *sorted(root.rglob("*"), key=lambda path: path.as_posix())]
    result: dict[str, tuple[object, ...]] = {}
    for path in paths:
        relative = "." if path == root else path.relative_to(root).as_posix()
        if path.is_symlink():
            result[relative] = ("symlink", os.readlink(path))
        elif path.is_dir():
            result[relative] = ("directory", path.stat().st_mode & 0o777)
        elif path.is_file():
            result[relative] = (
                "file",
                hashlib.sha256(path.read_bytes()).hexdigest(),
                path.stat().st_mode & 0o777,
            )
    return result


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
            with self.assertRaises(InjectedCrash):
                receipt_store.detach(apply=True, inject_at="after-receipt")
            receipt_path = receipt_target / ".harness-v2-detached.json"
            receipt = load_json(receipt_path, require_canonical=True)
            receipt["item_id"] = "different-item"
            receipt_path.write_bytes(canonical_json_bytes(receipt))
            receipt_status = receipt_store.status()
            self.assertEqual("degraded", receipt_status["classification"])
            self.assertEqual("HV2-PRODUCT-IMMUTABLE-CONTRADICTION", receipt_status["error_code"])
            self.assertIn("do not delete", receipt_status["next_action"])

    def test_detach_receipt_semantic_type_is_fail_closed_without_replacement(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            target = Path(raw) / "target"
            git_init(target)
            store = ProductStore(target)
            store.init(source_root(), apply=True)
            with self.assertRaises(InjectedCrash):
                store.detach(apply=True, inject_at="after-receipt")
            receipt_path = target / ".harness-v2-detached.json"
            receipt = load_json(receipt_path, require_canonical=True)
            receipt["observed_at"] = 7
            receipt_path.write_bytes(canonical_json_bytes(receipt))
            before = exact_snapshot(target)
            status = store.status()
            self.assertEqual("degraded", status["classification"])
            self.assertEqual("HV2-PRODUCT-DETACH-RECEIPT", status["error_code"])
            with self.assertRaisesRegex(ContractError, "HV2-PRODUCT-DETACH-RECEIPT"):
                store.detach(apply=True)
            self.assertEqual(before, exact_snapshot(target))

    def test_authority_root_and_file_forms_are_stable_non_pass_and_read_only(self) -> None:
        structural_forms = {
            "root-missing",
            "root-symlink",
            "root-file",
            "authority-missing",
            "authority-symlink",
            "authority-directory",
        }
        for authority in ("state", "intent"):
            for form in (*sorted(structural_forms), "malformed", "wrong-identity"):
                with self.subTest(authority=authority, form=form), tempfile.TemporaryDirectory() as raw:
                    base = Path(raw)
                    target = base / "target"
                    git_init(target)
                    store = ProductStore(target)
                    store.init(source_root(), apply=True)
                    root_name = ".harness-v2" if authority == "state" else ".harness-v2-intents"
                    error_code = (
                        "HV2-PRODUCT-STATE-BINDING" if authority == "state" else "HV2-PRODUCT-INTENT-BINDING"
                    )
                    authority_root = target / root_name
                    authority_path = authority_root / "authority.json"
                    if form == "root-missing":
                        shutil.rmtree(authority_root)
                    elif form == "root-symlink":
                        external = base / "external-authority-root"
                        shutil.copytree(authority_root, external)
                        shutil.rmtree(authority_root)
                        authority_root.symlink_to(external, target_is_directory=True)
                    elif form == "root-file":
                        shutil.rmtree(authority_root)
                        authority_root.write_text("wrong type\n", encoding="utf-8")
                    elif form == "authority-missing":
                        authority_path.unlink()
                    elif form == "authority-symlink":
                        external = base / "external-authority.json"
                        external.write_bytes(authority_path.read_bytes())
                        authority_path.unlink()
                        authority_path.symlink_to(external)
                    elif form == "authority-directory":
                        authority_path.unlink()
                        authority_path.mkdir()
                    elif form == "malformed":
                        authority_path.write_text("{\n", encoding="utf-8")
                    elif form == "wrong-identity":
                        payload = load_json(authority_path, require_canonical=True)
                        payload["authority_home_id"] = "wrong-authority-home"
                        authority_path.write_bytes(canonical_json_bytes(payload))

                    before = exact_snapshot(target)
                    status = store.status()
                    self.assertEqual("degraded", status["classification"])
                    if form in structural_forms or form == "wrong-identity":
                        self.assertEqual(error_code, status["error_code"])
                    else:
                        self.assertEqual("HV2-JSON-SYNTAX", status["error_code"])

                    for executable, cwd in ((source_root() / "hv2", source_root()), (target / "hv2", target)):
                        result = subprocess.run(
                            [str(executable), "status", "--target", str(target)],
                            cwd=cwd,
                            check=False,
                            text=True,
                            capture_output=True,
                        )
                        self.assertEqual(10, result.returncode)
                        self.assertEqual(status, json.loads(result.stdout))
                    self.assertEqual(before, exact_snapshot(target))

    def test_unrelated_authority_stat_and_read_permission_errors_are_not_reclassified(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            target = Path(raw) / "target"
            git_init(target)
            store = ProductStore(target)
            store.init(source_root(), apply=True)
            before = exact_snapshot(target)
            real_load_json = load_json

            def guarded_load_json(path: Path, *, require_canonical: bool = False):
                candidate = Path(path)
                if candidate.resolve() == (target / ".harness-v2/authority.json").resolve():
                    raise PermissionError(str(candidate))
                return real_load_json(candidate, require_canonical=require_canonical)

            with mock.patch("hv2ref.product.load_json", side_effect=guarded_load_json):
                with self.assertRaises(PermissionError):
                    store.status()
            self.assertEqual(before, exact_snapshot(target))

            real_lstat = Path.lstat
            for root_name in (".harness-v2", ".harness-v2-intents"):
                with self.subTest(root_name=root_name):
                    authority_path = store.target_root / root_name / "authority.json"

                    def guarded_lstat(path: Path):
                        if path == authority_path:
                            raise PermissionError(str(path))
                        return real_lstat(path)

                    with mock.patch.object(Path, "lstat", new=guarded_lstat):
                        with self.assertRaises(PermissionError):
                            store.status()
                        with mock.patch("sys.argv", ["hv2", "status", "--target", str(target)]):
                            with mock.patch("hv2ref.cli._print") as print_result:
                                from hv2ref.cli import main as cli_main

                                self.assertEqual(70, cli_main())
                                self.assertEqual("PermissionError", print_result.call_args.args[0]["exception_type"])
                    self.assertEqual(before, exact_snapshot(target))

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
