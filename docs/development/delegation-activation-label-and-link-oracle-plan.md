# Delegation Activation Labels And Local-Link Oracle

Publication copy: this version replaces only identifying local paths and external repository names with repository-relative paths or neutral labels. The exact pre-publication source bytes (SHA-256 `ace22bdc756aeaa81869a7bc06b05ea0b43b4ef82fe92fb80dad69df2af0585b`) and original review records remain privately retained. Neutral labels are provenance locators, not executable paths; accepted scope, decisions, evidence counts and limitations are unchanged.

- Revision: proposal-1 / 2026-10-18.
- Status: Proposed — 방향과 계획 제안만 요청받았다. 구현·새 검증·외부 R0/R1 호출은 아직 승인·착수하지 않았다.
- Risk / mode: L2 / Standard source development. 승인 후 단일 source 작업으로 진행할 것을 제안한다.
- Roles: human Owner, Codex Driver, 별도 승인된 fresh Claude Reviewer. 이 문서는 runtime Work/intent가 아니다.

## Recommended Outcome

설치 문서는 실제 적용된 delegation-1 profile의 동작과 grant 조건을 설명하고, 준비 당시의 “미활성” 문구가 이후 사용을 계속 막지 않도록 정리한다. source의 실제 activation 기록은 별도 Owner 결정까지 미활성으로 둔다. 함께 링크 검사에서 fenced 코드 예제를 실제 링크로 오인하는 부분을 고친다.

두 변경을 한 번에 검토·검증해 새 정확한 release identity와 활성화 제출안을 준비한다. 이 작업의 결과 수락과 실제 활성화·Git·adopter 적용은 각각 별도다. 지금은 계획 문서와 A 수락/탐색 기록만 갱신한다.

## Owner Planning Authorization — 2026-10-18

> A 결과는 수락해. 설치본 라벨을 활성화에 맞게 정리하는 작업과 링크 검사 oracle 보정을 묶어 후속 계획을 제안해. 기존 증거를 재사용하고, 실제 활성화·Git·adopter 적용은 아직 보류해.

