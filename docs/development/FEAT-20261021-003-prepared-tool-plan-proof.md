# Prepared Tool Plan Initial Proof

## Public Snapshot Notice

이 문서는 비공개 원본에서 식별 정보만 중립화한 공개 파생물이다. 원본이 과거 승인·리뷰·실행 기록의 기준이며 별도로 보존돼 있다. `[공개용 중립화]` 표지가 있는 인용·본문과 그 표지가 붙은 code block은 원문 그대로가 아니다. 아래의 과거 `Verbatim` 표기도 이 제한을 따른다. 기존 SHA-256은 원본 bytes 기준이며 이 공개 사본의 digest나 새 승인으로 해석하지 않는다. 결과·실패·수락 범위·수치·미측정 한계는 원래 의미를 유지한다.

`Reference A`는 실제 외부 대상의 중립 표기다. 실행 데이터의 합성 ID는 `synthetic-reference-a` / `synthetic-operations-guide-check`, 회귀용은 `synthetic-reference-a-regression` / `synthetic-operations-guide-regression`이다. 표시용 branch `reference-a-guide-branch`, 문서 `docs/briefs/reference-a-operations-guide.md`, `private-evidence/E…` 및 `private-approval/O…` 표기는 공개된 실제 경로나 실행 승인이 아니다. private 원본과의 대응은 비공개로 보존한다. 기존 실제 대상 재실행은 원본에 대한 근거이며, 중립화한 소스의 새 native PASS가 아니다.

Status: Initial proof accepted by Owner; implementation, bounded verification, R1, and explicitly approved cleanup complete; no product publication.
Owner: human Owner. Driver: Codex. Reviewer: Claude via bounded authorized CLI calls.

## Outcome For Owner Review

승인된 A 초기 proof의 구현·검증·R1을 완료했고, 2026-10-22 07:43 KST Owner가 이 범위의 결과 수락과 제안한14개 중간 경로 정리를 함께 승인했다. 승인된14개 중간 경로 정리와 보존 확인도 완료했다.

```text
prepare → 입력·설정·tool envelope 보관 → handle 1회 소비
        → 매 요청의 최종 HTTP body 검사 → 같은 router의 clock handler 1회 실행
```

| 항목 | 현재 결과 |
| --- | --- |
| 구현 범위 | 고정 공개 source에 offline fixture와 prepared plan 계약 구현; 최소 tool은 clock.curr_time |
| 실행 검증 | core 집중5, registry4, protocol/기존 collision/설정 로딩 각1, schema4 PASS; Clippy·두 binary build PASS |
| 통합 검증 | 최종8 cases PASS; production HTTP body9개와 실제 clock dispatch4개 관측; 일반/Lite·거절·재시작 포함 |
| Stable Protocol | 공식 생성1066파일이 기준 HEAD와 byte-identical |
| 독립 정적 검토 | fresh Claude2회; 최초 필수3건 보정 후 잔여0. Reviewer 자체 실행 재현은 없음 |
| 결과 경계 | 합성 no-auth/비압축 HTTP fixture 적격. 실제 provider·인증 CLI·OS worker·기존 U2 통합 완료는 아님 |
| 실행물 | fixture binary SHA df5e7ab4b63fdfe8aa2b45eba8ad8fd7d956ebe228469d37a9fbe6d2d16973a6; ordinary binary 별도 보존 |
| Git / Authority | 제품 commit/push/PR/merge·기존 runtime 교체·Core/H05 승인·STATUS 변경 없음 |
| Cleanup | Owner 명시 승인 후14개 경로 삭제 완료(삭제 전 할당량51.33GiB); source·두 실행물·필수 evidence 보존, active path 변경0 |

known limits: sourceIdentity는 base commit이고 patched candidate는 binary SHA로 결속한다. 실패/interrupt 후 같은 thread 재사용은 제한된다. wire_profile 일부는 고정 선언이며 ordinary auth/header/compression 동등성, syscall 수준 network 무시도, release/non-macOS/full-workspace 검증은 수행하지 않았다. 선택적 보강은 이 초기 proof의 필수 조건으로 승격하지 않는다.

## Authorization And Scope

2026-10-21 22:58:56 KST Owner가 “A 실행 묶음 승인”으로 R0 보정 후 통합 실행안을 승인했다. private authorized-plan.md의 sha256은99c4dbb470f2aecfc9b2bfd07c43959261433dddfb188944cf5b4a6a3ace2b97이다. 별도 고정 checkout·task-local Rust 도구체인·최소 runtime 구현·격리 offline 검사·보정2묶음·R1최대2회를 포함한다. 예상6–10시간/별도 누적600분, bootstrap90분 조기 판별과 마지막15분 종료 여유를 적용한다. 종전 U2 사용량을 초기화하거나 이 새600분에 숨기지 않는다.

기존 [FEAT-20261021-002](FEAT-20261021-002-u2-single-host-source.md)는 중단 상태이며 이 proof의 결과에 의존한다. 새 runtime prepared handle은 기존 Core authority grant/ticket을 대체하지 않는다. 실제 provider/model, 실제 adopter, 원 CLI 교체, Core/managed runtime, 제품 commit/push/PR/merge, H05 복구, 결과 수락은 제외한다.

## Minimum Contract And Completion Criteria

- strict default-deny method admission, process 시작부터 consume 전 부작용0.
- complete post-policy registry/tool envelope와 collision/unsupported 종류의 fail-closed.
- initial turn snapshot과 process-local1회 handle; foreign/drift/reuse/concurrent/restart 거절.
- 매 production sampling request에서 승인 envelope와 handler binding 대조; 같은 검증 router의 dispatch.
- 일반 tools와 Lite AdditionalTools를 포함한 실제 serializer 결과의 독립 mock 관측.
- task-local fixture bootstrap, 새 build/test sandbox canary, 네트워크 없는 검증.
- 관련 focused/regression/schema 검사, R1 disposition, 실행/미검증 구분, Owner 결과 수락.

## Evidence Selection And Limits

누적 변경은 외부 runtime의 사전 준비·turn/tool 결속과 fixture 검증 경계다. 기존 Core source/managed bytes는 바꾸지 않는다. 이전 Python/Git/host canary 및 suite는 새 Rust 경계의 PASS로 재사용하지 않는다. 고정 공개 source와 기존 R0는 설계 근거이며 새 실행 증거가 아니다. 첫 build 전 새 sandbox canary, 변경 경로의 focused/unit/protocol 통합, 일반 mode 영향 검사와 schema 최신성을 수행한다. 무관한 workspace/기존 제품 full을 이 proof의 이름으로 반복하지 않는다. 실제 case/command/timeout은 첫 실행 전에 고정하며 App Server 자식은 모두 카운트한다.

App Server36 starts/fixture threads72/simulated turns72, real provider0, 보정2묶음/R1최대2회다. baseline과 영향 보정에만 배정하며 같은 원인의 무근거 재실행은 하지 않는다. 범위/안전/권한/한도에 닿으면 중단하고 남은 요청을 묶는다. 통상 단계마다 재승인을 요구하지 않는다.

## Initial State And Preservation

현재/retained source 개발 ID를 확인해 당일003을 배정했다. 기존 기록과 다른 변경은 보존한다. 새 task root의 승인 입력·controller·진행 결과를 실행 전에 저장하고 named consumer가 필요한 증거를 checkpoint마다 보존한다. 고유 patch/결과/마지막 recovery를 유지하며 불필요한 중복과 build 자료는 standing cleanup 조건에 따라 정리한다. Git publication/결과 수락은 아직 없다.

## A0 Stop And Proposed Recovery — 2026-10-21

고정 공개 checkout과 task-local Rust1.95.0 설치는 완료했다. runtime setup canary6개(outside read/write, symlink, network, child read, allowed read/write)는 통과했다. 이것은 Rust build/worker 적격이나 prepared runtime의 검증이 아니다. Git fetch transport와 loader/TLS/CLT setup 보정은 private stage별 logs에 보존했다. cargo-fetch-cli2는 Cargo의 기본 재시도3회가 같은 CLT shim 실패를 반복했고, 이를 확인한 뒤 자동 재시도를0으로 고정했다. 성공으로 합치거나 숨기지 않는다.

