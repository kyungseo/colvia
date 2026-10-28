"""Exact Codex prepared transport and its historical native budget policies."""
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
import stat
import sys
import re

from ..contracts import *
from ..execution_os import execution_os
from . import fresh_codex_contract as fresh_u2
from . import edit_codex_contract as edit_u2


def execution_policy(anchor):
    """Closed descriptor selection; unknown kind/version never selects a new execution path."""
    if anchor.get("version") == 59:
        edit_u2.anchor_fields(anchor)
        return edit_u2
    if anchor.get("version") == 58:
        fresh_u2.anchor_fields(anchor)
        return fresh_u2
    return None

DISABLED_FEATURES = ("apps", "hooks", "multi_agent", "multi_agent_v2", "code_mode", "code_mode_host")


EXPECTED_MCP = ("openaiDeveloperDocs", "node_repl", "computer-use")


ALLOWED_PREFLIGHT = {"initialize", "config/read", "configRequirements/read", "account/read", "model/list", "plugin/installed", "thread/start", "mcpServerStatus/list"}


class StdioClient:
    """Single child, bounded JSON lines, no server-initiated effects."""

    def __init__(self, argv: list[str], cwd: Path, run: Path, deadline: float):
        self.deadline = deadline
        self.buffer = b""
        self.sequence = 0
        self.events: list[dict] = []
        self.stderr = (run / "stderr.txt").open("xb")
        self.process = subprocess.Popen(argv, cwd=cwd, stdin=subprocess.PIPE,
                                        stdout=subprocess.PIPE, stderr=self.stderr,
                                        start_new_session=True)
        self.selector = selectors.DefaultSelector()
        self.selector.register(self.process.stdout, selectors.EVENT_READ)
        self.cleanup: dict = {}
        durable_json(run / "process.json", {"pid": self.process.pid, "argv": argv,
                                            "cwd": str(cwd), "started": time.time()})

    def send(self, value: dict) -> None:
        if time.monotonic() >= self.deadline:
            raise HostRefusal("RPC deadline expired")
        self.process.stdin.write(canonical(value))
        self.process.stdin.flush()

    def receive(self) -> dict:
        while b"\n" not in self.buffer:
            remaining = self.deadline - time.monotonic()
            if remaining <= 0 or not self.selector.select(remaining):
                raise HostRefusal("RPC receive deadline expired")
            chunk = os.read(self.process.stdout.fileno(), 65536)
            if not chunk:
                raise HostRefusal("App Server closed stdout before response")
            self.buffer += chunk
            if len(self.buffer) > 8 * 1024 * 1024:
                raise HostRefusal("RPC frame exceeded 8 MiB")
        line, self.buffer = self.buffer.split(b"\n", 1)
        value = json.loads(line)
        if not isinstance(value, dict):
            raise HostRefusal("RPC frame is not an object")
        return value

    def request(self, method: str, params: dict) -> dict:
        if method not in ALLOWED_PREFLIGHT:
            raise HostRefusal("Method is outside the preflight allowlist")
        self.sequence += 1
        request_id = self.sequence
        self.send({"id": request_id, "method": method, "params": params})
        while True:
            value = self.receive()
            if "method" in value:
                self.events.append({"method": value["method"], "request": "id" in value})
                if value["method"] == "configWarning":
                    raise HostRefusal("App Server reported a configuration warning; defaults are not accepted")
                if "id" in value:
                    # No command, file, permission, auth, or dynamic call can be approved here.
                    self.send({"id": value["id"], "error": {"code": -32601, "message": "preflight denies server requests"}})
                    raise HostRefusal("Unexpected server request during read-only preflight")
                continue
            if value.get("id") != request_id:
                raise HostRefusal("Unexpected RPC response identity")
            if "error" in value:
                raise HostRefusal("RPC refused " + method + ": " + str(value["error"]))
            if not isinstance(value.get("result"), dict):
                raise HostRefusal("RPC result is not an object")
            self.events.append({"method": method, "result_keys": sorted(value["result"])})
            return value["result"]

    def close(self) -> None:
        """Record cleanup even if a process fails to terminate; never claim absence from exit alone."""
        try:
            if not self.process.stdin.closed:
                self.process.stdin.close()
            try:
                self.process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                pass
            for sig in (signal.SIGTERM, signal.SIGKILL):
                try:
                    os.killpg(self.process.pid, 0)
                except ProcessLookupError:
                    break
                os.killpg(self.process.pid, sig)
                try:
                    self.process.wait(timeout=8)
                except subprocess.TimeoutExpired:
                    pass
            try:
                os.killpg(self.process.pid, 0)
                absent = False
            except ProcessLookupError:
                absent = True
            self.cleanup = {"exit_code": self.process.poll(), "process_group_absent": absent}
        finally:
            self.selector.close()
            self.process.stdout.close()
            self.stderr.close()


def normalized_profile(value: object) -> object:
    """Remove only schema-defined null defaults, retaining every access rule."""
    if not isinstance(value, dict):
        return value
    result = dict(value)
    for key in ("description", "extends", "workspace_roots"):
        if key in result and result[key] is None:
            del result[key]
    if isinstance(result.get("filesystem"), dict):
        result["filesystem"] = dict(result["filesystem"])
        if result["filesystem"].get("glob_scan_max_depth", 0) is None:
            del result["filesystem"]["glob_scan_max_depth"]
    if isinstance(result.get("network"), dict):
        result["network"] = dict(result["network"])
        for key in ("allow_local_binding", "allow_upstream_proxy", "dangerously_allow_all_unix_sockets",
                    "dangerously_allow_non_loopback_proxy", "domains", "enable_socks5", "enable_socks5_udp",
                    "mitm", "mode", "proxy_url", "socks_url", "unix_sockets"):
            if key in result["network"] and result["network"][key] is None:
                del result["network"][key]
    return result


def policy_observation(response: dict, profile_name: str, expected: dict) -> dict:
    """Persist only policy fields and layer identities, never general user config."""
    config = response.get("config", {})
    layers = response.get("layers")
    layer_findings = []
    legacy = []
    if not isinstance(layers, list):
        raise HostRefusal("config/read did not return layers")
    for index, layer in enumerate(layers):
        body = layer.get("config", {})
        if "sandbox_mode" in body:
            legacy.append(index)
        layer_findings.append({"index": index, "name": layer.get("name"),
                               "version": layer.get("version"), "disabledReason": layer.get("disabledReason"),
                               "keys": sorted(body), "sandbox_mode_present": "sandbox_mode" in body})
    profiles = config.get("permissions", {})
    actual = profiles.get(profile_name) if isinstance(profiles, dict) else None
    mcp = config.get("mcp_servers", {})
    features = config.get("features", {})
    reasons = []
    if legacy or config.get("sandbox_mode") is not None:
        reasons.append("legacy sandbox_mode present")
    if normalized_profile(actual) != expected:
        reasons.append("effective named profile differs from frozen profile")
    if isinstance(actual, dict) and actual.get("extends") is not None:
        reasons.append("profile inheritance is not allowed")
    if config.get("default_permissions") != profile_name:
        reasons.append("effective default_permissions differs")
    if not isinstance(mcp, dict) or set(mcp) != set(EXPECTED_MCP):
        reasons.append("MCP inventory differs")
    elif any(mcp[name].get("enabled") is not False for name in EXPECTED_MCP):
        reasons.append("MCP capability is not explicitly disabled")
    if any(features.get(name) is not False for name in DISABLED_FEATURES):
        reasons.append("feature override is not effective")
    if config.get("web_search") != "disabled":
        reasons.append("web search is not disabled")
    plugins = config.get("plugins")
    enabled_plugins = [key for key, value in plugins.items()
                       if not isinstance(value, dict) or value.get("enabled") is not False] if isinstance(plugins, dict) else []
    if plugins is not None and not isinstance(plugins, dict):
        reasons.append("plugin configuration is not observable")
    if enabled_plugins:
        reasons.append("configured plugins are not explicitly disabled")
    return {"layers": layer_findings, "effective_keys": sorted(config),
            "enabled_plugin_count": len(enabled_plugins),
            "plugin_configuration_present": plugins is not None,
            "legacy_effective_value": config.get("sandbox_mode"),
            "normalized_profile_sha256": digest(canonical(normalized_profile(actual))),
            "profile": actual, "profile_sha256": digest(canonical(actual)),
            "default_permissions": config.get("default_permissions"),
            "legacy_layers": legacy, "mcp_enabled": {k: v.get("enabled") for k, v in mcp.items()} if isinstance(mcp, dict) else None,
            "feature_values": {k: features.get(k) for k in DISABLED_FEATURES},
            "web_search": config.get("web_search"), "reasons": reasons}


def preflight(spec_path: Path) -> int:
    spec = json.loads(spec_path.read_bytes())
    run = Path(spec["run"])
    run.mkdir(mode=0o700, parents=False, exist_ok=False)
    deadline = time.monotonic() + min(spec["seconds"], 300) - 20
    result: dict = {"kind": "preflight", "status": "unverified", "model_turns": 0,
                   "spec_sha256": digest(spec_path.read_bytes()), "started": time.time()}
    client = None
    try:
        binary = Path(spec["codex"]).resolve(strict=True)
        if digest(binary.read_bytes()) != spec["codex_sha256"]:
            raise HostRefusal("Codex executable identity changed")
        cwd = Path(spec["worker"]).resolve(strict=True)
        if any(os.environ.get(k) for k in ("OPENAI_API_KEY", "CODEX_API_KEY", "OPENAI_BASE_URL", "CODEX_HOME")):
            raise HostRefusal("Authentication or configuration override present")
        profile = spec["profile"]
        name = "colvia-u2-worker"
        argv = [str(binary)]
        # Each override layer must define a valid transport, and later layers
        # merge fields. Keep the known public HTTP transport's kind; replace
        # stdio commands with an inert executable. Every server stays disabled.
        for server in EXPECTED_MCP:
            transport = 'url="https://developers.openai.com/mcp"' if server == "openaiDeveloperDocs" else 'command="/usr/bin/false"'
            argv += ["-c", f'mcp_servers.{server}={{' + transport + ',enabled=false}']
        for key, value in [("features." + n, "false") for n in DISABLED_FEATURES] + [("web_search", '"disabled"'), ("default_permissions", json.dumps(name))]:
            argv += ["-c", key + "=" + value]
        plugins = spec.get("disabled_plugin_ids", [])
        if not isinstance(plugins, list) or not all(isinstance(x, str) and x for x in plugins) or len(set(plugins)) != len(plugins):
            raise HostRefusal("Invalid frozen plugin inventory")
        if plugins:
            argv += ["-c", "plugins={" + ",".join(json.dumps(x) + "={enabled=false}" for x in plugins) + "}"]
        # Keep literal path keys inside one TOML value. CLI dotted-key parsing does
        # not preserve a quoted path containing dots as one component.
        filesystem = ",".join(json.dumps(path) + "=" + json.dumps(access)
                              for path, access in profile["filesystem"].items())
        profile_toml = "{filesystem={" + filesystem + "},network={enabled=false}}"
        argv += ["-c", f"permissions.{name}=" + profile_toml,
                 "app-server", "--listen", "stdio://"]
        client = StdioClient(argv, cwd, run, deadline)
        init = client.request("initialize", {"clientInfo": {"name": "colvia_u2_qualification", "version": "0.1"}, "capabilities": {"experimentalApi": True}})
        result["initialize_keys"] = sorted(init)
        client.send({"method": "initialized", "params": {}})
        account = client.request("account/read", {"refreshToken": False})
        # The account object may contain an email. Never persist it.
        result["auth"] = {"type": (account.get("account") or {}).get("type"),
                          "requiresOpenaiAuth": account.get("requiresOpenaiAuth")}
        if result["auth"]["type"] != "chatgpt":
            raise HostRefusal("Expected ChatGPT subscription authentication")
        config = client.request("config/read", {"cwd": str(cwd), "includeLayers": True})
        result["policy"] = policy_observation(config, name, profile)
        requirements = client.request("configRequirements/read", {})
        result["requirements_present"] = requirements.get("requirements") is not None
        result["requirements_keys"] = sorted((requirements.get("requirements") or {}))
        if result["policy"]["reasons"]:
            raise HostRefusal("Effective configuration did not satisfy admission")
        inventory = client.request("plugin/installed", {"cwds": [str(cwd)]})
        plugins = [plugin for marketplace in inventory.get("marketplaces", [])
                   for plugin in marketplace.get("plugins", [])]
        result["plugin_inventory"] = {"installed_count": sum(p.get("installed") is True for p in plugins),
                                      "enabled_installed_count": sum(p.get("installed") is True and p.get("enabled") is True for p in plugins),
                                      "load_error_count": len(inventory.get("marketplaceLoadErrors", []))}
        if result["plugin_inventory"]["enabled_installed_count"] or result["plugin_inventory"]["load_error_count"]:
            raise HostRefusal("Plugin inventory is active or unavailable after disabled config")
        dynamic = [
            {"type": "function", "name": "u2_verify", "description": "Request one fixed verifier.",
             "inputSchema": {"type": "object", "properties": {"verifier_id": {"enum": ["DOC-LINKS", "DOC-GFM", "DOC-CLAIMS"]}}, "required": ["verifier_id"], "additionalProperties": False}},
            {"type": "function", "name": "u2_accept", "description": "Request the one sealed acceptance handle.",
             "inputSchema": {"type": "object", "properties": {"handle": {"type": "string"}}, "required": ["handle"], "additionalProperties": False}}]
        thread = client.request("thread/start", {"model": "gpt-6-astra", "allowProviderModelFallback": False,
                    "approvalPolicy": "never", "permissions": name, "cwd": str(cwd),
                    "runtimeWorkspaceRoots": [str(cwd)], "environments": [], "ephemeral": True,
                    "dynamicTools": dynamic, "config": {"model_reasoning_effort": "xhigh"}})
        result["thread_observation"] = {key: thread.get(key) for key in ("model", "modelProvider", "reasoningEffort", "approvalPolicy", "activePermissionProfile", "instructionSources", "disabledPluginIds", "runtimeWorkspaceRoots")}
        result["thread_observation"].update({"response_keys": sorted(thread), "thread_keys": sorted(thread.get("thread", {})),
                                           "extra_keys": sorted((thread.get("thread", {}).get("extra") or {})),
                                           "ephemeral": thread.get("thread", {}).get("ephemeral"),
                                           "environments": thread.get("thread", {}).get("environments")})
        if thread.get("model") != "gpt-6-astra" or thread.get("approvalPolicy") != "never" or (thread.get("activePermissionProfile") or {}).get("id") != name:
            raise HostRefusal("Thread identity or active profile differs")
        mcp = client.request("mcpServerStatus/list", {"threadId": thread["thread"]["id"], "detail": "toolsAndAuthOnly", "limit": 100})
        result["thread_mcp_inventory"] = {"server_count": len(mcp.get("data", [])), "has_more": mcp.get("nextCursor") is not None}
        # An empty MCP catalog does not prove which native tools the model receives.
        # This preflight has no model turn route and never treats configured tools
        # or a model's own inventory claim as the actual runtime catalog.
        result["status"] = "config-observed-host-unqualified"
        result["remaining"] = ["complete native tool inventory before first turn", "instruction-source allowlist", "actual enforcement canaries"]
    except Exception as exc:
        result["status"] = "refused"
        result["failure"] = {"type": type(exc).__name__, "message": str(exc)}
    finally:
        if client is not None:
            try:
                client.close()
            except Exception as exc:
                result["cleanup_error"] = type(exc).__name__
            result["cleanup"] = client.cleanup
            result["rpc_observations"] = client.events
        result["finished"] = time.time()
        durable_json(run / "result.json", result)
    print(json.dumps({k: result.get(k) for k in ("status", "failure", "model_turns", "cleanup")}, ensure_ascii=False))
    return 2  # Configuration observations alone never qualify a host.


PHASE_CAPS = {"clock": (2, 2, 2), "synthetic": (2, 4, 12), "h10": (2, 2, 40)}


JOURNAL_KINDS = frozenset(("genesis start runtime-entered control thread thread-bound turn generation dispatch host-dispatch "
    "proxy-start offline-start offline-thread offline-turn build correction review pause resume stop checkpoint seal "
    "prepare-accept authority-apply recovery-approved recovery-apply process-ended input verifier worker-result stage").split())


DIAGNOSTIC_POLICY = {"version":1,"kind":"manifest-identity","model_turns":0,"generation":0,"dispatch":0,"control_endpoints":["models","accounts"]}


DIAGNOSTIC_ALLOCATIONS = {int(k): v for k, v in json.loads('{"21":{"approval_plan_sha256":"bc51e2f4bb8c2a53f4ef43d15ee226ad007fe32cdef000b35d075b160b0a7b86","owner_message_id":"owner-mcp49-diagnostic-only-source38","parent":{"anchor_sha256":"9f8e2ca6f455aa1d1a839c271ec7e9eaef64d5b3ddd303391045c1a94efc7586","journal_sha256":"36879e8219379474fb76fd6d7957e354cb2858d77ab3019601452da1073c6c6f","last_seq":10,"last_sha256":"fa076f26fa05847992495e53e4a8ab69d57cbea44f655962ae6b385104575f22"},"parent_counts":{"authority-apply":0,"control":15,"dispatch":0,"generation":0,"host-dispatch":0,"proxy-start":13,"recovery-apply":0,"runtime-entered":11,"seal":0,"start":11,"thread":5,"thread-bound":4,"turn":0},"parent_rows":11,"parent_starts":11,"parent_version":20,"prior_attempts":{"build":26,"correction":38,"offline-start":59,"offline-thread":58,"offline-turn":33,"proxy-start":13,"review":3},"prior_cap_ms":139114000,"proxy_start":"s4-14","proxy_total":14,"run_deadline_ms":1792898287084,"source":38,"start":"clock-12","total_cap_ms":145045641,"version":21},"22":{"approval_plan_sha256":"02483264fe5f98b47f8de914f9b9d16fba81e1a569b32f408c1e3d11c5c48df0","owner_message_id":"owner-mcp51-diagnostic-only-source40","parent":{"anchor_sha256":"0d3ec4ae05f7a105e93216fdd223820690657be0678ebb8681037f622f74ba8a","journal_sha256":"432ba6a259e7165c221e2acb5203ba0e00eef8cafd765adfc1ef7cc58cf4fbac","last_seq":6,"last_sha256":"2bc963d16c493a28f3b74e3c56f594d148b82f75c5ae6e71ef5692c742f2f561"},"parent_counts":{"authority-apply":0,"control":16,"dispatch":0,"generation":0,"host-dispatch":0,"proxy-start":14,"recovery-apply":0,"runtime-entered":12,"seal":0,"start":12,"thread":5,"thread-bound":4,"turn":0},"parent_rows":7,"parent_starts":12,"parent_version":21,"prior_attempts":{"build":28,"correction":40,"offline-start":63,"offline-thread":58,"offline-turn":33,"proxy-start":14,"review":3},"prior_cap_ms":145045641,"proxy_start":"s4-15","proxy_total":15,"run_deadline_ms":1792903091997,"source":40,"start":"clock-13","total_cap_ms":147497229,"version":22},"23":{"approval_plan_sha256":"ff6278bd1c854ba436181160d197276618af67b4f3ff3122fbc61661bb57925d","owner_message_id":"owner-mcp54-291161300-diagnostic-only-source42","parent":{"anchor_sha256":"ef719f989689dc56f8aa9e5163423bb38f25badb117541b23758470486a73dca","journal_sha256":"cfd88ba25d37699278174c53aa070f048b48e4715af3627334e04a9855079728","last_seq":10,"last_sha256":"8fab13f84df7c9d8e16ca78e9af51dbafde17f560d464eeee6aa53bb8b04eff6"},"parent_counts":{"authority-apply":0,"control":18,"dispatch":0,"generation":0,"host-dispatch":0,"proxy-start":15,"recovery-apply":0,"runtime-entered":13,"seal":0,"start":13,"thread":6,"thread-bound":5,"turn":0},"parent_rows":11,"parent_starts":13,"parent_version":22,"prior_attempts":{"build":30,"correction":42,"offline-start":67,"offline-thread":59,"offline-turn":33,"proxy-start":15,"review":3},"prior_cap_ms":147497229,"proxy_start":"s4-16","proxy_total":16,"run_deadline_ms":1792909672235,"source":42,"start":"clock-14","total_cap_ms":147497229,"version":23}}').items()}


DIAGNOSTIC_PRIOR = DIAGNOSTIC_ALLOCATIONS[21]["prior_attempts"]


DIAGNOSTIC_PARENT = DIAGNOSTIC_ALLOCATIONS[21]["parent"]


def diagnostic_allocation(version):
    require(type(version) is int and version in DIAGNOSTIC_ALLOCATIONS,"diagnostic allocation version")
    return DIAGNOSTIC_ALLOCATIONS[version]


def diagnostic_anchor_fields(anchor):
    cfg=diagnostic_allocation(anchor.get("version"))
    require(set(anchor)=={"version","approval","work","candidate","source_identity","total_deadline_ms","origin_wall_ms","origin_monotonic_ns","input_identity","recovery","activity_clock","launch_mode","launch_contract_sha256","approval_wall_ms","run_deadline_ms","direct_tool_policy","diagnostic_policy"},"diagnostic anchor fields")
    require(type(anchor["version"]) is int and anchor["version"] in (21,22,23) and anchor["diagnostic_policy"]==DIAGNOSTIC_POLICY and anchor["activity_clock"]=="mach_continuous_time_ns" and anchor["launch_mode"]=="trusted-native-runtime","diagnostic mode binding")
    for key in ("total_deadline_ms","origin_wall_ms","origin_monotonic_ns","approval_wall_ms","run_deadline_ms"):
        require(type(anchor[key]) is int and anchor[key]>0,"diagnostic clock type")
    require(anchor["approval_wall_ms"]<=anchor["origin_wall_ms"]<anchor["run_deadline_ms"]==cfg["run_deadline_ms"],"diagnostic deadline")
    for key in ("approval","work","candidate","source_identity","input_identity","launch_contract_sha256"):
        require(isinstance(anchor[key],str) and anchor[key],"diagnostic identity")
    require(anchor["direct_tool_policy"]=={"version":1,"mode":"direct","model":"gpt-6-astra","profiles":["clock","u2"],"approval":anchor["approval"]},"diagnostic direct policy")


def diagnostic_budget_state(budget,rows,now):
    a=budget.anchor;diagnostic_anchor_fields(a);r=a["recovery"];cfg=diagnostic_allocation(a["version"])
    require(set(r)=={"owner_message_id","predecessor","accounting","checkpoint","resume_authorization","carry_active_ms","total_cap_ms","uncertainty_reserve_ms","closeout_reserve_ms","prior_attempts","transition"},"diagnostic recovery fields")
    def bound(ref):
        require(set(ref)=={"path","sha256"},"diagnostic reference")
        raw=control_read(ref["path"]);require(digest(raw)==ref["sha256"],"diagnostic input drift")
        v=json.loads(raw,object_pairs_hook=reject_duplicate_keys);require(canonical(v)==raw,"diagnostic canonical input");return v
    parent=r["predecessor"];require(set(parent)==set(cfg["parent"])|{"directory"} and all(parent[k]==v for k,v in cfg["parent"].items()),"diagnostic exact parent")
    old,prior=Budget.inspect_for_clock_recovery(parent["directory"],parent["anchor_sha256"])
    require(old.directory!=budget.directory and digest(control_read(old.path))==parent["journal_sha256"] and old.anchor["version"]==cfg["parent_version"] and prior["stopped"] and len(prior["rows"])==cfg["parent_rows"] and prior["prev"]==parent["last_sha256"],"diagnostic stopped predecessor")
    pc=prior["counts"];require(all(pc.get(k,0)==v for k,v in cfg["parent_counts"].items()),"diagnostic inherited effects")
    require(type(r["carry_active_ms"]) is int and cfg["prior_cap_ms"]-(old.anchor["total_deadline_ms"]-prior["rows"][-1]["event"]["at_ms"])<=r["carry_active_ms"]<=cfg["total_cap_ms"],"diagnostic no usage refund")
    require(r["total_cap_ms"]==cfg["total_cap_ms"] and r["uncertainty_reserve_ms"]==858141 and r["closeout_reserve_ms"]==1200000 and a["total_deadline_ms"]==a["origin_wall_ms"]+cfg["total_cap_ms"]-r["carry_active_ms"] and r["prior_attempts"]==cfg["prior_attempts"],"diagnostic fixed caps")
    require(bound(r["accounting"])=={"version":1,"approval":a["approval"],"work":a["work"],"active_ms":r["carry_active_ms"],"total_cap_ms":cfg["total_cap_ms"],"uncertainty_reserve_ms":858141,"closeout_reserve_ms":1200000,"prior_attempts":cfg["prior_attempts"]},"diagnostic accounting")
    cp=bound(r["checkpoint"]);require(cp=={"version":1,"approval":a["approval"],"work":a["work"],"input_identity":old.anchor["input_identity"],"journal_seq":cfg["parent"]["last_seq"],"journal_sha256":parent["last_sha256"],"sealed":False,"pending":False,"process_ids":[]},"diagnostic checkpoint")
    auth=bound(r["resume_authorization"])
    require(set(auth)=={"version","owner_message_id","approval_plan_sha256","failure_evidence","diagnostic_policy","allowed_next_start","launch_contract_sha256"} and auth["version"]==1 and auth["owner_message_id"]==r["owner_message_id"]==cfg["owner_message_id"] and auth["approval_plan_sha256"]==cfg["approval_plan_sha256"] and auth["diagnostic_policy"]==DIAGNOSTIC_POLICY and auth["allowed_next_start"]==cfg["start"] and auth["launch_contract_sha256"]==a["launch_contract_sha256"],"diagnostic Owner binding")
    evidence=bound(auth["failure_evidence"]);require(evidence==cfg["parent"],"diagnostic failure evidence")
    require(a["approval"]==old.anchor["approval"] and a["work"]==old.anchor["work"] and r["transition"]=={**{"old_"+k:old.anchor[k] for k in ("candidate","source_identity","input_identity")},**{"new_"+k:a[k] for k in ("candidate","source_identity","input_identity")}},"diagnostic transition")
    counts=pc.copy()
    for k,v in cfg["prior_attempts"].items():require(v>=counts.get(k,0),"diagnostic attempt refund");counts[k]=v
    counts["correction-source"]=cfg["source"];counts["correction-content"]=0
    limits={"genesis":1,"proxy-start":1,"start":1,"runtime-entered":1,"control":2,"thread":1,"thread-bound":1,"input":1,"stop":1,"process-ended":1}
    used={};prev="";last=prior["rows"][-1]["event"]["at_ms"];stopped=False;thread_request=None;thread_id=None;endpoints=set();events=[]
    require(0<len(rows)<32,"diagnostic bounded journal")
    for i,row in enumerate(rows):
        require(set(row)=={"event","sha256"},"diagnostic row");e=row["event"]
        require(set(e)=={"seq","prev","approval","work","candidate","phase","start","kind","subject","at_ms"} and type(e["seq"]) is int and e["seq"]==i and e["prev"]==prev and row["sha256"]==digest(wire_bytes(e)) and all(e[k]==a[k] for k in ("approval","work","candidate")),"diagnostic journal chain")
        kind=e["kind"];sub=e["subject"];require(kind in limits and isinstance(sub,dict) and type(e["at_ms"]) is int and last<=e["at_ms"]<=now,"diagnostic effect/time")
        used[kind]=used.get(kind,0)+1;require(used[kind]<=limits[kind] and (not stopped or kind=="process-ended"),"diagnostic cap/stop")
        if i==0:require(kind=="genesis" and e["phase"]==e["start"]=="controller" and sub=={"anchor_sha256":budget.anchor_sha256},"diagnostic genesis")
        else:require(kind!="genesis","diagnostic repeated genesis")
        if kind=="proxy-start":require(e["phase"]==e["start"]=="controller" and sub=={"slot":"s4","start_id":cfg["proxy_start"]},"diagnostic proxy")
        if kind in ("start","runtime-entered","control","thread","thread-bound","input","process-ended"):
            require(e["phase"]=="clock" and e["start"]==cfg["start"],"diagnostic start binding")
            require(used.get("start",0)==1 and used.get("proxy-start",0)==1,"diagnostic start order")
        if kind=="start":require(sub.get("execution_binding",{}).get("diagnostic_policy")==DIAGNOSTIC_POLICY,"diagnostic start policy")
        if kind=="runtime-entered":require(sub=={"start":cfg["start"]},"diagnostic runtime entry")
        if kind in ("control","thread","thread-bound","input"):require(used.get("runtime-entered")==1,"diagnostic before runtime")
        if kind=="control":require(set(sub)=={"endpoint"} and sub["endpoint"] in ("models","accounts") and sub["endpoint"] not in endpoints,"diagnostic control retry");endpoints.add(sub["endpoint"])
        if kind=="thread":thread_request=sub.get("request");require(thread_request is not None,"diagnostic thread request")
        if kind=="thread-bound":require(thread_request is not None and sub.get("request")==thread_request and isinstance(sub.get("thread"),str) and bool(sub["thread"]),"diagnostic thread binding");thread_id=sub["thread"]
        if kind=="input":require(thread_id is not None and set(sub)=={"plan","input_sha256","manifest_sha256"},"diagnostic input order")
        if kind=="stop":require(set(sub)=={"reason"} and isinstance(sub["reason"],str),"diagnostic stop");stopped=True
        if kind=="process-ended":require(stopped and sub.get("process_group_absent") is True,"diagnostic process close")
        counts[kind]=counts.get(kind,0)+1;events.append(e);prev=row["sha256"];last=e["at_ms"]
    return {"events":events,"history_events":prior["history_events"]+events,"rows":rows,"prev":prev,"counts":counts,"excluded_ms":0,"paused_at":None,"stopped":stopped,"active_ms":now,"remaining_ms":min(a["total_deadline_ms"],a["run_deadline_ms"])-now}


CLOCK_POLICY = {"version":1,"kind":"clock-single-turn","model_turns":1,"generation":2,"dispatch":1,"control_endpoints":["models","accounts"]}


CLOCK_ALLOCATIONS = {int(k): v for k, v in json.loads('{"24":{"approval_plan_sha256":"3f369d9c567fa4aedaa50ab1cda0d1e919ba4c3debf695b4b90c1f826d7a72e2","owner_message_id":"owner-mcp55-207112262-clock-source43","parent":{"anchor_sha256":"57ceea377c652c83b75c92dcdd7bb33b502abff1e12b833cf81c1fcf243a31ca","journal_sha256":"aacbf2002e55dc4174c62461ec4e76fd47ff9c4e568c44ee6a5a57018011fb98","last_seq":10,"last_sha256":"40b0d86e38d2e985dfdf9f8435527cb6160759b6a3692c46ecc6f8b01ae1dcb8"},"parent_counts":{"authority-apply":0,"control":20,"dispatch":0,"generation":0,"host-dispatch":0,"proxy-start":16,"recovery-apply":0,"runtime-entered":14,"seal":0,"start":14,"thread":7,"thread-bound":6,"turn":0},"parent_rows":11,"parent_starts":14,"parent_version":23,"prior_attempts":{"build":31,"correction":43,"offline-start":70,"offline-thread":59,"offline-turn":33,"proxy-start":16,"review":3},"prior_cap_ms":147497229,"proxy_start":"s4-17","proxy_total":17,"run_deadline_ms":1792915552902,"source":43,"start":"clock-15","total_cap_ms":149297229,"version":24},"25":{"approval_plan_sha256":"36276e2d1f83ccf0b88da9cdd7c3fbce4766ee54f3a6812bfb6e3c64d7a9e56a","owner_message_id":"owner-mcp56-58124524-clock-source44","parent":{"anchor_sha256":"d892bbac56b17d9edbafe81a9b35e8fb271cf2aaf0d638fc28a8a5050ff1ca30","journal_sha256":"d93d9383ae241718caef983ec3bdaedf55b15f2e9b18389d8e883303b9b06d60","last_seq":6,"last_sha256":"485f8ea5fbc1c543cecb7bb34b09ed7b3a6227f318715e1a0909d647229ae413"},"parent_counts":{"authority-apply":0,"control":21,"dispatch":0,"generation":0,"host-dispatch":0,"proxy-start":17,"recovery-apply":0,"runtime-entered":15,"seal":0,"start":15,"thread":7,"thread-bound":6,"turn":0},"parent_rows":7,"parent_starts":15,"parent_version":24,"prior_attempts":{"build":32,"correction":44,"offline-start":72,"offline-thread":59,"offline-turn":33,"proxy-start":17,"review":3},"prior_cap_ms":149297229,"proxy_start":"s4-18","proxy_total":18,"run_deadline_ms":1792915950648,"source":44,"start":"clock-16","total_cap_ms":149297229,"version":25},"26":{"approval_plan_sha256":"10ed5ab7c8995a4effd0320fc7d8ed8437cf38d9a105b5f7c653f129095af790","owner_message_id":"owner-mcp58-984820975-clock-source48","parent":{"anchor_sha256":"d01d820a3ac331620a4ff15949a85b57d977de62e1d5ba4369d91df8d8b42cb7","journal_sha256":"3def95249851addadd6ff09c2bd26be123979fe13a30dbed300fb9b248221e6d","last_seq":11,"last_sha256":"858525c145768fd610c7fbe1426d9cb23d2af297fb306369b231a15648bbba1e"},"parent_counts":{"authority-apply":0,"control":23,"dispatch":0,"generation":0,"host-dispatch":0,"proxy-start":18,"recovery-apply":0,"runtime-entered":16,"seal":0,"start":16,"thread":8,"thread-bound":7,"turn":1},"parent_rows":12,"parent_starts":16,"parent_version":25,"prior_attempts":{"build":35,"correction":48,"offline-start":75,"offline-thread":59,"offline-turn":33,"proxy-start":18,"review":3},"prior_cap_ms":149297229,"proxy_start":"s4-19","proxy_total":19,"run_deadline_ms":1792922543850,"source":48,"start":"clock-17","total_cap_ms":153497229,"version":26},"27":{"approval_plan_sha256":"b196ccda65278ae5fa1204b64f34955b998eebc79975777e2b1b1d3be5f65f66","owner_message_id":"owner-mcp59-984820975-clock-source49","parent":{"anchor_sha256":"2cb67bf37f83112fbf5804763fb6bd81c242486b4466cc53c9b8ef263982164e","journal_sha256":"2a38eb6b02f894bf3645306a901f6216f400c8c4b370bf311dcb9625b9439aea","last_seq":12,"last_sha256":"3dad74fc3c76fb4fe72e7e8b5a43883deecb095e555b5f3701339be5322f4df5"},"parent_counts":{"authority-apply":0,"control":25,"dispatch":0,"generation":1,"host-dispatch":0,"proxy-start":19,"recovery-apply":0,"runtime-entered":17,"seal":0,"start":17,"thread":9,"thread-bound":8,"turn":2},"parent_rows":13,"parent_starts":17,"parent_version":26,"prior_attempts":{"build":36,"correction":49,"offline-start":78,"offline-thread":59,"offline-turn":33,"proxy-start":19,"review":3},"prior_cap_ms":153497229,"proxy_start":"s4-20","proxy_total":20,"run_deadline_ms":1792922543850,"source":49,"start":"clock-18","total_cap_ms":153497229,"version":27},"28":{"approval_plan_sha256":"689f81f25e0866c8bf54f1e67bb42f8e3c59e4b25ad358c891a1f526a4941c4b","owner_message_id":"owner-mcp60-984820975-clock-source50","parent":{"anchor_sha256":"4cb3388d54ea43b67a79a308d203f42aa32fa6a4daa0011198255f20a84775ff","journal_sha256":"3f4f9ec0076af1528004a7a44776de1bce36bf2cf5106c68b9e9cdbbce8a58ba","last_seq":12,"last_sha256":"7bf4c67015d01ebac7d0b7d93352fc843d0c38684fe5f7b837fed33c4c94cdb9"},"parent_counts":{"authority-apply":0,"control":27,"dispatch":0,"generation":2,"host-dispatch":0,"proxy-start":20,"recovery-apply":0,"runtime-entered":18,"seal":0,"start":18,"thread":10,"thread-bound":9,"turn":3},"parent_rows":13,"parent_starts":18,"parent_version":27,"prior_attempts":{"build":37,"correction":50,"offline-start":81,"offline-thread":59,"offline-turn":33,"proxy-start":20,"review":3},"prior_cap_ms":153497229,"proxy_start":"s4-21","proxy_total":21,"run_deadline_ms":1792922543850,"source":50,"start":"clock-19","total_cap_ms":153497229,"version":28},"29":{"approval_plan_sha256":"35cdd261796d55388ea3370799842e3c35d1966ad587fdd21d6bf9ad735c979b","owner_message_id":"owner-mcp61-984820975-clock-source51","parent":{"anchor_sha256":"0cdf21c1e63f789e70bc54a24379853ff356b614956ff00677248dd5028ea917","journal_sha256":"c1710a9fe79357be2a45e84ab1cbaf9c381c390d471db3d2b58003aec1395974","last_seq":12,"last_sha256":"ff0c5a1150aa39934f7449acb9c99701b228ddb18e5c49cda77c6cf49096a29b"},"parent_counts":{"authority-apply":0,"control":29,"dispatch":0,"generation":3,"host-dispatch":0,"proxy-start":21,"recovery-apply":0,"runtime-entered":19,"seal":0,"start":19,"thread":11,"thread-bound":10,"turn":4},"parent_rows":13,"parent_starts":19,"parent_version":28,"prior_attempts":{"build":38,"correction":51,"offline-start":85,"offline-thread":59,"offline-turn":33,"proxy-start":21,"review":3},"prior_cap_ms":153497229,"proxy_start":"s4-22","proxy_total":22,"run_deadline_ms":1792922543850,"source":51,"start":"clock-20","total_cap_ms":153497229,"version":29},"30":{"approval_plan_sha256":"411a047fe31d99a9c657002bd4f0ed1827b8379e8e4261d5f336317ef2f8ae83","owner_message_id":"owner-mcp62-984820975-clock-source52","parent":{"anchor_sha256":"2c8a37d9dc10c72f96dd975c1c1f02f154d775eebe504d4eadcc3f04eb6a7846","journal_sha256":"bb87c79a94329a114f30818df992ef1d581c8edf2b9c2da96650981807502efb","last_seq":12,"last_sha256":"58ffed3d2cc7d5fba57f08a4492d115aa55bff3657b645897d633e27e844ac62"},"parent_counts":{"authority-apply":0,"control":31,"dispatch":0,"generation":4,"host-dispatch":0,"proxy-start":22,"recovery-apply":0,"runtime-entered":20,"seal":0,"start":20,"thread":12,"thread-bound":11,"turn":5},"parent_rows":13,"parent_starts":20,"parent_version":29,"prior_attempts":{"build":39,"correction":52,"offline-start":89,"offline-thread":59,"offline-turn":33,"proxy-start":22,"review":3},"prior_cap_ms":153497229,"proxy_start":"s4-23","proxy_total":23,"run_deadline_ms":1792922543850,"source":52,"start":"clock-21","total_cap_ms":153497229,"version":30}}').items()}


