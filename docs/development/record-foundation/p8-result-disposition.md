# P8 source result review and corrections

Fresh tool-less Claude CLI static review completed in 450.029 seconds, with fixed packet identities and no drift. Nine of ten authorized calls have been used. Findings are static unless an executed oracle is explicitly identified below. This review does not accept product results or authorize installation/Git publication.

| Finding | Disposition | Implemented boundary and evidence |
| --- | --- | --- |
| Completion reapplies pre-ref context and wedges later user edits | revise | Admission remains exact before CAS. N/I0 recovery completes only the approved index transition and preserves later working-file edits. Synthetic after-ref edit/recovery and before-ref edit/not-applied checks passed. |
| Recorded exit callback can lag actual closure | revise | Read current process-group absence from recorded start identity. Missing identity or live group remains unavailable. Synthetic closure tests pass; they are not native sandbox closure evidence. |
| Rewritten index can make stale stat-cache data look clean | revise | Invalidate stat cache for all serialized entries. Preserve unselected content/mode/flags. Codec checks pass. |
| Commit-only existence check misses absent transitive objects | revise | Walk candidate object closure, check every required object, flush loose objects or containing pack files and ref/log metadata. Missing candidate blob refuses before ref mutation in a synthetic repository. |
| Deleting then recreating an owned lock leaves a recovery gap | revise | Re-adopt the same owned lock; absent lock uses exclusive creation with exact I0 identity. Unknown replacement remains untouched. Synthetic absent-lock completion and foreign-lock refusal pass. |
| Mode-only partial staging may pass | defend with added test | Entry content comparison already includes mode and object identity; the explicit mode-only fixture now confirms refusal. |
| Other checks | revise | Strict paired iteration, stable index mode, no shared-repository automation, lexical staging-path checks, and lock-created callback after ownership publication. Child ref locks remain observations only. |

The correction run passed 33 of 34 checks. Its one failure was an obsolete oracle expecting a late working-file edit to block index completion. The revised oracle plus codec/closure checks passed 10 checks in 3.051 runner seconds, with no drift. Both the initial failure and exact input snapshots remain private evidence. No refusal was weakened to make an unknown effect look complete.

Remaining limits: the native Git writer is Darwin-only. Windows ref/index replacement and real installed-host qualification remain open. The integration lock is cooperative within one trusted account; it is not protection against a hostile same-account process replacing files at an instruction boundary. Group absence is not proof against deliberately detached descendants, so this port admits only the qualified Git plumbing configuration and rejects executable hooks/filters. The stopped P5 sandbox lane is separate and has not been retried.


## Platform boundary and Windows index source checkpoint

Core Git lock ownership now retains an exact scheme/value identity rather than
requiring POSIX inode fields. The matching platform port must still compare its
native identity; a Windows-tagged identity cannot claim a macOS lock. This is a
pre-publication format correction, not a migration of installed trial records.

Candidate construction, whole-index comparison, object verification and ref
admission were extracted into a shared layer. macOS owns its process/identity,
index effect and durability operations. All 14 selected candidate/integration
checks passed after extraction; that runner also requested a nonexistent recovery
test module, so the aggregate attempt is recorded as failed. The actual recovery
boundary module was then run with the new Windows protocol/import checks and
passed. The previous passed checks were not repeated merely to obtain a green
aggregate label.

The Windows child adapter streams a private prepared input file and connects
spawn/exit observations to the shared Git journal. Closure is evidence of zero
active members in the exact owned unnamed Job, not an assertion about a later
process reusing its PID. Missing or unknown closure remains unavailable.

The Windows index component retains the original and publishes prepared bytes
with exact-handle no-replace moves under a separately owned index lock. It exposes
old, evacuated, new and divergent states; partial effects, competing files,
changed retained originals and foreign locks refuse rather than overwrite.
Portable API-double tests passed. The calling Git port still needs to connect
ref CAS, durable index state, gate release and Core recovery; this component is
not yet a usable Windows integration command.

This design avoids depending on the partial replacement and ACL-merging behavior
of [ReplaceFileW](https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-replacefilew).
The native move uses [FILE_RENAME_INFO](https://learn.microsoft.com/en-us/windows/win32/api/winbase/ns-winbase-file_rename_info)
without replacement. API documentation and portable doubles do not establish
Windows ARM64/x64 runtime qualification.

### Windows Git source composition checkpoint

Common candidate/tree/index preservation logic is shared; native ownership is a scheme/value identity rather than a POSIX inode assumption. Windows Git now composes the owned Job child, retained-index publication, exact native file-ID ownership, ref CAS, process-birth checks, retained gate finalization and explicit crash recovery. CLI dispatch chooses the platform port. A crash after moving the index gate but before DB acknowledgement verifies the retained gate instead of repeating file effects.

Evidence: `p8-windows-git-composition` passed (64.967 s); `p8-windows-index-transition` passed (72.846 s); correct CLI-routing test `p8-git-cli-routing` passed (3.920 s). The composition oracle uses Mac Git plus explicit native API doubles; it is not native Windows qualification. Read-only Git object flushing, Windows sharing/rename semantics and native handle durability remain live-platform checks. Earlier wrong test-name selection failures are retained; the focused runner now rejects invalid selections before executing tests.
