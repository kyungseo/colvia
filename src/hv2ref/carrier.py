from __future__ import annotations

import os
import re
import shutil
import unicodedata
from pathlib import Path, PurePosixPath
from typing import Any

from .errors import ContractError
from .jsonio import canonical_json_bytes, load_json, sha256_bytes, sha256_file, sync_directory, write_new_bytes


RELEASE_KEYS = {
    "authority_home_id",
    "created_at",
    "inventory_ref",
    "record_type",
    "release_id",
    "schema_generation",
}
INVENTORY_KEYS = {"entries", "inventory_id", "record_type", "schema_generation"}
ENTRY_KEYS = {"path", "sha256", "size_bytes"}
PAYLOAD_PATH = "payload/generation-1-contract.md"


def _safe_relative_path(value: str) -> PurePosixPath:
    if not isinstance(value, str) or unicodedata.normalize("NFC", value) != value:
        raise ContractError("HV2-CARRIER-UNSAFE-PATH", repr(value))
    path = PurePosixPath(value)
    if (
        path.is_absolute()
        or not path.parts
        or any(part in {"", ".", ".."} for part in path.parts)
        or str(path) != value
    ):
        raise ContractError("HV2-CARRIER-UNSAFE-PATH", value)
    return path


def _validate_seal(seal: dict[str, Any]) -> None:
    required = {"authority_home_id", "created_at", "inventory_id", "release_id"}
    allowed = required | {"item_id", "run_id", "target_repository_id"}
    if not isinstance(seal, dict) or not required <= set(seal) or not set(seal) <= allowed:
        raise ContractError("HV2-CARRIER-SEAL", repr(sorted(seal) if isinstance(seal, dict) else seal))
    for key in seal:
        if not isinstance(seal[key], str) or not seal[key]:
            raise ContractError("HV2-CARRIER-SEAL", key)


def build_release(source: Path, output: Path, seal: dict[str, Any]) -> dict[str, Any]:
    _validate_seal(seal)
    if output.exists() or output.is_symlink():
        raise ContractError("HV2-CARRIER-EXISTS", str(output))
    if not source.is_file() or source.is_symlink():
        raise ContractError("HV2-CARRIER-SOURCE", str(source))
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.parent / f".{output.name}.hv2-build"
    if temporary.exists() or temporary.is_symlink():
        raise ContractError("HV2-CARRIER-TEMP-RESIDUE", str(temporary))
    temporary.mkdir()
    try:
        payload = temporary / PAYLOAD_PATH
        source_bytes = source.read_bytes()
        write_new_bytes(payload, source_bytes)
        entry = {"path": PAYLOAD_PATH, "sha256": sha256_bytes(source_bytes), "size_bytes": len(source_bytes)}
        inventory = {
            "entries": [entry],
            "inventory_id": seal["inventory_id"],
            "record_type": "inventory",
            "schema_generation": 1,
        }
        inventory_bytes = canonical_json_bytes(inventory)
        write_new_bytes(temporary / "inventory.json", inventory_bytes)
        release = {
            "authority_home_id": seal["authority_home_id"],
            "created_at": seal["created_at"],
            "inventory_ref": {"id": seal["inventory_id"], "sha256": sha256_bytes(inventory_bytes)},
            "record_type": "release",
            "release_id": seal["release_id"],
            "schema_generation": 1,
        }
        write_new_bytes(temporary / "release.json", canonical_json_bytes(release))
        result = verify_release(temporary)
        os.replace(temporary, output)
        sync_directory(output.parent)
        result["source_sha256"] = sha256_bytes(source_bytes)
        return result
    except Exception:
        if temporary.exists() and not temporary.is_symlink():
            shutil.rmtree(temporary)
            sync_directory(output.parent)
        raise