def clock_allocation(version):
    require(type(version) is int and version in CLOCK_ALLOCATIONS,"clock allocation version")
    return CLOCK_ALLOCATIONS[version]


def clock_anchor_fields(anchor):
    cfg=clock_allocation(anchor["version"])
    require(set(anchor)=={"version","approval","work","candidate","source_identity","total_deadline_ms","origin_wall_ms","origin_monotonic_ns","input_identity","recovery","activity_clock","launch_mode","launch_contract_sha256","approval_wall_ms","run_deadline_ms","direct_tool_policy"},"diagnostic anchor fields")
    require(type(anchor["version"]) is int and anchor["version"] in (24,25,26,27,28,29,30) and anchor["activity_clock"]=="mach_continuous_time_ns" and anchor["launch_mode"]=="trusted-native-runtime","diagnostic mode binding")
    for key in ("total_deadline_ms","origin_wall_ms","origin_monotonic_ns","approval_wall_ms","run_deadline_ms"):
        require(type(anchor[key]) is int and anchor[key]>0,"diagnostic clock type")
    require(anchor["approval_wall_ms"]<=anchor["origin_wall_ms"]<anchor["run_deadline_ms"]==cfg["run_deadline_ms"],"diagnostic deadline")
    for key in ("approval","work","candidate","source_identity","input_identity","launch_contract_sha256"):
        require(isinstance(anchor[key],str) and anchor[key],"diagnostic identity")
    require(anchor["direct_tool_policy"]=={"version":1,"mode":"direct","model":"gpt-6-astra","profiles":["clock","u2"],"approval":anchor["approval"]},"diagnostic direct policy")


def clock_budget_state(budget,rows,now):
    a=budget.anchor;clock_anchor_fields(a);r=a["recovery"];cfg=clock_allocation(a["version"])
    require(set(r)=={"owner_message_id","predecessor","accounting","checkpoint","resume_authorization","carry_active_ms","total_cap_ms","uncertainty_reserve_ms","closeout_reserve_ms","prior_attempts","transition"},"diagnostic recovery fields")
    def bound(ref):
        require(set(ref)=={"path","sha256"},"diagnostic reference")
        raw=control_read(ref["path"]);require(digest(raw)==ref["sha256"],"diagnostic input drift")
        v=json.loads(raw,object_pairs_hook=reject_duplicate_keys);require(canonical(v)==raw,"diagnostic canonical input");return v
    parent=r["predecessor"];require(set(parent)==set(cfg["parent"])|{"directory"} and all(parent[k]==v for k,v in cfg["parent"].items()),"diagnostic exact parent")
    old,prior=Budget.inspect_for_clock_recovery(parent["directory"],parent["anchor_sha256"])
    require(old.directory!=budget.directory and digest(control_read(old.path))==parent["journal_sha256"] and old.anchor["version"]==cfg["parent_version"] and prior["stopped"] and len(prior["rows"])==cfg["parent_rows"] and prior["prev"]==parent["last_sha256"],"diagnostic stopped predecessor")
    pc=prior["counts"];require(all(pc.get(k,0)==v for k,v in cfg["parent_counts"].items()),"diagnostic inherited effects")
    require(type(r["carry_active_ms"]) is int and cfg["prior_cap_ms"]-(old.anchor["total_deadline_ms"]-prior["rows"][-1]["event"]["at_ms"])<=r["carry_active_ms"]<=cfg["total_cap_ms"],"diagnostic no usage refund")
    require(r["total_cap_ms"]==cfg["total_cap_ms"] and r["uncertainty_reserve_ms"]==858141 and r["closeout_reserve_ms"]==1200000 and a["total_deadline_ms"]==a["origin_wall_ms"]+cfg["total_cap_ms"]-r["carry_active_ms"] and r["prior_attempts"]==cfg["prior_attempts"],"diagnostic fixed caps")
    require(bound(r["accounting"])=={"version":1,"approval":a["approval"],"work":a["work"],"active_ms":r["carry_active_ms"],"total_cap_ms":cfg["total_cap_ms"],"uncertainty_reserve_ms":858141,"closeout_reserve_ms":1200000,"prior_attempts":cfg["prior_attempts"]},"diagnostic accounting")
    cp=bound(r["checkpoint"]);require(cp=={"version":1,"approval":a["approval"],"work":a["work"],"input_identity":old.anchor["input_identity"],"journal_seq":cfg["parent"]["last_seq"],"journal_sha256":parent["last_sha256"],"sealed":False,"pending":False,"process_ids":[]},"diagnostic checkpoint")
    auth=bound(r["resume_authorization"])
    require(set(auth)=={"version","owner_message_id","approval_plan_sha256","failure_evidence","clock_policy","allowed_next_start","launch_contract_sha256"} and auth["version"]==1 and auth["owner_message_id"]==r["owner_message_id"]==cfg["owner_message_id"] and auth["approval_plan_sha256"]==cfg["approval_plan_sha256"] and auth["clock_policy"]==CLOCK_POLICY and auth["allowed_next_start"]==cfg["start"] and auth["launch_contract_sha256"]==a["launch_contract_sha256"],"diagnostic Owner binding")
    evidence=bound(auth["failure_evidence"]);require(evidence==cfg["parent"],"diagnostic failure evidence")
    require(a["approval"]==old.anchor["approval"] and a["work"]==old.anchor["work"] and r["transition"]=={**{"old_"+k:old.anchor[k] for k in ("candidate","source_identity","input_identity")},**{"new_"+k:a[k] for k in ("candidate","source_identity","input_identity")}},"diagnostic transition")
    counts=pc.copy()
    for k,v in cfg["prior_attempts"].items():require(v>=counts.get(k,0),"diagnostic attempt refund");counts[k]=v
    counts["correction-source"]=cfg["source"];counts["correction-content"]=0
    limits={"genesis":1,"proxy-start":1,"start":1,"runtime-entered":1,"control":2,"thread":1,"thread-bound":1,"input":1,"stop":1,"process-ended":1,"turn":1,"generation":2,"dispatch":1}
    used={};prev="";last=prior["rows"][-1]["event"]["at_ms"];stopped=False;thread_request=None;thread_id=None;endpoints=set();events=[];plan=None;turn=None;generation=0;call=None
    require(0<len(rows)<32,"diagnostic bounded journal")
    for i,row in enumerate(rows):
        require(set(row)=={"event","sha256"},"diagnostic row");e=row["event"]
        require(set(e)=={"seq","prev","approval","work","candidate","phase","start","kind","subject","at_ms"} and type(e["seq"]) is int and e["seq"]==i and e["prev"]==prev and row["sha256"]==digest(wire_bytes(e)) and all(e[k]==a[k] for k in ("approval","work","candidate")),"diagnostic journal chain")
        kind=e["kind"];sub=e["subject"];require(kind in limits and isinstance(sub,dict) and type(e["at_ms"]) is int and last<=e["at_ms"]<=now,"diagnostic effect/time")
        used[kind]=used.get(kind,0)+1;require(used[kind]<=limits[kind] and (not stopped or kind=="process-ended"),"diagnostic cap/stop")
        if i==0:require(kind=="genesis" and e["phase"]==e["start"]=="controller" and sub=={"anchor_sha256":budget.anchor_sha256},"diagnostic genesis")
        else:require(kind!="genesis","diagnostic repeated genesis")
        if kind=="proxy-start":require(e["phase"]==e["start"]=="controller" and sub=={"slot":"s4","start_id":cfg["proxy_start"]},"diagnostic proxy")
        if kind in ("start","runtime-entered","control","thread","thread-bound","input","turn","generation","dispatch","process-ended"):
            require(e["phase"]=="clock" and e["start"]==cfg["start"],"diagnostic start binding")
            require(used.get("start",0)==1 and used.get("proxy-start",0)==1,"diagnostic start order")
        if kind=="start":
            binding=sub.get("execution_binding",{})
            require(binding=={"launch_mode":a["launch_mode"],"launch_contract_sha256":a["launch_contract_sha256"],"epoch_sha256":budget.anchor_sha256,"approval":a["approval"],"direct_tool_policy":a["direct_tool_policy"]},"clock start binding")
        if kind=="runtime-entered":require(sub=={"start":cfg["start"]},"diagnostic runtime entry")
        if kind in ("control","thread","thread-bound","input"):require(used.get("runtime-entered")==1,"diagnostic before runtime")
        if kind=="control":require(set(sub)=={"endpoint"} and sub["endpoint"] in ("models","accounts") and sub["endpoint"] not in endpoints and thread_request is None,"clock control retry/order");endpoints.add(sub["endpoint"])
        if kind=="thread":thread_request=sub.get("request");require(thread_request is not None and endpoints=={"models","accounts"},"clock thread before controls")
        if kind=="thread-bound":require(thread_request is not None and sub.get("request")==thread_request and isinstance(sub.get("thread"),str) and bool(sub["thread"]),"diagnostic thread binding");thread_id=sub["thread"]
        if kind=="input":
            require(thread_id is not None and set(sub)=={"plan","input_sha256","manifest_sha256"} and isinstance(sub["plan"],str) and bool(sub["plan"]),"clock input order")
            plan=sub["plan"]
        if kind=="turn":require(used.get("input")==1 and set(sub)=={"thread","plan"} and sub=={"thread":thread_id,"plan":plan},"clock turn binding")
        if kind in ("generation","dispatch"):
            require(used.get("turn")==1 and sub.get("plan")==plan and sub.get("thread")==thread_id and isinstance(sub.get("turn"),str) and bool(sub["turn"]) and turn in (None,sub["turn"]),"clock effect identity")
            if kind=="generation":
                require(set(sub)=={"thread","turn","plan","generation"} and type(sub["generation"]) is int and sub["generation"]==generation+1 and (generation==0 or call is not None),"clock generation order")
                generation=sub["generation"];turn=sub["turn"]
            else:
                require(set(sub)=={"thread","turn","plan","call"} and generation==1 and call is None and isinstance(sub["call"],str) and bool(sub["call"]),"clock dispatch order")
                call=sub["call"]
        if kind=="stop":require(set(sub)=={"reason"} and isinstance(sub["reason"],str),"diagnostic stop");stopped=True
        if kind=="process-ended":require(stopped and sub.get("process_group_absent") is True,"diagnostic process close")
        counts[kind]=counts.get(kind,0)+1;events.append(e);prev=row["sha256"];last=e["at_ms"]
    return {"events":events,"history_events":prior["history_events"]+events,"rows":rows,"prev":prev,"counts":counts,"excluded_ms":0,"paused_at":None,"stopped":stopped,"active_ms":now,"remaining_ms":min(a["total_deadline_ms"],a["run_deadline_ms"])-now}


U2_ALLOCATION = json.loads('{"approval_plan_sha256":"15ee3aedab89fdfb8a7328ce86683ccbffec2f0ef912f50f6290285579a85482","authority_apply":1,"content_corrections":2,"owner_message_id":"824273881","parent":{"anchor_sha256":"02cc6fd506cde882af60593f9091005f91a9e0568402628bd70f214e0956cc02","journal_sha256":"274801402ff46567de5d6852ff8431af95465aebdf03ab103f8e3a241afa7240","last_seq":14,"last_sha256":"cf4c7a5deb8a49ee5e254ff38d701c53c3ef5a7340448ba825997ad12230e088"},"parent_counts":{"authority-apply":0,"control":33,"dispatch":1,"generation":6,"host-dispatch":0,"proxy-start":23,"recovery-apply":0,"runtime-entered":21,"seal":0,"start":21,"thread":13,"thread-bound":12,"turn":6},"parent_rows":15,"parent_starts":21,"parent_version":30,"prior_attempts":{"build":40,"correction":53,"offline-start":93,"offline-thread":59,"offline-turn":33,"proxy-start":23,"review":3},"prior_cap_ms":153497229,"proxy_start":"s4-u2-01","proxy_total":24,"run_deadline_ms":1792948113976,"source":53,"starts":["synthetic-01","synthetic-02"],"total_cap_ms":182297229,"turns":12,"version":31}')


U2_POLICY = json.loads('{"authority_apply":1,"content_corrections":2,"control_endpoints":["models","accounts"],"dispatch_per_turn":1,"generation_per_turn":2,"kind":"synthetic-u2-continuation","model_turns":12,"recovery_apply":0,"starts":["synthetic-01","synthetic-02"],"version":1}')


