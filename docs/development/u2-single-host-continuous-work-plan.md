# U2 Single-Host Continuous Work Plan

상태: 착수 제안, 구현 전. 2026-10-21 Owner는 U1 적용을 마친 뒤 U2의 대상·범위·완료 기준·근거·시간을 구체화하도록 요청했다. 이 문서는 그 계획 작성만 수행한 결과이며 R0, host 실행, 새 intent/Work, 실제 위임이나 구현을 승인하지 않는다. Source 시작점은 `7d012f5297de1d9a77aa0b8187406f4785221573`, U1 release는 `continuation-1/a58003fa932fbd2c1ecadd79b0a3e9d168d170a1c9254514d38187b184ce3557`다.

## Proposed Outcome

기존 프로젝트 하나의 필요한 업무를 한 Work 안에서 수행·검증·허용 보정하고, 중단 후에도 같은 승인과 남은 예산으로 검증된 결과 후보까지 이어간다. 위임 수락을 사용하는 부분은 먼저 실제 host의 권한 차단과 정확한 복구를 증명한 뒤 적용한다. 같은 범위의 반복 수행과 사람에게 돌아와야 하는 새 판단을 구분하는 것이 이번 결과다.

```text
Owner의 범위·검증·예산 승인
  → 한 Work 수행 → 검증 → 허용 보정 → 검증된 후보
       ↑ 중단·재개: 같은 승인, 누적 사용량, 원 입력을 확인
  → 수락: 사람 / 정확한 일반 worker grant의 1회 예외
  → 결과·계획 반영·잔여 보고 → 다음 선택은 U1 경로
```

U1 후속 선택 기록에 실행 예산을 넣지 않는다. Work의 기존 narrative가 승인·실행·누적 예산을 소유하고 CONT는 완료한 Work 이후의 선택만 소유한다. 새로운 scheduler, 범용 실행기, 중앙 큐, 여러 host나 병렬 worker를 만들지 않는다.

## Project And Host

| 대상 | 제안과 선택 이유 | 착수 조건 |
| --- | --- | --- |
| 실제 프로젝트 | Reference A: 이미 U1을 설치한 기존 서비스 프로젝트. 미완료 운영 안내에서 작은 문서 Work 하나를 선택한다. 관측용 업무를 새로 만들지 않는다. | 현재 다른 Driver가 제출한 문서 Work의 수락·dirty 처리·단일 writer 기준점을 먼저 정리. 그 Work를 인계하거나 재개한 것으로 보지 않음 |
| 실제 업무 | 기존 비동기 실행과 DB 대기·취소·종료 한계를 설명하는 운영 가이드 첫 범위. 기존 개발·설정·관측 정본을 재사용한다. | exact intent의 문서 scope·근거·verifier·grant를 Owner가 수락. 전체 운영 가이드나 template acceptance 완료로 확대하지 않음 |
| Host | local macOS 27.0.1 / 26A434 / arm64, Codex CLI 0.163.0의 stdio App Server 한 조합. Colvia는 final/GIL CPython 3.14.7을 고정한다. | 실제 인증·과금, 모델/effort, protocol과 enforcement를 확인. 데스크톱 UI나 다른 CLI 버전의 지원으로 넓히지 않음 |
| 구성 | 신뢰된 Driver/control 경로 하나 + 편집용 isolated worker 하나. host가 admitted 실행과 delegate를 결속하고 좁은 accept 호출을 검증한다. | worker가 control truth·managed runtime·Git 관리 영역·host 정책을 직접 쓰지 못해야 함. worktree만으로 격리했다고 보지 않음 |

실제 프로젝트의 이름·경로·branch/HEAD·해당 backlog와 결과 위치는 Owner의 비공개 대상 부록에서 고정한다. 이 source 계획의 기술 조건은 그 비공개 자료 없이도 이해·검증할 수 있어야 한다. 모델은 승인 시 실제 가용 모델과 effective 설정으로 고정하고 자동 대체하지 않는다. 실사용 위임 여부와 exact grant는 해당 프로젝트의 판단으로 남긴다.

## Scope And Deliverables

1. 현재 host의 지원 API와 실행 경계를 확인하고, 기존 Core의 ordinary-worker accept만 호출하는 최소 host 연결을 만든다. 모델이 Owner actor, 임의 shell, action/home 또는 ticket 파일을 고르도록 하지 않는다. 재사용 가능한 host 연결과 합성 검증은 source-only 범위로 두며 기본 backend·공개 지원으로 선언하지 않는다.
2. 같은 Work의 기존 승인·verifier·시간/시도 사용량·마지막 검증 결과·재개 조건을 기존 narrative에서 이어 읽는다. 현재 adapter의 `Supervised Work Iteration`과 작업 방식 안내를 사용한다. 실제로 발견한 안내 누락만 보정 대상으로 제시하며 별도 상태 장부를 만들지 않는다.
3. V22/V23의 실제 host 거절·복구와 아래 H01–H10을 확인한다. 범위 안의 수행·검증·보정은 매 단계 재승인을 요구하지 않지만, authority apply 실패는 자동 retry 루프에 넣지 않는다.
4. host가 적격일 때 선택한 실제 업무 한 건에서 반복 수행·재개와 V26을 관측한다. 합성 입력의 품질 판정과 실제 업무의 품질·Owner 개입을 구분한다.
5. 기존 source 절차의 R0/R1, 필요한 회귀와 문서 확인을 거쳐 결과와 남은 제한을 보고한다. source task 결과 수락은 사람에게 남는다.

Core schema·권한 규칙·lifecycle window, 기존 grant 소비/revoke 의미, CONT/P 범위는 변경하지 않는다. 이를 바꿔야 진행할 수 있으면 아래 예산 안에서 이유와 최소 변경안을 보고하고 해당 구현을 멈춘다. Windows, 다른 OS/host, 민감정보·실제 고객 자료, 새로운 보호 시스템, U3 전체 복구, Git/공개 배포와 자동 후속 착수는 제외한다.

신규 문서/host 연결의 최종 파일 목록과 exact 실행 명령은 R0 대상에 고정한다. 새 구현 파일 이름을 지금부터 runtime 지원 계약으로 간주하지 않는다. managed adapter를 수정하면 새 inventory·consumer·정확한 설치 검증과 adopter 적용 결정이 필요하다. 기존 설치를 손으로 수정하지 않는다.

## Host Boundary And Early Stop

