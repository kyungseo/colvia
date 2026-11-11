# Implementation Regression Map

Status: 준비한 의미 기준 목록. 기존 코드와 테스트를 읽고 분류했으며 새 형식에서 시험을 실행한 결과가 아니다. R1 패킷 고정 이후 독립 준비 자료로 작성했다. R1 입력 파일을 바꾸지 않았다.

기존 설치와 형식은 호환 기준이 아니다. 유지할 동작을 아래 oracle로 다시 작성하고, 새 구조가 그 동작을 제공하는지 검사한다. 기존 테스트를 모두 그대로 실행해 통과시키는 것이 목표는 아니다.

| 기능/경계 | 유지할 의미 | 기존 근거 재사용 | 새 형식에서 확인할 변화 |
| --- | --- | --- | --- |
| 일반 Work | 실행 범위 승인→편집/검사/제출→사용자 결과 수락, 불필요한 재승인 없음 | ordinary_work, general_work_invariants | UUID/제목 분리, before/after bytes, SQLite commit/CAS |
| 범위 보호 | 파일 범위 밖 변경을 결과에 흡수하지 않음 | general_work, trial_usability | trie 전체 diff와 scope claim; unrelated concurrent edit 거부 |
| 새 대화·다중 Work | 정확한 Work와 결과/현재 파일 차이, 여러 Work 상태 독립 | ordinary_work, trial_usability | 대상 closure 조회, 같은 제목 다른 ID, 없는/손상된 본문 |
| 정확한 파일 bytes | CRLF·binary·삭제·mode·경로 alias 처리 구별 | worktree_checkout_bytes, general_work | bytes 보존과 텍스트 표시 분리; 대형 body bound |
| 보완·수락 취소 | 옛 수락이 새 결과로 옮겨지지 않음 | general_work_recovery | 불변 사건과 새 head, replay/중단/동시 CAS |
| 작업 분해·worker·umbrella | 자식 수락과 통합 수락 구별; 적용/통합의 명시적 권한 | worktree_execution, umbrella | 공용 DB/작업 폴더별 결과와 기존 한정 적용 의미 |
| 후보·후속 선택 | 선택은 실행 권한 아님; 완료 결과와 다음 행동 구별 | candidates, continuation | 분리된 typed tables/refs, 재실행 중복 없음 |
| 기록 경쟁 | 같은 결과 두 수락/다른 경쟁 선택이 둘 다 게시되지 않음 | worktree_process_safety, continuation_process | BEGIN IMMEDIATE/CAS와 transaction fault injection |
| 맡기기·알림 | 실행/제출/알림 효과를 구별; 원 결과와 현재 상태로 이동 | 기존 delivery/수신기 근거 | 새 locator와 Work ID 연결; 중복·늦은 응답·불명 효과 보호 |
| 선택형 실행·보호 | 실행 권한·범위·취소·불명 상태 보존 | official_execution, official_faults | 과거 profile 대신 capability; 이전 실행 이력 계속 조회 |
| 연결·갱신·복구·해제 | 프로젝트 규칙/설정/기록 보존, 실패 후 안전한 상태 | productization_safety, workspace | 첫 공개 버전 기준 compatible/incompatible update·capability·rollback/repair/detach |
| 소스·설치본 문서 | 사람용 한영 안내/짧은 agent entry, 실제 포함된 링크 | source_layout, 기존 문서 검증 | 새 capability/명령 기준, 과거 profile와 개발 지침 제외 |

## Deliberate Non-regressions

- 옛 JSON bytes, window/profile 이름, 옛 절대 경로 binding, legacy migration/update chain은 유지 목표가 아니다.
- 기존 문서가 모든 명령마다 내부 경로·승인 토큰을 노출하거나 불필요한 승인을 요구하는 동작을 보존하지 않는다.
- 기존 기능을 뺄 때는 그 기능이 필요 없다는 제품 판단을 기록한다. 코드 줄 수를 줄이기 위한 암묵적 삭제는 하지 않는다.
- SQLite 트랜잭션으로 대체된 옛 여러 파일 쓰기 순서를 재현하지 않는다. 대신 동일하거나 더 강한 외부 의미의 중단·경합 oracle을 둔다.

## Phase Gates

1. schema/typed ref/hash/trie/store: malformed input, unknown version, exact bounds, duplicate paths, corrupt/missing objects, rollback and stale CAS. 제품 연결은 아직 새 store를 선택하지 않는다.
2. context/observation: common-dir identity, non-Git, registered nested worktree, raw policy vs structural boundary, D1/D7 negative cases. filesystem/SQLite 정책은 이 계층에서 재사용한다.
3. ordinary vertical path: 신규 연결부터 쓰기/검토/수락/재개/과거 본문 조회, 소수/다수Work. 기존 합성 규모값과 비교하며 속도와 정확성을 따로 판정한다.
4. remaining capabilities/lifecycle/platform: 기능별 필요 조건을 충족한 뒤 public packaging 전환. 아직 미연결인 기능을 지원 표에 올리지 않는다.
5. 최종 누적 영향에 맞춰 전체 관련 회귀와 결과 리뷰. 실제 OS 설치·클릭·사용자 모델 흐름·공개 경로 검증은 별도 패키지다.