U2_ALLOCATIONS = {int(k): v for k, v in json.loads('{"31":{"approval_plan_sha256":"15ee3aedab89fdfb8a7328ce86683ccbffec2f0ef912f50f6290285579a85482","authority_apply":1,"content_corrections":2,"owner_message_id":"824273881","parent":{"anchor_sha256":"02cc6fd506cde882af60593f9091005f91a9e0568402628bd70f214e0956cc02","journal_sha256":"274801402ff46567de5d6852ff8431af95465aebdf03ab103f8e3a241afa7240","last_seq":14,"last_sha256":"cf4c7a5deb8a49ee5e254ff38d701c53c3ef5a7340448ba825997ad12230e088"},"parent_counts":{"authority-apply":0,"control":33,"dispatch":1,"generation":6,"host-dispatch":0,"proxy-start":23,"recovery-apply":0,"runtime-entered":21,"seal":0,"start":21,"thread":13,"thread-bound":12,"turn":6},"parent_rows":15,"parent_starts":21,"parent_version":30,"prior_attempts":{"build":40,"correction":53,"offline-start":93,"offline-thread":59,"offline-turn":33,"proxy-start":23,"review":3},"prior_cap_ms":153497229,"proxy_start":"s4-u2-01","proxy_total":24,"run_deadline_ms":1792948113976,"source":53,"starts":["synthetic-01","synthetic-02"],"total_cap_ms":182297229,"turns":12,"version":31},"32":{"approval_plan_sha256":"15ee3aedab89fdfb8a7328ce86683ccbffec2f0ef912f50f6290285579a85482","authority_apply":1,"content_corrections":2,"owner_message_id":"824273881","parent":{"anchor_sha256":"954619d2ffdbcdfa8ec81af8d4f931c16ae95d05ee35192a7af2fe3004dc6e59","journal_sha256":"c6699cb853266e945cdf52a3995fa9e505344dcf8cf3fa4993b51f38612e6587","last_seq":9,"last_sha256":"46894f22c5c24876c3a452376218b09b10e57b5cae039c1f5a1ddc2cc0d7db9b"},"parent_counts":{"authority-apply":0,"control":35,"dispatch":1,"generation":6,"host-dispatch":0,"proxy-start":24,"recovery-apply":0,"runtime-entered":22,"seal":0,"start":22,"thread":14,"thread-bound":13,"turn":6},"parent_rows":10,"parent_starts":22,"parent_version":31,"prior_attempts":{"build":43,"correction":56,"offline-start":96,"offline-thread":59,"offline-turn":33,"proxy-start":24,"review":3},"prior_cap_ms":182297229,"proxy_start":"s4-u2-02","proxy_total":25,"run_deadline_ms":1792948113976,"source":56,"starts":["synthetic-01","synthetic-02"],"total_cap_ms":182297229,"turns":12,"version":32},"33":{"approval_plan_sha256":"15ee3aedab89fdfb8a7328ce86683ccbffec2f0ef912f50f6290285579a85482","authority_apply":1,"content_corrections":2,"owner_message_id":"824273881","parent":{"anchor_sha256":"2d87479be285ad229b47f2bff67e67c248671ceead1ebcae3b90de57d32d41e7","journal_sha256":"a0ca9568bc43c8e0996a4ab041da517b097f3866dc743f9188e1435bd4892ee7","last_seq":12,"last_sha256":"2e9b705d78b8dea5bd636544744de063e7f5570fce716775fd3c8442e7882b3a"},"parent_counts":{"authority-apply":0,"control":37,"dispatch":1,"generation":7,"host-dispatch":0,"proxy-start":25,"recovery-apply":0,"runtime-entered":23,"seal":0,"start":23,"thread":15,"thread-bound":14,"turn":7},"parent_rows":13,"parent_starts":23,"parent_version":32,"prior_attempts":{"build":45,"correction":58,"offline-start":101,"offline-thread":59,"offline-turn":33,"proxy-start":25,"review":3},"prior_cap_ms":182297229,"proxy_start":"s4-u2-03","proxy_total":26,"run_deadline_ms":1792948113976,"source":58,"starts":["synthetic-01","synthetic-02"],"total_cap_ms":182297229,"turns":12,"version":33},"34":{"approval_plan_sha256":"15ee3aedab89fdfb8a7328ce86683ccbffec2f0ef912f50f6290285579a85482","authority_apply":1,"content_corrections":2,"owner_message_id":"824273881","parent":{"anchor_sha256":"7fd7f7084fdeb69237fdeb43053f140051d6fcd19ee6192ba707f12a7efcfa57","journal_sha256":"aa06b938b2efbd0f0213b84ddf1142a120a66d2019345598e298785b4500b0d1","last_seq":12,"last_sha256":"4d36bb40b074af5ca71d0c95217cd0dd246a18cdf6ba51ed8477ab47fe2202bf"},"parent_counts":{"authority-apply":0,"control":39,"dispatch":1,"generation":8,"host-dispatch":0,"proxy-start":26,"recovery-apply":0,"runtime-entered":24,"seal":0,"start":24,"thread":16,"thread-bound":15,"turn":8},"parent_rows":13,"parent_starts":24,"parent_version":33,"prior_attempts":{"build":46,"correction":59,"offline-start":106,"offline-thread":59,"offline-turn":33,"proxy-start":26,"review":3},"prior_cap_ms":182297229,"proxy_start":"s4-u2-04","proxy_total":27,"run_deadline_ms":1792948113976,"source":59,"starts":["synthetic-01","synthetic-02"],"total_cap_ms":182297229,"turns":12,"version":34},"35":{"approval_plan_sha256":"15ee3aedab89fdfb8a7328ce86683ccbffec2f0ef912f50f6290285579a85482","authority_apply":1,"content_corrections":2,"owner_message_id":"824273881","parent":{"anchor_sha256":"a096282a0c2cdb2f8330ed9401efc116c5b96909e613f43762334566ff7c1a87","journal_sha256":"e2b295321a8856fd37c3ed6ac45aae41be3bbf877e53a270b851f676e68ca4fe","last_seq":12,"last_sha256":"0eb18f0d15ffc22c78d5956bb5652c31ad99f82acd94889d94366aa5c4be58c2"},"parent_counts":{"authority-apply":0,"control":41,"dispatch":1,"generation":9,"host-dispatch":0,"proxy-start":27,"recovery-apply":0,"runtime-entered":25,"seal":0,"start":25,"thread":17,"thread-bound":16,"turn":9},"parent_rows":13,"parent_starts":25,"parent_version":34,"prior_attempts":{"build":47,"correction":60,"offline-start":114,"offline-thread":59,"offline-turn":33,"proxy-start":27,"review":3},"prior_cap_ms":182297229,"proxy_start":"s4-u2-05","proxy_total":28,"run_deadline_ms":1792948113976,"source":60,"starts":["synthetic-01","synthetic-02"],"total_cap_ms":182297229,"turns":12,"version":35},"36":{"approval_plan_sha256":"15ee3aedab89fdfb8a7328ce86683ccbffec2f0ef912f50f6290285579a85482","authority_apply":1,"content_corrections":2,"owner_message_id":"824273881","parent":{"anchor_sha256":"89b3e5b1888399bfbd1a442c7f85422900fb2396334f8feda00a737fd06a15a7","journal_sha256":"6f80f4d3f2b2fd550bc9a3564943aacd5d736238872da8863a8095ae1c33ee95","last_seq":15,"last_sha256":"fbb594dffb9a6d3b1198afc43dba6de47642606195ab077c48d847831627b79d"},"parent_counts":{"authority-apply":0,"control":43,"dispatch":2,"generation":10,"host-dispatch":1,"proxy-start":28,"recovery-apply":0,"runtime-entered":26,"seal":0,"start":26,"thread":18,"thread-bound":17,"turn":10},"parent_rows":16,"parent_starts":26,"parent_version":35,"prior_attempts":{"build":48,"correction":61,"offline-start":121,"offline-thread":59,"offline-turn":33,"proxy-start":28,"review":3},"prior_cap_ms":182297229,"proxy_start":"s4-u2-06","proxy_total":29,"run_deadline_ms":1792948113976,"source":61,"starts":["synthetic-01","synthetic-02"],"total_cap_ms":182297229,"turns":12,"version":36},"37":{"approval_plan_sha256":"15ee3aedab89fdfb8a7328ce86683ccbffec2f0ef912f50f6290285579a85482","authority_apply":1,"content_corrections":2,"owner_message_id":"824273881","parent":{"anchor_sha256":"a7af117831eb511fccdc9649d9c65ce87654f4803d430e45f12485321c360eb7","journal_sha256":"8a09d9828be1aed9d1742f503911d75d5b4fb30fa1384b40fb041f70e38fb265","last_seq":14,"last_sha256":"64dce7119fdb9db85839f044c2d9456811f4ff4b0e155f16004df37b40ebf2c5"},"parent_counts":{"authority-apply":0,"control":45,"dispatch":3,"generation":11,"host-dispatch":2,"proxy-start":29,"recovery-apply":0,"runtime-entered":27,"seal":0,"start":27,"thread":19,"thread-bound":18,"turn":11},"parent_rows":15,"parent_starts":27,"parent_version":36,"prior_attempts":{"build":49,"correction":62,"offline-start":125,"offline-thread":59,"offline-turn":33,"proxy-start":29,"review":3},"prior_cap_ms":182297229,"proxy_start":"s4-u2-07","proxy_total":30,"run_deadline_ms":1792948113976,"source":62,"starts":["synthetic-01","synthetic-02"],"total_cap_ms":182297229,"turns":12,"version":37},"38":{"approval_plan_sha256":"15ee3aedab89fdfb8a7328ce86683ccbffec2f0ef912f50f6290285579a85482","authority_apply":1,"content_corrections":2,"owner_message_id":"824273881","parent":{"anchor_sha256":"d07aa950fc5fd1d93755498b1285befbccb147b1decb3d686916a8d5b41daf3f","journal_sha256":"f4273666e38fa66ae23e3d01222a6e90ba6a836de0ff1e6851206d284df5ca9e","last_seq":29,"last_sha256":"07819070060c8386d0c6187238552f22993e29c0201f8a2162a761613777b54f"},"parent_counts":{"authority-apply":0,"control":49,"dispatch":5,"generation":14,"host-dispatch":4,"proxy-start":30,"recovery-apply":0,"runtime-entered":29,"seal":0,"start":29,"thread":21,"thread-bound":20,"turn":13},"parent_rows":30,"parent_starts":29,"parent_version":37,"prior_attempts":{"build":50,"correction":63,"offline-start":128,"offline-thread":59,"offline-turn":33,"proxy-start":30,"review":3},"prior_cap_ms":182297229,"proxy_start":"s4-u2-08","proxy_total":31,"run_deadline_ms":1792948113976,"source":63,"starts":["synthetic-01","synthetic-02"],"total_cap_ms":182297229,"turns":12,"version":38},"39":{"approval_plan_sha256":"15ee3aedab89fdfb8a7328ce86683ccbffec2f0ef912f50f6290285579a85482","authority_apply":1,"content_corrections":2,"owner_message_id":"824273881","parent":{"anchor_sha256":"4a9338a4898a0a87f7d5572e4e2ba97743ba2214c09c83b813d94614380de8e2","journal_sha256":"4e69ada64a860a3b7fab8aa395597011fdb56640a696a01762b398589bc880f9","last_seq":29,"last_sha256":"9f992e85140e70f43adef3430ee0704fda192cc57cd8b3d84e840f7164752700"},"parent_counts":{"authority-apply":0,"control":53,"dispatch":7,"generation":17,"host-dispatch":6,"proxy-start":31,"recovery-apply":0,"runtime-entered":31,"seal":0,"start":31,"thread":23,"thread-bound":22,"turn":15},"parent_rows":30,"parent_starts":31,"parent_version":38,"prior_attempts":{"build":51,"correction":64,"offline-start":132,"offline-thread":59,"offline-turn":33,"proxy-start":31,"review":3},"prior_cap_ms":182297229,"proxy_start":"s4-u2-09","proxy_total":32,"run_deadline_ms":1792948113976,"source":64,"starts":["synthetic-01","synthetic-02"],"total_cap_ms":182297229,"turns":12,"version":39},"40":{"approval_plan_sha256":"15ee3aedab89fdfb8a7328ce86683ccbffec2f0ef912f50f6290285579a85482","authority_apply":1,"content_corrections":2,"owner_message_id":"824273881","parent":{"anchor_sha256":"9a81562f11ffe31e0bb5ca0f71f5aeb03eb8a8bad53f0b71e2d77305f6f95caf","journal_sha256":"d32b21821a38602d0e3d7ecc8b625ae25acc72e05f4992ccbf905557e9081a7d","last_seq":34,"last_sha256":"b66af5f5827ffdda90e334069f24b9ce199252c52b320b68f73bfde9a66a2f5e"},"parent_counts":{"authority-apply":0,"control":57,"dispatch":10,"generation":22,"host-dispatch":8,"proxy-start":32,"recovery-apply":0,"runtime-entered":33,"seal":0,"start":33,"thread":25,"thread-bound":24,"turn":18},"parent_rows":35,"parent_starts":33,"parent_version":39,"prior_attempts":{"build":52,"correction":65,"offline-start":138,"offline-thread":59,"offline-turn":33,"proxy-start":32,"review":3},"prior_cap_ms":182297229,"proxy_start":"s4-u2-10","proxy_total":33,"run_deadline_ms":1792948113976,"source":65,"starts":["synthetic-01","synthetic-02"],"total_cap_ms":182297229,"turns":12,"version":40},"41":{"approval_plan_sha256":"d11c73b5c8bdca41e7077f3b478439782df5fcb31d067a3ada7aa5eb1e6d6cec","authority_apply":1,"content_corrections":2,"owner_message_id":"562448390","parent":{"anchor_sha256":"64e84e5b6e4ecab60dd0be6cff7549ed9e251a5819011ec4421b2b78ce7a3790","journal_sha256":"df8d6d836f164ac41deb453001da9d7ab169228d35b9cbacb6f39bec3b083c1f","last_seq":89,"last_sha256":"a535e309ed16881a4adda2749f032255284492b9365b12210a17705eab66e512"},"parent_counts":{"authority-apply":0,"control":61,"dispatch":20,"generation":42,"host-dispatch":18,"proxy-start":33,"recovery-apply":0,"runtime-entered":35,"seal":1,"start":35,"thread":27,"thread-bound":26,"turn":28},"parent_rows":90,"parent_sealed":true,"parent_starts":35,"parent_version":40,"prior_attempts":{"build":53,"correction":67,"offline-start":143,"offline-thread":59,"offline-turn":33,"proxy-start":33,"review":3},"prior_cap_ms":182297229,"proxy_start":"s4-u2-11","proxy_total":34,"replacement_work":{"home":"u2-synthetic-h04-20261025","work":"synthetic-h04-same-thread"},"run_deadline_ms":1792935456554,"source":66,"starts":["synthetic-01","synthetic-02"],"total_cap_ms":182297229,"turns":12,"version":41},"42":{"approval_plan_sha256":"077c4387b13833a6f4cccd2f7e565d1193c47de200d6d81cfe7a10960483738f","authority_apply":1,"content_corrections":2,"owner_message_id":"824273881","parent":{"anchor_sha256":"d91dd60f032c7d592bf3ad55c1251db2444615e389a8367507af9fea34043d3f","journal_sha256":"ab79e76ee5e03af2bfbb4fd9f87214f1ac62e79f0c85d7c6fad0c7e693857169","last_seq":97,"last_sha256":"1a6e0edd3ca4454e569f9376b2aa92043b146e3bea738e6f55227cfae3e40e45"},"parent_counts":{"authority-apply":1,"control":65,"correction-content":2,"dispatch":31,"generation":64,"host-dispatch":29,"proxy-start":34,"recovery-apply":0,"runtime-entered":37,"seal":2,"start":37,"thread":29,"thread-bound":28,"turn":39},"parent_rows":98,"parent_sealed":true,"parent_starts":37,"parent_version":41,"phase":"h10","policy":{"authority_apply":1,"content_corrections":2,"control_endpoints":["models","accounts"],"dispatch_per_turn":1,"generation_per_turn":2,"kind":"h10-u2-continuation","model_turns":40,"recovery_apply":0,"starts":["h10-01","h10-02"],"version":1},"prior_attempts":{"build":54,"correction":69,"offline-start":156,"offline-thread":59,"offline-turn":33,"proxy-start":34,"review":3},"prior_cap_ms":182297229,"proxy_slot":"s6","proxy_start":"s6-h10-01","proxy_total":35,"replacement_work":{"home":"synthetic-reference-a","work":"synthetic-operations-guide-check"},"run_deadline_ms":1792948113976,"source":67,"starts":["h10-01","h10-02"],"total_cap_ms":182297229,"turns":40,"version":42},"43":{"approval_plan_sha256":"077c4387b13833a6f4cccd2f7e565d1193c47de200d6d81cfe7a10960483738f","authority_apply":1,"content_corrections":2,"owner_message_id":"824273881","parent":{"anchor_sha256":"d91dd60f032c7d592bf3ad55c1251db2444615e389a8367507af9fea34043d3f","journal_sha256":"ab79e76ee5e03af2bfbb4fd9f87214f1ac62e79f0c85d7c6fad0c7e693857169","last_seq":97,"last_sha256":"1a6e0edd3ca4454e569f9376b2aa92043b146e3bea738e6f55227cfae3e40e45"},"parent_counts":{"authority-apply":1,"control":65,"correction-content":2,"dispatch":31,"generation":64,"host-dispatch":29,"proxy-start":34,"recovery-apply":0,"runtime-entered":37,"seal":2,"start":37,"thread":29,"thread-bound":28,"turn":39},"parent_rows":98,"parent_sealed":true,"parent_starts":37,"parent_version":41,"phase":"h10","policy":{"authority_apply":1,"content_corrections":2,"control_endpoints":["models","accounts"],"dispatch_per_turn":1,"generation_per_turn":2,"kind":"h10-u2-continuation","model_turns":40,"recovery_apply":0,"starts":["h10-01","h10-02"],"version":1},"prior_attempts":{"build":55,"correction":70,"offline-start":158,"offline-thread":59,"offline-turn":33,"proxy-start":34,"review":3},"prior_cap_ms":182297229,"proxy_slot":"s6","proxy_start":"s6-h10-01","proxy_total":35,"replacement_work":{"home":"synthetic-reference-a","work":"synthetic-operations-guide-check"},"run_deadline_ms":1792948113976,"source":68,"starts":["h10-01","h10-02"],"total_cap_ms":182297229,"turns":40,"version":43},"44":{"approval_plan_sha256":"077c4387b13833a6f4cccd2f7e565d1193c47de200d6d81cfe7a10960483738f","authority_apply":1,"content_corrections":2,"owner_message_id":"824273881","parent":{"anchor_sha256":"d91dd60f032c7d592bf3ad55c1251db2444615e389a8367507af9fea34043d3f","journal_sha256":"ab79e76ee5e03af2bfbb4fd9f87214f1ac62e79f0c85d7c6fad0c7e693857169","last_seq":97,"last_sha256":"1a6e0edd3ca4454e569f9376b2aa92043b146e3bea738e6f55227cfae3e40e45"},"parent_counts":{"authority-apply":1,"control":65,"correction-content":2,"dispatch":31,"generation":64,"host-dispatch":29,"proxy-start":34,"recovery-apply":0,"runtime-entered":37,"seal":2,"start":37,"thread":29,"thread-bound":28,"turn":39},"parent_rows":98,"parent_sealed":true,"parent_starts":37,"parent_version":41,"phase":"h10","policy":{"authority_apply":1,"content_corrections":2,"control_endpoints":["models","accounts"],"dispatch_per_turn":1,"generation_per_turn":2,"kind":"h10-u2-continuation","model_turns":40,"recovery_apply":0,"starts":["h10-01","h10-02"],"version":1},"prior_attempts":{"build":56,"correction":71,"offline-start":160,"offline-thread":59,"offline-turn":33,"proxy-start":34,"review":3},"prior_cap_ms":182297229,"proxy_slot":"s6","proxy_start":"s6-h10-01","proxy_total":35,"replacement_work":{"home":"synthetic-reference-a","work":"synthetic-operations-guide-check"},"run_deadline_ms":1792948113976,"source":69,"starts":["h10-01","h10-02"],"total_cap_ms":182297229,"turns":40,"version":44},"45":{"approval_plan_sha256":"077c4387b13833a6f4cccd2f7e565d1193c47de200d6d81cfe7a10960483738f","authority_apply":1,"content_corrections":2,"owner_message_id":"824273881","parent":{"anchor_sha256":"b3feb6a341c30ad090218047af5e12d7baae0d56e8ae90298ebc423420e9d74c","journal_sha256":"7fe8c5c03c7f72fe118d8c447caeb97a789ea8be74054544671d8fccd1b93356","last_seq":1,"last_sha256":"6e14986c61ec78a8b91aaaf55cffc8c94da3c91f77c0ca72e39002a0fbc5325e"},"parent_counts":{"authority-apply":1,"build":56,"control":65,"correction":71,"correction-content":2,"correction-source":69,"dispatch":31,"generation":64,"genesis":37,"host-dispatch":29,"input":42,"offline-start":168,"offline-thread":59,"offline-turn":33,"pause":3,"process-ended":37,"proxy-start":34,"resume":1,"review":3,"runtime-entered":37,"seal":2,"start":37,"stop":36,"thread":29,"thread-bound":28,"turn":39,"worker-result":27},"parent_rows":2,"parent_sealed":false,"parent_starts":37,"parent_version":44,"phase":"h10","policy":{"authority_apply":1,"content_corrections":2,"control_endpoints":["models","accounts"],"dispatch_per_turn":1,"generation_per_turn":2,"kind":"h10-u2-continuation","model_turns":40,"recovery_apply":0,"starts":["h10-01","h10-02"],"version":1},"prior_attempts":{"build":57,"correction":72,"offline-start":168,"offline-thread":59,"offline-turn":33,"proxy-start":34,"review":3},"prior_cap_ms":182297229,"proxy_slot":"s6","proxy_start":"s6-h10-01","proxy_total":35,"replacement_work":{"home":"synthetic-reference-a","work":"synthetic-operations-guide-check"},"run_deadline_ms":1792948113976,"source":70,"starts":["h10-01","h10-02"],"total_cap_ms":182297229,"turns":40,"version":45},"46":{"approval_plan_sha256":"077c4387b13833a6f4cccd2f7e565d1193c47de200d6d81cfe7a10960483738f","authority_apply":1,"content_corrections":2,"owner_message_id":"824273881","parent":{"anchor_sha256":"658a6aa50c973c4fe5c1aabe569c8bc5b4fcf168e829ec5991666f4a54aa02ac","journal_sha256":"49d2d1b2776472138565ef77477015a5091a245b5770ad3c1d27b4a957ab4746","last_seq":2,"last_sha256":"9401976ead3121ac6cd3042ad5ecaf44a4945213d1e54f938c7aeb36b1460659"},"parent_counts":{"authority-apply":1,"build":57,"control":65,"correction":72,"correction-content":2,"correction-source":70,"dispatch":31,"generation":64,"genesis":38,"host-dispatch":29,"input":42,"offline-start":173,"offline-thread":59,"offline-turn":33,"pause":3,"process-ended":37,"proxy-start":35,"resume":1,"review":3,"runtime-entered":37,"seal":2,"start":37,"stop":37,"thread":29,"thread-bound":28,"turn":39,"worker-result":27},"parent_rows":3,"parent_sealed":false,"parent_starts":37,"parent_version":45,"phase":"h10","policy":{"authority_apply":1,"content_corrections":2,"control_endpoints":["models","accounts"],"dispatch_per_turn":1,"generation_per_turn":2,"kind":"h10-u2-continuation","model_turns":40,"recovery_apply":0,"starts":["h10-01","h10-02"],"version":1},"prior_attempts":{"build":58,"correction":73,"offline-start":173,"offline-thread":59,"offline-turn":33,"proxy-start":35,"review":3},"prior_cap_ms":182297229,"proxy_slot":"s6","proxy_start":"s6-u2-h10-02","proxy_total":36,"replacement_work":{"home":"synthetic-reference-a","work":"synthetic-operations-guide-check"},"run_deadline_ms":1792948113976,"source":71,"starts":["h10-01","h10-02"],"total_cap_ms":182297229,"turns":40,"version":46},"47":{"approval_plan_sha256":"077c4387b13833a6f4cccd2f7e565d1193c47de200d6d81cfe7a10960483738f","authority_apply":1,"content_corrections":2,"owner_message_id":"824273881","parent":{"anchor_sha256":"c8e216db5c7f0a19f66c24d54b5029fe21f044d16f2d9c3042d8ea01767dc41b","journal_sha256":"330fe3589f5c9b5c425c634e1529693e346bd5b817df3f74ead22131e8500a68","last_seq":2,"last_sha256":"07664ea5d7f0dd344dbaa2ca6a354b0c4970d0d39c1c06d0113e0ea19ec9b8aa"},"parent_counts":{"authority-apply":1,"build":58,"control":65,"correction":73,"correction-content":2,"correction-source":71,"dispatch":31,"generation":64,"genesis":39,"host-dispatch":29,"input":42,"offline-start":176,"offline-thread":59,"offline-turn":33,"pause":3,"process-ended":37,"proxy-start":36,"resume":1,"review":3,"runtime-entered":37,"seal":2,"start":37,"stop":38,"thread":29,"thread-bound":28,"turn":39,"worker-result":27},"parent_rows":3,"parent_sealed":false,"parent_starts":37,"parent_version":46,"phase":"h10","policy":{"authority_apply":1,"content_corrections":2,"control_endpoints":["models","accounts"],"dispatch_per_turn":1,"generation_per_turn":2,"kind":"h10-u2-continuation","model_turns":40,"recovery_apply":0,"starts":["h10-01","h10-02"],"version":1},"prior_attempts":{"build":59,"correction":74,"offline-start":177,"offline-thread":59,"offline-turn":33,"proxy-start":36,"review":3},"prior_cap_ms":182297229,"proxy_slot":"s6","proxy_start":"s6-u2-h10-03","proxy_total":37,"replacement_work":{"home":"synthetic-reference-a","work":"synthetic-operations-guide-check"},"run_deadline_ms":1792948113976,"source":72,"starts":["h10-01","h10-02"],"total_cap_ms":182297229,"turns":40,"version":47},"48":{"approval_plan_sha256":"077c4387b13833a6f4cccd2f7e565d1193c47de200d6d81cfe7a10960483738f","authority_apply":1,"content_corrections":2,"owner_message_id":"824273881","parent":{"anchor_sha256":"c8e216db5c7f0a19f66c24d54b5029fe21f044d16f2d9c3042d8ea01767dc41b","journal_sha256":"330fe3589f5c9b5c425c634e1529693e346bd5b817df3f74ead22131e8500a68","last_seq":2,"last_sha256":"07664ea5d7f0dd344dbaa2ca6a354b0c4970d0d39c1c06d0113e0ea19ec9b8aa"},"parent_counts":{"authority-apply":1,"build":58,"control":65,"correction":73,"correction-content":2,"correction-source":71,"dispatch":31,"generation":64,"genesis":39,"host-dispatch":29,"input":42,"offline-start":176,"offline-thread":59,"offline-turn":33,"pause":3,"process-ended":37,"proxy-start":36,"resume":1,"review":3,"runtime-entered":37,"seal":2,"start":37,"stop":38,"thread":29,"thread-bound":28,"turn":39,"worker-result":27},"parent_rows":3,"parent_sealed":false,"parent_starts":37,"parent_version":46,"phase":"h10","policy":{"authority_apply":1,"content_corrections":2,"control_endpoints":["models","accounts"],"dispatch_per_turn":1,"generation_per_turn":2,"kind":"h10-u2-continuation","model_turns":40,"recovery_apply":0,"starts":["h10-01","h10-02"],"version":1},"prior_attempts":{"build":60,"correction":75,"offline-start":177,"offline-thread":59,"offline-turn":33,"proxy-start":36,"review":3},"prior_cap_ms":182297229,"proxy_slot":"s6","proxy_start":"s6-u2-h10-03","proxy_total":37,"replacement_work":{"home":"synthetic-reference-a","work":"synthetic-operations-guide-check"},"run_deadline_ms":1792948113976,"source":73,"starts":["h10-01","h10-02"],"total_cap_ms":182297229,"turns":40,"version":48},"49":{"approval_plan_sha256":"077c4387b13833a6f4cccd2f7e565d1193c47de200d6d81cfe7a10960483738f","authority_apply":1,"content_corrections":2,"owner_message_id":"824273881","parent":{"anchor_sha256":"1a330f6b59c574e632921c1300b2d7d59757714b132b495051af1a6944be7e8e","journal_sha256":"ea73a18601e5d45c82af3fe081b2c07353a686a73aed5f3daf647178a2a63d43","last_seq":57,"last_sha256":"ae0aee3e32015bd6b0c1f60198ac6239906b18a6290f50e4969c1a42c377eda4"},"parent_counts":{"authority-apply":1,"build":60,"control":67,"correction":75,"correction-content":2,"correction-source":73,"dispatch":38,"generation":77,"genesis":40,"host-dispatch":36,"input":49,"offline-start":180,"offline-thread":59,"offline-turn":33,"pause":3,"process-ended":38,"proxy-start":37,"resume":1,"review":3,"runtime-entered":38,"seal":2,"start":38,"stop":39,"thread":30,"thread-bound":29,"turn":46,"worker-result":34},"parent_rows":58,"parent_sealed":false,"parent_starts":38,"parent_version":48,"phase":"h10","policy":{"authority_apply":1,"content_corrections":2,"control_endpoints":["models","accounts"],"dispatch_per_turn":1,"generation_per_turn":2,"kind":"h10-u2-continuation","model_turns":33,"recovery_apply":0,"starts":["h10-01"],"version":1},"prior_attempts":{"build":61,"correction":76,"offline-start":180,"offline-thread":59,"offline-turn":33,"proxy-start":37,"review":3},"prior_cap_ms":182297229,"proxy_slot":"s6","proxy_start":"s6-u2-h10-final","proxy_total":38,"replacement_work":{"home":"synthetic-reference-a","work":"synthetic-operations-guide-check"},"run_deadline_ms":1792948113976,"source":74,"starts":["h10-01"],"total_cap_ms":182297229,"turns":33,"version":49},"50":{"approval_plan_sha256":"077c4387b13833a6f4cccd2f7e565d1193c47de200d6d81cfe7a10960483738f","authority_apply":1,"content_corrections":2,"owner_message_id":"824273881","parent":{"anchor_sha256":"1a330f6b59c574e632921c1300b2d7d59757714b132b495051af1a6944be7e8e","journal_sha256":"ea73a18601e5d45c82af3fe081b2c07353a686a73aed5f3daf647178a2a63d43","last_seq":57,"last_sha256":"ae0aee3e32015bd6b0c1f60198ac6239906b18a6290f50e4969c1a42c377eda4"},"parent_counts":{"authority-apply":1,"build":60,"control":67,"correction":75,"correction-content":2,"correction-source":73,"dispatch":38,"generation":77,"genesis":40,"host-dispatch":36,"input":49,"offline-start":180,"offline-thread":59,"offline-turn":33,"pause":3,"process-ended":38,"proxy-start":37,"resume":1,"review":3,"runtime-entered":38,"seal":2,"start":38,"stop":39,"thread":30,"thread-bound":29,"turn":46,"worker-result":34},"parent_rows":58,"parent_sealed":false,"parent_starts":38,"parent_version":48,"phase":"h10","policy":{"authority_apply":1,"content_corrections":2,"control_endpoints":["models","accounts"],"dispatch_per_turn":1,"generation_per_turn":2,"kind":"h10-u2-continuation","model_turns":33,"recovery_apply":0,"starts":["h10-01"],"version":1},"prior_attempts":{"build":62,"correction":77,"offline-start":182,"offline-thread":59,"offline-turn":33,"proxy-start":37,"review":3},"prior_cap_ms":182297229,"proxy_slot":"s6","proxy_start":"s6-u2-h10-final","proxy_total":38,"replacement_work":{"home":"synthetic-reference-a","work":"synthetic-operations-guide-check"},"run_deadline_ms":1792948113976,"source":75,"starts":["h10-01"],"total_cap_ms":182297229,"turns":33,"version":50},"51":{"approval_plan_sha256":"077c4387b13833a6f4cccd2f7e565d1193c47de200d6d81cfe7a10960483738f","authority_apply":1,"content_corrections":2,"owner_message_id":"824273881","parent":{"anchor_sha256":"1ec72dfe6c980b4fd0a58ce8773b6d6d84ecaa915c93d7eb22ff81efc7749e73","journal_sha256":"ddfd1d7f9e9a9758a1e4bfaa3fd80bb49a95788a05c90e947574ce6026649e81","last_seq":2,"last_sha256":"f23c30994c0bfe0f9cd6ea90912c86b82d587976d4ab6be5c427423c7c4255fc"},"parent_counts":{"authority-apply":1,"build":62,"control":67,"correction":77,"correction-content":2,"correction-source":75,"dispatch":38,"generation":77,"genesis":41,"host-dispatch":36,"input":49,"offline-start":187,"offline-thread":59,"offline-turn":33,"pause":3,"process-ended":38,"proxy-start":38,"resume":1,"review":3,"runtime-entered":38,"seal":2,"start":38,"stop":40,"thread":30,"thread-bound":29,"turn":46,"worker-result":34},"parent_rows":3,"parent_sealed":false,"parent_starts":38,"parent_version":50,"phase":"h10","policy":{"authority_apply":1,"content_corrections":2,"control_endpoints":["models","accounts"],"dispatch_per_turn":1,"generation_per_turn":2,"kind":"h10-u2-continuation","model_turns":33,"recovery_apply":0,"starts":["h10-01"],"version":1},"prior_attempts":{"build":63,"correction":78,"offline-start":187,"offline-thread":59,"offline-turn":33,"proxy-start":38,"review":3},"prior_cap_ms":182297229,"proxy_slot":"s6","proxy_start":"s6-u2-h10-last-start","proxy_total":39,"replacement_work":{"home":"synthetic-reference-a","work":"synthetic-operations-guide-check"},"run_deadline_ms":1792948113976,"source":76,"starts":["h10-01"],"total_cap_ms":182297229,"turns":33,"version":51},"52":{"approval_plan_sha256":"077c4387b13833a6f4cccd2f7e565d1193c47de200d6d81cfe7a10960483738f","authority_apply":1,"content_corrections":2,"owner_message_id":"896607746","parent":{"anchor_sha256":"a69e489cf848dbd6586b9b70c76a0482fca6c18320155a3353ad699f0def41f4","journal_sha256":"e595f1f73c1fc8bce187caaef7e347e991eaa1b341951dac57847f840b575aa0","last_seq":51,"last_sha256":"a06cba7394819e13321152b9b1180371bb2d25062bc43ececf3778e296f51952"},"parent_counts":{"authority-apply":1,"build":63,"control":69,"correction":78,"correction-content":2,"correction-source":76,"dispatch":44,"generation":89,"genesis":42,"host-dispatch":42,"input":55,"offline-start":190,"offline-thread":59,"offline-turn":33,"pause":3,"process-ended":39,"proxy-start":39,"resume":1,"review":3,"runtime-entered":39,"seal":2,"start":39,"stop":41,"thread":31,"thread-bound":30,"turn":52,"worker-result":40},"parent_rows":52,"parent_sealed":false,"parent_starts":39,"parent_version":51,"phase":"h10","policy":{"authority_apply":1,"content_corrections":2,"control_endpoints":["models","accounts"],"dispatch_per_turn":1,"generation_per_turn":2,"kind":"h10-u2-continuation","model_turns":27,"recovery_apply":0,"starts":["h10-01"],"version":1},"prior_attempts":{"build":66,"correction":81,"offline-start":194,"offline-thread":59,"offline-turn":33,"proxy-start":39,"review":3},"prior_cap_ms":182297229,"proxy_slot":"s6","proxy_start":"s6-u2-h10-additional-start","proxy_total":40,"replacement_work":{"home":"synthetic-reference-a","work":"synthetic-operations-guide-check"},"run_deadline_ms":1792948113976,"source":79,"starts":["h10-01"],"total_cap_ms":182297229,"turns":27,"version":52},"53":{"approval_plan_sha256":"077c4387b13833a6f4cccd2f7e565d1193c47de200d6d81cfe7a10960483738f","authority_apply":1,"content_corrections":2,"owner_message_id":"332859366","parent":{"anchor_sha256":"9fcda975687ed3dd13c8afcf87dfdf52efb9ff90631a43919364be36fac5e164","journal_sha256":"9605ccee43b5efc76299bce79378b25fa92bd58da09b2c433cdd5a5912f30137","last_seq":95,"last_sha256":"d4dd5dcab9896487bf3fafec0a68b911d5d7722036099fab065136d2f5088e4d"},"parent_counts":{"authority-apply":1,"build":66,"control":71,"correction":81,"correction-content":2,"correction-source":79,"dispatch":56,"generation":113,"genesis":43,"host-dispatch":54,"input":67,"offline-start":197,"offline-thread":59,"offline-turn":33,"pause":4,"process-ended":40,"proxy-start":40,"resume":1,"review":3,"runtime-entered":40,"seal":3,"start":40,"stop":42,"thread":32,"thread-bound":31,"turn":64,"worker-result":52},"parent_rows":96,"parent_sealed":true,"parent_starts":40,"parent_version":52,"phase":"h10","policy":{"authority_apply":1,"content_corrections":2,"control_endpoints":["models","accounts"],"dispatch_per_turn":1,"generation_per_turn":2,"kind":"h10-u2-continuation","model_turns":15,"recovery_apply":0,"starts":["h10-01"],"version":1},"prior_attempts":{"build":67,"correction":83,"offline-start":199,"offline-thread":59,"offline-turn":33,"proxy-start":40,"review":3},"prior_cap_ms":182297229,"proxy_slot":"s6","proxy_start":"s6-u2-h10-index-correction-start","proxy_total":41,"replacement_work":{"home":"synthetic-reference-a","work":"synthetic-operations-guide-check"},"run_deadline_ms":1792948113976,"source":81,"starts":["h10-01"],"total_cap_ms":182297229,"turns":15,"version":53},"54":{"approval_plan_sha256":"077c4387b13833a6f4cccd2f7e565d1193c47de200d6d81cfe7a10960483738f","authority_apply":1,"content_corrections":2,"owner_message_id":"17934842","parent":{"anchor_sha256":"8f6e4a88a351df1329ac07c70c714aaf642abf5b665c09c840acb9b36db035d4","journal_sha256":"fd1968d0aeae8133fecd9b0280d9395063aa793a168827b2c6f9221331924e87","last_seq":2,"last_sha256":"1cc3c0141d2d31c7b2d55ab60c8942a71fda0763b5b5b1939602ad3ff726f4c4"},"parent_counts":{"authority-apply":1,"build":67,"control":71,"correction":83,"correction-content":2,"correction-source":81,"dispatch":56,"generation":113,"genesis":44,"host-dispatch":54,"input":67,"offline-start":202,"offline-thread":59,"offline-turn":33,"pause":4,"process-ended":40,"proxy-start":41,"resume":1,"review":3,"runtime-entered":40,"seal":3,"start":40,"stop":43,"thread":32,"thread-bound":31,"turn":64,"worker-result":52},"parent_rows":3,"parent_sealed":false,"parent_starts":40,"parent_version":53,"phase":"h10","policy":{"authority_apply":1,"content_corrections":2,"control_endpoints":["models","accounts"],"dispatch_per_turn":1,"generation_per_turn":2,"kind":"h10-u2-continuation","model_turns":15,"recovery_apply":0,"starts":["h10-01"],"version":1},"prior_attempts":{"build":68,"correction":84,"offline-start":202,"offline-thread":59,"offline-turn":33,"proxy-start":41,"review":3},"prior_cap_ms":182297229,"proxy_slot":"s6","proxy_start":"s6-u2-h10-input-path-recovery","proxy_total":42,"replacement_work":{"home":"synthetic-reference-a","work":"synthetic-operations-guide-check"},"run_deadline_ms":1792948113976,"source":82,"starts":["h10-01"],"total_cap_ms":182297229,"turns":15,"version":54},"55":{"approval_plan_sha256":"077c4387b13833a6f4cccd2f7e565d1193c47de200d6d81cfe7a10960483738f","authority_apply":1,"content_corrections":2,"owner_message_id":"258208394","parent":{"anchor_sha256":"18d9e37be21b78784756004859809dde439f81440d9a07e62dffdc3f6a51e7d6","journal_sha256":"535dedac55552b4dcb47dd10410d0374437c7f080d63903dea2e86bc9464c8ba","last_seq":95,"last_sha256":"30ba0ddebb19f9323d6288c2868fef11ece7ce909cd273821179f418526cff2d"},"parent_counts":{"authority-apply":1,"build":68,"control":73,"correction":84,"correction-content":2,"correction-source":82,"dispatch":68,"generation":137,"genesis":45,"host-dispatch":66,"input":79,"offline-start":205,"offline-thread":59,"offline-turn":33,"pause":5,"process-ended":41,"proxy-start":42,"resume":1,"review":3,"runtime-entered":41,"seal":4,"start":41,"stop":44,"thread":33,"thread-bound":32,"turn":76,"worker-result":64},"parent_rows":96,"parent_sealed":true,"parent_starts":41,"parent_version":54,"phase":"h10","policy":{"authority_apply":1,"content_corrections":2,"control_endpoints":["models","accounts"],"dispatch_per_turn":1,"generation_per_turn":2,"kind":"h10-u2-continuation","model_turns":13,"recovery_apply":0,"starts":["h10-01"],"version":1},"prior_attempts":{"build":69,"correction":85,"offline-start":205,"offline-thread":59,"offline-turn":33,"proxy-start":42,"review":3},"prior_cap_ms":182297229,"proxy_slot":"s6","proxy_start":"s6-u2-h10-table-continuity","proxy_total":43,"replacement_work":{"home":"synthetic-reference-a","work":"synthetic-operations-guide-check"},"run_deadline_ms":1792948113976,"source":83,"starts":["h10-01"],"total_cap_ms":182297229,"turns":13,"version":55},"56":{"approval_plan_sha256":"ceccc3bedb51f0df9f8418ed0c84eaa06e8b34c5af532eafcab0d880cedb48da","authority_apply":1,"content_corrections":2,"owner_message_id":"250157751","parent":{"anchor_sha256":"2c20096f1705cac7ef6d0014de21d0d7477db9fb2645abdd3f72bd04c853baa2","journal_sha256":"4cd3148714f9bed42d6b9bc8492db1bd9669c90d38a999494fb5886a17e0f725","last_seq":1,"last_sha256":"bbf637dd38a5b99d704159f22fe50239d6fc02890055244a3e9c3ecd8e725d9c"},"parent_counts":{"authority-apply":1,"build":69,"control":73,"correction":85,"correction-content":2,"correction-source":83,"dispatch":68,"generation":137,"genesis":46,"host-dispatch":66,"input":79,"offline-start":208,"offline-thread":59,"offline-turn":33,"pause":5,"process-ended":41,"proxy-start":42,"resume":1,"review":3,"runtime-entered":41,"seal":4,"start":41,"stop":45,"thread":33,"thread-bound":32,"turn":76,"worker-result":64},"parent_rows":2,"parent_sealed":false,"parent_starts":41,"parent_version":55,"phase":"h10","policy":{"authority_apply":1,"content_corrections":2,"control_endpoints":["models","accounts"],"dispatch_per_turn":1,"generation_per_turn":2,"kind":"h10-u2-continuation","model_turns":13,"recovery_apply":0,"starts":["h10-01"],"version":1},"prior_attempts":{"build":70,"correction":86,"offline-start":208,"offline-thread":59,"offline-turn":33,"proxy-start":42,"review":3},"prior_cap_ms":182297229,"proxy_slot":"s6","proxy_start":"s6-u2-h10-external-deadline-recovery","proxy_total":43,"replacement_work":{"home":"synthetic-reference-a","work":"synthetic-operations-guide-check"},"run_deadline_ms":1792949313976,"source":84,"starts":["h10-01"],"total_cap_ms":182297229,"turns":13,"version":56}}').items()}


U2_ALLOCATIONS[57] = json.loads('{"approval_plan_sha256":"43c839c75b1dc4614920c1d4247aede059ad0330b6ed63cbd2c010df69c3de0e","authority_apply":1,"content_corrections":1,"owner_message_id":"owner-h10-revalidation-20261026","parent":{"anchor_sha256":"6ed8c1ab466148badc5db1f00c366d2afe49cb42e98b803cb62cd81aaafc97ef","journal_sha256":"77962857b5f7adfb7317814e8c0315bf7a926d2a1b7cd65c38e6dc8251fcac99","last_seq":103,"last_sha256":"b6ea12b024aa0088d30edfa49f91fd78c9830ca59e44f7d4b3a05ecd98874908"},"parent_counts":{"authority-apply":2,"build":70,"control":75,"correction":86,"correction-content":2,"correction-source":84,"dispatch":81,"generation":163,"genesis":47,"host-dispatch":79,"input":92,"offline-start":211,"offline-thread":59,"offline-turn":33,"pause":6,"process-ended":42,"proxy-start":43,"resume":2,"review":3,"runtime-entered":42,"seal":5,"start":42,"stop":46,"thread":34,"thread-bound":33,"turn":89,"worker-result":76},"parent_rows":104,"parent_sealed":true,"parent_starts":42,"parent_version":56,"phase":"h10","policy":{"authority_apply":1,"content_corrections":1,"control_endpoints":["models","accounts"],"dispatch_per_turn":1,"generation_per_turn":2,"kind":"h10-u2-continuation","model_turns":17,"recovery_apply":0,"starts":["h10-01"],"version":1},"prior_attempts":{"build":72,"correction":89,"offline-start":222,"offline-thread":59,"offline-turn":33,"proxy-start":43,"review":7},"prior_cap_ms":182297229,"proxy_slot":"s6","proxy_start":"s6-h10-revalidation-20261026","proxy_total":44,"replacement_work":{"home":"synthetic-reference-a-regression","work":"synthetic-operations-guide-regression"},"run_deadline_ms":1792986085000,"source":87,"starts":["h10-01"],"total_cap_ms":193097229,"turns":17,"version":57}')


def u2_allocation(version=31):
    require(version in U2_ALLOCATIONS, "unallocated U2 version")
    return U2_ALLOCATIONS[version]


def u2_policy(version):
    return u2_allocation(version).get("policy", U2_POLICY)


def u2_anchor_fields(anchor):
    cfg=u2_allocation(anchor["version"])
    require(set(anchor)=={"version","approval","work","candidate","source_identity","total_deadline_ms","origin_wall_ms","origin_monotonic_ns","input_identity","recovery","activity_clock","launch_mode","launch_contract_sha256","approval_wall_ms","run_deadline_ms","direct_tool_policy"},"diagnostic anchor fields")
    require(type(anchor["version"]) is int and anchor["version"] in (31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57) and anchor["activity_clock"]=="mach_continuous_time_ns" and anchor["launch_mode"]=="trusted-native-runtime","diagnostic mode binding")
    for key in ("total_deadline_ms","origin_wall_ms","origin_monotonic_ns","approval_wall_ms","run_deadline_ms"):
        require(type(anchor[key]) is int and anchor[key]>0,"diagnostic clock type")
    require(anchor["approval_wall_ms"]<=anchor["origin_wall_ms"]<anchor["run_deadline_ms"]==cfg["run_deadline_ms"],"diagnostic deadline")
    for key in ("approval","work","candidate","source_identity","input_identity","launch_contract_sha256"):
        require(isinstance(anchor[key],str) and anchor[key],"diagnostic identity")
    require(anchor["direct_tool_policy"]=={"version":1,"mode":"direct","model":"gpt-6-astra","profiles":["clock","u2"],"approval":anchor["approval"]},"diagnostic direct policy")


def u2_budget_state(budget,rows,now):
    a=budget.anchor;u2_anchor_fields(a);r=a["recovery"];cfg=u2_allocation(a["version"])
    require(set(r)=={"owner_message_id","predecessor","accounting","checkpoint","resume_authorization","carry_active_ms","total_cap_ms","uncertainty_reserve_ms","closeout_reserve_ms","prior_attempts","transition"},"diagnostic recovery fields")
    def bound(ref):
        require(set(ref)=={"path","sha256"},"diagnostic reference")
        raw=control_read(ref["path"]);require(digest(raw)==ref["sha256"],"diagnostic input drift")
        v=json.loads(raw,object_pairs_hook=reject_duplicate_keys);require(canonical(v)==raw,"diagnostic canonical input");return v
    parent=r["predecessor"];require(set(parent)==set(cfg["parent"])|{"directory"} and all(parent[k]==v for k,v in cfg["parent"].items()),"diagnostic exact parent")
    old,prior=Budget.inspect_for_clock_recovery(parent["directory"],parent["anchor_sha256"])
    require(old.directory!=budget.directory and digest(control_read(old.path))==parent["journal_sha256"] and old.anchor["version"]==cfg["parent_version"] and prior["stopped"] and len(prior["rows"])==cfg["parent_rows"] and prior["prev"]==parent["last_sha256"],"diagnostic stopped predecessor")
    require(r["prior_attempts"]["proxy-start"]==cfg["prior_attempts"]["proxy-start"],"U2 unrecorded proxy attempt")
    pc=prior["counts"];require(all(pc.get(k,0)==v for k,v in cfg["parent_counts"].items()),"diagnostic inherited effects")
    require(type(r["carry_active_ms"]) is int and cfg["prior_cap_ms"]-(old.anchor["total_deadline_ms"]-prior["rows"][-1]["event"]["at_ms"])<=r["carry_active_ms"]<=cfg["total_cap_ms"],"diagnostic no usage refund")
    require(r["total_cap_ms"]==cfg["total_cap_ms"] and r["uncertainty_reserve_ms"]==858141 and r["closeout_reserve_ms"]==1200000 and a["total_deadline_ms"]==a["origin_wall_ms"]+cfg["total_cap_ms"]-r["carry_active_ms"] and set(r["prior_attempts"])==set(cfg["prior_attempts"]) and all(type(v) is int and cfg["prior_attempts"][k]<=v<=cfg["prior_attempts"][k]+64 for k,v in r["prior_attempts"].items()),"diagnostic fixed caps")
    require(bound(r["accounting"])=={"version":1,"approval":a["approval"],"work":a["work"],"active_ms":r["carry_active_ms"],"total_cap_ms":cfg["total_cap_ms"],"uncertainty_reserve_ms":858141,"closeout_reserve_ms":1200000,"prior_attempts":r["prior_attempts"]},"diagnostic accounting")
    cp=bound(r["checkpoint"]);require(cp=={"version":1,"approval":a["approval"],"work":a["work"],"input_identity":old.anchor["input_identity"],"journal_seq":cfg["parent"]["last_seq"],"journal_sha256":parent["last_sha256"],"sealed":cfg.get("parent_sealed",False),"pending":False,"process_ids":[]},"diagnostic checkpoint")
    auth=bound(r["resume_authorization"])
    require(set(auth)=={"version","owner_message_id","approval_plan_sha256","failure_evidence","u2_policy","allowed_starts","launch_contract_sha256"} and auth["version"]==1 and auth["owner_message_id"]==r["owner_message_id"]==cfg["owner_message_id"] and auth["approval_plan_sha256"]==cfg["approval_plan_sha256"] and auth["u2_policy"]==u2_policy(a["version"]) and auth["allowed_starts"]==cfg["starts"] and auth["launch_contract_sha256"]==a["launch_contract_sha256"],"diagnostic Owner binding")
    evidence=bound(auth["failure_evidence"]);require(evidence==cfg["parent"],"diagnostic failure evidence")
    require(a["approval"]==old.anchor["approval"] and a["work"]==old.anchor["work"] and r["transition"]=={**{"old_"+k:old.anchor[k] for k in ("candidate","source_identity","input_identity")},**{"new_"+k:a[k] for k in ("candidate","source_identity","input_identity")}},"diagnostic transition")
    counts=pc.copy()
    for k,v in r["prior_attempts"].items():require(v>=counts.get(k,0),"diagnostic attempt refund");counts[k]=v
    counts["correction-source"]=cfg["source"] if a["version"] >= 41 else r["prior_attempts"]["correction"];counts["correction-content"]=pc.get("correction-content",0) if a["version"] >= 41 else 0
    limits={'genesis':1,'proxy-start':1,'start':2,'runtime-entered':2,'control':4,'thread':2,'thread-bound':2,'input':12,'turn':12,'generation':24,'dispatch':12,'host-dispatch':12,'worker-result':11,'correction':2,'seal':1,'pause':1,'resume':1,'authority-apply':1,'stop':1,'process-ended':2}
    phase_name=cfg.get('phase','synthetic');turn_cap=cfg['turns']
    limits.update({k:turn_cap for k in ('input','turn','dispatch','host-dispatch')});limits.update({'generation':2*turn_cap,'worker-result':turn_cap-1})
    limits['correction']=cfg['content_corrections']
    used={};prev='';last=prior['rows'][-1]['event']['at_ms'];stopped=False;events=[];starts={};plans={};current=None;paused=None;pause_seq=None;excluded=0;sealed=None;applied=set()
    require(0<len(rows)<(400 if phase_name=='h10' else 200),'U2 bounded journal')
    for i,row in enumerate(rows):
        require(set(row)=={'event','sha256'},'U2 row');e=row['event'];sub=e['subject'];kind=e['kind'];start=e['start'];phase=e['phase'];at=e['at_ms']
        require(set(e)=={'seq','prev','approval','work','candidate','phase','start','kind','subject','at_ms'} and type(e['seq']) is int and e['seq']==i and e['prev']==prev and row['sha256']==digest(wire_bytes(e)) and all(e[k]==a[k] for k in ('approval','work','candidate')),'U2 journal chain')
        require(kind in limits and isinstance(sub,dict) and type(at) is int and last<=at<=now,'U2 event/time')
        used[kind]=used.get(kind,0)+1;require(used[kind]<=limits[kind] and (not stopped or kind=='process-ended'),'U2 cap/stop')
        require((i==0 and kind=='genesis' and phase==start=='controller' and sub=={'anchor_sha256':budget.anchor_sha256}) or (i>0 and kind!='genesis'),'U2 genesis')
        if kind in ('genesis','proxy-start','stop'):require(phase==start=='controller','U2 controller event')
        else:require(phase==phase_name and start in cfg['starts'],'U2 phase/start')
        if paused is not None:require(kind in ('resume','stop','process-ended'),'U2 activity while paused')
        if kind=='proxy-start':require(sub=={'slot':cfg.get('proxy_slot','s4'),'start_id':cfg['proxy_start']} and not starts,'U2 proxy')
        if kind=='start':
            require(used.get('proxy-start')==1 and start not in starts and start==cfg['starts'][len(starts)] and (not starts or starts[cfg['starts'][0]]['ended']) and sealed is None,'U2 start order')
            require(sub.get('execution_binding')=={'launch_mode':a['launch_mode'],'launch_contract_sha256':a['launch_contract_sha256'],'epoch_sha256':budget.anchor_sha256,'approval':a['approval'],'direct_tool_policy':a['direct_tool_policy']},'U2 execution binding')
            starts[start]={'entered':False,'ended':False,'controls':set(),'request':None,'thread':None};current=None
        if kind not in ('genesis','proxy-start','stop'):
            require(start in starts and not starts[start]['ended'],'U2 inactive runtime');slot=starts[start]
            if kind not in ('start','runtime-entered','process-ended'):require(slot['entered'],'U2 before runtime entry')
        if kind=='runtime-entered':require(not slot['entered'] and sub=={'start':start},'U2 runtime entry');slot['entered']=True
        if kind=='control':
            require(set(sub)=={'endpoint'} and sub['endpoint'] in ('models','accounts') and sub['endpoint'] not in slot['controls'] and slot['request'] is None,'U2 control retry/order');slot['controls'].add(sub['endpoint'])
        if kind=='thread':
            require(set(sub)=={'request'} and sub['request'] is not None and slot['request'] is None and slot['controls']=={'models','accounts'},'U2 thread order');slot['request']=sub['request']
        if kind=='thread-bound':
            require(set(sub)=={'request','thread'} and slot['request'] is not None and sub['request']==slot['request'] and slot['thread'] is None and isinstance(sub['thread'],str) and bool(sub['thread']) and all(v['thread']!=sub['thread'] for v in starts.values()),'U2 thread binding');slot['thread']=sub['thread']
        if kind=='input':
            require(slot['thread'] is not None and set(sub)=={'plan','input_sha256','manifest_sha256'} and isinstance(sub['plan'],str) and sub['plan'] and sub['plan'] not in plans and (current is None or plans[current]['generation']==2),'U2 input order')
            require(all(isinstance(sub[k],str) and len(sub[k])==64 for k in ('input_sha256','manifest_sha256')),'U2 input digest')
            current=sub['plan'];plans[current]={'start':start,'thread':slot['thread'],'began':False,'turn':None,'generation':0,'call':None,'host':False,'result':False}
        if kind=='turn':
            require(current is not None and set(sub)=={'thread','plan'} and sub=={'thread':slot['thread'],'plan':current} and not plans[current]['began'],'U2 turn binding');plans[current]['began']=True
        if kind in ('generation','dispatch','host-dispatch'):
            require(current is not None,'U2 effect before input');p=plans[current]
            require(p['began'] and p['start']==start and sub.get('plan')==current and sub.get('thread')==p['thread'] and isinstance(sub.get('turn'),str) and sub['turn'] and p['turn'] in (None,sub['turn']),'U2 effect identity')
            if kind=='generation':
                require(set(sub)=={'thread','turn','plan','generation'} and type(sub['generation']) is int and sub['generation']==p['generation']+1<=2 and (p['generation']==0 or (p['host'] and p['result'])),'U2 generation order/result');p['generation']=sub['generation'];p['turn']=sub['turn']
            elif kind=='dispatch':
                require(set(sub)=={'thread','turn','plan','call'} and p['generation']==1 and p['call'] is None and isinstance(sub['call'],str) and sub['call'] and all(v['call']!=sub['call'] for v in plans.values()),'U2 dispatch reuse/order');p['call']=sub['call']
            else:
                require(set(sub)=={'thread','turn','plan','call'} and p['generation']==1 and p['call'] is not None and sub['call']==p['call'] and not p['host'],'U2 host callback binding');p['host']=True
        if kind in ('worker-result','correction','authority-apply'):
            require(current is not None,'U2 host effect without plan');p=plans[current]
            require(p['start']==start and p['host'] and p['generation']==1 and not p['result'],'U2 host effect order')
        if kind=='worker-result':
            require(sealed is None and set(sub)=={'tool','result_sha256','result_identity','oracle_sha256'} and sub['tool'] in ('u2_read_file','u2_write_file','u2_verify') and all(isinstance(sub[k],str) and len(sub[k])==64 for k in ('result_sha256','result_identity','oracle_sha256')),'U2 worker result');p['result']=True
        if kind=='correction':require(sealed is None and set(sub)=={'oracle_sha256','failure','class'} and sub['class']=='content','U2 content correction')
        if kind=='seal':
            require(sealed is None and current is not None and plans[current]['generation']==2 and set(sub)=={'result_identity','oracle_sha256'} and all(isinstance(v,str) and len(v)==64 for v in sub.values()),'U2 seal');sealed=sub['result_identity']
        if kind=='pause':
            require(sealed is not None and paused is None and sub=={'reason':'owner-only','sealed_result':sealed},'U2 pause');paused=at;pause_seq=i
        if kind=='resume':
            require(paused is not None and sub=={'pause_seq':pause_seq},'U2 resume');excluded+=at-paused;paused=None
        if kind=='authority-apply':
            require(sealed is not None and used.get('resume')==1 and set(sub)=={'ticket_sha256','thread','turn','call'} and all(sub[k]==p[k] for k in ('thread','turn','call')) and isinstance(sub['ticket_sha256'],str) and len(sub['ticket_sha256'])==64 and sub['ticket_sha256'] not in applied,'U2 authority binding');applied.add(sub['ticket_sha256']);p['result']=True
        if kind=='stop':require(set(sub)=={'reason'} and isinstance(sub['reason'],str),'U2 stop');stopped=True
        if kind=='process-ended':require(sub.get('process_group_absent') is True and sub.get('start')==start,'U2 process close');slot['ended']=True
        counts[kind]=counts.get(kind,0)+1
        if kind=='correction':counts['correction-content']=counts.get('correction-content',0)+1
        events.append(e);prev=row['sha256'];last=at
    active=(paused if paused is not None else now)-excluded
    return {'events':events,'history_events':prior['history_events']+events,'rows':rows,'prev':prev,'counts':counts,'excluded_ms':excluded,'paused_at':paused,'stopped':stopped,'active_ms':active,'remaining_ms':min(a['total_deadline_ms']-active,a['run_deadline_ms']-now)}