마지막 cargo fetch --locked는 원본 Cargo.toml의 workspace0.163.0과 원본 Cargo.lock의 local160개0.0.0 불일치로 lock 갱신이 필요한 상태에서 거절됐다. 두 파일과 rust-toolchain.toml은 HEAD와 byte-identical이고 checkout은 clean이다. 승인안의 Cargo.lock 변경 제외 경계에 따라 영향을 받는 실행을 중단했다. dependency crate archive 다운로드0개, 최소 build/소스 구현/통합 검증/R1은 미수행이다. App Server starts/fixture threads/simulated turns/real provider/R1 모두0이다.

private task root의 lock-exception-proposal.md와 lock-metadata-only.proposed.patch에 local160개 버전만 맞추는 미적용 예외안을 고정했다. TOML 구조 비교로 외부 package와 dependency 목록 불변을 확인했지만 Cargo 통과는 아직 미검증이다. Owner가 해당 예외를 승인하면 같은 source와 기존 묶음의 남은 한도로 재개한다. 자동 lock 재생성이나 dependency 변경을 제안 범위에 넣지 않는다.

중단 기록 시 누적15.43분/600분, A0 잔여74.57분이다. 이후 종료 기록 소요는 final accounting에 더하며 Owner 대기는 제외한다. 상세 산술과 소비 counter는 private budget.json을 따른다.

보존: 고정 checkout은 실패 원본/재개 source, task-local toolchain과 fetch cache는 구체 재개 입력, controller·승인안·raw logs·제안 diff는 Owner 검토/복구 자료다. Owner의 재개 결정과 proof 종료/중단 시 소비 목적을 다시 평가하며 필수 증거는 결과 수락 전 유지한다. 삭제: 설치와 hash 검증이 끝나고 사용 중인 process가 없는 rustup-init binary1개. checksum과 설치 로그는 유지했다. active path 변경은 없다. 모든 기록된 child process group이 종료됨을 재확인했다. STATUS 변경, 결과 수락, 제품 commit/push는 없다.

종료 검증: 제안 patch의 git apply --check 통과, 원본 checkout clean, 기록/제안 whitespace 확인 통과. 최종 누적16.03분, A0 잔여73.97분, 전체 잔여583.97분이며 이 시점부터 Owner 대기를 제외한다.

## Lock Exception Authorized And Resumed — 2026-10-21

Owner가 제안한 local package160개 version 보정과 기존 A 묶음 재개를 “승인”했다. 고정 원본과 제안 patch identity를 확인한 뒤 해당 Cargo.lock 변경만 적용했고 git diff --check를 통과했다. 외부 package1314개 및 dependency 목록은 그대로다. Cargo/build 통과는 아직 주장하지 않는다. Owner 대기를 제외하고 기존 누적16.03분과 A0/전체 잔여 한도를 유지하며, 자세한 시각/새 deadline은 private budget.json과 lock-exception-authorization.json에 기록했다.

## A0 Passed And A1 Entry — 2026-10-21

승인된 lock 메타데이터160개 보정 후 cargo fetch --locked가12.16초에 통과했고 추가 lock 변경은 없었다. offline Cargo 시작에 필요한 공개 시스템 openssl.cnf 한 파일을 허용한 뒤 canary6개를 재통과했다. Cargo fingerprint의 Git ignore 탐색은 process-local XDG_CONFIG_HOME을 빈 task fixture로 고정해 사용자 설정 접근을 추가하지 않았다. HOME/CODEX_HOME은 그대로이며 build network 차단을 유지했다. 마지막 명령 cargo build --frozen -p codex-app-server --bin codex-app-server -j2는407.97초에 통과했다.

실제 normal/build graph907개에서 custom build entry와 native/download 경로를 점검했다. V8는 선택 graph에 없고 protoc는 locked vendored crate를 사용했다. 별도 artifact/native package 설치는 없었다. 이 source/lock/toolchain/profile과 binary identity는 private A0-result.json에 고정했다. A0 누적29.30분으로90분 안에 최소 build 가능성을 확인했다. runtime/App Server는 아직 실행하지 않았다.

다음은 기존 승인안의 A1이다. fixture bootstrap에서 사용자 설정을 읽기 전에 명시 root와 strict process mode를 고정하고, MessageProcessor admission과 Session startup/sampling guard를 결속한다. 실제 post-policy ToolRegistry/ToolRouter에 handler 구현 tag와 선택 입력을 묶고, prepare snapshot/1회 handle을 소비한 turn의 매 step에서 대조한다. production client serializer의 일반/Lite 결과를 메모리 mock에 전달해 독립 observer가 확인한다. 통상 단계 승인 없이 진행하며 새로운 crate/dependency 또는 승인 범위 밖 파일이 필요하면 중단한다.

cold build6분47초 실측은 bootstrap 불확실성을 줄였지만 runtime 결속/negative 검증의 난도는 남는다. 기존 전체6–10시간 예상과600분 상한을 유지한다. focused 검사 중 반복 가능한 결함이 드러나면 승인된 보정2묶음 안에서 영향 검사를 합치며 무관한 full suite는 실행하지 않는다.

## A1 Initial Implementation Checkpoint — 2026-10-22

실제 protocol에 experimental turn/prepare와 turn/startPrepared를 추가했고, fixture 전용 process bootstrap·method admission·Session/step guard·실제 registry handler binding·일반/Lite serializer 뒤 메모리 transport를 연결했다. 고정 source와 local-version-only lock 예외 외 dependency 변경은 없다. 일반 app-server와 fixture binary의 초기 구현 build가88.804초에 통과했다. 이는 runtime 동작 합격이 아니다.

manifest missing/null/unknown 거절과 handle Debug 비노출 protocol 단위 검사1개는 통과했다. core 집중 검사는 test helper의 Arc<ToolSpec> 변환 compile 오류를 확인해 고쳤고 다시 검사 중이다. 초기 구현이 아직 검증 후보로 동결되지 않았으므로 첫 통합 baseline이나 보정 묶음 소비로 계산하지 않으며 해당 실패 로그를 보존한다.

첫 App Server 시작 전에 private case-catalog.md에8 starts/최대6 threads/최대5 simulated turns의 baseline을 고정했다. 정상/일반·Lite/미등록 dispatch/재시작/시작 MCP·hook marker/unsupported를 포함한다. 같은 schema의 handler 교체와 policy/collision은 실제 registry를 쓰는 순수 집중 검사로 구분한다. 일반 mode 관측은 normal binary build·기존 protocol/registry 회귀·fixture state 미초기화 검사 범위이며 사용자 인증 CLI 실행으로 확대하지 않는다. 아직 App Server starts/threads/simulated/real provider/R1 모두0이다.

검사 중 필요한 source·task-local 도구체인·cache·실행물·원본 결과는 같은 durable 경로에서 유지한다. 현재 cache는 바로 이어질 focused/schema/integration build가 소비한다. 이 checkpoint의 삭제와 active path 변경은 없고 결과 수락·제품 Git 작업도 없다. 전체6–10시간 예상과600분 상한은 유지하며 최신 사용량은 private budget.json과 A1-initial-checkpoint.json에 기록했다.

## A1 Focused Checks And Initial Candidate Preparation — 2026-10-22

현재 core 집중 검사7개(ordinary fixture guard1, 두 encoding의 serialized-envelope 변조1, unsupported inventory11종 및 malformed bootstrap1, actual registry binding/schema/exposure/collision/policy4)가 통과했다. 각 test 내부 assertion 수와 test 개수는 구분한다. 앞서 통과한 protocol malformed manifest/handle Debug 검사1개와 기존 namespace collision 회귀1개도 재사용한다.

