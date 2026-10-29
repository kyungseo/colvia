# U2 Host — Qualification Candidate

## Single-Document Edit Candidate — 2026-10-28

[`single-document-edit-v1`](../../FEAT-20261028-001-single-document-edit.md)은 macOS/Codex의 기존 문서 하나를 한 구간만 바꾸는 source-only 후속 후보다. 입력 ID는 총 1–8개이며 read1 → write1 → `DOC-LINKS`·`DOC-GFM`·`DOC-CLAIMS` 각1회 → 봉인 순서다. 마지막 callback은 durable 후보 receipt를 남긴 뒤 응답을 보내지 않고 종료하며, 정상 terminal은 `sealed-terminated`다. resume·correction·authority/recovery apply는 허용하지 않는다. 이전 qualification의 수락이 이 후보의 실제 실행 검증을 대신하지 않는다.

trusted Driver는 `host.edit_only('prepare', ...)`에 task 데이터와 신뢰한 snapshot/baseline reader를 전달한다. 같은 함수가 anchor·activation·launch contract·역할 profile을 만들며, 새 업무마다 source나 공통 template을 고치지 않는다. 준비는 reservation 소비와 별도다. 승인 후 소비·FD controller 준비를 마치면 `host.edit_only('execute', ...)`으로 실행한다. 입력 데이터가 임의 코드·reader를 고르는 loader는 제공하지 않는다. 실행 파일은 trusted Driver가 경로·hash를 고정한다. 이 entry의 구현과 offline 결과, 아직 관측하지 않은 실제 native 종료 동작은 연결된 개발 기록에서 구분한다.

## Current Navigation — 2026-10-27

