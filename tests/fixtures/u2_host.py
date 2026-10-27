"""Synthetic config/read fixtures only; no installed-runtime or account access."""
from copy import deepcopy


def profile():
    return {"filesystem": {":minimal": "read", ":tmpdir": "deny", ":slash_tmp": "deny",
                           "/synthetic/worker/input.md": "read", "/synthetic/worker/output.md": "write"},
            "network": {"enabled": False}}


def config_response():
    policy = profile()
    return {"config": {"permissions": {"colvia-u2-worker": deepcopy(policy)},
                       "default_permissions": "colvia-u2-worker", "sandbox_mode": None,
                       "mcp_servers": {name: {"enabled": False} for name in ("openaiDeveloperDocs", "node_repl", "computer-use")},
                       "features": {name: False for name in ("apps", "hooks", "multi_agent", "multi_agent_v2", "code_mode", "code_mode_host")},
                       "plugins": {"synthetic-plugin@synthetic-market": {"enabled": False}},
                       "web_search": "disabled"},
            "layers": [{"name": {"type": "sessionFlags"}, "version": "synthetic", "config": {"permissions": {"colvia-u2-worker": deepcopy(policy)}}}],
            "origins": {}}


def with_schema_null_defaults(response):
    result = deepcopy(response)
    policy = result["config"]["permissions"]["colvia-u2-worker"]
    policy.update(description=None, extends=None, workspace_roots=None)
    policy["filesystem"]["glob_scan_max_depth"] = None
    policy["network"].update(domains=None, mode=None, proxy_url=None, allow_upstream_proxy=None,
                              allow_local_binding=None, dangerously_allow_all_unix_sockets=None,
                              dangerously_allow_non_loopback_proxy=None, enable_socks5=None,
                              enable_socks5_udp=None, mitm=None, socks_url=None, unix_sockets=None)
    return result


