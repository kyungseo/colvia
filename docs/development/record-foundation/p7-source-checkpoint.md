# P7 source checkpoint

Status: partial source integration under the approved 100-hour bundle. These checks do not qualify an installed runtime, Windows native paths, host permissions, notifications or a public release. P7 result review remains pending.

## Implemented and checked slices

- Logical export pins one root, derives read/write schema requirements, streams objects, flushes and fully reads the output back, then publishes without replacing an existing destination. A local receipt is separate from semantic history and does not promise continued/off-device availability.
- An unpublished generation can receive a complete audited snapshot in bounded batches, rebuild its disposable operation index from retained lineage, and seal its root last. Partial/cancelled candidates remain unselected; names cannot be reused. Same-state activation preserves old DB path/inode and refuses to overwrite a newer active root. A different/older snapshot activates as a new instance: the older instance remains fenced and explicitly readable, while the restored instance is read-only until a fresh epoch/nonce/workspace rebind. Copied DB objects are fully audited again before root sealing. A same-state update cannot clear a pending rebind.
- Store requirements grow atomically with publication. An older runtime cannot read newly required semantics or write records it does not understand. Removing a head does not lower requirements. Optional-feature enablement is separate from reader support.
- Lifecycle preflight checks effects before creating pending state. A second known pre-fence refusal aborts only exact owned quiescence; permission/storage ambiguity keeps recovery pending. Crash/fence evidence remains preserved.
- The pinned TUF client verifies fixed upstream signed metadata and target bytes. Tests cover signature tampering, expiry, preserved version counters, clock rollback, target corruption, missing trust and no-overwrite staging. No keys were generated. The test clock touches only the pinned client verification-time seam. Dependency identities and required fixture licenses are retained; this does not establish production key rotation or a release endpoint.
- Runtime slots bind the full regular-file inventory, dedicated Python and manager/product entry points to a trusted manifest digest. Source tests cover missing/changed/extra files, symlinks, stale selection, monotonic release sequence, capability-compatible recovery and missing-state repair refusal. CLI/app contexts select the same isolated command without PATH fallback. The interpreter was not executed in these selection tests. Current native inventory verification is POSIX; Windows and archive normalization remain pending.
- Optional document execution requires an explicit feature choice. Disabling it preserves old history and readers, blocks a prepared grant from starting, and cannot race a live external effect. Configuration publication CAS also protects a decision made after preview.
- Recovery may switch a broken selected slot only to the previously recorded, independently verified recovery slot. Keep the broken files and exact prior selection in an immutable repair record, preserve the release high-water mark, and do not advertise the broken slot as the next recovery choice.
- Detach reserves one project-wide pending effect, removes routing before exact owned entry blocks and locator, then retires the binding. Durable per-step intents distinguish an unapplied step from an evacuated original or installed postimage. Synthetic local-APFS checks preserve outside-block text, old records and originals, resume a recorded interruption, and refuse late user edits without clobbering them. No actual host routing is changed.
- Normalized regular-file ZIP staging binds the signed platform/channel/release descriptor, archive digest, manifest and every content hash. It refuses path traversal, aliases, reserved Windows names, links, extra files and cancellation. Staging is distinct from activation; upstream runtime archives must be normalized by the release builder before signing.
- Source-only CLI entry exposes feature preview/apply and logical backup/status. Human output omits receipt/hash details by default. The installed launcher is not replaced.

## Focused evidence and corrections

Candidate restore, generation transition, process-boundary and requirement tests passed. The added generation-test method was initially placed after its module entry point; the preserved syntax failure was corrected before rerun. Fixed TUF tests initially expected no custom target metadata, but the signed fixture has a file-permission field; the expectation was corrected to require preservation. Runtime-corruption testing initially expected only an inventory mismatch; a larger corrupted file correctly hit the earlier byte budget, so the accepted refusal oracle now includes that bound. Configuration testing initially called review for an active Work; it now uses state view. All original runs remain retained.

