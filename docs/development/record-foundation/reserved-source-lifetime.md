# Reserved application source lifetime

Status: Owner accepted the completed source result on 2026-11-07. Plan/result reviews and focused source checks completed. Not installed qualification.

## Accepted boundary

An ordinary Work acceptance still verifies current result-file agreement. This
change applies only to the separate, explicitly approved worker apply-and-accept
operation. Preparing a preview is not reservation or acceptance.

Before reservation, validate the exact source result and, for a result still in
review, live source-file agreement. Validate source and destination registrations,
authorization/grant, destination baseline,
manifest and retained bodies. Publish the immutable authorization, manifest and
pending effect atomically under the existing CAS validation and effect lock.
For a result still in review, that pending effect binds the verified source
agreement for the named result. An already accepted result retains its prior
decision and can already use retained content without requiring current source
bytes to match; this existing behavior is unchanged.

After reservation, source-folder removal or later source-file edits do not change
the approved result. Continue only from its retained bodies. At every effect and
terminal publication retain the exact source head, registration heads, live grant,
pending selection and destination native/content checks, except cancellation,
which retains its existing exact-preimage/no-evacuated-original checks instead of
full destination topology observation. Store project/instance/
generation identity is checked at service construction; public project/registration
mutations are frozen by the pending-effect guard. These are not new per-effect
project-head comparisons or a mid-effect revocation API.
Do not infer consent to a newer result, apply later source edits, or accept an
unknown destination. Missing/corrupt retained bodies still refuse.

Acceptance is recorded only when the exact destination postimage and dependency
checks pass. Completing the worker effect, source acceptance and pending removal
remain atomic. Already accepted results retain their original decision. Cancel
remains possible only with verified current preimages and no evacuated originals;
it never accepts a result. No force cleanup or automatic rollback is introduced.

This is the first-public, not-yet-activated schema. Existing private trial runtime
migration is outside scope; no new record field is needed if the existing reserved
effect fully binds the evidence above. New public changes must respect the first
activated compatibility baseline.

## Implementation and evidence selection

Keep source filesystem validation at prepare, preview and reservation. Separate
post-reservation dependency validation from those initial checks. Keep ordinary
accept unchanged. Update source and user guidance to explain the reservation
boundary rather than claiming the source checkout is always required.

Reuse the recorded removed-source counterexample. Add focused assertions for
changed/missing source before reservation; after-reservation removal/edit;
changed record/registration/grant; retained-body corruption; multi-file partial
application, cancellation and source CLI re-entry after removal. Reuse unaffected
storage, ordinary acceptance and no-replace effect evidence. Run affected worker,
composition and CLI families once after related corrections.

## Limits

Expected 2–4 active hours plus at most 15 minutes reviewer wait; elapsed stop limit
6 hours within the existing 100-hour source allowance. Two fresh tool-free Claude
reviews, each at most 450 seconds, within the unchanged 6,000-second cumulative
review allowance. No extra behavior-model session, failed native-lane retry,
installation, host privilege change, key generation, notification, commit or
publication. The two stopped execution lanes receive only bounded read-only
inspection of existing evidence; unfinished-effect imports remain inspection-only.

## Plan review disposition

A fresh tool-free Claude plan review completed in 186.932 seconds with no input
drift. It reproduced nothing. Driver accepted the side-specific validation split:
`_live(source=False)` suppresses only source root/content checks after reservation;
destination validation remains. Cancellation retains its existing preimage/native
checks and does not acquire new workspace-verification requirements.

The existing storage-only helpers were read: `_baseline`, `_head_record`,
`_validate_head` and the direct-child `validate_transition` do not require a live
source checkout. LocalWorkspace construction is lazy; source CLI constructs its
Authority from explicit authority/project inputs, not from the removed root.
The focused CLI test still supplies a fixture Authority/Git: it verifies dispatch,
constructor arguments and destination locator use, not a real installed bootstrap.
A composition-member removal test covers the review-to-completed transition.

The initial pending worker effect is created by `execute` only, with source
agreement in its reservation validation for a result still in review. `_next` links subsequent states to it.
Low-level GenerationStore is a trusted storage primitive, not an authenticated
product command; arbitrary developer-created stores cannot be assigned human
approval provenance by shape alone. Public restore activation refuses a candidate with the project-wide pending-effect
head. A test supplies a real reserved effect to that gate. A dangling historical
pending application without that global head is not excluded by this one gate,
but cannot resume or cancel: those operations require both heads to match.
No private-trial import or repair path is newly authorized to create a reservation.

