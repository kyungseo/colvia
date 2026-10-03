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


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(prog="hv2ref", description="Harness v2 private Public Core candidate CLI")
    sub = root.add_subparsers(dest="command", required=True)

    product_init = sub.add_parser("init", help="preview or initialize one project-local product binding")
    product_init.add_argument("--target", type=Path, required=True)
    product_init.add_argument("--source", type=Path, default=product_source_root())
    product_init.add_argument("--apply", action="store_true")
    product_init.add_argument("--profile", choices=("planning-1",))
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
        p.add_argument("--profile", choices=("planning-1",))
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

    product_detach.add_argument("--profile",choices=("planning-1",))
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
        return workspace_status(args.target)
    if args.command == "repair":
        return _workspace_repair(args)
    if args.command in ("init", "update", "rollback", "detach"):
        if args.profile != "planning-1":
            raise ContractError("HV2-WORKSPACE-COMMAND", "source lifecycle requires explicit planning-1 profile; use retained old source for older windows")
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
    p = sub.add_parser("view", help="read-only human review; never applies a decision")
    p.add_argument("kind", nargs="?", choices=("intent", "work", "confirmation", "candidates"))
    p.add_argument("object_id", nargs="?")
    p.add_argument("--target", type=Path, default=target)
    p.add_argument("--revision")
    p.add_argument("--input", help="canonical ticket file or - for stdin; not the prepare envelope")


def workspace_parser(target: Path) -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(prog="hv2", description="Single-home human review and serial machine interface")
    sub = root.add_subparsers(dest="command", required=True)
    for name in ("status", "doctor"):
        p = sub.add_parser(name);p.add_argument("--target", type=Path, default=target)
    for command in ("update","rollback","detach"):
        p = sub.add_parser(command);p.add_argument("--target", type=Path, default=target)
        if command == "update": p.add_argument("--source",type=Path,required=True)
        elif command == "rollback": p.add_argument("--to",dest="to_release_id")
        p.add_argument("--operation-id");p.add_argument("--observed-at")
        p.add_argument("--input");p.add_argument("--confirm");p.add_argument("--apply",action="store_true")
        p.set_defaults(recover=False,inject_at=None)
    for kind in ("intent", "work"):
        parent = sub.add_parser(kind);commands = parent.add_subparsers(dest="action", required=True)
        for operation in (("draft", "prepare", "apply") if kind == "intent" else ("publish", "prepare", "apply")):
            p = commands.add_parser(operation)
            p.add_argument("--target", type=Path, default=target)
            p.add_argument("--input", default="-", help="canonical JSON input file or stdin")
            if operation == "apply": p.add_argument("--confirm", required=True)
            if kind == "work" and operation == "publish": p.add_argument("--worker", type=Path, help="registered linked worktree for a worker result")
    candidate = sub.add_parser("candidate", help="record project-local plans; never grants execution approval")
    from .candidates import ACTIONS
    candidate.add_argument("action", choices=ACTIONS)
    candidate.add_argument("--target", type=Path, default=target)
    candidate.add_argument("--input", default="-", help="canonical candidate-request JSON; agent prepares input")
    candidate.add_argument("--inject-at", choices=("after-temporary", "after-directory", "before-replace", "after-replace"), help=argparse.SUPPRESS)
    _view_parser(sub, target)
    return root


def workspace_run(args: argparse.Namespace) -> object:
    from .product import workspace_status, require_workspace_runtime
    from .work import WorkStore
    from .intent import WorkspaceIntentStore
    if args.command in {"status", "doctor"}: return workspace_status(args.target)
    # Reject source/worker/foreign-target entry before reading or publishing records.
    require_workspace_runtime(args.target)
    if args.command in ("update","rollback"): return _workspace_switch(args, installed=True)
    if args.command == "detach": return _workspace_detach(args,installed=True)
    value = _workspace_input(args.input)
    def exact(keys, optional=()):
        if not isinstance(value, dict) or not set(keys) <= set(value) or set(value) - set(keys) - set(optional):
            raise ContractError("HV2-WORKSPACE-CLI-INPUT", "unexpected input fields")
    if args.command == "candidate":
        from .candidates import CandidateStore
        if not isinstance(value, dict) or value.get("action") != args.action:
            raise ContractError("HV2-CANDIDATE-REQUEST", "command/action mismatch; not saved")
        return CandidateStore(args.target).mutate(value, inject_at=args.inject_at)
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
