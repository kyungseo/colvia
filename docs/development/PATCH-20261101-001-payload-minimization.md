# Payload Minimization And Refusal Closure

## Authorization And Scope

Owner가 2026-11-01 저장 schema v2, 최소 metadata 기록, 외부 recovery/transient, 효과 시작 전 거절과 종료 증거의 구현 및 Claude CLI 리뷰를 승인했다. 고정 source는 `ff299095ba450ef199392ce2f6d92ee5e8f3918b`다. 승인된 설계의 SHA-256은 `c0c16bc53c9260f2cd73ab9092d18a348cc36d00ab1eeb89226b478099c9f17c`이며, 사전 정적 검토 4회와 Driver 보정을 거쳤다. 이전 검토 원문은 기존 private 설계 기록에 보존되어 있다. Driver는 Codex, Reviewer는 Claude CLI, 결과 수락은 Owner 책임이다.

새 기록은 full live spec의 승인 digest를 유지하되 payload 원문을 capsule에 저장하지 않는다. 기존 v1 읽기는 유지하며, v2 상태는 strict event 전이와 실제 효과·process 종료 증거를 재계산해 판정한다. 미해결 intent나 손상 journal은 쓰기를 차단한다. 외부 원문은 결과 수락 전까지 보존하며 자동 재생·이관·시간 만료는 추가하지 않는다.

별도 View 작업의 checkout과 변경 파일은 수정하지 않는다. 구현은 분리된 작업 트리에서 진행한다. 공용 개발 index 추가는 해당 작업과 통합할 때 처리하며 이 파일이 진행 기록을 소유한다. Git commit·push·PR·merge, 실제 adopter 설치, 실제 자료, provider/model 호출, native qualification은 별도 승인이다. 검증용 offline 자식 process와 합성 workspace는 구현 검증 범위다.

## Estimate And Verification

착수 시각은 2026-10-31 14:59:43 UTC다. 예상 능동 작업 10–16시간, 승인 누적 상한 18시간이다. 설계 검토에서 제시한 판단 추정이며 구현 실측은 아직 없다. 포함 범위는 schema/reader 3–5시간, 저장·recovery·adapter 통합 3–5시간, 실패·호환·closure 검증 및 리뷰·보정·문서 4–6시간이다. 짧은 도구 및 Reviewer 실행 대기는 포함하고 Owner 응답·접근 제공 대기는 제외한다. 상한에 도달하면 미완료 범위와 후속 비용을 기록하고 중단한다.

schema/reader 완료 시 Claude 리뷰와 집중 검사 결과를 바탕으로 남은 범위·예상 시간·누적 사용 시간을 재산정한다. 이후 통합 변경의 fault 검사를 모아서 수행하며 마지막에 normal/parent-O 회귀를 각각 한 번 수행한다. 같은 digest만을 이유로 전체 검사를 반복하지 않는다. 단순 전이 fixture와 실제 offline process 부재 증거는 구분한다. capsule 표식 검사에는 입력이 경로에 도달했음을 입증하는 양성 대조를 포함한다.

## Progress — 착수 시점 기록

- Preflight: 고정 source에서 새 구현 작업 트리를 만들었다. 이전 View 작업은 경로와 변경 파일 목록만 확인했다.
- 호환성 결정 대기: 기존 inventory window의 양방향 읽기 규칙과 v2를 거절하는 구 reader가 충돌한다. 새 window와 exact predecessor 전환 경계를 권고했고 Owner에 질의했다. 답변 전에는 독립 schema/reader 작업만 진행한다.
- 구현·검증 결과는 아직 없다. 기존 합성 baseline은 실제 adapter 종료나 native 차단의 증거가 아니다.

### Schema Draft And Review Attempt

Owner가 새 `official-execution-2` inventory window와 exact predecessor 전환 경계를 승인했다. 실제 설치·배포 승인은 포함하지 않는다. 새 window 이후 구 window rollback은 거절하도록 연결한다.

