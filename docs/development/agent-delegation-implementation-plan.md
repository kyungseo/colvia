# 일반 Work 위임 수락: M1/M2 통합 실행 계획

- 상태: M1/M2 구현·검증은 Owner 요청으로 일시 중단했다. 이번에는 계획 통합, 한국어 본문 보정, 후속 범위 제안, Claude 보완 R0와 필요한 계획 보정만 진행한다. 제품 코드·테스트·공통 규칙·배포 파일 변경은 재개하지 않는다.
- 기준일: 2026-10-16. 구현 시작점은 `d86bd1fd7754144e5c8538712724ae78571941bf`다. 당시 원격 main 확인은 역사 관측이며 현재 원격 상태를 뜻하지 않는다.
- 현행 실행 기준: 이 문서의 통합 본문 하나다. 승인·실행·실패·리뷰 처분·잔여 예산의 유일한 진행 기록은 [FEAT-20261016-001](FEAT-20261016-001-delegated-ordinary-acceptance.md)이다. 두 문서는 계획과 진행 기록이며 서로 다른 실행 기준이 아니다.
- 설계 입력: [채택된 M0](agent-delegation-m0-plan.md#owner-m0-adoption-and-next-planning-scope--2026-10-16), 채택 기록 추가 전 SHA-256 `41861df1ffd24423ceeeae2d4b4a64edebd2990cd528049ebfc01a523c0fb0bf`. 정확한 원문은 기존 비공개 작업 자료에 보존되어 있다.
- 역할: Codex는 Driver, Claude Code는 독립 Reviewer, 사람인 Owner는 범위·계약·결과의 결정자다. R0는 계획 검토, R1은 결과 검토이며 어느 쪽도 Owner 수락을 대신하지 않는다.
- 언어: 주 독자는 이 계획을 검토·승인하는 Owner다. 이번 명시적 요청에 따라 본문은 한국어로 작성한다. 코드·명령·경로·테스트 ID는 유지한다. 다른 저장소의 언어 정책을 이 저장소에 적용하거나 제품 전체 언어 정책을 변경한 것이 아니다.

<a id="owner-approved-continuation-amendment--2026-10-16"></a>

## 1. 원문, 승인과 현행 계획의 관계

| 기준 | 정확한 입력과 의미 |
| --- | --- |
| 마지막 초기 R0 검토본 | 계획 SHA-256 `a70c6bdc28e85a94f79492cf94ebb3ed93c51fffe552ed7a13656ddcee75497b`. Claude 최종 보정 검토 패킷 SHA-256 `ac6cb0163f7cd30d0ea2b3b2160dae3e31dceeeb4e4c9049e95f8382ed3e2517`, 세션 `02ce6077-259d-4e4c-b04e-c51623746c76`. 원문은 기존 `implementation-plan-review/R0-final-input.md`에 복구 가능하게 남아 있다. 당시 판정은 중대한 계획 지적 없음이며 실행 승인 자체는 아니었다. |
| Owner가 구현을 승인한 계획 | `implementation/approved-plan.md`, SHA-256 `746135dcfe76a112b2358f66478eb76b78fd98c331dcf7bb766169e19b31b002`. 초기 R0 뒤 retained slot, 합산 deadline, 이전 시도 근거 연결에 관한 세 비차단 보완과 상태 설명이 반영됐다. 이는 Driver 확인 사항이며 추가 Claude 검토를 받았다고 표시하지 않는다. |
| 한국어 통합 직전 영어 문서 | `implementation/implementation-plan-pre-ko.md`, SHA-256 `65f63ab01a58d89fe612a3ecefebb15e13cd2ebdea6de10ad31046078fa9c0a5`. 승인 원문, 실행 승인 pointer와 이후 재개 조건이 함께 있던 47,037-byte 원문이다. 번역 비교와 승인 계보 확인을 위해 원래 bytes를 보존한다. |
| 이번 통합본 | 의미를 유지한 한국어 보정과 아래의 이미 승인된 변경을 본문에 합쳤다. 이전 리뷰를 이 수정본 전체의 검증으로 재사용하지 않는다. 정확한 보완 R0 입력 SHA와 판정, 이후 계획 보정은 FEAT에 남긴다. |

기존 승인 중 유지할 것은 M0 정책, M1/M2 범위, V/C 의무, C03 repair 예외, 8시간 누적 상한과 실패·보정 제한, 검증 후 별도 결과 수락·활성화·Git·adopter 결정이다. 기존 재개 승인 원문은 `owner-continuation-approval.json`에 보존했다. 이후 승인된 변경은 구버전 전수 실행 의무 제거, 위험별 사례 선정, 새 기능 우선 순서, 일반/parent-O별 합산 상한 10,800초, retained 집중 상한 1,500초, 추가 리뷰 최대 4회, 저장·정리 조건이다. 이번 요청은 여기에 계획 본문의 한국어 정리와 후속 후보 진단을 더하며, 실제 제품 구현·테스트 재개에는 Owner의 다음 지시를 요구한다.

변경하지 않은 M0 정책과 기존 R0의 소스 근거는 그 당시 범위에서 계속 유효하다. 검증 범위·순서·시간 배분과 번역의 의미 보존은 이번 보완 R0 대상이다. 후속 후보 A·B와 실행기 구조 개선은 제안이며, 제품 계약 변경·상세 설계 승인·정식 등록·착수를 뜻하지 않는다. 오래된 전수 실행 의무와 7,200초 상한은 위 원문에서만 역사로 보존하며 현행 지시로 적용하지 않는다.

## 2. 목적, 범위와 완료 조건

한 번의 일반 isolated-worker 위임 수락을 Core와 모든 reader·설치 호환 경로까지 하나의 결과물로 구현한다. M0의 grant, 한 번 사용, revoke, 역사 판정과 host 경계를 유지한다. 이번 결과는 합성 근거로 검증한 Core 동작이다. 자동으로 일하는 agent, 인증된 backend, 실제 Owner 부담 감소는 후속 host 작업에서 확인한다.

검증 목적은 세 가지다.

1. 새 구현의 기능과 회귀를 검증한다.
2. 실제 구버전→새 버전 전환에서 기록 보존과 중단 복구를 검증한다.
3. 이번에 바꾼 실행기의 수집·판정·격리·종료·누적 시간 계산을 검증한다.

포함 범위는 schema-3 일반 intent grant, actor/권한 확인, 영속적인 한 번 사용 키 K, 선택된 revoke 장벽, 새 revision을 포함한 graph 문맥, 직접 library와 CLI 경로, shared/fallback reader, 일반 child readiness, 설치 window 전환, 기존 CRLF 예외, 복구, 문서와 테스트다. 완료하려면 M0의 V01–V21/V24/V25, 아래 C01–C16, 새 구현의 전체 일반 discovery와 전체 delegation factory를 normal·parent-O에서 통과해야 한다. 위험에 따라 선정한 구버전 호환 사례와 정확한 P/Q 설치·전환 검증, R1 지적 처분, 잔여 제한 보고도 필요하다.

V22/V23 실제 host 권한과 V26 판단 품질·Owner 노력 관측은 이번에 실행하지 않는다. 같은 결정의 합성 복구는 포함하지만 인증된 Owner 복구를 검증했다고 주장하지 않는다. M1(Core)과 M2(reader·설치 호환)는 한 결과물 안의 단계다. 각각 따로 설치 가능하거나 검증 완료라고 표시하지 않는다.

제외 범위는 CONT 구현, 운영 host engine, model worker 호출, 다중 프로젝트 조율, backend SDK, scheduler, 새 authority ledger, runtime attach, 공개 release/version 지정, 실제 adopter 변경, source commit/push/PR/merge다. 테스트용 Git commit과 worktree는 허용된 실행 경계 안의 합성 입력이다. 후보 A·B와 실행기 재설계를 완료 조건에 추가하지 않는다.

통합 순서는 `entry-1`(rank 5) → `delegation-1`(rank 6)이다. CONT의 우선순위·선정을 바꾸지 않는다. 재개 전 main·관련 active window 계획·schema 할당을 확인한다. CONT가 먼저 main에 도달하면 코드·fixture 실행 전에 정지하고 차이를 비교한다. 다른 통합 변경도 predecessor/schema/rank에 미친 영향을 확인한다. 비교 뒤 계획 변경이 필요하면 그 영향에 한정한 R0·Owner 결정을 받는다. 라벨을 적는 것만으로 window를 예약하거나 schema 번호를 자동 변경하지 않는다.

```text
이번: 현행 계획 통합·한국어 보정 → 보완 R0·계획 보정 → 결과 보고·대기
Owner 재개 지시
  → 승인된 최소 보정·실제 제어 변경 검토·필수 안전 확인
  → 새 Core의 작은 실행 → 실제 구→신 전환·복구
  → 전체 normal/parent-O·선정 구버전 사례·정확한 P/Q 설치 검증
  → Claude 최종 R1 → Owner 결과 수락
  → 별도 승인된 계약 활성화·Git·adopter 단계
```

## 3. 유지할 Core·schema·window 계약

### 3.1 형식과 읽기 호환성

| 대상 | 새 writer | reader와 보존 조건 |
| --- | --- | --- |
| 일반 intent draft | 정확한 non-null M0 grant가 있을 때만 schema 3, grant가 없으면 schema 1 | schema 1 일반·schema 2 composition 동작과 적법한 v2/v3 orphan 역사를 보존한다. schema 3에 composition을 넣지 않는다. |
| 나머지 intent·Work record | 기존 version/key를 유지하며 기존 ticket actor에 delegate를 표시한다. | 정확한 accepted draft와 grant를 graph에서 해석한다. 두 번째 권한·완료 record를 추가하지 않는다. |
| root format·release inventory·product binding | 기존 schema 1 | 검증한 release ref에 새 window literal을 쓰고 기존 membership과 root identity를 보존한다. |
| window | `delegation-1`, rank 6, entry-1과 같은 정확한 29개 managed path | launcher는 둘 다 `colvia`다. 과거 window는 파생 alias가 아닌 literal set으로 유지한다. 새 runtime module은 추가하지 않는다. |
| 새 init/update/rollback/repair/detach | action별 plan/receipt가 모두 schema 4인 쌍 | action과 정확한 정수 schema를 함께 판정한다. 과거 init/repair 1, switch 1/2, detach 1/2/3 의미를 보존한다. 혼합 쌍, bool version, unknown key/window와 허용되지 않은 action/version을 거부한다. |
| switch | 기존 schema-2 switch key, schema 4, `remove: []` | launcher 이름 변경·retirement가 없다. candidate는 delegation-1이다. predecessor entry-1은 update만, delegation-1은 update/rollback을 허용한다. |
| init/repair | 기존 action별 schema-1 key에 schema 4 | init은 delegation-1을 직접 만든다. 새 repair는 활성 delegation-1의 정확한 기록 bytes만 복구한다. |
| detach | 기존 schema-3 key에 schema 4 | 기존 규칙에 따라 현재 `colvia`와 정확한 managed release를 제거한다. project truth·충돌 파일·plain evidence는 보존한다. `schema == 3`만으로 launcher를 추정하지 않는다. |

모든 새 lifecycle action에 schema 4를 쓰는 목적은 init/repair를 포함해 old writer의 허용 schema와 구분하는 것이다. version 분기만으로 모든 구 writer가 차단된다고 가정하지 않는다. C06/C07에서 실제 old source·중단 prefix·이미 열린 프로세스·늦게 lock을 얻는 프로세스를 실행한다. lifecycle schema 변경 자체로 Work identity/revision version, ticket, binding 형식을 바꾸지 않는다.

최초 정적 관측에서 lifecycle detach는 3, 나머지 lifecycle에는 4가 없었고 intent draft는 1/2였다. 재개 시 실제 할당을 다시 확인한다. candidate 쓰기, schema2 composition, 검증한 launcher 제외, unchanged-CRLF 증명처럼 entry-1 동작을 상속해야 할 정확한 capability predicate에 delegation-1을 반영한다. 운영 current-write admission은 새 window를 요구하고, old fixture용 제한된 주입 경로는 별도로 유지한다.

### 3.2 위임 수락과 graph 문맥

검증된 grant를 해석하고 각 결정 당시의 graph prefix에서 권한을 판정하는 내부 helper를 사용한다. writer preflight는 이와 별개로 현재 accepted intent를 요구한다. read/publish/prepare/apply의 `work_graph` 호출에는 새로 만들 revision까지 포함한 검증된 intent/Work 문맥을 전달한다. 호출자 boolean을 신뢰하거나 과거 시각을 근거로 당시 current 상태를 만들어내지 않는다.

K는 정확한 home/Work/intent/draft identity다. 적법한 delegate accept가 영속화되면 all-pre cancellation이나 이후 revoke가 있어도 K는 소비된다. 일반 Owner accept는 K를 소비하지 않지만, 선택된 revoke는 selection ancestry를 통해 M0 장벽을 만든다. baseline-refresh rebind, 새 result, reselection으로 이 장벽을 우회할 수 없다. 새로 accepted된 grant draft는 적법한 rebind를 통해 새 K를 만들며, 지원 밖 역사는 거부한다. Delegate는 supersedes가 null인 accept만 할 수 있다. 다른 결정, intent acceptance, cancellation/recovery 권한은 Owner에게 남는다.

기존 `work_graph`의 baseline `work.py:816` guard는 prior outcome이 completed인 모든 새 revision을 rebind까지 포함해 거부한다. V11은 Owner accept 뒤 같은 draft의 baseline refresh/new result를 쓰기 전에 거부하는지 확인한다. accept 전 selection을 `expected_prior_selection`으로 다시 제시하는 우회도 확인한다. 이 경우 writer의 실제 current CAS(`WorkStore.publish`)와 graph의 selection-fork/exact-parent 검사(`work_graph`, baseline 863–900)가 거부해야 한다. 정적 trace에 각 호출 근거를 남긴다. 필요한 Owner revoke 이후에는 V17이 기존 old-K 장벽을 확인한다. 이는 기존 M0 판정이며 새 정책 선택이 아니다.

좁은 `_delegation_runtime` 검사는 정확히 `inventory_id == "delegation-1"`을 요구한다. 주입된 verifier에도 적용한다. 검증된 입력 또는 prospective graph에 schema-3 draft가 있으면 intent acceptance/reselection, Owner 결정, Work publication/rebind, delegated prepare/apply/recovery, candidate mutation과 schema-3 역사가 있는 intent의 schema-1 publication 등 모든 writer에서 확인한다. guard 안에서 영속화 직전에 다시 확인한다. old/missing/unknown-window double은 쓰기 전에 거부한다. 역사 읽기는 새 권한을 만들지 않고 유지한다. 운영 runtime은 설치 binding을 검증하며 이 helper가 호출자 인증을 대신하지 않는다. V25/C14에서 직접 호출과 CLI를 확인한다.

Delegate ID는 기존 `_RECORD_ID` ASCII 문법으로 full match한다. Owner 문자열은 바꾸거나 정규화하지 않는다. M0가 정한 정확한 equality와 ASCII-only case collision을 거부한다. Grant scope는 revision의 canonical scope set과 같고 manifest 변경은 그 부분집합이어야 한다. Composition parent는 위임할 수 없다. 적법하게 위임 수락된 일반 child는 기존 required-child 조건을 충족할 수 있으며 실제 delegate/grant를 표시한다. Parent 수락은 사람에게 남는다.

## 4. 실제 전환, 복구와 되돌리기

첫 전환은 정확히 감사한 entry-1 release `product-release-2216a2634eb3fa5d6a8bfa7c`, SHA-256 `2216a2634eb3fa5d6a8bfa7c7d4847b29fb2443ba7b367156c15b15ddb5a17e0` 또는 완결된 같은 delegation-1 binding만 받는다. 이 entry-1 identity는 2026-10-16 d86의 변경되지 않은 payload에서 계산했다. 다른 entry-1 release 추가는 별도 검토할 admission 변경이다. 더 오래된 window는 이 작업 밖에서 이미 지원되는 정확한 entry-1 전환을 먼저 사용한다.

Pending intent/Work와 관측 가능한 pending lifecycle, 손상된 역사, 지원 밖 old truth, unknown inventory, 누락된 exact release evidence는 update를 막는다. Entry-1 home의 미수락 schema-3 draft도 지원 밖 입력이며 자동 upgrade 근거가 아니다. 예외는 이미 승인된 C03 repair 종료 구간이다. Repair 완료 receipt는 외부 backup에만 있다. 마지막 target 교체 뒤 외부 receipt를 쓰기 전에는 target만 보고 미완료 repair를 알아낼 수 없다. 이때 전환을 허용하되 repair 완료라고 표시하지 않는다. 운영자는 전환 전에 repair 완료를 마치거나 명시적으로 포기하고 backup을 보존한다. 전환 후 old repair recovery는 target과 backup에 새 쓰기 없이 거부해야 한다. 마지막 교체 전 target 자체가 미완료·손상된 cutpoint는 그 관측된 상태를 이유로 거부하며, 외부 pending repair를 발견했다고 주장하지 않는다. Backup과 원본 bytes의 보존을 확인한다. 새 marker·registry를 추가하지 않으며 다른 pending 거부는 유지한다.

첫 영속 receipt 전 기존 writer guard 아래에서 old product history와 모든 project authority object를 shared reader로 검증한다. 선택되지 않은/orphan draft와 child도 포함한다. 정확한 binding/truth를 관측하고 영속화 직전에 다시 비교한다. 전환은 record migration, grant 삭제, intent 수락이나 selection 합성을 하지 않는다. Project bytes/mode, Git ref/index를 보존한다. Launcher는 같은 경로의 bytes만 바뀌므로 snapshot/baseline 제외는 검증한 window를 따라야 한다. 진행 중 worker의 retained Git tree는 launcher bytes도 검증하므로, 전환 후 기존 결과가 자동으로 수락 가능하다고 가정하지 않는다. 필요한 control Git 통합·명시적 rebind·resubmission 경로와 거부를 C02/C15에서 D2의 전환·drift/replay 의무를 직접 증명하고, C09의 P/Q record 호환과 C14의 snapshot/capability 상속도 각각 확인한다.

| Prefix | 허용 상태와 복구 |
| --- | --- |
| T0: 새 receipt 없음 | Admission 실패는 authority/managed target bytes를 쓰지 않는다. Scratch/lock은 기존 계약을 따른다. 정확한 old source는 새 전환 전에 적법한 old operation을 끝낼 수 있다. |
| T1: schema-4 receipt 영속, binding은 old | 새 window로의 일방향 전환이 시작된다. 모든 old writer family는 새 product/authority 쓰기 전에 거부한다. 정확한 새 operation/source의 forward recovery만 허용하며 old-window rollback은 막는다. |
| T2: candidate staging/release 일부 공개 | 허용된 정확한 prefix를 보존한다. 검증한 exact candidate source로만 누락된 member를 완성한다. Torn/foreign bytes, 잘못된 mode, unsafe path는 추측 복구로 덮어쓰지 않는다. |
| T3: 새 `colvia` 교체, binding은 old | 독립된 신뢰 가능한 exact new source로 복구한다. 설치 launcher 성공이나 임의 old-source repair를 가정하지 않는다. `hv2` retirement 단계는 없다. |
| T4: 새 binding 교체, final sync 전 | 정확한 replay가 필요한 directory/file sync와 모든 기록 ref 검증을 한다. 실패·unavailable을 그대로 알린다. |
| T5: 완료 | 같은 결정 replay는 identity를 보존한다. 역사 replay로 old selection/binding을 현재로 승격하지 않는다. 이후 currentness는 별도 관측이다. |

T1–T5는 의미상 중단 지점이며 임의 syscall offset이 아니다. 실행 전 실제 publication syscall 각각을 versioned prefix oracle에 연결하고 before/after/partial-write/sync-error 사례를 정한다. 기존 binding atomic replace와 receipt-bound recovery를 재사용하고 저장 protocol을 재설계하지 않는다. 기존 retired-entry collision 보존도 포함한다. Exact new source를 잃으면 recovery는 unavailable이며 old writer로 돌아갈 권한이 생기지 않는다.

Old pending operation은 전환 전에 정확한 retained old source로 끝낸다. 새 reader가 역사를 읽을 수 있어도 old-operation writer가 되지는 않는다. T1 이후 old source는 과거 완료 operation replay도 현재 home의 지원 밖 전환 때문에 거부해야 한다. 새 reader의 역사 조회는 current authority를 바꾸지 않는다. 새 schema-4 pending init/repair/detach는 exact new source만 처리한다. 새 repair/detach는 entry-1 home을 거부한다. Entry-1 home의 repair/detach는 정확한 retained source로 수행한다. Fresh init에는 prior binding이 없으므로 old init이 새 receipt/prefix를 덮어쓰지 않는지 별도로 증명한다. Repair/detach의 collision·unknown path·managed bytes 규칙은 유지한다. Detach 완료는 과거 window rollback이 아니며 자동 reattach는 없다.

P와 Q는 모두 완전한 delegation 계약을 구현한 독립 포장 artifact다. Q에서 만든 schema-3 draft, accepted grant, delegated/cancelled/revoked 결정, 일반/parent record, candidate note를 실제 rollback 후 P에서 읽어야 한다. P를 entry-1 artifact의 라벨만 바꿔 만들지 않는다. 첫 P는 이번 candidate이며 Q는 같은 의미 계약을 유지한 검토된 배포 prose 차이만 갖는다. Inventory/digest 비교와 실제 update/rollback을 실행한다. 같은 실행 코드로 미래의 임의 의미 차이까지 증명했다고 주장하지 않는다. P가 이해하지 못하는 Q 동작에는 다른 semantic window가 필요하다.

## 5. 변경 대상과 남은 R1 보정

| 파일 | 필요한 변경 |
| --- | --- |
| `src/hv2ref/intent.py`, `work.py` | Schema·역사/prospective validation, grant writer admission, 같은 결정 복구 |
| `view.py`, `candidates.py`, `umbrella.py` | Shared/fallback 일치, actor/grant 표시, readiness와 새 window admission |
| `product.py`, `workspace.py`, `cli.py`, root `colvia` | Literal window ref, lifecycle action/version 분기, old-writer 거부, source/installed 진입 |
| `tests/test_delegated_acceptance.py`, `tests/test_delegation_window_transition.py` | Core 사례와 명시적 artifact/fault factory |
| 기존 intent/Work/view/candidate/umbrella/product/worker/checkout/runtime test와 `tests/fixtures/*plain_auditor.py` | 영향받은 assertion 추가, 기존 동작과 plain auditor 제한 보존 |
| `docs/development/verification/binding-permissions-controls/`의 기존 `common.py`, `controller.py`, `runner.py`, `canary.py`, `test.sb`, `acquire.sb`와 현재 작성된 `campaign.py`, `calibration.py`, `selfcheck.py`, `delegation_observer.py` | 새 factory/input 선택과 최소 admission·시간·종료·공간 제어. 새 runtime framework가 아니며 기존 observer/factory 근거를 보존한다. |
| `AGENTS.md`, `CLAUDE.md`, managed adapter, `README.md`, `PRODUCT-CAPABILITIES.json`, managed `docs/*.md` 11개 | 기존 M1/M2 위임 예외·window·복구·근거 제한에 필요한 절만 보정한다. 후보 A·B의 공통 규칙 보강은 이 권한에 포함하지 않는다. |
| DR-0005, 이름이 명시된 DR-0003 amendment, 기존 개발 기록/index | 계약·작업·활성화 기록. 과거 수락 원문을 보존한다. |

경로가 생략된 module은 `src/hv2ref/` 아래다. 모든 caller/plain reader를 확인하고 `workspace.py` release-ref validation을 빠뜨리지 않는다. 일괄 refactor나 새 module/registry는 금지한다. 추가로 영향받는 파일은 이유를 기존 기록에 남기고, 새 기능·정책은 Owner 범위 결정을 받는다. 이번 정리 단계에서는 이 표의 구현 변경을 실행하지 않는다.

기존 R1의 실제 보정과 코드로 해소한 의심은 다음처럼 구분한다. 자세한 원문과 처분은 기존 `R1-final-*` 근거를 유지한다.

| 구분 | 계획에 반영할 내용 |
| --- | --- |
| D1: 잘못된 old self-update fixture | 별도 prose-only old-Q를 만들어 실제로 다른 old release 간 update/rollback을 준비한다. 최종 전환 predecessor는 정확한 d86으로 유지하며 admission identity를 완화하지 않는다. |
| D2: 진행 중 Work 전환 증명 부족 | Local/parent snapshot, worker retained launcher, 명시적 rebind/resubmission의 실제 경로·거부를 분리한다. 문서나 정적 trace를 runtime PASS로 표시하지 않는다. |
| D4·N4·admission 기록 | Darwin EPERM은 group absence가 아니다. 기존 cleanup reserve 안에서 bounded 재관측과 reap을 하고 unknown이면 중단한다. Lane별 실패·영향 범위·이전 근거 연결·누적 시간을 검증한다. 반복 admission 실패도 기존 증거를 덮지 않고 시간을 차감한다. |
| D8: helper 호환성의 미확인 범위 | 확인한 lifecycle keyword 일치와 OLD의 다른 snapshot/launcher API를 구별한다. Action→source→CLI/library/injection 이름을 실제 도달 경로별로 확인하고 Q/old-Q까지 포함한다. 모든 OLD 경로가 이미 잘못됐다고 단정하지 않는다. |
| D10: expectation 이유 부족 | 변경된 76개 hunk 각각에 계약상 이유를 남긴다. 운영 writer 변경과 역사 reader 상속을 구별하고 entry-1·schema3 detach pairing 등 지원되는 기존 assertion을 복원/추가한다. |
| D11: token 거부와 권한 거부 혼동 | Token 변조 검사는 유지하되, 유효하게 재계산한 token으로 unauthorized actor/binding과 실제 writer의 K 중복 소비를 검사한다. Request ID 변경 자체는 첫 사용 전 적법할 수 있으므로 그것만을 위반으로 만들지 않는다. 각 거부 원인과 무변경을 확인한다. |
| D12: 시간 산정 | Owner가 승인한 선정 kind별 최대 관측 비용·개수 산정으로 반영한다. Unknown kind는 제한된 측정 전 full admission 불가다. |
| D3/D5/D6/D7/D9: 코드로 반박한 의심 | Rollback `release_ref`, 실제 `work_graph` 문맥 전달, `require_current=False` 검증 경로, 명시적 `LOCK_UN`, 기존 auditor field를 Driver가 소스에서 정적으로 확인해 반박했다. Reviewer가 독립 확인하거나 실행으로 입증한 사실이라는 뜻은 아니다. 코드 수정의 근거로 재사용하지 않으며 관련 실행 의무는 유지한다. |
| 미완료 V/C와 표시 보정 | C03/C05–C08/C10–C12/C14/C16 및 V 하위 사례, Q와 native observer를 완성한다. 무관한 capability JSON key 순서 변경을 제거하고 새 관측 날짜를 과거 검증과 구별한다. |

## 6. 실행 계약

### 6.1 환경, 격리와 사전 확인

Native macOS arm64, GIL-enabled final CPython 3.14.7을 사용한다. 2026-10-16 정적 관측은 macOS 27.0.1, executable SHA-256 `87d4df53fd91304be5bac391fb204643c36b7df2023c04a0953bcbc7d4fdf634`였다. 정확한 absolute runtime/Git 경로·binary/launcher hash·OS build는 비공개 invocation에 결속한다. Runtime 설치·dependency update·network test는 이번 범위가 아니다. Runtime/build가 달라졌으면 실행을 중단하고 근거 영향을 판정한다. 임의로 runtime을 교체하지 않는다.

기존 제한된 native controller와 준비된 실행 경로를 사용한다. 제한 없는 shell runner나 unsandboxed fallback을 사용하지 않는다. 승인된 영구 artifact root의 새 task-owned slot, 등록된 source worktree, 읽기 전용 controls/source/retained input, 실행별 쓰기 가능한 합성 WORK를 사용한다. Parent log/result는 child WORK 밖에 둔다. Old fixture는 기존 Git object에서만 재구성하고 adopter home은 사용하지 않는다. Process별 temp/home/config는 WORK 안에 두며 global 환경은 바꾸지 않는다.

`test.sb`의 default deny, network deny, user-config/keychain deny, source/control/parent-evidence 쓰기 금지, 기존 literal `/dev/fd` 읽기는 유지한다. 허용된 platform file·host metadata는 보이므로 이것은 M3 agent-host 기밀성 증명이 아니다. 읽기 전용 `PREDECESSOR`, `ARTIFACTS`는 정확한 d86 source와 고정 P/Q store 하위 경로만 허용한다. Parent가 child admission 전에 non-symlink 경로·hash를 재구성해 고정하고 다른 slot의 WORK를 가리키지 않게 한다. 실제 ancestor literal을 모두 나열하며 과거 9개라는 수치를 가정하거나 ancestor 재귀 읽기를 허용하지 않는다.

Retained lane에서는 `PREDECESSOR=SOURCE`, `ARTIFACTS=OLD`이며 이미 읽을 수 있는 root다. Current lane은 별도 exact predecessor/artifact root를 결속한다. 새 write/network/credential 권한은 없다. 테스트 전에 실제 WORK-write 성공과 source/control/input/parent/sibling/outside/predecessor/artifact/fake-secret/network 접근 거부를 확인한다. Sentinel bytes/mode와 child interpreter identity도 확인한다. Canary 실패는 제품 실행을 막는다.

### 6.2 두 버전의 수집과 실행

Retained input은 기존 schema-3/phase-entry와 context schema 1을 유지한다. Current input은 strict schema 4/phase `delegation`이며 exact source/control/runtime/tool identity, ordered selection, 기존 역사 OLD와 정확한 entry-1 d86, P/Q ref를 가진다. Unknown key, 누락 ref, hash 변경은 실행 전에 거부한다. 이 schema 4는 비공개 실행기 input version이며 lifecycle schema 4와 별개다.

Current interpreter는 새 source의 전체 ordinary discovery와 `build_delegation_suite`를 수집하고 normal·parent-O에서 전부 실행한다. Retained interpreter는 SOURCE와 `candidate_source`를 d86으로 고정하여 원래 OLD, observer, `baseline-inputs.json`, `prefix-oracle.json`과 `build_entry_suite`를 사용한다. 정확한 전체 collection에서 위험별로 선정한 ID만 freshly normal·parent-O에서 실행한다. 6,513개 전수는 완료 조건이 아니며, 제외된 항목은 미검증이다. 209개는 후보일 뿐 목표 개수가 아니다.

새 source의 `tests/test_entry_window_transition.py`는 d86과 byte-identical하게 유지한다. Old factory는 pinned d86 interpreter에서만 실행하며 current ordinary discovery에 import된 선언을 factory 실행으로 세지 않는다. Retained 결과는 old compatibility와 변경된 controls의 근거이며 새 제품 PASS가 아니다. 두 lane의 module import 경로를 source에 결속하고 current `hv2ref`를 retained `sys.modules`에 섞지 않는다. `candidate_source`만 바꾸는 방식은 허용하지 않는다. 공통 control/policy는 검토한 동일 identity를 사용하되 context·EXEC·collection digest는 분리한다.

수집은 occurrence를 보존하고 예상 밖 중복·누락·factory 부재·collection error를 실패로 처리한다. Lane/source/default 또는 factory origin, selected/executed/unstarted/unfinished ID, duration, 구조화된 subtest identity/result를 남긴다. `DelegationWindowTests`는 `build_delegation_suite` 안에서만 만들며 default discovery에는 나타나지 않아야 한다. Import 시 실행이나 수집 중 test source rewriting은 없다. Current window/schema expectation inventory는 unchanged·retained d86·계약 이유가 있는 변경으로 구별한다. 안전 assertion을 지우거나 약화해 PASS를 만들지 않는다. Authority verdict를 주입하거나 subprocess timeout을 교체하지 않는다.

기존 기록의 위험 표를 다음 기준으로 구체화하고, 정확한 ID와 각 선정 이유를 실행 전에 고정한다. 전체 old factory의 미관측 비용 산정이 새 기능의 선행 과제가 되어서는 안 된다.

| 실행기 변경 → 가능한 오류 | 직접 확인 | 실제 구버전 사례를 쓰는 이유 |
| --- | --- | --- |
| 수집/factory → 누락·중복·import side effect | Collection/membership/empty-overlap/constructor/import-purity 사례와 자체 점검 | 실제 retained factory가 같은 계약으로 생성되는지 확인한다. |
| Lane/context → 버전 혼입·잘못된 OLD/명령 | Source/context mismatch 거부, 실제 readonly context·command identity, canary | 작은 old 성공 경로로 실제 product import를 확인한다. |
| 완료/seal → 실패·skip·미완료를 PASS로 오판 | 실제 synthetic child의 success/failure/error/subtest failfast, counts·receipt/seal 변조 거부 | 대량의 old product fault 조합 대신 실행기 자체의 종료·판정 경로를 확인한다. |
| 시간/보정/reuse → 합산 reset·실패 누락·중복 차감·영향 lane 재사용 | Deterministic parent timing/accounting mock, 기존 1,555.021초 carry-forward, exclusive admission·prior link 검사 | 기존 r00 실패를 유지한 실제 입력 연결을 확인한다. |
| Sandbox → 경계 밖 쓰기·secret/network 접근 | Fresh positive/negative canary와 input identity | Representative old operation도 같은 제한 안에서 실행되는지 확인한다. |
| 종료/공간 → process 잔존·EPERM 오판·로그 유실 | Bounded real synthetic termination, exact PGID 관측, timeout/reap/unknown/storage-threshold 자체 점검 | 작은 old interruption/recovery·refusal 경로로 실제 subprocess와 복구를 확인한다. |

변경되지 않은 observer의 모든 fault permutation이나 무관한 old product 조합은 역사적 전수 근거가 없다는 이유만으로 포함하지 않는다. 선정 이유 없이 반복하지 않되, 필요한 안전 사례를 개수나 시간 목표 때문에 누락하지 않는다. R0에 제출할 구체 선정은 [FEAT의 retained 사례 선정](FEAT-20261016-001-delegated-ordinary-acceptance.md#retained-selection-for-supplemental-r0)에 명시했다. 그 선정은 개수 목표가 아니며 review·실제 control 영향으로 필요한 보정만 반영한다. Exact selected ID·kind·selection hash를 기존 invocation/collection에 결속하고 별도 장부·framework를 만들지 않는다.

### 6.3 허용 명령, slot과 근거 재사용

정확한 경로는 invocation에 고정한다. 승인된 기본 명령은 다음과 같으며 no-site bootstrap 등 실제 launch 구체화는 검토된 control identity에 결속한다.

```text
<PYTHON> -I -B <CONTROLS>/controller.py <INPUT.json> <INPUT_SHA256> <MODE> <SLOT>
```

| Lane / invocation phase | 이 campaign에서 사용할 mode와 slot, lane 내부 의존 순서 |
| --- | --- |
| Current / delegation | `acquire base`, `canary base`, `collect final`, `smoke base`, `focused core`, `focused transition`, `complete-normal final`, `complete-parent-O final`, `artifact final` |
| Retained / base | `acquire base`, `canary base`, `collect base`, `smoke base` |
| Retained / entry | `collect final`, `focused p1`, `complete-normal final`, `complete-parent-O final` |

Retained entry에는 유효한 base acquire/canary/smoke가 필요하다. 기존 `ENTRY_RUN_NAMES`가 retained entry path의 기준이며 `<lane EXEC>/runs/<mode>-<slot>/work`와 불일치하면 admission을 중단한다. 기존 slot 이름을 바꾸거나 `focused-p1-controls`의 특수 용도를 다른 실행에 쓰지 않는다. 각 lane은 별도 EXEC를 가지며 `acquire base`는 제한된 acquisition policy 안에서 exact fixture를 복원한다. Network/source mutation은 없다. Retained base smoke는 기존 `base-seed-ids.json`의 20건으로 runtime/old-contract/CRLF/process 안전 선행조건을 확인한다. `controller.preflight`의 retained entry 선행조건이므로 유지하며 6,513건 전수를 되살리는 것이 아니다. Current Core와 실제 전환·복구 뒤, pair admission 전에 retained base smoke와 `focused p1`을 수행한다. `focused p1`은 선정 17건의 kind별 비용을 제한 안에서 관측하기 위한 1회 측정이며 normal/O compatibility 실행을 대체하지 않는다. 같은 ID의 반복은 이 비용 측정과 각 mode의 호환 판정을 구분하기 위해서만 한다.

기존 `ENTRY_MODE_SLOTS`/`ENTRY_RUN_NAMES`의 보존 범위는 collect의 `p1-controls/p1/p1-correction/p2/p2-correction/p3/p3-correction/final`, focused의 `p1-controls/p1/p2/p3/correction`, complete-normal/complete-parent-O/artifact의 `final`이다. 위 campaign 표는 그중 사용할 부분집합이며 나머지 slot을 새 실행 의무로 만들지 않는다. `focused p1-controls`는 기존 control-stage 전용 의미를 보존하되 이번 17건 배치에는 사용하지 않는다.

Driver의 정적 추적에서 `verification_stage`는 factory의 분류값이며 `runner.main`은 `focused-p1-controls`에서만 control ID로 선택을 제한한다. 일반 `focused p1`과 complete에는 stage별 skip 조건이 없다. 17건 전부를 `focused p1`(normal 측정), `complete-normal final`, `complete-parent-O final`에 배치한다. 다만 현행 runner는 complete에서 selection을 거부하므로 retained-only selected complete 보정은 재개 후 구현·집중 검토해야 한다. Current complete의 전체 실행 조건은 유지한다. 정확한 ID→stage→slot/mode 대응은 FEAT에 두고, 실제 control 검토 전에 수정된 factory/runner 경로와 invocation 결속을 다시 확인한다. Stage 때문에 skip·누락되거나 실행 배치가 달라지면 PASS로 세지 않고 대체 slot·이유를 기존 기록에 명시한다.

Exact lane/source/control/phase별 final collection은 focused/full 실행 전에 한 번 만들고 digest를 재사용한다. Retained base와 entry collection은 다르다. 같은 입력의 결과 이름만 바꾸려고 재수집하지 않는다. 변경된 input에는 새 attempt root에서 영향받은 lane의 admission/collection을 반복한다. `r00`는 최초, `r01`·`r02`는 보정이며 매번 존재하지 않는 task-owned root를 사용한다. 이름 변경으로 누적 시간·실패·보정 횟수가 초기화되지 않는다.

Schema-4 invocation은 영향 없는 이전 attempt의 lane evidence를 exact input/result digest로 연결할 수 있다. Parent는 source, controls, runtime, collection, coverage와 원래 completion을 확인하고 원문 입력과 필수 receipt가 복구 가능해야 한다. Shared control/policy/runtime 변경은 양쪽 lane의 해당 근거를 무효화한다. Parent의 이전 근거 연결이 child의 cross-root 읽기 권한을 넓히지 않는다. Lane별 failure/affected phase·필수 prerequisite·수정 시도 한도를 구별해 r00의 실패 때문에 무관한 current 최초 실행이 숨겨지거나, prerequisite 때문에 한도가 재설정되지 않게 한다. 다음 r01 보정 묶음의 첫 실제 실행(필수 prerequisite 포함)을 시작할 때 global correction 1/2를 소비한다. 실패한 retained focused phase의 보정 1회와 필수 acquire/canary/collection/smoke 재수행을 묶되 prerequisite마다 추가 보정으로 세지 않는다. r01에서 처음 실행되는 current phase는 최초 실행이며 별도의 correction을 소비하지 않는다. Admission-only 거부는 시간을 차감하되 실행 slot·보정 횟수는 소비하지 않는다. 후속 r02는 남은 global 1회와 영향받은 phase별 최대 1회 조건을 모두 만족해야 한다. 실제 제어 코드 검토와 N4 자체 점검으로 이 계산을 r01 admission 전에 확인한다.

`complete-parent-O`는 test interpreter에 `-O`를 주고 controller는 optimized로 실행하지 않는다. 모든 interpreter는 `-B`, child environment는 `PYTHONDONTWRITEBYTECODE=1`을 쓴다. Installed launcher/auditor child는 실제 optimization flag를 유지하고 별도로 보고한다. 의미상 normal 명령은 `PYTHONPATH=src python3 -B -m unittest discover -s tests -v`에 current factory를 더한 것이고 parent-O는 `-B -O`다. 이는 의미 설명이며 unsandboxed fallback 실행 허가가 아니다. 기존 isolated Python·명시적 source/tests 경로를 사용한다.

이번 보완 R0는 변경된 계획을 검토한다. 이후 실제 수정될 controls diff, canary, invocation template, oracle은 제품 실행 전에 기존의 집중 Claude 검토 조건을 충족해야 한다. 이미 검토한 동일 bytes와 근거는 재사용하고 변경된 부분과 영향만 확인한다. 실제 수정 코드를 이번 계획 R0가 미리 검토했다고 표시하지 않는다. N4 accounting·monotonic 합산 deadline·D4 EPERM unknown 처리와 factory 포함·normal/O·실패/partial·exclusive slot·cleanup·storage 자체 점검은 r01 admission 전에 수행한다. Control delta→선정 ID/자체 점검 대응표를 FEAT에 유지하고 실제 수정 diff를 집중 검토할 때 갱신한다. 과거 predecessor PASS는 변경된 controls의 자격을 보증하지 않는다. 이는 이미 승인된 범위 내 기술 확인이며 반복 Owner 승인 단계가 아니다.

### 6.4 Core와 전환 검증표

`DelegatedAcceptanceTests`의 아래 method는 작성 대상/기존 초안이며 현재 구현에서 실행 완료된 목록이 아니다. 추가 하위 사례에는 frozen collection에서 명시적인 ID를 부여한다.

| ID | `test_` 뒤 method suffix | 확인할 결과 |
| --- | --- | --- |
| V01–V05 | `v01_owner_history`, `v02_exact_grant`, `v03_actor_home_work`, `v04_scope_mode`, `v05_actions` | 적법한 결과 또는 거부 시 bytes/mode/ref/index 보존 |
| V06–V11 | `v06_current_vs_history`, `v07_evidence`, `v08_prepare_apply_drift`, `v09_duplicate_k`, `v10_reselection`, `v11_reactivation` | 정확한 currentness·evidence·K 전이, timestamp 권한 금지 |
| V12–V16 | `v12_all_pre_cancel`, `v13_mixed_recovery`, `v14_late_cutpoints`, `v15_unavailable_drift`, `v16_pending_mutation` | 허용한 exact durable prefix, 같은 결정/actor 복구, 추가 쓰기 없음 |
| V17–V21 | `v17_revoke_barrier`, `v18_concurrent_requests`, `v19_prospective_context`, `v20_shared_readers`, `v21_child_parent` | Selection ancestry, 최대 한 번 사용, 실제 caller 경로, human parent |
| V25 | `v25_malformed_grant` | Exact schema/key/type/ASCII label, 모든 관련 경로에서 unsupported 표시 |

Owner/delegate cancellation·revoke, shared intent/Work 불일치, non-ASCII Owner, ASCII case collision, v1/v2/v3 공존, target revision schema1과 schema2 ancestry, 모든 grant field, historical prefix와 current authority를 하위 사례로 다룬다. Method 결과와 subtest identity를 함께 기록하며 실패·skip 하위 사례가 있는 method를 PASS로 세지 않는다. V02/V12/V13에는 pre/post bytes가 다른 tracked text 두 경로를 사용한다. 한 경로만 바뀐 mixed state를 실제로 구별한다. 같은 Work의 요청은 직렬화하고 concurrency에는 bounded barrier를 사용하며 sleep으로 순서를 추정하지 않는다.

`DelegationWindowTests`의 전체 method 이름은 `test_cNN_`과 아래 suffix를 합친 것이다. 이 전체 factory는 current complete normal/O와 artifact 실행의 필수 대상이며 V24는 이 표 전체를 뜻한다.

| ID / suffix | 필수 실행 |
| --- | --- |
| C01 `fresh_git_non_git` | Fresh Git/non-Git init, root/binding identity, grant 없는 일반 동작 |
| C02 `entry_transition` | 실제 entry-1→new update, 모든 truth preflight, 정확한 project bytes/mode/ref/index 보존 |
| C03 `pending_admission` | Pending intent/Work와 lifecycle별 거부, exact old source로 old operation 완료. 위에서 승인된 repair-tail 예외·backup 보존·전환 후 old recovery 무변경 거부를 포함한다. |
| C04 `draft_before_acceptance` | Selection/acceptance 전 new draft가 있을 때 old source가 쓰기 없이 거부 |
| C05 `old_window_rollback` | T1 이후 새 draft 전에도 모든 earlier window rollback 거부 |
| C06 `old_writer_prefixes` | T1–T5와 schema4 fresh-init prefix에서 old installed/source writer family 모두 확인 |
| C07 `late_lock_processes` | New lock 전에 시작한 실제 old process가 대기하고, 공개 후 lock을 얻어 각 writer family에서 거부 |
| C08 `transition_cutpoints` | Receipt/release/launcher/binding prefix, short/zero/torn write, sync failure/unavailable, neither/pre/post/mode drift |
| C09 `same_window_p_q` | Q가 만든 draft/decision/cancel/revoke/parent/candidate truth를 실제 rollback 후 P에서 확인 |
| C10 `repair_detach` | 새 repair/detach prefix·replay, authority 보존, missing source, collision, unknown managed member |
| C11 `historical_pairs` | 모든 역사 action/schema 쌍의 읽기, 모든 mixed/unknown/bool 쌍의 명시적 거부 |
| C12 `runtime_entries` | Source·installed·independent-source status/view/lifecycle, direct library, fallback reader |
| C13 `plain_auditors` | 독립 stdlib intent/product reader의 plain evidence 보존. Full Work/grant 권한 판단을 구현했다고 주장하지 않는다. |
| C14 `capability_inheritance` | 실제 candidate/schema2 child/CRLF 증명과 검증한 launcher 제외 동작 상속 |
| C15 `truth_drift_replay` | Admission/replay truth 변화, 역사 replay의 current 덮어쓰기 금지, 새 receipt 뒤 old operation 거부 |
| C16 `artifact_inventory` | 정확한 29-path inventory/hash, launcher allowlist, 설치 manual/adapter, secret sentinel, 두 Python mode |

CLI operation/parameter는 실제 parser에서 복사하며 추측하지 않는다. 새 38개 method 이름은 전체 회귀 개수를 대신하지 않는다. Current ordinary 전체와 delegation factory, 위험으로 선정한 retained 사례는 구분해 보고한다.

모든 window/schema literal과 writer entry의 정적 inventory를 inherit/new-only/historical-only로 유지한다. 필수 근거는 `product.py` planning-directory admission과 repair/runtime/init/switch/detach validator, `workspace.py` release ref/init pairing, `work.py` runtime/umbrella/launcher/CRLF predicate, candidate/intent writer gate다. Baseline `product.py:1784/1802/1835` detach action/version/window mapping과 validated plan에서 receipt version을 얻는 `_init_binding_receipt`를 확인한다. C11은 delegation-1을 담은 schema1 init/schema2 switch, old candidate window를 담은 schema4, mixed receipt와 불법 action/version을 거부해야 한다.

최초 fixture 실행 전에 retained entry-1의 intent/candidate/Work/lifecycle writer 각각을 guard acquisition에서 runtime/history 재검증까지 추적한다. `IntentStore.publish_draft`, `CandidateStore.mutate`, Work publish/apply, switch/detach apply와 나머지 action의 실제 호출 근거를 모두 확인한다. 한 경로로 family 전체를 추정하지 않는다. C06/C07에서 late lock 뒤 old writer가 진행하면 전환 설계의 중단 사유다. 단순 보정 재시도나 old source patch로 해결하지 않고 Owner에게 구체적으로 보고한다.

### 6.5 시간, 실패와 보정 한도

아래 수치는 예상 소요 시간이나 채워야 할 할당량이 아니라 cleanup을 포함한 상한이다. 이번 계획 정리 중 제품 테스트는 실행하지 않는다.

| Mode | 승인 상한 |
| --- | --- |
| Acquisition, canary, 각 collection | 각각 300초 |
| Current smoke, current의 각 focused | 각각 1,200초 |
| Retained base smoke | 3,600초 |
| Retained focused | 1,500초. 기존 r00의 1,200초 입력·결과를 소급 변경하지 않는다. |
| Complete normal / complete parent-O | 각 mode에서 current+선정 retained 합산 최대 10,800초 |
| Retained 단일 complete process | 5,400초 |
| 정확한 artifact matrix | 1,800초 |
| 전체 controller campaign | 실패·admission·보정을 포함해 누적 28,800초 |

기존 차감 1,555.021초를 그대로 승계한다. 최초 Git 입력 admission의 실제 시간이 확보되지 않아 300초를 보수적으로 차감한 사실을 측정 시간과 구별한다. 실패·보정 횟수와 정확한 잔여치는 FEAT와 기존 parent receipt에서 읽는다. 중단·재개·directory 이름 변경으로 reset하지 않는다.

현행 두 lane의 exact collection과 실제 smoke/focused에서 선정 kind별 관측 최대 duration × 해당 개수, ordinary class/native-heavy 대표값, 측정한 collection/fixture overhead를 산정한다. 합계에 기존 2배 여유와 mode당 900초를 더한다. 비용이 큰 process/fault 사례를 포함하고 mapping·가정·실제 관측을 기존 근거에 남긴다. 필요한데 미측정인 group은 bounded focused에서 측정하며 zero나 과거 평균을 대입하지 않는다. 제외된 old group은 산정하지 않는다. 과거 424 ID·약 38분·mode당 약 1,140초는 역사 참고이며 현재 retained 전체 또는 새 구현의 크기·PASS·완료 예상으로 쓰지 않는다. 예전 5,460초 예시와 첫 시도 maxima 합계 26,700초도 변경된 범위의 현행 예산식이 아니다.

측정 추정이 합산 10,800초 또는 retained 5,400초를 넘으면 자르거나 timeout을 바꾸지 않고 full admission 전에 중단한다. 첫 full mode 전에는 두 mode의 계산된 예산, artifact 전체 1,800초, 남은 필수 admission/collection/안전 종료·정리 시간을 함께 남겨 둔다. 이후에는 아직 실행하지 않은 필수 작업만 reserve하고 완료 단계를 이중 차감하지 않는다. 모든 phase maxima나 full rerun이 8시간 안에 들어간다고 약속하지 않는다.

Parent가 setup/cleanup을 포함한 하나의 monotonic deadline으로 합산 두 lane을 통제한다. 준비된 pair 경로의 retained→current 내부 순서는 유지할 수 있으나, pair 이전에는 current Core·실제 전환/복구를 우선한다. Retained 선정분 뒤 current의 계산된 몫이 남은 합산 시간 안에 들어갈 때만 진행한다. Lane 사이 시간을 reset하거나 합산 deadline 이후 child success를 PASS로 받지 않는다. Synthetic timing으로 이 계산을 검증하고 related run 동안 공통 controls를 고정한다.

최초 시도에 더해 영향받은 phase당 corrected attempt는 최대 1회, campaign 전체는 최대 2회다. 실패 입력·결과와 원인을 보존한다. 예상 밖 실패 뒤에는 disposition, 검증된 process 정리, 검토된 correction이 끝나기 전까지 어떤 새 실행도 시작하지 않는다. 이 중단 조건을 지키면서 보정의 영향 범위와 횟수는 lane/phase별로 계산한다. Source/fixture/runner/policy/assertion 변경은 영향받는 근거를 무효화하므로 drift를 확인하고 새 의미를 기존 complete anchor가 뒷받침하지 못하면 필요한 full rerun을 한다. 상한 부족은 미완료 중단이며 자동 추가 시도 권한이 아니다. 미완료 조건을 명시한 안전한 checkpoint에서 작업을 중단할 수 있다.

실행 중 current test와 완료 ID를 기록한다. 출력이 조용하다는 이유만으로 hang으로 판단하지 않는다. Timeout은 incomplete다. 자연 종료, process-group absence, signal/wait error와 descendant unknown을 구별한다. 살아 있거나 관측 불가한 process가 있으면 다음 실행·정리를 막는다. Network/credential 경계 위반, 예상 밖 쓰기, record corruption, 필수 recovery source 누락, 설명되지 않은 input drift는 자동 재시도 없이 즉시 중단한다. 권한·저장 계약·보안 경계·필수 범위·상한의 추가 변경은 구체적인 대안과 함께 Owner에게 돌린다.

## 7. 이번 작업의 저장·보존·정리

기존 AGENTS의 승인된 `agent-worktrees`·`agent-artifacts` root를 사용한다. 필요한 script/input/log/recovery 자료는 처음부터 task-owned 영구 경로에 둔다. 접근 불가 시 보고하고 필요한 접근·대안을 요청하며 `/tmp`, `/private/tmp`, `$TMPDIR` 등으로 우회하지 않는다. 살아 있는 경로를 임의 이동·삭제·retarget하거나 다른 작업을 일괄 정리하지 않는다. Tool-managed scratch는 유일한 원문·필수 복구 근거를 잃지 않는 기존의 좁은 예외만 따른다.

주요 단계·리뷰 종료·handoff마다 정확한 소유권, 실행·검토·복구 소비 여부, target 밖 복구 가능한 필수 bytes/metadata, 필요한 Owner 수락·retention 조건을 확인한다. 끝난 disposable helper/중복 transport/복사본은 기존 권한으로 정리하되 마지막 복구본·고유 산출물·필수 근거·사용 중 또는 구체적 재사용 예정 checkout은 유지한다. 복사만 한 것을 cleanup이라고 보고하지 않고, 보존/active path 변경/삭제/남긴 이유를 구분한다. Retention 목적·소비자·종료 조건은 FEAT에만 남긴다. 새 보존 대장·전체 source archive·중복 backup을 만들지 않는다.

장시간 실행 전 운영 기준은 task output 16 GiB 상한, 12 GiB running stop, 8 GiB 미만이며 volume free 25 GiB 이상일 때만 admission이다. Running free가 15 GiB 미만이면 안전 종료하며 10 GiB safety floor와 물리적으로 할당한 512 MiB cleanup/log reserve를 확보한다. Parent는 입력·로그를 포함한 task root 전체의 logical/allocated bytes와 volume free를 관측한다. Free는 자주, 전체 output은 bounded interval로 확인한다. Filesystem quota가 아닌 감시 기준이며 관측 지연·정리 공간을 margin에 포함한다. Threshold 도달 시 새 실행을 시작하지 않고 기존 실행을 안전 종료한 뒤 필수 로그·복구 증거를 보존해 보고한다.

현재 약 1.19 GB allocated, 약 106.9 GB free라는 값은 일시 중단 시점의 관측이지 미래 보장이나 disk 고갈 사례가 아니다. 제품 campaign의 감시와 물리 reserve는 아직 구현·검증하지 않았다. 이번 계획 리뷰에 한해서는 별도 wrapper가 같은 공간 기준을 감시하고 512 MiB를 실제 할당했으며, 리뷰 종료·보존 확인 뒤 해제했다. 이 관측을 제품 campaign qualification으로 재사용하지 않는다. 재개 후 필요한 최소 제어·자체 점검을 먼저 한다. 이 개발 작업의 운영 조건을 지켰다고 제품 복구 자료 관리 후보 B가 완료되는 것은 아니다.

## 8. 후속 후보와 현재 작업의 의존 관계

후속 후보의 첫 진단과 제안은 FEAT의 이번 통합 정리 절에 둔다. 정식 등록·상세 설계·구현은 별도 Owner 결정이다. 이번 보완 R0는 아래 경계·의존만 확인하며 상세 설계 심사나 제품 계약 승인이 아니다.

| 후보 | 첫 결과물과 범위 | M1/M2와 관계 |
| --- | --- | --- |
| A: 규칙 독자·source/installed 진입·문서 언어 | 기존 규칙이 해결하는 부분과 부족한 부분, 독자별 최소 진입 예시, 명시 요청→프로젝트 문서 언어→대화 언어 원칙의 기존 지침 통합안, 신규/기존 adopter의 정적·실제 생성 검증안 | 이번 계획의 한국어 보정은 직접 수행한다. 공통 규칙·adapter·template·배포 파일 보강은 후속이다. Filename으로 독자/정책을 추정하거나 라이선스·외부 기여 정책·자동 rule loading·package/registry로 확대하지 않는다. |
| B: 제품 복구 자료의 책임·수명주기 | 상태별 필수 입력·위치·유실 영향, 기록/retained Git의 기존 복구 재사용, 외부 backup 예외, 운영상 감축과 필요한 Core 변경, 호환성을 유지할 단계별 개선·실패 시험안 | 현행 M1/M2의 exact input·복구·C03 예외는 그대로 검증한다. 일반 제품의 저장 UX·quota·정리 책임 개선은 선행 조건이 아니다. 외부 자료 7개를 모든 Work의 필수 산출물로 일반화하지 않는다. |
| 실행기 구조 개선 | 재현된 구조 문제·필요성·최소 예상 범위와 재검토 조건 | 정확성·안전성에 필요한 최소 correction만 M1/M2에 포함한다. 새 framework/실행기 재설계는 별도 후보이며 B와 대규모 단일 구현으로 묶지 않는다. |

후속 조사에서 M1/M2 정확성·안전성에 직접 영향이 확인되면 최소 보정과 근거만 현재 범위에 제안한다. 단순 관련성만으로 후속 전체를 완료 조건에 넣지 않는다. M1/M2 최종 결과 보고 때 후보별 필요성·권장 순서·다음 판단 시점을 다시 제시한다. 현재 우선 제안은 A의 최소 지침 개선 가능성을 먼저 판단하고 B의 상태별 진단으로 실제 Core 필요 범위를 좁히며, 실행기 구조 개선은 이번 bounded run에서 드러난 구체적 근거로만 판단하는 것이다. 이는 착수 순서의 Owner 결정이 아니다.

## 9. 보완 R0, 재개와 최종 결정

이번 보완 R0는 변경된 검증 범위·순서·실행 통제·시간 상한, 필요한 안전 사례와 불필요한 old 전수 선행조건 여부, 한국어 조건·예외·식별자·승인 범위 보존, 후속 범위 분리, 근거 재사용과 영향 판단에 집중한다. 원래 M0/초기 R0를 처음부터 반복하지 않고 변경과 연결되는 근거만 제공한다. 기존 R1이 NO-GO였다는 사실과 아직 실행하지 않은 current 제품 검증을 그대로 밝힌다.

추가 독립 리뷰 최대 4회의 기존 승인을 사용한다. 이번 요청이 새 4회를 더한 것은 아니다. 각 호출은 fresh Claude Code session, tools 없음, 최대 600초이며 기존 Claude Pro의 `claude.ai`/`firstParty`/`pro` 경로를 확인한다. API/provider override가 있거나 경로가 다르면 호출 전에 중단·보고한다. Account email/key/token을 기록하지 않는다. 자료 범위는 같은 작업의 비공개 source·contract·test·evidence와 보완 자료이며 adopter 자료·secret은 포함하지 않는다.

보완 R0와 최종 R1을 우선 확보하고, 나머지는 필요한 계획/실제 control correction 검토에만 쓴다. 실제 제어 코드가 아직 보정되지 않았으므로 이번 계획 검토를 그 코드의 실행 gate 통과로 보지 않는다. 잔여 호출로 기존 필수 검토를 충족할 수 없으면 자동 증액하지 않고 영향을 구체적으로 보고한다. 결과와 exact input, model/session, 원문 응답, Driver `accept / revise / defend / needs-user`를 분리하고 호출 전후 input drift를 확인한다. Reviewer는 test 실행·파일 수정·Owner 수락을 하지 않는다. 별도 실행 리뷰에는 정확한 allowlisted command와 경계가 필요하다.

이번 보완 R0는 추가 호출 1/4를 사용했고, Reviewer는 B1(실행 중단·금지 조건)과 B2(선정 ID의 slot 결속)를 문구·사전 gate 보정으로 해소할 수 있다고 판단했다. Driver가 위 실행 조건과 FEAT 처분에 반영했다. 이는 계획 차단 지적의 보정이며 실제 controls와 제품 동작은 여전히 미검증이다. 문구 확인만을 위한 R0 재호출은 하지 않고, 남은 3회 중 최종 R1 1회를 예약한다.

이번 결과를 보고한 뒤 Owner가 명시적으로 재개할 때까지 대기한다. 그 뒤 진행을 막는 지적이 해소되고 승인 범위·상한을 유지하면 기존 계획의 남은 구현·검증을 계속한다. 재개라는 이유만으로 같은 R0나 유효한 검증을 반복하지 않는다. Routine preparation 오류와 안전한 범위 내 correction은 Driver가 처리하고 작은 승인을 반복 요청하지 않는다.

[DR-0005](../decisions/DR-0005-delegated-ordinary-work-acceptance.md)는 Draft다. M0 채택과 실행 승인은 live 권한 예외 활성화가 아니다. 검증·최종 R1 뒤 successor 문서의 exact hash와 해당 절, DR-0003 L-4/onboarding 4/10/13 amendment를 열거하고 Owner가 결과·활성화 bytes와 scope를 별도로 결정한다. 기존 accepted table을 덮어 준비 라벨이 발효를 뜻하도록 만들지 않는다. Source 개발 결과의 수락은 사람에게 남고 runtime grant가 Driver의 자기 수락·리뷰 우회를 허용하지 않는다. Manual provider-null 동작과 M0의 backend/process/project 경계는 유지한다.

보고는 정적 관측, 실제 실행, 재사용한 역사 근거, 미검증 host/품질을 구별한다. CLI transport 성공·static review·partial PASS를 제품 qualification으로 표시하지 않는다. Result acceptance, contract activation, commit/push/PR/merge와 실제 adopter 적용은 각각 기존 별도 결정이다.
