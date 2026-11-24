# Read-path efficiency follow-up

Status: P1 candidate. Phase A scope and time limit approved with a native x64 prerequisite. Assign a development record ID when the execution plan is approved. Recorded on 2026-11-24 from a static source review and macOS ARM64 synthetic measurements against source revision `9fbe2a5`.

Ownership: the [joint acceptance task](FEAT-20261122-002-multi-submission-acceptance.md) owns the eight-member finalization correction and its Windows timing. [Windows notification detail latency](PATCH-20261121-001-windows-notice-detail-latency.md) owns reuse of a verified runtime between calls. This note owns the remaining read-path candidates below.

## Owner planning authorization — 2026-11-24

The Owner authorized registering this P1 candidate and approved the scope and 28-hour cumulative limit for Phase A, starting after native x64 joint acceptance verification. The working estimate is 13–24 elapsed hours. It includes device waiting and excludes waiting for Owner decisions. Changes to the shared code make the main steps sequential. Assign a development record ID and type when the plan is selected for execution. A PATCH is the likely type.

The Owner chose reuse of verified immutable objects within one operation. A new operation starts with a fresh validation scope. Plan the shared mechanism in R2. The currently verified grouped publication uses one validation callback and remains the x64 task's implementation pending that plan.

The Owner chose to preserve existing per-read guards for read-only screens in Phase A. Evaluate whether the existing notification-detail pattern also fits other read-only screens. Read the required records and reuse the result only inside one short guarded transaction, retain the entry and exit checks, and close the transaction before any workspace or Git check. This is a design review. Any adoption of the alternative requires a separate decision after Phase A evidence. The [notification route](../../src/colvia/notice_routes.py) already isolates historical records in a read-only snapshot, closes it before constructing the live workspace or Git reader, and checks the route and root again before returning current details. For a new screen, identify its immutable record portion and define the post-live freshness checks before proposing any change.

Registration base `9fbe2a530b181bbb6d6cc5c8a909d69edb433899`. The working-tree change adds this English candidate note and one New Source Candidates index entry. The index SHA-256 is `3b0fd503dca7d3a17f90b0f565b2d1fe051de83f84c25b82049ca453f479fd3f` before and `7ea2980f8080766f627b6c5724d27e83d6776b44369782a41f09297de4cc3151` after. The bounded registration-only index diff SHA-256 is `44217ab49183783d1a2f3fc7b955c8d483be21c49812a1782ea4c852f1142920`. Git commit, push and PR require separate Owner decisions.

## Why this exists

A logical store read loads one immutable object inside its own guarded transaction. Validators then read and hash the same immutable objects again within one command. Total cost is the read count multiplied by the guard cost of one read.

The joint acceptance correction removed one repetition: eight-member finalization fell from 106,040 to 17,710 reads. An isolated prototype and the integrated macOS grouped publication both reached 621 reads for 155 unique objects by reusing bytes inside one validation call. The joint acceptance task owns the native x64 timing evidence. Ordinary Work, read-only views and large files still follow the same pattern.

R1 and R2 are P1 because guarded reads affect ordinary Windows commands as well as grouped acceptance. The macOS counts below establish demand for a native measurement of the per-read cost.

## Observed evidence

All rows are synthetic source measurements on macOS ARM64 unless marked otherwise. The private task evidence retains the counting scripts and raw logs.

| Path | Observation |
| --- | --- |
| Ordinary acceptance, 3,000-file plain workspace, one scoped file | 1,845 logical reads for at most 277 unique objects. Full-tree reads account for 1,028; the workspace tree was read four times. Closure validation accounts for 558 and connection checks for 199. |
| Phase totals, same workspace | approve 840, start 1,225, submit 923, accept 1,845–2,099 reads. Counts grow with workspace size. |
| Read-only Work view | 129 guarded transactions. The same three connection records account for 56 of 66 object reads. |
| One 32 MiB scoped file | approve and start each re-read 96 MiB of body chunks; submit re-reads 176 MiB and accept 192 MiB. |
| Git-connected workspace | `LocalWorkspace.verify()` runs 1–11 times per command. Git processes per command: plan 54, submit 63, accept 21, view 6. |
| Eight-member finalization residual (joint acceptance task) | 16,084 reads of 154 objects: 167 KB distinct, 16.4 MB re-read. The single project binding record was read 1,271 times. |
| Write transactions | About 5 ms each with the required DELETE journal and full synchronization, 1–10 per command. Not a bottleneck in these runs. |

