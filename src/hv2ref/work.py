"""General Work content evidence, installed writers and recovery guards.

Snapshots and recovery observations never grant acceptance or mutate project bytes.
Record graph, intent/product binding and human confirmation are separate prerequisites.
"""
from __future__ import annotations

import copy
from contextlib import contextmanager
from contextvars import ContextVar
import hashlib
import os
from pathlib import Path
import re
import stat
import subprocess
import sys
import unicodedata
from typing import Any

from .errors import ContractError
from .jsonio import canonical_json_bytes
from .workspace import classify_target, git_environment, git_executable, safe_target

_SHA = re.compile(r"[0-9a-f]{64}\Z")
_OID = re.compile(r"(?:[0-9a-f]{40}|[0-9a-f]{64})\Z")
_ENTRY = {"path", "mode", "sha256", "size_bytes"}
_TREE = {"policy_version", "ignore_fingerprint", "entries", "sha256"}
_MANIFEST = {"record_type", "schema_version", "base", "result", "changes", "base_commit", "candidate_commit", "base_retention_ref", "candidate_retention_ref"}


def _fail(message: str) -> ContractError:
    return ContractError("HV2-WORK-CONTENT", message)


def _digest(value: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def _keys(value: Any, keys: set[str]) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != keys:
        raise _fail("unknown or missing content fields")
    return value


def _sha(value: Any) -> bool:
    return isinstance(value, str) and _SHA.fullmatch(value) is not None


def project_path(value: Any) -> str:
    """Validate a literal relative file path, never silently normalize it."""
    if not isinstance(value, str) or not value or "\\" in value or "\x00" in value:
        raise _fail("invalid project path")
    try:
        value.encode("utf-8", errors="strict")
    except UnicodeError as exc:
        raise _fail("path is not UTF-8") from exc
    parts = value.split("/")
    if unicodedata.normalize("NFC", value) != value or any(p in {"", ".", ".."} for p in parts):
        raise _fail("path must be literal relative NFC")
    if any(p.casefold() in {".git", ".hrn"} for p in parts):
        raise _fail("metadata path cannot be project content")
    return value


def _path_set(paths: list[str]) -> None:
    """Check aliases in every prefix, not just complete file names."""
    spellings: dict[str, str] = {}
    files: set[str] = set()
    for path in paths:
        project_path(path)
        if path in files:
            raise _fail("duplicate path")
        files.add(path)
        pieces = path.split("/")
        for i in range(1, len(pieces) + 1):
            prefix = "/".join(pieces[:i])
            key = unicodedata.normalize("NFC", prefix.casefold())
            if key in spellings and spellings[key] != prefix:
                raise _fail("case alias in project paths")
            spellings[key] = prefix
    if any(parent in files for path in files for parent in _parents(path)):
        raise _fail("file is also a parent directory")


def _parents(path: str) -> list[str]:
    pieces = path.split("/")
    return ["/".join(pieces[:i]) for i in range(1, len(pieces))]


def _git(target: Path, *args: str, allowed: tuple[int, ...] = (0,), input_data: bytes | None = None, isolated_attributes: bool = False) -> subprocess.CompletedProcess[bytes]:
    try:
        result = subprocess.run([git_executable(), "--no-replace-objects", "-c", "core.fsmonitor=false", "-C", str(target), *args], capture_output=True, input=input_data, env={**git_environment(), "GIT_NO_LAZY_FETCH": "1", **({"GIT_ATTR_NOSYSTEM": "1"} if isolated_attributes else {})}, check=False)
    except OSError as exc:
        raise _fail("Git unavailable for content evidence") from exc
    if result.returncode not in allowed:
        raise _fail("Git content probe failed: " + args[0])
    return result


def _decode(data: bytes) -> str:
    try:
        return data.decode("utf-8", errors="strict")
    except UnicodeError as exc:
        raise _fail("Git path is not UTF-8") from exc


def _stable_file(path: Path, *, _capture_bytes: bool = False):
    # Detach may consume the bytes covered by this exact native observation.
    # The default signature-only path and all freshness checks are unchanged.
    if _capture_bytes and sys.platform != "win32":
        raise _fail("native byte capture requires Windows")
    captured = bytearray() if _capture_bytes else None
    from contextlib import ExitStack
    with ExitStack() as resources:
        native = None
        fd = None
        if sys.platform == "win32":
            import msvcrt
            from .jsonio import (windows_path_observation, windows_verify_handle,
                                 _windows_detach_read_observation, _windows_open_read)
            scope = _windows_detach_read_observation.get()
            if scope is not None and scope.capture_serial and scope.accepts(scope.absolute(path)):
                native, fd = resources.enter_context(_windows_open_read(path))
            else:
                native = windows_path_observation(path)
        before = path.lstat()
        if not stat.S_ISREG(before.st_mode):
            raise _fail("unsupported file type: " + path.name)
        if fd is None:
            flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
            fd = os.open(path, flags)
            resources.callback(os.close, fd)
        if native is not None:
            windows_verify_handle(path, msvcrt.get_osfhandle(fd), mutation=False, expected=native, content_unchanged=True)
        opened = os.fstat(fd)
        if (before.st_dev, before.st_ino) != (opened.st_dev, opened.st_ino):
            raise _fail("file changed while opening")
        hasher = hashlib.sha256()
        size = 0
        while chunk := os.read(fd, 1024 * 1024):
            size += len(chunk)
            hasher.update(chunk)
            if captured is not None:
                captured.extend(chunk)
        if native is not None:
            # Native timestamps are observations, not a content version. Compare
            # a second byte observation as well; this is not a hostile-race lock.
            os.lseek(fd, 0, os.SEEK_SET)
            checked_hash = hashlib.sha256()
            checked_size = 0
            while chunk := os.read(fd, 1024 * 1024):
                checked_size += len(chunk)
                checked_hash.update(chunk)
            if checked_size != size or checked_hash.digest() != hasher.digest():
                raise _fail("file changed during repeated content observation")
        after = os.fstat(fd)
        if native is not None:
            windows_verify_handle(path, msvcrt.get_osfhandle(fd), mutation=False, expected=native, content_unchanged=True)
    current = path.lstat()
    if native is not None:
        final_native = windows_path_observation(path)
        if final_native["chain"] != native["chain"] or final_native["content_signature"] != native["content_signature"]:
            raise _fail("native path or content changed during content observation")
    def signature(s: os.stat_result) -> tuple[int, ...]:
        return (s.st_dev, s.st_ino, s.st_mode, s.st_size, s.st_mtime_ns, s.st_ctime_ns)
    if native is None:
        changed = signature(before) != signature(after) or signature(after) != signature(current)
    else:
        # CPython's Windows path stat and fd stat differ in ctime and extension
        # executable bits. Compare each API with itself; native handle metadata
        # above independently checks cross-observation identity and content drift.
        changed = signature(before) != signature(current) or signature(opened) != signature(after)
    if changed or size != after.st_size:
        raise _fail("file changed during content observation")
    evidence = (hasher.hexdigest(), size, "100755" if current.st_mode & 0o100 else "100644")
    return (evidence, bytes(captured)) if captured is not None else evidence


def _regular_files(target: Path) -> list[str]:
    result: list[str] = []
    prefixes: dict[str, str] = {}
    def visit(directory: Path, relative: str) -> None:
        for member in sorted(directory.iterdir(), key=lambda p: os.fsencode(p.name)):
            if sys.platform == "win32":
                from .jsonio import windows_path_observation
                windows_path_observation(member)
            path = relative + member.name
            mode = member.lstat().st_mode
            if not relative and member.name in {".git", ".hrn"}:
                # Git topology is checked separately. Root evidence is a later guard.
                if member.name == ".hrn" and not stat.S_ISDIR(mode):
                    raise _fail("workspace root has unsupported type")
                continue
            project_path(path)
            folded = unicodedata.normalize("NFC", path.casefold())
            if folded in prefixes and prefixes[folded] != path:
                raise _fail("case alias in project tree")
            prefixes[folded] = path
            if stat.S_ISDIR(mode):
                visit(member, path + "/")
            elif stat.S_ISREG(mode):
                result.append(path)
            else:
                raise _fail("unsupported project file: " + path)
    visit(target, "")
    _path_set(result)
    return result


def _default_git_ignore_path(target: Path) -> Path:
    xdg = git_environment().get("XDG_CONFIG_HOME")
    if xdg:
        return Path(xdg) / "git" / "ignore"
    # Git resolves HOME itself; Windows Path.home() follows different variables.
    query = _git(target, "config", "--file", os.devnull, "--null", "--path",
                 "--default", "~/.config/git/ignore", "--get", "core.excludesFile")
    parts = query.stdout.split(b"\0")
    if len(parts) != 2 or not parts[0] or parts[1]:
        raise _fail("ambiguous default excludesFile")
    return Path(_decode(parts[0]))


def _policy(target: Path, all_files: list[str]) -> str:
    inputs: list[dict[str, Any]] = []
    for path in sorted((p for p in all_files if p.split("/")[-1].casefold() == ".gitignore"), key=lambda p: p.encode("utf-8")):
        # Fail closed for noncanonical ignore spelling across filesystem types.
        if path.split("/")[-1] != ".gitignore":
            raise _fail("noncanonical .gitignore spelling")
        parent = path.rpartition("/")[0]
        if parent:
            ignored = _git(target, "check-ignore", "--no-index", "-q", "--", parent + "/", allowed=(0, 1))
            if ignored.returncode == 0:
                detail = _git(target, "check-ignore", "--no-index", "-v", "-z", "--stdin", input_data=(parent + "/").encode("utf-8") + b"\0").stdout.split(b"\0")
                if len(detail) != 5 or detail[-1] != b"":
                    raise _fail("ambiguous ignore source")
                source = _decode(detail[0])
                # A cache's own '*' rule is applicable policy, unlike a directory
                # excluded before Git enters it. Preserve that distinction.
                if not source.startswith(parent + "/"):
                    continue
        inputs.append({"source": "project:" + path, "sha256": _stable_file(target / path)[0]})
    common = Path(_decode(_git(target, "rev-parse", "--path-format=absolute", "--git-common-dir").stdout).rstrip("\n"))
    config = _git(target, "config", "--path", "--get", "core.excludesFile", allowed=(0, 1))
    external: Path | None = None
    if config.returncode == 0:
        text = _decode(config.stdout).rstrip("\n")
        if not text or "\n" in text:
            raise _fail("ambiguous excludesFile")
        external = Path(text)
        if not external.is_absolute():
            external = target / external
    else:
        # Git's default global ignore file is effective even without a config key.
        external = _default_git_ignore_path(target)
    for label, path in (("info/exclude", common / "info" / "exclude"), ("core.excludesFile", external)):
        digest = None
        if path is not None:
            # External policy files may use dotfile-manager symlinks. Their
            # resolved regular contents are observed twice, without storing paths.
            if path.exists() or path.is_symlink():
                if sys.platform == "win32":
                    from .jsonio import windows_path_observation
                    windows_path_observation(path)
                digest = _stable_file(path.resolve(strict=True))[0]
        inputs.append({"source": label, "sha256": digest})
    return _digest(inputs)


def _verified_launcher_path(sha: str | None, window: str | None) -> str | None:
    if sha is None:
        return None
    paths = {"human-1": "hv2", "worker-1": "hv2", "umbrella-1": "hv2",
             "planning-1": "hv2", "checkout-1": "hv2", "entry-1": "colvia", "delegation-1": "colvia", "continuation-1": "colvia", "windows-2": "colvia", "official-execution-1": "colvia", "official-execution-2": "colvia"}
    if not _sha(sha) or not isinstance(window, str) or window not in paths:
        raise _fail("managed launcher proof requires a supported verified inventory window")
    return paths[window]



def _windows_content_policy(window: str | None) -> bool:
    if sys.platform != "win32" and window != "windows-2":
        return False
    from .workspace import require_supported_runtime
    require_supported_runtime(window)
    if window != "windows-2":
        raise _fail("native content policy requires verified windows-2")
    return True


def _windows_index_modes(data: bytes) -> dict[str, str]:
    """Parse the qualified Git debug shape; unknown flags/format fail closed.

The five diagnostic lines are not a stable Git public format. Qualification
must exercise the actual Git input; no alternate parser or mode fallback exists.
"""
    debug = re.compile(rb"  ctime: [0-9]+:[0-9]+\n  mtime: [0-9]+:[0-9]+\n"
                       rb"  dev: [0-9]+\tino: [0-9]+\n  uid: [0-9]+\tgid: [0-9]+\n"
                       rb"  size: [0-9]+\tflags: ([0-9a-f]+)\n")
    modes: dict[str, str] = {}
    offset = 0
    while offset < len(data):
        end = data.find(b"\0", offset)
        if end < 0:
            raise _fail("Windows index classification unavailable: missing record terminator")
        row = data[offset:end]
        header, separator, path_bytes = row.partition(b"\t")
        fields = header.split(b" ")
        if not separator or len(fields) != 3:
            raise _fail("Windows index classification unavailable: malformed entry")
        mode, oid, stage = fields
        if mode not in (b"100644", b"100755") or stage != b"0" or _OID.fullmatch(_decode(oid)) is None:
            raise _fail("unmerged or unsupported Windows index entry")
        found = debug.match(data, end + 1)
        if found is None:
            raise _fail("Windows index classification unavailable: unknown diagnostic shape")
        if int(found.group(1), 16) != 0:
            raise _fail("Windows index special flags are unsupported; preserve original index")
        path = _decode(path_bytes)
        if not path.startswith(".hrn/"):
            project_path(path)
        if not path or path in modes:
            raise _fail("duplicate or empty Windows index path")
        modes[path] = _decode(mode)
        offset = found.end()
    return modes


def _windows_git_state(target: Path) -> dict[str, Any]:
    stages = _git(target, "ls-files", "--stage", "--debug", "--full-name", "--abbrev=64", "-z").stdout
    tracked = _windows_index_modes(stages)
    others = _git(target, "ls-files", "--others", "--exclude-standard", "--full-name", "-z").stdout
    ignored = _git(target, "ls-files", "--others", "--ignored", "--exclude-standard", "--full-name", "-z").stdout
    def paths(raw):
        if raw and not raw.endswith(b"\0"):
            raise _fail("Windows membership classification unavailable")
        values = [_decode(p) for p in raw.split(b"\0") if p]
        if len(values) != len(set(values)):
            raise _fail("duplicate Windows membership entry")
        return {p for p in values if not p.startswith(".hrn/")}
    untracked, excluded = paths(others), paths(ignored)
    tracked = {p: mode for p, mode in tracked.items() if not p.startswith(".hrn/")}
    _path_set(list(tracked.keys() | untracked | excluded))
    if tracked.keys() & untracked or tracked.keys() & excluded or untracked & excluded:
        raise _fail("Windows Git membership classifications overlap")
    return {"raw": (stages, others, ignored), "tracked": tracked, "untracked": untracked, "ignored": excluded}


def _windows_non_git_manifest(target: Path, manifest: dict[str, Any], window: str | None) -> None:
    if _windows_content_policy(window) and classify_target(target)["kind"] == "non-git":
        if any(entry["mode"] == "100755" for side in ("base", "result") for entry in manifest[side]["entries"]):
            raise _fail("Windows non-Git mutation cannot reproduce retained 100755 mode; preserve original manifest")


def _windows_worker_modes(target: Path, manifest: dict[str, Any], window: str | None) -> None:
    """Additional acceptance condition, after all existing baseline/source guards."""
    if not _windows_content_policy(window):
        return
    if classify_target(target)["kind"] != "primary":
        raise _fail("Windows worker mode prediction requires primary Git control")
    state = _windows_git_state(target)
    base = {e["path"]: e for e in manifest["base"]["entries"]}
    result = {e["path"]: e for e in manifest["result"]["entries"]}
    checked_ignore = []
    for path in sorted(base.keys() | result.keys()):
        before, after = base.get(path), result.get(path)
        if before is not None and after is not None and before["mode"] != after["mode"]:
            raise _fail("Windows worker cannot apply an existing-file mode change without changing control index")
        if after is None:
            continue  # Real post-application absence is independently observed.
        predicted = state["tracked"].get(path)
        if predicted is None:
            # ls-files --others cannot name a future absent file. Query ignore
            # policy for its literal name; only successful non-ignored is default.
            ignored = _git(target, "check-ignore", "--no-index", "-q", "--", path, allowed=(0, 1))
            if ignored.returncode != 1 or path in state["ignored"]:
                raise _fail("Windows worker post path is ignored or membership is unsupported")
            checked_ignore.append(path)
            predicted = "100644"
        if predicted != after["mode"]:
            raise _fail("Windows worker post mode cannot be reproduced by current control index/default policy")
    if _windows_git_state(target) != state:
        raise _fail("Windows index or membership changed during worker mode prediction")
    for path in checked_ignore:
        if _git(target, "check-ignore", "--no-index", "-q", "--", path, allowed=(0, 1)).returncode != 1:
            raise _fail("Windows ignore classification changed during worker mode prediction")


def _snapshot_once(target: Path, verified_launcher_sha256: str | None, verified_inventory_id: str | None) -> dict[str, Any]:
    native = _windows_content_policy(verified_inventory_id)
    kind = classify_target(target)["kind"]
    if kind not in {"primary", "linked-worktree", "non-git"}:
        raise _fail("unsupported content target topology")
    native_state = _windows_git_state(target) if native and kind != "non-git" else None
    files = _regular_files(target)
    if kind == "non-git":
        members = set(files)
        policy = hashlib.sha256(b"no-git-v1").hexdigest()
    else:
        _offline_objects(target)
        members: set[str] = set()
        if native_state is not None:
            members = native_state["tracked"].keys() | native_state["untracked"]
            ignored = native_state["ignored"]
        else:
            stages = _git(target, "ls-files", "--stage", "-z").stdout
            for row in stages.split(b"\0"):
                if not row:
                    continue
                header, path_bytes = row.split(b"\t", 1)
                mode, _oid, stage = header.split(b" ")
                path = project_path(_decode(path_bytes)) if not _decode(path_bytes).startswith(".hrn/") else _decode(path_bytes)
                if stage != b"0" or mode not in {b"100644", b"100755"}:
                    raise _fail("unmerged or unsupported tracked entry")
                members.add(path)
            others = _git(target, "ls-files", "--others", "--exclude-standard", "-z").stdout
            members.update(_decode(p) for p in others.split(b"\0") if p)
            members = {p for p in members if not p.startswith(".hrn/")}
            ignored_bytes = _git(target, "ls-files", "--others", "--ignored", "--exclude-standard", "-z").stdout
            ignored = {_decode(p) for p in ignored_bytes.split(b"\0") if p and not _decode(p).startswith(".hrn/")}
        _path_set(list(members | ignored | set(files)))
        if members & ignored or set(files) - members - ignored:
            raise _fail("Git and filesystem membership disagree")
        for path in members - set(files):
            # Deletion is represented by absence only, never an alias/type mismatch.
            if native:
                from .jsonio import windows_path_observation
                if not windows_path_observation(target / path, allow_missing=True)["exists"]:
                    continue
            else:
                try:
                    (target / path).lstat()
                except FileNotFoundError:
                    continue
            raise _fail("tracked path exists under a different filesystem spelling or type")
        policy = _policy(target, files)
    launcher = _verified_launcher_path(verified_launcher_sha256, verified_inventory_id)
    if launcher is not None:
        if launcher not in files or _stable_file(target / launcher)[0] != verified_launcher_sha256:
            raise _fail("managed launcher proof does not match live bytes")
        members.discard(launcher)
    available = set(files)
    entries = []
    for path in sorted(members & available, key=lambda p: p.encode("utf-8")):
        digest, size, mode = _stable_file(target / path)
        if native:
            mode = native_state["tracked"].get(path, "100644") if native_state is not None else "100644"
        entries.append({"path": path, "mode": mode, "sha256": digest, "size_bytes": size})
    if native_state is not None and _windows_git_state(target) != native_state:
        raise _fail("Windows index or membership changed during content observation")
    tree = {"policy_version": 1, "ignore_fingerprint": policy, "entries": entries}
    tree["sha256"] = _digest(tree)
    return tree


def snapshot(target: Path, *, verified_launcher_sha256: str | None = None, verified_inventory_id: str | None = None) -> dict[str, Any]:
    """Read-only, whole project snapshot. No Work scope controls membership.

Two complete observations must agree. This detects ordinary concurrent changes;
trusted callers still need the shared guard and final publication revalidation.
An optional launcher digest is supplied only by the bound-release verifier.
"""
    target = safe_target(target)
    try:
        first = _snapshot_once(target, verified_launcher_sha256, verified_inventory_id)
        second = _snapshot_once(target, verified_launcher_sha256, verified_inventory_id)
    except (OSError, ValueError) as exc:
        raise _fail("unstable or unavailable project snapshot") from exc
    if first != second:
        raise _fail("project changed during snapshot")
    return first


def validate_tree(value: Any) -> dict[str, Any]:
    value = _keys(value, _TREE)
    if type(value["policy_version"]) is not int or value["policy_version"] != 1 or not _sha(value["ignore_fingerprint"]) or not _sha(value["sha256"]):
        raise _fail("tree policy or digest")
    entries = value["entries"]
    if not isinstance(entries, list):
        raise _fail("tree entries must be an array")
    paths = []
    for entry in entries:
        _keys(entry, _ENTRY)
        project_path(entry["path"])
        if entry["mode"] not in ("100644", "100755") or not _sha(entry["sha256"]) or type(entry["size_bytes"]) is not int or entry["size_bytes"] < 0:
            raise _fail("invalid tree entry")
        paths.append(entry["path"])
    _path_set(paths)
    if paths != sorted(paths, key=lambda p: p.encode("utf-8")):
        raise _fail("tree entries are not in canonical path order")
    if value["sha256"] != _digest({k: v for k, v in value.items() if k != "sha256"}):
        raise _fail("tree digest mismatch")
    return value


def _changes(base: dict[str, Any], result: dict[str, Any]) -> list[dict[str, Any]]:
    before = {e["path"]: e for e in base["entries"]}
    after = {e["path"]: e for e in result["entries"]}
    return [{"path": p, "pre": before.get(p), "post": after.get(p)} for p in sorted(before.keys() | after.keys(), key=lambda p: p.encode("utf-8")) if before.get(p) != after.get(p)]


def _retention(value: Any) -> bool:
    # git-check-ref-format's ordinary full heads/tags subset, without invoking Git.
    if not isinstance(value, str) or not value.startswith(("refs/heads/", "refs/tags/")):
        return False
    if any(ord(c) <= 32 or ord(c) == 127 or c in "~^:?*[\\" for c in value) or ".." in value or "@{" in value:
        return False
    return all(p and not p.startswith(".") and not p.endswith((".", ".lock")) for p in value.split("/"))


def validate_manifest(value: Any, *, scope: list[str] | None = None) -> dict[str, Any]:
    value = _keys(value, _MANIFEST)
    if value["record_type"] != "result-manifest" or type(value["schema_version"]) is not int or value["schema_version"] != 1:
        raise _fail("manifest type/version")
    base, result = validate_tree(value["base"]), validate_tree(value["result"])
    if base["ignore_fingerprint"] != result["ignore_fingerprint"]:
        raise _fail("membership policy changed; unsupported result, preserve changes for separate human policy review")
    if value["changes"] != _changes(base, result):
        raise _fail("changes are not the exact tree difference")
    # Explicit field/type checks prevent bool==1 or unknown fields surviving equality.
    if not isinstance(value["changes"], list):
        raise _fail("changes must be an array")
    for change in value["changes"]:
        _keys(change, {"path", "pre", "post"})
        for side in ("pre", "post"):
            if change[side] is not None:
                _keys(change[side], _ENTRY)
                if type(change[side]["size_bytes"]) is not int:
                    raise _fail("change entry size must be integer")
    fields = [value[k] for k in ("base_commit", "candidate_commit", "base_retention_ref", "candidate_retention_ref")]
    if any(v is not None for v in fields):
        if not all(isinstance(v, str) and _OID.fullmatch(v) for v in fields[:2]) or not all(_retention(v) for v in fields[2:]):
            raise _fail("worker manifest requires two OIDs and existing named retention refs")
    if scope is not None:
        if not isinstance(scope, list):
            raise _fail("scope must be an array")
        _path_set(scope)
        if not {c["path"] for c in value["changes"]}.issubset(set(scope)):
            raise _fail("result changes exceed exact file scope")
    return value


def make_manifest(base: dict[str, Any], result: dict[str, Any], *, scope: list[str], base_commit: str | None = None, candidate_commit: str | None = None, base_retention_ref: str | None = None, candidate_retention_ref: str | None = None) -> dict[str, Any]:
    base, result = validate_tree(base), validate_tree(result)
    value = {"record_type": "result-manifest", "schema_version": 1, "base": base, "result": result, "changes": _changes(base, result), "base_commit": base_commit, "candidate_commit": candidate_commit, "base_retention_ref": base_retention_ref, "candidate_retention_ref": candidate_retention_ref}
    validate_manifest(value, scope=scope)
    return copy.deepcopy(value)


def observe_recovery(manifest: dict[str, Any], current: dict[str, Any]) -> dict[str, Any]:
    """Pure content classification, never authorization to publish or cancel.

Worker cancellation also needs live occupant/ancestor preflight and valid records;
resume needs durable Git sources, unchanged authority/intent/product/evidence.
"""
    validate_manifest(manifest)
    validate_tree(current)
    before = {e["path"]: e for e in manifest["base"]["entries"]}
    after = {e["path"]: e for e in manifest["result"]["entries"]}
    now = {e["path"]: e for e in current["entries"]}
    paths = {c["path"] for c in manifest["changes"]}
    states = {p: "pre" if now.get(p) == before.get(p) else "post" if now.get(p) == after.get(p) else "neither" for p in sorted(paths)}
    outside = any(before.get(p) != now.get(p) for p in (before.keys() | now.keys()) - paths)
    same_policy = current["ignore_fingerprint"] == manifest["base"]["ignore_fingerprint"]
    return {"whole_result_matches": current == manifest["result"], "changed_paths": states, "outside_drift": outside, "policy_matches": same_policy, "all_changed_paths_pre": same_policy and all(s == "pre" for s in states.values()), "content_resume_possible": not outside and same_policy and "neither" not in states.values(), "authority_verification": "required"}


def _preflight_changed_paths(target: Path, manifest: dict[str, Any], *, verified_launcher_sha256: str | None = None, verified_inventory_id: str | None = None) -> dict[str, str]:
    """Inspect actual occupants including ignored files before worker apply/cancel.

This read-only check does not reserve paths. Repeat under the outer writer guard
immediately before each write and before publication; outside actors are trusted.
"""
    target = Path(classify_target(target, mutation=True)["target"])
    validate_manifest(manifest)
    native = _windows_content_policy(verified_inventory_id)
    native_state = (_windows_git_state(target) if native and classify_target(target)["kind"] != "non-git" else None)
    states: dict[str, str] = {}
    launcher_name = _verified_launcher_path(verified_launcher_sha256, verified_inventory_id)
    for change in manifest["changes"]:
        path = change["path"]
        if path == launcher_name and launcher_name is not None:
            raise _fail("managed launcher cannot enter a Work diff")
        current = target
        missing = False
        pieces = path.split("/")
        for index, piece in enumerate(pieces):
            if not missing:
                entries = {p.name: p for p in current.iterdir()}
                if any(unicodedata.normalize("NFC", name.casefold()) == unicodedata.normalize("NFC", piece.casefold()) and name != piece for name in entries):
                    raise _fail("case alias occupies a changed path or ancestor")
                missing = piece not in entries
            current = current / piece
            if not missing:
                mode = current.lstat().st_mode
                if index < len(pieces) - 1 and not stat.S_ISDIR(mode):
                    raise _fail("changed path has unsafe ancestor")
                if index == len(pieces) - 1 and not stat.S_ISREG(mode):
                    raise _fail("changed path has unsupported occupant")
        if native:
            from .jsonio import windows_path_observation
            physical = windows_path_observation(current, mutation=True, allow_missing=True)
            if physical["exists"] == missing:
                raise _fail("changed path existence changed during native observation")
        observed = None
        if not missing:
            digest, size, mode = _stable_file(current)
            if native:
                if native_state is not None and path not in native_state["tracked"] and path not in native_state["untracked"]:
                    states[path] = "neither"  # Preserve ignored/unknown physical occupant.
                    continue
                mode = native_state["tracked"].get(path, "100644") if native_state is not None else "100644"
            observed = {"path": path, "sha256": digest, "mode": mode, "size_bytes": size}
        states[path] = "pre" if observed == change["pre"] else "post" if observed == change["post"] else "neither"
    if native_state is not None and _windows_git_state(target) != native_state:
        raise _fail("Windows index or membership changed during changed-path preflight")
    return states


def _allows_unchanged_crlf(verified_inventory_id: str | None) -> bool:
    """A verified active window, never a caller-facing conversion option."""
    return verified_inventory_id in ("checkout-1", "entry-1", "delegation-1", "continuation-1", "windows-2", "official-execution-1", "official-execution-2")


def _unchanged_crlf_matches(target: Path, manifest: dict[str, Any],
                            tables: dict[str, dict[str, tuple[str, str]]],
                            entries: dict[str, dict[str, dict[str, Any]]],
                            path: str, data: bytes, expected: dict[str, Any]) -> bool:
    """Prove one unchanged raw checkout entry; never convert application bytes."""
    if tables["pre"].get(path) != tables["post"].get(path):
        return False
    before = entries["base"].get(path)
    after = entries["result"].get(path)
    if before != after or before != expected:
        return False
    # A deterministic LF-to-CRLF expansion cannot justify other transformations.
    if b"\n" not in data or b"\r" in data or b"\0" in data:
        return False
    checkout = data.replace(b"\n", b"\r\n")
    if len(checkout) != expected["size_bytes"] or hashlib.sha256(checkout).hexdigest() != expected["sha256"]:
        return False
    attributes = {p for table in tables.values() for p in table if p.rsplit("/", 1)[-1] == ".gitattributes"}
    if any(tables["pre"].get(p) != tables["post"].get(p) for p in attributes):
        return False
    # --source still consults info/attributes. Do not let unretained overrides
    # masquerade as a policy bound by both commits.
    # Asking Git for the absolute attributes path resolves its final symlink.
    # Keep the untrusted suffix literal so links remain observable here.
    common = Path(_decode(_git(target, "rev-parse", "--path-format=absolute", "--git-common-dir").stdout).rstrip("\n"))
    if not common.is_absolute():
        common = target / common
    info = common / "info" / "attributes"
    if info.parent.is_symlink() or info.is_symlink() or (info.exists() and _stable_file(info)[1] != 0):
        raise _fail("unchanged CRLF proof requires no info/attributes overrides")
    names = ("text", "eol", "filter", "working-tree-encoding", "ident", "crlf")
    for commit in dict.fromkeys((manifest["base_commit"], manifest["candidate_commit"])):
        for isolated in (True, False):
            options = ("-c", "core.attributesFile=/dev/null") if isolated else ()
            output = _git(target, *options, "check-attr", "--source=" + commit, "-z", *names, "--", path, isolated_attributes=isolated).stdout
            fields = output.split(b"\0")
            if fields[-1:] != [b""] or len(fields) != len(names) * 3 + 1:
                raise _fail("CRLF attribute observation is malformed")
            values = {}
            for index, name in enumerate(names):
                file, attribute, value = map(_decode, fields[index * 3:index * 3 + 3])
                if file != path or attribute != name:
                    raise _fail("CRLF attribute observation differs from requested path")
                values[name] = value
            if values["text"] != "set" or values["eol"] != "crlf" or any(values[name] not in {"unspecified", "unset"} for name in names[2:]):
                return False
    return True


def _verify_worker_sources(target: Path, manifest: dict[str, Any], *, verified_launcher_sha256: str | None = None, verified_inventory_id: str | None = None) -> dict[str, dict[str, bytes | None]]:
    """Read durable pre/post blobs from existing control refs without creating refs.

Returned bytes are reconstruction inputs, not acceptance authority. A caller must
also verify whole-tree currentness, physical path preflight and the record graph.
"""
    target = Path(classify_target(target, mutation=True)["target"])
    if classify_target(target)["kind"] != "primary":
        raise _fail("worker recovery requires a primary Git control target")
    validate_manifest(manifest)
    _offline_objects(target)
    if manifest["base_commit"] is None:
        raise _fail("local result has no worker Git sources")
    tables: dict[str, dict[str, tuple[str, str]]] = {}
    for side, prefix in (("pre", "base"), ("post", "candidate")):
        commit, ref = manifest[prefix + "_commit"], manifest[prefix + "_retention_ref"]
        _git(target, "check-ref-format", ref)
        exact_oid = _decode(_git(target, "show-ref", "--verify", "--hash", ref).stdout).strip()
        if _OID.fullmatch(exact_oid) is None:
            raise _fail("invalid exact retention ref")
        tip = _decode(_git(target, "rev-parse", "--verify", "--end-of-options", exact_oid + "^{commit}").stdout).strip()
        if _OID.fullmatch(tip) is None:
            raise _fail("invalid retention commit")
        _git(target, "merge-base", "--is-ancestor", commit, tip)
        table: dict[str, tuple[str, str]] = {}
        for row in _git(target, "ls-tree", "-r", "-z", "--full-tree", commit).stdout.split(b"\0"):
            if row:
                header, path = row.split(b"\t", 1)
                mode, kind, oid = header.split(b" ")
                table[_decode(path)] = (_decode(mode), _decode(oid)) if kind == b"blob" else ("unsupported", _decode(oid))
        tables[side] = table
    _git(target, "merge-base", "--is-ancestor", manifest["base_commit"], manifest["candidate_commit"])
    changed = {p for p in tables["pre"].keys() | tables["post"].keys() if tables["pre"].get(p) != tables["post"].get(p)}
    if changed != {c["path"] for c in manifest["changes"]}:
        raise _fail("whole Git diff differs from manifest; metadata or omitted tracked change")
    launcher_name = _verified_launcher_path(verified_launcher_sha256, verified_inventory_id)
    # Whole commit trees bind unchanged paths too. Excluded authority may remain
    # identical in both commits; it cannot be hidden in a worker result diff.
    blobs: dict[str, bytes] = {}
    verified_crlf: set[str] = set()
    entries = {name: {e["path"]: e for e in manifest[name]["entries"]} for name in ("base", "result")}
    for side, name in (("pre", "base"), ("post", "result")):
        table = tables[side]
        project = {p: v for p, v in table.items() if not p.startswith(".hrn/")}
        if verified_launcher_sha256 is not None:
            launcher = project.pop(launcher_name, None)
            if launcher is None or launcher[0] != "100755":
                raise _fail("commit lacks verified executable managed launcher")
            data = _git(target, "cat-file", "blob", launcher[1]).stdout
            if hashlib.sha256(data).hexdigest() != verified_launcher_sha256:
                raise _fail("commit launcher differs from bound runtime")
        _path_set(list(project))
        expected = entries[name]
        if project.keys() != expected.keys():
            raise _fail("whole commit membership differs from manifest")
        for path, (mode, oid) in project.items():
            if mode not in {"100644", "100755"} or mode != expected[path]["mode"]:
                raise _fail("whole commit mode differs from manifest")
            if oid not in blobs:
                blobs[oid] = _git(target, "cat-file", "blob", oid).stdout
            data = blobs[oid]
            if len(data) != expected[path]["size_bytes"] or hashlib.sha256(data).hexdigest() != expected[path]["sha256"]:
                if path not in verified_crlf:
                    if not _allows_unchanged_crlf(verified_inventory_id) or not _unchanged_crlf_matches(target, manifest, tables, entries, path, data, expected[path]):
                        raise _fail("whole commit content differs from manifest")
                    verified_crlf.add(path)
    sources: dict[str, dict[str, bytes | None]] = {}
    for change in manifest["changes"]:
        sources[change["path"]] = {}
        for side in ("pre", "post"):
            entry = change[side]
            source = tables[side].get(change["path"])
            if entry is None:
                if source is not None:
                    raise _fail("Git source contradicts absent manifest entry")
                data = None
            else:
                if source is None or source[0] != entry["mode"]:
                    raise _fail("Git source missing or mode differs")
                # Blob ID is read from ls-tree, never a caller-provided revision expression.
                data = blobs[source[1]]
                if len(data) != entry["size_bytes"] or hashlib.sha256(data).hexdigest() != entry["sha256"]:
                    raise _fail("Git blob differs from manifest content")
            sources[change["path"]][side] = data
    return sources


def _offline_objects(target: Path) -> None:
    """Version-independent refusal of repositories that may fetch/borrow objects."""
    config = _git(target, "config", "--get-regexp", r"^(remote\..*\.promisor|extensions\.partialclone)$", allowed=(0, 1))
    if config.returncode == 0:
        raise _fail("promisor/partial clone is unsupported; no lazy fetching")
    common = Path(_decode(_git(target, "rev-parse", "--path-format=absolute", "--git-common-dir").stdout).rstrip("\n"))
    objects = common / "objects"
    if sys.platform == "win32":
        from .jsonio import windows_path_observation
        windows_path_observation(objects)
    if objects.is_symlink() or not objects.is_dir():
        raise _fail("external object directory is unsupported")
    for directory, dirs, files in os.walk(objects, followlinks=False):
        for name in dirs + files:
            entry = Path(directory) / name
            if sys.platform == "win32":
                windows_path_observation(entry)
            mode = entry.lstat().st_mode
            if not (stat.S_ISDIR(mode) or stat.S_ISREG(mode)):
                raise _fail("external or special object storage is unsupported")
    for name in ("alternates", "http-alternates"):
        path = objects / "info" / name
        if path.exists() or path.is_symlink():
            raise _fail("external object alternates are unsupported")


def preflight_changed_paths(target: Path, manifest: dict[str, Any], *, verified_launcher_sha256: str | None = None, verified_inventory_id: str | None = None) -> dict[str, str]:
    """Read actual changed-path occupants; does not grant apply/cancel authority."""
    try:
        return _preflight_changed_paths(target, manifest, verified_launcher_sha256=verified_launcher_sha256, verified_inventory_id=verified_inventory_id)
    except (OSError, ValueError) as exc:
        raise _fail("changed-path preflight unavailable or unstable") from exc


def verify_worker_sources(target: Path, manifest: dict[str, Any], *, verified_launcher_sha256: str | None = None, verified_inventory_id: str | None = None) -> dict[str, dict[str, bytes | None]]:
    """Verify local-only retained blobs; does not grant acceptance authority."""
    try:
        return _verify_worker_sources(target, manifest, verified_launcher_sha256=verified_launcher_sha256, verified_inventory_id=verified_inventory_id)
    except (OSError, ValueError) as exc:
        raise _fail("worker sources unavailable or malformed") from exc

# Typed Work records use the bound-release verifier by default, including CLI writers.
_RECORD_BASE = {"record_type", "schema_version", "authority_home_id", "work_id"}
_PROVENANCE = {"record_id", "observed_at", "observed_scope", "unavailable_scope"}
_REVISION_KEYS = _RECORD_BASE | _PROVENANCE | {"author", "operation", "expected_prior_selection", "intent_ref", "scope", "document_refs", "evidence_refs", "result_refs", "progress", "next_action", "relations", "rebind_from", "execution_context"}
_SELECTION_KEYS = _RECORD_BASE | _PROVENANCE | {"parent_selection_ref", "revision_ref", "decision_ref", "operation_id"}
_TICKET_KEYS = {"record_type", "schema_version", "authority_home_id", "action", "actor", "object", "target_revision_ref", "expected_selection_ref", "intent_ref", "product_binding_ref", "document_refs", "evidence_refs", "execution_mode", "supersedes_decision_ref", "reason", "request_id", "observed_at", "target_fingerprint"}
_RECORD_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]{0,95}\Z")