upstream generator로 experimental bundle을 갱신한 뒤 stable schema 최신성 검사에서 새 manifest helper의 누락이 드러났다. 같은 공식 generator로 stable 산출물 중 변경6개만 적용했고 JSON/TypeScript/두 precomputed 최신성4개가 통과했다. generator 전용 ignored test1개는 앞서 명시적으로 실행한 생성 명령에서 수행됐다.

Clippy 첫 실행은 aws-lc-sys C compiler process 시작의 Resource temporarily unavailable(os error35)로 중단했다. 격리/네트워크 권한은 유지하고 Cargo 병렬도를2에서1로 낮춰 해당 검사와 미실행 최종 build만 진행 중이다. 이 재개에서는 해당 C dependency compile 단계를 넘어갔으며 아직 전체 Clippy 합격을 주장하지 않는다. source의 AbsolutePathBuf import가 debug에만 선언되어 있던 조건은 fixture entry의 모든 build-mode 참조에 맞춰 제거했다. 실제 release build 검증을 수행했다는 의미는 아니다.

App Server 실행 전 observer는 실제 Session startup inventory의 hooks/extensions/MCP empty 기록도 대조하도록 정리했다. 현재 App Server starts/fixture threads/simulated turns/real provider/R1은 모두0이고, 최초 통합 후보 동결 전 초기 구현/검사 단계다. 아직 보정 묶음을 소비하지 않았다. 통과한 focused/schema 근거를 다시 full 실행하지 않으며 실패한 lint와 미실행 build 이후 고정8-case catalog를 실행한다.

## A2 Baseline Bootstrap Failure And Correction Bundle 1 — 2026-10-22

변경3 crate의 Clippy --tests는 기존 routing test helper의 optional refresh worker 타입을 맞춘 뒤 통과했다. 초기 code의 let-and-return 경고도 제거했고, 변경하지 않은 upstream core test2곳의 unused import 경고만 남았다. 일반 app-server와 fixture binary build가 함께 통과한 후보를 private integration-ready.json에 고정했다.

첫 baseline은 normal_matrix process1개를 시작했으나 initialize 응답 전에 `packaged defaults config file .../config/packaged.toml not found`로 종료됐다. 임의 재시도 없이 나머지7 case를 미실행으로 남겼고 exit1·graceful process-group 종료를 기록했다. 성공한 thread/turn, wire/dispatch, real provider는 모두0이다. 실패 후보·명령·stderr와 catalog/binary identity는 private baseline 기록에 보존한다.

첫 보정 묶음을 이 시점에 사용으로 기록했다. 원인은 `packaged_defaults_path=Some`이 파일 존재를 요구하는데 fixture config 디렉터리는 비어 있어야 하는 구현 간 불일치였다. 고정 production loader를 확인한 뒤 None이 실행물에 embedded된 defaults.toml을 선택함을 근거로 수정했다. 다른 명시 경로·host config 무시·격리 권한은 유지한다. 동일 옵션을 helper로 추출하고 실제 ConfigManager.load_startup_config만 수행하는 집중 테스트1개를 추가했다. App Server/worker/model을 시작하는 테스트가 아니다.

이 집중 검사에서 합성 model catalog에 `base_instructions` 또는 `model_messages.instructions_template`이 필수라는 역직렬화 실패도 재현했다. 같은 보정 묶음에서 새 fixture와 test에 synthetic instruction template을 추가했고 기존 실패 fixture는 수정하지 않았다. 재실행한 설정 로딩 test1개가 통과했다. 이후 app-server Clippy --tests와 두 binary build를 진행 중이며 아직 correction 통합 PASS를 주장하지 않는다. 기존 core/protocol/schema 근거는 영향을 받지 않아 재사용한다.

현재 누적 App Server starts1, fixture threads0, simulated turns0, real provider0, correction bundles1/2, R1 calls0/2다. 추가 통합 검증은 fixed catalog의 전부 미검증 상태인8 cases이며 해당 보정 묶음의 최대12 starts와 전체36 starts 한도 안에서만 수행한다. raw failure와 현재 source/실행물·build cache는 원인 검토, 바로 이어질 보정 build/검증과 R1의 입력이다. 이 checkpoint에서 삭제와 active path 변경은 없고 결과 수락·제품 Git 작업도 없다.

## A2 Correction Bundle 1 Passed — 2026-10-22

첫 보정 묶음의 후속 실행에서 fixture worker stack overflow를 재현했다. 원 pinned arg0의16MiB main/worker stack budget을 fixture entry에 맞추되 host dotenv/helper dispatch가 있는 arg0는 호출하지 않았다. 다음 실행은 normal/Lite wire·dispatch를 통과했지만 empty extension registry가 legacy host skill discovery를 요구해 sandbox에 막힌 사용자 skill 탐색이 있었고, 미등록 tool Fatal이 debug panic으로 변해 failed-turn notification이 없었다. 그 후보의 격리 합격은 주장하지 않는다.

같은 보정 묶음에서 prepared startup과 per-turn host skill 경로를 명시적으로 건너뛰고 prepared-only Fatal을 정상 실패 경로로 전달했다. 집중 core3·변경3 crate Clippy --tests·두 binary build가200.703초에 통과했다. startup 변경으로 기존 runtime 증거가 영향을 받으므로 남은8 starts를 모든 고정 case에 사용했다. correction1-03의8개가119.217초에 전부 통과했다. normal/Lite 실제 serializer, 실제 clock dispatch/history, 미등록 handler 실행0과 failed turn, foreign/drift/reuse/concurrent consume, restart stale handle, MCP/hook/config와 unsupported startup 거절을 확인했다. 최신 stderr에는 host skill scan 오류가 없고 모든 process group은 강제 종료 없이 사라졌다.

이 후보의 총9 wire requests와4 actual clock dispatch는 모두 합성 메모리 transport 관측이다. 실제 provider0이고 ordinary authenticated CLI/OS worker/live 제품 적격은 미검증이다. ordinary 영향 검사는 normal build·fixture guard·기존 집중 회귀 범위다. 누적 App Server13 starts, fixture thread11개(실패 예약 포함), simulated turns9, 보정1/2, R1 0/2다. 첫 보정 묶음12 starts는 소진됐으며 두 번째는 R1 동일 범위 필수 수정에만 남긴다.

R1에는 공개 source diff·diff 밖 새 source3개·일반화한 계약·합성 실행 결과·private 경로를 치환한 observer/profile만 전달한다. 원본 공개 source revision, 전체 변경 파일 SHA, binary와 입력 digest를 고정했다. 실제 사용자/프로젝트 식별자·자료·credential·과거 private packet은 전송하지 않는다. 후보를 바꾸지 않은 상태에서 fresh CLI/무도구 R1을 최대15분 실행하며 auth/billing 경로는 호출 직전 별도 확인한다.

실측 누적 약2시간이다. cold build와 runtime 통합이 초기 예상보다 빨리 끝났으므로 R1·필수 보정·최종 정리에 남은 예상60–150분(판단값, 리뷰 결함 정도에 따라 변동), 전체 약3–4.5시간으로 재예측한다.600분 중단 상한과 마지막15분 종료 여유는 유지하며 대기·겹침은 기존 산식을 따른다. 현재 source/실행물/cache는 곧 진행할 R1과 승인된 필수 보정의 입력이므로 유지한다. 이 단계 삭제와 active path 변경은 없고 결과 수락·제품 Git·STATUS 변경도 없다.

## R1 First Review — 2026-10-22

Fresh Claude CLI의 실제 model은claude-opus-5-5, session은c67458a0-4879-49bd-9516-b6d745f68fcc이다. 호출 직전 claude.ai/firstParty/pro를 확인했고 tools/MCP0, tool use0,233.841초, exit0, process group 종료, source input drift0이다. 공개 source diff와 새 파일3개, 합성 evidence152393 bytes를 전달했으며 request SHA는4ec3f53d6b78528791c07b6e5f49a32108c2a2f171d05fc1daabf57d365b1c49이다. Reviewer는 정적 검토만 수행했다. 원 응답은 아래에 그대로 보존한다.

