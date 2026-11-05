"""Versioned standalone manager. CONFIG is frozen by the source-only builder."""
from __future__ import annotations

import argparse
import ast
import base64
import ctypes
import hashlib
import errno
import io
import json
import os
from pathlib import Path
import shutil
import signal
import shlex
import stat
import subprocess
import sys
import tarfile
import time
import uuid
from datetime import datetime, timezone

CONFIG: dict = {}


def canonical(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n").encode()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def regular(path):
    for parent in (path.parent, *path.parent.parents):
        if not stat.S_ISDIR(parent.lstat().st_mode):
            raise ValueError("경로에 디렉터리가 아닌 항목이 있습니다.")
    before = path.lstat()
    if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1:
        raise ValueError("독립된 일반 파일이 필요합니다.")
    raw = path.read_bytes()
    after = path.lstat()
    signature = lambda s: (s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns, s.st_ctime_ns)
    if signature(before) != signature(after):
        raise ValueError("읽는 동안 파일이 바뀌었습니다.")
    return raw


def store_root():
    # The builder renders a literal root only in separately identified fixtures.
    root = Path(CONFIG["fixture_root"]) if CONFIG["fixture_root"] else Path.home() / "Library/Application Support/Colvia"
    if not root.is_absolute() or root.resolve(strict=True) != root:
        raise ValueError("Colvia 저장 위치를 확인해 주세요.")
    return root


def clean_environment():
    scratch = store_root() / "checks"
    return {"HOME": str(Path.home()), "PATH": "/usr/bin:/bin", "LC_ALL": "C",
            "TMPDIR": str(scratch), "XDG_CONFIG_HOME": str(scratch / "config"),
            "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": "/dev/null",
            "GIT_CONFIG_SYSTEM": "/dev/null", "GIT_ATTR_NOSYSTEM": "1", "GIT_TERMINAL_PROMPT": "0",
            "PYTHONDONTWRITEBYTECODE": "1"}


def validate_payload(source, profile):
    expected = CONFIG["profiles"][profile]["files"]
    expected_dirs = {"."}
    for name in expected:
        expected_dirs.update(parent.as_posix() for parent in Path(name).parents)
    observed = set()
    observed_dirs = set()
    for path in (source, *source.rglob("*")):
        info = path.lstat()
        if stat.S_ISREG(info.st_mode):
            name = path.relative_to(source).as_posix()
            mode = 0o500 if name == "colvia" else 0o400
            if (name not in expected or info.st_uid != os.getuid()
                    or stat.S_IMODE(info.st_mode) != mode or sha(regular(path)) != expected[name]):
                raise ValueError("배포본 파일이 달라졌습니다. 원본을 보존하고 에이전트에게 손상 위치와 복구 계획을 확인해 주세요.")
            observed.add(name)
        elif stat.S_ISDIR(info.st_mode):
            name = path.relative_to(source).as_posix()
            if (name not in expected_dirs or info.st_uid != os.getuid()
                    or stat.S_IMODE(info.st_mode) not in (0o500, 0o700)):
                raise ValueError("배포본의 디렉터리 또는 권한이 달라졌습니다.")
            observed_dirs.add(name)
        else:
            raise ValueError("배포본에 지원하지 않는 링크가 있습니다.")
    if observed != set(expected) or observed_dirs != expected_dirs:
        raise ValueError("배포본 파일이 누락되었습니다.")


def runtime_path(store):
    return store / "runtimes" / CONFIG["runtime_id"]


def verify_runtime(root, store):
    for name, digest in CONFIG["runtime_files"].items():
        if sha(regular(root / name)) != digest:
            raise ValueError("전용 Python 검증 자료가 달라졌습니다.")
    try:
        result = subprocess.run(["/bin/bash", str(root / "verify-tree.sh"), str(root / "python"),
                                 str(root / "objects.txt"), str(root / "files.sha256"), str(store / "checks")],
                                stdin=subprocess.DEVNULL, capture_output=True, env=clean_environment(), timeout=30)
    except subprocess.TimeoutExpired:
        raise ValueError("전용 Python 검증 시간이 초과됐습니다. 손상 여부는 미확인입니다. 현재 파일을 보존하고 실행 환경을 확인해 주세요.") from None
    if result.returncode or result.stdout or result.stderr:
        raise ValueError("전용 Python 검증을 완료하지 못했습니다. 원본을 보존하고 에이전트에게 손상 위치 확인을 요청해 주세요.")


def sync_directory(path):
    fd = os.open(path, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def write_new(path, raw, mode=0o400):
    # Publish only complete bytes, never replace an existing destination.
    pending = path.parent / (".pending-" + uuid.uuid4().hex)
    fd = os.open(pending, os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, "wb") as stream:
        stream.write(raw); stream.flush(); os.fchmod(stream.fileno(), mode); os.fsync(stream.fileno())
    try:
        publish_file(pending, path)
    except OSError as error:
        if error.errno in (errno.EEXIST, errno.ENOTSUP):
            pending.unlink()
        raise
    sync_directory(path.parent)


def publish_file(pending, path):
    # Darwin RENAME_EXCL: atomic publication, EEXIST instead of replacement.
    # Process interruption cannot publish partial bytes or a second hardlink.
    # This is not a power-loss/full-storage durability guarantee.
    import ctypes
    native = ctypes.CDLL(None, use_errno=True).renamex_np
    native.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_uint]
    native.restype = ctypes.c_int
    if native(os.fsencode(pending), os.fsencode(path), 0x00000004):
        error = ctypes.get_errno()
        raise OSError(error, os.strerror(error), str(path))


def selected_profile(args):
    if args.profile is not None:
        return args.profile
    binding = args.target.absolute() / ".hrn/product/binding.json"
    try:
        candidate = None
        if getattr(args, "apply", False) and getattr(args, "input", None):
            request = json.loads(regular(args.input.absolute()))
            candidate = request.get("candidate_release")
            if candidate is None and isinstance(request.get("plan"), dict):
                candidate = request["plan"].get("candidate_release")
        if candidate is not None:
            value = candidate["inventory_id"]
        elif binding.exists() or binding.is_symlink():
            value = json.loads(regular(binding))["active_release"]["inventory_id"]
        elif args.command == "install" and not (args.target.absolute() / ".hrn").exists():
            return "continuation-1"
        elif args.command in ("status", "doctor"):
            return "continuation-1"
        else:
            raise ValueError("binding unavailable")
        if not isinstance(value, str): raise ValueError("profile type")
        # Reader selection only; the product validates the full request/binding.
        if value in CONFIG["profiles"]: return value
        if value == "official-execution-1": return "official-execution-2"
        raise ValueError("profile unavailable")
    except (OSError, ValueError, KeyError, TypeError, AttributeError, RecursionError):
        if args.command in ("status", "doctor"): return "continuation-1"
        raise ValueError("프로젝트 연결 정보를 읽지 못했습니다. status --details로 상태를 확인하고, 복구할 정확한 배포본과 --profile을 지정해 주세요.") from None


def run_lifecycle(argv):
    proc = None
    interruption_pending = False
    signals = (signal.SIGINT, signal.SIGTERM, signal.SIGHUP)
    previous = {sig: signal.getsignal(sig) for sig in signals}
    def interrupted(signum, frame):
        nonlocal interruption_pending
        # Never raise asynchronously, including during child creation/cleanup.
        interruption_pending = True
    try:
        for sig in signals: signal.signal(sig, interrupted)
        try:
            if interruption_pending: raise RuntimeError("management interrupted")
            proc = subprocess.Popen(argv, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE, env=clean_environment(), start_new_session=True)
            deadline = time.monotonic() + 300
            while True:
                if interruption_pending: raise RuntimeError("management interrupted")
                remaining = deadline - time.monotonic()
                if remaining <= 0: raise subprocess.TimeoutExpired(argv, 300)
                try:
                    out, err = proc.communicate(timeout=min(0.2, remaining))
                except subprocess.TimeoutExpired:
                    continue
                if interruption_pending: raise RuntimeError("management interrupted")
                return subprocess.CompletedProcess(argv, proc.returncode, out, err)
        except BaseException:
            # Flag-only handlers remain installed throughout bounded cleanup.
            if proc is None:
                raise ValueError("명령 시작 단계가 중단됐습니다. 실행 여부와 적용 결과를 확인한 뒤 진행해 주세요.") from None
            closed = False
            for sig in (signal.SIGTERM, signal.SIGKILL):
                try: os.killpg(proc.pid, sig)
                except ProcessLookupError: pass
                except PermissionError: break
                try: proc.communicate(timeout=2)
                except subprocess.TimeoutExpired: continue
                try: os.killpg(proc.pid, 0)
                except ProcessLookupError: closed = True; break
                except PermissionError: break
            note = "자식 프로세스 종료를 확인했습니다." if closed else "자식 프로세스 종료 여부도 미확인입니다."
            raise ValueError("명령이 중단되어 적용 결과를 확인하지 못했습니다. " + note + " 요청과 현재 파일을 보존하고, 재시도 전에 실행 중인 프로세스와 status를 확인해 주세요.") from None
    finally:
        for sig, handler in previous.items(): signal.signal(sig, handler)


NOTICE_BINARY = "Contents/MacOS/ColviaWork"
NOTICE_MEMBERS = {"Contents/Info.plist", NOTICE_BINARY, "Contents/_CodeSignature/CodeResources"}


def notice_members(encoded):
    if set(encoded) != NOTICE_MEMBERS:
        raise ValueError("알림 앱 구성 목록을 확인해 주세요.")
    return {name:base64.b64decode(value, validate=True) for name,value in encoded.items()}


def notice_matches(app, files):
    allowed_dirs = {".", "Contents", "Contents/MacOS", "Contents/_CodeSignature"}
    dirs, members = set(), set()
    for p in (app, *app.rglob("*")):
        name = p.relative_to(app).as_posix()
        st = p.lstat()
        if st.st_uid != os.getuid() or st.st_mode & 0o022:
            return False
        if stat.S_ISDIR(st.st_mode) and name in allowed_dirs:
            dirs.add(name)
        elif (name in files and stat.S_ISREG(st.st_mode) and st.st_nlink == 1
              and stat.S_IMODE(st.st_mode) == (0o500 if name == NOTICE_BINARY else 0o400)
              and regular(p) == files[name]):
            members.add(name)
        else:
            return False
    return dirs == allowed_dirs and members == set(files)


def install_notice_app(store, stage, old):
    app = store / "bin/ColviaWork.app"
    files = notice_members(CONFIG["notice_app"])
    exists = os.path.lexists(app)
    if exists:
        if notice_matches(app, files):
            return
        # The caller checked the previous manager against its retained copy.
        # Extract only its literal configuration; never execute an older manager.
        nodes = ast.parse(old).body if old else ()
        prior = [n for n in nodes if isinstance(n, ast.AnnAssign)
                 and isinstance(n.target, ast.Name) and n.target.id == "CONFIG"]
        conf = ast.literal_eval(prior[0].value) if len(prior) == 1 else {}
        if "notice_app" not in conf or not notice_matches(app, notice_members(conf["notice_app"])):
            raise ValueError("기존 알림 앱의 출처를 확인해 주세요.")
    pending = stage / "ColviaWork.app"
    pending.mkdir(mode=0o700)
    for name, raw in files.items():
        dest = pending / name
        dest.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        write_new(dest, raw, 0o500 if name == NOTICE_BINARY else 0o400)
    if not notice_matches(pending, files):
        raise ValueError("준비된 알림 앱을 확인해 주세요.")
    rename = ctypes.CDLL(None, use_errno=True).renamex_np
    rename.argtypes = [ctypes.c_char_p,ctypes.c_char_p,ctypes.c_uint]
    if rename(os.fsencode(pending), os.fsencode(app), 0x00000002 if exists else 0x00000004):
        raise OSError(ctypes.get_errno(), "알림 앱을 게시하지 못했습니다.")
    sync_directory(app.parent)


def notice_location_matches(store):
    # Do not silently redirect a HOME-based installation to another account store.
    # A source-built fixture has its own fixed root and distinct native identity.
    if CONFIG.get("fixture_root"):
        return store == Path(CONFIG["fixture_root"]).resolve()
    import pwd
    if os.getuid() != os.geteuid():
        return False
    expected = Path(pwd.getpwuid(os.getuid()).pw_dir) / "Library/Application Support/Colvia"
    return store == expected.resolve()


def notice_command(store, action, event):
    import sqlite3
    if not isinstance(event,str) or len(event)!=32 or any(c not in "0123456789abcdef" for c in event):
        return 65
    profile = "continuation-1"
    source = store / "releases" / CONFIG["profiles"][profile]["release"]["id"]
    validate_payload(source,profile)
    sys.path.insert(0,str(source/"src"))
    from hv2ref.continuation import notification_detail
    from hv2ref.errors import ContractError
    try:
        text = notification_detail(store,event)
        if action == "notice-detail":
            print(text if len(text) <= 30000 else text[:29900] + "\n상세 내용은 프로젝트 수신함에서 이어서 확인하세요."); return 0
        app = store / "bin/ColviaWork.app"
        if not notice_matches(app, notice_members(CONFIG["notice_app"])):
            return 65
        return subprocess.run([str(app/NOTICE_BINARY),"--post",event],stdin=subprocess.DEVNULL,
                              stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=30).returncode
    except (ContractError,OSError,KeyError,TypeError,ValueError,sqlite3.Error,subprocess.TimeoutExpired):
        return 65


def activate(stage):
    """Called only after bootstrap's OS-only hash/tree verification.

    All data is rechecked here. The caller holds the fixed store activation lock.
    A partial stage remains recoverable; no project authority is touched.
    """
    store = store_root()
    stage = Path(stage).absolute()
    if stage.parent != store / "staging" or stage.resolve(strict=True) != stage:
        raise ValueError("설치 준비 위치가 올바르지 않습니다.")
    if not (store / "activation.lock").is_dir():
        raise ValueError("설치 잠금이 필요합니다.")
    incoming_runtime = stage / "runtime"
    verify_runtime(incoming_runtime, store)
    if Path(sys.executable).resolve() != incoming_runtime / "python/bin/python3.14":
        raise ValueError("검증한 준비 단계의 Python으로 실행해야 합니다.")
    payload = regular(stage / "product.tar")
    if sha(payload) != CONFIG["product_archive_sha256"]:
        raise ValueError("제품 압축 파일이 달라졌습니다.")
    notices = regular(stage / "notices.tar")
    if sha(notices) != CONFIG["notices_sha256"]:
        raise ValueError("라이선스 자료가 달라졌습니다.")
    expected = {}
    for profile, value in CONFIG["profiles"].items():
        expected.update({value["release"]["id"] + "/" + name: digest for name, digest in value["files"].items()})
    prepared = stage / "releases"
    prepared.mkdir(mode=0o700)
    seen = set()
    with tarfile.open(fileobj=io.BytesIO(payload), mode="r:") as archive:
        for member in archive:
            if (not member.isfile() or member.name not in expected or member.name in seen
                    or member.size > 8 * 1024 * 1024 or member.mode not in (0o400, 0o500)):
                raise ValueError("배포 파일 목록이 일치하지 않습니다.")
            raw = archive.extractfile(member).read()
            if sha(raw) != expected[member.name]:
                raise ValueError("배포 파일 내용이 일치하지 않습니다.")
            target = prepared / member.name
            for parent in reversed(target.parent.parents):
                if parent == prepared or parent.is_relative_to(prepared):
                    parent.mkdir(exist_ok=True, mode=0o700)
            target.parent.mkdir(exist_ok=True, mode=0o700)
            write_new(target, raw, member.mode)
            seen.add(member.name)
    if seen != set(expected):
        raise ValueError("배포 파일이 누락되었습니다.")
    # Validate every candidate before publishing any of them.
    for profile, value in CONFIG["profiles"].items():
        validate_payload(prepared / value["release"]["id"], profile)
    # Keep directories owner-writable until rename has completed. On macOS,
    # moving a directory between parents can require write access to that
    # directory. Read-only publication is finalized below, including recovery
    # after a prior rename completed but sealing did not.
    destinations = [store / "runtimes", store / "releases", store / "tools", store / "bin", store / "requests"]
    for path in destinations:
        path.mkdir(exist_ok=True, mode=0o700)
        if path.resolve(strict=True) != path or not stat.S_ISDIR(path.lstat().st_mode):
            raise ValueError("설치 대상 경로가 달라졌습니다.")
    final_runtime = runtime_path(store)
    if final_runtime.exists() or final_runtime.is_symlink():
        verify_runtime(final_runtime, store)
    else:
        os.rename(incoming_runtime, final_runtime)
        sync_directory(final_runtime.parent)
    for profile, value in CONFIG["profiles"].items():
        destination = store / "releases" / value["release"]["id"]
        if destination.exists() or destination.is_symlink():
            validate_payload(destination, profile)
        else:
            os.rename(prepared / value["release"]["id"], destination)
            sync_directory(destination.parent)
        for path in sorted(destination.rglob("*"), key=lambda p: len(p.parts), reverse=True):
            if path.is_dir():
                sync_directory(path); path.chmod(0o500)
        sync_directory(destination); destination.chmod(0o500)
        sync_directory(destination.parent)
    notice_root = store / "notices"
    notice_root.mkdir(exist_ok=True, mode=0o700)
    notice_path = notice_root / (CONFIG["notices_sha256"] + ".tar")
    if notice_path.exists():
        if regular(notice_path) != notices:
            raise ValueError("기존 라이선스 자료가 달라졌습니다.")
    else:
        write_new(notice_path, notices)
    manager = regular(stage / "colvia-manage")
    if manager != regular(Path(__file__).absolute()):
        raise ValueError("관리 도구가 준비 중 바뀌었습니다.")
    tool_id = sha(manager)
    saved = store / "tools" / tool_id
    saved.mkdir(exist_ok=True, mode=0o700)
    retained = saved / "colvia-manage"
    if retained.exists():
        if regular(retained) != manager:
            raise ValueError("기존 도구 복사본이 달라졌습니다.")
    else:
        write_new(retained, manager, 0o500)
    active = store / "bin/colvia-manage"
    old = None
    if active.exists() or active.is_symlink():
        old = regular(active)
        if regular(store / "tools" / sha(old) / "colvia-manage") != old:
            raise ValueError("현재 도구의 복구 가능한 원본을 확인할 수 없습니다.")
    install_notice_app(store, stage, old)
    staged = store / "bin" / (".activate-" + uuid.uuid4().hex)
    write_new(staged, manager, 0o500)
    os.replace(staged, active); sync_directory(active.parent)
    print("Colvia와 전용 Python 준비가 끝났습니다. 프로젝트에 연결할 범위를 확인해 주세요.")
    print("처음이라면: " + shlex.quote(str(active)) + ' start --target "프로젝트 경로"')
    print("새 프로젝트 연결: " + shlex.quote(str(active)) + ' install --target "프로젝트 경로"')
    print("기존 프로젝트 갱신: " + shlex.quote(str(active)) + ' update --target "프로젝트 경로"')
    print("관리 명령만 복구했다면 기존 프로젝트에서 ./colvia view로 작업을 이어가세요.")
    print("활성 관리 도구: " + tool_id)
    print("기존 Work·승인 기록과 shell 설정은 그대로 유지됩니다.")


def lifecycle(args, store):
    if args.apply and (args.save or args.backup):
        raise ValueError("요청 저장과 백업 위치는 적용 전 미리보기에서 지정해 주세요.")
    if args.backup is not None and args.command != "repair":
        raise ValueError("--backup은 복구 미리보기에서 사용합니다.")
    if args.to is not None and args.command != "rollback":
        raise ValueError("--to는 프로젝트 rollback에서 사용합니다.")
    runtime_input = getattr(args, "runtime_input", None)
    if runtime_input is not None and args.command != "doctor":
        raise ValueError("--runtime-input은 doctor에서 사용합니다.")
    profile = selected_profile(args)
    diagnostic_supported = CONFIG["profiles"][profile].get("runtime_input_diagnostic") is True
    source = store / "releases" / CONFIG["profiles"][profile]["release"]["id"]
    validate_payload(source, profile)
    command = {"install": "init", "remove": "detach"}.get(args.command, args.command)
    argv = [str(runtime_path(store) / "python/bin/python3.14"), "-I", "-B", str(source / "colvia"),
            "--source-checkout", command, "--target", str(args.target.absolute())]
    if command in ("status", "doctor"):
        if runtime_input is not None and diagnostic_supported:
            argv += ["--runtime-input", str(runtime_input.absolute())]
    elif command in ("init", "update", "repair"):
        argv += ["--source", str(source)]
    if command not in ("status", "doctor", "repair"):
        argv += ["--profile", profile]
    if args.apply:
        if not args.input or not args.confirm:
            raise ValueError("적용에는 미리보기의 요청 파일과 확인값이 필요합니다.")
        argv += ["--apply", "--input", str(args.input.absolute()), "--confirm", args.confirm]
        if args.recover:
            argv += ["--recover"]
    elif command not in ("status", "doctor"):
        if args.input or args.confirm or args.recover:
            raise ValueError("먼저 새 적용 범위의 미리보기를 확인해 주세요.")
        argv += ["--operation-id", "manage-" + uuid.uuid4().hex,
                 "--observed-at", datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")]
        if command == "init":
            argv += ["--authority-home-id", "home-" + uuid.uuid4().hex]
        if command == "repair":
            if args.backup is None:
                raise ValueError("복구에는 프로젝트 밖의 새 --backup 경로가 필요합니다.")
            argv += ["--backup", str(args.backup.absolute())]
    if command == "rollback" and args.to:
        argv += ["--to", args.to]
    result = run_lifecycle(argv)
    try:
        value = json.loads(result.stdout)
        if not isinstance(value, dict): raise ValueError("object required")
    except (ValueError, UnicodeError):
        raise ValueError("명령 응답을 확인하지 못했습니다. 요청과 현재 파일을 보존하고 재시도 전에 status로 상태를 확인해 주세요.") from None
    diagnostic = value.get("official_runtime_input")
    diagnostic_present = (isinstance(diagnostic, dict) and
                          diagnostic.get("local_check") in ("passed", "failed", "unavailable") and
                          all(isinstance(diagnostic.get(k), str) for k in ("message", "next_action")))
    if runtime_input is not None and (not diagnostic_supported or not diagnostic_present):
        value["official_runtime_input"] = {
            "profile": "unavailable", "local_check": "unavailable",
            "reason": "diagnostic-not-supported" if not diagnostic_supported else "diagnostic-response-missing",
            "message": "이 관리 배포본에는 공식 실행 입력 진단이 없습니다." if not diagnostic_supported else "실행 입력 진단 결과를 받지 못했습니다.",
            "next_action": "현재 배포본의 지원 기능과 보존된 실행 근거를 확인하세요.",
            "account_connection": "unobserved", "model_connection": "unobserved",
            "environment_scope": "current-command-process"}
    if result.returncode == 0 and value.get("classification") == "preview" and "request" in value:
        path = args.save.absolute() if args.save is not None else store / "requests" / ("manage-" + uuid.uuid4().hex + ".json")
        if path.is_relative_to(args.target.absolute()) or any(p.name == ".hrn" for p in (path, *path.parents)):
            raise ValueError("미리보기 요청은 프로젝트 기록 밖에 보관해 주세요.")
        if path.parent.resolve(strict=True) != path.parent:
            raise ValueError("요청 저장 경로의 링크를 확인해 주세요.")
        if not isinstance(value.get("confirm_token"), str) or not value["confirm_token"]:
            raise ValueError("미리보기 확인값을 읽지 못했습니다. 적용을 보류하고 응답을 확인해 주세요.")
        write_new(path, canonical(value["request"]), 0o600)
        value["request_file"] = str(path)
    elif args.save is not None and result.returncode == 0:
        raise ValueError("성공한 미리보기의 요청만 저장할 수 있습니다.")
    if args.json:
        print(canonical(value).decode(), end="")
    else:
        state = value.get("classification", "checked")
        labels = {"preview": "적용 전 확인", "pass": "정상", "detached": "프로젝트 연결 해제됨",
                  "uninitialized": "프로젝트 연결 전", "partial": "중단된 적용 확인 필요",
                  "unsupported": "현재 실행 환경 확인 필요", "fail": "진행을 멈췄습니다"}
        print(("프로젝트 상태: " if runtime_input is not None else "현재 상태: ") + labels.get(state, str(state)))
        print("프로젝트: " + str(args.target.absolute()))
        diagnostic = value.get("official_runtime_input")
        if isinstance(diagnostic, dict):
            print("실행 입력: " + diagnostic["message"])
            print("다음 확인: " + diagnostic["next_action"])
            if diagnostic["local_check"] != "unavailable":
                print("진단 환경: 관리 명령에 전달된 환경")
            print("계정·모델 연결: 미확인")
        if result.returncode:
            for field in ("message", "next_action"):
                if value.get(field): print(str(value[field]))
            if not value.get("message") and not value.get("next_action"):
                print("명령 결과를 확인하지 못했습니다. 요청과 현재 파일을 보존하고 상태를 확인해 주세요.")
        elif args.command in ("status", "doctor"):
            if state in ("pass", "ready", "installed", "current"):
                print("상세한 작업 내용은 프로젝트에서 ./colvia view로 확인하세요.")
            elif state == "detached":
                print("보존한 기록 조회: " + shlex.join([str(runtime_path(store) / "python/bin/python3.14"), "-I", "-B", str(source / "colvia"), "--source-checkout", "view", "--target", str(args.target.absolute())]))
            else:
                print(str(value.get("next_action") or value.get("message") or "연결 상태를 먼저 확인해 주세요. --details에서 판정 근거를 볼 수 있습니다."))
        elif args.apply:
            if args.command == "remove":
                print("프로젝트 연결을 해제했습니다. 문서와 작업 기록은 그대로 있습니다. 관리 도구의 status로 보존한 기록을 읽는 방법을 확인하세요.")
            else:
                print("요청한 변경을 적용했습니다. 프로젝트에서 ./colvia view로 현재 작업을 확인하세요.")
        elif state == "preview":
            actions = {"install": "Colvia 연결", "update": "프로젝트 Colvia 갱신", "rollback": "이전 프로젝트 배포본으로 복귀",
                       "repair": "프로젝트 Colvia 복구", "remove": "프로젝트 Colvia 연결 해제"}
            print("확인할 변경: " + actions[args.command])
            if args.command == "remove":
                print("진행 중인 일과 검토할 결과는 해제 전에 확인하세요. 기록은 남으며, 같은 폴더에서 다시 이어갈 예정이면 연결을 유지하세요.")
            print("검토한 요청: " + value["request_file"])
            print("확인값: " + str(value["confirm_token"]))
            print("이 요청으로 진행하려면 에이전트에게 ‘저장한 요청대로 적용해줘’라고 말하세요. 변경·보존 파일은 --details에서 확인할 수 있습니다.")
        else:
            print(str(value.get("next_action") or value.get("message") or "--details에서 현재 상태를 확인해 주세요."))
        if args.details:
            print(canonical(value).decode(), end="")
    if result.stderr:
        print("추가 진단 출력이 있습니다. 위 응답 결과와 함께 현재 상태를 확인해 주세요.", file=sys.stderr)
    return result.returncode


def main():
    parser = argparse.ArgumentParser(description="Colvia 설치·갱신·제거: 먼저 적용 범위를 확인합니다.")
    parser.add_argument("command", choices=("install", "update", "rollback", "repair", "remove", "status", "doctor", "start", "resume", "remove-tool", "remove-runtime", "notice-post", "notice-detail", "notice-enable", "notice-check"))
    parser.add_argument("--target", type=Path, default=Path.cwd())
    parser.add_argument("--event")
    parser.add_argument("--profile", choices=("continuation-1", "official-execution-2"), default=None)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--recover", action="store_true")
    parser.add_argument("--input", type=Path)
    parser.add_argument("--runtime-input", type=Path, help="doctor 전용 로컬 입력 확인; 연결 확인은 별도")
    parser.add_argument("--confirm")
    parser.add_argument("--save", type=Path)
    parser.add_argument("--backup", type=Path)
    parser.add_argument("--to")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--details", action="store_true")
    args = parser.parse_args()
    if args.runtime_input is not None and args.command != "doctor":
        parser.error("--runtime-input은 doctor에서 사용합니다.")
    store = store_root()
    if args.command.startswith("notice-") and not notice_location_matches(store):
        print("현재 로그인 계정의 설치 위치와 알림 앱 위치가 다릅니다. 프로젝트 수신함에서 결과를 확인하고 설치 위치를 점검하세요.")
        return 3
    verify_runtime(runtime_path(store), store)
    if args.command in ("notice-enable", "notice-check"):
        app = store / "bin/ColviaWork.app"
        if args.event or not notice_matches(app, notice_members(CONFIG["notice_app"])):
            return 65
        action = "--check-receiver" if args.command == "notice-check" else "--authorize"
        try:
            code = subprocess.run([str(app/NOTICE_BINARY),action],stdout=subprocess.DEVNULL if args.command == "notice-check" else None,timeout=35).returncode
        except subprocess.TimeoutExpired:
            print("알림 앱 확인이 시간 안에 끝나지 않았습니다. 프로젝트 수신함에서 결과를 확인해 주세요.")
            return 65
        if code == 3:
            print("현재 설치본의 알림 앱 연결을 확인하지 못했습니다. 설치 위치와 열려 있는 Colvia 상세 창을 확인하세요. 결과는 프로젝트 수신함에서 볼 수 있습니다.")
        elif code == 0 and args.command == "notice-check":
            print("현재 설치본과 알림 앱의 연결이 일치합니다. 실제 알림 표시와 클릭은 별도로 확인해야 합니다.")
        return code
    if args.command in ("notice-post","notice-detail"):
        return notice_command(store,args.command,args.event)
    if args.event is not None:
        parser.error("--event requires a notification command")
    if args.command == "remove-runtime":
        print("현재 버전의 remove-runtime은 공유 Python 제거를 지원하지 않습니다. 이동·복제된 프로젝트의 사용 가능성을 고려해 Python·배포본·복구 자료를 보존합니다.")
        return 65
    if args.command == "remove-tool":
        path = store / "bin/colvia-manage"
        if not args.apply:
            identity = sha(regular(path))
            print("제거 대상: " + str(path) + " 및 이 도구의 알림 앱")
            print("보존: 프로젝트·전용 Python·요청·복구 복사본")
            print("확인값: " + identity)
            return 0
        lock = store / "activation.lock"
        try:
            lock.mkdir(mode=0o700)
        except FileExistsError:
            raise ValueError("설치·갱신 또는 중단된 작업의 잠금을 먼저 확인해 주세요.") from None
        try:
            raw = regular(path)
            identity = sha(raw)
            if args.confirm != identity or regular(store / "tools" / identity / "colvia-manage") != raw:
                raise ValueError("표시한 도구 identity와 복구 복사본을 확인해 주세요.")
            app = store / "bin/ColviaWork.app"
            if os.path.lexists(app):
                if not notice_matches(app, notice_members(CONFIG["notice_app"])):
                    raise ValueError("제거할 알림 앱의 내용을 확인해 주세요.")
                os.rename(app, store / "staging" / ("removed-notice-" + uuid.uuid4().hex))
            path.unlink(); sync_directory(path.parent)
        finally:
            lock.rmdir()
        print("관리 명령을 제거했습니다. 프로젝트·전용 Python·요청·복구 복사본은 보존했습니다.")
        return 0
    if args.command in ("start", "resume"):
        entry = args.target.absolute() / "colvia"
        if not entry.is_file():
            folder = entry.parent
            if not folder.is_dir() or folder.is_symlink():
                raise ValueError("시작할 프로젝트 폴더를 확인해 주세요.")
            command = "status" if os.path.lexists(folder / ".hrn") or os.path.lexists(entry) else "install"
            if command == "install":
                if any(item.name != ".DS_Store" for item in folder.iterdir()):
                    print("기존 프로젝트입니다. README와 프로젝트 규칙에서 맡길 일과 유지할 내용을 먼저 확인하세요.")
                else:
                    print("빈 폴더입니다. 여기에 만들 첫 결과물을 정하세요. Git 저장소를 만들 필요는 없습니다.")
                print("연결하면 이 폴더에 colvia와 .hrn이 생깁니다. 프로젝트 지침 변경은 따로 확인하세요. 다음 명령으로 적용할 범위를 미리 볼 수 있습니다.")
            label = "보존한 기록 확인" if command == "status" else "연결 미리보기"
            print(label + ": " + shlex.join([str(store / "bin/colvia-manage"), command, "--target", str(folder)]))
            if command == "status": print("기존 기록이 있습니다. 연결 해제·부분 적용 상태를 확인한 뒤 보존 기록 조회 또는 복구를 선택하세요.")
            return 15
        if args.command == "start":
            print("에이전트에게 원하는 결과와 바꿔도 되는 범위를 알려주세요. 예: ‘소개 문서를 살펴보고, 설치 안내를 보강할 계획부터 보여줘.’")
        else:
            print("에이전트에게 ‘이 프로젝트의 완료된 내용과 남은 작업을 확인하고, 다음에 할 일과 이유를 추천해줘’라고 요청하세요.")
        print("에이전트는 ./colvia view --details와 현재 Work·계획을 읽고 유효한 승인을 이어갑니다.")
        return 0
    return lifecycle(args, store)


if __name__ == "__main__":
    try:
        if len(sys.argv) == 3 and sys.argv[1] == "--bootstrap-activate":
            activate(sys.argv[2])
            raise SystemExit(0)
        raise SystemExit(main())
    except (OSError, ValueError, KeyError, subprocess.SubprocessError) as error:
        print("Colvia: " + str(error), file=sys.stderr)
        raise SystemExit(65)
