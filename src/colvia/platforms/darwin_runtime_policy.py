"""Explicit Darwin runtime policy binding; does not launch or grant authority.

A trusted Driver owns executable/config identity, authentication, RPC admission,
process lifetime and concurrent-path exclusion. This module checks a fixed
policy and existing canonical paths immediately before that Driver launches.
It neither installs an adapter nor claims protection against a hostile same-UID
process changing paths after validation.
"""
from pathlib import Path
from ..codec import RecordError
import hashlib
import os
import re
import stat

POLICY_SHA256 = "06da01c3130900a9b550185e5201d2dac494833ee8e1d561168da6671298bfe2"
PARAMETERS = frozenset({"BIN", "PYROOT", "RUNTIME", "SESSION", "CODEX_CONFIG", "CODEX_AUTH", "INSTALLATION_ID", "CODEX_RULES_DIR", "CODEX_RULES_FILE", "GLOBAL_INSTRUCTIONS", "CODE_MODE_HOST"})
DIRECTORIES = frozenset({"PYROOT", "RUNTIME", "SESSION", "CODEX_RULES_DIR"})


class PolicyRefusal(RecordError):
    """A supplied path or fixed policy cannot be safely bound."""


def require(condition, reason):
    if not condition:
        raise PolicyRefusal("execution-runtime-"+reason)


def canonical_existing(value, directory=None):
    require(type(value) is str and value and "\x00" not in value and "\n" not in value and "\r" not in value, "path-value")
    path = Path(value)
    require(path.is_absolute() and str(path) == value and ".." not in path.parts, "path-spelling")
    try:
        require(path.resolve(strict=True) == path, "path-alias")
        for part in (path, *path.parents):
            require(not part.is_symlink(), "path-symlink")
        info = path.lstat()
        require(stat.S_ISDIR(info.st_mode) if directory is True else
                stat.S_ISREG(info.st_mode) if directory is False else
                stat.S_ISDIR(info.st_mode) or stat.S_ISREG(info.st_mode), "path-kind")
    except OSError as error:
        raise PolicyRefusal("execution-runtime-path-unavailable") from error
    return path


def overlaps(left, right):
    return left == right or left in right.parents or right in left.parents


def prepare_launch(bindings, arguments, *, protected, policy_path):
    """Return an argv array and identity, without reading credential contents.

    protected must enumerate the trusted Driver's document/authority/journal
    boundaries. Metadata remains readable under the policy; content and effects
    are what the live canary checks. Callers must preserve these paths until exit.
    """
    require(type(bindings) is dict and set(bindings) == PARAMETERS, "parameter-set")
    require(type(arguments) in (list, tuple) and all(type(x) is str and "\x00" not in x for x in arguments), "argument-array")
    require(type(protected) in (list, tuple) and bool(protected), "protected-set")
    paths = {name: canonical_existing(value, name in DIRECTORIES) for name, value in bindings.items()}
    guarded = [canonical_existing(value) for value in protected]
    require(paths["CODEX_RULES_FILE"].parent == paths["CODEX_RULES_DIR"], "rules-file-parent")
    require(paths["SESSION"] != paths["RUNTIME"] and paths["RUNTIME"] in paths["SESSION"].parents, "session-containment")
    for name in ("RUNTIME", "SESSION"):
        info = paths[name].stat()
        require(info.st_uid == os.getuid() and stat.S_IMODE(info.st_mode) & 0o077 == 0, "runtime-private")
    require(os.access(paths["BIN"], os.X_OK), "binary-executable")
    require(stat.S_IMODE(paths["CODE_MODE_HOST"].stat().st_mode) & 0o111 != 0, "helper-not-executable")
    files = [paths[name] for name in PARAMETERS - DIRECTORIES]
    require(len({(p.stat().st_dev, p.stat().st_ino) for p in files}) == len(files), "file-alias")
    for name in ("CODEX_CONFIG", "CODEX_AUTH", "INSTALLATION_ID"):
        require(not any(overlaps(paths[name], paths[d]) for d in DIRECTORIES), "credential-root-overlap")
    fixed = canonical_existing(str(policy_path), False)
    try:
        raw = fixed.read_bytes()
    except OSError as error:
        raise PolicyRefusal("execution-runtime-policy-unavailable") from error
    require(hashlib.sha256(raw).hexdigest() == POLICY_SHA256, "policy-drift")
    text = raw.decode("utf-8")
    require(set(re.findall(r'\(param "([A-Z_]+)"\)', text)) == PARAMETERS, "policy-parameters")
    # Inspect static grants as well as dynamic roots. Do not silently accept a
    # protected path that is readable through an OS/library or runtime grant.
    static = [Path(value).resolve() for value in re.findall(r'\((?:subpath|literal) "([^"\n]+)"\)', text)
              if value != "/"]
    for guard in guarded:
        require(not any(overlaps(guard, p) for p in [*paths.values(), *static, fixed]), "protected-overlap")
        if guard.is_file():
            require(not any(p.exists() and p.is_file() and os.path.samefile(guard, p) for p in [*files, fixed, *static]), "protected-file-alias")
    argv = ["/usr/bin/sandbox-exec"]
    for name in sorted(PARAMETERS):
        argv += ["-D", name + "=" + str(paths[name])]
    argv += ["-f", str(fixed), str(paths["BIN"]), *arguments]
    return {"argv": argv, "policy_sha256": POLICY_SHA256,
            "bindings": {name: str(paths[name]) for name in sorted(PARAMETERS)},
            "protected": [str(path) for path in guarded]}

