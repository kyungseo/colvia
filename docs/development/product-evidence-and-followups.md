# Product evidence and retained follow-ups

Find the checks behind the current SQLite candidate and the earlier trial findings that still inform it. The [record foundation task](FEAT-20261106-002-record-foundation.md) owns the design and tracks the remaining work. Each result below applies to the named inputs and environment.

## Record-foundation verification

| Evidence | What was checked | Result and limits |
| --- | --- | --- |
| Cumulative source checks | [Fixed-input integration run](record-foundation/p9-source-checkpoint.md#cumulative-source-verification-after-integration), from the development worktree at the time | 822 tests passed across 104 modules. Later focused tests have separate results. The selected run excluded the native sandbox worker and process-group diagnostics. |
| Storage interruption and preserved results | In that source run, [killed writer recovery](../../tests/test_foundation_store_faults.py) and [Work acceptance and historical body retention](../../tests/test_foundation_work.py) | The killed writer left a recovery-required journal. The Work tests accepted a specific submitted result and verified historical content after rework, archiving and current-file removal. These are source tests with synthetic projects. |
| macOS ARM64 installation | [Isolated offline update](FEAT-20261111-001-guided-onboarding.md#installed-verification-result) from sequence 8 to 9 | The accepted guide was selected, and the earlier slot and prior project records were preserved. This check used offline transport. |
| macOS ARM64 agent behavior | The same [sequence 9 installation](FEAT-20261111-001-guided-onboarding.md#installed-verification-result) with Codex CLI | A new conversation used the installed guide to turn a purpose into a first plan, then recorded the person's exact approval. The trial stopped before starting the Work or writing project deliverables. |
| Windows ARM64 installation and restore | [Sequence 12 on a Windows ARM64 guest](FEAT-20261106-002-record-foundation.md#windows-origin-restored-project-rebind-qualification), using a standard-user console and a Windows-origin backup | Restore preserved the records. A conflicting rebind was refused after interruption, and a separate folder was rebound successfully. Cross-platform rebind remains outside this result. |
| Windows x64 packaging | Unsigned offline sequences 1 and 2, using the same native launcher and runtime bytes | The sequence 2 inventory matched all 472 payload entries. Native x64 installation, execution and recovery remain unverified. |
| Distribution | [Public installation and update criteria](record-foundation/runtime-and-extension.md#첫-공개-설치-진입과-완료-기준) | The actual HTTPS distribution address, installation command and end-to-end public path remain to be verified. |

The 822-test run pinned 528 inputs. The before and after input lists matched SHA-256 `36c3fbc96dc48994364fd6e53fda7568a565550d96423fc9d9c8ddc2faf27ede`.

Candidate manifest SHA-256 values identify the exact packages used for the scoped evidence above.

- macOS ARM64 sequence 9 · `dfd74b0b3ee94098fef22a9460390b784bb1122ea80e486ff8e88fb11e61f09e`
- Windows ARM64 sequence 12 · `22ce66034e75008b1a2d3a4c5b902d3925a9d61975d2c447d38aaace23f26181`
- Windows x64 sequence 1 · `8237994d92cb1e04f9fd4fa47d22ec996365d05e82e7ad85c2e457f2028d1eb1`
- Windows x64 sequence 2 · `4256b76795f3f5556c5b41305169b85f41f88d66abaa62452c766838ac4fd918`

## Reading the implementation and its evidence

Code explains what executes. Contracts explain what must remain true; verification records explain what was actually exercised. Read all three before concluding that a capability is supported.

| Question | Product-owned reading | Evidence boundary |
| --- | --- | --- |
| What does acceptance mean? | [General Work](../GENERAL-WORK.md), [approved work through review](FEAT-20261104-001-approved-work-review.md) | Scope approval, submission and accepting a particular result are separate. Historical checks do not qualify the proposed new store. |
| What is changing in storage and preservation? | [Design](record-foundation/design.md), [structure](record-foundation/structure.md), [review disposition](record-foundation/review-disposition.md) | Draft design and unresolved decisions; do not treat planned body preservation or backup as installed behavior. |
| Why change the foundation? | [Measurements](record-foundation/measurements.md), [diagnostics](record-foundation/diagnostics.md), [large Work checks](PATCH-20261104-005-large-ordinary-work.md) | Measured old-path cost, reproduced failures and an isolated prototype are distinct from new-format performance. |
| Which invariants must survive? | [Validation matrix](record-foundation/validation.md), [concurrency boundaries](record-foundation/concurrency.md) | A validation plan is not a passing run. Actual concurrent execution remains outside the selected implementation scope. |
| What did usability work establish? | [Trial usability](FEAT-20261106-001-trial-usability.md), desktop supplement below | Offline checks, interrupted scripted behavior checks and separately observed desktop use retain their own outcomes. |
| What does the protection layer cover? | [Local payload gates](PATCH-20261101-002-local-payload-gates.md), privacy supplement below | Bounded payload checks are not whole-desktop protection or proof that all model input is sanitized. |
| What must installation and support establish? | [Runtime and extension contract](record-foundation/runtime-and-extension.md), [release journey](preview-release-order-and-user-journey.md) | Target combinations and source tests are not actual installed-platform qualification. |
| What remains a later candidate? | [Development candidate index](README.md), [document placement](document-ownership.md) | Historical intake rows retain their dates; use the current owning task for decisions and status. Internal research is not an undisclosed product prerequisite. |

Detailed run logs, machine/account setup, raw reviewer correspondence, comparison provenance and recovery artifacts remain in private maintainer records where their evidence or recovery purpose requires them. Their absence from the public tree must not hide a product limitation, safety invariant or decision rationale. Public claims need a self-contained result summary identifying the tested source/candidate, method, outcome and limits, plus reusable synthetic checks where applicable. Do not disclose private identifiers merely to make a claim look more rigorous. Required dependency and license attribution remains intact.

## Desktop failure and entry supplement

These inputs come from a bounded source-launcher desktop trial. The observer reported successful cross-agent resume and acceptance in the primary folder, and a later failure involving an app-created nested worktree. They are inherited observations, not newly rerun tests and not managed-install qualification. The existing foundation design already includes nested worktree topology and ignore-policy drift; the following details need explicit coverage when implementing that design.

| Input | Required behavior to preserve or clarify | Focused check to carry forward |
| --- | --- | --- |
| Failure explanations (D2) | Show the actual failed boundary and a short next action. Do not replace a topology or permission refusal with generic usage text. | An unsupported topology and an inaccessible store produce distinct actionable explanations without private paths in general summaries. Detailed local diagnostics may identify the relevant user-selected folder. |
| Actual folder selection (D3) | Establish which folder the host opened and whether it is connected. A repeated project name does not establish folder identity. | A newly created empty folder and an existing connected folder with the same name are not confused. Installation guidance must explain how to open the intended existing folder. |
| Commit reminders (D4) | Keep accepting a result separate from committing it. Reuse an agreed Git workflow instead of repeating internal paths and commit prompts after every action. | Cross-agent resume retains the distinction and does not treat earlier acceptance as Git authorization. |
| Refused verification and lock interpretation (D5) | After verified state lookup fails, do not promote raw record inspection into a verified current state. A lock file's presence alone is not evidence of a live writer. | Preserve unavailable/partial state. Verify writer liveness through the selected locking contract, and label explicitly authorized raw diagnostics as non-authoritative. |
| Owned temporary preparation (D6, earlier I-8) | Account for abandoned preparation directories without deleting authoritative data or recovery evidence. | Cleanup considers ownership, active use and retained recovery needs; interruption or an empty directory alone does not authorize removal. |

The trial's successful ordinary flow does not overturn the earlier scripted-run failures: the host, launcher and execution boundary differed. It also does not prove that managed runtime access, notification permissions or nested-worktree writes work. Those remain in the installation and app qualification matrix. No app-owned worktree or ignore setting is automatically removed by this intake.

## Privacy experiments: decision rationale and later candidate

The [existing privacy direction](preview-release-order-and-user-journey.md) separates ordinary work from an explicitly selected protected-copy path. It includes personal identifiers and customer information. It does not make every Work go through sanitization. Product adoption and real customer data use remain deferred.

Retain these findings when selecting that later work:

- In fixed synthetic Korean records, normalization and known-name/particle boundary rules improved exact handling of registered names. An additional local detector found missing-name candidates but also needed boundary correction and false-positive removal. Detection coverage is not exact replacement quality or stable customer identity. An optional candidate suggester is a plausible experiment; automatic replacement is not justified by those observations.
- Human review timings did not establish time to a correct final copy. Different documents, one participant and unresolved copy differences prevent a productivity claim. A later review screen should expose unresolved candidates and permit returning to them; synthetic scoring should distinguish remaining originals, mixed identities and unintended edits.
- In a bounded execution probe, specified original/mapping reads were refused and a changed approved copy invalidated execution. However, names deliberately left in the copy or request still reached the local execution input. Path blocking is not comprehensive sanitization.
- A separate local pre-transmission experiment rejected the official CLI's assembled request under a narrow approved-copy contract. Constructed positive controls passed, but the real CLI did not complete a normal flow under that contract. This establishes neither successful official protected execution nor coverage of all provider requests. Normal behavior and unexpected-input refusal must both pass before adoption.
- An evidence-jump summary screen did not establish a review benefit: the participant used the full-copy view and never used the jump button. Shorter observed times did not establish improved accuracy. Keep summary/evidence navigation optional and reconsider it when a real review problem warrants another bounded test.

Any later protected-copy proposal must bind the human-reviewed copy and request to the actual permitted input, separately cover other context/tool input, and distinguish ordinary chat attachments from the controlled route. The existing source protection contract remains the authority; these experiments do not add a new advertised protection guarantee. Exact comparison-engine identities, checkpoints and raw examples remain private research provenance, not required product input.

## Historical material that stays internal

Do not import entire audit archives, desktop transcripts, VM commands, reviewer packets or cross-product planning dossiers. Preserve the originals with their existing consumers and retention conditions. Product-level requirements already owned by the development index, lifecycle documents and foundation specifications are reused rather than copied here. Earlier proposals to rely only on user Git commits for historical content, or to auto-migrate private trial installations, do not override the current preservation design and Owner scope.

The private reconciliation map records which historical sources were inspected and which were unavailable. This page contains only the technical conclusions needed to maintain Colvia; it is not an exhaustive audit of every historical artifact and does not claim that all old links or prose have been repaired.
