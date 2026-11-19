# Result review of Colvia's documentation language changes

On 2026-11-19 the Owner explicitly waived the separate plan review (R0) for this already-edited documentation change and approved one result review (R1). The practical reason was to check the finished translations against their originals before acceptance. The R1 review itself did not decide acceptance or publication.

## Review inputs and limits

Codex supplied the patch against `eed271ad5aa665f0002c9eded69d82f224da9ce0`, plus both new index files. Claude reviewed the Korean-to-English changes for authority, binding, refusal, recovery, obligation strength, and the distinction between requirements and observations. It also reviewed how the language conventions treat historical evidence.

- Tracked diff SHA-256: `1ca50e23cf6189278d94fe49d5fd68fffca8be8b9790b97d301b3310be918111`.
- Complete packet SHA-256: `28c4eecc34243b2f1f5ac32b32ea7fadff7e62d91a9d9483866b6626d75bec57`.
- New index `docs/development/record-foundation/README.md`, SHA-256 `5f0b346a3c49dd891002177c4a50e018c33da2e9626903ff9ee61d26300a1a8a`.
- New index `docs/development/verification/README.md`, SHA-256 `38c321af9c78ab59d7a9c828cdbadaa617236a24e08893679df35ddc222caec0`.

The reviewer used a fresh Claude Pro subscription CLI session, model `claude-opus-5-5`, session `f9ba00f8-831e-418c-8056-7cb4d2f9255c`, for 167.1 seconds within the 420-second limit. It had no tools and saw only the packet. The Driver checked the base, tracked diff and all 15 file identities after the round. The reviewer did not reproduce earlier link, rendering or archive checks.

## Driver disposition at the end of R1

- H1 — accept the mixed-purpose page ambiguity; needs Owner decision on adoption of corrected text. The five pages contain maintained explanations as well as historical passages. The Owner already authorized translation of maintained sections; that instruction did not adopt the exact English wording. Prefer an explicit rule for sections, link to the precise original revision and preserve dated decisions, review inputs and observations. The packet used for this review is pinned above. Earlier review packets must retain their original identities.
- M1–M13 — accept for correction against the Korean source. Preserve the original release conditions, the user's review of a new baseline, delegated acceptance and restrictions on writes. In particular, permission to make an explicit new connection must not become a requirement to do so. Source or elevated-mode checks must not count as the installed/default-mode checks they cannot establish.
- Low findings — accept the suggested precision edits in the five technical pages. Use a generic agent-entry label unless exclusivity is documented. Clarify where the new writing conventions are authorized without implying that an older decision adopted them. The reviewer raised the activation and live fragment points as questions, not as established failures.
- Keep the prior checks for package links, rendered tables and old fragments scoped to their original inputs. A live Pages language-switch check was not performed in this review.
- Status: changes required on the reviewed revision. Corrections and Owner acceptance are pending. No second review occurred.

## Driver verification after R1 (2026-11-19)

The Driver corrected the five maintained English references against the original revision and updated the language convention and both navigation pages. The R1 verdict applies to the reviewed input. Owner acceptance followed the Driver checks and is recorded below.

| Finding | Resolution |
| --- | --- |
| H1 | The convention now applies by section. Each mixed-language page links to its exact pre-translation revision. The dated originals govern the historical claims. The earlier R2 input for the runtime document remains identified by its recorded SHA-256 prefix, `0ec401056b35`. |
| M1–M6, M13 | The runtime reference distinguishes required coverage from actual support and completed tests. It restores the installation and default-permission gates, per-platform acceptance and the restriction on using agent transcripts or session IDs as authority. |
| M7, M9–M12 | The connection proposal identifies who reviews a new baseline, permits an explicit new connection when identity cannot be proven, preserves the distinct file/Git refusals and places automatic transitions in the follow-up. |
| M8 | The structure reference retains the prohibition on substituting a model judgment or click for Core acceptance, including when the existing delegated-acceptance contract applies. |
| Low findings | Corrected the concurrency, validation, launcher, WSL and dependency wording. The docs index identifies the shared agent entry, and the ownership map explains its language conventions without activating a technical decision. |

The Driver checked the five original revision links and retained heading targets, the generated earlier-profile links, and GFM rendering of all eight corrected pages. The other seven review inputs matched their R1 hashes. The official downloads HTML contains both language targets and selects Korean for `#ko` and English for `#en`. The response below is preserved byte for byte. These are Driver checks; there was one Claude result review.

## Owner acceptance

On 2026-11-19 the Owner accepted the corrected documentation and the English wording of the five maintained references. Their linked originals remain authoritative for dated decisions and observations. This decision covers the documentation only.

## Reviewer response (verbatim)

# Colvia document-language change: result review R1 (static)

**Basis:** base `eed271ad…`, tracked diff `1ca50e23…`, and the candidate hashes as supplied. I reviewed the diff text only. I made no edits and ran no tools or tests.

