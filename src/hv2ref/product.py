from __future__ import annotations

import os
import re
import shutil
import stat
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .errors import ContractError, InjectedCrash
from .intent import IntentStore
from .jsonio import (
    canonical_json_bytes,
    decode_json_bytes,
    load_json,
    replace_json,
    sha256_bytes,
    sha256_file,
    sync_directory,
    write_new_bytes,
    write_new_json,
)
from .parallel import ParallelStateStore
from .state import StateStore


PRODUCT_ROOT_NAME = ".harness-v2-product"
DETACH_RECEIPT_NAME = ".harness-v2-detached.json"
ACTIVE_NAME = "active-release.json"
INIT_PLAN_NAME = "init-plan.json"
RELEASE_ID_PATTERN = re.compile(r"product-release-[0-9a-f]{24}")
PRODUCT_SCHEMA_VERSION = 1
DETACH_DOCUMENT_PATHS = (
    "AGENTS.md",
    "README.md",
    "docs/GETTING-STARTED.md",
    "docs/MANUAL-OPERATION.md",
    "docs/OPERATIONS.md",
)
DETACH_INSTRUCTIONS = (
    "Project-owned state remains in .harness-v2/.",
    "Accepted intent history remains in .harness-v2-intents/.",
    "Product-managed documentation is removed; preserve the named release documents before detach if offline guidance is required.",
    "No path, timestamp, or newest-file heuristic selects authority.",
    "D1-A detach is terminal; continue manually from project-owned state.",
)

MANAGED_PATHS = (
    ".gitignore",
    "AGENTS.md",
    "CLAUDE.md",
    "PRODUCT-CAPABILITIES.json",
    "README.md",
    "docs/CONCEPTS.md",
    "docs/GENERATION-1-CONTRACT.md",
    "docs/GENERATION-2-PARALLEL-SAFETY.md",
    "docs/GETTING-STARTED.md",
    "docs/GUIDED-INTENT-FORMATION.md",
    "docs/MAINTAINING.md",
    "docs/MANUAL-OPERATION.md",
    "docs/OPERATIONS.md",
    "docs/README.md",
    "docs/REFERENCE.md",
    "docs/SECURITY-AND-SUPPORT.md",
    "hv2",
    "src/hv2ref/__init__.py",
    "src/hv2ref/carrier.py",
    "src/hv2ref/cli.py",
    "src/hv2ref/errors.py",
    "src/hv2ref/intent.py",
    "src/hv2ref/jsonio.py",
    "src/hv2ref/parallel.py",
    "src/hv2ref/product.py",
    "src/hv2ref/state.py",
)