def _record_error(message: str) -> ContractError:
    return ContractError("HV2-WORK-RECORD", message)


def _require(condition: bool, detail: str) -> None:
    if not condition:
        raise _record_error(detail)


def _identifier(value: Any) -> None:
    _require(isinstance(value, str) and _RECORD_ID.fullmatch(value) is not None, "invalid record identifier")


def _text(value: Any) -> None:
    _require(isinstance(value, str) and bool(value.strip()), "nonempty text required")


def _strings(value: Any) -> None:
    _require(isinstance(value, list), "text array required")
    for item in value:
        _text(item)


def validate_ref(value: Any, *, nullable: bool = False) -> None:
    if value is None and nullable:
        return
    _keys(value, {"id", "sha256"})
    _identifier(value["id"])
    _require(_sha(value["sha256"]), "invalid reference digest")


def record_ref(record: dict[str, Any], id_key: str = "record_id") -> dict[str, str]:
    return {"id": record[id_key], "sha256": _digest(record)}


def _qualified(value: Any, *, kind: str | None = None) -> None:
    _keys(value, {"authority_home_id", "kind", "id"})
    _identifier(value["authority_home_id"]); _identifier(value["id"])
    _require(value["kind"] in ("intent", "work") and (kind is None or value["kind"] == kind), "wrong object kind")


