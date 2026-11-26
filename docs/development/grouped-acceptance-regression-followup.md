# Retained Regression Follow-up After Multi-Submission Acceptance

## Owner Decision And Sequence

On 2026-11-22 the Owner accepted the two-submission implementation in [FEAT-20261122-001](FEAT-20261122-001-grouped-acceptance.md) and authorized its local commit. The eight existing findings below remain separate follow-up work; their deferral is explicit, not a passing result. The Owner requested a plan before implementing support for three or more submissions, then completion of these eight findings after that extension. This note records the selected sequence; it does not approve an unwritten extension plan, release, push or new runtime support.

The subsequently approved extension is owned by [FEAT-20261122-002](FEAT-20261122-002-multi-submission-acceptance.md). Revisit any finding immediately if the extension changes or relies on that exact behavior, or if evidence exposes an integrity defect. Do not postpone a required extension safety check merely because it is in this list. The later follow-up should continue from these exact IDs and original failure evidence, not rediscover a new list.

## Eight Findings And Closure Conditions

All eight original failures reproduced on unchanged base main `be19fb1362ca057eaad2d4af218ea9f89cc06adb`. Causes below are source assessments unless explicitly described as executed. At the original deferral, none had passed a corrected focused execution. The closure below records the later corrected runs; this original failure assessment remains historical evidence. Original private execution logs remain retained by the owning task.

| Prior ID | Exact test | Assessment and required follow-up | Closure evidence |
| --- | --- | --- | --- |
| 1 | `test_foundation_execution_processes.ProcessPortTests.test_replaced_stream_is_not_closed_as_an_owned_pipe` | The port closes its retained owned pipes, not a replacement stream; the test expects refusal. Settle the intended cleanup contract before changing the oracle. The group check runner uses a separate subprocess path. | Normal and parent-optimized ownership/replacement/cleanup tests; prove foreign streams stay untouched and owned resources are safely closed or recoverable under the chosen contract. Broaden if runtime behavior changes. |
| 4 | `test_foundation_platform_imports.PlatformImportTests.test_worker_effects_use_native_windows_port_and_refuse_unknown_hosts` | Expected factory call omits the current `native_entries=False` keyword. | Correct the call expectation; preserve Windows selection and unsupported-platform refusal assertions in both modes. This does not qualify native Windows. |
| 5 | `test_foundation_native_execution.NativeExecutionTests.test_read_write_and_three_verifiers_retain_result_without_accepting_work` | Executed baseline diagnostic shows the local Python needs an external gettext dynamic library denied by the existing worker sandbox. Group checks do not use this runner. | Diagnose the exact runtime dependency and choose a qualified contained runtime or narrowly justified resource binding; preserve sandbox denial boundaries. Run the actual read/write/three-verifier and no-acceptance checks in both modes. Never turn a skip or broad sandbox permission into a pass. Required before claiming this worker/runtime combination supported. |
| 7 | `test_foundation_review.ReviewTests.test_readonly_error_classification_uses_sqlite_code_not_journal_presence` | Synthetic exception supplies only the name; production classification checks matching name and numeric code. | Supply real matching SQLite codes, retain rollback/moved-file distinctions, and verify malformed or inconsistent metadata remains generic in both modes. |
| 8 | `test_foundation_submission_boundary.BoundaryCLITests.test_current_location_mismatch_does_not_claim_automatic_reconnection` | Assertion expects old prose; present guidance still refuses and preserves files. | Check current meaningful refusal/preservation/no-automatic-reconnection content in both modes without requiring obsolete wording. |
| 9 | `test_foundation_windows_plain_location.WindowsPlainRecordedLookupTests.test_recorded_workspace_lookup_and_local_verify_preserve_exact_heads` | Fixture patches absent `workspace.discover`; current code uses the connection-boundary topology helper. | Patch the actual boundary and retain exact heads, registration and index-preservation assertions in both modes. Do not describe this mock test as native Windows validation. |
| 10 | `test_foundation_work_integrity.IntegrityTests.test_candidate_page_refuses_mid_page_head_change` | Fixture callback lacks the current `display` keyword; this is ordinary planning-candidate pagination, not a group integration candidate. | Preserve the injected mid-page head change and exact `list-changed` refusal in both modes. |
| 11 | `test_windows_native.PortableNativeTests.test_source_profile_cannot_relabel_common_source` | Legacy command omits required `--source`, so argument parsing ends before the intended refusal. | Supply the explicit prepared source, retain profile-mismatch refusal and unchanged target assertions, both modes. |

## Evidence Selection And Completion

Correct related fixtures together, then run the affected cases and shared consumers in normal and parent-optimized modes. Reuse unchanged evidence from the accepted two-submission implementation and the eventual extension anchor, identifying their exact revisions and limits. If runtime, writer, acceptance or recovery behavior changes, apply Maintaining's corresponding full-regression requirements. Preserve old failures separately from corrected results.

For each row record the actual cause, change, exact execution result and any remaining limit. Completion means the required behavior is exercised successfully, or the Owner explicitly accepts a concrete alternative disposition; a static explanation, unavailable test, or renamed skip alone is not closure. Final result acceptance and any additional commit/publication remain separate Owner decisions.


<a id="closure-after-the-2-8-extension"></a>
## Closure After The 2–8 Extension

After the Owner approved the 2–8 extension and its review closed the implementation findings, all eight test-only corrections were executed. Production worker/process/sandbox behavior was unchanged. Each original exact test above passed in normal and parent-optimized focused runs and in the complete consolidated regression. No case was skipped to obtain closure; existing whole-suite skip identities and reasons remain unchanged. Final Owner acceptance and Git publication are still separate decisions.

| Prior ID | Corrected contract and observed result |
| --- | --- |
| 1 | Live admission refuses replaced public streams. Cleanup closes the retained owned pipes while leaving the foreign replacement untouched; the real child is stopped and reaped. Additional signal-denial coverage preserves unclosed/pending state and refuses another launch. |
| 4 | Match the current native_entries keyword, prove both true/false propagation, and retain unknown-host refusal. Portable selection checks do not qualify native Windows. |
| 5 | Supply an exact contained child runtime to the synthetic fixture. Actual read/write and three verifiers complete with Work still active. Outside read/write, write through the read-only profile and network remain denied. Parent CPython 3.14.7 is unchanged; the contained child is 3.14.10, not an installed-runtime qualification. |
| 7 | Supply matching numeric/name SQLite metadata. Missing, inconsistent, boolean and unknown metadata still get the generic error; rollback/moved-file distinctions remain. |
| 8 | Assert current meaningful refusal, preservation and explicit original-folder/move confirmation without the obsolete prose. No automatic reconnection is claimed. |
| 9 | Patch the current connection-boundary topology helper, assert the exact call and unchanged heads/registration/index. This remains a portable fixture. |
| 10 | Forward the display keyword; the same injected mid-page head change still produces list-changed. |
| 11 | Supply the explicit prepared source so the intended profile mismatch reaches exit 65; the target stays empty. |

Focused coverage was 28 ordinary cases plus the native five-operation case in each mode. Complete-run counts, exact runtime boundaries, review disposition and acceptance state belong to [the extension record](FEAT-20261122-002-multi-submission-acceptance.md#final-whole-regression-results). The private original failing logs and exact corrected execution ledgers remain available to the Owner for result review; corrected results do not erase the historical failures.


## Owner Acceptance — 2026-11-23

The Owner accepted the macOS result, including all eight corrections and their stated runtime/portable limits, and authorized a local commit. These eight findings are closed. Push, installation and Windows group qualification remain separate; the extension record owns the remaining Windows planning.
