"""Installed document effects and durable journal; no Core acceptance or model transport."""

from __future__ import annotations

import argparse

import hashlib

import json

import os
import resource

from pathlib import Path

import selectors

import signal

import subprocess

import time

import unicodedata

import fcntl

from .official_os import execution_os

import stat

import sys

import re

def worker_file_limit():
    # Kernel limit also bounds diagnostic files if the worker fails before output validation.
    resource.setrlimit(resource.RLIMIT_FSIZE, (1024 * 1024, 1024 * 1024))
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))

class HostRefusal(RuntimeError):
    """A required host boundary is unavailable or inconsistent."""

def digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()

def canonical(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode()

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
    raw = canonical(value)
    limit = 1048576 if Path(path).name == "spec.json" else 131072 if Path(path).name == "request.json" else 65536
    require(len(raw) <= limit, "worker-record-size")
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC, 0o600)
    with os.fdopen(fd, "wb") as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())
    parent = os.open(Path(path).parent, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        os.fsync(parent)
    finally:
        os.close(parent)

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
        require(len(template.encode()) <= 1048576, "worker-profile-size")
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
        spawn_failed_confirmed = False
        try:
            try:
                self.active = subprocess.Popen(argv, cwd=scratch, env=closed_environment({"HOME": str(scratch), "TMPDIR": str(scratch)}),
                        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=stderr_stream, start_new_session=True, close_fds=True, preexec_fn=worker_file_limit)
            except (OSError, subprocess.SubprocessError):
                # Popen reports a synchronous startup failure only after reaping its failed child.
                spawn_failed_confirmed = True
                raise
            from .official_state import process_birth
            birth = process_birth(self.active.pid)
            require(bool(birth), "worker process identity unavailable")
            durable_private(slot / "process.json", {"pid": self.active.pid, "birth": birth, "argv": argv, "profile_sha256": digest(template.encode()), "worker_sha256": self.spec["worker_sha256"]})
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
                "spawn_failed_confirmed": spawn_failed_confirmed,
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

import threading

def journal_rows(raw):
    """One canonical hash-chain parser shared by live and historical reads."""
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


def journal_identity(info):
    return (info.st_dev, info.st_ino, info.st_mode, info.st_uid, info.st_nlink,
            info.st_size, info.st_mtime_ns, info.st_ctime_ns)

def observe_journal(path):
    """Read a candidate history without granting append authority or changing mode."""
    path = Path(path)
    require(path.is_absolute() and path.resolve(strict=True) == path, 'noncanonical control file')
    before = path.lstat()
    mode = stat.S_IMODE(before.st_mode)
    # Preserve the live reader's private-mode predicate. Only the capsule state
    # machine may accept exactly 0600/0644 as terminal history.
    require(stat.S_ISREG(before.st_mode) and before.st_uid == os.getuid() and before.st_nlink == 1
            and (mode == 0o644 or not mode & 0o077), 'unsafe journal observation')
    limit = 16 * 1024 * 1024
    require(before.st_size <= limit, 'control file too large')
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC | os.O_NONBLOCK)
    with os.fdopen(fd, 'rb') as stream:
        require(journal_identity(before) == journal_identity(os.fstat(stream.fileno())), 'journal-observation-drift')
        raw = stream.read(limit + 1)
        require(len(raw) <= limit, 'control file too large')
        require(journal_identity(before) == journal_identity(os.fstat(stream.fileno())) == journal_identity(path.lstat())
                and path.resolve(strict=True) == path, 'journal-observation-drift')
    return journal_rows(raw), mode, journal_identity(before)

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
        return journal_rows(raw)

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
