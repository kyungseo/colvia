# PATCH-20261125-006 — Consistent Git marker classification in workspace observations

Owner-approved pre-publication correction, following [the native finding](CHORE-20261125-005-windows-directory-pinning-safety.md#pre-publication-candidate--nested-git-marker-case-on-windows). Selected on 2026-11-25. Product baseline `6ae484d`, preceded here by the separate Phase F documentation-only commit `41bbe8c`. The work began at 18:42:01 KST and is capped at 00:42:01 KST on 2026-11-26. The native x64 allocation closes at 20:50:22 KST. No changes to folder sharing, path links, package, schemas, authorization or publication semantics are in scope.

## Plan and baseline

Windows previously admitted case variants of an unregistered Git marker in a strict snapshot while checking all case variants in selected-path validation. A native case-insensitive macOS fixture reproduced the mismatch.

- Git recognized the marker by its conventional spelling.
- A strict POSIX snapshot included the case-variant nested metadata.
- A case-variant root marker also appeared in observed files despite a canonical root marker boundary with its exact identity.

Use a case-insensitive reserved name in strict snapshots on both ports. Exact proved boundaries take precedence. Only the root marker may use the canonical boundary key when a differently spelled entry has no exact proof and its native identity matches. Keep the collision check before pruning, preserve protected content and keep symlink, link, Git policy, effects and before/after observations in place. Non-strict snapshots retain their existing admission. The existing reason codes remain the interface. Newly rejected case variants use `unregistered-nested-git`. A wrong approved root identity remains `structural-boundary-changed`, conflicting protected content remains `boundary-swallows-protected` and a collision remains `path-collision`. Windows selected-path verification retains `progress-nested-project`.

## Static R0

One fresh Claude Opus 5.5 tool-disabled review on the same first-party subscription. The private exact packet digest is `7d900262135eb27f754bf28b059115d0a96c4e109a5b588abdee0176a78012d8`. It used a fixed product revision, selected public source excerpts and non-sensitive native outcomes. The review allowed proceeding with corrections inside scope. Original response and dispositions are retained.

| Finding | Disposition |
| --- | --- |
| G1. Preserve root collision precedence | Accept. POSIX checks the already enumerated sibling names only at a strict root marker. Windows already refuses folded-name collisions in its native listing before entry processing. |
| G2. Protect all spellings at the proved root | Accept. Match the protected first path component using the same case domain for both exact and fallback root Git boundaries. Other boundaries retain exact behavior. |
| G3. Align logical comparison | Accept. Reuse the normalized casefold previously computed for alias checks. Test the last path component without a new filesystem lookup. |
| G4. Bound the root fallback | Accept. Requires strict mode, a root marker, no existing explicit entry, the canonical proof key, and the existing non-symlink and exact native identity checks. |
| G5. Verify strict caller and flags | Accept. The application plain, inventory and content observations that pass structural Git proofs request strict nested-marker rejection. No non-strict caller was widened. |
| G6. Protect existing observations | Accept. Saved baseline paths and approved scope are supplied for Work re-observation, submit and publication recheck. Root protected evidence refuses instead of disappearing silently. First observations without prior content drop only the proved metadata. |
| G7. Record admissibility on case-sensitive volumes | Accept. The three reserved spellings are refused in strict mode even on a case-sensitive volume. Lower-level non-strict observers retain prior behavior. |
| Optional canonical-duplicate input hardening | Defer. Existing topology proof provides a single canonical root boundary. General boundary validation is outside the correction. |

## Verification plan and evidence

The changed workspace observation applies to plan, submit, accept and grouped validation. Use a single complete eligible normal and parent-optimized macOS regression on the frozen candidate and a native x64 focused result on two fixed overlay files in a standard-account copy. Keep previous Windows and macOS evidence separate from execution on this candidate. Required targeted cases cover ordinary controls, the three reserved spellings, a legitimate root boundary, wrong identity, old protected content, link rejection, existing nested registration and case collision.

Normal and parent-optimized targeted checks each passed 31 tests. On actual case-insensitive APFS, the new observer refused the synthetic nested marker with `unregistered-nested-git`. With a verified root marker boundary it succeeded and excluded the root Git metadata. The same fixture in non-strict unit tests still permits the content. The source and tests were fixed before the complete run. One early regression invocation inherited the evidence shell's umask and was stopped after a fixture creation-mode discrepancy. The candidate remained identical and the qualified execution restored the prior test-process umask.

Native x64 CPython 3.14.7 passed the fixed focused trial in a disposable copy. The two changed modules matched the expected bytes, 174 other copied files matched baseline, and all 216 original slot files retained their digests. Strict assessment and selected-path verification refused the three nested cases with their respective existing reason codes. Non-strict observation retained its behaviour. Proof-based root admission, protected-content refusal and wrong-identity refusal were confirmed. The owned Job returned zero with no active processes and EOF on both pipes. This qualifies the named focused native lane. An installed release artifact has its own qualification.

Native macOS application-level observation in a real temporary Git repository confirmed the identity-proved root and refused the nested case variant. Both macOS parent modes completed the normal and grouped partitions with 3,309 discovered occurrences each, 2,781 passes, 526 fully skipped and two partially skipped cases per mode. There were no failures, new skips or candidate drift. The five added observations all passed in both modes. The existing discovery and execution ledgers were reconciled against the prior anchor. Review before formal result acceptance remains separate from this round's authorized draft-PR delivery.
