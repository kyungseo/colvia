# P9 final source review and disposition

Status: corrections tested at source level; not accepted or release-ready.
Reviewer: fresh Claude Opus 5.5 CLI, static, tools disabled, existing subscription
path. Thirty-two inputs remained unchanged during the 537.719-second call.
The private packet identity, verbatim response and failed runs are retained.
The reviewer reproduced no counterexample. Driver checks below are separate.

## Corrections and remaining gates

| Finding | Driver disposition | Evidence / remaining boundary |
| --- | --- | --- |
| H1: receiver bundle feature order | Corrected to canonical sorted features. Generated macOS receiver and both Windows architecture bundles now pass payload/slot staging checks. | Inert binaries and metadata validation; not native execution. |
| H2: first installation interrupted before prepared.json | Confirmed open recovery gap. Keep partial home and trusted counters; never treat it as a fresh installation or erase it. | Explicit retry/recovery policy below remains an Owner decision. Failed perform now reports its operation. Failures before trust preparation may have no operation yet. |
| H3: expired verification during partial native/app replacement | Confirmed open recovery gap. Expiry and backward-clock checks still refuse; retained originals and pending markers remain. | No freshness bypass or automatic retry. A review of explicit reauthentication/rollback is required before release. |
| M1: Git gate created before ownership acknowledgement | Preserve fail-closed behavior; distinguish an unrecorded lock and explain that it must not be deleted or followed by another commit. | Exact lock identity and pending state remain intact in the interruption test. General automatic orphan-lock reclamation is not implemented. |
| M2: evacuated Windows index | Keep the existing retained-original transition. Guide now warns against deleting index.lock or making a commit during pending recovery. | Exact recovery passes the API-double test. A gap-free replacement redesign is not silently adopted. |
| M3: Windows DELETE-held gate reopened by guard | Corrected: the exact mover owns source identity/bytes validation; its guard checks other locks and live authority without reopening that source. | A sharing-sensitive guard double passes. Windows native sharing remains unqualified. |
| M4: release status/receipt not reachable | Added release-level inspection, exact receipt, activation attempt identities and operation on failure. No fetch or state change during inspection. | Managed status, failure JSON and release/child status tests pass. |
| M5: authenticated repair lacks resume | Added explicit bootstrap repair-resume, retaining the same prepared target and replacement flag. No new stage/download call during resume. | Manager routing, shell validation, Windows template and synthetic interrupted repair tests. Expiry still blocks under H3. |
| M6: unpublished native/app staging area wedges resume | A pending marker selects one exact preparation area. If no marker exists and live preimages still match, a fresh named area preserves the interrupted staging area. | Native update and initial receiver preparation fixtures preserve orphan bytes and complete. No live pending area is abandoned. |
| M7: registry entries outlive deleted home metadata | Added read-only registration inspection without adopting or deleting foreign/unconfirmed entries. | Registry-double test verifies zero writes. Cleanup of such entries needs an exact separate action. |
| M8: project pending effect blocks home update | Keep current global capability/backup barrier. Imported unfinished candidates cannot activate: RestoreManager._target rejects their pending effect. | The review's imported-active-state example is not admitted by current code. An actual active pending effect still blocks update; narrowing that scope is not adopted. |
| M9: guide claims | Paired guide now distinguishes declared-capability checking from executing workflows; states recovery gaps, local filesystem boundary, Windows same-volume/hook conditions and receiver reconnection. | Source guide, not installed qualification. |
| Low: recovery ref flush | Added before publishing recovered index. | Existing interruption/recovery tests pass. |
| Low: partially published initial/native-notice executable | Switched final executable publication from direct stream creation to atomic no-replace file creation, with executable mode set before POSIX publication. | Injected short-write fixture leaves only staged partial bytes and no final executable. Native Windows behavior remains separate. |
| Low: audit memo duplicate key | No change: normal validated graph traversal excludes duplicate insertion. No reproduced reachable counterexample was supplied. | Existing audit integrity/memo tests reused. |
| Low: ACL/COM trust boundary | A private index may retain same-account ACLs. The receiver's self-check detects accidental changes within the cooperative single-account model; it is not a defense against a malicious owner of that executable. | Cross-account Git service workflows and hostile same-account binaries are not claimed. |

## Driver usability correction

A project launcher now exposes the manager bound to the same verified runtime.
Management help/status need no Work store; callers cannot supply another home or
runtime identity through this route. `delivery notify` resolves the verified
project and uses the one-shot receiver composition. The adapter explains the
prepared-delivery sequence, so an agent need not read implementation files or
invent JSON to request a result notification. No OS emission was used in these
tests. This post-review guide revision has not been exercised in another model
session; the six-session budget is exhausted.

## Verification selection

The earlier cumulative source run remains 822 passing tests across 104 modules.
It predates these corrections and is not relabeled as their final verification.
The first targeted correction run executed 95 tests: 93 passed, one new diagnostic
missed a RecordError import, and one lock-refusal assertion still expected the
old generic code. Both original failures remain preserved. The corrected target
selection passed 77 tests in 88.312 seconds with no input drift. The refined
bootstrap/manager entry selection also passed. These suites overlap; do not add
their counts as distinct coverage. Platform doubles do not qualify installed
macOS/Windows, desktop permission behavior or actual notification clicks.

The narrower checks were selected because changes affect bundle metadata,
retained preparation, manager routing, executable publication and Git recovery.
Unchanged store/work/graph semantics reuse the earlier cumulative result. No
second complete run is justified by a new digest alone. New policy-dependent
recovery code must receive its own crash/failure tests and review.

## Required continuation decisions

Recommended policy for review, not implemented here:

1. In a recognized partial first installation, an explicit recovery action may
   continue authenticated preparation with retained trust/counters and all prior
   attempts preserved. Never overwrite unknown home contents or infer a fresh
   installation from a missing runtime pointer. Establish initialization ownership
   and recover every pre-preparation interruption before exposing this command.
2. For interrupted native/app replacement, allow explicit fresh signed
   reauthentication only for the same target bytes and descriptor. Do not lower
   trust counters or bypass backward-clock checks. If the old runtime remains
   selected, also provide a separately reviewed rollback of the exact retained
   original entry/app files; external edits refuse. This must restore usable old
   launchers without rolling back records, settings or trust.
3. Keep the three earlier policy/execution holds and the Codex writer diagnosis
   separate. No host setting, native execution retry or extra behavior session
   follows from source recovery authorization.

The ten-call static-review allocation is consumed. A proposed recovery correction
and focused result review need two further calls, at most 600 seconds each, within
the unchanged 6,000-second total review-wait cap and 100-active-hour source cap.
No further reviewer is invoked without that extension. Source recovery work is
estimated at 4–8 active hours including crash tests and review disposition; this
is a judgment estimate, not measured completion or a new overall cap. Actual
installation, privilege changes, keys, notifications, product commits and public
release remain held.