# The functions below construct synthetic control inputs. They never inspect a
# real account, installed project, authority home or user configuration.
def budget(host, root):
    import time
    return host.Budget.create(root / "budget", {"version": 1, "approval": "synthetic-approval", "work": "synthetic-task",
        "candidate": "a" * 64, "source_identity": "synthetic-source", "total_deadline_ms": time.time_ns() // 1_000_000 + 7_200_000,
        "origin_wall_ms": time.time_ns() // 1_000_000, "origin_monotonic_ns": time.monotonic_ns(), "input_identity": "b" * 64})


def identity():
    return {"approval": "synthetic-approval", "work": "work-synthetic", "home": "home-synthetic", "actor": "delegate-synthetic",
            "action": "accept", "scope_identity": "c" * 64, "result_identity": "d" * 64,
            "grant_identity": "e" * 64, "input_identity": "b" * 64}


def profile_tools():
    import json
    from pathlib import Path
    path = Path(__file__).resolve().parents[2] / "docs/development/verification/u2-host/tool-profile.json"
    return json.loads(path.read_bytes())


def admitted(host, root):
    b = budget(host, root)
    b.reserve("start", {"reason": "synthetic"}, "synthetic", "synthetic-01")
    b.reserve("runtime-entered", {"start": "synthetic-01"}, "synthetic", "synthetic-01")
    b.reserve("thread", {"request": 2}, "synthetic", "synthetic-01")
    b.reserve("thread-bound", {"request": 2, "thread": "thread-1"}, "synthetic", "synthetic-01")
    tools = profile_tools()
    a = host.Admission(identity(), "synthetic-source", "a" * 64, "template-1", tools, b, "synthetic", "synthetic-01")
    inputs = [{"type": "text", "text": "Owner-approved synthetic document task.", "text_elements": []}]
    entries = [{"name": tool["name"], "namespace": "functions", "origin": "dynamic", "exposure": "direct",
        "implementation": "synthetic::DynamicToolHandler", "spec": {"type": "function", "name": tool["name"],
            "description": tool["description"], "strict": False, "parameters": host.native_document_schema(tool["inputSchema"])}} for tool in tools]
    manifest = {"version": 1, "planId": "plan-1", "sourceIdentity": "synthetic-source", "buildIdentity": "sha256:" + "a" * 64,
        "snapshot": {"initial_input": inputs, "history_binding": {"input_template": "template-1", "input_sha256": host.digest(host.wire_bytes(inputs)),
            "count": 0, "sha256": host.digest(b"[]")}, "context": {"model": {"slug": "gpt-6-astra"}, "reasoning_effort": "xhigh",
                "wire_profile": {"api": "responses_http", "include_internal": False, "compression": "none", "authentication": "native_read_only"}}},
        "toolEnvelope": {"entries": entries, "model_specs": [entry["spec"] for entry in entries], "tool_mode": "direct", "namespaces": None, "policy": {"expose_additional_permissions": False, "require_managed_sandbox": False, "require_unified_exec": False, "allowed_tools": [{"namespace": None, "name": tool["name"]} for tool in tools]}}}
    prepared = {"handle": "synthetic-prepared-handle", "manifest": manifest}
    a.bind("thread-1", prepared, inputs)
    a.bind_turn("turn-1")
    b.reserve("turn", {"thread": "thread-1", "plan": "plan-1"}, "synthetic", "synthetic-01")
    subject = {"thread": "thread-1", "turn": "turn-1", "plan": "plan-1"}
    b.reserve("generation", {**subject, "generation": 1}, "synthetic", "synthetic-01")
    b.reserve("dispatch", {**subject, "call": "call-1"}, "synthetic", "synthetic-01")
    call = {"threadId": "thread-1", "turnId": "turn-1", "callId": "call-1", "namespace": None,
            "tool": "u2_read_file", "arguments": {"file_ids": ["Output"]}}
    return a, b, prepared, inputs, call


def ticket_packet(host):
    ticket = {"record_type": "confirmation-ticket", "schema_version": 1, "authority_home_id": "home-synthetic",
        "object": {"authority_home_id": "home-synthetic", "kind": "work", "id": "work-synthetic"},
        "action": "accept", "actor": "delegate-synthetic", "reason": "synthetic accepted result", "request_id": "request-1",
        "observed_at": "2026-01-01T00:00:00Z", "target_revision_ref": {"id": "revision-1", "sha256": "1" * 64},
        "expected_selection_ref": {"id": "selection-1", "sha256": "2" * 64}, "intent_ref": {"id": "intent-1", "sha256": "3" * 64},
        "product_binding_ref": {"id": "binding-1", "sha256": "4" * 64}, "document_refs": [], "evidence_refs": [],
        "execution_mode": "isolated-worktree", "supersedes_decision_ref": None, "target_fingerprint": "synthetic"}
    return {"ticket": ticket, "confirm_token": host.digest(host.core_bytes(ticket))[:16]}


class FakeCore:
    """A call recorder, never installed Core evidence."""
    def __init__(self, packet):
        self.packet = deepcopy(packet)
        self.calls = []
        self.refuse_prepare = False

    def invoke(self, action, value, token=None):
        self.calls.append((action, deepcopy(value), token))
        if action == "prepare":
            if self.refuse_prepare:
                raise RuntimeError("synthetic revoked grant")
            return deepcopy(self.packet)
        return {"synthetic": "accepted"}


def worker_module():
    import importlib.util
    from pathlib import Path
    spec = importlib.util.spec_from_file_location("u2_document_worker", Path(__file__).resolve().parents[2] / "docs/development/verification/u2-host/worker.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def documents(host, root):
    output, reference = root / "output.md", root / "reference.md"
    output.write_text("# Draft\n\nRequired claim is missing.\n")
    reference.write_text("# Source\n\nVerified reference fact.\n")
    output.chmod(0o600)
    reference.chmod(0o600)
    files = {"Output": host.file_record(output)[0], "Reference": host.file_record(reference)[0]}
    swap = root / "Output.swap"
    return {"version": 1, "files": files, "parents": host.parent_identities([str(output), str(reference), str(swap)]),
        "outputs": ["Output"], "swap": {"Output": str(swap)}, "parser": "/synthetic/parser.js", "parser_sha256": "0" * 64,
        "claims": {"Output": {"required": ["Verified reference fact."], "forbidden": ["unsupported claim"],
                               "evidence": [{"file_id": "Reference", "quote": "Verified reference fact."}]}}, "approved_external_links": []}


def installed_death_barrier(spec_path):
    """Synthetic-only instrumentation; replay and actual work never use it."""
    import contextlib
    import hashlib
    import json
    import os
    from pathlib import Path
    import runpy
    import stat
    import sys
    import time

    def need(value, message):
        if not value:
            raise RuntimeError(message)

    def checked(path, expected=None):
        path = Path(path)
        info = path.lstat()
        need(path.is_absolute() and path.resolve(strict=True) == path and stat.S_ISREG(info.st_mode) and info.st_nlink == 1, "barrier input alias")
        # Reading may change atime. Preserve inode, permissions and content metadata.
        stable = lambda value: (value.st_dev, value.st_ino, value.st_mode, value.st_nlink,
                                value.st_uid, value.st_gid, value.st_size,
                                value.st_mtime_ns, value.st_ctime_ns)
        fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC)
        with os.fdopen(fd, "rb") as stream:
            need(stable(os.fstat(stream.fileno())) == stable(info), "barrier input replaced")
            raw = stream.read()
            need(stable(os.fstat(stream.fileno())) == stable(info), "barrier input changed")
        need(stable(path.lstat()) == stable(info), "barrier input changed")
        if expected is not None:
            need(hashlib.sha256(raw).hexdigest() == expected, "barrier input digest")
        return raw

    spec = json.loads(checked(spec_path))
    need(set(spec) == {"synthetic_only", "case", "launcher", "launcher_sha256", "modules", "packet", "packet_sha256", "observation", "seconds"}, "barrier fields")
    need(spec["synthetic_only"] is True and spec["case"] in ("S1", "S2", "S3", "S4", "S5"), "synthetic death case")
    need(sys.flags.isolated and sys.dont_write_bytecode and type(spec["seconds"]) is int and 0 < spec["seconds"] <= 300, "barrier runtime/bound")
    need(not any(key == "hv2ref" or key.startswith("hv2ref.") for key in sys.modules), "source module cache contaminates installed evidence")
    launcher = Path(spec["launcher"])
    checked(launcher, spec["launcher_sha256"])
    packet = json.loads(checked(spec["packet"], spec["packet_sha256"]))
    # The installed launcher's own bootstrap verifies the complete module inventory.
    bootstrap = runpy.run_path(str(launcher), run_name="u2_verified_bootstrap")
    source = bootstrap["workspace_source"](launcher.parent)
    sys.path.insert(0, str(source))
    from hv2ref import work, workspace
    for name, module in list(sys.modules.items()):
        if name == "hv2ref" or name.startswith("hv2ref."):
            path = Path(module.__file__)
            need(path.parent == source / "hv2ref" and str(path) in spec["modules"], "loaded module outside installed payload")
            checked(path, spec["modules"][str(path)])
    original_guard = workspace.writer_guard
    original_immutable = work._publish_immutable
    original_file = work._apply_worker_path
    original_current = work._publish_current
    depth = 0
    file_count = 0
    fired = False

    @contextlib.contextmanager
    def observed_guard(*args, **kwargs):
        nonlocal depth
        with original_guard(*args, **kwargs):
            depth += 1
            try:
                yield
            finally:
                depth -= 1

    def barrier(point):
        nonlocal fired
        need(depth > 0 and not fired, "barrier outside active writer guard or repeated")
        fired = True
        loaded = {}
        for name, module in list(sys.modules.items()):
            if name == "hv2ref" or name.startswith("hv2ref."):
                path = Path(module.__file__)
                need(path.parent == source / "hv2ref" and str(path) in spec["modules"], "late module outside installed payload")
                checked(path, spec["modules"][str(path)])
                loaded[name] = {"path": str(path), "sha256": spec["modules"][str(path)]}
        observed = {"case": spec["case"], "point": point, "writer_guard_active": True, "pid": os.getpid(),
                    "process_group": os.getpgrp(), "packet_sha256": spec["packet_sha256"], "loaded_modules": loaded,
                    "launcher_sha256": spec["launcher_sha256"], "instrumented_initial_call": True}
        path = Path(spec["observation"])
        with path.open("xb") as stream:
            os.fchmod(stream.fileno(), 0o600)
            stream.write((json.dumps(observed, sort_keys=True, indent=2) + "\n").encode())
            stream.flush(); os.fsync(stream.fileno())
        fd = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)
        deadline = time.monotonic() + spec["seconds"]
        while time.monotonic() < deadline:
            time.sleep(0.05)
        raise RuntimeError("barrier ended without observed process death")

    def immutable(path, value):
        original_immutable(path, value)
        if spec["case"] == "S1" and Path(path).parent.name == "decisions":
            barrier("after-decision")
        if spec["case"] == "S4" and Path(path).parent.name == "selections":
            barrier("after-selection")

    def apply_file(*args, **kwargs):
        nonlocal file_count
        original_file(*args, **kwargs)
        file_count += 1
        if spec["case"] in ("S2", "S3") and file_count == 1:
            barrier("after-file")

    def current(*args, **kwargs):
        original_current(*args, **kwargs)
        if spec["case"] == "S5":
            barrier("after-current")

    workspace.writer_guard = observed_guard
    work._publish_immutable = immutable
    work._apply_worker_path = apply_file
    work._publish_current = current
    sys.argv = [str(launcher), "work", "apply", "--input", "-", "--confirm", packet["confirm_token"]]
    # runpy makes __main__.__file__ the actual launcher, preserving its native
    # installed-runtime verification while the named helpers are instrumented.
    runpy.run_path(str(launcher), run_name="__main__")
    raise RuntimeError("installed apply returned without the specified barrier")


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3 or sys.argv[1] != "--synthetic-death-spec":
        raise SystemExit("synthetic fixture command required")
    installed_death_barrier(sys.argv[2])
