from __future__ import annotations

import errno
import hashlib
import json
import math
import ntpath
import os
import stat
import sys
import tempfile
import unicodedata
from functools import lru_cache
from contextlib import contextmanager
from contextvars import ContextVar, copy_context
from pathlib import Path
from typing import Any

from .errors import ContractError

if sys.platform != "win32":
    import fcntl
else:
    fcntl = None


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
    except (RecursionError, TypeError, UnicodeEncodeError, ValueError) as exc:
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
        if isinstance(current, float) and not math.isfinite(current):
            raise ContractError("HV2-JSON-NONFINITE", "numeric overflow")
        if isinstance(current, dict):
            stack.extend((child, depth + 1) for child in current.values())
        elif isinstance(current, list):
            stack.extend((child, depth + 1) for child in current)
    if require_canonical and canonical_json_bytes(value) != data:
        raise ContractError("HV2-JSON-NONCANONICAL", "stored bytes do not match canonical emission")
    return value


def load_json(path: Path, *, require_canonical: bool = False) -> Any:
    return decode_json_bytes(path.read_bytes(), require_canonical=require_canonical)



class _WindowsAPI:
    """Lazy, typed Win32 bindings; importing this module never loads them on POSIX."""

    def __init__(self):
        if sys.platform != "win32":
            raise ContractError("HV2-WINDOWS-RUNTIME", "native Windows API unavailable")
        import ctypes as C
        from ctypes import wintypes as W
        self.C = C
        self.W = W
        self.kernel = C.WinDLL("kernel32", use_last_error=True)

        class AttributeTag(C.Structure):
            _fields_ = [("attributes", W.DWORD), ("tag", W.DWORD)]

        class FileId(C.Structure):
            _fields_ = [("volume", C.c_ulonglong), ("identifier", C.c_ubyte * 16)]

        class Standard(C.Structure):
            _fields_ = [("allocation", C.c_longlong), ("size", C.c_longlong),
                        ("links", W.DWORD), ("delete_pending", C.c_ubyte), ("directory", C.c_ubyte)]

        class Basic(C.Structure):
            _fields_ = [("creation", C.c_longlong), ("access", C.c_longlong),
                        ("write", C.c_longlong), ("change", C.c_longlong), ("attributes", W.DWORD)]

        class Overlapped(C.Structure):
            _fields_ = [("Internal", C.c_size_t), ("InternalHigh", C.c_size_t),
                        ("Offset", W.DWORD), ("OffsetHigh", W.DWORD), ("hEvent", W.HANDLE)]

        self.AttributeTag, self.FileId, self.Standard, self.Overlapped = AttributeTag, FileId, Standard, Overlapped
        self.Basic = Basic
        self.invalid = C.c_void_p(-1).value
        self.bind("CreateFileW", W.HANDLE, W.LPCWSTR, W.DWORD, W.DWORD, C.c_void_p, W.DWORD, W.DWORD, W.HANDLE)
        self.bind("CloseHandle", W.BOOL, W.HANDLE)
        self.bind("GetFileInformationByHandleEx", W.BOOL, W.HANDLE, C.c_int, C.c_void_p, W.DWORD)
        self.bind("GetFinalPathNameByHandleW", W.DWORD, W.HANDLE, W.LPWSTR, W.DWORD, W.DWORD)
        self.bind("GetVolumeInformationByHandleW", W.BOOL, W.HANDLE, W.LPWSTR, W.DWORD,
                  C.POINTER(W.DWORD), C.POINTER(W.DWORD), C.POINTER(W.DWORD), W.LPWSTR, W.DWORD)
        self.bind("GetDriveTypeW", W.UINT, W.LPCWSTR)
        self.bind("FlushFileBuffers", W.BOOL, W.HANDLE)
        self.bind("GetHandleInformation", W.BOOL, W.HANDLE, C.POINTER(W.DWORD))
        self.bind("CreateEventW", W.HANDLE, C.c_void_p, W.BOOL, W.BOOL, W.LPCWSTR)
        self.bind("LockFileEx", W.BOOL, W.HANDLE, W.DWORD, W.DWORD, W.DWORD, W.DWORD, C.POINTER(Overlapped))
        self.bind("UnlockFileEx", W.BOOL, W.HANDLE, W.DWORD, W.DWORD, W.DWORD, C.POINTER(Overlapped))
        self.bind("CancelIoEx", W.BOOL, W.HANDLE, C.POINTER(Overlapped))
        self.bind("GetOverlappedResult", W.BOOL, W.HANDLE, C.POINTER(Overlapped), C.POINTER(W.DWORD), W.BOOL)
        self.bind("WaitForSingleObject", W.DWORD, W.HANDLE, W.DWORD)

    def bind(self, name, result, *args):
        function = getattr(self.kernel, name)
        function.restype, function.argtypes = result, args
        setattr(self, name, function)

    def failure(self, api, phase, error=None):
        error = self.C.get_last_error() if error is None else error
        return ContractError("HV2-WINDOWS-IO", f"api={api}; result=failed; phase={phase}; winerror={error}; preserve actual prefix")

    def close(self, handle):
        if not self.CloseHandle(handle):
            raise self.failure("CloseHandle", "handle-cleanup")


