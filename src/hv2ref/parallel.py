from __future__ import annotations

import re
import subprocess
import unicodedata
from pathlib import Path, PurePosixPath
from typing import Any

from .errors import ContractError, InjectedCrash
from .jsonio import (
    canonical_json_bytes,
    load_json,
    replace_json,
    sha256_bytes,
    sha256_file,
    write_new_bytes,
    write_new_json,
)
from .state import ITEM_ID_PATTERN, StateStore


ID_PATTERN = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}")
SHA256_PATTERN = re.compile(r"[0-9a-f]{64}")
GIT_OBJECT_PATTERN = re.compile(r"[0-9a-f]{40}")
RESERVED_ROOTS = {".git", ".harness-v2"}


def _validate_id(kind: str, value: str) -> str:
    if not isinstance(value, str) or ID_PATTERN.fullmatch(value) is None:
        raise ContractError(f"HV2-{kind}-ID", repr(value))
    return value


def _validate_git_object(kind: str, value: str) -> str:
    if not isinstance(value, str) or GIT_OBJECT_PATTERN.fullmatch(value) is None:
        raise ContractError(f"HV2-{kind}", repr(value))
    return value


def _ref(record_id: str, data: bytes) -> dict[str, str]:
    return {"id": record_id, "sha256": sha256_bytes(data)}


def _path_ref(path: Path) -> dict[str, str]:
    value = load_json(path, require_canonical=True)
    record_id = value.get("record_id")
    if not isinstance(record_id, str) or not record_id:
        raise ContractError("HV2-GEN2-RECORD-ID", str(path))
    return _ref(record_id, path.read_bytes())


def _verify_ref(ref: Any, path: Path, expected_id: str | None = None) -> dict[str, Any]:
    if not isinstance(ref, dict) or set(ref) != {"id", "sha256"}:
        raise ContractError("HV2-REF-SHAPE", repr(ref))
    if not isinstance(ref["id"], str) or not isinstance(ref["sha256"], str):
        raise ContractError("HV2-REF-SHAPE", repr(ref))
    if SHA256_PATTERN.fullmatch(ref["sha256"]) is None:
        raise ContractError("HV2-REF-SHAPE", repr(ref))
    if expected_id is not None and ref["id"] != expected_id:
        raise ContractError("HV2-REF-ID", f"{ref['id']}:{expected_id}")
    if path.is_symlink() or not path.is_file():
        raise ContractError("HV2-REF-MISSING", str(path))
    if sha256_file(path) != ref["sha256"]:
        raise ContractError("HV2-REF-DIGEST", ref["id"])
    value = load_json(path, require_canonical=True)
    if value.get("record_id") != ref["id"]:
        raise ContractError("HV2-REF-ID", str(path))
    return value


def _write_exact_json(path: Path, value: Any) -> bool:
    data = canonical_json_bytes(value)
    if path.exists() or path.is_symlink():
        if path.is_symlink() or not path.is_file() or path.read_bytes() != data:
            raise ContractError("HV2-IMMUTABLE-CONTRADICTION", str(path))
        return False
    write_new_bytes(path, data)
    return True


def _git(root: Path, *args: str, check: bool = True) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    if check and result.returncode != 0:
        raise ContractError("HV2-GIT-IDENTITY", f"{args[0]}:{result.returncode}")
    return result.stdout.rstrip("\n")


def _git_identity(
    root: Path,
    expected_branch: str | None = None,
    *,
    require_clean: bool = False,
    allow_harness_dirty: bool = False,
) -> dict[str, str]:
    if root.is_symlink() or not root.is_dir():
        raise ContractError("HV2-WORKTREE-ROOT", str(root))
    resolved = root.resolve()
    top = Path(_git(resolved, "rev-parse", "--show-toplevel")).resolve()
    if top != resolved:
        raise ContractError("HV2-WORKTREE-ROOT", f"{top}:{resolved}")
    branch = _git(resolved, "symbolic-ref", "--quiet", "--short", "HEAD")
    if expected_branch is not None and branch != expected_branch:
        raise ContractError("HV2-WORKTREE-BRANCH", f"{branch}:{expected_branch}")
    status = _git(resolved, "status", "--porcelain")
    if require_clean and status:
        raise ContractError("HV2-WORKTREE-DIRTY", branch)
    if allow_harness_dirty and status:
        dirty_paths: list[str] = []
        for line in status.splitlines():
            value = line[3:]
            if " -> " in value:
                value = value.split(" -> ", 1)[1]
            dirty_paths.append(value)
        if any(path != ".harness-v2" and not path.startswith(".harness-v2/") for path in dirty_paths):
            raise ContractError("HV2-WORKTREE-DIRTY", f"{branch}:{dirty_paths}")
    return {
        "branch": branch,
        "commit": _git(resolved, "rev-parse", "HEAD"),
        "repository_common_dir": str(Path(_git(resolved, "rev-parse", "--git-common-dir")).resolve()),
        "tree": _git(resolved, "rev-parse", "HEAD^{tree}"),
        "worktree_root": str(resolved),
    }


