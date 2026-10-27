"""Source-only U2 effect, Core and recovery contracts; no model transport."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import selectors
import signal
import subprocess
import time
import unicodedata
import fcntl
from .execution_os import execution_os
import stat
import sys
import re


class HostRefusal(RuntimeError):
    """A required host boundary is unavailable or inconsistent."""


def digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def canonical(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode()


def durable_json(path: Path, value: object) -> None:
    # Run directories are exclusive; evidence is never silently overwritten.
    with path.open("xb") as stream:
        stream.write(canonical(value))
        stream.flush()
        os.fsync(stream.fileno())


def wire_bytes(value):
    """Rust serde_json::Value hash format, without the JSONL newline."""
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def require(condition, reason):
    if not condition:
        raise HostRefusal(reason)


def checked_open(path, flags=os.O_RDONLY):
    path = Path(path)
    require(path.is_absolute() and path.resolve(strict=True) == path, "noncanonical control file")
    fd = os.open(path, flags | os.O_NOFOLLOW | os.O_CLOEXEC)
    info = os.fstat(fd)
    if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or stat.S_IMODE(info.st_mode) & 0o077:
        os.close(fd)
        raise HostRefusal("aliased or nonprivate control file")
    return fd


def control_read(path, limit=16 * 1024 * 1024):
    with os.fdopen(checked_open(path), "rb") as stream:
        raw = stream.read(limit + 1)
        require(len(raw) <= limit, "control file too large")
        return raw


def durable_private(path, value):
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC, 0o600)
    with os.fdopen(fd, "wb") as stream:
        stream.write(canonical(value))
        stream.flush()
        os.fsync(stream.fileno())
    parent = os.open(Path(path).parent, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        os.fsync(parent)
    finally:
        os.close(parent)


def publish_acceptance_request(run, value):
    """Publish one complete request; retain collisions/partial writes for recovery."""
    import ctypes
    run = Path(run)
    require(run.is_absolute() and run.resolve(strict=True) == run, "noncanonical acceptance directory")
    parent = os.open(run, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC)
    partial, final = "accept-request.json.partial", "accept-request.json"
    try:
        for name in (partial, final):
            try:
                os.stat(name, dir_fd=parent, follow_symlinks=False)
            except FileNotFoundError:
                continue
            raise HostRefusal("acceptance publication already exists")
        fd = os.open(partial, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC,
                     0o600, dir_fd=parent)
        with os.fdopen(fd, "wb") as stream:
            stream.write(canonical(value))
            stream.flush()
            os.fsync(stream.fileno())
            written = os.fstat(stream.fileno())
        current = os.stat(partial, dir_fd=parent, follow_symlinks=False)
        require((current.st_dev, current.st_ino, current.st_nlink) ==
                (written.st_dev, written.st_ino, 1) and stat.S_ISREG(current.st_mode) and
                stat.S_IMODE(current.st_mode) == 0o600, "acceptance partial replaced")
        # macOS RENAME_EXCL: the final name must not replace another request.
        native = ctypes.CDLL(None, use_errno=True)
        rename = native.renameatx_np
        rename.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_uint]
        rename.restype = ctypes.c_int
        if rename(parent, os.fsencode(partial), parent, os.fsencode(final), 0x4) != 0:
            raise OSError(ctypes.get_errno(), "exclusive acceptance publication failed")
        published = os.stat(final, dir_fd=parent, follow_symlinks=False)
        require((published.st_dev, published.st_ino, published.st_nlink) ==
                (written.st_dev, written.st_ino, 1) and stat.S_ISREG(published.st_mode) and
                stat.S_IMODE(published.st_mode) == 0o600, "acceptance publication replaced")
        os.fsync(parent)
    finally:
        os.close(parent)


def continuous_ns():
    """macOS continuous clock includes sleep; epoch v1/v2 retain their original clock."""
    import ctypes
    require(sys.platform == "darwin", "qualified continuous clock is macOS-only")
    class Timebase(ctypes.Structure):
        _fields_ = [("numer", ctypes.c_uint32), ("denom", ctypes.c_uint32)]
    native = ctypes.CDLL("/usr/lib/libSystem.B.dylib")
    native.mach_continuous_time.restype = ctypes.c_uint64
    native.mach_timebase_info.argtypes = [ctypes.POINTER(Timebase)]
    info = Timebase()
    require(native.mach_timebase_info(ctypes.byref(info)) == 0 and info.denom != 0, "continuous clock unavailable")
    return native.mach_continuous_time() * info.numer // info.denom


def bounded_flock(fd, operation, deadline_ms):
    """Serialize normal contention without hiding corruption or removing another lock."""
    deadline = min(time.monotonic() + 5, time.monotonic() + max(0, deadline_ms - time.time_ns() // 1_000_000) / 1000)
    while True:
        try:
            fcntl.flock(fd, operation | fcntl.LOCK_NB)
            return
        except BlockingIOError:
            require(time.monotonic() < deadline, "journal lock deadline")
            time.sleep(min(0.01, max(0, deadline - time.monotonic())))


class ControllerLock:
    def __init__(self, path):
        self.fd = checked_open(path, os.O_RDWR)
        try:
            fcntl.flock(self.fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BaseException:
            os.close(self.fd)
            raise HostRefusal("another controller owns this execution")

    def close(self):
        if self.fd is not None:
            fcntl.flock(self.fd, fcntl.LOCK_UN)
            os.close(self.fd)
            self.fd = None


ENV_NAMES = frozenset({"HOME", "USER", "LOGNAME", "LANG", "LC_ALL", "LC_CTYPE", "__CF_USER_TEXT_ENCODING"})


def closed_environment(extra=None):
    result = {key: value for key, value in os.environ.items() if key in ENV_NAMES}
    result.update({"PATH": "/usr/bin:/bin", "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": "/dev/null",
                   "GIT_CONFIG_SYSTEM": "/dev/null", "GIT_TERMINAL_PROMPT": "0", "PYTHONDONTWRITEBYTECODE": "1"})
    if extra:
        require(set(extra) <= {"TMPDIR", "HOME", "LANG", "XDG_CONFIG_HOME"}, "unexpected child environment")
        result.update(extra)
    return result


def end_process(process):
    """A reaped parent alone is not proof that its process group disappeared."""
    for sig in (signal.SIGTERM, signal.SIGKILL):
        try:
            os.killpg(process.pid, 0)
        except ProcessLookupError:
            break
        os.killpg(process.pid, sig)
        limit = time.monotonic() + 10
        while time.monotonic() < limit:
            process.poll()
            try:
                os.killpg(process.pid, 0)
            except ProcessLookupError:
                break
            except PermissionError:
                # A signal just sent may race with group teardown. Keep the
                # bounded absence check; EPERM itself never means gone.
                pass
            time.sleep(0.02)
    process.poll()
    try:
        os.killpg(process.pid, 0)
        absent = False
    except ProcessLookupError:
        absent = True
    require(absent and process.returncode is not None, "child group termination unavailable")
    return {"exit_code": process.returncode, "process_group_absent": True}


def reject_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate RPC/JSON key")
        result[key] = value
    return result


def core_bytes(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n").encode()


def safe_text(text, allowed_identifiers=()):
    require(isinstance(text, str) and "\x00" not in text, "nontext or NUL document")
    # These are exposure guards, not a proof of factual correctness. Approved
    # source identifiers are enumerated in the Owner's transmission packet.
    residue = text
    for literal in sorted(allowed_identifiers, key=len, reverse=True):
        require(isinstance(literal, str) and len(literal) >= 3, "invalid approved identifier")
        residue = residue.replace(literal, "[approved]")
    require(not re.search(r"(?i)(?:sk-[A-Za-z0-9_-]{16,}|-----BEGIN [A-Z ]*PRIVATE KEY-----|Bearer\s+[A-Za-z0-9._-]{12,}|(?:access_token|refresh_token|api_key)\s*[=:]\s*[^\s,}]{8,})", text), "credential-like content")
    require(not re.search(r"(?:/Users/[^\s<>\"']+|/home/[^\s<>\"']+|[A-Za-z]:\\[^\s<>\"']+|[\w.+-]+@[\w.-]+\.[A-Za-z]{2,})", residue), "unapproved document identifier")


class InstalledCore:
    def __init__(self, spec, run, deadline):
        self.spec, self.run, self.deadline, self.invocations = spec, Path(run), deadline, 0
        require(set(spec) == {"python", "python_sha256", "launcher", "launcher_sha256", "cwd", "files", "env"}, "installed CLI spec")
        self.validate()

    def validate(self):
        for name in ("python", "launcher"):
            path = Path(self.spec[name])
            require(path.resolve(strict=True) == path and digest(path.read_bytes()) == self.spec[name + "_sha256"], "installed executable drift")
        for name, expected in self.spec["files"].items():
            path = Path(name)
            info = path.lstat()
            require(path.resolve(strict=True) == path and stat.S_ISREG(info.st_mode) and info.st_nlink == 1 and
                    stat.S_IMODE(info.st_mode) == expected["mode"] and digest(path.read_bytes()) == expected["sha256"], "installed binding/inventory drift")

    def invoke(self, action, value, token=None):
        require(action in ("prepare", "apply"), "unregistered Core route")
        self.validate()
        argv = [self.spec["python"], "-I", "-B", self.spec["launcher"], "work", action, "--input", "-"]
        if action == "apply":
            require(isinstance(token, str) and len(token) == 16, "missing exact token")
            argv += ["--confirm", token]
        self.invocations += 1
        number = self.invocations
        request = core_bytes(value)
        durable_private(self.run / f"core-{number:03d}-input.json", value)
        limit = min(300, self.deadline - time.monotonic() - 20)
        require(limit > 0, "Core deadline")
        process, out, err, interrupted, output_complete = None, b"", b"", False, False
        cleanup = {"exit_code": None, "process_group_absent": False}
        try:
            process = subprocess.Popen(argv, cwd=self.spec["cwd"], env=closed_environment(self.spec["env"]),
                stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
            durable_private(self.run / f"core-{number:03d}-process.json", {"pid": process.pid, "action": action, "input_sha256": digest(request)})
            try:
                out, err = process.communicate(request, timeout=limit)
                output_complete = True
            except subprocess.TimeoutExpired as error:
                out, err = error.output or b"", error.stderr or b""
                interrupted = True
        finally:
            try:
                if process is not None:
                    cleanup = end_process(process)
            finally:
                try:
                    durable_private(self.run / f"core-{number:03d}-metadata.json", {**cleanup, "interrupted": interrupted,
                        "stdout_bytes": len(out), "stdout_sha256": digest(out), "stderr_bytes": len(err), "stderr_sha256": digest(err),
                        "output_complete": output_complete and cleanup["process_group_absent"]})
                finally:
                    if process is not None:
                        for name in ("stdin", "stdout", "stderr"):
                            getattr(process, name).close()
        if interrupted:
            raise HostRefusal("Core operation interrupted; exact human recovery required")
        require(process.returncode == 0 and not err and len(out) <= 8_388_608, "installed Core refusal/unavailable")
        self.validate()
        result = json.loads(out, object_pairs_hook=reject_duplicate_keys)
        require(isinstance(result, dict), "Core result shape")
        return result


class Acceptance:
    """The model supplies only a handle; the original sealed ticket stays private."""
    def __init__(self, identity, packet_bytes, expected_digest, result_identity, handle, core, budget):
        require(digest(packet_bytes) == expected_digest, "ticket packet replacement")
        packet = json.loads(packet_bytes, object_pairs_hook=reject_duplicate_keys)
        require(set(packet) == {"ticket", "confirm_token"}, "ticket packet fields")
        ticket = packet["ticket"]
        require(packet["confirm_token"] == digest(core_bytes(ticket))[:16], "ticket token drift")
        require(ticket["authority_home_id"] == identity["home"] and ticket["object"] ==
                {"authority_home_id": identity["home"], "kind": "work", "id": identity["work"]} and
                ticket["action"] == identity["action"] == "accept" and ticket["actor"] == identity["actor"] and
                ticket["execution_mode"] == "isolated-worktree" and result_identity == identity["result_identity"], "home/work/action/actor/result drift")
        require(isinstance(handle, str) and len(handle) >= 32, "invalid acceptance handle")
        self.identity, self.packet, self.packet_digest = json.loads(json.dumps(identity)), packet, expected_digest
        self.packet_bytes, self.result_identity, self.handle = packet_bytes, result_identity, handle
        self.core, self.budget, self.used = core, budget, False

    def apply(self, args, admission, observed_result, no_writers):
        require(isinstance(args, dict) and args == {"handle": self.handle}, "unknown acceptance handle")
        require(not self.used and admission.sealed and not admission.stopped and admission.call is not None and no_writers, "acceptance phase/lifetime")
        require(admission.identity == self.identity and observed_result == self.result_identity, "acceptance identity/result drift")
        require(digest(self.packet_bytes) == self.packet_digest and json.loads(self.packet_bytes) == self.packet, "ticket bytes drift")
        ticket = self.packet["ticket"]
        request = {"work_id": ticket["object"]["id"], "action": ticket["action"], "actor": ticket["actor"],
                   "reason": ticket["reason"], "request_id": ticket["request_id"], "observed_at": ticket["observed_at"],
                   "revision_ref": ticket["target_revision_ref"], "supersedes": ticket["supersedes_decision_ref"]}
        fresh = self.core.invoke("prepare", request)
        require(core_bytes(fresh) == core_bytes(self.packet), "grant/selection/result changed before apply")
        self.used = True  # uncertainty or a failed apply never makes the ticket reusable
        self.budget.reserve("authority-apply", {"ticket_sha256": digest(core_bytes(ticket)), **admission.authority_subject()}, admission.phase, admission.start)
        result = self.core.invoke("apply", ticket, self.packet["confirm_token"])
        return {"accepted": True, "ticket_sha256": digest(core_bytes(ticket)), "result_sha256": digest(core_bytes(result))}


class RecoveryGate:
    """Trusted Driver relays an exact Owner decision; worker arguments cannot create it."""
    def __init__(self, packet, packet_sha256, owner_decision, budget):
        require(digest(core_bytes(packet)) == packet_sha256, "recovery packet drift")
        require(set(owner_decision) == {"packet_sha256", "ticket_sha256s", "actor", "decision", "owner_message_id"} and
                owner_decision["packet_sha256"] == packet_sha256 and owner_decision["decision"] == "replay-once" and
                isinstance(owner_decision["owner_message_id"], str) and bool(owner_decision["owner_message_id"]), "exact Owner recovery decision missing")
        cases = packet["cases"]
        require(set(cases) == {"S1", "S2", "S3", "S4", "S5"}, "recovery case coverage")
        digests = [cases[key]["ticket_sha256"] for key in sorted(cases)]
        require(owner_decision["ticket_sha256s"] == digests and all(cases[key]["actor"] == owner_decision["actor"] for key in cases), "recovery actor/ticket drift")
        require(all(case["process_group_absent"] and case["decision_observed"] for case in cases.values()), "recovery decision/termination unavailable")
        require(all(cases[key]["pending_observed"] and not cases[key]["current_published"] for key in ("S1", "S2", "S3", "S4")), "recovery pending state unavailable")
        final = cases["S5"]
        require(not final["pending_observed"] and final["current_published"] and
                final["actual_current"] == final["expected_current"], "historical recovery publication unavailable")
        self.packet, self.owner, self.budget, self.used = packet, owner_decision, budget, set()

    def replay(self, case_id, core, observation):
        require(case_id in self.packet["cases"] and case_id not in self.used, "recovery replay reuse/unknown")
        case = self.packet["cases"][case_id]
        require(observation == case["before_replay"] and case["actor"] == case["packet"]["ticket"]["actor"] and
                digest(core_bytes(case["packet"]["ticket"])) == case["ticket_sha256"], "recovery original decision changed")
        self.used.add(case_id)
        self.budget.reserve("recovery-apply", {"ticket_sha256": case["ticket_sha256"], "case": case_id,
                                              "owner_message_id": self.owner["owner_message_id"]})
        return core.invoke("apply", case["packet"]["ticket"], case["packet"]["confirm_token"])


def document_stat_key(info):
    # A read may update atime; content/identity metadata must remain stable.
    return (info.st_dev, info.st_ino, info.st_mode, info.st_nlink, info.st_size,
            info.st_mtime_ns, info.st_ctime_ns)


def file_record(path, *, limit=65_536, absent=False):
    path = Path(path)
    require(limit in (65_536, 131_072), "document size contract")
    if absent:
        require(path.is_absolute() and path.parent.resolve(strict=True) == path.parent and
                str(path) == os.path.normpath(str(path)), "absent document path alias")
        require(not os.path.lexists(path), "expected document absence drift")
        return {"path": str(path), "identity": None, "mode": 0o644, "sha256": None}, b""
    require(path.is_absolute() and path.resolve(strict=True) == path, "document path alias")
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC)
    with os.fdopen(fd, "rb") as stream:
        before = os.fstat(stream.fileno())
        require(stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and before.st_size <= limit, "document alias/size")
        raw = stream.read(limit + 1)
        require(document_stat_key(os.fstat(stream.fileno())) == document_stat_key(before) and len(raw) <= limit, "document changed while reading")
        raw.decode("utf-8")
    return {"path": str(path), "identity": [before.st_dev, before.st_ino], "mode": stat.S_IMODE(before.st_mode), "sha256": digest(raw)}, raw


def document_record(expected):
    observed, raw = file_record(expected["path"], limit=131_072 if "view" in expected else 65_536,
                                absent="view" in expected and expected["identity"] is None)
    if "view" in expected:
        observed["view"] = expected["view"]
        document_view(observed, raw)
    return observed, raw


def document_view(entry, raw):
    view = entry.get("view", {"kind": "full"})
    if view == {"kind": "full"}:
        return raw
    require(set(view) == {"kind", "ranges"} and view["kind"] in ("read-ranges", "replace-range") and
            isinstance(view["ranges"], list) and 1 <= len(view["ranges"]) <= 4 and
            (view["kind"] != "replace-range" or len(view["ranges"]) == 1), "document view contract")
    previous, parts = 0, []
    for pair in view["ranges"]:
        require(isinstance(pair, list) and len(pair) == 2 and all(type(x) is int for x in pair), "document range")
        begin, end = pair
        require(previous <= begin <= end <= len(raw) and (begin < end or view["kind"] == "replace-range"), "document range bounds")
        part = raw[begin:end]; part.decode("utf-8")
        parts.append(part); previous = end
    return b"\n\n<!-- approved excerpt boundary -->\n\n".join(parts)


def document_item(key, entry, raw):
    visible = document_view(entry, raw)
    result = {"file_id": key, "sha256": digest(visible), "content": visible.decode("utf-8")}
    if "view" in entry:
        result.update(file_sha256=entry["sha256"], state="absent" if entry["identity"] is None else "present", view=entry["view"])
    return result


def initial_view_contracts(files):
    contracts = {}
    for key, entry in files.items():
        _, raw = document_record(entry)
        contract = {"view": json.loads(json.dumps(entry["view"])), "initial_state": "absent" if entry["identity"] is None else "present"}
        if entry["view"]["kind"] == "replace-range":
            begin, end = entry["view"]["ranges"][0]
            contract.update(prefix_sha256=digest(raw[:begin]), suffix_sha256=digest(raw[end:]))
        contracts[key] = contract
    return contracts


def parent_identities(paths):
    parents = {}
    for name in paths:
        path = Path(name)
        for parent in path.parents:
            require(parent.resolve(strict=True) == parent, "ancestor alias")
            info = parent.lstat()
            require(stat.S_ISDIR(info.st_mode), "non-directory ancestor")
            parents[str(parent)] = [info.st_dev, info.st_ino]
    return parents


def sb_literal(path):
    require(isinstance(path, str) and Path(path).is_absolute() and "\n" not in path and "\x00" not in path, "profile literal")
    return "(literal " + json.dumps(path, ensure_ascii=False) + ")"


def pack_reads(files, maximum=8, origin=None):
    packs, current, result = [], [], {"files": []}
    for key in sorted(files):
        entry, raw = document_record(files[key])
        require(entry == files[key], "read pack drift")
        item = document_item(key, entry, raw)
        if origin is not None:
            item["origin"] = {"kind": "approved-document", "source_sha256": origin["sources"][key], "approval": origin["approval"]}
        require(len(wire_bytes({"files": [item]})) <= 64_000, "single read payload does not fit")
        if current and (len(current) == 8 or len(wire_bytes({"files": result["files"] + [item]})) > 64_000):
            packs.append(current)
            current, result = [], {"files": []}
        current.append(key)
        result["files"].append(item)
    if current:
        packs.append(current)
    require(len(packs) <= maximum, "complete read scope exceeds eight turns")
    return packs


class DocumentController:
    def __init__(self, spec, run, budget, phase, start, deadline):
        required = {"files", "outputs", "claims", "approved_external_links", "allowed_identifiers", "python", "python_sha256",
                    "worker", "worker_sha256", "parser", "parser_sha256", "profile_template", "profile_template_sha256", "scratch", "writer_attestation", "source_digests"}
        self.contract_version = spec.get("contract_version", 1)
        require(self.contract_version in (1, 2), "document contract version")
        if self.contract_version == 2:
            required |= {"contract_version", "link_metadata", "view_contracts"}
        require(set(spec) == required and spec["writer_attestation"] is True, "document scope/writer declaration unavailable")
        self.spec = json.loads(json.dumps(spec))
        self.files = json.loads(json.dumps(spec["files"]))
        self.run, self.budget, self.phase, self.start, self.deadline = Path(run), budget, phase, start, deadline
        self.sequence, self.active, self.sealed = 0, None, False
        self.read_ids, self.written_ids, self.verifiers = set(), set(), {}
        self.last_failure, self.correction_open = None, False
        require(set(spec["outputs"]) <= set(self.files) and len(set(spec["outputs"])) == len(spec["outputs"]), "document output scope")
        if phase == "h10":
            require(len(spec["outputs"]) == 5, "actual work requires exactly five documents")
        for name in ("python", "worker", "parser", "profile_template"):
            path = Path(spec[name])
            require(path.resolve(strict=True) == path and digest(path.read_bytes()) == spec[name + "_sha256"], "worker dependency drift")
        require(set(spec["source_digests"]) == set(self.files) and all(
            (isinstance(v, str) and re.fullmatch(r"[a-f0-9]{64}", v)) or
            (self.contract_version == 2 and v is None and key in spec["outputs"] and spec["view_contracts"].get(key, {}).get("initial_state") == "absent")
            for key, v in spec["source_digests"].items()), "original document identity missing")
        for key, entry in self.files.items():
            require(set(entry) == {"path", "identity", "mode", "sha256"} | ({"view"} if self.contract_version == 2 else set()), "document entry contract")
            if entry.get("view", {}).get("kind") == "replace-range":
                require(key in spec["outputs"], "editable view must be output")
            if key in spec["outputs"]:
                require(entry.get("view", {"kind": "full"})["kind"] in ("full", "replace-range"), "readonly output view")
        require(len({e["path"] for e in self.files.values()}) == len(self.files), "duplicate document path")
        require(not (set(spec.get("link_metadata", {})) & {e["path"] for e in self.files.values()}), "metadata/document overlap")
        self.check_files()
        for value in self.files.values():
            _, raw = document_record(value)
            safe_text(document_view(value, raw).decode(), spec["allowed_identifiers"])
        originals = self.run / "original-outputs"
        originals.mkdir(mode=0o700, exist_ok=False)
        for key in spec["outputs"]:
            _, raw = document_record(self.files[key])
            if self.files[key]["identity"] is None:
                durable_private(originals / (key + ".absence.json"), self.files[key])
                continue
            with (originals / (key + ".utf8")).open("xb") as stream:
                os.fchmod(stream.fileno(), 0o600); stream.write(raw); stream.flush(); os.fsync(stream.fileno())
            require((originals / (key + ".utf8")).read_bytes() == raw, "original output preservation failed")
        self.read_packs = pack_reads(self.files, origin={"sources": spec["source_digests"], "approval": budget.anchor["approval"]})
        scope = {"paths": {key: value["path"] for key, value in self.files.items()}, "outputs": spec["outputs"]}
        oracle = {key: spec[key] for key in ("claims", "approved_external_links", "parser_sha256")}
        if self.contract_version == 2:
            scope["views"] = spec["view_contracts"]
            oracle["link_metadata"] = spec["link_metadata"]
        self.scope_sha256 = digest(wire_bytes(scope))
        self.oracle_sha256 = digest(wire_bytes(oracle))

    def check_files(self):
        if self.spec.get("contract_version") == 2:
            require(set(self.spec["view_contracts"]) == set(self.files), "initial view coverage")
        for key, expected in self.files.items():
            observed, raw = document_record(expected)
            require(observed == expected, "document bytes/mode/identity drift")
            if self.spec.get("contract_version") == 2:
                contract = self.spec["view_contracts"][key]
                require(contract.get("initial_state") in ("absent", "present") and
                        (contract["initial_state"] == "absent") == (self.spec["source_digests"][key] is None) and
                        (expected["identity"] is not None or contract["initial_state"] == "absent"), "initial presence contract drift")
                if expected["view"]["kind"] == "replace-range":
                    require(set(contract) == {"view", "initial_state", "prefix_sha256", "suffix_sha256"} and
                            contract["view"]["kind"] == "replace-range" and len(contract["view"]["ranges"]) == 1,
                            "initial editable view contract")
                    begin, end = expected["view"]["ranges"][0]
                    initial_begin, initial_end = contract["view"]["ranges"][0]
                    require(type(initial_begin) is int and type(initial_end) is int and 0 <= initial_begin <= initial_end and
                            begin == initial_begin and digest(raw[:begin]) == contract["prefix_sha256"] and
                            digest(raw[end:]) == contract["suffix_sha256"], "immutable outside-range bytes drift")
                else:
                    require(contract == {"view": expected["view"], "initial_state": contract["initial_state"]}, "immutable read view drift")
                if key not in self.spec["outputs"]:
                    require(expected["sha256"] == self.spec["source_digests"][key], "reference source bytes drift")
        for name, expected in self.spec.get("link_metadata", {}).items():
            path = Path(name)
            require(path.is_absolute() and path.resolve(strict=True) == path, "metadata path alias")
            info = path.lstat()
            require(stat.S_ISREG(info.st_mode) and info.st_nlink == 1 and
                    [info.st_dev, info.st_ino] == expected["identity"] and stat.S_IMODE(info.st_mode) == expected["mode"] and
                    info.st_size == expected["size"] and info.st_mtime_ns == expected["mtime_ns"], "link metadata drift")
            if expected["sha256"] is not None:
                record, _ = file_record(path, limit=131_072)
                require(record["sha256"] == expected["sha256"], "link anchor content drift")

    def result_identity(self):
        self.check_files()
        return digest(wire_bytes({key: self.files[key] for key in self.spec["outputs"]}))

    def dispatch(self, tool, args):
        require(not self.sealed and self.active is None, "worker unavailable after seal/concurrent writer")
        require(tool in ("u2_read_file", "u2_write_file", "u2_verify"), "document tool scope")
        self.check_files()
        require(isinstance(args, dict), "tool arguments")
        if tool == "u2_read_file":
            require(set(args) == {"file_ids"} and isinstance(args["file_ids"], list) and
                    all(isinstance(k, str) for k in args["file_ids"]) and 1 <= len(args["file_ids"]) <= 8 and
                    len(set(args["file_ids"])) == len(args["file_ids"]) and set(args["file_ids"]) <= set(self.files), "read scope")
        elif tool == "u2_write_file":
            require(set(args) == {"file_id", "expected_sha256", "content"} and args["file_id"] in self.spec["outputs"] and
                    args["expected_sha256"] == self.files[args["file_id"]]["sha256"] and isinstance(args["content"], str) and
                    len(args["content"].encode()) <= 65_536, "write scope/CAS")
            safe_text(args["content"], self.spec["allowed_identifiers"])
            if self.last_failure is not None and not self.correction_open:
                self.budget.reserve("correction", {"oracle_sha256": self.oracle_sha256, "failure": self.last_failure, **({"class":"content"} if self.budget.anchor["version"] >= 4 else {})}, self.phase, self.start)
                self.correction_open = True
        else:
            require(set(args) == {"verifier_id"} and args["verifier_id"] in ("DOC-LINKS", "DOC-GFM", "DOC-CLAIMS"), "verifier scope")
        prior_write = None
        if tool == "u2_write_file":
            entry = self.files[args["file_id"]]
            _, prior_write = document_record(entry)
        self.sequence += 1
        slot = self.run / f"worker-{self.sequence:03d}"
        slot.mkdir(mode=0o700, exist_ok=False)
        scratch = Path(self.spec["scratch"]) / f"worker-{self.sequence:03d}"
        scratch.mkdir(mode=0o700, exist_ok=False)
        swap = {args["file_id"]: str(scratch / (args["file_id"] + ".swap"))} if tool == "u2_write_file" else {}
        require(all(not Path(name).exists() and not Path(name).is_symlink() for name in swap.values()), "unexpected swap")
        worker_spec = {"version": self.contract_version, "files": self.files, "parents": parent_identities([entry["path"] for entry in self.files.values()] + list(swap.values()) + list(self.spec.get("link_metadata", {}))),
            "outputs": self.spec["outputs"], "swap": swap, "parser": self.spec["parser"], "parser_sha256": self.spec["parser_sha256"],
            "claims": self.spec["claims"], "approved_external_links": self.spec["approved_external_links"]}
        if self.contract_version == 2:
            worker_spec["link_metadata"] = self.spec["link_metadata"]
        spec_path = slot / "spec.json"
        durable_private(spec_path, worker_spec)
        request = {"tool": tool, "arguments": args}
        # Only a write request contains new bytes; preserve it before any effect.
        durable_private(slot / "request.json", request)
        template = Path(self.spec["profile_template"]).read_text()
        require(digest(template.encode()) == self.spec["profile_template_sha256"], "worker profile drift")
        metadata_paths = list(self.spec.get("link_metadata", {}))
        reads = [value["path"] for value in self.files.values()] + [p for p, e in self.spec.get("link_metadata", {}).items() if e["sha256"] is not None]
        dependencies = [self.spec[k] for k in ("python", "worker", "parser")] + [str(spec_path)]
        ancestors = set(parent_identities(reads + dependencies + list(swap.values()) + metadata_paths))
        ancestors.update(metadata_paths)
        # S0 already permits these fixed dependency reads and their exact
        # ancestor metadata. Include them when materializing the placeholder.
        common_inputs = ["/System/Library", "/usr/lib", "/private/var/db/dyld", "/private/var/db/timezone",
                         "/dev/null", "/dev/random", "/dev/urandom",
                         "/opt/homebrew/opt/gettext/lib/libintl.8.dylib", "/opt/homebrew/Cellar/gettext/1.0/lib/libintl.8.dylib"]
        for name in common_inputs:
            ancestors.update(str(parent) for parent in Path(name).parents)
        ancestors.add(str(scratch))
        metadata = "(allow file-read-metadata " + " ".join(sb_literal(name) for name in sorted(ancestors)) + ")"
        read_rules = "(allow file-read* " + " ".join(sb_literal(name) for name in reads) + ")"
        writes = ""
        if swap:
            target, swap_path = self.files[args["file_id"]]["path"], next(iter(swap.values()))
            require(Path(target).parent.stat().st_dev == Path(swap_path).parent.stat().st_dev, "swap device differs")
            parents = {str(Path(target).parent), str(Path(swap_path).parent)}
            writes = "(allow file-write* " + sb_literal(target) + " " + sb_literal(swap_path) + ")\n" + \
                "(allow file-read-data file-write-data " + " ".join(sb_literal(name) for name in sorted(parents)) + ")"
            template += "(allow file-read-metadata " + sb_literal(swap_path) + ")\n"
        template = template.replace("; @@ANCESTOR_METADATA_LITERALS@@", metadata).replace("; @@APPROVED_INPUT_READ_LITERALS@@", read_rules)
        marker = "; @@EXACT_WRITE_TARGET_AND_SWAP@@ only for write operation, omitted for read and all verifiers."
        require(marker in template, "worker profile marker drift")
        template = template.replace(marker, writes)
        profile = slot / "worker.sb"
        fd = os.open(profile, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "w") as stream:
            stream.write(template); stream.flush(); os.fsync(stream.fileno())
        params = {"BIN": self.spec["python"], "SPEC": str(spec_path), "PARSER": self.spec["parser"], "WORKER": self.spec["worker"],
                  "PYROOT": str(Path(self.spec["python"]).parent.parent)}
        operation = {"u2_read_file": "read", "u2_write_file": "write"}.get(tool, args.get("verifier_id"))
        argv = ["/usr/bin/sandbox-exec"]
        for key, value in params.items():
            argv += ["-D", key + "=" + value]
        argv += ["-f", str(profile), self.spec["python"], "-I", "-S", "-B", self.spec["worker"], "--spec", str(spec_path), "--operation", operation]
        timeout = self.budget.check_worker_result({"tool": tool, "result_sha256": "0" * 64,
            "result_identity": "0" * 64, "oracle_sha256": self.oracle_sha256}, self.phase, self.start,
            min(300, self.deadline - time.monotonic() - 20))
        durable_private(slot / "worker-admission.json", {"preflight_only": True, "timeout_seconds": timeout})
        stderr_stream = (slot / "stderr.private").open("xb")
        os.fchmod(stderr_stream.fileno(), 0o600)
        cleanup = {}
        try:
            self.active = subprocess.Popen(argv, cwd=scratch, env=closed_environment({"HOME": str(scratch), "TMPDIR": str(scratch)}),
                    stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=stderr_stream, start_new_session=True, close_fds=True)
            durable_private(slot / "process.json", {"pid": self.active.pid, "argv": argv, "profile_sha256": digest(template.encode()), "worker_sha256": self.spec["worker_sha256"]})
            out, _ = self.active.communicate(canonical(request), timeout=timeout)
            cleanup = end_process(self.active)
            stderr_stream.flush(); os.fsync(stderr_stream.fileno())
            err = (slot / "stderr.private").read_bytes()
            diagnostic = {**cleanup, "output_bytes": len(out), "output_sha256": digest(out),
                          "stderr_bytes": len(err), "stderr_sha256": digest(err)}
            if self.active.returncode != 0 and len(out) <= 4096:
                try:
                    failure_response = json.loads(out)
                    if set(failure_response) == {"ok", "code"} and failure_response["ok"] is False:
                        diagnostic["worker_failure_code"] = failure_response["code"]
                except (ValueError, TypeError):
                    pass
            durable_private(slot / "completion-metadata.json", diagnostic)
            require(self.active.returncode == 0 and not err and len(out) <= 131_072, "worker refused/unavailable")
            response = json.loads(out, object_pairs_hook=reject_duplicate_keys)
            require(set(response) == {"ok", "result"} and response["ok"] is True, "worker result shape")
            result = response["result"]
            durable_private(slot / "result-metadata.json", {**cleanup, "ok": True, "output_bytes": len(out), "output_sha256": digest(out),
                "stderr_bytes": len(err), "stderr_sha256": digest(err)})
        except BaseException:
            if self.active is not None:
                cleanup = end_process(self.active)
            durable_private(slot / "failure.json", {**cleanup, "worker_started": self.active is not None,
                "effect_unknown": tool == "u2_write_file" and self.active is not None})
            raise
        finally:
            try:
                stderr_stream.flush(); os.fsync(stderr_stream.fileno())
            finally:
                stderr_stream.close()
                if self.active is not None:
                    self.active.stdin.close(); self.active.stdout.close()
                    if cleanup.get("process_group_absent"):
                        self.active = None
        effect_applied = False if tool != "u2_write_file" else None
        journal_attempted = False
        result_identity = None
        try:
            if tool == "u2_write_file":
                key = args["file_id"]
                old = self.files[key]
                observed, raw = file_record(old["path"], limit=131_072 if self.contract_version == 2 else 65_536)
                wanted = args["content"].encode()
                if "view" in old:
                    observed["view"] = json.loads(json.dumps(old["view"]))
                    if old["view"]["kind"] == "replace-range":
                        begin, end = old["view"]["ranges"][0]
                        observed["view"]["ranges"] = [[begin, begin + len(wanted)]]
                        wanted = prior_write[:begin] + wanted + prior_write[end:]
                require(raw == wanted and observed["mode"] == old["mode"] and observed["sha256"] == result["sha256"] and
                        observed["identity"] == result["identity"] and not Path(swap[key]).exists(), "worker write postcondition")
                effect_applied = True
                self.files[key] = observed
                self.written_ids.add(key)
                self.verifiers.clear()
                result = {"file_id": key, "sha256": observed["sha256"], "bytes": len(raw)}
            elif tool == "u2_read_file":
                require([row["file_id"] for row in result["files"]] == args["file_ids"], "read result IDs")
                for row in result["files"]:
                    key = row["file_id"]
                    entry, raw = document_record(self.files[key])
                    require(row == document_item(key, entry, raw), "read result binding")
                    safe_text(row["content"], self.spec["allowed_identifiers"])
                for row in result["files"]:
                    row["origin"] = {"kind": "approved-document", "source_sha256": self.spec["source_digests"][row["file_id"]], "approval": self.budget.anchor["approval"]}
                self.read_ids.update(args["file_ids"])
            else:
                require(result["verifier_id"] == args["verifier_id"] and result["inputs"] == {key: value["sha256"] for key, value in self.files.items()} and type(result["pass"]) is bool, "verifier input identity")
                self.verifiers[args["verifier_id"]] = result
                if not result["pass"]:
                    failure = digest(wire_bytes({"verifier": args["verifier_id"], "inputs": result["inputs"], "findings": result["findings"]}))
                    require(failure != self.last_failure, "repeated failure without new evidence")
                    self.last_failure = failure
                if len(self.verifiers) == 3:
                    self.correction_open = False
            self.check_files()
            require(len(wire_bytes(result)) <= 64_000, "tool output does not fit native result envelope")
            result_identity = self.result_identity()
            journal_attempted = True
            self.budget.reserve("worker-result", {"tool": tool, "result_sha256": digest(wire_bytes(result)),
                "result_identity": result_identity, "oracle_sha256": self.oracle_sha256}, self.phase, self.start)
            return result
        except BaseException as error:
            # An attempted append may have reached disk before an I/O failure.
            diagnostic = {"tool": tool, "effect_applied": effect_applied,
                "journal_outcome": "unconfirmed" if journal_attempted else "not_attempted",
                "effect_applied_unjournaled": None if journal_attempted else effect_applied,
                "result_identity": result_identity, "error_type": type(error).__name__}
            try:
                durable_private(slot / "journal-failure.json", diagnostic)
            except BaseException as record_error:
                raise error from record_error
            raise

    def seal(self):
        require(self.active is None and not self.sealed and set(self.verifiers) == {"DOC-LINKS", "DOC-GFM", "DOC-CLAIMS"} and
                all(result["pass"] for result in self.verifiers.values()) and set(self.spec["outputs"]) <= self.written_ids, "seal requires all five outputs and three current verifiers")
        identity = self.result_identity()
        self.budget.reserve("seal", {"result_identity": identity, "oracle_sha256": self.oracle_sha256}, self.phase, self.start)
        self.sealed = True
        return identity

    def progress(self):
        return {"unread_packs": [pack for pack in self.read_packs if not set(pack) <= self.read_ids],
                "unwritten_outputs": [key for key in self.spec["outputs"] if key not in self.written_ids],
                "verifiers": {key: {"pass": value["pass"], "findings": value["findings"]} for key, value in self.verifiers.items()},
                "current_outputs": {key: self.files[key]["sha256"] for key in self.spec["outputs"]}, "sealed": self.sealed}


TEMPLATE_VERSION = "u2-trusted-progress-v1"


def trusted_turn_input(owner_text, identity, progress, remaining_turns, handle=None, recovery=None):
    require(isinstance(owner_text, str) and len(owner_text.encode()) <= 65_536, "Owner input size")
    state = {"template": TEMPLATE_VERSION, "approval": identity["approval"], "work": identity["work"],
             "phase": "sealed-accept-only" if handle else "editing", "progress": progress, "remaining_turns": remaining_turns}
    if handle:
        state["accept_handle"] = handle
    if recovery is not None:
        state["recovery"] = recovery
    texts = [owner_text, wire_bytes(state).decode()]
    require(all(0 < len(text.encode()) <= 65_536 for text in texts), "trusted template payload limit")
    return [{"type": "text", "text": text, "text_elements": []} for text in texts]


def artifact_read(path, *, executable=False, limit=536_870_912):
    """Public-readable immutable input is distinct from a private control file."""
    path=Path(path)
    require(path.is_absolute() and path.resolve(strict=True)==path,"noncanonical artifact")
    fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC)
    with os.fdopen(fd,"rb") as stream:
        before=os.fstat(stream.fileno());mode=stat.S_IMODE(before.st_mode)
        require(stat.S_ISREG(before.st_mode) and before.st_nlink==1 and before.st_uid==os.getuid()
                and mode in ((0o700,0o755) if executable else (0o600,0o644)),"artifact ownership/mode/alias")
        raw=stream.read(limit+1)
        same=lambda after: all(getattr(before,k)==getattr(after,k) for k in ("st_dev","st_ino","st_mode","st_nlink","st_uid","st_size","st_mtime_ns","st_ctime_ns"))
        require(len(raw)<=limit and same(os.fstat(stream.fileno())) and same(path.lstat()),"artifact size/drift")
        return raw


def fixed_file_observation(paths):
    result = {}
    for name in paths:
        path = Path(name)
        require(path.is_absolute() and path.parent.resolve(strict=True) == path.parent, "recovery path alias")
        if not path.exists():
            require(not path.is_symlink(), "recovery path symlink")
            result[name] = {"missing": True}
            continue
        info = path.lstat()
        require(stat.S_ISREG(info.st_mode) and info.st_nlink == 1, "recovery file alias")
        stable = lambda value: (value.st_dev, value.st_ino, value.st_mode, value.st_nlink,
                                value.st_uid, value.st_gid, value.st_size,
                                value.st_mtime_ns, value.st_ctime_ns)
        fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC)
        with os.fdopen(fd, "rb") as stream:
            require(stable(os.fstat(stream.fileno())) == stable(info), "recovery file replaced")
            raw = stream.read()
            require(stable(os.fstat(stream.fileno())) == stable(info), "recovery observation changed")
        require(stable(path.lstat()) == stable(info), "recovery observation changed")
        result[name] = {"sha256": digest(raw), "mode": stat.S_IMODE(info.st_mode)}
    return result


class EffectAdmission:
    """Host-owned authority and effect gate; native envelopes are normalized by adapters."""
    def __init__(self, identity, tools, budget, phase, start):
        expected = {"approval", "work", "home", "actor", "action", "scope_identity", "result_identity", "grant_identity", "input_identity"}
        require(set(identity) == expected and identity["action"] == "accept", "invalid delegated identity")
        actor = identity["actor"]
        require(isinstance(actor, str) and bool(actor) and actor == actor.strip() and
                not any(unicodedata.category(char).startswith("C") for char in actor) and
                unicodedata.normalize("NFKC", actor).casefold() not in ("owner", "human"), "invalid delegated actor")
        self.identity = json.loads(json.dumps(identity))
        self.identity_hash = digest(wire_bytes(identity))
        self.tools = json.loads(json.dumps(tools))
        self.budget, self.phase, self.start = budget, phase, start
        self.session, self.step, self.plan, self.manifest_sha = None, None, None, None
        self.call, self.used_calls, self.envelope_sha = None, set(), None
        self.completed, self.stopped, self.sealed = True, False, False

    def callback(self, params):
        require(not self.stopped and not self.completed and self.call is None and self.step is not None, "callback outside active turn")
        require(isinstance(params, dict) and set(params) == {"session", "step", "call", "tool", "arguments"}, "callback fields")
        require(params["session"] == self.session and params["step"] == self.step, "foreign callback identity")
        call = params["call"]
        require(isinstance(call, str) and call and call not in self.used_calls, "unknown/reused call")
        require(params["tool"] in {tool["name"] for tool in self.tools}, "unknown callback tool")
        require(digest(wire_bytes(self.identity)) == self.identity_hash, "authority identity drift")
        if self.sealed:
            require(params["tool"] == "u2_accept", "post-submit tool rejected")
        else:
            require(params["tool"] != "u2_accept", "accept before sealing")
        subject = self.dispatch_subject(call)
        # A native reservation with this exact call must precede the host effect.
        self.budget.reserve("host-dispatch", subject, self.phase, self.start)
        self.call = call
        self.used_calls.add(call)
        return params["tool"], params["arguments"]

    def stop(self):
        self.stopped = True

    def dispatch_subject(self, call):
        return {"session": self.session, "step": self.step, "plan": self.plan, "call": call}

    def authority_subject(self):
        return {"session": self.session, "step": self.step, "call": self.call}


__all__ = ['HostRefusal', 'digest', 'canonical', 'durable_json', 'wire_bytes', 'require', 'checked_open', 'control_read', 'durable_private', 'publish_acceptance_request', 'continuous_ns', 'bounded_flock', 'ControllerLock', 'ENV_NAMES', 'closed_environment', 'end_process', 'reject_duplicate_keys', 'core_bytes', 'safe_text', 'InstalledCore', 'Acceptance', 'RecoveryGate', 'document_stat_key', 'file_record', 'document_record', 'document_view', 'document_item', 'initial_view_contracts', 'parent_identities', 'sb_literal', 'pack_reads', 'DocumentController', 'TEMPLATE_VERSION', 'trusted_turn_input', 'artifact_read', 'fixed_file_observation']

__all__.append('EffectAdmission')


# Appended to contracts.py by the scoped B edit script.
import threading


class EffectJournal:
    """Private hash chain; append failure poisons this process and never repairs history."""
    def __init__(self, path, *, create=False):
        self.os = execution_os(require)
        self.path = Path(path)
        self.mutex, self.failed = threading.RLock(), False
        if create:
            self.os.create_journal(self.path)
        self.rows = self.read()


    def read(self):
        raw = control_read(self.path, 16 * 1024 * 1024)
        require(not raw or raw.endswith(b'\n'), 'journal-partial')
        rows, previous = [], '0' * 64
        for line in raw.splitlines():
            row = json.loads(line, object_pairs_hook=reject_duplicate_keys)
            require(isinstance(row, dict) and set(row) == {'seq', 'previous', 'kind', 'value', 'sha256'}, 'journal-fields')
            body = {key: value for key, value in row.items() if key != 'sha256'}
            require(type(body['seq']) is int and body['seq'] == len(rows) + 1 and body['previous'] == previous
                    and digest(canonical(body)) == row['sha256'] and canonical(row) == line + b'\n', 'journal-chain')
            require(len(rows) < 8192, 'journal-count-limit')
            rows.append(row)
            previous = row['sha256']
        return rows

    def append(self, kind, value):
        with self.mutex:
            require(not self.failed, 'journal-poisoned')
            require(self.read() == self.rows, 'journal-external-change')
            require(len(self.rows) < 8192, 'journal-count-limit')
            row = {'seq': len(self.rows) + 1, 'previous': self.rows[-1]['sha256'] if self.rows else '0' * 64,
                   'kind': kind, 'value': json.loads(json.dumps(value))}
            row['sha256'] = digest(canonical(row))
            raw = canonical(row)
            require(len(raw) <= 2_097_152, 'journal-row-limit')
            try:
                self.os.append_journal(self.path, raw, checked_open, lambda: self.read() == self.rows, 16 * 1024 * 1024)
            except BaseException:
                self.failed = True
                raise
            self.rows.append(row)
            return row



class ReadWorkerBudget:
    """Only a Host-reserved document operation may report a worker result."""
    def __init__(self, host):
        self.host = host
        self.anchor = {'version': 4, 'approval': host.cfg['identity']['approval']}

    def check_worker_result(self, subject, phase, start, timeout):
        require(self.host.pending is not None and timeout > 0, 'worker-not-reserved')
        remaining = self.host.deadline - self.host.os.monotonic()
        require(remaining > 0, 'worker-deadline')
        return min(timeout, 60, remaining)

    def reserve(self, kind, subject, *args):
        require(kind == 'worker-result' and self.host.pending is not None, 'unexpected-worker-event')
        return self.host.journal.append(kind, subject)


class ReadOnlyHost:
    """Approved read/verify profile, independent of any CLI, model or native protocol.

    The trusted caller supplies an exact Core reader and fixed config digest.
    This profile has no delegated accept/write handle. It is intentionally not
    evidence that another adapter supports the Codex authority path.
    """
    RUNTIME_KINDS = frozenset({'native-start', 'host-input', 'bridge-request'})

    def __init__(self, cfg, cfg_sha256, run, snapshot_reader, deadline, *, resume=False, worker=True):
        self.os = execution_os(require)  # Capability refusal precedes files and reservations.
        require(digest(canonical(cfg)) == cfg_sha256, 'config-drift')
        self.cfg = json.loads(json.dumps(cfg))
        self.cfg_sha256, self.snapshot_reader, self.deadline = cfg_sha256, snapshot_reader, deadline
        expected = {'core_project', 'core_snapshot_sha256', 'identity', 'identity_sha256', 'documents',
                    'request_limit', 'effect_limit', 'runtime_limits'}
        require(set(cfg) == expected, 'read-host-config-fields')
        require(set(cfg['runtime_limits']) == self.RUNTIME_KINDS and all(
            type(n) is int and n > 0 for n in cfg['runtime_limits'].values()), 'runtime-limits')
        require(all(type(cfg[k]) is int and 0 < cfg[k] <= 16 for k in ('request_limit', 'effect_limit')), 'effect-limits')
        self.run = Path(run)
        require(self.run.is_absolute() and self.run.resolve() == self.run, 'run-path-alias')
        self.os.private_directory(self.run, resume=resume)
        if not resume:
            durable_private(self.run / 'controller.lock', {})
        self.lock = self.os.controller_lock(self.run / 'controller.lock', checked_open, require)
        self.mutex = threading.RLock()
        self.pending, self.session, self.step = None, None, None
        self.stopped, self.revoked, self.slot = False, False, False
        self.seen, self.steps, self.starts, self.stops = set(), set(), set(), set()
        self.requests, self.effects, self.worker_calls = 0, 0, 0
        self.runtime_counts = {kind: 0 for kind in self.RUNTIME_KINDS}
        self.controller = None
        try:
            self.journal = EffectJournal(self.run / 'journal.jsonl', create=not resume)
            if resume:
                self.restore()
            else:
                self.journal.append('anchor', {'config_sha256': cfg_sha256})
            self.check_core()
            if worker:
                generation = self.runtime_counts['native-start']
                wd, scratch = self.run / ('workers-' + str(generation)), self.run / ('scratch-' + str(generation))
                wd.mkdir(mode=0o700); scratch.mkdir(mode=0o700)
                self.controller = DocumentController({**self.cfg['documents'], 'scratch': str(scratch)}, wd,
                    ReadWorkerBudget(self), 'synthetic', 'read-profile', deadline)
        except BaseException:
            self.lock.close()
            raise

    def check_core(self, *, check_deadline=True):
        if check_deadline:
            require(self.os.monotonic() < self.deadline, 'host-deadline')
        require(digest(canonical(self.cfg)) == self.cfg_sha256, 'config-drift')
        identity = self.cfg['identity']
        require(set(identity) == {'approval', 'home', 'work', 'actor', 'action', 'scope_sha256', 'result_sha256',
                                 'intent_sha256', 'grant'}, 'read-identity-fields')
        actor = identity['actor']
        require(isinstance(actor, str) and actor and actor == actor.strip() and
                not any(unicodedata.category(char).startswith('C') for char in actor) and
                unicodedata.normalize('NFKC', actor).casefold() not in ('owner', 'human'), 'read-actor')
        require(identity['action'] == 'read-verify-only' and identity['grant'] == 'none; authority tools excluded', 'read-authority')
        require(digest(canonical(identity)) == self.cfg['identity_sha256'], 'identity-drift')
        snapshot = self.snapshot_reader(self.cfg['core_project'], identity['work'])
        require(digest(canonical(snapshot)) == self.cfg['core_snapshot_sha256'], 'core-state-drift')
        require(snapshot['home'] == identity['home'] and snapshot['work'] == identity['work'] and
                digest(canonical(snapshot['result_refs'])) == identity['result_sha256'] and
                digest(canonical(snapshot['intent_ref'])) == identity['intent_sha256'], 'core-identity-drift')
        require(not self.cfg['documents']['outputs'] and
                digest(canonical(self.cfg['documents']['files'])) == identity['scope_sha256'], 'read-scope-drift')
        return snapshot

    def restore(self):
        rows = self.journal.rows
        require(rows and rows[0]['kind'] == 'anchor' and rows[0]['value'] == {'config_sha256': self.cfg_sha256}, 'resume-anchor')
        pending, stopped = set(), False
        allowed = {'anchor', 'request', 'effect', 'completed', 'refused', 'worker-result', 'step', 'stop', 'revoke', 'native-stop'} | self.RUNTIME_KINDS
        for row in rows[1:]:
            kind, value = row['kind'], row['value']
            require(kind in allowed and kind != 'anchor', 'journal-unknown-event')
            if kind == 'request':
                self.requests += 1
                if isinstance(value, dict) and isinstance(value.get('session'), str) and isinstance(value.get('call_id'), str):
                    self.seen.add((value['session'], value['call_id']))
            elif kind == 'effect':
                self.effects += 1
                require(value['request_seq'] not in pending, 'journal-duplicate-effect')
                pending.add(value['request_seq'])
            elif kind == 'completed':
                require(value['request_seq'] in pending and digest(canonical(value['result'])) == value['result_sha256'], 'journal-completion')
                pending.remove(value['request_seq'])
            elif kind in self.RUNTIME_KINDS:
                self.runtime_counts[kind] += 1
                if kind == 'native-start':
                    require(value['session'] not in self.starts, 'native-session-reuse')
                    self.starts.add(value['session'])
            elif kind == 'native-stop':
                require(value['session'] in self.starts and value.get('processes_absent') is True, 'native-stop-unverified')
                self.stops.add(value['session'])
            elif kind == 'step':
                key = (value['session'], value['step'])
                require(key not in self.steps, 'step-reuse')
                self.steps.add(key)
                stopped = False
            elif kind == 'stop':
                require(value['requests'] == self.requests and value['effects'] == self.effects and value['pending'] is None, 'stop-state')
                stopped = True
            elif kind == 'revoke':
                self.revoked = True
        require(not pending, 'pending-effect-unknown')
        require(stopped and self.starts == self.stops and not self.revoked, 'resume-not-safely-stopped')
        require(self.requests <= self.cfg['request_limit'] and self.effects <= self.cfg['effect_limit'] and all(
            self.runtime_counts[k] <= self.cfg['runtime_limits'][k] for k in self.RUNTIME_KINDS), 'resume-budget-drift')

    def reserve_runtime(self, kind, value):
        with self.mutex:
            require(kind in self.RUNTIME_KINDS and not self.stopped and not self.revoked, 'runtime-closed')
            self.check_core()
            require(self.runtime_counts[kind] < self.cfg['runtime_limits'][kind], 'runtime-budget')
            if kind == 'native-start':
                require(isinstance(value.get('session'), str) and value['session'] and value['session'] not in self.starts, 'native-session-reuse')
            row = self.journal.append(kind, value)
            self.runtime_counts[kind] += 1
            if kind == 'native-start':
                self.starts.add(value['session'])
            return row

    def native_stopped(self, session, processes_absent):
        with self.mutex:
            require(session in self.starts and processes_absent is True, 'native-stop-unverified')
            self.journal.append('native-stop', {'session': session, 'processes_absent': True})
            self.stops.add(session)

    def open_step(self, session, step):
        with self.mutex:
            require(not self.stopped and not self.revoked and self.pending is None, 'step-closed')
            require(isinstance(session, str) and isinstance(step, str) and session and step and
                    (session, step) not in self.steps, 'step-reuse')
            self.check_core()
            self.journal.append('step', {'session': session, 'step': step})
            self.session, self.step, self.slot = session, step, False
            self.steps.add((session, step))

    def dispatch(self, envelope):
        with self.mutex:
            try:
                row = self.journal.append('request', envelope)
                self.requests += 1
            except BaseException:
                self.stopped = True
                raise
            try:
                require(self.requests <= self.cfg['request_limit'], 'request-budget')
                require(not self.stopped and not self.revoked and self.pending is None, 'closed-or-revoked')
                require(isinstance(envelope, dict) and set(envelope) == {'session', 'step', 'call_id', 'tool', 'arguments', 'identity'}, 'envelope-fields')
                require(envelope['identity'] == self.cfg['identity'], 'identity-mismatch')
                self.check_core()
                require(envelope['session'] == self.session and envelope['step'] == self.step and self.session is not None, 'session-step-mismatch')
                key = (envelope['session'], envelope['call_id'])
                require(isinstance(key[1], str) and key[1] and key not in self.seen, 'duplicate-call')
                self.seen.add(key)
                require(not self.slot, 'effect-slot-budget')
                tool, args = envelope['tool'], envelope['arguments']
                require(tool in ('u2_read_file', 'u2_verify') and isinstance(args, dict), 'tool-scope')
                if tool == 'u2_read_file':
                    require(set(args) == {'file_ids'} and isinstance(args['file_ids'], list) and 1 <= len(args['file_ids']) <= 8
                            and all(isinstance(v, str) for v in args['file_ids']) and len(set(args['file_ids'])) == len(args['file_ids'])
                            and set(args['file_ids']) <= set(self.cfg['documents']['files']), 'file-scope')
                else:
                    require(set(args) == {'verifier_id'} and args['verifier_id'] in ('DOC-LINKS', 'DOC-GFM', 'DOC-CLAIMS'), 'verifier-scope')
                require(self.effects < self.cfg['effect_limit'], 'effect-slot-budget')
                require(self.controller is not None, 'worker-unavailable')
                self.journal.append('effect', {'request_seq': row['seq'], 'tool': tool})
                self.slot, self.pending = True, row['seq']
                self.effects += 1
                self.worker_calls += 1
                result = self.controller.dispatch(tool, args)
                self.journal.append('completed', {'request_seq': row['seq'], 'result_sha256': digest(canonical(result)), 'result': result})
                self.pending = None
                return {'ok': True, 'result': result}
            except HostRefusal as error:
                # A worker-side failure after reservation stays pending and cannot resume.
                if self.pending is not None:
                    self.stopped = True
                self.journal.append('refused', {'request_seq': row['seq'], 'code': str(error)})
                return {'ok': False, 'code': str(error)}
            except BaseException:
                self.stopped = True
                raise

    def revoke(self):
        with self.mutex:
            self.journal.append('revoke', {})
            self.revoked = True

    def stop(self):
        with self.mutex:
            self.stopped = True
            self.journal.append('stop', {'session': self.session, 'step': self.step, 'requests': self.requests,
                                        'effects': self.effects, 'pending': self.pending})

    def recovery(self):
        snapshot = self.check_core(check_deadline=False)
        require(self.stopped and self.pending is None and self.starts == self.stops and not self.revoked, 'recovery-not-stopped')
        require(self.journal.read() == self.journal.rows, 'recovery-journal-drift')
        return {'core': snapshot, 'identity': self.cfg['identity'], 'requests': self.requests, 'effects': self.effects,
                'runtime_counts': dict(self.runtime_counts), 'journal_sha256': digest(control_read(self.journal.path)),
                'pending': None, 'last_completed': [r['value'] for r in self.journal.rows if r['kind'] == 'completed'], 'stopped': True}

    def close(self):
        self.lock.close()


__all__ += ['EffectJournal', 'ReadWorkerBudget', 'ReadOnlyHost']
