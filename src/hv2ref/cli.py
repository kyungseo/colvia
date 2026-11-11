from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .errors import ContractError, InjectedCrash
from .intent import classify_entry
from .jsonio import durability_probe, load_json
from .product import source_root as product_source_root


def _print(value: object) -> None:
    print(json.dumps(value, allow_nan=False, ensure_ascii=False, indent=2, sort_keys=True))


def _doctor_argument(parser):
    parser.add_argument("--runtime-input", type=Path,
                        help="공식 실행 입력 파일의 로컬 검사; 계정·모델 연결은 미확인. 종료코드는 프로젝트 상태 기준")


def _doctor_status(args):
    from .product import workspace_status
    result = workspace_status(args.target)
    supplied = getattr(args, "runtime_input", None)
    if args.command != "doctor" or supplied is None:
        return result
    product = result.get("product")
    inventory = product.get("inventory") if isinstance(product, dict) else None
    profile = inventory.get("inventory_id") if isinstance(inventory, dict) else None
    observation = {"profile": profile if profile in ("continuation-1", "windows-2", "official-execution-1", "official-execution-2") else "unavailable",
                   "local_check": "unavailable", "reason": "project-check-required",
                   "message": "프로젝트 상태를 먼저 확인해야 합니다.",
                   "next_action": "위 프로젝트 상태에 안내된 확인부터 진행하세요.",
                   "account_connection": "unobserved", "model_connection": "unobserved",
                   "environment_scope": "current-command-process"}
    if result.get("classification") == "pass":
        if profile != "official-execution-2":
            observation.update(reason="official-profile-required",
                               message="이 프로젝트는 공식 실행 입력 진단 대상이 아닙니다.",
                               next_action="현재 연결된 배포본의 기능 범위를 확인하세요.")
        elif sys.platform != "darwin":
            observation.update(reason="platform-unavailable",
                               message="공식 실행 입력 진단은 검증된 macOS 환경에서 제공합니다.",
                               next_action="현재 환경의 지원 범위를 확인하세요.")
        else:
            try:
                from .official_entry import diagnose_runtime_input
            except ImportError:
                observation.update(reason="official-install-inconsistent",
                                   message="공식 실행 진단 모듈을 읽지 못했습니다.",
                                   next_action="현재 배포본의 파일과 설치 무결성을 확인하세요.")
            else:
                observation.update(diagnose_runtime_input(supplied))
    return {**result, "official_runtime_input": observation}


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(prog="hv2ref", description="Colvia private Public Core candidate CLI", epilog='Windows-2 integration candidate: use an absolute allowed Python path with -I -B and the verified launcher in native Windows PowerShell. Explicit source profile windows-2 must match prepared source. Native OS/process and local NTFS checks apply; worker mode changes and new untracked 100755 results are unsupported. Qualification and activation remain pending. See the verified manual.')
    sub = root.add_subparsers(dest="command", required=True)

    product_init = sub.add_parser("init", help="preview or initialize one project-local product binding")
    product_init.add_argument("--target", type=Path, required=True)
    product_init.add_argument("--source", type=Path, required=True)
    product_init.add_argument("--apply", action="store_true")
    product_init.add_argument("--profile", choices=("continuation-1", "windows-2", "official-execution-1", "official-execution-2"))
    product_init.add_argument("--authority-home-id")
    product_init.add_argument("--operation-id")
    product_init.add_argument("--observed-at")
    product_init.add_argument("--input")
    product_init.add_argument("--confirm")
    product_init.add_argument("--recover", action="store_true")
    product_init.add_argument(
        "--inject-at",
        choices=("after-release", "after-plan", "after-launcher", "after-root", "after-product-dir", "after-format", "after-ignore", "after-intents", "after-work", "after-staged-inventory", "after-staged-payload", "after-receipt", "after-launcher-bytes", "after-binding"),
        help=argparse.SUPPRESS,
    )

    product_status = sub.add_parser("status", help="report product binding, state, capability and next action")
    product_status.add_argument("--target", type=Path, default=Path.cwd())

    product_doctor = sub.add_parser("doctor", help="run read-only runtime and binding diagnostics")
    product_doctor.add_argument("--target", type=Path, default=Path.cwd())
    _doctor_argument(product_doctor)

    product_update = sub.add_parser("update", help="preview or apply a digest-bound product release update")
    product_update.add_argument("--target", type=Path, default=Path.cwd())
    product_update.add_argument("--source", type=Path, required=True)
    product_update.add_argument("--apply", action="store_true")
    product_update.add_argument(
        "--inject-at", choices=("after-release", "after-receipt", "after-staged-inventory", "after-staged-payload", "after-launcher", "after-binding"), help=argparse.SUPPRESS
    )

    product_rollback = sub.add_parser("rollback", help="preview or switch to a prior immutable product release")
    product_rollback.add_argument("--target", type=Path, default=Path.cwd())
    product_rollback.add_argument("--to", dest="to_release_id")
    product_rollback.add_argument("--apply", action="store_true")
    product_rollback.add_argument(
        "--inject-at", choices=("after-receipt", "after-release", "after-launcher", "after-binding"), help=argparse.SUPPRESS
    )

    for p in (product_update, product_rollback):
        p.add_argument("--profile", choices=("continuation-1", "windows-2", "official-execution-1", "official-execution-2"))
        p.add_argument("--operation-id")
        p.add_argument("--observed-at")
        p.add_argument("--input")
        p.add_argument("--confirm")
        p.add_argument("--recover", action="store_true")

    repair = sub.add_parser("repair", help="restore exact active bytes from independent trusted source")
    repair.add_argument("--target", type=Path, required=True)
    repair.add_argument("--source", type=Path, required=True)
    repair.add_argument("--backup", type=Path)
    repair.add_argument("--operation-id")
    repair.add_argument("--observed-at")
    repair.add_argument("--apply", action="store_true")
    repair.add_argument("--input")
    repair.add_argument("--confirm")
    repair.add_argument("--recover", action="store_true")
    repair.add_argument("--inject-at", choices=("after-backup-request","after-backup","after-file","after-receipt"), help=argparse.SUPPRESS)

    product_detach = sub.add_parser("detach", help="preview or remove product-managed bytes while preserving project truth")
    product_detach.add_argument("--target", type=Path, default=Path.cwd())
    product_detach.add_argument("--apply", action="store_true")
    product_detach.add_argument(
        "--inject-at", choices=("after-receipt", "after-launcher", "after-file", "after-files", "after-directory", "after-product"), help=argparse.SUPPRESS
    )

    product_detach.add_argument("--profile",choices=("continuation-1", "windows-2", "official-execution-1", "official-execution-2"))
    product_detach.add_argument("--operation-id")
    product_detach.add_argument("--observed-at")
    product_detach.add_argument("--input")
    product_detach.add_argument("--confirm")
    product_detach.add_argument("--recover",action="store_true")

    classify_intent = sub.add_parser("classify-intent-entry")
    classify_intent.add_argument("--consequence", choices=("consequential", "non-consequential"), required=True)
    classify_intent.add_argument("--input", type=Path)

    probe = sub.add_parser("durability-probe")
    probe.add_argument("--root", type=Path, required=True)
    _view_parser(sub, Path.cwd())
    return root


