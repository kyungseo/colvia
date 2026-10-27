# CHORE-20261027-002 — 사용자 흐름과 개발 문서 정렬

상태: Done — 2026-10-27 Owner가 사용자 매뉴얼 보강·개발 navigation 정렬 결과와 명시된 한계를 수락했다. R1 원판정 REVISE, Driver 보정과 최종 7/7을 구분해 보존한다.

Owner: human Owner. Driver: Codex. Reviewer: 승인된 fresh Claude CLI, tools0.
시작일: 2026-10-27. 실행 시작: 2026-10-27 09:52:55 UTC.

## 목적과 범위

처음 읽는 사람이 요청·에이전트 수행 범위·사람 판단·중단과 재개를 이해하도록 기존 제품 문서를 보강한다. 개발 인덱스와 이전 기록에서는 U2의 현재 closeout과 후속 판단으로 가는 연결을 바로잡는다. 상세 범위·제외·파일별 변경안·검사 명세는 [승인 계획과 R0 원문](u2-document-alignment-plan.md)에 있다. 이후 진행은 이 기록 하나가 소유한다.

Core/Host 실행 구현, 플랫폼 지원, 다른 작업이나 도입처 변경, commit/push/PR/merge/release는 제외한다. 의미를 바꾸는 규칙 수정은 named amendment와 Owner 판단 없이는 적용하지 않는다. 프로젝트가 채택하는 문서 currentness 규칙과 공통 plan/continuation 정렬을 구분한다.

## 고정 입력과 Owner 실행 승인

- source base: `17dc804a6af4e168d1bb73aa765e9354db4952ba`.
- 승인 계획: `u2-document-alignment-plan.md`의 원래 UTF-8 bytes `[0, 31416)`, SHA-256 `97b6624914da11ddf44bdc0d60c8ae684550e61f92dddd51e55cbe0525798a9b`. 이후 추가된 승인·handoff pointer는 이 원래 bytes와 구분한다.
- R0-01: Claude Opus 5.5, REVISE, 정적 packet 검토. M1–M5 및 L1–L4 Driver 처분은 계획서에 있다. 보정 뒤 Reviewer 재검토 PASS를 주장하지 않는다.
- Owner는 R0 보정 계획으로 문서 수정 → 기존 7개 검사 → R1을 진행하는 질문에 “보정 계획 실행 승인”이라고 답했다. 예상 60–90분 + Reviewer 대기 10–30분, 실행 착수 후 누적 중단 한도 120분, Owner 응답 대기 제외 조건이다. 앞서 승인한 CLI R0/R1·보정 재검토 한도도 유지한다.
- 기본 중단 시각: 2026-10-27 11:52:55 UTC. Owner 응답 대기를 제외할 경우 실제 구간과 근거를 이 기록에 남긴다. 동시 진행 시간은 한 번만 센다.
- ID 확인: 현재 파일, 전체 retained Git history와 등록 worktree에서 2026-10-27의 기존 번호는 001뿐이었다. 002를 새로 할당했다. 실제 충돌이 보이면 기록을 분리 생성하지 않고 판단을 요청한다.

## 완료 기준

- [x] Concepts에서 전체 흐름과 다섯 요청, 사람 판단·중단·재개를 찾을 수 있다. 첫 진입 문서는 짧게 연결한다.
- [x] 설치 profile, agent 지침, source 개발용 실행 검증과 향후 구성을 구분하며 지원·배포 주장을 확대하지 않는다.
- [x] adapter와 사용자 안내의 승인·수락·계획 정렬 설명이 일치하고 기존 규칙의 조건을 보존한다.
- [x] development index와 이전 U2 기록이 현재 수락/closeout으로 연결되며 과거 실패·진행 이력은 보존된다.
- [x] 변경된 링크/anchor, GFM, disclosure, whitespace 및 최종 문장 보강 후보의 기존 7개 focused 검사 결과·한계를 기록한다.
- [x] R1 처분과 실제 Owner 결과 판단을 구분해 남기고, 적용 공백·필요한 후속·보존/정리를 보고한다.

## 검사와 한계

승인 계획의 7개 `ActualWorkspaceInitTests`를 normal 모드, 고정 final GIL-enabled CPython 3.14.7과 Seatbelt 경계에서 한 번 실행한다. 15분 test lane 한도와 기존 45초 subprocess timeout을 유지한다. 정확한 명령·controls identity는 계획서에 있다. 입력·source/runtime drift와 선택/수집/실행 ID, skip/failure를 기록한다.

이번 문서 후보에는 새 inventory와 설치·update/rollback·repair·detach 소비 결과가 필요하다. 이전 실제 release에서 문서 bytes가 바뀌는 exact-pair 전환은 이번 검사가 아니며 실제 도입처 update 준비에 남긴다. 이전 U2 결과는 지원 주장과 종료 상태의 근거로만 사용한다. 전체 회귀 PASS를 재사용한다고 주장하지 않는다.

agent 진입·재개는 다섯 요청 및 pending/stale reference/new acceptance 사례의 정적 대조다. 실제 native agent 사용이나 일반 사용자 이해도 관측은 수행하지 않는다. `tiktoken==0.13.0`은 확인한 환경에 없어 읽기 token 한도는 미확인이다. 승인 계획대로 전체 흐름·예시를 Concepts에 두고 필수 첫 진입 두 문서는 짧게 연결한다.

## 진행

2026-10-27: R0 보정 계획 실행 승인 후 기록을 생성했다. 제품 문서 편집과 선택 검사를 시작한다. 추가 규칙 의미 변경이나 전체 회귀 필요가 드러나면 해당 범위의 보정안을 제시한다.

## 결과·잔여와 다음 판단

앞선 문서 후보의 R1·검사를 마친 뒤 Owner가 추가 문장 보강을 요청했다. 현재 보강 후보는 R1 처분·보정과 최종 7/7을 마쳤으며 Owner가 명시된 범위와 한계를 수락했다. 문서 완료 후에도 실제 적용에는 정확한 Host/adapter 배포물, 프로젝트 연결, 승인 범위·검증·복구 계획을 따로 정해야 한다. 도입 대상과 설치 관측은 private 보고에만 남긴다. Git·배포·실제 적용은 이번 문서 실행 승인에 포함되지 않는다.

## 보존과 정리

이 source 기록·계획/R0 원문·미커밋 문서는 현재 결과 검토와 수락의 입력이다. 전용 task의 고정 reviewer packet/identity와 검사 controls는 R1 및 선택 검사에 사용한다. 재생성 가능한 raw 출력·렌더·fixture는 소비 종료와 필요한 결과 보존을 확인한 뒤 standing cleanup 조건으로 정리한다. 마지막 recovery copy와 미해결 실패 증거는 유지한다. R0 raw stream·빈 stderr·중복 응답은 계획서의 원문 동일성과 열린 파일 없음 확인 후 정리했으며 활성 source 경로는 바뀌지 않았다.

## 초안과 정적 검사 — 2026-10-27

README·Getting Started는 Concepts로 짧게 연결하고, Concepts에 전체 흐름·영문 요청 5개·사람 판단·중단/재개를 모았다. docs/README는 설치 manual, agent 지침, source-only 실행 검증을 구분한다. 공통 adapter와 REFERENCE는 기존 프로젝트별 문서 규칙을 따르는 보고와 공통 plan/continuation 정렬을 연결한다. WORKFLOW에는 기존 완료 기준·검증·navigation 책임의 교차참조만 추가했다.

development index와 source A 상단에 U2 closeout 링크를 추가했다. index에서 직접 연결하는 `u2-tool-neutral-execution-plan.md`에도 옛 승인 대기 문구가 남아 있어 같은 방식의 dated pointer를 추가했다. 이는 승인된 관련 development 안내 정렬이며 실행 범위나 과거 판정을 변경하지 않는다. 이전 FEAT의 완료 기록은 이미 정확하여 수정하지 않았다. OPERATIONS·Security·Guided Intent·Manual Operation·Maintaining과 Capability Declaration은 대조하고 그대로 유지했다.

첫 정적 확인은 변경/작업 문서 12개, 로컬 링크 238개, heading 200개에서 신규 오류와 기존 literal 강조 잔여가 없었다. marked 17.0.5의 GFM 렌더링을 사용했다. source A 원문과 승인 계획 원래 bytes를 보존했다. source-only 계획 pointer 추가 뒤 영향받은 검사를 다시 확인한다. 실행 코드·tests·launcher·Capability Declaration·agent entry는 unchanged이며 managed 30개 중 설명/adapter 7개가 바뀌었다.

## Focused 검사 첫 실행 실패와 보정 승인

첫 실행은 normal CPython 3.14.7에서 7개 ID를 선택·수집·실행했고 1.049541초 뒤 exit 1이었다. local-link 메서드 1개만 통과했고, failure 5건·error 2건이다. 한 round-trip 메서드의 두 subtest가 각각 failure/error여서 이 수를 통과 메서드 수와 단순 합산하지 않는다. skip·expected failure는 0이다. file/network canary는 통과했고 source/runtime drift와 timeout은 없었다. 제품 적격성 PASS가 아니다.

관측: 설치 preview는 `HV2-INTERNAL`, `exception_type: RuntimeError`, Git fixture는 초기화 exit 1이었다. 읽기 전용 진단으로 두 환경 결함을 재현했다. HOME 누락 상태의 `Path.home()`은 `Could not determine home directory.`로 실패하고 기존 HOME 값 전달 시 성공했다. 시스템 Git stub은 sandbox가 허용하지 않은 Xcode library를 찾다 실패했고, 이미 허용된 Command Line Tools의 실제 Git은 `git version 2.54.0 (Apple Git-157)`을 출력했다. 이는 Driver가 만든 검사 환경 결함이며 문서나 제품 코드의 결함을 재현한 결과는 아니다.

원 controls·log·summary·입력 metadata를 보존한 뒤 보정안을 별도로 준비했다. 기존 HOME 값은 변경 없이 전달하고 XDG config는 fixture 안에 둔다. scoped Git wrapper는 이미 허용된 실제 Git을 실행하며 system/global config를 끈다. 이는 제품의 Git 환경 정리 이후에도 실제 사용자 설정을 읽지 않게 하는 검사 환경 조치다. 파일/네트워크 권한 확대, source/assertion/45초 timeout 변경은 없다. 새 실행은 같은 7개 ID와 failfast를 사용하며 별도 output directory에 쓴다.

Owner는 이 보정안의 1회 재실행 질문에 “보정 검사 1회 승인”이라고 답했다. test lane 누적 15분에서 첫 1.049541초를 뺀 잔여를 내림한 898초 한도이며 전체 120분은 유지한다. 첫 실패를 PASS로 바꾸지 않는다. 원 failing fixture는 기존 unittest cleanup으로 이미 정리되어 상세 입력 상태는 남지 않았고, 원 log·고정 controls·source identity와 read-only 재현 근거를 보존했다. 이것은 환경 원인 처분의 한계로 남긴다.

## 보정 검사 결과와 적용 공백 — 2026-10-27

승인된 두 번째 실행은 같은 7개 ID를 모두 수집·실행해 7/7 통과했다. test body 73.571초, controller 포함 73.742262초, exit 0이다. skip/failure/error/expected failure는 0이며 file/network canary 통과, source/runtime drift 및 timeout 없음이다. 첫 실패와 합한 test lane 사용은 74.791803초이며 전체 검증이나 실제 사용자 관측으로 보고하지 않는다.

