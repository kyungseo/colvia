# Independent document entry and roadmap guidance

Owner: human project owner. Driver: Codex. Started: 2026-11-23.
Status: completed and accepted by the Owner on 2026-11-23. Local commit authorized; main integration and publication remain withheld.

## Purpose, authority and baseline

Reduce the effort needed to start using Colvia and understand its current behavior without adding features. On 2026-11-23 the Owner authorized the reviewed three-item, five-file plan, both mandatory review corrections and the recommended optional improvements. Keep the reviewed English and Korean README wording exact. This record owns execution and the separate, previously added authoring example; the completed [installation guide task](CHORE-20261123-001-installation-guide-flow.md) remains closed.

Baseline: `8f0d013d40e53b604d422d792a8473d3ba14469b`. The only pre-existing tracked change was the authoring example in `user-documentation.md`, with file SHA-256 `87992677cd027000112598c7e1e67087cfb5260529cc3469a45accc7f1b52555` and tracked diff SHA-256 `1a2841fe978b553ada8f90e88a0010d7323ba906466caec283a4879b81a697ea`. The reviewed five-file proposal SHA-256 was `e7916c57f7b5104eca036a136b3e502b6247f973800dd7957137175136246798`. The original packet and verbatim response remain in the private review evidence; their exact identity and public-safe dispositions are recorded here. No private path is needed to understand or apply this plan.

## Scope and preserved meaning

| Item | Files | Authorized delta |
| --- | --- | --- |
| D1 | `manual/en/README.md`, `manual/ko/README.md` | Replace the first three numbered items with purpose-based choices, installation first; name who decides what in both languages. Preserve destinations, headings, images and all other guidance. |
| D2 | Root `README.md`, `README.ko.md` | Replace only the third roadmap bullet body with the reviewed current-query/future-presentation distinction. Preserve the headings, all other text and exact bilingual wording. |
| D3 | `docs/MAINTAINING.md` | Add one introductory paragraph locating current source development and the earlier-profile code map. Use source path names rather than links to files absent from the earlier-profile inventory. Retain the local evidence-selection link and all existing content. |
| Separate existing example | `docs/development/user-documentation.md` | Preserve the registered Before/After pair. Explain the actual Before wording, clarify the local use of “버전” versus established “판”, and remove one extra blank line. |
| Record and navigation | This record and `docs/development/README.md` | Establish one owner and add one index link; do not modify another task’s progress. |

The example is a sixth content file, not hidden inside the five-file proposal. This record and its navigation link are two additional administrative files. No runtime, adapter, installer, dependency, approval, storage, support or command changes. Parallel and pseudonymization implementations, demos, installation, publication and the previously deferred optional first-connection findings remain outside this batch.

Invariants: existing query and future presentation remain distinct; future wording remains exploratory. The roadmap does not claim an existing single-screen view or persistent storage of later explanations. Conditions, actors, decisions, link destinations and command blocks remain unchanged outside the named deltas. The example does not establish a project-wide terminology replacement.

## Review disposition and Owner authorization

The manual review response SHA-256 is `c62c28df313eac6997a4efc6767f8958aca79399cde6a8b752e19574de1e63c5`. Reviewer: Claude Opus 5.5, same session as earlier first-connection reviews. D1–D3 and the authoring example were new to that reviewer; the already accepted ten-page wording check had limited independence. Findings were static; the reviewer ran no product tests or reproduced counterexamples. The six request input files and tracked diff identity matched before implementation.

- R1 accept: MAINTAINING is absent from the current Preview bundle but present in seven literal earlier-profile managed inventories and the official sets derived from them. The earlier-profile builder uses its source bytes. Replace the two new off-inventory links with source path names and check the retained page-local anchor in both contexts. Do not retire earlier-profile packaging as a workaround.
- R2 accept: explain “당시 남긴 말” from the actual Before example, then separately caution against confusing decision statements with progress notes.
- AS1 accept: restore the explicit decision actor in the Korean manual index, matching the existing English meaning.
- BS1 accept: explain that “버전” follows this README wording while other submitted-revision references keep “판”.
- BS2 accept: remove the single extra blank line before the example heading.
- AS2, AS4 and AS5 defer: retain the reviewed English tutorial label, English roadmap wording and existing history-link placement.
- AS3 not selected: retain the Owner-selected README term “버전”.
- Existing accepted ten-page result and deferred O1/N1/S2–S5 remain unchanged.