### Verbatim Reviewer Response

````text
# Prepared Tool Plan R1 정적 검토 결과

## 0. 검토 근거와 구분

- **정적 추론**: 이 문서의 결론은 모두 제공된 diff, 새 파일 3개, controller와 sandbox profile 텍스트만 읽고 내린 것입니다. 도구, 명령, 빌드, 실행은 사용하지 않았습니다.
- **Driver 실행**: canary, cargo/clippy, unit test, `correction1-03`의 8개 case 통과는 Driver가 관측한 결과입니다. Reviewer가 재현하지 않았으므로 근거 자료로만 인용합니다.
- **미검증**: 다음 항목은 diff 밖에 있어 볼 수 없었습니다.
  - Cargo.lock 반복 hunk
  - binary schema(zst) 내용
  - `codex_api` 내부 구현
  - upstream의 schema experimental 필터 구현
  - `turn_start_inner`, `capture_speculative_step_context` 본문

---

## 1. 필수 보정 Findings

### [P1] F1. mock 위치가 production transport/encoding 경로 앞이라 "최종 serializer bytes" 계약이 입증되지 않음

- **위치**
  - `core/src/client.rs`의 `ModelClientSession::stream` 맨 앞에 추가된 prepared 분기
  - 같은 파일의 `ModelClient::build_api_transport`가 prepared 모드에서 `Err`를 반환하는 부분
  - `core/src/session/prepared.rs`의 `mock_stream`
- **논리 경로**
  1. prepared 모드에서 `stream()`은 `build_responses_request(..., false)`를 호출합니다.
  2. 그 결과인 `ResponsesApiRequest` 구조체를 `serde_json::to_vec`로 직접 직렬화해 기록하고 즉시 반환합니다.
  3. 따라서 `WireApi::Responses` 분기, `stream_responses_api`, `codex_api`의 request body 구성, `HttpTransport` 경계를 전혀 거치지 않습니다.
  4. `build_api_transport`는 메모리 transport를 돌려주지 않고 에러로 막혀 있습니다. 즉 "메모리 mock transport"가 존재하지 않습니다.
  5. 응답도 `ResponseEvent`를 직접 주입하므로 production SSE parser를 거치지 않습니다.
- **계약 위반 가능성**
  - 계약은 "최종 production serializer의 normal tools / Lite AdditionalTools를 대조하고, 메모리 mock transport가 직렬화된 bytes를 기록"하는 것입니다.
  - 현재 후보가 기록하는 것은 transport 이전 단계 구조체의 serde 결과입니다.
  - 다음 중 하나라도 있으면 proof가 이를 검출하지 못합니다.
    - production HTTP 경로가 `build_responses_request`에 넘기는 마지막 bool 인자가 `false`가 아닌 경우
    - `codex_api` 계층이 body를 변형하는 경우(item id 부착, provider별 보정, 압축 등)
  - 코드 주석의 "after the real production serializer"는 정적으로 뒷받침되지 않습니다.
  - 실제 bytes 차이가 있는지는 `codex_api`가 diff 밖에 있어 **확인 불가**입니다. 다만 계약이 명시적으로 요구하는 증거 형태가 없는 것은 정적으로 확정됩니다.
- **최소 보정**
  - prepared 모드에서 `build_api_transport`(또는 `codex_api` transport trait 주입점)가 in-memory transport를 반환하도록 바꿉니다.
  - 이 transport는 다음을 수행합니다.
    - 실제 request body bytes를 기록합니다.
    - tools / AdditionalTools를 대조합니다.
    - 고정 SSE bytes를 반환해 production parser를 통과시킵니다.
  - `stream()`의 조기 반환은 제거합니다.
  - 위 보정이 범위상 불가능하다면, 최소한 production HTTP 경로와 같은 인자로 request를 만들고 같은 body encoder를 호출하도록 맞춰야 합니다. 이때 production encoder 결과와 mock 기록 bytes가 같다는 unit test가 필요합니다.
- **필요 검사**
  - normal과 Lite 각각에 대해 transport 경계에서 캡처한 bytes를 Python observer가 검증합니다.
  - 기존 8-case 재실행이 필요합니다. 두 번째 보정 묶음의 최대 12 starts 안에서 가능합니다.

### [P2] F2. router guard가 dispatch 1회와 선택 입력을 dispatch 시점에 강제하지 않음

- **위치**
  - `prepared.rs`의 `validate_dispatch`와 `record_dispatch`
  - `router.rs`의 dispatch 경로에 추가된 prepared 분기
- **반례 경로**
  1. `validate_dispatch`는 `requests == 1`, 같은 turn, envelope, tool 이름만 확인합니다. `dispatches == 0` 확인이나 예약은 하지 않습니다.
  2. `dispatches` 증가는 handler 실행이 끝난 뒤 별도 lock에서 `record_dispatch`가 수행합니다.
  3. 첫 sampling 응답에 `clock.curr_time` call이 두 개(병렬 포함) 있으면, 두 call 모두 검증을 통과하고 handler가 2회 실행됩니다.
  4. 두 번째 request의 `dispatches == 1` 검사는 사후 탐지일 뿐입니다.
  5. 현재 mock은 call을 하나만 만들기 때문에 이 경로는 실행되지 않습니다. 즉 상한이 core guard가 아니라 mock 구성에 의존합니다.
- **추가 문제(선택 입력)**
  - `ToolPayload`의 종류와 `arguments`를 승인된 schema(`{}`, `additionalProperties:false`)와 대조하지 않습니다.
  - 계약의 "선택 입력 대조"를 dispatch 지점에서 수행하지 않는 것입니다.
- **최소 보정**
  - `validate_dispatch` 안에서 같은 mutex 아래 `ensure!(active.dispatches == 0 && !reserved)`를 확인하고 즉시 예약 표시를 남깁니다.
  - payload가 `Function`이고 arguments가 빈 객체인지 확인합니다.
- **필요 검사**
  - 다음 unit test를 추가합니다.
    - 같은 step에서 두 번째 dispatch가 거절되는지
    - arguments에 `{"x":1}`이 들어오면 거절되는지
  - fixture case 추가는 선택입니다.

### [P2] F3. experimental 전용 타입이 stable schema와 TS export에 노출됨(ordinary 표면 회귀)

- **위치**
  - `app-server-protocol/src/protocol/v2/turn.rs`의 `PreparedToolPlanManifest`
  - 생성물 `ClientRequest.json`, `codex_app_server_protocol.schemas.json`, `codex_app_server_protocol.v2.schemas.json`
  - `typescript/v2/index.ts`
  - `precomputed/app-server-exports-stable.json.zst`(SHA 변경)
- **논리 경로**
  - `turn/prepare`와 `turn/startPrepared`는 `#[experimental]`로 선언되어 있습니다.
  - 그 결과 `TurnPrepareParams`, `TurnStartPreparedParams` 등 params/response 타입은 stable 산출물에 나타나지 않습니다.
  - 그러나 중첩 타입인 `PreparedToolPlanManifest`만 stable JSON schema 세 곳과 v2 TS index에 추가되었습니다. stable precomputed export도 바뀌었습니다.
  - 결과적으로 어떤 stable method도 참조하지 않는 고아 정의가 생겼습니다.
- **계약 관점**
  - fixture 전용 실험 기능이 ordinary 공개 프로토콜 표면을 바꿉니다.
  - freshness test는 "현재 generator 출력과 같다"는 것만 보장하므로 이 노출을 막지 못합니다.
- **최소 보정**
  - upstream의 experimental 타입 필터 메커니즘에 이 타입을 등록하거나 동등한 처리를 합니다. 메커니즘 자체는 diff 밖이라 **확인 불가**입니다.
  - stable 산출물에서 제거되도록 다시 생성합니다.
