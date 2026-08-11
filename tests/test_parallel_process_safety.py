from __future__ import annotations

import hashlib
import json
import os
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from typing import Any

from hv2ref.errors import ContractError
from hv2ref.jsonio import load_json
from hv2ref.parallel import ParallelStateStore
from hv2ref.state import StateStore


AUTHORITY_HOME_ID = "c26a4a91-11b9-4c10-8f65-6c07c2a905d0"
REPOSITORY_ID = "HV2-REPO-CP4-FIXTURE"
FINALIZER = "OWNER-LOCAL-CP4"
OBSERVED = "2026-08-10T09:00:00Z"
GIT_NAME = "Harness v2 CP4 Fixture"
GIT_EMAIL = "harness-v2-cp4@example.invalid"
WORKER = Path(__file__).parent / "fixtures" / "parallel_process_worker.py"
SOURCE_ROOT = Path(__file__).resolve().parents[1] / "src"


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True) + "\n").encode("utf-8")


def write_once(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as handle:
        handle.write(canonical_bytes(value))


def git_environment(sequence: int = 0) -> dict[str, str]:
    environment = dict(os.environ)
    timestamp = f"2001-01-01T00:00:{sequence:02d}Z"
    environment.update(
        {
            "GIT_AUTHOR_DATE": timestamp,
            "GIT_COMMITTER_DATE": timestamp,
            "GIT_CONFIG_NOSYSTEM": "1",
        }
    )
    return environment


def git(root: Path, *args: str, check: bool = True, sequence: int = 0) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=root,
        env=git_environment(sequence),
        text=True,
        capture_output=True,
        check=False,
    )
    if check and result.returncode != 0:
        raise AssertionError(f"git {args} failed: {result.returncode}: {result.stderr}")
    return result.stdout.rstrip("\n")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def project_digest(root: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for path in sorted(root.rglob("*")):
        if not path.is_file() or ".git" in path.parts or ".harness-v2" in path.parts:
            continue
        result[path.relative_to(root).as_posix()] = sha256_bytes(path.read_bytes())
    return result


def harness_digest(root: Path) -> dict[str, str]:
    harness = root / ".harness-v2"
    return {
        path.relative_to(root).as_posix(): sha256_bytes(path.read_bytes())
        for path in sorted(harness.rglob("*"))
        if path.is_file()
    }


def added_paths(before: dict[str, str], after: dict[str, str]) -> set[str]:
    for path in before:
        if after.get(path) != before[path]:
            raise AssertionError(f"pre-existing state changed: {path}")
    return set(after) - set(before)


class RepositoryFixture:
    def __init__(self, root: Path):
        self.root = root
        self.integration = root / "integration"
        self.integration.mkdir(parents=True)
        git(self.integration, "init", "-b", "main")
        git(self.integration, "config", "user.name", GIT_NAME)
        git(self.integration, "config", "user.email", GIT_EMAIL)
        (self.integration / "README.md").write_text("# CP4 fixture\n", encoding="utf-8")
        git(self.integration, "add", "README.md")
        git(self.integration, "commit", "-m", "fixture: initialize repository", sequence=0)
        StateStore(self.integration).initialize(AUTHORITY_HOME_ID, "item-0001", OBSERVED)
        git(self.integration, "add", ".harness-v2")
        git(self.integration, "commit", "-m", "fixture: persist generation 1 state", sequence=1)
        self.base_commit = git(self.integration, "rev-parse", "HEAD")
        self.base_tree = git(self.integration, "rev-parse", "HEAD^{tree}")
        self.store = ParallelStateStore(self.integration)
        self.store.activate_parallel(
            repository_id=REPOSITORY_ID,
            item_id="item-0001",
            finalizer=FINALIZER,
            worktree_id="integration-main",
            branch="main",
            base_commit=self.base_commit,
            base_tree=self.base_tree,
            observed_at=OBSERVED,
            worktree_root=self.integration,
        )

    def register_item(self, item_id: str) -> None:
        self.store.register_item(item_id=item_id, item_type="parallel-work", observed_at=OBSERVED)

    def add_worktree(self, name: str, branch: str, base: str | None = None) -> Path:
        path = self.root / name
        git(self.integration, "worktree", "add", "-b", branch, str(path), base or self.base_commit)
        git(path, "config", "user.name", GIT_NAME)
        git(path, "config", "user.email", GIT_EMAIL)
        return path

    def claim_parameters(
        self,
        *,
        claim_id: str,
        item_id: str,
        worktree: Path,
        worktree_id: str,
        scope: list[str],
        actor: str,
    ) -> dict[str, Any]:
        return {
            "actor": actor,
            "base_commit": self.base_commit,
            "base_tree": self.base_tree,
            "branch": git(worktree, "branch", "--show-current"),
            "claim_id": claim_id,
            "finalizer": FINALIZER,
            "item_id": item_id,
            "observed_at": OBSERVED,
            "repository_id": REPOSITORY_ID,
            "worktree_id": worktree_id,
            "worktree_root": str(worktree),
            "write_scope": scope,
        }

    def finalize_parameters(
        self,
        *,
        epoch_id: str,
        claim_ids: list[str],
        claim_worktrees: dict[str, Path],
        result_commit: str,
        result_tree: str,
        succeeds_epoch_id: str | None = None,
        successor_reason: str | None = None,
    ) -> dict[str, Any]:
        result = {
            "base_commit": self.base_commit,
            "base_tree": self.base_tree,
            "claim_ids": claim_ids,
            "claim_worktrees": {claim_id: str(path) for claim_id, path in claim_worktrees.items()},
            "epoch_id": epoch_id,
            "finalizer": FINALIZER,
            "integration_branch": "main",
            "integration_worktree_root": str(self.integration),
            "observed_at": OBSERVED,
            "result_commit": result_commit,
            "result_tree": result_tree,
        }
        if succeeds_epoch_id is not None:
            result["succeeds_epoch_id"] = succeeds_epoch_id
            result["successor_reason"] = successor_reason
        return result

    def commit_scoped(self, worktree: Path, relative: str, content: str, message: str, sequence: int) -> str:
        path = worktree / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        git(worktree, "add", relative)
        git(worktree, "commit", "-m", message, sequence=sequence)
        return git(worktree, "rev-parse", "HEAD")

    def merge(self, branch: str, message: str, sequence: int) -> None:
        git(self.integration, "merge", "--no-ff", branch, "-m", message, sequence=sequence)


class ParallelProcessSafetyFixture(unittest.TestCase):
    artifact_root: Path
    temporary: tempfile.TemporaryDirectory[str] | None

    @classmethod
    def setUpClass(cls) -> None:
        configured = os.environ.get("HV2_CP4_ARTIFACT_ROOT")
        if configured:
            cls.artifact_root = Path(configured).resolve()
            cls.artifact_root.mkdir(parents=True, exist_ok=True)
            if any(cls.artifact_root.iterdir()):
                raise RuntimeError(f"artifact root is not empty: {cls.artifact_root}")
            cls.temporary = None
        else:
            cls.temporary = tempfile.TemporaryDirectory(prefix="hv2-cp4-self-contained-")
            cls.artifact_root = Path(cls.temporary.name)

    @classmethod
    def tearDownClass(cls) -> None:
        arms = []
        for path in sorted(cls.artifact_root.glob("*/semantic.json")):
            arms.append(json.loads(path.read_text(encoding="utf-8")))
        ledger = {"arms": arms, "schema": "hv2-cp4-ledger-1"}
        (cls.artifact_root / "ledger.json").write_bytes(canonical_bytes(ledger))
        if cls.temporary is not None:
            cls.temporary.cleanup()

    def setUp(self) -> None:
        self.scenario = self.artifact_root / self._testMethodName
        self.scenario.mkdir()

    def record(self, arm: str, payload: dict[str, Any], runtime: dict[str, Any] | None = None) -> None:
        semantic = {"arm": arm, **payload}
        (self.scenario / "semantic.json").write_bytes(canonical_bytes(semantic))
        if runtime is not None:
            (self.scenario / "runtime.json").write_bytes(canonical_bytes(runtime))

    def worker_spec(
        self,
        *,
        action: str,
        participant: str,
        target: Path,
        parameters: dict[str, Any],
        barrier_root: Path | None = None,
        barrier_mode: str | None = None,
    ) -> dict[str, Any]:
        return {
            "action": action,
            "barrier_mode": barrier_mode,
            "barrier_root": str(barrier_root) if barrier_root else None,
            "barrier_timeout": 15.0,
            "parameters": parameters,
            "participant": participant,
            "target_root": str(target),
        }

    def spawn(self, spec: dict[str, Any], root: Path) -> tuple[subprocess.Popen[str], Path, Path, Path]:
        participant = spec["participant"]
        spec_path = root / f"{participant}.spec.json"
        result_path = root / f"{participant}.result.json"
        stderr_path = root / f"{participant}.stderr.txt"
        spec_path.write_bytes(canonical_bytes(spec))
        environment = dict(os.environ)
        environment.update({"PYTHONDONTWRITEBYTECODE": "1", "PYTHONPATH": str(SOURCE_ROOT)})
        process = subprocess.Popen(
            [sys.executable, "-B", str(WORKER), "--spec", str(spec_path), "--result", str(result_path)],
            cwd=Path(__file__).resolve().parents[1],
            env=environment,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return process, spec_path, result_path, stderr_path

    def wait_ready(self, processes: list[subprocess.Popen[str]], barrier: Path, participants: list[str]) -> str:
        deadline = time.monotonic() + 15.0
        ready = [barrier / f"{participant}.ready" for participant in participants]
        while not all(path.is_file() for path in ready):
            exited = [process.returncode for process in processes if process.poll() is not None]
            if exited:
                return "early-exit"
            if time.monotonic() >= deadline:
                return "timeout"
            time.sleep(0.01)
        return "all-ready"

    def collect(self, process: subprocess.Popen[str], result_path: Path) -> tuple[int, dict[str, Any], str, str]:
        stdout, stderr = process.communicate(timeout=20)
        if not result_path.is_file():
            raise AssertionError(f"worker result missing: rc={process.returncode}:stderr={stderr}")
        result = json.loads(result_path.read_text(encoding="utf-8"))
        return process.returncode, result, stdout, stderr

    def run_pair(
        self,
        root: Path,
        specs: list[dict[str, Any]],
        barrier: Path,
    ) -> tuple[list[tuple[int, dict[str, Any], str, str]], list[int]]:
        barrier.mkdir(parents=True)
        spawned = [self.spawn(spec, root) for spec in specs]
        processes = [entry[0] for entry in spawned]
        barrier_state = self.wait_ready(processes, barrier, [spec["participant"] for spec in specs])
        write_once(barrier / "release", {"released": True})
        if barrier_state == "timeout":
            for process in processes:
                if process.poll() is None:
                    process.terminate()
        collected = [self.collect(process, result_path) for process, _, result_path, _ in spawned]
        pids = [result[1]["pid"] for result in collected]
        self.assertEqual(len(pids), len(set(pids)))
        self.assertNotIn(os.getpid(), pids)
        return collected, pids

    def run_single(self, root: Path, spec: dict[str, Any]) -> tuple[int, dict[str, Any], str, str]:
        process, _, result_path, _ = self.spawn(spec, root)
        return self.collect(process, result_path)

    def assert_shared_unchanged(
        self,
        fixture: RepositoryFixture,
        before_project: dict[str, str],
        before_selector: bytes,
        before_index: str,
    ) -> None:
        self.assertEqual(before_project, project_digest(fixture.integration))
        self.assertEqual(before_selector, (fixture.integration / ".harness-v2/parallel/active-integration.json").read_bytes())
        self.assertEqual(before_index, git(fixture.integration, "write-tree"))

    def test_a1_disjoint_claims_two_processes_pass(self) -> None:
        fixture = RepositoryFixture(self.scenario / "repo")
        fixture.register_item("item-0002")
        work_a = fixture.add_worktree("work-a", "work/a")
        work_b = fixture.add_worktree("work-b", "work/b")
        before_project = project_digest(fixture.integration)
        before_selector = (fixture.integration / ".harness-v2/parallel/active-integration.json").read_bytes()
        before_index = git(fixture.integration, "write-tree")
        barrier = self.scenario / "barrier"
        specs = [
            self.worker_spec(
                action="claim",
                participant="actor-a",
                target=fixture.integration,
                parameters=fixture.claim_parameters(
                    claim_id="claim-a1-a",
                    item_id="item-0001",
                    worktree=work_a,
                    worktree_id="worktree-a",
                    scope=["src/alpha"],
                    actor="ACTOR-A",
                ),
                barrier_root=barrier,
                barrier_mode="claim-after-write",
            ),
            self.worker_spec(
                action="claim",
                participant="actor-b",
                target=fixture.integration,
                parameters=fixture.claim_parameters(
                    claim_id="claim-a1-b",
                    item_id="item-0002",
                    worktree=work_b,
                    worktree_id="worktree-b",
                    scope=["docs/beta"],
                    actor="ACTOR-B",
                ),
                barrier_root=barrier,
                barrier_mode="claim-after-write",
            ),
        ]
        results, pids = self.run_pair(self.scenario, specs, barrier)
        classifications = sorted(result[1]["classification"] for result in results)
        verified = fixture.store.verify_repository("item-0001")
        project_unchanged = before_project == project_digest(fixture.integration)
        selector_unchanged = before_selector == (
            fixture.integration / ".harness-v2/parallel/active-integration.json"
        ).read_bytes()
        index_unchanged = before_index == git(fixture.integration, "write-tree")
        worktrees_clean = not git(work_a, "status", "--porcelain") and not git(work_b, "status", "--porcelain")
        self.record(
            "CP4-A1",
            {
                "classifications": classifications,
                "claim_count": verified["claim_count"],
                "conflict_count": verified["conflict_count"],
                "index_unchanged": index_unchanged,
                "process_count": len(pids),
                "project_unchanged": project_unchanged,
                "selector_unchanged": selector_unchanged,
                "worktrees_clean": worktrees_clean,
            },
            {"parent_pid": os.getpid(), "worker_pids": pids},
        )
        self.assertEqual([0, 0], sorted(result[0] for result in results))
        self.assertEqual(["pass", "pass"], classifications)
        self.assertEqual(2, verified["claim_count"])
        self.assertEqual(0, verified["conflict_count"])
        self.assert_shared_unchanged(fixture, before_project, before_selector, before_index)
        self.assertEqual("", git(work_a, "status", "--porcelain"))
        self.assertEqual("", git(work_b, "status", "--porcelain"))

    def test_a2_git_commits_and_declared_finalizer_integration(self) -> None:
        fixture = RepositoryFixture(self.scenario / "repo")
        fixture.register_item("item-0002")
        work_a = fixture.add_worktree("work-a", "work/a")
        work_b = fixture.add_worktree("work-b", "work/b")
        for participant, parameters in (
            (
                "actor-a",
                fixture.claim_parameters(
                    claim_id="claim-a2-a",
                    item_id="item-0001",
                    worktree=work_a,
                    worktree_id="worktree-a",
                    scope=["src/alpha"],
                    actor="ACTOR-A",
                ),
            ),
            (
                "actor-b",
                fixture.claim_parameters(
                    claim_id="claim-a2-b",
                    item_id="item-0002",
                    worktree=work_b,
                    worktree_id="worktree-b",
                    scope=["docs/beta"],
                    actor="ACTOR-B",
                ),
            ),
        ):
            result = self.run_single(
                self.scenario,
                self.worker_spec(
                    action="claim",
                    participant=participant,
                    target=fixture.integration,
                    parameters=parameters,
                ),
            )
            self.assertEqual(0, result[0])
        fixture.commit_scoped(work_a, "src/alpha/a.txt", "alpha\n", "fixture: alpha work", 2)
        fixture.commit_scoped(work_b, "docs/beta/b.txt", "beta\n", "fixture: beta work", 3)
        fixture.merge("work/a", "fixture: integrate alpha", 4)
        fixture.merge("work/b", "fixture: integrate beta", 5)
        result_commit = git(fixture.integration, "rev-parse", "HEAD")
        result_tree = git(fixture.integration, "rev-parse", "HEAD^{tree}")
        final = self.run_single(
            self.scenario,
            self.worker_spec(
                action="finalize",
                participant="finalizer",
                target=fixture.integration,
                parameters=fixture.finalize_parameters(
                    epoch_id="epoch-a2",
                    claim_ids=["claim-a2-a", "claim-a2-b"],
                    claim_worktrees={"claim-a2-a": work_a, "claim-a2-b": work_b},
                    result_commit=result_commit,
                    result_tree=result_tree,
                ),
            ),
        )
        active = load_json(fixture.integration / ".harness-v2/parallel/active-integration.json", require_canonical=True)
        finalization = load_json(
            fixture.integration / ".harness-v2/parallel/generations/2/integration-epochs/epoch-a2/finalization.json",
            require_canonical=True,
        )
        inventory = finalization["project_mutation_inventory"]
        self.record(
            "CP4-A2",
            {
                "classification": final[1]["classification"],
                "current_commit": active["current_commit"],
                "inventory": inventory,
                "result_commit": result_commit,
                "result_tree": result_tree,
            },
            {"finalizer_pid": final[1]["pid"], "parent_pid": os.getpid()},
        )
        self.assertEqual(0, final[0])
        self.assertEqual("pass", final[1]["classification"])
        self.assertEqual(result_commit, active["current_commit"])
        self.assertEqual(["docs/beta/b.txt", "src/alpha/a.txt"], inventory)
        self.assertEqual("", git(work_a, "status", "--porcelain"))
        self.assertEqual("", git(work_b, "status", "--porcelain"))

    def test_a3_same_item_path_and_reserved_metadata_fail_closed(self) -> None:
        actual: dict[str, Any] = {}
        for label, same_item, scopes in (
            ("same-item", True, (["src/left"], ["docs/right"])),
            ("path-overlap", False, (["src/shared"], ["SRC/shared/file.txt"])),
        ):
            fixture = RepositoryFixture(self.scenario / label / "repo")
            fixture.register_item("item-0002")
            work_a = fixture.add_worktree("work-a", f"work/{label}-a")
            work_b = fixture.add_worktree("work-b", f"work/{label}-b")
            before_project = project_digest(fixture.integration)
            before_selector = (fixture.integration / ".harness-v2/parallel/active-integration.json").read_bytes()
            before_index = git(fixture.integration, "write-tree")
            before_harness = harness_digest(fixture.integration)
            barrier = self.scenario / label / "barrier"
            specs = [
                self.worker_spec(
                    action="claim",
                    participant=f"{label}-a",
                    target=fixture.integration,
                    parameters=fixture.claim_parameters(
                        claim_id=f"claim-{label}-a",
                        item_id="item-0001",
                        worktree=work_a,
                        worktree_id=f"worktree-{label}-a",
                        scope=scopes[0],
                        actor="ACTOR-A",
                    ),
                    barrier_root=barrier,
                    barrier_mode="claim-after-write",
                ),
                self.worker_spec(
                    action="claim",
                    participant=f"{label}-b",
                    target=fixture.integration,
                    parameters=fixture.claim_parameters(
                        claim_id=f"claim-{label}-b",
                        item_id="item-0001" if same_item else "item-0002",
                        worktree=work_b,
                        worktree_id=f"worktree-{label}-b",
                        scope=scopes[1],
                        actor="ACTOR-B",
                    ),
                    barrier_root=barrier,
                    barrier_mode="claim-after-write",
                ),
            ]
            results, _ = self.run_pair(self.scenario / label, specs, barrier)
            classifications = sorted(result[1]["classification"] for result in results)
            additions = added_paths(before_harness, harness_digest(fixture.integration))
            actual[label] = {
                "classifications": classifications,
                "evidence_only": all("/claims/" in path or "/conflicts/" in path for path in additions),
                "exit_codes": sorted(result[0] for result in results),
                "index_unchanged": before_index == git(fixture.integration, "write-tree"),
                "project_unchanged": before_project == project_digest(fixture.integration),
                "selector_unchanged": before_selector
                == (fixture.integration / ".harness-v2/parallel/active-integration.json").read_bytes(),
            }

        reserved = RepositoryFixture(self.scenario / "reserved" / "repo")
        work = reserved.add_worktree("work", "work/reserved")
        before = harness_digest(reserved.integration)
        reserved_result = self.run_single(
            self.scenario / "reserved",
            self.worker_spec(
                action="claim",
                participant="reserved",
                target=reserved.integration,
                parameters=reserved.claim_parameters(
                    claim_id="claim-reserved",
                    item_id="item-0001",
                    worktree=work,
                    worktree_id="worktree-reserved",
                    scope=[".harness-v2/parallel"],
                    actor="ACTOR-RESERVED",
                ),
            ),
        )
        actual["reserved"] = {
            "classification": reserved_result[1]["classification"],
            "code": reserved_result[1].get("contract_code"),
            "exit": reserved_result[0],
            "state_unchanged": before == harness_digest(reserved.integration),
        }
        self.record("CP4-A3", actual)
        for label in ("same-item", "path-overlap"):
            self.assertTrue(actual[label]["evidence_only"])
            self.assertTrue(actual[label]["project_unchanged"])
            self.assertTrue(actual[label]["selector_unchanged"])
            self.assertTrue(actual[label]["index_unchanged"])
            self.assertEqual(["conflict", "conflict"], actual[label]["classifications"])
            self.assertEqual([12, 12], actual[label]["exit_codes"])
        self.assertEqual(65, reserved_result[0])
        self.assertEqual("HV2-WRITE-SCOPE-CONTROL", reserved_result[1]["contract_code"])
        self.assertEqual(before, harness_digest(reserved.integration))

    def test_a4_stale_after_finalize_preserves_selector(self) -> None:
        fixture = RepositoryFixture(self.scenario / "repo")
        work = fixture.add_worktree("work", "work/current")
        claim = self.run_single(
            self.scenario,
            self.worker_spec(
                action="claim",
                participant="current",
                target=fixture.integration,
                parameters=fixture.claim_parameters(
                    claim_id="claim-current",
                    item_id="item-0001",
                    worktree=work,
                    worktree_id="worktree-current",
                    scope=["src/current.txt"],
                    actor="ACTOR-CURRENT",
                ),
            ),
        )
        self.assertEqual(0, claim[0])
        fixture.commit_scoped(work, "src/current.txt", "current\n", "fixture: current work", 2)
        fixture.merge("work/current", "fixture: integrate current", 3)
        result_commit = git(fixture.integration, "rev-parse", "HEAD")
        result_tree = git(fixture.integration, "rev-parse", "HEAD^{tree}")
        finalized = self.run_single(
            self.scenario,
            self.worker_spec(
                action="finalize",
                participant="finalizer",
                target=fixture.integration,
                parameters=fixture.finalize_parameters(
                    epoch_id="epoch-current",
                    claim_ids=["claim-current"],
                    claim_worktrees={"claim-current": work},
                    result_commit=result_commit,
                    result_tree=result_tree,
                ),
            ),
        )
        self.assertEqual(0, finalized[0])
        stale_work = fixture.add_worktree("stale-work", "work/stale", fixture.base_commit)
        selector_path = fixture.integration / ".harness-v2/parallel/active-integration.json"
        before_selector = selector_path.read_bytes()
        before_project = project_digest(fixture.integration)
        before_index = git(fixture.integration, "write-tree")
        stale = self.run_single(
            self.scenario,
            self.worker_spec(
                action="claim",
                participant="stale",
                target=fixture.integration,
                parameters=fixture.claim_parameters(
                    claim_id="claim-stale",
                    item_id="item-0001",
                    worktree=stale_work,
                    worktree_id="worktree-stale",
                    scope=["src/stale.txt"],
                    actor="ACTOR-STALE",
                ),
            ),
        )
        self.record(
            "CP4-A4",
            {
                "classification": stale[1]["classification"],
                "exit": stale[0],
                "selector_sha256": sha256_bytes(before_selector),
            },
            {"parent_pid": os.getpid(), "worker_pid": stale[1]["pid"]},
        )
        self.assertEqual(13, stale[0])
        self.assertEqual("stale", stale[1]["classification"])
        self.assert_shared_unchanged(fixture, before_project, before_selector, before_index)

    def test_a5_simultaneous_distinct_epoch_finalize_serializes(self) -> None:
        fixture = RepositoryFixture(self.scenario / "repo")
        work = fixture.add_worktree("work", "work/finalize")
        claim = self.run_single(
            self.scenario,
            self.worker_spec(
                action="claim",
                participant="claim",
                target=fixture.integration,
                parameters=fixture.claim_parameters(
                    claim_id="claim-finalize",
                    item_id="item-0001",
                    worktree=work,
                    worktree_id="worktree-finalize",
                    scope=["src/finalize.txt"],
                    actor="ACTOR-FINALIZE",
                ),
            ),
        )
        self.assertEqual(0, claim[0])
        fixture.commit_scoped(work, "src/finalize.txt", "finalize\n", "fixture: finalize work", 2)
        fixture.merge("work/finalize", "fixture: integrate finalize", 3)
        before_project = project_digest(fixture.integration)
        before_index = git(fixture.integration, "write-tree")
        result_commit = git(fixture.integration, "rev-parse", "HEAD")
        result_tree = git(fixture.integration, "rev-parse", "HEAD^{tree}")
        barrier = self.scenario / "barrier"
        specs = [
            self.worker_spec(
                action="finalize",
                participant="epoch-a",
                target=fixture.integration,
                parameters=fixture.finalize_parameters(
                    epoch_id="epoch-a5-a",
                    claim_ids=["claim-finalize"],
                    claim_worktrees={"claim-finalize": work},
                    result_commit=result_commit,
                    result_tree=result_tree,
                ),
                barrier_root=barrier,
                barrier_mode="finalize-before-switch",
            ),
            self.worker_spec(
                action="finalize",
                participant="epoch-b",
                target=fixture.integration,
                parameters=fixture.finalize_parameters(
                    epoch_id="epoch-a5-b",
                    claim_ids=["claim-finalize"],
                    claim_worktrees={"claim-finalize": work},
                    result_commit=result_commit,
                    result_tree=result_tree,
                ),
                barrier_root=barrier,
                barrier_mode="finalize-before-switch",
            ),
        ]
        results, pids = self.run_pair(self.scenario, specs, barrier)
        classifications = sorted(result[1]["classification"] for result in results)
        epoch_root = fixture.integration / ".harness-v2/parallel/generations/2/integration-epochs"
        finalizations = sorted(path.parent.name for path in epoch_root.glob("*/finalization.json"))
        arbitration_root = fixture.integration / ".harness-v2/parallel/generations/2/finalize-arbitrations"
        arbitrations = sorted(arbitration_root.glob("*.json"))
        arbitration_epochs = sorted(load_json(path, require_canonical=True)["epoch_id"] for path in arbitrations)
        active = load_json(fixture.integration / ".harness-v2/parallel/active-integration.json", require_canonical=True)
        self.record(
            "CP4-A5",
            {
                "active_matches_finalization": len(finalizations) == 1
                and active["integration_epoch_id"] == finalizations[0],
                "arbitration_count": len(arbitrations),
                "arbitration_matches_finalization": arbitration_epochs == finalizations,
                "classifications": classifications,
                "exit_codes": sorted(result[0] for result in results),
                "finalization_count": len(finalizations),
                "index_unchanged": before_index == git(fixture.integration, "write-tree"),
                "process_count": len(pids),
                "project_unchanged": before_project == project_digest(fixture.integration),
            },
            {
                "active_epoch": active["integration_epoch_id"],
                "arbitration_epochs": arbitration_epochs,
                "finalization_epochs": finalizations,
                "parent_pid": os.getpid(),
                "worker_pids": pids,
            },
        )
        self.assertEqual(1, classifications.count("pass"))
        self.assertEqual(1, len(arbitrations))
        self.assertEqual(1, len(finalizations))
        peer = [value for value in classifications if value != "pass"]
        self.assertEqual(1, len(peer))
        self.assertIn(peer[0], {"conflict", "stale"})
        self.assertEqual(finalizations, arbitration_epochs)
        self.assertEqual(finalizations[0], active["integration_epoch_id"])
        self.assertEqual(before_project, project_digest(fixture.integration))
        self.assertEqual(before_index, git(fixture.integration, "write-tree"))

    def test_a6_crash_abandoned_claim_and_explicit_reassignment(self) -> None:
        fixture = RepositoryFixture(self.scenario / "repo")
        work = fixture.add_worktree("work", "work/abandoned")
        barrier = self.scenario / "barrier"
        barrier.mkdir()
        spec = self.worker_spec(
            action="claim",
            participant="abandoned",
            target=fixture.integration,
            parameters=fixture.claim_parameters(
                claim_id="claim-abandoned",
                item_id="item-0001",
                worktree=work,
                worktree_id="worktree-abandoned",
                scope=["src/abandoned.txt"],
                actor="ACTOR-ABANDONED",
            ),
            barrier_root=barrier,
            barrier_mode="claim-after-write",
        )
        process, _, result_path, _ = self.spawn(spec, self.scenario)
        self.wait_ready([process], barrier, ["abandoned"])
        process.send_signal(signal.SIGKILL)
        stdout, stderr = process.communicate(timeout=10)
        self.assertEqual(-signal.SIGKILL, process.returncode)
        self.assertFalse(result_path.exists())
        claim_path = fixture.integration / ".harness-v2/parallel/generations/2/claims/claim-abandoned.json"
        self.assertTrue(claim_path.is_file())
        reassigned = self.run_single(
            self.scenario,
            self.worker_spec(
                action="reassign",
                participant="successor",
                target=fixture.integration,
                parameters={
                    "actor": "ACTOR-SUCCESSOR",
                    "claim_id": "claim-abandoned",
                    "finalizer": FINALIZER,
                    "observed_at": OBSERVED,
                    "reason": "fixture child terminated after claim write",
                    "reassignment_id": "reassignment-a6",
                },
            ),
        )
        verified = fixture.store.verify_repository("item-0001")
        self.record(
            "CP4-A6",
            {
                "claim_retained": claim_path.is_file(),
                "killed_returncode": process.returncode,
                "reassignment": reassigned[1]["classification"],
                "repository": verified["classification"],
            },
            {
                "killed_pid": process.pid,
                "parent_pid": os.getpid(),
                "stderr": stderr,
                "stdout": stdout,
                "successor_pid": reassigned[1]["pid"],
            },
        )
        self.assertEqual(0, reassigned[0])
        self.assertEqual("pass", reassigned[1]["classification"])
        self.assertEqual("pass", verified["classification"])

    def test_a7_deleted_and_diverged_worktrees_fail_closed(self) -> None:
        actual: dict[str, Any] = {}
        for label in ("deleted", "diverged"):
            fixture = RepositoryFixture(self.scenario / label / "repo")
            work = fixture.add_worktree("work", f"work/{label}")
            claim_id = f"claim-{label}"
            claimed = self.run_single(
                self.scenario / label,
                self.worker_spec(
                    action="claim",
                    participant=f"claim-{label}",
                    target=fixture.integration,
                    parameters=fixture.claim_parameters(
                        claim_id=claim_id,
                        item_id="item-0001",
                        worktree=work,
                        worktree_id=f"worktree-{label}",
                        scope=[f"src/{label}.txt"],
                        actor=f"ACTOR-{label.upper()}",
                    ),
                ),
            )
            self.assertEqual(0, claimed[0])
            before_selector = (fixture.integration / ".harness-v2/parallel/active-integration.json").read_bytes()
            if label == "deleted":
                git(fixture.integration, "worktree", "remove", "--force", str(work))
            else:
                git(work, "switch", "-c", "work/diverged-successor")
            finalized = self.run_single(
                self.scenario / label,
                self.worker_spec(
                    action="finalize",
                    participant=f"finalize-{label}",
                    target=fixture.integration,
                    parameters=fixture.finalize_parameters(
                        epoch_id=f"epoch-{label}",
                        claim_ids=[claim_id],
                        claim_worktrees={claim_id: work},
                        result_commit=fixture.base_commit,
                        result_tree=fixture.base_tree,
                    ),
                ),
            )
            actual[label] = {
                "classification": finalized[1]["classification"],
                "code": finalized[1].get("contract_code"),
                "exit": finalized[0],
            }
            self.assertEqual(65, finalized[0])
            self.assertEqual(before_selector, (fixture.integration / ".harness-v2/parallel/active-integration.json").read_bytes())
            self.assertFalse(
                (
                    fixture.integration
                    / f".harness-v2/parallel/generations/2/integration-epochs/epoch-{label}/finalization.json"
                ).exists()
            )
        self.record("CP4-A7", actual)

    def test_a8_single_process_manual_fallback(self) -> None:
        fixture = RepositoryFixture(self.scenario / "repo")
        work = fixture.add_worktree("work", "work/manual")
        result = self.run_single(
            self.scenario,
            self.worker_spec(
                action="manual-fallback",
                participant="manual-operator",
                target=fixture.integration,
                parameters={
                    "claim": fixture.claim_parameters(
                        claim_id="claim-manual",
                        item_id="item-0001",
                        worktree=work,
                        worktree_id="worktree-manual",
                        scope=["docs/manual"],
                        actor="ACTOR-MANUAL",
                    ),
                    "verify_item_id": "item-0001",
                },
            ),
        )
        self.record(
            "CP4-A8",
            {
                "classification": result[1]["classification"],
                "generation": result[1]["outcome"].get("generation"),
                "item_ids": result[1]["outcome"].get("item_ids"),
            },
            {"operator_pid": result[1]["pid"], "parent_pid": os.getpid()},
        )
        self.assertEqual(0, result[0])
        self.assertEqual("pass", result[1]["classification"])
        self.assertNotEqual(os.getpid(), result[1]["pid"])

    def test_a9_finalizer_crash_exact_resume_preserves_arbitration(self) -> None:
        fixture = RepositoryFixture(self.scenario / "repo")
        work = fixture.add_worktree("work", "work/finalizer-crash")
        claim = self.run_single(
            self.scenario,
            self.worker_spec(
                action="claim",
                participant="claim-finalizer-crash",
                target=fixture.integration,
                parameters=fixture.claim_parameters(
                    claim_id="claim-finalizer-crash",
                    item_id="item-0001",
                    worktree=work,
                    worktree_id="worktree-finalizer-crash",
                    scope=["src/finalizer-crash.txt"],
                    actor="ACTOR-FINALIZER-CRASH",
                ),
            ),
        )
        self.assertEqual(0, claim[0])
        fixture.commit_scoped(
            work,
            "src/finalizer-crash.txt",
            "finalizer crash\n",
            "fixture: finalizer crash work",
            2,
        )
        fixture.merge("work/finalizer-crash", "fixture: integrate finalizer crash", 3)
        result_commit = git(fixture.integration, "rev-parse", "HEAD")
        result_tree = git(fixture.integration, "rev-parse", "HEAD^{tree}")
        before_project = project_digest(fixture.integration)
        before_selector = (fixture.integration / ".harness-v2/parallel/active-integration.json").read_bytes()
        before_index = git(fixture.integration, "write-tree")
        parameters = fixture.finalize_parameters(
            epoch_id="epoch-a9-crash",
            claim_ids=["claim-finalizer-crash"],
            claim_worktrees={"claim-finalizer-crash": work},
            result_commit=result_commit,
            result_tree=result_tree,
        )
        barrier = self.scenario / "barrier"
        spec = self.worker_spec(
            action="finalize",
            participant="finalizer-crash",
            target=fixture.integration,
            parameters=parameters,
            barrier_root=barrier,
            barrier_mode="finalize-before-switch",
        )
        process, _, result_path, _ = self.spawn(spec, self.scenario)
        barrier_state = self.wait_ready([process], barrier, ["finalizer-crash"])
        self.assertEqual("all-ready", barrier_state)
        process.send_signal(signal.SIGKILL)
        stdout, stderr = process.communicate(timeout=10)
        self.assertEqual(-signal.SIGKILL, process.returncode)
        self.assertFalse(result_path.exists())
        selector_after_kill = (fixture.integration / ".harness-v2/parallel/active-integration.json").read_bytes()
        arbitration_root = fixture.integration / ".harness-v2/parallel/generations/2/finalize-arbitrations"
        epoch_root = fixture.integration / ".harness-v2/parallel/generations/2/integration-epochs/epoch-a9-crash"
        self.assertEqual(1, len(list(arbitration_root.glob("*.json"))))
        self.assertTrue((epoch_root / "finalization.json").is_file())
        self.assertEqual(before_selector, selector_after_kill)
        self.assertEqual(before_project, project_digest(fixture.integration))
        self.assertEqual(before_index, git(fixture.integration, "write-tree"))

        resumed = self.run_single(
            self.scenario,
            self.worker_spec(
                action="finalize",
                participant="finalizer-resume",
                target=fixture.integration,
                parameters=parameters,
            ),
        )
        verified = fixture.store.verify_repository("item-0001")
        active = load_json(fixture.integration / ".harness-v2/parallel/active-integration.json", require_canonical=True)
        arbitrations = list(arbitration_root.glob("*.json"))
        finalizations = list(
            (fixture.integration / ".harness-v2/parallel/generations/2/integration-epochs").glob("*/finalization.json")
        )
        self.record(
            "CP4-A9",
            {
                "active_matches_epoch": active["integration_epoch_id"] == "epoch-a9-crash",
                "arbitration_count": len(arbitrations),
                "classification": resumed[1]["classification"],
                "finalization_count": len(finalizations),
                "killed_returncode": process.returncode,
                "prior_selector_retained_after_kill": before_selector == selector_after_kill,
                "repository": verified["classification"],
                "resumed": resumed[1]["outcome"].get("resumed"),
            },
            {
                "killed_pid": process.pid,
                "parent_pid": os.getpid(),
                "resume_pid": resumed[1]["pid"],
                "stderr": stderr,
                "stdout": stdout,
            },
        )
        self.assertEqual(0, resumed[0])
        self.assertEqual("pass", resumed[1]["classification"])
        self.assertTrue(resumed[1]["outcome"].get("resumed"))
        self.assertEqual(1, len(arbitrations))
        self.assertEqual(1, len(finalizations))
        self.assertEqual("epoch-a9-crash", active["integration_epoch_id"])
        self.assertEqual("pass", verified["classification"])
        self.assertEqual(before_project, project_digest(fixture.integration))
        self.assertEqual(before_index, git(fixture.integration, "write-tree"))

    def test_a10_unresumable_arbitration_explicit_successor_recovers(self) -> None:
        fixture = RepositoryFixture(self.scenario / "repo")
        work = fixture.add_worktree("work", "work/successor")
        claim = self.run_single(
            self.scenario,
            self.worker_spec(
                action="claim",
                participant="claim-successor",
                target=fixture.integration,
                parameters=fixture.claim_parameters(
                    claim_id="claim-successor",
                    item_id="item-0001",
                    worktree=work,
                    worktree_id="worktree-successor",
                    scope=["src/successor.txt"],
                    actor="ACTOR-SUCCESSOR",
                ),
            ),
        )
        self.assertEqual(0, claim[0])
        fixture.commit_scoped(work, "src/successor.txt", "first result\n", "fixture: first successor result", 2)
        fixture.merge("work/successor", "fixture: integrate first successor result", 3)
        first_commit = git(fixture.integration, "rev-parse", "HEAD")
        first_tree = git(fixture.integration, "rev-parse", "HEAD^{tree}")
        prior_selector = (fixture.integration / ".harness-v2/parallel/active-integration.json").read_bytes()
        first_parameters = fixture.finalize_parameters(
            epoch_id="epoch-a10-abandoned",
            claim_ids=["claim-successor"],
            claim_worktrees={"claim-successor": work},
            result_commit=first_commit,
            result_tree=first_tree,
        )
        barrier = self.scenario / "abandoned-barrier"
        spec = self.worker_spec(
            action="finalize",
            participant="abandoned-finalizer",
            target=fixture.integration,
            parameters=first_parameters,
            barrier_root=barrier,
            barrier_mode="finalize-after-arbitration",
        )
        process, _, result_path, _ = self.spawn(spec, self.scenario)
        self.assertEqual("all-ready", self.wait_ready([process], barrier, ["abandoned-finalizer"]))
        process.send_signal(signal.SIGKILL)
        stdout, stderr = process.communicate(timeout=10)
        self.assertEqual(-signal.SIGKILL, process.returncode)
        self.assertFalse(result_path.exists())
        arbitration_root = fixture.integration / ".harness-v2/parallel/generations/2/finalize-arbitrations"
        abandoned_epoch = fixture.integration / ".harness-v2/parallel/generations/2/integration-epochs/epoch-a10-abandoned"
        self.assertEqual(1, len(list(arbitration_root.glob("*.json"))))
        self.assertFalse((abandoned_epoch / "finalization.json").exists())
        self.assertEqual(prior_selector, (fixture.integration / ".harness-v2/parallel/active-integration.json").read_bytes())

        git(fixture.integration, "worktree", "remove", "--force", str(work))
        exact_resume = self.run_single(
            self.scenario,
            self.worker_spec(
                action="finalize",
                participant="unresumable-exact",
                target=fixture.integration,
                parameters=first_parameters,
            ),
        )
        self.assertEqual(65, exact_resume[0])
        self.assertEqual("HV2-WORKTREE-ROOT", exact_resume[1].get("contract_code"))

        git(fixture.integration, "worktree", "add", str(work), "work/successor")
        git(work, "config", "user.name", GIT_NAME)
        git(work, "config", "user.email", GIT_EMAIL)
        (fixture.integration / "src/successor.txt").write_text("corrected result\n", encoding="utf-8")
        git(fixture.integration, "add", "src/successor.txt")
        git(fixture.integration, "commit", "-m", "fixture: correct successor result", sequence=4)
        corrected_commit = git(fixture.integration, "rev-parse", "HEAD")
        corrected_tree = git(fixture.integration, "rev-parse", "HEAD^{tree}")
        implicit_parameters = fixture.finalize_parameters(
            epoch_id="epoch-a10-implicit",
            claim_ids=["claim-successor"],
            claim_worktrees={"claim-successor": work},
            result_commit=corrected_commit,
            result_tree=corrected_tree,
        )
        implicit = self.run_single(
            self.scenario,
            self.worker_spec(
                action="finalize",
                participant="implicit-successor",
                target=fixture.integration,
                parameters=implicit_parameters,
            ),
        )
        self.assertEqual(12, implicit[0])
        self.assertEqual("conflict", implicit[1]["classification"])
        self.assertEqual(prior_selector, (fixture.integration / ".harness-v2/parallel/active-integration.json").read_bytes())

        successor_parameters = fixture.finalize_parameters(
            epoch_id="epoch-a10-successor",
            claim_ids=["claim-successor"],
            claim_worktrees={"claim-successor": work},
            result_commit=corrected_commit,
            result_tree=corrected_tree,
            succeeds_epoch_id="epoch-a10-abandoned",
            successor_reason="abandoned result corrected by declared finalizer",
        )
        successor = self.run_single(
            self.scenario,
            self.worker_spec(
                action="finalize",
                participant="explicit-successor",
                target=fixture.integration,
                parameters=successor_parameters,
            ),
        )
        self.assertEqual(0, successor[0])
        self.assertEqual("pass", successor[1]["classification"])
        before_successor_resume = harness_digest(fixture.integration)
        before_successor_project = project_digest(fixture.integration)
        before_successor_index = git(fixture.integration, "write-tree")
        exact_successor_resume = self.run_single(
            self.scenario,
            self.worker_spec(
                action="finalize",
                participant="explicit-successor-exact-resume",
                target=fixture.integration,
                parameters=successor_parameters,
            ),
        )
        self.assertEqual(0, exact_successor_resume[0])
        self.assertEqual("pass", exact_successor_resume[1]["classification"])
        self.assertTrue(exact_successor_resume[1]["outcome"]["resumed"])
        self.assertEqual(before_successor_resume, harness_digest(fixture.integration))
        self.assertEqual(before_successor_project, project_digest(fixture.integration))
        self.assertEqual(before_successor_index, git(fixture.integration, "write-tree"))
        late_predecessor = self.run_single(
            self.scenario,
            self.worker_spec(
                action="finalize",
                participant="late-predecessor",
                target=fixture.integration,
                parameters={**first_parameters, "claim_worktrees": {"claim-successor": str(work)}},
            ),
        )
        self.assertEqual(13, late_predecessor[0])
        self.assertEqual("stale", late_predecessor[1]["classification"])

        successor_root = fixture.integration / ".harness-v2/parallel/generations/2/finalize-successors"
        successors = list(successor_root.glob("*.json"))
        self.assertEqual(1, len(successors))
        successor_record = load_json(successors[0], require_canonical=True)
        successor_finalization = load_json(
            fixture.integration
            / ".harness-v2/parallel/generations/2/integration-epochs/epoch-a10-successor/finalization.json",
            require_canonical=True,
        )
        verified = fixture.store.verify_repository("item-0001")
        active = load_json(fixture.integration / ".harness-v2/parallel/active-integration.json", require_canonical=True)
        self.record(
            "CP4-A10",
            {
                "exact_resume_code": exact_resume[1].get("contract_code"),
                "implicit_classification": implicit[1]["classification"],
                "late_predecessor_classification": late_predecessor[1]["classification"],
                "repository": verified["classification"],
                "successor_count": len(successors),
                "successor_exact_resume": exact_successor_resume[1]["outcome"]["resumed"],
                "successor_finalization_bound": successor_finalization["arbitration_ref"]["id"]
                == successor_record["record_id"],
                "successor_is_active": active["integration_epoch_id"] == "epoch-a10-successor",
            },
            {
                "abandoned_pid": process.pid,
                "parent_pid": os.getpid(),
                "stderr": stderr,
                "stdout": stdout,
            },
        )
        self.assertEqual("pass", verified["classification"])
        self.assertEqual("epoch-a10-successor", active["integration_epoch_id"])
        self.assertEqual(successor_record["record_id"], successor_finalization["arbitration_ref"]["id"])

    def test_post_acceptance_successor_option_guards(self) -> None:
        fixture = RepositoryFixture(self.scenario / "repo")
        selector_path = fixture.integration / ".harness-v2/parallel/active-integration.json"
        before_harness = harness_digest(fixture.integration)
        before_project = project_digest(fixture.integration)
        before_selector = selector_path.read_bytes()
        before_index = git(fixture.integration, "write-tree")
        base_parameters = {
            "epoch_id": "epoch-post-acceptance",
            "claim_ids": ["claim-not-reached"],
            "finalizer": FINALIZER,
            "base_commit": fixture.base_commit,
            "base_tree": fixture.base_tree,
            "result_commit": fixture.base_commit,
            "result_tree": fixture.base_tree,
            "integration_branch": "main",
            "observed_at": OBSERVED,
            "integration_worktree_root": fixture.integration,
            "claim_worktrees": {},
        }
        cases = [
            ("successor-epoch-only", "HV2-SUCCESSOR-OPTION", "epoch-predecessor", None),
            ("successor-reason-only", "HV2-SUCCESSOR-OPTION", None, "explicit recovery"),
            ("same-epoch", "HV2-SUCCESSOR-EPOCH", "epoch-post-acceptance", "explicit recovery"),
            ("blank-reason", "HV2-SUCCESSOR-REASON", "epoch-predecessor", "   "),
        ]
        observed_codes: dict[str, str] = {}
        for name, expected_code, succeeds_epoch_id, successor_reason in cases:
            with self.subTest(name=name), self.assertRaises(ContractError) as failure:
                fixture.store.finalize_work(
                    **base_parameters,
                    succeeds_epoch_id=succeeds_epoch_id,
                    successor_reason=successor_reason,
                )
            self.assertEqual(expected_code, failure.exception.code)
            observed_codes[name] = failure.exception.code
            self.assertEqual(before_harness, harness_digest(fixture.integration))
            self.assertEqual(before_project, project_digest(fixture.integration))
            self.assertEqual(before_selector, selector_path.read_bytes())
            self.assertEqual(before_index, git(fixture.integration, "write-tree"))

        self.record(
            "POST-ACCEPTANCE-OBS-1",
            {
                "codes": observed_codes,
                "harness_unchanged": before_harness == harness_digest(fixture.integration),
                "index_unchanged": before_index == git(fixture.integration, "write-tree"),
                "project_unchanged": before_project == project_digest(fixture.integration),
                "selector_unchanged": before_selector == selector_path.read_bytes(),
            },
        )

    def test_a11_concurrent_same_epoch_exact_resume_uses_owned_temps(self) -> None:
        fixture = RepositoryFixture(self.scenario / "repo")
        work = fixture.add_worktree("work", "work/duplicate-resume")
        claim = self.run_single(
            self.scenario,
            self.worker_spec(
                action="claim",
                participant="claim-duplicate-resume",
                target=fixture.integration,
                parameters=fixture.claim_parameters(
                    claim_id="claim-duplicate-resume",
                    item_id="item-0001",
                    worktree=work,
                    worktree_id="worktree-duplicate-resume",
                    scope=["src/duplicate-resume.txt"],
                    actor="ACTOR-DUPLICATE-RESUME",
                ),
            ),
        )
        self.assertEqual(0, claim[0])
        fixture.commit_scoped(
            work,
            "src/duplicate-resume.txt",
            "duplicate resume\n",
            "fixture: duplicate resume work",
            2,
        )
        fixture.merge("work/duplicate-resume", "fixture: integrate duplicate resume", 3)
        result_commit = git(fixture.integration, "rev-parse", "HEAD")
        result_tree = git(fixture.integration, "rev-parse", "HEAD^{tree}")
        before_project = project_digest(fixture.integration)
        before_index = git(fixture.integration, "write-tree")
        parameters = fixture.finalize_parameters(
            epoch_id="epoch-a11-resume",
            claim_ids=["claim-duplicate-resume"],
            claim_worktrees={"claim-duplicate-resume": work},
            result_commit=result_commit,
            result_tree=result_tree,
        )
        crash_barrier = self.scenario / "crash-barrier"
        crash_spec = self.worker_spec(
            action="finalize",
            participant="resume-seed",
            target=fixture.integration,
            parameters=parameters,
            barrier_root=crash_barrier,
            barrier_mode="finalize-before-switch",
        )
        process, _, result_path, _ = self.spawn(crash_spec, self.scenario)
        self.assertEqual("all-ready", self.wait_ready([process], crash_barrier, ["resume-seed"]))
        process.send_signal(signal.SIGKILL)
        stdout, stderr = process.communicate(timeout=10)
        self.assertEqual(-signal.SIGKILL, process.returncode)
        self.assertFalse(result_path.exists())

        resume_barrier = self.scenario / "resume-barrier"
        specs = [
            self.worker_spec(
                action="finalize",
                participant=participant,
                target=fixture.integration,
                parameters=parameters,
                barrier_root=resume_barrier,
                barrier_mode="finalize-before-switch",
            )
            for participant in ("resume-a", "resume-b")
        ]
        results, pids = self.run_pair(self.scenario, specs, resume_barrier)
        classifications = sorted(result[1]["classification"] for result in results)
        resumed = sorted(result[1]["outcome"].get("resumed") for result in results)
        active_path = fixture.integration / ".harness-v2/parallel/active-integration.json"
        active = load_json(active_path, require_canonical=True)
        verified = fixture.store.verify_repository("item-0001")
        temp_residue = sorted(path.name for path in active_path.parent.glob(f".{active_path.name}.hv2-tmp-*"))
        self.record(
            "CP4-A11",
            {
                "classifications": classifications,
                "index_unchanged": before_index == git(fixture.integration, "write-tree"),
                "process_count": len(pids),
                "project_unchanged": before_project == project_digest(fixture.integration),
                "repository": verified["classification"],
                "resumed": resumed,
                "selector_epoch": active["integration_epoch_id"],
                "temp_residue_count": len(temp_residue),
            },
            {
                "killed_pid": process.pid,
                "parent_pid": os.getpid(),
                "resume_pids": pids,
                "stderr": stderr,
                "stdout": stdout,
            },
        )
        self.assertEqual([0, 0], sorted(result[0] for result in results))
        self.assertEqual(["pass", "pass"], classifications)
        self.assertEqual([True, True], resumed)
        self.assertEqual("epoch-a11-resume", active["integration_epoch_id"])
        self.assertEqual("pass", verified["classification"])
        self.assertEqual([], temp_residue)
        self.assertEqual(before_project, project_digest(fixture.integration))
        self.assertEqual(before_index, git(fixture.integration, "write-tree"))


if __name__ == "__main__":
    unittest.main()