def run(args: argparse.Namespace) -> object:
    from .product import workspace_status
    if args.command in ("status", "doctor"):
        return _doctor_status(args)
    if args.command == "repair":
        return _workspace_repair(args)
    if args.command in ("init", "update", "rollback", "detach"):
        from .product import _launcher_inventory_window, _serial_file
        from .workspace import require_supported_runtime
        declared = _launcher_inventory_window(_serial_file(product_source_root() / "colvia"))
        if args.profile != declared:
            guidance = ("; use retained old source for older windows" if args.profile is None
                        else " matching the prepared source; preserve older windows")
            raise ContractError("HV2-WORKSPACE-COMMAND", "source lifecycle requires explicit " + declared + " profile" + guidance)
        require_supported_runtime(declared)
        source = getattr(args, "source", None)
        if source is not None:
            from .product import workspace_candidate
            if workspace_candidate(source)["release_ref"]["inventory_id"] != declared:
                raise ContractError("HV2-WORKSPACE-COMMAND", "candidate declaration differs from source profile; no cross-window fallback")
        if args.command == "init":
            return _source_workspace_init(args)
        if args.command == "detach":
            return _workspace_detach(args, installed=False)
        return _workspace_switch(args, installed=False)
    if args.command == "classify-intent-entry":
        if args.input is None:
            gaps = []
        else:
            value = load_json(args.input)
            if not isinstance(value, dict) or set(value) != {"gaps"}:
                raise ContractError("HV2-INTENT-CLASSIFY-INPUT", str(args.input))
            gaps = value["gaps"]
        return classify_entry(args.consequence, gaps)
    if args.command == "durability-probe":
        resolved = args.root.resolve()
        if any((p / ".hrn").exists() or (p / ".hrn").is_symlink() for p in (resolved, *resolved.parents)):
            raise ContractError("HV2-WORKSPACE-COMMAND", "diagnostic probe cannot enter workspace")
        return durability_probe(args.root)
    raise AssertionError(args.command)


