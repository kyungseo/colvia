# CHORE-20261125-005 — Native Windows directory pinning safety trial

Status: Owner-approved design/evidence trial. Source and installed test baseline `48e5d86`. The Owner accepted [Phase E](CHORE-20261125-004-windows-workspace-observation-design.md) and kept relative open on hold. Hash hints and watcher work remain deferred. Verification cadence remains a separate candidate.

## Authorized work

On the existing native x64 standard-account lane, run a single disposable synthetic trial. Compare the current metadata-only masks with a list-directory handle excluding delete sharing, first held for directory D and then its relevant ancestor chain. Check rename, cross-parent move, empty removal, ancestor rename, temporary replacement and restoration, supported POSIX-semantics rename and a synthetic junction. Retain actual native errors, observed state and process/handle closure. Check routine child saves and Git with a handle held in the same fixture. The documented plan/submit times describe an earlier measurement; this round measures no latency.

Follow-on relative-open safety requires the pinning gate and ordinary-operation controls to pass. If eligible, check file identity after a relative open, the current observer against the same replacement control, separate workspace/store links, and a permission-negative control using an available unmodified synthetic fixture. The Owner excluded symlink testing, policy/security changes, installation and product edits. Failure or missing parity evidence retains the hold. Independently check native same-object reopening and nested Git marker comparison. A reproduced marker discrepancy can be registered for separate pre-publication review.

Started 18:19:50 KST. Cumulative cap 23:19:50 KST. One native allocation, capped at 20:20:40 KST. Driver estimate 3–4 hours including the independent Git action. Separate R1 was waived for this evidence-only round. An implementation proposal would require a new R0 and Owner approval.

## Existing behavior and documentation

The current Windows observer resolves the path, checks the native object and rechecks at observation points. It uses pathname-based names and symlink target reads. A held metadata handle allowed some directory changes in the bounded prior tests. Continuous registration identity and detection of a change restored between observations are outside the demonstrated guarantees. These limits concern workspace observation; they do not change the private store, worker boundary or final publication contract.

Read-only check of SECURITY, README, both manuals, packaged guides and the named technical contracts at the observed main and updated PR head found no promise of continuous directory pinning or detection of transient replacement between checkpoints. The Windows workspace contract already calls for checks before writing and qualifies same-account races. No public-facing wording change was indicated.

Phase E now states that 145.804 seconds of submit ancestor validation is aggregate product cost. The workspace/store split is unknown. The earlier 64.079-second gap is 244.079 minus 180 seconds at the launcher-inclusive eight-member accept boundary. The updated Phase E record labels distinct directory, listing, process and pass counters with their actual coverage and marks static call-site mapping.

## Independent Git integration

Draft PR #90 was fast-forwarded from `d09530c` to `a09c57e` (Phase D cherry-pick) and then `6ae484d` (Phase E documentation). The cherry-pick tree differs from `48e5d86` only in the Phase C acceptance record. The second commit changes four development documents. Two-mode macOS evidence was reconciled by 481 unchanged input digests and the retained, already checked single-test fixture correction. The four Windows source overlay digests and historical launcher/slot receipts agreed. Reuse applies to that existing evidence, with release qualification a separate stage.

Disclosure checks passed for the two commits and the proposed PR body. GitHub readback confirmed the two-commit head, open draft state and the submitted body including Phase D and E results. The trial results in this record are local pending Owner disposition.

## Native safety results

The first native run on Windows 11 26300.10075 verified the selected managed slot and 216 input files, then used fresh standard-account synthetic cases. Native Win32 outcomes appear below. The first run did not collect NTSTATUS.

| Hold | Rename D | Move D across parents | Remove empty D | Rename D's parent |
| --- | ---: | ---: | ---: | ---: |
| None | 0 | 0 | 0 | 0 |
| Workspace leaf access 0x80, share 1, D only | 0 | 0 | 0 | 5 |
| Ancestor access 0x20080, share 3, D only | 0 | 0 | 0 | 5 |
| List-directory access 0x20081, share 3, D only | 32 | 32 | 32 | 5 |
| List-directory access 0x20081, share 3, synthetic chain | 32 | 32 | 32 | 32 |

All 20 matrix cases reached the requested hold or no-hold state before the operation. Win32 0 indicates the change succeeded, 5 access denied, and 32 sharing violation. Permanently suppressing every directory mutation is not demonstrated by this shortened first run. The three outstanding cases were requested separately within the original allocation without replaying these 20 cases. Follow-on relative opening remains gated on the complete evidence and ordinary compatibility.

While holding the synthetic chain, ordinary child-file editing and atomic replacement passed. Git status and single-file checkout exited zero and the checked-out bytes matched. The protected directories' rename/move/remove operations would be unavailable for the duration of the handle hold. A long observation can therefore interfere with folder refactors and file tools that rename a directory, even when routine file saves and simple Git commands work. Directory-changing editor and Git operations were not separately qualified.

