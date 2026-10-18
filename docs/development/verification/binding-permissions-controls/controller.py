"""Bounded native verification controller; authoring draft, never an approval token."""
import fcntl
import json
import os
from pathlib import Path
import signal
import stat
import subprocess
import sys
import time
from types import MappingProxyType
from common import canonical, config, digest, exclusive_json, file_map, read_json, regular, require, verify_old, python_command, require_isolated, unlinked_path

# Single entry-mode contract, imported before any product/test module.
ENTRY_MODE_SLOTS = MappingProxyType({
    "collect": ("p1-controls", "p1", "p1-correction", "p2", "p2-correction", "p3", "p3-correction", "final"),
    "focused": ("p1-controls", "p1", "p2", "p3", "correction"),
    "complete-normal": ("final",), "complete-parent-O": ("final",), "artifact": ("final",),
})
ENTRY_RUN_NAMES = frozenset(mode + "-" + slot for mode, slots in ENTRY_MODE_SLOTS.items() for slot in slots)
DELEGATION_MODE_SLOTS = MappingProxyType({"acquire": ("base",), "canary": ("base",), "collect": ("final",), "smoke": ("base",), "focused": ("core", "transition"), "complete-normal": ("final",), "complete-parent-O": ("final",), "artifact": ("final",)})
DELEGATION_RUN_NAMES = frozenset(mode+"-"+slot for mode,slots in DELEGATION_MODE_SLOTS.items() for slot in slots)
COLLECTIONS = frozenset(("base", *ENTRY_MODE_SLOTS["collect"]))
LIMITS = {"acquire": 300, "canary": 300, "collect": 300, "smoke": 3600,
          "focused": 1500, "complete-normal": 5400, "complete-parent-O": 5400, "artifact": 1800}


def allowed(mode, slot, phase):
    require(mode in LIMITS and phase in {"base", "entry", "delegation"}, "unlisted mode/phase")
    if phase == "delegation":
        require(mode in DELEGATION_MODE_SLOTS and slot in DELEGATION_MODE_SLOTS[mode], "delegation mode/slot")
        return
    if phase == "base":
        require(mode in {"acquire", "canary", "collect", "smoke"} and slot == "base", "base-only operation")
    else:
        require(mode in ENTRY_MODE_SLOTS and slot in ENTRY_MODE_SLOTS[mode], "entry mode/slot")


def require_new_collection(c, prior):
    require(prior.get("phase") in {"base", "entry", "delegation"}, "phase-less collection evidence cannot be reused")
    require((prior["source_digest"], prior["controls"], prior["phase"]) !=
            (c["source_digest"], c["controls"], c["phase"]), "collection source/controls/phase already attempted")


def main():
    started = time.monotonic()
    require_isolated()
    require(len(sys.argv) == 5, "usage: controller.py INPUT SHA256 MODE SLOT")
    input_path = Path(sys.argv[1]).absolute()
    c, p = config(input_path, sys.argv[2])
    mode, slot = sys.argv[3:]
    allowed(mode, slot, c["phase"])
    require(digest(Path(sys.executable).resolve().read_bytes()) == c["runtime"]["sha256"], "controller interpreter mismatch")
    if (p["controls"] / "campaign.json").exists():
        import campaign
        return campaign.dispatch(c, p, input_path, sys.argv[2], mode, slot, started)
    if mode == "acquire":
        require(not p["root"].exists(), "execution root already exists; inspect, do not reuse")
        p["root"].mkdir(mode=0o700)
        p["exec"].mkdir(mode=0o700)
        (p["root"] / "denied-sentinel").write_text("synthetic-not-a-credential\n")
    require(p["root"].is_dir() and p["exec"].is_dir(), "acquisition layout unavailable")
    with (p["root"] / "controller.lock").open("a+b") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        raise SystemExit(0 if run(c, p, input_path, sys.argv[2], mode, slot, started) else 2)