@lru_cache(maxsize=1)
def _windows_api():
    return _WindowsAPI()


def _windows_absolute(path: Path) -> Path:
    drive, tail = ntpath.splitdrive(os.fspath(path))
    if drive and not tail.startswith(("/", chr(92))):
        raise ContractError("HV2-WINDOWS-PATH", "drive-relative native path is unsupported")
    # Win32 full-path resolution can remove trailing dots/spaces. Refuse the
    # original spelling before it can become an apparently safe different path.
    if ntpath.isreserved(os.fspath(path)):
        raise ContractError("HV2-WINDOWS-PATH", "unsupported path component")
    # Use the ordinary Win32 namespace without relying on machine-wide long
    # path settings. A directory must leave the documented MAX_PATH - 12
    # margin. Apply the same conservative bound to every observed path so an
    # overlong CreateFileW error cannot be mistaken for an absent leaf.
    if len(os.fspath(path).encode("utf-16-le", errors="surrogatepass")) // 2 >= 248:
        raise ContractError("HV2-WINDOWS-PATH", "native path exceeds the supported 247 UTF-16 code units")
    absolute = Path(os.path.abspath(path))
    if len(str(absolute).encode("utf-16-le", errors="surrogatepass")) // 2 >= 248:
        raise ContractError("HV2-WINDOWS-PATH", "native path exceeds the supported 247 UTF-16 code units")
    # Device, UNC, drive-relative and alternate-stream spellings are not local
    # mutation paths. Read callers report the unsupported classification.
    if len(absolute.drive) != 2 or absolute.drive[1] != ":" or not absolute.root:
        raise ContractError("HV2-WINDOWS-PATH", "unsupported native local path namespace")
    for part in absolute.parts[1:]:
        if (unicodedata.normalize("NFC", part) != part or os.path.isreserved(part)
                or part in {".", ".."} or any(ord(c) < 32 for c in part)):
            raise ContractError("HV2-WINDOWS-PATH", "unsupported path component")
    return absolute


def _windows_open(path: Path, *, access=0, share=7, disposition=3, extra_flags=0):
    api = _windows_api()
    handle = api.CreateFileW(str(path), access, share, None, disposition,
                             0x02000000 | 0x00200000 | extra_flags, None)
    if handle == api.invalid:
        raise api.C.WinError(api.C.get_last_error())
    return handle


def _windows_final_name(handle, flags=0):
    api = _windows_api()
    # Keep every path observation fresh; avoid a size-only native query when
    # the normalized name fits. No handle, ancestor or result is cached.
    buf = api.C.create_unicode_buffer(512)
    length = api.GetFinalPathNameByHandleW(handle, buf, len(buf), flags)
    if not length:
        raise api.failure("GetFinalPathNameByHandleW", "path-observation")
    if length >= len(buf):
        # An insufficient-buffer result includes the terminating null. Bound
        # allocation and retries; never accept truncation or repeated growth.
        if length > 32768:
            raise api.failure("GetFinalPathNameByHandleW", "path-observation")
        buf = api.C.create_unicode_buffer(length)
        length = api.GetFinalPathNameByHandleW(handle, buf, len(buf), flags)
        if not length or length >= len(buf):
            raise api.failure("GetFinalPathNameByHandleW", "path-observation")
    return buf.value


