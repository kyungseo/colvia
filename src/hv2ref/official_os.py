"""macOS operations for newly added U2 paths, not a general platform framework.

Policy and journal state transitions stay in the Host. These operations retain
private-file/fsync, bounded nonblocking locks, and the existing observed-process
termination semantics. The ps scan is not a proof against daemon escape or PID
reuse within its one-second birth-time resolution.
"""
import ctypes
import fcntl
import os
from pathlib import Path
import selectors
import signal
import subprocess
import time


class MacControllerLock:
    def __init__(self, path, checked_open, require):
        self.fd = checked_open(path, os.O_RDWR)
        try:
            fcntl.flock(self.fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BaseException:
            os.close(self.fd)
            self.fd = None
            require(False, 'another controller owns this execution')

    def close(self):
        if self.fd is not None:
            fcntl.flock(self.fd, fcntl.LOCK_UN)
            os.close(self.fd)
            self.fd = None


class MacExecution:
    def __init__(self, require):
        self.require = require

    def preflight(self, purpose):
        needed = ['O_NOFOLLOW', 'O_DIRECTORY', 'O_CLOEXEC']
        self.require(all(hasattr(os, name) for name in needed), 'execution-file-capability-unavailable')
        if purpose == 'claude-native':
            self.require(hasattr(os, 'mkfifo') and hasattr(os, 'killpg'), 'execution-process-capability-unavailable')
            self.require(Path('/bin/ps').is_file(), 'execution-observation-unavailable')
        if purpose == 'codex-v58':
            self.require(hasattr(os, 'killpg'), 'execution-process-capability-unavailable')
            self.require(Path('/bin/ps').is_file(), 'execution-observation-unavailable')
            import socket
            self.require(hasattr(socket, 'AF_UNIX') and hasattr(socket, 'SCM_RIGHTS'), 'execution-FD-capability-unavailable')
            self.continuous_ns()  # Fail before admission or live reservation.

    @staticmethod
    def monotonic():
        # Retain the Claude/read-host clock, including its suspend semantics.
        return time.monotonic()

    def continuous_ns(self):
        class Timebase(ctypes.Structure):
            _fields_ = [('numer', ctypes.c_uint32), ('denom', ctypes.c_uint32)]
        native = ctypes.CDLL('/usr/lib/libSystem.B.dylib')
        native.mach_continuous_time.restype = ctypes.c_uint64
        native.mach_timebase_info.argtypes = [ctypes.POINTER(Timebase)]
        value = Timebase()
        self.require(native.mach_timebase_info(ctypes.byref(value)) == 0 and value.denom != 0, 'continuous-clock-unavailable')
        return native.mach_continuous_time() * value.numer // value.denom

    @staticmethod
    def private_directory(path, *, resume=False):
        Path(path).mkdir(mode=0o700, exist_ok=resume)

    @staticmethod
    def controller_lock(path, checked_open, require):
        return MacControllerLock(path, checked_open, require)

    @staticmethod
    def create_journal(path):
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)
        parent = os.open(Path(path).parent, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        try:
            os.fsync(parent)
        finally:
            os.close(parent)

    def append_journal(self, path, raw, checked_open, unchanged, limit):
        fd = checked_open(path, os.O_WRONLY | os.O_APPEND)
        try:
            # Immediate bounded refusal; never inherit an indefinite wait.
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            current, opened = Path(path).lstat(), os.fstat(fd)
            self.require((current.st_dev, current.st_ino) == (opened.st_dev, opened.st_ino), 'journal-replaced')
            self.require(unchanged(), 'journal-race')
            self.require(os.fstat(fd).st_size + len(raw) <= limit, 'journal-byte-limit')
            view = memoryview(raw)
            while view:
                written = os.write(fd, view)
                self.require(written > 0, 'journal-short-write')
                view = view[written:]
            os.fsync(fd)
        finally:
            os.close(fd)

    @staticmethod
    def replace_checkpoint(partial, final, value, private_writer):
        # This is a mutable checkpoint, not an exclusive acceptance publication.
        private_writer(partial, value)
        os.replace(partial, final)
        fd = os.open(Path(final).parent, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)

    @staticmethod
    def relay_channels(run):
        selector = selectors.DefaultSelector()
        up = down = None
        try:
            for name in ('up.fifo', 'down.fifo'):
                os.mkfifo(Path(run) / name, 0o600)
            up = os.open(Path(run) / 'up.fifo', os.O_RDWR | os.O_NONBLOCK | os.O_NOFOLLOW)
            down = os.open(Path(run) / 'down.fifo', os.O_RDWR | os.O_NONBLOCK | os.O_NOFOLLOW)
            return selector, up, down
        except BaseException:
            for fd in (up, down):
                if fd is not None:
                    os.close(fd)
            selector.close()
            # Keep partial names for diagnosis; do not repair/retry creation.
            raise

    @staticmethod
    def launch(argv, cwd, env):
        return subprocess.Popen(argv, cwd=cwd, env=env, stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)

    @staticmethod
    def watch_native(selector, process, up):
        for stream, name in ((process.stdout, 'stdout'), (process.stderr, 'stderr')):
            os.set_blocking(stream.fileno(), False)
            selector.register(stream, selectors.EVENT_READ, name)
        selector.register(up, selectors.EVENT_READ, 'relay')

    @staticmethod
    def ready_chunks(selector, timeout):
        for key, _ in selector.select(timeout):
            chunk = os.read(key.fd, 65536)
            if not chunk:
                selector.unregister(key.fd)
            yield key.data, key.fd, chunk

    @staticmethod
    def send_process(process, raw):
        process.stdin.write(raw)
        process.stdin.flush()

    def send_relay(self, fd, raw):
        self.require(os.write(fd, raw) == len(raw), 'relay-short-write')

    def observe_owned(self, process, known):
        out = subprocess.check_output(['/bin/ps', '-axo', 'pid=,ppid=,pgid=,lstart='], text=True, timeout=5)
        rows = {}
        for line in out.splitlines():
            fields = line.split(None, 3)
            if len(fields) == 4:
                rows[int(fields[0])] = {'ppid': int(fields[1]), 'pgid': int(fields[2]), 'birth': fields[3]}
        owned = {process.pid} | {pid for pid, row in rows.items() if row['pgid'] == process.pid}
        changed = True
        while changed:
            newer = {pid for pid, row in rows.items() if row['ppid'] in owned}
            changed = not newer <= owned
            owned |= newer
        for pid in owned:
            if pid in rows:
                if pid in known:
                    self.require(known[pid]['birth'] == rows[pid]['birth'], 'pid-reuse')
                known[pid] = rows[pid]
        return rows

    @staticmethod
    def signal_group(pid, sig):
        try:
            os.killpg(pid, sig)
        except ProcessLookupError:
            pass

    def stop_owned(self, process, known, snapshot):
        scan_ok, alive, rows = True, [], {}
        try:
            rows = snapshot()
        except BaseException:
            scan_ok = False
        for sig in (signal.SIGTERM, signal.SIGKILL):
            self.signal_group(process.pid, sig)
            for pid, old in known.items():
                row = rows.get(pid)
                if row and row['birth'] == old['birth'] and row['pgid'] != process.pid:
                    try:
                        os.kill(pid, sig)
                    except ProcessLookupError:
                        pass
            end = time.monotonic() + 10
            while time.monotonic() < end:
                process.poll()
                try:
                    rows = snapshot()
                except BaseException:
                    scan_ok = False
                    break
                alive = [pid for pid, old in known.items() if pid in rows and rows[pid]['birth'] == old['birth']]
                if not alive and not any(row['pgid'] == process.pid for row in rows.values()):
                    break
                time.sleep(.1)
            if scan_ok and not alive and not any(row['pgid'] == process.pid for row in rows.values()):
                break
        return process.poll() is not None and scan_ok and not alive and not any(row['pgid'] == process.pid for row in rows.values())

    @staticmethod
    def close_channels(selector, up, down):
        selector.close()
        for fd in (up, down):
            if fd is not None:
                os.close(fd)

    def budget_lock(self, fd, *, exclusive, deadline_ms):
        deadline = self.monotonic() + min(5.0, max(0.0, (deadline_ms - time.time_ns() // 1_000_000) / 1000))
        while True:
            self.require(self.monotonic() < deadline, 'v58-journal-lock-deadline')
            try:
                fcntl.flock(fd, (fcntl.LOCK_EX if exclusive else fcntl.LOCK_SH) | fcntl.LOCK_NB)
                return
            except BlockingIOError:
                time.sleep(0.01)


def execution_os(require, *, purpose='read-host', platform=None):
    import sys
    require((sys.platform if platform is None else platform) == 'darwin', 'unsupported-execution-platform')
    require(purpose == 'read-host', 'unsupported-official-purpose')
    runtime = MacExecution(require)
    runtime.preflight(purpose)
    return runtime