The Owner explicitly authorized the above implementation and verification after receiving the review. This is execution authority, not acceptance of the resulting bytes or permission to commit, merge or release.

## Verification selection and limits

Use the smallest checks that cover changed prose: exact delta and reviewed README byte comparison, GFM rendering, source links/images/anchors, preserved fenced blocks and headings, the earlier-profile installed link context, an allowed-path check and `git diff --check`. Compare both languages for the selected actor, destination and current/future distinction. Check added public text for private paths and identifying external-comparison provenance.

All five proposed pages are absent from current Preview guide sources. MAINTAINING is nevertheless an earlier-profile managed document; rebuilding that profile would change its bytes and inventory digest. Its new paragraph adds only one page-local hyperlink. Validate this against the source inventory and mapping without generating a package or installing a runtime. No executable, package-map or command bytes change, so a full runtime or bundle-suite rerun is not selected. Prior package PASS results remain evidence only for their prior inputs. Actual packaging, installation, native platforms and external URLs remain unverified in this task.

Expected execution: 10–20 minutes; cumulative stop limit: 30 minutes, excluding Owner/reviewer waiting, Git actions and demo work. These are planning judgments, not measured performance. Stop for unexplained drift, a failed check requiring wider changes, or the time limit. Reversal is limited to this document diff, preserving the pre-existing example and all prior accepted work.

## Progress and remaining decision

Implementation began from the verified baseline. Record and history lookup found `001` as the only used development sequence for this date in the current files and available Git history; `002` was selected without reusing an existing record. Validation results are recorded below. R1 recommends acceptance; Owner acceptance remains pending. No commit or integration is authorized.


## Applied result and validation — 2026-11-23

Applied D1–D3, R1/R2 and AS1/BS1/BS2. The root README pair matches the reviewed candidate byte for byte: Korean SHA-256 `2456d20a20eed5a8f709cb9eb34bcf94537c6c942cf91cbe8f0fcce4890b20c1`; English SHA-256 `ea9923e6724909bfa83c55c6b0f2a4646d47dd34bf9c7fb308b585b0606f3f3e`. Each README has exactly the one reviewed roadmap bullet replacement. No additional README suggestions were applied.

A focused artifact checker (`verify-independent-docs.cjs`, Node.js v18.20.5, with Python standard-library AST inspection) exited 0. It replayed the original five-file proposal in memory with only the authorized R1 and AS1 corrections and compared each resulting file with the applied bytes. It also checked:

- Eight changed documents render with GFM without literal emphasis markers outside code.
- 230 local references resolve: source content, this record and its new index link, plus the new MAINTAINING paragraph in seven earlier-profile inventory contexts. Existing unrelated development-index references were not re-audited.
- Both README candidate hashes match; the authoring example’s After equals the Korean roadmap body. Existing headings/anchors and fenced code blocks survive.
- The seven literal earlier-profile inventories contain MAINTAINING and exclude the two off-inventory destinations from the original proposal. The source mapping leaves MAINTAINING unchanged. Its new paragraph has only the existing page-local evidence-selection link; no off-inventory hyperlink remains in that paragraph.
- Changed paths are limited to six content documents, this record and its index link. The staged diff is empty. Added source text contains no private local paths or reviewer session identifier. No code or package-map files changed.
- `git diff --check` passes.

The bilingual reading confirms three optional learning purposes and the same decision actor, current history-query capability and exploratory single-screen improvement. The example explanation now refers to its actual Before text and confines “버전” to this wording. The existing first-connection acceptance, safety conditions and deferred items are preserved.

These are executed static document checks and a Driver semantic assessment. No product test suite, package build, installation, native-platform exercise or external URL request ran. The corrected earlier-profile link is checked against the declared inventory, not a newly generated or installed archive. Actual package bytes would be checked if that profile is rebuilt. No earlier test result is presented as a run on this candidate.

The focused checker remains in the private task artifacts for the near-term result review and any authorized correction; reassess retention after result acceptance. The verbatim prior review and original packet remain there for the same review. No full source snapshot or rendered-page archive was created.

The later Owner acceptance and local-commit authorization are recorded below; main integration remains withheld.


