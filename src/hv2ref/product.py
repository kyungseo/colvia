from __future__ import annotations

import ast
import os
import re
import stat
import sys
from functools import lru_cache
from pathlib import Path
from typing import Any

from .errors import ContractError, InjectedCrash
from .jsonio import canonical_json_bytes, decode_json_bytes, sha256_bytes, sync_directory, write_new_bytes, rename_directory, remove_path


def source_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _exact_dict(value: object, keys: set[str], code: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != keys:
        actual = sorted(value) if isinstance(value, dict) else type(value).__name__
        raise ContractError(code, repr(actual))
    return value


def _lifecycle_output_bytes(value: Any, label: str) -> bytes:
    """Check the exact prospective bytes before publishing lifecycle output."""
    data = canonical_json_bytes(value)
    try:
        decode_json_bytes(data, require_canonical=True)
    except ContractError as exc:
        if exc.code == "HV2-JSON-LIMIT":
            raise ContractError(exc.code, f"prospective-output:{label}:{exc.message}") from exc
        raise
    return data


def _write_exact(path: Path, data: bytes) -> None:
    if path.exists() or path.is_symlink():
        if path.is_symlink() or not path.is_file() or path.read_bytes() != data:
            raise ContractError("HV2-PRODUCT-IMMUTABLE-CONTRADICTION", str(path))
        return
    write_new_bytes(path, data)


# Single-home runtime verification. Lifecycle publication is deliberately separate
# from these read-only checks; lifecycle receipts bind the installed history.
SERIAL_MANAGED_PATHS = (
    '.gitignore',
    'AGENTS.md',
    'CLAUDE.md',
    'PRODUCT-CAPABILITIES.json',
    'README.md',
    'adapters/harness-v2-work/SKILL.md',
    'docs/CONCEPTS.md',
    'docs/GENERAL-WORK.md',
    'docs/GETTING-STARTED.md',
    'docs/GUIDED-INTENT-FORMATION.md',
    'docs/MAINTAINING.md',
    'docs/MANUAL-OPERATION.md',
    'docs/OPERATIONS.md',
    'docs/README.md',
    'docs/REFERENCE.md',
    'docs/SECURITY-AND-SUPPORT.md',
    'docs/WORKSPACE-CONTRACT.md',
    'hv2',
    'src/hv2ref/__init__.py',
    'src/hv2ref/candidates.py',
    'src/hv2ref/cli.py',
    'src/hv2ref/errors.py',
    'src/hv2ref/intent.py',
    'src/hv2ref/jsonio.py',
    'src/hv2ref/product.py',
    'src/hv2ref/umbrella.py',
    'src/hv2ref/view.py',
    'src/hv2ref/work.py',
    'src/hv2ref/workspace.py',
)

UMBRELLA_MANAGED_PATHS = (
    '.gitignore',
    'AGENTS.md',
    'CLAUDE.md',
    'PRODUCT-CAPABILITIES.json',
    'README.md',
    'adapters/harness-v2-work/SKILL.md',
    'docs/CONCEPTS.md',
    'docs/GENERAL-WORK.md',
    'docs/GETTING-STARTED.md',
    'docs/GUIDED-INTENT-FORMATION.md',
    'docs/MAINTAINING.md',
    'docs/MANUAL-OPERATION.md',
    'docs/OPERATIONS.md',
    'docs/README.md',
    'docs/REFERENCE.md',
    'docs/SECURITY-AND-SUPPORT.md',
    'docs/WORKSPACE-CONTRACT.md',
    'hv2',
    'src/hv2ref/__init__.py',
    'src/hv2ref/cli.py',
    'src/hv2ref/errors.py',
    'src/hv2ref/intent.py',
    'src/hv2ref/jsonio.py',
    'src/hv2ref/product.py',
    'src/hv2ref/umbrella.py',
    'src/hv2ref/view.py',
    'src/hv2ref/work.py',
    'src/hv2ref/workspace.py',
)

LEGACY_MANAGED_PATHS = (
    '.gitignore',
    'AGENTS.md',
    'CLAUDE.md',
    'PRODUCT-CAPABILITIES.json',
    'README.md',
    'adapters/harness-v2-work/SKILL.md',
    'docs/CONCEPTS.md',
    'docs/GENERAL-WORK.md',
    'docs/GETTING-STARTED.md',
    'docs/GUIDED-INTENT-FORMATION.md',
    'docs/MAINTAINING.md',
    'docs/MANUAL-OPERATION.md',
    'docs/OPERATIONS.md',
    'docs/README.md',
    'docs/REFERENCE.md',
    'docs/SECURITY-AND-SUPPORT.md',
    'docs/WORKSPACE-CONTRACT.md',
    'hv2',
    'src/hv2ref/__init__.py',
    'src/hv2ref/cli.py',
    'src/hv2ref/errors.py',
    'src/hv2ref/intent.py',
    'src/hv2ref/jsonio.py',
    'src/hv2ref/product.py',
    'src/hv2ref/view.py',
    'src/hv2ref/work.py',
    'src/hv2ref/workspace.py',
)

ENTRY_MANAGED_PATHS = (
    '.gitignore',
    'AGENTS.md',
    'CLAUDE.md',
    'PRODUCT-CAPABILITIES.json',
    'README.md',
    'adapters/colvia-work/SKILL.md',
    'colvia',
    'docs/CONCEPTS.md',
    'docs/GENERAL-WORK.md',
    'docs/GETTING-STARTED.md',
    'docs/GUIDED-INTENT-FORMATION.md',
    'docs/MAINTAINING.md',
    'docs/MANUAL-OPERATION.md',
    'docs/OPERATIONS.md',
    'docs/README.md',
    'docs/REFERENCE.md',
    'docs/SECURITY-AND-SUPPORT.md',
    'docs/WORKSPACE-CONTRACT.md',
    'src/hv2ref/__init__.py',
    'src/hv2ref/candidates.py',
    'src/hv2ref/cli.py',
    'src/hv2ref/errors.py',
    'src/hv2ref/intent.py',
    'src/hv2ref/jsonio.py',
    'src/hv2ref/product.py',
    'src/hv2ref/umbrella.py',
    'src/hv2ref/view.py',
    'src/hv2ref/work.py',
    'src/hv2ref/workspace.py',
)

DELEGATION_MANAGED_PATHS = (
    '.gitignore',
    'AGENTS.md',
    'CLAUDE.md',
    'PRODUCT-CAPABILITIES.json',
    'README.md',
    'adapters/colvia-work/SKILL.md',
    'colvia',
    'docs/CONCEPTS.md',
    'docs/GENERAL-WORK.md',
    'docs/GETTING-STARTED.md',
    'docs/GUIDED-INTENT-FORMATION.md',
    'docs/MAINTAINING.md',
    'docs/MANUAL-OPERATION.md',
    'docs/OPERATIONS.md',
    'docs/README.md',
    'docs/REFERENCE.md',
    'docs/SECURITY-AND-SUPPORT.md',
    'docs/WORKSPACE-CONTRACT.md',
    'src/hv2ref/__init__.py',
    'src/hv2ref/candidates.py',
    'src/hv2ref/cli.py',
    'src/hv2ref/errors.py',
    'src/hv2ref/intent.py',
    'src/hv2ref/jsonio.py',
    'src/hv2ref/product.py',
    'src/hv2ref/umbrella.py',
    'src/hv2ref/view.py',
    'src/hv2ref/work.py',
    'src/hv2ref/workspace.py',
)


CONTINUATION_MANAGED_PATHS = (
    '.gitignore',
    'AGENTS.md',
    'CLAUDE.md',
    'PRODUCT-CAPABILITIES.json',
    'README.md',
    'adapters/colvia-work/SKILL.md',
    'colvia',
    'docs/CONCEPTS.md',
    'docs/GENERAL-WORK.md',
    'docs/GETTING-STARTED.md',
    'docs/GUIDED-INTENT-FORMATION.md',
    'docs/MAINTAINING.md',
    'docs/MANUAL-OPERATION.md',
    'docs/OPERATIONS.md',
    'docs/README.md',
    'docs/REFERENCE.md',
    'docs/SECURITY-AND-SUPPORT.md',
    'docs/WORKSPACE-CONTRACT.md',
    'src/hv2ref/__init__.py',
    'src/hv2ref/candidates.py',
    'src/hv2ref/cli.py',
    'src/hv2ref/continuation.py',
    'src/hv2ref/errors.py',
    'src/hv2ref/intent.py',
    'src/hv2ref/jsonio.py',
    'src/hv2ref/product.py',
    'src/hv2ref/umbrella.py',
    'src/hv2ref/view.py',
    'src/hv2ref/work.py',
    'src/hv2ref/workspace.py',
)


# Windows integration membership is a separate literal policy identity.
WINDOWS_MANAGED_PATHS = (
    '.gitignore',
    'AGENTS.md',
    'CLAUDE.md',
    'PRODUCT-CAPABILITIES.json',
    'README.md',
    'adapters/colvia-work/SKILL.md',
    'colvia',
    'docs/CONCEPTS.md',
    'docs/GENERAL-WORK.md',
    'docs/GETTING-STARTED.md',
    'docs/GUIDED-INTENT-FORMATION.md',
    'docs/MAINTAINING.md',
    'docs/MANUAL-OPERATION.md',
    'docs/OPERATIONS.md',
    'docs/README.md',
    'docs/REFERENCE.md',
    'docs/SECURITY-AND-SUPPORT.md',
    'docs/WORKSPACE-CONTRACT.md',
    'src/hv2ref/__init__.py',
    'src/hv2ref/candidates.py',
    'src/hv2ref/cli.py',
    'src/hv2ref/continuation.py',
    'src/hv2ref/errors.py',
    'src/hv2ref/intent.py',
    'src/hv2ref/jsonio.py',
    'src/hv2ref/product.py',
    'src/hv2ref/umbrella.py',
    'src/hv2ref/view.py',
    'src/hv2ref/work.py',
    'src/hv2ref/workspace.py',
)

WINDOW_PATHS = {"human-1": LEGACY_MANAGED_PATHS, "worker-1": LEGACY_MANAGED_PATHS,
                "umbrella-1": UMBRELLA_MANAGED_PATHS, "planning-1": SERIAL_MANAGED_PATHS,
                "checkout-1": SERIAL_MANAGED_PATHS, "entry-1": ENTRY_MANAGED_PATHS, "delegation-1": DELEGATION_MANAGED_PATHS, "continuation-1": CONTINUATION_MANAGED_PATHS, "windows-2": WINDOWS_MANAGED_PATHS}
WINDOW_LAUNCHERS = {"human-1": "hv2", "worker-1": "hv2", "umbrella-1": "hv2",
                    "planning-1": "hv2", "checkout-1": "hv2", "entry-1": "colvia", "delegation-1": "colvia", "windows-2": "colvia", "continuation-1": "colvia"}
WINDOW_ADAPTERS = {"human-1": "adapters/harness-v2-work/SKILL.md",
                   "worker-1": "adapters/harness-v2-work/SKILL.md",
                   "umbrella-1": "adapters/harness-v2-work/SKILL.md",
                   "planning-1": "adapters/harness-v2-work/SKILL.md",
                   "checkout-1": "adapters/harness-v2-work/SKILL.md",
                   "entry-1": "adapters/colvia-work/SKILL.md",
                   "delegation-1": "adapters/colvia-work/SKILL.md",
                   "windows-2": "adapters/colvia-work/SKILL.md", "continuation-1": "adapters/colvia-work/SKILL.md"}


def _managed_paths(window: str) -> tuple[str, ...]:
    _serial_require(isinstance(window, str) and window in WINDOW_PATHS, "unsupported inventory window")
    return WINDOW_PATHS[window]


def _launcher_path(window: str) -> str:
    _managed_paths(window)
    return WINDOW_LAUNCHERS[window]


def _retired_entry_collision(target: Path) -> dict[str, Any] | None:
    # Names only: never follow or open a retired occupant, including dangling links.
    import unicodedata
    names = sorted((p.name for p in target.iterdir()
                    if unicodedata.normalize("NFC", p.name).casefold() == "hv2"), key=lambda n:n.encode("utf-8"))
    return ({"path": "hv2", "observed_names": names, "ownership": "project", "preserved": True}
            if names else None)


def _refuse_retired_entry(target: Path, operation: str) -> None:
    collision = _retired_entry_collision(target)
    _serial_require(collision is None, operation + ": retired entry collision; preserve project occupants: "
                    + repr(collision["observed_names"] if collision else []))


def _entry_absence_admission(target: Path, *, owned_prefix: bool = False) -> None:
    from .work import _git, _visible_truth
    from .workspace import classify_target
    import unicodedata
    fold = lambda p: unicodedata.normalize("NFC", p).casefold()
    _serial_require(not any(fold(p.name) == "colvia" and not (owned_prefix and p.name == "colvia") for p in target.iterdir()),
                    "preexisting launcher or alias is not owned")
    if classify_target(target)["kind"] != "non-git":
        tracked = _git(target, "ls-files", "-z").stdout
        try:
            names = [p.decode("utf-8", "strict") for p in tracked.split(b"\0") if p]
        except UnicodeDecodeError as exc:
            raise ContractError("HV2-WORKSPACE-PRODUCT", "tracked path encoding unavailable; preserve") from exc
        _serial_require(not any(fold(n) == "colvia" or fold(n).startswith("colvia/") for n in names),
                        "new launcher or alias/descendant is tracked")
    _visible_truth(target, ["colvia"])


def _serial_require(condition: bool, detail: str) -> None:
    if not condition:
        raise ContractError("HV2-WORKSPACE-PRODUCT", detail)


def _launcher_inventory_window(data: bytes, *, allow_legacy: bool = False) -> str:
    """Reuse only declaration parsing; callers still read and verify current bytes."""
    if type(data) is bytes and type(allow_legacy) is bool and len(data) <= 1024 * 1024:
        return _cached_launcher_inventory_window(data, allow_legacy)
    return _parse_launcher_inventory_window(data, allow_legacy=allow_legacy)


@lru_cache(maxsize=4)
def _cached_launcher_inventory_window(data: bytes, allow_legacy: bool) -> str:
    # At most four 1 MiB inputs; exceptions are not retained by lru_cache.
    return _parse_launcher_inventory_window(data, allow_legacy=allow_legacy)


def _parse_launcher_inventory_window(data: bytes, *, allow_legacy: bool = False) -> str:
    """Read a candidate's declaration without executing it; not a code trust check."""
    _serial_require(isinstance(data, bytes) and len(data) <= 1024 * 1024,
                    "invalid or oversized launcher declaration input")
    try:
        module = ast.parse(data)
    except (SyntaxError, RecursionError, MemoryError, ValueError) as exc:
        raise ContractError("HV2-WORKSPACE-PRODUCT", "unreadable launcher declaration") from exc
    name = "WORKSPACE_INVENTORY_ID"
    declarations = [node for node in module.body
                    if isinstance(node, ast.Assign) and len(node.targets) == 1
                    and isinstance(node.targets[0], ast.Name) and node.targets[0].id == name
                    and isinstance(node.value, ast.Constant) and node.value.value in (("worker-1", "umbrella-1", "planning-1", "checkout-1", "entry-1", "delegation-1", "continuation-1", "windows-2") if allow_legacy else ("continuation-1", "windows-2"))]
    target = declarations[0].targets[0] if len(declarations) == 1 else None
    bindings = []
    try:
        for node in ast.walk(module):
            if isinstance(node, ast.Name) and node.id == name and isinstance(node.ctx, (ast.Store, ast.Del)):
                bindings.append(node)
            elif isinstance(node, ast.arg) and node.arg == name:
                bindings.append(node)
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and node.name == name:
                bindings.append(node)
            elif isinstance(node, ast.alias) and (node.asname or node.name.split(".")[0]) == name:
                bindings.append(node)
            elif isinstance(node, (ast.Global, ast.Nonlocal)) and name in node.names:
                bindings.append(node)
            elif isinstance(node, ast.ExceptHandler) and node.name == name:
                bindings.append(node)
            elif isinstance(node, (ast.MatchAs, ast.MatchStar)) and node.name == name:
                bindings.append(node)
            elif isinstance(node, ast.MatchMapping) and node.rest == name:
                bindings.append(node)
            elif isinstance(node, (ast.TypeVar, ast.ParamSpec, ast.TypeVarTuple)) and node.name == name:
                bindings.append(node)
    except (RecursionError, MemoryError, ValueError) as exc:
        raise ContractError("HV2-WORKSPACE-PRODUCT", "unreadable launcher declaration") from exc
    if not bindings and allow_legacy:
        return "human-1"
    _serial_require(len(declarations) == 1 and bindings == [target],
                    "launcher must declare exactly one supported literal inventory window")
    return declarations[0].value.value


def _serial_file(path: Path) -> bytes:
    from .work import _stable_file
    _serial_require(path.lstat().st_nlink == 1, "hardlinked product file: " + str(path))
    if sys.platform == "win32":
        from .jsonio import _windows_detach_read_observation
        scope = _windows_detach_read_observation.get()
        if scope is not None and scope.capture_serial and scope.accepts(scope.absolute(path)):
            # This call still opens the leaf, rereads binary content and checks
            # both handle and final path evidence. Nothing survives this call.
            before, data = _stable_file(path, _capture_bytes=True)
            _serial_require((sha256_bytes(data), len(data)) == before[:2],
                            "unstable product file: " + str(path))
            _serial_require(path.lstat().st_nlink == 1, "hardlinked product file: " + str(path))
            return data
    before = _stable_file(path)
    data = path.read_bytes()
    _serial_require(before == _stable_file(path) and (sha256_bytes(data), len(data)) == before[:2],
                    "unstable product file: " + str(path))
    _serial_require(path.lstat().st_nlink == 1, "hardlinked product file: " + str(path))
    return data


def _serial_tree(root: Path, expected_files: set[str], *, optional_files: set[str] = frozenset()) -> dict[str, bytes]:
    """Exact directories as well as files; never follow an unknown occupant."""
    from .workspace import _require_kind
    _require_kind(root, True)
    expected_dirs = {parent.as_posix() for name in expected_files for parent in Path(name).parents
                     if str(parent) != "."}
    files: dict[str, bytes] = {}
    dirs: set[str] = set()
    pending = [root]
    while pending:
        directory = pending.pop()
        for member in directory.iterdir():
            relative = member.relative_to(root).as_posix()
            if relative in expected_dirs:
                _require_kind(member, True)
                dirs.add(relative)
                pending.append(member)
            else:
                _serial_require(relative in expected_files, "unknown product member: " + relative)
                _require_kind(member, False)
                files[relative] = _serial_file(member)
    _serial_require(expected_files - optional_files <= set(files) <= expected_files and dirs == expected_dirs, "incomplete product tree")
    return files


def _serial_inventory(value: Any) -> dict[str, Any]:
    from .workspace import _sha
    value = _exact_dict(value, {"record_type", "schema_version", "inventory_id", "entries"}, "HV2-WORKSPACE-INVENTORY")
    _serial_require(value["record_type"] == "release-inventory"
                    and type(value["schema_version"]) is int and value["schema_version"] == 1,
                    "unsupported release inventory schema")
    _serial_require(isinstance(value["inventory_id"], str) and value["inventory_id"] in WINDOW_PATHS, "unsupported inventory window")
    _serial_require(isinstance(value["entries"], list), "inventory entries must be an array")
    paths = []
    for item in value["entries"]:
        item = _exact_dict(item, {"path", "sha256", "size_bytes"}, "HV2-WORKSPACE-INVENTORY")
        _serial_require(isinstance(item["path"], str) and item["path"] in _managed_paths(value["inventory_id"]),
                        "unknown inventory path")
        _serial_require(_sha(item["sha256"]) and type(item["size_bytes"]) is int and item["size_bytes"] >= 0,
                        "invalid inventory digest or size")
        paths.append(item["path"])
    _serial_require(paths == list(_managed_paths(value["inventory_id"])), "inventory coverage, order or duplicate")
    return value


def workspace_candidate(source: Path) -> dict[str, Any]:
    """Read the exact managed subset; unrelated source/test files are not shipped."""
    try:
        from .workspace import safe_target, _require_kind
        source = safe_target(source)
        payload: dict[str, bytes] = {}
        for name in CONTINUATION_MANAGED_PATHS:
            path = source / name
            for parent in reversed(path.relative_to(source).parents):
                _require_kind(source / parent, True)
            _require_kind(path, False)
            payload[name] = _serial_file(path)
        window = _launcher_inventory_window(payload["colvia"])
        inventory = {"record_type": "release-inventory", "schema_version": 1, "inventory_id": window,
                     "entries": [{"path": name, "sha256": sha256_bytes(data), "size_bytes": len(data)}
                                 for name, data in payload.items()]}
        digest = sha256_bytes(canonical_json_bytes(inventory))
        # Repeat after reading the complete set; do not silently combine two sources.
        for name, data in payload.items():
            _serial_require(_serial_file(source / name) == data, "candidate changed while reading")
        return {"inventory": inventory, "payload": payload,
                "release_ref": {"id": "product-release-" + digest[:24], "sha256": digest, "inventory_id": window}}
    except OSError as exc:
        raise ContractError("HV2-WORKSPACE-PRODUCT", "candidate managed bytes unavailable; preserve source and target") from exc


def _workspace_release_once(path: Path) -> tuple[dict[str, Any], dict[str, bytes], Path]:
    """Read and validate one release; the caller must independently compare it."""
    from .workspace import safe_target
    path = safe_target(path)
    from .workspace import _require_kind
    _require_kind(path / "inventory.json", False)
    inventory_bytes = _serial_file(path / "inventory.json")
    inventory = _serial_inventory(decode_json_bytes(inventory_bytes, require_canonical=True))
    files = _serial_tree(path, {"inventory.json"} | {"payload/" + p for p in _managed_paths(inventory["inventory_id"])})
    _serial_require(files["inventory.json"] == inventory_bytes, "inventory changed while reading")
    digest = sha256_bytes(files["inventory.json"])
    _serial_require(path.name == "product-release-" + digest[:24], "release directory/inventory mismatch")
    for entry in inventory["entries"]:
        data = files["payload/" + entry["path"]]
        _serial_require(len(data) == entry["size_bytes"] and sha256_bytes(data) == entry["sha256"],
                        "payload digest mismatch: " + entry["path"])
    _serial_require(_launcher_inventory_window(files["payload/" + _launcher_path(inventory["inventory_id"])], allow_legacy=True)
                    == inventory["inventory_id"], "launcher declaration differs from inventory window")
    return {"release_ref": {"id": path.name, "sha256": digest, "inventory_id": inventory["inventory_id"]},
            "inventory": inventory}, files, path


def verify_workspace_release(path: Path) -> dict[str, Any]:
    """Verify immutable inventory bytes, exact payload membership and every digest."""
    verified, files, path = _workspace_release_once(path)
    _serial_require(files == _serial_tree(path, set(files)), "release changed while reading")
    return verified


# Only this audited predecessor is admitted across the one-way entry boundary.
ENTRY_PREDECESSOR = {
    "id": "product-release-8bd0eeac55fb0af92b61a7a3",
    "sha256": "8bd0eeac55fb0af92b61a7a36a98adb9957b880c791b957b20c319a51c5577f3",
    "inventory_id": "checkout-1",
}


def _entry_retirement(plan: dict[str, Any], prior: dict[str, Any], inventory: dict[str, Any]) -> None:
    if plan["schema_version"] != 2:
        return
    if prior["active_release"]["inventory_id"] == "checkout-1":
        _serial_require(prior["active_release"] == ENTRY_PREDECESSOR,
                        "entry transition predecessor is not the audited release")
        entry = next(e for e in inventory["entries"] if e["path"] == "hv2")
        _serial_require(plan["action"] == "update" and plan["remove"] == [entry],
                        "entry retirement differs from the verified predecessor launcher")
    else:
        _serial_require(prior["active_release"]["inventory_id"] in ("entry-1", "windows-2") and plan["remove"] == [],
                        "same-entry switch cannot retire project paths")


def _entry_umask() -> None:
    # Inspect without creating a probe file; restore even a rejected process mask.
    mask = os.umask(0o777)
    os.umask(mask)
    _serial_require(0o600 & ~mask == 0o600, "unsupported umask for atomic entry mode 0600")


def _entry_file_prefix(path: Path, data: bytes, *, executable: bool) -> dict[str, Any] | None:
    from .workspace import _exists, _require_kind
    if not _exists(path):
        return None
    _require_kind(path, False)
    raw = _serial_file(path)
    mode = stat.S_IMODE(path.lstat().st_mode)
    _serial_require((mode == 0o600 and data.startswith(raw)) or
                    (executable and mode == 0o755 and raw == data),
                    "unexpected entry bytes/mode; preserve: " + str(path))
    return {"sha256": sha256_bytes(raw), "size_bytes": len(raw), "mode": mode}


def _entry_binding_stage(target: Path, plan: dict[str, Any], data: bytes, *, allowed: bool) -> dict[str, Any] | None:
    from .workspace import _exists, _require_kind
    staging = target / ".hrn/staging"
    if not _exists(staging):
        return None
    _require_kind(staging, True)
    operation = staging / ("entry-" + plan["operation_id"])
    if not _exists(operation):
        return None
    _require_kind(operation, True)
    names = {p.name for p in operation.iterdir()}
    _serial_require(names <= {"binding.next"}, "unknown entry staging member; preserve")
    _serial_require(allowed or not names, "binding staging is not an expected physical prefix")
    observed = _entry_file_prefix(operation / "binding.next", data, executable=False) if names else None
    return {"directory": True, "binding_next": observed}


def _entry_transition_prefix(target: Path, plan: dict[str, Any], old: bytes, new: bytes | None,
                             binding_bytes: bytes) -> dict[str, Any]:
    from .workspace import _exists, _require_kind
    import unicodedata
    fold = lambda name: unicodedata.normalize("NFC", name).casefold()
    names = {p.name for p in target.iterdir()}
    _serial_require(not any(fold(n) in {"hv2", "colvia"} and n not in {"hv2", "colvia"} for n in names),
                    "entry transition root alias; preserve")
    old_path = target / "hv2"
    old_present = _exists(old_path)
    if old_present:
        _require_kind(old_path, False)
        _serial_require(_serial_file(old_path) == old and stat.S_IMODE(old_path.lstat().st_mode) == 0o755,
                        "transition old launcher bytes/mode changed; preserve")
    if new is None:
        _serial_require(old_present and not _exists(target / "colvia"), "launcher without complete entry release")
        new_observation = None
        prefix = "receipt-or-staging"
    else:
        new_observation = _entry_file_prefix(target / "colvia", new, executable=True)
        ready = new_observation is not None and new_observation["mode"] == 0o755
        _serial_require(old_present or ready, "missing old launcher before executable new entry; preserve")
        prefix = "S5" if not old_present else "S4" if ready else "S3-prefix" if new_observation else "S3"
    stage = _entry_binding_stage(target, plan, binding_bytes, allowed=prefix == "S5")
    return {"prefix": prefix, "old_present": old_present, "new": new_observation, "staging": stage}


def _entry_local_baselines(target: Path) -> dict[str, dict[str, Any]]:
    """Reload immutable selected local/parent manifests; workers stay untouched."""
    from .work import WorkStore, _resolve
    from .intent import read_workspace_intent_graph, _resolve_workspace_intent
    import unicodedata
    baselines = {}
    def depends(name):
        name = unicodedata.normalize("NFC", name).casefold()
        return any(name == entry or name.startswith(entry + "/") or entry.startswith(name + "/")
                   for entry in ("hv2", "colvia"))
    graphs = WorkStore(target)._all()
    for work_id, graph in graphs.items():
        if graph["current"] is None or graph["state"] == "completed":
            continue
        selected = graph["selections"][graph["current"]["selection_ref"]["id"]]
        revision = graph["revisions"][selected["revision_ref"]["id"]]
        if revision["execution_context"]["mode"] != "local":
            continue
        intent_graph = read_workspace_intent_graph(target, revision["intent_ref"]["id"])
        _, bound = _resolve_workspace_intent(intent_graph, revision["intent_ref"]["id"],
                                              revision["intent_ref"], require_current=False)
        intent = _resolve(intent_graph["acceptances"], bound["acceptance_ref"])["confirmation"]
        paths = list(revision["scope"])
        for record in (revision, intent):
            for kind in ("document_refs", "evidence_refs"):
                paths.extend(ref["path"] for ref in record.get(kind, []) if ref["required"])
        _serial_require(not any(depends(name) for name in paths), "entry path dependency in selected local Work: " + work_id)
        if revision["schema_version"] == 2:
            offending_children = set()
            for child in revision["umbrella_evidence"]["children"]:
                child_id = child["work"]["id"]
                child_revision = _resolve(graphs[child_id]["revisions"], child["revision_ref"])
                child_graph = read_workspace_intent_graph(target, child["intent_ref"]["id"])
                _, child_bound = _resolve_workspace_intent(child_graph, child["intent_ref"]["id"],
                                                          child["intent_ref"], require_current=False)
                child_intent = _resolve(child_graph["acceptances"], child_bound["acceptance_ref"])["confirmation"]
                if any(depends(ref["path"]) for record in (child_revision, child_intent)
                       for kind in ("document_refs", "evidence_refs")
                       for ref in record.get(kind, []) if ref["required"]):
                    offending_children.add(child_id)
            _serial_require(not offending_children, "entry path dependency in selected local parent Work: " + work_id
                            + "; captured child Work IDs: " + repr(sorted(offending_children)))
        baselines[work_id] = graph["manifests"][revision["result_refs"]["manifest"]["id"]]["result"]
    return baselines


def _entry_compare_local(target: Path, *, launcher_sha256: str, window: str) -> dict[str, Any]:
    from .work import snapshot
    baselines = _entry_local_baselines(target)
    if not baselines:
        return {"classification": "not-applicable", "work_ids": [], "reason": "no unfinished selected local Work"}
    actual = snapshot(target, verified_launcher_sha256=launcher_sha256, verified_inventory_id=window)
    mismatches = sorted(work_id for work_id, expected in baselines.items() if expected != actual)
    _serial_require(not mismatches, "entry transition selected local baseline differs: " + repr(mismatches) +
                    ("; B1 remains current and verified; product cutover is complete; preserve project content"
                     if window == "entry-1" else "; no transition receipt has been published"))
    return {"classification": "verified", "work_ids": sorted(baselines), "observation": "actual project snapshot"}


def _entry_admission(target: Path, state: dict[str, Any]) -> None:
    _serial_require(state["binding"]["active_release"] == ENTRY_PREDECESSOR,
                    "entry transition predecessor is not the audited release")
    _serial_require(state["pending"] is None, "old pending lifecycle requires the retained old source")
    _entry_umask()
    _entry_absence_admission(target)
    _serial_require(_retired_entry_collision(target) ==
                    {"path": "hv2", "observed_names": ["hv2"], "ownership": "project", "preserved": True},
                    "transition predecessor launcher missing or aliased")
    _serial_require(stat.S_IMODE((target / "hv2").lstat().st_mode) == 0o755, "transition predecessor launcher mode")
    from .workspace import _exists, _require_kind
    staging = target / ".hrn/staging"
    if _exists(staging):
        _require_kind(staging, True)
        for member in staging.iterdir():
            _require_kind(member, True)
            _serial_require(not any(member.iterdir()), "unresolved staging; retain old source and preserve")
    _entry_compare_local(target, launcher_sha256=state["launcher_sha256"], window="checkout-1")


def _entry_sync(target: Path, path: Path, *, phase: str, role: str, b1: bool = False) -> None:
    """D3 applies only to the admitted transition, never shared helper policy."""
    failure = None
    try:
        result = sync_directory(path)
    except OSError as exc:
        failure = "oserror:" + str(exc.errno)
    else:
        if result != "pass":
            failure = str(result)
    if failure is None:
        return
    verification = "not-requested"
    if b1:
        try:
            verify_workspace_product(target)
        except (ContractError, OSError):
            verification = "unavailable"
        else:
            verification = "verified"
    raise ContractError("HV2-WORKSPACE-PRODUCT",
                        f"d3-sync:{phase}:{role}; directory synchronization {failure}; "
                        f"B1 publication observed={'yes' if b1 else 'no'}; current product verification={verification}; "
                        "preserve receipt, prefix and binding; use the exact admitted retry or separately authorized disposition")


def _entry_durable_directory(target: Path, path: Path, *, role: str) -> None:
    from .workspace import _exists, _require_kind
    phase = "recovery" if _exists(path) else "publication"
    try:
        path.mkdir()
    except FileExistsError:
        _require_kind(path, True)
    _entry_sync(target, path.parent, phase=phase, role=role + "-parent")
    _entry_sync(target, path, phase=phase, role=role + "-self")


def _entry_write_exact(target: Path, path: Path, data: bytes, *, role: str) -> None:
    from .workspace import _exists, _require_kind, _error
    from .jsonio import _sync_fd
    # Every caller has explicitly prepared its parent. No hidden parent creation.
    _require_kind(path.parent, True)
    if _exists(path):
        _require_kind(path, False)
        if path.read_bytes() != data:
            raise _error(f"immutable mismatch: {path.name}; preserve torn/modified bytes for explicit manual disposition")
        with path.open("rb") as handle:
            os.fsync(handle.fileno())
        phase = "recovery"
    else:
        try:
            with path.open("xb") as handle:
                handle.write(data); handle.flush(); _sync_fd(handle.fileno())
        except FileExistsError as exc:
            raise ContractError("HV2-IMMUTABLE-EXISTS", str(path)) from exc
        phase = "publication"
    _entry_sync(target, path.parent, phase=phase, role=role)


def _entry_inventory_directories(release: Path, inventory: dict[str, Any]) -> set[Path]:
    return {release} | {release / parent for item in inventory["entries"]
                        for parent in (Path("payload") / item["path"]).parents if str(parent) != "."}


def _entry_sync_paths(target: Path, plan: dict[str, Any], inventory: dict[str, Any], *,
                      candidate: dict[str, Any] | None = None, replay: bool = False) -> dict[Path, str]:
    """Finite inventory-derived set, qualified before any D3 probe. No history walk."""
    from .workspace import _exists, _require_kind
    root = target / ".hrn"; product = root / "product"
    paths = {target: "target", root: "home", product: "product", product / "receipts": "receipts",
             product / "releases": "releases", root / "locks": "locks"}
    for path in paths:
        _require_kind(path, True)
    rid = plan["candidate_release"]["id"]; release = product / "releases" / rid
    if _exists(release):
        _serial_require(verify_workspace_release(release)["release_ref"] == plan["candidate_release"], "published candidate mismatch")
        for path in _entry_inventory_directories(release, inventory):
            _require_kind(path, True)
            paths[path] = "release-directory" if path == release else "release-member-directory"
    else:
        _serial_require(not replay, "current transition release missing; preserve")
    staging = root / "staging"
    if _exists(staging):
        _require_kind(staging, True); paths[staging] = "staging"
        operation = staging / ("switch-" + plan["operation_id"])
        if _exists(operation):
            _require_kind(operation, True); paths[operation] = "switch-operation"
            names = {p.name for p in operation.iterdir()}
            _serial_require(names <= ({rid} if not _exists(release) else set()), "unknown switch staging member; preserve")
            staged = operation / rid
            if _exists(staged):
                _serial_require(candidate is not None and not replay, "candidate staging without exact source; preserve")
                expected = {"inventory.json": canonical_json_bytes(candidate["inventory"])} | {
                    "payload/" + p: data for p, data in candidate["payload"].items()}
                _init_partial_tree(staged, expected)
                for path in _entry_inventory_directories(staged, inventory):
                    if _exists(path):
                        _require_kind(path, True)
                        paths[path] = "candidate-directory"
        operation = staging / ("entry-" + plan["operation_id"])
        if _exists(operation):
            # The preflight has already admitted the exact binding prefix.
            _require_kind(operation, True)
            names = {p.name for p in operation.iterdir()}
            _serial_require(names <= ({"binding.next"} if not replay else set()), "binding staging is not an expected physical prefix")
            paths[operation] = "binding-operation"
    return paths


def _entry_sync_admission(target: Path, plan: dict[str, Any], candidate: dict[str, Any]) -> None:
    paths = _entry_sync_paths(target, plan, candidate["inventory"], candidate=candidate)
    first = [target, target / ".hrn", target / ".hrn/product", target / ".hrn/product/receipts",
             target / ".hrn/product/releases", target / ".hrn/locks", target / ".hrn/staging"]
    ordered = [p for p in first if p in paths]
    ordered += sorted(paths.keys() - set(first), key=lambda p: (len(p.relative_to(target).parts), p.relative_to(target).as_posix().encode("utf-8")))
    for path in ordered:
        _entry_sync(target, path, phase="admission", role=paths[path])


def _entry_resync_release(target: Path, plan: dict[str, Any], inventory: dict[str, Any]) -> None:
    from .workspace import _exists, _require_kind
    release = target / ".hrn/product/releases" / plan["candidate_release"]["id"]
    paths = {path: "release-directory" for path in _entry_inventory_directories(release, inventory)}
    paths[release.parent] = "release-parent"
    operation = target / ".hrn/staging" / ("switch-" + plan["operation_id"])
    # A permitted empty-directory retirement still leaves a parent to sync.
    operation = next(path for path in (operation, operation.parent, target / ".hrn") if _exists(path))
    paths[operation] = "release-operation-parent"
    for path in sorted(paths, key=lambda p: (-len(p.relative_to(target).parts), p.relative_to(target).as_posix().encode("utf-8"))):
        _require_kind(path, True)
        _entry_sync(target, path, phase="recovery", role=paths[path])


def _entry_append_file(path: Path, data: bytes, *, target: Path, executable: bool, recover: bool, checkpoint) -> None:
    """Exclusive named publication; only the receipt-bound 0600 prefix may grow."""
    from .workspace import _exists
    from .jsonio import _sync_fd
    checkpoint()
    exists = _exists(path)
    _serial_require(recover or not exists, "new entry occupant appeared; preserve")
    before = _entry_file_prefix(path, data, executable=executable) if exists else None
    flags = os.O_RDWR | os.O_NOFOLLOW
    if not exists:
        flags |= os.O_CREAT | os.O_EXCL
    fd = os.open(path, flags, 0o600)
    try:
        def identity():
            opened = os.fstat(fd); current = path.lstat()
            _serial_require(stat.S_ISREG(opened.st_mode) and opened.st_nlink == current.st_nlink == 1
                            and (opened.st_dev, opened.st_ino) == (current.st_dev, current.st_ino),
                            "entry descriptor/path identity changed; preserve")
            return opened
        st = identity()
        wanted_mode = before["mode"] if before else 0o600
        _serial_require(stat.S_IMODE(st.st_mode) == wanted_mode, "entry atomic initial mode differs")
        observed = b""
        while chunk := os.read(fd, 1024 * 1024):
            observed += chunk
            _serial_require(len(observed) <= len(data), "entry prefix grew unexpectedly")
        _serial_require(data.startswith(observed) and (before is None or
                        before == {"sha256": sha256_bytes(observed), "size_bytes": len(observed), "mode": wanted_mode}),
                        "entry prefix changed while reopening")
        _serial_require(wanted_mode == 0o600 or (executable and wanted_mode == 0o755 and observed == data),
                        "unexpected executable prefix")
        while len(observed) < len(data):
            checkpoint(); identity()
            count = os.write(fd, data[len(observed):])
            _serial_require(count > 0, "entry write made no progress; preserve prefix")
            observed += data[len(observed):len(observed) + count]
        checkpoint(); identity(); _sync_fd(fd)
        if executable and wanted_mode == 0o600:
            checkpoint(); identity(); os.fchmod(fd, 0o755)
            checkpoint(); identity(); _sync_fd(fd)
        _serial_require(_serial_file(path) == data and stat.S_IMODE(identity().st_mode) == (0o755 if executable else 0o600),
                        "entry publication changed before directory sync")
    finally:
        os.close(fd)
    checkpoint()
    _entry_sync(target, path.parent, phase="recovery" if exists else "publication",
                role="new-entry-parent" if executable else "binding-member-parent")


def _entry_replay_result(target: Path, plan: dict[str, Any], *, classification: str) -> dict[str, Any]:
    if sys.platform == "win32" and plan["schema_version"] == 6:
        from .work import _lifecycle_git_observation
        # A fresh read-only phase after B1 publication, with independent leaf
        # reads and final ancestor/Git checks before the result can escape.
        with _switch_read_scope(target), _lifecycle_git_observation(target):
            return _entry_replay_records(target, plan, classification=classification)
    return _entry_replay_records(target, plan, classification=classification)


def _entry_replay_records(target: Path, plan: dict[str, Any], *, classification: str) -> dict[str, Any]:
    from .jsonio import _sync_fd
    product = verify_workspace_product(target)
    _refuse_retired_entry(target, "entry lifecycle completion/replay; preserve historical result")
    if (plan["remove"] or plan["schema_version"] in (4, 5)) and product["binding_ref"]["id"] == plan["operation_id"]:
        paths = _entry_sync_paths(target, plan, product["inventory"], replay=True)
        # Caller holds the shared writer guard. An observed B1 can precede the
        # last directory sync, so exact current replay finishes durability only.
        _serial_require(stat.S_IMODE((target / "colvia").lstat().st_mode) == 0o755,
                        "completed transition entry mode differs; preserve B1")
        for path in (target / "colvia", target / ".hrn/product/binding.json"):
            fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
            try:
                opened = os.fstat(fd); observed = path.lstat()
                _serial_require(stat.S_ISREG(opened.st_mode) and opened.st_nlink == observed.st_nlink == 1
                                and (opened.st_dev, opened.st_ino) == (observed.st_dev, observed.st_ino),
                                "completed transition descriptor changed; preserve B1")
                _sync_fd(fd)
            finally:
                os.close(fd)
        for directory in sorted(paths, key=lambda p: (-len(p.relative_to(target).parts), p.relative_to(target).as_posix().encode("utf-8"))):
            _entry_sync(target, directory, phase="replay", role=paths[directory], b1=True)
        _serial_require(product == verify_workspace_product(target), "completed transition changed during sync")
    # Native completed replay observes current truth under the writer guard;
    # it adds no file mutation preflight or reflush (Windows replay contract).
    result = {"classification": classification, "operation_id": plan["operation_id"], "product": product}
    if plan["remove"] or plan["schema_version"] in (4, 5, 6):
        truth = _lifecycle_truth(target, allow_pending=True)
        if truth != plan["truth_refs"]:
            result.update(classification="degraded", historical_operation_result=classification)
            result["transition_content_verification"] = {
                "classification": "unavailable",
                "reason": "truth changed after transition; current binding remains verified; use current Work content/ref checks"}
        elif plan["remove"]:
            result["transition_content_verification"] = _entry_compare_local(
                target, launcher_sha256=product["launcher_sha256"], window="entry-1")
        else:
            result["transition_content_verification"] = {
                "classification": "verified", "scope": "recorded authority bytes and graph references; not live project result content"}
        _serial_require(truth == _lifecycle_truth(target, allow_pending=True),
                        "truth changed during completed transition comparison; preserve B1")
    return result


def _switch_plan_shape(plan: Any, fmt: dict[str, Any]) -> dict[str, Any]:
    from .workspace import PLAN_KEYS, _id, _sha, _text
    from .work import validate_ref
    plan = _exact_dict(plan, set(PLAN_KEYS), "HV2-WORKSPACE-PLAN")
    _serial_require(plan["record_type"] == "lifecycle-plan" and type(plan["schema_version"]) is int
                    and plan["schema_version"] in (1, 2, 4, 5, 6) and plan["action"] in ("update", "rollback"), "unsupported switch plan")
    _serial_require(_id(plan["operation_id"]) and plan["authority_home_id"] == fmt["authority_home_id"]
                    and _text(plan["created_at"]) and _sha(plan["target_fingerprint"])
                    and plan["format_sha256"] == sha256_bytes(canonical_json_bytes(fmt)), "switch plan identity/format")
    validate_ref(plan["expected_binding_ref"])
    ref = _exact_dict(plan["candidate_release"], {"id", "sha256", "inventory_id"}, "HV2-WORKSPACE-RELEASE")
    _serial_require(_sha(ref["sha256"]) and ref["id"] == "product-release-" + ref["sha256"][:24]
                    and isinstance(ref["inventory_id"], str) and ref["inventory_id"] in WINDOW_PATHS, "invalid switch release")
    _serial_require(plan["schema_version"] == (6 if ref["inventory_id"] == "windows-2" else 5 if ref["inventory_id"] == "continuation-1" else 4 if ref["inventory_id"] == "delegation-1" else 2 if ref["inventory_id"] == "entry-1" else 1), "switch schema/window pair")
    if plan["schema_version"] in (1, 4, 5, 6):
        _serial_require(plan["remove"] == [], "same-path switch cannot remove")
    else:
        _serial_require(isinstance(plan["remove"], list) and len(plan["remove"]) <= 1, "entry retirement shape")
        if plan["remove"]:
            retired = _exact_dict(plan["remove"][0], {"path", "sha256", "size_bytes"}, "HV2-WORKSPACE-PLAN")
            _serial_require(retired["path"] == "hv2" and _sha(retired["sha256"])
                            and type(retired["size_bytes"]) is int and retired["size_bytes"] >= 0, "entry retirement identity")
    _serial_require(plan["preserve"] == [] and isinstance(plan["truth_refs"], list), "switch cannot remove truth")
    names = []
    for ref in plan["truth_refs"]:
        ref = _exact_dict(ref, {"path", "sha256"}, "HV2-WORKSPACE-TRUTH")
        name = ref["path"]
        _serial_require(isinstance(name, str) and (name == "planning/candidates.json" or (name.split("/")[0] in ("intents", "work") and len(name.split("/")) >= 3)) and all(p not in ("", ".", "..") for p in name.split("/"))
                        and "\\" not in name and _sha(ref["sha256"]), "invalid truth path/digest")
        names.append(name)
    _serial_require(names == sorted(set(names), key=lambda n:n.encode()), "truth refs order/duplicate")
    return plan


def _switch_binding_receipt(plan: dict[str, Any], prior: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    from .work import record_ref
    _serial_require(plan["expected_binding_ref"] == record_ref(prior, "operation_id"), "switch predecessor mismatch")
    _serial_require(plan["candidate_release"] != prior["active_release"], "switch to active release is not an operation")
    rank = {"human-1": 0, "worker-1": 1, "umbrella-1": 2, "planning-1": 3, "checkout-1": 4, "entry-1": 5, "delegation-1": 6, "continuation-1": 7}
    next_window = plan["candidate_release"]["inventory_id"]
    prior_window = prior["active_release"]["inventory_id"]
    if "windows-2" in (next_window, prior_window):
        _serial_require(next_window == prior_window == "windows-2" and plan["schema_version"] == 6
                        and plan["remove"] == [], "windows-2 requires a same-window schema-6 switch")
    else:
        _serial_require(next_window in rank and prior_window in rank, "unsupported inventory window")
        _serial_require(rank[next_window] >= rank[prior_window],
                        "inventory history cannot downgrade to an older semantic window")
    if plan["schema_version"] == 2 and next_window != "windows-2":
        window = prior["active_release"]["inventory_id"]
        _serial_require(window in ("checkout-1", "entry-1"), "entry switch predecessor")
        _serial_require((window == "checkout-1") == bool(plan["remove"]), "entry retirement/predecessor mismatch")
        _serial_require(window == "entry-1" or plan["action"] == "update", "entry transition requires update")
        if window == "checkout-1":
            _serial_require(prior["active_release"] == ENTRY_PREDECESSOR, "entry transition predecessor is not the audited release")
    if plan["schema_version"] == 4:
        window = prior["active_release"]["inventory_id"]
        _serial_require(window in ("entry-1", "delegation-1") and plan["remove"] == [], "delegation predecessor/remove")
        if window == "entry-1":
            _serial_require(plan["action"] == "update" and prior["active_release"] == DELEGATION_PREDECESSOR,
                            "delegation transition requires exact audited entry-1 update")
    if plan["schema_version"] == 5:
        window = prior["active_release"]["inventory_id"]
        _serial_require(window in ("delegation-1", "continuation-1") and plan["remove"] == [],
                        "continuation predecessor/remove")
        if window == "delegation-1":
            _serial_require(plan["action"] == "update" and prior["active_release"] == CONTINUATION_PREDECESSOR,
                            "continuation transition requires exact qualified delegation-1 update")
    if plan["action"] == "rollback":
        _serial_require(plan["candidate_release"] == prior["prior_release"], "rollback must select the recorded previous release")
    binding = {"record_type":"product-binding", "schema_version":1, "authority_home_id":plan["authority_home_id"],
               "active_release":plan["candidate_release"], "prior_release":prior["active_release"], "operation_id":plan["operation_id"]}
    receipt = {"record_type":"lifecycle-receipt", "schema_version":plan["schema_version"], "operation_id":plan["operation_id"],
               "plan":plan, "prior_binding_ref":record_ref(prior,"operation_id"), "result_binding_ref":record_ref(binding,"operation_id")}
    return binding, receipt


def _workspace_product_once(target: Path, *, allow_pending: bool = False, repair_candidate: dict[str, Any] | None = None) -> dict[str, Any]:
    from .workspace import inspect_root, _file_json, _validate_plan_shape, _require_kind, _exists, _id
    from .work import _visible_truth, record_ref, validate_ref
    root = target / ".hrn"; product = root / "product"
    _serial_require(inspect_root(target)["classification"] == "root-ready", "root is not ready")
    fmt = _file_json(root / "format.json"); initial = _file_json(product / "init-plan.json")
    _validate_plan_shape(initial)
    first_binding, first_receipt = _init_binding_receipt({"plan":initial})
    _require_kind(product / "receipts", True)
    receipts = {}; raw_receipts = {}
    for path in (product / "receipts").iterdir():
        _require_kind(path, False); data = _serial_file(path)
        receipt = _exact_dict(decode_json_bytes(data, require_canonical=True),
                             {"record_type","schema_version","operation_id","plan","prior_binding_ref","result_binding_ref"}, "HV2-WORKSPACE-RECEIPT")
        op = receipt["operation_id"]
        _serial_require(_id(op) and path.name == op + ".json" and receipt["record_type"] == "lifecycle-receipt"
                        and type(receipt["schema_version"]) is int and receipt["schema_version"] in (1, 2, 4, 5, 6), "invalid receipt identity/schema")
        _serial_require(op not in receipts, "duplicate receipt")
        receipts[op] = receipt; raw_receipts[op] = data
    _serial_require(len({op.casefold() for op in receipts}) == len(receipts), "receipt case alias")
    _serial_require(raw_receipts.get(initial["operation_id"]) == canonical_json_bytes(first_receipt), "initial receipt mismatch")
    children = {}
    for op, receipt in receipts.items():
        if op == initial["operation_id"]: continue
        plan = _switch_plan_shape(receipt["plan"], fmt)
        _serial_require(op == plan["operation_id"], "receipt/plan identity mismatch")
        validate_ref(receipt["prior_binding_ref"]); validate_ref(receipt["result_binding_ref"])
        prior = receipt["prior_binding_ref"]; key = (prior["id"], prior["sha256"])
        _serial_require(key not in children, "forked product history")
        children[key] = receipt
    bindings = [first_binding]; chain = [first_receipt]
    while True:
        prior_ref = record_ref(bindings[-1], "operation_id")
        child = children.get((prior_ref["id"], prior_ref["sha256"]))
        if child is None: break
        _serial_require(len(chain) < len(receipts), "cyclic product history")
        binding, expected_receipt = _switch_binding_receipt(child["plan"], bindings[-1])
        _serial_require(raw_receipts[child["operation_id"]] == canonical_json_bytes(expected_receipt), "receipt does not bind complete plan/result")
        bindings.append(binding); chain.append(child)
    _serial_require(len(chain) == len(receipts), "orphan product receipt")
    raw_binding = _serial_file(product / "binding.json")
    matches = [i for i,b in enumerate(bindings) if canonical_json_bytes(b) == raw_binding]
    _serial_require(len(matches) == 1 and matches[0] >= len(bindings)-2, "binding is not the current or single pending predecessor")
    index = matches[0]; binding = bindings[index]; pending = chain[-1] if index != len(bindings)-1 else None
    _serial_require(not _exists(root / "planning") or binding["active_release"]["inventory_id"] in ("planning-1", "checkout-1", "entry-1", "delegation-1", "continuation-1", "windows-2"), "planning records require an applied planning-capable binding")
    _serial_require(binding["active_release"]["inventory_id"] in ("continuation-1", "windows-2") or
                    (not _exists(root / "work") or not any(_exists(path / "continuation") for path in (root / "work").iterdir())),
                    "continuation truth requires an applied continuation-1 binding")
    _serial_require(allow_pending or pending is None, "pending lifecycle blocks product use; recover exact plan from independent source")
    if repair_candidate is not None:
        _serial_require(binding["active_release"]["inventory_id"] in ("continuation-1", "windows-2"),
                        "older-window repair requires the exact retained old source")
        _serial_require(pending is None and repair_candidate["release_ref"] == binding["active_release"],
                        "repair requires the exact active release and no pending lifecycle")
    repair_paths = set()
    releases = {}
    release_files = {}
    for i,b in enumerate(bindings):
        ref = b["active_release"]; rid = ref["id"]
        if rid in releases:
            _serial_require(releases[rid]["release_ref"] == ref, "release prefix collision")
            continue
        path = product / "releases" / rid
        if i > index and not _exists(path): continue
        _require_kind(product / "releases", True)
        if repair_candidate is not None and ref == repair_candidate["release_ref"]:
            repair_paths = {"releases/"+rid+"/inventory.json"} | {"releases/"+rid+"/payload/"+p for p in _managed_paths(ref["inventory_id"])}
            verified = {key: repair_candidate[key] for key in ("release_ref", "inventory")}
        elif sys.platform == "win32":
            verified, release_files[rid], _ = _workspace_release_once(path)
        else:
            verified = verify_workspace_release(path)
        _serial_require(verified["release_ref"] == ref, "binding/release mismatch")
        releases[rid] = verified
    for position, receipt in enumerate(chain[1:], 1):
        previous = bindings[position - 1]
        _entry_retirement(receipt["plan"], previous, releases[previous["active_release"]["id"]]["inventory"])
        if position <= index and receipt["plan"]["remove"]:
            _entry_binding_stage(target, receipt["plan"], canonical_json_bytes(bindings[position]), allowed=False)
            if position == index:
                _serial_require(stat.S_IMODE((product / "binding.json").lstat().st_mode) in (0o600, 0o644),
                                "entry transition B1 mode is not 0600 or 0644")
    expected = {"init-plan.json", "binding.json"} | {"receipts/"+op+".json" for op in receipts}
    for rid in releases:
        expected |= {"releases/"+rid+"/inventory.json"} | {"releases/"+rid+"/payload/"+p for p in _managed_paths(releases[rid]["inventory"]["inventory_id"])}
    files = _serial_tree(product, expected, optional_files=repair_paths)
    # The complete product read supplies the independent second release read.
    # Keep this comparison local to this observation, including retained releases.
    for rid, prior_files in release_files.items():
        prefix = "releases/" + rid + "/"
        _serial_require(prior_files == {name[len(prefix):]: data for name, data in files.items()
                                        if name.startswith(prefix)}, "release changed while reading")
    _serial_require(files["binding.json"] == raw_binding and files["init-plan.json"] == canonical_json_bytes(initial)
                    and all(files["receipts/"+op+".json"] == data for op,data in raw_receipts.items()), "product changed while reading")
    active = binding["active_release"]["id"]
    launcher_name = _launcher_path(binding["active_release"]["inventory_id"])
    launcher = target / launcher_name
    entry_transition = None
    crossing = pending is not None and bool(pending["plan"]["remove"])
    if repair_candidate is not None:
        _refuse_retired_entry(target, "current repair observation")
        repair_window = binding["active_release"]["inventory_id"]
        actual = {".hrn/product/" + p: _repair_file_observation(product / p, repair_window) for p in sorted(repair_paths)}
        actual[launcher_name] = _repair_file_observation(launcher, repair_window)
        launcher_bytes = _serial_file(launcher) if _exists(launcher) else b""
    elif crossing:
        actual = None
        old_bytes = files["releases/" + active + "/payload/hv2"]
        pending_id = pending["plan"]["candidate_release"]["id"]
        new_bytes = files["releases/" + pending_id + "/payload/colvia"] if pending_id in releases else None
        entry_transition = _entry_transition_prefix(target, pending["plan"], old_bytes, new_bytes,
                                                     canonical_json_bytes(bindings[-1]))
        launcher_bytes = old_bytes if entry_transition["old_present"] else None
    else:
        actual = None
        _require_kind(launcher, False); launcher_bytes = _serial_file(launcher)
        permitted = [files["releases/" + active + "/payload/" + launcher_name]]
        if pending and pending["plan"]["candidate_release"]["id"] in releases:
            permitted.append(files["releases/" + pending["plan"]["candidate_release"]["id"] + "/payload/" + launcher_name])
        window = binding["active_release"]["inventory_id"]
        mode_admitted = window == "windows-2" or bool(launcher.stat().st_mode & stat.S_IXUSR)
        detail = "launcher differs from permitted release or is not executable"
        if sys.platform == "win32" and launcher_bytes in permitted and not mode_admitted:
            detail = (f"historical {window} executable-bit observation is unavailable on native Windows; "
                      "old-window mutation is unsupported; preserve target")
        _serial_require(launcher_bytes in permitted and mode_admitted, detail)
        if chain[index]["plan"]["remove"]:
            _serial_require(stat.S_IMODE(launcher.lstat().st_mode) == 0o755,
                            "completed transition entry mode differs; preserve B1")
    _visible_truth(target, [".hrn/format.json", ".hrn/.gitignore", launcher_name] +
                   (["colvia"] if crossing else []) + [".hrn/product/" + p for p in files])
    return {"binding_ref": record_ref(binding, "operation_id"), "binding": binding,
            "launcher_sha256": sha256_bytes(launcher_bytes) if launcher_bytes is not None else None,
            "release_path": str(product / "releases" / active), "inventory": releases[active]["inventory"],
            "pending": pending, "history": chain, "bindings": bindings,
            "observation": {p: sha256_bytes(data) for p, data in files.items()}, "repair_files": actual,
            "entry_transition": entry_transition}


def verify_workspace_product(target: Path) -> dict[str, Any]:
    """Read-only complete applied lifecycle history; pending is never active."""
    observed = _workspace_observe(target)
    return {key: observed[key] for key in ("binding_ref","launcher_sha256","release_path","inventory")}


def require_workspace_runtime(target: Path) -> dict[str, Any]:
    """Default writer gate: isolated control launcher and exact loaded payload.

This verifies trusted-local path/digest provenance, not protection from a malicious
process modifying Python objects or undetectable manual edits between observations.
"""
    from .workspace import classify_target, require_supported_runtime
    observed = verify_workspace_product(target)
    window = observed["inventory"]["inventory_id"]
    _serial_require(window in ("continuation-1", "windows-2"), "new installed runtime requires a supported bound window")
    require_supported_runtime(window)
    target = Path(classify_target(target, mutation=True)["target"])
    _serial_require(sys.flags.isolated == 1 and sys.dont_write_bytecode,
                    "writer must use isolated Python startup without bytecode writes")
    main = sys.modules.get("__main__")
    main_path = getattr(main, "__file__", None)
    _serial_require(isinstance(main_path, str) and Path(main_path).absolute() == target / "colvia"
                    and Path(main_path).resolve() == target / "colvia", "executing launcher is not the control launcher")
    payload = Path(observed["release_path"]) / "payload"
    package = payload / "src/hv2ref"
    entries = {entry["path"]: entry for entry in observed["inventory"]["entries"]}
    loaded = [(name, module) for name, module in list(sys.modules.items())
              if name == "hv2ref" or name.startswith("hv2ref.")]
    _serial_require(bool(loaded), "runtime package is not loaded")
    for name, module in loaded:
        relative = "src/hv2ref/" + ("__init__.py" if name == "hv2ref" else name[7:].replace(".", "/") + ".py")
        _serial_require(relative in entries, "unmanaged runtime module: " + name)
        expected = payload / relative
        path = getattr(module, "__file__", None)
        spec = getattr(module, "__spec__", None)
        _serial_require(isinstance(path, str) and Path(path).absolute() == expected
                        and Path(path).resolve() == expected
                        and getattr(spec, "origin", None) == str(expected), "module outside bound payload: " + name)
        _serial_require(sha256_bytes(_serial_file(expected)) == entries[relative]["sha256"],
                        "executing module digest changed: " + name)
        if name == "hv2ref":
            _serial_require(list(getattr(module, "__path__", [])) == [str(package)]
                            and list(getattr(spec, "submodule_search_locations", []) or []) == [str(package)],
                            "package search path escaped bound payload")
    _serial_require(observed == verify_workspace_product(target), "product changed during runtime verification")
    return {**{key: observed[key] for key in ("binding_ref", "launcher_sha256")}, "inventory_id": observed["inventory"]["inventory_id"]}


def workspace_init_preview(source: Path, target: Path, *, authority_home_id: str, operation_id: str, created_at: str) -> dict[str, Any]:
    from .workspace import classify_target, target_fingerprint, validate_format, _validate_init_plan, require_supported_runtime
    candidate = workspace_candidate(source)
    require_supported_runtime(candidate["release_ref"]["inventory_id"])
    target = Path(classify_target(target, mutation=True)["target"])
    fmt = validate_format({"record_type": "workspace-format", "format_version": 1,
                           "authority_home_id": authority_home_id, "created_at": created_at, "lineage": None})
    plan = {"record_type": "lifecycle-plan", "schema_version": 6 if candidate["release_ref"]["inventory_id"] == "windows-2" else 5, "operation_id": operation_id, "action": "init",
            "authority_home_id": authority_home_id, "expected_binding_ref": None, "candidate_release": candidate["release_ref"],
            "format_sha256": sha256_bytes(canonical_json_bytes(fmt)), "truth_refs": [], "remove": [], "preserve": [],
            "created_at": created_at, "target_fingerprint": target_fingerprint(target)}
    _validate_init_plan(plan, fmt, target)
    request = {"format": fmt, "plan": plan}
    _workspace_init_preflight(target, request, candidate, recover=False)
    return {"classification": "preview", "request": request, "confirm_token": sha256_bytes(canonical_json_bytes(request))[:16]}


def _init_binding_receipt(request: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    from .work import record_ref
    plan = request["plan"]
    binding = {"record_type": "product-binding", "schema_version": 1, "authority_home_id": plan["authority_home_id"],
               "active_release": plan["candidate_release"], "prior_release": None, "operation_id": plan["operation_id"]}
    receipt = {"record_type": "lifecycle-receipt", "schema_version": plan["schema_version"], "operation_id": plan["operation_id"],
               "plan": plan, "prior_binding_ref": None, "result_binding_ref": record_ref(binding, "operation_id")}
    return binding, receipt


def _init_partial_tree(root: Path, expected: dict[str, bytes]) -> set[str]:
    """Inspect a subset of owned exact bytes; no deletion or repair inference."""
    from .workspace import _require_kind
    dirs = {parent.as_posix() for name in expected for parent in Path(name).parents if str(parent) != "."}
    seen: set[str] = set()
    _require_kind(root, True)
    pending = [root]
    while pending:
        directory = pending.pop()
        for member in directory.iterdir():
            name = member.relative_to(root).as_posix()
            if name in dirs:
                _require_kind(member, True); pending.append(member)
            else:
                _serial_require(name in expected, "unowned init member: " + name)
                _require_kind(member, False)
                _serial_require(_serial_file(member) == expected[name], "torn or changed init bytes: " + name)
                seen.add(name)
    return seen


def _workspace_init_preflight(target: Path, request: dict[str, Any], candidate: dict[str, Any], *, recover: bool) -> str:
    from .workspace import _exists, _require_kind, _root_aliases, _file_json, inspect_root
    root = target / ".hrn"
    window = candidate["release_ref"]["inventory_id"]
    _serial_require(window in ("continuation-1", "windows-2") and request["plan"]["schema_version"] == (6 if window == "windows-2" else 5), "new init requires the exact current schema/window pair")
    _serial_require(not _root_aliases(target), "workspace root alias")
    _serial_require(not any(p.name.casefold().startswith(".harness-v2") for p in target.iterdir()), "old homes require a fresh target")
    if not _exists(root):
        _serial_require(not recover, "cannot recover an absent root")
        _refuse_retired_entry(target, "fresh continuation-1 init")
        _entry_absence_admission(target)
        return "fresh"
    _require_kind(root, True)
    _serial_require(_exists(root / "product"), "no durable ownership plan; preserve existing root")
    _require_kind(root / "product", True)
    plan_path = root / "product/init-plan.json"
    _serial_require(_exists(plan_path), "no durable ownership plan; preserve existing root")
    _serial_require(_file_json(plan_path) == request["plan"] and _serial_file(plan_path) == canonical_json_bytes(request["plan"]), "different initialization plan")
    fmt = root / "format.json"
    if _exists(fmt): _serial_require(_serial_file(fmt) == canonical_json_bytes(request["format"]), "different format bytes")
    if _exists(root / "product/binding.json"):
        observed = verify_workspace_product(target)
        _serial_require(observed["inventory"]["inventory_id"] == window, "completed init has another live window")
        _refuse_retired_entry(target, "exact completed-init replay; historical completion preserved")
        return "complete"
    _serial_require(recover, "partial init requires explicit exact recovery")
    state = inspect_root(target)["classification"]
    _serial_require(state in {"root-ready", "partial-candidate"}, "root is not an exact initialization prefix")
    _entry_absence_admission(target, owned_prefix=True)
    for category in ("intents", "work", "planning"):
        path = root / category
        if _exists(path):
            _require_kind(path, True)
            _serial_require(not any(path.iterdir()), "truth present before init binding")
    _, receipt = _init_binding_receipt(request)
    rid = candidate["release_ref"]["id"]
    relprefix = "releases/" + rid + "/"
    expected = {"init-plan.json": canonical_json_bytes(request["plan"]),
                "receipts/" + request["plan"]["operation_id"] + ".json": canonical_json_bytes(receipt),
                relprefix + "inventory.json": canonical_json_bytes(candidate["inventory"])}
    expected.update({relprefix + "payload/" + p: b for p, b in candidate["payload"].items()})
    seen = _init_partial_tree(root / "product", expected)
    release = root / "product/releases" / rid
    if _exists(release):
        _serial_require(verify_workspace_release(release)["release_ref"] == candidate["release_ref"], "published release is incomplete")
    receipt_path = root / "product/receipts" / (request["plan"]["operation_id"] + ".json")
    if _exists(receipt_path): _serial_require(_exists(release), "receipt before immutable release")
    if _exists(target / "colvia"):
        _serial_require(_exists(receipt_path), "launcher without durable init receipt")
        _serial_require(_serial_file(target / "colvia") == candidate["payload"]["colvia"], "changed launcher; preserve")
    if state == "partial-candidate":
        _serial_require(seen == {"init-plan.json"} and not _exists(target / "colvia"), "product published before root completion")
    _refuse_retired_entry(target, "exact continuation-1 init recovery")
    return state


def workspace_init_apply(source: Path, target: Path, request: dict[str, Any], *, confirm_token: str, recover: bool = False, inject_at: str | None = None) -> dict[str, Any]:
    from .workspace import classify_target, validate_format, _validate_init_plan, bootstrap_root, writer_guard, _exists, _durable_directory, _write_exact, require_supported_runtime
    from .work import _visible_truth
    from .jsonio import windows_preflight_files, sync_existing_file
    candidate = workspace_candidate(source)
    require_supported_runtime(candidate["release_ref"]["inventory_id"])
    points = {None, "after-root", "after-product-dir", "after-plan", "after-format", "after-ignore", "after-intents", "after-work",
              "after-staged-inventory", "after-staged-payload", "after-release", "after-receipt", "after-launcher-bytes", "after-launcher", "after-binding"}
    _serial_require(inject_at in points, "unknown init crash point")
    request = _exact_dict(request, {"format", "plan"}, "HV2-WORKSPACE-INIT")
    # Validate canonical JSON limits before writing any part of the request.
    raw = canonical_json_bytes(request); decode_json_bytes(raw, require_canonical=True)
    _serial_require(isinstance(confirm_token, str) and confirm_token == sha256_bytes(raw)[:16], "init confirmation token mismatch")
    target = Path(classify_target(target, mutation=True)["target"])
    fmt = validate_format(request["format"]); _validate_init_plan(request["plan"], fmt, target)
    _serial_require(candidate == workspace_candidate(source), "source changed during init admission")
    _serial_require(candidate["release_ref"] == request["plan"]["candidate_release"], "source changed since init preview")
    root = target / ".hrn"; plan = request["plan"]; rid = candidate["release_ref"]["id"]
    planned = [".hrn/format.json", ".hrn/.gitignore", ".hrn/product/init-plan.json", ".hrn/product/binding.json", "colvia",
               ".hrn/product/receipts/" + plan["operation_id"] + ".json", ".hrn/product/releases/" + rid + "/inventory.json"]
    planned += [".hrn/product/releases/" + rid + "/payload/" + p for p in CONTINUATION_MANAGED_PATHS]
    _visible_truth(target, planned)
    state = _workspace_init_preflight(target, request, candidate, recover=recover)
    if state == "complete": return {"classification": "initialized", "replayed": True, "product": verify_workspace_product(target)}
    def native_preflight():
        staged = root / "staging" / ("init-" + plan["operation_id"]) / rid
        paths = [target / name for name in planned]
        paths += [staged / "inventory.json", root / "locks/writer.lock"]
        paths += [staged / "payload" / name for name in CONTINUATION_MANAGED_PATHS]
        windows_preflight_files(paths)
    native_preflight()
    bootstrap_points = {"after-root", "after-product-dir", "after-plan", "after-format", "after-ignore", "after-intents", "after-work"}
    if state in {"fresh", "partial-candidate"}:
        bootstrap_root(target, plan, fmt, recover=state != "fresh", inject_at=inject_at if inject_at in bootstrap_points else None)
    with writer_guard(target):
        # Once root ownership exists, every resume is checked under the common guard.
        state = _workspace_init_preflight(target, request, candidate, recover=True)
        if state == "complete": return {"classification": "initialized", "replayed": True, "product": verify_workspace_product(target)}
        native_preflight()
        _visible_truth(target, planned)
        product = root / "product"; release = product / "releases" / rid
        if not _exists(release):
            _durable_directory(root / "staging")
            staging = root / "staging" / ("init-" + plan["operation_id"])
            _durable_directory(staging)
            staged = staging / rid; _durable_directory(staged)
            expected = {"inventory.json": canonical_json_bytes(candidate["inventory"])} | {"payload/" + p: b for p, b in candidate["payload"].items()}
            _init_partial_tree(staged, expected)
            for name, data in expected.items():
                path = staged / name
                for parent in reversed(path.relative_to(staged).parents): _durable_directory(staged / parent)
                _write_exact(path, data)
                if name == "inventory.json" and inject_at == "after-staged-inventory": raise InjectedCrash(inject_at)
            if inject_at == "after-staged-payload": raise InjectedCrash(inject_at)
            _serial_require(verify_workspace_release(staged)["release_ref"] == candidate["release_ref"], "staged release mismatch")
            _durable_directory(product / "releases")
            rename_directory(staged, release); sync_directory(release.parent); sync_directory(staging)
        elif plan["schema_version"] == 6:
            # Resume a visible publication before any later receipt; retain
            # common directory-sync policy, including permitted unavailable.
            sync_directory(release.parent)
            staging = root / "staging" / ("init-" + plan["operation_id"])
            if _exists(staging): sync_directory(staging)
        if inject_at == "after-release": raise InjectedCrash(inject_at)
        binding, receipt = _init_binding_receipt(request)
        _durable_directory(product / "receipts")
        _write_exact(product / "receipts" / (plan["operation_id"] + ".json"), canonical_json_bytes(receipt))
        if inject_at == "after-receipt": raise InjectedCrash(inject_at)
        _write_exact(target / "colvia", candidate["payload"]["colvia"])
        if inject_at == "after-launcher-bytes": raise InjectedCrash(inject_at)
        if candidate["release_ref"]["inventory_id"] != "windows-2":
            (target / "colvia").chmod(0o755)
        sync_existing_file(target / "colvia")
        sync_directory(target)
        if inject_at == "after-launcher": raise InjectedCrash(inject_at)
        _write_exact(product / "binding.json", canonical_json_bytes(binding))
        if inject_at == "after-binding": raise InjectedCrash(inject_at)
        return {"classification": "initialized", "replayed": False, "product": verify_workspace_product(target)}


def workspace_status(target: Path) -> dict[str, Any]:
    """Read-only diagnostics; pending product/truth never becomes a healthy pass."""
    return _workspace_status_observation(target)[0]


def _workspace_status_observation(target: Path, *, _share_intents: bool = True) -> tuple[dict[str, Any], tuple[dict, dict] | None]:
    """Keep healthy status and its graphs within one read-only observation."""
    from .workspace import classify_target, inspect_root, _exists, runtime_supported, SUPPORTED_PYTHON_STRINGS, SUPPORTED_PYTHON_TEXT, _TopologyObservation
    from .work import WorkStore
    from .intent import workspace_intents
    topology = classify_target(target); target = Path(topology["target"])
    root = inspect_root(target)
    if root["classification"] == "detach-candidate":
        try:
            result = workspace_detached_status(target)
            next_action = ("preserve remaining files; use the exact original detach request and confirmation token with --recover from an independent trusted source"
                           if result["classification"] == "partial" else
                           "read retained project truth with an independent trusted source; no active product runtime remains")
            if result["classification"] == "partial" and result["receipt"]["plan"]["schema_version"] in (1, 2, 3, 4):
                next_action = "preserve remaining files; use the exact original detach request and confirmation token with --recover from the retained matching OLD source; do not use the current continuation-1 source"
            return {**result, "topology":topology["kind"], "authoritative_control":False, "next_action":next_action}, None
        except ContractError as exc:
            return {"classification":"degraded", "error_code":exc.code, "message":exc.message, "topology":topology["kind"]}, None
    if root["classification"] != "root-ready":
        classification = {"partial-candidate":"partial", "detach-candidate":"partial", "integrity-failure":"degraded", "unrecognized":"degraded", "unstable":"degraded"}.get(root["classification"], root["classification"])
        status = {**root, "root_classification":root["classification"], "classification":classification, "topology":topology["kind"]}
        if root["classification"] == "partial-candidate":
            status["next_action"] = "use an independent trusted source matching the candidate release in the exact original init request and confirmation token; for an OLD pending init, use the retained matching OLD source, not the current continuation-1 source; unknown/torn bytes require manual preservation"
        return status, None
    if not _exists(target / ".hrn/product/binding.json"):
        return {"classification": "partial", "product_verification": "incomplete", "topology": topology["kind"],
                "next_action": "use an independent trusted source matching the candidate release in the exact original init request and confirmation token; for an OLD pending init, use the retained matching OLD source, not the current continuation-1 source; unknown/torn bytes require manual preservation"}, None
    try:
        state = _workspace_observe(target, allow_pending=True)
        if state["pending"] is not None:
            next_action = "recover exact lifecycle request from independent trusted source; receipt alone is not completion"
            if state["pending"]["plan"]["candidate_release"]["inventory_id"] not in ("continuation-1", "windows-2"):
                next_action = "preserve pending lifecycle bytes; recover only the exact original lifecycle request and confirmation token with the retained matching OLD source for its candidate release; do not use the current source; receipt alone is not completion"
            return {"classification":"partial", "topology":topology["kind"],
                    "pending_lifecycle":state["pending"]["operation_id"], "binding_ref":state["binding_ref"],
                    "next_action":next_action}, None
        product = verify_workspace_product(target)
        observed_intents = {}
        topology_observation = _TopologyObservation(target) if _share_intents and topology["kind"] == "primary" else None
        def intent_graph(intent_id):
            from .intent import read_workspace_intent_graph
            if intent_id not in observed_intents:
                observed_intents[intent_id] = (read_workspace_intent_graph(target, intent_id) if topology_observation is None else
                                               read_workspace_intent_graph(target, intent_id, _topology_observation=topology_observation))
            return observed_intents[intent_id]
        # Only this read-only sweep shares graphs/raw probes; writers stay fresh.
        # A damaged continuation must not erase a verified base Work lifecycle.
        continuation_errors = {}
        try:
            if topology_observation is not None:
                works = WorkStore(target)._all(_intent_graph_reader=intent_graph, _topology_observation=topology_observation,
                                               _continuation_errors=continuation_errors)
                topology_observation.finish()
            else:
                works = (WorkStore(target)._all(_intent_graph_reader=intent_graph, _continuation_errors=continuation_errors)
                         if _share_intents else WorkStore(target)._all(_continuation_errors=continuation_errors))
        finally:
            if topology_observation is not None:
                topology_observation.close()
        intents = workspace_intents(target)  # Independent final read, never the shared getter.
        _serial_require(all(intents.get(key) == graph for key, graph in observed_intents.items()),
                        "unstable intent observation")
        from .candidates import read_candidates
        try:
            observed_planning = read_candidates(target)
            planning = {"available": True, "present": observed_planning["present"], "sha256": observed_planning["sha256"],
                        "candidate_count": len(observed_planning["store"]["candidates"]), "selected": observed_planning["store"]["selected"],
                        "selection_semantics": "recorded planning choice; not Work readiness or execution authority", "execution_authority": False}
        except ContractError as exc:
            planning = {"available": False, "error_code": exc.code, "message": exc.message, "execution_authority": False,
                        "next_action": "preserve planning bytes; unavailable is not empty; inspect with an independent trusted source"}
        pending_work = [key for key, graph in works.items() if graph["pending_decisions"] or graph["pending_selections"]]
        pending_intent = [key for key, graph in intents.items() if graph["pending_acceptances"] or graph["pending_selections"]]
        pending_continuation = [key for key, graph in works.items()
                                if graph["continuation"] is not None and graph["continuation"]["pending"]]
        documentation_root = (Path(product["release_path"]) / "payload/docs").relative_to(target).as_posix()
        next_action = "read " + documentation_root + "/README.md"
        supported = runtime_supported(product["inventory"]["inventory_id"])
        if not supported:
            next_action = f"use final GIL-enabled CPython {SUPPORTED_PYTHON_TEXT} before mutation; " + next_action
        pending_publish = any(graph["selections"][key]["decision_ref"] is None
                              for graph in works.values() for key in graph["pending_selections"])
        pending_apply = bool(pending_intent) or any(graph["pending_decisions"] or
                            any(graph["selections"][key]["decision_ref"] is not None for key in graph["pending_selections"])
                            for graph in works.values())
        if pending_apply:
            next_action = "preserve pending decision; resume apply with the exact original ticket and confirmation token after prerequisites are restored; " + next_action
        if pending_publish:
            next_action = "preserve pending publication; retry the exact original publish request after prerequisites are restored; " + next_action
        if pending_continuation:
            next_action = "preserve pending continuation; resume the exact pending ticket; an already pending cancellation may only resume that cancellation; explicitly cancel only an unresolved normal choice; all other writes except exact active repair are blocked; " + next_action
        status = {"classification": "partial" if pending_work or pending_intent or pending_continuation or not planning["available"] else ("pass" if supported else "unsupported"), "topology": topology["kind"],
                "authoritative_control": topology["kind"] in {"primary", "non-git"}, "product": product,
                "documentation_root": documentation_root, "next_action": next_action,
                "pending_work": pending_work, "pending_intent": pending_intent,
                "pending_continuation": pending_continuation,
                "continuation_usage": {key: (dict(graph["continuation"]["usage"]) if graph["continuation"] is not None else None)
                                       for key, graph in works.items()},
                "work_states": {key: graph["state"] for key, graph in works.items()}, "intent_count": len(intents),
                "planning": planning,
                "runtime": {"implementation": sys.implementation.name, "python": ".".join(map(str, sys.version_info[:3])), "supported_baseline": SUPPORTED_PYTHON_STRINGS[0], "supported_versions": list(SUPPORTED_PYTHON_STRINGS), "required_releaselevel": "final", "free_threaded_supported": False,
                            "supported": supported}}
        if continuation_errors:
            status.update(classification="degraded", lifecycle_ready=False,
                          continuation_unavailable={key: dict(value) for key, value in continuation_errors.items()},
                          pending_continuation=None,
                          next_action="preserve unavailable continuation records; all official writes including repair and detach are blocked; " + next_action)
        if status["classification"] == "pass" and product["inventory"]["inventory_id"] in ("entry-1", "delegation-1", "continuation-1", "windows-2"):
            collision = _retired_entry_collision(target)
            if collision is not None:
                status.update(classification="conflict", lifecycle_ready=False, retired_entry_collision=collision,
                              next_action="preserve retired entry occupants " + repr(collision["observed_names"]) +
                                          "; a separate operator decision is required before lifecycle mutation; " + next_action)
        if _share_intents and status["classification"] != "pass":
            return _workspace_status_observation(target, _share_intents=False)
        return status, (works, intents) if status["classification"] == "pass" or continuation_errors else None
    except ContractError as exc:
        if _share_intents:
            return _workspace_status_observation(target, _share_intents=False)
        return {"classification": "degraded", "error_code": exc.code, "message": exc.message, "topology": topology["kind"]}, None

def _workspace_observe(target: Path, *, allow_pending: bool = False, repair_candidate: dict[str, Any] | None = None) -> dict[str, Any]:
    from .workspace import classify_target
    target = Path(classify_target(target)["target"])
    try:
        first = _workspace_product_once(target, allow_pending=allow_pending, repair_candidate=repair_candidate)
        _serial_require(first == _workspace_product_once(target, allow_pending=allow_pending, repair_candidate=repair_candidate), "unstable product history")
        return first
    except (OSError, ValueError, RecursionError) as exc:
        raise ContractError("HV2-WORKSPACE-PRODUCT", "product unavailable, malformed or unstable") from exc


def _lifecycle_truth(target: Path, *, allow_pending: bool = False, _topology_observation=None) -> list[dict[str, str]]:
    from .workspace import _exists, _require_kind
    from .work import WorkStore, _visible_truth
    from .intent import workspace_intents
    root = target / ".hrn"
    for kind in ("intents", "work"):
        if _exists(root/kind): _require_kind(root/kind, True)
    if _topology_observation is None:
        works = WorkStore(target)._all(); intents = workspace_intents(target)
    else:
        from .intent import read_workspace_intent_graph
        def read_intent(intent_id):
            return read_workspace_intent_graph(target, intent_id, _topology_observation=_topology_observation)
        works = WorkStore(target)._all(_intent_graph_reader=read_intent, _topology_observation=_topology_observation)
        intents = workspace_intents(target, _graph_reader=read_intent)
    if not allow_pending:
        from .continuation import require_no_pending
        require_no_pending(target, works=works)
    _serial_require(allow_pending or not any(g["pending_decisions"] or g["pending_selections"] for g in works.values()), "pending Work blocks lifecycle")
    _serial_require(allow_pending or not any(g["pending_acceptances"] or g["pending_selections"] for g in intents.values()), "pending intent blocks lifecycle")
    result = []
    stack = [root/k for k in ("intents","work") if _exists(root/k)]
    while stack:
        directory = stack.pop(); _require_kind(directory, True)
        for p in directory.iterdir():
            if stat.S_ISDIR(p.lstat().st_mode): stack.append(p)
            else:
                _require_kind(p, False)
                result.append({"path":p.relative_to(root).as_posix(),"sha256":sha256_bytes(_serial_file(p))})
    from .candidates import read_candidates
    planning = read_candidates(target)
    if planning["present"]: result.append({"path": "planning/candidates.json", "sha256": planning["sha256"]})
    result.sort(key=lambda r:r["path"].encode())
    if _topology_observation is None:
        _visible_truth(target, [".hrn/"+r["path"] for r in result])
    else:
        _visible_truth(target, [".hrn/"+r["path"] for r in result], _topology_observation=_topology_observation)
    return result


DELEGATION_PREDECESSOR = {
    "id": "product-release-2216a2634eb3fa5d6a8bfa7c",
    "sha256": "2216a2634eb3fa5d6a8bfa7c7d4847b29fb2443ba7b367156c15b15ddb5a17e0",
    "inventory_id": "entry-1",
}


def _delegation_admission(target: Path, state: dict[str, Any], *, pending: bool = False) -> None:
    from .intent import workspace_intents
    window = state["binding"]["active_release"]["inventory_id"]
    _serial_require(window in ("entry-1", "delegation-1"), "delegation switch requires an admitted predecessor")
    _refuse_retired_entry(target, "delegation lifecycle")
    if window == "entry-1":
        _serial_require(state["binding"]["active_release"] == DELEGATION_PREDECESSOR,
                        "delegation predecessor is not the audited entry-1 release")
        _serial_require(not any(d["schema_version"] == 3 for g in workspace_intents(target).values()
                                for d in g["drafts"].values()), "schema3 truth in an entry-1 home is unsupported")
    _serial_require(pending or state["pending"] is None, "old pending lifecycle requires retained old source")



CONTINUATION_PREDECESSOR = {
    "id": "product-release-d71214aa37687189ebf12c51",
    "sha256": "d71214aa37687189ebf12c517874016e2d50622b0fbd21d3e5b971df9ec59262",
    "inventory_id": "delegation-1",
}


def _continuation_admission(target: Path, state: dict[str, Any], *, pending: bool = False) -> None:
    window = state["binding"]["active_release"]["inventory_id"]
    _serial_require(window in ("delegation-1", "continuation-1"), "continuation switch requires an admitted predecessor")
    _refuse_retired_entry(target, "continuation lifecycle")
    if window == "delegation-1":
        _serial_require(state["binding"]["active_release"] == CONTINUATION_PREDECESSOR,
                        "continuation predecessor is not the exact qualified delegation-1 release")
        from .work import WorkStore
        _serial_require(not any(g["continuation"]["data"] for g in WorkStore(target)._all().values()),
                        "continuation truth in a delegation-1 home is unsupported")
    _serial_require(pending or state["pending"] is None, "old pending lifecycle requires retained old source")


def _current_switch_admission(target: Path, state: dict[str, Any], *, pending: bool = False) -> None:
    from .workspace import require_supported_runtime
    window = state["binding"]["active_release"]["inventory_id"]
    require_supported_runtime(window)
    if window == "windows-2":
        _serial_require(all(b["active_release"]["inventory_id"] == window for b in state["bindings"]),
                        "Windows lifecycle cannot contain another window")
        _refuse_retired_entry(target, "Windows same-window lifecycle")
        _serial_require(pending or state["pending"] is None, "pending lifecycle requires exact recovery")
    else:
        _continuation_admission(target, state, pending=pending)


def workspace_switch_preview(target: Path, *, action: str, source: Path | None, operation_id: str,
                             created_at: str, to_release_id: str | None = None, installed: bool = False) -> dict[str, Any]:
    from .workspace import classify_target, _file_json, target_fingerprint
    target = Path(classify_target(target, mutation=True)["target"])
    if installed: require_workspace_runtime(target)
    state = _workspace_observe(target); binding = state["binding"]
    _serial_require(action in ("update", "rollback"), "unsupported lifecycle action")
    _current_switch_admission(target, state)
    if action == "update":
        _serial_require(source is not None and to_release_id is None, "update requires source only")
        candidate = workspace_candidate(source)["release_ref"]
    else:
        _serial_require(source is None and binding["prior_release"] is not None, "no recorded rollback release")
        candidate = binding["prior_release"]
        _serial_require(to_release_id is None or to_release_id == candidate["id"], "rollback target is not previous release")
    expected_window = "windows-2" if binding["active_release"]["inventory_id"] == "windows-2" else "continuation-1"
    _serial_require(candidate["inventory_id"] == expected_window, "source switch cannot cross the Windows boundary or downgrade an old semantic window")
    fmt = _file_json(target / ".hrn/format.json"); truth = _lifecycle_truth(target)
    plan = {"record_type": "lifecycle-plan", "schema_version": 6 if expected_window == "windows-2" else 5, "operation_id": operation_id, "action": action,
            "authority_home_id": fmt["authority_home_id"], "expected_binding_ref": state["binding_ref"], "candidate_release": candidate,
            "format_sha256": sha256_bytes(canonical_json_bytes(fmt)), "truth_refs": truth, "remove": [], "preserve": [],
            "created_at": created_at, "target_fingerprint": target_fingerprint(target)}
    _switch_plan_shape(plan, fmt)
    result_binding, receipt = _switch_binding_receipt(plan, binding)
    _lifecycle_output_bytes(plan, "plan"); _lifecycle_output_bytes(result_binding, "binding"); _lifecycle_output_bytes(receipt, "receipt")
    _serial_require(all(r["operation_id"].casefold() != operation_id.casefold() for r in state["history"]), "operation id already used")
    _serial_require(state == _workspace_observe(target) and truth == _lifecycle_truth(target), "preview changed while reading")
    _current_switch_admission(target, state)
    return {"classification": "preview", "request": plan, "confirm_token": sha256_bytes(canonical_json_bytes(plan))[:16],
            "transition_notice": ("windows-2 admits same-window lifecycle only. Retain the exact source/request for recovery; older source and cross-window rollback are refused." if expected_window == "windows-2" else "continuation-1 is one-way after the first schema-5 receipt. Retain the exact new source/request for forward recovery; older source and old-window rollback are refused. Same-window rollback needs a qualified compatible release.")}


def _switch_read_scope(root: Path):
    from contextlib import nullcontext
    from .jsonio import _windows_detach_read_scope
    # One read-only phase; all leaf reads remain fresh and ancestors are
    # independently re-opened before the next phase or publication.
    return _windows_detach_read_scope(root) if sys.platform == "win32" else nullcontext()


def _switch_preflight(target: Path, plan: dict[str, Any], *, recover: bool) -> tuple[dict[str, Any], bool]:
    from .work import _lifecycle_git_observation
    # Reuse only ancestors within this read-only preflight, never leaf bytes or
    # results across checkpoints. The existing scope independently reopens all
    # shared ancestors before returning, and is closed before any publication.
    with _switch_read_scope(target), _lifecycle_git_observation(target):
        return _switch_preflight_records(target, plan, recover=recover)


def _switch_preflight_records(target: Path, plan: dict[str, Any], *, recover: bool) -> tuple[dict[str, Any], bool]:
    _serial_require((plan["schema_version"], plan["candidate_release"]["inventory_id"]) in ((5, "continuation-1"), (6, "windows-2")),
                    "new source switches only exact current schema/window pairs; use retained source for old pending operations")
    state = _workspace_observe(target, allow_pending=True)
    _current_switch_admission(target, state, pending=True)
    matching = [r for r in state["history"] if r["operation_id"] == plan["operation_id"]]
    _serial_require(not any(r["operation_id"] != plan["operation_id"] and r["operation_id"].casefold() == plan["operation_id"].casefold() for r in state["history"]), "operation id case alias")
    if matching:
        _serial_require(canonical_json_bytes(matching[0]["plan"]) == canonical_json_bytes(plan), "operation id reused with another plan")
        if matching[0] != state["pending"]:
            _serial_require(state["pending"] is None, "another lifecycle is pending")
            return state, True
    if state["pending"]:
        _serial_require(recover and state["pending"]["plan"] == plan, "pending lifecycle requires same explicit recovery")
    else:
        _serial_require(not recover, "no pending lifecycle to recover")
    _serial_require(state["binding_ref"] == plan["expected_binding_ref"], "binding changed since preview")
    _switch_binding_receipt(plan, state["binding"])
    _serial_require(_lifecycle_truth(target) == plan["truth_refs"], "truth changed since lifecycle preview")
    return state, False


def _replace_product_file(target: Path, destination: Path, data: bytes, *, executable: bool) -> None:
    from .workspace import _durable_directory, _require_kind
    from .jsonio import _sync_fd, replace_file, windows_preflight_files
    import tempfile
    windows_preflight_files([destination, target / ".hrn/staging"])
    staging = target/".hrn/staging"; _durable_directory(staging); _require_kind(staging, True)
    _require_kind(destination, False)
    fd,name = tempfile.mkstemp(prefix="product-replace-",dir=staging); staged = Path(name)
    with os.fdopen(fd,"wb") as handle:
        handle.write(data); handle.flush()
        if sys.platform != "win32":
            os.fchmod(handle.fileno(),0o755 if executable else stat.S_IMODE(destination.stat().st_mode) & 0o777)
        _sync_fd(handle.fileno())
    if sys.platform == "win32":
        sync_directory(staging)
        replace_file(staged, destination)
        sync_directory(destination.parent); sync_directory(staging)
    else:
        _entry_sync(target, staging, phase="publication", role="replacement-staging")
        replace_file(staged, destination)
        _entry_sync(target, destination.parent, phase="publication", role="replacement-parent", b1=not executable)
        _entry_sync(target, staging, phase="publication", role="replacement-staging", b1=not executable)


def workspace_switch_apply(target: Path, plan: dict[str, Any], *, confirm_token: str, source: Path | None = None,
                           recover: bool = False, inject_at: str | None = None, installed: bool = False) -> dict[str, Any]:
    from .workspace import classify_target, _file_json, target_fingerprint, writer_guard, _exists, _durable_directory, _write_exact, require_supported_runtime, _require_kind
    from .work import _visible_truth
    points = {None, "after-receipt", "after-staged-inventory", "after-staged-payload", "after-release", "after-launcher", "after-binding"}
    _serial_require(inject_at in points, "unknown lifecycle crash point")
    raw = canonical_json_bytes(plan); decode_json_bytes(raw, require_canonical=True)
    _serial_require(isinstance(confirm_token, str) and confirm_token == sha256_bytes(raw)[:16], "lifecycle confirmation mismatch")
    target = Path(classify_target(target, mutation=True)["target"])
    _require_kind(target / ".hrn", True)
    _switch_plan_shape(plan, _file_json(target / ".hrn/format.json"))
    require_supported_runtime(plan["candidate_release"]["inventory_id"])
    _serial_require(plan["target_fingerprint"] == target_fingerprint(target), "lifecycle target changed")
    if installed:
        _serial_require(not recover, "lifecycle recovery requires independent source")
        with _switch_read_scope(target):
            require_workspace_runtime(target)
    candidate = None
    if source is not None:
        with _switch_read_scope(source):
            candidate = workspace_candidate(source)
    _serial_require((plan["action"] == "update") == (candidate is not None), "update requires exact source; rollback uses retained release")
    if candidate: _serial_require(candidate["release_ref"] == plan["candidate_release"], "candidate changed since preview")
    state, done = _switch_preflight(target, plan, recover=recover)
    if done:
        if not plan["remove"] and plan["schema_version"] not in (4, 5, 6):
            return _entry_replay_result(target, plan, classification="replayed")
        with writer_guard(target):
            if installed:
                with _switch_read_scope(target):
                    require_workspace_runtime(target)
            state, done = _switch_preflight(target, plan, recover=recover)
            _serial_require(done, "completed lifecycle changed before replay")
            return _entry_replay_result(target, plan, classification="replayed")
    rid = plan["candidate_release"]["id"]; root = target / ".hrn"; product = root / "product"
    planned = ["colvia", ".hrn/product/binding.json", ".hrn/product/receipts/" + plan["operation_id"] + ".json",
               ".hrn/product/releases/" + rid + "/inventory.json"] + [".hrn/product/releases/" + rid + "/payload/" + p for p in CONTINUATION_MANAGED_PATHS]
    _visible_truth(target, planned)
    def native_preflight():
        from .jsonio import windows_preflight_files
        if sys.platform != "win32": return
        release = product / "releases" / rid
        paths = [product / "binding.json", product / "receipts" / (plan["operation_id"] + ".json"), root / "locks/writer.lock"]
        launcher = candidate["payload"]["colvia"] if candidate else _serial_file(release / "payload/colvia")
        if _serial_file(target / "colvia") != launcher:
            paths.append(target / "colvia")
        if not _exists(release):
            staged = root / "staging" / ("switch-" + plan["operation_id"]) / rid
            paths += [staged / "inventory.json", release]
            paths += [staged / "payload" / name for name in CONTINUATION_MANAGED_PATHS]
        windows_preflight_files(paths)
    native_preflight()
    with writer_guard(target):
        if installed:
            with _switch_read_scope(target):
                require_workspace_runtime(target)
        state, done = _switch_preflight(target, plan, recover=recover)
        if done: return _entry_replay_result(target, plan, classification="replayed")
        binding, receipt = _switch_binding_receipt(plan, state["binding"])
        binding_bytes = _lifecycle_output_bytes(binding, "binding")
        receipt_bytes = _lifecycle_output_bytes(receipt, "receipt")
        _visible_truth(target, planned)
        native_preflight()
        transition = bool(plan["remove"]) or plan["schema_version"] in (4, 5)
        guarded = transition or plan["schema_version"] == 6
        if guarded:
            if candidate is None:
                retained = product / "releases" / plan["candidate_release"]["id"]
                verified = verify_workspace_release(retained)
                candidate = {**verified, "payload": {p: _serial_file(retained / "payload" / p)
                             for p in _managed_paths(plan["candidate_release"]["inventory_id"])}}
            _serial_require(candidate["release_ref"] == plan["candidate_release"], "transition requires exact candidate")
            if transition:
                _entry_sync_admission(target, plan, candidate)
            else:
                # Windows uses its accepted directory-flush error allowlist.
                paths = _entry_sync_paths(target, plan, candidate["inventory"], candidate=candidate)
                for path in sorted(paths, key=lambda p: (len(p.relative_to(target).parts), p.relative_to(target).as_posix().encode("utf-8"))):
                    sync_directory(path)
        def durable(path, role):
            if transition: _entry_durable_directory(target, path, role=role)
            else: _durable_directory(path)
        def exact(path, data, role):
            if transition: _entry_write_exact(target, path, data, role=role)
            else: _write_exact(path, data)
        exact(product / "receipts" / (plan["operation_id"] + ".json"), receipt_bytes, "receipt-parent")
        if inject_at == "after-receipt": raise InjectedCrash(inject_at)
        def checkpoint():
            current, finished = _switch_preflight(target, plan, recover=True)
            _serial_require(not finished and current["binding_ref"] == state["binding_ref"], "binding changed during switch")
            if guarded and source is not None:
                with _switch_read_scope(source):
                    _serial_require(candidate == workspace_candidate(source), "switch source changed")
            return current
        release = product / "releases" / rid
        if not _exists(release):
            _serial_require(candidate is not None, "rollback release is unavailable")
            if guarded: checkpoint()
            staging = root / "staging"; durable(staging, "staging-directory")
            operation = staging / ("switch-" + plan["operation_id"]); durable(operation, "switch-directory")
            if guarded:
                _serial_require({p.name for p in operation.iterdir()} <= {rid}, "unknown switch staging member; preserve")
            staged = operation / rid; durable(staged, "candidate-directory")
            expected = {"inventory.json": canonical_json_bytes(candidate["inventory"])} | {"payload/" + p: b for p, b in candidate["payload"].items()}
            _init_partial_tree(staged, expected)
            for name, data in expected.items():
                if guarded: checkpoint()
                path = staged / name
                for parent in reversed(path.relative_to(staged).parents): durable(staged / parent, "candidate-directory")
                exact(path, data, "candidate-member-parent")
                if name == "inventory.json" and inject_at == "after-staged-inventory": raise InjectedCrash(inject_at)
            if inject_at == "after-staged-payload": raise InjectedCrash(inject_at)
            _serial_require(verify_workspace_release(staged)["release_ref"] == plan["candidate_release"], "staged candidate mismatch")
            if guarded: checkpoint()
            rename_directory(staged, release)
            if transition:
                _entry_sync(target, release.parent, phase="publication", role="release-parent")
                _entry_sync(target, operation, phase="publication", role="release-operation-parent")
            else:
                sync_directory(release.parent); sync_directory(operation)
        elif guarded:
            if transition:
                _entry_resync_release(target, plan, candidate["inventory"])
            else:
                for directory in sorted(_entry_inventory_directories(release, candidate["inventory"]),
                                        key=lambda p: (-len(p.parts), p.as_posix().encode("utf-8"))):
                    sync_directory(directory)
                sync_directory(release.parent)
        _serial_require(verify_workspace_release(release)["release_ref"] == plan["candidate_release"], "published candidate mismatch")
        operation = root / "staging" / ("switch-" + plan["operation_id"])
        if guarded and _exists(operation):
            _require_kind(operation, True)
            _serial_require(not any(operation.iterdir()), "unknown staging remains beside published release")
        if inject_at == "after-release": raise InjectedCrash(inject_at)
        checkpoint()
        launcher_bytes = _serial_file(release / "payload/colvia")
        if plan["remove"]:
            # No replacement helper for the new root pathname. An initial apply
            # cannot claim an intervening occupant; exact recovery uses the table.
            _entry_append_file(target / "colvia", launcher_bytes, target=target, executable=True, recover=recover, checkpoint=checkpoint)
            checkpoint()
            old = target / "hv2"
            if _exists(old):
                recorded = plan["remove"][0]; data = _serial_file(old)
                _serial_require(sha256_bytes(data) == recorded["sha256"] and len(data) == recorded["size_bytes"]
                                and stat.S_IMODE(old.lstat().st_mode) == 0o755, "old entry changed before retirement")
                checkpoint(); old.unlink()
                retirement_phase = "publication"
            else:
                retirement_phase = "recovery"
            _entry_sync(target, target, phase=retirement_phase, role="old-retirement-parent")
            if inject_at == "after-launcher": raise InjectedCrash(inject_at)
            checkpoint()
            staging = root / "staging"; durable(staging, "staging-directory")
            binding_stage = staging / ("entry-" + plan["operation_id"]); durable(binding_stage, "binding-directory")
            _entry_binding_stage(target, plan, binding_bytes, allowed=True)
            next_binding = binding_stage / "binding.next"
            _entry_append_file(next_binding, binding_bytes, target=target, executable=False, recover=recover, checkpoint=checkpoint)
            checkpoint()
            _serial_require(_serial_file(next_binding) == binding_bytes and
                            stat.S_IMODE(next_binding.lstat().st_mode) == 0o600, "binding stage changed")
            _serial_require(_serial_file(product / "binding.json") == canonical_json_bytes(state["binding"]), "expected B0 changed")
            os.replace(next_binding, product / "binding.json")
            _entry_sync(target, product, phase="publication", role="binding-product-parent", b1=True)
            _entry_sync(target, binding_stage, phase="publication", role="binding-operation-parent", b1=True)
        else:
            if _serial_file(target / "colvia") != launcher_bytes:
                _replace_product_file(target, target / "colvia", launcher_bytes, executable=True)
            if inject_at == "after-launcher": raise InjectedCrash(inject_at)
            current, finished = _switch_preflight(target, plan, recover=True)
            _serial_require(not finished and current["binding_ref"] == state["binding_ref"], "binding changed before publication")
            _replace_product_file(target, product / "binding.json", binding_bytes, executable=False)
        if inject_at == "after-binding": raise InjectedCrash(inject_at)
        return _entry_replay_result(target, plan, classification="updated" if plan["action"] == "update" else "rolled-back")


# Repair is an independent-source operation. Its backup/receipt is external
# evidence, never an authority node in the binding-selection history.
def _repair_file_observation(path: Path, window: str = "entry-1") -> dict[str, Any] | None:
    from .workspace import _exists
    if not _exists(path): return None
    if window == "windows-2":
        from .jsonio import windows_path_observation
        before = windows_path_observation(path)
        data = _serial_file(path)
        after = windows_path_observation(path)
        _serial_require(before == after and not after["directory"], "unstable Windows repair observation")
        mode = int(bool(after["attributes"] & 1))
    else:
        data = _serial_file(path)
        mode = stat.S_IMODE(path.stat().st_mode)
    return {"sha256":sha256_bytes(data), "size_bytes":len(data), "mode":mode}


def _repair_expected(candidate: dict[str, Any]) -> dict[str, bytes]:
    prefix = ".hrn/product/releases/"+candidate["release_ref"]["id"]+"/"
    return {"colvia":candidate["payload"]["colvia"], prefix+"inventory.json":canonical_json_bytes(candidate["inventory"])} | {
        prefix+"payload/"+p:b for p,b in candidate["payload"].items()}


def _repair_backup_path(backup: Path, target: Path, source: Path) -> Path:
    from .workspace import safe_target
    backup = Path(os.path.abspath(backup))
    safe_target(backup.parent, mutation=True)
    _serial_require(backup.name not in ("", ".", ".."), "invalid backup destination")
    def identity(path: Path) -> tuple[int, int]:
        info = path.stat(follow_symlinks=False)
        return info.st_dev, info.st_ino
    try:
        for root in (target, safe_target(source)):
            _serial_require(backup != root and backup not in root.parents and root not in backup.parents,
                            "backup must be outside target and source")
            # String paths do not identify directories on case-insensitive or
            # normalization-insensitive filesystems. Check both containment directions.
            root_identity = identity(root)
            _serial_require(all(identity(parent) != root_identity for parent in backup.parents),
                            "backup must be outside target and source")
            if backup.exists():
                backup_identity = identity(backup)
                _serial_require(all(identity(parent) != backup_identity for parent in (root, *root.parents)),
                                "backup must be outside target and source")
    except OSError as exc:
        raise ContractError("HV2-WORKSPACE-PRODUCT", "repair backup identity unavailable") from exc
    return backup


def workspace_repair_preview(source: Path, target: Path, backup: Path, *, operation_id: str, created_at: str) -> dict[str, Any]:
    from .workspace import classify_target, _file_json, target_fingerprint, _exists, _id, _text
    target = Path(classify_target(target, mutation=True)["target"])
    backup = _repair_backup_path(backup, target, source)
    _serial_require(not _exists(backup), "repair backup destination must be new")
    candidate = workspace_candidate(source)
    from .workspace import require_supported_runtime
    require_supported_runtime(candidate["release_ref"]["inventory_id"])
    windows = candidate["release_ref"]["inventory_id"] == "windows-2"
    state = _workspace_observe(target, repair_candidate=candidate)
    _serial_require(_id(operation_id) and _text(created_at), "repair identity/time")
    _serial_require(all(r["operation_id"].casefold() != operation_id.casefold() for r in state["history"]), "operation id already used")
    truth = _lifecycle_truth(target, allow_pending=True)
    files = []
    for path, data in sorted(_repair_expected(candidate).items()):
        before = state["repair_files"][path]
        after = {"sha256":sha256_bytes(data), "size_bytes":len(data),
                 "mode":0 if windows else 0o755 if path == "colvia" else (before["mode"] & 0o777 if before else 0o644)}
        if windows and before is not None and (before["sha256"], before["size_bytes"]) == (after["sha256"], after["size_bytes"]):
            continue  # A read-only attribute alone is never a repair target.
        if windows and before is not None and before["mode"] == 1:
            raise ContractError("HV2-WINDOWS-READONLY", "damaged repair target is read-only; preserve bytes and original requests")
        if before != after: files.append({"path":path, "before":before, "after":after})
    _serial_require(bool(files), "active release needs no repair")
    preserve = [{"path":f["path"], "sha256":f["before"]["sha256"], "size_bytes":f["before"]["size_bytes"]}
                for f in files if f["before"] is not None]
    fmt = _file_json(target/".hrn/format.json")
    plan = {"record_type":"lifecycle-plan", "schema_version":6 if windows else 5, "operation_id":operation_id, "action":"repair",
            "authority_home_id":fmt["authority_home_id"], "expected_binding_ref":state["binding_ref"],
            "candidate_release":candidate["release_ref"], "format_sha256":sha256_bytes(canonical_json_bytes(fmt)),
            "truth_refs":truth, "remove":preserve, "preserve":preserve, "created_at":created_at,
            "target_fingerprint":target_fingerprint(target)}
    request = {"plan":plan, "files":files, "backup":str(backup), "product_observation":state["observation"]}
    _serial_require(state == _workspace_observe(target, repair_candidate=candidate)
                    and truth == _lifecycle_truth(target, allow_pending=True), "repair preview changed while reading")
    return {"classification":"preview", "request":request, "confirm_token":sha256_bytes(canonical_json_bytes(request))[:16]}


def _repair_preflight(target: Path, request: dict[str, Any], candidate: dict[str, Any], *, recover: bool) -> dict[str, Any]:
    from .workspace import _file_json, target_fingerprint, _id, _text, PLAN_KEYS, _require_kind
    from .work import validate_ref
    request = _exact_dict(request, {"plan", "files", "backup", "product_observation"}, "HV2-WORKSPACE-REPAIR")
    plan = _exact_dict(request["plan"], set(PLAN_KEYS), "HV2-WORKSPACE-REPAIR")
    _require_kind(target/".hrn", True)
    fmt = _file_json(target/".hrn/format.json")
    _serial_require(plan["record_type"] == "lifecycle-plan" and type(plan["schema_version"]) is int
                    and plan["schema_version"] == (6 if candidate["release_ref"]["inventory_id"] == "windows-2" else 5) and plan["action"] == "repair" and _id(plan["operation_id"])
                    and _text(plan["created_at"]) and plan["target_fingerprint"] == target_fingerprint(target)
                    and plan["authority_home_id"] == fmt["authority_home_id"]
                    and plan["format_sha256"] == sha256_bytes(canonical_json_bytes(fmt)), "repair plan identity/target/format")
    validate_ref(plan["expected_binding_ref"])
    state = _workspace_observe(target, repair_candidate=candidate)
    _serial_require(plan["expected_binding_ref"] == state["binding_ref"] and plan["candidate_release"] == candidate["release_ref"], "repair binding/source changed")
    _serial_require(all(r["operation_id"].casefold() != plan["operation_id"].casefold() for r in state["history"]), "repair operation id already used")
    _serial_require(plan["truth_refs"] == _lifecycle_truth(target, allow_pending=True), "repair truth changed")
    windows = candidate["release_ref"]["inventory_id"] == "windows-2"
    expected = _repair_expected(candidate); files = request["files"]
    _serial_require(isinstance(files, list) and bool(files), "repair file list missing")
    names = []; preserve = []
    for f in files:
        _exact_dict(f, {"path", "before", "after"}, "HV2-WORKSPACE-REPAIR")
        name = f["path"]; _serial_require(isinstance(name,str) and name in expected, "repair path outside active release")
        names.append(name)
        for value in (f["before"], f["after"]):
            if value is None: continue
            _exact_dict(value, {"sha256", "size_bytes", "mode"}, "HV2-WORKSPACE-REPAIR")
            from .workspace import _sha
            _serial_require(_sha(value["sha256"]) and type(value["size_bytes"]) is int and value["size_bytes"] >= 0
                            and type(value["mode"]) is int
                            and (value["mode"] in (0, 1) if windows else 0 <= value["mode"] <= 0o7777), "repair observation shape")
        before=f["before"]; data=expected[name]
        if windows and before is not None and before["mode"] != 0:
            raise ContractError("HV2-WINDOWS-READONLY", "repair request cannot replace a read-only target")
        after={"sha256":sha256_bytes(data), "size_bytes":len(data), "mode":0 if windows else 0o755 if name=="colvia" else (before["mode"] & 0o777 if before else 0o644)}
        _serial_require(f["after"] == after and before != after, "repair replacement must be exact active bytes/mode")
        actual=state["repair_files"][name]
        _serial_require(actual == before or (recover and actual == after), "repair target drift")
        if before: preserve.append({"path":name,"sha256":before["sha256"],"size_bytes":before["size_bytes"]})
    _serial_require(names == sorted(set(names)), "repair path order/duplicate")
    _serial_require(plan["remove"] == preserve and plan["preserve"] == preserve, "repair preservation mismatch")
    # Every other active file must already be correct; no silent partial repair.
    for name,data in expected.items():
        if name not in names:
            actual=state["repair_files"][name]
            _serial_require(actual is not None and actual["sha256"] == sha256_bytes(data)
                            and actual["size_bytes"] == len(data)
                            and (windows or name != "colvia" or actual["mode"] == 0o755), "unplanned damage remains")
    observation=request["product_observation"]
    _serial_require(isinstance(observation,dict), "repair product observation shape")
    skipped={n[len(".hrn/product/"):] for n in names if n.startswith(".hrn/product/")}
    _serial_require({p:h for p,h in state["observation"].items() if p not in skipped}
                    == {p:h for p,h in observation.items() if p not in skipped}, "repair metadata/retained release changed")
    for f in files:
        if f["path"] == "colvia": continue
        p=f["path"][len(".hrn/product/"):]
        _serial_require(observation.get(p) == (f["before"]["sha256"] if f["before"] else None), "repair initial observation mismatch")
    return state


def workspace_repair_apply(source: Path, target: Path, request: dict[str, Any], *, confirm_token: str,
                           recover: bool = False, inject_at: str | None = None) -> dict[str, Any]:
    from .workspace import classify_target, writer_guard, _exists, _durable_directory, _write_exact, _require_kind, require_supported_runtime
    from .jsonio import _sync_fd, replace_file, windows_preflight_files
    from .work import _visible_truth
    import tempfile
    _serial_require(inject_at in {None, "after-backup-request", "after-backup", "after-file", "after-receipt"}, "unknown repair crash point")
    raw=canonical_json_bytes(request); decode_json_bytes(raw,require_canonical=True)
    _serial_require(isinstance(confirm_token,str) and confirm_token == sha256_bytes(raw)[:16], "repair confirmation mismatch")
    _exact_dict(request,{"plan","files","backup","product_observation"},"HV2-WORKSPACE-REPAIR")
    _serial_require(isinstance(request["backup"],str), "repair backup path type")
    target=Path(classify_target(target,mutation=True)["target"])
    backup=_repair_backup_path(Path(request["backup"]),target,source)
    _serial_require(str(backup) == request["backup"], "repair backup path is not absolute/canonical")
    candidate=workspace_candidate(source)
    window=candidate["release_ref"]["inventory_id"]
    require_supported_runtime(window)
    _repair_preflight(target,request,candidate,recover=recover)
    _serial_require(recover == _exists(backup), "existing backup requires explicit recovery; absent backup requires initial apply")
    plan=request["plan"]
    receipt={"record_type":"lifecycle-receipt", "schema_version":plan["schema_version"], "operation_id":plan["operation_id"], "plan":plan,
             "prior_binding_ref":plan["expected_binding_ref"], "result_binding_ref":plan["expected_binding_ref"]}
    with writer_guard(target):
        _serial_require(candidate == workspace_candidate(source), "repair source changed")
        _repair_preflight(target,request,candidate,recover=recover)
        _visible_truth(target,[f["path"] for f in request["files"]])
        expected_backup={"request.json":raw,"receipt.json":canonical_json_bytes(receipt)}
        # Backups bind original bytes before any replacement. A partial backup may
        # only be filled from a still-original target, never from repaired bytes.
        for f in request["files"]:
            if f["before"] is None: continue
            path=backup/"original"/f["path"]
            if _exists(path):
                for parent in reversed(path.relative_to(backup).parents): _require_kind(backup/parent,True)
                data=_serial_file(path)
            else:
                _serial_require(_repair_file_observation(target/f["path"], window) == f["before"], "original bytes unavailable for backup")
                data=_serial_file(target/f["path"])
            _serial_require(sha256_bytes(data)==f["before"]["sha256"] and len(data)==f["before"]["size_bytes"], "backup original digest mismatch")
            expected_backup["original/"+f["path"]]=data
        if _exists(backup):
            seen=_init_partial_tree(backup,expected_backup)
            _serial_require("request.json" in seen, "backup has no ownership request; preserve")
            if "receipt.json" in seen:
                _serial_require(seen==set(expected_backup), "completed repair backup is incomplete")
                _serial_require(all(_repair_file_observation(target/f["path"], window)==f["after"] for f in request["files"]), "completed repair has new damage")
                return {"classification":"replayed", "backup":str(backup), "product":verify_workspace_product(target)}
        windows_preflight_files([target/f["path"] for f in request["files"]]
                                + [backup/name for name in expected_backup]
                                + [target/".hrn/staging", target/".hrn/locks/writer.lock"])
        if not _exists(backup): _durable_directory(backup)
        _write_exact(backup/"request.json",raw)
        if inject_at=="after-backup-request": raise InjectedCrash(inject_at)
        for name,data in expected_backup.items():
            if not name.startswith("original/"): continue
            for parent in reversed(Path(name).parents): _durable_directory(backup/parent)
            _write_exact(backup/name,data)
        _serial_require(_init_partial_tree(backup,expected_backup)==set(expected_backup)-{"receipt.json"}, "incomplete repair backup")
        if inject_at=="after-backup": raise InjectedCrash(inject_at)
        expected=_repair_expected(candidate)
        for f in request["files"]:
            _repair_preflight(target,request,candidate,recover=True)
            if _repair_file_observation(target/f["path"], window) == f["after"]: continue
            staging=target/".hrn/staging"; _durable_directory(staging)
            fd,name=tempfile.mkstemp(prefix="repair-",dir=staging); staged=Path(name)
            with os.fdopen(fd,"wb") as handle:
                handle.write(expected[f["path"]]); handle.flush()
                if window != "windows-2": os.fchmod(handle.fileno(),f["after"]["mode"])
                _sync_fd(handle.fileno())
            sync_directory(staging)
            _repair_preflight(target,request,candidate,recover=True)
            replace_file(staged,target/f["path"]); sync_directory((target/f["path"]).parent); sync_directory(staging)
            if inject_at=="after-file": raise InjectedCrash(inject_at)
        _repair_preflight(target,request,candidate,recover=True)
        _serial_require(all(_repair_file_observation(target/f["path"], window) == f["after"] for f in request["files"]),
                        "repair replacement observations are incomplete")
        product=verify_workspace_product(target)
        _write_exact(backup/"receipt.json",canonical_json_bytes(receipt))
        if inject_at=="after-receipt": raise InjectedCrash(inject_at)
        return {"classification":"repaired", "backup":str(backup), "product":product}


def _detach_entries(value: Any) -> dict[str, dict[str, Any]]:
    from .workspace import _sha
    _serial_require(isinstance(value,list), "detach inventory is not a list")
    names=[]; result={}
    for item in value:
        item=_exact_dict(item,{"path","sha256","size_bytes"},"HV2-WORKSPACE-DETACH")
        name=item["path"]
        _serial_require(isinstance(name,str) and name and all(p not in ("", ".", "..") for p in name.split("/"))
                        and not name.startswith("/") and "\\" not in name and _sha(item["sha256"])
                        and type(item["size_bytes"]) is int and item["size_bytes"] >= 0, "detach inventory path/digest/size")
        names.append(name);result[name]=item
    _serial_require(names==sorted(set(names),key=lambda n:n.encode()) and len({n.casefold() for n in names})==len(names), "detach inventory order/alias")
    return result


def _detach_plan_shape(plan: Any, fmt: dict[str, Any]) -> dict[str, Any]:
    from .workspace import PLAN_KEYS, _id, _sha, _text, IGNORE_BYTES
    from .work import validate_ref
    import re
    plan=_exact_dict(plan,set(PLAN_KEYS),"HV2-WORKSPACE-DETACH")
    _serial_require(plan["record_type"]=="lifecycle-plan" and type(plan["schema_version"]) is int and plan["schema_version"] in (1, 2, 3, 4, 5, 6)
                    and plan["action"]=="detach" and _id(plan["operation_id"]) and _text(plan["created_at"])
                    and plan["authority_home_id"]==fmt["authority_home_id"] and plan["format_sha256"]==sha256_bytes(canonical_json_bytes(fmt))
                    and _sha(plan["target_fingerprint"]) and plan["candidate_release"] is None, "detach plan identity/format")
    validate_ref(plan["expected_binding_ref"])
    remove=_detach_entries(plan["remove"]);preserve=_detach_entries(plan["preserve"])
    launcher = {1: "hv2", 2: "hv2", 3: "colvia", 4: "colvia", 5: "colvia", 6: "colvia"}[plan["schema_version"]]
    required={launcher,".hrn/product/init-plan.json",".hrn/product/binding.json"};releases=set();receipts=set()
    for name in set(remove)-required:
        if name.startswith(".hrn/product/receipts/"):
            tail=name[len(".hrn/product/receipts/"):]
            _serial_require(tail.endswith(".json") and _id(tail[:-5]), "detach receipt path")
            receipts.add(tail[:-5]);required.add(name)
        else:
            parts=name.split("/")
            _serial_require(len(parts)>=5 and parts[:3]==[".hrn","product","releases"]
                            and re.fullmatch(r"product-release-[0-9a-f]{24}",parts[3]) is not None, "detach removal outside managed product")
            releases.add(parts[3])
    _serial_require(bool(releases) and bool(receipts) and plan["operation_id"].casefold() not in {n.casefold() for n in receipts}, "detach operation/release set")
    for rid in releases:
        prefix=".hrn/product/releases/"+rid+"/"
        # Resumption can occur after inventory bytes have been removed. Only the
        # three exact shipped memberships are allowed; preflight bound their bytes.
        if plan["schema_version"] == 6:
            _serial_require(prefix+"payload/colvia" in remove and prefix+"payload/src/hv2ref/continuation.py" in remove, "detach6 requires windows-2 fixed payload membership")
        if prefix+"payload/colvia" in remove:
            _serial_require(plan["schema_version"] in (3, 4, 5, 6), "old detach schema cannot contain colvia payload")
            if prefix+"payload/src/hv2ref/continuation.py" in remove:
                _serial_require(plan["schema_version"] in (5, 6), "old detach schema cannot contain continuation payload")
                paths = CONTINUATION_MANAGED_PATHS
            else:
                paths = ENTRY_MANAGED_PATHS if plan["schema_version"] == 3 else DELEGATION_MANAGED_PATHS
        else:
            paths = SERIAL_MANAGED_PATHS if prefix+"payload/src/hv2ref/candidates.py" in remove else UMBRELLA_MANAGED_PATHS if prefix+"payload/src/hv2ref/umbrella.py" in remove else LEGACY_MANAGED_PATHS
        required |= {prefix+"inventory.json"} | {prefix+"payload/"+p for p in paths}
        _serial_require(prefix+"inventory.json" in remove and rid=="product-release-"+remove[prefix+"inventory.json"]["sha256"][:24], "detach release/inventory mismatch")
    _serial_require(set(remove)==required and remove[".hrn/product/binding.json"]["sha256"]==plan["expected_binding_ref"]["sha256"], "detach incomplete removal/binding set")
    _serial_require(any((remove[launcher]["sha256"], remove[launcher]["size_bytes"]) ==
                        (remove[".hrn/product/releases/"+rid+"/payload/"+launcher]["sha256"],
                         remove[".hrn/product/releases/"+rid+"/payload/"+launcher]["size_bytes"])
                        for rid in releases if ".hrn/product/releases/"+rid+"/payload/"+launcher in remove), "detach launcher is not bound to a removed release")
    _serial_require(isinstance(plan["truth_refs"],list), "detach truth refs shape")
    truth=[]
    for ref in plan["truth_refs"]:
        _exact_dict(ref,{"path","sha256"},"HV2-WORKSPACE-DETACH")
        name=ref["path"]
        _serial_require(isinstance(name,str) and (name == "planning/candidates.json" or (name.split("/")[0] in ("intents","work") and len(name.split("/"))>=3))
                        and all(p not in ("", ".", "..") for p in name.split("/")) and "\\" not in name and _sha(ref["sha256"]), "detach truth path/digest")
        truth.append(name)
        _serial_require(".hrn/"+name in preserve and preserve[".hrn/"+name]["sha256"]==ref["sha256"], "detach preserve/truth mismatch")
    _serial_require(truth==sorted(set(truth),key=lambda n:n.encode()), "detach truth order/duplicate")
    _serial_require(set(preserve)=={".hrn/format.json",".hrn/.gitignore"}|{".hrn/"+n for n in truth}, "detach preservation set")
    for name,data in ((".hrn/format.json",canonical_json_bytes(fmt)),(".hrn/.gitignore",IGNORE_BYTES)):
        _serial_require(preserve[name]=={"path":name,"sha256":sha256_bytes(data),"size_bytes":len(data)}, "detach format/ignore preservation")
    return plan


def _detach_receipt(plan: dict[str, Any]) -> dict[str, Any]:
    return {"record_type":"lifecycle-receipt","schema_version":plan["schema_version"],"operation_id":plan["operation_id"],"plan":plan,
            "prior_binding_ref":plan["expected_binding_ref"],"result_binding_ref":None}


def _detach_order(plan: dict[str, Any]) -> tuple[list[str],list[str]]:
    launcher = {1: "hv2", 2: "hv2", 3: "colvia", 4: "colvia", 5: "colvia", 6: "colvia"}[plan["schema_version"]]
    files=[launcher]+[e["path"] for e in plan["remove"] if e["path"]!=launcher]
    dirs={p.as_posix() for name in files if name!=launcher for p in Path(name).parents if p.as_posix().startswith(".hrn/product")}
    return files,sorted(dirs,key=lambda n:(-len(n.split("/")),n.encode()))


def _detach_initial_read(target: Path, reader, *args):
    """Keep each Windows pre-publication read separate from locks and writes."""
    if sys.platform != "win32":
        return reader(target, *args)
    from .jsonio import _windows_detach_read_scope
    from .work import _lifecycle_git_observation
    with _windows_detach_read_scope(target, capture_serial=True), _lifecycle_git_observation(target):
        return reader(target, *args)


def _detach_preview_plan(target: Path, operation_id: str, created_at: str) -> dict[str, Any]:
    return _detach_initial_read(target, _detach_preview_plan_records, operation_id, created_at)


def _detach_preview_plan_records(target: Path, operation_id: str, created_at: str) -> dict[str, Any]:
    from .workspace import _file_json, target_fingerprint
    state=_workspace_observe(target)
    window = state["binding"]["active_release"]["inventory_id"]
    _serial_require(window in ("continuation-1", "windows-2"), "older-window detach requires retained old source")
    from .workspace import require_supported_runtime
    require_supported_runtime(window)
    if window == "windows-2":
        _serial_require(all(b["active_release"]["inventory_id"] == window for b in state["bindings"]),
                        "detach6 cannot contain historical-window releases")
    _refuse_retired_entry(target, "current detach preview")
    truth=_lifecycle_truth(target);fmt=_file_json(target/".hrn/format.json")
    observed_bytes = {}
    def entry(name):
        data=_serial_file(target/name); observed_bytes[name] = data
        return {"path":name,"sha256":sha256_bytes(data),"size_bytes":len(data)}
    remove=[entry(n) for n in sorted(["colvia"]+[".hrn/product/"+p for p in state["observation"]],key=lambda n:n.encode())]
    preserve=[entry(n) for n in sorted([".hrn/format.json",".hrn/.gitignore"]+[".hrn/"+r["path"] for r in truth],key=lambda n:n.encode())]
    plan={"record_type":"lifecycle-plan","schema_version":6 if window == "windows-2" else 5,"operation_id":operation_id,"action":"detach",
          "authority_home_id":fmt["authority_home_id"],"expected_binding_ref":state["binding_ref"],"candidate_release":None,
          "format_sha256":sha256_bytes(canonical_json_bytes(fmt)),"truth_refs":truth,"remove":remove,"preserve":preserve,
          "created_at":created_at,"target_fingerprint":target_fingerprint(target)}
    _detach_plan_shape(plan,fmt)
    if window == "windows-2":
        _detach_remaining_window(plan, {item["path"]: observed_bytes[item["path"]] for item in remove})
    _serial_require(state==_workspace_observe(target) and truth==_lifecycle_truth(target), "detach preview changed")
    return plan


def workspace_detach_preview(target: Path, *, operation_id: str, created_at: str, installed: bool = False) -> dict[str, Any]:
    from .workspace import classify_target
    target=Path(classify_target(target,mutation=True)["target"])
    if installed: _detach_initial_read(target, require_workspace_runtime)
    plan=_detach_preview_plan(target,operation_id,created_at)
    _lifecycle_output_bytes(plan, "plan")
    _lifecycle_output_bytes(_detach_receipt(plan), "receipt")
    return {"classification":"preview","request":plan,"confirm_token":sha256_bytes(canonical_json_bytes(plan))[:16]}



def _detach_remaining_window(plan: dict[str, Any], files: dict[str, bytes]) -> None:
    """Check surviving metadata; never reconstruct already removed bytes."""
    from .workspace import _sha
    version = plan["schema_version"]
    if version != 6:
        # Keep the original main reader contract. Only new Windows witnesses
        # distinguish unsupported/relabelled Windows records from that history.
        for name, data in files.items():
            windows = []
            if name.endswith("/inventory.json") or name == ".hrn/product/binding.json":
                try:
                    value = decode_json_bytes(data, require_canonical=True)
                except ContractError:
                    continue  # Legacy receipt/byte rules still own old metadata.
                if isinstance(value, dict):
                    windows.append(value.get("inventory_id"))
                    for field in ("active_release", "prior_release"):
                        ref = value.get(field)
                        if isinstance(ref, dict): windows.append(ref.get("inventory_id"))
            elif name == "colvia" or name.endswith("/payload/colvia"):
                if len(data) > 1024 * 1024: continue  # Optional legacy witness only.
                try:
                    tree = ast.parse(data)
                except (SyntaxError, ValueError, UnicodeError, RecursionError, MemoryError):
                    continue
                for node in tree.body:
                    if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "WORKSPACE_INVENTORY_ID" for t in node.targets):
                        if isinstance(node.value, ast.Constant): windows.append(node.value.value)
            _serial_require(not any(isinstance(w, str) and w in ("windows-1", "windows-2") for w in windows),
                            "detach pair conflicts with remaining Windows window; preserve original matching source")
        return
    expected_window = "windows-2"
    allowed = {"windows-2"}
    planned = _detach_entries(plan["remove"])
    def admitted(window):
        return isinstance(window, str) and window in allowed
    for name, data in files.items():
        if name.endswith("/inventory.json"):
            inventory = _serial_inventory(decode_json_bytes(data, require_canonical=True))
            _serial_require(admitted(inventory["inventory_id"]), "detach pair conflicts with remaining inventory window")
            prefix = name[:-len("inventory.json")] + "payload/"
            for entry in inventory["entries"]:
                full = prefix + entry["path"]
                _serial_require(planned.get(full) == {**entry, "path": full}, "detach inventory differs from complete removal list")
        elif name == "colvia" or name.endswith("/payload/colvia"):
            _serial_require((lambda w: w == expected_window if name == "colvia" else admitted(w))(_launcher_inventory_window(data, allow_legacy=True)),
                            "detach pair conflicts with remaining launcher window")
    if ".hrn/product/binding.json" in files:
        binding = _exact_dict(decode_json_bytes(files[".hrn/product/binding.json"], require_canonical=True),
                              {"record_type", "schema_version", "authority_home_id", "active_release", "prior_release", "operation_id"},
                              "HV2-WORKSPACE-DETACH")
        _serial_require(binding["record_type"] == "product-binding" and type(binding["schema_version"]) is int
                        and binding["schema_version"] == 1 and binding["authority_home_id"] == plan["authority_home_id"]
                        and binding["operation_id"] == plan["expected_binding_ref"]["id"], "detach remaining binding identity")
        for field in ("active_release", "prior_release"):
            release = binding[field]
            if field == "prior_release" and release is None:
                continue
            release = _exact_dict(release, {"id", "sha256", "inventory_id"}, "HV2-WORKSPACE-DETACH")
            _serial_require(admitted(release["inventory_id"]), "detach pair conflicts with remaining binding window")
            _serial_require(_sha(release["sha256"]) and isinstance(release["id"], str)
                            and release["id"] == "product-release-" + release["sha256"][:24], "detach binding release identity")
            item = planned.get(".hrn/product/releases/" + release["id"] + "/inventory.json")
            _serial_require(item is not None and item["sha256"] == release["sha256"], "detach binding inventory link")
        _serial_require(binding["active_release"]["inventory_id"] == expected_window,
                        "detach pair conflicts with active binding window")


def _detach_observe_once(target: Path) -> dict[str, Any]:
    from contextlib import nullcontext
    from .workspace import _DetachTopologyObservation
    from .jsonio import _windows_detach_read_scope
    from .work import _detach_git_observation
    # The scope closes before the independent second sweep or next removal.
    # All leaves, bytes, record graphs and removal checkpoints stay fresh.
    scope = _windows_detach_read_scope(target, capture_serial=True) if sys.platform == "win32" else nullcontext()
    with scope:
        observation = _DetachTopologyObservation(target)
        try:
            visibility = _detach_git_observation(target, observation) if sys.platform == "win32" else nullcontext()
            with visibility:
                result = _detach_observe_records(target, observation)
            observation.finish()
            return result
        finally:
            observation.close()


def _detach_observe_records(target: Path, observation) -> dict[str, Any]:
    from .workspace import inspect_root, _file_json, _exists, _require_kind
    from .work import _visible_truth
    from .jsonio import _windows_detach_read_observation
    scope = _windows_detach_read_observation.get() if sys.platform == "win32" else None
    def preserve(entry):
        data = _serial_file(target / entry["path"])
        _serial_require(len(data) == entry["size_bytes"] and sha256_bytes(data) == entry["sha256"], "detached preserved bytes changed")
    def remaining(name):
        return name, _serial_file(target / name)
    _serial_require(inspect_root(target)["classification"]=="detach-candidate", "no valid detach candidate")
    root=target/".hrn";fmt=_file_json(root/"format.json");receipt=_file_json(root/"detached.json")
    receipt=_exact_dict(receipt,{"record_type","schema_version","operation_id","plan","prior_binding_ref","result_binding_ref"},"HV2-WORKSPACE-DETACH")
    plan=_detach_plan_shape(receipt["plan"],fmt)
    _serial_require(_serial_file(root/"detached.json")==canonical_json_bytes(_detach_receipt(plan)), "detach receipt does not bind plan")
    _serial_require(_lifecycle_truth(target, _topology_observation=observation)==plan["truth_refs"], "detached truth differs from preserved plan")
    if scope is not None:
        scope.read_batch(preserve, plan["preserve"])
    else:
        for entry in plan["preserve"]:
            preserve(entry)
    planned=_detach_entries(plan["remove"]);order,dir_order=_detach_order(plan)
    files={};dirs=set();product=root/"product"
    launcher = {1: "hv2", 2: "hv2", 3: "colvia", 4: "colvia", 5: "colvia", 6: "colvia"}[plan["schema_version"]]
    if _exists(target/launcher):files[launcher]=_serial_file(target/launcher)
    reads = []
    stack=[product] if _exists(product) else []
    while stack:
        directory=stack.pop();_require_kind(directory,True);name=directory.relative_to(target).as_posix()
        _serial_require(name in dir_order, "unknown detach directory")
        dirs.add(name)
        for p in directory.iterdir():
            name=p.relative_to(target).as_posix()
            if name in dir_order:_require_kind(p,True);stack.append(p)
            else:
                _serial_require(name in planned, "unknown detach member; preserve")
                if scope is not None:
                    reads.append(name)
                else:
                    files[name]=_serial_file(p)
    if scope is not None:
        files.update(scope.read_batch(remaining, reads))
    for name,data in files.items():
        _serial_require(sha256_bytes(data)==planned[name]["sha256"] and len(data)==planned[name]["size_bytes"], "detach remaining bytes changed; preserve")
    _detach_remaining_window(plan, files)
    if sys.platform == "win32":
        # A missing leaf under an unsafe or inaccessible ancestor is not removal.
        for name in planned:
            if name not in files:
                _serial_require(not _exists(target/name), "detach removed path is not safely absent")
    remaining=[n for n in order if n in files]
    _serial_require(remaining==order[len(order)-len(remaining):], "not an exact detach file-removal prefix")
    if remaining:_serial_require(dirs==set(dir_order), "directory removed before planned files")
    else:_serial_require([n for n in dir_order if n in dirs]==dir_order[len(dir_order)-len(dirs):], "not an exact detach directory-removal prefix")
    if plan["schema_version"] in (3, 4, 5, 6):
        _refuse_retired_entry(target, "schema-3 detach or completed-detach replay")
    _visible_truth(target,[".hrn/detached.json"]+list(files)+[e["path"] for e in plan["preserve"]], _topology_observation=observation)
    return {"classification":"partial" if remaining or dirs else "detached", "authority_home_id":fmt["authority_home_id"],
            "receipt":receipt,"remaining_files":remaining,"remaining_directories":[n for n in dir_order if n in dirs],
            "record_verification":"verified", "truth_files":len(plan["truth_refs"])}


def workspace_detached_status(target: Path) -> dict[str, Any]:
    from .workspace import classify_target
    target=Path(classify_target(target)["target"])
    try:
        observed=_detach_observe_once(target)
        _serial_require(observed==_detach_observe_once(target), "unstable detached state")
        return observed
    except (OSError,ValueError,RecursionError) as exc:
        raise ContractError("HV2-WORKSPACE-DETACH","detached state unavailable or malformed") from exc


def workspace_detach_apply(target: Path, plan: dict[str, Any], *, confirm_token: str, recover: bool = False,
                           inject_at: str | None = None, installed: bool = False) -> dict[str, Any]:
    from .workspace import classify_target, _file_json, _exists, target_fingerprint, writer_guard, _write_exact, require_supported_runtime, _require_kind
    from .work import _visible_truth
    from .jsonio import windows_preflight_files
    _serial_require(inject_at in {None,"after-receipt","after-launcher","after-file","after-files","after-directory","after-product"}, "unknown detach crash point")
    raw=canonical_json_bytes(plan);decode_json_bytes(raw,require_canonical=True)
    _serial_require(isinstance(confirm_token,str) and confirm_token==sha256_bytes(raw)[:16], "detach confirmation mismatch")
    target=Path(classify_target(target,mutation=True)["target"])
    _require_kind(target/".hrn", True)
    _detach_plan_shape(plan,_file_json(target/".hrn/format.json"))
    _serial_require(plan["schema_version"] in (5, 6), "legacy detach writes require retained old source")
    require_supported_runtime("windows-2" if plan["schema_version"] == 6 else "continuation-1")
    _serial_require(plan["target_fingerprint"]==target_fingerprint(target), "detach target changed")
    if installed:
        _serial_require(not recover, "detach recovery requires independent source")
        _detach_initial_read(target, require_workspace_runtime)
    receipt_path=target/".hrn/detached.json"
    def preflight():
        if _exists(receipt_path):
            _serial_require(recover, "detach already started; exact source recovery required")
            state=workspace_detached_status(target)
            _serial_require(state["receipt"]==_detach_receipt(plan), "another detach plan is recorded")
            return state
        _serial_require(not recover, "no detach receipt to recover")
        _serial_require(plan==_detach_preview_plan(target,plan["operation_id"],plan["created_at"]), "detach plan changed since preview")
        return None
    previous=preflight()
    if previous and previous["classification"]=="detached":return {**previous,"replayed":True}
    _visible_truth(target,[".hrn/detached.json"]+[e["path"] for e in plan["preserve"]])
    with writer_guard(target,purpose="detach-recovery" if previous else "work"):
        if installed:_detach_initial_read(target, require_workspace_runtime)
        previous=preflight()
        _visible_truth(target,[".hrn/detached.json"]+[e["path"] for e in plan["preserve"]])
        if previous and previous["classification"]=="detached":return {**previous,"replayed":True}
        remaining = previous["remaining_files"] if previous else [e["path"] for e in plan["remove"]]
        windows_preflight_files([target/name for name in remaining] + [receipt_path, target/".hrn/locks/writer.lock"])
        receipt_bytes = _lifecycle_output_bytes(_detach_receipt(plan), "receipt")
        _write_exact(receipt_path,receipt_bytes)
        if inject_at=="after-receipt":raise InjectedCrash(inject_at)
        state=workspace_detached_status(target)
        for name in state["remaining_files"]:
            current=workspace_detached_status(target)
            _serial_require(current["receipt"]==_detach_receipt(plan) and name==current["remaining_files"][0], "detach state changed")
            windows_preflight_files([target/name])
            try:
                remove_path(target/name);sync_directory((target/name).parent)
            except OSError as exc:
                raise ContractError("HV2-WORKSPACE-DETACH", "detach removal interrupted; preserve and inspect remaining paths") from exc
            if inject_at==("after-launcher" if name=="colvia" else "after-file"):raise InjectedCrash(inject_at)
        if inject_at=="after-files":raise InjectedCrash(inject_at)
        for name in workspace_detached_status(target)["remaining_directories"]:
            current=workspace_detached_status(target)
            _serial_require(current["receipt"]==_detach_receipt(plan) and not current["remaining_files"]
                            and name==current["remaining_directories"][0], "detach directories changed")
            try:
                remove_path(target/name, directory=True);sync_directory((target/name).parent)
            except OSError as exc:
                raise ContractError("HV2-WORKSPACE-DETACH", "detach removal interrupted; preserve and inspect remaining paths") from exc
            if inject_at=="after-directory":raise InjectedCrash(inject_at)
        if inject_at=="after-product":raise InjectedCrash(inject_at)
        return workspace_detached_status(target)