## Verdict

**Changes required.** The new language rules, entry pages, tutorials and indexes are sound. The five record-foundation pages are the problem.

1. **Placement conflict.** They replace Korean originals in place. That conflicts with the change's own rule for dated material, and nothing adopts the translations.
2. **Meaning changes.** Several English sentences alter the meaning in exactly the areas the brief names: approval authority, binding or scope, refusals, recovery, normative strength, proposal versus requirement, and observed versus unverified status.

Resolve H1 and the Medium findings before this proceeds to acceptance. The Low findings can be fixed in the same pass.

## Evidence classification

- **Static findings:** everything below comes from comparing the old and new text in the diff.
- **Test evidence:** reused from the driver as reported (links and rendering). I did not repeat it.
  - The driver's check does not show that the external fragments `colvia.github.io/downloads/#en` and `#ko` exist on the live site. I have not checked them either. Treat them as unverified unless the driver's report covers them.

## High

**H1. Korean originals replaced in place without adoption**

- **Files:** all five record-foundation pages, `document-ownership.md#document-language`, and `record-foundation/README.md`.
- **What the new rule says:**
  - Preserve the original language of "accepted decisions, dated plans, reviewer responses…".
  - "A dated update to an older file can use English under its own heading."
  - "A translation is a summary unless it has itself been adopted."
- **What the diff does:**
  - `connection-edge-scope.md` is itself labelled "2026-11-06 Driver 범위 제안", a dated proposal. Its body is rewritten in English in place.
  - `runtime-and-extension.md` keeps its status line "…다음 집중 리뷰 패킷은 이 문서를 입력으로 참조한다". Its body text changed, so the next review packet's input has changed too.
  - The Korean status lines and some Korean paragraphs remain. The page now reads as if the English body were the adopted text.
- **Changed meaning:** canonical design and requirement text is now an unadopted translation, and the Korean source is visible only in git history.
- **Root cause:** the rule has no row for existing, still-maintained design pages.
- **Minimal correction (either):**
  - **(a) Adopt the translations.** The Owner records that these five pages are current maintained references and adopts the English text. Add a rule row allowing in-place conversion for such pages. Add a one-line note per page citing base `eed271ad` as the Korean original.
  - **(b) Restore the originals.** Restore the Korean bodies and add the English under a dated heading.
  - **In either case,** the review packet that cites `runtime-and-extension.md` must pin a hash or the base commit.

## Medium

| # | File / section | Old (excerpt) | New (excerpt) | Changed meaning | Minimal correction |
|---|---|---|---|---|---|
| M1 | runtime-and-extension / Platform targets | "아래 표는 목표를 고정하며 아직 상위 제품의 지원 여부나 시험 완료를 주장하지 않는다" | "records the intended coverage at the time" | Binding current targets become historical intent. The disclaimer "no support or test-completion claim" is lost. | "The table below fixes the targets. It claims neither upstream support nor completed tests." |
| M2 | runtime / Implementation req. 6 | "…충돌하므로 기본 경로로 확정하지 않는다" | "R1 proposed storing under `.git`, which conflicts…" | The operative decision (not confirmed as the default path) is dropped. | Append "It is not adopted as the default location." |
| M3 | runtime / Completion criteria; Final matrix row 1 | "선행 근거이며 실제 배포 경로 완료를 대신하지 않는다"; "실제 새 사용자 설치를 대체하지 않는다" | "provide preliminary evidence"; row 1 has no non-substitution clause | Observed versus unverified: local, source, mock and synthetic runs no longer explicitly fail to satisfy completion. | Restore both "does not substitute for…" clauses. |
| M4 | runtime / Req. 7 | "추가 권한을 받았으면 기본 앱 모드 통과로 기록하지 않는다" | "Record any additional diagnostic grant separately" | Status rule weakened: a pass under an extra grant is no longer barred from counting as a default-mode pass. | "A diagnostic that received additional access is not a default app-mode pass." |
| M5 | runtime / First-release UX | Heading "공개 전 갖춰야 할…"; "이 설치 부담 해소는 첫 공개 조건이다"; "일반 사용자 경로의 대안으로 떠넘기지 않는다" | Heading "First-release user experience"; "Document running from source separately for contributors" | The pre-release gate is softened, and the ban on offering the source path to ordinary users is lost. | State "This is a release condition." Add "Source runs are not an alternative for ordinary users." |
| M6 | runtime / 12 combinations | "플랫폼별 최종 수락은 별도로 한다" | "Accept each platform independently." | The imperative assigns acceptance to whoever reads the page. Owner authority becomes ambiguous. | "Final acceptance is recorded separately for each platform." |
| M7 | connection-edge-scope / Files or branch change | "사용자가 새 기준을 검토하여 새 Work로 이어간다" | "…or review a new baseline for a new Work." | The approving actor (the user) is dropped. | "…or the user reviews a new baseline and continues in a new Work." |
| M8 | structure / Capability adapters | "Core 수락을 모델 판단이나 알림 클릭으로 대체" (prohibited) | "Acceptance in Core requires the human decision." | Adds a requirement. It may conflict with delegated acceptance (concurrency case 7, "수락 위임"). | "A model judgment or notification click cannot substitute for acceptance in Core." |
| M9 | connection-edge-scope / Criteria; Git-status follow-up | "드문 전환을 자동 처리하는 기능은 따로 만들지 않는다"; follow-up "자동 전환하고 활성 Work까지 이어주는 전환 도구" | "Automatic resolution is a separate capability"; "Transition the same logical project…" | The first-release exclusion of automatic handling weakens. The follow-up loses "automatic", so the line between first release and follow-up blurs. | "The first release does not build automatic handling." Make the follow-up "An automatic transition tool that…". |
| M10 | connection-edge-scope / Git missing paragraph | "기록 보존과 명시적 새 연결까지만 허용한다" | "preserve the records and require an explicit new connection" | A ceiling (only these are permitted) becomes a mandate. | "…permit only record preservation and an explicit new connection." |
| M11 | connection-edge-scope / External changes | "자동 checkout/reset/stash, 사용자 파일 덮어쓰기, 기준점 교체로 해결하지 않는다" | "Do not automatically check out, reset, stash, overwrite user files or replace the baseline." | "Automatically" now also qualifies overwriting user files and replacing the baseline, which narrows those refusals. | "Never resolve by overwriting user files or replacing the baseline, and never check out, reset or stash automatically." |
| M12 | connection-edge-scope / Min. case 4 | "정본을 손상으로 오인하거나" | "do not misdiagnose a corrupt authority" | Mistranslation. The original means "don't mistake a sound authority for a corrupt one." | "…do not misreport the authority as corrupt." |
| M13 | runtime / Capability paragraph | "결과 schema는 … transcript나 session ID를 필수 권위로 삼지 않는다" | "…can supply provenance." | The schema prohibition is lost. Only the permissive half remains. | Add "The result schema must not require them as authority." |