def main(workspace_target: Path | None = None) -> int:
    try:
        args = workspace_parser(workspace_target).parse_args() if workspace_target is not None else parser().parse_args()
        if args.command in ("help", "?"):
            from .view import render_help
            print(render_help(args.target, installed=workspace_target is not None), end="")
            return 0
        if args.command == "view":
            from .view import run as view_run
            rendered, code = view_run(args, installed=workspace_target is not None)
            print(rendered, end="")
            return code
        result = workspace_run(args) if workspace_target is not None else run(args)
        _print(result)
        if isinstance(result, dict) and result.get("classification") == "degraded":
            return 10
        if isinstance(result, dict) and result.get("classification") == "incompatible":
            return 11
        if isinstance(result, dict) and result.get("classification") == "conflict":
            return 12
        if isinstance(result, dict) and result.get("classification") == "stale":
            return 13
        if isinstance(result, dict) and result.get("classification") == "partial":
            return 14
        if isinstance(result, dict) and result.get("classification") == "uninitialized":
            return 15
        if isinstance(result, dict) and result.get("classification") == "unsupported":
            return 16
        return 0
    except InjectedCrash as exc:
        _print({"classification": "injected-crash", "code": exc.code, "point": exc.point})
        return 75
    except ContractError as exc:
        _print({"classification": "fail", "code": exc.code, "message": exc.message})
        return 65
    except Exception as exc:
        _print({"classification": "internal-error", "code": "HV2-INTERNAL", "exception_type": type(exc).__name__})
        return 70


def _workspace_input(value: str) -> object:
    from .jsonio import decode_json_bytes, MAX_JSON_BYTES
    if value == "-": return decode_json_bytes(sys.stdin.buffer.read(MAX_JSON_BYTES + 1), require_canonical=True)
    return load_json(Path(value), require_canonical=True)


def _view_parser(sub, target):
    help_parser = sub.add_parser("help", aliases=["?"], help="조회 명령과 질문 예시")
    help_parser.add_argument("--target", type=Path, default=target)
    p = sub.add_parser("view", help="read-only human review; never applies a decision")
    p.add_argument("kind", nargs="?", choices=("intent", "work", "continuation", "confirmation", "candidates", "inbox"))
    p.add_argument("object_id", nargs="?")
    p.add_argument("--target", type=Path, default=target)
    p.add_argument("--revision")
    p.add_argument("--details", action="store_true", help="프로젝트 기술 상세와 직접 조회 명령도 표시")
    p.add_argument("--brief", action="store_true", help="작업 또는 후보의 판단에 필요한 요약만 표시")
    p.add_argument("--input", help="canonical ticket file or - for stdin; not the prepare envelope")