검사 시점 managed 후보는 `continuation-1`, `product-release-95c67e34f43cffdab8634fd4`, inventory SHA-256 `95c67e34f43cffdab8634fd4a04e74042188375ebf630b8129ffa5cf04979635`이다. 30개 중 7개 설명/adapter bytes가 기준에서 바뀌었다. 이후 추가한 source-only U2 Host README의 dated pointer는 이 managed 후보와 선택한 test assertion/input에 포함되지 않아 이 7개 검사를 다시 실행하지 않는다. 원 Host README의 미검증 문구와 실제 완료 판단을 연결할 필요가 있어 승인된 개발 문서 정렬에 포함했다. 그 문서는 과거 내용을 보존하고 public allocation 변경의 별도 한계도 함께 연결한다.

기존 두 도입처의 설치 release inventory와 payload를 읽기 전용으로 확인했다. 두 곳의 현재 payload는 기준 source의 30개와 일치하고 이번 문서 후보와는 같은 7개 설명 파일만 다르다. 정확한 대상과 설치 identity는 private 작업 기록에 있다. 문서 안내 개선을 받기 위한 업데이트 후보는 생겼지만 R1·결과 수락·정확한 이전/새 release 쌍의 적용 준비가 남아 있어 지금 설치하지 않는다.

실제 U2 적용에는 일반 runtime update와 별도로 다음 준비가 필요하다.

1. 적용할 실제 업무·프로젝트 상태와 승인 범위를 정하고, source-only Host/adapter를 그 작업의 고정 실행 묶음으로 구성할 수 있는지 확인한다. 현재 CLI는 trusted materializer가 준비한 controller 없이 자동 실행하지 않으며 새 controller·DNS·권한 fallback도 하지 않는다.
2. 실행할 tool/runtime/model/auth, source/build와 필요한 policy·parser·proxy·spec의 exact identity를 고정한다. 기존 verification allocation의 대상·deadline·예산·승인은 새로운 실행에 재사용하지 않는다. 공개용 allocation 변경 뒤의 원 native 결과를 새 후보의 PASS로 쓰지 않는다.
3. 실제 프로젝트의 intent/Work·문서와 effect scope를 연결하고, 검증 oracle·시간/시도·stop·fresh-session resume를 정한다. 민감한 자료의 외부 전달은 별도 승인 범위를 확인한다.
4. 필요한 합성 refusal/preflight와 실제 read/write/verify/stop/resume 관측을 해당 후보·OS·도구에 대해 계획한다. 결과 품질·부담의 Owner 판단과 Core의 정확한 수락은 별개다.
5. 원 입력·journal·예산·retained source와 중단/복구 조건을 보존하고, 문서 runtime의 same-window update/rollback과 pending exact recovery를 구분한다. 실제 적용 전에 현재 상태를 다시 확인한다.

이 목록은 다음 적용 계획에 필요한 공백이며 이번 작업에서 실행하거나 구현한 기능이 아니다. 배포 가능한 Host 통합 또는 공통 운영 진입을 새로 구현해야 한다면 별도 범위로 정한다. Windows의 기존 작업 범위는 변경하지 않았다.

## R1 검토 입력 준비

R1은 최종 문서 diff, 관련 계약과 실행·실패 기록을 정적으로 대조한다. 현재 source-only 설명을 포함한 14개 변경/작업 문서의 링크·GFM 검사는 오류가 없다. 실제 사용자 이해도나 native agent 동작의 실행 검토는 아니다. R1 결과 수락은 Owner에게 남겨 둔다.

## R1-01 원문과 처분 — 2026-10-27

R1-01은 base `17dc804a6af4e168d1bb73aa765e9354db4952ba`, tracked diff SHA-256 `1468cd121cd4b5e65cef063b6aa08019e45c9f99c60336216140ffd02f703578`, packet SHA-256 `943c1779413710b7ca022d228652125a03104849e057cea9f90f60932058e46d`를 검토했다. untracked 계획과 이 작업 기록 및 정규화된 검사 controls도 packet에 포함하고 별도 identity로 대조했다. 실제 Reviewer는 fresh Claude Opus 5.5 (`claude-opus-5-5`), CLI 2.1.310, session `c837a2b7-d53d-4e4f-a7b2-dc14149b3d31`, tools0/MCP0, claude.ai/firstParty/pro다. 202.526399초, exit0, timeout·input drift 없음이다. 정적 검토이며 Reviewer가 tests를 실행하지 않았다.

### Reviewer 최종 응답 원문

# R1 검토 결과: **REVISE**

차단(BLOCKED) 사유는 없습니다. 다만 R1-01부터 R1-04까지는 결과 수락 전에 보정하거나 Owner가 판단해야 합니다. 이 검토는 제공된 diff, 입력 문서와 정규화된 controls를 정적으로 대조한 것입니다. 저는 아무것도 실행하지 않았습니다.

## 주요 결함 (Medium)

### R1-01 · Medium · `docs/CONCEPTS.md`, Five Requests 표 3행 ("Implement this feature and fix issues found by the tests.")

- **문제:** 이 행은 "Establishes the scope … then works within the approved boundary"라고만 씁니다. 두 가지가 빠져 있습니다.
  1. accepted intent나 Work가 없을 때는 intent 초안을 만들고 사람이 수락해야 실행할 수 있다는 점.
  2. "테스트 문제까지 고쳐줘"라는 요청은 테스트나 수락 oracle을 바꿔도 된다는 허가가 아니라는 점.
- **근거:** `GENERAL-WORK.md` Supervised Work Iteration은 "a change to the acceptance oracle requires human approval"과 "does not authorize weakening an oracle"을 명시합니다. 승인 계획도 이 요청 예시들이 "무제한 실행 승인이 아니다"라고 고정했습니다.
- **영향:** 첫 독자가 요청 문장 하나로 실행이 승인되고 테스트도 조정할 수 있다고 이해할 수 있습니다. 이 행은 다섯 요청 중 위험도가 가장 높습니다.
- **최소 수정:** 같은 행에 두 내용을 추가합니다.
  - "What the agent does" 열: "If no accepted intent/Work covers it, prepares an intent for your acceptance first."
  - "Where you decide" 열: "Changing tests or the acceptance checks needs your approval; the request alone is not open-ended execution approval."

### R1-02 · Medium · `docs/REFERENCE.md`, First Example: Documentation Currentness 다음 문단 (신규 문장 "Keep the accepted result and deferred document updates visible in the existing narrative; follow the same scope and reference checks before writing.")

- **문제:** 바로 위에 인용된 규칙은 "Record it … only when authorized and Check Before Writing permits; otherwise report it in conversation as unsaved"입니다. 신규 문장은 "Keep … visible in the existing narrative"라는 명령형입니다.
  - 기록 조건 가운데 checks만 남기고 "only when authorized"를 빠뜨렸습니다.
  - unsaved로 대화에서 보고하는 대체 경로도 빠뜨렸습니다.
  - 보고 시점은 result review에서 handoff와 closeout까지 넓어졌습니다.
- **영향:** 서술 기록이 기본 의무처럼 읽힙니다. 이는 계획의 고정점("조건부 문서 영향 보고를 무조건적 새 규칙으로 바꾸지 않는다")과 amendment 경계에 걸립니다.
  - adapter 쪽 대응 문장("Carry … into the existing handoff or closeout explanation")은 대화 설명이므로 쓰기 의무가 아닙니다. 그래서 adapter 쪽은 수용 가능합니다.
- **최소 수정:** 해당 문장을 다음과 같이 바꿉니다. "Record the accepted result and deferred document updates in the existing narrative only as the rule above permits; otherwise report them as unsaved." 아울러 CHORE 완료 기준 3번의 체크([x])는 이 보정 뒤에 유지합니다.

### R1-03 · Medium (needs-user; 적용 DR이 WORKFLOW 바이트를 고정한다면 High) · `docs/development/WORKFLOW.md`, Close And Assess Adopter Impact의 신규 문단

- **문제:** WORKFLOW는 Owner가 수락한 개발 절차입니다. Rule Changes And Retirement에 따르면 절차 변경에는 DR-0003의 named amendment가 필요합니다. 그런데 index preamble은 DR-0006의 relocation/activation 상태를 조건으로 둡니다.
  - 제공 자료만으로는 WORKFLOW 바이트에 대한 설명성 추가가 amendment 없이 허용되는지 확인할 수 없습니다.
  - index에는 "initial full-file identity does not freeze later authorized navigation"이라는 문장이 있지만, WORKFLOW에 대해서는 그런 문장이 보이지 않습니다.
  - 셋째 문장 "A retained historical status does not become a new task merely because it appears earlier in the index"는 단순 교차참조가 아니라 해석 규칙입니다.
  - 문단이 스스로 "adds no … new acceptance condition"이라고 선언해도, 그것이 경계 판단을 대신하지는 않습니다.
- **영향:** 의미를 바꾸는 절차 개정이 설명 수정이라는 이름으로 들어갈 위험이 있습니다. 반면 이 문단이 없어도 목표인 탐색 연결은 index와 pointer로 이미 달성됩니다.
- **최소 수정 (권고 순서):**
  1. 이 hunk를 제거합니다.
  2. 유지한다면, 해당 DR에 비추어 non-semantic 판단을 내린 Owner의 명시 결정을 CHORE에 기록합니다. 이때 셋째 문장은 삭제합니다.

### R1-04 · Medium · `CHORE-20261027-002`의 "초안과 정적 검사" 및 "보정 검사 결과" 절

- **문제:** WORKFLOW Candidate And Navigation Changes, index preamble, 승인 계획은 모두 navigation 변경의 resulting revision과 bounded diff를 authorizing record에 남기라고 요구합니다. 대상 navigation 변경은 index, FEAT-20261021-002, u2-tool-neutral plan, Host README입니다.
  - 현재 CHORE 기록에는 서술만 있습니다. base, tracked-diff SHA(`1468cd…`), 파일별 before/after digest가 없습니다. 이 식별자들은 R1 packet에만 있습니다.
  - Host README pointer는 검사 뒤에 추가되었으므로 최종 diff identity가 특히 필요합니다.
- **영향:** 결과를 수락하거나 closeout할 때 어떤 navigation 바이트가 승인되었는지 기록만으로 복원할 수 없습니다.
- **최소 수정:** CHORE 기록에 다음을 추가합니다.
  - base commit, 최종 tracked-diff SHA-256 (또는 변경 파일별 SHA-256)
  - navigation hunk 목록과 "검사 이후 추가된 hunk" 구분

## 경미한 결함 (Low)

- **R1-05 · Low (needs-user) · 범위 해석.** `u2-tool-neutral-execution-plan.md`와 `verification/u2-host/README.md`는 승인 계획의 파일별 변경표에 없습니다. 목적과는 맞지만 Driver가 범위를 해석한 결과입니다.
  - **최소 수정:** CHORE에 "계획표 외 추가 파일"로 명시하고 Owner 결과 판단의 대상으로 올립니다.
- **R1-06 · Low · `CONCEPTS.md`의 "Submitted results and accepted required inputs cannot be changed behind an existing ticket."**
  - **문제:** Core는 파일 편집을 막지 못합니다. Collaboration Boundary 절도 이를 명시합니다. 실제 동작은 편집을 막는 것이 아니라 ticket이 stale해지는 것이므로, "cannot"은 enforcement를 과장합니다.
  - **최소 수정:** "must not be changed behind an existing ticket; such a change stales it and needs the supported rework/new acceptance path."
- **R1-07 · Low · `CONCEPTS.md`의 "There are two kinds of continuation here."**
  - **문제:** 제품에서 continuation은 follow-up 기록을 뜻합니다(`view continuation`). 같은 단어로 Work 안의 반복까지 부르면 두 개념이 섞입니다.
  - **최소 수정:** "two kinds of 'keep going'"처럼 표현을 바꾸고, continuation은 follow-up에만 씁니다.