## Low

- **concurrency / intro:** "직렬로 두더라도" (even if serial) became the assertion "Serial execution in the first release…". Restore the conditional "Even if…".
- **concurrency / intro:** the clause "범위 claim … OS 접근 차단이 아니다" (a claim is not an OS access block) was dropped. Restore it.
- **concurrency / Case 5:** the pass criterion "구별한다" (distinguish) became "Exercise…". Add "…and distinguish them."
- **concurrency / Case 7:** the ban on labelling retained Works as automatic parallel success became a descriptive sentence. Restore "must not be reported as…".
- **connection-edge-scope:** "분류하지 않는다" (do not classify) became "Avoid attributing". Restore "Do not attribute".
- **validation / Phase 1:** "아직 새 store를 선택하지 않는다" became "still uses the previous store", which asserts that a previous store exists. Use "does not yet select the new store."
- **validation / Phase 5:**
  - "전체 관련 회귀" (all relevant regressions) became "Select the relevant…". Use "Run all relevant…".
  - "필수 항목으로 포함" (include as mandatory) lost "mandatory".
  - "필요한 조작과 이유만 짧게 보여야 한다" (must show only the needed action and reason, briefly) became "should give…".
- **validation / intro:** the sentence "기존 테스트를 모두 그대로 실행해 통과시키는 것이 목표는 아니다" (passing every existing test unchanged is not the goal) was dropped. Restore it.
- **validation / Plan mode:** "조회·계획 제시만" (only query and propose) became "may query and propose". Restore "only".
- **runtime / Launcher:** "Codex 앱·CLI와 Claude Code 데스크톱·CLI마다 다른 … 규칙을 두지 않는다" means one set of rules across all four forms. The new sentence can be read as per-product only. Use "All four host forms use the same…".
- **runtime / WSL:** "Block unverified writes…" reads as filtering only unverified writes. Use "This path is unverified. Block writes through it and explain."
- **structure / Layers:** "고정한다" (fixed as a decision) was dropped, and "The user interacts with several layers" was added. Restore "This dependency direction is fixed."
- **docs/README.md:** `AGENTS.md` is now labelled "Codex instructions". Confirm it is Codex-only. Otherwise keep "Agent instructions".
- **document-ownership.md:** the page header says the map "locates existing rules; it does n…" (truncated in the packet). The new section adds normative conventions. Confirm it is consistent with that header and with DR-0006's activation condition, or cite the authorizing decision.

## No change needed

- `CONTRIBUTING*.md`, `user-documentation.md` and the tutorials (subject to the external-fragment note above).
- `development/README.md` and `verification/README.md`.
- The retained Korean anchors on renamed headings.
- The retained Korean status lines, evidence paragraphs and Owner-confirmed passages, including "Owner 확정 요구" and the current Codex evidence paragraph in validation.md.