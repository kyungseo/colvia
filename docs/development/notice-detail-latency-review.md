# Windows notification detail latency — plan review

Baseline: public source 863de45a1c663c83eb59201dee1b3ff2a08bf9d9. This is a proposed bounded correction. Review the plan only. Identify necessary revisions and a minimal falsifiable acceptance test. No tools or execution.

## User-visible boundary

A Windows notification arrives promptly and remains available in Notification Center. Selecting it opens the detail window. The delay under review is from the visible loading message until the correct readable Work title and submitted summary appear. Track activation-to-window separately. A brief console flash is a separate observation. Use a submitted Work with a known title/summary, verify the visible text, not just the time to paint a placeholder or finish a subprocess.

## Proposed change

1. Keep the trusted launcher, receiver identity, routing and event ownership checks. Reuse the manager entry's verified runtime only within this one detail request, only for the same runtime home and exact active selection, with appropriate locking, revalidation and bounded lifetime. Never share evidence across processes or commands. Check whether reuse preserves the tamper-detection and update/uninstall guarantees under concurrent changes; if it cannot, keep the redundant verification and evaluate the record-reading improvement independently.
2. Read the records needed to verify the event and render its submitted title/summary from one coherent, explicitly read-only snapshot. Preserve object digest checks, project/instance/generation and receiver binding, capability checks and stale/retired-store refusal. Do not expose a long-lived global cache, nest transactions on the same SQLite handle, or hold a database transaction or runtime lock over slow live project filesystem work. Preserve preexisting write transaction behavior. Inspect duplicated traversal of Notices.event. Keep original submitted facts separate from current workspace state. If splitting rendering becomes necessary, publish only the verified original details first, then label refreshed state explicitly and reject out-of-order or wrong-event responses.
3. Keep result acceptance explicit. No banner delivery changes. Moving a folder, console startup, or an unrelated Git integration failure is not part of this correction.

## Evidence and acceptance

Compare a baseline and candidate on the same Windows ARM64 VM, same Windows account, Work and event, and same registration/cache conditions. Record the displayed-loading to displayed-title-and-summary interval, separately the pre-window wait and backend phase timings. Use monotonic timestamps, record only elapsed times and boolean correctness. Do not log user content or opaque identifiers. Distinguish old moved-folder/unavailable cases from an actually connected case. An installed-module benchmark alone cannot qualify GUI responsiveness. First target: two seconds or less from visible loading to readable title and summary on the retained small connected fixture. Report each cold/warm sample separately and label the target unmet or unverified if appropriate. ARM64 timing does not qualify x64 timing.

Focused regression cases: valid/corrupt/foreign event, correct original result and current status, file drift and missing connection, changed runtime or authority generation, updates concurrent with read, retired store, write refusal, no receipt or acceptance on click, bounded database/lease lifetime and no changes to the ordinary write path. Preserve previous evidence for unrelated delivery, installation and Git features.

Report any specific blocker to achieving these semantics with the smallest code change, particularly where performance improvements would weaken an existing guard. No release or Git publication is requested.


## Independent static plan review · 2026-11-21

The Owner authorized one tool-free plan review of the first 3,784 bytes of this file, SHA-256 `f7a1505f5486cf19d127db72b7049d68e145b475376ee44c4c9a08047c805c93`. Model `claude-opus-5-5`, fresh session `8d5245c0-569f-467e-8c02-cca3ed259e4f`. The reviewer received the plan only. The reviewer did not inspect code, run the application or receive device logs.

### Verbatim final response

# Plan review: Windows notification detail latency

## Verdict

**Approve with revisions.** The scope and guard preservation are sound. As written, though, the plan can't fail cleanly: it doesn't require profiling before changing code, step 1 may be a no-op, and the acceptance target has no sample count or baseline condition.

## Concrete risks

1. **No profiling gate.** Both changes are proposed before any phase breakdown shows where the time goes. If most of the latency is subprocess or console startup (the console flash hints at this), neither change will hit 2 s. The plan would then pressure someone to weaken guards to close the gap.
2. **Step 1 may be empty or unsafe.**
   - If a detail request spans more than one process, "never share across processes" means there is nothing to reuse. Step 1 then does nothing.
   - If it is one process, reusing earlier verification creates a time-of-check/time-of-use gap. An update or uninstall between verify and use would run unverified code.
   - "Revalidation" is undefined. If it means re-hashing, the reuse saves nothing.
3. **Snapshot semantics are under-specified.**
   - A SQLite read snapshot exists only inside an explicit read transaction. Separate autocommit reads are not coherent.
   - `mode=ro` or `query_only` does not prevent WAL/shm interaction. `immutable=1` would break concurrent-update detection and must be forbidden.
   - A long-lived reader blocks WAL checkpoints. Lifetime must be bounded by code structure, not by convention.
4. **Stale and retired checks must run inside the same snapshot** as the event read. Otherwise a retirement that commits between the check and the read is missed.
5. **Split rendering adds new failure modes**: races, wrong-event display, and stale labels. Treat it as out of scope unless the profile shows it is required.
6. **The acceptance target is weak.**
   - "≤2 s" with unspecified samples can pass on one lucky warm run.
   - If the baseline is already ≤2 s on this fixture, the test cannot tell baseline from candidate.
   - Instrumentation inside the app can shift timings.
   - "Cold" is undefined.

## Required changes

