"""Offline OLD reconstruction. Runs only under acquire.sb after separate approval."""
import os
from pathlib import Path
import subprocess
import sys
from common import BASE, canonical, config, digest, read_json, relative, require, verify_old, git_blob_oid, require_isolated, unlinked_path


def main():
    require_isolated()
    require(len(sys.argv) == 4, "expected invocation path, digest and work directory")
    c, p = config(sys.argv[1], sys.argv[2])
    m = read_json(p["controls"] / "baseline-inputs.json")
    require(m["base"] == BASE, "baseline mismatch")
    old = p["old"]
    require(not old.exists(), "OLD already exists; preserve and stop")
    work = unlinked_path(sys.argv[3])
    require(work == p["exec"] / "runs/acquire-base/work", "acquisition work boundary")
    objects = unlinked_path(p["common_git"] / "objects")
    alternates = objects / "info/alternates"
    require(not alternates.exists() and not alternates.is_symlink(), "alternate object stores unavailable")
    require(not list((objects / "pack").glob("*.promisor")), "promisor object stores unavailable")
    # A small synthetic bare metadata directory, not a source checkout or worktree.
    # Git reads only its safe local config and the fixed source object store.
    metadata = work / "git-metadata"
    metadata.mkdir(mode=0o700)
    (metadata / "objects").mkdir(); (metadata / "refs").mkdir()
    (metadata / "HEAD").write_text("ref: refs/heads/synthetic-acquisition\n")
    (metadata / "config").write_text("[core]\n\trepositoryformatversion = 0\n\tbare = true\n")
    env = dict(os.environ)
    env.update({"GIT_OBJECT_DIRECTORY": str(objects), "GIT_NO_LAZY_FETCH": "1", "GIT_OPTIONAL_LOCKS": "0",
                "GIT_CONFIG_SYSTEM": c["git_system_config"]["path"], "GIT_CONFIG_GLOBAL": "/dev/null"})
    def git(*args):
        return subprocess.check_output([c["git"]["path"], "--git-dir=" + str(metadata), *args], env=env, stdin=subprocess.DEVNULL, timeout=30)
    rows = git("ls-tree", "-rz", "--full-tree", BASE).split(b"\0")
    observed = {}
    for row in rows:
        if not row:
            continue
        header, rawname = row.split(b"\t", 1)
        mode, kind, oid = header.decode("ascii").split()
        name = rawname.decode("utf-8")
        relative(name)
        require(kind == "blob" and mode in ("100644", "100755"), "unsupported committed member")
        require(name not in observed, "duplicate committed member")
        observed[name] = (mode, oid)
    require(observed == {n: (v["git_mode"], v["oid"]) for n, v in m["files"].items()}, "tree identity mismatch")
    old.mkdir(mode=0o700)
    for name, entry in m["files"].items():
        data = git("cat-file", "blob", entry["oid"])
        require(len(data) == entry["size"] and digest(data) == entry["sha256"] and git_blob_oid(data) == entry["oid"], "blob mismatch")
        dest = old / relative(name)
        dest.parent.mkdir(parents=True, exist_ok=True)
        with dest.open("xb") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        dest.chmod(0o555 if entry["git_mode"] == "100755" else 0o444)
    for directory in sorted((p for p in old.rglob("*") if p.is_dir()), key=lambda p: len(p.parts), reverse=True):
        directory.chmod(0o555)
    old.chmod(0o555)
    print(canonical({"old_verified": verify_old(old, m), "files": len(m["files"])}).decode(), flush=True)


if __name__ == "__main__":
    main()
