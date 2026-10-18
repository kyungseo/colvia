"""Source-only verification helpers. No product imports and no command dispatch."""
import hashlib
import json
import os
from pathlib import Path
import stat
import sys

BASE = "238514686078ce1564010a7b69013f48a635c57c"
OLD_RELEASE = "8bd0eeac55fb0af92b61a7a36a98adb9957b880c791b957b20c319a51c5577f3"

def require(ok, message):
    if not ok:
        raise RuntimeError(message)

def digest(data):
    return hashlib.sha256(data).hexdigest()

def canonical(value):
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False) + "\n").encode()

def read_json(path):
    def pairs(items):
        out = {}
        for k, v in items:
            require(k not in out, "duplicate JSON member")
            out[k] = v
        return out
    raw = Path(path).read_bytes()
    require(len(raw) <= 4 * 1024 * 1024, "oversized control JSON")
    return json.loads(raw, object_pairs_hook=pairs)

def regular(path):
    path = Path(path)
    st = path.lstat()
    require(stat.S_ISREG(st.st_mode) and st.st_nlink == 1, "not a one-link regular input: " + str(path))
    return path.read_bytes()

def relative(value):
    p = Path(value)
    require(not p.is_absolute() and value == p.as_posix() and all(x not in ("", ".", "..") for x in value.split("/")), "unsafe input member")
    return p

def unlinked_path(path, *, exists=True):
    p = Path(path)
    require(p.is_absolute() and str(p) == os.path.normpath(p), "nonliteral absolute path")
    for q in (p, *p.parents):
        require(not q.is_symlink(), "linked path: " + str(q))
    if exists:
        require(p.exists(), "missing path: " + str(p))
    return p

def file_map(root, expected):
    result = {}
    for name in sorted(expected):
        p = unlinked_path(root / relative(name))
        b = regular(p)
        result[name] = {"sha256": digest(b), "size": len(b), "mode": stat.S_IMODE(p.stat().st_mode)}
    require(result == expected, "input bytes/mode drift")
    # Import/discovery roots cannot acquire unlisted code or data, including pyc.
    for directory in ("src", "tests"):
        if (root / directory).is_dir():
            actual = set()
            for p in (root / directory).rglob("*"):
                require(not p.is_symlink(), "linked import/discovery member")
                if p.is_file():
                    actual.add(p.relative_to(root).as_posix())
            require(actual == {n for n in expected if n.startswith(directory + "/")}, "import/discovery membership drift")
    return digest(canonical(result))

def git_blob_oid(data):
    # This fixed predecessor uses SHA-1 Git object IDs, not a security/password hash.
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()

def verify_old(old, manifest):
    require(stat.S_ISDIR(old.lstat().st_mode), "OLD absent or not a directory")
    expected_dirs = {"."}
    for name in manifest["files"]:
        expected_dirs.update(q.as_posix() for q in relative(name).parents)
    actual_files, actual_dirs = set(), {"."}
    require(stat.S_IMODE(old.stat().st_mode) == 0o555, "OLD root mode drift")
    for p in old.rglob("*"):
        info = p.lstat()
        name = p.relative_to(old).as_posix()
        if stat.S_ISDIR(info.st_mode):
            require(stat.S_IMODE(info.st_mode) == 0o555, "OLD directory mode drift")
            actual_dirs.add(name)
        elif stat.S_ISREG(info.st_mode):
            actual_files.add(name)
        else:
            require(False, "unsupported OLD member: " + name)
    require(actual_files == set(manifest["files"]) and actual_dirs == expected_dirs, "OLD tree membership mismatch")
    observed = {}
    for name, entry in manifest["files"].items():
        p = old / relative(name)
        b = regular(p)
        require(entry["git_mode"] in {"100644", "100755"}, "unsupported baseline mode")
        require(digest(b) == entry["sha256"] and len(b) == entry["size"] and git_blob_oid(b) == entry["oid"], "OLD content/blob identity drift")
        require(stat.S_IMODE(p.stat().st_mode) == (0o555 if entry["git_mode"] == "100755" else 0o444), "OLD mode drift")
        observed[name] = {"path": name, "sha256": digest(b), "size_bytes": len(b)}
    names = manifest["literal_paths"]["checkout-1"]
    require(len(names) == len(set(names)) and all(n in observed for n in names), "invalid checkout inventory membership")
    require(digest(("\n".join(names) + "\n").encode()) == manifest["path_list_sha256"]["checkout-1"], "checkout path hash drift")
    inventory = {"record_type": "release-inventory", "schema_version": 1, "inventory_id": "checkout-1", "entries": [observed[n] for n in names]}
    require(manifest["base"] == BASE and digest(canonical(inventory)) == manifest["release_sha256"] == OLD_RELEASE, "wrong old release identity")
    # manifest.tree is historical metadata; it is not a separately attested tree seal.
    return digest(canonical(manifest))

