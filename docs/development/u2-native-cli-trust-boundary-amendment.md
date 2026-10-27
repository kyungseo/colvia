# U2 Native CLI Trust Boundary Amendment

Status: Driver-revised after one Opus 5.5 R0 (REVISE: three blocking and seven nonblocking findings), 2026-10-26; awaiting Owner execution decision. These revised bytes were not re-reviewed. Progress owner: [FEAT-20261022-001](FEAT-20261022-001-prepared-tool-plan-live-qualification.md). This amendment is not activated. The approved [tool-neutral execution plan](u2-tool-neutral-execution-plan.md) remains at Hold until a new exact execution decision.

## Purpose And Authority

Colvia는 업무 승인과 실제 변경을 통제하고, 공식 Claude CLI의 내부 모델 통신·로그인 관리는 해당 실행기에 맡기는 경계를 제안한다. Core와 U1 수락은 그대로 유지한다. Codex 실험 경로에서 추가로 입증한 transport 보장을 모든 도구의 공통 요구로 확대하지 않는다.

Owner는 이 조정안 작성과 Opus 5.5 정적 R0 1회 및 최대 160 KiB의 비민감 조항·합성 근거 packet 전송만 승인했다. 이번 승인으로 구현, Sonnet worker 실행, OAuth 관리 동작 허용 또는 기존 Hold 해제가 이루어지지는 않는다. 이 문서는 U2 실행안의 명시적 변경 제안이며 Core/DR-0005의 authority 계약을 개정하거나 기존 runtime을 지원으로 승격하지 않는다.

문제의 근거는 A의 실제 CLI help 확인과 공식 공개 인터페이스 조사다. 공개 hook/CLI 표면에서 최종 HTTP body/headers 결속과 송신 전 fsync gate, native subscription credential write의 사전 veto를 확인하지 못했다. 이는 그런 제어가 절대 불가능하다는 증명이나 Sonnet 실행 실패가 아니다. 실제 worker 호출은 0회이며 A는 Hold다.

## Named Clause Changes

아래 표는 기존 실행안의 변경 조항을 특정한다. 표시하지 않은 Core/권한/효과/worker·복구·결과 품질 조건은 보존한다. 모든 완화는 Claude native-CLI profile에 한정하며, 기존 Codex exact candidate의 조건과 과거 PASS 의미는 변경하지 않는다. 향후 다른 도구에도 같은 profile을 적용하려면 별도 qualification이 필요하다.

| 기존 실행안 조항 | Claude native-CLI profile의 제안 변경 | 없어지는 보장과 남는 책임 |
| --- | --- | --- |
| Required Common Guarantees 3, Guarantee Mapping의 final sender/fsync 및 retry 행 | Host는 CLI에 제공한 고정 입력·model·tool schema와 반환 결과를 기록한다. 내부 HTTP 생성·재시도·TLS/fallback 정책은 native CLI의 신뢰 범위다 | 최종 HTTP bytes/headers의 Host 결속, 모든 송신 전 fsync 예약, 내부 retry/redirect/fallback 0을 보장하지 않는다. Host tool 효과 전 durable 예약은 계속 필수 |
| Required Common Guarantees 4, Guarantee Mapping의 auth/policy/catalog 행 | 기존 계정·firstParty subscription을 유지한 native OAuth 갱신·저장 및 native policy/catalog 취득을 허용하는 신뢰 범위를 제안한다 | credential store write 0, 정책 단회/무cache 및 catalog 전체 불변을 보장하지 않는다. OAuth refresh 실패에 따른 저장 credential 삭제와 로그인 상태 변경도 native trust의 잔여 위험이다. 계정/provider/billing 경로 변경, Host의 raw credential 취득·복사·기록은 금지 |
| Exact Runtime Setup의 외부 송신·control endpoint hard cap, Cumulative Budget의 model sends/control requests/generation | Host가 실제 강제할 starts·입력 step·tool 요청·wall time으로 상한을 정하고 native 사용량은 관측 가능한 범위에서만 별도 보고한다 | 내부 model/control 송신의 정확한 횟수·24/32 hard cap, generation 2/turn 보장을 주장하지 않는다. 내부 unknown을 0이나 추정 횟수로 표시하지 않음 |
| First Three Hours의 Go 근거 | 이번 profile에서 유지되는 공통 effect/authority 보장의 구조적 근거와 실제 최소 loop/거절/중단/fresh 재개를 요구한다 | 완화한 transport 조건의 부재를 결함 은폐 없이 지원 설명에 명시. simple success만으로 Go 또는 전체 qualification 통과 불가 |

