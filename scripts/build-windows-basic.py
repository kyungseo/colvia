"""Build a private ARM64 bootstrap, offline, from an explicitly prepared windows-2 tree."""
import argparse
import hashlib
import io
import json
import os
from pathlib import Path, PureWindowsPath
import shutil
import subprocess
import sys
import zipfile

SOURCE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SOURCE / "src"))
from hv2ref.product import workspace_candidate

PYTHON_ZIP = "python-3.14.7-embed-arm64.zip"
PYTHON_SHA = "f6773983c8959d4281e48c4540cb0bdd23e42391e4e951ce17e7ceb52658f21c"
PYTHON_BYTES = 11980260


def digest(data):
    return hashlib.sha256(data).hexdigest()


def build(prepared, upstream, output, fixture):
    candidate = workspace_candidate(prepared)
    if candidate["release_ref"]["inventory_id"] != "windows-2":
        raise ValueError("requires prepared windows-2 payload")
    raw = upstream.read_bytes()
    if len(raw) != PYTHON_BYTES or digest(raw) != PYTHON_SHA:
        raise ValueError("unexpected upstream CPython ZIP")
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
    for name in ("cache", "temp"):
        (work / name).mkdir()
    go = shutil.which("go")
    if go is None:
        raise ValueError("The release builder requires an existing local Go toolchain")
    env = {**os.environ, "GOOS": "windows", "GOARCH": "arm64", "CGO_ENABLED": "0",
           "GOTOOLCHAIN": "local", "GOENV": "off", "GOWORK": "off", "GOFLAGS": "",
           "GOPROXY": "off", "GOSUMDB": "off", "GOTELEMETRY": "off", "GO111MODULE": "off",
           "GOCACHE": str(work / "cache"), "GOTMPDIR": str(work / "temp")}
    exe = output / "colvia-manage.exe"
    subprocess.run([go, "build", "-trimpath", "-buildvcs=false", "-o", str(exe), "bootstrap.go", "window.go"],
                   check=True, cwd=work, env=env)
    result = {"profile": "windows-2", "architecture": "arm64", "fixture": bool(fixture),
              "sha256": digest(exe.read_bytes()), "release": candidate["release_ref"],
              "runtime_archive_sha256": PYTHON_SHA}
    (output / "build.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepared", type=Path, required=True)
    parser.add_argument("--upstream-zip", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--fixture-store", help="bake an isolated test path into this build")
    args = parser.parse_args()
    build(args.prepared.absolute(), args.upstream_zip, args.output.absolute(), args.fixture_store)