def _windows_handle_state(handle, *, mutation=False):
    api = _windows_api()
    # Classify unsupported mutation filesystems before NTFS identity queries.
    if mutation:
        fs = api.C.create_unicode_buffer(261)
        if not api.GetVolumeInformationByHandleW(handle, None, 0, None, None, None, fs, len(fs)):
            raise api.failure("GetVolumeInformationByHandleW", "filesystem-admission")
        if fs.value != "NTFS":
            raise ContractError("HV2-WINDOWS-FILESYSTEM", "mutation requires native local NTFS")
    tag, identity, standard, basic = api.AttributeTag(), api.FileId(), api.Standard(), api.Basic()
    for kind, value in ((9, tag), (18, identity), (1, standard), (0, basic)):
        if not api.GetFileInformationByHandleEx(handle, kind, api.C.byref(value), api.C.sizeof(value)):
            raise api.failure("GetFileInformationByHandleEx", "path-observation")
    if tag.attributes & 0x400 or tag.tag:
        raise ContractError("HV2-WINDOWS-PATH", "reparse point is unsupported")
    if standard.delete_pending:
        raise ContractError("HV2-WINDOWS-PATH", "path deletion pending")
    if tag.attributes != basic.attributes:
        raise ContractError("HV2-WINDOWS-PATH", "attributes changed during observation")
    name = _windows_final_name(handle)
    result = {"identity": (int(identity.volume), bytes(identity.identifier).hex()),
              "attributes": int(tag.attributes), "directory": bool(standard.directory),
              "links": int(standard.links), "final_name": name,
              "content_signature": (int(standard.size), int(basic.creation), int(basic.write), int(basic.change))}
    if mutation:
        volume_name = _windows_final_name(handle, 1)  # VOLUME_NAME_GUID
        prefix, sep, _ = volume_name.partition("}\\")
        if not sep or not prefix.startswith("\\\\?\\Volume{"):
            raise ContractError("HV2-WINDOWS-FILESYSTEM", "local volume identity unavailable")
        result["volume"] = prefix + "}"
    return result


_windows_detach_read_observation = ContextVar("windows_detach_read_observation", default=None)


class _WindowsDetachReadObservation:
    """Ancestor observations for one read sweep, discarded before any removal."""
    def __init__(self, root: Path):
        self.root = _windows_absolute(root)
        self.directories = {}
        self.prefixes = {}
        self.lexical = {}
        self.spellings = {}
        self.accepted = set()
        self.closed = False
        from threading import Lock
        self._directory_lock = Lock()
        self._executor = None
        self._batch_active = False

    def read_batch(self, reader, items):
        """Join fresh independent reads before the caller can continue.

        Only this read sweep shares ancestor observations. Workers never write
        files, reuse leaf results, or outlive an error or the enclosing scope.
        """
        from concurrent.futures import ThreadPoolExecutor, wait
        if self.closed or self._batch_active:
            raise ContractError("HV2-WINDOWS-PATH", "invalid detach read batch")
        values = list(items)
        if len(values) < 2:
            return [reader(item) for item in values]
        self._batch_active = True
        futures = []
        try:
            if self._executor is None:
                self._executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="colvia-detach-read")
            for item in values:
                futures.append(self._executor.submit(copy_context().run, reader, item))
            return [future.result() for future in futures]
        finally:
            # A failed member cannot leave another observation running while
            # the outer scope validates ancestors, clears state or mutates.
            for future in futures:
                future.cancel()
            wait(futures)
            self._batch_active = False

    def absolute(self, path: Path) -> Path:
        # Only pure spelling work is shared. Relative spellings must observe
        # the current working directory every time; raw keys preserve aliases.
        raw = os.fspath(path)
        if raw in self.lexical:
            return self.lexical[raw]
        absolute = _windows_absolute(path)
        if Path(path).is_absolute() and self.accepts(absolute) and len(self.lexical) < 4096:
            self.lexical[raw] = absolute
        return absolute

    def accepts(self, path: Path) -> bool:
        if self.closed:
            raise ContractError("HV2-WINDOWS-PATH", "closed detach read observation")
        raw = str(path)
        if raw in self.accepted:
            return True
        inside = path == self.root or self.root in path.parents or path in self.root.parents
        if inside and len(self.accepted) < 4096:
            self.accepted.add(raw)
        return inside

    def spelling(self, path: Path):
        # Pure representations only, keyed by exact spelling rather than Path's
        # case-insensitive equality. No filesystem observation is stored here.
        raw = str(path)
        value = self.spellings.get(raw)
        if value is None:
            parent = path.parent
            value = (raw, parent, str(parent), ("\\\\?\\" + raw).rstrip("\\").casefold(),
                     tuple(reversed((path, *path.parents))))
            if len(self.spellings) < 4096:
                self.spellings[raw] = value
        return value

    def remember(self, path: Path, state: dict) -> None:
        if not state["directory"]:
            return
        # Readers can discover the same ancestor concurrently. Compare and
        # publish its observation atomically; never lose a conflicting state.
        with self._directory_lock:
            previous = self.directories.get(path)
            if previous is not None and any(state[key] != previous[key] for key in ("identity", "attributes", "final_name")):
                raise ContractError("HV2-WINDOWS-PATH", "ancestor changed during detach read observation")
            self.directories[path] = dict(state)

    def finish(self) -> None:
        # Re-open every shared ancestor independently, including the target's
        # chain. No retained handle, content result or next-sweep observation.
        api = _windows_api()
        for path, previous in sorted(self.directories.items(), key=lambda item: (len(item[0].parts), str(item[0]))):
            handle = _windows_open(path)
            try:
                current = _windows_handle_state(handle)
                if not current["directory"] or any(current[key] != previous[key] for key in ("identity", "attributes", "final_name")):
                    raise ContractError("HV2-WINDOWS-PATH", "ancestor changed during detach read observation")
            finally:
                api.close(handle)

    def close(self) -> None:
        if self._executor is not None:
            self._executor.shutdown(wait=True, cancel_futures=True)
            self._executor = None
        self.closed = True
        self.directories.clear()
        self.prefixes.clear()
        self.lexical.clear()
        self.spellings.clear()
        self.accepted.clear()