After the changes, 36 configuration/execution/nested-delivery/session checks passed without input drift. Source lifecycle CLI and existing ordinary CLI checks also passed. No stopped native execution lane was rerun. No synthetic behavior session or additional reviewer call was consumed in this slice.

## Remaining P7 boundaries

The source restore, detach and package staging slices are implemented and focused checks pass. Production manager composition (including actual locator/entry creation and restored rebind routing), native Windows runtime/package composition and manager activation remain unfinished. Bootstrap templates and native Windows storage primitives now have source implementations; only portable refusal tests ran for Windows, not native qualification. A signed descriptor alone is not installation. A synthetic runtime inventory is not dedicated-Python execution evidence. Imported unfinished effects remain inspection-only; automatically clearing them was not adopted.

The retained native sandbox/process-closure failure and the reviewed-source-lifetime decision remain separate morning questions. Continue independent source work; do not retry the stopped lane or change actual host permissions.

Additional focused source evidence: restore read-back and instance restoration; durable lifecycle file flushing and pinned verifier factory; ordered native detach plus runtime repair; normalized package staging. Each run completed without input drift. Native detach checks operate only on synthetic files and reuse the existing qualified source APFS effect primitive. No installation, notification, host grant or model execution was performed.

## Focused review and source entry additions

[P7/P8 review disposition](p7-result-p8-plan-disposition.md) records the limited static review and subsequent corrections. Seven focused suites passed after correcting partial-final-file publication, seal-time revalidation and Windows handle/lock declarations. Failures and the original review are preserved privately.

An installed transaction lease now pins runtime selection for each short transaction. Synthetic local checks prove that activation waits for a transaction and an old handle refuses after selection changes. This does not prove any desktop host permission path. Bootstrap renderers prepare one command per platform from an exact normalized bundle; the scripts are not published or executed. The Windows API declarations and lock rules remain unexecuted on native Windows.


## Manager composition checkpoint

This later checkpoint supersedes only the earlier unfinished-manager statements;
prior failures and evidence remain preserved.

- Managed product and manager entries require the exact selected dedicated Python,
  Python/SQLite versions and slot digest. Source test doubles do not establish an
  installed-interpreter success. Runtime leases fence old processes after update.
- Connection writes exact owned agent blocks and the launcher before the locator.
  Detach reads stored ownership, preserves later surrounding rules and all history,
  and advances journaled steps without retrying a failed effect. The manager uses
  the same management-then-runtime lock order as updates. A normal command finishes
  distinct approved steps without requiring a separate user decision per file.
- The initial native entry is standard-library Go with full inventory validation;
  Darwin ARM64 and Windows ARM64/x64 cross-builds succeeded. Windows native handle,
  SID/DACL and reparse checks are source-implemented, not executed on Windows.
- First bootstrap verifies the exact extracted inventory and dedicated process.
  Existing homes delegate to their already trusted manager; partial homes refuse
  a fresh start. New homes stage a signed target, verify platform/channel and native
  entry, recheck metadata expiry and publish selection last. Composition fixtures
  use an explicitly named verifier double; fixed TUF signature tests are separate.
  No real installation or release endpoint was exercised.
- Signed update composition preserves all registered authority backups before
  switching runtime selection and rechecks prepared metadata after backup. The
  pinned TUF client uses a versioned root plus convenience link; validation reads
  the exact versioned file and checks the link target, without following an arbitrary
  link. The original cache mismatch failure and corrected pass are preserved.
- The extracted bootstrap checker initially imposed a private-root mode on every
  inner runtime directory. Existing fixtures correctly use non-writable inner
  directories under a private root. The checker now distinguishes these conditions;
  the failed run and corrected pass remain separate.

Focused checks passed for managed entry, manager connect/detach, project setup,
first-install refusal/activation composition, slot integrity and fixed TUF trust.
Required remaining work includes packaging real managed wrappers, complete recovery
and restored rebind routing, native Windows runtime/package/workspace composition,
and actual installed-host qualification under a later authorization. An unfinished
first installation is retained for explicit repair, not silently overwritten.


