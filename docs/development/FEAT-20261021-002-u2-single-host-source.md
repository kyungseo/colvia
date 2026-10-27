# FEAT-20261021-002 — U2 single-host source A

상태: E01 admission에서 중단, source A 미완료·결과 수락 전. Owner는2026-10-21 source A 구현·검증과 R0-002 보완안을 승인했다. F-03의 trusted Driver 중계와 F-04의 계측/순정 검증 구분을 채택했다. 후속 진행은 이 기록 하나가 소유하며 기존 계획은 검토·승인 입력으로 보존한다.

## Scope And Owner Decisions

- Driver: Codex. Reviewer: 승인된 Claude Code CLI R1 1회. Owner: 사용자.
- 승인 입력: [U2 계획과 R0-002](u2-single-host-continuous-work-plan.md#focused-execution-review-r0-002--2026-10-21), plan SHA-256=`4721ddeb2c3e8b76653fd502d3bc203b6ad6bb26a688e9d5ba3d87d76b4bfc9b`, source base=`7d012f5297de1d9a77aa0b8187406f4785221573`.
- source A: host 제한과 H01–H09 합성 검증, 최소 host/fixture/test/안내4파일, 기존 native runner의 승인된 경로·collection·누적 deadline·종료기록 보완. Core/managed runtime 무변경.
- 합성 모델 통신: 기존 ChatGPT 인증의 `gpt-6-astra/xhigh`, 대체 없음. 합성 fixture·지시·도구 결과만 전달.
- Claude R1: 기존 `claude.ai/firstParty/pro` 경로로 변경 코드·관련 계약 발췌·합성 검증 결과·실패 근거를 고정 packet으로1회 정적 검토. 실제 대상 식별정보/본문·자격 증명 제외. 범위 안 payload 변경은 별도 승인을 반복하지 않되 매회 실제 identity/auth/disclosure를 확인한다.
- H05: 정확한 S1–S5 원 ticket·상태·digest·process-group 부재가 준비되면 사람이 판단할 packet 하나로 묶는다. 지금 복구 apply는 승인되지 않았다. S0의 자동 재호출은 금지다.
- 제외: 실제 대상 실행/H10·실제 intent/grant·제품 저장소 commit/push/tag/PR/merge·설치·정책/과금 경로 변경. 합성 fixture 내부 Git 조작만 테스트 범위다. 별도 subagent 사용 승인은 없다.

## Completion And Evidence Selection

source A 결과는 H01–H09의 관측·거절·한계, 고정 focused55/예정 full701 집합 대조와 해당 검증, R1 지적 처분을 포함한다. H05의 정확한 사람 승인 관측이 없으면 해당 기준은 미완료다. source A만으로 실제 대상 H10·V26 또는 U2 전체 완료를 선언하지 않는다. host 제한을 입증하지 못하면 실제 모델 행동/authority 실행 전에 미확인으로 중단하고 남은 구현을 무작정 늘리지 않는다.

V22→H01–H03, V23→H05. V24 old/new window·draft-before-acceptance·rollback/recovery는 관련 기존 test/근거와 별도로 대조하며 focused22개로 모두 충족했다고 주장하지 않는다. 새8개 단위 test는 live host 강제의 대체 증거가 아니다.

전체 회귀는 host 경로·중단/복구의 상호작용 때문에 승인된 normal/parent-O 각1회다. 초기 적격 gate 실패로 해당 경로를 진행할 수 없으면 full을 소모해 통과처럼 꾸미지 않고 영향 검사와 미실행 사유를 기록한다. 기존 U1 원 error1과 실패·비재현의 한계는 유지하며 동일 오류도 재발하면 실패 중단한다. exact a580 managed bytes 무변경일 때만 해당 설치 근거를 범위 한정 재사용한다.

## Time And Attempts

2026-10-21 19:15:05 KST 실행 승인 시 carry는 약59.9분이다: 이전 checkpoint57.4분 + 이후 마감90.720초 + 승인 범위 정리58.839초. 전용 Owner 대기는 제외했다. 승인 이후 활동 wall time을 이어 더하며 병행 작업은 중복 산입하지 않는다.

전체 U2 예상385–535분은 판단값·과거 관측 혼합이며 누적 중단600분과 별개다. source A의 남은 실행은 host60–90 + iteration60–90 + regression125–145 + R1/정리30–45분을 기준으로 하며 실제 대상60–90분은 이번 실행에 포함하지 않는다. 입력 고정의 남은 비용을 실측으로 더한다. host 단계120분·full pair180분·전체600분 중 먼저 닿는 한도가 우선한다. full normal/O 각1회, scope 내 보정 최대2묶음, R1 1회. 추가 full·reviewer·scope 변경은 자동으로 열지 않는다.

## Progress

- 19:15 KST: Owner 승인. branch/base/dirty 상태 확인: base unchanged; 기존 index 수정과 계획 untracked만 존재. 현재 파일/retained Git history에20261021-001만 있어002를 사용한다.
- 입력 보존: 기존 실행 묶음·원문·protocol·test selection 유지. task-owned durable 실행 root와 승인/예산 입력을 만들었다. source/runtime/계정 설정은 변경하지 않았다.
- 다음: E01의 stdio handshake/effective config/관측 가능성 → 좁은 profile와 canary의 early qualification. 설치된 바이트를 바꾸지 않는다.

## Retention And Remaining Decisions

이 source worktree는 구현·R1·Owner 결과 판단의 consumer가 사용한다. private 실행 root는 승인 입력·실패/qualification 근거를 보존한다. 단계 완료마다 중복 transport/helper를 평가하고 required 원문·결과/마지막 복구 입력은 유지한다. 종료/복구 의존성을 확인하지 않은 fixture는 삭제하지 않는다. 사람 H05 exact 승인, source 결과 수락과 실제 대상/Git 판단은 구분한다.

### E01 Startup Observation And Bounded Correction

E01-001은 모델 turn0, 초기 RPC 응답 전 exit1, process group 부재로 종료됐다. `mcp_servers.openaiDeveloperDocs`의 `invalid transport`가 관측됐다. 사용자 설정을 수정하지 않고 알려진3개 MCP에 세션 전용 inert disabled stdio transport(`/usr/bin/false`, enabled=false)를 완전한 table로 전달하도록 보정한다. 기존 command/env/URL/credential을 복사하지 않는다. 이것은 기존 MCP 비활성화 목적의 보정이며 새 도구를 활성화하지 않는다. 실제 effective config에서3개 모두 비활성인지 확인하기 전 모델 turn은 금지다. 보정 묶음1/2를 사용한다.

E01-002는 MCP transport 오류를 통과한 뒤 filesystem path에서 종료됐다. 점이 있는 파일 경로를 CLI dotted key로 전달하면 경로가 분리되는 진단이 새 근거다. 같은 preflight 설정 보정 묶음 안에서 profile 전체를 하나의 TOML value로 전달하도록 고친다. 허용 경로·access는 동일하며 권한 확대는 없다. model turn0, exit1, process group 부재다.

E01-003은 초기화에 도달했지만 합성된 MCP 설정의 HTTP URL과 stdio command가 함께 남아 `url is not supported for stdio` 경고와 requirements 로드 실패로 중단됐다. App Server의 defaults fallback은 적격으로 인정하지 않는다. known public HTTP MCP는 원 transport 종류/공개 URL을 유지한 disabled table로, stdio2개는 inert command의 disabled table로 고정한다. configWarning을 즉시 거절하도록 보완한다. 사용자 설정 mutation과 모델 turn은0이다. 같은 설정 보정 묶음의 새로운 layer-merge 근거이며, 이 경로에서 무근거 반복은 허용하지 않는다.

E01-004에서 ChatGPT 인증, MCP3개 disabled, feature6개 false, web disabled, raw layer의 legacy sandbox key 부재를 관측했다. config/read의 typed response는 미설정 optional field를 null로 직렬화하므로 aggregate sandbox_mode=null 및 profile extends=null을 실제 설정으로 오판한 classifier를 보정한다. schema에 정의된 null 기본값만 정규화하며 path/access와 비-null 추가 설정은 그대로 비교한다. user config에는 enabled plugin12개가 있어, 최종 effective config에서도 이를 별도 진단한다. 이 관측만으로 실제 tool 노출 여부를 판정하지 않으며 모델 turn 전 중단 경계를 유지한다.

### E01 Plugin Boundary — Second Bounded Correction

E01-005는 정규화한 exact profile과 legacy-free raw layer 검사를 통과했지만 enabled plugin12개가 남아 중단됐다. source A의 불필요 도구 차단 목적 안에서 두 번째 보정 묶음을 사용한다: 관측한 plugin ID 목록을 private 입력에 고정하고 세션 CLI table에서만 enabled=false를 전달한다. 사용자 설정/설치 상태를 수정하지 않는다. 공식 plugin 문서는 로컬 enabled=false와 workspace-managed 정책을 구분하므로 설정값만으로 비활성화를 추정하지 않고 plugin/installed를 읽는다. 실제 disabled inventory가 확인될 때만 ephemeral thread/start와 thread MCP 목록을 관측하며 model turn은0으로 유지한다. native tool inventory를 입증하지 못하면 첫 turn 전에 중단한다.

### Host Admission Stop And Focused Evidence

E01-006: config/read의 exact profile·raw layer·MCP3·feature6·web·configured plugin 비활성 검사는 통과했다. 그러나 plugin/installed는 installed23개 중 enabled11개를 보고했다(목록 로드 오류0). 이 값은 실제 모델 tool catalog가 아니므로 실제 노출/우회가 재현됐다고 주장하지 않는다. 동시에 세션 비활성 설정만으로 plugin capability가 차단됐다고 입증할 수도 없다. 승인된 첫-turn 전 admission 기준에 따라 host 미확인으로 중단한다. thread/start·model turn·위임/복구 apply는 모두0이며 모든 E01 child process group이 종료됐다.

source A는 완료되지 않았다. H05 원 ticket이 없으므로 복구 승인 packet을 만들거나 사람 승인을 요청하지 않는다. 현재 early-stop 경계를 검증하고 승인된 R1을 수행한 뒤 남은 source 범위를 보고한다. 불명확한 capability를 무시하거나 전역 설정/설치 상태를 바꾸는 우회는 하지 않는다. 보정 묶음2/2를 사용했으며 이 검토 뒤 추가 실행/보정은 남은 판단으로 제시한다.

집중 검사는 `test_u2_host.U2HostTests.test_h03_permission_routes`1개,22subcase가 통과했다(failure/error/skip0, 본문0.015초). schema null 기본값의 동일 의미, 넓어진 파일/네트워크/상속/legacy/MCP/plugin/web 설정의 거절, 설정 경고·서버 승인 요청·잘못된 응답 ID·turn/start 금지를 검사했다. 기존 native Seatbelt policy bytes를 유지했고 run 밖 read/write·network·unlisted executable 거절 및 shell 상속8개 canary가 통과했다. runtime은 pinned final/GIL CPython3.14.7, parent/child `-I -S -B`, input drift0, process group 부재다. 이는 synthetic classifier/프로토콜 거절만의 증거이며 live H03 강제나 host qualification이 아니다.

planned8개 단위 중1개만 구현돼 현재 기본 collection 예상은694개다. 나머지 H01–H09 host/accept/recovery/iteration 경로가 admission에서 중단됐으므로 full normal/O 각1회를 아직 실행하지 않았다. 새로운 authority/runtime 동작을 완성하지 않은 preflight에 full을 소모해 전체 완료로 표시하지 않는다. full 시도는 normal0/optimized0이다. 범위/근거가 갖춰져 source A가 재개되면 기존 full 의무와 상한을 유지해 다시 선택한다. P/Q·설치 근거는 managed bytes가 바뀌지 않은 범위만 유지하며 이번의 새 qualification으로 세지 않는다.

R1은 이 부분 구현의 fail-closed 성질·검증 범위·중단 해석을 대상으로 한다. 전체 source A 또는 실제 host 적격 판정을 요청하지 않는다. 외부 전송은 이미 승인된 source 코드·계약·합성 결과만 포함하고 실제 대상 식별정보·본문은 제외한다.

## R1-001 — Partial Implementation Review And Driver Disposition

Owner가 승인한 R1 1회를 fresh Claude Code CLI session `af78b41a-b077-4a42-b9e0-3a34c150d585`에서 수행했다. actual model=`claude-opus-5-5`, 인증/과금 경로=`claude.ai/firstParty/pro`,8개 override 없음,208.957초,exit0,tool/MCP 사용0,process group 부재다.26개 입력의 실행 전후 drift는0이다. source base는 위와 같다. untracked host/fixture/test/안내/기록도 명시적으로 전달했다. packet115785bytes SHA-256=`2e4f6661adf4ad572fa00b2a90f67ae514eacbd2477ff025fc63a75878461f1e`;응답18383bytes SHA-256=`96426aa21b128a0159af56945dd2bfe2ff9865e274534ce3972d9279c72288aa`다.

원문은 기존 비공개 실행 묶음에 bytes 그대로 보존했다. 원문에 로컬 plugin 식별자가 포함돼 있어 public-intent source에는 복제하지 않는다. 아래는 원문 인용을 가장한 수정본이 아니라 Driver의 비식별 처분이다. source 기록은 이후 진행의 단일 owner이고 private 묶음의 원문 절은 증거 보관만 담당한다. 새 세션이지만 같은 모델 계열의 독립성·망라성을 보장하지 않는다.

### Verdict And What Remains Unknown

Reviewer는 첫 turn 전 중단을 타당하다고 보았고 현 상태의 다음 thread/turn 진행은 안전하지 않다고 지적했다. source A 완료나 host 전체 부적격을 판정하지 않았다. Driver도 source A를 미완료로 유지한다. 이번 증거는 모델 tool 노출/우회 재현이 아니다.

중요한 대안 가설: config에서 고정한12개가 설치23개 전체를 포함하지 않아 나머지11개가 기본 활성일 수 있다. 숫자23−12=11만 맞는 추론이며 현재 count만으로는 입증되지 않았다. 따라서 “session disabled 설정이 적용되지 않았다”는 원인 확정은 하지 않는다. 현재 입증된 것은 config 검사 후 plugin/installed가 enabled11개를 보고했고 이 admission에서 멈췄다는 점이다. 보정 판단에는 installed ID와 frozen ID를 메모리에서 대조한 집합 count가 필요하다.

### Findings

| ID / severity | Driver 처분 | 현재 결론·다음 범위 |
| --- | --- | --- |
| F1 High — inventory schema 누락 | accept | 필수 container/항목/boolean 형식을 엄격히 확인해야 한다. 누락·비정형을0으로 만들 수 있는 현 코드의 공백을 인정한다. 실제 응답에서 이 결함이 재현된 것은 아니다. 다음 thread 전에 보정·negative test 필요 |
| F2 High — 실행성 config 누락 | revise | notify/hooks/memories/env/provider/base URL/instructions/tools와 허용 feature 집합의 명시적 admission이 필요하다. unrelated 표시 설정까지 복사해 거대한 정책 장부를 만들기보다 실행·전달·권한 관련 집합을 닫고 미지 실행성 설정을 거절하는 범위로 구체화한다. 현 reasons=[]는 전체 config 안전 판정이 아니다 |
| F3 High — host 환경 전체 상속 | accept | 명시적 child env allowlist와 key-only 기록, synthetic sentinel 거절 검사가 필요하다. 현재 첫 turn은0이며 실제 credential 전달/노출을 재현했다고 주장하지 않는다 |
| F4 Medium — plugin 목록 모집단 | accept / needs-user | config12개와 installed23개의 차집합 가설을 읽기 전용1회로 판별하는 최소 후속안을 권고한다. ID는 private memory에서 비교하고 교집합·차집합 count만 남긴다. 새 실행은 아래 bound 결정 후 |
| F5 Medium — packet 비식별 누락 | accept | stderr의 plugin manifest 경로에 이름1개가 남아 전송됐다. “plugin 식별자 생략”이라는 설명과 불일치다. 실제 대상 본문·자격 증명은 포함하지 않았다. 이미 보낸 자료를 되돌렸다고 주장하지 않는다. 향후 stderr/argv에서 path뿐 아니라 plugin/marketplace 이름을 검사한다 |
| F6 Medium — 늦은 warning/notification | accept | response 뒤 warning drain과 stderr defaults/error 처리, notification별 expected state가 필요하다. remoteControl 이벤트의 존재만으로 원격제어 활성이라고 단정하지 않는다 |
| F7 Medium — null 정규화 | revise / defend | 이는 schema 표현 비교를 위한 classifier/oracle 변경임을 명시한다. 실제 OS 권한 동등성의 증거로 승격하지 않는다. 기존 기록의 config 비교 통과만 유지하며 runtime roots·effective policy·canary는 미검증이다. H03 canary는 원 source A 범위에 있었으나 admission 중단으로 미실행이며, 범위 밖이라서 빠진 것이 아니다 |
| F8 Medium — group과 descendant | defend / revise | 현재 source 기록은 process group 부재만 주장했으며 detached descendant 전체 종료를 입증하지 않았다. thread/helper 실행을 재개할 때는 descendant 추적/회수 또는 주장 범위의 명시적 제한이 필요하다 |
| F9 Medium — 보정/시간 경계 | needs-user | 실제 E01 시작6회, Driver 기록상 설정 보정1묶음과 plugin 보정1묶음이다. 묶음당 시작 횟수와 oracle 변경 포함 여부가 사전에 충분히 닫히지 않은 공백을 인정한다. 이를 소급해 자동 승인됐다고 확정하지 않는다. 아래 실제 시간과 다음 명시적 횟수를 제시하며 현재 추가 실행은 중단한다 |
| F10 Low/Medium — preflight 최소권한 | revise | unused model/list, 아직 불필요한 dynamic accept, MCP nonempty/pagination의 거절 공백은 다음 보정 대상이다. experimental opt-in은 named permissions 등 승인된 schema 관측에 필요한 부분을 분리해 설명해야 한다. 다음 최소 진단에서는 thread/start 자체를 제외한다 |
| F11 Medium — 검사 공백 | accept | 현재22subcase는 유의미하지만 inventory/argv/env/hash/deadline/cleanup/late-notification을 검증하지 않는다. 해당 필요한 negative test만 추가하는 후속 범위를 제안한다. runner canary를 App Server sandbox 증거로 쓰지 않는다 |
| F12 Low — runner 종료 race | accept | TERM/KILL 사이 group 소멸로 completion이 누락될 수 있는 정적 공백이다. 다음 runner 보정에서 ProcessLookupError를 부재로 처리하고 종료 경로 기록을 확인한다. 이번 집중 실행은 자연 종료·completion 존재·group 부재였고 이 race는 재현하지 않았다 |

F1/F2/F3/F6/F10/F11의 실제 보정은 아직 하지 않았다. R1 이후 code·fixture·test·runner는 그대로이며 이 기록에 처분만 추가했다. required findings가 남아 있어 R1을 PASS/전체 수락으로 표시하지 않는다. Reviewer가 개별 synthetic 검사를 “별도 승인”이라고 표현한 것은 그 검사 자체가 원 범위 밖이라는 뜻으로 채택하지 않는다. 현재 추가 판단이 필요한 이유는 보정 한도 사용과 미확정 admission 의미다. H03 실제 강제와 H05 원 ticket 승인은 그대로 유지한다.

### Proposed Next Bounded Diagnostic — Not Authorized

권고는 원인 판별만 하는 짧은 후속이다. 예상10–15분(판단값), 누적 중단20분이며 기존600분 잔여 안에 포함한다. 준비·검사·App Server 대기·종료·보고를 포함하고 전용 Owner 대기는 제외한다. 다음 실행은 최대1회로 고정하고, 실패하면 반복하지 않는다.

- 입력: 현재 pinned CLI/Python, exact worker profile, frozen12개 ID의 기존 private 입력. 기존 계정 경로 유지, API/provider override·credential 복제·CODEX_HOME 교체 없음.
- 실행: thread/start/turn/start 없이 initialize → config/read(includeLayers=true) → plugin/installed만 읽는다. Driver env 전체를 상속하지 않는 명시적 최소 env와 task-local temp를 사용한다. config/설치 상태 mutation 없음.
- 처리: response shape를 엄격히 검사하고 installed/enabled/frozen ID를 메모리에서 대조한다. 기록은 enabled∩frozen, enabled−frozen, frozen−installed count와 caller/cwd/config-layer identity뿐이다. private ID는 모델이나 외부 reviewer에게 전송하지 않는다.
- 해석: enabled−frozen만 있으면 고정 목록의 누락을 지지한다. enabled∩frozen이 있어도 API가 전역 설치 상태인지 thread capability인지 아직 확인되지 않았으므로 세션 비활성 실패나 tool 노출로 확정하지 않는다. 원문의 그 확정 제안은 이 한계 때문에 채택하지 않는다.
- 종료: 실제 process/group 종료와 결과를 보존한 뒤 정지한다. 이 진단이 성공해도 자동으로 host/thread/model/H05를 재개하지 않는다. 결과를 바탕으로 F1–F12 중 필요한 구현 보정과 첫-turn 전 tool 관측 가능성을 하나의 새 bounded안으로 제시한다. 새 R1 호출은 포함하지 않는다.

이 제안은 별도 CODEX_HOME이나 인증 복제보다 먼저 필요한 최소 판별이다. 완전한 native tool inventory를 얻을 수 없으면 그 사실을 유지하고 관측 기준 변경은 Owner 결정으로 남긴다. F-04는 Core 장애 주입과 순정 replay의 근거 구분이며, 첫 model turn 전에 필요한 admission을 면제하는 조항이 아니다. 두 기준을 혼용하지 않는다.

### Record Validation And Retention

R1 직전 source 문서3개 local link51개·GFM 렌더 오류0, 새5파일 whitespace/disclosure 검사0, Core/managed runtime diff0을 확인했다. 테스트 및 reviewer 입력의 drift는0이다. R1 뒤 변경은 상태·원문 보존·지적 처분·시간 기록뿐이다.

source worktree와4개 구현/검사 파일은 미완료 source A의 구체적인 후속 소비자가 있으므로 유지한다. private E01 결과와 최소 native 검사 근거는 원인 판별/재개 입력이다. R1 원문은 기존 private 묶음에 보존한다. 전송 packet은 F5 누락을 Owner가 판단할 때까지 정확한 전송 내용 확인용으로 유지하고, 나머지 중복 stream/controller/응답은 이관 검증 뒤 정리한다. active path 이동이나 제품 Git 변경은 없다.

### Suspension Checkpoint — 2026-10-21 19:45:23 KST

이번 실행 승인 후 이 checkpoint까지 활동 약30.3분, 이전 사용량을 합쳐 누적 약90.2분/600분, 잔여 약509.8분이다. 전용 Owner 대기는 없었고 R1의208.957초도 병행 wall time으로 한 번만 포함했다. E01 초기 준비부터 마지막 admission 중단까지 host 단계는 약14.9분/120분이었다. 기록된 E01 시작6회·보정 묶음2/2·R1 1/1·full normal0/1·parent-O0/1이다. 이 checkpoint 뒤 최종 문서 검사는 다음 재개 때 이어 계산한다.

기존385–535분 완주 예상은 현재 admission 공백으로 유효한 완료 예측으로 사용할 수 없다. 먼저 위10–15분 예상/20분 상한의 읽기 전용1회 진단안을 Owner가 판단해야 한다. 잔여600분은 자동 추가 실행 권한이나 완주 보장이 아니다. H05 packet은0개이고 실제 대상/제품 Git 작업도0이다.

정리: R1 중복 stream·stderr·응답·일회 controller·attempt5파일과 재사용하지 않는 합성 read canary1개를 삭제했다. 집중 run의 empty HOME/XDG/TMP 디렉터리도 비어 있음을 확인한 뒤 제거했다. 원문은 private 실행 묶음, 정확한 전송 packet은 F5 Owner 판단, E01 runs는 plugin 집합 진단과 argv/config negative case 작성, native 검사 결과는 source A 재개 검증의 consumer가 보존한다. 각 원인이 후속 검사로 정리되면 해당 오래된 E01 transport부터 재평가한다. worktree·코드·입력 경로는 유지했고 이동/retarget하지 않았다. source A 결과 수락이나 완료 처리는 하지 않았다.


### Authorized Read-Only Diagnostic 001 — Stopped Without Comparison

Owner가 2026-10-21 19:59:32 KST에 기존600분 잔여 안의 최대20분 읽기 전용 진단1회를 승인했다. 모델·thread 시작, H05 복구, 실제 대상 실행과 Git 작업은 제외했고 결과 보고 후 정지하도록 지정했다. 앞의 Not Authorized 제안은 이 범위에서만 승인되었다.

App Server 시작1회, initialize 성공 뒤 config/read 응답 대기 중 허용하지 않은 서버 알림을 받아 중단했다. plugin/installed는 호출하지 못했으므로 enabled∩frozen, enabled−frozen, frozen−installed는 모두 unavailable이다. 알림 종류와 본문을 보존하지 않은 진단 도구의 한계 때문에 원인을 분류할 수 없다. 기존23/11 수치를 새 집합 비교 결과로 재사용하지 않으며 session override 실패·runtime tool 노출·host 미지원으로 단정하지 않는다.

집합 비교1개와 잘못된/모호한 응답9개 검사는 통과했지만 실제 알림 경로 검증은 아니다. 프로세스 exit0·group 부재, 사용자 config.toml 바이트 불변, 입력/controller 불변을 확인했다. thread/model0, H05/실제 대상/Git0, 재시도0, 추가 reviewer0이다. 기존 보정2/2와 R1 1/1은 그대로이며 source A는 미완료·중단 상태다.

검증 checkpoint까지 이번4.27분/20분, 누적96.29분/600분, 잔여503.71분이다. Owner 대기를 제외했고 준비·실행·결과 기록을 포함한다. 최종 종료 시간은 private budget에 이어 기록한다. 실행 전 승인 파일은 저장했지만 budget 상대경로 계산이 실패해 실행 후 기존 carry로 복구했다. 승인된 시작 횟수나 상한은 늘리지 않았다.

private execution/plugin-set-diagnostic-001에 정확한 controller·승인·검사·시작·결과·검증 기록을 보존했다. 후속 원인 판별과 Owner 판단이 소비자이며, 그 판단 뒤 보존 필요를 재평가한다. 원문 stderr/plugin ID의 새 저장·외부 전송은 없고 빈 task tmp 디렉터리만 삭제했다. 기존 활성 경로는 유지했다. 승인된1회를 소진했고 추가 실행 없이 정지한다.


### Authorized Read-Only Diagnostic 002 — Notification Routing Mismatch

Owner는 2026-10-21 20:06:14 KST에 알림 종류와 비민감 메타데이터를 남기는 도구 보완 및 추가 읽기 전용 진단1회를 승인했다. 기존600분 잔여 안에서 최대20분이며 모델·thread/H05/실제 대상/Git은 제외하고 보고 후 정지하는 범위다.

새 task-private 진단 도구는 frozen protocol 알림85종과 필드 이름을 바탕으로 알림 이름·시각·대기 RPC·요청 여부·값 타입/길이·고정 경고 분류만 거절 전에 보존한다. 임의 본문·경로·식별자 값은 남기지 않고 이전 도구의 허용/거절 기준은 유지했다. 기존 inventory 검사10개와 추가 metadata/redaction/refusal6개·분류1개 합계17개가 통과했다.

App Server 추가1회에서 initialize 성공 뒤 config/read 대기 중 remoteControl/status/changed를 받았다. 기존 허용 이름 remoteControl/status와 달라 거절했다. 이번 원인은 진단 도구의 notification routing 불일치로 확인됐고, 알림 메타데이터를 private notification-001.json과 result.json에 보존했다. status와 원격 식별자의 실제 값은 저장하지 않았으므로 원격 제어 활성 여부는 판정하지 않는다. 이 알림은 configWarning이 아니지만 설정 경고 전체의 부재를 뜻하지 않는다. 진단001의 알림 종류는 여전히 미확정이며 소급 재분류하지 않는다.

plugin/installed 미호출이므로 enabled∩frozen, enabled−frozen, frozen−installed는 unavailable이다. 실제 config 결과나 tool 노출/차단 성공으로 확대하지 않는다. 프로세스 exit0·group 부재, 사용자 config.toml 바이트 불변, frozen 입력/controller/schema 불변을 확인했다. 재시도0, 모델·thread/H05/실제 대상/Git/reviewer0이다.

검증 checkpoint까지 이번2.97분/20분, 누적99.92분/600분, 잔여500.08분이며 전용 Owner 대기를 제외했다. 최종 보고 준비 시간은 private budget에 이어 기록한다. private execution/plugin-set-diagnostic-002의 exact 도구·schema projection·승인·검사·실행·metadata·결과를 Owner 후속 판단용으로 보존하며 판단 뒤 재평가한다. 빈 task tmp 디렉터리만 삭제했고 이전 진단과 활성 source/evidence 경로는 그대로다. 추가1회를 소진하여 정지한다. source A는 미완료·중단 상태이며 기존 보정2/2·R1 1/1은 그대로다.


### Authorized Read-Only Diagnostic 003 — Remote Status Handled, Inventory Unavailable

Owner는 2026-10-21 20:12:17 KST에 실제 remoteControl/status/changed 처리로 도구를 수정하고, 다른 중단 기준을 유지한 추가 읽기 전용1회를 승인했다. 기존600분 잔여 안의 최대20분이며 모델·thread/H05/실제 대상/Git은 제외하고 비교 결과 보고 후 정지하는 범위다.

진단 도구에서 알림 처리·metadata enum의 이름만 실제 프로토콜로 수정했다. inventory10개, 알림 기록/수락/거절8개, 경고 분류1개 합계19개가 통과했다. 새 이름 수락, 옛 이름 거절, 새 이름을 사용한 server request 거절을 포함한다. 실제 App Server1회에서 initialize 성공 뒤 config/read 대기 중 remoteControl/status/changed를 처리했고 보고된 상태는 disabled였다. config/read에서 frozen12개 plugin 설정이 모두 enabled=false임을 확인했다.

plugin/installed 요청 후 응답 대기 중 account/updated notification을 받아 기존 거절 규칙에 따라 종료했다. authMode/planType은 문자열 타입·길이만 기록하고 실제 값은 남기지 않았다. 이 알림만으로 인증 실패라고 해석하지 않는다. 설치 목록 응답을 수락하지 못했으므로 enabled∩frozen, enabled−frozen, frozen−installed는 모두 unavailable이다. 설정상12개 비활성을 실제 설치/런타임 도구 차단으로 확대하지 않고 기존23/11 관측을 현재 비교로 재사용하지 않는다.

재시도0, 모델·thread/H05/실제 대상/Git/reviewer0이며 process exit0·group 부재와 config.toml 바이트 불변, controller/spec/schema 불변을 확인했다. checkpoint까지 이번1.93분/20분, 누적102.46분/600분, 잔여497.54분이다. Owner 대기를 제외하고 최종 보고 준비는 private budget에 이어 기록한다.

private execution/plugin-set-diagnostic-003의 exact 도구·schema projection·승인·검사·실행·알림 metadata2건·결과·검증은 Owner 후속 판단용으로 보존하고 판단 뒤 재평가한다. 빈 task tmp 디렉터리만 삭제했고 이전 진단 및 활성 경로는 유지했다. 승인된1회를 소진해 추가 실행 없이 정지하며 source A는 미완료·중단 상태다. 기존 보정2/2와 R1 1/1은 그대로다.


### Authorized Read-Only Diagnostic 004 — Plugin Set Comparison Completed

Owner는 2026-10-21 20:16:16 KST에 account/updated도 비민감 metadata만 기록하고 계속 진행하도록 수정한 뒤, 다른 중단 기준을 유지하여 읽기 전용 추가1회를 수행하도록 승인했다. 기존600분 잔여 안의 최대20분이며 모델·thread/H05/실제 대상/Git은 제외하고 비교 결과 보고 후 정지하는 범위다.

account/updated notification만 허용에 추가했다. 해당 authMode/planType은 타입·길이만 기록하며 값은 남기지 않는다. 같은 이름의 server request는 여전히 거절한다. inventory10개·notification10개·분류1개 합계21개 검사를 통과했다. 실제 App Server1회에서 initialize → config/read → plugin/installed 응답을 읽고 메모리 안에서 exact PluginSummary.id를 대조했다. 모든 ID가 name@marketplace.name과 일치했고 중복/load error 검사를 통과했다. raw ID는 새 evidence에 남기지 않았다.

| 비교 항목 | 개수 |
| --- | --- |
| frozen | 12 |
| installed | 23 |
| enabled installed | 11 |
| enabled∩frozen | 0 |
| enabled−frozen | 11 |
| frozen−installed | 0 |
| installed∩frozen | 12 |
| marketplace load error | 0 |

따라서 고정 목록12개가 설치 목록 전체를 포함하지 못했고, enabled로 보고된11개는 모두 그 밖에 있음을 확인했다. 고정12개는 전부 설치돼 있고 비활성으로 보고됐다. 고정12개가 catalog에서 계속 enabled였다는 주장은 이번 관측과 맞지 않는다. 이 결과는 session override의 인과적 효과나 실제 thread tool 노출/차단·sandbox 강제·host 적격을 증명하지 않는다.

remoteControl/status/changed와 account/updated 알림 각1개를 처리했고 전자는 disabled 상태를 보고했다. config/read도 고정12개 모두 enabled=false를 보고했다. 원문 본문·계정값·plugin ID의 새 저장/외부 reviewer 전송은 없고 config.toml 바이트는 불변이다. process exit0·group 부재, controller/spec/schema 불변을 재확인했다. 재시도0, 모델·thread/H05/실제 대상/Git/reviewer0이다.

checkpoint까지 이번1.85분/20분, 누적104.95분/600분, 잔여495.05분이다. 전용 Owner 대기를 제외하며 최종 보고 준비는 private budget에 이어 기록한다. private execution/plugin-set-diagnostic-004의 exact 도구·schema projection·승인·검사·실행·metadata2건·개수만 담은 비교 결과·검증은 source A 후속 Owner 판단용으로 보존한다. 이전 진단은 진단 이력과 R1/보정 묶음 판단의 근거로 유지하고 이번 관측을 수락으로 간주하지 않는다. 빈 task tmp 디렉터리만 삭제했으며 활성 경로는 그대로다.

승인된1회를 완료해 추가 실행 없이 정지한다. plugin 집합 진단 완료를 source A 구현 완료나 host admission으로 확대하지 않는다. source A는 미완료·중단 상태이며 기존 보정2/2와 R1 1/1은 그대로다.


### Authorized Read-Only Diagnostic 005 — Full Session List Applied, Enabled Zero Not Observed

Owner는 2026-10-21 20:19:59 KST에 고정 비활성 목록을 설치23개 전체로 보완하여 사용자 설정 파일 변경 없이 세션 설정에 적용하고, 기존600분 잔여 안의 최대20분 읽기 전용1회를 수행하도록 승인했다. 다른 중단 기준과 모델·thread/H05/실제 대상/Git 제외를 유지하며 enabled0 여부 보고 후 정지하는 범위다.

이전 진단은 ID 원문을 보존하지 않았으므로 local cache23개 identity와 package manifest24개의 name 일치로 후보 목록을 만들었다. 이전12개는 모두 포함됐다. 이를 설치 정본으로 단정하지 않고 실제1회에서 live installed 목록과 exact PluginSummary.id 집합이23개 전체 일치함을 확인했다. task-private23개 고정 입력은 mode0600으로 보존하고 source/보고서/외부 reviewer에는 ID를 넣지 않는다.

기존 argv의 plugin 설정 인자1개만23개 모두 enabled=false로 바꿨다. 기존21개 검사와 argv 교체5개·enabled0 비교1개 합계27개가 통과했다. App Server1회에서 initialize → config/read → plugin/installed만 읽었다. 허용된 알림2종 각1개를 비민감 metadata로 기록했다.

| 관측 항목 | 결과 |
| --- | --- |
| frozen / installed | 각각23개, exact ID 집합 일치 |
| config/read의 enabled=false | 23개 |
| plugin/installed의 enabled | 11개 |
| enabled∩frozen | 11개 |
| enabled−frozen / frozen−installed | 각각0개 |
| marketplace load error | 0개 |
| enabled=0 조건 | 미충족 |

고정 목록 누락은 해소됐지만 세션 설정 표현과 설치 catalog의 enabled 값이 다르다. 이번 결과만으로 session override 전체가 무시됐거나 실제 thread에 도구가 노출된다고 단정하지 않는다. API가 보고하는 전역 설치 상태와 세션 적용 의미는 아직 구별되지 않았다. user/system layer identity와 config.toml 바이트는 그대로이고 sessionFlags identity만 바뀌었다.

재시도0, 모델·thread/H05/실제 대상/Git/reviewer0이다. 프로세스 exit0·group 부재, controller/이전입력/신규23개입력/schema 불변을 확인했다. checkpoint까지 이번3.78분/20분, 누적109.39분/600분, 잔여490.61분이다. Owner 대기를 제외하고 최종 보고 준비는 private budget에 이어 기록한다.

private execution/plugin-set-diagnostic-005의 required23개 고정 입력(mode0600), exact 도구·schema projection·승인·검사·실행·metadata·개수만 담은 결과·검증은 source A 후속 Owner 판단용으로 보존한다. 이전 진단/R1/보정 묶음 근거는 해당 판단용으로 유지한다. 빈 task tmp 디렉터리만 삭제하고 활성 경로는 그대로다. 승인된1회를 소진해 추가 실행 없이 정지한다. source A는 미완료·중단 상태이고 host admission을 선언하지 않는다. 기존 보정2/2와 R1 1/1은 그대로다.


### Read-Only Semantics Investigation — Remote Activation And Missing Default Policy

Owner는 2026-10-21 20:28:14 KST에 기존600분 잔여 안에서 최대20분 코드·프로토콜 읽기 전용 조사만 승인했다. 추가 App Server/model/thread, 설정 변경, H05/실제 대상/Git은 제외하고 두 조회 차이를 보고한 뒤 정지하는 범위다. 반복 보완·승인 부담을 줄이라는 요청도 재확인했다.

설치0.163.0 대응 공개 source와 로컬 생성 프로토콜을 대조했다. config/read는 병합 설정을 직렬화한다. plugin/installed의 local 항목은 개별 enabled를 직접 반영하지만 remote 항목은 계정 설치 enabled와 allows_plugin 정책을 AND한다. 그 정책은 plugins._default가 없으면 true를 반환하여 기존 source/account 상태를 유지하며, _default가 있어야 개별 enabled 또는 default.enabled를 읽는다. 따라서 개별23개 false만 추가한 진단005에서 remote11개가 계속 enabled로 나오는 코드상 이유가 확인됐다. 두 API 모두 같은 종류의 최종 runtime 상태를 보고한다고 가정했던 Driver 판단을 정정한다.

기존12개는 remote-global0개, 추가11개는 전부 그 범주였고 보완23개 입력과 성공한 config key 집합 검사에 _default가 없었다. protocol 입력에는 thread id가 없으며 실제 전체 도구 노출/차단은 별도 미검증이다. 공개 tag source·schema는 설치 버전과 맞지만 native binary의 재현 빌드 동일성까지 주장하지 않는다. 수정 방향은 세션에 plugins._default.enabled=false 정책을 명시하고 진단의 정책 key와 plugin ID 집합을 분리하는 것으로 좁혀졌다. 이번 조사에서는 적용하거나 실행하지 않았다.

정상 알림 처리와 enabled 의미를 먼저 확인하지 않아 작은 보완과 승인이 연속된 것은 Driver의 진단 준비 순서 문제다. 이를 Owner가 계속 지켜보며 승인해야 할 당연한 부담으로 취급하지 않는다. 조사 결과는 private execution/plugin-enabled-semantics-001/result.md와 exact source/line evidence-index에 기록했다.

추가 App Server/model/thread0, 설정/H05/실제 대상/Git0, 테스트 실행0이다. checkpoint까지 이번8.16분/20분, 누적118.24분/600분, 잔여481.76분이며 Owner 대기는 제외했다. 최종 보고 준비는 private budget에 이어 기록한다. 필요한 source13개·프로토콜·provenance·결과를 후속 Owner 판단용으로 유지하고 결론과 무관한 다운로드 source4개만 삭제했다. 기존 진단/입력과 활성 경로는 그대로다. 추가 승인 요청이나 실행 없이 정지하며 source A는 미완료·중단 상태다.


### Authorized Read-Only Diagnostic 006 — Default Policy Added, Enabled Zero Observed

Owner의 2026-10-21 20:50:33 KST “계속해”에 따라 직전 조사에서 특정한 수정 방향의 후속 진단을 수행했다. 최대20분·App Server1회와 기존 중단 조건을 유지하고 일반 source 구현 재개/추가 reviewer/model/thread/H05/실제 대상/Git으로 확대하지 않았다.

세션 plugin 설정에 _default.enabled=false만 추가했다. 기존23개 고정 입력은 byte-identical이며 policy key와 plugin ID 집합을 분리해 검사했다. 합성34개 검사가 통과했고 실제1회에서 config/read는 기본 정책false와 개별23개false를, plugin/installed는 동일한 installed23개와 enabled0개를 보고했다. enabled∩frozen0, enabled−frozen0, frozen−installed0, marketplace load error0이다. 이전 진단005의 enabled11개가0개로 바뀌어 직전 코드 조사 설명과 일치했다.

user/system layer identity와 사용자 설정 파일 바이트는 불변이고 sessionFlags identity만 변경됐다. 허용된 remoteControl/status/changed1건을 비민감 metadata로 처리했다. 추가 모델/thread/H05/실제 대상/Git/reviewer0, 재시도0이다. exit0과 process group 부재 및 고정 입력/controller/schema 불변을 확인했다. 전체 native/tool inventory, 실제 thread 도구 차단, sandbox 강제, detached descendant 전체 부재나 host 적격은 증명하지 않는다.

checkpoint까지 이번3.36분/20분, 누적122.56분/600분, 잔여477.44분이다. 전용 Owner 대기를 제외하고 최종 보고 준비는 private budget에 이어 기록한다. private execution/plugin-set-diagnostic-006의 exact 실행 입력·결과·검증은 후속 판단용으로 유지하고 빈 tmp만 제거한다. 활성 경로는 그대로다. 이 진단을 종료하며 Source A는 미완료·중단 상태, 기존 보정2/2·R1 1/1과 미해결 검토 항목은 유지한다.


## Proposed Source A Resumption Bundle — Pending Owner Decision, 2026-10-21

Owner는 20:56 KST에 계속 진행하고 휴대폰에서 읽는 보고에 요청을 포함하도록 지시했다. Driver는 남은 source A와 소진된 보정/검토 한도를 대조해 아래 실행 묶음을 준비했다. 이번 단계는 그 요청을 구체화하는 문서 준비이며, 아래 추가 보정과 reviewer 실행을 이미 승인된 것으로 표시하지 않는다. 진단006의 plugin installed23/enabled0 결과는 유지하고 host 적격으로 확대하지 않는다.

### Closed Scope And Sequence

1. 기존4개 source 파일(host.py, tests/fixtures/u2_host.py, tests/test_u2_host.py, u2-host/README.md)과 private native runner의 필요한 부분에 R1 필수 지적을 반영한다. F1/F4는 필수 inventory shape와 정확한23개+기본 정책 검사, F2/F3은 실행성 config·instruction sources·최소 child env, F5/F6은 비식별화·알림/warning/종료 시점 처리, F8/F10은 좁은 RPC/child 종료 주장, F11/F12는 실제 결함을 검증하는 집중 negative 검사와 종료 race 기록을 맡는다. Native Codex 실행 파일까지 identity를 고정하고 wrapper hash를 native pin으로 부르지 않는다. F7은 schema 표현 비교와 OS 강제를 구분한다. F9의 과거6회/2묶음 문제는 소급 수락으로 덮지 않는다.
2. 첫 model turn 전에 지원 API·현재 유효 설정·instruction sources·전체 native/plugin/MCP tool 집합을 확인한다. 설치 catalog0이나 MCP0을 전체 tool0으로 대체하지 않는다. 관측 경로가 없으면 모델을 실행하지 않고 미확인으로 종료한다. 계측된 Core 복구 근거의 허용을 host admission 면제로 해석하지 않는다. 설정 파일 변경·CLI upgrade·외부 sandbox·새 backend·credential 복제·권한 확대는 하지 않는다.
3. 위 gate를 통과한 경우에만 기존 승인된 합성 H01–H09를 이어 구현·검증한다. 기존 ChatGPT 인증의 gpt-6-astra/xhigh만 사용하고 대체하지 않는다. H03은 합성 파일 생성/교체·alias·network·직접 우회 deny를 실제 policy로 확인한다. 합성 H04 acceptance와 H05 중단 주입은 원 승인 의미를 유지하며 authority apply 실패는 자동 retry하지 않는다. H05 S1–S5 원 ticket·상태·digest·종료 증거가 준비되면 사람이 판단할 exact packet 하나로 별도 승인 요청한다. 이 묶음은 H05 replay의 사전 승인이 아니며 S0 재호출을 허용하지 않는다. Owner 응답 대기 중에는 그 승인에 의존하지 않는 범위만 이어간다.
4. 반복 중에는 변경 위험에 맞는 집중 검사만 한다. 필요한 source 구현과 host 경로가 준비되면 고정 focused 선택과 실제 collection을 대조하고, 기존 normal/parent-O 전체 회귀 각1회(현재 각각0회)를 수행한다. planned701은 구현 후 집합 대조 대상이지 숫자를 맞추기 위한 test 추가 목표가 아니다. admission에서 멈추면 full을 소모하지 않고 미실행 사유를 기록한다. 과거 errno35 오류도 재발 시 실패로 중단한다.
5. 완성된 변경 후보와 합성 근거를 추가 Claude R1 정적 검토1회에 전달한다. 기존 claude.ai/firstParty/pro 경로를 사전 확인하고 fresh session·실제 model·입력 identity·원문·disposition을 보존한다. 전송 범위는 source 변경·필요 계약 발췌·합성 검사/실패 근거이며 실제 대상 식별정보/본문·자격 증명을 제외한다. path뿐 아니라 plugin/marketplace 식별자도 검사한다. 미해결 필수 지적이 있으면 완료/수락으로 처리하지 않는다. 별도 subagent나 추가 reviewer는 포함하지 않는다.

### New Attempt Limits Without Resetting History

이 재개에서 추가 보정은 최대2묶음이다: 첫 묶음은 위 R1 필수 지적과 진단006 정책의 통합, 둘째 묶음은 같은 scope/oracle에서 새 실행·검토 근거로 드러난 보정만이다. 기존2묶음 사용 기록은 유지한다. 보정할 때 영향 검사만 반복하며 같은 원인으로 새 근거 없이 실패하면 잔여가 있어도 중단한다. 사후에 여러 임의 변경을 한 묶음으로 재분류하지 않는다.

App Server 신규 시작은 이 재개 전체 최대4회(첫 admission/qualification용1회, 새 근거를 반영한 admission 재확인용1회, 합성 iteration용1회, H07 fresh 재개용1회)로 제한한다. 용도별 사용을 실행 전에 기록하고 실패한 용도의 여분을 자동 재시도로 전용하지 않는다. 각 preflight는5분 이내다. 모델 turn은 전체 최대8회·각15분 이내이며 합성 qualification/iteration/재개/accept에 실제 필요한 turn을 시작 전에 H case와 결속한다. 상한을 채우기 위한 실행이나 서비스 실패의 무근거 재호출은 하지 않는다. 등록할 ephemeral thread는 최대4개, thread당 권한·identity gate는 동일하다. H04–H05의 installed Core child는 App Server와 별개이고 기존 S0–S5 고정 시나리오를 따르며 H05 exact 복구는 위 사람 승인을 기다린다.

추가 R1은1회이며 기존 소진1회를 되돌리지 않는다. full normal/parent-O는 기존 미사용 각1회만 유지하고 추가 full은 열지 않는다. host120분·full pair180분·전체600분 중 해당하는 가장 짧은 잔여가 우선하며 종료/cleanup 시간도 포함한다. 한도나 contract/scope를 바꿔야 한다면 임의로 넓히지 않고 중단 보고에 요청을 넣는다.

### Estimate And Cumulative Accounting

이번 준비 checkpoint까지 누적 125.82분/600분, 전체 잔여 474.18분이다. source A 잔여 예상은 약260–360분이다. 이는 host 관련 남은 작업45–65분, same-Work 구현/합성70–105분, 최종 회귀125–145분, R1/정리20–45분을 합친 대략260–360분으로, 실측117.53분의 이전 full 두 실행 외 대부분은 판단값이다. host 관측 가능성이 아직 미확인이라 완주 예측의 신뢰는 낮고 early stop이 가능하다. 실제 대상 H10의 비용은 포함하지 않는다.

과거 host 사용14.9분만 이어 쓰면 후속 진단/원인 조사 시간이 빠지므로 보수적으로 기존 host_stage_elapsed_seconds + 진단001–006 + semantics001 + 이번 준비를 합산했다. 이 checkpoint의 host 사용은 48.67분/120분, 잔여 71.33분이다. 원래 기록을 소급 변경하지 않고 이 재개 기준으로 더 엄격하게 적용한다. 첫 model turn의 진입 가능성 판단은 재개 후 최대60분과 host 잔여 중 작은 값 안에서 끝내며, 그 뒤 H01–H05도 동일한 host 잔여 안에서만 진행한다. 위 예상의 상단보다 잔여가 작으면 예상에 맞춰 한도를 늘리지 않고 중단한다.

준비·구현·검사·서비스 대기·reviewer·기록/종료를 활동 경과시간에 포함한다. 전용 Owner 응답 대기는 제외하고 병행 wall time은 한 번만 센다. 지금의 예상은 완료 약속이 아니며 관측 비용이 달라지면 같은 기록에 재산정한다.

### Owner Request And Exclusions

요청: 위 source A 재개 묶음(추가 보정2묶음·App Server4회·thread4개·model turn8회 상한·추가 Claude R1 1회 및 명시된 전송 범위)을 기존 누적600분/host120분/full pair180분 안에서 승인할지 판단한다. Core source/managed runtime 변경, 실제 대상 실행·intent/grant 수락·제품 Git 작업·설치·정책/과금 변경은 제외한다. 기존 합성 fixture 내부 Git은 원 검증 범위다. H05 exact replay는 원 ticket packet으로 별도 승인받고 결과 수락도 사람에게 남긴다.

휴대폰 응답 예: “재개 묶음 승인. H05는 원 ticket 준비 후 한 번에 요청하고, 실제 대상과 제품 Git은 제외해.” 통상적인 범위 내 보정/집중 검사마다 다시 승인을 요구하지 않는다. 중대한 새 경계 또는 소진 한도에 닿았을 때만 이유·남은 일·요청을 함께 보고한다.

보존: 기존 source worktree와 private 실행 입력/결과는 이 재개 판단과 이후 검증의 consumer가 사용한다. 이번에는 새 실행물이나 복구 사본을 만들지 않았고 삭제/이동/활성 경로 변경도 없다. 이 제안의 승인 전에는 새 App Server/model/thread/reviewer를 시작하지 않는다.


### Owner Approval — Source A Resumption Bundle

2026-10-21 21:46:32 KST Owner가 “재개 묶음 승인”으로 위 정확한 제안을 승인했다. 이전 보정2/R1 1 기록은 유지하고 추가 보정2·R1 1·App Server4·thread4·turn8 상한을 별도로 이어 쓴다. 전체600분/host120분/full pair180분을 유지하고 첫-turn 진입 가능성은 재개 후60분 이내에 판단한다. H05 exact replay, 실제 대상/제품 Git, 결과 수락은 여전히 별도다. 첫 단계는 R1 필수 보정과 실제 관측 경로 확인이며 모델 실행 전에 해당 gate를 충족해야 한다.


### Resumption 001 — Admission Observation Unavailable, Stopped Before Execution

승인된 첫-turn 전 판별에서 로컬 experimental protocol172개 요청과0.163.0 대응 공개 source를 대조했다. thread/start 응답에는 전체 native tool catalog가 없고 fresh thread.extra는 None이며, model-visible tool specs는 TurnContext/ModelInfo/environment/MCP를 소비하는 내부 router에서 구성된다. MCP 목록·provider capability boolean·process gauge·sampling 시점 등록 metric을 전체 도구 목록으로 대체하지 않는다. 확인한 지원 표면에서 사전 관측 경로를 확보하지 못했으므로 승인된 early-stop 기준에 따라 모델 실행 전에 중단한다. 모든 host/미래 버전이 불가능하다는 결론이나 실제 노출/우회 재현은 아니다.

공개 stable와 로컬 experimental schema 전체는 같지 않다. ThreadStartResponse의 공통 shape/required는 동일하고 차이3개는 source의 experimental field였다. native 실행 파일 bytes는 이전 관측과 같지만 재현 빌드 동일성은 미증명이다. exact 근거는 private execution/resumption-001/result.md와 evidence-index에 보존했다.

새 App Server0/4·thread0/4·model turn0/8·추가 보정0/2·추가 R1 0/1·full normal0/1·parent-O0/1이다. host/fixture/test/runner source 변경, 사용자 설정, Core/managed runtime, 실제 대상/제품 Git은0이다. R1 필수 보정과 H01–H09는 남아 있으며 H05 ticket은 아직 없다. 사전 관측 가능성 확인을 초기 진단보다 앞서 하지 못한 Driver의 준비 순서 문제를 인정한다.

이번 활동 7.45분, 누적 133.27/600분, 잔여 466.73분, 보수적 host 사용 56.12/120분이다. Owner 대기는 제외했다. 조건부 실행 승인에서 first-turn gate를 통과하지 못했으므로 추가 실행은 정지한다.

다음 요청은 기준을 유지하는 대안 설계 비교 문서만이다: 현행 CLI의 요청 전 관측/검증 확장과 host가 전체 허용 도구를 직접 소유하는 별도 연결 방식을 비교해 권고1개를 제시한다. 예상20–30분/최대30분, 기존600분 잔여 안이며 구현·빌드·설치·server/model/reviewer·인증/과금·실제 대상/Git 변경은 없다. 새 구조 검토는 현재 실행 묶음의 자동 backend 전환으로 수행하지 않고 Owner 판단을 기다린다. '기준 유지, 대안 설계 비교 승인'을 간단 응답으로 제안한다.

필요 source4개와 schema/비교/identity/결과를 후속 판단용으로 유지하고 보조 source2개·공개 stable schema2개만 정리했다. 기존 recovery/evidence와 worktree는 유지하며 활성 경로는 그대로다. Source A 미완료·host 미확인 상태이고 결과 수락을 선언하지 않는다.


### Alternative Design Comparison 001 — Document Only, A Recommended

Owner가 2026-10-21 22:00:21 KST “기준 유지, 대안 설계 비교 승인”으로 최대30분 문서 비교를 승인했다. 기존600분 잔여에 포함하며 구현/빌드/설치/server/model/reviewer/인증과금/실제 대상/Git은 제외했다.

A는 기존 CLI에 첫 turn 전 immutable 도구 계획을 prepare하고 실제 요청/handler 집합에 결속하는 확장이다. 목록만 출력하는 기능은 충분하지 않으며 model-visible 도구와 실행 registry, hosted/deferred/추가 도구를 함께 닫아야 한다. 기존 ChatGPT auth와 sandbox를 재사용하는 설계이지만 수정 binary에서의 인증/정책/거절은 미검증이다. 고정 별도 runtime build와 새 qualification이 필요하고 원본 CLI를 덮어쓰지 않는다.

B는 host가 fixed tools 요청과 모든 handler dispatch를 소유하는 Responses API 연결이다. 사전 목록 통제는 단순하지만 Platform 인증/과금과 executor 격리·회수·복구를 별도 검증해야 한다. 현재 ChatGPT 구독을 일반 API 권한으로 확대하지 않으며 token 추출/복제 방식을 제안하지 않는다. SDK wrapper만 교체해 현재 App Server의 사전 관측 공백이 해소된다고 주장하지 않는다.

권고는 현재 ChatGPT 인증 유지 조건 아래 A를 별도 후속 개발안으로 선택하는 것이다. source A의 즉시 완주나 기준 완화를 권고하지 않는다. 예비 비용은 macOS/기존 Core 무변경 첫 검증 후보까지 A8–16시간, B12–24시간의 낮은 신뢰 판단값이며 source/build prototype 실측이 아니다. 구현/빌드·검사·리뷰 대기와 기록을 포함하고 Owner 대기/상류 배포/다른 OS/장기 유지보수는 제외한다. 기존 full117.53분은 회귀 참고일 뿐 신규 host 비용의 실측이 아니며,260–360분 source A 예상을 새 구조 개발에 재사용하지 않는다. 예비 범위는 실행 승인이나 중단 한도가 아니다.

private execution/alternative-design-001/result.md에 두 구조·보장/한계·근거·필요 검증과 'A 후속안 채택' 판단 요청을 남겼다. 방향 채택은 build/install/model/예산 연장 승인과 다르며 후속 최소 계약·검증·비용/상한·review를 하나의 실행안으로 제시해야 한다. 이번 비교 뒤 자동 착수하지 않는다.

이번8.19분/30분, 누적141.46/600분, 잔여458.54분이다. 공식 문서·기존 고정 source와 registry source1개만 읽었다. 구현/빌드/설치/server/model/reviewer/실제 대상/Git/credential 변경0이며 추가 실행 카운터도 그대로다. 비교/근거는 후속 판단 consumer 때문에 보존하고 이번 삭제/이동/활성 경로 변경은 없다. Source A는 미완료·중단 상태다.


### A Follow-Up Direction Adopted — Initial Proof Plan Prepared

2026-10-21 22:11:46 KST Owner가 “A 후속안 채택”으로 방향을 선택했다. 최소 계약·경로·검증·예산·review를 private execution/a-followup-plan-001/plan.md로 구체화했다. 방향 채택은 runtime 구현/설치/build/model 실행이나 결과 수락이 아니다. 새 개발 ID는 bounded 실행 승인 뒤 부여하며 기존 Source A는 미완료·중단 상태다.

첫 proof는 실제 수정 binary의 first-turn 전 prepare와 동일 immutable tool plan의 consume, registry/요청 결속, drift/reuse/우회 거절을 offline fixture로 확인한다. 기존 CLI를 교체하지 않는 별도 고정 source/build이며 실제 인증·sandbox 적격, U2 통합/H01–H09와 기존 R1 보정은 후속이다. 조사한 PATH와 기본 위치에서는 Rust 도구체인을 찾지 못했으므로 작업 전용 도구체인 설치와 격리 build 경계를 실행 제안에 포함했다. 설치나 build는 아직 하지 않았다.

첫 proof 예상4–6시간/별도 prospective 누적 상한360분이며 낮은 신뢰 판단값이다. A 전체8–16시간 예비 추정은 유지하고 남은 기존 예산으로 전체를 완주한다고 약속하지 않는다. 새 상한은 승인되지 않았고 기존600분 장부를 재설정하지 않는다. 현재 계획 준비와 다음 R0는 기존 장부 범위이며 새 proof 시작 시 이전 사용량을 보존하고 중복 계산하지 않는다.

source workflow는 R0를 실행 승인 전에 요구한다. 다음 요청은 새 Claude CLI R0 정적 검토1회, 예상10–20분/최대30분과 비식별 최소 계약/공개 source 발췌 전송이다. 기존 미사용 R1을 새 R0로 재분류하지 않는다. 검토 결과 반영 후 exact 실행 묶음을 Owner에게 제시하고 그 승인 전에는 설치/구현/build를 시작하지 않는다. 이번 reviewer/server/model/test/build/install/source 구현은0이다.

계획 checkpoint 활동4.96분, 누적146.43/600분, 잔여453.57분이다. Owner 대기는 제외한다. 계획과 기존 증거는 Owner/R0/재개 판단에 필요해 보존한다. 기존 활성 경로 변경·삭제는 없고 STATUS/typed Work/Git 변경도 없다.


### A Follow-Up R0 001 — Corrected Execution Bundle Ready

2026-10-21 22:31:04 KST Owner가 “자잘하게 요청 올리지 말고 한번에 묶어서 … A 실행안 R0 검토 승인”으로 정적 검토1회와 종합 요청 준비를 승인했다. 실제 Claude reviewer는 claude-opus-5-5, fresh session43e9dac3-c9f5-489f-882f-5ec803d8f1ed이며 기존 구독 인증 경로를 비민감 필드로 확인했다. 도구/MCP/실행0, 입력 drift0, exit0과 process group 부재를 확인했다. 원 응답은 private execution-bundle.md에 byte-identical로 import했다.

판정은 필수 보정 후 진행 가능이다. Driver는 F1–F14에 accept/revise를 기록했다. 주요 보정은 고정 approval envelope와 step별 실제 router 결속, unsupported 집합의 명시적 empty/unavailable, 중앙 method allowlist와 내부 sampling guard, fixture bootstrap의 명시적 config root, macOS default-deny build/test profile과 첫 build 전 canary, process 시작부터 부작용 측정, production wire의 독립 mock 대조다. handler descriptor만으로 다른 handler 선택을 놓치지 않도록 좁은 registration binding 검사도 포함한다.

private execution/a-followup-r0-001/execution-proposal.md에 설치·별도 checkout·최소 구현·offline 검사·보정2묶음·R1최대2회(필요한 수정 후 재검토 포함)를 하나로 묶었다. 초기 proof 예상은 cold build와 필수 보정을 반영해6–10시간으로 재산정했고, 별도 prospective 중단 상한10시간을 제안한다. 최초90분 bootstrap 판별과 안전 실패 조기 중단은 유지한다. 초기4–6시간/6시간 상한은 미승인 제안이었으며 현재 제안으로 대체하고 소급 승인/증액으로 처리하지 않는다.

이번 새600분은 기존 U2누적600분과 별도 승인 대상이다. 기존 사용량을 초기화하거나 기존 한도 안이라고 표현하지 않는다. 새로운 proof 실행 시 두 기록을 연결하고 중복 합산하지 않는다. 전체A8–16시간은 이전 예비치이며 현재 완주 약속으로 쓰지 않고 live qualification/기존 Source A 잔여는 새 증거 후 재산정한다.

통상 단계 전환/국소 보정/집중 검사와 묶음 안의 R1 후속마다 재승인을 요청하지 않는다. scope·권한·안전·시간/시도 한도·결과 수락 경계에서만 요청을 묶는다. 지금은 R0만 완료했고 설치/구현/build/실제 model/provider/기존 host 수정/실제 대상/Git commit 등은0이다. 새 개발 ID·typed Work·STATUS 변경도 없다. 보정본은 Driver가 작성했으며 Reviewer 재검토 또는 Owner 실행 승인으로 표시하지 않는다.

이번 활동15.36분/30분, 기존 누적161.79/600분, 잔여438.21분이다. 원 검토와 packet/metadata·고정 source 발췌·보정 제안은 Owner 실행 판단과 다음 구현의 consumer가 사용한다. 기존 checkout/recovery/활성 경로는 유지한다.

R0 closeout: 원 응답/대응을 기존 private record에서 바이트/문구 대조한 뒤 중복 response·raw stream·빈 stderr·1회 controller/attempt·중복 disposition JSON과 빈 tmp를 정리했다. request/metadata/통합 제안과 필요한 공개 고정 source 자료는 Owner 판단 및 다음 구현이 사용하므로 유지한다. 기존 활성 경로 변경은 없다. 문서 검사와 git diff --check가 통과했다. 정리까지 이번16.60분, 기존 누적163.03/600분, 잔여436.97분이다.


### Prepared Plan Proof Execution Approved

2026-10-21 22:58:56 KST Owner가 통합 실행안을 승인했다. 새 offline runtime proof는 [FEAT-20261021-003](FEAT-20261021-003-prepared-tool-plan-proof.md)이 단독 진행 기록을 소유한다. 본 Source A의 host/R1/H01–H09 잔여는 중단 상태로 유지하며 새600분 실행 한도를 본 기록의 예산 재설정이나 본 결과 수락으로 해석하지 않는다.

## Integrated Execution Handoff — 2026-10-22

Owner가 최종 live/U2 통합 실행안을 승인하여 미완료 host/H01–H10 후속 진행을 [FEAT-20261022-001](FEAT-20261022-001-prepared-tool-plan-live-qualification.md#owner-approved-integrated-execution--2026-10-22)로 넘겼다. 이 기록의 원 승인·검토·실패/부분 근거는 그대로 보존한다. 기존 U2 누적9781.67초(163.03분; host 사용56.12분 포함)는 새 실행 장부에서도 유지한다. source 결과/실제 H10 수락 또는 기존 미해결 finding closure를 뜻하지 않는다. 새 전체16시간은 통합안 R0/보정905.507초부터 포함하며 기존600/host120 잔여를 암묵 초기화한 것이 아니다. 실제 프로젝트 Work는 해당 프로젝트의 exact 승인/예산을 계속 소유한다.