Source cost model: in an installed store, one guarded transaction performs 13 ancestor-checked file accesses. These are the runtime lock, four lease checks (each an uninstall-marker check and a runtime-selection read), two store identity checks and two active-pointer reads. The Windows file port opens every ancestor directory on each access. At an assumed path depth of eight, one logical read implies about 120 `CreateFileW` calls. The [physical x64 read-cost measurement](FEAT-20261122-002-multi-submission-acceptance.md#physical-x64-guarded-read-cost) subsequently found mean 47.078 ms and 140 product Win32 opens per managed read, compared with 19.116 ms and 50 opens for the source-only control. This establishes the scale of guarded reading on the measured device. Exact attribution within the earlier reservation timeout remains open.

## Candidates

### R1. Guard cost per read on installed stores (Windows first)

- `RuntimeLease.hold()` keeps the shared runtime lock for the whole transaction, but the store guard repeats `RuntimeLease.check()` twice more inside it, and `hold()` checks again on exit. If every writer of the runtime selection and the uninstall marker holds the exclusive runtime lock, these repeats add no information. Confirm this for every writer, including bootstrap paths, before removing them.
- Read immutable objects for validation through one bounded guarded transaction. Notification detail already reads related records in one short guarded transaction; follow that precedent.
- Keep every guard in the final publication transaction unchanged.

### R2. Operation-scoped reuse of verified objects

- Provide one shared mechanism at the storage/validation boundary, not a cache specific to grouped acceptance.
- Metadata objects: reuse verified bytes within one operation, with a byte bound.
- Body chunks: remember that a chunk was verified in this operation without retaining its bytes, unless the consumer needs the bytes.
- Expected removals: repeated baseline tree and body-map reads across `WorkService._validate_head()` and `_validate_result()`; the full canonical rebuild on every `read_tree()` and `read_map()` call; reloading and re-inspecting a node when `validate_closure()` revisits it at a greater depth.

### R3. Body re-verification policy

- Every head publication currently re-hashes all scoped bodies. Approve and start re-hash bodies that plan already verified.
- Decide which commands require chunk-level verification and which may rely on descriptor-level checks plus the publication guard. This is an integrity policy and needs an Owner decision.

### R4. Connection verification

- Resolve the connection once per `verify()`. A single call currently resolves the connection identity about six times through `Connections.workspace()`, `binding()`, `identity()` and `registrations()`.
- Within one command, reuse a topology observation only when it is keyed by every input that affects its meaning, and invalidate it on any connection change. Keep the before/after checks the Owner selects as full checks. Reference A, an external comparison implementation, shares identical in-flight worktree scans and advances a generation on mutation, so no caller receives a pre-mutation result.

### R5. Read-budget regression checks

- Add counting checks for ordinary acceptance, a read-only view, one large file and eight-member finalization. Measure logical reads against unique objects, chunk bytes against scoped bytes, guarded transactions per view, and Git processes per command.
- Reference A bounds its work counters in scale tests, for example keeping list reads proportional to the input count. Without such checks, the 106,040-read regression passed functional tests.

### R6. Lineage walk in `operation_result()` (later)

- Confirming an older recorded operation walks every later root, with two guarded reads per step. The cost grows with history length.
- Reference A treats an index row as a candidate that the caller validates. Colvia would still need a cheap proof that the candidate belongs to the current lineage. This needs a record-format decision and has lower priority.

### Minor

- `application_registry()` rebuilds its 83 schemas on every call, including per-object call sites.
- `decode_policy()` reads the same policy object twice.
- The publication transaction issues `UPDATE ... published=1` for objects that are already published.

## Invariants to preserve

- The final publication transaction keeps its checks of store identity, generation, fence and quiescence, capabilities, exact head CAS, and published/claim state.
- No reuse outlives its operation or crosses processes. No SQL projection becomes authority.
- Refusals stay unchanged for a replaced store, a retired generation, a changed connection and a wrong event. Same-request replay and zero-or-N acceptance stay unchanged.
- Corrupted stored bytes are still detected, at least on first read within an operation. Later commands follow the R3 decision.

## Owner decisions

1. Reuse scope. The Owner approved one operation.
2. Read-only views. The Owner kept per-read guards for Phase A and requested the short-transaction design review recorded above.
3. Body re-verification policy (R3).
4. Which `verify()` checks remain full checks (R4).
5. Order relative to verified-runtime reuse in PATCH-20261121-001.

## Proposed phasing

Phase A comes first. Start it after the joint acceptance task closes its native x64 qualification, because both change the storage core. Decisions 1 and 2, this scope and the 28-hour cumulative limit are recorded above.

1. Reuse the [read-only native x64 measurement](FEAT-20261122-002-multi-submission-acceptance.md#physical-x64-guarded-read-cost) brought forward by the Owner. It timed 256 `store.load()` calls per route on the same references and counted opens separately. Neither route replayed a preserved request. A fresh baseline is needed only if the device, storage entry or guard changes make this sample inapplicable.
2. R2 operation-scoped reuse as one shared mechanism.
3. R1 lease-check deduplication, after confirming the writer lock rule.
4. R4 single connection resolution per `verify()`, with the same checks.
5. R5 read-budget regression checks.
6. Full regression in both modes, static review, and a native x64 recheck of ordinary commands and eight-member acceptance.

Expected elapsed time is 13–24 hours. Review the short read-only transaction design during planning. Keep existing read-only guards throughout Phase A.

Phase B follows the Phase A measurements and the remaining Owner decisions:

- R1 batched guarded validation reads, if Windows reads still dominate after Phase A
- R3 body re-verification policy
- Reducing `verify()` before/after checks
- Verified-runtime reuse, owned by PATCH-20261121-001
- R6

Expected effect of Phase A, by inference and not yet measured on Windows:

- Eight-member acceptance: from tens of minutes to seconds or tens of seconds.
- Ordinary acceptance on a 3,000-file workspace: a few seconds.
- Notification detail: largely unchanged, because its two full runtime verifications take most of its time.

## Out of scope

- Changing the journal mode. Measured write cost is small, and the store requires the DELETE journal.
- Record format changes, except a separately approved R6 decision.
- Candidate reconstruction in grouped finalization, which the joint acceptance task owns.
