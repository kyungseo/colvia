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
import shutil
import sys
import sysconfig
import subprocess
import threading
from typing import Any

from .errors import ContractError, InjectedCrash
from .jsonio import canonical_json_bytes, exclusive_file_lock, load_json, sync_directory, write_new_bytes

ROOT_NAME = ".hrn"
IGNORE_BYTES = b"staging/\nlocks/\n"
ROOT_MEMBERS = frozenset({"format.json", ".gitignore", "detached.json", "product", "intents", "work", "planning", "staging", "locks", "executions"})
FORMAT_KEYS = {"record_type", "format_version", "authority_home_id", "created_at", "lineage"}
PLAN_KEYS = {"record_type", "schema_version", "operation_id", "action", "target_fingerprint", "authority_home_id", "expected_binding_ref", "candidate_release", "format_sha256", "truth_refs", "remove", "preserve", "created_at"}
ID = re.compile(r"[a-zA-Z0-9][a-zA-Z0-9_-]{0,95}\Z")
SHA = re.compile(r"[0-9a-f]{64}\Z")


SUPPORTED_PYTHON_VERSIONS = ((3, 14, 6), (3, 14, 7))
SUPPORTED_PYTHON_STRINGS = tuple(".".join(map(str, version)) for version in SUPPORTED_PYTHON_VERSIONS)
SUPPORTED_PYTHON_TEXT = ", ".join(SUPPORTED_PYTHON_STRINGS)



def windows_runtime_observation() -> dict:
    """Observe the actual Windows client and process pair, never just a profile."""
    result = {"supported": False, "classification": "unsupported", "platform": sys.platform}
    if sys.platform != "win32":
        result["reason"] = "windows-2 requires native Windows"
        return result
    try:
        import ctypes as C
        from ctypes import wintypes as W
        import sysconfig
        kernel = C.WinDLL("kernel32", use_last_error=True)
        process = kernel.GetCurrentProcess
        process.argtypes, process.restype = [], W.HANDLE
        machine = kernel.IsWow64Process2
        machine.argtypes, machine.restype = [W.HANDLE, C.POINTER(W.USHORT), C.POINTER(W.USHORT)], W.BOOL
        process_machine, native_machine = W.USHORT(), W.USHORT()
        if not machine(process(), C.byref(process_machine), C.byref(native_machine)):
            raise C.WinError(C.get_last_error())
        class Version(C.Structure):
            _fields_ = [("size", W.DWORD), ("major", W.DWORD), ("minor", W.DWORD),
                        ("build", W.DWORD), ("platform", W.DWORD), ("service_pack", W.WCHAR * 128),
                        ("sp_major", W.WORD), ("sp_minor", W.WORD), ("suite", W.WORD),
                        ("product_type", W.BYTE), ("reserved", W.BYTE)]
        version = Version()
        version.size = C.sizeof(version)
        query = C.WinDLL("ntdll").RtlGetVersion
        query.argtypes, query.restype = [C.POINTER(Version)], W.LONG
        status = query(C.byref(version))
        if status != 0:
            result.update(classification="unknown", reason="RtlGetVersion failed", ntstatus=int(status))
            return result
        result.update(os_version=[version.major, version.minor, version.build],
                      product_type=int(version.product_type), process_machine=int(process_machine.value),
                      native_machine=int(native_machine.value), pointer_bits=C.sizeof(C.c_void_p) * 8,
                      implementation=sys.implementation.name, python=list(sys.version_info[:3]),
                      releaselevel=sys.version_info.releaselevel,
                      free_threaded=bool(sysconfig.get_config_var("Py_GIL_DISABLED")),
                      process_platform=sysconfig.get_platform())
        result["supported"] = (version.major == 10 and version.build >= 22000 and version.product_type == 1
                               and process_machine.value == 0
                               and {"win-amd64": 0x8664, "win-arm64": 0xAA64}.get(result["process_platform"]) == native_machine.value
                               and C.sizeof(C.c_void_p) == 8 and sys.implementation.name == "cpython"
                               and sys.version_info[:3] in {(3, 14, 6), (3, 14, 7)}
                               and sys.version_info.releaselevel == "final" and not result["free_threaded"])
        result["classification"] = "supported" if result["supported"] else "unsupported"
        result["reason"] = "native tuple admitted" if result["supported"] else "OS/process/Python tuple is outside windows-2 policy"
    except (AttributeError, OSError, ValueError) as exc:
        result.update(classification="unknown", reason=type(exc).__name__, winerror=getattr(exc, "winerror", None))
    return result


