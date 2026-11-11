# R3a disposition and focused independent check

Status: 2026-11-06 Driver review intake. These are proposed contract amendments for the next focused review, not implemented behavior or Owner policy acceptance. The 13 R3a inputs remain byte-identical; this document does not silently activate a replacement contract. Before the affected implementation phase, merge the reviewed corrections into C1–C8, the refusal map and validation plan. Progress belongs to the [owning Work](../FEAT-20261106-002-record-foundation.md).

## Verdict and provenance

Retain the direction: one project authority, workspace-specific observations, preserved bodies, explicit human acceptance, independent Git integration and managed runtime. R3a is useful follow-up scrutiny, but it is not the fresh independent review requested. A new conversation should challenge only the residual format/recovery/access questions below; repeating the entire project investigation is unnecessary.

The [exact reviewer response](review-r3a.md) is preserved without edits. Reviewer reports Claude Opus 5.5, session identity unavailable, same conversation as R2 and informal advice. All 13 named inputs matched their manifest on Driver intake. Reviewer disclosed additional source/development-record reads outside the allowed list. Driver independently inspected the relevant current product functions and existing test definitions for S1/S7; this does not retroactively authorize the reviewer's access. Its disclosure paragraph calls the payload issue R3, while the finding is S7; the original typo remains intact. No new product tests, model calls, installation or host changes were performed for this disposition.

## Mandatory findings

| Finding | Disposition | Concrete response and phase |
| --- | --- | --- |
| S1 protected opaque entries | revise | Accept representing symlinks/gitlinks without offering their editing. Qualify the current limitation as admitted/tracked entries, not every ignored link anywhere. Commit ID alone does not observe a submodule working tree; use the boundary conditions below. Settle before P1. |
| S2 unknown reference roles | revise | Define roles on a generic reference envelope and constrain them by the parent schema. A writer cannot relabel a decision dependency as optional provenance. Preserve unknown optional objects during export. Settle before P1. |
| S3 intentional body removal | needs-user | Recommend a separate, previewed reconstruction operation, with additional fencing/retirement safeguards below. Owner has not approved deletion or changed retention policy. Resolve before format freeze. |
| S4 early host access | revise / needs-user | Prepare a product-independent diagnostic alongside P0, followed by actual managed-launcher qualification later. A generic probe cannot prove the installed path. Real host/settings/model execution remains subject to the existing hold. |
| S5 new workspace and entry | revise | Verify same common-dir/project and associate a new workspace on its first authorized mutation without a redundant connection question. Read-only discovery remains read-only. Make missing worktree entry visible at connection; no automatic Git commit. P2/P3. |
| S6 index lock recovery | revise | Add ownership, process identity, interruption and replaced-lock handling. A stale index lock obstructs index writers, not every Git read. No age-only deletion. P8. |
| S7 fixed secret-pattern checks | accept | Name the existing payload/return/composed-output checks explicitly in RF-27 and RF-T27 before P5. Preserve tested limitations; this is not a general PII guarantee. |

## A. Entry and reference format amendments for P1

### Protected opaque entries

Replace the regular-file-only tree assumption with a versioned discriminated entry representation. Regular entries retain exact bytes, executable mode and content identity. A symlink entry records mode 120000 and exact target-string bytes identity, without following the target; the target's contents are not thereby protected. A gitlink entry records mode 160000 and the Git object algorithm plus commit OID, not a misleading body SHA-256. Unknown entry kinds fail closed for decisions.

The first implementation permits ordinary edits elsewhere only when opaque-boundary observation is trustworthy. Opaque paths cannot be selected for edit, materialization or changed Git integration. An unchanged opaque entry can remain in a whole candidate tree; otherwise merely preserving a symlink would make unrelated Git integration unusable. Missing/changed opaque entries are out-of-scope changes. Explicitly state that a superproject Work does not preserve or approve the contents of a submodule or symlink referent.

For initialized submodules, inspect verified topology, checkout HEAD and dirty/untracked state under a defined, non-mutating observation policy. A dirty or uninspectable boundary cannot pass merely because its commit OID is unchanged. The initial conservative route refuses such a boundary; a pristine boundary may be preserved only with repeated verification and no supported editing below it. Ignored submodule content remains outside this limited guarantee; a claim to preserve every byte there would require a separate admitted-content snapshot. Do not initialize/fetch/reset submodules as a side effect of observation. Handle deinitialized/absent state explicitly; nonempty unregistered paths are not equivalent to absence.

Windows link emulation and reparse points require platform-specific evidence; do not treat every reparse point as a safe symlink. Unsupported special devices, multiply linked content and ambiguous ancestry still refuse. This is protected representation, not comprehensive submodule support.

Planned tests: unrelated regular edit with unchanged link/clean gitlink; changed target string; attempted referent/path edit; same gitlink OID with changed submodule HEAD, tracked content or untracked content; absent versus unregistered nonempty submodule; platform link emulation; unchanged opaque entries retained in the whole commit candidate. These are proposed tests, not reproduced cases.