제품 소스 작성은 R1 구조 처분 후 시작한다. 이 준비는 테스트 실행이나 제품 완료를 뜻하지 않는다. 기존 dirty checkout은 그대로 두고 별도 worktree에서 구현한다.


## Managed Runtime And App Permissions Gate

[실행환경 계약의 최종 검증 행렬](runtime-and-extension.md#최종-검증-행렬)을 연결·갱신·복구 및 실제 설치본 검증의 필수 항목으로 포함한다. 개인 Python 설정 없는 최초 준비, 앱/CLI의 같은 전용 실행기 선택, 일반 Git/non-Git·linked·앱 nested worktree에서 runtime 읽기/실행과 authority/journal·프로젝트 쓰기를 구분한다. source 실행·합성 환경 검사는 실제 설치본/앱 sandbox 통과의 대체 근거가 아니다. 기존 성공/실패는 버전과 한계로 재사용하고 변경된 경계만 집중 검증한다. 정상 업데이트·실패 복구에서 기록/설정/본문/수락 이력을 보존하며 실패 안내는 필요한 조작과 이유만 짧게 보여야 한다.


## Codex·Claude 권한 모드별 접근·승인 경로

공개 전 기존 Codex 승인 요청 모드의 기록 폴더 접근 항목을 이 항목으로 통합한다. 완료 기준은 사용자가 선택한 승인 절차를 거쳐 정상적으로 일을 끝낼 수 있는가이다. 모드별 전체 기능 시험을 반복하지 않는다.

- 실행 가능한 모드의 확인 대상 이름은 Codex의 승인 요청·나 대신 승인, Claude의 수동 승인·편집 자동 수락·자동이다. 해당 host/버전에서 실제 제공되는지와 실제 승인·도구·파일 접근 동작을 먼저 확인한다. 이름만으로 동등 권한 또는 지원을 선언하지 않는다.
- 같은 Colvia 명령을 각 모드가 제공하는 승인 절차로 실행할 수 있는지 확인한다. 거절하면 해당 동작이 실행되지 않고 기존 파일·기록 상태가 보존돼야 한다. 일반 실행 승인과 특정 폴더의 추가 쓰기 허용은 실제 허용 범위를 따로 기록한다. 전체 권한 전환을 필수로 요구하지 않는다.
- 승인 절차만 다르고 실제 실행기·권한·도구·작업 위치 조건이 같으면 기존 작성·제출·재개 근거를 재사용한다. 달라진 권한·도구 조건에만 최소 추가 행동 시험을 한다. 모든 모드×기능×위치의 곱을 새 시험으로 만들지 않는다.
- 계획 모드는 허용된 조회·계획 제시만 하고 파일·Colvia 기록을 임의로 변경하지 않아야 한다. 실행 모드로 전환한 뒤 필요한 승인을 거쳐 이어갈 수 있으면 된다. 계획 모드의 쓰기 제한 자체는 실패가 아니다.
- 호스트 도구 승인·편집 자동 허용은 Colvia 작업 범위 승인이나 최종 결과 수락을 대신하지 않는다. 필요한 사람의 결정과 도구 승인 횟수를 구분하고, 반복 승인 부담·안내 명확성도 결과로 남긴다.

현재 Codex 근거의 정확한 범위: 승인 요청의 새 대화에서 설정한 기록 폴더 쓰기 권한이 반영되지 않은 것은 관측했다. 명령 실행 시 사용자 승인으로 진행 가능한지는 아직 미확인이다. 설정 미반영을 곧바로 사용 불가로 판정하지 않는다. 기존 성공·실패는 당시 조건 그대로 보존한다.

각 관측에는 host/버전·제공 모드·실제 정책·실행기/위치·승인 또는 거절·실제 허용 범위·파일/기록 보존·승인 횟수·재사용 근거·미확인 차이를 남긴다. 계정·토큰은 수집하지 않는다. 이 기준 정리는 추가 설정 변경·모델 시험 실행 승인이 아니다.


## Distribution Entry And Adapter Extension Gates

- 실제 공개 예정 배포 주소의 플랫폼별 한 명령에서 신규 설치/업데이트를 시작해 자동 자산 검증·runtime 준비·호환 binding 선택과 실패 복구를 확인한다. 사용자 Python ZIP/해시/profile 조합을 요구하면 일반 진입 완료가 아니다. 실제 게시 승인은 별도다.
- macOS ARM64, Windows 11 ARM64/x64 × Codex/Claude Code × CLI/데스크톱 12개 조합의 지원 가능성 및 검증 상태를 따로 기록한다. 설치/권한/첫 Work/결과/알림/재개를 기능별로 판정한다. 앱과 linked/nested worktree 관측은 앞 행렬에 포함한다.
- import 경계 검사와 최소 합성 adapter로 Core가 제품명·OS API에 결합되지 않고 능력 부족/취소 미확정/결과 불일치를 구별하는지 확인한다. 이는 Linux나 미래 에이전트 실제 지원의 근거가 아니다.
- 동일 authority의 Codex→Claude 및 Claude→Codex 재개에서 같은 Work·보존 결과·수락 이력이 유지되는지 확인한다. 새 adapter 추가만으로 기존 store schema 변경이나 이력 재작성 경로가 생기지 않아야 한다.
- [후속 후보](runtime-and-extension.md#후속-후보--현재-구현-제외)는 이번 구현·실행 검증 제외이며 이후 실제 연동 검증이 필요하다.


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