v2 exact schema·순수 상태 reducer·버전별 capsule reader 초안을 작성했다. CPython 3.14.6 `-I -S -B`에서 집중 검사 24개를 실행했다. 첫 실행은 22개 통과·2개 오류였고 손상 journal의 실제 거절 예외와 테스트 oracle의 종류 차이가 원인이었다. 예외 oracle과 birth 미확정 자동 종료 제한을 보정한 두 번째 실행은 24개 모두 통과했다. 이 검사는 합성 전이와 로컬 capsule 판독이며 실제 process·adapter·native 보호 검증이 아니다.

Claude.ai Pro 구독 인증·firstParty 경로와 과금 override 부재를 확인했다. Owner가 새 9개 입력 패킷의 전송 및 같은 범위 보정 재검토를 승인했다. 최초 구현 리뷰 시도는 입력 drift 없이 사용량 한도로 종료했고 실제 모델 응답·기술 검토는 없었다. CLI 원문:

```text
You've hit your 5-hour limit · resets 12:50am (Asia/Seoul)
```

Driver 처분: 검토 미실행으로 기록한다. 동일 구독 경로의 재개 시각(2026-11-01 00:50 KST) 이후 다시 시도하며, 그동안 독립 recovery/reader 구현을 계속한다. schema/reader 완료 및 재산정 checkpoint는 아직 도달하지 않았다.

### Schema/Reader Checkpoint — Initial Implementation

착수 약30분 시점에 v2 schema·reader·외부 recovery 판독·resolution preview의 1차 구현을 마쳤다. 집중 검사32개가 통과했다. v1/v2 혼재, strict field·순서·효과 재계산, 부분 journal, 외부 가용성, 원문 저장 실패, process identity 미확정 거절을 포함한다. 실제 process 관찰은 이 단계에서 mock이며 process 종료의 실행 증거로 사용하지 않는다. Claude 기술 검토는 사용량 제한으로 미실행이어서 검토 완료 판정은 보류한다.

남은 예상 능동 작업은10–15시간, 누적 승인 상한까지 약17시간30분이다. 저장·adapter 통합 검증, 새 inventory window의 전환·복구, F01–F24와 실제 offline closure, normal/parent-O 회귀·리뷰·문서가 남았다. 초안 코드는 빠르게 작성됐지만 통합 실행 근거가 없어 초기 추정을 크게 줄이지 않는다. 새 window 추가 범위도 이 판단치에 포함한다. Reviewer 대기 중 독립 구현은 능동 시간에 포함하며 아직 제외한 Owner 대기 시간은 없다.

전환 predecessor는 고정 source의44개 배포 경로를 기존 합성 candidate와 byte 비교해 불일치0을 확인했다. release는 `product-release-6bf0d829b473c9f31f3d4be5`, digest는 `6bf0d829b473c9f31f3d4be50a6a4ddb74ed5493b09fa86997b8651a41a501fc`다. 새 window는48개 경로이며 기존44개 window의 history membership은 유지한다. 현재 설치·배포는 실행하지 않았다.

### Reader Review Correction And Consolidated Verification

Claude 기술 리뷰는 schema/reader에서 종료 코드 검증, 성공 write의 CAS identity 결속, resolution append 사전 검증을 지적했다. Driver가 재현·보정했고 집중 검사37개가 통과했다. 실제 document observation은 이미 hardlink·크기 초과를 거절하므로 해당 재현은 잘못된 관측값을 주입한 방어 경로 검사로 구분한다. Review 원문과 입출력 identity는 기존 private task record에 보존했다. 같은 승인 범위의 보정 재검토를 진행하며 Owner 수락은 별도다.

통합 검사는 실제 offline adapter/worker, 실패 경계, 원문 양성 대조 및 truth/Git index, process 생존·부재, v1 permission과 exact window 전환·중단·rollback·repair·detach를 포함한다. 네이티브 profile·provider 호출·실제 adopter 검증은 수행하지 않았다. 전체 normal/parent-O 회귀는 변경된 writer guard와 lifecycle이 여러 command에 미치는 영향을 확인하기 위한 필수 검사다. 동일 source/class/method의 import alias만 한 번 실행하며 원래 discovery와 대응표를 남긴다.

### Schema/Reader Completion Checkpoint

