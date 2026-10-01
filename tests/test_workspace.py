from __future__ import annotations

import hashlib
import os
from pathlib import Path
import subprocess
import tempfile
import threading
from concurrent.futures import ThreadPoolExecutor
import unittest
from unittest.mock import patch

from hv2ref.errors import ContractError, InjectedCrash
from hv2ref.jsonio import canonical_json_bytes
from hv2ref.workspace import bootstrap_root, classify_target, git_environment, inspect_root, target_fingerprint, writer_guard


class WorkspaceRootTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="new-workspace-")
        self.base = Path(self.tmp.name).resolve()
        self.target = self.base / "project"
        self.target.mkdir()
        (self.target / "README.md").write_text("Project content stays.\n")
        self.format = {"record_type":"workspace-format", "format_version":1, "authority_home_id":"project-a", "created_at":"2026-01-01T00:00:00Z", "lineage":None}
        self.plan = {"record_type":"lifecycle-plan", "schema_version":1, "operation_id":"init-a", "action":"init", "target_fingerprint":target_fingerprint(self.target), "authority_home_id":"project-a", "expected_binding_ref":None, "candidate_release":{"id":"product-release-"+"a"*24,"sha256":"a"*64,"inventory_id":"human-1"}, "format_sha256":hashlib.sha256(canonical_json_bytes(self.format)).hexdigest(), "truth_refs":[], "remove":[], "preserve":[], "created_at":"2026-01-01T00:00:00Z"}

    def tearDown(self):
        self.tmp.cleanup()

    def git(self, *args, target=None):
        if args and args[0] == "commit":
            args = ("-c", "maintenance.auto=false", "-c", "gc.auto=0", *args)
        return subprocess.run(["git", "-C", str(target or self.target), *args], env=git_environment(), check=True, capture_output=True, text=True).stdout.strip()

    def init_git(self):
        self.git("init", "-q")
        self.git("config", "user.name", "Fixture")
        self.git("config", "user.email", "fixture@example.invalid")
        self.git("add", "README.md")
        self.git("commit", "-qm", "fixture")

    def tree(self):
        return {str(p.relative_to(self.target)):p.read_bytes() for p in self.target.rglob("*") if p.is_file() and not p.is_symlink()}

    def test_non_git_and_primary_are_explicit(self):
        self.assertEqual(classify_target(self.target, mutation=True)["kind"], "non-git")
        self.init_git()
        self.assertEqual(classify_target(self.target, mutation=True)["kind"], "primary")

    def test_linked_worker_cannot_bootstrap_or_guard(self):
        self.init_git()
        worker = self.base / "worker"
        self.git("worktree", "add", "-q", "-b", "worker", str(worker))
        self.assertEqual(classify_target(worker)["kind"], "linked-worktree")
        with self.assertRaises(ContractError):
            bootstrap_root(worker, self.plan, self.format)
        with self.assertRaises(ContractError):
            with writer_guard(worker):
                self.fail("worker guard acquired")
        self.assertFalse((worker / ".hrn").exists())

    def test_git_environment_cannot_redirect_target(self):
        self.init_git()
        env = {"GIT_DIR":str(self.base / "wrong"), "GIT_WORK_TREE":str(self.base), "GIT_INDEX_FILE":str(self.base / "wrong-index"), "GIT_CONFIG_COUNT":"1", "GIT_OPTIONAL_LOCKS":"1"}
        with patch.dict(os.environ, env):
            self.assertEqual(classify_target(self.target, mutation=True)["kind"], "primary")
            self.assertEqual(git_environment()["GIT_OPTIONAL_LOCKS"], "0")
            self.assertNotIn("GIT_CONFIG_COUNT", git_environment())
        self.assertFalse((self.base / "wrong-index").exists())

    def test_git_subdirectory_and_nested_repo_are_not_controls(self):
        self.init_git()
        child = self.target / "child"
        child.mkdir()
        with self.assertRaises(ContractError):
            classify_target(child, mutation=True)
        self.git("init", "-q", target=child)
        self.assertEqual(classify_target(child)["kind"], "nested-repository")
        with self.assertRaises(ContractError):
            classify_target(child, mutation=True)

    def test_separate_git_dir_is_explicitly_unsupported(self):
        self.git("init", "-q", "--separate-git-dir", str(self.base / "metadata"))
        self.assertEqual(classify_target(self.target)["kind"], "separate-git-dir")
        with self.assertRaises(ContractError):
            classify_target(self.target, mutation=True)

    def test_bare_git_is_not_non_git(self):
        bare = self.base / "bare"
        subprocess.run(["git", "init", "--bare", "-q", str(bare)], check=True)
        with self.assertRaises(ContractError):
            classify_target(bare, mutation=True)

    def test_classification_does_not_change_git_index_or_create_locks(self):
        self.init_git()
        before = self.tree()
        for _ in range(3):
            classify_target(self.target)
            inspect_root(self.target)
        self.assertEqual(before, self.tree())
        self.assertFalse((self.target / ".git/index.lock").exists())

    def test_target_symlink_and_symlink_ancestor_are_refused(self):
        alias = self.base / "alias"
        alias.symlink_to(self.target, target_is_directory=True)
        with self.assertRaises(ContractError):
            classify_target(alias, mutation=True)
        child = self.target / "child"
        child.mkdir()
        with self.assertRaises(ContractError):
            classify_target(alias / "child", mutation=True)

    def test_case_alias_root_is_not_new_or_recoverable_authority(self):
        alias = self.target / ".HRN"
        alias.mkdir()
        (alias / "user-note").write_bytes(b"preserve")
        before = self.tree()
        self.assertEqual(inspect_root(self.target)["classification"], "degraded")
        with self.assertRaises(ContractError):
            bootstrap_root(self.target, self.plan, self.format)
        self.assertEqual(before, self.tree())

    def test_uninitialized_inspection_is_read_only(self):
        before = self.tree()
        self.assertEqual(inspect_root(self.target)["classification"], "uninitialized")
        self.assertEqual(before, self.tree())

    def test_bootstrap_preserves_project_and_creates_no_work(self):
        result = bootstrap_root(self.target, self.plan, self.format)
        self.assertEqual(result["classification"], "root-ready")
        self.assertEqual(result["record_verification"], "required")
        self.assertEqual((self.target / "README.md").read_text(), "Project content stays.\n")
        self.assertEqual(list((self.target / ".hrn/work").iterdir()), [])
        self.assertEqual(list((self.target / ".hrn/intents").iterdir()), [])
        self.assertFalse((self.target / "hv2").exists())
        self.assertFalse((self.target / ".hrn/locks").exists())

    def test_every_owned_bootstrap_prefix_recovers_exactly(self):
        for point in ["after-plan", "after-format", "after-ignore", "after-intents", "after-work"]:
            with self.subTest(point=point), tempfile.TemporaryDirectory(dir=self.base) as directory:
                target = Path(directory).resolve()
                plan = self.plan | {"target_fingerprint":target_fingerprint(target)}
                with self.assertRaises(InjectedCrash):
                    bootstrap_root(target, plan, self.format, inject_at=point)
                self.assertEqual(bootstrap_root(target, plan, self.format, recover=True)["classification"], "root-ready")
                before = {str(p.relative_to(target)):p.read_bytes() for p in target.rglob("*") if p.is_file()}
                bootstrap_root(target, plan, self.format, recover=True)
                self.assertEqual(before, {str(p.relative_to(target)):p.read_bytes() for p in target.rglob("*") if p.is_file()})

    def test_root_without_plan_is_never_adopted(self):
        with self.assertRaises(InjectedCrash):
            bootstrap_root(self.target, self.plan, self.format, inject_at="after-root")
        before = self.tree()
        with self.assertRaises(ContractError):
            bootstrap_root(self.target, self.plan, self.format, recover=True)
        self.assertEqual(before, self.tree())
        self.assertEqual(inspect_root(self.target)["classification"], "unrecognized")

    def test_wrong_plan_or_format_never_overwrites(self):
        bootstrap_root(self.target, self.plan, self.format)
        before = self.tree()
        changed = self.plan | {"operation_id":"different"}
        with self.assertRaises(ContractError):
            bootstrap_root(self.target, changed, self.format, recover=True)
        self.assertEqual(before, self.tree())
        (self.target / ".hrn/format.json").write_bytes(b"broken\n")
        before = self.tree()
        with self.assertRaises(ContractError):
            bootstrap_root(self.target, self.plan, self.format, recover=True)
        self.assertEqual(before, self.tree())
        self.assertEqual(inspect_root(self.target)["classification"], "integrity-failure")

    def test_plan_validation_precedes_root_creation(self):
        for key, value in [("schema_version", True), ("target_fingerprint", "0"*64), ("format_sha256", "0"*64), ("action", "detach")]:
            with self.subTest(key=key), self.assertRaises(ContractError):
                bootstrap_root(self.target, self.plan | {key:value}, self.format)
            self.assertFalse((self.target / ".hrn").exists())

    def test_format_boolean_and_unknown_version_differ(self):
        bootstrap_root(self.target, self.plan, self.format)
        path = self.target / ".hrn/format.json"
        for version, expected in [(True, "integrity-failure"), (2, "incompatible")]:
            path.write_bytes(canonical_json_bytes(self.format | {"format_version":version}))
            before = self.tree()
            self.assertEqual(inspect_root(self.target)["classification"], expected)
            self.assertEqual(before, self.tree())

    def test_unknown_format_member_is_degraded_without_dropping_bytes(self):
        bootstrap_root(self.target, self.plan, self.format)
        path = self.target / ".hrn/format.json"
        path.write_bytes(canonical_json_bytes(self.format | {"future": "preserve"}))
        before = self.tree()
        self.assertEqual(inspect_root(self.target)["classification"], "degraded")
        self.assertEqual(before, self.tree())
        with self.assertRaises(ContractError):
            bootstrap_root(self.target, self.plan, self.format, recover=True)
        self.assertEqual(before, self.tree())

    def test_extra_file_and_ignore_drift_are_preserved(self):
        bootstrap_root(self.target, self.plan, self.format)
        extra = self.target / ".hrn/.DS_Store"
        extra.write_bytes(b"keep me")
        self.assertEqual(inspect_root(self.target)["classification"], "degraded")
        with self.assertRaises(ContractError):
            bootstrap_root(self.target, self.plan, self.format, recover=True)
        self.assertEqual(extra.read_bytes(), b"keep me")
        extra.unlink()
        ignore = self.target / ".hrn/.gitignore"
        ignore.write_bytes(b"*\n")
        self.assertEqual(inspect_root(self.target)["classification"], "degraded")
        with self.assertRaises(ContractError):
            bootstrap_root(self.target, self.plan, self.format, recover=True)
        self.assertEqual(ignore.read_bytes(), b"*\n")

    def test_detach_receipt_is_not_accepted_without_lifecycle_verification(self):
        bootstrap_root(self.target, self.plan, self.format)
        (self.target / ".hrn/detached.json").write_bytes(b"not a valid receipt\n")
        result = inspect_root(self.target)
        self.assertEqual(result["classification"], "detach-candidate")
        self.assertEqual(result["record_verification"], "required")
        with self.assertRaises(ContractError):
            bootstrap_root(self.target, self.plan, self.format, recover=True)
        with self.assertRaises(ContractError):
            with writer_guard(self.target):
                self.fail("detach was treated as active")

    def test_format_without_product_and_receipt_is_not_init_prefix(self):
        root = self.target / ".hrn"
        root.mkdir()
        (root / "format.json").write_bytes(canonical_json_bytes(self.format))
        self.assertEqual(inspect_root(self.target)["classification"], "integrity-failure")

    def test_symlinked_root_member_never_reads_external_bytes(self):
        bootstrap_root(self.target, self.plan, self.format)
        path = self.target / ".hrn/format.json"
        path.unlink()
        sentinel = self.base / "private-sentinel"
        sentinel.write_bytes(b"never read or overwrite")
        path.symlink_to(sentinel)
        self.assertEqual(inspect_root(self.target)["classification"], "integrity-failure")
        with self.assertRaises(ContractError):
            bootstrap_root(self.target, self.plan, self.format, recover=True)
        self.assertEqual(sentinel.read_bytes(), b"never read or overwrite")

    def test_guard_anchor_is_stable_and_inspection_creates_nothing(self):
        bootstrap_root(self.target, self.plan, self.format)
        with writer_guard(self.target):
            first = (self.target / ".hrn/locks/writer.lock").stat().st_ino
        with writer_guard(self.target):
            self.assertEqual(first, (self.target / ".hrn/locks/writer.lock").stat().st_ino)
        before = self.tree()
        inspect_root(self.target)
        self.assertEqual(before, self.tree())

    def test_nonempty_truth_is_not_bootstrap_recovery(self):
        bootstrap_root(self.target, self.plan, self.format)
        (self.target / ".hrn/work/user-note").write_text("preserve\n")
        before = self.tree()
        with self.assertRaises(ContractError):
            bootstrap_root(self.target, self.plan, self.format, recover=True)
        self.assertEqual(before, self.tree())

    def test_future_format_wins_over_new_members_and_bad_header_does_not(self):
        bootstrap_root(self.target, self.plan, self.format)
        path = self.target / ".hrn/format.json"
        (self.target / ".hrn/future-dir").mkdir()
        path.write_bytes(canonical_json_bytes(self.format | {"format_version": 2, "future": []}))
        self.assertEqual(inspect_root(self.target)["classification"], "incompatible")
        bad = self.format | {"record_type": "different", "future": []}
        path.write_bytes(canonical_json_bytes(bad))
        self.assertEqual(inspect_root(self.target)["classification"], "integrity-failure")
        bad = self.format | {"future": []}; del bad["lineage"]
        path.write_bytes(canonical_json_bytes(bad))
        self.assertEqual(inspect_root(self.target)["classification"], "integrity-failure")

    def test_git_clone_and_clean_transport_empty_truth_without_reader_mutation(self):
        self.init_git()
        bootstrap_root(self.target, self.plan, self.format)
        self.git("add", ".hrn")
        self.git("commit", "-qm", "workspace fixture")
        clone = self.base / "clone"
        self.git("clone", "-q", str(self.target), str(clone))
        self.assertFalse((clone / ".hrn/work").exists())
        self.assertEqual(inspect_root(clone)["classification"], "root-ready")
        self.assertFalse((clone / ".hrn/work").exists())
        with writer_guard(clone):
            self.assertFalse((clone / ".hrn/work").exists())
        # Explicit test-only clean, never a development checkout cleanup.
        self.git("clean", "-fd")
        self.assertEqual(inspect_root(self.target)["classification"], "root-ready")

    def test_product_dir_without_durable_plan_and_torn_files_are_preserved(self):
        with self.assertRaises(InjectedCrash):
            bootstrap_root(self.target, self.plan, self.format, inject_at="after-product-dir")
        self.assertEqual(inspect_root(self.target)["classification"], "unrecognized")
        (self.target / ".hrn/product/init-plan.json").write_bytes(b"")
        before = self.tree()
        self.assertEqual(inspect_root(self.target)["classification"], "unrecognized")
        with self.assertRaises(ContractError):
            bootstrap_root(self.target, self.plan, self.format, recover=True)
        self.assertEqual(before, self.tree())
        (self.target / ".hrn/product/init-plan.json").write_bytes(canonical_json_bytes(self.plan))
        (self.target / ".hrn/format.json").write_bytes(b"")
        self.assertIn("manual", inspect_root(self.target)["recovery"])
        with self.assertRaises(ContractError):
            bootstrap_root(self.target, self.plan, self.format, recover=True)
        self.assertEqual((self.target / ".hrn/format.json").read_bytes(), b"")

    def test_malformed_missing_and_out_of_order_plan_prefixes_do_not_resume(self):
        root = self.target / ".hrn"
        (root / "product").mkdir(parents=True)
        (root / "product/init-plan.json").mkdir()
        self.assertEqual(inspect_root(self.target)["classification"], "unrecognized")
        (root / "product/init-plan.json").rmdir()
        (root / "product/init-plan.json").write_bytes(canonical_json_bytes(self.plan))
        (root / "work").mkdir()
        self.assertEqual(inspect_root(self.target)["classification"], "integrity-failure")
        with self.assertRaises(ContractError):
            bootstrap_root(self.target, self.plan, self.format, recover=True)
        (root / "work").rmdir()
        (root / "detached.json").write_bytes(b"{}\n")
        self.assertEqual(inspect_root(self.target)["classification"], "integrity-failure")

    def test_shared_guard_supports_only_explicit_detach_recovery_and_blocks_recursion(self):
        bootstrap_root(self.target, self.plan, self.format)
        with writer_guard(self.target):
            with self.assertRaises(ContractError):
                with writer_guard(self.target):
                    self.fail("recursive guard entered")
        anchor = (self.target / ".hrn/locks/writer.lock").stat().st_ino
        (self.target / ".hrn/detached.json").write_bytes(b"{}\n")
        with writer_guard(self.target, purpose="detach-recovery"):
            self.assertEqual((self.target / ".hrn/locks/writer.lock").stat().st_ino, anchor)
        self.assertEqual(inspect_root(self.target)["record_verification"], "required")

    def test_concurrent_first_guard_uses_one_anchor(self):
        bootstrap_root(self.target, self.plan, self.format)
        barrier = threading.Barrier(2)
        def acquire():
            barrier.wait(timeout=5)
            with writer_guard(self.target):
                return (self.target / ".hrn/locks/writer.lock").stat().st_ino
        with ThreadPoolExecutor(max_workers=2) as pool:
            futures = [pool.submit(acquire) for _ in range(2)]
            self.assertEqual(futures[0].result(timeout=10), futures[1].result(timeout=10))

    def test_ancestor_authority_refuses_non_git_nested_target(self):
        (self.target / ".HRN").write_bytes(b"preserve")
        child = self.target / "child"
        child.mkdir()
        with self.assertRaises(ContractError):
            classify_target(child, mutation=True)

    def test_missing_git_and_probe_errors_never_hide_ancestral_metadata(self):
        with patch("hv2ref.workspace.subprocess.run", side_effect=FileNotFoundError):
            self.assertEqual(classify_target(self.target)["kind"], "non-git")
            (self.target / ".git").mkdir()
            with self.assertRaises(ContractError):
                classify_target(self.target)
        failure = subprocess.CompletedProcess([], 128, b"", b"dubious ownership")
        with patch("hv2ref.workspace.subprocess.run", return_value=failure), self.assertRaises(ContractError):
            classify_target(self.target)
        failure.stderr = b"not a git repository"
        with patch("hv2ref.workspace.subprocess.run", return_value=failure), self.assertRaises(ContractError):
            classify_target(self.target)

    def test_missing_target_and_permission_error_are_bounded(self):
        with self.assertRaises(ContractError):
            classify_target(self.base / "missing")
        bootstrap_root(self.target, self.plan, self.format)
        with patch("hv2ref.workspace._file_json", side_effect=PermissionError):
            self.assertEqual(inspect_root(self.target)["classification"], "integrity-failure")

    def test_real_submodule_is_not_a_control(self):
        self.init_git()
        source = self.base / "module-source"
        self.git("clone", "-q", str(self.target), str(source))
        self.git("-c", "protocol.file.allow=always", "submodule", "add", "-q", str(source), "module")
        module = self.target / "module"
        self.assertEqual(classify_target(module)["kind"], "submodule")
        with self.assertRaises(ContractError):
            classify_target(module, mutation=True)


if __name__ == "__main__":
    unittest.main()
