# P3 result review — Driver disposition

Status: authorized source corrections and focused verification, not Owner acceptance or installed qualification.

The [verbatim reviewer response](review-p3-work.md) came from one fresh Claude CLI session, model `claude-opus-5-5`, through the previously approved subscription path. The 20 supplied source/test inputs did not drift during review. The call completed in 312.29 seconds within the Owner-authorized 360-second bound. The reviewer had no tools and executed nothing. This was the final reserved review call; no extra review or model trial was added.

The existing private review packet records the base revision, tracked diff digest, untracked input digests, exact request and actual session identity. It is retained for acceptance and follow-on integration review; it does not become public provenance or a second progress tracker.

## Findings

| Finding | Disposition | Correction / evidence |
| --- | --- | --- |
| 1. Approved ignored path cannot be submitted | accept, with scope clarification | Explicit scope joins the protected observation set at plan/start/submit/recheck and policy validation. Existing unrelated ignored paths remain outside observation. Registered workspace/container and opaque boundaries still refuse scope traversal before publishing a plan. The ignored new file counterexample failed before and passes after correction. |
| 2. Current-file failure hides stored review and receipt | accept | Review returns retained result plus unavailable current state and the exact receipt. Acceptance still refuses unavailable/mismatching files. Rework remains possible; CLI historical reads no longer eagerly require the current folder to exist. Directory replacement and moved-folder cases are covered. |
| 3. Another workspace replaces a planned Work | accept | Plan replacement requires a valid current head owned by that workspace, even with a computable receipt. Read-only retained result/content may be inspected from another workspace; writes and acceptance remain bound to the result workspace. Both refusal and read-only behavior are checked. |
| 4. Dirty submodule blocks ordinary observation; malformed Git parsing | defend dirty-state boundary, accept diagnostics/parsing | The approved opaque contract deliberately refuses dirty/changed/nested submodules rather than certifying hidden contents. It does not remove the repository's changes. Added a concise state-check message and exact ls-tree field-count validation; existing dirty/ignore/placeholder checks remain applicable. Dirty-submodule coexistence is not silently added. |
| 5. Map collapse returns unreachable temporary nodes | accept | Return only new nodes reachable from the resulting map root. A 17→16-key collapse demonstrated the surplus empty node before the correction. Canonical rebuild/update properties and store consumers still pass. |
| 6. Duplicate acceptance after archive reports stale; duplicate archive writes | accept | Follow the bounded same-decision chain back to its reviewed head; verify that receipt and result. Repeated identical archive is a no-op. No new acceptance is written. |
| 7. Managed path aliases can enter a plan | accept | Validate canonical, distinct scope before staging and compare reserved components with casefold. `.GIT/config` refuses before a plan is recorded. |
| 8. Two simultaneously edited Works collide | defend serial scope protection | Separate Work state is supported; simultaneous edits of one workspace and automatic baseline reconciliation remain deferred. An outside-scope refusal now explains that another Work may be involved and preserves the current result for a new baseline/Work. It does not guess ownership or exempt another Work's edits. |
| 9. CLI failure/duplicate input/unknown outcome handling | accept, bounded | Validate scope before staging; convert invalid arguments to a stable failure. Unexpected errors are outcome-unknown, never assumed rollback, and name the operation for inspection. A read-only operation query lets the agent inspect a recorded result without retrying. Internal tracebacks are not normal human output. |

## Executed evidence and limits

- The first counterexample run reproduced five applicable product/behavior failures; two Git cases initially hit a test-fixture inheritance error. That runner failure is preserved and is not a product reproduction.
- After fixing only the fixture, the ignored-file submission and cross-workspace plan replacement failures were reproduced separately.
- The first correction run found a missing local scope variable in the start callback. This source regression was corrected; its failed output remains separate from the final pass.
- Focused corrected suites cover all reproduced cases, retained bodies through rework/archive/export, ordinary CLI restart, scope escape, changed result, pagination and opaque protection. The owning Work records final cumulative/optimized counts.
- The reviewer did not read every dependency and did not independently execute tests. Corrected source was checked by the Driver within the approved scope; it was not sent for an unapproved extra review.

No actual installation, host configuration, keys, notification, product commit or publication occurred. Codex desktop access remains a separate failed probe with no automatic retry. P4–P9 feature/lifecycle integration and actual platform/host qualification remain required.
