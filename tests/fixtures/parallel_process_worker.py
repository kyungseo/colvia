from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

import hv2ref.parallel as parallel_module
from hv2ref.errors import ContractError, InjectedCrash
from hv2ref.parallel import ParallelStateStore


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True) + "\n").encode("utf-8")


def write_once(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as handle:
        handle.write(canonical_bytes(value))
        handle.flush()
        os.fsync(handle.fileno())


def wait_at_barrier(spec: dict[str, Any]) -> None:
    barrier_root = Path(spec["barrier_root"])
    barrier_root.mkdir(parents=True, exist_ok=True)
    participant = spec["participant"]
    write_once(barrier_root / f"{participant}.ready", {"participant": participant, "pid": os.getpid()})
    deadline = time.monotonic() + float(spec.get("barrier_timeout", 15.0))
    release = barrier_root / "release"
    while not release.is_file():
        if time.monotonic() >= deadline:
            raise RuntimeError("barrier-timeout")
        time.sleep(0.01)


def install_barrier(spec: dict[str, Any], store: ParallelStateStore) -> None:
    mode = spec.get("barrier_mode")
    if mode == "claim-after-write":
        original = parallel_module.write_new_json
        claim_name = f"{spec['parameters']['claim_id']}.json"

        def wrapped(path: Path, value: Any) -> dict[str, str]:
            result = original(path, value)
            if path.parent.name == "claims" and path.name == claim_name:
                wait_at_barrier(spec)
            return result

        parallel_module.write_new_json = wrapped
    elif mode == "finalize-before-switch":
        original = parallel_module.replace_json
        active_path = store._active_integration_path()

        def wrapped(path: Path, value: Any) -> dict[str, str]:
            if path == active_path:
                wait_at_barrier(spec)
            return original(path, value)

        parallel_module.replace_json = wrapped
    elif mode == "finalize-after-arbitration":
        original = parallel_module._write_exact_json
        epoch_id = spec["parameters"]["epoch_id"]

        def wrapped(path: Path, value: Any) -> bool:
            result = original(path, value)
            if value.get("record_type") in {"finalization-arbitration", "finalization-successor"} and value.get(
                "epoch_id"
            ) == epoch_id:
                wait_at_barrier(spec)
            return result

        parallel_module._write_exact_json = wrapped
    elif mode not in {None, "none"}:
        raise RuntimeError(f"unknown-barrier:{mode}")


def run_action(spec: dict[str, Any]) -> dict[str, Any]:
    store = ParallelStateStore(Path(spec["target_root"]))
    install_barrier(spec, store)
    action = spec["action"]
    parameters = dict(spec["parameters"])
    if action == "claim":
        parameters["worktree_root"] = Path(parameters["worktree_root"])
        return store.claim_work(**parameters)
    if action == "finalize":
        parameters["integration_worktree_root"] = Path(parameters["integration_worktree_root"])
        parameters["claim_worktrees"] = {
            claim_id: Path(path) for claim_id, path in parameters["claim_worktrees"].items()
        }
        return store.finalize_work(**parameters)
    if action == "reassign":
        return store.reassign_claim(**parameters)
    if action == "verify":
        return store.verify_repository(**parameters)
    if action == "manual-fallback":
        claim_parameters = dict(parameters["claim"])
        claim_parameters["worktree_root"] = Path(claim_parameters["worktree_root"])
        claim = store.claim_work(**claim_parameters)
        verified = store.verify_repository(parameters["verify_item_id"])
        if claim.get("classification") != "pass" or verified.get("classification") != "pass":
            return {"classification": "degraded", "claim": claim, "verified": verified}
        return {
            "claim_id": claim.get("claim_id"),
            "classification": "pass",
            "generation": verified.get("generation"),
            "item_ids": verified.get("item_ids"),
        }
    raise RuntimeError(f"unknown-action:{action}")


def exit_code(result: dict[str, Any]) -> int:
    classification = result.get("classification")
    if classification == "conflict":
        return 12
    if classification == "stale":
        return 13
    if classification == "degraded":
        return 10
    if classification == "incompatible":
        return 11
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--spec", type=Path, required=True)
    parser.add_argument("--result", type=Path, required=True)
    args = parser.parse_args()
    spec = json.loads(args.spec.read_text(encoding="utf-8"))
    try:
        outcome = run_action(spec)
        code = exit_code(outcome)
        result = {
            "action": spec["action"],
            "classification": outcome.get("classification"),
            "exit_code": code,
            "outcome": outcome,
            "participant": spec["participant"],
            "pid": os.getpid(),
        }
    except ContractError as exc:
        code = 65
        result = {
            "action": spec["action"],
            "classification": "contract-error",
            "contract_code": exc.code,
            "detail": exc.message,
            "exit_code": code,
            "participant": spec["participant"],
            "pid": os.getpid(),
        }
    except InjectedCrash as exc:
        code = 75
        result = {
            "action": spec["action"],
            "classification": "injected-crash",
            "contract_code": exc.code,
            "exit_code": code,
            "participant": spec["participant"],
            "pid": os.getpid(),
        }
    except Exception as exc:
        code = 70
        result = {
            "action": spec.get("action"),
            "classification": "internal-error",
            "detail": f"{type(exc).__name__}:{exc}",
            "exit_code": code,
            "participant": spec.get("participant"),
            "pid": os.getpid(),
        }
    write_once(args.result, result)
    sys.stdout.buffer.write(canonical_bytes(result))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
