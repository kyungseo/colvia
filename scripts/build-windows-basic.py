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
    files["notices.py"] = (SOURCE / "distribution/windows/notices.py").read_bytes()
    with zipfile.ZipFile(io.BytesIO(raw)) as source:
        runtime = {name: digest(source.read(name)) for name in source.namelist()}
    config = {"release": candidate["release_ref"]["id"], "fixture": fixture or "",
              "runtime": runtime, "payload": {k: digest(v) for k, v in files.items()}}
    output.mkdir(parents=True, exist_ok=False)
    work = output / "build"
    work.mkdir()
    (work / "catalog.json").write_text(json.dumps(config, sort_keys=True), encoding="utf-8")
    with zipfile.ZipFile(work / "core.zip", "x", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, data in sorted(files.items()):
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            archive.writestr(info, data, compress_type=zipfile.ZIP_DEFLATED)
    shutil.copyfile(SOURCE / "distribution/windows/bootstrap.go", work / "bootstrap.go")
    shutil.copyfile(SOURCE / "distribution/windows/window.go", work / "window.go")
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
        (work / name).mkdir()
    go = shutil.which("go")
    if go is None:
        raise ValueError("The release builder requires an existing local Go toolchain")
    env = {**os.environ, "GOOS": "windows", "GOARCH": architecture, "GOAMD64": "v1", "GOARM64": "v8.0", "CGO_ENABLED": "0",
           "GOTOOLCHAIN": "local", "GOENV": "off", "GOWORK": "off", "GOFLAGS": "",
           "GOPROXY": "off", "GOSUMDB": "off", "GOTELEMETRY": "off", "GO111MODULE": "off",
           "GOCACHE": str(work / "cache"), "GOTMPDIR": str(work / "temp")}
    exe = output / "colvia-manage.exe"
    subprocess.run([go, "build", "-trimpath", "-buildvcs=false", "-o", str(exe), "bootstrap.go", "python_target.go", "window.go"],
                   check=True, cwd=work, env=env)
    result = {"profile": "windows-2", "architecture": architecture, "fixture": bool(fixture),
              "sha256": digest(exe.read_bytes()), "release": candidate["release_ref"],
              "runtime_archive_sha256": target.sha256}
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
