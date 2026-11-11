# Partial first-install quarantine and explicit replacement

Status: Owner approved this source extension and two further static review calls
on 2026-11-07. The slice has a six-hour elapsed cap within the existing cumulative
100-hour source limit and 6,000-second review-wait limit. Actual installation and
the other held actions remain excluded.

Owner: [record-foundation Work](../FEAT-20261106-002-record-foundation.md).
Basis: [recovery result and preserved counterexample](recovery-extension-result.md).
The existing recovery result and original failed attempts are not rewritten.

## Purpose and boundary

A first attempt may publish native aliases or receiver files before selecting its
runtime. If its authentication expires and the server replaces the target, exact
resume, metadata renewal and the current retry path all refuse. There is no prior
runtime to restore. Add one explicit path: inspect the exact attempt, retire its
forward authority, retain its generated files in quarantine, then prepare a new
signed attempt using the existing trust state.

Only a recognized initial home, current initial-attempt chain and valid prepared
release are eligible. Require no runtime selection, completion or project
authority; refuse malformed, moved/copied, foreign or ambiguous homes. Preserve
home identity, configuration, trust anchor/root history, learned version/time
floors, slots, original preparations, failure records and quarantined bytes.
Neither expired execution nor a bootstrap anchor reset is permitted. Verification
of historical ownership is not permission to execute the old payload.

No installed host is changed by this source task. Recovery of already active
installations, project data migration and OS registration repair are excluded.
The existing four worker/execution/import/host holds remain unchanged.

## Contract to implement

1. Preview identifies the latest attempt and exact eligible files, with a receipt
   bound to preparation, home identity, inventory and observed file identities.
   It does not download, move files or clear a pending marker.
2. Revalidate under the management exclusion and the relevant native effect
   locks. Fix lock ordering consistently with existing recovery. A stale preview,
   changed ancestor, replaced file, unexpected hardlink/symlink/reparse point,
   additional directory entry or foreign pending operation refuses before effects.
3. Before the first move, persist a one-way quarantine intent that blocks every
   old forward route, including claimed start, resume, renewal and publication.
   No new installation may begin while quarantine is incomplete. Record the
   single replacement relationship without permitting forks or orphan authority.
4. Move only explicitly owned generated paths, retaining originals with native
   no-replace, same-volume semantics. Reuse current retained-file and publication
   ports. Do not recursively delete or move the whole management home. A whole
   generated subtree is eligible only when its exhaustive inventory and identity
   are proven; unknown content stops it. Preserve displaced descriptions and
   pending-marker bytes as evidence, not as live authority for another attempt.
5. Persist progress before relying on a move, then verify destination identity,
   bytes/mode and durability. After interruption, classify actual source and
   destination states. Resume the same operation only when unambiguous; changed,
   missing or multiply present objects never trigger a blind repeat or cleanup.
6. Complete only after every selected file and barrier is accounted for and live
   installation paths meet the existing retry preconditions. Keep a permanent old
   attempt barrier even when transient markers have been removed from live paths.
   Retrying completion must not touch files belonging to a later attempt.
7. Start a uniquely linked new attempt using the retained Trust and unchanged
   origin/channel. Fresh signed target preparation may choose the current target;
   learned floors may advance, never reset. Download failure leaves a new failed
   attempt with explicit recovery, not an automatic download loop. A verified
   bootstrap provides this path while no managed runtime is selected.

Normal user flow: one preview and one confirmation may authorize quarantine plus
one new preparation. Internal receipts stay in tool output. A stopped operation
reports what remains and the exact next action. It does not claim installation
success before runtime selection and completion have been verified.

## Exact ownership and registration constraints

The eligible surface is the two fixed native aliases, their generated entry
record, optional packaged receiver files and description, and pending markers
bound to this exact initial attempt. Authenticated slots, trust/configuration and
operation history stay in place. Foreign native-update or receiver-registration
state is not swept into the list.

Current first-install aliases are checked by bytes but do not have individual
publication identity receipts. Add durable publication intent/receipts using the
existing effect machinery before treating those identities as proven. Cover the
interruption between file publication and receipt completion. Do not fabricate
historical receipts for old trial files; an older ambiguous attempt remains
preserved and unavailable for automatic quarantine. Reproduce the known failure
with the corrected publisher to verify the complete future public path.

The installer publishes receiver files but never registers or launches them.
Require no managed notification choice/registration/pending-registration evidence
and no conflicting known receiver registration. Absence of local markers is not
proof of global OS registration absence. Do not run the expired receiver to check
registration, unregister an app or expand into OS-wide diagnostics. If a required
platform ownership fact cannot be established, refuse and retain the state;
actual installed-platform confirmation remains a separate qualification stage.

## Implementation slices

| Slice | Main source surface | Result |
| --- | --- | --- |
| Ownership and barrier | updates/installation.py, initial_home.py, reauthentication.py; small dedicated quarantine module | Exact initial publication ownership, permanent retirement and one replacement chain |
| Retained moves and recovery | Existing platform file/effect ports, only narrowly necessary additions | Exhaustive paths, no-replace moves, crash classification and exact resume |
| Entry and explanation | Verified bootstrap routing/generation, presentation, paired foundation-preview manuals | Preview, confirmed quarantine/replacement, state and bounded next-action guidance |
| Evidence and disposition | Focused foundation tests and this Work | Preserved counterexample, positive recovery evidence, review findings and limits |