def validate_intent_ref(value: Any) -> None:
    _keys(value, {"authority_home_id", "kind", "id", "revision_ref", "acceptance_ref", "selection_ref"})
    _qualified({k: value[k] for k in ("authority_home_id", "kind", "id")}, kind="intent")
    for key in ("revision_ref", "acceptance_ref", "selection_ref"):
        validate_ref(value[key])


def _external_refs(value: Any, *, evidence: bool) -> None:
    _require(isinstance(value, list), "references must be an array")
    paths = []
    for item in value:
        _keys(item, {"path", "sha256", "required", "verification" if evidence else "role"})
        paths.append(project_path(item["path"]))
        _require(_sha(item["sha256"]) and type(item["required"]) is bool, "invalid external reference")
        if evidence:
            _require(item["verification"] in ("worker-observed", "control-required"), "unknown evidence provenance")
            _require(not item["required"] or item["verification"] == "control-required", "required evidence must be accessible on control")
        else:
            _require(item["role"] in ("decision", "brief", "plan", "narrative", "result"), "unknown document role")
    _path_set(paths)


def validate_ticket(value: Any) -> dict[str, Any]:
    _keys(value, _TICKET_KEYS)
    _require(value["record_type"] == "confirmation-ticket" and type(value["schema_version"]) is int and value["schema_version"] == 1, "ticket type/version")
    _identifier(value["authority_home_id"]); _identifier(value["request_id"])
    for key in ("actor", "reason", "observed_at"):
        _text(value[key])
    _qualified(value["object"])
    _require(value["object"]["authority_home_id"] == value["authority_home_id"], "ticket authority mismatch")
    _require(value["action"] in ("accept", "reject", "rebind", "revoke") and _sha(value["target_fingerprint"]), "ticket action/target")
    validate_ref(value["target_revision_ref"]); validate_ref(value["product_binding_ref"])
    validate_ref(value["expected_selection_ref"], nullable=True); validate_ref(value["supersedes_decision_ref"], nullable=True)
    _external_refs(value["document_refs"], evidence=False); _external_refs(value["evidence_refs"], evidence=True)
    if value["object"]["kind"] == "intent":
        _require(value["action"] == "accept" and value["intent_ref"] is None and value["execution_mode"] is None and value["supersedes_decision_ref"] is None, "invalid intent confirmation")
    else:
        validate_intent_ref(value["intent_ref"])
        _require(value["execution_mode"] in ("local", "isolated-worktree"), "invalid execution mode")
    return value


