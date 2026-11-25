# PATCH-20261125-003 — Windows command latency and observation efficiency

Status: Owner approved implementation. Baseline: `503a714`.

The round targets Windows x64 elapsed time through the native launcher. Measure ordinary plan, start, submit and accept, joint acceptance of eight submissions, and representative reads. The limits are 15 seconds per ordinary command and 180 seconds for joint acceptance. The experiment also covers a 3,000-file workspace and competing writers. Compare equivalent fresh synthetic requests and preserve previous evidence. Native allocations are capped at two hours each. The round stops after twelve hours.

## Owner decisions — 2026-11-25

- Combine Git child calls within one observation, retaining independent beginning and ending checks. Qualify submodule results, origin and precedence of Git settings, and Git for Windows home resolution without an inherited `HOME`.
- Reduce the cost of allocating a Windows file-state buffer while retaining its existing checks. Changes to parent-directory observation, path checks, or directory list reuse may proceed only when native safety probes support them. Test held-parent rename, delete and reparse transitions, replacement of child entries, and newly created Git and connection markers. Retain leaf guards and entry/exit checks. Keep the existing path for cases the proposed reuse cannot prove.
- Preserve Git Job termination, the output cap and EOF on both pipes for any change to process waiting. Separate executable verification time from pre/post state checks before considering same-process, handle-backed reuse. Measure Python bytecode loading on the same runtime and handle packaged bytecode as a separate change if justified.
- The Owner waived R0 for this round. The plan came from a Claude static code review, the driver checked it against source, and high-risk implementation is conditional on safety tests. Record a single static Claude R1 review on the entire fixed change.
- Run focused checks during development. When the candidate is fixed, begin the two-mode macOS regression and dispatch the exact Windows input in parallel. Keep Mac timing runs separate from regression. Repeat the full regression only if a subsequent change invalidates its coverage. Use the completed round as an anchor for later publication checks when its coverage remains applicable.
- Phase C was accepted separately and published to the existing draft review branch. Phase D Git changes stay local. Retain the protections for final publication, exact heads, concurrent writers and recovery.

## Managed entry paths

| Route | Retained inventory proof |
| --- | --- |
| Ordinary Work via product CLI | Eligible for one connected-store open |
| Group Work via product CLI | Eligible for one connected-store open |
| External initialization completion | Released before external initialization. Store opening verifies the runtime again. |
| Manager via product CLI | Released before forwarding |
| Native manager | Performs full startup validation with no retained product proof |
| Recovery manager | Uses the explicit recovery route and its own validation |
| Notification receiver | Uses the native manager route with receiver-specific validation and no retained product proof |

Tests of routing with Windows-shaped fixture ports cover the composition on macOS. Record actual Windows runtime evidence separately.

## Native baseline and selected changes

The native launcher plus the isolated x64 fixture measured 12.033 s (plan), 10.929 s (start), 15.652 s (submit), 9.530 s (accept), and 235.020 s (eight-member accept). The group was independently read back as zero to eight terminal decisions with exact effects and no pending barrier. That timing is for the accept command. The fixture's complete group journey took 1,014.950 s.

In the profiled 3,000-file plan, four full snapshots made 3,367, 6,368, 3,367, and 6,368 ancestor guard requests. Each pass observed 191 unique parent directories. Two simultaneous plans on that authority completed. Their maximum observed write transaction was 141.578 ms, with no store-busy result.

The native safety probe showed that an existing held parent could still be renamed, deleted when empty, and changed into a junction. A parent-only handle also permitted a same-name child replacement. The existing leaf guard and revalidation detected that replacement. The closing directory read refused additions at its entry bound. The selected-path check separately identified each new Git and connection marker. Parent and listing reuse remain pending. Separate Git-native timings attributed more of the measured adapter overhead to the pre/post file stamps than to executable hashing. Retain both guards.

The selected candidate batches the opening Git topology and exclude lookup, uses the ordered configuration to skip a redundant absent-value lookup, and uses Git's typed query for every explicit path and the independent closing checks. On Windows it reduces final-path buffer allocation with bounded fallback to the prior capacity, and wakes process polling on pipe completion while retaining the existing deadlines, guards and closure predicates.

## Fixed candidate results

The same native launcher and isolated x64 lane used new synthetic requests for this comparison.

| Command | Baseline, seconds | Candidate, seconds |
| --- | ---: | ---: |
| Plan | 12.033 | 12.516 |
| Start | 10.929 | 9.819 |
| Submit | 15.652 | 14.545 |
| Ordinary accept | 9.530 | 9.073 |
| View | 5.101 | 5.010 |
| Content | 4.299 | 4.163 |
| Project status | 8.529 | 7.915 |
| Eight-member accept | 235.020 | 244.079 |

The candidate passed the 15 s ordinary limits in this sample. The grouped result exceeded the 180 s limit. This pair does not establish a grouped speed improvement. The group completed its required file check, published exactly eight decisions from zero, and cleared the pending marker. Independent readback matched the eight submission references, native file identities and hashes. The harness confirmed no active Job members and EOF on both pipes. The synthetic slot did not contain installed guides. The large workspace and additional native diagnostics were measured only at baseline or remained unavailable.

Claude R1 flagged a risk that Colvia's initial interpretation of a configured exclusion path could disagree with Git. The fixed candidate delegates every explicit value to pinned Git, preserves the old independent capture when the combined output cannot fit, and signals process waiting only when a pipe worker completes or reports an error. One static review covered the first fixed diff. Focused tests passed after applying the dispositions.

The revised macOS passes reconciled both parent modes with 3,304 discovered occurrences per mode. Each had 2,776 executed passes, 526 wholly skipped occurrences and two partially skipped occurrences. There were no new skips. Both full runs initially reported one error in the same new Git test because the intentionally scrubbed runner provided no HOME. A synthetic HOME corrected only that fixture. The one affected test passed in each original sandbox and mode. The other test and product bytes matched their inputs, and the native patch bytes remained identical.

The operating system and account types remain limited to the observed evidence. Full publication checks and supported-package qualification are separate.

## Owner result acceptance — 2026-11-25

The Owner accepted the exact local candidate `48e5d86` with candidate 2, S1 buffer-only and S9 retained. The 180-second eight-member goal remains unmet. The 9.059-second difference in one paired run does not establish a stable change. S12, S10, verification cadence, resident execution, the 200-Work fixture and the Windows bytecode comparison remain deferred. The Owner held the PR branch update because the draft PR and this commit diverged. [Phase E](CHORE-20261125-004-windows-workspace-observation-design.md#frozen-input-and-integration-comparison) records the read-only integration comparison and owns the separate large-workspace study.