착수 약96분 시점에 schema/reader의 독립 정적 리뷰 PASS를 받았다. Blocker·High·Medium은 없었다. Driver는 Low 중 non-zero write의 latch 표시와 verifier 모순 조합을 추가 보강했고 정상 close/result 순서도 포함한 집중 검사40개가 통과했다. 시작 전 잘못된 callback은 예약 없이 거절할 수 있어야 하므로 해당 제한 제안은 채택하지 않았다. 추가 보강분은 전체 구현 리뷰에서 다시 확인한다. Reviewer가 실행한 검사는 없으며 전체 writer·recovery·adapter·window 리뷰를 이 PASS로 대체하지 않는다.

남은 예상 능동 시간은4–7시간, 누적 상한까지 약16시간24분이다. 전체 회귀와 보정, 전체 구현 CLI 리뷰·보정, exact-artifact 최종 확인 및 문서가 남았다. 통합 집중 검사의 실측 진척을 반영한 판단치이며 기다리는 동안 독립 작업을 하면 중복 계산 없이 능동 시간에 포함한다. 순수 Owner 대기는 제외한다.

전체 회귀 첫 시도는 부모 Python과 shebang 자식 Python의 PATH 선택이 달라 installed 검사 startup에서 실패했다. 제품 변경 없이 task runner의 per-process PATH를 고정한 단일 재현은 통과했다. 두 전체 실행은 중단했고 보정 환경에서 다시 수행한다. 별도 실제 process 검사에서는 durable schema8 receipt 직후 SIGKILL 및 exact recovery, lock에서 기다리던 구 installed writer의 거절, 실제 synchronous exec 실패, 실제 resolution writer guard 경로를 확인했다.

### Consolidated Regression And Final Candidate

전체 normal/parent-O 실행은 각각1,266개를 수집한 실행 집합에서1,165개 통과·1개 실패·100개 제외로 끝났다. 제외100개는 Windows 전용 검사이며 macOS 통과로 계산하지 않는다. 실행 시간은 각각4,243.601초·4,247.042초다. 유일한 실패는 기존 문서의 inline-code 링크 예시를 실제 링크로 읽은 검사였고, 검사 조건을 유지하며 예시를 일반 경로 표기로 보정했다. 전체 실행 뒤 task runner가 skipped test 객체를 JSON으로 직렬화하지 못했다. 원본 로그·수집 목록은 보존했고 요약은 해당 로그에서 재구성한 기록임을 명시했다. 제품 입력의 전체 실행 중 변경은 없었다.

후속 Claude schema 리뷰도 PASS였으나 locale에 따른 process birth 변화를 잠재 문제로 제시했다. Driver는 실제 살아 있는 child가 locale 변경 시 부재로 판정되는 preview를 재현했다. 관측을 C locale·UTC로 고정하고 stderr·불일치 exit/stdout·형식 오류를 부재로 인정하지 않도록 보정했다. 기존 v1 child birth는 지역화될 수 있으므로 해당 PID가 존재하면 보수적으로 resolution을 보류한다. PID 재사용 시에도 실제 부재까지 지연될 수 있으며 기존 기록을 변경하지 않는다. 시작 전 거절 terminal의 revoked 표시도 true로 맞췄다. 전체 구현의 정적 리뷰는 아직 별도 대기 중이다.

최종48경로 후보는 `product-release-4ed8700a4b9aec1f5326a12d`, digest `4ed8700a4b9aec1f5326a12d0ab3149b1a05521bdd0965695fd1942e432cb8ed`다. 실제 adopter 설치는 하지 않았다. 전체 회귀의 영향받지 않은 결과를 재사용하고, 보정된 process/resolution/schema·문서 링크를 두 모드로 집중 재검사하며 고정 후보의 별도 lifecycle matrix를 실행한다. 단순 후보 digest 변경 때문에 전체 회귀를 반복하지 않는다.

### Local Verification Complete — Integration Review Pending

최종 보정 집중 검사60개 중58개는 두 모드 모두 통과했다. 나머지2개는 실제 OS 범위를 벗어난 합성 PID를 쓰던 순수 Host fixture에서 오류가 났고, 제품 관측 조건을 유지하며 fixture의 mock 경계를 명시한2개 재실행이 모두 통과했다. 실제 process·locale·Host 사망·writer lock·adapter 종료 검사는 양 모드에서 통과했다. 전체 회귀의 문서 링크 실패도 정확한 해당 검사로 해소했다. 실패한 원 실행을 모두 통과한 것처럼 바꾸지 않고 후속 근거를 연결했다.

