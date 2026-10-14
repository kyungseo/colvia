# Colvia Entry Implementation And Verification Plan

Date: 2026-10-09
State: R0 completed; corrected P0a authoring proposal awaits Owner approval; implementation and execution not approved
Risk: L3; one source-owned implementation task after plan approval

## P0a Handoff — 2026-10-09

The Owner subsequently approved P0a authoring only. [CHORE-20261009-002](CHORE-20261009-002-colvia-verification-controls.md) now owns that scope and progress. The plan and R0 below retain their historical reviewed/prepared meaning; pending approval statements describe their checkpoint. No runtime execution or product implementation is authorized by this handoff.

## Conclusion And Authorization

Implement C1 runtime/tests and C2 current instructions as one entry-1 candidate, then qualify and review the fixed result. Do not release an intermediate launcher/adapter combination. [DR-0004](../decisions/DR-0004-colvia-managed-entry-and-one-way-transition.md) owns the accepted A design; [C0 closeout](CHORE-20261009-001-colvia-entry-contract.md#owner-acceptance-and-c0-closeout--2026-10-09) is completed document work and remains unchanged. M3 is still the active contract.

After the Driver proposed preparing this implementation/verification plan and its separate R0 execution boundary, the Owner replied “진행하자”. This authorizes read-only preparation and this source-only note. It does not authorize a new reviewer transmission, runtime/test/runner edits or execution, activation, Git publication or adopter mutation. Earlier C0 CLI review allowances are exhausted. This note is the sole preparation/review record for the new scope, under Contributing's pre-task procedure; no task ID or index selection is allocated now. On explicit P0a authoring-plan approval, allocate the next available source task ID, link this note and designate that record as the sole implementation progress owner. Do not reopen C0 or add a second central implementation ledger.

## Fixed Inputs And Evidence

- Source base: `238514686078ce1564010a7b69013f48a635c57c`; tree `80abba08dfa635d2a0cf8b40a85546e797d0a4ae`.
- Accepted DR-0004 SHA-256: `799d45740ba00fe7722df3c6caec1c9de8898f2e1b442cca5ab8a08183726ea7`; C0 task SHA-256: `e60681aa486beefe06803158847d1f3b0f82e866f26f4ebba7ddd9cb00b3e9a0`.
- The four existing uncommitted C0 documents are inputs, not implementation. Preserve their exact accepted copies; only this new note is created in this preparation.
- The single audited predecessor is `product-release-8bd0eeac55fb0af92b61a7a3`, complete SHA-256 `8bd0eeac55fb0af92b61a7a36a98adb9957b880c791b957b20c319a51c5577f3`, checkout-1. No known installation is assumed to match it.
- Read-only source/caller and AST test inspection was performed, followed by the static R0 recorded below. No product import, test discovery, runner canary, old-writer counterexample or runtime suite was executed. AST definitions are not discovered/executed tests.
- Historical passing summaries are context only; no complete-run PASS is reused for this entry/lifecycle change. Normal and parent-optimized complete runs and exact-artifact lifecycle checks are required after convergence.

## Scope And Implementation Order

| Step | Change | Exit condition |
| --- | --- | --- |
| P0a: Author controls only | One source task owns runner/controller/policy, exact offline legacy acquisition procedure, numbered prefix oracle and execution map drafts; no execution or runtime/test edits | Owner approves this bounded authoring scope first; outputs live outside managed inventory and test discovery |
| P0b: Review exact controls | R0 of actual controller, policy, command allowlist, acquisition and test-oracle design | Separate named review authorization; Driver dispositions; exact execution approval still required |
| P0c: Validate controls | Acquire/verify OLD under a separate bounded acquisition step before dependent test loading; then isolation/topology/runtime canaries, real base collection and base smoke | Named execution approval; fixed controls/source; runner result R1 and Owner acceptance before P1; no inferred waiver |
| P1: Reader and identity foundation | Freeze old path tables; new entry-1 mapping, paired versions and bootstrap/source profile; migrate all proof callers and fixture seams | Old inventories remain independent literals; no arbitrary caller-supplied exclusion; missing production inventory_id fails closed |
| P2: Transition and recovery | Admission, S1–S6 plus physical prefixes, exact old retirement, B1 mode, lifecycle refusals and schema-3 detach | Focused positives/refusals, actual old-executor controls and interruption outcomes match A; no project-record rewrite |
| P3: User and normative text | Current CLI/view/help, adapter, eleven-member normative successor and EN/KO consumers | One internally consistent candidate; history/current instructions distinguished; exact amendment diff/table ready but not activated |
| P4: Qualification and result review | Freeze candidate; complete normal/parent-O suites; exact-artifact smoke; R1 and Driver dispositions | Owner accepts exact result and separately activates named normative successor; generic adopter impact reported |

P0 is a prerequisite, not a claim that a runner is already available. No product coding starts under a generic approval while actual runner controls, test collection or proof boundary are unresolved. This staged plan avoids inventing exact future source/test digests before those bytes exist. Each later fixed-input gate records their values in the one owning task.

## Closed File And Caller Inventory

These are the proposed edit boundaries, not permission to rewrite every listed file. Any additional runtime module, schema field, predecessor release or behavior needs a scope/contract disposition first.

| File or bounded set | Required change and caller obligation |
| --- | --- |
| Root `hv2` → `colvia` | New literal inventory declaration, installed root/payload path verification, module allowlist and explicit independent-source mode. No wrapper/alias or implicit fallback |
| `src/hv2ref/product.py` | Literal per-window path/launcher/adapter mapping; candidate/release verification; `_switch_plan_shape`, `_switch_binding_receipt`, `_workspace_product_once`, `require_workspace_runtime`; init/status; `_lifecycle_truth`, switch preview/preflight/apply; repair expected/preflight/apply; all detach shape/order/observation/apply paths |
| `src/hv2ref/work.py` | Carry verified inventory_id through snapshot, changed-path protection, external required refs and worker source proof; CRLF capability entry-1; WorkStore runtime/umbrella/worker gates and all publish/prepare/apply/recovery calls. Test doubles remain explicit test seams, never a production two-field fallback |
| `src/hv2ref/intent.py` | Three runtime-backed `_live_external_refs` callers and the WorkStore runtime seam must carry the verified entry identity; the separate bound-intent historical-ref call at base line 258 keeps explicit None/no live launcher exclusion; retain intent schemas and authority gates |
| `src/hv2ref/workspace.py` | Init plan/reference allowlists and current-window admission; retain root identity, lock namespace, path/topology/runtime validation and durability semantics outside named transition primitives |
| `src/hv2ref/candidates.py` | Current writer window gate; preserve request/store schema and binding recheck |
| `src/hv2ref/view.py` | Two snapshot sites, worker proof and changed-path preflight; current manual/adapter discovery and emitted commands; report retired-entry collision without falsely asserting lifecycle readiness |
| `src/hv2ref/cli.py` | Installed display name and explicit entry-1 source profile; preserve stable HV2 codes; path-specific diagnostics and exit mapping |
| `tests/fixtures/product_plain_auditor.py` | Independent literal old/new detach membership, schema pairing, root payload hash relation and exact deletion suffix; no production verifier imports |
| Existing 26 `tests/test_*.py` files, only affected cases | Update current fixtures/expected commands without weakening old-window controls; inspect imported/re-exported classes and verifier doubles. Preserve assertion semantics; no blanket replacement of all hv2 literals |
| New `tests/test_entry_window_transition.py` | Named transition/control/prefix/local/worker/retired-entry cases listed below; test-local helpers or one fixture helper only if reviewed in P0/P1 scope |
| `adapters/harness-v2-work/SKILL.md` → `adapters/colvia-work/SKILL.md`; 11 normative members below; existing current entry/manual consumers | C2 only, preserving claims and exact historical records |

`src/hv2ref/__init__.py`, `errors.py`, `jsonio.py` and `umbrella.py` are inspected/read-only inputs by default. In particular do not generalize the shared immutable writer to make S1/S2 torn bytes recoverable: that would change accepted T-A. No package rename, new dependency, global registry, automatic rebind or project-entry rewrite.

Static call closure at the base is in the appendix. Before coding, extend the same AST/literal scan to tests and imported aliases, document every verifier double and retain the runtime production gate. At implementation closeout repeat it against the candidate; an empty text search alone does not prove semantic closure.

## Normative Successor And Consumer Map

The exact normative set remains eleven members. For each row P3 records old M3 hash, new hash, precise amended clauses and unchanged meaning in the implementation record; changed artifact identity is separately computed. No new hashes are fabricated in this plan.

| Member | Required delta |
| --- | --- |
| `docs/WORKSPACE-CONTRACT.md` | entry-1 mapping, switch schema 2/detach schema 3, admission and durable sequence; unchanged record/root schemas |
| `docs/GENERAL-WORK.md` | Verified mapped entry exclusion; local/parent admission and actual S6 comparison; worker rebind/resubmit and preserved old result meaning |
| `docs/GUIDED-INTENT-FORMATION.md` | Current entry/required-ref restrictions; unchanged intent authority and schemas |
| `docs/REFERENCE.md` | Source profile and installed commands; exact schema pairs, refusal/diagnostic/exit behavior and retired-entry observation |
| `docs/OPERATIONS.md` | Allowlisted transition, quiescence, S1 one-way boundary, first-release no rollback, exact source recovery and external restore limits |
| `docs/MANUAL-OPERATION.md` | Mixed-history plain reading, schema-3 detach; old-source-only recovery for old prefixes |
| `docs/SECURITY-AND-SUPPORT.md` | Same runtime/account/platform boundary; atomic mode/prefix assumptions, torn S1/S2 and power-loss limits; no new qualification claim before evidence |
| `docs/MAINTAINING.md` | 29-file new/old literal membership, current entry, verification and new artifact evidence |
| `docs/GETTING-STARTED.md` | New init versus exact old migration; current adapter; worker baseline/Git action separation and recovery |
| `adapters/colvia-work/SKILL.md` | Replaces the old adapter member; current verified discovery, first Work/resume, exact approval and error instructions |
| `docs/development/CHECKOUT-1-STRUCTURE.md` | Named entry/switch/detach/reader successor clauses; preserve source-only role and historical filename unless separately agreed |

Consumers: root README/AGENTS/CLAUDE, docs/README and CONCEPTS, PRODUCT-CAPABILITIES.json, six existing files in each of manual/en and manual/ko. Classify current executable instructions, old-window examples and frozen history; preserve HV2-, .hrn and hv2ref. No zero-hv2-occurrence target. Contributing's accepted procedure and historical decisions/receipts/generation contracts remain unchanged. At activation append named DR-0002/0003 amendment records outside protected ranges and make only the authorized Development Index clause/navigation change; do not rewrite DR-0003's accepted first 25,338 bytes. DR-0004 activation and those amendments need exact Owner result/activation acceptance after P4.

Retired-entry diagnostic proposal for R0: preserve the verified current binding, display an explicit lifecycle-blocked collision observation; lifecycle writes return existing HV2-WORKSPACE-PRODUCT with precise guidance. Status/doctor/view classification and individual exit codes must be fixed against existing command contracts before P1/P3 approval; do not mark an unresolved mapping as implemented or invent a new persistent state.

## Required Tests And Independent Oracles

| Group | Minimum cases and observation |
| --- | --- |
| Literal history | Read exact 27/28/29 old membership, mixed releases and versions; derive from preserved baseline bytes, never from new membership substitution |
| Four executors | Old installed/old independent/new installed/new independent at every S state; old init/switch/repair/detach and record writers refuse after S1 without mutation; late old writers waiting on the common lock recheck after acquiring it |
| Admission | Allowlisted old release only; reject unknown predecessor, old pending lifecycle and persisted record transactions; collision/aliases/links/modes, tracked colvia or descendants, ignore rules including external inputs; compare before/after bytes on refusal |
| Local and parent | Unfinished selected schema1 local/schema2 parent: renamed-path dependencies refuse; manifest result versus actual admission baseline; multiple distinct baselines/drift refuse; actual S6 comparison after restart. No selected local means vacuous comparison, not whole-project preservation proof |
| Worker | Unfinished/orphan records alone allowed under W-A; quiescence and pending refusal; old committed proof rejected; separately retained synthetic new control baseline plus explicit human rebind/resubmit succeeds; old tickets fail binding |
| Replay | B1 complete with unchanged truth succeeds; subsequent changed truth makes historical content comparison unavailable while keeping B1 current and normal fresh Work checks possible |
| Retired entry | Reappearing hv2 preserved as project content; lifecycle/repair/detach refuse; ordinary record paths use normal content proof and only verified colvia exclusion |
| Physical prefixes | S1 receipt and S2 staging byte tears preserve non-pass; N exclusive create/short-write/0600/reopen/append/fsync/0755/dir-sync; old unlink and root sync; binding.next exclusive creation/partial/complete/fsync/replace/two-directory sync; unexpected partial executable, hardlink, symlink, unknown staging member and B1+binding.next refuse |
| Lifecycle | Git/non-Git fresh init; exact old→new transition; two distinct new candidates for update/rollback; cross-window rollback refusal; exact active repair and externally observable repair limits; mixed-history detach and independent plain audit |
| Semantics and safety | Existing intent/Work/parent/candidate checks, CRLF/attributes, secret-sentinel bytes and project authority preservation, no network/outside writes; current EN/KO first-work/resume/recovery/discovery |

For byte tears use bounded test-local syscall fault seams plus child-process termination at the new physical boundaries. Test hooks do not create an operator command or production recovery permission. A complete stage boundary injection cannot substitute for a partial write test. Assert expected preserved refusal for T-A tears; never delete receipts to obtain a pass. Process termination and simulated faults are distinct from power-loss proof. Keep old subprocesses on the exact retained source with their original code; pause them at a test harness synchronization boundary without modifying that old implementation. If that cannot cover late-lock writers safely, stop for a revised test plan.

Legacy acquisition after approval: reconstruct tracked baseline bytes from the fixed commit into a dedicated OLD input directory outside the test-writable EXEC subtree, verify complete source/29-member inventory and launcher hashes before running. Retain that fixture for the named transition/old-writer test consumer through qualification/R1, then rely on the durable Git commit and minimal fixture provenance where sufficient. Current-generated fixtures are prohibited as the only old-source oracle. No unrelated real project state is copied.

## Execution Boundary Proposal

The exact native runner is not shipped and has not been created for this task. Prior task-specific runners contain hard-coded paths and special diagnostic instrumentation; do not reuse their authority or monkeypatches. P0 prepares a small task-specific runner/controller and Seatbelt policy for a new bounded execution directory under the approved agent-worktree root; check registration, destination ownership and absence before creation. Keep the implementation checkout read-only to child tests; no temporary-directory sole copy of deliverables. The private invocation supplement records absolute execution/input/output paths; public-safe source uses symbolic SOURCE/OLD/EXEC/RUNNER names. OLD, SOURCE and reviewed controls are outside the test-writable EXEC subtree. A narrow acquisition phase may populate OLD before testing; the child-test policy then denies OLD writes. Hash OLD before and after each run. The execution container directory is a non-Git sibling under the approved root, not inside a repository/worktree or .hrn ancestor; validate this rather than assume the root name proves topology.

Observed host: macOS 27.0.1 arm64; final GIL-enabled Homebrew CPython 3.14.7, Py_GIL_DISABLED=0; executable SHA-256 `87d4df53fd91304be5bac391fb204643c36b7df2023c04a0953bcbc7d4fdf634`. Recheck binary/build and child interpreter before/after execution; this observation is not current artifact qualification or OS compatibility proof.

Proposed fixed runner interface: `collect`, `focused`, `complete-normal`, `complete-parent-O`, `artifact`; no arbitrary shell/command argument. Bind each mode to fixed commands, inputs and output paths. Collection uses the real unittest loader after isolation preflight, preserves its ordered IDs and reports duplicates and load failures. Do not silently deduplicate: document whether imported/re-exported tests are intentional; any changed collection algorithm/assertion needs R0/Owner scope. Full normal and parent-O runs use equivalent complete discovery and record actual IDs, skips/errors/failures. Installed children retain their own optimization state; parent -O does not propagate.

Underlying full commands, with the fixed CPython path substituted for PYTHON, cwd SOURCE and controlled environment:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src PYTHON -B -m unittest discover -s tests -v
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src PYTHON -B -O -m unittest discover -s tests -v
```

The controller may wrap unittest result reporting to record IDs and preserve failing synthetic fixtures before cleanup; it must not replace subprocess timeout values, assertions, skipped tests or discovery results. Exact implementation and policies are reviewed before execution. Focused mode uses a fixed selected-ID file produced from actual collection and the new cases above, not arbitrary user input. Artifact mode selects fixed IDs from the same reviewed transition test module/loader, with no second ad hoc scenario runner. Its factory loading, ordered IDs and required OLD identity are fixed in the controls; no unreviewed command expansion.

Environment must be constructed from an allowlist: fixed tool PATH, isolated HOME/XDG_CONFIG_HOME/TMPDIR under EXEC, C.UTF-8-compatible locale, TZ, bytecode controls and explicit PYTHONPATH; no inherited auth variables, SSH agent, Git credential helpers or user Git configuration. Fix the actual Git binary/path/version/digest, not a platform shim. Product git_environment removes GIT_* variables, so isolation relies on HOME/XDG and filesystem/service policy, not GIT_CONFIG_NOSYSTEM propagation. Canary Git configuration origins and check-attr --source capability under the actual child environment. Synthetic Git operations may init/commit/create worktrees only inside EXEC and are fixture actions, not source Git publication. Allow reads only for SOURCE, OLD, EXEC and required system/runtime tooling, with user credential directories denied; deny network including child processes; deny writes outside EXEC except required null device. No credential/keychain service access. Retain literal /dev/fd read-data only if the fixed policy needs it; do not broaden user-home access. Verify paths are disjoint and not linked before execution.

Canaries before test imports: in-boundary write succeeds; out-of-boundary file creation fails; synthetic forbidden secret read fails; network attempts fail; real credentials are never probed. Verify child inheritance, source digest stability, interpreter identity and file-descriptor behavior. A failed canary stops before discovery/tests. The static review must assess whether the platform policy actually expresses these guarantees; unknown service or filesystem access is an unresolved boundary, not a pass.

Proposed bounds for Owner approval: one P0 acquisition (300 seconds), one canary set (300 seconds), one base collection (300 seconds) and one fixed base seed smoke (1,200 seconds). Later collection is once per exact (controls, source digest) pair, at most eight collections including baseline and final candidate, 300 seconds each. Focused iteration has three named phase sets P1/P2/P3, one run each plus one correction rerun shared across all three: at most four runs of 1,200 seconds, 4,800 seconds total. One converged qualification candidate only: normal 5,400 seconds and parent-O 5,400 seconds, each once; artifact IDs 1,800 seconds once. No second qualification candidate/run or replacement control budget is implied. Historical 38-minute two-mode summary is not a calibrated current bound; 90 minutes per mode is a conservative provisional cap including the larger current suite. Record actual elapsed times and compare before launch. Do not raise budgets, silently resume/deduplicate or repeat the full matrix on cosmetic edits. On budget exhaustion stop, preserve completed IDs and exact failed/incomplete state, and obtain the bounded next decision. Controller timeout includes process-group termination/grace and verifies no surviving child; natural completion is reported separately. Progress reports remain at most 60 seconds apart without modifying the run.

## R0 Packet And Next Decision

Prepare a fixed, disclosure-checked packet containing this note, the accepted DR, C0 closeout/baseline inventory excerpts, Contributing review/authority procedure, Maintaining, and exact source/bootstrap/caller/auditor inputs. Record base, tracked diff hash and individual untracked input hashes outside the source public narrative. The first implementation R0 below identified remaining P0 controls. There is no actual runner-byte review yet and no runtime execution readiness claim.

Historical first-review proposal, now executed under the Owner approval below: one fresh no-tool Claude subscription R0, at most 600 seconds, for that fixed packet; no tests, file edits or external tools in the reviewer. Verify claude.ai/firstParty/pro immediately before invocation, report actual model/session and limitations, and stop on auth/billing mismatch. A later correction-confirmation round or actual-runner review is not silently included. Record response verbatim here with Driver dispositions. The next Owner choice is only P0a controls authoring. P0b exact-control review and P0c execution/result acceptance remain separate; runtime implementation remains behind those gates and the unresolved choices below. A reviewer verdict never selects or accepts the task for the Owner.

## Completion, Reversal And Stop Rules

Preparation completes when the source/contract/caller mapping, tests, runtime and bounded execution proposal, exact review input and remaining decisions are inspectable. Execution-ready is a later state: actual runner bytes/policy, real collected IDs, fixed fixture/candidate identities and isolation evidence must exist. Preserve this distinction in all reports.

Implementation completion requires converged C1+C2, all required executed evidence or explicit unresolved disposition, fixed normative successor and R1, then exact Owner result acceptance/activation. Preserve accepted historical clauses and unknown bytes throughout. Before application, source edits are reversible; after S1 product rollback to an old window is unavailable, and torn S1/S2 may require separately authorized external whole-target restoration. C0 has already accepted this cost; do not reopen it merely because it is inconvenient.

Stop for source/fixture drift, contract expansion, missing old source, wrong billing path, failed isolation, unknown ownership, unavailable proof, integrity discrepancy or exhausted bounds. Preserve and propose one bounded correction; no automatic retry, cleanup of unique evidence or test weakening. No adopter update recommendation can yet identify a qualified new candidate. Actual adoption, source Git/publication and namespace/branding rights remain separate.

## Preparation Checks And Preservation

Validate this note's links/rendering/disclosure/whitespace, input identities and that the original 29 managed files remain byte-identical to the base. Preserve the final note and fixed R0 packet outside the active checkout for the next reviewer/Owner until the approved task references them and Git or equivalent custody retains the necessary exact input. Keep existing accepted C0 recovery copies. Reproducible render/scan output need not be retained. The current worktree has concrete near-term implementation reuse and is retained; no cleanup is performed.

## Static Appendix

The following is AST inspection only. Runtime collection remains P0 work; inherited tests, factories and module aliases may make real discovery differ.

| Module | Locally declared test methods |
| --- | ---: |
| `test_candidates.py` | 38 |
| `test_checkout_window_transition.py` | 5 |
| `test_detach_topology_sharing.py` | 11 |
| `test_general_work.py` | 45 |
| `test_general_work_invariants.py` | 58 |
| `test_general_work_recovery.py` | 55 |
| `test_git_candidate_reuse.py` | 3 |
| `test_human_view.py` | 24 |
| `test_intent_observation_sharing.py` | 16 |
| `test_plain_auditor_boundary.py` | 1 |
| `test_productization.py` | 0 |
| `test_productization_safety.py` | 171 |
| `test_runtime_admission.py` | 7 |
| `test_topology_observation_sharing.py` | 14 |
| `test_umbrella.py` | 18 |
| `test_umbrella_lifecycle.py` | 4 |
| `test_umbrella_recovery.py` | 21 |
| `test_view_observation_sharing.py` | 15 |
| `test_workspace.py` | 33 |
| `test_worktree_checkout_bytes.py` | 23 |
| `test_worktree_execution.py` | 25 |
| `test_worktree_history.py` | 1 |
| `test_worktree_integration.py` | 1 |
| `test_worktree_pending_lifecycle.py` | 2 |
| `test_worktree_process_recovery.py` | 6 |
| `test_worktree_process_safety.py` | 2 |

Total local definitions: 599. Not a collected or executed count.

### Base Caller Locations

- `src/hv2ref/intent.py`: `_live_external_refs:258`, `_live_external_refs:369`, `_live_external_refs:397`, `_live_external_refs:403`.
- `src/hv2ref/view.py`: `verify_worker_sources:144`, `snapshot:149`, `preflight_changed_paths:151`, `snapshot:232`.
- `src/hv2ref/work.py`: `_snapshot_once:263`, `_snapshot_once:264`, `_preflight_changed_paths:569`, `_live_external_refs:1030`, `snapshot:1036`, `verify_worker_sources:1037`, `snapshot:1047`, `preflight_changed_paths:1048`, `_live_external_refs:1054`, `snapshot:1058`, `preflight_changed_paths:1059`, `snapshot:1066`, `preflight_changed_paths:1080`, `preflight_changed_paths:1093`, `_live_external_refs:1286`, `snapshot:1287`, `_live_external_refs:1348`, `snapshot:1349`, `_live_external_refs:1393`, `snapshot:1394`, `verify_worker_sources:1424`, `_live_external_refs:1427`.

### Existing Focused Seed IDs

These 16 concrete base IDs identify assertions to preserve/adapt and compare with real collection; they are not the complete focused set and do not cover new entry-1 behavior. P0 fixes selected IDs after actual collection, while P1 records new IDs before their execution. Missing or changed IDs must be explicitly dispositioned rather than silently omitted.

- `test_runtime_admission.RuntimeAdmissionTests.test_status_rejects_both_unsupported_identities_without_blocking_reads`
- `test_runtime_admission.RuntimeAdmissionTests.test_installed_record_entry_gate_precedes_input_and_preserves_truth`
- `test_runtime_admission.RuntimeAdmissionTests.test_source_lifecycle_apply_has_no_writes_under_unsupported_runtime`
- `test_runtime_admission.RuntimeAdmissionTests.test_bootstrap_and_shared_guard_refuse_before_creating_files`
- `test_runtime_admission.RuntimeAdmissionTests.test_explicit_allowlist_rejects_future_prerelease_and_free_threaded`
- `test_checkout_window_transition.CheckoutWindowTests.test_current_source_declares_checkout_window_with_same_membership`
- `test_checkout_window_transition.CheckoutWindowTests.test_old_and_unknown_source_declarations_are_not_current_candidates`
- `test_checkout_window_transition.DetachVersionTests.test_paired_version_reader_and_independent_auditor_reject_invalid_versions`
- `test_checkout_window_transition.DetachVersionTests.test_older_synthetic_predecessors_refuse_preview_and_apply_before_writes`
- `test_checkout_window_transition.DetachVersionTests.test_legacy_version_is_read_only_for_new_source`
- `test_plain_auditor_boundary.PlainAuditorBoundaryTests.test_missing_or_legacy_authority_is_degraded_without_fallback`
- `test_worktree_checkout_bytes.UnchangedCrlfTests.test_unchanged_crlf_start_submit_accept_keeps_exact_checkout_bytes`
- `test_worktree_checkout_bytes.UnchangedCrlfTests.test_requires_explicit_committed_text_and_crlf`
- `test_worktree_checkout_bytes.UnchangedCrlfTests.test_global_attributes_cannot_supply_missing_committed_policy`
- `test_worktree_checkout_bytes.UnchangedCrlfTests.test_info_attributes_cannot_supply_or_override_retained_policy`
- `test_worktree_checkout_bytes.UnchangedCrlfTests.test_unsupported_committed_attributes_do_not_execute_filter`

### Executed Preparation Checks — 2026-10-09

GFM rendering passed with no literal emphasis delimiters outside code; both local document links resolved. New-file and tracked-diff whitespace checks passed. Disclosure scan found no external private project identity in this note. The original 29 managed files match the fixed source base byte-for-byte; 19 unchanged earlier review inputs also match their recorded hashes. The new note contains 599 locally declared AST test methods across 26 modules and 16 specific seed IDs, not runtime discovery results. No runtime/test/runner source was edited or executed. The fixed packet and note preservation are recorded in the private handoff identity; this statement described the pre-R0 checkpoint; the completed review and unchanged-input checks are recorded below.

## R0 Corrections And Remaining Decisions — 2026-10-09

These are Driver plan corrections after the fixed-input R0, not a second reviewed revision or Owner execution approval. They refine implementation/verification preparation without changing Accepted DR-0004. The fixed original input remains recoverable. Where a proposed test seam or policy is not demonstrated, P0a must supply actual controls and P0b must review them; prose does not discharge proof.

### Controls And Test Execution Map

- Create the source task only after explicit P0a selection/plan approval, before controls authoring or P0c evidence. Keep this note as its linked review input; task owns all later progress. Do not allocate another tracker for runner work.
- P0a produces runner/controller/policy plus a fixed offline acquisition script/command specification. The acquisition phase is separate from the five test modes, with exact Git object/entry allowlist, destination, 300-second cap and readback hashes. It needs no fetch/network. OLD becomes read-only to every test subprocess; it must not be inside EXEC's write allowance. Unknown destination contents stop acquisition.
- P0c starts acquisition before any transition loader that requires OLD, then canaries, collection and base seed smoke. P0b must review all actual commands and exact input channels before execution. Runner result R1/Owner acceptance is retained; no default review waiver or combination is inferred.
- Existing make_exact_suite in test_checkout_window_transition is a historical planning-1 factory, not part of default discovery and not executable evidence for this transition. Preserve its old revision/meaning. Its 20 generated cases are not part of the reported five local AST definitions. Do not silently retarget the factory or count it as covered by default discovery.
- Proposed new entry test module: ordinary current-window tests are discovered normally. Exact-old controls use one explicitly invoked factory with required OLD path, old release reference and source digest supplied by the reviewed controller's fixed input file; never an ambient arbitrary env path. Missing/wrong input is an error, never skip. The controller appends this suite for both complete modes and can select its already-created case objects by their verified IDs for focused/artifact mode. Record default-discovery IDs, factory IDs, final order and duplicate handling separately; no silent deduplication. Review this loader change as a safety oracle.
- Exact checkout-1 release/schema2 detach fixtures come from running the verified OLD on synthetic targets. Older 27/28/planning path lists come from literals and C0 recorded list hashes, not actual old release bytes from this commit. Label them structural/synthetic evidence. Schema1 detach needs an independently reviewed literal fixture; until supplied it is unverified and blocks a claim of covered historical detach compatibility. Do not create historical schema1 by changing only schema numbers on entry-1 output. Reclassify former negative (3,3) pairing tests under the new positive schema3 contract explicitly.
- Every old writer refusal case includes the same executor/request's S0 positive control and path-specific error code plus diagnostic class, followed by exact preservation. Wrong interpreter, topology, permission or malformed-request errors do not count as receipt fencing. Only the contract-permitted empty writer lock may differ; do not exempt staging or other scratch trees wholesale.
- Canary fixed shebang env-python identity, SOURCE/OLD/EXEC and TMPDIR ancestors/symlinks, non-Git target classification and synthetic Git primary classification before trusting refusal tests. Fix Git path/version/digest; inspect child Git config origins without real secrets. Include lock, worktree, durability/fsync and process spawning behavior in base smoke, using actual reviewed test IDs or explicit bounded canaries. Seed additions include the installed CRLF proof class and verified-window/view gate; actual selected IDs and 1,200-second smoke cap are fixed before P0c.

### Prefix And Caller Closure

P0a must define a numbered test-local expected operation sequence directly from DR-0004, independent of production helpers: receipt creation/complete write; each candidate directory/member create/write/sync and release publication; N exclusive open at 0600, partial os.write progress, fsync, fchmod0755, file and parent sync; O verified unlink/root sync; binding staging directory and binding.next exclusive0600/open/write/fsync/parent sync; expected-B0 recheck, os.replace, both directory syncs; allowed empty-staging cleanup. Cross each applicable before/after operation with expected recoverable prefix or preserved non-pass. Compare observed namespace and descriptor operations with that literal sequence; unexplained operations invalidate affected evidence.

Proposed N/binding primitive implementation uses fd-based os.open O_EXCL|O_NOFOLLOW with checked atomic0600, bounded os.write loops, os.fsync and os.fchmod. The reviewed child harness observes operation/path/fd relationships and supplies fault/termination injection without adding a public product command or changing shared jsonio immutable writers. For S1/S2 tears, explicitly labelled synthetic damaged prefixes of lengths 0/1/mid/L-1 exercise refusal; they are not process-kill evidence. Real child termination at selected N/binding boundaries is recorded separately. If hooks cannot observe and terminate at the claimed boundary, report that case unavailable; never infer it from exception injection.

Late-lock controls need a witnessed pre-lock path and waiting-acquisition signal (a reviewed test wrapper/audit mechanism is a proposal, not proven supported instrumentation). Parent holds the common lock while old code reaches the witnessed wait, executes the new prefix under correct lock ownership, releases, and observes old under-lock rejection. No witness means no late-writer evidence. Signal permission is bounded to synthetic child processes; review controller cleanup and process-group absence. Add unsupported-umask rejection before S1, late foreign N collision at S3, and separately simulated operator relocation followed by the same exact recovery. Relocation in synthetic tests is not permission for real project moves.

Add the indirect caller inventory: _worker_required_refs, _worker_content_state, _apply_worker_path and the internal _verify_worker_sources wrapper route. Historical intent bound-reference inspection with launcher_sha=None remains non-live and must not invent runtime identity. Before P1 enumerate every verifier double by window, sha presence and keep/migrate/duplicate disposition. Proposed test-seam rule: non-null launcher SHA requires a supported inventory_id; legacy two-field doubles are allowed only with SHA None and no managed-entry proof. Production default runtime verification always requires a valid inventory_id independently of test seams. This remains a reviewed-plan proposal until P1 scope approval; no callable-identity heuristic or implicit production fallback.

### Unresolved Before Product Editing

| Item | Current disposition and required resolution |
| --- | --- |
| Retired-entry status/doctor/view classification and exit codes | needs-user: prepare exact command/output choices and their consumer effects before first affected code edit; current-bound product must not be called lifecycle-clean |
| Fresh entry-1 init with an existing project hv2 file | needs-user: C0-H-A explicitly covers reappearance/init replay; do not silently extend it. Prepare a narrow interpretation or named amendment for Owner decision before fresh-init implementation |
| Historical detach coverage | Actual OLD schema2 prefix plus independently reviewed schema1 literal fixture required; otherwise compatibility evidence remains incomplete |
| Missing operation matrix cells | Add new-source checkout-1 init/rollback/repair/detach refusals, old-source fresh-entry1 refusals and new source --profile checkout-1 refusal; each has an appropriate positive/control reason |
| P1 double/caller closure and physical oracle | Proposed above; exact enumerated inventory, test loader and observable boundaries must pass P0 review/validation, not be deferred to final R1 |

### Normative And Qualification Completion

P3 mapping explicitly includes Maintaining's opening current profile, Inventory Window Compatibility, Checkout Proof And Detach Versions and Umbrella Candidate Boundary runtime seam. Structural supplement mapping includes Window type; update/rollback plan schema/remove; receipt pair/version; rank/switch chain; permitted binding-tip/pending predecessor plus O/N byte/mode combinations including S3a–S5; repair launcher and detach order. Keep exact eleven-member authority membership and protected decision prefixes.

Include managed .gitignore as a read-only consumer check: inspect current ignore behavior for colvia; do not modify it without demonstrated need within the plan. Measure AGENTS and combined AGENTS+README+GETTING-STARTED reading budgets with existing tiktoken==0.13.0 / o200k_base in an identified isolated environment before candidate freeze. No dependency install is silently authorized; if unavailable, report the measurement gap and propose the bounded tool provision. Rendering, language/claim parity and fresh-reader behavior remain distinct checks.

Use an exact immutable candidate archive outside the implementation checkout for the named qualification/R1 and recovery consumer while Git publication is unapproved. This is recoverable custody, not a commit or a new release artifact. Record source, ordered discovered/executed IDs, runner/policy, runtime/Git, mode results and limitations once in the owning task/anchor. Retain only required fixture/failure material, with a 64 MiB per-failure and 256 MiB per-run proposed cap; exceeding that cap stops for preservation disposition rather than truncating unique evidence silently. Archive preservation is already within the task preservation duty; it does not need an unrelated commit choice. A second qualification candidate or rerun requires a new bounded decision under the stated budget.

## Implementation Plan R0 Record

### Request, Authorization And Identity

The Owner replied “승인” to one fresh no-tool Claude subscription review of the fixed 595,047-byte packet, at most 600 seconds. Packet SHA-256 `d13b17c0e5be828e71bfc58c2f781448c8b341addf4c7081b57f487d2d723686`; reviewed plan SHA-256 `2478b91723822da8436d370c6e79af27020aebfa08373d19dc96a8efbbc908d2`. Source base and tracked diff SHA-256 are `238514686078ce1564010a7b69013f48a635c57c` and `66eff4ce3d773f0bd6bca4d2ea231d981bc50c8ec88a9c9aca638e1fe3dc9993`. Twenty-two full inputs and one explicitly bounded C0 closeout excerpt were supplied; untracked plan/DR and excerpt full/slice identities are preserved in the fixed input manifest. All hashes/base/diff were verified unchanged before and after review.

Authentication verified outside the restricted filesystem context as logged in via claude.ai / firstParty / pro; no API-key environment was present. The restricted-context auth false negative was not treated as account failure. No credential values or account identity were retained. Invocation disabled tools, MCP, slash commands, external settings and session persistence, with safe/restricted mode. Actual model: Claude Opus 5.5 (`claude-opus-5-5`); session `bff9b164-6114-4450-8162-629bfea37705`; elapsed 471.43 seconds, exit 0, no reported error/stderr. This is a fresh static review of supplied context, not executable or complete-source validation. It did not include all test fixtures, DR-0002, all normative members, actual runner controls or candidate implementation. No tests were run.

### Reviewer Response Verbatim

````text
# Colvia C1/C2 구현 계획 R0 검토 보고

**판정 요약**: 계획은 지금 형태로 P1 이후(runtime 편집·실행) 승인 근거가 되지 못합니다. 다음에 승인할 수 있는 범위는 아래 교정을 반영한 "P0a: 통제물 작성(실행 없음)"까지입니다. DR-0004 A안을 다시 열어야 할 새 구체적 모순은 찾지 못했습니다.

**증거 구분**
- **실행 증거**: 없음. 아래는 모두 제공된 바이트의 정적 판독입니다.
- **정적으로 일치 확인한 것**:
  - old-writer fence: `product.py` `_workspace_product_once`의 receipt schema==1 검사, `hv2` `workspace_source`의 release-ref 창 비교, `workspace.py` `_validate_plan_shape`의 창 allowlist가 DR 4-executor 논증과 맞습니다.
  - AST 수치: 제공된 4개 test module의 7/5/1/23이 제 판독과 같습니다.
  - 해시: packet 헤더의 `hv2`·`product.py` 해시 표기가 DR Fixed Baseline과 같습니다(재계산은 못 함).
- **확인 못 한 것**: Static Appendix의 줄 번호, 나머지 22개 test module과 fixture, verifier double 전체, M3 11문서 실제 구성(DR-0002 미제공), C0 baseline appendix의 path-list 해시, Seatbelt 정책의 실효성.

## Blocker — P0 실행 또는 P1 승인 전에 계획 수정 필요

**B1. P0가 서로 다른 승인 네 개를 한 행에 묶었고 내부 모순이 있습니다** (계획 "Scope And Implementation Order" P0, "Execution Boundary Proposal").
- **근거**:
  - 통제물 작성, 실제 바이트 검토, canary·collection 실행, legacy 취득이 한 종료 조건에 들어 있습니다.
  - legacy 취득은 Git 읽기 명령이 필요한데 runner의 5개 mode 어디에도 없고 명령·예산도 없습니다.
  - OLD를 "isolated execution area 안에 재구성"한다는 문장과 "SOURCE/OLD/EXEC 읽기, EXEC만 쓰기"가 충돌합니다. OLD가 EXEC 안이면 oracle 자체가 테스트의 쓰기 범위에 들어갑니다.
  - collection이 "exact controls당 1회"인데, P1~P3에서 테스트가 추가된 뒤 focused ID 고정과 후보 collection이 다시 필요합니다.
  - task ID 할당 시점("On approval")이 P0 증거 생성보다 앞인지 불명확합니다. Contributing "Start And Select"는 진행 기록 소유자를 하나로 요구합니다.
  - runner도 Contributing "Review And Execute"의 R0/R1 기본 대상인데, runner 결과에 대한 R1 또는 Owner의 명시적 결합·면제 기록이 없습니다.
- **교정**:
  - P0a(작성만), P0b(exact-control 검토), P0c(canary, base collection, base smoke 실행), P0d(legacy 취득: 고정 명령, 독립 검증, 실행 후 digest 재확인)로 나눕니다.
  - OLD는 쓰기 경계 밖의 읽기 전용 위치에 둡니다.
  - `collect`는 "(controls, source digest) 쌍당 1회, 총 N회"로 정의합니다.
  - task 기록은 P0c 이전에 만듭니다.

**B2. old-source 테스트의 실행 경로가 정의되지 않았습니다** (계획 "Closed File And Caller Inventory"의 새 test module 행, "Static Appendix").
- **근거**:
  - `tests/test_checkout_window_transition.py`의 `make_exact_suite`는 기본 discovery에 잡히지 않는 factory입니다. 중첩 5개와 `setattr` 15개로 20건이며 `countTestCases() != 20` 가드가 있습니다. 계획의 AST 수치 "5"에는 이 20건이 없습니다.
  - 이 factory는 `planning-1` P와 `--profile planning-1`을 고정하므로, checkout-1/entry-1만 전환하는 새 source에서는 Q로 실행할 수 없습니다.
  - old inventory를 새 `hv2ref.product.SERIAL_MANAGED_PATHS`를 import해 계산합니다. 계획이 스스로 금지한 "new membership substitution"에 해당합니다.
  - 새 `test_entry_window_transition.py`가 기본 discovery 대상인지 factory인지, OLD 경로와 해시를 어떤 채널로 받는지 없습니다. 환경변수 allowlist에도 없습니다.
  - factory라면 complete 실행에 4-executor 행렬이 빠지고, "selected-ID file"로 이름 로드도 안 됩니다.
- **교정**:
  - 필수 테스트 그룹마다 실행 mode, OLD 입력 채널, "부재 시 skip 아닌 error"를 표로 고정합니다.
  - 기존 20건 factory는 "역사적 증거로 보존, 재실행 불가" 또는 "checkout-1→entry-1로 재작성" 중 하나로 명시 처분합니다.
  - old path 목록은 test-local literal로 두고 C0 appendix의 path-list 해시와 대조합니다.

**B3. 거부 테스트가 엉뚱한 이유로 통과할 수 있습니다** (계획 "Required Tests" Four executors/Admission).
- **근거**:
  - 기존 `refused()`는 `returncode != 0`과 바이트 보존만 단언합니다.
  - `hv2` shebang은 `/usr/bin/env -S python3`라 PATH의 python3가 3.14.7이 아니면 `HV2-WORKSPACE-RUNTIME`으로 거부됩니다.
  - `workspace.py` `_classify_target`은 조상 디렉터리에 `.git`이 있으면 `nested-repository`로 mutation을 거부하고, `.hrn`이 있으면 거부합니다. EXEC를 "agent-worktree root 아래"에 두면 모든 target이 이 경로로 거부될 수 있습니다.
  - 위 두 경우 모두 "S1 이후 old writer 거부"가 receipt fence와 무관하게 통과합니다.
- **교정**:
  - 각 (executor, 요청)마다 S0 양성 대조와, 명령 경로별 거부 원인 단언(코드와 메시지 부류)을 필수로 합니다. DR "Source By Target By Operation"의 경로별 코드 구분을 따릅니다.
  - test import 전 canary에 다음을 추가합니다: EXEC/TMPDIR 조상에 `.git`/`.hrn`과 symlink 없음, 새 temp dir이 `non-git`으로 분류되고 `git init` dir이 `primary`로 분류됨, `env python3`의 실체가 고정 인터프리터임.
  - 거부 시 허용되는 scratch 차이는 빈 `.hrn/locks/writer.lock`만으로 한정하고, `staging/`은 면제하지 않습니다.

**B4. late-lock writer와 물리 prefix의 독립 oracle이 없습니다** (계획 "Required Tests" Physical prefixes와 그 아래 문단).
- **근거**:
  - late-lock: "old 구현을 수정하지 않고 동기화 경계에서 정지"의 증인이 없습니다. old writer가 S0에서 pre-lock 검사를 통과하고 `flock`에서 대기 중이었다는 증거가 없으면, S1 이후에 새로 시작한 writer와 구별되지 않습니다.
  - prefix: DR이 요구한 "각 syscall/byte/mode/directory prefix 열거"의 번호 매긴 목록이 없습니다.
  - 구현자가 놓은 seam은 "열거 밖의 mutation이 없음"을 증명하지 못합니다.
  - 새 구현의 child를 production hook 없이 물리 경계에서 죽이는 방법이 없습니다. 기존 `inject_at`과 `cli.py`의 숨은 `--inject-at`에 새 지점을 추가할지도 미정입니다.
  - S1 receipt와 S2 staging tear를 `jsonio.py` 변경 없이 어떻게 만드는지 없습니다.
- **교정**:
  - late-lock: wrapper에서 `fcntl.flock` audit event 같은 비침습 신호로 "S0 통과, lock 대기"를 건별 기록합니다. 증인이 없는 건은 증거로 세지 않습니다.
  - prefix: DR 표에서 직접 옮긴 test-local 기대 연산 순서(literal)를 두고, 관측한 namespace 연산(create/chmod/unlink/replace/mkdir)과 대조합니다.
  - partial write: N과 `binding.next`를 fd 기반 primitive(`os.open` O_EXCL|O_NOFOLLOW 0600, `os.write`, `os.fsync`, `os.fchmod`)로 구현한다는 제약을 계획에 명시하고, child wrapper에서 k바이트 뒤 SIGKILL합니다.
  - S1/S2 tear는 "합성한 정지 상태"(길이 0, 1, 중간, L-1)로 만들고, process-kill 증거와 다른 라벨을 붙입니다.
  - 누락 케이스 추가: 지원하지 않는 umask의 S1 전 거부, S3 시점 외부 N 충돌 후 차단, 운영자 이동 후 동일 recovery 재시도.

**B5. 새 runner의 실행 의미를 runtime 편집 전에 검증하지 않습니다** (계획 "Execution Boundary Proposal", Maintaining "Validation Frequency").
- **근거**:
  - P0는 canary와 collection뿐입니다. shebang exec, git worktree, flock, F_FULLFSYNC, `/dev/fd` 비용은 collection으로 드러나지 않습니다.
  - 수정된 후보에서 처음 실행하면 runner 원인과 후보 원인이 섞입니다. 기존 runner 출력은 anchor가 아니므로 대조군도 없습니다.
  - 고정 대상이 CPython뿐이고 Git 실행 파일의 경로·버전·digest가 없습니다. macOS `/usr/bin/git` shim은 캐시 접근을 합니다.
  - `workspace.py` `git_environment()`가 `GIT_*` 환경변수를 모두 제거합니다. runner가 설정한 `GIT_CONFIG_NOSYSTEM` 등은 제품의 child git에 전달되지 않고, system gitconfig는 계속 읽힙니다.
- **교정**:
  - P0c에 base 상태의 seed 16개 실행(시간 상한 포함)을 넣습니다.
  - Git 실체를 고정하고, `check-attr --source`와 `git config --show-origin --list` canary를 둡니다.
  - Git 격리는 환경변수가 아니라 HOME/XDG 격리와 정책으로 한다고 명시합니다. `XDG_CONFIG_HOME`도 allowlist에서 정합니다(`work.py` `_policy`가 읽음).

**B6. verifier double 규칙이 닫히지 않았습니다** (P1 진입 전; 계획 Inventory의 `work.py` 행, DR "Contract Closure").
- **근거**:
  - `WorkStore._runtime`은 주입된 callable이 production인지 double인지 구별할 수 없습니다.
  - launcher 경로를 `inventory_id`에서 유도하면, `launcher_sha256`이 non-None이고 `inventory_id`가 없는 결과의 의미가 정의되지 않습니다.
  - `test_worktree_checkout_bytes.py`의 `inventory_id: "checkout-1"` double은 고치지 않아도 계속 통과하면서 entry-1 mapping을 전혀 검증하지 않을 수 있습니다.
- **교정**:
  - 규칙을 "`launcher_sha256`이 non-None이면 유효한 `inventory_id` 필수, 2-field는 None일 때만 허용"으로 고정합니다.
  - 모든 double을 (창, sha 유무, 유지/이관/복제 사유)로 열거하는 것을 P1 진입 조건에 넣습니다.

## P1/P2/P3 진입 전 닫을 항목 (P0a는 막지 않음)

| # | 항목 | 근거 | 교정 |
| --- | --- | --- | --- |
| G1 | retired-entry 진단 결정 시점이 "before P1/P3"로 모호합니다. | `cli.py` `main`의 exit mapping. `pass`(0)에 필드를 더할지 비-pass로 할지에 따라 `view.py` `_observe` 동작이 달라집니다. | 해당 코드를 처음 쓰기 전에 Owner 결정(needs-user)으로 닫습니다. |
| G2 | fresh entry-1 init 대상에 기존 사용자 파일 `hv2`가 있는 경우가 정의되지 않았습니다. | DR C0-H-A는 "reappearing"과 init replay만 말합니다. | 해석을 확정하고 테스트를 추가합니다. |
| G3 | legacy detach oracle이 없습니다. | seed의 `test_legacy_version_is_read_only_for_new_source`는 현재 생성물의 version 숫자만 바꿉니다. schema 3은 remove set이 `colvia`라 이 합성이 성립하지 않습니다. 취득하는 OLD는 schema 2만 씁니다. | schema 2 prefix는 실제 OLD로 생성합니다. schema 1은 literal fixture로 하거나 "미검증"으로 명시합니다. `(3,3)` 음성 케이스 변경도 단언 변경으로 처분합니다. |
| G4 | 27/28 창과 planning-1의 실제 release 바이트는 고정 commit에서 나오지 않습니다. | "Literal history" 행 | path-list literal과 기록된 해시 대조라는 점, 합성분이라는 라벨을 명시합니다. |
| G5 | DR 행렬 중 이름 붙은 테스트가 없는 행이 있습니다. | DR "Source By Target By Operation" | 다음을 추가합니다: 새 source의 정상 checkout-1 대상 rollback/repair/detach/init 거부, old executor의 fresh entry-1 대상 거부, `--profile checkout-1` 거부. |
| G6 | 규범 매핑이 빠져 있습니다. | Maintaining, CHECKOUT-1-STRUCTURE | 아래 두 목록을 P3 표의 최소 항목으로 넣습니다. |
| G7 | `AGENTS.md`/`README.md`/`GETTING-STARTED.md`를 바꾸는데 reading budget 측정이 계획에 없습니다. | Maintaining "Reading Budget And Claims" (`tiktoken==0.13.0`) | 측정 도구와 실행 환경을 포함해 P3/P4 검사에 넣습니다. |
| G8 | focused 예산이 P1/P2/P3의 종료 조건과 맞지 않습니다. | "at most two runs"가 전역이면 세 단계에 부족하고, set별이면 set 수가 무한입니다. complete도 후보 수 상한이 없습니다. | 단계별 set 수와 횟수, 최대 후보 수를 명시합니다. |
| G9 | P4 "Freeze candidate"의 수단이 없습니다. | commit 권한이 없는 상태에서 Maintaining은 anchor의 복구 가능한 고정을 요구합니다. | 로컬 commit 승인 또는 불변 보존 archive 중 하나를 Owner가 선택합니다. |

G6의 Maintaining 누락 절:
- 첫 문장의 "checkout-1 profile"
- "Inventory Window Compatibility"
- "Checkout Proof And Detach Versions" (CRLF 창, detach schema 2→3)
- "Umbrella Candidate Boundary"의 seam 문장

G6의 CHECKOUT-1-STRUCTURE 누락 절:
- `Window` 타입
- Plans 표의 update/rollback 행(schema 2, `remove`)
- receipt version 문장
- rank/switch 문장
- "binding은 tip 또는 단일 pending predecessor, launcher는 permitted bytes" 문장 (S3a~S5의 O/N 공존을 담아야 함)
- repair launcher와 detach 순서

## 선택 개선

- **artifact mode**: 별도 scenario runner는 구현 뒤에야 바이트가 생겨 통제물 검토가 한 번 더 필요합니다. 같은 test module의 고정 ID 실행으로 합치면 승인 부담과 oracle 이원화가 줄어듭니다.
- **실패 fixture 보존**: 3.11+ unittest는 실패 직후, cleanup 전에 `addFailure`/`addError`를 호출합니다. 테스트를 patch하지 않고 TestResult에서 보존할 수 있으니 방식과 크기 상한을 적으면 됩니다.
- **seed 보강**: `test_verified_window_gate_and_view_share_the_same_proof`와 `InstalledUnchangedCrlfTests`는 CRLF 창 gate와 실제 verifier 경로를 직접 단언합니다.
- **Appendix 보강**:
  - inventory_id 전달자 `_worker_required_refs`, `_worker_content_state`, `_apply_worker_path`를 넣습니다.
  - wrapper 안의 `_verify_worker_sources` 호출을 넣습니다.
  - `intent.py:258`은 runtime이 없는 호출이므로 "None 유지"인지 명시합니다.
- **Seatbelt 정책 검토 항목**: same-sandbox `signal` 허용(SIGKILL 테스트와 그룹 정리에 필요), `/dev/fd` read-data 채택 여부를 spawn 비용 canary로 결정.
- **소비자 확인**: managed 루트 `.gitignore`가 소비자 목록에 없습니다(내용 미제공).

## 다음에 승인 가능한 범위

1. **지금**: B1~B5와 G8을 반영한 계획 note 개정(문서만). 이어서 P0a, 즉 runner/controller/정책/legacy 취득 절차의 작성만 승인할 수 있습니다. 위치는 `tests/` discovery와 managed 29 경로 밖이며, 실행·runtime/test 편집·Git 행위는 포함하지 않습니다.
2. **그다음 별도 승인**: 실제 통제물 바이트 검토(P0b), 이어서 canary·base collection·base seed 실행·legacy 취득(P0c/d).
3. **P1 이후**: P0c/d 통과, B6, G1~G5가 닫힌 뒤에만 가능합니다. B2~B4가 미정인 상태에서는 "old-writer fence와 prefix 복구가 A안과 일치"라는 P2 종료 조건을 판정할 oracle이 없으므로 runtime 편집 승인을 권하지 않습니다.

이 보고는 reviewer 소견이며 계약 수락, 활성화, 실행 권한 부여가 아닙니다.
````

### Driver Dispositions

| Finding | Disposition | Source-grounded response / plan action |
| --- | --- | --- |
| B1 | revise | Split authoring, actual-control review and execution/result gates; one task from P0a approval. OLD outside writable EXEC, separate offline acquisition before dependent loading, finite per-controls/source collection. P0c orders acquisition first to avoid a missing-OLD loader cycle; retain runner R1/Owner acceptance |
| B2 | accept | Confirmed planning-1 profile, imported current membership and explicit 20-case factory guard. Preserve historical factory meaning; proposed new explicit factory joins both complete modes with fixed inputs and missing-input errors |
| B3 | revise | Confirmed shebang/runtime and topology can cause unrelated refusal. The approved root is not itself proof of bad topology; require actual ancestor/classification and S0 controls rather than asserting every root child is nested. Assert specific refusal causes and exact preservation |
| B4 | revise | Add literal operation oracle, fd primitive constraint, separate synthetic tears/process kills and witnessed late-lock controls. Audit/wrapper feasibility remains P0 actual-control evidence, not established by accepting a reviewer suggestion |
| B5 | accept | Confirmed git_environment strips GIT_* variables. Add real Git identity, HOME/XDG/policy checks and unchanged-base smoke before candidate edits; no inherited runner pass |
| B6 | revise | Non-null SHA needs verified supported window in test seams; production verifier always needs inventory_id. Explicit double/caller list before P1; no implementation or contract waiver now |
| G1 | needs-user | Exact retired-entry diagnostic/exit choice must be proposed and resolved before affected code edits |
| G2 | needs-user | Fresh-init pre-existing hv2 is not silently covered by reappearance wording; prepare narrow Owner interpretation/amendment |
| G3–G5 | accept | Distinguish actual OLD schema2 from synthetic historical schemas/path lists; add missing operation/profile refusal cells and explicit assertion-version disposition |
| G6–G7 | accept | Added named normative clauses, reading-budget measurement and isolated tool availability gate; no blind eleven-document membership assumption |
| G8 | accept | Finite collection pairs, three focused phase sets plus one shared rerun, one qualification candidate and explicit phase totals; no unbounded set/candidate multiplier |
| G9 | revise | Recoverable immutable archive for named qualification/R1 consumer fulfills preservation without inventing commit approval; actual source commit remains separately authorized |
| Optional controls and consumers | revise | Use one reviewed test loader/ID surface for artifact checks, bounded failure fixture preservation, stronger installed seed, indirect callers and .gitignore observation. Signal/dev-fd permissions require exact policy review and canaries |

### Owner Decision And Next Bounded Scope

The Owner authorized and received this one R0, not P0a execution, product implementation or result acceptance. The review allowance is consumed. The Driver corrected planning text only; these final bytes have not been re-reviewed. No new contradiction requiring DR-0004 A-policy reopening was demonstrated. P1+ is not ready for approval while the identified controls and Owner choices remain open.

Next proposal is P0a authoring only: approve one source-owned task and author the exact runner/controller/policy, offline legacy acquisition specification, enumerated input/test-loader and prefix oracle, and two narrow Owner-choice proposals above. Keep these controls outside managed paths and test discovery; no runtime/test source edit, acquisition, canary, test, reviewer invocation, Git publication or adopter mutation occurs under that authoring approval. Completion means actual inspectable control bytes and fixed commands/budgets plus input/decision tables, ready for separately authorized P0b. Retain the current worktree for that specific near-term use. Required input/result copies remain outside it; no checkout retirement is eligible yet.

### Post-Review Document Checks

After Driver corrections, GFM rendering passed with no literal emphasis outside code; local links, disclosure and whitespace checks passed. The Reviewer response matches the collected final text verbatim. Twenty-one other full packet inputs and the full C0 excerpt source are unchanged; all 29 managed files still match the fixed base. The tracked diff identity is unchanged. These are document/input checks, not a reviewer recheck, runner validation or runtime test. The corrected note and fixed review input are preserved outside the implementation checkout for the P0a/P0b handoff consumer until referenced and retained in the approved task or equivalent custody. Raw API envelope/stderr and duplicate response files are not permanent deliverables once the verbatim record and recoverable copy are verified.