def _is_ancestor(root: Path, ancestor: str, descendant: str) -> bool:
    result = subprocess.run(
        ["git", "merge-base", "--is-ancestor", ancestor, descendant],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode not in {0, 1}:
        raise ContractError("HV2-GIT-IDENTITY", f"merge-base:{result.returncode}")
    return result.returncode == 0


def _scope_overlap(left: tuple[str, ...], right: tuple[str, ...]) -> bool:
    for left_path in left:
        left_parts = tuple(part.casefold() for part in left_path.split("/"))
        for right_path in right:
            right_parts = tuple(part.casefold() for part in right_path.split("/"))
            shortest = min(len(left_parts), len(right_parts))
            if left_parts[:shortest] == right_parts[:shortest]:
                return True
    return False


def normalize_write_scope(worktree_root: Path, values: list[str]) -> tuple[str, ...]:
    if not isinstance(values, list) or not values:
        raise ContractError("HV2-WRITE-SCOPE", "empty")
    root = worktree_root.resolve()
    normalized: list[str] = []
    identities: set[tuple[str, ...]] = set()
    for raw in values:
        if not isinstance(raw, str) or not raw:
            raise ContractError("HV2-WRITE-SCOPE", repr(raw))
        if unicodedata.normalize("NFC", raw) != raw:
            raise ContractError("HV2-WRITE-SCOPE-NFC", raw)
        if "\\" in raw or any(ord(character) < 32 or ord(character) == 127 for character in raw):
            raise ContractError("HV2-WRITE-SCOPE-CHAR", repr(raw))
        if raw.startswith("/"):
            raise ContractError("HV2-WRITE-SCOPE-ABSOLUTE", raw)
        parts = raw.split("/")
        if any(part in {"", ".", ".."} for part in parts):
            raise ContractError("HV2-WRITE-SCOPE-SEGMENT", raw)
        pure = PurePosixPath(raw)
        if pure.is_absolute() or not pure.parts:
            raise ContractError("HV2-WRITE-SCOPE", raw)
        identity = tuple(part.casefold() for part in pure.parts)
        if identity[0] in RESERVED_ROOTS:
            raise ContractError("HV2-WRITE-SCOPE-CONTROL", raw)
        if identity in identities:
            raise ContractError("HV2-WRITE-SCOPE-COLLISION", raw)
        identities.add(identity)
        current = root
        for part in pure.parts:
            current = current / part
            if current.is_symlink():
                raise ContractError("HV2-WRITE-SCOPE-SYMLINK", raw)
        candidate = (root / Path(*pure.parts)).resolve(strict=False)
        try:
            candidate.relative_to(root)
        except ValueError as exc:
            raise ContractError("HV2-WRITE-SCOPE-ESCAPE", raw) from exc
        normalized.append(pure.as_posix())
    normalized.sort(key=lambda value: tuple(part.casefold() for part in value.split("/")))
    for index, left in enumerate(normalized):
        for right in normalized[index + 1 :]:
            if _scope_overlap((left,), (right,)):
                raise ContractError("HV2-WRITE-SCOPE-COLLISION", f"{left}:{right}")
    return tuple(normalized)


class ParallelStateStore:
    def __init__(self, target_root: Path):
        self.target_root = target_root.resolve()
        self.root = self.target_root / ".harness-v2"
        self.parallel_root = self.root / "parallel"
        self.generation_root = self.parallel_root / "generations" / "2"

    def _item_root(self, item_id: str) -> Path:
        if not isinstance(item_id, str) or ITEM_ID_PATTERN.fullmatch(item_id) is None:
            raise ContractError("HV2-ITEM-ID", repr(item_id))
        return self.root / "items" / item_id

    def _generation_assertion_path(self) -> Path:
        return self.parallel_root / "generation-assertions" / "generation-assertion-0002.json"

    def _repository_path(self) -> Path:
        return self.generation_root / "repository.json"

    def _active_generation_path(self) -> Path:
        return self.parallel_root / "active-generation.json"

    def _active_integration_path(self) -> Path:
        return self.parallel_root / "active-integration.json"

    def _registration_path(self, item_id: str) -> Path:
        return self.generation_root / "item-registrations" / f"{item_id}.json"

    def _claim_path(self, claim_id: str) -> Path:
        return self.generation_root / "claims" / f"{claim_id}.json"

    def _conflict_path(self, conflict_id: str) -> Path:
        return self.generation_root / "conflicts" / f"{conflict_id}.json"

    def _reassignment_path(self, reassignment_id: str) -> Path:
        return self.generation_root / "reassignments" / f"{reassignment_id}.json"

    def _epoch_root(self, epoch_id: str) -> Path:
        return self.generation_root / "integration-epochs" / epoch_id

    def _load_repository(self) -> dict[str, Any]:
        return load_json(self._repository_path(), require_canonical=True)

    def _load_active_integration(self) -> dict[str, Any]:
        return load_json(self._active_integration_path(), require_canonical=True)

    def _generation_one_inventory(self, item_id: str) -> list[dict[str, str]]:
        item_root = self._item_root(item_id)
        active_selector = item_root / "active-generation.json"
        entries: list[dict[str, str]] = []
        for path in sorted(self.root.rglob("*")):
            if not path.is_file() or path.is_symlink():
                continue
            if self.parallel_root in path.parents or path == active_selector or self.root / "staging" in path.parents:
                continue
            entries.append({"path": path.relative_to(self.target_root).as_posix(), "sha256": sha256_file(path)})
        return entries

    def activate_parallel(
        self,
        *,
        repository_id: str,
        item_id: str,
        finalizer: str,
        worktree_id: str,
        branch: str,
        base_commit: str,
        base_tree: str,
        observed_at: str,
        worktree_root: Path,
        _inject_at: str | None = None,
    ) -> dict[str, Any]:
        _validate_id("REPOSITORY", repository_id)
        self._item_root(item_id)
        _validate_id("ACTOR", finalizer)
        _validate_id("WORKTREE", worktree_id)
        _validate_id("BRANCH", branch.replace("/", "-"))
        _validate_git_object("BASE-COMMIT", base_commit)
        _validate_git_object("BASE-TREE", base_tree)
        if self.parallel_root.exists() or self.parallel_root.is_symlink():
            raise ContractError("HV2-GEN2-STABLE-REUSE", str(self.parallel_root))
        generation_one = StateStore(self.target_root).verify(item_id)
        if generation_one.get("classification") != "pass":
            raise ContractError("HV2-GEN1-ADMISSION", str(generation_one.get("classification")))
        git_identity = _git_identity(worktree_root, branch, require_clean=True)
        if git_identity["commit"] != base_commit or git_identity["tree"] != base_tree:
            raise ContractError("HV2-BASE-IDENTITY", f"{git_identity['commit']}:{git_identity['tree']}")
        authority = load_json(self.root / "authority.json", require_canonical=True)
        prior_selector_path = self._item_root(item_id) / "active-generation.json"
        prior_selector_bytes = prior_selector_path.read_bytes()
        prior_selector_ref = {"id": f"{item_id}-active-generation-0001", "sha256": sha256_bytes(prior_selector_bytes)}
        generation = {
            "generation": 2,
            "observed_at": observed_at,
            "record_id": "generation-assertion-0002",
            "record_type": "parallel-generation-assertion",
            "schema_generation": 2,
            "state": "active",
        }
        generation_path = self._generation_assertion_path()
        write_new_json(generation_path, generation)
        generation_ref = _path_ref(generation_path)
        repository = {
            "authority_home_id": authority.get("authority_home_id"),
            "declared_finalizer": finalizer,
            "generation_1_inventory": self._generation_one_inventory(item_id),
            "initial_base_commit": base_commit,
            "initial_base_tree": base_tree,
            "integration_branch": branch,
            "integration_worktree_id": worktree_id,
            "observed_at": observed_at,
            "record_id": "parallel-repository-0001",
            "record_type": "parallel-repository",
            "repository_id": repository_id,
            "schema_generation": 2,
        }
        write_new_json(self._repository_path(), repository)
        registration = {
            "item_id": item_id,
            "item_type": "minimum-production-vertical",
            "observed_at": observed_at,
            "predecessor_selector_ref": prior_selector_ref,
            "record_id": f"item-registration-{item_id}",
            "record_type": "item-registration",
            "schema_generation": 2,
        }
        write_new_json(self._registration_path(item_id), registration)
        initial_integration = {
            "current_commit": base_commit,
            "current_tree": base_tree,
            "finalization_ref": None,
            "integration_epoch_id": None,
            "schema_generation": 2,
        }
        write_new_json(self._active_integration_path(), initial_integration)
        item_selector = {
            "generation": 2,
            "generation_assertion_ref": generation_ref,
            "schema_generation": 2,
        }
        replace_json(prior_selector_path, item_selector)
        if _inject_at == "after_item_switch":
            raise InjectedCrash("after_gen2_item_switch")
        write_new_json(self._active_generation_path(), item_selector)
        return {
            "base_commit": base_commit,
            "base_tree": base_tree,
            "classification": "pass",
            "generation": 2,
            "item_id": item_id,
            "repository_id": repository_id,
        }

    def register_item(self, *, item_id: str, item_type: str, observed_at: str, _inject_at: str | None = None) -> dict[str, Any]:
        self._require_gen2()
        item_root = self._item_root(item_id)
        if item_root.exists() or item_root.is_symlink() or self._registration_path(item_id).exists():
            raise ContractError("HV2-ITEM-REUSE", item_id)
        _validate_id("ITEM-TYPE", item_type)
        identity = {"item_id": item_id, "item_type": item_type, "lineage": [], "schema_generation": 2}
        write_new_json(item_root / "identity.json", identity)
        registration = {
            "item_id": item_id,
            "item_type": item_type,
            "observed_at": observed_at,
            "predecessor_selector_ref": None,
            "record_id": f"item-registration-{item_id}",
            "record_type": "item-registration",
            "schema_generation": 2,
        }
        write_new_json(self._registration_path(item_id), registration)
        if _inject_at == "before_selector":
            raise InjectedCrash("before_gen2_item_selector")
        selector = load_json(self._active_generation_path(), require_canonical=True)
        write_new_json(item_root / "active-generation.json", selector)
        return {"classification": "pass", "generation": 2, "item_id": item_id}

    def _require_gen2(self) -> dict[str, Any]:
        path = self._active_generation_path()
        if not path.is_file() or path.is_symlink():
            raise ContractError("HV2-GEN2-INACTIVE", str(path))
        selector = load_json(path, require_canonical=True)
        if selector.get("generation") != 2 or selector.get("schema_generation") != 2:
            raise ContractError("HV2-GEN2-INACTIVE", repr(selector))
        _verify_ref(selector.get("generation_assertion_ref"), self._generation_assertion_path(), "generation-assertion-0002")
        return selector

    def _claims(self) -> list[tuple[Path, dict[str, Any]]]:
        claims_root = self.generation_root / "claims"
        if not claims_root.exists():
            return []
        return [(path, load_json(path, require_canonical=True)) for path in sorted(claims_root.glob("*.json"))]

    def _conflicts(self) -> list[tuple[Path, dict[str, Any]]]:
        conflicts_root = self.generation_root / "conflicts"
        if not conflicts_root.exists():
            return []
        return [(path, load_json(path, require_canonical=True)) for path in sorted(conflicts_root.glob("*.json"))]

    def _write_claim_conflict(
        self,
        claim_path: Path,
        claim: dict[str, Any],
        conflicting: list[tuple[Path, dict[str, Any]]],
        reasons: list[str],
        observed_at: str,
    ) -> dict[str, Any]:
        conflict_id = f"conflict-{claim['claim_id']}"
        record = {
            "candidate_claim_ref": _path_ref(claim_path),
            "conflicting_claim_refs": [_path_ref(path) for path, _ in conflicting],
            "observed_at": observed_at,
            "reasons": sorted(set(reasons)),
            "record_id": conflict_id,
            "record_type": "claim-conflict",
            "schema_generation": 2,
        }
        write_new_json(self._conflict_path(conflict_id), record)
        return {"claim_id": claim["claim_id"], "classification": "conflict", "conflict_id": conflict_id}

    def claim_work(
        self,
        *,
        claim_id: str,
        item_id: str,
        actor: str,
        finalizer: str,
        repository_id: str,
        worktree_id: str,
        branch: str,
        base_commit: str,
        base_tree: str,
        write_scope: list[str],
        observed_at: str,
        worktree_root: Path,
    ) -> dict[str, Any]:
        self._require_gen2()
        _validate_id("CLAIM", claim_id)
        self._item_root(item_id)
        _validate_id("ACTOR", actor)
        _validate_id("ACTOR", finalizer)
        _validate_id("REPOSITORY", repository_id)
        _validate_id("WORKTREE", worktree_id)
        _validate_git_object("BASE-COMMIT", base_commit)
        _validate_git_object("BASE-TREE", base_tree)
        if not self._registration_path(item_id).is_file():
            raise ContractError("HV2-ITEM-UNREGISTERED", item_id)
        repository = self._load_repository()
        if repository.get("repository_id") != repository_id:
            raise ContractError("HV2-REPOSITORY-IDENTITY", repository_id)
        if repository.get("declared_finalizer") != finalizer:
            raise ContractError("HV2-FINALIZER-DECLARATION", finalizer)
        git_identity = _git_identity(worktree_root, branch, require_clean=True)
        if git_identity["commit"] != base_commit or git_identity["tree"] != base_tree:
            raise ContractError("HV2-BASE-IDENTITY", f"{git_identity['commit']}:{git_identity['tree']}")
        scope = normalize_write_scope(worktree_root, write_scope)
        record = {
            "actor": actor,
            "base_commit": base_commit,
            "base_tree": base_tree,
            "branch": branch,
            "claim_id": claim_id,
            "finalizer": finalizer,
            "item_id": item_id,
            "observed_at": observed_at,
            "predecessor_ref": None,
            "record_id": claim_id,
            "record_type": "work-claim",
            "repository_id": repository_id,
            "schema_generation": 2,
            "worktree_id": worktree_id,
            "write_scope": list(scope),
        }
        claim_path = self._claim_path(claim_id)
        write_new_json(claim_path, record)
        active = self._load_active_integration()
        conflicting: list[tuple[Path, dict[str, Any]]] = []
        reasons: list[str] = []
        if active.get("current_commit") != base_commit or active.get("current_tree") != base_tree:
            reasons.append("stale-base")
        for other_path, other in self._claims():
            if other_path == claim_path:
                continue
            other_scope = tuple(other.get("write_scope", []))
            pair_reasons: list[str] = []
            if other.get("item_id") == item_id:
                pair_reasons.append("same-item")
            if _scope_overlap(scope, other_scope):
                pair_reasons.append("scope-overlap")
            if other.get("repository_id") != repository_id or other.get("finalizer") != finalizer:
                pair_reasons.append("control-metadata")
            if pair_reasons:
                conflicting.append((other_path, other))
                reasons.extend(pair_reasons)
        if reasons:
            result = self._write_claim_conflict(claim_path, record, conflicting, reasons, observed_at)
            if "stale-base" in reasons:
                result["classification"] = "stale"
            return result
        return {"claim_id": claim_id, "classification": "pass", "write_scope": list(scope)}

    def reassign_claim(
        self,
        *,
        reassignment_id: str,
        claim_id: str,
        actor: str,
        finalizer: str,
        reason: str,
        observed_at: str,
    ) -> dict[str, Any]:
        self._require_gen2()
        _validate_id("REASSIGNMENT", reassignment_id)
        _validate_id("ACTOR", actor)
        _validate_id("ACTOR", finalizer)
        claim_path = self._claim_path(claim_id)
        if not claim_path.is_file():
            raise ContractError("HV2-CLAIM-MISSING", claim_id)
        repository = self._load_repository()
        if repository.get("declared_finalizer") != finalizer:
            raise ContractError("HV2-FINALIZER-DECLARATION", finalizer)
        if not isinstance(reason, str) or not reason.strip():
            raise ContractError("HV2-REASSIGNMENT-REASON", repr(reason))
        record = {
            "actor": actor,
            "claim_ref": _path_ref(claim_path),
            "finalizer": finalizer,
            "observed_at": observed_at,
            "reason": reason,
            "record_id": reassignment_id,
            "record_type": "claim-reassignment",
            "schema_generation": 2,
        }
        write_new_json(self._reassignment_path(reassignment_id), record)
        return {"classification": "pass", "reassignment_id": reassignment_id}

    def _conflicted_claim_ids(self) -> set[str]:
        result: set[str] = set()
        for _, conflict in self._conflicts():
            if conflict.get("record_type") != "claim-conflict":
                continue
            candidate = conflict.get("candidate_claim_ref")
            if isinstance(candidate, dict) and isinstance(candidate.get("id"), str):
                result.add(candidate["id"])
            for ref in conflict.get("conflicting_claim_refs", []):
                if isinstance(ref, dict) and isinstance(ref.get("id"), str):
                    result.add(ref["id"])
        return result

    def finalize_work(
        self,
        *,
        epoch_id: str,
        claim_ids: list[str],
        finalizer: str,
        base_commit: str,
        base_tree: str,
        result_commit: str,
        result_tree: str,
        integration_branch: str,
        observed_at: str,
        integration_worktree_root: Path,
        claim_worktrees: dict[str, Path],
    ) -> dict[str, Any]:
        self._require_gen2()
        _validate_id("EPOCH", epoch_id)
        _validate_id("ACTOR", finalizer)
        for value, kind in (
            (base_commit, "BASE-COMMIT"),
            (base_tree, "BASE-TREE"),
            (result_commit, "RESULT-COMMIT"),
            (result_tree, "RESULT-TREE"),
        ):
            _validate_git_object(kind, value)
        if not claim_ids or len(set(claim_ids)) != len(claim_ids):
            raise ContractError("HV2-CLAIM-SET", repr(claim_ids))
        claim_ids = sorted(claim_ids)
        repository = self._load_repository()
        if repository.get("declared_finalizer") != finalizer:
            raise ContractError("HV2-FINALIZER-DECLARATION", finalizer)
        active = self._load_active_integration()
        if active.get("integration_epoch_id") == epoch_id:
            finalization_path = self._epoch_root(epoch_id) / "finalization.json"
            if not finalization_path.is_file():
                return {"classification": "conflict", "epoch_id": epoch_id}
            prior = load_json(finalization_path, require_canonical=True)
            prior_claim_ids = sorted(ref.get("id") for ref in prior.get("claim_refs", []) if isinstance(ref, dict))
            if (
                prior.get("base_commit") == base_commit
                and prior.get("base_tree") == base_tree
                and prior.get("result_commit") == result_commit
                and prior.get("result_tree") == result_tree
                and prior.get("finalizer") == finalizer
                and prior_claim_ids == claim_ids
                and active.get("current_commit") == result_commit
                and active.get("current_tree") == result_tree
            ):
                return {
                    "classification": "pass",
                    "epoch_id": epoch_id,
                    "result_commit": result_commit,
                    "result_tree": result_tree,
                    "resumed": True,
                }
            prior_refs = prior.get("claim_refs", [])
            conflict_id = f"finalize-conflict-{epoch_id}-duplicate"
            conflict = {
                "candidate_claim_ref": prior_refs[0],
                "conflicting_claim_refs": prior_refs[1:],
                "observed_at": observed_at,
                "reasons": ["duplicate-finalize-input"],
                "record_id": conflict_id,
                "record_type": "finalization-conflict",
                "schema_generation": 2,
            }
            _write_exact_json(self._conflict_path(conflict_id), conflict)
            return {"classification": "conflict", "epoch_id": epoch_id}
        if active.get("current_commit") != base_commit or active.get("current_tree") != base_tree:
            return {"classification": "stale", "epoch_id": epoch_id}
        conflicted = self._conflicted_claim_ids()
        claim_records: list[tuple[Path, dict[str, Any]]] = []
        scopes: list[tuple[str, ...]] = []
        for claim_id in claim_ids:
            claim_path = self._claim_path(claim_id)
            if not claim_path.is_file():
                raise ContractError("HV2-CLAIM-MISSING", claim_id)
            if claim_id in conflicted:
                return {"classification": "conflict", "epoch_id": epoch_id}
            claim = load_json(claim_path, require_canonical=True)
            if claim.get("finalizer") != finalizer or claim.get("base_commit") != base_commit or claim.get("base_tree") != base_tree:
                return {"classification": "conflict", "epoch_id": epoch_id}
            worktree = claim_worktrees.get(claim_id)
            if worktree is None:
                raise ContractError("HV2-CLAIM-WORKTREE", claim_id)
            identity = _git_identity(worktree, claim.get("branch"), require_clean=True)
            if not _is_ancestor(worktree, base_commit, identity["commit"]):
                raise ContractError("HV2-CLAIM-WORKTREE", claim_id)
            revalidated_scope = normalize_write_scope(worktree, claim.get("write_scope", []))
            if tuple(claim.get("write_scope", [])) != revalidated_scope:
                raise ContractError("HV2-WRITE-SCOPE", claim_id)
            claim_records.append((claim_path, claim))
            scopes.append(revalidated_scope)
        for index, left in enumerate(scopes):
            for right in scopes[index + 1 :]:
                if _scope_overlap(left, right):
                    return {"classification": "conflict", "epoch_id": epoch_id}
        integration_identity = _git_identity(
            integration_worktree_root,
            integration_branch,
            allow_harness_dirty=True,
        )
        if integration_identity["commit"] != result_commit or integration_identity["tree"] != result_tree:
            raise ContractError("HV2-RESULT-IDENTITY", f"{integration_identity['commit']}:{integration_identity['tree']}")
        if not _is_ancestor(integration_worktree_root, base_commit, result_commit):
            raise ContractError("HV2-RESULT-ANCESTRY", result_commit)
        for worktree in claim_worktrees.values():
            claim_head = _git_identity(worktree)["commit"]
            if not _is_ancestor(integration_worktree_root, claim_head, result_commit):
                raise ContractError("HV2-RESULT-MISSING-CLAIM", claim_head)
        project_mutation_inventory = [
            path
            for path in _git(integration_worktree_root, "diff", "--name-only", f"{base_commit}..{result_commit}").splitlines()
            if path
        ]
        combined_scope = tuple(scope for values in scopes for scope in values)
        for changed_path in project_mutation_inventory:
            if not any(_scope_overlap((changed_path,), (scope,)) for scope in combined_scope):
                raise ContractError("HV2-RESULT-SCOPE", changed_path)
        claim_refs = [_path_ref(path) for path, _ in claim_records]
        closed_claim_refs = [_path_ref(path) for path, _ in self._claims()]
        epoch_root = self._epoch_root(epoch_id)
        intent = {
            "base_commit": base_commit,
            "base_tree": base_tree,
            "claim_refs": claim_refs,
            "closed_claim_refs": closed_claim_refs,
            "finalizer": finalizer,
            "observed_at": observed_at,
            "record_id": f"integration-intent-{epoch_id}",
            "record_type": "integration-intent",
            "result_commit": result_commit,
            "result_tree": result_tree,
            "schema_generation": 2,
        }
        marker = {
            "base_commit": base_commit,
            "claim_refs": claim_refs,
            "finalizer": finalizer,
            "record_id": f"finalize-marker-{epoch_id}",
            "record_type": "finalize-marker",
            "result_commit": result_commit,
            "schema_generation": 2,
        }
        try:
            _write_exact_json(epoch_root / "intent.json", intent)
            _write_exact_json(epoch_root / "finalize-marker.json", marker)
        except ContractError as exc:
            conflict_id = f"finalize-conflict-{epoch_id}-marker"
            conflict = {
                "candidate_claim_ref": claim_refs[0],
                "conflicting_claim_refs": claim_refs[1:],
                "observed_at": observed_at,
                "reasons": ["duplicate-finalize-marker", exc.code],
                "record_id": conflict_id,
                "record_type": "finalization-conflict",
                "schema_generation": 2,
            }
            _write_exact_json(self._conflict_path(conflict_id), conflict)
            return {"classification": "conflict", "epoch_id": epoch_id}
        active_after_marker = self._load_active_integration()
        claims_after_marker = [_path_ref(path) for path, _ in self._claims()]
        integration_after_marker = _git_identity(
            integration_worktree_root,
            integration_branch,
            allow_harness_dirty=True,
        )
        worktrees_still_valid = True
        for claim_path, claim in claim_records:
            worktree = claim_worktrees[claim["claim_id"]]
            identity = _git_identity(worktree, claim.get("branch"), require_clean=True)
            if not _is_ancestor(worktree, base_commit, identity["commit"]) or not _is_ancestor(
                integration_worktree_root,
                identity["commit"],
                result_commit,
            ):
                worktrees_still_valid = False
                break
        revalidation_failed = (
            active_after_marker != active
            or claims_after_marker != closed_claim_refs
            or integration_after_marker["commit"] != result_commit
            or integration_after_marker["tree"] != result_tree
            or not worktrees_still_valid
        )
        if revalidation_failed:
            conflict_id = f"finalize-conflict-{epoch_id}-revalidation"
            conflict = {
                "candidate_claim_ref": claim_refs[0],
                "conflicting_claim_refs": claim_refs[1:],
                "observed_at": observed_at,
                "reasons": ["pre-switch-revalidation-failed"],
                "record_id": conflict_id,
                "record_type": "finalization-conflict",
                "schema_generation": 2,
            }
            _write_exact_json(self._conflict_path(conflict_id), conflict)
            return {"classification": "stale", "epoch_id": epoch_id}
        finalization = {
            "base_commit": base_commit,
            "base_tree": base_tree,
            "claim_refs": claim_refs,
            "finalizer": finalizer,
            "git_state": "integrated",
            "observed_at": observed_at,
            "project_mutation_inventory": project_mutation_inventory,
            "record_id": f"finalization-{epoch_id}",
            "record_type": "integration-finalization",
            "result_commit": result_commit,
            "result_tree": result_tree,
            "schema_generation": 2,
        }
        finalization_path = epoch_root / "finalization.json"
        _write_exact_json(finalization_path, finalization)
        selector = {
            "current_commit": result_commit,
            "current_tree": result_tree,
            "finalization_ref": _path_ref(finalization_path),
            "integration_epoch_id": epoch_id,
            "schema_generation": 2,
        }
        current_selector = self._active_integration_path()
        if current_selector.read_bytes() != canonical_json_bytes(selector):
            replace_json(current_selector, selector)
        return {"classification": "pass", "epoch_id": epoch_id, "result_commit": result_commit, "result_tree": result_tree}

    def verify_repository(self, item_id: str) -> dict[str, Any]:
        if not self._active_generation_path().exists():
            if self.parallel_root.exists():
                return {
                    "classification": "degraded",
                    "current_commit": None,
                    "degraded_reasons": ["partial-generation-2-activation"],
                    "finalizable": False,
                    "generation": 1,
                    "item_ids": [],
                    "writable": False,
                }
            result = StateStore(self.target_root).verify(item_id)
            result["generation"] = 1
            return result
        candidate_selector = load_json(self._active_generation_path(), require_canonical=True)
        if candidate_selector.get("generation") != 2 or candidate_selector.get("schema_generation") != 2:
            return {
                "classification": "incompatible",
                "current_commit": None,
                "degraded_reasons": [],
                "finalizable": False,
                "generation": candidate_selector.get("generation"),
                "incompatible_reasons": ["parallel-active-generation"],
                "item_ids": [],
                "writable": False,
            }
        selector = self._require_gen2()
        repository_path = self._repository_path()
        repository = load_json(repository_path, require_canonical=True)
        if repository.get("schema_generation") != 2 or repository.get("record_type") != "parallel-repository":
            raise ContractError("HV2-GEN2-REPOSITORY", str(repository_path))
        authority = load_json(self.root / "authority.json", require_canonical=True)
        if repository.get("authority_home_id") != authority.get("authority_home_id"):
            raise ContractError("HV2-AUTHORITY-HOME", str(repository.get("authority_home_id")))
        for entry in repository.get("generation_1_inventory", []):
            if not isinstance(entry, dict) or set(entry) != {"path", "sha256"}:
                raise ContractError("HV2-GEN1-INVENTORY", repr(entry))
            path = self.target_root / entry["path"]
            if path.is_symlink() or not path.is_file() or sha256_file(path) != entry["sha256"]:
                raise ContractError("HV2-GEN1-INVENTORY", entry["path"])
        registrations: list[dict[str, Any]] = []
        expected_parallel_files = {
            self._active_generation_path(),
            self._active_integration_path(),
            self._generation_assertion_path(),
            repository_path,
        }
        registration_root = self.generation_root / "item-registrations"
        for path in sorted(registration_root.glob("*.json")):
            registration = load_json(path, require_canonical=True)
            if registration.get("schema_generation") != 2 or registration.get("record_type") != "item-registration":
                raise ContractError("HV2-ITEM-REGISTRATION", str(path))
            registered_item = registration.get("item_id")
            if not isinstance(registered_item, str):
                raise ContractError("HV2-ITEM-REGISTRATION", str(path))
            item_root = self._item_root(registered_item)
            item_selector = load_json(item_root / "active-generation.json", require_canonical=True)
            if item_selector != selector:
                raise ContractError("HV2-ITEM-GENERATION", registered_item)
            identity = load_json(item_root / "identity.json", require_canonical=True)
            if identity.get("item_id") != registered_item or identity.get("schema_generation") not in {1, 2}:
                raise ContractError("HV2-ITEM-IDENTITY", registered_item)
            registrations.append(registration)
            expected_parallel_files.add(path)
        if not registrations:
            raise ContractError("HV2-ITEM-REGISTRATION", "empty")
        claims = self._claims()
        claim_ids: set[str] = set()
        for path, claim in claims:
            claim_id = claim.get("claim_id")
            if claim.get("schema_generation") != 2 or claim.get("record_type") != "work-claim" or claim.get("record_id") != claim_id:
                raise ContractError("HV2-CLAIM-RECORD", str(path))
            if claim_id in claim_ids:
                raise ContractError("HV2-CLAIM-REUSE", str(claim_id))
            claim_ids.add(claim_id)
            if path != self._claim_path(claim_id):
                raise ContractError("HV2-CLAIM-PATH", str(path))
            expected_parallel_files.add(path)
            if not self._registration_path(claim.get("item_id", "")).is_file():
                raise ContractError("HV2-ITEM-UNREGISTERED", str(claim.get("item_id")))
            if tuple(claim.get("write_scope", [])) != normalize_write_scope(self.target_root, claim.get("write_scope", [])):
                raise ContractError("HV2-WRITE-SCOPE", str(path))
        for path, conflict in self._conflicts():
            if conflict.get("schema_generation") != 2 or conflict.get("record_type") not in {"claim-conflict", "finalization-conflict"}:
                raise ContractError("HV2-CONFLICT-RECORD", str(path))
            candidate = conflict.get("candidate_claim_ref")
            if not isinstance(candidate, dict) or candidate.get("id") not in claim_ids:
                raise ContractError("HV2-CONFLICT-REF", str(path))
            _verify_ref(candidate, self._claim_path(candidate["id"]), candidate["id"])
            for ref in conflict.get("conflicting_claim_refs", []):
                if ref.get("id") not in claim_ids:
                    raise ContractError("HV2-CONFLICT-REF", str(path))
                _verify_ref(ref, self._claim_path(ref["id"]), ref["id"])
            if path != self._conflict_path(conflict.get("record_id", "")):
                raise ContractError("HV2-CONFLICT-PATH", str(path))
            expected_parallel_files.add(path)
        reassignment_root = self.generation_root / "reassignments"
        if reassignment_root.exists():
            for path in sorted(reassignment_root.glob("*.json")):
                value = load_json(path, require_canonical=True)
                if value.get("schema_generation") != 2 or value.get("record_type") != "claim-reassignment":
                    raise ContractError("HV2-REASSIGNMENT-RECORD", str(path))
                claim_ref = value.get("claim_ref")
                if not isinstance(claim_ref, dict) or claim_ref.get("id") not in claim_ids:
                    raise ContractError("HV2-REASSIGNMENT-REF", str(path))
                _verify_ref(claim_ref, self._claim_path(claim_ref["id"]), claim_ref["id"])
                if path != self._reassignment_path(value.get("record_id", "")):
                    raise ContractError("HV2-REASSIGNMENT-PATH", str(path))
                expected_parallel_files.add(path)
        epoch_root = self.generation_root / "integration-epochs"
        if epoch_root.exists():
            for directory in sorted(path for path in epoch_root.iterdir() if path.is_dir()):
                allowed_names = {"intent.json", "finalize-marker.json", "finalization.json"}
                for path in sorted(directory.iterdir()):
                    if path.is_symlink() or not path.is_file() or path.name not in allowed_names:
                        raise ContractError("HV2-GEN2-TREE-EXTRA", str(path))
                    value = load_json(path, require_canonical=True)
                    if value.get("schema_generation") != 2:
                        raise ContractError("HV2-EPOCH-RECORD", str(path))
                    expected_parallel_files.add(path)
                if not (directory / "intent.json").is_file() or not (directory / "finalize-marker.json").is_file():
                    raise ContractError("HV2-EPOCH-RECORD", str(directory))
        active = self._load_active_integration()
        if active.get("schema_generation") != 2:
            raise ContractError("HV2-ACTIVE-INTEGRATION", repr(active))
        finalization_ref = active.get("finalization_ref")
        if finalization_ref is not None:
            epoch_id = active.get("integration_epoch_id")
            finalization_path = self._epoch_root(epoch_id) / "finalization.json"
            finalization = _verify_ref(finalization_ref, finalization_path, f"finalization-{epoch_id}")
            if finalization.get("result_commit") != active.get("current_commit") or finalization.get("result_tree") != active.get("current_tree"):
                raise ContractError("HV2-ACTIVE-INTEGRATION", str(finalization_path))
        actual_parallel_files = {path for path in self.parallel_root.rglob("*") if path.is_file() or path.is_symlink()}
        if actual_parallel_files != expected_parallel_files:
            extra = sorted(str(path.relative_to(self.parallel_root)) for path in actual_parallel_files - expected_parallel_files)
            missing = sorted(str(path.relative_to(self.parallel_root)) for path in expected_parallel_files - actual_parallel_files)
            raise ContractError("HV2-GEN2-TREE", f"extra={extra}:missing={missing}")
        allowed_state_files = {
            self.target_root / entry["path"]
            for entry in repository.get("generation_1_inventory", [])
        }
        allowed_state_files.update(expected_parallel_files)
        for registration in registrations:
            registered_item = registration["item_id"]
            allowed_state_files.add(self._item_root(registered_item) / "identity.json")
            allowed_state_files.add(self._item_root(registered_item) / "active-generation.json")
        staging_root = self.root / "staging"
        actual_state_files = {
            path
            for path in self.root.rglob("*")
            if (path.is_file() or path.is_symlink()) and staging_root not in path.parents
        }
        if actual_state_files != allowed_state_files:
            extra = sorted(str(path.relative_to(self.root)) for path in actual_state_files - allowed_state_files)
            missing = sorted(str(path.relative_to(self.root)) for path in allowed_state_files - actual_state_files)
            raise ContractError("HV2-GEN2-STATE-TREE", f"extra={extra}:missing={missing}")
        return {
            "claim_count": len(claims),
            "classification": "pass",
            "conflict_count": len(self._conflicts()),
            "current_commit": active.get("current_commit"),
            "current_tree": active.get("current_tree"),
            "finalizable": True,
            "generation": 2,
            "item_ids": sorted(registration["item_id"] for registration in registrations),
            "repository_id": repository.get("repository_id"),
            "writable": True,
        }