2026-10-21 읽은 [공식 App Server 문서](https://learn.chatgpt.com/docs/app-server)는 stdio, thread/turn과 client가 처리하는 dynamic tool 경로를 설명한다. 이는 연결 방식의 근거이며 Colvia 권한 강제의 증거가 아니다. 이번 로컬 관측은 CLI version/help까지만이다. [M0](agent-delegation-m0-plan.md#first-host-feasibility-path)의 0.162.1 schema 조사와 현행 0.163.0은 다르므로 옛 schema 결과를 현재 지원으로 대입하지 않는다.

첫 host 단계에서 현행 버전의 schema와 effective 정책을 고정하고 합성 control/worker/canary로 아래 경계를 확인한다. 승인된 범위에 맞는 제한 기능이 없거나 직접 우회가 가능하면 host 부적격 또는 미확인으로 보고한다. 자동 upgrade, 외부 sandbox 도입, 다른 backend, full-access, 추가 경로·credential 허용으로 대체하지 않는다. 첫 단계 예상은 60–90분, 중단 상한은120분이다. 실패한 host로 실사용·위임 수락을 시작하지 않는다.

좁은 accept 경로는 모델의 인자를 권한으로 믿지 않는다. trusted host가 admitted 실행·delegate·home·Work·intent/revision·scope·action과 검사된 evidence/result를 결속하고, 생성한 canonical ticket의 정확한 bytes를 소유한다. handle만 넘겨도 실제 실행 직전 동일 bytes·현재 binding·grant 사용 여부를 재검증해야 한다. 중복·알 수 없는 call은 거절하며, 모델에 Core authority를 쓰는 일반 shell을 제공하지 않는다. 허용된 Core 호출도 기존 writer guard와 fresh-state 검사를 거친다.

`thread/shellCommand`, host filesystem API, unrestricted process/API·MCP·network 같은 다른 진입점은 worker/delegate에 노출하지 않는다. 문서상 존재 여부와 실제 차단을 별도로 확인한다. 자격 검증은 외부 서버나 다른 계정을 공격하는 작업이 아니라 승인된 합성 fixture와 canary에 대한 제한된 검사다.

## Verification And Completion Criteria

| ID | 확인할 결과 | 성공 기준과 근거 종류 |
| --- | --- | --- |
| H01 | 실행과 delegate 결속 | 다른 thread/turn/call, Owner 사칭, grant 없는 actor, 잘못된 home/action/scope의 실제 host 요청을 거절하고 control 무변경 확인. V22 |
| H02 | 정확한 payload | 준비 후 파일 교체·digest/인자 변경·다른 결과 결속·중복/불명확 call을 거절. 모델 문장이나 token만으로 허용하지 않음. V22 |
| H03 | 우회 경로 차단 | 실제 worker 실행 환경에서 control truth·managed runtime·Git 관리 영역·정책 파일의 직접 쓰기와 경로 alias/symlink, 불필요 tool/permission 확대가 차단됨. canary와 bytes/mode로 확인. V22 |
| H04 | 정상 위임과 1회 사용 | exact ordinary isolated-worker grant로 허용된 accept 한 번만 성공. 재사용·revoke 이후·부모/다른 Work/다른 action은 거절. Core와 host 결과를 함께 확인 |
| H05 | 중단과 복구 | S0–S5의 기존 결정/게시 경계를 합성 대상에서 확인. 실제 프로세스 중단, 종료 확인, pending 보존, Owner가 승인한 원 delegated ticket의 동일 actor/decision 재생. mixed/all-post의 cancellation 우회와 새 accept 생성 금지. V23 |
| H06 | 같은 Work 반복 | 고정 verifier가 실패 원인을 설명하고 허용 scope 내 보정 후 통과. oracle·권한·입력·기대 결과를 바꾸지 않음. 의도된 거절은 expected 결과로, 예상 밖 실패는 실제 실패로 기록 |
| H07 | 재개·예산 | 중단 뒤 저장한 Work/입력·마지막 단계·누적 사용량/남은 한도를 읽어 같은 권한으로 이어감. budget 초기화, 무조건 재실행, 중복 제출 없음. 깨진 checkpoint는 unavailable |
| H08 | 중단 경계 | 새 범위·exact ticket 승인·revocation·상한·Owner 중단·해결 근거 없는 반복 실패에서 해당 작업 중지. 실제 실패나 중단을 PASS로 바꾸지 않음 |
| H09 | 작업 방식 선택 | 단일 결과는 ordinary Work, 같은 범위 개선은 같은 Work, 독립 child 수락+통합 결과가 필요한 사례만 umbrella로 분류. 선택 이유·착수 조건·미결을 제시하는 짧은 합성 사례3개. umbrella의 실사용 효율 증명은 아님 |
| H10 | 실제 업무 품질·부담 | 선택한 문서 Work의 정확성·누락·불필요 수정·검증 근거를 결과 내용으로 판정. 재설명, 불필요 반복 승인, 정당한 새 승인, 추가 조작/대기와 Owner 개입 대략 시간을 별도로 관측. V26 |

H01–H09의 합성·host 결과와 H10의 실제 결과가 모두 있어야 이 제안의 U2 범위를 완료로 보고한다. 자연 업무에 수정이나 중단이 없었다면 그 사례를 억지로 만들지 않고 H06/H07의 합성 관측만 있다고 밝힌다. 실사용 한 건·단일 host로 일반 생산성 향상이나 다른 프로젝트 품질을 주장하지 않는다. Owner 시간을 직접 받지 못했으면 미측정으로 남기고 V26의 해당 부분은 미완료다.

원 authority apply는 한 번만 호출한다. 실패/timeout/불명확 결과가 나면 근거를 보존하고 별도 권한을 확인한다. V23의 fault injection과 복구는 처음부터 승인된 합성 시나리오의 exact original ticket으로 한정하며 실제 프로젝트 자동 복구 권한으로 이전하지 않는다. 실제 결과 acceptance를 받기 전에 grant의 유효성, 1회 사용 조건과 host 검증을 재확인한다.

## Evidence Reuse And Additional Checks

| 재사용할 입력 | 재사용 가능한 범위 | 추가 확인 |
| --- | --- | --- |
| [U1 수락 결과](CHORE-20261021-001-continuation-contract-review.md#owner-result-acceptance-and-closeout)와 exact release | P-1–P-6/DC1–DC9의 수락된 의미, 유지한 문서·Core 계약 | 실제 installed view/continuation, 이번 same-Work 입력·budget과 source/runtime drift |
| [위임 M0](agent-delegation-m0-plan.md), [M1/M2](FEAT-20261016-001-delegated-ordinary-acceptance.md#owner-result-acceptance-and-a-planning-proposal--2026-10-18), [DR-0005](../decisions/DR-0005-delegated-ordinary-work-acceptance.md) | ordinary grant·1회 소비·revoke·reader·복구 계약과 식별된 합성 근거 | 현재 release/controls 대응, 실제 host V22/V23, 실제 품질/Owner 관측 V26 |
| [U1 label/entry 선행 보정](PATCH-20261018-002-delegation-label-and-link-oracle.md)과 현재 adapter | 원 변경의 해당 consumer·링크·label 근거 | 이번 host·재개에서 바뀐 안내와 installed 소비 경로만 새로 확인 |
| 실제 프로젝트의 수락된 source/test/config·가이드 | 이번 문서의 기술 사실과 기존 실행의 제한 | 변경 링크/GFM/명령·경로, 새로 주장하는 동작에 필요한 가장 좁은 테스트 |

U1의 normal110 기존 통과+보정5, parent-O116/116, exact P/Q6/6을 새 전체 실행으로 부르지 않는다. 앞선 전체 parent-O693의 실패2와 normal693의 오류1, 최초 중단은 유지한다. alias 결함 보정과 별개로 target-classification·errno35의 원인/관련성은 미확인이고, 나중의 비재현은 원인 해결이 아니다. R1은 조건부였고 이후 Driver 보정은 독립 재검토되지 않았다. 두 fresh Codex reader는 합성 agent 관측이며 실제 신규 사용자나 provider 독립 관측이 아니다. 실제 설치 성공도 전체 회귀·일반 공개 qualification을 대체하지 않는다.

이번 계획은 새로운 host 수락 경로와 중단/복구를 연결하므로 집중 검사만으로 그 상호작용을 모두 설명하지 못한다. [Maintaining](../MAINTAINING.md#evidence-reuse-and-selection)에 따라 H01–H09를 반복 중 집중 검사한 뒤 최종 입력을 모아 normal·parent-O 전체 회귀를 각각 한 번 수행한다. 옛 실패를 재사용해 전체 PASS라고 주장할 수 없다는 점도 선정 이유다. 현행 발견 ID·원본 runner/격리 정책·상세 invocation을 승인된 준비 단계에서 고정한다. 예상 소요와 실제 collection이 맞지 않으면 실행 전에 남은 한도를 다시 계산한다. candidate 이름/문서 hash만 바뀌었다는 이유로 전체를 반복하지 않는다.

핵심 기존 test 영역은 `test_general_work*`, `test_worktree*`, `test_continuation*`, `test_productization_safety.py`, 위임 test/factory와 해당 reader/installed 경로다. 구현 과정에서는 H 항목 및 변경 consumer에 해당하는 exact ID만 선택한다. 최종 full scope는 그때의 전체 discovery 결과로 식별하고 skip·중복·미실행·cleanup 실패를 누락하지 않는다. -O는 parent interpreter 조건이며 child까지 최적화됐다고 주장하지 않는다.

새 release/managed 문서 변경이 없다면 기존 exact a580 설치 근거와 host 연결 결과를 재사용한다. managed bytes가 바뀌면 inventory/설치/update/repair/detach 소비와 exact artifact 경계를 확인하고 adopter 적용안은 마지막에 별도로 제시한다. 기존 U1의 완결·한계를 재판정하거나 일반 출시를 이 작업에 합치지 않는다. actual adopter의 문서 Work만으로 Core 전체 테스트를 다시 돌리지 않는다.

## Estimate, Limits And Attempts

단위는 분이며 아래 합계는 승인된 실행 시작부터의 누적 활동 경과시간이다. 판단·구현·수정·리뷰 CLI·테스트·결과 정리를 포함한다. 전용 Owner 응답 대기는 시작/종료를 남겨 제외하고, 그동안 다른 일을 수행한 시간은 포함한다. 동시에 돌아가는 일은 wall time으로 한 번 계산한다. context 전환·새 session·재개 시 기존 사용량과 시도 횟수를 이어받는다. 이번 계획 작성과 완료한 선행 설치 시간은 아래 U2 예산에 포함하지 않는다.

| 단계 | 예상 시간 | 근거/조건 |
| --- | ---: | --- |
| R0와 실행 입력 고정 | 30–45 | 기존 source 계약·M0 조사 재사용, 새 review 한 번. 판단값 |
| host 제한 확인과 H01–H05의 최소 연결 | 60–90 | 새 권한 강제는 미측정. 최대120분 안에 적격 여부와 잔여를 판단 |
| same-Work 수행·재개와 H06–H09 | 60–90 | 기존 adapter/Work 계약 재사용, 새 범용 loop engine 없음. 판단값 |
| 최종 normal·parent-O와 통합 확인 | 115–145 | U1 전체693 두 실행이 3583.493초·3468.361초, 합계117.531분이었다. 실패한 실행의 시간 참고이며 현재 PASS/성능 보장 아님 |
| 실제 문서 Work와 V26 | 60–90 | 좁은 문서 결과·기존 근거 재사용·허용 보정 포함. Owner 대기 제외 |
| R1·처분·결과 정리 | 30–45 | reviewer 한 번과 scope 내 보정. 판단값 |

합계 예상은355–505분, 약6–8.5시간이다. 누적 중단 상한은600분(10시간)으로 제안한다. 상한을 예상 완료시간으로 제시하지 않는다. host 단계는120분, 전체 테스트 실행 누적은180분을 내부 상한으로 두며 전체600분이 먼저 적용된다. 첫 host가 부적격이면 그 단계에서 멈추므로 전체 예산을 소진하지 않는다. 큰 Core 결함·계약 변경·새 runtime/격리가 필요하면 이 예상의 전제가 깨진다.

수정은 같은 scope와 고정 oracle 안에서 최대2회 묶어 수행하며, 그때마다 해당 집중 검사만 재실행한다. 같은 원인으로 새 근거 없이 실패하면 횟수가 남아도 멈춘다. 전체 normal/O 각1회 이후 추가 전체 실행은 이번 제안에 포함하지 않는다. R0/R1 각1회, 필요한 지적 처분은 포함하되 추가 reviewer 호출은 실행 전 근거·비용·기존 권한을 확인한다. 이 횟수 제안은 required review를 생략하는 면제가 아니다. 미해결 필수 지적은 미완료로 남긴다.

host 검사 한 건은 기본5분, 모델 수행 turn은15분, 단계별 중단/프로세스 종료 확인은1분 이내를 제안한다. 실제 실행 wrapper의 timeout/TERM/KILL·자식 종료 확인을 고정하고 native test의 더 긴 기존 상한은 유지하되 단계/전체 잔여가 우선한다. 모델 서비스 지연·실패도 활동/실행 시간에 포함하며 자동 backend 전환하지 않는다. 체크포인트는 host 적격 판단, 보정 묶음 완료, 최종 회귀, 실제 결과 제출 때 같은 task record에 남긴다.

## Start, Review And Ownership

다음 결정 대상은 이 bounded 계획과 실제 대상 부록이다. R0는 구현 전 수행하며, reviewer CLI 호출과 전달 자료 범위의 승인이 있을 때만 실행한다. 이번 요청만으로 reviewer나 subagent를 호출하지 않았다. 공통 review 절차에 따라 실제 model/session·인증/과금·입력 identity·원문·Driver 처분을 보존한다.

계획 승인 뒤 source Workflow에 따라 미사용 ID를 확인하고 source record 하나를 만든다. 이후 진행은 그 record가 소유하고 이 계획은 입력으로 남긴다. 실제 프로젝트의 업무 진행은 해당 Work narrative 하나가 소유하며 source에는 필요한 익명 검증 결과만 연결한다. source 개발 결과, 실제 업무 결과, 계약 활성화와 Git/설치/배포는 각각 해당 Owner 결정이다.

실사용은 host 적격 확인과 실제 프로젝트의 준비 조건이 모두 충족돼야 한다. 이미 승인된 동일 scope의 routine 작업은 다시 승인받지 않는다. 새 exact intent/grant/ticket, 범위 변경, 권한 확대나 한도 연장은 해당 규칙대로 판단받는다. 현재 Work가 준비되지 않았으면 source 검증까지 수행하고 실제 업무/V26을 미완료로 남기며 다른 프로젝트나 가짜 업무로 바꾸지 않는다.

## Preservation And Cleanup

재사용 가능한 source/doc/test는 repository에, 실행 스크립트·고정 ticket·원 로그와 복구 입력은 task 소유의 durable artifact 경로에 둔다. 실행 전에 경로 소유권과 가용성을 확인하고 system temporary 경로로 우회하지 않는다. 실제 프로젝트·비공개 비교 식별자는 공개 의도 source에 넣지 않는다.

예상 밖 실패는 원 입력·결과·필요 target 상태를 먼저 보존한다. exact delegated recovery에는 원 ticket·동일 actor/decision이 필요하며 schema5 뒤 과거 window rollback을 복구로 제시하지 않는다. 실제 apply/recovery는 exact 승인과 기존 제품 규칙을 따른다. 작업이 끝난 파일은 소비·보존·Owner 조건을 확인해 정리하며 유일한 결과·복구 사본, 실행 중 또는 근접 후속에 쓸 worktree는 유지 이유와 종료 조건을 기존 기록에 남긴다.

## Plan Preparation Checkpoint — 2026-10-21

source runtime, managed inventory, tests와 기존 task/decision bytes는 변경하지 않았다. 이 source-only 제안과 비공개 대상 부록만 작성했고 새 Work/intent·review·host 모델 실행·제품 테스트를 시작하지 않았다. 선행 설치는 그 별도 승인·결과 기록에서 완료했으며 U2 실행으로 계산하지 않는다. 문서의 링크·GFM·공개 식별정보와 diff를 확인한 뒤 Owner에게 제시한다.


## Documentation Alignment And Tutorial Follow-Up

### Owner Planning Direction — 2026-10-21

Owner는 U2 착수 전에 구현과 문서가 같은 행동을 안내하도록 현재 영향 범위와 남은 실습 개정을 구분하고, 기존 후속 항목에 연결하도록 요청했다. 이번 계획 보강은 그 요청을 반영한다. 이미 수락된 U1에 전체 매뉴얼 개정 조건을 추가하지 않으며, 이 요청으로 U2 구현·실습 실행·계약 변경·배포·adopter 업데이트를 시작하지 않는다.

이 절은 앞의 U2 문서 산출물·완료 보고 범위를 구체화한다. 다음 구현 작업도 해당 행동에 영향을 받는 문서와 예시를 함께 정렬한다. 원 기술 계약과 기존 source Workflow의 권한·검증 규칙을 유지하고, 별도의 문서 상태 장부나 전역 절차 변경을 만들지 않는다. 개발 인덱스의 기존 Product Documentation And Comprehension 및 Onboarding And First Work 행에는 이 계획의 탐색 링크만 추가한다. 기존 후보의 목적·기준·상태는 그대로다.

### Verified Starting Point

| 구분 | 확인한 결과 | 아직 완료하지 않은 범위 |
| --- | --- | --- |
| U1 source | [U1 문서 통합·검사 기록](CHORE-20261021-001-continuation-contract-review.md#process-r1-result-and-document-integration)과 source 변경 목록에서 계약·운영·명령 참조·진입 지침·adapter의 continuation-1 반영을 확인. EN/KO의 README와 rules-and-removal도 갱신됨 | 모든 입문 실습을 최신 절차로 개정한 결과는 아님 |
| 입문 실습 | [EN 목차](../../manual/en/README.md#the-shortest-path)와 [KO 목차](../../manual/ko/README.md#가장-짧은-경로)는 이전 실습 명령 대신 현재 운영 문서를 따르도록 안내 | getting-started·first-work·resume의 EN/KO 6개 문서에는 entry-1 후보 안내와 과거 실습이 남음. 직접 연결된 concepts의 EN/KO 2개도 이전 candidate 안내가 남아 함께 대조할 대상 |
| 배포본 포함 | U1 exact a580 inventory에는 managed payload 30개가 포함됨. 해당 계약·운영 docs와 adapter는 포함되지만 `manual/en/`·`manual/ko/`는 source-only | source 매뉴얼 수정만으로 설치 payload에 포함됐다고 보고하지 않음. 매뉴얼 배송 방식 변경은 이번 계획에 없음 |
| adopter 설치 | U1의 원 실제 적용과 별도 추가 적용은 각 exact target의 결과 기록을 따름. 이번 비공개 대상 재확인에서 installed a580의 30개 bytes가 inventory와 source에 일치 | 다른 설치본·모든 adopter의 currentness 또는 입문 실습 설치 완료를 뜻하지 않음. 대상별 반영 여부는 private 종료 보고가 소유 |
| 계획·인덱스·작업 기록 | [개발 인덱스](README.md)의 U1 표시는 제한을 포함한 완료이며 [U1 수락 기록](CHORE-20261021-001-continuation-contract-review.md#owner-result-acceptance-and-closeout)과 일치. U2는 착수 제안, 문서·onboarding 후보는 미착수 | 과거 U1 계획/진행 절의 Draft·검사 대기 표시는 당시 기록으로 보존. 그 문장을 현재 완료 설명 대신 사용하거나 미완료 실습을 완료로 표시하지 않음 |

이 확인은 관련 source·inventory·설치 bytes·계획 문구의 대조다. EN digest marker는 6쌍 모두 일치했지만 번역의 의미 대응이나 최신 실습 실행을 증명하지 않는다. U1의 원 검사·실패·조건부 review 한계는 앞 절과 원 수락 기록 그대로다.

### Documentation Within Each Implementation

작업 시작 때 변경할 사용자 행동과 연결된 문서를 정하고, 코드·예시·문서를 같은 후보에서 대조한다. 변경 필요가 없는 항목은 기존 기록에 이유만 남긴다. 모든 문서를 기계적으로 수정하거나 모든 구현에 전체 매뉴얼 개정을 요구하지 않는다.

| 변경할 행동 | 함께 확인·정렬할 문서 | U2에서 확인할 내용 |
| --- | --- | --- |
| 계약·권한·상태·지원 조건 | 관련 technical contract, `docs/REFERENCE.md`, capability/지원 안내 | 정확한 grant와 실제 host 검증 경계. 기존 Core 계약을 바꾸려면 해당 결정 절차를 먼저 따름 |
| 실행 명령·중단·복구 | `docs/GETTING-STARTED.md`, `docs/OPERATIONS.md`, `docs/GENERAL-WORK.md`, 관련 manual 예시 | 같은 Work 반복·재개, 누적 예산, authority apply 실패 시 중지, 원 ticket 복구 조건 |
| agent가 제안하거나 수행하는 행동 | `AGENTS.md`·`CLAUDE.md`의 해당 안내, `adapters/colvia-work/SKILL.md`, 자연어 요청 예시 | 일반 Work·같은 Work 반복·umbrella·위임의 선택과 권한을 설명하고 실제 지원 범위를 넘지 않음 |
| 사용자 실습·다음 행동 | 관련 EN/KO 문서 쌍과 그 목차·연결된 개념 설명 | 상황→요청→수행→예상 결과→사람의 판단→실패·다음 단계가 두 언어에서 같은 조건·제한을 가짐 |
| 완료와 잔여 | 해당 계획·개발 인덱스의 navigation·단일 작업 기록 | 실제 완료와 미관측을 대조하고 남은 문서의 담당 항목과 재개 조건 연결. 과거 수락 본문은 보존 |

U2의 문서 완료 기준은 선택한 host·같은 Work 수행/재개 경로에서 기능과 안내·예시가 모순되지 않고, 변경한 EN/KO 행동·조건·제한·링크가 대응하는 것이다. U2가 직접 바꾼 행동을 설명하는 예시는 같은 작업에서 정렬·확인한다. 최초 프로젝트 준비부터의 전체 입문 과정은 아래 후속 범위다. 이 문서 정렬은 기존 U2의 문서·consumer 검사에 포함하며 전체 6–8.5시간 예상/10시간 상한을 자동으로 늘리지 않는다. 실제 변경 범위가 그 예상을 깨면 진행 전에 잔여와 추가 비용을 재산정한다.

### Remaining First-Path Tutorial

남은 개정은 [Product Documentation And Comprehension](README.md#product-documentation-and-comprehension)이 문서의 currentness·EN/KO 대응을, [Onboarding And First Work](README.md#onboarding-and-first-work)가 실제 첫 경로와 이해도 근거를 맡는 기존 후속 범위에 연결한다. 새 backlog나 Work를 만들지 않는다. 실행을 선택하면 하나의 승인된 task record가 해당 실습 개정의 진행을 소유하고 두 후보는 그 결과를 참조한다.

- 주 대상은 `manual/en/`·`manual/ko/` 각각의 `getting-started.md`, `first-work.md`, `resume.md`다. README의 경로·경고와 concepts의 기존 candidate 안내·권한 설명은 직접 연결된 범위만 같이 정렬한다. rules-and-removal은 영향을 받는 부분이 있을 때만 바꾼다.
- 현재 지원하는 source 준비·정확한 artifact 확인·설치·프로젝트 목표/계획·작업 요청서 수락·첫 Work 수행/결과 수락·새 세션 재개의 한 경로를 최신 절차로 이어 쓸 수 있어야 한다. 지원하지 않는 공개 installer, OS/host, 자동 실행·수락을 예제로 추가하지 않는다. 기본 local/human 경로와 선택적 isolated-worker 위임을 섞지 않는다.
- 실행은 지원 조합·정확한 candidate와 검증 범위·예산을 정한 별도 계획으로 선택한다. U2가 직접 바꾼 실습은 그 변경에 포함하고, 나머지는 입문 실습 정렬을 선택할 때 진행한다. 전체 매뉴얼 개정을 U1 완료나 U2 host 검증의 선행 조건으로 두지 않는다.
- 완료하려면 변경된 경로를 첫 준비부터 새 세션 조회까지 실제로 실행한 새 근거가 필요하다. 최신 명령/예상 결과와 과거 실행 identity를 분리하고, 원 checkout-1 실행의 날짜·범위·한계·근거는 식별 가능한 역사 기록으로 보존한다. `entry-1` 문자열만 바꾸거나 옛 PASS를 새 실습의 PASS로 사용하지 않는다.
- 종료 시 EN/KO의 같은 행동·조건·거절/복구·검증 한계와 모든 필수 단계의 상태를 확인한다. 새 독립 agent 읽기, 실제 사용자 이해도는 실제 수행한 경우만 별도 결과로 표시한다. 실행 성공과 정적 문서 검사만 있으면 그 범위로 보고한다.

### Focused Documentation Verification

변경된 명령과 예상 출력은 현재 CLI/계약에 대조하고 영향을 받는 지원 경로만 실행한다. 링크·anchor와 GFM 렌더링을 검사하고 code/pre 밖 literal `**`가 남지 않는지 확인한다. EN/KO는 문장 수나 digest만 맞추지 않고 권한·선행 조건·지원/미지원·실패/복구·후속 행동을 짝지어 읽는다.

변경하지 않은 문서·runtime·실습은 입력 identity와 영향 범위가 유효한 기존 근거를 재사용한다. 문서 변경만으로 전체 제품 테스트를 반복하지 않는다. 현재 U2가 제안한 전체 회귀는 host 수락/복구 연결의 위험에 대한 검사이며 이번 문서 계획 보강 때문에 추가된 것이 아니다. 실행/권한 의미가 바뀌면 Maintaining에 따라 필요한 검증을 다시 고른다.

이번 계획·인덱스 편집의 검증은 링크/GFM·기존 수락 기록 보존·navigation 한정 diff·payload 무변경이다. 실습 명령과 runtime은 수정하지 않았으므로 새 실습·제품 테스트를 실행하지 않는다. 이는 문서 계획 검사이며, 개정 실습의 실행 또는 실제 사용자의 이해도 확인 결과가 아니다.

### Closeout Fields

각 구현 작업의 기존 종료 보고에 다음 세 항목을 간단히 포함한다. 별도 보고서나 장부를 만들지 않는다.

- 이번에 정렬한 문서: 파일/언어와 변경 행동, 실제 수행한 문서·명령·실습 검사. 소스 수정과 해당 artifact 포함 여부를 구분한다.
- 남은 문서와 연결된 후속 항목: 미정렬 파일/실습, 이유, 기존 담당 후보/Work와 재개 조건. 관련 잔여가 없으면 없음으로 적는다.
- adopter 반영 여부: 대상별 적용 완료·미적용·확인 불가·설치 대상 아님(source-only), 확인한 release와 근거 또는 다음 조건. source commit/배포본 생성만으로 설치 완료라고 하지 않는다.

이번 보강에서 정렬한 것은 이 U2 계획과 개발 인덱스의 두 navigation 항목이다. 입문 실습 본문은 아직 개정하지 않았고 위 두 기존 후속 항목에 연결했다. managed payload와 설치본은 변경하지 않았으므로 이번 계획 보강의 adopter 적용은 해당 없음이다. 원 U1 작업 기록·accepted decision·실행 근거와 앞의 계획 제안은 그대로 보존했다.

이번 navigation 변경의 기준은 source `7d012f5297de1d9a77aa0b8187406f4785221573`와 직전 U2 계획 SHA-256 `44604e7af9f3573a20849701942d36fc11733c76fb41e86069bb4aa861540bfe`다. 기존 계획의 전체 bytes를 앞부분에 보존하고 이 절만 추가했다. 개발 인덱스는 두 후보 행의 Current navigation 셀만 변경했으며, SHA-256은 `4f6c8e6d5f78ebfa2417ddac2f8e374905549c2cacc9c48a148f127be56f9291`에서 `aeaaad2b52dc4fa760e96da38d07b07195f7a1422e78444e1e93982ca8c09b39`로 바뀌었다. 기존 criteria와 U1 완료 표시는 변경하지 않았다.


## R0-001 — Owner-Authorized Plan Review — 2026-10-21

### Request, Identity And Actual Execution

Owner는 문서 정렬 보강까지 포함한 이 계획을 Claude Code CLI로 R0 한 번 검토하고, 기존 인증·과금 경로, 지적별 처분과 착수 전 남은 판단을 정리하도록 요청했다. 구현은 명시적으로 보류했다. 이 날짜의 요청은 앞의 계획 작성 당시 “R0 미승인·미실행” 상태 뒤에 주어진 별도 검토 승인이다. U2 실행·새 Work·계약 변경·추가 reviewer 호출·Git·adopter 작업은 승인하지 않는다.

Driver는 Codex, Reviewer는 Claude Code CLI 2.1.305의 `claude-opus-5-5`다. 새 세션 `81e51b53-7b47-43bf-af82-9905c2477fa0`에서 기존 Claude Pro 구독 로그인(`authMethod=claude.ai`, `apiProvider=firstParty`, `subscriptionType=pro`)을 호출 직전 재확인했다. 환경의 API-key/token/base-URL 및 별도 provider override는 없었고 user settings에도 API-key helper나 env override가 없었다. 샌드박스 안의 최초 로그인 미확인은 실제 로컬 자격 증명 접근 환경에서 해소됐으며 재로그인·인증 경로 변경을 하지 않았다. 비밀값·계정 주소를 출력하거나 기록하지 않았다. 이는 이 Reviewer 호출의 인증 확인이며 U2 Codex host의 인증·모델 가용성 확인이 아니다.

실행은 `claude --print --safe-mode --tools "" --disable-slash-commands --strict-mcp-config --mcp-config '{"mcpServers":{}}' --permission-mode dontAsk --permission-prompts none --no-session-persistence --no-chrome --effort high --output-format stream-json --verbose`와 고정 Reviewer system prompt·새 session ID로 한 번 호출했다. 기존 task의 전용 durable review 경로를 작업 디렉터리와 입출력 위치로 사용했다. source와 실제 adopter에 대한 도구 접근·실행은 허용하지 않았다. 추가 모델 지정이나 fallback은 하지 않았고 실제 init의 model/session을 위에 기록했다.

2026-10-21 09:07:25.940–09:10:48.944 UTC, 203.003초, exit 0. 실행 상한 900초·종료 정리 20초 안에 자연 종료했고 process group 부재를 확인했다. 실제 tools 0, MCP 0, tool use 0. 제품 테스트·재현·host 실행은 0회다. 고정 자료를 읽은 fresh session이지만 Driver가 고른 packet에 한정되므로 독립 실행·전체 source 검토를 뜻하지 않는다.

입력은 base `7d012f5297de1d9a77aa0b8187406f4785221573`, tracked diff SHA-256 `87daf25ce53db09ee65f1accf76cba07abacc6e1a1065a94174e9e4eadf57fce`다. tracked diff는 개발 인덱스 두 navigation 셀뿐이고, untracked인 이 계획 전체는 별도 입력으로 전달했다. 요청 packet은 95,229 bytes / SHA-256 `c7a6a7b87135e48c855972b61614f53660f4b43c08f5807959eb85ef73d4c2f9`. 이 계획 전체와 관련 source 발췌를 제공했으며 실제 프로젝트 부록·식별정보·문서 본문·credential은 전달하지 않았다. 익명 대상 설명과 기존 Work가 이후 completed가 됐다는 한정된 준비 상태만 추가했다.

| Reviewed source input | SHA-256 |
| --- | --- |
| `docs/development/u2-single-host-continuous-work-plan.md` | `a3f5e539db24fea2f69fd30ad04ea4ea7a2084ebbf1a1d2e8caacbd6eaf46ad8` |
| `docs/development/README.md` | `aeaaad2b52dc4fa760e96da38d07b07195f7a1422e78444e1e93982ca8c09b39` |
| `docs/development/WORKFLOW.md` | `1b6c235c548157e5ad03ddb9dcc300729e0f25b68cc5162bb70033ea637aa928` |
| `docs/MAINTAINING.md` | `99c457472a5c5a6a0a0d5054e1473e335fdf2f37b9f51f8a2ea372de562a1d3a` |
| `docs/development/agent-delegation-m0-plan.md` | `4621ebb7a72d05a08fb702648c804c0fd0f85377786d7e4fa12a3896bd5842bb` |
| `docs/development/CHORE-20261021-001-continuation-contract-review.md` | `42e1fd037277512cbd75fbcbae9236c5e4148207c8bbdb8db2ce46ab66407f8a` |
| `manual/en/README.md` | `f44639152212ea1c33541d7f33f8ea0983420025aac518cccdabc14ed48d164a` |
| `manual/ko/README.md` | `64e2f21ce925ad90155f071a9d3d3a1305f805ee67af9e300eecbef3ac35f739` |

호출 전후 위 8개 파일·base·tracked diff·packet의 drift가 없었다. Reviewer가 스스로 hash·인증을 확인했다는 뜻은 아니며 Driver가 확인한 실행 사실이다. 아래 원문은 17,708 bytes / SHA-256 `d934f39fca5051a93bc97cc4758b0ab450cb716c3f289947e418a005921e7868`와 일치한다. 앞의 검토 입력 전체를 바꾸지 않고 이 기록을 뒤에 붙였다. 아래 Driver 보강은 이번 Reviewer가 재검토한 내용으로 세지 않는다.

### Reviewer Response — Verbatim

<!-- R0-001-REVIEWER-RESPONSE-BEGIN -->
~~~~markdown
# U2 R0-001 정적 검토 결과 (Reviewer: Claude)

## 0. 검토 정체성과 한계

- **Reviewer 모델**: 실행 환경에 표시된 모델 ID는 `claude-opus-5-5`입니다. 세션 ID와 인증·과금 경로는 제가 확인할 수 없습니다. Owner가 요청한 "기존 인증·과금 경로 확인"은 WORKFLOW 108행에 따른 호출 전 Driver 확인 사항입니다. 그 결과는 Driver가 기록해야 합니다. 이 검토의 Claude 인증은 U2 실행 모델·인증(gpt-6-astra/xhigh 등)에 대한 근거가 아닙니다.
- **검토 방식**: 도구·shell·네트워크·테스트를 사용하지 않은 정적 판독입니다. 아래의 어떤 내용도 실행·재현된 근거가 아닙니다.
- **입력 정체성**: 제공된 SHA-256과 크기는 대조할 수 없었습니다. 전달된 행 범위를 그대로 읽었을 뿐입니다. Driver가 왕복 전후 drift를 확인해야 합니다.

## 1. 종합 판정

**조건부 착수 가능.** 차단(blocker) 지적은 없습니다. 착수 전 해결이 필요한 지적은 4건(R-1~R-4)이며, 모두 문구 보정이나 짧은 명시로 해결할 수 있습니다. 비차단 지적은 7건입니다.

계획의 다음 측면은 정적으로 볼 때 건전합니다.
- 첫 host 단계의 fail-closed 원칙: 46·101·113행
- U1 한계 보존: 80행, CHORE 689·714행과 일치
- 문서·source·artifact·adopter 구분: 140·141·184·186행

다만 다음 네 가지가 고정되지 않아, 이대로 시작하면 H05·H06·H10의 완료 주장 범위가 실행 중에 Driver 해석으로 정해질 위험이 있습니다.
- R0가 무엇을 고정하는지
- 같은 Work 반복의 lifecycle 위치
- 복구 승인 근거의 형태
- 실제 업무가 어떤 runtime에 묶이는지

## 2. 지적 사항

### 착수 전 필요 (required-before-start)

**R-1. R0 대상에 고정한다고 한 파일 목록·실행 명령이 계획에 없음**

- **근거**
  - plan 40행: "신규 문서/host 연결의 최종 파일 목록과 exact 실행 명령은 R0 대상에 고정한다"
  - plan 82행: "상세 invocation을 승인된 준비 단계에서 고정"
  - plan 94행: "R0와 실행 입력 고정" 단계
  - WORKFLOW 108행: 실행 승인 시 명령·인자·runtime·작업 디렉터리·timeout·쓰기 경계를 고정
  - MAINTAINING 59행 (4): exact ID·모드·예상 시간은 실행 전 계획에 둠
- **결과**: 40행을 문자 그대로 읽으면 이번 R0는 그 대상을 검토하지 못했습니다. 82·94행 해석을 따르면 R0 이후에 고정되는 입력은 리뷰를 거치지 않습니다. 어느 쪽인지 기록되지 않으면 이후 "R0 완료"가 무엇을 덮는지 다툼이 생깁니다.
- **최소 보정**: 40행을 다음 취지로 바꿉니다. "R0는 경계·기준·예산을 검토한다. 파일 목록, exact 명령, runner, timeout, 쓰기 경계는 첫 host 실행 전에 source record에 고정한다. 그 내용이 R0를 거친 경계(새 권한 표면 없음, full-access 없음 등)를 벗어나면 해당 실행을 멈추고 Owner 결정을 받는다."
- **결정 성격**: 문구 정리는 Driver 몫입니다. 사후에 고정된 입력을 추가 검토 없이 수용할지는 Owner 선택입니다. 저는 추가 리뷰를 기본으로 권하지 않습니다.

**R-2. 같은 Work 반복의 lifecycle 위치가 isolated worker의 rework 금지와 충돌할 수 있음**

- **근거**
  - plan 11행: "수행 → 검증 → 허용 보정 → 검증된 후보 → 수락"
  - plan 33행
  - H06(61행): "고정 verifier가 실패 원인을 설명하고 … 보정 후 통과"
  - M0 148행: "The `rework` operation itself is forbidden for isolated workers … same-K baseline-refresh rebind followed by new submit-result … does not remove this barrier"
- **결과**: 보정이 submit-result 이후에 일어난다고 하면 isolated worker는 rework를 할 수 없습니다. 이 경우 H06은 "고정 oracle 안의 반복"이 아니라 금지된 경로 또는 정의되지 않은 경로를 시험하게 됩니다. 실행 중에 Owner reject나 local-mode 전환으로 우회하면 범위 밖 행동이 됩니다.
- **최소 보정**: 다음 두 가지를 한 문장으로 명시합니다.
  - 반복(검증→보정)은 submit-result 이전에 같은 Work 상태 안에서만 일어난다.
  - 제출 후 실패는 worker rework가 아니라 기존 Owner reject 등 기존 규칙의 경로로 돌아가며, 이는 "새 판단"(H08)으로 분류한다.
- **결정 성격**: Driver 명확화입니다.

**R-3. H05/V23의 "Owner 승인" 근거가 사전 일괄 승인이면 V23의 승인 요소를 증명하지 못함**

- **근거**
  - plan 69행: "V23의 fault injection과 복구는 처음부터 승인된 합성 시나리오의 exact original ticket으로 한정"
  - H05(60행): "Owner가 승인한 원 delegated ticket의 동일 actor/decision 재생"
  - M0 152행: "Recovery requires human approval for the trusted host to replay EXACT original delegated ticket bytes … the host must establish that recovery path … that evidence belongs to host qualification (M3/V23)"
  - M0 267행: V23
- **결과**: 계획 시점의 승인은 아직 존재하지 않는 ticket bytes에 결속될 수 없습니다. 그래서 H05가 통과해도 증명되는 것은 "동일 bytes·actor·decision 재생 메커니즘"까지입니다. host가 사람의 복구 승인을 어떻게 확인하는지(V23의 핵심)는 미관측으로 남습니다. 이를 구분하지 않으면 V23 완료로 과대 보고될 위험이 있습니다.
- **최소 보정**: 둘 중 하나를 고르면 됩니다.
  - (a) 복구 시점에 Owner가 기록된 ticket digest에 결속된 승인을 host 경로로 제공한다. 이때 Owner 대기는 예산에서 제외된다.
  - (b) H05 결과를 "재생 메커니즘 확인, host의 Owner 승인 확인 경로는 미검증"으로 보고하고, V23을 부분 완료로 표시한다.
- **결정 성격**: (a)/(b) 선택은 Owner 결정입니다. 어느 쪽이든 완료 기준을 조용히 약화하지 않으려면 67행의 완료 조건과 함께 기록해야 합니다.

**R-4. 실제 업무(H10)가 어떤 Core/adapter에 결속되는지, U2의 managed 변경과 어떻게 순서가 정해지는지 미정**

- **근거**
  - plan 32행: host 연결은 source-only이며 기본 backend가 아님
  - plan 40·86행: managed bytes가 바뀌면 inventory·설치 검증과 adopter 적용 결정이 필요함
  - plan 153–154행: 정렬 대상에 OPERATIONS·GENERAL-WORK·SKILL.md·AGENTS/CLAUDE 등 포함
  - plan 140행: 계약·운영 docs와 adapter는 payload에 포함됨
  - plan 111행: 설치·적용은 별도 Owner 결정
  - 공개 사실: Reference A는 installed a580 상태
  - MAINTAINING 57행: shipped prose는 inventory·installed/update/repair/detach 소비 확인, entry/adapter는 entry/resume 행동 확인 필요
- **결과**
  - 실제 업무는 a580 설치 안내 위에서 진행됩니다. 따라서 U2가 source에서 보정한 안내는 H10에서 관측되지 않습니다.
  - 위임 accept를 쓸 경우, source의 host 연결이 대상의 installed a580 Core를 호출하는지 source Core를 호출하는지 정해져 있지 않습니다. 버전 혼합이 생길 위험이 있습니다.
  - managed 변경 시 필요한 artifact·inventory·lifecycle 검사 시간이 355–505분 예상에 명시돼 있지 않습니다. 158행은 재산정만 약속합니다.
- **최소 보정**
  - H10은 "installed a580 + (사용 시) 그 설치본의 Core를 호출하는 source host 연결"로 수행한다고 명시합니다.
  - U2의 managed 안내 변경은 H10 근거에 포함되지 않는다고 보고합니다.
  - managed 변경이 생기면 artifact 검사가 예산을 넘는지 그 시점에 재산정한다는 조건을 추가합니다.
- **결정 성격**: 결속 명시는 Driver 몫입니다. U2 안에서 새 artifact를 실제 대상에 적용할지는 Owner 선택입니다. 현재 계획은 이를 제외하고 있으며, 그 제외를 유지하는 것도 정당한 선택입니다.

### 비차단 (nonblocking)

**N-1. 최종 회귀 예상 하한이 이미 측정된 값보다 낮음**
- **근거**: 97행 115–145분 vs 같은 행의 3583.493+3468.361초 = 117.531분. 이 값은 실패한 실행의 시간이고 "통합 확인"을 포함하지 않으며, U2 신규 테스트로 collection은 693을 넘을 것입니다. MAINTAINING 68행: 측정치+명시적 여유.
- **결과**: 하한이 비현실적입니다. 다만 180분 내부 상한과 82행의 재계산 조항이 있어 안전 문제는 아닙니다.
- **보정**: 하한을 약 125분 이상으로 올리거나, 측정치+여유 산식을 한 줄로 적습니다.

**N-2. M0이 지목한 대체 권한 표면의 재조사 목록이 계획에 없음**
- **근거**: M0 212행은 `additionalPermissions`, `permissions` 프로필, `externalSandbox`, policy-amendment 요청을 "present but unqualified"로 표시하고 자동 승인 금지를 요구합니다. plan 50행은 shellCommand·filesystem API·MCP·network만 나열합니다. 44행은 옛 결과를 대입하지 않는다고 적었습니다.
- **보정**: 0.163.0 schema 고정 시 이 표면들을 결과가 아닌 "재확인 항목"으로 H03 점검 목록에 넣습니다.

**N-3. H07의 "깨진 checkpoint" 판정 기준이 비어 있음**
- **근거**: H07(62행)의 "깨진 checkpoint는 unavailable"과 17·33행의 별도 장부 없음, narrative 소유.
- **결과**: 산문 narrative의 무결성은 Core가 강제하지 않습니다. 판정이 agent 판독에 의존하며 PASS 기준이 모호합니다.
- **보정**: H07 실행 전 준비 단계에서 33행의 필드(승인 참조, verifier, 시간·시도 사용량, 마지막 검증, 재개 조건) 중 누락이나 모순이 있으면 unavailable로 본다는 기준을 고정합니다. 이 근거가 runtime 보장이 아니라 안내 행동 근거라는 점도 명시합니다.

**N-4. host 부적격 시 비위임 실사용을 허용하는지 문구가 엇갈림**
- **근거**: 7행 "위임 수락을 사용하는 부분은 먼저 … 증명한 뒤 적용" vs 101·113행 "첫 host가 부적격이면 그 단계에서 멈춤", "실사용은 host 적격 확인 … 충족돼야".
- **결과**: 현재의 엄격한 해석(전체 정지)은 fail-closed로 안전합니다. 다만 7행만 읽으면 H06–H10의 비위임 진행이 가능해 보입니다.
- **결정 성격**: Owner 선택으로 확정하면 됩니다(§3).

**N-5. 23행의 대상 준비 조건 문구가 현재 사실보다 이전 상태임**
- **근거**: 23행 "다른 Driver가 제출한 문서 Work의 수락·dirty 처리"와 공개 사실 "수락·완료됨, Git/writer 인계는 live 재확인 필요".
- **보정**: 남은 조건을 "Git·dirty·단일 writer 기준점의 live 재확인"으로 갱신합니다. 그 Work를 인계하지 않는다는 문장은 유지합니다.

**N-6. 개발 인덱스 navigation 링크의 범주와 링크 대상**
- **근거**
  - tracked diff 69·71행: "Unselected; [link]"
  - WORKFLOW 56행: navigation은 "task/closeout links and candidate selected/closed/dropped notices"
  - README 83행: 기록된 Owner 결정이 있으면 navigation 변경 가능
  - plan 128–132행: Owner 결정 기록
- **결과**: 계획 절 링크는 56행이 나열한 범주 밖이어서 해석 여지가 있습니다. 독자가 부분 선택으로 오인할 수 있습니다. 또한 계획 파일이 untracked이므로 인덱스만 보존되면 링크가 깨집니다.
- **보정**: 다음 두 가지를 기록합니다.
  - 이 링크가 기록된 Owner 결정에 근거한 참조용 navigation이며 선택이 아니라는 점
  - 인덱스와 계획 파일은 함께 보존해야 한다는 조건
- **결정 성격**: 범주 해석이 부족하다고 보면 Owner 판단 사항입니다.

**N-7. 남은 실습 범위가 후보의 명시 항목과 완전히 대응하지 않음**
- **근거**
  - README 91행: 후속 계획은 clone guidance, human companions, optional editorial observations를 식별해야 함
  - README 101행 경로: doctor, init preview/apply, verification
  - plan 165행: 이 항목들이 빠짐
- **결과**: 166행에 따라 실행은 별도 계획이므로 지금 결함은 아닙니다. 다만 링크된 이 절이 README 91행의 "follow-up plan"을 충족한 것으로 읽힐 수 있습니다.
- **보정**: 이 절은 연결 기록일 뿐이며, 91·101행 항목은 별도 계획이 식별한다는 한 문장을 추가합니다.

## 3. Owner 선택과 Driver 명확화의 구분

**실제 Owner 선택**
1. R-1: R0 이후 고정되는 exact 입력을 추가 검토 없이 수용할지 여부. 경계 이탈 시 정지는 전제입니다.
2. R-3: V23 승인 근거를 (a) 복구 시점의 digest 결속 승인으로 할지, (b) 부분 완료로 보고할지. (b)를 택하면 67행 완료 조건을 함께 조정하는 것은 **제안된 Owner 결정**이며, 조용한 약화가 아닙니다.
3. R-4: U2 안에서 새 artifact를 Reference A에 적용할지. 계획은 제외 중입니다.
4. N-4: host 부적격 시 비위임 실사용(H06–H10)을 허용할지, 전체를 정지할지.
5. 계획 승인 자체와 비공개 대상 부록 승인(109·111행), 실제 실행 모델·effort·인증·과금 확인 결과의 수용.
6. N-6: navigation 범주 해석(필요 시).

**Driver 명확화(일상 처리)**: R-1 문구, R-2, R-4의 결속 문장, N-1, N-2, N-3, N-5, N-7.

각 지적에 대한 accept/revise/defend/needs-user 처분은 Driver가 기록합니다. 위 Owner 선택 항목은 needs-user 후보로 보입니다.

## 4. 요청된 관점별 평가

**추정·상한**
- 단계 합계 355/505분은 산술적으로 맞습니다.
- 600분 누적 상한, host 120분, 테스트 180분 상한, 대기 제외 규칙, 시도 2회, 동일 원인 재실패 시 정지 규칙(90·101·103행)은 일관됩니다.
- 신규 trusted host 연결(canonical ticket 소유, handle 재검증)과 H01–H05(H05 fault injection 포함)를 60–90분에 끝낸다는 예상은 낙관적입니다. 그러나 계획 스스로 "미측정"이라 표시했고 120분 정지가 있으므로, 결과가 "미확인"으로 끝날 가능성이 클 뿐 안전 문제는 아닙니다.
- 하한 문제는 N-1, artifact 비용 누락은 R-4에서 다뤘습니다.

**첫 host fail-closed 가능성**
- 46행은 M0 202·212행의 핵심을 보존합니다. 자동 upgrade, 외부 sandbox, 다른 backend, full-access, 권한 확대로 대체하지 않으며, 부적격이나 미확인이면 정지합니다.
- 48행은 모델 인자를 권한으로 믿지 않고, 실행 직전 bytes·binding·grant를 재검증합니다.
- 105행은 TERM/KILL과 자식 종료 확인을 두어, "stop request ≠ 종료"(M0 144행)를 반영합니다.
- 정적으로 실현 가능한 설계로 보입니다. 보완점은 N-2입니다. 실제 차단 여부는 실행 없이 평가할 수 없습니다.

**U1 한계 보존**
- 80행은 CHORE 689·714행과 일치합니다(normal 110+5, O 116/116, P/Q 6/6, 전체 실행 실패, errno-35 미해결, 조건부 R1, 합성 reader).
- 97행은 옛 시간을 PASS나 성능 보장으로 쓰지 않는다고 밝힙니다.
- 130·166행은 전체 매뉴얼 개정을 U1의 소급 기준으로 만들지 않습니다.
- 문제를 찾지 못했습니다.

**같은 Work 반복 vs 위임**
- 반복은 Work narrative가, 이후 선택은 CONT가 소유합니다(17행). 수락 주체(사람 / 정확한 grant 1회)도 분리돼 있습니다.
- authority apply를 자동 retry하지 않는다는 원칙(34·69행)도 명확합니다.
- 남은 공백은 R-2(제출 전후 경계)와 N-4(위임 없는 진행 허용 여부)입니다.

**H01–H10 근거·커버리지**
- M0 204행의 M3 목록이 H01–H03·H05에 대응합니다: payload 교체, Owner 사칭, home/action 오류, 직접 우회, 중복·모호 call, 동일 decision 복구.
- H04는 1회 소비와 revoke를 다룹니다.
- 합성과 실제를 구분하고, 자연 업무에서 사례를 억지로 만들지 않으며, Owner 시간이 없으면 미측정으로 둡니다(67행). 이는 정직한 기준입니다.
- 약점
  - H05의 승인 요소(R-3)
  - H07 판정 기준(N-3)
  - H09: 3개 합성 사례를 누가 분류하는지(Driver 자체 vs 새 agent) 정해지지 않아 자기평가가 될 수 있습니다. 결과 보고 시 분류자를 명시하면 됩니다.
- 82행의 전체 회귀 선정 이유는 MAINTAINING 46·57행(수락·복구 의미와 상호작용)에 부합합니다.

**문서·source·artifact·adopter 구분**
- 140행(manual은 source-only), 141행(대상별 반영은 private 종료 보고 소유), 184행(source commit ≠ 설치), 186행(이번 보강의 adopter 적용 해당 없음)이 명확합니다.
- 실행 중 이 구분을 위협하는 지점은 R-4뿐입니다.

## 5. 이 packet으로 평가할 수 없는 것

- 비공개 대상 부록, Reference A의 실제 상태, Git/writer 인계, 운영 가이드 범위와 5개 경로의 적정성
- Driver 관측값: 30개 payload 일치, EN/KO digest marker 6쌍, CLI 0.163.0, macOS 버전
- 입력 SHA-256과 크기
- 0.163.0 schema와 공식 App Server 문서 내용
- 미제공 문서: FEAT-20261016, DR-0005, PATCH-20261018, SECURITY-AND-SUPPORT, MAINTAINING의 다른 절
- U2 실행 모델·인증·과금, 이번 Reviewer 세션의 인증·과금 경로
- 모든 실제 강제·차단·종료·복구 동작. 위 판단은 정적 추론이며 재현된 결과가 아닙니다.

추가 리뷰 라운드는 권하지 않습니다. 위 보정은 Driver 처분과 Owner 결정으로 처리할 수 있는 범위입니다.
~~~~
<!-- R0-001-REVIEWER-RESPONSE-END -->

### Driver Dispositions And Clarified Proposal

현재 결론은 “계획 경계는 조건부로 타당하나 실행 착수는 아직 보류”다. R0는 1회 완료했지만 실행 명세가 아직 고정되지 않았고 Owner 실행 승인이 없다. 아래는 계획·처분의 명확화이며 implementation이나 technical contract 변경이 아니다. Reviewer의 blocker 0, 착수 전 필요 4건, 비차단 7건을 그대로 보존한다.

| ID | Driver 처분 | 이번 정리와 남은 조건 |
| --- | --- | --- |
| R-1 | revise | 이번 R0는 범위·완료 기준·권한 경계·예산을 검토했다. 최종 파일 목록·명령·runner를 검토했다고 주장하지 않는다. 첫 실행 전에 같은 기록의 실행 명세로 파일/명령·인자·runtime·cwd·write/read/network 범위·tool allowlist·timeout·종료 확인·정확한 H/test ID를 고정해야 한다. 아직 미완료다. 추가 검토 전면 면제는 채택하지 않는다. |
| R-2 | accept | 같은 Work의 검증→보정 반복은 `submit-result` 전의 허용 content 작업으로 한정한다. 제출 후 문제는 H08의 새 판단으로 돌아가며 worker `rework`, 자동 reject/rebind 또는 local-mode 전환으로 우회하지 않는다. 아래 lifecycle 명확화 적용. |
| R-3 | needs-user | H05/V23 완료 기준을 유지하는 (a)를 권고한다. 실제 중단 상태·종료와 원 ticket bytes/digest·actor·decision을 확인한 뒤, host의 사람 전용 승인 경로로 정확한 복구 승인을 받아 재생한다. 사전 시나리오 승인이나 delegate가 주장한 승인만으로 대체하지 않는다. 정확한 ticket이 생기기 전의 이 계획 승인은 복구 승인으로 세지 않는다. |
| R-4 | revise | 실제 H10은 현행 verified installed a580와 그 설치본의 launcher/Core·adapter에 결속한다. source-only host 연결도 실제 대상에서는 그 설치본만 호출하고 source Core를 섞지 않는다. managed 변경이 생기면 그 새 artifact·consumer 검사는 source 검증이며, 미적용 상태의 H10은 새 문서/adapter 실사용 근거가 아니다. 새로운 실제 설치는 이번 기본 제안에서 계속 제외한다. |
| N-1 | accept | 최종 회귀+통합 예상은125–145분으로 보정한다. 기존117.531분에 약7.5–27.5분의 판단 여유를 더한 값이며 신규 collection 비용은 아직 미측정이다. 전체 예상은365–505분(6시간5분–8시간25분), 누적 상한600분이다. 아래 산정 조건을 따른다. |
| N-2 | accept | 현행 schema/정책 점검에 `additionalPermissions`, named `permissions` profile, `externalSandbox`, permission/policy-amendment 요청을 명시한다. 존재한다고 사용하지 않으며 자동 허용·fallback은 없다. 채택할 정확한 surface와 deny 경로를 실행 명세에 넣는다. |
| N-3 | accept | H07의 필수 narrative 항목은 승인 참조·고정 scope/verifier·누적 시간/시도·마지막 단계/결과·재개 조건이다. 누락·모순·해결되지 않은 입력 drift·사용량 불명은 unavailable이며 0으로 초기화하지 않는다. 이는 안내/host 관측 기준이지 Core가 산문 무결성이나 budget을 강제한다는 주장이 아니다. |
| N-4 | defend | 본 제안의 기존 엄격한 조건을 유지한다. host 부적격·미확인 또는 host120분 상한이면 이 U2 실행 묶음을 중지하고, 비위임 실사용으로 자동 전환하지 않는다. 별도의 일반 업무 가능성과 이번 U2 완료를 구분한다. 이를 바꾸고 싶을 때만 새 scope 판단이 필요하다. |
| N-5 | accept | 계획 초안의 이전 review 상태는 당시 snapshot이다. 검토 packet에 제공한 갱신 사실은 기존 Work completed이며, 남은 실제 착수 조건은 branch/HEAD·dirty·binding·Git 처리·단일 writer의 live 재확인이다. 다른 Driver의 Work나 진행을 인계하지 않는다. 현재 정리는 그 이후 상태를 새로 검증한 주장도 아니다. |
| N-6 | defend / clarify | Owner가 기존 후속 항목 연결을 직접 요청했고 그 날짜·기준 diff가 이 note에 있다. 두 링크는 source Workflow가 허용한 preliminary review note를 찾는 참조이며 후보 선택·criteria 변경이 아니다. 이 요청을 새 navigation 정책으로 일반화하지 않는다. 인덱스와 이 untracked 계획은 한 쌍으로 보존·향후 제출해야 하며 인덱스만 commit하는 것은 불충분하다. 이번에는 Git 작업을 하지 않는다. |
| N-7 | accept | 앞의 Remaining First-Path Tutorial은 기존 후보와의 연결 및 영향 범위 기록이다. 전체 후속 착수 계획을 대체하지 않는다. 그 별도 계획은 clone/source acquisition, human companions, optional editorial observations, doctor, init preview/apply, 검증, 첫 결과 수락과 fresh-session resume를 각각 식별하고 실행/의미/이해도 근거를 구분해야 한다. |

R-1의 후속 명세에는 reviewed envelope 안의 경로·인자 확정과 새 실행 의미를 구분한다. 단순 구체화는 기존 source 절차대로 기록하고 Owner에게 구체적인 착수안을 제시한다. 새로운 권한 표면·oracle·runner 동작·계약 또는 검토되지 않은 주요 위험이 필요하면 해당 실행을 멈추고 적용되는 R0 또는 명시적 면제 판단을 받는다. 이 구분은 지금 추가 reviewer 호출을 승인하거나 모든 future runner를 검토 없이 허용한다는 뜻이 아니다. 이번에 허용된 R0 1회는 소비했으며 자동 재호출하지 않는다.

R-2는 [Supervised Work Iteration](../GENERAL-WORK.md#supervised-work-iteration)과 [Worker Publication Development Checkpoint](../GENERAL-WORK.md#worker-publication-development-checkpoint)를 Driver가 추가 정적 대조했다. `src/hv2ref/work.py`의 isolated-worktree 검사는 worker rework를 거절하고 human baseline refresh를 요구한다. 제출 후 필요한 reject/rebind/resubmission은 각각 현재 상태에 맞는 기존 사람 권한 경로를 확인해야 하며 “Owner reject 하나면 다시 편집 가능”이라고 단순화하지 않는다. 기존 grant의 소비·selected-revoke barrier는 이 반복으로 초기화하지 않는다.

R-3의 완료 주장에는 exact same-ticket replay와 host가 별도의 사람 승인 근거를 확인했다는 두 결과가 모두 필요하다. 복구 input/action·대상·현재 pending 관측을 사람이 확인할 수 있게 제시하고, 승인 전달을 worker가 위조하거나 재사용할 수 없음을 합성 deny case로 확인한다. 새 Core 승인 장부를 만들지 않는다. 사람 응답 대기는 시작/종료를 기록해 제외하되, 준비·상태 확인·실제 복구·검증은 활동시간이다. 승인을 받지 못하면 H05/V23은 부분/미완료로 남기고 H01–H10 전체 완료 기준도 충족하지 못한다. (b)로 바꾸는 완료 기준 축소는 제안에 채택하지 않았다.

R-4는 synthetic host qualification에서도 actual H10과 같은 installed a580 호출 경로를 사용해야 한다는 조건을 포함한다. 다른 source invocation으로 통과한 결과를 그대로 옮기지 않는다. managed 문서/adapter를 바꾸면 새 inventory와 installed/update/repair/detach consumer, affected entry/resume 검증을 산정한다. 그 활동비용을 아직 “포함된 실측”으로 제시하지 않는다. 새 scope가 예상 또는 남은600분·각 내부 상한에 맞지 않으면 추가 실행 전에 재산정·정지하고 최소 후속안을 낸다. source 문서 정렬은 그 변경에 포함하되 미적용 새 안내를 실제 installed 검증으로 표시하지 않는다.

H09 분류자는 이 제안에서 Driver로 고정한다. 3개 합성 사례의 분류 이유를 source 결과에 기록하고 R1에서 근거를 읽을 수 있게 한다. 이는 fresh-agent/user 이해도나 독립 판정 실행을 추가한 것이 아니다. 신규 agent 호출은 포함하지 않는다.

### Additional Driver Finding — Worker Result Commit Boundary

D-1, 착수 전 해결 필요 / needs-user. Reviewer 원문 외에 Driver가 [Worker Publication Development Checkpoint](../GENERAL-WORK.md#worker-publication-development-checkpoint)를 대조해 확인했다. isolated-worker `submit-result`는 worker HEAD가 보존된 candidate commit이고 전체 관측 내용이 committed result와 일치해야 한다. 따라서 앞의 “Git 제외”를 모든 local Git mutation의 금지로 해석하면 실제 위임 경로가 성립하지 않는다. 이는 실행된 반례가 아니라 기존 계약을 읽어 확인한 계획 공백이다.

권고하는 구분은 다음과 같다. source/실제 control branch의 commit·push·PR·merge와 공개 출판은 계속 제외한다. 합성 fixture의 Git 조작은 승인된 검증 명령 안에서만 수행한다. 실제 업무에서 필요한 worker candidate commit은 해당 프로젝트가 exact 내용·메시지·필수 trailer와 필요한 retained ref를 별도로 승인한 범위에서 trusted control 경로가 수행한다. 모델 worker에는 Git 관리 영역의 직접 쓰기를 주지 않는다. 그 권한을 받지 못하면 isolated submission/H10은 미완료로 남기며 worker가 임의 commit하거나 다른 모드로 전환하지 않는다. 정확한 commit 묶음은 아직 없고 이번에 만들거나 실행하지 않았다.

### Remaining Owner Decisions Before Start

1. 먼저 R-1의 실행 명세를 검토 가능한 수준으로 구체화한 뒤, 실제 대상 부록·H01–H10·single-host 경계와 보정된 예상/상한을 포함한 착수안을 결정한다. 현재 review 승인만으로 시작하지 않는다. U2 host의 실제 model/effort·인증/과금·effective restriction 확인은 별도 준비 항목이며 이번 Claude 인증 확인을 재사용하지 않는다.
2. H05/V23는 정확한 복구 승인 관측까지 완료하는 원 기준을 유지할지 확인한다. 권고는 유지다. 이후 실제 original ticket과 상태가 준비되면 그 정확한 복구 승인은 해당 시점의 사람 판단으로 남는다. 부분 완료를 전체 완료로 수락하는 변경은 자동으로 넣지 않는다.
3. 실제 작업 선택/intent·ordinary delegate grant와 D-1의 필요한 worker candidate commit 권한을 대상 프로젝트 규칙에 맞춰 결정한다. 기술 입력이 없는 지금 포괄 commit 승인을 요구하지 않는다. 실제 문서 Work의 단일 writer 기준점을 확인하기 전에는 시작하지 않는다.

새 adopter update, host 실패 뒤의 비위임 전환, 전면 입문 실습 개정은 권고 착수안에 추가하지 않았다. 이 제외를 유지하는 데 별도의 반복 확인이 필요한 것으로 취급하지 않는다. 바꾸려는 경우에만 그 범위와 비용을 새로 판단한다. navigation 두 링크도 기존 Owner 연결 요청 안의 기록이며 별도 정책 채택을 요청하지 않는다.

### Revised Estimate And Review Accounting

앞의355–505분 중 회귀/통합 하한만115→125분으로 보정해 전체365–505분을 제안한다. host 연결과 H01–H05의60–90분은 미측정 판단값이며,120분 안에 적격 여부를 증명하지 못하면 미확인으로 정지한다. 이를 완주 보장으로 표현하지 않는다. 전체600분·host120분·전체 회귀180분 중 가장 먼저 닿는 상한을 적용하며, full normal/O 각1회·보정 묶음 최대2회·R0/R1 각1회 제안은 그대로다. 새 artifact 비용과 발견된 collection에 따라 실제 실행 전 재산정한다.

이번 R0는 첫30–45분 단계의 기수행 부분이며 착수 후 같은 R0를 다시 예산에 넣거나 호출하지 않는다. 활동시간은 이번 Owner review 요청부터 종료 checkpoint까지 누적해 이후 제안의600분에서 차감할 값으로 보존한다. reviewer203.003초와 그 대기는 활동시간에 한 번만 포함한다. 이 시간 기록은600분 실행의 사전 승인이 아니다.

### Documentation Closeout And Retention

- 이번에 정렬한 문서: 기존 source U2 계획에 이번 R0의 정확한 요청·입력·원문·처분·남은 판단만 추가했다. 비공개 대상 부록은 review 완료 사실과 이 정본 링크만 연결한다. implementation·기존 accepted U1 record·normative docs·adapter·실습 본문은 바꾸지 않았다.
- 남은 문서와 후속: R-1 exact 실행 명세, D-1 실제 worker 제출의 Git 권한 구체화는 U2 착수안의 잔여다. 입문 실습 본문 개정과 실제 이해도는 기존 Product Documentation And Comprehension / Onboarding And First Work 범위로 남는다.
- adopter 반영 여부: 이번 기록은 source-only이며 managed payload 변경·새 artifact·실제 설치 업데이트는 없다. a580 installed 실사용 제안과 향후 source 변경의 근거를 구분했다.

검토 packet·raw API envelope·one-use controller·별도 response 복사본은 진행 중 검토와 원문 이관 소비가 끝나면 정리한다. 원문이 이 문서에 byte-identical로 보존됐고 입력 prefix/계약 무변경·process 부재를 검증한 후에만 삭제한다. compact private metadata는 Owner의 착수 판단과 승인된 record 인계까지 input/drift·auth 실행 사실을 설명하는 근거로 유지한다. 이 계획과 인덱스, 기존 private 대상 부록, 현재 source worktree는 그 가까운 다음 계획 판단에 필요하므로 유지한다. 새 source 전체 복사본·실행 환경 archive는 만들지 않는다.


### R0 Completion Checkpoint — 2026-10-21 09:19:39 UTC

이번 R0 요청부터 이 종료 checkpoint까지 활동시간은 16.9분(1016.692초)이다. 전용 Owner 응답 대기는 없었고 CLI 실행203.003초를 포함해 겹치는 시간을 한 번만 계산했다. 이후 같은 U2 묶음이 승인되면 제안600분에서 이 값을 이어받는다(남은 상한 약583.1분). 첫 단계의 R0 1회는 이미 끝났으며 추가 실행 명세 작성 비용과 예상은 착수안에 남긴다.

기록 검사는 GFM 3문서·로컬 링크70개·anchor50개에서 오류0, 원문 byte identity와 검토 입력 prefix 보존, 나머지7개 review source 입력·tracked navigation diff 불변을 확인했다. 원문은 자체 Markdown 표기까지 보존하기 위해 fenced Markdown으로 수록했다. 변경 없는 제품/실습 테스트는 실행하지 않았다. source에는 이 계획과 기존 두 navigation 셀 변경만 남고 implementation·accepted U1·managed payload는 그대로다.

소비가 끝난 이 round 전용 파일6개(request packet, raw stream, empty stderr, one-use controller, attempt marker, 별도 response 복사본)를 정리했다. 원문·요청 범위·입력 identity·처분은 이 계획에 보존했고 compact private metadata와 대상 부록을 유지한다. source worktree·기존 task/root·활성 경로는 이동하거나 retarget하지 않았다. 이 계획과 인덱스는 다음 exact 실행 명세/Owner 착수 판단을 위해 함께 유지한다. 추가 reviewer 호출·host 실행·실제 Work·Git·설치 변경은0회다.

## Pre-Start Execution Specification — 2026-10-21

상태: Owner가 R0 처분을 실행 명세로 구체화하도록 요청한 제안이다. 구현·host/model 실행·실제 Work·Git mutation은 시작하지 않았다. 이전 R0 원문과 당시 상태는 보존한다. 현재 제안의 우선순위는 이 절 → R0 처분 → 초기 계획이며, 원 계약이나 U1 수락 기준을 바꾸지 않는다. Owner는 원 ticket에 대한 사람 승인 복구 방식을 유지하도록 결정했다. R-3의 방식 선택은 해소됐지만, 아직 없는 ticket의 복구를 미리 승인한 것은 아니다.

### Execution Shape And File Boundary

```text
Source: host 연결·회귀·합성 fixture → H01–H09
                                      ↓ 적격일 때만
설치 a580 + 실제 문서 Work → 편집·검증·최대2회 보정
  → 사람의 exact candidate commit 승인 → trusted Driver가 commit/보존 ref
  → installed publish → exact grant의 delegate accept 1회 → H10
중단/불명확 apply → 원 bytes·pending·프로세스 종료 확인
  → 사람이 그 ticket의 복구 승인 → 같은 actor/decision 재생 1회
```

아래 경로는 승인 뒤 만들거나 수정할 파일의 닫힌 목록이다. 아직 구현 파일은 존재하지 않으며 명령의 새 CLI도 구현할 interface 제안이다. Source task ID는 선택 승인 후 기존 절차에 따라 다음 미사용 ID를 부여한다. 이 계획을 별도 progress ledger로 늘리지 않는다.

| 구분 | 제안 파일 | 역할과 변경 한계 |
| --- | --- | --- |
| Source 구현 | `docs/development/verification/u2-host/host.py` | stdio App Server 연결, admitted call 검증, fixed verifier, installed CLI 호출. Core를 import해 authority 결정을 대체하지 않음 |
| Source 합성 fixture | `tests/fixtures/u2_host.py` | task-local fixture·canary·S0–S5 interruption barrier. 실제 프로젝트에서는 import/활성화 금지 |
| Source 단위 검사 | `tests/test_u2_host.py` | 아래 8개 고정 ID. 실제 host enforcement나 모델 품질로 집계하지 않음 |
| Source 사용 안내 | `docs/development/verification/u2-host/README.md` | exact invocation, 권한·복구·결과 해석. managed 배포 대상 아님 |
| Source 기록 | 승인 후 source record 1개, `docs/development/README.md`, 이 계획 | task 소유권·입력 참조와 기존 navigation 정렬. accepted U1 원문은 그대로 보존 |
| 조건부 source 안내 | `docs/development/agent-delegation-m0-plan.md` | 실제 관측을 날짜 있는 후속 포인터로 연결할 때만 추가. 원 M0 계획/결과를 덮어쓰지 않음. Core/managed adapter 변경은 이 기본 묶음에서 제외 |
| 비공개 실행 보조물 | task의 `run-tests-native.py`, `verification-git.sb`, `execution.json`, `profile.json`, `runs/` | 기존 검증 runner의 경로·선택·현재 identity를 최소 변경. input·invocation·원 로그·failure fixture·종료 관측을 durable 경로에 보존 |

실제 대상의 5개 문서·read allowlist·Git 기준점·grant·실행 경로는 Owner용 비공개 실행 묶음에 고정한다. 실제 식별정보를 source나 외부 review packet으로 옮기지 않는다. target writer와 control branch의 commit/PR 진행은 이 계획이 소유하지 않는다.

### Fixed Runtime And Proposed Command Interface

`SOURCE`는 현재 계획 checkout, `ARTIFACT`는 이 task의 durable 실행 하위 경로, `TARGET`은 합성 installed control 또는 승인된 실제 installed control, `WORKER`는 정확한 등록 worktree다. Owner용 묶음에서 절대경로로 치환한다. 명령은 shell 문자열을 모델로부터 받지 않고 argv 배열로 구성한다.

| ID | 제안 명령, cwd=`SOURCE` | 실행·쓰기·상한 |
| --- | --- | --- |
| E00 | `PY -I -B ARTIFACT/run-tests-native.py collect normal 300 discover` | source 읽기, 자기 run 디렉터리만 쓰기. collection과 입력 고정, 테스트 본문 실행 없음 |
| E01 | `PY -I -B SOURCE/docs/development/verification/u2-host/host.py preflight --spec ARTIFACT/execution.json` | 버전·auth 종류·effective config/schema·경로 identity 확인. 비밀값 미기록, model turn 없음, 300초 |
| E02 | `PY -I -B SOURCE/docs/development/verification/u2-host/host.py qualify --spec ARTIFACT/execution.json --cases H01,H02,H03,H04,H05` | 합성 대상만. H05는 아래 사람 승인 입력이 올 때까지 정지. host 단계 전체120분 우선 |
| E03 | `PY -I -B SOURCE/docs/development/verification/u2-host/host.py iterate --spec ARTIFACT/execution.json --cases H06,H07,H08` | 합성 같은-Work 실패·보정·중단·재개. H09는 Driver의 3개 사례 분류 문서 |
| E04 | `PY -I -B ARTIFACT/run-tests-native.py focused normal 1800 @ARTIFACT/focused-ids.json` | 최초 exact55개=기존47+새8. 보정 때는 그중 영향 ID를 사유와 함께 봉인하고 집중 검사 |
| E05 | `PY -I -B ARTIFACT/run-tests-native.py full normal 6300 discover` | 현재693+새8=701개 예상. 실제 collection 일치 후 1회 |
| E06 | `PY -I -B ARTIFACT/run-tests-native.py full optimized 6300 discover` | 동일701개 parent `-O` 1회. E05+E06+cleanup 누적180분 우선 |
| E07 | `PY -I -B SOURCE/docs/development/verification/u2-host/host.py actual --spec ARTIFACT/execution.json --case H10` | host 적격·target intent/grant 수락·writer 확인 후 실제 5문서만. 자동 commit/submission/recovery 없음 |
| E08 | `PY -I -B SOURCE/docs/development/verification/u2-host/host.py recover --spec ARTIFACT/execution.json --ticket TICKET --human-approval APPROVAL` | 신뢰된 사람이 승인한 원 bytes의 같은 actor/decision만 1회. pending/종료 재확인, 300초 |

`PY`는 final/GIL CPython3.14.7, `-I -B`가 기본이다. native 회귀 child는 기존 `-I -S -B`, optimized parent만 `-O`를 추가한다. Git과 허용 helper·runtime·runner/policy hash를 invocation에 고정한다. 과거 U1 runner는 삭제된 checkout 경로가 박혀 있으므로 그대로 실행하지 않는다. 새 runner는 `collect`, exact `@ids`, 새 source/run 경로만 추가하며 assertion·native timeout·oracle·failure 분류를 바꾸지 않는다. 기존 factory 모드는 이 기본 실행에 포함하지 않는다. a580 managed bytes 무변경을 먼저 확인해 기존 exact P/Q6 및 M1/M2 artifact 근거를 해당 범위만 재사용한다.

모든 child는 새 process group과 durable stdout/stderr/result를 갖는다. timeout은 단계·전체 잔여 중 작은 값, TERM10초→KILL10초와 실제 group 부재 확인을 포함한다. 불명확 종료는 통과가 아니며 child가 살아 있으면 cleanup/retry 금지다. 테스트용 HOME/XDG/TMP는 child env에만 task-local 경로를 준다. 전역 환경·사용자 인증 위치·sandbox 설정은 변경하지 않는다. 기본 native test policy는 source/runtime 읽기, 해당 run만 쓰기, network deny와 기존 native Git helper allowlist를 유지한다.

### App Server Policy And Admission

현행0.163.0의 로컬 `generate-json-schema --experimental`에서 thread/turn의 named `permissions`, dynamic tool의 `threadId/turnId/callId`, permission request/response를 읽었다. 이는 schema 관측이다. [공식 Permissions 문서](https://learn.chatgpt.com/docs/permissions)의 profile은 beta이며 legacy `sandbox_mode`/`--sandbox`와 합성되지 않으므로 둘을 섞지 않는다. 실제 enforcement는 H03에서만 판정한다.

App Server 실행은 기존 ChatGPT 로그인 경로를 사용하는 `codex app-server --listen stdio://` 1개다. 세션 override로 발견된 MCP3개를 모두 disabled, `features.apps=false`, `features.hooks=false`, `features.multi_agent=false`, `features.multi_agent_v2=false`, `features.code_mode=false`, `features.code_mode_host=false`, `web_search="disabled"`를 고정한다. user/enterprise config를 수정하지 않는다. 예상치 못한 plugin·hook·MCP·native tool이 남으면 모델 turn 전에 중지한다. 다른 권한·외부 sandbox·추가 backend로 대체하지 않는다.

`thread/start`는 `model=gpt-6-astra`, `allowProviderModelFallback=false`, `approvalPolicy=never`, `permissions=colvia-u2-worker`, `cwd=WORKER`, `runtimeWorkspaceRoots=[WORKER]`, `environments=[]`, `ephemeral=true`와 고정 dynamic tool2개를 사용한다. `turn/start`도 같은 profile/cwd/roots, `effort=xhigh`, `environments=[]`를 유지한다. legacy `sandbox`/`sandboxPolicy`와 `additionalPermissions`는 보내지 않는다. active profile ID 확인만으로 성공 처리하지 않고 effective config와 실제 deny 결과를 함께 요구한다.

| 경계 | 허용 | 거절/차단 |
| --- | --- | --- |
| Worker filesystem | minimal 실행 runtime, 승인된 source/doc read 파일, 실제 결과5파일 쓰기, task 소유 worker scratch만 쓰기 | control checkout·`.hrn`·managed payload·실제 git/common-dir·설정·credentials·다른 task 읽기/쓰기, system tmp 쓰기. root/worker 전체를 write로 허용하지 않음 |
| Worker 도구 | sandbox 안의 `exec_command`, 그 자식만의 `write_stdin`, `apply_patch`; `u2_verify(verifier_id)`, `u2_accept(handle)` | server RPC를 일반 함수처럼 전달, arbitrary host shell, 다른 dynamic tool, MCP/apps/web/network, agent spawn. 추가 tool은 조용히 허용하지 않음 |
| 권한 요청 | 기존 policy 안의 도구 수행 | permission request는 `permissions={}`, scope=turn; command/file approval은 decline/cancel. `acceptForSession`, exec/network policy amendment, full-access, externalSandbox, settings write 없음 |
| Trusted host | 승인한 ID의 verifier와 installed launcher 호출, 고정 상태/근거 읽기, 자기 로그 쓰기 | 모델이 actor/home/action/path/argv/ticket bytes 선택, 외부 임의경로·URL·설정 mutation |
| 네트워크/인증 | App Server 자신의 기존 ChatGPT 모델 통신만 | worker command network=false, API-key/provider override, 모델 대체. private key/token/email/log 원문을 모델·evidence로 전달하지 않음 |

profile은 `:minimal=read`, system temp deny와 정확한 절대 파일 allowlist로 구성하며 나머지는 미허용으로 둔다. 실제 worker는 명시한 파일만 읽을 수 있어야 하고, symlink/alias를 따라 밖으로 나갈 수 없어야 한다. secret 위치의 실제 값을 읽어 시험하지 않고 합성 deny canary로 검사한다. 현재 host가 개별 파일 write·원자적 교체·좁은 read를 지원하지 않으면 H03 미확인/실패로 중지한다. 루트 write로 넓히는 편법은 없다.

worker가 narrative를 편집해도 승인·사용량을 변경한 것으로 인정하지 않는다. trusted Driver가 보유한 승인 입력과 마지막 체크포인트에 대조하고, host가 기록한 사용량/stop을 narrative에 반영한다. 불일치하면 중지하며 새 Core budget 장부를 도입하지 않는다.

`u2_verify`는 `DOC-LINKS`, `DOC-GFM`, `DOC-CLAIMS` 세 enum만 받는다. `u2_accept`의 schema는 `{"handle":"opaque string"}`만 허용하고 additionalProperties=false다. trusted host는 call의 thread/turn/call을 admitted 실행에 결속하고 handle로 자기 소유 ticket을 조회한다. 실행 직전 Work·selected intent/revision·actor·scope·binding·evidence/result·bytes/digest·one-use를 다시 확인한다. handle 전달이나 모델의 “승인됐다”는 문장은 권한이 아니다. grant는 1회 acceptance에만 적용하며 commit·새 intent·revoke·복구·다른 action을 허용하지 않는다.

### Verification IDs And Recovery Cases

기존 테스트 ID는 U1 normal 원본693개와 현재 `HEAD`의 tests tree가 같음을 Git으로 확인해 선택 기준만 재사용했다. 그 원본에는 error1이 있으며 이번에 통과한 것으로 바꾸지 않는다. 비공개 `execution-test-selection.json`에 원693 ID, 정적 확인한 기존47 focused ID, 신규8 ID, 합계701 제안 집합이 있다. 새 구현 뒤 격리 collection이 집합과 다르면 delta/위험/잔여 시간을 보고한 뒤 필요한 변경을 판단한다. 별도 factory는 default discovery에 숨겨 합산하지 않는다.

| H ID | 고정 case ID / 주요 oracle |
| --- | --- |
| H01 | `H01-foreign-thread`, `-foreign-turn`, `-unknown-call`, `-owner-spoof`, `-home-action-scope`; host 거절+control bytes/mode 무변경 |
| H02 | `H02-ticket-swap`, `-digest`, `-result-swap`, `-duplicate`; immutable handle→bytes 재검증, 재시도 성공으로 바꾸지 않음 |
| H03 | `H03-control-write`, `-runtime-write`, `-git-write`, `-policy-write`, `-credential-read`, `-symlink-alias`, `-permission-escalation`, `-network-tool`; 실제 같은 worker policy·canary hash/mode와 deny code |
| H04 | `H04-accept-once`, `-used-grant`, `-revoked`, `-other-work-action`; 정상1회와 사용/revoke 이후 거절 |
| H05 | `H05-S0`부터 `H05-S5`, `H05-human-forgery`, `-approval-reuse`; 아래 exact 사람 복구·원결정·중복 미게시 |
| H06 | `H06-fixed-verifier-fail-correct-pass`; 제출 전 scope 내 보정, 같은 oracle |
| H07 | `H07-resume`, `-missing-budget`, `-input-drift`; 누적 시간/시도 carry, unavailable을0으로 바꾸지 않음 |
| H08 | `H08-new-scope`, `-new-ticket`, `-revoke`, `-limit`, `-owner-stop`, `-repeat-no-evidence`, `-post-submit`; 중단 후 자동 fallback 없음 |
| H09 | `H09-ordinary`, `-same-work`, `-umbrella`; Driver 분류3개, 독립 사용자 이해도 주장 없음 |
| H10 | `H10-content`, `-scope`, `-evidence`, `-owner-effort`; 실제5문서 정확성·누락·불필요수정과 Owner 재설명/승인/조작/대기 관측 분리 |

신규 단위 ID는 `test_u2_host.U2HostTests.test_h01_admission_binding`, `test_h02_payload_binding`, `test_h03_permission_routes`, `test_h04_single_use`, `test_h05_human_recovery_gate`, `test_h06_pre_submit_iteration`, `test_h07_resume_budget`, `test_h08_stop_boundaries`다. 기존 집중 범위는 `test_delegated_acceptance.DelegatedAcceptanceTests`22개와 `test_worktree_execution`의 Publication/Application/InstalledPublication25개다. 단위8개는 live H01–H08을 대체하지 않는다.

S0=durable decision 전, S1=decision/all-pre, S2=mixed, S3=all-post/selection 전, S4=selection/current 전, S5=current 게시 후다. 합성 전용 fixture는 기존 installed apply 경계에 barrier를 걸고 fsync된 관측 후 실제 child를 TERM/KILL해 종료를 확인한다. S1=`after-decision`, S2=2개 변경 중 첫 `after-file`, S3=1개 변경의 `after-file`, S4=`after-selection`, S5=`after-current`, S0=호출 전이다. 기존 exception injection만 실행한 결과는 process-death 증거가 아니다. barrier를 위한 test-only wrapper는 설치된 Core의 기존 호출에만 적용하며 실제 H10에서는 비활성이다.

S1–S5의 ticket/path/SHA-256·actor·decision·pending·프로세스 부재를 사람이 볼 수 있는 고정 packet으로 제시한다. 사람은 그 packet의 정확한 ticket 목록에 복구1회를 승인할 수 있다. 승인은 worker가 쓸 수 없는 control 입력이며 call ID/표식 파일을 worker가 만들었다고 인정하지 않는다. S0는 durable decision이 없음을 확인하고 기존 apply를 자동 재호출하지 않는다. S5 replay는 역사적 동일 결정 조회/복구이며 현재 결과를 다시 승격하지 않아야 한다. mixed/all-post cancellation 거절, 승인 위조/재사용 거절을 별도로 확인한다. target의 실제 authority 실패에도 같은 방식이 필요하며 합성 승인으로 이전하지 않는다.

### Actual Work, Git And Remaining Decisions

실제 Work는 별도 intent `schema_version=3`의 ordinary isolated-worker grant를 제안한다. action=accept, delegate=`colvia-u2-delegate`, exact Work identity와5파일 scope를 결속한다. intent의 goal/outcome/oracle/forbidden scope, selected revision과 수락 ticket은 실제 입력을 만든 뒤 사람이 확인한다. 이 문서의 JSON 설명 자체를 published draft나 수락으로 취급하지 않는다.

worker는 제출 전에만 편집·검증·보정한다. 결과가 준비되면 trusted Driver가 exact5파일 diff/whole-tree·기준 commit·message/trailer·scope·검증 결과를 먼저 제시한다. 사람의 그 commit 승인 뒤 worker를 멈추고 trusted Driver가 worker candidate commit1개 및 base/result 보존 ref를 만든다. 실제 control checkout의 index/HEAD·business files를 이 commit으로 변경하지 않는다. `work publish --worker`와 delegate accept 후 control의 business files·`.hrn`이 바뀌는 것은 installed acceptance의 결과이며, control Git commit/push/PR/merge는 별도 권한으로 남는다. Git hook 오류를 무시하거나 `--no-verify`로 우회하지 않는다.

기존 실제 target의 runtime은 다른 담당 작업에서 commit됐음을 이번 읽기 전용 확인으로 관측했다. 현재 base에 verified executable launcher가 포함되어 있어, 이 U2가 runtime 보존 commit을 추가로 만들 필요는 없다. 시작 시 branch/HEAD/dirty·writer와 필요한 untracked/ignored 상태를 다시 확인한다. clean tree만으로 writer 중단을 추정하지 않는다. 현재 source 실제 대상 식별정보는 비공개 묶음만 소유한다.

남은 판단은 (1) 이 source/target 묶음의 구현·host 실행 범위와 시간, (2) 실제 업무의 exact intent/grant 수락, (3) 준비된 worker candidate commit과 실제 발생한 원 ticket 복구다. (2)와(3)는 구체적인 입력이 생겼을 때만 해당 정확한 판단을 받는다. 반복 검증·허용 보정을 매번 승인받는 조건을 추가하지 않는다. 이번 명세의 새 profile/runner·human gate 설계는 완료한 R0에 들어 있지 않다. 새 실행 의미를 검토한 독립 결과가 아직 없으므로, 적용되는 source review 절차에 따라 필요한 focused 검토 또는 명시적 면제를 실행 전에 결정해야 한다. 이번 요청은 추가 CLI review나 면제를 승인하지 않았다.

### Estimate And Documentation Impact

R0+입력 고정의 종전30–45분은 실제 진행을 반영해50–75분으로 조정한다. R0 실측16.9분과 이번 명세 작성·검사 누적을 포함하며, 같은 R0를 다시 호출하는 비용을 넣지 않는다. 나머지 단계는60–90 +60–90 +125–145 +60–90 +30–45분으로 유지해 전체385–535분(6시간25분–8시간55분), 누적 중단 상한600분을 제안한다. 현재 구현/host는 미측정이며, 필요해진 추가 독립검토는 남은 입력 고정 시간 안에서 산정하고 넘으면 실행 전에 재산정한다. host120분·full pair180분, normal/O 각1회와 scope 내 보정 최대2회는 유지한다. 전용 Owner 대기 제외·중첩 wall time1회·이전 소요 carry 규칙도 같다.

- 이번 정렬: R0 R-1/R-2/R-4와 D-1을 파일·명령·권한·ID·Git 순서에 반영했고, R-3는 Owner가 선택한 원 ticket 사람 승인 방식으로 고정했다. 공개 계획과 private target 실행 묶음은 서로 역할을 나눠 한 검토 묶음을 이룬다.
- 남은 문서: 실제 구현 후 해당 host README/source record/조건부 delegation 안내와 문서 의미·명령·링크를 확인한다. EN/KO3단계 입문 실습·concepts 후속은 기존 담당 후보에 남으며 이번 구현 범위에 합치지 않는다. 문서 검사를 이해도 PASS로 부르지 않는다.
- Adopter 반영: 기존 installed a580 고정. 새 runtime/adapter artifact·adopter update 없음. H10은 이 설치본과5문서 Work의 범위에만 적용된다.


### Execution Specification Checkpoint — 2026-10-21 09:42:52 UTC

이번 명세 작성·읽기 전용 확인의 활동시간은 19.6분이다. 전용 Owner 대기는 없었다. 앞선 R0 16.9분과 합쳐 36.6분을 제안600분에서 이어받고 남은 상한은 약563.4분이다. 이 산정은 실행 승인이나 남은 시간 안의 완주 보장이 아니다.

기존 R0 원문을 포함한 앞선69,781 bytes는 SHA-256 `dd7943b8cb9f18307e2c13852bc39ea2c29a60dfca300af9b88bca6ed005937f` 그대로 보존했다. 구현·native tests·host/model turn·추가 CLI review·실제 Work·Git mutation은0회다. 로컬 schema export/feature 목록과 installed 상태 읽기는 host 권한 검증으로 세지 않는다. focused55/full701은 실행 전 선택 제안이며 PASS가 아니다.

정리: 실행 명세는 이 source 문서와 private 대상 묶음에 보존한다. 새로 export한 task-owned schema 중 내용 동등성이 입증된 중복433개는 제거하고 aggregate2개와 개별17개를 host protocol 입력 확정까지 유지한다. source로 이관한 명세 작성용 복사본도 exact 이관 확인 뒤 제거했다. source checkout·실제 target·기존 task의 활성 경로는 이동하거나 바꾸지 않았다. 기존 U1 실패/회복 근거와 R0 원문은 그대로 유지한다.

## Focused Execution Review R0-002 — 2026-10-21

최신 상태: Owner가 새 실행 명세의 profile·runner·사람 승인 복구와 실제 대상 grant·worker commit 경계를 Claude Code CLI로 1회 검토하도록 요청했다. 정확한 비식별 packet의 외부 전송도 별도로 승인했다. 검토는 완료됐고 종합 판정은 조건부다. 아래 처분은 Driver의 보완 제안이며 구현·host 실행·실제 intent/grant·Git 작업의 승인이 아니다. 앞의 실행 명세는 검토 당시 입력으로 보존하고, 충돌하는 부분은 아래 보완안을 최신 제안으로 읽는다. Owner가 보완안을 채택했다는 기록은 아직 없다.

### Request, Identity And Execution Evidence

- 범위: 실행 명세의 권한·순서·검증 oracle. 정적 검토만 허용했으며 reviewer tool/MCP 사용은0, 테스트·재현·구현은0이다.
- source base=`7d012f5297de1d9a77aa0b8187406f4785221573`; tracked diff SHA-256=`87daf25ce53db09ee65f1accf76cba07abacc6e1a1065a94174e9e4eadf57fce`. 이 계획은 untracked 입력으로 별도 포함됐으며 검토 직전90717bytes, SHA-256=`fff12c53798f0f5007a67a60ca5f3d2e8b5ff86f32d8b55351d0c000b11ad11f`다. 비공개 실행 묶음·선택 ID·이전 runner/policy·로컬 protocol도 diff 밖 입력이다. 전체15입력은 실행 전후 digest가 같았다.
- packet160981bytes, SHA-256=`cf1a4081163fd94c785f8b26d87a7a326198151b990284e85e0f7a89e2fad231`. 실제 대상 이름·경로·revision·read 파일명은 일관된 기호로 치환했고 실제 대상 파일 본문·자격 증명은 제외했다. 권한과 명령 순서는 유지했다. 비공개 묶음 입력 SHA-256=`64982187d536d98598ed1cf2910bb96464f17d8ee3927cbe87ef681daa9438e3`.
- 사전 인증: Claude Code2.1.305, `claude.ai / firstParty / pro`; API/provider/OAuth/config override8개는 없음. 계정 이메일·비밀값은 기록하지 않았다. sandbox 안의 미인증 관측은 밖의 실제 인증 확인으로 구분했다. CLI가 보고한 list-price 추산은 실제 구독 청구액의 증거가 아니다.
- fresh session=`48837398-a048-4a6c-8bec-a4a6147bde74`, actual model=`claude-opus-5-5`. 기존 R0와 모델 계열의 독립성은 보장하지 않는다. 고정 argv는 `claude --print --safe-mode --tools '' --disable-slash-commands --strict-mcp-config --mcp-config '{"mcpServers":{}}' --permission-mode dontAsk --permission-prompts none --no-session-persistence --no-chrome --effort high --output-format stream-json --verbose`와 고정 system prompt/session ID였다. 실제 인자는 배열로 전달했다.
- 실행09:54:50.590551–09:58:39.321412 UTC,228.730초, exit0, timeout 아님, process group 부재 확인. 실제 reviewer 호출1회다. 최초 자동 승인 검토는 외부 payload 승인이 불충분하다는 이유로 프로세스 생성 전에 차단했다. Owner의 정확한 packet 전송 승인 뒤 같은 입력으로 실행했으며 이 차단은 추가 reviewer 실행이 아니다.
- 응답20001bytes, SHA-256=`2da65da8ee09a0189728d56b68d6316b5ae0f7dfede371e1c179fd02dc1a1559`. 아래 원문은 bytes 그대로 보존한다. 구체적인 비공개 입력 manifest와 실행 메타데이터는 기존 task record에서 관리한다.

### Driver Disposition — Proposed Corrections

| 지적 | 처분 | 필요한 시점 | 결론 |
| --- | --- | --- | --- |
| F-01 High | accept | 실제 대상 B 전 | 지원하는 tags namespace와 base/result 생성 순서를 적용하는 제안 |
| F-02 High | revise | source A 전 | 편집 종료와 accept turn을 E07a/E07b로 분리; 같은 actor/thread의 쓰기 없는 후속 turn |
| F-03 High | revise / needs-user | source A 전 | 정확한 사람 응답을 trusted Driver가 중계하는 채널과 그 신뢰 한계 결정 |
| F-04 Medium | revise / needs-user | source A 전 | 계측된 종료 주입과 순정 installed replay의 근거를 구분하는 R-4 보완 |
| F-05 Medium | accept | oracle은 A 전, 관측은 실제 turn 전 | actual cwd의 모든 config layer·도구·신규 생성/교체·비파괴 canary 확인 |
| F-06 Medium | revise / defend | source A 전 | 외부 누적 deadline·종료 기록 보완 수용; 기존 오류 재발 허용은 채택하지 않음 |
| F-07 Medium | accept | 실제 commit C 전 | hook·identity·환경과 전체 commit 결과를 승인 범위에 결속 |
| F-08 Medium | revise | 실제 대상 B 전 | intent required ref는 output과 비중첩; Work post-blob 규칙과 구별 |

F-01: Driver가 `_retention`과 manifest 검사를 직접 읽어 `refs/heads/`와 `refs/tags/`만 지원함을 확인했다([work.py](../../src/hv2ref/work.py)). base tag는 이름·expected absence·OID를 사람의 Git setup 승인에 포함하고 worker 생성/start publication 전에 생성·검증한다. result tag는 candidate commit 검증 뒤, result publication 전에 생성한다. 임의 namespace·기존 tag overwrite는 허용하지 않는다. 합성 H04/H06에서 지원 namespace의 성공과 비지원 namespace의 거절을 확인한다. 현재 tag는 만들지 않았다.

F-02: E07a는 기존 `actual --case H10`의 편집·검증 단계이며 봉인한 후보에서 모델 turn과 그 자식 쓰기 프로세스가 끝나야 한다. Driver가 exact candidate 승인·commit 검증·result tag·result publication·delegate accept prepare를 수행한 뒤, E07b=`host.py actual-accept --spec ARTIFACT/execution.json --handle HANDLE`을 제안한다. 같은 admitted actor/thread의 후속 turn에서 `colvia-u2-accept`라는 쓰기 없는 named profile을 적용하고 실제 유효성을 관측한다. `u2_accept`만 authority effect를 갖는다. turn마다 dynamic tool 목록을 교체할 수 있다고 가정하지 않는다. 남는 `u2_verify`는 phase gate로 거절하고 native tool의 쓰기도 거절해야 한다. handle은 봉인한 ticket/actor/result/thread/turn/call에 결속하며1회만 소비한다. 같은 thread에서 동등한 제한을 입증하지 못하면 host 미확인으로 중단하며 새 thread/principal로 자동 전환하지 않는다. H08-post-submit은 해당 후속 turn의 실제 write 거절과 control/worker 불변을 확인한다. host가 worker 요청 없이 대신 accept하는 방식은 채택하지 않는다.

F-03: 권고 채널은 이 Codex 대화에서 실제 사람이 exact recovery packet에 응답하고 trusted Driver가 그 응답 참조를 host 입력에 중계하는 방식이다. 레코드는 ticket SHA-256, packet SHA-256, S 상태, pending 관측 digest, process-group 부재 관측, 원 actor/decision, `replay 1회` 범위, 실제 사람 응답 참조를 포함한다. host는 replay 직전 상태를 다시 확인하고 input mismatch/reuse를 거절하며 자기 run log에 소비를 기록한다. 새 Core 권한 장부는 만들지 않는다. worker가 파일을 만들거나 승인 문자열을 말하는 것은 사람 승인이 아니다. 이 방식은 trusted Driver가 거짓 사람 응답을 만들어내는 공격까지 암호학적으로 방지하지 않는다. 그 보장까지 요구한다면 독립된 사람 인증 UI/채널이 필요하므로 현재 host 범위 안에서 충족했다고 주장하지 않고 별도 설계를 판단한다. S0는 이미 시작된 결정의 복구가 아니며 재호출에는 새 authority 판단이 필요하다. H05에는 다른 ticket, 상태 drift, 승인 재사용, worker 위조 거절을 포함한다. 실제 복구 승인은 실제 원 ticket이 생겼을 때만 받는다.

F-04: 제안은 합성 대상에서만 test-only wrapper가 검증된 installed launcher를 실행하면서 해당 installed module의 실제 publication helper에 barrier를 거는 방식이다. source module cache를 섞지 않도록 로드된 module 경로·digest와 launcher/inventory를 확인하며 installed bytes는 바꾸지 않는다. barrier는 실제 publish 직후 writer guard 안에서 fsync 관측을 남기고 대기해야 한다. 예외로 guard를 빠져나온 뒤 대기한 결과는 process-death 근거로 인정하지 않는다. TERM/KILL 후 process group 부재·S별 파일 bytes를 확인하고 replay는 wrapper 없는 installed `colvia work apply`로 수행한다. H04 정상 경로와 H10도 순정 installed 호출을 사용한다. wrapper의 경로/hash는 합성 profile에만 허용하고 실제 실행 admission에서 wrapper/import hook의 부재를 확인한다. 계측된 최초 호출과 순정 호출이 완전히 같다는 기존 R-4 표현은 유지할 수 없으므로, 이 근거 경계의 보완을 Owner 판단으로 남긴다. wrapper가 실제 guard 안의 정확한 지점을 만들 수 있는지는 구현 후 입증 대상이다.

F-05: E07a/E07b 각각 첫 turn 전에 실제 `cwd=WORKER`의 `config/read(includeLayers=true)`를 확인한다. 모든 layer의 legacy `sandbox_mode` 부재, 정확한 named profile 정의·hash와 `extends` 부재, 예상 instruction sources, 활성 tool/plugin inventory를 대조한다. `disabledPluginIds`만으로 capability가 사라졌다고 판단하지 않는다. 관측 불가능하거나 예상 밖 노출이 있으면 중단한다. 실제 profile canary는 ARTIFACT의 task-owned 합성 경로에만 적용하고 실제 control bytes에 위험한 write 시도를 하지 않는다. file allowlist의 기존 파일 쓰기·새 파일 생성·원자적 교체와 alias/범위 밖/시스템 temp/network 거절을 합성 H03에서 확인한다. 실제 경로의 정책·경계와 합성 canary가 입증한 범위를 나눠 보고하며 control 전체의 직접 침투 검증으로 과장하지 않는다.

F-06: E05/E06의6300은 호출 때마다 보장되는 시간이 아니라 단계 최대초다. 외부 controller는 시작 전 `SECONDS=min(6300, full-pair 누적10800초 잔여-cleanup reserve, 전체 잔여-cleanup reserve)`를 계산하며 잔여가 없으면 실행하지 않는다. 개별 test의 native timeout은 바꾸지 않는다. TERM/KILL과 종료 대기도 이 deadline 안에 포함하고 최종 미종료 상태·exception에도 completion 기록을 남긴다. 과거 error1은 `test_continuation_recovery.ContinuationRecoveryTests.test_cancellation_prefixes_keep_prior_choice_and_original_bytes`, subtest=`original='after-choice', cancel='after-staged-current'`, 내부 Git topology probe의 `BlockingIOError errno35`가 `ContractError`로 감싸진 경우다. 이는 원인이 확정된 상시 허용 결함이 아니다. 같은 ID/분류가 재발해도 실패로 중단하고 fixture/stack/state를 보존한다. reviewer의 동일 오류 별도허용 제안은 채택하지 않는다. 영향 집중 검사는 승인된 보정 범위와 잔여 예산 안에서 판단하며 normal/O full 각1회 상한을 자동으로 다시 열지 않는다. 추가 full이 필요하면 실패를 제시하고 새 bounded 실행 판단을 받는다. 현재 오류를 재현하거나 고쳤다는 주장은 없다.

F-07: candidate 승인 packet에 유효 `core.hooksPath`와 실행 hook 목록/hash, author/committer identity, 적용 Git config·환경과 hook 실행 권한 범위를 포함한다. 비밀값은 기록하지 않으며 identity의 실제 값은 비공개 packet에서만 확인한다. 승인하지 않은 credential/network 권한을 hook에 추가하지 않는다. `--no-verify`로 우회하지 않는다. commit 뒤 parent, 전체 tree membership/bytes/mode, `HEAD^{tree}`, 메시지 bytes와 trailer, index/working tree 상태를 승인본과 대조하고 일치해야 result tag를 만든다. 다르면 commit을 자동 reset/amend하지 않고 그 상태를 보존해 중단한다. 합성 H06/H08에 hook이 index 또는 메시지를 바꾸는1건을 포함한다.

F-08: Driver가 `_worker_external_refs`를 읽어 required intent input과 변경 path의 동일·조상·자손 overlap은 거절됨을 확인했다. retained post blob 검사는 required Work reference에만 적용된다. reviewer 최소 수정의 “겹친다면 post blob”은 intent에는 적용할 수 없어 이 부분을 수정한다. 실제 대상 부록에서 read27과 구별되는 최소 required intent refs를 명시하고5개 output과 비중첩을 확인한다. existing Work narrative는 start 후 첫 모델 편집 loop 전에 trusted Driver가 승인된5파일 중 narrative 경로에 계획·scope·예산·resume 기준을 seed한다. start 기준점은 기존 base이며 새 narrative를 포함한 결과는 submit 때 post blob으로 결속한다. required intent ref에 신규 narrative를 넣지 않는다. 별도6번째 파일·baseline commit·추가 상태 장부는 만들지 않는다. exact intent draft에서 참조 집합과 시작 순서를 사람이 확인한다.

### Coverage Limits And Remaining Owner Decisions

V22는 H01–H03, V23은 H05의 실제 host 의무로 남는다. V24는 전체 old/new window와 draft-before-acceptance·rollback/recovery 조합에 관한 Core 의무이므로 delegated focused22개의 통과만으로 충족했다고 표시하지 않는다([M0 계획](agent-delegation-m0-plan.md)). 기존 근거와 예정 full collection의 관련 ID를 구현 전 대조하고 빠진 위험이 있으면 focused 선택과 예상에 반영한다. 지금 실행하지 않은701개를 V24 통과 근거로 쓰지 않는다. 새 test method를 무조건 늘리기보다 기존 H subcase/관련 회귀 근거를 재사용한다. 새로운 범위나 상한 변경이 필요하면 먼저 재산정한다.

착수 전 필요한 판단은 보완안 채택과 source A 실행 범위·시간이다. 특히 F-03의 trusted Driver 중계 신뢰 범위와 F-04의 계측/순정 근거 구분이 결정 대상이다. 이1회 검토는 요청된 새 실행 의미를 검토했고, 후속 보완안이 다시 독립 검토됐다고 표시하지 않는다. 통상적인 finding 처분을 이유로 자동 R0-003을 열지 않는다. 실제 구현 R1은 기존 계획의 별도 검토 단계다.

실제 대상 B/C/D는 host 적격 뒤 exact 입력이 준비될 때 결정한다: 대상 read27의 ChatGPT 전달 범위와5문서 scope·required refs를 포함한 intent/grant, base tag/worker setup의 이름·OID, 결과 candidate의 diff·hook·identity·메시지·commit/result tag, 실제 원 ticket의 복구 승인. 정상 delegate accept에는 수락된 grant가 권한 근거이며 불필요한 재승인 gate를 덧붙이지 않는다. 이번 Claude packet 전송 승인을 실제 대상 본문 전송 승인으로 재사용하지 않는다.

기존 예상385–535분과 누적600분, host120분·full pair180분을 유지하는 제안이다. 이 집중 검토·처분 시간은 첫 입력 고정50–75분에 포함해 누적하고 reviewer 대기는 활동시간에1회만 산입한다. 현재 host/보완 구현비는 판단값이며 관측된 추가 범위가 잔여에 맞지 않으면 실행 전에 재산정한다. U1의 error1·host 미검증·실제 사용자 검증 한계는 그대로다.

### Reviewer Response — Verbatim

~~~~text
# R0-002 집중 정적 검토 — U2 실행 명세

## 종합 판정: **조건부 (conditional)**

이 판정은 계획의 구현 가능성과 권한 정합성에 대한 의견입니다. 실행, 구현, 커밋, 복구 승인을 뜻하지 않습니다.

- **정합한 부분:** 전체 권한 구조는 기존 계약과 대체로 맞습니다.
  - 명명 프로필 사용, legacy sandbox와 혼용 금지.
  - grant 1회 사용, 원 ticket에 대한 사람 승인 복구.
  - control의 HEAD/index 무변경.
  - 테스트 ID 산술: 22+25=47, 47+8=55, 693+8=701.
- **구현 전에 고정할 결함:** 계약과 직접 충돌하거나 구현 형태를 결정하는 설계 공백이 있습니다.
  - Git 보존 ref의 namespace와 생성 순서.
  - 제출 후 accept를 누가 호출하는지.
  - 사람 승인 입력의 채널과 결속 방식.
  - S0–S5 barrier 메커니즘.
- **수정 규모:** 모두 명세 문장이나 표 수준의 작은 보완으로 해소할 수 있습니다. 일반적인 재설계는 필요하지 않습니다.
- **단계별 필요 시점:**
  - F-02, F-03, F-04, F-05, F-06은 source 구현(단계 A) 전에 필요합니다. host 구조와 H04/H05 설계에 직접 영향을 줍니다.
  - F-01, F-07, F-08은 단계 A 구현 자체를 막지는 않습니다. 다만 해당 단계(B/C) 착수 전에 필요합니다.

---

## Findings

### F-01 — 보존 ref namespace가 계약상 미지원이고, base ref 생성이 start 이후로 배치됨
- **심각도:** High
- **분류:** 착수 전 필요 (단계 B 전, 사람의 Git 승인 묶음에 반영)
- **근거:**
  - C 0139: 보존 ref로 `refs/colvia-u2/target-operations-work/base`와 `/result`를 제안합니다. 계약 GENERAL-WORK 0273은 "Heads and tags are supported; arbitrary ref namespaces are not"이라고 정합니다.
  - C 0139와 A 0100은 commit 승인 이후에 base/result ref를 함께 만듭니다. 그러나 GENERAL-WORK 0273은 start manifest를 포함한 publication 전에 이름을 정하고 검증하라고 요구합니다. 0252도 start manifest의 base가 "retained by existing refs"여야 한다고 정합니다.
  - C 0116의 `work publish --input START_INPUT`는 worker 결과보다 먼저 실행됩니다.
  - 코드 work.py 0487–0488은 retention ref를 `show-ref --verify`로 검증합니다. 이 packet만으로는 `validate_manifest`의 namespace 제한 여부를 확인할 수 없습니다.
- **위험:**
  - start 또는 submit이 거절되거나, 계약 밖 ref에 의존하는 manifest가 생깁니다.
  - start 시점에 base를 보존하는 ref가 없을 수 있습니다.
  - control 저장소의 공유 common-dir에 ref를 쓰는 작업이 명시된 Git 승인 범위 밖에 놓일 수 있습니다.
- **최소 수정:**
  - 보존 ref를 `refs/tags/<승인된 이름>/base`와 `/result`로 바꿉니다.
  - base tag는 worker 생성 전, start publish 전에 trusted Driver가 생성합니다. 이 생성은 별도로 승인된 Git setup 단계로 순서에 넣습니다.
  - result tag는 candidate commit 직후에 생성합니다.
  - 두 tag 모두 사람의 Git 승인 범위에 이름과 OID 조건으로 명시합니다.
- **확인:**
  - 합성 fixture(H04/H06 경로)에서 tags namespace로 start → submit → accept를 통과하는지 봅니다.
  - 비지원 namespace를 쓰면 거절되는지(또는 계약 위반임을) 1건으로 관측합니다.

### F-02 — worker를 멈춘 뒤 제출하는 순서와 `u2_accept`를 worker 도구로 둔 설계가 충돌
- **심각도:** High
- **분류:** 착수 전 필요 (단계 A 전, host 구조 결정)
- **근거:**
  - A 0100: 사람의 commit 승인 뒤 **worker를 멈춘다**.
  - A 0011–0012: 그 다음에 publish → delegate accept 1회.
  - A 0062: `u2_accept(handle)`는 worker 모델의 dynamic tool입니다.
  - A 0044의 E07은 "자동 commit/submission 없음"입니다. 그러나 commit 이후의 publish/accept를 실행할 host 하위 명령이 E00–E08 닫힌 목록에 없습니다.
- **위험:**
  - delegate accept의 주체가 불명확해집니다. 모델이 호출할지, host가 직접 호출할지가 정해져 있지 않습니다.
  - 제출 후에도 같은 프로필(5파일 write)과 `apply_patch`가 남으면 post-submit 편집을 막을 장치가 없습니다. 이는 R-2와 GENERAL-WORK 0142의 경계를 넘습니다.
  - host가 직접 accept하면 "위임 actor 행사"라는 H10의 의미가 바뀝니다.
- **최소 수정:**
  - E07을 두 단계로 나눕니다. (a) 편집·검증 단계는 제출 전 후보에서 정지합니다. (b) Driver의 commit, base/result ref 생성, publish를 거친 뒤 별도 accept 단계를 둡니다.
  - (b)에 고정 명령 ID를 부여합니다(예: E07b).
  - accept 단계의 turn은 쓰기 없는 profile로 제한하고 `u2_accept`만 노출합니다(또는 동등한 제한). 이때 publish된 정확한 handle 1개만 유효합니다.
  - 제출 후 편집 시도는 H08 `-post-submit` 거절 oracle로 연결합니다.
- **확인:**
  - 합성 H04/H08에서 제출 후 같은 thread의 write 시도가 거절되는지 봅니다.
  - accept 단계에서 `u2_accept`가 1회만 성공하는지 봅니다.

### F-03 — 사람 복구 승인 입력의 채널·형식·결속·1회성이 정의되지 않음
- **심각도:** High
- **분류:** 착수 전 필요 (단계 A 전)
- **근거:**
  - A 0045: `recover --ticket TICKET --human-approval APPROVAL`.
  - A 0094: 승인은 "worker가 쓸 수 없는 control 입력"입니다.
  - C 0034: `ARTIFACT/human/`.
  - B 0023: "host가 별도의 사람 승인 근거를 확인"해야 한다고 요구합니다.
- **빠진 정의:**
  - **결속:** 승인이 무엇에 묶이는지 정의가 없습니다. 후보는 ticket digest, 제시 packet digest, S 상태 분류, pending 관측, 프로세스 부재 관측 시각입니다.
  - **입력 경로:** 사람이 승인을 어떤 경로로 넣는지 정의가 없습니다(TTY 대화형 확인 등).
  - **1회 소비 기록:** 소비 기록을 어디에 남기는지 정의가 없습니다.
  - **위조 대상:** H05의 forgery 사례는 worker 위조만 다룹니다. Driver 에이전트가 같은 디렉터리에 파일을 쓰는 경우와 구분되지 않습니다.
  - **S0 이후:** "자동 재호출 금지"만 있고, 다음 조치에 어떤 권한이 필요한지 없습니다. 같은 ticket을 다시 apply하면 새 authority 행사가 됩니다.
- **위험:**
  - 승인 게이트가 사실상 파일 존재 확인으로 축소됩니다.
  - packet을 제시한 뒤 상태가 바뀌어도(drift, 다른 S 상태) 이전 승인이 재사용될 수 있습니다.
- **최소 수정:**
  - 승인 레코드의 필수 필드를 고정합니다: ticket SHA-256, packet SHA-256, S 상태, pending 관측 digest, 승인 범위 "replay 1회".
  - 입력 채널을 고정하고, host가 recover 직전에 상태를 재관측해 packet과 일치할 때만 수락하도록 합니다.
  - 소비는 host 자기 로그에 1회 기록합니다. 새 Core 장부는 만들지 않습니다.
  - S0는 "복구 아님, 별도 판단 필요"로 명시합니다.
- **확인:**
  - H05 `-approval-reuse`와 `-human-forgery` 사례에 다음을 추가합니다: packet과 상태 불일치 거절, 다른 ticket 승인 거절.
  - 사람 대기 시간은 별도 기록합니다.

### F-04 — S0–S5 실제 프로세스 barrier 메커니즘이 R-4의 동일 installed 경로 조건과 충돌할 수 있음
- **심각도:** Medium
- **분류:** 착수 전 필요 (단계 A 전)
- **근거:**
  - A 0092: barrier를 "설치된 Core의 기존 호출에만 적용하는 test-only wrapper"로 건다고 합니다.
  - B 0025: 합성 qualification도 actual H10과 같은 installed a580 호출 경로여야 합니다.
  - MAINTAINING 0074: launcher가 12개 모듈을 검증한 뒤 실행합니다.
  - MAINTAINING 0136: 실제 프로세스와 실제 guard/publication helper를 쓰라고 요구합니다.
  - 코드의 `inject_at`(1605)은 예외 주입이고, 계획 스스로 이를 process-death 증거가 아니라고 합니다.
- **위험:**
  - barrier를 걸려면 사실상 두 길뿐입니다. launcher를 우회해 hv2ref를 import하고 monkeypatch하거나, installed bytes를 변경해야 합니다.
  - 전자는 "같은 installed 호출 경로"가 아닙니다. 후자는 a580 무변경 전제와 충돌합니다.
  - 정지 지점이 code의 실제 publish 직후와 정확히 같다는 보장도 없습니다.
- **최소 수정:**
  - barrier 방식을 1개로 고정합니다.
  - 사용하는 경로가 installed launcher가 아니라면, 그 차이를 R-4 조건의 명시적 한계로 기록합니다.
  - 그 대신 H05 replay 자체는 반드시 installed `colvia work apply`로 수행한다고 적습니다.
  - barrier wrapper가 실제 프로젝트에서 import될 수 없음을 확인하는 방법을 명시합니다(경로나 hash 확인).
- **확인:**
  - 각 S 상태에서 fsync된 관측 직후 TERM/KILL을 보냅니다.
  - process group 부재, decision/selection/current 파일 상태, 원 bytes를 기록합니다.
  - installed launcher로 replay했을 때의 결과를 기록합니다.

### F-05 — 실제 대상에서 effective profile과 도구 노출을 재확인하는 oracle이 불충분
- **심각도:** Medium
- **분류:**
  - 착수 전 필요: oracle 정의.
  - 경험적 gate: enforcement 결과 자체.
- **근거:**
  - A 0039: H03은 "합성 대상만"입니다.
  - C 0159: "`config/read`, thread active profile, 실제 canary 거절을 함께 요구"한다고 하지만, 실제 프로필에 적용되는지 불명확합니다.
  - H: legacy `sandbox_mode`가 어느 layer에든 있으면 named default를 대체할 수 있습니다. profile 정의도 layer 사이에 누적됩니다.
  - F 0287: `config/read`의 cwd가 프로젝트 layer를 포함합니다. WORKER는 실제 대상의 checkout이므로, 프로젝트 `.codex` 설정이나 지침 파일이 합성과 다르게 로드될 수 있습니다. F 0143의 `instructionSources`가 이를 보여줍니다.
  - F 0135: `disabledPluginIds`는 "Does not yet filter plugin capabilities"입니다. 계획에는 plugin을 끄는 수단이 없고 탐지만 있습니다.
  - A 0067: 새 파일 생성 사례가 없습니다. narrative 등 일부 scope 파일은 신규일 가능성이 있습니다.
- **위험:**
  - 합성 대상의 H03 통과가 실제 경로, 실제 프로젝트 layer, 실제 신규 파일 생성에 그대로 적용된다고 오인할 수 있습니다.
  - control 쓰기 거부를 실제 control에 쓰기 시도해서 검사하면, 실패하지 않을 경우 실제 bytes가 변합니다.
- **최소 수정:** E07의 첫 모델 turn 전 정지 조건을 다음처럼 명시합니다.
  1. `config/read`를 `cwd=WORKER`, `includeLayers=true`로 호출해 확인합니다: 모든 layer에 legacy `sandbox_mode`가 없고, `colvia-u2-worker` 정의가 해시를 기록한 JSON과 정확히 같으며, `extends`가 없고, 예상 밖 `instructionSources`나 plugin도 없어야 합니다.
  2. 실제 프로필로 비파괴 canary를 수행합니다. canary 대상은 ARTIFACT 아래의 합성 파일, 또는 존재하지 않는 경로의 생성 거절로 합니다. 실제 control bytes를 바꿀 수 있는 쓰기 시도는 하지 않습니다.
  3. H03에 "file allowlist 아래 신규 파일 생성과 원자적 교체" 사례를 추가합니다.
- **확인:** 합성과 실제 각각의 layer 목록, 프로필 해시, canary deny code를 대조해 기록합니다.

### F-06 — runner 상한 의미와 고정 argv가 불일치하고, 알려진 error1의 처분이 미정
- **심각도:** Medium
- **분류:** 착수 전 필요 (단계 A 전)
- **근거:**
  - **상한 규칙과 argv 충돌:**
    - A 0049는 "단계·전체 잔여 중 작은 값"을 적용한다고 합니다.
    - A 0047은 runner가 "native timeout을 바꾸지 않는다"고 합니다.
    - 기존 runner(D 0301–0302, 0353)는 인자 SECONDS 하나만 씁니다.
    - E05/E06(A 0042–0043)은 각각 6300초가 고정이라 합이 12600초입니다. 이는 "누적 180분(10800초) 우선"과 맞지 않습니다.
  - **알려진 error1:**
    - A 0075와 G 0063은 원 693개 중 error1이 있다고 기록합니다.
    - D 0373–0375는 `successful`이 아니면 `stage_success=false`로 판정합니다.
    - 이 기존 오류가 E05/E06에서 다시 나올 때의 처분이 없습니다. 중지할지, 보정 횟수를 소모할지, 사전 선언된 기존 결함으로 분리할지 정해져 있지 않습니다.
  - **KILL 이후 처리:** D 0361은 KILL 후 대기가 타임아웃되면 예외로 끝납니다. 이 경우 completion.json이 남지 않습니다.
- **위험:**
  - 상한 위반이나 임의 해석이 생길 수 있습니다.
  - 알려진 오류로 인해 full pair가 항상 "실패"가 되어 불필요한 정지나 보정 소모가 생길 수 있습니다.
  - 반대로 그 오류를 은폐할 위험도 있습니다.
- **최소 수정:**
  - 외부 controller가 SECONDS를 `min(단계 상한, 누적 잔여 − cleanup)`으로 계산해 넘긴다고 명시하고, argv의 6300을 "상한"으로 표기합니다. runner의 timeout 의미는 그대로 둡니다.
  - error1의 정확한 ID와 예상 분류를 실행 전에 기록합니다. 판정 규칙은 "동일 ID·동일 분류면 기존 결함으로 별도 보고, 그 외 실패는 중지"로 둡니다. 이것을 PASS로 표기하지 않습니다.
  - KILL 후 미종료 상태도 completion 기록을 남기도록 합니다.
- **확인:**
  - E00 collection에서 701개와 error1 ID가 실재하는지 대조합니다.
  - runner의 변경 diff가 위 세 가지에 한정되는지 R1에서 확인합니다.

### F-07 — candidate commit 실행의 hook·identity·사후 검증이 불충분
- **심각도:** Medium
- **분류:** 착수 전 필요 (단계 C 전) / 단계 A에는 비차단
- **근거:**
  - C 0139: staged 상태를 비교한 뒤 commit하고, trailer만 다시 확인합니다.
  - A 0100: `--no-verify` 우회는 금지합니다.
  - 그러나 hook 경로(`core.hooksPath` 포함)의 사전 inventory가 없습니다. trusted Driver 권한으로 실행되는 hook의 환경(network, HOME, 전역 config)도 정해져 있지 않습니다. commit author/committer identity도 정해져 있지 않습니다.
- **위험:**
  - pre-commit이나 commit-msg hook이 index나 메시지를 바꿀 수 있습니다. 그러면 승인한 diff와 실제 commit이 달라집니다.
  - 프로젝트 코드가 Driver 권한으로 실행됩니다.
  - 그 결과 submit 시점에 whole-tree 불일치가 생깁니다(work.py 0504–0525).
- **최소 수정:**
  - commit 전에 hook 목록과 hash를 사람 승인 packet에 포함합니다.
  - commit 후 `HEAD^{tree}`, 전체 membership, mode, 메시지 bytes가 승인본과 정확히 같은지 검사합니다. 다르면 tag를 만들기 전에 중지합니다.
  - author/committer 값과 commit 환경 변수를 고정합니다.
- **확인:** 합성 저장소에서 hook이 수정하는 사례 1건을 정지 경로로 관측합니다. 이것은 기존 H06/H08 범위 안에 둘 수 있습니다.

### F-08 — intent required reference와 Work narrative의 위치·겹침 규칙이 미지정
- **심각도:** Medium
- **분류:** 착수 전 필요 (단계 B 전)
- **근거:**
  - GENERAL-WORK 0254: intent의 required documents/evidence는 worker diff와 겹칠 수 없습니다. 결과가 바꾼 required Work reference는 retained post blob으로 검사합니다.
  - GENERAL-WORK 0136: supervised iteration 시작 전에 계획을 기존 Work narrative에 기록해야 합니다.
  - 계획 C 0043은 narrative(`work/target-operations-work.md`)를 worker scope 5파일 안에 두고, 신규 작성으로 보입니다.
  - A 0098과 C 0104는 intent의 required reference 집합을 명시하지 않습니다. 27개 read 파일이 required reference인지 아닌지도 정해져 있지 않습니다.
- **위험:**
  - submit 단계에서 overlap 거절이 날 수 있습니다.
  - 시작 전 계획 기록 위치가 정해지지 않아 H07 resume의 근거 위치가 불명확해집니다.
- **최소 수정:** 비공개 묶음에 다음 두 가지를 명시합니다.
  - required reference 집합. 5개 scope와 겹치지 않아야 하며, 겹친다면 post blob으로 검사한다는 점을 함께 적습니다.
  - 시작 전 계획 기록 위치. worker narrative의 첫 편집인지, 다른 위치인지 정합니다.

  실제 값은 intent를 작성할 때 사람이 확인합니다.
- **확인:**
  - 합성 H06에 "required reference와 diff overlap 거절" 1건을 두거나, 기존 `test_bound_intent_input_overlap_is_refused`를 근거로 연결합니다.
  - 실제 draft에서 overlap이 없는지 정적으로 대조합니다.

---

## 경험적으로 남을 수 있는 항목 (b, 실행 전 입증 불요)
- named profile의 실제 enforcement: 파일 단위 read/write, 원자적 교체, 신규 파일, symlink/alias, system temp, network deny. H03과 실제 대상 canary로 판정합니다.
- `-c` override와 thread `config`에 의한 profile 정의의 실효성. builtin tool과 plugin inventory를 관측할 수 있는지.
- dynamic tool call의 thread/turn/call 결속 동작. `approvalPolicy=never`일 때 permission request가 실제로 발생하는지.
- `gpt-6-astra/xhigh`의 가용성, 과금, 무대체 여부.
- 실제 TERM/KILL barrier의 재현성과 S 상태별 replay 결과.
- 신규 8개 포함 collection이 701개와 일치하는지. 각 단계의 실측 시간.
- 대상 프로젝트 commit hook의 실제 동작.

## 실제 입력이 생긴 뒤에만 정해지는 값 (c, 현 단계의 빈칸 허용)
- intent draft와 selected revision ref, ticket, confirm token, request/operation ID.
- 결과 manifest, candidate OID, 최종 commit tree와 메시지 bytes.
- 복구 승인 packet의 실제 내용, focused-ids.json 실물, hook 목록의 실제 hash.

## 남은 Owner 결정
1. 이 source/target 묶음의 구현·host 실행 범위, 시간(385–535분, 상한 600분), 위 수정 반영 여부. 이번 R0-002로 새 실행 의미에 대한 검토가 충분한지, 아니면 추가 검토나 명시적 면제가 필요한지(WORKFLOW 0064).
2. 27개 비민감 파일 내용을 ChatGPT 모델 경로로 전달하는 범위(C 0046).
3. 실제 intent/grant 수락. 여기에는 required reference 집합(F-08)이 포함됩니다.
4. candidate commit 승인. 여기에는 retention tag 이름과 생성 시점(F-01), hook, identity, trailer(F-07)가 포함됩니다.
5. 실제 원 ticket 복구 승인. 실제 상태가 생겼을 때만 판단합니다.
6. 알려진 error1의 사전 처분 규칙(F-06).

## 한계
- **정적 검토:** packet만 읽은 정적 검토입니다. 명령, 테스트, schema export, host 실행은 하지 않았습니다. 실행 결과를 주장하지 않습니다.
- **packet 밖 근거:** `validate_manifest`의 ref 검사, CLI의 inject 지원 여부, `execution-test-selection.json`과 protocol-observation 원문, 공식 Permissions 문서 본문은 packet 밖입니다. 이 부분은 Driver 요약에 의존했습니다.
- **집중 세트 누락 ID:** focused 세트의 delegated 22개에 V22–V24가 빠져 있습니다. 이것이 의도(host 전용 의무)인지 누락인지는 판단할 수 없어 finding으로 올리지 않았습니다.
- **비식별화:** 실제 대상 식별정보는 기호로 치환되어 있습니다. 실제 경로, branch, hook, 프로젝트 config layer의 존재 여부는 확인하지 않았습니다.
- **U1 한계 유지:** 원 693개의 error1과 과거 runner 관측은 역사적 근거로만 다뤘습니다. U1 수락 기준이나 PASS로 재표기하지 않았습니다.
- **독립성 한계:** 새 세션과 고정 packet으로 검토했지만 망라적인 검토는 아닙니다. 이전 R0 검토자와 같은 계열 모델일 수 있습니다.
~~~~

### R0-002 Completion Checkpoint — 2026-10-21 10:08:14 UTC

이번 집중 검토·처분·검사의 활동시간은 약20.8분이다. 전용 Owner 대기 약37초는 제외하고 그 사이의 승인 기록 준비는 활동시간에 포함했다. reviewer228.730초와 병행 작업은 wall time으로 한 번만 셌다. 이전 checkpoint36.6분을 이어받아 누적 약57.4분, 제안600분의 잔여 약542.6분이다. 이 checkpoint 뒤 최종 기록 검사는 다음 재개 때 실제 시간으로 이어받는다. 예상385–535분은 유지하는 제안이며 실행 승인은 아니다.

원문·처분과 비공개 대상 보완안을 기록했고 두 문서의 검토 당시 prefix, 다른13개 입력, 응답 bytes를 확인했다. GFM 렌더의 코드 밖 literal emphasis는0, local link26개·anchor15개 오류는0이다. reviewer 원문의 빈 줄 trailing space1개는 원문 보존을 위해 그대로 두었으며 Driver 작성 부분은 whitespace 검사를 통과했다. 정적 코드 대조만 수행했고 제품 테스트·반례 재현·host/model 실행은 하지 않았다. 전달용 중복 자료는 원문 이관 검증 뒤 정리하며 compact metadata와 실제 착수 판단에 필요한 기존 작업물은 유지한다.

## Source A Selection — 2026-10-21

Owner가 R0-002 보완안과 source A 구현·검증을 승인했다. 이후 진행은 [FEAT-20261021-002](FEAT-20261021-002-u2-single-host-source.md)에서 관리하며 이 계획의 이전 검토 입력·원문은 보존한다. 실제 대상 실행과 제품 Git 작업은 별도 판단이다.