SYSTEM_GIT_CONFIG = {
    "path": "/Library/Developer/CommandLineTools/usr/share/git-core/gitconfig",
    "sha256": "d9edd909b86735d18b57095355e8f16a67f2a557d02431bb223854291eb6e653",
    "entries": {"credential.helper": "osxkeychain", "init.defaultbranch": "main"},
}
BOOTSTRAP = 'import runpy,sys; p=sys.argv.pop(1); f=sys.argv.pop(1); sys.path.append(p); runpy.run_path(p+"/"+f,run_name="__main__")'

def require_isolated():
    require(sys.flags.isolated and sys.flags.ignore_environment and sys.flags.no_site and sys.flags.no_user_site and sys.dont_write_bytecode, "requires isolated no-site -I -S -B bootstrap")

def python_command(c, p, script, *args, optimized=False):
    require(script in {"controller.py", "acquire.py", "canary.py", "observer.py", "delegation_observer.py", "runner.py", "selfcheck.py", "calibration.py"}, "unlisted bootstrap script")
    return [c["runtime"]["path"], "-I", "-S", "-B", *(["-O"] if optimized else []), "-c", BOOTSTRAP, str(p["controls"]), script, *map(str, args)]

def verify_source_root(root, expected):
    # Immediate names/types only; existing non-src/tests subtrees are not sealed.
    require(isinstance(expected, dict) and expected, "missing source root inventory")
    for name, kind in expected.items():
        require(isinstance(name, str) and len(relative(name).parts) == 1 and
                name not in (".", "..") and kind in ("file", "directory"), "source root inventory entry")
    actual = {}
    for entry in root.iterdir():
        mode = entry.lstat().st_mode
        require(stat.S_ISREG(mode) or stat.S_ISDIR(mode), "linked/special source root entry")
        actual[entry.name] = "directory" if stat.S_ISDIR(mode) else "file"
    require(actual == expected, "source root membership/type drift")


def campaign_limits_disabled(policy):
    keys = {"schema", "root", "attempts", "total_seconds", "pair_seconds", "corrections"}
    if type(policy.get("schema")) is int and policy["schema"] == 2:
        require(set(policy) == keys | {"approval_sha256"}
                and all(policy[k] is None for k in ("attempts", "total_seconds", "pair_seconds", "corrections"))
                and isinstance(policy["approval_sha256"], str) and len(policy["approval_sha256"]) == 64
                and all(x in "0123456789abcdef" for x in policy["approval_sha256"]), "campaign shape/bounds")
        return True
    require(set(policy) == keys and type(policy.get("schema")) is int and policy["schema"] == 1
            and policy["total_seconds"] == 28800 and policy["pair_seconds"] in (7200,10800)
            and type(policy["corrections"]) is int and policy["corrections"] in (2,3,4,5,6,7,8,9), "campaign shape/bounds")
    return False


def attempt_number(name):
    require(isinstance(name, str) and name.startswith("r") and name[1:].isascii()
            and name[1:].isdigit(), "campaign attempt name")
    number = int(name[1:])
    require(name == "r%02d" % number, "campaign attempt name")
    return number