def source_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _exact_dict(value: object, keys: set[str], code: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != keys:
        actual = sorted(value) if isinstance(value, dict) else type(value).__name__
        raise ContractError(code, repr(actual))
    return value


def _require_lstat_type(path: Path, *, directory: bool, code: str) -> None:
    try:
        mode = path.lstat().st_mode
    except (FileNotFoundError, NotADirectoryError):
        raise ContractError(code, str(path)) from None
    matches = stat.S_ISDIR(mode) if directory else stat.S_ISREG(mode)
    if stat.S_ISLNK(mode) or not matches:
        raise ContractError(code, str(path))


def _validate_ref(value: object, code: str) -> dict[str, str]:
    ref = _exact_dict(value, {"id", "sha256"}, code)
    if not isinstance(ref["id"], str) or not isinstance(ref["sha256"], str):
        raise ContractError(code, repr(ref))
    if re.fullmatch(r"[0-9a-f]{64}", ref["sha256"]) is None:
        raise ContractError(code, repr(ref))
    return {"id": ref["id"], "sha256": ref["sha256"]}


def _safe_root(path: Path, code: str) -> Path:
    if path.is_symlink() or not path.exists() or not path.is_dir():
        raise ContractError(code, str(path))
    resolved = path.resolve()
    if resolved == Path("/") or resolved == Path.home().resolve():
        raise ContractError(code, str(resolved))
    return resolved


def _target_root(path: Path) -> Path:
    root = _safe_root(path, "HV2-PRODUCT-TARGET")
    marker = root / ".git"
    if marker.is_symlink() or not marker.exists() or not (marker.is_file() or marker.is_dir()):
        raise ContractError("HV2-PRODUCT-GIT-ROOT", str(root))
    return root


def _source_root(path: Path) -> Path:
    root = _safe_root(path, "HV2-PRODUCT-SOURCE")
    if root.name == PRODUCT_ROOT_NAME:
        raise ContractError("HV2-PRODUCT-SOURCE", str(root))
    return root


def _write_exact(path: Path, data: bytes) -> None:
    if path.exists() or path.is_symlink():
        if path.is_symlink() or not path.is_file() or path.read_bytes() != data:
            raise ContractError("HV2-PRODUCT-IMMUTABLE-CONTRADICTION", str(path))
        return
    write_new_bytes(path, data)


def _write_exact_json(path: Path, value: Any) -> None:
    _write_exact(path, canonical_json_bytes(value))


def _candidate(source: Path) -> dict[str, Any]:
    root = _source_root(source)
    inventory_path = root / "inventory.json"
    if inventory_path.exists() or inventory_path.is_symlink():
        if inventory_path.is_symlink():
            raise ContractError("HV2-PRODUCT-INSTALLED-SOURCE", str(root))
        try:
            _verify_release(root)
        except ContractError as exc:
            raise ContractError("HV2-PRODUCT-INSTALLED-SOURCE", f"unverified release-like source:{root}") from exc
        raise ContractError("HV2-PRODUCT-INSTALLED-SOURCE", str(root))
    entries = []
    payload: dict[str, bytes] = {}
    for relative in MANAGED_PATHS:
        path = root / relative
        cursor = root
        for component in Path(relative).parts[:-1]:
            cursor /= component
            if cursor.is_symlink() or not cursor.is_dir():
                raise ContractError("HV2-PRODUCT-SOURCE-DIRECTORY", str(cursor))
        if path.is_symlink() or not path.is_file():
            raise ContractError("HV2-PRODUCT-SOURCE-FILE", relative)
        data = path.read_bytes()
        payload[relative] = data
        entries.append({"path": relative, "sha256": sha256_bytes(data), "size_bytes": len(data)})
    capabilities = decode_json_bytes(payload["PRODUCT-CAPABILITIES.json"], require_canonical=True)
    if not isinstance(capabilities, dict):
        raise ContractError("HV2-PRODUCT-CAPABILITIES", "source manifest")
    inventory = {
        "entries": entries,
        "record_type": "product-release-inventory",
        "schema_version": PRODUCT_SCHEMA_VERSION,
    }
    inventory_bytes = canonical_json_bytes(inventory)
    release_id = f"product-release-{sha256_bytes(inventory_bytes)[:24]}"
    return {
        "inventory": inventory,
        "inventory_bytes": inventory_bytes,
        "payload": payload,
        "release_ref": {"id": release_id, "sha256": sha256_bytes(inventory_bytes)},
        "source": root,
    }


def _verify_release(path: Path) -> dict[str, str]:
    if path.is_symlink() or not path.is_dir() or RELEASE_ID_PATTERN.fullmatch(path.name) is None:
        raise ContractError("HV2-PRODUCT-RELEASE-PATH", str(path))
    inventory_path = path / "inventory.json"
    if inventory_path.is_symlink() or not inventory_path.is_file():
        raise ContractError("HV2-PRODUCT-INVENTORY", str(inventory_path))
    inventory = _exact_dict(
        load_json(inventory_path, require_canonical=True),
        {"entries", "record_type", "schema_version"},
        "HV2-PRODUCT-INVENTORY",
    )
    if inventory["record_type"] != "product-release-inventory" or inventory["schema_version"] != PRODUCT_SCHEMA_VERSION:
        raise ContractError("HV2-PRODUCT-INVENTORY", str(inventory_path))
    if not isinstance(inventory["entries"], list):
        raise ContractError("HV2-PRODUCT-INVENTORY", "entries")
    inventory_bytes = canonical_json_bytes(inventory)
    expected_id = f"product-release-{sha256_bytes(inventory_bytes)[:24]}"
    if path.name != expected_id:
        raise ContractError("HV2-PRODUCT-RELEASE-ID", path.name)
    expected_files = {"inventory.json"}
    prior = None
    for entry in inventory["entries"]:
        item = _exact_dict(entry, {"path", "sha256", "size_bytes"}, "HV2-PRODUCT-INVENTORY-ENTRY")
        relative = item["path"]
        if not isinstance(relative, str) or relative not in MANAGED_PATHS or relative == prior:
            raise ContractError("HV2-PRODUCT-INVENTORY-PATH", repr(relative))
        if prior is not None and relative.encode("utf-8") <= prior.encode("utf-8"):
            raise ContractError("HV2-PRODUCT-INVENTORY-ORDER", relative)
        prior = relative
        if type(item["size_bytes"]) is not int or item["size_bytes"] < 0:
            raise ContractError("HV2-PRODUCT-INVENTORY-SIZE", relative)
        if not isinstance(item["sha256"], str) or re.fullmatch(r"[0-9a-f]{64}", item["sha256"]) is None:
            raise ContractError("HV2-PRODUCT-INVENTORY-DIGEST", relative)
        file_path = path / relative
        if file_path.is_symlink() or not file_path.is_file():
            raise ContractError("HV2-PRODUCT-RELEASE-FILE", relative)
        if file_path.stat().st_size != item["size_bytes"] or sha256_file(file_path) != item["sha256"]:
            raise ContractError("HV2-PRODUCT-RELEASE-DIGEST", relative)
        expected_files.add(relative)
    if {entry["path"] for entry in inventory["entries"]} != set(MANAGED_PATHS):
        raise ContractError("HV2-PRODUCT-RELEASE-COVERAGE", path.name)
    actual_files = set()
    for member in path.rglob("*"):
        if member.is_symlink():
            raise ContractError("HV2-PRODUCT-RELEASE-SYMLINK", str(member))
        if member.is_file():
            actual_files.add(member.relative_to(path).as_posix())
    if actual_files != expected_files:
        raise ContractError("HV2-PRODUCT-RELEASE-TREE", repr(sorted(actual_files ^ expected_files)))
    return {"id": path.name, "sha256": sha256_bytes(inventory_bytes)}


def _ensure_directory(path: Path) -> None:
    if path.exists() or path.is_symlink():
        if path.is_symlink() or not path.is_dir():
            raise ContractError("HV2-PRODUCT-DIRECTORY", str(path))
        return
    path.mkdir()
    sync_directory(path.parent)


class ProductStore:
    def __init__(self, target_root: Path):
        self.target_root = _target_root(target_root)
        self.root = self.target_root / PRODUCT_ROOT_NAME
        self.releases = self.root / "releases"
        self.staging = self.root / "staging"
        self.receipts = self.root / "receipts"
        self.active_path = self.root / ACTIVE_NAME
        self.plan_path = self.root / INIT_PLAN_NAME
        self.launcher_path = self.target_root / "hv2"
        self.detach_receipt_path = self.target_root / DETACH_RECEIPT_NAME

    def _ensure_product_root(self) -> None:
        if self.root.is_symlink():
            raise ContractError("HV2-PRODUCT-ROOT", str(self.root))
        _ensure_directory(self.root)
        _ensure_directory(self.releases)
        _ensure_directory(self.staging)
        _ensure_directory(self.receipts)

    def _release_path(self, release_ref: dict[str, str]) -> Path:
        if RELEASE_ID_PATTERN.fullmatch(release_ref["id"]) is None:
            raise ContractError("HV2-PRODUCT-RELEASE-REF", release_ref["id"])
        return self.releases / release_ref["id"]

    def _verify_release_ref(self, release_ref: object) -> dict[str, str]:
        ref = _validate_ref(release_ref, "HV2-PRODUCT-RELEASE-REF")
        actual = _verify_release(self._release_path(ref))
        if actual != ref:
            raise ContractError("HV2-PRODUCT-RELEASE-REF", repr(ref))
        return ref

    def _materialize_release(self, candidate: dict[str, Any]) -> dict[str, str]:
        self._ensure_product_root()
        release_ref = candidate["release_ref"]
        final = self._release_path(release_ref)
        if final.exists() or final.is_symlink():
            actual = _verify_release(final)
            if actual != release_ref:
                raise ContractError("HV2-PRODUCT-RELEASE-CONTRADICTION", final.name)
            return actual
        stage = self.staging / release_ref["id"]
        if stage.is_symlink():
            raise ContractError("HV2-PRODUCT-STAGING", str(stage))
        _ensure_directory(stage)
        for relative, data in candidate["payload"].items():
            _write_exact(stage / relative, data)
        _write_exact(stage / "inventory.json", candidate["inventory_bytes"])
        actual = _verify_release(stage)
        if actual != release_ref:
            raise ContractError("HV2-PRODUCT-STAGING", stage.name)
        os.replace(stage, final)
        sync_directory(self.releases)
        sync_directory(self.staging)
        return _verify_release(final)

    def _load_active(self) -> dict[str, Any]:
        if self.active_path.is_symlink() or not self.active_path.is_file():
            raise ContractError("HV2-PRODUCT-ACTIVE", str(self.active_path))
        active = _exact_dict(
            load_json(self.active_path, require_canonical=True),
            {"prior_release_ref", "receipt_ref", "record_type", "release_ref", "schema_version"},
            "HV2-PRODUCT-ACTIVE",
        )
        if active["record_type"] != "product-active-release" or active["schema_version"] != PRODUCT_SCHEMA_VERSION:
            raise ContractError("HV2-PRODUCT-ACTIVE", str(self.active_path))
        active["release_ref"] = self._verify_release_ref(active["release_ref"])
        if active["prior_release_ref"] is not None:
            active["prior_release_ref"] = self._verify_release_ref(active["prior_release_ref"])
        active["receipt_ref"] = _validate_ref(active["receipt_ref"], "HV2-PRODUCT-RECEIPT-REF")
        receipt_path = self.receipts / f"{active['receipt_ref']['id']}.json"
        if receipt_path.is_symlink() or not receipt_path.is_file() or sha256_file(receipt_path) != active["receipt_ref"]["sha256"]:
            raise ContractError("HV2-PRODUCT-RECEIPT-REF", str(receipt_path))
        return active

    def _load_plan(self) -> dict[str, Any]:
        _require_lstat_type(self.plan_path, directory=False, code="HV2-PRODUCT-INIT-PLAN")
        plan = _exact_dict(
            load_json(self.plan_path, require_canonical=True),
            {
                "intent_authority_home_id",
                "item_id",
                "observed_at",
                "record_type",
                "release_ref",
                "schema_version",
                "state_authority_home_id",
            },
            "HV2-PRODUCT-INIT-PLAN",
        )
        if plan["record_type"] != "product-init-plan" or plan["schema_version"] != PRODUCT_SCHEMA_VERSION:
            raise ContractError("HV2-PRODUCT-INIT-PLAN", str(self.plan_path))
        plan["release_ref"] = _validate_ref(plan["release_ref"], "HV2-PRODUCT-RELEASE-REF")
        for key in ("intent_authority_home_id", "item_id", "observed_at", "state_authority_home_id"):
            if not isinstance(plan[key], str) or not plan[key]:
                raise ContractError("HV2-PRODUCT-INIT-PLAN", key)
        return plan

    def _init_plan(self, release_ref: dict[str, str]) -> dict[str, Any]:
        if self.plan_path.exists() or self.plan_path.is_symlink():
            plan = self._load_plan()
            if plan["release_ref"] != release_ref:
                raise ContractError("HV2-PRODUCT-INIT-PLAN", "release contradiction")
            return plan
        existing_authority = any(
            path.exists() or path.is_symlink()
            for path in (
                self.target_root / ".harness-v2",
                self.target_root / ".harness-v2-intents",
                self.detach_receipt_path,
            )
        )
        if existing_authority:
            raise ContractError("HV2-PRODUCT-ATTACH-REQUIRED", "existing authority or detach receipt; init cannot reissue identity")
        plan = {
            "intent_authority_home_id": str(uuid.uuid4()),
            "item_id": "item-0001",
            "observed_at": _now(),
            "record_type": "product-init-plan",
            "release_ref": release_ref,
            "schema_version": PRODUCT_SCHEMA_VERSION,
            "state_authority_home_id": str(uuid.uuid4()),
        }
        write_new_json(self.plan_path, plan)
        return plan

    def _ensure_state(self, plan: dict[str, Any]) -> None:
        state_root = self.target_root / ".harness-v2"
        if not state_root.exists() and not state_root.is_symlink():
            StateStore(self.target_root).initialize(
                plan["state_authority_home_id"],
                plan["item_id"],
                plan["observed_at"],
            )
        self._verify_state(plan)

    def _verify_state(self, plan: dict[str, Any]) -> dict[str, Any]:
        state_root = self.target_root / ".harness-v2"
        authority_path = state_root / "authority.json"
        _require_lstat_type(state_root, directory=True, code="HV2-PRODUCT-STATE-BINDING")
        _require_lstat_type(authority_path, directory=False, code="HV2-PRODUCT-STATE-BINDING")
        authority = load_json(authority_path, require_canonical=True)
        if not isinstance(authority, dict) or authority.get("authority_home_id") != plan["state_authority_home_id"]:
            raise ContractError("HV2-PRODUCT-STATE-BINDING", repr(authority))
        result = ParallelStateStore(self.target_root).verify_repository(plan["item_id"])
        resumable = result.get("classification") == "degraded" and result.get("resumable") is True
        if result.get("classification") != "pass" and not resumable:
            raise ContractError("HV2-PRODUCT-STATE-BINDING", repr(result))
        generation = result.get("generation")
        if generation not in {1, 2}:
            raise ContractError("HV2-PRODUCT-STATE-BINDING", repr(result))
        if generation == 2 and plan["item_id"] not in result.get("item_ids", []):
            raise ContractError("HV2-PRODUCT-STATE-BINDING", repr(result))
        return result

    def _ensure_intent_home(self, plan: dict[str, Any]) -> None:
        intent_root = self.target_root / ".harness-v2-intents"
        if not intent_root.exists() and not intent_root.is_symlink():
            IntentStore(self.target_root).initialize(plan["intent_authority_home_id"], plan["observed_at"])
        self._verify_intent_home(plan)

    def _verify_intent_home(self, plan: dict[str, Any]) -> None:
        intent_root = self.target_root / ".harness-v2-intents"
        authority_path = intent_root / "authority.json"
        _require_lstat_type(intent_root, directory=True, code="HV2-PRODUCT-INTENT-BINDING")
        _require_lstat_type(authority_path, directory=False, code="HV2-PRODUCT-INTENT-BINDING")
        authority = _exact_dict(
            load_json(authority_path, require_canonical=True),
            {"authority_home_id", "authority_kind", "created_at", "record_type", "schema_generation"},
            "HV2-PRODUCT-INTENT-BINDING",
        )
        if authority["authority_home_id"] != plan["intent_authority_home_id"]:
            raise ContractError("HV2-PRODUCT-INTENT-BINDING", repr(authority["authority_home_id"]))

    def _write_launcher(self, release_ref: dict[str, str], *, allow_missing: bool = True) -> None:
        source_launcher = self._release_path(release_ref) / "hv2"
        data = source_launcher.read_bytes()
        if self.launcher_path.exists() or self.launcher_path.is_symlink():
            if self.launcher_path.is_symlink() or not self.launcher_path.is_file() or self.launcher_path.read_bytes() != data:
                raise ContractError("HV2-PRODUCT-LAUNCHER-DRIFT", str(self.launcher_path))
        elif allow_missing:
            write_new_bytes(self.launcher_path, data)
        else:
            raise ContractError("HV2-PRODUCT-LAUNCHER-MISSING", str(self.launcher_path))
        os.chmod(self.launcher_path, 0o755)
        sync_directory(self.target_root)

    def _verify_launcher(self, release_ref: dict[str, str]) -> None:
        source_launcher = self._release_path(release_ref) / "hv2"
        if self.launcher_path.is_symlink() or not self.launcher_path.is_file():
            raise ContractError("HV2-PRODUCT-LAUNCHER-MISSING", str(self.launcher_path))
        if self.launcher_path.read_bytes() != source_launcher.read_bytes():
            raise ContractError("HV2-PRODUCT-LAUNCHER-DRIFT", str(self.launcher_path))
        if self.launcher_path.stat().st_mode & 0o111 == 0:
            raise ContractError("HV2-PRODUCT-LAUNCHER-MODE", str(self.launcher_path))

    def _receipt(self, receipt_id: str, fields: dict[str, Any]) -> dict[str, str]:
        path = self.receipts / f"{receipt_id}.json"
        if path.exists() or path.is_symlink():
            receipt = load_json(path, require_canonical=True)
            if not isinstance(receipt, dict):
                raise ContractError("HV2-PRODUCT-RECEIPT", receipt_id)
            expected = {
                **fields,
                "observed_at": receipt.get("observed_at"),
                "receipt_id": receipt_id,
                "record_type": "product-operation-receipt",
                "schema_version": PRODUCT_SCHEMA_VERSION,
            }
            if receipt != expected:
                raise ContractError("HV2-PRODUCT-RECEIPT-CONTRADICTION", receipt_id)
        else:
            receipt = {
                **fields,
                "observed_at": _now(),
                "receipt_id": receipt_id,
                "record_type": "product-operation-receipt",
                "schema_version": PRODUCT_SCHEMA_VERSION,
            }
            write_new_json(path, receipt)
        return {"id": receipt_id, "sha256": sha256_file(path)}

    def _switch(self, release_ref: dict[str, str], prior: dict[str, str] | None, receipt_ref: dict[str, str]) -> None:
        replace_json(
            self.active_path,
            {
                "prior_release_ref": prior,
                "receipt_ref": receipt_ref,
                "record_type": "product-active-release",
                "release_ref": release_ref,
                "schema_version": PRODUCT_SCHEMA_VERSION,
            },
        )

    def _strict_status(self) -> dict[str, Any]:
        if self.root.is_symlink():
            raise ContractError("HV2-PRODUCT-ROOT", str(self.root))
        if not self.root.exists():
            if self.detach_receipt_path.exists() or self.detach_receipt_path.is_symlink():
                receipt = self._load_detach_receipt()
                return {
                    "classification": "detached",
                    "detach_receipt": receipt,
                    "next_action": "continue manually from plain project-owned state; D1-A detach is terminal",
                    "product_root": PRODUCT_ROOT_NAME,
                }
            return {
                "classification": "uninitialized",
                "next_action": "run hv2 init --target <project> --apply from the contribution source",
                "product_root": PRODUCT_ROOT_NAME,
            }
        if not self.active_path.exists() and not self.active_path.is_symlink():
            if self.detach_receipt_path.exists() or self.detach_receipt_path.is_symlink():
                receipt = self._load_detach_receipt()
                self._validate_interrupted_detach_completion(receipt)
                return {
                    "classification": "partial",
                    "next_action": (
                        "repeat the exact hv2 detach --target <project> --apply command from a trusted contribution source; "
                        "do not init, update, or rollback"
                    ),
                    "product_root": PRODUCT_ROOT_NAME,
                }
            return {
                "classification": "partial",
                "next_action": "repeat the exact init command from the contribution source",
                "product_root": PRODUCT_ROOT_NAME,
            }
        plan = self._load_plan()
        durable_root_entries = {ACTIVE_NAME, INIT_PLAN_NAME, "receipts", "releases"}
        allowed_root_entries = durable_root_entries | {"staging"}
        actual_root_entries = {path.name for path in self.root.iterdir()}
        missing = durable_root_entries - actual_root_entries
        unexpected = actual_root_entries - allowed_root_entries
        if missing or unexpected:
            raise ContractError("HV2-PRODUCT-ROOT-TREE", repr(sorted(missing | unexpected)))
        if self.staging.exists() or self.staging.is_symlink():
            if self.staging.is_symlink() or not self.staging.is_dir():
                raise ContractError("HV2-PRODUCT-STAGING", str(self.staging))
            staging_entries = sorted(self.staging.iterdir(), key=lambda path: path.name)
            if staging_entries:
                raise ContractError("HV2-PRODUCT-STAGING", str(staging_entries[0]))
        active = self._load_active()
        if active["release_ref"] != plan["release_ref"] and active["prior_release_ref"] is None:
            raise ContractError("HV2-PRODUCT-INIT-PLAN", "active lineage")
        self._verify_existing_detach_receipt(active, plan)
        self._verify_launcher(active["release_ref"])
        state = self._verify_state(plan)
        if state.get("resumable") is True:
            interruption = state.get("interruption")
            if not isinstance(interruption, dict) or not isinstance(interruption.get("resume_action"), str):
                raise ContractError("HV2-PRODUCT-STATE-BINDING", repr(state))
            raise ContractError("HV2-PRODUCT-STATE-INTERRUPTED", interruption["resume_action"])
        self._verify_intent_home(plan)
        capabilities_path = self._release_path(active["release_ref"]) / "PRODUCT-CAPABILITIES.json"
        capabilities = load_json(capabilities_path, require_canonical=True)
        if not isinstance(capabilities, dict):
            raise ContractError("HV2-PRODUCT-CAPABILITIES", str(capabilities_path))
        documentation_root = str(
            (Path(PRODUCT_ROOT_NAME) / "releases" / active["release_ref"]["id"] / "docs").as_posix()
        )
        return {
            "capabilities": capabilities,
            "classification": "pass",
            "documentation_root": documentation_root,
            "intent_authority_home_id": plan["intent_authority_home_id"],
            "item_id": plan["item_id"],
            "next_action": f"read {documentation_root}/GETTING-STARTED.md or run hv2 doctor",
            "prior_release_ref": active["prior_release_ref"],
            "product_root": PRODUCT_ROOT_NAME,
            "release_ref": active["release_ref"],
            "state": state,
            "state_authority_home_id": plan["state_authority_home_id"],
        }

    def status(self) -> dict[str, Any]:
        try:
            return self._strict_status()
        except ContractError as exc:
            classification = "degraded"
            next_action = "run doctor from a trusted source checkout; do not update or detach until the contradiction is resolved"
            if exc.code == "HV2-PRODUCT-DETACH-INCOMPLETE":
                classification = "partial"
                next_action = (
                    "repeat the exact hv2 detach --target <project> --apply command from a trusted contribution source; "
                    "do not init, update, or rollback"
                )
            elif exc.code == "HV2-PRODUCT-STATE-INTERRUPTED":
                classification = "partial"
                next_action = exc.message
            elif exc.code == "HV2-PRODUCT-STAGING" or (
                exc.code == "HV2-PRODUCT-IMMUTABLE-CONTRADICTION" and str(self.staging) in exc.message
            ):
                next_action = (
                    "stop and confirm there is no active writer; follow docs/OPERATIONS.md product-managed scratch "
                    "recovery for only the reported child, then retry"
                )
            elif exc.code == "HV2-PRODUCT-IMMUTABLE-CONTRADICTION" and str(self.detach_receipt_path) in exc.message:
                next_action = "do not delete the differing detach receipt; stop and report the contradiction"
            return {
                "classification": classification,
                "error_code": exc.code,
                "message": exc.message,
                "next_action": next_action,
                "product_root": PRODUCT_ROOT_NAME,
            }

    def doctor(self) -> dict[str, Any]:
        status = self.status()
        git_path = shutil.which("git")
        git_result = None
        if git_path is not None:
            result = subprocess.run([git_path, "--version"], text=True, capture_output=True, check=False)
            git_result = {"exit_code": result.returncode, "version": result.stdout.strip() if result.returncode == 0 else None}
        runtime = {
            "implementation": sys.implementation.name,
            "version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        }
        classification = status["classification"]
        if classification == "pass" and (runtime["implementation"] != "cpython" or runtime["version"] != "3.14.6"):
            classification = "unsupported"
        if classification == "pass" and (git_result is None or git_result["exit_code"] != 0):
            classification = "unsupported"
        return {
            "classification": classification,
            "git": git_result,
            "network_required": False,
            "runtime": runtime,
            "status": status,
            "trust_boundary": "trusted-local-os-account-logical-actor-declarations",
        }

    def init(self, source: Path, *, apply: bool, inject_at: str | None = None) -> dict[str, Any]:
        candidate = _candidate(source)
        if candidate["source"] == self.target_root:
            raise ContractError("HV2-PRODUCT-SOURCE-TARGET", str(self.target_root))
        if self.detach_receipt_path.exists() or self.detach_receipt_path.is_symlink():
            if self.root.exists() and self.active_path.exists() and self.plan_path.exists():
                self._verify_existing_detach_receipt(self._load_active(), self._load_plan())
            raise ContractError("HV2-PRODUCT-ATTACH-REQUIRED", "detach receipt is terminal for init")
        if self.root.exists() and self.active_path.exists():
            active = self._load_active()
            if active["release_ref"] == candidate["release_ref"]:
                return {"classification": "pass", "operation": "init", "result": "already-initialized", "status": self._strict_status()}
            raise ContractError("HV2-PRODUCT-ALREADY-INITIALIZED", "use update")
        if not self.root.exists() and (
            (self.target_root / ".harness-v2").exists() or (self.target_root / ".harness-v2-intents").exists()
        ):
            raise ContractError("HV2-PRODUCT-ATTACH-REQUIRED", "existing authority home; D1 init does not infer attach")
        if self.launcher_path.exists() or self.launcher_path.is_symlink():
            if self.launcher_path.is_symlink() or not self.launcher_path.is_file() or self.launcher_path.read_bytes() != candidate["payload"]["hv2"]:
                raise ContractError("HV2-PRODUCT-COLLISION", "hv2")
        preview = {
            "classification": "preview",
            "mutation": 0,
            "operation": "init",
            "release_ref": candidate["release_ref"],
            "target": str(self.target_root),
        }
        if not apply:
            return preview
        release_ref = self._materialize_release(candidate)
        if inject_at == "after-release":
            raise InjectedCrash(inject_at)
        plan = self._init_plan(release_ref)
        if inject_at == "after-plan":
            raise InjectedCrash(inject_at)
        self._ensure_state(plan)
        if inject_at == "after-state":
            raise InjectedCrash(inject_at)
        self._ensure_intent_home(plan)
        if inject_at == "after-intent":
            raise InjectedCrash(inject_at)
        self._write_launcher(release_ref)
        if inject_at == "after-launcher":
            raise InjectedCrash(inject_at)
        receipt_ref = self._receipt(
            f"init-{release_ref['id'].removeprefix('product-release-')}",
            {
                "from_release_ref": None,
                "operation": "init",
                "plain_continuation": True,
                "to_release_ref": release_ref,
            },
        )
        self._switch(release_ref, None, receipt_ref)
        if inject_at == "after-switch":
            raise InjectedCrash(inject_at)
        return {"classification": "pass", "operation": "init", "release_ref": release_ref, "status": self._strict_status()}

    @staticmethod
    def _entry_map(release: Path) -> dict[str, dict[str, Any]]:
        inventory = load_json(release / "inventory.json", require_canonical=True)
        return {entry["path"]: entry for entry in inventory["entries"]}

    def update(self, source: Path, *, apply: bool, inject_at: str | None = None) -> dict[str, Any]:
        self._strict_status()
        active = self._load_active()
        self._verify_launcher(active["release_ref"])
        candidate = _candidate(source)
        if candidate["release_ref"] == active["release_ref"]:
            return {"classification": "pass", "mutation": 0, "operation": "update", "result": "no-change"}
        current_entries = self._entry_map(self._release_path(active["release_ref"]))
        candidate_entries = {entry["path"]: entry for entry in candidate["inventory"]["entries"]}
        changes = [path for path in MANAGED_PATHS if current_entries[path]["sha256"] != candidate_entries[path]["sha256"]]
        if current_entries["hv2"]["sha256"] != candidate_entries["hv2"]["sha256"]:
            raise ContractError("HV2-PRODUCT-LAUNCHER-CHANGE", "D1 launcher migration requires a separate gate")
        preview = {
            "changes": changes,
            "classification": "preview",
            "from_release_ref": active["release_ref"],
            "mutation": 0,
            "operation": "update",
            "to_release_ref": candidate["release_ref"],
        }
        if not apply:
            return preview
        release_ref = self._materialize_release(candidate)
        if inject_at == "after-release":
            raise InjectedCrash(inject_at)
        receipt_ref = self._receipt(
            f"update-{active['release_ref']['id'][-12:]}-{release_ref['id'][-12:]}",
            {
                "changes": changes,
                "from_release_ref": active["release_ref"],
                "operation": "update",
                "plain_continuation": True,
                "to_release_ref": release_ref,
            },
        )
        if inject_at == "after-receipt":
            raise InjectedCrash(inject_at)
        self._switch(release_ref, active["release_ref"], receipt_ref)
        if inject_at == "after-switch":
            raise InjectedCrash(inject_at)
        post_status = self.status()
        return {
            "classification": post_status["classification"],
            "mutation": 1,
            "operation": "update",
            "prior_release_ref": active["release_ref"],
            "release_ref": release_ref,
            "result": "committed",
            "status": post_status,
        }

    def rollback(self, to_release_id: str | None, *, apply: bool, inject_at: str | None = None) -> dict[str, Any]:
        self._strict_status()
        active = self._load_active()
        self._verify_launcher(active["release_ref"])
        if to_release_id is None:
            if active["prior_release_ref"] is None:
                raise ContractError("HV2-PRODUCT-NO-ROLLBACK", active["release_ref"]["id"])
            target_ref = active["prior_release_ref"]
        else:
            if RELEASE_ID_PATTERN.fullmatch(to_release_id) is None:
                raise ContractError("HV2-PRODUCT-ROLLBACK-ID", to_release_id)
            target_ref = _verify_release(self.releases / to_release_id)
        if target_ref == active["release_ref"]:
            return {"classification": "pass", "mutation": 0, "operation": "rollback", "result": "already-active"}
        current_launcher = self._entry_map(self._release_path(active["release_ref"]))["hv2"]["sha256"]
        target_launcher = self._entry_map(self._release_path(target_ref))["hv2"]["sha256"]
        if current_launcher != target_launcher:
            raise ContractError("HV2-PRODUCT-LAUNCHER-CHANGE", "rollback launcher mismatch")
        preview = {
            "classification": "preview",
            "from_release_ref": active["release_ref"],
            "mutation": 0,
            "operation": "rollback",
            "to_release_ref": target_ref,
        }
        if not apply:
            return preview
        receipt_ref = self._receipt(
            f"rollback-{active['release_ref']['id'][-12:]}-{target_ref['id'][-12:]}",
            {
                "from_release_ref": active["release_ref"],
                "operation": "rollback",
                "plain_continuation": True,
                "to_release_ref": target_ref,
            },
        )
        if inject_at == "after-receipt":
            raise InjectedCrash(inject_at)
        self._switch(target_ref, active["release_ref"], receipt_ref)
        if inject_at == "after-switch":
            raise InjectedCrash(inject_at)
        post_status = self.status()
        return {
            "classification": post_status["classification"],
            "mutation": 1,
            "operation": "rollback",
            "prior_release_ref": active["release_ref"],
            "release_ref": target_ref,
            "result": "committed",
            "status": post_status,
        }

    def _validate_detach_tree(self) -> None:
        required = {ACTIVE_NAME, INIT_PLAN_NAME, "receipts", "releases"}
        allowed = required | {"staging"}
        actual = {path.name for path in self.root.iterdir()}
        missing = required - actual
        unexpected = actual - allowed
        if missing or unexpected:
            raise ContractError("HV2-PRODUCT-DETACH-TREE", repr(sorted(missing | unexpected)))
        if self.staging.exists() or self.staging.is_symlink():
            if self.staging.is_symlink() or not self.staging.is_dir():
                raise ContractError("HV2-PRODUCT-DETACH-STAGING", str(self.staging))
            staging_entries = sorted(self.staging.iterdir(), key=lambda path: path.name)
            if staging_entries:
                raise ContractError("HV2-PRODUCT-DETACH-STAGING", str(staging_entries[0]))
        for release in self.releases.iterdir():
            _verify_release(release)
        for receipt in self.receipts.iterdir():
            if receipt.is_symlink() or not receipt.is_file():
                raise ContractError("HV2-PRODUCT-DETACH-RECEIPT", str(receipt))
            load_json(receipt, require_canonical=True)
        self._load_plan()
        self._load_active()

    def _detach_receipt(
        self, active: dict[str, Any], plan: dict[str, Any], existing_detach: object | None
    ) -> dict[str, Any]:
        if existing_detach is not None and (
            not isinstance(existing_detach, dict)
            or not isinstance(existing_detach.get("observed_at"), str)
            or not existing_detach["observed_at"]
        ):
            raise ContractError("HV2-PRODUCT-DETACH-RECEIPT", str(self.detach_receipt_path))
        return {
            "active_release_ref": active["release_ref"],
            "documentation": {
                "availability_after_detach": "not-guaranteed",
                "release_ref": active["release_ref"],
                "required_relative_paths": list(DETACH_DOCUMENT_PATHS),
            },
            "instructions": list(DETACH_INSTRUCTIONS),
            "intent_authority_home_id": plan["intent_authority_home_id"],
            "item_id": plan["item_id"],
            "observed_at": existing_detach.get("observed_at") if isinstance(existing_detach, dict) else _now(),
            "record_type": "product-detach-receipt",
            "removed": ["hv2", f"{PRODUCT_ROOT_NAME}/"],
            "schema_version": PRODUCT_SCHEMA_VERSION,
            "state_authority_home_id": plan["state_authority_home_id"],
        }

    def _load_detach_receipt(self) -> dict[str, Any]:
        _require_lstat_type(self.detach_receipt_path, directory=False, code="HV2-PRODUCT-DETACH-RECEIPT")
        receipt = _exact_dict(
            load_json(self.detach_receipt_path, require_canonical=True),
            {
                "active_release_ref",
                "documentation",
                "instructions",
                "intent_authority_home_id",
                "item_id",
                "observed_at",
                "record_type",
                "removed",
                "schema_version",
                "state_authority_home_id",
            },
            "HV2-PRODUCT-DETACH-RECEIPT",
        )
        release_ref = _validate_ref(receipt["active_release_ref"], "HV2-PRODUCT-DETACH-RECEIPT")
        documentation = _exact_dict(
            receipt["documentation"],
            {"availability_after_detach", "release_ref", "required_relative_paths"},
            "HV2-PRODUCT-DETACH-RECEIPT",
        )
        documentation_ref = _validate_ref(documentation["release_ref"], "HV2-PRODUCT-DETACH-RECEIPT")
        if (
            RELEASE_ID_PATTERN.fullmatch(release_ref["id"]) is None
            or documentation_ref != release_ref
            or documentation["availability_after_detach"] != "not-guaranteed"
            or documentation["required_relative_paths"] != list(DETACH_DOCUMENT_PATHS)
            or receipt["instructions"] != list(DETACH_INSTRUCTIONS)
            or receipt["removed"] != ["hv2", f"{PRODUCT_ROOT_NAME}/"]
            or receipt["record_type"] != "product-detach-receipt"
            or type(receipt["schema_version"]) is not int
            or receipt["schema_version"] != PRODUCT_SCHEMA_VERSION
        ):
            raise ContractError("HV2-PRODUCT-DETACH-RECEIPT", str(self.detach_receipt_path))
        for key in ("intent_authority_home_id", "item_id", "observed_at", "state_authority_home_id"):
            if not isinstance(receipt[key], str) or not receipt[key]:
                raise ContractError("HV2-PRODUCT-DETACH-RECEIPT", str(self.detach_receipt_path))
        receipt["active_release_ref"] = release_ref
        receipt["documentation"]["release_ref"] = documentation_ref
        return receipt

    def _validate_interrupted_detach_tree(self) -> None:
        allowed = {ACTIVE_NAME, INIT_PLAN_NAME, "receipts", "releases", "staging"}
        unexpected = {path.name for path in self.root.iterdir()} - allowed
        if unexpected:
            raise ContractError("HV2-PRODUCT-DETACH-TREE", repr(sorted(unexpected)))

    def _validate_interrupted_detach_receipt(self, receipt: dict[str, Any]) -> None:
        code = "HV2-PRODUCT-DETACH-RECEIPT"

        _require_lstat_type(self.target_root / ".harness-v2", directory=True, code=code)
        _require_lstat_type(self.target_root / ".harness-v2-intents", directory=True, code=code)

        def require_authority_id(path: Path, expected: str) -> None:
            _require_lstat_type(path, directory=False, code=code)
            try:
                authority = load_json(path, require_canonical=True)
            except ContractError as exc:
                raise ContractError(code, str(path)) from exc
            if not isinstance(authority, dict) or authority.get("authority_home_id") != expected:
                raise ContractError(code, str(path))

        require_authority_id(
            self.target_root / ".harness-v2" / "authority.json",
            receipt["state_authority_home_id"],
        )
        require_authority_id(
            self.target_root / ".harness-v2-intents" / "authority.json",
            receipt["intent_authority_home_id"],
        )

        if self.plan_path.exists() or self.plan_path.is_symlink():
            try:
                plan = self._load_plan()
            except ContractError as exc:
                raise ContractError(code, str(self.plan_path)) from exc
            if (
                plan["item_id"] != receipt["item_id"]
                or plan["state_authority_home_id"] != receipt["state_authority_home_id"]
                or plan["intent_authority_home_id"] != receipt["intent_authority_home_id"]
                or plan["release_ref"] != receipt["active_release_ref"]
            ):
                raise ContractError(code, str(self.plan_path))

        release_path = self._release_path(receipt["active_release_ref"])
        if release_path.exists() or release_path.is_symlink():
            try:
                actual_release_ref = _verify_release(release_path)
            except ContractError as exc:
                raise ContractError(code, str(release_path)) from exc
            if actual_release_ref != receipt["active_release_ref"]:
                raise ContractError(code, str(release_path))

    def _validate_interrupted_detach_completion(self, receipt: dict[str, Any]) -> None:
        self._validate_interrupted_detach_tree()
        self._validate_interrupted_detach_receipt(receipt)
        if self.launcher_path.exists() or self.launcher_path.is_symlink():
            raise ContractError("HV2-PRODUCT-LAUNCHER-DRIFT", str(self.launcher_path))

    def _verify_existing_detach_receipt(self, active: dict[str, Any], plan: dict[str, Any]) -> None:
        if not (self.detach_receipt_path.exists() or self.detach_receipt_path.is_symlink()):
            return
        if self.detach_receipt_path.is_symlink() or not self.detach_receipt_path.is_file():
            raise ContractError("HV2-PRODUCT-DETACH-RECEIPT", str(self.detach_receipt_path))
        existing = load_json(self.detach_receipt_path, require_canonical=True)
        if existing != self._detach_receipt(active, plan, existing):
            raise ContractError("HV2-PRODUCT-IMMUTABLE-CONTRADICTION", str(self.detach_receipt_path))
        raise ContractError("HV2-PRODUCT-DETACH-INCOMPLETE", str(self.detach_receipt_path))

    def detach(self, *, apply: bool, inject_at: str | None = None) -> dict[str, Any]:
        if self.root.is_symlink() or (self.root.exists() and not self.root.is_dir()):
            raise ContractError("HV2-PRODUCT-ROOT", str(self.root))
        if not self.root.exists():
            self._load_detach_receipt()
            return {"classification": "detached", "mutation": 0, "operation": "detach", "result": "already-detached"}
        if not self.active_path.exists() and not self.active_path.is_symlink():
            detach_receipt = self._load_detach_receipt()
            self._validate_interrupted_detach_completion(detach_receipt)
            preview = {
                "classification": "preview",
                "mutation": 0,
                "operation": "detach",
                "preserved": [".harness-v2/", ".harness-v2-intents/"],
                "release_ref": detach_receipt["active_release_ref"],
                "removed": ["hv2", f"{PRODUCT_ROOT_NAME}/"],
            }
            if not apply:
                return preview
            shutil.rmtree(self.root)
            sync_directory(self.target_root)
            return {
                "classification": "detached",
                "detach_receipt": detach_receipt,
                "operation": "detach",
                "preserved": [".harness-v2/", ".harness-v2-intents/"],
            }
        active = self._load_active()
        plan = self._load_plan()
        existing_detach = None
        if self.detach_receipt_path.exists() or self.detach_receipt_path.is_symlink():
            if self.detach_receipt_path.is_symlink() or not self.detach_receipt_path.is_file():
                raise ContractError("HV2-PRODUCT-DETACH-RECEIPT", str(self.detach_receipt_path))
            existing_detach = load_json(self.detach_receipt_path, require_canonical=True)
        if existing_detach is None:
            self._verify_launcher(active["release_ref"])
        preview = {
            "classification": "preview",
            "mutation": 0,
            "operation": "detach",
            "preserved": [".harness-v2/", ".harness-v2-intents/"],
            "release_ref": active["release_ref"],
            "removed": ["hv2", f"{PRODUCT_ROOT_NAME}/"],
        }
        if not apply:
            return preview
        self._validate_detach_tree()
        detach_receipt = self._detach_receipt(active, plan, existing_detach)
        _write_exact_json(self.detach_receipt_path, detach_receipt)
        if inject_at == "after-receipt":
            raise InjectedCrash(inject_at)
        if self.launcher_path.exists() or self.launcher_path.is_symlink():
            self._verify_launcher(active["release_ref"])
            self.launcher_path.unlink()
            sync_directory(self.target_root)
        if inject_at == "after-launcher":
            raise InjectedCrash(inject_at)
        shutil.rmtree(self.root)
        sync_directory(self.target_root)
        return {
            "classification": "detached",
            "detach_receipt": detach_receipt,
            "operation": "detach",
            "preserved": [".harness-v2/", ".harness-v2-intents/"],
        }