- **필요 검사**
  - schema freshness 4개 test와 explicit generator를 재실행합니다.
  - stable 산출물에 `PreparedToolPlanManifest`가 없는지 확인합니다.

---

## 2. 비필수 관찰 (필수 보정 아님)

- **고정 sourceIdentity**: `run_prepared_tool_plan_fixture`가 `sourceIdentity`에 base commit 상수를 넣습니다. 실제 binary는 patch가 적용된 source로 빌드되었으므로, 이 값은 후보 source를 식별하지 않습니다. 후보 결속은 `buildIdentity`(binary SHA)에 의존합니다. 명칭이나 의미 정리를 권장합니다.
- **interrupt 후 thread 고착**: `turn/interrupt`나 run_turn 실패 이후 `ActivePlan`이 `completed=false`로 남습니다. 이 경우 같은 thread에서는 새 consume이 "another consumed plan is active"로 영구 거절됩니다. fail-closed이며 자동 재소비도 없으므로 계약과 충돌하지 않습니다.
- **startPrepared의 direct input 검사 생략**: `turn_start_prepared`는 `ensure_direct_input_allowed`를 호출하지 않습니다. 다만 prepare 시점에 검사했고 입력 동일성을 강제하므로 영향은 낮습니다.
- **null 필드 처리 시점**: `snapshot`과 `toolEnvelope`가 `JsonValue`이므로 내부 `null`은 typed admission을 통과합니다. 이후 consume의 equality 검사에서 handle을 소비하며 거절됩니다. 계약상 거절은 이루어집니다.
- **환경 변수 검사 방식**: env 검사는 고정 denylist(5개)입니다. 그 밖의 경로 변경 env(예: state DB 위치 관련)는 controller의 env allowlist와 sandbox 쓰기 제한에 의존합니다.
- **startup 사전 검사 범위**: `verify_files`와 startup 부재 검사 대상이 제한적입니다. 예를 들어 `home/AGENTS.override.md`는 대상이 아닙니다. 이는 fixture root 내부 입력이고, snapshot의 `loaded_instructions`에 반영되는지는 **확인 불가**입니다.

## 3. 정적으로 계약 부합이 확인된 부분 (요약)

- **process 고정**: `OnceLock` 기반으로 process가 고정되며, ordinary entry에는 초기화 경로가 없습니다.
- **RPC 2중 allowlist**: raw method와 typed method 모두에 allowlist가 있습니다. `thread/start`는 `{"ephemeral":true}`만 허용합니다.
- **core 측 guard**:
  - `run_turn`은 `admit_turn`을 거쳐야 합니다.
  - `mock_stream`은 `Turn` kind만 허용합니다.
  - pending input과 내부 input은 거절됩니다.
  - compaction은 비활성입니다.
- **handle 처리**:
  - 256-bit `OsRng`를 사용합니다.
  - mutex 아래에서 remove-first로 처리합니다.
  - foreign, drift, 재사용 시에도 handle이 소비됩니다.
  - Debug 출력에서 handle이 redaction됩니다.
- **startup 제한**:
  - 확장 registry가 비어 있는지 검사합니다.
  - hooks, MCP, dynamic, hosted, code-mode, search를 거절합니다.
  - host skill discovery는 startup과 turn 단계에서 모두 명시적으로 skip합니다.
  - prewarm과 provider transport는 차단됩니다.
- **envelope 결속**: 실제 typed registration을 `Weak` + `ptr_eq` + `type_name`으로 묶습니다. step과 dispatch마다 envelope를 재대조하고, 같은 router의 registry로 dispatch합니다.

## 4. 확인 불가 및 Remaining Limitations

1. **network와 외부 HTTP**
   - network는 "시도 0"이 아니라 "sandbox에 의한 거부"로만 관측되었습니다. syscall 수준 감사가 없습니다.
   - `build_models_manager`, auth, telemetry, 그 밖의 비-transport HTTP client가 시도조차 하지 않는다는 점은 정적으로도 확인하지 못했습니다.
2. **MCP/hook marker case의 의미**
   - 두 case는 `home/config.toml` 존재에 대한 preflight 거절을 확인한 것입니다.
   - core의 hooks/MCP 런타임 guard 자체는 unit/정적 근거로만 뒷받침됩니다.
3. **ordinary 회귀 범위**
   - 인증된 ordinary session 전체 회귀, release build, non-macOS 빌드는 수행되지 않았습니다.
   - `macos_managed_config_requirements_base64` 필드는 cfg 처리가 없어 다른 OS에서 컴파일되는지 **확인 불가**입니다.
4. **diff 밖 본문**
   - `codex_api` body 구성, `turn_start_inner`, `capture_speculative_step_context`의 부수효과는 볼 수 없었습니다.
5. **lock 예외와 binary 산출물**
   - Cargo.lock version-only 예외와 zst 산출물 내용은 SHA로만 식별했고 내용은 검토하지 않았습니다.
6. **observer 독립성**
   - observer는 schema를 독립적으로 검증합니다.
   - 하지만 wire bytes 기록 자체는 후보 process가 작성합니다(F1과 연관).
7. **수락 범위**
   - Owner 수락, 실제 provider/CLI/OS worker 적격, production 적격은 이 검토의 판단 범위가 아닙니다.

---

## 결론

- **Mandatory findings 수: 3** (P1 1건: F1 / P2 2건: F2, F3)
- **Remaining limitations**: 4절 항목 1~7
- **Recommendation**: **현 후보는 R1 기준 미통과(필수 보정 필요)입니다.**
  - 두 번째 보정 묶음(최대 12 starts)에서 동일 범위 안의 보정으로 진행할 것을 권고합니다.
    - F1: transport 경계의 메모리 mock 도입, 또는 production encoder와 동등함을 입증하는 test
    - F2: dispatch 시점의 1회 예약과 arguments 검사
    - F3: stable schema 노출 제거
  - 보정 후 다음을 재실행한 뒤 R2(최대 2회 중 두 번째)에 제출할 것을 권고합니다.
    - 해당 unit test
    - schema freshness
    - 8-case batch
  - tool 지원 확대나 production 확장은 필수 보정에 포함하지 않습니다.
````

### Driver Disposition And Correction Plan

F1 accept: 현재 관측은 production request builder 이후 구조체 serde 단계였다. 최종 HTTP body preparation/transport 경계를 통과한 증거라는 주장을 철회한다. 승인 범위인 client.rs와 prepared internal module 안에 existing codex_api ResponsesClient/HttpTransport를 사용하는 실제 memory transport를 붙이고 production body preparation bytes와 SSE parser를 통과시킨다. synthetic no-auth/비압축 HTTP profile을 명시하며 실제 credential/provider 경로는 열지 않는다. 추가 crate/dependency 없이 기존 공개 API만 사용한다.

F2 accept: clock dispatch 전에 같은 mutex 아래1회 권한을 예약하고 Function payload의 빈 JSON object를 강제한다. 두 번째/동시 dispatch와 nonempty arguments 집중 검사를 추가한다. 선택 tool은 늘리지 않는다.

F3 accept: 기존 experimental dependency filter에 manifest helper를 등록하고 공식 generator로 stable/experimental 산출물을 재생성한다. stable 결과는 기준 source와 동일해야 하며 schema freshness를 다시 확인한다. generator owner 파일은 승인된 protocol/schema 소유 범위다.

Reviewer 비필수 관찰은 별도 한계로 유지한다. base source identity와 patched binary SHA의 역할을 구분하고 실패/interrupt 뒤 thread 재사용, 환경 allowlist 의존, marker preflight의 좁은 범위, 일반 인증 session/release/non-macOS 미검증을 결과에 남긴다. Owner 수락이나 새 범위 승격은 없다.

두 번째 보정 묶음을 시작한다. core 집중 검사·schema 생성/최신성·관련 Clippy·두 binary build 뒤 transport 경계가 바뀐 고정8-case를 한 번 실행한다. 추가 필요한 unit 검사는 App Server를 시작하지 않는다. 보정 묶음 최대12 starts와 R1 두 번째 호출 최대15분을 유지한다. 전체600분 안의 남은 예상60–150분은 유지한다.