다음 종속 조항도 각각 명시적으로 바꾼다. 앞 표의 철회 항목을 원문의 보존 문장으로 다시 요구하거나, 아래 표 밖의 Host 효과 조건을 묵시적으로 완화하지 않는다.

| 기존 실행안의 종속 조항 | Claude profile에 적용할 정확한 대체 |
| --- | --- |
| Required Common Guarantees 서두의 강화 조건 보존 및 2의 native identity·세대 고정/외부 연결 금지 | Host 입력/schema는 고정한다. native identity·세대·history는 init inventory, CLI metadata와 Host step/call mapping으로 관측하고 dispatch 직전에 검증한다. native 내부 송신 전 결속·세대 불변은 요구하지 않는다. 필요한 firstParty model/OAuth/service-policy 통신은 native trust이며 승인되지 않은 Host tool/외부 효과는 계속 사전 차단한다 |
| Guarantee Mapping 도입부 및 후문: 탐지 후 중단 금지, 모든 조건에 구조적 사전 gate 요구, 미지원 No-Go | Host 효과·authority에는 원문을 그대로 적용한다. native model 변경, service-policy/catalog, telemetry 설정 준수, 표준 cache/credential 운영에 한해서 신뢰한 CLI의 설정·metadata를 근거로 쓰고 이상 관측 후 중단을 허용한다. 내부 미관측 자체는 Hold 사유가 아니며 unknown으로 기록한다. managed hook/MCP 효과는 이 예외에 포함하지 않는다 |
| Mapping의 prepared inventory/native thread·turn·call/history/input 행 | init inventory 확인, bridge dispatch 직전 요청 검증, native call ID와 Host step의 대응으로 대체한다. 모델 본문 자기보고는 인정하지 않는다. 최초 model 통신 이후 inventory가 제공된다면 live start/Host step을 소비하되 첫 tool 효과 전 검증을 완료한다 |
| Mapping의 dispatch 1/turn·native call identity·결과 행 | Claude에는 Host step당 effect slot 최대 1을 적용한다. 내부 agentic turn 수와 구별하며 dispatch 전 예약·변조/재호출 거절은 유지한다 |
| Exact Runtime Setup의 model/control 외 송신 0, start당 control 4, 설정만으로 차단 입증 불가 | strict packet-level 0 및 control 사전 hard cap 보장은 철회한다. updater/telemetry/오류 보고를 끄는 고정 설정은 계속 요구하고 신뢰한 CLI의 준수를 전제로 한다. 비허용 설정·연결이 관측되면 Hold한다. 허용한 model/OAuth/service-policy 내부 횟수가 unknown이라는 이유만으로 Hold하지 않는다 |
| Exact Runtime Setup의 예기치 않은 home 기록 Hold·인증 갱신 필요 Hold | 표준 native cache/credential metadata와 OAuth 관리에 한해 허용한다. native transcript 재개, 실제 업무 데이터 기록, 새 login·계정/API 경로는 계속 제외한다. login expired/credential 소실은 Hold하며 자동 재로그인하지 않는다 |
| Exact Runtime Setup의 모든 필드 사전 확정과 native model/policy drift | 실행 입력·argv·요청 model/effort·binary는 사전 고정한다. 실제 model/inventory metadata는 첫 효과 전 확인한다. service-policy/catalog 불변은 철회하되 managed 정책 부재 조건은 아래와 같다. effort는 medium 요청값을 고정하며 effective 값 미노출은 unknown으로 허용하고 다른 값이 관측되면 Hold한다 |
| First Three Hours의 30–75분 송신 gate 미지원 No-Go, 75–145분의 turn/send 계수, Go 설명 | native trust 항목의 final sender gate 부재로 No-Go를 내리지 않는다. 유지한 효과·권한 조건의 구조적 집행과 최소 실제 loop/거절/Host stop/fresh 재개를 요구한다. 아래 잔여 일정과 Host 계수를 적용한다 |
| Cumulative Budget의 Claude turns/sends/control/offline 행 및 내부 송신 사전 제한 불가 Hold | 아래 Claude Host 계수와 non-model 검사 분류로 대체한다. 내부 sends/control/generation의 정확한 hard cap을 주장하지 않는다. Codex 계수와 offline fake fixture의 model/auth/network 0은 그대로다 |
| Remaining Implementation B–D 및 Completion의 두 도구 공통 계약/transport 검증·완료 표기 | Core/효과/복구의 공통 기준은 보존한다. Claude 내부 transport/credential 동등성은 완료 기준에서 제외하고 지원 한계로 표시한다. Codex exact candidate의 강화 transport 조건, 원 H01–H10의 나머지 증거/품질/Owner 수락 조건은 그대로 남는다 |

