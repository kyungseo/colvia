# Maintaining

Entry-1 successor candidate; [qualification and activation remain pending](README.md#entry-1-candidate).

Current document authority is indexed in [README.md](README.md). This source supports only the single-home `entry-1` development profile.

## Source Layout

- `colvia`: isolated installed launcher and explicit trusted source entry.
- `src/hv2ref/cli.py`: source/installed commands and exit codes.
- `workspace.py`: root format, target classification, cooperating writer guard.
- `work.py`: content observations, Work graph, publication and decisions.
- `intent.py`: guided intent validation, graph and publication.
- `candidates.py`: bounded planning history, guarded writes and read-only candidate view; no execution authority.
- `umbrella.py`: direct-child composition, captured references and history/current predicates; no scheduler.
- `product.py`: exact inventory, binding, lifecycle and recovery.
- `view.py`: read-only GFM projection and bounded document observations.
- `adapters/colvia-work/SKILL.md`: manual natural-language entry guidance.
- `jsonio.py`, `errors.py`: canonical JSON, durability primitives and errors.
- `tests/`: stdlib contract tests, installed CLI fixtures and bounded independent auditor.
- `receipts/`: immutable historical evidence; presence is not current qualification.

Use [Records And Retention](REFERENCE.md#records-and-retention) for the common recording default. Routine development keeps its plan, selected checks, result and limits in the existing Work narrative; a new receipt, source copy or validation archive is not required for each run. Add exact raw evidence only for an identified failure, qualification, reuse or delivery consumer, with its end condition. This does not remove any existing authority, historical evidence or recovery prerequisite.

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
- Release candidate: a complete regression anchor plus justified checks for every cumulative change, and exact-artifact lifecycle smoke. Run a new complete matrix when the anchor cannot support the changed behavior or environment; candidate naming or a whole-source digest change alone is not a reason to repeat it.

Use focused checks during iteration; finish related corrections and documentation before freezing the candidate. Repeat a complete matrix for changed risk, an invalidated oracle, a failure or a concrete unresolved concern, not for each small edit. Source/control/runtime digests still detect input drift within a run; they do not automatically determine the next run's scope.

### Evidence Reuse And Selection

Reuse is an explicit Driver assessment in the existing verification plan/result, not an automatic pass or a new registry. Compare the candidate cumulatively against the complete-run anchor, not merely against the last commit. When preserving a complete-run anchor for qualification or planned reuse, retain its original receipt, exact source/artifact identities, ordered discovered and executed test IDs, both mode results, runtime/build, environment, runner/policy, budgets and known failures. Keep that evidence once at its existing location; do not duplicate it for each later check. A narrative can serve as the original receipt only if it contains all applicable anchor information listed here and its exact version is fixed and recoverable through a Git commit or equivalent immutable retained bytes; a mutable working summary is insufficient. This requirement does not make every routine run a future anchor. Missing or unverifiable evidence cannot support the reuse that needs it.

Classify by behavior, not filename extension. Unchanged executable bytes are necessary for an unchanged-code claim but not sufficient to waive verification: shared fixtures, imports, discovery/order, assertions, runner isolation, packaging, dependencies and agent instructions can change behavior. For test-only changes, check changed tests and affected consumers; retain a separate result for new assertions. For shipped prose-only changes, check claims, links/rendering, exact inventory and installed/update/repair/detach consumption. Entry/adapter instructions additionally need affected entry/resume behavior checks. Acceptance, record or recovery semantics and new runtime/platform combinations still require the complete matrix described above. If interaction or isolation effects cannot be bounded, run the affected complete matrix.

Cover four points briefly in the existing plan before execution, without requiring a separate file or fixed fields: (1) cumulative change and risk, (2) evidence reused and missing, (3) new checks and why narrower checks suffice or do not, (4) exact IDs/modes and expected duration/budget. The Owner's existing scope and execution authorization still applies; this adds no repeated acceptance gate. A full-rerun proposal explains which risk the inherited results do not cover.

Report three separate categories: executed on this candidate, inherited from an identified anchor, and unverified/unresolved. For a selected run, identify the selected/executed tests and collection scope; preserve full ordered discovery when the qualification or reuse claim needs it. A focused run cannot be reported as a complete run even if every selected test passes. Retain skip, expected failure, interruption and unexplained-failure limits. Non-recurrence is not a fix. The new artifact must have its own inventory and lifecycle evidence because changed shipped bytes change release identity. Never relabel an old PASS as a fresh execution or as proof for a new OS/build. General usability and adopter acceptance remain separate.

The following native runner observations are historical. Their full source/runtime/runner inputs are not bundled here, and the old-generation `receipts/` are not their qualification anchor. [Security and Support](SECURITY-AND-SUPPORT.md#historical-observations) identifies that availability limit. Do not use these summaries alone to select a reused PASS or claim a reproduced run.

Earlier native qualification used a calibrated runner that replaced only explicitly supplied 45-second subprocess timeouts with 240 seconds; the original budgets and observations remain historical evidence. Later isolated A/B work identified repeated process-spawn overhead when Seatbelt denied listing `/dev/fd`. The earlier worker-integration qualification (called N4 in historical records) used a new runner policy allowing only `file-read-data` on literal `/dev/fd`, with network denial and write boundaries retained. It ran 424 unique test IDs in each of normal and parent-optimized modes without timeout substitution; both passed with no skips or expected failures. The two modes together took about 38 minutes for that source/runtime, not a future duration guarantee.

Keep source, test IDs, controller and policy bytes unchanged during each qualification run and retain the exact recoverable inputs needed by its named consumer. A Git revision or existing durable artifact can preserve them; freezing a run is not an instruction to copy every source tree into a permanent archive. Use the recorded final GIL-enabled Homebrew CPython 3.14.7 identity for reproducing that qualification; check executable digest and child interpreter identity before and after, canary failures outside the write boundary, and network denial. Do not reuse the old calibrated timeout requirement as a current default or reduce file-descriptor limits to conceal runner cost. Preserve both historical and new runner evidence separately. No portable native sandbox runner is shipped with this candidate.
Set the next runner's total budget from measured duration plus an explicit margin before starting. Record current test/phase and completed IDs; a quiet log alone is not a hang. Budget exhaustion is incomplete execution, not an assertion failure or a pass. Observe natural process completion separately from process-group absence after cleanup. Parent `-O` does not propagate to installed launcher or auditor children.

For unexplained failures, preserve the original run and capture failing synthetic state before fixture cleanup. Non-reproduction does not establish a root-cause fix. An explicit bounded owner risk decision can remove a progress blocker while retaining the failure and a recurrence trigger; it does not authorize known integrity defects or turn that run into a pass.

## Release Inventory

`SERIAL_MANAGED_PATHS` in `product.py` defines 29 shipped files; `UMBRELLA_MANAGED_PATHS` retains 28 paths; `LEGACY_MANAGED_PATHS` retains the exact 27-path old history set. Canonical inventory names, byte counts and SHA-256 determine release identity. Exact membership includes directories; missing, extra, linked, reordered, or mismatched bytes fail. The launcher validates all eleven importable modules before executing them. Tests, historical generation contracts and receipts are not shipped.

Keep inventory, bootstrap module allowlist, docs and detach tests aligned. Do not add project truth, configuration or secrets to the managed set. Updating launcher bytes requires the existing receipt-bound switch and independent-source recovery path. Release compatibility requires qualification; a valid digest is not compatibility proof.

## Reading Budget And Claims

The maintainer-only budget uses `tiktoken==0.13.0`, `o200k_base`: `AGENTS.md` at most 2,000 tokens; `AGENTS.md + README.md + docs/GETTING-STARTED.md` at most 4,000 tokens and three mandatory reads. Record exact files/tool/counts when measuring. It is not a runtime dependency and does not replace a fresh-reader exercise.

Commands and current docs change together. Public identity, license, version, distribution, native runtime admission and real adoption require their own evidence. Historical receipts are never rewritten to match a new source.

Runtime qualification uses an explicit patch allowlist, not a minimum-version promise. Later 3.14 patches, 3.15, prereleases and free-threaded builds require separate qualification. Optimized parent tests do not make installed launcher children optimized. Historical receipts retain their original runtime identity.

## Inventory Window Compatibility

New candidates declare `WORKSPACE_INVENTORY_ID = "entry-1"` once as a literal in the existing managed launcher. Packaging reads that declaration without importing candidate code. A declaration is not a trust credential; source identity and qualification remain necessary. The current managed set is 29 paths with `colvia` and `adapters/colvia-work/SKILL.md`. The reader retains the literal old 29-path planning-1/checkout-1 inventories, exact 28-path umbrella-1 and original 27-path human-1/worker-1 history, and rejects serial-1 or unknown windows. Do not derive old memberships by renaming the new set.

Releases in the same inventory window must read each other's records and preserve their meaning in both directions. An incompatible semantic change requires a new inventory_id, an explicit transition design and human approval. After the first durable entry-1 switch receipt, downgrade to checkout-1, planning-1, umbrella-1, worker-1 or human-1 is refused even before any candidate record exists. Test Q-created local and worker records after rollback to P; a matching window name alone does not establish compatibility.

The recorded N4 source completed bounded worker execution, complete 424-ID regression in both modes and exact-artifact checks. A later documentation or source change has a different release identity and requires the evidence assessment and exact-artifact checks above; it does not automatically invalidate every prior regression result. This document does not attest its own current bytes as qualified; use the candidate's separately identified immutable qualification evidence and artifact digest. An equivalently complete, fixed narrative can serve as that original receipt under [Evidence Reuse And Selection](#evidence-reuse-and-selection); a routine summary cannot. Previous human-1 evidence does not qualify worker-1.

## Umbrella Candidate Boundary

The umbrella-1 development result has recorded review, Driver disposition and Owner acceptance with limitations. The earlier fixed source passed complete normal/parent-optimized regression; the later test-source follow-up has focused evidence. Keep those identities separate. The exact release candidate still requires the complete regression anchor and cumulative change coverage described above, plus exact-artifact transition and recovery qualification; do not describe development acceptance as release qualification. Do not promote earlier worker-1 receipts or a focused pass to qualification of this checkout. Include schema2 intent/Work round trips, ordinary schema1 behavior, mixed old/new inventory history, old-artifact refusal, Q-created records on P, and detach/plain reading.

The internal runtime seam returns `binding_ref`, `launcher_sha256`, and `inventory_id`. Current installed writes require entry-1; the internal schema2 seam retains umbrella-1, planning-1 and checkout-1 fixture support alongside entry-1; older two-field fixture doubles remain usable only for ordinary schema1 tests. Parent record schema2 does not change identity, selection, current, ticket, decision or manifest versions.

## Adopter Impact At Development Closeout

After completing and validating a Harness source change, the agent assesses its effect on known adopters and proactively reports one outcome: update recommended, no update currently needed, or installation state unverified. Assess once for the completed change, not after every source edit; use existing Work, release and adopter evidence rather than creating a registry or an extra mandatory document.

For a recommended update, report the target, observed installed release identity, exact candidate source/artifact identity and qualification state, expected effect, verification method, and rollback/recovery limits. Do not equate a source commit with an installed release digest. If the candidate is not fixed or the installed state cannot be verified, state that explicitly and identify the next check. Reconfirm state before applying; a snapshot is not permanent authority. A target without a current installation needs an adoption proposal, not an update claim.

Apply only after explicit Owner approval for that target and candidate, through the existing preview/confirmation procedure in [Operations](OPERATIONS.md). Verify the resulting binding, project-state preservation and relevant changed behavior, and link the result to the original change. Approval of source work, its completion or a merge is not adopter-update approval. A deferred update records the reason and re-evaluation trigger in the existing completion report; it does not force source work to remain open unless its agreed completion criteria require actual application.

Do not add automatic monitoring, bulk updates, Core management state or an additional acceptance gate. Keep target identifiers and installation observations in the private task report; the shipped instructions remain generic.

## Checkout Proof And Detach Versions

Only a verified active checkout-1 or entry-1 inventory enables the unchanged CRLF exception. Publication, same-intent rebind, acceptance/resume and view inspection use that verified value; absent, older or unknown windows keep exact-blob proof. Raw manifests and changed-path recovery are unchanged. Git must support `check-attr --source`; no minimum Git version is inferred. Live attributes/capability changes can refuse pending recovery until the original conditions are restored. Existing cancellation rules remain applicable; completed decision replay preserves recorded meaning while view reports fresh observations separately.

New detach plans and their enclosing receipts both use schema 3. Keys and null candidate release remain; removal validates `colvia`, each retained release's exact inventory, and retired-entry collision preservation. Readers retain paired schema 1/2 and reject mixed/unknown/non-integer versions; current writers and recovery require schema 3. This version boundary keeps retained old detach writers from consuming entry-1 detach prefixes. Preserve old bytes; legacy detach recovery requires the exact retained old source. The independent stdlib auditor checks paired versions and preserved inventory/bytes, not full Work/candidate semantics.

## Entry-1 Candidate Validation Boundary

Entry-1 init/repair retain schema 1; update/rollback use paired schema 2, with `remove` containing exact old `hv2` only for the allowlisted checkout-1 transition and empty for same-entry switches. Validate both the ordinary lifecycle and [transition-specific admission/publication/replay](WORKSPACE-CONTRACT.md#entry-1-admission-and-publication), including captured-child references, OLD writer refusal, collisions and synchronization. A production runtime result without a valid `inventory_id` refuses; injected verifier doubles remain test-only seams.

This P3 document alignment does not issue an exact-artifact qualification receipt. Exact token counts are unmeasured here; the P4 plan must fix the stated tokenizer environment and measure the existing AGENTS/combined reading limits. Lines/bytes and readability review are not token-budget PASS. If measurement requires further document changes, identify the affected successor hashes and revalidation/review before using them as final candidate evidence.
