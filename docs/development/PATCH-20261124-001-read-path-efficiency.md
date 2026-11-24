# Read-path efficiency Phase A

State: Phase A implementation and verification complete. Owner acceptance and Git publication remain separate decisions. The approved [candidate and Phase A scope](read-path-efficiency-followup.md) are the planning basis. The [x64 closeout](FEAT-20261122-002-multi-submission-acceptance.md#owner-closeout-and-follow-up-order--2026-11-24) accepts the verified correctness scope. Windows performance remains open. Phase A precedes the separate Codex qualification.

The approved order is x64 closeout, operation-scoped verified reuse (R2), guarded lease-writer audit and conditional deduplication (R1), same-call connection resolution reuse (R4), read budgets (R5), matched Mac measurement, complete normal and parent-optimized regression, one compact Claude static review, and physical x64 supplementary validation or a prepared device handoff. The Owner supplied this implementation order and specified one Claude review after the regression. The earlier Windows read-only measurement is reused. No preserved acceptance or application request is replayed.

The starting commit is `9fbe2a530b181bbb6d6cc5c8a909d69edb433899`; the isolated working base includes the exact pending x64 source as a separately recorded overlay. The latter preserves the already qualified starting behavior without a Git commit. Started 2026-11-24 at about 20:14 KST. Total elapsed limit 28 hours. The initial 13–24-hour estimate includes device and test waiting and excludes Owner decisions. The morning report uses the Owner's stated threshold or the completed queue. No report timer is necessary; the canceled decision reminder is separate.

Implementation retains the final publication guard and closure, active generation, identity, fence and claim checks, exact head CAS, and zero-or-all acceptance. A fresh operation never inherits previous trust; body contents are not retained in a cache. Read-only commands keep their existing independent guards. No journal, settings, permissions, real-user data, Codex qualification or Git publication change is in scope.

## Work checkpoints

- x64 correctness closed and performance moved here by the Owner. The earlier morning decision reminder was canceled. The existing x64 worktree remains the closeout and baseline; implementation is isolated in a dedicated Phase A worktree.

- R1 writer audit found that slot initialization and activation take the exclusive runtime lock, uninstall and restore hold management and runtime locks, reinstall completion is called only under both locks, and complete removal publishes its live marker under the same locks. The shell and native launcher paths read the live selector and delegate writes to those maintenance paths. The implementation drops the two duplicate selection/marker checks inside a read transaction while retaining entry and exit plus both store-identity and authority checks. Write transactions, including final publication, keep the original lease checks.

- R2 implementation is confined to ordinary and grouped mutations, with a bounded memo of verified immutable published metadata on the exact store handle. Each operation has a fresh scope. Ordinary and grouped read-only entry points suspend the memo. Private staged chunks keep their claim context and proofs inside their validator. Published body proofs can be reused across validators of the same operation without retaining chunk bytes. The publication's dependency walk and transaction still use uncached reads. R2 never memoizes mutable roots or heads.
- R4 passes immutable connection identity resolutions through a single workspace verification. Mutable head/index and filesystem/Git checks still run in their original order. Resolutions are discarded before the next call.

- R5 adds guarded-counter regressions for ordinary acceptance, ordinary read-only views, 32 MiB bodies, one Git-connected identity resolution, and eight-member finalization. Additional checks pin per-handle scope, final store-generation validation and original write lease checks. The corrected targeted selection ran 16 and passed. An earlier targeted selector named a nonexistent case; its remaining 42 cases passed and the actual exact-replay test ran in the corrected selection.

## Matched macOS comparison

The same fixture program ran sequentially against the byte-matched inherited x64 worktree and Phase A. Measurements exclude environment setup. Seconds are single-run observations; counts are deterministic-test inputs. The earlier 106,040-read profile predates the inherited terminal correction and is historical context.

| Scenario | Guarded read transactions, before → after | Elapsed seconds, before → after | Other observations |
| --- | ---: | ---: | --- |
| Ordinary acceptance with 3,000 files | 2,534 → 472 | 1.2598 → 0.9258 | SQLite object reads 2,700 → 637 |
| Ordinary read-only view with 3,000 files | 130 → 94 | 0.0415 → 0.0352 | No work-scope memo; R4 removes duplicate semantic resolution |
| 32 MiB body acceptance | 709 → 325 | 0.3843 → 0.2490 | Physical object-loader body reads 224 → 112 MiB |
| Git-connected submission | 752 → 377 | 0.5844 → 0.5446 | Git processes 63 → 63; freshness checks preserved |
| Eight-member terminal publication | 658 → 177 | 1.8602 → 1.7127 | SQLite object reads 830 → 344; body bytes 614 → 13,279 because chunks are not retained |
| Eight-member completed fresh-fixture replay | 70,508 → 8,800 | 22.7705 → 6.9101 | Outcome and root were identical after replay on each newly created Mac fixture |

The 32 MiB row counts all chunk bytes through the physical SQLite object loader. The earlier standalone 192 MiB observation counted public load calls. The matched denominator for this table is the new 224 MiB starting measurement. No preserved request was re-executed. The complete regression is running on the consolidated immutable input inventory in both modes.

## Assumptions used

- Isolate Phase A from the closed x64 worktree, inheriting its exact uncommitted source in a reproducible overlay without creating a commit.
- Integrate reuse into ordinary plan, approve, start, submit, accept, revise and archive and grouped create, approve, candidate, check, dissolve, execute and cancel. Future mutating services can opt in after checking their effect boundaries.
- Use 2 MiB, 2,048 metadata entries and a separate 8,192-proof bound. Bypass the cache when a bound is reached. Keep private import claims local to their validator and store no body chunk bytes.
- Keep both read lease boundaries and all four write lease checks. Treat formal read-only snapshots for ordinary screens as a separate design choice. No changes to journaling, settings, permissions or publication.

## Read-only design note

The notification-detail path demonstrates a guarded, read-only snapshot that ends before live workspace and Git checks, followed by an exact route/root check before returning current details. An ordinary Work view would first need an explicit split between its immutable record display and live file agreement checks. That design can use one short read transaction for the historical part, close it before opening the workspace or Git, and recheck the exact selected heads and generation afterward. Phase A retains the current guards and does not switch ordinary views to this design.

## Regression preparation

The first ordinary full partitions discovered an omitted task-parent directory in the inherited external test runner profile. They were stopped with their failure ledgers preserved. The runner now allows enumeration of this specific synthetic task parent, as the predecessor runner already did for its own parent. Its write boundary, network restrictions and product/filesystem contracts are unchanged. The original native partitions remain valid and in progress on unchanged source. The corrected ordinary partitions run against that same exact source. The Windows input packet and exact eight-file production patch are ready. The Windows thread is currently reachable; no physical runs are started until the one Claude source review.

- The native Mac partition completed with 92 executed tests and no problems in each mode. The corrected ordinary partitions are running. Both reproduced a stale Windows port mock expectation inherited from the x64 candidate. The same single test fails on the untouched inherited branch because the mock expected no grouped argument, while its actual product call explicitly passes `grouped=False`. Keep the running collection frozen. Resolve the expectation in the Phase A test only after collecting both full ledgers, then verify the same assertion in both modes along with the independent Windows grouped/ordinary port routing check. No product compatibility behavior needs to change.


## Full macOS regression

Both normal and parent-optimized regression runs covered 3,262 discovered occurrences each, including 92 native cases per mode. In the two complete ledgers, four ordinary failures were repeated: the inherited mock expectation above and three U2 fixture preparations that resolved byte-identical worker resources in the earlier worktree. The synthetic runner fixture now points these three exact files at the current worktree, with byte equality checked. The ordinary mock explicitly expects grouped=false on both ordinary variants, and the independent group test still requires grouped=true. Both focused runs passed all five affected or related cases. No production file changed during or after the suite. The reconciled result per mode is 2,734 passed, 526 skipped, two partially skipped, zero unresolved failures. All skip identities and reasons match the earlier qualified suites. Original failed ledgers and the focused output remain available for acceptance, review and reproducibility of the corrected runner.

The matched regression took about 73 minutes in parallel. Focused correction took 1.3 seconds per mode. Physical Windows validation and the one Claude review remain next.


## Independent static review and disposition

One first-party Claude Code subscription review ran with no tools or execution. The reported model is Claude Opus 5.5, session e1893d4e-0094-4667-9a04-d965c5c20ba7. Input was the eight-file production diff and selected counters (request SHA-256 45590cdaffd7d789b4cc93ac388ee7f79eca2c72cbb1a8e68046d9dde8396b90, reviewed source patch SHA-256 eea1113579dc71f5d6e89006b5a9ab9606c04f94416eba124a429cdc70f6e0eb). The raw response remains in the private task evidence for Owner review. The reviewer saw a condensed regression excerpt that omitted the optimized focused-correction lines. Both full and focused mode ledgers are available to the Driver.

- F1: Tightened sharing. Publications with staged chunks or incoming body descriptors keep their proofs local to the validation view. A synthetic losing CAS followed by a second publication now tests that an unpublished descriptor is actually looked up and refused. Staged chunks are never incoming records.
- F2: The supported store staging entry rejects every kind except body.chunk version 1. Its claims therefore cannot supply a staged manifest. The real multi-chunk acceptance and staging checks cover the supported contract.
- F3 and F5: Nested calls on the same store and thread share the active operation scope. A trailing guard runs only if a cache hit followed the last successful guarded transaction, and closed scopes cannot trigger it. Focused checks cover a selected-generation change after a durable commit, after an unguarded cache hit, and inside a closed scope.
- F4: Other chunk versions go through the original registry/loader order. Chunk refs still count toward path depth and edge/reference limits, and stored capabilities and publication claims are checked on their original paths. Body validation still streams, limits and hashes the complete content. The focused error-order regression covers missing and unsupported chunks.
- F6: Repeated immutable reads can defer selection detection until the next live check or the return guard. Explicitly read-only commands, mutable heads, final publication and lease boundaries remain live, as authorized for operation-scoped reuse.
- F7 and F8: The two store guards are explicit in the transaction and the lease holds the runtime shared lock through both selection checks. Active callbacks are assigned only at construction. The metadata memo shares Python bytes references; an incoming metadata window remains separately bounded. Effective connection identity consists of frozen values resolved from exact refs through the supplied loader. The live head/index/Git checks remain independent.
- Body-byte attribution is isolated from timing and retained with the matched measurements. The final code was intentionally not sent for a second Claude review. The combined regression is repeated because the review changed a shared transaction and proof boundary.

The reviewed-to-final production change is confined to the store implementation. Final source patch SHA-256 4774ebed1cec4b8ad31a331d21a11cfb908149ca59c545a12c4f13af3d9fc9c8. The x64 input is this final patch, with the prior exact parent identities unchanged.

Physical x64 revalidation was dispatched to the designated reachable device at 2026-11-24 21:53:34 KST. Its two-hour stop is 2026-11-24 23:53:34 KST. The case uses a fresh managed slot and fresh synthetic work and group requests. Nightly macOS final regression is independent of the device runs.

Final focused tests passed (normal: 19 passed in 173.952 s; optimized: 19 passed in 176.711 s). This includes the store proof/guard cases, staged claims, original runtime lease write guards, and fresh Mac 3/4/8-member recovery and exact replay. The first post-review focused selector had a misspelled class name; the corrected two runs use the actual test IDs.


## Final matched Mac measurements

The earlier table records the reviewed snapshot. This table reruns the same synthetic workloads on the inherited starting source and final corrected source, sequentially. Logical counters depend on the generated graph and its selected objects. These single-run times describe the exercised Mac fixture.

| Scenario | Guarded reads, before → after | Seconds, before → after |
| --- | ---: | ---: |
| Ordinary acceptance with 3,000 files | 1,997 → 471 | 1.1091 → 0.9042 |
| Ordinary read-only view with 3,000 files | 130 → 94 | 0.0419 → 0.0350 |
| 32 MiB body acceptance | 604 → 324 | 0.3242 → 0.2483 |
| Git-connected submission | 740 → 376 | 0.6315 → 0.5063 |
| Eight-member terminal publication | 658 → 177 | 1.7974 → 1.6613 |
| Eight-member replay of the new synthetic fixture | 62,815 → 7,645 | 20.5226 → 6.2541 |

The 32 MiB case read 144 → 112 MiB through the physical object loader. The Git submission still invoked 63 Git processes. The eight-member terminal measured 614 → 13,279 chunk bytes. The fresh grouped replay returned the same result and selected root under each build. These samples did not re-execute any preserved request.


The separate call-stack measurement accounts for the terminal chunk reads. The inherited validator loaded 343 bytes for closure checks and 271 bytes for actual body consumers. The corrected variant had no physical chunk reads attributed to closure checks in that terminal sample. Actual body consumers read all 13,279 bytes because they receive transient bytes and cannot reuse a proof as body contents. The earlier validator retained chunk bytes and served more of those reads from memory. The trade-off is deliberate under the Owner's no-body-bytes reuse rule. Read-only replay still incurs substantial semantic and body work, documented as a later consideration. The separate stack instrument was not used for the elapsed time table.


## Physical Windows x64 revalidation

The final eight input hashes, exact patch and canonical identity manifest matched on Windows 11 x64 in the existing standard-user managed CLI test lane. Physical closure finished at 22:45:52 KST inside the 23:53:34 KST device allocation. The tested slot used a fresh synthetic ordinary workload and eight-member group. Prior correctness and timeout evidence hashes were unchanged.

- Ordinary work passed plan through acceptance and independent review. Its exact result and independent view passed. The run took 160.848 seconds and its accept command took 21.065 seconds. The independent view entered zero write transactions and left the authority root, pending status and target bytes unchanged.
- The protected check verified eight files and exited zero. Applying published one completed root with eight exact accepted decisions and no PENDING. The previous root contained zero accepted decisions. Windows checked resulting file identities and hashes, sixteen native move events and eight per-file progress records. Earlier native interruption and replay evidence was reused. No preserved request was executed.
- The first synthetic group creation was correctly refused for a missing pre-feature backup. There were zero writes in that command. The runner confirmed the eight plans and unchanged unpublished state, obtained a backup of the exact current root, and continued the fresh trial. The first read preparation also corrected a synthetic JSON-format error.
- The grouped accept CLI took 479.273 seconds (7 min 59 s). The 2,273.807-second trial includes setup, the backup correction and the final check. The final zero-to-eight publication took 11.744 seconds and 79 guarded reads. NTFS application and verification took 339.040 seconds and 5,057 of the CLI's 7,026 guarded reads. This was the dominant acceptance phase. The earlier 74 min 51 s finalization was on an older build and different run.
- Managed exact-ref reads averaged 37.039 ms and 109 product open attempts per call. The same new SQLite file and refs in the source-only control averaged 19.935 ms and 54 opens. The managed selection was checked once at entry and once at exit. The earlier 47.078-ms, 140-open managed sample used a different store and refs. A matched speedup percentage is unavailable.
- All 42 owned Jobs ended with no active processes and both streams at EOF. There were no timeouts. The native evidence index SHA-256 is 905a60c7a7979ea81d7f68c89ad1bb549a77ea366b147fb265accb5b60d44f94. The exact readback and reported evidence digests are retained in private Phase A evidence and were reconciled to the local source patch and manifest.

Completed terminal publication is substantially faster in the observed run. Windows user-visible end-to-end performance remains open. Native target application and verification and per-member preparation are the largest measured costs. Existing Windows x64 file-based check scope applies. Final macOS regression reconciliation remains in progress.


## Queue closeout

The final normal and parent-optimized macOS regressions both passed. Each mode reconciled 3,266 discovered occurrences: 2,738 passed, 526 skipped and two with skipped subtests. Skip cases and reasons match the qualified baseline. Ninety-two native cases per mode passed. Both ordinary partitions and both native partitions reported exit zero. The normal and optimized ledgers used one identical source and test inventory. The eight Phase A production inputs matched the device. The initial synthetic test-path and inherited mock corrections were resolved before the final full runs. No product regression remained.

Items 0–8 in the approved queue were completed by 2026-11-24 23:14 KST, about 180 elapsed minutes from the recorded start against the cumulative 28-hour limit. The one Claude review and the actual Windows run are separately recorded above. The earlier morning decision reminder was canceled. No commit, push, public support or release action was taken.

Remaining Owner decision: accept Phase A and decide how to integrate its change with the existing x64 work. The agreed provider order puts Codex qualification after Phase A. Residual Windows application and preparation latency and the Phase B policy choices stay open.

Retention: keep this dedicated worktree and its scoped source delta for Owner integration and Codex qualification. Keep the final tested digests, private review response, reconciled macOS ledgers and native measurement/readback for acceptance and the follow-up decision. The earlier x64 worktree and retained native evidence remain the baseline and interruption/recovery record. Reassess the runner working directories after acceptance and the next Windows evidence handoff.


## Owner acceptance and Phase B authorization — 2026-11-25

The Owner accepted the final Phase A patch with the Windows input SHA-256 `4774ebed1cec4b8ad31a331d21a11cfb908149ca59c545a12c4f13af3d9fc9c8` and matching manifest. The previous x64 closeout precedes Phase A in local Git history. Both belong to the Phase A branch. Push, PR, main merge and release remain separate Owner decisions.

Phase B now precedes Codex verification. Its approved stop is 2026-11-25 09:00 KST or 12 elapsed hours, whichever comes first. The working estimate is five to nine hours. The existing native x64 lane has a two-hour allowance. Use fresh synthetic ordinary and eight-member workloads and leave the preserved requests untouched.

Phase B covers bounded guarded reads, command-specific body verification, same-command reuse of middle workspace checks, and a short guarded record snapshot for ordinary Work view. Full body hashes stay at fresh import, file application and terminal acceptance. Approve and start check descriptor and referenced chunk identity, sizes and publication claims. Full workspace checks stay at command entry and immediately around writes and publication. The ordinary view closes its record snapshot before live workspace or Git checks and rechecks the selected head and generation before returning.

The existing closure, active generation, store identity, fence and claim checks, exact head CAS, and zero-or-all acceptance are mandatory. Phase B excludes R6, verified-runtime reuse, journal/settings/permissions/format changes, and Codex verification. The Phase B development record owns implementation, comparisons, one tool-disabled Claude result review, and conditional local commits after the required checks.