고정 최종 후보의 lifecycle9개와31개 subcase가 normal/parent-O 모두 통과했다. 실제 receipt 직후 process 사망, lock 대기 구 writer, exact predecessor 전환·중단 복구, 구 writer family·구 window rollback 거절, 같은 window의 Q 이력·rollback·repair·detach와 원문 reader를 포함한다. 각 실행은 약186초였고 후보 bytes 변경은 없었다. 전용 runner의 합성 workspace는 검사 종료 후 정리됐다. 필요한 source·후보·검사/리뷰 근거는 후속 리뷰와 Owner 수락을 위해 보존한다.

현재 누적 능동 작업은 약174분,18시간 상한까지 약906분이다. 남은 예상은 전체 통합 Claude CLI 리뷰·보정·보고1–3능동 시간이며, 새 통합 지적의 규모에 따라 달라진다. Owner 전송 승인 대기는 제외한다. 확대 구현 패킷의 외부 전송은 승인 대기이고 통합 리뷰 완료나 결과 수락을 주장하지 않는다. 실제 adopter 설치 상태는 확인하지 않았으며 native qualification·실제 자료·provider 호출·배포·Git 통합은 이번 결과에 포함하지 않는다.

### Integration Review Corrections

전체 통합 Claude CLI 리뷰는 CHANGES_REQUESTED(High1·Medium2·Low4)였다. High는 제품 효과 경계가 아니라 보정 뒤 검사 소비자 누락이었다. 앞선 로컬 검증 완료 판단은 충분하지 않았으며 이 후속 검증으로 대체한다. 누락된4개 Host fixture의 합성 PID 경로를 재현해 mock 경계를 명시했고 전체 execution·fault·payload·admission·history와 schema·recovery·process·adapter 소비자를 양 모드로 다시 검사한다.

CLI는 입력 parsing/prepare와 실행·상태·취소·resolution의 오류 기본 코드를 구분하며, 실행 오류에는 status 확인 안내를 붙인다. 프로세스 미확인은 closure_unconfirmed로 매핑한다. receipt는 locks 경로에서 완성한 뒤 exclusive rename으로 게시한다. 부분 게시 실패와 rename 후 동기화 실패에서도 유효 journal을 읽고 알려진 효과·종료 상태를 보존한다. 이9개 집중 검사에서 보정 전9개 assertion 실패·5개 오류를 확인했고 보정 뒤9개가 모두 통과했다. subtest 실패 수와 test method 수는 다르다.

명시적 root status 조회는 transient·cleanup marker 존재 여부만 보고한다. 늦은 callback은 최초 중단 사유를 덮어쓰지 않는다. 기존 응답 손실 검사는 exchange 오류 주입이었음을 정정하고 실제 worker의 빈 pipe 종료 검사도 추가했다. exact predecessor 전환 후 detach를 검사하고 더 오래된 window 이력의 기존 거절 한계를 문서화했다. window 허용 범위·자동 정리 권한은 확장하지 않았다. 보정된 후보의 같은-window 이력·rollback·detach와 predecessor 전환 후 detach는 양 모드 각2개(각4 subcase) 통과했다.

전체 소비자172개는 normal412.483초·parent-O412.545초에 모두 통과했다(실패·오류·skip0). 이 결과로 부족했던 영향 범위 검증을 대체한다. 보정 후보는 `product-release-d8fc9501595ac5b79f283394`, digest `d8fc9501595ac5b79f28339490e90a33fb14775ec08303da71ff0488ec562adf`이며48경로·미설치 상태다. lifecycle 추가2개/4 subcase는 각116.040초·116.074초에 통과했고 후보 bytes 변경은 없었다. 변경되지 않은 lifecycle 정책의 기존9개 matrix 근거는 재사용한다. 보정 diff와 이 실행 결과의 Claude CLI 재검토를 진행한다.

### Final Low Corrections