## Correction Bundle 2 Verification — 2026-10-22

core prepared5개는169.552초에 통과했다. 그중 실제 production HTTP encoder/SSE parser 왕복과 dispatch 예약/invalid payload 검사를 새로 추가했다. schema generator 두 모드는30.530초에 통과했으며 stable 생성 파일1066개 전부가 기준 HEAD bytes와 같았다. stable helper 노출 관련 변경5개를 되돌리고 생성 TS orphan을 제거했다. experimental zst SHA는 기존과 같고, schema freshness4개도 통과했다.

Clippy는 동시성 테스트의 needless_collect를 지적해 한 번 실패했다. collect 제거로 실행을 직렬화하지 않고 eager array와 Barrier2로 바꿨다. 해당 test1개·변경3 crate Clippy --tests·두 binary build가299.634초에 통과했다. 나머지 focused/schema 결과는 영향이 없어 재사용했다. unchanged upstream 경고2개만 남았다.

후보 binary df5e7ab4b63fdfe8aa2b45eba8ad8fd7d956ebe228469d37a9fbe6d2d16973a6의 correction2 고정8-case가119.022초에 모두 통과했다. actual ResponsesClient/EncodedJsonBody/Request preparation/HttpTransport에서 body를 캡처하고 production SSE parser/core map을 거쳐 normal/Lite의9 wire requests와4 actual clock dispatch를 확인했다. 관측자는 capture boundary와 synthetic HTTP/no-auth/no-compression profile도 검사한다. 첫 보정의 구조체 serde 기록은 이 최종 transport 증거로 재사용하지 않았다.

누적 App Server21 starts, fixture threads17(예약 실패 포함), simulated turns14, runtime real provider0, 보정2/2, R1 1/2다. 두 번째 묶음8/12 starts를 사용했고 모두 강제 종료 없이 process group이 사라졌다. 남은 단계는 같은 후보의 마지막 정적 R1과 결과 정리다. code23파일(새2개)을 동결하고 해당 reviewer가 확인하지 못했던 공개 production encoder/transport/SSE context를 추가해 보낸다. 실제 사용자 자료/경로/credential은 제외한다.

## R1 Final Review — 2026-10-22

Fresh Claude CLI 실제 model은claude-opus-5-5, session은0e09f338-dffc-43e0-bd3a-ab322ab359ee이다. 호출 직전 구독 claude.ai/firstParty/pro를 재확인했다. tools/MCP0, tool use0,106.662초, exit0, process group 종료, input drift0이다. 입력204657 bytes의 request SHA는ed11042e8f53d48f393c78bcdc30f465f3051453f6c67f913ca4349f2e7b983b이다. 원 응답을 아래에 그대로 보존한다.

### Verbatim Reviewer Response

````text
# Prepared Tool Plan R1 두 번째 정적 검토 결과

## 0. 근거 구분

- **정적 추론**: 이 검토는 제공된 diff, 새 파일 2개, 공개 source 발췌(`codex-api` endpoint/session/SSE, `http-client` request/transport, `core/client.rs` 956–1118), controller 텍스트만 읽고 내린 판단입니다. 도구 사용, 빌드, 실행은 하지 않았습니다.
- **Driver 실행 관측**: 다음 결과는 Driver가 관측한 것이며, Reviewer가 재현하지 않았습니다.
  - core prepared 5 tests, schema freshness 4 tests, Clippy, build
  - stable 1066파일 byte-identical
  - correction2 통합 8 case 결과(9 captured requests, 4 dispatch, real provider 0)
- **확인 불가**: 다음은 제공 범위 밖이라 판단할 수 없습니다.
  - ordinary `ResponsesHttpExecutor` loop 본문(prepared 분기 이후)
  - `tool_metadata::bounded_input`, `map_response_stream`, `session_telemetry_for_request`
  - `run_with_request_telemetry`의 retry 의미
  - `AuthProvider::apply_auth` 기본 구현
  - export.rs의 experimental 필터 구현 본문
  - `capture_speculative_step_context`, `turn_start_inner`

---

## 1. F1–F3 판정

### F1 (P1) 최종 transport bytes 증명 — **resolved**

**근거 symbol과 경로 (정적)**

1. `ModelClientSession::stream`의 prepared 조기 반환이 diff에 더 이상 없습니다.
2. prepared 모드에서는 `responses_websocket_enabled()`가 `false`이므로 HTTP executor로 진행합니다.
3. `ResponsesHttpExecutor`의 prepared 분기는 다음 순서로 실행됩니다.
   - `build_responses_request(..., false)`
   - `prepare_response_items_for_request`
   - `bounded_input`
   - `prepared::stream_request`
4. `stream_request`는 기존 `codex_api::ResponsesClient::stream_request`를 호출합니다. 이후 production 경로는 다음과 같습니다.
   - `EncodedJsonBody::encode`(responses.rs:83)
   - `stream_encoded`
   - `EndpointSession::stream_encoded_json_with`
   - `Request::into_prepared`(session.rs:136)
   - `auth.apply_auth`
   - `FixtureTransport::stream`
5. `transport_body`가 호출하는 `prepare_body_for_send`는 `prepared == true` 분기(request.rs:189–193)로 들어가 저장된 최종 bytes를 그대로 반환합니다. 이는 `ReqwestTransport::send`(transport.rs:77)가 wire에 실을 bytes와 같은 경로입니다.
6. 따라서 이 fixture profile에서는 "transport 경계의 최종 body bytes" 주장이 정적으로 성립합니다.
7. 응답 쪽은 고정 SSE bytes가 `spawn_response_stream`(production parser)과 `map_response_stream`을 거칩니다.
8. tool 대조는 `mock_response` 안의 `verify_serialized_tools`가 최종 bytes를 파싱한 값에 대해 수행합니다. 그래서 `bounded_input`이나 정규화가 tools 또는 AdditionalTools를 바꾸면 검출됩니다.
9. `transport_body`는 다음을 강제합니다: POST, 고정 URL, `compression None`, `Authorization`/`Content-Encoding` 부재, `application/json`.

**실행 근거(Driver)**: integration에서 `capture_boundary == "http_transport_prepared_body"`와 `wire == request` 대조가 관측되었습니다.

**남는 점(비필수, §3 참조)**

- prepared 분기는 ordinary executor loop를 재사용하지 않는 병렬 분기입니다.
- 계약이 auth, header, contributor 비활성과 일반 인증 CLI 비동등성을 명시하고 있으므로 필수 결함으로 보지 않습니다.

### F2 (P2) dispatch 1회 예약과 선택 입력 대조 — **resolved**

**근거 symbol**

- `ToolRouter::dispatch_tool_call`(router.rs)이 handler 실행 전에 `prepared_envelope()`와 `validate_dispatch(..., &call.payload)`를 호출합니다. 이후 같은 `self.registry`로 dispatch합니다.
- `validate_dispatch`는 단일 plan-store mutex 아래에서 다음 순서로 확인합니다.
  1. `requests == 1`
  2. turn 일치
  3. envelope 일치
  4. 이름 일치
  5. `reserve_dispatch`
- `reserve_dispatch`는 다음을 확인합니다.
  - `!reserved`
  - `ToolPayload::Function`
  - arguments가 빈 JSON object
  - 위 조건을 모두 통과할 때만 `reserved = true`를 기록합니다.
- 실패, 취소, handler 오류가 나도 예약을 해제하는 경로가 없습니다.
  - 이 경우 `dispatches == 0`인 채로 follow-up 요청이 `mock_response`의 "follow-up request lacks approved dispatch"에서 거절됩니다. 즉 fail-closed입니다.
- `record_dispatch`는 `dispatch_reserved && dispatches == 0`을 요구합니다.

**정적 추론**

