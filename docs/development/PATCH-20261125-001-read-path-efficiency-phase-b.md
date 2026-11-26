# Read-path efficiency Phase B

State: Phase B implementation, review and verification accepted by the Owner on 2026-11-25. Windows performance remains unresolved. The Driver owns the implementation and evidence. The starting source is `0df39779dda5a29a008531254529e6d846967367`. Its first parent `cf8a15c449cc68d120da094f7bf30eef4336ef19` exactly matches the 41-file inherited x64 manifest. Phase A's final production patch is `4774ebed1cec4b8ad31a331d21a11cfb908149ca59c545a12c4f13af3d9fc9c8`. Its complete Mac inventory and eight final Windows input files were checked before the two local commits. The Phase A record carries the [dated Owner acceptance](PATCH-20261124-001-read-path-efficiency.md#owner-acceptance-and-phase-b-authorization--2026-11-25).

The Owner supplied and approved the detailed Phase B plan, then explicitly waived the separate R0 for this exact scope. One tool-disabled Claude result review remains mandatory. Phase B precedes Codex coordination qualification. Work began about 00:38 KST. The earliest stop is 09:00 KST on 2026-11-25 or 12 elapsed hours. The estimate is five to nine elapsed hours. Windows has a separate two-hour allocation inside that deadline. No push, PR, main merge, release, runtime reuse, Codex trial, settings, permissions, journal, record format, R6 or preserved-request replay is in scope.

## Delivery and evidence

1. Use the existing Phase A physical result to prioritize bounded immutable-read batching, descriptor checks for non-body-changing approvals/starts, and middle same-command Workspace verification reuse. Full workspace checks remain at entry and around writes and final publication. Full body verification stays at fresh import, writing bytes to user files, and final acceptance.
2. Reuse the notification snapshot architecture for ordinary Work view. Close immutable record reads before workspace and Git observation. Confirm the exact heads relating to the returned view and active generation afterward. Keep the other readonly screens unchanged and note the applicable design only.
3. Reuse fixed application schemas, load policy records once and avoid updating already published rows. Update read budgets and synthetic integrity checks.
4. Run matched Mac Phase A/Phase B measurements and both full Mac modes. Send only the final diff and bounded counters to Claude for a static result review. Apply supported findings and run focused checks. Repeat full regression if shared transaction or proof boundaries change.
5. Use the existing native x64 managed lane in a new synthetic slot, with exact inputs and existing protections, one ordinary work and one fresh eight-member group. Do not replay any preserved request. After the Mac full modes and review pass, the Owner authorizes a local Phase B commit. Record later Windows evidence in a separate local commit if required.

Final publication retains exact head CAS, closure, authority generation, store identity, fence and claims, with zero-or-all acceptance and existing refusals for wrong event, changed connection, replaced store and retired generation. No operation inherits trust from a different operation. Body bytes remain transient.

## Starting Windows evidence

The Phase A accept command spent 339.040 of 479.273 seconds in NTFS application and verification, with 5,057 of 7,026 guarded reads (72 percent). The stage ran 16 native move events, eight progress publications and 10,146 selection checks. The next acceptance cost was authorization and staging, 84.090 seconds and 1,637 reads. Reservation was 24.799 seconds with 27 reads and one write. Terminal publication was 11.744 seconds, 79 reads and one write.

Per-member preparation was the largest prior end-to-end cost: eight plans took 408.951 seconds and eight starts/submissions 823.987 seconds. Ordinary accept took 21.065 seconds, with 178 reads and one write. The normal managed exact-reference read averaged 37.039 ms, with 109 product-open attempts. Estimating 5,057 times that standalone rate gives 187 seconds, compared to 339 measured for the application phase. This indicates scale and leaves native writes, file observation, workspace verification and different reference cost unallocated. It is not a matched attribution or a reason to remove live checks. The stored evidence provides no per-function Windows split. No physical command was replayed for this analysis.

## Implementation decisions and checkpoints

The finished x64 and Phase A state was preserved on its own branch. This worktree starts at their second verified local commit. A separate private task-artifact directory retains the evidence and any runner or review input. Temporary test artifacts remain inside that approved task location.

### Implemented boundaries and assumptions