def validate_work_record(value: Any) -> dict[str, Any]:
    _require(isinstance(value, dict), "record object required")
    kind = value.get("record_type")
    fields = {
        "work-identity": _RECORD_BASE | {"work_type", "created_at", "acceptance_authority", "lineage"},
        "work-revision": _REVISION_KEYS,
        "work-decision": _RECORD_BASE | {"record_id", "confirmation"},
        "work-selection": _SELECTION_KEYS,
        "work-current": _RECORD_BASE | {"selection_ref"},
    }
    _require(isinstance(kind, str) and kind in fields, "unknown Work record type")
    version = value.get("schema_version")
    _require(type(version) is int and version in ((1, 2) if kind == "work-revision" else (1,)), "unsupported record version")
    _keys(value, fields[kind] | ({"umbrella_evidence"} if version == 2 else set()))
    _identifier(value["authority_home_id"]); _identifier(value["work_id"])
    if "record_id" in value:
        _identifier(value["record_id"])
    if kind in ("work-revision", "work-selection"):
        _text(value["observed_at"]); _strings(value["observed_scope"]); _strings(value["unavailable_scope"])
    if kind == "work-identity":
        for key in ("work_type", "created_at", "acceptance_authority"):
            _text(value[key])
        if value["lineage"] is not None:
            _qualified(value["lineage"])
    elif kind == "work-current":
        validate_ref(value["selection_ref"])
    elif kind == "work-selection":
        validate_ref(value["parent_selection_ref"], nullable=True)
        validate_ref(value["revision_ref"]); validate_ref(value["decision_ref"], nullable=True)
        _identifier(value["operation_id"])
    elif kind == "work-decision":
        ticket = validate_ticket(value["confirmation"])
        _require(ticket["object"] == {"authority_home_id": value["authority_home_id"], "kind": "work", "id": value["work_id"]}, "decision object mismatch")
        _require(value["record_id"] == "decision-" + _digest(ticket), "decision ID does not bind complete ticket")
    else:
        _text(value["author"]); _text(value["next_action"])
        _require(value["operation"] in ("start", "checkpoint", "submit-result", "rework", "rebind"), "invalid revision operation")
        _require(value["progress"] in ("planned", "active", "review", "rework"), "agent cannot declare completion")
        _require((value["progress"] == "review") == (value["operation"] == "submit-result"), "review requires submitted result")
        validate_ref(value["expected_prior_selection"], nullable=True)
        validate_intent_ref(value["intent_ref"])
        _require(value["intent_ref"]["authority_home_id"] == value["authority_home_id"], "cross-home intent")
        _require(isinstance(value["scope"], list), "scope array required"); _path_set(value["scope"])
        _external_refs(value["document_refs"], evidence=False); _external_refs(value["evidence_refs"], evidence=True)
        _keys(value["result_refs"], {"manifest"}); validate_ref(value["result_refs"]["manifest"])
        _keys(value["execution_context"], {"mode", "attempt_id"})
        _identifier(value["execution_context"]["attempt_id"])
        _require(value["execution_context"]["mode"] in ("local", "isolated-worktree"), "invalid execution mode")
        _require(isinstance(value["relations"], list), "relations array required")
        seen = set()
        for relation in value["relations"]:
            _keys(relation, {"relation", "target"}); _qualified(relation["target"], kind="work")
            _require(relation["relation"] in ("parent", "depends_on", "continues"), "unknown relation")
            _require(relation["target"]["authority_home_id"] == value["authority_home_id"] and relation["target"]["id"] != value["work_id"], "cross-home or self relation")
            key = (relation["relation"], relation["target"]["id"])
            _require(key not in seen, "duplicate relation"); seen.add(key)
        if version == 2:
            from .umbrella import validate_evidence
            validate_evidence(value["umbrella_evidence"], value["authority_home_id"], submitted=value["operation"] == "submit-result")
        _require((value["operation"] == "rebind") == (value["rebind_from"] is not None), "rebind provenance")
        if value["rebind_from"] is not None:
            validate_intent_ref(value["rebind_from"])
    return value


def _resolve(records: dict[str, Any], ref: Any, *, nullable: bool = False) -> Any:
    validate_ref(ref, nullable=nullable)
    if ref is None:
        return None
    _require(ref["id"] in records and _digest(records[ref["id"]]) == ref["sha256"], "missing or changed referenced record")
    return records[ref["id"]]


def _bound_delegation(identity, revision, intent_graphs):
    """Resolve K from verified exact intent context, never a caller verdict."""
    from .intent import _resolve_workspace_intent, validate_delegation
    ref = revision["intent_ref"]
    _require(intent_graphs is not None and ref["id"] in intent_graphs,
             "delegated decision requires complete verified intent context")
    bound, _ = _resolve_workspace_intent(intent_graphs[ref["id"]], ref["id"], ref)
    _require(bound["acceptance_authority"] == identity["acceptance_authority"], "Work and intent authorities differ")
    grant = bound["acceptance_delegation"]
    if grant is None:
        return None, None
    validate_delegation(grant, identity["authority_home_id"], identity["acceptance_authority"])
    if grant["work"]["id"] != identity["work_id"]:
        return grant, None
    key = (identity["authority_home_id"], identity["work_id"], ref["id"],
           ref["revision_ref"]["id"], ref["revision_ref"]["sha256"])
    return grant, key


def work_graph(identity: dict[str, Any], revisions: dict[str, Any], decisions: dict[str, Any], selections: dict[str, Any], manifests: dict[str, Any], current: dict[str, Any] | None, *, intent_graphs: dict[str, Any] | None = None) -> dict[str, Any]:
    """Validate every record and derive state from exact selections, never recency.

This checks persisted Work semantics. Intent graph, release binding, live content,
relations across Works and human confirmation remain publication prerequisites.
"""
    validate_work_record(identity)
    _require(identity["record_type"] == "work-identity", "identity required")
    groups = ((revisions, "work-revision"), (decisions, "work-decision"), (selections, "work-selection"))
    for records, kind in groups:
        _require(isinstance(records, dict), "record map required")
        _require(len({key.casefold() for key in records}) == len(records), "record ID case collision")
        for key, record in records.items():
            validate_work_record(record)
            _require(record["record_type"] == kind and record["record_id"] == key, "record kind/filename mismatch")
            _require(all(record[k] == identity[k] for k in ("work_id", "authority_home_id")), "foreign record identity")
    for key, manifest in manifests.items():
        validate_manifest(manifest)
        _require(key == _digest(manifest), "manifest filename digest mismatch")
    if current is not None:
        validate_work_record(current)
        _require(current["record_type"] == "work-current" and all(current[k] == identity[k] for k in ("work_id", "authority_home_id")), "foreign selector")
        _resolve(selections, current["selection_ref"])

    def revision(selection): return _resolve(revisions, selection["revision_ref"])
    def outcome(selection):
        if selection is None: return "empty"
        decision = _resolve(decisions, selection["decision_ref"], nullable=True)
        return {"accept": "completed", "reject": "rejected", "revoke": "revoked", "rebind": revision(selection)["progress"]}[decision["confirmation"]["action"]] if decision else revision(selection)["progress"]

    for record in revisions.values():
        prior = _resolve(selections, record["expected_prior_selection"], nullable=True)
        manifest_ref = record["result_refs"]["manifest"]
        _require(manifest_ref["id"] == manifest_ref["sha256"], "manifest ID must be digest")
        manifest = _resolve(manifests, manifest_ref)
        validate_manifest(manifest, scope=record["scope"])
        mode = record["execution_context"]["mode"]
        _require((mode == "local") == (manifest["base_commit"] is None), "manifest execution provenance differs")
        operation = record["operation"]
        _require((operation == "start") == (prior is None), "start/prior mismatch")
        if operation != "submit-result":
            _require(manifest["base"] == manifest["result"] and not manifest["changes"], "baseline revision contains changes")
        if mode == "isolated-worktree":
            _require(operation != "rework", "worker rework requires human baseline refresh")
            if operation in ("start", "rebind"):
                _require(manifest["base_commit"] == manifest["candidate_commit"], "worker baseline requires one commit")
        if prior is not None:
            old = revision(prior)
            if old["schema_version"] == 2:
                _require(record["schema_version"] == 2, "selected parent cannot downgrade record schema")
            if record["schema_version"] == 2 and operation != "rebind":
                _require(old["schema_version"] == 2 and record["umbrella_evidence"]["children"] == old["umbrella_evidence"]["children"], "parent evidence differs from selected baseline")
            _require(mode == old["execution_context"]["mode"], "Work execution mode cannot change")
            if mode == "isolated-worktree" and operation == "checkpoint":
                _require(old["operation"] != "submit-result", "worker checkpoint cannot absorb submitted result; human baseline refresh required")
            previous = _resolve(manifests, old["result_refs"]["manifest"])
            _require(manifest["base"]["ignore_fingerprint"] == previous["result"]["ignore_fingerprint"], "ignore policy change requires a separately supported workflow")
            if operation in ("checkpoint", "rework"):
                _require(manifest["result"] == previous["result"], "agent baseline cannot absorb unreviewed content drift")
            _require(outcome(prior) != "completed", "completed Work requires human revoke before new revision")
            if operation == "rebind":
                _require(record["rebind_from"] == old["intent_ref"], "rebind provenance differs from prior intent")
                if record["intent_ref"] == old["intent_ref"]:
                    _require(mode == "isolated-worktree", "local rebind must explicitly change intent")
                    _require(record["scope"] == old["scope"] and record["progress"] == "active", "worker baseline refresh must preserve scope and remain active")
            else:
                _require(record["intent_ref"] == old["intent_ref"], "intent change requires rebind")
            if outcome(prior) in ("rejected", "revoked"):
                _require(operation in ("rework", "rebind"), "rejected/revoked result requires rework")
            if operation == "rework":
                _require(outcome(prior) in ("rejected", "revoked"), "rework needs reject/revoke")
            if operation == "submit-result":
                previous = _resolve(manifests, old["result_refs"]["manifest"])
                _require(old["operation"] != "submit-result" and outcome(prior) not in ("review", "rejected", "revoked"), "new result needs a selected baseline")
                _require(manifest["base"] == previous["result"], "submission base differs from selected baseline")

    # Validate all decisions, including orphan/pending ones, before deriving current.
    delegated = []
    request_ids: dict[str, str] = {}
    superseded: dict[str, str] = {}
    for key, decision in decisions.items():
        t = decision["confirmation"]
        r = _resolve(revisions, t["target_revision_ref"])
        prior = _resolve(selections, t["expected_selection_ref"])
        if t["actor"] != identity["acceptance_authority"]:
            delegated.append((key, t, r))
        for field in ("intent_ref", "document_refs", "evidence_refs"):
            _require(t[field] == r[field], "ticket differs from revision " + field)
        _require(t["execution_mode"] == r["execution_context"]["mode"], "ticket mode differs")
        _require(t["request_id"] not in request_ids or request_ids[t["request_id"]] == key, "request ID reused with different ticket")
        request_ids[t["request_id"]] = key
        action = t["action"]
        if action == "rebind":
            _require(t["supersedes_decision_ref"] is None and r["operation"] == "rebind" and r["expected_prior_selection"] == t["expected_selection_ref"], "invalid rebind decision")
        else:
            _require(prior["revision_ref"] == t["target_revision_ref"], "decision target is not selected revision")
            if action == "revoke":
                _require(outcome(prior) == "completed" and t["supersedes_decision_ref"] == prior["decision_ref"], "revoke needs current completed acceptance")
            else:
                _require(prior["decision_ref"] is None and r["operation"] == "submit-result" and r["progress"] == "review", "accept/reject needs undecided submitted result")
                supersedes = t["supersedes_decision_ref"]
                if supersedes is not None:
                    old = _resolve(decisions, supersedes)["confirmation"]
                    _require(action == "reject" and old["action"] == "accept" and old["supersedes_decision_ref"] is None and all(old[f] == t[f] for f in ("expected_selection_ref", "target_revision_ref")), "invalid cancellation chain")
                    _require(supersedes["id"] not in superseded, "multiple cancellation successors")
                    superseded[supersedes["id"]] = key
    children: dict[str | None, str] = {}
    selected_decisions: dict[str, str] = {}
    operation_ids: set[str] = set()
    for key, selection in selections.items():
        parent = _resolve(selections, selection["parent_selection_ref"], nullable=True)
        parent_id = parent["record_id"] if parent else None
        _require(parent_id not in children, "selection fork")
        children[parent_id] = key
        r = revision(selection)
        decision = _resolve(decisions, selection["decision_ref"], nullable=True)
        _require(selection["operation_id"] not in operation_ids, "operation ID reused")
        operation_ids.add(selection["operation_id"])
        if decision:
            t = decision["confirmation"]
            _require(t["expected_selection_ref"] == selection["parent_selection_ref"] and t["target_revision_ref"] == selection["revision_ref"] and t["request_id"] == selection["operation_id"], "selection does not publish exact decision")
            _require(decision["record_id"] not in selected_decisions, "decision selected twice")
            selected_decisions[decision["record_id"]] = key
        else:
            _require(r["operation"] != "rebind" and r["expected_prior_selection"] == selection["parent_selection_ref"], "agent selection does not match expected prior")
            _require(selection["operation_id"] not in request_ids, "agent operation ID collides with human request")
    _require(not (set(superseded) & set(selected_decisions)), "cannot cancel a decision with durable selection")
    chain = []
    node = children.get(None)
    while node is not None:
        _require(node not in chain, "selection cycle")
        chain.append(node); node = children.get(node)
    _require(len(chain) == len(selections), "disconnected or cyclic selection graph")
    # Only traverse ancestry after its complete shape, references and acyclicity
    # are established. Later revocation never invalidates an earlier decision.
    consumed = {}
    for decision_id, ticket, target_revision in delegated:
        grant, key = _bound_delegation(identity, target_revision, intent_graphs)
        _require(grant is not None and key is not None, "no grant for this Work")
        _require(ticket["actor"] == grant["delegate_actor"] and ticket["action"] == "accept"
                 and ticket["supersedes_decision_ref"] is None, "actor/action outside delegation")
        _require(target_revision["schema_version"] == 1 and ticket["execution_mode"] == "isolated-worktree"
                 and set(target_revision["scope"]) == set(grant["scope"]), "delegated Work scope/mode/role differs")
        _require(key not in consumed or consumed[key] == decision_id, "delegation already consumed")
        consumed[key] = decision_id
        node = _resolve(selections, ticket["expected_selection_ref"])
        while node is not None:
            ancestor_revision = revision(node)
            _require(ancestor_revision["schema_version"] == 1, "parent ancestry cannot delegate")
            ancestor_decision = _resolve(decisions, node["decision_ref"], nullable=True)
            if ancestor_decision and ancestor_decision["confirmation"]["action"] == "revoke":
                revoked = _resolve(decisions, ancestor_decision["confirmation"]["supersedes_decision_ref"])
                revoked_revision = _resolve(revisions, revoked["confirmation"]["target_revision_ref"])
                _, revoked_key = _bound_delegation(identity, revoked_revision, intent_graphs)
                _require(revoked_key != key, "selected revoke bars this delegation draft")
            node = _resolve(selections, node["parent_selection_ref"], nullable=True)
    current_id = current["selection_ref"]["id"] if current else None
    selected_index = chain.index(current_id) if current_id is not None else -1
    pending_selections = chain[selected_index + 1:]
    _require(len(pending_selections) <= 1, "more than one unpublished selection")
    resolved = set(selected_decisions) | {old for old, cancel in superseded.items() if cancel in selected_decisions}
    pending_decisions = set(decisions) - resolved
    _require(not (pending_selections and pending_decisions), "pending selection must resolve before another decision")
    grouped: dict[str, set[str]] = {}
    for key in pending_decisions:
        prior_id = decisions[key]["confirmation"]["expected_selection_ref"]["id"]
        _require(prior_id == current_id, "pending decision on historical selection")
        grouped.setdefault(prior_id, set()).add(key)
    for keys in grouped.values():
        _require(len(keys) == 1 or (len(keys) == 2 and any(old in keys and new in keys for old, new in superseded.items())), "incomparable pending decisions")
    return {"state": outcome(selections[current_id]) if current_id else "empty", "current": current, "pending_decisions": sorted(pending_decisions), "pending_selections": pending_selections, "orphan_revisions": sorted(set(revisions) - {s["revision_ref"]["id"] for s in selections.values()}), "identity": identity, "revisions": revisions, "decisions": decisions, "selections": selections, "manifests": manifests}


def _authority_directory(target: Path, category: str, object_id: str) -> tuple[Path, str]:
    from .workspace import _file_json, _require_kind, validate_format
    _identifier(object_id)
    target = safe_target(target)
    root = target / ".hrn"
    _require_kind(root, True)
    authority = validate_format(_file_json(root / "format.json"))["authority_home_id"]
    directory = root / category
    _require_kind(directory, True)
    names = [p.name for p in directory.iterdir()]
    _require(len({n.casefold() for n in names}) == len(names), "object ID case collision")
    _require(object_id in names, "object directory missing or incorrectly spelled")
    _require_kind(directory / object_id, True)
    return directory / object_id, authority