class DiagnosticNumber(str):
    pass


def diagnostic_token_tree(raw):
    return json.loads(raw,object_pairs_hook=reject_duplicate_keys,parse_int=DiagnosticNumber,parse_float=DiagnosticNumber)


def diagnostic_token_summary(before,after):
    from decimal import Decimal
    out={"numeric_tokens":0,"representation_changes":0,"numeric_value_changes":0,"non_numeric_changes":0,"first_change":None}
    nodes=0
    def walk(a,b,depth=0):
        nonlocal nodes
        nodes+=1;require(nodes<=100000 and depth<=64,"diagnostic tree bound")
        if type(a) is DiagnosticNumber and type(b) is DiagnosticNumber:
            out["numeric_tokens"]+=1
            if a!=b:
                out["representation_changes"]+=1;out["numeric_value_changes"]+=int(Decimal(a)!=Decimal(b))
                if out["first_change"] is None:out["first_change"]={"ordinal":nodes,"kind":"number","same_decimal_value":Decimal(a)==Decimal(b)}
        elif type(a) is dict and type(b) is dict and a.keys()==b.keys():
            for key in sorted(a):walk(a[key],b[key],depth+1)
        elif type(a) is list and type(b) is list and len(a)==len(b):
            for av,bv in zip(a,b):walk(av,bv,depth+1)
        elif type(a) is not type(b) or a!=b:
            out["non_numeric_changes"]+=1
            if out["first_change"] is None:out["first_change"]={"ordinal":nodes,"kind":"non-number"}
    walk(before,after);return out