- Immutable record pages use up to 64 reads and 4 MiB per guarded transaction, with a 150 ms check between reads. An individually oversized existing record keeps its own transaction. The pure grouped checks and closure projections finish the page before native observation, normal mutable-head reads or any write. No group progress or terminal CAS was deferred. The existing guarded dependency walk uses pages and the final SQL transaction has the same dependency checks and only skips the requested no-op update of already published rows.
- Ordinary and grouped approval and ordinary start verify immutable descriptors and exact referenced chunk identity, actual length and published state without importing. Their proof sets are private to that publication and never satisfy a later full-hash validation. Plan, submit, ordinary accept and grouped application stay on full verification. When start consumes a Git ignore-policy value, an exact historical prefix of the newly observed policy supplies equivalent bytes without loading saved chunks. If the live input cannot establish that exact prefix, the existing verified-policy path decides the observation.
- Workspace reuse is confined to the middle of ordinary start and submit where a paired native observation already supplies exact topology. The live outer-marker checks, fresh locator and guarded authority root, local write counter and SQLite's external change flag must match. A mismatch returns to the original full check. Existing first and publication/application-boundary checks retain their full paths.
- Ordinary Work view uses one guarded historical record snapshot. The bound is 1,024 uncached reads, 8 MiB or 200 ms at a read boundary. Larger legitimate views use the existing per-read guard. File/approval-progress comparisons, pause comparison and live rework diagnostics begin only after the record snapshot closes. Guarded head and generation checks run before return. For lifecycle scans, the existing exact-root check remains. Other readonly views could adopt the same separation after an individual map of their immutable and live dependencies. No other screen was changed.
- Schemas are built once and their maps are read-only. Policy metadata is read and decoded once per use. The final transaction still checks identities and import claims for every required object. Already published rows avoid a redundant update.

The first 64 focused cases passed. The first additional focused pass found an invalid empty-policy test fixture. It was corrected to carry the required empty sources link. The corrected implementation and tests passed 58 focused cases covering the new boundaries, Work view and resume/attribution behavior. No product or environment safety rule was changed to clear a test.


## Matched Mac measurements

The same synthetic workload ran first on the accepted Phase A commit and then the fixed Phase B candidate. Timing is one sequential observation. Generated record IDs can vary per trial. Mac group preparation includes fresh plan, approval, submissions, candidate and file check. The replay belongs to each newly made Mac fixture.

| Scenario | Guarded read transactions A → B | Seconds A → B |
| --- | ---: | ---: |
| Ordinary approval, 3,000 files | 303 → 45 | 0.2847 → 0.3250 |
| Ordinary start, 3,000 files | 371 → 338 | 0.6303 → 0.6957 |
| Ordinary acceptance, 3,000 files | 471 → 192 | 0.7483 → 0.8412 |
| Ordinary read-only view, 3,000 files | 94 → 82 | 0.0316 → 0.0330 |
| 32 MiB approval | 112 → 41 | 0.0883 → 0.0248 |
| 32 MiB start | 180 → 82 | 0.1417 → 0.0683 |
| 32 MiB acceptance | 324 → 215 | 0.2342 → 0.2314 |
| Git-connected submission | 376 → 318 | 0.5025 → 0.4770 |
| Eight-member preparation | 27,385 → 24,303 | 30.9226 → 29.6248 |
| Eight-member apply before terminal publication | 9,531 → 7,397 | 14.1705 → 14.0146 |
| Eight-member terminal publication | 177 → 21 | 1.4220 → 1.4032 |
| New eight-member fixture replay | 7,574 → 146 | 5.9595 → 4.2543 |

Large-body approval and start each moved from 64 MiB of physical chunk loads to zero. Acceptance still loaded 112 MiB in both samples. Git submission retained 60 of its previous 63 process starts. All boundary checks, actual file verification and the saved exact-result replay remained enabled. Some short Mac durations increased despite fewer guarded reads. The Mac result makes no Windows runtime claim.


### First complete two-mode regression

The normal and parent-optimized macOS runs passed against the same source and test inventory. Each discovered 3,274 occurrences, with 2,746 complete passes, 526 skipped, two with a skipped subtest and no failures or errors. All 92 native partition cases passed in each mode. Skip identities and reasons match Phase A. The runs completed in about 73 minutes in parallel. Candidate production delta SHA-256 these runs qualify is `2c49b6dc5c305d56a99c222cc650a1bf83f3219c6b91a733680ba70fd000576a`. This is also the candidate supplied for the one independent static result review.


## One independent static result review

A fresh Claude Opus 5.5 session used the expected first-party subscription, with tools and execution disabled. Session b470f3f9-c399-4289-8684-6d0f60fb35aa. The supplied reviewed delta was the exact production source and bounded counter summary. Packet SHA-256 bb758c3a148e9e05d194ef8718641f69b88942e502a40d6ee4870630870c1e42. The original response is retained verbatim in private task evidence. No reviewer execution results are claimed.

