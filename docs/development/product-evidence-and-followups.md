# Product evidence and retained follow-ups

Find the checks behind the current SQLite candidate and the earlier trial findings that still inform it. The [record foundation task](FEAT-20261106-002-record-foundation.md) owns the design and tracks the remaining work. Each result below applies to the named inputs and environment.

## Record-foundation verification

| Evidence | What was checked | Result and limits |
| --- | --- | --- |
| Historical cumulative source checks | [Fixed-input integration run](record-foundation/p9-source-checkpoint.md#cumulative-source-verification-after-integration), earlier development inputs | 822 tests passed across 104 modules. The run excluded the native sandbox worker and process-group diagnostics. Later focused runs overlap and are reported separately. |
| Clean source clone | `448b581`, macOS ARM64, CPython 3.14.7, SQLite 3.54.0; [representative Work test](../../CONTRIBUTING.md#make-your-first-change) | One test passed in a clean local clone: scope approval, submission for review, and acceptance of a specific result. |
| Storage interruption and preserved results | Earlier fixed-input run; current examples: [killed writer recovery](../../tests/test_foundation_store_faults.py) and [Work acceptance and historical body retention](../../tests/test_foundation_work.py) | A killed writer left a recovery-required journal. Work tests checked retained content after rework, archiving and current-file removal. These are source tests with synthetic projects. |
| macOS ARM64 offline update | [Sequence 8 → 9](FEAT-20261111-001-guided-onboarding.md#installed-verification-result) | Selected the accepted guide and kept the previous slot and existing project records. |
| macOS ARM64 agent behavior | The same [sequence 9 installation](FEAT-20261111-001-guided-onboarding.md#installed-verification-result) with Codex CLI | In a new chat, the installed guide helped turn a purpose into a first plan and record the person's exact approval. The trial stopped before starting the Work or writing deliverables. |
| ARM64 offline updates | macOS 9 → 10 and Windows 12 → 13; sequences 10 and 13 use `448b581` source without the later private HTTPS overlay | The installations selected the new guides and retained project records, backup receipts and the previous recovery slots. Slot inspection did not perform a rollback. |
| Windows ARM64 restore and rebind | [Sequence 12 on a Windows ARM64 guest](FEAT-20261106-002-record-foundation.md#windows-origin-restored-project-rebind-qualification), using a Windows-origin backup | Restore preserved the records. A conflicting rebind was refused after interruption; a separate folder was rebound. Cross-platform rebind was outside the trial. |
| Windows x64 offline packaging | Historical unsigned sequences 1 and 2, using the same native launcher and runtime bytes | Sequence 2 matched all 472 payload entries. This packaging check did not install or run either sequence. |
| Windows x64 Git registration and connection | Offline sequence 5 on one real device; Git for Windows `2.56.1.windows.1` at its standard per-user installation path | The manager registered the executable and connected a synthetic repository. Connection preserved existing files, Git metadata, HEAD and staging. |
| Windows x64 private HTTPS | Frozen trial sequences 6 and 7, one real device, standard user, ordinary Windows PowerShell 5.1 | First install, installed launcher readiness and HTTPS update 6 → 7 passed. Records and settings remained intact, and sequence 6 was retained as the recovery slot. The public endpoint, first public trust and other host/permission combinations were outside this check. |
| Windows ARM64 private HTTPS | Frozen trial sequence 14, test VM, standard user, ordinary Windows PowerShell 5.1 | First installation and launcher readiness passed. An earlier attempt stopped in the trial wrapper while handling an OpenSSL warning. The corrected wrapper retained the warning and verified exit code 0 and the installed launcher. |
| macOS ARM64 private HTTPS | Frozen trial sequence 11, test VM, standard user | First installation and installed launcher readiness passed. |
| Windows x64 launcher recovery and basic project entry | Offline recovery to sequence 8 after an interrupted update; then sequence 10 on the same device | The project batch launcher resolved the installed runtime in ordinary PowerShell and the Codex app. This checks the tested standard layout. |
| Windows x64 Git integration and recovery | Offline sequence 14 → 15, one device, synthetic repositories and a forced interruption | Normal integration and recovery of the recorded Git lock path were verified. Unrecorded external locks are preserved for diagnosis. |
| Windows ARM64 change boundaries | Offline sequence 18 → 20 on a Windows 11 ARM64 VM; recovery slot 18 | Verified native installed Git interruption recovery and preserved 41 existing records byte-for-byte. The prior slot was inspected in this update; this run did not qualify a rollback involving moved records. |
| Project move and compatibility | Accepted Stage 2 integrated source on macOS ARM64 local APFS; synthetic plain and single Git folders and a previous trial payload reader | Same-volume moves retained Work and approvals. At the checked boundary the prior reader refused records and backup data requiring the newer connection capability. A prior writer opened before the move was refused at its next write. The following rows describe the separate Windows observations. |
| Windows ARM64 project move | Official v0.1.0 on Windows 11 ARM64, native PowerShell 5.1, one ordinary folder on local NTFS | Manager preview and approval updated the connection after a same-volume move. The old location was refused and the existing Work under review and its submission were readable from the moved location. The prior native launcher could also read it. Windows Git checkouts and an agent-led move were outside this check. |
| Windows x64 project move | Isolated signed 0.1.0 test build on a physical x64 device, PowerShell 5.1, one ordinary folder on local NTFS | The manager reconnected the folder after a same-volume move. The required check read the existing Work under review and verified its submission bytes after the move. The movement check used the isolated build delivered over local HTTPS. |
| Host permissions and public delivery | [Host and platform verification criteria](record-foundation/validation.md#codexclaude-권한-모드별-접근승인-경로), [public installation and update criteria](record-foundation/runtime-and-extension.md#첫-공개-설치-진입과-완료-기준) | Earlier scoped host results are listed below. The official Pages command installed Colvia and updated `v0.1.0-preview.1` to `v0.1.0` on macOS ARM64, Windows x64 and Windows ARM64. Direct agent execution stays disabled in the first Preview. |

### Windows x64 host observations

| Host and candidate | Observed permission and behavior | Verification boundary |
| --- | --- | --- |
| Official Codex CLI 0.167.1, sequence 10 | Explicit MXC with user approval, the project plus one added record folder for writing. Created and submitted one Work; a new read-only session recovered approval, submission, current and retained contents, and pending acceptance. | Existing settings and checked NTFS permissions were preserved. The saved elevated route remains a separate path. |
| Codex app, sequence 11 | A temporary project profile used user approval with one added writable record folder. An approved one-file Work reached review. After restoring the settings, the additional permission was absent in a new session. | The approval menu alone did not supply this path. A later Plan-mode response had no tool calls; the user confirmed return to execution mode. Other host profiles and previously open sessions are outside this proof. |
| Claude Code desktop, sequence 11 | Manual approval per command, Code engine 2.1.325. Approved one-file Work reached review with current and submitted bytes matching. | The app shell build was not established. Manual command approval is the observed path. |
| Claude Code CLI 2.1.325, sequence 11 | Resumed an earlier approved Work in Manual mode, finished its writing and checks, submitted, compared bodies and confirmed the CLI exit. | Existing read and cross-session results come from earlier runs. Plan-mode read-only behavior and a refused Write action were observed. A separate later run confirmed an explicit PowerShell approval refusal, with files and records unchanged. |
| Windows notification receiver, sequence 12 | A Claude Work notification was sent and clicked, opening the exact Work detail from a cold start. A previously sent Codex event was separately resolved by the detail command. A later sequence 12 trial verified both clicks and the switch from Codex to Claude Work detail in the same window. | Receiver re-registration was reverted. Unknown delivery stays recorded without resending. The first Preview reuses this x64 click evidence and checks the changed Windows detail command on the official ARM64 package. |

The ordinary PowerShell and packaged-app installation path difference was observed during the x64 trial. Ordinary PowerShell on the standard account installed the managed runtime at the expected location. The current bootstrap checks path and available space before preparing installation. The currently combined bootstrap also passed its Windows ARM64 PowerShell 5.1 no-install branch checks. Both Windows architectures passed manager selection and the version-changing update with the same official install command.

The 822-test run pinned 528 inputs. The before and after input lists matched SHA-256 `36c3fbc96dc48994364fd6e53fda7568a565550d96423fc9d9c8ddc2faf27ede`.

The four private HTTPS packages were tested with trial trust. They include 11 packaged Python files whose bytes differ from the bare `448b581` checkout. The clean-clone test covers that checkout; the installed results cover the packages below. Their manifests still identify the guides shipped during the trials, including earlier installation and agent-entry wording. For the corrected wording, see the current [English](../../manual/en/foundation-preview.md) and [Korean](../../manual/ko/foundation-preview.md) source guides.

Selected manifest SHA-256 values identify the packages used for the scoped evidence above.

- macOS ARM64 sequence 9 · `dfd74b0b3ee94098fef22a9460390b784bb1122ea80e486ff8e88fb11e61f09e`
- macOS ARM64 sequence 10 · `24fa1035eced9dc433cd95a31b905c5ab7307a2974b82a41c2663cf58f5498a5`
- Windows ARM64 sequence 12 · `22ce66034e75008b1a2d3a4c5b902d3925a9d61975d2c447d38aaace23f26181`
- Windows ARM64 sequence 13 · `da6aa28cf069031cd49ad71a8fe18cec8345788049b0d2453a4e45bffbe70521`
- Windows x64 sequence 1 · `8237994d92cb1e04f9fd4fa47d22ec996365d05e82e7ad85c2e457f2028d1eb1`
- Windows x64 sequence 2 · `4256b76795f3f5556c5b41305169b85f41f88d66abaa62452c766838ac4fd918`
- Windows x64 sequence 5 · `f0ceb43d5d63dfac9e6dbf7db171ed7dec754f93a98121895a2a5c06d9a53d64`
- Windows x64 sequence 6 · `dc7e4ce8d326cb8669badc54bb89cc279fcfa34a8ae142c2b86d3454d17ec315`
- Windows x64 sequence 7 · `cb528c7f0958827229c466644426d242a03f2f28fe2c5e4be2282f25ae6ae401`
- Windows ARM64 sequence 14 · `e70d405eda2c4468fab49822ad4cc6d9ae6932cc7c0815cfd28ded835a378708`
- macOS ARM64 sequence 11 · `e3fd4704cd596f9906c1ca7ea2300816065eefdeeafca29fc7dac907b3d7cd85`

The Windows project-move observations above cover ordinary folders on local NTFS. Prior-launcher compatibility after a move was observed on ARM64. The Windows evidence also includes Git interruption recovery and the packaged ARM64 notification receiver. The [Preview notification record](CHORE-20261103-005-notification-guidance.md#첫-preview-확인--2026-11-17) describes the ARM64 click, the detail subprocess and the screen observation. Use the actual candidate and host pairs for permission changes and reuse observations when the relevant inputs and conditions still match.

Before assembling a public candidate, update the installation guidance with the approved public address and command, and verify that the packaged guides and manager agree. The trial manifests above remain tied to the guides originally shipped.

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

## Follow-ups recorded on 2026-11-17

The Owner requested these follow-ups on 2026-11-17 against source revision `58e8b1e44ef25f57b7fe9e73e9341560936d7262`.

### P1: Short guide at the start of a new chat

Keep the installed `adapters/colvia-work/SKILL.md` short at entry. It should help the agent confirm the project connection, find the relevant Work and identify the next action. Load submission and recovery instructions only at the steps where they are needed. The current Preview bundles the guide from [the foundation adapter](../../adapters/foundation-work/SKILL.md).

When selecting this change, check that a new chat can resume an existing Work from the short guide and that the agent can still find and follow the full procedure when submitting or recovering. Preserve the existing approval and record protections.

### P3: Retire earlier-generation code

Inventory `src/hv2ref` and the remaining `.hrn`-era runtime, entry instructions, build inputs and checks. Before selecting removal, trace dependencies from the current SQLite Preview's build, install, update and recovery paths. Remove obsolete pieces from maintained source and build paths once that boundary is established. Preserve existing project records and the source and inputs needed to reproduce or recover earlier releases.

## Work follow-ups approved for registration on 2026-11-17

The Owner set the priorities below for candidate registration against source revision `58e8b1e44ef25f57b7fe9e73e9341560936d7262`. The [existing plain-folder-to-Git conversion candidate](plain-to-git-project-conversion-followup.md#owner-계획-결정--2026-11-16) keeps its P1 priority.

### P1: Add paths to the same Work

Start with read-only exploration when the affected paths are unknown. When the goal stays the same and additional edits become necessary, show the added files, why they are needed and what extra checks will run. Bind the user's approval to that scope change before editing the added paths. Keep the Work identity, prior approval history, exact boundaries and existing edits. If the original bytes of an already changed file cannot be verified, record that they are unavailable. Consider directory-wide approvals separately. The [implementation record](FEAT-20261119-003-scope-additions.md) covers approval-time absence for new paths and original content for existing files.

### P1: Record progress before submission

When asked to save progress, let the agent record what it did, what it checked, what remains and the immediate next action on the active Work. Saving a note keeps the Work active. A fresh chat should find the note and the approved scope, compare the note with the current files and distinguish recorded progress from any changes observed later. Keep the note separate from review submissions and their verification results.

The [first-submission implementation record](FEAT-20261119-002-pre-submission-progress.md) tracks the local candidate and its compatibility boundary.

### P1: Pause, end or replace a Work

Let the user pause a Work for later resumption or end it with a reason. When a changed goal calls for a different Work, confirm the disposition of the old Work, link it to the replacement and remove it from the active list. Preserve the old Work's approvals, submissions and files. Show how unfinished edits will be handled, and obtain approval for the replacement's own scope. Build on the [existing continuation](README.md#continuation-scope-and-remaining-criteria) and [successor criteria](README.md#verifiable-slicing).

### P2: Candidate priority, project status and dependencies

Add user-set priority to the existing candidate list. Derive the project view from Work and candidate records so it can show active, awaiting review and paused Work, the next action within a Work and any selected follow-up. Use a dependency only when one Work actually waits for another. Reuse the [existing priority and readiness criteria](README.md#continuation-scope-and-remaining-criteria), the [read-only view](README.md#human-readable-projection) and the [blocker criteria](README.md#verifiable-slicing).

### P3: Milestones when needed

Reconsider when users repeatedly need to track several Works against a shared outcome or date that the current direct parent-child relationship cannot represent. Assess that gap with the [existing work decomposition criteria](README.md#verifiable-slicing) before adding a separate milestone record.

## Historical material that stays internal

Do not import entire audit archives, desktop transcripts, VM commands, reviewer packets or cross-product planning dossiers. Preserve the originals with their existing consumers and retention conditions. Product-level requirements already owned by the development index, lifecycle documents and foundation specifications are reused rather than copied here. Earlier proposals to rely only on user Git commits for historical content, or to auto-migrate private trial installations, do not override the current preservation design and Owner scope.

The private reconciliation map records which historical sources were inspected and which were unavailable. This page contains only the technical conclusions needed to maintain Colvia; it is not an exhaustive audit of every historical artifact and does not claim that all old links or prose have been repaired.