def _record_tree(home: Path, folders: set[str], *, allow_continuation: bool = False) -> dict[str, Any]:
    from .workspace import _require_kind
    from .jsonio import load_json
    data: dict[str, Any] = {}
    for member in home.iterdir():
        if allow_continuation and member.name == "continuation":
            _require_kind(member, True)
            continue  # The separate bounded reader validates this entire subtree.
        if member.name in folders:
            _require_kind(member, True)
            names = [p.name for p in member.iterdir()]
            _require(len({n.casefold() for n in names}) == len(names), "record path alias")
            for path in member.iterdir():
                _require_kind(path, False)
                _require(path.suffix == ".json", "unknown record file")
                _identifier(path.stem)
                data[member.name + "/" + path.name] = load_json(path, require_canonical=True)
        else:
            _require(member.name in ("identity.json", "current.json"), "unknown object member: " + member.name)
            _require_kind(member, False)
            data[member.name] = load_json(member, require_canonical=True)
    return data


_lifecycle_visibility = ContextVar("lifecycle_visibility", default=None)


class _LifecycleVisibility:
    """Batch Git reads within one checkpoint, bracketed by independent reads."""

    def __init__(self, target: Path, *, _detach_topology=None):
        from .workspace import _TopologyObservation
        self.target = target
        self._detach_topology = _detach_topology
        self.topology = _detach_topology if _detach_topology is not None else _TopologyObservation(target)
        self.before = self._snapshot()
        self.paths = {name for name, value in self.before.items() if value[-1] is not None}
        self.policy = self._policy()
        classify_target(target, _topology_observation=self.topology)
        self.ignored = self._ignored()

    @staticmethod
    def _signature(path: Path):
        try:
            value = path.lstat()
        except (FileNotFoundError, NotADirectoryError):
            return None
        return (value.st_dev, value.st_ino, value.st_mode, value.st_nlink,
                value.st_size, value.st_mtime_ns, value.st_ctime_ns)

    def _snapshot(self):
        from .jsonio import _windows_detach_read_observation
        scope = _windows_detach_read_observation.get() if sys.platform == "win32" and self._detach_topology is not None else None
        reads = []
        def observe_file(item):
            path, signature = item
            digest = _stable_file(path)[0]
            _require(signature == self._signature(path), "unstable lifecycle observation member")
            return path.relative_to(self.target).as_posix(), (*signature, digest)
        root = self.target / ".hrn"
        root_signature = self._signature(root)
        _require(root_signature is not None and stat.S_ISDIR(root_signature[2]),
                 "unsupported lifecycle observation root")
        result = {".hrn": (*root_signature, None)}
        pending = [self.target / name for name in (
            "colvia", ".hrn/format.json", ".hrn/.gitignore", ".hrn/product",
            ".hrn/work", ".hrn/intents", ".hrn/planning", ".hrn/executions")]
        if self._detach_topology is not None:
            pending.append(root / "detached.json")
        while pending:
            path = pending.pop()
            signature = self._signature(path)
            if signature is None:
                continue
            mode = signature[2]
            _require(stat.S_ISDIR(mode) or stat.S_ISREG(mode),
                     "unsupported lifecycle observation member")
            digest = None
            if stat.S_ISDIR(mode):
                pending.extend(path.iterdir())
            elif scope is not None:
                reads.append((path, signature))
                continue
            else:
                digest = _stable_file(path)[0]
            _require(signature == self._signature(path), "unstable lifecycle observation member")
            result[path.relative_to(self.target).as_posix()] = (*signature, digest)
        if scope is not None:
            result.update(scope.read_batch(observe_file, reads))
        _require(root_signature == self._signature(root), "lifecycle root changed during observation")
        return result

    def _policy(self):
        # Values such as credentials are not requested. Track config origins and
        # effective exclude paths, including their identities and change times.
        config = _git(self.target, "config", "--null", "--show-origin", "--name-only", "--list").stdout
        exclude_query = _git(self.target, "config", "--null", "--path", "--get-all",
                             "core.excludesfile", allowed=(0, 1))
        excludes = exclude_query.stdout
        watched = {self.target / ".git/info/exclude"}
        if exclude_query.returncode == 1:
            # Unset uses Git's default; an explicitly empty value does not.
            default_ignore = _default_git_ignore_path(self.target)
            watched.add(default_ignore if default_ignore.is_absolute() else self.target / default_ignore)
        for item in config.split(b"\0"):
            if item.startswith(b"file:"):
                path = Path(os.fsdecode(item[5:]))
                watched.add(path if path.is_absolute() else self.target / path)
        for item in excludes.split(b"\0"):
            if item:
                path = Path(os.fsdecode(item)).expanduser()
                watched.add(path if path.is_absolute() else self.target / path)
        # Build the same watch set without revisiting shared lexical ancestors.
        # Every policy invocation still observes each watched path afresh below.
        parents = set()
        stop = self.target.parent
        for name in self.paths:
            parent = (self.target / name).parent
            while parent != stop and parent not in parents:
                parents.add(parent)
                watched.add(parent / ".gitignore")
                parent = parent.parent
        # Follow a config symlink only for metadata; its target identity must
        # remain stable too. Git itself remains the ignore-policy interpreter.
        signatures = {}
        for path in watched:
            signatures[str(path)] = self._signature(path)
            if path.is_symlink():
                signatures[str(path) + ":target"] = self._signature(path.resolve())
        # Index locks and fetch metadata change the directory's times, not its
        # policy. Keep replacement/type/mode detection independently of those.
        git_directory = self._signature(self.target / ".git")
        git_identity = git_directory[:3] if git_directory is not None else None
        return config, excludes, signatures, git_environment(), git_identity

    def _ignored(self):
        raw = b"\0".join(os.fsencode(name) for name in sorted(self.paths)) + b"\0"
        result = _git(self.target, "check-ignore", "--no-index", "-z", "--stdin",
                      input_data=raw, allowed=(0, 1))
        return {os.fsdecode(name) for name in result.stdout.split(b"\0") if name}

    def visible(self, target: Path, paths: list[str]):
        _require(target == self.target, "lifecycle observation target changed")
        classify_target(target, _topology_observation=self.topology)
        _require(set(paths) <= self.paths, "lifecycle truth membership changed")
        _require(not self.ignored.intersection(paths), "truth hidden by effective Git ignore policy")

    def finish(self):
        _require(self.before == self._snapshot(), "lifecycle inputs changed during checkpoint")
        _require(self.policy == self._policy(), "Git policy changed during checkpoint")
        if self._detach_topology is None:
            self.topology.finish()
        _require(self.ignored == self._ignored(), "Git visibility changed during checkpoint")


@contextmanager
def _lifecycle_git_observation(target: Path):
    """Never share observations across checkpoint calls, threads or writers."""
    target = safe_target(target)
    if classify_target(target)["kind"] != "primary":
        yield
        return
    _require(_lifecycle_visibility.get() is None, "nested lifecycle observation")
    observed = None
    token = None
    try:
        observed = _LifecycleVisibility(target)
        token = _lifecycle_visibility.set(observed)
        yield
        observed.finish()
    except (OSError, ValueError, RecursionError) as exc:
        raise _fail("lifecycle observation unavailable or unstable") from exc
    finally:
        if token is not None:
            _lifecycle_visibility.reset(token)
        if observed is not None:
            observed.topology.close()


@contextmanager
def _detach_git_observation(target: Path, topology):
    """Batch visibility only inside one independently rechecked detach sweep.

    The caller owns and finishes the exact topology observation. Other readable
    topologies keep their existing checks; this context never spans a removal.
    """
    if classify_target(target, _topology_observation=topology)["kind"] != "primary":
        yield
        return
    _require(_lifecycle_visibility.get() is None, "nested lifecycle observation")
    token = None
    try:
        observed = _LifecycleVisibility(target, _detach_topology=topology)
        token = _lifecycle_visibility.set(observed)
        yield
        observed.finish()
    except (OSError, ValueError, RecursionError) as exc:
        raise _fail("lifecycle observation unavailable or unstable") from exc
    finally:
        if token is not None:
            _lifecycle_visibility.reset(token)


def _visible_truth(target: Path, paths: list[str], *, _topology_observation=None) -> None:
    observed = _lifecycle_visibility.get()
    if observed is not None and (_topology_observation is None or _topology_observation is observed.topology):
        observed.visible(target, paths)
        return
    topology = (classify_target(target) if _topology_observation is None else
                classify_target(target, _topology_observation=_topology_observation))
    if topology["kind"] != "non-git" and paths:
        result = _git(target, "check-ignore", "--no-index", "-z", "--stdin", input_data=b"\0".join(p.encode() for p in paths) + b"\0", allowed=(0, 1))
        _require(result.returncode == 1 and not result.stdout, "truth hidden by effective Git ignore policy")


def _preflight_publication(target: Path, paths: list[str]) -> None:
    """Check the operation's replace/reflush union without changing read paths."""
    from .jsonio import windows_preflight_files
    _visible_truth(target, paths)
    windows_preflight_files(target / path for path in paths)


def read_work(target: Path, work_id: str, *, _intent_graph_reader=None, _topology_observation=None,
              _with_continuation: bool = True, _continuation_errors=None) -> dict[str, Any]:
    """Double-read Work records; status may supply observation-local intent graphs."""
    try:
        home, authority = _authority_directory(target, "work", work_id)
        folders = {"revisions", "decisions", "selections", "results"}
        data = _record_tree(home, folders, allow_continuation=True)
        _require(data == _record_tree(home, folders, allow_continuation=True), "unstable Work observation")
        truth_paths = [(home.relative_to(safe_target(target)) / key).as_posix() for key in data]
        if _topology_observation is None:
            _visible_truth(target, truth_paths)
        else:
            _visible_truth(target, truth_paths, _topology_observation=_topology_observation)
        _require("identity.json" in data, "partial Work identity")
        identity = validate_work_record(data["identity.json"])
        _require(identity.get("authority_home_id") == authority and identity.get("work_id") == work_id, "directory identity mismatch")
        maps = [{key.split("/")[1][:-5]: value for key, value in data.items() if key.startswith(folder + "/")} for folder in ("revisions", "decisions", "selections", "results")]
        from .intent import read_workspace_intent_graph
        intents = {}
        for value in maps[0].values():
            validate_work_record(value)
            iid = value["intent_ref"]["id"]
            if iid not in intents:
                intents[iid] = (read_workspace_intent_graph(target, iid) if _intent_graph_reader is None
                                else _intent_graph_reader(iid))
        graph = work_graph(identity, *maps, data.get("current.json"), intent_graphs=intents)
        from .intent import read_workspace_intent, _resolve_workspace_intent
        for revision in graph["revisions"].values():
            ref = revision["intent_ref"]
            bound, _ = _resolve_workspace_intent(intents[ref["id"]], ref["id"], ref)
            _require(bound["acceptance_authority"] == identity["acceptance_authority"], "Work and intent authorities differ")
            _require((revision["schema_version"] == 2) == (bound["composition"] is not None), "Work schema and bound intent composition differ")
            if bound["composition"] is not None:
                _require(bound["composition"]["parent"]["id"] == identity["work_id"], "composition names another parent Work")
        if _with_continuation:
            from .continuation import graph as continuation_graph, read_continuation
            continuation_home = home / "continuation"
            try:
                graph["continuation"] = (read_continuation(target, work_id, _source_graph=graph,
                                          _topology_observation=_topology_observation,
                                          _intent_graph_reader=_intent_graph_reader)
                                         if continuation_home.exists() or continuation_home.is_symlink()
                                         else continuation_graph(identity, {}))
            except ContractError as exc:
                if _continuation_errors is None:
                    raise
                # Status-only projection. Recheck the base independently before
                # localizing the failure; a changed base Work is not CONT damage.
                after = read_work(target, work_id, _with_continuation=False,
                                  _intent_graph_reader=_intent_graph_reader,
                                  _topology_observation=_topology_observation)
                _require(graph == after, "base Work changed while reading unavailable continuation")
                _continuation_errors[work_id] = {"error_code": exc.code, "message": exc.message}
                graph["continuation"] = None
        return graph
    except PermissionError as exc:
        raise ContractError("HV2-WORK-UNAVAILABLE", "Work read permission denied: " + str(target / ".hrn/work" / work_id)) from exc
    except (OSError, ValueError, RecursionError) as exc:
        raise _record_error("Work unavailable, malformed or unstable: " + str(target / ".hrn/work" / work_id)) from exc


def _canonical_record_bytes(value: dict[str, Any]) -> bytes:
    from .jsonio import decode_json_bytes
    data = canonical_json_bytes(value)
    decode_json_bytes(data, require_canonical=True)  # Enforce limits before any write.
    return data


def _publish_immutable(path: Path, value: dict[str, Any]) -> None:
    from .workspace import _write_exact
    _write_exact(path, _canonical_record_bytes(value))


def _live_external_refs(target: Path, revision: dict[str, Any], launcher_sha: str | None, *, verified_inventory_id: str | None = None) -> None:
    launcher_name = _verified_launcher_path(launcher_sha, verified_inventory_id)
    for category in ("document_refs", "evidence_refs"):
        for ref in revision[category]:
            if not ref["required"]:
                continue
            path = project_path(ref["path"])
            _require(not (path == launcher_name and launcher_name is not None), "managed release cannot be required evidence")
            current = safe_target(target)
            for component in path.split("/"):
                _require(current.is_dir() and not current.is_symlink(), "required reference parent is not a directory")
                names = [p.name for p in current.iterdir()]
                _require(component in names and not any(n.casefold() == component.casefold() and n != component for n in names), "required reference missing or aliased")
                current = current / component
                _require(not current.is_symlink(), "required reference symlink")
            _require(_stable_file(current)[0] == ref["sha256"], "required reference is stale")



def _worker_required_refs(target, revision, manifest, launcher_sha, sources, *, verified_inventory_id=None):
    from .intent import read_workspace_intent_graph
    intent_refs = [revision["intent_ref"]]
    if revision["schema_version"] == 2:
        intent_refs.extend(child["intent_ref"] for child in revision["umbrella_evidence"]["children"])
    changed = [unicodedata.normalize("NFC", c["path"].casefold()) for c in manifest["changes"]]
    checked = set()
    for intent_ref in intent_refs:
        key = (intent_ref["id"], intent_ref["acceptance_ref"]["sha256"])
        if key in checked:
            continue
        checked.add(key)
        graph = read_workspace_intent_graph(target, intent_ref["id"])
        acceptance = _resolve(graph["acceptances"], intent_ref["acceptance_ref"])["confirmation"]
        for category in ("document_refs", "evidence_refs"):
            for ref in acceptance[category]:
                path = unicodedata.normalize("NFC", ref["path"].casefold())
                _require(not ref["required"] or not any(path == c or path.startswith(c + "/") or c.startswith(path + "/") for c in changed), "worker result overlaps required intent input; use separate output or obtain human intent revision first")
    remaining = {"document_refs": [], "evidence_refs": []}
    for category in remaining:
        for ref in revision[category]:
            if ref["required"] and ref["path"] in sources:
                post = sources[ref["path"]]["post"]
                _require(post is not None and hashlib.sha256(post).hexdigest() == ref["sha256"], "required Work reference differs from retained post blob")
            else:
                remaining[category].append(ref)
    _live_external_refs(target, remaining, launcher_sha, verified_inventory_id=verified_inventory_id)