## Prepared bundle and explicit recovery

The normalized bundle assembler now includes the managed product/manager wrappers,
source package, explicitly supplied normalized runtime and verifier dependencies,
fixed anchor, native entry, bilingual guide entries and required notices. It rejects
links, input collisions, missing guides/notices and source drift, and independently
checks the completed ZIP. Identical fixture inputs produce identical bytes. A host
Python invocation with `-I -B` proved the packaged manager help/import path only;
this is not execution of the fixture's deliberately nonfunctional interpreter.

The manager exposes explicit compatible-runtime recovery. A recovery process must
match the recorded recovery slot and its dedicated interpreter; it cannot run normal
project commands. Review binds current roots and settings. Applying recovery backs
up current data, preserves the broken slot and trusted release high-water mark, and
changes runtime selection without rolling data back. Late decisions invalidate the
recovery preview. Focused source fixtures passed.

Logical restore now has manager prepare/apply/status/resume operations. Preparation
fully audits/imports an unselected generation. Apply preserves a backup of the
current root and switches to a new instance requiring explicit rebind. An interrupted
fence is observed and can be explicitly completed using the recorded operation;
inspection never automatically retries it. The previous generation remains readable.

Restored-instance connection supports an existing owned integration or a new folder.
It preserves user rules and historical accepted bodies, publishes a new locator last,
and does not copy restored report bytes into the working folder. The next Work uses
new workspace identity; historical acceptance is not new current-file agreement.
A test exposed missing preview coverage for unchanged rule files. Their hashes and
modes are now part of the preview and revalidated during preparation/recovery.
Original failures and corrected passing runs are retained.