- 같은 step의 병렬 call 2개는 mutex 때문에 직렬화되고, 두 번째는 `already reserved`로 handler 실행 전에 거절됩니다.
- 이름이 불일치하면 예약 전에 거절되므로 예약을 소모하지 않습니다.
- `Function` 외 payload 변형은 모두 `bail`합니다.

**실행 근거(Driver)**

- pure unit `dispatch_reservation_rejects_duplicate_and_invalid_arguments`
  - `{"x":1}`, `null`, `[]`, `bad`, `Custom`, 순차 중복, barrier 동시 중복
- 통합 4 dispatch와 unregistered 0 dispatch

### F3 (P2) stable 표면 노출 — **resolved** (효과는 Driver 관측에 의존)

**근거 symbol**: `export.rs`의 `EXPERIMENTAL_CLIENT_METHOD_DEPENDENCY_TYPES`에 `"PreparedToolPlanManifest"`가 등록되었습니다.

**정적 확인 범위**

- 등록 자체는 확인됩니다.
- candidate `source_files_sha256`에 stable precomputed zst나 stable schema/TS 생성물이 포함되지 않습니다. 이는 "stable tracked diff 0"과 일관됩니다.

**실행 근거(Driver)**

- official generator 두 모드 실행
- stable 1066파일 base와 byte-identical
- stable TS orphan 제거
- freshness 4 PASS

**확인 불가**: 필터 구현이 이 목록을 어떻게 적용하는지는 본문이 제공되지 않아 정적으로 검증하지 못했습니다.

---

## 2. 보정으로 새로 생긴 같은 계약 결함

**필수 결함은 발견하지 못했습니다.** 점검한 항목은 다음과 같습니다.

- **FixtureTransport 거절 시 재시도**: `mock_response`는 모든 검사를 마친 뒤에만 기록하고 `requests`를 증가시킵니다. 그래서 transport 또는 core 계층이 거절된 시도를 재시도해도 상태 변경이나 side effect가 없고, 상한(`requests < 2`)도 유지됩니다. retry 의미 자체는 확인 불가이지만, 결과는 fail-closed입니다.
- **SSE 반환 후 parse 실패와 core 재시도**: `requests`가 1인 상태에서 재요청하면 `dispatches == 0` 검사로 거절됩니다. fail-closed입니다.
- **비-Turn sampling 경로**: compaction, background 등이 같은 executor로 오면 `mock_response`의 `CodexResponsesRequestKind::Turn` 검사에서 거절됩니다. 다른 endpoint 경로는 여전히 `build_api_transport`의 `Err`에서 막힙니다.
- **ordinary 영향**: 새 분기는 모두 `prepared::enabled()`로 가드되어 있고, ordinary entry는 `initialize_fixture`를 호출하지 않습니다.

---

## 3. 비필수 관찰 (필수 보정 아님)

1. **`wire_profile`은 선언 상수입니다.**
   - `config_snapshot`의 `wire_profile`은 실제 request에서 도출한 값이 아니라 하드코딩 JSON입니다.
   - `compression` / `authentication`은 `transport_body`에서 부분적으로 강제됩니다.
   - `include_internal: false`는 분기 인자 상수에만 의존하고, transport 경계에서 관측되지 않습니다(예: `client_metadata` 내부 키 부재 검사 없음).
   - "manifest에 결속"은 "고정 라벨 결속"으로 읽는 것이 정확합니다.
2. **ordinary executor와의 동등성**
   - prepared 분기는 builder, 정규화, bounded 단계를 재호출하는 별도 분기입니다.
   - ordinary loop의 `include_internal` 값, 호출 순서, header/compression/contributor/access_programs 처리와 동일한지는 확인 불가입니다.
   - 다만 계약 범위인 tools/AdditionalTools는 최종 bytes에서 검증됩니다.
3. **unit round-trip 대상**
   - `production_http_encoder_and_sse_parser_round_trip`은 `ResponsesClient::stream(Value)`를 사용하고, 타입이 있는 `stream_request(ResponsesApiRequest)`는 사용하지 않습니다.
   - `stream_request` 경로는 통합 관측(Driver)으로만 뒷받침됩니다.
4. **`ResponsesOptions::default()`**
   - session, thread, subagent header가 붙지 않습니다.
   - body에는 영향이 없지만, ordinary header 동등성은 주장 범위가 아닙니다.
5. **이전 R1의 비필수 관찰은 여전히 유효합니다.**
   - `sourceIdentity`는 base 상수이고, 후보 결속은 `buildIdentity`가 담당합니다.
   - interrupt나 실패 후 thread가 고착됩니다.
   - `startPrepared`에서 direct input 재검사를 하지 않습니다.
   - env denylist가 제한적입니다.
   - startup 부재 검사 대상이 제한적입니다.

---

## 4. Limitations

1. **network**: "시도 0"은 syscall 감사로 확인된 것이 아닙니다. sandbox 차단과 `build_api_transport`의 `Err`로만 뒷받침됩니다. `build_models_manager`, `AuthManager`, telemetry 등 비-transport client의 무시도 여부는 정적으로 확인하지 못했습니다.
2. **MCP/hook marker case**: config 존재에 대한 preflight 거절 범위입니다. host-wide runtime audit가 아닙니다.
3. **ordinary 회귀**: 다음은 수행되지 않았습니다.
   - authenticated ordinary session
   - release build
   - non-macOS build (`macos_managed_config_requirements_base64`가 cfg 없이 쓰임)
   - full workspace 테스트
4. **router 외 dispatch 경로**: `dispatch_any_with_state`를 router를 거치지 않고 직접 호출하는 경로가 있는지는 diff 밖이라 확인 불가입니다. code-mode, MCP, dynamic, search는 사전에 거절됩니다.
5. **lock과 생성물 내용**: Cargo.lock version-only 예외와 zst/schema 내용은 파일 identity로만 식별했습니다.
6. **기록 주체**: wire와 dispatch 기록은 후보 process가 작성합니다. observer는 그 기록을 독립적으로 재검증하는 구조입니다.
7. **판단 범위 밖**: Owner 수락, 실제 provider/인증 CLI/OS worker, 다른 제품 통합, production 적격은 이 검토의 판단 범위가 아닙니다.

---

## 결론

| 항목 | 판정 |
|---|---|
| F1 | resolved |
| F2 | resolved |
| F3 | resolved (효과는 Driver 관측 의존) |
| **남은 필수 findings** | **0** |
| 최소 보정 | 없음 |

- **Recommendation**: 제공 범위의 정적 검토 기준으로 R1 필수 보정은 해소되었으며, **R1 통과로 판단합니다.**
  - §3의 1번(`include_internal` 라벨을 transport 경계에서 관측)과 3번(`stream_request` 타입 경로 unit test)은 선택적 강화입니다. 필수 조건이 아닙니다.
- 이 판정은 정적 추론과 Driver 관측 자료 인용에 근거합니다. Reviewer가 재현한 결과가 아닙니다.
- 이 판정은 Owner 결과 수락이나 더 넓은 production 적격을 대신하거나 함의하지 않습니다.
````

### Driver Disposition And Owner Boundary

F1/F2/F3 resolved 판정을 받아들인다. 필수 잔여0이고 추가 보정/검토 호출은 하지 않는다. F3의 효과는 Driver의 generator와 byte 비교 실행 근거이며 Reviewer가 재현한 결과가 아니다. wire_profile의 include_internal은 고정 분기 상수이고 transport의 별도 관측 필드가 아니라는 비필수 지적도 유지한다. typed stream_request는 통합 실행에서, Value stream encoder는 focused unit에서 확인했다. 일반 인증 executor/header/contributor/compression 동등성, syscall 수준 network 무시도, OS worker, non-macOS/release/full workspace는 주장하지 않는다.

Owner 결과 수락은 아직 없다. 기존 중단 작업의 완료·Core grant/ticket/H05 승인·실제 모델/CLI 교체·제품 Git publication·STATUS 변경을 이 검증으로 진행하지 않는다. 현재 checkpoint는 승인된 A 초기 proof 구현·검증·R1까지의 완료다. source와 실행물은 Owner가 이 좁은 결과를 판단할 대상으로 유지한다.