- **R1-08 · Low · `docs/README.md`의 "Source development completion does not qualify every installation or platform."**
  - **문제:** "every"는 일부 설치는 적격이라는 함의를 남깁니다.
  - **최소 수정:** "does not by itself qualify an installation, host or platform beyond its recorded cases."
- **R1-09 · Low · `CONCEPTS.md` 표의 2행과 5행.**
  - 2행("continue")에는 다음이 없습니다.
    - 대상이 여러 개일 때 먼저 확정하는 단계
    - pending recovery를 일반 편집보다 먼저 설명하는 순서
    - 모호한 continue 요청은 읽기만 하고 선택을 저장하지 않는다는 점
  - 5행("Stop")은 unsaved 조건을 submitted/pending으로만 좁혔습니다. 범위 밖 경로, 그리고 reject/revoke 이후 rework 전 상태가 빠졌습니다. 또한 "allowed"는 authorization 요건을 흐립니다.
  - **최소 수정:** 각 행에 짧은 절을 하나씩 추가하거나, Session Handoff 링크와 함께 "authorized and permitted by Check Before Writing"으로 표현합니다.
- **R1-10 · Low · `CONCEPTS.md` 도식 교체.**
  - **문제:** 기존 도식의 "pending is not current"와 "selected acceptance derives completed"가 사라졌습니다. Getting Started와 Reference에는 남아 있지만, 사용자 모델 문서에서 pending의 의미가 약해졌습니다.
  - **최소 수정:** 도식 아래에 한 문장을 복원합니다.

## 확인되어 문제없는 항목

- **설치 안내와 source-only Host 구분:** `docs/README`의 표와 `GENERAL-WORK`/`SKILL`의 추가 문장은 다음을 지킵니다. 설치 manual이 development 파일로 링크하지 않습니다. 일반 update가 Host를 설치하지 않습니다. follow-up 선택이 실행 권한을 확장하지 않습니다.
- **공통 정렬과 선택적 문서 규칙의 분리:** adapter("distinct from the common plan/result/follow-up alignment")와 CONCEPTS 마지막 문단에서 명확합니다. R1-02의 문구 하나만 예외입니다.
- **adapter 도입부:** 예시는 설명용이고 실제 행동은 아래 절차를 따른다는 구분이 적절합니다.
- **개발 pointer:** source A의 실패 상태, 계획의 R0/승인 대기 문구, Host 후보의 미검증 표기를 원문 그대로 보존하고 "성공으로 바꾸지 않는다"를 명시합니다. index 상단은 closed notice와 task 링크만 있고 진행을 복제하지 않습니다.
- **anchor 형식:** `#the-work-cycle`, `#following-a-result`, `#first-example-documentation-currentness`가 heading과 일치합니다.

## 증거 주장 평가

- **실행된 검사:** focused 7개를 같은 ID로 선택·수집·실행했고 7/7 통과입니다. 첫 실패를 실패로 유지하고, 전체 회귀나 사용자 관측으로 주장하지 않습니다. MAINTAINING의 shipped-prose 기준(inventory 및 install/update/repair/detach 소비)과도 맞습니다. 전체 suite를 요구하지 않습니다.
- **adapter 변경의 entry/resume 확인:** 정적 대조만 했습니다. 변경이 문장 몇 개로 한정되어 있으므로 수용할 수 있습니다. 다만 R1-02를 보정하기 전에는 "의미 보존"을 주장할 근거가 부족합니다.
- **검사 후 추가된 pointer가 assertion에 영향이 없다는 주장:** 정적 추론입니다. local-links 테스트가 development 문서를 검사하는지는 제가 확인하지 못했습니다. 다만 Driver의 별도 링크 검사(14개 문서)가 이를 보완합니다.
- **controls에 대한 정적 비판:**
  - Git wrapper는 CLT Git 2.54.0을 쓰고 system/global config를 끕니다. 따라서 이번 PASS는 이 조건에 한정되며, 기본 `/usr/bin/git` shim 경로를 증명하지 않습니다.
  - drift hash는 tracked 파일만 대상으로 합니다. 새 CHORE와 계획 노트 같은 untracked 파일은 감시 밖입니다.
  - `file-read-metadata`는 전역으로 허용됩니다.
  - `focused.sb`에는 치환되지 않은 사용자 홈 경로가 남아 있습니다. 이는 "private 경로만 치환"했다는 control view note와 맞지 않습니다. source에 포함되는 것은 아니지만 packet 위생 문제입니다.
- **범위 밖 관찰:** HOME이 설정되지 않았을 때 설치 preview가 `HV2-INTERNAL`/`RuntimeError`로 끝났습니다. runner 결함으로 분류한 것은 타당합니다. 다만 제품이 진단 메시지 대신 내부 오류를 낸다는 점은 후속 candidate로 기록할지 Owner가 판단할 수 있습니다.

## 한계

- FEAT-20261022-001, OPERATIONS, DR-0003, DR-0006 원문이 제공되지 않았습니다.
  - FEAT 쪽 anchor(`#final-owner-acceptance…`, `#accepted-scope…`), `OPERATIONS.md#interrupted-operations`, Host README의 `#public-history-allocation-boundary`를 확인하지 못했습니다.
  - WORKFLOW의 amendment 상태를 판단하지 못했습니다(R1-03).
- 제공된 계획 노트에는 R0-01 원문, Driver 처분, 승인 이후 CHORE로 가는 dated pointer가 보이지 않습니다. 계획 노트의 상태 줄은 아직 "실행 승인 전"입니다. 따라서 진행 소유자가 하나로 넘어갔는지 확인하지 못했습니다. 실제 파일에 pointer가 없다면 추가해야 합니다.
- Reading Budget은 측정되지 않았습니다. 필수 첫 읽기 문서인 README는 소폭 늘었고, 수락할 때도 미확인으로 남습니다.
- 이전 실제 release에서 이번 후보로의 전환, 실제 native agent 동작, 사용자 이해도는 관측되지 않았습니다.
- 이 검토 의견은 Owner의 결정이 아닙니다. 처분은 Driver가, 결과 수락은 Owner가 합니다.

### Driver disposition

| 항목 | 처분 | 보정 또는 판단 근거 |
| --- | --- | --- |
| R1-01 | revise | 새 업무를 덮는 accepted intent/Work가 없으면 intent 수락부터 준비한다고 명시했다. 이미 승인된 test 변경까지 매번 새 승인을 요구하지는 않는다. test 편집은 승인 범위 안에서, oracle 변경은 Owner 판단으로 구분하고 검증 약화를 금지했다. |
| R1-02 | accept | 서술 기록은 위 규칙이 허용할 때만 저장하고 나머지는 conversation의 unsaved로 보고한다고 명시했다. write authorization과 reference 조건을 유지한다. |
| R1-03 | accept | WORKFLOW 신규 문단을 제거하여 base와 완전히 같은 bytes로 복원했다. 기존 Close/Start/Navigation 및 Maintaining 책임만 적용하며 새 named amendment를 도입하지 않는다. |
| R1-04 | accept | 아래 navigation 파일별 before/after digest, 변경 hunk와 검증 이후 추가 여부, 최종 tracked diff identity를 기록한다. recoverable bytes는 source checkout과 base Git에 있다. digest만 복구 사본으로 간주하지 않는다. |
| R1-05 | needs-user | 파일별 계획표 외 추가는 `u2-tool-neutral-execution-plan.md`와 `verification/u2-host/README.md`의 dated pointer 두 곳이다. 승인된 관련 개발 안내 정렬을 Driver가 이 두 직접 연결 문서에도 적용했다. 기존 본문을 보존했으며 최종 Owner 결과 판단에 이 범위를 명시한다. |
| R1-06 | revise | cannot를 물리적 차단으로 읽지 않도록 금지 행동과 prerequisite 무효화 가능성, 적용되는 rework/new-acceptance 경로로 설명했다. 과거 완료 ticket이 항상 stale해진다고 단정하지 않는다. |
| R1-07 | accept | Work 안 반복을 continuation이라고 부른 도입 문장을 제거했다. continuation은 기록된 follow-up을 설명하는 곳에만 사용한다. |
| R1-08 | accept | source 완료만으로 해당 설치·host·platform 지원이 성립하지 않는다고 명확히 썼다. |
| R1-09 | accept | 모호한 재개는 read-only, target 확인과 pending 설명이 편집보다 먼저임을 명시했다. 중단 기록은 authorized + Check Before Writing 전체 조건으로 표현하여 submitted/pending 외 제한도 유지했다. |
| R1-10 | accept | pending 자체가 current를 바꾸지 않으며 selected accepted result가 completed를 만든다는 설명을 복원했다. |

일부 도식 문구도 `completion/residual wording` 대신 `proposed plan update`, `plan alignment` 대신 무엇이 완료·잔여인지 설명하는 문장으로 고쳐 첫 독자의 부담을 줄였다. 이 변경은 같은 타이밍·권한 의미를 유지한다.

### R1 근거 한계와 부가 관찰

- 첫 packet의 controls view에서 사용자 홈 ancestor 경로의 정규화가 빠졌다. 도입처 파일이나 자료는 포함되지 않았지만 private 경로를 모두 치환했다는 note는 정확하지 않았다. 후속 packet은 홈 ancestor까지 치환하고 식별 가능한 절대 경로 잔여를 확인한다. 원 packet과 Reviewer 관찰은 보존한다.
- tracked-file drift 검사와 untracked 계획/CHORE의 보호를 구분한다. tests 실행 중 source 편집을 하지 않았으나 그 runner의 drift 해시가 untracked 파일까지 확인했다고 주장하지 않는다. Reviewer packet은 untracked 두 파일도 전후 hash로 확인했다.
- Seatbelt는 metadata를 전역에 허용한다. 내용 읽기·쓰기·네트워크 경계와 whole-host confidentiality를 동일시하지 않는다. 검사 PASS는 CLT Git 2.54.0 wrapper 조건이며 기본 `/usr/bin/git` 경로의 PASS가 아니다.
- HOME 누락에서 제품이 내부 오류를 보인 관측은 사실로 남긴다. 진단 개선을 별도 candidate로 기록하거나 구현하는 일은 선택하지 않았다.
- 승인 계획의 R0 원문·Driver 처분·CHORE dated pointer는 실제 파일에 있으며 첫 R1 packet에는 앞부분만 제공했다. Owner 승인 원래 bytes `[0,31416)`는 그대로 유지한다. 후속 검토에는 이 생략 범위와 pointer를 제공한다.

managed 파일 3개의 R1 보정으로 이전 `95c67e…` 후보와 최종 문서 후보의 identity는 달라진다. 7/7 결과는 그 이전 후보의 실행으로 보존하고 최종 후보가 이미 통과한 것으로 쓰지 않는다. 모든 보정을 모은 뒤 같은 7개 consumer 검사의 추가 1회가 필요한 이유이며, 15분 test lane과 전체 120분 한도는 유지한다.

### 최종 navigation 변경 identity

기준 source는 `17dc804a6af4e168d1bb73aa765e9354db4952ba`, R1 보정 후 tracked diff SHA-256은 `5fcd427ae015e5b73be6f51ea8564e3e1726c5cf6fe1d725950d22f27ab8a06a`이다. 아직 commit 전이므로 아래 after digest가 결과 revision의 파일 identity다. base Git과 현재 worktree가 해당 bytes를 보존한다.