# A distribution qualification is a tuple and exact normalized tree, never a
# blanket addition to SUPPORTED_PYTHON_VERSIONS or the Windows policy.
MACOS_RUNTIME_OBJECTS = "3e730af422bdfa77dff666ac882726ce12e87d7cceae6b39c17775b2d88e2510"
MACOS_RUNTIME_FILES = "ed7b15de8cf79458c2d0c06713424bcc48326f1c59fe454844e1c8fa1400fe89"
MACOS_RUNTIME_ID = "e3d42cd0b305583e46e16d5265e3b6ac24a01ef9ee32a08418e1be5965db816f"


MANAGED_MACOS_RUNTIME_DECLARATION = {
    "python": "3.14.10", "platform": "darwin", "machine": "arm64",
    "process_platform": "macosx-11.0-arm64", "isolated": True,
    "bytecode_disabled": True, "tree_identity": MACOS_RUNTIME_ID,
    "admission": "exact normalized tree and manifests; location-independent; not authentication",
}
RUNTIME_SELECTION_GUIDANCE = (
    f"use final GIL-enabled CPython {SUPPORTED_PYTHON_TEXT} before mutation; "
    "for a managed macOS installation, preserve damaged bytes and restore the exact pinned "
    "CPython 3.14.10 tree and manifests through the documented recovery procedure"
)


def runtime_admission_path(window: str | None, supported: bool) -> str:
    """Describe an already computed gate result without re-verifying the tree."""
    if not supported:
        return "unsupported"
    if window == "windows-2":
        return "windows-window-policy"
    if sys.platform == "darwin" and sys.version_info[:3] == (3, 14, 10):
        return "managed-macos-exact-tree"
    return "legacy-version"


def managed_macos_runtime_supported() -> bool:
    """Post-start corroboration; the pinned OS verifier owns first execution.

    This also rejects direct installed entry through a different interpreter.
    No writable verification stamp or environment-selected catalog is trusted.
    """
    if (sys.platform != "darwin" or sys.implementation.name != "cpython"
            or sys.version_info[:3] != (3, 14, 10)
            or sys.version_info.releaselevel != "final"
            or sysconfig.get_config_var("Py_GIL_DISABLED")
            or os.uname().machine != "arm64"
            or sysconfig.get_platform() != "macosx-11.0-arm64"
            or not sys.flags.isolated or not sys.dont_write_bytecode):
        return False
    try:
        root = Path(sys.prefix).absolute()
        if root != Path(sys.base_prefix).absolute():
            return False
        for p in (root, *root.parents):
            if not stat.S_ISDIR(p.lstat().st_mode):
                return False
        executable = root / "bin/python3.14"
        if Path(sys.executable).resolve(strict=True) != executable:
            return False
        def regular(p, digest=None):
            before = p.lstat()
            if (not stat.S_ISREG(before.st_mode) or before.st_nlink != 1
                    or before.st_uid != os.getuid()):
                raise ValueError("unsafe runtime file")
            raw = p.read_bytes()
            after = p.lstat()
            fields = lambda x: (x.st_dev,x.st_ino,x.st_size,x.st_mtime_ns,x.st_ctime_ns)
            if fields(before) != fields(after) or digest and hashlib.sha256(raw).hexdigest() != digest:
                raise ValueError("runtime drift")
            return raw
        objects = regular(root.parent / "objects.txt", MACOS_RUNTIME_OBJECTS)
        checksums = regular(root.parent / "files.sha256", MACOS_RUNTIME_FILES)
        actual = []
        files = {}
        pending = [(root, ".")]
        while pending:
            path, name = pending.pop()
            info = path.lstat()
            if info.st_uid != os.getuid():
                return False
            if stat.S_ISLNK(info.st_mode):
                actual.append("Symbolic Link|-|" + name + "|" + os.readlink(path))
            elif stat.S_ISDIR(info.st_mode):
                actual.append("Directory|" + format(stat.S_IMODE(info.st_mode), "o") + "|" + name + "|")
                pending.extend((p, "./" + p.relative_to(root).as_posix()) for p in path.iterdir())
            elif stat.S_ISREG(info.st_mode) and info.st_nlink == 1:
                actual.append("Regular File|" + format(stat.S_IMODE(info.st_mode), "o") + "|" + name + "|")
                files[name.removeprefix("./")] = path
            else:
                return False
        if ("\n".join(sorted(actual)) + "\n").encode() != objects:
            return False
        expected = {}
        for line in checksums.decode("ascii").splitlines():
            digest, name = line.split("  ", 1)
            if not re.fullmatch("[0-9a-f]{64}", digest) or name in expected:
                return False
            expected[name] = digest
        if files.keys() != expected.keys():
            return False
        for name, path in files.items():
            regular(path, expected[name])
        return True
    except (OSError, ValueError, UnicodeError, RuntimeError):
        return False


