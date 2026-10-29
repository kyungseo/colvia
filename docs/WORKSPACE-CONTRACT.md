# Workspace Contract

Continuation-1 profile; see [authorization and qualification](README.md#continuation-1).

Status: single-home development contract with bounded worker integration. General adoption and public release remain unqualified. [Security and Support](SECURITY-AND-SUPPORT.md) lists the historical observations and their source versions; this exact candidate still needs its own qualification.

The format uses one `.hrn/` authority. Installed machine commands and the lifecycle layer build on the root primitives below.
Record and product-binding verification take place in the layers above the root primitives.

## Root Primitives

`workspace.py` provides explicit target classification, immutable root-format validation, read-only root inspection, bounded
bootstrap prefixes and an outer cooperating writer guard. It does not verify intent/Work records, install releases, or accept results.
`root-ready`, `partial-candidate` and `detach-candidate` report only the root-layer checks. Full workspace verification still requires the checks below.
The caller must verify the complete records, pending operations, product binding and executing release before any product mutation.

Primary Git checkout and standalone non-Git targets can host a control workspace. Linked worktrees, repository subdirectories,
nested repositories, submodules, separate Git directories, bare repositories and ambiguous Git results cannot mutate it. Git routing
variables are removed and optional locks disabled for probes. The target itself and its ancestors must not be symlink aliases.

A new root is exclusively created. Its exact init plan is made durable before the immutable format, ignore rules and empty intent/Work
directories. Exact complete-file prefixes support explicit recovery with the same plan and format. This is not atomic file publication:
an interruption inside a file write can leave torn bytes. A missing/invalid plan is unrecognized; a torn format is integrity-failure;
a torn ignore file is degraded. Preserve these bytes and obtain explicit manual disposition instead of replacing them automatically.
A root without a durable plan is never adopted. No initial Work is created. Missing empty intent/Work directories mean zero records;
Git clone/clean can omit them. Future record writers create required directories under the shared guard.

`format.json` has exact keys `record_type`, `format_version`, `authority_home_id`, `created_at`, `lineage`.
Version 1 uses record_type `workspace-format`; boolean versions are invalid. Unknown integer versions are incompatible. Unknown
members are degraded/non-writable. The root's exact ignore bytes are `staging/\nlocks/\n`; project authority and product files remain
tracked. The record/content and lifecycle layers verify effective Git ignore policy before mutation.

## Windows Native Observation And Publication

These rules apply only to windows-2 on its admitted native Windows runtime. Keep the trusted-local-account/cooperating-writer boundary and existing Git topology, content membership and ignore scope. Examine the absolute ancestor chain from the volume root through the target and the ancestors/leaf of each path actually inspected. Refuse reparse points and indeterminate or unreadable classifications; do not treat them as ordinary paths or absence. Preserve existing hard-link, type, identity, case/normalization, reserved-name and trailing-dot/space constraints. Do not recursively inspect unrelated excluded content merely because this clause exists. Compare opened-handle identity with the path observation and repeat the required checks before writing. A final-path string alone is not proof against every alias or same-account race.

Before any filesystem mutation, verify native local NTFS for every path the operation will create, write, replace or remove: target authority/runtime and changed content, staging, lock/scratch and any external repair backup. Include existing files whose mandatory synchronization in that operation requires a write-capable handle, even when their bytes remain unchanged; do not add unrelated read paths or every retained release to that set. For an absent path, validate the actual volume and identity of its nearest existing ancestor and the admitted creation chain; revalidate newly opened/created paths before relying on them. Do not infer filesystem/locality from a drive letter, path string, guest label or profile. Remote, non-NTFS, indeterminate or inaccessible mutation paths are non-pass. Apply this check before creating guard scratch, repeat it under the writer guard and at the required publication boundaries, and retain the preceding reparse/identity checks. A same-account race can still cause later failure; preserve the actual prefix.

Each replacement source/destination pair must be on the same admitted volume. A separate external backup may use another verified native local NTFS volume under the existing outside-target/source and durable-copy rules; this is not permission for cross-volume replace. This mutation gate does not recursively scan unrelated content or add a new filesystem condition to otherwise permitted read-only inspection. Keep existing source/read-path checks. Do not add a fixed-drive-type restriction or administrator-token gate. Standard-user qualification evidence and actual filesystem admission remain distinct.

Cooperating writers share one stable anchor and the same byte range, offset 0 and length 1, using non-inheritable handles without delete sharing. Keep indefinite contention waiting and immediate same-thread reentry refusal; add no default timeout or takeover. An interrupt before entering the mutation section must leave no held lock/handle and no authority/content writes when the invocation exits. Normal scratch parents/anchor created while preparing to wait may remain. Do not promise that the lock was never transiently acquired. After mutation entry, interruption follows the actual publication prefix and existing recovery rules. Read-only inspection creates no anchor. Qualification must cover empty anchors, cancellation/acquisition races, process termination and handle cleanup; this clause does not promise an unobserved OS release-time bound.

Map each existing required or explicitly permitted-unavailable synchronization step to its Windows publication phase. Required failure or unavailable is non-pass; NTFS alone does not waive it. Do not silently promote a helper's permitted unavailable result into a new mandatory obligation. Preserve macOS-specific mandatory sync duties. File and required directory flushes use explicit results from appropriate write-capable handles. Preserve content-before-publication ordering and each call site's parent-sync requirement, including init launcher and immutable-member revalidation. API success observes that request's OS result, not power-loss persistence.

Distinguish failure before publication, after publication but before required flush, after required flush, and unknown phase/state. Preserve actual original, staged and published bytes; never report earlier publication as absent or automatically undo it. Diagnostic phase/API/error output is not a persisted receipt field. A later invocation re-observes durable records, bytes and identity and proceeds only within the original exact operation's admitted prefix. Read-only status/doctor do not reflush. A required reflush belongs only to authorized apply/recovery and is a new observation, not proof that the earlier flush succeeded.

Windows permission bits, ACL inheritance, read-only attributes and executable suffixes do not prove POSIX confidentiality or publication completion. Do not broaden ACLs or change ownership to make the operation pass. Determine completion from admitted prefixes, exact bytes/membership and binding/receipt relationships. If states formerly separated only by permission bits lack an independent durable distinction, preserve them as unknown/non-pass. Do not invent a mode value or receipt to force classification; a required new persisted distinction must be separately specified and accepted.

New files created by windows-2 writers, including managed runtime, authority, receipts, published content, staging/scratch and external backup files, must have native FILE_ATTRIBUTE_READONLY clear before publication/use as the new file. Read-only is not an immutability, confidentiality or completion marker. Do not normalize existing files, retained evidence or read-only sources to meet this creation rule.

Before the operation's first durable authority/content/receipt/backup publication, preflight the union of existing files it will replace/remove and existing files whose required flush needs a write-capable open, even without byte replacement. Refuse the whole operation if any such file has FILE_ATTRIBUTE_READONLY set; an unavailable or unsafe observation is separately unknown/non-pass. This includes init, update/rollback, repair, detach and intent/Work/worker/planning writes. The flush subset follows each operation's actual mandatory call sites, including admitted existing staging/receipt/backup revalidation where required, not all retained releases or read-only sources. Do not omit a required flush to avoid this gate or turn permitted-unavailable synchronization into a new obligation. Normal guard-preparation scratch may remain, but no authority/content or recovery backup may be published before this check succeeds. Repeat checks under the writer guard and before the relevant replacement/removal/required flush. During recovery check every remaining replacement/removal and every required reflush in the admitted original prefix, including already published files when that prefix requires their reflush; do not rewrite the request or published evidence.

Files only read or preserved unchanged, with no required write-capable flush, are not refused solely for being read-only under this mutation preflight. This exemption does not waive bound observations such as Windows Exact Repair Observation. Directory type, identity, emptiness and access rules remain separate; a file read-only flag is not a directory access test. If attribute/identity drift or an actual replace/remove/flush failure occurs after preflight, preserve the original request, backup, evidence and actual prefix. Never clear an existing target or evidence file's read-only flag, broaden ACLs, change ownership or use delete-then-copy to force success. Completed read-only replay keeps its existing exact observations and gains no mutation gate or reflush.

Replacement stays on the admitted filesystem and uses no delete-then-copy fallback. Automatic retries are zero. On access/sharing or other replace failure, report the actual phase, native error and observable old/new/staged state; unreadable is not absent. Explicit retry reuses the existing operation, request, token, candidate, recover option and prefix rules. It introduces no retry command, one-use token or automatic replacement preview. Preserve completed replay versus pending recovery. Existing authorization may cover the exact retry; this clause adds no repeated approval when action, target, inputs and prerequisites remain covered.

## Record Encoding And Shape Boundaries

Persisted authority and planning JSON is UTF-8 without a BOM or CR bytes, with sorted keys, two-space indentation, unescaped Unicode and exactly one final LF. Digests bind the stored raw bytes using lowercase SHA-256. Stored authority and planning records must match canonical emission; invalid input is not normalized into accepted history. Duplicate keys, nonfinite numbers, malformed UTF-8 and oversized/deep input are refused. A field requiring an integer rejects a boolean.

The common JSON reader allows at most 4 MiB, depth 128 and 1,024 integer digits. Depth counts the root value as 1 and each contained value as one deeper. These are reader limits, not a promise that every document at the limit can pass its record-specific or lifecycle checks. Candidate planning additionally has its lower 1 MiB/100-candidate/1,000-decision limits. The advisory document reader's 4 MiB limit is a separate observation boundary.

Typed record IDs use ASCII `[a-zA-Z0-9][a-zA-Z0-9_-]{0,95}`. A digest reference is `{id, sha256}`; a qualified object is `{authority_home_id, kind, id}`. Field meaning fixes the referenced record kind. Persisted record and confirmation-ticket keys are exact; their required nullable fields remain explicit nulls rather than omitted keys. This does not require every CLI convenience input to spell every field: documented defaults and optional CLI fields remain unchanged. Root format, record schemas and inventory windows are independent versions. Ordinary intent drafts and Work revisions use schema 1; parent drafts/revisions use schema 2 with their additional composition/evidence fields. Identity, confirmation, decision, selection, current and manifest do not inherit that version change. Detach's paired plan/receipt versions follow Checkout-1 Transition And Detach Schema below.

Project document/content paths are literal relative NFC paths with POSIX separators, no empty/dot/parent components, backslashes, NUL or components equal to `.hrn` or `.git` under casefold comparison. Casefold/NFC aliases and file/ancestor collisions are refused; the reader does not silently rewrite spelling. Object identity, path and a digest are different concepts. Timestamps are provenance, never a selector or an authority grant.

The detailed structural checks remain in the source families below. These locators help inspect exact field sets and refusal cases; implementation or test output does not override the documented authority, state-transition or preservation rules. Report a disagreement and preserve affected state before changing either side.

| Record family | Structural and graph checks |
| --- | --- |
| Root format and init plan | `workspace.py` |
| Work identity/revision/decision/selection/current; manifest and ticket | `work.py` |
| Persisted intent identity/draft/acceptance/selection/current | `intent.py`; persisted typed ID checks are distinct from the standalone entry-classifier utility |
| Parent composition and evidence | `umbrella.py` |
| Candidate request and store | `candidates.py` |
| Product inventory, binding, lifecycle and detach | `product.py`; [Update And Rollback](#update-and-rollback-development) and [Receipt-Bound Detach](#receipt-bound-detach) govern their meaning |

These modules are under `src/hv2ref/` in the source and retained managed payload. [Guided Intent](GUIDED-INTENT-FORMATION.md), [General Work](GENERAL-WORK.md) and [Candidate Planning](REFERENCE.md#candidate-planning) define the corresponding authority and transition rules. Unknown versions/members and damaged records remain preserved and non-writable under their existing diagnostic classifications.

## Layer Responsibilities

The writer guard serializes cooperating calls only. It neither authenticates the caller nor makes several files or Git operations
atomic. It does not authorize an operation merely because the lock was acquired. The caller must revalidate under the guard and must
not recursively acquire it (same-thread recursion fails immediately). Read-only inspection never creates a lock or on-disk cache. A healthy primary status observation may reuse verified intent graphs
and a raw Git topology probe within its first Work sweep. Target/ancestor/path checks and effective ignore checks remain live. A reused
topology probe is checked again before the independent final intent read; changed observations fall back to fresh reads. No context
crosses observations or reaches writers. Intermediate changes that revert before the final probe are not guaranteed to be observed. The same anchor admits an explicit detach-recovery purpose,
but receipt verification remains the lifecycle caller's responsibility. Root-ready is the default guard purpose.
Ancestor or descendant workspace authorities are unsupported, including non-Git targets. Target fingerprints bind the literal resolved
path spelling; case/normalization aliases are not promised equivalent. Pending operations cannot resume after path relocation.

Integrated layers verify accepted-intent binding, Work currentness and bounded pending cancellation, full-project content manifests,
actual loaded-release checks, and product lifecycle. Exact worker diff application and recovery are implemented; human view is a development projection.
Exact-candidate process/recovery checks, real-project multi-worker use and measured benefit require their own evidence.


## Initial Installed Runtime Verification (Development Checkpoint)

The exact `delegation-1` inventory contains 29 managed paths, including `candidates.py`, `umbrella.py` and existing `workspace.py`
and `work.py` and excluding retired generation modules. `workspace_candidate`
reads that subset without publishing it. `verify_workspace_release` checks the
inventory encoding, ordered exact set, release ID and full digest, every payload
byte, and directory membership. Unknown empty directories also fail verification.
Managed product files and the launcher must not share a hard-link inode; both
file observations require a single link. This restriction does not change project
content membership. Work and intent publication recheck the bound runtime just
before their first truth write, including modules loaded by intervening checks.

`verify_workspace_product` reads the complete applied binding/receipt chain and
all referenced release inventories, launcher and visible managed bytes. A pending
lifecycle fails this active-runtime check; independent-source status can describe
that exact pending prefix. Product verification alone does not validate project
Work/intent truth or claim full status health. Exact repair and receipt-bound detach are implemented in their bounded lifecycle paths.

The default Work/intent runtime gate calls `require_workspace_runtime`. It
requires isolated Python startup, disabled bytecode writes, the control checkout's
launcher, and every loaded `hv2ref` module and package search path inside the exact
bound payload. A worker launcher cannot target the control checkout. Source imports
cannot use the default gate to impersonate an installed runtime. Explicit verifier
doubles remain available only as a Python testing seam; they are not CLI options.

The original runtime tests use installation-shaped fixtures. A subsequent actual
init test suite uses the unmodified managed launcher and CLI. Update/rollback now has a separate actual lifecycle checkpoint;
exact active repair now has an independent-source path; receipt-bound detach is implemented. General adoption still needs its own qualification evidence. Path/digest
checks assume a trusted local process; malicious Python object mutation and
outside edits that escape the observation points are outside their protection.


## Actual Init And Recovery (Development)

From the trusted source checkout, `colvia --source-checkout init --profile continuation-1 --target PATH
--authority-home-id ID --operation-id ID --observed-at UTC` emits a preview with
`request` (format plus lifecycle plan) and its `confirm_token`. It writes nothing.
Apply uses `colvia --source-checkout init --profile continuation-1 --target PATH --apply --input -
--confirm TOKEN`, with the exact request on stdin; `--source PATH` selects the
candidate in both calls. A changed source, target, format, or confirmation fails.
This machine interface does not replace the future human-facing onboarding.

Publication order is root ownership plan/format, shared guard, exact staged
release, immutable release directory, init receipt, launcher, then binding.
The receipt describes the planned result; its presence alone does not mean the
binding was published. Init recovery requires `--recover` and the same request,
source candidate and confirmation. No ownership plan means preserve/manual
resolution; unknown, torn or changed bytes are never overwritten. Exact completed
init replay observes the existing binding without touching records; scoped retired-entry collision retains its refusal.

The staged release is disposable reconstruction from the explicitly supplied source;
it is not authority. After release publication, product recovery validates that
complete release. Product-managed files and the launcher alone are written;
project source/docs are preserved. A preexisting launcher or old-generation home
is refused. No Gen1 item is created. Update/rollback use their own exact lifecycle plans. Exact repair and receipt-bound detach are separate lifecycle paths below; neither is an alias for init recovery.

The production launcher starts Python isolated with bytecode disabled. Before
importing package code it checks the bound inventory digest, all twelve module
bytes and its own bytes. The import root must contain only `hv2ref`, whose members are exactly the twelve managed modules.
With `.hrn` absent the installed launcher fails closed; it never automatically imports project `src`
or an old home. Trusted developer invocation explicitly uses `--source-checkout` before the command.
Generation runtime/readers and `--legacy-baseline` are removed. Source init/update/rollback/detach require `--profile continuation-1`. Repair has no profile option and requires the exact active continuation-1 release. Valid human-1/worker-1 history retains each original 27-path set; umbrella-1 retains 28, and planning-1/checkout-1 each retain the literal old 29. Entry-1 ships 29 paths with root `colvia` and `adapters/colvia-work/SKILL.md` replacing the old launcher/adapter memberships. No old membership is derived by renaming the new set. Delegation-1 preserves its historical 29-path membership/schema4. Continuation-1 has 30 paths/schema5; after its first durable switch receipt, downgrade to delegation-1 or earlier is refused. See [Continuation-1](#continuation-1-successor-contract); the earlier [Entry-1 admission](#entry-1-admission-and-publication) remains historical.
Explicit source mode does not override a present `.hrn`. These operator choices are not an authentication boundary.
Loaded-module provenance and full product checks still run at writer entry and
before publication. This is a trusted-local guard, not a signature/trust service.

The confirmation token checks consistency with the exact previewed request. It is deterministic and
can be computed by an agent; it is not proof that a human reviewed or authorized an action. The
external Owner interaction remains responsible for approval until the human surface is implemented.
An empty ignored staging operation directory can remain after successful init. It is preserved;
this checkpoint does not automatically clean up staging directories.

## Update And Rollback (Development)

Installed `colvia update --source PATH --operation-id ID --observed-at UTC` previews
a LifecyclePlan and token. Apply takes the exact plan on stdin with `--apply
--input - --confirm TOKEN` and the same source. `rollback` uses the recorded
previous active release; optional `--to ID` must name that release. It needs no
source candidate. Source recovery uses an independent trusted launcher with
`--source-checkout update|rollback --profile continuation-1 --target PATH ... --recover`.
The command must match the plan action. Same-active updates and reused operation
IDs with different bytes are refused. These are machine interfaces, not human approval.

Receipts reconstruct a single chain by full prior/result binding references. Current
is the exact published binding, never a filename or timestamp choice. Every retained
release is verified. At most one subsequent receipt can be pending; forks, orphans,
unknown files and torn records fail closed. An exact historical operation replay is
read-only and never moves current backward. History reads may occur at a relocated
path, but new confirmation and exact recovery bind the current path fingerprint.

The plan binds every intent/Work file path and digest plus the current format and
binding. Pending Work decision/selection or intent acceptance/selection blocks
preview and apply. The same checks repeat under the shared writer guard. A pending
lifecycle receipt blocks ordinary record writers and any new lifecycle operation.
Completed Work is permitted; its records and project result bytes are not rewritten.

Update/rollback preview checks the canonical plan, result binding and embedded-plan
receipt against the existing JSON reader limits before issuing a token. Apply repeats
the output check under the writer guard using the freshly observed prior binding,
before writing the exact checked receipt/binding bytes. Oversized output is refused
before lifecycle publication; it does not create a pending receipt or candidate release.
Acquiring a previously absent writer lock may still create its normal scratch anchor.
This prevents new unreadable output; it does not increase capacity or recover an
already oversized stored receipt. Preserve such existing bytes for explicit disposition.

For a same-window switch, publication is receipt (planned result), staged candidate, immutable release, atomic
executable launcher replacement, then atomic binding replacement. The retained checkout-1 to entry-1 transition instead follows its historical exclusive-publication sequence below. Current delegation-1 to continuation-1 transition keeps the same launcher path and follows the schema5 boundary in [Continuation-1](#continuation-1-successor-contract). The receipt alone
is not completion. Exact explicit recovery resumes supported complete-file prefixes.
Unknown/torn bytes or drift are preserved; no automatic undo or deletion is attempted.
A launcher/binding mismatch can temporarily prevent installed startup: use independent
source diagnostics and the original exact plan/candidate. Rollback needs the retained
previous release. Same-filesystem staging is ignored and may retain interrupted debris.

History inspection checks the full retained release chain. Its cost grows with retained
releases; production-scale cost has not yet been measured. Tests cover cooperative
serial process interruptions, not power-loss atomicity or a malicious outside writer.
Exact repair/detach and a bounded independent auditor are implemented below. Old-generation runtime/readers are removed. [Security and Support](SECURITY-AND-SUPPORT.md) summarizes historical observations for their recorded source versions. General adoption and later modified releases need their own qualification.

Rollback selects the current binding's previous release when permitted by the inventory window (delegation-1 and earlier windows are refused after a durable continuation-1 receipt; historical entry-1 receipts retain their checkout-1 barrier): a second rollback
can therefore reselect the release just left. Each switch still requires a new exact
plan/token. Same-window binding replacement preserves existing ordinary permission bits; the first entry-1 transition explicitly publishes B1 at 0600. Launcher replacement sets executable mode 0755.

For update recovery after the candidate release was completely published, the original
source checkout is not the only possible `--source`: explicitly point an independent
trusted launcher at `.hrn/product/releases/<candidate-id>/payload`. The same inventory
and plan digest checks apply; no source is chosen automatically. This works even if
the original source changed or became unavailable. Before complete release publication,
recovery needs the original exact candidate bytes (or an independently preserved exact
copy); restore those bytes and rerun the same request. If unavailable, preserve the
pending state for explicit manual disposition. Never delete a receipt to claim success.

P and Q in lifecycle tests both implement this new-format reader contract. Digest
verification does not prove arbitrary source code is compatible; release qualification
remains necessary before using a candidate. Earlier development snapshots and old
generations are not supported adoption/upgrade sources.


### Exact Active Repair

An independent source may supply only the exact active release. The normal
runtime verifier remains strict. The repair observer instead allows missing or
changed regular files only within that active release and the project launcher;
all directories, metadata, receipt history, retained releases, file kinds and
unknown-member rules are still validated. Missing directories and metadata
reconstruction are outside this repair operation.

The ephemeral confirmation request binds the LifecyclePlan(action=repair),
original/replacement path+digest+size+mode observations, complete product
observation, and an explicit external backup path. Its plan binds target, format,
active release, current binding and all truth files. `remove` enumerates existing
bytes being replaced; `preserve` enumerates the same bytes to retain in backup.
Absent files have no old bytes and are restored from the exact inventory. The
source candidate and read observations are rechecked before mutation under the
common writer guard. Pending Work/intent graphs must still be valid, but their
publication need not be complete. Product lifecycle pending is refused.

The external backup stores `request.json`, `original/<project-relative-path>`,
and, after successful verification, `receipt.json`. Before replacements, every
original byte is durably preserved. The receipt has identical prior/result binding
refs; it is evidence and is not inserted into the binding-selection chain. There
is no new authority record family or backup registry. Exact explicit recovery
accepts each requested file only in its original or restored state. A completed
receipt requires all originals and all restored target files; replay is read-only.
An unowned, unknown or torn backup is preserved, not overwritten. A crash before
the backup's ownership request exists requires manual preservation/investigation.

Files are replaced atomically through ignored staging. Restored launcher mode is
0755; other existing files retain ordinary permission bits, with special bits
removed, and absent files use 0644. Original mode is preserved in the request.
Checks cover trusted local cooperation, not an adversarial process bypassing the
guard, atomic power-loss guarantees, or authentication of the confirming human.


### Receipt-Bound Detach

A detach LifecyclePlan has `candidate_release=null`, full current
`expected_binding_ref`, target/format/truth refs, exact launcher/product `remove`
entries, and format/ignore/intent/Work `preserve` entries. Paths in these inventory
entries are project-relative; `truth_refs` paths remain `.hrn`-relative. Unmanaged
project files cannot be deletion candidates. Complete release membership, receipt
IDs, inventory digests, binding digest and preserved truth are validated before
publishing the plan. Pending Work/intent/product lifecycle blocks initial removal.

`.hrn/detached.json` is a LifecycleReceipt with the exact embedded plan,
`prior_binding_ref=expected_binding_ref`, and `result_binding_ref=null`. It is
written durably before removing the launcher, then product files in UTF-8 path
order, then empty directories by deepest-first/path order. The product root is
last. Each deletion is preceded by exact remaining-inventory/truth checks under
the common guard; no recursive deletion is permitted. A valid receipt with a
remaining suffix of that sequence is partial. Unexpected bytes, unsafe file
kinds, modified preservation entries or a non-prefix deletion state are degraded.

Detach preview checks its plan and derived receipt against the same reader limits.
Apply rechecks the exact receipt bytes under the guard before recording the receipt
or removing files. A refused preview emits no token; a refused apply creates no
lifecycle output, apart from the normal scratch lock anchor if it was absent.
These checks do not guarantee that every large workspace can detach under the
current format and limits, or make an existing oversized receipt recoverable.

Recovery requires the same explicit plan/token from an independent source and the
original target fingerprint. Complete replay is read-only. The receipt, format and
preserved inventory remain sufficient for detached diagnostics after init-plan and
all product files are gone. Read-only clone auditing does not require the original
filesystem path. It does not grant mutation rights or silently attach a new root.

Source status/doctor checks complete current Work/intent graphs in detached state.
The independent stdlib fixture checks canonical receipt/format shape, complete
inventory bytes, deletion prefix and current selection/revision refs. Its declared
scope is receipt-inventory-and-selected-refs, not the full record state machine.
`detached` is a lifecycle state, not a supported-runtime or private-admission pass.
Ignored staging/locks contents are preserved. Unknown authority root members block
removal and are not recursively cleaned. Authored documents and result paths are
preserved by excluding them from the entire removal surface.

## Planning Preservation

`planning` is an optional root directory containing only `candidates.json`. It is project-owned planning, not execution authority. A planning-1, checkout-1, entry-1, delegation-1 or continuation-1 binding admits retained planning while product is present; current writers require continuation-1. Init does not create an empty planning directory. Candidate bytes join lifecycle truth refs and detach preservation; changing them invalidates an earlier preview. Candidate temporary files stay in ignored staging. Detached source view can inspect retained planning; the independent plain auditor verifies its receipt/digest/bytes, not the full planning state machine. See [Candidate Planning](REFERENCE.md#candidate-planning).


## Checkout-1 Transition And Detach Schema

Historical checkout-1 source contract; the following schema-2 writer belongs to its retained old source. Retained entry-1 writers follow the next section; current continuation-1 writers use paired schema5 as specified at the end of this document.

The new source admits only planning-1 or checkout-1 as an update predecessor, in both preview and apply preflight. Older supported history is read-only here. The first durable checkout-1 receipt requires exact forward recovery; direct acceptance of old worker manifests requires a separately authorized new baseline/rebind/resubmission as described in Getting Started.

Detach plan and receipt schema 2 retain the existing field sets and `candidate_release: null`. Both versions must match and be integers. Readers accept paired 1 or 2; current apply/recover accepts only 2. Legacy schema 1 bytes remain readable and must be resumed with their retained old source. Partial schema 2 detach is resumed only by the new independent source with the original request/token. Completed detach does not permit init over preserved authority or a supported attach operation.

A schema-1-only plain auditor copied from an older source cannot verify schema 2 detach receipts and reports them as degraded without writing. Use an auditor from the qualified checkout-1 source for paired schema 2; this does not expand its receipt/inventory/selected-reference scope into full Work or candidate semantic validation.

## Entry-1 Admission And Publication

Retained entry-1 technical clauses, including their preparation-era labels. Source decision DR-0004 identifies the effective entry-1 set and its accepted First B1 permission supplement. They do not make the following older profiles/schema versions current continuation-1 commands; use [Continuation-1](#continuation-1-successor-contract) for that candidate.

Entry-1 changes only the managed entry/lifecycle/proof clauses described here; `.hrn/`, `HV2-`, internal `hv2ref`, authority IDs and intent/Work/candidate record meanings remain unchanged. Init and repair retain schema 1. Update/rollback plan and receipt use paired schema 2 for entry-1 candidates. Same-entry switches have empty `remove`; only the admitted checkout-1→entry-1 update has exactly one retirement entry for `hv2`, with bytes/size verified from that exact predecessor. `preserve` stays empty. Reject mixed/non-integer versions, arbitrary retirement entries and any other window pairing.

The only old-window predecessor is `{id: "product-release-8bd0eeac55fb0af92b61a7a3", sha256: "8bd0eeac55fb0af92b61a7a36a98adb9957b880c791b957b20c319a51c5577f3", inventory_id: "checkout-1"}`. Compare the complete reference. This allowlist is not artifact qualification or permission to apply. An arbitrary old program is outside the audited old-writer set. Stop cooperating writers and retire prepared tickets operationally; stored-state inspection cannot discover every ticket or stop arbitrary filesystem edits. Recheck candidate, exact old binding/launcher, topology/runtime, truth, effective ignore policy and `colvia` index/name/ancestor collisions under the common guard. The index check includes absent `colvia`, NFC/casefold aliases and descendants.

For fresh entry-1 init, any immediate-root name equal to `hv2` after NFC/casefold is an occupant, including directories, files and dangling symlinks. Do not follow, open, execute, remove or rename it. An occupant present at first admission refuses with `HV2-WORKSPACE-PRODUCT`/65 before any target write. A tracked-but-absent `hv2` alone adds no refusal. Exact incomplete init and guard re-observations repeat the check. If collision appears late, preserve earlier permitted bootstrap/recovery writes and stop further publication; do not call that zero-change. Only the existing guard's exact lock directory/empty regular anchor exception applies. This is not atomic protection against non-cooperating path changes.

Pending durable Work/intent/product operations block the transition. Selected unfinished worker records and orphan revisions alone do not; preserve them and their results. Each selected non-completed local Work, including local parents and rejected/revoked states, must have no renamed-entry path dependency in its scope or required Work/intent references. For a schema-2 local parent, include required document/evidence references from the exact sealed direct captured child revisions and bound intent confirmations, even if that child is completed or worker-mode. Exclude child scope, optional references, uncaptured children, deeper descendants and worker-mode parents. Own-reference refusal has priority; captured-child refusal identifies the parent and offending children. No historical reference is refreshed.

Each such local/parent manifest result must equal the admission snapshot excluding verified old launcher O, and the S6 snapshot excluding verified new launcher N, including entries/modes/digests/sizes and ignore fingerprint. Drift refuses; the product neither publishes nor discards local edits nor changes baselines. A selected local Work may require a separately approved changed-intent rebind; same-intent local rebind remains unsupported. With no applicable local Work, this comparison is vacuous and is not a whole-project preservation proof. Old worker manifests cannot be accepted after cutover under the renamed launcher proof: preserve result/refs, separately authorize a new control commit, explicitly rebind the same-intent worker baseline and resubmit.

| Step | Admitted state and next publication |
| --- | --- |
| S0 | Exact old O/B0 and no new receipt; preview or exact authorized apply |
| S1 | Paired schema-2 switch receipt; irreversible semantic boundary and exact forward recovery only |
| S2 | Exact complete-file candidate-staging prefix; publish missing expected files |
| S3 | Complete verified immutable new release; exclusively create N at mode 0600, one regular link, no-follow/no-clobber |
| S3a / S3b | N is a zero/strict byte prefix at 0600, or complete bytes at 0600; exact recovery rechecks descriptor/path/prefix, appends only missing bytes, syncs, sets 0755 and syncs file/root |
| S4 | Exact executable N and exact O with B0; verify both, unlink only O and sync root; if O is visible again, re-observe this same state |
| S5 | N only/B0; exclusively create `.hrn/staging/entry-<operation_id>/binding.next` at 0600, exact prefix-append canonical B1, sync, recheck B0 and replace binding; sync both directories |
| S6 | N only/exact complete B1 at 0600 or 0644; verify and synchronize current state before content comparison; never rewind binding |

Candidate permission amendment (not activated): S5 still publishes `binding.next` and the first B1 at 0600. Only an exact complete current first-transition B1 may be observed at 0600 or 0644, including after a Git checkout. This does not attest that the final sync completed: current-B1 recovery/replay repeats its existing synchronization obligations. Readers never chmod the binding. Staged or incomplete `binding.next` remains strictly 0600; executable N remains exactly 0755. Other modes, types, links, altered bytes and B1 plus remaining `binding.next` remain refused. Retained older entry-1 readers require 0600 for the first B1. The C0-M publication rule and historical activation hashes remain unchanged; exact successor qualification and separate Owner activation are pending.

All steps recheck exact plan, binding, truth and supported prefix under the guard. New installed `colvia` requires entry-1 binding and cannot write before S6. Audited old writers recheck the shared schema/window fence after acquiring the guard; the lock alone is not that fence. New independent source is the S1–S5 recovery executor, with original request/token and exact candidate. Retain recovery inputs and restoration-verified external target recovery material before actual transition.

Only the stated N/binding-staging prefixes permit byte completion. Unknown members, wrong types/modes/links, torn receipt or candidate files, executable partial N and changed prerequisites are preserved and refused. With B0 and O present, *any* `binding.next` member is unsupported, including a zero-byte file; do not retire O or alter staging to manufacture a supported prefix. B1 plus remaining `binding.next` is also refused. Exact O/N with an absent or empty exact staging directory may follow S4. Byte-identical same-account substitutions cannot establish authorship and are a retained cooperation limit. A torn first receipt or S2 member can block both old and new ordinary writers with no supported product recovery; external restoration/disposition needs separate authorization. Backup is not permission to undo S1.

Directory synchronization is mandatory for the bounded transition path. Under the guard and before the first receipt, refuse an observable unsupported directory-sync environment with `HV2-WORKSPACE-PRODUCT`/65; guard lock creation is not zero-write. Successful preflight does not guarantee later synchronization. Check each required publication/retirement sync through S1–S6, direct and reused helpers. Failure preserves exact bytes, including post-S1 prefixes and independently verified B1; it does not roll back. Before advancing on retry, repeat required syncs for admitted existing prefixes. Exact-current B1 replay verifies product/prefix/collision first, then existing file/descriptor checks and the finite directory set: target, `.hrn`, product, receipts, releases, locks, the exact candidate's inventory-derived directories, admitted existing operation staging, and surviving parents of legitimately retired directories. Do not recreate directories or traverse unrelated releases. Older historical replay must not synchronize a newer binding as though it were its B1. Re-observe current product before comparing content; no persistent sync-success bit is added. A successful retry or later healthy status does not prove earlier durability, power-loss persistence or fullfsync qualification. Shared guard and unrelated same-entry sync behavior are unchanged.

## Entry-1 Detach And Retired Entry

New detach plans/receipts use paired integer schema 3 and null candidate release. Retained paired 1/2 history stays readable and requires its exact retained old source for mutation/recovery. Schema 3 removes current `colvia` and the verified product, including each retained release's literal historical membership; it does not authorize deleting a root `hv2` occupant. The plain auditor reads paired 1/2/3 within its existing receipt/inventory/selected-reference scope.

Scoped retired-entry collision applies to independently verified live entry-1 (including supported repair), exact entry-1 init, or verified schema-3 detach evidence, not a filename guess. Exact managed O in an admitted S0–S5 transition remains governed by the physical table. On collision, lifecycle calls—including completed replay—refuse further publication/removal with `HV2-WORKSPACE-PRODUCT`/65 and preserve history, binding, occupant and prefix. Ordinary otherwise-valid live diagnostics return conflict/12 with derived collision fields and `lifecycle_ready: false`; prior damaged/partial/unsupported outcomes keep precedence. Readable content and confirmation display still require fresh checks and grant no write authorization. For schema-3 detach without binding, otherwise-valid source diagnostics report degraded/10 with the collision error and preservation guidance, not clean completion or a fabricated active binding. See [diagnostic context](REFERENCE.md#entry-1-diagnostic-context).

## Delegation-1 Implementation Candidate

Continuation-1 inherits the delegation-1 behavior described below. Follow [Continuation-1](README.md#continuation-1) for current lifecycle commands and authorization requirements. Historical versions retain their original meaning. Human authorization comes from the Owner’s actual decision; host authentication and general readiness require their own evidence.

`delegation-1` is rank 6 after `entry-1`, with the same literal 29 managed paths, root/format/binding/inventory schema 1 and `colvia` launcher. In that retained window, init plan/receipt, switch plan/receipt, repair request/receipt and detach plan/receipt use schema 4 with each action's existing fields. Switch removal is the empty list. Booleans, mixed pairs, unknown versions/windows and cross-window mismatches are invalid; schema 4 is not a wildcard for future windows.

Historical init/repair schema 1, switch schemas 1/2 and detach schemas 1/2/3 keep their historical meaning. A detach receipt proves its exact historical plan/receipt pairing and removed membership, not a reconstructible active-window identity after all managed bytes have gone. In particular the equal entry-1/delegation-1 path sets cannot independently establish old window provenance; current writer admission enforces that boundary before deletion.

Within that retained window, validated or prospective schema-3 intent history requires delegation-1 at writer admission, including Owner actions, replay and later no-grant draft publication. Historical readers validate exact references and actor/grant semantics separately from live writer admission. The schema-4 switch receipt itself excludes old writers before schema-3 publication. Repeat admission under the existing lock; an old late-lock writer that proceeds after this boundary is a design failure, not a recoverable test skip.

No new authority directory, runtime grant registry, service, SDK or persistence marker is introduced. Keep existing project truth, Git refs/index and unrelated content untouched through lifecycle transitions. Actor strings remain trusted-local-account declarations rather than authentication.

## Continuation-1 Successor Contract

The source successor accepted through source-only DR-0001 adds rank-7 continuation-1 after delegation-1 and the managed `src/hv2ref/continuation.py` module, for exactly 30 files and 12 launcher modules. Keep root/format/inventory/binding schema 1 and existing Work schemas 1/2 and intent schemas 1/2/3. Every new init/update/rollback/repair/detach uses paired lifecycle schema 5; validate exact retained action/schema pairs 1~4 without recomputing their historical managed sets.

Initial cross-window update admits only the exact delegation-1 release and inventory digest named in [Operations](OPERATIONS.md#continuation-1), with separate exact-candidate qualification. From the first durable schema-5 receipt containing the exact plan, old writers/downgrade are refused even when no continuation exists. A saved preview plan is not authoritative pending. Only the exact new source may forward-recover the new receipt prefix; retain exact old source for old prefixes. Same-window rollback requires exact P→Q→P evidence with Q-created continuation preserved.

Include continuation choices, selections and current in preserved project truth and lifecycle observations. Pending allows only exact continuation recovery/cancellation or valid exact active-release repair changing neither binding nor truth; unknown/damaged continuation refuses all official writers including repair/detach. Clone/plain read preserves historical fingerprints without rebinding pending authority; pending move/clone recovery and general damaged-current repair remain unsupported. All unrelated entry-1/First B1 and delegation guarantees remain. Implementation/qualification and each exact adopter application remain distinct.

## Windows Fresh And Same-Window Lifecycle

Windows-2 admits fresh initialization and same-window update/rollback, exact active repair and receipt-bound detach under the existing preview/confirmation, pending, truth-preservation and exact-recovery rules. For windows-2 only, this clause qualifies the common continuation-1 source-profile and exact-active-repair statements in Actual Init And Recovery (Development), the binding/current-writer list in Planning Preservation, and the new-write switch/detach version statements: source init/update/rollback/detach selects windows-2; repair has no profile option and requires the exact active windows-2 candidate; a verified applied windows-2 binding admits the same retained planning and current writer duties. It neither broadens an old source allowlist nor adds an OS gate to historical entry-1 source. No predecessor-to-windows-2 or cross-OS transition is admitted. An old window is not a fresh target; do not use detach/reinstall, receipt deletion or a replacement request to bypass that boundary. Existing macOS continuation-1 defaults and all historical window semantics remain unchanged.

Fresh init requires explicit source profile windows-2, a verified candidate with inventory_id windows-2 and the admitted native runtime. The original plan's candidate release, format, authority home, target and canonical request token bind the operation before a binding exists. New init uses plan/receipt 6 and binding 1. Same-window switch uses paired plan/receipt 6 with both prior and candidate in windows-2; rollback selects exactly the recorded compatible prior release. Do not rank windows-2 above old windows to create an implicit migration. Repair uses paired plan/receipt 6 with the existing field shape, exact active candidate, external backup and unchanged binding; it preserves the existing narrow pending-record exception. Its FileObservation.mode uses Structure's Windows Exact Repair Observation, not the POSIX launcher-0755 rule. Bytes, namespace/identity, publication prefix and binding/receipt checks remain independent of that attribute observation.

All windows-2 lifecycle creation, replacement, removal and required synchronization follows Windows Native Observation And Publication's native local NTFS and read-only rules. New managed/authority/receipt files are created with read-only clear. Before the first durable publication, reject the whole operation if any existing file to be replaced/removed or opened with write capability for a required flush is read-only, including init and same-window repair/switch/detach. For detach this gate precedes .hrn/detached.json publication and covers the complete remove set plus any existing file with a required write-capable flush; recovery checks the admitted remaining suffix and required reflushes in the actual prefix. Preserve-only truth without such a flush is not rejected for its flag alone; all bound observations still apply. This is a Windows initial support restriction, not an automatic attribute-clearing transition or a proof that later races/failures cannot leave a partial prefix.

Windows detach uses paired plan/receipt 6 with the existing detach field set. Its candidate_release remains null. The expected/prior binding ref, exact managed remove inventory, preserved format/ignore/truth inventory, original target and operation remain bound as before. Reuse the existing complete path/digest/size lists: the remove set includes the launcher, product init plan, binding, every lifecycle receipt, and each retained release inventory plus its exact 30-path payload. Thirty is the per-release payload membership, not the number of total removals. Preserve exactly the format/ignore and every truth-ref file under the existing scope; do not add arbitrary project files to removal. Only windows-2 releases using its fixed ordered membership may enter this detach plan; no historical-window mixture is admitted. Before first publication, verify the original binding and all release inventories establish that window, every planned digest and the complete removal/preservation set. Preserve size/reader-limit checks, pending barriers and exact prefix validation.

Publish .hrn/detached.json durably before any removal, then remove only verified listed files and verified-empty managed directories in the existing order. After any removal, validate the complete canonical plan/receipt pair: version 6 in both, action/operation/home, null candidate/result binding, expected/prior binding equality, exact ordered path/digest/size lists and their internal digest links. The remove list must still express the complete admitted layout: per-release inventory and exact fixed payload paths, release ID versus inventory digest prefix, expected binding digest versus its remove entry, and launcher digest/size versus an admitted retained payload launcher. Verify case/name/type, size and reader-limit constraints. These retained links are assertions bound before removal, not fresh hashes of files already deleted.

The receipt embeds the complete canonical plan. Read-only validation uses that embedded plan and the actual preserved/remnant state; it does not require a separate external original-plan file or confirmation token. Mutation recovery still requires the original exact request/token and original target under the existing operation contract. Retained plan fields do not authorize a writer merely because a reader can validate them.

Observe the actual filesystem independently. Every remaining removable file must match its listed bytes/size and the admitted removal-order suffix; every already removed path must be safely absent, never merely unreadable. After file removal, admit only the existing ordered directory-removal prefix and verified-empty managed directories. Preserved format/ignore/truth bytes and references remain exact and their current graphs retain the reader's existing validation scope. Changed preserved content, an unexpected occupant, unsafe absence or out-of-order remnant is non-pass. Mutation recovery also revalidates the original target and exact request/token; read-only clone auditing retains its existing exemption from the original filesystem path and gains no mutation right.

After inventory/binding removal, validated paired schema 6 and the fixed windows-2 contract identify the policy from this complete bound inventory and admitted actual prefix. A bare version, digest or count of 30 is insufficient. Deleted payload and metadata bytes cannot be rehashed or reconstructed from their hashes: their pre-removal validation is carried by the durable exact plan/receipt under the existing trusted-local/cooperating-writer boundary. Do not claim a new signature or hostile same-account tamper guarantee. A partial prefix resumes only through a compatible independently trusted windows-2 source and the original plan/token. A valid complete receipt supports read-only completed replay; it grants no new attachment, initialization or mutation. Unknown versions, mixed pairs, wrong membership, unsafe occupants or changed preserved bytes remain non-pass. Do not convert historical schema 1/2/3/4/5 or Windows-1 receipts to 6.

Windows publication completion follows the Windows Native Observation And Publication clause. A successful primitive, parse, matching schema or policy label alone is not a completed lifecycle. Any state requiring a new durable marker must be specified and accepted before being implemented; this lifecycle clause does not authorize guessing a completed prefix.

The Windows-2 integration retains the delegated-acceptance and continuation semantics of the common continuation-1 source. Its separate fixed 30-path inventory includes continuation.py; equal path membership does not identify the window. All five lifecycle action pairs use schema 6, and new Windows-2 writes admit neither Windows-1 nor any other predecessor. Historical Windows-1/schema4 detach evidence keeps its original meaning and requires its matching retained source; it is not delegation-1/schema4 or Windows-2/schema6 evidence. Qualification must include continuation records created on Q and read after rollback to P.