Source basis: current `work.py` regular-file/index-mode/manifest checks reject admitted non-regular entries. The official [submodule description](https://git-scm.com/docs/gitsubmodules) defines the gitlink as an expected commit; [status documentation](https://git-scm.com/docs/git-status) separately reports HEAD, content and untracked changes. Those distinctions support the correction, not an executed qualification.

### Generic edges and compatibility

Keep an object identity reference separate from its use: each dependency edge has `{role, ref}`, where `ref` retains C2's kind/version/length/digest. Fixed v1 roles are decision, integrity, provenance and display. Parent kind/version/field schemas specify permitted roles; required fields cannot be weakened by selecting a different role. The canonical object's digest includes its edge roles. Unknown roles refuse.

Decision/integrity dependencies and mandatory capability requirements must be understood and verified. Provenance/display may be rendered as unavailable only when the known parent contract permits omission for that operation. If an operation needs provenance to justify its decision, that dependency is required regardless of its label. Optional unknown data is never interpreted as approval or executable instructions.

Every typed object's dependencies must be exposed in a generic versioned envelope, including unknown optional kinds; no hidden authoritative object references inside opaque payloads. This lets export preserve and validate complete reachability without understanding optional semantics. Unknown required reader/writer features block the corresponding operation. Optional means skippable display, not discardable data or permission to write over an unknown extension. Tests must cover round-trip preservation and refusal of a role-downgrade attempt, not just unknown kind display.

Creation ordinals are derived local storage values, excluded from immutable identity and export. Restore validates generic edges, rejects cycles, and assigns fresh topological ordinals. Selected query locality still follows only the dependencies needed by that operation; full audit/export is a separate bounded traversal.

## B. Body-removal decision — not authorized

Preferred proposal: after an explicit affected-content preview and Owner confirmation, reconstruct a new store through logical export/restore, preserving the historical decision facts and recording why bodies are intentionally unavailable. Do not mutate an immutable historical body descriptor in place. Use a versioned removal record/availability overlay linked to the preserved identity; prevent affected operations from bypassing it by following an older root. Define reader/writer requirements and complete export semantics before v1 freeze if selected.

Reuse of C4 reduces implementation, but does not make the cutover and old-store retirement automatically safe. Quiesce/fence all writers and relevant readers, preserve operation identity and binding epochs, verify the new store, activate its instance, and handle interruption before/after activation and before/after old-store retirement. A stale process must not keep serving the removed body from an old open handle. An unproven old process or file ownership stops retirement; Windows open handles and filesystem behavior require qualification. Report removal pending rather than claiming completion while the old live store remains available.

A shared chunk proves identical chunk bytes, not that every consumer contains the same whole secret. Preview affected bodies/decisions and chunk sharing without printing the sensitive content. Never delete a chunk still needed by an unapproved retained body. Any necessary expansion of removal targets needs confirmation. Prevent silent refill from older local snapshots during repair/import. Preserve original result acceptance as historical fact, while content-dependent replay, application and new acceptance refuse when required content is absent.

Deleting the old DB does not prove physical secure erasure; exports, OS snapshots, original files, Git history and filesystem remnants remain separate. Fresh-store activation and disposal have independent failure states. Temporary space is measured from actual source/retained data and backup requirements, not promised as exactly two times.

Owner choices: include a bounded reconstruction-based removal command in the first release (recommended, after its contract/cost check), or retain bodies without individual removal and clearly disclose that limitation. Existing no-automatic-deletion policy stays effective meanwhile. Reviewer 8–13 additional hours is an unmeasured estimate and does not yet cover every cutover/retirement detail above; it is neither a budget nor an accepted forecast. A new schema version remains a legitimate later mechanism; an empty reserved enum is no substitute for specified semantics.

## C. Early host check and workspace entry

Prepare the smallest fixture-only access diagnostic alongside P0, before broad feature porting. Record each host's baseline permissions first. Check narrow project-authority access, DB/journal creation and recovery, restart persistence, new linked/app worktree sessions and whether each normal command needs another prompt. Test a sibling directory's denial only when the selected baseline host mode actually isolates it; a host that already permits broader writes cannot prove a sandbox boundary by this test. Ensure the new grant adds no unintended paths.

The final installed manager/runtime identity, launcher routing, update binding and actual host journey remain separate tests. Source success and a generic SQLite probe do not satisfy them. Reuse the qualification cell; count the diagnostic and final confirmation separately where their risks differ. No automatic grants to all authorities, sandbox disabling, installation or authentication changes are authorized here.

If narrow access fails, first identify the host-supported per-project grant or explicit per-operation path. Report the required action and user cost. A broader grant or changed integration architecture needs Owner choice; unsupported is not inferred from a failed first probe. Present concrete commands, targets, time and invocation limits together before executing this held diagnostic.

Already connected, identity-verified worktrees may be resolved provisionally for read-only queries without writing registration. Register on the first authorized state change under the existing project connection, rechecking membership/generation and retaining a distinct workspace identity. This does not authorize editing or accepting any Work. Foreign/copied/orphan roots remain unbound. Copies must not present the original project's Work as their current state.

Connection must ensure an agent entry reaches future worktrees: explain the required entry commit, or use an explicitly qualified host-level route. Never auto-commit it. Compare managed entry fragments/version without overwriting project rules. Colvia cannot diagnose a session in which it was never invoked; document that limitation and cover it in first-entry tests.

## D. Git lock and official execution

C6 recovery must include exclusive lock creation, durable operation ownership, native file identity and process-start identity; PID or age alone is insufficient. Cover a crash after lock creation but before durable ownership: such an unproven lock is not automatically deleted. External or replaced locks are preserved. Before completing I1 or removing an owned abandoned lock, recheck ownership, the relevant ref/index/working-file row, process liveness and operation fencing. Do not race a new writer or overwrite a divergent index. Preserve partial lock bytes as evidence when the state cannot be proven.

The existing O/I0, N/I0, N/I1, O/I1 and external-divergence table still applies. Add kill/restart tests around each lock boundary, including ownership-record failure, live owner/PID reuse, external replacement and partial lock contents. Git's [lockfile API](https://git-scm.com/docs/api-lockfile) separates writers from readers and describes exclusive creation/rename; normal cleanup handlers do not substitute for Colvia's abrupt-crash recovery contract.

RF-27 amendment: preserve fixed secret-pattern refusal for outgoing frames, tool returns and composed replacement content before its write reservation; include supported nested decoding/escape cases. Do not log rejected raw content or secret hashes. Existing S1b tests for nested escapes, cross-boundary credentials, actual boundary joins and late rejection after an applied effect are named reuse inputs. A late output refusal cannot rewrite an earlier applied effect to none. Source/test definitions were read, not rerun. Retain false-negative/false-positive limits; ordinary chat and general PII are not newly covered.

## Remaining recommendations

| R3a item | Disposition and amendment |
| --- | --- |
| R1 registry reconciliation | accept: update only Colvia's authorized registry; no implicit Git worktree prune or Git metadata cleanup. |
| R2 copied-root reads | accept: show unbound/copy mismatch and next step, not the original history as current. Explicit historical inspection, if offered later, must identify its distinct source. |
| R3 local ordinals | accept: derived, reassigned after complete import graph validation; see A. |
| R4 shared staged chunks | accept: many-to-many import claims; reclaim only with no published dependency and no live claims, transactionally. Timeout alone cannot prove another importer abandoned its claim. |
| R5 repair trust | revise: retain trusted metadata/root chain/high-water versions outside replaceable runtime slots; authenticated repair must preserve them. Unknown/invalid trust stops; a warning alone cannot authorize reset. |
| R6 storage summary | revise: do not replace bounded counters with an unbounded aggregate scan on every status. Use audited/rebuildable accounting, cheap physical size and explicitly estimated expensive values. Full reconciliation remains separate. |
| R7 WSL | accept with qualification: detect native invocation against WSL-shared project/authority paths; do not claim Windows qualification for them. Other network filesystems also require separate qualification. Linux process support remains later. |
| R8 stale estimate | accept: the current pointer is implementation-plan's latest estimate, not the historical 50–75-hour paragraph. Reconcile both documents before implementation. |
| R9 changed global ignore | revise: offer an explicitly authorized policy restore, or a separately approved new baseline for remaining work. Do not rewrite global configuration automatically, erase old evidence or certify the old Work by starting a new one. |

## Cost and next gate

The last Driver forecast is 75–120 active implementation hours, excluding body removal and actual qualification. R3a estimates 90–145 hours for the same broad scope and identifies optimistic P3/P6/P9 assumptions. Treat this as a material risk to the Driver forecast, not a new authorized budget. Do not mechanically add every finding's hours on top of revised phases: some are the same work already included in those phases. Reconcile reusable components and missing implementation once at the implementation gate; do not advertise 75–120 as a settled completion promise.

The proposed 100-hour cumulative stop remains unchanged and may be reached before completion. No automatic extension, removal command, host execution or implementation kickoff follows from this intake. Preserve the P1/P2/P3 measured re-estimation gates. Owner waiting and actual qualification remain separate. The next fresh review should settle correctness and identify omitted cost categories, not produce yet another unsupported universal total.

Four focused questions: (1) protected opaque entries and role/envelope semantics; (2) optional removal availability/cutover; (3) host probe/worktree entry and no repeated authorization; (4) Git lock recovery and preservation of existing secret checks. Read current contracts first, then this proposed delta; report a concrete counterexample for any mandatory change. No new general repository survey or another rewrite is requested.
