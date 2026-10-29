# Official Adapter Product Entry And Payload

## Approved Scope

2026-10-29 Owner가 공식 adapter의 제품 진입점·설치 payload 연결, macOS 합성 설치/검증, R0/R1 및 범위 내 보정을 승인했다. 기존 합성 source-only 결과는 수락됐다. 누적 중단450분/신규작업420분이며 기존 소비를 이어받는다. 추가 권한이나 live 실패 재시도가 필요하면 중단한다. Git 통합·실제 adopter·자동 Core accept/apply는 제외한다.

## Implementation Contract

명시적 official-execution-1/schema7, 기존30개형식 보존, flat official 모듈과 별도 runtime resource, 실제 Work/intent/문서/예산 결속을 구현한다. 실행기록은 새window의 project-owned .hrn/executions 아래 보존하며 detach가 삭제하지 않는다. Host가 공통writer_guard를 보유하고 effect/journal을 단독 기록한다. cancel.json의 write-once 게시만 동시쓰기 예외다. 미종결/unknown은 새실행/lifecycle을 차단하며 명시적 관측기록 resolve가 삭제·재시도 없이 종료처리한다. 삭제된runtime 이후에도 원문기록은 보존한다. 기존 Work/intent schema와 수락 의미는 바꾸지 않는다.

새형식은 고정모듈집합과 resource hash를 import 전에 확인한다. 공통source의 기본선언은 continuation-1이며 명시적prepare출력에만 새형식을 부여한다. Windows의 기존 고정후보와 qualification은 변경하지 않는다. fresh init·exact predecessor update·동일형식 P/Q 왕복·repair/detach/중단복구를 검증하며 downgrade와 cross-OS전환은 거절한다.

## Review And Evidence Plan

Claude Opus 5.5의 두 정적R0는 revise 및 revise(국소)였다. 저장/authority/취소/상호배제/bootstrap/전환/P-Q검증 지적을 모두accept했고 최종3건은 window별bootstrap, 취소marker단독예외, operator-resolved-unknown으로 반영한다. 도구/실행없는 검토이며 Owner수락이 아니다. 원문과 정확한입력은 Driver의 private 검토기록에 보존한다.

집중admission/취소/복원·실제process경쟁·합성Git/non-Git설치와lifecycle·최종normal/O전체회귀각1회·설치entry공식live3회/worker11회를 계획한다. 기존TLS진단/Rustbuild는 반복하지 않는다. static검색1065개test method는 discovery나PASS가 아니다. 새경로/새authority의 효과는 이전합성PASS로 대체하지 않는다.

## Estimate And Bound

추가예상200–300분은 판단추정이며 구현/집중검사후 잔여를 다시평가한다. 기존live58초와 과거424개matrix38분은 새전체작업의 측정값이 아니다. 450/420분상한은 그대로고 마지막30분은 종료/보존에 남긴다. Owner대기제외·겹친시간은1회계상한다. 예산부족시 미시작/미완료를 그대로보고한다.

## Current State

2026-10-29 구현과 승인된 macOS 합성 검증을 완료했다. 아래 Owner Result Acceptance에 따라 개발 결과는 수락됐다. Git 통합과 실제 adopter 적용의 진행은 별도로 승인됐으며, 완료 여부와 Windows 제품 지원을 이 수락에서 추론하지 않는다.

## Executed Evidence And Reuse

- 최종 R4 후보의 admission·실행·기존 실패 사례 집중 검사 52개와 고정 P/Q 설치·전환 검사 10개가 일반/최적화 모드에서 각각 모두 통과했다.
- R3 전체 회귀는 두 모드 각각 1,176회 실행, 1,166개 고유 ID였다. 통과 1,075회(고유 1,065개), schema7 분리 계획 하위 사례 실패 1건, native Windows 전용 제외 100개를 원본 그대로 보존했다. 전체 PASS로 보고하지 않는다. 영향받지 않은 증거를 재사용하고, 최종 R4에서 해당 기존 실패와 변경 위험을 양쪽 모드로 확인했다. R4 전체 회귀를 새로 실행했다는 뜻은 아니다.
- 최종 native 합성 Host에서 실제 sandbox worker 5개를 사용한 검사와 실제 broken-pipe 종료 검사가 통과했다. 후자의 process 관측 seam은 별도 기록했으며 실제 descendant observer 검증으로 확대하지 않는다.
- 보호 검사 첫 시도는 검사기의 프로젝트 상위 경로가 설치 정책 파일과 겹쳐 프로세스 생성 전에 거절됐다. 실패와 소비 예약을 보존했다. Owner가 별도 승인한 보정 1회는 제품·OS 정책 변경 없이 부모/자식 읽기·쓰기 거절 12개를 통과했다.
- 최종 설치된 공식 runtime에서 정상 실행 28.214초, 중단 10.794초, 새 grant 재실행 26.304초가 통과했다. 실제 runtime·account/read·model/list·thread/start·turn/start 각 3회, worker 총 11개, turn/interrupt 1회를 사용했다. 보호 문서와 설치 식별자는 불변이다.
- 읽기 전용 Host 복원 1회에서 과거 call ID와 새 합성 call ID, 소비된 grant의 재실행이 거절됐고 문서·기록 바이트가 유지됐다. 이 검사는 모델을 다시 시작하거나 모델이 생성한 늦은 callback을 관측한 것이 아니다.
- 기록된 runtime·worker·관측된 자식의 종료와 소유 process group 부재를 확인했다. 표본으로 발견하지 못한 detached daemon까지 없다는 보장은 하지 않는다.