@contextmanager
def _windows_detach_read_scope(root: Path, *, capture_serial: bool = False):
    if _windows_detach_read_observation.get() is not None:
        raise ContractError("HV2-WINDOWS-PATH", "nested detach read observation")
    observation = _WindowsDetachReadObservation(root)
    observation.capture_serial = capture_serial
    token = _windows_detach_read_observation.set(observation)
    try:
        yield
        _windows_detach_read_observation.reset(token)
        token = None
        observation.finish()
    finally:
        if token is not None:
            _windows_detach_read_observation.reset(token)
        observation.close()


def windows_path_observation(path: Path, *, mutation=False, allow_missing=False, _read_fds=None) -> dict:
    """Observe only this ancestor chain. No pinning or hostile-race guarantee."""
    if _read_fds is not None and (mutation or allow_missing or _read_fds):
        raise ContractError("HV2-WINDOWS-PATH", "invalid read-handle transfer")
    observation = None if mutation else _windows_detach_read_observation.get()
    absolute = observation.absolute(path) if observation is not None else _windows_absolute(path)
    api = _windows_api()
    if observation is not None and not observation.accepts(absolute):
        observation = None
    # The original sweep already shared these ancestor states. Reuse their
    # immutable chain representation too, never the requested leaf's state.
    spelling = observation.spelling(absolute) if observation is not None else None
    parent = spelling[1] if spelling is not None else absolute.parent
    prefix = (observation.prefixes.get(spelling[2])
              if observation is not None and parent != absolute else None)
    chain = list(prefix) if prefix is not None else []
    missing = False
    leaf = observation.directories[parent] if prefix is not None else None
    parts = ((absolute,) if prefix is not None else spelling[4] if spelling is not None
             else reversed((absolute, *absolute.parents)))
    for part in parts:
        if missing:
            continue
        # Only ancestors may be shared. The requested leaf is always freshly
        # opened, even if it was an ancestor of an earlier read in this sweep.
        shared = observation.directories.get(part) if observation is not None and part != absolute else None
        if shared is not None:
            chain.append((str(part), shared["identity"], shared["attributes"]))
            leaf = shared
            continue
        try:
            # The initial leaf observation can own the actual read handle.
            # Match CRT read sharing (no delete sharing), keep reparse refusal,
            # and retain every later independent path/handle observation.
            handle = (_windows_open(part, access=0x80000000, share=3)
                      if _read_fds is not None and part == absolute else _windows_open(part))
        except OSError as exc:
            if getattr(exc, "winerror", None) in {2, 3} and allow_missing and chain:
                # ERROR_PATH_NOT_FOUND can also mean an ancestor changed.
                # Re-open the nearest observed parent before calling this absence.
                parent = Path(chain[-1][0])
                previous = chain[-1]
                retry = _windows_open(parent)
                try:
                    observed = _windows_handle_state(retry, mutation=mutation)
                    if (not observed["directory"] or observed["identity"] != previous[1]
                            or observed["attributes"] != previous[2]):
                        raise ContractError("HV2-WINDOWS-PATH", "ancestor drift during absence observation")
                finally:
                    api.close(retry)
                missing = True
                continue
            raise api.failure("CreateFileW", "path-observation", getattr(exc, "winerror", None)) from exc
        try:
            state = _windows_handle_state(handle, mutation=mutation)
            final = state["final_name"]
            expected = (observation.spelling(part)[3] if observation is not None
                        else ("\\\\?\\" + str(part)).rstrip("\\").casefold())
            if final.rstrip("\\").casefold() != expected:
                raise ContractError("HV2-WINDOWS-PATH", "opened path is an alias or changed")
            if part != absolute and not state["directory"]:
                raise ContractError("HV2-WINDOWS-PATH", "non-directory ancestor")
            if mutation:
                drive_type = api.GetDriveTypeW(str(part.anchor))
                if drive_type in {0, 1, 4}:
                    raise ContractError("HV2-WINDOWS-FILESYSTEM", "remote or unknown volume")
            if observation is not None:
                observation.remember(part, state)
            chain.append((str(part), state["identity"], state["attributes"]))
            if observation is not None and state["directory"]:
                observation.prefixes[str(part)] = tuple(chain)
            leaf = state
            if _read_fds is not None and part == absolute:
                if state["directory"]:
                    raise ContractError("HV2-WINDOWS-PATH", "read input is a directory")
                import msvcrt
                # open_osfhandle transfers ownership only on success. The
                # context closes the descriptor; never also CloseHandle it.
                fd = msvcrt.open_osfhandle(handle, os.O_RDONLY | getattr(os, "O_BINARY", 0)
                                          | getattr(os, "O_NOINHERIT", 0))
                if fd < 0:
                    raise ContractError("HV2-WINDOWS-PATH", "read descriptor unavailable")
                handle = None
                _read_fds.append(fd)
        finally:
            if handle is not None:
                api.close(handle)
    if leaf is None or (missing and not leaf["directory"]):
        raise ContractError("HV2-WINDOWS-PATH", "missing or unsafe ancestor")
    return {"path": str(absolute), "exists": not missing, "chain": tuple(chain), **leaf}