native CLI를 신뢰한다는 것은 model 출력이나 tool 요청을 신뢰한다는 뜻이 아니다. Model이 승인 문구·actor·경로·ticket을 만들어도 권한이 생기지 않는다. 실제 효과는 Host가 가진 고정 mapping과 기존 Core/worker 경계를 통과해야 한다. Native runtime의 악의적 구현·공급망 침해·OS 계정 전체 침해를 방어한다는 주장은 이 profile에 없다. CLI의 표준 설정/cache/session 운영과 기존 계정 OAuth 관리는 신뢰 범위로 구분하고 실제 업무 파일·authority 변경과 섞지 않는다.

## Common Effect And Authority Contract

1. Colvia가 exact intent/Work/grant/ticket/result와 actor/home/action/scope를 소유한다. adapter가 제공한 native ID는 진단·중복 검사용이며 Core authority가 아니다. result 수락은 기존 human/명시적 ordinary delegation 규칙에 따른다.
2. 모델에서 온 모든 tool 요청은 Host가 작성한 얇은 bridge relay로 들어온다. CLI가 stdio MCP relay를 띄워도 실제 authority 판단·journal·slot·fsync·worker 생성은 별도 Host controller가 소유한다. relay는 Core authority handle·journal 쓰기 권한을 갖지 않으며 고정 task-local IPC로 요청/결과만 전달한다. 이 IPC는 새 network proxy/SDK가 아니고, 연결용 run nonce도 업무 권한이 아니다. Host는 relay 입력도 model 입력처럼 검증한다. 임의 file path, shell argv, actor나 target을 model이 선택하지 못하게 고정 file ID/schema/handle을 검증한다. 다른 scope·stale·revoke·중복·결과 변조는 효과 전에 거절한다.
3. 허용 효과를 실행하기 전에 Host가 request ID·입력 hash·사용 slot·전후 상태를 durable journal에 예약하고 fsync한다. 예약 실패·상한 초과·unknown이면 worker를 실행하지 않는다. 이 journal은 HTTP sender journal이 아니다.
4. 실제 파일 읽기/쓰기/verifier는 기존 격리 worker만 수행한다. Native shell/file/browser/subagent tool은 노출하지 않는다. Native CLI에 control/실제 adopter checkout을 cwd나 추가 directory로 넘기지 않고 task-owned bridge cwd와 선별한 합성 입력을 사용한다. worker의 control/runtime/Git/policy/credential·alias/network 차단 조건은 그대로다.
5. CLI tool 권한 설정은 보조 제어이며 Host 검증을 대신하지 않는다. managed hook/외부 MCP 등 우회 효과 경로의 시작 전 배제 근거가 없으면 native 시작 전에 Hold한다. 시작 후 얻는 실제 tool inventory가 고정 allowlist와 다르면 첫 업무 효과 전에 Hold한다. 사용자/조직 정책을 지우거나 우회해 진행하지 않는다.
6. Host stop/revoke/상한은 새 요청과 효과를 즉시 차단한다. CLI를 별도 process group으로 시작하고 CLI·bridge relay·Host가 띄운 worker의 모든 소유 group/descendant를 추적한다. TERM 10초 → KILL 10초 뒤 전체 group/tree의 부재를 확인한다. 직접 child만 사라진 것은 충분하지 않다. 불명확한 descendant가 있으면 미확인으로 Hold한다. provider에 이미 도달한 요청·요금이 되돌아갔다고 주장하지 않는다. pending/journal/누적 사용량을 보존하고 자동 replay하지 않는다.
7. 재개는 native transcript가 아니라 Core의 승인·선별 입력·이전 결과/검증·pending·누적 사용량으로 fresh session을 만든다. 실행 ID는 새로 생겨도 Work와 소비한 slot은 유지한다. missing/drift·sealed 뒤 변경은 거절한다.
8. H10 원 5문서의 품질·누락·불필요 수정과 Owner 부담/수락은 그대로 남는다. 모델 변경·리뷰 verdict·기술적 accept가 이를 대체하지 않는다.