1. **Add phase 0: instrumented baseline only.** Record per-phase monotonic durations: activation→window, window→loading, launcher/verification, each subprocess spawn, DB open, each query, filesystem/live-state reads, and render. Proceed with a step only if its phase accounts for a material share, for example ≥25% of loading→readable.
2. **Make step 1 conditional.** First state whether one detail request is one process.
   - If it is not, drop step 1.
   - If it is, reuse is allowed only when bound to an open, held file identity (handle plus size/mtime/file ID re-check at use). It must be scoped to a single call stack, never stored in module or global state.
   - If identity binding isn't possible on Windows for this runtime layout, keep full verification and record that as the blocker.
3. **Specify the snapshot exactly.**
   - One connection, opened read-only.
   - One `BEGIN` (deferred) read transaction containing: event lookup, digest check, binding/capability/generation checks, and retired-store check.
   - Close the transaction before any live-filesystem or Git/workspace call.
   - No nesting, and no reuse of a write connection.
   - Add an assertion or test that the transaction is closed before the live-state phase.
4. **Fix the order of operations.** Render the original submitted facts from the snapshot. Read current workspace state afterwards and label it separately. Do not split the response unless phase data requires it.
5. **Define the measurement harness.**
   - Use external UI Automation polling of the detail window text, not in-app logging.
   - t0 = loading text first observed; t1 = expected title and summary both observed.
   - The harness compares against values it holds and logs only a boolean match.
   - Fix the polling interval (≤50 ms) and report it.
6. **Define the sample conditions.**
   - **Cold:** after reboot, or after killing all app processes and waiting a fixed time.
   - **Warm:** immediate repeat.
   - **Samples:** at least 5 cold and 10 warm per build, each reported individually, with median and max.

## Minimal falsifiable acceptance test

Use the same ARM64 VM, account, connected fixture Work and event for both builds.

1. **Baseline must reproduce the problem.** Its warm median for loading→readable must be >2 s. If it isn't, label the result "not discriminating" and stop.
2. **Candidate timing and correctness.**
   - Warm median ≤2 s, with every sample individually reported.
   - 100% of samples show the correct title and summary (boolean).
   - Report cold samples separately. Label the cold target met or unmet; do not average it away.
3. **Guard checks on the candidate.** Each must show refusal and no title/summary displayed:
   - A runtime file modified after the request starts, before use. This specifically tests step 1 reuse.
   - A corrupt event.
   - A foreign event.
   - A retired store, retired concurrently between notification and click.
   - A generation bump.
4. **Concurrency.** Writer commits during the read: the result shows either the full pre-commit or full post-commit snapshot, never a mix. The writer is not blocked beyond a fixed bound, and a WAL checkpoint completes after the request.
5. **No side effects of clicking.**
   - No receipt or acceptance is written on click.
   - The ordinary write-path tests are unchanged and pass.
   - Existing delivery, installation and Git evidence is retained and unchanged.
6. **Scope labels.** Results are ARM64-only; mark x64 as unverified. Report moved-folder and unavailable cases separately from the connected case.

## Likely blocker to report

If the profile shows that latency is dominated by spawning separate verified subprocesses per command, it cannot be fixed under these rules:

- Merging those subprocesses into one process is the console/launcher change that was excluded.
- Sharing verification evidence across those processes is forbidden.

In that case, report "target unmet within scope" rather than weakening verification.

### Driver dispositions and revised execution proposal

1. **accept** — Establish a connected, installed GUI baseline before changing product code. Use the existing backend phase profile to select investigations. Measure activation to window separately, then the visible loading state to correct title and submitted summary; do not attribute the console flash to a process without evidence.
2. **accept** — Trace process and lock boundaries first. Reuse verification only within one request with held identity and update/uninstall exclusion sufficient to preserve the current guarantee. File timestamps or path equality alone cannot establish integrity. If equivalent protection cannot be demonstrated, retain verification and assess the read path independently.
3. **accept** — Use an explicitly bounded, read-only transaction for related records, checking event, digest, ownership and available database generation/retirement information coherently. Validate externally held authority according to its existing lock and generation contract. Release the reader before live workspace I/O. Exercise concurrent updates and checkpoint completion. Keep the write path intact.
4. **accept** — Keep submitted facts and current workspace state distinguishable. Keep a single rendered response for this correction. If the profile warrants a second rendering phase, report the need before expanding scope.
5. **accept** — Measure both builds externally with identical UI polling at up to 50 ms intervals. Only mark the end when both expected fields are readable. Record timings and boolean matches. Report a missed loading transition as interval-censored, never as zero. Include time to readable from activation so delaying the loading indicator cannot hide a regression.
6. **revise** — Use fresh application processes after a fixed idle interval as process-cold samples; document VM and filesystem cache conditions. Use five process-cold and ten warm samples per build for final comparison, individually with median and maximum. Stop early if the connected baseline does not reproduce the delay. Target a warm median of at most two seconds, with the correct Work on every sample. Report process-cold timing and any slow tail distinctly. The existing x64 observation and the disconnected fixture are separate evidence.
7. **accept** — Check corrupt/foreign events, retirement, generation change, concurrent update and click without a recorded user decision. Measure the effect of the smallest safe change. Stop and report if the target would require a cross-process cache, weakened verification or a new launcher architecture.

The Owner approved the static review. Implementation and result review are pending Owner authorization.

On 2026-11-21 the Owner authorized the [execution record](PATCH-20261121-001-windows-notice-detail-latency.md) and the isolated ARM64 scope above.
