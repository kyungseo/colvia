"""Explicit platform choices for synthetic contract fixtures, not runtime proof.

The product functions stay unpatched. Installed tests must continue to pass their
actual verified inventory explicitly; these helpers serve labelled unit doubles.
"""
from __future__ import annotations

import copy
import sys
from hv2ref import work


def fixture_window(legacy=None):
    return "windows-2" if sys.platform == "win32" else legacy


def fixture_init_schema():
    return 6 if sys.platform == "win32" else 1


def fixture_runtime(binding, legacy=None):
    value = {"binding_ref": copy.deepcopy(binding), "launcher_sha256": None}
    window = fixture_window(legacy)
    if window is not None:
        value["inventory_id"] = window
    return value


def fixture_snapshot(target, **kwargs):
    kwargs.setdefault("verified_inventory_id", fixture_window())
    return work.snapshot(target, **kwargs)


def fixture_preflight_changed_paths(target, manifest, **kwargs):
    kwargs.setdefault("verified_inventory_id", fixture_window())
    return work.preflight_changed_paths(target, manifest, **kwargs)


def fixture_verify_worker_sources(target, manifest, **kwargs):
    kwargs.setdefault("verified_inventory_id", fixture_window())
    return work.verify_worker_sources(target, manifest, **kwargs)


def fixture_temporary_directory(**kwargs):
    import os
    import tempfile
    if sys.platform == "win32":
        # This root is supplied by the bounded native runner, never a private profile.
        kwargs.setdefault("dir", os.environ["COLVIA_NATIVE_TEST_ROOT"])
        kwargs["prefix"] = "t-"
    return tempfile.TemporaryDirectory(**kwargs)


def fixture_source():
    """Prepare one real Windows source per test process; keep raw source untouched."""
    from hv2ref.product import source_root, workspace_candidate
    if sys.platform != "win32":
        return source_root()
    cached = getattr(fixture_source, "_prepared", None)
    if cached is not None:
        return cached
    import os
    from pathlib import Path
    import shutil
    import subprocess
    import tempfile
    common = source_root()
    holder = Path(tempfile.mkdtemp(prefix="s-", dir=os.environ["COLVIA_NATIVE_TEST_ROOT"]))
    output = holder / "p"
    result = subprocess.run([sys.executable, "-I", "-B", str(common / "scripts/prepare-windows.py"),
                             "--source", str(common), "--output", str(output)], capture_output=True, timeout=45)
    if result.returncode:
        raise AssertionError((result.stdout + result.stderr).decode(errors="replace"))
    # Source-oriented help/link and independent-auditor tests also consume support
    # files. Copy them once; never transform extra files or replace managed bytes.
    for path in common.rglob("*"):
        relative = path.relative_to(common)
        if any(part in {".git", "__pycache__"} for part in relative.parts):
            continue
        if path.is_symlink():
            raise AssertionError("source fixture requires non-symlink inputs")
        if path.is_file():
            destination = output / relative
            if not destination.exists():
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(path, destination)
    if workspace_candidate(output)["release_ref"]["inventory_id"] != "windows-2":
        raise AssertionError("prepared fixture window mismatch")
    fixture_source._prepared = output
    return output


def fixture_pgid(pid=None):
    import os
    if sys.platform == "win32":
        return None  # The native runner's Job report owns descendant containment.
    return os.getpgrp() if pid is None else os.getpgid(pid)


def fixture_kill(test, child):
    import signal
    child.kill()
    expected = 1 if sys.platform == "win32" else -signal.SIGKILL
    test.assertEqual(expected, child.wait(timeout=10))


def fixture_assert_lock(test, path, *, blocked):
    """Independent OS lock observation, not a call to the product lock helper."""
    import errno
    import os
    before = path.stat()
    mode = "r+b" if sys.platform == "win32" else "rb"
    with path.open(mode) as handle:
        if sys.platform == "win32":
            import msvcrt
            os.lseek(handle.fileno(), 0, os.SEEK_SET)
            if blocked:
                with test.assertRaises(OSError) as caught:
                    msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
                # The successful open above excludes file-open access denial.
                # Microsoft _locking specifies EACCES for a nonblocking conflict.
                test.assertEqual(errno.EACCES, caught.exception.errno)
            else:
                # Process exit and the OS's final lock release need not coincide.
                import time
                started = time.monotonic(); deadline = started + 5
                while True:
                    try:
                        msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
                        break
                    except OSError as exc:
                        if exc.errno != errno.EACCES or time.monotonic() >= deadline:
                            raise
                        time.sleep(.01)
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
                print("NATIVE_LOCK_RELEASE_WAIT_SECONDS " + str(time.monotonic() - started), flush=True)
        else:
            import fcntl
            if blocked:
                with test.assertRaises(BlockingIOError):
                    fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
            else:
                fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
                fcntl.flock(handle, fcntl.LOCK_UN)
    after = path.stat()
    test.assertEqual((before.st_dev, before.st_ino, before.st_size),
                     (after.st_dev, after.st_ino, after.st_size))


def fixture_directory_link(path, target):
    """POSIX directory symlink or an actual standard-account NTFS junction."""
    import os
    import subprocess
    if sys.platform != "win32":
        path.symlink_to(target, target_is_directory=True)
        return
    if path.exists() or path.is_symlink() or path.is_junction():
        raise AssertionError("directory link fixture already exists")
    result = subprocess.run(["cmd", "/d", "/c", "mklink", "/J", str(path), str(target.absolute())],
                            capture_output=True, timeout=10)
    if result.returncode or not path.is_junction() or not (path.lstat().st_file_attributes & 0x400):
        raise AssertionError((result.stdout + result.stderr).decode(errors="replace"))


def fixture_is_link(path):
    return path.is_symlink() or (sys.platform == "win32" and path.is_junction())


def fixture_unlink(path):
    if sys.platform == "win32" and path.is_junction():
        path.rmdir()  # Remove this fixture link only, never the target tree.
    else:
        path.unlink()


def fixture_snapshot_paths(root):
    """Do not traverse junctions while collecting preservation evidence."""
    if sys.platform != "win32":
        return [root, *sorted(root.rglob("*"), key=lambda path: path.as_posix())]
    pending=[root]; result=[]
    while pending:
        path=pending.pop();result.append(path)
        if not fixture_is_link(path) and path.is_dir():
            pending.extend(sorted(path.iterdir(), key=lambda child: child.as_posix(), reverse=True))
    return result


def fixture_unsafe_link(path, target):
    """Use actual POSIX symlinks or a native junction at the same unsafe member.

    For a file-valued target on Windows, the junction names its parent directory.
    This is explicitly directory-reparse refusal evidence, not file-symlink
    creation or file-symlink support. All original external bytes stay in place.
    """
    from pathlib import Path
    target = Path(target)
    if sys.platform != "win32":
        path.symlink_to(target)
        return
    if not target.is_absolute():
        target = path.parent / target
    directory = target if target.is_dir() else target.parent
    fixture_directory_link(path, directory)


def posix_mechanism(reason):
    """Declared before discovery; excluded cases are never added to PASS."""
    import unittest
    return unittest.skipIf(sys.platform == "win32", "POSIX mechanism only: " + reason)