## Fixed Runtime Profile

작업 model은 `claude-sonnet-5-5`, Reviewer는 `claude-opus-5-5`다. 호출별 `--model`을 지정하고 전역 기본값은 바꾸지 않는다. CLI는 기존 계획에 고정한 2.1.310 및 같은 binary digest를 사용한다. SDK 설치·CLI update·새 proxy·TLS 가로채기·endpoint/base URL·API key·계정 변경·다른 runtime fork는 제외한다. CLI가 model을 바꾸었다면 관측 즉시 새 tool 효과를 차단하고 Hold한다. Native가 바꾼 model의 최초 송신까지 사전 차단했다고 주장하지 않는다.

다음 필드를 실제 시작 전에 고정한다. 값이 확정되지 않거나 조합이 지원되지 않으면 실행하지 않는다.

- binary path/digest, 전체 argv, model/effort, cwd, environment allowlist, 출력/temporary 경로, 명령별 timeout. Sonnet effort는 `--effort medium`으로 요청한다. actual effective effort를 CLI가 보고하면 일치를 확인하고, 미노출이면 요청값만 확인됨/effective unknown으로 남긴다. 요청값 준수를 native trust로 수용하는 변경이며 actual model identity 미확인까지 허용하는 것은 아니다. 이번 draft에서 설정을 적용하지 않는다.
- 별도 native tools는 제거하고 strict MCP로 Host bridge 하나만 허용한다. A의 bridge는 `u2_read_file`과 `u2_verify`만 제공하며 schema/native 표시명을 고정한다. `u2_write_file/u2_accept`는 A inventory에서 제외한다. 이후 C에 필요하면 기존 합성 범위의 exact mapping을 먼저 고정하고, accept는 기존 human/명시적 ordinary delegation 규칙에만 연결한다. 실제 adopter authority handle은 넣지 않는다.
- native 권한은 `dontAsk`와 명시 allowlist를 사용한다. CLI의 `--safe-mode`, explicit MCP 설정, permission 옵션의 조합이 고정 bridge를 실제로 제공하면서 다른 경로를 배제하는지 init inventory로 확인한다. 조합이 불가능하면 즉흥 mode 변경 없이 Hold한다. `--safe-mode`가 managed 정책까지 모두 지운다고 가정하지 않는다.
- 사용자/project 설정·memory·skill/plugin/output style·hook·ambient MCP를 배제할 옵션과 effective configuration을 확인한다. 이 profile은 admin-managed 정책이 없는 환경에만 적용한다. native 시작 전에 문서화된 managed 설정 source의 존재 여부, 조직/계정의 관리 여부에 대한 비밀 없는 기존 provenance로 부재를 확인한다. 계정이 Pro라는 사실만으로 부재를 추정하지 않는다. 원격 관리 여부나 적용 source를 확인할 수 없으면 init/model을 시작하지 않고 Hold한다. 필요한 경우 알려진 설정 source의 존재와 hook/MCP/tool 관련 제한된 키만 읽고 계정 email·credential·무관한 설정 전체는 수집하지 않는다. 시작 뒤 effective hook/MCP/tool inventory는 추가 확인이며 시작 전 근거를 대신하지 않는다. service-policy/catalog의 native 취득 허용과 admin-managed 실행 정책 부재를 구별한다. 세션 도중 managed 정책 출현/변경이 관측되면 새 효과를 닫고 종료한다. 이 profile은 신뢰한 CLI와 관리되지 않은 환경이 유지된다는 전제에 한정되며, 동시 관리자 변경/악의적 OS 변경을 막는다고 주장하지 않는다. 사전 근거상 세션 도중 관리 정책이 자동 적용될 수 있는 환경이면 적용 대상에서 제외한다. 정책을 지우거나 우회하지 않는다.
- updater/telemetry/error reporting/불필요한 기능 연결은 공식 옵션으로 비활성화하고 effective 설정을 확인한다. 이 조건은 신뢰한 CLI의 설정 준수를 전제로 하며 모든 내부 packet에 대한 독립 OS 차단/계측 보장이 아니다. 실제 비허용 설정·연결이 드러나면 중단하고 별도로 처분한다. Native의 필요한 firstParty model/OAuth/policy 동작은 위 trust 범위이며 control 송신 수는 unknown일 수 있다.
- native session persistence는 끄고 raw debug/request-body logging은 사용하지 않는다. task-local 출력은 Sonnet이 처리할 합성 입력/반환 결과만 선별해 보존한다. 표준 CLI 운영 cache/credential metadata는 native trust 범위이며 Host가 내용을 수집하거나 대량 복사하지 않는다. 예상 밖 실제 업무 데이터 기록/전송이 드러나면 중단한다.
- native subscription 로그인 경로는 호출 전 비밀 없는 status로 확인한다. 기존 계정의 native OAuth refresh/store 관리와 refresh 실패에 따른 저장 credential 삭제/로그인 상태 변경 가능성이 이 profile의 미래 승인에 포함된다. login expired나 credential 소실이 관측되면 Hold하고 자동 재로그인하지 않으며 native trust 결과로 기록한다. 새 login/계정/구독/유료 사용량 구매/API fallback·key provisioning은 포함하지 않는다. 요금/계정 경로가 불명확하면 Hold다.

