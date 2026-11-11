"""Build a private Windows bootstrap, offline, from an explicitly prepared windows-2 tree."""
import argparse
import hashlib
import io
import json
import os
from pathlib import Path, PureWindowsPath
import shutil
import subprocess
import sys
from typing import NamedTuple
import zipfile

SOURCE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SOURCE / "src"))
from hv2ref.product import workspace_candidate

class PythonTarget(NamedTuple):
    machine: int
    size: int
    sha256: str


# Official CPython 3.14.7 embeddable ZIPs; the Go target selects one complete row.
TARGETS = {
    "arm64": PythonTarget(0xAA64, 11980260, "f6773983c8959d4281e48c4540cb0bdd23e42391e4e951ce17e7ceb52658f21c"),
    "amd64": PythonTarget(0x8664, 12673227, "d297e5ff019966817ad8502465176139f2d3d840fa4ed84b13bed399a6ab1f15"),
}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def build(prepared, upstream, output, fixture, architecture="arm64"):
    target = TARGETS[architecture]
    archive_name = f"python-3.14.7-embed-{architecture}.zip"
    candidate = workspace_candidate(prepared)
    if candidate["release_ref"]["inventory_id"] != "windows-2":
        raise ValueError("requires prepared windows-2 payload")
    raw = upstream.read_bytes()
    if len(raw) != target.size or digest(raw) != target.sha256:
        raise ValueError(f"expected the pinned {archive_name}")
    if fixture and (not PureWindowsPath(fixture).is_absolute() or
                    not PureWindowsPath(fixture).drive.endswith(":") or ".." in PureWindowsPath(fixture).parts):
        raise ValueError("fixture requires an absolute local Windows test directory")
    files = {"core/" + k: v for k, v in candidate["payload"].items()}
    files["manage.py"] = (SOURCE / "distribution/windows/manage.py").read_bytes()
    icon = (SOURCE / "assets/brand/png/icon-256.png").read_bytes()
    icon_sha = digest(icon)
    notices = (SOURCE / "distribution/windows/notices.py").read_bytes()
    marker = b'ICON_SHA256 = ""'
    if notices.count(marker) != 1:
        raise ValueError("notification icon pin marker")
    files["notices.py"] = notices.replace(marker, ('ICON_SHA256 = "' + icon_sha + '"').encode(), 1)
    files["notice-icon.png"] = icon
    with zipfile.ZipFile(io.BytesIO(raw)) as source:
        runtime = {name: digest(source.read(name)) for name in source.namelist()}
    config = {"release": candidate["release_ref"]["id"], "fixture": fixture or "",
              "runtime": runtime, "payload": {k: digest(v) for k, v in files.items()}}
    resource_name = f"rsrc_windows_{architecture}.syso"
    resource = (SOURCE / "distribution/windows" / resource_name).read_bytes()
    resource_info = json.loads((SOURCE / "distribution/windows/icon-resources.json").read_text())
    resource_sha = digest(resource)
    if (resource_info["png_256_sha256"] != icon_sha or
            resource_info["objects"].get(resource_name) != resource_sha or
            resource_info["icon_sha256"] != digest((SOURCE / "assets/brand/colvia.ico").read_bytes())):
        raise ValueError("Windows icon resource differs from its recorded inputs")
    output.mkdir(parents=True, exist_ok=False)
    # A fixed GOPATH import identity prevents absolute host paths in build info
    # and file tables. Keep module mode off to preserve existing Go defaults.
    gopath = output.resolve() / "build"
    work = gopath / "src/colvia.local/windows-bootstrap"
    work.mkdir(parents=True)
    (work / "catalog.json").write_text(json.dumps(config, sort_keys=True), encoding="utf-8")
    with zipfile.ZipFile(work / "core.zip", "x", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, data in sorted(files.items()):
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            archive.writestr(info, data, compress_type=zipfile.ZIP_DEFLATED)
    shutil.copyfile(SOURCE / "distribution/windows/bootstrap.go", work / "bootstrap.go")
    shutil.copyfile(SOURCE / "distribution/windows/window.go", work / "window.go")
    (work / resource_name).write_bytes(resource)
    # Compile the same pins used to verify the archive into the bootstrap.
    (work / "python_target.go").write_text(
        "package main\n\n"
        f'const pythonArch = "{architecture}"\n'
        f'const pythonMachine = {target.machine:#x}\n'
        f'const pythonSize = {target.size}\n'
        f'const pythonSHA = "{target.sha256}"\n'
        f'const upstream = "https://www.python.org/ftp/python/3.14.7/{archive_name}"\n',
        encoding="ascii",
    )
    for name in ("cache", "temp"):
        (gopath / name).mkdir()
    go = shutil.which("go")
    if go is None:
        raise ValueError("The release builder requires an existing local Go toolchain")
    env = {**os.environ, "GOOS": "windows", "GOARCH": architecture, "GOAMD64": "v1", "GOARM64": "v8.0", "CGO_ENABLED": "0",
           "GOTOOLCHAIN": "local", "GOENV": "off", "GOWORK": "off", "GOFLAGS": "",
           "GOPROXY": "off", "GOSUMDB": "off", "GOTELEMETRY": "off", "GO111MODULE": "off",
           "GOPATH": str(gopath), "PWD": str(work),
           "GOCACHE": str(gopath / "cache"), "GOTMPDIR": str(gopath / "temp")}
    exe = output / "colvia-manage.exe"
    subprocess.run([go, "build", "-trimpath", "-buildvcs=false", "-o", str(exe), "."],
                   check=True, cwd=work, env=env, timeout=120)
    build_info = subprocess.run([go, "version", "-m", str(exe)], env=env,
                                check=True, capture_output=True, text=True, timeout=20).stdout
    if [line.strip() for line in build_info.splitlines() if line.startswith("\tpath\t")] != ["path\tcolvia.local/windows-bootstrap"]:
        raise ValueError("Windows build has no stable package identity")
    executable = exe.read_bytes()
    for path in (output.absolute(), output.resolve(), gopath):
        if str(path).encode() in executable or path.as_posix().encode() in executable:
            raise ValueError("Windows build contains a private build path")
    dependencies = subprocess.run([go, "list", "-deps", "-f", "{{if not .Standard}}{{.ImportPath}}{{end}}", "."],
                                  cwd=work, env=env, check=True, capture_output=True, text=True, timeout=30).stdout
    if dependencies.split() != ["colvia.local/windows-bootstrap"]:
        raise ValueError("Windows bootstrap must use only standard-library dependencies")
    (gopath / "build-info.txt").write_text(build_info, encoding="utf-8")
    (gopath / "dependencies.txt").write_text(dependencies, encoding="utf-8")
    result = {"profile": "windows-2", "architecture": architecture, "fixture": bool(fixture),
              "sha256": digest(exe.read_bytes()), "release": candidate["release_ref"],
              "runtime_archive_sha256": target.sha256, "resource_sha256": resource_sha, "notice_icon_sha256": icon_sha,
              "build_import_path": "colvia.local/windows-bootstrap"}
    (output / "build.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--arch", choices=TARGETS, default="arm64", help="native Windows architecture (amd64 for x64)")
    parser.add_argument("--prepared", type=Path, required=True)
    parser.add_argument("--upstream-zip", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--fixture-store", help="bake an isolated test path into this build")
    args = parser.parse_args()
    build(args.prepared.absolute(), args.upstream_zip, args.output.absolute(), args.fixture_store, args.arch)
