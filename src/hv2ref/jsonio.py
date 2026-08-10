from __future__ import annotations

import errno
import fcntl
import hashlib
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any

from .errors import ContractError


MAX_JSON_BYTES = 4 * 1024 * 1024
MAX_JSON_DEPTH = 128
MAX_INTEGER_DIGITS = 1024


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_json_bytes(value: Any) -> bytes:
    try:
        text = json.dumps(value, allow_nan=False, ensure_ascii=False, indent=2, sort_keys=True)
        return (text + "\n").encode("utf-8")
    except (RecursionError, UnicodeEncodeError, ValueError) as exc:
        raise ContractError("HV2-JSON-EMISSION", type(exc).__name__) from exc


def _reject_duplicate_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ContractError("HV2-JSON-DUPLICATE-KEY", key)
        result[key] = value
    return result


def decode_json_bytes(data: bytes, *, require_canonical: bool = False) -> Any:
    if len(data) > MAX_JSON_BYTES:
        raise ContractError("HV2-JSON-LIMIT", f"bytes:{len(data)}")
    if data.startswith(b"\xef\xbb\xbf"):
        raise ContractError("HV2-JSON-BOM", "UTF-8 BOM is forbidden")
    if not data.endswith(b"\n") or data.endswith(b"\n\n"):
        raise ContractError("HV2-JSON-EOF", "exactly one EOF LF is required")
    if b"\r" in data:
        raise ContractError("HV2-JSON-CR", "CR bytes are forbidden")
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ContractError("HV2-JSON-UTF8", str(exc)) from exc
    try:
        def bounded_int(value: str) -> int:
            if len(value.lstrip("-")) > MAX_INTEGER_DIGITS:
                raise ContractError("HV2-JSON-LIMIT", "integer-digits")
            return int(value)

        value = json.loads(
            text,
            object_pairs_hook=_reject_duplicate_pairs,
            parse_int=bounded_int,
            parse_constant=lambda value: (_ for _ in ()).throw(ContractError("HV2-JSON-NONFINITE", value)),
        )
    except ContractError:
        raise
    except json.JSONDecodeError as exc:
        raise ContractError("HV2-JSON-SYNTAX", str(exc)) from exc
    except (RecursionError, UnicodeEncodeError, ValueError) as exc:
        raise ContractError("HV2-JSON-LIMIT", type(exc).__name__) from exc
    stack = [(value, 1)]
    while stack:
        current, depth = stack.pop()
        if depth > MAX_JSON_DEPTH:
            raise ContractError("HV2-JSON-LIMIT", f"depth:{depth}")
        if isinstance(current, dict):
            stack.extend((child, depth + 1) for child in current.values())
        elif isinstance(current, list):
            stack.extend((child, depth + 1) for child in current)
    if require_canonical and canonical_json_bytes(value) != data:
        raise ContractError("HV2-JSON-NONCANONICAL", "stored bytes do not match generation 1 emission")
    return value


def load_json(path: Path, *, require_canonical: bool = False) -> Any:
    return decode_json_bytes(path.read_bytes(), require_canonical=require_canonical)


def _sync_fd(fd: int) -> dict[str, str]:
    os.fsync(fd)
    result = {"fsync": "pass", "fullfsync": "not-applicable"}
    if sys.platform == "darwin":
        fullfsync = getattr(fcntl, "F_FULLFSYNC", None)
        if fullfsync is None:
            result["fullfsync"] = "unavailable"
        else:
            try:
                fcntl.fcntl(fd, fullfsync)
                result["fullfsync"] = "pass"
            except OSError as exc:
                result["fullfsync"] = f"error:{exc.errno}"
    return result


def sync_directory(path: Path) -> str:
    flags = os.O_RDONLY
    if hasattr(os, "O_DIRECTORY"):
        flags |= os.O_DIRECTORY
    fd = os.open(path, flags)
    try:
        os.fsync(fd)
        return "pass"
    except OSError as exc:
        if exc.errno in {errno.EINVAL, errno.ENOTSUP}:
            return f"unavailable:{exc.errno}"
        raise
    finally:
        os.close(fd)


def _ensure_parent(path: Path) -> None:
    missing: list[Path] = []
    current = path.parent
    while not current.exists():
        missing.append(current)
        current = current.parent
    if current.is_symlink() or not current.is_dir():
        raise ContractError("HV2-PARENT-TYPE", str(current))
    for directory in reversed(missing):
        try:
            directory.mkdir()
        except FileExistsError as exc:
            if directory.is_symlink() or not directory.is_dir():
                raise ContractError("HV2-PARENT-TYPE", str(directory)) from exc
        if directory.is_symlink() or not directory.is_dir():
            raise ContractError("HV2-PARENT-TYPE", str(directory))
        sync_directory(directory.parent)
        sync_directory(directory)


def write_new_bytes(path: Path, data: bytes) -> dict[str, str]:
    _ensure_parent(path)
    if path.exists() or path.is_symlink():
        raise ContractError("HV2-IMMUTABLE-EXISTS", str(path))
    try:
        with path.open("xb") as handle:
            handle.write(data)
            handle.flush()
            result = _sync_fd(handle.fileno())
    except FileExistsError as exc:
        raise ContractError("HV2-IMMUTABLE-EXISTS", str(path)) from exc
    result["directory_fsync"] = sync_directory(path.parent)
    return result


def write_new_json(path: Path, value: Any) -> dict[str, str]:
    return write_new_bytes(path, canonical_json_bytes(value))


def replace_bytes(path: Path, data: bytes) -> dict[str, str]:
    _ensure_parent(path)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.hv2-tmp-", dir=path.parent)
    tmp = Path(tmp_name)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            result = _sync_fd(handle.fileno())
        os.replace(tmp, path)
        result["directory_fsync"] = sync_directory(path.parent)
        return result
    finally:
        if tmp.exists():
            tmp.unlink()


def replace_json(path: Path, value: Any) -> dict[str, str]:
    return replace_bytes(path, canonical_json_bytes(value))


def durability_probe(root: Path) -> dict[str, str]:
    probe = root / ".hv2-durability-probe"
    result = write_new_bytes(probe, b"harness-v2-durability-probe\n")
    probe.unlink()
    result["cleanup_directory_fsync"] = sync_directory(root)
    result["platform"] = sys.platform
    result["power_loss_claim"] = "not-claimed"
    result["scope"] = "same-filesystem-process-ordering"
    return result