MCP bridge가 도구를 제공한다는 사실만으로 공통 계약을 충족하지 않는다. 실제 거절·effect slot·process death·Core fresh-session 복구를 아래에서 확인한다. 첫 actual model identity는 CLI가 출력하는 구조화 metadata에서 확인하고 모델 본문 자기보고는 인정하지 않는다. 이는 native runtime을 신뢰한 관측이다. 해당 metadata가 없거나 불일치하면 tool 요청을 실행하지 않고 Hold한다.

### Fixed Argv Template And Evidence Limits

다음은 실행 전 exact bytes로 봉인할 argv template이다. `PINNED_CLI`, `BRIDGE_CONFIG`, `ALLOWLIST`, `SESSION_UUID`, `SYSTEM_TEXT`는 Driver가 고정하며 model이 채우지 않는다. 아직 만들어지지 않은 bridge 경로나 schema를 확정됐다고 표시하지 않는다.

```text
PINNED_CLI --print --model claude-sonnet-5-5 --effort medium
  --safe-mode --tools "" --disable-slash-commands
  --strict-mcp-config --mcp-config BRIDGE_CONFIG --setting-sources ""
  --permission-mode dontAsk --permission-prompts none --allowedTools ALLOWLIST
  --input-format stream-json --output-format stream-json --verbose
  --no-session-persistence --no-chrome --session-id SESSION_UUID
  --system-prompt SYSTEM_TEXT --max-turns 2
```