| Navigation file | Before SHA-256 | After SHA-256 | Bounded hunk / 검사 시점 |
| --- | --- | --- | --- |
| `docs/development/README.md` | `cc7daed3c9b6212e0d1b780851bc413f0700c7422027465c9a614d7a59d8a38e` | `256c133f93df5070bc6b80f6e1daada1ed29851acf8eaf9184522d47344873aa` | 상단 closeout/task 링크와 source A notice만 변경; 7/7 이전 |
| `docs/development/FEAT-20261021-002-u2-single-host-source.md` | `f88f63afe9f759608d98091d8547015b5f58500d024f9cbb10dd68ad3d4814a0` | `c2ce8c52578e15afd7652ef6d0153d5a7001e5f483cc7706a0683739bb1e9609` | 제목 뒤 dated pointer 삽입만; 7/7 이전 |
| `docs/development/u2-tool-neutral-execution-plan.md` | `a8e6ce48a0d162e70a6e5095df60d6100fe785a8e36d05571d16528ad7306f1d` | `bc0a84443880889c7dfb9c86298496a23886c141cee540ca43850c304008ec6e` | 제목 뒤 dated pointer 삽입만; 7/7 이전; 계획표 외 추가 |
| `docs/development/verification/u2-host/README.md` | `fb2b4c22568639d779e120a5a7676fae825a215996b07d1958f4a39868cc7519` | `12574e1bb0f8778640470f64b5a3b6cea44487fce8d07a20b160a11214c430c0` | 제목 뒤 dated pointer 삽입만; 7/7 이후 추가; managed/test 소비와 무관; 계획표 외 추가 |

세 predecessor 문서는 삽입 부분을 제외한 기존 제목·본문이 base와 byte-for-byte 같다. WORKFLOW는 base와 동일하며 신규 절차 조항은 없다.

### 최종 후보 검사 추가 승인

Owner는 R1 재검토를 마친 최종 문서 후보에 같은 7개 consumer 검사를 1회 수행하는 질문에 “최종 후보 검사 1회 승인”이라고 답했다. 승인된 문서 범위 안의 재검토 보정을 모두 마친 뒤 입력을 고정하며 같은 환경·assertion·권한, 남은 test lane 825초와 전체 120분 한도를 유지한다. 현재 보정 후보는 `product-release-556631f00c805a437c03faab`, inventory SHA-256 `556631f00c805a437c03faabe0eb7320a4aff52d1922a6d992dd5f088651fe30`이다. 최종 실행 전 identity를 다시 확인한다.

## R1-02 정적 재검토 결과 — 2026-10-27

실제 Reviewer는 fresh Claude Opus 5.5, CLI 2.1.310, session `4595106e-7c03-4bbd-93d9-995fc650ef09`, tools0/MCP0, claude.ai/firstParty/pro다. 64.457025초, exit0, timeout·input drift 없음. packet SHA-256 `a1376e86e58e125c619f6057084af3969afbd25bd0ea67474d1020b2da0f374a`, tracked diff `5fcd427ae015e5b73be6f51ea8564e3e1726c5cf6fe1d725950d22f27ab8a06a`를 검토했다. Closeout 발췌의 private 대상명 한 곳은 Reference A로 중립화한 view이며 원문 전체 bytes와 동일하다고 주장하지 않는다.

### Reviewer 최종 응답 원문

# R1-02 검토 결과: **PASS** (정적 문서 준비 상태에 한정)

R1-01부터 R1-10까지의 처분은 현재 문서에 의미를 유지한 채 반영되었습니다. 남은 차단 사유도 없습니다.

이 PASS는 제공된 현재 본문, base 대비 전체 diff, Driver 처분과 navigation identity를 정적으로 대조한 결과입니다. 저는 아무것도 실행하지 않았습니다. 다음 사항은 이 판정에 포함되지 않습니다.

- **최종 후보 실행:** `product-release-556631f00c805a437c03faab`(SHA-256 `556631f0…fe30`)에 대한 같은 7개 검사 1회는 아직 실행되지 않았습니다. 따라서 통과로 보지 않습니다. 기존 7/7은 이전 후보 `95c67e…`의 결과입니다.
- **결과 수락:** 이 검토는 Owner의 결과 수락이 아닙니다.

## 처분 확인

| 항목 | Driver 처분 | 확인 |
| --- | --- | --- |
| R1-01 | revise | **해소.** 표 3행에 두 내용이 추가되었습니다. accepted intent/Work가 없으면 intent 수락을 먼저 준비합니다. "changes to the acceptance checks"는 사람이 결정하며, 이 요청은 "does not permit weakening a check"라고 명시합니다. GENERAL-WORK의 "oracle 변경은 사람 승인, 약화 금지"와 일치합니다. 승인 범위 안의 test 편집까지 매번 다시 승인받게 하지 않는 해석도 타당합니다. 무제한 실행이 아니라는 점은 "within that approved boundary"와 Approval 절이 함께 전달합니다. |
| R1-02 | accept | **해소.** "only as the rule above permits; otherwise report them in conversation as unsaved"로 바뀌어 authorized 조건, Check Before Writing, unsaved 대체 경로가 모두 복원되었습니다. handoff와 closeout 시점의 *설명*은 쓰기 의무가 아니므로 수용합니다. 이 선택 규칙과 공통 plan/follow-up 흐름의 독립성도 명시되었습니다. |
| R1-03 | accept | **해소.** diff에 WORKFLOW hunk가 없고, CHORE 기록에 base와 동일하다고 적혀 있습니다. 새 named amendment는 필요하지 않습니다. |
| R1-04 | accept | **해소.** base, tracked diff SHA `5fcd427a…`, 파일 4개의 before/after digest, hunk 범위, 7/7 실행 이전·이후 추가 구분이 기록되었습니다. digest를 복구 사본으로 보지 않는다는 한계도 적절합니다. |
| R1-05 | needs-user | **Owner 판단 대상으로 남습니다.** 계획표 밖의 두 파일은 CHORE 기록에 명시되었습니다. |
| R1-06 | revise | **해소.** "Do not change … the edit can invalidate its prerequisites"는 물리적 차단을 주장하지 않습니다. stale이 항상 발생한다고 단정하지도 않습니다. 해당 rework/new-acceptance 경로로 안내합니다. |
| R1-07 | accept | **해소.** Work 안의 반복은 "checking and correcting"으로 부릅니다. continuation은 follow-up 경로에만 씁니다. GENERAL-WORK 신규 문장도 같은 구분을 따릅니다. |
| R1-08 | accept | **해소.** "alone does not establish support for your installation, host or platform"으로 바뀌어 "every"가 남기던 함의가 사라졌습니다. |
| R1-09 | accept | **해소.** 2행에 모호한 대상 확정, pending을 편집보다 먼저 설명, 모호한 요청은 read-only이며 선택을 저장하지 않음이 들어갔습니다. 5행은 authorized와 Check Before Writing 전체 조건을 씁니다. 이로써 범위 밖 경로와 reject/revoke 이후 제한도 포함됩니다. |
| R1-10 | accept | **해소.** pending이 current를 바꾸지 않는다는 문장과 selected accepted result가 completed를 만든다는 문장이 도식 아래에 복원되었습니다. |

## 이전 한계의 해소

- **Anchor:** `#final-owner-acceptance-and-work-done--2026-10-27-kst`, `#accepted-scope-and-remaining-limits`, `OPERATIONS.md#interrupted-operations`, `#public-history-allocation-boundary`, `#current-navigation--2026-10-27`, `#following-a-result`가 모두 제공된 heading의 GFM slug와 일치합니다.
- **계획 노트의 handoff pointer:** "실행 승인과 진행 소유권 — 2026-10-27" 절이 실제로 있습니다. 승인된 원래 bytes `[0,31416)`를 보존하기 위해 pointer를 뒤에 덧붙인 방식은 타당합니다. 진행 소유자는 CHORE 하나로 정리됩니다.
- **R1 보정 범위:** CONCEPTS, REFERENCE, docs/README 세 파일입니다. CHORE의 "managed 파일 3개"와 맞습니다. adapter는 R1 이후 바뀌지 않았습니다.

## 비차단 편집 권고 (Low)

세 항목은 모두 untracked CHORE 기록만 고칩니다. 따라서 managed inventory `556631…`와 tracked diff `5fcd427a…`의 identity는 바뀌지 않습니다. 최종 실행 전 입력 고정과 함께 처리하면 됩니다.

1. **CHORE 상단 상태 줄:** "R1과 결과 수락은 아직 이루어지지 않았다"는 이제 사실과 다릅니다. "R1 REVISE 처분 및 R1-02 재검토 완료, 최종 후보 검사와 결과 수락 대기"로 갱신하기를 권합니다.
2. **완료 기준 5번의 [x]:** 기록 행위 자체는 끝났지만, 체크 표시가 최종 후보 검사 완료로 읽힐 수 있습니다. "7/7은 이전 후보 `95c67e…`의 결과, 최종 후보 `556631…` 실행은 pending"이라는 한 줄을 덧붙이기를 권합니다.
3. **"초안과 정적 검사" 절:** "WORKFLOW에는 … 교차참조만 추가했다"는 이후 R1-03에서 제거된 사항입니다. 당시 이력으로 보존하되, 문장 끝에 "(R1-03에 따라 제거, base와 동일)"을 덧붙이기를 권합니다.

이번 수정 이후 managed 또는 tracked 파일을 편집한다면 다음 두 가지를 다시 해야 합니다.

- 최종 navigation identity 표와 tracked diff SHA를 갱신합니다.
- 최종 실행 전 identity를 다시 확인합니다.

## Owner만 결정할 사항

- **R1-05:** 계획표 밖 두 파일(`u2-tool-neutral-execution-plan.md`, `verification/u2-host/README.md`)의 dated pointer를 결과 범위로 수락할지 판단합니다.
- **최종 7개 검사:** 실행 결과를 받은 뒤 결과 수락 여부를 결정합니다. 최종 후보 검사 1회는 이미 승인되어 있습니다(남은 825초, 전체 120분).
- **미확인 상태로 남는 항목의 수락 여부:**
  - 읽기 token budget (`tiktoken` 없음)
  - 이전 실제 release에서 이번 후보로의 정확한 전환
  - 실제 사용자와 native agent의 동작
- **선택 사항:** HOME이 없을 때 발생하는 `HV2-INTERNAL` 진단 개선을 별도 candidate로 기록할지 결정합니다.
- **이번 승인에 포함되지 않은 작업:** commit, push, release, 도입처 적용은 별도 승인 대상입니다.

Driver의 source 보정 처분과 Owner의 결과 수락은 서로 다른 단계입니다. 이 Reviewer 판정은 둘 중 어느 것도 대신하지 않습니다.

### Driver 처분과 최종 검사 준비

PASS는 정적 문서 준비 상태에만 적용한다. 비차단 권고 3건을 accept하여 상단 현재 상태를 갱신하고, 최종 후보 검사 전 완료 기준 5번을 미완료로 두었다. 이전 초안 절의 WORKFLOW 추가 설명은 당시 이력이며 R1-03에서 제거하여 현재는 base와 동일하다. 이전 7/7은 95c67e 후보의 결과다. 최종 556631 후보에 대해 승인된 7개 검사 1회를 수행한다. 계획표 밖 pointer 두 곳과 남은 미관측 범위는 Owner 결과 판단 대상으로 보고한다. HOME 진단 개선 candidate는 새로 기록하지 않는다.

## 최종 후보 실행 결과와 결과 수락 준비 — 2026-10-27

