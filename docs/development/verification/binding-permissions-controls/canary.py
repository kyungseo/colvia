"""Named synthetic bootstrap probes. Authoring draft; no product qualification."""
import errno
import fcntl
import json
import os
from pathlib import Path
import shutil
import socket
import stat
import subprocess
import sys
import sysconfig
import time
from common import config, digest, exclusive_json, read_json, require, require_isolated, python_command


def denied(action):
    try:
        action()
    except OSError as exc:
        require(exc.errno in (errno.EACCES, errno.EPERM), "wrong refusal cause: " + str(exc.errno))
        return exc.errno
    raise RuntimeError("named isolation probe unexpectedly permitted")


def open_only(path, flags):
    fd = os.open(path, flags | os.O_NOFOLLOW)  # No truncation or content write.
    os.close(fd)


def boundary_probes(c, p, input_path, work):
    evidence = read_json(work.parent / "boundary-positive.json")
    require(evidence["uid"] == os.geteuid(), "positive control user mismatch")
    expected = {"SOURCE": p["source"] / "colvia", "CONTROLS": p["controls"] / "common.py",
                "INPUT": Path(input_path), "PARENT_INPUTS": work.parent / "inputs.json",
                "PRIOR_RESULT": p["exec"] / "runs/acquire-base/result.json",
                "OLD_MODE": p["old"] / ".gitignore", "COMMON_GIT": p["common_git"] / "HEAD",
                "SENTINEL": p["root"] / "denied-sentinel", "SIBLING": p["exec"] / "sibling-sentinel", "CREDENTIAL": p["root"] / "credential-sentinel"}
    if c["schema"] == 4:
        expected.update({"PREDECESSOR": p["predecessor"] / "colvia", "ARTIFACTS": p["artifacts"] / "q/colvia"})
    require(set(evidence["probes"]) == set(expected), "positive control membership")
    observed = {}
    for label, path in expected.items():
        row = evidence["probes"][label]
        require(row["path"] == str(path), "positive control target drift")
        if label == "OLD_MODE":
            require(row["operation"] == "chmod-same-mode" and stat.S_IMODE(path.stat().st_mode) == row["mode"], "OLD mode probe mismatch")
            observed[label] = denied(lambda: os.chmod(path, row["mode"], follow_symlinks=False))
            require(stat.S_IMODE(path.stat().st_mode) == row["mode"] and digest(path.read_bytes()) == row["sha256"], "OLD probe changed bytes/mode")
        elif label in {"COMMON_GIT", "SENTINEL", "SIBLING", "CREDENTIAL"}:
            require(row["operation"] == "open-read", "read probe mismatch")
            observed[label] = denied(lambda: open_only(path, os.O_RDONLY))
        else:
            require(row["operation"] == "open-write-without-write", "write probe mismatch")
            observed[label] = denied(lambda: open_only(path, os.O_WRONLY))
    return observed


