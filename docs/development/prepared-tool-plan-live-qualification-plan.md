# Prepared Tool Plan Live Qualification — Proposed Execution Plan

## Public Snapshot Notice

이 문서는 비공개 원본에서 식별 정보만 중립화한 공개 파생물이다. 원본이 과거 승인·리뷰·실행 기록의 기준이며 별도로 보존돼 있다. `[공개용 중립화]` 표지가 있는 인용·본문과 그 표지가 붙은 code block은 원문 그대로가 아니다. 아래의 과거 `Verbatim` 표기도 이 제한을 따른다. 기존 SHA-256은 원본 bytes 기준이며 이 공개 사본의 digest나 새 승인으로 해석하지 않는다. 결과·실패·수락 범위·수치·미측정 한계는 원래 의미를 유지한다.

`Reference A`는 실제 외부 대상의 중립 표기다. 실행 데이터의 합성 ID는 `synthetic-reference-a` / `synthetic-operations-guide-check`, 회귀용은 `synthetic-reference-a-regression` / `synthetic-operations-guide-regression`이다. 표시용 branch `reference-a-guide-branch`, 문서 `docs/briefs/reference-a-operations-guide.md`, `private-evidence/E…` 및 `private-approval/O…` 표기는 공개된 실제 경로나 실행 승인이 아니다. private 원본과의 대응은 비공개로 보존한다. 기존 실제 대상 재실행은 원본에 대한 근거이며, 중립화한 소스의 새 native PASS가 아니다.

Status: R0 completed with REVISE; Driver correction v2 prepared; implementation/live execution awaiting Owner approval. Corrected plan not re-reviewed.
Owner: human Owner. Driver: Codex. Reviewer: fresh Claude CLI, claude-opus-5-5; static review only.

## Decision And Practical Outcome

2026-10-22 Owner는 “진행해”로 실제 연결을 위한 실행안 구체화를 지시했다. 이 문서는 그 계획이다. 이후 Owner 승인으로 R0 정적 검토1회를 완료했다. 실제 runtime 인증 조회·network·build·구현은 시작하지 않았다. 기존 offline proof 결과 수락은 실제 연결 승인으로 확대하지 않는다.

권고는 기존 ChatGPT 구독 인증과 고정 gpt-6-astra/xhigh를 유지하는 clock-only live qualification이다. 같은 prepared plan이 실제 송신 직전과 dispatch에서 유지되는지 확인한다. 인증은 기존 저장소의 native read 경로만 사용하고 refresh/save/delete가 필요하면 중단한다. 이 제한은 일반 CLI의 자동 갱신 동작과 다르며 장기 운용 적격을 뜻하지 않는다.

순서: R0 계획 검토 → 보정된 실행안의 Owner 승인 → 격리·native auth 연결·최종 송신 guard 구현 → offline negative 검사 → 최소 live clock 검증 → R1·Owner 결과 수락 → 별도 U2 재개 판단.

이번 산출물은 별도 candidate, frozen launch/profile/case catalog, qualified 또는 unavailable 결과와 근거다. 실제 CLI 설치/교체, U2 adapter/H01–H09 구현, Core/managed runtime, H05 replay, 실제 프로젝트 자료, 제품 Git publication, typed Work/STATUS, 다른 모델/API-key fallback은 제외한다. clock-only process 검증을 OS worker/executor sandbox나 U2 완료로 부르지 않는다.

## Current Evidence And Gaps

| 구분 | 확인된 사실 | 새 검증의 필요성 |
| --- | --- | --- |
| Accepted proof | 최종8 cases, production HTTP body9개, clock dispatch4개; R1 필수3건 해소 | no-auth/non-compressed/in-memory fixture 범위 |
| 준비/실행 결속 | process-local 단회 handle, initial snapshot, 매 step registry/handler 제한 | live mode에서도 우회·재시도·권한 drift 없이 적용돼야 함 |
| client branch | core/src/client.rs의 prepared 분기는 ordinary auth setup 전에 mock 경로로 반환 | mock transport만 교체해서 ordinary auth/metadata 동등성을 주장할 수 없음 |
| HTTP boundary | http-client/src/transport.rs는 prepare_body_for_send 이후 request body를 실제 request에 넣음 | 이 최종 bytes와 destination을 guard한 뒤 바로 같은 request를 보내야 함 |
| Auth | login/src/auth/manager.rs의 auth()는 proactive refresh를 실행할 수 있음 | read-only native auth 선택과 refresh/write/identity-change 거절을 검증해야 함 |
| Policy | fixture bootstrap은 managed/login requirements를 무시하도록 설계됨 | live에 해당 ignore 설정을 복사하지 않고 local/cloud requirements를 정상 적용해야 함 |
| Regression | stable generator1066파일이 base와 동일; core/registry/protocol 집중 검사 통과 | mode 분리와 공통 guard 영향분만 다시 검사; fixture8은 공통 경로 변경 시 재실행 |

고정 source base는83086188ae0614bd882818ff1aa23f3194962012이고, accepted candidate는 변경23파일과 fixture binary SHA df5e7ab4b63fdfe8aa2b45eba8ad8fd7d956ebe228469d37a9fbe6d2d16973a6로 구분한다. base commit만으로 수정 candidate를 식별하지 않는다. 이번 계획 준비에서23파일 모두 accepted digest와 일치했다.

