# P4 result review disposition

Status: authorized source corrections and focused verification; bounded correction review completed; one source-lifetime policy question remains open. Reviewer findings are static. Driver counterexamples and actual executed checks are recorded separately. No installed contract is activated and no Owner source acceptance is inferred.

## Findings and corrections

| Finding | Driver disposition | Implemented boundary |
| --- | --- | --- |
| B1 policy-file effects | Accept. Ordinary scoped policy edits and cross-workspace native application have different intermediate states. | A changed `.gitignore` in worker transitions refuses before staging/reservation. General per-step policy-edit application is a follow-up, not an unsafe automatic fallback. Ordinary scoped editing retains its existing protection. |
| B2 no-effect cancellation | Accept with root/authority and no-follow protections retained. | Cancel validates exact immutable pending/binding/authorization, current registration/selection references, original authority/destination root/stage identity, no evacuated names and actual exact preimage content. It does not require source checkout existence, unchanged unrelated content/policy, or the old file/ancestor inode. Alias/symlink/hardlink refusal and attached-path checks remain. Cancellation neither writes user files nor accepts any result. |
| M1 occupied staging | Accept explicit refusal, not automatic reuse or cleanup. | An existing per-application staging name has a specific code and directs the caller to inspect status and prepare a new application if no reservation occurred. Reproducible staged posts and failure evidence remain intact. |
| M2 inspection/guidance | Accept. | Application view inspects paths under the existing process lock without creating a missing lock, reports pre/post/evacuated/unknown and the blocking reason. Historical outcome is distinct from current file observation. Worker errors point to the exact worker application command, not a nonexistent unsuffixed operation receipt; an observable pending record is explicitly identified. |
| M3 late writes to original | Accept only for an exact verified postimage. | A retained original with its original native identity may contain a later edit after the destination reaches exact post. Preserve it and report the modification in view; it does not prevent completion of the approved post. A replaced retained inode, missing original, unknown target or modified original before post still refuses. No cleanup is introduced. |
| M4 archive after child changes | Accept. | Archive/unarchive of an already-completed head with identical plan/result/decision/context validates historical child evidence without requiring current child readiness. New submission/acceptance still requires live readiness. |
| Minor source bytes | Accept narrower correction. | Already-accepted source bodies may be applied after later source-file edits; exact current source selection and registered workspace identity still apply. A new acceptance of a reviewed source continues checking current source-file agreement. |
| Minor operation bound | Accept. | Validate all derived operation-name capacity before staging/reservation or resume. An overlong supplied operation cannot first apply bytes and then fail to journal them. |
| Minor preview/marking | Accept. | Preview distinguishes new source acceptance from already-accepted application and names the destination label. Delegated child acceptance is derived from the retained decision authorization; no duplicated marker is claimed. |

## Reproduction and test truth

The first counterexample run had eight behavior failures and one fixture setup error. It did not reproduce the archive finding: the fixture's reused `super()` was invalid for its new class. Archive was established statically and then verified after the fixture correction. The first product correction passed those eight behavior cases; the fixture still failed. The later expanded run passed the new recovery/role cases but its competing-write fixture shared the active validation context and raised candidate-not-found instead of simulating another writer. A fresh context corrected that fixture; the targeted race, archive and safe-save cancellation checks then passed. All original logs are retained, not relabelled as successful tests.

Added focused coverage includes mixed two-file progress followed by resume; parent apply/grant refusal; duplicate application reservation; safe cancellation after unrelated edit, safe-save inode replacement, source checkout removal and ignore change; retained-original late writes; empty ancestor residue; registration and connection barriers; symlink/changed-preimage cancellation refusal; changed retained-original identity; read-only inspection with missing lock; and a mocked CLI error-projection test. A later actual-dispatch recovery test separately checks destination locator independence. Source tests are synthetic local fixtures, not real host or installed qualification.