## Candidate Identity

검증 대상은 official-execution-1의 P `26e35d58cd28a49cae6c2342ee354efc16dfd4209a214de545974b28b6680c47`, Q `39d910f3f2ffb4de8b4ed183d8a4846f22050d569d346d84cefb140bad0a9271`이다. 고정 predecessor는 continuation-1 `fd1a49a6f62cc1fc6ee84f649bec8c95fe5ce1b4b30b76d032e56eb41031735b`다. 실증 후에는 이 source-only 작업 기록만 갱신했다. 고정 설치 payload와 실행 코드의 바이트는 바꾸지 않았다.

## Review Disposition And Remaining Decisions

R1 최종 정적 판정은 “accept dispositions; revise (minor, local) before live”였다. Driver는 N1 broken-pipe 종료, N2 worker 생성 실패의 안전한 resolve를 보정하고 양쪽 모드 및 필요한 실제 process 검사로 확인했다. N3 용량 산정은 61파일/63.625MiB로 바로잡았고 N4는 worker RLIMIT_CORE=0으로 보완했다. 선택 사항 N5는 적용하지 않아 turn ID 미확정 중단의 unknown 한계를 유지한다. 후속 schema7 분리 계획 보정은 Driver 검증이며 새로운 Reviewer 승인으로 표현하지 않는다. 원문 리뷰와 입력 identity, 실제 Owner 결정은 기존 private 작업 기록에 보존했다.

deadline 만료·쓰기 후 verifier 실패는 unknown을 남길 수 있다. 저장 실패 시 durable terminal을 보장할 수 없고, 생성 직후 identity 기록이 없는 crash gap은 resolve를 거절한다. 늦은 cancel 게시가 이미 허용된 효과를 되돌리지는 않는다. Windows native, 일반 사용성·운영 적합성과 실제 adopter 검증은 이 결과의 범위 밖이다.

제품 결과 수락이 다음 Owner 결정이다. commit/push/PR/merge와 실제 프로젝트 설치·실행·Core accept/apply는 별도 권한이 필요하다. 기존 설치는 이번 범위에서 조회하지 않아 현재 설치 상태가 미확인이다. 즉시 업데이트를 권고하지 않으며, 대상과 고정 후보를 선택한 후 현재 binding·문서 보존·원래 사용 사례·rollback 한계를 별도 확인한다.

최종 source 변경과 복구본, 고정 후보, 리뷰/실패/실증 증거는 결과 수락과 Git/복구 결정까지 유지한다. 소비가 끝난 비어 있는 검사 socket 경로는 제거했다. 추가 실행이나 자동 재시도는 예약하지 않는다.


## Owner Result Acceptance — 2026-10-29

Owner는 제시된 순서대로 진행하도록 지시하여 현재 구현·검증 결과를 수락하고 Git 보존·통합 및 후속 실제 프로젝트 적용·실증의 진행을 승인했다. 수락 대상은 위 고정 P/Q와 실행·상속·미검증 범위를 구분한 결과다. 기존 실패, 알려진 한계, Reviewer의 실제 판정과 Driver 처분을 유지한다. 후속 설치·실행은 대상 상태와 정확한 입력을 확인하고 해당 승인 경계를 따라 수행하며, 이 기록이 이후 결과를 미리 수락하지는 않는다. 이전 절의 수락 대기 문구는 결과 제출 당시 상태다.