def runtime_supported(window: str | None = None) -> bool:
    """Qualified final, GIL-enabled CPython builds; not interpreter authentication."""
    if window == "windows-2":
        return windows_runtime_observation()["supported"]
    if sys.platform == "win32":
        return False
    return (sys.implementation.name == "cpython"
            and (sys.version_info[:3] in SUPPORTED_PYTHON_VERSIONS
                 or managed_macos_runtime_supported())
            and getattr(sys.version_info, "releaselevel", None) == "final"
            and not sysconfig.get_config_var("Py_GIL_DISABLED"))


def require_supported_runtime(window: str | None = None) -> None:
    if window in ("official-execution-1", "official-execution-2") and sys.platform != "darwin":
        raise ContractError("HV2-WORKSPACE-RUNTIME", "official execution requires macOS")
    if window == "windows-2" or sys.platform == "win32":
        if window != "windows-2":
            raise ContractError("HV2-WORKSPACE-RUNTIME", "native Windows mutation requires a verified windows-2 window")
        observed = windows_runtime_observation()
        if not observed["supported"]:
            raise ContractError("HV2-WORKSPACE-RUNTIME", "windows-2 runtime " + observed["classification"] + ": " + observed["reason"])
        if not sys.flags.isolated or not sys.dont_write_bytecode:
            raise ContractError("HV2-WORKSPACE-RUNTIME", "windows-2 mutation requires explicit allowed Python -I -B")
    if not runtime_supported(window):
        raise ContractError("HV2-WORKSPACE-RUNTIME", RUNTIME_SELECTION_GUIDANCE)


def _error(detail: str) -> ContractError:
    return ContractError("HV2-WORKSPACE-CONTRACT", detail)


def _exists(path: Path) -> bool:
    if sys.platform == "win32":
        from .jsonio import windows_path_observation
        return windows_path_observation(path, allow_missing=True)["exists"]
    try:
        path.lstat()
        return True
    except FileNotFoundError:
        return False


def _require_kind(path: Path, directory: bool) -> None:
    if sys.platform == "win32":
        from .jsonio import windows_path_observation
        windows_path_observation(path)
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


def safe_target(target: Path, *, mutation: bool = False) -> Path:
    if sys.platform == "win32":
        from .jsonio import _windows_absolute, windows_path_observation
        absolute = _windows_absolute(target)
        windows_path_observation(absolute, mutation=mutation)
    else:
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