[A 결과 수락](CHORE-20261018-001-rule-entry-language-activation-preparation.md#owner-result-acceptance--2026-10-18)은 기존 A의 완료다. 이번 후속은 그 완료 결과를 다시 Active로 만들지 않는다. 제품 source의 [Start And Select](WORKFLOW.md#start-and-select), [Preliminary Review Location](WORKFLOW.md#preliminary-review-location), [Review And Evidence](WORKFLOW.md#review-and-evidence)가 분류·위치·착수·검토를 소유한다.

새 task ID는 아직 부여하지 않는다. 이 source-only 계획 문서가 착수 전 제안의 유일한 소유자이며, 계획·착수 승인이 나면 ID 충돌을 확인해 한 개의 development record로 연결한다. 기존 index에는 후보 제목·목적·재검토 조건과 이 승인 위치만 둔다. A 승인이나 이전 reviewer 호출 허용을 새 실행 허가로 재사용하지 않는다.

## Starting Inputs

- 기존 작업 checkout/branch는 `codex/colvia-agent-delegation-m0-20261016`, HEAD `d86bd1fd7754144e5c8538712724ae78571941bf`다. 고유 미커밋 M1/M2+A를 보존하고 후속에도 같은 checkout을 사용할 것을 제안한다. 새 worktree·branch·commit은 만들지 않았다.
- 읽기 전용 재확인: remote main `a93f71c359c4f0a9d57fcfb50d5999160e870f77`, open PR0. A의 source 정합 대상과 같다. 별도 path-scoped tool rule 디렉터리는 없으며 source 절차와 기존 코드 스타일을 따른다.
- A 수락 대상 P: `49969df17f06e85cae8039c8dbd8cbf43a39f3ca8a317fceace4edd19596ad0b`. `final-candidate-v2.json` SHA-256 `cb7785b10aa90f8d71f8980753733fcaeac605b62da8e542fc11904da8ce3a5e`가 managed29와 successor17을 결속한다. 현재 일치 여부를 확인했다.
- 수락 직전 A 결과 문서 SHA-256 `3df089903c82988b049293c3277b95d805326449e7c1aebe902f50b1d202a27a`; 정확한 원문은 기존 A artifact directory의 `accepted-a-result-20261018.md`에 한 번 보존한다. 최종 R1 `R1-a-correction-002`는 Blocker0·필수0이며 새 후속의 R0/R1을 대신하지 않는다.
- 기존 complete anchor는 r11 normal656/parent-O656 및 retained17씩이다. A의 새 P artifact16/16·612.358초, safety59·TERM/KILL2·smoke7/7, A 이전 P의 focused normal8/O2와 reader5·token3898, 마지막 GFM22파일325링크 오류0은 각 입력과 범위를 유지한다. reader는 언어5/5 관찰, strict Read1/5 통과라는 제한이 있다.
- 현행 기술 계약은 DR-0004 entry-1이며 DR-0005는 Draft다. Core가 source activation 상태를 조회하거나 강제하지 않는다는 기존 한계를 유지한다. 계약 발효·인증·새 grant 기능을 추가하는 계획이 아니다.

## Scope 1 — Installed Labels

### Proposed Wording Direction

managed 문서에서 현재 delegation-1을 설명하는 준비 상태 문구만 profile 중심으로 바꾼다. 예를 들어 AGENTS의 “unactivated implementation candidate” 대신 “These instructions describe the `delegation-1` profile of the verified installed release.”를 사용하고, 문서 존재·verified binding 자체가 사람의 승인이나 실제 rollout 허가를 증명하지 않는다는 기존 한계를 함께 둔다. 이것은 검토할 문안 방향이며 현재 제품 파일에는 적용하지 않았다.

adapter의 exact delegated acceptance는 profile·Owner가 수락한 정확한 grant·단일 ordinary isolated-worker·Work와 scope·actor/action 일치 조건으로 설명한다. “현재 활성화 완료”를 새로 선언하거나 grant 없이 권한을 추론하도록 바꾸지 않는다. source 개발 진입은 계속 source 절차와 Draft/activation 기록을 확인한다. 설치본이 source-only DR을 자동 발견하거나 Core가 activation을 검증한다고 설명하지 않는다. 실제 도입은 별도 activation 및 정확한 설치/업데이트 승인 이후라는 기존 운영 경계를 유지한다.

주요 대상은 다음15개 managed 파일의 현재 delegation-1 라벨·이를 설명하는 문장이다.

- `AGENTS.md`, `README.md`, `adapters/colvia-work/SKILL.md`, `PRODUCT-CAPABILITIES.json`.
- `docs/README.md`, `docs/CONCEPTS.md`, `docs/GENERAL-WORK.md`, `docs/GETTING-STARTED.md`, `docs/GUIDED-INTENT-FORMATION.md`, `docs/MAINTAINING.md`, `docs/MANUAL-OPERATION.md`, `docs/OPERATIONS.md`, `docs/REFERENCE.md`, `docs/SECURITY-AND-SUPPORT.md`, `docs/WORKSPACE-CONTRACT.md`.

전체 검색 후 R0에서 정확한 변경 문장과 유지 문장을 확정한다. heading/anchor를 바꿔야 하면 그 heading을 참조하는 managed 링크를 같은 범위에서 갱신한다. 가능한 한 기존 anchor를 보존한다. CAPABILITIES의 current profile 경계만 맞추고 runtime·지원 범위·과거 evidence 날짜를 새로 검증한 듯 바꾸지 않는다.

역사적 entry-1/First B1의 준비 문구·원래 activation hash·인용은 보존한다. 특히 OPERATIONS의 permission amendment와 WORKSPACE의 S5 설명을 delegation-1 라벨과 함께 일괄 치환하지 않는다. 실제 발효 상태는 source 기록에서 판단하며, 미검증 지원을 활성화 문구로 덮지 않는다. 첫 A의 비차단 narrative 저장 규칙·project/managed CLAUDE 표현 등 별도 편집 후보는 이번 범위에 자동 합치지 않는다.

source-only 범위는 새 작업의 검토/결과, 새 P 기준 exact successor17 표와 관련 activation 제출안 갱신이다. DR-0005의 실제 Accepted/activation 전환이나 최종 Decision/Rationale/Consequences 확정, DR-0003/0004/0006와 WORKFLOW의 발효 문구 적용은 포함하지 않는다.

## Scope 2 — Local-Link Oracle

`tests/test_productization_safety.py`의 `test_document_port_local_links_resolve`는 원문 전체를 regex로 읽는다. DECISION-GUIDE의 fenced 역사 예시2개를 `docs/docs/...` 링크로 해석할 것으로 정적으로 확인했으며, 실제 실패는 아직 실행하지 않았다.

가장 작은 보정은 기존 inline Markdown 링크 검사에 fence 인식을 추가하는 것이다. 표준 라이브러리만 사용하는 test-local helper를 같은 파일 또는 별도 test helper에 둔다. 새 제품 parser·외부 패키지·런타임 dependency는 추가하지 않는다. 기존 docs 범위와 repository-inside/existence/fragment·외부 URL 처리 의미를 유지하고, 코드 fence 안의 예시만 제외한다. reference-link/autolink/전체 CommonMark 지원으로 범위를 확대하거나 이 검사를 완전한 GFM oracle이라고 부르지 않는다. 전체 문서의 GFM 렌더·anchor 검사는 별도 기존 검사로 보완한다.

helper의 인정 범위는 백틱/틸드 fence, 같은 delimiter와 충분한 닫기 길이, info string·허용 들여쓰기, fence 안의 다른 delimiter 및 코드 블록 종료 후 일반 링크 처리다. 기존 문서의 실제 패턴과 아래 반례로 충분히 한정되지 않으면 R0에서 설계를 조정하고 영향을 설명한다.

보정 전후를 다음과 같이 남긴다.

1. 정확한 현재 source에서 기존 테스트1개를 normal로 실행해 예상 실패를 실제로 확인한다. 예상과 다르면 원인을 먼저 좁히며 성공했다고 보정 근거를 만들지 않는다.
2. 고정 합성 사례: 정상 상대 링크, 외부 URL/기존 fragment 처리, fenced 역사 링크2개, 백틱·틸드 및 길이가 다른 내부 delimiter, fence 종료 뒤의 실제 링크를 확인한다.
3. 실패해야 하는 사례: fence 밖의 누락 링크, 저장소 밖 경로, fenced 예시를 밖으로 옮긴 경우가 계속 실패해야 한다. 검출된 링크 집합/수도 확인해 모든 링크를 무시하는 구현은 통과하지 못하게 한다.
4. helper와 변경 oracle을 normal/parent-O에서 확인하고 source 실제 테스트의 보정 전 실패·보정 후 통과를 구분해 기록한다. 수정 후에도 runtime assertions나 다른 테스트를 약화시키지 않는다.

보정 전 예상 non-pass와 보정 후 실행은 서로 다른 고정 입력/attempt로 구분한다. baseline 실패 원문·exit status를 보존하고 PASS나 expected-success로 바꾸지 않는다. 실패한 slot을 덮어쓰거나 같은 attempt의 실패 차단을 완화해 후속 실행을 통과시키지 않는다. 원인·보정 diff·새 입력 admission을 기록한 다음 보정 후 검증을 시작한다.

## Evidence Reuse And New Checks

재사용은 [Maintaining](../MAINTAINING.md#evidence-reuse-and-selection)의 누적 영향 평가로 정한다. 단순히 A 이후 파일 수만 보지 않고 r11→A→후속의 runtime·test·fixture·controller·discovery 변화와 assertion 소비 범위를 대조한다.

| 대상 | 제안한 확인 | 재사용 경계 |
| --- | --- | --- |
| 제품 실행·record·권한·복구 | runtime bytes·mode·의존성·격리 불변 대조 | r11 complete656×2와 retained17×2의 영향 없는 assertion 재사용. 후속 source의 fresh complete PASS로 표시하지 않음 |
| 바뀌는 링크 oracle | 기존1개 실패 재현, 새 helper 반례, 변경된1개 normal/parent-O | 그 테스트의 과거 결과는 새 assertion의 근거로 재사용하지 않음 |
| 설치 문서 직접 소비 | 아래 focused normal5개 및 view2개 parent-O | A의 나머지 오류코드/지원 안내 등은 변경 문장과 assertion 영향이 없음을 확인해 재사용 |
| instruction 이해 | 아래4개 새 reader 시나리오 | A의 언어 우선순위 관찰은 해당 규칙 bytes/의미가 그대로일 때만 재사용. strict1/5는 그대로 남음 |
| 최종 managed artifact | 새 P, Q는 수락된 A P `49969df1…`; 기존 exact entry-1 predecessor 유지. C01–C16 normal1회 | A의16/16은 baseline일 뿐 새 P의 PASS가 아님 |
| 문서·inventory | 전체 영향 문서 GFM/link/anchor/강조·managed29·정확한17문서 범위·generic disclosure·token 확인 | 같은 날짜나 동일 결과 수치만으로 현재 바이트 검증을 대신하지 않음 |

focused normal의 기존 ID는 다음5개다. 첫 번째와 두 번째를 parent-O에서도 확인한다. 변경된 oracle은 위 보정 전후 실행과 중복되지 않게 한 번의 같은 결과를 연결한다.

- `test_human_view.HumanViewInstalledTests.test_empty_actual_source_installed_and_git_are_read_only`
- `test_human_view.HumanViewInstalledTests.test_p_q_p_uses_current_adapter_path_and_detach_remains_readable`
- `test_productization_safety.ActualWorkspaceInitTests.test_document_port_managed_payload_generic_disclosure_guard`
- `test_productization_safety.ActualWorkspaceInitTests.test_document_port_local_links_resolve`
- `test_productization_safety.ActualWorkspaceInitTests.test_document_port_status_and_doctor_expose_verified_docs_read_only`

generic disclosure는 managed 전체를 읽는 직접 소비자다. filename literal 탐색 결과만으로 빠뜨리지 않는다. oracle parent-O1개와 새 helper의 모드별 고정 ID는 R0/입력 준비에서 선정 목록에 결속한다. 새 test ID가 생기면 collection 순서·기존 ID 보존·추가 ID를 기록하며 무조건656개라고 가정하지 않는다.

### Reader Scenarios

| 사례 | 관찰할 행동 |
| --- | --- |
| L-S: source checkout | AGENTS 조건부 source 진입을 따라 A 수락과 DR-0005 미활성을 구분. profile 라벨만 보고 실제 activation/Git/adopter 허가를 선언하지 않음 |
| L-G: 승인된 synthetic 설치·정확한 grant | 운영자가 제공한 합성 exact-install 승인 문맥과 verified view에서 profile/adapter·정확한 Work grant를 읽고 ordinary accept 허용 범위를 설명. 남은 “미활성” 라벨 때문에 무조건 보류하지 않음 |
| L-H: 동일 profile·grant 없음 | human 기본 경로를 유지. 새 라벨이나 CLI token만으로 delegation 권한을 만들어내지 않음 |
| L-R: grant 불일치 또는 stale | 합성 fixture의 한 가지 고정 반례를 먼저 지정하고 exact scope/action/actor/Work 검증 실패를 거부로 해석. 다른 Work·parent·source 결과 수락으로 권한을 넓히지 않음 |

실제 activation/adopter 없이 synthetic fixture만 쓴다. case별 prompt, 필요한 자료/읽기 경로, 예상 판정과 실패 조건을 호출 전에 고정한다. runtime view는 Driver의 격리 실행 결과로 제공하며 reader가 자율 CLI를 실행했다고 주장하지 않는다. Read만 허용하고 실제 writer는 실행하지 않는다. 언어·필수 읽기·권한 판단을 따로 기록하고, 미달 결과를 지우거나 사후 기준을 완화하지 않는다. 지침 수정이 필요하면 영향을 설명한 새 case/revision으로만 재확인한다.

### Admission Adaptation

기존 A의 `a_admission.validate_anchor`는 protected104의 모든 파일을 byte-exact로 비교하므로 test oracle 보정은 그대로는 거부된다. 기존 manifest에 allowed_changed만 추가하거나 test 파일 전체를 보호 목록에서 빼는 방식은 쓰지 않는다.

새 task-local 입력에서 변경한 oracle/helper의 정확한 diff와 assertion을 별도 검증하고, 같은 테스트 파일의 나머지 함수·setup/import와 공통 fixture는 unchanged 증거를 유지한다. `src/`, launcher, 권한·복구 runtime, Seatbelt 정책 및 무관한 controls는 계속 byte-exact로 보호한다. AST 구조 대조만으로 중요한 module-level 부수효과를 놓치지 않게 원문 diff와 import/setup도 함께 본다. 신뢰 경계가 한정되지 않으면 affected complete 검증을 제안한다.

변경된 assertion·선택 목록·admission 입력에는 새 고정 identity를 부여하고 focused safety/guard 반례를 확인한다. 기존 safety59, 실제 TERM/KILL2, canary, collection, smoke7 중 변경 admission이 의존하는 prerequisite를 새 입력에서 수행한다. 기존 통과 결과는 기존 의미 그대로 보존한다. static checker의 CAPABILITIES 허용 변경도 실제 profile 라벨의 지정 row/field만 명시하고, runtime·다른 field 보호를 제거하지 않는다. first A와 correction의 소비 완료 slot/launcher를 재사용 실행하지 않는다.

## Sequence, Budgets And Stop Conditions

제안 순서: R0 계획/라벨 경계/새 oracle·admission 검토 → 범위 내 필수 보정 → 라벨·oracle 일괄 구현 → 집중 검증·reader → 최종 P 고정 → artifact16 → R1 및 필요한 범위 내 보정 → 결과와 새 exact activation 제출안 보고.

계획 승인 시 이 R0부터 최종 R1까지를 한 묶음으로 허용하도록 제안한다. 작은 보정마다 별도 승인을 다시 요청하거나 전체 matrix를 반복하지 않는다. 새로운 권한/record/복구 의미, 외부 dependency, 실행 경계·리소스 한도 확대 또는 실제 activation/Git/adopter는 이 묶음에 포함하지 않는다. 현재 요청만으로 새 CLI reviewer를 호출하지 않는다.

고정 runtime은 이전 GIL-enabled CPython3.14.7 `-I -S -B`와 동일 환경을 우선한다. native network/credential 차단, input/output 분리, lock·process-group 정리, 8/12GiB task·25/15GiB free-space 조건을 유지한다. 실제 호출 전 non-secret 인증 경로가 기대한 `claude.ai/firstParty/pro`인지 확인하고 다른 결제 경로이면 멈춘다. Reviewer는 fresh tools 없는 정적 호출, reader는 고정 fixture의 Read만 허용한다.

초기 per-call 제안은 acquire/canary/collection300초, oracle/focused600초, artifact1800초, reader300초, static reviewer900초다. native/reader 한도에는 cleanup20초를 포함하고 reviewer는 별도 cleanup20초를 둔다. 최근 artifact612.358초, A focused normal33.905초/O18.589초, reader약28–62초는 예산 근거이며 ETA 보장이 아니다. 새 assertion/reader 시나리오의 실제 시간은 아직 모른다. 원문 실패와 모든 호출·시간을 누적 기록한다.

전체656×2는 기본 재실행하지 않는다. runtime·권한·record·복구 변경, 공통 fixture/격리/수집 의미의 광범위 변화, 기존 anchor를 무효화하는 반례 또는 영향 범위를 한정할 수 없는 경우에만 해당 complete 범위와 이유를 제안한다. 한도 초과·미완료·알 수 없는 상태는 PASS가 아니며 자동 timeout 상향이나 같은 실패 입력 반복으로 처리하지 않는다.

실행용 새 입력이 필요하면 승인 후 `PRIVATE_LABEL_ORACLE_EVIDENCE`의 부재/소유권을 먼저 확인해 사용한다. 전체 source 사본은 실제 격리 실행이 요구하는 한 벌만 만들고, 이전 증거는 원래 경로로 참조한다. 지금 새 실행 directory나 reserve를 만들지는 않는다.

## Completion And Remaining Decisions

1. 설치 문서의 current profile·정확한 grant 조건이 일관되고, 시간에 종속된 준비 라벨이 activation 이후 사용을 막지 않는다. 원래 승인·권한 조건이나 역사 의미를 약화시키지 않는다.
2. 원래 링크 오류의 실행 결과와 새 oracle의 positive/negative·모드별 결과가 남는다. 실제 누락/경로 이탈 검출을 유지한다.
3. 새 P의 inventory·설치 소비·artifact16 및 영향받는 reader 결과를 갖추고, 이전 anchor·미검증 사실을 구분한다.
4. R1 필수 지적을 처분하고 새 exact successor 문서/조항/hash 및 activation 제출안을 제시한다. 새 source complete 실행 여부와 근거를 과장하지 않는다.
5. 실제 activation·Git·adopter 변경 없이 Owner 결과 수락을 기다린다. source의 DR-0005 상태나 현행 기술 계약을 미리 바꾸지 않는다.

문서와 test helper의 되돌리기는 낮은 비용이지만 잘못된 라벨이 agent의 권한 해석에 영향을 줄 수 있어 L2로 다룬다. 제품 runtime의 일방향 전환 제한은 문서 되돌리기로 사라지지 않는다. 이 계획은 배포·활성화 gate를 우회하는 근거가 아니다.

A의 미커밋 source와 r11/A 입력·결과·reader 원문은 이 후속의 누적 영향 평가/R0와 정확한 새 P 검증에 재사용한다. R0에서 실제 소비하는 증거를 확정한 뒤 사용이 끝난 생성 fixture·중복 파일을 재평가한다. 후속이 선정되지 않으면 그 판단 시점에 보존 목적을 다시 확인한다. A 결과 수락만으로 고유 미커밋 source나 마지막 복구본을 지우지 않는다.

## Navigation Record

이번 index 변경은 New Source Candidates의 후속 제목/목적/재검토 조건/계획 승인 링크 추가와 A 완료 결과 링크 갱신뿐이다. 기존 intake criteria나 실행 경계를 고치지 않았다. Before `ea3cffd753c921132337a8d724f0e01067d014847b51a1926c9ff0c852958fb4`, after `9212527afe6510ba0db2b4a15947ec04827de3eab2e5b000c7bc7560f220fdf9`; bounded diff SHA-256 `e14694924fcc6a08ad11594f64101867b2190bd81612af5be4ec86abb3ee427d`. 원문 diff는 기존 A artifact directory의 `a-acceptance-followup-index.diff`에 있다. 별도 STATUS·backlog·runtime candidate·Work는 생성하지 않았다.

## Selected Follow-up — 2026-10-18

The Owner approved the combined R0-through-final-R1 plan. Subsequent authorization, progress and review belong to [PATCH-20261018-002](PATCH-20261018-002-delegation-label-and-link-oracle.md#owner-authorization--2026-10-18). The proposal above is retained as the planning snapshot; it is not a second progress record. Actual activation, Git and adopter application remain on hold.
