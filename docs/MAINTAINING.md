# Maintaining

Current document authority is indexed in [README.md](README.md). This source supports only the single-home `umbrella-1` development profile.

## Source Layout

- `hv2`: isolated installed launcher and explicit trusted source entry.
- `src/hv2ref/cli.py`: source/installed commands and exit codes.
- `workspace.py`: root format, target classification, cooperating writer guard.
- `work.py`: content observations, Work graph, publication and decisions.
- `intent.py`: guided intent validation, graph and publication.
- `umbrella.py`: direct-child composition, captured references and history/current predicates; no scheduler.
- `product.py`: exact inventory, binding, lifecycle and recovery.
- `view.py`: read-only GFM projection and bounded document observations.
- `adapters/harness-v2-work/SKILL.md`: manual natural-language entry guidance.
- `jsonio.py`, `errors.py`: canonical JSON, durability primitives and errors.
- `tests/`: stdlib contract tests, installed CLI fixtures and bounded independent auditor.
- `receipts/`: immutable historical evidence; presence is not current qualification.

Generation modules and old stores/commands are removed. Source-only generation contracts retain historical meaning, not executable support. Parallel-process, interruption and unavailable-evidence checks have bounded N4 evidence; legacy test removal alone never discharged those obligations.

## Validation

For a fixed candidate and each OS/runtime/build combination being qualified, run in an isolated environment. The version allowlist does not mean that every combination is qualified; see [Security and Support](SECURITY-AND-SUPPORT.md). The uncalibrated suite commands are:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -B -m unittest discover -s tests -v
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -B -O -m unittest discover -s tests -v
git diff --check
```

Child interpreters require the environment bytecode setting as well as `-B`. Check for unexpected source artifacts after testing. Lifecycle changes require actual fresh Git/non-Git targets, init/update/rollback round trips, repair/detach, interrupted prefixes, drift, unsafe-path refusal, secret-sentinel invariance, and plain-reader evidence. Run potentially mutating tests without real credentials or network in a constrained runner. Test worktrees alone are not sandboxes.

## Validation Frequency And Native Timeouts

Ordinary adopter intent/Work use does not require the product development suite. During development, choose checks by the changed behavior:

- Non-shipped prose: links, rendering and claim consistency.
- Local view/help changes: focused tests and shared-boundary regression. Shipped documents/adapters also require managed-inventory and consumer-path checks.
- Record, acceptance, writer, lifecycle or recovery changes: positive/refusal/interruption/recovery cases and complete normal/parent-optimized regression.
- Tests or runner changes: verify the altered assertions, collection, fixture, isolation and execution semantics. A safety-oracle change belongs to safety validation; preserve the previous complete-run evidence separately from focused evidence for the new test source.
- Runtime/platform additions: fixed focused and complete runs on the new combination, plus relevant existing-environment regression.
- Release candidate: complete fixed-candidate regression and exact-artifact lifecycle smoke. Focused evidence during iteration does not waive this gate.

Use focused checks during iteration and run the necessary complete matrix when the candidate stabilizes. Repeat a completed identical run only for a new change, failure or concrete unresolved concern. Preserve source/control/runtime identities and do not label an earlier source's pass as a fresh pass for a modified source.

Earlier native qualification used a calibrated runner that replaced only explicitly supplied 45-second subprocess timeouts with 240 seconds; the original budgets and observations remain historical evidence. Later isolated A/B work identified repeated process-spawn overhead when Seatbelt denied listing `/dev/fd`. The recorded N4 qualification used a new runner policy allowing only `file-read-data` on literal `/dev/fd`, with network denial and write boundaries retained. It ran 424 unique test IDs in each of normal and parent-optimized modes without timeout substitution; both passed with no skips or expected failures. The two modes together took about 38 minutes for that source/runtime, not a future duration guarantee.

Freeze source, test IDs, controller and policy bytes for each candidate. Use the recorded final GIL-enabled Homebrew CPython 3.14.7 identity for reproducing that qualification; check executable digest and child interpreter identity before and after, canary failures outside the write boundary, and network denial. Do not reuse the old calibrated timeout requirement as a current default or reduce file-descriptor limits to conceal runner cost. Preserve both historical and new runner evidence separately. No portable native sandbox runner is shipped with this candidate.
Set the next runner's total budget from measured duration plus an explicit margin before starting. Record current test/phase and completed IDs; a quiet log alone is not a hang. Budget exhaustion is incomplete execution, not an assertion failure or a pass. Observe natural process completion separately from process-group absence after cleanup. Parent `-O` does not propagate to installed launcher or auditor children.

For unexplained failures, preserve the original run and capture failing synthetic state before fixture cleanup. Non-reproduction does not establish a root-cause fix. An explicit bounded owner risk decision can remove a progress blocker while retaining the failure and a recurrence trigger; it does not authorize known integrity defects or turn that run into a pass.

## Release Inventory

`SERIAL_MANAGED_PATHS` in `product.py` defines 28 shipped files; `LEGACY_MANAGED_PATHS` retains the exact 27-path old history set. Canonical inventory names, byte counts and SHA-256 determine release identity. Exact membership includes directories; missing, extra, linked, reordered, or mismatched bytes fail. The launcher validates all ten importable modules before executing them. Tests, historical generation contracts and receipts are not shipped.

Keep inventory, bootstrap module allowlist, docs and detach tests aligned. Do not add project truth, configuration or secrets to the managed set. Updating launcher bytes requires the existing receipt-bound switch and independent-source recovery path. Release compatibility requires qualification; a valid digest is not compatibility proof.

## Reading Budget And Claims

The maintainer-only budget uses `tiktoken==0.13.0`, `o200k_base`: `AGENTS.md` at most 2,000 tokens; `AGENTS.md + README.md + docs/GETTING-STARTED.md` at most 4,000 tokens and three mandatory reads. Record exact files/tool/counts when measuring. It is not a runtime dependency and does not replace a fresh-reader exercise.

Commands and current docs change together. Public identity, license, version, distribution, native runtime admission and real adoption require their own evidence. Historical receipts are never rewritten to match a new source.

Runtime qualification uses an explicit patch allowlist, not a minimum-version promise. Later 3.14 patches, 3.15, prereleases and free-threaded builds require separate qualification. Optimized parent tests do not make installed launcher children optimized. Historical receipts retain their original runtime identity.

## Inventory Window Compatibility

New candidates declare `WORKSPACE_INVENTORY_ID = "umbrella-1"` once as a literal in the existing managed launcher. Packaging reads that declaration without importing candidate code. A declaration is not a trust credential; source identity and qualification remain necessary. The current managed set is 28 paths. The new reader retains the original 27-path human-1 and worker-1 history and rejects serial-1 or unknown windows.

Releases in the same inventory window must read each other's records and preserve their meaning in both directions. An incompatible semantic change requires a new inventory_id, an explicit transition design and human approval. After the first durable umbrella-1 receipt, downgrade to worker-1 or human-1 is refused even before any schema2 record exists. Test Q-created local and worker records after rollback to P; a matching window name alone does not establish compatibility.

The recorded N4 source completed bounded worker execution, complete 424-ID regression in both modes and exact-artifact checks. A later documentation or source change has a different release identity and requires the fixed-candidate gate above. This document does not attest its own current bytes as qualified; use the separate immutable qualification receipt and artifact digest. Previous human-1 evidence does not qualify worker-1.

## Umbrella Candidate Boundary

The current umbrella-1 change is in development. Focused evidence is separate from the required complete normal/parent-optimized matrix, exact-artifact transition, recovery and final review. Do not promote earlier worker-1 receipts or a focused pass to qualification of this checkout. Include schema2 intent/Work round trips, ordinary schema1 behavior, mixed old/new inventory history, old-artifact refusal, Q-created records on P, and detach/plain reading.

The internal runtime seam returns `binding_ref`, `launcher_sha256`, and `inventory_id`. Schema2 writes require umbrella-1; older two-field fixture doubles remain usable only for ordinary schema1 tests. Parent record schema2 does not change identity, selection, current, ticket, decision or manifest versions.