def config(path, expected_sha):
    path = unlinked_path(path)
    require(digest(regular(path)) == expected_sha, "invocation identity mismatch")
    c = read_json(path)
    keys = {"schema", "phase", "paths", "runtime", "git", "source_files", "controls", "selection", "collection_sha256", "factory", "source_digest", "git_system_config", "source_root_entries"}
    require(set(c) == keys | ({"predecessor_files", "artifact_files"} if c.get("schema") == 4 else set()) | ({"prior_evidence"} if c.get("schema") == 4 and "prior_evidence" in c else set()), "invocation keys")
    require(type(c["schema"]) is int and ((c["schema"] == 3 and c["phase"] in ("base", "entry")) or (c["schema"] == 4 and c["phase"] == "delegation")), "invocation version/phase")
    require(set(c["paths"]) == {"source", "controls", "root", "old", "exec", "common_git"} | ({"predecessor", "artifacts"} if c["schema"] == 4 else set()), "path keys")
    paths = {k: unlinked_path(v, exists=k in ("source", "controls", "common_git", "predecessor", "artifacts")) for k, v in c["paths"].items()}
    require(paths["old"] == paths["root"] / "old" and paths["exec"] == paths["root"] / "exec", "fixed execution layout")
    campaign_path = paths["controls"] / "campaign.json"
    campaign = read_json(campaign_path) if campaign_path.exists() else None
    if campaign is None:
        require(paths["root"].parent.name == "agent-worktrees", "unapproved execution root")
    else:
        accounting_only = campaign_limits_disabled(campaign)
        home = unlinked_path(campaign["root"])
        require(home.parent.parent.name == "agent-artifacts" and home.name == "implementation", "campaign storage root")
        if accounting_only:
            attempt_number(paths["root"].parent.name)
            require(paths["root"].parent.parent == home and paths["root"].name in {"current", "retained"}, "campaign lane root")
        else:
            require(campaign["attempts"] == ["r%02d" % n for n in range(campaign["corrections"]+1)], "fixed campaign attempts")
            require(paths["root"] in {home / attempt / lane for attempt in campaign["attempts"] for lane in ("current", "retained")}, "campaign lane root")
        require((paths["root"].name == "current") == (c["schema"] == 4), "lane/schema mismatch")
    for readonly in (paths["source"], paths["controls"], paths["old"], path, *[paths[k] for k in ("predecessor", "artifacts") if k in paths]):
        require(not readonly.is_relative_to(paths["exec"]) and not paths["exec"].is_relative_to(readonly), "read/write overlap")
    require(campaign is not None or paths["controls"].is_relative_to(paths["source"]), "controls outside source scope")
    for p in (paths["root"], *paths["root"].parents):
        require(not (p / ".git").exists() and not (p / ".hrn").exists(), "execution target has repository/authority ancestor")
    require({q.name for q in paths["controls"].glob("*.py")} == {n for n in c["controls"] if n.endswith(".py") and "/" not in n}, "control module membership drift")
    require(not list(paths["controls"].rglob("*.pyc")), "unexpected control bytecode")
    require({q.relative_to(paths["controls"]).as_posix() for q in paths["controls"].rglob("*") if q.is_file()} == set(c["controls"]), "control file membership drift")
    for name, h in c["controls"].items():
        require(digest(regular(paths["controls"] / relative(name))) == h, "control drift: " + name)
    for tool in (c["runtime"], c["git"]):
        require(set(tool) == {"path", "sha256", "version"}, "tool identity keys")
        require(digest(regular(unlinked_path(tool["path"]))) == tool["sha256"], "tool binary drift")
    require(c["git_system_config"] == SYSTEM_GIT_CONFIG, "unapproved system Git configuration")
    system_config = unlinked_path(c["git_system_config"]["path"])
    require(digest(regular(system_config)) == c["git_system_config"]["sha256"], "system Git configuration drift")
    require(file_map(paths["source"], c["source_files"]) == c["source_digest"], "source digest mismatch")
    verify_source_root(paths["source"], c["source_root_entries"])
    if campaign is not None:
        actual = {q.relative_to(paths["source"]).as_posix() for q in paths["source"].rglob("*") if q.is_file()}
        require(actual == set(c["source_files"]), "frozen source membership drift")
        require(not any(q.is_symlink() for q in paths["source"].rglob("*")), "linked frozen source member")
    require(isinstance(c["selection"], list) and all(isinstance(x, str) for x in c["selection"]), "selected IDs must be literal list")
    require(len(c["selection"]) == len(set(c["selection"])), "duplicate selected IDs")
    require(c["factory"] is (c["phase"] in {"entry", "delegation"}), "phase/factory mismatch")
    if c["schema"] == 4:
        links=c.get("prior_evidence",{})
        require(isinstance(links,dict),"prior evidence map")
        for name,refs in links.items():
            require(name in {lane+"/"+mode+"/final" for lane in ("current","retained") for mode in ("complete-normal","complete-parent-O")},"prior evidence phase")
            require(isinstance(refs,dict) and set(refs)=={"invocation","result","parent_result"},"prior evidence keys")
            for item in refs.values():
                require(isinstance(item,dict) and set(item)=={"path","sha256"} and isinstance(item["path"],str)
                        and isinstance(item["sha256"],str) and len(item["sha256"])==64
                        and all(ch in "0123456789abcdef" for ch in item["sha256"]),"prior evidence reference")
        # Reference bytes are validated only by the parent. The child gains no
        # cross-root reads by receiving these literal, non-authority pointers.
        file_map(paths["predecessor"], c["predecessor_files"])
        file_map(paths["artifacts"], c["artifact_files"])
        for key, inventory in (("predecessor", c["predecessor_files"]), ("artifacts", c["artifact_files"])):
            actual = set()
            for member in paths[key].rglob("*"):
                require(not member.is_symlink(), "linked frozen input")
                require(member.is_dir() or member.is_file(), "special frozen input")
                if member.is_file(): actual.add(member.relative_to(paths[key]).as_posix())
            require(actual == set(inventory), "frozen input membership drift")
    return c, paths

def exclusive_json(path, value):
    with Path(path).open("xb") as f:
        f.write(canonical(value))
        f.flush()
        os.fsync(f.fileno())