The fixed-input affected-family regression and optimized checks supply the final correction evidence. Counts and input-drift status belong to their actual run records. Unaffected foundation storage/body/ordinary evidence is reused; this is not a new full repository run.

## Next-stage obligations

P7 must preserve recovery-critical `effects/` material and extend the common pending guard to lifecycle operations. P9 must measure whole-tree observation cost across a multi-file application. Windows/native installed qualification, real power-loss behavior, desktop permissions and notification clicks remain outside this source checkpoint. The public first-format contract will be activated only after separately authorized qualification.

## Bounded correction review disposition

The fourth fresh static review supplied R1–R3 and minor presentation observations. It ran without tools or input drift; it reproduced nothing. Two reserved correction rounds are consumed. Driver ran six focused counterexamples: five failed before correction; the sixth confirms the deliberately retained reviewed-source dead end. The first corrected run passed 50 affected checks with fixed inputs. Later command-entry tests are recorded separately, not folded into that run.

- R1: revise the conditional blocker claim. The actual Git policy collector currently matches exact `.gitignore`, so the packet did not establish the claimed adapter condition. Still refuse casefold-equivalent policy basenames in the worker before any reservation as a conservative, cheap boundary. The new check proves that refusal, not the whole hypothesized intermediate-policy failure.
- R2: accept. A vacant target with the same retained original inode and exact staged post is recoverable even if the original bytes received a late held-descriptor edit. Preserve that edit, install only into the vacant target, keep original-identity/attached-path guards, and report the retained edit in both pending and completed views. No rollback or unknown-byte overwrite is added.
- R3 accepted result: accept. After reservation, an already-accepted retained result needs its exact record/registration selection, destination identity and retained bodies, not the continued existence of the source checkout. The source CLI must read the destination's own locator, not a closure that reopens the removed source root. No new acceptance decision is made.
- R3 reviewed result: needs-user. If the source checkout is removed after partial application, current code refuses both completion (source-currentness evidence missing) and no-effect cancel (an original was evacuated). Records and all bytes are preserved; this is a reproduced recovery dead end, not a pass. Do not delete the barrier or silently accept the retained result under weaker semantics. Recommended decision for the next Owner return: bind current-file agreement at explicit application reservation and complete only that immutable approved result thereafter, retaining live record/registration/delegation checks. The alternative is to keep this limitation and require source checkout retention during application; recreating a path does not restore native identity. This question blocks P4 closure, not independent execution/delivery implementation.
- Minor human output: accept. Cancel describes verified current preimage content, not a claim that no effect ever happened. Completed view also shows preserved extra edits and unavailable current inspection. Lock contention has concise guidance. Recovery subcommands require the same global source-workspace and authority options; this is source tooling, not a managed installed entry.
- Explicit reuse of an operation identifier can collide with a progress publication. Default unique IDs avoid it and fresh-operation resume remains available. Preserve as a bounded P9 command-quality check; do not claim idempotent effect replay or silently reuse staging.
- Reviewer evidence limit: tracked diff is empty for these untracked new modules. Their exact bytes are in the bounded review packet and full-file manifest. Runner input snapshots are retained privately; packet run summaries alone do not let the reviewer independently compare those snapshots. Driver fixed-input statements come from those actual runner records.

P9 cost measurement must include both repeated whole-tree observation and repeated all-item state hashing. P7 must preserve unique retained late edits. None of these source corrections qualifies installed notification, host permissions, Windows effects or power loss.


## Source lifetime amendment · 2026-11-07

The Owner approved replacing the historical reviewed-source lifetime hold with
[reservation-time source agreement](reserved-source-lifetime.md). The preserved
counterexample above describes the earlier implementation. The new source work
keeps initial agreement and exact source-record/registration/grant checks, while
allowing only the reserved retained result to finish after independent source
checkout loss. Ordinary acceptance and destination safety checks are unchanged.
Current verification and acceptance state belong to the linked amendment and the
owning Work, not to the earlier historical result above.