@contextmanager
def _windows_open_read(path: Path):
    """Transfer one freshly verified leaf handle; no state survives the read."""
    descriptors = []
    try:
        native = windows_path_observation(path, _read_fds=descriptors)
        yield native, descriptors[0]
    finally:
        for fd in descriptors:
            os.close(fd)


def windows_preflight_files(paths) -> None:
    """Read-only union check; callers choose the whole operation before publication."""
    if sys.platform != "win32":
        return
    for path in dict.fromkeys(Path(p) for p in paths):
        state = windows_path_observation(path, mutation=True, allow_missing=True)
        if state["exists"] and not state["directory"] and state["attributes"] & 1:
            raise ContractError("HV2-WINDOWS-READONLY", f"existing file is read-only: {path.name}")


def windows_verify_handle(path: Path, handle, *, mutation=True, expected=None, content_unchanged=False) -> dict:
    current = windows_path_observation(path, mutation=mutation)
    opened = _windows_handle_state(handle, mutation=mutation)
    if (current["identity"] != opened["identity"] or current["attributes"] != opened["attributes"]
            or (expected is not None and current["chain"] != expected["chain"])):
        raise ContractError("HV2-WINDOWS-PATH", "path/handle identity or attributes changed")
    if content_unchanged and (expected is None or current["content_signature"] != opened["content_signature"]
                              or current["content_signature"] != expected["content_signature"]):
        raise ContractError("HV2-WINDOWS-PATH", "content changed during observation")
    return current


def windows_bounded_bytes(path: Path, limit: int, *, limit_code="HV2-JSON-LIMIT") -> bytes:
    """Bounded native binary observations; no hostile-race or ancestor-pinning guarantee."""
    import msvcrt
    native = windows_path_observation(path, allow_missing=True)
    if not native["exists"]:
        raise FileNotFoundError(os.fspath(path))
    if native["directory"] or native["links"] != 1:
        raise ContractError("HV2-WINDOWS-PATH", "read input is linked or special")
    if native["content_signature"][0] > limit:
        raise ContractError(limit_code, "read input exceeds byte limit; preserve file")
    fd = os.open(path, os.O_RDONLY | os.O_BINARY)
    try:
        handle = msvcrt.get_osfhandle(fd)
        opened = windows_verify_handle(path, handle, mutation=False, expected=native, content_unchanged=True)
        if opened["directory"] or opened["links"] != 1:
            raise ContractError("HV2-WINDOWS-PATH", "read input is linked or special")
        before = os.fstat(fd)
        if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1:
            raise ContractError("HV2-WINDOWS-PATH", "read input is linked or special")
        def read_once():
            data = bytearray()
            while len(data) <= limit:
                chunk = os.read(fd, min(65536, limit + 1 - len(data)))
                if not chunk:
                    break
                data.extend(chunk)
            if len(data) > limit:
                raise ContractError(limit_code, "read input exceeds byte limit; preserve file")
            return bytes(data)
        data = read_once()
        os.lseek(fd, 0, os.SEEK_SET)
        if data != read_once():
            raise ContractError("HV2-WINDOWS-PATH", "content changed during repeated read observation")
        after = os.fstat(fd)
        # Compare fd metadata with fd metadata. Windows path and CRT stat do
        # not agree on ctime or executable-extension mode bits.
        def stamp(value):
            return (value.st_dev, value.st_ino, value.st_mode, value.st_nlink,
                    value.st_size, value.st_mtime_ns, value.st_ctime_ns)
        if stamp(before) != stamp(after) or len(data) != after.st_size:
            raise ContractError("HV2-WINDOWS-PATH", "content changed during read observation")
        observed = windows_verify_handle(path, handle, mutation=False, expected=native, content_unchanged=True)
        if observed["directory"] or observed["links"] != 1:
            raise ContractError("HV2-WINDOWS-PATH", "read input became linked or special")
    finally:
        os.close(fd)
    final = windows_path_observation(path)
    if (final["chain"] != native["chain"] or final["content_signature"] != native["content_signature"]
            or final["directory"] or final["links"] != 1):
        raise ContractError("HV2-WINDOWS-PATH", "path or content changed during read observation")
    return data