def _worker_record_preflight(target: Path, revision: dict[str, Any], manifest: dict[str, Any], launcher_sha: str | None, *, verified_inventory_id: str | None = None, worker: Path | None = None, initial_baseline: bool = False) -> None:
    """Control-side observation only; it neither accepts nor applies worker bytes."""
    _require(classify_target(target, mutation=True)["kind"] == "primary", "worker publication requires primary control")
    _require(snapshot(target, verified_launcher_sha256=launcher_sha, verified_inventory_id=verified_inventory_id) == manifest["base"], "control differs from worker baseline; human baseline refresh required")
    sources = verify_worker_sources(target, manifest, verified_launcher_sha256=launcher_sha, verified_inventory_id=verified_inventory_id)
    if revision["operation"] == "submit-result":
        _require(worker is not None, "worker result requires explicit linked worktree")
        worker = safe_target(worker)
        _require(classify_target(worker)["kind"] == "linked-worktree", "worker must be a registered linked worktree")
        common = _git(target, "rev-parse", "--path-format=absolute", "--git-common-dir").stdout.rstrip(b"\n")
        _require(_git(worker, "rev-parse", "--path-format=absolute", "--git-common-dir").stdout.rstrip(b"\n") == common, "worker belongs to another repository")
        registered = [row[len(b"worktree "):] for row in _git(target, "worktree", "list", "--porcelain", "-z").stdout.split(b"\0") if row.startswith(b"worktree ")]
        registered_path = worker.as_posix() if sys.platform == "win32" else worker
        _require(os.fsencode(registered_path) in registered, "worker registration is missing")
        _require(_decode(_git(worker, "rev-parse", "--verify", "HEAD").stdout).strip() == manifest["candidate_commit"], "worker HEAD differs from candidate")
        _require(snapshot(worker, verified_launcher_sha256=launcher_sha, verified_inventory_id=verified_inventory_id) == manifest["result"], "worker bytes differ from committed result")
        _require(all(v == "pre" for v in preflight_changed_paths(target, manifest, verified_launcher_sha256=launcher_sha, verified_inventory_id=verified_inventory_id).values()), "control changed-path occupant is not pre")
        _worker_required_refs(target, revision, manifest, launcher_sha, sources, verified_inventory_id=verified_inventory_id)
    else:
        _require(worker is None, "baseline publication does not consume a worker locator")
        if initial_baseline:
            _require(_decode(_git(target, "rev-parse", "--verify", "HEAD").stdout).strip() == manifest["base_commit"], "new worker baseline must use current control commit")
        _live_external_refs(target, revision, launcher_sha, verified_inventory_id=verified_inventory_id)


def _worker_content_state(target, manifest, launcher_sha, *, verified_inventory_id=None, cancellation=False, initial=False, final=False):
    observed = observe_recovery(manifest, snapshot(target, verified_launcher_sha256=launcher_sha, verified_inventory_id=verified_inventory_id))
    physical = preflight_changed_paths(target, manifest, verified_launcher_sha256=launcher_sha, verified_inventory_id=verified_inventory_id)
    _require(physical == observed["changed_paths"], "physical occupants differ from visible worker snapshot")
    if cancellation:
        _require(observed["all_changed_paths_pre"], "worker cancellation requires every changed path still pre")
    else:
        _require(observed["content_resume_possible"], "worker recovery blocked by outside drift, policy or changed-path bytes")
        if initial:
            _require(snapshot(target, verified_launcher_sha256=launcher_sha, verified_inventory_id=verified_inventory_id) == manifest["base"], "new worker acceptance requires exact baseline")
        if final:
            _require(observed["whole_result_matches"], "worker result is not fully applied")
    return physical


def _apply_worker_path(target, change, post, launcher_sha, manifest, inject_at, *, verified_inventory_id=None):
    """Replace one verified pre image; never touch Git or restore other bytes."""
    from .workspace import _durable_directory, _require_kind
    from .jsonio import _sync_fd, sync_directory, replace_file, windows_preflight_files, remove_path
    from .errors import InjectedCrash
    import tempfile
    path = target / change["path"]
    if post is None:
        _require(preflight_changed_paths(target, manifest, verified_launcher_sha256=launcher_sha, verified_inventory_id=verified_inventory_id)[change["path"]] == "pre", "worker path changed before deletion")
        windows_preflight_files([path])
        remove_path(path); sync_directory(path.parent)
        return
    staging = target / ".hrn/staging"
    _durable_directory(staging); _require_kind(staging, True)
    fd, name = tempfile.mkstemp(prefix="worker-content-", dir=staging)
    staged = Path(name)
    with os.fdopen(fd, "wb") as handle:
        handle.write(post); handle.flush()
        if sys.platform != "win32":
            os.fchmod(handle.fileno(), 0o755 if change["post"]["mode"] == "100755" else 0o644)
        _sync_fd(handle.fileno())
    sync_directory(staging)
    if inject_at == "after-staged-file": raise InjectedCrash(inject_at)
    _require(preflight_changed_paths(target, manifest, verified_launcher_sha256=launcher_sha, verified_inventory_id=verified_inventory_id)[change["path"]] == "pre", "worker path changed before replacement")
    parent = target
    for component in change["path"].split("/")[:-1]:
        parent = parent / component
        if not parent.exists(): _durable_directory(parent)
        _require_kind(parent, True)
    replace_file(staged, path)
    sync_directory(path.parent); sync_directory(staging)


def _publish_object_home(target: Path, category: str, object_id: str, identity: dict[str, Any], inject_at: str | None) -> Path:
    from .workspace import _durable_directory, _require_kind
    from .jsonio import sync_directory, rename_directory
    from .errors import InjectedCrash
    import tempfile
    _require(category in ("work", "intents"), "unknown object category")
    home = target / ".hrn" / category / object_id
    if home.exists() or home.is_symlink():
        _require_kind(home, True)
        _publish_immutable(home / "identity.json", identity)
        if sys.platform == "win32":
            # A previous rename may have published before its parent sync.
            # Completed Work/intent replay returns before this writer helper.
            sync_directory(home.parent)
            staging = target / ".hrn/staging"
            if staging.exists(): sync_directory(staging)
        return home
    staging = target / ".hrn/staging"
    _durable_directory(staging)
    _require_kind(staging, True)
    staged = Path(tempfile.mkdtemp(prefix=category + "-home-", dir=staging))
    _publish_immutable(staged / "identity.json", identity)
    sync_directory(staged)
    if inject_at == "after-staged-identity": raise InjectedCrash(inject_at)
    rename_directory(staged, home)  # Shared writer guard serializes cooperative writers.
    sync_directory(home.parent); sync_directory(staging)
    if inject_at == "after-home": raise InjectedCrash(inject_at)
    return home


def _publish_current(target: Path, path: Path, value: dict[str, Any], inject_at: str | None) -> None:
    from .workspace import _durable_directory, _require_kind
    from .jsonio import _sync_fd, sync_directory, replace_file
    from .errors import InjectedCrash
    import tempfile
    staging = target / ".hrn/staging"
    _durable_directory(staging)
    _require_kind(staging, True)
    data = _canonical_record_bytes(value)
    fd, name = tempfile.mkstemp(prefix="work-current-", dir=staging)
    staged = Path(name)
    with os.fdopen(fd, "wb") as handle:
        handle.write(data); handle.flush(); _sync_fd(handle.fileno())
    sync_directory(staging)
    if inject_at == "after-staged-current": raise InjectedCrash(inject_at)
    replace_file(staged, path)
    sync_directory(path.parent); sync_directory(staging)