Guard-refusal tests for registration/grant changes reuse their existing assertions.
New injected-head cases are defense-in-depth tests, not claims that those mutations
are available to users during a pending application. Both staged post bytes and a
reachable stored record receive corruption checks. Preflight refusal is distinct
from refusal after staging: the latter preserves prepared files for diagnosis.

Removal tolerance applies only while destination topology, policy and opaque
context remain valid. Removing a primary checkout that contains the destination's
common Git directory can correctly block completion. The tested deletion is a
separate linked source worktree; no shared Git data is deleted by the product.

## Executed source checkpoint

The affected selection passed 103 tests in 188.774 seconds with no input drift.
It covers the new 12-case reservation suite and existing worker, correction,
recovery, composition, command entry, pending barrier and restore-manager families.
The two old post-reservation refusal oracles were changed only at the approved
semantic boundary. Earlier failure evidence remains private and unchanged.

The new CLI case mocks Authority/Git but asserts the exact explicit authority and
project arguments, then executes dispatch and checks the retained authorization
on the final decision. It does not prove a managed installed entry works from a
deleted source folder. The imported-effect case exercises the real pending-effect
activation gate against a real reserved effect; it is not a full archive roundtrip.
The injected-head cases prove defensive rejection without exposing an API that
can change grant/registration during pending. Actual native/behavior failed lanes
were not rerun. No installation or permission changes occurred.

## Static result review disposition

The fresh tool-free result review completed in 175.145 seconds with no input drift.
It found no blocking correctness defect in the approved boundary. This is static
review, not an executed guarantee; the Driver dispositions are below.

| Finding | Disposition |
| --- | --- |
| Source-agreement wording overgeneralized | Qualified the contract/comment: initial current-file agreement applies to a source still in review. Previously accepted results keep their existing retained-result behavior. |
| Cancellation exception omitted in summary | State the existing exact-preimage path explicitly; no full destination topology requirement is added to cancellation. |
| Restore gate overstatement | Narrowed to the global pending-effect head. Historical orphan state is not claimed absent; resume/cancel require matching global/application heads. No unbounded restore scan is added. |
| Completion-time dependency tests missing | Add injection only after `before-completion` for source registration, live grant and destination verification. Installed bytes do not imply acceptance: pending remains and the source stays in review. |
| CLI wording too broad | Assert the explicit Git constructor and observe destination locator reads as well as Authority arguments. This is still dispatch evidence with supplied Authority/Git fixtures, not installed execution. |
| Plain folder deletion leaves stale Git metadata | Add a synthetic folder-loss case that leaves Git metadata intact. Stale/prunable membership refuses and preserves the partial application. Source removal tolerance requires valid destination Git topology, including its worktree list; the successful case removes the worktree through Git. |
| Broad corruption refusal assertions | Pin the staged-file and stored-object mismatch codes; retain that the stored-object test injects a loader fault, not physical database damage. Pin pre-reservation source loss to its observed filesystem refusal. |
| Pre-reservation staging residue recovery | Reuse the existing conflict test and concise error guidance: inspect the request; if no reservation occurred, prepare a new application identifier while keeping the old stage. Do not automatically reuse or delete it. |
| Paired user guidance absent from review input | Driver aligned both languages to the reviewed contract and local Git topology limit, then rendered the changed documents. No independent prose review is claimed. |

No further reviewer or model behavior session is needed for these bounded
corrections: runtime behavior did not change after result review, only its comment,
claims and focused tests. Existing 103-test source evidence remains applicable;
the new/strengthened cases receive their own recorded run. These counts overlap.

## Final source verification

The result-review correction run executed 14 cases in 42.574 seconds. Thirteen
passed; the terminal registration case refused safely with the earlier
`workspace-location-index-mismatch` guard rather than the expected later
`worker-connection-changed`. The original failure remains preserved. Only that
expected code was corrected. The terminal test, covering registration, live grant
and destination checks in three subcases, then passed in 9.598 seconds with no
input drift. No runtime behavior changed after the independent result review.

Together with the unaffected 103-case checkpoint, these runs cover the final
changed behavior. Counts overlap and are not summed. No full suite was repeated:
ordinary acceptance, storage and unaffected lifecycle evidence remain reusable.
The stale Git-membership refusal is intentional, not a claim that arbitrary
source-folder deletion can always complete. Actual installed entry and stopped
host/model lanes remain unqualified and were not retried.

Both review rounds, their exact input packets, original refusals and focused test
logs remain in private durable evidence. Current source/manual changes remain
uncommitted; no actual installation, permission change, key generation, notification
or publication occurred.