def sync_existing_file(path: Path) -> dict[str, str]:
    """Reflush only when an admitted mutation/recovery requires this file."""
    if sys.platform != "win32":
        with path.open("rb") as handle:
            os.fsync(handle.fileno())
        return {"fsync": "pass"}
    windows_preflight_files([path])
    expected = windows_path_observation(path, mutation=True)
    if expected["directory"]:
        raise ContractError("HV2-WINDOWS-PATH", "required file flush received directory")
    api = _windows_api()
    try:
        handle = _windows_open(path, access=0x40000000)
    except OSError as exc:
        raise api.failure("CreateFileW", "required-file-reflush", exc.winerror) from exc
    try:
        windows_verify_handle(path, handle, expected=expected)
        if not api.FlushFileBuffers(handle):
            raise api.failure("FlushFileBuffers", "required-file-reflush")
        windows_verify_handle(path, handle, expected=expected)
        return {"fsync": "pass", "method": "FlushFileBuffers"}
    finally:
        api.close(handle)


def _windows_operation_error(api: str, phase: str, error: OSError, paths) -> ContractError:
    """Observe failure state without retry, cleanup, or assuming absence."""
    states = []
    for role, path in paths:
        try:
            value = windows_path_observation(path, allow_missing=True)
            state = "missing" if not value["exists"] else "directory" if value["directory"] else "file"
        except (OSError, ContractError):
            state = "unavailable"
        states.append(role + "=" + state)
    return ContractError("HV2-WINDOWS-IO", f"api={api}; result=failed; phase={phase}; "
                         f"winerror={getattr(error, 'winerror', None)}; errno={error.errno}; "
                         + "; ".join(states) + "; observed after failure; preserve actual prefix")


def rename_directory(source: Path, destination: Path) -> None:
    """One admitted directory publication; no retry or cleanup."""
    if sys.platform == "win32":
        before = windows_path_observation(source, mutation=True)
        target = windows_path_observation(destination, mutation=True, allow_missing=True)
        if not before["directory"] or target["exists"]:
            raise ContractError("HV2-WINDOWS-PATH", "directory publication requires a directory and absent destination")
        if before["volume"] != target["volume"]:
            raise ContractError("HV2-WINDOWS-FILESYSTEM", "cross-volume directory publication is unsupported")
    try:
        os.rename(source, destination)
    except OSError as exc:
        if sys.platform != "win32": raise
        raise _windows_operation_error("os.rename/MoveFileExW", "directory-publication", exc,
                                       (("staged", source), ("published", destination))) from exc
    if sys.platform == "win32":
        try:
            after = windows_path_observation(destination, mutation=True)
        except (OSError, ContractError) as exc:
            code = exc.code if isinstance(exc, ContractError) else "HV2-WINDOWS-PATH"
            detail = exc.message if isinstance(exc, ContractError) else f"winerror={getattr(exc, 'winerror', exc.errno)}"
            raise ContractError(code, "phase=post-directory-publication; publication occurred; preserve prefix; " + detail) from exc
        if after["identity"] != before["identity"] or after["attributes"] != before["attributes"]:
            raise ContractError("HV2-WINDOWS-PATH", "phase=post-directory-publication; identity changed; publication occurred; preserve prefix")


def remove_path(path: Path, *, directory: bool = False) -> None:
    """One removal after the caller's fresh preflight; no success-path reread."""
    try:
        path.rmdir() if directory else path.unlink()
    except OSError as exc:
        if sys.platform != "win32": raise
        operation = "directory-removal" if directory else "file-removal"
        api = "os.rmdir/RemoveDirectoryW" if directory else "os.unlink/DeleteFileW"
        raise _windows_operation_error(api, operation, exc, (("target", path),)) from exc