R1-02 이후 고정한 `product-release-556631f00c805a437c03faab`(inventory SHA-256 `556631f00c805a437c03faabe0eb7320a4aff52d1922a6d992dd5f088651fe30`)에 승인된 같은 7개 consumer 검사를 한 번 실행했다. 선택·수집·실행 ID가 일치하며 7/7 통과, skip/failure/error/expected failure/unexpected success는 모두 0이다. normal final GIL-enabled CPython 3.14.7, CLT Git 2.54.0 wrapper 및 기존 Seatbelt 조건이다. file/network canary 통과, source/runtime drift와 timeout 없음, exit 0이다. test body 66.224초, controller 포함 66.391916초를 사용했다.

세 실행의 test lane 누적은 141.183720초(약 2.35분/15분), R0·R1·재검토의 reviewer 누적은 371.804783초(약 6.20분/45분)다. 첫 환경 실패는 실패 기록으로, 이전 후보 7/7은 이전 후보의 근거로 보존한다. 최종 실행 뒤 managed/source tracked bytes는 변경하지 않았다. 앞의 navigation 표에서 “7/7 이전·이후”는 두 번째 실행 시점을 뜻하며 최종 실행에는 모든 해당 pointer가 이미 포함되어 있었다.

Owner 결과 판단에는 계획표 밖 dated pointer 두 곳(`u2-tool-neutral-execution-plan.md`, `verification/u2-host/README.md`)을 포함한다. 읽기 token budget, 이전 실제 release→최종 후보의 정확한 전환, 실제 사용자 이해도와 native agent 동작은 여전히 미확인이다. 정적 문서 준비와 선택한 consumer 결과만 수락 대상으로 제시한다. commit/push/release/도입처 적용은 포함하지 않는다.

결과 수락 뒤 이 문서 작업을 Done으로 처리할 수 있다. 이후 U2 실제 적용 계획은 위 “적용 공백”의 고정 실행 묶음·실제 대상·권한·검증·복구 조건을 먼저 구체화해야 한다. 그 준비는 이번 문서 결과 수락만으로 실행 승인되지 않는다.

## 사용자 매뉴얼 문장·흐름 보강 요청과 계획 — 2026-10-27

Owner는 결과 수락 대신, 보강된 편집 지침을 사용하여 기존 문서를 모두 읽고 반복되는 방어적 부정·번역투·내부 검토용 표현과 같은 문제를 찾아 고치라고 요청했다. 사실·중요 조건·경고·의무와 이미 자연스러운 부분은 유지하며, 필요한 문장·문단 재구성을 허용했다. 범위 질문에는 “사용자 매뉴얼 전체: 루트 README와 docs 바로 아래 문서, 연결된 agent 안내”를 선택했고, 이어 “다 보는게 좋을까? 네가 판단해서 조정해!”라고 맡겼다. Done 승인은 받지 않았으며 같은 작업 기록에서 계속한다.

읽기 대상은 루트 README, docs 바로 아래 Markdown 14개, AGENTS·CLAUDE와 adapter의 총 18개다. 현행 매뉴얼과 agent 안내의 필요한 표현만 수정한다. 두 generation 계약과 Decision Guide의 역사·보존 인용은 의미 확인용으로 읽되 그대로 보존한다. decisions·development·fixtures 전체 재작성은 제외하며 필요한 계약 근거만 대조한다. 편집 지침은 별도 배포/설치 없이 Owner가 지정한 최신 작업본의 읽기 입력을 고정해 사용한다. 해당 도구를 배포하거나 설치하지 않는다.

의미 보존 기준은 사실·검증 범위, 승인자와 실행자, 의무 강도, 전제·예외·위험·복구 순서, 숫자·버전·명령·경로·코드·상태·링크다. 직접 인용과 보존 이력은 byte-identical로 둔다. 각 수정은 원문 범위와 독자 문제를 연결하고, 단순 동의어 교체나 자연스러운 문장의 임의 재작성은 하지 않는다. 문단 재구성은 중복 설명 또는 선행 조건의 위치 문제를 문장 수정으로 풀 수 없을 때만 한다. 실행 규칙·계약 의미는 바꾸지 않는다.

누적 변경은 설명/agent 지침이며 runtime·test·assertion·권한 구현은 그대로다. 이전 7/7은 보강 전 후보의 근거로 남기고 새 후보에 재표시하지 않는다. 전면 suite는 반복하지 않는다. 새 후보에는 링크·GFM·disclosure·heading 유지, 코드/인용/식별자 보존, managed inventory와 변경된 entry/resume 의미 대조, 기존 7개 consumer 검사를 최종 1회 수행하는 계획이다. 문서 보정을 모은 뒤 candidate를 고정하며 같은 CPython 3.14.7, CLT Git wrapper, Seatbelt, normal 모드, assertion, 45초 subprocess 한도를 사용한다. test lane 15분 중 141.183720초를 사용했으므로 남은 758초 이내로 정한다. 실패 시 자동 재실행하지 않는다.

작업 예상은 편집·보존 점검 35–50분과 reviewer 대기 5–10분이다. 이는 18개/2,207줄의 문서 규모에 대한 판단이며 편집 실측은 아니다. 검사 자체는 앞선 성공 실행 66–74초를 근거로 약 1–2분을 예상한다. 기존 실행 착수 후 누적 120분 한도와 중단 시각 11:52:55 UTC를 유지한다. review 대기는 포함하고 Owner 응답 대기는 제외하며 겹친 시간은 한 번만 센다. 범위 또는 실제 소요가 이 한도를 넘으면 미완료 부분과 후속 비용을 보고한다.

기존 검토 승인의 잔여 follow-up 1회를 이 추가 계획의 R0 보충 검토에 사용할 수 있다. 새 결과 R1 1회는 기존 횟수를 넘으므로 추가 승인을 요청한다. 각 15분·누적 reviewer 45분과 tools0/MCP0·동일 subscription 경계를 유지한다. 이 계획과 R0 보정 내 편집·최종 focused 1회까지를 구체적 실행 범위로 제시한다. Git·배포·도입처 적용·새 구현은 제외한다.

보강 전 18개 문서 bytes는 private task의 최소 비교 입력으로 보존했다. 코드 전체를 복제하지 않았으며, 기존 Git base와 함께 문장 보존 대조·검토·기존 결과 복원에 사용한다. 보강된 결과 수락과 source 통합 후 이 소비가 끝나면 정리 여부를 재평가한다. R1 중복 raw stream·응답·빈 stderr 6개는 원문이 이 기록에 그대로 있고 결과 metadata가 보존되었으며 열린 파일이 없음을 확인한 뒤 정리했다. 활성 경로는 바뀌지 않았다.

## 문장 보강 R0 보충 검토와 처분 — 2026-10-27

fresh Claude Opus 5.5, CLI 2.1.310, tools0/MCP0, claude.ai/firstParty/pro, session `959f5521-d827-47b0-8352-22b5811c77bd`. 정적 검토 REVISE, 91.695393초, exit0, timeout/input drift 없음. packet SHA-256 `78d63c9cdbfa43157982dea6feb2577854b0e9ab6e6d9f661f8cbd4edfecee89`. 이는 추가 계획의 검토이며 새 편집 결과의 PASS가 아니다.

### Reviewer 응답 원문

# R0 보충 계획 검토 — 판정: **REVISE**

계획의 범위 선택, 의미 보존 기준, 검증 선택(전면 suite 미반복, 기존 7/7 재표시 금지, 최종 7-consumer 1회), 시간·회차 한도는 대체로 타당합니다. 다만 실행 전에 보정해야 할 보존 경계 누락이 세 가지 있고, 검증 순서에도 공백이 하나 있습니다. 새 구현, 프레임워크, 레지스트리는 필요하지 않습니다.

## 유지할 점

- 읽기 대상 18개 산정이 정확합니다. 루트 README, docs 바로 아래 14개, AGENTS·CLAUDE·adapter입니다. `docs/development/`와 decisions를 제외한 판단도 사용자 선택과 맞습니다.
- 두 generation 계약을 읽기 전용으로 둔 판단, 코드·인용·식별자·heading 보존, 문단 재구성을 구조 gate 통과 시로 제한한 점이 편집 계약과 일치합니다.
- shipped prose-only 변경에 대해 inventory 대조, consumer 경로, entry/resume 정적 대조를 선택한 것은 Maintaining의 기준에 부합합니다.
- R1을 추가 승인 대상으로 분리했고, private 비교 입력에는 소비처와 종료 조건이 명시되어 있습니다.

## 발견사항

**1. [Blocking 위험] Decision Guide 편집 권한이 불명확합니다**
- 계획은 "역사·보존 인용"만 고정합니다. 그러나 Decision Guide는 사용자 매뉴얼이 아니라 DR-0006이 소유하는 source-only 결정 절차 문서입니다. 문서 색인에도 없습니다.
- WORKFLOW의 Rule Changes는 2026-10-07 수락 절차를 바꾸려면 Owner가 수락한 named amendment가 필요하다고 정합니다. 이 때문에 Acceptance Records, Document Identity And State, 카탈로그 상태 문구를 문장만 다듬어도 수락된 절차 텍스트를 바꾸는 것이 될 수 있습니다.
- Retained Source Procedures 절도 위험합니다. byte 범위, SHA-256, 320-byte 설명, `git show` 명령, DR-0003/0004 관계 문장 전체가 정확한 역사 식별자인데, 현재 문구로는 이 절이 잠금 대상인지 모호합니다.
- 편집 계약도 host workflow가 소유한 승인 경계를 우회하지 말라고 정합니다.

**2. [Blocking 위험] frozen preparation label이 정규화될 수 있습니다**
- README의 Entry-1 Candidate와 Decision Guide는 DR-0004가 "retained preparation labels"를 동결했다고 명시합니다. 대상은 "Implementation Candidate" heading, "Candidate permission amendment (not activated)", "(Development)", "development candidate/checkout" 같은 표기입니다.
- 이 표기들은 내부 검토어나 번역투처럼 보이지만 활성화 상태와 역사적 식별을 담고 있습니다.
- WORKSPACE-CONTRACT·OPERATIONS의 Entry-1/Checkout-1 절도 같은 문제를 안고 있습니다. 이 절들은 스스로 "retained ... clauses"라고 선언하므로, 재구성하면 보존 주장과 실제 텍스트가 어긋납니다.

**3. [Major] 필요한 참조 계약 없이 Korean span이 수정될 수 있습니다**
- adapter에는 agent가 그대로 말하도록 지정한 한국어 문구가 있습니다. 예: "기준만 갱신하며 작업 결과를 수락하거나 완료하지 않습니다.", "완료 기록 X와 내용 일치, 변경 원인 미확인.", "연결 미저장", Candidate 표의 한국어 요청 예시.
- 같은 언어 Korean `Revise`에는 `references/en-ko-adaptation.md`가 필수인데, 이번에 고정된 계약 입력에 없습니다. 계약은 필수 참조를 로드할 수 없으면 수정 전에 멈추라고 정합니다.

**4. [Major] agent 대상 파일의 부정 규칙과 skill frontmatter가 보호되지 않습니다**
- AGENTS·CLAUDE·adapter의 "does not prove / is not approval" 문장은 독자 설명이 아니라 agent의 추론을 금지하는 운영 규칙입니다. 반복을 줄이는 것은 허용되지만, 금지 효과를 직접 규칙으로 남기지 않고 삭제하면 행동 계약이 바뀝니다.
- adapter의 `name`·`description`은 host가 skill을 고르는 트리거입니다. 이를 바꾸면 실제 native 로딩 동작이 달라질 수 있는데, 이번 검증으로는 확인되지 않습니다.

