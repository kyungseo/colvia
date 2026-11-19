# Implementation Regression Map

Status: 준비한 의미 기준 목록. 기존 코드와 테스트를 읽고 분류했으며 새 형식에서 시험을 실행한 결과가 아니다. R1 패킷 고정 이후 독립 준비 자료로 작성했다. R1 입력 파일을 바꾸지 않았다.

English reference, 2026-11-19. The [original wording at the translation base](https://github.com/kyungseo/colvia/blob/eed271ad5aa665f0002c9eded69d82f224da9ce0/docs/development/record-foundation/validation.md) governs the dated decisions and evidence. The Owner [accepted this English reference](../document-language-result-review.md#owner-acceptance).

The compatibility baseline is the behavior to preserve. The earlier installation and byte format are outside that baseline. Use the checks below to establish whether the new structure preserves each behavior. Passing every existing test unchanged is not the goal.

| Area | Behavior to preserve | Reusable evidence | What to check in the new format |
| --- | --- | --- | --- |
| Ordinary Work | Approve scope, edit, check and submit, then let the user accept the result without redundant approvals. | ordinary_work, general_work_invariants | Separate UUID and title, preserve before/after bytes, verify SQLite commit and CAS. |
| Scope | Keep changes outside the approved file paths out of the result. | general_work, trial_usability | Compare the full trie diff with the scope claim. Reject unrelated concurrent edits. |
| New chat and multiple Works | Find the exact Work, compare the result with current files and keep each Work’s state independent. | ordinary_work, trial_usability | Query the target's required references. Cover identical titles with different IDs and missing or corrupt bodies. |
| Exact file bytes | Distinguish CRLF, binary data, deletion, mode and path aliases. | worktree_checkout_bytes, general_work | Preserve bytes independently of text display. Check the large-body bound. |
| Revision and revocation of acceptance | An earlier acceptance cannot transfer to a new result. | general_work_recovery | Immutable events, new heads, replay, interruption and concurrent CAS. |
| Child Works, worker and umbrella | Distinguish child acceptance from integrated acceptance. Require explicit authority to apply or integrate. | worktree_execution, umbrella | Shared database, results scoped to each workspace and existing bounded application semantics. |
| Candidates and follow-ups | Selection gives no authority to execute. Distinguish a completed result from the next action. | candidates, continuation | Separate typed tables/references and no duplication on replay. |
| Competing writes | Two competing acceptances or selections cannot both publish. | worktree_process_safety, continuation_process | `BEGIN IMMEDIATE`, CAS and transaction fault injection. |
| Handoff and notification | Distinguish execution, submission and notification effects. Resolve the original result and its current state. | Earlier delivery and receiver evidence | Bind the new locator to the Work ID. Cover duplicates, late responses and unknown effects. |
| Optional execution and safeguards | Preserve execution authority, scope, cancellation and unknown outcomes. | official_execution, official_faults | Use capabilities in place of earlier profiles and retain access to previous run history. |
| Connection, update, recovery and disconnection | Preserve project rules, settings and records, including after failure. | productization_safety, workspace | Use the first public version as the baseline for compatible/incompatible updates, capabilities, rollback, repair and disconnection. |
| Source and installed documentation | Provide paired user guidance, a short agent entry and links that resolve inside the package. | source_layout and earlier documentation checks | Check current commands and capabilities. Exclude earlier profiles and source-development instructions. |

## Deliberate Non-regressions

- Earlier JSON bytes, window/profile names, absolute path bindings and the legacy migration/update chain are outside the preservation target.
- Avoid reproducing guidance that exposed internal paths or approval tokens on every command or requested unnecessary approval.
- Record a product decision before removing a feature. A reduction in line count alone cannot justify its removal.
- For multi-file writes replaced by SQLite transactions, verify equivalent or stronger externally observable interruption and concurrency guarantees. The earlier write sequence itself need not be reproduced.

## Phase Gates

1. Schema, typed references, hashes, trie and store. Test malformed input, unknown versions, exact limits, duplicate paths, corrupt or missing objects, rollback and stale CAS. At this stage the product connection does not yet select the new store.
2. Context and observation. Cover common-dir identity, non-Git folders, registered nested worktrees, raw policy versus structural boundaries and the D1/D7 negative cases. Reuse filesystem and SQLite policies at this layer.
3. Ordinary Work end to end. Exercise new connection, writing, review, acceptance, resumption and historical body lookup with small and large Work counts. Compare against the earlier synthetic scale measurements and assess performance and correctness separately.
4. Remaining capabilities, lifecycle and platforms. Switch public packaging after meeting each feature's prerequisites. Only list features connected to the product in the support table.
5. Run all regressions relevant to the combined changes and review the results. Qualify real OS installation, clicks, user/model interaction and the public delivery path separately.

제품 소스 작성은 R1 구조 처분 후 시작한다. 이 준비는 테스트 실행이나 제품 완료를 뜻하지 않는다. 기존 dirty checkout은 그대로 두고 별도 worktree에서 구현한다.


## Managed Runtime And App Permissions Gate

Require the [runtime verification matrix](runtime-and-extension.md#최종-검증-행렬) when qualifying connection, update, recovery and the installed product. Check first setup without personal Python settings and selection of the same dedicated launcher in apps and CLIs. In ordinary Git and non-Git folders and linked or nested app worktrees, distinguish runtime read/execute access from project and authority/journal writes. Source and synthetic runs do not qualify the installed app sandbox. Reuse earlier passes and failures within their version and scope. Focus new checks on changed boundaries. Verify record, setting, body and acceptance-history preservation through normal updates and failure recovery. Diagnostics must briefly show only the action needed and the reason for it.


<a id="codexclaude-권한-모드별-접근승인-경로" name="codexclaude-권한-모드별-접근승인-경로"></a>

## Codex and Claude host approval modes

This check incorporates record-directory access under Codex approval requests. Verify that the user can finish the task through the chosen approval flow. Reuse feature checks where their conditions match.

- For Codex, check the host's request-approval and approve-for-me modes. For Claude, check manual approval, automatic acceptance of edits and automatic mode. Verify availability and actual approval, tool and file access on the specific host version before making claims about equivalent permissions or support.
- Run the same Colvia command via each applicable approval flow. On denial, the action must not execute or change existing files or records. Record the effective scope of ordinary command approval separately from additional write access to a specific folder. Full access is not required.
- Reuse edit, submission and resumption evidence when launcher, effective permissions, tools and workspace match and only the approval interaction differs. Add a minimal behavior check for each material difference.
- Within its granted access, plan mode may only query and propose a plan. It must preserve files and Colvia records. Check that work can continue after entering an execution mode and obtaining the required approval. A write restriction in plan mode is expected.
- Host tool permission and automatic edit approval cannot approve a Colvia scope or accept a submission. Distinguish human decisions from tool approval counts. Record repeated prompts and whether the instructions were clear.

현재 Codex 근거의 정확한 범위: 승인 요청의 새 대화에서 설정한 기록 폴더 쓰기 권한이 반영되지 않은 것은 관측했다. 명령 실행 시 사용자 승인으로 진행 가능한지는 아직 미확인이다. 설정 미반영을 곧바로 사용 불가로 판정하지 않는다. 기존 성공·실패는 당시 조건 그대로 보존한다.

For each observation, record the host and version, available mode, effective policy, launcher and location, approval or denial, actual access, file and record preservation, approval count, basis for reuse and unresolved differences. Exclude accounts and tokens. Recording the criteria does not authorize new settings or model runs.


## Distribution Entry And Adapter Extension Gates

- Start first installation and update with the documented platform command at the intended public address. Check automatic asset verification, runtime preparation, compatible binding selection and recovery. Requiring the user to assemble a Python ZIP, hash and profile leaves the ordinary entry incomplete. Actual publication needs separate approval.
- Record upstream availability and verification separately for all 12 combinations of macOS ARM64 and Windows 11 ARM64/x64 with Codex or Claude Code in a CLI or desktop app. Evaluate installation, permissions, first Work, result, notification and resumption separately. Include app access and linked or nested worktree observations in the preceding matrix.
- Use import checks and a minimal synthetic adapter to verify Core's independence from product names and OS APIs. Distinguish a missing capability, unconfirmed cancellation and mismatched result. This cannot establish Linux or future-agent support.
- Resume in both directions between Codex and Claude using the same authority. Verify that the same Work, retained result and acceptance history remain available. Adding an adapter alone must not require a store schema change or rewrite history.
- The [follow-up candidates](runtime-and-extension.md#후속-후보--현재-구현-제외) require later integration checks and are outside this implementation and execution scope.


## Desktop Cases And R2 Additions

Historical D labels name observed scenarios, not private documents required to run a test. See the [product evidence supplement](../product-evidence-and-followups.md) for inherited observations and [R2 disposition](review-r2-disposition.md) for corrections. The expectations below are future test criteria, not new passes.

| Case | Setup and expected behavior |
| --- | --- |
| D1 nested workspace | A host registers a linked worktree inside a primary checkout. Resolve its distinct workspace and shared authority; do not ingest its metadata into parent content. Foreign, orphan, aliased or racing boundaries are unavailable/refused, never silently excluded by a directory name. |
| D2 failed observation | A topology or access check fails. Show the actual boundary and next action, preserving unavailable current state instead of generic usage output. |
| D3 same-name folder | An app creates a different empty folder with the same display name. Identify the actual opened folder and connection; never reuse authority by title. |
| D4 repeated Git reminder | After an ordinary result is accepted, the agent creates a later candidate. Preserve agreed commit practice without repeated internal-path narration or implicit Git authorization. |
| D5 refused lookup | Verified lookup fails while raw records and a lock file exist. Raw inspection does not restore verified status, and file presence alone does not prove a live writer. |
| D6 preparation remainder | Interrupted connection leaves an empty staging directory. Only owned, unused, non-recovery content is eligible for cleanup. |
| D7 ignore drift | A host adds an exclusion for nested worktrees. Historical accepted bodies remain identifiable; submission equivalence needs proof of effects confined to validated structural boundaries, including newly created paths. |

Add concise/detailed View parity, partial/unavailable/corrupt state, title/ID separation and next-action correctness to semantic regression. Include a copied and a moved Git/non-Git root; exported settings/archived history; interrupted chunk import; bounded query delay during import; NFC/NFD/case/mode collisions; repeated ignore rules and removed negations; Git ref/index/content interruption pairs and hook handling; launcher/Git discovery; signed metadata tamper/replay/expiry/key transition. Exact protocols and numeric pass bounds must be fixed before executing their tests.

Bounded Codex desktop source probes now cover primary, sibling and nested workspaces with an explicitly enabled project-local permission-request feature and an exact, turn-scoped authority grant while retaining the base workspace mode; see [source checkpoint](source-checkpoint.md). Available-by-default access, installed managed-launcher behavior, permanent permission and real install/notification qualification remain separate. No test requires deleting a real authority: destructive restore cases use isolated synthetic copies.


## R2 detailed contracts and refusal oracles

[Implementation contracts C1–C8](implementation-contracts.md) and [RF-T01–36](refusal-map.md) extend the table above. IDs below name required test groups, not implemented or passing tests.

| Group | Required focused cases | Success criterion |
| --- | --- | --- |
| C1 / RF-T03,36 | Clone/non-Git copy, move, replaced root, stale epoch, sibling/nested worktree, denied narrow access | No accidental shared writes; explicit actionable unavailable status |
| C2 / RF-T01,04,06 | NFC/NFD/case aliases, binary/mode, reorder/delete/rebuild, overflow, unknown required kind | Same set has same root; unsafe path/materialization refuses |
| C3 / RF-T07,09,11,36 | Partial chunk import, disk-full/sync error, hot journal, same/different Work CAS, every numeric edge | No partial result, no lost updates, bounded busy result, no false corruption/completion |
| C4 / RF-T23–25,36 | Complete export, corrupt/truncated stream, restore binding, archived bodies/settings, disabled capability, rollback | Exact history/settings preserved; no automatic activation or replay |
| C5 / RF-T05 | Exact app exclude, negation/reorder/global origin, hidden new path, policy-edit union, orphan worktree | Scope protection remains complete or explicitly unavailable |
| C6 / RF-T12,13,36 | Partial/unrelated staging, hooks/filter, other checkout, O/I0, N/I0, N/I1, O/I1, external ref/index drift | Original index/content preserved unless precisely authorized; recovery classified, never guessed |
| C7 / RF-T21,22,31–35 | Managed entry identity, missing runtime, source/installed route, wrong arch, private-Python-free environment | One verified runtime; no silent PATH fallback or permission expansion |
| C8 / RF-T23,31–33,36 | Signed metadata rotation/replay/expiry, wrong target dependency, download/activation failure | Last valid runtime/data remains usable; no trusted-counter downgrade |

C1/C7 actual host tests and OS click tests belong to the later installed qualification matrix. Offline fixtures cannot pass those rows. Existing unknown-effect/process fixtures cover RF-T26–30 semantically, with new-store integration retested. Original failed/stopped measurements remain failed/stopped; they are not retroactively overwritten by this map.

Use [P0–P9](implementation-plan.md) for phased coverage and cost. The new format changes common storage/lifecycle authority, so P9 requires a cumulative relevant regression after focused iteration; merely rerunning every old profile/byte-format test is not a substitute.


## Last direction-check additions

- Selected Work query against a growing history: record objects/bytes accessed, validate required dependencies and do not recursively load provenance-only history by default. Full audit still detects corruption outside that query.
- Body growth: use unique/recompressed binary content as well as deduplicable text; distinguish logical size, unique chunks, DB allocation, staging and backup bytes. No assumed compression ratio.
- Storage pressure: low-space refusal, mid-import/export exhaustion, bounded cancellation, and interrupted backup preserve the previous committed state and last complete export. Read/list does not trigger compaction or all-history validation.
- No-Git ordinary project: no Git executable or personal Python; connect and use the managed entry, ordinary Work, retained body, export/restore, detach. A Git marker with missing executable is a distinct unavailable Git context, not a non-Git fallback.
- Early P2 feasibility: actual four host forms resolve the same managed runtime and correct project authority with narrow access. Record which permission/config action was necessary. Until separately authorized and observed, this remains pending even if source fixtures pass.


## Pre-R3 advisory cases

- D7: actual `.claude/worktrees/` spelling and leading-slash equivalent; verified parent with two registered roots; former parent empty/absent after reconciliation; unregistered/foreign/hidden/file sibling; tracked baseline collision; replaced parent; a new sibling after an earlier pass even with unchanged ignore text. No app-directory blanket exclusion.
- Chunk batch edges: 4 MiB and 64-count below/at/above limits, many tiny files and unique large bodies; reader busy/cancel/commit ambiguity; actual EXTRA/fullfsync behavior and sync-error evidence. No synthetic claim of a fixed fsync latency.
- Bootstrap: first trusted entry versus existing installation; trusted manager missing; replay/expiry/renewal outage; a fetched new manager must not execute before existing update trust verifies it.
- Hook manual handoff: unrelated/partial staging, hook-modified content, failed commit and actual resulting tree correspondence. No automatic hook invocation in this design exercise.
- Export notice: success versus interrupted attempt, root changes, unavailable destination, timestamp absent. WSL/native/interop distinctions in the host matrix.
- Body-removal tests and cost remain policy proposals pending Owner choice; no deletion test or implementation is authorized by recording them.


## R3b와 연결 경계 — 추가 집중 셀

- P1: fixed field-role/operation closure, role downgrade와 hidden reference, 서로 다른 위상 순서의 같은 의미, 65개 이상 provenance chain import, cycle/자원 초과. 새 세대 전환 각 경계 중단, 옛 handle read/write, fence 뒤 pointer 전 실패, hot journal namespace와 불명 pointer.
- P2: opaque 추가/삭제/type-change, opaque 조상과 D/F 충돌; submodule ignore override·내부 policy 변화·dirty/nested/init-deinit 거부; Windows placeholder/native link/junction 구분. root 하위 실행과 독립 연결 구분; Git init/locator 소실/실행 불가 구분, 기존 기록 보존과 오래된 binding 쓰기 거부.
- 호스트 실제 진단은 [초기 실행안](implementation-start.md)의 셀·한도·원복·근거 전이표를 따른다. 두 세션 첫 등록 경쟁과 등록 직전 worktree 교체는 P2 합성으로 검사하며 실제 병렬 에이전트 편집을 실행하지 않는다.
- P5: RF-27 fixed identifier/credential 검사, RPC의 실제 nested JSON Unicode escape 해제, 실행 전 보존 문맥, complete output·callback/reservation 관계, zero-new-byte와 prior-effect 유지.
- P8: ref child lock과 index lock 구분, 소유 intent-only/실소유/외부·교체·live/unknown, 재획득 전 조건 재검사, Windows 교체 거부, I1 bytes 후검증. 새로운 자동 retry/lock 강제 삭제는 없다.

이 목록은 신규 실행 결과가 아니다. 기존 source fixture/실패 기록을 재사용하고 새 형식의 달라진 경계만 검사한다. 실제 OS/host·설치·알림·공개 경로 검증을 합성 통과로 대체하지 않는다.
