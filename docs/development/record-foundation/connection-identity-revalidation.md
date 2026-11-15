# Persistent connection identity and explicit legacy revalidation

Status: Owner accepted design and authorized the bounded source correction, 2026-11-13. Source implementation and focused checks are recorded below. Installed application remains a separate decision. The source checkpoint is `a4b4f4416c650e546c0b4796889604e226dc6b61`. The [owning record](../FEAT-20261106-002-record-foundation.md) retains progress. This is a proposed narrow amendment to [C1](implementation-contracts.md#c1--project-identity-location-and-access), not an activated format contract.

## Problem and evidence boundary

An installed macOS connection preview stopped while validating an existing independent project's root, before deciding whether the new target overlapped. Six existing live registrations had unchanged recorded/current inode numbers but different device numbers. No connection apply or representative Work began. The cause of the device-number change is unconfirmed. The executed evidence is from the installed runtime; source comparison confirms the same relevant connection/observation logic, not a separate source reproduction.

`platforms/posix.py:identity` uses `(st_dev, st_ino)` for both persistent locations and immediate observation stamps. `connection_boundary.py:_ancestor_ids` rejects a stored root when those values differ. Ignoring that failure or comparing only path/inode would weaken overlap protection. The same stored identities also occur in workspace registrations, location indexes, integration ownership and Work observations.

Existing recovery is insufficient for this case. `Connections.rebind_restored` requires a restored instance with `needs_rebind`; it is not a live-store identity refresh. `ProjectSetup.detach_context` itself requires matching location identity. Neither is a safe bypass. Historical objects and failed attempts remain intact.

## Recommended boundary

Keep one logical project and its existing history. Separate persistent connection identity from operation-local file identity. For legacy records, add an explicit, scoped identity revalidation decision rather than replacing old object bytes or resetting Work baselines.

Do not add general relocation, clone adoption, automatic baseline refresh, distributed synchronization or a filesystem-wide registration catalog. Windows keeps its existing volume/file/creation identity provider. Linux and unqualified filesystems are not added to the supported matrix by this change.

### Persistent and operation-local identity

| Use | Required identity and behavior |
| --- | --- |
| New macOS root/common-dir/gitdir registrations and persisted observation locations | Versioned filesystem UUID plus directory file ID and creation identity; preserve path spelling and existing alias policy. A proposed encoded scheme is `darwin-volume-uuid-v1:<uuid>` with a versioned inode/birth-time file component. Keep the existing three-field NativeLocation container; explicitly validate the new scheme. |
| An open operation, snapshot stamps, entry pruning and effect/file guards | Keep current descriptor/handle checks, raw device/inode and existing stamp fields. Recheck around observation and use. A persistent-ID match must not waive an operation-local replacement or remount discrepancy. |
| Existing decimal-device macOS records | Classify as legacy. No automatic equivalence to a new UUID and no device-wide replacement table. Use the exact revalidation decision described below. |
| Existing Windows records | Preserve existing semantics and serialized values. Shared comparison changes must not loosen case, reparse, hardlink or creation-identity checks. |

Implementation must not simply replace the return value of `posix.identity`. `Snapshot.root`, `location`, structural nested-worktree proofs, container pruning and `opaque_git.inspect_gitlink` currently mix location pairs and live stat pairs. Supply the two concepts explicitly at those boundaries. In particular, a persistent UUID must never be compared to a raw `st_dev` when deciding which entries may be excluded.

The macOS provider reads the UUID and native creation time through the same no-follow directory descriptor. The read-only probe established that these exact attributes are returned from project directories on this local APFS host. The provider checks the filesystem type, local mount flag and returned attribute masks, and rejects unsupported queries. It does not search for another mount or substitute a device number. Validate supported/returned attributes, buffer lengths, nonzero UUID, file ID and creation identity. Encode creation time from integer native fields, not rounded floating-point timestamps. No shell parsing, external installation or `diskutil` dependency is required by the design. No fallback to a persistent device number is permitted on unsupported/ambiguous results.

Apple documents `fgetattrlist`, filesystem UUID attributes and volume-dependent availability, including volume-root query restrictions. The local SDK declares the UUID selector. This supports the API choice, not qualification of the proposed implementation or proof that a UUID cannot be duplicated by a disk clone. [Apple native attribute manual](https://github.com/apple-oss-distributions/xnu/blob/main/bsd/man/man2/getattrlist.2)

The implementation's first check is a read-only native probe on the already-used local filesystem. If qualified attributes are unavailable, stop this path and report the missing capability; do not silently change supported filesystems. Reject detectable ambiguous mount/identity results. This remains accidental-copy/replacement protection under C1, not authentication against a hostile OS account or a fabricated disk clone.

### Legacy revalidation is a new local decision

Old records contain no historical filesystem UUID or creation identity. A matching pathname and inode cannot prove that the historical and current physical volume are identical. The UI must distinguish this absence from a verified persistent-ID match.

Offer a bounded preview of the exact affected registrations. The Owner confirms that the listed current folders are the intended working locations for those existing projects. This is a local identity decision, not approval of file contents, broader Work scope or any result. A batch may contain the six known registrations; never include every project automatically merely because its old device number matches.

A candidate is eligible only when all of these checks pass:

- The authority project/instance, active generation, binding/workspace/integration references and original location indexes agree.
- The complete locator identity, including nonce/epoch, matches the authority; copied locator bytes alone are insufficient.
- The original path is still the selected path under existing platform spelling/alias rules, the old directory file ID matches the observed one, and current no-follow ancestry is valid. A path move, changed inode, missing locator, Git/non-Git transition or unverifiable topology uses a separate recovery path; do not adopt it here.
- Current stable identity is available for each exact role. Git common-dir, gitdir and registered members are checked together; one root match cannot revalidate all worktrees on the volume. A non-primary Git registration missing from the current membership is left as history only when both its old workspace and Git directory are absent. A replacement, inaccessible path or ambiguous Git membership still refuses.
- The complete known-root census, including pending reservations and other live projects, has no independent duplicate/ancestor conflict. Same-project verified worktrees retain their existing exception.
- No unresolved effect, import, restore/rebind, detach or connection publication is being carried through by this operation. Preserve it and report its supported inspection/recovery path.

A single new immutable `connection.identity` v1 schema is proposed, with `initial` and `legacy-revalidated` modes. It records project/instance/workspace, exact binding and registration references, exact observed persistent locations and the authorizing operation. The legacy mode additionally requires the old locations, exact preview receipt and Owner statement; the initial mode uses the already-authorized connection plan. No empty legacy proof is accepted as an initial connection. Its references are mandatory decision/integrity references as appropriate, not display-only hints. Initial connections using the new persistent scheme publish this mandatory identity anchor atomically with their binding. Validators refuse publishing a new-scheme binding or observation without the applicable mandatory anchor; a three-field location container alone does not establish reader compatibility. Validate each mode as a distinct fixed field set and reject role downgrades. The implemented encoding retains old locations through the original decision references. New observation snapshots carry the exact applicable identity evidence as a required decision reference. The immutable submission audit can compare old and new locations without reading current heads or the live filesystem.

Keep existing binding, registration, integration, Work, approval, submission and body objects unchanged. An authority-scoped resolver may use the active anchor to relate only the named old location roles/references to the named current locations. It must never map an arbitrary old device number, arbitrary historical workspace or foreign instance. New observations record the persistent scheme. Existing Work baselines remain immutable; only their exact location comparisons may consult the verified anchor. Content, scope, policy, opaque-entry and protected-tree comparisons keep their current meaning. A scope violation must still refuse after identity revalidation.

Keep the original location index and publish checked new-location aliases to the same exact registration in the same transaction as the anchor. Aliases are a derived lookup, not authority: verify the binding, workspace head and active anchor on every use. Conflicting aliases refuse. Detach, new binding epochs and restored instances invalidate applicability of an old anchor. Restored history retains the old decision, but existing explicit restore-rebind must establish fresh local identity; it cannot replay the old anchor as permission.

### Publication, concurrency and restart

Use existing management/runtime locks, expected-head transactions, operation IDs and store capability requirements. Do not build another transaction service.

1. Preview captures the exact project set, authority instances/generations, relevant heads, locator bytes, native identities, topology and overlap census. It writes no authority or project files.
2. Apply requires the exact preview receipt and Owner statement. Recheck the entire affected census, full selected Git topology, and selected live device/inode observations before publication, under the same management exclusion used by connection/rebind lifecycle writes. Any registration entry point capable of changing the census must share that exclusion or equivalent verified serialization; an unprotected scan alone is insufficient.
3. During this check only, validated candidate identities may replace the exact stale roots in a complete comparison set. This is not an exemption from overlap checks. Compare every independent pair and both ancestry directions, including non-candidates. An unavailable non-candidate still blocks. Do not temporarily write guessed IDs to make ordinary preview pass.
4. Publish each project's anchor, derived aliases and required schema capability atomically using expected heads and the existing operation-ID map. Do not rewrite the DB, replace its pathname, rotate the active generation unnecessarily or modify project files.
5. Across projects there is no claimed all-or-nothing transaction. Record per-project completion. If interrupted, inspect completed operations, verify their anchors and continue only the unchanged remaining approved entries. A new conflict or different target requires a new preview. Normal connection cannot ignore unresolved registrations during a partial batch.
6. Old runtimes must refuse the new required read/write capability rather than ignore the anchor. Existing transaction guards check requirements on every transaction, including old open handles. Candidate manifests must advertise the capability. Verify this behavior explicitly; a new record kind without enforced requirements is insufficient.

A compatible runtime can continue with the appended records. Returning to an older runtime alone is not a supported rollback of the new store semantics. Preserve a verified pre-application export/recovery copy before the first real write; restoring it is a separate explicit recovery decision and must not discard later work silently. Old processes and native effects are never resumed merely by translating persisted identities.

### User-facing behavior

Replace the generic first-project failure with a specific condition: saved filesystem identity needs revalidation, which registered folder is affected, what was verified, and what is unavailable. The next action is the supported preview/revalidation flow, not deleting records, editing identifiers or changing host permissions.

Example approval wording: confirm these listed folders as the current working locations of their existing projects; file changes, Work scopes and submitted results are not approved by this decision. Show partial batch completion and the exact remaining item on interruption. Preserve the original failure code/details in diagnostic output.

## Minimum implementation surface

| Surface | Minimum change |
| --- | --- |
| `platforms/posix.py`, `platforms/observation_port.py`, proposed macOS identity adapter | Persistent location observation with a separate live descriptor identity. Keep existing observation budgets. |
| `platforms/structural.py`, `adapters/opaque_git.py` | Keep pruning proofs tied to live identities while checking registered locations through the scoped resolver. No extra excluded paths. |
| `binding.py`, `connection.py`, `connection_boundary.py`, proposed identity service | Scheme validation, exact anchors/aliases, fresh full overlap check and structured refusal. |
| `workspace.py`, `work.py`, `rework.py` and their actual callers | Resolve only exact historical location roles; preserve baseline, approval, content and policy checks. No arbitrary rebase. |
| `project_setup.py`, `restored_setup.py`, manager command routing, `records.py` | Preview/apply/inspect/resume composition, lifecycle invalidation, required schema, versioned plans and clear guidance. |
| Store/manifest capability assembly | Reuse the existing requirements mechanism; change it only if an uncovered enforcement gap is demonstrated. |
| Existing C1/validation map, paired installed guides and tests | Activate only the accepted amendment, explain the supported recovery flow, add focused regressions. |

These are affected boundaries, not permission to refactor every listed module. Inspect actual callers and keep unchanged implementations when the shared abstraction is sufficient. Product-neutral design belongs here; private roots, native identifiers, raw review packets and failed runs remain in the existing internal evidence directory.

## Focused verification selection

Reuse the accepted storage, body, backup, installation, HTTPS and Git integration evidence outside the changed boundaries. Do not repeat the full source suite, full host matrix or previous writing demos for a changed digest alone.

| Check group | Required new or extended case |
| --- | --- |
| Native identity | Same persistent volume/directory with changed live device token; different UUID with coincident inode; directory replacement/birth change; unsupported/empty UUID; descriptor/ancestor replacement during observation. A synthetic device-token change is labelled synthetic. |
| Existing failure | Six legacy registrations and an unrelated new target: ordinary connection initially refuses; read-only preview changes nothing; approved exact batch establishes anchors; new target no longer fails for that resolved identity reason. Unknown/missing roots still refuse. |
| Overlap protection | Parent→child and child→parent, same root through existing supported alias spelling, independent Git common-dir conflict, sibling success, same-project sibling/nested worktrees, conflicting connection after preview and during resume. Reuse the existing project/restored-setup fixtures. |
| Work continuity | Existing approved scope and original before/submission bodies unchanged; valid in-scope continuation succeeds; out-of-scope and overlapping unauthorized edits still refuse. Include rework context, policy and opaque-entry changes. No approval or acceptance is manufactured. |
| Publication/recovery | Kill before/after per-project publication, partial multi-project batch, stale receipt/head/locator, idempotent operation inspection, index/anchor conflict, old running reader/writer refusal, export/restore with historical anchor and new local rebind. |
| Cross-platform | Existing Windows location/case/reparse protections and no-op legacy Windows behavior through shared logic. No raw Windows identity migration. |

Regression assertions compare authority heads/operation set, project marker bytes, Work scope/approval/submission/body references before and after. A refusal must not publish an anchor or alias. For unexpected exit after a possible commit, report outcome unknown and inspect the existing operation; do not call it a clean refusal or replay it. Include one mutation-style counterexample that disables the scoped identity/overlap guard and demonstrate that the corresponding test fails.

Likely reuse: `test_foundation_project_setup`, `test_foundation_restored_setup`, `test_foundation_connection`, `test_foundation_binding`, `test_foundation_observation`, `test_foundation_rework_integrity`, `test_foundation_windows_observation`, and existing store capability/activation fixtures. Select concrete cases after implementation; do not run entire modules repeatedly during iteration.

## Installed application order, requiring later approval

1. Build and inspect the corrected candidate with existing runtime/dependencies. Keep the frozen checkpoint and prior signed candidates intact. New signing/application are not part of this design authorization.
2. Qualify on an isolated macOS installation and synthetic authority first: legacy refusal, exact revalidation, preserved Work/body references, duplicate rejection and normal in-scope continuation. Confirm the new manifest's capability and old-runtime refusal. Verify persistent identity across an approved restart of an existing test VM or another controlled mount-lifetime boundary; if only simulated, retain the real-lifetime check as unverified. Do not reboot the user's host to manufacture this evidence.
3. Apply to the affected host installation once, then read-only preview all six existing registrations. Present one exact Owner decision. Preserve a verified backup; process the six approved entries once with per-project checkpoints. Installation and record revalidation are distinct permissions even if authorized in one later bundle.
4. Confirm old Work/submission lookup and the representative copy's connection preview. Only then resume its already-approved Work trial. Do not substitute the identity correction for that real-use evidence.
5. Qualify shared boundary changes on Windows ARM64 and x64 with narrow installed overlap/rebind/Work-location checks, reusing existing installations. Platform-native differences cannot be discharged by a POSIX double. Full Windows installation, HTTPS, Git staging and agent-mode matrices remain reusable unless the implementation changes their relevant behavior.

Stop on changed project set, uncertain native identity, unsupported attributes, denied access, active external effect, corrupted/mismatched locator, overlapping independent roots or a new unclassified failure. Preserve the exact state; no blind retries or protection waiver.

## Estimates and next authorization

The 60-minute design stage is complete. The Owner subsequently authorized the source correction and focused tests within 240 minutes, including up to two Claude reviews of 420 seconds each. Installed application remains outside this approval.

Original estimates and proposed installed scope:

| Bundle | Normal elapsed estimate | Stop cap | Included and uncertainty |
| --- | --- | --- | --- |
| Native read probe, narrow source correction, focused regressions and plan/result static review | 100–160 min | 240 min | Reuse existing storage/capability and overlap fixtures; two Claude reviews, expected 90–180 s each, cap 420 s each. Review/preparation overlap counts once. Native API availability or a new record-protocol issue can stop the bundle. |
| macOS isolated candidate/application, synthetic native check and exact host revalidation | 45–75 min | 120 min | Existing runtime and trial key; one update per actually selected isolated target, one exact batch over existing records. VM login/restart and Owner waiting are separate external delays; this is not permission to perform them now. |
| Windows changed-boundary installed checks | 20–35 min | 60 min | Existing ARM64/x64 assets and installations; candidate/manifest content and target access must be ready. x64 device availability is external waiting. |

The earlier measured small source and installed fixes (about 73 and 29 minutes) bound reuse expectations; this new identity contract, compatibility bridge and crash boundary justify additional work. These are planning judgments, not measurements of this change. Do not sum stop caps as a normal completion estimate. The representative Work trial retains its separate existing 180-minute cap and remains unexecuted.

The Owner accepted explicit revalidation with immutable history and the required reader/writer capability. The remaining application decision concerns the exact installed target, verified backup and exact record batch. No generic old-record migration obligation, general move support, production key work or publication is added.


## Source correction checkpoint

The source adds `identity-preview`, `identity-apply`, `identity-status` and `identity-resume` to the management entry. Preview requires explicit project IDs and records the whole occupied-root census. Apply checks the receipt and exact selection; it publishes one atomic decision per project. Status reads recorded completion separately from the current filesystem, so a missing remaining folder does not hide finished entries. Resume verifies the remaining selection before publishing and skips confirmed entries.

The read-only macOS probe confirmed the required native attributes for the source directory and two volume roots. Synthetic tests cover the six-record interruption and continuation, old-runtime refusal, exact Work history and body references, scope refusal, reserved-root overlap, retained Git workspace registration and a missing derived index. Existing connection, Work, restore, Git and observation cases were reused. The Windows observer checks used source fixtures on macOS; they do not qualify a Windows installation. A real remount/reboot and installed application remain unverified.

The source and tests are uncommitted. No existing installed authority, failed attempt, or representative Work was changed. The original review attempt was blocked before transmission. The Owner then approved the exact two inputs and destination; both static reviews completed within their limits.


### Review disposition

- Apply now pins the full selected Git topology and the live device/inode pair read from the same descriptor as persistent identity. Rechecking the exact plan detects a live-pair change even if persisted identity remains equal.
- Restored the previous protection against a plain reservation at a Git common directory, including an independent attempt through a separate linked worktree.
- An absent non-primary Git workspace may remain historical without blocking revalidation of its primary. Git must no longer report that member and both recorded paths must be absent. The old registration is retained. A missing independent project remains an unresolved overlap boundary; this change does not add retirement, deletion or forced detach.
- A native APFS probe demonstrated that backdating mtime can change creation time without changing the live device/inode pair. The user receives a specific refusal for that change. There is no automatic reattachment or same-inode exception. Recovery for an already-persistent identity that changed requires a separately designed and approved flow.
- Native ancestry already compares object identity rather than path spelling, and mandatory schema requirements already make incompatible runtimes refuse. The UUID parser accepts canonical UUIDs independently of their version. The peer-selection loader is bound in the actual implementation; its focused tests already passed.
- An exact block-level volume clone can reproduce all recorded identity fields. Those fields do not authenticate a disk clone. The workflow assumes a trusted local volume and explicit confirmation; cross-volume relocation and clone adoption remain out of scope. A changed census after interruption needs fresh review.
- Seven affected checks passed after these changes. Static review covered the original approved diff; the follow-up corrections were verified locally with the focused tests. Installed behavior is still unverified.