def git_executable() -> str:
    """Avoid Apple's installation/cache shim; never start CLT setup implicitly."""
    if sys.platform != "darwin" or shutil.which("git") != "/usr/bin/git":
        return "git"
    environment = {"PATH": "/usr/bin:/bin", "LC_ALL": "C"}
    if os.environ.get("DEVELOPER_DIR"):
        environment["DEVELOPER_DIR"] = os.environ["DEVELOPER_DIR"]
    try:
        selected = subprocess.run(["/usr/bin/xcode-select", "-p"], capture_output=True,
                                  env=environment, timeout=10)
    except subprocess.TimeoutExpired as error:
        raise ContractError("HV2-WORKSPACE-TARGET", "Git developer directory lookup timed out") from error
    if selected.returncode:
        if b"unable to get active developer directory" in selected.stderr.lower():
            raise FileNotFoundError("Git developer tools are not installed")
        raise ContractError("HV2-WORKSPACE-TARGET", "Git developer directory unavailable")
    developer = Path(os.fsdecode(selected.stdout).strip())
    candidate = developer / "usr/bin/git"
    if not developer.is_absolute() or not candidate.is_file():
        raise FileNotFoundError("Git binary unavailable in selected developer tools")
    candidate = candidate.resolve(strict=True)
    info = candidate.stat()
    if not stat.S_ISREG(info.st_mode) or not info.st_mode & 0o111:
        raise FileNotFoundError("Selected Git is not executable")
    return str(candidate)


def git_environment() -> dict[str, str]:
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update({"GIT_OPTIONAL_LOCKS": "0", "LC_ALL": "C"})
    # A closed caller may disable user/system configuration, but cannot inject
    # arbitrary GIT_* settings or configuration paths through this boundary.
    if all(os.environ.get(k) == v for k, v in {
            "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": "/dev/null",
            "GIT_CONFIG_SYSTEM": "/dev/null"}.items()):
        env.update({"GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": "/dev/null",
                    "GIT_CONFIG_SYSTEM": "/dev/null", "GIT_ATTR_NOSYSTEM": "1",
                    "XDG_CONFIG_HOME": "/dev/null", "GIT_TERMINAL_PROMPT": "0"})
    return env


def _topology_probe(target: Path, env: dict[str, str]) -> tuple[int, bytes, bytes]:
    result = subprocess.run(
        [git_executable(), "-C", str(target), "rev-parse", "--path-format=absolute", "--show-toplevel", "--absolute-git-dir", "--git-common-dir", "--show-superproject-working-tree"],
        capture_output=True, env=env, check=False,
    )
    return result.returncode, result.stdout, result.stderr


class _TopologyObservation:
    """Share only validated primary raw probes within one status Work sweep."""
    _kinds = frozenset({"primary"})

    def __init__(self, target: Path):
        self.target = safe_target(target)
        self._environment = None
        self._raw = None
        self._kind = None
        self._reused = 0
        self._finishing = False
        self._closed = False

    def _probe(self, target: Path, env: dict[str, str], *, mutation: bool):
        if self._closed or mutation or target != self.target:
            raise ContractError("HV2-WORKSPACE-TARGET", "invalid topology observation use")
        if self._environment is not None and self._environment != env:
            raise ContractError("HV2-WORKSPACE-TARGET", "topology observation environment changed")
        if self._raw is None or self._finishing:
            return _topology_probe(target, env)
        self._reused += 1
        return self._raw

    def _probe_identity(self, raw):
        return raw

    def _accept(self, env: dict[str, str], raw: tuple[int, bytes, bytes], kind: str):
        if kind not in self._kinds:
            raise ContractError("HV2-WORKSPACE-TARGET", "topology observation is not primary")
        if self._finishing:
            if self._probe_identity(raw) != self._probe_identity(self._raw) or kind != self._kind:
                raise ContractError("HV2-WORKSPACE-TARGET", "unstable topology observation")
        elif self._raw is None:
            self._raw = raw
            self._kind = kind
            self._environment = dict(env)

    def _unavailable_git(self) -> None:
        raise ContractError("HV2-WORKSPACE-TARGET", "Git unavailable during topology observation")

    def finish(self) -> None:
        if self._closed:
            raise ContractError("HV2-WORKSPACE-TARGET", "topology observation already closed")
        try:
            if self._reused:
                self._finishing = True
                classify_target(self.target, _topology_observation=self)
        finally:
            self.close()

    def close(self) -> None:
        self._closed = True
        self._raw = None
        self._kind = None
        self._environment = None


