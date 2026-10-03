# Workspace Contract

Status: single-home development contract with bounded worker integration. Synthetic qualification is recorded; bounded private worker installation and document continuation have been observed. General adoption and public release remain unqualified.

The format uses one `.hrn/` authority. Installed machine commands and the lifecycle layer build on the root primitives below.
Root-layer success alone does not verify records or product binding.

## Root Primitives

`workspace.py` provides explicit target classification, immutable root-format validation, read-only root inspection, bounded
bootstrap prefixes and an outer cooperating writer guard. It does not verify intent/Work records, install releases, or accept results.
`root-ready`, `partial-candidate` and `detach-candidate` are internal root-layer observations. They are never full workspace success.
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

## Layer Responsibilities

The writer guard serializes cooperating calls only. It neither authenticates the caller nor makes several files or Git operations
atomic. It does not authorize an operation merely because the lock was acquired. The caller must revalidate under the guard and must
not recursively acquire it (same-thread recursion fails immediately). Read-only inspection never creates a lock or cache. The same anchor admits an explicit detach-recovery purpose,
but receipt verification remains the lifecycle caller's responsibility. Root-ready is the default guard purpose.
Ancestor or descendant workspace authorities are unsupported, including non-Git targets. Target fingerprints bind the literal resolved
path spelling; case/normalization aliases are not promised equivalent. Pending operations cannot resume after path relocation.

Integrated layers verify accepted-intent binding, Work currentness and bounded pending cancellation, full-project content manifests,
actual loaded-release checks, and product lifecycle. Exact worker diff application and recovery are implemented with bounded synthetic qualification; human view is a development projection.
Bounded synthetic process interruption/contention is recorded for the N4 source; real-project multi-worker use and measured benefit require later evidence.


## Initial Installed Runtime Verification (Development Checkpoint)

The exact `planning-1` inventory contains 29 managed paths, including `candidates.py`, `umbrella.py` and existing `workspace.py`
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
exact active repair now has an independent-source path; receipt-bound detach is implemented. Separately, bounded private worker installation and document continuation have been observed; this does not establish general adoption qualification. Path/digest
checks operate within the trusted local process boundary, not against malicious
Python object mutation or undetectable outside edits between observations.


## Actual Init And Recovery (Development)

From the trusted source checkout, `hv2 --source-checkout init --profile planning-1 --target PATH
--authority-home-id ID --operation-id ID --observed-at UTC` emits a preview with
`request` (format plus lifecycle plan) and its `confirm_token`. It writes nothing.
Apply uses `hv2 --source-checkout init --profile planning-1 --target PATH --apply --input -
--confirm TOKEN`, with the exact request on stdin; `--source PATH` selects the
candidate in both calls. A changed source, target, format, or confirmation fails.
This machine interface does not replace the future human-facing onboarding.

Publication order is root ownership plan/format, shared guard, exact staged
release, immutable release directory, init receipt, launcher, then binding.
The receipt describes the planned result; its presence alone does not mean the
binding was published. Init recovery requires `--recover` and the same request,
source candidate and confirmation. No ownership plan means preserve/manual
resolution; unknown, torn or changed bytes are never overwritten. Exact completed
init replay returns the existing binding without touching records.

The staged release is disposable reconstruction from the explicitly supplied source;
it is not authority. After release publication, product recovery validates that
complete release. Product-managed files and the launcher alone are written;
project source/docs are preserved. A preexisting launcher or old-generation home
is refused. No Gen1 item is created. Update/rollback use their own exact lifecycle plans. Exact repair and receipt-bound detach are separate lifecycle paths below; neither is an alias for init recovery.

The production launcher starts Python isolated with bytecode disabled. Before
importing package code it checks the bound inventory digest, all eleven module
bytes and its own bytes. The import root must contain only `hv2ref`, whose members are exactly the eleven managed modules.
With `.hrn` absent the installed launcher fails closed; it never automatically imports project `src`
or an old home. Trusted developer invocation explicitly uses `--source-checkout` before the command.
Generation runtime/readers and `--legacy-baseline` are removed. Source init/update/rollback/detach require `--profile planning-1`. Repair has no profile option and requires the exact active planning-1 release. Valid human-1/worker-1 history remains readable with each window's original 27-path membership. Retained umbrella-1 history has 28 paths. New candidates declare planning-1 and ship 29 paths. After the first durable planning-1 receipt, older-window downgrade is refused. See [Transition To Planning-1](GETTING-STARTED.md#transition-to-planning-1).
Explicit source mode does not override a present `.hrn`. These operator choices are not an authentication boundary.
Loaded-module provenance and full product checks still run at writer entry and
before publication. This is a trusted-local guard, not a signature/trust service.

The confirmation token checks consistency with the exact previewed request. It is deterministic and
can be computed by an agent; it is not proof that a human reviewed or authorized an action. The
external Owner interaction remains responsible for approval until the human surface is implemented.
An empty ignored staging operation directory can remain after successful init. It is preserved;
this checkpoint does not automatically clean up staging directories.

## Update And Rollback (Development)

Installed `hv2 update --source PATH --operation-id ID --observed-at UTC` previews
a LifecyclePlan and token. Apply takes the exact plan on stdin with `--apply
--input - --confirm TOKEN` and the same source. `rollback` uses the recorded
previous active release; optional `--to ID` must name that release. It needs no
source candidate. Source recovery uses an independent trusted launcher with
`--source-checkout update|rollback --profile planning-1 --target PATH ... --recover`.
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

Publication is receipt (planned result), staged candidate, immutable release, atomic
executable launcher replacement, then atomic binding replacement. The receipt alone
is not completion. Exact explicit recovery resumes supported complete-file prefixes.
Unknown/torn bytes or drift are preserved; no automatic undo or deletion is attempted.
A launcher/binding mismatch can temporarily prevent installed startup: use independent
source diagnostics and the original exact plan/candidate. Rollback needs the retained
previous release. Same-filesystem staging is ignored and may retain interrupted debris.

History inspection checks the full retained release chain; cost grows with retained
releases and is not yet measured as a production-scale claim. Tests cover cooperative
serial process interruptions, not power-loss atomicity or a malicious outside writer.
Exact repair/detach and a bounded independent auditor are implemented below. Old-generation runtime/readers are removed; the human view has bounded private narrative-review evidence on the earlier human-1 runtime, with subsequent bounded private worker installation and document-continuation evidence. These observations do not qualify general adoption or later modified release bytes.

Rollback selects the current binding's previous release when permitted by the inventory window (older windows are refused after a durable planning-1 receipt): a second rollback
can therefore reselect the release just left. Each switch still requires a new exact
plan/token. Binding replacement preserves existing ordinary permission bits; launcher
replacement explicitly sets executable mode 0755.

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

`planning` is an optional root directory containing only `candidates.json`. It is project-owned planning, not execution authority. An applied planning-1 binding is required while product is present. Init does not create an empty planning directory. Candidate bytes join lifecycle truth refs and detach preservation; changing them invalidates an earlier preview. Candidate temporary files stay in ignored staging. Detached source view can inspect retained planning; the independent plain auditor verifies its receipt/digest/bytes, not the full planning state machine. See [Candidate Planning](REFERENCE.md#candidate-planning).