- F1 revise. Descriptor-only commits explicitly refuse new body descriptors or imports. Incoming chunks already require staging. F9 defend. The group descriptor-only entry point is approval, while reservation, progress and finalization still hash full content.
- F2, F3 and F12 revise. Deferred lifecycle observation contributes only the since-pause comparison. Bind deferred result and rework inputs. When another operation changes the whole root, revalidate the relevant lifecycle record projection and all watched heads instead of rejecting an unrelated change. File comparison and live diagnostic behavior stay outside the short snapshot.
- F4 and F5 defend the page's explicit pure-record call sites and limited advisory time rule. The cap is enforced between reads. No page may span arbitrary sleeps, native effects or workspace and Git observation. Source audit confirms the workspace reservation guard reads only the sealed map, group plan, and effect state. The native eight-member regression proves actual observation, Git calls and effect callbacks run outside the open transaction.
- F6 and F7 revise. Observing another store or entering any fresh guarded transaction closes the active page on the synchronous thread before a second operation can start. Opening a snapshot also closes a previously active page. Each store owns an independent SQLite connection and shares a process lock when opening the same file.
- F8 revise and defend. The cache context now includes the exact store, workspace, root, qualified Git and locator reader, alongside the complete paired observed topology, actual locator, guarded authority root and write markers. Store constructors do not share SQLite connection objects, normal writers use the guarded transaction, and the native observation checks final topology itself. The existing raw locator access error path remains unchanged.
- F10 defend and add a regression. Descriptor proof sets are allocated inside their validator and never populate the operation's full-body set. A second publication in the same operation must make an actual chunk load for its full proof. F11 revise. Retained capture uses its original full body verification behavior.
- F13 clarify the distinct budget signal and strengthen the final snapshot bound. Snapshot fallback repeats pure record reads before native observation. Active generation is rechecked through the actual guarded transaction. Record memo never retains chunks. F14 defend. The fixed registry has no runtime settings lookup. Its application schema collections contain immutable role tags and frozensets.
- The two partial tests are existing retained earlier-profile runtime admission checks. Two and ten subcases respectively are skipped without that retained checkout. Their identities and reasons match Phase A.

Because the reviewed changes affect shared read transactions and proof boundaries, perform a second complete regression in both Mac modes after the focused guards and repeat the matched counters. No second Claude CLI invocation is authorized.


## Final matched Mac measurements after review

The exact native candidate now has patch SHA-256 b279cc476949ead009ad462459fb6db19c22e329423290ffa41ac15ddbfc6f5b. The repeat used the same sequential fixture against the Phase A commit and corrected candidate.

| Scenario | Guarded read transactions A → B | Seconds A → B |
| --- | ---: | ---: |
| Ordinary approval, 3,000 files | 303 → 45 | 0.3425 → 0.2810 |
| Ordinary start, 3,000 files | 371 → 338 | 0.7033 → 0.6616 |
| Ordinary acceptance, 3,000 files | 471 → 192 | 0.8160 → 0.7970 |
| Ordinary read-only view, 3,000 files | 94 → 82 | 0.0332 → 0.0324 |
| 32 MiB start | 180 → 82 | 0.1503 → 0.0677 |
| 32 MiB acceptance | 324 → 215 | 0.2417 → 0.2324 |
| Git-connected submission | 376 → 318 | 0.5121 → 0.4876 |
| Eight-member preparation | 27,384 → 24,327 | 31.4907 → 29.4919 |
| Eight-member apply before terminal publication | 9,257 → 7,378 | 14.1035 → 13.7777 |
| Eight-member terminal publication | 177 → 22 | 1.4190 → 1.3457 |
| New eight-member fixture replay | 6,427 → 128 | 5.4177 → 3.9168 |

The 32 MiB approval and start sample loads no persisted chunk bytes after the correction. Full acceptance is still 112 MiB of physical chunk loads in both builds. The final Mac replay compared identical result receipts and root within each new fixture, with no preserved request execution. Its measured SQLite object loads varied with generated records (6,430 → 7,648 in this run) while the transaction count dropped, which supports grouping reads rather than the removal of body verification.
The separate body call-stack pair shows nearly unchanged physical bytes in application and replay. Application across the run was 300,709 → 300,095 bytes and replay was 998,689 → 995,683 bytes. The body validation stream and actual consumer byte counts matched exactly in both phases. The remaining variation was attributed to closure traversal; across independent generated graphs the timing sample has additional variation. Terminal publication reloaded the same 13,279 bytes for actual consumers. These measurements answer the review’s byte attribution question without using the instrumented durations for the matched timing table.
Post-review focused regression passed all 24 cases. The fresh full two-mode regression is now running on this candidate.



