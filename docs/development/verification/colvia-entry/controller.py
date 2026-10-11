"""Bounded native verification controller; authoring draft, never an approval token."""
import fcntl
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
COLLECTIONS = frozenset(("base", *ENTRY_MODE_SLOTS["collect"]))
LIMITS = {"acquire": 300, "canary": 300, "collect": 300, "smoke": 1200,
          "focused": 1200, "complete-normal": 5400, "complete-parent-O": 5400, "artifact": 1800}


def allowed(mode, slot, phase):
    require(mode in LIMITS and phase in {"base", "entry"}, "unlisted mode/phase")
    if phase == "base":
        require(mode in {"acquire", "canary", "collect", "smoke"} and slot == "base", "base-only operation")
    else:
        require(mode in ENTRY_MODE_SLOTS and slot in ENTRY_MODE_SLOTS[mode], "entry mode/slot")


def require_new_collection(c, prior):
    require(prior.get("phase") in {"base", "entry"}, "phase-less collection evidence cannot be reused")
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
    if mode == "acquire":
        require(not p["root"].exists(), "execution root already exists; inspect, do not reuse")
        p["root"].mkdir(mode=0o700)
        p["exec"].mkdir(mode=0o700)
        (p["root"] / "denied-sentinel").write_text("synthetic-not-a-credential\n")
    require(p["root"].is_dir() and p["exec"].is_dir(), "acquisition layout unavailable")
    with (p["root"] / "controller.lock").open("a+b") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        run(c, p, input_path, sys.argv[2], mode, slot, started)


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
    return inputs


def positive_boundary_controls(c, p, input_path, out):
    # Future canary execution only. Opens do not truncate/write; chmod retains mode.
    # The parent confirms DAC permits the exact operations before the sandbox probe.
    targets = {"SOURCE": p["source"] / "hv2", "CONTROLS": p["controls"] / "common.py",
               "INPUT": input_path, "PARENT_INPUTS": out / "inputs.json",
               "PRIOR_RESULT": p["exec"] / "runs/acquire-base/result.json"}
    observations = {}
    for label, target in targets.items():
        target = unlinked_path(target)
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
    for label, target in {"COMMON_GIT": p["common_git"] / "HEAD", "SENTINEL": p["root"] / "denied-sentinel"}.items():
        target = unlinked_path(target)
        observations[label] = {"path": str(target), "operation": "open-read", "sha256": digest(regular(target))}
    return {"uid": os.geteuid(), "probes": observations, "limit": "OLD chmod proves a metadata-write refusal, not all data-write operations; mode-bit custody is checked separately"}


def test_ancestor_parameters(p, out):
    # Exact directory entries needed by classify_target, never recursive reads.
    ancestors = (out, *out.parents)
    require(len(ancestors) == 9 and ancestors[1:4] ==
            (p["exec"] / "runs", p["exec"], p["root"]) and ancestors[-1] == Path("/"),
            "unapproved test ancestor layout")
    return {"ANCESTOR_" + str(i): directory for i, directory in enumerate(ancestors)}


def run(c, p, input_path, input_sha, mode, slot, start):
    manifest = read_json(p["controls"] / "baseline-inputs.json")
    before_source = file_map(p["source"], c["source_files"])
    if mode != "acquire":
        verify_old(p["old"], manifest)
        completed(c, p, "acquire", "base")
    if mode not in {"acquire", "canary"}:
        completed(c, p, "canary", "base")
    if c["phase"] == "entry":
        completed(c, p, "smoke", "base")
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
                  "BOUNDARY": out / "boundary-positive.json", "LOG": out / "stdout.log"}
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
    budget = LIMITS[mode]
    exclusive_json(out / "inputs.json", {"invocation_sha256": input_sha, "phase": c["phase"], "source_digest": before_source,
        "controls": c["controls"], "runtime": c["runtime"], "git": c["git"], "git_system_config": c["git_system_config"], "collection_sha256": c["collection_sha256"], "mode": mode, "slot": slot, "command": command, "cwd": str(p["source"]),
        "environment": env, "budget_seconds_including_cleanup": budget})
    inputs_sha = digest(regular(out / "inputs.json"))
    boundary_sha = None
    if mode == "canary":
        exclusive_json(out / "boundary-positive.json", positive_boundary_controls(c, p, input_path, out))
        boundary_sha = digest(regular(out / "boundary-positive.json"))
    require(time.monotonic() - start < budget - 20, "setup exhausted mode budget")
    reason = None
    with (out / "stdout.log").open("xb") as log:
        child = subprocess.Popen(command, cwd=p["source"], env=env, stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
        next_progress = start
        while child.poll() is None:
            now = time.monotonic()
            if now - start >= budget - 20:
                reason = "budget-exhausted"
                break
            if os.fstat(log.fileno()).st_size > 16 * 1024 * 1024:
                reason = "output-limit"
                break
            if now >= next_progress:
                print("RUN", mode, slot, "pid", child.pid, "seconds", round(now - start), flush=True)
                next_progress = now + 30
            time.sleep(0.2)
        if os.fstat(log.fileno()).st_size > 16 * 1024 * 1024:
            reason = reason or "output-limit"
        natural = reason is None and child.returncode is not None and child.returncode >= 0
        def group_exists():
            try:
                os.killpg(child.pid, 0)
                return True
            except ProcessLookupError:
                return False
        leftover = group_exists()
        if leftover:
            reason = reason or "surviving-process-group"
            try:
                os.killpg(child.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
            deadline = min(start + budget - 5, time.monotonic() + 10)
            while group_exists() and time.monotonic() < deadline:
                time.sleep(0.1)
            if group_exists():
                os.killpg(child.pid, signal.SIGKILL)
        try:
            child.wait(timeout=max(0.1, start + budget - time.monotonic()))
        except subprocess.TimeoutExpired:
            reason = "cleanup-incomplete"
        absent = not group_exists()
    unchanged = False
    try:
        config(input_path, input_sha)  # Controls, runtime/Git and SOURCE bytes/modes.
        verify_old(p["old"], manifest)
        require(digest(regular(out / "inputs.json")) == inputs_sha, "parent inputs altered")
        if boundary_sha is not None:
            require(digest(regular(out / "boundary-positive.json")) == boundary_sha, "parent boundary evidence altered")
        unchanged = True
    except (OSError, RuntimeError, ValueError) as exc:
        reason = reason or "input-drift-or-incomplete-acquisition:" + str(exc)
    if time.monotonic() - start > budget:
        reason = reason or "total-budget-exhausted"
    result = {"mode": mode, "slot": slot, "inputs_sha256": inputs_sha, "exit": child.returncode, "seconds": round(time.monotonic() - start, 3),
              "natural_completion": natural, "group_absent": absent, "reason": reason,
              "inputs_unchanged_or_acquired_exact": unchanged, "source_digest": before_source}
    # A completed child may leave a group that disappears during cleanup: still non-pass.
    ok = child.returncode == 0 and reason is None and absent and unchanged and natural
    result["execution_pass"] = ok
    exclusive_json(out / "result.json", result)
    print(canonical(result).decode(), flush=True)
    raise SystemExit(0 if ok else 2)


if __name__ == "__main__":
    main()