This does not change Work acceptance, record format, backup policy or the runtime
trust model. No new general cleanup engine or installation subsystem is proposed.

## Smallest sufficient checks

- Preserve the existing retired-target refusal result; add the positive sequence:
  partial first publication, expiry, changed signed target, quarantine, fresh
  preparation, selection and completion. Assert retained old evidence and trust
  floors across both operations; use fixed signed fixtures without generating keys.
- Interrupt before/after intent, each move, completion and replacement-link
  publication. Check exact resume, lost acknowledgement and old-forward refusal.
- Race two callers; change runtime selection, authority presence, home/parent/file
  identity, bytes, modes, extra files and pending ownership between preview/apply.
  Verify zero unrelated file mutation and no replacement-chain fork.
- Reject missing/corrupt publication evidence, altered quarantine content, copied
  home, foreign notification state, cross-volume paths, Windows sharing failures
  and indeterminate moves. Retain all first failures. Permission/native failures
  do not cause automatic retries or host changes.
- Cover alias-only and partially published receiver cases, missing descriptions,
  empty generated directories, later attempts and failures during new download.
- Check verified-bootstrap argument routing, no network during inspection/moves,
  unchanged bootstrap trust anchor behavior and readable paired instructions.
- Run focused initial-home/install/renewal/native-file/rollback/trust/routing suites
  after related changes are consolidated. Reuse the unaffected 822-test checkpoint
  and later 112-test evidence; do not add overlapping counts. Broaden checks only
  for a changed risk or concrete unresolved finding.

All effects occur in durable task-owned synthetic fixtures with inert payloads.
macOS local file tests and Windows API doubles remain distinct from actual
installation and native Windows qualification. No model behavior sessions are
needed. Do not modify test inputs while a run is active.

## Estimate, review and stop limits

Expected: 3–5 active hours for contract completion, implementation, focused checks,
review corrections and documentation; allow up to 20 additional minutes of static
review waiting when serial. This is engineering judgment, not a measured runtime
promise. It assumes reuse of existing effect ports, fixed signed fixtures and the
focused runner. New native ownership limitations are the main uncertainty.

Proposed slice stop limit: 6 elapsed hours including reviews, charged within the
existing cumulative 100-hour source limit, not added to it. Prior consumption and
failures carry forward. Contract/plan review comes before code; result review
comes after focused checks; correct in-scope findings and rerun affected checks.

Owner approved two further fresh static Claude CLI calls, at most 600 seconds each,
using the existing Claude Pro subscription and tool-free review. Limit packets
to this contract, relevant changed code/dependency excerpts and synthetic results;
exclude credentials, personal paths, original private trial logs and comparison
identities. Record authentication/billing route, input identity/drift, verbatim
findings and Driver dispositions. No behavior/host sessions are added.

The prior explicit transmission consent was for a particular result packet, not
an unlimited disclosure grant. Owner approved the bounded rounds and then the exact plan and result packets
for the Claude.ai subscription destination. If automatic review still
requires approval of concrete bytes, prepare the exact minimal packet first and
request that approval; do not use another channel to bypass a rejection.

Stop at either bound, unresolved ownership/unknown outcome, required OS mutation,
new contract scope or unavailable authentication. No automatic failed reviewer or
native-run retry. Ordinary source/test corrections stay in the approved slice;
required additional rounds or platform actions are reported separately.

Actual installation, host permission expansion, key generation, notifications,
product commits and publication remain prohibited. This source slice executes quarantine only on inert synthetic fixtures; it
does not install anything on a user or VM installation. Public qualification and Owner result acceptance
remain separate from passing source checks.


## Plan review disposition and implemented source boundary

The fresh tool-free plan review completed in 237.217 seconds with unchanged inputs.
Its six blocking observations were static inferences, not executed failures.

- B1: one permanent quarantine intent reserves the successor; the existing retry
  edge remains the only chain. Old forward routes and premature retry refuse.
- B2: first installation now stages every generated node before recording native
  identities and publishing with no-replace moves. Matching foreign bytes are not
  adopted. Ambiguous old trials without publication evidence remain preserved.
- B3: included the narrowly necessary owned-file port and initial publisher.
  Receiver contents reuse the existing signed candidate definition; first-install
  descriptions and directories are published through the new receipt path. Update
  replacement remains on its existing effect path. No new subsystem is introduced.
- B4: all foreign pending/registration paths refuse before retirement. Quarantine
  moves files individually into flat private names; it removes only verified empty
  generated directories, deepest first. It never moves a whole live subtree.
- B5: terminal completion returns its recorded outcome without revisiting successor
  paths. Interrupted successor metadata resumes only the reserved exact claim.
- B6: eligibility is offline inventory/receipt verification. It never activates the
  expired target. Network construction follows completion and the unique edge.

The local workflow does not establish absence of global LaunchServices state.
It does not execute an expired receiver to probe that state or change registration.
First-install/resume/retry/renewal suites are rerun as affected, not inherited as
unchanged evidence. One result review remains within the two-call approval; no
third review or failed-review retry is implied. The exact plan packet transmission
was approved separately after the automatic-review refusal, both preserved privately.
