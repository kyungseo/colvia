"""Source-only macOS distribution preparation. No fetch, install or publication."""
from __future__ import annotations

import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import posixpath
import re
import shlex
import stat
import tarfile

ARCHIVE = "cpython-3.14.10+20261026-aarch64-apple-darwin-install_only.tar.gz"
ARCHIVE_SHA = "30a18bcb9ab75e485b4bf4e5d783dde165571e7e42c56dff47a2d2c5345183a4"
ARCHIVE_SIZE = 26891793
FULL = "cpython-3.14.10+20261026-aarch64-apple-darwin-pgo+lto-full.tar.zst"
FULL_SHA = "137db511241f7693ddc57586af1744c7b6375982ab4c31c4a82d10115657d462"
OBJECTS_SHA = "3e730af422bdfa77dff666ac882726ce12e87d7cceae6b39c17775b2d88e2510"
FILES_SHA = "ed7b15de8cf79458c2d0c06713424bcc48326f1c59fe454844e1c8fa1400fe89"
RUNTIME_ID = "e3d42cd0b305583e46e16d5265e3b6ac24a01ef9ee32a08418e1be5965db816f"
ROOT_EXPRESSION = '"${HOME:?}/Library/Application Support/Colvia"'
GRAMMAR = re.compile(r"[A-Za-z0-9_./+@=,%-]+\Z")


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def canonical(value) -> bytes:
    return (json.dumps(value, sort_keys=True, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode()


def regular(path: Path) -> bytes:
    for parent in (path.parent, *path.parent.parents):
        if not stat.S_ISDIR(parent.lstat().st_mode):
            raise ValueError("non-directory ancestor")
    before = path.lstat()
    if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1:
        raise ValueError("regular unshared file required")
    raw = path.read_bytes()
    after = path.lstat()
    fields = lambda s: (s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns, s.st_ctime_ns)
    if fields(before) != fields(after):
        raise ValueError("input drift")
    return raw


def runtime_catalog(archive: Path) -> tuple[bytes, bytes]:
    raw = regular(archive)
    if len(raw) != ARCHIVE_SIZE or digest(raw) != ARCHIVE_SHA:
        raise ValueError("unqualified runtime archive")
    entries, folded, directories, checks = {}, set(), {"."}, {}
    with tarfile.open(fileobj=io.BytesIO(raw), mode="r:gz") as stream:
        for member in stream:
            name = member.name
            if (not GRAMMAR.fullmatch(name) or not name.startswith("python/")
                    or any(part in ("", ".", "..") for part in name.split("/"))
                    or member.mode & 0o7000 or name.casefold() in folded
                    or not (member.isfile() or member.issym() or member.isdir())):
                raise ValueError("unsafe archive member")
            folded.add(name.casefold())
            relative = name.removeprefix("python/")
            for parent in PurePosixPath(relative).parents:
                directories.add("." if str(parent) == "." else "./" + str(parent))
            key = "./" + relative
            if member.isfile():
                mode = "500" if member.mode & 0o111 else "400"
                entries[key] = "Regular File|" + mode + "|" + key + "|"
                checks[relative] = digest(stream.extractfile(member).read())
            elif member.issym():
                link = member.linkname
                target = posixpath.normpath(posixpath.join(posixpath.dirname(relative), link))
                if (not GRAMMAR.fullmatch(link) or link.startswith("/")
                        or target == ".." or target.startswith("../")):
                    raise ValueError("unsafe runtime link")
                entries[key] = "Symbolic Link|-|" + key + "|" + link
            else:
                directories.add(key)
    if directories & entries.keys():
        raise ValueError("member is also an ancestor")
    for name in directories:
        entries[name] = "Directory|500|" + name + "|"
    # No path component may be a symbolic link, even one with an in-tree target.
    objects = ("\n".join(sorted(entries.values())) + "\n").encode()
    hashes = ("".join(checks[name] + "  " + name + "\n" for name in sorted(checks))).encode()
    if (digest(objects) != OBJECTS_SHA or digest(hashes) != FILES_SHA
            or digest(objects + hashes) != RUNTIME_ID):
        raise ValueError("tree differs from fixed S0 qualification")
    return objects, hashes


def runtime_slot(verifier_sha: str) -> str:
    """Keep each pinned verifier with its tree without changing older entries."""
    return digest((RUNTIME_ID + ":" + verifier_sha).encode("ascii"))


def header(verifier_sha: str, *, fixture_root: Path | None = None) -> bytes:
    if not re.fullmatch("[0-9a-f]{64}", verifier_sha):
        raise ValueError("invalid verifier pin")
    if fixture_root is not None and not fixture_root.is_absolute():
        raise ValueError("absolute fixture root required")
    root = ROOT_EXPRESSION if fixture_root is None else shlex.quote(str(fixture_root))
    # First enter an empty environment. The shell body is literal, not evaluated
    # from argv, a mutable catalog or an environment-selected Python executable.
    body = f'''set -euo pipefail
store={root}
entry=$1; shift
runtime="$store/runtimes/{runtime_slot(verifier_sha)}"
fail() {{ printf '%s\\n' 'Colvia: restore the exact managed runtime with its verified bootstrap.' >&2; exit 65; }}
pin() {{
 [ -f "$1" ] && [ ! -L "$1" ] || fail
 [ "$(/usr/bin/stat -f %l "$1")" = 1 ] || fail
 value=$(/usr/bin/shasum -a 256 < "$1") || fail
 [ "${{value%% *}}" = "$2" ] || fail
}}
pin "$runtime/verify-tree.sh" {verifier_sha}
pin "$runtime/objects.txt" {OBJECTS_SHA}
pin "$runtime/files.sha256" {FILES_SHA}
/bin/bash "$runtime/verify-tree.sh" "$runtime/python" "$runtime/objects.txt" "$runtime/files.sha256" "$store/checks" < /dev/null || fail
export TMPDIR="$store/checks" XDG_CONFIG_HOME="$store/checks/config"
export GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null GIT_ATTR_NOSYSTEM=1 GIT_TERMINAL_PROMPT=0
exec "$runtime/python/bin/python3.14" -I -B "$entry" "$@"
exit 65'''
    home_check = "case \"${HOME-}\" in /*) ;; *) printf '%s\\n' 'Colvia: HOME must be an absolute path.' >&2; exit 65 ;; esac\n"
    shell = home_check + 'exec /usr/bin/env -i HOME="${HOME:?}" PATH=/usr/bin:/bin LC_ALL=C PYTHONDONTWRITEBYTECODE=1 /bin/bash -c ' + shlex.quote(body) + ' colvia "$0" "$@"\nexit 65\n'
    # Shell sees a here-compatible quoted no-op; Python sees one module docstring.
    return ('#!/bin/sh\n""":"\n' + shell + '\":\"\"\"\n').encode("ascii")


def tar_bytes(files: dict[str, bytes], executable: set[str]) -> bytes:
    output = io.BytesIO()
    # Deterministic uncompressed tar: compressed runtime stays byte-identical.
    with tarfile.open(fileobj=output, mode="w", format=tarfile.USTAR_FORMAT) as stream:
        for name, raw in sorted(files.items()):
            if (not GRAMMAR.fullmatch(name) or name.startswith("/")
                    or any(p in ("", ".", "..") for p in name.split("/"))):
                raise ValueError("unsafe distribution member")
            info = tarfile.TarInfo(name)
            info.size, info.mode, info.mtime = len(raw), 0o500 if name in executable else 0o400, 0
            stream.addfile(info, io.BytesIO(raw))
    return output.getvalue()


def licenses(full_archive: Path) -> dict[str, bytes]:
    raw = regular(full_archive)
    if digest(raw) != FULL_SHA:
        raise ValueError("full metadata archive identity")
    result = {}
    with tarfile.open(fileobj=io.BytesIO(raw), mode="r:zst") as stream:
        for item in stream:
            if item.name == "python/PYTHON.json" or item.name.startswith("python/licenses/"):
                if item.isfile():
                    if not GRAMMAR.fullmatch(item.name) or item.size > 1024 * 1024:
                        raise ValueError("unsafe license member")
                    result[item.name.removeprefix("python/")] = stream.extractfile(item).read()
    if "PYTHON.json" not in result or len(result) < 10:
        raise ValueError("missing upstream metadata/licenses")
    return result


def bootstrap(manifest: dict, manifest_sha: str, *, origin: str,
              fixture_root: Path | None = None, fixture_assets: Path | None = None) -> bytes:
    if fixture_root is not None and not fixture_root.is_absolute():
        raise ValueError("absolute fixture root required")
    root = ROOT_EXPRESSION if fixture_root is None else shlex.quote(str(fixture_root))
    if (fixture_root is None) != (fixture_assets is None):
        raise ValueError("fixture root/assets must be rendered together")
    if not re.fullmatch(r"https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/releases/download/[A-Za-z0-9_.-]+", origin):
        raise ValueError("fixed GitHub release origin required")
    if digest(canonical(manifest)) != manifest_sha:
        raise ValueError("manifest identity mismatch")
    if fixture_assets is not None and not fixture_assets.is_absolute():
        raise ValueError("absolute fixture assets required")
    if fixture_assets is None:
        retrieve = f'''url={shlex.quote(origin)}/$name
 for redirects in 0 1 2 3; do
  case "$url" in https://github.com/*|https://release-assets.githubusercontent.com/*) ;; *) fail '다운로드 제공처가 다릅니다.' ;; esac
  code=$(/usr/bin/curl -q --silent --show-error --proto '=https' --proto-redir '=https' --max-redirs 0 --max-time 120 --max-filesize "$size" --dump-header "$stage/headers" --output "$target" --write-out '%{{http_code}}' "$url") || fail '다운로드를 완료하지 못했습니다. 준비 자료를 보존했습니다.'
  if [ "$code" = 200 ]; then break; fi
  case "$code" in 301|302|303|307|308) ;; *) fail '배포 파일을 가져오지 못했습니다.' ;; esac
  url=$(/usr/bin/awk 'tolower($1)=="location:" {{sub(/\\r$/, "", $2); print $2}}' "$stage/headers")
 done
 [ "$code" = 200 ] || fail '다운로드 이동 횟수를 초과했습니다.'
'''
    else:
        retrieve = f'/bin/cp {shlex.quote(str(fixture_assets))}/"$name" "$target"\n'
    fetches = []
    assets = {"manifest.json": {"sha256": manifest_sha, "size": len(canonical(manifest))}, **manifest["assets"]}
    for name, item in assets.items():
        fetches.append(f'fetch {shlex.quote(name)} {item["sha256"]} {item["size"]}')
    body = f'''set -Eeuo pipefail
store={root}
bootstrap_path=$1; shift
fail() {{ printf '%s\\n' "Colvia: $1" >&2; exit 65; }}
trap 'fail "준비를 완료하지 못했습니다. 현재 자료를 보존하고 오류를 확인해 주세요."' ERR
case "$store" in /*) ;; *) fail '저장 위치는 절대 경로여야 합니다.' ;; esac
[ "$(/usr/bin/uname -s)" = Darwin ] && [ "$(/usr/bin/uname -m)" = arm64 ] || fail 'macOS arm64 배포본이 필요합니다.'
if [ "$#" = 0 ]; then
 printf '%s\\n' 'Colvia와 전용 Python을 준비합니다. 프로젝트 연결은 그 뒤에 별도로 확인합니다.' "저장 위치: $store" '보존: 프로젝트, Work, 승인·복구 기록, shell 설정' '공급: 고정된 CPython 3.14.10 arm64 및 확인한 배포본'
 printf '적용: /bin/sh %q --apply --confirm %s\\n' "$bootstrap_path" {manifest_sha}
 exit 0
fi
[ "$#" = 3 ] && [ "$1" = --apply ] && [ "$2" = --confirm ] && [ "$3" = {manifest_sha} ] || fail '표시된 배포 확인값이 필요합니다.'
parent=$store
while [ "$parent" != / ]; do
 [ ! -L "$parent" ] || fail '저장 위치에 링크가 있습니다.'
 if [ -e "$parent" ]; then [ -d "$parent" ] || fail '저장 위치를 확인해 주세요.'; fi
 parent=${{parent%/*}}; [ -n "$parent" ] || parent=/
done
umask 077
/bin/mkdir -p "$store/staging" "$store/checks"
/bin/mkdir "$store/activation.lock" || fail '다른 설치 또는 중단된 설치의 잠금을 확인해 주세요.'
trap '/bin/rmdir "$store/activation.lock"' EXIT
stage=$(/usr/bin/mktemp -d "$store/staging/prepare.XXXXXXXX")
# Unique stage survives a failure. Never infer success from its presence.
fetch() {{
 name=$1; expected=$2; size=$3; target="$stage/$name"
 {retrieve}
 [ -f "$target" ] && [ ! -L "$target" ] || fail '일반 배포 파일이 필요합니다.'
 [ "$(/usr/bin/stat -f %l "$target")" = 1 ] || fail '공유된 배포 파일을 거절했습니다.'
 [ "$(/usr/bin/stat -f %z "$target")" = "$size" ] || fail '배포 파일 크기가 다릅니다.'
 actual=$(/usr/bin/shasum -a 256 < "$target")
 [ "${{actual%% *}}" = "$expected" ] || fail '배포 파일 해시가 다릅니다.'
}}
{chr(10).join(fetches)}
/bin/mkdir "$stage/runtime"
/bin/mv "$stage/objects.txt" "$stage/files.sha256" "$stage/verify-tree.sh" "$stage/runtime/"
# The maintainer inspected this exact pinned tar; reject any changed archive.
/usr/bin/tar -xzf "$stage/{ARCHIVE}" --no-same-owner -C "$stage/runtime"
/usr/bin/find -P "$stage/runtime/python" -type f -perm +111 -exec /bin/chmod 500 {{}} +
/usr/bin/find -P "$stage/runtime/python" -type f ! -perm +111 -exec /bin/chmod 400 {{}} +
/usr/bin/find -P "$stage/runtime/python" -type d -exec /bin/chmod 500 {{}} +
/bin/chmod 400 "$stage/runtime/objects.txt" "$stage/runtime/files.sha256" "$stage/runtime/verify-tree.sh"
/bin/bash "$stage/runtime/verify-tree.sh" "$stage/runtime/python" "$stage/runtime/objects.txt" "$stage/runtime/files.sha256" "$store/checks" < /dev/null || fail 'Python 실행 전 검증을 완료하지 못했습니다.'
export TMPDIR="$store/checks" XDG_CONFIG_HOME="$store/checks/config"
export GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null GIT_ATTR_NOSYSTEM=1 GIT_TERMINAL_PROMPT=0
"$stage/runtime/python/bin/python3.14" -I -B "$stage/colvia-manage" --bootstrap-activate "$stage" < /dev/null
'''
    # No environment switch can bypass sanitization, and production has no fixture input.
    return ("#!/bin/sh\ncase \"${HOME-}\" in /*) ;; *) printf '%s\\n' 'Colvia: HOME must be an absolute path.' >&2; exit 65 ;; esac\n"
            + 'exec /usr/bin/env -i HOME="${HOME:?}" PATH=/usr/bin:/bin LC_ALL=C PYTHONDONTWRITEBYTECODE=1 /bin/bash -c '
            + shlex.quote(body) + ' colvia-bootstrap "$0" "$@"\n').encode()


def build_notice_app(source, output, *, fixture_root):
    """Embed signed bundle bytes in the same retained manager as their publication recipe."""
    import base64
    import plistlib
    import subprocess
    app = output / "notification-build" / "ColviaWork.app"
    contents = app / "Contents"
    binary = contents / "MacOS" / "ColviaWork"
    binary.parent.mkdir(parents=True)
    suffix = ".fixture." + digest(str(fixture_root).encode())[:16] if fixture_root else ""
    info = {"CFBundleIdentifier":"org.colvia.work.notice"+suffix,"CFBundleName":"Colvia Work",
            "CFBundleDisplayName":"Colvia","CFBundleExecutable":binary.name,"CFBundlePackageType":"APPL",
            "CFBundleVersion":"1","CFBundleShortVersionString":"1.0","NSPrincipalClass":"NSApplication",
            "LSMinimumSystemVersion":"13.0"}
    (contents / "Info.plist").write_bytes(plistlib.dumps(info))
    subprocess.run(["/usr/bin/xcrun","clang","-arch","arm64","-mmacosx-version-min=13.0","-fobjc-arc",
                    "-framework","AppKit","-framework","UserNotifications","-framework","CoreServices",
                    str(source / "distribution/notification/WorkWindow.m"),"-o",str(binary)],check=True)
    subprocess.run(["/usr/bin/codesign","--force","--sign","-",str(app)],check=True)
    subprocess.run(["/usr/bin/codesign","--verify","--strict",str(app)],check=True)
    return {f.relative_to(app).as_posix():base64.b64encode(regular(f)).decode("ascii")
            for f in sorted(app.rglob("*")) if f.is_file()}


def prepare(source: Path, supply: Path, output: Path, *, version: str, origin: str,
            fixture_root: Path | None = None) -> dict:
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,63}", version):
        raise ValueError("explicit version required")
    if output.exists() or output.is_symlink() or source == output or source in output.parents:
        raise ValueError("new external output required")
    from hv2ref.product import workspace_candidate, OFFICIAL_V2_MANAGED_PATHS
    baseline = workspace_candidate(source)
    if baseline["release_ref"]["inventory_id"] != "continuation-1":
        raise ValueError("common source required")
    objects, checksums = runtime_catalog(supply / ARCHIVE)
    notice_files = licenses(supply / FULL)
    verifier = regular(source / "distribution/verify-macos-tree.sh")
    launch_header = header(digest(verifier), fixture_root=fixture_root)
    output.mkdir(mode=0o700, parents=True)
    profile_info, packaged, executable = {}, {}, set()
    # Temporary candidates are retained build inputs, not a separate source archive.
    for profile, paths in (("continuation-1", tuple(baseline["payload"])),
                           ("official-execution-2", OFFICIAL_V2_MANAGED_PATHS)):
        prepared = output / "prepared" / profile
        prepared.mkdir(parents=True, mode=0o700)
        for name in paths:
            raw = regular(source / name)
            if name == "colvia":
                raw = raw.split(b"\n", 1)[1]
                raw = raw.replace(b'WORKSPACE_INVENTORY_ID = "continuation-1"',
                                  ('WORKSPACE_INVENTORY_ID = "' + profile + '"').encode(), 1)
                raw = raw.replace(b'MANAGED_MACOS_RUNTIME = False', b'MANAGED_MACOS_RUNTIME = True', 1)
                raw = launch_header + raw
                compile(raw, "colvia", "exec")
            path = prepared / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(raw); path.chmod(0o500 if name == "colvia" else 0o400)
        candidate = workspace_candidate(prepared)
        ref = candidate["release_ref"]
        profile_info[profile] = {"release": ref, "runtime_input_diagnostic": True, "files": {name: digest(raw) for name, raw in candidate["payload"].items()}}
        packaged.update({ref["id"] + "/" + name: raw for name, raw in candidate["payload"].items()})
        executable.add(ref["id"] + "/colvia")
    product = tar_bytes(packaged, executable)
    notices = tar_bytes(notice_files, set())
    runtime_files = {"verify-tree.sh": digest(verifier), "objects.txt": OBJECTS_SHA, "files.sha256": FILES_SHA}
    config = {"version": version, "fixture_root": str(fixture_root) if fixture_root else None,
              "profiles": profile_info, "runtime_id": runtime_slot(digest(verifier)), "runtime_files": runtime_files,
              "product_archive_sha256": digest(product), "notices_sha256": digest(notices)}
    config["notice_app"] = build_notice_app(source, output, fixture_root=fixture_root)
    manager_source = regular(source / "distribution/manager.py")
    manager_source = b"from __future__ import annotations\n" + manager_source.split(b"from __future__ import annotations\n", 1)[1]
    if manager_source.count(b"CONFIG: dict = {}") != 1:
        raise ValueError("manager config marker")
    manager = launch_header + manager_source.replace(b"CONFIG: dict = {}", ("CONFIG: dict = " + repr(config)).encode(), 1)
    compile(manager, "colvia-manage", "exec")
    assets = {"product.tar": product, "notices.tar": notices, "objects.txt": objects,
              "files.sha256": checksums, "verify-tree.sh": verifier, "colvia-manage": manager,
              ARCHIVE: regular(supply / ARCHIVE)}
    manifest = {"schema": 1, "version": version, "platform": "darwin", "architecture": "arm64",
                "python": "3.14.10", "gil": "enabled", "runtime_id": runtime_slot(digest(verifier)),
                "runtime_catalog_id": RUNTIME_ID,
                "supply": {"provider": "astral-sh/python-build-standalone", "tag": "20261026",
                           "archive_sha256": ARCHIVE_SHA, "metadata_sha256": FULL_SHA,
                           "recipe": "upstream bytes unchanged; directories 500; executable files 500; other files 400"},
                "fixture": fixture_root is not None, "profiles": {p: value["release"] for p, value in profile_info.items()},
                "assets": {name: {"sha256": digest(raw), "size": len(raw)} for name, raw in assets.items()}}
    raw_manifest = canonical(manifest)
    assets["manifest.json"] = raw_manifest
    assets["bootstrap.sh"] = bootstrap(manifest, digest(raw_manifest), origin=origin, fixture_root=fixture_root,
                                        fixture_assets=output if fixture_root else None)
    for name, raw in assets.items():
        path = output / name
        path.write_bytes(raw); path.chmod(0o500 if name in ("bootstrap.sh", "colvia-manage") else 0o400)
    (output / "SHA256SUMS").write_text("".join(digest(raw) + "  " + name + "\n" for name, raw in sorted(assets.items())))
    if workspace_candidate(source) != baseline:
        raise ValueError("source changed during preparation")
    return {"manifest_sha256": digest(raw_manifest), "bootstrap_sha256": digest(assets["bootstrap.sh"]),
            "profiles": manifest["profiles"], "fixture": manifest["fixture"], "published": False, "installed": False}