def verify_release(root: Path) -> dict[str, Any]:
    if root.is_symlink() or not root.is_dir():
        raise ContractError("HV2-CARRIER-ROOT", str(root))
    if {path.name for path in root.iterdir()} != {"inventory.json", "payload", "release.json"}:
        raise ContractError("HV2-CARRIER-ROOT-COVERAGE", str(root))
    release_path = root / "release.json"
    inventory_path = root / "inventory.json"
    payload_root = root / "payload"
    if release_path.is_symlink() or not release_path.is_file():
        raise ContractError("HV2-CARRIER-ROOT-MEMBER-TYPE", "release.json")
    if inventory_path.is_symlink() or not inventory_path.is_file():
        raise ContractError("HV2-CARRIER-ROOT-MEMBER-TYPE", "inventory.json")
    if payload_root.is_symlink() or not payload_root.is_dir():
        raise ContractError("HV2-CARRIER-ROOT-MEMBER-TYPE", "payload")
    release = load_json(release_path, require_canonical=True)
    inventory = load_json(inventory_path, require_canonical=True)
    if (
        set(release) != RELEASE_KEYS
        or release.get("record_type") != "release"
        or type(release.get("schema_generation")) is not int
        or release.get("schema_generation") != 1
    ):
        raise ContractError("HV2-CARRIER-RELEASE-SCHEMA", str(sorted(release)))
    if (
        set(inventory) != INVENTORY_KEYS
        or inventory.get("record_type") != "inventory"
        or type(inventory.get("schema_generation")) is not int
        or inventory.get("schema_generation") != 1
    ):
        raise ContractError("HV2-CARRIER-INVENTORY-SCHEMA", str(sorted(inventory)))
    ref = release.get("inventory_ref")
    if not isinstance(ref, dict) or set(ref) != {"id", "sha256"}:
        raise ContractError("HV2-CARRIER-INVENTORY-REF", repr(ref))
    if not isinstance(ref["id"], str) or not isinstance(ref["sha256"], str) or not re.fullmatch(r"[0-9a-f]{64}", ref["sha256"]):
        raise ContractError("HV2-CARRIER-INVENTORY-REF", repr(ref))
    for key in ("authority_home_id", "created_at", "release_id"):
        if not isinstance(release[key], str) or not release[key]:
            raise ContractError("HV2-CARRIER-RELEASE-TYPE", key)
    if not isinstance(inventory["inventory_id"], str) or not inventory["inventory_id"]:
        raise ContractError("HV2-CARRIER-INVENTORY-TYPE", "inventory_id")
    entries = inventory.get("entries")
    if not isinstance(entries, list) or not entries:
        raise ContractError("HV2-CARRIER-EMPTY", "entries")
    paths: list[str] = []
    folded = set()
    for entry in entries:
        if not isinstance(entry, dict) or set(entry) != ENTRY_KEYS:
            raise ContractError("HV2-CARRIER-ENTRY-SCHEMA", repr(entry))
        if (
            not isinstance(entry["sha256"], str)
            or not re.fullmatch(r"[0-9a-f]{64}", entry["sha256"])
            or type(entry["size_bytes"]) is not int
            or entry["size_bytes"] < 0
        ):
            raise ContractError("HV2-CARRIER-ENTRY-TYPE", repr(entry))
        relative = _safe_relative_path(entry["path"])
        if relative.parts[0] != "payload":
            raise ContractError("HV2-CARRIER-PAYLOAD-SCOPE", str(relative))
        folded_path = str(relative).casefold()
        if folded_path in folded:
            raise ContractError("HV2-CARRIER-PATH-COLLISION", str(relative))
        folded.add(folded_path)
        paths.append(str(relative))
    if paths != sorted(paths, key=lambda item: item.encode("utf-8")) or len(paths) != len(set(paths)):
        raise ContractError("HV2-CARRIER-ENTRY-ORDER", repr(paths))
    actual_files: list[str] = []
    for directory, dirnames, filenames in os.walk(payload_root, followlinks=False):
        dirnames.sort()
        for name in dirnames:
            child = Path(directory) / name
            if child.is_symlink() or not child.is_dir():
                raise ContractError("HV2-CARRIER-ENTRY-TYPE", str(child))
        if Path(directory) != payload_root and not dirnames and not filenames:
            raise ContractError("HV2-CARRIER-EMPTY-DIRECTORY", Path(directory).relative_to(root).as_posix())
        for name in sorted(filenames):
            file_path = Path(directory) / name
            if file_path.is_symlink() or not file_path.is_file():
                raise ContractError("HV2-CARRIER-ENTRY-TYPE", str(file_path))
            actual_files.append(file_path.relative_to(root).as_posix())
    if actual_files != paths:
        raise ContractError("HV2-CARRIER-INVENTORY-COVERAGE", repr(actual_files))
    for entry in entries:
        target = root.joinpath(*PurePosixPath(entry["path"]).parts)
        data = target.read_bytes()
        if len(data) != entry["size_bytes"] or sha256_bytes(data) != entry["sha256"]:
            raise ContractError("HV2-CARRIER-ENTRY-DIGEST", entry["path"])
    if ref["id"] != inventory["inventory_id"] or ref["sha256"] != sha256_file(inventory_path):
        raise ContractError("HV2-CARRIER-INVENTORY-DIGEST", ref["id"])
    return {
        "authority_home_id": release["authority_home_id"],
        "carrier_sha256": sha256_file(release_path),
        "inventory_id": inventory["inventory_id"],
        "inventory_sha256": sha256_file(inventory_path),
        "payload_entries": entries,
        "release_id": release["release_id"],
    }
