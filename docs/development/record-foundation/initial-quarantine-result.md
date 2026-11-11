# First-install quarantine source result

Status: implemented, independently reviewed and corrected; focused source checks passed.
Owner acceptance and actual installation qualification remain separate.
[Approved scope and plan-review disposition](initial-quarantine-plan.md).

## Behavior

The first publisher stages every node and records its native identity before it
becomes live. A pre-existing file or directory is not adopted because its bytes
match. Every generated executable, descriptor and receiver directory is covered.

An explicit offline preview identifies one unselected, current initial attempt.
After exact confirmation, a permanent intent blocks all old forward actions.
Only that attempt's files are moved to private flat retained names; proven empty
directories are removed non-recursively. Identity, complete inventory and bytes
are checked around effects. A partial or indeterminate operation is retained for
exact explicit resume; foreign files and registrations are never swept away.

Completion reserves one successor in the existing retry chain. The verified
bootstrap constructs the network port only after retirement completion and that
edge. A failed successor preparation is recorded and not automatically repeated.
Repeating the old completed quarantine does not inspect or move successor files.
The old slot, attempt, publication evidence, trust root history and learned floors
remain. No expired payload is executed and no anchor is imported over existing
trust. Unreceipted old trial files remain unavailable for automatic quarantine.

## Executed evidence

- Affected initial publication/install/resume/receiver/bootstrap selection: 46
  tests passed, 5.312 seconds, no input drift.
- Consolidated affected install, quarantine, retry, renewal, rollback, native entry,
  bootstrap routing and trust selection: 130 tests passed, 30.058 seconds, no drift.
- Two additional focused checks passed in 0.947 seconds: real fixed signed trust
  metadata/floors stay byte-identical across quarantine and claim, with no fetch;
  a matching but foreign initial file is not given ownership. No keys were created.
- The new sequence recovered an expired, replaced-target partial first attempt and
  selected a fresh synthetic target. Every publication position and each quarantine
  boundary were interrupted and explicitly resumed. Races, altered identity/mode,
  links, foreign pending state, added files, lost move acknowledgement, duplicate
  callers and failed successor preparation have focused assertions.

Counts overlap and are not added to the previous 822-test checkpoint. The first
quarantine run failed on a directory passed to the regular-file exists primitive;
that call now uses strict not-found detection followed by private-directory validation. Access-denied and indeterminate lookups propagate rather than count as absence.
The next run exposed a test injecting a foreign file into a different directory
than the one being removed: the product correctly refused at its next inventory
check. The corrected fixture injects at the actual final rmdir and confirms native
nonempty-directory refusal. Both original failures are preserved.

## Limits

All writes were to source or inert durable synthetic fixtures. Native local file
checks do not qualify actual installation. Windows no-replace/sharing protocol
doubles do not qualify native Windows durability, security descriptors or scanners.
Global OS receiver registration is not inferred from missing local markers. No
actual installation, privilege expansion, key generation, notification, product
commit or publication occurred. The four earlier policy/host holds remain held.

## Final review disposition and verification

The fresh, tool-free plan and result reviews consumed 237.217 and 429.550 seconds.
Both fixed input sets remained unchanged during their own reviews. Reviews were
static, not executed reproductions. The raw packets, responses, rejected first
transmission and subsequent exact-packet Owner permissions remain private.

| Result finding | Driver disposition |
| --- | --- |
| POSIX rename allegedly lacks parent sync | Not established: the existing native exclusive-rename primitive already synchronizes both directory descriptors. Do not duplicate that change. Separately strengthen resume: synchronize surviving publication/quarantine parents again before terminal publication, because an earlier move can succeed while its durability acknowledgement fails. |
| Missing POSIX birth identity | Fail closed when birth identity is unavailable. Linux remains outside the current platform support contract. |
| Windows file identity | Existing implementation already uses the 128-bit FileIdInfo API and requires local NTFS. No replacement API is needed; native Windows qualification is still separate. |
| Indeterminate path lookup treated as absent | Replace lexical existence checks on this path with strict lstat: only FileNotFoundError means absent; other failures stop the operation. |
| Quarantine parent replacement | Revalidate recorded home/quarantine identities in every state inspection and bind move parents to recorded identities, including initial publication. |
| Name-based move/removal race | Retain observed identity checks and native no-replace/nonempty refusal. Do not claim hostile same-user isolation between system calls; this residual boundary is explicit below. |
| Recomputed receiver surface | The candidate is derived from the retained verified immutable slot; it does not execute old payload code. Damage to that slot stops recovery with evidence preserved. Do not weaken ownership to resume through corruption. |
| Foreign registration between completion and successor claim | Retry claim now checks local choice/registration/pending markers as well as published files. No OS registration mutation is added. |
| Completion and repeated claim details | Validate terminal intent shape, recheck base after the directory checkpoint, and report a valid later descendant without downloading or preparing again. |

Driver also closed a completion gap: after the last injectable boundary, every
owned node must still be retained or removed. A same-identity file moved back to
its live name cannot be declared quarantined. Recheck this after final parent
synchronization as well.

The final affected selection passed **141 tests in 35.014 seconds**, with no input
drift. This includes nine new cases for denied lookup, replaced quarantine parent,
returned live file, failed sync acknowledgement, new registration, malformed
terminal intent, repeated ancestor claim, interrupted publication and recorded
parent binding. Reuse the earlier 18 bundle/managed-entry routing checks and two
fixed-trust/foreign-ownership checks; their counts overlap, not additive coverage.

The runtime-specific name-based effects assume a cooperative single-account
installation. An unsynchronized hostile process can still swap an empty directory
between validation and native removal. This implementation does not promise
handle-based isolation against that adversary. Unknown observed outcomes retain
the barrier and evidence. Power loss, native Windows scanners/sharing and real
installed bootstrap execution remain qualification work, not synthetic passes.

## Continuation

This closes the source recovery gap for an exactly receipted partial initial
publication whose old target is expired or replaced. Owner acceptance is still
separate. The source-result lifetime decision, native process-closure diagnosis,
unfinished external-effect restore policy and Codex write-behavior diagnosis
remain held. They are not implied by this recovery approval.


Owner accepted this source result on 2026-11-07. This acceptance does not qualify
actual installation or authorize an update, commit or public release. The historical
review/checkpoint statements above describe their recorded completion time.