def completed(c, p, mode, slot, *, same_source=False):
    anchor = unlinked_path(p["exec"] / "runs" / (mode + "-" + slot))
    result = read_json(unlinked_path(anchor / "result.json"))
    inputs = read_json(unlinked_path(anchor / "inputs.json"))
    require(result["execution_pass"] is True and result["mode"] == mode and result["slot"] == slot, "prior execution incomplete")
    require(result["inputs_sha256"] == digest(regular(anchor / "inputs.json")), "prior parent evidence mismatch")
    require(inputs["mode"] == mode and inputs["slot"] == slot, "prior mode mismatch")
    for key in ("controls", "runtime", "git", "git_system_config"):
        require(inputs[key] == c[key], "prior control/tool/config identity drift")
    if same_source:
        require(inputs["source_digest"] == c["source_digest"], "prior source drift")
    for name, value in result.get("child_evidence", {}).items():
        require(digest(regular(anchor / "work" / name)) == value, "sealed child evidence drift")
    require("child_evidence" in result, "unsealed prior child evidence")
    return inputs


def positive_boundary_controls(c, p, input_path, out):
    # Future canary execution only. Opens do not truncate/write; chmod retains mode.
    # The parent confirms DAC permits the exact operations before the sandbox probe.
    targets = {"SOURCE": p["source"] / "colvia", "CONTROLS": p["controls"] / "common.py",
               "INPUT": input_path, "PARENT_INPUTS": out / "inputs.json",
               "PRIOR_RESULT": p["exec"] / "runs/acquire-base/result.json"}
    if c["schema"] == 4:
        targets.update({"PREDECESSOR": p["predecessor"] / "colvia", "ARTIFACTS": p["artifacts"] / "q/colvia"})
    observations = {}
    for label, target in targets.items():
        target = unlinked_path(target)
        require(target.stat().st_uid == os.geteuid() and target.stat().st_mode & stat.S_IWUSR and os.access(target, os.W_OK), "canary positive-control DAC unavailable")
        before = regular(target)
        mode = stat.S_IMODE(target.stat().st_mode)
        fd = os.open(target, os.O_WRONLY | os.O_NOFOLLOW)  # No O_TRUNC or write.
        os.close(fd)
        require(regular(target) == before and stat.S_IMODE(target.stat().st_mode) == mode, "positive open altered input")
        observations[label] = {"path": str(target), "operation": "open-write-without-write", "sha256": digest(before), "mode": mode}
    old_file = unlinked_path(p["old"] / ".gitignore")
    before = regular(old_file); mode = stat.S_IMODE(old_file.stat().st_mode)
    require(old_file.stat().st_uid == os.geteuid(), "OLD probe not owned by the executing user")
    os.chmod(old_file, mode, follow_symlinks=False)
    require(regular(old_file) == before and stat.S_IMODE(old_file.stat().st_mode) == mode, "positive chmod altered OLD bytes/mode")
    observations["OLD_MODE"] = {"path": str(old_file), "operation": "chmod-same-mode", "sha256": digest(before), "mode": mode}
    for label, target in {"COMMON_GIT": p["common_git"] / "HEAD", "SENTINEL": p["root"] / "denied-sentinel", "SIBLING": p["exec"] / "sibling-sentinel", "CREDENTIAL": p["root"] / "credential-sentinel"}.items():
        target = unlinked_path(target)
        observations[label] = {"path": str(target), "operation": "open-read", "sha256": digest(regular(target)), "mode": stat.S_IMODE(target.stat().st_mode)}
    return {"uid": os.geteuid(), "probes": observations, "limit": "OLD chmod proves a metadata-write refusal, not all data-write operations; mode-bit custody is checked separately"}


def test_ancestor_parameters(p, out):
    # Exact directory entries needed by classify_target, never recursive reads.
    ancestors = (out, *out.parents)
    require(len(ancestors) == 12 and ancestors[1:4] ==
            (p["exec"] / "runs", p["exec"], p["root"]) and ancestors[-1] == Path("/"),
            "unapproved test ancestor layout")
    return {"ANCESTOR_" + str(i): directory for i, directory in enumerate(ancestors)}