## Cleanup Proposal And Auto-Review Block — 2026-10-22

standing cleanup을 적용하기 전에 task 소유권·현재 source23파일·두 binary SHA/권한/mtime·시스템 dylib 의존을 확인했다. recorded process group82개는 모두 종료됐고 lsof target 조회는 output 없이 exit1(열린 파일 없음)이었다. source·두 실행물·필수 승인/실패/최종검증/review 입력과 원문은 제안 삭제 대상 밖에 있다.

그러나 자동 승인 검토가 삭제 실행 명령을 거절했다. 사유는 “recorded Owner result-acceptance end condition is not met; standing cleanup authorization does not yet cover deletion of roughly50GB build/schema artifacts”였다. 프로세스 시작 전에 거절되어 제안 삭제나 명령 안의 기록 변경은 전혀 실행되지 않았다. 우회 재시도/축소 삭제를 하지 않았고14개 대상이 모두 남아 있음을 재확인했다.

Owner에게 요청하는 추가 결정은 이 좁은 A 초기 proof 결과의 수락과 아래14개 task-owned 재생성 가능 경로의 삭제다. 삭제하면 같은 집중 build/tests 재실행에 재컴파일이 필요하다. 현재 두 실행물의 실행과 source/검증 기록 열람에는 아래 cache가 필요하지 않다.

Task root: `private-evidence/E003` [공개용 중립화]

| 삭제 대상(위 root 기준) | 성격 |
| --- | --- |
| `target/debug/incremental`, `target/debug/deps`, `target/debug/build`, `target/debug/.fingerprint`, `target/debug/examples` | 재생성 가능한 compilation cache |
| `target/debug/.cargo-lock`, `target/debug/codex-app-server.d`, `target/debug/codex-prepared-tool-plan-fixture.d`, `target/tmp`, `target/.rustc_info.json` | 종료된 build metadata/temp |
| `fixtures/generated-schema`, `fixtures/generated-stable-schema`, `fixtures/generated-correction2-stable`, `fixtures/generated-correction2-experimental` | source 적용과 최신성 검사가 끝난 생성 복사본 |

보존 대상은 별도 source checkout 전체의 현재 변경, `target/debug/codex-app-server`, `target/debug/codex-prepared-tool-plan-fixture`, 승인안·controller/profile/catalog·실패/최종 raw logs·합성 fixture·review 원문/입력·이 기록이다. task-local Rust toolchain과 Cargo source cache는 Owner 결과 검토 및 정확한 offline build 재구성 입력으로 남기고 결과 수락/후속 범위 결정 때 재평가한다. active path 변경0, 삭제0, 추가 backup0이다.

## Accounting Before Owner Acceptance

현재 누적 활동은153.60분/600분이고 남은 승인 한도는446.40분이다. 설치·구현·build/test·review 대기와 기록을 포함하며 기존 Owner 대기361.925초를 제외하고 겹친 wall time은 한 번만 계산했다. 종료 기록의 최종 산술은 private budget.json을 따른다. 현재부터 Owner 결과 수락/cleanup 승인 대기를 제외한다. 종전 U2 사용량은 별도 중단 장부 그대로이며 이 사용량으로 초기화하거나 합치지 않았다.

최종 counter: App Server21/36 starts, fixture threads17/72(실패 예약 포함), simulated turns14/72, 시험 runtime real provider0, 보정2/2, R1 2/2다. 첫 보정은12/12 starts, 두 번째는8/12 starts이고 추가 자동 retry는 없다. 현재 target 전체 du 할당량은55047824KiB이며 이 중 두 binary를 제외한 약50GiB 중간 자료 삭제가 보류됐다. required input/output은 durable task/source 경로에 그대로 읽을 수 있고 실행 중인 task process는 없다.

## Owner Acceptance And Approved Cleanup — 2026-10-22

Owner가 직전 결과 수락·14개 경로 정리 묶음 요청에 “승인”으로 답했다. 이전 자동 승인 검토 거절 사유인 결과 수락 조건은 충족됐다. 이 승인은 초기 offline proof와 명시된 중간 자료 정리에 한정하며 실제 CLI 교체·Core/H05·기존 U2 완료·Git publication·Work Done/STATUS 변경으로 확장하지 않는다. 삭제 전 source23파일·두 실행물·필수 evidence 및 사용 중인 process를 다시 확인하고, 실제 삭제 결과를 이어 기록한다.

### Cleanup Completion

정확히 승인된14개 경로를 삭제했고, 삭제 전 중복 inode를 제외한 할당량은55116210176bytes(51.33GiB)였다. 이는 삭제 대상의 할당량이며 APFS snapshot 등을 포함한 전체 볼륨의 실제 여유 공간 증가량을 뜻하지 않는다. `logs/cleanup-result.json`에 각 경로 삭제 직후 checkpoint와 최종 검증 결과가 있다.

- 보존: source23파일, 두 binary 및 승인·controller·합성 fixture·실패/최종 검증·review 입력/원문을 포함한1370개 파일의 삭제 전후 SHA 동일성을 확인했다. 두 binary는 system dylib만 참조하며 삭제된 deps에 의존하지 않는다. 이후 이 문서의 current summary 변경에 맞춰 review metadata의 원문 위치 offset만 갱신했고, 두 review 원문 byte 동일성은 다시 확인했다.
- 활성 경로: 변경0. source checkout, binary, evidence 경로를 이동하거나 retarget하지 않았다. 추가 backup0.
- 삭제: 위14개 compilation cache/build metadata/generated schema 복사본. 현재 같은 build/test 재실행에는 재컴파일이 필요하다.
- 사용 여부: target 및4개 generated schema 경로의 lsof는 열린 파일 없이 완료됐다. 과거 기록에서 중복을 제외한 process group 번호60개는 없었고, 나머지50208은 과거 fetch 종료 이후 새로 시작한 macOS AssetCacheSubscriber였다. 실행 시각·system executable 신원을 확인했으며 이 service에 signal을 보내거나 종료하지 않았다. 최초 signal0 검사는 권한 제한으로, 다음 검사는 이 번호 겹침으로 각각 삭제 전에 중단됐다. 최종 ps/lsof 확인 후에만 삭제했다.
- 보존 이유와 종료 조건: 두 source checkout의 고유 미commit 변경과 필수 증거는 Driver/Owner의 기존 U2 재개 범위 결정 및 source 반영 판단에 필요하다. task-local toolchain/Cargo source cache는 같은 offline source를 재구성하는 고정 입력으로 보존한다. 후속 범위가 결정되면 필요한 입력을 확정하여 재평가하고, source 반영 또는 해당 후속 작업 포기 때 미사용 recovery/cache를 다시 정리한다. checkout/branch 삭제·Git publication·Work Done/STATUS 변경은 수행하지 않았다.

### Final Accounting After Cleanup

누적 활동157.52분/600분, 남은 승인 한도442.48분이다. 이번 Owner 응답 대기365.37분과 이전 대기361.925초를 제외했다. 정리 재개 후 검사·삭제·기록 시간은 포함한다. App Server21/36, fixture threads17/72, simulated turns14/72, runtime real provider0, correction2/2, R1 2/2로 실행 counter 변화는 없다. 결과 수락 및 승인된 정리는 완료됐으며 추가 runtime/build/review 실행은 하지 않았다.

## Follow-Up Planning — 2026-10-22

Owner가 실제 연결 실행안 구체화를 지시했다. [Live Qualification Plan](prepared-tool-plan-live-qualification-plan.md)이 새 계획과 preliminary R0 진행을 소유한다. 이 accepted offline proof의 결과·범위·수락은 그대로이며 실제 인증·network·U2 통합으로 확대하지 않는다. 현재 후속은 문서 준비만 승인됐고 구현/검토 실행은 아직 하지 않았다.
