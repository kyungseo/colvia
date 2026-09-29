"""New-format workspace root primitives. Not yet an installed product entry.

Record/lifecycle verification must follow root inspection before user mutation.
This module never interprets or converts old-generation authority.
"""
from __future__ import annotations

from contextlib import contextmanager
import hashlib
import os
from pathlib import Path
import re
import stat
import sys
import sysconfig
import subprocess
import threading
from typing import Any

from .errors import ContractError, InjectedCrash
from .jsonio import canonical_json_bytes, exclusive_file_lock, load_json, sync_directory, write_new_bytes

ROOT_NAME = ".hrn"
IGNORE_BYTES = b"staging/\nlocks/\n"
ROOT_MEMBERS = frozenset({"format.json", ".gitignore", "detached.json", "product", "intents", "work", "staging", "locks"})
FORMAT_KEYS = {"record_type", "format_version", "authority_home_id", "created_at", "lineage"}
PLAN_KEYS = {"record_type", "schema_version", "operation_id", "action", "target_fingerprint", "authority_home_id", "expected_binding_ref", "candidate_release", "format_sha256", "truth_refs", "remove", "preserve", "created_at"}
ID = re.compile(r"[a-zA-Z0-9][a-zA-Z0-9_-]{0,95}\Z")
SHA = re.compile(r"[0-9a-f]{64}\Z")


SUPPORTED_PYTHON_VERSIONS = ((3, 14, 6), (3, 14, 7))
SUPPORTED_PYTHON_STRINGS = tuple(".".join(map(str, version)) for version in SUPPORTED_PYTHON_VERSIONS)
SUPPORTED_PYTHON_TEXT = ", ".join(SUPPORTED_PYTHON_STRINGS)


def runtime_supported() -> bool:
    """Qualified final, GIL-enabled CPython builds; not interpreter authentication."""
    return (sys.implementation.name == "cpython"
            and sys.version_info[:3] in SUPPORTED_PYTHON_VERSIONS
            and getattr(sys.version_info, "releaselevel", None) == "final"
            and not sysconfig.get_config_var("Py_GIL_DISABLED"))


def require_supported_runtime() -> None:
    if not runtime_supported():
        raise ContractError("HV2-WORKSPACE-RUNTIME", f"mutation requires final GIL-enabled CPython {SUPPORTED_PYTHON_TEXT}; preserve bytes and use a supported runtime")


def _error(detail: str) -> ContractError:
    return ContractError("HV2-WORKSPACE-CONTRACT", detail)


def _exists(path: Path) -> bool:
    try:
        path.lstat()
        return True
    except FileNotFoundError:
        return False


def _require_kind(path: Path, directory: bool) -> None:
    mode = path.lstat().st_mode
    valid = stat.S_ISDIR(mode) if directory else stat.S_ISREG(mode)
    if stat.S_ISLNK(mode) or not valid:
        raise _error(f"wrong file type: {path.name}")


def _exact(value: Any, keys: set[str]) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != keys:
        raise _error("unexpected object keys")
    return value


def _text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _id(value: Any) -> bool:
    return isinstance(value, str) and ID.fullmatch(value) is not None


def _sha(value: Any) -> bool:
    return isinstance(value, str) and SHA.fullmatch(value) is not None


def _format_object(value: Any, keys: set[str]) -> dict[str, Any]:
    if not isinstance(value, dict) or keys - set(value):
        raise _error("missing nested format fields")
    if set(value) - keys:
        raise ContractError("HV2-WORKSPACE-UNKNOWN", "unknown nested format member")
    return value


def validate_format(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict) or value.get("record_type") != "workspace-format" or type(value.get("format_version")) is not int:
        raise _error("format type/version")
    if value["format_version"] != 1:
        raise ContractError("HV2-WORKSPACE-VERSION", "unsupported format version; preserve all bytes")
    if FORMAT_KEYS - set(value):
        raise _error("missing format fields")
    if set(value) - FORMAT_KEYS:
        raise ContractError("HV2-WORKSPACE-UNKNOWN", "unknown format member")
    if not _id(value["authority_home_id"]) or not _text(value["created_at"]):
        raise _error("format authority/time")
    if value["lineage"] is not None:
        lineage = _format_object(value["lineage"], {"parent", "reason"})
        parent = _format_object(lineage["parent"], {"authority_home_id", "kind", "id"})
        if not _text(lineage["reason"]) or not _id(parent["authority_home_id"]) or not _id(parent["id"]) or parent["kind"] not in {"intent", "work"}:
            raise _error("format lineage")
    return value