def settle_child(child, start, budget, reason, natural, *, observations=None, parent_snapshot=False):
    """Reap and prove exact group absence within the already reserved deadline.

    EPERM is unknown, never absence. A successful bounded parent ps snapshot
    may resolve it after the direct child has exited. This is not a proof that
    a malicious descendant did not escape the admitted process group.
    """
    observations = observations if observations is not None else []
    errors = []
    end = time.monotonic() + 20 if budget is None else start + budget
    def failure(stage, exc):
        nonlocal reason
        errors.append({"stage": stage, "type": type(exc).__name__, "errno": getattr(exc, "errno", None)})
        reason = reason or "cleanup-observation-or-operation-unavailable"
    def group_state():
        child.poll()
        try:
            os.killpg(child.pid, 0)
            return True
        except ProcessLookupError:
            return False if child.returncode is not None else None
        except OSError as exc:
            observations.append({"stage": "group-probe", "type": type(exc).__name__, "errno": exc.errno})
            if not parent_snapshot or exc.errno != 1 or child.returncode is None:
                return None
            try:
                remaining = end - time.monotonic()
                require(remaining > 0, "no time for exact PGID observation")
                seen = subprocess.run(["/bin/ps", "-axo", "pid=,pgid="], stdin=subprocess.DEVNULL,
                    capture_output=True, text=True, timeout=min(1.0,remaining))
                require(seen.returncode == 0 and len(seen.stdout) <= 4*1024*1024, "PGID observation unavailable")
                rows = [line.split() for line in seen.stdout.splitlines() if line.strip()]
                require(rows and all(len(row)==2 and all(x.isdigit() for x in row) for row in rows), "invalid PGID observation")
                members = [int(pid) for pid,pgid in rows if int(pgid)==child.pid]
                observations.append({"stage":"parent-pgid-snapshot", "pgid":child.pid, "members":members})
                return bool(members)
            except (OSError,RuntimeError,subprocess.TimeoutExpired) as error:
                observations.append({"stage":"parent-pgid-snapshot", "error":type(error).__name__})
                return None
    def send(sig):
        try: os.killpg(child.pid, sig)
        except ProcessLookupError: pass
        except OSError as exc: failure("signal-"+str(int(sig)),exc)
    state=group_state()
    probe_until=min(end-5,time.monotonic()+1)
    while state is None and time.monotonic()<probe_until:
        time.sleep(min(.1,max(0,probe_until-time.monotonic())))
        state=group_state()
    if state is not False:
        reason=reason or "surviving-or-unobservable-process-group"
        send(signal.SIGTERM)
        term_until=min(end-5,time.monotonic()+8)
        while state is not False and time.monotonic()<term_until:
            time.sleep(min(.1,max(0,term_until-time.monotonic())))
            state=group_state()
        if state is not False:send(signal.SIGKILL)
    try:child.wait(timeout=max(0,end-time.monotonic()))
    except (subprocess.TimeoutExpired,OSError) as exc:failure("child-wait",exc)
    state=group_state()
    while state is not False and time.monotonic()<end:
        time.sleep(min(.1,max(0,end-time.monotonic())))
        state=group_state()
    absent=state is False and child.returncode is not None
    if not absent:
        errors.append({"stage":"group-probe-unresolved", "type":"UnknownOrPresent", "errno":None})
        reason=reason or "cleanup-incomplete"
    return reason,natural,absent,errors