Native Windows source work remains incomplete. In particular, the directory-flush
contract cannot be assumed from file-flush success: Windows documentation requires
write access for `FlushFileBuffers`, while its documented directory-handle operations
do not establish the same parent-directory durability promise. The existing native
adapter refuses an unsuccessful flush rather than ignoring it or requesting broader
privilege. A native standard-user qualification is still needed before claiming this
boundary; no actual Windows probe was performed in this source slice.
Sources: [FlushFileBuffers](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-flushfilebuffers)
and [Directory Handles](https://learn.microsoft.com/en-us/windows/win32/fileio/obtaining-a-handle-to-a-directory).


## Capacity accounting boundary

Authority DB deduplication does not bound total disk use. Retained runtime slots,
pre-update logical backups and retired generations are separate copies. Report
these categories separately in the final capacity check. In particular, repeated
full backups of a growing history can make total retained backup bytes grow faster
than the active DB; the previous active-DB measurements do not rule that out. No
automatic deletion policy was introduced in this slice. A future verified redundant-
copy cleanup must preserve unique history, active users and the last required
recovery copy; it cannot be presented as permission to prune authoritative records.

## Cumulative source check and platform stream boundary

One cumulative run covered 85 foundation modules: 641 tests in 426.871 seconds,
with 635 passes and six failures in synthetic pending-effect injection. Those
fixtures introduced an unknown record kind without declaring its capability;
production admission correctly refused publication. Only the fixture runtime now
declares that kind. Focused effect-barrier, composition, managed-entry, package,
connection and restored-routing checks passed afterward. The original failed run
is preserved; it is not relabelled a cumulative pass. The stopped native execution
lane and unchanged process-signalling checks were deliberately excluded.

The prepared package now carries a compact agent guide. `colvia guide` verifies
that exact bundled content without opening project records. The managed entry
points direct agents to this guide and the next command's help, not implementation
source or JSON-building scripts. Existing installed guidance has not changed.

Repeated update checks reuse the already verified runtime when refreshed signed
metadata identifies exactly its manifest, release and sequence. They create no
second runtime slot, target download or backup; monotonic trust metadata is still
retained. Fixed-signature and composition checks passed. This reduces duplicate
runtime growth without deleting historical data or changing backup retention.

Runtime extraction and verified-download streams now use platform file ports.
Windows implementations retain native handles, reject reparse/link/identity
changes, use private SID/DACL checks and duplicate handle ownership explicitly for
Python streams. Inventory verification uses signed logical file modes rather than
POSIX executable bits. Its traversal/content/refusal algorithm was checked with an
explicit POSIX identity double; native Windows API behavior remains unqualified.
The bootstrap template protects its extracted runtime root with the same private
ACL as its preparation root. No bootstrap or actual setup was executed.

The pinned verifier's exact versioned-root/convenience-name pair has a separate
Windows alias reader. Only that declared pair may share two links; authority,
runtime and other lifecycle files still require a single link. Ordinary files do
not gain a general hardlink exception.

Native API references: [DuplicateHandle](https://learn.microsoft.com/en-us/windows/win32/api/handleapi/nf-handleapi-duplicatehandle)
and [Python Windows file handles](https://docs.python.org/3/library/msvcrt.html#msvcrt.open_osfhandle).
These establish API contracts, not evidence of execution on a supported Windows host.


## Native Windows source ports (not native qualification)

A separate Windows backup destination now pins the selected local NTFS parent,
creates only the new backup with a private ACL, reads back the complete export,
and publishes without replacement or cross-volume copying. It never changes an
existing destination directory ACL. Eight protocol tests use an explicitly
identified POSIX destination double; original fixture failures are retained.
This does not establish Windows durability or standard-user directory flushing.
The native operation follows [MoveFileExW](https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-movefileexw);
post-publication uncertainty remains a recovery condition, not permission to retry.

The Windows observation port pins native identities, preserves opaque symlink
leaves, rejects reparse ancestors/other reparse kinds, retains protected paths,
and checks changed reads and exact captured bodies. Portable algorithm tests
passed after correcting a case-insensitive fixture and unpublished-body reader.
Metadata reads use the same bounded native path. POSIX observation/ordinary/Git
Work and manager-entry regressions passed after platform dispatch was introduced.
Windows project setup, structural Git proof and Git invocation still require
completion; these port tests are not a complete Windows user journey.

## Windows integration and import boundary checkpoint

The read-command transport now uses a contained Windows Job with explicit stream
handles, bounded output/time and closure checks. Git observation uses native file
identities and Git's logical executable modes. Registered nested-worktree proof
has a native-identity port. Visible WSL interop markers are refused at the native
and Python entries; absence of those markers is not WSL qualification.

Owned integration-file validation is shared across platforms. Windows effects
retain the original, move only the checked native handle into an absent name,
and distinguish pre, evacuated, post and unknown states. A competing file,
changed retained original, sharing failure, cross-volume move or unsupported
executable-mode edit refuses without replacement, privilege changes or automatic
retry. Source ordering follows Microsoft's [FILE_RENAME_INFO contract](https://learn.microsoft.com/en-us/windows/win32/api/winbase/ns-winbase-file_rename_info)
and [SetFileInformationByHandle](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-setfileinformationbyhandle).
Those references establish API contracts, not native execution evidence.

Portable tests cover native-buffer packing, no replacement, failure before and
after an effect, retained originals, creation/deletion, reconnect-file ownership
and detached-file preservation. The first effect fixture used an unavailable
macOS nanosecond birth-time field and an incorrect double-exception expectation;
both original failures remain recorded. The shared integration check caught a
real directory-versus-file existence error while preparing the second file; the
native stage-directory check was corrected and the focused checks passed.

Common entry imports no longer require the POSIX-only `fcntl` dependency.
macOS connection/restore and backup behavior passed after extraction; the backup
fault injection was retargeted to the deferred native function. A portable import
check refuses POSIX-only imports and loads both common and Windows source entries.

Windows setup routes to the native file-effect port and an explicit installed
native entry, never a PATH-selected Python. The interim batch entry is only valid
for ASCII fixed manager paths and refuses other paths before connecting a project.
Unicode-safe launch, Windows restore rebind, mutating Git and native platform
qualification remain required implementation/verification work. These source
checks do not declare the Windows user journey complete or narrow the support goal.


## Default Windows paths and exact prepared-install resume

The standard Windows project entry now stays ASCII and selects the installed
native entry through the standard local-user-data environment. At generation,
that environment and the management home must match the native KnownFolder
location; no PATH Python, code-page change or host setting change is introduced.
A Unicode account name therefore need not be embedded in batch-file source.
Custom non-ASCII development homes still refuse; real cmd invocation and desktop
qualification remain pending. Restored project integration uses the Windows
retained-original port. A different platform's old launcher requires a separate
integration review rather than silently retaining an unusable launcher.

Prepared first-install recovery can finish the exact recorded install without
redownloading or replacing existing bytes. It rechecks the download descriptor,
slot inventory, native entries and trust expiry; an interruption after runtime
selection can complete its receipt without changing that selection. Changed,
partial or expired inputs are preserved and refused. The recovery entry still
needs composition into the externally verified bootstrap; this internal API is
not a completed public repair command. Incomplete download/staging, two damaged
runtime slots and native entry upgrades remain open implementation work.

Focused launcher, Windows integration, import and macOS restore checks passed.
The new resume checks initially exposed a missing target-path field in the
synthetic verifier double; the original failure was retained, the double aligned
with the actual downloader contract, and all 11 installation checks passed.
No native Windows execution, real installation, permission change or signing key
creation is claimed by these source results.


### Prepared recovery entry and saved-signature verification

The verified bootstrap now has an explicit prepared-install resume command.
It reuses the existing update origin, root trust and monotonic counters; it cannot
import the bootstrap's new root into an existing home. Both generated platform
scripts pass the operation as an argument, with invalid input rejected before
preparation. macOS shell syntax/negative argument execution and Windows template
inspection passed; PowerShell/native execution remains unverified.

Recovered target descriptions are reauthenticated against the cached signed
metadata through the pinned TUF verifier. The retained root history must start
at the original externally pinned anchor and verify each consecutive rotation.
Timestamp, snapshot, targets, exact versions and target length/hash/custom fields
are rechecked without network, counter advancement or key generation. Fixed
signed fixtures passed including altered prepared descriptions, altered cached
signatures and unavailable anchor history. This closes the prepared recovery
entry composition noted above; incomplete staging, expired preparation, damaged
native entries and two damaged runtime slots are still explicit unresolved repair
cases, not automatic reinstall permissions.

### Signed repair and retained native entry update source checkpoint

Explicit authenticated bootstrap repair stages a fresh signed runtime even when selected/recovery slots are damaged. It preserves trusted metadata counters, old bytes, project backup/settings and the runtime high-water mark. A healthy runtime refuses replacement. Cached first-install resume now reconstructs the original pinned TUF root chain and verifies cached signed targets again, not merely caller-supplied preparation hashes. Tests use the pinned verifier/fixed signed fixtures; no new keys or installation occurred.

The two native aliases now have a retained-original replacement journal. It runs inside management exclusion and the exclusive runtime lease after project backups. A pending barrier prevents another release from replacing an interrupted operation. Exact explicit resume checks the same target, trust freshness and current runtime, retains earlier evidence/backups, and either continues known file states or refuses competing files. Version 1 entry/argument/runtime-pointer compatibility is required throughout; this is not permission to introduce a new native protocol silently. Windows executable sharing/rename and native durability remain unqualified. Damaged/missing native entry bytes still refuse ordinary update; no overwrite repair is inferred.

Focused evidence: `p7-runtime-replacement-guard-location` passed after the preserved misplaced-guard failure; `p7-bootstrap-runtime-repair-entry` passed; `p7-trust-failure-guidance` passed; `p7-native-entry-retained-update` passed (3.804 s). All are source fixtures. Prepared install recovery does not silently reset incomplete trust/home or missing runtime selection.