def replace_file(source: Path, destination: Path) -> None:
    """One same-volume replace; no retry or destructive fallback."""
    if sys.platform == "win32":
        windows_preflight_files([source, destination])
        before = windows_path_observation(source, mutation=True)
        target = windows_path_observation(destination, mutation=True, allow_missing=True)
        if before["volume"] != target["volume"]:
            raise ContractError("HV2-WINDOWS-FILESYSTEM", "cross-volume replace is unsupported")
    try:
        os.replace(source, destination)
    except OSError as exc:
        if sys.platform != "win32":
            raise
        raise _windows_api().failure("os.replace/MoveFileExW", "replace-publication", exc.winerror) from exc
    if sys.platform == "win32":
        try:
            after = windows_path_observation(destination, mutation=True)
        except (ContractError, OSError) as exc:
            code = exc.code if isinstance(exc, ContractError) else "HV2-WINDOWS-IO"
            detail = exc.message if isinstance(exc, ContractError) else f"winerror={getattr(exc, 'winerror', exc.errno)}"
            raise ContractError(code, "phase=post-publication; publication occurred; preserve prefix; " + detail) from exc
        if after["identity"] != before["identity"] or after["attributes"] != before["attributes"]:
            raise ContractError("HV2-WINDOWS-PATH", "phase=post-publication; post-replace identity changed; publication occurred; preserve prefix")


def _windows_finish_lock(handle, overlapped):
    """Cancel if pending and observe completion before releasing OVERLAPPED memory."""
    api = _windows_api()
    transferred = api.W.DWORD()
    cancel_error = None
    while True:
        try:
            if not api.CancelIoEx(handle, api.C.byref(overlapped)):
                error = api.C.get_last_error()
                if error != 1168:  # ERROR_NOT_FOUND: completion may have won the race.
                    cancel_error = api.failure("CancelIoEx", "lock-cancel", error)
            break
        except KeyboardInterrupt:
            continue
    while True:
        try:
            if api.GetOverlappedResult(handle, api.C.byref(overlapped), api.C.byref(transferred), False):
                # Also covers an interrupt immediately after the native acquisition.
                if not api.UnlockFileEx(handle, 0, 1, 0, api.C.byref(overlapped)):
                    error = api.C.get_last_error()
                    if error != 158:  # ERROR_NOT_LOCKED if the request failed synchronously.
                        raise api.failure("UnlockFileEx", "lock-cleanup", error)
                if cancel_error is not None:
                    raise cancel_error
                return
            error = api.C.get_last_error()
            if error == 995:  # ERROR_OPERATION_ABORTED is observed completion.
                if cancel_error is not None:
                    raise cancel_error
                return
            if error != 996:  # ERROR_IO_INCOMPLETE
                raise api.failure("GetOverlappedResult", "lock-cleanup", error)
            waited = api.WaitForSingleObject(overlapped.hEvent, 50)
            if waited not in {0, 258}:
                cancel_error = api.failure("WaitForSingleObject", "lock-cleanup")
                if not api.GetOverlappedResult(handle, api.C.byref(overlapped), api.C.byref(transferred), True):
                    error = api.C.get_last_error()
                    if error != 996:
                        raise cancel_error
                # If it completed successfully, the next iteration unlocks it.
        except KeyboardInterrupt:
            # A repeated interrupt must not free a live asynchronous request.
            continue


@contextmanager
def _windows_exclusive_lock(path: Path):
    api = _windows_api()
    windows_preflight_files([path])
    try:
        handle = _windows_open(path, access=0xC0000000, share=3, disposition=4, extra_flags=0x40000000)
    except OSError as exc:
        raise api.failure("CreateFileW", "lock-anchor", exc.winerror) from exc
    event = None
    submitted = False
    overlapped = api.Overlapped()
    try:
        state = windows_verify_handle(path, handle)
        if state["directory"] or state["links"] != 1 or state["attributes"] & 1:
            raise ContractError("HV2-LOCK-ANCHOR", "unsafe native lock anchor")
        flags = api.W.DWORD()
        if not api.GetHandleInformation(handle, api.C.byref(flags)):
            raise api.failure("GetHandleInformation", "lock-anchor")
        if flags.value & 1:
            raise ContractError("HV2-LOCK-ANCHOR", "inheritable lock handle")
        sync_directory(path.parent)
        event = api.CreateEventW(None, True, False, None)
        if not event:
            raise api.failure("CreateEventW", "lock-wait")
        overlapped.hEvent = event
        # Mark before the call: Python may receive SIGINT as the native call returns.
        submitted = True
        if not api.LockFileEx(handle, 2, 0, 1, 0, api.C.byref(overlapped)):
            error = api.C.get_last_error()
            if error != 997:
                raise api.failure("LockFileEx", "lock-acquire", error)
            transferred = api.W.DWORD()
            while True:
                waited = api.WaitForSingleObject(event, 50)
                if waited == 258:
                    continue  # Interruptible indefinite wait, not a lock timeout.
                if waited != 0:
                    raise api.failure("WaitForSingleObject", "lock-wait")
                if not api.GetOverlappedResult(handle, api.C.byref(overlapped), api.C.byref(transferred), False):
                    raise api.failure("GetOverlappedResult", "lock-acquire")
                break
        windows_verify_handle(path, handle, expected=state)
        yield
    finally:
        try:
            if submitted:
                _windows_finish_lock(handle, overlapped)
        finally:
            try:
                if event:
                    api.close(event)
            finally:
                api.close(handle)


