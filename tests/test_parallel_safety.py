from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from hv2ref.errors import ContractError, InjectedCrash
from hv2ref.jsonio import load_json, replace_json
from hv2ref.parallel import ParallelStateStore, normalize_write_scope
from hv2ref.state import StateStore


AUTHORITY_HOME_ID = "7d854f54-6538-4cd4-8961-2e2f50ef9653"
REPOSITORY_ID = "HV2-REPO-TARGET-TEST"
FINALIZER = "OWNER-LOCAL-001"
OBSERVED = "2026-08-10T08:00:00Z"


def git(root: Path, *args: str, check: bool = True) -> str:
    result = subprocess.run(["git", *args], cwd=root, text=True, capture_output=True, check=False)
    if check and result.returncode != 0:
        raise AssertionError(f"git {args} failed: {result.returncode}: {result.stderr}")
    return result.stdout.strip()


def digest_files(root: Path, *, exclude_active_selector: bool = False) -> dict[str, str]:
    result: dict[str, str] = {}
    for path in sorted((root / ".harness-v2").rglob("*")):
        if not path.is_file() or "/staging/" in path.as_posix():
            continue
        relative = path.relative_to(root).as_posix()
        if exclude_active_selector and relative == ".harness-v2/items/item-0001/active-generation.json":
            continue
        result[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def project_digest(root: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for path in sorted(root.rglob("*")):
        if not path.is_file() or ".git" in path.parts or ".harness-v2" in path.parts:
            continue
        result[path.relative_to(root).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


class ParallelSafetyFixture(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.integration = self.root / "integration"
        self.integration.mkdir()
        git(self.integration, "init", "-b", "main")
        git(self.integration, "config", "user.name", "Harness v2 Parallel Fixture")
        git(self.integration, "config", "user.email", "harness-v2-parallel@example.invalid")
        (self.integration / "README.md").write_text("# Parallel fixture\n", encoding="utf-8")
        git(self.integration, "add", "README.md")
        git(self.integration, "commit", "-m", "fixture: initialize repository")
        StateStore(self.integration).initialize(AUTHORITY_HOME_ID, "item-0001", OBSERVED)
        git(self.integration, "add", ".harness-v2")
        git(self.integration, "commit", "-m", "fixture: persist generation 1 state")
        self.base_commit = git(self.integration, "rev-parse", "HEAD")
        self.base_tree = git(self.integration, "rev-parse", "HEAD^{tree}")
        self.parallel = ParallelStateStore(self.integration)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def activate(self, *, inject_at: str | None = None) -> dict[str, object]:
        return self.parallel.activate_parallel(
            repository_id=REPOSITORY_ID,
            item_id="item-0001",
            finalizer=FINALIZER,
            worktree_id="integration-main",
            branch="main",
            base_commit=self.base_commit,
            base_tree=self.base_tree,
            observed_at=OBSERVED,
            worktree_root=self.integration,
            _inject_at=inject_at,
        )

    def add_worktree(self, name: str, branch: str, base: str | None = None) -> Path:
        path = self.root / name
        git(self.integration, "worktree", "add", "-b", branch, str(path), base or self.base_commit)
        git(path, "config", "user.name", "Harness v2 Parallel Fixture")
        git(path, "config", "user.email", "harness-v2-parallel@example.invalid")
        return path

    def claim(
        self,
        *,
        claim_id: str,
        item_id: str,
        worktree: Path,
        worktree_id: str,
        scope: list[str],
        base_commit: str | None = None,
        base_tree: str | None = None,
    ) -> dict[str, object]:
        return self.parallel.claim_work(
            claim_id=claim_id,
            item_id=item_id,
            actor=f"ACTOR-{claim_id}",
            finalizer=FINALIZER,
            repository_id=REPOSITORY_ID,
            worktree_id=worktree_id,
            branch=git(worktree, "branch", "--show-current"),
            base_commit=base_commit or self.base_commit,
            base_tree=base_tree or self.base_tree,
            write_scope=scope,
            observed_at=OBSERVED,
            worktree_root=worktree,
        )

    def test_reader_matrix_multi_item_and_generation_one_bytes(self) -> None:
        before = digest_files(self.integration, exclude_active_selector=True)
        generation_one = self.parallel.verify_repository("item-0001")
        self.assertEqual("pass", generation_one["classification"])
        self.assertEqual(1, generation_one["generation"])

        self.activate()
        legacy = StateStore(self.integration).verify("item-0001")
        self.assertEqual("incompatible", legacy["classification"])
        current = self.parallel.verify_repository("item-0001")
        self.assertEqual("pass", current["classification"])
        self.assertEqual(2, current["generation"])
        after = digest_files(self.integration, exclude_active_selector=True)
        self.assertEqual(before, {path: after[path] for path in before})

        registered = self.parallel.register_item(item_id="item-0002", item_type="parallel-work", observed_at=OBSERVED)
        self.assertEqual("pass", registered["classification"])
        verified = self.parallel.verify_repository("item-0001")
        self.assertEqual(["item-0001", "item-0002"], verified["item_ids"])
        with self.assertRaises(ContractError) as duplicate:
            self.parallel.register_item(item_id="item-0002", item_type="parallel-work", observed_at=OBSERVED)
        self.assertEqual("HV2-ITEM-REUSE", duplicate.exception.code)

        selector_path = self.integration / ".harness-v2/parallel/active-generation.json"
        selector = load_json(selector_path, require_canonical=True)
        selector["generation"] = 3
        selector["schema_generation"] = 3
        replace_json(selector_path, selector)
        future = self.parallel.verify_repository("item-0001")
        self.assertEqual("incompatible", future["classification"])

    def test_activation_is_byte_deterministic_across_clones(self) -> None:
        mirror = self.root / "mirror"
        git(self.root, "clone", str(self.integration), str(mirror))
        self.activate()
        mirror_store = ParallelStateStore(mirror)
        mirror_store.activate_parallel(
            repository_id=REPOSITORY_ID,
            item_id="item-0001",
            finalizer=FINALIZER,
            worktree_id="integration-main",
            branch="main",
            base_commit=self.base_commit,
            base_tree=self.base_tree,
            observed_at=OBSERVED,
            worktree_root=mirror,
        )

        def generation_two_bytes(root: Path) -> dict[str, bytes]:
            selected = [
                root / ".harness-v2/items/item-0001/active-generation.json",
                *(root / ".harness-v2/parallel").rglob("*"),
            ]
            return {
                path.relative_to(root).as_posix(): path.read_bytes()
                for path in selected
                if path.is_file()
            }

        self.assertEqual(generation_two_bytes(self.integration), generation_two_bytes(mirror))

    def test_partial_activation_is_nonwritable_and_legacy_incompatible(self) -> None:
        with self.assertRaises(InjectedCrash):
            self.activate(inject_at="after_item_switch")
        partial = self.parallel.verify_repository("item-0001")
        self.assertEqual("degraded", partial["classification"])
        self.assertFalse(partial["writable"])
        legacy = StateStore(self.integration).verify("item-0001")
        self.assertEqual("incompatible", legacy["classification"])

    def test_scope_normalization_and_escape_matrix(self) -> None:
        (self.integration / "src/module").mkdir(parents=True)
        self.assertEqual(("docs/guide.md", "src/module"), normalize_write_scope(self.integration, ["src/module", "docs/guide.md"]))
        invalid = (
            [],
            [""],
            ["/absolute"],
            ["."],
            ["src/../escape"],
            ["src\\alias"],
            [".git/config"],
            [".harness-v2/authority.json"],
            ["cafe\u0301.txt"],
            ["src/Foo", "src/foo"],
            ["src", "src/module"],
        )
        for values in invalid:
            with self.subTest(values=values), self.assertRaises(ContractError):
                normalize_write_scope(self.integration, list(values))
        outside = self.root / "outside"
        outside.mkdir()
        os.symlink(outside, self.integration / "linked")
        with self.assertRaises(ContractError) as symlink:
            normalize_write_scope(self.integration, ["linked/file.txt"])
        self.assertEqual("HV2-WRITE-SCOPE-SYMLINK", symlink.exception.code)

    def test_disjoint_claims_and_visible_conflicts_preserve_shared_truth(self) -> None:
        self.activate()
        self.parallel.register_item(item_id="item-0002", item_type="parallel-work", observed_at=OBSERVED)
        self.parallel.register_item(item_id="item-0003", item_type="parallel-work", observed_at=OBSERVED)
        work_a = self.add_worktree("work-a", "work/a")
        work_b = self.add_worktree("work-b", "work/b")
        before_project = project_digest(self.integration)
        before_index = git(self.integration, "write-tree")
        before_selector = (self.integration / ".harness-v2/parallel/active-integration.json").read_bytes()

        first = self.claim(
            claim_id="claim-0001",
            item_id="item-0001",
            worktree=work_a,
            worktree_id="worktree-a",
            scope=["src/alpha"],
        )
        second = self.claim(
            claim_id="claim-0002",
            item_id="item-0002",
            worktree=work_b,
            worktree_id="worktree-b",
            scope=["docs/beta"],
        )
        same_item = self.claim(
            claim_id="claim-0003",
            item_id="item-0001",
            worktree=work_a,
            worktree_id="worktree-a-2",
            scope=["other/disjoint"],
        )
        overlapping = self.claim(
            claim_id="claim-0004",
            item_id="item-0003",
            worktree=work_b,
            worktree_id="worktree-b-2",
            scope=["SRC/ALPHA/file.py"],
        )
        self.assertEqual("pass", first["classification"])
        self.assertEqual("pass", second["classification"])
        self.assertEqual("conflict", same_item["classification"])
        self.assertEqual("conflict", overlapping["classification"])
        self.assertEqual(before_project, project_digest(self.integration))
        self.assertEqual(before_index, git(self.integration, "write-tree"))
        self.assertEqual(before_selector, (self.integration / ".harness-v2/parallel/active-integration.json").read_bytes())
        self.assertFalse((self.integration / ".harness-v2/staging").exists())
        verified = self.parallel.verify_repository("item-0001")
        self.assertEqual(4, verified["claim_count"])
        self.assertEqual(2, verified["conflict_count"])

    def test_cli_conflict_exit_and_control_identity_rejection(self) -> None:
        self.activate()
        work = self.add_worktree("work-cli", "work/cli")
        self.claim(
            claim_id="claim-cli-0001",
            item_id="item-0001",
            worktree=work,
            worktree_id="worktree-cli-1",
            scope=["src/first"],
        )
        source_root = Path(__file__).resolve().parents[1] / "src"
        environment = dict(os.environ)
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        environment["PYTHONPATH"] = str(source_root)
        result = subprocess.run(
            [
                sys.executable,
                "-B",
                "-m",
                "hv2ref.cli",
                "claim-work",
                "--target",
                str(self.integration),
                "--claim-id",
                "claim-cli-0002",
                "--item-id",
                "item-0001",
                "--actor",
                "ACTOR-CLI-2",
                "--finalizer",
                FINALIZER,
                "--repository-id",
                REPOSITORY_ID,
                "--worktree-id",
                "worktree-cli-2",
                "--worktree",
                str(work),
                "--branch",
                "work/cli",
                "--base-commit",
                self.base_commit,
                "--base-tree",
                self.base_tree,
                "--write-scope",
                "docs/disjoint",
                "--observed-at",
                OBSERVED,
            ],
            cwd=self.integration,
            env=environment,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(12, result.returncode)
        self.assertEqual("conflict", json.loads(result.stdout)["classification"])
        with self.assertRaises(ContractError) as identity:
            self.parallel.claim_work(
                claim_id="claim-wrong-repository",
                item_id="item-0001",
                actor="ACTOR-WRONG",
                finalizer=FINALIZER,
                repository_id="OTHER-REPOSITORY",
                worktree_id="worktree-wrong",
                branch="work/cli",
                base_commit=self.base_commit,
                base_tree=self.base_tree,
                write_scope=["other/path"],
                observed_at=OBSERVED,
                worktree_root=work,
            )
        self.assertEqual("HV2-REPOSITORY-IDENTITY", identity.exception.code)
        self.assertFalse((self.integration / ".harness-v2/parallel/generations/2/claims/claim-wrong-repository.json").exists())

    def test_reassignment_is_append_only_and_finalizer_bound(self) -> None:
        self.activate()
        work = self.add_worktree("work-reassign", "work/reassign")
        self.claim(
            claim_id="claim-reassign",
            item_id="item-0001",
            worktree=work,
            worktree_id="worktree-reassign",
            scope=["src/reassign"],
        )
        reassigned = self.parallel.reassign_claim(
            reassignment_id="reassignment-0001",
            claim_id="claim-reassign",
            actor="ACTOR-SUCCESSOR",
            finalizer=FINALIZER,
            reason="caller worktree abandoned",
            observed_at=OBSERVED,
        )
        self.assertEqual("pass", reassigned["classification"])
        self.assertTrue((self.integration / ".harness-v2/parallel/generations/2/claims/claim-reassign.json").is_file())
        self.assertTrue((self.integration / ".harness-v2/parallel/generations/2/reassignments/reassignment-0001.json").is_file())
        with self.assertRaises(ContractError) as wrong_finalizer:
            self.parallel.reassign_claim(
                reassignment_id="reassignment-0002",
                claim_id="claim-reassign",
                actor="ACTOR-SUCCESSOR",
                finalizer="OTHER-FINALIZER",
                reason="invalid finalizer",
                observed_at=OBSERVED,
            )
        self.assertEqual("HV2-FINALIZER-DECLARATION", wrong_finalizer.exception.code)

    def test_finalize_exact_resume_duplicate_and_stale_base(self) -> None:
        self.activate()
        work = self.add_worktree("work-finalize", "work/finalize")
        claimed = self.claim(
            claim_id="claim-finalize",
            item_id="item-0001",
            worktree=work,
            worktree_id="worktree-finalize",
            scope=["src/result.txt"],
        )
        self.assertEqual("pass", claimed["classification"])
        (work / "src").mkdir()
        (work / "src/result.txt").write_text("integrated result\n", encoding="utf-8")
        git(work, "add", "src/result.txt")
        git(work, "commit", "-m", "fixture: complete claimed work")
        git(self.integration, "merge", "--no-ff", "work/finalize", "-m", "fixture: integrate claimed work")
        result_commit = git(self.integration, "rev-parse", "HEAD")
        result_tree = git(self.integration, "rev-parse", "HEAD^{tree}")
        prior_selector = (self.integration / ".harness-v2/parallel/active-integration.json").read_bytes()

        kwargs = {
            "epoch_id": "epoch-0001",
            "claim_ids": ["claim-finalize"],
            "finalizer": FINALIZER,
            "base_commit": self.base_commit,
            "base_tree": self.base_tree,
            "result_commit": result_commit,
            "result_tree": result_tree,
            "integration_branch": "main",
            "observed_at": OBSERVED,
            "integration_worktree_root": self.integration,
            "claim_worktrees": {"claim-finalize": work},
        }
        finalized = self.parallel.finalize_work(**kwargs)
        self.assertEqual("pass", finalized["classification"])
        arbitration_paths = list(
            (
                self.integration
                / ".harness-v2/parallel/generations/2/finalize-arbitrations"
            ).glob("*.json")
        )
        self.assertEqual(1, len(arbitration_paths))
        self.assertEqual(hashlib.sha256(prior_selector).hexdigest(), arbitration_paths[0].stem)
        arbitration = load_json(arbitration_paths[0], require_canonical=True)
        self.assertEqual("epoch-0001", arbitration["epoch_id"])
        finalization = load_json(
            self.integration
            / ".harness-v2/parallel/generations/2/integration-epochs/epoch-0001/finalization.json",
            require_canonical=True,
        )
        self.assertEqual(arbitration["record_id"], finalization["arbitration_ref"]["id"])
        resumed = self.parallel.finalize_work(**kwargs)
        self.assertEqual("pass", resumed["classification"])
        self.assertTrue(resumed["resumed"])

        conflicting = dict(kwargs)
        conflicting["result_tree"] = "0" * 40
        duplicate = self.parallel.finalize_work(**conflicting)
        self.assertEqual("conflict", duplicate["classification"])
        self.assertTrue(
            (
                self.integration
                / ".harness-v2/parallel/generations/2/conflicts/finalize-conflict-epoch-0001-duplicate.json"
            ).is_file()
        )

        stale_work = self.add_worktree("work-stale", "work/stale", self.base_commit)
        stale = self.claim(
            claim_id="claim-stale",
            item_id="item-0001",
            worktree=stale_work,
            worktree_id="worktree-stale",
            scope=["src/stale.txt"],
        )
        self.assertEqual("stale", stale["classification"])
        selector = load_json(self.integration / ".harness-v2/parallel/active-integration.json", require_canonical=True)
        self.assertEqual(result_commit, selector["current_commit"])
        verified = self.parallel.verify_repository("item-0001")
        self.assertEqual(2, verified["conflict_count"])

    def test_unknown_parallel_tree_is_fail_closed(self) -> None:
        self.activate()
        rogue = self.integration / ".harness-v2/parallel/rogue.json"
        rogue.write_text(json.dumps({"schema_generation": 2}) + "\n", encoding="utf-8")
        with self.assertRaises(ContractError) as failure:
            self.parallel.verify_repository("item-0001")
        self.assertEqual("HV2-GEN2-TREE", failure.exception.code)


if __name__ == "__main__":
    unittest.main()