def safe_target(target: Path) -> Path:
    absolute = Path(os.path.abspath(target))
    try:
        for part in reversed((absolute, *absolute.parents)):
            if _exists(part):
                _require_kind(part, True)
        _require_kind(absolute, True)
        resolved = absolute.resolve(strict=True)
        if resolved == Path(resolved.anchor) or resolved == Path.home().resolve():
            raise ContractError("HV2-WORKSPACE-TARGET", "filesystem root and home are not targets")
        return resolved
    except OSError as exc:
        raise ContractError("HV2-WORKSPACE-TARGET", "target unavailable") from exc


def git_environment() -> dict[str, str]:
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update({"GIT_OPTIONAL_LOCKS": "0", "LC_ALL": "C"})
    return env


def _classify_target(target: Path, *, mutation: bool = False) -> dict[str, str]:
    target = safe_target(target)
    if any(any(p.name.casefold() == ROOT_NAME.casefold() for p in parent.iterdir()) for parent in target.parents):
        raise ContractError("HV2-WORKSPACE-TARGET", "nested workspace authority is unsupported")
    try:
        result = subprocess.run(
            ["git", "-C", str(target), "rev-parse", "--path-format=absolute", "--show-toplevel", "--absolute-git-dir", "--git-common-dir", "--show-superproject-working-tree"],
            capture_output=True, env=git_environment(), check=False,
        )
    except FileNotFoundError:
        # No Git binary is sufficient only for a tree with no ancestral Git metadata.
        if any(_exists(p / ".git") for p in (target, *target.parents)):
            raise ContractError("HV2-WORKSPACE-TARGET", "Git unavailable for repository target") from None
        return {"kind": "non-git", "target": str(target)}
    if result.returncode:
        if b"not a git repository" in result.stderr.lower() and not any(_exists(p / ".git") for p in (target, *target.parents)):
            return {"kind": "non-git", "target": str(target)}
        raise ContractError("HV2-WORKSPACE-TARGET", "Git classification failed")
    lines = os.fsdecode(result.stdout).splitlines()
    if len(lines) not in {3, 4}:
        raise ContractError("HV2-WORKSPACE-TARGET", "ambiguous Git topology")
    top, git_dir, common_dir = (Path(p).resolve(strict=True) for p in lines[:3])
    if top != target:
        kind = "subdirectory"
    elif len(lines) == 4 and lines[3]:
        kind = "submodule"
    elif git_dir != common_dir:
        kind = "linked-worktree"
    elif git_dir != target / ".git":
        kind = "separate-git-dir"
    elif any(_exists(p / ".git") for p in target.parents):
        kind = "nested-repository"
    else:
        kind = "primary"
    if mutation and kind != "primary":
        raise ContractError("HV2-WORKSPACE-TARGET", f"mutation unsupported: {kind}")
    return {"kind": kind, "target": str(target)}


def classify_target(target: Path, *, mutation: bool = False) -> dict[str, str]:
    try:
        return _classify_target(target, mutation=mutation)
    except (OSError, UnicodeError, ValueError) as exc:
        raise ContractError("HV2-WORKSPACE-TARGET", "target classification unavailable") from exc


def target_fingerprint(target: Path) -> str:
    return hashlib.sha256(os.fsencode(safe_target(target))).hexdigest()


def _file_json(path: Path) -> dict[str, Any]:
    _require_kind(path, False)
    return load_json(path, require_canonical=True)


def _root_aliases(target: Path) -> list[str]:
    return sorted(p.name for p in target.iterdir() if p.name.casefold() == ROOT_NAME.casefold() and p.name != ROOT_NAME)


