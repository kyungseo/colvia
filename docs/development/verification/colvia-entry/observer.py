"""Instrumented synthetic child: transparent flock witness and bounded fd fault seam.

This is NOT an uninstrumented CLI observation or a product recovery feature.
The future reviewed factory supplies a fixed-shape scenario and verifies events.
"""
import fcntl
import json
import os
from pathlib import Path
import runpy
import signal
import stat
import controller as control_slots
import sys
import time
from common import config, digest, read_json, regular, relative, require, unlinked_path, require_isolated, canonical


class IncompleteHandshake(Exception):
    """A newly created exclusive handshake is still being written; poll boundedly."""


def main():
    require(len(sys.argv) == 5, "expected INPUT SHA SCENARIO SHA")
    require_isolated()
    c, p = config(sys.argv[1], sys.argv[2])
    require(unlinked_path(control_slots.__file__) == p["controls"] / "controller.py", "controller import outside validated controls")
    scenario_path = unlinked_path(sys.argv[3])
    require(scenario_path.is_relative_to(p["exec"]), "scenario outside synthetic execution")
    require(digest(regular(scenario_path)) == sys.argv[4], "scenario drift")
    scenario_sha = sys.argv[4]
    s = read_json(scenario_path)
    require(isinstance(s, dict) and set(s) in ({"entry", "target", "argv", "events", "fault"},
        {"entry", "target", "argv", "events", "fault", "pause"}), "scenario keys")
    work = None
    if c["phase"] == "entry":
        work = scenario_path.parent.parent
        require(scenario_path.parent.name == "entry-scenarios" and scenario_path.suffix == ".json" and
                work.name == "work" and work.parent.name in control_slots.ENTRY_RUN_NAMES and
                work.parent.parent == p["exec"] / "runs" and work.is_dir(), "entry scenario WORK boundary")
    target, events = unlinked_path(s["target"]), unlinked_path(s["events"], exists=False)
    require(target.is_relative_to(p["exec"]) and events.is_relative_to(p["exec"]) and not events.is_relative_to(target), "scenario boundaries")
    if work is not None:
        require(target != work and target.is_relative_to(work) and events.is_relative_to(work), "entry paths outside current WORK")
    entries = {"old-source": p["old"] / "hv2", "new-source": p["source"] / "colvia",
               "installed-old": target / "hv2", "installed-new": target / "colvia"}
    primitive = s["entry"] in {"primitive-canary", "lock-canary", "lock-fd-canary", "lock-prefix-canary"}
    require(s["entry"] in entries or primitive, "entry selector")
    entry = None if primitive else unlinked_path(entries[s["entry"]])
    require(isinstance(s["argv"], list) and all(isinstance(x, str) for x in s["argv"]), "literal argv")
    argv = s["argv"]
    commands = {"init", "update", "rollback", "repair", "detach", "status", "doctor", "view", "work", "intent", "candidate"}
    offset = 1 if s["entry"].endswith("source") else 0
    require((primitive and argv == []) or (not primitive and len(argv) > offset and argv[offset] in commands and (not offset or argv[0] == "--source-checkout")), "command family")
    fault = s["fault"]
    if fault is not None:
        require(s["entry"] == "primitive-canary" or c["phase"] == "entry" and s["entry"] in {"new-source", "installed-new", "lock-prefix-canary"}, "no old-code fault substitution")
        require(set(fault) == {"event", "path", "occurrence", "write_bytes"}, "fault keys")
        require(fault["event"] in {operation + "-" + edge for operation in
                ("open", "write", "fsync", "fchmod", "unlink", "replace", "mkdir", "rename", "rmdir", "chmod")
                for edge in ("before", "after")}, "fault event")
        if fault["path"] == ".":
            require(fault["event"] in {"fsync-before", "fsync-after"}, "root fault requires fsync")
        else:
            relative(fault["path"])
        require(type(fault["occurrence"]) is int and fault["occurrence"] > 0, "fault occurrence")
        require(fault["write_bytes"] is None or type(fault["write_bytes"]) is int and fault["write_bytes"] > 0, "short write length")
        require(fault["write_bytes"] is None or fault["event"] == "write-after", "short-write event")
    pause = s.get("pause")
    if "pause" in s:
        require(c["phase"] == "entry" and s["entry"] in
                {"new-source", "installed-new", "lock-canary", "lock-fd-canary", "lock-prefix-canary"}, "pause selector/phase")
        require(isinstance(pause, dict) and set(pause) ==
                {"event", "path", "occurrence", "ready", "release", "timeout_seconds"}, "pause keys")
        require(pause["event"] == "lock-acquired" and pause["path"] == ".hrn/locks/writer.lock" and
                type(pause["occurrence"]) is int and pause["occurrence"] == 1 and
                type(pause["timeout_seconds"]) is int and pause["timeout_seconds"] in {15, 60}, "pause contract")
        ready = unlinked_path(work / relative(pause["ready"]), exists=False)
        release = unlinked_path(work / relative(pause["release"]), exists=False)
        require(ready != release and ready not in {events, scenario_path} and release not in {events, scenario_path} and
                not ready.is_relative_to(target) and not release.is_relative_to(target), "pause paths")
        require(not ready.exists() and not release.exists(), "pause paths must be exclusive")
        if fault is not None:
            require(s["entry"] in {"new-source", "installed-new", "lock-prefix-canary"}, "pause/fault selector")
            require(fault["path"] != pause["path"], "pause fault must follow lock acquisition")
            if s["entry"] == "lock-prefix-canary":
                require(fault["path"] == "prefix-probe.bin" or fault["path"] == "." and
                        fault["event"] in {"fsync-before", "fsync-after"}, "fixed synthetic prefix fault path")
    require(s["entry"] != "lock-prefix-canary" or c["phase"] == "entry", "entry-only synthetic prefix")
    log = events.open("x", buffering=1)
    active = False
    sequence = 0
    matches = 0
    pause_matches = 0
    pause_complete = False
    original = {n: getattr(os, n) for n in ("open", "write", "fsync", "fchmod", "unlink", "replace", "mkdir", "rename", "rmdir", "chmod", "read", "close")}
    original_flock = fcntl.flock
    def same_inode(info, path):
        now = unlinked_path(path).lstat()
        require(stat.S_ISREG(now.st_mode) and now.st_nlink == 1 and
                (now.st_dev, now.st_ino) == (info.st_dev, info.st_ino), "handshake/lock inode changed")
    def publish_ready(value):
        data = canonical(value)
        fd = original["open"](ready, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
        try:
            info = os.fstat(fd)
            require(stat.S_ISREG(info.st_mode) and info.st_nlink == 1, "ready file kind")
            pending = data
            while pending:
                count = original["write"](fd, pending); require(count > 0, "ready short write"); pending = pending[count:]
            original["fsync"](fd)
            same_inode(info, ready)
        finally:
            original["close"](fd)
        return info, data
    def read_handshake(path):
        unlinked_path(path)
        fd = original["open"](path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
        try:
            info = os.fstat(fd)
            require(stat.S_ISREG(info.st_mode) and info.st_nlink == 1 and info.st_size <= 4096, "handshake file kind/size")
            data = b""
            while True:
                part = original["read"](fd, 4097 - len(data))
                if not part: break
                data += part; require(len(data) <= 4096, "handshake too large")
            after = os.fstat(fd)
            if (info.st_size, info.st_mtime_ns, info.st_ctime_ns) != (after.st_size, after.st_mtime_ns, after.st_ctime_ns):
                raise IncompleteHandshake("handshake write in progress")
            same_inode(info, path)
        finally:
            original["close"](fd)
        try:
            value = json.loads(data)
        except (json.JSONDecodeError, UnicodeError) as exc:
            raise IncompleteHandshake("handshake JSON incomplete") from exc
        require(canonical(value) == data, "noncanonical/duplicate handshake")
        return value, info, data
    def pause_after_lock(fd):
        nonlocal pause_complete
        lock = unlinked_path(target / pause["path"])
        lock_info = os.fstat(fd); same_inode(lock_info, lock)
        require(lock_info.st_size == 0, "nonempty lock anchor")
        target_info = target.stat()
        token = {"scenario_sha256": scenario_sha, "sequence": sequence,
            "event": "lock-acquired", "pid": os.getpid(), "pgid": os.getpgrp(),
            "lock": {"dev": lock_info.st_dev, "ino": lock_info.st_ino, "path": pause["path"]},
            "target": {"dev": target_info.st_dev, "ino": target_info.st_ino}}
        ready_info, ready_bytes = publish_ready(token)
        deadline = time.monotonic() + pause["timeout_seconds"]
        while time.monotonic() < deadline:
            if release.exists() or release.is_symlink():
                try:
                    value, _, _ = read_handshake(release)
                except IncompleteHandshake:
                    time.sleep(0.02)
                    continue
                require(isinstance(value, dict) and set(value) == {"scenario_sha256", "sequence", "action"} and
                        type(value["sequence"]) is int and isinstance(value["scenario_sha256"], str) and
                        value == {"scenario_sha256": token["scenario_sha256"], "sequence": token["sequence"],
                        "action": "continue"}, "pause release token mismatch")
                same_inode(ready_info, ready)
                _, _, current_ready = read_handshake(ready)
                require(current_ready == ready_bytes, "ready token changed")
                same_inode(lock_info, lock)
                require((target.stat().st_dev, target.stat().st_ino) == (target_info.st_dev, target_info.st_ino), "target changed while paused")
                pause_complete = True
                return
            time.sleep(0.02)
        raise RuntimeError("pause release timeout")
    def path_of(value):
        if isinstance(value, int):
            if stat.S_ISFIFO(os.fstat(value).st_mode):
                return None
            require(hasattr(fcntl, "F_GETPATH"), "fd path observation unavailable")
            value = fcntl.fcntl(value, fcntl.F_GETPATH, b"\0" * 1024).split(b"\0", 1)[0]
        if isinstance(value, bytes):
            value = os.fsdecode(value)
        if not isinstance(value, (str, os.PathLike)):
            return None
        q = Path(os.path.abspath(value))
        return q.relative_to(target).as_posix() if q.is_relative_to(target) else None
    def emit(event, value, extra=None):
        nonlocal active, sequence, matches, pause_matches
        if active:
            return
        name = path_of(value)
        if name is None:
            return
        active = True
        try:
            sequence += 1
            log.write(json.dumps({"seq": sequence, "event": event, "path": name, "detail": extra,
                "pid": os.getpid(), "pgid": os.getpgrp(), "monotonic_ns": time.monotonic_ns()}) + "\n")
            log.flush(); original["fsync"](log.fileno())
            if pause and event == pause["event"] and name == pause["path"]:
                pause_matches += 1
                if pause_matches == pause["occurrence"]:
                    pause_after_lock(value)
            if fault and event == fault["event"] and name == fault["path"]:
                require(pause is None or pause_complete, "fault occurred before matching pause release")
                matches += 1
                if matches == fault["occurrence"]:
                    os.kill(os.getpid(), signal.SIGKILL)
        finally:
            active = False
    relative_open_path = None
    def audit(event, args):
        if active:
            return
        if event in {"open", "os.mkdir", "os.remove", "os.rmdir", "os.rename", "os.chmod"} and args:
            value = relative_open_path if event == "open" and relative_open_path is not None else args[0]
            emit("audit-before:" + event, value, repr(args[1:])[:1024])
    def observed_open(path, flags, mode=0o777, *, dir_fd=None):
        nonlocal relative_open_path
        if dir_fd is not None:
            # Preserve the product's descriptor-relative no-follow read. Resolve
            # only the witness; the original syscall still receives dir_fd.
            allowed = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_NONBLOCK | getattr(os, "O_CLOEXEC", 0)
            require(type(flags) is int and flags & ~allowed == 0 and flags & os.O_NOFOLLOW,
                    "relative-fd read flags unsupported")
            component = os.fsdecode(os.fspath(path))
            require(component not in {"", ".", ".."} and "/" not in component,
                    "relative-fd read component unsupported")
            require(type(dir_fd) is int and stat.S_ISDIR(os.fstat(dir_fd).st_mode),
                    "relative-fd read requires directory descriptor")
            require(hasattr(fcntl, "F_GETPATH"), "fd path observation unavailable")
            parent = Path(os.fsdecode(fcntl.fcntl(dir_fd, fcntl.F_GETPATH, b"\0" * 1024).split(b"\0", 1)[0]))
            require(parent.is_absolute(), "relative-fd parent path unavailable")
            parent_info = os.fstat(dir_fd); named_parent = parent.stat(follow_symlinks=False)
            require((parent_info.st_dev, parent_info.st_ino) == (named_parent.st_dev, named_parent.st_ino),
                    "relative-fd parent identity changed")
            observed = parent / component
            detail = {"flags": flags, "mode": mode, "dir_fd": dir_fd}
            emit("open-before", observed, detail)
            previous = relative_open_path; relative_open_path = observed
            try:
                fd = original["open"](path, flags, mode, dir_fd=dir_fd)
            finally:
                relative_open_path = previous
            try:
                opened = os.fstat(fd); named = observed.stat(follow_symlinks=False)
                actual = Path(os.fsdecode(fcntl.fcntl(fd, fcntl.F_GETPATH, b"\0" * 1024).split(b"\0", 1)[0]))
                require(actual == observed and (opened.st_dev, opened.st_ino) == (named.st_dev, named.st_ino),
                        "relative-fd opened identity changed")
                emit("open-after", fd, detail)
            except BaseException:
                original["close"](fd)
                raise
            return fd
        emit("open-before", path, {"flags": flags, "mode": mode})
        fd = original["open"](path, flags, mode)
        emit("open-after", path, {"flags": flags, "mode": mode})
        return fd
    def observed_write(fd, data):
        emit("write-before", fd, {"requested": len(data)})
        selected = fault and fault["event"] == "write-after" and path_of(fd) == fault["path"] and matches + 1 == fault["occurrence"]
        if selected and fault["write_bytes"] is not None:
            require(fault["write_bytes"] <= len(data), "requested fault byte count unavailable")
            data = data[:fault["write_bytes"]]
        count = original["write"](fd, data)
        emit("write-after", fd, {"written": count})
        return count
    def observed_fsync(fd):
        emit("fsync-before", fd)
        result = original["fsync"](fd); emit("fsync-after", fd); return result
    def observed_fchmod(fd, mode):
        emit("fchmod-before", fd, {"mode": mode})
        result = original["fchmod"](fd, mode); emit("fchmod-after", fd, {"mode": mode}); return result
    def observed_unlink(path, *, dir_fd=None):
        require(dir_fd is None, "relative-fd unlink observation unsupported")
        emit("unlink-before", path)
        result = original["unlink"](path); emit("unlink-after", path); return result
    def observed_replace(src, dst, *, src_dir_fd=None, dst_dir_fd=None):
        require(src_dir_fd is None and dst_dir_fd is None, "relative-fd replace observation unsupported")
        emit("replace-before", dst, {"from": path_of(src)})
        result = original["replace"](src, dst); emit("replace-after", dst, {"from": path_of(src)}); return result
    def observed_mkdir(path, mode=0o777, *, dir_fd=None):
        require(dir_fd is None, "relative-fd mkdir observation unsupported")
        emit("mkdir-before", path, {"mode": mode})
        result = original["mkdir"](path, mode); emit("mkdir-after", path, {"mode": mode}); return result
    def observed_rename(src, dst, *, src_dir_fd=None, dst_dir_fd=None):
        require(src_dir_fd is None and dst_dir_fd is None, "relative-fd rename observation unsupported")
        emit("rename-before", dst, {"from": path_of(src)})
        result = original["rename"](src, dst); emit("rename-after", dst, {"from": path_of(src)}); return result
    def observed_rmdir(path, *, dir_fd=None):
        require(dir_fd is None, "relative-fd rmdir observation unsupported")
        emit("rmdir-before", path)
        result = original["rmdir"](path); emit("rmdir-after", path); return result
    def observed_chmod(path, mode, *, dir_fd=None, follow_symlinks=True):
        require(dir_fd is None, "relative-fd chmod observation unsupported")
        emit("chmod-before", path, {"mode": mode})
        result = original["chmod"](path, mode, follow_symlinks=follow_symlinks)
        emit("chmod-after", path, {"mode": mode}); return result
    def observed_flock(fd, operation):
        observed_fd = fd if isinstance(fd, int) else fd.fileno()
        require(isinstance(observed_fd, int), "flock descriptor unavailable")
        if operation == fcntl.LOCK_EX:
            info = os.fstat(observed_fd)
            emit("lock-attempt", observed_fd, {"fd": observed_fd, "dev": info.st_dev, "ino": info.st_ino})
        result = original_flock(fd, operation)  # Preserve original object/operation semantics.
        if operation == fcntl.LOCK_EX:
            info = os.fstat(observed_fd)
            emit("lock-acquired", observed_fd, {"fd": observed_fd, "dev": info.st_dev, "ino": info.st_ino})
        return result
    # Old-source late-lock runs change only flock delegation/logging, not byte writers.
    fcntl.flock = observed_flock
    if s["entry"] in {"new-source", "installed-new", "primitive-canary", "lock-prefix-canary"}:
        sys.addaudithook(audit)
        os.open, os.write, os.fsync, os.fchmod = observed_open, observed_write, observed_fsync, observed_fchmod
        os.unlink, os.replace, os.mkdir = observed_unlink, observed_replace, observed_mkdir
        os.rename, os.rmdir, os.chmod = observed_rename, observed_rmdir, observed_chmod
    sys.argv = [str(entry), *argv]
    try:
        if s["entry"] == "primitive-canary":
            # Fixed fake bytes exercise controls only; no runtime format or records.
            fd = os.open(target / "colvia", os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
            try:
                data = b"synthetic-launcher\n"
                while data:
                    written = os.write(fd, data); require(written > 0, "zero canary write"); data = data[written:]
                os.fsync(fd); os.fchmod(fd, 0o755); os.fsync(fd)
            finally:
                os.close(fd)
            os.unlink(target / "hv2")
            stage = target / ".hrn/staging/entry-canary/binding.next"
            fd = os.open(stage, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
            try:
                os.write(fd, b'{"synthetic": "B1"}\n'); os.fsync(fd)
            finally:
                os.close(fd)
            os.replace(stage, target / ".hrn/product/binding.json")
            directory = target / "primitive-dir"
            os.mkdir(directory); os.chmod(directory, 0o700)
            renamed = target / "primitive-renamed"
            os.rename(directory, renamed); os.rmdir(renamed)
            for parent in (target, stage.parent, target / ".hrn/product"):
                fd = os.open(parent, os.O_RDONLY)
                try: os.fsync(fd)
                finally: os.close(fd)
        elif s["entry"] in {"lock-canary", "lock-fd-canary", "lock-prefix-canary"}:
            with (target / ".hrn/locks/writer.lock").open("rb") as f:
                operand = f if s["entry"] == "lock-canary" else f.fileno()
                fcntl.flock(operand, fcntl.LOCK_EX)
                if s["entry"] == "lock-prefix-canary":
                    fd = os.open(target / "prefix-probe.bin", os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
                    try:
                        data = b"synthetic-prefix-only\n"
                        while data:
                            count = os.write(fd, data); require(count > 0, "zero prefix write"); data = data[count:]
                        os.fsync(fd)
                    finally:
                        os.close(fd)
                    root_fd = os.open(target, os.O_RDONLY)
                    try:
                        os.fsync(root_fd)
                    finally:
                        os.close(root_fd)
                fcntl.flock(operand, fcntl.LOCK_UN)
        else:
            try:
                runpy.run_path(str(entry), run_name="__main__")
            except SystemExit as exc:
                if exc.code is None or exc.code == 0:
                    require(pause is None or pause_complete, "requested pause was not observed")
                    require(fault is None, "requested fault was not observed")
                raise
        require(pause is None or pause_complete, "requested pause was not observed")
        require(fault is None, "requested fault was not observed")
    finally:
        log.close()


if __name__ == "__main__":
    main()
