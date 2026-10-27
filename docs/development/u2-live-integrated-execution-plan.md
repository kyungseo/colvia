# U2 And Live Connection — Integrated Execution Proposal

Status: corrected after one authorized static R0, 2026-10-22; awaiting Owner approval of this execution bundle. Reviewer verdict remains REVISE. Driver plan dispositions are complete; implementation, build, runtime authentication and H10 execution have not started.
Progress owner: [FEAT-20261022-001](FEAT-20261022-001-prepared-tool-plan-live-qualification.md). Existing U2 source record remains paused until the explicit handoff below is accepted.

## Outcome And Unchanged Completion Criteria

U2의 최종 목표는 기존 프로젝트의 실제 업무 하나를 같은 Work 안에서 수행·검증·허용 보정하고, 중단 후에도 동일 승인·남은 예산으로 이어가며, 실제 결과 품질과 Owner 부담까지 확인하는 것이다. [원 H01–H10 완료 기준](u2-single-host-continuous-work-plan.md#verification-and-completion-criteria)과 [고정 case/recovery 명세](u2-single-host-continuous-work-plan.md#fixed-verification-ids-and-recovery-cases)는 그대로 유지한다. 아래 표는 검사 배치 위치를 설명하며 원 기준을 축소하거나 대체하지 않는다.

통합은 동일 구현·동일 위험 검사의 중복을 줄이는 선택이다. 결과 품질이 사전에 보장된다는 뜻은 아니다. 품질·권한·복구 기준을 충족하지 못하면 미완료/실패로 보고한다. 시간·도구 한도에 맞추려고 대상5문서, verifier, 실제 host 검사나 H10을 빼지 않는다.

| 기준 | 유지할 결과 | 새 근거를 만드는 단계 |
| --- | --- | --- |
| H01 | 실행/delegate 결속; 다른 thread/turn/call, Owner 사칭·home/action/scope 거절 | S2 집중 negative + S4 실제 host 경로 |
| H02 | exact ticket/result/bytes; 교체·변조·중복 거절, control 무변경 | S2/S3 + S4 |
| H03 | 실제 worker의 control/runtime/Git/policy/credential·alias/symlink·권한/network 우회 차단 | S3와 실제 적용 직전 S6의 해당 경계 |
| H04 | ordinary isolated-worker grant의 정상 accept1회; 사용/revoke/다른 Work/action 거절 | S4 순정 installed Core 경로 |
| H05 | S0–S5 실제 process death·종료·pending 보존과 Owner가 승인한 원 actor/decision의 exact replay | S4; exception injection만으로 대체하지 않음 |
| H06 | 고정 verifier fail → 같은 scope 보정 → pass | S4 합성 및 S6 자연 발생 시 관측 |
| H07 | 승인·입력·직전 결과·문맥·누적 시간/시도 복구; drift/missing budget 거절 | S2/S4; 단순 새 thread 시작은 통과 아님 |
| H08 | 새 범위/ticket/revoke/상한/Owner 중단/근거 없는 실패 반복/제출 뒤 편집에서 중지 | S2/S4/S6 |
| H09 | ordinary/same-Work/umbrella 분류3사례 및 이유·미결 | S4 |
| H10 | 실제 기존 업무의5문서 정확성·누락·불필요 수정·근거·scope와 Owner 재설명/승인/조작/대기 관측 | S6. 미실행/Owner 시간 미측정이면 해당 기준 미완료 |

실제 업무에 보정·중단이 자연 발생하지 않으면 이를 강제로 만들지 않고 H06/H07의 합성 관측과 구분한다. 합성 통과만으로 U2 완료나 일반 생산성 향상을 선언하지 않는다. Core 계약, 일반 작업/위임의 권한, source 결과 수락과 실제 업무 결과 수락은 그대로 분리한다.

## One Candidate And Three Responsibilities

- candidate runtime: 기존 native ChatGPT 인증·정책·고정 gpt-6-astra/xhigh를 사용하고, prepared plan을 최종 HTTP 송신·도구 dispatch에 결속한다. Ordinary/OfflineFixture/Live mode와 Clock/U2 tool profile을 시작 시 고정한다.
- trusted host: admitted thread/turn/call과 고정 도구를 검증하고 누적 실행을 통제한다. exact target/actor/action/Work/revision/result/evidence/ticket은 host가 소유한다. Core는 기존 installed CLI를 호출하며 host가 Core를 import해 권한 판단을 대체하지 않는다.
- isolated document worker: 승인된 read 파일과 결과5파일만 처리한다. auth·network·Core/control·managed runtime·Git 관리 영역·host 입력에는 접근/쓰기 권한을 주지 않는다. model에 일반 shell·임의 path·MCP/plugin/subagent를 제공하지 않는다.

문서 도구는 file-ID 기반 batch read/write, 고정 verify, sealed accept의4종이다. read는 최대8개의 고정 file-ID 목록, write는 단일 file-ID·이전 bytes digest·UTF-8 전체 교체만 받는다. 아래 보정 계약의 호출/크기/문맥 한도를 적용하고 exact 파일과 경로는 해당 대상 승인 입력에 결속한다. 필요한5문서를 처리할 수 없는 제한이라면 scope를 줄이지 않고 부적격으로 중단한다. DOC-LINKS/GFM/CLAIMS의 정적 확인을 전체 사실성의 자동 증명으로 부르지 않는다.

L0의 단계별 fresh-thread 안은 최소 구조 비교안이었다. 본 실행안의 정상 경로는 같은 Work의 같은 ephemeral thread를 유지하고 turn마다 새 prepared handle을 쓰는 것이다. prepared snapshot에 native reset version/token, prepare 시점 for_prompt 항목열의 개수·정규 bytes digest와 승인 input digest를 결속한다. 정상 gen2의 허용 delta와 초과 call 처리는 아래 보정 계약으로 고정한다. 근거는 현재 source의 `session/mod.rs:4721` native clone_history와 `session/turn.rs:1769` prompt 생성 경로이며 구현 검증은 아직 없다. 새 history 저장 엔진을 만들지 않는다. process 재시작 때만 새 thread를 만들고 Work의 승인·원 입력·현재 문서·직전 검증·누적 사용량·pending 상태로 필요한 문맥을 복구한다. 설명 누락·반복 설명 부담·context limit을 숨기기 위해 임의 요약/절삭이나 새 thread로 우회하지 않는다.

각 turn은 승인된 도구 dispatch 최대1회와 generation 최대2회를 유지한다. accept와 문서 편집을 같은 call로 합치지 않는다. runtime handle은 일회성 실행 결속이고 Core ticket은 기존 권한/결정 입력이다. 둘은 서로 대체되지 않는다.

## Source Boundary And Early Feasibility Gate

입력은 accepted offline proof의 source base와21 tracked+2 untracked 변경, 기존 U2 host source/미해결 findings, 원 U2/H 명세 및 live v2의 M-01–M-13이다. 정확한 source/diff/untracked/build identity는 기존 private metadata를 재사용하고 각 실행 전 drift를 확인한다.

기본 수정 경계는 [L0의 Minimum Proposed File Boundary](FEAT-20261022-001-prepared-tool-plan-live-qualification.md#minimum-proposed-file-boundary)를 따른다. 주요 묶음은 다음과 같다.

| 묶음 | 수정 범위 |
| --- | --- |
| 공통 runtime | app-server lib/message_processor/config_manager/turn_processor, 별도 `app-server/src/bin/prepared_tool_plan_live.rs`와 Cargo bin 선언; core client/config/session/prepared/turn/turn_context/tool spec/router/registry/environment_context/turn_metadata; experimental prepared protocol과 대응 tests |
| auth/HTTP/policy/model | login auth manager/storage; http-client client_builder/client/transport/request; codex-api endpoint/session; backend-client client; cloud-config lib/service/bundle_loader/backend; model-provider models_endpoint와 필요한 lib 노출; 대응 tests |
| U2 연결 | 기존 verification/u2-host의 host.py/README, tests/test_u2_host.py·fixtures/u2_host.py; 같은 디렉터리의 worker.py·tool-profile.json 신규 |
| 실행 보조물 | 기존 task durable root의 launch/controller, process별 Seatbelt profile, fixed input/case catalog, 최소 recovery bundle, logs/results. 새 worktree·새 toolchain·전역 설정 변경은 기본안에 없음 |

동일 native mode/handler/history를 위한 module 선언·직접 대응 tests만 포함한다. 기존 dynamic forwarding, StaticModelsManager, route-aware pool, analytics disabled client, CONNECT proxy를 재사용하며 그 제품 의미를 재설계하지 않는다. authority Core source/schema, managed 배포/adapter inventory, 원 CLI 설치본, auth 저장소 내용은 수정하지 않는다. 실제 worker candidate commit은 아래 S6의 exact 별도 승인 뒤에만 한다. source commit/push/PR/merge/release는 제외한다.

S0의 남은 입력 고정에서 unresolved sender/constructor·write-root·loader·retry와 exact OS profile의 최소 요구를 아래 Go/No-Go 표에 따라 닫는다. 이 작업은 최종 실행안 승인 후, 코드 수정 전의 첫 단계다. 이 gate는 L0 No-Go를 자동 PASS로 바꾸지 않는다. 위 목록 밖의 실행 module, 더 넓은 권한, 새 sandbox/proxy/credential 방식이나 Core 변경이 필요하면 구현 전에 이유와 최소 delta를 보고하고 중단한다. source/예산/권한을 자동 확대하지 않는다.

필수 구현은 native read-only auth와 keyring 내부 write 차단, stale/reload/recovery/agent-identity 거절, 정책의 단회·무cache·고정 bundle, 성공한 native model catalog 고정, final headers/bytes guard와 fsync send reservation, reqwest retry0/redirect0/TLS fallback0, 금지 sender 생성 차단, 실제 response/cancel 종료와 dispatch reservation 분리다. host의 기존 inventory/env/late-warning/notification/cleanup findings도 같은 묶음에서 보정한다.

## Stages And Estimated Time

단위는 분이다. 합계는 승인된 후속 활동의 wall time이며 구현·build·검사·reviewer 대기·기록·종료를 포함한다. Owner 응답만 기다리는 시간은 제외하고, 그동안 진행한 독립 작업과 겹친 실행은 한 번만 센다. 기본은 한 Driver의 순차 수행이며 병렬 agent 절감은 가정하지 않는다.

| 단계 | 구체 작업과 산출 | 예상 | 단계 중단 상한 |
| --- | --- | ---: | ---: |
| S0 | R0 1회·계획 보정 완료분을 carry. 승인 후 코드 수정 전 exact 정적 입력 고정은 추가10–15분 예상 | 완료 실측 + 10–15 | 기존45 중 잔여 |
| S1 | 공통 live auth/policy/model/HTTP/mode·privacy/send guard 구현, 해당 focused checks | 110–160 | 200 |
| S2 | U2 callback·문서 worker·ticket/예산/문맥·중단/cleanup 통합, 기존 host findings 및 focused checks | 110–170 | 210 |
| S3 | 한 candidate의 build, 필수 offline negative·실제 OS canary·영향 fixture8, ordinary 기본 경로 smoke | 90–135 | 150 |
| S4 | live clock 최소1턴, 같은 candidate의 합성 H01–H09; H05 원 ticket packet 및 승인 후 순정 replay | 55–85 | 105 |
| S5 | 최종 Colvia normal/parent-O 각각1회, discovery·실패·cleanup 확인 | 125–145 | 180 |
| S6 | 실제 대상 준비 확인·intent/grant, 원5문서 Work/H10, exact candidate commit 승인·publish/accept·내용과 Owner 관측 | 60–90 | 120 |
| S7 | 통합 R1·필수 처분·근거/잔여·보존/정리·결과 보고 | 30–45 | 60 |
| 남은 작업 합계 | S0 잔여10–15 + S1–S7 합계580–830 | 590–845 | 전체960에서 S0 기사용 차감 |

R0/보정 완료 뒤 남은 예상은590–845분(9시간50분–14시간5분), 신뢰는 낮다. 이번 S0 기사용을 더한 전체 예상은 기존605–870분과 비교해 보고하며 단축을 약속하지 않는다. S3의 cold build45–75분은 판단값이고, S5는 과거 실패한 normal/O pair117.53분을 시간 참고로만 사용했다. 나머지도 이 통합 후보의 실측이 없다. 특히 read-only auth 적격성과 모델 지연,5문서 작업의 실제 보정량이 불확실하다. 절감할 구조는 확정했지만 절감 시간을 측정한 것은 아니다.

제안하는 통합 묶음 전체 중단 상한은960분(16시간)이며 이번 R0 준비·실행·처분 실측도 포함한다. 승인 뒤 새960분을 시작하지 않고 기록된 S0 기사용을 뺀 잔여만 사용한다. 마지막20분은 종료/보존에 남긴다. 단계별 상한은 독립 ceiling이고 합산한 실행 권리가 아니다. 단계 또는 전체 중 먼저 도달하는 상한이 적용된다. 최초 build 적격 판별은 build 시작 후90분 이내, full pair는180분 이내다. S0/S3/S4 종료 때 실측으로 남은 예상과 완료 가능성을 갱신하며, 실행이 예상보다 커지면 상한 직전까지 숨기지 않고 보고한다.

기존 U2 사용9781.67초(163.03분)와 live/L0 사용1334.87초(22.25분)는 그대로 남는다. 새960분을 승인한다면 이 두 장부와 연결한 누적 상한은1145.28분(약19시간5분)이다. 기존600/480/host120분의 남은 한도로 통합안을 완주한다는 뜻이 아니며, 승인 시 후속 부분의 상한을 위 표로 명시적으로 대체하는 제안이다. host 기사용56.12분은 이미 U2 사용량에 포함하므로 다시 더하지 않는다. 완료된 offline proof157.52분과 이전 live 계획/R0 19.84분은 별도 historical ledger로 보존한다. 이전 계획/R0 19.84분은 live/L0 22.25분보다 앞선 별도 활동 구간이며 서로 포함하지 않는다. 이번 계획 작성 시간도 별도로 기록하고 새 실행 사용량을 조작하지 않는다.

## Duplicate Work Removed Without Coverage Loss

| 줄이는 중복 | 공유 방법 | 유지할 검사 |
| --- | --- | --- |
| clock용 연결 후 U2용 연결 재구현 | 한 auth/policy/model/HTTP/mode 기반에 Clock/U2 profile만 분리 | clock과 U2 각각의 tool-envelope·callback·권한 검증 |
| 두 단계의 별도 cold build | S1/S2 변경을 모아 S3 candidate build. 개발 중에는 해당 crate/target만 점검 | 최초 build 적격 gate, 변경 뒤 필요한 재build와 binary 결속 |
| 같은 공통 경계 negative의 이중 실행 | exact candidate/profile/입력에서 동등한 guard 검사는 한 receipt를 두 소비처가 참조 | profile·worker·Core·실제 계정이 다르면 별도 검사 |
| clock 완료 후 U2에서 fixture8 반복 | 통합 candidate의 S3에서 영향 fixture8 한 번 | 이후 공통 동작이 바뀌면 그 영향 case만 재검사 |
| 단계별 전체 회귀와 별도 최종 review | Colvia normal/O 각1회 및 통합 R1 기본1회 | 기존 full 실패/새 권한·복구 상호작용 때문에 full pair는 면제하지 않음 |
| 바뀌지 않은 source의 재증명 | 식별된 accepted proof/기존 Core 근거 재사용 | 새 live/host/worker 환경 및 변경된 envelope/history는 새 증거 필요 |

새 crypto identity나 digest만 바뀌었다고 green 검사를 반복하지 않는다. 반대로 테스트·runner·assertion·discovery·권한·공통 fixture가 바뀌면 영향 분석 없이 과거 PASS를 재사용하지 않는다. 기존 live R0 M-01–M-13, 원 U2 R0 F-01–F-08, host 미해결 F1/F2/F3/F6/F8/F10/F11/F12, 이번 IR0-01–IR0-16을 같은 coverage/disposition 표에 연결한다. 합성·실제 실행·상속 근거·미확인을 구분하며 같은 receipt를 실행2회로 세지 않는다.

Python focused 선택은 기존47개와 신규 host8개 ID를 출발점으로 삼고, env/inventory/late notification/cleanup/history/CAS negative를 해당 host test에 추가한다. full701은 옛 예상값이지 강제 collection 수가 아니다. 실제 discovery와 delta를 고정한 후 전체를 실행하며 필요한 새 case를701에 맞추려고 빼지 않는다. Rust는 auth/storage, HTTP builder/final guard, cloud/model, prepared/runtime의 바뀐 경계만 집중 검사한다. full Codex workspace test는 기본안에 추가하지 않는다.

## Invocation And Attempt Limits

아래 명령은 구현할 interface 제안이다. 현재 host에는 preflight만 있으므로 qualify/iterate/actual/recover/live-smoke가 구현됐다고 주장하지 않는다. `PY`, `SOURCE`, `RUNTIME_SOURCE`, `ARTIFACT`, `SPEC`은 S0의 private 고정 입력에서 기존 승인 절대경로·digest로 치환한다. 모델은 argv/spec/path를 고르지 않는다.

- Runtime build (IR0-09): approved Rust toolchain의 `cargo build --offline --locked -p codex-app-server --bin codex-app-server --bin codex-prepared-tool-plan-fixture --bin codex-prepared-tool-plan-live`, cwd=`RUNTIME_SOURCE/codex-rs`, process-local `CARGO_TARGET_DIR=ARTIFACT/integrated-candidate-target`를 고정한다. 새 target의 부재 또는 이 task 소유·상태를 확인한 뒤 사용하고 기존 두 accepted binary의 경로/bytes는 build 전후 대조한다. 기본 target 출력이나 기존 accepted binary를 덮어쓰지 않는다. missing dependency/lock drift는 자동 fetch/upgrade 없이 중단한다.
- Host: `PY -I -B SOURCE/docs/development/verification/u2-host/host.py COMMAND --spec SPEC`; COMMAND는 live-smoke, qualify(H01–H05), iterate(H06–H08), actual(H10 편집), actual-accept(H10 봉인 후 수락), recover의 고정 allowlist다. H09는 기존3사례 문서 판정이다.
- Python 검증: 기존 task native runner의 collect, focused exact IDs, full normal, full optimized를 사용한다. normal/O는 각각 기본6300초, pair180분과 전체 잔여가 먼저 적용된다. native child의 기존 assertion·timeout·격리 정책을 줄이거나 바꾸지 않는다.
- RPC: native initialize/admission → thread/start → turn/prepare → turn/startPrepared. 같은 thread의 다음 turn도 새 handle·현재 history 결속을 요구한다. shellCommand/filesystem API·permission escalation·미등록 request는 거절한다.

| 항목 | 제안 상한과 처리 |
| --- | --- |
| candidate build | 최초1회 + 필수 보정 후 최대2회, clean rebuild 기본0. targeted test compile도 시간 장부에 포함 |
| runtime offline qualification | App Server36 starts/72 threads/72 simulated turns. Core 회귀 subprocess는 이 모델-runtime 카운터와 구분해 S5에 계상 |
| live runtime | 총6 starts(clock/synthetic/H10 각각 최대2), live threads 총8(clock2/synthetic4/H10 2), proxy2 starts. 실제 credential read는 승인된 native startup 경로에서만; refresh/relogin/store mutation0 |
| live model turns | clock 최대2, synthetic U2 최대12, 실제 H10 최대40; 합계54. 모두 최대치이며 필요한 최소만 사용. phase 간 자동 전용 없음 |
| generation/control | turn당 generation 최대2, 전체108 sends; control start당4·전체24. HTTP 내부/SSE/WS/auth/route retry와 fallback0. 예약 실패·초과는 실패로 중단 |
| 보정 | 같은 scope·oracle의 실패 후 수정 묶음 전체 최대2. 각 묶음은 관련 focused check만 수행; Core authority apply는 자동 retry 대상이 아님 |
| review | 변경 경계 R0 1회, 최종 통합 R1 기본1회·필수 보정 확인 때만 최대2회; CLI 각15분, 단계/전체 잔여 우선 |
| process 제한 | 모델 turn 최대15분, 일반 host case5분. 단계/전체 잔여 우선. TERM10초→KILL10초 및 실제 종료 확인; 불명확한 descendant는 미확인으로 중단 |

Clock 두 번째 turn은 최초 범위 안의 필수 보정·영향 negative 재통과 후에만 가능하다. 실제 auth 만료/401/403/계정 불일치·Keychain prompt·정책 불명·모델 부재·unexpected sender/권한 요구는 남은 횟수가 있어도 중단한다. 모델을 바꾸거나 API key를 쓰지 않는다. 장기 실행 중 read-only 인증이 유효기간을 넘으면 이 상한 내에서도 중단할 수 있다.

S4 negative는 fake provider/고정 callback 입력으로 실제 candidate·host·worker·installed Core를 실행하는 검사와 실제 provider의 성공 흐름을 구분한다. 모든 거절 case마다 provider를 호출하지 않지만, 단순 unit mock을 실제 host/OS 결과로 표시하지 않는다. H10의40 turns는5문서의 read/write·verifier·수락 및 허용 보정을 담기 위한 ceiling이며, 상한 부족을 이유로 파일이나 완료 기준을 줄이지 않는다.

## Approval, Review And Ownership

Owner는 통합 계획 작성에 이어 고정98,424bytes 입력을 Claude 외부 서비스에 보내는 정적 R0 1회를 명시 승인했다. 해당1회는 완료했다. 이번 승인에는 구현·build·runtime auth/model·실제 대상 접근/Git이 포함되지 않는다.

source [Workflow: Review And Evidence](WORKFLOW.md#review-and-evidence)는 “R0 reviews a plan before execution approval; R1 reviews the resulting change before result acceptance.”를 요구한다. 이번 R0는 fresh Claude CLI로 한 번 수행했고 REVISE/필수13건·선택3건을 받았다. 원문과 항목별 Driver 처분은 진행 기록에 보존했다. 아래 보정안은 Driver가 반영했으며 재검토 PASS라고 주장하지 않는다. 추가 R0는 기본안에 없다. Owner가 이 최종안을 승인하면 S0 잔여 정적 입력 고정 후 Go일 때만 S1을 시작한다. R0는 실제5문서/계정/절대 로컬 경로를 전송하지 않았고, 호출 전 구독 firstParty 인증을 확인했다. 제안하는 실행 승인에는 S7의 fresh Claude 정적 R1 기본1회·필수 보정 확인 때만 최대2회와 그 bounded packet의 Claude 외부 전송도 포함한다. packet은 통합 source 변경·synthetic case·비식별 검사 요약/identity로 제한하고 실제5문서 본문·계정·credential·실제 target 경로를 제외한다. 호출마다 이 경계·입력 identity·구독 firstParty 인증을 확인한다. 이 제안은 현재 R1 호출/전송 권한이 아니다.

실행안 승인 뒤에는 범위 내 단계 이동·집중 검사·정해진 보정·R1 호출마다 재승인을 요구하지 않는다. 남는 Owner 판단은 실제 내용이 생겼을 때의 H05 exact 원 ticket 복구, H10 대상/read·provider 전달 범위/intent/grant와 required refs, base tag/worker setup의 exact 이름·OID·부재, worker candidate commit1개의 diff·hook·identity·메시지·result tag, source 및 실제 결과 수락이다. 동일한 승인·동일한 exact 입력을 다시 승인받지 않는다.

H10은 기존5문서와 verified installed release를 그대로 사용한다. 실제 target의 다른 writer와 기준점·dirty/ignored 보존을 확인하며 clean Git만으로 writer 중단을 추정하지 않는다. 제출 전 편집/보정을 마친 뒤 exact diff·whole-tree·base·commit message/trailers를 제시하고 승인 후 trusted Driver가 candidate commit과 필요한 보존 ref를 만든다. 그 뒤 기존 publish/prepare/위임 accept 순서를 따른다. L0 기록의 “host submit 연결”은 이 기존 선행 gate를 생략하는 자동 제출 허가가 아니다. control Git commit/push/PR/merge, managed runtime update는 포함하지 않는다.

H05는 guard 내부 barrier/fsync 후 실제 process death를 확인하고, S1–S5의 원 ticket/actor/decision·pending·종료를 한 packet으로 제시해 정확한 replay1회 승인을 받는다. replay는 wrapper 없는 installed CLI다. S0는 자동 재호출하지 않고 mixed/all-post cancellation·위조/재사용 거절을 유지한다. trusted Driver가 인간 응답을 전달하는 기존 신뢰 한계를 유지하며 새로운 인간 인증 시스템으로 과장하지 않는다.

통합 실행안 승인에는 미완료 U2 host/H01–H10과 live 잔여를 FEAT-20261022-001 한 진행 기록으로 모으는 제한된 handoff도 명시한다. 승인 시 원 U2 기록에 dated pointer와 미완료 범위/사용량을 남기고 양쪽을 확인하며, 원문·accepted proof 결과·과거 verdict는 바꾸지 않는다. 현재는 handoff 미활성이다. 실제 프로젝트 Work narrative는 그 프로젝트의 승인·진행·예산을 계속 소유하고 source 기록에는 필요한 비식별 결과만 연결한다.

## R0 Corrections That Govern Execution

아래 계약은 이번 IR0 필수13건과 선택3건의 Driver 보정이다. 원 H01–H10 및 live M-01–M-13, U2 F-01–F-08을 유지한다. 순서는 이 통합 보정 → 원 지적 처분 → 초기 설명이며, 실행 증거가 없는 항목은 아래 gate에서 판정한다.

### History, Turn Input And Excess Calls — IR0-01, IR0-02, IR0-04

- prepare 시 reset version과 cancellation token, native `for_prompt()` 항목열의 순서·타입·개수·정규 bytes digest, 고정 host input template/version/digest를 저장한다. reset version만으로 내용 동일성을 주장하지 않는다. consume/gen1은 이 정확한 snapshot과 일치해야 한다.
- gen2에서만 허용하는 delta는 이 turn의 검증된 gen1 응답 항목열과 admitted call 최대1개의 대응 output이다. 항목 ID·순서·call ID·bytes를 원 응답/host 결과와 대조한다. 그 밖의 append/삽입/수정, reset 취소, 외부 pending input, guardian 경로 활성은 실패다. `executed_tool_calls.attach_to_prompt`까지 반영한 최종 body를 guard가 검사하며 guard 뒤 변형은 금지한다.
- `parallel_tool_calls=false`를 요청에 고정한다. gen1 stream 전체를 끝까지 받아 call 목록과 종료를 검증한 뒤에만 dispatch한다. gen1의 call>1, 미등록 call, gen2의 추가 call은 dispatch 전에 거절하고 turn 실패·thread 종료로 끝낸다. 해당 출력열을 같은 thread의 다음 turn에 보내지 않고 자동 보정/retry/새 thread도 시작하지 않는다. gen2 위반이면 gen1에서 이미 일어난 효과와 예약은 유지해 보고한다. 추가 dispatch는0, 이미 예약한 generation/turn은 소모다. 정상 무도구 최종 응답은1 generation으로 끝날 수 있다.
- host가 신뢰 기록에서 결정적으로 생성한 진행 template과, Owner가 직접 제공한 원문 메시지만 새 turn input이 된다. Driver의 임의 업무 지시·요약·재설명 추가는 없다. 불가피한 수동 개입은 명시적으로 중단 사유/개입으로 기록하고 H10 비용에서 숨기지 않는다. 복구 template은 승인된 goal/oracle/scope, 원 입력, 현재 승인 문서의 exact bytes/digest, 마지막 verifier, 남은 예산·pending을 file-ID 기반으로 결속한다. worker narrative 단독은 승인·예산 근거가 아니다.
- prepare input은 plain text 최대8 item, item당65,536 UTF-8 bytes를 그대로 유지한다. 경로·계정·credential·raw control ticket은 모델 template에 넣지 않는다. 복구·재송신 문서는 동일 H10 전달 승인에 포함돼야 한다. 초과하면 절삭/임의 요약/compaction 없이 unavailable로 중단한다. context 복구로 Owner 설명을 새로 받은 경우 별도 관측한다.

### Five-Document Turn And Context Budget — IR0-03

read schema는 `file_ids`의 중복 없는 목록(1–8개, 고정 allowlist)만 받고 arbitrary path는 거절한다. 한 호출의 결과는 ID/digest와 승인된 UTF-8 bytes를 합해 최대65,536bytes다. write는 단일 ID, expected prior digest, 최대65,536 UTF-8 bytes 전체 내용만 받는다. ID별 read 결과를 임의 절삭/요약하지 않는다. exact 파일 크기는 아직 조회하지 않았으며 아래 배분은 적격성 조건이다.

| H10 호출 배분 | 최대 turns | 조건 |
| --- | ---: | --- |
| 최초 승인 read 집합과5개 현재 결과 읽기 | 8 | 원 read27과5개가 겹치면 exact identity로 중복만 제거. 최대32개를 고정 ID 순서/byte limit으로 pack하여8호출 이하인지 확인 |
|5문서 최초 write | 5 | 파일별1회 |
| 최초 DOC-LINKS/GFM/CLAIMS | 3 | 각 고정 verifier1회 |
| 같은 scope 보정2묶음 | 16 | 묶음당 최대5 write+3 verifier. 공통 전체 보정2회 장부도 동시에 적용 |
| 봉인 후 accept | 1 | same-thread의 별도 쓰기 없는 turn |
| 추가 read/설명 없는 진행 등 여유 | 7 | 위 분류가 덜 쓰면 남겨 두며 phase 간 전용은 하지 않음 |
| 합계 | 40 | 매 turn dispatch≤1/generation≤2. 실제 필요한 최소만 사용 |

S0는 이 schema·산정식을 고정하고 synthetic bytes로 검사 설계를 닫는다. S6는 대상 read/provider 전달 승인 뒤, 어떤 target mutation보다 먼저 exact ID·bytes로 pack/최대 payload/예상 turns를 계산한다.8회 read 또는40turn 안에 필요한 처리가 들어가지 않으면 파일·oracle을 빼지 않고 중단한다. 승인 read가 늘어나야 하면 이 묶음의 자동 허용이 아니다.

context는 성공한 native model catalog/effective config의 window와 output reserve를 사용한다. 매 prepare 및 gen2 전에 실제 prompt/history와 허용 최대 다음 response/tool output, 남은 native framing을 포함한 크기를 검사한다. 기존 native estimator의 적용 가능성을 확인하고 가능한 상한을 보수적으로 잡는다. 계수가 검증되지 않거나 window/output 여유를 입증할 수 없으면 admit하지 않는다.40turn 전체의 예상 history 증가를 S4에서 관측하고 S6 exact byte 산정과 결합한다. context를 비우려고 thread를 갈거나 요약/compaction을 추가하지 않는다.

### Durable Budgets And Start Allocation — IR0-05, IR0-06, IR0-16

모든 start는 같은 task-owned durable budget journal과 단일 controller를 사용한다. phase별·전체 start/thread/turn/generation/control/dispatch·보정·활동시간을 함께 유지한다. 고정 lock 아래 순번/직전 checksum을 검증하고 effect/send 이전 reservation을 fsync한다. 승인 envelope·Work·candidate identity에 결속하며 worker는 이 장부에 접근하지 못한다. 동시 controller, missing/corrupt journal, 회수 불가능한 종료/시간은 unavailable이며0으로 만들지 않는다. 예약 후 crash나 송신 여부 불명도 소모로 남긴다. 새 candidate·process·thread가 카운터를 초기화하지 않는다. runtime auth 세부값은 장부에 넣지 않는다.

| phase | start/thread 배정 | 두 번째 start의 허용 용도 |
| --- | --- | --- |
| clock | start2/thread2 한도 | 최초 범위 안 mandatory correction1회. 적격성 negative 재통과 후만 |
| synthetic U2 | start2/thread4 한도 | 첫 process 최대2thread, 두 번째 process 최대2thread. 두 번째 start는 H07의 의도한 재시작에 우선 배정; 보정 재실행과 경쟁하면 여유가 없으므로 중단 |
| H10 | start2/thread2 한도 | 첫 편집 thread1, 봉인 이전의 실제 중단 복구1회에만 두 번째 start/thread. 사용 전 mandatory correction이 필요하면 같은 슬롯을 소비하며 복구 슬롯이 남는다고 주장하지 않음 |
| proxy | 총2 starts | 첫 proxy=S4 clock+synthetic, 종료 확인 후 두 번째=S6. 각 phase 내 runtime은 같은 proxy를 사용; proxy 장애의 새 재시작 슬롯 없음 |

H07의 새 thread는 봉인 전 편집 단계에서만 허용한다. 기존 prepared/dispatch handle은 무효화하고 trusted checkpoint로 새 admission을 만들며 원 scope/actor/budget을 유지한다. pending authority 결정이 있으면 일반 편집 복구로 들어가지 않는다. accept는 편집을 수행한 현재 admitted thread에서만 한다. 봉인 이후 runtime/thread 소실 시 새 handle/thread로 accept를 자동 재결속하지 않고 H10 미완료로 중단한다. 이미 apply가 시작됐으면 H05와 같은 exact 원 ticket 사람 복구 판단으로만 간다.

candidate commit 승인 대기 중에는 문서 worker 및 쓰기 child를 종료하고 runtime thread는 idle로 유지한다. send/refresh/background/generation은0, 대기 후 identity·예산·grant·원 auth 상태와 봉인 bytes를 재확인한다. 같은 thread의 도구 등록4종은 유지하되 host phase gate가 read/write/verify를 거절하고 accept만 허용한다. 이를 입증 못하면 종료한다. Owner만 기다린 시간은 활동시간에서 빼지만 인증 수명은 멈추지 않으며, 인증 만료 시 아래 중단 규칙이 우선이다.

### Privacy, Atomic Write And Verifier Boundary — IR0-07, IR0-08

final guard는 원천을 구분한다. runtime의 자동 context/metadata/header에는 실제 path/git/account 식별정보를 계속 금지한다. 승인 file-ID·exact source digest로 host가 전달한 문서 bytes는 별도 typed document segment로 결속하고, 그 문서에 포함된 식별정보의 전달 허용 여부까지 실제 Owner packet에서 정한다. read/write 도구 인자·결과와 복구 시 재송신도 이 승인 범위에 포함한다. 문서 예외를 임의 문자열/metadata에 적용하지 않는다. model이 생성한 candidate/응답은 untrusted이며 승인된 문서 변환 범위와 허용 식별정보를 검사하고, 새 비승인 식별정보·credential·원천 불명 내용을 후속 요청에 넣지 않는다. 검증할 수 없으면 거절한다. 민감한 원문 payload나 token을 일반 진단 로그로 복제하지 않는다.

원자적 교체 경로는 task durable root의 `worker-scratch/<run-id>/<file-id>.swap`처럼 파일별 하나로 고정한다. 생성 전 exact 부재·task 소유·대상과 같은 device를 확인하고, worker profile은 exact target와 exact swap의 생성/rename만 허용한다. 결과 디렉터리 전체 write는 허용하지 않는다. approved write input bytes를 해당 task 기록에 먼저 보존한 뒤, 검증한 parent dirfd·no-follow/exclusive open·fsync·원자 rename·directory fsync·사후 bytes/mode 확인을 적용한다. target/swap의 inode와 nlink=1, ancestor/symlink/alias·변경된 prior digest를 검사한다. writer quiescence와 host의 직렬 소유 조건이 깨지면 CAS 보장을 주장하지 않고 중단한다. 예상치 못한 swap 잔여/교체 실패는 보존·보고하며 자동 삭제/재시도하지 않는다. whole-tree 결과에는5개 결과 파일 외 swap이 없어야 한다. actual target와 같은 device 또는 literal rename 권한을 만족하지 못하면 H03 unavailable이다.

세 verifier는 network·임의 child 없는 동일 worker executable의 고정 verify mode에서 실행하고, 그 실행에는 결과 쓰기/swap 권한이 없는 read-only profile을 적용한다. read 집합은 승인된 doc/read ID와 고정 verifier 코드·최소 runtime으로 닫는다. DOC-LINKS가 범위 밖 target 내용/metadata를 필요로 하면 임의 read나 성공 생략을 하지 않고 검사 불가로 중단한다. DOC-GFM은 실제 GFM parser로 렌더 의미를 확인하며, DOC-CLAIMS는 고정 참조/주장 점검일 뿐 전체 사실성의 자동 보장이 아니다. script/profile/parser/ID와 source bytes를 결과에 결속한다. H03에 literal 생성·rename·symlink 및 hardlink alias negative를 포함한다.

### S0 Go/No-Go And Runtime Gates — IR0-11, IR0-12, IR0-13

| 시점 | 닫을 조건 | 미충족 시 |
| --- | --- | --- |
| S0, 코드 수정 전 | exact source/diff·모듈·argv·profile template·runtime/auth/output roots, reachable sender/constructor와 loader/retry 처분표, history/template/schema·phase/budget journal, case/receipt 재사용 표·recovery 입력 고정. 불필요 sender는 생성 거절, required sender는 final guard로 매핑 |45분 누적 또는 unresolved 범위/권한/unknown sender면 No-Go; S1 시작 안 함 |
| S3, 실제 인증 전 | 같은 candidate의 offline negative, ordinary/fixture 분리, worker literal 권한·DNS/direct egress·synthetic credential/mach canary, source/build/profile identity | 구현·OS 적격 실패. Keychain 실제 성공을 synthetic PASS로 바꾸지 않음 |
| S4, 실제 연결 | 고정 최소 mach로 prompt 없는 native auth, native policy/account/model 분류, guarded HTTP·실제 callback/history·latency/context | Keychain prompt/401/403/stale/unknown이면 거부·종료. 권한 확대·refresh/relogin0 |
| S6, target 부작용 전 | 실제 read/provider 승인 뒤 pack/context 산정, writer·installed 기준, S4 실측으로 목표 업무 남은시간/turns 적격성 | 부족하면 base tag/worker/intent publication 등 target mutation 전에 중단 |

S0는 전체 OS·계정 적격을 정적으로 PASS하는 단계가 아니다. 최소 OS profile의 exact 허용 항목을 정할 근거조차 없거나 추가 권한이 필요하면 S0 No-Go다. 허용 항목 안에서의 실제 동작은 S3/S4가 판정한다. 코드 수정 전에 남은 S0를 닫도록 승인하는 것이며 무조건 S1 진입 승인이 아니다.

이번 R0의 사전 승인 활동은 별도 측정한 뒤 S0 기사용으로 carry한다. 자동 승인 차단까지의 준비168.98초와 명시 전송 승인 뒤의 활동을 합하고 Owner 대기는 제외한다. S0의45분과 전체960분은 이 합을 포함하며 재설정하지 않는다. 최종 보고의 실측·잔여가 이 문서의 초기 예상보다 우선한다.

read-only auth가 만료/변경되면 중단 후 Owner 재판단을 받는 선택을 채택한다. 이 묶음은 start 사이의 일반 CLI refresh/relogin을 승인하지 않으며 다른 앱의 갱신을 기다려 자동 재개하지 않는다. S4의 성공은 S5 이후 S6 auth 유효성을 보장하지 않는다. 각 live start와 send 전 native 검증을 수행하고, attribution 불명 변경도 중단한다. 다른 프로세스를 자동 종료하지 않는다.

S6 시작 적격성은 S4 실측 중 가장 느린 유사 turn과 exact context 증가를 사용해 예상필요 turns·verifier·Git/authority·종료 시간을 보수적으로 합한다. H10이 더 긴 context이면 여유를 추가하고 근거가 부족하면 unavailable로 둔다. 예상 활동이 S6 잔여120분과 전체 잔여에서 S7 최소30분·종료20분을 보존한 시간 중 작은 값에 들어갈 때만 actual setup을 시작한다. Owner 대기는 예상 활동에서 제외하지만 auth 수명/idle thread 유지 가능성은 따로 확인한다. 이는 완료 보장이 아니므로 S6 중에도 새 보정 필요·지연으로 재계산해 잔여 부적격이면 추가 부작용 전에 중단한다.

### Original U2 Review Coverage And Actual Sequence — IR0-10, IR0-14, IR0-15

| 기존 finding | 통합안의 처분과 증거 위치 |
| --- | --- |
| F-01 retention refs | 지원 `refs/tags/`만 사용. base tag 이름·expected absence·OID/worker setup 승인 → base tag 검증 → worker 생성/start. result tag는 candidate 검증 뒤 publication 전. overwrite 금지 |
| F-02 edit/accept | actual 편집 → worker/child 종료·봉인 → exact candidate 승인/commit 검증 → result tag/publish/prepare → 같은 thread의 actual-accept. 등록4종 유지+phase gate로 read/write/verify 거절, H08-post-submit 실제 검사 |
| F-03 human recovery | trusted Driver의 exact 사람 응답 중계 한계 유지. packet/ticket/actor/decision/pending/종료/one-use 대조. worker 위조·drift·재사용 거절 |
| F-04 death barrier | synthetic wrapper만 writer guard 내부 barrier/fsync에 사용. 실제 process death/installed module identity 확인. H04/H10 및 replay는 wrapper 없는 installed CLI |
| F-05 effective policy | runtime synthetic cwd의 native mandatory config/read/inventory와 별도 실제 worker executable/profile/cwd/read/write map을 각각 관측. legacy override·예상 밖 tools 거절. synthetic canary와 actual profile identity를 결속하고 실제 control 침투 증명으로 과장하지 않음 |
| F-06 regression | actual discovery와 V24/기존47+신규8 및 영향 delta 확인; 기존 오류 재발도 실패.6300초/호출·pair180분·전체 잔여/종료 reserve 중 최소. full 재실행 자동 허용 없음 |
| F-07 candidate commit | exact hook 목록/hash·effective config·identity/환경·scope·메시지/trailers를 승인 packet에 포함. commit 후 parent/tree/bytes/mode/message/index 확인; 불일치면 자동 reset/amend/우회 없음 |
| F-08 refs/narrative | required intent refs는5 outputs와 동일/조상/자손 비중첩. 승인된5파일 안의 narrative는 start 뒤 첫 편집 전 trusted Driver가 seed; Work post-blob 근거로 결속.6번째 파일/추가 baseline commit 없음 |

실제 순서는 target/read·전달/intent/grant·base tag/worker setup 승인 → S6 시간/문맥 gate → base tag → worker/start → narrative seed → 편집/검증/허용 보정 → 봉인·쓰기 종료 → exact candidate commit/result tag 승인 → commit 사후 검증 → result tag → publish/prepare → 같은 thread accept다. intent publication이 setup 전에 필요하면 해당 승인과 시간 gate를 먼저 충족한다. H05 exact recovery는 실제 필요할 때 별도 원 ticket 판단이다. 승인된 동일 입력은 반복 승인받지 않는다.

OfflineFixture의 proof-model·빈 dynamic/network·단일 fixture root 검사 의미를 삭제하지 않는다. `validate_config`/`config_snapshot`을 mode별로 분리하고 Live는 native auth/runtime root 분리·Clock/U2 profile·proxy·history를 따로 검사한다. Ordinary 기본 동작도 대응 smoke로 확인한다. accepted fixture8은 기존 oracle을 유지한다.

## Preservation, Stop And Delivery

구현 전 기존 tracked diff·untracked 원문과 U2 host 입력을 최소 복구 bundle로 보존하고 bytes를 대조한다. 기존 두 binary와 원 검사 evidence는 유지한다. build/controller/log/result는 처음부터 기존 durable task root에 두고 tool temp는 허용된 process-local 하위 경로만 사용한다. global HOME/TMPDIR·사용자 credential·sandbox 정책은 변경하지 않는다.

scope/권한 확대, unknown sender, oracle 변경, recovery 입력 손실, 불명확한 authority apply, 근거 없는 같은 실패 반복, Owner 중단, 단계/전체/시도 한도에서 영향 작업을 멈춘다. 종료 상태·원 bytes·pending·잔여 비용을 기록하고 실패를 PASS로 바꾸지 않는다. 전체 상한 직전20분에는 새 부작용 작업을 시작하지 않는다.

최종 보고는 H01–H10 각각의 실행/상속/미확인 근거, required findings 처분, source/build/profile identity, 실제 품질·Owner 관측, 사용/잔여 시간, 보존·active path 변경·삭제·유지 이유와 adopter 영향으로 구성한다. 실제 H10 또는 Owner 관측이 빠지면 synthetic/source 후보 부분 성과만 보고하고 U2 전체는 미완료로 남긴다. 기본안은 Colvia managed 배포 변경이 없으므로 기존 adopter update를 자동 제안/실행하지 않으며, candidate CLI의 일반 지원·설치 완료도 주장하지 않는다.

## R0 Closeout And Remaining Budget — 2026-10-22

R0/Driver 계획 보정·검증·정리까지 S0 기사용 15.09분(Owner 대기 제외), S0 45분 중 잔여 29.91분이다. 승인 후 S0 입력 고정 예상10–15분은 이 잔여 안에 둔다. 전체960분 중 잔여는 944.91분(약15시간45분)이며 종료20분을 포함한다. 남은 예상590–845분을 더한 이 통합 묶음의 전체 활동 예상은 605.09–860.09분이다. 추정치는 낮은 신뢰의 판단값이며 S0/S3/S4에서 실측으로 갱신한다. 기존 U2/live 사용량과 앞선 계획/proof 장부는 보존한다.

정적 R0 1회(4.04분)의 REVISE 원문과 Driver 필수13/선택3 처분을 진행 기록에서 읽을 수 있다. 원 H01–H10 명세와 accepted runtime diff/untracked2는 무변경, 링크/수치/whitespace와 두 checkout의 diff check를 확인했다. 구현·build·runtime 인증/모델·실제 대상 작업은0이다. 최종 실행안 승인 전 정지하며, 승인 후에도 S0 No-Go 또는 실제 적격 실패는 중단한다.