def check_canary_dac(c, p, input_path):
    # Existing exact targets only. The new parent inputs file is checked again
    # in positive_boundary_controls before any child is launched.
    targets = [p["source"] / "colvia", p["controls"] / "common.py", Path(input_path),
               p["exec"] / "runs/acquire-base/result.json"]
    if c["schema"] == 4:
        targets += [p["predecessor"] / "colvia", p["artifacts"] / "q/colvia"]
    for target in targets:
        info = unlinked_path(target).stat()
        require(info.st_uid == os.geteuid() and info.st_mode & stat.S_IWUSR and os.access(target, os.W_OK), "canary positive-control DAC unavailable")
    require((p["old"] / ".gitignore").stat().st_uid == os.geteuid(), "OLD chmod positive control not owned")


def partial_child_evidence(out):
    # Stable post-group-absence diagnostics, never qualification evidence.
    names = ("collection.json", "selected.json", "counts.json", "unstarted.json", "unfinished.json", "executed.jsonl", "subtests.jsonl")
    return {name:digest(regular(out / "work" / name)) for name in names if (out / "work" / name).is_file()}


def collection_for(c, p):
    slot = "base" if c["phase"] == "base" else "final"
    completed(c, p, "collect", slot, same_source=True)
    path = p["exec"] / "runs" / ("collect-" + slot) / "work/collection.json"
    require(isinstance(c["collection_sha256"], str) and digest(regular(path)) == c["collection_sha256"], "collection identity not fixed")
    collection = read_json(path)
    require(collection["source_digest"] == c["source_digest"] and collection["controls"] == c["controls"] and not collection["duplicates"], "collection identity mismatch")
    return collection


def selected_identities(c, collection, mode):
    ordered = collection["ordered"]
    if mode in {"complete-normal", "complete-parent-O"}:
        if c.get("schema") != 3 or c.get("phase") != "entry":
            require(not c["selection"], "current complete selection must be empty")
            return ordered
        require(c["selection"] and all("#" not in x for x in c["selection"]), "retained complete requires exact selected IDs")
    chosen = set(c["selection"])
    ids = {row["id"] for row in ordered}
    tokens = {row["id"] + "#" + str(row["occurrence"]) for row in ordered}
    require(chosen and (chosen <= ids or chosen <= tokens), "selected ID absent from exact collection")
    selected = [row for row in ordered if row["id"] in chosen or row["id"] + "#" + str(row["occurrence"]) in chosen]
    if mode == "artifact":
        require({row["id"] for row in selected} == set(collection["factory_ids"]), "artifact requires the complete factory")
    return selected


def preflight(c, p, mode, slot, *, input_path=None):
    # Parent-only checks before a slot or process can be consumed.
    allowed(mode, slot, c["phase"])
    require(not (p["exec"] / "runs" / (mode + "-" + slot)).exists(), "run slot already exists")
    if mode == "acquire":
        require(not p["root"].exists(), "execution root already exists")
        return
    require(p["root"].is_dir() and p["exec"].is_dir(), "acquisition unavailable")
    completed(c, p, "acquire", "base", same_source=True)
    if mode == "canary":
        require(input_path is not None, "canary input identity required")
        check_canary_dac(c, p, input_path)
    else:
        completed(c, p, "canary", "base", same_source=True)
    if c["phase"] == "entry" or c["phase"] == "delegation" and mode in {"focused", "complete-normal", "complete-parent-O", "artifact"}:
        completed(c, p, "smoke", "base", same_source=True)
    if mode not in {"acquire", "canary", "collect"}:
        collection = collection_for(c, p)
        selected_identities(c, collection, mode)
        if mode == "smoke" and c["phase"] == "base":
            require(c["selection"] == read_json(p["controls"] / "base-seed-ids.json"), "retained smoke selection drift")


