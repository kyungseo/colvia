"""U2 compatibility entry; effects are common, native transport is adapter-owned."""
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

# Load only this checkout's sibling package, even when a caller uses spec_from_file_location.
# The canonical path separates concurrent source candidates without searching ambient sys.path.
import importlib.util as _import_util
_root = Path(__file__).resolve().parent
_package_name = '_colvia_u2_' + hashlib.sha256(str(_root).encode()).hexdigest()[:16]
if _package_name not in sys.modules:
    _spec = _import_util.spec_from_file_location(_package_name, _root / '__init__.py', submodule_search_locations=[str(_root)])
    _package = _import_util.module_from_spec(_spec)
    sys.modules[_package_name] = _package
    _spec.loader.exec_module(_package)
import importlib as _importlib
contracts = _importlib.import_module(_package_name + '.contracts')
codex = _importlib.import_module(_package_name + '.adapters.codex')
claude_code = _importlib.import_module(_package_name + '.adapters.claude_code')
fresh_codex = _importlib.import_module(_package_name + ".adapters.fresh_codex")
edit_codex = _importlib.import_module(_package_name + ".adapters.edit_codex")
FreshCodexSession = fresh_codex.FreshCodexSession
ClaudeCodeAdapter = claude_code.ClaudeCodeAdapter
for _module in (contracts, codex):
    for _name in _module.__all__:
        globals()[_name] = getattr(_module, _name)


def load_host_spec(path):
    raw = control_read(path, 2_097_152)
    spec = json.loads(raw, object_pairs_hook=reject_duplicate_keys)
    require(spec.get("version") == 1, "host spec version")
    require(Path(spec["run"]).resolve(strict=False) == Path(spec["run"]), "run path alias")
    return spec


def edit_only(action, *, snapshot_reader, baseline_reader, cfg=None, execution=None, destination=None,
              spec_path=None, fd_controller=None):
    """Trusted caller entry. Data never selects a reader, plugin, or authority writer."""
    require(callable(snapshot_reader) and callable(baseline_reader), 'edit-trusted-readers-required')
    if action == 'prepare':
        require(spec_path is None and fd_controller is None, 'edit-prepare-launch-forbidden')
        return edit_codex.prepare_execution(cfg, execution, destination,
            snapshot_reader=snapshot_reader, baseline_reader=baseline_reader)
    require(action == 'execute' and cfg is None and execution is None and destination is None, 'edit-action-or-resume-forbidden')
    return edit_codex.run_edit(load_host_spec(spec_path), fd_controller=fd_controller,
        snapshot_reader=snapshot_reader, baseline_reader=baseline_reader)


