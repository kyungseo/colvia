# FEAT-20261022-001 — Prepared Tool Plan Live Qualification

## Public Snapshot Notice

이 문서는 비공개 원본에서 식별 정보만 중립화한 공개 파생물이다. 원본이 과거 승인·리뷰·실행 기록의 기준이며 별도로 보존돼 있다. `[공개용 중립화]` 표지가 있는 인용·본문과 그 표지가 붙은 code block은 원문 그대로가 아니다. 아래의 과거 `Verbatim` 표기도 이 제한을 따른다. 기존 SHA-256은 원본 bytes 기준이며 이 공개 사본의 digest나 새 승인으로 해석하지 않는다. 결과·실패·수락 범위·수치·미측정 한계는 원래 의미를 유지한다.

`Reference A`는 실제 외부 대상의 중립 표기다. 실행 데이터의 합성 ID는 `synthetic-reference-a` / `synthetic-operations-guide-check`, 회귀용은 `synthetic-reference-a-regression` / `synthetic-operations-guide-regression`이다. 표시용 branch `reference-a-guide-branch`, 문서 `docs/briefs/reference-a-operations-guide.md`, `private-evidence/E…` 및 `private-approval/O…` 표기는 공개된 실제 경로나 실행 승인이 아니다. private 원본과의 대응은 비공개로 보존한다. 기존 실제 대상 재실행은 원본에 대한 근거이며, 중립화한 소스의 새 native PASS가 아니다.

Status: Done. 승인된 U2 source/adapter qualification과 H10 첫 운영 가이드·Q1 보완을 Owner가 수락했다(2026-10-27). 확인 부담은 이번 검증에서 수용하며 시간 절감은 미측정이다. 최신 완료 판단은 문서 끝의 “Final Owner Acceptance And Work Done”이며 과거 기록은 당시 이력으로 보존한다. commit/push는 별도다.
actual_end: 2026-10-27
Owner: human Owner. Driver: Codex. Reviewer: fresh Claude CLI R0 및 integrated R1-01 완료; R1 model claude-opus-5-5, tools0.

## Purpose And Approved Boundary

기존 accepted offline prepared-tool-plan proof를 바탕으로, 기존 ChatGPT 구독 인증과 gpt-6-astra/xhigh를 사용하는 clock-only HTTPS 검증의 적격성을 판별한다. 일반 CLI 설치/교체, 실제 프로젝트 자료, U2 완료/Core/H05, 제품 Git publication 및 결과 수락은 제외한다.

2026-10-22 Owner 실행 승인: “보정 v2 실행 묶음 승인. L0 최대60분, 전체 최대8시간으로 진행하고 Keychain prompt는 거부·중단해.”

승인된 [v2 계획 및 R0 원문](prepared-tool-plan-live-qualification-plan.md)의 승인 시점 SHA-256은 1c817491c9e74ab1ff40d91b461dc002f68ff0f37ebbfe84ca84f0961d0940f7이다. 별도 private 실행 입력에 승인 원문 bytes를 보존했다. R0 REVISE와 필수13건의 Driver 계획 보정은 구분하며 보정 v2 재검토를 주장하지 않는다.

## Starting Inputs And Preservation

Source base: 83086188ae0614bd882818ff1aa23f3194962012. Accepted tracked binary diff SHA-256: 0f8bd8c87b73c564132c06edcdd5870decd3a951b6f1af3ffe3b671c02f4e00d; tracked21 + untracked2를 현재 source와 대조했다. 기존 두 binary와 필수 proof evidence는 유지한다. Source를 수정하기 전에 binary patch와 untracked 원문으로 최소 복구 bundle을 보존·검증한다. L0 동안 source를 바꾸지 않는다.

## Verification, Limits And Completion Criteria

L0: mode/sender/context/write-root/loader/retry의 exact call site와 수정 범위를 닫고 기존 proxy/HTTP factory/auth 경계가 승인된 범위로 가능한지 확인한다. unknown sender·범위 확대·권한 확대가 남거나60분이 지나면 unavailable로 중단하며 L1/실제 인증으로 진행하지 않는다.

L0 통과 시 승인 v2의 L1 구현 → L2 필수 negative/격리 canary/영향 fixture8 → L3 최소 live clock → L4 R1·보존/정리를 따른다. actual auth 전 모든 필수 negative PASS와 고정 endpoint/profile이 필요하다. Keychain prompt는 거부·중단한다. 최종 qualified/unavailable의 근거, source/build/send/dispatch 결속, mandatory 처분 및 Owner 결과 수락을 별개로 보고한다.

예상4–6시간은 낮은 신뢰의 판단값이다. 활동 시작2026-10-22 08:44:27 KST, L0 종료한도09:44:27 KST, 전체 종료한도16:44:27 KST. 총480분에 build·검사·reviewer 대기·기록을 포함하고 Owner 대기만 제외하며 마지막15분은 종료에 남긴다. 기존 U2/proof 장부는 변경하지 않는다.

상한: offline28 starts/56 threads/56 simulated turns, live2 starts/2 threads/2 turns(기본1, 필수 보정 후 최대1), proxy2 starts, generation2 sends/turn·4 total, control4 sends/start·8 total, auth refresh/relogin0, 보정2묶음, fresh R1최대2회·각15분. 숨은 retry/fallback0. 최초 rebuild 적격 판별90분. 단계 전환 재승인은 요구하지 않는다.

## Current Evidence And Next Action

L0 시작. 승인 입력/source drift 확인 완료. 실제 credential 조회·build·runtime·provider·reviewer 호출0. 먼저 proxy/HTTP 경계의 정적 연결 가능성을 확인한다. 모든 상세 진행은 이 문서가 소유한다.

## Owner Pause And L0 Checkpoint — 2026-10-22

Owner는 “잠깐 멈춰서 얘기하고 다시 진행하자.”로 실행을 중지했다. 추가 source 범위 질문에 대한 승인은 아직 없다. 재개 지시 전 구현·검사·auth·network·reviewer 호출을 진행하지 않는다.

정적 발견: 고정 reqwest0.12.28의 retry.rs 기본 정책은 ProtocolNacks이며 request당 추가 retry2를 허용한다. async_impl/client.rs의 내부 Retry service는 공통 HttpClient wrapper보다 아래에 있다. 현재 http-client/src/client_builder.rs의 base_reqwest_builder는 이 정책을 끄지 않고 public builder에도 retry 제한 setter가 없다. 따라서 상위 final-request guard/counter만으로 실제 HTTP 재전송0을 증명할 수 없다. 이는 source 확인이며 실제 재전송 재현 결과가 아니다.

제안한 최소 추가 경로는 http-client/src/client_builder.rs와 직접 대응 tests다. live mode에서 reqwest::retry::never()를 적용하고 ordinary 기본 동작은 유지하는 후보이며 아직 수정하지 않았다. 나머지 L0 call-site/권한 표가 모두 닫혔다거나 L0가 통과됐다고 주장하지 않는다.

중지 시 누적 활동 7.69분, L0 잔여 52.31분, 전체 잔여 472.31분이다. Owner 논의 대기는 제외하며 재개 때 누적 사용량을 초기화하지 않는다. 코드 수정0, build0, offline/live runtime0, credential 조회0, provider/control HTTP0, proxy0, R1호출0이다. 실행한 장기 process는 없다.

보존: 승인 v2 exact 원문·실행 승인/상한·pause/checkpoint 및 기존 accepted source/binaries/evidence. source full binary diff와 untracked2 원문 digest는 accepted 값과 동일함을 다시 확인했다. source 수정 전이므로 새 recovery source 복사나 build cache는 만들지 않았다. 기존 active 경로 변경·삭제0. 이 record와 private 실행 입력은 Owner 논의 및 재개의 consumer가 있어 유지한다.

## Decision Checkpoint Before L0 Resumption — 2026-10-22

Owner는 현재 단계·누적 비용·재사용 범위·후속 비용의 짧은 재평가를 요청했고, 추가 review/full 검사 없이 정리 후 판단하도록 지시했다. L0 및 추가 builder 수정은 재개하지 않았다. 실행 중인 process가 없으므로 끝내야 할 build/검사가 없고 중지에 따른 미완성 실행 결과 손실도 없다. accepted source diff/untracked2 동일성을 다시 확인했고 기존 두 binary와 승인 원문·실행 기록은 읽을 수 있다. source 변경·새 build/cache·review/full 실행0, 경로 변경·삭제0이다. 현재 evidence/source/toolchain은 결과 판단과 구체 재개 입력으로 보존한다.

### Current State And Distinct Accounting

- 기존 U2 source A: 미완료·중단, 누적163.03분. 제한된 admission/classifier와 OS canary 근거만 있으며 H01–H09 전체 검증은 미완료다.
- Offline proof: 구현·집중검사·최종8 cases·R1 필수0·Owner 수락·승인 cleanup 완료, 누적157.52분. prepared snapshot/단회 handle/tool envelope/handler binding/최종 serialized body 검사와 clock dispatch의 합성 검증이다.
- Live 계획/R0: 계획7.42분 + R0/처분12.42분 =19.84분. R0 REVISE, Driver v2 보정·Owner 실행 승인. 실제 구현 검증의 PASS가 아니다.
- Live 실행: 중지 당시7.69분, 이번 재평가 2.32분을 보수적으로 L0와 전체480분에 더해 현재 10.01분. 네 장부의 중복 없는 총 활동은 350.40분이다. build·test·review 대기는 포함하고 Owner 응답만 기다린 시간은 제외한다. 종전 장부는 초기화하지 않는다.

### Reuse And Remaining Implementation

| 구분 | 재사용/잔여 |
| --- | --- |
| 그대로 유지할 기반 | prepared snapshot, 단회 consume, tool envelope와 handler binding, drift/reuse 거절, experimental protocol, observer·집중 negative 구조. 변하지 않은 검사 결과는 재사용 |
| 확장·재결속 필요 | auth/policy/model identity, 실제 최종 송신 bytes/header guard, 새 executable/profile identity. 공통 bootstrap/client 변경 영향이 있는 fixture8만 재실행; unchanged collision/protocol/schema evidence는 재사용 |
| fixture 전용 | 가짜 model transport, proof-model, 정책을 무시하는 offline bootstrap은 테스트 입력으로만 유지. live 인증/정책/transport 구현의 대체품이 아님 |
| live에서 아직 신규 | read-only native auth, mandatory policy, proxy/OS egress, retry0·control/send counter·privacy guard. 현재 live source 구현0 |
| U2에서 여전히 신규 | 실제 작업 도구/worker 격리, host와 Core grant/ticket 연결, exact payload/한 번 사용·revoke/Owner 복구, 같은 Work 반복·재개. clock handler와 process-local handle은 Core 승인이나 실제 worker 경계를 대신하지 않음 |

전체23파일을 다시 쓰는 계획은 아니다. 다만 clock-only 검증 성공을 U2 adapter/worker 완료로 환산할 근거도 없다. 기존 코드는 유지하되 새 경계의 영향 부분을 구현·검증해야 한다.

### Prospective Cost And Recommendation

현 live 묶음을 끝까지 계속할 경우 남은 예상은240–360분(4–6시간), 낮은 신뢰의 판단값을 유지한다. L0가 아직 끝나지 않았고 auth/proxy/mandatory policy가 미검증이므로 초기7분만큼 기계적으로 단축하지 않는다. 캐시 삭제 후 재compile45–75분, focused/영향 fixture·live 최소1턴·R1/종료를 포함한다. 추가 새 scope나 적격 실패 시 이 예상은 폐기하고 중단한다. 현재 L0 잔여 49.99분, 전체 중단한도 잔여 469.99분이며 마지막15분 종료 여유를 포함한다. 상한은 예상시간이나 완료 보장이 아니다.

Live 성공 이후 U2는 source 통합/host H01–H05 90–150분, H06–H09 45–75분, 필요한 최종 normal/O 회귀125–145분, R1/정리30–45분, 실제 H10 60–90분으로 총350–505분(약6–8.5시간)을 임시 판단한다. 회귀만 기존117.53분(과거 실패한 pair)의 시간 근거에 여유를 더한 값이고 나머지는 미측정 판단이다. 기존 유효 근거는 재사용하며 불필요한 full 반복은 포함하지 않는다. Owner 승인 응답 대기·배포/publication·다른 OS·Core 재설계는 제외한다. H05 실제 exact-ticket 승인과 H10 실제 대상 승인은 여전히 필요하다. 이 추정은 새 상한/실행 승인이 아니다. 기존 U2 잔여436.97분과 host 잔여 약63.88분에 상한 쪽 추정이 들어맞지 않으므로 예전 예산으로 완주한다고 약속하지 않는다.

권고는 범위 축소다. 현재는 paused를 유지하고, Owner가 재개를 선택해도 우선 기존 잔여 L0 안에서 경계·재사용·필수 수정 목록만 닫는 것으로 다음 실행 단위를 한정하는 안을 제안한다. 그 결과를 보고 clock-only live 구현과 U2 필수 통합을 함께 설계할지 결정한다. 지금 전체 live를 진행하면 추가4–6시간 뒤에도 U2에 약6–8.5시간이 남는 반면, 현재 중단에는 새 코드/실행 결과 손실이 없다. 안전/수락 기준을 낮추거나 추가 리뷰·전체 검사를 이 재평가에 붙이지 않는다.

다음 결정 전 L1/build/auth/network로 넘어가지 않는다. 이 권고 자체를 Owner의 범위 변경 수락으로 기록하지 않는다.

## L0 Static Outcome And Integrated U2 Proposal — 2026-10-22

Owner는 “L0 판별까지만”, “남은50분 안”, “구현·빌드·실제 인증은 시작하지 말고 결과 보고 후 멈춰”로 범위를 좁혔다. 이 지시가 앞의 L0 이후 자동 L1–L4 진행보다 우선한다. 이번 결과는 정적 source 판별과 통합안이며 구현 승인·실행 적격·Owner 결과 수락이 아니다.

### Decision

판정은 기존 clock-only v2 그대로의 L1 진행에 대해 No-Go다. 재사용 기반은 확인했으나 필수 수정 경로가 기존 목록 밖에도 있고, clock-only 제한을 그대로 두면 U2의 실제 도구·worker·권한 연결을 사용할 수 없다. 전체 reachable sender와 OS 권한이 이미 닫혔다는 Go도 발급하지 않는다. 이 결과는 기존 offline proof의 실패나 해당 host 전체의 불가능 판정이 아니다.

권고는 clock live를 별도 완제품처럼 먼저 끝내지 않고, 공통 live 연결과 좁은 U2 문서 host를 한 candidate에서 구현·검증하는 것이다. clock은 그 candidate의 첫 live smoke로 남긴다. 실제 프로젝트 자료를 보내는 단계는 synthetic 통합 검증 및 해당 대상 승인 뒤다.

### Smallest Useful Boundary

```text
Owner의 기존 Work/intent/grant
            |
신뢰된 U2 host ── 기존 Core의 submit/prepare/apply
   |        |       exact ticket·fresh state·1회 사용·revoke
   |        |
   |        └── 문서 worker: 승인 파일만 읽기/쓰기, auth·network·Core 쓰기 없음
   |
   └── candidate runtime: prepared 검증 + native auth + guarded HTTPS
            └── 기존 CONNECT proxy: 허용 목적지만, TLS 해독 없음
```

runtime의 provider 통신 권한과 문서 worker의 권한을 분리한다. runtime에는 일반 shell/native filesystem/MCP/plugin/subagent 도구를 노출하지 않는다. host가 검증된 dynamic callback만 받고, 문서 처리는 별도의 고정 worker 작업으로 실행한다. 이 host는 기존 Core와 같은 trusted local account 경계이며 actor 문자열을 인증 수단이라고 주장하지 않는다.

작업 지속성의 단위는 같은 Work다. 최소안에서는 단계마다 새 ephemeral thread와 새 prepared handle을 사용한다. 한 turn의 도구 effect1회·generation 최대2회라는 기존 한계를 유지하고, 임의 길이 multi-tool turn이나 persisted model-history 복구를 추가하지 않는다. 필요한 문서/직전 결과만 host가 허용된 입력으로 다시 결속한다. 새 thread·process를 만들더라도 Work의 누적 시간·시도·사용한 ticket은 초기화하지 않는다. 중단한 process-local handle은 재사용하지 않는다.

### Confirmed Reuse And Required Changes

| 경계 | 재사용할 것 | 반드시 바꿀 것 / 판별 근거 |
| --- | --- | --- |
| prepared primitive | snapshot, handle 선소비, 매 step envelope·handler 검사, dispatch 전 reservation, drift/reuse 거절 | clock 전용 이름·빈 인자·mock completion을 profile별 검증/실제 종료로 분리. `core/src/session/prepared.rs:266,299,349,407,554,609,820` |
| runtime mode | ordinary와 fixture의 기존 의미 | process 시작 시 Ordinary/OfflineFixture/Live 고정; clock/U2 tool profile은 별도 immutable 값. 현재 boolean 분기의 mock·정책 우회가 Live로 들어오지 않게 분리 |
| U2 tool 노출 | 기존 dynamic tool protocol과 handler forwarding | `spec_plan.rs:148`와 `session.rs:816`의 dynamic 전면 거절을 exact U2 profile에서만 허용. model의 search 지원 metadata와 실제 허용 도구를 구분하며 native search는 계속 배제 |
| host callback | `DynamicToolCallParams`의 threadId/turnId/callId/namespace/tool/arguments; 기존 forwarding | runtime registry의 generic dynamic handler identity만으로 외부 host 구현까지 결속되지 않음. host/worker 코드·schema·profile·launch identity와 exact callback을 함께 검증 |
| 실제 HTTP | native provider/auth·encoder·기존 route-aware pool·CONNECT proxy | 최종 headers/bytes 검사, durable send 예약, redirect/retry/TLS fallback 차단, actual response 최소 수집. proxy tunnel 수는 HTTP send 수의 대용이 아님 |
| Core authority | 현재 ordinary isolated-worker grant, submit/prepare/apply, writer guard·fresh-state·revoke·exact replay | Core schema/규칙 변경0. host가 target/actor/action/Work/revision/result/evidence를 소유하고 opaque accept handle만 모델에 제공 |
| 반복·복구 | 기존 Work narrative, H01–H10 및 V22/V23/V26 의미 | host의 step dispatch·예산·중단·종료·pending ticket 보존 구현. prepared handle을 Core ticket이나 위임 승인으로 바꾸지 않음 |

Core source 확인: `src/hv2ref/work.py:759,914–932,1573,1601–1657`. prepare가 만든 조건은 apply의 writer guard 안에서 다시 확인된다. 완료된 exact ticket의 과거 replay는 current를 다시 올리지 않는다. 이 의미는 유지하며 host의 timeout 뒤 임의 새 ticket 생성/자동 apply 재시도를 금지한다.

### Source Findings That Change The Minimum Scope

1. HTTP 내부 retry: `http-client/src/client_builder.rs:359`는 reqwest 기본 retry를 끄지 않는다. pinned reqwest0.12.28의 ProtocolNacks 추가 retry2는 상위 guard 아래에 있다. live-only `retry::never()` 전달과 직접 대응 검사가 필수다. 실제 재전송을 실행·재현한 결과는 아니다.
2. 최종 guard 위치: `http-client/src/transport.rs:76–114`가 body를 준비하지만 `http-client/src/client.rs:162–169`에서 default/trace headers가 더 붙는다. guard는 이 추가 변환 뒤, 내부 execute 앞이어야 한다. live builder를 route-aware pool로 넘기고 TLS fallback을 활성화하지 않으며 redirect를 Reject로 고정한다. `route_aware_client_pool.rs:280`의 공개 builder 주입을 재사용할 수 있다.
3. cloud policy: `cloud-config/src/bundle_loader.rs:100–141`의 without-cache 경로는 getter마다 fetch하고 별도 AuthManager를 만든다. without-cache만 선택해서 단회 조회·공통 read-only auth가 성립하지 않는다. admitted AuthManager와 guarded backend를 전달하고, 검증된 bundle을 한 번 읽어 고정하는 좁은 진입점이 필요하다. service의 retry/auth recovery/background/cache 정책도 함께 제한한다.
4. model catalog: `models-manager/src/manager.rs:500–540`는 refresh 실패를 기록하고 기존 catalog/fallback을 쓸 수 있다. live admission을 이 best-effort 결과만으로 판단하지 않는다. native models endpoint의 성공 응답과 실제 auth identity를 단회 결속한 뒤 공개 `StaticModelsManager::new`를 사용한다. static manager의 etag refresh는 no-op이다. `model-provider/src/models_endpoint.rs:91–202,272–290`의 transport 생성도 strict builder를 받도록 연결해야 한다.
5. auth의 숨은 write/stale: `login/src/auth/manager.rs:2393–2419`는 refresh 실패 뒤 기존 auth를 반환할 수 있다. read-only 실패 정책은 auth_cached/auth/factory/agent-identity/reload/recovery/store 전체에 적용해야 한다. `login/src/auth/storage.rs:387` → `secrets/src/local.rs:131,197,259`의 load도 passphrase가 없으면 keyring save를 시도할 수 있으므로, storage의 save/delete만 막는 것으로 부족하다. 주입된 KeyringStore의 load-only wrapper로 해당 save/delete까지 거절한다. 기존 계정의 실제 backend·만료·Keychain prompt는 이번에 조회하지 않았다.
6. host는 아직 preflight다: `verification/u2-host/host.py:43,81,287,318`은 child env 전체를 상속하고 모든 server request를 거절하며, CLI command도 preflight 하나뿐이다. verify/accept schema가 있다는 사실은 구현 증거가 아니다. 이전 F1/F2/F3/F6/F8/F10/F11/F12의 필요한 보정은 통합 scope에 남는다.
7. live 종료: 현재 `prepared.rs:820–879`의 요청2회·완료 표시는 mock response 생성에 속한다. 이를 실제 send reservation, tool response, turn 종료·cancel의 서로 다른 상태로 분리해야 한다. clock proof의 완료 flag를 live 성공 판정으로 재사용하지 않는다.

### Minimum Proposed File Boundary

아래는 다음 통합안의 수정 경계 제안이다. 지금 파일 수정 권한을 새로 받은 것으로 간주하지 않는다. 직접 대응 unit/fixture tests와 필요한 module 선언만 포함하며, 이 밖의 실행 module이 필요하면 변경 이유와 비용을 다시 제시한다.

| 묶음 | 경로 및 목적 |
| --- | --- |
| 기존 v2 공통 경계 | 이미 명시한 app-server entry/lib/message_processor/config_manager/turn_processor, core client/config/session/prepared/turn/turn_context/tool spec/router/registry/context/environment_context/turn_metadata, login auth manager/storage, http-client transport/client/request, codex-api endpoint/session, backend-client client. 실제로 필요한 경로만 수정하며 모두를 재작성하지 않음 |
| v2보다 추가가 필요한 최소 경로 | `codex-rs/http-client/src/client_builder.rs`; `codex-rs/cloud-config/src/bundle_loader.rs`, `backend.rs`; `codex-rs/model-provider/src/models_endpoint.rs`, 필요한 `lib.rs` 노출. 앞의 source findings에 직접 대응. cloud-config lib/service는 v2 목록에 이미 있었음 |
| U2 runtime 연결 | 기존 prepared/profile/manifest와 `app-server-protocol/src/protocol/v2/turn.rs`의 experimental 경계. dynamic 전달 protocol 자체는 유지하며 `core/src/tools/handlers/dynamic.rs`, `app-server/src/bespoke_event_handling.rs`, `dynamic_tools.rs`는 우선 기존 경로 재사용·경계 검사 대상으로 둠 |
| U2 host/worker | 기존 `docs/development/verification/u2-host/host.py`, README, `tests/test_u2_host.py`, `tests/fixtures/u2_host.py`; 같은 host 디렉터리의 좁은 `worker.py`, `tool-profile.json` 신규 제안. task launch/profile/canary/evidence는 기존 private durable task 경로 사용 |
| 유지 / 범위 밖 | authority Core source/schema, managed adapter/runtime inventory, 일반 CLI 설치본, 기존 auth 저장소 내용, network-proxy의 제품 의미, 새 proxy/broker/범용 scheduler·queue·executor. 이 변경이 필요하면 통합안도 중단 |

U2 최소 도구는 문서 read/write, 고정 verify, sealed accept의 네 종류로 제한한다. read/write는 host가 고정한 file ID만 받고 임의 path/command를 받지 않는다. write는 expected prior digest와 제한된 UTF-8 전체 내용 교체로 한정하여 별도 patch 언어/범용 shell을 추가하지 않는다. 실제 byte 상한·허용 파일 목록·원자적 교체용 경로는 대상 실행 입력에 고정한다. symlink/alias·변경된 prior bytes·범위 밖 파일은 거절한다. worker는 auth/home/Core/managed runtime/Git 관리 경로에 접근·쓰기 권한을 받지 않으며 network와 임의 child 실행도 거절한다.

DOC-LINKS/GFM/CLAIMS는 host가 고정한 verifier ID로만 선택한다. CLAIMS의 정적 참조 확인을 문서 전체 사실성의 자동 증명으로 부르지 않고 H10의 실제 내용 판정은 유지한다. host는 검증된 결과·evidence를 기존 submit 경로에 결속한 후 Core prepare의 원 ticket을 보존하고, 해당 grant에 맞는 accept handle을 발급한다. callback은 admitted thread/turn/call/schema·host identity·현재 grant/result를 검증하고 효과 전에 사용을 예약한다. 뒤늦은 callback/중복/연결 교체는 실패로 끝낸다.

### Runtime Roots, Senders And Remaining Qualification

읽기 경계는 원 auth home의 native credential 참조, 필요한 native user/system/managed/MDM/exec-policy 입력, pinned executable/runtime 및 해당 단계의 승인 문서 입력이다. 쓰기는 task runtime home/log/sqlite/cache/rollout/history/lock/installation-metadata와 worker의 exact 결과 경로로 분리한다. 원 auth home은 write-deny다. config의 별도 `log_dir`, `sqlite_home` 및 환경 override를 runtime home과 같은 것으로 가정하지 않는다(`core/src/config/mod.rs:989–1003,4205–4221`). source context 수집과 mandatory policy 읽기는 별개다.

송신 허용은 generation과 명시적 policy/model control 요청뿐이다. app-server lib의 OTel provider 생성·metrics, analytics, remote-control 및 message_processor의 models-refresh/cost worker는 Live에서 생성/시작을 막는다. analytics에는 기존 `AnalyticsEventsClient::disabled()`를 재사용할 수 있다. app-server entry의 plugin-startup skip, strict request admission과 session의 skills/hooks/child 제한을 유지한다. auth refresh/agent identity/WS/prewarm/compaction/background와 다른 sender는 실패로 끝내야 한다. 이번 정적 조회를 전체 프로그램의 unknown-sender0 실행 증명으로 올리지 않는다.

네트워크는 runtime→고정 loopback proxy→고정 first-party 목적지만 허용한다. existing proxy의 Full은 CONNECT tunnel을 위해 필요하지만 destination allowlist, SOCKS/UDP/upstream/local-destination 제한을 별도로 고정해야 한다. worker는 loopback도 허용하지 않는다. same-host auth path는 CONNECT proxy가 구별하지 못하므로 native auth와 final HTTP guard가 차단한다. runtime DNS/direct IPv4·IPv6/alternate proxy와 helper DNS는 서로 다른 검사 대상이다.

미완료 gate는 (a) 모든 strict constructor와 금지 sender의 연결·negative 결과, (b) 정확한 OS read/write/mach/network profile과 실제 canary, (c) 실제 native 저장소·정책·모델·계정 적격성이다. 필요한 Keychain mach 서비스가 현재 경계로 충분한지 또는 추가 권한이 필요한지 실행 근거가 없으며 wildcard 허용으로 채우지 않는다. Keychain prompt는 거부·중단한다. 이 미완료 항목을 통합안 채택이나 synthetic PASS로 면제하지 않는다.

### Combined Sequence And Evidence Selection

1. 변경된 경계만 반영한 실행 입력을 고정한다. 위 추가 경로, host/worker schema·identity, process별 OS 경계, control/generation 및 전체 U2 누적 상한을 한 묶음으로 둔다. 기존 clock의 live2 turns/4 generation sends는 전체 U2 예산으로 사용할 수 없다. 변경 scope에 필요한 계획 검토는 기존 R0 절차를 따르되 이번 L0에서 추가 reviewer를 부르지 않는다.
2. 공통 live 연결과 U2 profile/host를 함께 구현한다. auth/transport는 fake store·local synthetic 입력으로 먼저 확인한다. host는 callback spoof/duplicate·ticket binding·revoke·result drift·cleanup과 worker OS canary를 집중 검사한다. 모든 수정이 모인 candidate에서 최초 build와 영향받은 fixture8을 수행한다. L0에서는 수행하지 않는다.
3. 같은 candidate로 live clock smoke → synthetic U2 read/write/verify·같은 Work 반복/중단/재개 → H01–H09와 최종 normal/parent-O → 통합 결과 R1 순으로 판정한다. H05의 원 delegated ticket에 대한 Owner 복구 승인은 그대로 유지한다. H10 실제 대상·전달 범위 승인과 실제 문서 결과/Owner 관측은 별도 gate다. 소스 결과와 실제 업무 수락을 합치지 않는다.

변하지 않은 Core 계약·accepted proof의 충돌/프로토콜 근거는 식별된 원 evidence로 재사용한다. dynamic tool profile과 live auth/HTTP·mode·공통 bootstrap은 변경 영향 검사 대상이다. 새로운 권한 연결/복구와 기존 unexplained full-run 실패 때문에 U2의 최종 normal/parent-O 각1회 의무는 유지한다. clock용 full suite를 따로 추가하지 않고, candidate 이름/digest만 바뀌었다고 green 전체 검사를 반복하지 않는다. 최초 build를 한 번으로 모으되 실제 결함 보정이 필요하면 추가 build가 생길 수 있으므로 “항상1회 완료”를 보장하지 않는다.

### Cost And Stop State

통합의 목적은 공통 연결·candidate·fixture·최종 review를 재사용하는 것이다. 절감 시간을 실측한 것은 아니다. 현재 근거로 후속 전체 예상은 기존 live240–360분 + U2 350–505분 =590–865분, 약10–14.5시간을 보수적 계획값으로 유지한다. 구현·cold build45–75분·집중검사·필요 회귀·review 대기·정리를 포함한다. Owner만 기다리는 시간은 제외하고 겹치는 실행은 wall time 한 번으로 센다. 회귀의 과거117.53분 외에는 주로 판단값이며 기존 실패 실행을 PASS로 재사용하지 않는다. 추가 scope/권한이나 첫 build 적격 실패가 발생하면 이 예상을 폐기한다.

기존 전체8시간은 완료 예상이 아니라 중단 상한이고 현재 L0-only 지시 이후 실행 권한은 중지돼 있다. 위10–14.5시간은 새 상한 승인이나 이미 사용한 장부의 초기화가 아니다. 통합안을 선택하더라도 기존 U2/live/host 장부를 연결하고 실제 첫 build·negative 소요로 남은 비용을 다시 계산해야 한다.

이번에는 source 구현·build·actual auth·provider/control HTTP·proxy·offline/live runtime·추가 reviewer·전체 테스트를 시작하지 않았다. 기존23파일의 tracked binary diff와 untracked2 digest가 accepted 값과 같음을 확인했다. 추가 기록은 이 source record와 기존 private execution metadata뿐이다. 실행 중인 task process0, 경로 변경0, 삭제0이다. accepted source/binaries/evidence와 이번 판별 기록은 통합안 선택 및 후속 구현의 입력으로 유지하며, 결과 수락 또는 해당 후속안의 명시적 폐기 시 보존 목적을 재판정한다.

정적 판별 checkpoint: 2026-10-22T00:15:59.147868+00:00; 이번 L0-only 활동 11.59분, live/L0 누적 21.59분, L0 잔여 38.41분, live480분 장부 잔여 458.41분. 이전 장부와 합한 중복 없는 활동은 361.99분이다. 종료 확인/보고에 사용한 시간은 최종 closeout에서 더하며 사용량을 초기화하지 않는다.

최종 closeout 2026-10-22T00:16:38.321348+00:00: 이번 활동 12.24분, L0/live 누적 22.25분, L0 잔여 37.75분, 전체 장부 잔여 457.75분, 선행 장부 포함 총 활동 362.64분. 결과 기록 읽기·문서 whitespace·두 checkout diff check·accepted source 동일성 확인을 마쳤다. 새 구현/실행0을 유지하고 보고 후 정지한다.


## Integrated Execution Planning — 2026-10-22

Owner는 U2 최종 목표와 H01–H10 기준·품질·범위를 유지하면서 live 연결과 U2를 묶는 방향을 선택하고, 중복을 줄인 구체 실행안·단계별 예상·중단 상한을 요청했다. 구현은 실행안을 보고 승인한 뒤 시작하도록 명시했다.

[통합 실행 제안](u2-live-integrated-execution-plan.md)을 작성했다. 원 H01–H10과 실제5문서·H05 exact replay·H10 candidate commit/실제 결과/Owner 관측을 유지한다. 정상 수행은 같은 thread의 문맥을 유지하면서 turn마다 새 prepared handle을 쓰고 native history identity를 결속한다. L0의 매 단계 fresh-thread 제안은 필수 설계로 채택하지 않았으며, 재시작 때만 Work checkpoint에서 문맥과 누적 사용량을 복구한다. 이에 필요한 history negative를 기존 prepared/U2 검사 범위에 포함했다.

후속 예상605–870분(10시간5분–14시간30분), 후속 중단 상한960분 제안이다. 기존 U2/live 사용185.28분을 남겨 연결 누적 상한1145.28분으로 표시하며 기존600/480/host120분을 초기화하거나 현 잔여 내 완주를 주장하지 않는다. 최종20분은 종료에 남긴다. source 절차의 R0→실행 승인→구현→R1→결과 수락을 유지하므로 이번에는 reviewer도 호출하지 않았다. 계획의 단계/시도/권한/후속 handoff는 모두 제안이며 아직 활성화되지 않았다.

공통 auth/HTTP/policy/model 구현, 한 candidate build, 영향 fixture8, 동등한 common negative receipt와 최종 통합 R1을 공유한다. Core/host/worker/profile이 다른 검사는 동일하다고 간주하지 않으며 Colvia normal/parent-O 각1회와 실제 H10은 유지한다. 실제 입력이 아직 없어야 하는 ticket/target/commit 승인도 미리 받은 것으로 처리하지 않는다.

계획 SHA-256: e9cb82f8db96da562d363f06facdc03475b24094705343a9e870d4a08c82681c. 계획 checkpoint 2026-10-22T00:30:24.581152+00:00, 이번 작성 활동 9.09분. 기존 실행 장부 사용량은 변경하지 않았으며 이번 계획 작성은 별도로 계상한다. 구현/build/auth/model/reviewer/test 실행0, 기존 source patch·binary 유지, 경로 변경/삭제0이다.

통합 계획 closeout 2026-10-22T00:31:19.069076+00:00: 작성/검사 10.00분. 시간 합계605–870분·전체상한960분, H01–H10 참조, local link 존재/whitespace, 두 checkout diff check와 accepted source 동일성을 확인했다. 실행 사용량은 그대로이며 계획의 R0 호출·구현 승인은 대기한다.

## Integrated R0 Authorization And Egress Block — 2026-10-22

Owner는 통합안 R0 1회와 필수 계획 보정을 승인했고 H01–H10/실제5문서를 유지하며 구현은 최종 실행안 승인 뒤에만 시작하도록 지시했다. 통합안 전체, 기존 완료/복구 계약, 앞선 R0 필수 보정과 필요한 source 발췌를 한 비식별 packet으로 고정했다. 실제 대상5문서 본문·계정·절대 로컬 경로는 포함하지 않았다. packet98,424bytes, SHA-256 `0955fa35c320d4e0da080f1a4f12094ea49c92f10b8514d892853d8b5c7faf38`; 통합안 원 입력 SHA-256 `e9cb82f8db96da562d363f06facdc03475b24094705343a9e870d4a08c82681c`.

자동 승인 검토가 준비된 CLI의 실행을 거부했다. 사유는 로컬 source/실행계획이 민감할 수 있고, R0 승인만으로 해당 payload를 Claude 외부 서비스에 전송하는 권한이 구체적으로 확인되지 않았다는 것이다. 실제 CLI/auth-status 호출·외부 전송·reviewer 응답 모두0이다. 우회/재시도하지 않았으며 exact packet과 destination 전송 승인 대기다. R0가 완료되거나 통과한 것으로 처리하지 않는다. source 구현/build/runtime auth/model 호출0, 최종 실행안 보정 미착수다.

기존 private task 경로의 `live-qualification/integrated-r0`에 packet·controller·metadata를 보존한다. 소비자는 Owner의 exact 전송 판단과 승인 시 R0이며, 이 판단 전에는 삭제하지 않는다. active 경로 변경/삭제0. 이번 준비·차단 처리 시간은 metadata의 별도 R0 활동 장부에 남기고 기존 U2/live 사용량을 초기화하지 않는다.

## Integrated R0 Result And Driver Corrections — 2026-10-22

### Owner Authorization, Input And Actual Execution

Owner는 고정 검토 입력을 Claude 외부 서비스에 전송하는 정적 R0 1회를 명시 승인했다. 앞의 자동 승인 차단 뒤 동일 packet의 SHA/bytes를 확인하고 실행했다. 목적은 live/U2 통합 경계의 계획 검토였고 H01–H10과 실제5문서 범위를 유지했다. 실제 대상 본문·계정·절대 로컬 경로는 packet에 없었다. source base/diff/untracked와7개 input 파일 identity를 private metadata에 고정했다. 이전 차단 기록을 추가한 자체 변경은 원 발췌 bytes 무변경을 대조한 뒤 처분했으며 실행 전후 unexplained drift는0이다.

- Reviewer: Claude `claude-opus-5-5`, fresh session `bc8dcda2-c726-4c9f-aaa6-9c77351a491f`. Driver: Codex. 별도 모델/세션의 정적 검토이며 Driver가 제공한 bounded 자료에 의존한다.
- 인증/과금: 호출 전 `loggedIn=true`, `authMethod=claude.ai`, `apiProvider=firstParty`, `subscriptionType=pro` 확인. override 존재 검사 모두false. 비밀값/계정 이메일 미기록. Reviewer가 인증 자체를 확인한 것은 아니며 Driver의 실행 관측이다.
- 실행: 직접 CLI print/safe-mode, tools 빈 목록, MCP 빈 목록, slash commands/browser 비활성, permission dontAsk/none, no-session-persistence, fresh session, effort high. stdin은 고정98,424bytes packet(SHA-256 `0955fa35c320d4e0da080f1a4f12094ea49c92f10b8514d892853d8b5c7faf38`). exact argv/runtime/cwd는 private metadata에 기록. CLI880초 제한, 총 S0 45분 우선.
- 실제 결과: 호출1회,242.285초, exit0, result success/turn1, tool use0, MCP0, timeout=false, process group 부재 확인, input drift0, stderr0bytes. 구현·build·runtime auth/model·실제 대상/Git 실행은0이다.
- 응답15,703bytes, SHA-256 `4f7fb6d1bc3c69ea62ee1bc54621930ad0cbdb937c8043f1301f62dce699f652`. 아래 원문을 bytes 대조해 가져왔으며 verdict REVISE를 유지한다.

### Driver Dispositions

필수13건과 선택3건을 [최종 실행안](u2-live-integrated-execution-plan.md)에 반영했다. 이는 계획 처분 완료이며 구현/test closure나 Reviewer 재검토 PASS가 아니다. 추가 R0를 호출하지 않았다. 원 H01–H10과 실제5문서·품질/Owner 부담 기준은 그대로다.

| ID | 처분 | 계획 보정 | 남은 실행 증거 |
| --- | --- | --- | --- |
| IR0-01 | accept | reset뿐 아니라 history 내용/개수/digest; gen2 허용 delta 및 최종 body 검증 | S1/S2; T-01 |
| IR0-02 | accept | parallel false; gen1 전체 수신 뒤 dispatch; 초과 call은 실패/thread 종료·이미 예약한 사용 유지 | S1/S2; T-01/T-02 |
| IR0-03 | revise | 고정 batch read≤8 IDs·64KiB, H10 8+5+3+16+1+7=40; exact bytes/context 사전 적격 | S2/S4/S6; T-07 |
| IR0-04 | accept | host 결정적 진행/복구 template, 신뢰 입력/digest·8item/64KiB, 수동 개입 별도 관측 | S2/S4; T-01/T-07 |
| IR0-05 | accept | 공통 durable phase/total journal·lock/fsync 예약; crash 소모·missing/corrupt fail | S1/S2/S4; H07 |
| IR0-06 | revise | phase별 start 배정, 봉인 전만 restart; 봉인 뒤 thread 소실은 H10 중단; accept 새 thread 금지 | S2/S4/S6; H07/H08 |
| IR0-07 | accept | 자동 metadata와 승인 문서 segment 원천 분리; candidate untrusted·정확한 전달 범위 유지 | S1/S2/S6; T-02 |
| IR0-08 | revise | 같은 device의 task scratch exact swap·literal rename·nlink/inode; verifier read-only 범위; 잔여 보존 | S2/S3/S6; T-04 |
| IR0-09 | accept | 별도 durable CARGO_TARGET_DIR; accepted binary 경로/bytes 전후 확인 | S3 |
| IR0-10 | accept | F-01–F-08 대응표·base/result tag·hook/identity·refs·actual-accept 순서 복원 | S2/S4/S6; T-02/T-08 |
| IR0-11 | revise | R0/처분 기사용을 S0로 carry; S0 정적 gate와 S3/S4 실행 gate 구분;45분 유지 | S0/S3/S4; T-03/T-05/T-06 |
| IR0-12 | accept | 만료/귀속 불명 변경 때 중단 후 Owner 재판단; 사이 refresh/relogin 자동 허용 없음 | S4/S6; T-03/T-07 |
| IR0-13 | accept | S4 실측 latency/context로 S6 시간 재산정; 실제 setup 부작용 전 적격 gate | S4/S6; T-07 |
| IR0-14 | accept | 이전 live 계획/R0 19.84와 이후 L0 22.25가 별도 구간임을 명시 | 장부 확인 |
| IR0-15 | accept | mode별 validate_config/config_snapshot; fixture 기존 의미 유지 | S1/S3; T-02/T-05/T-06 |
| IR0-16 | accept | proxy1=S4, proxy2=S6; 실패 시 숨은 새 start 없음 | S3/S4/S6 |

실행 전용 T-01–T-09는 미확인으로 남긴다. T-01 history=S1/S2/S4; T-02 tool/forwarding=S2/S3/S4; T-03 actual Keychain=S4; T-04 rename/alias=S3/S6; T-05 HTTP=S1/S3/S4; T-06 policy/model=S1/S3/S4; T-07 latency/context/auth=S4/S6; T-08 installed barrier/replay=S4; T-09 normal/O discovery·완료=S5다. accepted 기존 근거와 새 관측을 섞어 PASS로 올리지 않는다.

### Reviewer Response — Verbatim

``````text
# 통합 R0 정적 검토 — U2 및 Live 통합 실행안

## 0. 판정과 전제

- **판정: REVISE.** 아래 필수 13건(IR0-01–13)을 계획 문서에서 닫은 뒤 Owner 실행 승인을 판단할 수 있습니다.
  - 이 보정만을 이유로 추가 R0를 요구하지 않습니다. 보정 반영 여부는 Driver 처분과 R1이 확인합니다.
- **근거 범위:** 제공된 통합안, 원 H01–H10, F-01–F-08, M-01–M-13, L0 정적 결과, 그리고 `mod.rs`·`turn.rs`·`prepared.rs` 발췌만 읽었습니다.
  - 실행·빌드·테스트·브라우징은 하지 않았습니다.
  - 발췌 밖 line 번호와 call site는 확인하지 않았습니다.
- **판단하지 않은 것:** 이 검토는 Owner 수락, 구현 완료, 실현 가능성 확인, 일반 생산성 qualification을 뜻하지 않습니다.
- **기준 유지:** 원 H 기준, 대상 5문서, 권한·품질·Owner 부담 기준은 바꾸지 않았습니다. 더 쉬운 검사로 대체하자는 지적도 없습니다.

---

## 1. 승인 전 닫아야 할 계획 결함 (필수)

### IR0-01 [필수] history 결속의 정의가 부족합니다

**근거**
- `history_reset()`(mod.rs 발췌)은 `(reset_version, child_token)`만 반환합니다. 이는 reset 감지용 값입니다. append, 삽입, 주입된 항목 같은 내용 변화는 감지하지 못합니다.
- turn.rs 1766–1770을 보면, 첫 generation 뒤에는 prompt를 `clone_history().for_prompt()`로 다시 만듭니다. 따라서 두 번째 generation의 history는 정상적으로도 "gen1 출력 + tool call/output"만큼 달라집니다.
- 그 직후 `executed_tool_calls.attach_to_prompt`와 `prepare_guardian_prompt`가 prompt를 변형합니다.
- 계획의 "consume/매 send에서 불일치 거절"만으로는 둘 중 하나가 됩니다. 정상 gen2를 항상 거절하거나, 아니면 검사가 사실상 무의미해집니다.

**최소 보정**
1. prepare snapshot에 `reset_version`과 함께 prepare 시점 `for_prompt` 항목열의 digest와 개수를 결속합니다.
2. gen2에서 허용하는 delta를 "이 turn gen1의 출력 항목 + admitted call 1건의 output"으로 정확히 명시합니다. 그 밖의 delta, reset token 취소, guardian 경로 활성은 거절합니다.
3. `attach_to_prompt` 결과를 guard가 검사하는 최종 body에 포함시킵니다.

### IR0-02 [필수] dispatch·generation 한도를 넘는 모델 출력의 처리가 정의되지 않았습니다

**근거**
- 계획은 "dispatch 최대 1, generation 최대 2"만 정합니다.
- 다음 경우의 결과가 없습니다.
  - gen1에서 병렬 function call이 2건 이상 나오는 경우
  - gen2에서 다시 tool call이 나오는 경우
- output이 없는 function call이 history에 남으면, 같은 thread의 다음 turn 요청이 provider에서 거절될 수 있습니다. 이는 IR0-01과 같은 thread 설계에 직접 영향을 줍니다.

**최소 보정**
1. `parallel_tool_calls=false`를 고정합니다.
2. 초과 call에 대해 "dispatch 없는 고정 거절 output을 history에 기록하고 effect 0으로 둔다"와 "turn 실패 후 thread 종료" 중 하나를 정합니다.
3. 그 거절 output이 dispatch 1회로 세는지, 그리고 send·turn 예산에 어떻게 계상하는지 명시합니다.

### IR0-03 [필수] H10의 40 turn 상한이 1 dispatch/turn 구조와 맞는지 근거가 없습니다

**근거**
- 1 turn에서 효과가 있는 도구 호출은 최대 1건입니다.
- 이전 기록에는 대상 read 집합이 27이었습니다(F-08, "대상 read27").
- 최소 소요를 세면 다음과 같습니다. 정확한 수는 private입니다.

| 항목 | turn 수 |
| --- | ---: |
| read 27 | 27 |
| 5문서 read | 5 |
| 5문서 write | 5 |
| verify 3 | 3 |
| accept | 1 |
| **합계** | **41 이상** |

- 이는 보정 2묶음을 넣기 전에 이미 40을 넘습니다.
- 또한 compaction이 0이므로 같은 thread의 context가 계속 누적됩니다. 그런데도 window 한도 계산이 없습니다.

**최소 보정**
1. S0에서 실제 파일 수와 bytes로 turn·context 산정표를 만듭니다.
2. 맞지 않으면 다음 중 하나로 처리합니다.
   - read 도구가 고정 상한의 file-ID 목록을 한 번에 받도록 합니다. 이는 여전히 1 dispatch이고 고정 도구 4종을 유지합니다.
   - 대상 접근 전에 부적격으로 중단합니다.
3. 40을 조용히 늘리거나 read 집합을 줄이지 않습니다.

### IR0-04 [필수] turn 입력과 재시작 복구 packet의 작성 주체·형식·개인정보 경계가 없습니다

**근거**
- 같은 thread의 각 turn은 새 input과 함께 prepare해야 하지만, 그 input을 누가 작성하는지 정해져 있지 않습니다.
- Driver가 임의 문장으로 작성하면 H10의 "재설명·Owner 부담" 관측이 오염됩니다.
- 재시작 시 넣는 "승인·원 입력·현재 문서·직전 검증·누적 사용량"은 사실상 요약 packet입니다.
  - 원 명세에 따르면 worker narrative는 신뢰할 수 없습니다.
  - `prepare_tool_plan`에는 입력 제한(≤8 item, 각 ≤65536B, plain text)이 있습니다.
- 재송신되는 실제 문서는 H10 provider 전달 범위에 속해야 합니다.

**최소 보정**
1. 진행 input과 복구 packet은 host가 소유한 기록만으로 결정적 template을 만들어 사용합니다.
2. digest를 snapshot에 결속합니다.
3. Owner가 직접 쓴 메시지만 원문 그대로 추가할 수 있게 합니다.
4. 크기가 초과하면 부적격으로 중단하고, 절삭하지 않습니다.
5. 실제 경로·계정 정보는 넣지 않습니다.

### IR0-05 [필수] 재시작을 거쳐도 유지되는 예산 장부가 정의되지 않았습니다

**근거**
- 상한은 "fsync send reservation"과 "전체 108 sends / 54 turns / control 24"로 정해져 있습니다.
- 그러나 reservation counter가 process별인지 전체 공통인지 명시되지 않았습니다.
- H07은 "누적 시도 carry, budget 초기화 금지"를 요구합니다.

**최소 보정**
1. 모든 start가 같은 durable 장부를 이어서 쓴다고 명시합니다. 단위는 phase별이며 전체 합계도 함께 둡니다.
2. 예약 후 송신 전에 crash가 나면 그 예약은 소모로 계상합니다.
3. 장부가 손상되었거나 없으면 unavailable로 처리하고 0으로 초기화하지 않습니다.

### IR0-06 [필수] 2번째 start의 용도가 충돌합니다

**근거**
- synthetic과 H10은 각각 최대 2 start입니다.
- 2번째 start는 다음 세 가지 용도와 경쟁합니다.
  - H07이나 자연 발생 중단 뒤 재시작 carry
  - M-12의 필수 보정 후 재검정
  - F-02의 accept turn
- F-02는 "같은 thread에서 제한을 입증하지 못하면 새 thread로 자동 전환하지 않는다"고 정합니다. 그런데 통합안은 재시작 시 새 thread를 허용합니다. 따라서 재시작 뒤 accept가 허용되는지 불명확합니다.

**최소 보정**
1. phase별로 start·thread 용도를 미리 배정합니다.
2. 재시작 뒤 accept에 대해 다음 중 하나를 정합니다.
   - 봉인된 ticket에 host가 새 handle을 발급하고, 기존 handle은 무효화합니다.
   - 미완료로 중단합니다.
3. Owner의 commit 승인을 기다리는 동안 thread를 유지하는 조건을 명시합니다.

### IR0-07 [필수] 최종 privacy guard와 승인된 실제 문서 송신이 충돌합니다

**근거**
- M-08과 L2(6)은 final body에서 실제 path·git·계정 식별정보를 거절합니다.
- H10은 실제 문서 내용을 read·write 인자와 결과로 provider에 보냅니다. 문서 안에 경로나 이름이 들어 있으면 오탐으로 H10이 실패합니다. 반대로 예외 처리를 하면 누출 경로가 됩니다.

**최소 보정**
1. guard를 원천별로 나눕니다.
   - runtime이 주입하는 context·metadata·header는 내용 검사를 합니다.
   - host가 승인 file-ID와 digest로 제공한 문서 bytes는 provenance로 허용합니다.
2. 그 밖의 위치에 식별정보가 있으면 거절합니다.

### IR0-08 [필수] 원자적 교체와 verifier의 실제 OS 범위가 미정입니다

**근거**
- "원자적 교체용 경로"만 적혀 있습니다.
- rename 방식은 같은 volume의 임시 파일 생성 권한을 필요로 합니다.
  - worktree에 임시 파일이 남으면 whole-tree와 5파일 scope를 오염시킵니다.
- 원 명세는 "개별 파일 write·원자적 교체를 지원하지 못하면 H03 중단"이라고 정합니다.
- DOC-LINKS는 read allowlist 밖의 link 대상을 읽어야 할 수 있습니다. 그런데 verifier가 어느 process·profile에서 실행되는지 정해져 있지 않습니다.

**최소 보정**
1. 임시 경로를 고정 이름으로 정하고, 시작 전에 부재를 확인합니다.
2. Seatbelt literal 규칙에 생성·rename 권한을 명시합니다.
3. 임시 파일이 남으면 중단하고 보고하며, 자동 삭제하지 않습니다.
4. verifier의 실행 위치와 read 집합을 고정합니다.
5. 선택 사항: 파일 ID별로 `nlink==1`과 inode를 확인하고, hardlink alias canary를 H03에 추가합니다.

### IR0-09 [필수] build가 수락된 fixture binary를 덮어쓸 수 있습니다

**근거**
- build 명령이 cwd=`RUNTIME_SOURCE/codex-rs`의 기본 target dir에서 `codex-prepared-tool-plan-fixture`를 다시 빌드합니다.
- 이 경우 계획의 "기존 두 binary 유지"(fixture SHA df5e…)가 깨집니다.

**최소 보정**
- 다음 중 하나를 적용합니다.
  - durable task root 아래 별도 `CARGO_TARGET_DIR`을 지정합니다.
  - build 전에 기존 binary를 복사하고 digest를 대조합니다.

### IR0-10 [필수] F-01–F-08이 처분표와 Owner 판단 목록에서 빠졌습니다

**근거**
- 처분표 대상은 "M-01–13 + U2 미해결 findings"로만 되어 있습니다.
- "남는 Owner 판단" 목록에는 F-01의 base tag·worker setup 승인과 result tag가 없습니다. F-07 hook·identity 결속, F-08 required refs 비중첩도 명시되지 않았습니다.
- F-05는 runtime cwd를 WORKER로 전제했습니다. 통합안은 synthetic cwd와 별도 worker를 쓰므로, 대응 oracle을 다시 정해야 합니다.
- F-02(E07a/E07b와 쓰기 없는 accept turn)는 phase gate로 바뀌었는데, 대응 관계가 없습니다.

**최소 보정**
1. F-01–F-08을 coverage·처분표에 넣습니다.
2. S6 순서에 base tag → worker → 편집 → candidate 승인 → result tag → publish → accept를 명시합니다.
3. Owner 판단 목록을 원 범위로 되돌립니다. Owner 판단 축소는 금지입니다.

### IR0-11 [필수] S0 종료 기준과 시간 장부의 소유가 불명확합니다

**근거**
- S0(최대 45분)에는 "이 R0 + 정적 gate 종료"가 들어 있습니다. 그러나 같은 gate (a)(b)(c)는 L0에서 60분 상한 안에 No-Go로 끝났습니다.
- S0는 960분 승인보다 먼저 일어나는데도 960 안에 계상됩니다.
- 지금 진행 중인 이 R0의 시간이 어느 장부에 속하는지 정해져 있지 않습니다.

**최소 보정**
1. S0 Go/No-Go 표를 만듭니다. 정적으로 닫을 항목과 S3 실행 gate로 넘길 항목(OS canary, Keychain mach 등)을 구분합니다.
2. 이 R0와 처분 시간의 장부를 명시합니다. 사전 승인 장부와 S0 중 하나입니다.
3. S0를 넘기면 No-Go로 처리합니다.

### IR0-12 [필수] read-only 인증 만료 시 처리 규칙이 없습니다

**근거**
- refresh와 relogin은 0이고, O-05에 따라 외부 변경의 귀속이 불명확하면 불확정으로 처리합니다.
- S4 → S5(2–3시간) → S6 사이에 Owner 대기까지 겹치면 S6에서 인증이 유효할 근거가 없습니다.
- 계획은 "중단할 수 있다"고만 적었습니다. 이는 H10 가능성을 좌우하는 승인 경계입니다.

**최소 보정**
- 승인 전에 다음 중 하나를 결정합니다.
  - start와 start 사이에 Owner가 일반 설치 CLI로 갱신합니다. 이때 전후 비민감 metadata를 기록하고, runtime이 꺼져 있을 때만 허용합니다.
  - 만료 시 중단하고 Owner 재판단을 받습니다.

### IR0-13 [필수] S6의 부작용을 시작하기 전에 시간 적격성 gate가 필요합니다

**근거**
- S6의 예상은 60–90분, 상한은 120분입니다. 그 안에 대상 준비, intent·grant, 40 turn × 2 generation(xhigh), commit 승인, publish·accept가 모두 들어갑니다.
- turn당 15분 상한이므로 시간 상한이 먼저 걸릴 가능성이 큽니다.
- 그러면 base tag, worker, intent 같은 실제 부작용만 남고 H10은 미완료로 끝날 수 있습니다.

**최소 보정**
1. S4의 실측 latency·context로 S6 완료 가능성을 다시 계산합니다.
2. 그 결과가 부족하면 실제 대상의 부작용 전에 중단하고 보고합니다.
3. 상한은 바꾸지 않습니다.

---

## 2. 선택 지적

| ID | 내용 | 최소 보정 |
| --- | --- | --- |
| IR0-14 | live/L0 22.25분과 "이전 live 계획/R0 19.84분"이 서로 포함 관계인지 불명확합니다. 누적 1145.28분의 산술 자체는 맞습니다. | 두 장부가 서로 다른 구간임을 한 줄로 명시합니다. |
| IR0-15 | `prepared.rs`의 `validate_config`와 `config_snapshot`은 OfflineFixture 전제를 강제합니다. 예: proof-model, dynamic tools 비어 있음, network None, codex_home 단일 root. | 이 검사를 삭제하지 말고 mode별로 분기합니다. fixture8의 의미를 보존하고, Live는 auth와 runtime root 분리, proxy 허용을 따로 검사합니다. |
| IR0-16 | proxy start가 2회뿐이어서 proxy 장애 시 runtime start 배정과 관계가 불명확합니다. | IR0-06 배정표에 포함합니다. |

---

## 3. 실행으로만 판정 가능한 항목

아래는 계획 결함이 아닙니다. S1–S6 검사가 소유하며, 정적 PASS로 표시하지 않습니다.

- **T-01** 같은 thread에서 IR0-01 delta 규칙으로 정상 gen2를 통과시키면서 드리프트를 거절하는지.
- **T-02** U2 profile에서 dynamic 4종만 등록되고 native 도구는 0인지. prepared consume과 dynamic forwarding이 결속되는지.
- **T-03** Seatbelt 아래에서 Keychain을 prompt 없이 읽을 수 있는지, 최소 mach로 충분한지. wildcard는 쓰지 않습니다.
- **T-04** literal 경로의 생성·rename만으로 원자적 교체가 되는지. symlink와 hardlink alias가 거절되는지.
- **T-05** reqwest `retry::never`, redirect Reject, `client.rs`의 header 추가 뒤 final guard 위치, route pool의 TLS fallback 0.
- **T-06** cloud-policy를 단회·무cache로 조회하고 StaticModelsManager를 고정하는지. 실제 계정 class 판정.
- **T-07** xhigh latency, compaction 0 상태의 context 증가, 인증 유효기간.
- **T-08** F-04 barrier가 installed module의 writer guard 내부에 실제로 위치하는지. 순정 replay.
- **T-09** full normal과 parent-O의 실제 collection, 그리고 180분 pair 상한 안에서 끝나는지.

---

## 4. 한계

- **사설 자료:** 사설 metadata(정확한 파일·bytes·read 집합·digest)는 보지 못했습니다. IR0-03의 수치는 이전 기록인 "read27"에 근거한 추정입니다.
- **발췌 범위:** 발췌 3개 외의 line 인용(client_builder, bundle_loader, auth manager 등)은 확인하지 않았습니다.
- **reviewer 인증 경로:** 예상된 subscription firstParty 경로를 이 세션 안에서 확인하지 못했습니다.
- **증거의 성격:** 제공된 이전 관측과 Driver 처분은 증거로만 다뤘습니다. 재검증된 결과로 간주하지 않았습니다.
``````

### Current Decision Boundary

최종 실행안 승인 대기다. 승인하면 S0의 남은 exact 정적 입력 고정을 먼저 수행하고,45분 누적/범위·권한 gate를 충족할 때만 구현한다. source/actual 결과 수락과 H05/H10의 기존 exact Owner 판단은 별개다. 본 review의 전달 승인을 실제5문서의 provider 전달 승인으로 재사용하지 않는다. 기존 U2에서의 진행 소유권 handoff도 실행안 승인 전에는 활성화하지 않는다.

### Integrated R0 Closeout, Cost And Retention

checkpoint `2026-10-22T00:52:23.584568+00:00`. 이번 S0 준비·R0·Driver 처분·검증·정리 활동 15.09분, S0 잔여 29.91분. 제안한 전체960분에 이 사용량을 포함하면 향후 잔여 944.91분이다. Owner-only 대기는 제외했다. 승인 후 남은 예상590–845분이며 원 범위/상한 축소·증액은 없다. source/handoff/runtime 실행은 미승인 상태를 유지한다.

보존: 최종 실행안, 이 기록의 Reviewer 원문·처분·실행 근거, private 고정 request와 metadata. 소비자는 Owner의 실행안 판단과 후속 R1의 지적 추적이며 결과 수락/명시 포기 때 재평가한다. accepted source/binary/기존 증거는 계속 후속 구현의 입력이다. 정리: 이번 R0의 사용 끝난 controller, 이 기록과 bytes가 일치하는 중복 response 파일, 빈 per-process scratch 디렉터리를 삭제했다. process group 부재를 다시 확인했고 active 경로 변경은0이다. 고정 request는 승인한 전달 입력 및 아직 미수락한 계획의 원형을 소유하므로 보존한다.

## Owner-Approved Integrated Execution — 2026-10-22

Owner는 최종 통합 실행안 SHA-256 `dcfb672cb1883adc2ccee26f7e8615029e42e2dd86266aaf203bd0f89ef2371c`와 전체16시간(R0/보정 포함), S0 Go 뒤 구현, H01–H10/실제5문서 유지, 계획의 bounded R1 및 Claude 전송을 승인했다. H05/H10의 별도 exact 판단과 모든 중단 조건을 유지한다. 승인 원문과 exact plan은 기존 private task의 integrated-execution 입력으로 보존했다.

진행 소유권: 이 기록이 미완료 U2 host/H01–H10과 live 후속을 함께 소유한다. [원 source A 기록](FEAT-20261021-002-u2-single-host-source.md)에 같은 dated handoff를 남겼다. 기존 U2 사용9781.67초·live/L0 1334.87초와 원 결과/실패는 보존한다. 과거 작업의 수락/완료를 소급하지 않는다.

S0 재개 `2026-10-22T01:04:47+00:00`, 기사용905.507초. S0 종료한도 `2026-10-22T01:34:41.493000+00:00`, 전체 종료한도 `2026-10-22T16:49:41.493000+00:00`(Owner-only 대기 시 그 구간만 제외). 마지막20분 종료 reserve와 단계별 ceiling 우선. R0는 이미1회 완료; 현재 R1/build/runtime/auth/target 실행0. accepted runtime binary patch·untracked2 및 host 시작4파일을 최소 recovery bundle에 bytes/mode 대조해 보존했다. 새 worktree/설치/전역 설정 변경0.

## S0 No-Go And Minimal Source Delta — 2026-10-22

현재 승인된 닫힌 파일 목록으로는 S0 Go를 발급하지 않는다. 통합 목표나 H01–H10의 불가능 판정이 아니라, 필수 guard를 정상 오류로 전달할 때 필요한 실행 module2개가 목록 밖이라는 source 경계 판정이다. [승인 실행안](u2-live-integrated-execution-plan.md#source-boundary-and-early-feasibility-gate)의 “위 목록 밖의 실행 module … 구현 전에 이유와 최소 delta를 보고하고 중단한다”를 적용했다. 구현·build·runtime 인증·model·proxy·추가 reviewer·실제 대상 작업은 모두0이다.

### Required Delta And Bounded Change

| 추가할 정확한 파일 | 정적 근거 | 제안하는 최소 변경 | 유지/검증 |
| --- | --- | --- | --- |
| `codex-rs/http-client/src/route_aware_client_pool/execution.rs` | `client.rs:144–169`의 최종 default/trace header 뒤 execute는 `reqwest::Error`만 반환한다. `execution.rs:125–141,203–211`은 이 error를 그대로 TLS fallback 함수에 전달한다. 최종 guard의 typed 거절/fsync 실패는 reqwest 오류가 아니다. | 승인된 client.rs의 반환을 기존 `RouteAwareRequestError`에 맞추고 이 호출부에서 guard 거절을 즉시 전달. 실제 reqwest 오류일 때만 기존 ordinary fallback 의미 유지. 기존 `Build(String)` 오류 또는 기존 policy 오류로 비민감 거절을 표현하므로 enum 정의 파일 추가 수정은 기본안에 없음. | direct/routed send0·retry0 negative, ordinary transport 오류 경로 유지. panic/abort나 가짜 reqwest 오류를 만들어 범위를 억지로 맞추지 않음 |
| `codex-rs/keyring-store/src/lib.rs` | `KeyringStore` load/save/delete의 오류는 `CredentialStoreError`이고 현재 constructor는 keyring의 구체 오류를 요구한다(lib.rs:8–17,68–71). login은 keyring을 dev dependency로만 갖는다. 공통 keyring-store는 기존 runtime keyring 및 macOS security-framework 의존성을 이미 보유한다. | 같은 module에 native load-only/no-prompt helper를 추가하거나 비민감 read-only 오류 constructor와 wrapper를 제공한다. login/storage의 승인된 주입 경로에서 Live에만 사용하고 save/delete를 underlying store 호출 전에 거절한다. macOS의 기존 `SecKeychain::disable_user_interaction` guard는 Live process lifetime 동안 유지해 도중에 UI를 다시 켜지 않음. | fake backend로 load 경로·save/delete 실제 호출0·ordinary 무변경. 실제 auth를 fake 검사로 대체하지 않으며 interaction 필요/실패는 unavailable. 새 dependency/lock 변경·credential backend 교체·ACL 변경 없음 |

두 번째 항목의 macOS API는 로컬 pinned security-framework3.5.1 `os/macos/keychain.rs:95–105,239–250`에서 확인했다. 이 helper의 존재는 현재 Keychain backend가 prompt 없이 읽힌다는 증거가 아니다. 실제 credential은 조회하지 않았다. 원 auth path/native backend를 유지하고 process-local UI 억제만 사용하며 사용자 설정을 변경하지 않는다.

추가 범위는 위2개 실행 파일과 직접 대응 tests뿐이다. 기존 승인 파일 내 연결/검사는 그대로이며 network-proxy 제품 의미·Core authority·managed runtime·source publication 변경은 없다. 이 두 경로를 이미 승인된 것으로 처리하지 않았다. 원 R0에서 요구한 final guard/read-only auth의 구현 연결 보완이므로 추가 R0/full 회귀 횟수는 제안하지 않고, 기존 focused checks와 최종 R1에 포함한다. 그 밖의 실행 module/권한이 필요하면 같은 중단 조건을 적용한다.

### Completed And Unclosed S0 Work

완료: 승인 plan hash·accepted runtime diff/untracked2·host 시작4파일을 대조하고 최소 recovery bytes/mode를 검증했다. 원 U2와 현재 기록의 handoff 양쪽을 기록했다. final HTTP header/실행/error 경로, auth storage 주입/내부 write 경로, cloud loader의 별도 AuthManager·background, app-server OTel/analytics/environment 생성 위치를 읽었다. OS 기본 profile에서 securityd/trustd의 구체 service 이름을 확인했지만 이를 실제 필요한 mach allowlist나 실행 PASS로 확정하지 않았다.

미완료: source delta 승인 뒤 exact reachable sender/constructor·loader/root/profile·case/journal 표와 정적 Go 판정. 실제 OS canary·계정/정책/모델 적격은 원 S3/S4로 남는다. 따라서 이 기록은 나머지 S0 항목이 모두 닫혔다는 뜻이 아니다.

### Time, Preservation And Next Decision

checkpoint `2026-10-22T01:12:20.079406+00:00`. 이번 S0 활동 7.55분, 이전 R0/보정 포함 S0/통합 누적 22.64분. S0 45분 중 잔여 22.36분, 전체960분 중 잔여 937.36분이다. 지금부터 Owner-only 대기는 제외하며 사용량은 초기화하지 않는다.

두 경로가 승인된다면 남은 S0 예상8–12분(판단값), 그 뒤 S1–S7 예상580–830분은 유지한다. 합계 남은588–842분이며 여전히 낮은 신뢰다. 두 파일은 이미 계획한 guard/auth 목적을 실현하는 연결이므로 별도 full/R0나 상한 증액을 추가하지 않는다. 잔여 S0에서 닫히지 않으면 구현하지 않고 종료한다.

보존: 승인 plan·기존 source/binaries/evidence·이번 최소 recovery bundle·실행 장부. 소비자는 이 정확한 delta 판단과 승인된 통합 구현의 복구이며, 결과 수락/명시 포기 때 재평가한다. active 경로 변경/삭제0, 장기 process0. source 코드와 accepted patch/untracked2·host 시작4파일은 무변경을 다시 확인했다.

### Source Delta Accepted And S0 Resumed — 2026-10-22

Owner가 위2개 실행 파일과 직접 대응 검사를 명시 승인했다. 기존16시간·기사용·H01–H10/5문서·H05/H10 판단과 중단 조건은 그대로다. 재개 `2026-10-22T01:14:04+00:00`, 기사용1358.586초를 유지하고 Owner-only 대기 103.921초만 제외했다. S0 종료한도 `2026-10-22T01:36:25.413594+00:00`, 전체 종료한도 `2026-10-22T16:51:25.413594+00:00`. 남은 정적 gate를 먼저 닫고 Go일 때만 코드 수정한다. 이 승인으로 과거 No-Go를 소급 PASS 처리하지 않는다.

## S0 Go And Implementation Start — 2026-10-22

Owner의 두 module/direct-test 추가 승인 뒤 S0 정적 입력 고정을 마쳤다. S0 누적 38.01분(45분 상한), 전체960분 중 잔여 921.99분이며 종료20분을 포함한다. 전용 Owner 대기 103.92초는 제외했고 기존 사용량은 그대로 이월했다. S1–S7 예상580–830분은 낮은 신뢰의 판단값이다.

판정은 S0 Go다. accepted source23 bytes·두 checkout HEAD와 최소 recovery 원문을 유지한 채 exact argv, mode/profile별 roots/Seatbelt template, sender/constructor·loader/retry 처분, history/input/schema·공통 journal, 원 case/recovery/reuse 입력을 고정했다. 이는 구현 착수 적격이며 OS/auth/model/실제5문서 품질의 PASS가 아니다. S3/S4/S6의 실제 gate와 H05/H10 Owner 판단은 그대로다. source commit·배포·publication은 승인되지 않았다.

문서 worker는 Python dir_fd 기반 원자 교체를 유지한다. 기존 marked GFM parser는 macOS 기본 JavaScriptCore 안에서 실행하며 child/host IO binding을 만들지 않는다. S0 local capability probe에서 table/strikethrough/checkbox/Korean render를 확인했으며 worker OS profile 적격은 미확인이다. 원 full runner snapshot은 preflight-only selector/옛 budget에 묶여 있어 S2 task helper에서 approved selectors/현 공통 budget/output root만 연결한다. 원 runner·oracle·isolation은 보존하고 S5 앞 actual collection을 고정한다.

Private S0 input manifest SHA256 `42b769fe4ca5d022cfa537b4a26b6537e5a38c0438f29802cad0dd61e5f600f5`. 실제 auth 조회·candidate build·offline/live App Server·provider send는 모두0이다. 다음은 승인된 S1 공통 runtime 구현이며 단계 상한200분과 전체 잔여 중 먼저 닿는 한도를 적용한다. 기존 binaries/recovery/검사 입력은 진행 중 구현·R1의 consumer가 있어 유지한다. Active path 이동0, 삭제0이다.

### S1 Implementation Checkpoint — 2026-10-22T02:02:16.948836+00:00

승인된 S1 구현을 진행 중이다. mode/history/native 결과 결속, 최종 HTTP 요청 guard와 실패 latch, 공통 장부 예약, native read-only auth 파일 identity, 단회 정책/모델 초기화, 별도 live entry를 작성했다. 24개 구현 파일의 현재 identity를 task execution 장부에 기록했다. Rustfmt 구문 정리 및 diff check는 통과했으나 아직 컴파일·제품 검사 전이다. 구현 완료나 실행 적격 PASS로 판정하지 않는다. U2 dynamic profile/host 연결, guard focused tests, privacy/입력/이력 검증은 계속 필요하다.

S1 실측 32.85분 / 상한200분, 통합 누적 70.86분 /960분, 잔여 889.14분(종료20분 포함). build/runtime/auth/network/reviewer 추가 실행0. 현재 실행 중 process0. 원 accepted binary·diff/untracked 복구본과 진행 source/task artifacts는 후속 구현·S3 검증의 입력이므로 유지하며 active path 변경·삭제0이다.

### S1 Focused Verification Progress — 2026-10-22T02:28:04.139504+00:00

HTTP/keyring 집중 검사에서 direct+routed guard 거절·실패 latch와 native backend에 대한 save/delete 차단, process-lifetime no-prompt guard의 fake 검사가 통과했다(선택4 tests, subprocess3 scenarios; 실제 Keychain 검사는 아님). 최초 컴파일의 closure 수명·직접 대응 TLS 테스트 타입 오류는 원인 보정 후 재검사 통과로 닫았다. 공통 app-server lib/live entry cargo check도 통과했다. 새 history/context/final-bytes 검사와 보정은 아직 core test compile 중이므로 S1 완료나 live 적격 PASS로 판단하지 않는다. native SSE는 tx_event.closed 경로를 재사용하며, 종료의 실행 검사는 이어 수행한다.

S1 실측 58.64분 /200분, 통합 누적 96.65분 /960분, 잔여 863.35분(종료20분 포함). formal candidate build·App Server·실제 인증/provider/reviewer 추가 호출0. 현재 child는 task 장부에 정확한 PID와 단계로 기록했다. H01–H10은 아직 qualification 전이며 실제5문서·H05/H10 별도 Owner gate를 유지한다. 원 accepted binary/recovery/source·실행 증거는 S2/S3/R1의 입력이므로 유지한다. Active path 이동·삭제0.

### S1 Focused Verification Progress — 2026-10-22T02:39:51.525720+00:00

core 집중 검사9개가 통과했다. 최초 native timestamp 가정 오류와 SSE fake auth Arc 타입 오류는 각각 보정 후 통과로 닫았다. 실제 native SSE parser의 idle body가 consumer drop 뒤1초 내 해제됨을 fake transport로 확인했으며 실제 OS/host 종료 증거는 아니다. 추가 native startup/config·client identity·최종 header exact 검사를 구현했고 fake auth 만료/identity/latch 검사는 실행 중이다. runtime journal의 controller 연동은 예정된 S2에 남겨 두며 S1 완료를 선언하지 않는다.

S1 실측 70.43분 /200분, 통합 누적 108.44분 /960분, 잔여 851.56분(종료20분 포함). formal candidate build·App Server·실제 인증/provider/reviewer 추가 호출0. 현재 child는 task 장부에 정확한 PID와 단계로 기록했다. H01–H10은 아직 qualification 전이며 실제5문서·H05/H10 별도 Owner gate를 유지한다. 원 accepted binary/recovery/source·실행 증거는 S2/S3/R1의 입력이므로 유지한다. Active path 이동·삭제0.

### S1 Focused Verification Progress — 2026-10-22T02:56:17.091962+00:00

S1 app2·cloud policy1·core15개의 선택 검사는 통과했고, 넓은 prepared 이름 필터에 우연히 포함된 무변경 compaction4개는 mock port bind EPERM으로 실패했다. 이4개를 PASS나 제품 결함으로 바꾸지 않고 실행 제한으로 보존한다. 재검사는 명시한 compaction prefix만 제외하고, 새 native loader flags/mandatory policy 충돌·xhigh 지원·비민감 auth 위반 counter를 포함한 변경 경계를 대상으로 한다. S1-final-focused-02 실행 중이며 formal candidate build·실제 auth/provider는 여전히0이다.

S1 실측 86.85분 /200분, 통합 누적 124.86분 /960분, 잔여 835.14분(종료20분 포함). formal candidate build·App Server·실제 인증/provider/reviewer 추가 호출0. 현재 child는 task 장부에 정확한 PID와 단계로 기록했다. H01–H10은 아직 qualification 전이며 실제5문서·H05/H10 별도 Owner gate를 유지한다. 원 accepted binary/recovery/source·실행 증거는 S2/S3/R1의 입력이므로 유지한다. Active path 이동·삭제0.

### S1 Focused Verification Progress — 2026-10-22T03:03:59.581445+00:00

S1-final-focused-02 통과(app3/cloud1/core15/auth2/model1), 마지막 loader baseline/정책별 거부 App Server3개 통과. HTTP/keyring4개+3 subprocess 기존 동일 근거 재사용. 필수 S1 경계 focused 완료, 실제 auth/OS/candidate qualification은 미실행. S2 공통 journal/controller와 host/worker 연결을 시작한다.

S1 실측 94.56분 /200분, 통합 누적 132.57분 /960분, 잔여 827.43분(종료20분 포함). formal candidate build·App Server·실제 인증/provider/reviewer 추가 호출0. 현재 child는 task 장부에 정확한 PID와 단계로 기록했다. H01–H10은 아직 qualification 전이며 실제5문서·H05/H10 별도 Owner gate를 유지한다. 원 accepted binary/recovery/source·실행 증거는 S2/S3/R1의 입력이므로 유지한다. Active path 이동·삭제0.

### S2 Implementation Checkpoint — 2026-10-22T03:48:26.261994+00:00

Rust S2 focused App Server5/Core16 및 초기 Python host8 통과. CLI 광범위 tail 교체의 자동 승인 검토 거부 후 원문 byte 보존과 승인 계획 범위를 확인했고, 두 곳만 연결한 수정은 승인됨. journal thread/turn/control 결속, 원문 출처, 출력 원본 보존, Owner 대기 산정 보정은 다음 focused 검사를 앞둔 상태. actual-accept/recover CLI, 재개 연결 및 실제 worker/OS 검사는 아직 남음.

S2 실측 44.44분 /210분, 통합 누적 177.01분 /960분, 잔여 782.99분(종료20분 포함). actual auth/provider/target/authority/reviewer 미실행이며 H01–H10 미적격 상태를 유지한다. 기존 source·원문 복구와 검사 근거는 S2/S3/R1 소비가 남아 보존한다. Active path 이동·삭제0.

### S2 Implementation Checkpoint — 2026-10-22T03:57:20.114818+00:00

H05 synthetic installed barrier helper·exact accept/recover route·봉인 전 current-bytes checkpoint 재개 연결을 구현했다. native schema projection 전체 대조와 provenance 포함 pack 크기 계산을 보정했다. Python 확장 host8 PASS(0 failures, actual child 종료·aliases 포함); 새 proxy snapshot 결속 App Server focused가 실행 중이다. 실제 OS/installed/Core/model 효과는 아직 없다.

S2 실측 53.34분 /210분, 통합 누적 185.91분 /960분, 잔여 774.09분(종료20분 포함). actual auth/provider/target/authority/reviewer 미실행이며 H01–H10 미적격 상태를 유지한다. 기존 source·원문 복구와 검사 근거는 S2/S3/R1 소비가 남아 보존한다. Active path 이동·삭제0.

### S2 Implementation Checkpoint — 2026-10-22T04:12:42.233261+00:00

OS worker read qualification은 첫 실행과 read-only 진단, 선언된 ancestor metadata 누락 보정 후에도 dyld 초기화 SIGABRT로 종료했다. stdout/stderr0·process group 부재를 확인했으며 write/verifier 시작0이다. 원인 syscall은 미확정. 현 macOS의 두 Cryptex dyld cache 위치가 승인 read 목록 밖인 것을 관측하여 permission delta 제안을 미실행으로 고정했다. 현행 host8·App Server6·앞선 변경 없는 Core16 focused PASS이며 실제 OS 실패와 구분한다. 다음은 Owner의 exact read-only delta/단일 진단 판단이다.

S2 실측 68.71분 /210분, 통합 누적 201.28분 /960분, 잔여 758.72분(종료20분 포함). actual auth/provider/target/authority/reviewer 미실행이며 H01–H10 미적격 상태를 유지한다. 기존 source·원문 복구와 검사 근거는 S2/S3/R1 소비가 남아 보존한다. Active path 이동·삭제0.

### S2 OS Gate Stop And Next Owner Decision — 2026-10-22T04:12:42.394080+00:00

S1 구현/집중 검사는 완료했고 S2는 부분 구현 상태다. 승인된 worker profile에서 native interpreter가 dyld ignition/CacheFinder 초기화 중 SIGABRT로 종료했다. 첫 read, 원 stderr 미보존을 보완한 read-only 진단1회, 이미 선언된 dependency ancestor metadata 누락 보정 검사1회를 구분해 보존했다. 모두 process group 부재를 확인했고 write·verifier·실제 auth/provider/authority/target 실행은0이다. 실패를 source 단위 검사 PASS로 대체하지 않는다.

Crash의 정확한 거절 syscall/path는 미확정이다. 현재 OS의 `/System/Cryptexes/OS/System/Library/dyld`와 `/System/Volumes/Preboot/Cryptexes/OS/System/Library/dyld`는 기존 read 목록에 없으며, 그 누락은 원인 후보이지 확정 진단이 아니다. 승인 실행안의 추가 권한/불명 상태 중단 조건에 따라 후속 실행을 멈췄다.

| 기준 | 현재 근거와 한계 |
| --- | --- |
| H01 | 합성 admission/callback binding 단위 검사 PASS; 실제 native callback 경로 미검증 |
| H02 | 합성 exact packet/ticket/result 변조 거절 PASS; installed 경로 미검증 |
| H03 | alias·RPC·cleanup 단위 검사 PASS; 실제 worker OS 초기화 실패로 unavailable |
| H04 | FakeCore로 prepare/apply1회 및 거절 PASS; 순정 installed accept 미실행 |
| H05 | 원 packet/사람 응답/재사용 거절 단위 PASS, installed barrier helper 구현; 실제 death·원 ticket·Owner replay 미실행 |
| H06 | 단위 fixture에서 claims 실패→atomic write→같은 oracle PASS; 실제 sandboxed iteration 미검증 |
| H07 | 장부 carry/손상/다른 thread·turn/중복 control 거절 PASS; 새 process/thread 실제 재개 미검증 |
| H08 | 합성 stop·봉인 후 도구 거절 PASS; 실제 host stop 경계 미검증 |
| H09 | 기존 세 사례의 최종 disposition 미완료 |
| H10 | 실제5문서 접근·전송/setup/commit/accept 및 Owner 내용 관측 미시작 |

다음 승인 제안은 고정 OS-cache 읽기 delta와 단일 read-only 진단이다. 두 OS 경로의 regular cache 파일164 literal(동일 inode82개), 해당 정확한 directory read/ancestor metadata만 제안하며 write/network/mach/fork/exec를 추가하지 않는다. private packet에 전체 목록과 worker/runtime/proxy 미실행 profile hash를 고정했다. 진단은 합성 read1회·process60초·활동15분 상한, 예상5–10분(판단값)이다. 성공할 때에만 같은 delta를 세 역할의 profile에 적용하고 기존 계획을 이어가는 승인을 요청한다. 추가 권한 필요·동일 실패면 다시 멈추며 H05/H10 별도 판단과16시간 누적 상한은 그대로다.

중단 시 S2 68.71/210분, 통합 201.28/960분(R0 포함), 잔여 758.72분(종료20분 포함)이다. 예상 잔여425–620분은 모든 gate 통과를 전제로 한 낮은 신뢰의 판단값이며 Owner 대기는 제외한다. Owner가 재개를 승인하면 중단/응답 시각으로 대기만 제외하고 기존 사용량과 단계/전체 잔여를 carry한다.

최신 native Python host8(실패/skip0), App Server6, 바뀌지 않은 Core16 집중 근거와 두 checkout diff check를 확인했다. 전체47 focused와 full normal/O는 아직 실행하지 않았다. 처음부터 보존한 accepted source/recovery·현 source·실패 inputs/profile/controller·검사 결과·미실행 delta는 후속 판단/S2/S3/R1 소비를 위해 유지한다. 활성 경로 변경·worktree 삭제0이다. 검증 후 소비자가 없는 일회성 편집/제안 helper7개와 확인된 bytecode cache·빈 prelaunch 디렉터리만 삭제했다. 중간 host recovery 삭제는 자동 검토가 exact 원문 별도 보존 미확인을 이유로 거부해 그대로 유지했다. 원래 recovery/승인 계획/accepted fixture와 lock/schema 입력은 그대로다.

Adopter impact: managed Core/source schema·설치 runtime·실제 adopter 변경0. 이 후보의 일반 지원·배포/설치 완료 또는 U2 완료를 주장하지 않는다. source commit/push/PR/merge0, R1 호출0이며 결과 수락은 남아 있다.

### Approved OS Diagnostic Failed — 2026-10-22T04:17:33.252696+00:00

Owner는 2026-10-22T04:15:18.635484+00:00에 고정 OS 공유캐시 읽기 delta·합성 read 진단1회·활동15분 상한과 성공 시 기존 계획 재개를 승인했다. 기존 중단부터 응답까지 156.241404초만 Owner 대기로 제외했고 기존 사용량·16시간 상한·H05/H10 판단을 유지했다. 승인 proposal SHA256은 `b48e10f5ed83c623c0dfe65dd1ed7218488d145c1b8215a8d498ce32d624113c`, 진단 profile SHA256은 `d2679ff10f283f5ebee5d5e931f43db87ff65e49877eaf55be7bd877ff613be8`이다.

고정된 기존 argv/read request/spec/worker와 synthetic 두 문서의 identity를 확인한 뒤 profile만 승인안으로 바꿔 정확히1회 실행했다. PID 31808는 0.022초 후 exit -6(SIGABRT), stdout0/stderr0으로 종료했다. process group 부재·문서 원문 불변을 확인했다. 이 결과는 cache 읽기 delta만으로 startup을 해결하지 못했다는 근거다. 정확한 원인이나 다음 필요한 권한은 아직 확정할 수 없다.

같은 실패 시 중단하라는 Owner 조건에 따라 재시도0, 추가 권한0이며 후속 worker/runtime/proxy 실행과 구현 재개를 중단했다. 성공 조건이 성립하지 않아 runtime/proxy effective profile에 delta를 채택하지 않았다. 실제 auth/model/Core/5문서 작업·candidate build·R1 추가 호출0, H01–H10 미적격/미완료 상태를 유지한다.

승인 응답부터 이 결과 보존까지 진단 활동 2.24분 /15분, S2 누적 70.95분 /210분, 통합 누적 203.53분 /960분, 전체 잔여 756.47분(종료20분 포함)이다. 원래 예상5–10분보다 조기에 실패 중단했으며 새 recovery 예상은 산정하지 않았다. 이후 전용 Owner 대기는 다음 명시적 재개 승인 시에만 제외한다.

private task의 `integrated-execution/os-profile-delta/diagnostic-result.json`에 결과를, 같은 디렉터리에 승인·exact profile·script·시작/프로세스 기록·stdout/stderr를 읽을 수 있게 보존했다. 해당 입력/실패 근거와 기존 source/recovery는 후속 Owner 판단 및 복구 범위 결정에 필요하므로 유지한다. 이번 단계 삭제0, 활성 경로 이동0, worktree 삭제0이며 실행 중 process0이다. 소비 종료 조건은 대체 복구 근거의 수락 또는 명시적 작업 포기 후 복구 필요성 해소다.

### Existing Failure Static Analysis — 2026-10-22T04:22:16.047529+00:00

Owner가 승인한 기존 실패 근거 분석만 수행했다. workflow-work-debug의 INIT에서 기존 반복 실패를 확인하고 FAIL → RECOVER → PLAN으로 정리했다. 분석 위험도 L1(읽기와 기존 checkpoint 기록), 향후 sandbox 보안 변경은 L3로 별도 판단한다. source·profile 수정과 새 target 실행은0이다. docs/STATUS.md 변경은 필요하지 않으며 이 기존 Work의 discovery만 기록한다.

네 PID(18326, 20288, 21370, 31808)의 crash는 모두 동일 dyld UUID `D341DDCB-7969-3A9C-8E03-0CF4751398A9`와 `boot_boot+228`이다. 현재 `/usr/lib/dyld`의 arm64e UUID가 정확히 일치함을 확인한 뒤 기존 binary를 정적으로 대조했다. return address `0x7b748`의 직전 `0x7b744`는 `ignition_halt` 호출이며, 그 분기는 `open("/", 0x20100000)`의 음수 반환 후 도달한다. 같은 분기의 진단 문자열은 `failed to open root directory: %s: %d`다. 따라서 즉시 실패 지점은 공유캐시 파일 내용 읽기나 worker Python 코드 이전의 루트 디렉터리 open으로 좁혀졌다.

현재 worker profile과 승인 cache delta는 `/`의 file-read-metadata만 허용하고 file-read-data는 허용하지 않는다. 이 불일치가 가장 유력한 원인 후보다. 다만 실제 errno·거절한 sandbox layer/OS 검사·보고된 operation은 기존 crash에서 확인할 수 없으며 단정하지 않는다. termination code2는 POSIX errno2로 읽지 않는다. `/` open이 해결되더라도 후속 loader/worker 통과나 cache delta의 필요 여부는 별도 미검증이다. [Apple open flags 정의](https://raw.githubusercontent.com/apple-oss-distributions/xnu/main/bsd/sys/fcntl.h)와 [CacheFinder의 ignition 호출](https://raw.githubusercontent.com/apple-oss-distributions/dyld/main/dyld/DyldProcessConfig.cpp)은 해석 보조이며, 정확한 실패 분기는 UUID가 일치하는 로컬 image에서 확인했다.

추가 확인 제안은 기존 unified log에서 마지막 PID31808의 KST13:16:40–13:16:43 기록을 단1회 읽는 것이다. 가설은 `file-read-data /` 거절이며, 정확한 operation/path/errno가 기록돼 있는지만 확인한다. query argv와 최소 보존 필드는 private `os-profile-delta/static-root-open-evidence.json`에 고정했다. 예상3–5분(판단값), 활동10분/조회60초 상한, 새 worker 실행0·권한/profile/로그 설정 변경0이다. 일치 기록이 없거나 접근 불가/timeout이면 Unknown으로 종료하고 범위 확대·재조회하지 않는다. 미실행 제안이며 지금 승인된 실행으로 간주하지 않는다. 결과가 원인을 뒷받침하더라도 권한 변경·원 계획 재개는 별도 Owner 판단이다.

변경 파일은 이 Work checkpoint와 private evidence/누적 장부뿐이다. 원인 수정 예정 파일은 아직 없다. 검증은 crash의 image UUID와 frame offset·실제 local symbol/instruction 대조, exact 실패 profile hash 확인으로 수행했다. 제품 검사 재실행은 하지 않는다. 되돌릴 제품 변경이 없고 원 실패 자료는 보존된다.

이번 분석 활동 3.52분을 기존 사용량에 더했다. 전용 Owner 대기 71.88초만 제외했고 통합 누적 207.04/960분, 잔여 752.96분(종료20분 포함), S2 잔여 135.53분이다. H05/H10 Owner 판단과 실제 auth/model/Core/5문서 미실행을 유지한다. 새 evidence는 다음 원인 판단의 입력으로 보존하고 해당 판단/대체 근거 수락 또는 명시적 포기까지 유지한다. 삭제·활성 경로 변경0이다.

### Approved Existing Log Query — No Records — 2026-10-22T04:25:37.619389+00:00

Owner는 2026-10-22T04:23:45.684690+00:00에 앞서 고정한 기존 OS 로그 조회1회를 승인했다. exact argv로 마지막 실패 PID31808의 KST13:16:40–13:16:43 구간만 조회했다. 조회 process PID38875, exit0, 소요 1.066초, stdout은 빈 JSON 배열2bytes, stderr0, 일치 기록0건이었다. process group 부재를 다시 확인했다. 실제 명령은 task의 `os-profile-delta/existing-log-query-start.json`, 결과는 `existing-log-query-result.json`에 보존했다.

기록 없음 중단 조건을 충족했으므로 재조회·시간/PID 범위 확대·새 worker 실행·권한 또는 로그 설정 변경은 모두0이다. 이는 지정된 조회의 일치 기록이 없다는 뜻이며, 거절 자체가 없었다거나 시스템 전체 로그에 원인 기록이 없다는 뜻으로 확대하지 않는다. 기존 crash/binary 주소 대조로 확인한 루트 디렉터리 open 실패 지점은 유지한다. root file-read-data 누락은 여전히 유력 후보이나 정확한 errno·보고된 operation·거절 주체는 미확정이다. 후속 실행은 승인되지 않았으며 H05/H10 Owner 판단을 유지한다.

이번 승인부터 결과 보존까지 활동 1.87분 /10분, 조회 1.066초 /60초였다. 직전 중단부터 응답까지 전용 Owner 대기89.637161초만 제외했다. 기존 사용량을 이월한 통합 누적 208.91/960분, 잔여 751.09분(종료20분 포함), S2 잔여 133.66분이다. 실제 auth/model/Core/5문서·candidate build·R1 추가 실행0이다.

필수 승인·query script·시작/프로세스/결과 기록은 읽기 가능한 기존 durable task 경로에 보존했다. 다음 Owner 판단에서 query1회 소비와 Unknown 결과를 확인하는 근거이므로 대체 근거 수락 또는 명시적 작업 포기까지 유지한다. 삭제·활성 경로 이동·worktree 삭제0이며 남은 query process0이다. 제품 source/profile/STATUS는 변경하지 않았다.

### Root Directory Read Diagnostic Proposal — Not Executed — 2026-10-22T04:28:53.073429+00:00

Owner의 제안 준비 요청에 따라 마지막 실패 profile을 그대로 보존하고 `/` directory의 file-read-data 한 가지 권한만 추가하는 별도 미실행 profile을 작성했다. 기존 shared-cache delta도 그대로 두어 한 변수만 바꾼다. 정확한 추가 규칙은 다음과 같다.

```scheme
(allow file-read-data
  (require-all
    (literal "/")
    (vnode-type DIRECTORY)))
```

`require-all`로 literal `/`와 DIRECTORY를 모두 만족하게 한다. 추가 노출은 root directory 자체의 읽기이며 바로 아래 entry 이름을 열거할 능력도 포함한다. 이 규칙은 하위 파일 내용의 재귀 읽기·새 하위 metadata·쓰기·network/mach·exec/fork 권한을 추가하지 않는다. 기존 profile의 다른 권한은 그대로이므로 위 설명은 전체 profile이 아닌 추가분의 범위다. unchanged worker는 합성 두 문서만 읽으며 root 열거를 수행하지 않는다. selector 조합은 기존 정책 패턴으로 정적 확인했으며 profile compiler/실제 OS 검증은 하지 않았다.

제안은 기존 argv·Python/worker/spec/request·합성 문서/identity·dyld를 고정하고 -f 대상만 `os-profile-delta/root-read-proposed.sb`로 바꾸는 단일 실행이다. 준비 profile SHA256 `31bba8100f4622b01048fd4c191f2cd0b72e05718f40ce3365555a1939f86c8e`, 전체 제안은 `root-read-proposal.json`에 고정했다. 실행 예상3–5분(이전 준비/종료 관측에 기반한 판단값), 활동10분·process60초 상한이다. 입력 확인·실행1회·종료·필요 시 같은 PID의 이미 생성된 crash 해석·결과 보존까지 포함한다. 전용 Owner 대기는 제외하며 기존16시간/S2 잔여를 그대로 사용한다.

실행 전 identity drift·중복 attempt·추가 권한 필요·잔여 부족이면 시작하지 않는다. 정확한 합성 read 결과/exit0/원문 불변/process group 부재가 모두 확인되면 해당 baseline에서 root grant가 기존 초기화 장애를 해소했다는 강한 지지로 판정한다. 다른 후속 실패로 이동하면 기존 root 장애 해소 가능성만 부분 지지하고 중단한다. 같은 실패·timeout·profile/launch 오류·관측 불가는 미확정/실패로 종료한다. 어떤 결과에서도 재시도·즉석 수정·권한 추가는 하지 않으며 성공해도 원 계획 자동 재개나 runtime/proxy profile 채택을 하지 않는다. 이것은 OS startup의 단일 원인 진단이며 전체 역할/격리/H01–H10 PASS가 아니다.

변경은 private 미실행 제안2개와 이 checkpoint/누적 장부뿐이다. 현재 target 시작·profile compile·적용은0이고 설치/보안 설정/source/STATUS 변경0이다. 실행 승인 전에는 위 진단도 수행하지 않는다. rollback은 단일 process 종료로 한정되며 원 profile·effective template는 그대로 보존한다. 원 실패와 제안은 다음 Owner 판단 입력이므로 승인/거절 후 증거 소비가 끝날 때까지 유지한다. 삭제·활성 경로 이동0이다.

제안 준비 2.19분을 기존 사용량에 포함했다. Owner 전용 대기 64.28초만 제외했고 통합 누적 211.09/960분, 잔여 748.91분(종료20분 포함), S2 잔여 131.48분이다. H05/H10 별도 Owner 판단과 실제 auth/model/Core/5문서 미실행을 유지한다.

### Approved Root Read Diagnostic — Passed, Stopped — 2026-10-22T04:31:48.959885+00:00

Owner는 2026-10-22T04:29:59.869591+00:00에 고정 root-directory 읽기 규칙과 합성 read1회를 승인했고 성공해도 중단하도록 명시했다. 고정 proposal/input/profile/dyld·cache metadata·합성 문서 identity와 parser hash를 확인한 뒤 단1회 실행했다. target PID44305, exit0, 소요 1.304초, stdout333bytes/stderr0이었다. 반환된 두 문서 ID·내용·hash가 예상과 정확히 일치했고 원문 bytes·identity·mode 불변과 process group 부재를 확인했다.

이는 마지막 실패 profile의 shared-cache 규칙을 유지한 상태에서 정확한 root-directory file-read-data 규칙 하나를 추가했을 때 초기화 장애가 해소되고 worker read까지 성공했다는 관측이다. 앞서 UUID/주소로 특정한 root open 실패와 합쳐 해당 누락 가설을 강하게 지지한다. cache delta가 불필요하다는 증거나 실제 거절 errno·상위 policy의 직접 관측은 아니다. 전체 OS 격리, write/verifier, runtime/proxy, installed Core, 실제 auth/model/5문서 및 H01–H10 적격 PASS로 확대하지 않는다. H03에는 이 좁은 read 진단 PASS만 구분해 연결했다.

승인된 성공 후 중단 조건을 적용했다. 재시도0, root grant 외 추가 권한0, 원 계획 자동 재개0, 다른 역할 검사0, runtime/proxy/worker effective template 채택0이다. 원 profile bytes를 다시 확인했고 전역 OS 보안·설치 runtime·제품 source·STATUS 변경은 없다. H05/H10 별도 Owner 판단은 그대로다.

이번 승인부터 결과 보존까지 활동 1.82분 /10분, process 1.304초 /60초였다. 전용 Owner 대기66.796162초만 제외하고 기존 사용량을 이월했다. 통합 누적 212.91/960분, 잔여 747.09분(종료20분 포함), S2 잔여 129.66분이다. 원 formal candidate build·actual auth/provider/Core/5문서·R1 추가 실행0을 유지한다.

private task `os-profile-delta/root-read-result.json`과 같은 디렉터리의 승인·exact proposal/profile·controller·시작/프로세스·stdout/stderr를 보존하고 읽기 가능함을 확인했다. 기존 실패/정적분석과 이번 성공의 대비는 다음 적용/재개 판단에 필요한 유일한 근거이므로 그 판단과 대체 근거 수락 또는 명시적 포기까지 유지한다. 삭제·활성 경로 이동·worktree 삭제0, 남은 process0이다.

### Three-Role Profile Adoption And Resume Proposal — Not Applied — 2026-10-22T04:40:36.758772+00:00

Owner는 검증된 `/` 읽기 규칙을 worker/runtime/proxy에 반영하고 기존 계획을 재개할 최소 변경안만 요청했다. workflow-work-resume의 drift 확인에서 두 worktree branch/HEAD가 각각 runtime `codex/u2-tool-plan-proof`/83086188ae0614bd882818ff1aa23f3194962012, host `codex/colvia-u2-plan-20261021`/7d012f5297de1d9a77aa0b8187406f4785221573임을 확인했다. 현재 판단은 최신 dated checkpoint의 S2 중단/진단 read PASS이며, 앞부분의 옛 L0/S0 상태 문구나 원 계획의 승인 전 표기를 현행 실행 상태로 사용하지 않는다. 이 제안은 PLAN이며 실행 재개 승인은 아니다.

최소 변경은 세 S0 role template의 본문을 보존하고 동일한 고정 cache delta와 성공한 root `file-read-data`/`literal /`/`DIRECTORY` conjunction만 추가한 새 template3개를 선택하는 것이다. cache를 빼는 별도 실험은 하지 않는다. 제안 파일은 private `os-profile-delta/<role>-root-read-template-proposed.sb.in`이며 지금은 미적용이다. 승인 뒤 이 exact path/hash를 effective mapping에 결속하고 기존 DocumentController의 profile_template+hash 입력 및 아직 미완료인 S2 runtime/proxy materializer에 연결한다. 원 S0 manifest/승인 계획/journal lineage와 기존 실패·성공 증거는 그대로 보존한다. 새 registry·sandbox backend·Core/auth/HTTP 변경은 이 delta에 필요하지 않다.

세 프로세스 모두 root directory 자체를 읽고 바로 아래 이름을 열거할 능력이 추가된다. 하위 내용의 재귀 읽기나 역할별 write/network/mach/exec 범위는 추가하지 않는다. cache164 literal/82개 파일·4 directory와 ancestor metadata도 기존 제안 그대로다. worker의 성공이 runtime/proxy나 전체 OS 격리의 PASS를 뜻하지 않는다.

| 근거 구분 | 재사용 또는 추가 확인 |
| --- | --- |
| 재사용 | exact worker read 출력·문서 불변·exit/종료 성공. 같은 입력의 rendered policy·의존성이 동등한지 정적으로 확인하고 단순 새 파일명/hash 때문에 반복하지 않는다. |
| 조건부 재사용 | source/test/runner/oracle 무변경인 S1/S2 집중 근거. 단위/fake 근거의 한계를 유지한다. |
| worker 추가 | 기존 예정 atomic write/swap/rename/fsync·세 verifier와 H03 금지 descendant/control/credential/network/mach/alias 검사. `/` immediate entry 열거는 승인 노출로 취급한다. |
| runtime/proxy 추가 | S3 합성 OS canary와 S4 첫 배정 start에서 실제 기동·역할별 read/write/egress·native auth/policy/model. 별도 무료 probe start를 추가하지 않는다. proxy2회와 원 start/thread/turn/send 배정을 유지한다. |
| 원 의무 유지 | S3 candidate build/fixture8/ordinary, S4 H01–H09 및 H05, S5 normal/O 각1회, S6 실제5문서/H10, S7 bounded R1. 이 profile 변경만을 위한 별도 build/full/review는 추가하지 않는다. |

| 작업 | 예상 활동분 | 중단 상한 |
| --- | ---: | --- |
| profile 선택·결속·정적 대조 |10–20 |30분, 기존 S2 안에 포함 |
| 변경 영향 OS 확인 |20–35 |45분, 기존 S3 안에 포함 |
| S2 잔여 전체(위 profile 작업 포함) |65–110 |현재 S2 잔여 126.05분 |
| S3 |90–135 |150분; 최초 build 적격90분 유지 |
| S4 |55–85 |105분 |
| S5 |125–145 |180분 |
| S6 |60–90 |120분 |
| S7 |30–45 |60분 |
| S2–S7 합계 |425–610 |전체960분에서 기존 사용량 차감; 단계/전체 중 먼저 닿는 한도 |

profile/OS 두 행은 아래 단계에 이미 포함돼 중복 합산하지 않는다. 예상은 단일 worker read1.304초로 다른 역할 시간을 추정한 값이 아니라 남은 integration/build/검사에 대한 낮은 신뢰의 판단이다. S5는 과거 실패 pair117.53분을 시간 참고로만 재사용한다. 구현·build·검사·reviewer 대기·기록/종료를 포함하고 Owner만 기다리는 시간만 제외하며 병렬 절감을 가정하지 않는다. S3/S4에서 재산정하고 상한 때문에 H 기준이나5문서를 줄이지 않는다.

명시 승인 뒤에만 profile mapping → S2 마무리 → S3 적격 → S4 → S5 → S6 → S7로 이어간다. 기존 H05 exact-ticket와 H10 대상/read·전달/intent/grant/setup/candidate/result Owner 판단은 유지한다. 새 권한/경로·unknown sender·auth prompt/만료·불명 authority·drift·예산/시도 초과면 중단하며 즉석 확대/우회 재시도하지 않는다. 프로세스 종료 뒤 mapping을 원본으로 되돌릴 수 있으나 그것이 옛 실패 profile 재실행이나 예산 초기화를 허용하지는 않는다.

이번 준비 3.61분을 사용량에 더하고 Owner 전용 대기 311.20초만 제외했다. 누적 216.52/960분, 전체 잔여 743.48분(종료20분 포함)이다. 제안 정적 파일3개와 `profile-adoption-resume-proposal.json`, 이 checkpoint/장부만 작성했다. 적용·profile compile·실행·build/검사/review·auth/target 효과는0이다. 기존 source/STATUS는 변경하지 않았고 삭제·활성 경로 이동0이다. 제안/근거는 다음 Owner의 채택 또는 거절 판단과 필요한 복구 확인까지 보존한다.

### S2 Implementation Checkpoint — 2026-10-22T04:44:44.197246+00:00

Owner 승인 exact 세 profile mapping을 결속했다. 새 worker template를 기존 고정 입력으로 정적 치환한 bytes가 성공 진단 profile과 완전히 같아 동일 read 실행 없이 근거를 재사용한다. runtime/proxy materializer와 남은 S2 검증을 계속한다. 단계 시간은 Owner 대기를 반영한 고정 deadline 기준으로 carry하며 재설정하지 않는다.

S2 실측 85.70분 /210분, 통합 누적 218.27분 /960분, 잔여 741.73분(종료20분 포함). actual auth/provider/target/authority/reviewer 미실행이며 H01–H10 미적격 상태를 유지한다. 기존 source·원문 복구와 검사 근거는 S2/S3/R1 소비가 남아 보존한다. Active path 이동·삭제0.

### S2 Worker Write Permission Stop — 2026-10-22T04:49:17.770768+00:00

Owner 승인 세 profile 선택과 기존 read 근거 재사용을 유지한다. 별도 합성 fixture의 DOC-CLAIMS 누락 검사는 예상대로 false를 반환했으나 첫 write가 PermissionError(exit 2)로 종료돼 중단했다. 새 권한·재시도·runtime/proxy/auth/provider/Core/실제 대상 실행은 없다. 원본 Output/Reference bytes·inode·mode는 그대로이고 요청한 34바이트 swap만 남아 보존한다. 실제 실패 syscall은 미확정이다. swap의 명시적 metadata 읽기 규칙 부재는 소스상 후보일 뿐 확인된 원인으로 승격하지 않는다. 두 worker process group의 부재를 재확인했다.

근거: `private-evidence/E109`; source 수정0. runtime/proxy 명세 연결과 나머지 S2–S7은 미완료다. 종료 조건에 따라 새 실행을 멈추고 Owner 판단을 기다린다. H05/H10 판단은 변하지 않는다. [공개용 중립화]

누적 활동 222.83/960분, 잔여 737.17분(종료20분 포함). S2 90.26/210분, 잔여 119.74분. 이번 재개부터 종료·보존까지 6.31분. Owner 대기 시작은 이 시각으로 고정하며 재개 시 기존 사용량을 유지한다.

보존: 기존 source/recovery/read 근거와 이번 실패 입력·profile·로그·원본 사본·swap. 소비자: 후속 원인 진단·복구 판단 및 S2–S7. 유지 종료 조건: 해당 실패 처분을 대체할 검증된 근거와 Owner 결정이 생길 때 재평가. active path 변경0, 삭제0; swap은 실패 증거이므로 삭제하지 않았다.

### Write Operation Diagnostic Preparation — 2026-10-22T05:03:50.499607+00:00

Owner는 권한 추가 없는 최소 진단안 준비만 요청했다. 예외 출력만 확장한 worker 사본·동일 권한 규칙의 경로 치환 profile·동일 bytes 합성 입력·1회 실행기를 별도 task 경로에 고정했다. 원본 worker와 쓰기 함수, 기존 실패 파일25개·원본·swap은 변경하지 않았다. AST/bytes/profile 치환 비교만 수행했고 diagnostic 실행0, approval.json/attempt.json 없음이다.

제안: `private-evidence/E107`; manifest SHA-256 `be32f5d43460cff10c127ae85ac19c2fa040be961250ab008b7aa76468ab0cf3`. 승인 후 예상2–4분, 활동10분 상한, 프로세스60초, TERM/KILL 각각10초. 성공·실패 모두 보고 후 중단하며 새 권한·자동 재개는 제외한다. H05/H10 판단 유지. [공개용 중립화]

이번 준비 활동 4.83분을 누적했다. 직전 중단부터 준비 요청까지 Owner 대기 582.957초만 제외했다. 총 227.66/960분, 잔여 732.34분(종료20분 포함); S2 95.09/210분, 잔여 114.91분. 새 승인 대기는 이 checkpoint 시각부터다.

보존: 원본25개·기존 swap 및 새로운 진단 사본/입력/manifest. 소비자는 원인 진단·Owner 처분이며 대체 근거와 결정 후 재평가한다. active 경로 변경0·삭제0·프로세스0.

### Single Write Diagnostic Result — 2026-10-22T05:06:54.829190+00:00

Owner 승인 메시지 723548390에 따라 고정 manifest의 write 진단1회를 실행했다. worker exit2, PermissionError(errno1/EPERM), traceback atomic_write:111 `new = os.fstat(stream.fileno())`로 실패 연산을 특정했다. 새 swap의 exclusive 생성·mode·34바이트 쓰기·flush·파일 fsync 뒤, 열린 swap fd의 fstat가 실패했다. 경로 기반 os.stat과 rename에는 도달하지 않았다. 이전 os.stat 후보는 확인된 원인이 아니었으며 이번 관측은 더 이른 fstat 실패다. 정확한 Seatbelt 거절 규칙은 아직 미확정이고 권한 추가 실험도 하지 않았다.

근거: `private-evidence/E108`, `private-evidence/E106`. 원본 실패 파일25개·기존 swap의 bytes/mode/inode/nlink 불변과 PID 74271 process-group 부재를 재확인했다. 새 합성 문서도 그대로이며 새 swap은 증거로 보존한다. 재시도0·권한 추가0·S2 자동 재개0, H05/H10 판단 유지. [공개용 중립화]

프로세스/종료 확인 0.132753초(60초 프로세스 상한), 승인부터 해석·보존까지 활동 109.291초/600초. 누적 229.48/960분, 잔여 730.52분(종료20분 포함); S2 96.91/210분, 잔여 113.09분. 직전 대기 75.039008초만 제외했다. 다음 Owner 대기는 이 checkpoint부터이며 사용량을 초기화하지 않는다.

보존: 기존 실패 근거25개·원본·old swap, 이번 고정 입력/코드/profile·출력·결과·new swap. 소비자는 원인 해석과 Owner 복구 판단이며 대체 근거/처분 뒤 재평가한다. active path 이동0, 삭제0, 실행 프로세스0. 진단만 종료했고 본 작업은 미완료 상태로 중단했다.

### Exact Swap Metadata Proposal — 2026-10-22T05:14:29.200832+00:00

Owner 요청 33616778에 따라 fstat 실패의 최소 권한 후보와 검증 조건만 준비했다. 후보 delta는 exact swap 파일 한 개의 file-read-metadata 규칙1행이며 내용/부모/다른 role 권한은 추가하지 않는다. 직전과 동일한 diagnostic worker·요청 bytes, 별도 깨끗한 합성 문서로 전체 atomic write 완료를 판정하도록 고정했다. fstat 통과만으로 충분성을 주장하지 않고 rename·directory fsync·사후 bytes/mode/inode·swap 부재·Reference/원본 불변·group 종료까지 요구한다. 호스트 renderer 한 줄 patch는 미적용 preview이며 source 반영은 단일 검증의 자동 후속이 아니다.

제안 `private-evidence/E111`, manifest SHA-256 `1aa2c830926a557d352a1599b26024cdaedd6f3795bbadab8826c9e77e37f045`. profile 적용0·진단 실행0·source 수정0·approval.json/attempt.json 없음. 기존 두 swap과 실패/진단 파일47개를 유지했고 새 후보의 source/profile/input AST·bytes 비교만 수행했다. 예상2–4분, 활동10분·프로세스60초·종료 확인20초 상한; 승인 후1회, 성공·실패 모두 중단, S2 자동 재개 없음. H05/H10 유지. [공개용 중립화]

준비 활동 3.27분을 누적하고 직전 Owner 대기 258.175465초만 제외했다. 누적 232.75/960분, 잔여 727.25분(종료20분 포함); S2 100.18/210분, 잔여 109.82분. 새 승인 대기는 이 시각부터다.

보존: 기존47개 및 두 swap, 새 권한 후보·preview patch·입력·실행기·manifest. 소비자는 충분성 판정과 Owner source 반영/복구 결정이며 대체 근거와 처분 뒤 재평가한다. 이동0·삭제0·실행 프로세스0.

### Exact Swap Metadata Single Verification Passed — 2026-10-22T05:17:31.565282+00:00

Owner 승인 299389682에 따라 고정 candidate의 swap 한 파일 file-read-metadata 규칙1행만 단일 프로세스에 적용해 write1회를 실행했다. exit0으로 atomic_write 전체가 반환했고, fstat·경로 stat·rename·양쪽 directory fsync·사후 읽기까지 완료했다. trusted controller와 closeout 재확인에서 요청 bytes/sha256, mode 유지, inode 교체/worker 반환 일치, nlink1, 새 swap 부재, Reference 불변, 기존47개·두 기존 swap 불변, PID 84196 group 부재를 확인했다. 새 swap은 정상 rename으로 소모됐으며 cleanup 삭제가 아니다.

이 delta는 기록된 native worker/CPython/OS/profile/합성 입력의 전체 write에 충분했다. 다른 환경/실제 문서/H03 전체나 alias·금지 경로 negative를 통과했다고 확대하지 않는다. source/채택 template는 그대로이며 host-renderer-preview.patch는 미적용이다. 성공 시에도 중단하라는 Owner 지시에 따라 추가 권한0·재시도0·S2 자동 재개0을 유지한다. H05/H10 판단은 그대로다.

근거: `private-evidence/E112`, `private-evidence/E110`. [공개용 중립화]

프로세스/종료 확인 0.076749초, 승인부터 해석·보존까지 90.287초/600초. 기존 Owner 대기 92.077001초만 제외했다. 누적 234.25/960분, 잔여 725.75분(종료20분 포함); S2 101.68/210분, 잔여 108.32분. 다음 Owner 대기는 이 checkpoint부터다.

보존: 기존47개·두 이전 swap, 이번 고정 입력/profile·성공 output·process/stdout/stderr/result/해석. 소비자는 Owner의 정식 반영·후속 적격 판단이며 검증된 대체 근거와 처분 후 재평가한다. active 경로 이동0·cleanup 삭제0·실행 프로세스0. 실제 source와 본 작업은 미완료 상태로 중단한다.

### Host Swap Adoption And S2 Resume Proposal — 2026-10-22T05:23:05.962442+00:00

Owner 요청281940973은 실제 반영/재개 전 준비다. 본 host if swap에서 template 끝에 exact metadata 규칙을 추가하는1행 patch를 고정했다. 기존 preview와 삽입 위치만 달라 성공 profile bytes와 정확히 일치함을 정적으로 확인했으며 diagnostic/production worker 성공 경로 AST도 동등하다. source 수정0, 새 실행0이며 같은 read/write를 반복하지 않고 성공 근거를 재사용한다. controller/role materializer/예산·복구·cleanup 잔여 및 미확인 focused/OS 검사는 원 계획 안에서 완료해야 한다.

제안 `private-evidence/E104`; manifest SHA-256 `70611776019186a312668e43451d149ba17e6ed95b7a9caa3ade15527796439c`. S2예상65–110분/전체잔여예상425–610분 유지, S2 상단추정은 잔여를 넘을 수 있어 완주를 보장하지 않는다. 단계·전체·매핑 세부상한 중 먼저 닿는 조건에서 중단한다. H05/H10 및 원 할당 유지. [공개용 중립화]

이번 준비 4.07분을 누적, 직전 Owner 대기 90.416764초만 제외. 누적 238.32/960분, 잔여 721.68분(종료20분 포함); S2 105.75/210분, 잔여 104.25분. 매핑30분 상한은 첫 재개 전체6.306분+이번 준비를 계상해 잔여 19.63분; 별도 진단은 각 승인과 S2/전체에 이미 포함해 중복하지 않는다. 새 승인 대기는 이 시각부터다.

원본·기존 실패/성공·두 swap 보존. 새 patch/동등성/제안/manifest는 반영과 S2/S3/R1 판단이 소비한다. 검증된 대체/Owner 처분 후 재평가하며 이동0·삭제0·프로세스0이다.

### Host Swap Rule Adopted; S2 Resumed — 2026-10-22T05:25:29.538138+00:00

Owner 승인875230974에 따라 exact 한 줄 patch를 반영했다. 적용 후 host SHA-256은 99d483cc17ff0f11fb0a6e35d218d9feb4f6b51c5ec51e0f93c0b2ffe7c4e248이며 이전 bytes를 task 경로에 보존·동일성 확인했다. 성공 profile byte동등성 및 worker 성공 경로 근거를 재사용해 추가 read/write 실행0이다. S2와 매핑 잔여를 유지하고 runtime/proxy materializer·미완료 집중 항목을 이어간다. H05/H10와 추가 권한/범위/상한 중단은 그대로다.

매핑 종료 상한 2026-10-22T05:44:21.454379+00:00, S2 상한 2026-10-22T07:08:58.942058+00:00, 전체 상한 2026-10-22T17:26:24.597104+00:00. Owner 대기만 97.859775초 제외했고 사용량 초기화는 없다.

### S2 Native Policy Directory Permission Gap — 2026-10-22T05:28:24.607291+00:00

승인된 host swap 한 줄은 exact source에 반영했고 성공 근거/profile 동등성을 재사용했다. runtime 명세 연결을 위한 정적 대조에서 native exec-policy 로더의 fs::read_dir가 기존 `private-evidence/E002` 디렉터리를 열거해야 하지만, 채택 runtime profile은 exact .rules 파일과 ancestor metadata만 허용해 디렉터리 읽기 규칙이 없음을 발견했다. source chain은 native user config→Inherit root session→ExecPolicyManager→collect_policy_files/read_dir로 확인했다. rules 디렉터리 및 default.rules 이름/metadata만 관측했고 내용은 읽지 않았다. [공개용 중립화]

이는 source/profile 정적 불일치이며 runtime에서 EPERM를 재현한 결과가 아니다. 한 디렉터리 규칙만 추가하면 전체 runtime이 통과한다고 주장하지 않는다. 추가 권한 필요 시 중단하라는 Owner 지시에 따라 runtime rule 추가·loader 우회·새 실행 없이 중단했다. 별도 disposition 전 S2를 자동 재개하지 않는다. H05/H10 유지.

근거 `private-evidence/E105`. host SHA-256 99d483cc17ff0f11fb0a6e35d218d9feb4f6b51c5ec51e0f93c0b2ffe7c4e248; 이전 bytes와 patch/adoption 결과 보존. runtime/proxy materializer는 아직 미완료, worker 재실행0·build/runtime/proxy/auth/provider/Core/actual/R1 실행0이다. [공개용 중립화]

이번 재개 활동 3.68분(중단 보존 포함), 매핑30분 잔여 15.95분. 누적 242.00/960분, 잔여 718.00분(종료20분 포함); S2 109.43/210분, 잔여 100.57분. 시간 상한 도달이 아니라 추가 권한 경계로 중단했으며 다음 Owner 대기는 이 checkpoint부터다.

보존: 원본/실패/성공/두 swap, host 반영 전 bytes와 적용 후source·patch·동등성, 이번 정적 source-chain 근거. 소비자는 runtime 권한 disposition 및 S2/S3/R1이며 대체 근거와 Owner 판단 후 재평가한다. active path 이동0·삭제0·프로세스0.

### Native Policy Minimum Permission Proposal — 2026-10-22T05:37:47.569703+00:00

Owner 요청30108065에 따라 실제 권한 변경/S2 재개 없이 최소 후보만 준비했다. native loader는 System/User/활성 Project의 rules를 조회하며 config 부재도 required System/User 계층을 없애지 않는다. base User SLOT/home는 기존 권한으로 충족하고, metadata-only ancestor 조사에서 외부 Project 추가 후보는 없다. MDM/Enterprise/legacy/flags에는 별도 rules 폴더 권한이 필요하지 않으며 requirements inline 정책과 native trust는 그대로 유지한다.

현재 외부 후보는 사용자 rules 디렉터리의 목록 읽기와 현재 부재인 System rules 경로의 부재 조회, 각 exact metadata다. directory predicate와 exact literal만 제안하고 기존 default.rules1개 내용/metadata 권한은 재사용한다. 모든 entry의 file_type 확인이 확장자 필터보다 앞서지만 현재 비-.rules 추가 항목은 없다. 새 항목/alias/경로는 자동 허용하지 않는다. System missing 경로의 실제 ENOENT 전달과 runtime OS 충분성은 아직 미검증이며 추가 실행 없이 승인 뒤 기존 S3 영향 OS gate에 남긴다. 정책/설정/auth 내용은 이번에 읽지 않았다.

제안 `private-evidence/E101`, metadata/source 근거 `private-evidence/E102`, manifest SHA-256 `359fc4c22b282ae5b1a9cf3d915004fddc1aaf8234dce90da265ff418e91f26e`. 기존 source-chain·host·template·approved plan 해시 및 새 참조 source 해시가 일치했고 manifest 정적 확인을 통과했다. 실제 permission/template/mapping/source 변경0, build/test/review/runtime/auth/provider/Core/target/R1 추가0이다. worker read/write 성공과 host byte/AST 동등성 근거를 재사용하며 H03/H05/H10 판단을 승격하지 않는다. [공개용 중립화]

이번 준비 6.44분을 전체/S2/mapping에 보수적으로 차감했다. 직전 Owner 전용 대기 176.625957초만 제외했다. 누적 248.44/960분, 잔여 711.56분(종료20분 포함); S2 잔여 94.13/210분; mapping30분 잔여 9.51분. 기존 예상 S2 65–110분/전체425–610분과 모든 단계별 상한을 유지하며 예상 상단이 잔여를 넘을 수 있음을 유지한다. 다음 Owner 대기는 이 checkpoint부터다. 권한 후보 채택과 S2 재개는 모두 미승인이다.

보존: 원본/실패/성공/두 swap/host 적용 전후 및 새 proposal/meta/manifest. 소비자는 권한 처분과 S2/S3/R1이며 대체 근거와 Owner 처분 뒤 재평가한다. active 경로 이동0·삭제0·실행 프로세스0. STATUS/index 변경은 필요하지 않아 수행하지 않았다.

### Native Policy Profile Adopted; S2 Resumed — 2026-10-22T05:57:33.258741+00:00

Owner 승인650244841의 두 exact rules 디렉터리 data/metadata 후보를 별도 runtime template에 반영하고 effective mapping을 결속했다. 기존 template/manifest는 보존했다. source/entry/topology 동일성을 재확인했으며 worker 성공 근거는 재사용한다. System 부재 처리는 기존 S3 gate에 남긴다. runtime/proxy 명세 materializer를 계속하며 H05/H10와 추가 권한/경로/범위/상한 중단을 유지한다.

새 mapping `private-evidence/E100`; runtime template SHA-256 abb4176852e0c97954c6fdd1d689e9a603d76f1d875a70fe73cad30832cfb07e. 매핑 잔여570.510633초의 deadline은 2026-10-22T06:06:08.789337+00:00, S2 2026-10-22T07:30:46.277016+00:00, 전체 2026-10-22T17:48:11.932062+00:00이다. Owner 대기 1130.709001초만 제외했고 사용량 초기화0이다. 아직 runtime/proxy/auth/provider/Core/target 실행0이다. [공개용 중립화]

### S2 Role Mapping Implementation Checkpoint — 2026-10-22T06:03:25.455864+00:00

승인한 native rules delta를 반영한 runtime과 기존 proxy/worker template를 결속했다. task-owned `materialize-roles.py`는 native inventory drift/extra path 거절, exact ancestor/file literals, Runtime Spec와 host binding, proxy public IP literals·단일 예약 snapshot을 생성한다. 새 global budget/candidate를 만들거나 실제 process/DNS/auth를 호출하지 않는다. 별도 합성 fixture의 명세 필드/해시/append.lock 연결/권한 확대/재사용 거절18개를 통과했고 실제 clock slot의 정적 치환도 확인했다. 이는 OS profile compile 또는 native runtime 적격이 아니다.

근거 `private-evidence/E103`; helper SHA-256 40efdc57f19109889187ee81a8cb378501ef0a0b936578672b9a9431cac2b238. 이번 native adoption+mapping 활동 6.79분을 차감해 mapping30분 잔여 2.72분을 보존한다. 이후 추가 role/profile mapping이 필요하면 이 잔여를 사용하며 초기화하지 않는다. 전체 누적 255.23/960분, S2 잔여 87.35분이다. S2 자체는 계속 active이며 남은 host failure/cleanup·verifier 집중 확인 및 최종 build 준비를 수행한다. System 부재/S3 및 H05/H10 gate 유지. 실제 role slots/global budget/runtime/proxy/auth/provider/Core/target 실행0이다. [공개용 중립화]

원본 template·성공 근거·host 복구와 이번 helper/합성 입력/결과는 S2/S3/R1 소비가 남아 보존한다. active 경로 이동0·삭제0·실행 프로세스0.

### S2 Implementation Checkpoint — 2026-10-22T06:15:44.157945+00:00

native worker DOC-CLAIMS/LINKS/GFM의 positive3·negative2 총5개 확인 PASS, H08 시작실패/프로세스기록실패/기존run보존/Core timeout 정리 집중 검사 PASS. 새 권한·실제 runtime/provider/Core/target 호출0. S2의 잔여 연결과 S3 실행 준비를 계속한다.

S2 실측 134.96분 /210분, 통합 누적 267.54분 /960분, 잔여 692.46분(종료20분 포함). actual auth/provider/target/authority/reviewer 미실행이며 H01–H10 미적격 상태를 유지한다. 기존 source·원문 복구와 검사 근거는 S2/S3/R1 소비가 남아 보존한다. Active path 이동·삭제0.

### S2 Implementation Checkpoint — 2026-10-22T06:27:57.640850+00:00

기존 고정 focused47 PASS(실패/skip0, 입력 drift0, group absent). host8 및 추가 H08, Rust App6/Core16, role materializer18, native worker read/write·verifier5의 해당 근거를 재사용한다. S2 구현/집중 범위를 닫고 S3 candidate build·OS/fixture8/ordinary 적격으로 이동한다. H01–H10 실제 적격은 별도이며 H05/H10 Owner gate 유지.

S2 실측 147.19분 /210분, 통합 누적 279.76분 /960분, 잔여 680.24분(종료20분 포함). actual auth/provider/target/authority/reviewer 미실행이며 H01–H10 미적격 상태를 유지한다. 기존 source·원문 복구와 검사 근거는 S2/S3/R1 소비가 남아 보존한다. Active path 이동·삭제0.

### S2 Complete; S3 Qualification Started — 2026-10-22T06:28:01.842084+00:00

S2 구현과 집중 범위를 완료했다. 기존47개는 모두 PASS, 추가 host H08·verifier5·materializer18 근거를 연결하고 바뀌지 않은 host/Rust/worker 검사는 재사용한다. 실제 OS 전체·native 인증/정책/model·installed H05·H10을 단위 결과로 승격하지 않는다. source/원문·실패/성공 근거는 S3–S7 소비가 남아 보존한다. 추가 권한·경로·scope 확대와 mapping 잔여 상한 중단은 유지한다.

S2 활동 147.26/210분, 통합 누적 279.83/960분, 잔여 680.17분(종료20분 포함). mapping 잔여 2.72분 유지. S3 상한150분, 최초 build90분; S3 deadline 2026-10-22T08:58:01.842084+00:00. 남은 S3–S7 예상360–500분은 기존 단계별 판단값 합계이며 Owner-only 대기 제외/중첩1회 계상, OS/auth 적격 미확인으로 신뢰 낮음.

고정 helper run-s3-build.py/register-s3-candidate.py/run-s3-offline.py/run-s3-runtime-os.py를 준비했다. 원 fixture oracle16개 함수 및 Server 동작은 그대로이며 경로/장부 연결만 달라진다. 첫 static AST 비교는 profile 기록 경로까지 동일하다고 요구해 prelaunch에서 멈췄고, 해당 경로 차이만 제외한 재대조를 통과했다. 이는 실행 실패/보정 묶음이 아니며 actual run0이다. Git/STATUS 변경·active 경로 이동·cleanup 삭제0.

### S3 First Build Failure And Bounded Correction — 2026-10-22T06:36:12.536973+00:00

최초 build1회는 300.169초 뒤 app-server/src/lib.rs:2712의 http::HeaderMap 정규 dependency 가시성 오류(E0433)1개로 실패했다. 기존 unit build는 dev-dependency http를 볼 수 있어 이 문제를 잡지 못했다. 프로세스 종료·입력 source/기존 accepted binary 불변을 확인했다. 정규 dependency axum0.8.8의 pub use http를 확인하고 같은 타입 경로를 axum::http::HeaderMap으로 한 줄 보정했다. 새 crate/Cargo/lock/권한 변경0이며 헤더 판정 로직은 그대로다. 보정 묶음1/2를 사용하고 build2/3을 준비했다. 원 최초 build 시작 기준90분·S3/전체 잔여를 유지한다. 동일 타입/불변 판정의 unit 근거를 재사용하고 실제 production build로 연결을 검증한다.

### S3 Runtime Profile Compile Stop — 2026-10-22T06:41:06.419000+00:00

한 줄 보정 뒤 build2는 30.490초에 통과했다. 첫 build 시작부터90분 안에 동일 candidate의 ordinary/fixture/live3개 binary를 얻었으며, 원 accepted2개 binary·성공 이후 source/binary 불변을 확인했다. build2/3·보정1/2 사용을 원 시간 장부와 공통 runtime journal에 이월했고 새 예산을 시작하지 않았다.

이후 고정 runtime profile의 OS canary1회에서 sandbox-exec가 exit65로 profile 컴파일을 거절했다: `host must be * or localhost in network address`, exact `(remote tcp "127.0.0.1:38971")` (runtime.sb:16). C canary 본문은 시작되지 않았고 stdout0, User rules 열거·System ENOENT 확인0이다. 따라서 System 부재가 실패했다고도, 통과했다고도 판정하지 않는다. 다른 주소 표기의 기존127.0.0.1 단일 endpoint와 권한 동등성이 미확정이므로 자동 교체·권한 확대·재실행 없이 중단했다. C helper compile은 기존 builder profile의 검사용 compile이며 runtime candidate build를 추가하지 않았다.

근거: `private-evidence/E123`. 네 build/compile/probe process group 부재를 재확인했다. 실제 model runtime/proxy/credential/provider/actual target/H05/H10 실행0. 준비한 worker negative14개·offline fixture8·ordinary smoke는 미실행이며 별도 근거로 주장하지 않는다. H01–H10은 전체 미적격, H05/H10 Owner 판단 유지. [공개용 중립화]

중단 시 통합 활동 292.91/960분, 잔여 667.09분(종료20분 포함); S2 147.26/210분 완료, S3 13.08/150분, 잔여 136.92분. 매핑 잔여 2.72분은 그대로다. 이번 검사는 매핑 구현 변경 없이 S3 적격 시간에 계상했다. Owner-only 대기는 공통 journal pause seq4와 이 시각부터이며 기존 사용량을 초기화하지 않는다. 권한/표현 처분 전 새 완료 예상은 제시하지 않는다.

보존: original/changed source·복구 patch·기존/새 binary·실패/성공 입력과 로그 및 미실행 S3 helper. empty `integrated-execution/runtime/clock-01/{home,cwd,tmp}`는 이번 exact profile/argv의 다음 bounded 처분이 소비하는 probe topology이며 실제 live start가 아니다. 처분/재할당 또는 포기 때 재평가하고 materializer가 조용히 재사용하지 않는다. active 경로 이동0·삭제0, source commit/push/STATUS 갱신0.


### S3 Address Static Disposition — 2026-10-22T06:47:47.927400+00:00

Owner 요청에 따라 정적 확인과 최소 수정·검증안을 작성했다: `private-evidence/E113`. localhost는 다른 로컬 주소까지 허용할 수 있어 tcp/tcp4 단순 치환의 기존 IPv4 단일 endpoint 동등성을 인정하지 않는다. 현재 적용 가능한 동등 표현은 미확정이다. profile 변경/재실행/ledger resume0, H05/H10·기존 단계/누적/매핑 상한 유지. 별도 정적 준비 활동 235.561초와 이후 보고 활동은 다음 누적/S3 정산에 한 번 이월하며 Owner-only 대기로 제외하지 않는다. 기존 실행 장부는 중단 상태 그대로다. [공개용 중립화]


### S3 Endpoint Alternatives — 2026-10-22T06:55:34.923268+00:00

Owner 요청에 따른 구현 전 비교: `private-evidence/E117`. 기존 client/proxy는 정확한 주소를 이미 고정하며 profile-only 동등 보정은 확인되지 않았다. 최소 구조 변경 후보는 runtime IP 전면 거부 + 전용 UDS + 신뢰 host의 고정 CONNECT 중계다. 직접 TCP/OS-per-process 경계 유지와는 구분하며 새 IPC/host 책임을 현재 승인에 포함하지 않는다. runtime 구간180–300분, proxy 구간 포함 조건부300–540분은 낮은 신뢰의 활동 예상이고 기존 S4–S7 제외다. proxy bind/inbound·외부 숫자 IP profile 위험도 별도 미해결로 기록했다. 기존 S3/매핑 잔여로 실행 불가, source/profile/ledger/journal 변경·재실행0, H05/H10 판단 유지. 이번 비교 활동 351.687초와 후속 보고 시간은 누적/S3에 한 번 이월한다. [공개용 중립화]


### Network Boundary Revised Execution Proposal N-01 — 2026-10-22T07:12:54.174403+00:00

Owner 요청에 따라 `private-evidence/E121`을 준비했다. 시간 절감을 위한 단순 우회가 아니라 runtime/proxy IP권한 제거·고정 중계·원 TLS/native auth 재사용을 택하되, 외부IP의 독립 OS 제한을 유지하려면 역할별 제한 identity/출구 필터가 추가로 필요하다. PF의 safe hook/loopback/identity 적격을 먼저 확인하고 실패 시 No-Go; 코드 검사만 남기는 fallback은 없다. 현재 /etc/pf.conf 읽기만 했고 active PF 적격은 미확인이다. [공개용 중립화]

새 N 예상480–780분, 후속 필수 작업 포함 남은795–1220분. 전체 cap960→1800, 새N900, mapping30→180(+150), build3→5, correction2→3 등은 모두 미채택 증분 제안이다. 기존 사용/매핑 잔여/H05/H10 및 pause4 유지. 기존 journal candidate 고정으로 인한 append-only amendment/transition과 재사용/필수검증도 포함했다. 첫 두 준비 구간 전체732.421463초와 이번802.509347초 및 이후 전달 활동을 누적/S3에 한 번 이월하며 과거 부분 준비 기록과 중복 합산하지 않는다. 구현/profile/OS/ledger 변경·재실행·reviewer 호출0.


### N-01 N0 Read-Only Eligibility — 2026-10-22T07:25:30.291010+00:00

Owner 요청에 따른 읽기 전용 조사와 조건부 identity/설치/회수 패킷: `private-evidence/E119`. 후보 계정/그룹 `_u2_ingress`45001, `_u2_egress`45002는 현재 local/Search ID 목록과 조회 가능한 프로세스에서 충돌 없음. 일반 PF 조회는 /dev/pf0600으로 거절됐고, host의 sudo -n 조회도 관리자 password가 필요해 활성 규칙/skip/reference를 확보하지 못했다. 디스크에는 Apple anchor만 존재하므로 safe task hook 미확정, 설치·구현 진입 No-Go다. OS 불가능 또는 기존 앱 무영향을 입증한 것은 아니다. [공개용 중립화]

UID PF는 TCP/UDP에 한정하고 다른 family는 Seatbelt 경계로 별도 검증해야 한다. 차단만 추가해 기존 앱 정책을 덮지 않는 anchor 후보, 홈 권한 변경 없는 별도 root 설치본/UDS 경로, 정확한 UID 전환·소켓 생성 순서, 프로세스·state 확인 후 task만 회수하는 패킷을 구체화했다. root hook 설치/제거 방법과 actual OS proof는 미해결이다. 관리자 읽기 전용 추가 조회 명령을 남겼으며 비밀번호/OS 설정/계정/source/profile/실행/상한 변경0, reviewer 호출0이다.

보호 입력15개와 journal/pause4 유지. 확정 전체292.908117분·mapping 잔여2.722225분·build2/3·correction1/2·H05/H10 판단 유지. 앞선 세 정적 구간1702.305283초와 이번484.067968초 및 후속 전달 시간을 누적/S3에 한 번 이월한다. 이전 부분 기록과 중복 합산하지 않는다. STATUS 변경 불필요, active path 이동0·삭제0, 기존 required evidence와 이번 패킷을 후속 N0/S3–S7 처분까지 보존한다.


### N0 Authenticated PF Snapshot Assessed — 2026-10-22T07:39:35.935235+00:00

Owner가07:34:52 UTC에 수집한 `pf-readonly-01/`을 정적으로 판정했다: `private-evidence/E118`. PF Enabled, state213개, pfd reference1개. root 전후 byte/hash는 동일하며 Apple wildcard와 internet-sharing 호출만 존재한다. 독립 task hook이 없으므로 task anchor만 적재하는 현재 N-01 경로는 성립하지 않아 설치/구현 No-Go를 유지한다. disk 기본 파일과 달리 활성 root에는 internet-sharing 경로가 있어 단순 root reload의 기존 서비스 보존을 보장할 수 없다. [공개용 중립화]

재귀 filter 조회는 rc0이지만 DIOCGETRULES Invalid argument가 있어 전체 하위 규칙 확인으로 인정하지 않는다. shared_v4 일부만 관측했고 skip 표시는 없으나 실제 UID/loopback 적격·앱 무영향 증거는 아니다. 원본 collected 상태와 오류 로그를 그대로 보존하고 이 판정으로 범위를 한정한다. 추가 조회/OS 변경/구현/재실행/상한 확대0, 보호 입력15개/수집기 원본 불변, mapping 잔여2.722225분·H05/H10 판단 유지.

앞선 전체 준비+수집 미반영 활동2494.620555초와 이번247.285057초 및 후속 전달 활동을 누적/S3에 한 번 이월한다. 이전 부분 구간은 전체 구간으로 대체하고 중복 합산하지 않는다. 확정 ledger292.908117분·pause4 유지. 원본/복구/수집파일과 판정은 후속 N0/S3–S7 처분까지 보존, active path 이동0·삭제0, STATUS 변경 불필요다.


### PF Hook Preservation And Isolation Static Assessment — 2026-10-22T07:49:16.080758+00:00

Owner 요청에 따라 `private-evidence/E120`를 준비했다. Apple XNU source에 DIOCCHANGERULE 및 owner/priority/ticket 기반 INSERT/DELETE 기구가 있어 full root reload 없이 개별 변경하는 기술적 경로는 있다. 그러나 private ABI, GET_TICKET의 변경 효과, 타 PF writer와의 경쟁, 동적 reload 후 hook 소실, exact 회수와 state 수명 때문에 현재 host에서 안전하게 채택할 근거는 없다. 기술적 불가능으로 단정하지 않고 PF 후보 보류를 권고했다. [공개용 중립화]

동일 Mac/native auth/endpoint 유지의 다음 설계 후보로 공식 NE content filter를 추천하되 role identity·loopback/IP·장애 시 차단 유지·기존 앱 공존을 선행 적격으로 남긴다. VM/별도 Mac은 환경·인증·실제 actor를 바꾸며 NAT/host relay가 독립 출구 제한을 자동 해결하지 않는다. H05/H10 승격/환경 이관 승인0이다. 이번에는 저장 snapshot/로컬 manual/공식 source 정적 확인과 보고서만 수행했고 OS/ioctl/구현/재실행/상한 변경0이다.

확정 장부292.908117분·mapping 잔여2.722225분·pause4·build2/3·correction1/2 유지. 직전 해석 전체358.808679초를 부분 기록 대신 반영한 이전 pending2853.429234초와 이번404.874909초 및 후속 전달 활동을 전체/S3에 한 번 이월한다. evidence/복구/새 보고서는 후속 판단 소비가 남아 보존하며 active path 이동0·삭제0, STATUS 변경 불필요다.


### Imported Claude Static Review; Driver Disposition — 2026-10-22T08:06:56.040954+00:00

Owner가 2026-10-22T07:59:30.170900Z에 제공한 Claude 정적 검토를 가져왔다. 목적은 기존 PF No-Go와 최소 대안을 재평가하는 것이며, reviewer 실행·구현·OS 변경·canary·상한 확대 요청으로 해석하지 않는다. Driver는 Codex, Reviewer는 Owner가 별도로 의뢰한 Claude이며 모델/세션 ID/authentication/billing path는 알려지지 않았다. Codex가 새 reviewer를 호출하거나 계정 정보를 조회하지 않았다. 별도 reviewer라는 점 외의 독립성은 보증하지 않는다.

원문 attachment: `private-evidence/E001 텍스트.txt`, SHA-256 `0b5617c7582520ac3207e2bec2b29340d78302b1b817a83e86cb7300c1fea510`, 52,450 bytes. 아래 fenced block 내부에 원문 bytes를 그대로 보존했다. 소비자는 Owner 처분 및 후속 S3 검증이며 그 처분과 검증이 끝날 때 보존 필요를 재평가한다. 별도 복사/리뷰 문서는 만들지 않았다. [공개용 중립화]

Reviewer는 일부 파일·일부 행과 SHA-256 앞 8자만 보고했다. 현재 비교 시 아래 전체 해시의 해당 prefix와 일치하며 이는 reviewer가 전체 파일을 검토했다는 뜻이 아니다. Review 당시 source base/diff digest는 제공되지 않아 당시 revision은 확정할 수 없다. 현재 참고 HEAD: Codex `83086188ae0614bd882818ff1aa23f3194962012`, Colvia `7d012f5297de1d9a77aa0b8187406f4785221573`. Work의 검토 전 전체 해시는 `dd08fb0151819877fd3e3bd250fef22aa88226ead79a11cc3ddf20990ee2aef7`; 원문이 명시한 Work136–153/http_proxy505–545/materializer100–135 한정을 유지한다. 최신 PF hook 보고서는 reviewer가 의도적으로 제외했으며 그 문서에 대한 리뷰가 아니다.

현재 비교한 입력:
- `private-evidence/E118`: `4830b4aad7c1f21072cb5631874dd7eaefcb776742aafe9a1b694b0d9d42946e` [공개용 중립화]
- `private-evidence/E121`: `cdee0f0e2583746995eefebb88bc54c7e64f718df5b09418b25f0f3b8f9663c4` [공개용 중립화]
- `private-evidence/E119`: `61f4049bba8fb9c653c0f6c25ef9fa9a46aa839d776132918a27f6ab3cbfbf57` [공개용 중립화]
- `private-evidence/E117`: `5ba6ae411409a8c18187a0b7c47a1148c2f370c4e024cae646564434cb924478` [공개용 중립화]
- `private-evidence/E113`: `f7020ec8f735aec877d75c2c5118681a7f32d5bb95c3ccddd188be491480c796` [공개용 중립화]
- `private-evidence/E122`: `6ad608f70e87c74a90be58b4162697e12081fc2f6a89477f599fe752dc41f66c` [공개용 중립화]
- `private-evidence/E099`: `f17c458fa8b5e91aaa00bd0adcb09320bf9f29a4cd3e4f12cb6fa6ccb135250f` [공개용 중립화]
- `private-evidence/E098`: `40efdc57f19109889187ee81a8cb378501ef0a0b936578672b9a9431cac2b238` [공개용 중립화]
- `private-evidence/E120`: `e139069276285245d94df055c524e4db059170c82e54a81fb9c5541c27c5d19e` [공개용 중립화]
- `private-evidence/E160`: `de8ac4fa9317c8440abc79fbe2c040ae85f1e665ebcbe48baa8e8fb919290101` [공개용 중립화]

PF 수집 파일16개는 이번 기록 전후 불변으로 확인한다. Reviewer는 probe/build/test/OS 변경을 하지 않았다고 보고했으며, Driver도 이번 검토에서 실행 검증을 하지 않았다. 아래 판단은 source·문서 정적 비교이며 재현 결과가 아니다.

#### Driver disposition

- accept/revise — proxy 외부 연결에 대한 connected-FD 후보를 우선 조사 대상으로 올린다. 이전 대안 문서에는 proxy capability 가능성의 짧은 언급이 있었지만, runtime 쪽 적용 제약에 비해 proxy egress 적용을 충분히 구체화·비교하지 않았다. NE 우선 추천을 수정하며, C-FD의 좁은 사전 검증을 먼저 검토할 가치가 있다. C-FD 채택이나 실행 승인은 아니다.
- accept with limit — 공개 Apple XNU의 `sendit` 목적지 검사와 `soo_read/soo_write` 경로는 연결된 FD I/O 가능성을 뒷받침한다. 해당 함수에서 검사가 보이지 않는다는 사실만으로 설치 OS 전체의 Sandbox 경로를 배제할 수 없다. Reviewer §6의 한정을 적용하며, “막을 hook 자체가 없다”는 앞부분 단정은 채택하지 않는다. 참조: https://raw.githubusercontent.com/apple-oss-distributions/xnu/main/bsd/kern/uipc_syscalls.c 및 https://raw.githubusercontent.com/apple-oss-distributions/xnu/main/bsd/kern/sys_socket.c .
- defend/clarify — 기존 PF No-Go를 유지한다. 동적 root reload로 task hook이 사라지는 위험과 VM NAT의 host 영향은 reviewer가 제외한 최신 PF hook 보고서에서 이미 다뤘다. 재귀 조회 오류의 위치는 좁힐 수 있는 가설이며 하위 규칙 전체 확보로 승격하지 않는다. snapshot만으로 PF writer를 특정하지 않는다.
- needs-user — 이전 Owner 지시는 `127.0.0.1:38971` endpoint와 승인 범위를 유지했다. 따라서 TCP→UDS를 단순 구현 선택으로 자동 변경할 수 없다. controller의 frozen-IP 연결/FD 발급 책임도 새 신뢰 경계이며, 기존 Work139의 범위 처분이 필요하다. Reviewer 제안 자체는 범위 승인이나 Owner 수락이 아니다.
- revise — controller 종료는 새 FD 발급을 멈추지만 proxy가 이미 보유한 TCP FD를 자동 회수하지 않는다. controller의 마지막 자체 참조 close와 공유 socket에 대한 shutdown은 다르다. controller 비정상 종료 시 기존 host 감독에 의한 proxy 종료/연결 회수, deadline, 재시작과 중복 발급까지 검증할 계약이 필요하다. 평상시 shutdown canary만으로 crash fail-closed를 주장하지 않는다.
- revise — 같은 UID에서 controller가 소유한 UDS 디렉터리라는 이유만으로 runtime/proxy의 경로 교체를 막을 수는 없다. exact UDS와 부모 경로에 대한 create/unlink/rename 등의 OS 쓰기 제한, 상속 FD 최소화와 전달 검증이 필요하다. 이 사항은 구현 변경 없이 후속 검증 요건으로 남긴다.
- revise — canary 통과는 OS 기구의 부분 적격이다. Rama/Tokio의 UDS accept·FD 연결, CONNECT·end-to-end TLS·native auth, 예약/총량/재발급 방지, candidate/journal transition, controller 장애 회수 및 H05/H10을 대신하지 않는다. I-1a가 기존 CONNECT 의미를 더 유지하는 후보지만 채택 전 연결 경로 검증이 필요하다. I-1b는 CONNECT 단계 생략의 제품 의미 변경을 별도 판단해야 한다.
- revise — 제안된 거부 oracle도 실행 전 정리해야 한다. 연결된 TCP에 다른 목적지로 sendto가 EISCONN 등 protocol 제약으로 거절될 수 있으며, 이는 sandbox EPERM과 다른 근거다. UDP socket 생성 금지와 생성 후 통신 금지는 각각 판정해야 한다. ECONNREFUSED/timeout을 OS 격리 통과로 인정하지 않는 원칙은 유지한다. Reviewer §5의 30–60분은 좁은 canary 준비/검사 예상이며 전체 구현·통합 예상 또는 승인 상한으로 사용하지 않는다.

#### Actual Owner decisions and accounting

Owner는 검토 답변만 제공했다. C-FD 채택, TCP→UDS/신뢰 경계 변경, canary 실행과 시간 할당, 구현/OS 변경/상한 확대는 결정되지 않았다. 기존 ledger 확정292.908117분, mapping 잔여2.722225분, build2/3, correction1/2, pause4, H05/H10 미적격과 Owner 판단을 유지한다. 기존 정적 분석 pending도 없애지 않는다. 이번 Driver 활동은07:59:30.170900Z부터 이 checkpoint와 이후 검증/보고까지 기존 전체/S3 정산에 한 번 이월하며 mapping 또는 미채택 N 예산으로 옮기지 않는다.

Reviewer는07:50:13–07:56:33 UTC의380초와 이후 답변 작성 시간을 보고했다. 종료 시각이 없어 총량은 미확정이다. 직전 Driver 구간과 겹치는 시간은 중복 차감하지 않고 구간 합집합으로 정산해야 하므로380초를 그대로 기존 pending에 더하지 않았다. 현재 기록은 장부 초기화·대기시간 소급 면제·상한 변경이 아니다.

기존 source/profile/OS/PF/ledger/journal 변경0, build/test/probe/reviewer 호출0, Git commit/push/STATUS 변경0. 기존 Work에 이 import와 처분만 추가했다. Active 경로 이동·삭제0. 기존 실패/성공/복구 입력과 PF 근거의 소비 목적은 그대로다.

#### Reviewer response — verbatim

~~~~text
⏺ macOS 네트워크 격리 정적 리뷰: 최소 해결책과 No-Go 판단 검증

  결론

  - 기존 No-Go는 타당합니다. 기존 hook만 써서 PF로 진행하는 경로는 이 host에서 성립하지 않습니다.
  - 다만 추천 순서는 바꿔야 합니다. 놓친 더 작은 OS 강제 방식이 있습니다.
  - 그 방식은 이렇습니다. proxy는 IP socket을 새로 만들지도, 연결하지도 못하게 합니다. 외부로 나가는 연결은 trusted controller가 frozen IP:443에 미리 연결해
    둔 TCP FD로만 받습니다. runtime은 정확한 UDS 경로 하나만 허용합니다.
  - 이렇게 하면 broker 두 개, 새 UID 두 개, PF, 전역 필터가 모두 필요 없습니다. 관리자 권한도 들지 않습니다.
  - 이 방식이 되는지는 결정적인 offline canary 한 번으로 판정할 수 있습니다. 이 canary가 실패할 때만 Network Extension과 PF private ioctl을 비교할 가치가
    생깁니다.

  판정을 바꾸는 근거는 두 가지입니다.
  1. [source] Apple XNU 공개 source에서 연결된 TCP socket의 send/recv는 MACF 검사를 거치지 않습니다. Seatbelt는 MACF로 동작하므로 이 경로를 막을 hook이
     없습니다. 근거는 아래 B-0에 있습니다.
  2. [source + 관측] PF로 추가한 task hook은 다른 writer가 root를 commit하면 조용히 사라집니다. 사라지면 결과는 fail-open, 즉 차단이 풀리는 쪽입니다. 그런데
     이 host의 root에는 /etc/pf.conf에 없는 hook이 이미 동적으로 들어가 있습니다. 런타임에 root를 바꾸는 시스템 writer가 있다는 뜻입니다. 그래서 N-01 §3의
     fail-closed 조건은 PF 경로로는 구조적으로 충족되기 어렵습니다.

  제안 C-FD (broker·UID·PF 없음)
  runtime ──[Seatbelt: 정확한 UDS path-literal 하나만]──▶ proxy(상속받은 UDS listener)
                                                           │ 신규 IP connect/socket/DNS 금지
                                                           │ 외부 연결은 받은 FD로만
  controller ──connect(frozen IP:443)──▶ 연결된 FD ──SCM_RIGHTS(상속 socketpair)──▶ proxy
  (주소 입력 없음 · 예약 단위 발급 · getpeername 대조 · dup을 보관해 shutdown으로 회수)

  ---

  1. 현재 판단의 오류와 누락

  ┌─────┬───────────────────────────────────────────┬───────────────────────────────────────────────────────────────────────────────────────┬─────────────┐
  │  #  │                   위치                    │                                         내용                                          │    구분     │
  ├─────┼───────────────────────────────────────────┼───────────────────────────────────────────────────────────────────────────────────────┼─────────────┤
  │     │ s3-endpoint-alternatives-01.md 표의 "사전 │ FD 전달을 runtime 구간에만 평가하고 후순위로 미뤘습니다. proxy egress 구간에는 적용해 │ 누락, 정적  │
  │ 1   │  연결 TCP FD 전달" 행                     │  보지 않았습니다. egress 구간에 쓰면 egress broker, UID, PF가 통째로 빠집니다. N-01이 │ 추론        │
  │     │                                           │  커진 주된 이유가 바로 이 구간입니다.                                                 │             │
  ├─────┼───────────────────────────────────────────┼───────────────────────────────────────────────────────────────────────────────────────┼─────────────┤
  │     │ 같은 문서의 "sandbox 후 해당 FD의 I/O     │ 공개 source로 상당 부분 줄일 수 있는 불확실성입니다. 아래 B-0을 보면 sandbox가 연결된 │ 정정,       │
  │ 2   │ 가능성도 미검증"                          │  FD의 I/O를 막을 hook 자체가 없습니다. 다만 설치된 26A434와 같은지는 실행으로         │ source      │
  │     │                                           │ 확인해야 합니다.                                                                      │             │
  ├─────┼───────────────────────────────────────────┼───────────────────────────────────────────────────────────────────────────────────────┼─────────────┤
  │     │ N-01 §3의 fail-closed 조건, eligibility   │ 의도적 root 공격은 신뢰 가정 밖으로 뒀지만, 정상 시스템 서비스가 root를 다시 적재하는 │ 누락,       │
  │ 3   │ 문서의 "차단만 하는 anchor, 허용은 기존   │  경우는 다루지 않았습니다. 그렇게 되면 task hook이 사라지고 broker 트래픽이 무제한이  │ source와    │
  │     │ 정책으로 반환"                            │ 됩니다. egress broker의 Seatbelt는 IP를 좁힐 수 없어서(* 또는 localhost만 허용) 다른  │ 관측에서    │
  │     │                                           │ 방어선도 없습니다.                                                                    │ 추론        │
  ├─────┼───────────────────────────────────────────┼───────────────────────────────────────────────────────────────────────────────────────┼─────────────┤
  │     │                                           │ "새 proxy/broker … 이 변경이 필요하면 통합안도 중단"으로 고정돼 있습니다. N-01은      │             │
  │ 4   │ Work 파일 line 139                        │ broker 두 개를 새로 만들므로 이 고정 범위와 직접 충돌합니다. N-01 §2 끝에 "별도 Owner │ 누락, 문서  │
  │     │                                           │  구조 승인"이라고 적혀 있지만, 이후 N0 문서들은 이 범위 조건을 다시 거론하지          │ 근거        │
  │     │                                           │ 않습니다. C-FD도 범위 판단이 필요하지만 새 process를 만들지 않습니다.                 │             │
  ├─────┼───────────────────────────────────────────┼───────────────────────────────────────────────────────────────────────────────────────┼─────────────┤
  │     │                                           │ anchor "*" all {} 출력과 DIOCGETRULES EINVAL을 보면, 빠진 부분은 com.apple/* 하위     │             │
  │ 5   │ snapshot assessment의 "재귀 filter" 행    │ child일 가능성이 큽니다. "하위 전체 미확인"보다 범위를 좁힐 수 있습니다. PF 경로를    │ 추론        │
  │     │                                           │ 계속 갈 때만 의미가 있습니다.                                                         │             │
  ├─────┼───────────────────────────────────────────┼───────────────────────────────────────────────────────────────────────────────────────┼─────────────┤
  │     │                                           │ com.apple.internet-sharing/shared_v4에 pass on en0 … keep state가 있습니다. Internet  │             │
  │ 6   │ 같은 문서의 VM 관련 서술                  │ Sharing이나 vmnet shared NAT 계열이 host PF를 쓰고 있다는 정황입니다. "VM은 host PF와 │ 추론        │
  │     │                                           │  무관"이라는 가정이 틀렸다는 직접 정황이니 비교에 반영해야 합니다. 어떤 서비스인지는  │             │
  │     │                                           │ 특정하지 않습니다.                                                                    │             │
  └─────┴───────────────────────────────────────────┴───────────────────────────────────────────────────────────────────────────────────────┴─────────────┘

  s3-address-static-proposal-01.md가 localhost/tcp4 치환을 동등하지 않다고 본 판정은 맞습니다. 아래 A-3에서 더 다룹니다.

  ---

  2. A: 문제 설정과 최소성

  A-1. 필수 보장과 구현 선택 구분

  ┌────────────────────────────────────────────────────────────┬──────────────────────────────────────────────────────────────────────────────────────────┐
  │           필수 보장 (Work line 151, 사용자 요구)           │                              현재 구현 선택 (바꿀 수 있음)                               │
  ├────────────────────────────────────────────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────┤
  │ runtime이 통신할 수 있는 상대는 proxy 하나                 │ 전송이 IPv4 TCP 127.0.0.1:38971이라는 점                                                 │
  ├────────────────────────────────────────────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────┤
  │ proxy가 나갈 수 있는 곳은 frozen public A/AAAA × TCP443뿐  │ proxy가 직접 DNS를 해석하고 dial하는 점 (proxy-template-proposed.sb.in에 mDNSResponder   │
  │                                                            │ 허용)                                                                                    │
  ├────────────────────────────────────────────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────┤
  │ 위 두 제한을 restricted process의 코드가 아니라 OS가 강제  │ 강제 수단이 IP 대상 필터(Seatbelt IP literal, PF)라는 점                                 │
  ├────────────────────────────────────────────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────┤
  │ native 인증과 end-to-end TLS 유지, credential 복사·복호화  │ —                                                                                        │
  │ 없음                                                       │                                                                                          │
  ├────────────────────────────────────────────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────┤
  │ 기존 앱·VPN·PF 보존                                        │ —                                                                                        │
  └────────────────────────────────────────────────────────────┴──────────────────────────────────────────────────────────────────────────────────────────┘

  이렇게 나누면 127.0.0.1:38971 자체는 보장 대상이 아닙니다. 보장 대상은 "runtime의 유일한 상대가 proxy"라는 사실입니다. 정확한 UDS path는 이 보장을 OS가
  정확히 표현할 수 있는 수단입니다. 다만 Work에 고정된 전송 형태가 바뀌므로 Owner 결정이 필요합니다.

  A-2. 두 broker, 새 UID, PF, 전역 필터가 모두 필요한가

  필요 없다고 봅니다(정적 추론). broker가 필요했던 이유는 IP 목적지를 OS 필터로 묶을 대상 process를 만들기 위해서였습니다. FD 방식에서는 목적지가 정해지는
  시점이 connect를 하는 순간이고, 그 connect는 controller가 합니다. 제한받는 proxy는 connect를 아예 할 수 없습니다. 묶을 대상이 사라지므로 UID, PF, broker도
  필요 없어집니다.

  A-3. Seatbelt 표현을 놓쳤나

  - [관측] (remote tcp "127.0.0.1:38971")는 이 OS에서 컴파일이 거부됩니다(s3-runtime-os-01/compile.stderr). 같은 이유로 proxy template의 (local tcp
    "127.0.0.1:38971") bind/inbound와 materialize-roles.py:119-123이 만드는 IP literal도 같은 오류를 낼 가능성이 높습니다(정적 위험이고 기존 문서도 지적함).
  - [추론] remote tcp4 "localhost:38971"은 port와 protocol은 정확합니다. 하지만 host 범위가 문제입니다. 외부 보고에 따르면 localhost에는 host의 비-loopback
    주소도 들어갑니다(미재현). 같은 UID 501의 다른 process는 그 주소들의 38971에 bind할 수 있고, interface 주소는 수시로 바뀝니다. controller가 port를
    선점해도 이 틈을 닫을 수 없습니다. 따라서 동등하지 않다는 판정을 유지합니다. "다른 user process는 공모하지 않는다"는 위협 가정을 Owner가 받아들일 때만 쓸
    수 있는 하위 선택지입니다.
  - [추론] 반면 (allow network-outbound (remote unix-socket (path-literal P)))는 정확한 단일 endpoint를 OS가 강제하는 표현입니다. 앞 문서들도 같은 전제를
    썼습니다. P의 부모 디렉터리는 controller 소유로 두고 runtime과 proxy가 쓸 수 없게 하면, 경로를 가로채는 공격도 막힙니다.

  A-4. 미리 연결한 FD 전달 + 신규 연결 금지 (질문하신 대안)

  이 질문은 두 가지로 나눠 봐야 합니다.

  ┌─────────────────────┬──────────────────────────────────────────────────────────────────────────────────────────────────────┬──────────────────────────┐
  │        질문         │                                                 근거                                                 │           상태           │
  ├─────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────────────────┼──────────────────────────┤
  │ 받은 연결된 FD의    │ [source] sendit()은 to != NULL일 때만 mac_socket_check_send를 부릅니다. soo_read/soo_write에는 MAC   │ 공개 main source로 확인. │
  │ I/O가 sandbox       │ 검사가 없습니다. recvit/recvmsg_x는 !SS_ISCONNECTED && !PR_CONNREQUIRED일 때만 검사합니다. 따라서    │  설치된 26A434에서는     │
  │ 아래에서 되는가     │ 연결된 TCP의 read/write/send/recv와, 연결된 socketpair로 받는 SCM_RIGHTS에는 hook이 없습니다.        │ 실행 확인 필요           │
  ├─────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────────────────┼──────────────────────────┤
  │ 동시에 신규 연결은  │ [source] connectit/connectitx는 mac_socket_check_connect를 무조건 부릅니다. socket_common은          │ hook은 있음. Seatbelt가  │
  │ 거부되는가          │ mac_socket_check_create를 부릅니다. 받은 TCP FD에 주소를 지정한 sendto도 to != NULL이라 검사         │ 실제로 거부하는지는 실행 │
  │                     │ 대상입니다(연결된 TCP라 EISCONN도 납니다).                                                           │  확인 필요               │
  ├─────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────────────────┼──────────────────────────┤
  │                     │ soioctl의 mac_socket_check_ioctl. setsockopt/getsockopt 계열도 검사가 있을 수 있습니다. tokio나      │                          │
  │ 남는 hook           │ Rama가 쓰는 호출이 막히는지 확인해야 합니다. 상속받은 listener의 accept는                            │ 실행 확인 필요           │
  │                     │ mac_socket_check_accept/accepted를 거칩니다.                                                         │                          │
  └─────────────────────┴──────────────────────────────────────────────────────────────────────────────────────────────────────┴──────────────────────────┘

  결과적으로 proxy는 OS 수준에서 새 IP 연결을 만들 능력이 없습니다. 쓸 수 있는 것은 발급받은 FD뿐입니다.

  Rama의 CONNECT 경로는 바꿀 곳이 하나로 모입니다. network-proxy/src/http_proxy.rs:511의 TargetCheckedTcpConnector::new(app_state)를 prepared 경로에서만 "FD를
  받아 오는 connector"로 바꾸면 됩니다. CONNECT 정책, 즉 authority가 chatgpt.com:443이어야 한다는 검사는 그대로 남습니다. 확인 시점의 이 파일 digest는
  de8ac4fa…0101입니다.

  A-5. trusted controller로 옮기는 책임과 남는 권한

  이 안을 독립 OS 제한과 동등하다고 무조건 주장하지는 않겠습니다. 정확히 무엇이 바뀌는지는 이렇습니다.

  - 기존 방식: controller가 IP 목록을 정하고, kernel이 proxy의 connect를 그 목록과 대조합니다.
  - C-FD: kernel은 proxy의 connect 자체를 막습니다. 목록에 있는 IP로의 connect는 controller가 직접 합니다.

  ┌───────────────────────┬───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
  │         항목          │                                                             내용                                                              │
  ├───────────────────────┼───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
  │ 이미 있던 신뢰        │ controller가 IP snapshot을 정하고 profile을 만들며 budget을 관리하고 sandbox 밖에서 실행됩니다. 지금도 이렇습니다.            │
  ├───────────────────────┼───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
  │ 새로 생기는 신뢰      │ controller의 connect 함수(주소 입력 없이 예약 index만 받음, connect 후 peer 대조), FD 발급 횟수 계상, 보관한 dup에 대한       │
  │                       │ shutdown() 회수                                                                                                               │
  ├───────────────────────┼───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
  │ controller가 하지     │ byte 중계, CONNECT 해석, TLS 처리. N-01 broker와 달리 신뢰하지 않는 data stream을 만지지 않습니다. 그래서 "중계 코드 침해 →   │
  │ 않는 일               │ 임의 443 접속" 경로가 없습니다.                                                                                               │
  ├───────────────────────┼───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
  │ proxy가 침해되면 남는 │ 발급받은 FD를 쓸 수 있고(같은 CDN IP의 다른 vhost 문제는 PF 방식과 같음), 예약 상한까지 FD를 더 요청할 수 있습니다. 새 IP     │
  │  권한                 │ 연결, UDP, DNS는 할 수 없습니다(실행 확인 대상).                                                                              │
  ├───────────────────────┼───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
  │ controller가 침해되면 │ 무엇이든 할 수 있습니다. 지금 구조와 같고, N-01의 PF도 이 경우를 막지 못합니다. PF 규칙도 controller가 설치하기 때문입니다.   │
  └───────────────────────┴───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

  ---

  3. B: PF hook의 추가와 회수

  B-0. source에서 확인한 사실 (Apple XNU main, 설치된 build와 같은지는 미확인)

  - DIOCINSERTRULE (Apple 고유)
    - ticket 없이 active list에 바로 씁니다.
    - rule.owner를 기록합니다.
    - 위치는 priority 값 순서로 정해집니다.
    - 같은 anchor-call이 이미 있으면 owner에 따라 EEXIST 또는 EPERM을 냅니다.
  - DIOCDELETERULE
    - ticket이 있으면 ticket으로 지웁니다. owner가 다르면 EACCES입니다.
    - ticket이 0이면 owner 기준으로 지웁니다. 빈 owner의 동작은 확인하지 못했습니다.
  - DIOCCHANGERULE
    - GET_TICKET 후 ticket이 일치해야 동작합니다(불일치 시 EINVAL). 그래서 동시 writer를 감지할 수 있습니다.
    - owner가 없고 대상은 nr 번호로 지정합니다.
  - process 종료 시 규칙을 정리하는 경로는 찾지 못했습니다. 보이는 범위에서 그렇습니다.
  - pf_commit_rules는 active list 전체를 inactive로 바꾸고 기존 규칙을 제거합니다. INSERTRULE이나 CHANGERULE로 넣은 root 규칙도 다음 root commit 때
    사라집니다. 다만 transaction 진입부는 읽은 범위에서 잘려 있었습니다.

  B-1. 경로별 판단

  경로: 공식 CLI
  다른 동적 anchor를 다시 적재하지 않고 task hook만 추가·회수 가능?: root에 규칙 하나만 넣는 CLI는 없습니다. pfctl -f로 root를 바꾸면 transaction commit이라
  동적 hook이 지워집니다. 현재 hook으로 닿는 CLI는 pfctl -a com.apple/<child> -f뿐인데, Apple namespace를 점유하므로 Owner 조건상 제외됩니다.
  판단: 불가 (조건상)
  ────────────────────────────────────────
  경로: private ioctl (INSERT/DELETE)
  다른 동적 anchor를 다시 적재하지 않고 task hook만 추가·회수 가능?: 추가·회수의 정밀도는 좋습니다(owner, ticket). crash 후에도 남으므로 차단 규칙이 남는다는
  점에서는 유리합니다. 하지만 다른 writer가 root를 commit하면 사라지고 결과는 fail-open입니다. 순서도 문제입니다. 기존 규칙의 priority 값이 pfctl -sr에
  보이지 않아서 com.apple/* 앞인지 뒤인지 미확정입니다. pfvar.h가 SDK에 없어 ABI 일치도 미검증입니다. 규칙을 지워도 state는 남습니다. 지우지 않으면 회수가 안
   되고, 주소 기준 kill은 다른 앱까지 건드립니다.
  판단: 메커니즘은 있으나 이 host 근거 없음. 요구 조건에서 fail-open 위험이 구조적
  ────────────────────────────────────────
  경로: 시스템 서비스 경로 (pfd 등)
  다른 동적 anchor를 다시 적재하지 않고 task hook만 추가·회수 가능?: 공개 interface를 찾지 못했습니다. root 동적 hook을 실제로 누가 쓰는지 특정하지
  못했습니다.
  판단: 확인 불가

  "private이라서 불가능"도, "source에 있으니 안전"도 아닙니다. 메커니즘은 존재합니다. 하지만 이 host에는 root를 런타임에 바꾸는 writer가 관측됩니다. 그래서
  N-01 스스로 정한 fail-closed 조건과 맞지 않습니다. ABI가 확인되더라도 C-FD보다 뒤로 둬야 한다고 봅니다.

  ---

  4. C: 대안 비교

  ┌─────────────────┬──────────────────────────────────┬────────────────────────────────┬─────────────────────────────────────┬──────────────────────────┐
  │      기준       │           C-FD (제안)            │       NE content filter        │          VM 또는 전용 host          │      N-01 PF (참고)      │
  ├─────────────────┼──────────────────────────────────┼────────────────────────────────┼─────────────────────────────────────┼──────────────────────────┤
  │                 │                                  │ 모든 앱의 flow가 filter를      │ host 영향은 작지만 NAT가 host       │ root hook·state·enable   │
  │ 기존 앱 영향    │ 없음. 전역 설정 0                │ 거침. 허용하는 경우에도 앱     │ PF/Internet Sharing을 쓸 수         │ reference가 얽힘         │
  │                 │                                  │ 오류 보고가 있음               │ 있음(정황)                          │                          │
  ├─────────────────┼──────────────────────────────────┼────────────────────────────────┼─────────────────────────────────────┼──────────────────────────┤
  │ endpoint/IP     │ Seatbelt가 proxy의 connect와     │ NE provider 코드 (공식 OS      │ guest 방화벽 또는 host 필터. 결국   │                          │
  │ 강제 주체       │ socket 생성을 막음. IP 선택은    │ 경계지만 판정은 provider가 함) │ PF나 NE가 다시 필요                 │ PF + UID                 │
  │                 │ controller                       │                                │                                     │                          │
  ├─────────────────┼──────────────────────────────────┼────────────────────────────────┼─────────────────────────────────────┼──────────────────────────┤
  │                 │ 유지. TLS는 runtime에서 원       │                                │ Keychain 등 native 인증 환경이 VM에 │                          │
  │ native 인증/TLS │ 서버까지                         │ 유지                           │  없음. 복사(금지)나 새 로그인(시험  │ 유지                     │
  │                 │                                  │                                │ 대상 변경)이 필요                   │                          │
  ├─────────────────┼──────────────────────────────────┼────────────────────────────────┼─────────────────────────────────────┼──────────────────────────┤
  │                 │ runtime은 UDS만 쓰므로 loopback  │ 규칙이 nil이면 loopback 제외.  │                                     │ lo0 skip이 없음은 확인.  │
  │ loopback        │ 문제 자체가 없음                 │ 명시 규칙이 필요하고 버전별    │ 해당                                │ 실제 경로는 미검증       │
  │                 │                                  │ 동작 변화 보고 있음            │                                     │                          │
  ├─────────────────┼──────────────────────────────────┼────────────────────────────────┼─────────────────────────────────────┼──────────────────────────┤
  │ IPv4/IPv6/UDP   │ 새 socket 생성·연결 모두         │                                │                                     │ TCP/UDP만. 나머지는      │
  │ 등              │ 거부(검증 대상). AAAA는          │ 표현 가능                      │ 해당                                │ Seatbelt에 맡김          │
  │                 │ controller가 연결                │                                │                                     │                          │
  ├─────────────────┼──────────────────────────────────┼────────────────────────────────┼─────────────────────────────────────┼──────────────────────────┤
  │ 장애 시 차단    │ controller가 죽으면 FD 발급이    │ 확인하지 못함 (extension 중단  │                                     │ 다른 writer의 commit으로 │
  │ 유지            │ 멈춤 = 차단. profile은 process   │ 시 동작이 문서로 확인되지      │ guest 구성에 따라 다름              │  fail-open               │
  │                 │ 수명 동안 바뀌지 않음            │ 않음)                          │                                     │                          │
  ├─────────────────┼──────────────────────────────────┼────────────────────────────────┼─────────────────────────────────────┼──────────────────────────┤
  │                 │                                  │ Developer ID 서명, system      │                                     │                          │
  │ 설치·회수 권한  │ 없음 (user 권한)                 │ extension entitlement, 사용자  │ VM 구성                             │ root, 계정 생성, PF      │
  │                 │                                  │ 승인 UI                        │                                     │                          │
  ├─────────────────┼──────────────────────────────────┼────────────────────────────────┼─────────────────────────────────────┼──────────────────────────┤
  │                 │ §5의 offline canary 1회 + 통합   │ loopback 포착, 프로세스        │                                     │ N0/N1 전체 + priority    │
  │ 필수 검증       │ 검사                             │ 식별(audit token), fail 동작,  │ 환경·인증·시험 대상 동등성          │ 순서 + ABI               │
  │                 │                                  │ 기존 filter와의 공존           │                                     │                          │
  ├─────────────────┼──────────────────────────────────┼────────────────────────────────┼─────────────────────────────────────┼──────────────────────────┤
  │                 │ 작음. prepared 경로의 connector  │ 큼 (기존 추정 2–5일, 외부 대기 │                                     │ 가장 큼 (N 480–780분 +   │
  │ 구현·운영 부담  │ seam 1곳 + controller FD 발급 +  │  별도)                         │ 큼                                  │ 관리 작업)               │
  │                 │ runtime UDS                      │                                │                                     │                          │
  └─────────────────┴──────────────────────────────────┴────────────────────────────────┴─────────────────────────────────────┴──────────────────────────┘

  ingress(runtime → proxy) 구간에는 Owner가 고를 하위 선택이 하나 있습니다. 둘 다 근거가 부족한 부분이 있습니다.
  - I-1a: runtime의 prepared connector가 UDS P에 연결해 고정 CONNECT를 보내고 TLS를 시작합니다. proxy의 CONNECT 경로가 그대로 실행되어 시험 대상과의 동등성이
    높습니다. 대신 runtime 코드가 늘어납니다.
  - I-1b: reqwest 0.12.28의 unix_socket 기본 동작(proxy를 무시하고 UDS 위에서 바로 TLS)을 쓰고, proxy의 UDS listener는 고정 tunnel로 동작합니다. 코드는 작지만
    proxy가 CONNECT를 해석하는 단계가 빠집니다. Work line 139의 "network-proxy 제품 의미"에 걸리는지 판단이 필요합니다.
  - Rama가 상속받은 UDS listener에서 accept할 수 있는지는 확인하지 못했습니다.

  ---

  5. 가장 작은 다음 검증 (제안만 하며, 실행·승인하지 않았습니다)

  offline Seatbelt FD canary 1회입니다. 실제 credential, provider, 외부 트래픽, 관리자 권한을 쓰지 않고, 기존 s3-runtime-os-probe.c 방식의 합성 probe로
  합니다.

  1. 컴파일만 확인
     - proxy용 profile: IP network-outbound/bind 없음, mDNSResponder 없음, (local unix-socket (path-literal P)) inbound
     - runtime용 profile: (remote unix-socket (path-literal P))만
  2. 부모 process가 loopback 합성 echo fixture에 TCP 연결을 만들고, 상속 socketpair로 SCM_RIGHTS를 통해 sandbox 안 child에게 넘깁니다.
  3. child가 확인할 것:
     - (a) 받은 FD로 read/write/send/recv, 그리고 tokio가 쓰는 fcntl/setsockopt/getpeername
     - (b) 같은 fixture로 새로 connect
     - (c) socket(AF_INET/AF_INET6, SOCK_DGRAM)과 sendto
     - (d) 받은 FD에 다른 주소로 sendto
     - (e) mDNSResponder UDS 연결과 다른 UDS 경로 연결
     - (f) 상속받은 UDS listener의 accept
     - (g) 부모가 보관한 dup에 shutdown()을 걸어 child 쪽이 EOF를 받는지
  4. 판정 기준
     - 허용: (a)(f)(g)가 성공해야 합니다.
     - 거부: (b)–(e)는 sandbox 거부여야 합니다. EPERM과 sandbox violation log를 함께 확인합니다. ECONNREFUSED나 timeout은 통과로 세지 않습니다.
     - 첫 번째 non-pass에서 멈추고 재시도하지 않습니다.

  결론이 바뀌는 조건은 이렇습니다.
  - (a)가 통과하고 (b)–(e)가 모두 거부되면, C-FD가 성립합니다. PF, UID, NE, VM은 이 작업에 필요 없습니다.
  - (a)가 막히면 C-FD는 폐기합니다. 이후 남는 것은 NE(loopback과 장애 시 동작을 먼저 검증)와 PF INSERTRULE(ABI와 commit 시 fail-open 문제를 먼저 해결)입니다.
    둘 다 무겁기 때문에 No-Go 유지가 기본값입니다.
  - (b)–(e) 중 하나라도 허용되면, 해당 표현 없이는 C-FD가 성립하지 않습니다.

  시간은 근거가 약한 판단값으로 활동 30–60분 정도입니다. 기존 mapping 잔여 2.722225분 안에는 들어가지 않습니다. 별도 할당이 필요하며, Owner 판단 사항입니다.
  저는 ledger와 상한을 바꾸지 않았습니다.

  6. 남은 불확실성

  - 공개 XNU main과 설치된 26A434가 같다는 보장이 없습니다. Sandbox.kext가 MACF 바깥의 다른 경로로 FD 사용을 막을 가능성은 source로 배제할 수 없습니다. 그래서
    canary가 필요합니다.
  - C-FD의 강제 형태는 "kernel이 proxy의 connect를 목록과 대조"에서 "kernel이 connect를 금지하고 controller가 대신 연결"로 바뀝니다. 이것을 요구 조건 충족으로
    받아들일지는 Owner가 결정할 일입니다. Reviewer가 판정할 사항이 아닙니다.
  - Work line 139의 고정 범위에 대해서는 C-FD도 범위 변경 승인이 필요합니다. 대상은 network-proxy prepared connector, controller FD 발급, runtime UDS입니다.
    N-01보다 작지만 0은 아닙니다.
  - NE의 장애 시 동작은 Apple 문서에서 확인하지 못했습니다. loopback 동작은 forum 보고 수준의 근거만 있습니다.
  - PF의 root 동적 hook을 실제로 쓰는 writer는 특정하지 못했습니다(pfd인지 InternetSharing인지 미상).

  7. 입력 기록과 범위 준수

  - 확인 시점은 2026-10-22 16:50:13–16:56:33 KST입니다. 끝날 때 digest를 다시 확인했고 바뀐 것은 없었습니다.
  - 읽은 자료와 digest (SHA-256 앞 8자리):

  ┌──────────────────────────────────────────────────┬──────────────────────────────────────────────────────┐
  │                       자료                       │                        digest                        │
  ├──────────────────────────────────────────────────┼──────────────────────────────────────────────────────┤
  │ s3-n01-n0-pf-snapshot-assessment-01.md           │ 4830b4aa                                             │
  ├──────────────────────────────────────────────────┼──────────────────────────────────────────────────────┤
  │ pf-readonly-01/ 16개 파일                        │ assessment 문서의 표와 일치. summary.json은 b29edef3 │
  ├──────────────────────────────────────────────────┼──────────────────────────────────────────────────────┤
  │ s3-network-boundary-revised-execution-plan-01.md │ cdee0f0e                                             │
  ├──────────────────────────────────────────────────┼──────────────────────────────────────────────────────┤
  │ s3-n01-n0-readonly-eligibility-01.md             │ 61f4049b                                             │
  ├──────────────────────────────────────────────────┼──────────────────────────────────────────────────────┤
  │ s3-endpoint-alternatives-01.md                   │ 5ba6ae41                                             │
  ├──────────────────────────────────────────────────┼──────────────────────────────────────────────────────┤
  │ s3-address-static-proposal-01.md                 │ f7020ec8                                             │
  ├──────────────────────────────────────────────────┼──────────────────────────────────────────────────────┤
  │ s3-runtime-os-01/runtime.sb                      │ 6ad608f7                                             │
  ├──────────────────────────────────────────────────┼──────────────────────────────────────────────────────┤
  │ proxy-template-proposed.sb.in                    │ f17c458f                                             │
  ├──────────────────────────────────────────────────┼──────────────────────────────────────────────────────┤
  │ materialize-roles.py                             │ 40efdc57 (100–135행만)                               │
  ├──────────────────────────────────────────────────┼──────────────────────────────────────────────────────┤
  │ network-proxy/src/http_proxy.rs                  │ de8ac4fa (505–545행만)                               │
  ├──────────────────────────────────────────────────┼──────────────────────────────────────────────────────┤
  │ Work 파일                                        │ dd08fb01 (136–153행과 grep 결과만. 전체를 읽지 않음) │
  └──────────────────────────────────────────────────┴──────────────────────────────────────────────────────┘

  - 의도적으로 읽지 않은 자료: s3-n01-pf-hook-and-isolation-static-review-01.md (16:49:16 생성, e1390692). 메인 채팅이 작성 중인 최신 결과라서, 독립성을 위해
    입력에서 뺐습니다.
  - 외부 근거: Apple XNU 공개 source uipc_syscalls.c, sys_socket.c, pf_ioctl.c. 두 파일은 일부가 잘려서 끝까지 읽지 못했습니다. NE loopback 관련은 Apple
    Developer Forums의 668813, 762619, 803694, 837709입니다.
  - 범위 준수: 파일·OS·PF·권한 변경, sudo, probe/build/test, Git 변경을 하지 않았습니다. 이 답변 외에 산출 파일을 만들지 않았습니다. ledger 292.908117분,
    mapping 잔여 2.722225분, build 2/3, correction 1/2, H05/H10 미적격, Owner 판단은 그대로입니다.
  - 정산용 기록: 이 리뷰의 활동은 16:50:13 KST에 시작했고, 16:56:33 이후 이 답변을 작성한 시간이 더 있습니다.
  - 이 판단은 구현 승인이나 Owner 수락을 대신하지 않습니다.

  다음 단계로는 §5 canary의 실행 여부와 시간 할당, 그리고 C-FD의 강제 형태 변경(A-5)을 받아들일지를 Owner가 함께 정하시면 됩니다.
~~~~


### C-FD Minimum Preflight Proposal — 2026-10-22T08:20:27.234611+00:00

Owner의 계획 전용 요청에 따라 `private-evidence/E116`를 준비했다(SHA-256 `36bd1d10b51ae6db72a8eaed6702154fe72d53a373325a2db0a4cdc4b5350d16`). deny-default 두 역할에서 exact UDS·connected FD 전달/입출력·신규 IP/DNS 통로 거부·목적지 불변·명시적 shutdown을 정상 대조군과 함께 확인하는 M0–M6만 제안한다. controller crash 자동 회수·실제 CONNECT/TLS/native auth·예약/총량/journal·H05/H10은 별도 적격이다. 첫 non-pass 중단, compile1/probe1묶음/보정·재실행0, 예상45–75분과 누적 중단90분(마지막10분 종료) 모두 미승인 제안이다. [공개용 중립화]

확정 ledger292.908117분·S3 13.076282분·mapping 잔여2.722225분·build2/3·correction1/2·pause4 유지. snapshot 잔여를 현재 가용 시간으로 제시하지 않는다. 이전 미정산 분석/검토/보고와 이번08:12:48.494843Z 이후 활동(작성 시점까지458.741초 및 이후 검증·보고)을 기존 전체/S3에 한 번 이월하고, 중첩은 한 번만 계상한다. mapping 준비가 시작된 것은 아니며 이 계획 작성으로 기존 mapping 잔여를 재설정하지 않는다. 실행 전 실제 pending 정산과 필요한 mapping/S3 시간 증분 승인 없이는 진행하지 않는다.

이번 변경은 계획 문서1개와 기존 Work의 이 checkpoint뿐이다. 보호 입력/장부10개와 PF snapshot16개는 기록 전후 불변으로 확인했다. 구현·compile·probe·OS·상한·ledger/journal·Git·STATUS 변경0. 새 실행 디렉터리는 만들지 않았다. 계획·기존 근거는 Owner 처분/후속 검증 소비까지 보존, active 경로 이동·삭제0이다.


### C-FD Time Reconciliation And Unapplied Cap Calculation — 2026-10-22T08:32:38.022805+00:00

Owner의 미정산 시간 정산·증분 계산 요청에 따른 기록이다. 구현·검증 실행·OS 변경·상한 적용은 승인되지 않았다. 기존 execution.json의 전체/S3 사용량에 확인된 미정산 구간의 합집합만 가산했다. 과거 사용량은 그대로 이월했으며 state는 S3-stopped-profile-compile, runtime journal pause4, mapping·counts·H05/H10·모든 상한과 기존 deadline은 불변이다. pause 상태의 실제 정적 활동을 Owner 대기로 면제하지 않는다.

| 구간 | 추가 활동 초 | 처리 |
| --- | ---: | --- |
| 기존 확인 subtotal,07:41:27.458857Z까지 | 2853.429234 | 이전 partial들을 대체한2853.429234초를 한 번 반영 |
| Post-stop evidence and report: 06:41:06.419000–06:43:12.782207 UTC | 126.363207 | 실제 구간; 아래 중복 차감 |
| PF hook static review: 07:42:31.205849–07:51:17.624186 UTC | 526.418337 | 실제 구간; 아래 중복 차감 |
| Claude review confirmed interval: 07:50:13.000000–07:56:33.000000 UTC | 380 | 실제 구간; 아래 중복 차감 |
| Driver C-FD review disposition: 07:59:30.170900–08:08:25.633776 UTC | 535.462876 | 실제 구간; 아래 중복 차감 |
| Driver reference-source check: 08:08:49.438987–08:10:12.513142 UTC | 83.074155 | 실제 구간; 아래 중복 차감 |
| Driver reference-review disposition: 08:11:09.677253–08:12:18.028012 UTC | 68.350759 | 실제 구간; 아래 중복 차감 |
| C-FD minimum preflight planning: 08:12:48.494843–08:23:00.136273 UTC | 611.64143 | 실제 구간; 아래 중복 차감 |
| Current accounting: 08:24:18.733711–08:32:38.022805 UTC | 499.289094 | 실제 구간; 아래 중복 차감 |
| Driver/Claude 중복 제거 | -64.624186 |07:50:13–07:51:17.624186 한 번만 계상 |
| 이번 확정 가산 | 5619.404906 | 93.656748분 |

첫 중단 장부06:41:06.419Z부터 최초 중단 보고06:43:12.782207Z까지126.363207초는 이전 subtotal에 없어 이번에 추가했다. 이 항목과 이미 포함된 후속 준비 구간을 중복하지 않는다.

| 항목 | 이전 확정 분 | 이번 정산 후 확인 사용 분 | 현행 상한 분 | 확인 잔여 분 |
| --- | ---: | ---: | ---: | ---: |
| 전체 |292.908117 |386.564865 |960 |573.435135 |
| S3 |13.076282 |106.733030 |150 |43.266970 |
| mapping |27.277775 |27.277775 |30 |2.722225 |

정산 기준은 위 cutoff UTC까지다. 이번 기록 뒤 검증/보고 시간은 다음 정산에 한 번 추가한다. 미상 리뷰 시간은 사용량0으로 확정하지 않았다. 따라서 전체/S3 사용은 확인된 하한, 잔여는 상한이다.

Owner가 Claude에 재확인한 결과 첫 date는 실제 시작이 아니고 마지막 date는 답변 종료가 아니다. 알려진380초 외의 작성/두 번째 리뷰 시간을 정확히 나눌 수 없다. 다만 두 답변을 실제로 받은07:59:30.170900Z/08:11:09.677253Z를 각각 종료의 상한으로 쓰고, 이미 계상한 Driver 구간을 빼면 첫 date 이후 추가 가능한 미확정분은0–258.140222초(0–4.302337분)다. 이는 활동 실측이 아니라 최대 예약 범위이며 Owner 대기를 실제 활동으로 일괄 계상하지 않는다. 제시받은16:56:33–17:27:02 KST의1829초를 통째로 더하지 않는다.

첫 date07:50:13보다 앞선 미상 활동은07:42:31.205849 이후라면 기존 Driver와 전부 겹친다. 그보다 이른 활동 중 기존 합집합 밖의 부분은 U_pre로 남기며 시작 기록 없이0 또는 임의 상한을 확정하지 않는다. 위0–4.302337분 범위를 이 U_pre까지 포함한 절대 전체 상한으로 부르지 않는다.

90분 확보 계산은 다음과 같다. 단위는 분이며 미적용 제안이다.

| 한도 | 배정 전제 | 필요한 최소 증분 | 필요한 새 누적 상한 |
| --- | --- | ---: | ---: |
| mapping, 최소 배정안 | 준비를 최대35분으로 고정;90분 전체와 별도인 하위 제약 | +32.277775 | 62.277775 |
| mapping, 전체90분도 배정하는 경우 | 전체90분을 mapping에도 쓸 수 있게 보수 예약 | +87.277775 | 117.277775 |
| S3, 확인 시간만 | 기존 사용량+사전검증90분 | +46.733030 | 196.733030 |
| S3, 첫 date 이후 미상 최대도 예약 | 위 조건+미확정 최대4.302337분을 사용량과 구분해 예약 | +51.035367 | 201.035367 |

S3의 마지막 두 행에는 U_pre와 cutoff 뒤 실제 활동이 추가되면 각각 같은 분만큼 더 필요하다. 지금 확정할 수 없는 시간을 숨겨 정확한 최종 승인액이라고 부르지 않는다. mapping 최소안은 계획의 준비 예상 상단35분을 실제 중단 subcap으로 채택하는 조건부 제안이며,35분을 넘기면 전체90분이 남아도 중단한다. 이 조건을 채택하지 않고90분 전체를 두 한도 모두에서 확보하려면 mapping 증분87.277775분을 써야 한다. 실제 전체/S3 활동을 mapping과 중복해서 두 번 합산하지 않는다.

전체960분 상한은 확인된 사용량+90분+첫 date 이후 미상 최대+기존 종료 예비20분을 수용한다. U_pre와 이후 활동이 현재 여유를 초과하지 않는 한 이번90분 때문에 전체 상한을 늘릴 필요는 없다. build2/3·correction1/2·H05/H10 미적격/Owner 판단 유지. 새로운 상한·예산·실행 승인0.

변경은 execution.json의 시간 정산 필드와 회복 가능한 정산 entry, 이 Work의 checkpoint뿐이다. 정산 entry에 이전 변경 필드·이전 SHA·정확한 JSON 형식을 보존했고 역변환으로 이전 execution.json 전체 bytes를 복원할 수 있음을 쓰기 전에 검증했다. 별도 backup/registry/전체 source 복사를 만들지 않았다. 기존 probe 계획·source/profile·budget anchor/journal·candidate는 불변이며 현재 계획 문서는 당시 snapshot이라는 역사적 의미를 유지한다. 새 실행 디렉터리 생성0, active path 이동·삭제0이다.


### Owner-Requested Session Pause — 2026-10-22T08:45:53.339527+00:00

Owner는2026-10-22T08:42:33.786824Z에 금일 종료/노트북 덮기와 늦은 밤 또는 다음 날 재개를 요청했고,08:43:21.576433Z에 “내가 재개하자고 하면 다시 작업 제안해줘”라고 명시했다. 자동 재개·예약 실행·알림은 만들지 않는다. Work Done 또는 결과 수락이 아니라 Owner 요청에 따른 세션 중단이다.

완료한 범위는 S2 구현/집중검사와 candidate build, S3 profile compile 실패 보존, PF/대안 정적 검토, C-FD 최소 사전 검증안 및 확인된 시간 정산이다. 실제 C-FD 구현/compile/probe, native auth/provider/actual target, H05/H10은 진행하지 않았다. 별도 실행 승인과 상한 적용은 없다.

중단 전 읽기 전용 확인: task 경로 및 고정 helper 이름의 process 목록에는 확인 명령 자신 외의 실행 process가 없었고, 활성 하위 agent도 없었다. 두 feature worktree의 상태를 확인했고, Codex HEAD·tracked diff·untracked source3개·host.py가 candidate binding과 일치했다. durable candidate binary3개는 기록된 SHA-256과 일치하며, host helper/tests6개와 실패/성공 result·profile stop evidence·journal·장부·계획을 읽을 수 있다. 두 checkout git diff --check 통과. 이 확인은 제품/OS 적격 test 재실행이 아니다.

보존: `private-evidence/E159`와 `private-evidence/E162`의 미커밋 변경, `private-evidence/E003`의 원본/복구·candidate binary·실패/성공 근거·PF snapshot·C-FD 계획·시간 장부. 소비자는 바로 다음 U2 재개/범위 처분/검증이며, 폐기 또는 후속 결과 수락과 근거 소비 종료 때 필요성을 재평가한다. 근시일 내 동일 checkout을 재사용하므로 archive/remove하지 않는다. 기존 clock-01 빈 slot도 앞선 고정 probe topology의 처분 전까지 유지한다. 활성 경로 이동0, 파일/작업트리 삭제0, 새 backup/복제0이다. 복사만 수행한 cleanup이라고 보고하지 않는다. [공개용 중립화]

시간: 직전 정산 cutoff08:32:38.022805Z 뒤 보고 종료08:35:05.309446Z까지147.286641초와, 이번 종료 준비08:42:33.786824Z부터 이 checkpoint까지199.552703초(합계346.839344초), 이후 최종 보고까지를 다음 정산에서 기존 전체/S3에 한 번 가산한다.08:35:05.309446–08:42:33.786824는 Owner-only 대기로 제외한다. 늦은 밤/다음 날까지 단순 경과한 시간을 활동 시간으로 쓰지 않는다. 기존 static_accounting_reconciliations가 이미 가산한93.656748분을 다시 더하지 않는다. 미상 Claude 시간의 범위/U_pre는 앞 정산 그대로 남긴다. 이번에는 장부·상한·pause4를 다시 수정하지 않았다.

재개 순서: (1) Owner가 재개를 요청하면 이 Work의 시간 정산과 중단 checkpoint, `s3-cfd-minimal-preflight-plan-01.md`, execution.json을 먼저 읽는다. (2) 두 checkout/입력/남은 process·현재 host 세션 상태를 다시 확인하고 위 미정산 꼬리와 실제 활동만 반영한다. 기존 wall deadline 또는 오래된 OS 관측만으로 바로 실행하지 않는다. 수면/재시작으로 바뀐 부분은 필요한 범위에서만 재확인한다. (3) C-FD 사전 검증의 범위·필수 oracle·시간 증분/매핑35분 제한안과 필요한 승인 항목을 다시 제안한다. (4) 명시 승인 전 harness/profile 작성·compile/probe·OS 변경·상한 적용을 하지 않는다. 실제 endpoint/신뢰 모델 최종 채택과 H05/H10 Owner 판단은 별도로 유지한다.

STATUS/index/backlog/DR 상태 변경은 불필요하다. 기존 Work가 계속 미완료이고 새로운 기술 선택이 채택되지 않았기 때문이다. 미결 C-FD/예산/회수 문제는 이 Work와 계획에 이미 남아 있으므로 새 OQ/DR/별도 troubleshooting registry를 만들지 않는다. 상태는 기록 확인 PASS + CHECKPOINT/Owner pause이며, 원 S3 compile failure와 미적격은 그대로다. 이번 변경은 이 중단 기록뿐이고 commit/push/PR은 하지 않았다. 미커밋 작업은 durable checkout에 보존됐지만 Git publication/결과 수락을 대신하지 않는다.

다음 시작 문장: “U2 작업 재개하자. 저장된 중단 상태와 미정산 시간을 확인하고, C-FD 사전 검증의 작업 범위와 필요한 승인을 다시 제안해줘.”


### Resume Inspection And C-FD Reproposal — 2026-10-22T14:06:34.536849+00:00

Owner의2026-10-22T14:01:50.640837Z 요청은 저장 상태·미정산 확인과 실행 전 제안이며 구현/실행 승인이 아니다. 두 feature checkout의 Codex source HEAD/tracked diff/untracked3개, host.py, candidate binary3개는 기존 binding과 일치했고 diff --check가 통과했다. task 경로/helper로 식별한 실행 프로세스는 확인 명령 자신 외에는 없었다. OS는27.0.1/build26A434이다. 재부팅 여부나 boot identity 동일성을 이 확인으로 단정하지 않으며 실제 실행 승인 후 필요한 현행 조건을 별도로 확인한다. fd01 실행 디렉터리 부재, runtime journal pause4, build2/3·correction1/2, H05/H10 미적격 유지.

문서 불일치: Work 상단 Status는 초기 S0 No-Go/구현 미착수 문구인 반면 최신 checkpoint와 execution.json은 S2 완료·S3 profile compile 중단이다. Development Index에는 이 Work ID의 직접 pointer도 없다. Toolstead STATUS는 별도 저장소의 dashboard이므로 그 Active Work 부재를 이 외부 작업의 완료/부재로 해석하지 않는다. 이번에는 상단/색인을 바로 수정하지 않았다. 제안: 기존 이력은 유지하고 Work 상단의 현재 상태를 S3-stopped-profile-compile/C-FD proposal pending으로 바꾸며 source development index에 기존 Work pointer를 추가한다. 이는 문서 현행화이며 신규 Work/실행/결과 수락이 아니다.

정산은 이전 report tail147.286641초, 종료 준비253.939223초(17:42:33.786824–17:46:47.726047 KST), 이번 재개 요청부터 cutoff까지283.896012초를 합친685.121876초(11.418698분)를 기존 전체/S3에 한 번 가산했다. 이전 checkpoint의 부분346.839344초를 별도로 또 더하지 않는다.17:46:47.726047–23:01:50.640837 KST의18902.914790초는 Owner 중단/대기라 제외한다. 앞 정산의93.656748분도 재가산하지 않는다.

| 항목 | 확인 사용 분 | 현행 상한 분 | 확인 잔여 분 |
| --- | ---: | ---: | ---: |
| 전체 | 397.983563 |960 |562.016437 |
| S3 | 118.151728 |150 |31.848272 |
| mapping |27.277775 |30 |2.722225 |

| 미적용 증분 제안 | 최소 증분 분 | 계산상 새 상한 분 |
| --- | ---: | ---: |
| mapping 준비 최대35분으로 제한 |32.277775 |62.277775 |
| mapping에도 전체90분 확보 |87.277775 |117.277775 |
| S3 확인 사용+90분 |58.151728 |208.151728 |
| S3 확인 사용+90분+후기 미상 최대4.302337분 예약 |62.454065 |212.454065 |

현재 산출값은 cutoff 기준이다. 이후 실제 활동과 기록이 발견되는 U_pre를 S3 필요액에 한 번 더한다. 미상0–4.302337분은 사용량으로 단정하지 않는 예약 범위이며, 첫 date 이전의 합집합 밖 U_pre는 별도 미상이다. U_pre를0으로 자동 수락하지 않는다. 정확한 시각을 복구할 수 없음을 Owner가 확인했으므로, 실행 전 이 계측 공백을 어떤 예산 기준으로 처리할지도 명시적인 Owner 처분에 포함한다. 전체960분은 확인 사용량+90분+후기 미상 예약+종료20분을 수용하며, U_pre/후속 활동이 남은 여유를 초과하지 않는 한 전체 상한 확대는 필요 없다.

재제안 범위는 기존 C-FD 최소안의 M0–M6 그대로다: 정상 대조군, 두 deny-default 역할, exact UDS/경로 변경 거부, sandbox 이후SCM_RIGHTS로 받은FD의 입출력, 신규TCP/UDP v4/v6와 resolver UDS 통로 거부, 받은FD 목적지 불변, controller의 명시적shutdown 및 종료 확인. compile1회/probe1묶음/첫non-pass 중단/보정·재실행0회. socket 생성과 통신의 구분, protocol 거부와 sandbox 거부의 구분, 로그/IPv6 미확보는UNAVAILABLE 원칙을 유지한다. 예상45–75분(판단값), 실행 묶음90분 상한·마지막10분 종료 예약을 제안하고 새 임의 테스트/외부 접속/OS 설정은 포함하지 않는다.

승인 대상: (1) task-only probe/runner/profile 작성과 위 고정1회 검증, (2) task 디렉터리·local TCP/UDP/UDS/FD·자기process 정리·resolver UDS connect 차단시험·권한 범위 내 PID 한정 로그, (3) mapping35분 준비한도 또는 전체90분 배정 선택 및 실제 S3 증분/미상 시간 처분. 실행을 선택한다면 상한은 채택 시점 사용량과 정확히 결속해야 하며 지금 적용하지 않는다. controller crash 자동 회수·실제Rama/Tokio/CONNECT/TLS/nativeauth/publicIP443·예약/총량/journal·실제endpoint변경·H05/H10은 포함하지 않는다. 사전 검증 PASS는 제품 구조 채택이나 원 작업 전체 재개가 아니다.

이번 변경은 execution.json의 회복 가능한 시간 정산entry와 이 Work의 checkpoint뿐이다. 이전 execution.json 전체 bytes를 역변환으로 복원할 수 있음을 확인했다. 상한·mapping·실행 상태·deadline·runtime journal·source/profile/OS·Git/STATUS/index 변경0, compile/probe/reviewer 호출0. 원 계획/미커밋 변경/근거와 두 작업트리는 후속 Owner 판단·검증 소비를 위해 보존하며 이동·삭제·중복backup0이다. 상태는 사전 확인 완료/제안이며 다음 전이는 명시적 범위·예산 승인 후에만 허용한다.


## C-FD Preflight Execution Authorization — 2026-10-22 23:23 KST

Owner가 최소 사전 검증 실행을 승인했다. 제품 source/OS 설정 변경 없이 task-only 입력과 M0–M6를 준비하고 compile1회·검사 묶음1회, 첫 non-pass 중단·보정0·재실행0을 적용한다. 기존 runtime state와 pause4, product build2/correction1, H05/H10 판단은 유지한다.

직전 보고 tail128.812266초와 이번 활동을 기존 전체/S3에 중복 없이 계상한다. S3 상한 224.600936분, 증분 74.600936분으로 확정했다. 매핑 상한 62.277775분은 기존 사용량27.27777545분 + 이번 준비35분이다. 시작23:23:08.464689, 준비 마감23:58:08.464689, 새 작업 마감00:43:08.464689, 전체 마감00:53:08.464689 KST. 전체960분 상한과 기존20분 종료 예약은 유지한다.

미확정 후기258.140222초와 U_pre 임시600초를 S3/전체 가용량에서 따로 예약한다. U_pre 실제는 미상이며600초는 실측이나 입증된 최대치가 아니다. 추가 확인량이 예약을 넘으면 중단하고 자동 증액하지 않는다. 이번90분은 예약과 별개로 준비·실행·자체 대기·정리·보고를 포함하며 Owner 대기만 제외한다.

입력·결과 위치: `private-evidence/E004`. 시간·상한·승인 상세는 기존 `integrated-execution/execution.json`의 `cfd_preflight`에 결속했다. 준비/양성 대조/필수 로그 가용성에서 첫 non-pass가 나오면 후속 compile/검사도 수행하지 않는다. [공개용 중립화]


## C-FD Preflight Stop — 2026-10-22 23:35 KST

결과는 `UNAVAILABLE`이다. C compile1회와 고정 검사 묶음1회를 수행했고 첫 non-pass인 M2에서 중단했다. 보정0·재실행0·추가 로그 조회0이다. 고정 입력 manifest SHA-256: `d84d0f5f9651c742bf92fd0ef4c92e318c00f77f3150025ad10827538e35db51`; 결과 SHA-256: `267abdb7b8eeaebdf7c5a30f29e6baafda0921fc8aae2f1d5878ed45d3c48ff4`. 원문은 `private-evidence/E004`에 보존했다. [공개용 중립화]

| 항목 | 관측 및 한계 |
| --- | --- |
| M0 | 같은 UID의 native C TCP/UDP IPv4·IPv6, A/B fixture, P/Q, 동일 task 경로 filesystem 양성 대조 성공. 초기 로그 조회 접근은 가능했으나 실제 거부 로그 적격을 뜻하지 않음 |
| M1 | 두 deny-default profile 시작 성공. proxy FD5개·runtime FD4개가 고정 허용 목록과 일치 |
| M2 일부 | runtime→exact P 연결과 proxy 상속 listener accept, 양방향 합성 bytes 일치 |
| 첫 non-pass | runtime PID42884의 Q 연결 `-1/EPERM(1)` 관측. 고정 10초 구간·PID predicate의 로그 결과 `[]`; 필수 PID/시각/network-outbound 근거 미확보로 UNAVAILABLE |
| 미실행 | M2 나머지 거부/path 보호, M3 FD 전달, M4 신규 IP/DNS, M5 목적지 불변, M6 명시적 shutdown 회수 |

이번 조회가 빈 결과라는 사실만 확인했다. OS가 로그를 생성하지 않았다는 원인 판정이나 C-FD의 영구 불가능 판정은 아니다. 로그 predicate·시점·가용성 중 어떤 요인이었는지도 미확정이다. 실행 중 판정 기준을 완화하거나 조회 범위를 넓히지 않았다. 미실행 코드 분기는 검증되지 않았으므로 차기 실행 입력으로 자동 채택하지 않는다. 기존 source/runtime/H05/H10의 적격 또는 Owner 수락으로 확대하지 않는다.

준비 실측 12.268337분/35분. 2026-10-22T14:38:08.820289+00:00 정산 cutoff까지 이번 활동 15.005927분/90분(준비·실행·정리·해석·기록 포함), 기존 전체 415.136361분/960분, S3 135.304526분/224.600936분이다. 매핑 누적 39.546112분/62.277775분. 미확정 예약14.302337분은 소비 실측과 분리해 계속 보유하며 U_pre 실제는 미상이다. cutoff 이후 최종 검증/보고는 미정산으로 남기고 다음 정산 때 한 번만 반영한다. 남은 시간은 자동 재실행 권한이 아니다.

종료: compiler·baseline·두 제한 역할의 process group 부재, fixture thread 종료, 보유 socket FD 닫힘을 확인했다. 제품 source tracked diff와 untracked inputs, host·기존3 binary·materializer·anchor/journal/lock hash가 유지됐다. product build2/3·correction1/2·runtime pause4·H05/H10은 변경하지 않았다. 제품·OS/PF·인증·외부 통신·Git 변경0이다.

보존: source/header/runner/profile/binary·정확한 argv/FD/환경·reservation·raw events/로그/결과는 Owner 결과 처분과 후속 C-FD 판단이 소비하므로 유지한다. 삭제: 종료 확인 뒤 p.sock·q.sock·합성 replacement-canary·빈 compiler-tmp를 정리했다. baseline 양성 대조용 create-canary·denied-child는 fixture 구성 중 이미 제거했다. 기존 active 경로 이동0이며 기존 evidence/worktree는 보존했다. 재시도 또는 제품 재개는 수행하지 않았다.


## C-FD Historical Log Read Authorization — 2026-10-22 23:50 KST

Owner가 A/B 각1회와 결과 저장·Work 기록을 승인했다. 고정 범위는 2026-10-22 23:35:20–23:35:35 KST의 기존 task 로그다. 기존 profile/probe/OS 변경0, 재실행0, H05/H10 및 기존 UNAVAILABLE 유지. 현재 사용자와 기존 실행 경계에서만 조회하며 command timeout 각5초·출력 각256KiB, 전체 활동 상한20분이다. 새 결과는 `private-evidence/E005`에 기록한다. [공개용 중립화]

미정산 7.587913분(직전 결과 보고 1.758785분 + 읽기 전용 진단/제안 5.829128분)을 기존 전체/S3에 먼저 반영했다. Owner 대기 구간은 제외했다. 이번 활동도 승인 시각부터 계상하며 기존 S3 상한224.600936분과 미확정 예약14.302337분, 전체960분 및 mapping/counts/journal은 유지한다. 신규20분은 기존 S3 안의 진단 한도이며 사용량 초기화나 C-FD 재개 권한이 아니다.


## C-FD Historical Log Read Result — 2026-10-22 23:53 KST

A·B 각1회 모두 exit0·stdout `[]`·stderr 빈 값으로 끝나 승인한 중단 조건에 도달했다. 추가 조회·probe 실행·profile·OS 변경0이며 기존 C-FD UNAVAILABLE와 H05/H10 not-qualified를 유지한다. 조회는 UID501/eUID501에서 수행했다. 원래 사건 시각23:35:25.411526에서 약18분 뒤, 23:35:20–23:35:35 KST를 절대 시간으로 고정했다.

| 조회 | 조건 | 실제 수행 | 결과 |
| --- | --- | --- | --- |
| A | 기존 kernel/sandboxd 및 `(42884)` 표기 조건 | 23:53:15.751030–23:53:16.494290 KST, 0.743262초 | 0건 |
| B | 발생 주체·괄호 표기 가정을 제거하고 exact task 경로 또는 PID 또는 binary명+PID로 한정 | 23:53:16.495898–23:53:17.230326 KST, 0.734437초 | 0건 |

해석: 기존 발생 주체·PID 표기 제한을 완화하고 뒤늦게 조회해도 해당 구간의 대응 로그를 확보하지 못했다. 따라서 원래 predicate만 바꾸거나 짧게 기다리면 해결된다는 근거는 얻지 못했다. 다만 미생성·미보존·현재 사용자에게 비가시·다른 식별 표현 중 무엇인지는 구분하지 못하며 권한 부족으로 단정하지 않는다. 기존 raw `[]`이므로 Python 후처리 시각/operation 필터가 수집된 행을 누락한 경우도 아니다. 사전 접근 확인 역시 알려진 sandbox 양성 로그가 없는 wrapper PID 조회여서 visibility proof가 아니었다.

정밀도 보충: 원래 `probe.c`의 Q 레코드는 socket()/connect()를 묶은 uds helper의 -1/EPERM이다. P 성공 직후라는 관측은 있으나 실패 syscall을 분리 기록하지 않았으므로 connect 자체 거부의 직접 trace라고 확대하지 않는다. 원래 source/결과 bytes는 수정하지 않았다.

기록 위치: `private-evidence/E005`. 원본 C-FD evidence manifest의 모든 파일 hash가 유지됐고, query argv·절대 시작/종료·elapsed·UID·exit·raw stdout/stderr·단일 예약·결과를 추가 보존했다. 두 log process group 부재를 확인했다. 새 probe/listener/socket은 없고 active 경로 이동0·삭제0이다. 이 고유 조회 근거는 Owner 진단 처분과 다음 최소 근거 계획에서 소비할 때까지 보존한다. [공개용 중립화]

2026-10-22T14:55:39.130082+00:00 cutoff 기준 이번 활동 5.551569분/20분(준비·조회·대기·해석·기록 포함). 사전 미정산 7.587913분을 먼저 반영했고 전체 확인 사용 428.275843분/960분, S3 148.444008분/224.600936분이다. 미확정 예약 14.302337분 유지 후 S3 계산상 잔여 61.854591분. 상한 증가·mapping 변경·product build/correction count·runtime journal 변경0. cutoff 이후 최종 확인/보고 시간은 미정산으로 보존하고 다음 continuation에서 한 번만 반영한다. 남은 시간은 재조회/재실행 권한이 아니다.


## C-FD Stream Diagnostic Authorization — 2026-10-23 00:07 KST

Owner가 최소 진단 실행을 승인했다. 기존 binary/runtime profile bytes를 재사용하고 stream·비민감 공개 준비 표식·정상 Q 연결·합성 Q 거부·저장 조회를 각각 최대1회로 제한한다. 준비 표식 미수신 등 첫 중단 조건에서 재시도 없이 종료한다. 기존 UNAVAILABLE/H05/H10은 유지하고 compile/profile/OS 변경 및 전체 C-FD 묶음 재실행은 제외한다. 새 결과 위치: `private-evidence/E013`. [공개용 중립화]

기존 미정산 9.485075분을 전체/S3에 먼저 반영했다. Owner 대기 구간은 제외했다. 이번30분은 기존 S3 상한224.600936분 안에서 준비·자체 대기·실행·해석·기록·정리·보고를 포함한다. 시작00:07:15.283176, 준비 마감00:22:15.283176, 새 작업 마감00:32:15.283176, 전체 마감00:37:15.283176 KST. 마지막5분은 종료·보존에 남긴다. 준비는 최대15분이며 기존 mapping 잔여 안에서 함께 계상하고 전체/S3에 중복 합산하지 않는다. 기존 전체960분·미확정 예약14.302337분·전역 종료 예약20분·cap/counts/journal/H05/H10은 유지한다.


## C-FD Stream Diagnostic Result — 2026-10-23 00:14 KST

승인한 stream·준비 표식·정상 Q 연결·합성 Q 거부·저장 조회를 각각1회 수행하고 종료했다. 재시도·추가 조회·C compile·profile 변경·OS 변경·전체 C-FD 재실행0이다. 기존 C-FD UNAVAILABLE와 H05/H10 not-qualified, product build/correction count와 runtime pause/journal을 유지한다. 진단 결과 확인은 원래 검사 묶음의 재판정이나 제품 적격·Owner 수락이 아니다.

| 항목 | 관측 |
| --- | --- |
| 정상 Q 양성 대조 | 같은 UID501/eUID501에서 기존 native binary의 Q helper 성공(rc3/errno0), 이번 listener accept 확인 |
| 제한 runtime | 기존 profile로 시작, 초기 FD4개, PID69327 |
| 준비 표식 | 합성 공개 표식1회, live stream 수신1건을 확인한 뒤에만 Q 실행 |
| Q 거부 | helper -1/EPERM(1), 00:14:09.756798 KST에 exact PID·Q 경로·network-outbound의 Sandbox deny live 로그1건 |
| 저장 조회 | 약10초 관찰 뒤 동일 predicate, 절대 구간00:14:06–00:14:20 KST로1회. exit0·stderr 없음. 준비 표식1건과 sandbox-exec 호환성 안내1건, 대응 거부 로그0건 |

이번 새 사건에서 sandbox 거부 로그의 생성과 현재 UID의 실시간 가시성은 확인했다. 저장 조회에서는 해당 거부가 보이지 않았다. 미저장·보존 지연·저장 조회 가시성 차이 중 원인은 아직 구분하지 못한다. 일반 표식의 저장 조회 성공이 Sandbox 로그의 저장을 증명하지는 않는다. 원래 PID42884 사건의 로그 생성/저장 여부를 소급해 확정하지 않는다. Q helper는 socket()/connect()를 묶으므로 개별 실패 syscall 직접 trace라는 확대 해석도 하지 않는다.

원문·고정 입력·argv·UID/PID·시각·reservation·결과는 `private-evidence/E013`에 보존했다. result SHA-256 `dc754f3d860c2a6d164abfc36048068fa7debcbb6ff5fc45bf69ec7480583eb7`. 원래 C-FD/A·B 근거와 binary/profile, 외부 frozen inputs·제품 tracked diff의 hash 유지 확인. 이번5개 process group과 capture thread 종료, socket FD 닫힘을 확인했다. 10초 관찰을 마친 stream의 exit -15는 계획된 controller 종료이며 timeout/non-pass가 아니다. 생성한 exact inode의 q.sock만 삭제했다. active 경로 이동0, 추가 삭제0. 고유 진단 근거는 Owner 결과 처분과 다음 근거 결정이 끝날 때까지 보존한다. [공개용 중립화]

2026-10-22T15:16:50.713322+00:00 cutoff까지 이번 활동 9.590502분/30분(준비·실행·자체 대기·해석·검증·기록 포함), 준비 6.873924분/15분이다. 사전 미정산9.485075분은 먼저 반영했고 이번 준비를 기존 mapping에도 귀속하되 전체/S3에는 중복 합산하지 않았다. 전체 확인 사용 447.351420분/960분, S3 167.519585분/224.600936분, mapping 46.420036분/62.277775분이다. 미확정 예약14.302337분 유지 후 S3 계산상 잔여 42.779014분. 상한 증가/초기화0. cutoff 이후 최종 검증·보고 시간은 미정산으로 남기고 다음 정산에서1회 반영한다. 남은 시간은 자동 재실행/재개 권한이 아니다.


## C-FD M2/M3 Stream Continuation Authorization — 2026-10-23 00:39 KST

Owner가 M2 잔여11항목과 M3 IPv4/IPv6 FD 전달·사용까지만 승인했다. 기존 binary/profile 및 runtime Q live 근거를 재사용하고 새 자원의 필요한 양성 대조와 두 역할 startup/FD를 확인한다. 준비 표식1회, stream1회 최대180초, 검사 묶음1회 최대300초, 첫 non-pass 중단·재시도0. 기존 전체 C-FD UNAVAILABLE/H05/H10을 유지하며 M4–M6·추가 저장 조회·C compile·product/profile/OS 변경0이다. 기록 위치는 `private-evidence/E006`. [공개용 중립화]

기존 미정산 6.337672분을 전체/S3에 먼저 반영했다. Owner 대기는 제외했다. 시작00:39:12.806287, 준비 마감00:51:12.806287, 새 작업 마감01:04:12.806287, 전체 마감01:09:12.806287 KST. 예상20–25분과 중단 상한30분을 구분한다. 준비12분은 기존 mapping 잔여에 귀속하고 전체/S3와 중복 합산하지 않는다. S3/전체 상한 증가·초기화0, 미확정 예약14.302337분·전역 종료 예약20분 유지.


## C-FD M2/M3 Stream Continuation Stop — 2026-10-23 00:45 KST

고정 검사 묶음1회 중 새 P 연결의 양방향 교환에서 첫 non-pass가 발생해 중단했다. 이번 묶음 결과는 FAIL이며 원래 C-FD UNAVAILABLE/H05/H10 not-qualified는 유지한다. stream0·준비 표식0·M2 잔여11항목0·M3 IPv4/IPv6 0회다. M4–M6·추가 저장 조회·C compile·product/profile/OS 변경0이며 실행 후 입력 보정·재시도0이다.

같은 UID의 새 P/Q, filesystem5항목과 TCP IPv4/IPv6 양성 대조는 성공했다. 제한 proxy/runtime startup은 rc0이고 FD5개/4개가 예상과 일치했다. proxy PID88794의 native P_ACCEPT는 accept fd=-1, rc=-1, errno35(EAGAIN)을 기록했고, runtime PID88795의 P_CONNECT helper도 약5초 뒤 rc=-1/errno35, fd3을 기록했다. runtime helper는 connect/exchange 복합이므로 실패한 개별 runtime syscall을 단정하지 않는다. 세 process stderr는 모두 빈 값이다.

정적 원인 분석: Driver가 새 runner의 P listener를 timeout5 상태로 만들고 native proxy에 넘기면서, 기존 `fd01/run.py:149`의 `P.sock.setblocking(True)`를 빠뜨렸다. 상속 전 blocking 복원 누락이 코드에서 확인되며 native accept EAGAIN 관측과 부합한다. 실행 중 FD flag trace나 수정 후 재현은 수행하지 않았으므로 원인 재현 완료로 표기하지 않는다. 이 시험 장치 문제를 C-FD 기구나 OS 격리의 실패로 확대하지 않는다. 원래 stream-read-01의 live 거부 근거도 그대로 유지한다.

준비 중 고정 입력 확정 전 source 문법 검사에서 newline literal 오류를 보정했고, 완성되지 않은 NDJSON 수신 행을 건너뛰도록 정리했다. 변경 전 hash와 역변환 정보를 preparation-static-review.json에 보존했다. 이는 최초 묶음 이전의 준비 수정이며 product correction count를 변경하지 않았다. 실행 이후 runner SHA `266376bb7ca547fdf8f217f2edadf1d5f3ccd2aaf606343bacda58fd3bdf77c0`는 유지했다. 결과 SHA `d3fcf0574dcb5e1697fb11a388ad92c95c2249331245ba5054f92a96817850d0`. 정확한 입력·raw stdout/stderr·argv·reservation·events·결과·분석은 `private-evidence/E006`에 보존한다. [공개용 중립화]

종료 검증: 세 task process group 및 capture/fixture thread 종료, 보유 socket FD 닫힘을 확인했다. setup 중 양성 대조 canary를 정리했고 종료 시 exact ownership의 replacement-canary/p.sock/q.sock을 삭제했다. fixture 잔존0·active 경로 이동0이다. 기존 C-FD/A·B/stream 근거, 외부 frozen inputs 및 제품 tracked diff hash가 유지됐다. 기존 product build2/correction1·runtime pause/journal·상한·H 상태는 변경하지 않았다. 고유 실패 입력과 원문은 Owner 실패 처분 및 listener-mode 복구 결정에서 소비할 때까지 보존한다.

2026-10-22T15:48:58.110168+00:00 cutoff 기준 이번 활동 9.755065분/30분, 준비 6.665850분/12분, 묶음 실행·종료 5.073438초/300초다. 사전 미정산 6.337672분을 먼저 반영했다. 전체 확인 사용 463.444157분/960분, S3 183.612323분/224.600936분, mapping 53.085886분/62.277775분이다. 미확정 예약14.302337분 유지 후 S3 계산상 잔여 26.686277분, mapping 잔여 9.191889분이다. cutoff 이후 최종 확인/보고는 다음 정산에서1회 반영하며 미정산을0으로 보지 않는다.

후속 후보는 P listener 상속 mode만 바로잡는 runner 보정과 한정 재검증이다. 현재 승인한 묶음1회가 소진됐으므로 새 수정·실행은 수행하지 않는다. 실패 입력을 덮어쓰거나 전체 기구 기준을 완화하지 않는다. STATUS/index/Work 완료 또는 Git 변경은 하지 않았다.


## C-FD Four-Fix M2/M3 Authorization — 2026-10-23 00:59 KST

Owner가 P listener blocking 복원, M3 전달 TCP FD blocking 복원, USEFD→fd_use 응답 이름 대응, 종료·원본 보존 확인의 최종 부분 PASS 결속 네 곳만 보정하고 M2 잔여/M3를1묶음 재검증하도록 승인했다. 실패 입력은 그대로 보존하고 새 경로 `private-evidence/E007`를 사용한다. C compile/profile/OS/product 변경0, M4–M6/추가 저장 조회/runtime Q 재검사0, 기존 UNAVAILABLE/H05/H10 유지. [공개용 중립화]

직전 보고·정적 계획의 미정산 7.200120분을 기존 전체/S3에 먼저 반영했다. Owner 대기는 제외했다. 시작00:59:14.603635, 준비 마감01:05:14.603635, 새 작업 마감01:12:14.603635, 전체 마감01:17:14.603635 KST. 예상12–16분과 중단 상한18분을 구분하며 준비6분은 기존 mapping 잔여에 귀속한다. stream1회 최대180초·묶음1회 최대300초·첫 non-pass 중단·재시도0. 기존 cap과 미확정 예약14.302337분·전역 종료 예약20분을 유지한다.


## C-FD Four-Fix M2/M3 Result — 2026-10-23 01:01 KST

승인한 네 곳만 보정한 새 runner로 검사 묶음1회·stream1회·준비 표식1회를 수행해 PARTIAL_M2_M3_PASS로 종료했다. 재시도0. P listener 상속 전과 M3 TCP FD 전달 전의 실제 blocking 상태를 확인했다. 기존 실패 입력 및 원래 C-FD UNAVAILABLE/H05/H10 not-qualified는 그대로 유지한다. M4–M6·C compile·product/profile/OS 변경·저장 조회·runtime Q 반복0이다.

M2 잔여11건 모두 native -1/EPERM, fixture identity 불변 및 고정 PID·시간·operation·resource 로그 대응 조건을 충족했다. 대응 원문은 직접 deny9건과 OS 중복 요약2건(runtime_RENAME/proxy_RENAME)이다. 두 요약의 시각은 각각 RENAME 명령 이후·다음 명령 이전이며 그 사이 다른 명령은 없다. 이 한정 oracle은 통과했으나 11개 독립 syscall 직접 trace로 확대하지 않는다.

M3 IPv4·IPv6 모두 receive_fd/실제 응답명 fd_use의 rc0, 예상 peer·family·port 및 fdWRITEfdSEND payload를 확인했다. fd_use 성공 행의 errno9는 native FD inventory의 잔여 값이며 원문을 보존했다. 실제 Rama/Tokio 통합은 미검증이다. 초기 proxy/runtime FD는5개/4개이고 P 양방향 교환과 새 자원의 양성 대조도 성공했다.

종료·보존 확인: 다섯 task process group과 capture/fixture thread 종료, 모든 보유 socket FD 닫힘, fixture 잔존0을 확인했다. setup 양성 대조 임시물을 정리했고 종료 시 exact ownership의 replacement-canary/p.sock/q.sock을 삭제했다. active 경로 이동0. 기존 실패 묶음·C-FD/A·B/stream 근거·외부 frozen inputs·product tracked diff hash 불변이다. 새 정확한 입력·raw 출력·events·result·검증·정산은 `private-evidence/E007`에 보존한다. 이 고유 근거와 이전 실패 입력은 Owner 부분 결과 처분 및 구체적인 M4 기준/M5–M6 결정에서 소비하고 수락 조건을 충족할 때까지 유지한다. [공개용 중립화]

2026-10-22T16:06:58.941291+00:00 cutoff까지 이번 활동 7.738961분/18분, 준비 2.444303분/6분, 묶음 실행·종료 2.926934초/300초다. stream은180초 상한 안에서 검사를 마친 뒤 계획대로 종료했다. 직전 미정산 7.200120분을 먼저 반영했고, 준비는 mapping에도 귀속하되 전체/S3에 중복 합산하지 않았다. 전체 확인 사용 478.383239분/960분, S3 198.551404분/224.600936분, mapping 55.530190분/62.277775분이다. 미확정 예약14.302337분 유지 후 S3 계산상 잔여 11.747196분, mapping 잔여 6.747586분. cutoff 이후 최종 확인/보고는 미정산으로 남겨 다음 정산에서1회 반영한다. 상한·product build2/correction1·runtime journal·기존 H 판단은 유지하며 STATUS/index/Work 완료 또는 Git publication 변경0이다.


## C-FD M4–M6 Plan Only — 2026-10-23

Owner 요청으로 기준과 최소 실행안을 `private-evidence/E115`에 정리했다. M4의 엄격한 socket 생성 금지와 downstream 직접 실행 근거 사이의 충돌 때문에 기존 기준 그대로 전체 PASS를 얻을 수 없다. M4-1 단일 생성 진단은 예상3–4분/중단5분의 선택지이며 M5/M6 독립 묶음은 예상8–12분/중단12분으로 현 잔여에 들어가지 않는다. 기준 변경/예산 증분/실행 승인은 적용하지 않았다. M2/M3 부분 PASS와 RENAME2건 중복 요약 로그 한계, 기존 UNAVAILABLE/H05/H10 판단을 유지한다. [공개용 중립화]

2026-10-22T16:14:09.246717+00:00까지 직전 미정산 1.178716분과 이번 계획 4.490757분을 전체/S3에 반영했다. Owner 대기는 제외했고 mapping은 변경하지 않았다. 전체 484.052712/960분, S3 204.220877/224.600936분, 미확정 예약14.302337분 후 S3 가용 6.077722분, mapping 잔여 6.747586분. cutoff 뒤 최종 확인/보고는 다음 정산 대상으로 남긴다. 검증 실행·compile·profile/OS/product·journal·Git publication·STATUS/index/Work 완료 변경0, 이동·삭제0. 고유 입력/결과와 계획은 Owner 처분 및 후속 검증 소비까지 유지한다.


## M4 Criteria Revision Proposal — 2026-10-23

Owner 요청에 따라 `private-evidence/E114`에 socket 생성과 통신 차단의 기준 분리 제안을 기록했다. 통신 보호 목적의 조건부 유지 가능성과 생성 자체 금지/모든 syscall 직접 실행 기준의 명시적 변경을 구분한다. 기준 채택0, 실행0, 기존 M2/M3 부분 PASS·로그 한계·UNAVAILABLE/H05/H10 유지. 새 task-only native/runner 보강·compile1·binary literal만 치환한 profile clone·M4 경로16+resolver/M5/M6 한 묶음은 예상14–18분/중단22분/준비10분 제안이며 미승인이다. [공개용 중립화]

2026-10-22T16:19:54.633808+00:00까지 직전 보고 1.361298분 + 이번 계획 3.736508분을 전체/S3에 반영했다. 미확정 예약 후 S3 가용 0.979916분, mapping 잔여 6.747586분. cutoff 기준 필요한 최소 증분은 S3 +21.020084분, mapping +3.252414분이고 실제 제안은 S3 +22분/mapping +3.252414분이다. 전체960분 상한은 유지하며 두 예약을 제외한 전체 가용 436.547145분 안에 수용한다. cap 실제 변경0, mapping charge0, cutoff 이후 보고 시간은 다음 정산 대상이다. profile/OS/product·journal·Git publication·STATUS/index/Work 완료 변경0, 이동·삭제0.

## M4 Criteria Adoption And Budget Admission Stop — 2026-10-23

Owner가 2026-10-23 16:25:51 KST에 앞서 보관한 M4 개정 기준·S3 +22분·mapping +3.252414분과 기존 전체16시간 내 최소 검증의 재개를 지시했다. 기준 채택과 두 증분을 적용했으며 전체960분·미확정 예약14.302337분·전역 종료 예약20분은 유지한다. 과거 제안/실행 기록은 수정하지 않고 현재 처분을 이 절에 추가한다.

직전 cutoff부터 최종 보고까지 미정산 82.336592초를 먼저 반영하니, 이번 재개 활동을 빼기 전부터 S3 가용은 21.607639분으로 승인안의 시작 조건22분보다 23.541630초 부족했다. 최초 예산 admission non-pass에서 중단했다. Driver의 직전 보고가 제안에 둔 여유58.794962초를 초과한 것이 원인이며 OS/격리 실패가 아니다. 검사 범위나 종료 여유를 줄여 실행하지 않았다.

2026-10-23T07:28:34.955633+00:00 cutoff까지 이번 재개·정산 활동 2.729148분을 전체/S3에 반영했다. Owner 대기와 별도 번외 검토·핸드오프 시간은 C-FD에 포함하지 않았다. 전체 사용 493.251943/960분, S3 사용 213.420108/246.600936분, 미확정 예약 후 S3 가용 18.878491분이다. mapping은 이번 charge0이며 가용 9.999999850분이다. 승인 숫자를 그대로 반영했으므로10분 대비9마이크로초의 표시 반올림 차이가 있으며 이번 중단의 실질 이유는 S3다. 미확정·전역 종료 예약 후 전체 가용은 432.445720분이다. cutoff 뒤 최종 확인/보고는 다음 정산 대상이다.

M4–M6 준비·compile·묶음·stream·resolver IPC·profile/OS/product 변경·실제 runtime/model/auth/send0. 기존 UNAVAILABLE, M2/M3 부분 PASS와 로그 한계, H05/H10 not-qualified를 유지한다. 상세 정산·직전값·복구 정보는 기존 execution.json의 m4_m6_admission_01에 보존한다. STATUS/index/Work 완료/Git publication 변경0, 이동·삭제0. 이후 실행은 잔여 창 부족에 대한 Owner 처분 뒤 판단한다.

## M4–M6 Single Bundle Result — 2026-10-23

Owner가 S3 추가5분을 승인해 직전 보고 미정산 76.847662초를 먼저 반영했다. 시작 시 S3 가용 22.597697분으로22분 창을 충족했다. 기존 개정 기준에 따라 task-only native compile1회·묶음1회·stream1회·표식1회만 수행하고 첫 non-pass에서 중단했다. 재시도0. 새 binary와 두 profile clone은 기존 binary literal2곳씩만 치환했고 network 권한·OS·product source는 변경하지 않았다. 기존 실패 입력·M2/M3 근거를 보존했다.

결과는 UNAVAILABLE다. 정상 대조에서 IPv4/IPv6의 TCP connect·bind/listen·UDP connect/send·sendto와 B endpoint, resolver UDS connect-close가 성공했다. resolver payload/DNS query는0이다. 제한 runtime IPv4 TCP connect·TCP bind·UDP connect는 socket 생성 성공 뒤 -1/EPERM과 직접 OS 로그·fixture 불변이 대응됐다. 로그 resource는 각각 remote:*:52558/local:*:0/remote:*:49630이며 wildcard 주소를 정확한 IP의 독립 증거로 확대하지 않는다. bind 뒤 listen과 UDP connect 뒤 send는 dependency-blocked로 남긴다.

다음 runtime IPv4 UDP sendto도 -1/EPERM이고 fixture 변화는 없었지만,5초 내 해당 명령의 직접 로그 대신 동일 PID·UDP 목적지의1 duplicate report만 관측됐다. 이번 직접 로그 기준에 따라 이 경로는 UNAVAILABLE이며 전체 M4 PASS가 아니다. runtime IPv6·proxy IP·제한 역할 resolver·M5/M6는 실행하지 않았다. 실제 Rama/Tokio/TLS/auth/public IP/제품 채택 근거로 사용하지 않는다. 원래 UNAVAILABLE와 H05/H10 not-qualified, M2/M3 부분 PASS·기존 로그 한계를 유지한다.

종료 확인: compile 포함6개 process group 부재, capture/fixture thread 종료, socket FD 닫힘, 이전 입력/결과 hash 불변을 확인했다. task 소유 p.sock과 검증된 빈 compiler-tmp만 삭제했고 active 경로 이동0이다. 새 native source·binary·profile clone·runner·raw 로그·결과는 UDP 로그 귀속에 대한 Owner 처분과 별도 승인 후속의 입력으로 보존한다. 기록은 private-evidence/E009 및 closeout.json이다. [공개용 중립화]

2026-10-23T07:42:24.786286+00:00 cutoff까지 이번 활동 9.734486분/22분, 준비 6.889671분/10분, compile0.346446초/120초, 묶음 7.642047초/180초다. 준비는 mapping에도 귀속하되 전체/S3에 중복 합산하지 않았다. 전체 사용 504.267223/960분, S3 사용 224.435389/251.600936분, 미확정 예약 후 S3 가용 12.863211분, mapping 잔여 3.110329분이다. 미확정·전역 종료 예약 후 전체 가용 421.430440분이다. cutoff 이후 확인/보고는 다음 정산 대상으로 남긴다. 기존 product counts/H 상태·runtime journal·STATUS/index/Work 완료·Git publication 변경0이다.


## UDP Sendto Single Diagnostic Authorization — 2026-10-23

Owner가 S3 +5분/mapping +3분과 단일 진단1회를 승인했다. 직전 보고 139.374807초와 원인 분석·제안 189.078318초를 먼저 전체/S3에 반영했고 Owner 대기는 제외했다. 시작 2026-10-23T07:54:55.175785+00:00; 12분/준비6분/새 작업9분/종료 여유3분 한도다. 시작 S3 가용 12.38899206666665분, mapping 6.110328966666668분이며 admission True. 기존 binary/runtime profile bytes를 재사용하고 새 runner에서 IPv4 UDP sendto만 정상대조1·제한진단1·stream1·표식1로 확인한다. PID·명령 시간·operation·정확한 포트의 직접 로그, EPERM, fixture 불변을 요구한다. 첫 non-pass 중단·재시도0, compile/proxy/resolver/M5/M6/product/OS 변경0. 기존 UNAVAILABLE/H05/H10과 기존 증거는 유지한다. 기록 private-evidence/E012 예상8–10분은 기존 준비6.89분/묶음7.64초와 재사용에 근거한 판단이며 12분 상한과 구분한다. 준비는 mapping에 귀속하되 전체/S3에 중복 합산하지 않는다. [공개용 중립화]


## UDP Sendto Single Diagnostic Result — 2026-10-23

승인된 정상 대조1·runtime IPv4 UDP sendto1·stream1·표식1을 수행해 PARTIAL_SENDTO_PASS로 종료했다. 재시도0, compile/profile/product/OS 변경0. 기존 바이너리와 runtime profile의 bytes/hash를 재사용했다. 새 runtime PID87693의 첫 제한 네트워크 호출은 sendto였으며 native -1/EPERM, 명령 시각 07:58:38.618439Z 뒤 직접 OS 로그 07:58:38.618681Z의 network-outbound remote:*:49630, fixture 불변을 확인했다. 정상 대조의 canary7 송수신은 성공했고 제한 호출 이후 추가 수신은 없었다. 주소 wildcard를 정확한 IP의 독립 증거로 확대하지 않는다.

기존 연속 connect/sendto에서의 OS 중복 집계 가설을 뒷받침하지만 내부 집계 key/window 또는 원인의 통제 재현을 입증하지 않는다. 이번 한 경로만 추가 근거로 기록하며 기존 전체 C-FD UNAVAILABLE, H05/H10 not-qualified, M2/M3 부분 PASS와 이전 로그 한계는 유지한다. 나머지 M4, proxy/resolver, M5/M6는 실행하지 않았다. 실제 runtime/model/auth/provider·Git publication·STATUS/index/Work 완료 변경0이다.

입력/보호 대상218개 hash, native 호출 순서, raw direct log1+표식1, 네 child process group 부재 및 capture/fixture thread 종료와 socket FD 닫힘을 확인했다. 파일 경로 이동·삭제0이며 disposable 파일은 없었다. 새 고유 runner/승인/원문/결과/정산과 이전 실패·부분 증거는 Owner 처분 및 별도 승인 잔여 검증의 비교·복구 입력으로 보존한다. 증거 경로: private-evidence/E012 [공개용 중립화]

2026-10-23T08:00:23.364320+00:00 cutoff까지 이번 활동 5.469809분/12분, 준비 3.689914분/6분, 단일 묶음 2.133742초다. 직전 보고·분석 미정산 5.474219분은 시작 전에 반영했고 Owner 대기는 제외했다. 전체 사용 515.211251/960분, S3 사용 235.379416/256.600936분, 미확정 예약 후 S3 가용 6.919183분, mapping 잔여 2.420415분이다. 미확정·전역 종료 예약을 유지하며 cutoff 이후 최종 확인·보고는 다음 정산에1회 반영한다. 추가 실행 권한으로 남은 시간을 자동 사용하지 않는다.


## M4 Remainder And M5/M6 Authorization — 2026-10-23

Owner가 S3 +18분/mapping +7분과 M4 잔여14개→M5/M6 IPv4·IPv6 단일 묶음1회를 승인했다. 직전 보고 78.072761초와 계획·보고 180.623736초를 전체/S3에 먼저 반영했고 Owner 대기는 제외했다. 시작 2026-10-23T08:06:14.392524+00:00; 이번20분/준비9분/새 작업15분/종료 여유5분이다. 시작 S3 가용 20.60757486666665분, mapping 9.420414616666669분이며 admission True. 기존 runtime IPv4 네 경로와 M2/M3 근거를 한계와 함께 재사용한다. runtime IPv6, proxy IPv4, proxy IPv6 각각 TCP connect/bind/UDP connect용 A와 sendto용 B를 다른 PID로 배치하고 resolver는 runtime A/proxy IPv4 A에서 확인한다. 기존 binary/profile bytes 재사용·compile0, stream1·표식1·묶음1·첫 non-pass 중단·재시도0이다. 새 fixture의 정상 대조와 resolver connect-close(payload0), M5 같은 FD 정상 사용/peer 불변/B 신규 수신0, M6 같은 FD shutdown/EOF/추가 write 실패/신규 payload0을 확인한다. 기존 UNAVAILABLE/H05/H10·기존 로그 한계를 유지한다. 예상12–16분(준비6–8/실행대기1–2/검증정리보고5–6)은 판단값이며20분 상한과 구분한다. 준비는 mapping에 귀속하되 전체/S3에 중복 합산하지 않는다. 기록 private-evidence/E010 [공개용 중립화]


## M4 Remainder And M5/M6 Single Bundle Result — 2026-10-23

승인된 단일 묶음1·stream1·표식1을 실행했고 M4 runtime resolver에서 첫 non-pass가 발생해 UNAVAILABLE로 중단했다. 재시도0. 준비 중 새 slot 반환 필드 누락을 정적 확인으로 보정한 뒤 입력을 확정했고, 여섯 slot/14개 경로와 matcher18조건 및 M5/M6 기존 절차 재사용의 정적 검증을 통과했다. 이 준비 보정은 native 실행 전이며 변경 전후 hash와 exact 한 줄을 보존했다. 실행 후 runner 변경0이다.

정상 IPv4/IPv6 네 경로씩, B4/B6 endpoint, resolver connect-close는 성공했으며 resolver payload/DNS query0이다. 여섯 제한 프로세스 startup FD도 확인했다. R6A runtime PID2820의 IPv6 TCP connect·TCP bind·UDP connect는 socket 생성 성공 뒤 -1/EPERM, 직접 OS 로그와 fixture 불변을 확인했다. 대응 resource는 remote:*:52559, local:*:0, remote:*:53669이다. 주소 wildcard는 정확한 IP의 독립 로그 근거가 아니며, listen/send는 dependency-blocked로 유지한다.

다음 resolver dns_connect도 -1/EPERM이었지만, 17:12:04.625346 KST의 같은 PID 로그는 file-read-metadata /var였다. 5초 내 승인 oracle이 요구하는 network-outbound 및 resolver service 경로의 직접 로그를 얻지 못했다. 중복 요약은 이번 원문에 없었다. 관측된 metadata 거부를 resolver network 차단의 qualified 증거로 바꾸거나 내부 원인 재현으로 단정하지 않는다. 이번 묶음은 UNAVAILABLE이며 기존 전체 UNAVAILABLE/H05/H10 not-qualified, M2/M3 부분 PASS와 runtime IPv4 네 경로 근거를 유지한다. runtime IPv6 sendto, proxy IP8개/proxy resolver, M5/M6는 미실행이다. 다른 다섯 native slot은 startup만 수행했다. 실제 runtime/model/auth/provider·compile/profile/OS/product·Git publication·STATUS/index/Work 완료 변경0이다.

종료 검증: 아홉 child process group 부재, capture/fixture thread 종료, socket FD 닫힘, fixture 불변 및 보호 대상252개 hash를 확인했다. task 소유 p.sock만 삭제했고 active 경로 이동0이다. 고유 runner/정적 준비 기록/승인/원문/결과/정산 및 이전 실패·부분 증거는 Owner resolver 근거 처분과 별도 승인 잔여 검증의 비교·복구 입력으로 보존한다. 증거 경로: private-evidence/E010 [공개용 중립화]

2026-10-23T08:14:02.223964+00:00 cutoff까지 이번 활동 7.797191분/20분, 준비 5.799780분/9분, 단일 묶음 7.391244초다. 직전 보고·계획 미정산 4.311608분을 먼저 반영했고 Owner 대기는 제외했다. 전체 사용 527.320050/960분, S3 사용 247.488215/274.600936분, 미확정 예약 후 S3 가용 12.810384분, mapping 잔여 3.620635분이다. 준비를 mapping에도 귀속하되 전체/S3에 중복 합산하지 않았고 미확정·전역 종료 예약은 유지했다. cutoff 뒤 최종 확인·보고는 다음 정산에1회 반영한다. 남은 시간으로 보정·추가 실행하지 않는다.


## Canonical Resolver Diagnostic Authorization — 2026-10-23

Owner가 resolver 정규 경로 진단, 실행파일 경로 literal만 치환하는 두 profile 사본 예외, S3 +7분/mapping +4분을 승인했다. 직전 보고 82.479847초와 분석·제안 252.189086초를 먼저 전체/S3에 반영했고 Owner 대기는 제외했다. 시작 2026-10-23T08:23:31.878197+00:00; 이번14분/준비7분/새 작업10분/종료 여유4분이다. 시작 S3 가용 14.232568649999983분, mapping 7.620634650000001분이며 admission True. 새 native 사본에서 DNS path만 /private/var/run/mDNSResponder로 바꾸고 compile1, 두 profile은 exact executable literal2곳씩만 치환한다. 네트워크·metadata 권한 추가0, 기존 입력/결과 불변이다. 두 경로의 같은 socket identity를 고정/확인하고 정상 connect-close1(payload0), 제한 runtime/proxy 각1·stream1·표식1·묶음1을 수행한다. 첫 non-pass 중단·재시도0, M4 IP/M5/M6 실행0, 기존 UNAVAILABLE/H05/H10 유지. 예상8–11분(준비4–6/실행대기0–1/검증정리보고4)은 판단값이며14분 상한과 구분한다. 준비는 mapping에 귀속하되 전체/S3에 중복 합산하지 않는다. 기록 private-evidence/E011 [공개용 중립화]


## Canonical Resolver Diagnostic Result — 2026-10-23

승인된 native compile1·진단 묶음1·stream1·표식1을 실행해 PARTIAL_CANONICAL_RESOLVER_PASS로 종료했다. 정상 canonical connect-close1과 제한 runtime/proxy 각1을 수행했고 재시도0, payload/DNS query0이다. native는 DNS path 한 곳만 /private/var/run/mDNSResponder로 변경했다. 두 profile 사본은 executable literal2곳씩만 치환했고 network/metadata 규칙은 원본과 byte-identical이다. 원본 입력·정책·결과와 기존 바이너리는 보존했다.

현재 /var→private/var alias 및 두 resolver 경로의 같은 socket dev16777231/inode153868179를 고정하고 정상 대조·제한 호출 전후 동일성을 확인했다. runtime PID17604, proxy PID17606 모두 dns_socket 성공 뒤 dns_connect -1/EPERM이었다. 직접 OS 로그는 각각 17:28:30.106963/17:28:30.163938 KST의 network-outbound /private/var/run/mDNSResponder였으며 metadata 거부·중복 요약은 이번 원문에 없었다. 두 역할의 이 정규 서비스 경로에 한정된 부분 근거다. 기존 /var alias의 선행 metadata 차단 설명을 뒷받침하지만 OS 내부 인과 추적 완료나 일반 DNS 우회 차단의 검증으로 확대하지 않는다. 기존 alias UNAVAILABLE 기록·전체 UNAVAILABLE·H05/H10 not-qualified를 유지하고 나머지 M4 IP/M5/M6는 실행하지 않았다.

종료 검증: compile 포함6개 process group 부재, capture thread 종료, socket FD 닫힘, 보호 대상320개 및 새 binary/input hash를 확인했다. task 소유 p.sock과 검증된 빈 compiler-tmp만 삭제했고 active 경로 이동0이다. 고유 source/binary/profile/runner·승인·원문·결과·정산과 원래 alias 실패/이전 부분 증거는 Owner 처분 및 별도 승인 잔여 검증의 비교·복구 입력으로 보존한다. 기록 private-evidence/E011 실제 runtime/model/auth/provider·OS/product·Git publication·STATUS/index/Work 완료 변경0이다. [공개용 중립화]

2026-10-23T08:30:50.784268+00:00 cutoff까지 이번 활동 7.315101분/14분, 준비 4.927109분/7분, compile 0.338176초, 단일 묶음 2.670255초다. 직전 보고·계획 미정산 5.577816분은 시작 전에 반영했고 Owner 대기는 제외했다. 전체 사용 540.212967/960분, S3 사용 260.381132/281.600936분, 미확정 예약 후 S3 가용 6.917467분, mapping 잔여 2.693525분이다. 준비를 mapping에도 귀속하되 전체/S3에 중복 합산하지 않았고 미확정·전역 종료 예약은 유지했다. cutoff 이후 최종 확인·보고는 다음 정산에1회 반영한다. 추가 실행은 하지 않는다.


## Remaining M4 IP And M5/M6 Authorization — 2026-10-23

Owner의 계속 진행 요청으로 직전 최소 검증안을 실행한다. 미정산 289.902214초(직전 보고92.495746+계획보고197.406468)를 먼저 전체/S3에 반영하고 S3 +14분/mapping +5분을 1회 적용했다. 시작 2026-10-23T08:41:26.143600+00:00, 예상9–12분/상한16분/준비7분/새 작업12분/종료 여유4분. 시작 S3 가용 16.085764분, mapping 7.693525분으로 admission 통과. 제한 PID5개로 M4 IP9개와 M5/M6 IPv4→IPv6를 단일 묶음1회 검증한다. 기존 binary/profile 및 이전 부분 근거는 유지하고 resolver 호출/compile/제품/OS/Git 변경0, 첫 non-pass 중단·재시도0이다. 전체960분·미확정 및 종료 예약·기존 UNAVAILABLE/H05/H10 판단을 유지한다. 준비는 mapping에도 귀속하되 전체/S3에는 중복 합산하지 않는다. Owner 대기는 제외한다. 기록 private-evidence/E008 [공개용 중립화]


## Remaining M4 IP And M5/M6 Single Bundle Result — 2026-10-23

승인된 묶음1·stream1·표식1을 실행했다. M4 잔여 IP9개는 모두 native -1/EPERM, PID/시각/operation/resource에 대응하는 직접 OS 로그와 fixture 불변을 확인했다. 기존 runtime IPv4 4개·IPv6 3개와 결합해 두 역할의 IP16개에 대한 부분 근거를 확보했다. wildcard resource를 정확한 IP의 독립 로그 근거로 확대하지 않으며 listen/send 후속은 dependency-blocked다. 별도 바이너리의 정규 resolver 두 역할 부분 결과와 기존 alias UNAVAILABLE 이력은 구분해 유지한다. 정상 IP8개와 B4/B6 대조도 통과했다.

첫 non-pass는 M5 IPv4 retarget이다. proxy PID33904가 controller의 연결 FD를 받아 정상 fdWRITE/fdSEND를 수행했고 peer는 127.0.0.1:52558로 유지됐다. 다른 목적지 B4를 지정한 sendto는 -1/EPERM이었다. 고정 oracle은 EISCONN 또는 원래 A로만8바이트 전송을 허용하므로 이번 결과는 FAIL로 중단했다. 캡처된 직접 OS 로그는 network-outbound remote:*:52560 거부이며, 종료 원문의 A4 수신은 fdWRITEfdSEND뿐이고 B4/B6는 정상 대조 BBASE 이후 추가 수신이 없다. 거부 관측과 판정 조건 불일치를 구분하며 사후 PASS 전환이나 네트워크 우회 성공으로 해석하지 않는다. 내부 OS 원인은 별도 미확정이다. M6 IPv4·M5/M6 IPv6는 미실행, 재시도0이다. 기존 전체 C-FD UNAVAILABLE와 H05/H10 not-qualified는 유지한다.

준비 정적 검사에서는 PID5개/IP9개/DNS 호출0, 기존 matcher18조건의 동일 AST 재사용, M5/M6 본문 byte-identical을 확인했다. native compile/profile/product/OS/model/auth/provider 변경0, Git publication·STATUS/index·Work Done 변경0이다. 다음 권고는 기존 원문으로 EPERM이 M5 목적지 불변 계약에 부합하는지 판정 조건을 먼저 검토하는 것이며, 조건 수정·후속 실행은 이번 범위에 포함하지 않는다.

종료 확인: child8개와 driver를 포함한9개 process group 부재, capture/fixture thread 종료, socket FD 닫힘, 보호 대상369개 hash 불변을 확인했다. task 소유 p.sock만 삭제했고 active 경로 이동0이다. 고유 runner/승인/원문/결과/정산 및 기존 근거는 Owner의 M5 판정 처분과 별도 승인 잔여 검증의 비교·복구 입력으로 보존한다. 별도 복사·새 백업은 만들지 않았다. 기록 private-evidence/E008 [공개용 중립화]

2026-10-23T08:46:22.770977+00:00 cutoff까지 이번 활동 4.943790분/16분, 준비 3.021503분/7분, 단일 묶음 2.310562초다. 직전 미정산 4.831704분을 먼저 반영했고 Owner 대기는 제외했다. 전체 사용 549.988460/960분, S3 사용 270.156625/295.600936분, 미확정 예약 후 S3 가용 11.141974분, mapping 잔여 4.672022분이다. 준비를 mapping에도 귀속하되 전체/S3에 중복 합산하지 않았으며 미확정·전역 종료 예약은 유지했다. cutoff 뒤 최종 확인·보고는 다음 정산에1회 반영하고 남은 예산으로 보정·추가 실행하지 않는다.


## Full Work Goal And Continuous Execution Authorization — 2026-10-23

Owner 요청627284518에 따라 FEAT-20261022-001 전체 승인 범위의 완료와 최종 수락용 증거·결과 보고 준비를 Goal로 등록했다. M4/M5/M6만을 목표로 축소하지 않는다. 기존 회차별 단일 묶음/첫 non-pass 뒤 전체 중단/재시도0 운영은 이번부터 대체한다. non-pass 실행은 즉시 중단·원문 보존하되 범위 내 원인 분석·최소 보정·필요 재검증은 이어간다. 다음 시도 전 변경점·검증 목적을 본 기록과 장부에 남기며 동일 조건의 근거 없는 반복·중복 검사·routine 재승인은 하지 않는다. 이는 실패의 사후 PASS나 보안/Done Criteria 완화가 아니다.

멈추는 경계는 승인 범위 밖 또는 실질 요구/판정 기준 변경, 필수 권한/입력 부재, 전체 누적 한도, Owner 최종 수락 또는 별도 Git publication 승인이다. 기존 UNAVAILABLE/H05/H10 승격과 제품·OS·인증·모델 등 제외는 유지한다. 실제 C-FD 채택/endpoint·controller 구조 통합은 기존 사전 검증과 별도 범위이며 현재 승인을 가정하지 않는다. Owner 수락과 Work Done을 구분한다.

직전 cutoff→최종 보고 86.426225초를 전체/S3에1회 반영했고 그 뒤 Owner 대기는 제외했다. 새 활동 시작 2026-10-23T08:49:57.344428+00:00; 전체 기사용 551.428897/960분, 미확정 14.302337분과 전역 종료20분을 제외한 작업 가용 374.268766분. 잔여 ceiling은 S3 40/S4 55/S5 145/S6 90/S7 35분(합365분), 미배정 9.268766분이다. S3 준비 mapping 잔여20분은 S3 40분 안의 부분 한도이며 중복 합산하지 않는다. 단계 예산은 전체 잔여 안에서 필요에 따라 재배분하고 전체960분/예약은 늘리거나 차용하지 않는다. 원 runtime journal/anchor는 현재 pause4 그대로 두며 실제 모델-runtime 재개 전 별도 장부와 시간 정합성을 확인한다.

조건부 예상은 S3 독립 근거20–35/S4 55–85/S5 125–145/S6 60–90/S7 30–45분(합290–400분)이다. S5의 과거 pair117.53분 외에는 판단값이며 build/검사/자체대기/리뷰/기록을 포함, Owner 대기 제외·겹침1회다. 상단 예상은 배정365분을 넘고 C-FD 통합은 미승인이라 전체 완주를 약속하지 않는다. 먼저 현 증거·독립 검증과 실제 gate를 정리한다. 실패 원문 보존·현재 navigation 갱신 외 historical verdict는 변경하지 않았다. 기록 private-evidence/E014 [공개용 중립화]


## Independent S3 Checks — 2026-10-23

Goal 운영 전환 뒤 첫 신규 실행은 기존 offline 격리 canary6개와 verifier/write 두 worker profile의 OS negative7개씩이다. 이전에 미실행인 독립 항목이며 실제 auth/provider/runtime C-FD 채택과 무관하다. 기존 task runner 사본에서 E 경로를 원 위치로 고정하고 S3 진입 확인을 활성 Goal 승인으로 연결한다. profile/fixture/syscall/errno oracle/timeout은 변경하지 않는다. 첫 non-pass가 나오면 해당 runner를 중단하고 원문을 보존한다. 다음 보정은 관측 원인과 변경 목적을 먼저 기록하며, 권한 또는 실질 oracle 변경은 Owner 결정으로 남긴다. exact 입력은 integrated-execution/goal-continuation-01/independent-s3-attempts.json에 고정했다.


## Independent M6 Verification Intent — 2026-10-23

offline canary6/6와 문서 verifier/write OS negative14/14가 기존 profile/oracle로 PASS했고 process 종료·문서/profile 불변을 확인했다. 다음은 M6 IPv4/IPv6 독립 검사다. M5 FAIL/판정표를 보존하고 RETARGET을 재실행하지 않는다. 새 controller 연결 FD마다 같은 proxy FD의 정상 fdWRITE/fdSEND와 echo drain을 먼저 확인하고, 같은 socket duplicate의 shutdown(SHUT_RDWR), proxy EOF·EPIPE/ENOTCONN/ECONNRESET write 실패, endpoint EOF 동기화와 AFTER_REVOKE 신규 수신0을 기존 기준으로 확인한다. M6가 M5 통과를 입증하거나 전체 gate를 해제하지 않는다. native binary/profile/권한/제품 변경0, C compile0, M4/resolver/stream 반복0. 예상4–6분·부분 작업8분 상한은 S3 잔여 안에 포함하며 추가 예산이 아니다. exact 입력과 변경 목적은 fd01/m6-independent-01에 보존한다.


## Goal Progress, Coverage And Owner Decision Boundary — 2026-10-23

전체 Work는 미완료다. 독립 offline 격리 canary6/6, 문서 verifier/write OS negative14/14, M6 IPv4/IPv6 명시적 회수는 PASS다. M6는 fresh 동일 FD의 fdWRITE/fdSEND echo drain 뒤 EOF와 EPIPE32, endpoint EOF 동기화 및 AFTER_REVOKE 수신0을 확인했다. C-FD M5 원 FAIL, 전체 UNAVAILABLE, H05/H10 not-qualified는 유지한다. 원 candidate3 binaries/source/host/lock identity 불변을 확인했다.

### H09 Documentary Cases

| Case | Request | Choice | Reason And Admission | Open Boundary |
| --- | --- | --- | --- | --- |
| H09-ordinary | 한 안내문의 승인된 링크·설명을 수정해 결과 하나를 수락한다. | ordinary Work | 결과/수락 단위가 하나이며 독립 child 수락이 없다. 대상·목표·완료 기준·권한을 먼저 고정한다. | 실제 파일은 미지정이며 착수 승인이 아니다. |
| H09-same-work | 그 안내문의 고정 verifier가 찾은 누락을 같은 파일·목표 안에서 보정한다. | same Work continuation | 원 승인·입력·실패·누적 예산과 동일 verifier를 이어받는다. 새 독립 수락 단위가 아니다. | 새 대상/요구는 원 범위에 자동 포함하지 않는다. |
| H09-umbrella | API 안내와 배포 안내를 각각 수락하고 두 결과의 일관성을 통합 수락한다. | umbrella | child별 독립 수락과 parent 통합 기준이 모두 필요하다. child 경계·의존성·책임을 먼저 고정한다. 파일 수만으로 선택하지 않는다. | 실제 child/책임자는 미지정; 병렬 실행·생산성 실측의 근거가 아니다. |

위3건은 합성 문서 판정 근거이며 실제 umbrella 실행/효율·사용자 이해도 또는 Owner 수락을 주장하지 않는다.

### Completion Evidence Matrix

| Criterion | Current Evidence | Remaining |
| --- | --- | --- |
| H01 | 기존 S1/S2 focused negative | actual host foreign thread/turn/call·Owner 사칭·grant/home/action/scope 거절 미완료 |
| H02 | prepared primitive·focused guard | offline8·actual host exact bytes/handle 교체·중복 거절 미완료 |
| H03 | worker/verifier14·offline6 PASS, C-FD 부분 근거·M6 양 주소군 | 원 runtime profile·최종 실제 대상 경계 미완료 |
| H04 | 기존 Core 계약 재사용 | 순정 installed grant accept1회·used/revoked/other Work 거절 미완료 |
| H05 | not-qualified 유지 | S0–S5 process death/pending·Owner exact 원 ticket replay 미완료 |
| H06 | 기존 focused 근거 | actual host fixed verifier fail-correct-pass 미완료 |
| H07 | runtime journal clock guard 실제 거절 | 누적량/입력/pending을 보존하는 복구 및 actual resume 미완료 |
| H08 | 실제 중단·보존 관측 | actual host scope/revoke/limit/stop/post-submit matrix 미완료 |
| H09 | 아래 합성 문서 사례3개 준비 | Owner 수락 대기; 실사용 효율 주장은 하지 않음 |
| H10 | not-qualified 유지, 실제 대상 접근0 | exact5문서·전달/intent/grant/refs/commit·내용/Owner 부담 관측 미완료 |

S5 full은 최종 candidate/profile/clock gate가 미해결인 상태에서 소모하지 않았다. 의무를 면제하지 않으며 C-FD 통합이 source를 바꿀 때 무효화될 수 있는 중복 검사를 피한다. S7 R1도 미완성 통합 결과를 최종 검토라고 전송하지 않았다.

### Decisions Required Together

B1 — 실질 M5 판정 기준 변경. 관측: IPv4 RETARGET -1/EPERM; A peer 유지, B4 direct network-outbound 거부; 고정 oracle의 EISCONN/rc8에 해당하지 않아 원 FAIL 유지 필요한 결정: 향후 새 실행에 EPERM + exact PID/time/op/B endpoint 직접 로그 + 정상 동일 FD/전후 A peer + 정상 B 대조 및 동기화한 신규 수신0을 별도 OS 차단 분기로 채택할지. IPv4/IPv6 fresh 검증과 protocol 거부 구분; 과거 FAIL 소급 변경 없음.

B2 — 제품/runtime 변경 제외 및 clock 복구 계약. 관측: 기존 Budget.read가 activity clock drift로 거절. wall/monotonic 약22094초 차이 vs 허용2초. pause4 중 일부 활동은 별도 장부에 이미 계상됨. 필요한 결정: 기존 anchor/journal/hash·누적 사용량·카운터·pending을 보존하는 명시적 복구 계약과 Python/Rust 대응 변경안을 허용할지. 2초 guard 완화/장부 초기화/전체 gap을 Owner 대기로 처리하지 않음. exact diff 검토 전 구현하지 않음.

B3 — C-FD 구조 채택 및 제품 통합 범위. 관측: 원 numeric TCP runtime profile compile 실패; 실제 proxy는 여전히 TcpStream::connect를 호출. task-only C-FD 부분 근거는 실제 통합이 아님. 필요한 결정: C-FD를 UDS + controller 발급 FD 통합 후보로 선택할지. 선택 뒤 CONNECT/TLS/auth/frozen endpoint 유지, 권한/회수/원장 결속, exact 파일 범위와 rollback을 구체화한다. 방향 선택은 blanket 구현 승인이 아님.

H05 exact 원 ticket 및 H10 exact 대상/전달·Git 수락 packet은 아직 생성되지 않았다. 지금 백지 승인을 받거나 실제 대상 자료를 먼저 열지 않는다. 해당 단계에 도달하면 구체 입력을 준비한다. 현재는 Owner 지정 정지 조건1(실질 oracle/승인 밖 변경)에 해당한다. Goal 등록과 독립 근거의 PASS를 전체 완료로 바꾸지 않는다.

### Time And Retention

2026-10-23T09:08:18.814082+00:00까지 Goal 활동 18.357828분, 전체 569.786725/960분이다. 미확정858.140222초·전역 종료1200초를 보존하며 작업 가용 355.910938분, S3 가용 21.642172분, mapping 17.646691분이다. 기존 미정산86.426225초는 시작 때1회 반영했다. mapping 귀속은 기존 S3 준비/검증 포괄126초와 M6 준비15.198568초이며 전체에 다시 더하지 않는다. cutoff 뒤 확인·보고는 다음 정산에1회 반영한다.

새 검사 process group 모두 종료, M6 task p.sock 삭제, active 경로 이동0. 새 고유 runner/입력/원문/결과와 이전 실패·복구 근거를 보존한다. offline/control canary와 worker outside/alias fixture는 원문 검증 및 필요한 다음 offline 입력의 소비자가 있어 해당 gate 처분까지 유지한다. broad cleanup·worktree 삭제·commit/push/merge/release·Work Done0이다. 결과/결정 packet: integrated-execution/goal-continuation-01/coverage-and-decisions.json. M6 exact 원문: fd01/m6-independent-01/result.json.


### Mapping Accounting Clarification — 2026-10-23T09:10:00.401104+00:00

앞선 mapping126초 포괄구간은 정확한 시작 근거가 충분하지 않아 그대로 사용하지 않는다. 확인 가능한 Goal 시작 2026-10-23T08:49:57.344428+00:00부터 M6 종료 2026-10-23T08:57:20.399796+00:00까지 전체 443.055368초를 보수적으로 mapping에 귀속했다. 이는 순수 mapping 작업만의 실측이라는 뜻이 아니며 전체/S3에 이미 포함된 시간을 다시 더하지 않았다. 기존 귀속 141.198568초 대비 301.856800초를 mapping에서 추가 차감했다. 원 기록/정산 원문은 보존하고 정정 근거를 goal-continuation-01/mapping-accounting-correction.json에 남겼다. 현재 전체 571.479842/960분, 미확정·전역 종료 예약 후 작업 가용 354.217821분, mapping 12.615744분이다. cutoff 이후 최종 확인/보고는 다음 정산에 반영한다.


## Approved Directions And Prospective Verification — 2026-10-23

Owner가 M5 미래 OS 차단 기준, 시간 복구 예외 방향, C-FD 통합 후보 방향을 승인했다. 과거 FAIL/UNAVAILABLE/H05/H10은 유지한다. 시간 복구와 C-FD는 exact 변경 범위·검증·rollback을 먼저 구체화하며 방향 승인만으로 전체 구현을 시작하지 않는다. 기존 원문과 제품 source는 현재 그대로다.

M5 새 시도는 기존 binary/profile 그대로 IPv4·IPv6 fresh FD의 정상 fdWRITE/fdSEND echo drain, 전후 exact A peer, RETARGET 결과를 확인한다. EISCONN 또는 A에만 8byte 전송한 분기를 유지하고, 새 OS 분기는 -1/EPERM과 command 시간·PID·network-outbound·exact B endpoint 직접 로그가 모두 필요하다. B 정상 대조·동기화된 사후 barrier와 신규 예상 외 bytes0을 확인한다. M4/M6는 재실행하지 않고 유효 근거를 재사용한다. 실행180초/stream180초/직접 로그 관측5초/출력256KiB 그대로이며 첫 non-pass에서 해당 실행을 중단·보존한다. profile/OS/제품/인증/모델 변경0이다.

미정산 181.199817초를 1회 반영하고 2026-10-23T09:13:01.600921+00:00–2026-10-23T10:37:54.068117+00:00 Owner 대기를 제외했다. 2026-10-23T10:41:34.386618+00:00 기준 전체 578.171814/960분, 미확정858.140222초·종료1200초 예약 후 가용 347.525849분. 이후 배분 S3 45/S4 45/S5 140/S6 85/S7 30분, 미배분 2.525849분. mapping30분은 S3 안의 부분 한도이며 추가 전체 예산이 아니다. M5 예상4–7분, 상세 설계15–25분은 판단치다. 실제 통합/복구 구현 비용은 정확한 범위 확정 후 별도 산정한다.


### M5 Matcher Correction Before Attempt 02

M5-os-01은 IPv4 EPERM 뒤 matcher가 literal IP를 요구하여 UNAVAILABLE로 중단했다. raw OS 로그는 해당 PID/명령 시각의 network-outbound remote:*:52560이다. 기존 M4/IP 및 sendto 기준은 wildcard 주소를 IP 독립 증거로 주장하지 않고 고정 syscall 목적지·PID·시각·operation·고유 포트를 결합했다. 새 runner의 추가 literal-IP 요구를 그 기존 의미에 맞게 보정한다. IPv4 B52560/IPv6 B52561이 구분되고 native 고정 binary의 목적지를 유지한다. 새 OS 분기의 EPERM·직접 로그·same-FD positive·전후 A peer·B 정상대조/사후 barrier는 그대로다. 원 M5 FAIL 및 os-01 UNAVAILABLE를 변경하지 않는다. 다음 fresh 시도의 변경은 matcher1줄과 시도 identity뿐이며 profile/권한/시간 한도는 동일하다. wildcard IP의 직접 관측은 여전히 unavailable이다.


## Exact Clock Recovery And C-FD Integration Proposal — 2026-10-23

### Decision And Authority

Owner의 세 방향 승인 뒤 M5 새 기준 검증을 진행했다. 시간 복구와 C-FD는 아래 exact 구조/파일/검증/rollback을 먼저 고정한 구현 제안이다. 기존 장부나 제품 source를 아직 바꾸지 않았다. 방향 채택을 전체 구현 승인으로 해석하지 않는다는 직전 경계를 유지한다. 새 발견은 reqwest 0.12.28 unix_socket()이 proxy 옵션을 무시한다는 점이다. 단순 UDS 설정 변경으로 기존 CONNECT를 유지할 수 없다. 따라서 아래 prepared 전용 HTTP transport 추가와 budget v2 carry 계약은 구현 전 Owner가 확인할 구체 delta다. TLS 검증/CONNECT/격리 기준을 줄이는 선택은 제안하지 않는다.

### Shape

```text
Host controller ── journal reserve / exact frozen target connect ── TCP FD
       │                                            │ SCM_RIGHTS
       ├─ inherited private broker control FD ──────┘
       └─ shutdown retained duplicate on stop/revoke

Prepared runtime ── exact UDS ── existing Rama CONNECT handler / proxy
                   CONNECT → TLS over same tunnel → original endpoint
                   runtime/proxy new IP sockets denied
```

C-FD는 controller가 이미 연결한 TCP socket만 proxy에 전달하는 방식이다. worker에는 새 권한을 주지 않는다. public target TCP443 연결 권한은 기존 승인된 controller 경계에 머물며, proxy/runtime은 새 IP socket·DNS·임의 UDS 경로를 열 수 없다. UDS 경로는 task 전용으로 고정하고 controller가 먼저 listener를 만들어 상속한다. 같은 UID라는 사실만 인증 근거로 삼지 않는다. 현재 역할의 PID/시작·candidate/spec·journal reservation·일회 nonce 및 inherited channel identity를 함께 결속하며 지원 밖 OS는 fail-closed다.

### Clock Recovery Contract

1. 원 budget/anchor.json·journal.jsonl·append.lock·controller.lock 및 checkpoint를 byte/hash 그대로 보존한다. 누적 사용량이나 build/correction/start/turn/send/review 카운터를 초기화하지 않는다. 원 journal의 마지막 seq/hash와 보존 사본의 byte 일치를 고정한다.
2. 새 immutable epoch 디렉터리 budget-epoch-02를 만든다. anchor v2에는 predecessor의 exact 경로/hash/last seq, 이전 approval/work/source/candidate/input identity, 새 후보 identity와 승인된 transition, 누적 활동 carry, 상한57600초, 미확정858.140222초·종료1200초, 새 wall/monotonic 원점을 명시한다. 날짜/최신 파일명으로 선택하지 않고 runtime spec이 exact anchor hash를 지정한다.
3. predecessor는 clock 경과 계산만 분리한 구조 검증으로 hash chain·event 순서·카운터·pending/stop/paused 상태를 재구성한다. 이는 일반 Budget.read의 guard 우회가 아니다. 복구 전용 경로만 controller lock+append lock을 획득하고, 살아 있는 controller/runtime/proxy가 없고 event/lock identity가 불변일 때 사용할 수 있다. runtime에는 복구 쓰기 API를 주지 않는다.
4. 외부 execution.json의 검증된 누적 활동을 carry의 하한으로 사용하고, 기존 runtime journal의 누적 계산보다 작으면 거절한다. 원 pause4 전체를 Owner 대기로 처리하지 않는다. 실제 승인/보고 timestamp로 확인된 Owner 대기만 제외하고, 아직 미정산이거나 미확정인 시간은 제외하지 않는다. 전체 경과시간22094초를 활동량이라고 단정하지 않는다.
5. v2 genesis는 predecessor를 참조하는 연속 장부 시작이다. 유효 카운터·동작 ID/replay set·pending/seal/stop 상태는 predecessor를 재생한 값에서 이어진다. stop이나 pending이 있으면 이를 clock 복구만으로 해제하지 않는다. H05 원 ticket replay는 별도 exact 승인 경계다. 현재 입력이 교체되는 source/candidate/spec 전환은 기존 승인 경로와 신규 transition hash로 명시하고 이전 입력을 새 입력처럼 표시하지 않는다.
6. 새 epoch 안에서도 wall/monotonic 차이2초 guard와 역행/초과 검사를 유지한다. old/new Python·Rust가 같은 fixture에서 같은 누적량·카운터·거절을 내야 한다. 한쪽만 v2를 지원하거나 predecessor/carry/spec이 다르면 runtime 시작을 거절한다. budget v1 정상 경로는 유지한다.

| Clock File Boundary | Exact Change |
| --- | --- |
| Colvia docs/development/verification/u2-host/host.py | Budget v2 reader, predecessor structural replay, explicit recovery prepare/apply, carry/lock invariants; 기존 live effect gate 유지 |
| Colvia tests/test_u2_host.py | v1 regression 및 v2 carry/손상/경쟁/pending/동일복구재사용 거절 direct tests |
| Codex codex-rs/app-server/src/lib.rs | Spec exact epoch binding, v2 validator/count inheritance/2초 guard, 직접 대응 Rust tests |
| Codex codex-rs/app-server/src/bin/prepared_tool_plan_fixture.rs | 외부 효과 없는 동일 fixture의 Python/Rust 판정 비교 entry만 추가 |
| 기존 task integrated-execution/goal-continuation-02/clock-recovery/ | 원 장부 보존·정산 manifest·schema fixtures·검사 원문; 실제 epoch 생성은 검증 뒤 새 exact path |
| 기존 Work 및 u2-host/README.md | current v2 적용/재개/회수 방법과 한계. 과거 기록은 보존 |

### C-FD Implementation Boundary

단순 reqwest unix_socket 옵션은 제외한다. 현재 reqwest connector_layer의 Conn 생성/URI 내부는 public 구현 경계가 아니므로 이를 private API에 의존해 우회하지 않는다. 제안은 prepared-live 모드에만 UDS→CONNECT→TLS를 수행하는 별도 transport를 추가하고, 기존 최종 request bytes guard·send 예약과 streaming response 변환을 그 전후에 유지하는 것이다. 일반 HTTP 경로·auth storage·model/fallback·Core authority는 바꾸지 않는다. reqwest vendoring/버전 변경/registry 수정은 포함하지 않는다.

| C-FD File Boundary | Exact Change |
| --- | --- |
| Codex codex-rs/http-client/src/prepared_uds.rs (new) | 고정 UDS 연결, 엄격한 CONNECT response 한도/검증, 동일 tunnel TLS, 기존 요청 bytes·header/stream 응답 adapter. redirect/retry/fallback0 |
| Codex codex-rs/http-client/src/client.rs, lib.rs | prepared-only backend 선택/노출, 기존 guard·durable generation/control 예약과 결속. 일반 constructor 경로 그대로 |
| Codex codex-rs/http-client/Cargo.toml, codex-rs/Cargo.lock | 이미 lock된 hyper/hyper-util/http-body-util/tokio-rustls 의존성의 해당 crate 선언만. 새 버전/다운로드 불가이면 중단 |
| Codex codex-rs/http-client/src/prepared_uds_tests.rs (new) | CONNECT/TLS/body/header/stream/취소/재시도0 및 ordinary regression |
| Codex codex-rs/network-proxy/src/prepared_fd.rs (new), lib.rs | macOS prepared-only inherited UDS listener/broker entry; SCM_RIGHTS 단일FD·type/peer/metadata·truncation 검증과 오류 시 FD 닫기 |
| Codex codex-rs/network-proxy/src/http_proxy.rs, attribution.rs | 기존 Rama CONNECT/policy handler를 UDS 입력에 적용. 현재 TCP peek/extension attribution의 UDS 대응. TCP/SOCKS 기존 경로 그대로 |
| Codex codex-rs/network-proxy/src/connect_policy.rs, state.rs | frozen prepared target만 controller FD로 취득. prepared에서는 DNS/TcpStream::connect/upstream proxy fallback 금지. 일반 target policy는 그대로 |
| Codex codex-rs/network-proxy/src/prepared_fd_tests.rs (new) | broker/target/FD/UID-PID binding·reuse·revoke·death·leak·CONNECT malformed negative |
| Codex codex-rs/app-server/src/lib.rs | 앞의 clock 변경과 같은 후보에 prepared UDS/broker/spec/role admission 결속; 기존 proxy lifetime·slot2 제한 유지 |
| Colvia docs/development/verification/u2-host/host.py, tests/test_u2_host.py | controller 대상 고정·connect-before-transfer·reserve-before-effect·FD lease/회수/프로세스 종료; clock 변경과 통합 검사 |
| 기존 task integrated-execution/goal-continuation-02/cfd-integration/ | 새 materialize-roles 파생본, exact runtime/proxy SBPL과 manifest, synthetic broker inputs와 raw 결과. 기존 채택 template/script/profile은 덮어쓰지 않음 |
| 기존 Work 및 u2-host/README.md | 실제 관측/선택한 profile·candidate/spec만 current 설명에 반영 |

위 파일 밖의 dependency API나 TLS backend 전환이 필요하면 구현 전에 새 delta로 보고한다. 기존 TLS root/hostname/SNI 검증과 native auth read-only 경로를 동등하게 유지할 수 있는지 먼저 offline fixture로 검증한다. 검증 불가를 fallback이나 certificate 검증 해제로 메우지 않는다. 다른 model·새 network permission·global 설정·설치본/managed runtime·권한 Core/제품 공개는 제외한다.

### Verification And Evidence Reuse

- Clock: predecessor byte/hash/chain 손상·torn record·seq rollback·낮은 carry·새 cap 증가·누락 카운터·pending/stop 해제·wrong work/candidate/input·concurrent writer·복구 재사용·2초 초과/역행을 거절. 승인된 carry의 정상 재개·카운터 증가·상한 도달·재중단을 Python/Rust 같은 fixtures로 비교한다. 이전 장부는 검사 뒤에도 동일하다.
- Transport: 합성 server로 UDS CONNECT→TLS→요청/stream을 실제 수행한다. 잘못된 CONNECT host/port/상태·duplicate Host·header injection·truncated response·다른 인증서/hostname·wrong broker nonce/FD count/type/peer·SCM truncation·예상 외 FD·proxy/controller death·revoke를 거절한다. URL/SNI/Host/Authorization/body identity와 reservation-before-send, redirect/retry/reconnect/fallback0, partial stream/취소/timeout 정리를 관측한다. credential 본문을 로그에 남기지 않는다.
- OS: 통합한 실제 Rust runtime/proxy에 대해 UDS 정상 교환 및 runtime/proxy IP/DNS/다른 UDS 차단, peer 고정, explicit shutdown 이후 새 bytes0을 검사한다. 기존 C canary M2–M6는 설계 선행 근거로 재사용하되 실제 Rust 통합 검사를 대신하지 않는다. worker/verifier/offline profile이 byte 동일하면 기존6+14 검사 결과를 재사용한다.
- 범위 검사 뒤 필수 offline8/ordinary smoke와 S4 actual host matrix로 진행한다. H05는 exact packet 없이는 실행/승격하지 않는다. 최종 source가 안정된 후 S5 normal/O 각각1회를 실행한다. clock source가 Core 전체를 바꾸지는 않지만 Colvia host regression/상호작용과 기존 acceptance requirement 때문에 이 최종 pair는 면제하지 않는다.
- H10은 실제5문서 exact 대상·read/provider 전달·intent/grant/refs/commit 승인과 Owner 부담 관측이 남는다. 새 구조 승인에 이 권한을 묶지 않는다. S7 R1은 통합 증거를 모은 뒤 기존 bounded transmission 권한에서 수행한다. 현재 H 상태를 승격하지 않는다.

### Rollback And Counter Boundary

구현 전 현재 source tracked diff·untracked bytes와 metadata, candidate3 binaries, 두 원 budget 파일과 controller lock identity, role inputs를 task 소유 경로에 보존하고 byte 비교한다. 기존 task의 이미 보존된 원본을 우선 재사용한다. 변경은 이 patch만 별도 diff로 관리한다. 실패 시 현재 실행을 중단하고 FD shutdown/프로세스 종료·socket/파일 ownership을 확인한 뒤 이 patch만 역적용한다. reset --hard/clean 또는 타 작업 변경 삭제는 하지 않는다.

rollback은 코드와 새 candidate 선택을 이전 값으로 되돌리는 작업이다. 이미 소비한 시간·build/correction/start/turn/send 카운터와 새 실패/장부를 되돌리지 않는다. v2 epoch가 효과를 기록했다면 과거 budget v1로 실행을 재개하지 않는다. 원 clock/profile 문제가 남으므로 이전 candidate로 돌아갔다고 live 실행 가능으로 표시하지 않는다. 새 epoch/candidate/고유 raw는 복구 또는 수락 검토 소비자가 있어 해당 처분까지 보존한다.

현재 candidate build2/3·제품 correction1/2가 소비됐다. clock+C-FD를 한 correction 후보로 모으고 focused test compile을 활용한 뒤 마지막 candidate build1회를 사용한다. test compile 시간도 전체 장부에 포함한다. 실패하면 같은 조건을 맹목 재실행하지 않고 분석하지만 build/correction 총량을 자동 증가시키지 않는다. M5 task runner matcher 보정은 제품 source/candidate 변경이 아니며 이 제품 카운터를 변경하지 않았다.

### Forecast And Next Owner Boundary

남은 구현·검증 예상은 clock20–35분 + C-FD55–90분 + 통합 focused/build/OS15–25분 =90–150분(판단치)이다. 마지막 warm build30.49초는 참고 실측이지만 이번 transport/의존성 변경 비용을 대표하지 않는다. S4 45–70분, S5 125–145분(이전 pair117.53분 참고), S6 60–90분, S7 30–45분을 합치면 남은 전체350–500분이다. Owner 대기는 제외하고 독립 작업/검사 중첩은 한 번만 센다. 추가 구조가 확인되어 이전의 조건부 예상보다 증가했다. 현재 약340분의 예약 제외 가용량보다 낮은 예상도 크므로 전체 완료를 약속할 수 없다. 요구/검사 축소나 전체16시간 증액을 제안하지 않는다.

다음 Owner 확인은 이 구체 budget-v2 carry와 prepared-only UDS CONNECT/TLS transport의 구현 범위다. 범위 승인 뒤에는 전체 잔여 안에서 단계 예산을 다시 배분하고, 먼저 이 기반 변경의 focused 결과와 통합 실행 가능성을 확보한다. 16시간·기존 예약 및 카운터 상한은 그대로이며 소진 시 미완료 항목을 보존·보고한다. 이 범위 결정 전 제품 source/장부를 쓰거나 최종 full pair를 소모하지 않는다.


### Prospective M5 Result And Current Accounting

M5-os-02 IPv4/IPv6 모두 OS_DENIAL 분기로 PARTIAL_M5_PROSPECTIVE_PASS다. 같은 FD 정상 사용/echo drain·전후 A peer·EPERM·직접 PID/명령 시각/network-outbound/고유 B 포트 로그·A EOF와 B barrier의 예상 외 bytes0을 확인했다. wildcard 주소 자체를 정확한 IP 로그 증거로 주장하지 않는다. M5-os-01 UNAVAILABLE와 원 M5 FAIL/전체 UNAVAILABLE/H05/H10은 보존한다. process/socket cleanup PASS, 제품/source/profile/OS/auth/model 변경0이다.

2026-10-23T10:51:01.752491+00:00 정산: 전체 587.627911/960분, 예약 제외 가용 338.069752분. 이번 전체 포괄 구간787.684374초를 mapping에 보수적으로 귀속했고 전체/S3에 다시 더하지 않았다. cutoff 이후 확인·보고 시간은 다음 정산에1회 반영한다.


### Final Scope-Preparation Verification

2026-10-23T10:52:45.387021+00:00 기준 source는 s3-build-02 exact HEAD/diff/untracked/lock와 일치하고 host source·candidate3 binaries·H 상태/제품 카운터·runtime journal metadata는 불변이다. 오래된 implemented_files의 lib.rs hash는 비교 기준에서 제외하고 실제 S3 build 입력을 사용했다. 새 두 시도 process group 종료와 보호 원문 hash, diff-check를 확인했다. 현재 전체 589.355154/960분, 예약 제외 가용 336.342509분. 이후 최종 보고 시간은 다음 정산에서1회 반영한다. 정확한 검증 원문은 goal-continuation-02/final-verification.json이다. 새 고유 입력/원문/제안과 직전 Work/장부 사본은 Owner 범위 결정·최종 검증을 위해 유지한다. task p.sock만 ownership 확인 후 제거됐고 active 경로 변경·제품/source/OS 변경·Git publication·Work Done은0이다. 앱 Goal은 재개 요청 뒤에도 paused이며 업무 승인과 앱 상태를 구분한다.


## Exact Scope Implementation Authorization — 2026-10-23

Owner 메시지617072585가 직전 budget-v2 carry와 prepared UDS CONNECT/TLS transport의 exact 범위·검증·rollback 구현을 승인했다. 전체16시간·예약·카운터·과거 판단은 유지하고 작은 단계별 승인 없이 진행한다. source/원 장부의 선택 파일 bytes와 metadata·기존 diff/status를 goal-implementation-03/recovery에 보존·byte 검증했다. 미정산 113.071667초를1회 반영하고 Owner 대기를 제외했다. 2026-10-23T10:57:04.260068+00:00 기준 전체 593.233870/960분. 잔여 배분 S3 100/S4 45/S5 125/S6 40/S7 20분과 미배분 2.463793분은 전체 가용 안이다. 이는 완료 예상이 아니라 정지/재배분 경계이며 기존350–500분 예상과 구분한다. 한정 단계가 미완료이면 상한 안에서 배분을 다시 확인하고 검사/수락 기준을 축소하지 않는다. 새 correction1개에 clock+C-FD를 함께 묶고 focused 검증 뒤 마지막 candidate build1회를 사용한다.


## 구현 중간 체크포인트 — 2026-10-23

Owner의 exact scope 승인에 따라 clock-v2와 C-FD 통합 source를 수정 중이다. native TLS 의존성은 별도 승인된 기존 native backend로 유지했다. 합성 정상 TLS는 SecurityServer 단일 Mach lookup이 없을 때 실패했고, 직접 deny 관측 후 조건부 승인한 한 항목을 추가하자 통과했다. 같은 프로파일에서 CONNECT 거부·인증서 불신 거부·응답 취소도 통과했다. 실제 runtime 프로파일 적용과 실제 인증·provider 실행은 아직 하지 않았다.

FD의 실제 loopback TCP 전달·peer·CLOEXEC·controller shutdown 검사는 통과했다. 잘린 SCM_RIGHTS 반환 시험에서 일부 FD가 닫히지 않는 문제를 관측했으며 아직 해결 판정하지 않는다. Python의 새 clock/controller 검사는 통과했으나 기존 자식 process 종료 시험은 EPERM으로 unavailable이며 PID66081 부재를 별도로 확인했다. 이 시험 묶음 전체를 PASS로 기록하지 않는다.

누적 활동 639.45분, 불확실성·종료 예비 제외 잔여 286.25분, 현 S3 배정 잔여 53.78분이다. 병행한 Owner 응답 대기는 별도 공제하지 않았다. 최종 candidate build는 아직 쓰지 않았으며 실제 role 연결·공통 clock fixture·필수 통합/normal-O 회귀·R1이 남는다. 실행 evidence는 private task의 goal-implementation-03/focused-checkpoint.json과 logs에 보존한다.


## 2026-10-23 Final Candidate S3 Checkpoint

마지막 candidate build3/3와 source 불변 확인을 마쳤다. 최종 binary에서 offline8/8, ordinary initialize/config, clock 공통17사례 parity가 통과했다. 파생 runtime OS15개와 인증 전 bootstrap, Rust runtime UDS/native TLS 및 proxy FD IPv4/IPv6 경계, 승인된 S5 검사 프로파일의 host12개도 통과했다. 기존 byte 동일 offline canary6와 worker/verifier negative14 및 변경 없는 auth/keyring/cloud/model 집중 근거를 재사용한다. 실제 App Server/provider 전체 연결과 native 계정/정책/model 성공은 아직 확인하지 않았으며 S4가 판정한다.

새 clock epoch는 실제 누적674.110083분을 carry했고 build3/correction2 및 원 장부 bytes를 보존했다. 2026-10-23T12:28:22.302975+00:00 기준 전체 684.53/960분, 예약 제외 가용 241.16분이다. S4 배분45분은 중단 경계이며 S5 125/S6 40/S7 20분 배분과 전체 예약은 유지한다. H05/H10 및 과거 FAIL/UNAVAILABLE는 그대로다.

Owner가 S5 task 한정 UDS 파생 프로파일과 중복 예약 차감 보정을 승인했다. cf5n/cf5o 아래 검사 파일·UDS만 허용하며 IP/DNS/Mach 및 제품 역할 권한은 추가하지 않았다. 첫 집중 검사 입력 수집은 이 작업의 재생성 bytecode 디렉터리 때문에 실행 전에 중단됐다. 원본·timestamp/size·열린 소비자 부재 확인 후 그 bytecode만 삭제했고, 동일 oracle 재실행12/12 및 격리 canary가 통과했다. full 실행은 아직0회다. 고유 입력/실패/검증 원문과 이전 후보3 binaries는 R1/결과 수락 소비자 때문에 유지한다. 실제 runtime 경로 변경과 Git publication/Work Done은0이다.


## 2026-10-23 S4 Initialization Failure And Independent S5

실제 clock runtime1회는 native 인증 초기화 전에 invalid fixture directory로 종료됐다. stderr 원문은 credential 보호 계약에 따라 저장하지 않았지만 33bytes/hash가 이 정적 오류 문자열과 정확히 일치한다. source initialize_live가 요구하는 home/cwd/config 중 task materializer가 config 디렉터리를 만들지 않았음을 확인했다. home은 비어 있으며 control/generation/thread/turn 예약0, 실제 인증 내용 접근0이다. 이 관측을 TLS/provider 성공이나 계정 실패로 해석하지 않는다.

runtime/proxy 종료와 FD leases0을 확인했다. journal stop 및 build3/3·보정2/2를 유지하고 config 추가·장부 해제·clock 재시도를 하지 않았다. S4 합성 live·H05/H10은 미완료다. 수정 없이 안정된 Colvia/host source의 필수 최종 normal/O 회귀는 이 실패와 독립적으로 진행한다. 집중12개만으로 전체 Core/host 상호작용과 기존 최종 회귀 요구를 대체할 수 없어 full 각각1회를 유지한다. 실행 전 discovery를 고정하고 source/oracle/profile 변경·skip 없이 확인한다. 예상125–145분은 기존117.53분 근거와 판단 여유이며 배분125분은 정지 경계다. 전체 예약과 per-mode6300초/pair10800초도 유지한다.


## Owner Travel Pause — 2026-10-23

Owner 요청에 따라 S5 normal 회귀를 SIGTERM으로 중단했다. worker process group19949와 runner19948의 부재를 확인했으며 강제 종료는 사용하지 않았다. 전체706개 중318개는 stop event까지 기록됐고1개는 실행 도중 중단,387개는 미실행이다. normal 결과는 INTERRUPTED이며 PASS/완료가 아니다. optimized는 미실행이다. 정확한 목록과 원문은 기존 private task의 goal-implementation-03/travel-pause-20261023/regression-disposition.json 및 full-normal에 보존한다.

최종 후보 build3/3·correction2/2, offline start10, live start1, proxy start1, thread/turn/generation/control/auth-read0, R0 1/R1 0을 유지한다. 완료된 S3 근거는 s3-final-gate.json을 재사용한다. S4의 config 디렉터리 누락에 따른 인증 전 초기화 실패와 journal stop은 그대로이며, S4 live/H05·S6 H10·S7 R1은 미완료다. discovery706은 기존 제안701보다5개 많다. 승인된 clock/controller4개 외 기존 view observation1개의 이전 목록과의 차이는 재개 시 읽기 전용으로 대조할 항목이다. suite나 oracle을 변경하지 않았다.

현재 누적 활동707.496/960분, 총 잔여252.504분, 불확실성14.302분과 종료20분을 제외한 가용218.201분이다. 마지막 보존 확인/보고까지의 활동은 최종 checkpoint cutoff에1회 추가 정산한다. 이동 시간은 그 cutoff부터 명시적 재개 요청까지 제외한다. 시간과 횟수를 초기화하지 않으며 과거 absolute deadline을 그대로 사용하지 않는다. 재개 때 남은 전체·S5·pair 활동량에서 새 deadline을 계산하고 예약을 유지한다. runtime의 기존 stop은 해제하지 않는다. sleep에 따른 clock drift는2초 guard를 완화하지 않고 exact recovery 권한을 먼저 확인한다.

현재 실행기는 중간 재개 기능이 없다. full normal 수락 근거가 필요하면 첫 검사부터 새 실행이 필요하며, 기존 normal1회 소비 기록을 보존한 상태에서 Owner의1회 제한 예외 승인이 필요하다. 남은 suffix만 실행해 full PASS로 합치지 않는다. optimized의 미사용1회도 지금 시작하지 않는다. config 보정/live 재시도·stop 처분, H05/H10 별도 권한과 최종 수락은 이번 이동 요청에 포함되지 않는다.

재개 첫 확인은 checkpoint.json을 읽는 것이다. 원본 소스 변경64개는 byte 검증한 선택 복구본과 Git patch로 보존했고, 실행 입력/프로파일/로그/장부/후보293개 파일의 읽기와 hash를 확인했다. 원본·필수 복구 자료 삭제와 active path 변경은0이다. 파일 소비자는 재개·Owner 결정·R1·결과 수락이며 해당 처분까지 유지한다. Goal은 paused다.

First read-only command:

[공개용 중립화] 다음 code block의 식별 정보는 공개용으로 바꿨다.

```sh
cat private-evidence/E015
```

이후 순서: process 부재·source/입력/후보/장부 hash 확인 → 실제 재개 시각과 이동 제외 구간 정산 → 잔여 시간/횟수와 승인 경계 확인 → 필요한 normal 재실행 예외 및 live blocker 처분을 Owner에게 제시. 이 기록을 읽는 것만으로 새 검사·재실행·리뷰를 시작하지 않는다.


## Full Goal Resumption After Travel — 2026-10-23

Owner 메시지562784518은 기존 전체 Goal을 재개하고 이동으로 중단한 normal에만 추가1회를 승인했다. 기존 중단 실행1회와16.056분 runtime 및 준비/보존 시간을 그대로 남긴다. partial318+1+387을 다른 실행과 합쳐 full PASS로 만들지 않는다. optimized는 미실행 기본1회다. 소스·기존 selection 입력·프로파일·후보3 binaries·journal hash가 모두 중단 때와 같고 잔존 프로세스가 없다. discovery706의 추가5개는 승인 clock/controller4개와 현재 HEAD의 기존 view observation1개이며, 후자는 tracked clean이다.

전체 목표는 FEAT-20261022-001의 기존 승인 범위와 완료 기준을 실제 증거로 검증하고 최종 Owner 수락 자료를 준비하는 것이다. S0 계획/R0와 S1/S2 구현, S3 최종 candidate/범위 검사는 근거가 있으며 최종 수락은 아니다. H01–H10 및 실제5문서가 남은 전체 범위이고 M5 또는 회귀만으로 Goal을 완료하지 않는다. 현재 순서는 S5 normal 새 경로→optimized 최초 실행, 동시에 source/evidence 기반 S4·H05/H10 선행조건 정리→결정이 확보된 범위의 후속 실행→S7 bounded R1→Owner 수락 보고다. 실제 auth/provider 성공과 S4 live/H05, S6 H10, S7 R1은 아직 미완료다.

이동 제외는12:51:58.220355UTC부터13:46:31.280264UTC까지다. 재개 후 준비·실행·보고는 전체에1회 계상한다. 앱 Goal은 paused이고145476 tokens/1267seconds 값은 앱 자체 지표다. 실행 장부의16시간·누적708.133분과 다르며 앱 Goal을 삭제/완료/재생성하지 않았다. 도구로 resume/edit할 수 없어 Owner는 현재 채팅 Goal 진행 행의 Resume을 사용한다. 목표 문구는 원문 그대로 보존한다.

회귀 예상125–145분은 과거 pair117.53분을 참고한 판단이며 current 후보의 실측 완료시간이 아니다. 재개 시 총251.867분, 불확실성14.302분·종료20분을 뺀217.564분 안에 회귀와 예약이 들어간다. 기존 S5 잔여103.940분은 부족해 승인된 전체 내 재배분으로 S3/S4 미사용분을 옮겨 S5에150분을 배정한다. 누적 pair180분 중 중단/보존까지20.624분을 이미 사용했으므로 재개 준비 포함159.376분의 기존 pair잔여도 적용하며 mode6300초/전체16시간 중 먼저 오는 상한을 지킨다. 모든 남은 live/H10/R1까지 완료할 시간은 보장하지 않는다.

Task runner는 source/test/profile을 바꾸지 않고 normal 예외1회·새 output/canary 경로·이동 제외 deadline만 파생했다. exact delta와 입력은 private task goal-resume-04에 보존한다. 제품 build3/3·correction2/2, 기존 stopped journal, H05/H10 실제 입력/권한·Git publication 경계는 그대로다. S4 materializer의 config 누락 보정과 새 live slot/stop 처분은 별도 권한 판단을 묶어서 제시한다. 이미 승인된 독립 회귀와 증거 정리는 계속한다.


### Resumed Completion Evidence And Dependencies

| Criterion | Valid Evidence | Remaining |
| --- | --- | --- |
| H01 | S1/S2 focused protocol and admission guards; same candidate offline8 | Actual integrated host foreign thread/turn/call, Owner spoof, grant/home/action/scope matrix |
| H02 | Prepared primitives, final-byte guards, offline8, focused host input/ticket negatives | Actual integrated host ticket/bytes/result replacement and duplicate rejection with control invariance |
| H03 | Worker/verifier14 and offline6, final runtime OS15/bootstrap and Rust UDS/nativeTLS/FD IPv4/IPv6 helper boundaries | Full integrated candidate/provider flow; actual H10 target boundary immediately before use |
| H04 | Existing Core grant contract evidence; focused host acceptance primitive | Actual host + unwrapped installed CLI accept once, used/revoked/other Work/action rejection |
| H05 | Preserved recovery contract and focused negatives; no exact replay receipt | Synthetic S0-S5 actual process death/pending packet, then Owner exact original actor/decision/ticket approval and replay |
| H06 | Focused verifier/worker guards and fixed verifier OS positives/negatives | Actual host same-Work fixed verifier fail -> allowed correction -> pass; natural H10 observation separately |
| H07 | Shared Python/Rust17 clock fixtures, actual carried epoch, preserved counters, movement resume accounting | Actual host Work/context/results/pending resume and corruption/drift refusal; stopped epoch not resumable |
| H08 | Focused guards, actual stop/preservation, Owner travel interruption and one-shot exception | Actual host scope/new ticket/revoke/limit/repeat/post-submit matrix |
| H09 | Existing Driver documentary cases in Work H09 Documentary Cases, goal-continuation-01/coverage-and-decisions.json | R1/Owner assessment; no independent user or production efficiency claim |
| H10 | Original five-document scope and quality/effort criteria only; actual target content access0 | Host qualification, exact actual target/read/provider/intent/grant/refs and candidate commit approval, five-doc content/scope/evidence and Owner effort observations |

위 표는 기존 근거의 소비 위치를 갱신한 것이며 historical FAIL/UNAVAILABLE나 H05/H10을 승격하지 않는다. H09의 기존3사례와680440bytes R1 초안을 재사용하며 원 입력50여 개의 hash drift0을 확인했다. R1은 아직 전송0회다. 실제 소스/검사/프로파일은 회귀 중 고정한다.

S4에는 config 누락 외에 stopped budget을 해제하는 명시적 계약과 S4 proxy 재시작 배정 문제가 있다. 기존 clock recovery는 stop을 보존하도록 설계됐고 남은 proxy slot은 S6용이다. 따라서 config만 만들거나 새 epoch/남은 slot을 임의 사용해 재실행하지 않는다. build3/3·correction2/2도 소진되어 source/빌드/배정 변경이 필요하면 R1 findings와 함께 최소 범위를 Owner에게 제시한다. H05는 exact 원 ticket packet이 아직 없어 replay를 일괄 승인받지 않으며 H10 실제 자료도 아직 읽지 않는다.

잔여 회귀125–145분 + 별도 권한 확보 뒤 S4 45–70분 + H10 60–90분 + R1/처분30–45분을 단순 합산하면260–350분이며, 새 복구 설계 비용은 포함하지 않은 판단값이다. R1 준비의 회귀 중첩은1회 계상하지만 live/H10 선행 관계는 병렬로 줄일 수 없다. 현재 예약 제외 가용보다 크므로 전체 완료를 보장하지 않고, 허용된 회귀·증거/R1을 진행하며 실제 제한과 필요한 결정을 모은다.


### Travel Replacement Normal Result

normal 추가1회가706/706 PASS로 종료됐다. failures/errors/skips/expected failures/unexpected successes0, exit0, process group 부재와 input drift0을 확인했다. 실행시간57.861분이며 원 중단 실행과 합산하지 않은 독립 full 결과다. 중단 실행1회 및 사용량은 그대로 남긴다. 다음은 기존 승인된 optimized 최초1회다. 현재 normal 실측과 이전 pair117.53분을 참고한 optimized 예상55–70분은 현 단계/pair/전체 중 먼저 오는 잔여88.105분 안에 들어가며 별도 종료/불확실성 예약은 유지한다. source·검사·프로파일은 불변이다. 전체 Goal의 S4/H05/H10 및 R1 미완료 상태는 그대로다.


### Resume 04 — Final S5 Pair And R1 Admission

일반/최적화 모드가 각각 동일한 706개 전체 검사를 통과했다. 실패·오류·skip·expected failure·unexpected success 모두 0이며 입력 drift 없음과 process group 소멸을 확인했다. 일반 모드 3471.653초, 최적화 모드 3382.126초다. 앞선 이동 중 중단 결과는 원문 그대로 보존하며 통과 결과에 합치지 않았다. parent `-O`는 기존 launcher child까지 `-O`라는 의미가 아니다. 실제 provider 통합/H01–H10 수락은 이 결과만으로 승격하지 않는다.

S5 미사용 예산에서 900초를 S7로 옮겨 R1 및 Driver 분류에 35분을 배정했다. 전체 16시간, 기존 미확정·종료 예약과 소모 카운터를 유지한다. 기존 승인된 1회 R1 전송을 진행하며 source/build 변경은 없다.

### Resume 04 — R1 Transmission Block And Preservation

확정 R1 자료는 704,235bytes, SHA-256 `c00ff53e67b452a758d51d4677b35a404bdf15143f154da374864705c8b4f894`다. 통합 source/계약/합성 근거와 final S5 결과를 담고 실제5문서·계정/credential·실제 target 경로는 제외했다. 자동 승인 검토가 payload/destination 권한 불충분을 이유로 호출 전 차단했다. 기존 Owner 직접 승인과 approved-plan 123행의 명시적 Claude 전송 범위를 확인해 제시했지만, 재요청도 신뢰된 승인으로 인정하지 않고 우회로 판단해 차단했다. 우회하지 않았으며 reviewer process/auth check/전송은 시작되지 않았고 R1_calls=0이다. 확정 자료의 Claude 전송1회에 한정한 Owner 확인을 요청했다. Reviewer 응답·판정은 아직 없다.

S4는 config 누락에 따른 인증 전 실패다. stop은 유지되며 build3/3·제품 보정2/2·S4 proxy1 소모를 되돌리지 않는다. stopped-run 재개 계약과 추가 보정/build/같은 단계 proxy 재시도는 기존 travel 예외로 승인되지 않는다. H05 exact packet은 미생성, H10 실제 대상 접근/전달/intent/grant/refs/commit과 최종 수락은 별도다. 전체 Goal을 회귀 검사 완료로 닫지 않는다.

보존 확인: runtime51+host13개 복구 원문 byte 일치, 현재 제품 입력과 후보3개 불변, 중단 journal 불변. 이동 중 중단된 원 실행과 새 normal/O 전체 결과를 각각 유지했다. Work current report만 갱신됐다. source/recovery/binaries/journal/test receipts/확정 R1 packet은 R1·Owner 결정·정확한 재개의 소비자가 있어 유지하며 그 종료 시 재평가한다. active 경로 변경0, 삭제0.

정산 시각 2026-10-23T15:50:04.127543+00:00 기준 누적 831.681분, 전체 잔여 128.319분이다. 미확정14.302분·종료20분을 보존한 가용량은 94.017분이다. 최종 보고 overhead는 다음 재개 때 실제 timestamp로 먼저 정산하고 그 뒤 Owner 대기만 제외한다. 추가 검토/구현/실행/전송 없이 대기한다.

### Integrated R1-01 — Request, Execution And Evidence Boundary

2026-10-24 06:22 KST Owner는 확정704,235bytes/SHA-256 `c00ff53e67b452a758d51d4677b35a404bdf15143f154da374864705c8b4f894` 자료의 Claude 외부 전송1회를 직접 승인했다. 앞선 자동 승인 검토 차단은 이 새 직접 승인 뒤 해소됐다. 기존 내용/목적지 범위를 그대로 사용했으며 실제5문서·계정/credential·실제 target 내용/경로는 제외했다.

실행: 기존 task의 `goal-implementation-03/scripts/run-integration-r1.py`를 Python3.14.7 `-I -S -B`로 실행했다. runtime source base는 `83086188ae0614bd882818ff1aa23f3194962012`, host base는 `7d012f5297de1d9a77aa0b8187406f4785221573`이며 미커밋 patch/신규 파일과 각 hash는 확정 request 및 metadata에 결속돼 있다. 60개 검토 입력의 전후 hash가 일치했다.

구독 인증은 `loggedIn=true, authMethod=claude.ai, apiProvider=firstParty, subscriptionType=pro`였다. 실제 model `claude-opus-5-5`, fresh session `a00726d1-0132-483f-8015-88a8f3929c14`, tools/MCP 없음, tool use0, 1turn. 880초 상한 내 483.654초에 exit0/end_turn으로 완료했고 stderr0, input drift0, process group 소멸을 확인했다. 결과 원문24,726bytes/SHA-256 `0550c9cc02b8a424b81f9e814ea0b8dbd442353ab0b94cee30293b8ffc6d612a`를 아래에 그대로 보존한다.

Reviewer는 전달 packet만 읽었고 실행/외부 조회는 하지 않았다. source/comment의 명령을 실행하지 않는 정적 검토다. 서로 다른 모델의 새 세션이지만 제공된 packet에 의존하므로 context 독립성에는 한계가 있다. Driver의 아래 추가 소스 대조와 공식 clock 자료 확인은 Reviewer가 수행한 검사나 추가 formal review가 아니다. 이번에 제품 테스트/build/live/auth/model을 새로 실행하지 않았다.

### Integrated R1-01 — Verbatim Reviewer Response

``````text
# Integrated Prepared Live + Document Host — R1 정적 검토 (Fresh Independent Reviewer)

## 0. 검토 범위와 판정 원칙

- 이 검토는 stdin으로 받은 patch, 신규 source, 계약 문서, 합성 evidence만 읽은 **정적 검토**입니다. 도구, 명령, 빌드, 테스트를 실행하지 않았고 외부 조회도 하지 않았습니다. 아래의 "Driver 실행 근거"는 packet에 기록된 Driver 측 결과를 인용한 것이며 Reviewer가 재현한 결과가 아닙니다.
- 현재 상태로 전제한 사항은 다음과 같습니다.
  - Work는 미완료입니다.
  - S4는 인증 초기화 전에 종료됐습니다.
  - 장부는 stop 상태이며 build 3/3, 보정 2/2를 소진했습니다.
  - H05와 H10은 not-qualified입니다.
- 이 검토로부터 다음 중 어느 것도 추론하지 않습니다: Owner 수락, H05/H10 완료, production qualification, 수정·재시도·재빌드 권한, Git publication.
- 아래의 "최소 보정"은 **제안**일 뿐입니다. 실행하려면 소진된 build/보정 장부와 stop 상태를 넘는 별도의 Owner 결정이 필요합니다.
- Known blocker와 이번에 새로 발견한 결함을 구분합니다. Known blocker는 materializer가 `config` 디렉터리를 만들지 않아 `validate_directories`에서 거절된 문제입니다. 핵심 결론은 이 blocker를 고쳐도 아래 F1–F6 때문에 live 경로가 다시 막힐 가능성이 높다는 것입니다.

---

## 1. 필수 Findings

### F1. [차단 · 확정적 정적 추론] U2 `thread/start`가 첫 번째 prepared gate에서 항상 거절됨

- **영향**
  - synthetic U2(H01–H09)와 H10의 thread가 시작되지 않습니다.
  - clock은 통과합니다.
  - host는 이 거절을 refusal로 처리하고 장부에 `stop`을 기록합니다(F4 참조).
- **Trigger**
  - `LiveSession.launch`는 dynamic tool이 있으면 `{"ephemeral": true, "dynamicTools": [...]}`를 보냅니다.
- **근거 symbol**
  - `MessageProcessor`의 첫 번째 prepared 검사가 `thread/start` params에 `object.len() == 1 && ephemeral == true`를 요구합니다(`safe_start`).
  - 이 첫 gate는 원래 fixture 전용이었고, live U2 경로에서도 그대로 적용됩니다.
  - 두 번째 gate인 `ClientRequest::ThreadStart`는 dynamic_tools를 포함한 정확한 비교를 이미 갖추고 있습니다. 그러나 첫 gate가 먼저 거절하므로 두 번째 gate에 도달하지 못합니다.
  - 기존 테스트에는 U2 params로 두 gate를 모두 통과하는 사례가 없습니다.
- **최소 보정 (제안)**
  - live U2 profile에서 첫 gate의 허용 key 집합을 `{ephemeral, dynamicTools}`로 바꿉니다.
  - 정확한 값 비교는 두 번째 gate에 맡깁니다.
  - U2 params가 두 gate를 모두 통과하고, 그 밖의 key는 거절되는지 확인하는 대응 테스트를 추가합니다.

### F2. [높음 · 조건부/경합] SSE 정상 완료 직후 body가 EOF 전에 drop되면 전역 latch가 걸려 gen2가 거절될 수 있음

- **영향**
  - 정상적인 gen1(tool call) 완료 뒤에 gen2 송신이 `unqualified prepared HTTP constructor`로 거절될 수 있습니다.
  - 그러면 clock live-smoke(dispatch 후 gen2)와 모든 U2 turn이 실패합니다.
- **Trigger**
  - `core/src/client.rs`의 live 분기에서 spawn된 task는 `ResponseEvent::Completed`를 받으면 `break`하고 `upstream`을 drop합니다.
  - codex-api parser가 body의 Ready(None)을 보기 전에 소비자가 drop되면 다음이 이어집니다.
    - `PreparedBody`/`ConnectionGuard::drop`이 `complete == false` 상태에서 실행되어 `failed=true`가 됩니다.
    - 이 플래그는 `PreparedHttpBoundary.failed`와 같은 Arc입니다.
    - 따라서 `execute_without_request_logging`이 이후 모든 요청을 거절합니다.
- **근거 symbol**
  - `prepared_uds.rs::{ConnectionGuard, PreparedBody::poll_next}`
  - `client.rs::install_prepared_http_guard`(동일한 `failed` 공유)
  - `prepared_uds_body_cancel_closes_connection_and_latches`: "EOF 전 drop이면 latch"가 의도된 동작임을 보여줍니다.
  - `live_native_sse_consumer_drop_releases_idle_response_body`: parser가 소비자 drop을 감지해 body를 놓는다는 것을 보여줍니다.
  - 이 두 동작이 결합되면 결과는 서버의 terminating chunk 도착 시점과 drop 시점의 경합에 의존합니다.
  - 실제 codex-api parser와 PreparedUds를 함께 써서 "completed 이후 두 번째 요청이 허용되는지"를 확인한 테스트는 없습니다. 기존 테스트는 전체 body 읽기와 drop만 다룹니다.
- **최소 보정 (제안)**
  - live 분기에서 Completed 이후에도 고정 시간·byte 상한 안에서 upstream을 None(EOF)까지 소비합니다.
  - 그 사이 추가 이벤트가 오면 오류로 처리합니다.
  - 실제 parser, PreparedUds, 합성 TLS 서버로 "gen1 정상 완료 후 gen2 허용"과 "실제 절단이면 latch"를 모두 검사합니다.

### F3. [높음 · 환경 의존 추론, uncertain] 실제 native user config의 MCP/plugin 항목이 `validate_startup`에서 거절될 가능성

- **영향**
  - config 디렉터리를 보정해도 다음 live start가 `unsupported startup configuration set`으로 종료될 수 있습니다.
  - 이 경우에도 start 1개가 소모되고 stop이 기록됩니다.
  - 인증 내용에 접근하기 전 단계이므로 credential 노출 위험은 없습니다.
- **Trigger**
  - `config_for_roots`는 `user_config_path = auth_home/config.toml`을 native로 로드합니다.
  - `mcp_servers`, `plugins`, `model_providers`, `notify`, `personality` 등은 덮어쓰지 않습니다.
- **근거**
  - 과거 preflight의 `EXPECTED_MCP = (openaiDeveloperDocs, node_repl, computer-use)`, `disabled_plugin_ids` 처리, fixture의 `config_response`를 보면 native config에 MCP와 plugin 항목이 존재했던 것으로 보입니다.
  - `prepared_live::validate_startup`과 `prepared::validate_config`는 이 집합이 비어 있지 않으면 거절합니다. `enabled=false` 여부는 고려하지 않습니다.
  - materializer의 `native_inventory`는 metadata만 확인하고 내용을 읽지 않으므로, 이 결과를 사전에 알 수 없습니다.
  - 실제 config 내용은 packet에 없으므로 이 항목은 추론입니다.
- **최소 보정 (제안, Owner 판단 필요)**
  - 다음 중 하나를 S4 재개 전에 결정합니다.
    - 인증 없이 config만 로드하는 정적 dry-run 판정 경로를 둡니다.
    - Owner 승인을 받은 CLI override로 해당 집합을 비우고, 비어 있음을 검증합니다.
  - 어느 쪽이든 정책 의미 변경이므로 자동 적용하지 않습니다.

### F4. [높음 · 계약 충돌] 어떤 start 실패든 Work 전체 `stop`으로 승격되고, stop은 epoch를 넘어 상속됨

- **영향**
  - 계약은 phase별 두 번째 start를 허용합니다(clock의 mandatory correction, H10 봉인 전 재시작). 그런데 run 1회 실패가 비가역적인 Work stop이 되어, 이 슬롯들에 실제로 도달할 수 없습니다.
  - S4가 정확히 이 경로를 밟았습니다: stop27, process-ended28.
- **근거 symbol**
  - `host.py::run_live_command`의 `except` 분기가 실패 종류와 무관하게 `budget.reserve("stop", ..., allow_closeout=True)`를 호출합니다. 이는 일시적 lock 경합(F7)을 포함한 모든 예외에 적용됩니다.
  - `Budget._validate`(Python)와 `validate_budget_rows`(Rust)는 stop 이후 `process-ended|checkpoint`만 허용합니다. 또 v2 lineage에서 `state.stopped`를 그대로 이어받습니다.
- **최소 보정 (제안, Owner 계약 결정 필요)**
  - start 수준 실패는 `process-ended`와 start 실패 기록으로 끝냅니다. 해당 start 슬롯은 소모로 둡니다.
  - Work 수준 stop은 Owner 중단, 상한, 불명확한 authority 효과, recovery 입력 손실에만 사용하도록 분리합니다.
  - 이미 기록된 stop27은 그대로 보존합니다. 재개에는 별도의 명시적 계약이 필요하며, 이는 R04-LIVE와 같은 경계입니다.

### F5. [높음 · 정적 추론] 2초 wall/monotonic guard가 sleep 중 멈추는 clock을 써서 시스템 sleep 한 번에 장부 전체가 거절 상태가 됨

- **영향**
  - 장시간 실행이나 Owner 대기(봉인 후 idle, 이동 중단) 중 macOS가 sleep하면, 이후 모든 `reserve`, `read`, `resume`이 `activity clock drift`로 거절됩니다.
  - acceptance, resume, recovery가 모두 불가능해집니다.
  - 복구하려면 다시 Owner 승인 epoch가 필요합니다.
- **근거 symbol**
  - Rust `prepared_live::monotonic_ns`는 `mach_absolute_time`을 씁니다(sleep 중 정지).
  - Python `time.monotonic_ns()`도 macOS에서 같은 성질로 알려져 있습니다(정적 지식 기반이며 미검증).
  - 이 값들이 `validate_epoch_clock`과 `Budget._clock`의 `abs(diff) <= 2000`에 쓰입니다.
  - Driver 근거에 따르면 S4의 `runtime-entered` 기록이 성공했으므로, 두 언어의 원점 정합성은 적어도 1회 확인됐습니다. 그러나 sleep 내성은 검사된 적이 없습니다.
- **최소 보정 (제안, guard 의미 변경이므로 Owner 승인 필요)**
  - 양쪽 모두 sleep을 포함하는 clock으로 바꿉니다(Darwin `mach_continuous_time` / `CLOCK_MONOTONIC` 계열). 같은 fixture로 parity를 재검증합니다.
  - 또는 controller 수명 동안 sleep을 막는 power assertion을 실행 조건으로 두고, 그 실패를 사전 gate로 만듭니다.
  - guard를 완화하는 방식은 제안하지 않습니다.

### F6. [높음 · H10 경로 결함] 봉인 후 Owner 대기에 상한이 없고, proxy와 controller의 wall 수명은 대기 중에도 흐름

- **영향**
  - candidate commit과 ticket 승인 대기가 proxy 수명보다 길어지면 다음이 일어납니다.
    - `PreparedFdController._serve`가 `time.monotonic() < self.deadline`을 만족하지 못해 proxy를 종료합니다.
    - Rust `prepared_live::proxy`의 `tokio::time::timeout(expires_wall_ms)`도 만료됩니다.
  - 그러면 accept turn의 generation을 보낼 수 없습니다.
  - 남은 proxy slot이 없어(proxy 총 2개, 1개는 S4에서 소모) H10 acceptance를 수행할 수 없습니다.
  - 인증 만료 역시 대기 중에 계속 진행됩니다.
- **근거 symbol**
  - `run_live_command`의 `while not request_path.exists()` 루프에는 deadline이 없습니다.
  - `materialize_proxy`의 `expires_wall_ms`는 pause와 무관한 wall 시각입니다.
  - 계약상 "candidate 승인 대기 중 runtime thread idle 유지"와 충돌합니다.
- **최소 보정 (제안)**
  - 대기 상한을 `min(proxy 만료, controller deadline, 인증 만료) - 여유`로 명시합니다.
  - 상한을 넘으면 unavailable로 정리하고 보고합니다.
  - 또는 accept 단계의 proxy·시간 배분을 Owner 계약에서 별도로 정합니다.
  - 자동 재시작은 하지 않습니다.

### F7. [중간] 장부 lock을 양쪽 모두 `LOCK_EX|LOCK_NB`로 잡아, 단순 읽기 경합도 비가역 실패가 됨

- **영향 / Trigger**
  - runtime spawn 직후에는 두 작업이 동시에 일어납니다.
    - Python `register_runtime`(`on_spawn`)이 `budget.read()`를 호출하며 append.lock을 배타적으로 잡습니다.
    - Rust `install`이 `reserve("runtime-entered")`를 호출합니다.
  - 둘이 겹치면 어느 쪽이든 "concurrent journal writer"로 실패합니다. 결과는 start 소모와 stop(F4)입니다.
  - controller thread와 main thread가 동시에 `read()`할 때도 같은 문제가 생깁니다.
- **근거 symbol**: `Budget.read` / `Budget.reserve`(Python), `Spec::reserve`(Rust).
- **최소 보정 (제안)**
  - 읽기는 `LOCK_SH`, 쓰기는 `LOCK_EX`를 쓰고, 둘 다 짧은 상한(예: 수 초) 안에서 blocking 대기합니다.
  - 양쪽에 동시성 테스트를 추가합니다.
  - 동시 controller 거절은 기존처럼 `controller.lock`으로 유지합니다.

### F8. [중간] 최종 request body 검증이 닫힌 key 집합이 아니고, privacy 검사는 `input`에만 적용됨

- **영향**
  - `instructions`, `include`, `text`, `service_tier`, `metadata`, `reasoning.summary` 등 검사하지 않는 top-level 필드가 그대로 송신될 수 있습니다.
  - 자동 metadata와 원천 분리라는 IR0-07의 의도가 부분적으로만 강제됩니다.
- **근거 symbol**
  - `prepared::bind_live_request`와 `validate_live_wire_input`은 일부 필드만 비교합니다.
  - 비어 있지 않은 base instructions를 input 앞에 `BaseInstructionsFragment`로 넣는 mirror 경로는 실제 `build_responses_request`와 대조된 적이 없습니다. fake 테스트의 base는 `""`입니다.
  - 실제 encoder가 `instructions` 필드를 쓴다면, 모든 live 송신이 거절되거나(fail-closed) 그 필드가 검사 없이 통과합니다.
- **최소 보정 (제안)**
  - wire top-level key의 정확한 allowlist를 둡니다.
  - `instructions`(존재 시)가 manifest base와 같은지 확인합니다.
  - `encrypted_content`를 제외한 전체 wire에 privacy 검사를 적용합니다.
  - 비어 있지 않은 base로 실제 encoder 출력을 대조하는 테스트를 추가합니다.

### F9. [중간 · uncertain] live tool envelope과 native catalog/serialization 정합성이 synthetic 기대값으로만 검증됨

- **영향**: native 값이 기대와 다르면, 정상 경로라도 prepare나 session init 단계에서 fail-closed가 됩니다(stop으로 이어짐).
- **근거**: 다음 항목이 실제 native 값과 대조되지 않았습니다.
  - clock의 `CurrentTimeHandler` 등록 조건. fixture는 `experimental_supported_tools:["clock"]`을 썼지만 native gpt-6-astra catalog의 값은 확인되지 않았습니다.
  - `tool_mode == "direct"`.
  - `validate_dynamic_tools`/`config_snapshot`의 `to_value(typed) == raw tool-profile` round-trip 동일성.
  - host `Admission.bind`의 `namespace=="functions"`, `strict: False` 및 schema 형태.
- **최소 보정 (제안)**
  - 실제 계정 없이 `tool-profile.json`을 ThreadStartParams → session → `prepared_envelope`로 통과시킵니다.
  - 그 결과를 host Admission 기대값과 비교하는 offline 테스트를 추가합니다.
  - native catalog의 tool 관련 필드 조건을 S4 시작 전 판정 항목으로 명시합니다.

### F10. [중간 · uncertain] final header guard와 실제 provider POST header의 정합성이 미검증

- **근거**
  - `validate_final_headers`는 미지정 header를 모두 거절합니다.
  - 실제 `ApiResponsesClient` 및 provider가 추가할 수 있는 header(session/conversation 계열, beta header, request-id, `trace_headers()` 결과)는 검사된 적이 없습니다.
  - `prepared_final_headers_reject_duplicate_and_metadata_drift`는 `default_headers()`만 사용합니다.
- **영향**: header가 하나라도 다르면 gen1이 fail-closed되어 turn 실패와 stop으로 이어집니다.
- **최소 보정 (제안)**: 실제 encoder와 auth provider의 요청을 fake transport로 포착해 guard에 통과시키는 offline 테스트를 추가합니다.

### F11. [중간 · open] Rust proxy CONNECT의 end-to-end 경로가 실행된 적 없음

- **근거**
  - S3 근거는 helper 수준입니다. limits에도 "transport/FD helpers"로 적혀 있습니다.
  - S4에서 proxy는 시작 후 바로 종료됐습니다.
  - 따라서 다음이 실행된 증거가 없습니다.
    - `PreparedConnection`이 UnixStream extensions에서 request extensions로 전파되는지(rama 내부 동작).
    - `connect_policy`의 FD 획득.
    - rama CONNECT 응답의 status line과 header가 엄격한 `read_connect_response`를 통과하는지.
- **최소 보정 (제안)**: 합성 controller, 실제 Rust proxy role, PreparedUds client, self-signed TLS로 구성한 통합 fixture를 사용합니다.

### F12. [낮음] 요청이 끝나도 controller의 dup lease가 TCP 연결을 유지함

- **근거**
  - `PreparedFdController._request`의 `lease = stream.dup()`은 `revoke(start)`나 `close()` 때만 shutdown됩니다.
  - 요청이 끝나거나 취소돼도 upstream TCP는 열린 채로 남습니다. runtime당 최대 64개입니다.
- **최소 보정 (제안)**: 터널 종료를 controller에 알리거나, 요청 단위로 revoke합니다. 최소한 한계로 문서화합니다.

### F13. [낮음] Rust `validate_proxy_spec`의 slot 카운트가 lineage를 반영하지 않음

- **근거**: `rows`(현재 epoch)만 셉니다. Python materializer는 lineage 전체 counts를 씁니다.
- **최소 보정 (제안)**: lineage segment 전체에서 `proxy-start`를 셉니다.

### F14. [낮음 · known blocker 관련] 결정적인 로컬 검사보다 effect 예약이 먼저 일어남

- **근거**
  - `prepared_live::install`은 `spec.reserve("runtime-entered")`를 호출한 뒤에야 `initialize_live`(`validate_directories`) 같은 결정적 로컬 검사를 수행합니다.
  - known blocker(materializer `allocate`에 `config`가 없음)도 이 순서 때문에 slot을 소모했습니다.
  - `config` 디렉터리 추가는 필요조건이지만 충분조건은 아닙니다(F1, F3, F9, F10).
- **최소 보정 (제안)**: 디렉터리, spec, identity에 대한 정적 검사를 예약보다 먼저 수행합니다.

### F15. [낮음 · H10 적격성] 실제 문서 특성이 verifier refusal이나 Work stop으로 이어질 수 있음

- **근거**
  - `worker.verify`의 DOC-LINKS는 범위 밖 상대 링크를 만나면 finding을 내지 않고 `WorkerRefusal`을 냅니다. host refusal을 거쳐 stop이 됩니다. 계약과는 일치합니다.
  - `LiveSession.iterate`는 진행이 없는 turn이 한 번만 있어도 중단합니다.
- **최소 보정 (제안)**: S6 사전 gate에서, target mutation 전에 원본 출력의 링크 범위와 식별정보 분포를 점검 항목으로 고정합니다.

---

## 2. 우선 감사 영역별 요약 (정적 추론)

| 영역 | 정적 판단 |
| --- | --- |
| clock v2 carry/stop/pending/replay/lock | 다음이 Python과 Rust에서 대칭으로 구현됐습니다: predecessor hash, 카운터 상속, pending/sealed 거절, stop 상속, 동일 복구 재사용 거절. Driver 근거로 clock17 parity와 실제 epoch02 연속 기록이 있습니다. 문제는 F5(sleep), F7(NB lock), F13입니다. |
| UDS CONNECT / native TLS / final bytes / latch | redirect, retry, 재연결은 0이고 hostname과 SNI 검증이 있으며 helper 테스트도 갖춰져 있습니다. F2(정상 완료 시 latch 경합), F8, F10, F11은 open입니다. |
| controller SCM_RIGHTS / identity / reservation / revoke | 다음이 적절합니다: 단일 FD, 받은 모든 rights를 소유 처리, peer audit token, runtime pid와 spec·sequence의 controller 측 결속, 예약 1개당 FD 1개. 문제는 F12, F13입니다. |
| ordinary 격리 | 모든 분기가 process-fixed OnceLock 뒤에 있습니다. `HttpError` 타입 변경도 ordinary에서는 `Request` variant만 유지하는 것으로 보입니다. Driver 근거로 ordinary smoke가 통과했습니다. 새 결함은 없습니다. |
| native read-only auth / retry0 / model / policy | 매 송신마다 storage를 다시 읽고 비교합니다. keyring write는 차단되고 refresh, reload, recovery는 0입니다. model catalog는 native 성공만 허용합니다. 실제 경로는 미실행입니다(인증 초기화 전에 종료). F3이 다음 잠재 blocker입니다. |
| history / context / gen2 / dispatch | snapshot, reset, history digest, gen2 허용 delta, parallel=false, gen1 전체 수신 후 dispatch가 구현됐습니다. fake 테스트만 있습니다. 실제 첫 turn에 initial item 외 native 항목이 기록되는지는 미확인입니다(T-01). |
| 문서 atomic write / verifier / installed accept / recovery / idle thread | worker의 parent dirfd, exclusive swap, fsync, identity 재확인, 합성 OS negative는 Driver가 재사용한 근거입니다. idle thread와 accept 경로는 F6 때문에 결함 상태입니다. H05 recovery gate는 합성 단위 테스트만 있습니다. |

---

## 3. IR0-01–16 분류

"resolved"는 packet 안의 근거가 있는 경우에만 붙였습니다.

| ID | 분류 | 근거 / 이유 |
| --- | --- | --- |
| IR0-01 | uncertain (구현됨, live 미검증) | `bind_live_history_items` 및 snapshot history digest에 fake 테스트만 있습니다. |
| IR0-02 | uncertain (구현됨) | `parallel_tool_calls=false`, 전체 버퍼링, 초과 call 거절이 구현됐습니다. F2가 정상 경로를 위협합니다. |
| IR0-03 | open | schema와 pack은 구현됐습니다. S6 실제 bytes 기준 산정은 없습니다. |
| IR0-04 | uncertain | `trusted_turn_input`과 Owner input digest 결속이 구현됐고, live는 미실행입니다. |
| IR0-05 | uncertain (부분 근거) | 공통 journal과 fsync 예약이 있고, S4 Rust 행을 Python이 수용했습니다. F7이 남아 있습니다. |
| IR0-06 | open | F4(stop 승격)가 start 배분 계약과 충돌합니다. |
| IR0-07 | open | 문서 segment의 origin 결속은 있습니다. F8 때문에 원천 분리 강제가 불완전합니다. |
| IR0-08 | uncertain | worker와 OS negative 14개(재사용 근거)가 있습니다. 실제 target device와 링크 범위는 S6 미실행입니다. |
| IR0-09 | uncertain | 별도 target 경로와 candidate hash가 있습니다. 기존 accepted binary의 전후 byte 대조 receipt는 packet에 없습니다. |
| IR0-10 | open | F-01–F-08 중 tag, commit, refs는 Driver 수동 경로이며 미실행입니다. |
| IR0-11 | uncertain | 절차와 시간 carry는 packet만으로 검증할 수 없습니다. |
| IR0-12 | uncertain (정적 구현) | 매 송신 검증과 refresh 0이 있고, 실제 만료 시 동작은 미실행입니다. |
| IR0-13 | open | S6 시간 gate의 구현이나 실측이 없습니다. F6도 관련됩니다. |
| IR0-14 | resolved (문서) | 장부 구간 분리가 문서에 명시돼 있습니다. |
| IR0-15 | uncertain | mode별 분기가 있고 Driver 근거로 offline8이 통과했습니다. live 분기는 미실행입니다. |
| IR0-16 | uncertain | Python 순서 강제가 있습니다. 다만 S4에서 proxy1을 소모해 남은 slot은 S6뿐이며, F13이 남아 있습니다. |

---

## 4. Known Limitations

- Reviewer는 테스트, 빌드, OS fixture를 재현하지 않았습니다. 통과 수치는 모두 Driver 기록입니다.
- 실제 runtime 경로는 startup 단계에서 종료됐습니다. 그 결과 다음은 실행 근거가 0입니다: auth 내용 접근, control/model 송신, thread, turn. 따라서 auth, policy, model, HTTP, CONNECT, history에 대한 판단은 정적 추론입니다.
- packet에 없는 내부 구현은 검증하지 못했습니다: `turn_processor`/`turn_prepare`/`turn_start_prepared`, codex-api SSE parser, `build_responses_request`, rama의 extension 전파, `DynamicToolSpec` 직렬화. F2, F8–F11의 불확실성은 여기서 비롯됩니다.
- 실제 native config 내용, 실제 5문서, 실제 target, 계정은 packet에서 제외됐습니다. 따라서 F3과 F15는 확정할 수 없습니다.
- SBPL의 loader cache 줄은 해시로 요약됐습니다. Cargo.lock은 delta만 제공됐습니다.
- H09 문서 사례는 Driver 분류이며, 독립 사용자의 이해도나 효율을 증명하지 않습니다.

## 5. Recommendation

- **판정: REVISE / not qualified.**
  - 통합 candidate는 known blocker를 고쳐도 F1 때문에 U2 경로에 진입할 수 없습니다.
  - clock 경로도 F2, F3, F9, F10에 따라 다시 실패할 위험이 큽니다.
  - H01–H08은 partial입니다. H05와 H10은 not-qualified를 유지합니다.
  - 이 검토를 근거로 Owner 수락, production 적격, 설치, publication을 승인하지 않습니다.
- 다음 단계는 Owner 결정 사항입니다. Reviewer는 자동 진행을 권고하지 않습니다.
  - (a) 소진된 build/보정 장부를 넘어 보정할지 여부와 그 범위.
  - (b) stop 의미를 분리할지(F4)와 stopped run 재개 계약.
  - (c) clock source 또는 sleep 방지 조건(F5).
  - (d) 봉인 후 대기와 proxy 수명 설계(F6).
  - (e) native config에 대한 사전 판정 경로(F3).
- 보정이 승인된다면 다음 offline 사전 검사를 먼저 수행하는 것을 권고합니다. 모두 실제 계정 없이 가능하며, 실패를 live start 소모 이전에 드러낼 수 있습니다.
  - F1: U2 params로 두 gate 통과.
  - F2: 실제 parser와 PreparedUds로 gen1 완료 후 gen2 허용.
  - F8/F10: 실제 encoder와 header의 guard 대조.
  - F9: tool envelope round-trip.
  - F11: proxy end-to-end.
``````

### Integrated R1-01 — Driver Disposition

Reviewer 원문은 위와 같고 아래는 Driver 판단이다. accept는 결함/공백의 수용이며 수정 완료나 Owner 채택을 뜻하지 않는다. revise는 주장 또는 최소 보정의 정정, defend는 현재 계약 유지, needs-user는 실제 계약 선택을 뜻한다. 모든 소스 판정은 정적이며 신규 재현 PASS를 주장하지 않는다.

| ID | Driver 처분 | 근거와 후속 경계 | 증거 수준 |
| --- | --- | --- | --- |
| F1 | accept | message_processor.rs:665–679는 ephemeral 단일 key만 허용해 host의 dynamicTools 포함 요청을 반드시 거절한다. 두 번째 typed gate의 정확값 검사는 유지하고 첫 gate의 prepared-live 허용 모양을 맞춰야 한다. | 확정 정적 결함; 실행 재현 아님 |
| F2 | revise | 본문 EOF 전 drop이 전역 failed를 잠그는 위험을 수용한다. 추가로 codex-api/src/sse/responses.rs:648–654 자체가 Completed를 보내고 즉시 return하므로 core 상위 upstream 루프만 drain하는 보정은 충분하지 않다. prepared 전용 parser/body 완료 계약과 실제 parser→UDS gen1/gen2·절단 검사가 필요하다. | 정적 경로 확인; 실제 경합/정상 gen2 재현 없음 |
| F3 | needs-user | native config가 로드되며 비어 있지 않은 MCP/plugin 집합을 거절하는 코드는 확인했다. 실제 config는 읽지 않았으므로 현재 환경 실패라고 확정하지 않는다. native 정책을 그대로 보존하는 config-only 사전 판정 경로를 우선 제안하며 집합을 비우는 override를 자동 채택하지 않는다. | 환경 의존 미확인 |
| F4 | needs-user | 일반 예외의 Work stop 승격과 epoch 간 상속은 확인됐고 S4 stop27은 실제 근거다. 기존 stop·카운터를 수정하지 않는다. 새 계약은 실패한 start의 무효 효과/프로세스 종료/원 장부 identity를 확인한 exact Owner 재개 처분으로 한정해야 하며 모든 예외의 자동 재시도를 허용하면 안 된다. | 현재 stop은 유효; 재개 계약 변경 필요 |
| F5 | revise | macOS clock 선택의 sleep 위험은 공식 Python/Apple 자료로 보강했다. 기존 2초 guard와 clock17 PASS는 그대로 유효하고 실제 sleep 내성을 검증한 것은 아니다. guard 완화나 sleep을 Owner 대기로 자동 분류하지 않는다. sleep 포함 clock의 양 언어 parity 또는 한정된 awake 실행 조건을 별도 계약으로 선택해야 한다. | 공식 문서+정적 추론; sleep 실험 없음 |
| F6 | accept | host.py:1858–1863의 승인 대기는 상한이 없고 FD controller/proxy는 고정 수명이다. 대기/accept 준비 상한을 실행 자원 수명 안에 두고 만료 전에 unavailable로 정리하는 계약이 필요하다. 같은 idle thread 기준이나 인증 만료 시 중단을 없애지 않는다. | 정적 수명 불일치 |
| F7 | accept | Python read/reserve와 Rust reserve의 배타 nonblocking lock은 정상 동시 접근도 거절할 수 있다. controller 단독 소유와 append 직렬성은 유지하고 읽기/쓰기 잠금을 짧은 고정 상한 내에서 조정하는 대응 동시성 검사가 필요하다. | 경합 가능성; 재현 안 함 |
| F8 | revise | top-level exact key/value 검증과 전체 비암호문 privacy 범위를 보완할 필요는 수용한다. 다만 core/client.rs:996–1006의 실제 encoder도 BaseInstructionsFragment를 input 앞에 넣으므로 top-level instructions를 쓴다는 추측은 현재 소스에서 지지되지 않는다. 비어 있지 않은 base의 실제 encoder→guard 검사는 여전히 필요하다. | 일부 추론 정정; 검증 공백 유지 |
| F9 | revise | 현재 DynamicToolFunctionSpec은 camelCase 및 false deferLoading 생략으로 고정 tool-profile과 정적으로 맞는다. envelope 전체/handler namespace/native catalog 적격성은 아직 실행하지 않았다. 실제 결함이라고 단정하지 않고 account-free typed pipeline 검사와 native clock capability gate로 남긴다. | 일부 정적 정합; 통합 적격성 미확인 |
| F10 | revise | live는 ApiResponsesClient.stream(wire, empty headers, None)을 사용해 stream_request의 session/thread/compatibility header 추가 경로를 거치지 않는다. 해당 예시는 현재 경로 근거가 약하다. provider/auth/default/trace_headers가 최종 guard와 맞는지는 fake transport 통합 검사로 확인해야 하며 allowlist를 추측으로 넓히지 않는다. | 일부 경로 추론 정정; 전체 header 통합 미검증 |
| F11 | accept | S3 helper/OS 증거와 실제 Rust proxy→CONNECT→TLS 통합 증거를 구분한 지적을 수용한다. 현재 H03 partial을 유지하고 실제 role·parser를 잇는 합성 통합 검사 없이 live 통과로 승격하지 않는다. | 알려진 증거 공백; 새 실행 실패는 아님 |
| F12 | revise | dup lease는 stop/revoke 시 shutdown을 보장하는 의도된 보존이다. 완료/취소 후 해제 handshake는 별도 설계가 필요하다. 추가로 Python controller·Rust broker·UDS transport 모두 64 요청 상한을 쓰므로 H10 40 turns×2 generation+control 최대 배분보다 실제 허용 범위가 작다. 이 제한을 preflight 비용에 반영하거나 계약을 맞춰야 하며 수치를 자동 증가시키지 않는다. | 정적 자원/요청 상한 한계 |
| F13 | revise | validate_proxy_spec의 s4/s6 slot 판정이 현재 epoch proxy-start 수만 보는 문제를 수용한다. 그러나 앞선 validate_budget_rows는 lineage 전체 proxy-start≤2를 이미 검사하므로 전체 cap 우회로 표현하지 않는다. epoch 전환 뒤 잘못 거절하는 가용성 문제와 slot identity 결속을 보정해야 한다. | 정적 slot 불일치; 전역 cap 유지 |
| F14 | accept | materializer config 누락은 실제 S4 원인이다. 순수한 root/spec/identity 검사를 효과 예약 전에 수행하도록 분리하되 auth/network/실행 전에 reserve하는 원칙과 이미 소비한 start를 유지해야 한다. | S4 재현 근거+정적 순서 확인 |
| F15 | defend | 범위 밖 상대 링크를 읽지 않고 unavailable로 거절하는 것은 승인된 DOC-LINKS 계약과 일치한다. verifier 기준을 완화하지 않는다. 실제 대상 접근 승인 뒤 S6 사전 점검에 링크/식별정보/진행 가능성을 포함하되 이번에는 실제 문서를 읽지 않았다. | 기존 범위 방어; S6 입력 적격성 미완료 |

F5 확인 출처: [Python 3.14 time.monotonic](https://docs.python.org/3.14/library/time.html#time.monotonic)은 macOS 구현이 mach_absolute_time임을 명시하고, [Apple mach_time.h](https://github.com/apple/darwin-xnu/blob/main/osfmk/mach/mach_time.h)는 mach_continuous_time이 sleep 중에도 증가함을 설명한다. 이는 환경 sleep 실험이나 현 실행의 drift 원인 재현을 대체하지 않는다. Reviewer의 일반적인 CLOCK_MONOTONIC 계열 제안을 그대로 채택하지 않고 양 언어의 정확한 API/단위/원점 parity를 따로 결정해야 한다.

IR0 분류는 Reviewer 표의 문서상 resolved14와 나머지 open/uncertain을 유지한다. Driver의 추가 소스 대조로 일부 추론을 좁혔지만 실제 runtime/send/history/accept 근거를 만들어내지는 않았다. H09는 기존 Driver 문서3사례를 Reviewer도 문서 근거로만 다뤘으며 Owner 수락과 독립 사용자의 효율 주장은 남는다.

### Integrated R1-01 — Concrete Continuation Boundary (Not Adopted)

현재 후보는 일반/최적화 회귀 각각706 PASS이나 actual host/provider 전체 경로가 qualified는 아니다. config 누락만 고치고 다음 live start를 쓰는 선택은 배제한다. 다음 보정은 아래 세 묶음으로 정리되며 구현 승인은 아직 없다.

| 묶음 | 최소 변경 경계와 완료 증거 |
| --- | --- |
| A. live 진입·완료·wire 정합성 | runtime `app-server/src/message_processor.rs`, `core/src/client.rs`, `core/src/session/prepared.rs`, `http-client/src/prepared_uds.rs` 및 직접 대응 tests; F2는 기존 범위 밖 `codex-api/src/sse/responses.rs`와 해당 entry/options의 prepared-only 완료 계약까지 필요할 수 있다. 두 gate 실제 통과, nonempty-base encoder/header/tool envelope, 실제 parser→UDS→proxy→TLS 정상 gen1/gen2 및 절단/cancel refusal를 먼저 합성으로 확인한다. ordinary 동작은 유지한다. |
| B. 예산·실패·대기 수명 | host `host.py`/tests와 runtime `app-server/src/lib.rs`/직접 대응 tests에서 F4/F5/F6/F7/F13을 함께 다룬다. 기존 stop27/카운터/epoch 원문을 유지하며 정확한 Owner 재개 처분, 정상 read/write 경합의 bounded serialization, sleep/idle/expiry 계약, lineage slot 결속을 고정한다. 새로운 원점이나 slot으로 소모량을 초기화하지 않는다. |
| C. 실행 전 적격 판정 | task materializer의 config 생성과 root/spec 사전 검사를 보정한다. native config-only gate는 정책 무시/override를 기본값으로 삼지 않는다. F12의 lease 및64요청 상한과 F15의 문서 적격성을 실제 S6 필요량에 대조한다. actual target read/provider 승인은 그대로 별도다. |

현재 build3/3·제품 보정2/2·S4 proxy1 소모 및 stop을 유지한다. 따라서 위 보정 구현/새 build/같은 단계 proxy 재시도·stopped-run 해제는 기존 승인으로 진행할 수 없다. H05는 원 actor/decision/ticket packet을 만든 뒤 exact Owner 판단을 받고, H10은 실제5문서 read/provider/intent/grant/refs/candidate commit과 최종 결과 수락을 따로 받는다. commit/push/merge/release나 설치본 변경은 포함하지 않는다.

예상과 상한을 구분한다. 위 통합 보정·직접 대응 offline 검사·candidate build는 90–150분 판단치다. 새 live S4 45–70분, H10 60–90분, 필수 보정 확인 R1/처분15–25분은 아직 이 통합 후보의 완료 실측이 없어 불확실하다. 최종 host/장부 source가 바뀌면 이전 source의706 PASS를 새 source PASS로 이전하지 않는다. 영향 분석과 재사용을 먼저 하고, 기존 최종 normal/O 기준을 유지하는 full pair가 필요하면 이번 실측114.23분을 근거로110–130분을 추가한다. 이 경우 후속 전체 예상은320–465분이며 기존 예약 제외 잔여에 들어가지 않는다. 새 총량이나 시도 상한을 자동 채택하지 않는다. Owner 대기는 제외하고 reviewer 대기·build/test와 겹치는 Driver 작업은 한 번만 센다.

Owner 결정 대기: (1) 위 보정 범위와 실패/재개·sleep/idle 계약, (2) 기존16시간 및 build/보정/proxy 한도에서 수행 불가능한 추가 실행의 별도 범위·예산. 아직 미채택이며 추가 제품 수정/테스트/실제 문서 접근을 시작하지 않는다. 현재 Work와 Goal은 미완료다.


### Integrated R1-01 — Preservation And Decision Checkpoint

검토 입력60개 hash와 전송 packet 불변, Reviewer 응답의 Work 내 원문1회 포함, Work diff check를 확인했다. 종료된 R1의 task 전용 `r1-integration-01/scratch`는 비어 있고 사용 process가 없어 디렉터리1개만 삭제했다. active 경로 변경0. 검토 원문/request/metadata, source와 복구 원문, 후보 binary, stop journal 및 normal/O·중단 결과는 Owner 보정 범위 판단과 정확한 후속 실행의 소비자가 있어 유지하며 그 처분 때 다시 평가한다. 추가 보관 사본은 만들지 않았다.

2026-10-23T21:37:34.213740+00:00 정산: 누적 848.883분, 전체 잔여 111.117분, 미확정14.302분·종료20분 제외 가용 76.814분. R1 1회 완료, build3/3·보정2/2 및 runtime auth/model/문서 효과0 상태 그대로다. 최종 보고 overhead는 다음 재개 전에 먼저 정산한다. 전체 Goal/Work 미완료, Owner 수락 없음. 새 계약·한도 결정 전 추가 제품 구현/검사/live/외부 전송 없이 대기한다.

## Consolidated Correction Proposal — 2026-10-24

Owner는 추가 보정·중단 후 재개 계약·시간/횟수를 한 번에 판단할 구체 실행안 작성을 요청했다. 구현이나 한도 변경 승인이 아니다. 비공개 통합 실행안 `private-evidence/E016`에 수정 파일, R1 처분, stop27의 제한 재개, 새 epoch/clock/idle/lock/transport 계약, H01–H10 완료 근거와 남은 exact Owner gates를 묶었다. 제안 SHA-256: 9af6b37fcd2c053469f240f4b8d8093527666a4fb99c937aab1cc1ab6a795b8d. [공개용 중립화]

제안: full pair가 필요하면 후속320–465분 예상, 통합 누적 상한16→24시간. 기존 사용량·실패·증거는 모두 carry한다. 추가 build2(누적5), source 보정2와 H10 내용 보정2(전체 누적6), proxy2(누적3), 필수 최종 R1 1회(누적2). live start6/thread8/turn54/generation108/control24와 offline36/72/72는 유지한다. 이번 보정안에 한정한 추가 R0 면제를 명시적 Owner 결정에 포함하며, 승인으로 간주하지 않는다.

H05 원 ticket packet, H10 실제 input/read/provider/intent/grant/setup와 봉인 후 exact candidate commit, 최종 결과 수락은 실제 입력 준비 뒤 묶어서 판단한다. source Git publication·설치본·전역 설정 변경 권한은 추가하지 않는다. Owner만 기다리는 시간은 제외하되 same-thread idle은15분/자원 만료의 더 이른 한도를 제안한다.

### Authoring Checkpoint

2026-10-24T00:21:23.298000+00:00 현재 계획 작성까지 정산: 기존 확정 848.883분 + 이전 최종 보고 1.441분 + 이번 작성/확인 8.381분 = 통합 858.706분.
현재 승인된16시간 상한은 그대로이며 잔여 101.294분이다.
24시간 안이 승인되면 잔여 581.294분, reserve14.302분·종료20분 제외 546.992분이다.
full pair 포함 예상 누적은 1178.706–1323.706분이다. 이 checkpoint 이후 최종 보고 시간은 승인/재개 전에 추가 정산한다. 실제 승인 전에는24시간을 활성화하지 않는다.

source·tests·live/provider·실제 문서·reviewer·Git 실행0. 기존 제품/원 proof·회귀/R1/journal evidence는 그대로 유지하고, 이번 제안과 원장·이 기록만 갱신했다. 새 진행 registry/Work/STATUS 변경 없음. 새로운 삭제/active 경로 변경0. 현재 source/binary/복구/evidence는 보정 판단과 후속 실행의 소비자가 있어 유지하며, 승인/종료 후 기존 cleanup 조건으로 다시 판단한다.

## Consolidated Correction Execution Approval — 2026-10-24

Owner 직접 승인(2026-10-24T00:36:53.935743Z, messageprivate-approval/O010): 실행안 SHA-256 9af6b37fcd2c053469f240f4b8d8093527666a4fb99c937aab1cc1ab6a795b8d의 보정 범위·제한 재개 계약·누적24시간·추가 시도·추가 R0 면제·Claude R1 1회를 승인했다. H05 복구, H10 actual 입력/권한 및 candidate commit, 최종 수락은 별도 exact packet 판단으로 남는다. source Git publication·설치본/전역 정책 변경 권한은 추가하지 않는다. 계획 원문은 historical Proposed bytes로 보존하며 이 승인 기록이 실행 선택을 소유한다. [공개용 중립화]

기존64개 복구 입력과 현재 source를 대조했다. 기존 진행 기록의 승인된 append 외 source drift0. 새 SSE 경계4파일은 현재 HEAD와 byte 일치하며 local Git에서 복구 가능하다. 다음 build가 덮어쓸 현재 후보3개 binary를 task correction-05/recovery/candidate-03에 copy2하고 hash를 대조했다. 기존 stop journal 불변을 고정했고 삭제/active path 변경0이다.

현재 사용862.331분, 누적24시간 잔여577.669분. 이전 보고2.155분과 이번 승인 후 활동을 포함했고 Owner 응답 대기는 제외했다. A 단계180분은 승인 시각부터 누적한다. 제품 수정/build/live/review 시도는 아직 추가 소모하지 않았다.

### Correction-05 — Native Config Gate And Bounded Amendment Proposal

현재 native user config의 key 조건만 검사했다. MCP3개 중 explicit disabled1, plugins12개 중 explicit disabled0이며 hooks table도 비어 있지 않다. 항목 이름·설정 내용·credential은 기록하지 않았다. App Server startup와 prepared turn의 두 gate는 mcp_servers/hooks/plugins/model_providers가 없거나 빈 table이어야 통과한다. 현재 native loader는 user config를 보존하고 feature=false overlay는 해당 table 자체를 제거하지 않는다. 이것은 raw config 관측과 실제 source 대조이며, native effective runtime을 실행해 얻은 실패라고 주장하지 않는다.

승인 실행안의 config 부적격 중단 조건을 적용했다. 설정 삭제/우회·candidate build·live·auth/provider·target 접근은 추가하지 않았다. F1 raw/typed U2 gate와 F2 prepared-only body EOF 완료 경로를4개 source 파일에 작성한 상태로 보존했다. SSE 집중3개는 최종 PASS(5.283초); 최초2회는 native RateLimits 선행 이벤트를 검사에서 예상하지 못한 assertion 실패였고 원 결과를 유지한다. raw/typed gate의 실제 실행, 전체 parser/transport 통합, 나머지 보정은 미검증이다. 후보 binary3개와 stop27 journal은 그대로다. 이번 source 보정1묶음을 이미 소비했으며 환불하지 않는다.

후속 판단을 위한 좁은 변경안(아직 미승인):

1. 전역 native config와 credential을 변경하지 않고, 이 prepared live 후보 프로세스의 CLI overlay에서 native loader로 확인한 MCP와 plugin 항목 각각의 enabled=false만 명시한다. hooks는 기존 features.hooks=false와 실제 hook 실행 경로 차단을 검사한다. 원 설정 항목을 삭제하거나 일반 CLI 기본값을 바꾸지 않는다.
2. 수정은 app-server/src/lib.rs의 후보 전용 config 구성/검사와 core/src/session/prepared.rs의 live config 검사 및 직접 tests로 제한한다. offline fixture의 빈-config 요구는 유지한다. 단순 nonempty table 허용은 금지한다. live에서는 원 inventory와 disabled 상태를 결속하고 startup/turn 양쪽에서 같은 설정·활성 도구0/비승인 loader0을 확인한다. managed/system/MDM/login/exec-policy는 계속 native로 읽으며 mandatory policy와 충돌하면 중단한다.
3. 합성 native config로 MCP/plugin/hook 실행 canary0·내부/최종 inventory0과 configured-but-disabled 성공, enabled/drift/mandatory conflict 거절을 검사한다. 실제 native config는 내용/이름을 로그에 복제하지 않는 config-only 적격성 확인을 먼저 수행한다. native auth나 새 live slot을 이 probe에 사용하지 않는다. 이 조건을 기존 허용 파일/권한 안에서 구현할 수 없으면 추가 확장 없이 중단한다.
4. 이 설정 적응은 남은 source 보정1묶음에 배정한다(실행하면 source 보정 추가2회 모두 사용, 전체 보정 누적4; H10 내용 보정2는 유지). 판단 예상20–40분이며 통합24시간·A180분·기존 build/live/proxy/R1 횟수 안에 포함한다. 전체 완료 예상은 이 추가 위험 때문에 실측 후 다시 산정하며 상한은 늘리지 않는다.
5. 추가 R0 면제는 이 좁은 변경안까지 명시적으로 확장하는 판단을 함께 받는다. 이미 승인된 최종 Claude R1 1회에 이 delta를 포함하고 review 호출은 늘리지 않는다. H05/H10/최종 수락 gate는 그대로다.

추천 판단 문구: “전역 native 설정과 인증/mandatory policy를 유지하고, prepared live 후보에서만 MCP·plugins 명시적 비활성화와 hooks 실행 차단을 검증하는 위5항의 제한 변경을 승인한다. 남은 source 보정1묶음과 기존24시간/A180분·시도 한도를 사용하고, 이 delta까지 추가 R0 면제를 확장한다.”

반대 선택이면 현재 부분 보정·원 evidence를 보존한 중단 상태를 유지한다. 빈 설정 파일 복제, 원 user config 제외, 정책 무시, 더 넓은 OS 권한은 이 제안에 포함하지 않는다.

정산 2026-10-24T00:49:31.350586+00:00: 통합873.485분,24시간 잔여566.515분, reserve 제외532.213분. 이번 승인 후 활동12.624분. counts는 build3·보정3·offline10·live1·proxy1·R1 1, thread/turn/generation/control/runtime auth0이다. 모든 집중 process group 종료 확인. source delta/현재 bytes와 원 복구 입력을 보존했고 active 경로 변경/삭제0. 계획/검증 후 최종 보고 시간은 다음 checkpoint에서 더한다.

### Correction-05 — Config Amendment Approved

Owner 직접 응답(2026-10-24T00:54:52.516566Z, messageprivate-approval/O009): “제한 변경과 R0 면제 확장 승인”. 위5항의 후보 전용 비활성화·검증 변경과 R0 면제 확장을 승인했다. source 보정 마지막1묶음을 예약하여 전체 보정4, 이번 source2/2를 소비한다. H10 내용2묶음은 별도 유지한다. 예상20–40분과 검증은 기존24시간/A180분 안에 포함한다. 추가 build/live/proxy/review 횟수 증가와 전역 설정·credential 변경은 없다. native loader 사전 관측 → 명시적 disabled overlay → startup/turn 동일 inventory 확인을 구현하며, mandatory 충돌·조건 입증 불가면 중단한다. [공개용 중립화]

### Correction-05 — Native System Policy Alias Gate

Owner 승인한 설정 적응을 구현했다. 원 native inventory를 보존하면서 후보 CLI overlay의 enabled=false leaf만 merge하고, startup/turn의 설정 계층과 disabled 상태를 process 안에 결속한다. 실제 전역 config/credential은 변경하지 않았다. 필수 managed hook은 feature 비활성화로 소실되지 않도록 명시적으로 거절한다.

최종 App Server 집중10 PASS, ignored3(별도 clock parity·native config·path probe)가 있다. raw/typed gate 및 합성 configured-but-disabled·plugin inventory0·hook canary 미실행·native 내용 drift·mandatory approval 충돌을 실행했다. 이전 실패는 type fixture 누락과 test stack overflow, 컴파일2건이며 원 기록을 보존한다. test stack은 후보 entry와 같은16MiB로 맞췄고 native child timeout/OS 권한은 변경하지 않았다. 기존 SSE3 PASS는 별도 evidence다. Host 새 epoch/정확한 재개·clock·lock 집중5 PASS이며, 그 뒤 작성한 host lease/transport/idle 보정과 Rust 대응·cross-language parity는 아직 미완료다. 이 부분 상태로 live를 실행할 수 없다.

실제 native config-only probe는 인증/provider/live slot 없이 실행했으나 PermissionDenied로 실패했다. 메시지 원문·설정 값 대신 고정 분류(operation not permitted, requirements, toml)만 출력했다. 같은 승인 runtime profile의 추가 read-only path probe는 /etc metadata와 /etc/codex/requirements.toml open에서 PermissionDenied, /private/etc metadata는 present, /private/etc/codex 및 그 requirements open은 NotFound를 관측했다. 이 probe의 test PASS는 경로 진단 실행 완료이며 설정 적격성 PASS가 아니다. source native loader는 /etc/codex/requirements.toml을 사용하고, 기존 profile은 /private/etc 쪽 exact paths만 허용한다. 별칭 경로 거절이 관측됐으며 더 넓은 설정·정책 적격성은 아직 입증되지 않았다.

승인안은 network/sandbox 허용 폭 변경을 제외했고, 이번 설정 적응도 기존 권한 안에서 입증하지 못하면 중단하도록 정했다. 따라서 OS profile을 변경하거나 loader에 정책 경로 override를 넣지 않고 중단한다. 추가 candidate build/live/proxy/R1은0, 인증/provider/실제 문서 접근0이다. product source 보정2/2는 이미 소비했고, H10 내용2묶음은 그대로 남는다.

구체적인 다음 제한안(미승인): exact alias read delta `private-evidence/E018` SHA-256 479a5d75939be08fff1c7e640ece0f2e88e031545138dea4f993fcdc1e71bd51를 새 후보 runtime profile에만 더한다. /etc와 /etc/codex 및 rules의 metadata, 기존 canonical 허용과 대응하는 config.toml·requirements.toml·managed_config.toml의 exact file-read, rules의 directory read만 포함한다. subtree/global metadata/write/network/Mach 허용은 추가하지 않는다. 적용 전과 매 시작에 기존 /etc→private/etc topology와 frozen native inventory를 확인하며 drift면 중단한다. 전역 profile과 historical profiles를 수정하지 않고 native defaults/mandatory policy 로딩을 유지한다. 먼저 config-only 적격성과 outside-read/write/network 거절 canary를 확인한 뒤 기존 보정을 계속한다. 다른 거절 경로를 자동 추가하지 않는다. 이것은 제한된 OS profile 변경이므로 별도 Owner 판단이 필요하다. [공개용 중립화]

예상5–15분 판단치(config-only·profile-equivalence/canary 포함)이며 기존24시간/A180분·잔여 build/live/review 한도 안에서 사용한다. 추가 source 보정 슬롯을 만들지 않고 현재 미완료 보정 묶음과 task materializer에 한정한다. 이 exact profile delta까지 추가 R0 면제를 확장하고 이미 승인된 최종 R1에 포함하는 판단을 함께 요청한다. 권한 변경이므로 기존 설정 적응 승인을 자동 확대하지 않는다.

추천 판단: “제시한 exact /etc alias read delta를 후보 전용 profile에 적용·검증하고 이 delta까지 R0 면제를 확장하는 것을 승인한다. 기존 누적24시간/A180분·시도 한도를 유지하며 다른 OS 경로·권한은 자동 확대하지 않는다.”

정산 2026-10-24T01:14:43.968772+00:00: 통합896.150분,24시간 잔여543.850분, reserve 제외509.547분. 모든 집중 검사·probe process group 종료와 old journal 불변을 확인했다. 현재8개 수정 파일을 task recovery/config-amendment-partial에 copy2·byte/hash 검증하여 보존했다. 후보 binary 복구본·원 source·stop27 증거는 계속 보존한다. active 경로 변경0/삭제0. 현재 partial source·task scripts·tests 및 cached test 산출물은 동일 보정의 완료와 Owner 판단을 위한 구체 소비자가 있어 유지하며 다음 gate에서 정리 여부를 다시 판단한다. 최종 보고 시간은 다음 checkpoint에 더한다.

### Correction-05 — Exact Native Alias Delta Approved

Owner 직접 응답 “exact alias 변경과 R0 면제 확장 승인”(question call_3fd74d77f66c4255a9b6f9620f3f4b23)을 받았다. delta SHA-256 479a5d75939be08fff1c7e640ece0f2e88e031545138dea4f993fcdc1e71bd51의 exact read/metadata 규칙만 새 후보 profile에 적용한다. 이 delta까지 R0 면제를 확장하고 기존 최종 R1에 포함한다. 시간·source 보정·build/live/proxy/review 한도는 그대로다. 확인·보존 작업 중 응답을 받았으므로 이번 구간에 별도 Owner 대기 공제를 넣지 않았다.

### Correction-05 — Alias Verified, Native Managed Policy Unavailable

승인된 exact alias delta(479a5d75939be08fff1c7e640ece0f2e88e031545138dea4f993fcdc1e71bd51)를 새 probe profile에만 적용했다. 전역 profile·설정·credential은 변경하지 않았다. /etc→private/etc topology를 launch 전에 확인하고, 별도 sandbox canary에서도 readlink/canonicalize가 일치함을 확인했다. alias requirements open은 이전 PermissionDenied에서 NotFound로 바뀌었다. 합성 outside 파일 read/write, loopback TCP bind/connect는 모두 PermissionDenied였다. 이 canary PASS는 해당5개 경계의 관측이며 전체 OS sandbox나 native 정책 적격성 PASS가 아니다.

실제 native config-only는 계속 FAIL이다. 첫 alias 검사와 값 없는 cause-chain 분류 검사 모두 kind=Other였다. 최종 고정 분류는 chain_depth=1, categories=[managed, failed to]다. source application.rs는 macOS managed preferences synchronize를 필수로 부르며, macos.rs의 CFPreferencesAppSynchronize가0을 반환하는 오류 경로만 이 분류와 일치한다. 이것은 실행 오류 분류와 source 경로를 결합한 localization이며 OS 근본 원인 재현은 아니다. 현재 profile에는 이미 com.apple.cfprefsd.daemon/agent Mach lookup이 포함되어 있으므로 Mach 권한 누락이라고 단정할 수 없다. 다른 경로 read/write나 Mach 권한을 추정해 추가하지 않았다. managed policy를 무시하거나 loader override로 우회하지 않았다.

마지막 App Server 집중10 PASS,4 ignored(명시적 clock parity/config/path/canary 전용)는 logs/config-09에 있다. 이 중 alias canary만 별도 ignored invocation에서1 PASS했다. 실제 config-only는0 PASS/1 FAIL이며 앞선 실패 기록도 유지한다. 기존 SSE3 PASS·Host5 PASS는 별도 범위다. clock/lease/transport/idle의 통합 보정과 qualification은 여전히 미완료이며 candidate build 또는 live에 사용할 수 없다.

이번 alias 승인 후 추가 candidate build/live/auth/provider/proxy/R1은 모두0이다. 기존 counts는 유지한다: build3, source correction 전체4(이번 추가 source2/2 소비), offline10, live1, proxy1, R0=1, R1=1. 모든 이번 test/probe group 종료, old budget journal 불변, 합성 marker bytes 불변을 확인했다. source 변화는 app-server lib의 진단 분류와 canary뿐이며 새 recovery/alias-diagnostic-partial에 copy2·byte/hash 검증했다. 이전8파일 recovery 중 나머지7파일은 현재 source와 같다. source·진단 script·profile·로그·canary fixture는 native-policy 후속 보정 및 최종 판단의 재현 입력으로, test cache는 동일 미완료 보정의 다음 build 소비자로 유지한다. active 경로 변경0, 삭제0.

승인한 별칭 범위 안에서 native mandatory policy 적격성을 입증하지 못했으므로 다음 단계로 진행하지 않고 중단한다. 재개에는 native managed preferences 동기화를 기존 격리 계약 안에서 충족할 방법의 확인이 필요하다. 추가 OS 권한, source 보정 묶음 또는 mandatory policy 계약 변경이 필요하면 exact delta와 실패 근거를 준비한 뒤 별도 Owner 판단을 받아야 한다. 현재 추가 권한·timeout·시도나 source 슬롯을 승인된 것으로 간주하지 않는다. H05/H10/최종 수락 gate도 유지한다. H01–H10 완료나 Work Done을 선언하지 않는다.

정산 2026-10-24T01:21:04.246213+00:00: 통합902.488분,24시간 잔여537.512분, reserve 제외503.209분; A 사용41.627분/180분. 이번 alias 승인 이후 본 checkpoint까지4.373분이며 예상5–15분 범위의 진단·차단검증·보존 작업이다. 시간 상한 소진이 아니라 native policy 조건 미충족 중단이다. 이후 검증/보고 시간은 다음 정산에 포함하고 실제 Owner 대기만 제외한다. Toolstead STATUS·backlog 및 이 Work 상태는 변경하지 않았다.

### Native Managed Policy Diagnosis And Amendment Proposal

Owner의 2026-10-24 진단/계획 요청에 따라 권한 확대 없이 최소 C probe1회를 실행했다. native·합성 domain 모두 AppSynchronize=false였고 Set/CopyValue0, auth/provider0, process group 종료, old journal 불변이다. 최초 compile은 SDK 미지정으로 실패, 기존 SDK 명시 후 성공했으며 두 기록을 유지한다. candidate build/source correction/live 카운터는 그대로다. profile은 기존 renderer+승인 alias 규칙과 같으며 새 logical 권한을 추가하지 않았다.

현재 profile에는 cfprefsd Mach lookup이 있으나 preference-read/write operation이 없다. 로컬 SDK는 AppSynchronize를 defaults 변경을 쓰는 함수로 설명하며 현재 OS profile은 domain별 preference read/write를 구분한다. 읽기 권한 누락은 확인됐으나 exact read delta만으로 동기화가 통과하는지는 아직 미검증이다. 강제 값 조회의 false도 MDM 부재 증거가 아니다. 좁은 OS 로그 조회는 추가 원인 분류를 제공하지 않았다.

추가로 raw user config의 nonempty notify와 후보 empty-notify invariant의 충돌을 발견했다. 실제 native effective load 이후 재현은 아직 unavailable이다. 다른 user-level instruction/model/provider override 충돌은 보이지 않았고, frozen native inventory와 user default.rules1개 조건은 통과했다. system 파일 부재가 MDM/cloud/실제 auth 적격성을 보장하지 않는다. source8파일·복구본 및 old journal이 기존 중단 시점과 같음을 검증했다.

한 번에 판단할 제한 보정안 `private-evidence/E017` SHA-256 b636ea03e7ce4b0cae74cab6defe0c03b774140a95223d858fa582c5f9cb498a. exact read delta SHA-256 deece84a62e711248ad91f9889995bcce97fcc49c8430e6670ec463d082c07a4는 미적용이다. 먼저 domain 하나의 read-only delta1회가 성공해야 source 추가1묶음(notify 비활성화/drift/local aggregate preflight)을 진행한다. source 총상한6→7 제안이며 기존 사용4와 H10용2를 유지한다. 예상20–35분/중단45분을 기존 누적24시간/A180분 안에서 사용한다. 이 범위까지 R0 면제 확장과 기존 최종 R1 포함을 함께 판단받는다. write 권한·policy 우회·다른 경로 자동 추가는 제외한다. 기존 중단 상태와 cap/count는 유지하며 새 실행은 승인 전 시작하지 않는다. [공개용 중립화]

정산 2026-10-24T02:07:54.185037+00:00: 사용916.257분,24시간 잔여523.743분, reserve 제외489.441분. A 사용55.395분/180분이다. 이전 보고1.268분·이번 진단/작성12.500분을 포함했고 실제 Owner 대기33.064분만 제외했다. 진단 source/binary/profile/결과는 이 exact read-delta 비교와 Owner 판단의 입력으로 보존한다. active 경로 변경0, 삭제0. 검토 종료 또는 다음 gate에서 소비 종료 여부를 재평가한다. STATUS/새 Work/설치본/Git 변경은 없다.

### Correction-06 — Conditional Read Gate Approved

Owner 직접 승인(2026-10-24T02:13:01.091884Z)에 따라 exact proposal b636ea03e7ce4b0cae74cab6defe0c03b774140a95223d858fa582c5f9cb498a의 read delta1회와 통과 후 source1묶음만 실행한다. source 총상한7을 활성화하되 현재 사용4는 유지한다. 본45분·누적24시간·A180분 중 먼저 닿는 상한과 R0 면제 확장/기존 최종 R1 포함을 기록했다. read gate 실패 시 source 묶음을 소비하거나 권한/우회를 추가하지 않는다. 이전 보고3.195분을 정산하고 실제 Owner 대기1.920분만 제외했다. 기존 source8파일/복구본, 원 journal, probe binary/source hash가 일치한다.

### Correction-06 — Exact Read Gate Failed And Stopped

Owner 승인한 domain 읽기 delta(deece84a62e711248ad91f9889995bcce97fcc49c8430e6670ec463d082c07a4)를 새 profile에만 추가하여 기존 hash 고정 C probe를1회 실행했다. 프로필은 승인 base+alias+해당 delta와 일치한다. native domain AppSynchronize=false, synthetic domain=false였으며 gate FAIL이다. native errno=1은 CF API의 보장된 원인 code가 아니므로 write 권한 필요나 특정 syscall 거절로 단정하지 않는다. 읽기 delta 하나로 native 동기화 gate를 해결하지 못했다는 결과만 확정한다.

probe elapsed0.017769초, process exit0은 진단 프로그램 종료를 뜻하며 정책 gate PASS가 아니다. Set/CopyValue 호출0, auth/provider/live0, process group 종료와 old journal 불변을 확인했다. 결과는 `private-evidence/E019`에 보존한다. [공개용 중립화]

명시적인 실패 시 중단 조건에 따라 notify/preflight source 보정은 시작하지 않았다. 추가 source 묶음 소비0이며 기존 correction 사용4/승인 총상한7을 유지한다. build3/offline10/live1/proxy1/R0=1/R1=1과 실제 auth/threads/turns/sends0도 그대로다. source 수정·새 permission·우회·추가 probe·재시도·리뷰를 실행하지 않았다. 기존 미완료 source와 H05/H10/최종 수락 상태는 그대로이며 완료로 보고하지 않는다.

source8파일과 기존 recovery bytes/hash, probe source/binary/profile hash, 원 journal hash를 검증했다. exact 실패 재현·Owner 처분에 필요한 기존 binary/source와 새 profile/result/authorization을 유지한다. active 경로 변경0, 삭제0. 전역 profile/config/credential은 변경하지 않았으며 새 read 권한은 종료된 진단 프로세스에만 적용됐다.

정산 2026-10-24T02:14:44.101057+00:00: 통합921.169분,24시간 잔여518.831분, reserve 제외484.529분. A 사용60.307분/180분, 이번 보정 사용1.717분/45분이다. 이후 최종 검증/보고 시간만 다음 정산에 더한다. 실패 후 새 실행을 진행하지 않는다.


### Trusted Native Runtime Transition Proposal — 2026-10-24

Owner가 native runtime을 신뢰 영역으로 옮기고 문서 worker 격리를 유지하는 방향을 선택하고, 기존 사용량/실패/증거를 보존한 단일 승인용 실행안 작성을 요청했다(messageprivate-approval/O007). 구현 재개 승인으로 해석하지 않는다. 실행안 `private-evidence/E020` SHA-256 8c476340d29c6df2d6541727290616fa61aea901702c917e6f51d917c0f3b5e7. 기존 Work/두 checkout을 유지하며 현재 Correction-06 실패와 R1 REVISE/not qualified 상태를 변경하지 않는다. [공개용 중립화]

제안은 runtime용 task Seatbelt wrapper만 제거하고 worker/verifier/proxy OS 경계, native mandatory policy·read-only auth 코드·request guard·exact host authority를 유지한다. runtime 자체의 arbitrary file/exec/direct network OS 차단 보장은 철회한다. H03의 worker access/alias/IPC/verifier/코드 guard/새 mode binding6개 후속 기준과 원 criteria 매핑을 명시하며 옛 strict-runtime H03 PASS로 바꾸지 않는다. source 범위는 기존 미완료 보정과 전용 launch mode/entry·host/runner/direct tests에 한정하고 전역 설정·credential·installed Core·제품 Git 변경은 제외한다.

예상 약6시간30분–10시간, 제안 통합 누적28시간(기존24시간에서4시간 증가), 승인 후12시간 및 단계별 더 이른 상한이다. source/내용 보정 총7→8(기존 사용4 유지, 추가 source2/H10내용2), R0 총1→2를 제안한다. build5/live6/proxy3/최종 R1총2 및 나머지 기존 상한은 유지한다. 새 R0와 조건부 실행 승인 결합은 이번에 한한 Owner 예외 결정으로 명시하고, 새 R0·기존 잔여 R1 각각1회의 bounded 비식별 Claude firstParty 전송을 포함한다. H05/H10 exact 입력·candidate commit/최종 수락은 여전히 별도다.

정산 2026-10-24T02:32:47.283572+00:00: 이전 최종 보고/feasibility/이번 계획을 더한 통합 935.841분, 현재24시간 잔여 504.159분. 확인된 Owner 대기 3.381분만 제외했다. 제안28시간은 아직 미활성이다. 코드·runtime/probe·build/test·auth/provider·reviewer 실행0. 기존 recovery·failure/profile/journal은 전환 및 최종 review/Owner 처분의 입력으로 유지한다. active 실행 경로 변경0, 삭제0. 이번에는 이 계획과 본 Work/장부 기록만 작성했다.

계획 검증 완료 2026-10-24T02:34:01.511767+00:00: source13경로·H03 6항목·원 승인 상한/카운터 불변·diff --check를 확인했고, 현재 source8파일은 기존 recovery와 bytes/hash/mode가 같다. 검증/보고 준비를 더한 통합 937.078분, 현재24시간 잔여 502.922분이다. final proposal SHA-256 8c476340d29c6df2d6541727290616fa61aea901702c917e6f51d917c0f3b5e7; 제안28시간은 미활성이다. source/runtime 실행 경로 변경0, 삭제0.


### Trusted Native Runtime Transition Approved

Owner 직접 승인: 실행안의 신뢰 경계·H03 변경, 수정 범위와 누적28시간·이번12시간 중 먼저 닿는 상한, 보정 총8, R0 조건부 실행과 R1 전송까지 승인하고 진행해줘. 기존 사용량·실패·증거는 유지하고, H05/H10의 exact 승인과 최종 수락은 준비된 묶음으로 제시해줘.

승인한 실행안 SHA-256 8c476340d29c6df2d6541727290616fa61aea901702c917e6f51d917c0f3b5e7. 통합 누적28시간/이번12시간/단계별 더 이른 상한, 보정총8, 새R0 1회와 기존 잔여R1 1회 및 명시된 bounded Claude firstParty 전송을 활성화한다. 기존 source4/build3/offline10/live1/proxy1/R0=1/R1=1과 auth/sends0을 유지한다. 원 실패와 epoch는 보존하고 이번 변경의 조건부 R0부터 수행한다. 아직 source 구현 재개·auth/provider 접근은 하지 않았다.

2026-10-24T02:38:46.674587+00:00 정산 통합941.831분. 이전 최종 보고 이후 짧은 미정산 구간은 보수적으로 포함했으며 확인되지 않은 대기는 공제하지 않았다. 이번12시간 시작은 2026-10-24T02:35:42+00:00이다.


### Native Transition R0 — Verbatim Reviewer Response

# R0 정적 검토: Trusted Native Runtime / Isolated Document Worker 전환 계획

## 0. 검토 전제와 판정 원칙

- **검토 성격**
  - stdin으로 받은 계획, R1 원문, 발췌 source만 읽은 정적 검토입니다.
  - 도구·명령·빌드·테스트·외부 조회는 한 번도 하지 않았습니다.
  - 계획에 적힌 수치(706 PASS, 114.23분, SSE3, clock17 등)는 모두 Driver 기록을 인용한 것이며, Reviewer가 재현하지 않았습니다.
- **추론하지 않는 사항**
  - Owner 승인·수락
  - H05/H10 완료
  - production 적격
  - 보정·재시도·재빌드 권한
- **승인 상태 관련 주의**
  - 계획 본문의 Status 줄은 "Proposed — … 새 실행·상한·H03 기준은 승인 대기"입니다.
  - 이번 요청이 이 파일을 승인안으로 제시하고 있지만, 승인 기록(Owner message id와 계획 hash의 결속)은 packet에 없어 확인하지 못했습니다.
- **수용한 전제**
  - runtime OS 파일·exec·직접 egress 보장의 철회를 목표 경계로 받아들였습니다.
  - 해당 보장의 복원은 요구하지 않습니다.

---

## 1. 판정

**REVISE (범위 내 필수 보정 필요). 신뢰 경계 설계 자체는 수용 가능합니다.**

**잘 된 부분**
- 경계를 정직하게 기술했습니다.
  - runtime OS 보장 철회를 명시했습니다.
  - worker/proxy의 OS 보장을 유지합니다.
  - 코드 guard와 OS 강제를 구분합니다.
  - 상위 sandbox를 우회하지 않습니다.
- 그 밖의 핵심 요구도 대체로 갖췄습니다.
  - H03 후속 기준을 6개 항목으로 나눴습니다.
  - 이전 PASS를 옮겨 붙이지 않습니다.
  - 정책·인증 유지 원칙과 구독 경로를 유지합니다.

**REVISE 사유**
- 계획의 시도·시간 상한과 목표 상태를 실제로 강제할 장부 계약이 계획에 명시돼 있지 않습니다.
- 그런데 현재 source(Python/Rust 양쪽 validator)는 이 상한들과 정면으로 충돌합니다.
- 다음 세 가지 판정 규칙이 불명확합니다.
  - mandatory policy 계층의 "unavailable"과 중단의 구분
  - Keychain 상호작용 감지 방법
  - 인증 저장소 불변 관측 방법

**진행 판단**
- 아래 필수 항목은 모두 계획이 명시한 파일 범위(`lib.rs`, `host.py`, task-root artifact) 안에서 보정할 수 있다고 판단합니다.
- 다만 보정 후 진행할지는 Owner와 Driver가 판단할 사항입니다.

---

## 2. 필수 Findings

### R0-01. 장부 epoch 계약이 계획 상한과 충돌하며, 계획에 신규 epoch 스키마가 정의되지 않음

**근거**
- 현재 hard-coded 값 (Python `Budget._lineage`/`_validate`, Rust `epoch_lineage`/`validate_budget_rows` 공통)

  | 항목 | v3 값 | v2 값 |
  | --- | --- | --- |
  | `total_cap_ms` | 86_400_000 (24h) | 57_600_000 |
  | `correction` | ≤6 | — |
  | `review` | ≤3 | — |
  | `build` | ≤5 | — |
  | `proxy-start` | ≤3 | — |

- v3 resume 조건도 고정돼 있습니다.
  - `failure_class == "pre-auth-config-root-missing"`
  - `allowed_next_start == "clock-02"`
  - stop subject `{"reason":"runtime stdout closed"}`
- 계획의 값은 이와 다릅니다.
  - 통합 상한 28h = 100_800_000ms
  - 보정 총 8 (계획은 "기존7→8"이라고 쓰지만 코드의 v3 상한은 6)
  - R0/R1 누적 2/2 = review 4
  - 후속 epoch를 "새 승인·mode 계약·anchor/tail/checksum·누적 사용량"으로 결속

**영향**
- v3 그대로라면 다음이 `journal attempt cap`이나 `recovery cap or reserve changed`로 거절됩니다.
  - 7번째 보정
  - 최종 R1 (4번째 review)
  - 24h를 넘는 carry
- 신규 epoch를 즉흥적으로 만들면 Python과 Rust의 parity가 깨질 위험이 큽니다.
- 계획의 "기존7"과 코드의 6 중 어느 쪽이 맞는지 정적으로 판정할 수 없습니다.
- Correction-06 이후 v3 epoch가 stop 상태인지도 packet에 없어 판정할 수 없습니다.

**최소 보정 (제안)**
- 계획의 범위 내 보정 묶음에 "anchor v4 계약"을 명시합니다.
  - cap
  - kind별 상한표
  - resume authorization 스키마 (failure class = Correction-06 / native transition, 허용 다음 start, 직전 stop/tail identity)
  - launch-mode/contract digest 필드
- 같은 fixture로 Python과 Rust 양쪽에서 accept/reject parity를 확인하는 것을 auth 전 local gate로 고정합니다.
- "기존7"의 출처를 정정합니다.

### R0-02. 승인 후 12시간 상한과 단계 상한이 기계적으로 강제되지 않음

**근거**
- 두 validator 모두 `total_deadline_ms == origin_wall_ms + cap - carry`를 정확히 요구합니다.
- 따라서 "승인 후 12h"처럼 더 이른 별도 상한을 anchor에 담을 수 없습니다.
- 단계 상한(A240 등)은 장부 개념에 없습니다.
- 현 정산으로 보면 28h 잔여는 742.922 − reserve 34.302 ≈ 708.6분입니다. 12h(720분)보다 작으므로 지금은 28h가 먼저 걸립니다. 다만 이것은 정산 수치에 의존하는 결과일 뿐 구조적 보장은 아닙니다.

**영향**
- "먼저 닿는 값" 원칙이 Driver의 수동 판단에만 의존합니다.
- 상한 초과가 장부에서 거절되지 않습니다.

**최소 보정 (제안)**
- v4 anchor에 `run_deadline_ms`(승인 시각 + 12h)를 추가합니다.
- validator가 실제 deadline을 `min(cap 기반, run_deadline)`으로 쓰게 합니다.
- 단계 상한은 Driver 장부 강제로 명시하고, 단계 진입과 종료를 `checkpoint` 행으로 남깁니다.

### R0-03. 보정 카운터가 단일 `correction` kind라서 "H10 두 슬롯은 source에 전용하지 않음"을 강제할 수 없음

**근거**
- `DocumentController.dispatch`는 실패 뒤 첫 write 시 `reserve("correction", …)`을 호출합니다.
- source 보정도 같은 kind로 계상됩니다.
- validator는 kind 총합만 셉니다.

**영향**
- source 보정이 H10 내용 보정 슬롯을 소모하거나, 반대로 내용 보정이 source 슬롯을 소모해도 장부가 막지 못합니다.

**최소 보정 (제안)**
- subject에 `class: source|content`를 필수로 둡니다.
- class별 상한을 양쪽 validator에 넣습니다.
  - source: 누적 6 = 기존 4 + 이번 2
  - content: 2
- 기존 4건은 `source`로 carry합니다.

### R0-04. mandatory policy 계층의 "unavailable" 처리와 "읽히지 않으면 중단"이 서로 모순됨

**근거**
- 계획 A: "load 뒤 미확인 계층은 unavailable로 표시"
- 같은 계획의 경계 절: "기존 native 정책이 여전히 읽히지 않거나 강제 설정과 충돌하면 중단"
- Correction-06은 `AppSynchronize=false`로 FAIL했습니다.
- `config_for_roots`는 native 경로를 기본값으로 둡니다.
  - managed/system/requirements/MDM 경로가 `None`입니다.
  - native loader가 NotFound(정상 부재)와 권한·동기화 실패를 구분해 드러내는지 packet으로는 확인할 수 없습니다.
- cloud config bundle은 인증 뒤 stage(1)에서만 확인할 수 있습니다.

**영향**
- managed preferences나 MDM 계층이 조용히 빈 값으로 처리된 상태에서 auth와 live로 진입할 수 있습니다.
- 이는 mandatory policy 보존 요구에 어긋납니다.

**최소 보정 (제안)**
- 원천별 상태표를 auth 전 gate로 고정합니다.
  - 원천: requirements.toml, managed_config.toml, system config, MDM requirements, managed preferences
  - 상태: `loaded | absent-confirmed(근거 종류) | unreadable/unknown`
  - `unreadable/unknown`이 하나라도 있으면 auth를 시작하지 않습니다.
- cloud bundle은 config-only 결과에서 `unavailable-until-auth`로 표기합니다.
- runtime stage(1)의 실패는 즉시 중단으로 명시합니다.
- `AppSynchronize`의 반환값은 성공 근거로 쓰지 않습니다.

### R0-05. 인증 저장소·HOME 불변을 관측하는 구체적 방법이 없음

**근거**
- native runtime은 직접 시작되며 Seatbelt write 제한이 없습니다.
- `LiveSession.launch`의 `closed_environment`는 실제 `HOME`을 그대로 전달합니다.
- `auth_home`(AUTH 디렉터리)은 user config와 인증의 원천이며, 이제 runtime이 쓸 수 있습니다.
- 계획은 "guard/counter/관측으로만 보고"라고만 적었습니다. 무엇을 어떻게 관측하는지, 그리고 credential 내용을 읽지 않는다는 제약과 어떻게 양립하는지 정의하지 않았습니다.
- `prepared_auth_violation_count`는 코드 경로 내부 카운터일 뿐입니다.

**영향**
- refresh, 재저장, 설정 파일 갱신 같은 부작용이 생겨도 감지되지 않을 수 있습니다.
- 반대로 Driver가 hash를 내려고 auth.json을 읽으면 "token 복사·전달 금지"와 충돌합니다.

**최소 보정 (제안)**
- 각 runtime start 전후로 AUTH 트리(`config.toml`, `auth.json`, `secrets/*`, `rules/*`)에 대해 다음 metadata만 기록하고 비교합니다.
  - 기록 항목: dev/ino/size/mode/mtime/ctime/항목 목록
  - 내용은 읽지 않습니다.
  - 변경이나 신규 항목이 있으면 not-qualified로 판정하고 중단합니다.
- task root 밖에 runtime이 만들 수 있는 알려진 경로는 존재 여부만 관측합니다.
- `auth-boundary`의 `violation_count`를 결과에 함께 결속합니다.
- 보고서에는 "코드 경로 관측이며 OS 강제가 아님"을 명기합니다.

### R0-06. Keychain prompt를 감지하는 방법과 "승인 금지"의 운영 규칙이 없음

**근거**
- 새 candidate는 새 build이고 서명·코드 identity가 바뀝니다.
- 계획은 "Keychain prompt면 즉시 중단"이라고 적었지만, prompt는 GUI 대화상자입니다.
- host가 관측할 수 있는 것은 RPC deadline 경과뿐입니다.
- prompt에서 "허용/항상 허용"을 누르면 그 자체로 계획이 금지한 Keychain 승인·ACL 변경이 됩니다.

**영향**
- 감지 기준이 불명확한 대기 상태로 live start와 시간이 소모됩니다.
- 사람이 실수로 허용하면 금지 효과가 발생합니다.

**최소 보정 (제안)**
- auth 단계(`bind_auth`부터 stage(1) 이전까지)에 짧은 고정 timeout을 둡니다.
- timeout은 `keychain-interaction-suspected` 분류로 중단하며, start는 소모로 처리하고 재시도는 0입니다.
- Owner에게 "prompt가 나타나면 허용하지 말고 거부/무응답"이라는 사전 지시를 승인 packet에 명시합니다.
- config-only가 Keychain에 접근하지 않음을 근거로 남깁니다. 남길 수 없으면 unavailable로 표기합니다.

### R0-07. notify의 layer 출처 검증과 drift 동결이 현재 snapshot 범위 밖에 있음

**근거**
- `disabled_live_config_snapshot`의 layer별 수집 key는 `mcp_servers / plugins / hooks / model_providers`뿐이며 `notify`가 빠져 있습니다.
- CLI `notify=[]`는 상위 계층에서 하위 계층 값을 조용히 덮어씁니다.
- 계획의 요구는 두 가지입니다.
  - 덮어쓰는 대상은 user layer의 선택적 notify로 한정한다.
  - system/managed의 강제 notify는 거절하고, 원 layer와 identity drift를 검증한다.

**영향**
- system layer의 notify도 조용히 억제되어 거절 대신 통과할 수 있습니다.
- 실행 중 notify 출처 drift가 동결 비교에서 누락됩니다.

**최소 보정 (제안)**
- override 전 snapshot에서 notify를 정의한 layer를 식별합니다. user layer 외에서 정의돼 있으면 거절합니다.
- per-layer snapshot key에 `notify`를 추가합니다.
- 다음 두 negative 테스트를 집중 검사에 포함합니다.
  - system-layer notify → 거절
  - managed-layer notify → 거절

### R0-08. start 실패나 유도된 process death가 Work 전체 stop으로 승격됨 (R1 F4 잔존). 계획의 2차 slot·H05·"제한된 재개"와 정합이 불명확

**근거**
- `run_live_command`의 `except`는 실패 종류와 무관하게 `budget.reserve("stop", …)`을 호출합니다.
- stop 이후에는 `process-ended|checkpoint`만 허용됩니다.
- `resume_check`와 `recovery_command`는 모두 `not stopped`를 요구합니다.
- stop을 해제하려면 owner_message_id에 결속된 신규 epoch가 필요합니다.
- 반면 계획은 다음을 전제합니다.
  - synthetic 2, H10 2 slot
  - H05: 실제 process death 후 승인된 replay
  - "알려진 startup 실패 뒤의 제한된 재개만 허용"
  - "범위 안 보정은 다시 묻지 않음"

**영향**
- 첫 실패에서 Work가 stop되면 두 번째 slot과 H05 replay 경로에 도달할 수 없습니다.
- 도달하려면 추가 Owner 결정이 필요한데, 이는 "다시 묻지 않음"과 충돌합니다.
- 특히 H05의 유도된 death가 live session 안에서 일어나면 recover가 거절됩니다. 이 부분은 정적 추론입니다.

**최소 보정 (제안)**
- 계획에 다음 세 가지를 명시합니다.
  - (a) Work stop 대신 `process-ended`와 start 소모로 끝낼 실패 종류의 닫힌 목록
  - (b) H05 death를 수행할 epoch·journal과, 그 경로에서 stop을 남기지 않는 구조
  - (c) 그 밖의 stop은 새 Owner 결정을 요구한다는 사실, 그리고 이 경우 해당 slot은 사실상 unavailable이라는 보고 규칙

---

## 3. 선택 Findings

- **O-1. Spec 필드명 충돌**
  - Rust `Spec.profile`은 tool profile(`clock|u2`)입니다.
  - host의 `runtime["profile"]`은 OS SBPL입니다.
  - 모드별 typed 계약으로 바꿀 때 `tool_profile`과 `launch_mode`로 분리하기를 권합니다.
  - spec version도 올려 v1 live spec을 거절하도록 하기를 권합니다.
- **O-2. 비HTTP egress 표면의 보고 범위 명시**
  - 대상: websocket·remote control·exec-server·DNS 등
  - "guard 경유"는 `codex_http_client` 경로에만 해당한다고 보고서에 한정하기를 권합니다.
  - 그 밖의 표면은 "비활성 설정(근거) 또는 unavailable"로 나열하기를 권합니다.
- **O-3. project config layer 원천 목록 동결**
  - runtime이 sandbox 밖에서 cwd 상위 경로의 `.codex/*`를 탐색할 수 있습니다.
  - 계층 원천(name·disabled_reason·key 집합)을 전부 동결 snapshot에 포함하기를 권합니다.
  - 현재는 4개 key가 있는 layer만 기록합니다.
- **O-4. writer quiescence의 한계 공개**
  - `writer_attestation`과 `check_files`로는 신뢰 runtime 자신의 직접 문서 write를 사전에 막지 못합니다. 사후 탐지만 가능합니다.
  - 이 한계를 H03-2 결과에 공개하기를 권합니다.
- **O-5. 단계 사용량 해석**
  - "이전 A 사용량은 통합 장부에서 유지"가 새 A240 한도에 합산되는지 불명확합니다.
  - 한 문장으로 명확히 하기를 권합니다.
- **O-6. 매핑표와 launch contract의 검토 공백**
  - retained/amended/historical/unavailable 매핑표와 실제 launch contract는 이번 R0 이후에 생성되므로 독립 검토를 받지 못합니다.
  - auth 전에 이를 hash로 고정하고 최종 R1 packet에 포함하기를 권합니다.
- **O-7. 정산 산술 (정적 확인만 수행)**
  - 1440 − 937.078 = 502.922, 1680 − 937.078 = 742.922, reserve 2058.14초 = 34.302분이 일치함을 확인했습니다.
  - 실제 사용량의 진위는 검증하지 않았습니다.

---

## 4. 미해결 실행 제한 (정적 추론과 Driver 실행의 구분)

- **Reviewer 미실행**
  - 빌드·테스트·canary·config-only·live를 실행하지 않았습니다.
  - 위 모든 판단은 정적 추론입니다.
- **packet에 없는 source**
  - `message_processor.rs`(R1 F1의 thread/start gate)
  - SSE parser·`client.rs`(R1 F2)
  - `prepared_uds_tests`, `prepared_fd_tests`
  - `initialize_prepared_read_only_auth`
  - HTTP constructor latch
  - 이들의 현재 처분 상태는 판정하지 못했습니다.
- **packet에 없는 상태와 입력**
  - 현재 장부 상태(v3 epoch의 stop 여부, 실제 correction/review 행 수)
  - native config 내용
  - managed preferences와 MDM의 실제 상태
  - Keychain 저장 방식
  - 실제 5문서
  - 따라서 R0-04, R0-05, R0-06의 실제 발현 여부는 미확정입니다.
- **확인하지 못한 승인 근거**
  - Owner 승인 기록과 계획 hash 결속은 packet에서 확인하지 못했습니다.
- **현재 상태 유지**
  - Work 미완료, S4 인증 전 실패, Correction-06 FAIL, H05/H10 not-qualified 상태를 그대로 유지합니다.
- **이 검토의 효력**
  - 이 검토는 구현·live·인증·전송 실행을 승인하지 않습니다.
  - 범위를 확대하는 근거도 아닙니다.

### Native Transition R0 — Driver Disposition

# R0 Driver Disposition — Native Transition

Owner authorization: direct message private-approval/direct-message; approved plan SHA-256 8c476340d29c6df2d6541727290616fa61aea901702c917e6f51d917c0f3b5e7. The original Proposed wording is preserved as the reviewed historical input; authorization.json and the Work separately record activation. Reviewer: claude-opus-5-5, session ae5f0fb8-63bf-43e9-a20c-47b0d8689b14, firstParty subscription, tools0, static only, 242.839 seconds. Input drift0. R0 REVISE is not an execution result or Owner acceptance. [공개용 중립화]

| Finding | Disposition | Required implementation / gate |
| --- | --- | --- |
| R0-01 | accept | New anchor version4 explicitly binds trusted-native-runtime mode and launch contract hash, 100800000ms total cap, immutable predecessor v2 stop27/tail28 and Correction-06 evidence, original approval/work, current candidate/input, actual accounting and prior attempt floors. v3 was proposed code, never activated: actual current anchor remains v2. Retain v1–v3 historical validation. Python/Rust share canonical positive/negative fixtures. Existing7 refers to Owner's later conditional amendment, not the historical validator. |
| R0-02 | accept | v4 run_deadline_ms is approval+43200000ms; effective remaining is min(activity cap, run deadline). Driver stage entry/exit records and bounded runner enforce P45/A240/B90/C140/D120/E45 minutes, plus total/segment and reserves. Previous A remains in cumulative usage; A240 starts at this transition's A entry. No fresh total budget. |
| R0-03 | accept | v4 correction subjects require class=source or content. Source cumulative6 (prior4 + new2), content2, total8. Preserve post-stop attempts through a bound nondecreasing prior_attempts accounting floor; do not rewrite predecessor rows. Correct the execution metadata's inherited source_correction_additional=3 to2 before implementation. |
| R0-04 | revise | Local native requirements/system/managed files: loaded or absent-confirmed by native loader plus filesystem metadata; unreadable/unknown fails before auth. MDM/config preferences: native synchronized loader and layer provenance jointly establish observed loaded/absent; AppSynchronize alone is not absence/success evidence. Existing loader errors propagate. Cloud unavailable-until-auth is the only deferred mandatory source; stage1 failure stops before catalog/generation. No native loader replacement or additional preference probe. |
| R0-05 | accept | Capture AUTH config/auth/secrets/rules metadata only (dev/ino/size/mode/mtime_ns/ctime_ns and entry names) before/after start, reject changes; no credential content hashing/copying. Observe known outside-task runtime path existence and combine native auth violation counter. Metadata and code counter are limited observations, never OS immutability proof. |
| R0-06 | revise | A fixed30s initial authentication/startup timeout, no retry/refund. Timeout is startup-interaction-unavailable, possible Keychain interaction, not a reproduced Keychain prompt. Config-only occurs before AuthManager creation. Owner must not approve any Keychain dialog; reject or leave unanswered. Do not click/alter ACL. |
| R0-07 | accept | Before notify=[] only user-layer notify may be suppressed. Reject other source layers with notify. Freeze notify and all config-layer origins/disabled reason/key inventory; tests cover system and managed notify, user drift and successful disable. |
| R0-08 | revise | No arbitrary failure is downgraded. Existing deliberate pre-seal editing checkpoint+confirmed process-ended is the only no-Work-stop runtime exit (closed list of one); it is successful bounded suspension, not a failed turn. H05 intentionally kills the isolated Core apply subprocess under the trusted H05 harness after exact packet binding, without failing run_live_command. It records pending/death, pauses for exact Owner replay. Runtime/auth/policy/transport/unclassified failure still stops the Work, makes remaining slot unavailable, and requires Owner disposition. No automatic epoch reset. |

Optional O1: spec version2 and explicit launch_mode/launch_contract_sha256; tool profile keeps its existing profile name, host runtime no longer uses an OS profile field in native mode. O2/O4: report guard-route scope and trusted runtime direct-write limitations. O3: include all native layer provenance. O5: clarified above. O6: freeze mapping and launch contract before auth and include in final R1. O7: arithmetic verified only, actual accounting remains Driver evidence.

These dispositions refine the already-approved criteria without restoring withdrawn runtime OS guarantees or authorizing new files, permissions, retries, calls or source slots. All implementation gates are pending until executed. R0-04 inability to establish local native policy still stops the run. R0-08 does not promise that a failed first runtime can use slot2.

P completed 2026-10-24T02:50:07.496952+00:00; total active 953.178 minutes; A deadline 2026-10-24T06:50:07.496952+00:00. No new source bundle/build/runtime/auth/provider used yet.


## Native Transition A — Proxy 집중 검사 상한 도달 (2026-10-24)

현재 승인 범위와 source 보정 총8, 누적28시간·이번12시간·A240분 및 나머지 모든 한도는 유지한다. 해당 집중 검사 묶음의 실행 횟수만 2→3으로 한 번 늘리는 결정이 필요하다. native config-only2/2와 native-binding2/2는 추가하지 않는다.

첫 proxy 검사는 macOS recvmsg에 control buffer가 없으면 예상한 MSG_CTRUNC 없이 ancillary FD가 버려질 수 있어, 금지된 ancillary 응답이 수락되는 결함을 재현했다. 모든 수신 FD를 먼저 소유하고 거절 시 닫는 기존 로직을 release acknowledgement에 적용했다. 두 번째 검사는 그 보정 과정에서 CMSG_FIRSTHDR/CMSG_NXTHDR에 남은 변수명 message 때문에 컴파일에 실패했다. 두 곳을 현재 변수 msg로 바꾼 수정본을 준비했고 세 번째 호출은 하지 않았다.

- 검토할 수정본: runtime worktree codex-rs/network-proxy/src/prepared_fd.rs. SHA-256 `2bccdb7293b59a4fc37d100d29fa9b6b10b85a477c25dc08d73d40089c372d75`.
- 실행: 기존 scripts/run-focused.py의 proxy selection을 proxy-lifetime-03 label로 정확히1회. 기존 sandbox/profile, offline/locked cargo, 작업용 temp/log 위치를 유지한다.
- 예상: 활동2–5분. 두 이전 호출의 실측12.34초·3.64초에 추가 compile/link와 결과 확인 시간을 판단으로 더했다. 대기/기록을 포함하고 다른 작업과 겹친 시간은 한 번만 센다.
- 중단: 이번 검사10분 또는 기존 A/segment/누적 한도에서 보존 reserve를 뺀 값 중 먼저 도달하는 값. 추가 실패는 재실행하지 않고 보존·보고한다.
- 통과하면 기존 승인된 나머지 A–E로 복귀한다. 합성 wire harness 첫 compile은 tempfile extern 누락으로 실패했고, 이미 build된 동일 의존성을 연결하는 수정 runner를 준비했다. 이 harness의 기존 허용 보정 후1회는 남아 있으며 새 제품 dependency/lockfile 변경은 없다.
- 실제 인증/모델/대상 문서 변경0, 새 후보 build0, 새 live/proxy phase start0. H05/H10 exact 승인과 최종 Owner 수락은 유지한다.

현재 native 설정 사전검사 PASS, Python native 계약/예산3 PASS, native launch Rust1 PASS, host FD2 PASS다. 새 v4 shared fixtures는 Python11개(정상1/거절10)를 생성했고 Rust parity와 Owner pause를 포함한 v2 추가fixture는 아직 실행하지 않았다. 실제 Rust proxy/SSE 통합, worker H03 후속, 최종 후보/offline/live/H05/H10/R1은 미완료다.

source8개 복구본은 recovery-proxy-focused-stop에 원문 byte와 mode를 대조해 보존했다. 이전 실패·장부·후보·원 profile은 유지한다. 현재 task source/cache/입력은 승인 후 구현·검증과 최종 R1의 구체 소비자가 있으므로 삭제하지 않았다. 활성 경로 이동·삭제는 없다.


### Owner 결정 — proxy 집중 검사1회 추가

2026-10-24T03:32:06.606294+00:00에 Owner가 “검사 1회 추가 승인, 통과하면 계속”으로 exact 제안을 승인했다. 질문 ID call_312c17c5bca7453c9be3421b8d353c1c. 해당 묶음만2→3회, 추가검사10분/기존 단계·누적 한도 중 먼저 닿는 상한을 적용한다. 나머지 source/live/config/review 한도와 H05/H10·최종 수락 조건은 유지한다.

### Native transition A local gate checkpoint 2026-10-24T03:46:07.419722+00:00

Owner 추가 승인 proxy focused3/3 PASS (7.505s), process group absent. 기존 compile-only 보정2/2 PASS. v4 공통 clock12개(accept2/reject10) Python/Rust parity PASS. Core guard11 PASS. Synthetic actual wire 최초 실패는 기존 DNS precheck와 FD-only 경로의 충돌로 판정하고 전용 entry/test의 중복 DNS 사전검사만 제거했다. 공개 peer:443/SCM_RIGHTS identity 검사는 유지하고 OS 권한은 추가하지 않았다. 보정 후 wire2/2 PASS: 정상2, truncation/extra/duplicate 거절3, release5, 양 process group absent. Worker 첫 시도는 입력 wrapper extraction KeyError로 실제 child0; 보정2/2 PASS: 실제 worker positive5, protected read6+verifier write 거절1, 동일 Python/role profile IPC probe2. Probe를 실제 worker API로 과장하지 않는다. 실제 auth/provider0, H03 전체와 live 적격은 아직 미완료. 근거: private-evidence/E097}. 누적 활동 1005.433분; A/12h/28h 상한 불변. [공개용 중립화]


### Native Transition A Completed / B Entry 2026-10-24T04:01:09.486414+00:00

후보 build4와 변경 영향 offline5, 공통 clock12, journal5, Core11, host8, 실제 합성 wire5 및 lease release5, worker positive5/negative9를 확인했다. 고정 candidate/source는 build 뒤 동일하다. 새 v4 epoch는 기존 stop27/tail28과 누적 시도를 보존한다. 전체 필수 local gate를 통과해 기존 조건부 승인에 따라 B를 시작한다. B 중단시각은 2026-10-24T05:31:09.486414+00:00이며 인증/policy/transport/runtime 실패는 재시도 없이 중단한다. 실제 인증·provider 검증과 H05/H10·최종 수락은 아직 완료되지 않았다. 정확한 기록: `private-evidence/E095`. [공개용 중립화]


### Native B Stopped Before Runtime 2026-10-24T04:04:43.535252+00:00

Driver의 native launch file 검증이 private control-file 조건을 executable0755와 role template0644에도 적용해 실패했다. 합성 fixture0600만 사용한 검증 공백이다. s4-02 proxy는 소비했지만 runtime/auth/provider 추가0, pending apply 없음, lease0, proxy/controller 부재를 확인했다. 원본 파일 권한·source는 수정하지 않았고 재시도하지 않았다. epoch stop18 및 기존 실패/시도는 보존한다. 마지막 source 보정·v4-stop18 전용 v5 복구·추가 proxy1(누적4)의 미실행 제안: `private-evidence/E027` (SHA-256 `8d66e7e6708b7a458e1d1f1f24a131395dc98e6b5efba6984647228bd273a2f2`). 기존 B/12시간/누적28시간 상한은 유지하는 안이다. 새 권한과 최종 수락은 아직 없다. [공개용 중립화]


### Input Gate Recovery Authorized / Local Gates Passed 2026-10-24T04:22:09.436448+00:00

Owner가 마지막 source 보정·이번 중단 한정 복구·proxy 누적4를 직접 승인했다. 원문과 고정 제안 hash는 `private-evidence/E029`에 보존했다. Source6/8(source 잔여0, H10 content2 유지), build5/5를 사용했다. Host/Rust 실제 권한 binding 각2 tests와 v4/v5 공통28 cases, 최종 build5, 영향 offline normal/restart3가 통과했다. Actual input preflight가 executable0755·worker/verifier0644·proxy0600을 hash/owner/alias 조건과 함께 검증했다. v5는 기존 v4 stop18과 bytes·사용량을 보존하며 아직 실제 auth/provider0이다. 복구 중단05:09:26Z, B종료05:31:09Z, 원래12시간/누적28시간 상한은 유지한다. [공개용 중립화]

추가 실패 보존: setuid fixture가 실제0755로 생성돼 요청/관측 mode를 분리한 최종2차 binding PASS; 첫 parity는 기존 pretty JSON failure receipt의 canonical 불일치, 원본 보존 및 값 동일 canonical input 후2차 PASS; build5는 실제 컴파일 PASS19.384초 뒤 기존 summary의 exclusive write 충돌, 새 build5 result를 직접 참조하고 재빌드하지 않음; offline1은 구 build summary 해시 참조로 child0, 수정한2차3 cases PASS48.867초. 정책·OS 권한·credential 변경은 없었다.


### Native Clock Stopped At Catalog TCP Connect 2026-10-24T04:27:03.442154+00:00

파일 권한 gate 보정·v5 exact 복구·최종 local checks는 통과했지만 actual clock은 models endpoint TCP connect5001ms TimeoutError로 중단됐다. 원인은 네트워크 계층으로 한정해서 추적되며 서비스/라우팅/정책 중 구체적 원인은 미확정이다. Native auth load/expiry 관측1, policy known-not-applicable, auth-boundary violation0, AUTH metadata 전후 동일. Control reservation1/FD-issued0/model thread·turn·generation0. Runtime/proxy/controller 종료와 lease0을 확인했다. 다른 IP나 경로 재시도는 하지 않았다. Source6/6·build5/5·clock start2/2 소진, proxy3/4의 남은1은 H10 전용이다. Top-level auth read 횟수는 계측이 없어 unavailable로 수정하고 관측 admission1을 별도로 기록했다. 원래 raw 결과·journal은 보존했다. H05/H10·최종R1/Owner 수락은 미완료이며 추가 실행 없이 중단한다. 상세 보고: `private-evidence/E032`. Source/필수 evidence는 보존, closed task socket2 및 빈 directory2만 확인 후 제거, active path 변경 없음. [공개용 중립화]


### Limited Network Diagnosis / Recovery Proposal 2026-10-24T04:42:45.700724+00:00

Owner “승인” 후 자격 증명 없는 TCP 확인2회를 수행했다. DNS의 기존 첫 IP172.64.155.209는5.003초 timeout, 두 번째104.18.32.47은0.0096초 connected/peer verified였다. 두 route는en0. TLS/HTTP/auth/model 추가0, production 시도·source/candidate/epoch hash 불변, 진단 process/소켓 종료 확인. 원격 서비스/라우터/정책 중 세부 원인은 미확정이며 TCP 성공은 provider 성공이 아니다. 실제 실행은 계속 B-stopped다. 준비한 exact v5-stop15/tail16 복구안은 source7/총보정9,build6,clock3/live7,proxy5,B150분을 제안하며 기존12h/28h 유지·복구60분 중 먼저 닿는 상한이다. 새 수치/소스 변경은 아직 승인·실행하지 않았다. 제안 private-evidence/E028 SHA 816c0d647567d2c090d327b608a55636964b7e63ad5fa363f0d99ab11d28a249. 원본 증거와 source/build5는 Owner 결정·qualification/final R1 소비자가 있어 유지하고 이동/삭제0. 누적 활동1062.071분, 잔여617.929분; 확인 안 된 대기 차감0. [공개용 중립화]


### Network Recovery Authorized / Local Gates Passed 2026-10-24T04:55:48.050230+00:00

Owner가 exact 네트워크 복구안 SHA816c0d647567d2c090d327b608a55636964b7e63ad5fa363f0d99ab11d28a249를 “승인”했다. source7/총보정9,build6,clock3/live7,proxy5,B150분(06:31:09Z),복구60분(05:44:27Z)과 기존12h/누적28h 중 먼저 도달하는 한도를 적용한다. 변경3파일은 이번 v5 stop15/tail16의 auth 관측1/control1/모델0을 보존하고 clock03·s4-04만 추가했다. Host network3/Rust network2 PASS, 새v6 37+기존28=65 공통판정 PASS, build6 PASS17.184초, offline normal/restart3 PASS48.672초. 기존 v5 bytes 유지, build5 binary3/source3 복구본 대조 완료. 실제 DNS/모델 재실행은 아직0. 현재 proxy FD capacity는 기존 계산의 더 작은36을 유지하며 확대하지 않는다. 원래 권한/시간/사용량을 보존했고 이제 승인된 단회 clock으로 넘어간다.


### Native V6 Stopped At Proxy Preface / Driver Omission 2026-10-24T05:00:53.781330+00:00

새 clock-03을 host/app budget에는 반영했으나 proxy bind_stream allowlist의 clock01/02 제한을 Driver가 범위 조사에서 놓쳤다. 실제proxy prepared connection failed/runtime stdout closed, FD reservation/issued0/model0. 단회18.630초,auth admission이번1/누적2(storagecalls unavailable),metadataequal/violation0. runtime26351/proxy26336/controller26314부재,lease0 확인. 기존v5/새v6stop15/tail16·source/build6불변 확인. source7/7 build6/6 clock3/3소진;proxy4/5남은1H10전용;offline21. source추가/재빌드/재실행0. closed task socket1+빈dir1만삭제,activepath이동0. 상세결과·미실행5파일복구안 private-evidence/E033 SHA 6f946235d6999fd1d8275b5027f1734d5c038ee62896b1e3e7cd728275e9c420. 새source8/총10,build7,clock4/live8,proxy6와복구45분은제안일뿐현재한도는변경하지않았다. 누적활동1080.206분/28h,잔여599.794분. [공개용 중립화]


### Native V7 Actual Synthetic Proxy Gate — 2026-10-24T05:13:45.807554+00:00

Owner의 2026-10-24T05:04:12Z 직접 승인에 따라 총5파일 보정과 source8/전체10(H10 content2 유지),build7,clock4/live8,proxy6을 적용했다. b-preface-recovery-authorization.json에 원문·제안 hash·복구 종료05:49:12Z를 기록했다. B 종료06:31:09Z/이번12h 종료14:35:42Z/누적28h와 기존 실패·사용량을 유지한다. 수정 전5소스와 build6 3실행 파일을 before-preface-recovery에 byte 검증해 보존했다.

새 clock04 producer/Host/Rust epoch/proxy preface/broker/release 소비자를 대조했다. 첫 proxy 집중 검사는 wrong-phase 음성을 통과시키는 결함으로 FAIL(18.224초); 동일 보정묶음에서 s4 clock/synthetic 및 s6 H10의 tuple 검사를 추가한 허용된 두 번째 검사6 PASS(5.733초). Host6 PASS, Rust network/native launch3 PASS(80.924초), v7 34+이전65=99 공통 fixture Host/Rust parity PASS(1.701초). 실패를 삭제하거나 환불하지 않았다.

새 실행 ID 실제 경로: pipeline-wire-v7에서 실제 PreparedUds→실제 proxy→localhost 합성 TLS→Responses parser→Host release, 정상2/잘린응답·extra·duplicate거절3 PASS(1.905초). release-events에 clock04 2회와 전체5 release가 기록되었고 양쪽 process group 부재/lease0 확인. 기존 client 테스트는 start를 clock01로 덮어써 task-owned fixture의 complete start만 clock04로 치환했다. 생산 transport 소스 복사본 bytes는 원본과 동일하며 fixture·원본·binary hash를 기록했다. 실제 credential/provider0이며 live 성공으로 해석하지 않는다. build7 1회는 진행 중, 실제 epoch-v7 및 인증 실행은 아직0. 누적 활동1093.073분/28h,잔여586.927분.

보존: source/worktree/build6 복구/이전 epoch와 실패·신규 고유 검사결과는 후속 qualification/R1/Owner 판단 입력이다. active path 이동0. 실행 종료된 합성 socket은 runner가 정리했고 그 외 삭제0.


### Native V7 Proxy Qualified / Model Encoding Stop — 2026-10-24T05:24:39.279071+00:00

승인된5파일·새clock04 실제합성경로 및 Host6/Rust3/proxy6/shared99/build7/offline3 PASS. 실제clock04는19.663초에 native catalog 반환 뒤 required model unavailable로 종료. stderr34bytes/SHA가 해당고정오류와정확히일치한다. FD1 issued/released,control누적3/auth admission관측누적3,storagecalls unavailable,model thread/turn/generation0,auth metadata동일/violation0,process/group부재·lease0. 로컬cache의gpt-6-astra는Lite=true이며후보normal-only가정과충돌하지만fresh응답필드전체는미기록이다. 이결과를live전체PASS로표시하지않는다.

source8/8 build7/7 clock4/4,proxy5/6의잔여1은H10전용,offline24/36. 후속실행0. b-v7-stop-report.md에결과와미승인9파일Lite보정·추가한도·B240예외제안을구체화했다. 제안SHA b2d44fdfc895bf105b78000a3433e2ba6faae158e34b3d82a6166772a02aaa66;현재B150/12h/28h와기존limits는변경하지않았다. 현재누적활동1103.964분/28h,잔여576.036분. H01–H10/최종R1/Owner수락은미완료다.

보존: source/worktree·build7·source/build6복구본·모든epoch와고유결과는후속qualification/finalR1/Owner처분입력. 삭제: 종료된cfnt7/s4.sock과검증한빈cfnt7dir각1. active경로변경0. 소스commit/push/PR/WorkDone0.

V7 final accounting 2026-10-24T05:25:35.119146+00:00: actual source count8 및 epoch correction-source8은 이미 맞았고, 파생 요약 new_source_corrections_used만 이전3에서4로 대조 수정했다(전환 이전4+전환 이후4=8). 실행/한도/실패 환불은 없다. 누적활동1104.895분,잔여575.105분. 추가 runtime/provider/source/build0, 후속 Lite 제안은 미승인이다.

## Native Lite Recovery — Local Checkpoint 2026-10-24T05:38:15.257918+00:00

Owner direct messageprivate-approval/O021(2026-10-24T05:27:58Z)는 b-v7-stop-report.md SHA b2d44fdfc895bf105b78000a3433e2ba6faae158e34b3d82a6166772a02aaa66의9파일 native normal/Lite와 exact v7-stop 복구를 승인했다. source9/전체보정11(H10 content2),build8,clock5/live9,proxy7; B240분 종료08:01:09Z,이번12h14:35:42Z·누적28h 및 기소비를 유지한다. 복구 expected35–60분(판단),stop75분06:42:58Z이며 대기·보고 포함,중복시간1회,Owner대기공제0이다. H05/H10 exact와 최종수락은 여전히 별도다. source9 예약,source9파일과 build7 binaries의 byte 검증 복구본 before-lite-recovery를 보존했다. [공개용 중립화]

Native catalog의 encoding을 snapshot/manifest→consume→exact AdditionalTools prefix/ID→API header→최종 HTTP guard에 결속했고 Lite U2 함수 namespace를 검증한다. normal/Lite callback은 같은 native DynamicToolHandler의 원 namespace로 Host에 도달한다. 선택 catalog의 비민감 eligibility만 별도 기록한다. 새 모델/계정/provider/의존성/정책/auth 저장소 변경0이다.

App focused18 PASS4ignored; Host 최초5검사에서 fixture 함수명·기대계산 두 테스트 오류가 실패했고 명확한 수정 후5 PASS했다. 실패 기록 유지. Host v8 34사례(정상6/거부28) 예상 판정 완료,기존99 공통 Rust parity는 다음 검사다. Core/proxy/실제 normal-Lite wire·build8/offline4/liveclock05는 아직 미완료. script implement-v8 최초 실행은 쓰기 전 exact string assertion 실패로 source변경0이었고 수정본02로 적용했다. 일부 v7 cap이 준비 중 넓어지는 것을 발견해 실행검사 전 이전 의미로 복원했으며 공통 parity가 확인한다.

누적활동1117.564분,잔여562.436분. 현재 provider/auth/live 추가0,Git publication0,source/status Done0. 기존 worker/verifier/auth/transport/parser 중 영향 없는 bytes·정상 증거는 재사용하며 전체 suite 필요성은 누적위험 기준으로 C에서 판단한다. 보존 consumer는 qualification/후속 R1/Owner exact 판단이고 승인된 closeout까지 유지한다.

### V8 local gates 2026-10-24T05:48:55.598610+00:00

App18,Core12,Host5,proxy6 및 v8 34+기존99=133 Host/Rust parity가 통과했다. Core 최초 검사11PASS1FAIL은 기존 합성 manifest의 encoding 값 누락이며 cfg(test) 입력을 명시한 허용 보정 뒤12PASS다. 실제 source-linked UDS/proxy/TLS/API parser 경로는 clock05 normal2/Lite2와 두 encoding의 잘린·추가·중복 응답 거부6,총10요청/10FD해제를 검증했다. 최초 wire 실행은 client10요청과 해제 완료 뒤 proxy test의 이전 기대값5 때문에 FAIL했고, test-only expected_requests10을 packet에 결속한 마지막 허용 실행이 PASS3.927초다. 기존5요청 fixture와 제품 proxy 동작은 바뀌지 않았다.

Build8 PASS131.612초,source/기존 기준binary변화0. Offline normal/Lite/restart-before/restart-after4 PASS63.684초,누적offline28/thread29/turn23으로 기록했다. v8 epoch생성은1회이고 exact v7 bytes 불변이다. 실제clock05 단회는 별도 실행 중이며 localPASS를 실제 native qualification으로 올리지 않는다. 기록 v8-local-gates.json.

정리: 두 종료된 합성 socket만 process부재+lsof미사용 확인 후 삭제했다. 활성경로 이동0,기존 소스·build7 복구본·실패/성공·입력은 qualification/R1/Owner 판단을 위해 유지한다. 회복안75분/B240분/12h/28h 및 H05/H10 exact·최종수락 조건은 동일하다.

### V8 actual-clock stop 2026-10-24T05:52:06.107817+00:00

clock05는19.931초 뒤 Host unknown native notification으로 중단했다. native catalog에서 gpt-6-astra present/Lite/xhigh/usable context=true를 이번에 직접 확인했다. initialize 응답 이후의 보호 metadata 검사1과 종료 후 검사1이 모두 이전과 동일하다. 현재 LiveClient는 수신 method 목록을 메모리에만 보관하므로 실제 unknown method는 unavailable이다. Source상 initialize 뒤 remoteControl/status/changed를 무조건 전송하고 Host allowlist에는 없다는 것은 확인했지만 실제 packet identity로 확정하지 않는다. 추가실행/재시도/allowlist/source변경0이다.

누적runtime start/entered5,control4,auth admission관측4,credential storage read 호출횟수unavailable. 이번FD events={"controller-closed": 1, "controller-ready": 1, "fd-issued": 1, "fd-released": 1, "fd-reserved": 1, "proxy-launched": 1, "runtime-bound": 1},leases0. modelthread/turn/generation/dispatch/authority/seal0. controller/proxy/runtime부재,authmetadata동일,oldv7와build8 source/binary불변을 검증했다. v8stop18/tail19를 보존한다. 중복stop 추가시도는 이미stopped여서 거부됐고 budget_stop_unavailable=true는 기존stop18의 손실을 뜻하지 않는다.

닫힌cfnt8/s4.sock과확인된빈cfnt8 directory만 삭제했다. 활성경로이동0,고유소스/복구/실패·성공증거는 qualification/R1/Owner 판단까지 유지한다. 현재 source9/9·build8/8·clock5/5를 소진했고 전체보정11중2는H10내용전용,proxy6/7의1은H10전용이다. 후속source/live는새승인전실행하지않는다. 누적활동1131.411분,잔여548.589분,Owner대기공제0.

V8 follow-up proposal 2026-10-24T05:54:18.182606+00:00: b-v8-stop-report.md SHA a606aabd45b2c921907323e076822e50cf3bc69cca7e5b6c62cd2b16087a00be을 준비했다. 초기화RPC전체합성검증과5파일/source10총12/build9/clock6live10/proxy8,예상20–35분·중단45분을 제안한다. 기존B240/12h/28h 및H05H10조건유지이고 미승인·미실행이다. 현재source9/build8/clock5/proxy6 및현재상한은바꾸지않았다. 누적활동1133.612분,잔여546.388분.


### Native Initialization RPC Local Stop — 2026-10-24T06:21:09.698920+00:00

Owner 승인된5파일 source10 진행. Host 최초 import 실패 후5 PASS,App 최초18 PASS/proxy6 PASS/Host-Rust167 PASS/clock06 normal-Lite 합성wire10 PASS. 실제 build8+현재Host RPC normal은 emittedAtMs schema 누락,보정 뒤Lite는 prepare 중 deprecationNotice로 중단했다. legacy CLI 보정의 App 후속은 sqlite gate17 PASS/1 FAIL이며,7개 default-false 키에 한정한 최종 수정은 추가검사 없이 보존했다. 따라서 최신source/초기화전체는 미검증이고 build9·actualclock06·새auth/provider는0이다. Native accounts/check background/routing sender가 현재 guard와 맞지 않는 정적경로를 발견했다. 새endpoint 허용과8파일/source11·총13의 후속안은 미승인이다.

Evidence: private-evidence/E096 proposal: private-evidence/E034 실제v8 epoch/기존실패·사용량 유지,source10/build8/offline30/live5/proxy6,모델thread/turn/generation0. 별도예약offline30/thread31/turn23은 다음epoch에 반드시carry한다. B08:01:09Z/12h14:35:42Z/누적28h와 H05/H10 exact조건 유지. 고유소스/build8/복구본/결과는후속qualification·R1·Owner판단용으로보존;활성경로변경0;종료합성socket1만삭제. Work Done/Git publication 없음. [공개용 중립화]


### Account Bootstrap Local Checkpoint — 2026-10-24T06:47Z

Owner approved the exact eight-file upper bound, source11/total13 and the existing unused build9/clock06 slots at 06:27:08Z. Follow-up ends07:12:08Z; B still ends08:01:09Z, segment14:35:42Z, cumulative28h and all prior failures/counters remain. Six of the eight source paths changed; proxy source is unchanged and its clock06 wire evidence is reused. The account GET is an exact no-body/no-query endpoint with a mutex-protected one-time durable control reservation. Native BackendClient header shapes before/after initialization, account cache/coalescing, Host metadata-only account notification admission and pre-thread routing validation were added. Native routing is read without refresh and must select the approved origin; its account result is never persisted or forwarded.

App22, Host focused tests, native BackendClient before/after header test and Host/Rust201 budget cases passed. Version10 binds this approval/source11 to the same actual v8 stop18/tail19; unactivated v9 records retain their old meaning. HTTP attempt1 failed compiling an unrelated existing client.rs test initializer missing max_requests. Attempt2 did not enter its test because the Driver's harness executable TARGET parameter was wrong. Owner separately approved exactly one more execution; corrected exact harness3 passed account GET UDS/TLS status200/302/401/503 with no redirect/retry. The current prepared_uds source and tests were copied byte-for-byte into that harness; this does not claim the entire HTTP crate test suite passed.

Build9 is running, not yet qualified. The next authorized check is one normal/Lite pair using the new binary, actual native BackendClient/AccountRequestProcessor, synthetic credentials and loopback account responses through full stdio initialization and generation. The native UDS/FD/TLS layers have separate evidence; the loopback RPC fixture is not a claim that all production boundaries ran in a single process chain. No new actual authentication/runtime/provider effect has occurred. H05/H10 exact approval and final Owner acceptance remain open. Durable checkpoint: existing native-runtime-transition/resume.md and execution.json; no Work Done or Git publication.

### Bootstrap V10 local stop 2026-10-24T06:54:48.948437+00:00

HTTP 추가1회 PASS; build9 PASS117.944초, source/binary 불변. 전체 합성 normal은 Core의 home/auth.json 금지로 초기화 전 exit1이다. 56byte stderr hash가 정확한 오류문과 일치한다. Lite 미시작, 합성 GET0, 실제 auth/provider 추가0. offline누계31/thread31/turn23; source11/build9/live5/proxy6/control4/auth admissions4/model0 유지. 양쪽 repo diff-check PASS.

중단보고 private-evidence/E030 closeout private-evidence/E035 소스/build/epoch/복구본 검증·보존,삭제0/이동0/활성경로변경0. 후속은 fixture 한정 ephemeral 합성 인증,3파일/source12총14/build10/집중검사+normalLite2,예상15–25분·새30분 상한을 제안 중이며 미승인이다. 기존B240/12h/28h,H05H10 exact 및 최종Owner조건 유지. 실제 clock+B 후속에 필요한65분이 B에 남지 않으면 실제 호출하지 않는다. 누적1194.125분/잔여485.875분,Owner대기공제0. [공개용 중립화]

### Fixture Ephemeral Recovery Checkpoint 2026-10-24T07:02:31.682769+00:00

Owner는 source12/총14/build10 및 새30분 상한을 직접 승인했다. 승인 관측06:56:52Z,종료07:26:52Z이며 기존B08:01:09.486414Z/12h14:35:42Z/누적28h 중 먼저 닿는 조건 유지다. 예상15–25분(기존build118초·합성19초+구현판단),대기·보고 포함,겹침1회,Owner대기공제0. 변경 전3파일/build9 3binary를 before-fixture-auth-recovery에 byte검증 보존했고 source12를 예약했다.

실제 변경은 app lib.rs와 Host2파일이다. 명시적 fixture만 고정 합성 ChatGPTAuth를 기존 Ephemeral 저장소에 넣으며 실제credential 입력을 받지 않는다. Core auth.json금지·live readonly auth 구현은 그대로다. 신규v11은 actualv8 exactstop18/tail19와 source12/build9이상/offline31/thread31/turn23/기존effect를 이월하며 v1–v10의 의미와 입력은 유지한다. App첫검사24PASS4ignored,Host첫검사6PASS,Host/Rust235사례PASS. 이전HTTP/Backend/proxy/worker/verifier 영향 없는 증거 재사용; 전체suite 반복근거없음. build10 실행 중,전체normal/Lite2는그다음한번만실행한다. 현재실제auth/provider추가0이며 실제clock+B에필요한65분이남지않으면호출하지않는다. H05/H10 exact·최종수락·R1미완료조건유지. 누적1201.837분,잔여478.163분.

### Fixture Auth V11 Stop 2026-10-24T07:07:12.461629+00:00

App24/Host6/공통예산235 PASS,build10 PASS25.474초. 전체normal은initialize후account/read에서거부됐고17.563초후정리했다. auth.json미생성,합성GET0,이번thread/turn0,Lite미시작,실제auth/provider추가0. Core RPC 목록에account/read가없고raw/typed gate가이를검사한다. 원error code/message는저장되지않아unavailable이며재실행0이다. 범위밖Core/message_processor를수정하지않았다.

private-evidence/E031 및 fixture-auth-v11-closeout.json에결과/5파일후속안(source13총15/build11,시간연장없이기존07:26:52Z끝)을준비했다. 미승인이다. 실제호출은전체합성실패및B잔여53.95분<필요65분으로시작하지않는다. source12/build10/offline32/thread31/turn23/live5/proxy6/control4/authadmission4/model0,이전실패와exactv8불변. 누적1206.517분/잔여473.483분,Owner대기공제0. source/build/복구본/고유증거검증보존;process부재,삭제0/이동0/active경로변경0. H05H10 exact/최종수락/R1미완료유지. [공개용 중립화]

### Account RPC Recovery Checkpoint 2026-10-24T07:13:46.897131+00:00

Owner는Core/RPC포함5파일/source13/총15/build11을승인했고 실제호출을명시적으로금지했다. 이전07:26:52Z종료/B240/12h/28h 및실패·사용량/H05H10유지다. 변경전5파일/build10을byte검증보존한뒤source13예약했다. 추가누락경계점검은account-rpc-boundary-audit.json에기록했다. raw exactrefreshfalse/typed phase·단회·mutex·실패후thread거부,계정응답schema/routeenum,bootstraploopback및Corein-memorymodeltransport를대조했다. 실제체인성공은아직아니다.

첫App26/Host7/Host-Rust269사례PASS,build11진행중. Core변경은RPC허용목록account/read1개이고actualauth파일금지/readonly auth/HTTP/provider정책은유지한다. v12는source13/build10이상/offline32/thread31/turn23을actualv8exactstop에서이월한다. 다음은고정build11의normal/Lite합성2회,실패자동재시도없음. 누적1213.091분/잔여466.909분,Owner대기공제0.

### Account RPC V12 Stop 2026-10-24T07:19:22.737625+00:00

App26/Host7/공통269PASS,build11PASS56.559초. 전체normal은계정GET1회·account/read응답검증·thread/start까지통과했다. turn/prepare중warning1회로18.378초후중단,Lite미시작/모델생성0/실제authprovider추가0이다. 경고본문은RPCmetadata에보존되지않아unavailable이고합성logs DB의WARN/ERROR도0행이다. 경고종류·단계·기존corestartup후보정적경로만확인했으며본문원인을단정하지않는다.

현재source13/build11/offline33/thread32/turn23,이전사용량·실패/actualv8불변. 소스·바이너리·복구본hash검증/process부재. 삭제0/이동0/active경로변경0. 경고만기록하고중단하는build11재사용단회합성진단(예상30초/최대3분,sourcebuild추가0,모델생성0,실제호출0,기존07:26:52Z끝유지)을warning-diagnostic-proposal.json에준비했고Owner응답대기다. 실패전체검증재시도는자동실행하지않는다. 누적1218.688분/잔여461.312분,Owner대기공제0.

### Warning Diagnostic Approval After Deadline 2026-10-24T07:29:12.759905+00:00

Owner는단회경고진단을승인했으나확인시각이기존고정종료07:26:52Z를지났다. 진단미시작,offline33/source13/build11그대로,실제호출0. 시간상한을임의로연장하지않았다. 진단자체승인은보존하고해당진단만새승인부터최대3분(B/12h/28h중먼저닿으면중단)예외가필요한상태로기록했다. 실패·사용량환불/Owner대기공제0,누적1228.522분/잔여451.478분. 기존소스·증거·복구본의consumer/retention조건동일,삭제0/이동0.


### 2026-10-24 MCP 비활성 목록 보정 승인

Owner가 6개 파일 보정, source17/total19/build13/offline41/live11/proxy9 및 clock-07 1회를 승인했다. 기존 절대 마감·28h/12h·실패 중단·H05/H10 exact 승인과 최종 수락은 유지한다. 설정 보존과 시작/도구 계획 빈 목록 검사의 충돌을 함께 고친다. 집중 검사와 후보 normal/Lite를 사용하고 영향 없는 기존 증거를 재사용한다. 예상 local25–45분/상한60분, actual45–70분/상한90분이나 기존 절대 마감이 먼저 적용된다. 인증·네트워크 호출 전 로컬 gate가 필요하다. 근거: private-evidence/E037 [공개용 중립화]


### MCP17 local gates 2026-10-24T08:54:32.647010+00:00

6파일 보정 후 Host17/Rust26, 새38+기존정상10=예산48 Python/Rust 판정이 통과했다. build13 58.656초, normal/Lite 각1회 34.918초 PASS. offline41/thread40/turn30으로 이월한다. source17/전체19 및 H10 내용2회 잔여를 유지한다. 기존 epoch13 실패·사용량·build12 바이트와 소스6파일 복구본을 보존했다. 자료 준비 중 parent 경로/0600 모드 오류2건은 실제 호출 전 실패로 남겼다. source 마지막 보정은 failed thread예약1/runtime6/control6 승계이며 추가 bundle을 쓰지 않았다. 실제 경로는 아직 미검증이다. private-evidence/E038 [공개용 중립화]


### MCP17 actual preparation stopped 2026-10-24T08:57:41.810384+00:00

6개 파일의 MCP 목록 계약 보정과 로컬 검증은 통과했다. 실제 clock 실행 준비는 task helper의 proxy 누적 횟수 사전조건 누락으로 중단했다. Driver가 이전 값6을7로 갱신하지 못했고, 사용량7을 보존한 장부가 올바르게 거절했다. 모델·인증 실패가 아니다. runtime/proxy 시작 전이므로 MCP 보정의 실제 native 전체 경로 성공은 아직 입증하지 못했다.


source17/build13/offline41/live6/proxy7/control6/auth admission5를 유지했다. runtime·proxy·인증·model 추가0, DNS1. epoch14 seq1 stop 보존. source/binary/이전epoch 불변과 controller부재 확인. 빈 taskdir9개만 삭제, 증거파일 삭제0/이동0. H05/H10 및 최종수락 미완료. 상세 private-evidence/E039 [공개용 중립화]


### MCP18 Local Failure — 2026-10-24T09:12:29.296272+00:00

MCP18은 합성 epoch15 생성 중 `build cap` 거부로 중단했다. Driver의 문자열 치환이 부모 version 조건 외에 build 상한 분기까지 변경해, 승인된 build14가 이전 상한9 분기로 떨어졌다. 실제 서비스나 인증의 실패가 아니라 이번 보정 구현 오류다. 실패 후 추가 보정·재시도는 하지 않았다.


Host6 PASS는 국소 증거다. Rust 검사는 종료했으며 새 build/실제 runtime/auth0. source18/build13/offline41/live6/proxy7/control6/auth관측5와 기존 마감 유지. 실패 source·입력·로그 보존, 빈 Host dir3개만 삭제. H05/H10 exact 승인·최종 수락 별도이며 준비 미완료. 상세 private-evidence/E040 [공개용 중립화]


### MCP19 Local-Only Authorization — 2026-10-24

Owner는 source19/전체21과 승인 확인09:20:35 UTC부터45분(19:05:35 KST)까지 최소 보정·전체 연결 검증을 승인했다. 전체19:47:28 KST와 나머지 상한 유지. 실제 clock/runtime/auth 실행은 제외하며 합성 proxy 시작·종료1회만 수행한다. 실패 시 보정/재시도 없이 중단. 세 소스·장부 변경전과 build13 원본3개를 byte 대조해 보존했다. 계약값/대응위치 사전 확인은 private-evidence/E041 고정했다. 독립 기대값→Host/Rust→build14→정확한 후보 proxy 격리 연결 검증 순서이며 기존 영향 없는 Core/wire/normal-Lite 증거는 재사용한다. 예상25–40분(판단), 중단상한45분. H05/H10 exact 승인과 결과 수락은 별도다. [공개용 중립화]


### MCP19 Verification Helper Failure — 2026-10-24T09:29:12.868699+00:00

MCP19은 첫 독립 기대값 검사에서 결과 기록 helper 오류로 중단했다. `durable_private`는 O_EXCL로 새 파일만 만드는 함수인데 Driver가 누적 result.json 갱신에 재사용했다. 첫 결과 뒤 FileExistsError가 발생했고 finally의 기록도 같은 오류를 냈다. 바깥 실행기의 stderr·exit1·process group 부재 기록은 정상 보존됐다. 저장 API의 기존 동작을 사전 확인하지 않은 Driver 오류다.


source19/build13/offline41/live6/proxy7/control6/auth관측5 유지. 실제/합성 proxy 및 runtime 추가0. 재시도0, 원본·변경·계약·부분 fixture·stderr 보존, 삭제/이동0. 전체 연결 검증 미완료. 상세 private-evidence/E042 [공개용 중립화]


### MCP20 Local-Only Authorization — 2026-10-24

Owner 승인: source20/전체22, 승인 확인09:40:34 UTC부터45분(19:25:34 KST)까지 저장·예외 처리 검사→계약/Host/Rust→build14→전체 연결 검증. 전체19:47:28 KST 및 나머지 상한 유지. 실제 clock/runtime/auth 제외, 첫 실패 시 재시도 없이 중단. 이전 source/장부 원본을 before-mcp20에 보존했고 기존 before-mcp19/build13 원문3개의 동일성을 재확인하여 중복 복사하지 않았다. 계약/저장 수명/대응위치는 private-evidence/E043 고정했다. 예상25–40분, 상한45분; compile/build 대기와 기록 포함. [공개용 중립화]


### MCP20 Static Connection Blocker — 2026-10-24T09:48:03.323941+00:00

저장·예외 처리 보정과 독립 계약·Host·Rust 집중검사는 통과했다. 이어진 전체 연결 경로 대조에서 network-proxy의 bind_stream 허용 시작 ID에 clock-07이 없음을 확인해 중단했다. 앞단 epoch15/명세는 clock-07을 허용하지만 proxy의 s4 clock 목록은 clock-06까지다. 이는 소스의 명시적 조건에서 도출한 거부 판정이며 실제 연결을 실행해 재현한 결과는 아니다.


상세 private-evidence/E044 [공개용 중립화]


### MCP21 Local-Only Authorization — 2026-10-24

Owner가 소스4파일·검증 helper, source21/전체23을 승인했다. 승인 확인09:55:03 UTC부터50분(19:45:03 KST), 전체19:47:28 KST와 나머지 상한·이전 사용량은 유지한다. proxy1개·합성 송신 자식1개만 허용하며 실제 runtime/clock/auth/외부 연결0, 첫 실패 시 재시도 없이 중단한다. 계약/집중검사→build14→검증용 명세→preface/CONNECT/broker 요청 관측 순서다. 저장7건과 영향 없는 normal/Lite·Core·SSE·FD 해제 증거를 재사용하고, 새 계약·proxy 수락은 새로 검증한다. 예상30–45분(최근 Rust37초/build59초 외 준비 시간은 판단), 상한50분; 순차 작업·컴파일 대기·기록 포함. 승인 및 원본4파일/장부 사본은 private-evidence/E045 및 before-mcp21에 보존했다. build13 원본/기존 복구본 동일성을 확인해 중복 복사하지 않았다. [공개용 중립화]


### MCP21 Fixture Parity Failure — 2026-10-24T10:04:06.379882+00:00

Python/Rust 공통 fixture 검사에서 valid-v15는 Python이 수락하고 Rust가 `budget version`으로 거절했다. Rust `epoch_fields` 최상위 허용 목록이 version14까지만 있고15가 빠져 있다. 하위 version15 분기보다 먼저 거절하는 실제 실행 실패다. 앞선 읽기 전용 점검에서 Driver가 이 입구 조건을 놓쳤다. proxy의 clock-07 수락 검사는 통과했지만 전체 연결 통과를 주장하지 않는다.

첫 실패에서 중단했다. 추가 소스 수정·검사 재시도0. build14·명세 전체 조립·격리 proxy·합성 송신 자식·실제 clock/auth/외부 연결은 실행하지 않았다. build14 실행기는 준비됐으나 미실행이며, 연결 검사기는 아직 준비 미완료다. 기존 materialize-native-v15 초안과 그 활성화 차단은 그대로다.

source21/build13/offline41/live6/proxy7/control6/auth관측5 유지, 모든 검사 process group 부재·기존 epoch14/build13 불변 확인. 삭제0/이동0/활성경로 변경0. 상세 private-evidence/E046 [공개용 중립화]


### MCP22 Approved Local Verification — 2026-10-24T10:09:46+00:00

Owner가 최소2파일+검증 helper, source22/전체24, 승인부터50분과 기존 전체19:47:28 KST 마감을 승인했다. 계약→실제 Rust 입구9사례→Host/Rust41대조→필요 Host/app→build14→로컬 조립/연결 순서이며 첫 실패에서 재시도 없이 중단한다. proxy1/합성 송신 자식1, 실제 clock/auth/외부 연결0. 기존 사용량과 proxy23·IO7 증거를 유지한다. 예상30–45분(컴파일 대기 포함, 병렬 절감 가정 없음); 전체 마감이 더 빨라 완료를 보장하지 않는다. 기존 epoch14/build13 복구본과 변경 전2파일·장부를 보존했다. 상세 private-evidence/E047 [공개용 중립화]


### MCP22 Local Proxy Launch Failure — 2026-10-24T10:23:31.940156+00:00

version15 허용 목록과 새 승인/source22·전체24 계약 값을 Host·Rust 두 파일에 보정했다. 실제 입구9사례, 계약30·집계5, Host/Rust41대조, Host7·Rust26, build14, 로컬 조립 Host10·Rust17은 통과했다. 변경 없는 proxy preface23사례와 IO7 증거를 재사용했다.

## First Failure

단회 로컬 연결에서 proxy 실행기가 sandbox_apply: Operation not permitted로 exit71을 반환했다. 합성 송신 자식은 BrokenPipeError로 exit1, 부모는 고정30초 broker 수신 대기 뒤 TimeoutError를 기록했다. broker 요청은 수신하지 못했다. 실제 후보 proxy 진입 전 실행기 실패이며 전체 연결 통과를 주장하지 않는다.

외곽 UNIX-only 검사 sandbox 안에서 production proxy sandbox를 적용하려던 위치는 확인됐다. 중첩 sandbox가 거절의 정확한 원인인지 또는 다른 macOS 조건인지 확정하지 않았다. 첫 실패 뒤 source/profile 보정·재시도·상한 확대0. 자동 승인 검토 도구의 거절이 아니라 실행 프로세스의 sandbox_apply 오류다.

## Boundary And Usage

source22/22, 전체 보정상한24(내용2회 포함), build14/14, offline41/41. 기존 실제 live6/11, proxy7/9, control6, thread예약1/admitted0, turn0, generation0, auth admission관측5를 유지한다. 실제 credential storage read 누적 횟수는 미확정이다. 이번 격리 검증 proxy 실행기 시도1/1(후보 진입0), 합성 송신 자식1/1은 별도로 모두 기록했다.

실제 runtime·clock·인증·DNS·외부 연결·connected FD 발급 추가0. 실제 epoch-v15는 생성하지 않았다. 비clock payload는 합성 계약 입력이므로 H05/H10 실행·수락 입력을 대체하지 않는다.

## Preservation And Cleanup

모든 검사/build process group과 두 자식의 부재, 로그·소켓 종료를 확인했다. 검증 UDS 한 개는 정확한 inode 확인 후 삭제했다. 이동0. 원본2파일/장부, 수정 후2파일, 승인·입력·로그·실패 결과와 build14를 보존했다. 기존 epoch14와 build13 최종 복구본은 bytes 불변이다. 후보 target 바이너리는 build14로 갱신됐고 기존 accepted 바이너리는 불변이다.

종료 스크립트 저장 첫 명령은 중첩 따옴표 SyntaxError로 파일 생성 전 실패했다. 검사·연결을 재실행하지 않고 보존 기록만 완료했다. 현재 worktree와 기록은 미완료 변경·실패 진단·복구·Owner 처분의 입력으로 유지한다. 전체 연결·H05/H10 exact packet·최종 Owner 수락·Work Done은 미완료다. 상세 mcp22-closeout.json 및 mcp22-failure-evidence.json.


누적 활동 1402.842분, 잔여 277.158분(기존 예약 34.302분 포함). 이번 승인 이후 13.766분. 로컬19:59:46 KST보다 전체19:47:28 KST 마감 우선. 잔여 시간은 재시도 권한이 아니다. 상세 private-evidence/E048 [공개용 중립화]

### MCP23 Helper-Only Verification — 2026-10-24T11:57:36.955886+00:00

동일 build14·프로필로 단회 로컬 proxy→broker 요청 전달과 PID 결속을 확인했다.

source22·전체24·build14 및 기존 실제 사용량 유지. 추가 격리 proxy 1회, sender 1회. 실제 runtime/clock/auth/DNS/외부 연결/FD 발급0. 기존 만료 runtime spec은 합성 sender 식별값으로만 사용했고 runtime 실행 적격성을 주장하지 않는다.

프로필 bytes 동일. helper3개·새 proxy 수명 입력과 전체 로그·PID/FD 결과를 보존했다. 종료 process group 부재=True, 로그 종료=True. 사용 완료 UDS 삭제=True. 기존 원본/복구본·build14·미완료 Work를 유지하며 Git publication·실제 epoch 활성화·Owner 수락·Work Done 없음.

전체 마감21:12:41 KST, 로컬21:04:41 KST. 상세 private-evidence/E036 [공개용 중립화]


### MCP24 Approved Actual Clock And Synthetic Preparation — 2026-10-24T12:05:33.915449+00:00

Owner가 build14 유지 실제 clock·합성 검증·H05 복구 묶음 준비까지 승인했다. 승인 관측12:04:21 UTC부터150분과 누적28시간 잔여·기존12시간 중 빠른 마감은 2026-10-24T14:34:21+00:00다. source22/전체24/build14/offline41 및 이전 사용량·권한 경계 유지, 첫 실패 재시도0. H05 exact replay/H10 미승인. 예상80–125분은 준비·서비스/검사 대기·기록 포함 판단값이며 종료20분을 확보한다. build14·소스·MCP23 증거 identity를 확인했다. 기록: private-evidence/E022 준비 helper와 새 입력만 갱신하며 source/build 추가0. [공개용 중립화]

### MCP24 Preparation Failure — 2026-10-24T12:09:51.533100+00:00

새 승인으로 실제 실행 장부를 준비하던 첫 검사에서 prelaunch recovery approval로 거절되어 중단했다. Host host.py:532와 build14의 Rust lib.rs:2715는 MCP22 로컬 전용 승인 해시를 고정 허용한다. MCP24 실제 실행 승인 해시는 다르다. Driver가 앞선 재개 계획에서 이 고정 결속을 놓쳤다. 기존 승인 해시로 바꾸거나 검사를 우회하지 않았다.

준비 process 약 1.093초 exit1. 재수정·재시도0, source/build 추가0. 실제 runtime/proxy/auth/DNS/외부 연결 추가0이며 actual epoch-v15 생성 전 거절됐다. H05 묶음 미준비, exact replay/H10 미실행이다. source22/전체24/build14/offline41 및 기존 실제 사용량을 유지했다.

소스·build14·기존 프로필 불변, 준비 process group 부재 및 로그 종료를 확인했다. 이번 생성한 사용 완료 빈 디렉터리 5개만 open-file 부재 확인 후 삭제했다. 실제 입력·계약·helper·실패 로그와 마지막 복구본은 다음 Owner 범위 판단/미완료 Work 때문에 보존한다. 기존 활성 제품 경로 변경·이동·Git publication·Work Done 없음.

누적 1509.168분, 누적 잔여 170.832분. 이번 승인 이후 종료까지 5.509분. 잔여 시간은 재시도 권한이 아니다. 후속으로는 Host/Rust 승인 결속 보정·직접 검사·새 build가 필요하며 현 build14 유지 승인 범위 밖이다.

상세 private-evidence/E021 [공개용 중립화]

### MCP25 Helper Preparation Failure — 2026-10-24T12:18:34.812940+00:00

Driver 보정 helper가 Rust build cap 수정 문자열을 두 위치에서 발견해 AssertionError로 중단했다. 두 위치는 parent version 선택(2656행)과 build cap(4183행)이며 parent version14는 그대로여야 한다. 제품 검증 실패가 아니라 helper의 고유 위치 선택 오류다. 소스 쓰기와 source 보정 예약 전에 실패했다. 첫 실패 뒤 helper 보정·재시도0이다.

source 사용22/승인23, 전체 보정상한25(H10내용2유지), build 사용14/승인15. 집중 검사·새 build·실제 runtime/auth/DNS/외부 연결·합성·H05 묶음 준비 추가0, H05 replay/H10 미실행. 승인·기존 마감23:34:21 KST는 유지되지만 실패 중단 상태에서 자동 재개하지 않는다.

기존 소스·build14·사용량 불변 및 helper process 부재를 확인했다. before-mcp25의 소스2파일·build14 3바이너리는 원본 bytes와 일치하며 다음 범위 내 수정/build의 복구 입력으로 보존한다. 실패 helper·승인·원인/검사 결과도 보존한다. 삭제0·이동0·활성 제품 경로 변경0.

승인 이후 5.097분, 누적 1517.889분, 누적 잔여 162.111분. 후속 최소 보정은 helper에서 build 항목 문맥까지 포함해 위치를 고정하는1곳이며, 이미 승인된 source23/build15는 아직 소비하지 않았다.

상세 private-evidence/E049 [공개용 중립화]

### MCP26 Helper Generation Failure — 2026-10-24T12:23:33.868694+00:00

재개 helper 생성 명령의 Python 문자열 줄바꿈 처리 오류로 AST 문법검사가 SyntaxError를 반환했다. helper 파일 저장 및 실행 전에 발생했으며 제품 코드나 검사 실패가 아니다. Driver 작성 오류이고 첫 실패 이후 수정/재시도하지 않았다.

source22/build14 및 기존 사용량·증거 불변을 확인했다. 승인 source23/전체25/build15는 유지하며 추가 source/build 슬롯은 미사용이다. 새 helper·집중검사·실제 runtime/auth/DNS/외부 연결·합성·H05 묶음 준비0. H05 replay/H10 미실행. 기존 마감23:34:21 KST 유지.

기존 before-mcp25 복구본과 원 helper는 승인된 보정 재개의 입력으로 보존한다. 이번 실패는 새 실행 파일을 생성하지 않았고 활성 제품 경로 변경·삭제·이동0이다.

승인 이후 1.998분, 누적 1522.874분, 누적 잔여 157.126분. 잔여 시간은 실패 이후 자동 재시도 권한이 아니다.

상세 private-evidence/E050 [공개용 중립화]


### MCP27 Saved Helper Resume — 2026-10-24T12:26:42.856713+00:00

Owner가 helper 줄바꿈 보정과 재개를 승인했다. 중첩 코드 생성 없이 파일을 직접 저장하고 AST 문법검사 후 실행했다. 기존 MCP25 exact 승인·source23/전체25/build15·23:34:21 KST 마감·누적/권한 경계를 유지한다. before-mcp25 복구본을 재사용했다. Rust parent version14는 유지하고 build cap만15로 보정했다. 두 소스 각5개 승인/한도 값만 변경하고 source23을 예약했다. 집중 통과 뒤 실제 clock/합성/H05 packet까지 수행하며 첫 실패 중단, H05 replay/H10 제외다.


### MCP27 Actual Clock Notification Failure — 2026-10-24T12:37:21.116423+00:00

helper 줄바꿈을 보정하고 모든 새 helper를 저장한 뒤 AST 문법검사를 통과시켰다. Host·Rust 승인 결속/source23·전체25·build15 값을 두 파일의 각5곳에 반영했다. 계약32·집계5, Rust 입구9, Host/Rust43대조, build15, 로컬 조립 Host10·Rust17, 실제 입력 조립은 통과했다.

## Actual Clock Failure

실제 clock 시도는 약20.12초 뒤 thread/start 단계에서 fixture notice phase or duplicate로 거절됐다. 인증 admission 관측과 models/accounts 제어 통신은 성공했고 thread-bound가 기록됐다. 개발 기능 warning은 정확한 내용·schema 검사를 지난 첫1건이었으며, 모델 turn·generation·clock dispatch는 모두0이다.

정적 코드와 실행 순서상 thread/start 응답이 fixture_notice_pending을 false로 만든 뒤 launch drain에서 늦게 도착한 warning을 읽어 pending 조건에 걸린 것으로 판단한다. 원문 notification을 새로 수집하거나 실행을 재현하지 않았다. 이번 집중 검사는 승인/한도/조립을 검증했으며 이 비동기 알림 순서는 다루지 못했다. 변경 없는 Host 알림 검사 증거를 재사용한 한계다.

첫 실패 뒤 보정·재시도·권한 확대0. 원 stop과 process-ended는 장부에 남았고, controller의 추가 stop 예약은 이미 중단된 상태에서 거절됐다. runtime/proxy/controller와 process group 부재, FD2개 반환 및 lease0, 보호 인증 파일 metadata 불변을 확인했다. credential storage read 실제 횟수는 미확정이다.

## Usage And Remaining Work

source23/23·전체 보정상한25(내용2 유지)·build15/15·offline41/41. 누적 live7/11·proxy8/9·control8·thread예약2/결속1·turn0·generation0·auth admission관측6. 이번 추가는 runtime1·proxy1·DNS1·control2·FD2·thread결속1·auth admission관측1이다.

합성 검증·H05 복구 묶음 준비는 미착수이며 H05 exact replay/H10·최종 수락·Work Done도 미완료다. 기존 마감23:34:21 KST와 누적28시간 한도는 바꾸지 않았다. source/build 승인 슬롯은 소진됐고 실패 중단 상태이므로 남은 시간이 재개 권한은 아니다.

## Preservation And Cleanup

두 소스의 현재 bytes와 build15 후보, build14 마지막 복구본, 이전 epoch14 불변을 확인했다. 기존 accepted 바이너리는 불변이다. 고유 입력·helper·검사/실행 로그·실패 장부와 Work 상태를 durable 경로에 보존했다. 현재 소스는 기존 worktree에 보존하며 중복 source archive는 만들지 않았다.

종료된 task socket1개와 비어 있는 전용 socket 디렉터리를 소유권·프로세스 부재·open-file consumer 부재 확인 후 삭제했다. 그 외 파일 삭제0, 이동0. 후보 target은 build15, 실제 epoch 포인터는 epoch-v15-mcp27로 변경됐고 중단 상태다. Worktree·복구본·runtime DB는 미완료 작업과 이번 실패 진단/Owner 처분의 입력으로 유지한다.

승인 이후 11.919분, 누적 1536.661분, 누적 잔여 143.339분. 종료20분 및 불확실성14.30235분 예약 유지.

상세 private-evidence/E051 [공개용 중립화]


### MCP28 Late Notification Recovery — 2026-10-24T12:42:32.101925+00:00

Owner가 첫 알림의 응답 전후 순서 최소 보정과 source24/전체26/build16을 승인했다. 기존 마감23:34:21 KST·live11/proxy9/offline41·누적 사용량/권한 경계를 유지한다. 응답 전/직후 drain/prepare 중 첫 알림과 중복·foreign thread·잘못된 내용·늦은 phase 거절을 검증하고 실제 clock/합성/H05 묶음 준비까지 수행한다. 첫 실패 중단, H05 replay/H10 별도다. 이전 epoch15 실제 실패와 사용량을 새 epoch16에 결속하며 이전 계약은 보존한다. 예상80–110분은 대기/기록 포함 판단값, 종료20분 확보, 절대 마감 우선이다. 세 소스와 build15 마지막 복구 bytes를 before-mcp28에 보존했다. 추가 proxy는 총9회 중 마지막을 쓰고 합성은 같은 controller를 공유한다.


### MCP28 Recovery Evidence Serialization Failure — 2026-10-24T12:51:50.396709+00:00

늦게 도착한 첫 알림을 native thread/start 응답 직후부터 첫 prepare 전까지 같은 thread에 결속해 받도록 최소 보정했다. 내용/schema·첫1건·중복/foreign thread·늦은 phase 거절은 유지했다. 이전 실제 epoch15의 누적 사용량을 epoch16 복구 계약에 반영하고 source24/전체26/build16을 결속했다.

## Verification And First Failure

알림 관련18개 검사 PASS: 새 도착 순서3개(응답 전, 응답 직후 실제 drain 경로, prepare 중)와 새 거절9사례를 포함한다. Host 계약33·집계5, Rust version 입구10사례도 통과했다.

Host/Rust 대조는 첫 새 valid-v16에서 Err(noncanonical recovery JSON)으로 실패했다. prepare-mcp28.py의 공통 저장 함수가 mcp28-parent-evidence.json을 들여쓰기·비정렬 JSON998바이트로 저장했다. Rust bound_json은 정렬·compact JSON과 마지막 줄바꿈866바이트를 요구한다. 다른 복구 입력3개는 canonical이며, 모든 참조 hash와 내용은 맞았다. 알림 보정의 실패가 아니라 Driver 준비 helper의 직렬화 오류다.

첫 실패 뒤 보정·재시도0. Rust version16 나머지 계약 사례·조립 연결은 미검증이다. build16·실제 clock·합성·H05 묶음 준비는 시작하지 않았다. 별도 재개 시 실패 원본을 보존한 새 canonical evidence 입력과 helper 참조 최소 보정이 필요하며, 이 실패만으로 제품 source 추가 보정이나 한도 확대가 필요하다는 근거는 없다.

## Usage And Preservation

source24/24 사용, 전체 보정상한26(내용2 유지), build15/승인16. offline41/live7/proxy8/control8/thread예약2·결속1/turn0/generation0/auth admission관측6 유지. 이번 실제 runtime/proxy/auth/DNS/외부 연결 추가0. credential storage read 실제 횟수는 미확정이다.

모든 검사 process group 부재와 로그 종료를 확인했다. source24 현재 bytes, source23 원본3개, build15 현재 후보·마지막 복구본, 실패 입력·검사 로그·장부·후속 helper 초안을 durable 경로에 보존했다. 이전 실제 epoch15와 accepted 바이너리는 불변이다. active source는24로 변경됐고 실제 epoch 포인터/build 후보는 이전15 유지. 삭제0·이동0. 예정된 serializer 보정·build16과 실패 진단/Owner 처분의 입력이므로 유지한다.

H05 묶음 준비/H05 exact replay/H10·최종 수락·Work Done 미완료. 마감23:34:21 KST와 누적28시간·종료20분/불확실성14.30235분 예약은 유지한다. 남은 시간은 중단 후 자동 재시도 권한이 아니다.

이번 승인 이후 11.373분, 누적 1551.149분, 누적 잔여 128.851분.

상세 private-evidence/E052 [공개용 중립화]


### MCP29 Canonical Evidence Resume — 2026-10-24T12:57:21.010872+00:00

Owner가 실패 원본 보존과 canonical JSON 입력 최소 보정·재개를 승인했다. mcp28-parent-evidence.json 998바이트는 불변 보존하고 같은 JSON 값의 정렬 compact+LF 866바이트 사본을 mcp29-parent-evidence.json에 저장했다. 원 MCP28 exact 승인 hash와 source24/전체26/build16·기존 마감23:34:21 KST·사용량/권한 경계를 유지한다. source/build 추가 사용0. 알림18·Rust 입구10·컴파일 결과는 재사용하고 새 입력의 Host33/집계5 및 Rust45 대조부터 수행한다. 통과 후 build16·로컬 조립·실제 clock·합성·H05 묶음 준비 순서, 첫 실패 중단, H05 replay/H10 별도다. 예상65–90분은 준비/대기/기록 포함 판단값이며 기존 마감과 종료20분 예약이 우선한다.


### MCP29 Actual Proxy Connection Failure — 2026-10-24T13:04:44.376472+00:00

실패 원본998바이트를 보존하고 같은 JSON 값의 canonical 사본866바이트를 만들었다. 제품 source 추가 변경0. 새 입력의 Host33·집계5·Host/Rust45 대조, build16, 로컬 조립 Host8·Rust14와 실제 epoch16 준비를 통과했다. 영향 없는 알림18·Rust 입구10 증거를 재사용했다.

## Actual Clock Failure

실제 clock 단회 실행은 약19.42초 뒤 initialize 단계에서 runtime stdout closed로 중단됐다. runtime exit1, stderr49바이트의 길이/hash만 보존됐다. proxy stderr는 Error: prepared connection failed다. DNS1·auth admission관측1·models 제어 예약1은 있었지만 FD 예약/발급0, 새 thread/turn/generation/clock 호출0이다.

정적 코드에서 runtime의 clock-08과 network-proxy/src/prepared_fd.rs의 허용 목록(clock-07까지)이 불일치함을 확인했다. 이 불일치는 clock-08 preface를 거절하며 실제 FD 이전 실패와 맞는다. 다만 proxy가 일반화한 바깥 오류만 저장해 내부 거절 문구는 확보되지 않았다. 재현/재시도는 하지 않았다.

Driver가 source24에서 Host/App Server 입구와 복구 계약을 바꾸면서 proxy의 별도 preface 허용 목록을 놓쳤다. 기존 proxy23사례는 clock-08을 검증하지 않았고, 명세 조립 검사는 실제 preface 교환을 대신하지 못한다. canonical JSON과 알림 순서 보정의 통과를 전체 연결의 통과로 볼 수 없다.

## Boundary And Usage

첫 실패 뒤 source/helper 보정·재시도·한도 확대0. source24/24·전체 보정상한26(내용2 유지)·build16/16·proxy9/9·offline41/41. 누적 live8/11·control예약9·thread예약2/결속1·turn0/generation0·auth admission관측7 유지. credential storage read 실제 횟수는 미확정이다. proxy 한도를 모두 사용했으므로 다음 실제 연결 시도는 현재 승인 범위에서 실행할 수 없다.

합성 검증/H05 묶음 준비는 미착수, H05 exact replay/H10·최종 수락·Work Done 미완료다. 기존 마감23:34:21 KST·누적28시간·종료20분/불확실성14.30235분 예약은 유지한다.

## Preservation And Cleanup

runtime/proxy/controller와 모든 검사 process group 부재, controller closed/lease0, 보호 인증 파일 metadata 불변을 확인했다. 원 stop/process-ended는 남았고 추가 stop 예약은 이미 중단된 상태에서 거절됐다.

실패 원본·canonical 사본·source24·build16·build15 마지막 복구본·정확한 입력/로그/epoch를 durable 경로에 보존했다. 이전 실제 epoch15와 accepted 바이너리는 불변이다. 현재 후보는 build16, 실제 epoch 포인터는 중단된 epoch-v16-mcp29다.

정확한 task socket1개와 비어 있는 전용 디렉터리를 소유권·프로세스 그룹 부재·open-file consumer 부재 확인 후 삭제했다. 다른 파일 삭제0·이동0. 나머지는 실패 진단·미완료 작업·Owner 처분의 입력으로 유지한다.

승인 이후 8.656분, 누적 1564.049분, 누적 잔여 115.951분. 잔여 시간은 자동 재개 권한이 아니다.

상세 private-evidence/E053 [공개용 중립화]


### MCP30 Proxy Preface Correction — 2026-10-24T13:07:58.378688+00:00

Owner가 proxy clock-08 허용과 source25/전체27/build17/proxy10을 승인했다. 나머지 한도와 마감23:34:21 KST, 첫 실패 중단을 유지한다. 실제 UDS 소켓에서 production bind_stream을 호출하는 positive/negative 검사를 추가한다. 소진된 clock-08 재사용은 금지되므로 live11 안의 clock-09 배정과 Host/Rust 복구 계약 포함 여부는 Owner 답변 대기다. 그와 독립적인 proxy2파일 보정과 focused preface만 우선 수행한다. 예상10–20분은 보정/검사/기록 대기를 포함한 판단값이고 전체 마감은 바뀌지 않는다. 기존 source24와 실패 증거는 보존했다. H05 replay/H10 별도, commit/publication 없음.


MCP30 preface checkpoint: 실제 UDS 25조건 PASS(1 test,8.185초), process group 부재, 두 저장소 diff check PASS. source25 사용, build16/proxy9 유지; build17은 clock-09 복구 배정 답변 뒤 최종 묶음으로 실행한다. build16 바이너리3개1564196256바이트를 before-mcp30/build16에 bytes/hash/metadata 검증 보존했다. 별도 실제 runtime/auth/외부 접속0. 활동계산13:09:22Z까지, 이후 Owner 답변만 기다린 시간은 제외하되 절대 마감은 유지한다. 원본/복구/검사 자료는 후속 build17 및 Owner 판단 입력으로 유지한다. 삭제/이동0.


### MCP30 Clock09 Recovery Scope — 2026-10-24T13:21:53.690962+00:00

Owner가 source25 안의 최소 Host/Rust 복구 계약과 live11 유지에 답변했다. 기존 clock8회/실패 epoch16을 그대로 보존하고 새 epoch17에 clock-09 1회 및 합성2회를 배정한다. proxy clock-08/09 허용, 잘못된 slot/identity/clock-10 거절을 actual UDS로 검증한다. source25/전체27/build17/proxy10 및 기존 offline41/thread8/turn/generation/권한/23:34:21 KST 마감을 유지한다. 합성2회까지 쓰면 live11 소진, H10은 별도 실행 권한과 여유가 필요하며 이번 실행에 포함하지 않는다. 예상40–60분은 보정/집중검사/build/clock/합성/H05 준비 및 실행 대기를 포함한 판단값이다. 마감/종료20분 예약이 우선하며 첫 실패 중단한다. 전체 suite 대신 새 Host 계약/집계, Rust admission/parity, 새 preface, 실제 조립의 집중 검사를 수행하고 변하지 않은 알림18과 기존 safety evidence를 재사용한다. 13:09:22–13:17:49Z Owner-only 대기는 누적 활동에서 제외했다.


### MCP30 Actual Clock Policy Failure — 2026-10-24T13:33:29.940671+00:00

proxy clock-08/09 허용과 exact epoch17 복구 계약을 source25 한 묶음에 반영했다. 기존 clock8회 사용을 보존하며 clock-09 1회와 합성2회를 전체 live11 안에 배정했다. source25/전체27/build17/proxy10 외 기존 한도와 권한·마감은 유지했다.

## Verification And Actual Failure

Host 새 계약35·집계5, Rust admission1 test, Host/Rust 신규35+과거13=48대조, 실제 UDS preface27조건을 통과했다. build17은120.295초에 완료했고 Host 조립8·Rust 조립14도 통과했다. 영향 없는 알림18 등의 증거는 재사용했다.

실제 clock은 약20.43초 뒤 turn/prepare의 RPC -32600으로 중단됐다. initialize·계정 확인·thread 시작·첫 알림 처리는 진행됐고 외부 FD2개가 발급/반납됐다. proxy 연결과 clock-09 허용은 실제 경로에서도 확인됐다. 모델 turn/generation/clock dispatch는0이다.

실행 입력의 document_policy가 빈 객체였다. Core privacy_literals는 allowed_identifiers 배열을 요구한다. 정적 경로에서 구성한 `prepared plan: document identifier policy unavailable: invalid type: null, expected a sequence`의 SHA-256이 보존된 RPC 오류 hash와 정확히 일치한다. 원 오류 문자열 자체는 저장되지 않았으며 hash 대조로 확인했다. 다음 owner_input_sha256 검사도 정적으로 존재하지만 이번에는 도달하지 않았다. Driver가 실제 clock 입력의 정책 필수 필드를 검증 범위에 포함하지 못했다.

첫 실패 뒤 추가 source/helper 보정·실제 재시도0. 합성 검증과 H05 묶음 준비는 미착수이며 H05 exact replay/H10·최종 수락·Work Done은 미완료다.

## Usage And Boundary

source25/25·전체 보정상한27(내용2 유지)·build17/17·proxy10/10·offline41/41. 누적 live9/11·control예약11·thread예약3/결속2·turn0/generation0·auth admission관측8. credential storage read 실제 호출 횟수는 미확정이다. 남은 live2는 합성 배정이며 소진된 clock-09 재사용 권한이 아니다. 다음 실제 시도에는 시작 배정·복구 계약 및 소진된 proxy 한도의 별도 판단이 필요하다.

기존 마감23:34:21 KST·누적28시간·종료20분/불확실성14.30235분 예약은 유지한다. 남은 시간은 중단 후 재개 권한이 아니다. 이번 승인 활동 시간에서는 명시적 Owner 대기를 제외했고, 누적 장부에는 기존 복구 계약의 보수적 carry 하한도 적용했다.

## Preservation And Cleanup

runtime/proxy/controller와 검사 process group 부재, controller closed/lease0, 보호 인증 metadata 불변을 확인했다. source25·build17·build16 마지막 복구 bytes·이전 실패와 epoch·정확한 입력/로그를 durable 경로에 보존했다. 이전 실제 epoch16과 accepted 바이너리는 불변이다. 현재 후보는 build17, 실제 epoch 포인터는 중단된 epoch-v17-mcp30다.

정확한 task socket1개와 비어 있는 전용 디렉터리를 소유권·프로세스 그룹 부재·open-file consumer 부재 확인 뒤 삭제했다. 다른 파일 삭제0·이동0. 남은 자료는 미완료 작업의 진단·복구·Owner 처분 입력으로 유지한다.

이번 승인 이후 활동 19.307분, Owner-only 대기 8.451분 제외. 누적 활동 1592.808분, 누적 잔여 87.192분.

상세 private-evidence/E054 [공개용 중립화]


### MCP31 Clock10 Policy And Recovery — 2026-10-24T13:42:28.244583+00:00

Owner 승인 source26/전체28/build18/proxy11/live12. 기존 9회 시작 및 thread3/bound2/control11/auth admission8/FD6 이력을 보존하고 clock-10 1회와 합성2회를 배정한다. clock 정책은 allowed_identifiers=[] 및 원문 바이트 SHA256을 제공하며 Core 검증을 유지한다. 실제 prepare가 부르는 입력 검증부를 직접 검사하고 Host/Rust 계약·preface·조립을 집중 검증한다. 전체 prepare 성공은 실제 clock의 별도 관측이다. 기존 offline41/thread8/기타 권한/23:34:21 KST 마감 및 첫 실패 중단을 유지한다. H05 묶음 준비만 포함, replay/H10/Owner 수락/Work Done/Git publication은 별도다. 예상40–55분은 판단값이며 실행 대기 포함, 이전 집중검사/build 약4분을 참고했다. 고정 마감과 종료20분 및 기존 불확실성 예약이 우선한다. build17 원본 복구 파일과 source25 원본을 before-mcp31에 검증 보존했다.


### MCP31 First Recovery Contract Failure — 2026-10-24T13:44:36.325242+00:00

source26 적용 뒤 첫 Host 복구 계약 검사에서 중단했다. 통과한 사례는 0개다. 정책·Rust·proxy 검사와 build18, clock-10, 합성2회, H05 묶음 준비는 시작하지 않았다. H05 replay/H10/최종 Owner 수락/Work Done은 별도이며 미완료다.

실행 오류는 `clock09 document policy recovery observed effects`다. Driver가 이전 증거 객체를 문자열로 치환하면서 키 순서 차이를 확인하지 않아 치환이 적용되지 않았다. 이후 일부 hash만 변경돼 stop_seq/last_seq/last_sha256/runtime_start/observed_effects/source_closeout_sha256에 이전 값이 남았다. Host는 실제로 이 불일치를 거절했다. Rust 새 분기도 같은 값이 남아 있음을 정적으로 확인했으며 Rust 검사는 실행하지 않았다. 구체 필드 차이는 mcp31-failure-evidence.json에 보존했다.

clock 호출부에 allowed_identifiers=[]와 원문 바이트 SHA256을 넣고, Core prepare의 기존 정책 검증을 공유 함수로 추출해 집중 검사를 준비했지만 이 검사는 미실행이다. 정책 보정이나 전체 prepare 성공을 주장할 수 없다. source26은 unverified 상태로 남겼다.

첫 실패 뒤 코드·검사 helper 보정과 재시도는 0회다. source26/26, build17/18, proxy10/11, live9/12, offline41/41. 누적 control11, thread예약3/결속2, turn0/generation0, auth admission관측8을 유지한다. credential storage read 실제 횟수는 미확정이다. clock-10/합성2회는 사용하지 않았다. 고정 마감23:34:21 KST 및 기존 예약은 그대로다.

검사 process group 부재, source26 실패 후 불변, source25 원본과 build17 원본/복구본의 byte hash 일치, accepted 바이너리 불변, 이전 실제 epoch17 불변, 두 저장소 git diff --check 통과를 확인했다. 새로운 runtime/proxy/auth/DNS/model 효과는 없다.

source25/26·build17·원본 로그·실패 입력·복구 계약은 기존 영구 작업 경로에 보존했다. 실행 기록은 mcp31-stopped로 변경했으며 활성 후보 build17과 실제 epoch17 포인터는 그대로다. 삭제0·이동0. source와 증거는 다음 승인된 보정 또는 Owner 처분에 필요하고, 새 build가 없어 build17 복구본도 아직 이 후속 작업의 복구 입력이다. 보존 사유와 종료 조건은 closeout에 기록했다.

승인 이후 8.686분, 누적 잔여 78.505분. 잔여 시간은 재개 권한이 아니다.

상세 private-evidence/E055 [공개용 중립화]


### MCP32 Structural Evidence Correction — 2026-10-24T13:47:38.323085+00:00

Owner 승인 source27/전체29, 미사용 build18/proxy11/live12 및 clock-10/합성2회 유지. Host AST와 Rust JSON 객체 경계를 사용해 이전 값6필드와 prior_attempts를 교체하고 전체 객체 동등성을 독립 확인했다. 역사 분기는 보존한다. Host/Rust 실행 일치를 먼저 확인한 뒤 정책/prepare/clock/합성/H05 준비 순으로 진행하며 첫 실패 중단한다. 기존 마감23:34:21 KST/권한/예약 유지, H05 replay/H10 별도. 예상35–45분은 앞선 집중검사/build 약4분을 참고한 판단값이며 실행 대기 포함, 누적 stop한도와 구별한다.


### MCP32 Local Checks Passed; Live Entry Held — 2026-10-24T13:57:51.297084+00:00

source27 구조 보정과 집중 검사, build18 및 로컬 조립 검사가 통과했다. 새 실패는 없다. 실제 실행 진입에 필요한 기존 시간 조건을 충족하지 못해 clock-10·합성2회와 H05 묶음 준비는 시작하지 않았다.

Host는 AST 노드 위치, Rust는 JSONDecoder 객체 경계로 새 epoch18의 증거 객체를 교체했다. 이전 값이 남았던 6필드를 고쳤고 증거 파일·Host·Rust 전체 객체 동등성을 확인했다. prior_attempts의 source27 및 전체29를 함께 반영했으며 이전 epoch 분기를 보존했다.

Host 계약35·집계5, 공통 Host/Rust49사례(기존 양성14 포함), Rust admission1테스트, Core 정책1테스트/7조건, 실제 UDS preface29조건, build18, Host 조립8·Rust 조립14가 통과했다. 빌드는 136.225초였다. 원문97바이트/마지막 newline을 유지한 SHA256이 clock template와 document_policy에 동일하게 들어감을 구조적으로 확인했고 실제 prepare가 테스트한 검증부를 호출함을 확인했다. 실제 turn/prepare 전체 실행은 아직 하지 않았으며 이 증거를 전체 prepare 성공으로 표현하지 않는다.

## Live Entry Time

마감은23:34:21 KST다. 기존 materializer는 남은 시간이40분을 초과해야 하고, controller는 종료20분 예약을 제외한 실행 여유가20분을 초과해야 한다. build18은22:55:22 KST에 끝났으므로 그때 이미 진입 조건에 미달했다. 이 조건이나 마감을 낮추거나 늘리지 않았고, 실패가 예상되는 실제 prepare 함수를 호출하지 않았다. 종료 확인 시 남은 wall time은 36.495분이다. 이는 검사 실패나 runtime 실패가 아니라 실행 전 시간 조건에 따른 보류다.

## Usage And Remaining Work

source27/27·전체29(내용2 별도)·build18/18, proxy10/11·live9/12·offline41/41. control11·thread예약3/결속2·turn0/generation0·auth admission관측8은 그대로다. credential storage read 횟수는 미확정이다. clock-10과 합성2회는 미사용이며 실제 runtime/proxy/auth/DNS 추가0이다.

실제 turn/prepare·clock·합성 검증·H05 묶음 준비는 미완료다. H05 replay/H10/최종 Owner 수락/Work Done/Git publication도 별도로 남겼다.

## Preservation And Cleanup

모든 검사/build process group 부재, source27 불변, source25/26 원본, build17 복구본, build18 후보, accepted 바이너리 및 이전 실제 epoch17 불변을 확인했다. 두 저장소 git diff --check가 통과했다.

활성 candidate 바이너리는 build18로 바뀌었고 build17은 before-mcp31/build17에 검증 보존했다. 실행 기록은 local-complete-live-held, 실제 epoch 포인터는 중단된 epoch-v17-mcp30 그대로다. source·정확한 입력/결과·helper·복구본은 다음 승인된 실행과 Owner 처분의 구체 입력이어서 보존한다. 삭제0·이동0이며 보존을 정리 완료로 표현하지 않는다.

작업 시작 이후 10.219분, 누적 잔여 68.286분. 누적 잔여와 별개로 더 이른 고정 마감/진입 조건을 적용했다.

상세 private-evidence/E056 [공개용 중립화]


### MCP34 Exact Deadline Extension — 2026-10-24T14:08:03.232416+00:00

Owner 승인 source28/전체30/build19. 새 epoch18만 이전 run deadline+1시간을 허용하고 원 approval wall·과거 epoch·효과·카운터를 보존한다. 외부 마감2026-10-25 00:34:21 KST, 내부13시간 segment, 누적28시간/종료20분/불확실성14.30235분 유지. Owner가 남은 시간 이내 실행을 선택해 실제 진입 최소 실행 여유만20분에서120초로 낮추고 실효 deadline은 기존 min 계산을 유지한다. proxy11/clock-10/합성2회 배정 불변. H05 replay/H10 별도, 첫 실패 중단. 이전 policy7조건/preface29/normal-Lite를 source 불변 확인 후 재사용하며 기한 Host/Rust 대조·build19·후보 조립만 새로 검사한다. 기대20–35분은 준비와 기존 집중검사/build 약4.5분·실제 남은 시간을 합친 판단값이며 완료 보장은 아니다. 더 이른 누적 한도가 우선한다.


### MCP34 Runtime Expiry Prelaunch Failure — 2026-10-24T14:16:31.868427+00:00

source28 기한 계약, Host/Rust52사례 대조, build19와 로컬 조립 Host8/Rust14 및 실제 epoch18 준비가 통과했다. 영향 없는 정책7조건·preface29조건 증거는 소스 불변 확인 후 재사용했다. build19는 20.453초였다.

실제 controller 단계는 runtime 생성 전에 `runtime expiry`로 실패했다. 기록된 만료 시각 1792851983309ms가 누적 마감에서 종료·불확실성 예약을 뺀 상한 1792851983302ms보다7ms 늦었다. controller가 한 번 읽은 남은 시간을 뒤에 읽은 현재 시각에 더하면서 생긴 불일치다. 이 설명은 코드와 고정 spec/anchor의 숫자 대조에 근거하며 재현 호출은 하지 않았다. 기존 로컬 조립은 이미 절대 시각으로 제한한 expiry를 사용해 이 controller 산술 경로를 검사하지 않았다.

proxy11과 DNS1은 사용했지만 runtime 시작 예약·프로세스·auth·실제 turn/prepare·clock 호출·모델 turn/generation은 모두 추가0이다. 기존 clock9회 이력은 유지했고 clock-10과 합성2회는 미사용이다. 첫 실패 뒤 source/helper 수정·재시도0. 실제 prepare·clock·합성 검증·H05 묶음 준비는 미완료이며 H05 replay/H10은 별도다.

source28/28·전체30(내용2 유지)·build19/19·proxy11/11·live9/12·offline41/41. control11·thread예약3/결속2·turn0/generation0·auth admission관측8 유지. credential storage read 실제 횟수는 미확정이다. 외부 마감2026-10-25 00:34:21 KST, 내부 run deadline+1시간이 실제 epoch18에 반영됐으며 원 승인 시각·누적28시간·종료20분·불확실성14.30235분은 보존했다. Owner가 남은 시간 내 실행을 선택한 진입 조건도 반영했지만 이를 예산 상한 우회에 쓰지 않았다.

모든 검사/controller/proxy process group 부재, controller closed/lease0, 보호 인증 파일 metadata 불변, source28/build19 및 source27/build18 복구본·accepted 바이너리·이전 epoch17 bytes를 확인했다. 두 저장소 git diff --check가 통과했다.

활성 후보는 build19, 실제 epoch 포인터는 중단된 epoch-v18-mcp34다. 실패 원본·입력·계약·기록과 이전 후보 복구본을 보존했다. task socket1개와 빈 socket 디렉터리, runtime이 생성되지 않은 빈 전용 상위 디렉터리만 소유권·프로세스/소비자 부재 확인 후 삭제했다. 다른 삭제/이동0. 나머지는 명시적 후속 복구 또는 Owner 처분의 입력으로 유지한다.

승인 관측 이후 11.348분, 누적 잔여 44.160분. 잔여 시간은 재시도 권한이 아니다.

상세 private-evidence/E057 [공개용 중립화]


### MCP35 Absolute Expiry Correction — 2026-10-24T14:25:00.066709+00:00

만료 시각 보정과 경계18검사가 통과했다. 실제 재시도0, build0이다. 실패 당시 MCP34 helper/epoch/원본은 보존하고 수정 후보를 별도로 만들었다. 후보는 아직 실행 계약에 활성화하지 않았다.

기존 controller의 시간 계산1줄을6줄로 바꿨다. expiry = min(누적 절대 마감−종료/불확실성 예약, 구간 절대 마감−같은 예약, 외부 절대 마감−종료20분)으로 먼저 고정하고, 남은 시간은 expiry에서 현재 시각을 빼서 계산한다. 기존 state remaining도 상한으로 유지한다. 읽기 지연을 만료 시각에 다시 더하지 않는다. 나머지 controller AST는 동일하다.

검증은 실제 helper의 변경 전/후 AST 블록과 기존 materializer의 정확한 거절 조건을 추출해 결정적 clock/budget 대역으로 실행했다. 기존7ms 초과 재현, 지연0/1/7/999/120001ms, 누적/구간/외부 마감·동률, 진입 여유120초±1ms/만료, materializer 상한±1ms, proxy/clock/synthetic 전달 연결을 포함한다. 실제 materialization 또는 provider 성공 증거가 아니다.

제품 source28/build19 및 정책 관련 소스의 bytes 불변을 확인했다. 기존 Host/Rust52·admission·조립 Host8/Rust14·build19·정책7/preface29 증거를 해당 변경 없는 범위에 재사용했다. 전체 검사와 재빌드는 반복하지 않았다. 향후 epoch19 계약은 별도 집중 검증이 필요하다.

이번 helper 보정을 source 보정29번째로 계산했다. 제품 소스 세대는28, build19, proxy11, live9, offline41을 유지했다. 내용 보정 허용2를 포함한 보정 상한 표기는31이다. 중단된 실제 epoch18 장부와 과거 상한은 수정하지 않았다.

## Retry Budget Proposal

실제 재시도에는 source 보정1묶음(29→30, 내용 허용2 포함 전체32), build1회(19→20), proxy1회(11→12)가 추가로 필요하다. Host/Rust의 현행 version18 admission은 이전 epoch17 실패·proxy10→11에 고정돼 있어 새 epoch18 실패를 잇는 version19 계약이 필요하다. 이 복구 계약 구현과 build는 이번에 실행하지 않았다. clock-10·합성2회는 미사용이므로 기존 live총12/offline41 상한 유지가 가능하다. 실제 grant/권한·auth/network 범위 확대는 없다. H05 replay와 H10은 별도다.

2026-10-24 23:25:00 KST 기준 누적28시간 중 잔여 35.69분. 종료20분·불확실성14.30235분을 제외하면 1.39분이며, 외부/구간 마감까지 함께 제한한 실행 여유도 1.39분이다. 종료 이후 Owner 대기까지 보수적으로 포함했고 별도 pause 공제는 하지 않았다. 잔여 시간은 실행 승인과 다르다.

재시도 예상20–35분은 낮은 신뢰의 판단값이다. 복구 계약·집중 검사/build·clock·합성2회·H05 준비·정상 종료를 포함한다. provider/test 대기는 포함하고 Owner 승인 대기는 예상 작업시간에서 제외하며 병렬 절약을 가정하지 않는다. 직전 local 단계 약5분/build20.453초는 실측 근거지만 뒤의 성공 경로 전체는 미측정이다.

작업 중단한도35분과 별도 예약34.30235분을 확보하려면 이 시점 누적 예산이 최소 33.61분 더 필요하다. 누적 +40분(28시간40분)을 제안하며 아직 적용하지 않았다. 기존 외부 마감은 10-25 00:34:21 KST, 구간 마감은 10-25 00:35:42 KST다. 승인 때 구간 마감이 승인 시각+69.30235분, 외부 마감이 승인 시각+55분보다 이르면 필요한 차이만 함께 연장해야 한다. 지금 판단을 미래 승인 시점의 잔여 시간으로 재사용하지 않는다.

보존: 수정 후보·patch·회귀 입력/결과와 source/build·실패 복구 근거. 활성 runtime 경로 변경0, 삭제/이동0. 다음 별도 승인 복구 또는 Owner 처분을 위해 유지한다. Work 수락/Done·commit·publication·adopter 적용0. 설치된 제품에는 이번 task helper 보정으로 인한 업데이트가 필요하지 않다.

상세 private-evidence/E058 [공개용 중립화]


### MCP36 Expiry Recovery Contract — 2026-10-24T14:52:00.637878+00:00

Owner 승인 source30/전체32/build20/proxy12/누적28시간40분. 중단 epoch18의 proxy11/stop2와 추가 runtime0을 exact 결속한 epoch19 후보를 만들었다. 원 승인 시각·이전 효과/사용량과 예약34.30235분은 유지한다. 내부 구간 마감은2026-10-25 00:40:41.443 KST로4분59.443초 연장, 기존 외부 마감00:34:21 KST는 충분해 유지한다. 보수적 누적 작업 cutoff00:06:23.302 KST가 먼저다. 승인 관측23:47:19 기준 예상20–35분보다 짧은 약19분 실행 여유이므로 완료 보장은 없다. 계약 집중/Host-Rust parity·build20·실제 controller 계산을 쓰는 조립을 새로 검사하고 정책/preface/기존 국소 증거를 재사용한다. 첫 실패 중단, H05 replay/H10 별도. source/build 복구본은 before-mcp36에 보존했다.


### MCP36 Actual Tool Source Refusal — 2026-10-24T14:59:31.330607+00:00

실제 clock-10이 turn/prepare에서 다시 거절돼 첫 실패로 중단했다. 응답은 `prepared plan: unsupported prepared tool source`다. RPC -32600과 메시지 SHA256이 source의 오류 문구에 정확히 일치한다. 여러 조건을 묶은 도구 소스 검사가 거절한 것은 확인했지만, 어떤 조건이 참이었는지는 현재 기록만으로 특정하지 못했다. 실패 후 수정·재시도0이다.

7ms 만료 시각 문제는 이번 실제 경로에서 통과했다. proxy/runtime expiry는 누적 절대 상한 이내였고 runtime 시작·read-only auth admission·control2회·thread 시작/결속까지 진행했다. prepared manifest/input 예약/model turn/generation은0이다. 이전 source 정책 입력 검사와 조립 검증은 전체 실제 speculative tool-plan 경로를 실행하지 않아 이 거절을 앞서 잡지 못했다.

## Evidence And Usage

source30의 Host 계약40사례+accounting5 및 역사 positive15를 포함한 Rust 대조, admission, build20, Host8/Rust14 조립이 PASS했다. 로컬 조립도 실제 controller의 변경된 시간 계산 블록을 real budget read로 실행했다. 정책7/preface29/기존 normal-Lite는 변경 없는 범위의 증거로 재사용했다. build20은 20.670초, 실제 controller 시도는 19.888초였다.

누적 source30·전체32상한(내용 허용2, 사용0)·build20·proxy12·live10·offline41·control13·thread예약4/결속3·auth admission관측9다. credential storage read 실제 횟수는 미확정이다. clock-10/proxy12는 소진됐으며 합성2회는 미사용이다. 합성 검증과 H05 묶음 준비는 미완료이고 H05 replay/H10·Work Done·Owner 수락은 별도다.

원 승인 시각과 누적 사용량을 유지하고 누적 상한만28시간40분으로 반영했다. 구간 마감2026-10-25 00:40:41.443 KST, 외부 마감00:34:21 KST, 누적 예약을 뺀 실제 작업 cutoff00:06:23.302 KST였다. 2026-10-24 23:59:31 KST 종료 기록 기준 누적 잔여 41.169분(종료20분·불확실성14.30235분 포함)이다. 잔여 예산은 첫 실패 이후 추가 실행을 허용하지 않는다.

## Preservation And Cleanup

runtime/controller/proxy 및 모든 검사 process group 부재, controller closed/lease0, FD2개 발급/해제, 보호 인증 metadata 불변을 확인했다. inner stop8·process-ended9가 durable하다. outer 중복 stop 거절은 원 stop 손실이나 cleanup 미완료가 아니다. source30/build20·이전 source/build19 복구본·accepted binaries·epoch18 bytes를 확인했다.

활성 후보는 build20, 실제 epoch 포인터는 중단된 epoch-v19-mcp36다. 원본 실패 입력/계약/기록·격리 runtime 파일과 복구 자료를 Owner 처분 또는 별도 승인 조사 입력으로 보존한다. 소비자가 없는 task socket1개·빈 socket 디렉터리와 빈 wrapper home/tmp 디렉터리만 정리했다. 삭제 4항목, 이동0. 제품 Git publication/adopter 적용0.

상세 private-evidence/E059 [공개용 중립화]


### MCP38 Prepare Diagnosis And Offline Qualification — 2026-10-24T15:14:05.810006+00:00

Owner는 source31/전체33/build21/offline47/누적29시간45분을 승인했다. 원인 코드와 모델 호환성 진단 및 전체 prepare 오프라인 검증까지만 수행한다. 실제 retry/auth/provider 호출·도구 모드 변경·H05 replay/H10·Git publication은 포함하지 않는다. 기존 source30/build20와 실패 epoch19를 보존했고 source31 한 묶음을 예약했다. 예상30–50분은 신규 test harness 구성에 대한 판단이며 직전 build20 20.670초는 빌드만의 실측이다. 작업 중단한도60분과 기존 예약34.30235분을 유지하고 먼저 닿는 누적 제한을 적용한다. Owner 대기는 보수적으로 누적한다. work deadline 2026-10-24T16:11:23.302481+00:00, segment deadline 2026-10-24T16:45:41.443481+00:00, external deadline 2026-10-24T16:31:23.302481+00:00. 실제 epoch/권한 계약은 활성화하거나 수정하지 않는다.

검증 선택: 8개 도구 소스 조건의 분리, model requested/effective mode 및 가용성, clock/U2 × normal/Lite 정상4와 CodeModeOnly 거절2의 전체 prepare 경로. 기존 expiry/정책/전송 근거는 소스가 변하지 않은 범위에만 재사용한다. 최초 예상 밖 실패에서 멈추고 정확한 결과를 보존한다.


### MCP38 Offline Prepare Qualification — 2026-10-24T15:36:40.276273+00:00

Source31/build21과 오프라인6개 경로가 모두 예상 판정으로 PASS했다. 실제 ThreadManager/Live 구성에서 Direct 검사용 모델의 clock/U2 × normal/Lite는 manifest/handle 생성에 성공했다. CodeModeOnly의 clock/U2는 나머지7개 원인이 모두 없는 상태에서 effective mode code_mode_only로 거절됐다. 모델 모드 선택은 바꾸지 않았다. 원인8개/복수 원인 및 preflight mode 집중 검사도 PASS했다. native auth/catalog와 app RPC transport는 이6개에서 새로 실행하지 않았고, 합성 auth/source-derived catalog 및 기존 unchanged RPC 경계 근거를 분리했다. 과거 clock-10의 tool_mode 미보존 때문에 당시 원인을 소급 확정하지 않는다.

누적 source31/build21/offline47; live10/proxy12/control13/thread4/auth admission관측9/turn0/generation0은 불변이다. 실제 retry/모드 변경/H05 replay/H10/Git publication/adopter 적용0, Work Done/Owner 결과 수락은 별도다. 2026-10-25 00:36:40 KST 기준 잔여69.02분(예약34.30235분 포함), 이번 경과25.17분. 작업 cutoff01:11:23.302/구간01:45:41.443/외부01:31:23.302 KST이며 원 절대 millisecond 상한+승인65분으로 보수적 고정했다. 모든 실행 process/group 종료, protected auth metadata/accepted binaries/epoch19 불변, source30/build20 rollback bytes 및 source31/build21/6개 입력결과 보존 확인. 삭제0/이동0; candidate는 build21, actual epoch19는 stopped 그대로다. 자료/worktree는 후속 호환성 판단과 R1/Owner 수락까지 유지한다.

상세 private-evidence/E060 [공개용 중립화]


### MCP39 Direct Policy Offline Scope — 2026-10-24T15:57:26.040476+00:00

Owner 승인 source32/전체34/build22/offline53/누적30시간45분에 따라 원본 모델 정보를 보존하는 prepared Live 전용 Direct 정책과 오프라인 검증만 수행한다. 실제 retry/auth/provider/proxy 호출·새 actual epoch·H05/H10·Git publication은 제외한다. source31/build21 복구 bytes를 before-mcp39에서 검증 보존했고 source32 한 묶음을 예약했다. 예상40–60분은 구현·검사/컴파일 대기·기록 포함 판단값이며 직전 MCP38 25.17분을 참고했다. 작업 중단한도75분과 종료20분/불확실성14.30235분 예약을 보존하며 먼저 닿는 상한을 적용한다. 원 사용량과 Owner 대기를 보수적으로 누적하고 마감만 승인60분 안에서 조정했다. work 2026-10-24T17:11:14+00:00, external 2026-10-24T17:31:14+00:00, segment 2026-10-24T17:45:41.443000+00:00. 첫 실패 시 보정/재시도 없이 중단한다. 정책 집중 검사, 원본 CodeModeOnly clock/U2 normal/Lite 긍정4 및 무승인 거절2, manifest/전송 결속 검증과 build1회로 변경 경계를 확인하고 불변 인증/프록시/파일 권한 근거를 재사용한다.


### MCP39 First Compile Failure — 2026-10-24T16:03:43.333829+00:00

Direct 정책 source32 초안을 구현했으나 첫 집중 검사 컴파일에서 E0507로 실패했다. Owner의 첫 실패 중단 조건에 따라 보정·재시도 없이 중단했다. 테스트 본문, app 검사 컴파일, 오프라인6회, 후보 build22는 미실행이다. 적격성·Work 완료·Owner 수락을 주장하지 않는다.


누적 source32/build21/offline47, 실제 호출0. 2026-10-25 01:03:43 KST 잔여101.97분(예약34.30235분 포함). source31/build21 복구 및 source32 실패 입력/로그 보존, process/group 부재, 실제 epoch19/accepted 바이너리/인증 metadata 불변을 확인했다. 알려진 참조 전달 최소 보정은 미적용이며 source33/전체35 추가 승인 후 기존 build22/offline53 미사용 배정으로 재개할 수 있다. 전체 적격성·Work Done·Owner 수락은 아직 아니다.

상세 private-evidence/E061 [공개용 중립화]


### MCP40 Borrow Fix And Offline Resume — 2026-10-24T16:06:17.111688+00:00

Owner 승인 source33/전체35와 미사용 build22/offline53으로 재개한다. source32 E0507 원본을 before-mcp40에 보존하고 model_reasoning_effort 직렬화에 참조 전달만 보정했다. 예상20–35분은 보정·집중 검사/컴파일·오프라인6회·후보 build/기록 포함 판단값이다. 승인 관측 2026-10-24T16:05:35+00:00 기준 원 사용량과 Owner 대기를 보존했으며 기록 시점 잔여99.41분(종료20/불확실성14.30235분 포함)이다. 누적30시간45분·work 2026-10-24T17:11:14+00:00·external 2026-10-24T17:31:14+00:00·segment 2026-10-24T17:45:41.443000+00:00 유지. 첫 실패 중단, 실제 retry/auth/provider/proxy/H05/H10 별도이며 이번에 실행하지 않는다. 이전 MCP39 실패 원본은 불변 보존한다.


### MCP40 Offline Result — 2026-10-24T16:11:52.901618+00:00

source33의 참조 전달 보정 후 정책 집중 검사, 전체 prepare 오프라인6개 예상 판정 및 후보 build22가 PASS했다. 실제 retry/auth/provider/proxy0. 누적 source33/build22/offline53; 2026-10-25 01:11:52 KST 잔여93.81분(예약34.30235분 포함). 기존 마감/예약 유지. source31/build21·source32 복구 및 실패 원본, source33 검사 입력/결과를 보존했고 accepted 바이너리/epoch19/보호 인증 metadata 불변과 process/group 부재를 확인했다. native 실제 호환성·새 epoch admission·R1/Owner 수락·H05/H10·Work Done은 별도다.

상세 private-evidence/E062 [공개용 중립화]


### MCP41 Preparation Failure — 2026-10-24T16:27:01.710365+00:00

source34 후보 생성 중 Rust 삽입 위치 검사(예상1/관측0)에서 첫 실패로 중단. 소스 적용·build23·새 offline·proxy13·clock-11 모두0; source33/build22/offline53/live10/proxy12/thread4 그대로. 보정·재시도0. 2026-10-25 01:27:01 KST 잔여78.66분(예약34.30235분 포함), 작업 마감까지44.20분. 마감/예약 불변. 결과 private-evidence/E063 [공개용 중립화]


### MCP42 Preparation Failure — 2026-10-24T16:33:16.057422+00:00

기존 start 삽입 위치 보정 PASS 후 추가 turn 삽입 위치 검사(예상1/관측0)에서 첫 실패로 중단. 소스 적용·build23·새 offline·proxy13·clock-11 모두0; source33/build22/offline53/live10/proxy12/thread4 그대로. 보정·재시도0. 2026-10-25 01:33:16 KST 잔여72.42분(예약34.30235분 포함), 작업 마감까지37.97분. 마감/예약 불변. 결과 private-evidence/E064 [공개용 중립화]


### MCP43 Contract Input Failure — 2026-10-24T16:38:14.838517+00:00

남은8개 삽입 위치 live 확인 후 source34 적용 PASS. 첫 계약 검사에서 부모 증거 파일 재사용 경로 연결 누락(FileNotFoundError)으로 사례 평가 전에 중단했다. 실패 후 보정/재시도0. source34/build22/offline53/live10/proxy12/thread4; 추가 build/offline runtime/actual0. 2026-10-25 01:38:14 KST 잔여67.44분(예약34.30235분 포함), 작업 마감까지32.99분. 마감/예약 불변. 현재 source34는 미검증이며 build22와 검증된 쌍이 아니다. 상세 private-evidence/E065 [공개용 중립화]


### MCP44 Offline Result / Actual Hold — 2026-10-24T16:53:32.994472+00:00

source34의 계약·Rust admission·변경 UDS preface·Host/Rust parity·normal/Lite 전체 준비 검사와 build23이 모두 통과했다. source34 추가 변경0. 입력 참조142개와 actual helper 입력10개 확인. 20분 확보 마지막 시작 시각에 build 진행 중이어서 actual clock11/proxy13/epoch20/auth0. 2026-10-25 01:53:32 KST 잔여52.14분(예약34.30235분 포함), 작업 마감까지17.68분. 마감/예약 불변. 결과 private-evidence/E066 [공개용 중립화]


### MCP45 Actual Consume Refusal — 2026-10-25T00:42:04.101253+00:00

clock-11을 한 번 실행했으며 `turn/startPrepared`가 `prepared consume: prepared manifest/input drift`로 거절돼 첫 실패로 중단했다. RPC -32600과 오류 메시지 SHA256이 source 문구에 일치한다. 준비 당시 manifest·input과 소비 요청의 동일성을 묶어서 검사한 지점이며, 어느 피연산자 또는 필드가 달랐는지는 미확정이다. 실패 후 source/실행 helper 수정·재시도는0이다.

`turn/prepare`와 prepared 입력 예약1회까지 진행했다. model turn·generation·clock 도구 호출은0이다. 외부 control2회와 thread 예약/결속1회는 실제로 사용했으므로 무실행으로 해석하지 않는다.

## Verification And Timing

source35/build24, 계약37사례와 역사 positive16, Rust admission·parity, Host 실행 입력 positive1/negative8, Rust runtime/proxy14사례와 실제 helper 시간 경계6사례가 PASS했다. 변경 없는 Core 정책·proxy·normal/Lite 검증을 재사용했고 offline start55를 유지했다. build24는 20.112초였다. 이전 통과 증거는 전체 실제 consume 경로의 성공을 입증하지 않는다.

승인 시각2026-10-25 09:33:48 KST를 기준으로 준비10분+실행 여유21분을 확보했다. 누적 상한38시간38분34초(139114초), 작업 마감10:04:48 KST, 외부 마감10:24:48 KST, 구간 마감10:39:15.443 KST로 고정했다. 기존 예약34분18.141초와 나머지 상한은 유지했다. 실제 runtime 시작은09:39:52.568 KST, 작업 마감까지 1495.432초(24분55.432초)가 남았으므로21분 gate를 충족했다. 실제 controller는 20.973초 뒤09:40:11 KST에 종료됐다. 종료 기록 시각 09:42:04 KST 기준 누적 잔여 57.189분에는 기존 예약이 포함된다. 잔여 시간은 추가 실행 권한이 아니다.

누적 source35/전체37상한(내용 보정 사용0)·build24·proxy13·live11·offline55·control15·thread예약5/결속4·auth admission관측10이다. credential storage read 실제 횟수는 미확정이다. 합성 U2·H05/H10은 수행하지 않았다. Work는 Active, R1 REVISE / not qualified이며 Owner 수락·Done·Git publication·adopter 적용은 수행하지 않았다.

## Preservation And Cleanup

runtime/controller/proxy와 검사 process group 부재, controller closed/lease0, FD2개 발급/해제, 보호 인증 metadata 불변을 확인했다. inner stop9·process-ended10을 보존했다. outer 중복 stop 거절은 원 stop 손실이 아니다. source35/build24, source34/build23 복구본, accepted binaries, parent epoch19 bytes를 검증했다.

활성 후보는 source35/build24, epoch 포인터는 중단된 epoch-v20-mcp45다. 후보·실패 입력/계약/기록과 복구 자료는 Owner 처분 또는 별도 승인 조사에서 소비할 정확한 증거로 보존한다. 두 worktree에도 고유 미커밋 작업이 있어 유지한다. 사용 종료를 확인한 task socket과 빈 전용 디렉터리 4항목을 삭제했으며 이동0이다. 삭제 목록과 상세 근거는 result.json에 기록했다.

상세 private-evidence/E067 [공개용 중립화]


### MCP46 Normal Roundtrip Non-Reproduction — 2026-10-25T00:59:10.147280+00:00

normal 정상 JSON 왕복이 통과했지만 기존 manifest/input drift가 재현되지 않아 승인된 미재현 중단 조건을 적용했다. Lite는 시작하지 않았다. 원인 해결·실제 clock 성공·전체 normal/Lite 검증 완료로 판정하지 않는다. 중단 후 source/실행 helper 변경과 재시도는0이다.

## Change And Evidence

source36은 Core 동일성 진단 기록과 offline 정상 왕복 검사만 추가한다. 원래 manifest/input 동일성 조건과 handle 제거 순서는 byte 비교로 불변을 확인했다. 진단에는 manifest_equal·input_equal, 고정된22개 schema 구간의 자료형·양쪽 digest·동일성만 남기며 원문 값이나 임의 native key를 기록하지 않는다.

검사는 typed prepare 요청 → Core prepare → 실제 OutgoingResponse 직렬화 → 고정한 Host JSON 함수와 CPython 왕복 → 실제 ClientRequest decoder → Core consume 순서다. 실제 App Server stdio loop나 native account/catalog 경로를 실행한 것은 아니다. clock 입력97바이트는 원 실패 입력과 같고, 인증·config·catalog는 합성 fixture다.

normal에서 manifest_equal=true, input_equal=true,22개 구간 digest·자료형 동일, consume 성공을 확인했다. 로컬 turn 예약 callback1회만 실행했고 실제 model turn·provider request·도구 dispatch는0이다. 기존 오류는 미재현이므로 특정 native manifest 필드 또는 JSON 왕복 자체를 원인으로 확정할 수 없다. 실제 실패의 manifest 원문이 없어 이번 합성 데이터로 원 실패 입력을 그대로 재구성하지 못했다. Lite의 정상 consume은 이번에 미검증이다.

build25 63.785초, test binary compile 43.621초, normal1회 6.485초가 PASS했다. Core 정책·proxy·기존 변조 거절 증거는 변경 없는 조건에 한해 재사용했고 새 실제 launch 계약은 만들지 않았다. git diff --check는 양쪽 저장소에서 통과했다.

## Accounting And Boundary

승인 시각2026-10-25 09:48:27 KST에 누적 사용136065.557초를 유지하고 작업40분과 기존 예약34분18.141초를 확보했다. 새 누적 상한은140523.698초(39시간2분3.698초), 작업 마감10:28:27 KST, 외부 마감10:48:27 KST, 최종/구간 마감11:02:45.141 KST다. 종료 기록 09:59:10 KST 기준 누적 잔여 63.583분에는 예약이 포함된다. 남은 시간·횟수는 미재현 중단 뒤 추가 실행 권한이 아니다.

누적 source36/상한36, 전체 보정 사용36/상한38(내용 보정 사용0), build25/25, offline start56/57이다. 이번 합성 thread1·로컬 consume 예약1을 추가한 관측 누적은 offline thread55·simulated turn31이다. 이는 실제 model turn이 아니며 과거 실제 epoch journal을 수정해 반영하지 않았다. 실제 live11·proxy13·thread예약5·control15·auth admission관측10·model turn/generation0은 그대로다. credential storage read 실제 누적 횟수는 미확정이다. 실제 실행·합성 U2·H05/H10·review·Git publication·adopter 적용은0이다.

준비 스크립트 초안 편집 중 문자열 치환 전제조건1회가 적용 전에 거절됐다. 그 호출의 파일 변경·저장소 적용·검증 시작은0이었고, 실행된 검증의 수정·재시도에 해당하지 않는다.

## Preservation And Cleanup

build/compiler/normal 및 child process group 부재를 확인했다. source36/build25, source35/build24 복구본, 원 MCP45 실패·epoch20, accepted binaries bytes를 검증했다. Core 변경은 진단 helper와 호출 추가 외에 없음을 before/after 비교로 확인했다.

현재 후보는 진단용 source36/build25이고 실제 epoch는 중단된 epoch-v20-mcp45를 유지한다. 원 실패와 이번 합성 fixture 차이 분석 및 Owner 처분을 위해 정확한 source·복구본·왕복 frame·진단 결과·fixture home과 두 고유 미커밋 worktree를 보존한다. 소비자가 없는 빈 case tmp 디렉터리 1개를 삭제했고 이동0이다. 다른 활성 경로는 바꾸지 않았다. Work는 Active, R1 REVISE / not qualified이며 Owner 수락·Done은 수행하지 않았다. 현재 adopter 업데이트는 권고하지 않는다.

상세 private-evidence/E068 [공개용 중립화]


### MCP47 Lite Continuation And Decoder Gap — 2026-10-25T01:20:08.968204+00:00

Owner의 재개 지시에 따라 기존 마감·상한 안에서 남은 offline1회로 Lite 검증을 완료했다. source36/build25를 재사용했고 추가 source 수정·제품 build·실제 실행은0이다. Lite는 0.890초에 통과했으며 manifest_equal/input_equal=true,22개 구간 digest 동일, 로컬 consume 예약1회, 실제 model turn/provider/dispatch0이다. MCP46 normal과 합쳐 두 합성 모드 모두 원 실패를 재현하지 못했다.

## Narrowed Evidence And Gap

추가 정적 대조에서 실제 stdio는 app-server-transport/src/transport/mod.rs:217의 JSONRPCMessage decoder를 거치지만 현재 fixture는 JSONRPCRequest를 직접 읽는 차이를 확인했다. 이 바깥 untagged envelope decoder는 아직 검증하지 않았다. 실제 request processor는 이후 ClientRequest를 만들고 params를 consume으로 넘기며, 확인한 경로에서 manifest/input의 명시적 변형은 찾지 못했다. decoder 차이가 원인이라는 실행 증거는 아직 없다.

보존된 실제 logs DB와 WAL28개 frame의 checksum을 확인하고 마지막 commit까지 메모리에서 복원해 읽었다. logs0행이며 원본 DB/WAL/SHM hash는 불변이다. 원문 로그·인증정보는 출력하지 않았다. 따라서 여기서 원 실패 manifest를 추가 복원할 수 없다. native config/catalog와 합성 입력 차이도 남아 있다.

두 decoder 지점을 바꾸는 outer-decoder-proposal.diff와 next-plan.md를 작성했지만 적용하지 않았다. 제안은 source37/전체39/offline59, 제품 build25 재사용, test binary 재컴파일1회와 normal/Lite 각1회 상한이다. 첫 검증 실패 또는 미재현에 중단하고 실제 실행·합성 U2·H05/H10은 계속 제외한다. 예상10–15분, 작업 상한30분+기존 예약을 다음 승인 시점 기준으로 확보하는 제안이며 아직 승인된 상한이 아니다.

## Accounting And Closeout

누적 source36/36, 전체36/38, build25/25, offline57/57이다. 합성 관측 누적 thread56·simulated turn32이며 실제 journal을 고쳐 반영하지 않았다. 실제 live11/proxy13/thread예약5/control15/auth admission관측10/model turn·generation0은 그대로다. 원 누적 상한140523.698초, 작업 마감10:28:27 KST, 외부10:48:27 KST, 예약 포함 최종11:02:45.141 KST를 유지했다. 종료 기록 기준 잔여 42.603분에는 예약34분18.141초가 포함되며, 횟수 상한 초과 실행 권한은 없다.

Lite 및 child process group 부재, source36/build25 불변, source35/build24 복구본, epoch20·MCP45 실패 증거 불변, 양쪽 git diff --check를 확인했다. 빈 case tmp1개를 삭제했고 이동0·다른 활성 경로 변경0이다. 정확한 두 모드 frame·진단/실패 자료·복구본은 미적용 decoder 검증 제안과 Owner 처분의 입력으로 보존한다. Work는 Active / R1 REVISE / not qualified다. 현재 adopter 업데이트는 권고하지 않는다.

상세 private-evidence/E069 [공개용 중립화]


### MCP48 Outer Decoder Verification — 2026-10-25T01:32:05.131112+00:00

승인된 두 outer decoder 수정·test 재컴파일·normal 검증·정리를 완료했다. normal consume은 6.372초에 PASS했지만 원래 manifest/input drift는 재현되지 않았다. 첫 미재현 중단 조건에 따라 Lite는 시작하지 않았다. 원인 미확정이며 Work는 Active / R1 REVISE / not qualified다.

## Change And Evidence

prepared_offline_tests.rs의 prepare/consume 두 지점을 승인된 patch 그대로 JSONRPCMessage → Request → ClientRequest 순서로 바꿨다. test source만 변경했고 Core 동일성 predicate·제품 source·Host는 그대로다. test binary 재컴파일1회는 15.694초에 통과했으며 제품 build25 세 executable은 hash 불변이다.

normal 왕복에서 manifest/input 동일,22개 비교 구간의 type·digest 동일, consume 성공과 로컬 예약1회를 관측했다. 실제 model turn/provider 요청0, wire/dispatch/auth-lifetime 관측0이다. 기존 합성 normal 입력에서 바깥 decoder를 포함해도 실패가 발생하지 않는다는 증거다. 원래 native config/catalog의 정확한 manifest는 보존되지 않아 어떤 값이 달랐는지 아직 특정할 수 없다. Lite의 새 decoder 경로와 실제 stdio 전체 경로를 검증한 결과로 확대하지 않는다.

같은 합성 입력을 다시 실행할 구체 근거가 없어 추가 반복을 권고하지 않는다. 후속 원인 판별은 실제/합성 입력 차이를 특정할 수 있는지 또는 제한된 진단 관측이 필요한지 별도 범위를 먼저 정해야 한다. 이 결과는 추가 수정·실제 실행을 승인하지 않는다.

## Limits And Time

Owner 승인 원문과 마감은 mcp48-authorization.json에 보존했다. 누적 source37/37, 전체 보정37/39, 제품 build25/25, offline58/59이며 미사용 offline1회가 있어도 미재현 중단 조건이 우선한다. test 재컴파일은1/1이다. 실제 실행·U2·H05/H10·review·Git publication은 이번에0이며 기존 실제 장부는 불변이다.

승인10:28:18.435 KST 기준 작업 마감10:58:18.435, 종료 예약 마감11:18:18.435, 불확실성 예약까지 최종11:32:36.576 KST다. 기존 누적 사용량을 유지한 총 상한은 142315.133초이며 예약은34분18.141초다. 예상10–15분에 대해 승인부터 종료 기록까지 3.78분이다. 작성·compile·검증·대기·정리를 포함한 순차 경과시간이며 검증이 미재현으로 끝나 Lite를 생략했다. 누적 사용 2311.395분, 남은 상한 60.524분은 재개 허가가 아니다.

종료 스크립트 저장용 첫 shell/Python 명령은 문자열 구분자 오류로 실행 전 parse 실패했다. 파일 생성·source 변경·검증 재실행은 없었으며 저장 방식만 고쳐 종료 기록을 완료했다.

## Preservation And Cleanup

compile/test process group 부재와 양쪽 git diff --check를 확인했다. source37, build25, source36 복구 파일, source35/build24 기존 복구본, epoch20·MCP45 실패·보존 logs DB/WAL/SHM의 hash를 확인했다. 원래 기록은 수정하지 않았다.

보존: source37/build25와 test executable은 후속 qualification 또는 Owner 폐기 판단까지, before-mcp48의 source36 원문은 이번 두 지점 rollback 처분까지, 원 실패와 정확한 합성 frame은 원인 판별/결과 처분까지 필요하다. 활성 경로 이동·변경0. 종료 process가 사용하지 않고 열린 파일이 없는 빈 case tmp1개만 삭제했다. Work Done/Owner 수락/STATUS 변경은 없고, 현재 adopter update는 권고하지 않는다.

상세 private-evidence/E070 [공개용 중립화]


### MCP49 Diagnostic Initialization Failure — 2026-10-25T02:01:04.153911+00:00

승인된 diagnostic-only 실제 실행1회를 수행했으나 initialize 중 runtime이 종료됐다. manifest 비교까지 도달하지 못했으므로 원래 manifest/input drift 원인은 미확정이다. 첫 실패에서 중단했으며 수정·재시도하지 않았다. Work는 Active / R1 REVISE / not qualified다.

## Finding And Evidence

Driver 구현에서 새 start `clock-12`를 proxy preface 허용 목록에 추가하지 않은 누락을 확인했다. `private-evidence/E161` 498행 이하 목록은 `clock-11`까지만 허용한다. 실제 입력은 clock-12이며 proxy의 `Error: prepared connection failed`, controller FD 요청/예약/발급0, runtime initialize 종료 관측과 일치한다. 이 결함 확인은 보존 source의 정적 비교이며 별도 재현 실행은 하지 않았다. runtime stderr는49 bytes와 digest만 보존돼 세부 dynamic 거절 branch를 직접 확인한 로그는 없다. [공개용 중립화]

집중 검증은 Core consume·저널·숫자 표현을 확인했지만 새 start를 사용하는 proxy preface 경로를 포함하지 않았다. start 입력이 바뀌었는데 기존 proxy evidence를 재사용한 Driver의 검증 선택 누락이다. 따라서 준비 검사 PASS를 실제 진단 경로 적격성으로 확대할 수 없다.

source38에는 계약에 결속된 진단 모드, 원래 동일성 검사를 유지한 강제 consume 종료, turn/generation/dispatch 예약 거부, models/accounts 외 HTTP 거부, 값·키를 남기지 않는 비교 metadata를 넣었다. build26은 65.615초, test compile은 46.218초에 통과했다. 집중 offline1회는 6.786초에 통과했다. Python/Rust 같은 저널19사례, 일치 시 강제 종료/예약0, 불일치와 재소비 거부, 기록 실패 시 예약0, 숫자 표현·정밀도 변화 분류를 검증했다. 원 manifest 실패의 재현으로 해석하지 않는다.

## Actual Effects And Limits

실제 controller 경과 19.331초. runtime1/proxy1/auth admission 관측1/control(models) 예약1을 추가했다. controller의 외부 연결용 FD 발급은0이며 thread·prepare·input·model turn·generation·dispatch 추가는 모두0이다. 장부의 `control_sends`는 예약 기반 카운터이므로 이번1회를 성공한 외부 HTTP 송신으로 읽지 않는다. credential storage read 실제 횟수는 미확정이다.

누적 source38/38, 전체 보정38/39, build26/26, offline59/59, runtime12/12, proxy14/14, thread예약5/6, control예약16/17, auth admission11/11이다. 남은 수치나 시간은 재시도 허가가 아니다. U2·H05·H10·review·Git publication·Owner 수락·Work Done은 수행하지 않았다.

승인10:43:48.943 KST부터 종료 기록까지 17.25분(작성·빌드·검증·대기·실행·정리 포함)이다. 예상25–40분보다 일찍 실패 중단했다. 작업60분 상한과 기존 예약34분18.141초를 유지했고, 실제 시작 시 작업 마감까지 45.90분이 남아21분 gate를 충족했다. 총 상한 145045.641초, 누적 사용 140422.711초, 남은 상한 4622.930초다.

## Preservation And Cleanup

runtime/proxy/controller 및 build/test process와 process group 부재, controller closed·lease0, 보호 인증 metadata 동일, auth-boundary violation0을 확인했다. source38/build26, source37/build25 복구본, accepted binary와 parent epoch20·MCP45 원 실패 bytes를 검증했다. source와 실행 helper는 실패 뒤 변경하지 않았다. 두 저장소 git diff --check도 통과했다.

보존: 현재 고유 미커밋 구현이 있는 두 worktree, 정확한 실패 입력·계약·metadata·검증 결과, source37/build25 복구본은 Owner 실패 처분 또는 별도 승인 보정의 입력이므로 유지한다. 후보는 source38/build26으로 바뀌었고 새 epoch21은 중단 상태이며 epoch20은 그대로다. 이동0. 소유권·process 부재·열린 handle 부재를 확인한 socket과 빈 작업 디렉터리 5항목을 삭제했다. 상세 삭제·보존 목적·종료 조건은 result.json에 기록했다.

후속 실행 전에는 새 start의 proxy preface admission을 포함한 범위와 소모 상한을 별도로 정해야 한다. 이번 결과는 source 보정이나 실제 재시도를 승인하지 않는다.

상세 private-evidence/E074 [공개용 중립화]


### Execution Method Correction — 2026-10-25T02:09:42.113713+00:00

Owner가 반복 실험/실패와 과도한 지연을 지적하고 진행 방식 개선 후 계속을 요청했다. 실제 배정 clock-12가 기존 proxy의 거부 fixture와 동일하다는 source/input 모순을 확인했다. 진도 기준을 실제 manifest 차이 관측으로 두고, 새 후보의 정확한 실행 입력을 production preface/launch/journal/Host 경로에 연결해 사전 확인하도록 변경안을 준비했다. 같은 합성 입력 반복과 불필요한 full 검증은 추가하지 않는다. 변경 source·새 native 실행·한도 증액은 이 기록에 포함하지 않는다.

계획·근거·후속 범위: private-evidence/E072 [공개용 중립화]
기계 대조: private-evidence/E073 [공개용 중립화]
실제 배정 입력의 회귀 검사 초안(미적용·미실행): private-evidence/E071 [공개용 중립화]


### Local Admission Patch Prepared — 2026-10-25T02:18:39.527455+00:00

Owner의 이 작업 진행 지시에 따라 실제 승인 입력을 production proxy에 연결하는 세 파일 patch와 로컬 검사 묶음을 준비했다. source38/build26/offline59 상한 소진으로 source39/전체39, build27, offline61 및 로컬 작업60분 한도 승인을 요청한 상태다. 예상30–50분은 낮은 신뢰의 판단값이며 실제 인증·native 재실행은 제외한다. 아직 source 적용·compile·테스트는 실행하지 않았다. 기존 source38 전체8개 digest 동일, patch 적용 가능 여부와 runner 구문 확인은 통과했다. 상세 계획과 미적용 patch: private-evidence/E076 / private-evidence/E075 [공개용 중립화]


### Local Proxy Admission Verified — 2026-10-25T02:25:20.696754+00:00

Owner가 source39/전체39, build27, offline61의 로컬 수정·검증 묶음을 명시 승인했다. 검증된 authorization의 allowed_next_start를 production proxy에 직접 전달하도록 세 파일을 수정했다. wire JSON은 이 메모리 필드를 주입할 수 없다. 실제 MCP49 proxy/runtime 입력을 production 승인 함수와 bind_stream에 순서대로 통과시켰고 새 거부 사례와 기존31개 preface 사례도 확인했다.

한 번의 test binary compile(208.390초)과 두 집중 검사(4.212초/2.020초)가 통과했다. production build26, Core/Host, 중단된 epoch20/21은 그대로다. 실제 인증·외부 통신·native/model turn/generation/dispatch 추가0. 실제 manifest 차이 관측은 남아 있으므로 live qualified나 Work Done으로 처리하지 않는다.

준비부터 종료까지 12.69분(예상30–50분, 승인 누적 중단 한도60분). 복구본·실제 입력·검증 결과를 보존하고 사용이 끝난 socket-root marker와 빈 디렉터리2항목을 삭제했다. active 경로 이동0. 세부 결과: private-evidence/E077 [공개용 중립화]


### Exact Candidate Diagnostic Proposal — 2026-10-25T02:48:35.695021+00:00

Owner의 계속 지시에 따라 source39 이후의 새 실제 진단 후보를 준비했다. epoch21/clock-12 재사용 없이 epoch22/clock-13/s4-15로 연결하고, 공통 배정 입력에서 Host/Rust 검증 값을 생성하며 같은 materialized input을 로컬 검증한 뒤에만 인증을 시작하는 안이다. 변경 대상 두 파일, 재사용/집중 검사, 실행 순서, source40/전체40/build28/offline63/native13/proxy15/thread6/control18/auth admission12 한도를 구체화했다. 새 한도 승인 전 source 수정·build·실행·인증은 하지 않았다. 계획: private-evidence/E078 [공개용 중립화]

MCP51 준비 체크포인트: 두 파일 미적용 patch template과 공통 배정 입력을 준비했고 두 저장소 git apply --check 및 Python 구문 확인을 통과했다. 실제 후보의 native launch와 journal parity를 기존 app-server 집중 검사에 연결하는 초안을 포함한다. 승인 hash/cap/deadline은 아직 미정이며 source39는 그대로다. 준비 10.92분을 기존 누적 사용량에 더했고 추가 한도 답변을 기다린다. 상세 private-evidence/E079 [공개용 중립화]

## MCP51 Diagnostic Reproduction — 2026-10-25

실제 manifest 불일치를 재현했다. 진단 목적은 달성했지만 원인 수정이나 live 적격 판정은 아니다.

- source40/build28 및 실제 launch 입력의 로컬 admission 검사 통과. app/proxy 집중 검사 2개 프로세스를 실행했고, 변경하지 않은 검증 근거는 재사용했다.
- 실제 runtime 1회에서 prepared manifest의 `/snapshot/context/config` 내부 값 한 건이 object → integer로 달랐다. input 및 다른 독립 section은 일치했다.
- Python JSON 재전송에서 숫자 표현·값·비숫자 값 변화는 0이었다. Rust가 예상 manifest를 자체 JSON 직렬화·역직렬화해도 동등하지 않았다.
- 따라서 다음 확인 범위는 Rust config 표현과 JSON 변환이다. 정확한 config 필드·원본 값은 수집하지 않았고, 특정 라이브러리나 변환 경로를 최종 원인으로 확정하지 않았다.
- 원래 manifest guard가 거절했고, 모델 턴·generation·dispatch는 모두 0이다. control 예약 2회, 외부 연결 FD 발급/반환 각 2회, auth admission 1회였다. credential 저장소의 실제 read 호출 수는 계측하지 않았다.

실제 controller 실행 39.68초. 승인부터 보존·종료 확인까지 14.06분(순차 build·검사·기록·대기 포함). 사전 예상 30–50분, 작업 중단한도 60분과 구별한다. 누적 활동 2378.04분, 전체 상한 잔여 80.24분이며 추가 실행 승인을 뜻하지 않는다.

보존: 두 작업 checkout, source40/build28, source39/production build26 복구본, 정확한 입력·진단 결과·epoch22 journal을 확인했다. 보호 대상 인증/config metadata와 epoch20/21은 변하지 않았다. 모든 실행 process/group 종료를 확인했다. 현재 candidate는 source40/build28, epoch22는 stopped다. 기존 경로 이동은 없다.

삭제: 사용이 끝난 cfnt51 socket/root, cfa51 소유 표식/root, 실제 검사 HOME의 apply_patch 링크·빈 lock과 빈 디렉터리, 실제 실행 scratch/tmp. 각 대상의 소유·process 종료·열린 handle 부재를 확인했다. 고유 증거와 복구본은 다음 로컬 재현 및 Owner 판단의 입력이므로 유지한다. 상세 경로는 result.json에 기록했다.

Work는 Active / not qualified다. 다음 제안은 실제 인증·네트워크 없이 합성 config의 Rust JSON 왕복을 최소 재현하여 수정 위치를 결정하는 것이다. 이번 승인 범위의 실행은 종료했다.

Private evidence: `private-evidence/E080`; exact diagnostic: `private-evidence/E023`. [공개용 중립화]

## MCP52 Local Config Reproduction — 2026-10-25

합성 config의 object→integer 불일치를 재현했다. 원래 live 실패와 같은 형태지만 원래 필드와 생성 경로까지 확정하지는 않았다.

`serde_json` arbitrary_precision 숫자 `7` → 일반 TOML serializer → `{integer: {"$serde_json::private::Number": "7"}}` → JSON 역직렬화 → `{integer: 7}`. 정상 TOML integer는 왕복 후 동일했다. JSON 재해석만으로 정규화하면 특별 table과 scalar가 같은 값이 되는 충돌도 실행으로 확인했다.

추천은 prepared manifest의 config를 형식 표식과 TOML 문자열로 보존하는 것이다. 이 표현은 합성 8개 경우에서 JSON/TOML 문자열 왕복, 문자열 변경 탐지 및 값/타입 구별을 통과했다. production에는 적용하지 않았다. 한 파일 patch와 범위·검사·리스크는 repair-proposal.md 및 proposed-source41.patch에 있다. patch 적용 가능성 검사는 통과했다.

이번 작업에서 Driver가 만든 실행 준비 오류 2건이 있었다. 첫 compiler는 새 sandbox의 상위 경로 읽기 누락 상태에서 dyld abort했다. 해당 항목 복원 후 compile은 통과했지만 fixture가 단일 값 파서로 TOML 문서를 읽어 실패했다. toml::from_str로 수정한 최종 fixture는 통과했다. 오류·입력·각 실행 결과는 덮어쓰지 않고 보존했다. 직접적인 dyld 원인 전체를 확정했다고 주장하지 않는다.

독립 진단 compile 3회(성공2), fixture process 2회(성공1). 제품 source 수정0·생산 build0·native/auth/network/model turn/generation/dispatch0. 기존 source40/build28 및 epoch20/21/22 journal은 그대로다. 누적 제품 장부를 reset하지 않았으며 독립 진단 시도는 별도 계수로 공개한다. 이번 활동 10.76분, 기존 포함 총 활동 2388.81분, 전체 상한 잔여 69.48분이다. Owner 대기 시간은 제외했다.

보존: 성공 재현 binary/source/로그, 검토용 한 파일 patch, 실패 입력과 로그 및 기존 task 복구본. 다음 로컬 수정 검증과 Owner 판단이 consumer다. 활성 제품 경로 변경·이동 없음. 삭제: 실패 fixture binary, 소비가 끝난 xcrun lookup cache, 빈 HOME/tmp(소유·process 종료·열린 handle 부재 확인). Work는 Active/not qualified이고 실제 원인 수정·live 적격은 미완료다.

Evidence: `private-evidence/E082`; proposal: `private-evidence/E081`. [공개용 중립화]

## MCP53 Config Representation Repair — 2026-10-25

config의 전달 규격을 수정했고 로컬 검증을 통과했다. `prepared.rs` 한 파일에서 config를 `{encoding: toml-v1, document: TOML text}`로 보존한다. JSON은 문자열을 그대로 전달하고, prepare·consume·dispatch는 같은 표현을 비교한다. config 값·타입 변경 및 기존 manifest/input 불일치 거절은 유지한다.

- 새 Core 회귀 검사 2개 통과: 원래 숫자 객체 변환 반례, JSON 왕복 안정성, table/scalar 구별 및 값 변경 탐지.
- 기존 실제 config loader → prepare → Python JSON echo → consume 경로 1회 통과. 합성 desktop 숫자7을 넣었고 loader 후 숫자 표현은 `private-number-table`였다. manifest와 input 모두 일치했으며 diagnostic 종료 전 모델 턴 예약0·provider 요청0·dispatch0이었다.
- 변경하지 않은 source40 proxy admission·parent journal 근거와 MCP52의 합성 표현8개 경우는 재사용했다. 전체 검사나 native 재실행은 하지 않았다.

이 단계에서 source41 한 파일 수정, test build29 한 묶음, offline process2를 실행했다. production build28/source40 binary는 교체하지 않았고 실제 인증·외부 네트워크·모델 턴은 0이다. 이것은 source41의 로컬 표현 수정 검증이며 실제 native 성공/전체 live 적격은 아니다.

활동 10.33분(compile·검사·기록 포함), 누적 2399.13분, 기존 전체 상한 잔여 59.15분. 예상15–25분과 중단한도30분을 구별하며 Owner 대기는 제외했다.

보존: source40 원문/mode, source41 변경과 정확한 test binary·입력·결과, 기존 production build28와 보호 journal. 실행 process/group 종료와 복구본 hash/mode를 확인했다. 활성 경로는 prepared.rs와 test binary만 바뀌었고 경로 이동은 없다. 사용이 끝난 빈 fixture tmp만 삭제했으며 고유 검사 결과와 복구본은 다음 qualification/Owner 판단의 consumer가 있어 유지한다. Work는 Active/not qualified다.

Evidence: `private-evidence/E083`. [공개용 중립화]

## MCP54 Native Verification Proposal — 2026-10-25

source41 로컬 수정 검증 다음의 native 진단 계획을 준비했다. 실제 인증/GET2개/runtime1회 범위는 아직 명시적 승인 전이다. source/build/epoch/auth/network 실행0이며 기존 제품 계수는 변경하지 않았다. 모델 턴0을 유지하는 제안, 3분 진단/5분 진입 여유 및 보호 예산 유지 조건은 `private-evidence/E084`에 있다. 검토용 allocation patch는 미적용이다. 이번 계획 활동 4.81분을 기존 누적 활동에 더했고 전체 잔여는 54.35분이다. [공개용 중립화]

## MCP54 Native Identity Verified — 2026-10-25

config 전달 규격 수정 후 실제 native 경로에서 manifest와 input이 일치했다. 이번 동일성 진단은 통과했으며 전체 live 적격 판정은 아직 하지 않는다.

- source42/build30 및 같은 launch/spec의 로컬 admission 통과. Python/Rust budget 21 cases, native launch positive/negative 및 proxy preface를 검사했다.
- 실제 runtime 1회에서 manifest_equal=true, input_equal=true, Rust 자체 JSON 왕복 동일성을 확인했다. 차이 목록은 비었고 Python 전달의 숫자 표현·값·비숫자 변화는 모두 0이었다.
- prepared diagnostic complete; no turn reserved 종료를 확인했다. 모델 턴·generation·dispatch는 모두 0이다. auth admission 1회, control 예약2회, 외부 FD 발급/반환 각2회였다. credential 저장소 read 호출 수는 계측하지 않았다.
- runtime/proxy를 포함한 process/group 종료, FD lease0 및 보호 인증/config metadata 불변을 확인했다. 재시도하지 않았다.

실제 controller 실행 40.05초(로컬 admission 포함), 승인부터 보존·종료 확인까지 5.80분이다. 예상10–18분, 승인 시 계산한 작업 중단한도18.96분과 구별한다. 누적 전체 잔여는 47.46분이며 추가 실행 승인을 뜻하지 않는다.

보존: source42/build30, 정확한 입력·검증·실제 진단 결과·stopped epoch23과 source41/build28 복구본. 기존 epoch20/21/22는 불변이다. 현재 두 checkout은 미완료 Work와 후속 qualification의 입력이므로 유지한다. 고유 결과와 복구본은 Owner 판단 및 승인된 후속 작업까지 보존한다.

활성 상태 변경: 두 allocation source와 production/test binary가 새 후보로 바뀌었고 epoch23을 생성·종료했다. 경로 이동은 없다.

삭제: 사용이 끝난 cfnt54 socket/root, cfa54 소유 표식/root, 검사 HOME의 링크·빈 lock 및 빈 디렉터리, 실행 tmp. 소유·process 종료·열린 handle 부재를 먼저 확인했다. 상세 대상은 result.json에 있다.

Work는 Active / not qualified다. 이번 승인 범위는 완료했으며 모델·도구 end-to-end 실행은 별도 후속 범위다. review·Git publication 및 Owner 결과 수락은 하지 않았다.

Evidence: `private-evidence/E085`; exact diagnostic: `private-evidence/E024`. [공개용 중립화]

## MCP55 Clock Execution Proposal — 2026-10-25

MCP54 실제 동일성 통과를 재사용해 실제 clock 한 턴의 후속 계획을 준비했다. 제품 source/build/실행은 변경하지 않았다. Host/Rust 두 파일의 새 epoch24 계약, source43/build31/offline70 및 runtime1·control2·generation최대2·clock dispatch1이 제안 범위다. 예상20–30분/작업 중단35분이며 기존 보호 예약34.30235분을 유지하기 위해 누적 상한+30분을 제안했다. 아직 실행·상한 변경 승인은 없다. 계획 활동3.20분을 누적해 기존 잔여43.45분, 예약 제외9.15분이다. 상세: `private-evidence/E086`. 기존 Work Active/not qualified와 stopped epoch23을 유지한다. [공개용 중립화]

## MCP55 Pre-Build Failure — 2026-10-25

Driver가 생성한 build helper의 카운터 검사 오류로 compiler 실행 전에 중단했다. build.py의 시작 조건은 현재 build30이어야 하는데, 순차 문자열 치환이 그 값을31로 바꾸었다. 실제 장부30과 달라 AssertionError가 발생했다. 제품 소스의 compile 실패로 분류하지 않는다.

source43 두 파일 변경은 적용했다. 기존 diagnostic 함수가 변경되지 않았음을 정적으로 확인했지만 새 clock 계약은 아직 compile·실행 검증 전이다. production binary는 build30 그대로다. source42/build30 복구 bytes/mode, 현재 source43 및 보호 epoch20–23을 검증 보존했다.

실제 compiler/build process0, offline 검사0, native/auth/network/model turn/dispatch0. build31/offline3/actual-clock1 배정은 미사용이다. 첫 실패 중단 조건에 따라 helper를 고치거나 재시도하지 않았다. 실패 helper 원문과 오류 위치, 한 줄 미적용 patch를 보존했다.

제안 patch는 build.py의 사전조건31→30 한 줄뿐이다. 제품 source43·실행 범위·예산·미사용 배정은 바꾸지 않는다. 이를 적용한 재개는 첫 실패 중단에 대한 Owner 결정 뒤에만 가능하다. 같은 source43 묶음의 실행준비 오류 보정으로 별도 helper correction1을 공개하고 source/build 카운터를 숨겨 재설정하지 않는다. 다음 실제 실패도 중단한다.

이번 승인부터 기록까지 5.76분. 원 작업35분 중 미사용 29.24분, 누적 전체 잔여 67.69분이다. Owner 대기는 제외하며 기존 사용량·보호 예약을 유지한다. 재개 시 예상15–25분은 남은 build·집중검사·실제 한 턴·기록에 대한 판단이고, 기존 작업 한도 잔여를 넘기지 않는다.

보존: 미검증 source43, 현재 production build30, source42/build30 복구본, 승인·오류·한 줄 patch 및 이전 검증 근거. 활성 소스는 source43이며 경로 이동0·삭제0이다. 새 compiler/test/runtime scratch나 socket이 생성되지 않아 이번에 정리할 실행 임시 파일은 없다. Work는 Active/not qualified다.

Evidence: `private-evidence/E088`; proposed fix: `private-evidence/E087`. [공개용 중립화]

## MCP55 Native Proxy Failure After Resumption — 2026-10-25

한 줄 build helper 수정 후 build31과 로컬 검사3회는 통과했다. 실제 clock 실행은 initialize 단계에서 proxy의 EPERM으로 중단됐고 모델 턴에는 도달하지 않았다. 첫 새 실패에서 중단했으며 재시도하지 않았다.

## Evidence And Limits

- production compile 24.77초, app test compile 15.28초 통과. Core 최종 bytes/도구 결과 검사, Host/Rust budget 51 cases와 실제 launch admission, proxy preface 검사 통과.
- 실제 controller 38.84초. proxy/runtime 각1, auth admission1, models control 예약1을 사용했다. 외부 연결 FD 예약·발급0, thread/model turn/generation/dispatch0. control 예약을 성공한 HTTP 송신으로 해석하지 않는다.
- proxy.stderr는 `Error: Operation not permitted (os error 1)`이다. runtime은 initialize 중 stdout이 닫혔다. controller의 prepared comparison missing 메시지는 초기화 실패 뒤에 발생한 후속 증상이다.
- 정적으로 proxy profile에 실제 epoch24 authorization 파일이 빠지고 존재하지 않는 resume01 하위 경로가 들어간 것을 확인했다. Driver가 재개 승인 파일 경로를 문자열 치환하면서 control-file 경로까지 바꾼 준비 오류다. 실제 권한 거절 syscall까지 추적하지 않아 EPERM의 최종 원인으로 확정하지는 않는다.
- 기존 로컬 admission은 넓은 테스트 읽기 범위에서 같은 spec/binary를 검증했으므로 실제 proxy profile의 읽기 목록 누락을 검출하지 못했다. 다음 검증에는 bound control-file 목록과 실제 role profile 허용 목록의 일치 확인이 필요하다. profile을 넓히거나 proxy를 다시 실행하지 않았다.

## Preservation And Accounting

runtime/proxy/controller 및 검사 process/group 종료, FD lease0, 보호 인증/config metadata 불변, source43/build31·복구본 및 epoch20–23 불변을 확인했다. 현재 후보는 source43/build31이며 epoch24는 stopped다. 초기 실패와 재개 승인 원문은 그대로 보존했다.

보존: 현재 source/build, 정확한 profile/spec/journal·실패 로그, 이전 source42/build30 및 재개 전 source43 binding. 다음 Owner 판단·승인된 원인 확인의 입력이다. 활성 경로 이동0. 삭제: 사용이 끝난 socket·소유 표식·검사 HOME 링크/빈 lock·빈 tmp 디렉터리 15항목. 소유·process 종료·열린 handle 부재를 먼저 확인했다. 보류 임시 항목 2건이다.

재개 활동 11.69분, 첫 중단 이전을 포함한 같은 작업 누적 17.45분, 원35분 작업 한도 잔여 17.55분. 전체 누적 상한 잔여 56.00분이며 Owner 대기는 제외했다. 누적 cap149,297,229ms와 보호 예약34.30235분을 유지한다. 다음 실행은 이번 실패에서 소진된 start/proxy와 stopped epoch를 재사용할 수 없다.

잘못된 경로 한 곳을 바로잡는 미적용 patch는 proposed-profile-path-fix.patch다. 이것만으로 실행 준비가 끝났다고 주장하지 않는다. 새 실행 배정·정확한 role profile 사전검증·필요한 counter/source binding은 후속 범위로 정해야 한다. Work는 Active/not qualified다.

Evidence: `private-evidence/E089`; exact actual: `private-evidence/E025`. [공개용 중립화]

## MCP56 Clock Progress And Local Notice Repair — 2026-10-25

proxy 권한 경로를 수정한 source44/build32로 초기화, 실제 입력 동일성, thread 생성과 turn 예약1까지 진행했다. 생성 요청과 curr_time 호출은0이다. 실제 실행은 turn/startPrepared의 Code Mode unavailable / Direct 도구 안내를 Host가 거절해 종료됐다.

실제 경고 params 382 bytes의 저장 SHA-256을 소스에서 재구성한 문장과 thread로 정확히 재현했다. 기존 승인 Direct 정책에 대응하는 한 종류의 안내만 candidate·mode·thread·단계·최초1회 조건으로 처리하는 Host 보정을 source45로 적용했다. 실제 재실행 없이 로컬18 cases와 기존8 tests가 통과했다. 다른 경고·변조·중복·잘못된 thread·단계는 계속 거절한다. 이 보정의 native 실행 성공은 아직 확인하지 않았다.

검증: production build 18.50초, app compile 8.87초, 공통 budget 51 cases 및 실제 입력의 app/proxy admission 통과. proxy bound control files116개가 실제 프로필에 있음을 확인했다. 변경 없는 Core 검사는 MCP55 결과를 재사용했다. JSON canonical 준비 오류와 빈 디렉터리 충돌은 자동 보정 후 진행했고 실패 기록은 보존했다.

실제 controller 40.15초, 이전 initialize EPERM은 재발하지 않았다. 이번 실제 추가 효과는 auth admission1, control 예약2, thread1, turn 예약1, generation0, dispatch0이다. 보호 인증/config metadata 불변, 관련 process/group 종료, proxy lease0, 기존 epoch20–24 불변과 두 저장소 diff-check를 확인했다.

현재 총 source45/build32/offline73/runtime16/proxy18/auth15/control23/thread8/turn1/generation0이다. source44의 Host는 notice-repair/host.py.before에 복구 가능하게 보존했고 source45는 notice-repair/source.json에 기록했다. Rust/build32는 변경 없이 유지했다. actual epoch25는 stopped다. 다음 native 시도는 새로운 소비 배정과 Rust/Host 계약 갱신이 필요하다.

자동 승인 검토는 첫 실행 승인 불명확 거절을 기존 사용자 승인·고정 payload 근거로 해소해 실제 실행을 허용했다. 이후 새 epoch·누적 두 번째 turn 배정 제안은 승인된1턴을 넘는다는 이유로 거절했다. 거절된 mcp57 생성/실행은 수행하지 않았다. 이후 보정과 검사는 외부 호출 없는 로컬 작업만 수행했다.

누적 상한149,297,229ms 유지. 원35분 작업의 남은 활동 시간 4.27분, 전체 상한 잔여 42.73분이다. Owner 대기는 이후 제외한다. 다음 최소 승인 범위는 같은 시각 조회 입력으로 추가 native 시도1회(추가 turn 예약1, generation 최대2, curr_time1), 이에 필요한 할당/빌드/집중 검사다. 고객 데이터·화면 조작·다른 도구는 포함하지 않는다. 기존 남은 작업 시간과 누적 상한을 그대로 적용하며 시간 증액은 요청하지 않는다.

보존: 소스/복구본, 실제 spec/profile/journal/로그, 실패 준비 입력 및 회귀검사. 활성 경로 이동0. 사용이 끝난 소켓·검사 HOME 링크/빈 lock·빈 디렉터리 17개를 소유·process·열린 handle 확인 후 삭제했다. 임시 보류 0개. Work는 Active/not qualified이며 완료·수락·Git publication은 하지 않았다.

Evidence: `private-evidence/E090`. [공개용 중립화]

## MCP57 Built Candidate At Work Time Limit — 2026-10-25

추가 실제 clock1회에 대한 Owner 승인753945489를 반영해 source46/build33을 준비했다. production build 19.76초와 app test compile 8.65초가 통과했다. 새 실제 epoch/runtime/proxy/controller는 만들거나 시작하지 않았다. 추가 실행 승인은 소진되지 않았다.

MCP56 closeout 이후 이전 최종 응답까지136.518370초도 활동 시간으로 차감했다. Owner 대기39.146297초는 제외했다. 이 결과 이번 재개에 사용 가능한 원35분 작업 한도 잔여는119.899267초였으며, 새 배정·보존·컴파일 동안 소진됐다. 임의로 작업 한도나 누적 상한을 늘리지 않았다. 원 작업 시간 종료 후 결과 기록은 기존 closeout 예약을 사용했다.

현재 source46/build33, offline75 중 추가2회는 예약만 했고 실행하지 않았다. runtime16/proxy18/auth15/control23/thread8/turn예약1/generation0을 유지한다. source45 복구본 두 파일,source46 source manifest,이전 epoch25 불변,build binaries,process/group 종료,두 저장소diff-check를 확인했다. 기존 Host경고26 checks와Core evidence는 재사용 가능하며 새 allocation app/proxy 집중 검사는 미실행이다.

전체 누적 상한149,297,229ms 유지. 전체 잔여37.30분, 보호 예약34.30235분 제외 실행 여유3.00분이다. 다음 최소 제안은 이번 작업 중단한도만120초 연장하고, 전체 누적 상한과 기존 추가1회 실행 승인은 유지하는 것이다. 소스/빌드 계약 변경 없이 extension sidecar로 helper의 작업 시간 조건만 갱신할 수 있는지 먼저 확인한다. 원 승인과 입력은 덮어쓰지 않는다. 실행 lifetime30초 상한과 집중검사/종료 여유가 확보될 때만 native를 시작한다.

보존: source45 복구본,source46/build33,고정 실행 입력·helper·로그. 모두 같은 추가 실행의 직접 입력이다. 이동·삭제0; 이번 빌드는 별도 일회성HOME/socket을 만들지 않았다. Work Active/not qualified,완료·수락·Git publication 없음.

Evidence: `private-evidence/E091`. [공개용 중립화]

## MCP57 Two-Minute Extension — 2026-10-25

Owner 대기 중 만료된 시한 metadata만 재바인딩했다. build34 통과 후 test compile 시작 전 남은 시간 gate에 걸렸다. 2분 예상은 부족했고 추가 실제 실행은0이다. 추가1회 실행 승인은 유지한다. 증거: `private-evidence/E092`. [공개용 중립화]

## MCP58–62 Native Clock Verification — 2026-10-25

수정 후보 source52/build39가 실제 native 시계 검증을 통과했다. 마지막 시도는 한 턴에서 generation2, clock.curr_time dispatch1 후 정상 완료했고, 모델 최종 응답은 `2026-10-25 09:00:17 UTC.`이다. 이 시각은 dispatch 장부의 UTC 초와 일치한다. 도구 출력 원문을 별도 저장한 검증은 아니며, Core가 검증한 실제 결과를 두 번째 요청 입력에 결합하는 경로와 최종 응답을 확인한 결과다.

## Changes And Evidence

- Native 일반 텍스트 기록 경로가 추가하는 `content_item_kinds=["unknown"]` 때문에 준비 상태의 엄격한 동일성 검사가 실패했다. 본문 수에 정확히 대응하는 이 분류만 허용하도록 수정했다. 본문·식별자·기존 분류·다른 메타데이터 변경은 계속 거부한다.
- 실제 `to_annotated_content` / `set_annotated_content` 변환과 native stamping을 사용한 회귀검사에서 정상 변환 허용, 분류 값·개수·본문·추가 metadata 변조 거부를 확인했다. 기존 최종 전송 bytes·history·중복 전송 거부 검사도 통과했다.
- Host의 native moderation metadata는 정확한 턴·단계·크기·횟수로 제한하고 hash만 기록한다. clock 오류 진단은 신원·단계와 개인정보 검사를 통과한 제한된 메시지만 남기며 오류 거부 자체는 유지한다.
- 이번 최종 검증: Host17 tests, Core 집중검사1, Host/Rust budget51 cases, 실제 후보 app/proxy admission, bound profile coverage 통과. 전체 test suite나 전체 U2 검증 통과를 뜻하지 않는다.
- 마지막 controller 전체 시간 49.45초에는 로컬 app/proxy 검증과 실제 실행이 포함된다. manifest/input 동일성, generation2·dispatch1, 정상 turn completion, 후속 read barrier를 확인했다.

## Scope And Accounting

Owner 승인984820975에 따라 같은 synthetic clock 범위의 수정·재시도를 별도 승인 요청 없이 이어갔다. 최초 예상10–20분은 원인 진단과 Core 재컴파일 때문에 초과했다. 현재까지 연속 작업·빌드·provider 대기·정리 누적 43.49분이며 60분 작업 중단한도 안이다. 대기와 겹치는 작업은 wall-clock으로 한 번만 계산했다. 누적 상한153,497,229ms와 보호 예약34.30235분을 유지한다. 현재 전체 잔여 58.80분, 이번 작업 한도 잔여 16.51분이다.

MCP58은 native moderation notification 거부, MCP59/60은 호출 전 준비 상태 실패, MCP61은 기록 변환의 최초 실패 사유 확인, MCP62는 보정 후 실제 성공이다. 실패 시도와 소비량을 그대로 보존했으며 초기화하지 않았다. 누적 generation6 중 최종 성공 시도는2, 누적 dispatch는1이다.

현재 Work는 Active이며 R1 REVISE 및 전체 qualification 미완료 상태를 유지한다. 이번 결과는 clock 한 턴의 실제 성공이다. U2 문서 작업·고객 자료·H05/H10·추가 review·Git publication·Owner 수락은 이번 범위에 포함하지 않았다. STATUS 및 Done 처리는 변경하지 않았다.

## Preservation And Cleanup

현재 source/build, 이전 실제 후보 복구본, 정확한 입력·journal·실패/성공 결과는 같은 영구 경로에서 유지한다. 소비자는 Owner 결과 검토와 후속 qualification이며, 수락 또는 중단 결정 뒤 남은 review/recovery 소비자가 없을 때 재평가한다. 활성 경로 이동0이다.

앞선 단계 46항목과 이번 36항목의 사용이 끝난 소켓·HOME 링크·빈 lock·빈 실행 디렉터리를 소유·프로세스 종료·열린 handle 부재 확인 후 삭제했다. 임시 보류 2건이다. 인증/config metadata 불변, runtime/proxy/controller 및 검사 프로세스 종료, FD lease0, 보호 epoch와 parent journal 불변을 확인했다.

Evidence: `private-evidence/E094`. Actual: `private-evidence/E026`. [공개용 중립화]

## Finalization

앞서 임시 보류한 Core test HOME 2개는 해당 Core test binary로 연결된 apply_patch 링크와 빈 lock뿐임을 확인했다. 프로세스·열린 handle 부재 확인 후 추가 16항목을 삭제해 이번 연속 작업의 총 삭제는 98항목, 임시 보류0이다. 현재 source52/build39 및 필요한 증거·복구본 경로는 그대로 유지한다. 재실행 없이 성공 근거를 재사용했다. 최종 기록 시 연속 활동 44.60분, 작업 한도 잔여 15.40분, 전체 누적 상한 잔여 57.69분이다. 최종 상세: `private-evidence/E093`. [공개용 중립화]

## 2026-10-25 남은 U2 연속 검증 승인

Owner 승인: 남은 U2 검증, 실패 보정 및 재시도를 연속 진행한다. 예상 4–6시간은 판단값이며, 이번 연속 활동 상한은 8시간이다. 구현·빌드·모델 대기·검증·정리를 포함하고 겹치는 시간은 한 번만 센다. 기존 누적 사용량과 보호 예비량을 이월한다.

1. 고정 합성 문서 5개로 native runtime → 실제 Host → 격리 worker → installed Colvia 경로를 검증한다.
2. H01–H08의 입력 결합, 단일사용 권한, 실패 후 수정, 중단·재개와 거부 경로에서 미관측 부분을 실행한다.
3. H09 기존 문서 근거는 재사용하고, H05 exact 복구와 H10 실제 자료·권한·Git 결과에 필요한 구체적 Owner 패킷을 준비한다.
4. 변경 위험에 맞는 Host/Core focused 검사를 사용한다. 기존 normal/optimized 706개 전체 결과는 영향 없는 부분에 재사용하며, 전체 재실행은 새로운 위험이 확인될 때만 한다.

각 실행의 입력·권한 효과·호출 수는 실행 전에 고정한다. 실패는 원인과 소비량을 기록한 뒤 같은 승인 범위에서 수정한다. 고객 자료 열람·전송, 실제 권한 복구, Git publication, 최종 수용의 기존 별도 Owner 판단은 유지한다.

실행 근거: `private-evidence/E151`. [공개용 중립화]


### U2 잔여 검증 중간 관측 — 2026-10-25 source60

Owner의 잔여 U2 계속·실패 수정 승인(824273881)에 따라 기존 누적 사용량을 보존하며 진행 중이다. source59의 실제 Lite 응답에서 허용된 `u2_read_file`의 namespace 생략을 관측했다. source60은 기본 namespace의 동등성을 두 응답 형식에 적용하고 미등록 이름·빈 문자열·외부 namespace 거부를 유지한다. Host 일반/최적화 검증과 Core namespace/이력 집중 검증은 통과했으며, source60 네이티브 실행 결과는 아직 없다.

H05 합성 S0–S5에서 실제 프로세스 종료와 예상 파일·decision·selection·current 상태를 확인했다. S0는 호출 전 무변경, S1–S4는 pending, S5는 current 게시 완료다. S5를 pending으로 가장하지 않으며 복구 gate에 게시 완료 분기를 반영했다. 관측기의 접근 시각 비교 문제는 inode·권한·내용 메타데이터 검사를 유지하는 방식으로 수정했다. 다섯 원본 티켓은 exact 복구 검토 패킷으로 준비했고 복구 재실행은 아직 하지 않았다.

실제 Reference A 대상은 metadata 수준으로만 다시 확인했다. H10의 본문/모델 입력·exact intent/grant·Git setup·후속 candidate 승인 경계는 유지한다. 신규 파일 2개와 64KB 초과 입력은 실제 admission 준비에서 해결할 제약이며 아직 H10 실행 증거가 아니다. 상세 단계 증거는 기존 비공개 실행 root의 `u2-continuation-20261025/stage-source60-pre-native.json`에 보존한다. source/실행 증거와 pending H05 worker는 qualification·exact recovery·Owner 검토를 위해 유지하며 source commit/push 및 Work Done은 하지 않았다. [공개용 중립화]


### U2 합성 native 편집·재개 경로 관측 — source65/build52

실제 native thread에서 합성 문서 6개를 읽고 checkpoint를 남긴 뒤 프로세스를 종료했다. 같은 Work를 새 thread로 재개해 DOC-CLAIMS의 예상 실패 5건을 확인하고 출력 문서 5개를 수정했다. DOC-LINKS·DOC-GFM·DOC-CLAIMS가 모두 통과해 결과를 봉인했다. 이는 합성 입력에서의 H06 실패→수정→통과 및 H07 계획 중단·재개 실행 근거다. H10 실제 자료나 일반 제품 품질의 성공으로 확대하지 않는다.

source64는 검증된 native history를 ResponseItem으로 역직렬화하며 생략된 reasoning content가 null로 바뀌던 문제를 수정했다. 이미 직렬화된 JSON을 보존하고 native request의 ID·내부 metadata 제거만 재현한다. 생략/null 차이와 암호화 content 변조 거부, namespace·history 집중검사 3개가 통과했다. source65는 다음 턴 준비 때 moderation metadata 카운터도 초기화한다. 턴당 최대2회와 신원·단계·크기 검사는 유지하며 세 턴 연속 및 이전 턴 이벤트 거부를 회귀검사에 추가했다. Host 일반/최적화 각각77개, 실제 후보 budget47 cases·app/proxy 사전검증이 통과했다. 영향 없는 Colvia authority 전체706개 일반/최적화 근거는 재사용했다.

합성 worker 10개(읽기1, 최초 검증1, 쓰기5, 최종 검증3)의 정상 종료와 인증/config metadata 비교13회 불변을 확인했다. 실제 credential read 횟수는 계측하지 않았으므로 unknown을 유지한다. 합성 편집 결과 identity는 `bd1bcef5a418895a615b2050056cf73b3350a0c3759ddc4e771ffd8d1d4008c0`이다. 권한 적용은0이며 source commit/push도0이다.

자동 승인 검토가 합성 worker의 로컬 커밋·Work 게시 명령을 별도 Owner 승인 필요로 거절했다. 명령은 실행되지 않았다. 검토 가능한 diff와 후보 정보를 보존하고 이 결과의 커밋·게시·정확한 티켓·동일 thread 수락1회에 대한 결정을 요청했다. 같은 thread는 2026-10-25T11:25:23.305Z까지 대기한다. H05 원 티켓 S1–S5 replay와 H10 private 본문 읽기/준비도 별도 요청의 응답 대기 상태다. 현재 Work는 Active/partial이며 독립 R1의 이전 REVISE, 최종 Owner 수락 및 전체 qualification 미완료를 유지한다.

근거: `private-evidence/E152` 및 같은 경로의 `sealed-review/review.json`. 소스·실행 journal·로그·checkpoint·후보 출력과 H05 pending worker는 qualification, exact recovery와 Owner 판단의 입력이므로 보존한다. native idle 종료 및 Owner 판단 뒤 더 이상 소비자가 없는 일회성 파일만 정리한다. [공개용 중립화]


### H05 exact recovery 완료 및 H04 별도 재검증 — 2026-10-25

Owner private-approval/O022 승인 뒤 S1–S5 원본 티켓을 원 actor·decision 그대로 순정 installed CLI로 각각 한 번 재실행했다. 총5회이며 모두 정상 완료, 문서 bytes가 제출 worker와 같고 S5의 이미 게시된 current는 그대로임을 확인했다. S0의 호출 전 무변경과 S1–S5 실제 프로세스 중단 관측은 앞선 근거를 재사용한다. 합성 H05 경계의 실행 근거이며 실제 고객 자료 복구의 일반 보장은 아니다. [공개용 중립화]

같은 승인에 따라 source65 봉인 후보를 로컬 commit b0237e69cd680190df56d046113a81c40947531f로 보존하고 synthetic Work result-1을 게시했다. 정확한5문서 및 Codex trailer를 확인했다. 앞선 자동 승인 거절은 이 명시 승인으로 해소됐다. 원래 편집 thread는 승인 도착 전에 idle 만료로 종료됐으므로 권한 적용은0이다. 실제 cleanup에서 runtime/proxy 종료와 controller lease0을 확인했다. 기존 결과와 티켓을 새 thread에서 수락하거나 제출 파일을 다시 쓰지 않았다.

Owner private-approval/O011은 별도 합성 Work에서 이미 검토한5개 결과 bytes와 정확히 일치하는 경우의 candidate commit·게시·같은 편집 thread 수락1회를 승인했다. 예상45–75분, 누적 상한90분은 기존8시간 안에 포함한다. source66/build53은 이를 위한 epoch41을 추가하며 이전 seal1·content correction1·전체 소비량을 이월한다. 새 allocation은 별도 home/Work에 결속한다. 과거 epoch40의 Rust 시작 identity 누적 누락은 원 journal을 바꾸지 않고 validator에서 보존하도록 수정했다. Host 일반/최적화 각각77개, build와 App Server test compile이 통과했다. 실제 H04 결과는 아직 없다. [공개용 중립화]

실제 대상 준비는 승인된 참고27·출력5 경로를 inventory로 고정하고 비활성 intent/grant/Git setup/내용 oracle을 작성했다. 설치본 parser의 순수 메모리 schema 검사만 통과했으며 intent/Work/실제 Git mutation은0이다. 신규2파일·65,536 bytes 초과 입력2파일이 현 worker 계약의 제약이다. Owner private-approval/O014이 추가로 허용한35개 링크 경로의 존재/type와4개 파일의 필요한 anchor를 로컬에서 확인했고 모두 통과했다. 추가 본문은 모델로 전송하지 않았다. 이 관측을 H10 실행 성공으로 올리지 않는다. [공개용 중립화]

상세 근거는 기존 private execution root의 `u2-continuation-20261025/h05-recovery-preparation/verified-result.json`, `attempt10/acceptance-preparation/review.json`, `attempt11/authorization.json`, `h10-preparation-O022/`에 있다. 소비자는 남은 qualification·실제 admission·Owner 검토이며, 원본 티켓·결과·journal·source 복구본·worktree를 유지한다. Work Active/partial, 기존 독립 R1 REVISE와 최종 Owner 수락 미완료는 그대로다. [공개용 중립화]


### H04 실제 수락 완료와 H10 사전 문맥 조건 — 2026-10-25

별도 합성 Work의 H04는 source66/build53에서 완료했다. 원본 입력 읽기·계획 중단 뒤 같은 Work의 새 편집 thread에서 실패를 관측하고5개 문서를 수정·검증했다. Owner private-approval/O011이 승인한 기존 결과와 exact diff/bytes/mode가 일치함을 확인한 뒤 candidate5d4b6095487f047c1e6bac95ea786017ef7106b8를 생성·게시하고, 아직 살아 있는 같은 편집 thread에서 순정 installed CLI의 ordinary grant accept1회를 실행했다. 실제 결정 actor는 합성 delegate이며 completed·pending0, 프로세스 종료·lease0을 확인했다. 실제 runtime257.628초, 준비/진단/검증 포함18.66분이다. Host guard replay21개와 installed read-only prepare 거절4개를 구분해 보존했다. revoked grant 및 다른 existing Work의 거절은 아직 별도 실제 CLI 근거가 부족하다. [공개용 중립화]

source68/build55는 H10의 expected-absence 신규 파일, whole-file CAS에 결속된 고정 구간 편집, metadata-only 링크 검사, 재개 시 원 scope 보존을 추가했다. Host 일반/최적화 각각92개 및 실제 OS worker 생성/교체/재개/검증, 범위 밖 쓰기·참고 쓰기·metadata 본문 읽기·verifier 쓰기 거절을 확인했다. 과거 source64 Core/history/privacy 근거는 변경 영향과 구분해 재사용한다.

실제 Reference A 실행 입력은27참고·5출력으로 준비했으며 로컬 승인 자료를 제시했다. 다만 실행 전 비용 대조에서6개 읽기 응답 합계와 native 출력 예약만으로도 기존에 관측한258,400 context window를 넘는 것을 발견했다. exact 입출력 가드를 유지하며 입력/출력 예산을 보정해야 하므로 실제 Reference A 변경·H10 모델 호출은0이다. 승인 응답이 도착하더라도 이 사전 조건이 해결되기 전에는 setup하지 않는다. 증거는 전용 작업 디렉터리의 h10-preparation-O022/context-preflight-failure.json에 보존한다. [공개용 중립화]

### H10 준비 보정과 추가 거절 근거 — 2026-10-25

H04의 기존 Work 불일치 grant와 selected revoke 이후 재수락 거절을 별도 합성 fixture의 순정 installed CLI에서 확인했다. 두 경우 모두 새 권한 적용 없이 bytes/mode 불변을 확인했다. revoked fixture는 기존 수락·revoke·rebind의 실제 게시 상태를 읽고 이어갔으며, no-op Git commit 실패를 권한 실패로 혼동하거나 이미 완료된 apply를 반복하지 않았다. 근거는 기존 실행 root의 `h04-installed-negatives/wrong-work/observed-negative.json`과 `h04-installed-negatives/revoked/resume/verified-result.json`이다.

Owner private-approval/O006가 실제 H10의5개 문서·exact intent/grant·base tag/worker 준비와 같은 provider 경로를 승인하고 동시 writer 부재를 확인했다. 최종 candidate commit/result tag는 실제 diff 이후 별도 판단으로 유지한다. 입력은 승인 원문 안의 관련 구간으로 좁혀27개 참고 ID와5개 출력, 전체 source digest, 원 oracle을 보존했다. source70의 출력 상한8192에서 보수적 문맥 예측242,525는 기존 관측 창258,400 안에 들어간다. 이는 예측이며 요청별 실제 context/wire guard가 계속 적용된다. Core 집중10개와 영향 없는 문서 계약92개·OS 검사는 구분해 재사용한다. [공개용 중립화]

배정45는 보조 스크립트의 기존 전용 폴더 재생성으로, 배정46은 최대40turn 테스트 입력에서 필수 봉인 후 pause/resume이 빠져 중단됐다. 두 기록과 소비 카운터는 보존했으며 새 H10 runtime/thread/권한 적용 및 실제 대상 변경은0이다. 폴더 소유권 재사용 검사와 테스트 순서를 수정했고49개 Python 예산 사례가 통과했다. oracle이나 권한 조건을 낮추지 않았다. source71/build58 빌드31.28초 및 App test compile15.19초는 통과했으나 실제 App/proxy 사전검사는 아직 완료되지 않았다.

자동 승인 검토가 포괄 승인으로는 새 Host/Rust 배정 변경을 허용하지 않아 구체적 복구 승인을 받았다. 이후 epoch46만 승인된 것으로 해석해 다음 배정47을 다시 차단했으며, 같은 원래 한도 내 후속 복구를 포함한 결정을 요청했다. 실제 대상 setup은 사전검사 통과 후에만 진행한다. H10 중단 시각2026-10-25T15:17:48.860237Z 및 전체8시간 한도는 늘리지 않았다. 현재는 Active/partial이며 최종 독립 검토와 Owner 수용은 미완료다. 입력·중단 기록·검증 결과·복구 source는 남은 실행/최종 검토를 위해 기존 전용 경로에 보존한다.


### H10 실제 첫 실행과 남은 한 번의 복구 — 2026-10-25

Owner private-approval/O020가 같은 한도 내 후속 복구를 승인했다. source73/build60의 Python 일반/최적화49개와 실제 App/proxy admission이 통과한 뒤 Owner private-approval/O006가 승인한 base tag·전용 worker·intent/grant·Work start를 준비했다. CLI의 빈 evidence_refs 필드 거절은 ticket 작성 전 실패였으며, 기존 draft와 Git 준비를 보존한 채 지원되는 입력으로 이어갔다. 실제 setup 근거는 기존 execution root의 `u2-continuation-20261025/h10-actual-setup/`이다. [공개용 중립화]

H10 첫 native thread는 참고27개와 출력5개를 모두 읽고 Operations·Handbook·backlog를 작성했다. 7번째 turn의 worker 쓰기는 성공했으나 다음 모델 전송 전에 문맥 여유 검사로 중단됐다. 기록된 error payload의 정확한 해시가 source의 `prepared tool plan: live context headroom unavailable`와 일치한다. 마지막 관측 input50,174 tokens와 usable258,400, output reserve8192는 실제 관측이며 전체 실행 성공은 아니다. intent-bound authority apply는0이고 runtime/proxy 종료·lease0을 확인했다. 마지막 정상 checkpoint 뒤의 backlog 쓰기는 원 요청과 현재 bytes를 대조했으며, 5개 partial 결과를 recoverable copy로 보존했다. 이전 실패·journal·checkpoint는 고치지 않았다.

source74는 ciphertext 바이트와 native output-token 상한의 중복 계산을 제거했고 집중11개가 통과했다. epoch49는 활성화하지 않았다. 복구 실행에서 같은 source를 재독하는 비용도 안전하게 다루도록 source75는 실제 native input-token 관측을 정확한 history prefix·model·tools·base에 결속한다. 변경된 prefix나 알 수 없는 opaque input은 그 관측을 재사용할 수 없고, 출력 예약과 원 usable-window 한도는 유지한다. source75/build62는 통과했으며 집중 검사와 실제 admission을 수행한 뒤에만 다음 native 실행을 시작한다.

남은 H10 배정은 runtime 시작1회·model33turn·content correction2회·authority apply1회이다. 이전 첫 시작과7turn 및 기존 누적 소비는 이월한다. 원 5문서 scope·원문 source origin·구간 밖 bytes·기존 intent/grant/Work를 그대로 재사용하고 setup·apply를 반복하지 않는다. H10 중단 시각2026-10-25T15:17:48.860237Z와 전체8시간 한도는 유지한다. candidate commit/result tag는 실제 봉인 diff 이후 Owner 판단이며 최종 독립 검토·Owner 수락·Work Done은 아직 미완료다. 부분 결과와 source 복구본은 남은 실행 및 최종 검토의 소비가 끝날 때까지 기존 경로에 보존한다.


### H10 두 시작 소진과 문맥 준비 보정 — 2026-10-26 KST

Owner private-approval/O015는 H10 누적 상한을150분으로30분 늘렸으며 시작 횟수는 늘리지 않았다. source76/build63의 epoch51에서 기존 setup을 같은 흐름으로 재결속하고 두 번째 native 실행을 수행했다. 참고27·출력5개를 읽고 Operations·Handbook을 작성한 뒤 turn/prepare가 문맥 여유 부족으로 거절됐다. 실제 실행250.85초,6턴·12generation이며 마지막 관측 입력55,951 tokens, usable258,400이다. 첫 실행을 합쳐 H10 시작2회·13턴·25generation을 사용했다. H10 봉인·권한 적용은0이며 runtime/proxy 종료·controller lease0을 확인했다. 남은 원래 턴은27개지만 추가 시작 권한은0이다. [공개용 중립화]

source77의 첫 회귀검사는 content None이 그대로 roundtrip되는 입력을 사용해 가설을 재현하지 못했다(기존12개 통과·신규1개 실패). 실패 source와 로그는 보존했다. serializer 코드를 확인한 source78은 실제로 필드가 생략되는 Some(empty) 사례를 사용했다. 이 JSON roundtrip이 생략 필드를 null로 바꿔 측정된 입력 prefix와의 일치를 깨고, 보수적 바이트 fallback에서 같은 문맥 거부를 일으키는 반례를 재현했다. 준비 단계에서 native typed history와 초기 입력을 그대로 유지하면 통과하며 unknown opaque 거절도 유지한다. 이는 재현된 코드 결함이며, 두 번째 실제 실패의 정확한 원인이라는 판단은 아직 추론이다.

source78/build65 빌드57.34초, Core test compile33.62초, 집중13개0.30초가 통과했다. Host/App allocation·proxy·Colvia authority는 이번 수정에서 바뀌지 않아 영향 없는 기존 예산 admission, 문서 계약92개/OS, authority normal/optimized706개 근거를 재사용한다. source77/build64와 실패검사도 소비량에 남긴다. 실제 모델 재실행은 하지 않았다.

다음 제안은 같은5문서·원 source/view/oracle·provider·기존 intent/grant/Work를 유지하며 추가 시작1회와 남은 총27턴만 사용한다. 예상15–25분은 최근6턴 약4분을 참고한 판단이며 준비·모델 대기·검증·정리를 포함하고 겹친 시간은 한 번 센다. 제안한 H10 상한180분(01:17:48 KST)은 기대 시간이 아니며, 전체8시간 종료02:08:33 KST는 그대로다. 추가 시작 및30분 연장은 아직 Owner 판단 대기다. candidate commit/result tag는 실제 봉인 diff 이후 별도 결정으로 유지한다.

이번 실행 후5개 partial 결과를 현재 파일과 bytes/mode 대조하여 기존 전용 root의 attempt22/partial-documents에 보존했다. 원본 journal·checkpoint·실패/성공 검사·source 복구본·후보 worktree는 추가 실행 결정과 qualification 검토의 입력이므로 유지한다. 활성 경로 변경0·삭제0이며, 소비자가 없는 일회성 항목의 정리는 다음 안전한 단계에서 재평가한다. 근거와 실행 제안은 기존 실행 root의 u2-continuation-20261025/attempt21/actual-native/result.json, attempt23/core-focus-selection.json 및 attempt23/next-execution-proposal.json에 있다.

### H10 문서 봉인 검토와 인덱스 교정 준비 — 2026-10-26 KST

Owner private-approval/O023이 추가 시작1회·H10 상한180분을 승인했다. source79/build66의 세 번째 native 실행은 이전 문맥 실패 지점을 지나 읽기4·저장5·검증3의12턴을 완료했다. DOC-LINKS/GFM/CLAIMS가 통과하고 결과를 봉인했으나, Driver가 실제 diff를 검토해 brief index의 기존4열 표에5열 행이 추가된 것을 발견했다. 이 결과는 의미 검토에서 거절했고 candidate commit·result tag·권한 적용 없이 실행을 종료했다. H10 누적 시작3회·25턴·49generation을 사용했으며 runtime/proxy 종료·lease0을 확인했다. 이 봉인 및 거절 기록은 보존하며 통과 결과로 대체하지 않는다. [공개용 중립화]

source80은 선택적 exact_view_sha256 검증을 추가했다. 이미 검토한 네 문서의 편집 구간은 정확한 bytes로 고정하고, brief index는 준비한4열 한 행과 정확히 일치해야 한다. 잘못된5열·추가 본문·잘못된 digest 형식 거절과 기존 계약 호환성을 포함해 문서/Host 일반·최적화 각각95개가 통과했다. 원 source/view 범위와 기존5파일은 유지한다. Core13개는 코드가 같아 재사용한다.

Owner private-approval/O008이 남은15턴 안에서 교정용 추가 시작1회를 승인했다. source81/build67 빌드36.90초 및 App test compile12.97초가 통과했지만, 실행 전 LiveSession 생성에서 준비 코드가 Owner 입력 파일 경로에 안내 본문을 붙인 오류를 발견했다. 모델·provider 호출과 native 시작은0회이고 proxy 프로세스도 시작하지 않았다. proxy 예약1개와 offline 예약3개는 환급하지 않고 기록했다. 중단된 epoch53의 controller 종료·lease0을 확인했다. [공개용 중립화]

실제 원본 입력 본문과 교정 안내를 별도 durable 파일로 저장하고 그 경로와 내용 해시를 결속했다. 실제 LiveSession 생성자 검사를 실행해 통과했으며 journal은 변하지 않았다. source 변경은 없고, 아직 사용하지 않은 승인 시작1회·15턴이 남아 있다. 필수18분 실행 여유를 확보할 수 없어 H10 상한만20분 늘리는 제안을 Owner에게 요청했다. 제안 잔여12–18분은 직전12턴 약8분 관측에 준비·검증·검토를 더한 판단값이며 대기를 포함한다. 제안 상한200분(01:37:48 KST)과 기존 전체8시간 상한(02:08:33 KST)은 기대 시간과 구분한다. 시간 변경 응답 전 추가 모델 실행은 하지 않는다.

근거는 기존 전용 root의 attempt24/sealed-review/driver-semantic-review.json, attempt25/actual-native/result.json, attempt25/preflight-stop-classification.json, index-repair/owner-input-repair-proof.json에 있다. 같은 root의 입력·원본 journal·source 복구본·거절된 봉인 문서·현재 worker checkout은 교정 실행, 최종 독립 검토 및 Owner 판단의 입력으로 유지한다. 활성 경로 변경0·삭제0이다. 최종 candidate commit/result tag·같은 편집 thread 수락 및 전체 Work 수용은 여전히 별도 미완료다.

Owner private-approval/O001가 시간만20분 연장을 승인했다. H10 중단 시각은2026-10-25T16:37:48.860237Z(01:37:48 KST)로 변경하며 전체 종료17:08:33.976911Z(02:08:33 KST)는 유지한다. 미사용 시작1회·15턴은 Owner private-approval/O008의 기존 승인을 재사용한다. source82/epoch54는 중단된 epoch53의 예약·실패 이력을 보존하고 입력 경로 교정을 적용한 후속 배정이다. candidate commit/result tag와 수락은 아직 승인하지 않았다. [공개용 중립화]

### H10 표 연속성 재검토와 마지막 교정 배정 — 2026-10-26 KST

source82/build68의 네 번째 native 실행은12턴·24generation으로5개 문서를 저장하고3개 verifier를 통과해 봉인했다. 네 문서는 이전 검토본과 exact bytes가 같았고 인덱스 행도 준비한4열 문자열과 일치했다. 그러나 Driver가 지정한 문자열의 끝에 LF가2개 있어 기존 표의 나머지25행이 새 행과 분리됐다. 실제 GFM parser에서 원래 표25행·거절된 후보1행을 확인했다. 따라서 H10-INDEX-TABLE-CONTINUITY로 봉인을 거절하고 commit/tag/publish/accept 없이 중단했다. 실제 controller442.35초이며 종료·lease0을 확인했다. H10 누적 시작4회·37턴이고 원래40턴 중3턴이 남았다.

행 끝을 LF1개로 교정한 미리보기는 기존25행 전체를 그대로 보존하면서26행·4열의 한 표로 렌더링됐다. 대상 파일은 수동 수정하지 않았다. exact verifier에는 이 단일 개행 문자열의 digest를 사용하고, 최종 Driver 검토에서는 실제 저장된 인덱스 전체를 다시 파싱해 행 수·열 수·기존 행 보존을 확인한다. 네 문서는 그대로 고정한다. 근거는 기존 전용 실행 root의 table-continuity-repair/render-proof.json과 corrected-index-preview.md/html이다.

Owner private-approval/O004가 추가 시작1회·10턴 추가·10분 연장을 승인했다. 남은3턴에10턴을 더한13턴으로 수행하며 H10 총 턴 상한은50, 중단 시각은2026-10-25T16:47:48.860237Z(01:47:48 KST)이다. 전체 종료17:08:33.976911Z는 그대로다. source83/build69·epoch55는 네 번째 시작과 모든 기존 소비량·봉인을 보존한다. candidate commit/result tag/수락은 최종 diff 이후 별도 Owner 판단이다. [공개용 중립화]

검토 스크립트를 -B 없이 호출하면서 installed payload에 생긴 bytecode6개를 해당 실행 시각·정확한 파일 집합으로 식별했다. 생성 source는 그대로 있고 고유 결과나 복구 입력이 아닌 파생 cache이므로 상시 정리 기준에 따라6개와 빈 디렉터리1개만 제거했다. 이어 installed product 검증과 원 control baseline 일치를 확인했다. 후속 검토/게시/수락 스크립트는 Python -I -B가 아니면 import 전 거절하도록 했으며 실제 명령도 이 옵션을 쓴다. cleanup 근거는 attempt26/review-bytecode-cleanup-input.json 및 result.json이다. 필요한 다섯 문서·봉인·거절·journal·source 복구본과 활성 worktree는 유지했고 활성 경로 변경은0이다.

source83/build69 빌드27.36초와 App test compile12.43초가 통과했지만 epoch55는 native 시작 전 `native H10 headroom`으로 중단됐다. H10 시각만 확인한 Driver 계산에서 전체 외부 마감에 적용되는 정리20분·불확실성14분18.141초 예약을 빠뜨렸다. 기존 외부 마감17:08:33.976911Z에서 예약을 빼면 실행 종료가16:34:15.835911Z이며, 당시16:18:50에는 약15분25초만 남아 필수18분보다 짧았다. runtime/provider/proxy 시작0회·turn0개이고 승인된 시작1회·13턴은 미사용이다. 실패 epoch와 offline 예약3개는 보존한다.

수정 제안은 전체 외부 마감만17:28:33.976911Z(02:28:33 KST)로20분 늘리는 것이다. 누적 활동 상한182,297,229ms, 기존 예약2,058,141ms, H10 중단16:47:48.860237Z, 시작1회·13턴은 유지한다. 답변 전 실행하지 않는다. 후속 준비 스크립트는 source를 바꾸기 전에 phase/외부/누적 마감 중 가장 이른 값에서 예약을 빼고 준비 예상120초 및 실행 여유18분을 함께 확인한다. 근거는 attempt27/actual-native/result.json과 prepare-attempt28-after-deadline-owner.py이다.

Owner private-approval/O003이 전체 외부 마감만20분 늘리도록 승인했다. 새 외부 마감은2026-10-25T17:28:33.976911Z(02:28:33 KST)이고 누적 활동 상한182,297,229ms·예약2,058,141ms·H10 중단16:47:48.860237Z는 그대로다. 미사용 시작1회·13턴은 Owner private-approval/O004 승인을 재사용한다. source84/build70·epoch56 준비 전 통합 시간 검사에서 준비 예상120초를 뺀 실행 여유1197.1초를 확인했다. 이전 epoch55의 시작 전 중단과 offline 예약을 보존했으며 build70은28.06초에 통과했다. 근거는 attempt28/preparation-headroom.json과 h10-external-deadline-owner.json이다. [공개용 중립화]

### U2 기술 실행 결과와 최종 판단 잔여 — 2026-10-26 KST

Owner private-approval/O005이 실제 봉인 후보817cf60c08d8b0433ec576fcb07eaaeff85f0fbd53fd9064c01726de3864f1ae의5파일 diff·제시한 커밋 메시지·로컬 결과 태그·결과 게시·같은 편집 세션의 순정 위임 수락1회를 승인했다. 후보 커밋은reference-a-result-revision이고 결과 태그는reference-a-result-tag 커밋 부모·정확한5경로·메시지·Codex co-author trailer를 검증했다. 원 편집 thread에서 실제 installed CLI의 ordinary delegated accept1회가 성공했으며 Reference A Work synthetic-operations-guide-check의 저장 상태는completed, pending decision/selection은0이다. 이는 상위 qualification Work의 Done이나 최종 Owner 내용 수용을 뜻하지 않는다. [공개용 중립화]

Primary의 운영 가이드·Handbook·backlog·narrative·brief index5파일 bytes/mode가 검토 후보 및 worker와 정확히 일치한다. 그 밖의 control content는 원 baseline과 같고 primary HEAD는reference-a-baseline-revision로 유지했다. 승인된 intent/Work 권한 기록은 .hrn/intents/synthetic-operations-guide-check/ 및 .hrn/work/synthetic-operations-guide-check/에 남는다. 이 두 디렉터리의 untracked 기록을 문서 drift로 잘못 분류한 최초 사후 검증 스크립트는 보존하고, r1에서는 승인된 권한 기록과5문서를 구분해 확인했다. 수락이나 게시를 다시 수행하지 않았다. [공개용 중립화]

최종 실제 실행은13턴·26generation·권한 적용1회이다. H10 전체로는5회 시작·50턴·99generation이며 앞선 실패와 거절 봉인도 모두 누적에 포함했다. 마지막 controller 실행896.716초에는 봉인 후 승인·게시 준비 대기473.784초가 포함된다. DOC-LINKS/GFM/CLAIMS와 별도 Driver 내용 검토가 통과했다. 네 문서는 앞선 검토본과 exact bytes가 같고, 실제 저장된 전체 인덱스를 pinned GFM parser로 다시 읽어 기존25행이 모두 보존된26행·4열 한 표임을 확인했다. runtime/proxy process group 종료·controller closed·lease0 및 journal 정상 stop을 확인했다.

후보 게시 뒤 확인 화면에 전체 packet을 넘겨 표시가 거절된 보조 오류가 있었다. 원 packet과 실패 출력을 보존한 채 원 ticket만 사용하는 읽기 전용 확인 화면을 생성해 모든 advisory 관측이 일치함을 확인했다. 커밋·태그·게시·티켓 준비는 반복하지 않았고, 같은 Owner 결정과 원 티켓으로 실제 편집 세션에 수락을 전달했다. 원 setup helper 로그에 남은 초기 Owner 라벨O006와 이번 실제 후보 승인O005의 관계는 display-repair-result.json에 구분했다. [공개용 중립화]

검증 근거는 기존 전용 execution root의 attempt28/sealed-review/, attempt28/acceptance-preparation/, attempt28/actual-native/result.json 및 attempt28/h10-verification/result.json이다. source80 문서/Host 일반·최적화 각각95개와 source78 Core 집중13개는 해당 source 불변을 대조해 재사용했다. 변경 없는 authority normal/optimized706개를 다시 돌리지 않았다. 새 Gradle/Docker/DB/HTTP 실행과 사용자 이해도·효율 검증은 하지 않았다. 실행 경계는 trusted native runtime이며 worker/verifier/proxy의 격리와 runtime 자체의 OS 파일·exec·직접 egress 보장은 구분한다.

남은 판단은 기존 독립 R1 REVISE에 대한 최종 재검토, Owner의 문서 내용·전체 qualification 수용이다. 이를 수행하거나 수락했다고 주장하지 않으며 상위 Work는Active로 유지한다. push·PR·merge·release는 수행하지 않았다. 이 단계에서 새 reviewer 호출이나 전체 회귀 실행을 추가하지 않았다.

보존·정리: primary와 세 전용 source/candidate worktree, 원 승인·intent/grant·티켓·journal·실패/봉인/검증 기록, 승인된5문서와 커밋은 최종 독립 검토 및 Owner 판단·필요 시 복구의 구체 입력으로 유지한다. 보존 종료 조건은 해당 검토/판단의 완료 또는 Owner의 작업 포기 결정 후 사용 여부 재평가다. 활성 경로 이동/변경0, branch 삭제0이다. 이번 단계에서 삭제한 것은 앞서 정확히 식별한 검토용 파생 bytecode6개와 빈 디렉터리1개뿐이며, 이후 추가 삭제는 없다.


## 야간 후속 검토·보정 승인 — 2026-10-26 KST

Owner가 독립 검토 최대3회, 범위 내 최소 수정·오프라인 검증 최대2회, 결과 기록·조건 충족 정리를 일괄 승인했다. 기존 구독 인증 경로를 확인한 도구 없는 Claude CLI 검토에 실험 코드·합성 검사·비식별 증거 요약을 회당1 MiB, 총3 MiB 이내로 제공한다. 실제 프로젝트 문서 원문과 고객·계정·인증 자료는 제외한다.

새 묶음의 보수적 예산 시작은 2026-10-25T17:03:00Z, 작업 종료는20:43:00Z, 보존·보고를 포함한 전체 종료는21:03:00Z다. 기존 실행 장부와 소진량은 변경하지 않는다. 실험 Host/native 연결부의 국소 보정과 해당 테스트만 포함하며 Core authority·실제 프로젝트 적용·새 native 모델 실행·Git publication·Work Done은 포함하지 않는다. 새 코드가 과거 실제 실행 증거에 영향을 주면 해당 부분은 재검증 필요로 남긴다.

현재 source84/build70의 기술 실행 증거를 시작점으로 사용한다. 검토 입력·응답은 Driver 처분, Owner 최종 내용 수용 및 미해결 검토의 소비를 위해 비공개 작업 경로에 보존하며, 최종 결정 또는 명시적 중단 때 재평가한다. 이하 검토 원문과 Driver 처분은 구분해서 추가한다.


### 야간 독립 검토 1 — 실행 및 원문

고정 입력 910,267 bytes, SHA-256 `ab9a7f7b798707e2a0d865071b365843712e242e862590d420cd13aba6cf7f07`; runtime base `83086188ae0614bd882818ff1aa23f3194962012`, Host base `7d012f5297de1d9a77aa0b8187406f4785221573`의 미커밋 변경과 신규 입력48개를 포함했다. 비공개 packet은 역사 allocation과 일부 테스트 본문의 생략을 명시한다. 실제 프로젝트 문서 원문은 전달하지 않았다.

실제 model `claude-opus-5-5`, 새 session `0a546cde-f2c4-445c-99c8-c18193cfc163`; Claude Pro 구독 firstParty 인증을 호출 직전에 확인했다. 도구/MCP/tool use0, 363.180초, exit0/end_turn, process group 종료 및 입력 drift0이다. 서로 다른 모델의 새 정적 검토지만 Driver가 제공한 제한 packet에 의존한다. 아래 원문은 Reviewer의 판단이며 Driver의 재현 결과나 Owner 수용이 아니다.

~~~~markdown
# U2 source84 최종 독립 정적 검토 및 국소 보정계획 검토

## 0. 검토 성격과 경계

- 이 검토는 제공된 packet만 읽은 **정적 검토**입니다. 도구·명령·빌드·테스트·실행·편집·에이전트·외부 조회는 하나도 사용하지 않았습니다.
- 수치와 "관측"은 모두 **Driver 실행 보고**를 인용한 것입니다. Reviewer가 재현한 결과가 아닙니다.
- 이 검토는 다음 어느 것도 부여하거나 추론하지 않습니다.
  - 실행·수락 권한
  - 전체 Owner 수락
  - production qualification
  - 다른 host 적용 가능성
  - 일반 효율
- native runtime은 trusted native runtime으로 취급합니다. worker/verifier/proxy의 OS 격리가 runtime 자체의 file/exec/direct-egress 격리를 증명하지 않는다는 전제를 유지합니다.
- 생략된 source는 hash가 기록돼 있어도 **검토하지 않은 것**으로 봅니다. 생략 목록은 §5에 있습니다.
- R1(F1–F15)은 당시 후보에 대한 역사입니다. 현재 후보에 대해서는 아래 §1에서 다시 대조했습니다.

## 요약 판정

1. **H04/H05/H10 관측을 무효로 만드는 fail-open 결함은 찾지 못했습니다.** 제공된 source84 코드 범위에 한정한 정적 판단입니다.
2. **관측된 성공 경로 주변에 잠복 결함이 남아 있습니다.**
   - 비가역 Work stop이나 "effect 후 기록 누락"으로 이어질 수 있는 fail-closed 결함입니다.
   - 대표 예: S84-01, 02, 03, 04.
   - 그중 S84-01은 H10 해석에 직접 영향을 줍니다. 모델이 받은 남은 turn 수가 실제 할당과 달랐고, 최종 성공은 turn 상한에 정확히 닿은 상태였습니다(여유 0).
3. **계획 위험 (가장 중요):** 어떤 수정이든 source85가 됩니다.
   - source84의 H04/H05/H10 live 관측은 source85로 **승격되지 않습니다.**
   - 추가 live 실행은 승인 범위 밖입니다. 따라서 보정본은 최대 "offline 검증만 된 후보"가 됩니다.
   - 이 비용을 감수할지는 Owner가 판단할 문제입니다. 상세는 §4에 있습니다.

---

## 1. R1 F1–F15 현재 상태 대조

| R1 | 현재 판정 | 근거 (정적 / Driver 관측) |
| --- | --- | --- |
| F1 thread/start gate | **해소** | `prepared_thread_start_matches`가 raw/typed 두 gate 모두 `{ephemeral, dynamicTools}`를 정확히 비교합니다. U2 thread 성공도 관측됐습니다. |
| F2 SSE 완료 latch | **해소** | `spawn_prepared_response_stream`이 `pending_completed`를 EOF까지 보류합니다. client.rs의 `break`는 EOF 이후에만 일어납니다. gen2 성공(gen26)이 관측됐습니다. |
| F3 native MCP/plugin | **해소** | `disable_native_extensions`가 `enabled=false` overlay를 넣고 `disabled_live_config_snapshot`/`validate_live_disabled_config`로 동결합니다. |
| F4 실패→Work stop | **잔존 (계약)** | `run_live_command`의 `except`는 여전히 무조건 `stop`을 기록합니다. → S84-09 |
| F5 sleep clock | **해소** | Rust `mach_continuous_time`과 Python `continuous_ns`를 사용합니다(version ≥ 3). |
| F6 봉인 후 무기한 대기 | **부분 해소** | `idle_deadline_wall_ms`가 추가됐습니다. 다만 여유값이 부족합니다. → S84-02 |
| F7 NB 배타 lock | **해소** | Python은 `LOCK_SH` 읽기와 `bounded_flock`, Rust는 5초 재시도를 씁니다. |
| F8 body 미폐쇄 | **잔존** | → S84-08 |
| F9/F10/F11 envelope·header·proxy | **관측 범위 내 해소** | 정적 대조 테스트는 packet에 없습니다. 근거는 실제 성공 관측뿐이며, 해당 계정·host·model catalog에 한정됩니다. |
| F12 dup lease | **해소** | `ConnectionLease` drop → release/ack 프로토콜이 있습니다. leases 0이 관측됐습니다. |
| F13 proxy lineage count | **해소** | U2 경로는 부모 counts와 `prior_attempts`를 반영하고 `proxy_total`과 대조합니다. |
| F14 예약 선행 | **잔존 (낮음)** | → S84-10 |
| F15 실제 문서 refusal | **잔존 (낮음, 계약)** | → S84-11 |

---

## 2. 현재 Findings

각 항목의 분류는 둘 중 하나입니다.
- **[국소]**: Driver가 범위 안에서 자동으로 보정할 수 있는 구현 문제
- **[계약]**: Owner의 계약 변경이나 판단이 필요한 문제

### S84-01 [중간–높음 · 국소] H10 host turn 계산이 할당(13)이 아니라 legacy `PHASE_CAPS`(40)를 사용

- **Symbol:** `host.py::LiveSession.iterate`, `trusted_turn_input(..., remaining_turns)`, `PHASE_CAPS = {"h10": (2, 2, 40)}`
- **Trigger:** H10 v56 실행. 실제 journal 상한은 `u2_allocation(56)["turns"]=13`, `worker-result` 상한은 `turn_cap-1=12`입니다.
- **영향:**
  1. 모델에게 전달된 `remaining_turns`가 `40-used`였습니다. 신뢰 입력(trusted progress)의 값이 실제 할당과 달랐습니다.
  2. `require(left > 1)`은 "수락용 1 turn 보존"을 의도한 것으로 보이지만 실제로는 작동하지 않습니다. 편집이 13번째 turn까지 가면 그 turn의 `worker-result` 예약이 `U2 cap`으로 실패합니다.
  3. 이 실패는 `DocumentController.dispatch`에서 worker effect(쓰기)가 일어난 **뒤에** 발생합니다. 결과는 effect가 journal에 기록되지 않은 상태의 stop입니다.
  4. 최종 성공 시도가 turn 13 / generation 26이므로, 성공은 상한에 정확히 닿은 상태였습니다(여유 0). 이는 Driver 관측과 정적 구조를 조합한 추론입니다.
- **최소 보정:**
  - U2 version에서는 `cap = u2_allocation(v)["turns"]`를 쓰고, 편집 turn 허용을 `used < cap-1`로 제한합니다.
  - `remaining_turns`도 같은 cap 기준으로 계산합니다.
  - 합성 v56 fixture로 "12번째 편집 turn 이후 13번째 편집 입력 거절"과 "수락 turn에 remaining=1 전달"을 offline으로 확인합니다.
- **계획 위험:**
  - 모델 입력 내용(progress 값)이 바뀝니다.
  - source84의 H10 관측은 새 source로 이전되지 않습니다.
  - `TEMPLATE_VERSION`을 올릴지는 Owner가 판단합니다. 템플릿 의미 자체는 바뀌지 않지만 값이 정정됩니다.

### S84-02 [중간 · 국소 + 계약(시간 배분)] idle 종료 여유 60초가 auth 갱신창(5분)과 수락 turn 길이를 덮지 못함

- **Symbol:**
  - `idle_deadline_wall_ms` (`expiry - 60_000`)
  - Rust `validate_prepared_auth_json`: `expiry <= now + 5분`이면 거절. 모든 HTTP guard에서 호출됩니다.
  - 재개 후 `session.deadline()`: pause를 제외한 active 기준이며, proxy/auth의 wall 만료로 상한이 걸리지 않습니다.
  - Rust `Spec::reserve`의 `active_now <= expires_unix_ms`도 pause 제외 시간 기준입니다.
- **Trigger:** Owner 응답이 `auth_expiry − 5분`과 `idle_until` 사이에 도착하는 경우. 또는 수락 turn 도중 proxy/auth의 wall 만료를 넘는 경우.
- **영향:**
  - gen1 이전에 걸리면 송신 전 거절 → stop. 권한 효과는 없습니다.
  - 다음 순서로 진행되면 **권한은 적용됐는데 turn은 실패**합니다(host 결과 `refused`):
    1. gen1 → dispatch → `authority-apply` 예약
    2. Core apply 성공
    3. gen2에서 auth/proxy 만료로 거절
  - 이 경우 사람의 복구 판정이 필요합니다. `InstalledCore`의 prepare와 apply가 각각 최대 300초까지 걸릴 수 있어 위험 구간이 실제로 존재합니다.
  - 관측된 473.784초 대기에서는 이 경로가 발생하지 않은 것으로 보입니다.
- **최소 보정:**
  - `idle_until = min(now+900s, runtime−A, proxy−A, auth−5분−A)`로 계산합니다. A는 수락 turn 상한입니다.
  - 재개 후 client deadline도 proxy·auth의 wall 만료로 상한을 겁니다.
- **계획 위험:**
  - A를 크게 잡으면 Owner 대기 창이 0 이하가 될 수 있습니다. 이 경우 즉시 거절됩니다.
  - A 값은 시간 배분 문제이므로 **Owner 결정**입니다. 공식 변경만 국소 보정입니다.

### S84-03 [중간 · 국소] accept-request 전달이 원자적이지 않음

- **Symbol:**
  - `submit_acceptance` → `durable_private(run/"accept-request.json")`: `O_CREAT|O_EXCL`로 파일을 연 **뒤에** 내용을 씁니다.
  - controller의 `while not request_path.exists()` → `control_read` → `json.loads`
- **Trigger:** 0.2초 poll이 생성과 쓰기 사이의 짧은 창에 걸리는 경우.
- **영향:** 빈 파일이나 부분 JSON을 읽어 `JSONDecodeError`가 나고, generic except를 거쳐 `stop`이 기록됩니다.
  - `Acceptance` 생성 전이므로 권한 효과는 없습니다.
  - 그러나 봉인된 결과의 수락 기회를 잃습니다. 재개하려면 새 epoch가 필요합니다.
  - 확률은 낮지만 결과는 비가역입니다.
- **최소 보정:**
  - `submit_acceptance`가 `accept-request.json.partial`을 `durable_private`로 쓰고, `os.rename`으로 최종 이름에 옮긴 뒤 디렉터리를 fsync합니다.
  - rename은 nlink 1과 0o600을 유지하므로 `control_read` 조건을 그대로 충족합니다.
  - offline 확인: rename 결과 파일을 읽을 수 있는지, 부분 파일 이름은 감시 대상이 아닌지.
- **계획 위험:** 낮습니다. host-only 변경이며 runtime binary는 그대로입니다. 다만 host source identity는 바뀝니다.

### S84-04 [낮음–중간 · 국소] worker effect 이후 journal 예약 실패 시 effect가 기록되지 않음

- **Symbol:** `DocumentController.dispatch`에서 `worker-result` 예약이 effect 후에 이뤄집니다. 예약 전 확인은 `host-dispatch`만 있습니다.
- **Trigger:** effect 이후 다음 중 하나가 일어나는 경우.
  - `worker-result` 상한 초과 (S84-01)
  - `remaining_ms <= execution_reserve`
  - clock drift
  - lock deadline
- **영향:** 문서 effect는 일어났는데 journal에는 `worker-result`가 없습니다. 실행 디렉터리의 `result-metadata.json`에는 근거가 남으므로 forensic 복구는 가능합니다.
- **최소 보정:**
  - effect 전에 `budget.read()`로 해당 kind의 남은 용량과 예산 여유를 확인합니다. 원자성은 보장되지 않으므로 사전 확인입니다.
  - 실패 시 `failure.json`에 `effect_applied_unjournaled`를 명시합니다.
- **계획 위험:** 사전 확인과 실제 예약 사이의 경합은 남습니다. 이 한계를 문서화해야 합니다.

### S84-05 [낮음–중간 · 계약] 누적 상한이 상속만 되고 강제되지 않음

- **Symbol:** Rust `validate_u2_budget`와 Python `u2_budget_state`
  - `correction-content`는 v ≥ 41에서 부모 값(v56 부모 = 2)을 상속하고 증가만 시킵니다. `<= 2` 검사는 없습니다.
  - 실제 상한은 epoch별 `correction` 2와 `authority-apply` 1입니다.
  - legacy 검증기에는 누적 `correction-content <= 2`가 있었습니다.
- **영향:** policy의 `content_corrections: 2`, `authority_apply: 1`이 epoch별인지 누적인지 코드만으로는 알 수 없습니다.
  - 누적 의미라면 v56의 content correction 1회만으로 위반입니다. 부모 누적 authority-apply 1에 H10 1회가 더해져 2가 됩니다.
  - v56에서 correction이 실제로 일어났는지는 packet에 없습니다(§5).
- **최소 보정:** **Owner가 의미를 확정**해야 합니다. 누적이라면 양 언어에 cap 검사를 추가하고, epoch별이라면 상속 값은 보고용임을 명시합니다.

### S84-06 [낮음 · 계약] policy endpoint: guard는 예약하지만 U2/clock journal은 금지

- **Symbol:**
  - HTTP guard stage 1이 `reserve("control", {"endpoint":"policy"})`을 수행합니다.
  - U2와 clock 검증기는 `matches!(ep, "models"|"accounts")`만 허용합니다.
- **Trigger:** `prepared_policy_applicable == Some(true)`인 계정 (business/enterprise).
- **영향:** `runtime-entered` 이후 policy fetch가 반드시 실패하고, start 소모와 stop으로 이어집니다. fail-closed입니다.
- **Claim 한계:** 관측된 성공은 `known-not-applicable` 계정 경로로만 가능했던 것으로 추론됩니다. 실제 분류값은 packet에 없습니다(§5).
- **최소 보정:** **Owner**가 policy endpoint 허용 여부를 결정합니다. 허용한다면 양 언어 검증기와 `phase_transport_limit` 상한을 함께 수정해야 합니다.

### S84-07 [낮음–중간 · 국소(테스트 전용)] http-client prepared guard 테스트가 정적으로 컴파일되지 않음

- **Symbol:**
  - `http-client/src/client.rs::prepared_guard_tests`의 `PreparedUdsConfig { ... }` literal에 `max_requests`가 빠져 있습니다.
  - `prepared_uds.rs`의 struct에는 `pub max_requests: u64`가 있습니다.
- **영향:**
  - macOS `cargo test -p codex-http-client`가 컴파일되지 않습니다.
  - final guard의 direct/routed/unverified fail-closed 및 latch 테스트는 source84에서 **실행될 수 없었습니다.**
  - Driver baseline 목록에도 이 테스트는 없습니다.
- **최소 보정:** `max_requests: 1`을 추가하고 macOS에서 실행합니다.
- **계획 위험:**
  - runtime candidate hash는 바뀌지 않을 것으로 추정됩니다(cfg(test) 전용). 그러나 anchor에 결속된 `source_identity`의 산정 방식이 packet에 없으므로 source 변경으로 취급해야 합니다.
  - 수정하지 않는다면 검증 공백으로 기록해야 합니다.

### S84-08 [중간 · claim 한계 / 계약] request body가 닫힌 key 집합으로 검증되지 않음 (R1 F8 잔존)

- **Symbol:**
  - `bind_live_request`와 `validate_live_wire_input`은 일부 field만 비교합니다.
  - `validate_private_value`는 `wire["input"]`에만 적용됩니다.
- **영향:** `instructions`, `include`, `text`, `service_tier`, `reasoning.summary` 등 검사하지 않는 top-level 값이 그대로 송신될 수 있습니다. "자동 metadata 및 원천 분리 강제"를 closed-set으로 주장할 수 없습니다.
- **최소 보정 (선택):**
  - (a) `encrypted_content`를 제외한 전체 wire에 privacy 검사를 적용합니다. 위험이 비교적 낮습니다.
  - (b) top-level allowlist를 둡니다. 다만 live wire가 저장되지 않으므로 실제 key 집합을 알 수 없습니다. offline에서 확정하면 오거절 위험이 큽니다.
- **권고:** 이번 범위에서는 claim 한계로 기록하는 것을 권합니다. 보정은 Owner 판단입니다.

### S84-09 [구조 · 계약] 실패=stop 승격과 epoch별 literal 할당의 이중 구현 (R1 F4 잔존)

- **근거:**
  - 모든 refusal이 `stop`으로 기록됩니다.
  - U2 epoch 31–56(26개)마다 Rust와 Python 양쪽에 allocation literal과 version별 분기를 넣었습니다(예: start rename 목록이 49–53과 55에만 있음).
  - 그 결과 복구 1회마다 새 source와 build가 필요하고, 그때마다 live 증거가 이전되지 않습니다.
- **영향:** 이번 검토의 "증거 승격 불가" 제약은 이 구조에서 비롯됩니다. 생략된 historical arm의 parity는 검증하지 못했습니다. v56만 양 언어가 일치함을 확인했습니다.
- **보정:** 자동 보정 대상이 아닙니다. 데이터 기반 allocation과 start 실패/Work stop 분리는 Owner의 계약 재설계 사항입니다.

### S84-10 [낮음 · 국소] `runtime-entered` 예약이 결정적 로컬 검사보다 먼저 일어남 (R1 F14 잔존)

- `prepared_live::install`은 `reserve("runtime-entered")` 뒤에 다음을 수행합니다: `initialize_live`(`validate_directories`), `initialize_prepared_read_only_auth`(keyring no-prompt 등).
- host가 root와 디렉터리를 사전 검사하므로 위험은 줄었지만, keyring 및 auth root 실패 시 start가 소모됩니다.
- **보정:** 결정적 검사를 예약 앞으로 옮깁니다. runtime 변경이므로 candidate hash가 바뀝니다.

### S84-11 [낮음 · 계약] 실제 문서 특성이 stop으로 이어짐 (R1 F15 잔존)

- 범위 밖 상대 링크가 있으면 `WorkerRefusal`이 나고 stop됩니다.
- 같은 실패가 반복되면 `repeated failure`, 진행이 없는 turn이 있으면 즉시 stop됩니다.
- tool 없이 답한 turn은 다음 `input` 순서 검사에서 stop됩니다.
- 모두 계약과 일치하지만, 효율과 견고성에 대한 주장을 제한합니다.

### S84-12 [낮음 · 국소] actor 사칭 거절이 대소문자 구분 denylist

- **Symbol:** `Admission.__init__`의 `identity["actor"] not in ("owner","human","Owner")`. `"OWNER"` 등은 통과합니다.
- 실제 권한은 Core prepare와 grant 결속에 있을 것으로 보이지만, 해당 코드는 packet에 없습니다.
- **보정:** case-fold 비교 또는 grant actor allowlist를 사용합니다.

### S84-13 [claim 경계] H05 replay를 현재 U2 lineage에서 실행할 수 없음

- **Symbol:**
  - `RecoveryGate.replay`가 `budget.reserve("recovery-apply")`를 호출합니다.
  - U2 검증기의 `limits`와 Rust cap match에는 `recovery-apply`가 없습니다. policy도 `recovery_apply: 0`입니다.
- **영향:**
  - 현재 source의 `recover` 명령은 v31–56 budget에서 반드시 거절됩니다.
  - 따라서 "H05 S1–S5 관측"은 다른 budget, 다른 version, 혹은 다른 source에서 나온 것으로 추론됩니다.
  - 그 실행의 source/budget identity가 없으면 source84 증거로 볼 수 없습니다(§5).

---

## 3. H01–H10 주장 경계 (Driver 보고와 정적 판단을 분리)

| ID | Driver 보고 | 정적으로 지지되는 범위 | 주장 한계 |
| --- | --- | --- | --- |
| H01/H02 | negative 경로 포함 | Admission·callback·ticket bytes·fresh prepare 결속 구현 | S84-12. Core grant 검사는 packet 밖입니다. |
| H03 | worker OS 격리 | sandbox-exec literal profile, 4개 tool envelope | runtime 자체의 OS 격리는 증명되지 않습니다(trusted native). |
| H04 | 같은 편집 thread에서 수락 1회 | 경로 구현 확인 | source84와 해당 계정에 한정됩니다. |
| H05 | S1–S5 exact replay | RecoveryGate 구현 | S84-13: 실행 identity가 필요합니다. |
| H06/H07 | 합성 관측 | 구현 | 자연 H10 재시작과 동등하다고 주장하지 않습니다. |
| H08 | — | stop 경계 구현 | S84-01·02·03의 의도치 않은 stop 경로가 존재합니다. |
| H09 | 문서 사례 3개 | — | 효율 증명이 아닙니다. |
| H10 | 문서 5개 commit·게시·수락 1회 | 구현 | S84-01(여유 0, 잘못된 progress 값), S84-05, S84-06. 시간 896.7초 중 473.784초는 Owner 대기를 포함하므로 사람의 실제 소요 시간이 아닙니다. 내용·이해도·효율은 미판정입니다. |

---

## 4. 보정 계획 검토 (Driver 최대 2주기, offline 한정)

### 선택지 A (권장 기본): 코드 변경 없음

- source84를 "관측된 후보"로 유지합니다.
- S84-01~13을 known defects와 claim limits로 문서화합니다.
- 장점: 증거 무효화 비용이 0입니다.

### 선택지 B: 국소 보정 (source85, offline 검증만)

- **1주기 (host-only):**
  - S84-01: cap 바인딩
  - S84-03: 원자적 전달
  - S84-02: 공식만 변경. A는 Owner가 값을 정할 때까지 파라미터로 둡니다.
  - S84-04: 사전 확인
  - S84-12
  - S84-07: 테스트 field
- **2주기:** 변경 전후 diff 재검토, 합성 fixture 테스트, Rust/Python parity 확인.

#### 위험

1. source84의 live 증거는 source85에 적용되지 않습니다. source85는 H04/H05/H10이 **미관측**입니다.
2. S84-01은 모델 입력 값을 바꿉니다.
3. S84-02는 A 값에 따라 idle 창이 사라질 수 있습니다.
4. runtime 변경(S84-10)과 S84-06, S84-08은 candidate hash를 바꿉니다. 이번 범위에서 제외하는 것을 권합니다.

#### Owner 계약이 필요한 항목

- S84-02의 A 값
- S84-05 (누적 의미)
- S84-06
- S84-08
- S84-09
- S84-11

---

## 5. 부족한 입력과 검증 불가 주장

- **생략된 test 모듈:**
  - core prepared tests (focused13은 Driver 보고)
  - app-server lib test 3개
  - `prepared_uds_tests.rs`, `prepared_fd_tests.rs`
  - `journal_tests`, `offline_prepare_tests`, `header_tests`
- **재전송되지 않은 파일:** `turn_processor.rs`, protocol 파일, `Cargo.lock`. "unchanged accepted"라는 주장은 hash 대조 근거 없이 수용할 수 없습니다.
- **materializer 등:** materializer/spec 생성기가 없습니다. 그래서 다음을 확인하지 못했습니다.
  - `journal_lock`과 `append.lock`의 경로 동일성
  - proxy `expires_wall_ms`와 controller deadline의 관계
  - `source_identity` 산정 방식
- **v56 journal과 observations:**
  - policy classification (S84-06)
  - correction 사용 여부 (S84-05)
  - stop을 기록한 주체와 사유. 성공 경로 코드에는 `stop` 예약이 없는데도 "journal STOPPED"로 보고됐습니다.
- **H05 replay:** 실행의 budget version과 source identity (S84-13).
- **authority Core:** "prior unchanged evidence reused"의 근거가 되는 Core binary와 source hash 대조 기록.
- **allocation parity:** Python/Rust historical allocation arm 31–55 (S84-09).
- **실제 프로젝트 문서:** 검토 범위 밖입니다. 따라서 H10의 내용 품질은 판정할 수 없습니다.

## 6. 한계

- 모든 판단은 정적 추론입니다. 컴파일 실패(S84-07)를 포함한 어떤 항목도 실행으로 확인하지 않았습니다.
- "관측 범위 내 해소"는 Driver 보고를 신뢰한 분류일 뿐입니다. 다른 계정, host, catalog, 문서에 대해서는 아무것도 주장하지 않습니다.
- 이 검토는 Owner 수락, qualification, 실행 또는 권한 적용 승인을 의미하지 않습니다.
~~~~


### 야간 보정 R0 — 실행 및 원문

입력91,061 bytes, SHA-256 `f26fcae44b6647c52fedded7dd13cef73fc8593c064966e65e1bf9a83659b444`; 구체 국소 보정 계획과 원 코드 발췌·합성 근거를 전달했다. model `claude-opus-5-5`, fresh session `adf4e458-4b41-4be1-a61f-acd1cf241c4e`, 구독 인증 firstParty/Pro, 도구/MCP/tool use0이다. 221.501초, exit0/end_turn, process group 종료, 입력 drift0으로 완료했다. 아래는 원문이며 Owner 권한 또는 실행 검증으로 취급하지 않는다.

~~~~markdown
# U2 야간 보정 R0 — 구체 보정계획 정적 검토 (검토 2)

## 0. 검토 성격과 경계

- 이 검토는 제공된 packet만 읽은 **정적 검토**입니다. 도구, 명령, 빌드, 테스트, 실행, 편집, 에이전트, 외부 조회는 사용하지 않았습니다.
- 수치와 "관측", "실행", "불변 확인"은 모두 **Driver 보고**입니다. Reviewer가 재현한 결과가 아닙니다.
- 이 검토는 다음을 부여하거나 추론하지 않습니다.
  - Owner 승인이나 전체 수락
  - production qualification
  - 실행·적용 권한
  - 일반 효율
- 아래 "기술 권고"는 Reviewer의 기술 의견일 뿐입니다. 실행 여부는 Owner가 이미 정한 한도(최대 3회 검토, 최대 2회 최소 수정·오프라인 검증)와 Owner 판단에 따릅니다.
- 이번 R0의 대상은 보정 **계획**입니다. 실제 코드 diff와 테스트 결과는 R1(세 번째 호출)에서 검토합니다.
- source84/build70(H10), source66/build53(H04), H05 별도 recovery lane의 기존 관측은 **역사 증거로 그대로 보존**합니다.
  - overnight-fix1에는 H04/H05/H10 live 관측이 **없습니다**.
  - 계획도 이 점을 올바르게 명시하고 있습니다.

## 1. 요약 판정

1. 계획의 방향(국소, host 중심, offline 한정, 증거 비승격)은 이전 검토 §4의 선택지 B와 일치합니다. 범위 확대도 보이지 않습니다.
2. 다만 **계획 문장만으로는 보장되지 않는 지점 4개(B1–B4)**가 있습니다. R1 이전에 계획을 보정하기를 권합니다.
   - 핵심: S84-04 사전 검사가 worker 실행 중 흐른 시간을 반영하지 않으면, 가장 가능성이 높은 effect 이후 실패(시간 예산)를 막지 못합니다.
3. 세 가지 주요 쟁점에 대한 판단은 다음과 같습니다.

| 쟁점 | 판단 | 조건 |
| --- | --- | --- |
| no-clobber 원자 게시 (S84-03) | 원리상 타당 | dir fd 고정, 게시 후 identity 확인, 잔존 partial 처리 명시 |
| 사전 검사와 effect 이후 진단의 경계 (S84-04) | 경계 정의는 타당 | 시간 여유를 사전 검사에 반영, 진단 범위를 "write postcondition 이후 모든 예외"로 확장 |
| 남은 턴 계산 (S84-01) | 기존 계약을 강화 | 실패 지점이 effect 후 → effect 전으로 이동, 최대 편집 turn 수는 사실상 동일. 단 epoch 범위 정의와 수락 turn 자원 범위 명시 필요 |

---

## 2. Blockers — R1 전에 계획 보정이 필요한 항목

### B1. S84-04 사전 검사가 시간 예산의 경과를 반영하지 않음

- **현재 구조:**
  - `Budget.reserve`는 append 전에 `state["remaining_ms"] > execution_reserve_ms()`와 `not stopped`를 검사합니다.
  - worker는 `timeout = min(300, deadline − now − 20)`, 즉 최대 300초 실행될 수 있습니다.
- **문제:**
  - 사전 검사 시점에 통과해도, worker가 실행되는 동안 남은 예산이 줄어 `reserve("worker-result")`가 **effect 이후에** 거절될 수 있습니다.
  - 계획은 이 가능성을 "남는다"고만 적었습니다. 그러나 이것은 단순한 경합이 아니라 **결정적으로 예측 가능한 주된 실패 경로**입니다.
- **최소 보정:**
  - 사전 검사가 `remaining_ms − (worker timeout_ms + 여유) > execution_reserve_ms`를 요구하게 합니다.
  - 또는 worker timeout을 "사전 검사로 확인된 여유" 이하로 줄입니다.
  - 사용한 timeout 값은 진단에 기록합니다.
- **추가 조건:**
  - 사전 검사는 `_validate`만이 아니라 `reserve()`의 guard 조건(`remaining_ms`, `stopped`)도 포함해야 합니다.
  - 두 경로가 갈라지지 않도록, event와 row를 만드는 로직(`seq`, `prev`, `at_ms`, `sha256`)을 하나의 공용 함수로 분리하는 방식을 권합니다. 지금처럼 복제하면 이후 드리프트 위험이 생깁니다.

### B2. S84-01의 "현재 epoch" 범위와 수락 turn 보존 범위가 정의되지 않음

1. **epoch 범위:**
   - 현재 코드는 `state["events"]` 전체에서 `phase`가 같은 `turn`을 셉니다.
   - U2 journal이 부모 lineage를 담는지는 packet만으로 알 수 없습니다(이전 F13: 부모 counts 반영). 다음 두 가지가 불명확합니다.
     - `events`가 현재 epoch만 담는지
     - phase 이름(`h10`)이 epoch 사이에 재사용되는지
   - **보정:** 남은 turn 계산은 Rust와 Python 검증기가 turn cap을 강제할 때 쓰는 **바로 그 카운트**(같은 함수나 같은 state 필드)를 사용해야 합니다.
   - 추가로 다음 경우에는 `PHASE_CAPS`로 폴백하지 말고 **거절**해야 합니다(fail-closed).
     - U2 version 판정이 모호한 경우
     - `u2_allocation(version)`에 해당 version이 없는 경우
2. **수락 turn 보존 범위:**
   - 수락 turn 1회는 다음을 함께 소비합니다: `input`, `turn`, `generation` 2회(H10 관측: 26/13), `dispatch`, `host-dispatch`, `authority-apply`.
   - `left > 1`은 turn cap만 보존합니다.
   - 편집 turn 하나가 generation이나 dispatch를 2회 이상 쓸 수 있다면, turn은 남아도 수락 turn의 generation이나 dispatch가 부족할 수 있습니다.
   - turn당 dispatch를 1회 이하로 강제하는 코드는 packet에 없습니다. H10의 dispatch 13 = turn 13은 관측일 뿐 강제의 증거가 아닙니다.
   - **최소 보정:** 다음 둘 중 하나를 택합니다.
     - (a) 편집 turn 허용 조건에 "수락 turn 1회분 잔여 용량(input, turn, generation ≥ 2, dispatch, host-dispatch, authority-apply)"을 포함합니다.
     - (b) claim을 "turn cap 기준 보존"으로 좁혀 명시합니다.
   - (b)를 택해도 S84-04의 사전 검사가 effect 이후 worker-result 실패는 막아 줍니다. 그러나 수락 turn의 자원 부족은 막지 못합니다.
3. **수락 turn의 `remaining_turns` 값:**
   - 계획은 편집 경로(`iterate`)만 다룹니다.
   - sealed 수락 turn에 어떤 `remaining_turns`가 전달되는지는 packet에 없습니다.
   - **보정:** 같은 cap 공식을 적용하고, 테스트 (1)에 "수락 turn 입력의 remaining_turns = 1"을 추가합니다.

### B3. "기존 qualification Work 기록"이 대상 파일에 포함된 의미가 모호함

- 계획은 "옛 장부를 바꾸지 않는다"고 하면서, 대상 파일 목록에는 "기존 qualification Work 기록"을 넣었습니다.
- **보정:** 다음을 명시해야 합니다.
  - 새 기록은 **append-only 새 항목이나 새 파일**에만 씁니다.
  - 기존 항목(R1 원문, H04/H05/H10 기록, journal)은 바이트 단위로 불변이며, 변경 전후 hash를 남깁니다.
  - overnight-fix1 기록에는 host diff sha, Rust test diff sha, test 파일 hash를 결속합니다. 그래야 R1이 정확한 대상을 검토할 수 있습니다.

### B4. Rust test 컴파일이 기존 build 산출물을 건드리지 않는다는 보장

- 계획은 "native binary는 재빌드·교체하지 않는다"고 합니다.
- 그러나 `cargo test --no-run`이 기존 target 디렉터리를 공유하면 다음이 갱신될 수 있습니다: deps, fingerprint, incremental 산출물.
- **보정:**
  - task-owned 경로의 **별도 `CARGO_TARGET_DIR`**를 사용합니다.
  - 그리고/또는 build70 산출물의 hash를 변경 전후로 대조해 드리프트 검사에 포함합니다.

---

## 3. 항목별 정적 검토

### S84-01 남은 turn 계산

**계약 영향 (정적 추론):**
- 수정 전에도 실제 최대 편집 turn은 12였습니다. 13번째 편집 turn은 effect 후 `worker-result` cap 12에서 실패합니다.
- 수정 후에는 13번째 편집 turn이 **turn 시작 전에** 거절됩니다.
- 결론: 편집 용량은 같고, 실패 지점만 effect 전으로 앞당겨집니다. 기존 계약을 **강화**합니다.
- `remaining_turns` 값이 실제 할당과 같아지므로, 신뢰 입력의 정확성도 개선됩니다.

**산술 확인 (cap 13):**

| 진입 시 사용 turn | `left` | 결과 |
| --- | --- | --- |
| 11 | 2 | 12번째 편집 turn 허용 |
| 12 | 1 | 편집 거절 |

- 계획의 테스트 (1)과 일치합니다.
- H10 closeout(`turn` 13, `worker-result` 12)은 "편집 12 + 수락 1"이 cap에 정확히 닿았다는 이전 판단(여유 0)과 일치합니다(Driver 보고).

**TEMPLATE_VERSION:**
- 구조와 필드가 같다는 Driver 판단은 기술적으로 수용 가능합니다.
- 다만 값이 바뀌므로 모델 입력이 달라집니다. H10을 이전하지 않는다는 계획 문장은 적절합니다.
- 버전을 유지하는 결정을 기록에 남기고, Owner가 다르게 판단할 여지를 표시하기를 권합니다.

**필요 사항:** B2 반영, legacy 40 유지 테스트, 버전 판정 폴백 금지 테스트.

### S84-03 no-clobber 원자 게시

**타당한 점:**
- 다음 순서는 reader의 부분 JSON 관측 창을 제거합니다: `O_EXCL` + `0600` partial → 내용 fsync → `renameatx_np(RENAME_EXCL)` → 디렉터리 fsync.
- 일반 `os.rename`이나 `os.replace`를 배제한 판단은 맞습니다. 둘 다 기존 final을 덮어씁니다.
- rename은 inode를 유지하므로, `checked_open`의 조건(정규 파일, nlink 1, group/other 비트 없음)을 그대로 충족합니다.
- worker 발췌에서 `RENAME_EXCL=0x4`와 ctypes 호출 형태가 동일하게 쓰인 것을 확인했습니다(정적).

**필수 최소 보정:**
1. **디렉터리 fd 고정:**
   - `durable_private`는 경로 문자열로 열고 부모를 따로 엽니다.
   - 생성, rename, fsync를 모두 **하나의 run 디렉터리 fd**(`O_DIRECTORY|O_NOFOLLOW`)를 기준으로 수행하기를 권합니다(`dir_fd`, `renameatx_np(dirfd, partial, dirfd, final, 0x4)`).
   - run 경로 자체의 canonical 여부도 확인합니다.
2. **게시 후 identity 확인:**
   - final에 대해 `lstat`을 수행합니다.
   - partial의 `fstat`에서 얻은 `(st_dev, st_ino)`와 같은지, `nlink == 1`인지 확인합니다. worker의 `swap-replaced` 검사와 같은 방식입니다.
3. **실패 처리:**
   - `renameatx_np`가 `EEXIST`, `ENOTSUP` 등으로 실패하면 거절합니다.
   - 이 경우 partial을 지울지 보존할지 명시해야 합니다. 이 결정은 보정 4번과 함께 정합니다.
4. **잔존 partial:**
   - partial 이름이 고정이므로, rename 전에 크래시가 나면 남은 partial 때문에 이후 모든 submit이 거절됩니다.
   - 결과는 fail-closed이지만, 수락 기회를 잃는다는 점에서 원래 문제(S84-03)와 같습니다.
   - 둘 중 하나가 필요합니다.
     - (a) 이 상태를 "사람 판정 필요"로 명시하고 테스트합니다.
     - (b) 시도마다 고유한 partial 이름(`O_EXCL`)을 씁니다.
5. **run 디렉터리 검사:**
   - controller나 closeout에 run 디렉터리의 파일 목록 검사가 있다면, partial이나 진단 파일 때문에 거절될 수 있습니다. 해당 코드는 packet에 없습니다.

**테스트 권고:**
- 실제 커널 호출로 다음을 확인합니다: final이 이미 있을 때 `renameatx_np` 거절, 기존 final 바이트 불변.
- 실제 reader poll 로직(`exists` → `control_read` → `json.loads`)을 partial이 존재하는 상태에 대해 실행합니다.
- 계획의 "partial 작성 중 final 부재" 검사는 쓰기 도중 중단 hook을 쓸 가능성이 큽니다. 그렇다면 **합성 interleaving**으로 표기합니다.

### S84-04 사전 검사와 effect 이후 진단

**경계 정의 (타당):**
- 사전 검사는 "예약이 아니라 사전 확인"입니다.
- 실제 reserve는 그대로 수행합니다.
- 실패 시 retry나 성공 처리를 하지 않고, 원 예외를 다시 올립니다.
- 이 경계는 이전 권고와 일치합니다.

**필수 최소 보정 (B1 외):**
1. **진단 범위:**
   - write effect가 확정되는 시점은 postcondition `require`가 통과한 이후입니다.
   - 그 뒤 `worker-result` append 전까지 `self.check_files()`도 실패할 수 있습니다. 이 경우도 effect는 일어났는데 journal에는 기록되지 않습니다.
   - 진단은 append 실패만이 아니라, **"postcondition 통과 이후, append 성공 이전의 모든 예외"**를 덮어야 합니다.
2. **진단 기록 실패:**
   - `journal-failure.json`을 쓰다가 실패해도 원 예외가 가려지면 안 됩니다. 예외를 연결(chaining)해 보존합니다.
3. **effect 필드 구분:**
   - read와 verify는 문서 effect가 없습니다.
   - `effect_applied_unjournaled`는 write에서만 true로 둡니다.
   - read와 verify는 "worker는 실행됐으나 문서 effect 없음"으로 구분해 기록합니다.

**권고 (비차단):**
- **사전 검사 위치:**
  - `correction` reserve는 worker 실행 전에 일어납니다.
  - 사전 검사를 그 **앞에** 두고 correction row와 worker-result row를 함께 검증하면, 사전 거절 때 correction이 불필요하게 소모되지 않습니다.
  - 그 뒤에 둔다면 "사전 거절 시 correction이 이미 소모됨"을 기록합니다.
  - 어느 쪽이든 slot 디렉터리 생성 전에 두기를 권합니다.
- **placeholder 값:**
  - result digest와 identity를 고정 64자리 값으로 두는 방식은 validator가 이 두 필드를 **형식만** 검사할 때에만 동등합니다. validator 코드는 packet에 없습니다.
  - read와 verify는 effect 전에도 실제 `result_identity()`를 알 수 있으므로 실제값 사용을 권합니다.
  - write는 placeholder 사용을 R1에서 validator 발췌로 확인해야 합니다.

### S84-07 Rust 테스트 field

**정적 확인:**
- `PreparedUdsConfig`에는 `pub max_requests: u64`가 있고, test literal에는 없습니다. 따라서 컴파일 오류가 예상됩니다.
- `PreparedUds::new`의 조건은 `max_requests != 0`, slot `s4`에서 `≤ 44`입니다. 값 1은 이를 통과합니다.
- 다른 field(nonce 64 hex, canonical parent)도 발췌 범위에서는 통과로 보입니다.

**주의:**
- "unverified" 사례는 `HttpError::Build`를 기대합니다.
- 외부 sandbox가 네트워크를 거절하면 다른 오류 타입이 나올 것으로 추정되며, 이 경우 테스트는 **실패**합니다(거짓 통과가 아님). 단 이것은 정적 추정이며 R1에서 결과 원문을 확인해야 합니다.
- 변경 전 컴파일 실패를 기록하는 것은 적절합니다.
- **offline cargo 환경:**
  - offline cargo도 `CARGO_HOME` lock이나 cache에 쓰기가 필요할 수 있습니다.
  - 권한을 넓히지 말고, 막히면 **incomplete로 보존**합니다. 계획 원칙과 일치합니다.

**claim 경계:**
- 이 수정은 cfg(test) 전용입니다.
- build70 binary가 이 테스트로 검증되었다는 의미가 아닙니다. "같은 source의 test build에서 final guard 경로를 검증"했다는 뜻입니다.
- runtime source diff hash는 바뀝니다.

### S84-12 actor 대소문자

**정적 판단:**
- `casefold`는 `OWNER`, `Human` 등을 막습니다.
- 그러나 denylist 방식이므로 다음은 여전히 통과합니다.
  - 전각 문자 `ＯＷＮＥＲ` (casefold로 정규화되지 않음)
  - 앞뒤 공백이나 제어 문자
  - zero-width 문자 삽입

**최소 보정 권고:**
- NFKC 정규화 후 casefold합니다.
- 앞뒤 공백과 제어 문자를 거절합니다.
- 또는 delegate actor의 형식 allowlist를 적용합니다. 다만 실제 actor 값의 형식이 packet에 없어 오거절 위험을 평가할 수 없습니다.

**claim:** 계획대로 "Host label guard 보강이며 Core 인증의 대체가 아님"으로 유지합니다.

---

## 4. 검증 계획 및 실행 환경 검토

1. **테스트 (1)–(6)의 구성:** 대체로 적절합니다. 다음을 추가하기를 권합니다.
   - 수락 turn `remaining_turns = 1` (B2)
   - 버전 폴백 금지 (B2)
   - 시간 예산 사전 거절 시 journal과 문서 바이트 불변 (B1)
   - postcondition 이후 `check_files` 실패 진단 (S84-04)
   - 잔존 partial (S84-03)
   - 전각 문자와 공백 actor (S84-12)
2. **v56 합성 budget:**
   - 현재 fixture는 `version: 1` anchor입니다.
   - v56 U2 검증기가 부모 lineage나 counts를 요구한다면, 합성 v56 budget을 구성할 수 있을지 packet만으로 판단할 수 없습니다.
   - 실제 H10 journal을 복사해 쓰는 방식은 계획의 "실제 프로젝트 접근 거절"과 충돌할 수 있습니다. 합성 구성이 불가능하면 incomplete로 기록하기를 권합니다.
3. **694개 재실행 생략:**
   - Driver 기록상 drift 대상은 다음 네 파일입니다: `host.py`, `worker.py`, fixture, `test_u2_host.py`.
   - 이번 변경 대상도 host와 Host test(그리고 필요 시 fixture)입니다.
   - 다음 조건을 R1 증거로 남기면 생략 판단을 기술적으로 수용할 수 있습니다.
     - 변경 후 **`host.py` 자체**를 import하거나 경로로 로드하는 test 소비자 목록을 다시 확인합니다. 기존 note는 fixture 소비자만 다룹니다.
     - claim은 "원 706 PASS는 역사, 694는 상속, 새 full PASS 아님"을 유지합니다.
4. **단위 불일치:**
   - "U2 tests 12"와 "focused 95/mode"는 세는 단위가 달라 보입니다(test 함수와 check/subTest).
   - R1 결과에 집계 단위를 명시하기를 권합니다.
5. **중첩 sandbox:**
   - 외부 Seatbelt deny-default 아래에서 Host test가 `sandbox-exec`를 호출하면, 중첩 sandbox 적용이 거절될 수 있습니다.
   - 이 경우 권한을 확대하지 말고, 실패를 환경 제약으로 분리해 기록합니다. 실패를 결함 부재나 통과로 해석하지 않습니다.
6. **시간 상한과 06:03 KST 전역 중단 우선:** 적절합니다. 현재 시각과 남은 시간은 packet에 없어 평가하지 않습니다.

---

## 5. 미변경 항목과 증거 정정 검토

| 항목 | 판단 |
| --- | --- |
| S84-02 | 알려진 제약으로 남기는 것을 수용합니다. 변경하지 않으면 claim에서 "auth 갱신창과 수락 turn 길이를 보장하지 않음"을 유지합니다. 참고로 A 없이도 `auth − 5분 − 60초`로 바꾸는 것은 기존 Rust guard와 맞추는 정정입니다. 다만 효과는 "송신 전 거절이 조금 앞당겨짐"에 그쳐, 미적용도 수용 가능합니다. |
| S84-05 | Driver 보고(누적 authority 2 = H04 1 + H10 1, v56 correction 0, 누적 content 2)는 이전 검토의 부족 입력을 보완합니다. 그러나 policy의 `authority_apply: 1`이 epoch별인지 누적인지는 **여전히 계약 미확정**입니다. "별도 정확한 Owner 승인 2건"은 packet에 원문이 없어 **검증할 수 없습니다**. claim에 누적 2를 명시하는 것은 적절합니다. |
| S84-06 | `known-not-applicable`(Driver 보고)로 이전 추론과 일치합니다. 범위 확장을 하지 않는 결정을 수용합니다. |
| S84-08/09/10/11 | 유지를 수용합니다. 기존 claim 한계를 그대로 둡니다. |
| S84-13 | 제공된 H05 controller 원문은 다음과 같고, 정적으로 지지됩니다. 실제 실행은 Driver 보고입니다. 상세 조건은 아래에 정리합니다. |

**S84-13 정적으로 지지되는 내용:**
- 별도 version 1 anchor와 `recover` spec을 사용합니다.
- native 결과의 closed 상태와 leases 0, process 부재를 확인합니다.
- 원 티켓의 바이트와 decision 결속을 확인합니다.

**S84-13 남는 조건:**
- `host_source_sha256 1e5de…`가 어느 Host source 번호에 해당하는지 대응 기록이 packet에 없습니다.
- `invocation.json`의 `max_recovery_apply: 5`는 기록일 뿐입니다. version 1 검증기가 5회 상한을 강제하는지는 packet에 없습니다.
- "U2 v31–56에 recovery-apply 추가 없음"은 v56 발췌에 대해서만 정적으로 확인됩니다. 31–55 arm은 제공되지 않았습니다.

**이전 검토 정정 (Reviewer 측):**
1. 이전 §3 표의 H04 "source84와 해당 계정에 한정"은 Driver 보고에 따라 **source66/build53**으로 정정합니다. 해당 hash 대조 기록은 packet에 없습니다.
2. 이전 §5의 "stop 기록 주체"는 다음과 같이 확인됐습니다: Driver의 postcondition 검증이 host 종료 후 `h10-completed` stop을 append했습니다(Driver 보고). 따라서 이 stop은 Host 자동 기록이 아니라 **Driver가 사후에 추가한 event**로 분류합니다.

---

## 6. 기술 권고 (Reviewer 의견, 권한 아님)

- B1–B4와 §3의 필수 최소 보정을 계획에 반영한다는 조건으로, 이 보정 묶음을 **offline 후보(overnight-fix1)로 진행하는 것은 기술적으로 타당**하다고 판단합니다. 이 판단은 실행 승인이 아닙니다.
- 반영하지 않으면 다음 claim 제한이 필요합니다.
  - S84-04는 "시간 예산 경과에 따른 effect 이후 실패를 막지 못함"
  - S84-01은 "turn cap 기준 보존만"
- 어느 경우든 overnight-fix1은 다음 상태입니다.
  - live H04/H05/H10은 **미관측**입니다.
  - source84/66의 관측은 역사로만 남습니다.

## 7. 부족한 입력과 검증 불가 주장

- **U2 검증기 관련:**
  - `_validate`와 U2 검증기의 worker-result subject 검사 내용(placeholder 동등성)
  - turn cap 카운트의 epoch 범위
- **할당과 turn 구조:**
  - `u2_allocation(56)`의 kind별 전체 할당(generation, dispatch, input 등)
  - turn당 dispatch 1회 강제 여부
- **수락 경로:** 수락 turn의 `trusted_turn_input` 호출부와 controller의 accept-request 감시 및 run 디렉터리 검사 코드
- **identity 대응:**
  - H05 Host hash와 source 번호의 대응
  - version 1 검증기의 recovery-apply 상한
  - H04 source66/build53과 H10 build70의 hash 대조 기록
- **승인 원문:** H04/H10 Owner 승인 원문 (S84-05의 "별도 정확한 승인")
- **불변 확인:** "Core/launcher/inventory 불변", "694개 상속"은 Driver 기록이며, Reviewer가 재확인하지 않았습니다.

## 8. 한계

- 모든 판단은 정적 추론입니다. 이번 R0는 어떤 계획 항목도 실행이나 diff로 확인하지 않았습니다. 최종 코드와 결과는 R1에서 검토합니다.
- 다음은 이 검토가 판단하지 않은 사항입니다.
  - 다른 계정, host, catalog, 실제 문서
  - 내용 품질과 효율
  - Owner 수락 및 qualification
~~~~


## 2026-10-26 야간 일괄 후속 — overnight-fix1 오프라인 검증 완료 / 최종 독립 검토 차단

Owner의 야간 일괄 승인 아래 source84를 출발점으로 검토1 지적 S84-01/03/04/07/12를 한 묶음으로 국소 수정했다. 검토2 R0의 B1–B4 조건을 반영했다. Host remaining_turns, 수락 요청의 원자 게시, worker-result 사전 검사·effect/journal 진단, actor label 검사, Rust cfg(test) 필드 누락이 대상이다. Core authority 및 이미 수락한 실제 문서·primary·Work 상태는 수정하지 않았다. 새 source 번호/epoch/live 권한도 배정하지 않았다.

검증: unittest test ID107개(기존95+신규12) normal/parent-O 각각 PASS, 오류·실패·skip0. 원706은 역사 PASS, 무영향694는 상속 근거이며 새 전체 실행이 아니다. Rust 변경 전 missing max_requests E0063 재현 후 수정본 crate test compile 및 exact final guard PASS. build70 실행 바이너리3개 불변, 기존 실제 증거6개와 H10 journal5개 불변을 확인했다. worker 진단 검사는 합성 파일·모의 subprocess이며, 현재 후보의 actual-native/H10 실행은0이다.

최종 독립 검토 입력은679,976바이트/SHA256 a3a31c19b83f0e6f039e7f8f92dae2f8f8bd176e6ab3a658859ef33efcd06e9a로 준비했으나 자동 승인 검토가 정확한 내부 소스 입력과 Claude 외부 전송 대상에 대한 승인을 확인하지 못했다는 이유로2회 차단했다. 원 일괄 승인 근거를 제시한 뒤에도 거절되어 우회하지 않았다. 세 번째 reviewer CLI는 미호출·전송0바이트다. 검토1/2 원문은 위 역사 항목에 그대로 보존돼 있으며 수정본에 대한 R1 ACCEPT는 없다. Driver 자체 검증을 Reviewer 판정이나 Owner 수용으로 대체하지 않는다.

미변경/잔여: S84-02 auth margin·수락시간, S84-05 누적/epoch 의미, S84-06 해당 계정 정책 관측 한정, S84-08 전체 request-body privacy claim 제외, S84-09/10/11 fail-closed/시도 소모/고정 oracle, S84-13 별도 recovery-only lane. H04는 source66/build53, H10은 source84/build70, H05는 별도 v1 원 티켓5개 범위다. 전체 qualification/Owner 내용·이해도·효율 판단은 미완료이며 Work Active를 유지한다.

정리: 중복 발췌·완료된 socket ownership 파일2개 및 비어 있는 이번 실행 디렉터리20개만 삭제. active 경로 이동/worktree 제거/branch 삭제0. 두 실험 worktree와 수정 전3개 소스, diff, 결과, 미전송 packet은 최종 검토·Owner 판단·국소 복구에 필요해 보존한다. 최종 판단 또는 명시적 중단 뒤 재평가한다.

실행·결과·해시·상세 지적별 판단과 보존 조건은 기존 작업 artifact의 overnight-review-proposal/morning-report.md, fix1-validation.json, execution.json에 기록했다. commit/push/PR/merge/release는 실행하지 않았다.


## 2026-10-26 09시 후속 — 최종 R1 ACCEPT (offline 국소 diff 범위)

Owner가 고정 입력679,976바이트를 기존 Claude Pro 경로로 보내는 최종 검토 요청에 “계속하자”로 재개를 승인했다. 만료된 야간4시간 상한은 변경하지 않았고 이번 검토·보고에 별도 bounded followup을 기록했다. 이전 자동 승인 검토 차단은 이번 재개 승인 뒤 해소됐다.

Reviewer: claude-opus-5-5, fresh session `2e0d1036-6b0f-4fce-aea4-54429fd2e1cb`. 기존 Claude Pro/claude.ai/firstParty 인증 확인, 도구0/MCP0, 호출271.693초, exit0, process group absent, 입력 드리프트0. 세 번 모두 같은 Claude 모델 계열의 새 세션이며 이번 입력에 이전 두 검토 의견을 제공했으므로 blind review는 아니다. Driver와 Reviewer의 역할은 분리했다.

입력 SHA256 `a3a31c19b83f0e6f039e7f8f92dae2f8f8bd176e6ab3a658859ef33efcd06e9a`,679,976바이트. 응답 SHA256 `c5e4c71edc4aef61001194973703c3c0fef0dca2cdd8ca28620cea5dcf884e86`,19,468바이트. 이번 승인 묶음의 검토는3/3회, 총 전송1,681,304바이트로 종료했다. 다음 원문은 계산·테스트를 직접 수행하지 않은 Reviewer의 정적 판단이며, 실행 수치는 Driver 결과를 인용한 것이다.

### 최종 Reviewer 응답 원문

~~~~text
# Overnight-fix1 결과 R1 — 세 번째(최종) 독립 정적 검토

## 0. 검토 성격과 경계

- 제공된 packet만 읽고 판단한 **정적 검토**입니다. 도구, 명령, 빌드, 테스트, 실행, 편집, 하위 에이전트, 외부 조회는 사용하지 않았습니다.
- 다음은 모두 **Driver 실행 보고**를 인용한 것이며, Reviewer가 재현하지 않았습니다.
  - 107 test ID PASS
  - Rust 변경 전 E0063 재현, 변경 후 compile/exact test PASS
  - build70 binary 3개 불변
  - Work prefix hash, diff/파일 sha256
- 이 검토는 다음 어느 것도 부여하거나 추론하지 않습니다.
  - Owner 승인·수락, 전체 Owner acceptance
  - production qualification
  - 실행·authority 권한
  - 내용 수용, 효율
- H04(source66/build53), H05(별도 version1 recovery-only Host), H10(source84/build70)의 관측은 **역사 증거**로만 보존합니다. overnight-fix1에는 live H04/H05/H10 관측이 없으며, 이번 검토가 그것을 이전하지 않습니다.
- 다음은 검토하지 않았습니다. 이번 검토는 이들의 fresh review가 아닙니다.
  - 생략된 역사 allocation map(Python 32–55, DIAGNOSTIC/CLOCK)
  - 재전송되지 않은 Rust runtime 전체
- 세 번째이자 마지막 검토라는 사실 때문에 판정을 완화하지 않았습니다.

---

## 1. 판정

**ACCEPT (offline 범위)**

### 적용 범위
- 아래 세 파일의 diff만 대상입니다. 위 consolidated diff 내용 그대로이며, Driver가 보고한 diff_sha256과 결속됩니다.
  - `host.py`
  - `tests/test_u2_host.py`
  - `http-client/src/client.rs`의 `cfg(test)` literal 1줄
- 이 diff가 다음을 충족한다고 판단합니다.
  - S84-01/03/04/07/12의 국소 결함을 기존 계약을 약화시키지 않고 보정함
  - R0의 B1·B2·B4와 필수 조건을 반영함
  - B3는 아래 §2에 적은 미확인 부분을 제외하고 반영함

### 적용되지 않는 것
- live/native/provider 경로의 동작
- H10 결과가 새 Host에서도 재현된다는 주장
- runtime 전체의 정합성
- 694개 비-U2 테스트의 새 PASS
- 생략된 allocation map

### 무효화 조건
- 이후 세 파일 중 어느 것이든 **한 바이트라도 바뀌면** 이 ACCEPT는 적용되지 않습니다.
- 남은 검토 호출이 없으므로, 아래 findings는 **추가 코드 수정보다 known limitation으로 기록할 것을 권합니다**. 수정한다면 그 수정은 검토되지 않은 변경입니다.

아래 findings(N1–N10)는 모두 **비차단**입니다. fail-open이나 계약 약화는 발견하지 못했습니다.

---

## 2. R0 조건 반영 대조 (정적)

| 조건 | 판단 | 근거 |
|---|---|---|
| **B1** 사전검사가 시간 경과를 반영 | 충족 | 아래 B1 상세 참조 |
| **B2** epoch 범위와 수락 turn 보존 | 충족 | 아래 B2 상세 참조 |
| **B3** Work append-only | 부분 확인 | prefix hash(629566 bytes, `06b0…`) 보존만 보고됨. 새 절에 diff/hash가 결속됐는지는 이 R1이 append된 뒤의 일이라 **미확인** |
| **B4** build 산출물 보존 | 충족 (Driver 보고) | 아래 B4 상세 참조 |
| 원자 게시 조건 | 충족 | 아래 원자 게시 상세 참조 |
| effect 진단 조건 | 충족 (N2/N3 단서) | 아래 effect 진단 상세 참조 |
| actor 조건 | 충족 | 아래 actor 상세 참조 |
| 집계 단위 | 충족 | test ID 단위 명시, 95+12=107. 새 class의 12개 ID가 목록에 있음 |

### B1 상세
- `_candidate_row`가 `reserve()`와 사전검사의 guard(`remaining_ms > execution_reserve`, `not stopped`)와 row 구성·검증을 함께 묶습니다.
- `check_worker_result`는 `LOCK_SH`로 읽고, append하지 않습니다.
- worker timeout은 `min(requested, (remaining − reserve − 20 s))`로 축소되고, 그 값이 `worker-admission.json`에 기록됩니다.

### B2 상세
- **epoch 범위:** `u2_budget_state`의 `events`는 현재 rows만 담습니다(`history_events`는 별도). 따라서 `sum(kind=="turn")`은 validator의 `used['turn']`과 동치이며, Rust 1657행 `turn_cap`과도 같은 기준입니다.
- **fail-closed:** version ≥31이면 `u2_allocation`이 미등록 version을 거절하고, phase가 cfg와 다르면 거절합니다. bool, 0, 문자열 version도 거절합니다. legacy(≤30)만 `PHASE_CAPS`를 씁니다.
- **수락 turn 입력:** 수락 turn은 `run_live_command`에서 literal `1`로 호출됩니다(정적 확인).
- **수락 자원은 validator 구조로 보장됩니다(정적 확인).**
  - plan당 `dispatch` ≤1(`p['call'] is None`)
  - plan당 `host-dispatch` ≤1
  - plan당 `worker-result` ≤1(`not p['result']`)
  - 다음 `input`은 직전 plan의 `generation==2`를 요구
  - 따라서 편집 12 turn 뒤에도 수락 1 turn에 필요한 input/turn 13, gen 25–26, dispatch/host-dispatch 13, authority-apply 1이 남습니다.

### B4 상세
- 기존 target을 재사용하는 대신 binary 3개의 hash를 대조하는 방식을 택했습니다. R0가 "그리고/또는"으로 허용한 범위입니다.

### 원자 게시 상세
- 단일 run dir fd를 고정하고, 다음을 같은 fd 기준으로 수행합니다.
  - partial을 `O_EXCL`·0600으로 생성하고 fsync
  - partial의 inode, nlink, mode 확인
  - `RENAME_EXCL`로 게시
  - final의 inode, nlink, mode 확인
  - dir fsync
- 잔존 partial은 자동 삭제·재시도 없이 거절됩니다.

### effect 진단 상세
- postcondition 전 실패는 `effect_applied=None`, 확인 후 실패는 `True`, append를 시도한 경우는 `unconfirmed`로 기록합니다.
- 진단 쓰기가 실패해도 원 예외 객체를 다시 raise합니다.
- read/verify는 `False`입니다.
- correction은 환급하지 않습니다.

### actor 상세
- type, 빈 값, 앞뒤 공백, Unicode 범주 C(제어·Cf zero-width 포함)를 거절합니다.
- NFKC 후 casefold해 예약 label을 거절합니다.
- identity 원문과 hash는 보존됩니다.

### 추가 정적 확인
- 사전검사의 placeholder 동등성(R0 미결 질문)을 확인했습니다.
  - Python `u2_budget_state`와 Rust 1701–1702행 모두 `worker-result` subject의 `result_sha256/result_identity/oracle_sha256`에 대해 **길이 64만** 검사합니다.
  - 따라서 `"0"*64` placeholder는 형식상 동등합니다.
- 이번 diff는 Python/Rust의 budget validator 자체를 바꾸지 않습니다. 따라서 journal 의미와 Rust parity는 이 diff로 변하지 않습니다.

---

## 3. 항목별 정적 검토

### S84-01 남은 turn 계산 — 계약 강화

- **cap 13 산술**
  - 진입 시 사용 11 → `left` 2 → 12번째 편집 허용
  - 사용 12 → `left` 1 → 거절
- **효과**
  - 13번째 편집 turn은 이제 **effect 전에** 거절됩니다. 이전에는 worker effect 후 `worker-result` cap(12)에서 실패했습니다.
  - 편집 용량은 동일하고, 실패 지점만 앞당겨집니다.
  - 모델에 전달되는 `remaining_turns`가 실제 할당과 일치하게 됩니다.
- **TEMPLATE_VERSION**
  - 유지 결정은 기술적으로 수용 가능합니다.
  - 다만 같은 template identity 아래 숫자의 의미가 정정되었다는 사실을 Work에 명시해야 합니다. 모델 입력과 `input_sha256`이 달라지므로 H10 이전은 불가합니다.

### S84-03 원자 게시

- reader의 감시 대상(`exists()` → `control_read` → `json.loads`)은 final 이름 하나입니다. rename은 원자적이므로 부분 JSON 관측 창이 제거됩니다.
- rename 후에도 nlink 1과 0600이 유지되어 `checked_open` 조건을 그대로 충족합니다.
- **경합 분석 (정적)**
  - 두 submitter가 동시에 사전검사를 통과한 경우를 보겠습니다.
  - 한쪽은 partial의 `O_EXCL`에서 실패하거나, rename 단계에서 `EEXIST`로 실패합니다.
  - 어느 쪽이든 final은 보존되고, 이중 전달은 발생하지 않습니다.
  - 커널 no-clobber 테스트가 이 rename 단계를 실제 커널로 확인합니다(Driver 보고).

### S84-04 사전검사와 사후 진단

- 사전검사는 worker spawn 직전에 위치하며, 실패하면 spawn하지 않습니다.
- 사전검사는 correction 예약 **뒤에** 있습니다. 따라서 사전 거절 시 이미 소모된 correction은 환급되지 않습니다. 계획과 일치하며 테스트로 확인됩니다.
- 사전검사와 실제 예약 사이의 경합은 남습니다. 원자 예약이 아니라는 점은 정직하게 명시되어 있습니다(N6).

### S84-07 Rust

- `max_requests: 1`은 `PreparedUds::new`의 조건(≠0, s4에서 ≤44)을 통과합니다.
- 이 테스트는 guard 단계에서 거절되므로 UDS 송신에 도달하지 않습니다.
- 변경은 cfg(test) 전용이며, build70 binary를 검증한 것이 아닙니다. "같은 source의 test build에서 final guard 경로를 확인"했다는 의미입니다.

### S84-12 actor

- Host label guard 보강입니다. Core 인증을 대체하지 않습니다.
- homoglyph(예: Cyrillic `о`)는 막지 않습니다. 계획에 명시된 한계입니다.

---

## 4. Findings (모두 비차단)

### N1 [낮음–중간] rename 이후 예외 시 "이미 전달됐는데 실패로 보고"되는 모호성
- **위치:** `publish_acceptance_request`
- **문제:**
  - `renameatx_np` 성공 이후 단계(`published` identity 확인, `os.fsync(parent)`)에서 예외가 나면 submitter는 실패로 끝납니다.
  - 그러나 controller는 이미 final을 읽고 수락 turn으로 진행할 수 있습니다.
- **안전성:** 재제출은 final 또는 partial 존재로 거절되므로 이중 전달은 없습니다.
- **위험:** Driver나 운영자가 "submit 실패 = 미전달"로 해석하는 것입니다.
- **최소 조치 (권고, 비코드):** Work와 운영 절차에 "rename 이후 오류는 publication outcome unconfirmed이며, controller 결과로만 판정한다"를 기록합니다.

### N2 [낮음] `journal_outcome="unconfirmed"`가 과보수적
- `reserve()` 내부의 validator 거절(cap, budget, stop)은 append 전에 확정적으로 일어납니다. 그런데도 `journal_attempted=True`이므로 `unconfirmed`로 기록됩니다.
- 안전한 방향의 부정확성이며 거짓 주장은 없습니다.
- 진단을 읽을 때 "append 미발생이 확정된 경우도 포함됨"을 명시합니다.

### N3 [낮음] `raise error from record_error`의 인과 방향이 역전됨
- 원 예외 객체와 타입은 보존됩니다(요구 충족).
- 그러나 `__cause__`가 "원 오류가 진단 실패 때문에 발생했다"는 반대 의미를 기록하고, 원 예외에 기존 `__cause__`가 있었다면 덮어씁니다.
- `run_live_command`는 타입명과 HostRefusal 문자열만 남기므로 영구 증거에 미치는 영향은 작습니다.
- 차기 보정 후보: `add_note` 사용 또는 암묵적 `__context__` 유지.

### N4 [낮음] 사전검사 거절 시 slot 수준 진단이 없음
- 거절은 spec/request/profile 생성 뒤 `try` 밖에서 발생합니다.
- 그 결과 slot에는 `worker-admission.json`, `failure.json`, `journal-failure.json` 모두 없습니다. 근거는 journal의 stop 사유뿐입니다.
- forensic 해석 시 "slot에 프로세스 기록이 없으면 사전 거절"로 읽는다는 규칙을 기록해야 합니다.

### N5 [낮음, 기존 동작 유지] 아주 작은 양의 timeout이 허용됨
- 예: 여유가 20.001 s이면 timeout은 0.001 s입니다.
- 이 경우 사실상 timeout이 확정된 spawn이 일어나고, write라면 `effect_unknown` 경로로 갑니다.
- 이전 `require(timeout > 0)`와 같은 동작이므로 약화는 아닙니다.
- 하한을 도입하는 것은 새 시간 정책이므로 이번 범위 밖입니다.

### N6 [낮음] 20 s 후처리 여유와 잔여 경합
- worker가 timeout 끝까지 실행되면 이후 남는 시간은 약 20 s입니다.
- 그런데 `end_process`가 잔존 process group 때문에 최악 약 20 s(SIGTERM/SIGKILL 각 10 s)를 쓰면, 이후 `check_files`·`result_identity`를 거친 뒤 `reserve`가 예산 거절될 수 있습니다.
- 이 경로는 N2의 `unconfirmed` 진단으로 관측 가능하며, 원자 예약이라고 주장하지 않는다는 계획과 일치합니다.

### N7 [테스트 공백]
- `iterate` 테스트는 `SimpleNamespace` budget을 씁니다. 실제 U2 journal/validator와 turn count가 동치라는 점을 통합 테스트로 확인하지 않았습니다(정적으로는 동치).
- controller의 실제 poll loop(`run_live_command` 대기 루프)는 실행하지 않았습니다. partial 가시성은 `exists()` 단언과 합성 interleaving으로만 확인했습니다.
- `worker-admission.json`의 존재와 timeout 값은 단언되지 않습니다.
- 수락 turn의 `remaining_turns=1`은 함수 단위 확인과 call site의 literal(정적)뿐입니다.
- 진단 테스트 4개는 Mock budget과 Mock subprocess를 씁니다. 실제 append I/O 실패 의미를 확인하지 않습니다(Driver도 한계로 명시).

### N8 [기존, 범위 밖] legacy 분기의 계산 기준 불일치
- `state["events"]`는 현재 rows 기준입니다.
- 반면 legacy validator는 lineage 전체의 `phase_counts`로 turn cap을 강제합니다.
- 다중 epoch legacy에서는 `remaining_turns`가 과대해질 수 있습니다. 이번 diff가 바꾸지 않았고, 현재 U2 경로에는 영향이 없습니다.

### N9 [기존 관찰]
- Rust의 `#[cfg(prepared_pipeline)]` 경고는 해당 cfg 아래 코드(`prepared_uds_tests.rs` 487행 이하)가 **컴파일도 실행도 되지 않음**을 뜻합니다.
- 실행된 Rust 테스트는 exact 1개뿐입니다(126 filtered). crate 전체 test PASS가 아닙니다.
- parent-O 실행에서 기존 FD 테스트의 `SyntheticTcp.connect` 내부 `assert`(fd-reserved가 connect보다 먼저인지)는 무력화됩니다. 이번 diff와 무관한 기존 테스트 약점입니다.

### N10 [낮음] run dir 확인 시점의 TOCTOU
- `resolve(strict=True)==run` 확인과 `os.open(..., O_NOFOLLOW)` 사이에 중간 경로 component가 교체될 수 있습니다. O_NOFOLLOW는 마지막 component에만 적용됩니다.
- 기존 Host 관행과 같은 수준이며, run dir 쓰기 권한을 가진 주체를 전제로 합니다.
- 보강하려면 worker의 `parent_fd`처럼 component마다 O_NOFOLLOW로 따라가거나, 열린 fd의 fstat과 lstat identity를 대조합니다.

---

## 5. Driver 실행 증거와 정적 추론의 구분

### Driver 보고 (Reviewer 미재현)
- Host와 document 107 ID가 normal과 parent-O 각 1회 PASS (0 error / 0 failure / 0 skip)
- Rust 변경 전 E0063, 8.627 s
- 변경 후 `--no-run` compile PASS, exact guard 1개 PASS
- build70 binary 3개 불변
- `git diff --check` PASS
- Work prefix 불변
- actual_native false, authority_apply 0

### 정적 추론 (Reviewer)
- §2와 §3의 동치성 판단: turn count, placeholder, 수락 자원 구조
- 경합 분석과 N1–N10

### 실제 커널 동작을 쓴 테스트 (Driver 보고)
- RENAME_EXCL no-clobber
- partial 잔존
- 실제 U2 validator와 실제 v1 stopped parent를 쓴 사전검사 cap
  - 단, 이 테스트의 v31 allocation은 **합성**(turns 2)이며 v56 실측이 아닙니다.

### 합성 테스트 (Driver 보고)
- scheduler interleaving
- 시간 여유 주입(`_read_locked` patch)
- worker 진단(실제 파일 쓰기 + 모의 subprocess)

### 694개 비-U2 테스트
- 입력 불변 재사용입니다. 원 706 PASS는 역사이며, **새 전체 PASS가 아닙니다.**

---

## 6. 재검사가 필요한 구체 위험 (향후 live 또는 별도 승인 시)

1. **편집 turn 12회 소진 시 동작 변화:** 이전에는 13번째 편집 turn이 시작됐지만, 새 Host는 이를 시작 전에 거절하고 stop합니다. 같은 문서 작업이 12 turn 안에 봉인되지 않으면 Work가 중단됩니다. 정정된 `remaining_turns`가 모델 행동을 바꿀 수 있어 H10 결과(13/26)의 재현은 보장되지 않습니다.
2. **worker timeout 축소:** 예산 여유가 작을 때 worker가 이전보다 짧은 timeout으로 실행됩니다. 실제 문서 크기와 verifier(JavaScriptCore GFM)의 소요시간에서 timeout 실패 빈도가 바뀌는지는 미관측입니다(N5, N6).
3. **실제 run dir에서의 게시:** macOS 실제 run dir에서 `renameatx_np`가 지원되는지, umask, controller poll과의 상호작용은 합성 경로로만 확인했습니다(N1, N7). 실제 파일시스템 종류는 packet에 없습니다.
4. **actor 거절 확대:** 실제 delegate actor 값이 공백, Cf, 범주 C 문자를 포함하는지는 packet에 없습니다. 포함한다면 offline에서 드러나지 않는 거절이 발생합니다.
5. **N1 운영 해석:** submit 오류를 근거로 재시도나 상태 판정을 하면 잘못된 기록이 생길 수 있습니다.

---

## 7. 미변경 항목과 역사 구분

- **S84-02/05/06/08/09/10/11/13 유지:** 수용합니다. 미해결이거나 범위 밖인 항목은 다음과 같습니다.
  - auth refresh margin과 수락 시간 충분성
  - 전체 request-body privacy closed-set
  - 범용 재시작과 자동 recovery
  - 사용자 실제 소요시간과 효율
  - 내용 수용
- **누적 authority:** 실제 2회(H04 1 + H10 1). v56 content correction 0, 전체 content correction 2(Driver 보고).
  - policy 명칭의 누적/epoch 의미는 여전히 **미확정**입니다.
  - Owner의 exact 승인 원문은 전송 범위에서 제외되어 **독립 검증할 수 없습니다.**
- **H05:** max5는 controller cases 수와 고정 티켓 목록에 의한 제한입니다. v1 Budget의 일반 recovery cap으로 주장하지 않습니다.
  - Host digest와 source 번호의 대응은 미확인이며, 번호를 발명하지 않습니다.
  - U2 v31–56에 recovery-apply가 없다는 판단은 공통 `u2_budget_state`의 closed `limits` 집합(recovery-apply 없음)과 Rust의 `_ => bail!` 분기에서 정적으로 지지됩니다.
- **H10 stop:** Driver가 Host 종료 뒤 추가한 closeout 기록입니다. 소스가 자동으로 기록한 stop이 아닙니다.

---

## 8. 누락 입력과 검증 불가 주장

- after_sha256, diff_sha256 값과 제공된 diff 텍스트의 일치: Reviewer가 계산할 수 없습니다. full Host는 allocation map이 생략된 형태라 after hash와 대조할 수 없습니다.
- `worker.py`, fixture, `test_u2_documents_v2.py` 불변 주장: diff에 없다는 점만 확인했고 hash는 미확인입니다.
- Work에 append될 새 절의 내용과 결속(B3 후반부)
- 실제 delegate actor 값, 실제 run dir 파일시스템
- 생략된 Python allocation 32–55 및 DIAGNOSTIC/CLOCK map, Rust runtime 전체
- Owner 승인 원문(H04/H10/H05)
- H05 Host digest와 source 번호의 대응
- 실행 환경(Seatbelt 정책 원문, 실제 logs)의 원문. 요약 JSON만 제공되었습니다.

---

## 9. 한계

- 모든 판단은 정적 추론입니다. 컴파일, 테스트, 커널 동작을 직접 확인하지 않았습니다.
- 이 ACCEPT는 overnight-fix1 diff의 **offline 국소 보정 적합성**에 대한 기술 판단일 뿐입니다. 다음을 의미하지 않습니다.
  - live 동작, H04/H05/H10 재현
  - runtime 전체 정합성
  - Owner 승인, production qualification
  - 실행·authority 권한
  - 내용 품질과 효율
- 이후 검토 호출이 없으므로, 이 응답 이후의 모든 코드 변경은 검토되지 않은 상태입니다.
~~~~

### 검토 대상의 정확한 결속과 B3 완료 기록

기존 Work의 직전 전체 prefix 632471바이트/SHA256 `a42f24d8a6a5e94148c675f91dbbc13e81c0196cfe572a3c0d336e08fb13305d`를 그대로 보존한 뒤 이 절을 append했다. 원 R0 전 prefix629,566바이트/SHA256 `06b0550df6a7c0a3c7f9a014470480f0a41f68f357cc0f54617d5c955cacfd89`도 불변이다. 아래 diff SHA는 수정 전 보존 소스와 현재 소스의 국소 unified diff에 결속된다. 입력21개 파일의 해시는 호출 전·후와 기록 직전에 확인했다. 이는 Reviewer가 미확인으로 남긴 B3 후반부에 대한 Driver 사후 검증이며 독립 재검토를 뜻하지 않는다.

| 대상 | 수정 전 SHA256 | 검토된 수정 후 SHA256 | 국소 diff SHA256 |
| --- | --- | --- | --- |
| Host host.py | `b1e3109ff468634c8bc1e10aecf4d160c3f0769225c5dc8d7d2818851093e6ef` | `4555c2f91fa3ba5970f299c11bafe6809f3faa0b4a9cfc2e7658f7693d4b26ba` | `1576e93bd75a4fa8147f9907d851456200fa85320c76d2ea617a108389757107` |
| Host tests/test_u2_host.py | `099a4c6f4a330438b039a4425f9ffd370ab1818a3bc0ea9fec5c85b950a02fe2` | `55e5d24d7f88f94a36bf7ac4b29fd3b5c66c1022b3987366102d9e313c8e3ea9` | `899c04c32128fb3d5d565f5a5ff75bc26b4b548b1fdb11a90e2614b58e93d14c` |
| runtime http-client/src/client.rs cfg(test) | `9f08f94c982a7a352767493b2f609be3bfe5f5491458c3bf92cfd221035c38bb` | `42b429523632bfbd72b4b66cf7a8e9e159b8ee25572543314717d332950aa9e8` | `1ac1ff4d2bf2785ced56a491c41a55d5a913253f29d1aa3705c5b4154aca7597` |

### Driver 판단과 운영상 한계

Driver는 수정된 세 파일의 국소 diff에 대한 offline ACCEPT를 수용한다. 차단 결함은0, 비차단 지적은 N1–N10이다. 검토 이후 소스3개를 변경하지 않았고 새 테스트나 실제 실행도 하지 않았다. 이 판정은 live/runtime 전체/production/Owner 수용을 뜻하지 않는다. 기존 Work Active를 유지한다.

| 지적 | Driver 처리 |
| --- | --- |
| N1 게시 후 오류 | 수용. rename 이후 오류는 publication outcome unconfirmed로 해석한다. submit 실패만으로 미전달을 단정하거나 자동 재시도하지 않는다. controller 결과·journal·프로세스 상태로 확인한다. 현재 코드의 자동 진단 필드가 새로 생긴 것은 아니며 운영 해석 규칙이다. |
| N2 journal unconfirmed | 수용. append 이전 validator 거절까지 포함한 보수적 상태임을 기록한다. 문서 effect와 journal 확정 여부를 분리한다. |
| N3 예외 원인 연결 | 수용/후속 후보. 원 예외는 보존되지만 cause 방향과 기존 cause 손실 가능성이 있다. 이번 검토본은 유지한다. |
| N4 사전 거절 진단 | 부분 수용. slot 수준 사전 거절 기록 부족은 맞다. 다만 process.json 부재만으로 worker 미시작을 확정하지 않는다. 실제 코드는 Popen 다음 process.json을 쓰므로 그 사이 실패·중단도 가능하다. stop/failure 기록과 프로세스 부재를 함께 확인한다. |
| N5/N6 시간 여유 | 수용. 아주 짧은 timeout과 cleanup이20초 여유를 소모하는 경합이 남는다. 사전 검사를 원자 예약이나 실행 후 journal 성공 보장으로 주장하지 않는다. 새 timeout 하한·시간 정책은 도입하지 않는다. |
| N7 합성 검사 공백 | 수용. 실제 poll loop, 실제 append I/O 실패, 실제 v56 iterate 결합은 새로 실행하지 않았다. 기존107 PASS는 해당 합성 assertion 범위다. |
| N8 legacy lineage | 수용/범위 밖. legacy 다중 epoch의 phase count 불일치는 이번 U2 수정과 분리한다. |
| N9 Rust/parent-O 범위 | 수용하되 실행 근거로 한정한다. Rust는 crate test compile 및 exact1개 PASS이며126개 filtered다. prepared_pipeline cfg 경로의 PASS를 주장하지 않는다. 기존 SyntheticTcp의 Python assert는 parent-O에서 비활성화되므로 모든 normal assertion과 동등한 검증이라고 주장하지 않는다. |
| N10 run 경로 경합 | 수용/기존 한계. 중간 path component 교체 경합을 해결한 것으로 주장하지 않는다. |

S84-02/05/06/08/09/10/11/13의 기존 한계는 유지한다. 수정본의 실제 H10/provider 경로는 미관측이며, 현재 source84/build70 실측을 새 Host의 실측으로 이전하지 않는다. TEMPLATE_VERSION은 구조·필드·의미를 유지한 remaining_turns 숫자 버그 보정으로 유지했다. input_sha256과 모델 입력은 달라진다. 다음 실제 실행을 한다면 턴12회 후 봉인 여부, 줄어든 worker timeout, 실제 run 경로의 게시/오류 해석, 실제 actor 값이 필요한 검증 대상이다. 그 실행은 이번 정적 검토의 승인 범위에 없다.

검토 입력·응답·실행 경계·3개 수정 전 소스·테스트 결과는 Owner의 전체 qualification/내용 판단과 국소 복구에 필요해 보존한다. 해당 판단 또는 명시적 중단 뒤 보존 필요를 재평가한다. 종료된 이번 reviewer의 빈 scratch 디렉터리만 제거하며 active 경로 이동·worktree 제거·branch 삭제는 없다.


## 2026-10-26 H10 재검증 일괄 실행 승인

Owner가 고정 승인안 SHA-256 43c839c75b1dc4614920c1d4247aede059ad0330b6ed63cbd2c010df69c3de0e 및 실제 데이터 전달, 누적180분 범위를 승인했다. 시작00:41:25Z, 작업중단03:21:25Z, 최종중단03:41:25Z. 계획 R0 차단0일 때 준비를 진행하는 조건부 승인이고 exact intent/grant 및 봉인 결과의 두 Owner 확인은 유지한다. 현재 실제 모델/authority 실행0. 실행 증거 경로: `private-evidence/E153`. 원 문서/기존 수락 불변. 이 절은 기존 기록 뒤 append이며 전체 qualification 수용을 뜻하지 않는다. [공개용 중립화]


## H10 재검증 R0 결과와 준비 진입 조건

R0는 계획 범위 ACCEPT, 차단0. 실제 Reviewer claude-opus-5-5, fresh session ae2cd02e-f0ea-4509-8de6-c5bdd2054c77, tools/MCP0, 174.473초, exit0. 전송45,627bytes, 입력 drift0, process group 종료 확인. 이전 의견을 전달했으므로 blind review가 아니다. 실행·내용 품질·Owner 수용은 검토하지 않았다. 원 manifest execution_authorized=false는 승인 전 역사값이며 현재 승인은 이 Work의 직전 절과 private 실행 기록이 별도로 보존한다. owner_input_sha256은 모델의 작업 지시 식별자이고 이번 Owner 실행 승인 식별자가 아니다.

Driver 처분(모두 기존 범위 안):

- P1 accept: process.json 부재만으로 spawn 부재를 주장하지 않는다. 불명확 시 중단하고 실제 worker bytes와 baseline/직전결과를 대조한다. 양성 process 종료 증거와 journal/controller 기록을 함께 보며 모호성을 무효 시도로 환급하지 않는다.
- P2 accept: 준비 보정 최대2회는 R1 전만. R1 뒤 실행 코드 동결, 차단 시 중단, 비차단 지적은 known limitation으로 남긴다. 검토는 R0/실행전R1/결과검토 총3회 이내다.
- P3 accept with clarification: 기술 조건부 수용은 정확한 tree·메시지 일치, Core completed/selected result·journal authority1·process 종료·원본 불변, 최종 evidence/claim 검토 차단0을 모두 요구한다. 품질·부담이 미측정이면 기술 범위(b)만 가능하다. Owner가 두 번째 확인에서 품질·부담 입력 및 해당 범위의 조건부 수용을 명시하면 (a) 판단도 그 Owner 입력에 근거하며 Reviewer가 대신하지 않는다.
- P4 accept: 품질은 Driver 파일별 대조와 Owner 직접 확인. Claude 최종 검토는 비식별 실행근거와 claim 정합성만 다룬다.
- P5 accept: 마지막 성공13턴은 편집12+수락1 총13이다. 이번17턴/새Host/새input은 동일 snapshot에 대한 새 경로 재검증으로만 부른다.
- P6 accept: Owner 결과확인에 result_identity·5파일SHA·commit message 원문을 제공하고 커밋후 tree/message 불일치면 accept하지 않는다.
- P7 accept: 00:41:25Z 시작/03:21:25Z 작업중단/03:41:25Z 최종중단. native45분은 시작부터 봉인·Owner대기·수락·종료까지 포함. R1후 기한 연장없음.
- P8 accept: H04 source66/build53, H05 별도v1 recovery Host, H10 source84/build70. 재관측하지 않은 것은 상속/역사로 표시한다.

I1–I10을 준비/실행 검증에 대조한다. I9는 불필요하게 미확정으로 만들지 않는다: 새 epoch authority1, 과거2와 분리하여 누적최대3이며 그 수치를 검증한다. I8은 Host의 선택 view·입력 결속 증거이며 전체 provider request-body closed-set privacy 보장으로 확대하지 않는다.

준비 구현 선택: 기준 reference-a-baseline-revision에는 tracked colvia와 기존 .hrn authority가 있다. 통째 checkout은 fresh init 전제에 맞지 않는다. 승인된 독립 Git 초기화 범위에서 해당 commit의 프로젝트 파일을 기존 .hrn/colvia 없이 새 primary에 가져와 git init하고 정식 init한다. 고정32개 입력으로 시작 content를 구성한다. worker의 whole-tree baseline 증명을 위해 새 초기 baseline commit이 필요하다. 이 commit은 아직 하지 않고 첫 Owner 확인에서 정확한 tree/message와 intent/grant를 함께 제시한다. 이후 worker를 그 승인된 baseline에서 만들고 exact spec을 생성한다. 기존 primary/worker/index/refs는 변경하지 않는다. 이는 원 commit의 재현이나 기존 authority 복제가 아니다. [공개용 중립화]

R0 원문:

[공개용 중립화] 다음 code block의 식별 정보는 공개용으로 바꿨다.

~~~~text
# H10 재검증 R0 — 계획 정적 검토

## 0. 검토 성격과 경계

- 이 검토는 제공된 승인안, manifest 메타데이터, 이전 R1 응답만 읽은 **정적 검토**입니다. 도구, 명령, 실행, 편집, 외부 조회는 사용하지 않았습니다.
- 승인안의 "확인된 출발점"은 모두 **Driver 보고**이며 Reviewer가 재현하지 않았습니다. 여기에는 다음이 포함됩니다.
  - 드리프트 0
  - 107 test ID PASS
  - digest 일치, 86,954 bytes
  - 설치본 상태, 커밋 clean 여부
- 이 판정은 다음 어느 것도 부여하거나 추론하지 않습니다.
  - Owner의 결과 수용, 전체 Owner acceptance
  - production qualification
  - 실행 권한, authority
- 실행 권한은 Owner 승인 기록에서만 나옵니다. 그러나 manifest에는 `execution_authorized: false`가 남아 있고, Owner 승인 원문은 packet에 없습니다. 원문은 `owner_input_sha256`으로만 식별되므로 Reviewer가 검증할 수 없습니다.
- 계획 검토이므로, 구현이 아직 없다는 사실은 결함으로 보지 않았습니다.

---

## 1. 판정

**ACCEPT (계획 범위, 차단 결함 0)**

- 범위·기준을 material하게 바꾸라는 요구는 없습니다. 따라서 승인안의 조건부 준비(단계 2–3) 진입 조건은 이 R0 기준으로 충족됩니다.
- 아래 §3의 P1–P8은 **실행 전 확정해야 할 조건**입니다.
  - 모두 기존 승인 범위 안에서 기록이나 절차로 해소할 수 있습니다.
  - 승인된 범위를 넓히지 않고 오히려 좁히는 해석입니다.
  - Work append 기록으로 남기면 충분하며, 승인안 본문을 재작성할 필요는 없습니다.
- 다만 다음 경우에는 이 조건이 충족되지 않은 것으로 보고 중단해야 합니다.
  - Driver가 어느 조건이든 기존 범위 안에서 충족할 수 없다고 판단하는 경우
  - 해소하려면 코드 기능 추가, 검토 호출 추가, 한도 변경이 필요한 경우
- §4는 비차단 구현 확인 항목입니다.

---

## 2. 차단 결함

없음.

다음 계약 요소는 정적으로 일관됩니다.

- **Owner 확인 지점 2곳:** 모델 시작 전 exact intent/grant 확인, 그리고 수락 전 결과·ticket·commit 확인이 모두 독립 확인 지점으로 유지됩니다.
- **중단 조건:** R0/R1 차단 시 자동 재시도 없이 중단합니다.
- **산술:** turn당 generation 2를 반영하면 17턴, generation 34, dispatch 1이 맞습니다.
- **수락 turn 보존:** 편집 최대 16턴 + 수락 1턴 구조는 S84-01 보정(남은 1턴이면 편집 거절)과 정합합니다.
- **보존 원칙:** 원 primary와 기존 수락을 보존합니다.
- **publish 오류 해석:** "publish 오류 ≠ 미전달" 원칙이 이전 R1의 N1을 반영합니다.
- **전송 대상 수:** 지정 view 32개 = 출력 시작본 5개 + 근거 27개로, manifest 항목 수와 일치합니다.

---

## 3. 실행 전 확정 조건

모두 기존 범위 안이며 비차단입니다. 다만 단계 2 착수 전에 Work에 기록해야 합니다.

### P1. spawn 부재의 증명 규칙 (이전 N4 추론 대체)

- **문제**
  - Driver가 지적한 대로, `process.json`이나 slot 진단 파일이 없다는 사실만으로는 "spawn 없음"을 증명할 수 없습니다.
  - 승인안은 "프로세스 종료 대조"를 말하지만, 어떤 **양성 증거**로 판정하는지 정하지 않았습니다.
- **최소 조치 (비코드)**
  - 사전 거절이나 slot 기록 부재는 "spawn 여부 미확인"으로 분류하고, 성공 근거로도 무효 근거로도 쓰지 않습니다.
  - effect 판정은 파일 존재 여부가 아니라 **실제 바이트**로 합니다. 즉 worker tree를 baseline·직전 결과 digest와 대조합니다.
  - 해당 시점 이후는 중단 또는 사람 판단 대상으로 남깁니다.
- **범위:** 기존 범위 안입니다.
- **선택 조치:** pre-spawn 거절 기록을 코드로 추가할 수도 있습니다. 이 경우 admission 진단 변경이므로 R1 packet에 반드시 포함해야 합니다. 필수 조건은 아닙니다.

### P2. R1 이후 바이트 동결과 검토 호출 회계

- **문제**
  - 검토 호출 3회는 R0(이번), 실행 전 R1, 최종 검토로 정확히 소진됩니다.
  - 그런데 국소 준비 보정 2회와 R1의 순서가 명시되지 않았습니다. R1 뒤에 보정하면 재-R1이 필요해 4번째 호출이 생깁니다.
- **최소 조치 (기록)**
  - 국소 보정 2회는 모두 **R1 전에만** 허용합니다.
  - R1 후에는 실행 대상 바이트를 동결합니다.
  - R1 차단 시에는 재-R1 없이 중단합니다(승인안 중단 조건과 같습니다).
  - R1의 비차단 지적은 수정하지 않고 known limitation으로 기록합니다.
- **범위:** 기존 범위 안입니다. 반대로 R1 후 수정이 필요하다면 검토 호출 추가라는 **material 변경**이 됩니다.

### P3. 조건부 최종 수용의 적용 한계

- **문제 1:** 부담 자료(Owner가 직접 알려주는 활동 시간, 재설명 횟수 등)는 Owner 입력 없이는 생성되지 않습니다. 따라서 결과 확인 자리에서 미리 걸어 둔 조건부 수용은 선택지 (a)를 자동 성립시킬 수 없습니다.
- **문제 2:** Claude의 최종 검토 결과는 Owner 수용이 아닙니다.
- **최소 조치 (기록)**
  - 조건부 수용 문구에 다음을 열거형으로 고정합니다.
    - 어떤 postcheck인지
    - 어떤 최종 검토인지
    - "새 차단 없음"의 판정 기준
  - 자동 적용은 최대 (b) 기술 범위까지로 제한합니다.
  - (a)는 Owner의 품질·부담 입력을 받은 뒤 별도로 결정합니다.
  - 조건 충족 여부에 대한 Driver의 평가 자체를 Owner에게 제시합니다.
- **범위:** 기존 범위 안입니다. 확인 지점을 추가하는 것이 아니라 기존 3번 확인의 생략 조건을 좁히는 것입니다.

### P4. 품질 판정의 주체

- **문제:** 최종 Claude 검토에는 실제 문서 본문이 전송되지 않습니다. 따라서 파일별 정확성·누락·근거 대응을 판정할 수 없습니다.
- **최소 조치 (기록)**
  - 파일별 품질 표의 근거 주체를 "Driver 대조 근거 + Owner 직접 확인"으로 명시합니다.
  - 최종 검토의 대상은 실행 증거와 claim 정합성으로 한정합니다.
- **범위:** 기존 범위 안입니다.

### P5. "회귀 재현"이 아닌 조건 변화의 명시

- **문제:** 이번 실행은 기존 H10과 다음 조건이 다릅니다.
  - cap 13 → 17
  - `remaining_turns` 의미 정정(이전 R1 §3 S84-01)
  - 새 Host/Rust 바이트
  - 새 `input_sha256`
- 따라서 "H10 결과 재현"은 성립하지 않습니다. "같은 스냅샷에 대한 새 Host 경로 재검증"이 정확한 표현입니다.
- 또한 "마지막 성공 13턴"이 총 turn(편집 12 + 수락 1, 즉 13/26)을 뜻하는지, 편집 turn만 뜻하는지가 승인안에서 모호합니다.
- **최소 조치 (기록):** 위 두 가지를 명시합니다.
- **범위:** 기존 범위 안입니다.

### P6. 결과 identity의 정의

- **문제**
  - Owner 확인은 commit 생성 **전**에 이루어지므로, commit hash는 그 시점에 정해지지 않습니다.
  - 따라서 "승인한 정확한 결과 = 실제 수락 결과"를 무엇으로 대조할지 정의되지 않았습니다.
- **최소 조치**
  - Owner에게 다음을 identity로 제시합니다.
    - `result_identity`
    - 5개 파일 blob sha(또는 tree sha)
    - commit message 원문
  - commit 생성 후 tree와 message가 일치하는지 대조합니다. 불일치하면 수락하지 않고 보존합니다.
- **범위:** 기존 범위 안입니다.

### P7. 시간 결속의 고정

- **문제**
  - 실행기 기한은 R1 대상 바이트에 포함되므로, R1 후에는 연장할 수 없습니다(P2와 연동).
  - native phase 45분 안에 봉인 대기, Owner 확인 10분, 수락 turn이 포함되는지 불명확합니다.
- **최소 조치 (기록)**
  - 180분 기준의 시작 시각을 기록합니다. 이 R0도 단계 1이므로 180분 안에 포함됩니다.
  - 기한은 180분 중단점 이전으로 바인딩합니다.
  - 45분에 무엇이 포함되는지 명시합니다.
- **범위:** 기존 범위 안입니다.

### P8. H04/H05 귀속의 불일치

- **문제**
  - 제공된 근거(이전 R1 §0)는 H04를 source66/build53, H05를 별도 version1 recovery-only Host로 귀속합니다.
  - packet 안에서 source84와 결속된 관측은 H10뿐입니다. "source84에서 H04/H05/H10 관측"이라는 전제는 이 packet만으로 대조할 수 없습니다.
- **최소 조치 (기록)**
  - 최종 H01–H10 표는 source/build 단위로 표기합니다.
  - 이번 실행이 재관측하지 않은 항목은 "상속"으로 둡니다.
- **범위:** 기존 범위 안입니다.

---

## 4. 비차단 구현 확인

R1 packet이나 실행 증거로 확인할 항목입니다.

| # | 확인 항목 |
|---|---|
| I1 | **control 사본 독립성:** hardlink/alternates 없이 독립 `.git`을 구성하고, push 경로를 무효화합니다. reference-a-baseline-revision full hash를 확인합니다. 가져오는 dirty 파일은 manifest digest와, overnight-fix1의 3개 파일은 R1 `after_sha256`과 대조한 뒤 수정을 시작합니다. |
| I2 | **init 부작용:** 정식 init 전후로 다음의 digest가 같은지 확인합니다. 기존 설치본 view, 기존 authority, pending, followup(0/256). 전역·사용자 수준 설정에 쓰지 않는지도 확인합니다. |
| I3 | **allocation map:** 이전 R1에서 생략·미검토였던 Python 32–55 map을 R1 packet에 포함합니다(최소한 신규 version과 인접 항목). Python과 Rust의 `turn_cap`을 동일하게 등록하고, 미등록 거절을 유지합니다. 다음 상한을 합성 검사로 대조합니다: turn 17, gen 34, dispatch 1, authority-apply 1, recovery-apply 0. |
| I4 | **Rust 비-test 변경 시:** 실행 binary hash를 R1 source와 결속합니다(이전 검증은 test build뿐이었습니다). "694 무영향" 집합이 Rust 변경 후에도 유효한지 재평가합니다. |
| I5 | **새 home의 실제 volume:** `RENAME_EXCL` 지원과 umask/0600을 합성 검사로 사전 확인합니다(이전 R1 §6-3). |
| I6 | **replace-range 보존:** Backlog와 BriefIndex의 범위 밖 바이트가 불변인지 검증합니다. 오프셋 단위(byte인지 문자인지)와 UTF-8 경계도 확인합니다. |
| I7 | **봉인 후 쓰기 0:** 봉인 시점, 수락 직전, 수락 후의 worker tree digest를 대조합니다. |
| I8 | **전송 범위 증거:** provider에 실제 송신된 view 목록이 manifest 32개 digest와 같은지 확인합니다. 86,954 bytes가 근거 27개의 합계인지 32개 전체의 합계인지도 명시합니다. |
| I9 | **authority 보고:** 과거 2회와 신규 최대 1회를 분리해 보고합니다. policy의 누적/epoch 의미는 미확정 상태로 유지합니다. |
| I10 | **auth 만료 metadata:** 확인할 수 없으면 대기에 진입하지 않습니다(승인안대로). 이 판단도 기록합니다. |

---

## 5. 정적 추론과 Driver 실행의 구분

- **정적 추론 (Reviewer)**
  - §2의 일관성 판단
  - P1–P8과 I1–I10
  - turn/generation 산술
- **Driver 보고 (미재현)**
  - 승인안의 출발점 전체
  - 이전 R1에 인용된 테스트 결과
  - digest
  - build 시간, controller 시간
- **이번 계획이 아직 낳지 않은 것**
  - 새 바이트, 새 R1
  - exact intent/grant
  - 결과, ticket
  - 어떤 live 관측

---

## 6. 누락 입력과 검증 불가 주장

- 제공된 승인안 텍스트와 `plan_sha256`의 일치 여부, Owner 승인 원문
- manifest 키(Backlog 등)와 5개 쓰기 경로의 대응. 원 경로가 메타데이터에 없습니다.
- 86,954 bytes의 산정 대상, view 바이트의 실제 내용
- reference-a-baseline-revision, a58003fa, reference-a-result-revision의 full hash와 상태
- 최종 검토 입력 21개의 드리프트 0, 694 무영향 목록
- Core init의 실제 쓰기 범위, 새 home의 파일시스템 종류
- 실제 allocation 수치를 담은 소스, Rust runtime 전체
- auth 만료 상태, 모델·계정 가용성
- H04/H05의 source84 관측 근거(P8)

---

## 7. 한계

- 이 ACCEPT는 승인안이 범위와 계약 면에서 내부적으로 일관되고, material 변경 없이 단계 2–3에 진입할 수 있는지에 대한 **정적 판단**입니다.
- 다음은 판단 대상이 아닙니다.
  - 새 바이트의 정합성. 이는 fresh R1의 몫입니다.
  - 실제 실행의 성공
  - 내용 품질, 효율
  - Owner 수용
- P1–P8을 기록하지 않은 채 단계 2에 착수하면, 이 R0의 조건이 충족되지 않은 것으로 봐야 합니다.
~~~~


## H10 재검증 준비 중단 — Driver 실행기 오류와 준비2회 한도


상태: 실제 H10 재검증 미시작. 계획 R0는 ACCEPT(차단0)이지만 준비 실행기에서 Driver 오류2건이 발생하여 승인된 준비2회 한도에서 멈췄다. 이는 Core 결함이나 환경 권한 차단의 증거가 아니다.

## 완료와 미실행

- R0: Claude Pro/firstParty, claude-opus-5-5, tools/MCP0, 174.473초, 입력45,627bytes, 차단0.
- 새 control 프로젝트 사본 및 독립 Git 초기화 완료. 고정32개 입력 일치. 새 .hrn/launcher 없음, worker/index/commit 없음.
- 기존 primary authority·Git status, 기존 source3 파일 불변.
- Host/Rust 신규 allocation 변경·build·실행전R1·native 모델·intent apply·ordinary accept 모두 미실행.

## 원인과 정확한 보정안

1. 첫 실행은 승인된 release ID의 product-release- 접두사를 대조에서 빠뜨려 init preview 직후 멈췄다. 실제 release SHA는 승인본과 동일했다.
2. 두 번째 실행은 compact JSON을 init 입력으로 저장했다. Core는 indent=2의 canonical JSON을 요구하므로 HV2-JSON-NONCANONICAL, exit65로 거절했다. CLI는 입력을 읽는 단계에서 실패했으며 workspace_init_apply 호출 전이다. 실제 .hrn/launcher 부재도 확인했다.

제안은 같은 preview request를 Core canonical_json_bytes로 저장한 `init-request-canonical-proposed.json`를 한 번 적용해 이어가는 것이다. 데이터 객체와 confirm token은 동일하다. canonical parser로 로컬 대조했고 proposed runner는 구문 검사만 했으며 실행하지 않았다. Source/Core 변경·추가 reviewer·실제 모델 재시도·기한 연장은 없다.

- 제안 입력 SHA-256: 4371a4189115a85fe73646f2df4bcf3070d5ccfeb5433e50758fad12b090cf95
- 제안 실행기: `resume-control-proposed.py`
- 추가 승인 범위: 준비 실행1회 추가. 이 한 번이 실패하면 중단. 이후에는 기존 승인 작업과 두 Owner 확인을 유지.
- 예상 추가 비용: 정규 입력 적용 자체1–3분(판단치), 전체 잔여작업 약75–125분(기존 추정에서 R0/기초 준비 완료만 반영; 아직 미측정 구성 위험 존재).
- 지금까지 경과: 8.92분. 원 최종중단03:41:25Z/12:41:25KST는 유지되고 대기도 포함된다. 별도 연장 승인을 추정하지 않는다.

## 보존·정리

보존: 새 control 사본은 첫 Owner 확인 전 준비 재개 소비자가 있어 유지한다. 원32개 입력/승인안/기존 source·리뷰/이번 오류 입력·preview·canonical 제안과 R0 원문은 중단 판단 및 정확한 재개의 근거로 유지한다. 수용 또는 명시적 중단 후 재평가한다. 기존 활성 경로 변경0. 종료한 reviewer의 빈 scratch1개만 삭제했다. primary/worker/branch/기존 증거 삭제0.



## H10 추가 준비1회 승인과 정식 init 완료

Owner가 준비 실행1회 추가를 승인하고 기존 종료시각 및 두 확인 지점을 유지했다. 같은 preview의 canonical request로 init1회 실행: classification=initialized, replayed=false, a58003fa… 동일release. 실행기는 이후 view(텍스트)를 JSON으로 파싱하는 기록 오류로 exit1이었으나 init-result가 저장됐고 별도 읽기 전용 status에서 pass/primary/runtime_supported, intent0/Work0을 확인했다. 초기화 재실행0, 불명확한 authority 재전송0. 실패한 출력 변환을 성공으로 기록하지 않는다. 원 primary/authority/32입력 불변 검증 후 아직 실행되지 않았던 baseline staging을1회 수행했다. baseline commit·intent apply·worker·actual model은0. 다음은 승인된 신규 배정·관련 검사이며 원 deadline03:41:25Z 유지.


## H10 신규 allocation57 구현·집중검사 checkpoint

변경은 Host allocation57/인식 분기, Rust app-server 같은 배정/분기, 기존 Host cap 검사 파라미터3파일이다. 새home/Work, 기존stopped v56parent, 단일start/thread,17턴/34generation,content correction1,epoch authority1/누적최대3,recovery0,03:41:25Z 절대한도에 결속했다. Core는 변경하지 않았다. source-before3개와 build70 binary3개를 정확한 bytes로 복구 보존하고 신규build를 진행했다. Host107IDs normal/O 각각PASS(0error/failure/skip), build248.230초PASS, app-testcompile121.702초PASS, process groups 종료. 신규 actual allocation/spec admission은 아직 미실행이다. 전체694무영향 검사는 재실행하지 않았으며 Rust 변경 영향은 app runtime/admission 검증으로 별도 닫는다.

첫 Owner 확인용 intent draft9d306dd1…/ticketf9e3f24f…가 생성됐다. 기록 전 helper import 이름 오류는 local input 작업 전 발생했고 실제 설치본의 순수 graph validator로 입력을 확인한 뒤 최초draft/prepare1회만 실행했다. intent apply·baseline commit·worker·native model·ordinary accept는0. 실행 전 R1도 아직 미실행이며 source 전체승인으로 보지 않는다. 고정 owner instruction은 실제4219bytes SHA99ef7994…로 불변이고 원문15턴 지시는 새로운17턴hardcap보다 좁은 모델지시로 유지한다. 문서보정은hardcap1이 우선하며 원문2묶음은 권한을 늘리지 않는다.


# H10 실행 전 보정 한도 불일치와 중단

실제 모델은 시작하지 않았다. 새 배정57은 내용 보정1회를 선언하지만 Python/Rust journal validator의 실제 상한은2회다. 정적 코드와 allocation 값 대조로 확인했으며 실제 native counterexample을 실행한 결과는 아니다. 앞선 Host107개 normal/O 검사와 build/compile PASS는 이 새 조건의 검증을 포함하지 않았다.

## 최소 수정안

- source.patch: Python limits의 correction과 Rust 해당 match arm이 고정 allocation의 content_corrections를 사용하도록 변경한다. 과거26개 배정은 모두2이므로 이전 의미를 유지하고 새57만1로 제한한다. 실제 소스에는 적용하지 않았다.
- budget-cases.py: 16문서 턴+수락1턴, 첫 내용 보정 허용·별도 두 번째 보정 거절,18턴 거절을 포함한 제안 검사다. 구문 검사만 완료했으며 실제 journal 검증은 아직 미실행이다.
- 후속 실행: 최소 패치 적용, 관련 Host 검사, rebuild/app compile, Python normal/O와 Rust journal parity, 정확한 runtime/proxy admission, 최종 bytes 실행 전 R1. 기존 성공한 init 재실행과 추가 모델 시작 배정은 없다.

## 추가 승인 이유와 범위

승인안56행은 국소 준비 보정을 최대2회(첫 준비와 정정1회)로 제한했다. Owner의 canonical init 추가1회까지 준비 실행3/3을 사용했다. 이미 빌드한 후보의 한도 구현을 바꾸고 다시 검증하는 작업을 추가 보정 없이 진행 가능한 것으로 확대 해석하지 않는다. 이 최소 패치 및 관련 재검증을 위한 준비 보정1회 추가만 요청한다. 이번 보정 실패 시 또 재시도하지 않는다. 기존 두 Owner 확인, 모델1시작/17턴/34generation/내용 보정1회/수락1회, 리뷰 총3회는 유지한다.

이 한도 수정·재검증의 예상 추가 비용은10–20분이다(판단치; 직전 build248.2초, compile121.7초, Host 약1초/모드 근거; 새 journal 검사와 검토 시간은 불확실). 전체 잔여 작업은 약65–105분으로 추정하며 Owner 대기를 포함한 기존 누적180분 상한은 별개다. 작업 종료 예약은12:21:25KST, 최종 중단은12:41:25KST 그대로이고 대기 중에도 시간이 흐른다. 기록 시점 경과32.2분, 최종 중단까지147.8분이다.

## 확인과 보존

원 primary HEAD/status/authority 불변, 입력32개와 새 control 기준32개 일치, 빌드 소스 불변을 다시 확인했다. 새 baseline commit0, worker 부재, 새epoch 부재, 모델 시작0, 수락0이다. init은 이미 성공했고 intent draft/ticket은 준비 상태다. 새 control, 소스 복구3개, 직전 바이너리3개, 입력·검사·리뷰·패치를 Owner 판단과 이어가기용으로 보존한다. 활성 경로 변경0, 삭제0. 수용 또는 명시적 중단 후 정리 조건을 다시 평가한다.


## H10 추가 보정 source87 및 실행 전 R1 진행

Owner의 내용 보정 한도 수정·관련 재검증1회 추가 승인으로 준비4/4를 사용했다. Python/Rust validator가 고정 cfg.content_corrections를 읽으며 과거26개 배정2회는 보존하고 새57만1회로 제한한다. 실제 journal reserve 검사2개를 추가해 Host109 normal/O 각각PASS, 수정 build176.918초PASS, app test compile22.002초PASS. 정확한 새 runtime/proxy admission은 첫 Owner 확인 후 모델·인증 시작 전에 수행해야 하며 아직 성공 근거가 아니다.

새 helper 입력 점검의 출처 JSON/원문 경로 혼동과 기존 ledger에 exclusive-create 저장 API를 사용한 오류2건을 별도 보존했다. 둘 다 실제 model/Core/epoch 호출 전이며 원문 bytes는 불변이다. 원래 실패 wrapper를 성공으로 바꾸지 않고 아직 미실행된 helper 경로를 수정했다. 후속 의존·idle 경계4개 확인PASS, helper점검3프로세스를 추가 offline carry에 포함한다. 초기화·실제 모델·authority 재시도0이다. 아직 실행되지 않은 새 저장소 보존 ref는 설치 Core가 허용하는 refs/heads 형식을 사용한다.

R1 패킷663327bytes(누적708954bytes), source87/새helper 입력50개를 고정했다. 최초 자동 승인 검토가 private 실험코드의 외부 Claude 전송에 대한 구체적 승인 불명확으로 실행 전 거절했다. 승인안55행의 Pro/firstParty·실험코드/diff·1MiB/3MiB 조항, 원 계획SHA 및00:41:24Z 실제 Owner승인을 대조한 뒤 동일 명령/목적지/패킷을 다시 심사받아 허용됐다. 거절 건의 프로세스·전송0이며 현재 두 번째 리뷰만 실행중이다. 실제 Claude Opus5.5, Pro/firstParty, tools/MCP0 확인. 별도동의나권한우회로기록하지않는다.

정리: 종료와 task소유를 다시 확인한 빈 offline home/tmp/fixture 및 테스트 socket 경로 26개만 삭제했다. 소스·입력·결과·리뷰·기준 binary 복구본은 Owner 판단 및 정확한 이어가기 소비자가 있어 유지한다. 활성 경로 변경0. 첫 Owner 확인 문서와 설치본 intent/confirmation view를 준비했지만 아직 승인을 요청하거나 적용하지 않았다.


# H10 R1 중단과 최소 보정 제안

실행 전 리뷰는 BLOCKED(차단1/비차단9)다. 실제 모델·proxy·epoch·baseline commit·intent apply·수락은 아직0이다. 기존 Core init과 intent draft만 준비되어 있다.

B1을 승인된 control 스냅샷32개로 효과 없이 계산해 확인했다. helper가 지정 view 객체만 hash하는 반면 Host는 initial_state 및 prefix/suffix SHA가 포함된 view_contracts를 hash한다. 두 SHA가 다르다. 이것은 실행된 오프라인 비교이며 실제 runtime 실패를 재현했다고 주장하지 않는다.

helper.patch는 documents.py와 preflight.py 두 파일만 변경하는 제안이다. policy에서 Host와 동일한 full view_contracts로 identity를 만들고 host spec에서 다시 대조한다. 실제 native 시작 예약 이전에 full scope,worker/verifier profile,새home/Work 결속도 검사한다. Host/Rust/Core와 바이너리는 변경하지 않으므로 rebuild와109개 전체 반복은 불필요하다. 제안 구문만 확인했으며 적용하지 않았다.

추가로 필요한 승인: helper 준비 보정1회, 남은 리뷰1회를 실행 전 재검토로 사용, 최종 결과 검토1회 추가(총 리뷰4회). 회당1MiB·합계3MiB,Pro/firstParty·tools/MCP0 및 기존03:41:25Z/12:41:25KST 종료시각은 유지한다. 새 native1시작과 두 Owner 확인도 유지한다. 외부 전송한계나 모델 재시도를 늘리는 요청은 아니다. 보정·집중 검사·재검토 예상10–20분, 이후 setup/실제실행/Owner대기/최종검토 예상35–60분(판단치, 실패·지연 불확실). 남은 시간에 모두 들어가지 않으면 정해진 시각에 중단한다.

추가 동의 전에는 패치를 적용하거나 재검토·실제 실행을 시작하지 않는다. N1~N9는 다음 패킷의 명시적 한계/확인 항목으로 유지한다. 정확한 runtime/proxy admission은 여전히 미실행이며 PASS를 선행조건으로 둔다. semantic claims는 불변이나 path/inode를 포함한 binding oracle은 새 대상에 재결속된다고 표현한다.

보존: 기존 입력·소스·복구 binary·review 원문·패치·반증은 Owner 판단과 정확한 재개의 소비자가 있어 유지한다. 활성 경로 변경0. 종료한 R1의 빈 scratch만 삭제했다. 앞서 삭제한26개 빈 검사 경로와 구분한다.


## R1 Reviewer 원문 — Claude Opus 5.5

````markdown
# R1 정적 검토 결과: source87 / allocation57 실행 전

## 판정: **BLOCKED**

- **차단 1건, 비차단 9건**입니다.
- 이번 판정은 제공된 패킷만 정적으로 읽고 내린 추론입니다. 실제 모델 성공, Owner 수용, 생산 적격성, 실행 권한을 뜻하지 않습니다.
- source87의 실제 실행 횟수는 여전히 0회입니다. source84의 H04/H05/H10 성공은 역사적 근거일 뿐 이번 실행의 증거가 아닙니다.
- 정확한 runtime/proxy admission(Python budget cases normal/O, Rust app admission, proxy preface)은 아직 실행되지 않았습니다. 이 admission이 모델 인증과 프로세스 시작 전에 통과해야 한다는 조건은 그대로 유지합니다.

---

## 1. 차단 항목

### B1. 승인 scope identity가 Host `DocumentController`와 일치하지 않음

**결과:** 실제 launch에서 거절되고, native 시도 1회가 소모됩니다.

**근거 (정적 추론):**

- **helper 쪽 (`documents.py prepare_policy`)**
  - `views={key: v['view'] ...}`로 범위 객체만 사용합니다.
  - `scope_identity = digest(wire_bytes({'paths','outputs','views'}))`로 계산합니다.
  - 이 값이 `native-document-policy.json`, runtime spec의 `document_policy`, host spec의 `identity.scope_identity`로 들어갑니다.
- **Host 쪽 (`host.py` 2322-2327)**
  - contract v2에서는 `scope["views"] = spec["view_contracts"]`를 사용합니다.
  - `host_spec()`은 `view_contracts = h.initial_view_contracts(files)`로 채웁니다.
  - 각 항목은 `{"view", "initial_state"}`이고, replace-range이면 `prefix_sha256`와 `suffix_sha256`가 추가됩니다.
  - 따라서 helper의 `{key: view}`와 다른 객체이고, digest도 달라집니다.
- **거절 지점:** `LiveSession.launch` 2957행 `require(self.documents.scope_sha256 == self.spec["identity"]["scope_identity"], "approved scope drift")`.
- **preflight가 잡지 못하는 이유:**
  - `preflight.qualify`는 `h.LiveSession(...)`의 `__init__`만 호출합니다. `launch()`의 DocumentController와 scope 검사는 실행하지 않습니다.
  - 두 정책 값을 서로 비교만 하므로, 둘 다 같은 잘못된 값이어서 통과합니다.
- **실제 영향 순서 (`run-actual.py`):**
  1. proxy-start 예약
  2. 로컬 admission 3프로세스 통과
  3. `native_starts_used=1` 예약
  4. proxy launch
  5. `run_live_command` → `launch()` → 위 검사에서 refused, stop

  모델 인증이나 runtime 시작 전에 멈추므로 보안 위반은 아닙니다. 그러나 승인된 단 1회의 native/proxy 시도가 결과 없이 소모됩니다. 원 승인 한도상 재시도 권한도 없습니다.
- **반증 방법:** Driver가 효과 없이 두 digest를 오프라인으로 계산해 같다는 것을 보이면 B1은 해소됩니다. 현재 패킷에는 그런 근거가 없습니다.

**최소 보정 계획 (Owner 결정 필요, 자동 수행 금지):**

1. `documents.py`에서 파일 record와 `initial_view_contracts(files)`를 policy 단계에서 먼저 계산합니다.
2. `scope_identity = digest(wire_bytes({'paths', 'outputs', 'views': view_contracts}))`로 Host와 같은 구조를 사용합니다.
3. `host_spec()`에서도 같은 값을 다시 계산하고 `need(...)`로 확인합니다.
4. `preflight.qualify`에 효과 없는 사전 검사를 추가합니다. 위치는 `native_starts_used` 예약 이전이며, 다음을 확인합니다.
   - Host 구조로 계산한 scope digest와 `identity.scope_identity`의 일치
   - `launch_contract.roles.worker/verifier`와 `documents.profile_template/sha256`의 일치
   - `identity.{home, work}`와 `replacement_work`의 일치

   이 셋은 `launch()`에서만 검사되는 항목입니다.
5. `host.py`와 Rust는 바꾸지 않습니다. 이 변경은 helper 2개(`documents.py`, `preflight.py`)에만 해당합니다.
   - 따라서 `prelive-freeze.json` 재동결과 Owner의 재승인이 필요합니다.
   - 추가 리뷰 횟수는 Owner가 결정합니다. 현재 남은 외부 리뷰는 결과 검토용 1회뿐입니다.
6. 모델, authority, epoch는 소비되지 않습니다. 보정 작업 자체는 offline/correction count로 기록해야 하며, 환불하지 않습니다.

---

## 2. 비차단 항목

| # | 내용 | 권고 |
|---|---|---|
| N1 | **Rust H10 start 재매핑 누락.** v49–51, 52, 53, 55는 이전 epoch의 `h10-01`을 `epochNN:` 접두로 옮깁니다. v57은 v56의 `h10-01`을 그대로 둔 채 같은 키로 덮어씁니다. parent_starts=42 검사는 통과한다고 계산됩니다. 다만 이후 `state.starts` 사용처는 패킷에 없어 확인할 수 없습니다. | 의무 Rust admission이 실패하면 그 자체로 차단입니다. 차기 epoch를 대비해 `57 => epoch56:` 재매핑을 검토하십시오. |
| N2 | **`source-correction` 음성 case의 판별력 상실.** cap이 1이어서 기존 correction 1회 뒤에 오는 이 case는 class 검사가 아니라 cap에서 거절됩니다. | correction이 없는 base에서 class=`source`가 거절되는 case를 추가하십시오. |
| N3 | **모델이 보는 턴 수 불일치.** Owner 원문은 15턴인데 trusted state의 `remaining_turns`는 17부터 시작합니다. 권한을 넓히지는 않지만 모델이 혼동할 수 있습니다. | 결과 보고서에 명시하십시오. |
| N4 | **Owner idle 10분 창이 빠듯함.** 그 안에 review-sealed, Owner checkpoint 2 결정, commit/publish/prepare, deliver가 모두 끝나야 합니다. 정적 계산으로는 runtime 만료 상한이 약 03:07:07Z(run_deadline − 34분18초 reserve)입니다. 따라서 seal은 약 02:42Z 이전, native 시작은 약 02:23Z 이전이어야 합니다. | 운영 위험입니다. 첫 checkpoint 화면에 이 제약을 명시하십시오. |
| N5 | **carry 하한을 확인할 수 없음.** `accounting-basis.json`의 `old_carry_floor_ms`와 execution의 `extra_offline_checks` 값이 패킷에 없습니다. run_deadline 03:41:25Z는 validator가 강제하는 것을 확인했지만, 사용량을 환불하지 않는다는 점(carry ≥ 이전 사용량)은 검증할 수 없습니다. | — |
| N6 | **oracle 표현.** semantic claims digest는 보존됩니다. 그러나 `oracle_sha256`에는 `link_metadata`(inode/mtime/경로)가 포함되므로 새 값이 됩니다. | "oracle bytes 불변"이 아니라 "semantic claims 불변, binding oracle은 재결속"으로 표기하십시오. |
| N7 | **owner-decision 형식.** publish helper가 만드는 `owner-decision.json`은 직접 Owner 결정과 같은 형식입니다. 구분 근거는 `decision-provenance.json`뿐입니다. | 결과 보고에서 이것이 조건부 파생 결정임을 유지하십시오. |
| N8 | **proxy test binary 재사용의 영향 범위.** attempt18의 proxy test binary를 v57에 재사용하는데, `prepared_fd` 테스트의 버전 처리가 패킷에 없습니다. | 미실행 상태입니다. preface가 실패하면 차단으로 처리하십시오. |
| N9 | **링크 metadata 경로 미확인.** `documents.host_spec`은 모든 이전 link metadata 경로가 old worker 아래에 있다고 가정합니다(`relative_to`). 또 하드코딩된 `docs/briefs/...` document_ref 경로는 확인할 수 없습니다. | — |

---

## 3. 정적으로 정합성을 확인한 항목 (실행 아님)

- **allocation57 일치:** Python, Rust, `allocation-corrected-input.json`의 allocation57 문자열이 같습니다(source 87, build 72, correction 89, offline-start 222, review 7, total_cap 193097229, run_deadline 03:41:25Z).
- **content correction cap:** Python `limits['correction']`과 Rust `match`가 모두 `cfg.content_corrections`를 사용합니다. 과거 26개 allocation은 2, v57은 1입니다.
- **턴과 전송 예산:**
  - 17턴, 34 generation, worker-result 16, `iterate`의 `left>1`로 편집 16 + accept 1이 됩니다.
  - 전송 상한 4+2×17=38이며, 필요한 양은 36(control 2 + generation 34)입니다.
  - proxy_total 44 = 43 + 1입니다.
- **idle 시간 조건:** strict idle 함수가 auth 30분, runtime/proxy 25분, hard-stop 25분, 최대 10분을 강제하며 global patch로 적용됩니다.
- **실행 순서 가드:** checkpoint 1/2의 exact binding, `native_starts_used` 사전 예약, `authority_apply_used==0` 확인 순서가 맞습니다.

---

## 4. 근거의 출처 구분

**Driver 실행 근거 (자가 보고, 원본 미열람):**

- Host 109개 테스트 normal/O PASS
- build 176.918초, app test compile 22.002초 PASS
- 입력 점검 오류 2건과 후속 PASS
- 32개 입력 SHA 일치

**미관측:**

- runtime instance, epoch, Owner 결정, 정확한 admission 3종
- Rust runtime parity (compile만 확인)

**누락 입력:**

- `materialize-roles.py` 본문
- `accounting-basis.json`, `execution.json`, `input-manifest.json`, attempt28 spec 본문
- Rust `qualified_proxy_transport`, `prepared_fd.rs` 본문
- 514-file tree, 첫 checkpoint 화면

**한계:**

- 변경되지 않은 Rust 제품 전체는 검토하지 않았습니다.
- redacted 텍스트로 digest 일치를 주장하지 않습니다.
- trusted native runtime을 OS 격리나 request-body privacy 보장으로 확대하지 않습니다.
- 품질, Owner 부담, 일반 생산성은 미측정 상태로 남습니다.
````

Driver disposition: B1 수용. 승인된 스냅샷의 두 scope digest 불일치를 오프라인 실행으로 확인했다. N1–N9는 비차단 한계로 유지하고 Owner 미결정 상태다. 실제 실행과 추가 보정은 중단. 리뷰 프로세스 종료·입력 드리프트0·tools/MCP0 확인.


## H10 Scope Binding Correction And R1 Re-review — 2026-10-26

Owner가 준비 보정1회와 독립 리뷰1회 추가를 명시 승인했다. 기존 deadline/two Owner gates/native1/전송한도는 유지했다. 제시된 documents/preflight 패치를 적용하고 추가 승인 횟수에 필요한 common/contract/review runner 숫자 결속만 반영했다. 제품 source87·Host/Rust/Core·binaries는 변경하지 않았다. 최초 apply wrapper는 구문 파싱 오류로 효과0이었고 기록 후 구문 보정하여 한 번 적용했다.

집중 검사: 실제 승인 control32개로 policy 함수 계산과 Host 구조 일치; 수정 preflight AST7case PASS; metadata35개 경로와 필요한 SHA 일치. 실제 worker/spec/admission은 아직0이며 control 경로 검사를 실제 runtime 성공으로 해석하지 않는다. 이전 source87 Host109 normal/O 및 빌드를 재사용한다. Git diff --check 통과. freeze50개 실제 SHA를 대조하고 이전 freeze를 보존했다.

Review: claude-opus-5-5 / session 538362af-9c51-40d9-80bb-84705d56aaf8 / request SHA f04f73e0f57376a8ccf49853d00cf322a6481cb996b77b7d0aa998a630ae3d36 / response SHA 338370f40169f3083758a1dbc9dbe446300f1046dbee9993034812a31943e518 / elapsed 183.733초 / exit0 / tools0 MCP0 / process group absent / drift0. 세 번째 호출이며 누적1,514,837바이트(3MiB 한도), 4번째 최종 결과 리뷰만 남는다.

### Reviewer Response Verbatim

````markdown
# R1 재검토 (3/4회): source87 / allocation57 — 승인 scope 결속 보정

## 판정: **ACCEPT-pre-live** — 차단 0건, 비차단 7건

- 이 판정은 제공된 패킷만 정적으로 읽고 내린 추론입니다. 실제 모델 성공, Owner 수용, 생산 적격성, 실행 권한을 뜻하지 않습니다.
- source87의 실제 실행은 0회입니다. 모델·authority·baseline commit·worker도 모두 0입니다. source84의 H04/H05/H10 성공은 역사적 근거일 뿐입니다.
- **유지되는 조건**
  - 정확한 runtime/proxy admission 세 가지(Python budget cases normal/O, Rust app admission, proxy preface)는 아직 실행되지 않았습니다.
  - 세 가지 모두 모델 인증과 native 프로세스 시작 전에 통과해야 합니다.
  - 하나라도 실패하면 실제 모델로 넘어가지 않습니다.
- appendix의 BLOCKED 원문은 역사적 findings로만 취급했습니다. 아래 판단은 현재 보정본 기준입니다.

---

## 1. B1 해소 판단 (정적 추론)

**결론: 해소된 것으로 판단합니다.** helper가 만드는 `scope_identity`와 Host `DocumentController.scope_sha256`이 같은 객체 구조에서 계산됩니다.

| 구성 요소 | helper `prepare_policy` (보정 후) | Host `DocumentController` (2322–2327) | 일치 여부 |
|---|---|---|---|
| `paths` | `str(c.W/project_path)` | `self.files[key]["path"]`. 이 값은 `host_spec`의 `file_record(c.W/...)`가 돌려준 `str(path)`입니다 | 일치. `file_record`가 `resolve(strict=True)==path`를 요구하므로 문자열이 같습니다 |
| `outputs` | `old['documents']['outputs']` | `spec["outputs"]`. 같은 `old` 복사본입니다 | 일치 |
| `views` | `initial_view_contracts(records)` | `spec["view_contracts"]`. 이 값은 `host_spec`의 `initial_view_contracts(files)`입니다 | 같은 함수, 같은 worker bytes |

**추가로 확인한 점**
- view contract에는 inode나 identity가 들어가지 않습니다. 들어가는 것은 view, `initial_state`, prefix/suffix SHA뿐입니다.
- 따라서 policy 생성 시점과 `host_spec` 시점 사이에 파일 bytes가 같으면 digest도 같습니다.
- `host_spec`은 `views==contract['view_contracts']`를 확인하고 scope를 재계산해 다시 확인합니다. 이 두 검사가 drift를 차단합니다.
- `check_files`의 v2 계약도 맞습니다.
  - replace-range 항목: `{view, initial_state, prefix_sha256, suffix_sha256}`
  - 그 외 항목: `{view, initial_state}`
  - `initial_view_contracts`의 출력과 정확히 같은 형태입니다.

**preflight 보강으로 `launch()` 전용 검사 세 가지를 `native_starts_used` 예약 전에 확인합니다.**
1. scope digest와 `identity.scope_identity`의 일치
2. worker/verifier role과 `profile_template`의 일치
3. `home`/`work`와 `replacement_work`의 일치

**기존 근거로 충분하다고 본 나머지 `launch()` 검사**
- `DocumentController.__init__`의 `safe_text`와 `pack_reads`는 preflight에 없습니다.
- 다만 같은 bytes와 같은 `allowed_identifiers`로 attempt28에서 통과한 이력이 있습니다.

**신규 코드의 정적 결함은 찾지 못했습니다.**
- `preflight`의 `cfg`, `read`, `m.CONTRACT`가 모두 정의되어 있습니다.
- 변수 충돌도 없습니다.

**근거의 출처 구분**
- 아래는 Driver 실행 근거입니다. 원본을 열람하지 않은 자가 보고입니다.
  - `focused-result.json`의 `host_formula_matches: true`
  - 32개 실제 control 파일로 실행한 policy 함수
  - AST 7개 case 통과
- 이 검사는 control 경로 기준입니다. 실제 worker 경로 기준 결속은 아직 실행되지 않았고, 첫 Owner gate 이후 실행 시점의 검사가 필수입니다.

---

## 2. 승인 횟수와 accounting 변경 확인 (정적)

- `common.guard`의 조건 `local_preparation_cycles_used==5`는 장부 값 5와 맞습니다.
- `contract.packet`의 조건 `review_calls_used==3`
  - 장부 값은 2이고, 이번 round 3에서 `run-review`가 3으로 올립니다. 이 조건은 이번 R1 재검토의 수락을 전제로 합니다.
  - 4번째 리뷰는 epoch 생성 이후이므로 이 조건과 충돌하지 않습니다.
- attempt 계산은 다음과 같습니다.
  - offline: 222 + 6 + 3 = 231
  - review: 7 + 2 = 9
  - correction: 89 + 1 = 90
  - 세 값 모두 validator의 `[cfg, cfg+64]` 범위 안에 있습니다.
  - proxy-start는 43으로 그대로이고, 이 값은 Python/Rust의 "unrecorded proxy" 검사와 맞습니다.
  - 모든 항목이 부모 counts 이상이므로 환불은 없습니다.
- `run-review`의 `review_calls_limit==4`, `used<4`, `used==round-1` 조건은 장부 값과 맞습니다.
- 제품 Host/Rust의 SHA는 `current_product_sources_unchanged`와 freeze에서 같습니다. 이번 보정은 helper에만 해당합니다.
- `accounting-basis`의 `old_carry_floor_ms=176128668`이 이번에 제공되어 이전 N5는 부분 해소되었습니다.
  - carry = floor + 경과 시간이므로 환불 방향의 오류는 정적으로 보이지 않습니다.
  - 다만 floor 값 자체가 v56 사용량 이상인지는 v56 anchor/journal 원문이 없어 확인할 수 없습니다.

---

## 3. 비차단 항목

### R3-N1. 시간 창: 가장 큰 운영 위험 (정적 계산)

**계산**
- `run-actual`은 `expiry = run_deadline − 34분18초`, 즉 약 **03:07:07Z**를 상한으로 씁니다.
- `expiry − now ≥ 2,600,000ms`를 요구하므로 **`activate_epoch` 이후 시각이 약 02:23:47Z 이전이어야 합니다.**
- seal 시점에는 strict idle 조건(runtime/proxy 25분)이 붙으므로 **seal은 약 02:42Z 이전**이어야 합니다.
- 이 20분 안에서 다음 작업이 모두 시간을 씁니다.
  - 로컬 admission 3개 프로세스(최대 120 + 180 + 180초)
  - materialization
  - 편집 턴. 최소 read 약 4회, write 5회, verify 3회입니다.
- 실제로 편집에 쓸 수 있는 시간은 약 12–15분으로 추정됩니다.

**fail-closed 경로의 문제**
- 이 시간 검사는 `prepare_contract`와 `activate_epoch` **뒤에** 있습니다.
- 늦으면 epoch는 genesis 후 stop으로 끝나 소모되고, 재시도 권한은 없습니다.
- seal 시점 검사에서 실패하면 모델 턴은 이미 소비된 뒤 결과 없이 중단됩니다.

**권고** (코드 변경 없이, 효과 없는 판단으로 충분합니다)
- Driver는 `run-actual`을 시작하기 전에 현재 시각이 위 cutoff보다 충분히 이른지 판단하고, 늦으면 실행하지 않습니다.
- 첫 Owner 화면에 cutoff 시각을 명시합니다.

### R3-N2. 신규 실패 지점: proxy-start 예약 이후

`run-actual`에서 `docs.prepare_policy`는 `materialize_proxy`가 proxy-start를 예약한 **다음**에 호출됩니다. 보정으로 그 안에 새 실패 가능 지점이 두 가지 생겼습니다.
- `file_record`와 SHA 비교
- `native-document-policy.json` / `document-admission-contract.json`의 O_EXCL 생성

proxy는 launch되지 않으므로 외부 효과는 없습니다. 그러나 epoch의 proxy-start 1회가 소모됩니다.

**권고:** 실행 전에 두 파일이 존재하지 않는지 확인합니다. 읽기 전용 확인이더라도 프로세스를 띄운다면 offline count에 반영합니다.

### R3-N3. 최종 리뷰의 accounting

- epoch의 `prior_attempts.review=9`는 activation 시점에 고정됩니다. U2 journal은 `review` kind를 허용하지 않습니다.
- 따라서 4/4 결과 리뷰는 epoch에 기록될 수 없고, 장부와 보고서에만 남습니다.
- `run-review`의 `left>920s` 조건 때문에 round 4는 **03:06:05Z 이전**에 시작해야 합니다.

### R3-N4. Rust runtime의 document_policy 처리는 검증할 수 없음

- runtime spec의 `document_policy.scope_identity`를 Rust core가 재계산하거나 비교하는지는 이 패킷에 원문이 없습니다.
- Rust app admission test도 이 경로를 실행하지 않습니다.
- 이전 실제 성공에서 Host 공식으로 통과했다면 호환된다고 추정할 수 있지만, 이는 추론입니다.

### R3-N5. N1 보완: 상속된 start key와 proxy 선문(preface)

- **Rust start key**
  - v57은 상속받은 `state.starts["h10-01"]="h10"`을 그대로 둡니다.
  - 4803행의 runtime lookup은 v57의 start 예약 전에도 이 상속 key로 통과할 수 있습니다.
  - 다만 각 row 검증이 epoch-local `slots`를 요구하므로 권한을 부여하지는 않습니다. 한계로 유지합니다.
- **proxy preface**
  - `bind_stream`은 s6에서 `h10-02`도 받아들이고, actual preface test의 `valid-resume` case도 이를 정상으로 기대합니다.
  - v57이 허용하는 start는 `h10-01` 하나입니다. 따라서 `h10-02` 차단은 journal과 Host에만 의존하며, proxy 계층에서는 이중 방어가 없습니다.

### R3-N6. 누적 count 표기

- Python/Rust 모두 v41 이상에서 `correction-source=cfg.source` 값 87을 씁니다.
- 반면 `correction` 누적은 90입니다.
- 둘은 정합하지만 보고서에서 "source 보정 87 ≠ correction 시도 90"이라는 차이를 설명해야 합니다.

### R3-N7. 기존 항목의 유지

- **N2:** `source-correction` case는 class 판별 증거로 쓰지 않습니다.
- **N3:** 원문 15턴과 운영 상한 17턴의 차이를 명시합니다.
- **N6:** semantic claims는 불변이고 binding oracle은 재결속됩니다.
- **N7:** owner-decision은 조건부 파생 결정이며 provenance를 보존합니다.
- **N8:** 정적으로 읽기에 proxy preface test는 v57 packet(s6, `allocated_start=None`)에서 통과할 구조입니다. 다만 아직 미실행입니다.
- **N9:** `document_refs`의 `docs/briefs/adopter-old-work.md`가 manifest의 Narrative 경로와 같으므로 이 항목은 해소되었습니다.

---

## 4. 확인할 수 없는 주장과 누락 입력

**내용이 제공되지 않은 파일**
- `application-result.json`, `applied-correction.diff`, `check-focused.py`, `apply-approved.py`는 SHA만 있고 본문이 없습니다.
- 그래서 다음 주장은 검증할 수 없습니다.
  - "구문 오류는 효과 0"
  - "수정된 wrapper가 승인 패치를 한 번 적용"
- `prelive-freeze.json` 본문도 없어, 이번 helper SHA가 freeze에 반영되었는지는 freeze 목록의 SHA를 신뢰하는 수준에서만 판단했습니다.

**실행 시점에만 생기는 대상 (아직 관측 불가)**
- worker 경로 기준의 scope digest와 link metadata 결속
- epoch 인스턴스
- 정확한 admission 3종
- Owner 결정 두 건

**검토하지 않은 범위**
- 변경되지 않은 Rust 제품 전체와 core `prepared.rs`는 다시 전수 검토하지 않았습니다.
- redacted 텍스트로 digest 일치를 주장하지 않습니다.

**확대하지 않는 해석**
- trusted native runtime을 OS 전체 격리나 request-body privacy 보장으로 확대하지 않습니다.
- 품질, Owner 부담, 일반 생산성은 미측정 상태로 남습니다.
````

### Driver Disposition

B1 해소 수용. 비차단7개는 실제 실행 전 시간·경로 부재 확인, 정확한 admission 강제, 최종 계수/한계 보고로 처리하며 추가 source 수정은 하지 않는다. N4의 runtime 직접 정책 검증과 향후 epoch 지원은 미검증으로 남긴다. Reviewer가 누락으로 기재한 일부 diff/freeze 정보는 패킷에 있었으나 wrapper 원문은 제공하지 않았으므로 wrapper 효과0 주장은 Driver 실행/구문 오류 기록에 한정한다. Review 판정은 Owner 승인이나 실제 성공이 아니다.

현재 첫 Owner 확인 대기: private-evidence/E155 baseline commit0/intent apply0/newworker0/epoch0/native0/authority0. 추가 독립 검사 process1을 포함해 extra offline7, activation시 예상232. 현재 원본·helper·review·baseline recovery는 Owner 판단/정확한 재개에 필요해 유지한다. 종료한 round3의 빈 scratch1개만 제거했고 활성 경로 변경0. Task Work Done/STATUS/commit/push는 수행하지 않았다. [공개용 중립화]


## H10 First Checkpoint Execution And Sealed Result — 2026-10-26

Owner messageprivate-approval/O017가 exact baseline/intent/grant/worker/native1과 writer quiescence를 승인했다. 시간 여유443초를 확인하고 기준 commitreference-a-regression-baseline-revision(treereference-a-regression-tree,514files,Codex trailer)를 만들었다. intent apply와 work start는 성공했고 기존 primary 불변을 확인했다. [공개용 중립화]

정확한 admission: Python31budget cases/optimized parity PASS, Rust app1 PASS26.393초, reused proxy preface1 PASS1.416초. 이후 actual native1/thread1/proxy1을 시작했다. 현재12turn/24generation,출력5저장,3verifier PASS,content correction0,authority0,recovery0으로 봉인했다. 봉인 결과 reference-a-regression-intermediate-revision. Driver exact 비교에서 네 출력 bytes 불변, BriefIndex의 table를 끊던 빈 줄1개 제거,기존26행4열 GFM continuity와고정이전성공결과 일치를 확인했다. 결과 commit과수락은 아직0이다. [공개용 중립화]

두 번째 Owner 자료 private-evidence/E156 idle deadline 2026-10-26T11:34:14.698000+09:00. 원래 세션은 소비 중이므로 종료/retarget/cleanup하지 않는다. 필요한 output review copies,worker/control,baseline/recovery evidence를 두 번째 판단과 최종 검증까지 보존한다. 최종12:41:25KST 한도와원본/외부publish경계는유지한다. [공개용 중립화]


## H10 Final Actual Regression And Independent Review — 2026-10-26

Owner private-approval/O012의두번째확인으로봉인결과commit reference-a-regression-result-revision와Core게시,조건부exactticket을원래thread에전달했다. 현재epoch start/thread/proxy1,turn13,generation26,contentcorrection0,authority1,recovery0. Corecompleted/decision1/pending0,봉인전후result동일,프로세스종료·원primary HEAD/status/authority동일을확인했다. 새control에는index1변경과Coreintent/work미추적15개가남고worker는clean이다. 이를삭제/임의commit하지않았다. [공개용 중립화]

최종 리뷰 claude-opus-5-5 / c57bfe96-8f7b-479e-89eb-7ff20716b8f5 / 193.075초 / tools0,MCP0,exit0,drift0,groupabsent. RequestSHA dc7ad0ca9c1da1941d979e6758b72ea1ed9a91b76c5651d91974e461432a36ed,responseSHA 089a20d3d191b92116f42a43987897bba2fc47203360995d3c21288f03575786. 총4/4호출,전송1,711,220바이트/3MiB. Reviewer정적판단은ACTUALregression정합성범위이며원문품질/Owner부담/전체qualification수용이아니다.

### Reviewer Response Verbatim

````markdown
**ACCEPT-regression**: 차단 0건, 비차단 9건과 기존 한계 유지

- 이 판정은 제공된 정적 패킷 안의 증거가 서로 맞는지에 대한 Reviewer의 정적 추론입니다.
- Owner의 전체 수락, 원문 품질 수락, 제품 생산 적격성, 일반 생산성, 추가 실행 권한을 뜻하지 않습니다.
- 실제 문서 본문, Owner 원문 대화, 자격증명은 받지 않았습니다. 원문 품질은 검토하지 않았습니다.
- 경로와 대상명이 비식별 치환되어 있으므로, 아래 해시 대조는 패킷에 적힌 값끼리의 일치만 뜻합니다. redacted 텍스트 자체의 해시 일치는 주장하지 않습니다.

---

## 0. 근거 구분

| 구분 | 내용 |
|---|---|
| **Driver 실제 실행 근거** (자가 보고, 원본 미열람) | candidate-admission `passed`(31 cases, 로컬 프로세스 3개), native 1회, result/postcheck JSON, journal projection, RPC 메타데이터, commit-completion, sealed/acceptance 메타데이터 |
| **Reviewer 정적 추론** | 아래 §1의 계수·시각·해시 교차 대조와 helper 코드 경로 분석 |
| **Owner 판단** (Driver가 기록한 메타데이터) | checkpoint-1: intent/baseline/model 승인, writer quiescence. checkpoint-2: 고정 결과의 commit·publish와 파생 ticket accept 1회 조건부 승인. `quality_and_burden={fixed_regression_result: accepted, original_content_quality: unmeasured, active_minutes: null}`. Owner 메시지 원문은 받지 않았습니다. |

source87 실행 근거는 이번 패킷의 Driver 보고뿐입니다. source84의 H04/H05/H10 성공은 역사적 근거로만 취급했습니다.

---

## 1. 정적 교차 대조 결과

### 1.1 Journal 계수 (projection seq 0–103 직접 집계)

- **편집 구간:** seq 8–91은 `input → turn → generation → dispatch → host-dispatch → worker-result → generation` 7행 묶음이 12회 반복됩니다.
  - turn 12, generation 24, dispatch·host-dispatch·worker-result 각 12입니다.
  - 32개 파일을 8개씩 읽으면 read 4이고, write 5와 verify 3을 더하면 12회로 주장과 맞습니다.
- **수락 구간:** seq 92–103은 다음 순서입니다.
  - seal → pause → resume → input → turn(13번째) → generation → dispatch → host-dispatch → authority-apply → generation(26번째) → process-ended → stop
- **집계 합계:** `counts_current_epoch`와 완전히 일치합니다.
  - turn 13, generation 26, dispatch 13, worker-result 12, authority-apply 1, correction 없음
  - start, thread, proxy-start, runtime-entered는 각 1
- **RPC 이벤트와의 정합:**
  - `item/tool/call 13`은 worker 12와 accept 1의 합입니다.
  - `turn/started`와 `turn/completed`는 각 13입니다.
  - `thread/tokenUsage/updated 26`은 generation 26과 같습니다.
- **상한 대비:** turn 13 ≤ 운영 상한 17, generation 26 ≤ 34, 현재 epoch content correction 0입니다.
- **최종 checkpoint:** `journal_seq 101`의 SHA(`2729af…`)가 seq 101 row SHA와 같습니다.
  - `process-ended 42`와 `stop 46`은 close 이전 값입니다. 최종값 43/47보다 1씩 작은 것이 정상입니다.

### 1.2 시각 (`idle_deadline_wall_ms 1792982054698 = 02:34:14.698Z` 기준 환산)

| 이벤트 | 환산 시각(Z) | 대조 |
|---|---|---|
| prelive R1 수락 | 02:10:33.9 | 아래 모든 이벤트보다 앞섬 |
| Owner checkpoint-1 | 02:15:50.8 | genesis 이전 |
| genesis / start | 02:17:39.1 / 02:18:15.1 | R1 조건 "02:23:47Z 이전"을 충족 |
| seal / pause | 02:24:14.63 / 02:24:14.73 | 편집 약 5분40초. 02:42:07Z 이전 |
| idle 기한 산출 | 약 02:24:14.698 + 600초 | `strict_idle_deadline`의 10분 상한과 정확히 일치 |
| Owner checkpoint-2 | 02:30:37.5 | seal 이후, 기한 이전 |
| resume (전달) | 02:32:14.29 | 기한보다 약 2분 앞섬 |
| authority-apply | 02:32:27.97 | |
| process-ended / stop | 02:32:56.07 / .14 | `finished_at 02:32:56.336`과 맞음 |
| 시작 역산 | 02:32:56.336 − 920.563초 = 02:17:35.8 | genesis 직전으로 맞음 |
| postcheck | 02:33:39.5 | |

- pause부터 resume까지는 479.56초입니다. `owner_wait_seconds 479.435`는 출력 이후부터 잰 값이므로 약 0.1초 차이로 정합합니다.
- 이 값은 Owner의 응답 시간이나 수동 작업 시간이 아니라 대기 구간 전체라는 설명에 동의합니다.

### 1.3 해시와 식별자 결속

- **result_identity `12973c…`**가 다음 모든 곳에서 같습니다.
  - sealed, review, owner-checkpoint-2, ticket_derivation_scope, acceptance review, runtime result, postcheck
- **diff와 host spec:**
  - diff `240eac…`가 sealed review와 checkpoint-2에서 같습니다.
  - host_spec `ac28f9…`가 sealed, Host result, acceptance에서 같습니다.
  - process_group 91938도 서로 같습니다.
- **출력 메타데이터와 3개 verifier 입력:** 5개 출력 SHA가 모두 같습니다. `changed: true`는 BriefIndex 하나뿐이고 `changed_paths`와 일치합니다.
  - publish의 `document_refs`에 쓰인 Narrative SHA(`6d2c4a…`)도 같은 값입니다.
- **baseline 결속:**
  - commit `85a4db…`, tree `72cb62…`, message `e3caf7…`가 checkpoint-1, freeze, sealed base와 일치합니다.
  - owner_message_id O017과 O012는 각각 setup·commit 기록과 일치합니다. [공개용 중립화]
- **ticket packet:** `packet_sha256 07a142…`가 `core-001` stdout SHA와 같습니다. 정합하는 관측이지만 core-001이 어떤 호출인지는 패킷에 없습니다(N7).
- **freeze:** `prelive_freeze_sha256 31499c…`가 R1 수락과 checkpoint-1에서 같습니다.
  - freeze에는 helper 10개(run-review, postcheck 포함), source87, 두 test binary가 들어 있습니다.
  - candidate-admission의 test binary SHA도 freeze와 같습니다.

### 1.4 회귀 판정 논리 (`review-sealed.py`)

- 바뀌지 않은 4개 문서는 두 가지와 모두 bytes가 같아야 통과합니다.
  - 고정 기준 원본
  - attempt28 기존 출력의 SHA
- BriefIndex는 다음을 모두 요구합니다.
  - 고정 render-proof preview SHA와 같을 것
  - 행 하나가 LF 한 개로 끝날 것
  - 실제 marked GFM 결과가 `{columns: 4, rows: 26}`일 것
- 따라서 이 코드를 통과한 결과는 **이전 성공 결과의 byte 단위 재현**입니다. 의미상 비슷하다는 판정이 아닙니다.
- 이 대조는 Driver 실행에 의한 것이며, Reviewer는 bytes를 보지 않았습니다.

### 1.5 계수 정합

- 누적 authority-apply는 3입니다. 과거 2에 이번 1이 더해진 값입니다.
  - run-actual은 `max(0, 3−2) = 1`로 계산하고, ledger도 `authority_apply_used 1`입니다.
- review 9 = 7 + 2이고, correction 90 = 89 + 1입니다.
  - `correction-source 87`과 `correction 90`은 서로 다른 계수이며 정합합니다(R1 N6 설명 유지).
- 현재 epoch에는 review나 correction 이벤트가 없습니다.
  - 이번 4/4 리뷰는 epoch journal 대상이 아니므로 execution ledger에만 기록되는 구조입니다.

---

## 2. 비차단 발견 (9건)과 최소 후속

**N1. control worktree(T)의 잔여 상태가 명시되지 않음**
- postcheck는 T의 HEAD가 base commit이라는 것과, T의 5개 출력 bytes가 수락된 bytes라는 것을 동시에 요구합니다.
- 따라서 정적으로 보면 T에는 **BriefIndex 변경이 commit되지 않은 상태로 남아 있습니다**. Core 수락이 반영된 것입니다.
- 그러나 T의 `status --porcelain`과 untracked 파일은 검사하지도 보고하지도 않습니다.
- 후속: T 상태를 읽기 전용으로 한 번 기록하고, 이것이 기대한 Core 반영 결과라고 분류합니다. 잔여 상태의 처분은 Owner 판단으로 남깁니다.

**N2. 저장소 구조와 primary 불변 범위**
- `original_unchanged`는 primary의 HEAD, status, authority 파일만 확인합니다.
- T와 W가 primary와 git common dir을 공유한다면, 새 ref와 object 생성은 감지되지 않습니다.
- publish의 hook 검사는 `c.T/.git/hooks`를 대상으로 합니다. commit은 W에서 실행되므로 이 검사가 유효하려면 W가 T의 common dir을 쓴다는 전제가 필요합니다. T의 `.git`이 파일이면 검사는 아무것도 확인하지 않습니다.
- `setup-approved.py` 본문이 없어 확인할 수 없습니다.
- 후속: T, W, primary의 `git rev-parse --git-common-dir`와 primary `for-each-ref`를 전후로 비교하는 읽기 전용 기록을 남깁니다.

**N3. postcheck의 Core decision 결속이 약함**
- postcheck는 `state == completed`, `len(decisions) == 1`, pending 0만 확인합니다.
- decision이 다음 값과 같은지는 다시 확인하지 않습니다.
  - ticket_sha256 `5dfc87…`
  - actor `colvia-u2-delegate`
  - target revision `result-1`
  - selection
- 이 결속은 Host의 `Acceptance`/`InstalledCore`에 의존합니다. 두 클래스의 본문은 패킷에 없습니다.
- 후속: decision record와 ticket 필드를 읽기 전용으로 대조합니다.

**N4. offline 계수 증가의 출처가 없음**
- R1 시점 계산은 222 + 6 + 3 = 231이었습니다. 실제 activation에서는 `extra_offline_checks = 8`로 offline-start가 233입니다.
- 증가 방향이라 환불은 없고 validator 범위 안으로 보입니다. 그러나 추가된 2건이 무엇인지 기록이 없습니다.
- 첫 생존 조회의 EPERM과 승인 범위 밖 재조회의 기록 위치도 제공되지 않았습니다.
- 후속: ledger에 두 건을 설명하는 주석을 추가합니다.

**N5. Owner 결정의 provenance (R1 N7 유지)**
- `owner-decision.json`은 Driver가 쓴 파일입니다. Host는 `owner_message_id`가 있는지만 확인합니다.
- checkpoint-2의 `review_sha256`, `semantic_review_sha256`, `commit_message_sha256`은 대상 파일 bytes가 없어 Reviewer가 검증할 수 없습니다.

**N6. RPC 이벤트 일부가 분류되지 않음**
- `warning 2`와 `remoteControl/status/changed 1`의 내용과 분류가 없습니다.
- 실패 플래그는 모두 null/false이지만, 경고가 무해하다는 것은 Driver 판단입니다.
- 후속: 해당 이벤트의 종류만 안전하게 투영해 기록합니다.

**N7. 라벨이 모호함**
- `result.json` 두 개(helper `actual-native/result.json`과 Host `actual-native/first/result.json`)가 경로 없이 같은 이름으로 제시되었습니다.
- core-001/002가 각각 어떤 명령인지 없습니다. 예를 들어 514,601 bytes 출력의 의미를 알 수 없습니다.
- "Control/worker Core publication metadata"(state `review`)는 수락 이전 graph입니다. 최종 상태가 아닙니다.

**N8. admission 세부가 미제공**
- normal 31 cases를 실행하는 `budget-cases.py`는 SHA만 있습니다.
- `qualified-proxy-packet.json`의 `candidate_preflight`, app/proxy stdout도 없습니다.
- candidate-admission은 `passed` 플래그만 보여 주므로 Driver의 자가 보고 수준입니다.

**N9. 이번 리뷰 자체의 조건을 확인할 수 없음**
- 제공된 ledger projection에는 `review_reservations`가 없습니다.
- 그래서 다음은 `run-review`의 assert 조건으로만 추정할 수 있습니다.
  - 4회차 시작 시각이 03:06:05Z 이전인지
  - 요청 bytes가 회당 1MiB 이하이고, 기존 1,514,837 bytes와 합쳐 3MiB 이하인지
- `run-review`는 ledger를 lock이나 원자적 rename 없이 덮어씁니다. 그 시점에는 단독 writer이므로 경미합니다.

---

## 3. 유지되는 기존 한계 (R1 비차단)

- Rust가 상속한 `h10-01` start key는 이전 h10 start와 완전히 구분되지 않습니다. epoch-local slots에 의존합니다.
- proxy의 `h10-02` 차단은 Host와 journal에만 의존합니다. proxy 계층의 이중 방어는 없습니다.
- runtime의 document_policy 재계산을 Rust가 독립적으로 수행하는지는 검증되지 않았습니다.
- source-correction 음성 case는 class 독립 증거가 아닙니다.
- 원문은 15턴이고 운영 상한은 17턴이며, 실제 사용은 13턴입니다.
- semantic claims는 불변이고 binding oracle은 재결속되었습니다.
- conditional decision의 provenance(N5)가 남아 있습니다.
- trusted native runtime이므로 OS 전체 격리나 request-body privacy 보장이 아닙니다.

---

## 4. 판정 범위와 확대 금지

- **입증된 범위 (Driver 보고 + 정적 정합):** 단일 host, 고정 스냅샷, 실제 provider를 사용한 다음 회귀 관측입니다.
  - native 1회, thread 1개, 동일 thread의 13번째 turn에서 위임 accept 1회
  - Core 상태 completed, decision 1, pending 0
  - 수락 전후 result identity 불변
  - 프로세스 그룹 부재
- **Host 상태 `accepted-awaiting-owner-content-review`:** 기술적 수락은 완료되었다는 뜻입니다. 원문 품질에 대한 Owner의 직접 판정은 여전히 `unmeasured`입니다.
- **확대하지 않는 해석:**
  - Owner 능동 부담(`active_minutes: null`), 일반 생산성, 생산 지원 적격성
  - 새로운 Gradle/Docker/DB/HTTP 검증
  - 원격 publish (helper에는 push 경로가 없음을 정적으로 확인)
  - 추가 실행·재시도·새 epoch 권한
  - §2의 후속도 모두 읽기 전용 기록이나 문서 보정 제안일 뿐이며, 실행 권한을 뜻하지 않습니다.
- **본문 미제공으로 판단 근거에서 제외한 입력:**
  - `setup-approved.py`, `materialize.py`, `budget-cases.py`
  - Host의 `Acceptance`/`InstalledCore`/`Budget` 본문
  - Rust 제품 전체, sealed-review의 diff와 commit message bytes, Owner 메시지 원문
````

### Driver Disposition And Closeout

ACCEPT-regression/차단0를기술회귀범위에수용한다. 읽기전용보완으로Coredecision-ticket전체일치,actor/revision/selection,Gitcommondir독립,expectedcontrol미추적15기록,admission상세와계수·경고분류를확인했다. 첫closeout관측기는control문서변경1개만예상해untrackedCore15개에서멈췄으며효과없이기록후실제승인된상태로관측조건만보완했다. 제품/실행기보정·추가native·authority재시도는없다.

정확한H01–H10실행/상속/미관측표와파일별품질/Owner부담,계수/시간,보존·삭제는 private-evidence/E154 과거H04=source66/build53,H05=별도v1lane,원H10=source84/build70로귀속을정정하며원리뷰원문은그대로보존한다. 원문품질·Owner활동시간은미측정이고전체qualificationWorkDone/STATUS는변경하지않는다. 기술회귀의제한적수용을권고한다. [공개용 중립화]

이번마무리에서정확히25개빈경로/종료소켓을삭제했다. activepath변경0. controlprimary와acceptedworker,source/input/result/ticket/journal/review및필수복구근거는최종Owner품질·전체qualification판단의입력으로보존하며그판단또는명시적중단후다시정리판단한다. 원격publication/branch삭제없음. 기록시누적129.20분(대기포함),고정180분상한잔여50.80분이다.


## Tool-Neutral Adjustment Plan And Claude R0 — 2026-10-26

### Owner Scope And Current State

Owner는 기존 Core와 U1 수락을 유지하고 최소 변경·검증 실행안 작성과 Claude R0만 진행하도록 요청했다. 구현·작업용 runtime/model 실행은 아직 승인하지 않았다. 실행안은 [U2 Tool-Neutral Execution Plan](u2-tool-neutral-execution-plan.md)이며 본 Work가 진행 기록을 계속 소유한다. 새 task ID·typed Work·STATUS 변경은 없다.

자동 승인 검토가 첫 CLI 실행을 시작 전에 차단했다. 구체적인 내부 packet의 Claude 서비스 전송 승인이 부족하다는 이유였고, Owner가 “이 고정 자료의 전송과 R0 1회 승인”이라고 명시한 후 동일 42,071바이트 packet으로 1회 실행했다. 차단된 요청은 process/model start 0이며 실제 R0는 1회 소비했다. 구현과 합성 worker 실행의 승인이 추가된 것은 아니다.

### R0 Request And Exact Input

검토 요청은 Core/U1 수락 보존, 공통 보장의 손실 여부, 첫 3시간 Go 근거, 누적 20시간·시도 승계, 실행 setup의 명확성을 고정 packet으로 정적 검토하는 것이었다. packet은 새 계획 전체와 기존 M0/통합 계약 일부, 비식별 audit 관측·source identity로 한정했다. 실제 5문서·고객 정보·계정·credential·개인 경로를 보내지 않았다.

- Source base: `7d012f5297de1d9a77aa0b8187406f4785221573`. 기존 tracked diff SHA-256: `19ba06558616fe6d7d3139e681c7aa9d21ba8b2547f5e9d6eeae79d2ed3b0785`. 새 계획은 untracked 별도 입력이며 본문 전체를 packet에 포함했다. 기존 untracked Host/test는 identity만 제시했고 body review를 주장하지 않는다.
- 검토한 계획 SHA-256: `e98b700600862928c13f813aa166aa260bac3347ae6f62a45d0ba7a66b33fb8c`.
- exact request: 42,071바이트, SHA-256 `dabd66ebd23ce13fce7c424f9c1c389d6ae035256f1ec4d0c202936f824c9878`.
- actual Reviewer: `claude-opus-5-5`, fresh session `62e1f480-79cc-45c3-bb8e-cc22d21c136f`. Driver는 Codex, Owner는 human이다. 고정 packet/새 세션이며 동일 task 사실 요약은 Driver가 제공했으므로 사실 검증의 독립성은 제한된다.
- 실행: direct `claude --print --safe-mode`, tools 비움, strict empty MCP, settings sources 비움, `dontAsk`, permission prompts none, no session persistence, no Chrome. 정확한 argv와 입력 identity는 기존 private task metadata에 있다. cwd는 이 task 소유 review 폴더, timeout 880초와 종료 정리 10초다. 테스트·명령·파일 편집 권한은 없었다.
- 인증/과금: 호출 직전 `loggedIn=true`, `authMethod=claude.ai`, `apiProvider=firstParty`, `subscriptionType=pro`. 비밀 값/계정 이메일은 기록하지 않았다.
- 실제 결과: exit 0, 199.258초, tool use 0, MCP 0, process group 부재, 입력 drift 0. 응답 20326바이트, SHA-256 `151e5aa750901425d8e22b6e85d337614820d2aab8657fd06f6fd14f4bebaae6`. 정적 R0 `REVISE`, 차단 4건·비차단 9건. 제품 테스트/worker runtime 실행 근거가 아니다.

### Reviewer Response Verbatim

````text
# Static R0 Review: U2 Tool-Neutral Execution Plan

## 판정: **REVISE**

- 대상은 고정 packet에 포함된 새 계획 본문(제시된 digest `e98b7006…`)과 발췌된 과거 계약입니다.
- 차단 finding은 4건이며, 모두 **문서 보정만으로** 해소할 수 있습니다. 구현, runtime 실행, 기존 시험의 재실행은 요구하지 않습니다.
- 계획의 기본 구조는 타당합니다. 기존 Core/U1 수락을 보존하고, 과거 ledger를 합산하지 않으며, 문서·mock만으로 Go를 내리지 않습니다. 또한 `--bare`와 API key 우회를 금지합니다.
- 이 판정은 구현 승인이나 Owner 수락이 아닙니다. 보정된 revision은 이번 R0가 검토한 bytes가 아닙니다.

**근거 구분**
- **[정적]**: 제시된 문서 bytes만으로 내린 Reviewer의 추론입니다.
- **[Driver]**: packet에 기재된 Driver 관측이며, Reviewer가 재확인하지 않았습니다.
- **[미검증]**: runtime 보장으로, 어떤 근거로도 아직 입증되지 않았습니다.

---

## 요청된 네 가지 질문에 대한 답

### 1. 첫 3시간 gate는 의미가 있는가

**조건부로 의미가 있습니다.**

장점 [정적]:
- 상한(180분)이 전체 20시간 안에 포함됩니다.
- 165분에 판별을 끊고 15분을 정리에 씁니다.
- 실제 process 수, turn 수, 송신 수, dispatch 수의 상한이 있습니다.
- "문서·정적 추론·mock으로는 Go 불가" 원칙과 No-Go/Hold 구분이 명확합니다.

약점 [정적]:
- Go 판정에 쓸 **수용 가능한 근거의 형태가 사전에 등록되어 있지 않습니다.** 무엇을 "enforce 지점"으로 인정할지가 Driver의 사후 판단에 맡겨져 있습니다.
- 그런데 Go가 나오면 Owner 재승인 없이 B–D(최대 약 14시간)로 넘어갑니다.
- 그 결과 gate가 판단 기준이 아니라 형식적 관문으로 약화될 위험이 있습니다. → **F2**
- Go 조건이 "잔여 **시간**"만 보고 잔여 **시도 횟수**는 보지 않습니다. → **N1**

### 2. 20시간 예산이 무언가를 reset하는가

**기록은 reset하지 않습니다** [정적].
- 과거 ledger, continuation, H10 회귀 사용량을 수정하지 않습니다.
- 과거 잔여나 종료된 deadline을 빌려 쓰지 않습니다.
- 이번 R0도 기존 4/4의 5번째 호출로 숨기지 않습니다.

**다만 시도 카운터는 실질적으로 새로 할당됩니다.**
- 새 카운터: Codex 4 starts, model turn 16회, 송신 24회 등입니다.
- 과거 live 카운터(6 starts, 54 turns, 108 sends)와 별개입니다.
- 이것 자체는 정당한 **신규 Owner 할당**이며 reset이 아닙니다.
- 단, 최종 보고에서 Owner가 "누적으로 얼마나 썼는지"를 볼 수 있어야 합니다. 따라서 범주별로 과거 식별 구간과 이번 구간을 별도 행으로 나란히 표시해야 합니다(합산은 하지 않음). → **N9**에 포함

### 3. 공통 보장이 과거 계약을 조용히 약화하는가

**일부 약화됩니다.**
- 계획은 "조용히 축소하지 않는다"고 선언합니다.
- 그러나 7개 항목은 과거의 구체적 조건을 **요약·의역**한 것입니다.
- 그 과정에서 최소 다음 조건이 빠지거나 더 약한 형태로 바뀌었습니다. → **F1**
  - "차단(prevent)"이 "탐지 후 중단(detect-stop)"으로 바뀌었습니다.
  - turn당 상한이 사라졌습니다.
  - 송신 전 durable 예약이 사라졌습니다.

### 4. 향후 시도 한도와 exact setup은 운영상 명확한가

**명확하지 않습니다.**
- offline/fake-provider runtime process가 8 starts에 포함되는지 불명확합니다.
- turn당·process당 시간 상한이 없습니다.
- turn, 송신, dispatch 한도를 adapter별로 어떻게 나누는지 정해져 있지 않습니다.
- 검사 batch 한도가 전체 범위인지 단계별인지 불명확합니다.
- Codex에서 사용할 exact binary가 지정되어 있지 않습니다.
- Claude 실행 setup의 필수 필드가 정해져 있지 않습니다.
→ **F3, F4**

---

## 차단 Findings

### F1. 공통 보장 7항이 과거 강화 조건을 의역하며 일부를 약화함

- **심각도:** 높음 (차단)
- **위치:** "Required Common Guarantees" 3·4·6항, 그리고 첫 문단의 "조용히 축소하지 않는다"

**문제 [정적]**

과거 통합 계약 발췌(54–57, 104–115행)와 비교하면 다음 차이가 있습니다.

| 과거 계약 | 새 계획 |
|---|---|
| native **read-only auth**와 keyring 내부 write **차단**. refresh/relogin/store mutation 0 | 4항: "인증 갱신/write 필요는 **중단 사유**". 막는 것이 아니라 발생 뒤 멈추는 조건으로 읽힘 |
| final headers/bytes guard와 **fsync send reservation**(송신 전 예약) | 3항: "관측·예약·결속"이라고만 표현. 예약이 송신 **전**이어야 하고 durable해야 한다는 조건이 없음 |
| turn당 dispatch 최대 1회, generation 최대 2회 | 공통 보장과 한도표 모두에 없음. 총량만 있음 |
| reqwest retry 0, redirect 0, TLS fallback 0, 금지 sender 생성 차단 | "숨은 retry/fallback/redirect가 있으면 계약 미충족"으로 바뀜. 판정 기준으로는 남았지만 강제 요구로서는 약해짐 |
| TERM 10초 → KILL 10초 후 실제 종료 확인, 불명확한 descendant는 중단 | 6항: "자식 종료를 확인". 시간 기준과 미확인 시 처리가 없음 |
| 정책 단회·무cache·고정 bundle, 성공한 native model catalog 고정 | 언급 없음 |

**영향**
- 0–30분 단계에서 "원 필수 보장을 공통/도구별로 대응"하는 작업이 예정되어 있습니다.
- 그러나 이 작업은 **승인 이후** Driver가 수행합니다.
- 따라서 Owner는 어떤 조건이 Claude에게 면제되는지 모르는 상태에서 승인하게 됩니다.
- 특히 subscription OAuth의 자동 갱신은 탐지 시점에 이미 credential store가 바뀐 상태일 수 있습니다. "중단 사유"만으로는 과거의 "차단" 계약보다 약합니다. [미검증]

**최소 보정**
1. 과거 S0/IR 필수 조건을 행으로 나열하는 **대응표**를 계획에 추가합니다.
2. 각 행에 다음 셋 중 하나를 표시합니다.
   - 공통 Host에서 강제
   - adapter에서 강제
   - 동등 대체(근거 필요)
3. 다음 규칙을 명시합니다.
   - "동등 대체를 실제 관측으로 입증하지 못하면 해당 도구는 No-Go"
   - "탐지만 가능하고 차단이 불가능한 항목은 차단 계약을 충족하지 않음"
4. 4항을 "인증 갱신·store write는 **발생하지 않아야** 하며, 사전 차단 또는 사전·사후 비교로 입증하지 못하면 Hold"로 고칩니다.

---

### F2. 3시간 gate의 Go 근거 형태가 사전에 등록되지 않음

- **심각도:** 높음 (차단)
- **위치:** "First Three Hours" 30–75분 행, Go 판정 문단, "각 정상 단계마다 재승인을 요구하지 않는다"

**문제 [정적]**

첫째, Host가 통제하는 강제 지점과 관측 근거가 구분되어 있지 않습니다.
- 계획은 "enforce 지점"을 요구합니다.
- 그런데 Claude Code subscription 경로에서는 model 송신이 Claude process에서 외부로 직접 나갑니다.
- 따라서 Host가 송신 **전에** 예약·결속할 지점이 있는지가 핵심입니다. [미검증]
- 반면 다음은 강제 지점이 될 수 없습니다.
  - runtime이 스스로 보고하는 사용량, transcript, 사후 hook 기록
  - 이것들은 "관측"일 뿐입니다.
- 계획에는 이 구분이 없습니다.

둘째, 송신 결속을 위해 새 방식이 필요해질 수 있습니다.
- 예: 새 proxy, TLS 가로채기, base URL 변경
- 이런 방식은 과거 계약 54행의 "새 sandbox/proxy/credential 방식은 구현 전 보고·중단"에 해당합니다.
- 또한 인증·과금 경로를 바꿀 수도 있습니다.
- 그런데 계획은 이 경우를 Hold로 명시하지 않습니다.

셋째, 2회 실행만으로 "숨은 retry가 없다"는 부재(不在)를 입증할 수는 없습니다.
- 따라서 부재는 구조적 강제(retry가 일어날 수 없는 구성)로 입증해야 합니다.
- 단순히 관측 횟수로 입증할 수 없다는 점을 명시해야 합니다.

**영향**
- Driver의 해석에 따라 같은 관측이 Go가 될 수도, No-Go가 될 수도 있습니다.
- Go가 나오면 재승인 없이 큰 코드 변경(B)으로 넘어가므로 판단 오류의 비용이 큽니다.

**최소 보정**
1. 공통 보장 7항마다 근거 형태를 사전 등록합니다.
   - **인정:** Host 소유의 사전 gate, 이미 승인된 OS 수준 효과 제어, 실제 거절 관측
   - **불인정:** 문서, callback 단독, runtime 자기보고, 사후 로그
2. "새 proxy, 가로채기, endpoint·base URL 변경, 추가 credential이 필요하면 A 안에서 시도하지 않고 Hold"를 명시합니다.
3. Go를 내리면 B를 시작하기 전에 다음을 기존 Work에 durable checkpoint로 기록합니다.
   - 보장별 근거
   - 잔여 시간
   - 잔여 시도 횟수
4. 기록 전에는 B를 시작하지 않습니다.
5. 별도 Owner 재승인까지 요구할지는 Owner의 선택입니다. Reviewer는 최소한 이 기록 의무를 권고합니다.

---

### F3. Claude 실행의 exact setup 필드와 환경 부작용 Hold 조건이 정해지지 않음

- **심각도:** 높음 (차단)
- **위치:** "Decision" 문단의 "실행마다 정확한 값을 고정", 0–30분 행, 75–145분 행, 공통 보장 2·4항

**문제 [정적·미검증]**

계획은 값을 "고정한다"고만 말하고, **어떤 필드를 고정해야 하는지** 정하지 않습니다. 그 결과 다음이 모두 미정입니다.

- **실행 경로**
  - CLI와 SDK 중 무엇을 쓸지 정해지지 않았습니다.
  - SDK는 별도 package 설치가 필요할 수 있습니다.
  - 계획은 "새 SDK 설치가 필요하면 추정의 전제가 깨진다"고만 쓰고, **A를 중단(Hold)한다고는 쓰지 않습니다.**
- **버전 drift**
  - CLI의 자동 update는 실행 중 binary 교체(설치 행위)가 될 수 있습니다.
  - telemetry, 오류 보고, update 확인은 model 이외의 외부 송신입니다.
  - 공통 보장 3항은 model 송신만 다루고, 2항의 "외부 연결"이 이를 포괄하는지 모호합니다.
- **Ambient 입력**
  - 사용자 설정, project 설정, memory 파일, skill/plugin, output style, hooks가 prompt나 tool 구성에 섞일 수 있습니다.
  - 이 경우 3항의 "허용 입력과 실제 송신의 정확한 결속"이 깨집니다.
- **재개 의미**
  - 75–145분의 "실제 stop 후 잔여 예산 재개"가 무엇을 뜻하는지 불명확합니다.
  - native session resume은 사용자 home의 transcript 저장소라는 ambient 상태에서 문맥을 불러옵니다.
  - 반면 Core 기반 fresh session은 계획 본문("재개는 Core의 승인·입력…에서 시작")과 과거 계약 35행이 정한 경로입니다.
  - 둘 중 어느 쪽인지 지정되지 않았습니다.
- **로컬 기록**
  - Claude가 사용자 home에 남기는 session 기록은 합성 데이터라도 4항의 "기록" 범위에 해당할 수 있습니다.
  - 기록 위치와 정리 방법이 없습니다.
- **인증 용도**
  - subscription 경로는 지금까지 Reviewer 호출 용도로만 쓰였습니다.
  - 이를 **worker runtime 용도**로 쓰는 것은 계획 서두의 "새 runtime 인증·과금 경로 전환"에 해당할 여지가 있습니다.
  - 실행 승인이 이 용도를 명시적으로 포함해야 하는지가 정해지지 않았습니다.
- **기타:** model 이름, 권한 mode, 허용 tool 목록, cwd/HOME, 환경변수 allowlist가 미정입니다.

**영향**
- Owner는 model, 버전, 설치 여부, 환경 부작용을 모르는 상태에서 실제 runtime 실행을 승인하게 됩니다.
- A 증거의 재현성과 결속 판정이 불가능해질 수 있습니다.

**최소 보정**
1. 계획에 "A 실행 전 고정할 필수 필드 목록"을 추가합니다. 값은 0–30분 단계에서 채웁니다.
   - 경로(CLI/SDK), 버전과 digest, model, 인증 경로, 권한 mode
   - tool allowlist, 설정 source, cwd/HOME/env
   - update·telemetry 상태, session 저장 위치, 재개 방식
2. 다음 경우는 Hold로 명시합니다.
   - 설치나 update가 필요한 경우
   - update·비model 송신을 끌 수 없거나 관측할 수 없는 경우
   - ambient 입력을 배제할 수 없는 경우
   - 인증 용도 확인이 불명확한 경우
3. 재개 방식은 **Core 기반 fresh session**을 기준으로 합니다. native resume을 쓰려면 native session ID와 history digest의 결속을 입증해야 한다고 명시합니다.
4. 실행 승인 문안에 "subscription 경로의 worker 실행 용도 포함 여부"를 명시 항목으로 둡니다.

---

### F4. 향후 시도 한도의 계수 범위와 단위가 모호함

- **심각도:** 중상 (차단: 운영 명확성)
- **위치:** "Cumulative Budget And Attempts"의 한도 목록, "Remaining Implementation" C행

**문제 [정적]**

1. **8 starts의 범위**
   - 과거 계약은 offline qualification(36 starts)과 live(6 starts)를 분리했습니다.
   - 새 계획의 "각 actual runtime process가 1회"라는 정의로는 다음이 8에 포함되는지 알 수 없습니다.
     - fake-provider/offline fixture runtime process
     - 집중 test가 띄우는 runtime process
   - 포함한다면 H01–H05 영향 경로를 재검사하기에 8이 부족할 수 있습니다.
   - 제외한다면 별도 상한이 없습니다.
2. **turn당·process당 상한 부재**
   - 총량(16/24/24)만 있고, turn당 dispatch 1회·generation 2회 상한이 없습니다(F1과 연관).
   - 과거의 "model turn 최대 15분, host case 5분, TERM 10초→KILL 10초"도 다시 명시되지 않았습니다.
3. **adapter별 배분**
   - starts만 4/4로 나누고, turn·송신·dispatch는 나누지 않았습니다.
   - A의 4/6/6이 16/24/24에 포함되는지도 starts와 달리 명시되지 않았습니다.
4. **검사 batch 범위**
   - "로컬 집중 검사 batch는 최초 1 + 보정 최대 2"가 20시간 전체에 대한 한도인지, A·B·C 단계별 한도인지 불명확합니다.
5. **Codex exact binary**
   - "exact 기존 binary/source 근거를 보존"한다고만 씁니다.
   - 과거 근거는 서로 다른 source/build(accepted offline proof, H10 회귀 candidate 등)에 걸쳐 있습니다.
   - C에서 Codex live 실행에 쓸 binary의 identity가 지정되지 않았습니다.

**영향**
- 같은 실행을 두고 한도 초과 여부를 달리 판정할 수 있습니다.
- Codex 회귀가 어느 build를 기준으로 하는지 불명확해집니다.

**최소 보정**
1. 한도표에 다음 열을 추가합니다.
   - 계수 대상(live/offline/test-spawned)
   - adapter별 배분
   - A 포함 여부
   - 단위(전체/단계/turn/process)
2. turn당 상한, process당 상한, 종료 시간 규칙을 과거 값 그대로 다시 명시합니다. 바꾼다면 그 이유를 적습니다.
3. Codex adapter가 사용할 단일 binary와 그 근거 build를 지정합니다. 0–30분에 특정하지 못하면 C의 Codex 실행은 Hold라고 명시합니다.

---

## 비차단 Findings

### N1. B–D 단계에 hard stop이 없고, Go 조건이 시도 잔량을 보지 않음

- **위치:** "Remaining Implementation" 표, Go 문단
- **문제 [정적]:**
  - 한도 우선순위 규칙은 "단계 한도와 전체 한도 중 먼저 닿는 것"입니다.
  - 그런데 B–D에는 추정치만 있고 단계 한도가 없습니다.
  - Claude starts는 최대 4회이고 A가 2회를 쓰므로, C에서는 2회만 남습니다. 이는 허용/거절/stop/resume 확인과 U1 확인을 겨우 담을 수 있는 수준이며 재시도 여유가 없습니다.
- **보정:**
  - B의 상한을 정합니다(예: 7시간 도달 시 재추정 checkpoint).
  - Go 조건에 "잔여 시도 횟수로 C를 수행할 수 있음"을 추가합니다.

### N2. A 증거를 C에 재사용한다는 가정이 낙관적임

- **문제 [정적]:**
  - A는 B(공통 Host 분리) 이전에 작성한 probe로 실행합니다.
  - 따라서 "같은 candidate/동일 경로"라는 재사용 조건을 대부분 충족하지 못할 가능성이 큽니다.
- **보정:** C의 시간과 횟수 추정은 A 증거를 재사용하지 않는다는 전제로 잡고, 재사용 가능한 항목은 예외로 표시합니다.

### N3. A probe의 위치와 처분이 최소 변경 경계표에 없음

- **보정:** probe를 artifact 경로에만 둘지 source에 둘지 정합니다. 또한 B에서 흡수하거나 폐기하는 기준을 한 줄로 명시합니다.

### N4. Hold/No-Go 이후의 예산과 승인 유효기간

- **보정:** 다음 두 가지를 명시합니다.
  - A를 다시 실행하면 같은 20시간과 같은 카운터에서 차감되며, 새 180분이 생기지 않습니다.
  - 실행 승인은 source/CLI 버전 drift가 생기면 효력을 잃습니다.

### N5. Owner 능동 확인 시간이 20시간 활동 예산에 포함되는지 불명확함

- D의 Owner 20–30분은 측정 대상입니다. 그런데 72,000초에 포함되는지, 별도 기록만 하는지 불명확합니다.
- **보정:** 포함 여부를 한 줄로 정합니다.

### N6. R0 verdict가 적용되는 revision을 구분해야 함

- 차단 finding을 Driver가 처분하면 revision이 바뀝니다. 계획대로 R0를 다시 하지 않는다면, 다음 결정 문서에 다음을 표시해야 합니다.
  - R0가 검토한 digest
  - 보정 후 digest
  - Reviewer가 보지 않은 보정 구간

### N7. "180분의 선행 구간" 표현이 모호함

- 계획/R0 시간이 180분 **밖에** 있고 20시간에서만 차감된다는 뜻으로 보입니다.
- **보정:** "180분에 포함되지 않음"으로 문장을 명확히 합니다.

### N8. onboarding 문서 수정의 시점

- Claude U2가 미검증인 상태에서 "Codex·Claude Code 주요 경로"라는 문구를 쓰면 지원 선언처럼 읽힐 수 있습니다.
- **보정:** 수정 시점을 C의 결과 이후로 하거나, "미검증" 표기를 의무화합니다.

### N9. 과거 ledger의 산술 불일치는 unknown으로 유지

- **관측 [정적]:**
  - 2026-10-25 continuation 기록에서 누적 cap 182,297.229초에서 이전 사용량 150,036.092초를 빼면 약 32,261초입니다.
  - 이는 "추가 8시간(28,800초)"과 약 3,461초 차이가 납니다.
- 계획이 이 값을 합산하지 않고 unknown으로 남기는 방침은 적절합니다. 지금 이 차이를 해소할 필요는 없습니다.
- 다만 최종 보고에서 범주별 과거 구간과 이번 구간을 별도 행으로 나란히 보여 주는 형식을 고정하기를 권합니다.

---

## 재요구하지 않는 사항

- 기존 normal 706회와 optimized 706회 검사의 재실행, Core 전체 suite, Rust 재build는 요구하지 않습니다. Core managed 30파일의 동일성 유지로 충분하며, 변경된 U2 4파일과 새 adapter 위험만 새로 검사하면 됩니다.
- H10 원 리뷰를 다시 수행하거나 5문서를 재생성할 필요가 없습니다.
- Claude runtime 능력의 증명은 지금 구현할 대상이 아닙니다. 그대로 **gate로 남겨 두는 것**이 맞으며, 미입증 상태는 PASS가 아닙니다.

## 한계

- 이 리뷰는 고정 packet만을 대상으로 한 정적 검토입니다. host.py, worker.py, test 본문, 원 H01–H10 기준과 recovery 명세 전체는 보지 못했습니다. digest는 identity 확인용일 뿐, 본문을 검토했다는 뜻이 아닙니다.
- Claude 공식 문서에 대한 서술은 Driver의 관측을 그대로 사용했고 Reviewer가 재확인하지 않았습니다. CLI의 자동 update, telemetry, session 저장 동작에 관한 언급은 확인된 사실이 아니라 **Hold 조건으로 다뤄야 할 위험 가설**입니다.
- 공통 보장 1–7항이 Claude 공식 경로로 충족 가능한지는 **[미검증]**입니다. 이 리뷰는 충족 가능성을 지지하지도 부정하지도 않습니다.
- 이 verdict는 구현 승인, 실행 승인, Owner 수락을 대신하지 않습니다.
````

### Driver Disposition

| Finding | 처분 | 문서 보정/판단 |
| --- | --- | --- |
| F1 | revise | 기존 강화 조건을 행별 대응표로 복원했다. 인증/store write 사전 차단, 정책·catalog 고정, final headers/bytes와 송신 전 fsync 예약, retry/fallback 0, generation 2/dispatch 1의 turn 상한, TERM/KILL을 명시했다. 탐지/사후 비교만으로 차단을 대신하지 않는다 |
| F2 | revise | 보장별 인정/불인정 근거를 사전에 정했다. 새 proxy/TLS/endpoint/credential 방식은 Hold다. Go 뒤 B 전 보장별 근거·잔여 시간/시도와 exact setup을 durable checkpoint로 남긴다 |
| F3 | revise | 현재 CLI/model/digest·subscription worker 용도, tool/config/env/update/telemetry/session/argv 필드를 고정했다. SDK 설치·ambient 입력·비model 송신을 배제할 수 없으면 Hold. 재개는 Core 기반 fresh session이며 native resume 0이다 |
| F4 | revise | live/offline/test-spawned 계수, 도구별 배정과 A 포함 여부, turn/process/batch timeout을 명시했다. Codex 입력은 초기 build snapshot이 아닌 H10 최종 보정·실제 봉인 candidate와 현재 binary bytes의 일치로 확인했다 |
| N1 | revise | B 8시간, C 6시간, D 2시간 단계 stop과 전체 stop 중 먼저 닿는 한도를 적용한다. Go는 C를 끝낼 시도 잔여도 확인한다 |
| N2 | revise | C 추정은 A probe를 재사용하지 않는 전제다. 동일 경로·candidate·보장을 입증한 경우만 재사용한다 |
| N3 | revise | A probe는 기존 durable task 하위 폴더에 두고 B에서 필요한 계약만 흡수한다. 소비자가 사라지면 일회성 probe를 정리한다 |
| N4 | revise | Hold/No-Go 뒤 자동 재개·새 180분 부여를 금지했다. 예상 밖 source/CLI drift는 기존 exact setup의 실행을 막는다. 승인된 B 수정과 drift를 구분한다 |
| N5 | revise | 이번 Owner 능동 확인도 20시간에 포함하고 동시 구간은 합집합으로 한 번 계산한다. Owner 답변만 기다리는 시간은 별도다 |
| N6 | revise | 원 reviewed digest와 보정본 digest를 구분한다. 이번 보정은 Driver 검토이며 Reviewer의 재검토/ACCEPT가 아니다 |
| N7 | revise | 현재 계획/R0 시간은 A의 180분 밖이며 전체 20시간에서만 차감한다고 명확히 했다 |
| N8 | revise | source-only EN/KO README의 필요한 문단은 C 결과 뒤 실제 지원/미검증을 구분한다. managed 30파일은 변경하지 않는다 |
| N9 | defend / revise | 보존·구간별 병기 제안은 반영했다. 다만 약 3,461초 차이는 당시 이전 cap 153,497.229초에서 사용량 150,036.092291초를 뺀 잔여와 추가 28,800초의 합으로 설명된다. 현재 사용 가능 잔여는 아니며 다른 역사적 포함 관계의 unknown을 해소한 것으로 확대하지 않는다 |

Driver 자체 문서 검사에서 recovery anchor 1개를 실제 heading으로 수정했다. 문서 scope에서 managed support/entry 변경과 source-only 설명을 분리하고, intake 기준 변경은 별도 DR-0003 amendment 대상으로 남겼다. 실행·관측 조건을 복원했을 뿐 현재 Claude worker의 적격성을 입증한 것은 아니다.

보정본 SHA-256: `b364f6bd6655b44822b0aa6c2251434043838654dd277df84b396b8d1ef1b6d8`. 변경된 구간은 Minimum Change Boundary, Required Common Guarantees, 새 Guarantee Mapping/Exact Runtime Setup, First Three Hours, Remaining Implementation, Cumulative Budget And Attempts, Next Decision이다. 이 구간과 anchor 보정은 Reviewer가 보지 않았다. 추가 R0는 실행하지 않았고 실제 verdict는 REVISE로 유지한다. 차단 지적의 Driver 문서 처분은 완료했으며 실행 승인/최종 수락은 Owner에게 남는다.

### Budget And Next Decision

향후 A–D 예상은 9.5–16.5시간 + 이번 준비/R0 실측이다. 현재 전체 전망은 약 10–18시간, 제안 추가 상한은 20시간이며 마지막 30분을 정리에 예약한다. 첫 A는 실행 승인 뒤 활동 3시간(판별 165분+정리 15분), 전체 안에 포함된다. 기존 누적 기록·실패/사용 횟수는 그대로 보존하고 종료된 H10 잔여를 전용하지 않는다. 이번 준비 구간은 metadata의 2026-10-26 06:27:00Z 시작부터 최종 checkpoint까지 계상한다.

현재 완료된 것은 계획 작성, Claude 정적 R0 1회와 문서 보정이다. 구현 edits 0, worker runtime/model starts 0, 새 authority apply 0, Core suite 실행 0, Rust build 0, commit/push 0이다. 과거 Core/U1 수락과 H10 제한적 기술 회귀 의미는 유지한다. 원 H10 품질·Owner 부담과 전체 U2 qualification은 여전히 열려 있다.

다음 결정은 보정본을 대상으로 한 구현·합성 실행·bounded R1 범위 승인이다. 이번 계획·R0 승인을 실행 승인으로 바꾸지 않는다. Work는 Active로 유지하며 별도 acceptance/Done/STATUS 변경을 하지 않는다.

### Planning Closeout Checkpoint

2026-10-26T06:56:40.402454+00:00 시점에 이번 준비/R0 활동 1780.206초(29.67분)를 기록했다. 전용 Owner idle은 0초로 두고 이 구간 전체를 보수적으로 계상했다. 향후 제안 72,000초에서 먼저 차감하면 70219.794초(19.505시간)가 남는다. 이는 미래 실행 승인 전 계산값이며 활성 권한/새 deadline이 아니다. 별도 마지막 보고 작업이 생기면 다음 checkpoint에서 같은 구간에 이어 계상한다.

검사 결과: 새 계획/추가 Work 구간의 local link·anchor, GFM 강조, 공백·비식별 공개 경계, tracked diff check 통과. 기존 구현 입력과 이전 ledger digest 변화 0, accepted managed 30파일 불일치 0, review process group 부재. 제품 테스트나 worker runtime 실행은 하지 않았다.

보존: source 실행안, 본 Work의 정확한 R0 원문/처분, private exact request와 identity·인증·계수 metadata. Owner 실행 결정과 다음 Driver의 근거 재사용이 소비자이며 결정/명시적 중단 뒤 재정리한다. 삭제: 종료된 단회 리뷰 runner 1개, 본 Work에 bytes 일치로 보존한 중복 응답 1개, 확인된 빈 scratch 디렉터리 1개. active 경로 변경 0. 기존 source/runtime/control worktree와 기존 증거·복구 입력은 후속 구현 및 미완료 품질 판정에 필요해 유지했다. branch 삭제나 bulk cleanup은 없다.

### Owner Model Direction — 2026-10-26

Owner는 사용량 부담을 고려해 Colvia 작업용 Claude CLI를 Sonnet 5.5로 바꾸고 현 세션 리뷰는 Opus 5.5로 유지하는 방향을 제시했다. 공식 CLI 문서의 호출별 `--model` 지원과 Sonnet 5.5의 공식 model ID를 확인해 실행안의 예정 설정만 수정했다. Worker는 `claude-sonnet-5-5`, Reviewer는 `claude-opus-5-5`로 분리한다. 전역 CLI 설정·구독/인증·Core·기존 budget/attempts는 바꾸지 않는다.

Sonnet의 account availability/worker 적격성은 미검증이며 첫 A의 기존 admission/승인된 probe에서 확인한다. 별도 시험 호출이나 자동 Opus/API fallback을 추가하지 않았다. 사용량 절감은 기대이며 절감률·생산성·성공을 측정한 결과가 아니다. 기존 Opus R0 원문과 reviewed identity는 그대로 보존하고 이 후속 수정은 R0 재검토를 받은 것으로 표시하지 않는다.

수정 전 실행안 SHA-256 `b364f6bd6655b44822b0aa6c2251434043838654dd277df84b396b8d1ef1b6d8`, 수정 후 `d7439bb54651f7e01a36c451214c2df59f656542ce5f0ea4d6dc8687856129c1`. 이번 추가 계획 구간은 2026-10-26T06:59:03.950390+00:00부터 2026-10-26T07:01:33.301131+00:00까지 149.351초이며 기존 준비 사용량에 추가한다. 이전 보고와 이번 요청 사이의 대기는 차감하지 않는다. 구현·worker model·새 Reviewer 호출은 모두 0회다. 실행 결정은 여전히 Owner에게 남는다.

### Owner Execution Approval And A Start — 2026-10-26

Owner의 “ㅇㅋ 계속하자”를 직전 Sonnet worker/Opus Reviewer 구분이 반영된 실행안 SHA-256 `d7439bb54651f7e01a36c451214c2df59f656542ce5f0ea4d6dc8687856129c1`에 대한 계속 실행 승인으로 기록한다. 앞선 계획/R0 사용량 1929.557초를 차감하고 기존 72,000초 전체 한도와 시도 이력을 승계한다. A 시작은 2026-10-26T07:04:23.887980+00:00, 판별 중지 2026-10-26T09:49:23.887980+00:00, 정리 포함 종료 2026-10-26T10:04:23.887980+00:00다. 이는 3시간을 반드시 소비한다는 뜻이 아니며 필수 제어 지점이 미지원/불명확하면 일찍 No-Go/Hold로 종료한다.

허용 범위는 승인안의 단계·파일·합성 데이터·고정 구독 경로와 횟수 안이다. Go checkpoint 전에 B 구현을 시작하지 않는다. 실제 adopter authority, credential/endpoint/권한 변경, 보장 축소, 새 fork/build, 전체 suite는 별도 경계를 유지한다. R1의 bounded public-safe packet 범위 외 데이터 전송은 허용하지 않는다. 현재는 비밀 없는 파일 identity/공식 인터페이스 조사를 수행하며 worker model invocation은 아직 0회다.


### A Feasibility Hold And Concrete Contract Choice — 2026-10-26

A는 2026-10-26T07:13:15.524162+00:00에 8.86분 활동 후 합성 worker/model 호출 전 Hold로 판정했다. 180분은 상한이며 필수 제어 지점이 미확정인 상태에서 시간을 채우거나 probe를 강행하지 않는다. 현재 제한은 Sonnet 성능·가용성 실패가 아니라 공식 CLI/subscription 경로의 제어 근거 부족이다. Claude U2가 영원히 불가능하다거나 미관측 사고가 발생했다고 주장하지 않는다.

실제로 수행한 것은 고정 source/binary identity 읽기와 Claude CLI `--safe-mode --help` 1회다. help는 0.074초, exit 0, stderr 0, process group 부재였다. 보수적으로 Claude offline start 1회에 계상했다. worker live starts/turns/sends/dispatch, 새 인증 subcommand, authority apply, 구현, 추가 Reviewer 호출은 모두 0이다. help 출력은 내부 통신을 계측한 결과가 아니며 model 요청을 공급하지 않았다는 사실과 구분한다. 기존 Opus 리뷰의 구독 인증 관측은 역사로 유지하고 이번 Sonnet worker admission 성공으로 옮기지 않는다.

| 필수 조건 | 이번 근거와 판정 |
| --- | --- |
| source·binary·model 선택 | 고정 두 binary와 기존 source 입력 일치. Sonnet 공식 ID와 CLI model 지정 가능은 확인; account worker availability는 미실행 |
| Core authority와 Host tool 효과 차단 | 기존 Core 수락 유지. Claude adapter의 실제 거절 관측은 아직 없으므로 미검증 |
| 최종 HTTP headers/body 결속 + 송신 전 fsync 예약 | 공개 CLI/help와 hook 목록에서 해당 사전 gate를 찾지 못했다. prompt/tool hook은 최종 HTTP sender와 동일하지 않다. 필수 근거 미확정 → Hold |
| native OAuth 갱신·credential store write 사전 차단 | 공식 문서는 saved login 갱신과 갱신 실패 시 저장 credential 정리 경로를 설명한다. 현 승인 경로에서 쓰기 전에 차단할 방법은 입증하지 못했다 → Hold |
| retry/fallback·model 송신 수 | retry 설정은 존재한다. 모든 인증/transport 경로의 0 retry와 송신 전 예약을 설정 이름만으로 입증하지 않는다 → 미검증 |
| update/telemetry/ambient/session | 끄는 공식 옵션은 있다. 실제 효과 차단 검증은 아직 없다. 새 설정·credential·proxy는 적용하지 않았다 |
| 실제 loop/stop/fresh resume, H01–H10 및 품질 | 선행 조건 미충족으로 미실행. 기존 결과는 해당 과거 범위로 유지 |

공식 근거(2026-10-26 확인): [Hooks](https://code.claude.com/docs/en/hooks), [CLI](https://code.claude.com/docs/en/cli-reference), [Login expired](https://code.claude.com/docs/en/errors#login-expired), [Retry controls](https://code.claude.com/docs/en/errors#tune-retry-behavior), [Environment variables](https://code.claude.com/docs/en/env-vars). 지원되는 표면에서 해당 제어를 확인하지 못한 정적 판정이다. 새 proxy/TLS 가로채기·endpoint·credential 경로·CLI fork를 만들지 말라는 승인안의 경계를 지켰다. 구조적 근거가 부족하므로 단순 성공 호출을 추가해도 Go 조건을 채우지 못한다.

#### Concrete Next Decision

기존 Core/U1 수락과 사용량 보존을 전제로 선택지는 다음과 같다. 아래 권고는 적용되지 않은 계약 변경 제안이며, 현재 승인안이나 과거 증거를 수정하지 않는다.

| 선택 | 유지/변경할 경계 | 결과 |
| --- | --- | --- |
| 현 강화 조건 유지 | 모든 adapter에 최종 HTTP bytes/송신 사전 예약·credential write 0을 계속 요구 | 현재 Claude U2는 Hold. 공식 제어 지점 또는 별도 승인된 구현 경로가 확보될 때만 재개 |
| 공통 계약 조정 검토(Driver 권고) | Core의 exact intent/Work/grant/ticket/result, 효과 전 tool 검사, worker 격리, 누적 예산/중단·복구는 공통 필수로 유지. 모델 서비스의 내부 HTTP 생성/자동 retry/OAuth 관리에는 공식 native CLI를 신뢰하는 범위를 명시 | Sonnet adapter를 공식 CLI로 검증할 수 있는 별도 지원 범위를 제안. 동일한 transport/credential 보장을 달성했다고 주장하지 않음 |

권고안에서 바뀌는 것은 세 항목이다. (1) Claude 경로에 대해 최종 HTTP bytes의 Host 결속·매 송신 fsync 예약 보장을 요구하지 않고, Host가 제공한 입력과 실제 model identity·CLI 결과를 기록한다. 내부 요청 전체와 정확한 송신 수는 관측/강제 불가로 표시한다. (2) 기존 구독의 native OAuth 갱신/저장 관리를 CLI의 신뢰 범위로 명시하되 raw credential을 Host로 가져오거나 API key·다른 계정으로 전환하지 않는다. (3) 내부 model sends 24회 같은 hard cap을 그대로 주장하지 않고, Host가 강제할 CLI starts·wall time·tool dispatch와 CLI가 제공하는 turn 제한·보고 사용량을 구분해 새 한도안을 제시한다. updater/telemetry/ambient 입력 배제와 모든 실제 업무 효과·authority 제한은 유지한다.

이 변경은 안전/지원 계약의 조정이므로 Driver가 자동 적용하지 않는다. Owner가 조정 검토를 선택하면 기존 Work 안에서 해당 세 조항과 한도를 수정한 계획 및 Opus 5.5 정적 리뷰안을 구체화한다. 별도 runtime 호출·추가 과금 경로·전역 설정 변경은 그 검토의 일부가 아니다. 예상 20–40분(판단 추정), 최대 60분, Opus R0 추가 1회/160 KiB/15분과 public-safe 수정 조항·합성 evidence 전송을 제안하며 현재 승인된 R1 두 회와 혼동하지 않는다. 기존 20시간의 남은 시간에서 차감하고 이후 구현은 보정 계획의 실행 결정에 따른다. 이 후속 검토는 아직 실행하지 않았다.

현재 A 잔여 171.14분과 전체 잔여 19.316시간은 기록값이며 Hold를 우회할 권한이 아니다. 재개하더라도 원 20시간과 사용한 CLI help 1회 등 누적 이력을 승계하고 A의 180분을 초기화하지 않는다.

A 보존 checkpoint: 2026-10-26T07:15:59.949894+00:00, 판별·선택안·정리까지 활동 11.60분. 이전 준비와 합쳐 43.76분이며 전체 20시간 잔여 19.271시간, A 잔여 168.40분이다. Owner 결정 대기 시작 이후 별도 활동이 없으면 이 시각부터 대기를 제외한다. 기존 승인안·Core30·구현 입력·과거 ledger는 모두 불변이고 추가 Work 구간의 GFM/공백 및 diff check를 통과했다. exact help 출력과 실행/관측 metadata는 Owner 경계 선택의 근거로 보존한다. 완료된 단회 help runner와 빈 stderr 파일 2개, 빈 scratch 디렉터리 1개를 삭제했다. active 경로 변경 0. 권고안 검토의 승인 여부를 기다리며 자동 모델 호출이나 구현을 하지 않는다.

### Owner Approval For Contract Amendment Review — 2026-10-26

Owner는 “공통 계약 조정안과 Opus R0 검토 승인”을 선택했다. [native CLI trust boundary amendment](u2-native-cli-trust-boundary-amendment.md)를 작성하고 Opus 5.5 R0 1회 및 비민감 packet 최대 160 KiB의 Claude 전송을 진행한다. 예상 20–40분, 최대 60분이며 시작 2026-10-26T07:18:06.482342+00:00, 판별/수정 중지 2026-10-26T08:13:06.482342+00:00, 정리 포함 종료 2026-10-26T08:18:06.482342+00:00다. 기존 조정 누적 2625.619초에 이어 계상하며 전용 Owner 대기 126.532초는 제외한다. 원 A 잔여 10103.938초와 기존 과거 카운터를 초기화하지 않는다. 구현/worker 실행·계약 activation은 아직 허용하지 않는다.


### Native CLI Amendment R0 And Driver Disposition — 2026-10-26

[공통 계약 조정안](u2-native-cli-trust-boundary-amendment.md)의 Opus 정적 R0 1회를 완료했다. 실제 verdict는 REVISE이며 차단 3건·비차단 7건이다. 아래 원문과 Driver 문서 처분을 분리한다. 구현/worker 실행, amendment activation 및 A Hold 해제는 이번 작성/R0 승인의 범위가 아니다.

#### Scope, Input Identity And Execution

- 요청: Claude native-CLI trust boundary의 명시적 변경, 보존할 Core/업무 효과·중단·복구, 구독 경로 및 누적 한도 정합성. test/tool/agent/network browsing/source edit 없는 고정 packet 정적 검토다.
- source base: `7d012f5297de1d9a77aa0b8187406f4785221573`; tracked diff SHA-256 `19ba06558616fe6d7d3139e681c7aa9d21ba8b2547f5e9d6eeae79d2ed3b0785`. 검토 문서는 untracked 입력으로 packet에 전문을 포함했으며 diff만으로 식별하지 않는다.
- reviewed amendment SHA-256 `cd783fe09ac6a4d2e8e0f68e1ab0a58a963cd25bf79ae7394f38da72c7bb8bf1`; parent 승인안 `d7439bb54651f7e01a36c451214c2df59f656542ce5f0ea4d6dc8687856129c1`; help 원문 `b10f5c36adfe3285f6c5a0d18284f466e6c4486499de56ef62745e13312a7fbc`.
- exact request 60,439 bytes/160 KiB 상한, SHA-256 `7720cca8d16a8d3443c795fbd86d9151e364d2f496a3125ee24d3fc9b2d68d44`. 비민감 조항·합성 Driver 관측·공식 help 발췌만 포함해 승인된 Claude 서비스에 전송했다. 실제 5문서/고객 내용·계정 email·credential은 포함하지 않았다.
- 실행: 고정 Claude Code 2.1.310, actual model `claude-opus-5-5`, fresh session `5fbee59c-60a4-4441-96a9-b9694826d00f`. 호출 직전 비밀 없는 인증 관측은 `claude.ai / firstParty / pro`, override 변수는 존재 여부만 확인했다. Reviewer 인증 확인은 이 R0의 사전 검사이며 미래 Sonnet admission 성공을 뜻하지 않는다.
- 명령: pinned CLI의 `--model claude-opus-5-5 --print --safe-mode --tools "" --disable-slash-commands --strict-mcp-config --mcp-config`(빈 MCP) `--setting-sources "" --permission-mode dontAsk --permission-prompts none --no-session-persistence --no-chrome --effort high --output-format stream-json --verbose`와 고정 session/system prompt. 전체 argv는 private R0 metadata에 보존한다.
- 시작 `2026-10-26T07:23:27.234782+00:00`, 종료 `2026-10-26T07:27:17.273861+00:00`, 실측 230.039초, exit 0, timeout 없음. process group 부재, tool use 0, MCP 0, stderr 0, 전후 입력 drift 0. CLI 결과 success는 응답 완료이며 문서 ACCEPT가 아니다. 테스트 실행/재현 counterexample은 없다.
- 원문 16,883 bytes, SHA-256 `287a7443573e47a8d91a9159070611804691a808207ccc8bbb4b6e1317fbdee8`. 아래 응답을 bytes 그대로 보존한다. Reviewer는 제공 packet만 읽었고 공식 문서와 Driver 관측을 독립 실행/재확인하지 않았다.

#### Verbatim Reviewer Response

````markdown
# R0 정적 검토: Claude Native CLI Trust Boundary Amendment

## 판정: **REVISE**

차단 지적은 3건, 비차단 지적은 7건입니다. 모두 문안을 보정하면 해소되는 수준이며, 재설계나 범위 확대는 필요하지 않습니다.

이 판정은 조정안 문안의 계약 적합성만 다룹니다. 실행, worker qualification, 계약 활성화를 승인하는 의미가 아니며 Owner 결정을 대신하지도 않습니다.

## 검토 근거의 구분

- **사실(packet 내 원문)**
  - 조정안 전문과 기존 실행안 전문
  - 고정 CLI의 `--safe-mode --help` 발췌
- **Driver 관측(본 Reviewer가 독립 확인하지 않음)**
  - binary/source digest 무변동
  - help 1회 실행과 그 계수
  - A의 소비 시간 696.062초
  - 공식 문서 조사 결과: hook 표면에 최종 송신 결속 gate가 없음, refresh 실패 시 저장 credential이 지워질 수 있음, safe-mode에서도 managed 정책이 적용됨
- **미지(런타임 미관측)**
  - Sonnet 가용성
  - `--safe-mode`·strict MCP·`dontAsk` 조합의 실제 동작
  - init inventory가 노출되는 시점
  - effective effort의 관측 가능성
  - managed 정책 존재 여부
  - `--max-turns`의 실제 의미

## 유지된 안전장치에 대한 총평

Transport 보장을 철회한다는 핵심 방향은 명시적이고 범위가 정해져 있습니다.

- 철회 대상은 최종 HTTP bytes 결속, 모든 송신 전 fsync 예약, retry 0, credential write 0, 정책·catalog 불변, 내부 송신 hard cap입니다.
- 적용 범위는 Claude native-CLI profile에 한정됩니다.
- Codex의 과거 PASS 의미를 바꾸지 않는다고 밝혔습니다.

본 검토는 이 완화를 옛 profile 기준으로 다시 요구하지 않습니다. 유지된 효과·권한 장치도 구조적으로 타당합니다.

- 모델 출력은 권한이 아님
- Host 소유 bridge와 고정 ID/schema 검증
- 효과 전 durable 예약과 fsync
- native shell/file/browser/subagent tool 미노출
- 실제 checkout을 cwd로 넘기지 않음
- 기존 worker 격리 유지
- stop 시 새 요청·효과 즉시 차단
- native transcript가 아닌 Core 기반 fresh 재개
- 미지 값을 0이나 추정치로 표시하지 않음
- 자동 replay·자동 구매·API 전환 금지

다음 사항도 대체로 충족됩니다.

- Core/U1/H10 수락을 재개방하거나 승격하지 않음(초점 4)
- proxy, SDK 설치, `--bare`, API key, 새 fork, 전역 model 변경이 없음(초점 6)

남은 문제는 세 가지입니다. 완화 조항 목록이 불완전해 보존 규칙과 충돌하는 점, 완화 대상이 아닌 stop 경계가 조용히 축소된 점, managed 정책 경계가 비어 있는 점입니다.

---

## 차단 지적

### B1. 조항 변경표가 불완전해, 보존 규칙이 철회한 보장을 다시 부과함

**위치**
- 조정안: "Named Clause Changes" 표와 "표시하지 않은 … 조건은 보존한다" 문장
- 기존 실행안의 미기재 조항:
  - **Required Common Guarantees 서두:** "강화 조건을 이번에 조용히 축소하지 않는다"
  - **Required Common Guarantees 2:** "native identity·세대 변경을 고정", "외부 연결을 실행하지 않는다"
  - **Guarantee Mapping 도입부:** "차단이 필요한 조건을 탐지 후 중단으로 바꾸지 않는다", "미지원은 No-Go"
  - **Guarantee Mapping 'prepared tool inventory, native thread/turn/call, history version과 승인 input 결속' 행:** "실제 송신/dispatch 직전 강제 지점"
  - **Exact Runtime Setup:** "model/control 외 송신은 0이다", "설정만으로 차단을 입증했다고 쓰지 않는다", "예기치 않은 home 기록이 필요한 경로는 Hold"
  - **First Three Hours 30–75분 행:** "송신 횟수/최종 입력 결속·retry … 제어 지점이 없으면 No-Go"
  - **Cumulative Budget 마지막 문단:** "내부 송신을 사전에 제한할 수 없으면 Hold이며 turn 수나 사후 token 사용량으로 대체하지 않는다"

**영향**

조정안은 여러 항목을 "관측 즉시 차단 후 Hold"로 바꿉니다. model 변경, 정책·catalog 변화, telemetry 설정 준수, 표준 cache·credential metadata 기록이 그 예입니다. 그러나 위 조항이 문자 그대로 남아 있으면 이 대체 방식은 금지되고, A의 Go는 구조적으로 불가능해집니다.

반대로 실행자가 "취지상 함께 바뀐 것"으로 해석하면 그것은 명시되지 않은 완화가 됩니다. 어느 쪽이든 초점 1이 경계하는 묵시적 재부과나 묵시적 완화가 생깁니다.

**최소 보정**

변경표에 위 조항을 각각 행으로 추가하거나, profile 우선 적용 대상 목록을 열거해 명시합니다. 포괄적인 "본 amendment 우선" 문장으로는 부족합니다. 구체적으로는 다음을 적습니다.

1. **inventory·history 결속:** Claude profile에서는 송신 직전 대신 다음으로 대체합니다.
   - init 시점의 inventory 확인
   - bridge dispatch 시점의 요청 검증
   - native call ID와 Host step의 대응
2. **탐지 후 중단 허용 범위:** native trust 항목에만 허용합니다(model 변경, 정책·catalog, telemetry 설정 준수, 표준 cache 기록). Host 효과 항목(효과 전 예약, scope 거절, worker 격리)에는 계속 사전 차단을 요구한다고 적습니다.
3. **Hold 사유에서 제외:** "model/control 외 송신 0"과 "내부 송신 사전 제한 불가 시 Hold"는 이 profile의 Hold 사유가 아님을 적습니다. 대신 "비허용 연결·설정이 관측되면 중단"으로 바꿉니다.

### B2. Stop 경계가 process group/descendant에서 "직접 소유 child"로 축소되었고, bridge 배치와 live 중단 관측이 정해지지 않음

**위치**
- 조정안 Common Effect And Authority Contract 6, 그리고 3과 4
- Fixed Runtime Profile의 strict MCP bridge 항목
- Minimum Qualification 4
- 기존 Required Common Guarantees 6과 비교

**영향**

1. **완화 대상이 아닌 축소.** 기존 조건은 "실제 process group/descendant 부재 확인, 불명확한 descendant가 있으면 미확인으로 중단"입니다. 이는 transport 보장이 아니라 효과·중단 보장이므로 완화 대상이 아닙니다. 그런데 새 6항은 "CLI와 직접 소유 child"로 범위를 좁혔습니다.
   - strict MCP의 stdio bridge는 통상 CLI가 띄웁니다(정적 추론이며 런타임은 미지).
   - 그러면 bridge는 CLI의 child가 되고, bridge가 호출하는 worker는 그 아래 descendant가 됩니다.
   - 이 경우 "직접 소유 child" 표현은 worker 잔존을 놓칠 수 있습니다.
2. **bridge 배치가 미정.** journal·fsync·slot 원자성은 Host가 소유해야 합니다. 그러나 다음이 정해지지 않았습니다.
   - CLI가 띄운 bridge process가 Host 신뢰 범위인지, native 신뢰 범위인지
   - authority handle을 bridge에 어떻게 전달하는지, 혹은 전달하지 않는지
   - stop 시 누가 누구를 종료하는지
3. **live "중단" 관측이 모호.** Minimum Qualification 4는 "첫 process가 종료된 상태를 확인"이라고만 씁니다. 자연 종료로도 충족되는 문장입니다. 그러나 변경표의 Go 행과 기존 First Three Hours는 실제 중단을 요구합니다.

**최소 보정**

- 6항을 기존 문언으로 되돌립니다. Host가 CLI를 별도 process group으로 띄우고, CLI·bridge·worker 전체의 부재를 확인하며, 불명확한 descendant가 있으면 미확인으로 중단한다는 내용입니다.
- bridge를 "Host 소유 journal·slot에 위임하는 얇은 relay"로 규정합니다. authority 판단과 fsync는 Host 측에서만 일어나고 bridge는 실제 authority handle을 갖지 않는다고 적습니다.
- A의 첫 process 종료를 다음 둘 중 하나로 확정합니다.
  - Host가 시작한 TERM 경로의 실제 stop과 부재 확인
  - live stop은 미관측으로 남겨 Go 불가로 처리
- 이 선택은 Owner가 결정할 수 있습니다.

### B3. Managed 정책·hook 경계가 정책 불변 철회와 함께 비어 있음

**위치**
- 조정안 변경표 둘째 행(auth/policy/catalog)
- Common Effect 4와 5
- Fixed Runtime Profile의 사용자·project 설정 배제 항목
- 근거: help 원문 "Admin-managed (policy) settings still apply"

**영향**

조정안은 정책 단회·무cache를 보장하지 않는다고 밝힙니다. 따라서 세션 도중 정책이 바뀔 가능성을 스스로 열어 둡니다. 한편 Common Effect 4는 "실제 파일 효과는 격리 worker만 수행"한다고 주장합니다.

managed hook이 있으면 이 주장이 성립하지 않을 수 있습니다.
- managed hook은 Host bridge를 거치지 않고 명령을 실행하는 효과 경로입니다.
- 세션 시작류 hook은 Host가 init inventory를 보기 전에 실행될 수 있습니다(정적 추론이며 실제 순서는 미지).

조정안은 "남으면 Hold"라고만 쓰고 두 가지를 정하지 않았습니다.
1. 대량 열람 없이 managed hook·MCP·tool 부재를 확인할 허용 근거
2. 세션 중 정책 변화로 효과 경로가 추가되는 경우의 처분과 잔여 위험

**최소 보정**

1. **시작 전 근거 정의.** 비밀이 없는 근거로 정합니다. 예를 들면 managed 설정 source의 존재 여부와, CLI가 보고하는 effective hook·MCP·tool 집합입니다. 확인할 수 없으면 Hold로 둡니다.
2. **세션 중 정책 변화 처분 선택.** 다음 중 하나를 고르도록 명시합니다.
   - (a) managed 정책이 부재할 때만 이 profile을 적용
   - (b) 세션 중 정책에 의한 효과 경로 추가는 Host가 사전에 거부할 수 없는 native trust 잔여 위험으로 명기하고, 관측 즉시 중단
3. **Owner 결정 문장에 포함.** 선택한 항목을 Owner 결정 문장에 넣습니다.

---

## 비차단 지적

### N4. Credential 잔여 위험과 정책·catalog 완화가 Owner 수용 문장에서 빠짐

**위치:** 변경표 둘째 행 "없어지는 보장" 열, "Support Claims And Owner Decision" 마지막 문단

**영향:** Driver 관측에는 refresh 실패 시 저장 credential이 지워질 수 있다는 내용이 있습니다. 이는 Owner 계정의 로그인 상태가 바뀌는 결과이지만, 수용 대상으로 명기되지 않았습니다. Owner 결정 문장도 "native OAuth 운영/transport 신뢰·계수 변경"만 열거하고 정책·catalog 불변 철회는 빠뜨렸습니다.

**최소 보정:** 두 가지를 명기합니다. 또한 login expired나 credential 소실이 관측되면 A를 Hold하고 재로그인하지 않으며, 이를 Host 결함이 아닌 native trust의 결과로 기록한다는 규칙을 추가합니다.

### N5. 일부 활동의 계수 귀속이 비어 있음

**위치:** "Proposed Limits And Inheritance" 표, Minimum Qualification 1–3, Fixed Runtime Profile의 비밀 없는 status 확인

**영향:** 다음 활동이 어느 카운터에 속하는지 정해지지 않았습니다.
- 비밀 없는 auth status 확인: native process 1회가 필요하며, 내부 refresh를 유발하는지는 미지입니다.
- init inventory·identity 관측: inventory가 첫 model 송신 이후에야 보인다면 live start와 Host step을 소비합니다.
- control message를 통한 고정 입력 주입
- offline bridge 검사: "최초 batch 1"을 A에서 쓰면 B–D에는 보정 batch 2만 남습니다.

**최소 보정:**
- 각 활동의 귀속 카운터를 표에 적습니다.
- "시작 전 Hold"가 실제로는 "첫 효과 전 Hold"일 수 있다면 그렇게 고쳐 씁니다.
- bridge 시도 카운터의 예약도 durable·fsync로 남겨 재개 시 승계된다고 적습니다.

### N6. A 잔여 시간에 맞춘 내부 일정이 다시 정해지지 않음

**위치:** "Proposed Limits And Inheritance" 둘째 문단, Minimum Qualification 전반

**영향:** 잔여는 10,103.938초(약 168.40분)입니다. 기존 0–180분 일정과 "165분에 판별 종료, 이후 15분 정리"를 잔여에 어떻게 대응시킬지 적혀 있지 않습니다.

정적 산술로는 들어갑니다. live process 30분×2와 Host step 15분×4가 같은 구간에 겹치고, bridge 작성과 offline 검사, 마지막 정리가 그 앞뒤에 놓입니다. 다만 여유는 작습니다. 요청 4개와 step 4개가 1:1이므로, 추가 요청이 하나만 나와도 이후 negative 관측은 불가능해집니다.

**최소 보정:**
- 판별 종료를 "A 잔여 15분 시점"으로 명기합니다.
- negative 미관측은 Go 불가 사유이며 Hold로 처리한다고 명확히 합니다. 원문 "Hold/No-Go"보다 구체적으로 적습니다.

### N7. Model identity와 effort의 근거 수준

**위치:** Fixed Runtime Profile 첫 bullet과 마지막 문단

**영향:** 기존 Mapping은 "모델 자기보고는 근거 아님"이라고 합니다. 조정안이 말하는 "actual model response의 identity"가 무엇인지 불명확합니다. 모델 본문 텍스트가 아니라 CLI가 보고하는 metadata, 즉 native trust 범위의 근거를 뜻하는지 밝혀야 합니다.

**최소 보정:** 근거 원천을 CLI metadata로 명기합니다. effective effort를 관측할 수 없을 경우, "요청값 기록으로 수용"할지 "Hold"할지는 Owner가 고를 선택지로 남겨 둡니다.

### N8. A bridge inventory에서 `u2_accept`와 `u2_write_file` 제외를 명시

**위치:** Fixed Runtime Profile의 strict MCP bridge 항목

**영향:** A의 네 사례는 read, verify, 거절뿐입니다. accept tool을 모델에 노출하면, Host가 검증하더라도 "모델이 승인 문구를 만들어도 권한이 생기지 않는다"는 원칙의 공격면만 넓어집니다.

**최소 보정:** A의 고정 부분집합을 `u2_read_file`과 `u2_verify`로 명기합니다. 이후 단계에서 쓰는 `u2_accept`는 기존 human 또는 명시적 delegation 판정에만 연결된다고 적습니다.

### N9. CLI 옵션 근거의 공백

**위치:** Host Steps And Bounded Effects(`--max-turns 2`), Fixed Runtime Profile, 그리고 help 발췌

**영향:**
- packet의 help 발췌에는 `--max-turns`가 없습니다. 이 옵션이 없다는 뜻이 아니라, 이 packet으로는 미확인이라는 뜻입니다.
- 발췌의 둘째 설명 블록은 옵션명이 잘린 채 중복돼 있어, 어떤 옵션의 설명인지 식별할 수 없습니다.
- `--no-session-persistence`는 `--print`에서만 동작한다고 적혀 있습니다.
- `--safe-mode`가 "MCP servers"를 끄는 범위에 명시적 `--mcp-config`도 포함되는지는 미지입니다.

**최소 보정:**
- 이미 소비한 1회 help 출력의 보존본에서 정확한 argv를 확정합니다. 보존본이 없어 다시 실행해야 하면 offline start로 계상합니다.
- native tool 제거 수단을 옵션명으로 고정합니다.

### N10. 이번 R0 처분 방식에 대한 고지

**위치:** "Proposed Limits" 표의 첫 행

**영향:** 승인된 R0는 1회입니다. 따라서 REVISE에 따른 보정본은 Driver 처분이며 재검토를 거치지 않습니다. 직전 실행안도 "revised bytes were not re-reviewed" 상태였습니다.

**최소 보정:** Owner 결정 요청에 다음을 명기합니다.
- 보정본은 재검토되지 않은 bytes임
- 추가 R0나 R1 소비는 없음

---

## 남은 Owner 선택과 누락 입력

1. **live 중단 관측:** A에서 Host가 시작한 실제 stop을 수행할지, 미관측으로 남겨 Go 불가로 둘지(B2)
2. **managed 정책:** 부재를 필수 조건으로 할지, 세션 중 변화를 잔여 위험으로 수용하고 관측 시 중단할지(B3)
3. **effort:** effective 값을 관측할 수 없을 때 수용할지, Hold할지(N7)
4. **credential 소실 위험:** native trust의 결과로 명시 수용할지(N4)
5. **누락 입력:**
   - 정확한 argv
   - native tool 제거 옵션명
   - `--max-turns` 존재 근거
   - init inventory 노출 시점(런타임 미지)

## 결론

transport 보장 철회 자체는 명시적이고, profile 범위가 한정되며, 정직하게 서술되어 있습니다. Host 효과·권한 계약도 대부분 그대로 유지됩니다.

다만 차단 지적 세 건은 Owner가 정확한 bytes를 실행 계약으로 적용하기 전에 문안에서 해소되어야 합니다.
- **B1:** 미열거 조항이 완화된 보장을 재부과함
- **B2:** 완화 대상이 아닌 stop 경계가 축소됨
- **B3:** managed 정책 경계가 비어 있음

보정은 표에 행을 추가하고 기존 문언을 복원하며 선택지를 명시하는 수준입니다. 새로운 테스트, 도구, 시간, 호출은 필요하지 않습니다. 이 검토는 계약 결정을 위한 참고 자료일 뿐이며, Sonnet worker 적격성이나 실행 승인 근거로 쓰일 수 없습니다.
````

#### Driver Disposition

| Finding | 처분 | 반영한 문서 변경과 한계 |
| --- | --- | --- |
| B1 | revise | 서두/보존 문장, inventory·history/dispatch mapping, exact setup의 송신·home·정책·필드, A Go, 계수 및 B–D 완료 조건을 각각 명시적으로 override했다. native trust에만 탐지 후 중단을 허용하며 Host 효과 전 gate는 유지한다 |
| B2 | revise | CLI·relay·worker 전체 group/descendant 종료로 복원했다. 얇은 relay는 authority/journal 권한을 갖지 않고 Host controller가 판단·fsync·worker 실행을 소유한다. A에서 Host가 시작한 TERM 및 전체 부재를 실제 관측하는 안으로 고정했다. 자연 종료만 있으면 Hold |
| B3 | revise / needs-user | admin-managed 정책 부재 환경만 적용하는 안을 선택했다. 시작 전 source 존재/관리 provenance 확인, unknown이면 시작 금지, init inventory는 추가 근거, 세션 중 정책 출현 시 종료를 명시했다. 사용자 정책 우회는 없다. 이 적용 전제는 최종 실행 결정의 일부다 |
| N4 | revise / needs-user | OAuth refresh 실패 시 credential 삭제·로그인 상태 변경 가능성, service-policy/catalog 불변 철회를 수용 대상에 적었다. expired/소실 관측 시 Hold하며 자동 재로그인하지 않는다. 실제 사고가 관측됐다는 뜻은 아니다 |
| N5 | revise | auth status/non-model 검사, init/live 입력, control/fault 입력, offline batch를 계수에 귀속했다. bridge 시도도 validation 전 durable/fsync 예약·재개 승계하며 실패/unknown은 Hold다. A 최초 batch 뒤 B–D 보정 2만 남는다 |
| N6 | revise | A 잔여 10,103.938초의 배치를 다시 정하고 마지막 900초 정리를 유지했다. process 30분×2와 step 15분×4는 겹친 시간이다. 필수 negative가 미관측이면 Hold이며 추가 요청/시간을 자동 부여하지 않는다 |
| N7 | revise / needs-user | model은 CLI 구조화 metadata로 확인한다. effort는 medium 요청 고정, effective 미노출 unknown 허용을 제안하며 다른 값 관측 시 Hold다. 이 native trust 선택을 실행 승인 묶음에 포함했다 |
| N8 | revise | A에는 read/verify만 노출하고 write/accept를 제외했다. 이후 accept도 기존 human/명시적 delegation 규칙에 한정한다 |
| N9 | revise | 기존 help 보존본을 재사용해 native tool 제거 및 print-mode argv template을 적었다. packet의 잘린 중복 발췌를 명시하되 frozen input은 바꾸지 않았다. max-turns는 공식 reference 근거이며 고정 binary/safe-mode+MCP 조합은 아직 미실행이다. 미지원이면 Hold |
| N10 | revise | reviewed/revised identity를 구별하고 보정본 미재검토를 명시했다. 추가 R0/R1 없이 Driver 처분만 수행했다 |

보정본 SHA-256 `2a885cc877402b9f62dcf0a0e157c12a60d8416128f7eaa6854a7dbe23f1e2ac`. 위 보정 전체는 Reviewer가 보지 않은 bytes다. 차단 지적을 문서로 처분했다는 Driver 판단이며 REVISE를 ACCEPT로 승격하지 않는다. 아직 native 정책 부재, Sonnet worker, 옵션 조합, Host stop/negative/fresh 재개는 검증하지 않았다.

#### Pending Owner Execution Decision

Owner가 결정할 구체 안은 위 digest의 amendment를 기존 승인안에 적용하고 원 A의 잔여부터 재개하는 것이다. native HTTP/재시도/내부 횟수·OAuth 운영과 credential 소실 가능성, service-policy/catalog 불변 철회, managed 정책 부재 환경 제한, requested medium/effective unknown 허용을 함께 제시한다. Host의 authority/effect gate와 전체 descendant 종료·Core fresh 재개는 유지하며 A의 실제 Host stop은 필수다.

기존 실행 승인 전체를 다시 요청하는 것이 아니라 보장/인증 관리 경계가 달라지는 부분과 Hold 뒤 재개에 대한 결정이다. 승인되면 기존 Go checkpoint 안에서 B–D를 이어가며 단계별 routine 재승인은 없다. 실제 고객 데이터·계정/과금 전환·commit/push·최종 수락은 포함하지 않는다. 이번 작성/R0 승인은 이 실행 결정을 대신하지 않는다. Work Active·Core/U1 수락·원 A Hold를 유지한다.

이번 추가 R0 1/1은 소비 완료, 미래 R1은 0/2다. worker live starts/model calls 0, 구현 edits 0, authority apply 0, Core suite/Rust build/commit/push 0이다. A help 1회 및 과거 R0/H10 사용 이력은 그대로다. A 잔여는 10,103.938초(168.40분)로 유지하고 이번 문서/R0 시간은 전체 20시간에서만 차감한다.


#### Amendment Closeout Checkpoint

2026-10-26T07:39:01.163194+00:00 시점에 이번 문서/R0/보정·정리 활동 1254.681초(20.91분)를 계상했다. 예상 20–40분/상한 60분 안이며 Opus 대기와 문서 검사를 포함한다. 이번 구간의 별도 Owner 대기는 0초다. 앞선 2625.619초를 합친 이번 조정 총 사용량은 3880.300초(64.67분), 기존 20시간 잔여는 68119.700초(18.922시간)다. A 잔여 10,103.938초는 그대로이고 마지막 전체 30분 정리 예약도 유지한다. 이는 현재 잔여 기록이며 Hold를 해제하는 권한이 아니다.

검사: 보정안과 추가 Work 구간의 GFM 강조(코드 밖 literal asterisk 없음)·local links·공백, git diff check, 응답 원문 bytes 보존을 확인했다. 원 승인안·Core managed 30파일·구현 입력 7개 변화 0, R0 종료 process group 부재다. 문서 보정만으로 새 runtime/full suite 실행이 필요하지 않아 수행하지 않았다. 보정 SHA-256은 `2a885cc877402b9f62dcf0a0e157c12a60d8416128f7eaa6854a7dbe23f1e2ac`이며 재검토되지 않았다.

보존: source 조정안, 본 Work의 exact R0 응답·처분·Owner 결정 대상, private exact reviewed packet과 인증/identity/계수 metadata. 소비자는 Owner 실행 결정과 다음 Driver의 A 재개이며 결정·근거 재사용 완료 또는 명시적 중단 뒤 용도를 다시 판단한다. 삭제: 완료된 단회 runner 1개, Work에 bytes 일치 보존한 중복 응답 1개, 확인된 빈 scratch 디렉터리 1개. active 경로 변경 0. 기존 source/runtime/control worktree는 A/B–D 후속 작업 및 미완료 H10 품질 판정에 필요해 유지했다. branch 삭제나 bulk cleanup은 없다.

구현/worker 실행/계약 activation은 하지 않았다. Owner의 exact 실행 결정을 기다리며 A Hold를 유지한다.


### Owner Amendment Execution Approval And A Resume — 2026-10-26

Owner는 직전 보정안 적용 및 A 재개 요청에 “승인”으로 답했다. 승인 대상은 [native CLI amendment](u2-native-cli-trust-boundary-amendment.md) SHA-256 `2a885cc877402b9f62dcf0a0e157c12a60d8416128f7eaa6854a7dbe23f1e2ac`와 기존 승인안 `d7439bb54651f7e01a36c451214c2df59f656542ce5f0ea4d6dc8687856129c1`의 명시적 결합이다. 이번 U2 실행 범위에서 해당 profile을 활성화한다. Core/DR-0005 자체나 기존 Codex 강화 계약을 수정하는 activation은 아니다. Opus REVISE 및 보정본 미재검토 사실을 유지하며 결과 수락을 대신하지 않는다.

A 재개 시작 `2026-10-26T07:42:54.656737+00:00`, 남은 활동 10103.938초, 판별 종료 `2026-10-26T10:16:18.594737+00:00`, 정리 포함 종료 `2026-10-26T10:31:18.594737+00:00`다. 이전 총 사용 3880.300초와 전체 잔여 68119.700초, A help 1회·worker 0회 및 기존 모든 시도를 승계한다. Owner 답변만 기다린 구간은 별도이며 과거 한도나 사용량을 초기화하지 않는다.

먼저 native 시작 전 관리 정책 부재와 고정 입력/구독 경로를 확인한다. 조건 충족 뒤만 승인된 작은 probe/bridge와 최소 합성 live 검증으로 진행한다. 모든 필수 Go 조건과 잔여 시간/시도를 기존 Work에 기록하기 전에는 B를 시작하지 않는다. 이후 정상 B–D는 기존 승인 범위에서 이어가며 추가 routine gate를 만들지 않는다. 실제 데이터·새 계정/과금·commit/push·최종 수락은 별도 경계를 유지한다.


### Native CLI A Resume: Auth Admission Hold — 2026-10-26

승인된 amendment를 적용한 A preflight에서 native auth 확인이 실패해 worker 시작 전에 Hold했다. 현재 결과는 Sonnet 가용성/성능 실패나 전체 계정 credential 소실을 입증하지 않는다. 실패를 보존하고 최초 실패 뒤 즉흥 재시도하지 않는 원 승인안의 A 규칙을 적용했다.

| 근거 종류 | 실제 관측과 한계 |
| --- | --- |
| local read / OS status | system managed settings/drop-ins/MCP, system/user managed preferences, user preferences, remote settings cache가 모두 부재했다. `profiles status -type enrollment` exit 0, DEP/MDM 모두 No. 설정 내용/전체 profile 목록·secret store를 수집하지 않았다 |
| 공식 기준 | [Managed settings](https://code.claude.com/docs/en/managed-settings)의 macOS source와 [server-managed eligibility](https://code.claude.com/docs/en/server-managed-settings#platform-availability)를 확인했다. 과거 Pro 관측 하나만으로 현재 정책 부재/계정 적격성을 단정하지 않고 native auth 재확인을 요구했다 |
| identity | 고정 amendment/parent plan/CLI digest 일치, Core30와 구현 입력7 무변경 |
| executed native auth | 고정 2.1.310의 `--safe-mode auth status` 1회, 시작 `2026-10-26T07:47:16.349264+00:00`, 0.090초/exit 1/stderr 0/timeout 없음/process group 부재. 모델 입력은 주지 않았다. non-model pool에 예약 후 실행했고 A 누적 2/6(기존 help1+이번 auth1), 전체 Claude non-model 2/12다 |
| 수집기 결함 | Driver 수집기가 exit 0일 때만 stdout JSON을 파싱하고 실패 stdout을 버렸다. 따라서 이번 응답의 loggedIn/authMethod/provider/configDirectory 필드는 복구할 수 없다. 이 수집기 결함을 인증 실패 원인과 구별하며 빈 dict를 실제 CLI 응답으로 해석하지 않는다 |
| static comparison | 이전 성공한 Reviewer auth는 `auth status`, ambient 환경 상속이었다. 이번에는 safe-mode와 제한된 환경 allowlist를 사용했다. 기존 USER/LOGNAME/SHELL/__CF_USER_TEXT_ENCODING 변수가 현재 부모 환경에는 있지만 이번 child에는 전달되지 않았다. 차이는 확인했으나 어느 항목이 원인인지 재현하지 않았다 |

[공식 CLI reference](https://code.claude.com/docs/en/cli-reference)는 auth status의 exit 1을 그 호출에서 로그인되지 않은 상태로 설명한다. 이 값만으로 일반 터미널의 저장 인증이 손상됐다고 확대하지 않는다. 재로그인/logout·키 발급·계정/endpoint 변경 명령은 실행하지 않았다. native OAuth 내부 저장 동작은 승인한 trust 범위이며 독립적으로 계측하지 않았다.

#### Prepared Single Recovery Decision

수집기를 보정한 단회 auth 재확인안을 준비했으며 실행하지 않았다. runner SHA-256 `af4f833d2c92c928d2cca399321721175e40bdec77a672d615a82a12dd85a0fa`. 동일 pinned CLI/`--safe-mode auth status`/cwd/30초 한도와 updater·telemetry·오류 보고 비활성화를 유지한다. 환경은 기존 allowlist에 USER, LOGNAME, SHELL, __CF_USER_TEXT_ENCODING 이름 4개만 추가해 현재 사용자 세션 값을 상속한다. 값을 출력/기록하거나 전역 환경을 수정하지 않는다. 이 환경 보정은 원인 확정이 아닌 제한된 후보이며 safe-mode를 제거하지 않는다.

변경된 수집기는 exit code와 관계없이 JSON의 loggedIn/authMethod/apiProvider/subscriptionType만 보존하고 configDirectory는 예상 경로와의 일치 여부만 남긴다. 원문 email/token·전체 출력은 저장하지 않는다. syntax compile만 확인했으며 이 script를 import/실행하지 않았다.

제안 범위는 auth 명령 1회(기존 A/전체 non-model 잔여에서 차감), 예상 2–5분/누적 중단 한도 10분이다. 명령 30초는 그 안에 포함한다. 모델 호출 0, 추가 리뷰 0, 새 login/API key/과금/endpoint/전역 설정 변경 0. 성공하면 해당 exact 환경을 고정하고 기존 승인된 A를 남은 시간/시도 안에서 계속한다. 실패하면 응답의 비밀 없는 필드를 보존하고 다시 Hold하며 추가 재시도하지 않는다. 이는 최초 실패 후 Hold에서 재개하고 고정 환경을 보정하는 제안이므로 Owner의 해당 재확인 승인을 기다린다. 기존 20시간과 A 잔여를 늘리지 않는다.

#### Resume Closeout

2026-10-26T07:52:20.512867+00:00까지 이번 재개 활동 565.856초(9.43분)를 계상했다. A 잔여 9538.082초(158.97분), 전체 잔여 67553.844초(18.765시간)다. worker live starts/Host steps/bridge requests/효과, focused test batch 및 R1은 이번 구간 모두 0이다. Source 구현은 하지 않았고 사전검사용 task-local helper만 작성했다. Work Active, Core/U1 수락, 원 품질/수락 조건을 유지한다.

보존: 이 Work와 execution 기록의 비밀 없는 관측, exact 실패 수집기, 준비된 단회 보정 수집기. 후속 진단이 실패 수집기·보정안을 소비하고 결과 처분 또는 명시적 중단 뒤 용도를 다시 판단한다. 삭제: 결과 보존이 완료된 단회 정책 preflight 스크립트 1개. active 경로 변경 0. 빈 scratch는 구체적인 다음 단회 검사에서 사용할 경로로 유지한다. 기존 worktree는 A/B–D 및 H10 품질 판정에 계속 필요하다. 이번 승인 amendment와 과거 실행/리뷰 기록은 수정하지 않았다.


### Owner Approval For Single Auth Recheck — 2026-10-26

Owner는 준비된 단회 auth 재확인과 성공 시 기존 A 계속 진행을 “승인”했다. 승인 시각 `2026-10-26T08:07:30.879168+00:00`, exact runner SHA-256 `af4f833d2c92c928d2cca399321721175e40bdec77a672d615a82a12dd85a0fa`다. 같은 pinned CLI/`--safe-mode auth status`를 1회만 호출하고 기존 사용자 세션 환경 이름 4개를 추가 상속한다. 명령 상한 30초, 진단 예상 2–5분/누적 상한 10분, 종료 `2026-10-26T08:17:30.879168+00:00`이며 기존 A/20시간 잔여에서 차감한다. 최초 실패와 사용 횟수는 보존한다.

시작 잔여 A 9538.082초/전체 67553.844초다. 성공하면 exact 환경을 고정해 A를 계속하고 실패하면 login/추가 retry 없이 Hold한다. 모델/새 인증 경로·계정/과금/전역 설정 변경 권한은 추가하지 않는다. 새 A 판별 종료 `2026-10-26T10:31:28.961168+00:00`, 정리 포함 종료 `2026-10-26T10:46:28.961168+00:00`는 Owner 전용 대기를 제외해 남은 활동 한도를 옮긴 값이며 새 예산이 아니다.


### Single Auth Recheck Passed And A Continued — 2026-10-26

승인한 단회 auth 재확인은 2026-10-26T08:08:21.450903+00:00에 0.094초/exit 0으로 완료했다. loggedIn true, claude.ai/firstParty/pro, configDirectory 예상 경로 일치, stderr 0, process group 부재다. stdout은 392 bytes였으며 비밀 없는 네 인증 필드와 경로 일치 여부만 보존했다. 모델 입력/login/key 발급은 없었다. non-model 누적은 Claude 전체 3/12, A 3/6이며 단회 재확인 1/1을 소비했다.

이 결과는 기존 사용자 세션 환경 이름 네 개를 포함한 exact 환경에서 인증이 동작함을 확인한다. 각 변수의 개별 인과나 첫 실패 응답 내용을 소급 단정하지 않는다. 승인된 성공 후 계속 진행 조건에 따라 이 환경을 고정하고 A를 이어간다. 시간은 재확인 승인 시점부터 연속 계상하며 다시 A를 초기화하지 않는다.

다음 좁은 검사는 model 입력 없는 CLI initialize/MCP status다. 같은 argv template의 safe-mode/strict MCP/dontAsk/max-turns 조합과 read/verify 두 schema를 고정한다. 공식 Python SDK의 control-message 형식을 참고하되 SDK 설치나 generic wrapper를 만들지 않는다. task-local relay는 schema 조회만 응답하고 모든 효과 요청은 거절하며 authority/journal/worker 권한을 갖지 않는다. native 시작 1회를 non-model pool에서 먼저 예약하고 일반 case 5분 안에 종료한다. init과 MCP status만 전송하며 user/model prompt는 0이다. 조합이 미지원/불명확하면 옵션을 제거하거나 mode를 바꾸지 않고 Hold한다. 이 검사는 live stop/worker/Go 증거를 대신하지 않는다.


### Native Initialize Hold And Prepared Configuration Correction — 2026-10-26

인증 재확인은 통과했으나 이어진 비모델 초기화는 고정 argv 조합이 MCP를 노출하지 못해 Hold했다. Driver가 준비한 `--safe-mode`와 명시적 MCP의 조합이 이번 환경에서 적합하지 않았다. 이 실패를 모델 가용성이나 Sonnet 품질 문제로 분류하지 않는다.

실행 시작 `2026-10-26T08:18:15.042759+00:00`, 종료 `2026-10-26T08:18:17.396912+00:00`, 2.354초다. initialize는 성공했으나 같은 프로세스 안의 MCP status 3회가 모두 빈 목록이었다. relay 시작/스키마 조회는 관측되지 않았다. user/model 입력 0, 도구 요청 0, 업무 효과 0이다. Host가 살아 있는 CLI에 TERM을 보내 exit 143으로 종료했고 소유 group/관측 descendant 부재를 확인했다. 이는 비모델 검사 정리이며 필수 live Host-stop 검증을 대신하지 않는다.

Claude non-model 누적은 전체 4/12, A 4/6이다. worker live starts, Host steps, bridge requests/effects, focused batches, 미래 R1은 모두 0이다. argv가 초기화 단계에서 수용됐다는 사실만으로 max-turns의 runtime 의미나 실제 모델 identity를 입증하지 않는다. pinned help는 safe-mode가 MCP를 비활성화한다고 명시하고, 이번 관측에서도 explicit MCP가 이를 되살리지 못했다. 실패 뒤 추가 CLI 호출이나 자동 mode 변경은 하지 않았다.

#### Concrete Pending Correction

원 amendment bytes를 수정하지 않고, 이번 profile의 고정 argv에 대한 좁은 예외를 제안한다. `--safe-mode`를 제거하고 `--settings '{"disableAllHooks":true,"autoMemoryEnabled":false,"disableClaudeAiConnectors":true}'`를 추가하며, 빈 설정 source를 SDK와 같은 `--setting-sources=` 형식으로 전달한다. 나머지 pinned binary/model/medium 요청, 인증 성공 환경, built-in tools 제거, slash-command 비활성화, strict MCP/read·verify allowlist, dontAsk, permission prompts none, no Chrome, no session persistence, 고정 system prompt와 max-turns를 유지한다. managed 정책 부재 gate와 Host의 모든 효과 거절도 유지한다. API key 또는 bare/simple 모드로 전환하지 않는다.

근거: [공식 feature 문서](https://code.claude.com/docs/en/agent-sdk/claude-code-features)는 빈 settingSources의 범위와 별도 auto-memory/connector 차단을 설명한다. [hook 문서](https://code.claude.com/docs/en/hooks#disable-or-remove-hooks)는 단회 inline disableAllHooks와 managed 정책 예외를 설명한다. [공식 SDK CLI 구성](https://raw.githubusercontent.com/anthropics/claude-agent-sdk-python/main/src/claude_agent_sdk/_internal/transport/subprocess_cli.py)은 빈 sources를 위 argv로 전달한다. global config와 native auth 내부는 기존 승인한 trust 범위다. 이 문서 근거는 후보 선정 근거이며 실제 ambient plugin/skill/명령 부재나 전체 입력 동등성 검증을 대체하지 않는다. 필요한 inventory를 확인할 수 없으면 A는 계속 Hold다.

실행 후보는 기존 task artifact의 `native-cli-resume/native-init-probe/probe-recovery.py`이며 승인 flag가 false인 상태에서는 시작할 수 없다. exact argv, inline settings, source/relay/CLI digest를 기존 execution.json에 고정했다. 원 실패 probe는 바꾸지 않았다. 동일 프로세스 안에서 initialize 1회와 MCP readiness 최대 3회를 관측하고 관측 사이 5초를 둔다. native 시작은 남은 A non-model 2회 중 1회만 소비한다. process 상한 300초(TERM/KILL 정리 포함), 준비·검사·기록 포함 예상 3–8분/누적 중단 한도 15분이다. 예상은 직전 초기화 2.354초와 수동 확인 작업에 대한 판단이며 연결 지연은 미측정이다. 이 구간의 대기·겹친 작업은 wall-clock으로 한 번만 계상하고 Owner 답변 전용 대기만 제외한다. 기존 A와 20시간 잔여에서 차감하며 새 예산은 없다.

통과하면 설정 admission만 통과한 것이다. 기존 A의 ambient inventory·실제 Sonnet identity·효과 gate·live Host stop·negative/fresh 재개를 남은 한도 안에서 이어가고, 원 Go를 모두 충족한 뒤에만 기존 승인된 B–D로 진행한다. 실패/unknown이면 Hold하며 두 번째 설정 시도나 추가 mode fallback은 없다. 이 보정은 새 공통 권한/효과 완화나 추가 R0/R1 제안이 아니다. 추가 모델 요청은 이 비모델 진단에는 없고, 성공 후 원 A 권한 범위에서만 가능하다.

원 승인안이 조합 실패 시 임의 option 제거/mode 변경 없이 Hold하도록 정했으므로, 이 구체적 argv 교정과 Hold 뒤 재개에 대한 Owner 결정이 필요하다. 기존 source 구현/commit/push/계정·과금 변경/최종 수락 권한을 새로 부여하지 않는다.

준비된 recovery runner SHA-256 `b92b33953ab37f188d07967aafe2df3546becf711639f72b81366fcb9c965292`. syntax compile만 확인했으며 실행하지 않았다.

#### Native Init Closeout

2026-10-26T08:30:23.562657+00:00까지 auth 재확인 승인 이후 진단·A 초기화·후보 준비·정리 활동 1372.683초(22.88분)를 연속 계상했다. A 잔여 8165.399초(136.09분), 전체 잔여 66181.161초(18.384시간)이며 마지막 A 15분/전체 30분 정리 예약을 유지한다. 앞선 auth 재확인 자체는 08:13:27에 처분하여 별도 10분 한도 안에 끝났고, 성공 후 A 계속 진행 시간은 같은 A/20시간 잔여에서 계상했다. 지금부터 Owner 결정만 기다리는 구간은 활동 예산에서 제외한다.

검사: Core managed 30파일·구현 입력 7개·승인 plan/amendment·과거 고정 기록 무변경, 새 runner syntax/digest 및 미실행 상태, git diff check를 확인했다. 변경은 Work/진단 기록과 미실행 검사 후보에 한정해 full suite/runtime 반복은 하지 않았다. GFM/링크 검사는 이 추가 구간을 대상으로 마감한다.

보존: 이 Work와 execution.json의 관측·계수, 원 native-init 실패 probe와 relay, 준비한 단회 recovery runner. 소비자는 다음 Owner 결정과 A의 설정 비교이며 회복 처분/명시적 중단 때 용도를 다시 판단한다. scratch는 구체적인 다음 검사에 쓸 task-local 경로다. 삭제: 용도가 끝난 auth 진단 runner 2개와 닫힌 FIFO 2개. active 경로 변경 0이며 다음 후보 입력만 추가했다. source/runtime/control worktree는 기존 A/B–D 및 미완료 H10 품질 판정에 필요해 유지했다. Work Active와 Core/U1 수락을 유지하며 자동 재개하지 않는다.


### Owner Approval For Single Native Configuration Correction — 2026-10-26

Owner가 직전 구체 보정 1회와 통과 시 기존 A 재개를 “승인”했다. 승인 시각 `2026-10-26T08:32:48.927776+00:00`, runner SHA-256 `b92b33953ab37f188d07967aafe2df3546becf711639f72b81366fcb9c965292`다. safe-mode를 개별 설정 차단으로 교체한 exact argv와 1회/300초 process 상한을 적용한다. 진단 예상 3–8분, 준비·관측·기록 누적 상한 15분이며 종료 시각 `2026-10-26T08:47:48.927776+00:00`다. A 잔여 8165.399초, 전체 잔여 66181.161초와 모든 기존 계수를 승계한다. Owner 전용 대기만 제외하며 예산은 늘리지 않는다.

통과하면 설정 admission 결과를 기록하고 원 A 필수 검증을 이어간다. 실패/unknown이면 추가 시도 없이 Hold한다. 모델 입력 없는 이번 probe가 실제 Sonnet identity/ambient 입력 부재/live Host stop/negative·fresh 재개를 대신하지 않는다. B–D는 원 Go 뒤에만 진행하며 commit/push/새 인증·과금/최종 수락은 포함하지 않는다.


### Native Configuration Admission Passed; A Continued — 2026-10-26

승인된 단회 보정은 2026-10-26T08:33:40.551125+00:00 시작, 2026-10-26T08:33:45.864304+00:00 종료, 5.312초에 통과했다. 첫 MCP status는 colvia pending, 다음은 connected였고 u2_read_file/u2_verify 두 schema와 relay의 tools-list 관측이 일치했다. model prompt와 도구 실행 0, Host TERM 후 전체 소유 group/descendant 부재다. exact 실행 argv와 승인 proposal argv 일치를 확인했다. non-model starts는 전체 5/12, A 5/6이며 이 보정 1/1은 소비 완료다.

설정 admission에 한정한 PASS다. 실제 Sonnet identity, 모든 ambient 입력 배제, Host 효과/거절, live stop와 Core fresh 재개는 아직 미검증이다. 승인한 성공 후 계속 진행 조건에 따라 작은 task-local Host bridge 및 offline 최초 집중 batch를 준비한다. live 시작 전 full argv/schema/합성 입력과 negative 변환을 고정하고 필수 gate를 확인한다. 남은 A 시간/계수는 같은 구간에서 연속 계상하며 재승인이나 새 예산을 만들지 않는다.


### A First Focused Batch Selection — 2026-10-26

Core30 무변경 증거와 기존 worker profile/parser를 재사용하고, 새 얇은 guard 및 현재 worker 읽기 경로만 검사한다. 최초 batch 1/3을 2026-10-26T08:58:10.605645+00:00에 예약했다. 계획 digest `2c1b8d116f86dfbeb41c63a0e8008816ce3a48846b25e69113920e23c68bff71`, 예상 3–8분/누적 상한 30분이다. native/model 0, 합성 Core CLI 최대 11개와 sandbox worker 2개, simulated turn 최대 12/dispatch 11을 예약한다. 새 root에 continuation-1 합성 fixture 하나만 만들며 init·guide-review intent/Work 수락·후속 proposal의 exact prepare ticket을 각 apply 전에 task-local evidence에 보존한다. 실제 adopter authority는 접근하지 않는다.

검사 대상은 허용 read/result 결속, actor/result/scope 거절, fresh guard의 중복 거절, budget/fsync 실패, 동시 slot 1개, stop/revoke 뒤 거절, missing/partial recovery다. full Core suite나 runtime build는 하지 않는다. 과거 worker digest와 현재 승인 입력이 달라 과거 worker PASS를 그대로 상속하지 않고 현재 입력으로 실제 read 2건을 검사한다. batch 실패 시 실제 실패를 보존하고 자동 재실행하지 않는다.


### A Offline PASS And Fixed Live Qualification — 2026-10-26

최초 batch는 08:58:14.327689Z–08:58:24.991004Z, 약 10.66초에 10개 항목을 통과했다. 합성 Core CLI 11개, sandbox worker 2개, simulated dispatch 11개를 실제 관측했고 native/model은 0이다. source Core30은 그대로이며 fixture는 실제 설치된 continuation-1 제품 검증을 통과했다. 수락된 guide-review Work와 미실행 후속 proposal, pending 없음이 현재 Core 상태다. fake runtime이나 mock Core를 설치 성공으로 바꾸지 않았다.

Live 입력을 고정했다. plan SHA-256 `074b3205303bb939d930a27f0802ccab65bde2d841a39b9854752bdda708376e`, runner SHA-256 `2460f6834a334246cc138899c1a3d5a84aaa8b43a130f984a22d6ab3603a5520`. 기존 A 권한으로 마지막 non-model auth 1회(30초)를 먼저 사용한 뒤 최대 live starts 2/Host steps 4/bridge requests 4를 사용한다. 첫 세션은 read 성공과 고정 scope 변환 거절, Host가 살아 있는 process를 종료한 다음 두 번째 새 세션은 Core 및 누적 journal에서 재개하여 read 성공과 소비한 call ID 변환 거절을 관측한다. 변환은 실제 native 요청이 지난 relay→Host 경로에만 적용하고 원문·변환·시점을 기록한다. 모델이 negative를 생성했다고 주장하지 않는다.

각 step 효과 전 CLI system init의 exact model/session/tools/skills/plugins/commands/permission과 실제 AssistantMessage model을 대조하고, assistant tool-use ID·name·arguments를 MCP request와 결속한다. 공식 기본 agent catalog 이름만 metadata로 허용하되 Agent 도구와 실행은 계속 제외한다. 이는 사용자 custom agent 허용이 아니다. 사용량 경고·한도, extra call, 알 수 없는 입력/설정/모델은 Hold다. firstParty/pro auth 확인을 이 연속 qualification의 두 세션에 공통으로 고정하고, 각 세션 시작 전 auth/provider override와 관리 정책 부재를 재확인한다.

worker·guard·Core snapshot·schema·relay·pinned CLI·네 prompt·session IDs를 실행 전에 고정했다. fresh prompt는 Core와 직전 결과/누적 사용량/pending의 결정적 조합으로 두 번째 native start 전에 bytes를 보존한다. 기존 CLI transcript/resume는 사용하지 않는다. process 30분/step 15분, TERM10+KILL10과 A 마지막 15분 정리 한도가 먼저 적용된다. live 예상은 미측정이므로 원 A의 낮은 신뢰도 추정을 유지하며, 성공해도 Go audit 전 B를 시작하지 않는다.


### A First Live Framing Failure And Hold — 2026-10-26

개별 설정 차단/MCP admission과 최초 offline guard batch는 통과했다. 첫 live 세션은 Driver 수집기가 미지원 메시지 유형을 처리하지 못해 중단했다. 이 결과는 Sonnet 응답/도구 수행 실패를 입증하지 않는다. 원 실행의 최초 실패 중단 규칙에 따라 추가 auth/live 호출·fallback·B 진입은 하지 않았다.

| 항목 | 관측 및 한계 |
| --- | --- |
| 직전 인증 | 09:06:46.787837Z, claude.ai/firstParty/pro, exit 0, stderr 0, process group 부재. non-model A 6/6·전체 6/12 소비 |
| live 초기화 | 09:06:47.350420Z 시작. default output style, custom commands 0. 공식 기본 agent catalog 이름 5개만 표시됐고 Agent 도구는 제거된 구성이다. 고정 MCP 연결과 read/verify 두 schema 확인 |
| Host 입력 | 09:06:52.778790Z에 합성 입력 1개 제출. live A 1/2·전체 1/4, Host step A 1/4·전체 1/8 소비 |
| 실패 | `unknown-native-message-type`. system init/AssistantMessage 보존 전 실패했고 bridge 요청·worker 실행·업무 효과 모두 0. CLI 내부 실제 model send 수와 모델 identity는 미관측 |
| 수집기 결함 | unknown 분기가 type 값·header keys·frame digest를 보존하지 않고 예외를 냈다. 원 메시지 유형과 무해 여부는 현재 증거에서 복구/확정할 수 없다. 빈 safe_events가 CLI 무응답을 뜻하지 않는다 |
| 종료 | 살아 있는 CLI에 Host TERM, 09:06:53.111405Z exit 143, stderr 0. CLI·relay 소유 group/관측 descendant 부재, 별도 ps 재확인에서도 부재 |
| 필수 검증 | live 정상 read·negative·두 step 뒤 stop·Core fresh-reader는 미관측. 이번 정리만으로 그 기준을 통과시키지 않는다 |

[공식 SDK parser](https://raw.githubusercontent.com/anthropics/claude-agent-sdk-python/main/src/claude_agent_sdk/_internal/message_parser.py)의 미지원 type 무시 처리는 다음 수집기의 참고다. 사라진 이번 frame이 무해했다는 증거나 현재 고정 실행에서 unknown을 자동 허용할 근거는 아니다. 다음 후보는 분류 전에 제한된 type/subtype/key 이름·순서·길이·digest·session 일치 여부를 보존해야 한다. raw account/auth/body 저장이나 unknown control/effect 허용은 포함하지 않는다. 실패 runner bytes는 수정하지 않았고 재실행하지 않았다.

남은 A live start 1회/non-model 0회로는 정상 세션 2 step → 실제 stop → fresh 세션 2 step이라는 기존 필수 경로를 충족할 수 없다. C 배정 전용·추가 start·검사 축소·시간 초기화는 하지 않는다. 후속 실행 결정에는 수집기 관측 보정과 정상/fresh 경로에 필요한 횟수 재배정이 함께 필요하다. 현재 자동 재개 권한은 없으며 근거 없는 개별 retry 제안은 만들지 않는다.

#### Qualification Closeout

2026-10-26T09:13:30.157289+00:00까지 이번 승인 이후 활동 2441.230초(40.69분)를 계상했다. A 잔여 5724.169초(95.40분), 전체 잔여 63739.931초(17.706시간)다. 시간은 남았지만 start 한도로 계속할 수 없다. A 마지막 900초/전체 마지막 1800초 정리 예약을 유지하며 Owner 전용 대기만 제외한다.

Core30·구현 입력7·승인 plan/amendment·과거 고정 기록 무변경, exact live runner/plan digest, 소유 프로세스 부재를 확인했다. source 구현 변경 없이 task-local probe/guard만 추가했다. focused batch 1/3, simulated dispatch 11/12, reserved simulated turn 12/12이며 추가 batch/R1은 0이다. authority rollback/replay는 없다.

보존: exact admission 및 live 스크립트·guard·Core fixture·offline 결과·journal·계수. 소비자는 Owner의 실패 처분과 다음 Driver/R1의 구성·실패 대조다. 해당 결정/근거 사용이 끝나면 용도를 다시 판단한다. 자동 승인 검토가 진단 스크립트 2개 삭제를 거절했다. digest/기록만으로 원본 bytes가 복구되지 않는다는 이유이며 거절된 명령은 실행되지 않았다. 안전한 대안으로 모든 스크립트 원본을 보존했다. 실제 삭제는 종료를 확인한 FIFO 4개만이다. active 경로 변경 0. source/runtime/control worktree는 A/B–D 및 H10 품질 판정에 계속 필요하다. Core/U1 수락·Work Active를 유지하고 A는 Hold다.


### Owner Approval For Collector Recovery And Reallocation — 2026-10-26

Owner는 “승인. 계속해”로 수집기 보정과 실행 횟수 재배정을 승인했다(2026-10-26T09:18:03.415160Z). 이전 실패 입력·결과와 사용량을 보존하고 새 live-recovery 후보를 별도로 고정했다. 내용 없는 keep_alive envelope만 무효과 알림으로 처리하며, JSON 파싱 뒤 메시지 분류 전에 유형·subtype·필드 이름·순서·크기·해시·session 일치 여부를 fsync한다. auth/account 원문과 알 수 없는 payload는 저장하지 않는다. 미지원 메시지·제어/효과 요청은 계속 거절한다. 이 보정은 유실된 첫 frame의 유형을 소급 확인하지 않는다.

전체 한도(non-model 12/live 4/Host step 8)와 20시간을 유지하면서 A 배정을 non-model 6→7/live 2→3/Host step 4→5로 변경했다. 이미 사용한 6/1/1은 유지해 추가 auth 1회와 정상·fresh 두 세션/네 step을 확보한다. bridge/effect 각 4와 모든 필수 검증은 유지한다. 전부 수행한 뒤 C 잔여는 live 1/step 3이므로, Go audit에서 재사용 가능한 동등 증거와 B–D 가능성을 확인하며 부족하면 Hold한다. 재배정은 검증 면제가 아니다.

수집기 보정·집중 검사·live 관측·기록 예상 활동 15–30분은 수동 작업 판단이며 live latency는 미측정이다. 대기와 겹친 작업은 wall-clock으로 한 번만 계상한다. A 잔여 5724.169초/전체 63739.931초에서 09:18:03 이후 활동을 차감하며 마지막 A 900초/전체 1800초 정리 예약을 유지한다. 기존 guard·worker·Core·offline 10개 증거는 변경 없이 재사용하고, 수집기만 두 번째 집중 batch에서 검사한다. 실패 시 새 호출 없이 Hold한다. source 구현/commit/push/최종 수락 경계는 그대로다.


### Collector Recovery Result And Concrete Lifecycle Candidate — 2026-10-26

수집기 보정 검사는 8/8 통과했으나 새 live는 command_lifecycle frame을 만나 Hold했다. CLI 시작 09:25:37.951327Z, stdout sequence 8, 197 bytes, type/command_uuid/state/uuid/session_id 필드와 session 일치, SHA-256 69df495fbebee5a3963375100a7cdd3aeee1729ed61e824d4ddf4c2226576c30을 분류 전에 보존했다. state/command_uuid 값은 projection에 없으므로 queued/started나 Host UUID 일치를 소급 단정하지 않는다. 첫 실패의 유실 frame이 같은 유형이었다는 증거도 없다.

auth는 claude.ai/firstParty/pro로 통과했고 첫 Host 입력 뒤 효과 전에 중단됐다. 이번 추가 live 1/Host 입력 1/bridge 요청 0/효과 0이다. 종료 09:25:43.908791Z, Host TERM exit 143, stderr 0, 전체 소유 group/관측 descendant 부재를 확인했다. actual model identity와 내부 model send 수는 unknown이며 Sonnet 실패로 판단하지 않는다. 정상 두 step 후 stop/fresh는 미완료다.

[공식 SDK 변경 기록](https://github.com/anthropics/claude-agent-sdk-typescript/blob/main/CHANGELOG.md)과 추가 실행 없이 읽은 pinned CLI 2.1.310 schema가 command_lifecycle을 UUID 입력의 처리 상태 알림으로 설명한다. 이는 정적 protocol 근거이며 live 보장을 대신하지 않는다. schema 발췌는 qualification/command-lifecycle-schema.txt에 보존했다.

준비한 lifecycle-recovery.py는 exact 다섯 필드, 동일 session, 이미 제출한 현재/직전 Host 입력 UUID를 확인한다. queued/started/completed는 알림으로만 기록하고 Host step 완료/효과 권한으로 사용하지 않는다. cancelled/discarded/refused, unknown UUID/state, wakeup/추가 필드는 중단한다. 늦게 온 직전 입력 completed도 그 입력에만 연결한다. 나머지 model/inventory/guard/worker/Core/negative/stop/fresh 조건은 유지한다. 기존 마지막 집중 batch 3/3에서 pure 9/9를 통과했다(native/model/Core/worker 0). 후보 native 실행은 승인 hash gate가 없어 금지돼 있다.

#### Proposed Cumulative Allocation

현재 배정으로 A를 다시 완주하면 C의 필수 두 세션을 남길 수 없다. A 증거 재사용을 성공으로 가정하지 않고 다음 묶음을 제안한다. 아직 적용하지 않았다.

| 계수 | 현재 사용 / 현재 전체 한도 | 제안 전체 한도 / A 한도 | 목적 |
| --- | --- | --- | --- |
| Claude live starts | 2 / 4 | 6 / 4 | A 추가 정상+fresh 2, C 기본 2 |
| Claude Host steps | 2 / 8 | 10 / 6 | A 추가 4, C 기본 4 |
| Claude non-model starts | 7 / 12 | 12 유지 / 8 | A auth 1, 이후 C 잔여 4 |
| 집중 batch | 3 / 3 | 5 | 통과한 보정 검사를 재사용하고 B–D 2 확보 |
| bridge 요청/효과 | 각각 0 / 8 | 전체 8/A 4 유지 | 효과 범위 확대 없음 |
| future R1 | 0 / 2 | 2 유지 | 추가 reviewer 없음 |

후보 plan SHA-256 f214538ac5531e4db7fee742fac6f1b237d8d9bece833bac4d6a37977e5b6459. exact 후보와 proposed_limits를 준비했지만 현재 execution limits는 바꾸지 않았다. 승인 시 auth 1/정상+fresh 2세션/4 step만 실행하고, 원 A Go와 B–D 잔여 가능성을 확인한 뒤 기존 승인 B–D를 이어간다. 다음 A 실패/unknown은 Hold이며 자동 재시도나 mode fallback은 없다.

다음 A 예상 활동 20–40분은 고정 확인·live·기록을 포함한 판단 추정이다. 정상 live latency를 아직 관측하지 못해 불확실성이 크다. B–D 기존 예상 8–14시간은 A Go 때 재추정한다. 전체 20시간과 A 원 180분/현재 잔여를 늘리지 않고 Owner 전용 대기만 제외한다. native 30분/step 15분은 겹쳐 계산하며 단계 잔여와 종료 예약이 우선한다. 계정/과금·Core authority·commit/push·최종 수락은 추가하지 않는다.

#### Collector Recovery Preservation

Core managed 30파일, 구현 입력 7개, 승인 parent/amendment와 과거 고정 기록, 원/보정 입력 digest 무변경을 확인했다. closeout 스크립트가 최초 metadata entry 객체를 문자열 hash와 비교해 assertion으로 중단했으며 실제 drift는 없었다. 객체의 sha256 필드로 대조를 고쳐 확인했다. 최초 assertion은 쓰기/삭제 전에 발생해 부수 효과가 없었다.

원 guard/worker/Core가 바뀌지 않아 offline 10개 증거를 재사용했고 full suite/build는 반복하지 않았다. 두 실패 source/metadata, 국소 검사, pending 후보는 Owner·다음 Driver·R1 비교에 필요해 유지한다. 삭제는 이번 닫힌 FIFO 2개뿐이며 active 경로 변경은 없다. source/runtime/control worktree는 A–D/H10에 계속 필요하며 처분/소비 종료 뒤 재평가한다.

마감 2026-10-26T09:33:29.418584+00:00: 이번 활동 926.003초, A 잔여 4798.166초, 전체 잔여 62813.928초(누적 사용 9186.072초). 마지막 A 900초/전체 1800초 예약 유지. Owner 결정 전 자동 재개하지 않는다.

최종 기록 확인 2026-10-26T09:34:33.492145+00:00: GFM render/강조·whitespace/git diff check와 required source 가독성 PASS. 위 마감 뒤 검증 시간까지 포함한 A 잔여 4734.092초/전체 잔여 62749.854초, 이번 활동 990.077초다. 이 지점 이후 Owner 전용 대기는 제외한다.


### Owner Approval For Lifecycle Recovery — 2026-10-26

Owner가 2026-10-26T10:04:47.569027Z에 직전 보정·한도 묶음을 승인했다. plan SHA-256 f214538ac5531e4db7fee742fac6f1b237d8d9bece833bac4d6a37977e5b6459와 기존 원본은 바꾸지 않고 실행 기록의 승인 hash gate를 활성화했다. Claude 전체 live 6/A 4, Host step 10/A 6, non-model 전체 12 유지/A 8, 집중 batch 5를 적용한다. 기존 사용 non-model 7/live 2/Host step 2/batch 3은 그대로다. bridge/effect, R1, 전체 20시간과 A 원 180분은 유지한다.

통과한 pure lifecycle 9개와 guard offline 10개 증거를 재사용한다. 이번 auth 1/정상+fresh 2세션/4 step 후 모든 원 Go 및 잔여 가능성을 확인해야 B–D로 이어간다. 최초 실패/unknown은 다시 Hold한다. A 잔여 4734.092초/전체 62749.854초에서 승인 이후 활동을 차감한다. A 판별 종료 2026-10-26T11:08:41.661027+00:00, 정리 포함 종료 2026-10-26T11:23:41.661027+00:00이며 Owner 전용 대기만 옮긴 값이다. 예상 다음 A 활동 20–40분의 불확실성을 유지한다.


### Lifecycle Passed; Builtin Plugin Inventory Hold — 2026-10-26

승인한 lifecycle 후보를 그대로 실행했다. auth는 기존 claude.ai/firstParty/pro 경로로 통과했고, 10:05:34.602668Z에 native를 시작했다. 첫 Host 입력의 command_lifecycle queued/started가 exact 입력 UUID에 결속돼 처리됐고 system/init까지 도달했다. 수집기 lifecycle 보정은 이 구간에서 관측됐다.

system/init은 model claude-sonnet-5-5, tools read/verify 두 개, skills/slash_commands 빈 목록, dontAsk를 보고했다. 그러나 plugins에는 cc-plugin-agents-md@builtin 및 cc-plugin-plugin-authoring@builtin 두 개가 있었다. 빈 plugin 목록을 요구한 원 gate가 ambient-customization-inventory로 중단했다. init 모델명은 실제 assistant 응답 model metadata를 대신하지 않으며 후자는 미관측이다. plugin 목록 존재만으로 hook 실행이나 실제 데이터 전송을 단정하지 않는다.

이번 live 1/Host 입력 1 추가, bridge 요청/효과 0이다. 10:05:40.409914Z Host TERM exit 143, stderr 0, 소유 group/관측 descendant 3개 부재를 확인했다. 최초 실패 후 재시도하지 않았다. 현재 누적 Claude non-model 8/12(A 8/8), live 3/6(A 3/4), Host 입력 3/10(A 3/6), bridge/effect 0, batch 3/5, future R1 0/2다. 정상 두 step 후 stop/fresh는 아직 미완료다.

#### Concrete Session Plugin Suppression Candidate

추가 native 호출 없이 pinned 2.1.310의 enabledPlugins schema, builtin 선택 함수와 두 plugin 등록부를 확인했다. 일반 flag 설정 false가 builtin enabled 선택에 사용되는 코드 경로를 확인했지만 runtime 성공은 아직 검증하지 않았다. [공식 세션 설정 설명](https://code.claude.com/docs/en/settings#change-a-setting-for-one-session)은 --settings의 세션 범위를 설명한다.

plugin-recovery-plan.json은 기존 inline 설정에 아래 두 항목만 추가한다. 전역 설정·plugin 설치 상태·managed 정책은 수정하지 않고 기존 plugins==[] gate를 유지한다.

    {"enabledPlugins":{"cc-plugin-agents-md@builtin":false,"cc-plugin-plugin-authoring@builtin":false}}

후보 plan SHA-256 3847f85823d6d9eefb02a0b1b512cb713e781aa0f655dc0d6b23546b05542c3a. plugin-recovery.py의 event/pump/dispatch_ready/step/close AST가 통과한 lifecycle 후보와 동일하다. 변경은 단회 설정, 별도 evidence 경로/UUID, 승계 counter 및 승인 gate다. syntax·정적 비교를 확인했고 guard offline 10, framing 8, lifecycle 9 검사를 재사용한다. 새 focused batch는 소비하지 않았고 후보 native도 미실행이다.

#### Proposed Follow-Up Allocation

A 정상+fresh와 C 기본 2세션을 모두 남기려면 이번 실패 1회만큼 전체 시작/입력 한도 보정이 필요하다. 아래는 미적용 제안이다.

| 계수 | 현재 → 제안 | 향후 배정 |
| --- | --- | --- |
| Claude live 전체/A | 6/4 → 7/5 | 사용 3 + A 추가 2 + C 기본 2 |
| Claude Host 입력 전체/A | 10/6 → 11/7 | 사용 3 + A 추가 4 + C 기본 4 |
| Claude non-model 전체/A | 12/8 → 12/9 | A auth 1 추가, 이후 전체 잔여 3 |
| 집중 batch | 5 유지 | 사용 3, B–D 잔여 2 |
| bridge/effect, future R1 | 기존 유지 | 효과 권한·review 확대 없음 |

제안은 exact 두 plugin의 세션 한정 차단과 누적 한도를 함께 적용하는 것이다. auth 1 및 정상+fresh 2세션/4 step, 원 Go 뒤 기존 B–D로 이어가며 다음 실패/unknown은 Hold한다. 전체 20시간/A 원 180분·현재 잔여는 늘리지 않는다. 다음 A 예상 활동 15–35분은 고정 확인·live·기록의 판단 추정이며 정상 model latency는 미관측이다. native 30분/step 15분과 단계/전체 잔여 중 작은 한도, A 900초/전체 1800초 정리 예약을 유지한다. 대기·동시 활동은 한 번 계상하며 Owner 전용 대기만 제외한다. 계정/과금·실제 authority·commit/push·최종 수락 경계는 유지한다.

#### Lifecycle Hold Preservation

Core managed 30파일·구현 입력 7개·원 plan/amendment·과거 고정 기록과 후보 digest 무변경을 확인했다. source/fixture/tests/실패 입력·결과와 pending 후보는 Owner/다음 Driver/R1 비교용으로 유지한다. 실패 처분·소비 종료 뒤 용도를 재평가한다. 종료 확인된 이번 FIFO 2개만 삭제했고 active 경로 변경은 없다. 기존 source/runtime/control worktree는 A–D/H10에 필요하다. Work Active를 유지하며 자동 재개하지 않는다.

마감 2026-10-26T10:11:54.153246+00:00: 이번 활동 426.584초, A 잔여 4307.508초, 전체 잔여 62323.27초(총 사용 9676.73초). Owner 결정 전 Hold다.

최종 확인 2026-10-26T10:12:58.296509+00:00: GFM render/강조·whitespace/git diff check와 required source 가독성 PASS. 마감 뒤 검증까지 포함해 이번 활동 490.727초, A 잔여 4243.365초/전체 잔여 62259.127초다. 이후 Owner 전용 대기만 제외한다.


### Owner Approval For Session Plugin Suppression — 2026-10-26

Owner가 2026-10-26T10:15:24.800866Z에 두 builtin plugin의 세션 한정 비활성화와 누적 횟수 보정을 승인했다. exact plan SHA-256 3847f85823d6d9eefb02a0b1b512cb713e781aa0f655dc0d6b23546b05542c3a. 전체 Claude live 7/A 5, Host step 11/A 7, non-model 전체 12/A 9, 집중 batch 5를 적용하며 기존 사용 non-model 8/live 3/Host step 3/batch 3을 유지한다. effect guard·빈 plugin 목록·원 Go, 20시간/A 원 180분은 그대로다.

승인 시 A 잔여 4243.365초/전체 62259.127초다. 새 A 판별 종료 2026-10-26T11:11:08.165866+00:00, 정리 포함 종료 2026-10-26T11:26:08.165866+00:00는 Owner 전용 대기를 제외해 옮긴 값이다. 통과한 검사 재사용 뒤 auth 1/정상+fresh 2세션/4 step을 수행하고 최초 실패/unknown이면 Hold한다. 원 Go 충족 뒤 기존 B–D를 이어간다. 예상 15–35분과 모델 latency 미측정 한계를 유지한다.


### A Go Checkpoint And Authorized B Entry — 2026-10-26

A 최소 검증을 통과해 기존 승인 B–D로 이어간다. 이는 전체 U2 적격성 또는 Owner 수락이 아니다. exact setup은 plugin-recovery-plan SHA-256 3847f85823d6d9eefb02a0b1b512cb713e781aa0f655dc0d6b23546b05542c3a다. 승인한 단회 plugin 차단 뒤 실제 init의 plugins/skills/slash_commands가 비었고 read/verify 두 도구만 있었다. 네 step의 assistant metadata 모두 claude-sonnet-5-5였으며 native auth는 claude.ai/firstParty/pro다. medium은 요청값이고 effective effort는 unknown이다.

| 유지 조건 | 집행·관측 근거 |
| --- | --- |
| Core/identity/scope/result | guard가 고정 Core snapshot/identity를 효과 전에 재확인; 실제 installed 합성 fixture와 offline actor/result/scope 거절 통과 |
| 요청 예약·slot·fsync | hash-chain journal을 validation 전에 fsync; offline budget/fsync/concurrent/stop/revoke 거절 10개 통과; live 요청 4/효과 2 |
| native 요청 결속 | assistant call ID/tool/arguments를 relay 요청과 dispatch 전에 비교; 고정 Host fault injection의 원/변환 입력을 보존 |
| 실제 허용/거절 | 첫 read 성공 → file-scope 거절 → fresh read 성공 → duplicate-call 거절. 모델이 negative를 생성했다고 주장하지 않음 |
| Host stop/fresh | 첫 두 step 뒤 살아 있는 CLI에 TERM, 전체 group/관측 descendant 부재 후 새 session; journal 요청 2/효과 1 승계, 마지막 4/2, pending 없음 |
| U1 fresh-reader | accepted_work_state completed, follow_up_kind proposal, follow_up_execution_authorized false를 실제 fresh 응답에서 확인 |
| worker 경계 | 기존 DocumentController/worker/profile/parser 재사용, 실제 sandbox read 2회, Core30·구현7 무변경 |
| native trust 한계 | 내부 sends/retries/OAuth store 및 service policy/catalog은 미계측 unknown. 승인한 amendment의 명시적 경계이며 Codex 강화 계약으로 전용하지 않음 |

live 구간은 10:15:59.406879Z–10:16:31.101887Z 약 32초다. 두 세션 각각 Host stop/부재를 확인했고 모든 native 결과가 success다. 이전 실패 및 사용량은 유지한다. Claude 누적 non-model 9/12, live 5/7, Host 입력 7/11, 요청 4/8, 효과 2/8, focused batch 3/5, future R1 0/2다. C에는 Claude live 2/Host 4/요청 4/non-model 3이 남고 Codex 새 lane은 미사용이다.

Go 시각 2026-10-26T10:21:04.018586+00:00, A 잔여 3904.147초, 전체 잔여 61919.909초다. B–D 예상 8–14시간은 원 판단 범위를 유지한다. 짧은 Claude live 실측만으로 source refactor/Codex materialization/품질 확인 시간을 축소하지 않는다. 정상 경로에 필요한 C 양 도구 실행, focused batch 2와 R1 최대 2를 확보했고 추가 실패가 예산을 소진하면 Hold한다. C 예산은 A 증거 재사용을 미리 성공으로 가정하지 않고 남겼다.

B는 공통 identity/효과/복구를 유지하면서 Codex protocol 경계를 adapter로 분리하고, 검증된 Claude profile을 작은 source adapter로 흡수한다. 예상 4–7시간/중단 상한 8시간이며 전체 잔여가 먼저 적용된다. Core managed 30파일과 기존 Rust/binary는 변경하지 않는다. source 변동을 모은 뒤 focused batch 1개, C/D에 1개를 남기는 계획이다. 기존 tests/evidence의 영향 없는 부분을 재사용하며 새로운 runtime/full suite/build는 기본 0이다.

원본 host/test/fixture/profile의 unique bytes를 이번 task의 b-adapter-separation/source-baseline에 검증 보존했다. 이 baseline은 scoped rollback과 R1 비교가 소비하며 종료 조건은 Owner 처분과 복구/비교 종료다. A 입력·결과·journal은 B 추출/C 재사용 판정/R1에 필요해 유지한다. 종료된 FIFO 4개만 정리했고 active 경로는 바꾸지 않았다. Work Active·최종 Owner 수락 경계를 유지한다.

### B Extraction Candidate And Focused Selection — 2026-10-26

공통 effect/worker/Core/recovery를 contracts.py로, Codex의 prepared RPC·native model/notification·과거 exact budget 정책을 adapters/codex.py로 분리했다. host.py는 기존 진입과 호환 이름을 유지한다. 기존 함수·클래스 71개 중 69개의 AST가 동일하다. Admission은 native 식별자를 공통 session/step/call로 변환하고, Acceptance는 adapter의 명시적 예산 식별자 대응을 사용한다. 기존 prepared 검증과 Codex budget 정책을 Claude에 전용하지 않는다.

Claude adapter/고정 read-verify relay와 공통 ReadOnlyHost는 A의 성공 경로에서 task별 경로·전역 상태를 제거한 source 후보다. 이 profile은 read/verify만 허용하며 authority accept/write 지원을 의미하지 않는다. exact config/Core/input 결속, hash-chain/fsync, 누적 사용량, unknown pending 거절, 실제 native stop 부재 확인을 source 경계에 둔다. 내부 native HTTP/OAuth 동작은 기존 승인 trust 한계로 유지한다. 새 source의 live 실행은 아직 없고 A의 성공을 새 candidate의 PASS로 재표시하지 않는다.

누적 변경 위험은 import/모듈 분리, native→logical identity 변환, Claude journal/복구·process 정리다. managed Core 30파일과 worker/profile은 변경하지 않는다. 기존 complete normal/parent-optimized anchor는 영향 없는 Core 근거로만 유지하며, 기존 Host의 이동한 69개 AST 동일성은 정적 재사용 근거다. 전체 Core matrix 재실행 대신 아래 변경 경로를 선택한다.

- 기존 U2 H01 admission, H04 single-use/acceptance, H05 recovery, H08 stop/cleanup, recovery observation 검사.
- 기존 DocumentV2Tests의 공통 document/import 소비 경로.
- 새 test_u2_adapters의 read-only 승인/거절·동시 slot·fsync·pending·fresh 복구·native frame/lifecycle/relay binding·cleanup 검사.

normal 집중 batch 1개를 사용한다. expected 30–180초는 in-process/mocked stdlib 검사에 대한 판단 추정이고 중단 상한은 1800초(마지막 20초 정리)다. 실제 test subprocess 예상 0이며 runtime/model/auth/network는 0이다. fixed test selection·source SHA·Python·Seatbelt 정책을 실행 전에 task artifact에 고정한다. 외부 경로 쓰기/credential/network/native CLI 접근을 허용하지 않는다. 도구별 offline 예약은 Codex simulated turn/dispatch 23/23, Claude 12/13이며 기존 A 12/11과 누적해 Claude 전체 24/24 안에 둔다. 실행 실패도 예약을 환급하지 않는다. 이 batch 뒤 전체 focused 4/5, C/D에는 1개가 남는다. 최초 실패에서 멈추고 실제 결과·영향·잔여 범위를 기록한다.

선택한 기존 Codex binary의 새 synthetic namespace 수용 여부는 별도 사전 확인 중이다. 과거 승인/parent journal에 고정된 runtime 정책을 발견했으며, Rust 변경·재빌드·과거 allocation 재사용은 이 단계가 승인하지 않는다. source 분리 검증과 새 runtime 실행 적격성을 구별한다.

### B Loader Hold And C Native Namespace Blocker — 2026-10-26

B source 후보는 보존했으나 검증 완료가 아니다. 집중 batch 4는 10:48:46.209788Z에 예약한 뒤 고정 CPython이 exit -6(SIGABRT)로 종료했다. 10:48:46.235051Z에 process group 부재를 확인했고 stdout/stderr는 각각 0 bytes, source 입력은 동일하다. collection/test start/result 파일은 생성되지 않았다. OS crash report의 task 소유 PID와 발생 시각이 일치하며 triggered frames는 dyld 초기화의 ignition_halt/boot_boot/CacheFinder다. Python 테스트 진입 전 실패로 판단하지만 정확한 denied operation·근본 원인은 확인하지 못했다. 좁힌 해당 PID의 로그에도 구체 원인은 없었다. 테스트 assertion 실패나 PASS로 기록하지 않는다.

사용량을 되돌리지 않는다. focused 4/5, Claude offline 예약 turn/dispatch 24/24, Codex offline 예약 23/23이며 이번 batch의 실제 collection/turn/dispatch는 관측되지 않았다. native runtime/model/auth 호출은 추가 0이다. Claude 기존 non-model 9/12, live 5/7, Host 입력 7/11, bridge 4/8, 효과 2/8, future R1 0/2를 유지한다. 자동 재실행·정책 확대는 하지 않았다.

별도 read-only C admission 조사에서 고정 Codex binary의 새 synthetic namespace 수용 불가를 확인했다. 실제 binary digest가 선택값과 같고, 조사한 native source도 해당 build의 보존된 source87 digest와 일치한다. native U2 버전 31–57은 exact 과거 parent/Owner binding과 고정 deadline을 요구한다. 가장 늦은 deadline도 2026-10-26T03:41:25Z로 만료됐다. earlier Direct 경로는 clock-only 또는 diagnostic 조건이며, 새 version은 거절한다. 현재 Python Host만 바꿔 이 native gate를 통과시킬 수 없다. 이는 source에 근거한 실행 전 Hold이고 새 native 실패 관측은 아니다. Rust 수정/build·과거 allocation/ticket 재사용·clock rollback·sender 조건 완화는 수행하지 않았다.

#### Concrete Recovery Proposal — Not Authorized

1. B loader 진단 후보는 기존 테스트 정책에 literal /usr/lib/dyld의 process-exec만 추가한다. file-read/write/network/credential/native CLI 범위는 더하지 않는다. 이것은 아직 검증하지 않은 가설이다. 같은 pinned Python의 입력 표시만 출력하는 30초 진단 1회를 수행하고 group 부재와 marker를 확인한 경우에만 기존 exact B 선택 검사를 진행한다. 실패하면 추가 후보/재시도 없이 Hold한다.
2. 실패한 batch 4를 유지하면서 전체 focused cap 5→6을 제안한다. batch 5는 위 진단+B 검사(최대 1800초, 정리 20초 포함), batch 6은 C/D용으로 남긴다. 실행되지 않은 batch 4의 offline 예약(Codex 23/23, Claude 12/13)을 이 복구에 명시적으로 재배정하는 Owner 결정이 필요하다. 실패 이력은 보존하고 도구별 전체 한도·기존 실행 사용량은 늘리거나 초기화하지 않는다.
3. Codex는 새 실행 namespace와 기존 native sender/auth/policy 보장을 함께 유지하는 구체 계약/source-diff 제안을 준비한다. 이 제안 작성은 실제 Rust 수정/build/model 호출·추가 리뷰를 포함하지 않으며, 필요한 변경·검사·시간을 다음 결정 대상으로 제시한다. 현재의 build 0 제외 조건은 그대로다.

복구+Codex 제안 준비의 예상 활동은 25–45분(판단 추정), 누적 중단 상한은 60분이다. 대기·문서화·정리를 포함하고 동시 활동을 중복 계상하지 않으며 기존 B 8시간/전체 20시간 잔여 안에서 수행한다. 새 runtime build의 시간을 포함한 완료 추정은 아니다. exact private recovery proposal SHA-256 7e56d4a3e52fc851e4458f1aabc1d3f22bf4461dc13449fb274c32fbc364d3bb. 아직 미승인이다.

10:56:21.984372Z 보존 checkpoint에서 B 활동 2117.966초/잔여 26682.034초, 전체 사용 12198.057초/잔여 59801.943초다. 기록·최종 확인이 끝날 때까지 활동 시간을 계속 더하고, 그 이후 Owner 전용 대기만 제외한다. B 후보·exact 테스트 입력·loader 증거·native eligibility·복구 제안을 기존 durable 경로에서 유지한다. 소비자는 다음 Driver/Owner/R1이며 종료 조건은 실패 처분과 검증/복구/리뷰 소비 종료다. source/runtime/control worktree는 기존 구체 후속에 필요해 유지한다. 이번에는 active 경로 변경·삭제가 없고 commit/push/설치/수락도 없다. Work는 Active/Hold다.

최종 보존 확인 2026-10-26T10:59:52.914429+00:00: Core 30파일·고정 B 입력 13개 동일, baseline 4개 가독성, source syntax/whitespace·git diff check, GFM render/강조 검사를 확인했다. 실제 테스트 실행 근거는 여전히 없다. B 활동 2328.896초/잔여 26471.104초, 전체 사용 12408.987초/잔여 59591.013초다. 이후 Owner 전용 대기만 제외한다.

### Approved B Loader Recovery Attempt — 2026-10-26

Owner가 2026-10-26T11:04:36.068319Z에 앞의 exact 복구 제안(7e56d4a3e52fc851e4458f1aabc1d3f22bf4461dc13449fb274c32fbc364d3bb)을 승인했다. focused cap 5→6을 적용하고 실패 batch 4를 유지하면서 batch 5에 미실행 offline 예약을 명시적으로 재배정했다. 과거 사용량·도구별 전체 한도와 실제 실행은 초기화하지 않았다. 재개 시 B 잔여 26471.104초/전체 59591.013초를 승계했고, 이번 복구/제안 준비는 승인 시점부터 최대 60분이다. 실제 Rust 수정/build/model 호출·추가 review는 승인하지 않았다.

승인한 loader 후보는 /usr/lib/dyld literal process-exec 한 항목만 추가한 정책이다. 11:05:53.941199Z–11:05:53.966938Z 단회 진단은 exit -6(SIGABRT), stdout/stderr 각각 0 bytes, marker 없음으로 실패했고 process group 부재를 확인했다. B 테스트는 시작하지 않았다. 추가 후보나 재시도를 하지 않는다. loader 실행 허용 가설은 해결책으로 확인되지 않았고 원인은 미확정이다.

focused 사용은 5/6이며 batch 6은 남아 있다. B 테스트 collection·실행은 여전히 0관측이고 Claude/Codex native/model 추가 사용도 0이다. 별도로 승인한 Codex 새 실행 계약/source-diff 제안은 read-only로 준비한다. 실패한 loader를 우회해 source 테스트나 native 실행을 시작하지 않는다.

### Codex New Execution Contract Proposal Prepared — 2026-10-26

승인된 준비 범위에서 새 실행 계약과 함수별 source-diff 제안을 private task artifact의 `b-adapter-separation/codex-new-execution-proposal.md`에 작성했다. 실제 Rust/adapter source 변경, build, 추가 review, native/model 호출은 하지 않았다. 선택 binary가 과거 승인·부모 journal·종료된 deadline에 결속되어 있어 새 실행을 받지 못한다는 소스 기반 Hold는 유지한다.

제안은 기존 1–57 계약을 보존하고 version 58 전용 읽기 계약을 추가하는 것이다. 현재 누적 기록의 잔여를 단회 배정하고, 새 template/activation·work/anchor·journal을 결속한다. 기존 sender/final headers·bytes, native auth read-only/retry 0, FD/peer/nonce 검증은 유지한다. Codex 새 live의 제안 부분 배정은 2 starts/4 turns/최대 6 sends/4 dispatch/4 controls이며 authority/recovery apply는 0이다. 이것을 H04/H05를 포함한 전체 적격성 대체 근거로 사용하지 않는다.

필요 변경은 native app-server 계약 진입부·journal 검증·launch/proxy 연결, Python Codex adapter, 선택 tests와 C materializer다. cargo test target compile 1회와 실행 binary build 1회가 필요하므로 기존 build 0 경계의 별도 결정이 필요하다. 새 offline 검사 2 batch 제안(총 cap 6→8)은 아직 활성화하지 않았다. 정확한 simulated turn/dispatch 추가 수와 실행 packet은 실제 구현 후 시작 전에 고정해야 한다. 과거 예약/실패 횟수는 환불하지 않는다.

구현·offline 검증·자료 준비의 예상 활동은 120–220분, 제안 중단 한도는 240분(마지막 20분 정리)이며 판단 추정이다. 기존 B/전체 잔여에서 차감하고 compile/검사 대기는 포함한다. 미해결 로더, C live, D 품질/R1은 포함하지 않는다. 원 B–D 8–14시간은 Rust build 없음이라는 전제가 깨졌으므로 현재 확정 전망으로 사용하지 않는다. 로더 실패를 먼저 처분하고 compile 실측으로 재산정해야 한다.

현재는 B tests 0, 새 Codex native/model 0, 실제 Rust edits/build 0이며 Hold다. 두 번째 loader 실패 이후 추가 진단·후보·재시도는 하지 않았다. 최종 완료/Owner 수락/commit/push/install/release를 선언하지 않는다.

### Approved Recovery And Proposal Closeout — 2026-10-26

정리 checkpoint 2026-10-26T11:20:13.198812+00:00. 이번 승인 이후 활동 937.130초, B 누적 3266.026초/잔여 25533.974초, 전체 누적 13346.117초/잔여 58653.883초다. 앞선 Owner 대기 구간은 제외했다. 예상 25–45분보다 짧은 이유는 loader 실패로 B 검사 batch가 시작하지 않았기 때문이며 검사 성능 개선을 뜻하지 않는다. 이후 Owner 결정 전용 대기는 활동 시간에서 제외한다.

새 제안 SHA-256 8cce1ee0b1f37ca3428c3af763ce934d60ef932547820c9035881928c3938f68. Core 30파일·B 고정 입력 13·baseline 4·native source·선택 binary 동일성을 확인했고, source syntax-only 및 문서 GFM 렌더/whitespace 검사도 통과했다. 이는 B 검사 실행 근거가 아니다. 실패 process groups 45553/57586 부재와 결과 파일 가독성을 확인했다.

보존: source/baseline, 실패 입력·runner·로그·결과, 새 제안 및 확인 기록. 소비자는 Owner의 실패 처분과 후속 B/C/R1이며 처분·복구·리뷰 소비자가 끝나면 재평가한다. 활성 경로 변경 없음. 삭제: 완료된 단회 loader-recovery-1의 비어 있는 home/scratch/failures 디렉터리 3개만 제거했다. 실패 로그·결과와 마지막 복구본은 유지했다. worktree는 구체적인 B/C 후속 구현·검증에 필요하여 유지한다.

현재 focused 5/6, 미래 R1 0/2이며 도구별 과거 사용·예약은 그대로다. 승인된 복구 시도와 별도 제안 준비는 종료했지만 B 및 전체 적격성은 Hold다. 추가 자동 실행은 없다.

### Root-Read Recovery Admission — 2026-10-26

Owner의 계속 요청 뒤 기존 근거를 대조했다. 두 번째 실패 PID57586의 dyld image UUID·binary digest·boot_boot+228이 과거 루트 directory open 실패 분기와 일치한다. 기존 성공 worker profile에는 literal / AND DIRECTORY의 file-read-data 규칙이 있고 B focused profile에는 없다. 현재 정확한 errno/거절 layer는 미관측이나 실패 지점과 누락 규칙의 직접 연관을 확인했다. 이 근거를 앞선 dyld process-exec 가설보다 우선한다.

Owner가 표시된 구체 범위에 “이 복구 범위 승인”으로 응답했다. 승인 기록 시각 2026-10-26T11:28:46.286547+00:00, exact proposal SHA-256 0bb352fc07482e246896603ab7f437760d0249427961453c8ceb0812cb2d64a9. failed profile은 유지하고 root directory 자체 read 한 항목만 추가한다. immediate entry 열거 가능성은 승인 노출이며 하위 내용/쓰기/network/mach/exec 확대는 없다. 진단 1회/30초, 성공 시에만 기존 고정 B 검사 1묶음/1800초(종료 20초 포함), 예상 8–20분/활동 상한 45분이다.

focused cap 6→7, 새 batch ID7, C/D 예약 ID6 유지, 실패4/5 유지. 미실행 offline 예약 Codex23/23·Claude12/13만 batch5에서 재배정하며 도구별 총량은 늘리지 않는다. 이번 준비 378.544초를 먼저 차감해 B 잔여 25155.430초, 전체 잔여 58275.339초로 시작한다. 새 실패는 보존 후 즉시 Hold하며 추가 후보/재시도는 없다. Rust/build/model/추가 reviewer는 이번 승인에 포함하지 않는다.

### Root-Read Recovery Result And Focused Failure — 2026-10-26

승인된 root-read 단회 진단은 exit0/정확한 python_entry 표시/stderr0/그룹 부재로 통과했다. 같은 정책으로 고정 B 검사를 시작했고 38개 수집 중 28개 실행, 27 pass/1 failure/0 error에서 fail-fast 종료했다. 남은 10개는 실행하지 않았다. 테스트의 실제 subprocess/model/auth/network 호출은 0이며 고정 입력 13개는 그대로다. 이는 로더 진입 해결 및 일부 focused 근거이고 B 전체 통과가 아니다.

실패는 test_relay_inventory_matches_existing_read_verify_schemas의 whole-object equality다. MCP relay는 name/description/inputSchema, Codex 함수 profile은 여기에 type=function과 다른 read 설명을 갖는다. 정적 AST literal 비교에서 두 도구 이름과 inputSchema는 정확히 같다. 제품 동작 차이가 확인된 실패로 표현하지 않는다. 자동 재시도·실제 소스 보정은 하지 않았다.

후속 후보는 이 테스트 하나만 두 형식에 맞춰 수정한다. 두 도구의 이름/순서·MCP field set·Codex function type·입력 스키마·MCP의 고정 설명·duplicate key 거절을 계속 검증한다. 통과 27개를 재사용하고 수정 1+미실행 10개만 검사한다. exact patch/plan/runner는 private task artifact에 준비했으며 미적용/미실행이다.

제안 SHA-256 84773adaa95c34bde7c3a41066c50db3e6dd578e2ed6e99b65a168daed96a94e. 새 batch ID8, focused cap 7→8, C/D 예약 ID6 유지. 아직 시작하지 않은 ReadHostTests의 Claude12 turns/12 dispatch만 batch7에서 재배정한다. 앞서 시작한 relay mismatch의 예약과 Codex23/23/과거 이력은 유지하고 도구별 총량은 증가하지 않는다. 추가 loader 진단0/native/model/reviewer0, 예상5–15분/활동30분/검사process300초+정리20초, 새 실패면 Hold다. 성공해도 Rust/build/live는 자동 실행하지 않는다.

현재 checkpoint 2026-10-26T11:35:07.735910+00:00, 이번 복구 승인 후 활동 381.449초, B 잔여 24773.981초/전체 잔여 57893.890초. 다음 승인까지 전용 Owner 대기만 제외한다. 실제 결과·입력·실패 로그와 미적용 patch는 다음 처분에 필요한 근거로 보존한다.

### Approved Test Descriptor Correction — 2026-10-26

Owner가 “보정과 남은 11개 검사 승인”으로 exact proposal 84773adaa95c34bde7c3a41066c50db3e6dd578e2ed6e99b65a168daed96a94e를 승인했다. 승인 기록 2026-10-26T11:36:32.530567+00:00. tests/test_u2_adapters.py의 비교식 한 곳만 고쳤고 이전 bytes는 별도 보존·대조했다. 제품 구현 12개 고정 입력은 동일하다. 통과 27개는 재사용하고 고친1개+미실행10개만 한 번 검사한다.

cap 7→8/new batch8/C-D reserve6. Claude 미실행12/12 예약만 승계하고 Codex/이미 시작한 relay mismatch 예약/실패 이력은 그대로다. 루트 진단을 반복하지 않으며 process300초+종료20초, 활동30분이 상한이다. 직전 복구 활동 466.244초를 계상해 B 잔여 24689.186초, 전체 잔여 57809.095초로 시작한다. 새 실패면 즉시 Hold하며 Rust/build/native/model/reviewer는 0으로 유지한다.

### B Focused Verification Completed — 2026-10-26

승인한 비교식 수정 뒤 단회 focused11/11이 pass했다. 첫 실행의 그대로인 27개와 결합해 선택38개의 근거를 충족했다. 38개를 동일한 한 실행에서 통과했다고 표현하지 않는다. test AST에서 수정 함수 하나를 제외한 나머지가 동일하며 제품 구현은 그대로이므로 27개를 재사용한다. 실제 source import/호출은 관측했으나 native/model/auth/network/추가 test subprocess는0이다.

원 H01 admission/H04 single-use/H05 recovery/H08 stop의 selected offline 검사, 문서18개, 공통 read guard 및 Claude envelope15개가 포함된다. 이 표는 현재 native 양 도구 실행, authority live, H10 품질 또는 Owner 최종 수락을 대신하지 않는다. C의 새 Codex namespace 제한은 여전히 별도 결정 대상이다.

checkpoint 2026-10-26T11:41:28.971808+00:00: 테스트 보정 승인 이후 활동 296.441초. B 누적 4407.255초/잔여 24392.745초, 전체 누적 14487.346초/잔여 57512.654초. focused사용7/8, C/D예약 ID6 1개, 미래R1 0/2, 기존 도구별 사용·예약 그대로다.

Core30/새 고정입력13/기존baseline4/수정 전 test bytes/native source·선택 binary 동일성과 관련 process 그룹 부재를 확인했다. 보존: source·patch·exact 원본/새 plan·profile·runner·결과/실패 로그. 소비자는 C 근거 선택/R1/Owner 처분이며 종료 시 재평가한다. 삭제: 완료된 두 실행의 child/plan 중복 사본4개(원본 byte 대조 후)와 비어 있는 scratch/home/failure 디렉터리만 제거했다. 활성 경로 변경과 worktree 삭제는 없다.

## Platform Direction Applied With Central Plan — 2026-10-26

Owner의 11:47:56Z 요청은 macOS·Windows를 U2와 이후 기능의 설계 대상으로 두고, 기존 Work에서 구조 보강·재사용·Windows 후속을 구분하라는 방향이다. 이어진 보충 지시는 중앙 통합계획의 플랫폼 책임 구분과 통합 후 OS 정비를 기준으로 삼고, 이번 완료 조건을 새/변경 U2 코드의 최소 경계로 한정했다. 해당 요청을 [실행계획의 새 절](u2-tool-neutral-execution-plan.md#platform-direction-and-minimum-u2-boundary--2026-10-26)에 반영했다. 기존 전체 OS 정비를 U2나 진행 중 Windows 작업의 새 선행 조건으로 만들지 않는다.

중앙 계획의 현행 제품 방향, 후속안의 Platform Responsibilities And Support Boundaries와 Cross-Platform Protection And Integration Follow-Up을 실제 파일에서 읽었다. 전체 우선순위는 중앙 계획, 기술 계약·진행은 Colvia 소스, 실제 적용은 각 도입처가 소유한다. 두 중앙 문서는 변경하지 않았다. public-intent source에는 외부 계획 저장소 식별자를 추가하지 않고 정확한 내부 provenance는 기존 private evidence에 둔다.

현재 소스에서 공통 모듈의 fcntl/continuous clock/파일 내구성, 새 Claude adapter의 FIFO/pipe polling/ps/process group 처리와 Codex의 Unix FD 경계를 확인했다. 새 코드에 필요한 국소 실행 helper만 계획에 넣고 기존 worker·Core 및 과거 Codex transport 전체 정리는 후속에 둔다. Windows jsonio 구현의 path/handle·LockFileEx·FlushFileBuffers·복구 의미는 참고하되, 무기한 잠금과 U2 기한부 잠금의 차이 및 directory flush unavailable 처분 차이를 명시했다. 코드 배치 재사용과 검증 결과 재사용을 구분한다.

Windows Work의 실제 현재 기록은 Session36 일반 모드 전체 검증 진행 중이다. 기존 native 집중3/3과 Git LF/index mode 조건은 그 범위의 근거이며 U2 qualification이 아니다. 별도 작업의 source·VM·runner·기한을 변경하거나 해당 chat에 메시지를 보내지 않았다.

이번 반영은 계획·완료 조건·후속 연결이다. 실제 OS 경계 추출은 아직 0이며, 새 Rust 계약/build/모델 실행도0이다. B focused38 근거와 이전 실패는 유지한다. 최소 OS 보강 추가 예상45–90분, 기존 새 Codex 준비와 합계165–310분, 후속 stop 제안330분 또는 기존 B/전체 잔여 중 작은 값으로 구분했다. 다음 단계는 두 변경을 합친 R0 delta 준비이며 현재 미래 R1 0/2·focused7/8와 모든 기존 도구별 계수를 유지한다.

### Codex Contract And Minimum Platform R0 Authorization

Owner는 2026-10-26T12:08:00Z 추가 정적 R0 1회와 119,800bytes 자료 전송을 명시 승인했다. packet SHA-256 `5844cbdbe0f064327eb81a40e171acaf3a02a86428bb9372304a78f4bc0c80e2`. 공개 안전 계약·합성 근거·현재 소스 발췌만 포함하며 기존 private planning 저장소·계정 식별자·사용자 절대 경로는 제외했다. 기존 Claude Pro/firstParty 인증과 CLI bytes를 확인한 뒤 12:09:37Z Opus 5.5 fresh session으로 시작했다. 실제 model/session과 tools0/MCP0을 확인했다. 호출1/1이며 미래 R1 0/2와 구별한다. 준비·리뷰·정리 stop30분은 12:38:00Z, 호출880초+종료20초이며 전체 기존 잔여에서 차감한다.

계획·Work 새 절의 상대 링크와 GFM 렌더링을 확인했으며 literal 강조 기호는0이었다. 기존 B 고정 입력13개의 byte identity와 tracked diff whitespace 검사를 통과했다. 이는 문서 검증이며 새 OS 경계 구현·Windows 실행 근거가 아니다. 리뷰 중 source와 검토 입력을 고정한다.

활동 checkpoint 2026-10-26T12:11:26.129744+00:00: 직전 B checkpoint 뒤 활동 1756.854초, 명시 pause 40.303835초 제외. B 잔여 22635.891초, 전체 잔여 55755.8초. 과거 카운터/실패는 유지한다.

### Codex Platform R0 — Verbatim Reviewer Response

# 판정: **REVISE**

R0 정적 검토 결과입니다. 아래 지적은 모두 제공된 문서와 발췌 소스에 대한 정적 판단입니다. Rust compile, 테스트, 실행 근거는 없습니다. 구현 세부가 없는 항목은 재현된 결함이 아니라 prospective 공백으로 표시했습니다.

중앙 계획은 올바르게 유지됩니다. 전체 OS 리팩토링은 통합 이후로 미루고, Windows Work의 선행 조건이나 Core/U1 재개방을 만들지 않습니다. 아래 수정은 모두 문서·계약 수준의 최소 보정이며, 범용 플랫폼 구조를 요구하지 않습니다.

---

## 차단 (Blocking)

**1. 「stop」 의미가 공통 Host와 v58 reducer 사이에서 충돌함**
- **위치:** Source-diff 제안의 "실행별 종료와 전체 종료"(전체 `stop` = terminal) ↔ 기존 `ReadOnlyHost.restore()`(`stop` 행이 있어야 resume 허용) 및 `ClaudeCodeAdapter.close()`(항상 `g.stop()` 호출). Minimum Change Now의 Codex 행에서 v58이 "공통 read-only guard"에 연결된다고 되어 있습니다.
- **결과:** Codex 경로가 `ReadOnlyHost`를 재사용하면 두 가지 중 하나가 됩니다.
  - 첫 프로세스 종료 시 기록된 `stop`이 v58에서 terminal로 해석되어 `synthetic-02` fresh 재개가 불가능해집니다.
  - 또는 Host의 `stop`을 resumable로 해석하여 terminal stop이 실제로는 terminal이 아니게 됩니다.
  - 어느 쪽이든 C의 stop/fresh-resume 결합 검증이 성립하지 않습니다.
- **최소 수정:** v58 계약에 세 사건의 대응표를 명시합니다.
  - Host의 `stop`(step 닫힘·resumable)
  - native `process-ended`(slot 닫힘)
  - 전체 terminal stop
  - terminal은 별도 event kind로 둡니다. `ReadOnlyHost`의 기존 동작과 Claude 경로의 의미는 바꾸지 않습니다.

**2. 단회 reservation의 결속 순서와 소비 주체가 미고정임**
- **위치:** 계약 제안 표의 `activation`/`accounting_snapshot`, 「재생 방지」 문단, "결속 순서는 미래 실행 packet에 고정". Budget 절의 "existing C/D reservation ID6".
- **결과:**
  - 비순환성이 이번 R0의 핵심 검토 대상인데 그 순서를 미래 packet으로 미뤘습니다.
  - native는 "승인 자료 일치와 남은 배정"만 검증하므로 ledger 소비 여부를 볼 수 없습니다. 그런데도 "별도 directory 재사용 거절"의 주체가 불명확합니다.
  - 소비할 reservation이 ID6인지, C Codex 배정(4/8/12/8/16)의 하위 배정인지도 불명이라 이중 계상이나 누락 위험이 있습니다.
- **최소 수정:** 다음 세 가지를 지금 고정합니다.
  - **DAG:** template(binary 참조 없음) → source에 template digest 고정 → build/binary → activation(template digest·binary/source/input hash·pre-consumption snapshot digest·reservation ID) → ledger 소비 행(activation digest·run dir 기록, fsync) → journal anchor(activation digest).
  - **책임 분리:** cross-journal 재생 방지는 trusted Host ledger 전용이고, native는 journal 내부 재생만 막는다고 명시합니다.
  - **배정 출처:** C Codex 배정의 child reservation이며, 소비 시 C 잔여에서 2/4/6/4/4를 즉시 차감하고 환불하지 않는다고 명시합니다. ID6와의 관계도 함께 적습니다.

**3. 미지원 거절 시점이 「효과 전」으로만 정의되어 단회 배정을 소진할 수 있음**
- **위치:** Responsibility And Sequence의 "효과 전 거절", Minimum Change Now의 "미지원 거절은 실행 경계에 둠" ↔ 재생 방지의 "중간 실패는 환불하지 않는다".
- **결과:** OS나 capability 부재(예: `mach_continuous_time`, FIFO, Unix FD 미지원)가 reservation 소비 후에 드러나면 효과는 0이어도 배정은 영구 소실됩니다. 또 OS 감지, admission, profile 전환의 분리가 순서상 보장되지 않습니다.
- **최소 수정:** 순서를 "capability 확인 → admission → reservation 소비"로 명시합니다.
  - 소비 전 실패는 미소비 거절로 처리합니다.
  - 소비 후 발견된 capability 실패는 소비됨/Hold로 분류합니다.
  - 모듈 import 실패(예: top-level `fcntl`·ctypes)도 소비 전 미지원으로 분류합니다.

---

## 비차단 (Nonblocking, 실행 packet 고정 전 해소 권장)

**4. `proxy-start=1`과 `starts=2`의 관계가 불명**
- **위치:** allocation 표, `validate_proxy_spec:7080`.
- **결과:**
  - proxy가 start마다 필요하면 `synthetic-02`가 count 초과로 거절되어 C 재개가 불가능해집니다.
  - 공유한다면 첫 start 종료 시 "process-group 부재" 판정에 proxy가 포함되는지 불명확합니다.
- **수정:** proxy 수명(공유/개별)과 stop 시 부재 확인 대상을 명시합니다.

**5. 거절 turn의 종료 방법과 계수가 미정의**
- **위치:** reducer 문단의 "거절 뒤 generation 2 금지".
- **결과:** tool 결과를 모델에 돌려주지 않고 turn을 닫으려면 interrupt 같은 control 또는 native 종료가 필요할 수 있습니다. 이 경우 controls=4와 sends=6 산정에 영향을 줄 수 있습니다.
- **수정:** 닫는 수단과 해당 control/send 계수를 vector에 고정합니다.

**6. native journal과 Host `EffectJournal`의 순서 및 crash 창 규칙이 없음**
- **위치:** Python `LiveSession` 행, "이벤트마다 예약은 효과 전".
- **수정:** 다음 두 규칙을 명시합니다.
  - native host-dispatch 예약이 Host의 `request`/`effect` 행보다 먼저 기록되어야 합니다.
  - 재개 시 "native dispatch는 있으나 Host 종결 행이 없음"은 unknown으로 판정하고 재개를 차단합니다.
- 기존 `EffectAdmission`의 주석 의도와 같으나, 현재 `ReadOnlyHost.dispatch`는 native 예약을 확인하지 않습니다.

**7. OS helper는 API가 아니라 의미 사후조건으로 정의해야 함 (범용 framework 아님)**
- **위치:** Minimum Change Now, Reuse From Windows Work.
- **수정:** 이번에 추출하는 helper마다 한 줄 사후조건을 남깁니다.
  - **예산 시계:** suspend 포함 여부를 명시합니다.
  - **잠금:** bounded deadline이며 indefinite wait를 금지합니다.
  - **발행:** exclusive no-replace입니다(`renameatx_np RENAME_EXCL`).
  - **소유 프로세스 부재:** 확인 방법과 한계를 적습니다.
- 위 수정에 포함해 기록할 현재 정적 사실:
  - `ReadOnlyHost`와 Claude adapter의 deadline은 `time.monotonic`(macOS에서 sleep 제외)이고, v58은 continuous clock입니다. 같은 이름의 "예산 시계"로 합치지 말아야 합니다.
  - `ps lstart`는 1초 해상도이고, daemonize 후 ppid=1로 재부모화된 후손은 scan으로 놓칠 수 있습니다.
- 이는 기존 A 근거를 재개방하라는 뜻이 아니라, macOS 근거의 보장 수준을 정확히 표기하라는 뜻입니다. 이렇게 해야 미래 Windows 구현(예: `QueryUnbiasedInterruptTime`은 sleep 제외)이 같은 보장으로 잘못 동등화되지 않습니다.

**8. 증거 재사용 단위를 함수 수준으로 고정해야 함**
- **위치:** Completion And Evidence Selection, 검사와 증거 재사용.
- **결과:** helper 위임으로 `contracts.py`의 파일 SHA(`b5f4…`)는 반드시 바뀝니다. 파일 digest 기준이면 27개 재사용 근거를 주장할 수 없습니다.
- **수정:** 다음 함수들의 byte 불변이나 호출 그래프 불변을 재사용 조건으로 명시하고, 변경 시 해당 사례만 재선정합니다.
  - `checked_open`, `durable_private`, `control_read`, `ControllerLock`
  - `DocumentController`와 worker 입력

**9. 실제 macOS 실패 경로 검증에 프로세스 배정이 없음**
- **위치:** Completion 조건 2, Budget의 "새 native fake-provider 불필요".
- **결과:** C의 성공 경로에 결합하는 것만으로는 deadline 초과, 강제 종료, 미지원 거절의 실제 실행 경로가 관측되지 않습니다.
- **수정:** 둘 중 하나를 택합니다.
  - Python batch에 model·auth·network 0인 test-spawned 프로세스 소수(N)를 명시 배정합니다.
  - 또는 해당 경로를 mock-only 근거로 결과에 표기합니다.
- Claude 16/16 simulated 상한도 실제 선택 사례 수와 연결해야 합니다.

**10. Rust 테스트와 build의 source 결속, 재컴파일 0의 귀결**
- **위치:** Rust 명령 형태, Budget.
- **수정:**
  - `cargo test`의 source digest와 `cargo build`의 source digest가 같아야 한다고 고정합니다.
  - 테스트 실패 후 source 수정은 자동 재컴파일 없이 Hold로 처리하고 별도 배정을 받는다고 명시합니다.
  - template digest가 native에 고정되므로, template bytes는 Rust 수정 전에 Owner 승인으로 확정되어야 한다는 순서도 적습니다.

**11. Claude와 Codex의 보장 비동등성 표기는 적절함 (확인 사항)**
- 다만 tool×OS×profile 결과표에서 Codex v58은 "macOS 전용, Windows 미구현·효과 전 거절"로 명시해야 합니다. 이는 Unix FD peer 검증과 `mach_continuous_time`에 의존하기 때문입니다.
- U1 Windows 통과를 U2 칸으로 옮기지 않는다는 규칙도 같은 표에 남기기를 권합니다.

---

**정리:** 차단 1–3은 문서·계약 문장 수준의 보정으로 해소할 수 있습니다. Owner 승인을 위한 정확한 실행 packet을 고정하기 전에 반영해야 합니다. 이 R0은 source 수정, 테스트, build, live 실행을 승인하지 않습니다.

### Codex Platform R0 — Driver Disposition

R0 REVISE: 차단1–3과 비차단4–10의 계약/실행안 보완을 위 실행계획의 [R0 처분 절](u2-tool-neutral-execution-plan.md#r0-delta-disposition-and-execution-proposal--2026-10-26)에 반영했다. 확인11의 tool×OS×profile 구분을 유지한다. Driver는 host stop/native slot 종료/전체 terminal 구분, 비순환 결속과 C child reservation 소비 책임, capability 사전 거절, proxy 공유 수명, 거절 turn 종료·dual-journal crash 창, helper 사후조건과 실제 local child2개 배정을 명시했다. native 소스의 policy/models/accounts 세 control 종류를 추가 대조해 controls4→6으로 제안 보정했으며 원 C16 한도 안의 부분 배정이다.

재리뷰는 실행하지 않았다. 원 packet119800bytes와 응답9553bytes·hash·모델/session·입력 불변·종료 근거는 기존 private R0 경로에 보존한다. 실제 source/build/model/추가 focused 실행은0이며, 문서 보정은 구현 승인이 아니다. 다음 결정은 B의 v58 계약+최소 OS helper 구현·offline 검증 묶음이다. C actual launch는 결과 뒤 exact activation으로 구체화한다.

### Platform R0 Closeout And Concrete Next Decision

checkpoint 2026-10-26T12:24:37.778248+00:00: 이번 R0 승인부터 기록·보정·정리까지 997.687초/상한1800초, 실제 Reviewer148.820초. B 누적 6955.758초/잔여 21844.242초, 전체 누적 17035.849초/잔여 54964.151초다. 명시 pause40.303835초를 제외하고 Reviewer 대기·동시 작업은 한 번 계상했다. 다음 Owner 결정 대기는 별도 제외한다.

고정한 B 실행 제안은22095bytes·SHA-256 `97d3fc87933ac36f3abec6517d8f1dae52142c4db26ae6706c5218c2f4e51ec8`, v58 template는3283bytes·SHA-256 `96982f9b9edf241a6cb47dd90ab72dd0a01f5dd1fd6acb82c734b87fdc9265e7`다. template는 source/binary 결과 hash를 포함하지 않고 보정 제안을 참조하므로 source에 template digest를 고정할 때 역참조 순환이 없다. 이 기록은 두 artifact의 승인·실행을 대신하지 않는다.

다음 제안은 B의 새 Codex v58 계약과 최소 OS helper 구현·offline 확인이다. 예상165–310분, stop330분 또는 B/전체 잔여 중 작은 값(마지막20분 정리). focused cap8→10, Python/Rust 각1batch, compile은 unit-test target1+binary1, local Python child2를 제안하며 model/live/authority0이다. 실제 C launch와 activation은 이 B 실행 승인에 포함하지 않는다. 기존 C/D batch ID6·미래R1 0/2·과거 사용량은 유지한다.

검증: 추가한 계획/Work 및 index의 GFM, tracked diff whitespace, 새 상대 링크를 확인했다. 기존 B 고정 입력13·Rust app-server source·두 중앙 계획·참조 Windows jsonio/DR은 관측 이후 그대로다. 코드 변경0이므로 기존 Core30 검증 결과를 상속하며 새 전체 suite를 실행하지 않았다.

정리: 완료된 단회 R0 runner와 비어 있는 scratch만 삭제했다. 활성 경로 변경0, worktree/branch 삭제0이다. 원 packet·원응답·수정 실행안/template·승인/모델/입력/종료 기록은 Owner 결정과 R1 소비를 위해 유지하며 그 처분 뒤 재평가한다. 중앙 계획의 전체 OS 정비와 진행 중 Windows 작업은 변경하지 않았다.

### B v58 And Minimum Platform Execution Authorized

Owner는 2026-10-26T12:28:40.691722Z 실행 제안97d3fc87…와 template96982f9b…를 승인했다. 새 Codex 계약·최소 OS 경계와 영향 tests만 구현한다. Python/Rust 집중 batch 각1, test compile1+binary build1, local Python child2, 추가 simulated Codex48/48·Claude16/16 상한이다. 기존 focused7/8은 사용량7을 유지한 채 cap10으로 늘리고 C/D ID6 예약을 유지한다. worker/native model·C live·authority0, 실패 뒤 자동 recompile0이다.

실행 stop 2026-10-26T17:58:40.691722+00:00, 새 작업 중지/정리 시작 2026-10-26T17:38:40.691722+00:00다. 기존 B/전체 잔여에서 차감하며 새 전체 cap이 아니다. 승인까지의 결정 대기는 기존 closeout 이후 별도로 제외한다. 수정 대상 현재7파일의 복구 bytes·mode를 기존 task 하위 before에 보존하고 원본과 SHA를 대조했다. 전체 checkout 사본이나 다른 작업의 source는 만들거나 바꾸지 않는다.


### Approved B v58 Implementation Checkpoint — 2026-10-26

Owner는 보정된 B 구현·offline 검증(template `96982f9b…`, 실행안 `97d3fc87…`)을 승인했다. 이 범위는 최소 OS 실행 경계, v58 전용 Python/Rust 계약·read-only adapter, 영향 집중 검사와 동일 source의 unit compile1/binary build1이다. C live·모델·authority 실행은 포함하지 않는다.

첫 source 초안은 새 helper 호출부와 v58 전용 reducer, trusted Host 단회 소비, materializer를 연결했다. 과거1–57 전용 reducer는 그대로 유지한다. 현재 근거는 source 작성과 Python AST 구문 확인뿐이며 import·테스트·compile·native 실행은 모두0이다. 다음은 정적 대조와 공통 입력 벡터·선택 검사의 정확한 사용량 고정이다. 승인 시작 기준 stop330분/마지막20분 보존을 유지하며 기존 사용량은 환불하지 않는다.


### B v58 First Failure Hold — 2026-10-26

Owner 승인 범위에서 v58와 최소 OS 경계를 구현하고 고정 Python21개를 단회 실행했다. 17pass 뒤 18번째 activation 소비 test가 `v58-journal-lock-deadline`으로 오류를 내어 중단했다. 남은 Python3, Rust compile/test/build, local fixture child는 모두0이다. C live/model/authority0, 자동 source 수정·재실행0을 유지한다.

직접 원인은 test가 Budget._clock만 합성값으로 바꾸고 새 OS lock의 wall clock은 실제값을 읽는 불일치다. test-only 보정의 성공 여부는 미검증이다. traceback과 이벤트·종료 결과는 보존했지만 TemporaryDirectory의 선행 cleanup으로 원 실패 fixture 사본은 비어 있다. 보존 누락을 원본 보존으로 주장하지 않는다. 상세 결과: `private-evidence/E126`. [공개용 중립화]

현재 focused8/10, 미래R1 0/2다. 통과17 재사용 + 실패/미실행4개 복구1batch + 미사용 Rust1batch + C/D 예약1을 위한 cap11 제안을 별도로 작성했다. runtime/native/template 변경0, local child2 배정 유지, 첫 실패 Hold다. 복구 예상45–120분/stop150분(기존 잔여와 작은 값, 마지막15분 정리)은 판단값이며 아직 승인·실행하지 않았다. 기존 Work Active/미완료를 유지하고 STATUS 및 중앙 계획은 변경하지 않는다.

이 checkpoint에서 B 누적10523.867초/잔여18276.133초, 전체 잔여51396.042초다. 정리로 검증된 실행용 중복2개·빈 home/scratch2개만 제거했으며 source/before/cache/logs는 실패 처분과 구체적 재개·R1 소비를 위해 유지한다.


### B v58 Offline Complete — 2026-10-26

Owner 메시지602957422(2026-10-26T13:40:17.915357Z, “진행해”)가 복구 제안d69ecd23…을 승인했다. test의 합성 시간2곳과 실패 fixture 보존 runner만 보정해 Python4/4를 통과했고, 앞선17pass와 합쳐 선택21개를 충족했다. 원 실패1건·원 fixture 보존 누락은 이력으로 유지한다. 실제 child2개의 정상 TERM/TERM deadline 후 KILL 종료를 관측했다.

같은 고정 native source에서 Rust compile1·선택6/6·binary build1을 완료했다. 새 binary `3860ebdc24190e34667e6a131ccff9993578c9d44370449cb99f1373109b3eac`는 실행0이며, template96982f9b…/native source7e761b0b…와 결속한다. 상세 결과: `private-evidence/E124`. source·Core30·worker·입력 불변과 함수 기반 재사용28개/재실행10개를 대조했다. [공개용 중립화]

현재 focused10/11(C/D 한 묶음 잔여), 미래R1 0/2, 이번 추가 simulated Codex33/35·Claude12/12다. native/model/authority0을 유지한다. Codex v58와 변경 Claude adapter의 실제 C 검증, H01–H10 처분, D/R1·Owner 최종 수락은 남아 있어 Work Active/미완료다. 두 도구 Windows U2와 통합 후 전체 OS 정비도 별도다.

복구 checkpoint까지876.083초를 계상했고 B 잔여17331.369초/전체 잔여50451.278초다. 최종 기록은 `private-evidence/E125`을 따른다. 고유 binary2개를 outputs로 검증 보존한 뒤 이번 복제 cache·성공 scratch·중복 입력을 정리했다. source/before/로그는 C·R1·Owner 처분 소비용으로 유지하며 기존 candidate·worktree·branch는 제거하지 않았다. [공개용 중립화]


### C Actual Claude And Codex Preflight Hold — 2026-10-27 KST

Owner 메시지648600329가 기존 B–D 진행 권한을 재확인했다. C에서 source Claude adapter2회/Host입력4/bridge4/실제 read2를 실행했고 실제 relay 경로의 고정 Host injection으로 file-scope·duplicate 거절을 각1회 관측했다. 살아 있는 두 native를 Host가 중단하고 process group/관측 descendant 부재를 확인했다. fresh Host가 Core completed·후속 proposal·실행 권한 없음 상태를 복원했다. Sonnet5.5/CLI2.1.310/firstParty Pro이며 medium은 요청값, effective effort와 내부 model transport 계수는 승인된 native trust 아래 unknown이다.

Codex v58는 activation/native/auth/network 모두0 상태에서 register_runtime의 spec digest 결속 불일치와 고정 peer 누락을 발견했다. 집중1묶음의 세 재현은 KeyError, frozen reducer의 추가 field 거절, helper peer 불일치다. helper 결과를 실제 network 우회로 확대하지 않는다. native candidate와 Core/worker source는 바꾸지 않았으며 재빌드0이다. 상세 재현: `private-evidence/E130`. [공개용 중립화]

### D Five-Document Assessment And Exact R1 Authorization

원 H10 출력5개와 보존 worker가 일치하며 Ref01–Ref27도 당시 SHA와 일치한다. Operations의 진단 흐름·취소/종료·DB timeout·503/privacy 경계에서 중대한 사실 충돌을 발견하지 않았다. Narrative에는 작성 후 검사·기술 수락 결과의 연결 보완을 권고한다. 원문 수정0, 새 Gradle/Docker/DB/HTTP0, Owner 유용성·활동 시간은 미측정이다. 품질 검토: `private-evidence/E149`. [공개용 중립화]

자동 승인 검토가 R1 전송을2회 거절한 뒤, Owner는 정확한 request.md143999bytes를 기존 Claude Pro/firstParty Opus5.5에1회 전송하는 질문에 “이 정확한 R1 자료 전송·1회 검토 승인”으로 응답했다. 승인 후14:57:09.548671Z부터271.370초간 실제 검토했다. tools/MCP0, source drift0, 실제 model claude-opus-5-5, process group absent다. packet SHA `ab2fc53e5f66e18d1d84b43ea102e5cd5291c2bde6cee35ed17f8abe7a2ae236`, 응답 SHA `db79f513a3955f021ac26767def3edfee41af06625a24edc3b6939f288e97597`. 원5문서·고객자료·계정정보는 전송하지 않았다.

### R1 Verbatim Response

# R1 독립 정적 검토: Tool-Neutral Read Profile / Codex v58 Launch

## 판정 요약

- **Codex v58 live launch: BLOCKED.**
  - P0 두 건은 Driver 발견을 반복 확인한 것입니다. FD 등록 실패와 v58 고정 peer 우회입니다.
  - 신규 P1 한 건은 위 P0과 결합하면 거짓 absence 기록으로 이어집니다.
  - 현 상태로 launch하면 activation 소비 후 비가역 Hold에 도달합니다. Driver가 preflight 불일치에서 launch하지 않은 결정은 정합합니다.
- **Claude native adapter: 공급된 발췌 범위 안에서 신규 차단 결함은 없습니다.** P2 증거 결합 사항 두 건만 있습니다. 이 판단은 C 실측 증거를 재판정하는 것이 아닙니다.
- 수리는 모두 **Owner disposition이 필요합니다.** 근거는 다음과 같습니다.
  - B 이후 소스 변경은 source_identity 변경, B 재검증, 신규 activation으로 이어집니다.
  - focused cap 11/11이 소진되었고 rebuild 할당이 없습니다.
- 본 검토는 수락 권한이 아닙니다. Owner 유용성·효율 수락을 추론하지 않습니다.

## 커버리지 한계

다음 코드는 공급되지 않아 정적 판정에서 제외했습니다. 해당 부분에 의존하는 보장은 **미검증**으로 둡니다.

- Python 측:
  - `LiveClient` (on_spawn, callback 예외 처리, send 경로)
  - `EffectAdmission`
  - `Budget` (create, read, reserve, fresh_bound, execution_reserve_ms)
  - `end_process`, `bind_native_notifications`, `check_auth_metadata`, `protected_auth_metadata`
  - `DocumentController`, `contracts` 헬퍼
- Rust 측:
  - proxy와 runtime 본체
  - v58 reducer의 line 550 이후
- 관측 증거와 본 검토의 성격 구분:
  - Driver 재현(KeyError, v58-start-fields, peer helper)은 **실행된 Driver 관측**입니다.
  - 아래의 나머지 주장은 모두 **본 검토자의 정적 추론**입니다.

---

## A. 반복 Driver 발견: 분류

### P0-1. v58 FD runtime 등록 불능 (Driver 1+2: 확인)

**위치**
- `PreparedFdController.register_runtime` line 2049: `starts[0]["subject"]["runtime_spec_sha256"]`
- `FreshCodexSession.launch`: `budget.reserve('start', {'execution_binding','proxy_identity_sha256'})`
- Python reducer `exact(sub, ('execution_binding','proxy_identity_sha256'), 'v58-start-fields')`
- Rust line 469 `exact_fields(sub, &["execution_binding","proxy_identity_sha256"])`

**정적 확인**
- register_runtime에는 v58 분기가 없습니다. 레거시 start subject 스키마를 그대로 가정합니다.
- 반면 v58 start subject는 Python과 Rust 양쪽에서 정확히 두 필드로 고정되어 있습니다.
- 따라서 Driver 2의 결론이 맞습니다. 생산자에 필드를 추가하면 reducer가 거부하고, 추가하지 않으면 등록이 KeyError로 실패합니다.
- KeyError는 `HostRefusal`이 아니므로 호출자의 예외 분류도 어긋납니다.

**추가 정적 관찰**
- v58 journal에는 runtime spec 내용 해시가 **durable하게 결합된 지점이 없습니다**.
  - `runtime-entered`는 `{start}`만 담습니다.
  - launch contract는 spec 경로별 argv/cwd/env만 담습니다.
- 레거시가 제공하던 "journal start 이벤트 ↔ spec sha" 링크는 v58에서 이미 사라졌습니다. 단순히 검사를 우회하는 것은 템플릿 guard `Unix_FD_peer_nonce_spec_binding: preserve`에 위배됩니다.

**발현 시점**
- 이 결함은 소비 이후에 발현합니다.
- launch 순서는 ledger `v58-consumed` → budget `start` → Host `native-start` → spawn → on_spawn 실패입니다.
- 따라서 실제 launch 시 allocation이 환불 없이 소진됩니다.

**최소 수리 (택1, Owner disposition)**

- **Option A (권장, reducer와 템플릿 무변경):** register_runtime에 `version == 58` 전용 분기를 둡니다.
  1. Trusted Host가 `materialize_runtime` 영수증 `{path, sha256}`을 **start reservation 이전에** controller에 등록합니다. 예: `expect_runtime(start, receipt)`. 이 등록은 `fd-events.jsonl`에 fsync 기록합니다.
  2. register 시 다음을 모두 요구합니다.
     - `runtime["spec_sha256"] == 영수증`
     - 파일 digest 재검증
     - start 이벤트가 정확히 1개이고, subject가 `{execution_binding: anchor 기대값, proxy_identity_sha256: controller 자체 계산값}`과 **완전 일치**
  3. `proxy_identity` 계산식을 controller 메서드 하나로 이동합니다. 현재 `FreshCodexSession.proxy_identity`에 중복되어 있습니다.
  4. 이것이 "spec binding preserve"와 동등한지는 R0/Owner 판단 사항으로 명시합니다. durable 근거가 budget journal에서 FD evidence log와 materialization 영수증으로 옮겨가기 때문입니다.
- **Option B:** Python/Rust reducer와 템플릿에 `runtime_spec_sha256`을 추가하는 계약 개정입니다. 템플릿 digest, source, build, activation이 모두 새로 필요하고 rebuild 할당도 필요합니다.
- **금지:** 다음은 허용하지 않습니다.
  - v58에서 spec sha 검사를 생략하는 것
  - `.get()`으로 완화하는 것
  - reducer exact 검사를 느슨하게 하는 것

### P0-2. v58 고정 peer 미적용 (Driver 3: 확인, 영향 범위 보강)

**위치**
- `frozen_network_peer` lines 1961–1966: 58이 버전 tuple에 없음
- `PreparedFdController.__init__` line 1983
- `_request` line 2084 `ip = self.selected_peer`

**정적 확인**
- v58에서는 `selected_peer` 기대값과 `"104.18.32.47" in addresses` 검사가 모두 빠집니다. 그 결과 `addresses[0]`을 반환합니다.
- `_request`의 `getpeername() == peer` 검사는 동어반복입니다. 이미 잘못 선택된 peer와 비교하기 때문입니다.
- `validate_native_launch` line 2214는 contract JSON의 peer만 검사합니다. controller의 `selected_peer`와는 비교하지 않습니다.

**영향**
- Python controller는 DNS 첫 주소로 TCP를 연결하고 FD를 발급합니다.
- TLS/SNI는 1.1.1.1 같은 무관한 주소는 막을 가능성이 높습니다. 그러나 chatgpt.com을 서빙하는 **다른 edge IP**는 통과시킬 수 있습니다. 이는 "fixed peer" guard 위반입니다.
- Rust proxy가 payload의 `peer`를 contract와 대조하는지는 미공급이라 미검증입니다.
- evidence 형태에 따라 결과가 갈립니다.
  - 생산자가 v57 형태(`selected_peer` 포함)로 evidence를 주면 v58은 `FD resolver binding`으로 fail-closed 됩니다. 즉 launch blocker가 됩니다.
  - 그 필드를 빼면 조용히 우회됩니다.

**최소 수리**
- `frozen_network_peer`에 명시적 `version == 58` 분기를 추가합니다. 1–57 tuple 의미는 변경하지 않습니다.
- 그 분기는 v57과 동일한 세 가지를 요구합니다.
  - evidence에 `selected_peer` 포함
  - `"104.18.32.47" in addresses`
  - 반환값 고정
- 추가로 controller init(v58)에서 `selected_peer == launch contract network peer`를 요구합니다.

**한계**
- Driver 재현은 helper 수준까지입니다. DNS, socket, native 경로의 우회는 미시도입니다.

---

## B. 신규 발견 (본 검토자의 정적 추론)

### P1-3. spawn 콜백 실패 시 고아 프로세스 가능성과 거짓 `native_absent` durable 기록

**위치**
- `FreshCodexSession.launch`: `self.client = native.LiveClient(..., on_spawn=...)`
- `close()`: `else: failure = HostRefusal('v58-native-absence-unavailable')`
- `stop_execution`: `session.client is None or (...)` → `budget.reserve('execution-stop', {'native_absent':True,...})`

**트리거**
- on_spawn이 Popen 이후 예외를 던지는 경우입니다. 현재 P0-1 때문에 **결정적으로** 발생합니다.
- 이 경우 LiveClient 생성자가 반환되지 않아 `self.client`가 None으로 남습니다.
- `self.known`도 관측되지 않은 상태입니다.

**영향**
- (a) LiveClient가 콜백 실패 시 자식을 스스로 종료하지 않는다면, `close()`는 프로세스 그룹을 종료할 핸들이 없습니다. 이 부분은 미공급이라 미검증입니다.
- (b) `stop_execution`은 client None을 "부재"로 취급합니다. 그래서 관측하지 않은 상태에서 `native_absent: True`를 담은 `execution-stop`을 **durable 기록한 뒤** 예외를 던집니다. 이는 템플릿 `native.process-ended`의 "observed absence" 의미에 위배됩니다.
- Host 측은 fail-closed입니다. native-start만 있고 native-stop이 없으므로 restore가 거부됩니다. 그러나 budget journal은 거짓 종단을 담게 됩니다.

**최소 수리**
- on_spawn 래퍼가 콜백 실행 **전에** `self.spawned_process`를 보관합니다. `close()`는 client가 None이어도 이 핸들로 `observe_owned`/`stop_owned`를 수행합니다.
- `stop_execution`의 판정을 바꿉니다.
  - 해당 slot에 budget `start`가 존재하면 `cleanup['process_group_absent'] is True`라는 **양성 관측**을 필수로 합니다.
  - client None을 부재로 간주하는 것은 start 미예약일 때만 허용합니다.

### P1-4. Codex "refusal 결과 미전송" 보장이 미공급 코드에 전적으로 의존 (증거 공백)

**위치**
- `FreshCodexSession.callback`의 `raise RefusedTurn(...)` 주석 "Raising prevents LiveClient from sending any result"
- `turn()`의 `except RefusedTurn`

**문제**
- LiveClient가 callback 예외를 잡아 다음을 할 수 있는지 검증되지 않았습니다.
  - JSON-RPC error 응답을 native에 쓰는 경우. native가 이를 tool 결과로 모델에 전달할 수 있습니다.
  - 예외를 다른 타입으로 감싸는 경우. 이때 `turn()`이 잡지 못해 close가 누락됩니다.
- 이는 템플릿 `tool_result_sent_to_model:false`, `generation2:false`, `interrupt_rpc:false`의 핵심입니다.
- B 테스트가 이 경로를 실제 LiveClient로 통과했다는 증거는 제공되지 않았습니다.

**최소 조치**
- 실제 LiveClient와 로컬 fake native(네트워크 0)로 다음을 단언하는 테스트를 추가합니다.
  - callback 예외 이후 native stdin으로 **0 바이트**가 쓰임
  - `rejected-terminated` 반환
  - process-ended 기록
  - generation이 1
- 실패 시 LiveClient 수리 범위로 편입합니다.

### P2-5. 모델 이탈 시 Host effect 발생 후 Hold

**위치**
- `FreshCodexSession.callback`: `gate.dispatch(...)` **이후**의 `require(tool == 'u2_read_file' and gate.effects == before + 1)`
- reducer의 `worker-result`는 `ordinal == 0`을 요구합니다.

**트리거**
- plan 0에서 `u2_verify`를 호출하는 경우
- 또는 refusal plan(ordinal 1)에서 범위 내 유효 read를 호출하는 경우

**결과**
- Host가 실제 worker effect를 완료합니다. 그 뒤 require가 실패하여 대응 없는 Hold가 됩니다. 결과는 미전송입니다.
- 쓰기나 authority는 아니므로 P2로 분류합니다. 다만 의도된 `worker_reads` 배분 밖의 read effect가 발생합니다.

**권고**
- `ReadAdmission`에서 plan ordinal을 추적합니다.
- ordinal 0에서 `u2_read_file` 이외의 도구는 Host dispatch **전에** 거부합니다. 이때 결과는 미전송, native는 종료합니다.
- ordinal 1의 유효 read 처리 방식은 Owner/R0가 결정해야 합니다. 템플릿 `missing_correspondence: unknown-Hold` 수용 여부의 문제입니다.

### P2-6. 상속 `Admission.bind`의 도구 수 하드코딩

- line 1894의 `len(envelope["model_specs"]) == 4`는 v58 `dynamic_tools`가 정확히 4개가 아니면 모든 turn을 `model-visible tool drift`로 거부합니다.
- v58 런타임 spec의 dynamic_tools는 미공급입니다.
- **조치:** v58 spec 인벤토리 개수를 확인하고, 이를 고정하는 테스트를 추가합니다.

### P2-7. `codex-v58` OS preflight의 범위 부족

- `MacExecution.preflight('codex-v58')`는 `/bin/ps`와 `os.killpg`를 검사하지 않습니다. claude-native는 검사합니다.
- 그러나 Codex close는 `observe_owned`/`stop_owned`를 사용합니다.
- 템플릿 `unsupported_before_consumption: true`에 따라 소비 전 검출이 원칙이므로 동일한 검사를 추가해야 합니다.

### P2-8. 버전 tuple fall-through 체계 감사

- P0-1과 P0-2는 모두 "58이 레거시 tuple에 없어 기본 분기로 떨어지는" 패턴입니다.
- 발췌 범위 내 결과:
  - `phase_transport_limit`, controller `expected`, `validate_native_launch`: v58 분기 있음
  - `register_runtime`, `frozen_network_peer`: 없음
- 미공급된 native 모듈 전체에서 `version in (...57)` 형태를 v58 관점으로 열거·대조하는 정적 점검을 수리 범위에 포함하기를 권고합니다.

### Claude 측 P2 (증거 결합 사항, 차단 아님)

- **P2-9.** `validate()`는 `spec['auth']`(firstParty/pro)를 **선언값**으로만 검사합니다.
  - init의 `apiKeySource`는 기록만 되고 검증되지 않습니다.
  - "firstParty subscription"을 런타임 관측으로 주장하려면 init 값이나 사전 auth status 캡처를 spec digest에 결합해야 합니다.
  - C 증거에 별도 관측이 있다면 해당 없습니다.
- **P2-10.** `dispatch_transform`(fault injection)은 `spec_sha256`에 결합되지 않습니다.
  - duplicate-negative 증거가 이 경로에 의존한다면, transform 식별자를 launch-spec이나 record에 결합해야 합니다.
  - 그래야 "fixed-host-injection"이 감사 가능해집니다.

---

## C. 권고 수리·검증 범위 (보장 약화 금지)

### 수리 (Owner disposition 후 단일 변경 집합)

1. `frozen_network_peer`에 v58 명시 분기를 추가하고, controller init에서 contract peer와 대조합니다. (P0-2)
2. `register_runtime`에 v58 분기를 추가하고 materialization 영수증으로 바인딩합니다(Option A). Option B는 계약 개정입니다. (P0-1)
3. spawn 핸들 보존과 `stop_execution`의 양성 absence 요구를 반영합니다. (P1-3)
4. (선택) preflight를 보강합니다. (P2-7)

### 필수 테스트 (네트워크, 공급자, 인증 0. 공급자 성공 증거가 아님)

- **T1:** 실제 `FreshCodexSession.launch` → 실제 `register_runtime` 경로를 로컬 fake native로 실행합니다.
  - 양성: 등록 성공과 `runtime-bound` 기록
  - 음성: spec digest 불일치, 영수증 불일치, start 이벤트 부재·중복, subject 불일치, 재등록 거부
- **T2:** start subject에 필드를 추가한 이벤트가 Python과 Rust 양쪽에서 계속 `v58-start-fields`로 거부되는지 확인합니다. reducer 동치 회귀 테스트입니다.
- **T3:** peer 테이블 검사입니다.
  - v58에서 `[1.1.1.1]`은 거부
  - `[1.1.1.1, 104.18.32.47]`은 `104.18.32.47` 반환
  - `selected_peer`가 없는 evidence는 거부
  - v1–57 결과는 불변
- **T4:** on_spawn 실패를 주입합니다.
  - 프로세스 그룹과 관측된 후손의 부재가 확인되어야 합니다.
  - 관측이 없으면 `execution-stop`이 기록되지 않아야 합니다.
  - Host resume은 거부되어야 합니다.
- **T5:** RefusedTurn 경로입니다. native stdin 0 바이트, generation 1, `process-ended`, Host 결과가 `refused`이고 effects 0임을 확인합니다. (P1-4)
- **T6:** 2-slot 순서를 검증합니다. 같은 proxy identity, slot 1 종료 후 fresh Host resume, slot 2 start, `v58-proxy-restart` 음성을 확인합니다.
- **T7:** 이탈 시나리오입니다. plan 0의 `u2_verify`와 plan 1의 유효 read가 Host effect 전에 거부되는지, 또는 Owner가 결정한 처리를 따르는지 확인합니다.

### 절차

- 변경 후 B 선택 테스트와 위 테스트를 동일 소스에서 실행합니다.
- Rust 변경 시(Option B) build를 동일 소스로 다시 수행합니다.
- 새 source_identity로 activation과 anchor를 다시 만듭니다.
- 현 C cap(11/11, rebuild 0) 안에서는 불가능합니다. 따라서 **Owner disposition이 선행**되어야 합니다.

### R1 Driver Disposition And Remaining Boundary

Codex BLOCKED 판정을 유지한다. Driver는 기존2결함과 양성 종료 관측 연결, 효과 전 이탈 검사, OS preflight를 복구 범위로 제안했다. 미공급 코드의 후속 정적 대조에서 LiveClient는 constructor 실패 시 end_process를 호출하고 callback 예외 뒤 result를 전송하지 않는 것을 확인했다. 따라서 고아 프로세스·거절 후 송신을 실제 발생 결함으로 단정하지 않으며 local fake native 검사를 추가한다. 상세10항목 처분과 Option B의 exact journal spec 결속 계획: `private-evidence/E148`. [공개용 중립화]

현재 focused11/11, 미래R1 1/2, Claude nonmodel11/12·live7/7·Host11/11·bridge8/8·effects4/8이다. Codex C child/parent는 미사용이고 authority0이다. 복구 제안은 focused2(총13), local child최대3, 추가 합성turn/dispatch각12, Rust unit compile1/binary build1이다. 예상 수정·offline120–210분/stop240분과 후속 기존 C30–90분을 분리한다. C 종료20:16:25.572537Z/전체 한도를 늘리지 않는다. 아직 실행 승인·source 수정·재검증·재빌드·Codex launch0이다.

Work Active/partial, 전체 U2 qualification 및 Owner 최종 내용 수락은 미완료다. 현재 도구×OS×profile/H01–H10 경계는 `private-evidence/E147`에 기록했다. 완료 C의 빈 디렉터리5개만 제거했고 활성 경로/worktree/branch 삭제0이다. 정확한 입력·source/binary·journal·원응답·복구 근거는 R1 처분/Codex 보정/Owner 판단 소비를 위해 보존한다. 이후 그 소비가 끝나면 재평가한다. [공개용 중립화]


### R1 Repair Authorized — 2026-10-27 KST

Owner 메시지475146456(2026-10-26T15:18:49.476436Z, “승인”)이 R1 처분의 Option B 복구 묶음을 승인했다. exact journal spec 결속·peer·양성 종료 관측·효과 전 이탈 gate·OS preflight를 수정하고 집중2/compile1/build1/local child최대3 뒤 기존 C 한도에서 이어간다. 수정 전8파일을 기존 durable task의 c-codex-r1-repair/before에 원bytes·mode와 대조해 보존했다. repair stop19:18:49.476436Z/마지막15분 정리이며 기존 C stop20:16:25.572537Z를 늘리지 않는다.

계수 산정에서 기존 Rust6개가 합성turn17/dispatch18인 점을 누락해 제안12/12를 초과함을 실행 전에 발견했다. Python상한12/12와 합쳐 최대29/30이므로 추가 합성 상한30/30 정정을 Owner에게 요청했다. source·fixture 작성은 승인 범위에서 진행하되 답변과 입력 고정 전 검사/child/compile/build는0으로 유지한다. 실제 model/network/auth0이며 검사 종류·실제C·시간 상한을 늘리는 요청이 아니다.

새 template SHA cf51609ec2ff2ebb31525a75620f652060747d098732c2b337afabfb65e9b4df를 Python/Rust 소비자에 반영했다. 작성 중 스크립트 인용 오류는 파일 생성 전에 종료했고, 테스트 초안의 괄호 누락은 AST에서 찾아 입력 고정 전에 보정했다. 고정 검사 실패나 runtime 관측으로 집계하지 않는다.

### R1 Repair Offline Passed; C Controller Ordering Hold — 2026-10-27 KST

Owner `475146456`의 복구 승인과 `232711614`의 합성 계수 각 30 정정 승인으로 v58 start/spec digest, fixed peer, positive process absence, pre-effect tool/ordinal, 4-tool inventory, cleanup capability 검사를 반영했다. Python 집중 10개와 Rust 집중 6개가 모두 통과했고 unit compile 1회와 binary build 1회를 완료했다. 집중 묶음은 전체 13/13이며 추가 합성 예약은 turn 29/30, dispatch 30/30이다. Core/Claude/worker의 영향 없는 증거는 재사용했다. 두 저장소 `git diff --check`도 통과했다.

새 후보는 `private-evidence/E127`에 보존했고 SHA-256은 `6ad2b75866207569851b93cf55dae944afcb25cad03c2a6af7dd09ba60d19033`이다. 테스트 바이너리도 mode/mtime/bytes를 검증해 보존했다. 소유권과 프로세스 부재를 확인한 복구용 cache 및 비사용 scratch만 삭제했다. Python 성공 fixture의 원본은 unittest 명시적 cleanup으로 제거됐으므로 고정 코드·case/event 로그·통과 assertion으로만 주장하며 raw fixture 재생 증거를 주장하지 않는다. [공개용 중립화]

기존 C 승인을 이어 실행했으나 Driver runner가 아직 active인 새 Host에 `recovery()`를 호출해 `recovery-not-stopped`로 중단됐다. `ReadOnlyHost.recovery()`는 stop 후 호출하는 계약이며 제품 결함으로 분류하지 않는다. 실제 native Codex 시작·모델/제공자 전송·dispatch·worker 읽기·권한 효과는 모두 0이다. 프록시 1개는 시작 후 종료했고 FD 요청 0, process group/controller 부재, stopped journal/pending 없음까지 확인했다. 활성화의 2 starts / 4 turns / 6 sends / 4 dispatch / 6 controls / 2 reads / 1 proxy 예약은 소비된 채 보존하며 환급하지 않는다.

실패 runner와 실행 증거는 `private-evidence/E131`에 보존했다. 종료된 전용 socket과 빈 디렉터리 8개만 정리했다. 별도 수정 runner는 시작 전 `check_core()`와 Host 계수만 읽고, stop 이후에만 `recovery()`를 호출하도록 준비했다. 제품 소스·검사·컴파일·빌드를 추가하지 않는다. 새 활성화는 기존 native parent 4/8/12/8/16의 잔여 할당을 쓰되 이미 소비된 부대 예약 때문에 worker reads 누적 2→4, proxy 누적 1→2 승인이 필요하다. 제안서: `private-evidence/E128`. 승인 전 실행 금지, 첫 실패 시 Hold, C 2026-10-27 05:16 KST 종료 한도 유지. [공개용 중립화]

현재 Claude C의 실제 관측 PASS와 D 문서 평가/R1 결과는 유지한다. Codex C 및 전체 qualification/Owner acceptance는 미완료이며 Work는 Active다.


### C Correction Attempt Closed On RPC Failure — 2026-10-27 KST

Owner `314599362`의 수정 실행 1회·부대 상한 승인과 `775002911`의 시간 창 변경 승인으로 같은 소스·후보를 한 번 실행했다. C 마감은 2026-10-27 10:50:06 KST, 전체 마감은 기존 13:15:44 KST다. 시간 회계에서 기록된 Owner 답변 대기만 제외했으며 기존 실패 예약은 환급하지 않았다. 추가 검사·컴파일·빌드·제품 소스 변경은 없다.

수정 runner는 첫 실행의 active Host recovery 호출 오류를 통과했으나, 08:51:37–08:51:54 KST에 `RPC refused or identity drift`로 중단됐다. 실제 native 시작 1회, proxy 시작 1회, models/accounts 제어 요청 2회다. 모델 turn·dispatch·worker 읽기·권한 효과는 모두 0이며 thread-bound도 없다. 이는 초기화 성공 후 account/read 또는 thread/start 구간의 실패로 좁혀지지만 정확한 RPC method/error code는 미보존으로 확정하지 않는다. logs DB는 0행이다. 정적 확인상 FreshCodexSession.close는 LiveClient.close의 RPC metadata 저장을 거치지 않는다. 이 관측 공백을 원인 자체로 단정하지 않는다.

두 활성화의 누적 예약은 starts 4 / turns 8 / sends 12 / dispatch 8 / controls 12 / reads 4 / proxy 2다. 잔여 control 4 외에 새 실행에 필요한 예약은 모두 소진됐다. 실제 사용량이 적더라도 재사용하지 않으며 자동 재시도 금지다. R1 offline PASS·기존 Claude C PASS·D/R1 결과는 보존하되 Codex C와 전체 qualification은 미완료다. Work는 Active이며 Owner acceptance·STATUS·Git publication 변경은 없다.

native/proxy process group 부재를 재확인했고 실행 종료 기록은 pending 없음·stopped 상태다. 보호된 인증 파일의 metadata는 실행 전후 동일하다. 전용 소켓·소유 기록·빈 디렉터리만 총 11개 제거했다. 활성 경로 변경은 없고 source/candidate/activation/journal/native home/결과는 실패 진단과 Owner 판단이 끝날 때까지 기존 위치에 보존한다. 상세 실행 및 정리 결과: `private-evidence/E129`. [공개용 중립화]

다음 판단 대상은 RPC 오류의 비민감 metadata 보존을 위한 offline 보정 범위다. 이는 아직 실행 승인되지 않았으며 새로운 native 활성화·계수·시간 승인을 포함하지 않는다.


### RPC Diagnostics Offline Correction Proposed — 2026-10-27 KST

Owner의 계속 진행 요청에 따라 Python 2파일의 최소 진단 보정 patch를 준비했다. 저장소 소스는 불변이며 AST 문법과 patch 적용 가능성만 확인했고 검사·child·native·model·network·compile·build는 0회다. stage/오류 코드/메시지 hash만 저장하고 기록 실패도 기존 종료를 방해하지 않도록 한다. 과거 RPC 원인은 여전히 미확정이다.

검토용 before/proposed bytes·98행 diff·입력 digest·검사 명세: `private-evidence/E142`. 기존 집중 13/13에 추가 1묶음(새 3개+기존 2개, 총 5 test method)을 제안했다. 합성 RPC 3회, child/native/turn/dispatch/인증/네트워크/build 0회다. 예상 15–25분은 판단 추정이며 stop 40분(정리 5분 포함), 기존 전체 절대 마감과 먼저 도달하는 한도를 적용한다. 첫 검사 실패 시 Hold, 자동 재실행 없음. 현재 범위·추가 계수 승인 대기이며 기존 live 소진 예약·실패 증거·Owner acceptance 상태는 바꾸지 않았다. [공개용 중립화]


### RPC Diagnostics Offline Correction Passed — 2026-10-27 KST

Owner 메시지1022261(2026-10-27T00:11:36.951811Z)의 offline 보정·집중 1묶음 승인을 실행했다. fresh_codex.py의 v58 close에서 기존 RPC stage·initialized/failed·method·id 일치·오류 여부·정수 code·메시지 SHA-256만 private JSON으로 보존한다. raw 응답·오류 문구·계정 식별자·토큰을 기록하지 않는다. 진단 저장에 실패해도 native/FD/Host 종료를 계속하며 이전 실패를 유지한다.

집중 검사 5/5가 한 번에 통과했다. 새 3개와 기존 Host stop 실패·RPC 원문 배제 2개다. 기존 initialize 오류 검사 1회를 재사용하도록 입력 고정 전에 새 사례를 account/read 오류와 thread/start id 불일치 2회로 조정해 합성 RPC 총 3회를 지켰다. 로컬 fixture child·native·model·dispatch·인증·네트워크·compile·build는 모두 0이다. 기존 offline 실행 profile을 변경하지 않았고 집중 묶음 누적은 14/14다. Python 고정 입력 75개와 native 입력 8,676개가 검사 후에도 일치했다. git diff --check를 통과했다. 이번 보정은 Rust 입력을 바꾸지 않아 이전 native build 증거를 재사용한다.

합성 raw fixture의 RPC JSON 4개(mode 0600), write-failure 종료 증거, exact 코드·입력·로그·applied diff를 기존 durable task에 보존했다. 실행 프로세스 그룹 부재를 재확인했고 비사용 빈 home 1개만 삭제했다. 활성 경로·worktree·branch 이동/삭제는 없다. 상세 결과: `private-evidence/E143`. [공개용 중립화]

과거 native RPC 원인은 미확정이며 이번 합성 PASS가 이를 해결하거나 Codex C를 통과시킨 것은 아니다. 기존 소진된 live 예약과 실패 증거는 유지하고 자동 재시도하지 않는다. 후속 native 진단에는 변경된 Python 입력의 새 결속과 별도 활성화·계수 승인이 필요하다. Work Active·Owner acceptance 미완료를 유지하며 STATUS·commit/push 변경은 없다.


### Native Initialization Diagnostic Proposed — 2026-10-27 KST

Owner의 최소 실제 진단 범위·예산 제안 요청에 따라 native 1회에서 initialize/account/read/thread-start까지만 진행하고 종료하는 진단을 제안했다. 실제 모델 turn·dispatch·worker read는 0이며 첫 실패 중단·자동 재시도 없음이다. v58 고정 ALLOCATION 때문에 새 예약 묶음은 starts/turns/sends/dispatch/controls/reads/proxy = 2/4/6/4/6/2/1이고 필요한 누적 상한은 6/12/18/12/18/6/3이다. 기존 controls 상한16의 미사용4를 감안한 해당 상한 증액은2다. 예약은 실제 사용 허가와 구별하며 미사용분도 환급하지 않는다.

예상15–25분,stop40분(정리5분 포함),native수명최대120초를 제안했다. 기존 C10:50:06 KST/global13:15:44 KST를 연장하지 않으며 v58 30분20초 이상 잔여 요구를 만족할 때만 활성화한다. 기존 offline5/5와 native 불변입력을 재사용하며 추가검사/build0이다. 상세: `private-evidence/E139`. 현재 제안만 기록했으며 실행·계수변경·새activation은 승인 전이다. [공개용 중립화]


### Native Initialization Diagnostic Authorized — 2026-10-27 KST

Owner private-approval/O016(2026-10-27T00:44:02.867360Z)이 최소 실제 진단 1회와 필요한 예약 상한 증액을 승인했다. 실제 native 1/proxy 1/초기 통신 최대3, 모델 turn·dispatch·worker read·권한효과0, 첫 실패 중단·자동재시도 없음이다. 고정 예약의 새 누적 상한은 starts/turns/sends/dispatch/controls/reads/proxy = 6/12/18/12/18/6/3이다. 과거 소진분은 유지한다. [공개용 중립화]

기존 C10:50:06 KST/global13:15:44 KST를 유지하며 이번 operational stop은10:24:02 KST, 새 시작 목표한도10:15 KST다. runner는 단일 launch만 호출하고 turn/두 번째 slot이 없음을 정적으로 확인했다. native수명120초,기존initialize30초,전송상한3이며 제품 소스·추가검사·build변경0이다. 실행 전 source/input/auth metadata와 deadline 여유를 다시 확인한다. 승인·고정입력·runner: `private-evidence/E134`. 이 기록 시점에는 아직 activation/native를 실행하지 않았다. [공개용 중립화]


### Native Initialization Diagnostic Identified Tool Tag Loss — 2026-10-27 KST

승인한 실제 진단 1회를 09:51:38–09:51:55 KST에 수행했다. initialize와 account/read는 통과했고 thread/start에서 code -32600, id 일치, RPC error가 관측됐다. 오류 메시지 SHA-256은 `64ceff114d86eaa876847b928064cad8e10cd8cc7c687c646da041c75a9696c3`이며, 고정 native 소스의 `invalid frozen dynamic tools` 문자열과 정확히 일치했다. 현재 거절 지점은 frozen dynamic tool 역직렬화다.

Driver runner가 정본 도구 4개의 type:function 필드를 제거한 것이 현재 정적 인과 사슬과 일치한다. runtime은 이 tag 없는 배열을 frozen inventory로 보존한다. 수신 ThreadStartParams의 legacy 정규화와 달리 prepared expected inventory는 type-tagged DynamicToolSpec으로 직접 역직렬화하므로 필수 type이 없는 배열을 거부한다. runtime 배열에 type:function만 복원하면 정본 4개와 정확히 같음을 정적 데이터 대조로 확인했다. 이는 source/입력 대조이며 추가 Rust 실행 검사를 했다는 뜻이 아니다. 이전 실패도 같은 배열을 썼지만 원 RPC metadata가 없어 동일 오류로 소급 확정하지 않는다.

실제 native1/proxy1/DNS1, models/accounts 제어통신2와 FD 발급·회수 각2다. 모델 turn·generation·dispatch·worker 읽기·권한효과는 모두0이며 첫 실패 후 재실행하지 않았다. 진단 목적은 달성했지만 초기화와 Codex C qualification은 실패/Hold다. 기존 예약은 보존하고 새 고정 묶음을 소비해 누적 starts/turns/sends/dispatch/controls/reads/proxy = 6/12/18/12/18/6/3이며 잔여 실행 예약은0이다.

native/proxy process group와 관측 후손의 부재, controller 종료·leases0, stopped journal·pending 없음, 보호 인증 metadata 불변을 확인했다. 원 source/Python75개/native8,676개/후보/과거 결과는 불변이다. 새 source 수정·검사·compile·build0이다. 종료된 전용 소켓·소유 기록·빈 디렉터리 총11개만 제거했고 활성 경로·worktree·branch는 바꾸지 않았다. 승인·소진 ledger·bounded RPC metadata·native home·원결과는 다음 Owner 처분/보정에 필요한 근거로 보존한다.

상세 원인·종료·정리 결과: `private-evidence/E135`. 다음 최소 보정 방향은 정본 type tag를 보존하는 runner 입력 구성이다. 이번 진단 승인은 그 보정이나 추가 실제 실행을 포함하지 않으므로 아직 적용하지 않았다. Work Active·Owner acceptance 미완료·자동 재개 금지를 유지한다. [공개용 중립화]


### Canonical Tool Tag Correction Applied; Verification Proposed — 2026-10-27 KST

Owner가 정본 도구 type 보존 보정과 최소 검증/재실행 예산 제안을 요청했다. 새 native-init-diagnostic-2 runner는 정본 배열을 그대로 읽고 type:function 4개를 activation 전에 확인하도록 보정했다. tests/test_u2_fresh_repair.py의 동일한 type 제거도 삭제했다. 기존 실패 runner·결과·소진 예약은 보존하고 제품 adapter·native Rust source·binary는 변경하지 않았다. AST/입력 구성의 정적 대조와 git diff --check를 확인했으며 새 검사/native 실행0이다. 원복용 fixture와 적용 diff는 기존 durable task의 새 하위 경로에 보존했다.

추가 집중1묶음(14→15)은 실제4개정본 필드 대조와 기존 Rust 바이너리의 prepared_raw_and_typed_thread_gates_accept_only_the_same_profile 1개(60초)를 결합한다. compile/build0,기존 종료/RPC5/5 재사용이다. 통과한 경우에만 모델없는 초기화1회(native1/proxy1/초기통신최대3/120초)를 제안한다. 필요한 누적 예약 상한 starts/turns/sends/dispatch/controls/reads/proxy는8/16/24/16/24/8/4다. 예상승인후10–15분/stop25분(정리5분포함),C10:50:06/global13:15:44KST불변,activation잔여30분20초초과·운영상10:15KST전시작을 유지한다. 첫 실패Hold·자동재시도없음이며 아직 검사/재실행/상한변경 승인은 없다. 상세: `private-evidence/E138`. [공개용 중립화]


### Canonical Tool Tag Recheck Authorized And Offline Passed — 2026-10-27 KST

Owner private-approval/O019(2026-10-27T01:06:48.482842Z)이 집중1묶음과 통과 시 초기화1회·필요 예약 증액을 승인했다. 고정 Rust test binary에서 prepared_raw_and_typed_thread_gates_accept_only_the_same_profile 정확히1개를 실행해 PASS했다(실행 약3.27초). source/input drift0·binary불변·process group부재이며 네트워크·인증·모델·native agent·compile/build0이다. 기존 offline profile에서 보존 TARGET 쓰기만 제거해 권한을 좁혔다. 집중 누적15/15다. [공개용 중립화]

정본4개 도구를 필드 제거 없이 전달하는 새 runner와 현재 source75개, 검증 결과를 결속했다. 승인 누적 native 예약 상한 starts/turns/sends/dispatch/controls/reads/proxy는8/16/24/16/24/8/4이며 기존 소비6/12/18/12/18/6/3은 환급하지 않는다. operational stop10:31:48KST, 새 시작목표한도10:15KST,기존C10:50:06/global13:15:44KST를 유지한다. 이 기록 시점에는 추가 native 실행0이며 통과한 검증과 남은 보호 시간 조건에서만 초기화1회를 진행한다. 위치: `private-evidence/E136`. [공개용 중립화]


### Canonical Tool Tag Recheck Passed; Policy Admission Hold — 2026-10-27 KST

승인한 focused batch 1회에서 기존 Rust exact case 1/1이 통과했다(3.27초, 누적15/15). 추가 compile/build는0이며 고정 source와 기존 시험 binary가 불변이다. 이 검사는 정본 도구의 raw/typed 일치를 검증하며 전체 native 초기화 성공을 보장하지 않는다.

조건부 실제 초기화 1회는 10:10:55–10:11:13 KST(17.85초)에 실행했다. runtime의 4개 도구가 type:function을 포함한 정본 배열과 정확히 같고 이전 frozen tool 오류는 통과했다. thread/start는 새 오류 code -32600으로 거절됐다. 메시지 SHA-256 `6533fb73c07e24554e50dd7d8b69d4db4da098495d60cd64eee0ae76bed542b4`는 고정 source의 `live thread reservation unavailable`과 일치한다. 초기화 및 Codex C qualification은 실패/Hold다.

관측 기록에는 정책 classification이 known-not-applicable이고 실제 control은 models/accounts 두 건이다. 정적 소스 대조에서 정책 비적용 분기는 policy HTTP fetch를 생략하지만, Python/Rust v58 thread 예약은 policy/models/accounts 세 control을 모두 요구한다. Spec.reserve는 새 thread 행을 기록하기 전에 검증하므로 이 상태가 예약 조건과 충돌한다. 다만 내부 상세 거절 문자열은 보존되지 않았으므로 v58-thread-order를 실행 재현했다고 주장하지 않는다. 첫 실패 이후 추가 시험·reducer 실행·소스 보정·native 재시도는0이다.

실제 native1/proxy1/DNS1, 제어통신2, FD 발급·회수 각2이며 모델 turn·generation·dispatch·worker 읽기·권한효과는0이다. 새 고정 예약을 전부 소비해 누적 starts/turns/sends/dispatch/controls/reads/proxy=8/16/24/16/24/8/4, 잔여 예약0이다. focused batch 누적도15/15로 잔여0이다. 이전 소진 기록과 결과를 보존하며 환급하지 않는다.

native/proxy/시험 process group 부재와 native 관측 후손 부재, controller 종료·leases0, stopped journal·pending 없음, 보호 인증 metadata 불변을 확인했다. 고정 Python75개/native8,676개/후보/과거 결과 불변을 재확인했다. 승인·고정 입력·시험 로그·RPC metadata·native home·journal·종료 결과는 Owner 처분과 후속 계약 보정의 근거로 보존한다. 종료된 소켓·소유 기록·빈 디렉터리와 시험이 만든 빈 lock 및 binary symlink만 제거했다. 활성 경로·worktree·branch는 변경하지 않았다. 정확한 대상과 수량은 cleanup.json에 기록했다.

상세 결과: `private-evidence/E137`. 다음 방향은 검증된 정책 비적용 상태를 Python/Rust 예약 계약에 명시적으로 표현하는 보정이다. 가짜 정책 통신 기록이나 검증 조건의 임의 완화로 우회하지 않는다. Work Active·Owner acceptance 미완료·자동 재개 금지를 유지한다. [공개용 중립화]


### Policy Admission Repair And Time Budget Proposed — 2026-10-27 KST

Owner 요청으로 정책 비적용 상태의 Python/Rust 계약 보정과 검증·재실행 예산을 제안했다. 실제 HTTP control과 성공한 native policy snapshot classification을 별도 policy-admission event로 구분한다. applied/applicable-empty는 실제 policy+models+accounts, known-not-applicable은 models+accounts와 검증된 비적용 admission을 요구한다. 새 event는 start당1·activation당2이고 HTTP/모델/효과 예산에 포함하지 않는다. 두 reducer·새 template digest·fixture·새 후보를 함께 결속하고 과거 기록은 보존한다. 소스 변경이나 새 검사/실행/상한 변경은 아직0이다.

A 권고: focused2(15→17), method6·공유 prefix vector20·초기화-only local child2/RPC≤6, 합성 turn/dispatch0, unit compile1+binary build1. 기존 Core/Claude·RPC/도구정본·변경없는 효과/인증/FD/종료 증거를 재사용한다. 예상35–60분/누적stop90분(마지막10분 정리),global13:15:44KST 유지. 기존 Rust compile257.95초/build25.65초/cacheclone154초를 측정 근거로 쓰고 구현·결속은 판단치다. 작업/도구대기를 포함하고 중첩1회,Owner-only 대기제외이며 절대마감은 연장하지 않는다.

기존 C10:50:06KST와 activation여유30분20초에 따른 시작기한10:19:46은 이미 지났으므로 현 조건의 보정 후 live는 불가능하다. 선택B는 A통과 후 초기화native1/proxy1/DNS1/HTTP≤3/120초/model0, 추가예약2/4/6/4/6/2/1(새누적10/20/30/20/30/10/5),C2시간연장12:50:06KST와phasecap6→8h의 명시적 승인 조건이다. 기존phasecharge·소비를 환급하지 않는다. A+B예상45–75분/누적stop120분,준비기한min(승인+100분,12:15KST),A90분stop·전체20h/global13:15:44유지. 첫실패Hold·자동재시도0·전체Cqualification/리뷰/commit/push/acceptance제외다.

정확한 범위·위험·원복·20vector 목록과 예산은 `private-evidence/E140`에 있다. 현 Work Active·C Hold·자동재개금지를 유지한다. [공개용 중립화]


### Policy Admission A+B Authorized — 2026-10-27 KST

Owner private-approval/O018이 제안 A+B를 승인했다(10:26:05 KST). 보정/검증 focused2(누적17), compile1/build1/합성child2/RPC≤6/합성turn·dispatch0, 통과와 준비기한 조건의 실제 초기화1회를 허용한다. C12:50:06 KST·phasecap8시간으로 연장하되 기존 phase charge와 소진 예약을 유지한다. 전체20시간·13:15:44 종료는 불변이다. offline stop11:56:05(새 작업11:46:05), A+B stop12:26:05, live 준비기한12:06:05 KST다. 첫 실패Hold·자동retry/rebuild0이며 준비기한 초과 시 offline 결과만 보존한다. 현재 소스 보정/검사/native 추가실행은0이다. 승인과 보정 전 파일/metadata는 기존 durable task의 c-execution/policy-admission-repair에 보존했다. [공개용 중립화]


### Policy Admission Repair And Initialization Passed — 2026-10-27 KST

승인한 A+B 범위를 완료했다. Python/Rust focused2묶음에서 method6/6이 통과했고, 공유 prefix20개를 각 언어에서 검증했다. Rust unit compile1회와 후보 build1회도 통과했다. 합성 통합은 기존 second-slot 완료 조건을 완화하지 않기 위해 독립된 fresh epoch2개에서 적용/비적용 초기화를 검사했다. local child2·합성RPC6·합성turn/dispatch0이며, 같은 epoch의 연속 두 slot 새 실행으로 주장하지 않는다. 그 연속 실행·read/refusal·Core/Claude·변경 없는 인증/FD/종료 증거는 기존 결과를 재사용했다.

native의 검증된 policy snapshot freeze 이후 policy-admission을 기록하고, Python/Rust가 HTTP control과의 대응을 확인하도록 보정했다. 적용/적용-empty는 policy+models+accounts, 비적용은 models+accounts와 비적용 admission을 요구하며 누락·중복·충돌·순서/결속 오류를 거절한다. v1–57의 동작과 정책 applicability/auth/HTTP sender/FD/종료/time guard는 변경하지 않았다. 새 template SHA는 2b3bf8ee01db992d066fbb4fd9ea43a8a6663e997bcecba4b5d20796d705ab5c, 새 native source identity는 3d2eb4094292eab4881d3440f2cd0d36aec4d3f2be539f2d718d516aa9e80794, 후보 SHA는 ce093f6439f4e67335f5a13c3c8b8492b4f1b7bf92d6ea2a156625049238aaa9다. 고정 Python75개/native8,676개와 이전 결과가 검증·실행 후에도 불변임을 확인했다.

실제 초기화1회는 10:52:25–10:52:45 KST에 수행해 PASS했다(약19.80초). 관측된 classification은 known-not-applicable이고 실제 HTTP는 models/accounts2건, policy-admission1건, thread/thread-bound 각1건이다. RPC metadata는 initialized=true, thread/start, rpc_failure=null이다. 모델turn·generation·dispatch·worker읽기·권한효과·Host요청/효과는0이며 pending 없음으로 종료했다. native/proxy 각1회, FD 발급·회수 각2, process group와 관측 후손의 부재, controller종료·leases0, 인증 metadata불변을 확인했다. 추가 재실행은0이다.

고정 예약 누적 starts/turns/sends/dispatch/controls/reads/proxy=10/20/30/20/30/10/5, 잔여0이며 focused17/17도 잔여0이다. 기존 소진과 phase charge를 유지하고 승인된 C12:50:06 KST·phasecap8시간, 전체20시간·13:15:44 종료를 지켰다. 준비기한12:06:05 전에 실행했다. 이번 범위 소요는 약32.6분이며 A+B120분 상한 안이다.

후보/시험 binary와 원시 합성 증거49개, 변경 전8파일, 승인·template·입력·native journal·종료 결과를 보존했다. 복제 cache·build scratch·중복 실행 사본7개와 종료된 소켓/소유 기록/빈 directory/시험 lock·symlink 19개, 합계26개 경로를 정리했다. 후보의 향후 활성 경로는 이 task의 outputs 아래로 고정했으며 원본 cache·과거 후보·기존 실패 기록·source worktree·branch는 보존했다. Worktree는 별도 전체 C qualification과 Owner 처분의 실제 후속 경로이므로 유지한다.

결과: private-evidence/E141 A+B 보정·초기화 범위는 완료했지만 전체 Codex C qualification과 Owner acceptance는 아직 완료하지 않았다. 적용/적용-empty의 실제 native 관측은 없고 이번 live는 비적용 초기화만 증명한다. 모델/tool을 포함한 C 후속은 별도 범위와 새 예약이 필요하다. Work Active·자동재개금지, commit/push/Done 미실행을 유지한다. [공개용 중립화]

### Full Codex C Qualification Minimum Proposal — 2026-10-27 KST

Owner 요청 814975815에 따른 제안이다. 실행 승인·새 예약 소비·기한 변경은 아직 없다. 최소 남은 범위는 새 activation1회, 같은 epoch/Host config/Core/ledger와 살아 있는 proxy1개 아래 fresh native2개를 순차 실행하는 것이다. 각 slot은 정상 합성 Reference 읽기1회(최대 generation2) 뒤 Outside 읽기 거부1회(generation1)를 수행한다. Host terminal refusal을 fsync한 뒤 tool result/interrupt/추가 송신 없이 native를 TERM10초→KILL10초로 종료하고 process group/관측 후손 부재와 pending 없음 확인 후 fresh ReadOnlyHost로 slot2를 시작한다. 예상된 범위 거부는 검증 대상이며 첫 예상 밖 실패·drift·timeout은 정리 후 Hold, 재시도0이다.

Evidence Reuse: policy-admission repair Python/Rust method6/6, 공유 prefix20개씩, unit compile1/build1, 실제 비적용 초기화1회와 RPC/인증/FD/종료 증거를 재사용한다. 기존 같은 epoch 두 slot의 합성 계약 검사 및 변경 없는 Core/Claude/종료 경계 증거, 이미 통과한 Claude C도 재사용한다. 이번 초기화 PASS를 실제 모델/tool qualification이나 같은 epoch의 두 native 성공으로 확대하지 않는다. 제품 소스·template·후보 binary 변경0, 새 focused test/compile/build/full suite/review0이다. 새 runner의 AST·고정 입력 hash·예약 산술·종료 조건은 정적으로 확인한다. 별도 초기화 smoke는 없고 실제 두 slot 안에 초기화를 포함한다.

Candidate: policy-admission-repair/outputs/codex-prepared-tool-plan-live SHA ce093f6439f4e67335f5a13c3c8b8492b4f1b7bf92d6ea2a156625049238aaa9, template SHA 2b3bf8ee01db992d066fbb4fd9ea43a8a6663e997bcecba4b5d20796d705ab5c, source identity 3d2eb4094292eab4881d3440f2cd0d36aec4d3f2be539f2d718d516aa9e80794를 그대로 쓴다. 승인 후에만 기존 task c-execution/full-c-qualification 아래 새 runner/고정 입력/승인 결속/activation/journal/로그/결과를 작성한다. 기존 run-init.py의 검증된 초기화·auth·accounting·RPC diagnostics와 과거 qualification runner의 두 slot read/refusal 순서를 결합하되 과거 runner를 그대로 재실행하지 않는다. 시작 전 check_core(), 정지 후 recovery(), canonical tool type, 이전 소진5건과 누적 시간 charge를 유지한다. source/입력 drift나 정적 확인 실패는 제품 수정·재빌드로 확대하지 않는다.

| Reservation | Consumed | Additional | New C Cumulative Limit |
| --- | ---: | ---: | ---: |
| Native starts | 10 | 2 | 12 |
| Model turns | 20 | 4 | 24 |
| Provider sends | 30 | 6 | 36 |
| Host dispatch | 20 | 4 | 24 |
| HTTP controls | 30 | 6 | 36 |
| Worker reads | 10 | 2 | 12 |
| Proxy starts | 5 | 1 | 6 |

새 activation 소비 시 전량 예약하고 실패·미사용분도 환급하지 않는다. policy-admission2건은 HTTP/effect가 아닌 별도 journal 사건으로 기존 v58 한도 안에서 기록한다. 실제 controls는 slot별 classification에 따라 비적용=models/accounts2, 적용 또는 적용-empty=policy/models/accounts3이므로 합계4–6이다. 모든 event count를 LIMITS와 기계적으로 같다고 요구하지 않고 실제 slot별 admission/control 집합과 고정 필수 사건을 검사한다. 적용 상태를 만들기 위해 계정/정책을 바꾸지 않는다. authority apply/recovery apply/content correction0, 기존 개인 native 인증·gpt-6-astra/xhigh·승인된 peer와 합성 입력만 유지한다.

Time Budget: 기존 예상30–90분은 준비·모델2slot·정리/보고를 포함한 판단치이고 모델 수행 실측은 없다. 초기화19.8초는 모델 시간 추정 근거로 쓰지 않는다. 실행 상한을 예상 시간으로 표현하거나 75분 내 완료를 보장하지 않는다. 승인 후 준비 최대15분, live 최대45분, 정리/증거 확인 최대15분, 합계75분의 새 범위 wall-clock cap을 제안한다. 이 범위의 승인 대기는 75분에 포함하지 않지만 기존 C/global 시계는 계속 흐른다. 내부 대기와 겹치는 작업은 한 번만 계산한다.

절대 기한이 먼저 적용된다. 새 activation은 min(승인+15분, 11:35 KST) 전에만 허용하고 준비기한을 넘으면 실행하지 않는다. live는 min(activation+45분, 12:15 KST)에 종료를 개시하도록 native/proxy/controller watchdog을 함께 제한한다. native 기존 lifetime29분40초/turn15분/초기화30초는 늘리지 않는다. cleanup/증거 정리는 min(승인+75분, 12:30 KST)까지 마치며 새 작업이 들어갈 수 있는 시간만 줄어든다. 기존 non-closeout 사건은 C 종료30분 전보다 이른 12:20:06 전에만 허용하므로 12:15 운영 cutoff를 둔다. 정리 의무는 timeout 뒤에도 남으며 남은 C 예약 여유에서 종료·부재·pending 확인만 수행한다. C 종료12:50:06·phase cap8시간, 전체20시간·13:15:44 종료는 유지하고 연장0이다. 11:35 시작이면 live는 최대40분으로 줄어들어 네 turn의 최악60분을 보장할 수 없다. 시간 부족/첫 실패 시 부분 증거만 보존하고 전체 qualification을 PASS로 표시하지 않는다.

Pass Criteria: 실제 native2/turn4/positive generation4+refusal generation2/dispatch4/worker read2/Host completed2+refused2/process-ended2와 각 slot의 policy-admission/thread-bound를 연결한다. 두 정상 응답은 accepted_work_state=completed, follow_up_kind=proposal, follow_up_execution_authorized=false의 고정 JSON을 만족해야 한다. 잘못된 tool/인자, 대체 읽기, text-only 응답 또는 JSON 불일치를 수정 prompt로 보완하지 않는다. Core snapshot/auth metadata 불변, pending 없음, 최종 execution-stop, 양 native 및 proxy/controller 종료·부재, leases0을 확인해야 전체 C 실행 PASS다. Host crash recovery나 실제 적용/적용-empty 정책의 live 검증으로 확대하지 않는다. 결과 PASS와 Owner acceptance/Work Done은 별개다.

Risk And Reversal: 실제 모델 순응성과 수행 시간은 미관측이며 단1회 실행이므로 완료를 보장할 수 없다. 되돌리기 비용은 소비한 모델·예약·시간이며 환급하지 않는다. 실패 결과와 고정 입력은 원래 위치에 보존하고 제품 소스 변경은 없다. 사용이 끝난 task 소유 socket/빈 scratch만 positive 종료와 보존 확인 후 정리한다. 후보·증거·source worktree는 이 qualification 및 Owner 처분까지 유지한다. 현재 Work Active/자동재개금지이며 commit/push/Done/배포는 포함하지 않는다.

### Full Codex C Qualification Authorized And Ready — 2026-10-27 KST

Owner private-approval/O002가 최소 1회 qualification과 추가 예약·75분 상한을 승인했다. 승인 시각은 수신 기록의 보수적인 초 단위 11:18:32 KST, 준비 기한은 11:33:32 KST다. 준비 중 기존 Python75개/native8,676개와 후보·template·기존 결과 hash, canonical tool type, 이전 process group 부재, runner AST·호출 순서를 정적으로 확인했다. 새 시험·컴파일·빌드·review는0이다. 새 runner SHA 86be99e910a6d89a055c2bd1ce1ee70e83c68d491d856c1345652bc8c354ab9b와 승인 결속을 private-evidence/E133 고정했다. 누적 한도12/24/36/24/36/12/6을 승인에 따라 기록했으며 기존 소진10/20/30/20/30/10/5는 유지한다. activation 소비는 실제 실행 admission에서만 한다. live 최대45분 및12:15 cutoff, 정리12:30, C12:50:06/8시간·전체13:15:44/20시간, 첫 실패 중단·재시도0을 유지한다. 아직 native 실행은 시작하지 않았고 실제 결과는 후속 기록으로 구분한다. [공개용 중립화]

### Full Codex C Qualification Postcheck Hold — 2026-10-27 KST

Owner private-approval/O002가 승인한 activation1회를 실행했고 최종 판정은 Hold다. 실제 실행은 11:23:42–11:24:48 KST, 약66.05초였다. runner는 PASS를 반환했지만 종료 후 evidence 대조에서 두 번째 negative의 거부 사유가 file-scope가 아니라 effect-slot-budget임을 발견했다. 원래 runner/result와 실패한 closeout.py·AssertionError 조건은 그대로 보존하고 closeout-failure.json에 최종 판정 근거를 기록했다. 추가 native 실행·보정·재시도는0이다. [공개용 중립화]

원인은 Host dispatch가 file-scope보다 effect-slot-budget을 먼저 검사하는 순서다(contracts.py 1096→1102). 정상 읽기2회로 effect_limit2가 소진되어 두 번째 Outside 요청은 scope 검사에 도달하지 못했다. runner는 durable refusal·추가 효과0·프로세스 종료를 검사했지만 정확한 거부 사유를 검사하지 않아 과도한 PASS를 반환했다. 첫 refusal은 file-scope이고 둘째는 effect-slot-budget이다. 정상 읽기2회, 같은 epoch/proxy의 fresh native 재개, 추가 effect 없는 두 차단은 관측했지만 scope refusal2회를 입증하지 못했으므로 전체 C qualification PASS로 수락하지 않는다. 계약·예산을 완화하거나 실패한 qualification을 재실행하지 않았다.

실제 native2/model turn4/provider send6/dispatch4/worker read2/refusal2/process-ended2와 journal45행을 보존했다. 두 정상 응답은 completed/proposal/follow_up_execution_authorized=false의 고정 JSON과 일치했다. Host completed2/refused2 및 terminal 결속4건, 거부 뒤 추가 generation 없음과 첫 native 종료 뒤 두 번째 시작을 대조했다. 두 slot 모두 known-not-applicable, policy-admission2/HTTP control4(models/accounts 각2)이며 적용 상태의 live 증거로 확대하지 않는다. RPC failed=true는 의도한 RefusedTurn 종료에서 생긴 상태이고 rpc_failure는 두 slot 모두 null이다.

실패 후 남은 작업은 종료·보존 검증으로 제한했다. Core snapshot과 인증 metadata10개 및 현재 metadata 불변, FD 예약/발급/회수 각10·leases0, pending 없음과 execution-stop, native2·worker2·proxy1 process group의 부재 및 관측 native 후손 부재, controller 종료를 확인했다. 권한 적용·복구 적용·내용 보정은0이다. 기존 Python75개/native8,676개·후보·template·이전 결과 hash가 불변이며 기존 Claude C PASS와 offline 결과는 재사용했다. 새 시험·compile·build·review는0이다.

누적 예약 starts/turns/sends/dispatch/controls/reads/proxy=12/24/36/24/36/12/6, 잔여0이며 미사용분은 환급하지 않았다. 준비기한11:33:32 전에 시작했고 live cutoff 2026-10-27T03:08:42.823000+00:00, 새 범위75분·C12:50:06/8시간·전체13:15:44/20시간 안에서 실행·종료했다. 승인부터 이 closeout까지 약13.2분이다. 첫 최종 검증 실패 후 추가 실행은 하지 않았다.

닫힌 task socket/소유 기록/빈 directory 17개를 정확히 확인해 정리했고 활성 경로 변경은 없다. 원래 PASS 결과·실패 검증·최종 Hold, 승인·고정 입력·activation·native/Host/FD/모델 결과와 격리 native home, 기존 후보·source worktree는 Owner의 Hold 처분과 필요한 review/recovery 증거로 보존한다. 처분 후 소비가 없으면 재평가한다. 기존 실패 기록은 덮어쓰지 않았다.

결과: private-evidence/E132 Codex C qualification은 postcheck Hold, Claude C는 기존 PASS이며 Owner acceptance/Work Done은 미완료다. Work Active·자동재개금지, commit/push/Done/배포 미실행을 유지한다. 현재 승인 범위에는 추가 실행이 없으며 보정·재실행은 별도 최소 제안과 승인이 필요하다. [공개용 중립화]

### Scope Refusal Precedence Repair Proposal — 2026-10-27 KST

Owner가 요청한 두 번째 scope refusal의 최소 보정·검증·재실행 제안이다. 아직 실행 승인은 없으며 이 기록 외에 소스·runner·예약·실행 상태를 바꾸지 않는다. 직전 full-c-qualification의 최종 Hold와 원래 runner PASS, postcheck 실패 및 모든 소비 기록은 보존한다.

Minimal Correction: qualification용 shared ReadOnlyHost의 contracts.py에서 결합된 `not self.slot and self.effects < effect_limit` 검사를 분리한다. 이미 사용한 step slot 거절은 현재 위치에 유지하고, 누적 effect budget 검사는 tool/arguments/file-scope 또는 verifier-scope 검사 직후, controller 확인·effect journal·worker dispatch 직전에 둔다. 따라서 두 번째 Outside는 effect_limit2가 소진된 상태에서도 file-scope로 거절하고, 동일 상태의 허용된 Reference 또는 유효한 verifier 요청은 effect-slot-budget으로 거절한다. effects2/request4·native 예약을 늘리거나 reset하지 않는다. identity/Core/session/duplicate/closed/pending/slot guards, effect 예약과 worker 호출 전의 budget 강제는 유지한다. 달라지는 의미는 예산 소진과 부적합 scope가 함께 있을 때의 거부 사유 우선순위이며 read/verify 공통 qualification Host에 적용된다. 생산 Core·Rust native·정책 admission·FD·인증은 변경하지 않는다.

기존 integration fixture의 기본 effect_limit4가 실제 live의2와 달라 원인을 놓쳤다. 해당 두 slot 검사는 effect_limit2로 명시하고 각 slot의 Host terminal.code와 native host-refusal.reason이 모두 file-scope인지, effect와 worker 호출이 늘지 않는지 검사한다. 기존 검사 목록의 나머지 fixture 기본값은 넓게 바꾸지 않는다.

Runner Correction: 새 task 전용 runner는 각 negative turn 종료 직후, 다음 slot이나 전체 PASS 판정 전에 요청의 Outside 인자·Host terminal/request hash·native host-refusal 연결과 두 사유 file-scope, 추가 효과0을 확인한다. effect-slot-budget 등 다른 사유는 즉시 Hold다. 동일 검사 함수를 offline oracle 검사와 실행 중 판정에 사용하고, 잘못된 사유·결속을 가진 입력을 거절하는지 확인한다. 최종 closeout은 별도로 같은 terminal 결속을 대조한다. 모델 prompt·정상 JSON·2개 native/각2turn 흐름과 같은 proxy 유지·거부 뒤 전송0은 그대로다.

Files: C worktree의 docs/development/verification/u2-host/contracts.py, tests/test_u2_adapters.py, tests/test_u2_fresh_repair.py 세 파일과 기존 Work 기록. 새 task-owned runner/oracle/검사 입력·결과는 기존 durable task c-execution/scope-refusal-repair 아래에 작성한다. 승인 후 변경 전 세 파일의 byte/metadata를 보존하고 기존 Python 입력 manifest에 정확한 세 파일 delta를 결속한 새 snapshot을 만든다. 이전 manifest·결과는 고치지 않는다. Rust source/template/binary identity는 그대로 유지한다. 이전 live 입력은 그대로 재실행하지 않고 새 approval/input identity/activation으로 결속한다.

Focused Verification: Python focused batch1회, 고정 method12개를 failfast로 각1회 실행한다. 기존 ReadHostTests9개(읽기 결속/identity·scope/session/fsync/동시 slot/stop·revoke/unknown effect/fresh budget·config/journal/Core)를 재사용 실행하고, 효과 예산 소진 뒤 scope precedence와 유효 요청의 budget 거절을 함께 확인하는 새 Host 회귀1개를 추가한다. 보강한 RepairTests.test_real_launch_register_refusal_and_two_slots1개, task-local runner refusal oracle의 정상·잘못된 사유/결속 입력 검사1개를 포함한다. 같은 상속 test를 중복 collection하지 않는다. 총12개이며 새 focused 누적 한도17→18, 실패 시 이후 method와 native를 실행하지 않는다. batch timeout180초, 합성 Python child2개/초기화RPC6/모의turn4(prepare/start 요청8), 실제 native/model/network/auth0이다. raw fixture와 stdout/stderr는 durable directory에 보존하고 준비 때 기존 sandbox와 subprocess allowlist를 그대로 적용한다. 새 Rust test/compile/build/full suite/formal review는0이다.

Evidence Reuse: native candidate ce093f6439f4e67335f5a13c3c8b8492b4f1b7bf92d6ea2a156625049238aaa9, template2b3bf8ee01db992d066fbb4fd9ea43a8a6663e997bcecba4b5d20796d705ab5c, native source3d2eb4094292eab4881d3440f2cd0d36aec4d3f2be539f2d718d516aa9e80794와 기존 policy Python/Rust 검증·compile/build·init 증거를 재사용한다. 직전 실제 두 세션의 정상 읽기/JSON·fresh resume·policy·auth/Core·FD·종료 증거는 관측된 부분에 한해 재사용하며 두 번째 scope refusal의 성공으로 바꾸지 않는다. Claude C는 기존 revision의 통과 증거로 보존하고 새 Host의 변경된 거부 우선순위는 이번 공통 Host focused 검사로 확인한다. Claude native 재실행은0이다.

Conditional Live: focused12개와 고정 입력/AST/권한·인증 admission이 모두 통과하고 준비기한 안인 경우에만 새 activation1회를 소비한다. 같은 epoch·proxy 아래 native2개, 각 정상 read1+Outside negative1을 다시 실행해야 한다. 이전 epoch의 첫 slot과 새 slot을 합쳐 연속 두 slot 성공으로 주장할 수 없으므로 한 slot만 재실행하는 축소안은 채택하지 않는다. 실제 worker read2/effect_limit2/request_limit4를 유지한다. 첫 예상 밖 실패·drift·timeout에서 정리·Hold, 재시도/모델 보정 prompt0이다.

| Reservation | Consumed | Additional | New C Cumulative Limit |
| --- | ---: | ---: | ---: |
| Native starts | 12 | 2 | 14 |
| Model turns | 24 | 4 | 28 |
| Provider sends | 36 | 6 | 42 |
| Host dispatch | 24 | 4 | 28 |
| HTTP controls | 36 | 6 | 42 |
| Worker reads | 12 | 2 | 14 |
| Proxy starts | 6 | 1 | 7 |

policy-admission2건은 기존 v58 계약의 non-HTTP 사건이며 실제 controls는 classification에 따라4–6이다. 새 activation 소비 시 전량 예약하며 이전6개 소비 및 실패·미사용분은 환급하지 않는다. authority apply/recovery apply/content correction0, 동일 개인 native 인증·gpt-6-astra/xhigh·고정 peer·합성 입력을 유지한다. offline local child2는 native 예약과 구분한다.

Time Budget: 예상20–35분은 직전 실제 live66초·준비/대조/정리 포함13.3분에 이번 소스/회귀/oracle 작성과 검증 여유를 더한 판단치다. 모델 실행66초는 한 번의 관측이고 상한이나 반복 보장이 아니다. 새 범위 누적 wall-clock cap45분(준비/보정/focused/입력 고정≤15분, live≤20분, 종료/대조/정리≤10분)을 제안한다. 승인 대기는 새45분에 포함하지 않지만 기존 C/global 시계는 계속 흐르며 내부 대기/겹치는 시간은 한 번만 계산한다.

준비·activation 기한은 min(승인+15분, 11:55 KST)다. 기한을 넘기면 소스/검사/준비 결과만 보존하고 native 실행은0이다. live cutoff는 min(activation+20분, 12:15 KST), closeout은 min(승인+45분, 12:30 KST)다. 기존 native lifetime29분40초/turn15분/init30초는 늘리지 않고 전체 live20분이 더 일찍 적용되면 그 시각에 종료한다. 네 turn의 최악60분은 허용하지 않으므로 지연 시 완료 보장 없이 Hold로 남긴다. 기존 non-closeout 30분 여유 때문에 일반 실행 사건은12:20:06 전이어야 하며12:15 운영 cutoff를 유지한다. timeout 후에도 필수 정지·부재·pending 확인은 남은 C 여유 안에서 완료하되 새 실행은 하지 않는다. C 종료12:50:06·phase cap8시간, 전체20시간·13:15:44 종료는 연장하지 않는다.

Risk And Disposition: 공통 Host의 오류 우선순위가 바뀌므로 영향을 받는 read/verify·slot·budget·resume 경계를 focused로 확인한다. 효과 허용량을 늘리지 않아 추가 읽기를 성공시키는 보정은 아니다. source rollback은 보존한 세 파일 단위로 가능하나 자동 rollback/재실행은 하지 않는다. 기존·새 예약과 실제 시간/모델 비용은 되돌릴 수 없다. 이번 제안의 승인 단위는 최소 소스/runner 보정 + focused1묶음/12methods + 통과 시 native qualification1회 + 추가 예약 + 45분 cap이며, 결과 Owner acceptance/Work Done/commit/push/배포는 별도다.

### Scope Refusal Repair Authorized And Ready — 2026-10-27 KST

Owner private-approval/O013 승인으로 세 파일 최소 보정과 집중12개를 각1회 실행해12/12 PASS했다. 로컬 합성 child2/initRPC6/모의turn4, 실제 native/model/network0이며 효과 한도2 뒤 file-scope와 유효 요청의 effect-slot-budget 거절, 같은 epoch 두 slot 및 oracle의 잘못된 사유/결속 거절을 확인했다. 기존 Rust source/template/binary는 불변이며 새 Python manifest delta와 task oracle을 결속했다. runner SHA d2f0cc2f5dfbb78d55df99e5795feca978556587961f1be8c93f3654f4b66822; 준비기한11:55, live20분/12:15 cutoff, closeout12:30, C12:50:06/8시간·전체13:15:44/20시간 유지. focused18회 누적소진, native 누적 한도14/28/42/28/42/14/7은 승인 반영했고 기존 소진12/24/36/24/36/12/6은 유지한다. 실제 native는 아직 시작하지 않았으며 고정 입력은 private-evidence/E146 보존했다. [공개용 중립화]

### Scope Refusal Repair And Codex C Qualification Passed — 2026-10-27 KST

Owner private-approval/O013가 승인한 최소 보정·집중 검증·조건부 native 실행1회를 완료했다. qualification용 shared ReadOnlyHost의 이미 사용한 step slot 거절은 유지하고 effect budget 검사를 tool/arguments/file·verifier scope 뒤, effect journal/worker 호출 전에 배치했다. effect_limit2/request_limit4와 기존 identity/Core/session/duplicate/pending 경계를 유지했다. 새 runner는 각 negative 직후 Outside 요청·Host/native terminal 결속·두 사유 file-scope·추가 효과0을 검사한 뒤 다음 slot 또는 PASS로 진행한다. 실제 수정은 contracts.py와 test_u2_adapters.py/test_u2_fresh_repair.py 세 파일이며 변경 전 bytes/mode/mtime와 delta를 보존했다. [공개용 중립화]

고정 focused12개를 batch1회로 실행해12/12 PASS했다. 기존 ReadHostTests9개, effect budget 소진 뒤 scope precedence 및 유효 요청/사용 slot의 budget 거절 회귀1개, effect_limit2로 보강한 같은 epoch 두 slot 합성 통합1개, runner oracle의 정상 및 잘못된 사유·결속 검사1개다. local Python child2/initRPC6/모의turn4(prepare/start RPC8), 실제 native/model/network/auth0이고 원시 fixture 92개를 보존했다. 추가 compile/build/full suite/formal review는0이다. 이전에는 fixture의 기본 effect_limit4가 live의2와 달랐으나 이번 통합은2로 일치시켰다.

준비는11:52:20 KST에 완료했고 준비기한11:55 전에 실제 실행을 시작했다. native 실행은11:53:01–11:54:06 KST, 약64.22초였다. 같은 epoch/proxy 아래 fresh native2개가 정상 read→Outside negative→종료를 순서대로 수행했다. 두 Host refusal code와 native reason이 모두 file-scope이고 추가 효과0임을 runner와 별도 postcheck에서 각각 확인했다. 두 번째 요청이 effect-slot-budget에서 먼저 차단됐던 과거 결과는 Hold로 그대로 남으며 이번 새 결과로 덮어쓰지 않는다.

실제 model turn4/provider send6/dispatch4/worker read2/file-scope refusal2/process-ended2, native journal45행과 Host completed2/refused2/terminal 결속4건을 확인했다. 두 정상 응답은 completed/proposal/follow_up_execution_authorized=false의 고정 JSON과 일치하고 거부 뒤 추가 generation은0이다. 첫 native의 종료·부재 이후에만 같은 proxy로 두 번째 fresh native/ReadOnlyHost generation을 시작했다. 두 slot 모두 known-not-applicable, policy-admission2/HTTP control4(models/accounts 각2)다. 적용/적용-empty는 기존 offline 증거이며 실제 관측으로 확대하지 않는다.

Core snapshot, 인증 metadata10개 및 종료 후 현재 인증 metadata 불변, FD 예약/발급/회수 각10·leases0, pending 없음·execution-stop, native2/worker2/proxy1 및 local focused 관련 process group 부재를 확인했다. native 관측 후손도 부재이며 controller를 종료했다. RPC failed=true는 의도한 RefusedTurn 종료이고 rpc_failure는 두 slot 모두 null이다. 권한 적용·복구 적용·내용 보정·재시도는0이다.

기존 native source/template/binary 및 과거 결과는 hash 불변이다. Python source는 승인된 세 파일 delta만 새 입력 manifest에 결속했다. 기존 policy/Rust/빌드 및 직전 부분 live 증거를 재사용했고 Claude C는 이전 Host revision의 native PASS 증거로 보존했다. 이번 shared Host 변경 경계는 공통 focused 검사로 확인했으며 Claude native를 새로 실행한 것으로 주장하지 않는다.

누적 예약 starts/turns/sends/dispatch/controls/reads/proxy=14/28/42/28/42/14/7, focused18/18이며 잔여0이다. 이전6개 activation 소비와 미사용 예약을 환급하지 않았다. 승인부터 closeout까지 약9.3분으로45분 cap 안이고, live20분/12:15 cutoff·closeout12:30·C12:50:06/8시간·전체13:15:44/20시간을 유지했다. 실제 live cutoff는 2026-10-27T03:13:01.942000+00:00였다.

닫힌 socket/소유 기록/빈 directory 및 canonical copy와 byte/metadata를 확인한 중복 검사 plan, 합계19개 경로를 정리했다. 활성 경로 변경은 없다. 세 파일의 변경 전 사본, 고정 runner/oracle/입력, raw focused/native/Host/model/FD/종료·검증 결과, 격리 native home과 기존 후보/source worktree는 Owner 결과 수락·처분과 review/recovery 증거를 위해 유지한다. 처분과 소비 종료 후 정리 여부를 재평가한다.

결과: private-evidence/E144 이번 최소 보정과 Codex C qualification 실행은 PASS이며 승인 범위의 추가 실행은 남지 않았다. Owner acceptance/Work Done은 별도다. Work Active·자동재개금지, commit/push/Done/배포 미실행을 유지한다. [공개용 중립화]


## Owner Acceptance And Completion Criteria Audit — 2026-10-27 KST

Owner는 “이번 최소 보정과 Codex C qualification 결과를 수락해. Work의 남은 완료 기준을 확인하고 모두 충족됐다면 Done 처리해. 필요한 증거는 보존하고 commit·push는 별도로 남겨 둬.”라고 지시했다. 이에 따라 최소 scope-refusal 보정과 Codex C qualification PASS 결과를 수락 완료로 기록한다. 앞선 실행 closeout의 acceptance pending은 당시 상태로 보존하며 이 후속 기록이 현재 수락 상태를 소유한다. 결과 수락과 조건부 Work Done 지시는 H10 내용 판단이나 미관측 근거의 면제로 확대하지 않는다.

판정: Work Active 유지. [승인 계획의 완료 기준](u2-tool-neutral-execution-plan.md#completion-rollback-and-next-decision) 중 H10 품질·부담과 그에 대한 최종 수락이 남아 있으므로 조건부 Done 전제가 충족되지 않았다. actual_end를 기입하지 않으며 별도 실행이나 리뷰를 추가하지 않는다.

| 완료 기준 | 처분 및 근거 |
| --- | --- |
| Core/U1 수락·30파일 동일성 | 기존 accepted 근거를 재사용한다. 최근 Codex C postcheck의 Core 불변·입력 동일성 근거를 유지하며 새 Core 변경이나 authority action은 없다. |
| 두 adapter의 필수 보장과 최소 실제 관측 | Claude C의 기존 revision PASS와 Codex C 최신 PASS를 각각 사용한다. Codex는 같은 epoch/proxy의 fresh native2개·read2·file-scope refusal2·종료2를 관측했다. Claude를 최신 Host revision으로 재실행했다고 주장하지 않는다. 변경된 공통 Host 경계는 focused12/12로 확인했다. |
| 영향받은 H01–H09 처분 | 기존 D의 항목별 disposition과 R1 보정 결과를 재사용하고 Codex 실제 read/refusal/stop/resume 및 관측 send/control 근거를 보완한다. H05 합성 복구, H06 합성 보정 사례, H09 문서 근거를 새 실제 사용자·운영 관측으로 바꾸지 않는다. |
| R1 finding 처분 | 원 R1 BLOCKED와 Driver 처분표를 보존한다. 승인된 계약/peer/spawn/이탈·preflight 보정과 Python10/Rust6, 이후 policy 보정 및 최신 focused12/native C 결과가 후속 근거다. P2-9는 실제 Claude auth 증거, P2-10은 runner 결속의 기존 제한으로 남긴다. 새 Reviewer PASS나 두 번째 R1을 주장하지 않는다. |
| H10 5문서 품질·부담 | 미완료. Driver의 기존 파일별 대조는 완료됐으나 Q1 결과 안내 처분과 Owner의 실제 유용성·확인 부담 판단이 남았다. 과거 대기/runner 시간을 Owner 활동 시간이나 생산성 개선으로 환산하지 않는다. |
| Owner 최종 수락 | 이번 최소 보정과 Codex C 결과는 수락 완료. 전체 Work는 위 H10 판단이 남아 조건부 Done을 적용하지 않았다. |

H10의 구체적인 잔여 판단은 기존 five-document-quality.md의 Q1·Needs Human Input에 있다. Narrative는 작성 당시의 미확인 상태를 정확히 기록했지만 이후 DOC 검사 PASS·exact technical acceptance·commit·Core completed로 이어지는 안내가 부족하다. 짧은 후속 안내를 보완할지와 첫 운영 가이드로 수락 가능한지를 Owner가 판단해야 한다. Q2의 작성 절차 표현 간소화는 선택적 개선이며 자동 필수 수정으로 추가하지 않는다. 기존 5문서는 다시 생성하거나 수정하지 않았다. Owner 능동 확인 시간은 직접 제공된 측정값이 없어 unknown을 유지한다.

증거 확인: 최신 closeout이 가리키는 native result/verification/cleanup/source delta/focused result/candidate 및 재사용 결과의 SHA가 모두 기록과 일치했다. H10 봉인본5개와 보존 worker5개도 기존 품질 평가의 SHA와 일치한다. 이번에는 파일 읽기·hash 대조·수락/완료 기준 기록만 했으며 test/build/native/model/reviewer/authority action은 모두0이다. 새로운 실행 예산이나 재시도 권한을 만들지 않는다.

보존: 기존 durable task의 승인·실패·수정 전 bytes·고정 입력·원시 결과·검증·종료·정리 기록을 그대로 유지한다. source/native worktree와 필요한 후보는 미커밋 변경의 복구·후속 통합에, H10 봉인본과 worker는 Owner 품질 판단에 사용된다. 해당 판단 및 별도 Git 통합 처분 뒤 소비 종료를 확인해 정리를 재평가한다. 이번에 삭제한 파일과 변경한 활성 경로는0이며 마지막 복구 사본을 삭제하지 않았다. commit/push/배포는 수행하지 않았다.

후속 수락 및 hash 대조 기록: private-evidence/E145 상세 품질 판단 자료: private-evidence/E150 전체 완료 전이므로 Work index의 Done 이동이나 다른 저장소 STATUS 변경은 하지 않는다. 자동 재개 금지를 유지한다. [공개용 중립화]


## Q1 Result Navigation Supplement — 2026-10-27 KST

Owner의 요청으로 기존 Narrative 본문을 그대로 유지하고 Verification And Result Boundary 앞에 짧은 후속 안내를 추가했다. 원 업무 result-1의 DOC-LINKS/DOC-GFM/DOC-CLAIMS PASS와 결과 후보 reference-a-result-revision의 exact 기술 수락 기록을 프로젝트 내부 상대 링크로 연결했다. 이는 원 업무의 기록이며 별도 고정 스냅샷 회귀 reference-a-regression-result-revision의 결과와 합치지 않는다. 당시 검증·수락은 봉인본에 귀속하고 이번 안내 추가 및 H10의 내용 유용성·확인 부담 판단은 포함하지 않는다고 명시했다. [공개용 중립화]

수정 위치는 primary Reference A 프로젝트의 docs/briefs/reference-a-operations-guide.md 한 곳이다. 기존 develop의 dirty 파일을 모두 보존한 채 reference-a-guide-branch branch를 생성했다. 새로운 worktree는 만들지 않았고 기존 봉인본·worker·typed intent/Work/decision을 수정하지 않았다. Narrative의 기존 bytes는 안내를 제거하면 봉인본과 완전히 같고 나머지 dirty 파일과 authority JSON은 불변임을 확인했다. 현재 Narrative는 기술 수락 뒤의 미커밋 변경이며 기존 수락된 bytes와 구분한다. [공개용 중립화]

새 안내의 두 링크와 대상의 검사/수락 주장을 대조했고, 전체 Narrative를 marked GFM으로 렌더해 code/pre 밖 literal 강조 구분자 없음, 기존 본문 보존과 whitespace 검사를 통과했다. 최초 로컬 검사문이 decision의 action 위치를 잘못 읽어 KeyError로 멈췄고, 원본 구조 confirmation.action에 맞춰 검사문만 바로잡아 검증했다. runtime/full suite/model/reviewer 및 새 typed 수락은0이다. Q1 안내 보완은 완료했으며 Q2 선택적 간소화는 수행하지 않았다. H10 핵심 내용·남은 한계·관측된 확인 횟수를 Owner에게 요약하며 유용성/부담 판단과 전체 Work Done은 미완료로 둔다. commit/push는 별도다.

검증과 복구 근거는 기존 d-quality-r1/q1-addendum-verification.json 및 q1-addendum-render.html에 보존했다. 원 Narrative는 기존 봉인본이 복구 사본이며 새 중복 원문 사본은 만들지 않았다. 보완문과 branch는 Owner 판단 및 후속 Git 통합의 입력이므로 유지하고 그 처분 뒤 정리를 재평가한다. 파일 삭제·활성 경로 이동0이다.


## Final Owner Acceptance And Work Done — 2026-10-27 KST

Owner는 “Q1 보완과 H10 5문서를 첫 운영 가이드 범위로 수락해. 확인 부담도 이번 검증에서는 수용하되 시간 절감은 미측정으로 남겨 둬. 남은 완료 기준이 모두 충족됐다면 Work를 Done 처리하고, 증거는 보존해. commit·push는 계속 별도로 남겨 둬.”라고 지시했다. 이전 최소 보정·Codex C 수락에 이어 마지막 잔여였던 Q1 보완과 H10 품질·부담 판단이 완료됐다. 아래 승인 범위의 완료 기준을 모두 확인해 FEAT-20261022-001을 Done 처리한다. 실제 종료일은 2026-10-27이다.

### Completion Criteria

- [x] Core/U1 수락·30파일 동일성 유지: 기존 accepted 근거와 Core30 preflight/최근 Core 불변 검증을 재사용한다. 종료 시 최신 고정 Python 입력75개와 기타 입력18개를 SHA로 재대조했고 Core source/authority를 바꾸지 않았다.
- [x] 두 adapter의 필수 보장과 최소 실제 관측: Claude C 이전 revision의 실제 PASS와 Codex C 최신 같은 epoch/proxy의 fresh native2개·정상 read2·file-scope refusal2·종료2를 사용한다. 공통 Host 거절 순서 보정은 focused12/12로 검증했다. Claude를 새 revision에서 재실행한 것은 아니다.
- [x] 영향받은 H01–H09 처분: 기존 항목별 disposition과 후속 Codex 실제 read/refusal/stop/resume 근거를 유지한다. H05/H06의 합성·역사 근거, H09 문서 사례와 독립 사용자 효율 미관측을 구분한다. 이 한계들을 새 실제 관측으로 바꾸지 않는다.
- [x] R1 finding 처분: 원 Reviewer BLOCKED, Driver 처분, 승인된 복구의 Python10/Rust6와 이후 policy/Host 보정·실제 C 결과를 연결한다. P2-9의 실제 Claude auth 근거와 P2-10의 고정 runner 결속 한계 처분을 유지한다. Reviewer 원문을 PASS로 고치거나 새 R1을 주장하지 않는다.
- [x] H10 품질·부담: Owner가 5문서를 첫 운영 가이드로 수락했다. Q1의 기존 본문 보존 및 후속 검사/기술 수락 링크 보완도 수락했다. 계획된 확인2회와 준비 결함에 따른 추가 승인3회의 부담은 이번 검증에서 수용한다. Owner 실제 활동 시간과 시간 절감은 미측정이며 생산성 개선 수치를 만들지 않는다.
- [x] 최종 Owner 수락·보존: 위 범위 수락과 조건부 Done 승인이 충족됐다. 승인 원문·고정 입력·실패 및 보정 이력·원시 실행·검사·리뷰·복구 근거를 보존했다. 종료 시 결과 연결18건, 입력93개, H10 봉인/worker 사본10개 및 Q1 변경 bytes를 재확인했다.

### Accepted Scope And Remaining Limits

완료는 승인된 source/adapter qualification과 첫 운영 가이드 범위에 한정한다. H10의 기술 수락, 이번 내용 품질 수락, source Work Done과 Git publication은 별개다. Spring의 기존 typed Work/decision은 그대로이며 Q1은 역사적 봉인본 수락 뒤의 문서 보완으로 이번에 사람이 수락한 미커밋 bytes다. 새 Core 제출/수락/위임 권한 소비를 실행하지 않았다.

Installed release·public support·Windows·production 적격성, 실제 환경별 배포·recovery/rollback, in-flight HTTP+async 전체 종료, workload capacity/SLO와 일반 사용자 효율은 미검증 또는 후속 범위다. Q2 표현 간소화는 선택적 개선이며 현재 완료 기준의 필수 수정이 아니다. 최소 OS 지원 경계와 별도 통합 리팩터링 방향은 기존 승인 계획을 유지한다. 이런 작업은 구체적 필요와 별도 범위 승인이 생겼을 때 검토하며 자동 재개하지 않는다. 시간 절감 미측정은 이번 수락으로 수치화하거나 성공으로 승격하지 않는다.

Adopter impact: 이번 결과만으로 적용할 새 배포 artifact가 정해지지 않았으므로 현재 adopter 업데이트는 필요하지 않다. 향후 설치 가능한 후보를 만들 때 exact release identity·적용 대상·rollback 경계와 해당 플랫폼 qualification을 별도로 확인해야 한다. source 완료가 자동 설치/업데이트 허가가 아니다. 현재 roadmap 방향·기존 backlog 요구는 바뀌지 않으며 새 STATUS/PLAN/후속 registry를 만들지 않는다. Development Index에는 이 closeout으로 가는 탐색 링크만 추가한다.

### Evidence, Accounting And Retention

이번 종료는 기록·hash·링크/형식 확인만 수행한다. test/build/native/model/reviewer/authority action0이며 이전 activation 소진과 실패는 환급하지 않는다. 기존 native 예약14/28/42/28/42/14/7과 focused18/18 소진 및 실제 사용 기록은 그대로 유지한다. 마지막 native closeout의 조정 범위 누적 활동38,145.135301초는 그 시점 값으로 보존하며 후속 문서 작업이나 Owner 활동 시간을 그 값에 소급 혼합하지 않는다. 과거 integrated ledger176,128.667634초, continuation의 당시32,261.136709초 예산, H10 회귀의 당시129.20분 경과는 서로 포함 관계가 다른 역사적 snapshot이며 합산하지 않는다. 미측정 시간 절감과 Owner 능동 시간은 unknown이다.

보존 경로와 소비 목적:

- 기존 durable task codex-u2-tool-plan-20261021: 승인/실패/고정 입력/원시 결과/검사/리뷰 및 마지막 복구 자료. 완료 결과 추적과 별도 Git 통합·검토의 입력이며 이 목적의 종료 또는 명시적 보존 처분 뒤 정리를 재평가한다.
- colvia-u2-plan-20261021 및 codex-u2-tool-plan-20261021 source worktree: 미커밋 source·문서와 재현 입력의 후속 Git 통합/복구를 위해 유지한다. 통합과 복구 가능성 확인 전 제거하지 않는다.
- H10 control/worker·봉인본: 원 업무와 고정 회귀의 수락 identity 및 결과를 재현하는 필수 증거다. 마지막 증거/복구 사본을 삭제하지 않는다.
- Reference A primary의 reference-a-guide-branch: 수락된 Q1 보완과 기존 미커밋 출력의 Git 통합 입력이다. 기존 경로를 유지하며 commit·push 승인까지 보존한다. [공개용 중립화]

이번에 삭제한 파일·worktree·branch와 이동한 활성 경로는0이다. 새 복사본이나 전체 source archive는 만들지 않았다. 기존 정리 기록과 보존 자료는 유지하며 commit/push/PR/merge/release/배포는 수행하지 않았다. 세부 종료 근거: 기존 tool-neutral-adjustment-20261026/owner-acceptance-closeout.json.