def child_evidence(c, p, out, mode):
    # Zero exit is insufficient: bind exact completed identities and child files.
    work = out / "work"
    if mode == "acquire":
        return {}
    if mode == "canary":
        paths = ("canaries.json", "child-canary.json")
        for name in paths:
            value = read_json(work / name)
            require(value["runtime_launcher_sha256"] == c["runtime"]["sha256"], "canary runtime result mismatch")
            expected_denials = set(read_json(out / "boundary-positive.json")["probes"]) | {"LOOPBACK_BIND", "LOOPBACK_CONNECT"}
            require(set(value["named_denials"]) == expected_denials and all(x in (1, 13) for x in value["named_denials"].values()), "canary denial report invalid")
    else:
        collection = read_json(work / "collection.json")
        require(set(collection) == {"source_digest", "source_root_entries", "controls", "default_ids", "factory_ids", "ordered", "duplicates"}, "collection result keys")
        require(collection["source_digest"] == c["source_digest"] and collection["controls"] == c["controls"] and collection["source_root_entries"] == c["source_root_entries"], "collection input mismatch")
        ids = collection["default_ids"] + collection["factory_ids"]
        require(ids and len(ids) == len(set(ids)) and not collection["duplicates"] and collection["ordered"] == [{"id": name, "occurrence": 1} for name in ids], "collection identity coverage invalid")
        require(bool(collection["factory_ids"]) == c["factory"], "mandatory factory missing or unexpected")
        paths = ("collection.json",)
        if mode != "collect":
            require(digest(regular(work / "collection.json")) == c["collection_sha256"], "runner collection drift")
            selected = read_json(work / "selected.json")
            require(selected == selected_identities(c, collection, mode), "selected execution coverage drift")
            counts = read_json(work / "counts.json")
            require(counts["run"] == counts["selected"] == len(selected) and counts["discovered"] == len(ids), "runner counts incomplete")
            require(all(counts[key] == 0 for key in ("unstarted", "unfinished", "failures", "errors", "skips", "expected_failures", "unexpected_successes")), "runner non-pass counts")
            require(read_json(work / "unstarted.json") == [] and read_json(work / "unfinished.json") == [], "runner identities unfinished")
            rows = [json.loads(line) for line in regular(work / "executed.jsonl").splitlines()]
            require([{"id": row["id"], "occurrence": row["occurrence"]} for row in rows] == selected and all(row["outcome"] == "pass" for row in rows), "runner executed identities incomplete")
            paths += ("selected.json", "counts.json", "unstarted.json", "unfinished.json", "executed.jsonl")
            if (work / "subtests.jsonl").exists():
                subs = [json.loads(line) for line in regular(work / "subtests.jsonl").splitlines()]
                require(all(row["outcome"] == "pass" and row["identity"] in selected for row in subs), "subtest report non-pass")
                paths += ("subtests.jsonl",)
    return {name: digest(regular(work / name)) for name in paths}


def write_result(c, p, input_path, input_sha, out, inputs_sha, boundary_sha,
                 manifest, before_source, child, start, budget, mode, slot,
                 reason, natural, absent, cleanup_errors, *, cleanup_observations=None):
    unchanged = False
    sealed = {}
    partial = {}
    completion_error = None
    input_error = None
    try:
        config(input_path, input_sha)
        verify_old(p["old"], manifest)
        require(digest(regular(out / "inputs.json")) == inputs_sha, "parent inputs altered")
        if boundary_sha is not None:
            require(digest(regular(out / "boundary-positive.json")) == boundary_sha, "parent boundary evidence altered")
            for row in read_json(out / "boundary-positive.json")["probes"].values():
                require(digest(regular(row["path"])) == row["sha256"] and stat.S_IMODE(Path(row["path"]).stat().st_mode) == row["mode"], "boundary target bytes/mode altered")
        unchanged = True
    except (OSError, RuntimeError, ValueError, KeyError, TypeError) as exc:
        input_error = type(exc).__name__ + ":" + str(exc)
        reason = reason or "input-drift-or-incomplete-acquisition:" + str(exc)
    if absent:
        try:
            partial = partial_child_evidence(out)
            if child.returncode == 0 and reason is None and natural and unchanged:
                sealed = child_evidence(c, p, out, mode)
        except (OSError, RuntimeError, ValueError, KeyError, TypeError) as exc:
            completion_error = type(exc).__name__ + ":" + str(exc)
            reason = reason or "incomplete-child-evidence:" + str(exc)
    if budget is not None and time.monotonic() - start > budget:
        reason = reason or "total-budget-exhausted"
    result = {"mode": mode, "slot": slot, "inputs_sha256": inputs_sha, "exit": child.returncode,
              "seconds": round(time.monotonic() - start, 3), "natural_completion": natural,
              "group_absent": absent, "reason": reason, "cleanup_errors": cleanup_errors, "cleanup_observations": cleanup_observations or [],
              "input_verification_error": input_error, "completion_error": completion_error, "child_evidence": sealed, "partial_child_evidence": partial,
              "inputs_unchanged_or_acquired_exact": unchanged, "source_digest": before_source}
    ok = child.returncode == 0 and reason is None and absent and unchanged and natural and not cleanup_errors
    result["execution_pass"] = ok
    exclusive_json(out / "result.json", result)
    print(canonical(result).decode(), flush=True)
    return ok