def run_live_command(command, spec_path, fd_controller=None):
    spec = load_host_spec(spec_path)
    require(spec["command"] == command and command in ("live-smoke", "qualify", "iterate", "actual"), "command/spec binding")
    budget = Budget(spec["budget_directory"], spec["budget_anchor_sha256"])
    run = Path(spec["run"])
    session, result = None, {"command": command, "status": "unavailable", "spec_sha256": digest(control_read(spec_path))}
    run_created = False
    lock = ControllerLock(budget.directory / "controller.lock")
    try:
        run.mkdir(mode=0o700, exist_ok=False)
        run_created = True
        session = LiveSession(spec, budget, run, fd_controller=fd_controller)
        session.launch()
        if command == "live-smoke":
            require(spec["phase"] == "clock", "clock phase")
            session.turn([{"type": "text", "text": session.owner_text, "text_elements": []}])
            events = budget.read()["events"]
            dispatches = [e for e in events if e["kind"] == "dispatch" and e["start"] == session.start]
            require(len(dispatches) == 1, "clock did not dispatch exactly once")
            result.update(status="clock-completed", model_turns=1)
            if budget.anchor["version"] in (24,25,26,27,28,29,30):budget.reserve("stop", {"reason":"clock-completed"}, allow_closeout=True)
        else:
            require(spec["phase"] == ("h10" if command == "actual" else "synthetic"), "U2 phase")
            identity = session.iterate()
            if identity is None:
                result.update(status="editing-stopped-for-resume")
                return 0
            require(session.documents.active is None and session.admission.completed, "editing worker not quiescent")
            require(fd_controller is not None, "idle proxy lifetime unavailable")
            fd_controller.wait_for_release(session.start)
            observations = [json.loads(line, object_pairs_hook=reject_duplicate_keys) for line in
                control_read(Path(session.runtime_spec["root"])/"observations.jsonl").splitlines()]
            lifetime = [row for row in observations if row.get("kind")=="auth-lifetime"]
            require(len(lifetime)==1, "idle native auth lifetime unavailable")
            now_ms=time.time_ns()//1_000_000
            proxy_expiry_ms=now_ms+int((fd_controller.deadline-time.monotonic())*1000)
            idle_until=idle_deadline_wall_ms(now_ms,session.runtime_spec["expires_unix_ms"],proxy_expiry_ms,lifetime[0].get("expires_wall_ms"))
            result.update(status="sealed-awaiting-exact-candidate-decision", result_identity=identity, idle_deadline_wall_ms=idle_until)
            durable_private(run / "sealed.json", result)
            # The same process/thread remains idle; a separate trusted CLI request
            # can supply the exact Owner-approved packet after candidate commit.
            paused = budget.reserve("pause", {"reason": "owner-only", "sealed_result": identity}, session.phase, session.start)
            request_path = run / "accept-request.json"
            stop_path = run / "owner-stop.json"
            print(json.dumps(result), flush=True)
            began = time.monotonic()
            while not request_path.exists():
                remaining_idle=(idle_until-time.time_ns()//1_000_000)/1000
                require(remaining_idle>0 and not fd_controller.failed,"same-thread idle expired or proxy unavailable")
                session.client.deadline = time.monotonic() + min(2,remaining_idle)
                session.client.drain(0.05)
                if stop_path.exists():
                    raise HostRefusal("Owner stopped execution")
                time.sleep(0.2)
            require(time.time_ns()//1_000_000 < idle_until and not fd_controller.failed, "same-thread idle expired")
            owner_wait_seconds = time.monotonic() - began
            request = json.loads(control_read(request_path, 262144), object_pairs_hook=reject_duplicate_keys)
            require(set(request) == {"command", "spec_sha256", "packet_path", "packet_sha256", "owner_decision_path", "owner_decision_sha256", "handle"} and
                    request["command"] == "actual-accept" and request["spec_sha256"] == result["spec_sha256"], "accept command drift")
            decision_bytes = control_read(request["owner_decision_path"])
            require(digest(decision_bytes) == request["owner_decision_sha256"], "Owner decision drift")
            decision = json.loads(decision_bytes)
            require(decision["result_identity"] == identity and decision["packet_sha256"] == request["packet_sha256"] and decision["action"] == "accept" and decision["owner_message_id"], "exact candidate/ticket approval missing")
            budget.reserve("resume", {"pause_seq": paused["seq"]}, session.phase, session.start, allow_closeout=True)
            session.client.deadline = session.deadline()
            session.documents.check_files()
            require(session.documents.active is None and session.admission.thread == session.thread, "same idle editing thread lost")
            core = InstalledCore(spec["core"], run, session.deadline())
            session.acceptance = Acceptance(session.admission.identity, control_read(request["packet_path"]), request["packet_sha256"],
                identity, request["handle"], core, budget)
            session.turn(trusted_turn_input(session.owner_text, session.admission.identity, session.documents.progress(), 1, request["handle"]))
            require(session.acceptance.used, "model did not request sealed acceptance")
            result.update(status="accepted-awaiting-owner-content-review", owner_wait_seconds=round(owner_wait_seconds, 3))
    except Exception as error:
        result.update(status="refused", failure_type=type(error).__name__, failure=str(error) if isinstance(error, HostRefusal) else "execution unavailable")
        try:
            budget.reserve("stop", {"reason": result["failure"]}, allow_closeout=True)
        except Exception:
            result["budget_stop_unavailable"] = True
    finally:
        try:
            if session:
                try:
                    session.close()
                    result["cleanup"] = session.client.cleanup if session.client else {"runtime_started": False}
                except Exception:
                    result["cleanup_unavailable"] = True
                    result["status"] = "refused"
            if run_created:
                durable_private(run / "result.json", result)
        finally:
            lock.close()
    print(json.dumps(result, ensure_ascii=False), flush=True)
    return 0 if result["status"] in ("clock-completed", "accepted-awaiting-owner-content-review") else 2


def recovery_command(spec_path):
    spec = load_host_spec(spec_path)
    require(spec["command"] == "recover", "recovery command binding")
    packet_bytes, decision_bytes = control_read(spec["packet"]), control_read(spec["owner_decision"])
    require(digest(packet_bytes) == spec["packet_sha256"] and digest(decision_bytes) == spec["owner_decision_sha256"], "recovery approval input drift")
    packet = json.loads(packet_bytes, object_pairs_hook=reject_duplicate_keys)
    decision = json.loads(decision_bytes, object_pairs_hook=reject_duplicate_keys)
    require(core_bytes(packet) == packet_bytes, "recovery packet canonical bytes")
    budget = Budget(spec["budget_directory"], spec["budget_anchor_sha256"])
    lock = ControllerLock(budget.directory / "controller.lock")
    run = Path(spec["run"])
    result = {"status": "refused", "replayed": []}
    run_created = False
    try:
        gate = RecoveryGate(packet, spec["packet_sha256"], decision, budget)
        require(type(spec["seconds"]) is int and 0 < spec["seconds"] <= 1500, "recovery time bound")
        run.mkdir(mode=0o700, exist_ok=False)
        run_created = True
        state = budget.read()
        require(not state["stopped"], "stopped budget requires new Owner disposition")
        if state["paused_at"] is not None:
            pause = next(e for e in reversed(state["events"]) if e["kind"] == "pause")
            budget.reserve("resume", {"pause_seq": pause["seq"]}, allow_closeout=True)
        deadline = time.monotonic() + min(spec["seconds"], (budget.read()["remaining_ms"] - 1_200_000) / 1000)
        for name in sorted(packet["cases"]):
            case = packet["cases"][name]
            # A live PID is never killed by recovery, and absence is rechecked now.
            require(type(case["process_group"]) is int and case["process_group"] > 1, "recovery process identity")
            try:
                os.killpg(case["process_group"], 0)
            except ProcessLookupError:
                pass
            else:
                raise HostRefusal("original process group still present")
            case_run = run / name
            case_run.mkdir(mode=0o700)
            observation = {"files": fixed_file_observation(case["snapshot_paths"])}
            core = InstalledCore(case["core"], case_run, deadline)
            after = gate.replay(name, core, observation)
            require(after.get("current") == case["expected_current"], "recovery result/current mismatch")
            if name == "S5":
                require(fixed_file_observation(case["snapshot_paths"]) == observation["files"], "historical replay changed publication")
            durable_private(case_run / "result.json", {"case": name, "ticket_sha256": case["ticket_sha256"],
                "result_sha256": digest(core_bytes(after)), "unwrapped_installed_cli": True})
            result["replayed"].append(name)
        result["status"] = "exact-recovery-completed"
    except Exception as error:
        result.update(failure_type=type(error).__name__, failure=str(error) if isinstance(error, HostRefusal) else "recovery unavailable")
    finally:
        try:
            if run_created:
                durable_private(run / "result.json", result)
        finally:
            lock.close()
    print(json.dumps(result), flush=True)
    return 0 if result["status"] == "exact-recovery-completed" else 2


def submit_acceptance(spec_path):
    envelope = json.loads(control_read(spec_path), object_pairs_hook=reject_duplicate_keys)
    require(set(envelope) == {"version", "host_spec", "host_spec_sha256", "request"} and envelope["version"] == 1, "acceptance envelope")
    raw = control_read(envelope["host_spec"])
    require(digest(raw) == envelope["host_spec_sha256"], "original host spec drift")
    host_spec = json.loads(raw, object_pairs_hook=reject_duplicate_keys)
    require(host_spec["phase"] in ("synthetic", "h10"), "acceptance phase")
    request = envelope["request"]
    require(set(request) == {"command", "spec_sha256", "packet_path", "packet_sha256", "owner_decision_path", "owner_decision_sha256", "handle"} and
            request["command"] == "actual-accept" and request["spec_sha256"] == envelope["host_spec_sha256"], "acceptance request identity")
    decision = control_read(request["owner_decision_path"])
    require(digest(decision) == request["owner_decision_sha256"] and digest(control_read(request["packet_path"])) == request["packet_sha256"], "acceptance packet changed")
    run = Path(host_spec["run"])
    sealed = json.loads(control_read(run / "sealed.json"))
    owner = json.loads(decision, object_pairs_hook=reject_duplicate_keys)
    require(owner["result_identity"] == sealed["result_identity"] and owner["packet_sha256"] == request["packet_sha256"] and
            owner["action"] == "accept" and owner["owner_message_id"], "sealed Owner decision mismatch")
    require(not (run / "result.json").exists(), "original controller already ended")
    publish_acceptance_request(run, request)
    print(json.dumps({"status": "delivered-to-original-idle-controller", "result_identity": sealed["result_identity"]}), flush=True)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["live-smoke", "qualify", "iterate", "actual", "actual-accept", "recover", "clock-recover"])
    parser.add_argument("--spec", required=True, type=Path)
    args = parser.parse_args()
    if args.command == "clock-recover":
        budget = Budget.recover_clock(args.spec)
        print(json.dumps({"status": "clock-recovered", "anchor_sha256": budget.anchor_sha256, "counts": budget.read()["counts"]}), flush=True)
        return 0
    if args.command == "actual-accept":
        return submit_acceptance(args.spec)
    if args.command == "recover":
        return recovery_command(args.spec)
    return run_live_command(args.command, args.spec)

if __name__ == "__main__":
    raise SystemExit(main())