## R1 result review and Driver disposition — 2026-11-23

The Owner relayed the manual R1 response. Response SHA-256: `43f5abc11f21fe3680e3eb96e122e8018b4f24f17d438f3fe348287f2708d5d7`. The Driver verified all 13 requested file identities, the tracked diff identity and the unchanged HEAD before recording this result. The new record was separately identified because it was untracked. The verbatim response is retained in the existing private review record, separately from these dispositions and any Owner decision.

Reviewer: Claude Opus 5.5, the same session that proposed the corrections. The Reviewer recommends acceptance with no mandatory findings. This is a check of that session's own proposals, with limited independence for detecting flaws in those proposals. No new reviewer session was invoked by the Driver.

The Reviewer directly ran the authorized `verify-independent-docs.cjs` once from the task checkout under the specified 30-second bound: Node.js v18.20.5, exit 0, eight rendered documents, 230 local-reference checks, seven literal inventory contexts and two exact README matches. The script used Python standard-library AST reading. This is an independently executed static check in the same review session, not a product test, package build, installation or native-platform qualification. No external URL access occurred. Input and tracked diff identities matched at the beginning and end of the review.

Driver dispositions:

- R1-N1 accept, record only: qualify the earlier count as seven literal inventories plus the official sets derived from them. The checker covered the seven literal declarations; no expanded execution coverage is claimed.
- R1-N2 accept, record only: the Reviewer read all added text and found no identifying external-comparison information. This is a manual reading result, separate from the checker's private-path and session-identifier pattern check.
- R1-N3 accept, record only: replace the stale future-tense validation sentence with the completed state and update the pending decision to Owner acceptance.
- Follow-up observation: the Korean README's existing “어떤 버전을 보고 수락하거나” and “그때 수락한 버전” wording remains an exception to the example's general “판” advice. Reconsider only when the Owner selects a future README terminology pass; retain the frozen README pair now. This is not a new acceptance condition.

Only this development record changes after R1. The six content documents, index link, checker and original review inputs in the artifact directory remain unchanged. The reviewed record's pre-update SHA-256 was `cfab70357d3ad419cd325c5796c4d6791c08b4ec7d9a6842ac9d77b28f58cdb6`; these optional record corrections are the declared post-review delta. A record-only GFM/disclosure check and source `git diff --check` cover this update; no product or full document-check rerun is needed for these prose-only record corrections.

Owner state: receipt of the Reviewer response is not result acceptance. Acceptance remains pending. Commit and main integration remain explicitly withheld. Retain the active checkout and review inputs for the concrete acceptance and subsequent authorized integration work; no cleanup or source-path migration is performed here.


## Owner acceptance and closeout — 2026-11-23

The Owner accepted this result, including the record-only R1 dispositions, and explicitly authorized the local commit. Main integration remains on hold. This dated decision supersedes the earlier pending-acceptance and commit-withheld states; it does not rewrite those historical observations. No push, PR, merge, release or adopter change is authorized here.

Completion criteria are met for this bounded task: purpose-based manual entry, exact reviewed bilingual roadmap wording, source/earlier-profile maintainer entry, the corrected authoring example, one owning record and one index link. The Driver's focused checks and the Reviewer's executed R1 check remain valid for unchanged content. The acceptance update changes only this record; final record rendering, disclosure, unchanged-content identity and diff checks are selected instead of repeating the product or full document suite.

Tracking finalization: this record owns the accepted result; its existing index link needs no change. This source repository uses the development index and this record rather than a separate STATUS update. No other task is closed or reopened.

The existing task checkout is retained for the concrete next work: sharing-readiness planning, Mac/Windows demos and later Owner-authorized main integration. The private review inputs, responses and focused checker remain for the pre-integration evidence audit; the checker is tied to its original baseline and pre-commit layout, so its earlier PASS is not a claim that it can run unmodified after this commit. Reassess these files after that audit; there are no generated package fixtures or rendered-page archives from this task to remove now.

Remaining work belongs to subsequent scopes: sharing readiness and demo media; the deferred README terminology observation and earlier optional guide findings; implementation-dependent parallel/pseudonymization guidance after those implementations finish. This closeout does not mark those items complete. The next action authorized in this turn is to arrange the sharing/demo sequence, not to install, record, publish or integrate main.