class _DetachTopologyObservation(_TopologyObservation):
    """Read-only probes for one detach observation, never across removals.

    Preserve all readable topology kinds. Mutation admission stays independent.
    With no Git binary there is no raw probe to share; every read checks again.
    """
    _kinds = frozenset({"primary", "non-git", "subdirectory", "submodule",
                        "linked-worktree", "separate-git-dir", "nested-repository"})

    def _probe_identity(self, raw):
        # Classification has validated stderr for non-Git. Diagnostic text is
        # not topology identity (platform shims may print varying cache paths).
        return raw[:2]

    def _unavailable_git(self) -> None:
        if self._raw is not None:
            super()._unavailable_git()


def _classify_target(target: Path, *, mutation: bool = False, _topology_observation=None) -> dict[str, str]:
    target = safe_target(target, mutation=mutation)
    if mutation and sys.platform == "win32":
        from .jsonio import windows_path_observation
        windows_path_observation(target, mutation=True)
    if any(any(p.name.casefold() == ROOT_NAME.casefold() for p in parent.iterdir()) for parent in target.parents):
        raise ContractError("HV2-WORKSPACE-TARGET", "nested workspace authority is unsupported")
    if sys.platform == "win32":
        from .jsonio import windows_path_observation
        for ancestor in (target, *target.parents):
            if _exists(ancestor / ".git"):
                windows_path_observation(ancestor / ".git")
    try:
        env = git_environment()
        raw = (_topology_probe(target, env) if _topology_observation is None else
               _topology_observation._probe(target, env, mutation=mutation))
        returncode, stdout, stderr = raw
    except FileNotFoundError:
        if _topology_observation is not None:
            _topology_observation._unavailable_git()
        # No Git binary is sufficient only for a tree with no ancestral Git metadata.
        if any(_exists(p / ".git") for p in (target, *target.parents)):
            raise ContractError("HV2-WORKSPACE-TARGET", "Git unavailable for repository target") from None
        return {"kind": "non-git", "target": str(target)}
    if returncode:
        if b"not a git repository" in stderr.lower() and not any(_exists(p / ".git") for p in (target, *target.parents)):
            if _topology_observation is not None:
                _topology_observation._accept(env, raw, "non-git")
            return {"kind": "non-git", "target": str(target)}
        raise ContractError("HV2-WORKSPACE-TARGET", "Git classification failed")
    lines = os.fsdecode(stdout).splitlines()
    if len(lines) not in {3, 4}:
        raise ContractError("HV2-WORKSPACE-TARGET", "ambiguous Git topology")
    if sys.platform == "win32":
        for value in lines[:3]:
            windows_path_observation(Path(value))
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
    if _topology_observation is not None:
        _topology_observation._accept(env, raw, kind)
    return {"kind": kind, "target": str(target)}


def classify_target(target: Path, *, mutation: bool = False, _topology_observation=None) -> dict[str, str]:
    try:
        if _topology_observation is not None:
            return _classify_target(target, mutation=mutation, _topology_observation=_topology_observation)
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
                _require_kind(path, name in {"product", "intents", "work", "planning", "staging", "locks", "executions"})
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
    if plan["record_type"] != "lifecycle-plan" or type(plan["schema_version"]) is not int or plan["schema_version"] not in (1, 4, 5, 6, 7, 8) or plan["action"] != "init":
        raise _error("not a supported init plan")
    if not all(_id(plan[k]) for k in ("operation_id", "authority_home_id")) or not _text(plan["created_at"]) or not all(_sha(plan[k]) for k in ("target_fingerprint", "format_sha256")):
        raise _error("invalid init identity or digest")
    if plan["expected_binding_ref"] is not None or any(plan[k] != [] for k in ("truth_refs", "remove", "preserve")):
        raise _error("invalid fresh init claims")
    release = _exact(plan["candidate_release"], {"id", "sha256", "inventory_id"})
    if not _sha(release["sha256"]) or release["id"] != "product-release-" + release["sha256"][:24] or (not isinstance(release["inventory_id"], str) or release["inventory_id"] not in {"human-1", "worker-1", "umbrella-1", "planning-1", "checkout-1", "entry-1", "delegation-1", "continuation-1", "windows-2", "official-execution-1", "official-execution-2"}):
        raise _error("invalid init release")
    if plan["schema_version"] != (8 if release["inventory_id"] == "official-execution-2" else 7 if release["inventory_id"] == "official-execution-1" else 6 if release["inventory_id"] == "windows-2" else 5 if release["inventory_id"] == "continuation-1" else 4 if release["inventory_id"] == "delegation-1" else 1):
        raise _error("init schema/window pair")


