from __future__ import annotations

import ast
import os
import re
import stat
import sys
from pathlib import Path
from typing import Any

from .errors import ContractError, InjectedCrash
from .jsonio import canonical_json_bytes, decode_json_bytes, sha256_bytes, sync_directory, write_new_bytes


def source_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _exact_dict(value: object, keys: set[str], code: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != keys:
        actual = sorted(value) if isinstance(value, dict) else type(value).__name__
        raise ContractError(code, repr(actual))
    return value


def _write_exact(path: Path, data: bytes) -> None:
    if path.exists() or path.is_symlink():
        if path.is_symlink() or not path.is_file() or path.read_bytes() != data:
            raise ContractError("HV2-PRODUCT-IMMUTABLE-CONTRADICTION", str(path))
        return
    write_new_bytes(path, data)


# Single-home runtime verification. Lifecycle publication is deliberately separate
# from these read-only checks; lifecycle receipts bind the installed history.
SERIAL_MANAGED_PATHS = tuple(sorted({
    ".gitignore", "AGENTS.md", "CLAUDE.md", "PRODUCT-CAPABILITIES.json", "README.md",
    "docs/CONCEPTS.md", "docs/GENERAL-WORK.md", "docs/GETTING-STARTED.md",
    "docs/GUIDED-INTENT-FORMATION.md", "docs/MAINTAINING.md", "docs/MANUAL-OPERATION.md",
    "docs/OPERATIONS.md", "docs/README.md", "docs/REFERENCE.md",
    "docs/SECURITY-AND-SUPPORT.md", "docs/WORKSPACE-CONTRACT.md", "hv2",
    "src/hv2ref/__init__.py", "src/hv2ref/cli.py", "src/hv2ref/errors.py",
    "src/hv2ref/intent.py", "src/hv2ref/jsonio.py", "src/hv2ref/product.py",
    "src/hv2ref/work.py", "src/hv2ref/workspace.py",
    "src/hv2ref/view.py", "src/hv2ref/umbrella.py", "src/hv2ref/candidates.py", "adapters/harness-v2-work/SKILL.md",
}, key=lambda path: path.encode("utf-8")))


UMBRELLA_MANAGED_PATHS = tuple(p for p in SERIAL_MANAGED_PATHS if p != "src/hv2ref/candidates.py")
LEGACY_MANAGED_PATHS = tuple(p for p in UMBRELLA_MANAGED_PATHS if p != "src/hv2ref/umbrella.py")


def _managed_paths(window: str) -> tuple[str, ...]:
    _serial_require(window in ("human-1", "worker-1", "umbrella-1", "planning-1"), "unsupported inventory window")
    return SERIAL_MANAGED_PATHS if window == "planning-1" else UMBRELLA_MANAGED_PATHS if window == "umbrella-1" else LEGACY_MANAGED_PATHS


def _serial_require(condition: bool, detail: str) -> None:
    if not condition:
        raise ContractError("HV2-WORKSPACE-PRODUCT", detail)


def _launcher_inventory_window(data: bytes, *, allow_legacy: bool = False) -> str:
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
                    and isinstance(node.value, ast.Constant) and node.value.value in (("worker-1", "umbrella-1", "planning-1") if allow_legacy else ("planning-1",))]
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
    expected_dirs = {str(parent) for name in expected_files for parent in Path(name).parents
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
    _serial_require(isinstance(value["inventory_id"], str) and value["inventory_id"] in {"human-1", "worker-1", "umbrella-1", "planning-1"}, "unsupported inventory window")
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
    from .workspace import safe_target, _require_kind
    source = safe_target(source)
    payload: dict[str, bytes] = {}
    for name in SERIAL_MANAGED_PATHS:
        path = source / name
        for parent in reversed(path.relative_to(source).parents):
            _require_kind(source / parent, True)
        _require_kind(path, False)
        payload[name] = _serial_file(path)
    window = _launcher_inventory_window(payload["hv2"])
    inventory = {"record_type": "release-inventory", "schema_version": 1, "inventory_id": window,
                 "entries": [{"path": name, "sha256": sha256_bytes(data), "size_bytes": len(data)}
                             for name, data in payload.items()]}
    digest = sha256_bytes(canonical_json_bytes(inventory))
    # Repeat after reading the complete set; do not silently combine two sources.
    for name, data in payload.items():
        _serial_require(_serial_file(source / name) == data, "candidate changed while reading")
    return {"inventory": inventory, "payload": payload,
            "release_ref": {"id": "product-release-" + digest[:24], "sha256": digest, "inventory_id": window}}


def verify_workspace_release(path: Path) -> dict[str, Any]:
    """Verify immutable inventory bytes, exact payload membership and every digest."""
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
    _serial_require(_launcher_inventory_window(files["payload/hv2"], allow_legacy=True)
                    == inventory["inventory_id"], "launcher declaration differs from inventory window")
    _serial_require(files == _serial_tree(path, set(files)), "release changed while reading")
    return {"release_ref": {"id": path.name, "sha256": digest, "inventory_id": inventory["inventory_id"]},
            "inventory": inventory}


def _switch_plan_shape(plan: Any, fmt: dict[str, Any]) -> dict[str, Any]:
    from .workspace import PLAN_KEYS, _id, _sha, _text
    from .work import validate_ref
    plan = _exact_dict(plan, set(PLAN_KEYS), "HV2-WORKSPACE-PLAN")
    _serial_require(plan["record_type"] == "lifecycle-plan" and type(plan["schema_version"]) is int
                    and plan["schema_version"] == 1 and plan["action"] in ("update", "rollback"), "unsupported switch plan")
    _serial_require(_id(plan["operation_id"]) and plan["authority_home_id"] == fmt["authority_home_id"]
                    and _text(plan["created_at"]) and _sha(plan["target_fingerprint"])
                    and plan["format_sha256"] == sha256_bytes(canonical_json_bytes(fmt)), "switch plan identity/format")
    validate_ref(plan["expected_binding_ref"])
    ref = _exact_dict(plan["candidate_release"], {"id", "sha256", "inventory_id"}, "HV2-WORKSPACE-RELEASE")
    _serial_require(_sha(ref["sha256"]) and ref["id"] == "product-release-" + ref["sha256"][:24]
                    and isinstance(ref["inventory_id"], str) and ref["inventory_id"] in {"human-1", "worker-1", "umbrella-1", "planning-1"}, "invalid switch release")
    _serial_require(plan["remove"] == [] and plan["preserve"] == [] and isinstance(plan["truth_refs"], list), "switch cannot remove truth")
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
    rank = {"human-1": 0, "worker-1": 1, "umbrella-1": 2, "planning-1": 3}
    _serial_require(rank[plan["candidate_release"]["inventory_id"]] >= rank[prior["active_release"]["inventory_id"]],
                    "inventory history cannot downgrade to an older semantic window")
    if plan["action"] == "rollback":
        _serial_require(plan["candidate_release"] == prior["prior_release"], "rollback must select the recorded previous release")
    binding = {"record_type":"product-binding", "schema_version":1, "authority_home_id":plan["authority_home_id"],
               "active_release":plan["candidate_release"], "prior_release":prior["active_release"], "operation_id":plan["operation_id"]}
    receipt = {"record_type":"lifecycle-receipt", "schema_version":1, "operation_id":plan["operation_id"],
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
                        and type(receipt["schema_version"]) is int and receipt["schema_version"] == 1, "invalid receipt identity/schema")
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
    _serial_require(not _exists(root / "planning") or binding["active_release"]["inventory_id"] == "planning-1", "planning records require an applied planning-1 binding")
    _serial_require(allow_pending or pending is None, "pending lifecycle blocks product use; recover exact plan from independent source")
    if repair_candidate is not None:
        _serial_require(binding["active_release"]["inventory_id"] == "planning-1",
                        "older-window repair requires the exact retained old source")
        _serial_require(pending is None and repair_candidate["release_ref"] == binding["active_release"],
                        "repair requires the exact active release and no pending lifecycle")
    repair_paths = set()
    releases = {}
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
        else:
            verified = verify_workspace_release(path)
        _serial_require(verified["release_ref"] == ref, "binding/release mismatch")
        releases[rid] = verified
    expected = {"init-plan.json", "binding.json"} | {"receipts/"+op+".json" for op in receipts}
    for rid in releases:
        expected |= {"releases/"+rid+"/inventory.json"} | {"releases/"+rid+"/payload/"+p for p in _managed_paths(releases[rid]["inventory"]["inventory_id"])}
    files = _serial_tree(product, expected, optional_files=repair_paths)
    _serial_require(files["binding.json"] == raw_binding and files["init-plan.json"] == canonical_json_bytes(initial)
                    and all(files["receipts/"+op+".json"] == data for op,data in raw_receipts.items()), "product changed while reading")
    active = binding["active_release"]["id"]; launcher = target / "hv2"
    if repair_candidate is not None:
        actual = {".hrn/product/"+p: _repair_file_observation(product/p) for p in sorted(repair_paths)}
        actual["hv2"] = _repair_file_observation(launcher)
        launcher_bytes = _serial_file(launcher) if _exists(launcher) else b""
    else:
        actual = None
        _require_kind(launcher, False); launcher_bytes = _serial_file(launcher)
    permitted = [repair_candidate["payload"]["hv2"] if repair_candidate is not None else files["releases/"+active+"/payload/hv2"]]
    if pending and pending["plan"]["candidate_release"]["id"] in releases:
        permitted.append(files["releases/"+pending["plan"]["candidate_release"]["id"]+"/payload/hv2"])
    if repair_candidate is None:
        _serial_require(launcher_bytes in permitted and bool(launcher.stat().st_mode & stat.S_IXUSR), "launcher differs from permitted release or is not executable")
    _visible_truth(target, [".hrn/format.json", ".hrn/.gitignore", "hv2"] + [".hrn/product/"+p for p in files])
    return {"binding_ref":record_ref(binding,"operation_id"), "binding":binding, "launcher_sha256":sha256_bytes(launcher_bytes),
            "release_path":str(product/"releases"/active), "inventory":releases[active]["inventory"],
            "pending":pending, "history":chain, "bindings":bindings,
            "observation":{p:sha256_bytes(data) for p,data in files.items()}, "repair_files":actual}


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
    require_supported_runtime()
    target = Path(classify_target(target, mutation=True)["target"])
    observed = verify_workspace_product(target)
    _serial_require(observed["inventory"]["inventory_id"] == "planning-1", "new installed runtime requires planning-1")
    _serial_require(sys.flags.isolated == 1 and sys.dont_write_bytecode,
                    "writer must use isolated Python startup without bytecode writes")
    main = sys.modules.get("__main__")
    main_path = getattr(main, "__file__", None)
    _serial_require(isinstance(main_path, str) and Path(main_path).absolute() == target / "hv2"
                    and Path(main_path).resolve() == target / "hv2", "executing launcher is not the control launcher")
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
    from .workspace import classify_target, target_fingerprint, validate_format, _validate_init_plan
    target = Path(classify_target(target, mutation=True)["target"])
    candidate = workspace_candidate(source)
    fmt = validate_format({"record_type": "workspace-format", "format_version": 1,
                           "authority_home_id": authority_home_id, "created_at": created_at, "lineage": None})
    plan = {"record_type": "lifecycle-plan", "schema_version": 1, "operation_id": operation_id, "action": "init",
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
    receipt = {"record_type": "lifecycle-receipt", "schema_version": 1, "operation_id": plan["operation_id"],
               "plan": plan, "prior_binding_ref": None, "result_binding_ref": record_ref(binding, "operation_id")}
    return binding, receipt


def _init_partial_tree(root: Path, expected: dict[str, bytes]) -> set[str]:
    """Inspect a subset of owned exact bytes; no deletion or repair inference."""
    from .workspace import _require_kind
    dirs = {str(parent) for name in expected for parent in Path(name).parents if str(parent) != "."}
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
    _serial_require(not _root_aliases(target), "workspace root alias")
    _serial_require(not any(p.name.casefold().startswith(".harness-v2") for p in target.iterdir()), "old homes require a fresh target")
    if not _exists(root):
        _serial_require(not recover, "cannot recover an absent root")
        _serial_require(not _exists(target / "hv2"), "preexisting launcher is not owned")
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
        verify_workspace_product(target)
        return "complete"
    _serial_require(recover, "partial init requires explicit exact recovery")
    state = inspect_root(target)["classification"]
    _serial_require(state in {"root-ready", "partial-candidate"}, "root is not an exact initialization prefix")
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
    if _exists(target / "hv2"):
        _serial_require(_exists(receipt_path), "launcher without durable init receipt")
        _serial_require(_serial_file(target / "hv2") == candidate["payload"]["hv2"], "changed launcher; preserve")
    if state == "partial-candidate":
        _serial_require(seen == {"init-plan.json"} and not _exists(target / "hv2"), "product published before root completion")
    return state


def workspace_init_apply(source: Path, target: Path, request: dict[str, Any], *, confirm_token: str, recover: bool = False, inject_at: str | None = None) -> dict[str, Any]:
    from .workspace import classify_target, validate_format, _validate_init_plan, bootstrap_root, writer_guard, _exists, _durable_directory, _write_exact, require_supported_runtime
    from .work import _visible_truth
    require_supported_runtime()
    points = {None, "after-root", "after-product-dir", "after-plan", "after-format", "after-ignore", "after-intents", "after-work",
              "after-staged-inventory", "after-staged-payload", "after-release", "after-receipt", "after-launcher-bytes", "after-launcher", "after-binding"}
    _serial_require(inject_at in points, "unknown init crash point")
    request = _exact_dict(request, {"format", "plan"}, "HV2-WORKSPACE-INIT")
    # Validate canonical JSON limits before writing any part of the request.
    raw = canonical_json_bytes(request); decode_json_bytes(raw, require_canonical=True)
    _serial_require(isinstance(confirm_token, str) and confirm_token == sha256_bytes(raw)[:16], "init confirmation token mismatch")
    target = Path(classify_target(target, mutation=True)["target"])
    fmt = validate_format(request["format"]); _validate_init_plan(request["plan"], fmt, target)
    candidate = workspace_candidate(source)
    _serial_require(candidate["release_ref"] == request["plan"]["candidate_release"], "source changed since init preview")
    root = target / ".hrn"; plan = request["plan"]; rid = candidate["release_ref"]["id"]
    planned = [".hrn/format.json", ".hrn/.gitignore", ".hrn/product/init-plan.json", ".hrn/product/binding.json", "hv2",
               ".hrn/product/receipts/" + plan["operation_id"] + ".json", ".hrn/product/releases/" + rid + "/inventory.json"]
    planned += [".hrn/product/releases/" + rid + "/payload/" + p for p in SERIAL_MANAGED_PATHS]
    _visible_truth(target, planned)
    state = _workspace_init_preflight(target, request, candidate, recover=recover)
    if state == "complete": return {"classification": "initialized", "replayed": True, "product": verify_workspace_product(target)}
    bootstrap_points = {"after-root", "after-product-dir", "after-plan", "after-format", "after-ignore", "after-intents", "after-work"}
    if state in {"fresh", "partial-candidate"}:
        bootstrap_root(target, plan, fmt, recover=state != "fresh", inject_at=inject_at if inject_at in bootstrap_points else None)
    with writer_guard(target):
        # Once root ownership exists, every resume is checked under the common guard.
        state = _workspace_init_preflight(target, request, candidate, recover=True)
        if state == "complete": return {"classification": "initialized", "replayed": True, "product": verify_workspace_product(target)}
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
            os.rename(staged, release); sync_directory(release.parent); sync_directory(staging)
        if inject_at == "after-release": raise InjectedCrash(inject_at)
        binding, receipt = _init_binding_receipt(request)
        _durable_directory(product / "receipts")
        _write_exact(product / "receipts" / (plan["operation_id"] + ".json"), canonical_json_bytes(receipt))
        if inject_at == "after-receipt": raise InjectedCrash(inject_at)
        _write_exact(target / "hv2", candidate["payload"]["hv2"])
        if inject_at == "after-launcher-bytes": raise InjectedCrash(inject_at)
        (target / "hv2").chmod(0o755)
        with (target / "hv2").open("rb") as file: os.fsync(file.fileno())
        sync_directory(target)
        if inject_at == "after-launcher": raise InjectedCrash(inject_at)
        _write_exact(product / "binding.json", canonical_json_bytes(binding))
        if inject_at == "after-binding": raise InjectedCrash(inject_at)
        return {"classification": "initialized", "replayed": False, "product": verify_workspace_product(target)}


def workspace_status(target: Path) -> dict[str, Any]:
    """Read-only diagnostics; pending product/truth never becomes a healthy pass."""
    from .workspace import classify_target, inspect_root, _exists, runtime_supported, SUPPORTED_PYTHON_STRINGS, SUPPORTED_PYTHON_TEXT
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
            return {**result, "topology":topology["kind"], "authoritative_control":False, "next_action":next_action}
        except ContractError as exc:
            return {"classification":"degraded", "error_code":exc.code, "message":exc.message, "topology":topology["kind"]}
    if root["classification"] != "root-ready":
        classification = {"partial-candidate":"partial", "detach-candidate":"partial", "integrity-failure":"degraded", "unrecognized":"degraded", "unstable":"degraded"}.get(root["classification"], root["classification"])
        return {**root, "root_classification":root["classification"], "classification":classification, "topology":topology["kind"]}
    if not _exists(target / ".hrn/product/binding.json"):
        return {"classification": "partial", "product_verification": "incomplete", "topology": topology["kind"],
                "next_action": "use independent trusted source and exact original init request; unknown/torn bytes require manual preservation"}
    try:
        state = _workspace_observe(target, allow_pending=True)
        if state["pending"] is not None:
            return {"classification":"partial", "topology":topology["kind"],
                    "pending_lifecycle":state["pending"]["operation_id"], "binding_ref":state["binding_ref"],
                    "next_action":"recover exact lifecycle request from independent trusted source; receipt alone is not completion"}
        product = verify_workspace_product(target)
        works = WorkStore(target)._all()  # Read-only graph check, no runtime mutation seam invoked.
        intents = workspace_intents(target)
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
        documentation_root = (Path(product["release_path"]) / "payload/docs").relative_to(target).as_posix()
        next_action = "read " + documentation_root + "/README.md"
        supported = runtime_supported()
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
        return {"classification": "partial" if pending_work or pending_intent or not planning["available"] else ("pass" if supported else "unsupported"), "topology": topology["kind"],
                "authoritative_control": topology["kind"] in {"primary", "non-git"}, "product": product,
                "documentation_root": documentation_root, "next_action": next_action,
                "pending_work": pending_work, "pending_intent": pending_intent,
                "work_states": {key: graph["state"] for key, graph in works.items()}, "intent_count": len(intents),
                "planning": planning,
                "runtime": {"implementation": sys.implementation.name, "python": ".".join(map(str, sys.version_info[:3])), "supported_baseline": SUPPORTED_PYTHON_STRINGS[0], "supported_versions": list(SUPPORTED_PYTHON_STRINGS), "required_releaselevel": "final", "free_threaded_supported": False,
                            "supported": supported}}
    except ContractError as exc:
        return {"classification": "degraded", "error_code": exc.code, "message": exc.message, "topology": topology["kind"]}

def _workspace_observe(target: Path, *, allow_pending: bool = False, repair_candidate: dict[str, Any] | None = None) -> dict[str, Any]:
    from .workspace import classify_target
    target = Path(classify_target(target)["target"])
    try:
        first = _workspace_product_once(target, allow_pending=allow_pending, repair_candidate=repair_candidate)
        _serial_require(first == _workspace_product_once(target, allow_pending=allow_pending, repair_candidate=repair_candidate), "unstable product history")
        return first
    except (OSError, ValueError, RecursionError) as exc:
        raise ContractError("HV2-WORKSPACE-PRODUCT", "product unavailable, malformed or unstable") from exc


def _lifecycle_truth(target: Path, *, allow_pending: bool = False) -> list[dict[str, str]]:
    from .workspace import _exists, _require_kind
    from .work import WorkStore, _visible_truth
    from .intent import workspace_intents
    root = target / ".hrn"
    for kind in ("intents", "work"):
        if _exists(root/kind): _require_kind(root/kind, True)
    works = WorkStore(target)._all(); intents = workspace_intents(target)
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
    _visible_truth(target, [".hrn/"+r["path"] for r in result])
    return result


def workspace_switch_preview(target: Path, *, action: str, source: Path | None, operation_id: str,
                             created_at: str, to_release_id: str | None = None, installed: bool = False) -> dict[str, Any]:
    from .workspace import classify_target, _file_json, target_fingerprint
    target = Path(classify_target(target, mutation=True)["target"])
    if installed: require_workspace_runtime(target)
    state = _workspace_observe(target); binding = state["binding"]
    _serial_require(action in ("update","rollback"), "unsupported lifecycle action")
    if action == "update":
        _serial_require(source is not None and to_release_id is None, "update requires source only")
        candidate = workspace_candidate(source)["release_ref"]
    else:
        _serial_require(source is None and binding["prior_release"] is not None, "no recorded rollback release")
        candidate = binding["prior_release"]
        _serial_require(to_release_id is None or to_release_id == candidate["id"], "rollback target is not previous release")
    _serial_require(candidate["inventory_id"] == "planning-1", "new source switches only to planning-1; retain old source for older-window operations")
    fmt = _file_json(target/".hrn/format.json"); truth = _lifecycle_truth(target)
    plan = {"record_type":"lifecycle-plan","schema_version":1,"operation_id":operation_id,"action":action,
            "authority_home_id":fmt["authority_home_id"],"expected_binding_ref":state["binding_ref"],"candidate_release":candidate,
            "format_sha256":sha256_bytes(canonical_json_bytes(fmt)),"truth_refs":truth,"remove":[],"preserve":[],
            "created_at":created_at,"target_fingerprint":target_fingerprint(target)}
    _switch_plan_shape(plan,fmt); _switch_binding_receipt(plan,binding)
    _serial_require(all(r["operation_id"].casefold() != operation_id.casefold() for r in state["history"]), "operation id already used")
    _serial_require(state == _workspace_observe(target) and truth == _lifecycle_truth(target), "preview changed while reading")
    return {"classification":"preview","request":plan,"confirm_token":sha256_bytes(canonical_json_bytes(plan))[:16],
            "transition_notice": "planning-1 lifecycle: once the first planning-1 receipt is durable, downgrade to older windows is unavailable, even before any candidate is recorded. Preserve the exact recovery source and request; a note request alone does not authorize update."}


def _switch_preflight(target: Path, plan: dict[str, Any], *, recover: bool) -> tuple[dict[str, Any], bool]:
    _serial_require(plan["candidate_release"]["inventory_id"] == "planning-1", "new source switches only to planning-1")
    state = _workspace_observe(target, allow_pending=True)
    matching = [r for r in state["history"] if r["operation_id"] == plan["operation_id"]]
    _serial_require(not any(r["operation_id"] != plan["operation_id"] and r["operation_id"].casefold() == plan["operation_id"].casefold() for r in state["history"]), "operation id case alias")
    if matching:
        _serial_require(canonical_json_bytes(matching[0]["plan"]) == canonical_json_bytes(plan), "operation id reused with another plan")
        if matching[0] != state["pending"]:
            _serial_require(state["pending"] is None, "another lifecycle is pending")
            return state, True  # Historical replay observes current; never rewinds it.
    if state["pending"]:
        _serial_require(recover and state["pending"]["plan"] == plan, "pending lifecycle requires same explicit recovery")
    else:
        _serial_require(not recover, "no pending lifecycle to recover")
    _serial_require(state["binding_ref"] == plan["expected_binding_ref"], "binding changed since preview")
    _serial_require(_lifecycle_truth(target) == plan["truth_refs"], "truth changed since lifecycle preview")
    return state, False


def _replace_product_file(target: Path, destination: Path, data: bytes, *, executable: bool) -> None:
    from .workspace import _durable_directory, _require_kind
    from .jsonio import _sync_fd
    import tempfile
    staging = target/".hrn/staging"; _durable_directory(staging); _require_kind(staging, True)
    _require_kind(destination, False)
    fd,name = tempfile.mkstemp(prefix="product-replace-",dir=staging); staged = Path(name)
    with os.fdopen(fd,"wb") as handle:
        handle.write(data); handle.flush()
        os.fchmod(handle.fileno(),0o755 if executable else stat.S_IMODE(destination.stat().st_mode) & 0o777)
        _sync_fd(handle.fileno())
    sync_directory(staging)
    os.replace(staged,destination)
    sync_directory(destination.parent); sync_directory(staging)


def workspace_switch_apply(target: Path, plan: dict[str, Any], *, confirm_token: str, source: Path | None = None,
                           recover: bool = False, inject_at: str | None = None, installed: bool = False) -> dict[str, Any]:
    from .workspace import classify_target, _file_json, target_fingerprint, writer_guard, _exists, _durable_directory, _write_exact, require_supported_runtime, _require_kind
    from .work import _visible_truth
    require_supported_runtime()
    points = {None,"after-receipt","after-staged-inventory","after-staged-payload","after-release","after-launcher","after-binding"}
    _serial_require(inject_at in points, "unknown lifecycle crash point")
    raw = canonical_json_bytes(plan); decode_json_bytes(raw,require_canonical=True)
    _serial_require(isinstance(confirm_token,str) and confirm_token == sha256_bytes(raw)[:16], "lifecycle confirmation mismatch")
    target = Path(classify_target(target,mutation=True)["target"])
    _require_kind(target/".hrn", True)
    _switch_plan_shape(plan,_file_json(target/".hrn/format.json"))
    _serial_require(plan["target_fingerprint"] == target_fingerprint(target), "lifecycle target changed")
    if installed:
        _serial_require(not recover, "lifecycle recovery requires independent source")
        require_workspace_runtime(target)
    candidate = workspace_candidate(source) if source is not None else None
    _serial_require((plan["action"] == "update") == (candidate is not None), "update requires exact source; rollback uses retained release")
    if candidate: _serial_require(candidate["release_ref"] == plan["candidate_release"], "candidate changed since preview")
    state,done = _switch_preflight(target,plan,recover=recover)
    if done: return {"classification":"replayed","operation_id":plan["operation_id"],"product":verify_workspace_product(target)}
    rid = plan["candidate_release"]["id"]; root=target/".hrn"; product=root/"product"
    planned = ["hv2",".hrn/product/binding.json",".hrn/product/receipts/"+plan["operation_id"]+".json",
               ".hrn/product/releases/"+rid+"/inventory.json"] + [".hrn/product/releases/"+rid+"/payload/"+p for p in SERIAL_MANAGED_PATHS]
    _visible_truth(target,planned)
    with writer_guard(target):
        if installed: require_workspace_runtime(target)
        state,done = _switch_preflight(target,plan,recover=recover)
        if done: return {"classification":"replayed","operation_id":plan["operation_id"],"product":verify_workspace_product(target)}
        binding,receipt = _switch_binding_receipt(plan,state["binding"])
        _visible_truth(target,planned)
        _write_exact(product/"receipts"/(plan["operation_id"]+".json"),canonical_json_bytes(receipt))
        if inject_at == "after-receipt": raise InjectedCrash(inject_at)
        release=product/"releases"/rid
        if not _exists(release):
            _serial_require(candidate is not None, "rollback release is unavailable")
            staging=root/"staging"; _durable_directory(staging)
            operation=staging/("switch-"+plan["operation_id"]); _durable_directory(operation)
            staged=operation/rid; _durable_directory(staged)
            expected={"inventory.json":canonical_json_bytes(candidate["inventory"])} | {"payload/"+p:b for p,b in candidate["payload"].items()}
            _init_partial_tree(staged,expected)
            for name,data in expected.items():
                path=staged/name
                for parent in reversed(path.relative_to(staged).parents): _durable_directory(staged/parent)
                _write_exact(path,data)
                if name == "inventory.json" and inject_at == "after-staged-inventory": raise InjectedCrash(inject_at)
            if inject_at == "after-staged-payload": raise InjectedCrash(inject_at)
            _serial_require(verify_workspace_release(staged)["release_ref"] == plan["candidate_release"], "staged candidate mismatch")
            os.rename(staged,release); sync_directory(release.parent); sync_directory(operation)
        _serial_require(verify_workspace_release(release)["release_ref"] == plan["candidate_release"], "published candidate mismatch")
        if inject_at == "after-release": raise InjectedCrash(inject_at)
        # Re-observe the exact pending plan, complete candidate and truth before swaps.
        current,_ = _switch_preflight(target,plan,recover=True)
        _serial_require(current["binding_ref"] == state["binding_ref"], "binding changed during switch")
        launcher_bytes = _serial_file(release/"payload/hv2")
        if _serial_file(target/"hv2") != launcher_bytes:
            _replace_product_file(target,target/"hv2",launcher_bytes,executable=True)
        if inject_at == "after-launcher": raise InjectedCrash(inject_at)
        current,_ = _switch_preflight(target,plan,recover=True)
        _serial_require(current["binding_ref"] == state["binding_ref"], "binding changed before publication")
        _replace_product_file(target,product/"binding.json",canonical_json_bytes(binding),executable=False)
        if inject_at == "after-binding": raise InjectedCrash(inject_at)
        return {"classification":"updated" if plan["action"] == "update" else "rolled-back",
                "operation_id":plan["operation_id"],"product":verify_workspace_product(target)}


# Repair is an independent-source operation. Its backup/receipt is external
# evidence, never an authority node in the binding-selection history.
def _repair_file_observation(path: Path) -> dict[str, Any] | None:
    from .workspace import _exists
    if not _exists(path): return None
    data = _serial_file(path)
    return {"sha256":sha256_bytes(data), "size_bytes":len(data), "mode":stat.S_IMODE(path.stat().st_mode)}


def _repair_expected(candidate: dict[str, Any]) -> dict[str, bytes]:
    prefix = ".hrn/product/releases/"+candidate["release_ref"]["id"]+"/"
    return {"hv2":candidate["payload"]["hv2"], prefix+"inventory.json":canonical_json_bytes(candidate["inventory"])} | {
        prefix+"payload/"+p:b for p,b in candidate["payload"].items()}


def _repair_backup_path(backup: Path, target: Path, source: Path) -> Path:
    from .workspace import safe_target
    backup = Path(os.path.abspath(backup))
    safe_target(backup.parent)
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
    state = _workspace_observe(target, repair_candidate=candidate)
    _serial_require(_id(operation_id) and _text(created_at), "repair identity/time")
    _serial_require(all(r["operation_id"].casefold() != operation_id.casefold() for r in state["history"]), "operation id already used")
    truth = _lifecycle_truth(target, allow_pending=True)
    files = []
    for path, data in sorted(_repair_expected(candidate).items()):
        before = state["repair_files"][path]
        after = {"sha256":sha256_bytes(data), "size_bytes":len(data),
                 "mode":0o755 if path == "hv2" else (before["mode"] & 0o777 if before else 0o644)}
        if before != after: files.append({"path":path, "before":before, "after":after})
    _serial_require(bool(files), "active release needs no repair")
    preserve = [{"path":f["path"], "sha256":f["before"]["sha256"], "size_bytes":f["before"]["size_bytes"]}
                for f in files if f["before"] is not None]
    fmt = _file_json(target/".hrn/format.json")
    plan = {"record_type":"lifecycle-plan", "schema_version":1, "operation_id":operation_id, "action":"repair",
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
                    and plan["schema_version"] == 1 and plan["action"] == "repair" and _id(plan["operation_id"])
                    and _text(plan["created_at"]) and plan["target_fingerprint"] == target_fingerprint(target)
                    and plan["authority_home_id"] == fmt["authority_home_id"]
                    and plan["format_sha256"] == sha256_bytes(canonical_json_bytes(fmt)), "repair plan identity/target/format")
    validate_ref(plan["expected_binding_ref"])
    state = _workspace_observe(target, repair_candidate=candidate)
    _serial_require(plan["expected_binding_ref"] == state["binding_ref"] and plan["candidate_release"] == candidate["release_ref"], "repair binding/source changed")
    _serial_require(all(r["operation_id"].casefold() != plan["operation_id"].casefold() for r in state["history"]), "repair operation id already used")
    _serial_require(plan["truth_refs"] == _lifecycle_truth(target, allow_pending=True), "repair truth changed")
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
                            and type(value["mode"]) is int and 0 <= value["mode"] <= 0o7777, "repair observation shape")
        before=f["before"]; data=expected[name]
        after={"sha256":sha256_bytes(data), "size_bytes":len(data), "mode":0o755 if name=="hv2" else (before["mode"] & 0o777 if before else 0o644)}
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
                            and (name != "hv2" or actual["mode"] == 0o755), "unplanned damage remains")
    observation=request["product_observation"]
    _serial_require(isinstance(observation,dict), "repair product observation shape")
    skipped={n[len(".hrn/product/"):] for n in names if n.startswith(".hrn/product/")}
    _serial_require({p:h for p,h in state["observation"].items() if p not in skipped}
                    == {p:h for p,h in observation.items() if p not in skipped}, "repair metadata/retained release changed")
    for f in files:
        if f["path"] == "hv2": continue
        p=f["path"][len(".hrn/product/"):]
        _serial_require(observation.get(p) == (f["before"]["sha256"] if f["before"] else None), "repair initial observation mismatch")
    return state


