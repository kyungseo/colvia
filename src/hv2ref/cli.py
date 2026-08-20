from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .carrier import build_release, verify_release
from .errors import ContractError, InjectedCrash
from .intent import IntentStore, classify_entry
from .jsonio import durability_probe, load_json
from .parallel import ParallelStateStore
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

    activate_parallel = sub.add_parser("activate-parallel")
    activate_parallel.add_argument("--target", type=Path, required=True)
    activate_parallel.add_argument("--repository-id", required=True)
    activate_parallel.add_argument("--item-id", required=True)
    activate_parallel.add_argument("--finalizer", required=True)
    activate_parallel.add_argument("--worktree-id", required=True)
    activate_parallel.add_argument("--worktree", type=Path, required=True)
    activate_parallel.add_argument("--branch", required=True)
    activate_parallel.add_argument("--base-commit", required=True)
    activate_parallel.add_argument("--base-tree", required=True)
    activate_parallel.add_argument("--observed-at", required=True)

    register_item = sub.add_parser("register-item")
    register_item.add_argument("--target", type=Path, required=True)
    register_item.add_argument("--item-id", required=True)
    register_item.add_argument("--item-type", required=True)
    register_item.add_argument("--observed-at", required=True)

    claim_work = sub.add_parser("claim-work")
    claim_work.add_argument("--target", type=Path, required=True)
    claim_work.add_argument("--claim-id", required=True)
    claim_work.add_argument("--item-id", required=True)
    claim_work.add_argument("--actor", required=True)
    claim_work.add_argument("--finalizer", required=True)
    claim_work.add_argument("--repository-id", required=True)
    claim_work.add_argument("--worktree-id", required=True)
    claim_work.add_argument("--worktree", type=Path, required=True)
    claim_work.add_argument("--branch", required=True)
    claim_work.add_argument("--base-commit", required=True)
    claim_work.add_argument("--base-tree", required=True)
    claim_work.add_argument("--write-scope", action="append", required=True)
    claim_work.add_argument("--observed-at", required=True)

    reassign_claim = sub.add_parser("reassign-claim")
    reassign_claim.add_argument("--target", type=Path, required=True)
    reassign_claim.add_argument("--reassignment-id", required=True)
    reassign_claim.add_argument("--claim-id", required=True)
    reassign_claim.add_argument("--actor", required=True)
    reassign_claim.add_argument("--finalizer", required=True)
    reassign_claim.add_argument("--reason", required=True)
    reassign_claim.add_argument("--observed-at", required=True)

    finalize_work = sub.add_parser("finalize-work")
    finalize_work.add_argument("--target", type=Path, required=True)
    finalize_work.add_argument("--epoch-id", required=True)
    finalize_work.add_argument("--claim-id", action="append", required=True)
    finalize_work.add_argument("--claim-worktree", action="append", required=True, metavar="CLAIM_ID=PATH")
    finalize_work.add_argument("--finalizer", required=True)
    finalize_work.add_argument("--base-commit", required=True)
    finalize_work.add_argument("--base-tree", required=True)
    finalize_work.add_argument("--result-commit", required=True)
    finalize_work.add_argument("--result-tree", required=True)
    finalize_work.add_argument("--integration-branch", required=True)
    finalize_work.add_argument("--integration-worktree", type=Path, required=True)
    finalize_work.add_argument("--observed-at", required=True)
    finalize_work.add_argument("--succeeds-epoch-id")
    finalize_work.add_argument("--successor-reason")

    verify_repository = sub.add_parser("verify-repository")
    verify_repository.add_argument("--target", type=Path, required=True)
    verify_repository.add_argument("--item-id", required=True)

    classify_intent = sub.add_parser("classify-intent-entry")
    classify_intent.add_argument("--consequence", choices=("consequential", "non-consequential"), required=True)
    classify_intent.add_argument("--input", type=Path)

    init_intent = sub.add_parser("init-intent-home")
    init_intent.add_argument("--target", type=Path, required=True)
    init_intent.add_argument("--authority-home-id", required=True)
    init_intent.add_argument("--observed-at", required=True)

    create_intent = sub.add_parser("create-intent-draft")
    create_intent.add_argument("--target", type=Path, required=True)
    create_intent.add_argument("--intent-id", required=True)
    create_intent.add_argument("--sequence", type=int, required=True)
    create_intent.add_argument("--observed-at", required=True)
    create_intent.add_argument("--input", type=Path, required=True)
    create_intent.add_argument("--inject-at", choices=("after-draft",))

    show_intent = sub.add_parser("show-intent")
    show_intent.add_argument("--target", type=Path, required=True)
    show_intent.add_argument("--intent-id", required=True)
    show_intent.add_argument("--revision-id", required=True)

    accept_intent = sub.add_parser("accept-intent")
    accept_intent.add_argument("--target", type=Path, required=True)
    accept_intent.add_argument("--intent-id", required=True)
    accept_intent.add_argument("--revision-id", required=True)
    accept_intent.add_argument("--revision-sha256", required=True)
    accept_intent.add_argument("--acceptance-id", required=True)
    accept_intent.add_argument("--actor", required=True)
    accept_intent.add_argument("--observed-at", required=True)
    accept_intent.add_argument("--supersedes-selection-id")
    accept_intent.add_argument("--supersedes-selection-sha256")
    accept_intent.add_argument("--inject-at", choices=("after-acceptance", "after-selection"))

    verify_intent = sub.add_parser("verify-intent")
    verify_intent.add_argument("--target", type=Path, required=True)
    verify_intent.add_argument("--intent-id", required=True)

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
    if args.command == "activate-parallel":
        return ParallelStateStore(args.target).activate_parallel(
            repository_id=args.repository_id,
            item_id=args.item_id,
            finalizer=args.finalizer,
            worktree_id=args.worktree_id,
            branch=args.branch,
            base_commit=args.base_commit,
            base_tree=args.base_tree,
            observed_at=args.observed_at,
            worktree_root=args.worktree,
        )
    if args.command == "register-item":
        return ParallelStateStore(args.target).register_item(
            item_id=args.item_id,
            item_type=args.item_type,
            observed_at=args.observed_at,
        )
    if args.command == "claim-work":
        return ParallelStateStore(args.target).claim_work(
            claim_id=args.claim_id,
            item_id=args.item_id,
            actor=args.actor,
            finalizer=args.finalizer,
            repository_id=args.repository_id,
            worktree_id=args.worktree_id,
            branch=args.branch,
            base_commit=args.base_commit,
            base_tree=args.base_tree,
            write_scope=args.write_scope,
            observed_at=args.observed_at,
            worktree_root=args.worktree,
        )
    if args.command == "reassign-claim":
        return ParallelStateStore(args.target).reassign_claim(
            reassignment_id=args.reassignment_id,
            claim_id=args.claim_id,
            actor=args.actor,
            finalizer=args.finalizer,
            reason=args.reason,
            observed_at=args.observed_at,
        )
    if args.command == "finalize-work":
        if (args.succeeds_epoch_id is None) != (args.successor_reason is None):
            raise ContractError("HV2-SUCCESSOR-OPTION", "both successor options are required")
        claim_worktrees: dict[str, Path] = {}
        for binding in args.claim_worktree:
            claim_id, separator, path = binding.partition("=")
            if not separator or not claim_id or not path or claim_id in claim_worktrees:
                raise ContractError("HV2-CLAIM-WORKTREE", binding)
            claim_worktrees[claim_id] = Path(path)
        return ParallelStateStore(args.target).finalize_work(
            epoch_id=args.epoch_id,
            claim_ids=args.claim_id,
            finalizer=args.finalizer,
            base_commit=args.base_commit,
            base_tree=args.base_tree,
            result_commit=args.result_commit,
            result_tree=args.result_tree,
            integration_branch=args.integration_branch,
            observed_at=args.observed_at,
            integration_worktree_root=args.integration_worktree,
            claim_worktrees=claim_worktrees,
            succeeds_epoch_id=args.succeeds_epoch_id,
            successor_reason=args.successor_reason,
        )
    if args.command == "verify-repository":
        return ParallelStateStore(args.target).verify_repository(args.item_id)
    if args.command == "classify-intent-entry":
        if args.input is None:
            gaps = []
        else:
            value = load_json(args.input)
            if not isinstance(value, dict) or set(value) != {"gaps"}:
                raise ContractError("HV2-INTENT-CLASSIFY-INPUT", str(args.input))
            gaps = value["gaps"]
        return classify_entry(args.consequence, gaps)
    if args.command == "init-intent-home":
        return IntentStore(args.target).initialize(args.authority_home_id, args.observed_at)
    if args.command == "create-intent-draft":
        return IntentStore(args.target).create_draft(
            args.intent_id,
            args.sequence,
            args.observed_at,
            load_json(args.input),
            inject_at=args.inject_at,
        )
    if args.command == "show-intent":
        return IntentStore(args.target).show(args.intent_id, args.revision_id)
    if args.command == "accept-intent":
        has_id = args.supersedes_selection_id is not None
        has_sha = args.supersedes_selection_sha256 is not None
        if has_id != has_sha:
            raise ContractError("HV2-INTENT-SUPERSEDE-OPTION", "both supersede fields are required")
        supersedes_ref = None
        if has_id:
            supersedes_ref = {"id": args.supersedes_selection_id, "sha256": args.supersedes_selection_sha256}
        return IntentStore(args.target).accept(
            args.intent_id,
            args.revision_id,
            args.revision_sha256,
            args.acceptance_id,
            args.actor,
            args.observed_at,
            supersedes_ref,
            inject_at=args.inject_at,
        )
    if args.command == "verify-intent":
        return IntentStore(args.target).verify(args.intent_id)
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
        if isinstance(result, dict) and result.get("classification") == "conflict":
            return 12
        if isinstance(result, dict) and result.get("classification") == "stale":
            return 13
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
