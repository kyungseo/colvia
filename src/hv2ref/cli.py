from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .carrier import build_release, verify_release
from .errors import ContractError, InjectedCrash
from .jsonio import durability_probe, load_json
from .state import StateStore


def _print(value: object) -> None:
    print(json.dumps(value, allow_nan=False, ensure_ascii=False, indent=2, sort_keys=True))


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(prog="hv2ref", description="Harness v2 first private reference core CLI")
    sub = root.add_subparsers(dest="command", required=True)

    build = sub.add_parser("build-release")
    build.add_argument("--source", type=Path, required=True)
    build.add_argument("--output", type=Path, required=True)
    build.add_argument("--seal", type=Path, required=True)

    verify_carrier = sub.add_parser("verify-release")
    verify_carrier.add_argument("--release", type=Path, required=True)

    init = sub.add_parser("init-target")
    init.add_argument("--target", type=Path, required=True)
    init.add_argument("--authority-home-id", required=True)
    init.add_argument("--item-id", required=True)
    init.add_argument("--observed-at", required=True)

    transition = sub.add_parser("transition")
    transition.add_argument("--target", type=Path, required=True)
    transition.add_argument("--item-id", required=True)
    transition.add_argument("--operation", choices=("create", "update", "rollback", "detach"), required=True)
    transition.add_argument("--sequence", type=int, required=True)
    transition.add_argument("--observed-at", required=True)
    transition.add_argument("--actor", required=True)
    transition.add_argument("--release", type=Path)
    transition.add_argument("--rollback-revision")
    transition.add_argument(
        "--inject-at",
        choices=("after_intent", "after_stage", "after_acceptance", "after_result", "after_revision", "after_pointer_assertion", "after_switch"),
    )

    resume = sub.add_parser("resume")
    resume.add_argument("--target", type=Path, required=True)
    resume.add_argument("--item-id", required=True)
    resume.add_argument("--operation", choices=("create", "update", "rollback", "detach"), required=True)
    resume.add_argument("--sequence", type=int, required=True)

    verify = sub.add_parser("verify-state")
    verify.add_argument("--target", type=Path, required=True)
    verify.add_argument("--item-id", required=True)

    probe = sub.add_parser("durability-probe")
    probe.add_argument("--root", type=Path, required=True)
    return root


def run(args: argparse.Namespace) -> object:
    if args.command == "build-release":
        return build_release(args.source, args.output, load_json(args.seal, require_canonical=True))
    if args.command == "verify-release":
        return verify_release(args.release)
    if args.command == "init-target":
        return StateStore(args.target).initialize(args.authority_home_id, args.item_id, args.observed_at)
    if args.command == "transition":
        if (args.operation == "rollback") != (args.rollback_revision is not None):
            raise ContractError("HV2-ROLLBACK-OPTION", args.operation)
        if args.release is not None and args.operation != "create":
            raise ContractError("HV2-RELEASE-OPTION", args.operation)
        return StateStore(args.target).transition(
            item_id=args.item_id,
            operation=args.operation,
            sequence=args.sequence,
            observed_at=args.observed_at,
            actor=args.actor,
            release_root=args.release,
            rollback_revision=args.rollback_revision,
            inject_at=args.inject_at,
        )
    if args.command == "resume":
        return StateStore(args.target).resume(args.item_id, args.operation, args.sequence)
    if args.command == "verify-state":
        return StateStore(args.target).verify(args.item_id)
    if args.command == "durability-probe":
        return durability_probe(args.root)
    raise AssertionError(args.command)


def main() -> int:
    try:
        result = run(parser().parse_args())
        _print(result)
        if isinstance(result, dict) and result.get("classification") == "degraded":
            return 10
        if isinstance(result, dict) and result.get("classification") == "incompatible":
            return 11
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


if __name__ == "__main__":
    sys.exit(main())