def workspace_repair_apply(source: Path, target: Path, request: dict[str, Any], *, confirm_token: str,
                           recover: bool = False, inject_at: str | None = None) -> dict[str, Any]:
    from .workspace import classify_target, writer_guard, _exists, _durable_directory, _write_exact, _require_kind, require_supported_runtime
    from .jsonio import _sync_fd
    from .work import _visible_truth
    import tempfile
    require_supported_runtime()
    _serial_require(inject_at in {None, "after-backup-request", "after-backup", "after-file", "after-receipt"}, "unknown repair crash point")
    raw=canonical_json_bytes(request); decode_json_bytes(raw,require_canonical=True)
    _serial_require(isinstance(confirm_token,str) and confirm_token == sha256_bytes(raw)[:16], "repair confirmation mismatch")
    _exact_dict(request,{"plan","files","backup","product_observation"},"HV2-WORKSPACE-REPAIR")
    _serial_require(isinstance(request["backup"],str), "repair backup path type")
    target=Path(classify_target(target,mutation=True)["target"])
    backup=_repair_backup_path(Path(request["backup"]),target,source)
    _serial_require(str(backup) == request["backup"], "repair backup path is not absolute/canonical")
    candidate=workspace_candidate(source)
    _repair_preflight(target,request,candidate,recover=recover)
    _serial_require(recover == _exists(backup), "existing backup requires explicit recovery; absent backup requires initial apply")
    plan=request["plan"]
    receipt={"record_type":"lifecycle-receipt", "schema_version":1, "operation_id":plan["operation_id"], "plan":plan,
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
                _serial_require(_repair_file_observation(target/f["path"]) == f["before"], "original bytes unavailable for backup")
                data=_serial_file(target/f["path"])
            _serial_require(sha256_bytes(data)==f["before"]["sha256"] and len(data)==f["before"]["size_bytes"], "backup original digest mismatch")
            expected_backup["original/"+f["path"]]=data
        if _exists(backup):
            seen=_init_partial_tree(backup,expected_backup)
            _serial_require("request.json" in seen, "backup has no ownership request; preserve")
            if "receipt.json" in seen:
                _serial_require(seen==set(expected_backup), "completed repair backup is incomplete")
                _serial_require(all(_repair_file_observation(target/f["path"])==f["after"] for f in request["files"]), "completed repair has new damage")
                return {"classification":"replayed", "backup":str(backup), "product":verify_workspace_product(target)}
        else: _durable_directory(backup)
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
            if _repair_file_observation(target/f["path"]) == f["after"]: continue
            staging=target/".hrn/staging"; _durable_directory(staging)
            fd,name=tempfile.mkstemp(prefix="repair-",dir=staging); staged=Path(name)
            with os.fdopen(fd,"wb") as handle:
                handle.write(expected[f["path"]]); handle.flush(); os.fchmod(handle.fileno(),f["after"]["mode"]); _sync_fd(handle.fileno())
            sync_directory(staging)
            _repair_preflight(target,request,candidate,recover=True)
            os.replace(staged,target/f["path"]); sync_directory((target/f["path"]).parent); sync_directory(staging)
            if inject_at=="after-file": raise InjectedCrash(inject_at)
        _repair_preflight(target,request,candidate,recover=True)
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
    _serial_require(plan["record_type"]=="lifecycle-plan" and type(plan["schema_version"]) is int and plan["schema_version"]==1
                    and plan["action"]=="detach" and _id(plan["operation_id"]) and _text(plan["created_at"])
                    and plan["authority_home_id"]==fmt["authority_home_id"] and plan["format_sha256"]==sha256_bytes(canonical_json_bytes(fmt))
                    and _sha(plan["target_fingerprint"]) and plan["candidate_release"] is None, "detach plan identity/format")
    validate_ref(plan["expected_binding_ref"])
    remove=_detach_entries(plan["remove"]);preserve=_detach_entries(plan["preserve"])
    required={"hv2",".hrn/product/init-plan.json",".hrn/product/binding.json"};releases=set();receipts=set()
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
        paths = SERIAL_MANAGED_PATHS if prefix+"payload/src/hv2ref/candidates.py" in remove else UMBRELLA_MANAGED_PATHS if prefix+"payload/src/hv2ref/umbrella.py" in remove else LEGACY_MANAGED_PATHS
        required |= {prefix+"inventory.json"} | {prefix+"payload/"+p for p in paths}
        _serial_require(prefix+"inventory.json" in remove and rid=="product-release-"+remove[prefix+"inventory.json"]["sha256"][:24], "detach release/inventory mismatch")
    _serial_require(set(remove)==required and remove[".hrn/product/binding.json"]["sha256"]==plan["expected_binding_ref"]["sha256"], "detach incomplete removal/binding set")
    _serial_require(any((remove["hv2"]["sha256"], remove["hv2"]["size_bytes"]) ==
                        (remove[".hrn/product/releases/"+rid+"/payload/hv2"]["sha256"],
                         remove[".hrn/product/releases/"+rid+"/payload/hv2"]["size_bytes"])
                        for rid in releases), "detach launcher is not bound to a removed release")
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
    return {"record_type":"lifecycle-receipt","schema_version":1,"operation_id":plan["operation_id"],"plan":plan,
            "prior_binding_ref":plan["expected_binding_ref"],"result_binding_ref":None}


def _detach_order(plan: dict[str, Any]) -> tuple[list[str],list[str]]:
    files=["hv2"]+[e["path"] for e in plan["remove"] if e["path"]!="hv2"]
    dirs={p.as_posix() for name in files if name!="hv2" for p in Path(name).parents if p.as_posix().startswith(".hrn/product")}
    return files,sorted(dirs,key=lambda n:(-len(n.split("/")),n.encode()))


def _detach_preview_plan(target: Path, operation_id: str, created_at: str) -> dict[str, Any]:
    from .workspace import _file_json, target_fingerprint
    state=_workspace_observe(target);truth=_lifecycle_truth(target);fmt=_file_json(target/".hrn/format.json")
    def entry(name):
        data=_serial_file(target/name)
        return {"path":name,"sha256":sha256_bytes(data),"size_bytes":len(data)}
    remove=[entry(n) for n in sorted(["hv2"]+[".hrn/product/"+p for p in state["observation"]],key=lambda n:n.encode())]
    preserve=[entry(n) for n in sorted([".hrn/format.json",".hrn/.gitignore"]+[".hrn/"+r["path"] for r in truth],key=lambda n:n.encode())]
    plan={"record_type":"lifecycle-plan","schema_version":1,"operation_id":operation_id,"action":"detach",
          "authority_home_id":fmt["authority_home_id"],"expected_binding_ref":state["binding_ref"],"candidate_release":None,
          "format_sha256":sha256_bytes(canonical_json_bytes(fmt)),"truth_refs":truth,"remove":remove,"preserve":preserve,
          "created_at":created_at,"target_fingerprint":target_fingerprint(target)}
    _detach_plan_shape(plan,fmt)
    _serial_require(state==_workspace_observe(target) and truth==_lifecycle_truth(target), "detach preview changed")
    return plan


def workspace_detach_preview(target: Path, *, operation_id: str, created_at: str, installed: bool = False) -> dict[str, Any]:
    from .workspace import classify_target
    target=Path(classify_target(target,mutation=True)["target"])
    if installed: require_workspace_runtime(target)
    plan=_detach_preview_plan(target,operation_id,created_at)
    return {"classification":"preview","request":plan,"confirm_token":sha256_bytes(canonical_json_bytes(plan))[:16]}


def _detach_observe_once(target: Path) -> dict[str, Any]:
    from .workspace import inspect_root, _file_json, _exists, _require_kind
    from .work import _visible_truth
    _serial_require(inspect_root(target)["classification"]=="detach-candidate", "no valid detach candidate")
    root=target/".hrn";fmt=_file_json(root/"format.json");receipt=_file_json(root/"detached.json")
    receipt=_exact_dict(receipt,{"record_type","schema_version","operation_id","plan","prior_binding_ref","result_binding_ref"},"HV2-WORKSPACE-DETACH")
    plan=_detach_plan_shape(receipt["plan"],fmt)
    _serial_require(_serial_file(root/"detached.json")==canonical_json_bytes(_detach_receipt(plan)), "detach receipt does not bind plan")
    _serial_require(_lifecycle_truth(target)==plan["truth_refs"], "detached truth differs from preserved plan")
    for entry in plan["preserve"]:
        data=_serial_file(target/entry["path"])
        _serial_require(len(data)==entry["size_bytes"] and sha256_bytes(data)==entry["sha256"], "detached preserved bytes changed")
    planned=_detach_entries(plan["remove"]);order,dir_order=_detach_order(plan)
    files={};dirs=set();product=root/"product"
    if _exists(target/"hv2"):files["hv2"]=_serial_file(target/"hv2")
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
                files[name]=_serial_file(p)
    for name,data in files.items():
        _serial_require(sha256_bytes(data)==planned[name]["sha256"] and len(data)==planned[name]["size_bytes"], "detach remaining bytes changed; preserve")
    remaining=[n for n in order if n in files]
    _serial_require(remaining==order[len(order)-len(remaining):], "not an exact detach file-removal prefix")
    if remaining:_serial_require(dirs==set(dir_order), "directory removed before planned files")
    else:_serial_require([n for n in dir_order if n in dirs]==dir_order[len(dir_order)-len(dirs):], "not an exact detach directory-removal prefix")
    _visible_truth(target,[".hrn/detached.json"]+list(files)+[e["path"] for e in plan["preserve"]])
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
    require_supported_runtime()
    _serial_require(inject_at in {None,"after-receipt","after-launcher","after-file","after-files","after-directory","after-product"}, "unknown detach crash point")
    raw=canonical_json_bytes(plan);decode_json_bytes(raw,require_canonical=True)
    _serial_require(isinstance(confirm_token,str) and confirm_token==sha256_bytes(raw)[:16], "detach confirmation mismatch")
    target=Path(classify_target(target,mutation=True)["target"])
    _require_kind(target/".hrn", True)
    _detach_plan_shape(plan,_file_json(target/".hrn/format.json"))
    _serial_require(plan["target_fingerprint"]==target_fingerprint(target), "detach target changed")
    if installed:
        _serial_require(not recover, "detach recovery requires independent source")
        require_workspace_runtime(target)
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
        if installed:require_workspace_runtime(target)
        previous=preflight()
        _visible_truth(target,[".hrn/detached.json"]+[e["path"] for e in plan["preserve"]])
        if previous and previous["classification"]=="detached":return {**previous,"replayed":True}
        _write_exact(receipt_path,canonical_json_bytes(_detach_receipt(plan)))
        if inject_at=="after-receipt":raise InjectedCrash(inject_at)
        state=workspace_detached_status(target)
        for name in state["remaining_files"]:
            current=workspace_detached_status(target)
            _serial_require(current["receipt"]==_detach_receipt(plan) and name==current["remaining_files"][0], "detach state changed")
            try:
                (target/name).unlink();sync_directory((target/name).parent)
            except OSError as exc:
                raise ContractError("HV2-WORKSPACE-DETACH", "detach removal interrupted; preserve and inspect remaining paths") from exc
            if inject_at==("after-launcher" if name=="hv2" else "after-file"):raise InjectedCrash(inject_at)
        if inject_at=="after-files":raise InjectedCrash(inject_at)
        for name in workspace_detached_status(target)["remaining_directories"]:
            current=workspace_detached_status(target)
            _serial_require(current["receipt"]==_detach_receipt(plan) and not current["remaining_files"]
                            and name==current["remaining_directories"][0], "detach directories changed")
            try:
                (target/name).rmdir();sync_directory((target/name).parent)
            except OSError as exc:
                raise ContractError("HV2-WORKSPACE-DETACH", "detach removal interrupted; preserve and inspect remaining paths") from exc
            if inject_at=="after-directory":raise InjectedCrash(inject_at)
        if inject_at=="after-product":raise InjectedCrash(inject_at)
        return workspace_detached_status(target)