def inspect_root(target: Path) -> dict[str, Any]:
    """Read-only root classification; never claims full workspace/record validity."""
    try:
        target = safe_target(target)
        root = target / ROOT_NAME
        aliases = _root_aliases(target)
        if aliases:
            return {"classification": "degraded", "paths": aliases, "record_verification": "not-run"}
        if not _exists(root):
            return {"classification": "uninitialized", "record_verification": "not-run"}
        _require_kind(root, True)
        format_path = root / "format.json"
        value = validate_format(_file_json(format_path)) if _exists(format_path) else None
        extra = sorted(p.name for p in root.iterdir() if p.name not in ROOT_MEMBERS)
        if extra:
            return {"classification": "degraded", "paths": extra, "record_verification": "not-run"}
        for name in ROOT_MEMBERS:
            path = root / name
            if _exists(path):
                _require_kind(path, name in {"product", "intents", "work", "staging", "locks"})
        product = root / "product"
        if _exists(root / "detached.json"):
            if value is None:
                raise _error("detach receipt without valid format")
            return {"classification": "detach-candidate", "authority_home_id": value["authority_home_id"], "record_verification": "required", "product_present": _exists(product)}
        plan_path = product / "init-plan.json"
        if value is None:
            try:
                plan = _file_json(plan_path)
                _validate_plan_shape(plan)
            except (ContractError, OSError):
                return {"classification": "unrecognized", "record_verification": "not-run", "paths": ["product/init-plan.json"], "recovery": "preserve bytes; explicit manual ownership decision required"}
            _bootstrap_prefix(root)
            return {"classification": "partial-candidate", "record_verification": "required"}
        if not _exists(product):
            raise _error("format without product or detach receipt")
        if not _exists(plan_path):
            raise _error("format/product without initialization plan")
        plan = _file_json(plan_path)
        _validate_plan_shape(plan)
        if plan["authority_home_id"] != value["authority_home_id"] or plan["format_sha256"] != hashlib.sha256(canonical_json_bytes(value)).hexdigest():
            raise _error("init plan/format mismatch")
        ignore = root / ".gitignore"
        if _exists(ignore) and ignore.read_bytes() != IGNORE_BYTES:
            return {"classification": "degraded", "paths": [".gitignore"], "record_verification": "not-run", "recovery": "preserve bytes; do not overwrite a torn or modified file"}
        # Empty truth directories do not survive Git transport. Absence means no
        # records, not a broken root; record writers create them under the guard.
        ready = _exists(ignore)
        return {"classification": "root-ready" if ready else "partial-candidate", "authority_home_id": value["authority_home_id"], "record_verification": "required"}
    except ContractError as exc:
        return {"classification": {"HV2-WORKSPACE-VERSION": "incompatible", "HV2-WORKSPACE-UNKNOWN": "degraded"}.get(exc.code, "integrity-failure"), "error": exc.code, "message": exc.message, "paths": ["format.json", "product/init-plan.json"], "record_verification": "not-run", "recovery": "preserve bytes; malformed or torn files require explicit manual disposition"}
    except (FileNotFoundError, NotADirectoryError):
        return {"classification": "unstable", "record_verification": "not-run"}
    except OSError:
        return {"classification": "integrity-failure", "error": "HV2-WORKSPACE-UNAVAILABLE", "record_verification": "not-run"}


def _validate_plan_shape(plan: Any) -> None:
    plan = _exact(plan, PLAN_KEYS)
    if plan["record_type"] != "lifecycle-plan" or type(plan["schema_version"]) is not int or plan["schema_version"] != 1 or plan["action"] != "init":
        raise _error("not a supported init plan")
    if not all(_id(plan[k]) for k in ("operation_id", "authority_home_id")) or not _text(plan["created_at"]) or not all(_sha(plan[k]) for k in ("target_fingerprint", "format_sha256")):
        raise _error("invalid init identity or digest")
    if plan["expected_binding_ref"] is not None or any(plan[k] != [] for k in ("truth_refs", "remove", "preserve")):
        raise _error("invalid fresh init claims")
    release = _exact(plan["candidate_release"], {"id", "sha256", "inventory_id"})
    if not _sha(release["sha256"]) or release["id"] != "product-release-" + release["sha256"][:24] or (not isinstance(release["inventory_id"], str) or release["inventory_id"] not in {"human-1", "worker-1"}):
        raise _error("invalid init release")


def _bootstrap_prefix(root: Path) -> None:
    present = {p.name for p in root.iterdir()}
    if "format.json" not in present and present != {"product"}:
        raise _error("not an exact bootstrap prefix")
    if "format.json" in present and ".gitignore" not in present and present - {"product", "format.json"}:
        raise _error("not an exact bootstrap prefix")
    if "work" in present and "intents" not in present:
        raise _error("out-of-order bootstrap directories")


def _durable_directory(path: Path) -> None:
    try:
        path.mkdir()
    except FileExistsError:
        _require_kind(path, True)
    sync_directory(path.parent)
    sync_directory(path)


def _write_exact(path: Path, data: bytes) -> None:
    if _exists(path):
        _require_kind(path, False)
        if path.read_bytes() != data:
            raise _error(f"immutable mismatch: {path.name}; preserve torn/modified bytes for explicit manual disposition")
        with path.open("rb") as handle:
            os.fsync(handle.fileno())
        sync_directory(path.parent)
        return
    write_new_bytes(path, data)


def _validate_init_plan(plan: Any, value: dict[str, Any], target: Path) -> dict[str, Any]:
    plan = _exact(plan, PLAN_KEYS)
    if plan["record_type"] != "lifecycle-plan" or type(plan["schema_version"]) is not int or plan["schema_version"] != 1 or plan["action"] != "init":
        raise _error("not a supported init plan")
    if not _id(plan["operation_id"]) or plan["authority_home_id"] != value["authority_home_id"] or not _text(plan["created_at"]):
        raise _error("init plan identity")
    if plan["target_fingerprint"] != target_fingerprint(target) or plan["format_sha256"] != hashlib.sha256(canonical_json_bytes(value)).hexdigest():
        raise _error("init plan target/format mismatch")
    if plan["expected_binding_ref"] is not None or plan["truth_refs"] != [] or plan["remove"] != [] or plan["preserve"] != []:
        raise _error("fresh init plan cannot claim existing truth")
    release = _exact(plan["candidate_release"], {"id", "sha256", "inventory_id"})
    if not _id(release["id"]) or not _sha(release["sha256"]) or (not isinstance(release["inventory_id"], str) or release["inventory_id"] not in {"human-1", "worker-1"}):
        raise _error("init plan candidate")
    if release["id"] != "product-release-" + release["sha256"][:24]:
        raise _error("init plan release identity")
    return plan