def _sync_fd(fd: int, *, phase: str = "file-content") -> dict[str, str]:
    if sys.platform == "win32":
        import msvcrt
        api = _windows_api()
        handle = msvcrt.get_osfhandle(fd)
        state = _windows_handle_state(handle, mutation=True)
        if state["directory"] or state["attributes"] & 1:
            raise ContractError("HV2-WINDOWS-READONLY", "new/written file must be regular and read-only clear")
        if not api.FlushFileBuffers(handle):
            raise api.failure("FlushFileBuffers", phase)
        return {"fsync": "pass", "fullfsync": "not-applicable", "method": "FlushFileBuffers"}
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
    if sys.platform == "win32":
        expected = windows_path_observation(path, mutation=True)
        if not expected["directory"]:
            raise ContractError("HV2-WINDOWS-PATH", "directory sync requires directory")
        api = _windows_api()
        try:
            handle = _windows_open(path, access=0x40000000)
        except OSError as exc:
            raise api.failure("CreateFileW", "directory-sync", exc.winerror) from exc
        try:
            windows_verify_handle(path, handle, expected=expected)
            if api.FlushFileBuffers(handle):
                return "pass"
            error = api.C.get_last_error()
            if error in {1, 50}:
                return f"unavailable:winerror:{error}"
            raise api.failure("FlushFileBuffers", "directory-sync", error)
        finally:
            api.close(handle)
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
    if sys.platform == "win32":
        windows_path_observation(path, mutation=True, allow_missing=True)
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
        if sys.platform == "win32":
            windows_path_observation(directory, mutation=True)
        sync_directory(directory.parent)
        sync_directory(directory)


@contextmanager
def exclusive_file_lock(path: Path):
    """Hold the cooperating writer's stable, process-scoped anchor."""
    _ensure_parent(path)
    if sys.platform == "win32":
        with _windows_exclusive_lock(path):
            yield
        return
    flags = os.O_RDWR | os.O_CREAT
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        fd = os.open(path, flags, 0o600)
    except OSError as exc:
        raise ContractError("HV2-LOCK-ANCHOR", f"{path}:{exc.errno}") from exc
    try:
        opened = os.fstat(fd)
        try:
            anchored = path.lstat()
        except (FileNotFoundError, NotADirectoryError):
            raise ContractError("HV2-LOCK-ANCHOR", str(path)) from None
        if (
            path.is_symlink()
            or not stat.S_ISREG(opened.st_mode)
            or not stat.S_ISREG(anchored.st_mode)
            or (opened.st_dev, opened.st_ino) != (anchored.st_dev, anchored.st_ino)
        ):
            raise ContractError("HV2-LOCK-ANCHOR", str(path))
        sync_directory(path.parent)
        fcntl.flock(fd, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(fd, fcntl.LOCK_UN)
    finally:
        os.close(fd)


def write_new_bytes(path: Path, data: bytes) -> dict[str, str]:
    _ensure_parent(path)
    if path.exists() or path.is_symlink():
        raise ContractError("HV2-IMMUTABLE-EXISTS", str(path))
    try:
        with path.open("xb") as handle:
            if sys.platform == "win32":
                import msvcrt
                windows_verify_handle(path, msvcrt.get_osfhandle(handle.fileno()))
            handle.write(data)
            handle.flush()
            result = _sync_fd(handle.fileno(), phase="created-file-content")
    except FileExistsError as exc:
        raise ContractError("HV2-IMMUTABLE-EXISTS", str(path)) from exc
    result["directory_fsync"] = sync_directory(path.parent)
    return result


def write_new_json(path: Path, value: Any) -> dict[str, str]:
    return write_new_bytes(path, canonical_json_bytes(value))


def replace_bytes(path: Path, data: bytes) -> dict[str, str]:
    windows_preflight_files([path])
    _ensure_parent(path)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.hv2-tmp-", dir=path.parent)
    tmp = Path(tmp_name)
    complete = False
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            result = _sync_fd(handle.fileno(), phase="file-content-before-publication")
        replace_file(tmp, path)
        result["directory_fsync"] = sync_directory(path.parent)
        complete = True
        return result
    finally:
        if tmp.exists() and (sys.platform != "win32" or complete):
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
