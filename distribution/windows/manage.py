"""User-facing Windows project entry, called by the verified native bootstrap."""
import argparse
import contextlib
from datetime import datetime, timezone
import io
import json
import os
from pathlib import Path
import runpy
import subprocess
import sys
import uuid

CORE = Path(__file__).absolute().parent / "core"
MUTATIONS = {"install": "init", "update": "update", "rollback": "rollback",
             "repair": "repair", "remove": "detach"}


def canonical(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n").encode()


def save_request(path, value, target):
    path = path.absolute()
    parents = path.parents
    if (".." in path.parts or os.path.isreserved(path.name)
            or any(p.lstat().st_file_attributes & 0x400 for p in parents)):
        raise ValueError("요청 파일은 프로젝트 밖의 일반 폴더에 저장해 주세요.")
    parent = path.parent.resolve(strict=True)
    if (any(p.samefile(target) for p in (parent, *parent.parents))
            or any(part.casefold() == ".hrn" for part in (*parent.parts, path.name))):
        raise ValueError("요청 파일은 프로젝트 밖의 일반 폴더에 저장해 주세요.")
    destination = parent / path.name
    pending = parent / (".pending-" + uuid.uuid4().hex)
    with pending.open("xb") as stream:
        stream.write(canonical(value))
        stream.flush()
        os.fsync(stream.fileno())
    # Windows rename refuses an existing destination. A known collision leaves
    # the destination intact. Preserve interrupted or unclassified failures.
    try:
        pending.rename(destination)
    except FileExistsError:
        pending.unlink()
        raise


def arguments():
    parser = argparse.ArgumentParser(description="프로젝트에서 Colvia로 작업을 시작하고 이어갑니다.")
    sub = parser.add_subparsers(dest="command", required=True)
    for name in (*MUTATIONS, "status", "doctor", "start", "resume", "view", "project"):
        p = sub.add_parser(name)
        p.add_argument("--target", type=Path, default=Path.cwd())
        if name in ("project", "view"):
            p.add_argument("args", nargs=argparse.REMAINDER)
        if name in ("view", "resume"):
            p.add_argument("--details", action="store_true")
        if name in (*MUTATIONS, "status", "doctor"):
            p.add_argument("--json", action="store_true")
        if name in MUTATIONS:
            p.add_argument("--apply", action="store_true")
            p.add_argument("--input", type=Path)
            p.add_argument("--save", type=Path)
            p.add_argument("--confirm")
            p.add_argument("--recover", action="store_true")
        if name == "repair":
            p.add_argument("--backup", type=Path)
        if name == "rollback":
            p.add_argument("--to")
    for name in ("notice-enable", "notice-disable", "notice-identity", "notice-detail", "notice-post"):
        p = sub.add_parser(name)
        if name in ("notice-detail", "notice-post"):
            p.add_argument("--event", required=True)
    return parser.parse_args(sys.argv[3:])


def lifecycle_args(args, target):
    name = MUTATIONS.get(args.command, args.command)
    argv = [name, "--target", str(target)]
    if args.command not in MUTATIONS:
        return argv
    if name in ("init", "update", "repair"):
        argv += ["--source", str(CORE)]
    if name != "repair":
        argv += ["--profile", "windows-2"]
    if args.apply:
        if not args.input or not args.confirm or args.save or getattr(args, "backup", None):
            raise ValueError("적용할 요청 파일과 미리보기의 확인값을 함께 지정해 주세요.")
        argv += ["--apply", "--input", str(args.input.absolute()), "--confirm", args.confirm]
        if args.recover:
            argv += ["--recover"]
    else:
        if args.input or args.confirm or args.recover:
            raise ValueError("저장한 요청을 적용할 때 --apply를 사용하세요.")
        argv += ["--operation-id", "manage-" + uuid.uuid4().hex,
                 "--observed-at", datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")]
        if name == "init":
            argv += ["--authority-home-id", "home-" + uuid.uuid4().hex]
        if name == "repair":
            if not args.backup:
                raise ValueError("원본을 보존할 프로젝트 밖의 새 --backup 경로를 지정해 주세요.")
            argv += ["--backup", str(args.backup.absolute())]
    if getattr(args, "to", None):
        argv += ["--to", args.to]
    return argv


def main():
    if sys.platform != "win32" or not sys.flags.isolated or not sys.dont_write_bytecode:
        raise ValueError("검증된 Windows용 colvia-manage.exe로 시작해 주세요.")
    store = Path(sys.argv[1])
    args = arguments()
    if args.command.startswith("notice-"):
        sys.path.insert(0, str(CORE / "src"))
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from notices import handle
        handle(store, sys.argv[2], args.command, getattr(args, "event", None))
        return 0
    target = args.target.absolute()
    if (".." in target.parts or target == store or target.is_relative_to(store)
            or store.is_relative_to(target)):
        raise ValueError("프로젝트와 전용 배포 폴더를 분리해 주세요.")
    entry = runpy.run_path(str(CORE / "colvia"))
    if not entry["windows_runtime_observation"]()["supported"]:
        raise ValueError("현재 Windows와 Python 조합을 확인해 주세요.")
    if args.command in ("view", "project", "start", "resume"):
        # Use the installed launcher as the real Python entry point. Writers
        # check __main__.__file__ as well as the loaded release modules.
        entry["workspace_source"](target)
        launcher = target / "colvia"
        if entry["regular_bytes"](launcher) != entry["regular_bytes"](CORE / "colvia"):
            raise ValueError("프로젝트에 연결한 배포본과 같은 관리 도구로 시작해 주세요.")
        rest = getattr(args, "args", [])
        if rest[:1] == ["--"]:
            rest = rest[1:]
        argv = rest if args.command == "project" else ["view", *rest]
        if getattr(args, "details", False):
            argv += ["--details"]
        if args.command == "start":
            print("에이전트에게 원하는 결과와 수정 범위를 알려주세요. 예를 들어 ‘설치 안내를 읽고 보강할 계획을 보여줘’라고 말할 수 있습니다.")
        if args.command == "resume":
            print("현재 Work와 승인 범위를 확인한 뒤 다음 작업을 이어가세요.")
        if any(arg.startswith("--") and "--target".startswith(arg.split("=", 1)[0])
               for arg in argv):
            raise ValueError("프로젝트는 관리 명령의 --target으로 한 번만 지정해 주세요.")
        sys.stdout.flush()
        return subprocess.run([sys.executable, "-I", "-B", str(launcher), *argv],
                              cwd=target, check=False).returncode

    sys.argv = ["colvia", *lifecycle_args(args, target)]
    sys.path.insert(0, str(CORE / "src"))
    from hv2ref.cli import main as cli
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        code = cli()
    value = json.loads(output.getvalue())
    if code == 0 and value.get("classification") == "preview":
        if not isinstance(value.get("request"), dict) or not value.get("confirm_token"):
            raise ValueError("미리보기의 요청과 확인값을 확인해 주세요.")
        path = args.save or store / "requests" / ("request-" + uuid.uuid4().hex + ".json")
        save_request(path, value["request"], target)
        value["request_file"] = str(path.absolute())
    if args.json:
        print(canonical(value).decode(), end="")
    elif "request_file" in value:
        print("적용 전 확인할 프로젝트:", target)
        print("저장한 요청:", value["request_file"])
        print("확인값:", value["confirm_token"])
        print("요청 내용을 검토한 뒤 에이전트에게 이 요청대로 적용해 달라고 말하세요.")
    elif code != 0:
        print(value.get("message") or value.get("next_action") or value.get("classification"))
    elif args.command == "remove":
        print("프로젝트 연결을 해제했습니다. 작업·승인·결과 기록은 프로젝트에 보존했습니다.")
    else:
        print(value.get("next_action") or "프로젝트 상태와 다음 작업은 colvia-manage view로 확인하세요.")
    return code


if __name__ == "__main__":
    for stream in (sys.stdout, sys.stderr):
        stream.reconfigure(encoding="utf-8", newline="\n")
    try:
        raise SystemExit(main())
    except (ValueError, OSError, KeyError, TypeError, RecursionError) as error:
        print("현재 파일과 요청을 보존하고 프로젝트 상태를 확인해 주세요.", error, file=sys.stderr)
        raise SystemExit(65)