def workspace_parser(target: Path) -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(prog="colvia", description="Single-home human review and serial machine interface", epilog='Windows-2 integration candidate: use an absolute allowed Python path with -I -B and the verified launcher in native Windows PowerShell. Explicit source profile windows-2 must match prepared source. Native OS/process and local NTFS checks apply; worker mode changes and new untracked 100755 results are unsupported. Qualification and activation remain pending. See the verified manual.')
    sub = root.add_subparsers(dest="command", required=True)
    for name in ("status", "doctor"):
        p = sub.add_parser(name);p.add_argument("--target", type=Path, default=target)
        if name == "doctor": _doctor_argument(p)
    for command in ("update","rollback","detach"):
        p = sub.add_parser(command);p.add_argument("--target", type=Path, default=target)
        if command == "update": p.add_argument("--source",type=Path,required=True)
        elif command == "rollback": p.add_argument("--to",dest="to_release_id")
        p.add_argument("--operation-id");p.add_argument("--observed-at")
        p.add_argument("--input");p.add_argument("--confirm");p.add_argument("--apply",action="store_true")
        p.set_defaults(recover=False,inject_at=None)
    simple = sub.add_parser("ordinary", help="prepare a plan, start a local Work, or present its result")
    actions = simple.add_subparsers(dest="action", required=True)
    for name in ("plan", "plan-review", "approve", "start", "status", "submit", "prepare-delivery", "review", "revise", "resume-revision", "resume-accept", "accept"):
        cmd = actions.add_parser(name)
        cmd.add_argument("id", help="explicit local Work and intent identifier")
        cmd.set_defaults(target=target)
        if name == "plan":
            cmd.add_argument("--goal", required=True)
            paths = cmd.add_mutually_exclusive_group(required=True)
            paths.add_argument("--file", action="append")
            paths.add_argument("--files-stdin", action="store_true", help="read the exact path list as canonical JSON on stdin")
            cmd.add_argument("--check", action="append", required=True)
            cmd.add_argument("--exclude", action="append", required=True)
            cmd.add_argument("--owner", required=True)
        if name in ("submit", "prepare-delivery"):
            cmd.add_argument("--summary", required=True)
            cmd.add_argument("--checked", action="append", required=True)
            cmd.add_argument("--unchecked", action="append", default=[])
            cmd.add_argument("--baseline", required=True, help="selection digest returned by start")
        if name == "start":
            cmd.add_argument("--approval", required=True, help="intent selection digest returned by approve")
        if name == "prepare-delivery":
            cmd.add_argument("--expires", type=int, required=True, help="UTC Unix deadline, within 24 hours")
        if name == "review":
            cmd.add_argument("--selection", help="require the exact submission identified by a handoff result")
        if name == "revise":
            cmd.add_argument("--reason", required=True, help="the human's requested correction")
        if name in ("approve", "accept", "revise"):
            cmd.add_argument("--receipt", required=True, help="use the receipt shown before the human decision")
    for kind in ("intent", "work"):
        parent = sub.add_parser(kind);commands = parent.add_subparsers(dest="action", required=True)
        for operation in (("draft", "prepare", "apply") if kind == "intent" else ("publish", "prepare", "apply")):
            p = commands.add_parser(operation)
            p.add_argument("--target", type=Path, default=target)
            p.add_argument("--input", default="-", help="canonical JSON input file or stdin")
            if operation == "apply": p.add_argument("--confirm", required=True)
            if kind == "work" and operation == "publish": p.add_argument("--worker", type=Path, help="registered linked worktree for a worker result")
    continuation = sub.add_parser("continuation", help="choose a Work follow-up; no target execution authority")
    commands = continuation.add_subparsers(dest="action", required=True)
    for operation in ("prepare", "apply"):
        p = commands.add_parser(operation)
        p.add_argument("--target", type=Path, default=target)
        p.add_argument("--input", default="-", help="canonical JSON input file or stdin")
        if operation == "apply":
            p.add_argument("--confirm", required=True)
    candidate = sub.add_parser("candidate", help="record project-local plans; never grants execution approval")
    from .candidates import ACTIONS
    candidate.add_argument("action", choices=ACTIONS)
    candidate.add_argument("--target", type=Path, default=target)
    candidate.add_argument("--input", default="-", help="canonical candidate-request JSON; agent prepares input")
    candidate.add_argument("--id", dest="candidate_id", help="build a request from explicit arguments instead of JSON input")
    for flag in ("request-id", "writer", "owner-statement", "reason", "title", "purpose", "effect", "resume-condition", "condition-observation", "link-work", "link-intent", "revision"):
        candidate.add_argument("--" + flag)
    candidate.add_argument("--related", action="append")
    candidate.add_argument("--brief", action="store_true", help="변경 결과의 짧은 확인만 반환")
    candidate.add_argument("--disposition", choices=("absorbed", "rejected"))
    candidate.add_argument("--inject-at", choices=("after-temporary", "after-directory", "before-replace", "after-replace"), help=argparse.SUPPRESS)
    handoff = sub.add_parser("handoff", help="작업 하나를 맡기고 로컬 수신함에서 답변과 결과 확인")
    actions = handoff.add_subparsers(dest="action", required=True)
    for name in ("prepare", "start", "answer", "stop", "inspect", "close-unknown", "show", "_step"):
        command = actions.add_parser(name)
        command.set_defaults(target=target)
        if name != "prepare":
            command.add_argument("key", help="접수 확인값")
        if name in ("prepare", "start"):
            command.add_argument("--input", default="-")
        if name == "answer":
            command.add_argument("--question", required=True)
        if name == "close-unknown":
            command.add_argument("--confirm", required=True)
        if name == "_step":
            command.add_argument("--epoch", type=int, required=True)
    execution = sub.add_parser("run", help="preview a bounded official document execution; installed official window only")
    execution.add_argument("action", nargs="?", default="prepare", choices=("prepare", "execute", "status", "cancel", "resolve"))
    execution.add_argument("--target", type=Path, default=target)
    execution.add_argument("--input", default="-", help="canonical request for prepare, exact spec for execute")
    execution.add_argument("--confirm", help="exact preview digest; trusted-local operator declaration")
    execution.add_argument("--grant", help="consumed execution grant digest")
    execution.add_argument("--reason", default="cancelled", help="fixed cancellation reason code")
    execution.add_argument("--host-control-root", help="explicit private store for recovery status or resolution")
    _view_parser(sub, target)
    return root


