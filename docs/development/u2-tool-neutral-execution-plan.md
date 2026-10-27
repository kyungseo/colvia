# U2 Tool-Neutral Execution Plan

## Current Navigation — 2026-10-27

아래 계획과 R0·승인 대기 문구는 당시의 준비 이력이다. 이후 승인·실행·수락 판단은 [FEAT-20261022-001의 최종 closeout](FEAT-20261022-001-prepared-tool-plan-live-qualification.md#final-owner-acceptance-and-work-done--2026-10-27-kst), [수락 범위와 남은 한계](FEAT-20261022-001-prepared-tool-plan-live-qualification.md#accepted-scope-and-remaining-limits)에서 확인한다. 이 연결은 과거 계획 bytes나 미검증 상태를 소급 수정하지 않는다. 현재 탐색 연결의 변경은 [CHORE-20261027-002](CHORE-20261027-002-user-flow-and-development-doc-alignment.md)가 소유한다.

Status: Driver-revised after one Claude R0 (REVISE, four blocking findings), 2026-10-26; awaiting Owner execution decision. The revised bytes were not re-reviewed. Progress owner: [FEAT-20261022-001](FEAT-20261022-001-prepared-tool-plan-live-qualification.md). This proposal does not activate implementation or runtime qualification.

Current direction: [2026-10-26 platform scope](#platform-direction-and-minimum-u2-boundary--2026-10-26) and the owning Work identify the current minimum scope; earlier approval wording below is historical.

## Decision And Preserved Acceptance

Core와 U1의 기존 수락은 유지한다. 이번 변경은 U2의 공통 제어와 Codex·Claude Code 연결부를 나누고, 도구별로 부족한 실행 근거를 채우는 일이다. 2026-10-26 Owner는 이 실행안 작성과 Claude R0만 승인했다. 구현, 작업용 runtime/model 실행, 새 runtime 인증·설치·과금 경로 전환은 아직 승인하지 않았다. 이번 R0는 명시적으로 요청된 정적 Reviewer 호출이며 작업용 runtime 실행과 구별한다.

도구 중립 원칙은 [M0](agent-delegation-m0-plan.md)와 [DR-0005](../decisions/DR-0005-delegated-ordinary-work-acceptance.md)의 기존 계약에서 출발한다. 이번 계획이 Core의 새 원칙을 발명하거나 과거 수락을 취소하는 것은 아니다. 두 주요 사용 도구는 Codex와 Claude Code다. 각 도구의 실제 지원 범위는 실행 근거로 독립 판정하며 manual/provider-null 경로도 유지한다. 현재 Claude Code U2는 미검증이다.

```text
프로젝트의 intent · Work · ticket · result · continuation (기존 Core)
                         |
       공통 Host: 승인 범위 · 효과 제어 · 누적 예산 · 복구
                         |
           +-------------+-------------+
           |                           |
      Codex adapter              Claude Code adapter
      기존 실험 경로              공식 CLI/SDK 후보
```

새 공통 SDK, scheduler, provider registry 또는 Core schema를 만들지 않는다. 모델 이름, 인증 경로, protocol과 notification은 adapter 설정에 귀속하되 실행마다 정확한 값을 고정한다. 설정 변경은 승인 변경이나 기존 실행의 예산 초기화가 아니다. 같은 대화의 도구 간 이동은 지원 목표가 아니며, 재개는 Core의 승인·입력·결과·누적 사용량에서 시작한다.

## Evidence Reuse And Remaining Gaps

| 영역 | 유지할 근거 | 이번에 필요한 확인 |
| --- | --- | --- |
| Core | 현재 source와 accepted 설치의 managed 30파일이 일치한다. 12 Python module의 정적 조사에서 모델 SDK/CLI 호출을 발견하지 않았다 | 변경 전후 30파일 동일성. 중립성의 전체 실행 증명으로 확대하지 않는다 |
| 기존 전체 검사 | 동일 candidate의 normal 706/706 및 parent optimized 706/706 통과. 두 실행 합계 약 114분 | 당시 선택 입력 94개 중 현재 90개 동일, U2 관련 4개 변경. 해당 4개와 새 adapter 위험만 새로 검사한다. 현재 전체 706 PASS라고 쓰지 않는다 |
| U1 | 기존 수락, 실제 사용·명시적 none 및 Codex fresh-reader 근거 | Claude fresh-session continuation 읽기·재개 1사례. 가능한 경우 아래 adapter 재개 검사와 결합 |
| 이전 Claude reader | 4사례 중 strict 3통과/1실패. grant 유무·actor 경계의 제한적 읽기 근거 | U2 실행이나 U1 continuation 성공으로 대체하지 않는다. source-entry 실패와 이전의 실패 이력을 보존 |
| Codex U2 | accepted offline proof와 H10 단일 host 기술 회귀, H01–H09의 각각 명시된 과거 source/build 근거 | 공통 경계 추출로 영향받은 경로만 재검사. H10 원문 품질·Owner 활동 시간은 아직 미측정 |
| Claude U2 | 공식 CLI/SDK의 기능 설명만 있음 | 동일 필수 보장의 구현 가능성 및 실제 실행. 문서·R0·mock은 이를 대신하지 못함 |
| Windows | 별도 OS qualification lane | 이번 macOS 도구 중립 조정의 완료/실패를 Windows 검증으로 옮기지 않음 |

원 [H01–H10 기준](u2-single-host-continuous-work-plan.md#verification-and-completion-criteria), [고정 recovery 사례](u2-single-host-continuous-work-plan.md#verification-ids-and-recovery-cases), [통합 실행안](u2-live-integrated-execution-plan.md)의 안전·수락 기준은 유지한다. 아래 검사는 중복 실행을 줄이는 배치이며 기준 면제가 아니다. 과거 서로 다른 source/build에서 관측한 H04/H05/H10을 한 현재 candidate의 전체 통과로 합치지 않는다.

## Minimum Change Boundary

| 대상 | 허용할 최소 변경 | 제외 |
| --- | --- | --- |
| `docs/development/verification/u2-host/host.py` | 공통 Admission/Acceptance/Budget/복구에서 Codex RPC·thread·model의 직접 의존을 제거하고 adapter 결과를 검증 | Core writer·새 권한·자동 수락 정책 추가 |
| 같은 디렉터리의 `adapters/codex.py`, `adapters/claude_code.py` 및 작은 공통 계약 모듈 | Codex transport를 기존 동작대로 이동, Claude 공식 경로 연결, 논리 실행 식별자와 native session/call 식별자의 명시적 대응 | 범용 plugin framework, 세 번째 backend, 두 번째 runtime fork |
| `worker.py`, 현재 `tool-profile-v2.json` | 실제 공통 경계가 요구하는 연결만 수정. macOS worker 효과 제어 유지 | OS 격리 완화·Windows 이식·worker network 확대 |
| `tests/fixtures/u2_host.py`, `tests/test_u2_host.py`, 필요한 adapter 집중 test 1개 | 실제 변경의 guard·실패·복구 검사 | Core 전체·외부 runtime 전체 테스트의 자동 반복 |
| 기존 Work와 본 계획, Development Index의 해당 설명, 기존 U2 계획의 현행 pointer | 공통 계약/도구별 실행 근거/미검증/예산을 일관되게 기록 | 과거 고정 계획·리뷰·사용량 덮어쓰기 |
| source-only `manual/en/README.md`, `manual/ko/README.md`의 필요한 문단 | C 결과 뒤 실제 지원/미검증을 구분하고 기존 현행 안내 pointer 유지 | managed 30파일 변경, 과거 tutorial 8파일 전체 재작성, prose만으로 지원 선언 |

A의 최소 probe는 기존 durable task 경로의 이번 조정 하위 폴더에만 둔다. B에서 유효한 계약만 source adapter로 흡수하고, 고유 증거/복구 소비자가 없어진 일회성 probe는 정리한다. 관리 대상 30파일은 이번 범위에서 한 바이트도 바꾸지 않는다. Development Index의 기존 intake 기준 자체를 바꿔야 하면 DR-0003의 별도 amendment로 넘기며 단순 navigation 변경으로 처리하지 않는다.

기존 Codex runtime fork는 exact 기존 binary/source 근거를 adapter 뒤에 보존한다. 이번 기본안에서 Rust fork를 수정하거나 재빌드하지 않는다. 공식 Codex 경로로 교체·fork 제거는 동등 보장 근거가 없으므로 별도 후속이다. 외부 비교 프로젝트의 식별 정보는 public-intent source 문서에 넣지 않는다.

## Required Common Guarantees

공통 계약은 다음을 모두 요구한다. 구현 위치가 달라도 효과와 거절 조건은 같아야 한다. 원 Codex 실행에서 승인한 prepared snapshot, 최종 송신·dispatch 결속, 인증/정책 고정과 retry 금지 등의 강화 조건을 이번에 조용히 축소하지 않는다.

1. Core의 exact intent/Work/grant/ticket/result와 승인 bytes를 Host가 확인하고, adapter가 제공한 문자열을 권한으로 신뢰하지 않는다. 다른 actor/home/action/scope, stale·변조·재사용·revoke는 효과 전에 거절한다.
2. 허용 tool inventory·입력/결과·native identity·세대 변경을 고정하고, 승인 없는 tool/shell/subagent·ambient MCP/hooks·외부 연결을 실행하지 않는다. tool 허용 UI 또는 callback 하나만으로 효과 차단을 입증하지 않는다.
3. 최종 model 송신과 tool dispatch 전에 durable 예약을 fsync하고, final headers/bytes와 승인 입력을 결속한다. 예약 실패·초과·불일치이면 송신/효과를 사전에 차단한다. HTTP/SSE/WS/auth/route retry, redirect, TLS fallback은 0이며 금지 sender 생성도 막는다. 관측 불가능한 송신을 사후 사용량으로 대체하지 않는다. turn당 generation은 최대 2회, dispatch는 최대 1회다.
4. credential은 native read-only 인증에만 사용한다. refresh/relogin/keyring·credential store mutation을 사전에 차단하며 발생 횟수는 0이어야 한다. native policy는 단회·무cache·고정 bundle이고 성공한 model catalog도 고정한다. raw credential·email·실제 고객 데이터는 기록/packet에 넣지 않는다. 다른 billing/provider, 갱신 필요, 차단 불능 또는 권한 확대는 실행 전 Hold다. 사후 변경 탐지만으로 사전 차단을 대신하지 않는다. 승인된 trusted-runtime 범위를 OS 전체 격리라고 주장하지 않는다.
5. 실제 worker는 기존 control/runtime/Git/policy/credential·alias·network 효과 경계를 지킨다. 승인 없는 변경과 오류 뒤 authority 재시도는 금지한다.
6. 중단/상한/프로세스 사망 뒤 pending·journal·남은 예산을 보존한다. TERM 10초 → KILL 10초 뒤 실제 process group/descendant 부재를 확인하며 불명확한 descendant가 있으면 미확인으로 중단한다. 재개는 exact 승인과 누적 사용량을 승계하며 missing/drift/unknown은 거절한다. crash 후 원 ticket recovery와 새 후보 실행을 혼동하지 않는다.
7. content quality와 source/실제 결과의 Owner 수락은 기술적 성공과 별도다. Reviewer나 adapter가 이를 대체하지 않는다.

공식 CLI/SDK가 이러한 관측·강제 기능을 모두 제공하는지는 미확정이다. [Claude headless 문서](https://code.claude.com/docs/en/headless)는 CLI/SDK 진입과 bare mode의 별도 API 인증을 설명하며, [permissions 문서](https://code.claude.com/docs/en/agent-sdk/permissions)는 callback 이전에도 허용되는 경로가 있음을 설명한다(2026-10-26 확인). 이것은 Colvia 계약 적격성의 증거가 아니다. 기존 subscription 경로를 유지하며 `--bare`나 API key로 우회하지 않는다.

## Guarantee Mapping And Admissible Evidence

아래는 기존 구체 조건의 집행 위치와 Go 근거다. adapter의 wire 형식은 달라도 각 조건의 효과는 유지한다. 동등 대체는 이미 승인된 경계 안의 사전 차단과 실제 거절을 함께 입증한 경우만 인정한다. 차단이 필요한 조건을 탐지 후 중단으로 바꾸지 않는다. 미지원은 No-Go, 불명확한 근거는 Hold다.

| 기존 필수 조건 | 집행 책임 | Go에 필요한 근거 |
| --- | --- | --- |
| exact intent/actor/home/action/scope/grant/ticket/result, stale/revoke/중복 거절 | 공통 Host + 기존 Core | 효과 전 exact gate 코드/고정 입력과 실제 adapter 경로의 합성 거절. Core authority 의미는 그대로 재사용 |
| prepared tool inventory, native thread/turn/call, history version과 승인 input 결속 | adapter의 native 경계 + Host | 실제 송신/dispatch 직전 강제 지점과 불일치 negative. schema/manifest/historical proof만으로 대체 불가 |
| native read-only auth, refresh/relogin/store mutation 0 | adapter + 이미 승인된 효과 제어 | 쓰기를 막는 구조적 근거와 read-only admission, 비밀을 노출하지 않는 사전·사후 무변경 확인. 비교만으로 차단 증명 불가 |
| 정책 단회·무cache·고정 bundle, 성공 model catalog 고정 | adapter | 재로딩/변경을 막는 코드·설정 및 drift 거절. 모델 자기보고는 근거 아님 |
| final headers/bytes guard, 송신 전 fsync 예약, generation 최대 2/turn | adapter의 final sender + 공통 Budget | 최종 sender까지 우회 없는 사전 gate, 예약 실패/초과 거절. transcript·사용량·사후 hook은 보조 관측만 |
| HTTP/SSE/WS/auth/route retry 0, redirect/TLS fallback 0, 금지 sender 생성 차단 | adapter | 해당 동작을 불가능하게 하는 설정/구조와 관련 negative. 2회 성공 관측만으로 부재를 입증하지 않음 |
| dispatch 최대 1/turn, native call identity·결과 결속 | 공통 Host + adapter | dispatch 전 예약과 재호출/변조 거절. native 실행 권한을 callback 단독에 맡기지 않음 |
| control/runtime/Git/policy/credential/alias/network worker 경계 | 기존 worker 효과 제어 | 변경하지 않은 기존 증거 + 새 경로가 이를 통과한다는 실제 거절 관측. 새 sandbox/proxy로 교체하지 않음 |
| process death/stop, pending·누적 사용량·exact recovery, TERM/KILL | 공통 Host + adapter | 실제 child 종료/부재, durable journal, Core 기반 fresh-session 재개와 missing/drift 거절 |
| H10 품질/부담과 Owner 수락 | Driver/Owner | 기존 5문서 근거 대조와 Owner 판정. 기술적 accept·Reviewer 판정으로 대체하지 않음 |

새 proxy, TLS 가로채기, endpoint/base URL 변경, 새 credential 방식 또는 권한 확대가 필요하면 A 안에서 시도하지 않고 Hold한다. 기존 Codex proxy의 승인된 exact 경계는 유지하며 이를 Claude 경로에 자동 전용하지 않는다. 문서, runtime 자기보고, callback 단독, 사후 로그는 필수 사전 강제 지점을 대신할 수 없다. 구조적 집행 근거와 최소 실제 관측이 함께 있어야 Go다.

## Exact Runtime Setup Before Any Probe

기본 후보는 현재 설치된 Claude Code CLI 2.1.310이며 SDK 설치는 제외한다. CLI bytes SHA-256은 `ffb64331bc0ee1b69efb7c2c428bd3ab516bc31b75bf60886b356c97c1c25ffd`, 인증은 현재 `claude.ai / firstParty / pro`다. 이 CLI/auth identity는 앞선 정적 Reviewer 호출에서 확인했으며, 당시 actual model은 Opus 5.5였다. 2026-10-26 Owner의 추가 방향에 따라 앞으로 Colvia가 호출할 작업용 Claude model은 Sonnet 5.5, 이 세션의 Reviewer는 Opus 5.5로 분리한다.

| 역할 | 실행 시 지정할 model | 현재 근거 |
| --- | --- | --- |
| Colvia Claude adapter / 합성 worker | `--model claude-sonnet-5-5` | 공식 model ID 확인. 이 계정의 실제 worker 호출·적격성은 미검증 |
| 현 세션의 Claude R0/R1 Reviewer | `--model claude-opus-5-5` | 기존 R0 actual model 확인. 이후에도 호출별 명시 지정 |

[공식 model 설정 문서](https://code.claude.com/docs/en/model-config)에 따라 호출별 `--model`로 분리하며 전역 설정·사용자 기본 model은 바꾸지 않는다. 움직이는 `sonnet`/`opus` alias 대신 위 버전을 지정한다. [Sonnet 5.5 공식 안내](https://www.anthropic.com/claude-sonnet-5-5)의 model ID를 사용하되 account availability와 실제 응답 identity는 A의 기존 admission/최초 승인된 probe에서 확인한다. Sonnet이 사용 불가이거나 실제 model이 다르면 Hold하고 Opus/API key로 자동 전환하지 않는다.

첫 3시간의 Claude 검증과 후속 C는 Sonnet 5.5를 대상으로 한다. Opus Reviewer 관측을 Sonnet worker 지원 근거로 승계하지 않는다. Core·권한·송신/시도·중단 기준과 기존 시간 한도는 그대로다. Sonnet이 사용량 부담을 줄일 것으로 기대하지만 구독 quota의 절감 비율이나 작업 성공률은 아직 측정하지 않았으며, API 가격비를 구독 사용 가능 시간으로 환산하지 않는다. 향후 실행 승인은 같은 subscription을 합성 worker 실행에 사용하는 범위를 포함해야 한다. 이번 model 방향 결정은 구현·worker 실행·추가 리뷰 호출 승인과 구별한다.

Codex는 마지막 H10 기술 회귀에서 최종 보정 뒤 실제 실행·봉인된 candidate에 대응하는 `codex-prepared-tool-plan-live` 단일 binary, SHA-256 `40b081c599d3918e3ec3525d125f16dbeec08efe4d7c717022285a774bf30505`를 선택한다. model/policy는 기존 `gpt-6-astra/xhigh`와 native read-only 경로를 유지한다. 다른 과거 binary의 PASS를 섞지 않는다. 기존 H10의 사용 완료 allocation/ticket을 재사용하지 않으며 이번 synthetic namespace/예산의 새 실행 입력으로만 준비한다. 이 binary가 그 입력을 허용하지 않으면 Hold하고 자동 Rust 수정·build로 전환하지 않는다.

A의 첫 30분에 다음 필드를 기존 task setup에 고정한다. 모델이 필드나 argv를 고르지 않는다. 하나라도 미확정이면 probe를 실행하지 않는다.

- CLI의 resolve된 절대 경로·버전·digest, model/effort와 native auth/provider/billing identity, 전체 argv와 cwd. 확인한 binary에 drift가 있으면 갱신해서 계속하지 않는다.
- native permission mode는 `dontAsk`를 기본으로 하고 모든 built-in shell/file/subagent/browser tool은 제거한다. MCP는 Host가 소유한 고정 custom bridge만 허용한다. 논리 tool은 기존 v2의 `u2_read_file/u2_write_file/u2_verify/u2_accept` 중 해당 합성 case에 필요한 부분집합만, schema digest와 native 표시명을 함께 고정한다. 실제 adopter authority handle은 넣지 않는다.
- 설정 source·system prompt·project/사용자 memory·skill/plugin/output style/hooks·ambient MCP를 배제하는 정확한 옵션과 허용 입력 digest. CLI가 이 조건을 제공하지 않으면 다른 mode로 우회하지 않는다.
- 부모 환경에서 상속할 이름 allowlist, native auth를 위한 기존 HOME identity, task-local cwd/temp/log/session 경로와 소유권. HOME/전역 설정을 바꾸거나 credential을 복사하지 않는다. credential/provider override는 값 없이 존재 여부만 확인하고 예상 밖 override는 거절한다.
- update/설치·telemetry·오류 보고·기타 비model 송신의 차단 설정과 실제 enforce/관측 방법. 필요한 native control endpoint는 기존 승인 집합만, startup당 최대 4회로 예약한다. 추가 endpoint가 필요하면 Hold다. model/control 외 송신은 0이다. 설정만으로 차단을 입증했다고 쓰지 않는다.
- session persistence는 끄고 user home의 ambient transcript를 재개 입력으로 사용하지 않는다. Core의 승인·고정 입력·직전 검증·pending·누적 사용량에서 fresh session을 만든다. 이 계획의 native resume은 0회다. 필요한 task-local 기록 위치와 종료 뒤 보존/정리 소비자를 고정하며, 예기치 않은 home 기록이 필요한 경로는 Hold다.
- 각 명령의 입력 bytes, timeout, signal/cleanup, 출력 경로, native process/turn/send/dispatch 계수와 remaining budget. 설치/update 필요, 비model 송신/ambient 입력 배제 불가, 인증 용도 불명, input drift 또는 과거 authority 소비 상태 불명은 실행 전 Hold다.

기록된 source/CLI/model/policy가 달라지면 기존 exact setup으로 실행할 수 없다. 승인된 B의 source 변경은 각 실행 전에 새 exact 입력과 영향 체크를 고정하는 범위에 포함하지만, 예상 밖 drift는 먼저 해소해야 한다. 권한/경로/보장 변경은 별도 결정이다.

## First Three Hours After Execution Approval

첫 판별의 상한은 실행 승인 후 활동 180분이며 전체 20시간에 포함된다. 첫 165분까지 판별을 끝내고 마지막 15분은 중단·보존·보고에 쓴다. 현재 계획/R0 시간은 이 180분에 포함되지 않으며 전체 20시간에서만 차감한다. 아래 비율은 작업 배치이고 각 단계마다 새 3시간이 생기지 않는다.

| 누적 활동 시간 | 작업 | 산출물/판정 |
| --- | --- | --- |
| 0–30분 | 현재 source/evidence drift, 인증·과금 경로, CLI/SDK 버전과 지원 옵션 확인. 원 필수 보장을 공통/도구별로 대응 | source·contract·설정 고정표. 인증 변경 필요 시 실행 전에 Hold |
| 30–75분 | 공식 인터페이스에서 inventory·native ID·송신 횟수/최종 입력 결속·retry·중단·재개 보장을 확인. 필요한 최소 adapter probe만 작성 | 보장마다 관측 방법과 enforce 위치. 지원 API/제어 지점이 없으면 No-Go; 구현을 확장하지 않음 |
| 75–145분 | 앞 단계가 충족될 때만 합성 데이터로 Claude 프로세스 최대 2회(첫 실행+재개), model turn 총 4회/송신 총 6회/dispatch 총 4회 이내 | 허용 호출 1개, 잘못된 identity/scope 거절, 실제 stop 후 잔여 예산 재개. 실제 경로에 결속한 negative를 기록 |
| 145–165분 | 원 보장과 실행 결과를 대조하고 후속 범위·예상 잔여 시간을 갱신 | Go/No-Go/Hold 판정과 근거 |
| 165–180분 | 실행 중지, process 부재·journal·필수 파일 확인, 기존 Work checkpoint | 자동 재시작 없이 판별 종료 |

Go는 첫 단계의 모든 필수 보장에 enforce 지점이 있고 최소 실제 loop·거절·중단/재개가 관측되며, 남은 구현/검증이 잔여 시간과 도구별 시도 횟수 안에 들어갈 때만 가능하다. B 시작 전에 보장별 enforce/관측 근거, 잔여 시간·시도, 고정 setup과 아직 상속할 수 없는 검사를 기존 Work에 durable checkpoint로 기록한다. 기록 전에는 B를 시작하지 않는다. 문서상 가능/정적 추론/mock만으로 Go를 내리지 않는다. 이 Go는 전체 적격성 통과가 아니다. 한 보장이라도 미지원이면 No-Go, 인증/환경/근거가 불명확하거나 165분까지 끝나지 않으면 Hold다. 둘 다 자동 대안 탐색·권한 확대·두 번째 fork 없이 보존하고 보고한다. Hold/No-Go 뒤 자동 재개하지 않는다. 이후 별도 재개가 승인돼도 같은 20시간·동일 카운터의 잔여에서 차감하며 A의 180분은 새로 생기지 않는다. A 자체가 소진됐으면 추가 판별 한도도 별도로 결정해야 한다.

향후 Owner가 이 전체 실행안을 승인한 경우에만 Go 후 아래 단계로 이어간다. 각 정상 단계마다 재승인을 요구하지 않는다. 안전 보장 변경, 새 비용/권한/데이터, 한도 초과와 exact authority action은 기존 별도 결정 경계를 유지한다. 현재의 계획·R0 승인은 Go 이후 실행 권한도 주지 않는다.

## Remaining Implementation And Verification

| 단계 | 예상 활동 시간 / 단계 중단 한도 | 최소 검증 |
| --- | --- | --- |
| A: 위 판별 | 1.5–2.5시간, stop 3시간 | official Claude 경로의 필수 보장과 실제 최소 loop |
| B: adapter 분리 | 4–7시간 / 8시간 | 공통 guard 1묶음, 기존 Codex host 동작 보존, tool 설정 교체 시 Core 형식 불변 |
| C: 두 도구 실행 | 3–5시간 / 6시간 | 각 adapter 실제 허용/거절/stop/resume, H01–H09 영향 항목, Claude U1 fresh-session 확인 |
| D: 품질·부담·R1·정리 | 1–2시간 / 2시간 | 기존 5문서 결과와 근거의 품질 확인, Owner 판단, 변경된 공통 경계와 도구별 근거를 대상으로 R1 |

합계 예상은 향후 A–D 9.5–16.5시간에 이번 계획/R0의 실제 시간을 더한다. 현재 전체 전망은 약 10–18시간이며 판단 기반·낮은 신뢰도의 추정이다. 기존 114분 전체 검사 재사용은 이 추정에 이미 반영했으므로 다시 차감하지 않는다. A의 실측으로 B–D를 재추정한다. 새로운 SDK 설치·runtime fork 보정이 필요하면 이 추정의 전제가 깨진 것이다.

공통 pure guard는 한 번 검사한다. adapter별 identity/dispatch/transport는 각 실제 경로에서 검사한다. process 종료·재개도 각 도구에서 수행한다. C의 기본 시간·시도 배정은 A의 probe를 재사용하지 않는 전제다. 같은 candidate/동일 경로/동일 보장인 경우에만 A 증거를 명시적으로 재사용하며 절약분을 추가 실행 권한으로 바꾸지 않는다. negative는 scope 밖의 실제 데이터나 network에 접근하는 방식으로 만들지 않고 합성 대상에서 효과 전에 거절되는지 관측한다. 순정 Core의 exact authority recovery가 필요해지면 원 H05의 Owner 경계를 유지한다.

기존 5문서는 다시 생성하지 않는다. Driver가 원 task 요구·참조·diff를 대조하고 Owner에게 파일별 정확성/누락/불필요 수정과 판정 요청을 제시한다. 예상 40–60분 중 Owner 능동 확인은 20–30분으로 가정한다. Owner의 이번 능동 확인 시간도 전체 20시간에 포함한다. Driver와 동시에 진행한 시간은 합집합으로 한 번 계상하고 역할별 실측은 별도로 표시한다. 과거 H10의 미측정 시간은 소급 추정해 성공 수치로 바꾸지 않는다. 새 문서 수정이 필요하면 결함과 수정 범위의 승인을 먼저 확인한다.

R1은 계획된 1회, 필요 시 같은 경계의 수정 확인 1회까지만 제안한다. 전체 기존 H10 리뷰를 다시 수행하지 않는다. 원 H01–H10 각 항목은 새 실행/유효한 상속/미관측으로 최종표에 남긴다. 미관측이 있으면 전체 qualification 완료로 선언하지 않는다.

## Cumulative Budget And Attempts

이번 조정의 제안 상한은 활동 72,000초(20시간)다. 계획/R0, 구현, build가 허용된 경우 그 시간, 모델/검사 대기, 실패 보정, 리뷰, 기록·정리를 모두 포함한다. 동시에 진행한 구간은 시간 합집합으로 한 번 계산한다. Owner 답변만 기다리는 구간은 별도 표시하고 활동 시간에서 제외하되, 실행 중인 child의 실제 대기는 제외하지 않는다. 마지막 1,800초(30분)는 정리 예약이며 70,200초에서 새 실행을 중지한다. 단계/시도 한도와 전체 한도 중 먼저 닿는 것이 우선이다.

기존 사용량·실패·승인·exact ticket과 journal은 수정하지 않는다. 기존 전체 한도의 잔여 표시, 이미 종료된 deadline, H10 회귀 잔여를 이번 예산으로 빌리지 않는다. 이번 20시간은 기존 노력의 reset이 아니라 후속 범위에 대한 추가 상한 제안이다. 현재 작성/R0는 승인된 범위만 수행하며, 20시간 자체와 나머지 실행은 Owner 결정 전까지 활성화하지 않는다. 이번 준비 구간은 2026-10-26 06:27:00Z부터 최종 보고 checkpoint까지 실제 활동을 기록하고, 실행 승인 시 그 사용량을 72,000초에서 먼저 차감한다.

| 기존 기록 | 승계 방식 |
| --- | --- |
| integrated ledger | `total_active_seconds=176128.667634`(약 48.925시간)라는 마지막 기록값과 후속 별도 승인 구간을 보존한다. 오래된 cap/deadline 필드가 섞여 있으므로 현재 실행 가능 잔여로 사용하지 않는다 |
| 2026-10-25 continuation | 추가 승인 8시간, 당시 이전 사용량 150036.092291초와 누적 cap 182297.229초, 이전 attempts snapshot을 그대로 보존한다. 이미 위 ledger에 반영된 구간을 다시 더하지 않는다 |
| 2026-10-26 H10 regression | 기록 시 7751.751319초(대기 포함), native 1/1, authority apply 1/1, preparation 5/5, review 4/4 소비. 종료된 고정 deadline의 잔여는 전용할 수 없다 |
| 이번 조정 | 기존 Work 아래 새 구간으로 시간과 시도를 append한다. 과거 전체 합계의 포함 관계가 확인되지 않은 부분은 unknown으로 표시하며 임의 총합을 만들지 않는다 |

현재 계획 R0 호출 상한은 1회, payload 160 KiB, 호출 wall 880초와 종료 정리 10초다. 호출 직전 subscription/firstParty 경로를 확인하며 실패·timeout에도 호출 시도는 소비된다. 이번 R0를 기존 4/4의 5번째 호출로 숨기거나 기존 횟수를 0으로 바꾸지 않는다.

향후 실행 승인에 제안하는 추가 시도 한도는 다음과 같다. 모든 횟수는 실행 직전 durable 예약하고 실패도 차감한다. 재개/새 session/수정 candidate가 예산을 초기화하지 않는다.

| 계수 대상 | Codex 배정 | Claude 배정 | A 사용분 / 단위 |
| --- | --- | --- | --- |
| live native process starts | 4 | 4 | A Claude 최대 2 포함. restart/fresh-session 재개도 1회. 전체 조정 범위 |
| live model turns | 8 | 8 | A Claude 최대 4 포함. 전체 16 |
| live model sends | 12 | 12 | A Claude 최대 6 포함. 전체 24, turn당 최대 2 |
| live tool dispatch | 8 | 8 | A Claude 최대 4 포함. 전체 16, turn당 최대 1 |
| native control requests | 16 | 16 | A Claude 최대 8 포함. start당 4, 전체 32. 기존 허용 endpoint만 |
| offline/fake-provider runtime process starts | 12 | 12 | A Claude 최대 6 포함. test가 띄운 native/fake process도 차감. 전체 24, model/auth/network 0 |
| offline simulated turns/dispatch | 각각 24/24 | 각각 24/24 | A Claude 각각 12/12 포함. 실제 provider 근거로 전환하지 않음 |
| 공통 Python/Core test subprocess | 도구별 배정 없음 | 도구별 배정 없음 | 최초 batch 1 + 보정 batch 2가 A–D 전체 한도. 선택 test ID/명령·예상 child 수를 실행 전 고정, batch당 30분. runtime을 띄우면 위 offline/live 카운터에도 예약 |
| runtime build / 전체 Core suite | 0 / 0 | 0 / 0 | 설치/추가 compile/전체 검사 자동 전환 없음 |

adapter 간 잔여 횟수를 자동 전용하지 않는다. C에는 Claude 2 starts(정상+fresh 재개), Codex 2 starts를 기본 배정하고 위 잔여 안에서만 통상 결함 보정 재시도 adapter당 최대 1회를 허용한다. A가 Claude 2 starts를 모두 쓰면 C의 2 starts 뒤 Claude 재시도 여유는 0이다. 부족하면 criteria를 줄이지 말고 Hold한다. A에서는 최초 실패를 보존하고 즉흥 재시도하지 않는다. safety discrepancy·unknown authority·반복 동일 실패는 즉시 중단한다.

모델 turn은 최대 15분, 일반 host/offline case는 5분, live native process는 30분이며 단계·전체 잔여가 먼저 적용된다. 종료는 TERM 10초 → KILL 10초 뒤 실제 부재 확인까지 포함한다. 이 20초 정리를 실행 deadline 전에 예약한다. 내부 송신을 사전에 제한할 수 없으면 Hold이며 turn 수나 사후 token 사용량으로 대체하지 않는다. pure guard의 수많은 assertion은 process starts와 같지 않으나, native child를 띄운다면 반드시 위 계수에 포함한다.

현재 R0 1회와 미래 R1 최대 2회는 구분한다. R1 각 15분/160 KiB와 종료 정리 20초 이내이며 전체 시간에 포함한다. 미래 실행 승인 요청에는 이 R1의 public-safe source diff·synthetic case·비식별 evidence packet을 Claude 서비스에 보내는 범위도 포함한다. 실제 5문서 본문·고객 데이터·계정·credential·실제 target 경로는 제외하고 호출마다 exact packet과 인증을 확인한다. 이번 R0 전송 승인은 미래 R1 전송 승인이 아니다. R0 보정본은 Driver 처분이며 재검토 PASS라고 표시하지 않는다.

실제 adopter authority apply, 새 intent/grant, commit/result tag는 위 횟수 표로 승인되지 않는다. synthetic target에서 Core writer가 필요한 경우에도 사전에 exact synthetic action/actor/범위와 ticket을 고정한다. 실제 H05/H10의 별도 Owner 판단을 유지한다. 공통/도구별 safety gate와 원 H01–H10 요구를 충족할 수 없는 횟수라면 추가 시도나 coverage 면제를 자동으로 만들지 않는다.

최종 보고는 과거 integrated ledger, continuation 승인 시점, H10 회귀, 이번 조정의 사용량·cap·시도를 구간별 행으로 병기한다. 겹치는 과거 행을 합산하지 않는다. continuation의 32,261.136709초는 과거 cap 153,497.229초에서 당시 사용량 150,036.092291초를 뺀 3,461.136709초와 추가 28,800초의 합이다. 이는 당시 snapshot의 산술 설명이며 현재 잔여나 추가 전용 권한을 뜻하지 않는다. 전체 역사에서 포함 관계가 확인되지 않은 항목은 여전히 unknown이다.

## Completion, Rollback And Next Decision

완료 조건은 Core/U1 수락·30파일 동일성 유지, 두 adapter의 필수 보장과 최소 실제 관측, 영향받은 H01–H09의 처분, 기존 H10 품질/부담 판정, R1 finding 처분 및 Owner 최종 수락이다. source 검증 완료가 installed release·public support·Windows·production 적격성이나 자동 adopter update를 뜻하지 않는다.

되돌리기는 새 adapter와 Host의 이번 변경을 분리한 diff 단위로 수행한다. 기존 accepted binary/결과/Core truth를 덮어쓰지 않으므로 기술적 되돌리기 비용은 국소적이나, 이미 사용한 시간·모델 호출은 돌려받을 수 없다. authority 효과는 Git rollback으로 되돌리지 않고 기존 recovery 규칙을 따른다. unknown 상태에서 자동 rollback·replay하지 않는다.

Owner/다음 실행 담당자가 사용할 계획, 리뷰 원문, 필수 입력·결과·복구 기록은 기존 durable task 경로에 보존한다. 리뷰 판정과 필요한 기록이 기존 Work에 옮겨지고 소비자가 사라진 임시 runner/중복 packet은 standing cleanup 조건에 따라 정리한다. 기존 worktree는 구체적인 다음 구현과 과거 recovery에 필요하므로 유지한다. branch 삭제·commit/push/release·새 환경 설치는 이번 계획 승인에 포함하지 않는다.

다음 결정은 이 문서의 정확한 revision과 R0 처분을 대상으로 한 실행 승인이다. 승인 범위는 이번 준비 사용량을 차감한 추가 20시간 한도, A의 남은 3시간, 표의 누적 시도, 같은 subscription의 합성 worker 용도, 지정 source 변경과 bounded R1 전송이다. 필수 안전 보장과 separate authority action은 유지한다. 승인되지 않으면 현재 계획·리뷰 checkpoint에서 멈춘다.

## Platform Direction And Minimum U2 Boundary — 2026-10-26

Owner는 2026-10-26 U2와 이후 기능의 설계 대상으로 macOS·Windows를 함께 두도록 요청했다. 이어 중앙 통합계획의 플랫폼 책임 구분과 통합 후 OS 리팩토링 순서를 기준으로 삼고, 이번 완료 조건은 새로 추가·변경하는 U2 코드의 최소 경계로 한정한다고 명확히 했다. 이 절은 그 방향을 현재 Work에 적용한다. 전체 OS 구조의 확정, Windows 구현 전체, 기존 Windows 작업의 새 선행 조건을 뜻하지 않는다. 앞선 도구 중립 실행안의 역사적 승인 전 문구는 당시 제안이며 실제 승인·진행·현재 누적 한도는 진행 Work를 따른다.

### Responsibility And Sequence

공통 정책은 승인·허용 효과·누적 예산·기록·중단/재개 판정을 소유한다. 도구 adapter는 Codex·Claude Code의 protocol·native identity·해당 도구에서 승인된 신뢰 경계를 소유한다. OS 구현은 그 정책을 수행하는 파일·잠금·시간·IPC·프로세스·격리 수단을 제공한다. OS helper가 지원 정책이나 수락 규칙을 대신 결정하지 않는다. OS 감지, 지원 조합 허용, 설치 profile 전환도 별개다. MCP 표준 사용은 내부 IPC·프로세스 수명의 이식성을 입증하지 않는다.

```text
U2 지금: 새/변경 코드의 공통 정책 ↔ 도구 protocol ↔ 필요한 macOS 실행 경계
후속: Windows·보호 기능 보강/통합 → 통합된 기준 버전의 전체 OS 분기 정리
검증: 도구 × OS × 승인된 실행 profile별 실제 근거로 판정
```

같은 보장은 동일한 OS API를 뜻하지 않는다. 같은 도구/profile에서 승인·거절·예산·중단·복구 의미를 보존하고, 대응 방법이 없으면 실행 전에 미지원으로 거절한다. Codex의 prepared sender 보장과 [별도 수락된 Claude native 신뢰 경계](u2-native-cli-trust-boundary-amendment.md)를 같은 수준의 내부 송신 관측으로 합치지 않는다. 이번 OS 방향은 어느 쪽의 신뢰 계약도 늘리거나 줄이지 않는다.

### Minimum Change Now

| 구분 | 이번 U2에서 할 일 | 전체 정비로 넘길 일 |
| --- | --- | --- |
| 새 공통 read-only 정책 | `ReadOnlyHost`·`EffectJournal` 등이 추가한 저장/잠금 및 예산 시계 의존을 작은 명시적 실행 helper에 위임. 승인·계수·기록 의미는 공통 로직에 유지 | 기존 `contracts.py` 전체의 파일·문서·authority 경로 재배치 |
| 새 Claude 연결 | protocol frame·tool/native identity 검사와 macOS FIFO·pipe polling·process launch/descendant 종료를 구분. 실제 호출이 macOS 실행 helper를 거치도록 하고 native 설정·신뢰 경계·격리 profile은 유지 | 전체 native runtime을 감싸는 범용 process/IPC framework, 빈 Windows backend |
| 새 Codex 실행 계약 | version 58의 승인/배정/journal 상태 전이에서 시계·파일 잠금 호출을 명시적으로 구분. 현재 macOS 구현 선택·미지원 거절은 실행 경계에 둠 | 기존 1–57 계약, sender/auth/Unix FD transport 전면 재구성 및 Windows transport 구현 |
| 기존 worker·Core | 변경하지 않는 동작과 근거를 유지. 이번 변경이 worker 입력/import를 바꾸면 그 영향만 별도 고정 | Core managed 30파일, 기존 문서 worker의 no-follow/atomic publication/sandbox 구조 전체 이식 |

최소 helper의 이름·파일 수는 구현 diff에서 정한다. 별도 영구 플랫폼 아키텍처나 registry를 확정하지 않는다. 공통 정책이 새 macOS 명령/API를 직접 추가하지 않고, 호출하는 OS 경계가 코드에 보이며, 다른 OS에서 필요한 기능이 없으면 효과 전 거절하는 것이 이번 목표다. 기존 모든 POSIX import 제거 또는 전체 Host의 Windows 실행 가능 상태를 이번 macOS 완료 조건으로 만들지 않는다. 도구 선택과 OS 선택을 하나의 backend 이름으로 합치지 않는다.

### Reuse From Windows Work

현재 Windows 작업의 수락 계약·동작·제약·검증을 참조한다. 그 코드 배치를 최종 구조로 채택하지 않는다. 기존 Windows 작업트리는 읽기만 했으며 그 작업의 source·입력·기한·완료 기준을 바꾸지 않는다. 최신 소스와 중앙 방향을 대조한 결과는 다음과 같다.

| 확인한 근거 | U2에서 사용할 의미 | 직접 이식하지 않는 이유/남은 판단 |
| --- | --- | --- |
| native path/handle identity, reparse·link 거절 | 경로 문자열만 신뢰하지 않고 열린 객체와 관측을 결속해야 한다는 계약·negative 사례 | 현재 U2의 no-follow·정확한 mode 및 worker 경계와 계약 대조 필요 |
| `LockFileEx` 기반 exclusive lock | Windows 잠금/정리 구현 및 오류 처리의 재사용 후보 | 현재 구현의 interruptible indefinite wait는 U2의 bounded deadline 잠금과 다름. 그대로 치환 불가 |
| 파일 flush·발행 후 오류·exact recovery | publication 전후 실패를 구분하고 원 입력을 보존하는 의미와 검증 사례 | directory flush의 `unavailable` 처분을 U2의 필수 durable reservation에 자동 적용하지 않음 |
| native 실행·Git fixture·검증 조합 | 실제 OS/runtime/파일시스템/Git 조건을 증거에 결속하는 방식 | runner의 Job 정리는 제품의 U2 process containment 증명이 아님. Git LF/execute-mode 조건도 범용 지원으로 확대하지 않음 |

관측 시 Windows Work는 일반 모드 전체 검증 진행 중이며 최종 native 검증·결과 수락이 남아 있다. U1 Windows의 통과 사례도 U2의 도구/OS 조합 통과로 옮기지 않는다. 코드 재사용은 통합된 기준 소스와 해당 의미가 일치할 때 판단하고, 지금은 중복 설계를 피할 계약과 제약만 유지한다. 정확한 참조 revision·파일 digest와 관측 시점은 기존 private task evidence에 기록한다.

### Completion And Evidence Selection

이번 macOS 단계의 추가 완료 조건은 다음 세 가지다.

1. 위 최소 범위의 새/변경 코드에서 공통 정책과 macOS 실행 동작의 호출 경계가 실제로 존재한다. 문서·Protocol 선언·사용하지 않는 wrapper만으로 완료하지 않는다.
2. 해당 경계의 정상/실패·기한 초과·중단·미지원 거절을 확인하고, 기존 승인·누적 예산·pending/복구 의미와 worker 효과 경계가 유지됨을 보인다. mock/정적 확인과 실제 macOS 실행을 구별한다.
3. 결과에는 각 도구의 macOS 근거, Windows 구현·검증 대기, 통합 후 전체 OS 정비로 넘긴 항목을 구별해 남긴다. Windows 전체 완료나 전체 OS 리팩토링을 이번 완료 선행 조건으로 두지 않는다.

B의 기존 집중 검사는 27개 재사용+보정 후 11개 통과로 38개 선택 항목의 근거를 확보했다. 이번 계획 작성으로 그 결과를 무효화하지 않는다. 향후 코드 변경 시 호출 경로가 바뀐 journal/adapter/process 사례만 다시 고르고, 불변인 문서 worker·Core·pure frame 판정은 입력과 의존 경계를 대조해 재사용한다. C의 기존 두 도구 실제 stop/fresh-resume 검사에 새 경계 확인을 결합하여 같은 검사를 따로 반복하지 않는다. 전체 Core suite나 Windows suite를 새로 요구하지 않는다. 실제 변경이 그 밖의 보장을 건드리면 먼저 범위와 비용을 재판단한다.

### Cost And Execution Boundary

최소 OS 경계 보강의 추가 예상은 활동 45–90분이다. 정적 source 대조·국소 추출·집중 확인·기록을 포함한 판단치이며 실제 추출 난이도는 아직 측정하지 않았다. 기존 새 Codex 계약 구현/compile/검증 예상 120–220분과 합치면 B 후속 예상은 165–310분이다. 같은 검사와 대기는 한 번만 세며 C의 실제 model 실행, D의 품질·R1·Owner 판단은 이 수치에 포함하지 않는다. 별도 플랫폼 아키텍처 설계·전체 OS 정비·Windows 구현 비용도 포함하지 않는다.

B 후속의 중단 한도 제안은 330분(마지막 20분 정리 예약)과 현재 B·전체 승인 잔여 중 작은 값이다. 추가 총시간을 활성화하지 않으며 기존 사용량·실패·시도를 보존한다. 코드 추출이 이 최소 경계를 넘어가야 한다면 전면 정비로 확대하지 않고 충돌 지점을 후속 통합 계획에 연결한다. C/D를 포함한 전체 완료 예측은 compile과 최소 추출 결과 뒤 갱신한다.

이 절의 방향·계획 반영과 새 Rust 계약의 실행 승인은 별개다. 다음 준비는 기존 새 Codex 계약과 이 최소 경계를 한 R0 delta에 묶는 것이다. 새 Reviewer 호출, Rust 수정/build, 추가 집중 batch·simulated 사용량은 아직 활성화하지 않았다. R0에서 지적된 변경을 처분한 뒤 정확한 실행안과 카운터를 제시한다. 기존 미래 R1 0/2를 R0로 전용하지 않는다. 중앙 통합계획의 순서와 진행 중 Windows 작업은 그대로 유지한다.

## R0 Delta Disposition And Execution Proposal — 2026-10-26

R0는 REVISE(차단3, 비차단 보완7, 확인1)다. 실제 Opus 5.5 fresh session, tools0/MCP0, 148.820초, exit0, 입력 drift0, process group 부재를 확인했다. Reviewer는 정적 계약/소스 발췌만 읽었으며 Rust compile·실행 검증은 하지 않았다. 아래는 Driver 보정이며 재리뷰 PASS가 아니다. 원 packet과 응답은 그대로 보존한다.

### Driver Disposition

| 지적 | 처분 | 보정 |
| --- | --- | --- |
| 1 stop 의미 충돌 | revise | Host `stop`은 해당 Host 세대 닫힘/재개 가능, native `process-ended`는 해당 start slot 종료, v58 `execution-stop`은 전체 terminal로 분리 |
| 2 비순환 결속·소비 주체 | revise | 아래 DAG와 trusted Host의 cross-journal 단회 소비를 고정. C/D test batch ID6는 live 배정과 별개 |
| 3 미지원 거절 시점 | revise | capability/import 사전 점검 → profile admission → child reservation 소비. 소비 뒤 실패는 consumed/Hold, 환불0 |
| 4 proxy 수명 | revise | proxy1개를 두 native start가 공유. 첫 slot 종료에서 proxy는 유지하고 마지막 전체 종료에서 proxy/controller까지 정리 |
| 5 거절 turn 종료 | revise | Host 거절을 durable 기록한 뒤 모델 응답 송신·generation2 없이 native process 종료. interrupt RPC/추가 network control0 |
| 6 두 journal crash 창 | revise | native host-dispatch 예약 → Host request/effect → Host terminal → native 연결 기록 순서. 대응 terminal 불명은 unknown/Hold |
| 7 helper 사후조건 | revise | clock 의미·기한부 잠금·발행 종류·관측 가능한 owned process 부재를 구별. 기존 Claude 신뢰/시계 의미를 바꾸지 않음 |
| 8 재사용 단위 | accept | 함수 AST/bytes와 의존 호출·worker 입력을 함께 비교. 파일 hash 변경만으로 전체 무효화하거나 과거27 PASS를 자동 재사용하지 않음 |
| 9 실제 실패 경로 배정 | revise | Python focused batch에 local Python child2개를 추가 제안. model/auth/network0, native agent0, exact child 입력·기한 고정 |
| 10 source/build 결속 | accept | Owner 승인 template 고정 뒤 Rust 수정. cargo test/build의 동일 source digest, 실패 뒤 자동 보정/recompile0 |
| 11 tool×OS×profile | accept | Codex prepared/Claude native profile을 구분하고 Windows는 둘 다 미구현·미검증으로 표시 |

### Fixed Semantics And Dependency Order

Host `stop`은 ReadOnlyHost가 현재 generation을 닫는 기존 사건이다. pending이 없고 원 config·Core snapshot·누적 budget이 일치하는 경우에만 fresh Host가 복원할 수 있다. native `process-ended`는 해당 start의 실제 process group/관측된 descendants 부재와 묶이며, 다음 slot의 선행 조건이다. v58 `execution-stop`은 전체 실행을 영구 닫고 이후 native start·Host resume·send·dispatch를 모두 거절한다. 과거1–57의 `stop` 의미나 Claude의 기존 기록은 바꾸지 않는다. 같은 event 이름을 두 journal에서 묵시적으로 대응시키지 않는다.

비순환 결속은 다음 순서로 고정한다.

```text
Owner가 승인한 template bytes (binary/source 결과 hash 없음)
 → native/Python에 template digest 고정
 → 동일 source로 test와 binary build
 → pre-consumption accounting snapshot + static input/launch-policy inventory
 → activation(template·binary/source/input·snapshot·child reservation ID·run dir·기한)
 → trusted Host ledger 소비 행(activation digest·run dir, fsync)
 → native journal anchor(activation digest·소비 행 identity)
 → runtime/proxy materialized spec(anchor digest·고정 static launch 정책 결속)
```

activation의 input identity에는 이미 존재하는 합성 입력·정적 launch-policy template만 포함한다. 뒤에서 생성하는 anchor·journal·materialized runtime/proxy spec은 포함하지 않는다. source/binary digest를 template 안에 넣거나 자신/후행 산출물의 digest를 upstream 입력으로 역참조하지 않는다. materialized spec은 고정 정책과 activation/anchor에 대조하고 자체 digest는 후행 실행 기록에 남긴다.

trusted Host가 기존 task controller lock 아래 C Codex live 배정의 child reservation을 단 한 번 소비한다. native는 해당 journal 내부의 순서·한도·재생만 검증하고, 다른 directory/journal에서 동일 activation을 다시 시작하지 못하게 하는 책임은 trusted Host ledger에 있다. native 단독으로 cross-directory replay를 막는다고 주장하지 않는다. 기존 C/D 예약 ID6는 Python test batch 한 건이며 이 live child reservation이 아니다.

Driver의 추가 소스 대조에서 native control의 허용 종류는 policy/models/accounts 세 가지였다. 따라서 첫안의 controls4를 controls6(각 start≤3)으로 보정한다. 이는 C의 원 Codex16개 배정 안의 부분 배정이며 새 endpoint를 허용하지 않는다. child 소비 시 C 가용 잔여에서 starts2/turns4/sends6/dispatch4/controls6을 즉시 차감하고, 실제 사용·예약은 구별해 기록한다. 실패·미사용 잔여도 자동 환불하지 않는다. proxy1/worker reads2/authority apply0/recovery apply0를 결속한다.

OS capability 확인·필수 module import 가능성 확인은 live reservation 소비 전에 수행한다. 그 뒤 정확한 OS/runtime/실행 profile·인증/고정 입력 admission을 확인하고 소비한다. 사전 확인이 성공해도 이후 capability가 사라지거나 drift하면 소비됨/Hold로 남긴다. OS 감지로 profile을 자동 전환하지 않는다. Windows v58과 Claude U2는 실행 전 unsupported이며 현행 macOS proof를 다른 조합에 적용하지 않는다.

두 native start는 하나의 proxy/controller를 공유한다. start1의 process-ended는 native runtime group과 관측된 owned descendants의 부재만 뜻하며 proxy는 승인된 allocation의 소유 process로 별도 추적한다. start2 전 동일 proxy identity·고정 spec·잔여·pending 부재를 확인한다. proxy 사망·재생성 필요·Host controller 사망은 Hold이며 이 배정으로 proxy 재시작하지 않는다. 마지막 `execution-stop`에서는 양 native와 proxy/controller 모두 종료·부재를 확인한다. fresh resume은 같은 살아 있는 Host control/proxy 안의 새 native process와 새 ReadOnlyHost generation이며, host crash 복구 성공을 뜻하지 않는다.

각 start는 정상 read1건(최대 generation2) 뒤 거절 turn1건(generation1만)을 수행한다. 두 start 합계 turns4/sends≤6/dispatch4, worker read2다. 거절은 Host terminal refusal을 fsync한 후 native에 tool result를 보내지 않고 해당 native process를 TERM10초→KILL10초로 종료한다. 모델 후속 송신·interrupt RPC·추가 network control은0이다. native turn은 성공으로 닫지 않고 rejected-terminated로 기록한다. runtime 종료를 기다리며 추가 send를 허용하는 grace 경로는 없다.

native `host-dispatch` 예약이 먼저 durable해져야 adapter가 ReadOnlyHost에 request를 전달한다. Host request/effect와 terminal completed/refused hash를 같은 native start/thread/turn/call·승인 input에 연결한 뒤 native journal에 결과 결속을 기록한다. native dispatch는 있는데 Host terminal 또는 그 대응 결속이 없으면 unknown으로 남겨 다음 start/효과를 막는다. Host 기록만으로 native 예약을 재구성하거나 missing을 성공으로 보정하지 않는다. 이 crash-window 판정은 pure vector로 확인하며 실제 authority recovery를 새로 수행하지 않는다.

### Minimum Helper Postconditions And Limits

| helper 책임 | 유지할 의미/검사 |
| --- | --- |
| 예산 시계 | v58의 continuous clock은 suspend 포함. 기존 Claude/ReadOnlyHost의 monotonic 및 wall deadline 조합은 그대로 유지하며 v58 clock과 같은 epoch로 취급하지 않음 |
| 잠금·journal append | 해당 operation의 deadline 이내 획득 또는 거절, 파일 identity와 단일 append/fsync 결속. 새 helper에서 무기한 대기 금지 |
| 발행 | 신규 control artifact는 exclusive no-replace. 기존 mutable checkpoint replacement는 별도 operation으로 구별. 이번 범위 밖의 acceptance publication을 전체 이식하지 않음 |
| IPC/process | 정확한 승인 channel·run 경로·소유 process만 사용. 종료 뒤 직접 child/group와 관측된 descendants의 부재를 확인하고 불명확하면 Hold |

로컬 Python `time.get_clock_info('monotonic')`는 `mach_absolute_time()`을 보고했다. Apple 문서는 [absolute clock](https://developer.apple.com/documentation/kernel/1462446-mach_absolute_time)이 수면 동안 증가하지 않고 continuous clock은 증가한다고 설명한다. 이것은 API 의미 확인이며 이번 세션에서 sleep 실험을 수행했다는 뜻이 아니다. 서로 다른 시계 의미를 Windows의 대체 API 이름만으로 동등 판정하지 않는다.

기존 Claude descendant scan은 `ps`의 parent/group와 초 단위 `lstart` 관측을 사용한다. scan 사이에 재부모화되거나 identity가 모호한 descendant의 완전 포획을 새로 입증하지 않는다. 현재 trusted-native profile의 실제 관측 범위와 이 한계를 보존한다. 범용 containment 보장을 추가하거나 과거 A 근거를 소급 확대하지 않는다. unknown이 실제 발생하면 지원된 종료로 보고하지 않는다.

재사용은 `checked_open`, `control_read`, `durable_private`, `ControllerLock`, `DocumentController` 및 worker bytes/입력의 함수·의존 호출 단위로 판정한다. wrapper 추출로 호출 경로가 바뀌면 해당 guard/journal/중단 검사를 다시 선택한다. B의27+11 결과는 당시 결과로 유지하고, 새 candidate의 상속 범위는 별도 표로 기록한다.

### Proposed B Execution Allocation

| 항목 | 정확한 제안 상한/조건 |
| --- | --- |
| source | 기존 Codex v58 전용 변경 위치 + 위 최소 OS helper/호출부 + 영향 tests. Core30·worker·sender/auth/FD 내부 보장·과거1–57 의미 유지 |
| Python focused | 추가 batch1, 실행30분. exact selected IDs·simulated count를 실행 전 고정. local Python child2개: 정상 종료1 + deadline/TERM 미응답 뒤 KILL1, 각5초 작업+10초 TERM+10초 KILL. native agent/model/auth/network0 |
| Rust focused | 추가 batch1, compilation45분 + test15분. pure journal/canary 선택. 실패 뒤 자동 재compile0 |
| executable build | 1회·60분. test와 동일 source digest·template, offline/locked, 새 task candidate output. 의존성 설치/fetch0 |
| batch 누적 | 기존7/8 사용 유지, 총 cap8→10 제안. 기존 C/D ID6 예약 유지, 새 batch ID9/10. 실패도 소비 |
| simulated 누적 추가 | Codex≤48 turns/48 dispatch, Claude≤16/16. 기존23/23 및24/24 환불0. exact assertion/사례 count가 이를 넘으면 실행 전 Hold |
| local process 추가 | 위 Python child2개만 별도 계수. 기존 도구 runtime start를 전용하지 않음. 기존 B profile의 process-fork/Python exec/same-sandbox signal 범위에서만 실행; 새 권한이 필요하면 Hold |
| review | 추가 R0는 이번1/1로 소진. 미래R1 0/2 유지. 새 static R0 자동 재호출0 |
| live/authority | 이번 B 구현·offline 결정에는0. C의 v58 child activation/live와 Claude C는 실제 source/build/검사 결과 뒤 exact launch binding으로 별도 준비. writer/authority/recovery apply0 |

두 local child는 해당 새 종료 helper의 실제 신호/부재 관측을 확인한다. ps 기반 전체 descendant 수집은 기존 실제 C 경로에 연결하고, daemon escape 방어처럼 배정되지 않은 조건은 미관측으로 남긴다. 새 unsupported/import/capability-before-consumption 검사는 synthetic selection/주입이며 실제 Windows 실행으로 보고하지 않는다.

이 배정의 예상165–310분과 stop330분(마지막20분 보존)을 유지하되 기존 B·전체 잔여가 먼저 제한한다. R0 finding 처분으로 실제 scope가 커지면 실행 전 재추정한다. 정적 검토 보정이 완료돼도 template/실행안에 대한 Owner 승인이 먼저이며, 승인한 exact template에 digest를 고정한 다음 source를 수정한다. compile 실패나 보정이 필요하면 원 결과를 보존하고 별도 재배정 전에는 source 보정 후 재compile하지 않는다.

현재 상태: Driver 보정 제안 준비, 새 runtime source/build/테스트/live0. macOS Codex v58은 구현 대기, macOS Claude는 A의 기존 제한적 feasibility+B offline 근거만 있으며 변경 후 C는 대기, 두 도구 Windows U2는 구현·검증 대기다. 전체 OS 리팩토링은 중앙 통합 후 계획에 남아 있다.
