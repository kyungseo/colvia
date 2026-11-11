# Explicit installation and interrupted-update recovery

Owner approved this source extension on 2026-11-07, within the existing 100 active
hours and 6,000 seconds of total review waiting. Two further static CLI calls
(plan/result), at most 600 seconds each, are authorized. No actual installation,
privilege/configuration changes, keys, notices, product Git mutation or host/model
behavior retry is included. Estimated 4–8 active hours remains a judgment.

## 1. Publish initialized home only after local preparation

Build a new, private, same-parent initialization directory containing ManagerHome,
updates.json, a bootstrap-identity/initial-attempt marker and fully initialized
Trust. Trust initialization verifies the pinned anchor locally; it performs no
metadata refresh or target download. Publish that directory to the final absent
home with a native no-replace same-volume directory move. Verify the same native
directory identity before/after and sync the parent. Keep an interrupted staging
directory; never recursively delete or overwrite an existing destination. Failure
before publication leaves no claimed live home; failure after publication is
recognized by the exact initialization marker and complete trusted state.

Existing unknown/old partial homes without that marker are not adopted or reset.
First public compatibility has not been activated, and no old trial migration is
promised. A valid existing runtime always uses its existing trusted manager.

Explicit retry of a recognized initial attempt is allowed only before any runtime,
project authority, native alias, receiver description or live-file pending marker
exists. Verify home/platform, initialization identity, origin/channel/target and
retained trust anchor. Keep learned counters and clocks. Use a new operation area
and a durable retry link to the prior attempt before preparing anything. A download
or staging failure never reuses partial bytes or loops. A prepared initial install
uses exact resume, not retry. Publish native entries atomically as already fixed.

## 2. Reauthenticate only the already prepared target

An explicit refresh command binds the original operation and review receipt. Under
management exclusion, refresh the existing TUF state and compare target path,
length, SHA-256 and the complete custom descriptor with the original download.
Advance learned trusted counters even if a changed target is then refused. Never
import another anchor, lower counters, tolerate clock rollback or fetch the target
body for this refresh. Persist a new immutable renewal receipt; original release
and failure evidence remain unchanged. Explicit resume may name this renewal;
activation checks the fresh cached signatures and exact original runtime target.
Renewal after runtime selection may finish only that target's pending description.

## 3. Restore exact originals while the old runtime remains selected

A separate rollback preview/apply path verifies the original runtime selection
byte-for-byte and its complete slot inventory. It takes management and exclusive
runtime leases. It does not change runtime.json, project records, settings, trust
state/counters or their histories. It is not a downgrade or an expiry bypass.

Resolve only native/app pending markers belonging to that exact release. Read each
original effect state under its native lock. Refuse changed retained originals,
unknown paths, foreign files or replaced ancestors. For pre-state files, no effect
is needed. For post/evacuated state, construct a reverse retained-original effect
from the observed state to the authenticated old bytes (or absence if there was
no old app file). The old slot inventory plus the saved before-description must
agree with those bytes. Store an explicit rollback intent and fully prepared
reverse effect manifest before its first live effect. A reverse effect may be
resumed using the same ownership/identity checks; it retains displaced new bytes.
Interrupted reverse staging creates no live changes and remains evidence.

Keep the forward barriers until every reverse file and description is checked,
then record rollback completion before clearing those exact markers. An unfinished
rollback prohibits forward refresh/resume. An already completed rollback prohibits
reuse of the original update receipt. A later update needs fresh preparation.
If the old runtime is corrupt or has already been replaced, this rollback refuses;
use authenticated runtime repair or exact forward completion as applicable.

The verifier can be a still-working manager or an explicitly verified bootstrap
runtime when an alias is missing. Bootstrap recovery never executes an unverified
payload or imports its root into an existing installation. User messages name the
needed next action; machine receipts stay in tool output.

## Focused validation

- Interrupt every local initialization step and publication boundary; retry must
  preserve staged evidence and never claim an unrelated destination.
- Initial download failure, cancellation and incomplete archive: explicit new
  attempt retains old artifacts/counters. Reject a prepared or active home retry.
- Fixed signed metadata reauthentication: same target accepted, changed hash,
  size/custom/path, version rollback, expiry and backward clock refused. No target
  fetch on renewal and no newly generated signing keys.
- Native aliases and app files: pre/post/evacuated reverse states, lost completion
  acknowledgement, foreign bytes/identity/ancestor, changed retained originals,
  old selection mismatch, expired metadata, interruption during reverse effect.
- No rollback writes to records/settings/trust or runtime selection; no forward
  resumption after rollback intent. Managed/bootstrap command routing is explicit.
- Reuse the 822-test cumulative source checkpoint and focused later corrections;
  rerun only affected trust/install/update/native-file tests unless new evidence
  shows broader risk. Windows API doubles remain separate from native qualification.

Remaining earlier policy/host holds are unchanged. Product result acceptance and
release qualification are still separate Owner decisions.

## Plan-review disposition and implementation boundary

The authorized fresh static plan review found three high-priority gaps and five
medium concerns. Adopted: create the initial operation/intent before publication;
renew a first installation using the prepared-record digest; bind renewal to the
original operation/receipt and use its effective descriptor in every guard; check
the permanent rollback barrier inside activation exclusion; advance trust floors
before missing/oversized target refusal; publish one retry-chain edge under the
management lock; retain reverse staging attempts and resume only published reverse
manifests; classify uncertain home publication without another rename attempt.

Rollback takes management, runtime, then effect locks. It requires the original
selection and complete old slot, verifies retained originals independently of
already reversed live paths, and never calls the new target expiry check. An
already selected newer runtime uses forward completion, not this rollback.
Runtime selection is one atomic pointer in this implementation; no separate
runtime pending pointer is adopted or cleared. No held policy/host lane reopens.

Implemented source paths now include initialized-home no-replace publication,
explicit initial retry, same-target metadata renewal, first-install renewal,
rollback preview/application/resume, managed commands and verified-bootstrap
fallback. API doubles do not qualify native Windows behavior. Fixed signed input
checks verify existing signatures and counter/clock handling; no signing key or
real update service was created. The release endpoint expiry-rollover journey and
native installed paths remain qualification work.

## Result-review refinement

See [result and disposition](recovery-extension-result.md). Prepared initial
attempts with no live installation files can now be explicitly superseded; the old
attempt cannot resume. Already selected runtimes can finish matching receipts
without fresh target authentication. Initial partial publication plus expired and
retired target remains an explicit blocker, not an implied successful recovery.