def main():
    require_isolated()
    require(len(sys.argv) in (4, 5), "expected INPUT SHA WORK [child]")
    c, p = config(sys.argv[1], sys.argv[2])
    out = Path(sys.argv[3])
    require(out == p["exec"] / "runs/canary-base/work" and out.is_dir(), "canary work boundary")
    child = len(sys.argv) == 5
    require(not child or sys.argv[4] == "child", "unknown child mode")
    require(sys.implementation.name == "cpython" and tuple(sys.version_info[:3]) == (3, 14, 7) and sys.version_info.releaselevel == "final", "runtime identity")
    require(not sysconfig.get_config_var("Py_GIL_DISABLED"), "free-threaded runtime not covered")
    require(digest(Path(sys.executable).resolve().read_bytes()) == c["runtime"]["sha256"], "interpreter launcher bytes")
    forbidden_env = {k for k in os.environ if any(x in k.upper() for x in ("TOKEN", "SECRET", "PASSWORD", "API_KEY", "SSH_AUTH", "GIT_"))}
    require(not forbidden_env, "credential/Git environment leaked: names only " + repr(sorted(forbidden_env)))
    denials = boundary_probes(c, p, sys.argv[1], out)
    def bind():
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind(("127.0.0.1", 0))
    def connect():
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(1)
            sock.connect(("127.0.0.1", 9))
    denials["LOOPBACK_BIND"] = denied(bind)
    denials["LOOPBACK_CONNECT"] = denied(connect)
    if child:
        exclusive_json(out / "child-canary.json", {"named_denials": denials, "runtime_launcher_sha256": c["runtime"]["sha256"]})
        return
    for directory in (Path(os.environ["TMPDIR"]), *Path(os.environ["TMPDIR"]).parents):
        require(not directory.is_symlink() and not (directory / ".git").exists() and not (directory / ".hrn").exists(), "canary topology ancestor")
    inbounds = out / "write-and-sync"
    with inbounds.open("xb") as f:
        f.write(b"synthetic\n"); f.flush(); os.fsync(f.fileno())
        require(hasattr(fcntl, "F_FULLFSYNC"), "F_FULLFSYNC unavailable")
        fcntl.fcntl(f.fileno(), fcntl.F_FULLFSYNC)
        fcntl.flock(f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        code = "import fcntl,sys; f=open(sys.argv[1],'rb');\ntry: fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)\nexcept BlockingIOError: sys.exit(0)\nsys.exit(1)"
        subprocess.run([c["runtime"]["path"], "-I", "-S", "-B", "-c", code, str(inbounds)], stdin=subprocess.DEVNULL, check=True, timeout=15)
    fd = os.open(out, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)
    require(isinstance(os.listdir("/dev/fd"), list), "descriptor directory unavailable")
    probe = "import hashlib,pathlib,sys;assert sys.flags.isolated and sys.flags.no_site;print(hashlib.sha256(pathlib.Path(sys.executable).resolve().read_bytes()).hexdigest())"
    spawn_seconds = []
    for _ in range(3):
        start = time.monotonic()
        result = subprocess.run(["/usr/bin/env", "python3", "-I", "-S", "-B", "-c", probe], stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=30, check=True)
        require(result.stdout.strip() == c["runtime"]["sha256"], "shebang/env python drift")
        spawn_seconds.append(round(time.monotonic() - start, 3))
    subprocess.run(python_command(c, p, "canary.py", sys.argv[1], sys.argv[2], out, "child"), stdin=subprocess.DEVNULL, check=True, timeout=30)
    resolved_git = shutil.which("git")
    require(resolved_git is not None and Path(resolved_git).resolve() == Path(c["git"]["path"]), "PATH Git resolution mismatch")
    require(digest(Path(resolved_git).resolve().read_bytes()) == c["git"]["sha256"], "PATH Git bytes mismatch")
    bare_version = subprocess.run(["git", "--version"], stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=30, check=True)
    require(bare_version.stdout.strip() == c["git"]["version"], "bare Git version mismatch")
    plain, repo, linked = out / "non-git", out / "git", out / "linked"
    plain.mkdir(); repo.mkdir()
    def git(*args):
        return subprocess.run([c["git"]["path"], "-C", str(repo), *args], stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=30, check=True)
    git("init", "-q")
    git("config", "user.name", "Synthetic Verification")
    git("config", "user.email", "synthetic@example.invalid")
    git("config", "commit.gpgsign", "false")
    system = c["git_system_config"]
    system_seen = {}
    local_seen = {}
    local_allowed = {"core.repositoryformatversion": {"0"}, "core.filemode": {"true", "false"},
                     "core.bare": {"false"}, "core.logallrefupdates": {"true"},
                     "core.ignorecase": {"true", "false"}, "core.precomposeunicode": {"true", "false"},
                     "user.name": {"Synthetic Verification"}, "user.email": {"synthetic@example.invalid"}, "commit.gpgsign": {"false"}}
    for line in git("config", "--show-origin", "--list").stdout.splitlines():
        require("\t" in line, "unparseable Git origin")
        origin, pair = line.split("\t", 1)
        require("=" in pair, "valueless Git config unavailable")
        key, value = pair.split("=", 1); key = key.lower()
        if origin == "file:" + system["path"]:
            require(key in system["entries"] and value == system["entries"][key] and key not in system_seen, "unapproved system Git entry")
            system_seen[key] = value
        else:
            require(origin in {"file:.git/config", "file:" + str(repo / ".git/config")}, "unexpected Git configuration origin")
            require(key in local_allowed and value in local_allowed[key] and key not in local_seen, "unexpected synthetic Git configuration")
            local_seen[key] = value
    require(not system_seen or system_seen == system["entries"], "partial system Git origin")
    require({"user.name", "user.email", "commit.gpgsign"} <= set(local_seen), "missing synthetic Git identity")
    (repo / ".gitattributes").write_text("sample text eol=lf\n")
    (repo / "sample").write_text("synthetic\n")
    git("add", ".gitattributes", "sample")
    # Per-commit only: do not add command-line origins to the config probe.
    git("-c", "maintenance.auto=false", "-c", "gc.auto=0", "commit", "-qm", "synthetic capability canary")
    attrs = git("check-attr", "--source=HEAD", "text", "eol", "--", "sample").stdout
    require("sample: text: set" in attrs and "sample: eol: lf" in attrs, "Git source-attribute capability")
    git("worktree", "add", "--detach", str(linked), "HEAD")
    # Product import only after named boundary/runtime/Git probes.
    sys.path.insert(0, str(p["source"] / "src"))
    from hv2ref.workspace import classify_target
    require(classify_target(plain, mutation=True)["kind"] == "non-git", "plain target misclassified")
    require(classify_target(repo, mutation=True)["kind"] == "primary", "Git target misclassified")
    require(classify_target(linked)["kind"] == "linked-worktree", "linked target misclassified")
    git("worktree", "remove", str(linked))  # Only the clean synthetic canary tree.
    def scenario(label, entry, fault=None):
        target = out / (label + "-target"); target.mkdir()
        (target / "hv2").write_bytes(b"old-synthetic\n")
        (target / ".hrn/product").mkdir(parents=True)
        (target / ".hrn/staging/entry-canary").mkdir(parents=True)
        (target / ".hrn/locks").mkdir()
        (target / ".hrn/locks/writer.lock").touch()
        (target / ".hrn/product/binding.json").write_bytes(b'{"synthetic": "B0"}\n')
        events = out / (label + "-events.jsonl")
        scenario_root=out/'entry-scenarios' if c['phase']=='delegation' else out
        scenario_root.mkdir(exist_ok=True)
        request = scenario_root / (label + "-scenario.json")
        exclusive_json(request, {"entry": entry, "target": str(target), "argv": [], "events": str(events), "fault": fault})
        command = python_command(c, p, "delegation_observer.py" if c["phase"]=="delegation" else "observer.py", sys.argv[1], sys.argv[2], request, digest(request.read_bytes()))
        return target, events, command
    target, events, command = scenario("primitive", "primitive-canary")
    subprocess.run(command, stdin=subprocess.DEVNULL, check=True, timeout=30)
    rows = [json.loads(x) for x in events.read_text().splitlines()]
    required = {"open-after", "write-after", "fsync-after", "fchmod-after", "unlink-after", "replace-after",
                "mkdir-after", "rename-after", "rmdir-after", "chmod-after",
                "audit-before:open", "audit-before:os.mkdir", "audit-before:os.rename", "audit-before:os.rmdir", "audit-before:os.chmod", "audit-before:os.remove"}
    require(required <= {x["event"] for x in rows}, "primitive observation missing")
    require(not (target / "hv2").exists() and (target / "colvia").read_bytes() == b"synthetic-launcher\n", "primitive result mismatch")
    require(not (target / "primitive-dir").exists() and not (target / "primitive-renamed").exists(), "primitive namespace cleanup mismatch")
    target, events, command = scenario("short-write", "primitive-canary", {"event": "write-after", "path": "colvia", "occurrence": 1, "write_bytes": 1})
    result = subprocess.run(command, stdin=subprocess.DEVNULL, timeout=30)
    require(result.returncode == -9 and (target / "colvia").read_bytes() == b"s" and (target / "hv2").read_bytes() == b"old-synthetic\n", "kill/short-write witness mismatch")
    require((target / "colvia").stat().st_mode & 0o777 == 0o600, "short-write mode")
    for label, entry in (("lock-object", "lock-canary"), ("lock-fd", "lock-fd-canary")):
        target, events, command = scenario(label, entry)
        with (target / ".hrn/locks/writer.lock").open("rb") as f:
            fcntl.flock(f, fcntl.LOCK_EX)
            observer = subprocess.Popen(command, stdin=subprocess.DEVNULL)
            deadline = time.monotonic() + 15
            waiting = False
            while observer.poll() is None and time.monotonic() < deadline:
                lines = events.read_text().splitlines() if events.exists() else []
                try:
                    rows = [json.loads(x) for x in lines]
                except json.JSONDecodeError:
                    rows = []
                if any(x["event"] == "lock-attempt" for x in rows):
                    require(not any(x["event"] == "lock-acquired" for x in rows), "acquired parent-held lock")
                    waiting = True; break
                time.sleep(0.01)
            require(waiting, "no observed lock wait: " + label)
            fcntl.flock(f, fcntl.LOCK_UN)
        require(observer.wait(timeout=15) == 0, "lock observer failed")
        require(any(json.loads(x)["event"] == "lock-acquired" for x in events.read_text().splitlines()), "no acquired witness")
    exclusive_json(out / "canaries.json", {"named_denials": denials, "runtime_launcher_sha256": c["runtime"]["sha256"],
        "git_sha256": c["git"]["sha256"], "git_version": c["git"]["version"], "system_config_observed": system_seen,
        "spawn_seconds": spawn_seconds, "topologies": ["non-git", "primary", "linked-worktree"],
        "fullfsync": "executed", "child_inheritance": "named-probes-pass", "old_mode_probe": "metadata-write denial only; separate exact mode custody"})


if __name__ == "__main__":
    main()