`--tools ""`는 built-in tool 제거 수단이다. `ALLOWLIST`는 A의 두 MCP native tool 이름만 포함한다. 입력 stream은 Host가 step별로 공급하며 native resume 옵션은 쓰지 않는다. 보존된 2.1.310 help에서 print, tools, strict MCP, permissions, effort, stream-json 및 no-session-persistence 옵션을 확인했다. R0 packet의 이름이 잘린 중복 help 블록은 발췌 오류이며 frozen packet은 수정하지 않는다. `--max-turns`는 그 help에 나타나지 않아 [공식 CLI reference](https://code.claude.com/docs/en/cli-reference)의 print-mode 설명만 근거로 삼았다. 고정 binary에서의 동작과 safe-mode/explicit MCP 조합은 아직 실행 미확인이다. 미지원이면 Hold하며 옵션을 빼거나 mode를 바꾸어 재시도하지 않는다. 위 template·환경 allowlist·입력 digest와 실제 schema를 모두 고정하기 전 live start를 소비하지 않는다.

## Host Steps And Bounded Effects

용어를 분리한다. Host step은 Host가 고정 입력 하나를 native CLI에 제출하도록 허용한 단위다. native agentic turn은 CLI 내부 처리 단위이며, HTTP send와도 같지 않다. 이전 model-turn 한도와 새 Host-step 계수의 의미를 혼동하지 않는다.

Claude의 합성 loop는 step당 effect slot 1개만 열고, `--max-turns 2`를 보조 제한으로 제안한다. 동일 CLI에 추가 입력을 밀어 넣기 전에 직전 step의 결과를 확인하고 닫는다. 이 옵션은 native agentic turn의 제한이며 내부 HTTP sends 2라는 뜻이 아니다. 고정 tool 요청이 추가로 오면 Host는 effect slot을 재사용하지 않고 거절/중단한다. 정상 작업이 이 제한 안에서 완료되지 않으면 범위를 늘리거나 자동으로 slot을 추가하지 않고 실패로 보고한다.

모든 bridge 요청은 validation 전에 시도 카운터를 durable journal에 예약하고 fsync한다. 거절된 요청도 소비하며 재개 시 승계한다. 시도 예약/fsync가 실패하면 효과를 거절하고 controller의 실패 관측을 보존한 뒤 Hold한다. 성공 여부가 불명확한 예약을 없던 일로 만들거나 자동 retry하지 않는다. 허용된 요청만 effect slot을 소비하며 side effect 전 별도 durable 예약이 있어야 한다. 실제 native session/call ID와 Host step mapping이 불명확하면 unknown으로 중단한다. 동시 요청에는 원자적 slot 예약을 적용하고 pending 요청을 다음 step으로 이월하지 않는다.

## Proposed Limits And Inheritance

전체 20시간은 그대로다. 첫 준비/R0와 model 방향 보정 1,929.557초, A 판별·정리 696.062초를 이미 소비했다. 이번 조정안/R0의 실제 활동도 같은 총량에 추가한다. 마지막 30분 정리 예약을 유지하며 Owner 전용 대기는 제외한다. 과거 ledger·H10·R0 원문과 카운터를 덮어쓰지 않는다.

A의 원 180분 중 696.062초가 소비돼 10,103.938초(약 168.40분)가 남았다. 이번 조정 검토는 별도 승인된 최대 60분의 문서/리뷰 구간으로, 전체 20시간에는 포함하지만 이미 Hold한 A의 시간을 초기화하거나 새 180분을 만들지 않는다. 미래 재개가 승인되면 A 잔여 안에서 수행한다.

| 구간/계수 | 유지 또는 제안값 | 현재 사용/변경 의미 |
| --- | --- | --- |
| 이번 조정안 작성/R0 | 예상 20–40분, 최대 60분; R0 1회/160 KiB/15분, 마지막 5분 정리 | 첫 도구 중립 R0 1회와 별도 추가 승인. 아직 미래 R1 2회를 소비하지 않음 |
| Claude live starts | 전체 최대 4, A 최대 2, C 기본 2 | 현재 0. 현재 한도 안에서만 정상+fresh 재개 |
| Claude Host steps | 전체 최대 8, A 최대 4 | 현재 0. 이전 예정 Claude model-turn 8 대신 새 의미로 기록; 실제 사용 이력은 0이므로 이동할 실행 없음 |
| Claude bridge 요청/효과 | 요청 전체 8/A 4, 허용 효과 전체 8/A 4 이내, step당 효과 최대 1 | 거절도 요청 횟수 소비. A의 음성 조합은 아래 분리로 수용하며 상한 자동 전용 없음 |
| Claude native internal sends/control/turns | 가능한 reported usage만 별도 기록, 정확 수 미관측이면 unknown | 종전 sends 12/control 16/generation 2의 강제 보장을 이 profile에서 철회하는 명시적 변경. Host step과 합산하지 않음 |
| Codex의 live/transport 계수 | 기존 계획 그대로 | 현재 0. 더 강한 기존 sender/credential 조건 유지 |
| non-model native 검사 / offline fixture | 각 도구 12 starts, A Claude 최대 6 | Claude help 1회 이미 소비. auth status도 이 pool에서 1회/30초를 소비하며 native OAuth 내부 활동은 trust 범위로 unknown이다. offline fake fixture만 model/auth/network 0을 요구. native/test-spawned process도 계상 |
| 집중 검사 batch | 전체 최초 1+보정 2, batch당 30분 | 현재 0. A offline bridge 검사에서 최초 batch 1을 사용하면 B–D에는 보정 2만 남는다. 영향 없는 증거는 재사용하고 부족하면 Hold. 새 Core full/Rust build/SDK 설치 기본 0 |
| 프로세스/중단 | native process 30분, Host step 15분, 일반 host/offline case 5분; 전체/단계 잔여 우선 | TERM10초+KILL10초 종료 예약. 같은 process 다음 step도 전체 사용량 유지 |
| future R1 | 기존 최대 2회, 각 15분/160 KiB | 현재 0. 이번 추가 R0와 별도이며 외부 전송은 기존 승인된 public-safe 범위 |

auth status는 model 없는 검사로 분류하되 OAuth/네트워크가 0이라는 주장은 하지 않는다. init 관측용 native process도 먼저 start를 예약한다. 모델 입력 없이 끝나는 검사만 non-model pool을 쓰고, model 입력을 공급할 process는 처음부터 live pool을 쓴다. 첫 prompt가 있어야 inventory가 나오면 live start와 Host step을 함께 소비하며 첫 효과 전 검증한다. 고정 control/fault 입력도 Host step 및 실제 발생한 bridge 요청 카운터를 소비한다. 모델이 생성했다고 표시하지 않는다. 별도 native process를 띄우면 해당 pool도 차감한다. offline simulated turns/dispatch의 기존 전체 도구별 24/24, A Claude 12/12 한도는 유지한다.

CLI starts·Host steps·tool 시도/효과·시간은 Host가 사전에 제한한다. subscription 내부 실제 요금·API send 수의 엄밀한 상한은 이 profile의 보장이 아니다. 사용량 경고/한도나 계정 경로 변화가 관측되면 중단하고 자동 구매/API 전환하지 않는다. Sonnet 선택을 이유로 이전 시간·시도 한도를 늘리지 않는다.

## Minimum Qualification After A Resume Approval

A 잔여에서 필요한 검증만 수행한다. R0 통과나 이 draft의 수락만으로 실제 지원을 선언하지 않는다.

1. 시작 전 managed 정책 부재·고정 CLI/config/bridge·계정 경로를 확인하고, native 시작 뒤 첫 효과 전 init identity·유효 tool inventory·CLI metadata의 model identity를 확인한다. 신뢰 범위를 넘는 tool/hook·다른 모델·불명확한 계정 경로가 있으면 효과를 허용하지 않는다.
2. offline exact bridge 경로에서 actor/scope/result/duplicate·budget/fsync 실패·동시 slot·stop 이후 요청을 확인한다. 실제 worker 쓰기 전에 거절되는지 확인하며 단순 모델 출력 평가로 대체하지 않는다. 실제 native process가 필요하면 남은 offline 계수에서 차감한다.
3. A live step 4개에 최대 bridge 요청 4개를 배정한다: (a) 고정 합성 파일 read 성공 1회, (b) 잘못된 file ID/scope 요청 거절 1회, (c) fresh 재개 뒤 허용 read/verify 1회, (d) 재개 뒤 이미 소비한 request/slot 또는 revoke 상태 요청 거절 1회. negative 입력은 실행 전 고정한다. 모델이 필요한 요청을 내지 않으면 미확인으로 남긴다. 공식 control 입력 또는 task-local probe의 고정 fault injection을 쓰는 경우 실제 native 요청이 지난 동일 relay→Host 검증 경로에만 적용하고, 원 요청/변환 입력 bytes·시점을 기록한다. model이 negative를 생성했다고 주장하지 않는다. 어느 방식이든 같은 step/요청 한도를 쓰며 추가 요청이 남은 사례를 소진하면 negative 미관측으로 Hold한다. 자동 추가 step/turn은 없다.
4. 첫 process의 두 step 뒤 아직 살아 있는 CLI에 Host가 TERM을 시작하는 실제 stop을 수행한다. 새 효과를 먼저 닫고 CLI·relay·worker의 전체 group/descendant 부재를 확인한 뒤 Core 기반 fresh session 1회로 재개한다. 자연 종료만 관측했다면 실제 Host stop은 미검증이므로 Go 불가/Hold이며 추가 start로 보충하지 않는다. 승인·입력·직전 결과·pending·전체/도구별 사용량을 승계한다. 과정에 Claude U1 fresh-reader 관측을 결합하되 U1 범위와 U2 효과 관측을 따로 기록한다.
5. 위 계약의 모든 필수 항목에 enforce 근거와 실제 최소 관측이 있고 잔여 시간/시도로 B–D가 가능할 때만 Go checkpoint를 남긴다. native transport 내부 미관측은 이 profile의 명시적 한계로 보고하되 common effect 미관측을 가리지 않는다. 필수 negative·stop·fresh 재개가 미관측이거나 시간/시도가 부족하면 Hold다. 유지한 필수 효과 제어의 구조적 미지원이 확인되면 No-Go다.

A 재개 시 새 180분을 부여하지 않고 다음 잔여 배치를 사용한다. 시간은 재개 후 활동 누적 분이며 실제 완료가 빠르면 다음 구간으로 진행한다. live process 최대 30분×2와 step 최대 15분×4는 같은 60분 안에서 겹쳐 계산하고 각 종료 여유 20초도 그 안에 예약한다.

| A 재개 후 누적 활동 | 배치 |
| --- | --- |
| 0–25분 | preflight, managed 정책 부재·계정·exact argv/입력 고정 |
| 25–75분 | 작은 bridge/probe 작성과 최초 offline 집중 batch |
| 75–135분 | 최대 2 live starts/4 Host steps, 거절·실제 stop·fresh 재개 |
| 135–153.40분 | 근거 대조, Go/Hold/No-Go 및 B–D 재추정 |
| 153.40–168.40분 | 중단·전체 process 부재·보존·보고 |

판별은 정확한 A 잔여 10,103.938초에서 마지막 900초를 남긴 시점에 종료한다. 표의 소수점은 표시용 반올림이다. 예상 A 활동은 기존 1.5–2.5시간의 판단 추정을 유지하되, 옵션 조합/정책 부재/negative가 미확정이므로 신뢰도는 낮다. 168.40분은 예상이 아니라 누적 중단 한도다.

A에서는 작은 task-local probe/bridge만 작성하며 전체 Host refactor를 먼저 하지 않는다. 원문 5문서를 다시 생성하거나 전송하지 않는다. B–D 범위·예상 시간·완료 조건은 기존안에 따르되, 모델 통신을 Host가 전부 통제한다고 주장하는 부분만 이 draft의 명시적 profile로 바뀐다. 실제 feasibility가 추정을 바꾸면 재추정하며 남은 전체 한도를 늘리지 않는다.

## Support Claims And Owner Decision

| 현재/향후 profile | 말할 수 있는 범위 |
| --- | --- |
| 기존 Core/U1 | 기존 수락과 검증 범위 유지 |
| 기존 Codex 실험 adapter | 해당 exact candidate에서 관측한 강화 transport/credential 보장과 별도 원 H 한계 |
| 제안 Claude native-CLI adapter | 아직 미검증. 통과 뒤에도 Host가 강제한 업무 효과·복구와 native CLI를 신뢰한 model/auth 범위를 함께 명시 |

도구별 실행 통제 방식이 다르더라도 Core authority와 업무 효과 계약은 동일하게 유지한다. 이 draft는 Claude와 Codex가 내부 HTTP/credential까지 동등하게 격리된다는 주장을 철회하는 제안이다. 공개 지원 표기는 각 OS·CLI·model·profile·실제 evidence에 한정한다.

Opus R0 실제 판정은 REVISE(차단 3건/비차단 7건)다. 이 보정본은 Driver가 지적별 문서 처분을 반영했으며 재검토되지 않았다. 추가 R0/R1은 소비하지 않았다. exact reviewed/revised digest와 응답 원문·처분은 기존 Work에 남긴다.

다음 Owner 결정은 이 amendment의 정확한 bytes를 실행 계약으로 적용하고 원 A의 잔여부터 재개할지 여부다. 제안은 한 묶음이다: (1) 내부 HTTP/재시도/횟수와 native OAuth 갱신·저장·실패 시 credential 삭제/로그인 상태 변경을 native trust로 수용, (2) service-policy/catalog 불변 철회, admin-managed 정책 부재를 적용 조건으로 채택, (3) medium 요청값만 확인 가능하면 effective effort unknown을 허용하되 실제 model metadata는 필수, (4) A에서 Host가 시작한 실제 stop과 전체 descendant 부재를 반드시 관측, (5) 위 Host 계수·원 A 잔여·20시간 누적 한도 유지. 관리 정책 부재를 확인할 수 없거나 필수 효과/중단 관측이 없으면 Hold다.

승인 시 이전 실행안의 B–D 권한은 이 명시적 수정과 기존 Go 조건 안에서 이어가며 정상 단계마다 재승인을 추가하지 않는다. 실제 고객 데이터·새 계정/과금·source/adopter commit·최종 수락은 포함하지 않는다. 거절하면 기존 강화 계약과 A Hold를 유지한다. 이번 작성/R0 승인은 그 실행 결정을 대신하지 않는다.