**5. [Major] R1과 최종 consumer 실행의 순서가 비어 있습니다**
- 계획은 "보정을 모은 뒤 고정 → 최종 1회"이고 R1은 별도 승인으로 둡니다.
- R1이 consumer 실행 뒤에 REVISE를 내면, 이후 편집은 실행 대상 candidate와 달라집니다. 그런데 재실행 여부와 예산(758초 잔여)이 정의되어 있지 않습니다.

**6. [Minor] 시간 초과 시 처리와 미검증 항목 보고가 빠져 있습니다**
- 2,207줄의 밀도 높은 계약 문서에 35–50분은 빠듯합니다. 한도에 도달했을 때 편집 중인 파일을 어떻게 처리할지, candidate를 어떻게 고정할지 정해져 있지 않습니다.
- AGENTS, README, GETTING-STARTED를 편집하면 reading budget(2,000 / 4,000 tokens) 측정 입력이 바뀝니다. 측정하지 않을 계획이라면 "준수 주장 없음, 미검증"을 명시해야 합니다.
- entry/resume 정적 대조가 실제 agent 행동을 검증하지 않는다는 점도 보고 범주에 넣어야 합니다.
- 7개 파일에 같은 "This retained heading explains…" 문단이 반복됩니다. 이를 고친다면 파일마다 같은 의미로 맞춰야 합니다.

## 최소 보정

기존 계획 기록에 아래 문장들을 추가하거나 교체하면 됩니다.

1. "Decision Guide는 DR-0006·WORKFLOW 개정 경로가 소유하는 source-only 절차 문서이므로 이번 작업에서는 전체를 읽기 전용으로 둔다. 문제가 보이면 수정하지 않고 보고하며, 별도 amendment 후보로 남긴다."
2. "DR-0004가 동결한 preparation label과 heading('Implementation Candidate', '(not activated)', '(Development)' 등), 그리고 스스로 'retained/historical clauses'라고 선언한 절(Entry-1·Checkout-1 transition/admission/detach, Historical Observations 표)은 의미·라벨·문단 구조를 바꾸지 않는다. 명백한 문장 결함은 해당 문장 안의 국소 편집만 허용한다."
3. "adapter의 한국어 문구는 en-ko 참조 계약이 입력에 없으므로 byte-identical로 잠근다. skill frontmatter의 `name`·`description`도 잠근다."
4. "agent 대상 파일의 'does not prove/authorize' 문장은 같은 금지를 직접 규칙으로 남기는 경우에만 축약한다."
5. "순서는 편집 → 보존·링크 정적 점검 → R1(승인 시) → R1 반영 → candidate 고정 → 7-consumer 1회로 한다. 고정 이후의 변경은 이 실행을 무효로 하며, 재실행은 잔여 예산 안에서 Owner가 결정한다."
6. "한도에 근접하면 진행 중인 파일을 되돌리고, 완료된 파일만으로 고정·검사한 뒤 미완료 파일 목록을 보고한다. reading budget과 실제 agent/native 행동은 미검증으로 보고하고 준수 주장은 하지 않는다."

## 판정 한계

- 이 판정은 제시된 계획과 원문에 대한 정적 검토입니다. 새 편집 결과는 아직 존재하지 않으므로 검토하지 않았습니다.
- DR-0004·DR-0006 본문은 입력에 없습니다. 따라서 발견사항 1·2는 현행 문서에 적힌 그 결정들의 서술에 근거합니다.
- 위 보정을 반영하면 실행 착수에 대한 계획상 장애는 남지 않습니다.

### Driver 처분과 적용 계획

| 항목 | 처분 | 반영 |
| --- | --- | --- |
| 1 | accept | Decision Guide 전체를 읽기 전용으로 둔다. 현재 source-only 절차와 역사 식별자를 재작성하지 않는다. 이번 편집으로 새 amendment나 후보를 등록하지 않는다. |
| 2 | revise | 모든 heading·preparation label을 보존한다. 두 generation 문서, 스스로 retained/historical clauses라고 지정한 Checkout-1/Entry-1 절과 Historical Observations 표는 이번 편집에서 전체를 잠근다. 현행 설명 문장에서 과거 결과를 설명하는 부분은 사실·범위·숫자를 보존하며 명시적으로 표시한 span만 고친다. |
| 3 | accept | 한국어 직접 인용·요청 예시·출력 문구를 포함한 모든 한국어 span은 byte-identical로 둔다. 한국어 본문을 편집하지 않으므로 별도 adaptation 참조를 로드하지 않는다. |
| 4 | accept | AGENTS·CLAUDE·adapter의 부정 규칙은 같은 금지 효과를 직접 명시한 경우에만 고친다. adapter frontmatter 전체를 잠근다. |
| 5 | accept | 편집 → 보존·링크 정적 검사 → 추가 승인된 R1 → 범위 내 R1 보정 → 최종 candidate 고정 → 같은 7개 consumer 검사 1회 순서다. 고정 이후 affected bytes가 바뀌면 이전 결과를 새 후보에 쓰지 않으며 필요한 추가 실행은 별도 판단한다. |
| 6 | revise | 중단 한도에 근접하면 편집 중인 파일을 보강 직전 bytes로 되돌리고 완료 파일·미완료 파일을 구분한다. 검토/검사까지 끝낼 시간이 없으면 해당 단계를 미완료로 보고하며 미검증 상태를 PASS로 고정하지 않는다. reading budget과 실제 agent/native 행동은 미검증이다. 반복되는 공통 문단은 같은 의미의 금지·조건을 일관되게 유지한다. |

18개 문서의 전체 읽기를 마쳤다. 실제 수정은 현행 설명의 독자 문제를 해결하는 범위로 좁힌다. 앞선 승인된 R0/R1과 follow-up 2회는 이 보충 검토까지 모두 사용했다. Reviewer 누적 사용은 463.500175초이며 누적 45분 한도 중 2,236.499825초가 남는다. 추가 R1 1회만 요청하며 자동 재검토는 포함하지 않는다. 최종 consumer 1회는 기존 7개 ID와 controls 의미를 유지하고 758초 한도를 사용한다. 이 실행에는 실제 도입처·비밀자료·네트워크를 사용하지 않는다.


## 문장 보강 실행 승인과 결과 — 2026-10-27

Owner는 구체화한 추가 범위에 “편집·R1 1회·최종 검사 1회 승인”이라고 답했다. 같은 120분 누적 한도, reviewer 각 15분/누적 45분, 기존 7개 consumer 1회/잔여 758초, 동일 환경·assertion과 자동 재실행 금지 조건을 유지한다. Git·도입처 적용 승인은 포함하지 않는다.

18개를 모두 읽고 현행 설명 14개를 고쳤다. Decision Guide·두 generation 계약·CLAUDE는 byte-identical로 유지했다. 수정은 독자 문제와 원문 span에 연결한 93개 순차 편집 단계다. 직접 승인·관측 근거를 설명하도록 방어적 문장과 번역투를 고쳤으며, 문단 재구성은 docs index의 delegation 설명 분리·중복 정리와 Reference의 Human Review 사용 안내 뒤로 내부 캐시 설명 이동 두 곳뿐이다. 마지막 이동은 문단 내용 그대로다. 명령·구조·새 규칙을 추가하지 않았다.

보강 전 후보에서 순차 편집을 재생하면 현재 18개 파일과 정확히 일치한다. 매핑 밖 변경 0개이며 코드 block·inline code·heading·링크·숫자·직접 인용·한국어 줄, frontmatter와 잠근 역사 구간·표가 보존되었다. 첫 정적 checker는 Historical Observations의 표 대신 주변 설명 전체를 잠그는 과도한 assertion으로 실패했다. 승인 범위의 표를 정확히 대조하도록 checker만 바로잡았고 본문은 바꾸지 않았다. 보강 후 정적 검사에서 변경/기록 20개 문서, 284개 local link, 316개 heading의 오류는 0개다. managed 30개 목록은 같고 그중 문서/지침 14개 bytes가 바뀌었다. runtime·tests·launcher·Capability Declaration은 unchanged다.

### 진입·재개 정적 의미 대조

| 사례 | 유지된 설명과 경계 | 대조 위치 |
| --- | --- | --- |
| 현재 상태·다음 작업 질문 | 실제 Work·plan·candidate·continuation을 읽고 추천하며 선택·실행은 별도 판단 | Concepts 다섯 요청, adapter Follow-Up And Plan Alignment |
| 이전 작업 재개 | selected Work와 plan reference·continuation을 읽고 같은 유효 승인을 재사용; 모호한 요청은 read-only | Concepts Approval, Pause And Resume; AGENTS; adapter |
| 기능 구현·검사·보정 | 수락된 intent/Work·scope·verifier·누적 시간/횟수 한도 안에서 수행; 새 exact acceptance는 사람 판단 | Concepts 다섯 요청; General Work supervised iteration |
| 결과를 계획에 반영 | 수락 전 완료/잔여 초안, 수락 후 실제 결과와 남은 문서 편집 설명; 쓰기 가능성 먼저 확인 | Concepts work cycle/following result; adapter; Reference Check Before Writing |
| 중단·다음 세션 | 입력·복구 증거와 소진 한도 보존, 기존 narrative의 허용된 handoff; scheduler/자동 재개 없음 | Concepts; Reference Session Handoff And Resume |
| pending·stale·새 결과 수락 | pending은 원 request/ticket 복구, stale required reference 거부·rebind/resubmit 경로 유지, 새 result의 exact acceptance 구분 | Reference installed port/acceptance, adapter result review, Operations recovery |

위 표는 지침 간 정적 대조이며 실제 agent 실행·사용자 이해도 관측이 아니다. 읽기 token budget과 정확한 기존 실제 release→새 후보 전환은 미확인이다. 앞선 7/7과 Reviewer PASS는 보강 전 bytes에만 적용한다. 다음 순서는 R1 → 범위 내 보정 → 최종 후보 고정 → 기존 7개 consumer 1회다.


## 문장 보강 R1과 Driver 보정 — 2026-10-27

fresh Claude Opus 5.5, CLI 2.1.310, tools0/MCP0, claude.ai/firstParty/pro, session `0864630b-1927-4d35-919e-aee963ea85eb`. 정적 판정 REVISE, 185.332521초, exit0, timeout/input drift 없음. packet SHA-256 `560c709daff039ed839b475a305fc51e14c3909cfca2b072f76a3aa2f9413f26`, reviewed tracked diff SHA-256 `36791b8df42537b20b413e859a50d29bb8f783c91260a2cb7ef2708a210847b1`. 현행 매뉴얼 전문과 보강 diff·편집 계약·관련 source 절을 전달했으며 이전 개발 이력과 결정 문서는 필요한 절만 발췌했다. reviewer는 실행을 하지 않았다.

### Reviewer 응답 원문

````markdown
# R1 정적 검토 — 판정: **REVISE**

이 판정은 제시된 diff와 현재 전문, 편집 계약을 대조한 정적 검토입니다. 실행, 테스트, Owner 수락은 포함하지 않습니다. 아래 보정은 모두 기존 diff span 안의 국소 수정이며 새 기능, 새 규칙, 전면 suite를 요구하지 않습니다. 후속 R1이 승인되지 않았으므로 Driver가 범위 안에서 보정을 반영한 뒤, 예정대로 후보를 고정하고 7-consumer를 1회 실행하면 됩니다.

## 유지할 점 (Preserve)

**보호 대상**
- heading과 frozen label, Korean 줄, code/inline code, adapter frontmatter, Decision Guide, 두 generation 계약, CLAUDE, Checkout-1·Entry-1 retained 절, Historical Observations 표가 diff에서 변경되지 않았습니다.