승인된 source/adapter qualification과 첫 운영 가이드의 완료 판단은 [최종 Owner 수락과 Done](../../FEAT-20261022-001-prepared-tool-plan-live-qualification.md#final-owner-acceptance-and-work-done--2026-10-27-kst)에 있다. 아래 후보 설명과 과거 미검증 표기는 작성 당시의 근거·한계와 함께 보존한다. 실제 다음 실행은 [수락 범위와 남은 한계](../../FEAT-20261022-001-prepared-tool-plan-live-qualification.md#accepted-scope-and-remaining-limits), 이 문서의 [공개 이력 allocation 경계](#public-history-allocation-boundary), 해당 새 대상·입력의 승인을 함께 확인해야 한다. 일반 설치 payload에는 이 검증용 Host가 포함되지 않는다. 이번 안내 연결은 [CHORE-20261027-002](../../CHORE-20261027-002-user-flow-and-development-doc-alignment.md)가 소유한다.

이 디렉터리는 prepared-tool runtime과 문서 worker를 연결하는 검증용 host 후보다. 구현과 집중 검사는 진행 중이며 실제 OS·native 인증·installed Core·H01–H10 적격성을 아직 얻지 않았다. 진행, 시간/시도 장부와 Owner 결정은 [FEAT-20261022-001](../../FEAT-20261022-001-prepared-tool-plan-live-qualification.md)이 소유한다. 과거 preflight 결과는 [이전 기록](../../FEAT-20261021-002-u2-single-host-source.md)에 남는다.

## Invocation And Trust Boundary

```text
PY -I -B SOURCE/docs/development/verification/u2-host/host.py COMMAND --spec SPEC
```

`COMMAND`는 `live-smoke`, `qualify`, `iterate`, `actual`, `actual-accept`, `recover` 중 하나다. trusted Driver가 exact executable/spec/profile/입력 identity와 승인 범위를 고정한다. 모델은 경로·argv·환경·도구 등록·승인 입력을 선택하지 않는다. 예전 preflight 함수는 비교 근거로 보존하지만 CLI로 실행하지 않는다.

`live-smoke`는 native clock turn, `qualify`와 `iterate`는 합성 U2 실행, `actual`은 별도 승인된 실제5문서 편집에 사용한다. 명령 등록 자체가 실행 승인은 아니다. H01–H09 qualification은 고정 negative·실제 host/worker/Core 증거를 함께 평가하며 명령 exit0 하나로 판정하지 않는다.

host는 native initialize → thread/start → turn/prepare → turn/startPrepared를 사용한다. 매 turn의 source/build·입력/history·tool envelope와 callback의 thread/turn/call을 대조한다. turn당 generation 최대2회, dispatch 최대1회를 유지한다. native schema 변환이 생략하는 `maxItems`, `uniqueItems`, `pattern`은 호스트의 인자 검사로 강제하며 나머지 wire schema는 전체 대조한다. 미등록 RPC, 늦게 도착한 경고, 과도한 알림, deadline·process 종료 불명은 거절한다.

## Documents, Budget And Resume

`worker.py`는 승인된 파일 ID의 read, 단일 파일의 prior digest를 확인하는 atomic write, `DOC-LINKS`·`DOC-GFM`·`DOC-CLAIMS`만 제공한다. 작업별 Seatbelt profile이 exact read/target/swap을 제한한다. 원본 출력과 쓰기 입력은 효과 전에 보존한다. symlink·hardlink·ancestor identity·동일 device·mode·사후 bytes를 확인하고 실패한 swap을 자동 삭제하거나 재시도하지 않는다. 직렬 writer 소유를 전제로 하며 이를 kernel CAS로 표현하지 않는다.

GFM은 고정 parser를 process 안의 JavaScriptCore에서 실행한다. verifier에는 결과 쓰기, network, 임의 child 권한을 주지 않는다. DOC-CLAIMS는 고정 required/forbidden 문구와 source quote를 점검하며 전체 사실성을 보장하지 않는다. 실제 결과 품질과 Owner 관측은 H10의 별도 판단이다.

동일 durable journal에서 approval·candidate·task, phase/start/thread/turn/generation/dispatch, authority 호출, 보정과 시간 사용을 유지한다. effect/send 전에 잠금 아래 reservation을 fsync한다. 손상·누락·다른 thread/turn·중복 control과 예약 재사용은 거절하며 crash 후 사용량을0으로 만들지 않는다. Owner만 기다리는 동안에는 새로운 작업을 예약하지 않는다.

봉인 전 재개는 원 입력, 현재 문서 전체 bytes/digest, 원 source identity, verifier·예산·pending 상태와 종료가 확인된 마지막 checkpoint가 필요하다. 설명용 요약으로 원문을 대체하지 않는다. 허용된 새 thread의 입력 한도에 전체 복구 문맥이 들어가지 않으면 unavailable로 중단한다. 봉인 이후 새 thread로 accept를 옮기지 않는다.

## Acceptance And Human Recovery

`actual-accept`는 exact candidate/ticket에 대한 Owner 응답을 이미 편집한 idle controller에 전달한다. 같은 admitted thread에서 read/write/verify는 거절하고 accept만 허용한다. 모델은 opaque handle만 반환한다. host는 원 ticket bytes·Work/home/actor/action/result·현재 grant를 다시 확인하고 순정 installed CLI의 prepare/apply를 한 번만 호출한다. apply 이후 불확실성은 자동 재호출 사유가 아니다.

`recover`는 실제 S1–S5 원 ticket·actor·decision·pending·종료 상태를 묶은 packet에 별도 Owner replay-once 승인이 있을 때만 사용한다. 직전 상태를 다시 비교하고 한 번 소비한 ticket은 거절한다. `tests/fixtures/u2_host.py`의 barrier는 합성 installed 최초 호출에만 적용한다. 로드된 module의 경로/digest와 writer guard 내부 publication 직후 fsync를 관측하며 실제 process death는 별도 실행으로 확인해야 한다. H04/H10과 replay는 wrapper 없는 installed CLI를 사용한다. trusted Driver의 인간 응답 중계는 별도의 암호학적 인간 인증이 아니다.

## Evidence Limits And Preservation

기존8개 host test ID에는 합성 admission/ticket/recovery, 문서 atomic write와 alias 거절, journal·late RPC·notification·자식 종료 검사가 포함된다. 이 결과는 실제 worker Seatbelt, native 계정/정책/model, installed authority recovery 또는 실제5문서 결과를 대신하지 않는다. process·profile·source·입력 identity와 미확인 항목은 실행 기록에서 함께 확인한다.

로그에는 필요한 metadata/digest와 task-private 승인·복구 입력을 구분해 보존한다. credential·계정 원문·민감한 모델 payload를 일반 진단 로그에 넣지 않는다. 단계/전체 상한, scope·권한 확대 필요, 예상 밖 sender, 원 복구 입력 손실, 불명확한 authority effect가 있으면 중단한다. source commit/push/배포와 실제 결과 수락은 이 host의 실행 성공에 포함되지 않는다.


## 승인된 Clock V2 및 C-FD 후보

시간 불연속 복구는 기존 장부를 수정하는 일반 resume가 아니다. `Budget.recover_clock`은 별도 Owner 승인 packet의 원 anchor/journal·정산·checkpoint를 확인하고, 원 controller/append lock을 획득한 뒤 새 immutable epoch를 만든다. 누적 시간과 모든 카운터·재사용 식별자·stop 상태를 이어받으며 pending 또는 sealed 상태를 해제하지 않는다. 같은 목적지 재사용·입력 drift·낮은 carry·상한/예비 변경을 거절하고 새 epoch에서도 2초 wall/monotonic guard를 유지한다. 원 장부와 exact packet은 복구·검토 소비자가 끝날 때까지 보존한다.

prepared runtime은 task의 고정 UDS로 CONNECT를 보낸 뒤 같은 tunnel에서 기존 native TLS의 hostname·SNI·인증서 검증을 수행한다. 요청 bytes/header와 streaming 응답을 유지하며 redirect·retry·재연결·대체 경로를 제공하지 않는다. 준비 중 취소, 부분 응답, 시간초과 또는 연결 오류가 나면 해당 transport의 후속 요청을 거절한다.

신뢰된 controller가 한 번 고정한 public 대상에 연결하고, journal send 예약을 확인한 뒤 연결된 TCP FD 한 개를 proxy에 전달한다. inherited channel과 커널 peer UID/PID, runtime PID·start·spec·nonce·candidate·anchor·예약을 함께 확인한다. controller는 복제 FD를 유지하여 runtime 종료·정지·오류 시 shutdown하고, proxy도 실제 부모 controller 종료 시 끝난다. runtime은 고정 UDS만 열 수 있고 proxy는 새 IP·DNS·UDS 연결을 열 수 없다. worker 권한은 이 변경으로 확대하지 않는다.

실행은 승인된 task materializer가 같은 process에서 생성한 `PreparedFdController`를 `run_live_command(..., fd_controller=...)`에 전달하는 경로를 사용한다. 단독 CLI에서 controller가 없으면 거절하며 자동 생성·DNS·권한 fallback을 하지 않는다. 역할별 OS 합성 검사는 실제 Rust UDS/TLS와 FD 전달·회수·차단 경로의 근거이며, 실제 candidate App Server와 provider 전체 연결의 완료 또는 H05/H10 수락을 대신하지 않는다.

## Public History Allocation Boundary

v42–v56의 `replacement_work`는 `synthetic-reference-a` / `synthetic-operations-guide-check`, v57은 `synthetic-reference-a-regression` / `synthetic-operations-guide-regression`이다. 이는 기존 private 실행 대상 식별자를 공개용 합성 값으로 바꾼 것이다. Python의 exact home/work 비교 대상이 달라지므로 단순 문구 변경이나 모든 동작의 보존을 뜻하지 않는다. 원래 실제 대상의 v42–v57 재실행 재현성은 이 공개 소스에서 보존되지 않으며, 원본 소스와 입력·결과는 별도로 보존한다.

기존 approval·receipt는 합성 대상의 새 실행 승인이 아니다. 해당 allocation의 고정 deadline은 모두 과거이며 정상 wall/continuous clock과 기존 budget guard에 따르면 새 실행 예산을 거부한다는 정적 근거가 있다. 이를 모든 환경의 실행 불가능성이나 새 live 거부 검증으로 주장하지 않는다. deadline·guard·부모 binding·v41과 그 밖의 allocation은 그대로 유지한다. 새 실행은 별도의 대상·입력·승인이 필요하다.

이번 공개 정리의 검증 범위는 Python 데이터 계약 3개, Python/Rust JSON literal의 정적 대응·허용 필드 비교와 문서 검사다. Rust compile/test·rebuild 및 native/live 실행은 수행하지 않는다. 기존 native PASS는 원본 후보의 증거이며 이 변경 후보에 승계하지 않는다. 실제 거부 경로는 새로 실행하지 않고 guard 미변경과 원본 검증 근거를 구분해 보고한다.