class WorkStore:
    """Control writer for local and worker results, with a bound-runtime verifier.

runtime_check(target) MUST verify the executing bound release under this module's
shared guard and return {binding_ref, launcher_sha256, inventory_id}. The default
verifies the isolated installed applied binding. Older ordinary-Work fixture
doubles with launcher_sha256=None may omit inventory_id; non-null proof requires a
verified supported window. Schema2 includes entry-1 capability. Lifecycle publication
remains separate.
Human confirmation is a trusted-local declaration, not OS authentication.
"""
    def __init__(self, target: Path, runtime_check=None):
        if runtime_check is None:
            from .product import require_workspace_runtime
            runtime_check = require_workspace_runtime
        _require(callable(runtime_check), "bound runtime verifier required")
        self.target = safe_target(target)
        self.runtime_check = runtime_check

    def _runtime(self) -> dict[str, Any]:
        result = self.runtime_check(self.target)
        _keys(result, {"binding_ref", "launcher_sha256"} | ({"inventory_id"} if "inventory_id" in result else set()))
        if "inventory_id" in result:
            _require(isinstance(result["inventory_id"], str) and result["inventory_id"] in ("worker-1", "umbrella-1", "planning-1", "checkout-1", "entry-1", "delegation-1", "continuation-1", "windows-2", "official-execution-1", "official-execution-2"), "unsupported writer inventory window")
        validate_ref(result["binding_ref"])
        _require(result["launcher_sha256"] is None or _sha(result["launcher_sha256"]), "invalid verified launcher digest")
        _verified_launcher_path(result["launcher_sha256"], result.get("inventory_id"))
        from .intent import workspace_intents
        if any(d["schema_version"] == 3 for g in workspace_intents(self.target).values() for d in g["drafts"].values()):
            self._delegation_runtime(result)
        return result

    @staticmethod
    def _delegation_runtime(runtime: dict[str, Any]) -> None:
        _require(runtime.get("inventory_id") in ("delegation-1", "continuation-1", "windows-2", "official-execution-1", "official-execution-2"), "delegation history requires a delegation-capable writer")

    def _graph(self, identity, revisions, decisions, selections, manifests, current):
        from .intent import workspace_intents
        return work_graph(identity, revisions, decisions, selections, manifests, current,
                          intent_graphs=workspace_intents(self.target))

    @staticmethod
    def _umbrella_runtime(runtime: dict[str, Any]) -> None:
        _require(runtime.get("inventory_id") in ("umbrella-1", "planning-1", "checkout-1", "entry-1", "delegation-1", "continuation-1", "windows-2", "official-execution-1", "official-execution-2"), "umbrella writer requires an installed umbrella-capable runtime")

    def _all(self, *, _intent_graph_reader=None, _topology_observation=None,
             _continuation_errors=None) -> dict[str, Any]:
        root = self.target / ".hrn/work"
        if not root.exists(): return {}
        _require(root.is_dir() and not root.is_symlink(), "invalid Work collection")
        readers = {}
        if _continuation_errors is not None:
            readers["_continuation_errors"] = _continuation_errors
        if _intent_graph_reader is not None:
            readers["_intent_graph_reader"] = _intent_graph_reader
        if _topology_observation is not None:
            readers["_topology_observation"] = _topology_observation
        result = {p.name: read_work(self.target, p.name, **readers) for p in root.iterdir()}
        _require(len({k.casefold() for k in result}) == len(result), "Work case alias")
        # Relations on every proposal must resolve. Detect cycles without recursion.
        edges = {key: set() for key in result}
        for key, graph in result.items():
            for r in graph["revisions"].values():
                for relation in r["relations"]:
                    other = relation["target"]["id"]
                    _require(other in result, "relation target does not exist")
                    edges[key].add(other)
        todo = {key: set(value) for key, value in edges.items()}
        while todo:
            leaves = {k for k, v in todo.items() if not v}
            _require(bool(leaves), "Work relation cycle")
            todo = {k: v - leaves for k, v in todo.items() if k not in leaves}
        if any(r["schema_version"] == 2 for g in result.values() for r in g["revisions"].values()):
            from .intent import workspace_intents
            from .umbrella import check_work_histories
            intents = (workspace_intents(self.target) if _intent_graph_reader is None else
                       workspace_intents(self.target, _graph_reader=_intent_graph_reader))
            check_work_histories(result, intents)
        return result

    def _pending_guard(self, graphs: dict[str, Any], work_id: str, *, content_write: bool = False) -> None:
        from .intent import require_no_pending_intents
        from .continuation import require_no_pending
        require_no_pending(self.target, works=graphs)
        require_no_pending_intents(self.target)
        for key, graph in graphs.items():
            if key == work_id: continue
            for d in graph["pending_decisions"]:
                ticket = graph["decisions"][d]["confirmation"]
                _require(graph["revisions"][ticket["target_revision_ref"]["id"]]["schema_version"] == 1, "umbrella decision pending blocks mutation")
                _require(ticket["execution_mode"] == "local", "worker pending blocks project mutation")
            for s in graph["pending_selections"]:
                revision = graph["revisions"][graph["selections"][s]["revision_ref"]["id"]]
                _require(revision["schema_version"] == 1, "umbrella publication pending blocks mutation")
                _require(revision["execution_context"]["mode"] == "local", "worker publication pending")
            if content_write:
                _require(not graph["pending_decisions"] and not graph["pending_selections"], "pending Work blocks worker content application")

    def _intent(self, revision: dict[str, Any], identity: dict[str, Any], *, require_current: bool = True) -> None:
        from .intent import read_workspace_intent
        observed = read_workspace_intent(self.target, revision["intent_ref"]["id"], revision["intent_ref"], require_current=require_current)
        _require(observed["acceptance_authority"] == identity["acceptance_authority"], "Work and intent authorities differ")

    def _umbrella(self, revision: dict[str, Any], runtime: dict[str, Any], *, current: bool) -> None:
        from .intent import workspace_intents, read_workspace_intent, read_workspace_intent_graph
        from .umbrella import bound_composition, prior_revision, check_baseline_binding
        iid = revision["intent_ref"]["id"]
        intents = {iid: read_workspace_intent_graph(self.target, iid)}
        composition = bound_composition(revision, intents)
        if composition is None and revision["schema_version"] == 1:
            return  # Ordinary Work gets no new authority or required inputs.
        self._umbrella_runtime(runtime)
        intents = workspace_intents(self.target)
        graphs = self._all()
        prior = prior_revision(revision, graphs.get(revision["work_id"]))
        check_baseline_binding(composition, revision, prior, graphs, intents, current=current)
        if current and composition is not None and revision["operation"] in ("start", "rebind", "submit-result"):
            for child in revision["umbrella_evidence"]["children"]:
                ref = child["intent_ref"]
                read_workspace_intent(self.target, ref["id"], ref)

    def publish(self, identity: dict[str, Any], revision: dict[str, Any], manifest: dict[str, Any], *, selection_id: str | None = None, operation_id: str | None = None, inject_at: str | None = None, worker: Path | None = None) -> dict[str, Any]:
        """Publish an agent baseline/result. Rebind proposals wait for human apply."""
        from .workspace import writer_guard, _durable_directory
        from .errors import InjectedCrash
        _require(inject_at in (None, "after-staged-identity", "after-home", "after-manifest", "after-revision", "after-selection", "after-staged-current", "after-current"), "unknown crash point")
        validate_work_record(identity); validate_work_record(revision); validate_manifest(manifest, scope=revision["scope"])
        if revision["operation"] != "rebind":
            _identifier(selection_id); _identifier(operation_id)
        for value in (identity, revision, manifest): _canonical_record_bytes(value)
        _require(revision["execution_context"]["mode"] != "local" or worker is None, "local publication cannot consume a worker locator")
        _require(revision["result_refs"]["manifest"] == {"id": _digest(manifest), "sha256": _digest(manifest)}, "wrong manifest ref")
        with writer_guard(self.target):
            runtime = self._runtime(); graphs = self._all(); wid = identity["work_id"]
            graph = graphs.get(wid)
            if graph is None:
                _require(revision["operation"] == "start" and revision["expected_prior_selection"] is None, "new Work requires start")
                graph = {"identity": identity, "revisions": {}, "decisions": {}, "selections": {}, "manifests": {}, "current": None, "pending_decisions": [], "pending_selections": []}
            _require(graph["identity"] == identity, "immutable Work identity mismatch")
            _require(revision["record_id"] not in graph["revisions"] or graph["revisions"][revision["record_id"]] == revision, "revision ID collision")
            parent = graph["current"]["selection_ref"] if graph["current"] else None
            existing = next((s for s in graph["selections"].values() if s["operation_id"] == operation_id), None)
            if existing:
                _require(existing["record_id"] == selection_id and existing["revision_ref"] == record_ref(revision), "operation ID reused with changed request")
            # An exact historical retry returns its outcome without moving current.
            if existing and existing["revision_ref"] == record_ref(revision) and existing["operation_id"] == operation_id and selection_id not in graph["pending_selections"]:
                _require(graph["revisions"].get(revision["record_id"]) == revision, "changed retry revision")
                return graph
            self._pending_guard(graphs, wid)
            _require(not graph["pending_decisions"], "pending human decision must resolve first")
            _require(parent == revision["expected_prior_selection"], "stale expected selection")
            def check_publication():
                if revision["execution_context"]["mode"] == "isolated-worktree":
                    self._runtime_equal(runtime)
                self._intent(revision, identity)
                self._umbrella(revision, runtime, current=True)
                if revision["execution_context"]["mode"] == "isolated-worktree":
                    _worker_record_preflight(self.target, revision, manifest, runtime["launcher_sha256"], verified_inventory_id=runtime.get("inventory_id"), worker=worker, initial_baseline=revision["record_id"] not in graph["revisions"] and revision["operation"] in ("start", "rebind"))
                else:
                    _windows_non_git_manifest(self.target, manifest, runtime.get("inventory_id"))
                    _live_external_refs(self.target, revision, runtime["launcher_sha256"], verified_inventory_id=runtime.get("inventory_id"))
                    _require(snapshot(self.target, verified_launcher_sha256=runtime["launcher_sha256"], verified_inventory_id=runtime.get("inventory_id")) == manifest["result"], "live result differs from proposed manifest")
            check_publication()
            selection = {k: revision[k] for k in _RECORD_BASE | _PROVENANCE}
            selection.update(schema_version=1, record_type="work-selection", record_id=selection_id, parent_selection_ref=parent, revision_ref=record_ref(revision), decision_ref=None, operation_id=operation_id)
            if revision["operation"] != "rebind":
                _require(selection_id not in graph["selections"] or graph["selections"][selection_id] == selection, "selection ID collision")
            revisions = graph["revisions"] | {revision["record_id"]: revision}
            manifests = graph["manifests"] | {_digest(manifest): manifest}
            selections = graph["selections"] if revision["operation"] == "rebind" else graph["selections"] | {selection_id: selection}
            self._graph(identity, revisions, graph["decisions"], selections, manifests, graph["current"])
            # Cross-Work relations are checked before any truth writes.
            for relation in revision["relations"]:
                _require(relation["target"]["id"] in graphs, "relation target missing")
                frontier = [relation["target"]["id"]]; seen = set()
                while frontier:
                    node = frontier.pop()
                    _require(node != wid, "Work relation cycle")
                    if node in seen: continue
                    seen.add(node)
                    frontier.extend(x["target"]["id"] for r in graphs[node]["revisions"].values() for x in r["relations"])
            planned_home = ".hrn/work/" + wid + "/"
            planned = ["identity.json", "results/" + _digest(manifest) + ".json", "revisions/" + revision["record_id"] + ".json"]
            if revision["operation"] != "rebind": planned += ["selections/" + selection_id + ".json", "current.json"]
            _preflight_publication(self.target, [planned_home + name for name in planned])
            self._runtime_equal(runtime)
            if revision["execution_context"]["mode"] == "isolated-worktree" or revision["schema_version"] == 2: check_publication()
            root = self.target / ".hrn/work"; _durable_directory(root)
            _require(not any(p.name.casefold() == wid.casefold() and p.name != wid for p in root.iterdir()), "Work case alias")
            home = _publish_object_home(self.target, "work", wid, identity, inject_at)
            _publish_immutable(home / "results" / (_digest(manifest) + ".json"), manifest)
            if inject_at == "after-manifest": raise InjectedCrash(inject_at)
            _publish_immutable(home / "revisions" / (revision["record_id"] + ".json"), revision)
            if inject_at == "after-revision": raise InjectedCrash(inject_at)
            if revision["operation"] == "rebind": return read_work(self.target, wid)
            if revision["execution_context"]["mode"] == "isolated-worktree" or revision["schema_version"] == 2: check_publication()
            _publish_immutable(home / "selections" / (selection_id + ".json"), selection)
            if inject_at == "after-selection": raise InjectedCrash(inject_at)
            if revision["execution_context"]["mode"] == "isolated-worktree" or revision["schema_version"] == 2: check_publication()
            _publish_current(self.target, home / "current.json", {**{k: identity[k] for k in _RECORD_BASE}, "record_type": "work-current", "selection_ref": record_ref(selection)}, inject_at)
            if inject_at == "after-current": raise InjectedCrash(inject_at)
            return read_work(self.target, wid)

    def prepare(self, work_id: str, *, action: str, actor: str, reason: str, request_id: str, observed_at: str, revision_ref: dict[str, str] | None = None, supersedes: dict[str, str] | None = None) -> dict[str, Any]:
        """Read-only ticket generation. Every condition is repeated inside apply."""
        from .workspace import target_fingerprint
        runtime = self._runtime(); graph = read_work(self.target, work_id)
        _require(graph["current"] is not None, "no current Work selection")
        selected = graph["selections"][graph["current"]["selection_ref"]["id"]]
        rref = revision_ref or selected["revision_ref"]
        revision = _resolve(graph["revisions"], rref)
        ticket = {"record_type": "confirmation-ticket", "schema_version": 1, "authority_home_id": graph["identity"]["authority_home_id"], "object": {"authority_home_id": graph["identity"]["authority_home_id"], "kind": "work", "id": work_id}, "action": action, "actor": actor, "reason": reason, "request_id": request_id, "observed_at": observed_at, "target_fingerprint": target_fingerprint(self.target), "target_revision_ref": rref, "expected_selection_ref": graph["current"]["selection_ref"], "intent_ref": revision["intent_ref"], "product_binding_ref": runtime["binding_ref"], "document_refs": revision["document_refs"], "evidence_refs": revision["evidence_refs"], "execution_mode": revision["execution_context"]["mode"], "supersedes_decision_ref": supersedes}
        decision = self._decision(ticket)
        self._graph(graph["identity"], graph["revisions"], graph["decisions"] | {decision["record_id"]: decision}, graph["selections"], graph["manifests"], graph["current"])
        self._pending_guard(self._all(), work_id, content_write=ticket["execution_mode"] == "isolated-worktree" and action == "accept")
        grants_authority = action in ("accept", "rebind")
        self._intent(revision, graph["identity"], require_current=grants_authority)
        self._umbrella(revision, runtime, current=grants_authority)
        manifest = _resolve(graph["manifests"], revision["result_refs"]["manifest"])
        if ticket["execution_mode"] == "isolated-worktree":
            self._worker_confirmation(ticket, revision, manifest, runtime, initial=decision["record_id"] not in graph["decisions"])
        elif grants_authority:
            _windows_non_git_manifest(self.target, manifest, runtime.get("inventory_id"))
            _live_external_refs(self.target, revision, runtime["launcher_sha256"], verified_inventory_id=runtime.get("inventory_id"))
            _require(snapshot(self.target, verified_launcher_sha256=runtime["launcher_sha256"], verified_inventory_id=runtime.get("inventory_id")) == manifest["result"], "result changed before confirmation")
        return {"ticket": ticket, "confirm_token": _digest(ticket)[:16]}

    @staticmethod
    def _decision(ticket):
        validate_ticket(ticket)
        return {"record_type": "work-decision", "schema_version": 1, "authority_home_id": ticket["authority_home_id"], "work_id": ticket["object"]["id"], "record_id": "decision-" + _digest(ticket), "confirmation": ticket}

    def apply(self, ticket: dict[str, Any], *, confirm_token: str, inject_at: str | None = None, match_reviewed_files: bool = False) -> dict[str, Any]:
        """Human decision publication, exact worker application and prefix resume."""
        from .workspace import writer_guard, target_fingerprint
        from .errors import InjectedCrash
        _require(inject_at in (None, "after-decision", "after-selection", "after-staged-current", "after-current", "after-staged-file", "after-file"), "unknown crash point")
        decision = self._decision(ticket)
        _require(confirm_token == _digest(ticket)[:16], "confirmation token mismatch")
        _require(ticket["object"]["kind"] == "work", "Work ticket required")
        _require(inject_at not in ("after-staged-file", "after-file") or (ticket["execution_mode"] == "isolated-worktree" and ticket["action"] == "accept"), "file crash point requires worker acceptance")
        _require(ticket["target_fingerprint"] == target_fingerprint(self.target), "ticket target moved or differs")
        wid = ticket["object"]["id"]
        with writer_guard(self.target):
            runtime = self._runtime(); graphs = self._all()
            _require(wid in graphs, "Work does not exist")
            graph = graphs[wid]; did = decision["record_id"]
            existing = [s for s in graph["selections"].values() if s["decision_ref"] == record_ref(decision)]
            if existing and existing[0]["record_id"] not in graph["pending_selections"]:
                return graph  # Historical replay cannot promote an old decision.
            self._pending_guard(graphs, wid, content_write=ticket["execution_mode"] == "isolated-worktree" and ticket["action"] == "accept")
            _require(runtime["binding_ref"] == ticket["product_binding_ref"], "active binding changed")
            _require(graph["current"] is not None and graph["current"]["selection_ref"] == ticket["expected_selection_ref"], "stale confirmation selection")
            _require(not any(d["confirmation"]["supersedes_decision_ref"] == record_ref(decision) and d["confirmation"]["action"] == "reject" for d in graph["decisions"].values()), "cancelled decision cannot resume")
            decisions = graph["decisions"] | {did: decision}
            self._graph(graph["identity"], graph["revisions"], decisions, graph["selections"], graph["manifests"], graph["current"])
            revision = _resolve(graph["revisions"], ticket["target_revision_ref"])
            grants_authority = ticket["action"] in ("accept", "rebind")
            self._intent(revision, graph["identity"], require_current=grants_authority)
            manifest = _resolve(graph["manifests"], revision["result_refs"]["manifest"])
            worker_mode = ticket["execution_mode"] == "isolated-worktree"
            def check_confirmation(*, initial=False, final=False):
                self._runtime_equal(runtime)
                self._intent(revision, graph["identity"], require_current=grants_authority)
                self._umbrella(revision, runtime, current=grants_authority)
                if worker_mode:
                    return self._worker_confirmation(ticket, revision, manifest, runtime, initial=initial, final=final)
                if grants_authority or match_reviewed_files:
                    _windows_non_git_manifest(self.target, manifest, runtime.get("inventory_id"))
                    _live_external_refs(self.target, revision, runtime["launcher_sha256"], verified_inventory_id=runtime.get("inventory_id"))
                    _require(snapshot(self.target, verified_launcher_sha256=runtime["launcher_sha256"], verified_inventory_id=runtime.get("inventory_id")) == manifest["result"], "result changed since submission")
            check_confirmation(initial=did not in graph["decisions"], final=bool(existing))
            selection = existing[0] if existing else {**{k: revision[k] for k in _RECORD_BASE | _PROVENANCE}, "schema_version": 1, "record_type": "work-selection", "record_id": "selection-" + _digest(ticket), "observed_at": ticket["observed_at"], "parent_selection_ref": ticket["expected_selection_ref"], "revision_ref": ticket["target_revision_ref"], "decision_ref": record_ref(decision), "operation_id": ticket["request_id"]}
            selections = graph["selections"] | {selection["record_id"]: selection}
            self._graph(graph["identity"], graph["revisions"], decisions, selections, graph["manifests"], graph["current"])
            _canonical_record_bytes(decision); _canonical_record_bytes(selection)
            home = self.target / ".hrn/work" / wid
            _preflight_publication(self.target, [f".hrn/work/{wid}/decisions/{did}.json", f".hrn/work/{wid}/selections/selection-{_digest(ticket)}.json", f".hrn/work/{wid}/current.json"])
            if worker_mode and ticket["action"] == "accept" and not existing:
                from .jsonio import windows_preflight_files
                states = _worker_content_state(self.target, manifest, runtime["launcher_sha256"], verified_inventory_id=runtime.get("inventory_id"))
                windows_preflight_files(self.target / path for path, state in states.items() if state != "post")
            _publish_immutable(home / "decisions" / (did + ".json"), decision)
            if inject_at == "after-decision": raise InjectedCrash(inject_at)
            if worker_mode and ticket["action"] == "accept" and not existing:
                for change in manifest["changes"]:
                    sources = check_confirmation()
                    states = _worker_content_state(self.target, manifest, runtime["launcher_sha256"], verified_inventory_id=runtime.get("inventory_id"))
                    if states[change["path"]] == "post": continue
                    _apply_worker_path(self.target, change, sources[change["path"]]["post"], runtime["launcher_sha256"], manifest, inject_at, verified_inventory_id=runtime.get("inventory_id"))
                    if inject_at == "after-file": raise InjectedCrash(inject_at)
            check_confirmation(final=True)
            _publish_immutable(home / "selections" / (selection["record_id"] + ".json"), selection)
            if inject_at == "after-selection": raise InjectedCrash(inject_at)
            if worker_mode or revision["schema_version"] == 2: check_confirmation(final=True)
            _publish_current(self.target, home / "current.json", {**{k: graph["identity"][k] for k in _RECORD_BASE}, "record_type": "work-current", "selection_ref": record_ref(selection)}, inject_at)
            if inject_at == "after-current": raise InjectedCrash(inject_at)
            return read_work(self.target, wid)

    def _worker_confirmation(self, ticket, revision, manifest, runtime, *, initial=False, final=False):
        sha = runtime["launcher_sha256"]
        if ticket["action"] == "rebind":
            _worker_record_preflight(self.target, revision, manifest, sha, verified_inventory_id=runtime.get("inventory_id"))
        elif ticket["action"] == "accept":
            sources = verify_worker_sources(self.target, manifest, verified_launcher_sha256=sha, verified_inventory_id=runtime.get("inventory_id"))
            _worker_required_refs(self.target, revision, manifest, sha, sources, verified_inventory_id=runtime.get("inventory_id"))
            _worker_content_state(self.target, manifest, sha, initial=initial, final=final, verified_inventory_id=runtime.get("inventory_id"))
            _windows_worker_modes(self.target, manifest, runtime.get("inventory_id"))
            if final: _live_external_refs(self.target, revision, sha, verified_inventory_id=runtime.get("inventory_id"))
            return sources
        elif ticket["action"] == "reject" and ticket["supersedes_decision_ref"] is not None:
            _worker_content_state(self.target, manifest, sha, cancellation=True, verified_inventory_id=runtime.get("inventory_id"))

    def _runtime_equal(self, expected):
        _require(self._runtime() == expected, "bound runtime changed during publication")