def _bootstrap_prefix(root: Path) -> None:
    present = {p.name for p in root.iterdir()}
    if "format.json" not in present and present != {"product"}:
        raise _error("not an exact bootstrap prefix")
    if "format.json" in present and ".gitignore" not in present and present - {"product", "format.json"}:
        raise _error("not an exact bootstrap prefix")
    if "work" in present and "intents" not in present:
        raise _error("out-of-order bootstrap directories")


def _durable_directory(path: Path) -> None:
    if sys.platform == "win32":
        from .jsonio import windows_path_observation
        windows_path_observation(path, mutation=True, allow_missing=True)
    try:
        path.mkdir()
    except FileExistsError:
        _require_kind(path, True)
    except OSError as exc:
        if sys.platform == "win32":
            from .jsonio import _windows_api
            raise _windows_api().failure("CreateDirectoryW", "directory-publication", getattr(exc, "winerror", None)) from exc
        raise
    sync_directory(path.parent)
    sync_directory(path)


def _write_exact(path: Path, data: bytes) -> None:
    if _exists(path):
        _require_kind(path, False)
        if path.read_bytes() != data:
            raise _error(f"immutable mismatch: {path.name}; preserve torn/modified bytes for explicit manual disposition")
        from .jsonio import sync_existing_file
        sync_existing_file(path)
        sync_directory(path.parent)
        return
    write_new_bytes(path, data)


def _validate_init_plan(plan: Any, value: dict[str, Any], target: Path) -> dict[str, Any]:
    plan = _exact(plan, PLAN_KEYS)
    if plan["record_type"] != "lifecycle-plan" or type(plan["schema_version"]) is not int or plan["schema_version"] not in (1, 4, 5, 6, 7, 8) or plan["action"] != "init":
        raise _error("not a supported init plan")
    if not _id(plan["operation_id"]) or plan["authority_home_id"] != value["authority_home_id"] or not _text(plan["created_at"]):
        raise _error("init plan identity")
    if plan["target_fingerprint"] != target_fingerprint(target) or plan["format_sha256"] != hashlib.sha256(canonical_json_bytes(value)).hexdigest():
        raise _error("init plan target/format mismatch")
    if plan["expected_binding_ref"] is not None or plan["truth_refs"] != [] or plan["remove"] != [] or plan["preserve"] != []:
        raise _error("fresh init plan cannot claim existing truth")
    release = _exact(plan["candidate_release"], {"id", "sha256", "inventory_id"})
    if not _id(release["id"]) or not _sha(release["sha256"]) or (not isinstance(release["inventory_id"], str) or release["inventory_id"] not in {"human-1", "worker-1", "umbrella-1", "planning-1", "checkout-1", "entry-1", "delegation-1", "continuation-1", "windows-2", "official-execution-1", "official-execution-2"}):
        raise _error("init plan candidate")
    if plan["schema_version"] != (8 if release["inventory_id"] == "official-execution-2" else 7 if release["inventory_id"] == "official-execution-1" else 6 if release["inventory_id"] == "windows-2" else 5 if release["inventory_id"] == "continuation-1" else 4 if release["inventory_id"] == "delegation-1" else 1):
        raise _error("init schema/window pair")
    if release["id"] != "product-release-" + release["sha256"][:24]:
        raise _error("init plan release identity")
    return plan