def workspace_run(args: argparse.Namespace) -> object:
    from .product import workspace_status, require_workspace_runtime
    from .work import WorkStore
    from .intent import WorkspaceIntentStore
    if args.command in {"status", "doctor"}: return _doctor_status(args)
    # Reject source/worker/foreign-target entry before reading or publishing records.
    require_workspace_runtime(args.target)
    if args.command == "ordinary":
        from .work import ordinary_command
        if args.action == "plan" and args.files_stdin:
            args.file = _workspace_input("-")
            if not isinstance(args.file, list) or not args.file or not all(isinstance(p, str) for p in args.file):
                raise ContractError("HV2-WORK-RECORD", "provide a nonempty JSON array of file paths")
        return ordinary_command(args.target, args)
    if args.command == "handoff":
        from .continuation import delivery_command
        value = _workspace_input(args.input) if args.action in ("prepare","start") else None
        return delivery_command(args.target,args,value)
    if args.command in ("update","rollback"): return _workspace_switch(args, installed=True)
    if args.command == "detach": return _workspace_detach(args,installed=True)
    if args.command == "run":
        if require_workspace_runtime(args.target)["inventory_id"] != "official-execution-2":
            raise ContractError("HV2-OFFICIAL-WINDOW", "explicit official installation required; no source fallback")
        from .official_entry import cli as official_cli
        if args.action == "execute" and not args.confirm:
            raise ContractError("HV2-OFFICIAL-CONFIRM", "execute requires the exact preview digest")
        if args.action in ("status", "cancel", "resolve") and not args.grant:
            raise ContractError("HV2-OFFICIAL-GRANT", "existing grant digest required")
        if (args.action in ("prepare", "execute") and args.grant or
            args.action in ("prepare", "status", "cancel") and args.confirm or
            args.action in ("status", "cancel", "resolve") and args.input != "-" or
            args.action != "cancel" and args.reason != "cancelled" or
            args.action not in ("status", "resolve") and args.host_control_root is not None):
            raise ContractError("HV2-OFFICIAL-OPTIONS", "options do not match execution action")
        failure_default = "input_shape"
        try:
            value = _workspace_input(args.input) if args.action in ("prepare", "execute") else None
            failure_default = "input_shape" if args.action == "prepare" else "internal_error"
            return official_cli(args.target, args, value)
        except (ContractError, OSError, ValueError, KeyError, TypeError, RuntimeError) as error:
            # Raw parser keys, OS errors, and exception strings are not CLI evidence.
            from .official_host import reason_code
            code = reason_code(error, failure_default)
            if args.action == "execute":
                code += "; inspect run status before retry"
            raise ContractError("HV2-OFFICIAL-EXECUTION", code) from None
    if args.command == "candidate" and args.candidate_id is not None:
        if args.input != "-" or args.inject_at is not None:
            raise ContractError("HV2-CANDIDATE-REQUEST", "argument request cannot be mixed with input or interruption injection")
        from .candidates import CandidateStore, argument_request
        result = CandidateStore(args.target).mutate(argument_request(args.target, args))
        if args.brief:
            row = result["store"]["candidates"][args.candidate_id]
            return {"classification": result["classification"], "candidate": args.candidate_id,
                    "title": row["title"], "disposition": row["disposition"], "notice": "계획을 기록했습니다. 작업 실행이나 결과 수락을 뜻하지 않습니다."}
        return result
    if args.command == "candidate" and (args.brief or any(getattr(args, k, None) is not None for k in ("request_id", "writer", "owner_statement", "reason", "title", "purpose", "effect", "resume_condition", "condition_observation", "link_work", "link_intent", "revision", "related", "disposition"))):
        raise ContractError("HV2-CANDIDATE-REQUEST", "argument options require --id; do not mix them with raw input")
    value = _workspace_input(args.input)
    def exact(keys, optional=()):
        if not isinstance(value, dict) or not set(keys) <= set(value) or set(value) - set(keys) - set(optional):
            raise ContractError("HV2-WORKSPACE-CLI-INPUT", "unexpected input fields")
    if args.command == "candidate":
        from .candidates import CandidateStore
        if not isinstance(value, dict) or value.get("action") != args.action:
            raise ContractError("HV2-CANDIDATE-REQUEST", "command/action mismatch; not saved")
        return CandidateStore(args.target).mutate(value, inject_at=args.inject_at)
    if args.command == "continuation":
        from .continuation import ContinuationStore
        store = ContinuationStore(args.target)
        if args.action == "prepare":
            exact(("work_id", "action", "actor", "owner_statement", "reason", "request_id", "observed_at"),
                  ("choice", "document_refs", "supersedes_choice_ref"))
            return store.prepare(value["work_id"], **{k: v for k, v in value.items() if k != "work_id"})
        return store.apply(value, confirm_token=args.confirm)
    if args.command == "intent":
        store = WorkspaceIntentStore(args.target)
        if args.action == "draft": return store.publish_draft(value)
        if args.action == "prepare":
            exact(("intent_id", "revision_ref", "actor", "reason", "request_id", "observed_at"), ("document_refs",))
            return store.prepare(value["intent_id"], value["revision_ref"], **{k:v for k,v in value.items() if k not in {"intent_id", "revision_ref"}})
        return store.apply(value, confirm_token=args.confirm)
    store = WorkStore(args.target)
    if args.action == "publish":
        exact(("identity", "revision", "manifest", "selection_id", "operation_id"))
        return store.publish(value["identity"], value["revision"], value["manifest"], selection_id=value["selection_id"], operation_id=value["operation_id"], worker=args.worker)
    if args.action == "prepare":
        exact(("work_id", "action", "actor", "reason", "request_id", "observed_at", "revision_ref", "supersedes"))
        return store.prepare(value["work_id"], **{k:v for k,v in value.items() if k != "work_id"})
    return store.apply(value, confirm_token=args.confirm)