def run(c, p, input_path, input_sha, mode, slot, start, *, budget_override=None, process_state=None, resource_guard=None, accounting_only=False):
    process_state = process_state if process_state is not None else {}
    process_state.update(spawned=False, cleanup_verified=True, pid=None, pgid=None)
    manifest = read_json(p["controls"] / "baseline-inputs.json")
    before_source = file_map(p["source"], c["source_files"])
    if mode != "acquire":
        verify_old(p["old"], manifest)
        completed(c, p, "acquire", "base", same_source=True)
    if mode not in {"acquire", "canary"}:
        completed(c, p, "canary", "base", same_source=True)
    if c["phase"] == "entry" or c["phase"] == "delegation" and mode in {"focused", "complete-normal", "complete-parent-O", "artifact"}:
        completed(c, p, "smoke", "base", same_source=True)
    if slot == "final":
        for prior in ("complete-normal-final", "complete-parent-O-final", "artifact-final"):
            existing = p["exec"] / "runs" / prior / "inputs.json"
            if existing.exists():
                anchor = read_json(existing)
                require(anchor["source_digest"] == c["source_digest"] and anchor["controls"] == c["controls"] and anchor["collection_sha256"] == c["collection_sha256"], "final candidate drift")
    if mode == "collect":
        for prior_slot in COLLECTIONS:
            existing = p["exec"] / "runs" / ("collect-" + prior_slot) / "inputs.json"
            if existing.exists():
                prior = read_json(existing)
                require_new_collection(c, prior)
    out = p["exec"] / "runs" / (mode + "-" + slot)
    ancestor_parameters = test_ancestor_parameters(p, out) if mode != "acquire" else {}
    out.parent.mkdir(exist_ok=True)
    out.mkdir(mode=0o700)  # Exclusive slot: no automatic replay or budget reset.
    work = out / "work"
    work.mkdir(mode=0o700)
    for name in ("home", "tmp", "xdg"):
        (work / name).mkdir(mode=0o700)
    env = {"PATH": str(Path(c["runtime"]["path"]).parent) + ":" + str(Path(c["git"]["path"]).parent) + ":/usr/bin:/bin:/usr/sbin:/sbin",
           "HOME": str(work / "home"), "XDG_CONFIG_HOME": str(work / "xdg"), "TMPDIR": str(work / "tmp"),
           "LC_ALL": "en_US.UTF-8", "TZ": "UTC", "PYTHONDONTWRITEBYTECODE": "1"}
    # No GIT_* isolation dependency: product git_environment strips those keys.
    parameters = {"SOURCE": p["source"], "OLD": p["old"], "CONTROLS": p["controls"], "WORK": work,
                  "INPUT": input_path, "OBJECTS": p["common_git"] / "objects",
                  "BOUNDARY": out / "boundary-positive.json", "LOG": out / "stdout.log",
                  "PREDECESSOR": p.get("predecessor", p["source"]), "ARTIFACTS": p.get("artifacts", p["old"])}
    parameters.update(ancestor_parameters)
    policy = p["controls"] / ("acquire.sb" if mode == "acquire" else "test.sb")
    script = p["controls"] / ("acquire.py" if mode == "acquire" else "canary.py" if mode == "canary" else "runner.py")
    command = ["/usr/bin/sandbox-exec"]
    for key, value in parameters.items():
        command += ["-D", key + "=" + str(value)]
    arguments = [str(input_path), input_sha, str(work)]
    if mode not in {"acquire", "canary"}:
        arguments += [mode]
    command += ["-f", str(policy), *python_command(c, p, script.name, *arguments, optimized=mode == "complete-parent-O")]
    budget = None if accounting_only else (budget_override if budget_override is not None else (1200 if mode in {"smoke", "focused"} and c["phase"] == "delegation" else LIMITS[mode]))
    require(accounting_only or 20 < budget <= (10800 if mode in {"complete-normal", "complete-parent-O"} and c["phase"] == "delegation" else 1200 if mode in {"smoke", "focused"} and c["phase"] == "delegation" else LIMITS[mode]), "budget override outside approved limit")
    exclusive_json(out / "inputs.json", {"invocation_sha256": input_sha, "phase": c["phase"], "source_digest": before_source,
        "controls": c["controls"], "runtime": c["runtime"], "git": c["git"], "git_system_config": c["git_system_config"], "collection_sha256": c["collection_sha256"], "mode": mode, "slot": slot, "command": command, "cwd": str(p["source"]),
        "environment": env, "budget_seconds_including_cleanup": budget})
    inputs_sha = digest(regular(out / "inputs.json"))
    boundary_sha = None
    if mode == "canary":
        exclusive_json(out / "boundary-positive.json", positive_boundary_controls(c, p, input_path, out))
        boundary_sha = digest(regular(out / "boundary-positive.json"))
    require(accounting_only or time.monotonic() - start < budget - 20, "setup exhausted mode budget")
    reason = None
    cleanup_observations = []
    if resource_guard is not None: resource_guard.check(force=True)
    with (out / "stdout.log").open("xb") as log:
        child = subprocess.Popen(command, cwd=p["source"], env=env, stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
        process_state.update(spawned=True, cleanup_verified=False, pid=child.pid, pgid=child.pid)
        next_progress = start
        try:
            exclusive_json(out / "child.json", {"pid": child.pid, "pgid": child.pid, "inputs_sha256": inputs_sha})
            while child.poll() is None:
                now = time.monotonic()
                if resource_guard is not None: resource_guard.check()
                if budget is not None and now - start >= budget - 20:
                    reason = "budget-exhausted"
                    break
                if os.fstat(log.fileno()).st_size > 16 * 1024 * 1024:
                    reason = "output-limit"
                    break
                if now >= next_progress:
                    print("RUN", mode, slot, "pid", child.pid, "seconds", round(now - start), flush=True)
                    next_progress = now + 30
                time.sleep(0.2)
        except BaseException as exc:
            reason = "monitor-error:" + type(exc).__name__ + ":" + str(exc)
        if os.fstat(log.fileno()).st_size > 16 * 1024 * 1024:
            reason = reason or "output-limit"
        natural = reason is None and child.returncode is not None and child.returncode >= 0
        reason, natural, absent, cleanup_errors = settle_child(child, start, budget, reason, natural, observations=cleanup_observations, parent_snapshot=resource_guard is not None)
        process_state["cleanup_verified"] = absent and not cleanup_errors
    ok = write_result(c, p, input_path, input_sha, out, inputs_sha, boundary_sha,
                      manifest, before_source, child, start, budget, mode, slot,
                      reason, natural, absent, cleanup_errors, cleanup_observations=cleanup_observations)
    return ok


if __name__ == "__main__":
    main()