공식 문서는 ChatGPT 구독 로그인과 API key 과금을 구분하고, file/keyring/auto/ephemeral 저장 방식과 자동 token refresh를 설명한다. 이 사실은 현재 계정의 저장 방식·모델 접근·수정 candidate의 적격을 증명하지 않는다. [OpenAI Authentication](https://learn.chatgpt.com/docs/auth#credential-storage), 확인일2026-10-22. source 해석과 공식 제품 안내를 구분한다.

## Scope And Source Ownership

기존 고정 checkout을 재사용한다. 구현 승인 뒤 수정 전에 accepted patch를 binary diff와 untracked2개 원문을 포함해 복원 가능한 최소 patch bundle로 보존하고 검증한다. 전체 source archive는 만들지 않는다. accepted 두 binary는 유지하고 새 target 디렉터리에서 build한다. 새 dependency·lock 변경·source upgrade는 이 묶음에 없다.

| 책임 | 허용 수정 후보 |
| --- | --- |
| 명시적 offline/live mode와 bootstrap | codex-rs/app-server/src/lib.rs, src/bin/prepared_tool_plan_fixture.rs 또는 별도 live entry, Cargo.toml의 bin 등록, message_processor.rs, request_processors/turn_processor.rs |
| prepared snapshot/consume/dispatch | core/src/session/prepared.rs, session.rs, turn.rs, turn_context.rs, tools/router.rs, registry.rs, spec_plan.rs와 직접 대응 tests |
| ordinary auth 연결·HTTP guard | core/src/client.rs, http-client/src/transport.rs 및 request.rs의 필요한 좁은 hook, codex-api/src/endpoint/session.rs의 필요 연결과 대응 tests |
| 읽기 전용 native auth | login/src/auth/manager.rs, storage.rs 및 대응 tests; 일반 mode 기본 동작 보존 |
| protocol | 기존 experimental prepared manifest의 mode/transport/auth-generation/policy identity 결속과 대응 schema; stable surface 변화 없음 |
| network routing | 기존 network-proxy/config 기능의 사용·설정/연결과 직접 대응 tests. 새로운 proxy/credential broker 구현, TLS interception, network-proxy 자체 의미 변경은 제외 |
| 실행 통제 | task-owned launch/controller, Seatbelt profile, synthetic canaries, case catalog, redacted evidence |

R0 뒤 추가 확인한 수정 후보는 app-server/src/config_manager.rs, core/src/config/mod.rs, core/src/turn_metadata.rs, core/src/context/environment_context.rs, cloud-config/src/lib.rs 및 service.rs, http-client/src/client.rs, backend-client/src/client.rs와 직접 대응 tests다. 이는 원 제안보다 넓어진8개 명시적 module 경로이며, Owner가 이 보정 실행안에 동의할 때만 구현 범위가 된다. 목적은 runtime/auth root 분리, policy loader의 단회·무cache 동작, 자동 context 수집 차단 및 control request guard 연결이다. 해당 코드의 일반 동작을 재설계하는 권한은 아니다.

위 표의 같은 계약 module 선언과 test 연결은 포함한다. auth/config/http routing의 광범위한 재설계가 필요하면 L0에서 중단한다. Core라는 명칭이 쓰인 Codex crate 수정과 외부 host의 authority Core 변경을 혼동하지 않는다. 후자는 제외다.

## Runtime And Authority Contract

### Bootstrap And Native Authentication

- 명시적인 live entry만 실제 인증에 접근할 수 있다. offline entry는 현재 network/auth 금지 의미를 유지한다. 일반 CLI의 기본 경로를 live qualification으로 바꾸지 않는다.
- task runtime/config/instruction/rollout root와 기존 auth 저장소 위치를 분리한다. HOME/CODEX_HOME이나 전역 설정을 바꾸지 않고 native AuthConfig/AuthManager에 필요한 기존 저장소 참조만 전달한다. Driver가 token을 추출·복사하거나 env/stdin/파일/로그로 전달하지 않는다. 실제 저장 방식은 사전 metadata 판별 때 확인하며 미확인이면 중단한다.
- API/provider/workload-identity/custom route/proxy override는 이름과 존재 여부만 검사한다. 계정 선택에 영향을 주는 override가 있으면 제거하거나 다른 계정으로 대체하지 않고 중단한다. ChatGPT auth mode·기대 workspace 일치 여부·auth generation만 기록하며 email/account ID/token/header 값은 기록하지 않는다.
- 읽기 전용 정책은 native 저장소의 save/delete 및 자동 refresh를 막는다. auth 조회가 refresh를 요구하거나401/403·만료·account mismatch·Keychain 접근 불가면 중단한다. 잘못된 auth를 logout하여 원 저장소를 바꾸는 경로도 금지한다. 자동 refresh를 허용하려면 별도 명시적 변경안이 필요하다.
- local login/storage/workspace requirements를 auth load 전에 적용하고 적용 가능한 cloud policy도 성공적으로 로드·검증한다. fixture의 ignore_managed_requirements/ignore_login_requirements나 fallback defaults를 가져오지 않는다. required policy를 좁은 접근 범위에서 읽을 수 없으면 중단한다.
- model metadata는 고정 모델의 실제 광고/접근 정보를 확인한다. proof-model catalog로 접근 가능하다고 대체하지 않는다. gpt-6-astra/xhigh가 없거나 다른 model/provider로 정규화되면 중단한다.
- startup 허용 부작용은 명시된 auth/policy metadata 읽기와 local proxy 인프라뿐이다. model generation·worker/hook/MCP/plugin/extension 실행은 prepare/consume 전0이다. policy/model metadata GET은 별도 control request로 세며 generation0과 network0을 혼동하지 않는다.

### Prepared Plan And Last Send Boundary

- mode, source patch/build identity, model/effort/catalog identity, config/instruction/policy digest, local auth generation, transport profile, complete tool envelope와 handler binding을 prepare에 결속한다. consume/매 step 직전에 drift를 검사한다. unsupported tools는 관측 가능한 empty 또는 unavailable이어야 한다.
- live 첫 범위는 HTTPS Responses HTTP, compression=None, WebSocket/fallback 비활성이다. 이 선택은 명시적 한정이며 일반 auth·header·compression 전체 동등성을 주장하지 않는다. 응답이 다른 encoding/transport를 요구하면 전환하지 않는다.
- ordinary native auth/provider 구성으로 request를 만든 뒤 최종 encoder/metadata 변환이 끝난 bytes를 검사한다. header 값은 저장하지 않는다. guard가 확인한 동일 immutable bytes/destination을 send에 전달하며, guard 후 재직렬화·다른 URL·redirect로 바뀔 수 없게 한다. lower transport hook이 필요한 이유를 code/test로 확인한다.
- tool registry와 실제 body의 tools/AdditionalTools를 같은 승인 envelope에 대조한다. model과 reasoning, synthetic initial input, instruction 및 output history도 확인한다. 실제 경로·host instruction·user data가 자동 주입되면 송신 전에 거절한다. clock-only 모델 입력에는 실제 cwd/사용자 경로가 필요하지 않다.
- 공개/합성 prompt와 clock 결과만 provider에 보낸다. actual final body의 비밀·식별정보 검사와 최소 허용 field 검사를 통과하기 전에는 wire body를 evidence에 저장하지 않는다. sanitized copy만으로 실제 송신 bytes 검사 통과를 대신하지 않는다.
- 허용 tool은 clock.curr_time 하나, arguments는 empty object, turn당 dispatch 최대1회다. 두 sampling requests는 각각 guard한다. native networking/auth recovery/transport/SSE retry까지 모두 상한에 포함하며 hidden retry, automatic fallback, auto compaction, background sampling을 막는다.

### Network And Process Isolation

runtime은 최소 filesystem/exec Seatbelt 경계 안에서 동작한다. 기존 network proxy를 별도 task-owned helper로 사용해 HTTPS CONNECT destination allowlist를 적용하고 runtime의 직접 egress는 OS 경계에서 거절하는 구성을 우선한다. helper는 TLS를 해독하거나 credential을 보관하지 않는다. 임의 localhost listener나 새 proxy framework를 만들지 않는다.

L0에서 해당 pinned source의 existing proxy와 HTTP factory 연결, exact loopback endpoint, DNS/IPv4/IPv6, proxy 자체의 destination filtering, runtime의 direct-IP/alternate-proxy 우회 거절이 구현 가능한지 확인한다. exact allowlist는 고정 source가 사용하는 first-party endpoint와 적용 policy로만 산출한다. wildcard, arbitrary redirect, insecure TLS, unrestricted network 권한은 허용하지 않는다. 기존 HTTP routing과 충돌하거나 이 경계를 못 만들면 credential/model 접근 전에 unavailable로 중단한다.

provider HTTPS가 허용된 runtime을 network-deny worker라고 부르지 않는다. clock에는 child executor가 없으며 child tool0을 유지한다. canary용 child 실행은 격리 검사 process에서만 허용하고 model process에는 shell 실행 권한을 주지 않는다. H03의 실제 worker filesystem/network 강제와 H04/H05 authority는 후속 검증이다.

## R0 Correction Contract V2

아래는 M-01–M-13을 실행 가능한 gate와 검사로 구체화한 Driver 보정이다. 구현이나 실행 검증 완료를 뜻하지 않는다. 원칙을 적은 앞 절과 함께 적용하며, 수치/경로/처분의 상세는 이 절을 따른다. R0 검토 입력은 private r0-request.md 그대로 보존했다.

### Native Authentication And Root Separation — M-01, M-03, M-04

AuthManager 생성 시 불변 ReadOnlyFailClosed 정책을 고정한다. live 호출부 한 곳에서 refresh error만 돌려주는 구현은 금지한다. proactive refresh가 필요하면 auth()가 Some(stale)을 반환할 수 없고 typed admission/turn failure로 끝나야 한다. auth_cached 우회, auth_with_http_client_factory, agent_identity_auth, prewarm, unauthorized recovery, store save/delete/logout를 포함해 stale/unknown auth가 send에 도달하지 못하는지 L0에서 call-site 표로 확정한다. refresh/write/delete/recovery 시도는 비민감 위반 counter로 남기고 요청 전 거절한다. external/workload/API auth는 거절한다. token/JWT/만료 판단은 candidate 내부만 하며 Driver가 decode하거나 digest를 남기지 않는다.

현재 public source에서 AuthConfig.codex_home을 별도 전달할 수 있고, DirectKeyring 저장소는 canonical codex_home 경로의 SHA 기반 key로 조회한다. 따라서 auth 참조는 원래 auth home을 유지하고 runtime Config의 home/output root만 task root로 분리한다. 기존 저장소를 새 root로 복사하거나 다른 key로 조회하는 방식은 사용하지 않는다. 다른 keyring backend와 모든 runtime write 위치를 확인한 것은 아니며 L0 필수 항목이다.

L0에서 rollout/log/state DB/history/model cache/cloud policy cache/lock/shell snapshot/installation metadata의 read/write root를 표로 고정한다. 실제 CODEX_HOME 전체는 OS write-deny다. file auth는 정확한 auth 파일만 read-allow하며, native 정책·설정 입력은 별도의 확인된 read allowlist로 구분한다. Keychain은 필요한 최소 mach service만 허용하고 과도한 security service wildcard는 허용하지 않는다. Keychain UI prompt가 발생하면 1회 허용/항상 허용을 선택하지 않고 거부·종료하여 unavailable로 기록한다. ACL 변경이나 재로그인은 범위 밖이다.

전후 증거는 file auth의 존재/size/mtime/inode 또는 keyring의 지원되는 비민감 metadata만 사용한다. token 내용/digest는 기록하지 않는다. 다른 CLI/앱의 동시 refresh 부재를 추정하지 않는다. 외부 변경이 관측되거나 저장소 변경의 귀속을 구분할 수 없으면 해당 live 결과를 불확정으로 중단한다. 다른 앱을 자동 종료하지 않는다. OS write-deny·native write-attempt counter·auth generation은 서로 다른 근거로 보고한다.

### Live Loader Field Disposition — M-02

| LoaderOverrides field | Live 처분 |
| --- | --- |
| packaged_defaults_path | 현재 고정 build의 native packaged/embedded 기본 의미 유지; fixture empty 파일로 대체 금지 |
| user_config_path, user_config_profile | 원래 user 선택·auth storage metadata 읽기 경로를 명시적으로 유지; runtime home 이동으로 빈 user 설정을 로드하지 않음 |
| managed_config_path, system_config_path, system_requirements_path | native 위치/기본값; task root나 빈 파일로 정책 우회 금지 |
| managed_preferences_base64, macos_managed_config_requirements_base64 | native MDM 입력 유지; Some(empty) 금지 |
| ignore_managed_requirements, ignore_login_requirements | false |
| ignore_user_config, ignore_project_config, ignore_user_and_project_exec_policy_rules | false; 입력 read 경계를 못 만족하면 중단. 프로젝트 cwd는 실제 대상이 아닌 task synthetic root |

| 선택 설정 | Live 처분 |
| --- | --- |
| cli_auth_credentials_store | 원래 effective 선택과 강제 정책 일치 여부 확인; file/ephemeral로 바꾸지 않음 |
| features, plugins/MCP/extension, analytics/web | strict mode에서 비필수 실행을 hard-disable. managed requirement가 활성화를 요구하면 override로 덮지 않고 중단 |
| model_catalog_json / model | proof-model fixture 사용 금지; 고정 모델의 검증된 native metadata만 사용 |
| model_instructions_file / user instructions | task-owned synthetic prompt만 모델 입력에 사용; 실제 사용자 instruction 수집·주입은 별도 code guard로 차단 |
| project_doc_max_bytes | 제한만으로 정책 로드를 건너뛰지 않음; AGENTS/context 주입과 mandatory policy 읽기를 분리 |
| experimental_thread_store / logs / cache | task memory/root에 한정; 기존 사용자 state에 쓰지 않음 |
| approval_policy / sandbox_mode | 관리 제한과 충돌 없는 좁은 profile만 허용; 불가하면 중단 |

synthetic loader tests는 각 neutralizing field가 live 생성자에서 설정되지 않는지와 강제 requirements/MDM/exec policy가 실제로 적용되거나 거절되는지를 함께 확인한다. defaults fallback은 failure다.

### Immutable Mode And Reachable Outbound Inventory — M-06, M-09

process 시작 시 Ordinary/OfflineFixture/Live 세 mode 중 하나를 1회 고정한다. boolean enabled를 켰다 껐다 하여 mock/ordinary 경로를 선택하지 않는다. rg에서 확인한 기존 enabled call site는 아래 묶음으로 처분하고, L0에서 정확한 파일/line 전체와 새로운 indirect call site를 붙여 누락0을 확인한다. 아래는 조사 출발점이지 완료된 whole-program 증명이 아니다.

| 기존 분기 위치 | OfflineFixture | Live | Ordinary |
| --- | --- | --- | --- |
| app-server lib bootstrap/loader/cloud loader | 기존 fixture 유지 | 위 live loader와 read-only policy bootstrap | 기존 동작 |
| message_processor setup/refresh/cost worker/admission | 기존 mock·strict guard | strict admission, background refresh/cost worker off, 명시적 control 조회만 | 기존 동작 |
| client transport/prewarm/stream | memory transport, 실제 egress 없음 | guarded native HTTP만; mock·WS·startup generation 없음 | 기존 동작 |
| session startup/skills/context/worker | 기존 fixture 제한 | host skills/hooks/MCP/plugins/child 불가, strict context | 기존 동작 |
| turn compaction/pending-input/error | 기존 strict 계약 | compaction/background/추가입력 불가, 오류 전달 유지 | 기존 동작 |
| tools spec/router/registry | clock envelope·dispatch | 같은 envelope·handler 결속 | 기존 동작 |

L0 outbound inventory는 live entry→initialize→thread/start→prepare→consume/종료에서 도달 가능한 아래 producer를 포함한다. 각 항목을 hard-disabled 또는 required-guarded로 정하고 실제 constructor/call site를 기록한다. 범위 밖 sender를 발견하면 source 범위와 권한을 자동 확대하지 않는다.

| Producer | Live 처분 / 증거 |
| --- | --- |
| Responses generation, SSE reconnect | 최종 bytes guard·durable send reservation 필수; reconnect/retry0 |
| model discovery/required policy | explicit one-shot control guard·별도 예산; background poll0 |
| auth refresh/login/device code/external/agent identity provisioning | native entry부터 거절; send0 |
| WebSocket connect/prewarm/fallback | handshake 생성 전에 hard-deny; negative 검사 |
| telemetry/analytics/feedback/usage·cost polling/remote control | 생성·전송 경로 hard-disable; config false만으로 증명하지 않음 |
| MCP/plugin/extension/skills/child/subagent/web/tool_search/compaction | 등록/admission 차단과 outbound/exec negative |
| reqwest direct/route-aware/other HttpClient factory consumers | 같은 control/generation guard 경유 또는 생성 거절; unknown sender0 |

proxy는 CONNECT destination과 tunnel 수만 증명한다. HTTP send 수·retry0·background0은 process 내 sender inventory와 guard 장부의 증거이며 keep-alive tunnel 수로 대체하지 않는다. runtime의 resolver 접근도 처분하고 가능하면 DNS lookup 권한을 거절한다. helper DNS는 별도 허용 범위이며 DNS0을 주장하지 않는다.

### Exact Send Sequence, Metadata And Retry — M-05, M-07, M-08, M-10, M-11

live transport 생성자는 필수 guard를 받아야 하며 미설치이면 생성 실패다. 일반 mode의 기존 동작은 별도 test로 유지한다. HttpTransport 이외의 control client에도 final request에 적용되는 guard를 연결한다. prepared HTTP 처리 순서는 다음으로 고정한다.

1. 모든 encoder/metadata/auth 변환 완료 후 prepare_body_for_send 결과를 확정한다.
2. method·URL·prepared.headers의 이름과 필요한 값·prepared.body의 실제 bytes를 검사한다. live는 ClientRedirectPolicy::Reject를 무조건 적용한다.
3. 통과한 동일 immutable request에 대해 mutex 아래 durable counter를 예약하고 fsync한다. 실패하면 send0이다.
4. 같은 Bytes를 body_mut으로 이동하여 송신한다. guard 후 재직렬화·URL 재계산·route fallback·body 변경은 금지한다. counter 초과는 failure이며 partial success가 아니다.

compression 결정 지점은 live에서 None을 반환한다. Content-Encoding 또는 비UTF-8/non-JSON generation body를 guard에서 거절한다. header 이름은 허용 목록만 통과하고 turn/workspace metadata 값도 메모리에서 내용 검사한다. credential-bearing header는 native auth provenance·종류·destination만 검사하며 값 복사/출력을 하지 않는다. 공개 endpoint 인증에 필요한 native header와 임의 metadata를 같은 것으로 취급하지 않는다.

| 자동 주입 원천 | 처분 |
| --- | --- |
| environment_context cwd/filesystem/home/shell | model 입력용으로 실제 경로를 생략하거나 고정 synthetic label 사용. 실제 cwd/policy 경로는 로컬 manifest에서 유지하며 거짓 실행 권한으로 치환하지 않음 |
| 사용자/전역/프로젝트 instructions | task synthetic instruction만 주입; mandatory 정책 읽기는 위 loader로 유지 |
| turn/workspace/git metadata header/body | local identity만 사용하거나 생략; remote URL/실제 path/account 설명 등 유출 여부를 final guard에서 검사 |
| git/shell snapshot/login shell/env/subprocess 수집 | mode guard를 수집 호출 전에 적용. 실패를 조용히 무시하는 것을 부재 증거로 쓰지 않음; model process exec-deny |
| request/response logging | credential/header 원문0. SSE/응답 body도 privacy allowlist 검사 후 최소 결과만 저장; response headers 저장0 |

runtime/task cwd를 사용자명이 없는 다른 root로 옮기는 Reviewer 예시는 채택하지 않는다. 승인된 durable root를 유지하고 model-visible context만 생략/synthetic 대체한다. 실제 cwd를 옮길 필요가 생기면 별도 판단한다. clock 결과는 UTC 형식으로 고정한다.

| Retry 계층 | Live 값과 gate |
| --- | --- |
| proactive auth refresh / unauthorized recovery | 불가; stale auth를 반환하거나 reload 후 재송신하지 않음 |
| cloud policy service | max attempts1, auth recovery0, background refresh0, cache write0 |
| codex-api provider retry policy / lower HTTP client | max attempts1 또는 retries0; underlying direct/route-aware fallback0 |
| core stream retry / SSE disconnect | retries0; 중도 disconnect 뒤 재연결0; send reservation은 소모 유지 |
| WebSocket→HTTP / transport fallback | handshake와 fallback0 |
| compaction/background sampler | 생성0 |

token refresh/login/device-code host/path는 allowlist에서 제외한다. generation/control과 host가 같으면 CONNECT proxy로 path를 구분할 수 없다고 기록하고, 동일 host 내부의 auth path는 request guard/native auth code가 차단하는 경계임을 명시한다. proxy를 path-level 방어로 주장하지 않는다.

### Policy Admission And Candidate Requalification — M-12, M-13

순서는 local policy 판별 → read-only native auth/known account classification → 필요할 때만 guarded cloud-policy 조회·validation → effective config/model metadata 고정 → prepare/consume다. cloud-config/service.rs에서 확인한 native 기준은 Codex backend의 known business-like/education-like/Enterprise다. known 비대상 class는 not-applicable로 구분하고, unknown class/identity는 not-applicable로 바꾸지 않고 unavailable로 끝낸다.

대상 class의 backend 응답은 성공적으로 decode/validate한 empty bundle이면 applicable-empty, nonempty bundle이면 applied다. 401/403/404/5xx/timeout/parse error/unknown status는 미적용으로 처리하지 않고 failure다. 기존 service의 최대5회 retry와 background refresh를 live에서는1회/0으로 제한한다. 기존 without_cache one-shot seam을 우선 사용하고 read/write cache를 모두 끈다. required runtime cache가 남는다면 task root에만 귀속하며 원 CODEX_HOME write-deny는 유지한다. control endpoint/method/purpose를 고정한 뒤 기존4/start·8/전체 예산 안에서만 수행한다.

두 번째 live 실행은 최초 승인 범위 안의 mandatory 보정에만 사용한다. 보정 원인/영향/새 source·binary·profile identity를 먼저 기록하고 영향 L2 negative와 관련 OS canary가 다시 PASS한 뒤 새 manifest에 결속한다. 1차와2차 결과를 합쳐 한 candidate의 성공으로 표시하지 않는다. credential/route/policy 범위 변경, unknown sender 또는 권한 확대가 필요하면 잔여 turn이 있어도 자동 진행하지 않는다.

### Required L2 Negatives And L0 Go Or No-Go

필수 L2 묶음은 (1) near-expiry/stale/refresh-error/401와 저장소 write/delete/logout 차단, (2) local/MDM/required policy 보존과 cloud empty/applied/unknown/error/cache/retry, (3) 삼중 mode 및 off/on network 구분, (4) guard 미설치·guard 후 body/URL 변경·redirect·alternate route·same-host auth path·counter/fsync failure, (5) HTTP/SSE/WS/compaction retry0, (6) 실제 path/git/instruction/header/SSE 식별정보 거절, (7) final envelope·중복/미등록 dispatch, (8) direct-IP/IPv6/alternate proxy/file/exec OS canary다. 기존 fixture8은 공통 경로 영향 때문에 한 번 실행하고 변경되지 않은 evidence만 재사용한다.

L0 최대60분의 go 조건은 위 mode/sender/context/write-root/loader/retry 표가 exact source call site와 필요한 수정 경로로 닫히고, auth/root/proxy 경계를 허용 범위로 구현할 수 있다는 정적 설계 근거가 갖춰지는 것이다. L0 통과를 실행 보안 검증으로 부르지 않는다. 범위·권한·unknown sender가 남거나60분이 지나면 no-go/unavailable이며 L1/실제 auth로 넘어가지 않는다. 실행 검증은 L2, actual account/route 적격성은 L3가 소유한다. 필수 gate가 늘어났다는 이유만으로 중단 상한을 늘리거나 full test를 추가하지 않는다.

### Driver Dispositions

| Finding | 처분 | 반영 및 남은 경계 |
| --- | --- | --- |
| M-01 | accept | immutable fail-closed auth policy, stale 반환 금지와 전체 auth entry negative; 구현 검증 전 |
| M-02 | accept | LoaderOverrides 전 field 및 raw 선택값 처분표; native 정책 유지 |
| M-03 | accept | 실제 keyring key 입력 확인, auth/runtime root 분리·OS write-deny·동시 변경 귀속 규칙 |
| M-04 | accept | Keychain prompt 기본 거부·unavailable, 1회/항상 허용 없음 |
| M-05 | accept | required final guard, unconditional Reject, fsync 후 same Bytes 송신 |
| M-06 | accept | reachable sender inventory와 hard-disable/guard 처분, proxy/HTTP 증거 분리 |
| M-07 | accept | auth endpoint 제외, same-host path 제한의 실제 계층 명시 |
| M-08 | revise | 승인된 root 유지, model context/header 원천 차단; context/metadata8개 확장 후보에 포함 |
| M-09 | accept | immutable 3-mode와 기존 분기 그룹별 처분; L0 exact call-site 전수 확인 |
| M-10 | accept | live compression None 코드 결정·header/body negative |
| M-11 | accept | 계층별 retries0/max attempts1, 초과 failure, SSE 재연결 금지 |
| M-12 | accept | 최초 승인에 conditional 2차 후보 포함, identity·영향 L2/canary 재PASS·증거 분리 |
| M-13 | accept | native eligibility 기준 확인, unknown/오류 fail, cloud service 단회·no-cache 및 추가 source 경로 명시 |
| O-01 | accept | tracked21+untracked2 구성, source diff와 executable digest를 아래 구분 |
| O-02 | accept | 실제 Owner R0 승인·호출·판정 기록 및 current status 갱신 |
| O-03 | accept | L0 산출물·60분 no-go 유지. 예상4–6시간은 낮은 신뢰 판단, gate 통과 시 실측 재산정 |
| O-04 | accept | clock UTC 출력 |
| O-05 | revise | 다른 앱 quiescence를 추정하거나 자동 종료하지 않음; auth drift 귀속 불명은 해당 run 중단 |
| O-06 | accept | response header 원문0, SSE도 privacy gate 후 최소 저장 |
| O-07 | accept | runtime DNS와 proxy DNS 경계 구분·L0/negative 포함 |
| O-08 | accept | 공식 문서는 Driver 확인이며 Reviewer 미확인 |

현재 accepted candidate는 tracked21+untracked2=23파일이다. full tracked binary diff SHA는 0f8bd8c87b73c564132c06edcdd5870decd3a951b6f1af3ffe3b671c02f4e00d이며 fixture executable SHA df5e7ab4b63fdfe8aa2b45eba8ad8fd7d956ebe228469d37a9fbe6d2d16973a6와 다른 객체다. untracked2개 digest와 excerpt identity는 private metadata에 보존했다. 실행 승인 뒤 만들 최소 recovery bundle은 아직 없으므로 bundle digest를 만들어내지 않는다.

필수13건의 계획 처분은 위와 같이 완료했지만 구현/재현 closure는 아직 없다. Reviewer verdict는 REVISE 그대로 보존하고, v2가 Reviewer에게 재검토되었다거나 실현성이 이미 확인됐다고 표현하지 않는다.

## Stages And Evidence Selection

| 단계 | 수행·산출 | 통과/중단 조건 |
| --- | --- | --- |
| L0, 최대60분 | 현재 source/accepted patch/binary·범위 확인, native read-only auth/policy와 existing proxy 설계 대조, synthetic preflight | 필요한 source·권한·endpoint·계정 경로를 한정하지 못하면 중단; 실제 credential 접근/model0 |
| L1 | mode·auth/transport/dispatch guards 구현, fixed argv/profile/case catalog 확정, 필요한 focused tests·Clippy·candidate build | 최초 재build 적격 판별은 build 시작 후90분 이내; old binary와 source 복구 입력 보존 |
| L2 | fake auth store로 read-only 보장, unknown policy/identity·401·redirect·hidden retry·final bytes drift·unregistered/duplicate dispatch, OS canaries, 영향받는 기존8 cases | 모든 필수 negative와 canary PASS 전 실제 인증/모델0 |
| L3 | bounded actual auth/policy/model metadata admission 후 live clock turn1개 | auth mismatch/required refresh/unexpected egress/body/receipt/limit 불명 즉시 중단; 실패 자동 재호출 없음 |
| L4 | 성공 결과의 source/build/request/dispatch 결속 정리, R1과 필요한 범위 내 보정, 종료/보존/정리 | mandatory finding0이어도 Owner 수락은 별도; 미확인은 unavailable |

fixture 8 cases는 bootstrap·공통 prepared/client branch 변화로 영향받으므로 새 candidate에서 한 번 검사한다. 첫 proof의 unchanged registry collision/protocol malformed/schema 검증은 해당 코드가 바뀌지 않은 경우 재사용하며, 변경되면 영향 검사만 추가한다. stable protocol generator는 protocol/schema 변경 때만 실행한다. 동일 오류 없는 green 검사를 단순 digest 변경 때문에 반복하지 않는다. full Codex workspace와 기존 host normal/O 회귀는 이 clock-only 단계에 필요하지 않으며, 후속 host 통합 때 원래 의무를 유지한다.

## Proposed Attempt And Time Limits

- 예상 활동240–360분(4–6시간), 별도 누적 중단480분(8시간). 판단값이며 완료 약속이 아니다. accepted proof157.52분 실측은 구현·보정·검토까지의 참고값이고, 새 auth/policy/proxy 연결 비용의 측정값이 아니다. 삭제한 build cache 때문에 재compile45–75분을 계획에 포함한다.
- 예상 구성: 초기 경계 판별30–45, 구현75–105, rebuild/집중 검증75–105, 실제 admission/clock10–25, R1/정리30–50분으로 약220–330분; 간접 준비·기록 변동을 포함해240–360분으로 보고한다. 각 항목 합은 중복 없는 순차 계획이며 실제 병행 wall time은 한 번만 센다.
- 설치/재build/검사·service/reviewer 대기·기록/종료를 포함한다. Owner 전용 대기는 제외하고 마지막15분은 종료·보존에 남긴다. 최초 L0 또는 build 판별 실패 때 남은 시간을 쓰려고 범위를 늘리지 않는다.
- 수정 보정 최대2묶음. 초기 candidate offline App Server starts 최대12, 각 보정 영향 재검사 최대8씩, offline 총28 starts/56 fixture threads/56 simulated turns. 한 묶음은 원인·수정·영향 case를 실행 전에 묶어 기록하며 임의 실패를 사후 합치지 않는다.
- live App Server 최대2 starts/2 threads, 대응 proxy helper 최대2 starts. 기본 live turn1개, 필수 보정 후 재적격 확인이 필요한 경우에만 추가1개: 총2 turns, turn당15분·generation HTTP send 최대2, 총4 sends. 실제 HTTP send 직전에 durable counter를 예약한다. failed send도 차감하며 자동 retry는0이다. model이 tool을 호출하지 않으면 부분/미충족으로 종료하고 성공을 얻으려 재질문하지 않는다.
- control-plane policy/model metadata 요청은 live start당 총4 sends 이하, 전체8 이하; exact method/endpoint/purpose를 첫 credential 접근 전에 고정한다. auth refresh/relogin requests0. 필요한 control flow가 상한을 넘으면 unavailable로 중단한다. metadata 요청 실패를 generation 예산으로 대체하지 않는다.
- R1 최대2회, 각각15분 이내·fresh Claude·tools/MCP/실행0. 첫 검토와 mandatory 보정 후 필요한 재검토만 포함한다. 이전 proof R1 2/2와 별개 신규 제안이다. R0는 실행 승인 전에 별도1회다.
- 기존 U2 사용163.03분과 accepted proof157.52분은 각 장부 그대로 보존한다. 남은 proof 한도를 live 실행에 전용하거나 기존 보정/R1 수를 되돌리지 않는다. 이번 계획 준비 시간은 아래 별도 checkpoint이며 proposed480분은 실행 승인 전에는 시작되지 않는다.

## Execution Decision After R0

R0는 Owner 승인 후1회 완료했다. REVISE 판정과 필수13건은 아래 원문·처분에 남겼다. Driver가 보정한 v2는 재검토받지 않았으므로 Reviewer PASS 또는 Reviewer 지적 해소 확인으로 표현하지 않는다. 추가 R0 호출을 자동으로 열지 않는다.

지금 제안하는 승인 묶음은 이 v2의 추가8개 module 후보, L0 최대60분의 feasibility 판별, 조건 충족 시 구현·격리 build/tests·read-only actual auth admission·clock live 최대2턴·보정2묶음·R1최대2회·종료/정리까지다. 예상4–6시간, 누적480분 상한과 마지막15분 종료 여유를 유지한다. L0에서 범위 밖 수정이나 더 넓은 권한이 필요하면 그 영향 실행은 시작하지 않고 중단한다. 이 조기 중단은 필수 항목 면제가 아니다.

일반 단계 전환과 같은 scope의 mandatory 보정 후 재검증에는 승인을 반복하지 않는다. 두 번째 live 후보도 아래 새 identity·negative/canary 재적격 조건을 모두 만족해야 하며, 최초 실행 승인에 포함하는 제안이다. Core/H05·실제 프로젝트·CLI 교체·제품 Git·결과 수락은 제외한다. Keychain prompt는 허용하지 않고 unavailable로 끝내는 기본안을 요청한다.

간단 승인 문구: “보정 v2 실행 묶음 승인 — L0 최대60분, 전체 최대8시간, Keychain prompt는 거부·중단.” 이 문구는 새 계정 로그인/토큰 갱신/인증 저장소 변경이나 예산 확대를 허용하지 않는다.

## Recovery, Retention And Adoption

실패 시 candidate와 proxy를 멈추고 task-owned process tree/열린 파일·필수 evidence를 확인한다. 원 CLI와 auth 저장소는 바꾸지 않는 설계이므로 변경한 사용자 설정을 복원하는 작업은 없다. 검증 불가능한 descendant나 auth write가 있으면 미확인/실패로 보존한다. consumed handle 재사용·network failure replay·다른 model/provider 전환은 금지다.

현재 accepted source와 두 binary·required evidence는 다음 실행안 검토의 입력으로 유지한다. 실행 시 accepted patch recovery bundle과 새 candidate는 결과 수락/정확한 source 반영 또는 후속 포기 때 재평가한다. cache는 concrete correction/review consumer가 끝나면 standing cleanup 기준으로 정리한다. Worktree/branch/Git publication과 adopter 적용은 별도다. 지금은 문서·review 입력만 만들며 신규 runtime task ID와 STATUS를 만들지 않는다.

## Local Inputs And Planning Checkpoint

Source checkout: private-evidence/E159 [공개용 중립화]
Existing host record: FEAT-20261021-002-u2-single-host-source.md
Accepted proof record: FEAT-20261021-003-prepared-tool-plan-proof.md
Private packet/evidence root: private-evidence/E158 [공개용 중립화]
Proposed future build/runtime root: private-evidence/E157 [공개용 중립화]

이 source-only 문서가 새 계획과 preliminary R0의 단일 진행 소유자다. accepted proof 기록에는 이 후속 pointer만 추가하고 완료 상태를 바꾸지 않는다. 실행 승인 뒤 새 기록을 만들 경우 이 계획의 exact identity와 검토를 연결하고 진행 소유자는 한 곳으로 정한다.

## R0 Review Record — 2026-10-22

Owner가 계획 작성 후 제시한 R0 요청에 “승인”으로 답했다. fresh Claude CLI1회, 기존 claude.ai/firstParty/pro, tools/MCP/commands0, 고정 비식별 입력만 전달했다. 실제 model은 claude-opus-5-5, session은4f75934d-b7ad-4995-923a-948a151c2874이다. 243.26초, exit0, tool use0, process group 부재, 입력 drift0을 확인했다. 판정 REVISE, 필수13건·선택8건이다. Reviewer는 실행 재현이나 외부 문서 조회를 하지 않았으며 이 결과는 구현 승인/결과 수락이 아니다. 아래 원문과 Driver 처분은 구분한다.

### Reviewer Response Verbatim

````text
# R0 정적 검토 결과 — Prepared Tool Plan Live Qualification 실행안

## 0. 판정 요약

- **권고: REVISE (보정 후 재제출)**
- 필수 보정 13건, 권고 8건입니다.
- 계획의 방향은 타당합니다. clock-only 범위, fail-closed 원칙, claim 한정, 예산 장부 분리가 그 근거입니다.
- 다만 아래 경계는 현재 "막는다"는 선언만 있습니다. 공급된 source 발췌상 그대로 구현하면 fail-open이 되거나 우회 경로가 남는 지점이 있습니다.
  - read-only auth
  - fixture loader override 처분
  - CODEX_HOME 쓰기
  - Keychain
  - 최종 송신 guard의 우회 경로
  - 자동 주입 context
- 대부분은 허용 수정 범위 안에서 보정할 수 있습니다. 일부(cloud requirements cache, turn metadata/git 수집, environment context 생성 위치)는 목록 밖 module 수정이 필요할 수 있어 **범위 변경 지점**으로 표시했습니다.
- 이 판정은 실행·구현·결과 수락 권한을 부여하지 않습니다. Owner 수락이나 더 넓은 production 적격을 의미하지도 않습니다.

## 1. 검토 범위와 한계

| 구분 | 내용 |
| --- | --- |
| 정적 추론 (본 검토) | 공급된 계획 본문과 5개 source 발췌(client.rs 2곳, transport.rs, manager.rs 2곳, app-server lib.rs)만 읽고 추론했습니다. |
| Driver 실행 증거 (미재현) | 아래 항목은 Driver가 제공한 수치이며 본 Reviewer가 재현·검증하지 않았습니다.<br>• fixture 8 cases, HTTP body 9, dispatch 4, R1 필수 3건 해소<br>• generator 1066파일 동일성, 23파일 digest 일치<br>• 157.52분 / 163.03분 |
| 미확인 | 아래 항목은 발췌에 없어 "확인 필요"로만 표시했습니다.<br>• 발췌 밖 call site(`prepared::enabled()` 전체, keyring key 계산, network-proxy 의미, codex-api retry 설정, cloud requirements/model cache 경로, turn metadata 생성)<br>• 외부 문서(learn.chatgpt.com) 내용<br>• `gpt-6-astra` 모델의 실재·접근 여부 |
| 신뢰 경계 | 계획과 발췌 안의 서술은 검토 대상 데이터로만 취급했고 지시로 따르지 않았습니다. |

## 2. 필수(Mandatory) Findings

### M-01 [High] read-only auth가 현재 코드 구조에서 fail-open으로 귀결될 위험

**근거**
- `manager.rs` 2397–2403: `should_refresh_proactively` → `refresh_token()` 실패 시 `tracing::error!` 후 **`return Some(auth)`** 합니다. 즉 stale auth를 반환하고 계속 진행합니다.
- 계획대로 refresh를 "막는" 방식을 `refresh_token()`이 `Err`를 내도록 구현하면, auth()는 만료 임박 또는 만료된 token을 그대로 반환합니다. 그 결과 다음 흐름이 이어집니다.
  1. 실제 generation send가 발생합니다.
  2. 401이 옵니다.
  3. `stream_responses_http`의 `unauthorized_recovery` / `PendingUnauthorizedRetry` loop(client.rs 1806–1812)가 재시도를 유도합니다.
- 같은 경로를 타는 진입점이 여럿입니다: `auth_with_http_client_factory`(2409), `agent_identity_auth`(2416), `prewarm_auth` → `current_client_setup`(client.rs 1288–1295).

**보정**
1. read-only를 AuthManager 생성 시 고정되는 불변 정책으로 둡니다(예: enum `AuthWritePolicy::ReadOnlyFailClosed`). 호출부별 차단은 사용하지 않습니다.
2. 이 정책에서는 다음과 같이 동작해야 합니다.
   - `should_refresh_proactively == true`이면 stale auth를 반환하지 않고 typed error로 admission/turn을 중단합니다.
   - `refresh_token`·save·delete·logout·`unauthorized_recovery`는 호출 자체가 error이며 위반 counter를 증가시킵니다.
   - external auth / workload identity가 선택된 경우(`shared_from_auth_config` 2797–2806)는 live entry에서 거절합니다.
3. "refresh 필요 여부" 판정은 candidate process 내부에서만 합니다. Driver가 JWT/만료 시각을 디코드하거나 기록하지 않음을 명시합니다.
4. L2 negative를 추가합니다.
   - (a) fake store의 near-expiry token → generation send 0, refresh request 0, store 무변경
   - (b) fake 401 → send 1회만 차감, reload/refresh 0, 즉시 중단
   - (c) refresh 실패를 주입해도 `Some(stale)` 경로에 도달하지 않음

### M-02 [High] fixture loader override 전체에 대한 live 처분이 정의되지 않음

**근거**
계획은 `ignore_managed_requirements` / `ignore_login_requirements`만 "복사하지 않는다"고 적었습니다. 그러나 `lib.rs` 459–510에는 정책을 무력화하는 항목이 더 있습니다.
- `managed_preferences_base64: Some(String::new())`, `macos_managed_config_requirements_base64: Some(String::new())`: macOS MDM 관리 설정과 requirements를 빈 값으로 대체합니다.
- `managed_config_path` / `system_requirements_path` / `system_config_path`: task root로 재지정되어 실제 시스템/관리 경로를 우회합니다.
- `ignore_user_config`, `ignore_project_config`, `ignore_user_and_project_exec_policy_rules`
- raw override: `cli_auth_credentials_store="file"`, 모든 feature false, `model_catalog_json`, `model_instructions_file`, in-memory thread store, `approval_policy`, `sandbox_mode`

**보정**
1. live loader에 대해 **field별 처분표**를 실행안에 넣습니다.
   - 정책을 담는 항목(system/managed/MDM/requirements/login)은 native 기본 경로와 기본값을 사용합니다.
   - 빈 값이나 task root로 대체하는 것은 금지합니다.
2. `cli_auth_credentials_store`는 override하지 않습니다. 사전 판별 결과와 requirements 강제값이 다르면 중단합니다.
3. 사용자 선택에 해당하는 항목(feature, analytics, instructions, thread store)은 별도 표로 둡니다. 정책이 강제하는 값과 충돌하면 override하지 않고 중단합니다.
4. L2에서 구조 test를 둡니다: live entry가 위 neutralizing field를 설정하지 않음. 가능하면 합성 requirements를 주입했을 때 live loader가 이를 적용하는지 unit test로 확인합니다.

### M-03 [High] "CODEX_HOME 불변"과 "runtime root 분리"의 동시 실현성이 미검증

**근거**
- 계획은 HOME/CODEX_HOME을 바꾸지 않고 runtime/config/rollout root만 분리한다고 했습니다.
- 그러나 ordinary runtime은 codex_home 기준으로 다음 항목을 쓸 가능성이 큽니다(정적 추론, 발췌 밖): session/rollout, log, state DB, models cache, cloud requirements cache, history.
- keyring 저장소의 service/account key가 codex_home 경로에서 파생된다면, runtime codex_home을 분리하는 순간 기존 credential을 찾지 못합니다(확인 필요).

**보정**
1. L0 gate로 확인합니다.
   - (a) `AuthConfig`가 runtime codex_home과 독립된 auth 저장소 참조를 받을 수 있는지
   - (b) keyring key 계산 입력이 무엇인지
   - (c) runtime이 쓰는 모든 파일 경로가 task root로 귀속되는지
2. **OS 이중 경계**를 둡니다. runtime Seatbelt에서 실제 CODEX_HOME 전체를 write-deny하고, auth 파일 1개만 read-allow합니다(file 저장 방식일 때).
3. 사후 확인 규칙을 둡니다.
   - auth 저장소의 비민감 metadata(존재, size, mtime, inode)를 실행 전후로 비교합니다. token 내용 digest는 기록하지 않습니다.
   - L3 동안 ordinary CLI 동시 사용 금지 또는 drift 귀속 규칙을 명시합니다.
4. 별도 수정 없이 분리가 안 되면 L0에서 unavailable로 처리합니다. `storage.rs` 밖 config 경로 수정이 필요하면 범위 변경 지점입니다.

### M-04 [High] Keychain 저장 시 승인 prompt가 원 저장소 변경을 유발할 수 있음

**근거 (정적 추론)**
- 새로 build한 candidate binary는 기존 Keychain item을 만든 binary와 code signature가 다릅니다. 따라서 접근 시 macOS 승인 prompt가 뜰 수 있습니다.
- "항상 허용"을 선택하면 item ACL이 수정됩니다. 이는 auth 저장소 쓰기에 해당합니다.
- 계획은 "Keychain 접근 불가 → 중단"만 정의했고, prompt라는 중간 상태를 정의하지 않았습니다.
- Seatbelt profile에는 securityd 계열 mach-lookup 허용이 필요할 수 있습니다.

**보정**
1. 저장 방식이 keyring으로 판별되면 이 위험을 Owner 승인 패킷에 별도 항목으로 표시합니다.
2. "항상 허용" 금지를 명시합니다.
3. "1회 허용"을 허용할지는 Owner가 사전에 결정하여 실행안에 고정합니다. 기본값은 prompt 발생 시 거부·중단·unavailable입니다.
4. Seatbelt의 Keychain 관련 허용 항목을 최소 목록으로 확정합니다.

### M-05 [High] 최종 송신 guard의 위치·필수성·redirect 정책이 불완전

**근거**
- `transport.rs` 76–93: 최종 bytes는 `prepared.body`이고 header는 `prepared.headers`입니다. `Request.headers`와 `compression`은 버려집니다.
- guard는 `prepare_body_for_send` 직후, `RequestDraft` 구성 전에 다음 값을 대상으로 해야 합니다: method, url, `prepared.headers` 이름, `prepared.body` bytes.
- `RouteAware` backend는 "every request and redirect URL"마다 route를 재해석합니다(68–73).
- `build_api_transport`는 `ACCOUNT_ROUTING_HEADER`가 있을 때만 `Reject`이고, 그 외에는 전달받은 redirect 정책을 그대로 씁니다(client.rs 1269–1276).
- `http-client`는 범용 crate입니다. hook이 "설치되지 않으면 통과"하는 구조라면 live mode에서 미설치 시 fail-open이 됩니다.

**보정**
1. live mode에서는 `ClientRedirectPolicy::Reject`를 무조건 강제합니다.
2. live transport 생성자가 guard callback을 필수 인자로 받게 합니다. 미설치이면 생성 실패로 fail-closed합니다. ordinary mode는 no-op이며 동작이 변하지 않음을 test로 고정합니다.
3. 송신 순서를 고정합니다: guard 판정 → durable counter 예약(fsync) → 같은 `Bytes` 객체를 `body_mut`에 이동 → send.
   - 그 사이에 재직렬화나 URL 재계산이 없음을 test로 확인합니다.
   - test 예: guard 후 body를 바꾸려는 주입, redirect 응답, 다른 host URL
4. Routed pool에서 proxy 실패 시 direct나 다른 route로 fallback하는지 L0에서 확인합니다. fallback이 있으면 live에서 차단합니다.

### M-06 [High] guard를 경유하지 않는 송신 경로와 proxy 증거의 한계가 정리되지 않음

**근거**
- proxy allowlist는 CONNECT destination(host:port) 수준입니다. 같은 first-party host로 가는 다른 요청을 구분하지 못합니다. 예: analytics/telemetry, rate-limit/account 조회, remote model, WebSocket prewarm(client.rs 1297–1300 주석), background 요청.
- keep-alive 때문에 CONNECT 수와 HTTP request 수가 일치하지 않습니다.
- 따라서 "hidden retry 0 / background 0"은 proxy 증거로는 증명되지 않습니다. **process 내 guard와 완전한 sender inventory**로만 주장할 수 있습니다.

**보정**
1. L0 산출물에 고정 source의 모든 outbound HTTP/WS 생성 지점 목록을 넣습니다(ReqwestTransport 미경유 client 포함).
2. 각 지점을 처분합니다: live mode에서 hard-disable(config가 아닌 mode 분기)하거나, guard 경유를 강제합니다.
3. WebSocket은 handshake 경로까지 live mode에서 코드 수준으로 차단하고 negative test를 둡니다.
4. 결과 claim에 증거 성격을 구분해 명시합니다: proxy 증거는 "tunnel destination 집합과 tunnel 수"이고, request 수와 retry 0은 "in-process guard 장부"입니다.

### M-07 [Medium] allowlist에 auth token/login endpoint 제외가 명시되지 않음

**근거**
"exact allowlist는 고정 source가 사용하는 first-party endpoint"로 산출한다고 했습니다. source는 refresh/login host도 사용하므로, 이 기준만으로는 refresh 경로가 network에서 허용될 수 있습니다.

**보정**
- token refresh/login/device-code 계열 host와 path는 allowlist에서 명시적으로 제외합니다. 이 계층이 M-01의 network 차원 이중 차단 역할을 합니다.
- 제외 대상이 generation/metadata host와 같아서 분리가 불가능하면 그 사실을 기록하고, M-01 코드 차단만이 유일한 차단 계층임을 claim에 표시합니다.

### M-08 [High] 자동 주입 context 때문에 송신 전 거절이 구조적으로 확정될 수 있음

**근거 (정적 추론)**
- ordinary turn은 다음과 같은 정보를 자동으로 붙일 수 있습니다.
  - environment context(cwd, shell, sandbox/network 상태)
  - user/global instructions(AGENTS.md 등 CODEX_HOME 기반)
  - turn metadata header(`responses_metadata.has_turn_metadata`, client.rs 1762)
  - 이를 위한 git 등 subprocess 수집
- 계획은 실제 경로가 주입되면 "송신 전 거절"한다고 했습니다. 따라서 설계 없이 진행하면 결과가 확정적으로 unavailable이 됩니다.
- 현재 작업 경로처럼 사용자명이 포함된 경로가 cwd이면 바로 식별정보가 됩니다.
- guard는 body만 검사하고 header는 "값 미저장"으로만 정의되어 있어 header를 통한 유출을 검사하지 않습니다.

**보정**
1. 주입 원천을 L0에서 목록화합니다. 각 원천을 synthetic 대체, 비활성, 또는 그대로 두되 guard 검사 대상으로 처분합니다.
   - 예: 사용자명이 없는 task-owned synthetic cwd
   - instructions root는 task root로 지정합니다.
2. guard는 header **이름 allowlist**를 적용하고, 식별 가능성이 있는 header 값(turn metadata 등)도 **내용 검사**합니다. 값 자체는 저장하지 않습니다.
3. subprocess 생성 지점(git, login shell/snapshot 등)을 목록화합니다. runtime Seatbelt exec-deny 상태에서 실패가 조용히 생략되는지, 오류로 중단되는지 확인합니다.
4. 이 처분에 `turn_context.rs`/`session.rs` 밖 module(turn metadata, environment context 생성부) 수정이 필요하면 **범위 변경 지점**으로 표시하고 Owner 결정을 받습니다.

### M-09 [Medium] `prepared::enabled()`의 전역 분기를 tri-state mode로 바꿀 때 call site 전수가 없음

**근거**
client.rs에서만 세 곳이 조기 반환합니다: 1265(build_api_transport Err), 1289(prewarm_auth Ok 생략), 1778(mock stream). live에서 이 flag를 켜면 mock으로 가고, 끄면 ordinary 전체 경로(feature, WS, compression, retry)가 열립니다.

**보정**
- process 시작 시 1회 고정되는 `Mode {Ordinary, OfflineFixture, Live}`를 둡니다.
- 모든 `prepared::enabled()` call site에 대한 처분표를 만들고, 다음을 test로 고정합니다.
  - live는 mock에 도달하지 않음
  - offline은 network에 도달하지 않음
  - ordinary는 기존과 동일
- mode가 실행 중에 변경되지 않음을 보장합니다.

### M-10 [Medium] compression=None과 WS 비활성의 구현 수단이 미정

**근거**
client.rs 1737–1745: ChatGPT auth는 `uses_codex_backend` 조건을 만족하므로 `enable_request_compression`이 켜져 있으면 Zstd가 선택됩니다. 계획은 None을 선언만 했습니다.

**보정**
- live mode에서 compression 결정 지점이 None을 반환하도록 강제합니다.
- guard는 다음을 거절합니다: `Content-Encoding` header가 있음, body가 UTF-8 JSON으로 parse되지 않음.
- 이 선택이 ordinary 요청과의 차이(비압축)라는 점은 이미 claim에 한정되어 있으므로 유지합니다.

### M-11 [Medium] retry 계층별 설정값과 분류 규칙이 미정

**근거**
retry 원천이 여러 층입니다: auth recovery loop(client.rs 1806–1812), codex-api request/stream 재시도(발췌 밖, 확인 필요), WS→HTTP fallback, auto compaction. 계획은 "모두 상한에 포함"이라고만 했습니다.

**보정**
1. 각 계층의 live 설정값(0 또는 비활성)과 설정 위치를 표로 둡니다.
2. guard counter 초과는 **실패**로 분류하고 "부분"으로 분류하지 않음을 명시합니다.
   - clock turn은 정상 경로에서 이미 sampling 2회를 사용합니다. 따라서 retry가 1회라도 일어나면 상한을 넘습니다.
3. SSE 중도 끊김 재연결도 send로 차감함을 test합니다.

### M-12 [Medium] 보정 후 두 번째 live turn의 승인·재적격 조건이 없음

**근거**
"필수 보정 후 재적격 확인이 필요한 경우에만 추가 1 turn"이라고 했습니다. 보정은 새 build, 즉 새 candidate identity를 뜻합니다. 그러나 다음이 정의되어 있지 않습니다.
- L2 negative/canary를 다시 실행해야 하는지
- Owner의 최초 승인이 이 재실행을 포함하는지

**보정**
- 두 번째 live start 전에 다음을 필수로 둡니다.
  - (a) 보정 묶음 기록
  - (b) 영향받는 L2 negative 재PASS
  - (c) 새 candidate identity를 prepare에 결속
- 최초 승인 범위에 포함할지, 별도 Owner 확인을 요구할지 실행안에 명시합니다.
- 1차 turn 결과와 2차 turn 결과를 별도 candidate의 증거로 분리 기록합니다.

### M-13 [Medium] cloud policy의 "적용 가능" 판정과 순서·부작용이 미정

**근거 (정적 추론)**
- cloud requirements 조회에는 auth가 필요하므로 auth load 이후에 일어납니다. 이 조회도 auth()를 거칠 수 있어 M-01 경로에 노출됩니다.
- 이 조회는 control-plane send이므로 guard와 counter 대상입니다.
- cache 파일이 CODEX_HOME에 쓰일 수 있습니다(M-03).
- "적용 가능한 cloud policy"를 판정하는 기준이 없습니다. 따라서 "미적용"과 "조회 실패"가 구분되지 않습니다.

**보정**
- 적용 여부 판정 규칙을 명시합니다: 계정 유형과 응답 상태별로 미적용 / 적용 / 실패를 구분하고, 실패는 중단합니다.
- 해당 요청의 method·endpoint·purpose를 control 예산 4/8 안에 사전 고정합니다.
- cache 쓰기 경로를 task root로 귀속하거나 비활성화합니다. 어느 쪽도 안 되면 범위 변경 지점으로 표시합니다.

## 3. 권고(Optional) Findings

| ID | 내용 | 보정 제안 |
| --- | --- | --- |
| O-01 | 공급된 "Current binary diff SHA-256 0f8bd8…"과 계획의 fixture binary SHA "df5e7a…"는 다른 객체입니다. 계획에 accepted **patch diff digest**가 없어 서로 대조할 수 없습니다. 23파일에 untracked 2개가 포함되는지도 불명확합니다. | accepted diff digest, 파일 수 구성(tracked/untracked), bundle digest를 계획에 명기합니다. |
| O-02 | Status 줄은 "R0 … not yet authorized"인데 본문은 R0 1회가 요청 가능하다고 합니다. | R0 승인 근거(일시, 범위)를 기록해 모순을 해소합니다. 본 Reviewer는 승인 여부를 추정하지 않습니다. |
| O-03 | L0 60분은 M-03/05/06/08/09/13의 inventory 범위를 고려하면 빠듯합니다. 총 240–360분 추정도 낙관적일 수 있습니다. 산술 자체는 일치합니다(30–45+75–105+75–105+10–25+30–50=220–330). | L0 산출물을 go/no-go 체크리스트로 고정합니다. 시간 초과 시 연장하지 않고 unavailable로 처리하는 규칙을 유지·강조합니다. |
| O-04 | clock 결과가 local time이면 timezone이 식별 단서가 될 수 있습니다. | UTC 고정 형식을 사용하거나 offset 포함 여부를 사전에 결정합니다. |
| O-05 | ordinary CLI를 동시에 사용하면 정상적인 refresh로 auth generation drift가 생겨 중단될 수 있습니다. | L3 동안 ordinary CLI 사용 자제를 Owner 안내 항목에 추가합니다. |
| O-06 | 응답 header(rate-limit, plan 정보 등)와 SSE에도 계정 관련 정보가 있을 수 있습니다. | response header는 저장하지 않습니다. SSE는 body와 동일하게 검사를 통과한 뒤에만 저장합니다. |
| O-07 | runtime의 DNS 조회(mDNSResponder 경유)는 egress 경계 밖 신호입니다. | runtime은 proxy CONNECT hostname만 사용하게 하고, 가능하면 DNS mach-lookup을 차단하는지 확인합니다. |
| O-08 | 외부 문서 링크 내용은 본 Reviewer가 확인하지 않았습니다. | "Driver 확인, Reviewer 미확인"으로 표기합니다. |

## 4. 열린 Feasibility Gate 점검

| Gate | 계획 반영 | R0 판단 |
| --- | --- | --- |
| read-only native auth | 선언만 있음 | 현 코드는 fail-open 구조 → **M-01 필수** |
| mandatory policy 보존 | ignore 2개만 언급 | MDM/경로 재지정 누락 → **M-02, M-13** |
| auth 저장소 분리 / 쓰기 금지 | 선언만 있음 | 실현성 미확인, OS 이중 경계 없음 → **M-03, M-04** |
| helper / direct-egress | L0 확인 항목 있음 | 방향은 타당. 증거 한계와 token host 제외 필요 → **M-06, M-07** |
| final body guard 위치 | transport 언급 있음 | 필수 설치, Reject 강제, 우회 sender 정리 필요 → **M-05, M-06** |
| retry/turn accounting | 상한 정의됨 | 계층별 설정과 2차 turn 조건 필요 → **M-11, M-12** |
| context / 식별정보 | 송신 전 거절만 정의 | 설계 없으면 확정 unavailable → **M-08** |
| claim 한계 | 대체로 양호 | proxy 증거와 guard 증거의 성격 구분 추가 → M-06 |
| 시간 산정 | 산술 일치 | 낙관적 가능성 → O-03 |

## 5. 최종 권고

**REVISE.**

M-01~M-13을 반영한 보정 실행안을 한 묶음으로 재제출할 것을 권고합니다. 각 항목에는 field/call-site 처분표, L0 gate 체크리스트, 추가할 L2 negative 목록을 포함하면 됩니다.

다음 경우는 Owner 결정 대상이며, 해당 시 판정은 BLOCKED로 전환될 수 있습니다.
- M-03, M-08, M-13 처분에 허용 수정 목록 밖 module이 필요한 경우
- M-04에서 Keychain prompt 처리를 확정할 수 없는 경우

이 판정은 구현, auth 접근, network, live 실행을 승인하지 않습니다. Owner 수락이나 장기 운용·production 적격을 의미하지도 않습니다.
````


## Execution Ownership — 2026-10-22

Owner가 보정 v2 실행 묶음을 승인했다. 이 문서는 승인 전 계획/R0 역사로 보존하며, 이후 진행은 [FEAT-20261022-001](FEAT-20261022-001-prepared-tool-plan-live-qualification.md)이 단독 소유한다. 승인 시점 exact bytes는 private 실행 입력에 보존했다.
