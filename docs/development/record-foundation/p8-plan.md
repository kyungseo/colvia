# P8 separate Git integration

Status: source plan within the approved P4–P9 bundle. Ordinary result acceptance remains metadata-only. Product commits, real repositories, installation, host changes and stopped native execution retries remain held. Only task-owned synthetic fixture Git writes are authorized.

## Proposed implementation slice

Reuse retained accepted Work bodies, the project effect barrier and the verified Git executable/topology port. Add one Git integration service and a native Git effect port, not a new Work acceptance path. Keep the full candidate/receipt and external-effect journal distinct from ordinary Work records.

1. Preview selects exact completed Work/result references in the destination workspace. Require current selected files to match accepted postimages. Applying another workspace's result remains WorkerService's separate operation first. Candidate paths must be regular-file transitions; protect unchanged symlinks and gitlinks, reject edits through opaque ancestors. Duplicate selected paths from different results must agree exactly or refuse.
2. Admit an attached, uniquely checked-out branch, including an explicitly absent branch for unborn HEAD. Parse the complete index v2/v3 with checksum, entry flags, names and a bounded optional-extension allowlist. Refuse unresolved stages, split/sparse index, unsupported flags/extensions, active transforms, partial-clone/promisor/alternates, sign-required commits and executable hooks. Expose a concise manual Git path when automation is unavailable; never silently disable an intentional hook. Capture actual symbolic HEAD, branch, OID algorithm, index bytes, worktree membership, config/attribute identities and executable identity.
3. Stage immutable selected bodies in private durable scratch. Hash blobs with `hash-object --no-filters`; build the commit candidate from HEAD plus only accepted paths using a private index. Build I1 separately from the complete original index, replacing only selected entries and preserving unrelated staged entries and supported flags. Compare parsed index entries/flags, not stat-cache offsets. Report the complete candidate commit diff, exclusions and author/message before an exact approval. Object creation and private-index writes are preparation effects, never a completed commit or result acceptance.
4. Reserve one durable project effect before touching branch/index. Persist index-lock creation intent, then create `index.lock` exclusively and capture native file/process-start identity. Preserve I0 and I1 and record exact O/N, symbolic HEAD, config/topology and working-file preconditions. Hold no SQLite transaction during Git or file effects. Pin an empty private hooks directory after checking actual hooks; use bounded plumbing with fsmonitor, optional refresh, external diff and lazy fetch disabled.
5. Recheck before CAS `update-ref O→N`; inspect actual ref even if the child returns failure. Ref-child/HEAD/packed-ref lock files are observations, never automatically removed. After the ref moves, complete the already approved I0→I1 transition using destination/HEAD identity, original index identity/bytes/mode, owned lock and object availability. Later working-file edits are not overwritten or silently accepted; they remain unstaged changes. Do not require selected working files or unrelated configuration to remain at their pre-commit values after N is already visible. Verify final index bytes/mode, ref, destination identity and retained Git objects before authority completion.
6. Interruption classification is exact O/I0, N/I0, N/I1, O/I1 or other, plus lock identity/liveness. Explicit recovery may finish only N/I0 or record N/I1 under exact destination/index dependencies and proven process closure. Unknown/replaced/live locks stay untouched; process age is not closure. No rollback, ancestry-based success or automatic retry. On Windows sharing failure, preserve the recorded partial state and remove only a provably owned lock if closure is established; native qualification stays separate.

The existing process reader is not sufficient evidence of a mutating child outcome. Add a journal-aware writer boundary that records admission/start/exit/closure. If bounded termination or process identity is unavailable, retain the pending effect and refuse completion. Do not reuse the stopped P5 sandbox trial to infer success here.

## Focused oracles

- HEAD candidate excludes unrelated staged changes; I1 keeps them; unrelated unstaged files remain unchanged.
- Selected index equals HEAD or accepted postimage; divergent partial staging refuses before branch/index mutation.
- Unborn HEAD, deletion, executable mode and binary body; SHA-1/SHA-256 parsing where the installed Git supports it.
- Hook appearance, filter/eol config change, branch/worktree movement, accepted-file edit and index replacement refuse.
- Faults at lock intent, lock identity, prepared state, ref CAS before/after result, index replacement and final publication. An existing foreign lock is never removed.
- Restore retained Work does not transfer original workspace authority or imply Git integration. Export preserves integration evidence without replaying external effects.

Expected P8 source effort remains 6–9 active hours, within the approved cumulative cap. Use focused fixtures first, then include only the cumulative changed behavior in P9. A prepared source command or passing POSIX fixture does not qualify native Windows, a desktop host or a public installer.

## Focused review corrections

Apply [P7/P8 Driver dispositions](p7-result-p8-plan-disposition.md) before implementation. In particular, serialize all emitted index entries with invalidated stat-cache fields, preserving unselected content and flags; refuse selected assume-unchanged/skip-worktree/intent-to-add; drop disposable TREE/EOIE/IEOT/FSMN extensions and initially refuse REUC/unknown formats; refuse skipHash, reftable/unknown extensions, grafts, alternate or replace-object views. O/I0 recovery can release only a proven abandoned owned lock and record not-applied, never rerun the commit. The Git writer does not signal timed-out children: preserve pending evidence and require observed closure before recovery.

### Result-review clarification

Full context is an admission condition before ref CAS. Completion after N is visible cannot replay that admission as if no effect occurred. Preserve later user edits while completing the approved index bytes. A pre-ref abandoned operation may release its proven lock and record not-applied even if the working file changed. Ref/index divergence after an observed effect still refuses.

Re-adopt a proven abandoned owned index lock in place. If it is absent, an exclusive create is allowed only while the exact I0 native identity/bytes/mode still match; an existing unknown replacement is never removed. Recheck current child-group absence using the recorded spawn identity; an old exit callback is neither required nor sufficient. Missing spawn identity remains unknown. This does not authorize signalling timed-out children.