class Budget:
    """No implicit creation, repair, rollback or retry on resume."""
    def __init__(self, directory, anchor_sha256):
        self.directory = Path(directory)
        self.path = self.directory / "journal.jsonl"
        self.lock_path = self.directory / "append.lock"
        raw = control_read(self.directory / "anchor.json", 65536)
        require(digest(raw) == anchor_sha256, "budget anchor drift")
        self.anchor = json.loads(raw, object_pairs_hook=reject_duplicate_keys)
        require(canonical(self.anchor) == raw, "noncanonical budget anchor")
        self._anchor_fields(self.anchor)
        if self.anchor["version"] in (58, 59):
            self.os = execution_os(require, purpose="codex-v58")
            require(str(self.directory) == self.anchor["run_directory"], "v58-directory-binding")
        self.anchor_sha256 = anchor_sha256
        self.read()

    @staticmethod
    def _anchor_fields(anchor):
        if isinstance(anchor, dict) and anchor.get("version") == 59: return edit_u2.anchor_fields(anchor)
        if isinstance(anchor, dict) and anchor.get("version") == 58: return fresh_u2.anchor_fields(anchor)
        if isinstance(anchor,dict) and anchor.get("version") in (31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57):return u2_anchor_fields(anchor)
        if isinstance(anchor,dict) and anchor.get("version") in (24,25,26,27,28,29,30):return clock_anchor_fields(anchor)
        if isinstance(anchor,dict) and anchor.get("version") in (21,22,23):return diagnostic_anchor_fields(anchor)
        fields = {"version", "approval", "work", "candidate", "source_identity", "total_deadline_ms",
                  "origin_wall_ms", "origin_monotonic_ns", "input_identity"}
        require(isinstance(anchor, dict) and type(anchor.get("version")) is int and anchor["version"] in (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14,15,16,17,18,19,20), "budget version")
        require(set(anchor) == fields | ({"recovery"} if anchor["version"] >= 2 else set()) | ({"activity_clock"} if anchor["version"] >= 3 else set()) | ({"launch_mode", "launch_contract_sha256", "approval_wall_ms", "run_deadline_ms"} if anchor["version"] >= 4 else set()) | ({"direct_tool_policy"} if anchor["version"] == 20 else set()), "budget anchor fields")
        if anchor["version"] >= 4:
            require(anchor["launch_mode"] == "trusted-native-runtime" and isinstance(anchor["launch_contract_sha256"], str)
                    and len(anchor["launch_contract_sha256"]) == 64 and all(c in "0123456789abcdef" for c in anchor["launch_contract_sha256"]), "native launch contract")
            require(type(anchor["approval_wall_ms"]) is int and type(anchor["run_deadline_ms"]) is int
                    and 0 <= anchor["approval_wall_ms"] <= anchor["origin_wall_ms"]
                    and anchor["run_deadline_ms"] == anchor["approval_wall_ms"] + (83013443 if anchor["version"] == 20 else 47099443 if anchor["version"] == 19 else 46_800_000 if anchor["version"] == 18 else 43_200_000), "native segment deadline")
        if anchor["version"] >= 3:
            require(anchor["activity_clock"] == "mach_continuous_time_ns", "activity clock kind")
        for key in ("total_deadline_ms", "origin_wall_ms", "origin_monotonic_ns"):
            require(type(anchor[key]) is int and anchor[key] >= 0, "budget clock fields")
        for key in ("approval", "work", "candidate", "source_identity", "input_identity"):
            require(isinstance(anchor[key], str) and bool(anchor[key]), "budget identity fields")

    @staticmethod
    def _rows(raw):
        require(raw and raw.endswith(b"\n"), "missing or torn journal")
        rows = [json.loads(line, object_pairs_hook=reject_duplicate_keys) for line in raw.splitlines()]
        require(all(wire_bytes(row) == line for row, line in zip(rows, raw.splitlines())), "noncanonical journal row")
        return rows

    def _lineage(self, rows):
        if self.anchor["version"] in (58, 59):
            execution_policy(self.anchor).contract(self.anchor, self.fresh_bound)
            return [(self.anchor, self.anchor_sha256, rows)]
        """Read immutable predecessors; only the selected epoch supplies the live clock."""
        segments, seen = [], set()
        anchor, anchor_sha, directory = self.anchor, self.anchor_sha256, self.directory
        while True:
            self._anchor_fields(anchor)
            require(anchor_sha not in seen and len(segments) < (9 if self.anchor["version"] == 14 else 15 if self.anchor["version"] == 20 else 14 if self.anchor["version"] == 19 else 13 if self.anchor["version"] == 18 else 12 if self.anchor["version"] == 17 else 11 if self.anchor["version"] == 16 else 10 if self.anchor["version"] == 15 else 8), "cyclic or excessive epochs")
            seen.add(anchor_sha)
            segments.append((anchor, anchor_sha, rows))
            if anchor["version"] == 1:
                break
            recovery = anchor["recovery"]
            required = {"owner_message_id", "predecessor", "accounting", "checkpoint", "carry_active_ms", "total_cap_ms", "uncertainty_reserve_ms", "closeout_reserve_ms", "transition"}
            if anchor["version"] >= 3:
                required.add("resume_authorization")
            if anchor["version"] >= 4: required.add("prior_attempts")
            require(isinstance(recovery, dict) and set(recovery) == required, "recovery fields")
            require(isinstance(recovery["owner_message_id"], str) and recovery["owner_message_id"], "recovery Owner decision missing")
            cap = 139114000 if anchor["version"] == 20 else 103_200_000 if anchor["version"] == 19 else 100_800_000 if anchor["version"] >= 4 else (86_400_000 if anchor["version"] == 3 else 57_600_000)
            require(recovery["total_cap_ms"] == cap and recovery["uncertainty_reserve_ms"] == 858_141 and recovery["closeout_reserve_ms"] == 1_200_000, "recovery cap or reserve changed")
            carry = recovery["carry_active_ms"]
            require(type(carry) is int and 0 <= carry <= cap and anchor["total_deadline_ms"] == anchor["origin_wall_ms"] + cap - carry, "recovery time carry")
            inputs = {}
            for name in (("accounting", "checkpoint", "resume_authorization") if anchor["version"] >= 3 else ("accounting", "checkpoint")):
                ref = recovery[name]
                require(isinstance(ref, dict) and set(ref) == {"path", "sha256"}, "recovery input reference")
                raw = control_read(ref["path"])
                require(digest(raw) == ref["sha256"], "recovery input drift")
                inputs[name] = json.loads(raw, object_pairs_hook=reject_duplicate_keys)
                require(canonical(inputs[name]) == raw, "noncanonical recovery JSON")
            accounting, checkpoint = inputs["accounting"], inputs["checkpoint"]
            require(set(accounting) == {"version", "approval", "work", "active_ms", "total_cap_ms", "uncertainty_reserve_ms", "closeout_reserve_ms"} | ({"prior_attempts"} if anchor["version"] >= 4 else set()) and type(accounting["version"]) is int and accounting["version"] == 1, "accounting fields")
            require(type(accounting["active_ms"]) is int and accounting["active_ms"] == carry and all(accounting[k] == recovery[k] for k in ("total_cap_ms", "uncertainty_reserve_ms", "closeout_reserve_ms")) and all(accounting[k] == anchor[k] for k in ("approval", "work")), "accounting carry drift")
            if anchor["version"] >= 4:
                attempts = recovery["prior_attempts"]
                require(isinstance(attempts, dict) and set(attempts) == {"proxy-start", "offline-start", "offline-thread", "offline-turn", "build", "correction", "review"}
                        and attempts == accounting["prior_attempts"] and all(type(v) is int and v >= 0 for v in attempts.values()), "prior attempts binding")
                require(attempts["correction"] >= 4 and attempts["build"] >= 3 and attempts["review"] >= 3 and attempts["offline-start"] >= 10, "prior attempts refund")
            predecessor = recovery["predecessor"]
            require(isinstance(predecessor, dict) and set(predecessor) == {"directory", "anchor_sha256", "journal_sha256", "last_seq", "last_sha256"}, "predecessor fields")
            parent_dir = Path(predecessor["directory"])
            require(parent_dir != directory and parent_dir.is_absolute() and parent_dir.resolve(strict=True) == parent_dir, "predecessor directory")
            raw_anchor = control_read(parent_dir / "anchor.json", 65536)
            raw_journal = control_read(parent_dir / "journal.jsonl")
            require(digest(raw_anchor) == predecessor["anchor_sha256"] and digest(raw_journal) == predecessor["journal_sha256"], "predecessor bytes drift")
            parent = json.loads(raw_anchor, object_pairs_hook=reject_duplicate_keys)
            require(canonical(parent) == raw_anchor, "noncanonical predecessor anchor")
            parent_rows = self._rows(raw_journal)
            require(type(predecessor["last_seq"]) is int and parent_rows and parent_rows[-1]["event"]["seq"] == predecessor["last_seq"] and parent_rows[-1]["sha256"] == predecessor["last_sha256"], "predecessor rollback")
            require(set(checkpoint) == {"version", "approval", "work", "input_identity", "journal_seq", "journal_sha256", "sealed", "pending", "process_ids"} and type(checkpoint["version"]) is int and checkpoint["version"] == 1, "clock checkpoint fields")
            require(type(checkpoint["journal_seq"]) is int and all(checkpoint[k] == parent[k] == anchor[k] for k in ("approval", "work")) and checkpoint["input_identity"] == parent["input_identity"] and checkpoint["journal_seq"] == predecessor["last_seq"] and checkpoint["journal_sha256"] == predecessor["last_sha256"], "clock checkpoint identity")
            require(checkpoint["sealed"] is False and checkpoint["pending"] is False, "clock recovery cannot resolve pending or sealed state")
            require(isinstance(checkpoint["process_ids"], list) and all(type(pid) is int and pid > 1 for pid in checkpoint["process_ids"]), "clock checkpoint processes")
            transition = recovery["transition"]
            require(isinstance(transition, dict) and set(transition) == {"old_candidate", "old_source_identity", "old_input_identity", "new_candidate", "new_source_identity", "new_input_identity"}, "clock transition fields")
            require(all(transition["old_" + k] == parent[k] and transition["new_" + k] == anchor[k] for k in ("candidate", "source_identity", "input_identity")), "clock transition drift")
            if anchor["version"] >= 3:
                authorization = inputs["resume_authorization"]
                require(set(authorization) == {"version", "owner_message_id", "failure_class", "stop_seq", "stop_sha256", "failure_evidence", "processes_and_fds_absent", "input_stable", "pending", "allowed_next_start"} | ({"launch_mode", "launch_contract_sha256", "approval_plan_sha256"} if anchor["version"] >= 4 else set()) | ({"observed_effects", "network"} if anchor["version"] in (7,8,9,10,11,12,13,14,15,16,17,18,19,20) else {"observed_effects", "network", "diagnostic_evidence"} if anchor["version"] == 6 else {"effects_zero"}), "resume authorization fields")
                require(authorization["version"] == 1 and authorization["owner_message_id"] == recovery["owner_message_id"]
                        and authorization["failure_class"] == ("native-clock10-prepare-rejected" if anchor["version"]==20 else "native-runtime-expiry-prelaunch-rejected" if anchor["version"]==19 else "native-clock09-document-policy-rejected" if anchor["version"]==18 else "native-proxy-clock08-preface-rejected" if anchor["version"]==17 else "native-late-first-notice-rejected" if anchor["version"]==16 else "native-proxy-slot-prelaunch-rejected" if anchor["version"]==15 else "native-disabled-mcp-inventory-rejected" if anchor["version"] in (14,15,16,17,18,19,20) else "native-initialize-notification-rejected" if anchor["version"] in (9,10,11,12,13,14,15,16,17,18,19,20) else "native-model-encoding-ineligible" if anchor["version"] == 8 else "native-proxy-preface-start-rejected" if anchor["version"] == 7 else "native-catalog-tcp-connect-timeout" if anchor["version"] == 6 else "native-input-mode-prelaunch" if anchor["version"] == 5 else "native-transition-after-correction06" if anchor["version"] == 4 else "pre-auth-config-root-missing")
                        and (canonical(authorization["observed_effects"]) == canonical({'runtime_starts': 10, 'runtime_entered': 10, 'control_reservations': 13, 'auth_admissions_observed': 9, 'credential_storage_read_call_count': None, 'fd_issued': 8, 'fd_released': 8, 'thread_reservations': 4, 'model_threads': 3, 'model_turns': 0, 'generation_sends': 0, 'pending_apply': False, 'sealed': False, 'leases': 0}) if anchor["version"]==20 else canonical(authorization["observed_effects"]) == canonical({'runtime_starts': 9, 'runtime_entered': 9, 'control_reservations': 11, 'auth_admissions_observed': 8, 'credential_storage_read_call_count': None, 'fd_issued': 6, 'fd_released': 6, 'thread_reservations': 3, 'model_threads': 2, 'model_turns': 0, 'generation_sends': 0, 'pending_apply': False, 'sealed': False, 'leases': 0}) if anchor["version"] in (18,19,20) else canonical(authorization["observed_effects"]) == canonical({'runtime_starts': 8, 'runtime_entered': 8, 'control_reservations': 9, 'auth_admissions_observed': 7, 'credential_storage_read_call_count': None, 'fd_issued': 4, 'fd_released': 4, 'thread_reservations': 2, 'model_threads': 1, 'model_turns': 0, 'generation_sends': 0, 'pending_apply': False, 'sealed': False, 'leases': 0}) if anchor["version"]==17 else canonical(authorization["observed_effects"]) == canonical({'runtime_starts': 7, 'runtime_entered': 7, 'control_reservations': 8, 'auth_admissions_observed': 6, 'credential_storage_read_call_count': None, 'fd_issued': 4, 'fd_released': 4, 'thread_reservations': 2, 'model_threads': 1, 'model_turns': 0, 'generation_sends': 0, 'pending_apply': False, 'sealed': False, 'leases': 0}) if anchor["version"]==16 else canonical(authorization["observed_effects"]) == canonical({'runtime_starts': 6, 'runtime_entered': 6, 'control_reservations': 6, 'auth_admissions_observed': 5, 'credential_storage_read_call_count': None, 'fd_issued': 2, 'fd_released': 2, 'thread_reservations': 1, 'model_threads': 0, 'model_turns': 0, 'generation_sends': 0, 'pending_apply': False, 'sealed': False, 'leases': 0}) if anchor["version"] in (14,15,16,17,18,19,20) else canonical(authorization["observed_effects"]) == canonical({'runtime_starts': 5, 'runtime_entered': 5, 'control_reservations': 4, 'auth_admissions_observed': 4, 'credential_storage_read_call_count': None, 'fd_issued': 1, 'fd_released': 1, 'model_threads': 0, 'model_turns': 0, 'generation_sends': 0, 'pending_apply': False, 'sealed': False, 'leases': 0}) if anchor["version"] in (9,10,11,12,13,14,15,16,17,18,19,20) else canonical(authorization["observed_effects"]) == canonical({'runtime_starts': 4, 'runtime_entered': 4, 'control_reservations': 3, 'auth_admissions_observed': 3, 'credential_storage_read_call_count': None, 'fd_issued': 1, 'fd_released': 1, 'model_threads': 0, 'model_turns': 0, 'generation_sends': 0, 'pending_apply': False, 'sealed': False, 'leases': 0}) if anchor["version"]==8 else canonical(authorization["observed_effects"]) == canonical({'runtime_starts': 3, 'runtime_entered': 3, 'control_reservations': 2, 'auth_admissions_observed': 2, 'credential_storage_read_call_count': None, 'fd_issued': 0, 'model_threads': 0, 'model_turns': 0, 'generation_sends': 0, 'pending_apply': False, 'sealed': False, 'leases': 0}) if anchor["version"] == 7 else canonical(authorization["observed_effects"]) == canonical({'runtime_starts': 2, 'runtime_entered': 2, 'control_reservations': 1, 'auth_admissions_observed': 1, 'credential_storage_read_call_count': None, 'fd_issued': 0, 'model_threads': 0, 'model_turns': 0, 'generation_sends': 0, 'pending_apply': False, 'sealed': False, 'leases': 0}) if anchor["version"] == 6 else authorization["effects_zero"] is True) and authorization["processes_and_fds_absent"] is True
                        and authorization["input_stable"] is True and authorization["pending"] is False
                        and authorization["allowed_next_start"] == ("clock-11" if anchor["version"]==20 else "clock-10" if anchor["version"] in (18,19) else "clock-09" if anchor["version"]==17 else "clock-08" if anchor["version"]==16 else "clock-07" if anchor["version"] in (14,15,16,17,18,19,20) else "clock-06" if anchor["version"] in (9,10,11,12,13,14,15,16,17,18,19,20) else "clock-05" if anchor["version"]==8 else "clock-04" if anchor["version"] == 7 else "clock-03" if anchor["version"] == 6 else "clock-02") and parent["version"] == (19 if anchor["version"]==20 else 18 if anchor["version"]==19 else 17 if anchor["version"]==18 else 16 if anchor["version"]==17 else 15 if anchor["version"]==16 else 14 if anchor["version"]==15 else 13 if anchor["version"]==14 else 8 if anchor["version"] in (9,10,11,12,13,14,15,16,17,18,19,20) else 7 if anchor["version"]==8 else 6 if anchor["version"] == 7 else 5 if anchor["version"] == 6 else 4 if anchor["version"] == 5 else 2), "limited resume contract")
                if anchor["version"] >= 4:
                    require(authorization["launch_mode"] == anchor["launch_mode"] and authorization["launch_contract_sha256"] == anchor["launch_contract_sha256"]
                            and isinstance(authorization["approval_plan_sha256"], str) and len(authorization["approval_plan_sha256"]) == 64, "native authorization binding")
                stop_seq = authorization["stop_seq"]
                require(type(stop_seq) is int and 0 <= stop_seq < len(parent_rows), "resume stop sequence")
                stop = parent_rows[stop_seq]
                expected_reason = "RPC refused or identity drift" if anchor["version"]==20 else "runtime expiry" if anchor["version"]==19 else "RPC refused or identity drift" if anchor["version"]==18 else "runtime stdout closed" if anchor["version"]==17 else "fixture notice phase or duplicate" if anchor["version"]==16 else "proxy slot/order" if anchor["version"]==15 else "RPC refused or identity drift" if anchor["version"] in (14,15,16,17,18,19,20) else "unknown native notification" if anchor["version"] in (9,10,11,12,13,14,15,16,17,18,19,20) else "aliased or nonprivate control file" if anchor["version"] == 5 else "runtime stdout closed"
                require(stop["sha256"] == authorization["stop_sha256"] and stop["event"]["kind"] == "stop"
                        and stop["event"]["subject"] == {"reason": expected_reason}, "resume stop identity")
                ref = authorization["failure_evidence"]
                require(set(ref) == {"path", "sha256"} and digest(control_read(ref["path"])) == ref["sha256"], "failure evidence drift")
                if anchor["version"] == 20:
                    evidence=json.loads(control_read(ref["path"]),object_pairs_hook=reject_duplicate_keys)
                    require(predecessor["anchor_sha256"] == '1f220e702a70eb24c1483f9a533a4068cc6cc585e28bc1ee7632f1d17f8fbf2a' and predecessor["journal_sha256"] == '705be91b5bb8099df1aea97d8b2998b22bba96aea726e8bed54b4eacd5269a74' and stop_seq==8 and stop["sha256"]=='6600df7cb59cc188114a6f607c8246f07bd6d3636bc2025c2037d01bccdd1bed' and len(parent_rows)==10 and parent_rows[-1]["event"]["kind"]=="process-ended" and parent_rows[-1]["event"]["subject"].get("process_group_absent") is True,"exact clock10 prepare stop recovery")
                    require(canonical(evidence)==canonical({'stop_seq': 8, 'stop_sha256': '6600df7cb59cc188114a6f607c8246f07bd6d3636bc2025c2037d01bccdd1bed', 'epoch_anchor_sha256': '1f220e702a70eb24c1483f9a533a4068cc6cc585e28bc1ee7632f1d17f8fbf2a', 'epoch_journal_sha256': '705be91b5bb8099df1aea97d8b2998b22bba96aea726e8bed54b4eacd5269a74', 'last_seq': 9, 'last_sha256': 'fd7abc3147393e3bcc4a0c761d022288f518ad8108c20d0fc7e06e035c1b20d1', 'runtime_start': 'clock-10', 'proxy_starts': 12, 'observed_effects': {'runtime_starts': 10, 'runtime_entered': 10, 'control_reservations': 13, 'auth_admissions_observed': 9, 'credential_storage_read_call_count': None, 'fd_issued': 8, 'fd_released': 8, 'thread_reservations': 4, 'model_threads': 3, 'model_turns': 0, 'generation_sends': 0, 'pending_apply': False, 'sealed': False, 'leases': 0}, 'all_processes_absent': True, 'protected_auth_metadata_equal': True, 'source_closeout_sha256': '157e16674f9ac82f94249a7db757c82d769d7c38337ae7ae372933b8e5674a9e'}),"clock10 prepare recovery observed effects")
                    require(authorization["network"]=={"host":"chatgpt.com","port":443,"peer":"104.18.32.47"} and authorization["approval_plan_sha256"]=='36d285e77268b845fc065e534317b5a109e43e3d9832a781d7e8ff738832a12c',"clock10 prepare recovery approval")
                    require(anchor["approval_wall_ms"]==parent["approval_wall_ms"] and anchor["run_deadline_ms"]==1792892355443 and recovery["prior_attempts"]=={'proxy-start': 12, 'offline-start': 55, 'offline-thread': 54, 'offline-turn': 30, 'build': 24, 'correction': 35, 'review': 3},"clock10 prepare recovery caps")
                elif anchor["version"] == 19:
                    evidence=json.loads(control_read(ref["path"]),object_pairs_hook=reject_duplicate_keys)
                    require(predecessor["anchor_sha256"] == '3f6ccc70d74f65dacfa9aa1a86596aca2f4b101247b473f1de36932add9af23e' and predecessor["journal_sha256"] == '0ebcf2563c27e404eecb592120d1197e43d37ca578f09f07ff8f01e60f0ccd33' and stop_seq==2 and stop["sha256"]=='eefea7cff30d02066d2013be34aa050b70de48997b5e849a05dff86c0fc0abaf' and len(parent_rows)==3 and [r["event"]["kind"] for r in parent_rows]==["genesis","proxy-start","stop"],"exact expiry prelaunch stop recovery")
                    require(canonical(evidence)==canonical({'stop_seq': 2, 'stop_sha256': 'eefea7cff30d02066d2013be34aa050b70de48997b5e849a05dff86c0fc0abaf', 'epoch_anchor_sha256': '3f6ccc70d74f65dacfa9aa1a86596aca2f4b101247b473f1de36932add9af23e', 'epoch_journal_sha256': '0ebcf2563c27e404eecb592120d1197e43d37ca578f09f07ff8f01e60f0ccd33', 'last_seq': 2, 'last_sha256': 'eefea7cff30d02066d2013be34aa050b70de48997b5e849a05dff86c0fc0abaf', 'runtime_start': None, 'proxy_starts': 11, 'observed_effects': {'auth_admissions_observed': 8, 'control_reservations': 11, 'credential_storage_read_call_count': None, 'fd_issued': 6, 'fd_released': 6, 'generation_sends': 0, 'leases': 0, 'model_threads': 2, 'model_turns': 0, 'pending_apply': False, 'runtime_entered': 9, 'runtime_starts': 9, 'sealed': False, 'thread_reservations': 3}, 'all_processes_absent': True, 'protected_auth_metadata_equal': True, 'source_closeout_sha256': 'a5b11246158240378e277c08e4ea01ce9a211c7310e5135ce9bd6ff9b5768a69', 'runtime_expiry_overshoot_ms': 7}),"expiry prelaunch recovery observed effects")
                    require(authorization["network"]=={"host":"chatgpt.com","port":443,"peer":"104.18.32.47"} and authorization["approval_plan_sha256"]=='7482da67b9ef77f9c8c504e9927f8c639dcaa7b8b31601ec75400a4ac8b013a7',"expiry prelaunch recovery approval")
                    require(anchor["approval_wall_ms"]==parent["approval_wall_ms"] and anchor["run_deadline_ms"]==parent["run_deadline_ms"]+299443 and recovery["prior_attempts"]=={'proxy-start': 11, 'offline-start': 41, 'offline-thread': 40, 'offline-turn': 30, 'build': 20, 'correction': 30, 'review': 3},"expiry prelaunch recovery caps")
                elif anchor["version"] == 18:
                    evidence=json.loads(control_read(ref["path"]),object_pairs_hook=reject_duplicate_keys)
                    require(predecessor["anchor_sha256"] == '3d3f1d4a870ba769eac30624e16669c1b501ef2bd1dc42efbf50bc0ae9304c93' and predecessor["journal_sha256"] == '58c69e3ef5153daec74f1b9925fc8ea62185b28239d4988f5ffd6f2ae48c4a48' and stop_seq==8 and stop["sha256"]=='3d177bec5d3e99f03bed17da3b9fc1957919a3236b1a18df45869a8e73205fee' and len(parent_rows)==10 and parent_rows[-1]["event"]["kind"]=="process-ended" and parent_rows[-1]["event"]["subject"].get("process_group_absent") is True,"exact clock09 document policy stop recovery")
                    require(canonical(evidence)==canonical({'all_processes_absent': True, 'epoch_anchor_sha256': '3d3f1d4a870ba769eac30624e16669c1b501ef2bd1dc42efbf50bc0ae9304c93', 'epoch_journal_sha256': '58c69e3ef5153daec74f1b9925fc8ea62185b28239d4988f5ffd6f2ae48c4a48', 'last_seq': 9, 'last_sha256': '5e1e1a59d87cc5b062b1457209a1c1172583edfa1aef631e6ffcc5377c9092a0', 'observed_effects': {'auth_admissions_observed': 8, 'control_reservations': 11, 'credential_storage_read_call_count': None, 'fd_issued': 6, 'fd_released': 6, 'generation_sends': 0, 'leases': 0, 'model_threads': 2, 'model_turns': 0, 'pending_apply': False, 'runtime_entered': 9, 'runtime_starts': 9, 'sealed': False, 'thread_reservations': 3}, 'protected_auth_metadata_equal': True, 'runtime_start': 'clock-09', 'source_closeout_sha256': '1597608563c4f4150df85a482de3d4179960db07425ff4b167fa50273010b1cb', 'stop_seq': 8, 'stop_sha256': '3d177bec5d3e99f03bed17da3b9fc1957919a3236b1a18df45869a8e73205fee'}),"clock09 document policy recovery observed effects")
                    require(authorization["network"]=={"host":"chatgpt.com","port":443,"peer":"104.18.32.47"} and authorization["approval_plan_sha256"]=='60c6699f961d18b7a04d878cf6717d372e546500c2ecbb61dff579db1b4f70b2',"clock09 document policy recovery approval")
                    require(anchor["approval_wall_ms"] == parent["approval_wall_ms"] and anchor["run_deadline_ms"] == parent["run_deadline_ms"] + 3_600_000 and recovery["prior_attempts"] == {'proxy-start': 10, 'offline-start': 41, 'offline-thread': 40, 'offline-turn': 30, 'build': 19, 'correction': 28, 'review': 3},"clock09 document policy recovery caps")
                elif anchor["version"] == 17:
                    evidence=json.loads(control_read(ref["path"]),object_pairs_hook=reject_duplicate_keys)
                    require(predecessor["anchor_sha256"] == 'd89165fdbc742f58ee1f66c7f9749efe52c448ffd2d45bcbfc46d79458f194f1' and predecessor["journal_sha256"] == '28bbd1a7ee5dc14beaeed3b069aeda42ac8d7c73cc5e695726bad243b4c19340' and stop_seq==5 and stop["sha256"]=='91cb08208cbee63cdd313930d40fd24f01979efb7d5ae41b5b44ae5dbb85b753' and len(parent_rows)==7 and parent_rows[-1]["event"]["kind"]=="process-ended" and parent_rows[-1]["event"]["subject"].get("process_group_absent") is True,"exact clock08 preface stop recovery")
                    require(canonical(evidence)==canonical({'stop_seq': 5, 'stop_sha256': '91cb08208cbee63cdd313930d40fd24f01979efb7d5ae41b5b44ae5dbb85b753', 'epoch_anchor_sha256': 'd89165fdbc742f58ee1f66c7f9749efe52c448ffd2d45bcbfc46d79458f194f1', 'epoch_journal_sha256': '28bbd1a7ee5dc14beaeed3b069aeda42ac8d7c73cc5e695726bad243b4c19340', 'last_seq': 6, 'last_sha256': '08ea6d3c95395259d37b311287f18c3e35ad8750863af8fa5dfb2246eb1334bf', 'runtime_start': 'clock-08', 'observed_effects': {'runtime_starts': 8, 'runtime_entered': 8, 'control_reservations': 9, 'auth_admissions_observed': 7, 'credential_storage_read_call_count': None, 'fd_issued': 4, 'fd_released': 4, 'thread_reservations': 2, 'model_threads': 1, 'model_turns': 0, 'generation_sends': 0, 'pending_apply': False, 'sealed': False, 'leases': 0}, 'all_processes_absent': True, 'protected_auth_metadata_equal': True, 'source_closeout_sha256': '073e324afc595d43595fbfdf0efad93093300066324b316e1236669e0bd00571'}),"clock08 preface recovery observed effects")
                    require(authorization["network"]=={"host":"chatgpt.com","port":443,"peer":"104.18.32.47"} and authorization["approval_plan_sha256"]=='baf6ccbbc8ce007392d241500c877d55bf29849c3c7732d2da0e9b22fe76d7e7',"clock08 preface recovery approval")
                    require(anchor["approval_wall_ms"]==parent["approval_wall_ms"] and anchor["run_deadline_ms"]==parent["run_deadline_ms"] and recovery["prior_attempts"]=={'proxy-start': 9, 'offline-start': 41, 'offline-thread': 40, 'offline-turn': 30, 'build': 17, 'correction': 25, 'review': 3},"clock08 preface recovery caps")
                elif anchor["version"] == 16:
                    evidence=json.loads(control_read(ref["path"]),object_pairs_hook=reject_duplicate_keys)
                    require(predecessor["anchor_sha256"] == "ecc7ad45a0a5d928a8b9e371f675aa4994586c593dddde703c783dd918697e57" and predecessor["journal_sha256"] == "46e60a4d1084ea26f237044ffdba529f8afecf2afb7f7aa79a3307deaa9018c7" and stop_seq==8 and stop["sha256"]=="d5bcbd3aea715062d6f971a87d176cb6056aa48f64a459b4b547c747aaad0fd5" and len(parent_rows)==10 and parent_rows[-1]["event"]["kind"]=="process-ended" and parent_rows[-1]["event"]["subject"].get("process_group_absent") is True,"exact late-notice stop recovery")
                    require(canonical(evidence)==canonical({'stop_seq': 8, 'stop_sha256': 'd5bcbd3aea715062d6f971a87d176cb6056aa48f64a459b4b547c747aaad0fd5', 'epoch_anchor_sha256': 'ecc7ad45a0a5d928a8b9e371f675aa4994586c593dddde703c783dd918697e57', 'epoch_journal_sha256': '46e60a4d1084ea26f237044ffdba529f8afecf2afb7f7aa79a3307deaa9018c7', 'last_seq': 9, 'last_sha256': 'bb4e264ac6e510f29b604f0d10be8b6e06f3859ebfef67afbeea73c320183795', 'runtime_start': 'clock-07', 'observed_effects': {'runtime_starts': 7, 'runtime_entered': 7, 'control_reservations': 8, 'auth_admissions_observed': 6, 'credential_storage_read_call_count': None, 'fd_issued': 4, 'fd_released': 4, 'thread_reservations': 2, 'model_threads': 1, 'model_turns': 0, 'generation_sends': 0, 'pending_apply': False, 'sealed': False, 'leases': 0}, 'all_processes_absent': True, 'protected_auth_metadata_equal': True, 'source_closeout_sha256': '77bb706ba754e9608a82a01acb4b3845cfc77ec557e93486af23a9064a457cea'}),"late-notice recovery observed effects")
                    require(authorization["network"]=={"host":"chatgpt.com","port":443,"peer":"104.18.32.47"} and authorization["approval_plan_sha256"]=="2ef5ca1c7bbaadf20220e54f82fa62835a7467b5634fca33be1b7f7e2cd30ea1","late-notice recovery approval")
                    require(anchor["approval_wall_ms"]==parent["approval_wall_ms"] and anchor["run_deadline_ms"]==parent["run_deadline_ms"] and recovery["prior_attempts"]=={"proxy-start":8,"offline-start":41,"offline-thread":40,"offline-turn":30,"build":16,"correction":24,"review":3},"late-notice recovery caps")
                elif anchor["version"] == 15:
                    evidence=json.loads(control_read(ref["path"]),object_pairs_hook=reject_duplicate_keys)
                    require(predecessor["anchor_sha256"] == '86f36f10035ff31e554d2f2d8a14fc8c5be7a18c990e3301dd8706ed4c88b959' and predecessor["journal_sha256"] == '73c562647c7bfdee3f57ea1fd82c653b3ff1d4e17e931d2d84615d735e997736' and stop_seq==1 and stop["sha256"]=='5badc1256fa299bb8d9b07177df3b93caa2218a5c30721e25f6c37190a1f71ca' and len(parent_rows)==2,"exact prelaunch stop recovery")
                    require(canonical(evidence)==canonical({'stop_seq': 1, 'stop_sha256': '5badc1256fa299bb8d9b07177df3b93caa2218a5c30721e25f6c37190a1f71ca', 'epoch_anchor_sha256': '86f36f10035ff31e554d2f2d8a14fc8c5be7a18c990e3301dd8706ed4c88b959', 'epoch_journal_sha256': '73c562647c7bfdee3f57ea1fd82c653b3ff1d4e17e931d2d84615d735e997736', 'observed_effects': {'auth_admissions_observed': 5, 'control_reservations': 6, 'credential_storage_read_call_count': None, 'fd_issued': 2, 'fd_released': 2, 'generation_sends': 0, 'leases': 0, 'model_threads': 0, 'model_turns': 0, 'pending_apply': False, 'runtime_entered': 6, 'runtime_starts': 6, 'sealed': False, 'thread_reservations': 1}, 'prelaunch_added': {'runtime': 0, 'proxy': 0, 'auth': 0, 'fd': 0}, 'all_processes_absent': True, 'source_closeout_sha256': 'c4f5c2d7d8ec3150cc4575a054287a383fe5ad6186c1a4fd53c4f1cbc6bb7b2c'}),"prelaunch recovery observed effects")
                    require(authorization["network"]=={"host":"chatgpt.com","port":443,"peer":"104.18.32.47"} and authorization["approval_plan_sha256"]=='299d45627b4e715b5af7b84db3ae98b6fe8c941b4505e4f7be37e7bbbe12b4fe',"prelaunch recovery approval")
                    require(anchor["approval_wall_ms"]==parent["approval_wall_ms"] and anchor["run_deadline_ms"]==parent["run_deadline_ms"] and recovery["prior_attempts"]=={"proxy-start":7,"offline-start":41,"offline-thread":40,"offline-turn":30,"build":15,"correction":23,"review":3},"prelaunch recovery caps")
                elif anchor["version"] == 14:
                    evidence=json.loads(control_read(ref["path"]),object_pairs_hook=reject_duplicate_keys)
                    require(predecessor["anchor_sha256"] == '84e944911a9f081f4f93b9ff3fdffaeb3fcc9829b4a2f5e3772788008e5e4ec2' and predecessor["journal_sha256"] == '5b099d10219a9d808c802df8a4690d757403a5c9194fbbb6fbb780c34cff8acc' and stop_seq==7 and stop["sha256"]=='d63b81072bf3731634a3d06421ab59dba275f1aa469de95ee11b6efb011c2c73' and len(parent_rows)==9 and parent_rows[8]["event"]["kind"]=="process-ended" and parent_rows[8]["event"]["subject"].get("process_group_absent") is True,"exact MCP stop recovery")
                    require(canonical(evidence)==canonical({'stop_seq': 7, 'stop_sha256': 'd63b81072bf3731634a3d06421ab59dba275f1aa469de95ee11b6efb011c2c73', 'epoch_anchor_sha256': '84e944911a9f081f4f93b9ff3fdffaeb3fcc9829b4a2f5e3772788008e5e4ec2', 'epoch_journal_sha256': '5b099d10219a9d808c802df8a4690d757403a5c9194fbbb6fbb780c34cff8acc', 'runtime_start': 'clock-06', 'observed_effects': {'runtime_starts': 6, 'runtime_entered': 6, 'control_reservations': 6, 'auth_admissions_observed': 5, 'credential_storage_read_call_count': None, 'fd_issued': 2, 'fd_released': 2, 'thread_reservations': 1, 'model_threads': 0, 'model_turns': 0, 'generation_sends': 0, 'pending_apply': False, 'sealed': False, 'leases': 0}, 'all_processes_absent': True, 'protected_auth_metadata_equal': True, 'error_message_sha256': '683a60aa4704e4f60a79239aad9fe1930be82644746fcde3f12628a443fbdd59', 'source_closeout_sha256': 'fab23230235580a7bbfb5c165e81d23a3eaa2732b7aad8b1b9d2bb5d9fb61684'}),"MCP recovery observed effects")
                    require(authorization["network"]=={"host":"chatgpt.com","port":443,"peer":"104.18.32.47"} and authorization["approval_plan_sha256"]=='5ff34b8eecadd0c1e7b5cd56a87e6828efa2ddd65c5e5c68d01122466b653c23',"MCP recovery approval")
                    require(anchor["approval_wall_ms"]==parent["approval_wall_ms"] and anchor["run_deadline_ms"]==parent["run_deadline_ms"] and recovery["prior_attempts"]["proxy-start"]==7 and recovery["prior_attempts"]["correction"]==17 and recovery["prior_attempts"]["build"]==13 and 39<=recovery["prior_attempts"]["offline-start"]<=41 and recovery["prior_attempts"]["offline-thread"]>=38 and recovery["prior_attempts"]["offline-turn"]>=28,"MCP recovery caps")
                elif anchor["version"] == 13:
                    evidence=json.loads(control_read(ref["path"]),object_pairs_hook=reject_duplicate_keys)
                    require(predecessor["anchor_sha256"] == 'cf578c094c7f916c1944b2e414dccd9fdc1801da6f7b46cf5d43e92bb702c45c' and predecessor["journal_sha256"] == '565074e5ec6a75072dea316dcd09097b85531741fbba2cd665f8e5d72ab23f38' and stop_seq==18 and stop["sha256"]=='edb7fe626c04fab1064052214290a7f4ea15a9441f4098f5c7f67aecf7b3a674' and len(parent_rows)==20 and parent_rows[19]["event"]["kind"]=="process-ended" and parent_rows[19]["event"]["subject"].get("process_group_absent") is True,"exact notification stop recovery")
                    expected={'stop_seq': 18, 'stop_sha256': 'edb7fe626c04fab1064052214290a7f4ea15a9441f4098f5c7f67aecf7b3a674', 'epoch_anchor_sha256': 'cf578c094c7f916c1944b2e414dccd9fdc1801da6f7b46cf5d43e92bb702c45c', 'epoch_journal_sha256': '565074e5ec6a75072dea316dcd09097b85531741fbba2cd665f8e5d72ab23f38', 'runtime_start': 'clock-05', 'control_reservations_cumulative': 4, 'auth_admissions_observed_cumulative': 4, 'credential_storage_read_call_count': None, 'fd_event_counts': {'controller-closed': 1, 'controller-ready': 1, 'fd-issued': 1, 'fd-released': 1, 'fd-reserved': 1, 'proxy-launched': 1, 'runtime-bound': 1}, 'model_threads': 0, 'model_turns': 0, 'generation_sends': 0, 'leases': 0, 'pending_apply': False, 'all_processes_absent': True, 'protected_auth_metadata_equal': True, 'auth_boundary_violation_count': 0}
                    require(canonical({k:evidence.get(k) for k in expected})==canonical(expected) and all(k in evidence for k in expected),"notification recovery observed effects")
                    require(authorization["network"]=={"host":"chatgpt.com","port":443,"peer":"104.18.32.47"} and authorization["approval_plan_sha256"]=='fe548facf78d351aa48d636ca1da803b398cc5d6300826cc837b66af42b092f0',"notification recovery approval")
                    require(anchor["approval_wall_ms"]==parent["approval_wall_ms"] and anchor["run_deadline_ms"]==parent["run_deadline_ms"] and recovery["prior_attempts"]["proxy-start"]==6 and recovery["prior_attempts"]["correction"]==16 and recovery["prior_attempts"]["build"]==12 and 37<=recovery["prior_attempts"]["offline-start"]<=39 and recovery["prior_attempts"]["offline-thread"]>=36 and recovery["prior_attempts"]["offline-turn"]>=26,"notification recovery caps")
                elif anchor["version"] == 12:
                    evidence=json.loads(control_read(ref["path"]),object_pairs_hook=reject_duplicate_keys)
                    require(predecessor["anchor_sha256"] == 'cf578c094c7f916c1944b2e414dccd9fdc1801da6f7b46cf5d43e92bb702c45c' and predecessor["journal_sha256"] == '565074e5ec6a75072dea316dcd09097b85531741fbba2cd665f8e5d72ab23f38' and stop_seq==18 and stop["sha256"]=='edb7fe626c04fab1064052214290a7f4ea15a9441f4098f5c7f67aecf7b3a674' and len(parent_rows)==20 and parent_rows[19]["event"]["kind"]=="process-ended" and parent_rows[19]["event"]["subject"].get("process_group_absent") is True,"exact notification stop recovery")
                    expected={'stop_seq': 18, 'stop_sha256': 'edb7fe626c04fab1064052214290a7f4ea15a9441f4098f5c7f67aecf7b3a674', 'epoch_anchor_sha256': 'cf578c094c7f916c1944b2e414dccd9fdc1801da6f7b46cf5d43e92bb702c45c', 'epoch_journal_sha256': '565074e5ec6a75072dea316dcd09097b85531741fbba2cd665f8e5d72ab23f38', 'runtime_start': 'clock-05', 'control_reservations_cumulative': 4, 'auth_admissions_observed_cumulative': 4, 'credential_storage_read_call_count': None, 'fd_event_counts': {'controller-closed': 1, 'controller-ready': 1, 'fd-issued': 1, 'fd-released': 1, 'fd-reserved': 1, 'proxy-launched': 1, 'runtime-bound': 1}, 'model_threads': 0, 'model_turns': 0, 'generation_sends': 0, 'leases': 0, 'pending_apply': False, 'all_processes_absent': True, 'protected_auth_metadata_equal': True, 'auth_boundary_violation_count': 0}
                    require(canonical({k:evidence.get(k) for k in expected})==canonical(expected) and all(k in evidence for k in expected),"notification recovery observed effects")
                    require(authorization["network"]=={"host":"chatgpt.com","port":443,"peer":"104.18.32.47"} and authorization["approval_plan_sha256"]=='13393834ad6b28121010e1ee4ca7d4c9419c944cf02462e5249348832048f62f',"notification recovery approval")
                    require(anchor["approval_wall_ms"]==parent["approval_wall_ms"] and anchor["run_deadline_ms"]==parent["run_deadline_ms"] and recovery["prior_attempts"]["proxy-start"]==6 and recovery["prior_attempts"]["correction"]==13 and recovery["prior_attempts"]["build"] in (10,11) and recovery["prior_attempts"]["offline-start"]>=32 and recovery["prior_attempts"]["offline-thread"]>=31 and recovery["prior_attempts"]["offline-turn"]>=23,"notification recovery caps")
                elif anchor["version"] == 11:
                    evidence=json.loads(control_read(ref["path"]),object_pairs_hook=reject_duplicate_keys)
                    require(predecessor["anchor_sha256"] == 'cf578c094c7f916c1944b2e414dccd9fdc1801da6f7b46cf5d43e92bb702c45c' and predecessor["journal_sha256"] == '565074e5ec6a75072dea316dcd09097b85531741fbba2cd665f8e5d72ab23f38' and stop_seq==18 and stop["sha256"]=='edb7fe626c04fab1064052214290a7f4ea15a9441f4098f5c7f67aecf7b3a674' and len(parent_rows)==20 and parent_rows[19]["event"]["kind"]=="process-ended" and parent_rows[19]["event"]["subject"].get("process_group_absent") is True,"exact notification stop recovery")
                    expected={'stop_seq': 18, 'stop_sha256': 'edb7fe626c04fab1064052214290a7f4ea15a9441f4098f5c7f67aecf7b3a674', 'epoch_anchor_sha256': 'cf578c094c7f916c1944b2e414dccd9fdc1801da6f7b46cf5d43e92bb702c45c', 'epoch_journal_sha256': '565074e5ec6a75072dea316dcd09097b85531741fbba2cd665f8e5d72ab23f38', 'runtime_start': 'clock-05', 'control_reservations_cumulative': 4, 'auth_admissions_observed_cumulative': 4, 'credential_storage_read_call_count': None, 'fd_event_counts': {'controller-closed': 1, 'controller-ready': 1, 'fd-issued': 1, 'fd-released': 1, 'fd-reserved': 1, 'proxy-launched': 1, 'runtime-bound': 1}, 'model_threads': 0, 'model_turns': 0, 'generation_sends': 0, 'leases': 0, 'pending_apply': False, 'all_processes_absent': True, 'protected_auth_metadata_equal': True, 'auth_boundary_violation_count': 0}
                    require(canonical({k:evidence.get(k) for k in expected})==canonical(expected) and all(k in evidence for k in expected),"notification recovery observed effects")
                    require(authorization["network"]=={"host":"chatgpt.com","port":443,"peer":"104.18.32.47"} and authorization["approval_plan_sha256"]=='611df46907653008766a228c43772f51d88c96cc0079bd530bf20cb0bbe6d089',"notification recovery approval")
                    require(anchor["approval_wall_ms"]==parent["approval_wall_ms"] and anchor["run_deadline_ms"]==parent["run_deadline_ms"] and recovery["prior_attempts"]["proxy-start"]==6 and recovery["prior_attempts"]["correction"]==12 and recovery["prior_attempts"]["build"] in (9,10) and recovery["prior_attempts"]["offline-start"]>=31 and recovery["prior_attempts"]["offline-thread"]>=31 and recovery["prior_attempts"]["offline-turn"]>=23,"notification recovery caps")
                elif anchor["version"] == 10:
                    evidence=json.loads(control_read(ref["path"]),object_pairs_hook=reject_duplicate_keys)
                    require(predecessor["anchor_sha256"] == 'cf578c094c7f916c1944b2e414dccd9fdc1801da6f7b46cf5d43e92bb702c45c' and predecessor["journal_sha256"] == '565074e5ec6a75072dea316dcd09097b85531741fbba2cd665f8e5d72ab23f38' and stop_seq==18 and stop["sha256"]=='edb7fe626c04fab1064052214290a7f4ea15a9441f4098f5c7f67aecf7b3a674' and len(parent_rows)==20 and parent_rows[19]["event"]["kind"]=="process-ended" and parent_rows[19]["event"]["subject"].get("process_group_absent") is True,"exact notification stop recovery")
                    expected={'stop_seq': 18, 'stop_sha256': 'edb7fe626c04fab1064052214290a7f4ea15a9441f4098f5c7f67aecf7b3a674', 'epoch_anchor_sha256': 'cf578c094c7f916c1944b2e414dccd9fdc1801da6f7b46cf5d43e92bb702c45c', 'epoch_journal_sha256': '565074e5ec6a75072dea316dcd09097b85531741fbba2cd665f8e5d72ab23f38', 'runtime_start': 'clock-05', 'control_reservations_cumulative': 4, 'auth_admissions_observed_cumulative': 4, 'credential_storage_read_call_count': None, 'fd_event_counts': {'controller-closed': 1, 'controller-ready': 1, 'fd-issued': 1, 'fd-released': 1, 'fd-reserved': 1, 'proxy-launched': 1, 'runtime-bound': 1}, 'model_threads': 0, 'model_turns': 0, 'generation_sends': 0, 'leases': 0, 'pending_apply': False, 'all_processes_absent': True, 'protected_auth_metadata_equal': True, 'auth_boundary_violation_count': 0}
                    require(canonical({k:evidence.get(k) for k in expected})==canonical(expected) and all(k in evidence for k in expected),"notification recovery observed effects")
                    require(authorization["network"]=={"host":"chatgpt.com","port":443,"peer":"104.18.32.47"} and authorization["approval_plan_sha256"]=='36a0d6466a3b62e880c5e47a104775f9a04f9159cee70f483add44c85263216a',"notification recovery approval")
                    require(anchor["approval_wall_ms"]==parent["approval_wall_ms"] and anchor["run_deadline_ms"]==parent["run_deadline_ms"] and recovery["prior_attempts"]["proxy-start"]==6 and recovery["prior_attempts"]["correction"]==11 and recovery["prior_attempts"]["build"] in (8,9),"notification recovery caps")
                elif anchor["version"] == 9:
                    evidence=json.loads(control_read(ref["path"]),object_pairs_hook=reject_duplicate_keys)
                    require(predecessor["anchor_sha256"] == 'cf578c094c7f916c1944b2e414dccd9fdc1801da6f7b46cf5d43e92bb702c45c' and predecessor["journal_sha256"] == '565074e5ec6a75072dea316dcd09097b85531741fbba2cd665f8e5d72ab23f38' and stop_seq==18 and stop["sha256"]=='edb7fe626c04fab1064052214290a7f4ea15a9441f4098f5c7f67aecf7b3a674' and len(parent_rows)==20 and parent_rows[19]["event"]["kind"]=="process-ended" and parent_rows[19]["event"]["subject"].get("process_group_absent") is True,"exact notification stop recovery")
                    expected={'stop_seq': 18, 'stop_sha256': 'edb7fe626c04fab1064052214290a7f4ea15a9441f4098f5c7f67aecf7b3a674', 'epoch_anchor_sha256': 'cf578c094c7f916c1944b2e414dccd9fdc1801da6f7b46cf5d43e92bb702c45c', 'epoch_journal_sha256': '565074e5ec6a75072dea316dcd09097b85531741fbba2cd665f8e5d72ab23f38', 'runtime_start': 'clock-05', 'control_reservations_cumulative': 4, 'auth_admissions_observed_cumulative': 4, 'credential_storage_read_call_count': None, 'fd_event_counts': {'controller-closed': 1, 'controller-ready': 1, 'fd-issued': 1, 'fd-released': 1, 'fd-reserved': 1, 'proxy-launched': 1, 'runtime-bound': 1}, 'model_threads': 0, 'model_turns': 0, 'generation_sends': 0, 'leases': 0, 'pending_apply': False, 'all_processes_absent': True, 'protected_auth_metadata_equal': True, 'auth_boundary_violation_count': 0}
                    require(canonical({k:evidence.get(k) for k in expected})==canonical(expected) and all(k in evidence for k in expected),"notification recovery observed effects")
                    require(authorization["network"]=={"host":"chatgpt.com","port":443,"peer":"104.18.32.47"} and authorization["approval_plan_sha256"]=='a606aabd45b2c921907323e076822e50cf3bc69cca7e5b6c62cd2b16087a00be',"notification recovery approval")
                    require(anchor["approval_wall_ms"]==parent["approval_wall_ms"] and anchor["run_deadline_ms"]==parent["run_deadline_ms"] and recovery["prior_attempts"]["proxy-start"]==6 and recovery["prior_attempts"]["correction"]==10 and recovery["prior_attempts"]["build"] in (8,9),"notification recovery caps")
                elif anchor["version"] == 8:
                    evidence=json.loads(control_read(ref["path"]),object_pairs_hook=reject_duplicate_keys)
                    require(predecessor["anchor_sha256"] == "5bfd8e52040d6d814c87803c0753a885be8a554ed3c8f23a2d7ab3ae5ba4e8cc" and predecessor["journal_sha256"] == "5318af9950bcaac5b7cbca1b9777230077fe38e0a6c7f8d970489646d8a10552"
                            and stop_seq == 15 and stop["sha256"] == "cf8addee5ff2b0de7d994802686b6f921368bef2bdbb04c0335cd151fb50f358" and len(parent_rows)==17
                            and parent_rows[14]["event"]["kind"]=="control" and parent_rows[14]["event"]["subject"]=={"endpoint":"models"}
                            and parent_rows[16]["event"]["kind"]=="process-ended" and parent_rows[16]["event"]["subject"].get("process_group_absent") is True,"exact model stop recovery")
                    expected={"stop_seq":15,"stop_sha256":stop["sha256"],"epoch_anchor_sha256":predecessor["anchor_sha256"],"epoch_journal_sha256":predecessor["journal_sha256"],"runtime_start":"clock-04","control_reservations_cumulative":3,"auth_admissions_observed_cumulative":3,"credential_storage_read_call_count":None,"fd_issued_this_run":1,"fd_reserved_this_run":1,"fd_released_this_run":1,"model_threads":0,"model_turns":0,"generation_sends":0,"leases":0,"pending_apply":False,"all_processes_absent":True,"protected_auth_metadata_equal":True,"auth_boundary_violation_count":0}
                    require(canonical({k:evidence.get(k) for k in expected})==canonical(expected) and all(k in evidence for k in expected),"Lite recovery observed effects")
                    require(authorization["network"]=={"host":"chatgpt.com","port":443,"peer":"104.18.32.47"} and authorization["approval_plan_sha256"]=="b2d44fdfc895bf105b78000a3433e2ba6faae158e34b3d82a6166772a02aaa66","Lite recovery approval")
                    require(anchor["approval_wall_ms"]==parent["approval_wall_ms"] and anchor["run_deadline_ms"]==parent["run_deadline_ms"] and recovery["prior_attempts"]["proxy-start"]==5 and recovery["prior_attempts"]["correction"]==9 and recovery["prior_attempts"]["build"] in (7,8),"Lite recovery caps")
                elif anchor["version"] == 7:
                    evidence=json.loads(control_read(ref["path"]),object_pairs_hook=reject_duplicate_keys)
                    require(predecessor["anchor_sha256"] == "eecdabcaa0afc9f35b2fd3e92abd37216e6334f0954c33ac5520b0942c19ce9c" and predecessor["journal_sha256"] == "ca1baea61152bf0186dbe7cf1e34627676196c11c5fe75d0d05b08567d414db9"
                            and stop_seq == 15 and stop["sha256"] == "0c9b870472b79c402f7fd80687f8604e4f88b339b04c3186e64551bd1746ec63" and len(parent_rows)==17
                            and parent_rows[14]["event"]["kind"]=="control" and parent_rows[14]["event"]["subject"]=={"endpoint":"models"}
                            and parent_rows[16]["event"]["kind"]=="process-ended" and parent_rows[16]["event"]["subject"].get("process_group_absent") is True,"exact preface stop recovery")
                    expected={"stop_seq":15,"stop_sha256":stop["sha256"],"epoch_anchor_sha256":predecessor["anchor_sha256"],"epoch_journal_sha256":predecessor["journal_sha256"],"runtime_start":"clock-03","control_reservations_cumulative":2,"auth_admissions_observed_cumulative":2,"credential_storage_read_call_count":None,"fd_issued_this_run":0,"fd_reservations_this_run":0,"model_threads":0,"model_turns":0,"generation_sends":0,"leases":0,"pending_apply":False,"all_processes_absent":True,"protected_auth_metadata_equal":True,"auth_boundary_violation_count":0}
                    require(canonical({k:evidence.get(k) for k in expected})==canonical(expected) and all(k in evidence for k in expected),"preface recovery observed effects")
                    require(authorization["network"]=={"host":"chatgpt.com","port":443,"peer":"104.18.32.47"} and authorization["approval_plan_sha256"]=="6f946235d6999fd1d8275b5027f1734d5c038ee62896b1e3e7cd728275e9c420","preface recovery approval")
                    require(anchor["approval_wall_ms"]==parent["approval_wall_ms"] and anchor["run_deadline_ms"]==parent["run_deadline_ms"] and recovery["prior_attempts"]["proxy-start"]==4 and recovery["prior_attempts"]["correction"]==8 and recovery["prior_attempts"]["build"] in (6,7,8,9,10,11,12,13,14),"preface recovery caps")
                elif anchor["version"] == 6:
                    evidence=json.loads(control_read(ref["path"]),object_pairs_hook=reject_duplicate_keys)
                    require(predecessor["anchor_sha256"] == "3bc746f979737e0ec05bc05f55b9ea17710ab3d494dd3c3c69833e48e0810139" and predecessor["journal_sha256"] == "8f51ecb50574a29fa207f00976725f90c1c08853ee64bb5fb3ba867e87ddc7c8"
                            and stop_seq == 15 and stop["sha256"] == "c5f75557b52f611444289de50425d09a7f0da081cb90e54883115b8958214467" and len(parent_rows) == 17
                            and parent_rows[14]["event"]["kind"] == "control" and parent_rows[14]["event"]["subject"] == {"endpoint":"models"}
                            and parent_rows[16]["event"]["kind"] == "process-ended" and parent_rows[16]["event"]["subject"].get("process_group_absent") is True,
                            "exact catalog stop recovery")
                    require(all(type(evidence.get(k)) is int for k in ("stop_seq","native_auth_runtime_admissions_observed","control_reservations","port")) and evidence.get("stop_seq") == 15 and evidence.get("stop_sha256") == stop["sha256"]
                            and evidence.get("epoch_anchor_sha256") == predecessor["anchor_sha256"] and evidence.get("epoch_journal_sha256") == predecessor["journal_sha256"]
                            and evidence.get("native_auth_runtime_admissions_observed") == 1 and "credential_storage_read_call_count" in evidence and evidence["credential_storage_read_call_count"] is None
                            and evidence.get("control_reservations") == 1 and evidence.get("control_endpoint") == "models"
                            and evidence.get("frozen_peer") == "172.64.155.209" and evidence.get("port") == 443
                            and all(type(evidence.get(k)) is int and evidence[k] == 0 for k in ("fd_issued","model_threads","model_turns","generation_sends","leases"))
                            and evidence.get("pending_apply") is False and all(evidence.get(k) is True for k in ("runtime_process_group_absent","proxy_process_group_absent")),
                            "catalog recovery observed effects")
                    require(authorization["network"] == {'host': 'chatgpt.com', 'port': 443, 'peer': '104.18.32.47'} and authorization["approval_plan_sha256"] == "816c0d647567d2c090d327b608a55636964b7e63ad5fa363f0d99ab11d28a249", "network recovery approval")
                    diagnostic_ref=authorization["diagnostic_evidence"]
                    require(set(diagnostic_ref)=={"path","sha256"} and digest(control_read(diagnostic_ref["path"]))==diagnostic_ref["sha256"], "network diagnostic drift")
                    diagnostic=json.loads(control_read(diagnostic_ref["path"]),object_pairs_hook=reject_duplicate_keys)
                    require(diagnostic.get("auth_read") is False and type(diagnostic.get("tls_http_bytes_sent")) is int and diagnostic.get("tls_http_bytes_sent")==0 and diagnostic.get("guarded_files_unchanged") is True
                            and len(diagnostic.get("attempts",[]))==2 and diagnostic["attempts"][0].get("peer")=="172.64.155.209" and diagnostic["attempts"][0].get("status")=="failed"
                            and diagnostic["attempts"][1].get("peer")=="104.18.32.47" and diagnostic["attempts"][1].get("status")=="connected" and diagnostic["attempts"][1].get("peer_verified") is True,
                            "network diagnostic evidence")
                    require(anchor["approval_wall_ms"]==parent["approval_wall_ms"] and anchor["run_deadline_ms"]==parent["run_deadline_ms"]
                            and recovery["prior_attempts"]["proxy-start"]==3 and recovery["prior_attempts"]["correction"]==7
                            and recovery["prior_attempts"]["build"] in (5,6), "catalog recovery caps")
                elif anchor["version"] == 5:
                    evidence=json.loads(control_read(ref["path"]),object_pairs_hook=reject_duplicate_keys)
                    require(stop_seq == 18 and len(parent_rows) == 19 and parent_rows[-2]["event"]["kind"] == "proxy-start"
                            and parent_rows[-2]["event"]["subject"] == {"slot":"s4","start_id":"s4-02"}
                            and all(row["event"]["kind"] in {"genesis","offline-start","offline-thread","offline-turn","proxy-start","stop"} for row in parent_rows), "prelaunch-only recovery shape")
                    require(evidence.get("failure")==expected_reason and evidence.get("stop_seq")==stop_seq
                            and evidence.get("stop_sha256")==stop["sha256"] and evidence.get("epoch_anchor_sha256")==predecessor["anchor_sha256"]
                            and evidence.get("epoch_journal_sha256")==predecessor["journal_sha256"]
                            and all(type(evidence.get(k)) is int and evidence[k]==0 for k in ("runtime_launch_added","auth_added","provider_send_added","leases"))
                            and evidence.get("pending_apply") is False and evidence.get("proxy_process_group_absent") is True
                            and evidence.get("controller_absent") is True, "prelaunch recovery evidence")
                    require(anchor["approval_wall_ms"]==parent["approval_wall_ms"] and anchor["run_deadline_ms"]==parent["run_deadline_ms"]
                            and recovery["prior_attempts"]["proxy-start"]==2 and recovery["prior_attempts"]["correction"]==6, "prelaunch recovery caps")
                else:
                    require(all(row["event"]["kind"] == "process-ended" and row["event"]["subject"].get("process_group_absent") is True
                                for row in parent_rows[stop_seq + 1:]) and len(parent_rows) > stop_seq + 1, "resume process tail")
            require(anchor["origin_wall_ms"] >= parent_rows[-1]["event"]["at_ms"], "epoch wall rollback")
            anchor, anchor_sha, rows, directory = parent, predecessor["anchor_sha256"], parent_rows, parent_dir
        return list(reversed(segments))

    @classmethod
    def inspect_for_clock_recovery(cls, directory, anchor_sha256):
        """Read-only structural inspection; never used by normal runtime admission."""
        value = object.__new__(cls)
        value.directory = Path(directory)
        value.path = value.directory / "journal.jsonl"
        value.lock_path = value.directory / "append.lock"
        raw = control_read(value.directory / "anchor.json", 65536)
        require(digest(raw) == anchor_sha256, "budget anchor drift")
        value.anchor, value.anchor_sha256 = json.loads(raw, object_pairs_hook=reject_duplicate_keys), anchor_sha256
        value._anchor_fields(value.anchor)
        rows = value._rows(control_read(value.path))
        # Only this explicit forensic entry uses wall time instead of the live clock.
        return value, value._validate(rows, recovery_inspection_ms=time.time_ns() // 1_000_000)

    @classmethod
    def recover_clock(cls, packet_path):
        """Apply one exact controller packet; no counter or pending reset."""
        packet = json.loads(control_read(packet_path), object_pairs_hook=reject_duplicate_keys)
        require(set(packet) == {"version", "destination", "anchor"} and type(packet["version"]) is int and packet["version"] == 1, "clock recovery packet")
        anchor = packet["anchor"]
        cls._anchor_fields(anchor)
        require(anchor["version"] in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57), "clock recovery version")
        parent = Path(anchor["recovery"]["predecessor"]["directory"])
        lock = ControllerLock(parent / "controller.lock")
        append = None
        try:
            append = checked_open(parent / "append.lock", os.O_RDWR)
            bounded_flock(append, fcntl.LOCK_EX, anchor["total_deadline_ms"])
            probe = object.__new__(cls)
            probe.directory = Path(packet["destination"])
            require(probe.directory.is_absolute() and probe.directory.parent.resolve(strict=True) == probe.directory.parent and not os.path.lexists(probe.directory), "clock recovery destination consumed or aliased")
            probe.anchor, probe.anchor_sha256 = anchor, digest(canonical(anchor))
            probe._clock()
            event = {"seq": 0, "prev": "", **{k: anchor[k] for k in ("approval", "work", "candidate")}, "phase": "controller", "start": "controller", "kind": "genesis", "subject": {"anchor_sha256": probe.anchor_sha256}, "at_ms": anchor["origin_wall_ms"]}
            probe._validate([{"event": event, "sha256": digest(wire_bytes(event))}])
            cp = json.loads(control_read(anchor["recovery"]["checkpoint"]["path"]), object_pairs_hook=reject_duplicate_keys)
            for pid in cp["process_ids"]:
                try:
                    os.kill(pid, 0)
                except ProcessLookupError:
                    continue
                raise HostRefusal("predecessor process may still be alive")
            return cls.create(probe.directory, anchor)
        except BlockingIOError:
            raise HostRefusal("concurrent predecessor writer")
        finally:
            if append is not None:
                os.close(append)
            lock.close()

    @classmethod
    def create(cls, directory, anchor):
        directory = Path(directory)
        if anchor.get("version") in (58, 59):
            execution_os(require, purpose="codex-v58")
            execution_policy(anchor).contract(anchor, cls.fresh_bound)
            require(str(directory) == anchor["run_directory"], "v58-directory-binding")
        directory.mkdir(mode=0o700, exist_ok=False)
        durable_private(directory / "anchor.json", anchor)
        for name in ("append.lock", "controller.lock"):
            durable_private(directory / name, {"version": 1})
        anchor_sha = digest((directory / "anchor.json").read_bytes())
        event = {"seq": 0, "prev": "", **{k: anchor[k] for k in ("approval", "work", "candidate")},
                 "phase": "controller", "start": "controller", "kind": "genesis",
                 "subject": {"anchor_sha256": anchor_sha}, "at_ms": anchor["origin_wall_ms"]}
        durable_private(directory / "journal.jsonl", {"event": event, "sha256": digest(wire_bytes(event))})
        return cls(directory, anchor_sha)

    @staticmethod
    def fresh_bound(ref):
        fresh_u2.exact(ref, ('path', 'sha256'), 'v58-bound-reference')
        raw = control_read(ref['path'], 1_048_576)
        require(digest(raw) == ref['sha256'], 'v58-bound-drift')
        value = json.loads(raw, object_pairs_hook=reject_duplicate_keys)
        require(canonical(value) == raw, 'v58-bound-canonical')
        return value

    def _clock(self):
        now = time.time_ns() // 1_000_000
        if self.anchor['version'] in (58, 59):
            elapsed = (self.os.continuous_ns() - self.anchor['origin_monotonic_ns']) // 1_000_000
            require(elapsed >= 0 and abs(now - self.anchor['origin_wall_ms'] - elapsed) <= 2000, 'v58-clock-drift')
            return now
        elapsed = ((continuous_ns() if self.anchor["version"] >= 3 else time.monotonic_ns()) - self.anchor["origin_monotonic_ns"]) // 1_000_000
        require(elapsed >= 0 and abs(now - self.anchor["origin_wall_ms"] - elapsed) <= 2000, "activity clock drift")
        return now

    def _validate(self, rows, recovery_inspection_ms=None):
        now = self._clock() if recovery_inspection_ms is None else recovery_inspection_ms
        if self.anchor["version"] in (58, 59): return execution_policy(self.anchor).budget_state(self, rows, now)
        if self.anchor["version"] in (31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57):return u2_budget_state(self,rows,now)
        if self.anchor["version"] in (24,25,26,27,28,29,30):return clock_budget_state(self,rows,now)
        if self.anchor["version"] in (21,22,23):return diagnostic_budget_state(self,rows,now)
        require(rows and len(rows) < 20_000, "missing or excessive journal")
        events, prev, last_time = [], "", 0
        starts, thread_requests, thread_ids, plans = {}, set(), {}, {}
        turn_ids, controls = {}, set()
        counts, phase_counts, start_counts = {}, {}, {}
        generations, dispatches, host_dispatches, applies = {}, {}, set(), set()
        paused_at, pause_seq, excluded_ms, stopped = None, None, 0, False
        current_rows = rows
        segments = self._lineage(rows)
        require(sum(len(segment[2]) for segment in segments) < 20_000, "excessive inherited journal")
        previous_anchor = None
        for anchor, anchor_sha, rows in segments:
            require(rows and len(rows) < 20_000, "missing or excessive journal")
            if previous_anchor is not None:
                require(paused_at is not None or stopped, "predecessor is not quiescent")
                previous_active = (paused_at if paused_at is not None else last_time) - excluded_ms
                previous_cap = previous_anchor.get("recovery", {}).get("total_cap_ms", 57_600_000)
                previous_used = previous_cap - (previous_anchor["total_deadline_ms"] - previous_active)
                require(0 <= previous_used <= anchor["recovery"]["carry_active_ms"], "recovery lost consumed time")
                # The new genesis explicitly ends the predecessor's owner pause.
                # The carried usage, not this gap, supplies historical accounting.
                if anchor["version"] >= 3:
                    if anchor["version"] == 20:
                        require(stopped and counts.get("proxy-start")==12 and starts=={f"clock-{n:02}":"clock" for n in range(1,11)} and counts.get("runtime-entered")==10 and counts.get("control")==13 and counts.get("thread")==4 and counts.get("thread-bound")==3 and all(counts.get(k,0)==0 for k in ("turn","generation","dispatch","host-dispatch","authority-apply","recovery-apply","seal")),"clock10 prepare recovery effects drift")
                    elif anchor["version"] == 19:
                        require(stopped and counts.get("proxy-start")==11 and starts=={f"clock-{n:02}":"clock" for n in range(1,10)} and counts.get("runtime-entered")==9 and counts.get("control")==11 and counts.get("thread")==3 and counts.get("thread-bound")==2 and all(counts.get(k,0)==0 for k in ("turn","generation","dispatch","host-dispatch","authority-apply","recovery-apply","seal")),"expiry prelaunch recovery effects drift")
                    elif anchor["version"] == 18:
                        require(stopped and starts=={f"clock-{n:02}":"clock" for n in range(1,10)} and counts.get("runtime-entered")==9 and counts.get("control")==11 and counts.get("thread")==3 and counts.get("thread-bound")==2 and all(counts.get(k,0)==0 for k in ("turn","generation","dispatch","host-dispatch","authority-apply","recovery-apply","seal")),"clock09 document policy recovery effects drift")
                    elif anchor["version"] == 17:
                        require(stopped and starts=={f"clock-{n:02}":"clock" for n in range(1,9)} and counts.get("runtime-entered")==8 and counts.get("control")==9 and counts.get("thread")==2 and counts.get("thread-bound")==1 and all(counts.get(k,0)==0 for k in ("turn","generation","dispatch","host-dispatch","authority-apply","recovery-apply","seal")),"clock08 preface recovery effects drift")
                    elif anchor["version"] == 16:
                        require(stopped and starts=={f"clock-{n:02}":"clock" for n in range(1,8)} and counts.get("runtime-entered")==7 and counts.get("control")==8 and counts.get("thread")==2 and counts.get("thread-bound")==1 and all(counts.get(k,0)==0 for k in ("turn","generation","dispatch","host-dispatch","authority-apply","recovery-apply","seal")),"late-notice recovery effects drift")
                    elif anchor["version"] in (14,15,16,17,18,19,20):
                        require(stopped and starts=={f"clock-{n:02}":"clock" for n in range(1,7)} and counts.get("runtime-entered")==6 and counts.get("control")==6 and counts.get("thread")==1 and all(counts.get(k,0)==0 for k in ("thread-bound","turn","generation","dispatch","host-dispatch","authority-apply","recovery-apply","seal")),"MCP recovery effects drift")
                    elif anchor["version"] in (9,10,11,12,13):
                        require(stopped and starts=={"clock-01":"clock","clock-02":"clock","clock-03":"clock","clock-04":"clock","clock-05":"clock"} and counts.get("runtime-entered")==5 and counts.get("control")==4 and all(counts.get(k,0)==0 for k in ("thread","thread-bound","turn","generation","dispatch","host-dispatch","authority-apply","recovery-apply","seal")),"notification recovery effects drift")
                    elif anchor["version"] == 8:
                        require(stopped and starts=={"clock-01":"clock","clock-02":"clock","clock-03":"clock","clock-04":"clock"} and counts.get("runtime-entered")==4 and counts.get("control")==3 and all(counts.get(k,0)==0 for k in ("thread","thread-bound","turn","generation","dispatch","host-dispatch","authority-apply","recovery-apply","seal")),"Lite recovery effects drift")
                    elif anchor["version"] == 7:
                        require(stopped and starts=={"clock-01":"clock","clock-02":"clock","clock-03":"clock"} and counts.get("runtime-entered")==3 and counts.get("control")==2 and all(counts.get(k,0)==0 for k in ("thread","thread-bound","turn","generation","dispatch","host-dispatch","authority-apply","recovery-apply","seal")),"preface recovery effects drift")
                    elif anchor["version"] == 6:
                        require(stopped and starts == {"clock-01":"clock","clock-02":"clock"} and counts.get("runtime-entered")==2 and counts.get("control")==1
                                and all(counts.get(kind,0)==0 for kind in ("thread","thread-bound","turn","generation","dispatch","host-dispatch","authority-apply","recovery-apply","seal")), "catalog recovery effects drift")
                    else:
                        require(stopped and starts == {"clock-01": "clock"} and counts.get("runtime-entered") == 1
                                and all(counts.get(kind, 0) == 0 for kind in ("control", "thread", "thread-bound", "turn", "generation", "dispatch", "host-dispatch", "authority-apply", "recovery-apply", "seal")), "pre-auth effects not zero")
                    stopped = False  # Only the exact bound Owner decision opens this epoch.
                if anchor["version"] >= 4:
                    for kind, carried in anchor["recovery"]["prior_attempts"].items():
                        require(carried >= counts.get(kind, 0), "attempt carry refund")
                        if kind == "proxy-start": require(carried == counts.get(kind, 0), "unrecorded proxy attempt")
                        counts[kind] = carried
                    counts["correction-source"] = counts["correction"]
                    counts["correction-content"] = 0
                paused_at, pause_seq, excluded_ms = None, None, 0
            prev = ""
            previous_anchor = anchor
            for number, row in enumerate(rows):
                require(isinstance(row, dict) and set(row) == {"event", "sha256"}, "journal row fields")
                event = row["event"]
                require(isinstance(event, dict) and set(event) == {"seq", "prev", "approval", "work", "candidate", "phase", "start", "kind", "subject", "at_ms"}, "journal event fields")
                require(type(event["seq"]) is int and event["seq"] == number and event["prev"] == prev and row["sha256"] == digest(wire_bytes(event)), "journal chain drift")
                require(all(event[k] == anchor[k] for k in ("approval", "work", "candidate")), "journal binding drift")
                at = event["at_ms"]
                require(type(at) is int and last_time <= at <= now, "journal time drift")
                kind, phase, start, subject = (event[k] for k in ("kind", "phase", "start", "subject"))
                require(kind in JOURNAL_KINDS and isinstance(subject, dict), "unknown journal event")
                if number == 0:
                    require(kind == "genesis" and subject == {"anchor_sha256": anchor_sha}, "journal genesis drift")
                else:
                    require(kind != "genesis", "repeated genesis")
                if stopped and number != 0:
                    require(kind in ("process-ended", "checkpoint"), "effect after stop")
                if kind == "pause":
                    require(paused_at is None and subject.get("reason") == "owner-only", "invalid pause")
                    paused_at, pause_seq = at, number
                elif kind == "resume":
                    require(paused_at is not None and subject.get("pause_seq") == pause_seq, "unpaired resume")
                    excluded_ms += at - paused_at
                    paused_at = None
                elif paused_at is not None:
                    require(kind in ("checkpoint", "process-ended", "stop"), "activity during owner-only pause")
                if kind == "stop":
                    stopped = True
                counts[kind] = counts.get(kind, 0) + 1
                phase_counts[phase, kind] = phase_counts.get((phase, kind), 0) + 1
                start_counts[start, kind] = start_counts.get((start, kind), 0) + 1
                if kind == "start":
                    if anchor["version"] == 20: require(phase == "clock" and start == "clock-11", "MCP41 clock-only start")
                    require(phase in PHASE_CAPS and start not in starts and (start in (phase + "-01", phase + "-02") or (anchor["version"] in (6,7,8,9,10,11,12,13,14,15,16,17,18,19,20) and phase == "clock" and start == ("clock-11" if anchor["version"]==20 else "clock-10" if anchor["version"] in (18,19) else "clock-09" if anchor["version"]==17 else "clock-08" if anchor["version"]==16 else "clock-07" if anchor["version"] in (14,15,16,17,18,19,20) else "clock-06" if anchor["version"] in (9,10,11,12,13,14,15,16,17,18,19,20) else "clock-05" if anchor["version"]==8 else "clock-04" if anchor["version"]==7 else "clock-03"))), "unallocated start")
                    require(counts[kind] <= (13 if anchor["version"]==20 else 12 if anchor["version"] in (18,19) else 11 if anchor["version"] in (14,15,16,17,18,19,20) else 10 if anchor["version"] in (9,10,11,12,13,14,15,16,17,18,19,20) else 9 if anchor["version"]==8 else 8 if anchor["version"]==7 else 7 if anchor["version"] == 6 else 6) and phase_counts[phase, kind] <= ((11 if anchor["version"]==20 else 10 if anchor["version"] in (18,19) else 9 if anchor["version"]==17 else 8 if anchor["version"]==16 else 7 if anchor["version"] in (14,15,16,17,18,19,20) else 6 if anchor["version"] in (9,10,11,12,13,14,15,16,17,18,19,20) else 5 if anchor["version"]==8 else 4 if anchor["version"]==7 else 3) if anchor["version"] in (6,7,8,9,10,11,12,13,14,15,16,17,18,19,20) and phase == "clock" else PHASE_CAPS[phase][0]), "start cap")
                    starts[start] = phase
                if kind in ("runtime-entered", "control", "thread", "thread-bound", "turn", "generation", "dispatch", "host-dispatch"):
                    require(starts.get(start) == phase, "effect before allocated start")
                if kind == "runtime-entered":
                    require(start_counts[start, kind] == 1, "runtime start reuse")
                if kind == "control":
                    control_key = (start, wire_bytes(subject))
                    require(control_key not in controls, "control retry")
                    controls.add(control_key)
                    require(counts[kind] <= 24 and start_counts[start, kind] <= 4, "control cap")
                if kind == "thread":
                    key = (start, json.dumps(subject.get("request"), sort_keys=True))
                    require(key not in thread_requests, "thread reservation reuse")
                    thread_requests.add(key)
                    require(counts[kind] <= 8 and phase_counts[phase, kind] <= (5 if anchor["version"]==20 and phase=="clock" else 4 if anchor["version"] in (18,19) and phase=="clock" else 3 if anchor["version"] in (16,17,18,19,20) and phase=="clock" else PHASE_CAPS[phase][1]) and start_counts[start, kind] <= (2 if phase == "synthetic" else 1), "thread cap")
                if kind == "thread-bound":
                    key = (start, json.dumps(subject.get("request"), sort_keys=True))
                    require(key in thread_requests and isinstance(subject.get("thread"), str) and subject["thread"] not in thread_ids, "thread binding")
                    thread_ids[subject["thread"]] = start
                if kind == "turn":
                    if anchor["version"] == 20: require(start_counts[start, kind] <= 1, "MCP42 clock turn cap")
                    plan, thread = subject.get("plan"), subject.get("thread")
                    require(isinstance(plan, str) and plan not in plans and thread_ids.get(thread) == start, "turn identity")
                    plans[plan] = (start, thread)
                    require(counts[kind] <= 54 and phase_counts[phase, kind] <= PHASE_CAPS[phase][2], "turn cap")
                if kind in ("generation", "dispatch", "host-dispatch"):
                    plan = subject.get("plan")
                    require(plans.get(plan) == (start, subject.get("thread")), "effect plan/thread drift")
                    require(isinstance(subject.get("turn"), str) and bool(subject["turn"]) and turn_ids.get(plan, subject["turn"]) == subject["turn"], "effect turn drift")
                    if kind == "generation":
                        value = subject.get("generation")
                        require(type(value) is int and value == generations.get(plan, 0) + 1 and value <= 2 and counts[kind] <= 108, "generation cap/order")
                        if value == 2:
                            require(plan in dispatches and (phase == "clock" or plan in host_dispatches), "generation 2 before tool result")
                        generations[plan] = value
                        turn_ids[plan] = subject["turn"]
                    elif kind == "dispatch":
                        require(generations.get(plan) == 1 and plan not in dispatches and isinstance(subject.get("call"), str), "dispatch cap/order")
                        dispatches[plan] = subject
                    else:
                        require(plan in dispatches and plan not in host_dispatches, "host dispatch cap/order")
                        require(all(subject.get(k) == dispatches[plan].get(k) for k in ("thread", "turn", "plan", "call")), "host callback identity drift")
                        host_dispatches.add(plan)
                if kind in ("authority-apply", "recovery-apply"):
                    key = (kind, subject.get("ticket_sha256"))
                    require(isinstance(key[1], str) and len(key[1]) == 64 and key not in applies, "authority invocation reuse")
                    applies.add(key)
                if kind == "proxy-start" and anchor["version"] >= 3:
                    require(subject.get("slot") in ("s4", "s6") and subject.get("start_id") == (("s4-13" if anchor["version"]==20 else "s4-12" if anchor["version"]==19 else "s4-11" if anchor["version"]==18 else "s4-10" if anchor["version"]==17 else "s4-09" if anchor["version"]==16 else "s4-08" if anchor["version"] in (14,15,16,17,18,19,20) else "s4-07" if anchor["version"] in (9,10,11,12,13,14,15,16,17,18,19,20) else "s4-06" if anchor["version"]==8 else "s4-05" if anchor["version"]==7 else "s4-04" if anchor["version"] == 6 else "s4-03" if anchor["version"] == 5 else "s4-02") if subject["slot"] == "s4" else "s6-01"), "proxy phase allocation")
                    prior = [e for e in events if e["kind"] == "proxy-start" and e["subject"].get("slot") == subject["slot"]]
                    require(len(prior) == ((12 if anchor["version"]==20 else 11 if anchor["version"]==19 else 11 if anchor["version"]==20 else 10 if anchor["version"] in (18,19) else 9 if anchor["version"]==17 else 8 if anchor["version"]==16 else 7 if anchor["version"] in (14,15,16,17,18,19,20) else 6 if anchor["version"] in (9,10,11,12,13,14,15,16,17,18,19,20) else 5 if anchor["version"]==8 else 4 if anchor["version"]==7 else 3 if anchor["version"] == 6 else 2 if anchor["version"] == 5 else 1) if subject["slot"] == "s4" else 0), "proxy phase cap")
                if anchor["version"] >= 4:
                    if kind == "correction":
                        require(subject.get("class") in ("source", "content"), "correction class required")
                        key = "correction-" + subject["class"]
                        counts[key] = counts.get(key, 0) + 1
                    require(counts.get("correction-source", 0) <= (35 if anchor["version"]==20 else 30 if anchor["version"]==19 else 28 if anchor["version"]==18 else 25 if anchor["version"]==17 else 24 if anchor["version"]==16 else 23 if anchor["version"]==15 else 17 if anchor["version"]==14 else 16 if anchor["version"]==13 else 13 if anchor["version"]==12 else 12 if anchor["version"]==11 else 11 if anchor["version"]==10 else 10 if anchor["version"] in (9,10,11,12,13,14,15,16,17,18,19,20) else 9 if anchor["version"]==8 else 8 if anchor["version"]==7 else 7 if anchor["version"] == 6 else 6) and counts.get("correction-content", 0) <= 2, "correction class cap")
                maxima = (("proxy-start", 13 if anchor["version"]==20 else 12 if anchor["version"]==19 else 11 if anchor["version"]==18 else 10 if anchor["version"]==17 else 9 if anchor["version"] in (14,15,16,17,18,19,20) else 8 if anchor["version"] in (9,10,11,12,13,14,15,16,17,18,19,20) else 7 if anchor["version"]==8 else 6 if anchor["version"]==7 else 5 if anchor["version"] == 6 else 4 if anchor["version"] == 5 else 3), ("offline-start", 55 if anchor["version"]==20 else 41 if anchor["version"] in (14,15,16,17,18,19,20) else 39 if anchor["version"]==13 else 36), ("offline-thread", 72), ("offline-turn", 72), ("build", 24 if anchor["version"]==20 else 20 if anchor["version"]==19 else 19 if anchor["version"]==18 else 17 if anchor["version"]==17 else 16 if anchor["version"]==16 else 15 if anchor["version"]==15 else 13 if anchor["version"]==14 else 12 if anchor["version"]==13 else 11 if anchor["version"]==12 else 10 if anchor["version"]==11 else 9 if anchor["version"] in (9,10,11,12,13,14,15,16,17,18,19,20) else 8 if anchor["version"]==8 else 7 if anchor["version"]==7 else 6 if anchor["version"] == 6 else 5), ("correction", 37 if anchor["version"]==20 else 32 if anchor["version"]==19 else 30 if anchor["version"]==18 else 27 if anchor["version"]==17 else 26 if anchor["version"]==16 else 25 if anchor["version"]==15 else 19 if anchor["version"]==14 else 18 if anchor["version"]==13 else 15 if anchor["version"]==12 else 14 if anchor["version"]==11 else 13 if anchor["version"]==10 else 12 if anchor["version"] in (9,10,11,12,13,14,15,16,17,18,19,20) else 11 if anchor["version"]==8 else 10 if anchor["version"]==7 else 9 if anchor["version"] == 6 else 8 if anchor["version"] >= 4 else 6), ("review", 4 if anchor["version"] >= 4 else 3)) if anchor["version"] >= 3 else (("proxy-start", 2), ("offline-start", 55 if anchor["version"]==20 else 41 if anchor["version"] in (14,15,16,17,18,19,20) else 39 if anchor["version"]==13 else 36), ("offline-thread", 72), ("offline-turn", 72), ("build", 3), ("correction", 2), ("review", 2))
                for capped, maximum in maxima:
                    require(counts.get(capped, 0) <= maximum, capped + " cap")
                last_time, prev = at, row["sha256"]
                events.append(event)
        active = (paused_at if paused_at is not None else now) - excluded_ms
        return {"events": [row["event"] for row in current_rows], "history_events": events, "rows": current_rows,
                "prev": prev, "counts": counts, "excluded_ms": excluded_ms, "paused_at": paused_at,
                "stopped": stopped, "active_ms": active, "remaining_ms": min(self.anchor["total_deadline_ms"] - active, self.anchor["run_deadline_ms"] - now) if self.anchor["version"] >= 4 else self.anchor["total_deadline_ms"] - active}

    def _read_locked(self):
        raw = control_read(self.path)
        require(raw and raw.endswith(b"\n"), "missing or torn journal")
        return self._validate(self._rows(raw))

    def read(self):
        fd = checked_open(self.lock_path, os.O_RDWR)
        try:
            if self.anchor["version"] in (58, 59):
                self.os.budget_lock(fd, exclusive=False, deadline_ms=min(self.anchor["total_deadline_ms"], self.anchor["run_deadline_ms"]))
            else:
                bounded_flock(fd, fcntl.LOCK_SH, self.anchor["total_deadline_ms"])
            return self._read_locked()
        except BlockingIOError:
            raise HostRefusal("concurrent journal writer")
        finally:
            os.close(fd)

    def _candidate_row(self, state, kind, subject, phase, start, allow_closeout=False):
        if not allow_closeout:
            require(state["remaining_ms"] > self.execution_reserve_ms() and not state["stopped"], "execution budget/stop")
        event = {"seq": len(state["events"]), "prev": state["prev"], **{k: self.anchor[k] for k in ("approval", "work", "candidate")},
                 "phase": phase, "start": start, "kind": kind, "subject": subject, "at_ms": self._clock()}
        row = {"event": event, "sha256": digest(wire_bytes(event))}
        self._validate(state["rows"] + [row])
        return row

    def check_worker_result(self, subject, phase, start, requested_timeout):
        """Read-only admission, not a reservation; the result still needs reserve()."""
        fd = checked_open(self.lock_path, os.O_RDWR)
        try:
            if self.anchor["version"] in (58, 59):
                self.os.budget_lock(fd, exclusive=False, deadline_ms=min(self.anchor["total_deadline_ms"], self.anchor["run_deadline_ms"]))
            else:
                bounded_flock(fd, fcntl.LOCK_SH, self.anchor["total_deadline_ms"])
            state = self._read_locked()
            self._candidate_row(state, "worker-result", subject, phase, start)
            timeout = min(requested_timeout, (state["remaining_ms"] - self.execution_reserve_ms() - 20_000) / 1000)
            require(timeout > 0, "worker result budget margin")
            return timeout
        except BlockingIOError:
            raise HostRefusal("concurrent journal writer")
        finally:
            os.close(fd)

    def reserve(self, kind, subject, phase="controller", start="controller", allow_closeout=False):
        require(self.anchor["version"] not in (58, 59) or not getattr(self, "fresh_failed", False) or (allow_closeout and kind == "execution-stop"), "v58-journal-poisoned")
        fd = checked_open(self.lock_path, os.O_RDWR)
        try:
            if self.anchor["version"] in (58, 59):
                self.os.budget_lock(fd, exclusive=True, deadline_ms=min(self.anchor["total_deadline_ms"], self.anchor["run_deadline_ms"]))
            else:
                bounded_flock(fd, fcntl.LOCK_EX, self.anchor["total_deadline_ms"])
            state = self._read_locked()
            row = self._candidate_row(state, kind, subject, phase, start, allow_closeout)
            event = row["event"]
            with os.fdopen(checked_open(self.path, os.O_WRONLY | os.O_APPEND), "ab") as stream:
                stream.write(canonical(row))
                stream.flush()
                os.fsync(stream.fileno())
            return event
        except BlockingIOError:
            if self.anchor["version"] in (58, 59): self.fresh_failed = True
            raise HostRefusal("concurrent journal writer")
        except BaseException:
            if self.anchor["version"] in (58, 59): self.fresh_failed = True
            raise
        finally:
            os.close(fd)

    def execution_reserve_ms(self):
        if self.anchor["version"] == 59: return edit_u2.RESERVE_MS
        if self.anchor["version"] == 58: return 1_800_000
        return 1_200_000 + (858_141 if self.anchor["version"] >= 2 else 0)

    def resume_check(self, checkpoint, input_identity):
        require(self.anchor["version"] != 59, "edit-resume-forbidden")
        state = self.read()
        require(checkpoint["approval"] == self.anchor["approval"] and checkpoint["work"] == self.anchor["work"] and
                input_identity == self.anchor["input_identity"] == checkpoint["input_identity"], "resume approval/input drift")
        require(checkpoint["journal_seq"] < len(state["rows"]) and state["rows"][checkpoint["journal_seq"]]["sha256"] == checkpoint["journal_sha256"], "resume journal rollback")
        require(not checkpoint["sealed"] and not checkpoint["pending"] and not state["stopped"], "resume requires exact human recovery")
        require(state["remaining_ms"] > self.execution_reserve_ms(), "resume budget exhausted")
        return state