보정 재검토는 PASS였고 기존 High·Medium·Low 항목을 닫았다. 추가 Low3건은 반복 revoke의 기존 사유 유지, 일반 OS 오류 경로 문자열의 코드 분류 제외, 복구본 상태 필드 주어 명시로 보정했다. 내부 ContractError·HostRefusal의 고정 메시지와 TimeoutError 타입 의미는 유지한다.2개 단위 검사에서 보정 전12개 assertion/subtest 실패를 재현했다.

영향60개 검사는 normal210.228초·parent-O209.392초에 모두 통과했고 소스 drift는0이었다. 로그에 Python·optimization·소스 digest를 포함했다. 검사 뒤 runner의 종료 표현식이 빈 목록을 SystemExit에 전달해 exit1과[]를 출력한 별도 기록 오류는 명시적으로 보존했다. 종료식을 정수0/1로 고치고 네 성공/drift 조합을 확인했으며 검사 의미가 바뀌지 않아60개를 반복하지 않았다.

마지막 후보는 `product-release-57dec58216c7d5a594a47bad`, digest `57dec58216c7d5a594a47bad8234ad55f225c83fa79bc85deee523cacdf9cb13`다. 공통 source의 continuation-1 선언에서 명시적48경로 official-execution-2 후보를 준비했으며 실제 설치는 하지 않았다. lifecycle 코드·저장 형식은 바뀌지 않아 앞선 고정 후보 검증을 재사용한다. 이 작은 보정의 마지막 정적 재검토를 진행한다.

### Review Closure And Claim Corrections

마지막 Claude CLI 정적 재검토도 PASS(Blocker·High·Medium0)였다. round6의 전체 통합 판단에 round7·8의 보정 판단을 연결한다. Reviewer는 테스트를 실행하지 않았고 같은 계열 모델의 fresh session을 사용했다. 결과 수락은 Owner에게 남는다.

앞선 “늦은 callback은 최초 중단 사유를 덮어쓰지 않는다”는 문장은 이미 철회된 Host의 직접 refuse 및 반복 revoke 경로로 한정한다. 이후 dispatch/fail은 현재 실패 원인을 다시 분류할 수 있으며, 모든 terminal 사유가 최초 revoked 사유와 같다는 전역 계약은 추가하지 않는다. 효과·권한·종료 근거 판정은 이 표시와 별개다. 프로세스 종료 오류가 모두 closure_unconfirmed라는 문서 표현도 제거했다. 명시적으로 분류한 고정 메시지 외의 관측 명령 오류는 호출 단계의 기본 코드가 될 수 있으며 execute의 status 확인 안내는 유지한다. 새 Low2건은 이 설명 보정으로 처리했고 추가 제품 동작 변경은 없다.

실제 receipt 게시 중 Host crash와 lock-stage 잔존의 lifecycle 영향을 별도로 시험한 것은 아니다. partial/post-rename IO 주입, 기존 exclusive rename, 별도 Host·lifecycle process 사망 검사는 구분한다. 최종 후보의 진단·문서 변경 뒤 exact lifecycle을 반복하지 않았으며 불변인 lifecycle/schema의 기존 고정 후보 근거를 재사용한다. source diff check와 보존 확인 후 구현·로컬 검증·CLI 리뷰를 인계한다.

### Implementation Handoff

승인된 구현·로컬 검증·Claude CLI 통합/보정 리뷰를 마쳤다. 최종 재검토 PASS, Blocker·High·Medium0이며 마지막 비차단 지적은 위 설명 범위 보정으로 처리했다. 마지막 인계 후보는 `product-release-65825b1fe786981d541dab26`, digest `65825b1fe786981d541dab2644f7e2ffadefd39f75cdc25ad38728f3ac51623b`이고48경로·미설치 상태다. 이전 후보는 검증 당시 identity이며 현재 인계 pointer가 아니다. 최종 코드가 리뷰 입력과 같고 후보의 소스 bytes·권한이 일치함을 확인했다.

누적 능동 작업은 약208분(3.46시간),18시간 상한 이내다. Owner 응답 대기는 제외하고 CLI·검사 대기는 포함했으며 병렬 실행 시간은 중복 계산하지 않았다. 구현은 미커밋 상태로 보존하며 Owner 결과 수락·Git 통합·실제 adopter 설치를 완료로 간주하지 않는다. 별도 View 작업은 수정하지 않았고 그 작업과의 통합 검증은 아직 없다.