def bootstrap_root(target: Path, plan: dict[str, Any], value: dict[str, Any], *, recover: bool = False, inject_at: str | None = None) -> dict[str, Any]:
    """Publish root primitives only. Product installation must validate the candidate.

No installed entry calls this yet. Each retry is explicit and exact; detached or
unknown state is never adopted. Process crash tests do not establish power-loss safety.
"""
    require_supported_runtime()
    target = Path(classify_target(target, mutation=True)["target"])
    if _root_aliases(target):
        raise _error("case-alias of workspace root; preserve existing path")
    value = validate_format(value)
    plan = _validate_init_plan(plan, value, target)
    points = {"after-root", "after-product-dir", "after-plan", "after-format", "after-ignore", "after-intents", "after-work"}
    if inject_at is not None and inject_at not in points:
        raise _error("unknown crash point")
    root = target / ROOT_NAME
    if _exists(root):
        if not recover:
            raise _error("existing root requires explicit recovery")
        _require_kind(root, True)
        if set(p.name for p in root.iterdir()) - ROOT_MEMBERS or _exists(root / "detached.json"):
            raise _error("existing root is not this initialization")
        for name in ROOT_MEMBERS:
            member = root / name
            if _exists(member):
                _require_kind(member, name in {"product", "intents", "work", "staging", "locks"})
        product = root / "product"
        if not _exists(product / "init-plan.json"):
            raise _error("no durable ownership plan; preserve root")
        if _file_json(product / "init-plan.json") != plan:
            raise _error("different initialization plan")
        _bootstrap_prefix(root)
        # This primitive can only resume its own prefix, before product publication.
        if set(p.name for p in product.iterdir()) != {"init-plan.json"}:
            raise _error("product publication requires lifecycle recovery")
        for name in ("intents", "work", "staging", "locks"):
            member = root / name
            if _exists(member) and any(member.iterdir()):
                raise _error("nonempty root prefix requires record/lifecycle verification")
    else:
        if recover:
            raise _error("cannot recover absent root")
        root.mkdir()  # exclusive creator; an existing unowned root is never reused
        sync_directory(target)
        sync_directory(root)
        if inject_at == "after-root":
            raise InjectedCrash(inject_at)
    _durable_directory(root / "product")
    if inject_at == "after-product-dir":
        raise InjectedCrash(inject_at)
    _write_exact(root / "product" / "init-plan.json", canonical_json_bytes(plan))
    if inject_at == "after-plan":
        raise InjectedCrash(inject_at)
    _write_exact(root / "format.json", canonical_json_bytes(value))
    if inject_at == "after-format":
        raise InjectedCrash(inject_at)
    _write_exact(root / ".gitignore", IGNORE_BYTES)
    if inject_at == "after-ignore":
        raise InjectedCrash(inject_at)
    for name in ("intents", "work"):
        _durable_directory(root / name)
        if inject_at == "after-" + name:
            raise InjectedCrash(inject_at)
    return inspect_root(target)


_guard_state = threading.local()


@contextmanager
def writer_guard(target: Path, *, purpose: str = "work"):
    """One stable outer lock for normal writes or exact lifecycle recovery.

Recovery purpose admits only a detach candidate, never arbitrary degraded bytes.
The caller verifies the receipt and complete operation under the same guard.
"""
    require_supported_runtime()
    allowed = {"work": {"root-ready"}, "detach-recovery": {"detach-candidate"}}
    if purpose not in allowed:
        raise _error("unsupported guard purpose")
    target = Path(classify_target(target, mutation=True)["target"])
    held = getattr(_guard_state, "held", set())
    if target in held:
        raise _error("recursive writer guard is forbidden")
    root = target / ROOT_NAME
    if inspect_root(target)["classification"] not in allowed[purpose]:
        raise _error("workspace root is not ready for this guarded operation")
    _durable_directory(root / "locks")
    _guard_state.held = held | {target}
    try:
        with exclusive_file_lock(root / "locks" / "writer.lock"):
            classify_target(target, mutation=True)
            if inspect_root(target)["classification"] not in allowed[purpose]:
                raise _error("workspace changed while acquiring guard")
            yield
    finally:
        _guard_state.held = held