### Verified source and local commit boundary

Final normal and parent-optimized macOS regressions passed on the same qualified source with 2,749 complete passes and zero failures or errors per mode. Each selected 3,277 occurrences, with 526 existing skips and two existing partial cases. The native partitions contributed 92 clear passes each. The focused regression and revised candidate were verified after the one result review. No new skips, drift or unresolved review blockers remained.

At 03:37:45 KST, the same designated native Windows host received the exact tested candidate for a fresh two-hour standard-user trial ending at 05:37:45 KST. The Phase B source commit is authorized now based on the full Mac modes and the result review. Native evidence arriving afterward is recorded separately. No delivery, public claim, release or Codex worker trial was started.


## Physical Windows x64 result and closure

Windows 11 native x64 standard-user testing used the existing managed CLI and protective lane with Python 3.14.7 and SQLite 3.50.4. Reported device hash checks passed for the patch, packet manifest and all 12 production files before and after application. The committed local source matches all 12 after hashes. Source commit 9c33c8198ee958b9fcde3fd6d99097a8e272f507. The initial handoff check found a mistyped manifest hash before child execution. Correcting that test input did not alter product or machine protections. No preserved request was replayed.

The ordinary path accepted one exact result with matching selected root, file ID and bytes. Its independent view used zero guarded writes. The verified pre-feature backup of the fresh planned root was present before the first group create. The existing protected file checker passed for eight files. Native readback confirmed 16 move observations, eight progress records, the exact eight submitted v1 IDs, NTFS identities and hashes, one 0-to-8 decision and no pending barrier. Previously qualified interruption and recovery inputs were retained and checked by hash.

| Same observation interval | Phase A | Phase B |
| --- | ---: | ---: |
| Ordinary managed acceptance | 21.065 s, 178 guarded reads | 19.597 s, 148 guarded reads |
| Eight-member accept CLI | 479.273 s, 7,026 guarded reads | 443.265 s, 5,673 guarded reads |
| NTFS application and verification | 339.040 s, 5,057 guarded reads | 301.492 s, 3,868 guarded reads |
| Terminal publication | 11.744 s, 79 guarded reads | 8.779 s, nine guarded reads |
| Eight individual plans | 408.951 s | 388.684 s |
| Eight individual starts and submissions | 823.987 s | 792.840 s |
| Managed independent read mean and Win32 open attempts | 37.039 ms, 109 opens | 38.869 ms, 109 opens |

The Phase B group took 1,941.554 seconds from setup through readback. The previous 2,273.807-second trial included a failed group attempt and backup correction. Treat those full-trial figures separately from the like-for-like command intervals. The independent read samples each used 128 reads per lane, with separate new stores and references between phases. A standalone managed lookup averaged about 39 ms in Phase B and the open count remains 109. The largest observed accept cost remains NTFS application and verification at about five minutes. Body bytes needed for output and final acceptance were still fully verified.

Final device readback finished 04:24:37 KST, before the 05:37:45 KST two-hour device bound. All 40 owned Jobs were inactive with both output streams at EOF and no timeout. Result index SHA-256 d289fd69e84b88e6bb0ddf04db4639e64b32155c6c27583d8a224d1676e76fa4. The reported native outcomes, exact group result IDs, guarded counters and digests were preserved in the private task evidence. A temporary host snapshot transport interruption recovered on the same actual trial. No second trial was sent.

The approved queue completed by 04:26 KST after about 228 elapsed minutes. Keep the Phase B worktree and exact tests/review/native evidence for Owner acceptance, integration and the next provider qualification. Keep the Phase A worktree as the matched comparison and both closeout commits. The original x64 worktree still holds one exact development-index version outside those commits plus generated bytecode. It remains available for reconciliation and is an archive candidate after that disposition. Preserve the separately recorded prior x64 interruption/recovery evidence regardless of worktree cleanup. Phase B result acceptance, push, PR, main merge, release and Codex coordination are pending Owner decisions.


## Owner acceptance and next measurement — 2026-11-25

The Owner accepted Phase B as recorded through cfa3b51, including the Windows file-based correctness result. Windows user-visible latency remains unresolved. The Owner authorized pushing the seven existing commits and this acceptance record on the existing topic branch and opening a draft pull request to main. Main integration and release remain separate decisions.

The next stage measures Windows runtime cost on the same native x64 lane with fresh synthetic inputs and process-local instrumentation. Use up to two hours on the device within the four-hour cumulative limit. The Owner will decide any runtime reuse, ancestor proof reuse or other trust-policy change after reviewing the measurements. Codex worker qualification follows the resulting shared-code change and its verification.
