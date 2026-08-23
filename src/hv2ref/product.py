from __future__ import annotations

import os
import re
import shutil
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

    def _verify_state(self, plan: dict[str, Any]) -> None:
        result = StateStore(self.target_root).verify(plan["item_id"])
        if result.get("authority_home_id") != plan["state_authority_home_id"] or result.get("classification") != "pass":
            raise ContractError("HV2-PRODUCT-STATE-BINDING", repr(result))

    def _ensure_intent_home(self, plan: dict[str, Any]) -> None:
        intent_root = self.target_root / ".harness-v2-intents"
        if not intent_root.exists() and not intent_root.is_symlink():
            IntentStore(self.target_root).initialize(plan["intent_authority_home_id"], plan["observed_at"])
        self._verify_intent_home(plan)

    def _verify_intent_home(self, plan: dict[str, Any]) -> None:
        intent_root = self.target_root / ".harness-v2-intents"
        authority_path = intent_root / "authority.json"
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
            if self.detach_receipt_path.exists() and not self.detach_receipt_path.is_symlink():
                receipt = load_json(self.detach_receipt_path, require_canonical=True)
                return {
                    "classification": "detached",
                    "detach_receipt": receipt,
                    "next_action": "continue from plain project-owned state or initialize a new product binding",
                    "product_root": PRODUCT_ROOT_NAME,
                }
            return {
                "classification": "uninitialized",
                "next_action": "run hv2 init --target <project> --apply from the contribution source",
                "product_root": PRODUCT_ROOT_NAME,
            }
        if not self.active_path.exists():
            return {
                "classification": "partial",
                "next_action": "repeat the exact init command from the contribution source",
                "product_root": PRODUCT_ROOT_NAME,
            }
        expected_root_entries = {ACTIVE_NAME, INIT_PLAN_NAME, "receipts", "releases", "staging"}
        actual_root_entries = {path.name for path in self.root.iterdir()}
        if actual_root_entries != expected_root_entries:
            raise ContractError("HV2-PRODUCT-ROOT-TREE", repr(sorted(actual_root_entries ^ expected_root_entries)))
        if any(self.staging.iterdir()):
            raise ContractError("HV2-PRODUCT-STAGING", str(self.staging))
        active = self._load_active()
        plan = self._load_plan()
        if active["release_ref"] != plan["release_ref"] and active["prior_release_ref"] is None:
            raise ContractError("HV2-PRODUCT-INIT-PLAN", "active lineage")
        self._verify_launcher(active["release_ref"])
        self._verify_state(plan)
        self._verify_intent_home(plan)
        capabilities_path = self._release_path(active["release_ref"]) / "PRODUCT-CAPABILITIES.json"
        capabilities = load_json(capabilities_path, require_canonical=True)
        if not isinstance(capabilities, dict):
            raise ContractError("HV2-PRODUCT-CAPABILITIES", str(capabilities_path))
        state = StateStore(self.target_root).verify(plan["item_id"])
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
            return {
                "classification": "degraded",
                "error_code": exc.code,
                "message": exc.message,
                "next_action": "run doctor from a trusted source checkout; do not update or detach until the contradiction is resolved",
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
        return {"classification": "pass", "operation": "update", "release_ref": release_ref, "status": self._strict_status()}

    def rollback(self, to_release_id: str | None, *, apply: bool, inject_at: str | None = None) -> dict[str, Any]:
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
        return {"classification": "pass", "operation": "rollback", "release_ref": target_ref, "status": self._strict_status()}

    def _validate_detach_tree(self) -> None:
        allowed = {ACTIVE_NAME, INIT_PLAN_NAME, "receipts", "releases", "staging"}
        actual = {path.name for path in self.root.iterdir()}
        if actual != allowed:
            raise ContractError("HV2-PRODUCT-DETACH-TREE", repr(sorted(actual ^ allowed)))
        if any(self.staging.iterdir()):
            raise ContractError("HV2-PRODUCT-DETACH-STAGING", str(self.staging))
        for release in self.releases.iterdir():
            _verify_release(release)
        for receipt in self.receipts.iterdir():
            if receipt.is_symlink() or not receipt.is_file():
                raise ContractError("HV2-PRODUCT-DETACH-RECEIPT", str(receipt))
            load_json(receipt, require_canonical=True)
        self._load_plan()
        self._load_active()

    def detach(self, *, apply: bool, inject_at: str | None = None) -> dict[str, Any]:
        if not self.root.exists() and self.detach_receipt_path.exists():
            return {"classification": "detached", "mutation": 0, "operation": "detach", "result": "already-detached"}
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
        detach_receipt = {
            "active_release_ref": active["release_ref"],
            "documentation": {
                "availability_after_detach": "not-guaranteed",
                "release_ref": active["release_ref"],
                "required_relative_paths": list(DETACH_DOCUMENT_PATHS),
            },
            "instructions": [
                "Project-owned state remains in .harness-v2/.",
                "Accepted intent history remains in .harness-v2-intents/.",
                "Product-managed documentation is removed; preserve the named release documents before detach if offline guidance is required.",
                "No path, timestamp, or newest-file heuristic selects authority.",
                "Reinitialize tooling only through an explicit new product binding.",
            ],
            "intent_authority_home_id": plan["intent_authority_home_id"],
            "item_id": plan["item_id"],
            "observed_at": existing_detach.get("observed_at") if isinstance(existing_detach, dict) else _now(),
            "record_type": "product-detach-receipt",
            "removed": ["hv2", f"{PRODUCT_ROOT_NAME}/"],
            "schema_version": PRODUCT_SCHEMA_VERSION,
            "state_authority_home_id": plan["state_authority_home_id"],
        }
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