def _source_workspace_init(args: argparse.Namespace) -> object:
    from .product import workspace_init_preview, workspace_init_apply
    if args.apply:
        if args.input is None or args.confirm is None:
            raise ContractError("HV2-WORKSPACE-INIT-INPUT", "apply requires exact preview request and confirmation token")
        return workspace_init_apply(args.source, args.target, _workspace_input(args.input), confirm_token=args.confirm,
                                    recover=args.recover, inject_at=args.inject_at)
    if args.input is not None or args.confirm is not None or args.recover or args.inject_at:
        raise ContractError("HV2-WORKSPACE-INIT-OPTION", "preview does not consume an apply request")
    return workspace_init_preview(args.source, args.target, authority_home_id=args.authority_home_id,
                                  operation_id=args.operation_id, created_at=args.observed_at)


def _workspace_switch(args: argparse.Namespace, *, installed: bool) -> object:
    from .product import workspace_switch_preview, workspace_switch_apply
    source = getattr(args,"source",None)
    if args.apply:
        if args.input is None or args.confirm is None:
            raise ContractError("HV2-WORKSPACE-SWITCH-INPUT","apply requires exact request and token")
        plan = _workspace_input(args.input)
        if not isinstance(plan,dict) or plan.get("action") != args.command:
            raise ContractError("HV2-WORKSPACE-SWITCH-INPUT","request action differs from command")
        if getattr(args,"to_release_id",None) is not None:
            ref = plan.get("candidate_release")
            if not isinstance(ref,dict) or args.to_release_id != ref.get("id"):
                raise ContractError("HV2-WORKSPACE-SWITCH-INPUT","rollback target differs from request")
        return workspace_switch_apply(args.target,plan,confirm_token=args.confirm,source=source,
                                      recover=args.recover,inject_at=args.inject_at,installed=installed)
    if args.input is not None or args.confirm is not None or args.recover or args.inject_at:
        raise ContractError("HV2-WORKSPACE-SWITCH-OPTION","preview cannot consume apply options")
    return workspace_switch_preview(args.target,action=args.command,source=source,operation_id=args.operation_id,
                                    created_at=args.observed_at,to_release_id=getattr(args,"to_release_id",None),installed=installed)