def _ordinary_paths(target, paths):
    _path_set(paths)
    for path in paths:
        parts = path.split("/")
        _require(parts[0].casefold() != "colvia" and not any(c in path for c in "*?[]"),
                 "name each editable file explicitly")
        directory = target
        for i, part in enumerate(parts):
            matches = [p for p in directory.iterdir()
                       if unicodedata.normalize("NFC", p.name).casefold() == part.casefold()]
            if not matches:
                break  # New files (and missing parent directories) are allowed.
            _require(len(matches) == 1 and unicodedata.normalize("NFC", matches[0].name) == part,
                     "scope path spelling differs from the project")
            directory = matches[0]
            info = directory.lstat()
            _require(not stat.S_ISLNK(info.st_mode) and not getattr(info, "st_file_attributes", 0) & 0x400 and
                     (stat.S_ISREG(info.st_mode) and info.st_nlink == 1
                      if i == len(parts) - 1 else stat.S_ISDIR(info.st_mode)),
                     "scope must name an ordinary file through real directories")


def ordinary_command(target, args):
    """Convenience entry for a serial local edit. All writes go through the original stores."""
    from datetime import datetime, timezone
    from .intent import WorkspaceIntentStore, read_workspace_intent_graph
    from .workspace import _file_json, validate_format

    wid, action = args.id, args.action
    _identifier(wid)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    works = WorkStore(target)
    intents = WorkspaceIntentStore(target)
    if action == "plan":
        _text(args.goal)
        for item in args.check + args.exclude:
            _text(item)
        _text(args.owner)
        _ordinary_paths(target, args.file)
        home = validate_format(_file_json(target / ".hrn/format.json"))["authority_home_id"]
        facets = dict(goal=args.goal, scope=args.file, expected_outcome=args.goal,
                      acceptance_oracle="\n".join(args.check), destination=args.file, forbidden_scope="\n".join(args.exclude))
        intents.publish_draft(dict(record_type="intent-draft", schema_version=1, authority_home_id=home,
                                   intent_id=wid, revision_id="ordinary-plan", sequence=1, prior_revision_ref=None,
                                   actor="agent", acceptance_authority=args.owner, observed_at=now,
                                   facets={k: {"status": "known", "value": v} for k, v in facets.items()},
                                   gaps=[], statements=[], route="direct-entry"))
        action = "plan-review"

    if action == "status" and wid not in works._all():
        plan = read_workspace_intent_graph(target, wid)
        if plan["pending_acceptances"] or plan["pending_selections"]:
            return {"work": wid, "state": "plan-approval-pending"}
        if plan["current"] is None:
            return {"work": wid, "state": "plan-awaiting-approval"}
        return {"work": wid, "state": "plan-approved", "selection": plan["current"]["selection_ref"]["sha256"]}
    if action in ("plan-review", "approve", "start"):
        graph = read_workspace_intent_graph(target, wid)
        _require(set(graph["drafts"]) == {"ordinary-plan"}, "select the exact intent revision through intent review")
        draft = graph["drafts"]["ordinary-plan"]
        _require(draft["schema_version"] == 1, "ordinary work requires a local, nondelegated intent")
        draft_ref = record_ref(draft, "revision_id")
        facets = {key: value["value"] for key, value in draft["facets"].items() if value["status"] == "known"}
        if action != "start":
            return _ordinary_confirmation(intents, graph, wid, draft_ref, draft["acceptance_authority"],
                                          facets, now, getattr(args, "receipt", None), intent=True)
        _require(graph["current"] is not None, "approve the exact plan before starting")
        approved = graph["current"]["selection_ref"]
        selected = _resolve(graph["selections"], approved)
        _require(approved["sha256"] == args.approval and selected["revision_ref"] == draft_ref,
                 "the approved plan has changed")
        scope = facets.get("scope")
        _require(isinstance(scope, list) and scope and all(isinstance(f, str) for f in scope),
                 "ordinary work requires explicit file paths")
        _ordinary_paths(target, scope)
        home = graph["identity"]["authority_home_id"]
        common = dict(schema_version=1, authority_home_id=home, work_id=wid)
        identity = dict(common, record_type="work-identity", work_type="local-edit", created_at=now,
                        acceptance_authority=draft["acceptance_authority"], lineage=None)
        revision = dict(common, record_type="work-revision", record_id="ordinary-start", observed_at=now,
                        observed_scope=[facets["goal"]], unavailable_scope=[], author="agent", operation="start",
                        expected_prior_selection=None, intent_ref=dict(authority_home_id=home, kind="intent", id=wid,
                            revision_ref=draft_ref, acceptance_ref=selected["acceptance_ref"], selection_ref=approved),
                        scope=scope, document_refs=[], evidence_refs=[], progress="active", next_action=facets["goal"],
                        relations=[], rebind_from=None, execution_context={"mode": "local", "attempt_id": "ordinary"})
    else:
        graph = read_work(target, wid)
        identity = graph["identity"]
        _require(graph["current"] is not None, "no current Work")
        current = graph["current"]["selection_ref"]
        selected = _resolve(graph["selections"], current)
        revision = _resolve(graph["revisions"], selected["revision_ref"])
        if action == "status":
            next_action = revision["next_action"]
            if _interrupted_correction(graph, selected):
                next_action = "이전에 요청한 보완 이어가기 (ordinary resume-revision)"
            return {"work": wid, "state": graph["state"], "selection": current["sha256"],
                    "files": revision["scope"], "next": next_action}
        _require(revision["execution_context"]["mode"] == "local" and revision["schema_version"] == 1,
                 "use the full review for a parent or worker result")
        if action in ("revise", "resume-revision", "prepare-delivery"):
            _require(identity["work_type"] == "local-edit" and revision["intent_ref"]["id"] == wid
                     and revision["execution_context"].get("attempt_id") == "ordinary",
                     "use the detailed procedure for this Work")
        if action == "resume-revision":
            recorded = _interrupted_correction(graph, selected)
            _require(recorded is not None, "no matching recorded correction to resume")
            ticket, reviewed = recorded
            return _ordinary_revise(works, graph, selected, revision, wid,
                                    ticket["observed_at"] + "@" + reviewed, ticket["reason"])
        if action == "revise":
            return _ordinary_revise(works, graph, selected, revision, wid, args.receipt, args.reason)
        if action in ("review", "accept"):
            prior = _resolve(graph["manifests"], revision["result_refs"]["manifest"])
            summary = dict(files=[item["path"] for item in prior["changes"]], summary=revision["next_action"],
                           checked=revision["observed_scope"], unchecked=revision["unavailable_scope"])
            return _ordinary_confirmation(works, graph, wid, selected["revision_ref"], identity["acceptance_authority"],
                                          summary, now, getattr(args, "receipt", None), intent=False)
        _require(action in ("submit", "prepare-delivery") and current["sha256"] == args.baseline and
                 graph["state"] == "active" and revision["operation"] in ("start", "rework"), "review the current baseline before submission")
        prior = _resolve(graph["manifests"], revision["result_refs"]["manifest"])
        submission_id = "ordinary-submit" if revision["operation"] == "start" else "submit-" + current["sha256"]
        revision = dict(revision, record_id=submission_id, operation="submit-result", progress="review",
                        observed_at=now, expected_prior_selection=current, next_action=args.summary,
                        observed_scope=args.checked, unavailable_scope=args.unchecked)

    runtime = works._runtime()
    actual = snapshot(target, verified_launcher_sha256=runtime["launcher_sha256"],
                      verified_inventory_id=runtime.get("inventory_id"))
    manifest = make_manifest(actual if action == "start" else prior["result"], actual, scope=revision["scope"])
    if action in ("submit", "prepare-delivery"):
        _require(bool(manifest["changes"]), "no edited file to submit; describe the unchanged result")
    digest = _digest(manifest)
    revision["result_refs"] = {"manifest": {"id": digest, "sha256": digest}}
    payload = dict(identity=identity, revision=revision, manifest=manifest,
                   selection_id=revision["record_id"], operation_id=revision["record_id"])
    if action == "prepare-delivery":
        from .continuation import prepare_delivery
        request = dict(work_id=wid, action="submit", payload=payload, expires=args.expires,
                       ask=False, notify=True, detail_required=True)
        return prepare_delivery(target, request)
    saved = works.publish(**payload)
    return {"work": wid, "state": saved["state"], "selection": saved["current"]["selection_ref"]["sha256"]}


def _original_review_digest(ticket):
    at = ticket["observed_at"]
    wid = ticket["object"]["id"]
    acceptance = dict(ticket, action="accept", reason="Accept the reviewed result",
                      request_id="review-" + _digest([wid, ticket["target_revision_ref"], at])[:32])
    return _digest(acceptance)


def _interrupted_correction(graph, selected):
    # Recover only the current decision (or its exact persisted pre-selection prefix).
    if graph["state"] == "rejected" and selected["decision_ref"]:
        decision = _resolve(graph["decisions"], selected["decision_ref"])
    elif graph["state"] == "review" and len(graph["pending_decisions"]) == 1:
        decision = graph["decisions"][graph["pending_decisions"][0]]
        if decision["confirmation"]["expected_selection_ref"] != graph["current"]["selection_ref"]:
            return None
    else:
        return None
    ticket = decision["confirmation"]
    digest = _original_review_digest(ticket)
    receipt = ticket["observed_at"] + "@" + digest
    if (ticket["action"] == "reject" and ticket["actor"] == graph["identity"]["acceptance_authority"]
            and ticket["target_revision_ref"] == selected["revision_ref"]
            and ticket["request_id"] == "revise-" + _digest([receipt, ticket["reason"]])):
        return ticket, digest
    return None


def _ordinary_revise(store, graph, selected, revision, wid, receipt, reason):
    """Record the human's revision request, then establish its unchanged editing baseline."""
    _require(re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z@[a-f0-9]{64}", receipt),
             "use the receipt for the result the human reviewed")
    _text(reason)
    _require(len(reason) <= 4096, "shorten the correction request")
    identity = graph["identity"]
    at, reviewed = receipt.split("@")
    request_id = "revise-" + _digest([receipt, reason])
    baseline_id = "rework-" + _digest([wid, request_id])
    previous = next((d for d in graph["decisions"].values()
                     if d["confirmation"]["request_id"] == request_id), None)
    if previous:
        ticket = previous["confirmation"]
    else:
        _require(graph["state"] == "review", "select the submitted result to revise")
        ticket = store.prepare(wid, action="reject", actor=identity["acceptance_authority"],
                               reason=reason, request_id=request_id, observed_at=at,
                               revision_ref=selected["revision_ref"])["ticket"]
    # Both decisions identify exactly the same review. Never apply the acceptance.
    reference = ticket["target_revision_ref"]
    _require(ticket["action"] == "reject" and ticket["reason"] == reason
             and ticket["observed_at"] == at and ticket["actor"] == identity["acceptance_authority"]
             and _original_review_digest(ticket) == reviewed, "the reviewed result changed; inspect it again")
    decision = store._decision(ticket)
    if previous and revision["record_id"] == baseline_id and graph["state"] == "active":
        parent = _resolve(graph["selections"], revision["expected_prior_selection"])
        _require(parent["decision_ref"] == record_ref(decision), "different rework decision")
        return {"work": wid, "state": "active", "selection": graph["current"]["selection_ref"]["sha256"]}
    saved = store.apply(ticket, confirm_token=_digest(ticket)[:16], match_reviewed_files=True)
    current = saved["current"]["selection_ref"]
    rejected = _resolve(saved["selections"], current)
    _require(saved["state"] == "rejected" and rejected["decision_ref"] == record_ref(decision),
             "the submitted result is no longer awaiting this correction")
    source = _resolve(saved["revisions"], reference)
    result = _resolve(saved["manifests"], source["result_refs"]["manifest"])["result"]
    manifest = make_manifest(result, result, scope=source["scope"])
    digest = _digest(manifest)
    baseline = dict(source, operation="rework", record_id=baseline_id, expected_prior_selection=current,
                    progress="active", next_action=reason, observed_at=at,
                    observed_scope=[reason], unavailable_scope=[],
                    result_refs={"manifest": {"id": digest, "sha256": digest}})
    saved = store.publish(identity, baseline, manifest, selection_id=baseline_id, operation_id=baseline_id)
    _require(saved["current"]["selection_ref"]["id"] == baseline_id and saved["state"] == "active",
             "this correction was already followed by another selection")
    return {"work": wid, "state": saved["state"], "selection": saved["current"]["selection_ref"]["sha256"]}


def _ordinary_confirmation(store, graph, wid, revision_ref, owner, summary, now, receipt, *, intent):
    """Regenerate an exact preview without a token file. Replays use the immutable decision if written."""
    at, expected = now, None
    if receipt is not None:
        _require(re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z@[a-f0-9]{64}", receipt),
                 "use the exact review receipt")
        at, expected = receipt.split("@")
    records = graph["acceptances"] if intent else graph["decisions"]
    prefix = "acceptance-" if intent else "decision-"
    previous = records.get(prefix + expected) if expected else None
    if previous:
        ticket = previous["confirmation"]
        _require(ticket["observed_at"] == at and ticket["action"] == "accept" and ticket["actor"] == owner
                 and ticket["target_revision_ref"] == revision_ref, "decision refers to a different review")
    else:
        if intent:
            _require(graph["current"] is None, "plan is already approved; use ordinary status")
        options = dict(actor=owner, reason="Approve this plan" if intent else "Accept the reviewed result",
                       observed_at=at, request_id="review-" + _digest([wid, revision_ref, at])[:32])
        if not intent:
            _require(graph["state"] == "review", "there is no submitted result awaiting review")
        prepared = (store.prepare(wid, revision_ref, **options) if intent else
                    store.prepare(wid, action="accept", revision_ref=revision_ref, **options))
        ticket = prepared["ticket"]
    digest = _digest(ticket)
    if expected is None:
        return {"work": wid, "review": summary, "receipt": at + "@" + digest,
                "question": ("이 범위로 진행할까요?" if intent else "이대로 마무리할까요, 아니면 고칠 부분이 있을까요?")}
    _require(digest == expected, "the reviewed plan or result changed; present it again")
    saved = store.apply(ticket, confirm_token=digest[:16])
    selection = _resolve(saved["selections"], saved["current"]["selection_ref"])
    decision_ref = selection["acceptance_ref"] if intent else selection["decision_ref"]
    _require(decision_ref and decision_ref["id"] == prefix + digest, "historical decision; inspect current state")
    return {"work": wid, "state": "plan-approved" if intent else saved["state"],
            "selection": saved["current"]["selection_ref"]["sha256"]}