LIVE_METHODS = frozenset({"initialize", "account/read", "thread/start", "thread/read", "turn/prepare", "turn/startPrepared", "turn/interrupt"})


LIVE_NOTIFICATIONS = frozenset({"thread/started", "thread/status/changed", "turn/started", "turn/completed", "item/started",
    "item/completed", "item/agentMessage/delta", "item/reasoning/textDelta", "item/reasoning/summaryTextDelta",
    "item/reasoning/summaryPartAdded", "thread/tokenUsage/updated", "serverRequest/resolved"})


FIXTURE_NOTICE_POLICY = "build11-skip-host-skills"


FIXTURE_NOTICE_BUILD_SHA256 = "f98712bd91c8c50a8d56a1a462000030caef29a823842ce1b58e4d6084435c26"


def prepared_fixture_notice_message(argv, cwd, run, policy):
    if policy is None:
        return None
    expected = FIXTURE_NOTICE_BUILD_SHA256
    if isinstance(policy, dict):
        require(set(policy) == {"policy", "candidate"} and policy["policy"] == "build12-clock-fixture"
                and isinstance(policy["candidate"], str) and re.fullmatch(r"[0-9a-f]{64}", policy["candidate"]),
                "fixture candidate policy")
        expected = policy["candidate"]
    else:
        require(policy == FIXTURE_NOTICE_POLICY, "unsupported fixture notice policy")
    require(isinstance(argv, (list, tuple)) and len(argv) >= 2, "fixture notice argv")
    root, binary = Path(argv[-1]), Path(argv[-2])
    require(root.is_absolute() and root.resolve() == root and root == Path(run)
            and Path(cwd) == root / "cwd", "fixture notice root binding")
    require(binary.is_absolute() and binary.resolve() == binary
            and binary.name == "codex-prepared-tool-plan-fixture"
            and binary.is_file() and digest(binary.read_bytes()) == expected,
            "fixture notice build binding")
    return ("Under-development features enabled: skip_host_skill_discovery. "
            "Under-development features are incomplete and may behave unpredictably. "
            "To suppress this warning, set `suppress_unstable_features_warning = true` in "
            + str(root / "home/config.toml") + ".")


class FixtureNotificationFlow:
    """The exact two-response clock fixture, not a general live notification policy."""
    def __init__(self):
        self.thread = self.turn = None
        self.prepared = self.consuming = self.started = self.completed = False
        self.rate_updates, self.messages = 0, []

    def bind(self, kind, value):
        require(isinstance(value, str) and 0 < len(value.encode()) <= 256, "fixture event identity")
        require(getattr(self, kind) in (None, value), "fixture event foreign " + kind)
        setattr(self, kind, value)

    def before_request(self, method, params):
        if method in ("turn/prepare", "turn/startPrepared", "thread/read"):
            require(self.thread is not None and params.get("threadId") == self.thread,
                    "fixture request thread")
        if method == "turn/startPrepared":
            require(self.prepared and not self.consuming, "fixture consume order")
            self.consuming = True
        if method == "thread/read":
            require(self.completed, "fixture read before completion")

    def response(self, method, result):
        if method == "thread/start":
            self.bind("thread", result["thread"]["id"])
        elif method == "turn/prepare":
            require(not self.prepared, "fixture repeated prepare")
            self.prepared = True
        elif method == "turn/startPrepared":
            require(self.consuming, "fixture unrequested turn response")
            self.bind("turn", result["turn"]["id"])

    def event(self, method, params):
        require(isinstance(params, dict), "fixture event params")
        if method == "account/rateLimits/updated":
            require(self.consuming and self.turn is not None, "fixture rate update phase")
            require(set(params) == {"rateLimits"}, "fixture rate update fields")
            snapshot = params["rateLimits"]
            nullable = {"limitName", "normalModelSlug", "primary", "secondary", "credits",
                        "individualLimit", "spendControlReached", "planType", "rateLimitReachedType"}
            require(isinstance(snapshot, dict) and set(snapshot) == nullable | {"limitId"}
                    and snapshot["limitId"] == "codex" and all(snapshot[k] is None for k in nullable),
                    "unqualified fixture rate snapshot")
            self.rate_updates += 1  # Repeated sparse snapshots are not a budget reset.
            return
        if method == "thread/started":
            thread = params.get("thread")
            require(isinstance(thread, dict) and thread.get("ephemeral") is True,
                    "fixture thread notification")
            self.bind("thread", thread.get("id"))
            return
        self.bind("thread", params.get("threadId"))
        if method == "thread/status/changed":
            return
        require(self.consuming, "fixture turn event before consume")
        if method in ("turn/started", "turn/completed"):
            turn = params.get("turn")
            require(isinstance(turn, dict), "fixture turn notification")
            self.bind("turn", turn.get("id"))
            if method == "turn/started":
                require(not self.started and not self.completed, "fixture repeated turn start")
                self.started = True
            else:
                require(self.started and not self.completed and turn.get("status") == "completed"
                        and turn.get("error") is None, "fixture unsuccessful or repeated completion")
                self.completed = True
            return
        require(self.started and not self.completed, "fixture item phase")
        self.bind("turn", params.get("turnId"))
        if method == "item/completed":
            item = params.get("item")
            require(isinstance(item, dict), "fixture completed item")
            if item.get("type") == "agentMessage":
                text = item.get("text")
                require(text == "Prepared proof complete." and not self.messages,
                        "fixture final message mismatch or duplicate")
                self.messages.append({"bytes": len(text.encode()), "sha256": digest(text.encode())})

    def verify_complete(self):
        require(self.prepared and self.consuming and self.started and self.completed
                and self.rate_updates >= 2 and len(self.messages) == 1,
                "fixture notification flow incomplete")
        return {"thread_bound": True, "turn_bound": True, "completed_once": True,
                "rate_updates": self.rate_updates, "messages": self.messages}


class NativeNotificationFlow(FixtureNotificationFlow):
    """Bounded account metadata and per-turn identities; never execution authority."""
    def __init__(self):
        super().__init__()
        self.moderation_metadata = []

    @staticmethod
    def rate_snapshot(snapshot):
        fields = {"limitId", "limitName", "normalModelSlug", "primary", "secondary", "credits",
                  "individualLimit", "spendControlReached", "planType", "rateLimitReachedType"}
        require(isinstance(snapshot, dict) and set(snapshot) == fields, "native rate fields")
        for key in ("limitId", "limitName", "normalModelSlug"):
            value = snapshot[key]
            require(value is None or (isinstance(value, str) and 0 < len(value.encode()) <= 256), "native rate label")
        for key in ("primary", "secondary"):
            value = snapshot[key]
            if value is None: continue
            require(isinstance(value, dict) and set(value) == {"usedPercent", "windowDurationMins", "resetsAt"}, "native rate window")
            require(type(value["usedPercent"]) is int and 0 <= value["usedPercent"] < 100, "native quota exhausted or invalid")
            for name in ("windowDurationMins", "resetsAt"):
                require(value[name] is None or (type(value[name]) is int and 0 <= value[name] <= 9_223_372_036_854_775_807), "native rate time")
        credits = snapshot["credits"]
        if credits is not None:
            require(isinstance(credits, dict) and set(credits) == {"hasCredits", "unlimited", "balance"}
                    and type(credits["hasCredits"]) is bool and type(credits["unlimited"]) is bool
                    and (credits["balance"] is None or (isinstance(credits["balance"], str)
                         and re.fullmatch(r"[0-9]{1,20}(?:\.[0-9]{1,12})?", credits["balance"]))), "native credits schema")
        individual = snapshot["individualLimit"]
        if individual is not None:
            require(isinstance(individual, dict) and set(individual) == {"limit", "used", "remainingPercent", "resetsAt"}
                    and all(isinstance(individual[k], str) and re.fullmatch(r"[0-9]{1,20}(?:\.[0-9]{1,12})?", individual[k]) for k in ("limit", "used"))
                    and type(individual["remainingPercent"]) is int and 0 < individual["remainingPercent"] <= 100
                    and type(individual["resetsAt"]) is int and 0 <= individual["resetsAt"] <= 9_223_372_036_854_775_807, "native spend control")
        require(snapshot["spendControlReached"] is None or snapshot["spendControlReached"] is False, "native spend cap reached")
        require(snapshot["rateLimitReachedType"] is None, "native rate cap reached")
        plans = {"free", "go", "plus", "pro", "prolite", "promax", "team", "self_serve_business_prolite", "self_serve_business_usage_based", "business", "ent26", "enterprise_cbp_automation", "enterprise_cbp_usage_based", "enterprise", "edu", "edu_plus", "edu_pro"}
        require(snapshot["planType"] is None or (isinstance(snapshot["planType"], str) and snapshot["planType"] in plans), "native rate plan")

    def before_request(self, method, params):
        if method == "turn/prepare" and self.completed:
            self.verify_complete()
            thread = self.thread
            self.__init__()
            self.thread = thread
        super().before_request(method, params)

    def event(self, method, params):
        require(isinstance(params, dict), "native event params")
        if method == "turn/moderationMetadata":
            require(set(params)=={"threadId","turnId","metadata"} and self.thread is not None and self.turn is not None and params["threadId"]==self.thread and params["turnId"]==self.turn and self.prepared and self.consuming and self.started and not self.completed,"native moderation identity/phase")
            raw=wire_bytes(params["metadata"])
            require(len(raw)<=65536,"native moderation size")
            rows=getattr(self,"moderation_metadata",[])
            require(len(rows)<2,"native moderation count")
            rows.append({"bytes":len(raw),"sha256":digest(raw)})
            self.moderation_metadata=rows
            return
        if method == "account/rateLimits/updated":
            require(self.consuming and self.thread is not None and set(params) == {"rateLimits"}, "native rate phase")
            self.rate_snapshot(params["rateLimits"])
            self.rate_updates += 1
            return
        if method == "item/completed" and isinstance(params.get("item"), dict) and params["item"].get("type") == "agentMessage":
            self.bind("thread", params.get("threadId")); self.bind("turn", params.get("turnId"))
            text = params["item"].get("text")
            require(self.started and not self.completed and isinstance(text, str) and 0 < len(text.encode()) <= 65536, "native message phase or size")
            self.messages.append({"bytes": len(text.encode()), "sha256": digest(text.encode())})
            return
        super().event(method, params)

    def verify_complete(self):
        require(self.prepared and self.consuming and self.started and self.completed and self.messages, "native notification flow incomplete")
        return {"thread_bound": True, "turn_bound": True, "completed_once": True,
                "rate_updates": self.rate_updates, "messages": self.messages}