def bootstrap_root(target: Path, plan: dict[str, Any], value: dict[str, Any], *, recover: bool = False, inject_at: str | None = None) -> dict[str, Any]:
    """Publish root primitives only. Product installation must validate the candidate.

No installed entry calls this yet. Each retry is explicit and exact; detached or
unknown state is never adopted. Process crash tests do not establish power-loss safety.
"""
    # The init record declares the policy; the operating system never selects it.
    _validate_plan_shape(plan)
    require_supported_runtime(plan["candidate_release"]["inventory_id"])
    target = Path(classify_target(target, mutation=True)["target"])
    if _root_aliases(target):
        raise _error("case-alias of workspace root; preserve existing path")
    value = validate_format(value)
    plan = _validate_init_plan(plan, value, target)
    points = {"after-root", "after-product-dir", "after-plan", "after-format", "after-ignore", "after-intents", "after-work"}
    if inject_at is not None and inject_at not in points:
        raise _error("unknown crash point")
    root = target / ROOT_NAME
    from .jsonio import windows_preflight_files
    windows_preflight_files([root / "product/init-plan.json", root / "format.json", root / ".gitignore",
                             root / "product", root / "intents", root / "work"])
    if _exists(root):
        if not recover:
            raise _error("existing root requires explicit recovery")
        _require_kind(root, True)
        if set(p.name for p in root.iterdir()) - ROOT_MEMBERS or _exists(root / "detached.json"):
            raise _error("existing root is not this initialization")
        for name in ROOT_MEMBERS:
            member = root / name
            if _exists(member):
                _require_kind(member, name in {"product", "intents", "work", "planning", "staging", "locks", "executions"})
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


def _guard_runtime_window(target: Path) -> str | None:
    """Read immutable policy before scratch creation; never authorizes a write.

The caller still verifies the current product/records under the common guard.
Init policy is stable within windows-2; its cross-window transitions are forbidden.
"""
    detached = target / ROOT_NAME / "detached.json"
    if _exists(detached):
        receipt = _file_json(detached)
        if receipt.get("schema_version") in (6, 7, 8):
            from .product import _detach_plan_shape, _detach_receipt
            plan = _detach_plan_shape(receipt.get("plan"), _file_json(target / ROOT_NAME / "format.json"))
            if receipt != _detach_receipt(plan):
                raise _error("detach policy receipt mismatch")
            return "official-execution-2" if receipt["schema_version"] == 8 else "official-execution-1" if receipt["schema_version"] == 7 else "windows-2"
    initial = target / ROOT_NAME / "product/init-plan.json"
    if _exists(initial):
        plan = _file_json(initial)
        _validate_plan_shape(plan)
        window = plan["candidate_release"]["inventory_id"]
        # This selects a stricter OS/execution barrier, never establishes authority.
        # The caller still validates the complete receipt history under the lock.
        binding_path = target / ROOT_NAME / "product/binding.json"
        # The immutable init can predate several validated runtime upgrades.
        # All legacy POSIX histories need the same stricter official barrier;
        # this hint still cannot authorize a write or a cross-OS transition.
        if window in {"human-1", "worker-1", "umbrella-1", "planning-1", "checkout-1",
                      "entry-1", "delegation-1", "continuation-1", "official-execution-1"} and _exists(binding_path):
            binding = _file_json(binding_path)
            if isinstance(binding, dict) and isinstance(binding.get("active_release"), dict) and binding["active_release"].get("inventory_id") in ("official-execution-1", "official-execution-2"):
                window = binding["active_release"]["inventory_id"]
        return window
    return None


@contextmanager
def writer_guard(target: Path, *, purpose: str = "work"):
    """One stable outer lock for normal writes or exact lifecycle recovery.

Recovery purpose admits only a detach candidate, never arbitrary degraded bytes.
The caller verifies the receipt and complete operation under the same guard.
"""
    target = safe_target(target)
    window = _guard_runtime_window(target)
    require_supported_runtime(window)
    allowed = {"work": {"root-ready"}, "detach-recovery": {"detach-candidate"}, "official-resolution": {"root-ready"}}
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
            if _guard_runtime_window(target) != window:
                raise _error("workspace policy changed while acquiring guard")
            require_supported_runtime(window)
            if inspect_root(target)["classification"] not in allowed[purpose]:
                raise _error("workspace changed while acquiring guard")
            if _exists(root / "executions"):
                if window not in ("official-execution-1", "official-execution-2"):
                    raise _error("execution records require the official window")
                from .official_state import require_no_open
                if purpose != "official-resolution":
                    require_no_open(target)
            elif purpose == "official-resolution":
                raise _error("no execution records to resolve")
            yield
    finally:
        _guard_state.held = held