**구조 편집 2건: 정당함**
- `docs/README.md` Delegation 절 분리는 상속 동작, 실제 사용 승인, source-only 기록, grant 경계를 각각 한 번씩 진술합니다. 원문 조건 중 Core 비조회·비강제, named ordinary accept 한정, no-grant 시 human, source-dev acceptance human이 모두 남았습니다. 삭제된 "These documents do not declare…"는 "Authorization comes from that actual decision."으로 대체되어 수용 가능합니다.
- `docs/REFERENCE.md` Human Review의 cache 문단은 내용 그대로 사용 안내 뒤, Topology 절 직전으로 이동했습니다. 행동 전에 필요한 경고가 늦어지지 않고 anchor도 그대로입니다.

**잘 된 국소 편집**
- AGENTS 첫 문단은 금지를 직접 규칙("Do not infer either…")으로 남겼습니다.
- GENERAL-WORK "Neither images"는 정의에 맞게 풀어 썼습니다.
- SECURITY grant 문단, WORKSPACE root-layer 문단, REFERENCE `documentation_root`·`runtime.supported`·extension 경계, MANUAL-OPERATION 첫 문단, OPERATIONS 디지털 검증 문단도 의미가 보존되었습니다.

**공통 delegation 문단 8곳**
- 같은 의미로 일관되게 바뀌었습니다.

## 발견사항

### Blocking

**B1. `docs/CONCEPTS.md` Approval, Pause And Resume** — 권한 변경
- 수정된 span: "You still decide acceptance of each newly prepared exact intent or result"
- 근거: 원문은 "needs its applicable acceptance"였습니다. 같은 문서의 delegation-1 절과 work cycle 문단은 ordinary-worker accept 예외를 인정합니다. 수정문은 모든 result acceptance를 사람에게 고정하므로 예외와 모순됩니다.
- 최소 보정: "Each newly prepared exact intent or result still needs its applicable acceptance; approval to implement covers the work, while result acceptance covers the submitted outcome."

**B2. `docs/MAINTAINING.md` Inventory Window Compatibility 마지막 문장** — 근거 없는 주장 추가
- 수정된 span: "Previous human-1 evidence covers that profile, while worker-1 needs its own qualification."
- 근거: 원문은 human-1 evidence가 worker-1을 qualify하지 않는다고만 했습니다. human-1 자체가 qualified되었다고는 주장하지 않았습니다.
- 최소 보정: "Previous human-1 evidence does not qualify worker-1; worker-1 needs its own qualification."

**B3. `docs/MAINTAINING.md` Source Layout 아래 generation 문단** — 의미 이동
- 수정된 span: "Those verification obligations remain in force even though the legacy tests were removed."
- 근거: 원문의 요지는 해당 의무에 bounded N4 evidence가 있고, legacy test 제거만으로 해소된 적은 없다는 것이었습니다. 수정문은 의무가 아직 열려 있다고 읽힐 수 있어, 앞 문장 "N4 evidence covers"와 충돌합니다.
- 최소 보정: "Bounded N4 evidence covers parallel-process, interruption and unavailable-evidence checks; removing the legacy tests did not by itself discharge those obligations."

**B4. `docs/GETTING-STARTED.md` Review Without Editing JSON 끝 문장** — 의무 추가와 용어 변경
- 수정된 span: "The version check permits the runtime to execute; testing of its OS and distributor build is a separate requirement."
- 근거: 원문은 "not necessarily a qualified OS/distributor build"였습니다. 수정문은 정의된 용어 qualification을 testing으로 바꿨습니다. 기록된 pyenv 3.14.6 사례처럼 test되었지만 unqualified인 조합이 있습니다. 또 원문에 없던 "requirement"를 추가했습니다. 다른 문서들은 미qualified build의 실행을 허용합니다.
- 최소 보정: "Passing the version check does not mean the OS or distributor build has been qualified."

**B5. `docs/GENERAL-WORK.md` Git Integration 마지막 문단** — 과대 주장과 금지 약화
- 수정된 span: "A Git copy or archive preserves bytes. Supported recovery and continued operation at another path still depend on the applicable contract;"
- 근거: Git copy가 uncommitted 또는 ignored bytes를 보존한다고 단정할 수 없습니다. 또 "depend on the applicable contract"는 다른 경로에서의 복구가 가능할 수도 있다고 읽힙니다. 실제로 pending recovery는 원래 target fingerprint에 묶여 있습니다.
- 최소 보정: "A Git copy or archive alone does not establish supported recovery or continued operation at another path; pending recovery still requires the original ticket, binding, target and retained sources."

**B6. `docs/OPERATIONS.md` Observe Before Acting** — 권한 금지 약화
- 수정된 span: "later unsubmitted edits and authorization to write must be considered separately."
- 근거: 원문 "do not … grant write authority"는 read-only 명령이 쓰기 권한을 주지 않는다는 명시 금지였습니다. "considered separately"는 그 금지를 흐립니다.
- 최소 보정: "Their results cover the verified records and product, not later unsubmitted edits, and they grant no write authority."

### Major

**M1. `docs/GENERAL-WORK.md` ignore fingerprint 문단** — 조건 강도 약화
- 수정된 span: "can change the effective ignore policy and fail validation."
- 근거: 원문은 "is explicitly non-pass"였습니다. 정책이 바뀌면 non-pass라는 확정 진술이었는데 수정문은 실패를 가능성(modal)으로 낮췄습니다.
- 보정: "can change the effective ignore policy; that result is explicitly not a pass."

**M2. `README.md` runtime 문단** — 용어 변경
- 수정된 span: "The version check alone says nothing about testing on a particular OS or distributor build."
- 근거: B4와 같은 qualification→testing 치환입니다.
- 보정: "Passing the version check does not mean the OS or distributor build has been qualified."

**M3. `docs/GETTING-STARTED.md` Prepare Project Agent Entry** — 새 의무 추가
- 수정된 span: "Whether a particular session followed that instruction must be checked in that session."
- 근거: 원문은 "not evidence"라는 진술이었습니다. 수정문은 매 세션 점검 의무를 만듭니다. 이는 계약의 "Do not add an obligation… merely to give a sentence a more actionable ending"에 해당합니다.
- 보정: "A pointer-only file tells the agent to “read and follow AGENTS.md”; it does not show whether a particular session followed it."

**M4. `adapters/colvia-work/SKILL.md` Human Review Response** — 새 절차 추가
- 수정된 span: "Check whether the agent followed these instructions and whether the human understood the explanation; the instructions alone establish neither."
- 근거: 독립된 명령문이 되어, 모든 세션에서 agent 준수와 사람의 이해를 점검하라는 새 의무로 읽힙니다.
- 보정: "These instructions alone do not show that an agent followed them or that the human understood the explanation. Before reporting that first entry and fresh resume work in practice, retain evidence from a real exercise."

**M5. `adapters/colvia-work/SKILL.md` Follow-Up And Plan Alignment 첫 문단** — gate 변경과 금지 상실
- 수정된 span: "explain what must be resolved before the work can be connected to the plan."
- 근거: 원문 "expose the gap before claiming alignment"는 정렬 주장을 금지하는 agent 규칙이었습니다. 수정문은 금지를 잃었고, 새 연결 gate를 만들었습니다. R0 처분 4번 위반입니다.
- 보정: "If either is missing or ambiguous, report the gap and do not claim plan alignment until it is resolved."

**M6. `AGENTS.md` Typed Pointers 아래 문단** — agent 금지 약화
- 수정된 span: "Keep the historical observations in [Security and Support](…) within their recorded scope."
- 근거: 원문의 "do not qualify the current source or installed release"라는 명시 금지가 모호한 지시로 바뀌었습니다. R0 처분 4번은 같은 금지가 직접 남을 때만 축약을 허용합니다.
- 보정: 문장 끝에 "; do not use them as qualification of the current source or installed release."를 추가합니다.

**M7. `docs/CONCEPTS.md` host 문단** — 주장 확장
- 수정된 span: "The agent follows these instructions through its configured host."
- 근거: 원문은 "guide a cooperating agent"였습니다. 수정문은 agent가 실제로 따른다고 단정하는데, 다른 문서는 이를 미검증으로 둡니다.
- 보정: "These instructions guide a cooperating agent through its configured host."

### Minor (안전, 범위 내 선택 보정)

- **`README.md`** "the optional grant for accepting one exact ordinary-worker result": exact가 grant에서 result로 옮겨가, grant가 특정 result bytes에 묶인 것처럼 읽힙니다. 보정: "the optional exact grant that lets a named delegate accept one ordinary-worker Work result."
- **`docs/CONCEPTS.md`** "document synchronization remains manual": manual은 원문 근거가 없는 추론입니다. 보정: "Colvia adds no automatic document synchronization."
- **`docs/README.md`** Continuation-1 끝 "Check the records for … separately; … those records establish which outcomes were observed or accepted.": 새 절차를 추가했고, 일부 기록은 이 checkout에 없습니다(Security 참조). 보정: "Synthetic execution, source result acceptance and actual user success each need their own evidence; this manual does not certify any of them."
- **`docs/GETTING-STARTED.md`** "before the Core init transaction": `temp/`는 "when first needed" 생성이 허용됩니다. 보정: "outside the Core init transaction".
- **`docs/SECURITY-AND-SUPPORT.md`** 세 가지입니다.
  - 순서를 바꾼 뒤 "that synthetic qualification"의 선행어가 멀어졌습니다. 해당 문장 앞으로 "Verify a candidate against its exact artifact receipt."를 다시 붙이거나 "the candidate's synthetic qualification"으로 바꿉니다.
  - "requires its own qualification decision"은 "requires its own qualification"으로 바꿉니다.
  - "beyond the historical entry qualification"은 historical entry qualification이 일부 근거가 된다는 함의를 남깁니다. "; historical entry qualification does not carry over"로 바꿉니다.
- **`docs/REFERENCE.md`** Session Handoff "show only those activities": 뜻이 불명확합니다. 보정: "A summary and a fresh agent’s reading of it do not show that the human understood."
- **`docs/GUIDED-INTENT-FORMATION.md`** "Machine commands create and accept these records": 보정: "create these records and record acceptance".
- **adapter** "assess … from their own execution evidence": 평가 의무를 추가했고, adopter use는 execution evidence에 한정되지 않습니다. 보정: "Multi-process behavior and actual adopter use need their own evidence; do not use a read-only view as qualification of either."
- **공통 delegation 문단 8곳**: "retained heading" 설명이 빠져, frozen "Implementation Candidate" heading이 남은 이유가 사라졌습니다. 선택 보정이며, 고친다면 8곳 동일 문구로 맞춥니다.

## 보정 후 처리

- B1–B6과 M1–M7은 해당 문장만 바꾸면 됩니다. 문단 구조, heading, 링크, 잠금 구간에는 영향이 없습니다.
- 보정 뒤 매핑 재생, 보호 span, 링크 정적 검사를 다시 수행하고 후보를 고정한 다음 7-consumer를 1회 실행합니다.
- adapter와 AGENTS 보정은 entry/resume 정적 대조표의 의미를 바꾸지 않습니다. 오히려 원래 경계로 되돌립니다.

## 판정 한계

- 정적 독해에 근거한 판정입니다. token budget, 실제 native 로딩과 agent 행동, 사용자 이해, 실제 old→new 설치 쌍은 여전히 미검증입니다.
- 이 판정은 Owner 수락이 아니며, 이전 7/7을 새 후보에 적용하지 않습니다.
````

### Driver 처분