def bind_native_notifications(client, runtime, runtime_spec, anchor):
    require(anchor["version"] in (13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59) and runtime["binary_sha256"] == anchor["candidate"]
            and runtime_spec["candidate"] == anchor["candidate"]
            and runtime_spec["launch_contract_sha256"] == anchor["launch_contract_sha256"], "native notice candidate binding")
    root = Path(runtime_spec["root"])
    require(root.is_absolute() and root.resolve(strict=True) == root
            and runtime_spec["launch_identity"]["cwd"] == str(root / "cwd")
            and runtime_spec["launch_identity"]["argv"] == [runtime["binary"], "--role", "runtime", "--spec", runtime["spec"]]
            and digest(artifact_read(runtime["binary"], executable=True)) == anchor["candidate"], "native notice launch binding")
    client.fixture_notice_message = ("Under-development features enabled: skip_host_skill_discovery. "
        "Under-development features are incomplete and may behave unpredictably. "
        "To suppress this warning, set `suppress_unstable_features_warning = true` in " + str(root / "home/config.toml") + ".")
    client.clock_error_diagnostics = runtime_spec.get("phase") in ("clock", "synthetic")
    client.native_notifications = True
    client.fixture_flow = NativeNotificationFlow()
    client.native_direct_notice = None
    if anchor["version"] in (25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59) and runtime_spec.get("direct_tool_policy") == anchor.get("direct_tool_policy") and anchor["direct_tool_policy"]["mode"] == "direct":
        host_program = str(Path(runtime["binary"]).parent / "codex-code-mode-host")
        client.native_direct_notice = ("Code Mode is unavailable because failed to spawn code-mode host " + host_program + ": host executable was not found. Falling back to direct tools; enable `features.code_mode_host` and install `codex-code-mode-host`.")
        client.native_direct_notice_seen = False