### Same-object reopen (F6)

`ReOpenFile` opened a second regular-file handle. The file ID and bytes matched. The directory attempt reported Win32 5 under the tried configuration and produced no second ID. Reopening a known object can preserve identity evidence. A same-object match supplies no fresh lookup of the registered name, ancestors, or current namespace binding. Any design would need a substitute for that independent observation before removing checks. The two content passes have 6,002 extra ancestor guard entries over the inventory passes, consistent with 6,000 workspace-file reopens and two fixture-marker reopens. This is a bound for investigation, not completed check removal, a native timing, or an implementation approval.

### Pre-publication candidate — nested Git marker case on Windows

**Owner planning authorization, 2026-11-25.** In the exact native x64 synthetic Windows observer, the strict snapshot refused the lowercase marker, but walked two case variants and included their files. The selected-path verification refused all three spellings when that check was enabled. The ordinary directory control remained readable. Keep detailed original test outputs with private evidence. Record the inconsistency as a pre-publication correction candidate.

Proposed scope is the Windows observer's nested marker classification. Align its strict snapshot with the existing case-insensitive selected-path rule while preserving the registered structural boundary and normal directory behavior. In plan review, cover recognized root Git metadata, nested marker variants, unrelated dot-names, independently registered boundaries, stable refusal reason, and Windows x64 application and no-publication effects when a relevant snapshot rejects. Consider alternate Windows name aliases separately only if evidence warrants. Obtain a new R0 and Owner implementation approval before changing the product. Driver estimate 1.5–3 elapsed hours for the narrow plan, correction and focused verification with a ready device, with a proposed four-hour cap. Broader marker alias or sharing-policy changes would require their own plan.

### Evidence and cleanup checkpoint

The first Job stopped after a fixture preparer rejected an installed Git executable with two links. An independent follow-up used the existing verified Git selection route and finished normally. Neither Job left active processes or output pipes. The Windows operator removed 34 synthetic files, 98 synthetic folders and an empty temporary folder. A read-only Git object and its seven containing directories were retained after the existing permissions produced Win32 5. The prior evidence and runtime identities matched. The read-only supplement confirmed the existing index digest.

### Remaining native cases and disposition

The supplemental check ended at 18:33:32 KST, within the original device allocation. The Windows executor treated the three remaining live reproduction cases as a safety boundary and returned a read-only review of preserved evidence. Tool output did not establish a distinct automatic approval rejection. The referenced digests were checked. No additional native Job or synthetic test case was created.

| Case | No-hold positive control | Current masks | Candidate D only | Candidate chain |
| --- | --- | --- | --- | --- |
| Temporary replacement and restoration | Unrun | Unrun | Unrun | Unrun |
| POSIX-semantics rename | Unrun | Unrun | Unrun | Unrun |
| Junction with a held path | Unrun in this round | Earlier observer refused the reparse state even after the earlier test could create it | Unrun | Unrun |

No new Win32 or NTSTATUS values exist for these cases. The earlier junction evidence concerns the earlier mask and fixture. It cannot be applied to the candidate chain. The ordinary changes in the initial matrix remain useful for the tested local synthetic tree, and the absence of proof for the three cases prevents a pass on continuous registered-directory identity. The four conditional relative-open checks stayed closed, including the ordinary/private link comparison and DACL negative control. No symlink trial, performance measurement or product modification was made.

The first two native Jobs closed with no active processes and EOF on both pipes. The earlier synthetic Git object reported read-only Win32 5 and remains with its containing directories. The receipts, checksums and native raw files stay in the designated evidence locations for the Owner decision and potential F7 qualification. The read-only supplement did not change them.

## Result and next separate decisions

- Keep the relative-open proposal on hold. Further design or native qualification requires separate disposition of the missing safety cases and routine directory-change behavior. No implementation estimate is assigned before that gate.
- Keep same-object reopening independent. Any new F6 proposal needs an independently justified path-binding check, a bounded native directory-open control and R0. The measured window supports conclusions about the tried operation only.
- Review the registered Windows marker-case correction first if proceeding to another code task. The estimate applies to the focused candidate described above. This round closes with two approved previous-phase commits on draft PR #90, and two local development document edits for Phase F and the F7 candidate.

## Owner acceptance — 2026-11-25

The Owner accepted the bounded Phase F result. A list-directory handle on the tested chain blocked the four ordinary directory mutations in the case matrix. The three unexecuted cases remain unresolved after the native safety hold. Keep the retained evidence without replaying those cases. F6 remains deferred and any proposal must preserve the independent pathname and ancestor observations. The Owner selected the Windows marker-consistency candidate for the next bounded correction, including the macOS port if the same behavior is verified.

### Relative open after publication

The Owner deferred the relative-open family until after publication. Reconsider only with new acceptable evidence for continuous registered-path identity, the previously unexecuted conditions, Git and editor directory-change compatibility, and retained path and leaf checks. This intake adds no implementation or publication approval.