| 항목 | 처분 | 반영 |
| --- | --- | --- |
| B1 | accept | applicable acceptance로 보정해 ordinary delegated accept 예외 유지 |
| B2 | accept | human-1 자체 qualification을 암시하는 새 주장 제거 |
| B3 | accept | N4의 근거와 legacy test 제거만으로 의무를 해소할 수 없다는 원래 뜻 복원 |
| B4 | accept | testing 대신 qualification 사용, 새 실행 전제 삭제 |
| B5 | accept | Git copy의 보존 완전성 주장 삭제, 원래 target·ticket·binding·source 복구 조건 복원 |
| B6 | accept | read-only 결과가 쓰기 권한을 부여하지 않는 직접 금지 복원 |
| M1 | accept | ignore 정책 변경 결과의 확정 non-pass 유지 |
| M2 | accept | README에서도 qualification과 test를 구분 |
| M3 | accept | 모든 세션의 점검을 요구하는 새 의무 삭제 |
| M4 | accept | 실제 경험 주장 전 근거 조건으로 한정, 별도 상시 점검 지시 삭제 |
| M5 | accept | 정렬을 주장할 수 없는 조건을 직접 규칙으로 복원 |
| M6 | accept | 역사 관측을 현행 qualification으로 쓰지 못하는 agent 규칙 명시 |
| M7 | accept | agent 준수 사실 주장 대신 지침의 역할 설명 |
| Minor README/Concepts | accept | exact는 grant 수식, 자동 문서 동기화를 제공하지 않는 범위로 복원 |
| Minor docs index | revise | 매뉴얼은 요건 설명, 결과는 별도 근거가 필요하다는 뜻으로 고침; 새 record 확인 절차는 제거 |
| Minor Getting Started | accept | Core init 이전 의무 대신 transaction 바깥의 project 준비로 복원 |
| Minor Security 3개 | accept | synthetic qualification 선행어 명시, qualification decision과 부분 승계 함의 제거 |
| Minor Reference/Guided Intent/adapter | accept | 사용자 이해의 증거 한계와 사람의 수락 판단 명확화, 새 평가 의무·execution 한정 제거 |
| Minor 공통 retained-heading 안내 | defend | 선택 보정은 적용하지 않는다. heading과 frozen label·역사 의미를 그대로 두고 현행 상속 관계를 설명한다. 원문의 편집 경위 해설을 반복하지 않는 것이 사용자 요청에 맞으며 authority 조건은 변하지 않는다. |

23개 국소 보정을 반영했다. 최초 보정 script는 inline code 표기가 빠진 원문 검색으로 쓰기 전 멈췄고, 정확한 표기를 맞춘 뒤 적용했다. 그 시도는 source를 바꾸지 않았다. 전체 edit-map은 보강 직전 candidate부터 117개 순차 단계로 현재 bytes를 재구성한다. 후속 Reviewer 호출은 하지 않으며 R1은 REVISE로 보존한다. 위 보정은 Driver 처분·검사이지 재검토 PASS가 아니다. 진입/재개 정적 의미 대조표의 원래 경계는 유지한다.

Reviewer 누적은 648.832696초(약 10.81분/45분)다. 다음은 보존 정적 검사와 최종 candidate 고정, 이미 승인된 7개 소비자 검사 1회다. 이 검사의 통과는 실제 사용자 이해·native agent 준수 또는 source 결과 수락을 의미하지 않는다.

보정 후 숫자·식별자 대조에서 B2 문장의 worker profile 표기가 한 번 중복 추가된 점을 잡았다. 같은 뜻의 후반절을 줄여 원래 문장으로 복원했으며 조건과 식별자 수를 보존했다.

Reviewer 원문에는 생략형 링크가 있어 문서의 실제 탐색 링크로 렌더링되지 않도록 원문 block에 보존했다. 응답 bytes는 그대로이며 제품 문서 링크는 바꾸지 않았다.


## 문장 보강 최종 후보와 소비자 검사 — 2026-10-27

후보 `product-release-84d267aba0725695e04c827d`, inventory SHA-256 `84d267aba0725695e04c827d2feb63f43e55744ea530fa7287ee5e24b63ac476`, tracked diff SHA-256 `f46e71b4830cefe9d173620b561e1d35076a37f12662b43874c7d5ddf9db09d0`를 고정했다. managed 30개 중 14개 문서/지침이 바뀌었고 실행 구현·test·launcher·declaration은 같다. 보호 구간·매핑 재생·GFM·284개 링크 검사에서 오류가 없다. R1은 REVISE와 Driver 보정 완료로 기록하며 새 Reviewer PASS를 주장하지 않는다.

이 후보로 승인된 기존 7개 검사를 1회 실행한다. 고정 CPython 3.14.7 normal, 같은 assertion·Git wrapper·Seatbelt·45초 subprocess 한도, controller 한도 758초다. output만 새로운 전용 실행 경로에 두며 권한·네트워크는 확대하지 않는다. 실행 결과는 아래에 추가한다.


### 최종 실행 결과와 수락 대상

고정 후보의 기존 7개 ID를 선택·수집·실행해 7/7 통과했다. test body 73.352초, controller 포함 73.511849초, exit0이며 skip/failure/error/expected failure/unexpected success는 0이다. file/network canary 통과, source/runtime drift 및 timeout 없음이다. 실제 실행 명령·고정 runtime/controls identity·전후 source hashes는 전용 실행 metadata에 남겼다. 네 실행의 test lane 누적은 214.695569초(약 3.58분/15분), reviewer 누적은 648.832696초(약 10.81분/45분)다. 환경 실패 1회와 이전 후보 두 번의 성공은 각각 원래 결과로 보존한다.

결과 수락 대상은 사용자 흐름 설명·개발 navigation 정렬과 추가 매뉴얼 문장 보강, R1 처분·Driver 보정 및 선택한 최종 consumer 결과다. R1의 원판정은 REVISE이며 후속 Reviewer PASS는 없다. 최종 정적 보존 검사는 통과했다. 읽기 token budget, 실제 native agent 동작·사용자 이해도, 기존 실제 release→이 후보의 exact-pair 전환은 미확인이다. development 계획표 밖 dated pointer 두 곳(도구 중립 실행 계획, U2 Host 검증 README)도 결과 수락 범위에 포함해 명시한다.

이 결과를 Owner가 수락하면 문서 작업의 완료 기준을 닫을 수 있다. 결과 수락은 commit·push·merge·release·실제 도입처 적용을 포함하지 않는다. 실제 U2 적용에 필요한 Host/adapter 고정 구성, 대상·권한·검증·복구 준비와 정확한 설치 전환은 별도 후속 판단으로 남는다. 문서가 개선되었다는 이유만으로 이 작업들을 시작하거나 저장된 후속 선택을 만들지 않는다.

### 단계 종료 정리

고유 문서 변경과 원문 비교 입력은 결과 수락·source 통합을 위해 전용 worktree와 private task에 보존했다. 실패 검사 증거, 고정 controls/결과·후보 identity, review packet/manifest와 편집 재생 map은 이 결과의 검토·처분과 source 통합까지 소비가 남아 있다. 마지막 recovery copy는 삭제하지 않았다.

Reviewer 원문 두 개가 이 문서와 byte-identical이며 해당 process가 종료되고 열린 파일이 없음을 확인한 뒤 중복 response/stream/stderr 6개를 정리했다. 완료된 편집·review controller 10개도 실행·보정 소비가 끝나고 결과와 명령·입력 identity가 남아 있음을 확인해 정리했다. 비어 있는 검사 scratch directory 7개만 제거했다. source worktree·문서·진행 기록과 활성 경로는 그대로다. worktree는 고유 미커밋 결과의 수락·통합에 사용 중이므로 유지한다.


## Owner 결과 수락과 Done — 2026-10-27

Owner는 매뉴얼 18개 읽기·14개 편집, R1 지적 보정, 최종 7/7과 정적 검사, 도구 중립 실행 계획·U2 Host 검증 README의 현행 결과 링크를 포함한 결과에 “결과 수락·Done 승인”이라고 답했다. 이 판단으로 완료 기준을 충족하여 CHORE-20261027-002를 Done 처리한다. R1 재검토 PASS는 없고 실제 사용자/native 동작, 읽기 token 한도, 기존 실제 release→최종 후보 전환은 미확인이라는 한계도 명시한 상태의 수락이다.

수락한 managed 후보는 `product-release-84d267aba0725695e04c827d`, inventory SHA-256 `84d267aba0725695e04c827d2feb63f43e55744ea530fa7287ee5e24b63ac476`이다. 최종 소비자 실행 뒤 이 30개 managed bytes는 변하지 않았다. source-only 완료 기록과 development index의 완료 연결만 갱신했으므로 기존 7개 소비자 실행 근거는 유지하고 영향받은 정적 문서 검사만 다시 확인한다.

개발 인덱스의 선택 작업 링크를 이 완료 절로 연결했다. 이 작업 기록이 결과·처분·잔여의 소유자이며 인덱스에 진행을 복제하지 않는다. 원래 계획과 이전 실패·검토 판정·수락 전 서술은 당시 이력으로 남긴다. 이번 Done은 Git·배포·도입처 적용을 승인하지 않으며 후속 작업이나 저장된 continuation 선택을 만들지 않는다.

고유 미커밋 source 문서와 마지막 비교·복구 입력은 아직 Git 통합이 결정되지 않아 유지한다. 소비자는 수락 결과의 source 통합이며, 동일 bytes의 통합·복구 가능성이 확인되고 남은 참조가 없을 때 정리를 재평가한다. 활성 worktree 경로 변경이나 추가 삭제는 없다.

완료 navigation의 bounded change는 `docs/development/README.md` 한 줄이다. 변경 전 SHA-256 `256c133f93df5070bc6b80f6e1daada1ed29851acf8eaf9184522d47344873aa`, 변경 후 `1d608923108bf62aef197d3d221fd6bdb4073c53971e638badce3a25e967cb23`이며 source base `17dc804a6af4e168d1bb73aa765e9354db4952ba` 위 미커밋 결과에 적용했다.


## 수락된 문서의 Git 통합 승인 — 2026-10-27

Owner는 “이번에 수락한 문서 변경을 커밋하고 통합하자”라고 지시했다. 이 승인은 위 수락 결과의 source commit·push·PR·main 통합에 적용한다. 실제 설치·배포·release, 별도 branch 삭제는 포함하지 않는다. source base와 원격 main은 같은 `17dc804a6af4e168d1bb73aa765e9354db4952ba`이며 열린 PR은 없다. 다른 checkout의 고유 변경은 그대로 보존한다.

통합 전 확인에서 Development Index가 Maintaining의 남은 역사 문구 정리에 named DR-0002 amendment를 요구함을 확인했다. 이번 결과 수락에 이미 포함된 Source Layout·Inventory Window Compatibility 두 문단의 정확한 전후 범위와 한계를 [DR-0002의 수락 추적 기록](../decisions/DR-0002-checkout-1-contract-baseline.md#accepted-historical-explanation-wording-amendment--2026-10-27)에 연결했다. 새 Owner 결정을 추정하거나 제품 설명을 추가 수정하지 않았으며 나머지 잔여 문구를 완료로 처리하지 않는다. 이 source-only 기록·navigation 추가는 수락 근거 정리이며 managed 30개 bytes는 최종 검사 후보와 동일하다.

원본 source commit을 보존하는 PR merge 방식으로 통합한다. 문서의 최종 7/7은 그대로 사용하고 변경된 source-only 기록의 GFM·링크·disclosure·whitespace를 확인한다. 통합 결과와 원격 revision은 private task 기록 및 실제 PR에 남긴다.