class LiveClient:
    """Bounded native RPC transport, closed environment and metadata-only stderr."""
    def __init__(self, argv, cwd, run, deadline, env, on_spawn=None, *, fixture_notice=None, fixture_notifications=False):
        self.deadline, self.sequence, self.buffer = deadline, 0, b""
        self.events, self.event_counts = [], {}
        self.run, self.rpc_stage, self.initialized = run, "created", False
        self.stderr_size, self.stderr_hash = 0, hashlib.sha256()
        self.callback, self.on_event = None, None
        self.failed, self.cleanup, self.pending_responses = False, {}, {}
        self.fixture_notice_message = prepared_fixture_notice_message(argv, cwd, run, fixture_notice)
        require(type(fixture_notifications) is bool and (not fixture_notifications or self.fixture_notice_message is not None),
                "fixture notification policy requires exact build binding")
        self.fixture_flow = FixtureNotificationFlow() if fixture_notifications else None
        self.fixture_notice_thread = self.fixture_notice_pending_thread = None
        self.fixture_notice_started = self.fixture_notice_prepared = self.fixture_notice_pending = False
        self.fixture_notices = []
        self.process = None
        self.selector = selectors.DefaultSelector()
        try:
            self.process = subprocess.Popen(argv, cwd=cwd, env=env, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                            stderr=subprocess.PIPE, start_new_session=True, close_fds=True, bufsize=0)
            if on_spawn is not None:
                on_spawn(self.process)
            for name in ("stdout", "stderr"):
                stream = getattr(self.process, name)
                os.set_blocking(stream.fileno(), False)
                self.selector.register(stream, selectors.EVENT_READ, name)
            os.set_blocking(self.process.stdin.fileno(), False)
            durable_private(run / "process.json", {"pid": self.process.pid, "argv": argv, "started_ms": time.time_ns() // 1_000_000})
        except BaseException:
            self.failed = True
            try:
                if self.process is not None:
                    self.cleanup = end_process(self.process)
            finally:
                self.selector.close()
                if self.process is not None:
                    for name in ("stdin", "stdout", "stderr"):
                        getattr(self.process, name).close()
                durable_private(run / "startup-failure-metadata.json", {"runtime_started": self.process is not None,
                    "pid": self.process.pid if self.process is not None else None, **self.cleanup})
            raise

    def send(self, value):
        import select
        raw = canonical(value)
        if getattr(self,"diagnostic_policy",None) is not None and value.get("method")=="turn/startPrepared":
            require(self.diagnostic_policy==DIAGNOSTIC_POLICY and hasattr(self,"diagnostic_manifest_tokens"),"diagnostic prepare tokens missing")
            summary=diagnostic_token_summary(self.diagnostic_manifest_tokens,diagnostic_token_tree(raw)["params"]["manifest"])
            durable_private(self.run/"manifest-diagnostic.json",summary)
        require(len(raw) <= 2_097_152 and not self.failed, "outbound RPC unavailable")
        remaining = memoryview(raw)
        while remaining:
            timeout = self.deadline - time.monotonic()
            require(timeout > 0, "RPC send deadline")
            ready = select.select([], [self.process.stdin], [], min(timeout, 1))[1]
            if ready:
                try:
                    count = os.write(self.process.stdin.fileno(), remaining)
                except BlockingIOError:
                    continue
                require(count > 0, "closed RPC stdin")
                remaining = remaining[count:]
            self._poll(0)

    def _poll(self, timeout):
        for key, _ in self.selector.select(timeout):
            chunk = os.read(key.fileobj.fileno(), 65536)
            if not chunk:
                self.selector.unregister(key.fileobj)
                if key.data == "stdout":
                    require(self.process.poll() is None and bool(self.buffer), "runtime stdout closed")
                continue
            if key.data == "stderr":
                self.stderr_size += len(chunk)
                self.stderr_hash.update(chunk)
                require(self.stderr_size <= 1_048_576, "runtime stderr limit")
            else:
                self.buffer += chunk
                require(len(self.buffer) <= 4_194_304, "RPC frame limit")

    def receive(self):
        while b"\n" not in self.buffer:
            remaining = self.deadline - time.monotonic()
            require(remaining > 0, "RPC receive deadline")
            self._poll(min(remaining, 1))
        line, self.buffer = self.buffer.split(b"\n", 1)
        value = json.loads(line, object_pairs_hook=reject_duplicate_keys)
        if getattr(self,"diagnostic_policy",None) is not None and self.rpc_stage=="turn/prepare" and isinstance(value,dict) and isinstance(value.get("result"),dict) and "manifest" in value["result"]:
            require(not hasattr(self,"diagnostic_manifest_tokens"),"diagnostic prepare retry")
            self.diagnostic_manifest_tokens=diagnostic_token_tree(line)["result"]["manifest"]
        require(isinstance(value, dict), "nonobject RPC")
        return value

    def _fixture_notice_event(self, value):
        try:
            require(getattr(self, "fixture_notice_message", None) is not None and not self.failed,
                    "unknown native notification")
            require(set(value) <= {"jsonrpc", "method", "params", "emittedAtMs"}
                    and value.get("jsonrpc", "2.0") == "2.0"
                    and ("emittedAtMs" not in value or
                         (type(value["emittedAtMs"]) is int and 0 <= value["emittedAtMs"] <= 9_223_372_036_854_775_807)),
                    "fixture notice envelope")
            params = value.get("params")
            require(isinstance(params, dict) and set(params) == {"message", "threadId"}
                    and isinstance(params["message"], str) and len(params["message"].encode()) <= 4096
                    and params["message"] == self.fixture_notice_message
                    and isinstance(params["threadId"], str) and 0 < len(params["threadId"].encode()) <= 256,
                    "fixture notice schema or content")
            require(self.initialized and getattr(self, "account_bootstrap_validated", False)
                    and (self.fixture_notice_pending or
                         (getattr(self, "native_notifications", False) and self.rpc_stage == "thread/start"
                          and self.fixture_notice_thread is not None and not self.fixture_notice_prepared))
                    and self.fixture_notice_started
                    and self.rpc_stage in ("thread/start", "turn/prepare")
                    and self.event_counts["warning"] == 1 and not self.fixture_notices,
                    "fixture notice phase or duplicate")
            if self.fixture_notice_thread is not None:
                require(params["threadId"] == self.fixture_notice_thread, "fixture notice thread mismatch")
            else:
                require(self.rpc_stage == "thread/start", "unbound fixture notice")
                self.fixture_notice_pending_thread = params["threadId"]
            self.fixture_notices.append({"kind": "skip-host-skill-discovery-development-notice",
                                         "stage": self.rpc_stage,
                                         "message_sha256": digest(params["message"].encode()),
                                         "thread_bound": self.fixture_notice_thread is not None})
        except HostRefusal:
            self.failed = True
            raise

    def _fixture_notice_before_request(self, method, params):
        try:
            if method == "thread/start":
                require(self.initialized and getattr(self, "account_bootstrap_validated", False)
                        and not self.fixture_notice_started, "fixture notice thread admission")
                self.fixture_notice_started = True
            elif method == "turn/prepare":
                if getattr(self, "native_notifications", False) and self.fixture_notice_prepared:
                    require(params.get("threadId") == self.fixture_notice_thread and not self.fixture_notice_pending,
                            "native repeated prepare binding")
                    return
                require(self.fixture_notice_thread is not None and not self.fixture_notice_prepared
                        and params.get("threadId") == self.fixture_notice_thread,
                        "fixture notice prepare admission")
                self.fixture_notice_prepared = True
            self.fixture_notice_pending = True
        except HostRefusal:
            self.failed = True
            raise

    def _fixture_notice_response(self, method, result):
        try:
            if method == "thread/start":
                thread = result.get("thread")
                thread_id = thread.get("id") if isinstance(thread, dict) else None
                require(isinstance(thread_id, str) and 0 < len(thread_id.encode()) <= 256,
                        "fixture notice thread response")
                require(self.fixture_notice_pending_thread in (None, thread_id),
                        "fixture notice pending thread mismatch")
                self.fixture_notice_thread = thread_id
                for notice in self.fixture_notices:
                    notice["thread_bound"] = True
            elif method == "turn/prepare":
                require(len(self.fixture_notices) == 1 and self.fixture_notices[0]["thread_bound"],
                        "expected fixture notice unavailable")
            self.fixture_notice_pending = False
        except HostRefusal:
            self.failed = True
            raise

    def event(self, value):
        try:
            require(not self.failed, "notification after failure")
            self._event(value)
        except BaseException as error:
            self.failed = True
            method = value.get("method") if isinstance(value, dict) else None
            params = value.get("params") if isinstance(value, dict) else None
            raw = wire_bytes(params)
            self.notification_failure = {
                "method": method if isinstance(method, str) and re.fullmatch(r"[A-Za-z][A-Za-z0-9/._-]{0,127}", method) else None,
                "stage": getattr(self, "rpc_stage", "created"), "error_type": type(error).__name__,
                "params_bytes": len(raw), "params_sha256": digest(raw)}
            raise

    def _record_clock_error(self, value):
        flow=getattr(self,"fixture_flow",None)
        if not getattr(self,"clock_error_diagnostics",False) or not isinstance(flow,NativeNotificationFlow): return
        try:
            require(set(value)<={"jsonrpc","method","params","emittedAtMs"} and value.get("jsonrpc","2.0")=="2.0" and ("emittedAtMs" not in value or (type(value["emittedAtMs"]) is int and 0<=value["emittedAtMs"]<=9_223_372_036_854_775_807)),"error diagnostic envelope")
            p=value.get("params")
            require(isinstance(p,dict) and set(p)=={"error","willRetry","threadId","turnId"} and type(p["willRetry"]) is bool and flow.thread is not None and flow.turn is not None and p["threadId"]==flow.thread and p["turnId"]==flow.turn and flow.prepared and flow.consuming and flow.started and not flow.completed,"error diagnostic identity/phase")
            e=p["error"]
            require(isinstance(e,dict) and set(e)=={"message","codexErrorInfo","additionalDetails","misalignment"} and isinstance(e["message"],str) and 0<len(e["message"].encode())<=4096,"error diagnostic schema")
            raw=wire_bytes(e);require(len(raw)<=8192,"error diagnostic size")
            record={"bytes":len(raw),"sha256":digest(raw),"will_retry":p["willRetry"],"text_recorded":False}
            self.clock_error_evidence=record
            safe_text(e["message"])
            require(not re.search(r"(?i)(?:https?://|token|authorization|password|secret|cookie)",e["message"]),"error diagnostic private marker")
            record.update(message=e["message"],text_recorded=True)
            if isinstance(e["codexErrorInfo"],str) and re.fullmatch(r"[A-Za-z]{1,64}",e["codexErrorInfo"]): record["code"]=e["codexErrorInfo"]
        except HostRefusal:
            return  # Diagnostics never authorize acceptance or persist rejected text.

    def _event(self, value):
        require(isinstance(value, dict), "nonobject notification")
        method = value.get("method")
        require(isinstance(method, str) and re.fullmatch(r"[A-Za-z][A-Za-z0-9/._-]{0,127}",method), "event method missing or invalid")
        self.event_counts[method] = self.event_counts.get(method, 0) + 1
        require(sum(self.event_counts.values()) <= 20_000, "notification count limit")
        if len(self.events) < 128:
            self.events.append({"method": method, "request": "id" in value, "stage":getattr(self,"rpc_stage","created")})
        if method == "warning":
            params=value.get("params")
            if getattr(self,"native_direct_notice",None) is not None and isinstance(params,dict) and params.get("message")==self.native_direct_notice:
                require(set(value)<={"jsonrpc","method","params","emittedAtMs"} and value.get("jsonrpc","2.0")=="2.0" and ("emittedAtMs" not in value or (type(value["emittedAtMs"]) is int and 0<=value["emittedAtMs"]<=9_223_372_036_854_775_807)),"direct notice envelope")
                require(set(params)=={"message","threadId"} and params["threadId"]==self.fixture_notice_thread and self.fixture_notice_thread is not None and not self.failed and self.initialized and self.account_bootstrap_validated and self.native_notifications and self.fixture_notice_prepared and self.rpc_stage=="turn/startPrepared" and self.event_counts["warning"]==2 and len(self.fixture_notices)==1 and not self.native_direct_notice_seen,"direct notice binding")
                self.native_direct_notice_seen=True
                self.direct_notice_evidence={"kind":"approved-direct-mode-notice","message_sha256":digest(params["message"].encode()),"thread_bound":True,"stage":self.rpc_stage}
                return
            self._fixture_notice_event(value)
            return
        if method in ("configWarning", "error"):
            if method=="error": self._record_clock_error(value)
            self.failed = True
            raise HostRefusal("runtime warning/error; fallback not accepted")
        if "id" in value:
            if method != "item/tool/call" or self.callback is None:
                self.send({"id": value["id"], "error": {"code": -32601, "message": "unregistered host request"}})
                self.failed = True
                raise HostRefusal("unexpected server request")
            try:
                result = self.callback(value.get("params"))
                self.send({"id": value["id"], "result": result})
            except BaseException:
                self.failed = True
                raise
        else:
            if method == "account/updated":
                params=value.get("params")
                require(set(value)<={"jsonrpc","method","params","emittedAtMs"} and ("emittedAtMs" not in value or (type(value["emittedAtMs"]) is int and 0<=value["emittedAtMs"]<=9_223_372_036_854_775_807)),"account envelope schema")
                require(isinstance(params,dict) and set(params)=={"authMode","planType"},"account notification schema")
                require(getattr(self,"initialized",False) and self.rpc_stage in ("initialized","account/read","thread/start","turn/prepare") and self.event_counts[method]==1,"account notification phase or duplicate")
                require(params["authMode"]=="chatgpt" and params["planType"] in ("free","go","plus","pro","prolite","promax","team","self_serve_business_prolite","self_serve_business_usage_based","business","ent26","enterprise_cbp_automation","enterprise_cbp_usage_based","enterprise","edu","edu_plus","edu_pro"),"account mode or plan changed/unqualified")
                return  # Account details are neither persisted nor forwarded to the model.
            if method == "remoteControl/status/changed":
                params=value.get("params")
                require(set(value)<={"jsonrpc","method","params","emittedAtMs"} and ("emittedAtMs" not in value or (type(value["emittedAtMs"]) is int and 0<=value["emittedAtMs"]<=9_223_372_036_854_775_807)) and isinstance(params,dict) and set(params)=={"status","serverName","installationId","environmentId"},"remote status schema")
                require(getattr(self,"initialized",False) and self.rpc_stage in ("initialized","account/read","thread/start") and self.event_counts[method]==1,"remote status phase or duplicate")
                require(params["status"]=="disabled" and params["environmentId"] is None and all(isinstance(params[k],str) and len(params[k].encode())<=4096 for k in ("serverName","installationId")),"remote status not inactive")
                return  # Identity fields are neither persisted nor forwarded to the model.
            flow = getattr(self, "fixture_flow", None)
            if flow is not None:
                require(set(value) <= {"jsonrpc", "method", "params", "emittedAtMs"}
                        and value.get("jsonrpc", "2.0") == "2.0"
                        and ("emittedAtMs" not in value or (type(value["emittedAtMs"]) is int
                             and 0 <= value["emittedAtMs"] <= 9_223_372_036_854_775_807)),
                        "fixture notification envelope")
                require(method in LIVE_NOTIFICATIONS or method == "account/rateLimits/updated" or (isinstance(flow,NativeNotificationFlow) and method=="turn/moderationMetadata"),
                        "unknown native notification")
                require(self.initialized and getattr(self, "account_bootstrap_validated", False),
                        "fixture notification before account admission")
                flow.event(method, value.get("params"))
                if method in ("account/rateLimits/updated","turn/moderationMetadata"):
                    return  # Bounded metadata is never forwarded or used as execution authority.
            require(method in LIVE_NOTIFICATIONS, "unknown native notification")
            if self.on_event is not None:
                self.on_event(method, value.get("params", {}))

    def request(self, method, params):
        require(method in LIVE_METHODS and not self.failed, "unregistered client request")
        if method=="account/read":
            require(getattr(self,"initialized",False) and not getattr(self,"account_read_requested",False) and params=={"refreshToken":False},"account read repeated or refresh requested")
            self.account_read_requested=True
        if getattr(self, "fixture_notice_message", None) is not None:
            self._fixture_notice_before_request(method, params)
        if getattr(self, "fixture_flow", None) is not None:
            try:
                self.fixture_flow.before_request(method, params)
            except BaseException:
                self.failed = True
                raise
        self.rpc_stage=method
        self.sequence += 1
        number = self.sequence
        self.send({"id": number, "method": method, "params": params})
        while True:
            value = self.receive()
            if "method" in value:
                self.event(value)
                continue
            valid=value.get("id")==number and "error" not in value and isinstance(value.get("result"),dict)
            if not valid:
                error=value.get("error");error=error if isinstance(error,dict) else {}
                message=error.get("message")
                self.rpc_failure={"method":method,"stage":self.rpc_stage,"id_matches":value.get("id")==number,"has_error":"error" in value,"error_code":error.get("code") if type(error.get("code")) is int else None,"error_message_sha256":digest(message.encode()) if isinstance(message,str) else None}
            require(valid,"RPC refused or identity drift")
            if getattr(self, "fixture_notice_message", None) is not None:
                self._fixture_notice_response(method, value["result"])
            if getattr(self, "fixture_flow", None) is not None:
                try:
                    self.fixture_flow.response(method, value["result"])
                except BaseException:
                    self.failed = True
                    raise
            if method=="initialize":self.initialized=True;self.rpc_stage="initialized"
            return value["result"]

    def validate_account_bootstrap(self):
        value=self.request("account/read",{"refreshToken":False})
        self.validate_account_result(value)
        self.account_bootstrap_validated=True

    @staticmethod
    def validate_account_result(value):
        require(isinstance(value,dict) and set(value)=={"account","requiresOpenaiAuth","workspaceRouting"} and value["requiresOpenaiAuth"] is True,"account read schema")
        account=value["account"];route=value["workspaceRouting"]
        require(isinstance(account,dict) and set(account)=={"type","email","planType"} and account["type"]=="chatgpt" and (account["email"] is None or isinstance(account["email"],str)),"account read auth schema")
        require(isinstance(route,dict) and set(route)=={"chatgptAccountId","backendOrigin","accountRoutingOverride"} and isinstance(route["chatgptAccountId"],str) and 0<len(route["chatgptAccountId"])<=4096 and route["backendOrigin"]=="https://chatgpt.com" and route["accountRoutingOverride"] in ("NO_CONSTRAINT","us","us_cr"),"account routing escaped approved origin")
        require(account["planType"] in ("free","go","plus","pro","prolite","promax","team","self_serve_business_prolite","self_serve_business_usage_based","business","ent26","enterprise_cbp_automation","enterprise_cbp_usage_based","enterprise","edu","edu_plus","edu_pro"),"account plan unqualified")
        # Deliberately return no account/identifier data to the caller or evidence.

    def drain(self, seconds=0.05):
        until = min(self.deadline, time.monotonic() + seconds)
        while time.monotonic() < until or b"\n" in self.buffer:
            self._poll(max(0, min(0.01, until - time.monotonic())))
            while b"\n" in self.buffer:
                value = self.receive()
                require("method" in value, "unexpected late RPC response")
                self.event(value)

    def close(self):
        try:
            self.cleanup = end_process(self.process)
        finally:
            self.selector.close()
            for name in ("stdin", "stdout", "stderr"):
                getattr(self.process, name).close()
            self.cleanup.update(stderr_bytes=self.stderr_size, stderr_sha256=self.stderr_hash.hexdigest())
            durable_private(self.run/"rpc-metadata.json",{"stage":self.rpc_stage,"initialized":self.initialized,"event_counts":self.event_counts,"events":self.events,"failed":self.failed,"rpc_failure":getattr(self,"rpc_failure",None),"notification_failure":getattr(self,"notification_failure",None),"fixture_notices":getattr(self,"fixture_notices",[]),"direct_notice":getattr(self,"direct_notice_evidence",None),"clock_error":getattr(self,"clock_error_evidence",None),"moderation_metadata":getattr(getattr(self,"fixture_flow",None),"moderation_metadata",[])})


def native_document_schema(schema):
    """Exact current native JsonSchema projection for the four fixed tools.

    Native JsonSchema omits maxItems, uniqueItems and pattern. The host validates
    these constraints before effects; their absence is not treated as permission.
    """
    require(isinstance(schema, dict), "tool schema object")
    known = {"type", "properties", "items", "minItems", "maxItems", "uniqueItems", "pattern", "enum", "required", "additionalProperties"}
    require(set(schema) <= known, "unknown fixed tool schema field")
    result = {}
    for key, value in schema.items():
        if key in ("maxItems", "uniqueItems", "pattern"):
            continue
        if key == "properties":
            result[key] = {name: native_document_schema(item) for name, item in value.items()}
        elif key == "items":
            result[key] = native_document_schema(value)
        else:
            result[key] = value
    if "type" not in result and "enum" in result:
        require(bool(result["enum"]) and all(isinstance(value,str) for value in result["enum"]), "fixed tool enum must contain strings")
        result["type"] = "string"
    return result


class Admission(EffectAdmission):
    """Codex prepared snapshot validation and explicit native/logical identity map."""
    def __init__(self, identity, source, candidate, template, tools, budget, phase, start):
        super().__init__(identity, tools, budget, phase, start)
        self.source, self.candidate, self.template = source, candidate, template

    @property
    def thread(self):
        return self.session

    @thread.setter
    def thread(self, value):
        self.session = value

    @property
    def turn(self):
        return self.step

    @turn.setter
    def turn(self, value):
        self.step = value

    def dispatch_subject(self, call):
        return {"thread": self.thread, "turn": self.turn, "plan": self.plan, "call": call}

    def authority_subject(self):
        return {"thread": self.thread, "turn": self.turn, "call": self.call}

    def callback(self, params):
        require(not self.stopped and not self.completed and self.call is None and self.turn is not None, "callback outside active turn")
        require(isinstance(params, dict) and set(params) == {"threadId", "turnId", "callId", "namespace", "tool", "arguments"}, "callback fields")
        require(params["threadId"] == self.thread and params["turnId"] == self.turn and params["namespace"] is None, "foreign callback identity")
        return super().callback({"session": params["threadId"], "step": params["turnId"], "call": params["callId"],
                                 "tool": params["tool"], "arguments": params["arguments"]})

    def bind(self, thread, prepared, inputs):
        require(not self.stopped and self.completed and isinstance(thread, str), "admission not idle")
        require(self.thread in (None, thread), "foreign thread")
        require(set(prepared) == {"handle", "manifest"} and isinstance(prepared["handle"], str), "prepared shape")
        manifest = prepared["manifest"]
        require(set(manifest) == {"version", "planId", "sourceIdentity", "buildIdentity", "snapshot", "toolEnvelope"}, "manifest fields")
        require(manifest["version"] == 1 and manifest["sourceIdentity"] == self.source and manifest["buildIdentity"] == "sha256:" + self.candidate, "manifest source/build drift")
        snapshot, envelope = manifest["snapshot"], manifest["toolEnvelope"]
        core_input = [{"type": "text", "text": item["text"], "text_elements": []} for item in inputs]
        require(snapshot["initial_input"] == core_input, "prepared input replacement")
        binding = snapshot["history_binding"]
        require(binding["input_template"] == self.template and binding["input_sha256"] == digest(wire_bytes(core_input)) and
                type(binding["count"]) is int and binding["count"] >= 0 and isinstance(binding["sha256"], str), "history/input binding")
        context = snapshot["context"]
        require(context["model"]["slug"] == "gpt-6-astra" and context["reasoning_effort"] == "xhigh" and
                context["wire_profile"] == {"api": "responses_http", "include_internal": False, "compression": "none", "authentication": "native_read_only"}, "runtime model/wire drift")
        require(set(envelope) == {"entries", "model_specs", "tool_mode", "namespaces", "policy"} and envelope["tool_mode"] == "direct", "tool envelope fields/mode")
        expected_names = {tool["name"] for tool in self.tools}
        entries = envelope.get("entries", [])
        require(len(entries) == len(expected_names) and {entry.get("name") for entry in entries} == expected_names, "tool inventory drift")
        for entry in entries:
            require(entry.get("origin") == "dynamic" and entry.get("namespace") == "functions" and
                    entry.get("exposure") in ("direct", "direct_model_only") and entry.get("implementation", "").endswith("::DynamicToolHandler"), "tool handler drift")
            definition = next(tool for tool in self.tools if tool["name"] == entry["name"])
            spec = entry["spec"]
            require(spec == {"type": "function", "name": definition["name"], "description": definition["description"],
                             "strict": False, "parameters": native_document_schema(definition["inputSchema"])}, "tool schema drift")
        policy = envelope["policy"]
        require(policy == {"expose_additional_permissions": False, "require_managed_sandbox": False, "require_unified_exec": False,
                           "allowed_tools": [{"namespace": None, "name": tool["name"]} for tool in self.tools]}, "tool permission drift")
        require(isinstance(envelope["model_specs"], list) and len(envelope["model_specs"]) == 4 and
                sorted(envelope["model_specs"], key=lambda value: value.get("name", "")) == sorted([entry["spec"] for entry in entries], key=lambda value: value["name"]), "model-visible tool drift")
        envelope_sha = digest(wire_bytes(envelope))
        require(self.envelope_sha in (None, envelope_sha), "same-thread envelope drift")
        self.envelope_sha = envelope_sha
        self.thread, self.plan = thread, manifest["planId"]
        self.manifest_sha = digest(wire_bytes(manifest))
        self.turn, self.call, self.completed = None, None, False
        return manifest

    def bind_turn(self, turn):
        require(isinstance(turn, str) and turn and self.turn in (None, turn), "foreign turn")
        self.turn = turn



def phase_transport_limit(state, slot, version=6):
    if version == 59:
        require(slot == edit_u2.SLOT and not state["stopped"], "edit-transport-slot-stop")
        used = sum(e["kind"] in ("control", "generation") for e in state["events"])
        require(0 <= used < 13, "edit-transport-cap")
        return 13 - used
    if version == 58:
        require(slot == 's4' and not state['stopped'], 'v58-transport-slot-stop')
        used = sum(e['kind'] in ('control', 'generation') for e in state['events'])
        require(0 <= used < 12, 'v58-transport-cap')
        return 12 - used
    if version in (31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57):
        cfg=u2_allocation(version);cap=4+2*cfg["turns"]
        require(slot==cfg.get("proxy_slot","s4"),"U2 transport slot")
        used=sum(e["kind"] in ("control","generation") for e in state["events"])
        require(0<=used<cap,"U2 transport cap")
        return cap-used
    if version in (24,25,26,27,28,29,30):
        require(slot=="s4","clock transport slot")
        used=sum(e["kind"] in ("control","generation") and e["start"]==clock_allocation(version)["start"] for e in state["events"])
        require(0<=used<4,"clock transport cap")
        return 4-used
    if version in (21,22,23):
        require(slot=="s4","diagnostic transport slot")
        used=sum(e["kind"]=="control" and e["start"]==diagnostic_allocation(version)["start"] for e in state["events"])
        require(0<=used<2,"diagnostic transport cap")
        return 2-used
    require(slot in ("s4", "s6"), "transport phase")
    if version == 20:
        require(slot == "s4", "MCP41 clock-only transport")
        events = state.get("history_events", state["events"])
        used = sum(e["kind"] in ("control", "generation") and e["start"] == "clock-11" for e in events)
        require(0 <= used < 6, "MCP41 transport cap")
        return 6 - used
    phases = ("clock", "synthetic") if slot == "s4" else ("h10",)
    events = state.get("history_events", state["events"])
    controls = sum(4 * ((10 if version in (18,19,20) and p=="clock" else 9 if version==17 and p=="clock" else 8 if version==16 and p=="clock" else 7 if version in (14,15,16,17,18,19,20) and p=="clock" else 6 if version in (9,10,11,12,13,14,15,16,17,18,19,20) and p=="clock" else 5 if version==8 and p=="clock" else 4 if version==7 and p=="clock" else PHASE_CAPS[p][0]) - sum(e["kind"] == "start" and e["phase"] == p for e in events)) for p in phases)
    generations = sum(2 * PHASE_CAPS[p][2] - sum(e["kind"] == "generation" and e["phase"] == p for e in events) for p in phases)
    count = state["counts"]
    limit = min(controls, 24 - count.get("control", 0)) + min(generations, 108 - count.get("generation", 0))
    require(0 < limit <= (44 if slot == "s4" else 88), "transport remaining budget")
    return limit


def idle_deadline_wall_ms(now_ms, runtime_expiry_ms, proxy_expiry_ms, auth_expiry_ms):
    require(all(type(value) is int and value > now_ms for value in (runtime_expiry_ms, proxy_expiry_ms, auth_expiry_ms)), "idle resource lifetime unavailable")
    deadline = min(now_ms + 900_000, runtime_expiry_ms - 60_000, proxy_expiry_ms - 60_000, auth_expiry_ms - 60_000)
    require(deadline > now_ms, "idle resource lifetime exhausted")
    return deadline


def frozen_network_peer(version, addresses, evidence):
    import ipaddress
    require(isinstance(addresses,list) and 0 < len(addresses) <= 32 and len(set(addresses))==len(addresses)
            and all(str(ipaddress.ip_address(ip))==ip and ipaddress.ip_address(ip).is_global and not ipaddress.ip_address(ip).is_multicast for ip in addresses), "FD frozen addresses")
    expected={"host":"chatgpt.com","addresses":addresses,"resolution_count":1}
    if version in (58, 59):
        expected["selected_peer"] = "104.18.32.47"
        require(type(evidence.get("resolution_count")) is int and "104.18.32.47" in addresses,
                "v58-approved-peer-unavailable")
        require(evidence == expected, "v58-FD-resolver-binding")
        return "104.18.32.47"
    if version in (6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57):
        expected["selected_peer"]="104.18.32.47"
        require(type(evidence.get("resolution_count")) is int,"DNS resolution count type")
        require("104.18.32.47" in addresses,"approved peer absent from fresh DNS")
    require(evidence==expected,"FD resolver binding")
    return "104.18.32.47" if version in (6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57) else addresses[0]


class PreparedFdController:
    """One slot's connected-FD broker; native credentials never pass through this object."""
    def __init__(self, budget, slot, root, socket_path, addresses, resolver_evidence):
        import socket
        import threading
        import secrets
        import ipaddress
        self.budget, self.slot, self.root, self.socket_path = budget, slot, Path(root), Path(socket_path)
        require(slot in ("s4", "s6") and self.root.resolve(strict=True) == self.root and
                self.socket_path.parent.resolve(strict=True) == self.socket_path.parent and
                not os.path.lexists(self.socket_path) and len(os.fsencode(self.socket_path)) < 104, "FD controller paths")
        require(isinstance(addresses, list) and 0 < len(addresses) <= 32 and len(set(addresses)) == len(addresses), "FD frozen addresses")
        require(all(str(ipaddress.ip_address(ip)) == ip and ipaddress.ip_address(ip).is_global and
                    not ipaddress.ip_address(ip).is_multicast for ip in addresses), "FD target not public")
        self.selected_peer = frozen_network_peer(budget.anchor["version"],addresses,resolver_evidence)
        if budget.anchor["version"] in (58, 59):
            require(self.selected_peer == "104.18.32.47", "v58-FD-peer-binding")
        state = budget.read()
        require(not state["stopped"] and state["paused_at"] is None and state["remaining_ms"] > budget.execution_reserve_ms(), "FD budget unavailable")
        last = state["events"][-1]
        expected = {"slot":slot, "start_id":((clock_allocation(budget.anchor["version"])["proxy_start"] if budget.anchor["version"] in (24,25,26,27,28,29,30) else diagnostic_allocation(budget.anchor["version"])["proxy_start"] if budget.anchor["version"] in (21,22,23) else "s4-13" if budget.anchor["version"]==20 else "s4-12" if budget.anchor["version"]==19 else "s4-11" if budget.anchor["version"]==18 else "s4-10" if budget.anchor["version"]==17 else "s4-09" if budget.anchor["version"]==16 else "s4-08" if budget.anchor["version"] in (14,15,16,17,18,19,20) else "s4-07" if budget.anchor["version"] in (9,10,11,12,13,14,15,16,17,18,19,20) else "s4-06" if budget.anchor["version"]==8 else "s4-05" if budget.anchor["version"]==7 else "s4-04" if budget.anchor["version"] == 6 else "s4-03" if budget.anchor["version"] == 5 else "s4-02") if slot=="s4" else "s6-01")} if budget.anchor["version"] >= 3 else {"slot":slot}
        if budget.anchor["version"] in (31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57):expected={"slot":u2_allocation(budget.anchor["version"]).get("proxy_slot","s4"),"start_id":u2_allocation(budget.anchor["version"])["proxy_start"]}
        if budget.anchor["version"] == 58: expected = {"slot":"s4", "start_id":"v58-" + budget.anchor["run_id"]}
        if budget.anchor["version"] == 59: expected = {"slot":edit_u2.SLOT, "start_id":"edit-" + budget.anchor["run_id"]}
        require(last["kind"] == "proxy-start" and last["subject"] == expected, "FD proxy reservation missing")
        self.max_requests = phase_transport_limit(state, slot, budget.anchor["version"])
        self.reservation, self.addresses, self.nonce = state["prev"], list(addresses), secrets.token_hex(32)
        self.proxy, self.thread, self.failed, self.closed = None, None, None, False
        self.condition = threading.Condition(threading.RLock())
        self.bindings, self.leases, self.used, self.next = {}, {}, set(), 0
        self.lease_bindings = {}
        self.listener = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.channel, self.proxy_channel = socket.socketpair(socket.AF_UNIX, socket.SOCK_DGRAM)
        try:
            self.listener.bind(str(self.socket_path)); os.chmod(self.socket_path, 0o600); self.listener.listen(4)
            self.socket_identity = (self.socket_path.lstat().st_dev, self.socket_path.lstat().st_ino)
            self.channel.settimeout(0.25)
            self.log_fd = os.open(self.root / "fd-events.jsonl", os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC, 0o600)
            self._record("controller-ready", {"slot": slot, "reservation_sha256": self.reservation,
                         "candidate": budget.anchor["candidate"], "anchor_sha256": budget.anchor_sha256})
        except BaseException:
            self.listener.close(); self.channel.close(); self.proxy_channel.close(); raise

    def _record(self, kind, metadata):
        raw = canonical({"kind": kind, "at_ms": time.time_ns() // 1_000_000, **metadata})
        require(os.write(self.log_fd, raw) == len(raw), "FD evidence short write")
        os.fsync(self.log_fd)

    def transport_spec(self):
        return {"listener_fd": self.listener.fileno(), "broker_fd": self.proxy_channel.fileno(),
                "path": str(self.socket_path), "controller_pid": os.getpid(), "controller_uid": os.getuid(),
                "nonce": self.nonce, "candidate": self.budget.anchor["candidate"], "work": self.budget.anchor["work"],
                "slot": self.slot, "anchor_sha256": self.budget.anchor_sha256, "reservation_sha256": self.reservation, "max_requests":self.max_requests}

    def runtime_transport(self):
        return {"path": str(self.socket_path), "nonce": self.nonce, "slot": self.slot, "max_requests":self.max_requests}

    def launch_proxy(self, argv, cwd, env, deadline):
        import threading
        require(self.proxy is None and self.thread is None and deadline > time.monotonic(), "FD proxy start reuse")
        self.deadline = deadline
        self.proxy_out = (self.root / "proxy.stdout").open("xb")
        self.proxy_err = (self.root / "proxy.stderr").open("xb")
        try:
            self.proxy = subprocess.Popen(argv, cwd=cwd, env=env, stdin=subprocess.DEVNULL,
                stdout=self.proxy_out, stderr=self.proxy_err, start_new_session=True,
                pass_fds=(self.listener.fileno(), self.proxy_channel.fileno()))
            self._record("proxy-launched", {"pid": self.proxy.pid})
            self.listener.close(); self.proxy_channel.close()
            self.thread = threading.Thread(target=self._serve, name="prepared-fd-controller", daemon=False)
            self.thread.start()
        except BaseException:
            self.close(); raise

    def register_runtime(self, runtime, process):
        raw = control_read(runtime["spec"])
        require(digest(raw) == runtime["spec_sha256"], "FD runtime spec drift")
        spec = json.loads(raw, object_pairs_hook=reject_duplicate_keys)
        require(spec["transport"] == self.runtime_transport() and spec["candidate"] == self.budget.anchor["candidate"] and
                spec["work"] == self.budget.anchor["work"] and spec["journal_anchor_sha256"] == self.budget.anchor_sha256,
                "FD runtime role binding")
        state = self.budget.read()
        starts = [e for e in state["events"] if e["kind"] == "start" and e["start"] == spec["start"]]
        require(len(starts) == 1 and starts[0]["subject"]["runtime_spec_sha256"] == runtime["spec_sha256"], "FD runtime start reservation")
        with self.condition:
            require(not self.closed and not self.failed and spec["start"] not in self.bindings and process.poll() is None, "FD runtime registration reuse/death")
            self.bindings[spec["start"]] = {"process": process, "spec_sha256": runtime["spec_sha256"], "phase": spec["phase"], "sequence": 0}
            self._record("runtime-bound", {"start": spec["start"], "pid": process.pid, "spec_sha256": runtime["spec_sha256"]})
            self.condition.notify_all()

    def _request(self, request):
        import socket
        import array
        import ipaddress
        fields = {"version", "request_id", "nonce", "candidate", "work", "slot", "anchor_sha256", "reservation_sha256",
                  "proxy_pid", "runtime_pid", "start", "spec_sha256", "runtime_sequence", "host", "port"}
        require(isinstance(request, dict) and set(request) == fields, "FD request schema")
        for key in ("version", "request_id", "proxy_pid", "runtime_pid", "runtime_sequence", "port"):
            require(type(request[key]) is int, "FD request integer")
        require(request["version"] == 1 and request["request_id"] == self.next and self.next < self.max_requests and
                request["nonce"] == self.nonce and request["candidate"] == self.budget.anchor["candidate"] and
                request["work"] == self.budget.anchor["work"] and request["slot"] == self.slot and
                request["anchor_sha256"] == self.budget.anchor_sha256 and request["reservation_sha256"] == self.reservation and
                request["proxy_pid"] == self.proxy.pid and self.proxy.poll() is None and
                request["host"] == "chatgpt.com" and request["port"] == 443, "FD request binding")
        with self.condition:
            # Registration follows Popen; waiting here has no network effect and does not retry a failed request.
            self.condition.wait_for(lambda: request["start"] in self.bindings or self.closed, timeout=2)
            binding = self.bindings.get(request["start"])
            require(binding is not None and not self.closed and binding["process"].pid == request["runtime_pid"] and
                    binding["process"].poll() is None and binding["spec_sha256"] == request["spec_sha256"] and
                    binding["sequence"] == request["runtime_sequence"], "FD runtime identity/replay")
            state = self.budget.read()
            require(not state["stopped"] and state["paused_at"] is None and state["remaining_ms"] > self.budget.execution_reserve_ms(), "FD current budget")
            event = state["events"][-1]
            require(event["start"] == request["start"] and event["phase"] == binding["phase"] and event["kind"] in ("control", "generation") and
                    state["prev"] not in self.used, "FD send reservation absent/reused")
            self.used.add(state["prev"]); self.next += 1; binding["sequence"] += 1
            ip = self.selected_peer  # Frozen before launch; connect failure never selects another address.
            family = socket.AF_INET6 if ipaddress.ip_address(ip).version == 6 else socket.AF_INET
            peer = (ip, 443, 0, 0) if family == socket.AF_INET6 else (ip, 443)
            metadata = {"request_id": request["request_id"], "runtime_pid": request["runtime_pid"], "start": request["start"],
                        "spec_sha256": request["spec_sha256"], "journal_seq": event["seq"], "journal_sha256": state["prev"], "peer": ip, "port": 443}
            self._record("fd-reserved", metadata)  # durable before TCP connect and SCM_RIGHTS
            stream = socket.socket(family, socket.SOCK_STREAM)
            try:
                stream.settimeout(min(5, max(0.001, self.deadline - time.monotonic())))
                stream.connect(peer)
                require(stream.getpeername()[:2] == peer[:2], "FD connected peer drift")
                lease = stream.dup(); lease.settimeout(None)
                self.leases[request["request_id"]] = (request["start"], lease)
                self.lease_bindings[request["request_id"]] = {key:request[key] for key in ("runtime_pid","start","runtime_sequence")}
                text_peer = f"[{ip}]:443" if family == socket.AF_INET6 else f"{ip}:443"
                payload = wire_bytes({"request": request, "peer": text_peer})
                require(self.channel.sendmsg([payload], [(socket.SOL_SOCKET, socket.SCM_RIGHTS, array.array("i", [stream.fileno()]))]) == len(payload), "FD transfer short send")
                self._record("fd-issued", metadata)
            finally:
                stream.close()

    def _release(self, request):
        fields = {"kind","request_id","nonce","candidate","work","slot","anchor_sha256","reservation_sha256","proxy_pid","runtime_pid","start","runtime_sequence"}
        require(isinstance(request, dict) and set(request)==fields and request["kind"]=="release", "FD release schema")
        for key, expected in (("nonce",self.nonce),("candidate",self.budget.anchor["candidate"]),("work",self.budget.anchor["work"]),
                ("slot",self.slot),("anchor_sha256",self.budget.anchor_sha256),("reservation_sha256",self.reservation),("proxy_pid",self.proxy.pid)):
            require(request[key]==expected,"FD release binding")
        with self.condition:
            identifier=request["request_id"]
            require(type(identifier) is int and identifier in self.leases and identifier in self.lease_bindings,"FD release absent or reused")
            require(self.lease_bindings[identifier]=={key:request[key] for key in ("runtime_pid","start","runtime_sequence")},"FD release runtime binding")
            owner,lease=self.leases.pop(identifier);lease.close();del self.lease_bindings[identifier]
            self._record("fd-released",{"request_id":identifier,"start":owner})
            reply=wire_bytes({"kind":"released","request_id":identifier,"nonce":self.nonce})
            require(self.channel.send(reply)==len(reply),"FD release acknowledgement failed")
            self.condition.notify_all()

    def wait_for_release(self, start, seconds=5):
        with self.condition:
            ready=self.condition.wait_for(lambda:self.failed or not any(owner==start for owner,_ in self.leases.values()),timeout=min(5,seconds))
            require(ready and not self.failed and not any(owner==start for owner,_ in self.leases.values()),"FD completion not acknowledged")

    def _serve(self):
        import socket
        import array
        try:
            while not self.closed:
                require(time.monotonic() < self.deadline and self.proxy.poll() is None, "FD proxy lifetime")
                for start, binding in list(self.bindings.items()):
                    if binding["process"].poll() is not None:
                        self.revoke(start)
                try:
                    raw, ancillary, flags, _ = self.channel.recvmsg(8193, socket.CMSG_SPACE(512 * 4))
                except socket.timeout:
                    continue
                # Proxy must send only a request. Close unsolicited descriptors even on rejection.
                for level, kind, data in ancillary:
                    if level == socket.SOL_SOCKET and kind == socket.SCM_RIGHTS:
                        fds = array.array("i"); fds.frombytes(data[:len(data) - len(data) % fds.itemsize])
                        for fd in fds:
                            os.close(fd)
                require(raw and len(raw) <= 8192 and not ancillary and not flags, "FD request ancillary/size")
                request = json.loads(raw, object_pairs_hook=reject_duplicate_keys)
                if request.get("kind") == "release": self._release(request)
                else: self._request(request)
        except BaseException as error:
            self.failed = type(error).__name__
            self._record("controller-refused", {"error_type": self.failed})
            self.revoke()
            if self.proxy is not None and self.proxy.poll() is None:
                self.proxy_cleanup = end_process(self.proxy)

    def revoke(self, start=None):
        import socket
        with self.condition:
            for key, (owner, lease) in list(self.leases.items()):
                if start is None or owner == start:
                    try:
                        lease.shutdown(socket.SHUT_RDWR)
                    except OSError:
                        pass
                    lease.close(); del self.leases[key]; self.lease_bindings.pop(key, None)
                    self._record("fd-revoked", {"request_id": key, "start": owner})

    def close(self):
        import threading
        if self.closed:
            return
        with self.condition:
            self.closed = True; self.condition.notify_all()
        self.revoke()
        if self.proxy is not None and self.proxy.poll() is None:
            self.proxy_cleanup = end_process(self.proxy)
        if self.thread is not None and self.thread is not threading.current_thread():
            self.thread.join(timeout=7)
            require(not self.thread.is_alive(), "FD controller did not stop")
        self.listener.close(); self.channel.close(); self.proxy_channel.close()
        for name in ("proxy_out", "proxy_err"):
            if hasattr(self, name):
                getattr(self, name).close()
        if hasattr(self, "log_fd"):
            self._record("controller-closed", {"leases": len(self.leases)})
            os.close(self.log_fd)


def protected_auth_metadata(auth_home):
    # Metadata only: never read, copy or hash credential/config contents here.
    def visit(path):
        try:
            st = path.lstat()
        except FileNotFoundError:
            return {"absent": True}
        require(not stat.S_ISLNK(st.st_mode), "protected metadata alias")
        value = {key:getattr(st,key) for key in ("st_dev","st_ino","st_size","st_mode","st_mtime_ns","st_ctime_ns")}
        if stat.S_ISDIR(st.st_mode):
            value["entries"] = {child.name:visit(child) for child in sorted(path.iterdir())}
        return value
    return {name:visit(Path(auth_home)/name) for name in ("config.toml","auth.json","secrets","rules")}


def validate_native_launch(runtime, spec, anchor, anchor_sha256, env):
    require(set(runtime)=={"binary","binary_sha256","spec","spec_sha256","launch_mode","launch_contract","launch_contract_sha256"}, "native runtime fields")
    require(runtime["launch_mode"]==spec.get("launch_mode")==anchor.get("launch_mode")=="trusted-native-runtime" and spec.get("version")==2 and anchor.get("version") in (4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59), "native launch mode")
    for key in ("binary","spec","launch_contract"):
        path=Path(runtime[key])
        require(path.resolve(strict=True)==path and digest(artifact_read(path,executable=True) if key=="binary" else control_read(path,1_048_576))==runtime[key+"_sha256"], "native input drift")
    require(runtime["launch_contract"]==spec.get("launch_contract") and runtime["launch_contract_sha256"]==spec.get("launch_contract_sha256")==anchor.get("launch_contract_sha256"), "native launch contract binding")
    contract=json.loads(control_read(runtime["launch_contract"]),object_pairs_hook=reject_duplicate_keys)
    require(set(contract)=={"version","launch_mode","candidate","source_identity","launches","roles"} | ({"network"} if anchor["version"] in (6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59) else set()) | ({"direct_tool_policy"} if anchor["version"] in (20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59) else set()) | ({"diagnostic_policy"} if anchor["version"] in (21,22,23) else set()) and contract["version"]==(2 if anchor["version"] in (6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59) else 1) and contract["launch_mode"]==runtime["launch_mode"] and
            contract["candidate"]==runtime["binary_sha256"]==spec["candidate"]==anchor["candidate"] and contract["source_identity"]==spec["source_identity"]==anchor["source_identity"], "native contract identity")
    if anchor["version"] in (6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59): require(contract["network"]=={'host': 'chatgpt.com', 'port': 443, 'peer': '104.18.32.47'},"native network binding")
    if anchor["version"] in (20,21,22,23,24,25,26,27,28,29,30):
        policy={"version":1,"mode":"direct","model":"gpt-6-astra","profiles":["clock","u2"],"approval":anchor["approval"]}
        require(spec.get("direct_tool_policy")==contract.get("direct_tool_policy")==anchor.get("direct_tool_policy")==policy and spec.get("approval")==anchor["approval"] and spec.get("profile")=="clock" and spec.get("phase")=="clock" and spec.get("start")==(clock_allocation(anchor["version"])["start"] if anchor["version"] in (24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59) else diagnostic_allocation(anchor["version"])["start"] if anchor["version"] in (21,22,23) else "clock-11"), "MCP41 Direct policy binding")
    if anchor["version"] in (21,22,23):require(spec.get("diagnostic_policy")==contract.get("diagnostic_policy")==anchor.get("diagnostic_policy")==DIAGNOSTIC_POLICY,"diagnostic policy binding")
    if anchor["version"] in (24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59):require("diagnostic_policy" not in spec and "diagnostic_policy" not in contract and "diagnostic_policy" not in anchor,"clock diagnostic policy forbidden")
    if anchor["version"] in (31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57):
        u2_anchor_fields(anchor)
        require(spec.get("phase")==u2_allocation(anchor["version"]).get("phase","synthetic") and spec.get("profile")=="u2" and spec.get("start") in u2_allocation(anchor["version"])["starts"] and spec.get("approval")==anchor["approval"] and spec.get("direct_tool_policy")==contract.get("direct_tool_policy")==anchor["direct_tool_policy"],"U2 Direct launch binding")
    descriptor = execution_policy(anchor)
    require(spec.get('execution_template_sha256') == descriptor.TEMPLATE_SHA256 if descriptor else 'execution_template_sha256' not in spec, 'execution-template-spec-binding')
    if anchor['version'] == 59:
        edit_u2.contract(anchor, Budget.fresh_bound)
        require(spec.get('phase') == edit_u2.PHASE and spec.get('profile') == 'u2' and spec.get('start') == edit_u2.START
                and spec.get('approval') == anchor['approval'] and spec.get('direct_tool_policy') == contract.get('direct_tool_policy') == anchor['direct_tool_policy']
                and spec.get('journal_anchor') == str(Path(anchor['run_directory']) / 'anchor.json'), 'edit-launch-binding')
        require(spec['expires_unix_ms'] <= min(anchor['run_deadline_ms'], anchor['total_deadline_ms']) - edit_u2.RESERVE_MS, 'edit-launch-deadline')
        require(spec.get('work') == anchor['work'] and spec.get('input_template_identity') == anchor['input_identity']
                and spec['document_policy']['sources'] == anchor['edit_scope']['files']
                and spec['document_policy']['outputs'] == [anchor['edit_scope']['output']['id']]
                and spec['document_policy']['approval'] == anchor['approval'], 'edit-launch-task-binding')
        require(spec['transport']['slot'] == edit_u2.SLOT and type(spec['transport']['max_requests']) is int
                and 0 < spec['transport']['max_requests'] <= 13, 'edit-launch-transport')
    if anchor['version'] == 58:
        execution_os(require, purpose='codex-v58')
        fresh_u2.contract(anchor, Budget.fresh_bound)
        require(spec.get('phase') == 'synthetic' and spec.get('profile') == 'u2' and spec.get('start') in fresh_u2.STARTS
                and spec.get('approval') == anchor['approval'] and spec.get('direct_tool_policy') == contract.get('direct_tool_policy') == anchor['direct_tool_policy']
                and spec.get('journal_anchor') == str(Path(anchor['run_directory']) / 'anchor.json'), 'v58-launch-binding')
        require(spec['expires_unix_ms'] <= min(anchor['run_deadline_ms'], anchor['total_deadline_ms'] - 1_800_000), 'v58-launch-deadline')
    argv=[runtime["binary"],"--role","runtime","--spec",runtime["spec"]]
    identity={"argv":argv,"cwd":str(Path(spec["root"])/"cwd"),"environment_keys":sorted(env)}
    require(spec.get("launch_identity")==identity==contract["launches"].get(runtime["spec"]), "native argv/environment/cwd drift")
    require(set(contract["roles"])=={"worker","verifier","proxy"}, "native role set")
    for role in contract["roles"].values():
        require(set(role)=={"path","sha256"} and digest(artifact_read(role["path"],limit=1_048_576))==role["sha256"], "native isolated role profile drift")
    require(spec["journal_anchor_sha256"]==anchor_sha256, "native epoch digest")
    return argv,identity,contract


class LiveSession:
    def __init__(self, spec, budget, run, fd_controller=None):
        self.fd_controller = fd_controller
        self.spec, self.budget, self.run = spec, budget, Path(run)
        self.phase, self.start = spec["phase"], spec["start"]
        self.client, self.documents, self.admission, self.acceptance = None, None, None, None
        self.turn_finished, self.last_turn, self.messages = False, None, []
        self.checkpoint_number = 0
        self.runtime_spec = json.loads(control_read(Path(spec["runtime"]["spec"])))
        self.deadline_active_ms = self.runtime_spec["expires_unix_ms"]
        self.owner_text = control_read(Path(spec["owner_input"]), 65_536).decode("utf-8")
        require(digest(self.owner_text.encode()) == spec["owner_input_sha256"], "Owner input drift")
        if budget.anchor["version"] == 59:
            edit_u2.anchor_fields(budget.anchor)
            require(spec["phase"] == edit_u2.PHASE and spec["start"] == edit_u2.START and not spec.get("resume_checkpoint"), "edit-phase-or-resume")
        else:
            require(spec["phase"] in PHASE_CAPS and (spec["start"] in (spec["phase"] + "-01", spec["phase"] + "-02") or (budget.anchor["version"] in (6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30) and spec["phase"]=="clock" and spec["start"]==(clock_allocation(budget.anchor["version"])["start"] if budget.anchor["version"] in (24,25,26,27,28,29,30) else diagnostic_allocation(budget.anchor["version"])["start"] if budget.anchor["version"] in (21,22,23) else "clock-11" if budget.anchor["version"]==20 else "clock-10" if budget.anchor["version"] in (18,19) else "clock-09" if budget.anchor["version"]==17 else "clock-08" if budget.anchor["version"]==16 else "clock-07" if budget.anchor["version"] in (14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30) else "clock-06" if budget.anchor["version"] in (9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30) else "clock-05" if budget.anchor["version"]==8 else "clock-04" if budget.anchor["version"]==7 else "clock-03"))), "phase/start allocation")

    def deadline(self):
        state = self.budget.read()
        remaining = min(state["remaining_ms"] - self.budget.execution_reserve_ms(), self.deadline_active_ms - state["active_ms"])
        require(remaining > 20_000 and not state["paused_at"] and not state["stopped"], "phase/total deadline")
        return time.monotonic() + remaining / 1000

    def launch(self):
        require(self.budget.anchor["version"] not in (58, 59), "fresh-kind-requires-dedicated-session")
        runtime = self.spec["runtime"]
        require(self.fd_controller is not None and self.runtime_spec.get("transport") == self.fd_controller.runtime_transport(), "prepared FD controller binding required")
        env=closed_environment({"TMPDIR":str(Path(self.runtime_spec["root"])/"tmp")})
        argv,identity,self.launch_contract=validate_native_launch(runtime,self.runtime_spec,self.budget.anchor,self.budget.anchor_sha256,env)
        self.execution_binding={"launch_mode":runtime["launch_mode"],"launch_contract_sha256":runtime["launch_contract_sha256"],"epoch_sha256":self.budget.anchor_sha256}
        if self.budget.anchor["version"] in (20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57):
            self.execution_binding.update(approval=self.budget.anchor["approval"],direct_tool_policy=self.budget.anchor["direct_tool_policy"])
        if self.budget.anchor["version"] in (21,22,23):self.execution_binding["diagnostic_policy"]=DIAGNOSTIC_POLICY
        require(runtime["binary_sha256"] == self.budget.anchor["candidate"] and self.runtime_spec["candidate"] == runtime["binary_sha256"] and
                self.runtime_spec["start"] == self.start and self.runtime_spec["phase"] == self.phase and
                self.runtime_spec["journal_anchor_sha256"] == self.budget.anchor_sha256, "runtime budget binding")
        if self.phase != "clock":
            if self.budget.anchor["version"] in (41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57):
                replacement=u2_allocation(self.budget.anchor["version"])["replacement_work"]
                require({k:self.spec["identity"][k] for k in ("home","work")} == replacement, "new H04 Work identity required")
            expected_role={"path":self.spec["documents"]["profile_template"],"sha256":self.spec["documents"]["profile_template_sha256"]}
            require(all(self.launch_contract["roles"][role]==expected_role for role in ("worker","verifier")),"document role contract drift")
            self.documents = DocumentController(self.spec["documents"], self.run, self.budget, self.phase, self.start, self.deadline())
            require(self.documents.scope_sha256 == self.spec["identity"]["scope_identity"], "approved scope drift")
            self.admission = Admission(self.spec["identity"], self.runtime_spec["source_identity"], self.runtime_spec["candidate"],
                self.runtime_spec["input_template_identity"], self.runtime_spec["dynamic_tools"], self.budget, self.phase, self.start)
        if self.spec.get("resume_checkpoint"):
            cp_raw = control_read(self.spec["resume_checkpoint"])
            require(digest(cp_raw) == self.spec["resume_checkpoint_sha256"], "resume checkpoint replacement")
            cp = json.loads(cp_raw, object_pairs_hook=reject_duplicate_keys)
            state = self.budget.resume_check(cp, self.budget.anchor["input_identity"])
            tail = state["events"][cp["journal_seq"] + 1:]
            require(len(tail) == 1 and tail[0]["kind"] == "process-ended" and tail[0]["start"] == cp["start"] and
                    tail[0]["subject"].get("process_group_absent") is True, "resume unresolved effect or process tail")
            require(self.start == self.phase + "-02" and cp["start"] == self.phase + "-01" and self.documents is not None and
                    cp["documents"] == self.documents.files and cp["owner_input_sha256"] == self.spec["owner_input_sha256"] and
                    cp["source_digests"] == self.documents.spec["source_digests"], "resume document/input drift")
            try:
                os.killpg(cp["process_group"], 0)
            except ProcessLookupError:
                pass
            else:
                raise HostRefusal("prior runtime process group present")
            self.documents.read_ids = set(cp["read_ids"])
            self.documents.written_ids = set(cp["written_ids"])
            self.documents.verifiers = cp["verifiers"]
            self.documents.last_failure = cp["last_failure"]
            self.documents.correction_open = cp["correction_open"]
            self.recovery_context = cp
        else:
            require(self.start.endswith("-01") or self.phase == "clock", "second U2 start requires exact pre-seal resume")
        root = Path(self.runtime_spec["root"])
        require(root.is_absolute() and root.resolve(strict=True)==root,"runtime root drift")
        for name in ("home","cwd","config","tmp"):
            directory=root/name
            require(directory.is_dir() and not directory.is_symlink() and directory.resolve(strict=True)==directory,"runtime directory unavailable")
        require(not list((root/"config").iterdir()),"runtime fixture config must remain empty")
        self.auth_metadata_before=protected_auth_metadata(self.runtime_spec["auth_home"])
        durable_private(self.run/"protected-metadata-before.json",self.auth_metadata_before)
        start_record = self.budget.reserve("start", {"runtime_spec_sha256":runtime["spec_sha256"],"execution_binding":self.execution_binding,
            "launch_identity":identity,"identity_sha256":digest(wire_bytes(self.spec.get("identity"))),"owner_input_sha256":self.spec["owner_input_sha256"]},self.phase,self.start)
        self.client=LiveClient(argv,Path(identity["cwd"]),self.run,min(self.deadline(),time.monotonic()+30),env,
            on_spawn=lambda process:self.fd_controller.register_runtime(runtime,process))
        self.client.diagnostic_policy=self.runtime_spec.get("diagnostic_policy")
        bind_native_notifications(self.client, runtime, self.runtime_spec, self.budget.anchor)
        self.client.on_event = self.on_event
        self.client.callback = self.callback if self.admission else None
        init = self.client.request("initialize", {"clientInfo": {"name": "colvia_u2_qualification", "version": "0.1"},
                                                 "capabilities": {"experimentalApi": True}})
        self.check_auth_metadata()
        self.client.deadline=self.deadline()
        self.client.send({"method": "initialized", "params": {}})
        self.client.validate_account_bootstrap()
        params = {"ephemeral": True}
        if self.runtime_spec["dynamic_tools"]:
            params["dynamicTools"] = self.runtime_spec["dynamic_tools"]
        request_id = self.client.sequence + 1
        result = self.client.request("thread/start", params)
        require(result["thread"]["ephemeral"] is True and result["model"] == "gpt-6-astra" and
                result["modelProvider"] == "openai" and result["reasoningEffort"] == "xhigh" and result["approvalPolicy"] == "never", "native thread admission")
        self.thread = result["thread"]["id"]
        self.budget.reserve("thread-bound", {"request": request_id, "thread": self.thread}, self.phase, self.start)
        self.client.drain()
        durable_private(self.run / "admission.json", {"start_seq": start_record["seq"], "thread": self.thread,
            "initialize_keys": sorted(init), "runtime_spec_sha256": runtime["spec_sha256"], "phase": self.phase})
        return self.thread

    def on_event(self, method, params):
        if "threadId" in params:
            require(getattr(self, "thread", None) in (None, params["threadId"]), "notification foreign thread")
        if method == "turn/started":
            self.last_turn = params["turn"]["id"]
            if self.admission:
                self.admission.bind_turn(self.last_turn)
        if method == "turn/completed":
            turn = params["turn"]
            require(turn["id"] == self.last_turn and turn["status"] == "completed" and turn.get("error") is None, "turn failed/interrupted")
            self.turn_finished = True
            if self.admission:
                self.admission.completed = True
        if method == "item/completed":
            item = params.get("item", {})
            if item.get("type") == "agentMessage":
                text = item.get("text", "")
                allowed = self.spec.get("documents", {}).get("allowed_identifiers", [])
                safe_text(text, allowed)
                if self.phase=="clock":
                    require(len(self.messages)<8 and len(text.encode())<=65536,"bounded clock answer")
                    durable_private(self.run/f"clock-message-{len(self.messages)+1:02d}.json",{"text":text,"bytes":len(text.encode()),"sha256":digest(text.encode()),"scope":"fixed synthetic clock response"})
                self.messages.append({"bytes": len(text.encode()), "sha256": digest(text.encode())})

    def callback(self, params):
        tool, args = self.admission.callback(params)
        if tool == "u2_accept":
            require(self.acceptance is not None, "acceptance not prepared by trusted Driver")
            result = self.acceptance.apply(args, self.admission, self.documents.result_identity(), self.documents.active is None)
        else:
            self.documents.deadline = min(self.deadline(), time.monotonic() + 300)
            result = self.documents.dispatch(tool, args)
        text = wire_bytes(result).decode()
        require(len(text.encode()) <= 64_000, "callback output limit")
        return {"contentItems": [{"type": "inputText", "text": text}], "success": True}

    def turn(self, inputs):
        require(len(inputs) <= 8 and all(item.get("type") == "text" and not item.get("text_elements") and 0 < len(item["text"].encode()) <= 65_536 for item in inputs), "turn input limit")
        self.turn_finished, self.last_turn = False, None
        self.client.deadline = min(self.deadline(), time.monotonic() + 900)
        prepared = self.client.request("turn/prepare", {"threadId": self.thread, "input": inputs})
        manifest = prepared["manifest"]
        require(manifest["snapshot"]["context"].get("execution_binding")==self.execution_binding,"prepared native execution binding")
        self.check_auth_metadata()
        if self.admission:
            durable_private(self.run / f"prepared-tool-envelope-{self.checkpoint_number+1:03d}.json", manifest["toolEnvelope"])
            self.admission.bind(self.thread, prepared, inputs)
        else:
            require(manifest["sourceIdentity"] == self.runtime_spec["source_identity"] and manifest["buildIdentity"] == "sha256:" + self.runtime_spec["candidate"] and
                    [entry["name"] for entry in manifest["toolEnvelope"]["entries"]] == ["curr_time"] and
                    manifest["snapshot"]["initial_input"] == inputs, "clock prepared binding")
        self.budget.reserve("input", {"plan": manifest["planId"], "input_sha256": digest(wire_bytes(inputs)),
                                     "manifest_sha256": digest(wire_bytes(manifest))}, self.phase, self.start)
        response = self.client.request("turn/startPrepared", {"threadId": self.thread, "handle": prepared["handle"], "manifest": manifest, "input": inputs})
        turn_id = response["turn"]["id"]
        require(self.last_turn in (None, turn_id), "turn response identity")
        self.last_turn = turn_id
        if self.admission:
            self.admission.bind_turn(turn_id)
        while not self.turn_finished:
            value = self.client.receive()
            require("method" in value, "unexpected turn response")
            self.client.event(value)
        self.client.drain()
        # A read barrier consumes prior queued warnings without adding a model turn.
        self.client.request("thread/read", {"threadId": self.thread, "includeTurns": False})
        self.client.drain()
        self.client.fixture_flow.verify_complete()
        self.checkpoint()
        return turn_id

    def checkpoint(self):
        state = self.budget.read()
        self.checkpoint_number += 1
        value = {"approval": self.budget.anchor["approval"], "work": self.budget.anchor["work"],
            "input_identity": self.budget.anchor["input_identity"], "owner_input_sha256": self.spec["owner_input_sha256"],
            "journal_seq": len(state["rows"]) - 1, "journal_sha256": state["prev"], "counts": state["counts"],
            "thread": getattr(self, "thread", None), "turn": self.last_turn, "phase": self.phase, "start": self.start,
            "sealed": bool(self.documents and self.documents.sealed), "pending": bool(self.acceptance and self.acceptance.used),
            "documents": self.documents.files if self.documents else {}, "progress": self.documents.progress() if self.documents else {},
            "active_ms": state["active_ms"], "remaining_ms": state["remaining_ms"], "messages": self.messages,
            "process_group": self.client.process.pid if self.client else None,
            "source_digests": self.documents.spec["source_digests"] if self.documents else {},
            "read_ids": sorted(self.documents.read_ids) if self.documents else [],
            "written_ids": sorted(self.documents.written_ids) if self.documents else [],
            "verifiers": self.documents.verifiers if self.documents else {},
            "last_failure": self.documents.last_failure if self.documents else None,
            "correction_open": self.documents.correction_open if self.documents else False}
        durable_private(self.run / f"checkpoint-{self.checkpoint_number:03d}.json", value)
        return value

    def iterate(self):
        require(self.budget.anchor["version"] not in (58, 59), "fresh-kind-requires-dedicated-iteration")
        while True:
            state = self.budget.read()
            version = self.budget.anchor["version"]
            require(type(version) is int and version >= 1, "invalid turn allocation version")
            if version >= 31:
                allocation = u2_allocation(version)
                require(self.phase == allocation.get("phase", "synthetic"), "turn allocation phase")
                # U2 events are epoch-local; counts include historical epochs.
                used = sum(e["kind"] == "turn" for e in state["events"])
                left = allocation["turns"] - used
            else:
                used = sum(e["kind"] == "turn" and e["phase"] == self.phase for e in state["events"])
                left = PHASE_CAPS[self.phase][2] - used
            require(left > 1, "no turn remains for sealed acceptance")
            before = self.documents.progress()
            inputs = trusted_turn_input(self.owner_text, self.admission.identity, before, left)
            if getattr(self, "recovery_context", None) is not None:
                cp = self.recovery_context
                recovery = {"original_input_sha256": cp["owner_input_sha256"], "last_verifiers": cp["verifiers"],
                            "pending": cp["pending"], "counts": self.budget.read()["counts"]}
                inputs = trusted_turn_input(self.owner_text, self.admission.identity, before, left, recovery=recovery)
                for pack in self.documents.read_packs:
                    rows = []
                    for key in pack:
                        entry, raw = document_record(self.documents.files[key])
                        row = document_item(key, entry, raw)
                        row["origin"] = {"kind": "approved-document", "source_sha256": self.documents.spec["source_digests"][key],
                                         "approval": self.budget.anchor["approval"]}
                        rows.append(row)
                    inputs.append({"type": "text", "text": wire_bytes({"recovery_documents": rows}).decode(), "text_elements": []})
                require(len(inputs) <= 8 and all(len(item["text"].encode()) <= 65_536 for item in inputs), "complete recovery context cannot fit")
                del self.recovery_context
            self.turn(inputs)
            after = self.documents.progress()
            if self.spec.get("planned_stop_after_turns") is not None:
                require(self.phase == "synthetic" and self.spec["planned_stop_after_turns"] == 1 and self.start.endswith("-01"), "planned stop scope")
                return None
            require(before != after, "no work progress or new evidence")
            if set(self.documents.verifiers) == {"DOC-LINKS", "DOC-GFM", "DOC-CLAIMS"} and all(v["pass"] for v in self.documents.verifiers.values()) and set(self.documents.spec["outputs"]) <= self.documents.written_ids:
                result = self.documents.seal()
                require(self.admission.completed, "seal during active turn")
                self.admission.identity["result_identity"] = result
                self.admission.identity_hash = digest(wire_bytes(self.admission.identity))
                self.admission.sealed = True
                self.checkpoint()
                return result

    def check_auth_metadata(self):
        after=protected_auth_metadata(self.runtime_spec["auth_home"])
        self.auth_metadata_checks=getattr(self,"auth_metadata_checks",0)+1
        durable_private(self.run/f"protected-metadata-after-{self.auth_metadata_checks:03d}.json",after)
        require(after==self.auth_metadata_before,"protected native auth metadata changed")

    def close(self):
        if self.fd_controller is not None:
            self.fd_controller.revoke(self.start)
        if self.admission:
            self.admission.stop()
        if self.documents and self.documents.active is not None:
            end_process(self.documents.active)
        if self.client:
            self.client.close()
            self.budget.reserve("process-ended", {"start": self.start, **self.client.cleanup}, self.phase, self.start, allow_closeout=True)
        if hasattr(self,"auth_metadata_before"):
            self.check_auth_metadata()

__all__ = ['DISABLED_FEATURES', 'EXPECTED_MCP', 'ALLOWED_PREFLIGHT', 'StdioClient', 'normalized_profile', 'policy_observation', 'preflight', 'PHASE_CAPS', 'JOURNAL_KINDS', 'DIAGNOSTIC_POLICY', 'DIAGNOSTIC_ALLOCATIONS', 'DIAGNOSTIC_PRIOR', 'DIAGNOSTIC_PARENT', 'diagnostic_allocation', 'diagnostic_anchor_fields', 'diagnostic_budget_state', 'CLOCK_POLICY', 'CLOCK_ALLOCATIONS', 'clock_allocation', 'clock_anchor_fields', 'clock_budget_state', 'U2_ALLOCATION', 'U2_POLICY', 'U2_ALLOCATIONS', 'u2_allocation', 'u2_policy', 'u2_anchor_fields', 'u2_budget_state', 'DiagnosticNumber', 'diagnostic_token_tree', 'diagnostic_token_summary', 'Budget', 'LIVE_METHODS', 'LIVE_NOTIFICATIONS', 'FIXTURE_NOTICE_POLICY', 'FIXTURE_NOTICE_BUILD_SHA256', 'prepared_fixture_notice_message', 'FixtureNotificationFlow', 'NativeNotificationFlow', 'bind_native_notifications', 'LiveClient', 'native_document_schema', 'Admission', 'phase_transport_limit', 'idle_deadline_wall_ms', 'frozen_network_peer', 'PreparedFdController', 'protected_auth_metadata', 'validate_native_launch', 'LiveSession']