def _workspace_repair(args: argparse.Namespace) -> object:
    from .product import workspace_repair_preview, workspace_repair_apply
    if args.apply:
        if args.input is None or args.confirm is None or args.backup is not None or args.operation_id is not None or args.observed_at is not None:
            raise ContractError("HV2-WORKSPACE-REPAIR-INPUT", "apply requires input/confirm; backup and identity are bound in the request")
        return workspace_repair_apply(args.source,args.target,_workspace_input(args.input),confirm_token=args.confirm,
                                      recover=args.recover,inject_at=args.inject_at)
    if args.backup is None or args.operation_id is None or args.observed_at is None or args.recover or args.input is not None or args.confirm is not None or args.inject_at:
        raise ContractError("HV2-WORKSPACE-REPAIR-INPUT", "preview requires new external backup, operation-id and observed-at")
    return workspace_repair_preview(args.source,args.target,args.backup,operation_id=args.operation_id,created_at=args.observed_at)



def _workspace_detach(args: argparse.Namespace, *, installed: bool) -> object:
    from .product import workspace_detach_preview, workspace_detach_apply
    if args.apply:
        if args.input is None or args.confirm is None or args.operation_id is not None or args.observed_at is not None:
            raise ContractError("HV2-WORKSPACE-DETACH-INPUT","apply requires input/confirm; identity is bound in the plan")
        return workspace_detach_apply(args.target,_workspace_input(args.input),confirm_token=args.confirm,
                                      recover=args.recover,inject_at=args.inject_at,installed=installed)
    if args.operation_id is None or args.observed_at is None or args.recover or args.input is not None or args.confirm is not None or args.inject_at:
        raise ContractError("HV2-WORKSPACE-DETACH-INPUT","preview requires operation-id and observed-at")
    return workspace_detach_preview(args.target,operation_id=args.operation_id,created_at=args.observed_at,installed=installed)


if __name__ == "__main__":
    raise SystemExit(main())
