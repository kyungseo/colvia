# Rule Entry, Document Language And Activation Preparation

Publication copy: this version replaces only identifying local paths and external repository names with repository-relative paths or neutral labels. The exact pre-publication source bytes (SHA-256 `91d12a2d0c11839c4e7dfdaab4ab77e501b0ecdf350be6011da785718f912bd0`) and original review records remain privately retained. Neutral labels are provenance locators, not executable paths; accepted scope, decisions, evidence counts and limitations are unchanged.

- ID: CHORE-20261018-001.
- Status: Done — Owner가 2026-10-18 A 결과를 수락했다. 실제 활성화·Git·adopter 적용은 계속 보류한다.
- Actual end: 2026-10-18.
- Date: 2026-10-18.
- Roles: human Owner, Codex Driver, Claude Code Reviewer. 실제 호출의 모델/session/auth 경로는 각 결과에 기록한다.
- Scope: L2 / Standard Work. A의 최소 지침 보정과 delegation-1 활성화 준비·필요한 검증·최종 R1까지다. 실제 활성화, Git publication, 실제 adopter 적용은 별도 Owner 결정이다.

## Authorization And Ownership

> 제안한 범위로 진행해. 최신 main의 source 문서와 정합하고, A 최소 보정·활성화 준비·필요한 검증을 묶어 R0부터 최종 R1까지 이어가. 기존 증거를 재사용하고 작은 수정마다 전수 검증이나 승인을 반복하지 마. 실제 활성화·Git·adopter 적용은 결과를 보고 별도로 결정할게.

Owner는 [M1/M2 결과와 A 계획](FEAT-20261016-001-delegated-ordinary-acceptance.md#owner-result-acceptance-and-a-planning-proposal--2026-10-18)의 범위를 승인했다. 그 입력 문서 SHA-256은 `c6d84ebf3e7400a4414b35153be5cee22de5b80764455d13f223173bfd49af5e`다. M1/M2 결과 수락은 이미 완료됐고 이 기록이 A의 유일한 진행 소유자다. 기존 완료 결과를 다시 Active로 만들거나 runtime Work/intent를 생성하지 않는다. review verdict는 Owner 결과 수락이나 계약 활성화를 대신하지 않는다.

이번 승인에는 R0와 최종 R1, 범위 내 보정·필요한 재검증, 아래 synthetic reader 관찰이 포함된다. 작은 수정마다 승인을 다시 요청하지 않는다. 범위·권한 의미·실행 경계가 달라지면 영향을 보고하고 해당 확대를 별도 결정한다. Driver 정적 판단, 실제 테스트, reviewer 판단과 실제 Owner 결정을 구분한다.

## Starting Inputs And Source Alignment

- 작업 branch/HEAD: `codex/colvia-agent-delegation-m0-20261016` / `d86bd1fd7754144e5c8538712724ae78571941bf`; 고유 미커밋 M1/M2 결과를 보존한다.
- 읽기 전용으로 확인한 remote main: `a93f71c359c4f0a9d57fcfb50d5999160e870f77`, open PR0. main의 source-only6개 변경을 작업 파일에 반영한다. Git HEAD/index/refs/history는 변경하지 않는다.
- 정합 대상: CONTRIBUTING, DECISION-GUIDE, development/WORKFLOW, development/README, DR-0006, CHORE-20261016-002. index에는 기존 FEAT와 이번 CHORE 링크를 보존·추가하고 승인된 criteria를 바꾸지 않는다.
- DR-0006이 source 규칙의 분리와 위치 변경을 이미 발효했다. A는 이를 재사용하며 AGENTS-only 진입의 남은 연결과 저장 문서 언어를 보완한다. source-only 문서가 managed29에 들어가지 않는 경계는 유지한다.
- M1/M2 anchor: frozen source `47d438671fe7752e37279b8bec4ce584def25ee8958ca9d8673eb56a44834332`; P `d4dd27cf8c98be1cd321b02d2dae62c9c6d2ff344ffa7034a5dd12a6df955526`, Q `d97b7c82cd65557a2f107a57b6ac613e82ab7efcae8d9e159524697a51718bbc`; final R1-006 Blocker0·필수수정0과 비차단7건 처분은 기존 기록에 있다.
- Technical contract는 여전히 DR-0004의 exact entry-1이다. DR-0005는 Draft이며 이번 편집으로 발효되지 않는다.

Source의 entry, [Workflow](WORKFLOW.md), [Decision Guide](../DECISION-GUIDE.md), [Maintaining](../MAINTAINING.md)가 적용된다. 별도 path-scoped tool rule은 없다. 상위 조정 저장소 STATUS를 갱신하거나 다른 저장소의 언어 정책을 가져오지 않는다. roadmap·서비스·infra·DB 변경은 없다. 이번 Owner용 계획·진행·결과는 한국어, 기존 shipped 안내는 영어를 유지하며 새 언어 선택 지침은 project 산출물에 적용한다.

## Scope And Invariants

| 대상 | 승인된 최소 변경 |
| --- | --- |
| AGENTS Start와 CLAUDE thin entry | 명시된 source 개발과 installed project의 진입을 구별한다. source에서 기존 CONTRIBUTING 경로를 찾되 설치 payload에 없는 source-only 문서를 요구하지 않는다. tool-specific 파일에 별도 정책을 복제하지 않는다. |
| Reference Repository-Owned Rules / Human Review / 작성 안내 | 독자·용도를 먼저 확인하고 문서 언어를 명시 요청 → project 규칙 → 대화 언어 순으로 선택한다. 배포/계약 언어 충돌, local override, rule provenance와 권한 경계를 유지한다. |
| Getting Started와 adapter | source/installed 경로, 신규·기존 project의 안정적 pointer와 local rule 보존을 기존 예시에 연결한다. 영어 template/diagnostic label만으로 산출물 언어를 정하지 않는다. |
| Maintaining, CAPABILITIES, DR-0005 | 낡은 campaign 상한·미실행 claim을 현행 결과와 구분한다. exact successor 조항·바이트·증거를 준비한다. M1/M2 결과 수락, A 검증, 미활성 계약을 분리한다. |
| README/index 및 관련 current-candidate 안내 | delegation-1/schema4 후보의 현재 안내를 일관되게 만들되 entry-1 유효 계약과 역사·predecessor·단방향 전환 의미를 보존한다. 기술 계약11개와 entry/설명/data6개를 점검하고 필요한 span만 고친다. |

불변 조건: 제품 executable/schema/권한/기록/복구 의미, managed membership29, 기존 exact predecessor, 승인·취소·거부·재바인딩 경계, project truth/local override, 역사 원문, actor가 인증이 아니라는 제한. Source 개발의 결과 수락은 human Owner다. Source instruction을 설치 project root에 복사하거나 Core 자동 로더·언어 field·rule registry를 추가하지 않는다. B, 실행기 재설계, 전면 번역, licensing/public contribution, 실제 adopter 변경은 제외한다.

문구 보정은 reader가 현재 단계에서 해야 할 행동을 명확하게 하는 span으로 한정한다. 안내의 순서가 필요한 경고를 뒤로 밀지 않게 하고, 명령·식별자·조건·예외·수치·역사적 인용을 보존한다. 읽는 사람의 이해를 실제로 관찰한 결과와 정적 문구 판단을 구별한다.

## Verification And Evidence Reuse

재사용 판단은 r11 anchor 이후의 누적 변경을 대상으로 한다. 다른 source-only 문서의 정합 및 shipped prose 변경은 새 release digest를 만들지만 그 자체가 656×2 재실행 이유는 아니다. 제품 실행 bytes, 관련 test/fixture/controls/runtime·환경을 대조해 기존 결과가 다루는 동작을 확인한다. 변경된 테스트나 도구의 결과를 과거 실행으로 표시하지 않는다.

| 검사 | 범위와 판정 |
| --- | --- |
| 정적·배포 정합 | GFM와 local link/anchor, JSON claim, diff whitespace, 29개 inventory bytes/mode/digest, source-only 문서 비배포, current/legacy 안내 및 exact 조항 범위. AGENTS≤2000, AGENTS+README+Getting Started≤4000 tokens도 측정한다. |
| CLI 진입·resume | HumanViewInstalledTests의 `test_empty_actual_source_installed_and_git_are_read_only`, `test_p_q_p_uses_current_adapter_path_and_detach_remains_readable`를 normal/parent-O로 확인한다. 이4개 실행은 path/readonly 확인이며 실제 agent 이해 증거가 아니다. |
| 실제 reader5개 | R-A source의 AGENTS만으로 source 절차 진입, R-B 신규 설치 project의 한국어 요청→한국어 계획, R-C 명시적 영어 요청→영어 문서, R-D 별도 요청 없는 project 언어 규칙, R-E 기존 project의 unique rule/override 보존·현재 adapter 진입/재개. 읽기 도구와 합성 fixture만 허용하고 생성 결과는 지정 output에 저장한다. 실제 adopter·일반 host 품질은 미검증이다. |
| exact-artifact | 최종 입력 고정 뒤 기존 C01–C16 전부를 normal 모드로1회 실행한다. exact entry-1→A, 새 Git/non-Git init, same-window P/Q 왕복, repair/detach·중단 prefix, plain reader, inventory와 truth 보존을 확인한다. Q에는 r11의 수락된 P를 사용해 새 후보와 실제 retained 후보를 비교한다. 기존 입력 제약은 R0에서 확인한다. |
| inherited | r11 normal656/parent-O656, retained17씩, safety47·실제 TERM/KILL2와 기존 exact-artifact16. 원본 input/result를 검증해 영향 없는 assertion만 재사용한다. 새 artifact나 새 runner의 fresh PASS로 표시하지 않는다. |

현재 runner는 artifact mode admission에 같은 source의 complete pair를 요구하고 parent-O focused mode는 없다. 이 캠페인 전용 제약을 이유로 전수를 반복하지 않는다. R0에는 task-local 실행 wrapper에서 기존 isolated controller/test factory를 재사용하여 (a) artifact의 완전한16 ID와 재사용 anchor를 명시적으로 검증하고 (b) 두 selected view test의 parent-O 실행만 허용하는 최소 적응안을 포함한다. 제품 source나 기존 historical controls는 수정하지 않는다. 변경한 wrapper/config/mode guard에는 집중 safety 검증을 하고 기존 safety evidence의 어느 부분이 그대로 적용되는지 명시한다. 실행기 framework나 격리 정책 완화로 확대하지 않는다.

전체 regression은 executable/권한·record/lifecycle/recovery 의미 또는 shared oracle/fixture·환경/격리 변화로 영향 범위를 한정할 수 없거나, 실패가 기존 anchor를 무효화할 때만 영향 근거와 함께 선택한다. 그 외에는 변경 사례와 소비 경로를 검증한다. 수정마다 전체 실행·리뷰를 자동 반복하지 않는다.

## Execution And Review Boundaries

R0/R1은 fresh Claude CLI session, 확인된 `claude.ai / firstParty / pro`, tools/MCP/session persistence off의 정적 검토다. 계정 email·token·key를 기록하지 않는다. 고정 packet과 입력 hash를 호출 전후 대조하고 최종 응답을 이 기록에 원문 그대로 붙인다. Driver 처분과 Owner 결정은 별도로 쓴다. 기존 M1/M2 승인을 재사용하지 않고 이번 A 승인으로 호출한다.

Native 제품 검사는 기존 exact final GIL-enabled CPython3.14.7과 Git identity, Seatbelt network denial·credential 격리·읽기 input/쓰기 fixture 분리·process-group 정리를 유지한다. 테스트는 task-owned durable 실행 경로만 쓴다. Runtime/control/invocation bytes를 고정하고 canary를 먼저 실행한다. child timeout과 cleanup20초, 8/12GiB task capacity·25/15GiB free-space 조건을 유지한다. 필요한512MiB physical reserve는 새 실행 전에 확보한다.

초기 per-call 한도는 acquire/canary/collection 각각300초, view focused 각600초, artifact1800초, 정적 reviewer 각900초, reader case 각300초를 제안한다. r11 artifact 실측597.568초를 근거로 여유를 둔 값이며 ETA 보장은 아니다. 초과는 미완료로 보존하고 원인/영향을 판단한다. 소규모 보정·후속 검토는 이번 승인 범위에서 이어가며 전수 재실행이나 새로운 의미를 자동 허용하지 않는다. 실행시간·실패·보정·review 호출은 누적 기록한다. 도구별 세부 command/권한은 R0 입력의 task-local launcher에 고정한다.

## Sequence And Completion

진행: source-only 문서 정합 → R0 및 필수 지적 보정 → 문서 일괄 보정 → 정적·CLI·reader 집중 확인 → 최종 candidate freeze → exact-artifact16 → 최종 R1 → Owner 결과·exact 활성화안 제출.

완료 기준은 다음과 같다.

1. source/installed 각각 올바른 규칙과 manual/adapter로 연결되고 local 규칙은 보존된다.
2. reader5개를 실제 관찰하고 언어 선택·진입 성공/실패와 제한을 기록한다.
3. 낡은 claim/상한/current-candidate 안내가 정리되고 역사·권한 의미는 보존된다.
4. 새 artifact와 selected tests가 실행되고 inherited/unverified 근거를 구분한다.
5. R1 필수 지적을 처분하고 Owner가 결정할 exact successor 문서·조항·hash·산출물·근거를 제시한다.

실제 activation record 적용, commit/push/PR/merge/release와 adopter application은 수행하지 않는다. A 결과 수락도 Owner에게 남는다. 발효 전 문서 diff 복구 비용은 낮으나 instruction과 managed release identity의 영향 때문에 L2다. 이전 window로의 실제 downgrade 제한은 문서 revert로 해제되지 않는다.

## Preservation And Checkpoints

이 기록이 진행·review 원문·Driver 처분·누적 결과를 소유한다. private task directory에는 필수 packet/identity, 테스트·reader 입력과 원본 결과, 실행 wrapper와 필요한 실패/reuse 증거만 둔다. 소비자는 R0/R1·영향 검증·Owner 결과/활성화 준비이며 완료 후 필요성을 다시 판단한다. 원본 r11 anchor는 기존 위치에서 재사용하고 새 full backup을 만들지 않는다. 실행에 필요한 frozen copy는 sandbox input으로만 만들고 유일한 source를 대체하지 않는다. 기록·검토가 끝난 중복 transport·빈 scratch·사용이 끝난 reserve는 사용/보존 조건을 확인해 정리한다. 기존 worktree의 미커밋 구현과 마지막 복구본은 보존한다.

## Admission Checkpoint — 2026-10-18

ID20261018-001은 live docs/development 및 retained Git history에서 미사용임을 확인했다. approved artifact root의 새 task directory를 만들었고 기존 작업 경로를 재사용·덮어쓰지 않았다. main source-only6개를 반영하되 현재 FEAT link와 새 CHORE link를 index에 함께 두었다. 상위 source-only 절차와 source 규칙 경로가 최신 main의 byte와 맞는지 확인한다. Runtime/managed29/test/controls는 이 admission에서 바뀌지 않았다. 이 시점 제품 테스트·reader·review 실행은0이다.


### R0 Execution Detail

Static reviewer는 tools 없는 fresh Claude Pro session으로 호출한다. Reader5개는 `--restricted --tools Read --permission-mode dontAsk --permission-prompts none --safe-mode --strict-mcp-config --mcp-config {"mcpServers":{}} --setting-sources "" --disable-slash-commands --no-chrome --no-session-persistence --output-format stream-json --verbose`의 새 세션으로 합성 fixture working directory 안의 자료만 읽는다. Bash/Write/네트워크 tool은 없다. CLI view 자체는 Driver가 격리된 실제 설치에서 실행하고 그 원문을 reader에게 운영자가 제공한 관측으로 준다. 따라서 reader 관찰은 제공된 view의 verified manual/adapter를 찾아 문서를 생성하는 증거이며 agent의 자율 CLI 실행/자동 발견을 주장하지 않는다. Source 사례는 AGENTS만 최초 경로로 주고 해당 문서의 조건부 source 진입을 실제로 따라가는지 본다. 생성 산출물은 model response 원문으로 보존하며 model이 파일에 썼다고 주장하지 않는다. 최종 language/entry 판단은 실제 Read 호출·열린 파일·내용과 응답을 대조한다.

Native task-local 적응안은 기존 common/config·controller.run·Seatbelt·factory를 재사용한다. Legacy campaign.dispatch의 same-input complete-pair 조건 대신 별도 wrapper가 정확한 inherited source/runtime/complete receipts와 cumulative prose-only diff를 검사한다. artifact의16개 exact ID, collection, 실행/완료 receipt를 기존 방식대로 검증한다. Parent-O focused 지원은 private controls copy에서 `focused-parent-O` mode를 core slot에만 추가하고 optimized child flag/selection check를 닫는 최소 변경이다. 기존 controls와 제품 source는 바꾸지 않는다. 이 변경은 단순 prose가 아니므로 inherited safety47을 새 controls PASS로 표시하지 않고, 새 copy의 기존 selfcheck47과 추가 mode/anchor/admission negative checks를 실행한다. 새 real cleanup probes와 canary로 실제 경계를 확인한 뒤 제품 테스트를 시작한다.

## R0 Result And Driver Disposition — 2026-10-18

Fresh Claude Opus5.5 (`claude-opus-5-5`), `claude.ai/firstParty/pro`, session `205d48ba-82ec-4fc7-beb9-a71e449c9a2c`. 도구 없는 정적 검토237.97초, exit0, input drift0/22, group absence 확인·cleanup 오류0. Packet354377 bytes SHA-256 `13e15acb603e45d1441b33fe2864bb32c4b94d2ae150c2d268d66c1ee53ee6a8`. API의 list-price metadata는 별도 청구 관측이 아니다. 아래 원문과 Driver 판단은 별개이며 결과 수락/활성화를 대신하지 않는다.

### Reviewer Verbatim

# R0 정적 검토: CHORE-20261018-001 (A 최소 보정과 활성화 준비 계획)

이 세션에는 도구가 없습니다. 그래서 plan 파일 작성이나 ExitPlanMode 호출을 하지 않았고, 아무것도 실행하지 않았습니다. 아래 내용은 제공된 packet만 읽고 내린 정적 판단입니다. 이 리뷰는 Owner의 계획 승인, 결과 수락, 계약 활성화를 대신하지 않습니다.

## 결론

- **Blocker: 0건**
- **필수수정: 7건** (R0-A-M1–M7)
- **비차단: 6건** (R0-A-N1–N6)

계획의 큰 방향은 Owner 승인 범위와 맞습니다.
- 최소 범위를 지킵니다.
- main DR-0006을 개정하지 않고 재사용합니다.
- 실제 활성화, Git, adopter 적용을 제외합니다.
- inherited와 fresh 증거를 구분합니다.
- 자동 전수 재실행을 하지 않습니다.

다만 일곱 가지를 실행 전에 계획에 명시해야 합니다.
- 설치 payload에 들어가는 AGENTS의 source 경로가 설치본에서 미치는 영향
- 언어 규칙과 기존 문구의 충돌
- inherited 656×2를 재사용할 수 있는 판정 근거
- 아직 없는 wrapper와 reader launcher가 갖춰야 할 최소 조건
- 증거를 최종 bytes에 결속하는 방법
- token budget 측정 절차

모두 문장 수준의 보정이며, 새 registry, 전수 재실행, 전면 재작성은 요구하지 않습니다.

---

## 필수수정

### R0-A-M1. 설치 payload에 들어가는 AGENTS의 source 진입 경로

**근거 (정적)**
- `AGENTS.md`는 설치 payload에 들어가는 managed29 문서입니다. 이는 Getting Started의 "Managed payload entries describe the Harness source"와 계획의 managed bytes 변경 언급에서 확인됩니다.
- source 진입처인 `CONTRIBUTING.md`와 `docs/development/WORKFLOW.md`는 source 전용이라 설치 payload에 없습니다.
- 계획의 정적 검사는 "local link/anchor"라고만 적혀 있어, 어느 트리를 기준으로 link를 검사하는지 정해져 있지 않습니다.
- `WORKFLOW.md` "Source And Installed Project Entry" 절에 "The unchanged AGENTS/CLAUDE entry does not provide a direct route to these source rules … An agent given only that entry has no verified automatic discovery path here."라는 문장이 있습니다. A가 AGENTS를 고치면 이 문장은 사실과 맞지 않게 됩니다. 그런데 계획의 범위 표에는 이 문장의 처분이 없습니다.

**최소 수정**
1. link와 anchor 검사를 두 트리에서 모두 수행합니다.
   - source 트리
   - 설치된 payload 29개 트리
2. source 전용 문서는 설치본에서 깨진 상대 링크가 되지 않게 합니다. 링크 대신 조건부 문장과 경로 텍스트로 쓰거나, 설치본에서 의도된 비해결임을 검사 예외로 명시합니다.
3. "source checkout에서 개발 중"임을 판별하는 조건을 문구에 둡니다. WORKFLOW 기준으로는 명시적 지시가 있거나 source 전용 진입 파일이 존재하는 경우입니다. 설치 project의 agent가 이 조건만 보고 source 절차로 들어가지 않아야 합니다.
4. WORKFLOW의 위 문장을 어떻게 처분할지 계획에 적습니다. WORKFLOW는 DR-0006으로 수락된 문서입니다. 따라서 다음 중 하나를 Owner 결정 항목으로 남깁니다.
   - navigation 수준의 사실 보정으로 볼 수 있는지 판단하고, bounded diff를 기록합니다.
   - DR-0006 또는 DR-0003의 named amendment가 필요한지 판단합니다.
   - Driver가 판단 없이 수락된 bytes를 고치지 않습니다.

### R0-A-M2. 언어 우선순위와 기존 문구의 충돌, 그리고 source 자체 규칙의 위치

**근거 (정적)**
- `REFERENCE.md` Project Document Assistance 절에 "Project rules own their language, location, identifiers…"라는 문장이 있습니다. 새 순서(명시 요청 → project 규칙 → 대화 언어)와 그대로 충돌합니다.
- `SKILL.md`의 "Use the human's conversation language for your explanation"은 **대화 설명 언어**에 관한 규칙입니다. 새 규칙은 **저장 산출물 언어**에 관한 것이므로 둘의 구분이 필요합니다.
- Colvia source 자체도 project이고, 그 규칙은 "shipped 안내는 영어"입니다. 그런데 이 규칙은 계획 본문에만 있고 source 규칙 문서에는 없습니다. 그대로 두면 새 shipped 규칙이 source 개발에 적용될 때 한국어 대화가 shipped 문서 언어를 바꾸는 해석이 가능합니다.

**최소 수정**
1. 범위 표의 "작성 안내" 행에 REFERENCE의 위 문장을 명시적인 수정 대상으로 적습니다.
2. 충돌 규칙을 한 문장으로 정합니다. 명시 요청이 배포, 계약, 법적 이유로 강제되는 project 언어 규칙과 충돌하면 조용히 한쪽을 고르지 않고 충돌을 보고하거나 질문합니다.
3. 대화 설명 언어와 저장 산출물 언어를 구별하는 한 문장을 둡니다. 기존 SKILL 문구는 유지합니다.
4. Colvia source의 언어 규칙(shipped=영어, Owner용 개발 기록=Owner 언어)을 둘 위치를 정합니다.
   - CHORE 기록의 task-scope 지시로만 둘 수 있습니다.
   - WORKFLOW에 넣는다면 그것은 절차 변경입니다. "Rule Changes And Retirement"에 따라 amendment 경로를 밟아야 하며 Owner 결정 사항입니다.

### R0-A-M3. inherited 656×2 재사용 조건을 소비자 목록으로 판정

**근거 (정적)**
- 계획은 "제품 실행 bytes, 관련 test/fixture/controls/runtime·환경 대조"를 원칙으로 둡니다. 그러나 **바뀐 managed 문서를 읽는 ordinary 테스트**가 무엇인지 판정하는 절차가 없습니다.
- MAINTAINING은 "Classify by behavior, not filename extension"과 "agent instructions can change behavior"를 요구합니다.
- 직전 R1-N1도 "이 문서를 읽는 테스트"를 다시 실행하라고 권고했습니다.
- `PRODUCT-CAPABILITIES.json`은 code나 테스트가 파싱할 가능성이 있는 데이터입니다. 소비자가 있다면 prose가 아니라 동작 입력입니다. 이 packet만으로는 확인할 수 없습니다.
- 확인된 테스트 제약은 다음과 같습니다.
  - `test_c16_artifact_inventory`는 설치 payload의 `README.md`, `docs/MAINTAINING.md`, `docs/OPERATIONS.md`, `adapters/colvia-work/SKILL.md`에 `b'delegation-1'` 문자열이 있어야 통과합니다.
  - `test_c09`는 새 P와 r11 P의 binding이 서로 달라야(`assertNotEqual`) 통과합니다.

**최소 수정** (실행 전 계획에 추가)
1. 변경되는 managed 경로마다 `tests/`와 fixture에서 그 경로, anchor, 문구를 소비하는 곳을 정적으로 찾습니다. CAPABILITIES는 `src/`도 함께 찾습니다. 찾은 소비자 목록을 기록하고 그 테스트를 focused 대상에 넣습니다.
   - 소비자가 0건이면 0건이라는 근거를 기록합니다.
   - CAPABILITIES를 code가 읽는다면 그 변경은 prose-only로 분류하지 않습니다.
2. 비문서 경로의 byte 동일성을 확인합니다.
   - 대상: `src/`, `tests/`, `colvia`, fixtures, controls, runtime
   - 비교 기준: r11 frozen 입력 `47d43867…`
   - 방법: `file_map` 대조와 diff 목록
3. 재사용 anchor의 보존 소비자를 갱신합니다. r11 handoff의 `retention_end`는 M1/M2 결과 처분에 묶여 있고, 그 처분은 이미 끝났습니다. 소비자를 "A 재사용과 활성화 준비"로 다시 지정하지 않으면 정리 판단에서 anchor가 사라질 수 있습니다. MAINTAINING은 "Missing or unverifiable evidence cannot support the reuse"를 요구합니다.
4. 위의 C16 문자열 제약과 C09 inequality 제약을 문구 보정의 불변 조건에 추가합니다.

### R0-A-M4. 아직 없는 native task-local wrapper의 최소 조건

**근거 (정적)**

계획은 아래 구현물을 "R0 입력의 task-local launcher에 고정"한다고 쓰지만, 이번 packet에는 `review-a.py`만 있습니다.
- wrapper
- private controls copy
- reader launcher

제공된 controls에서 다음 사실이 확인됩니다.
- `controller.main`은 `campaign.json`이 있으면 `campaign.dispatch`로 분기합니다. 반대로 `campaign.json`이 없으면 `config()`가 `agent-worktrees` 루트와 source 내부 controls를 요구하므로 실패합니다.
  - 따라서 wrapper가 `controller.run`을 직접 부르는 설계가 됩니다.
  - 그 경우 `main`이 하던 `require_isolated`, interpreter digest 확인, `controller.lock` 배타 잠금이 빠집니다.
- phase가 `delegation`일 때 focused와 artifact는 같은 source 기준의 `smoke-base` 완료를 요구합니다(`run`/`preflight`의 `completed(c,p,"smoke","base",same_source=True)`). 계획은 acquire, canary, collection만 언급하고 smoke는 언급하지 않습니다.
- parent-O 모드 추가는 core slot만 바꿔서는 끝나지 않습니다. 다음 지점이 모두 함께 바뀌어야 합니다.
  - `runner.py`의 mode 집합
  - `require(bool(sys.flags.optimize) == (mode == "complete-parent-O"))`
  - `run()`의 `optimized=mode=="complete-parent-O"`
  - budget 상한식
- schema2 `campaign.json`은 `approval_sha256`을 요구합니다.
- `run()`의 budget은 cleanup 시간을 포함합니다(`settle_child`의 `end=start+budget`).

**최소 수정** (계획 문구 정정과 실행 전 조건)
1. 문구를 정정합니다. 구현물이 R0 입력에 없다는 사실을 밝히고, 아래 조건으로 작성하고 고정한 뒤 최종 R1 packet에 원문, hash, selfcheck 결과를 넣는다고 씁니다.
2. wrapper는 다음을 다시 강제합니다.
   - `require_isolated`
   - 실행 interpreter의 digest
   - `controller.lock`의 배타 잠금
   - 기존 `preflight`
3. smoke-base를 실행할지, 또는 그 전제를 바꿀지 명시합니다. 전제를 바꾼다면 그것은 guard 변경이므로 selfcheck 대상이 됩니다.
4. `approval_sha256`에는 이번 승인 `4cd532b9…`를 사용합니다.
5. 추가 negative check 목록을 미리 고정합니다. 최소한 다음 다섯 가지입니다.
   - `focused-parent-O`가 `-O` 없이 실행되면 거부
   - normal focused가 `-O`로 실행되면 거부
   - `focused-parent-O`가 승인된 2개 ID 밖을 선택하면 거부
   - artifact에 16개 미만 ID를 넣거나 다른 ID를 섞으면 거부
   - inherited anchor의 source, runtime, receipt hash가 다르면 거부
6. budget 표기를 "cleanup 포함"으로 맞춥니다. 예를 들어 artifact 1800초는 cleanup 20초를 포함합니다.

### R0-A-M5. reader 5개 사례의 사전 등록과 격리

**근거 (정적)**
- 계획은 "최종 판단은 Read 호출·응답 대조"라고만 하고, 사례별 합격 기준을 실행 전에 고정하지 않습니다.
- `--tools Read`가 fixture 바깥 절대경로를 읽지 못한다는 근거가 packet에 없습니다. 바깥을 읽으면 두 가지 문제가 생깁니다.
  - 읽은 내용이 외부 서비스로 전송되므로 공개 범위 위반입니다(WORKFLOW Disclosure, Agent Collaboration).
  - 관찰이 오염됩니다.
- Claude Code는 cwd의 `CLAUDE.md`, 상위 디렉터리의 instruction 파일, 사용자 memory를 자동으로 읽을 수 있습니다. `--setting-sources ""`가 이 자동 로드까지 막는지는 이 packet으로 확인할 수 없습니다.
- R-A는 "AGENTS만으로" 진입하는지를 봅니다. 그런데 fixture에 `CLAUDE.md`가 있으면 실제 첫 진입점은 `CLAUDE.md`가 됩니다.

**최소 수정**
1. 사례마다 실행 전에 다음을 기록합니다.
   - fixture의 file hash
   - 기대 언어
   - 반드시 열어야 할 경로
   - 열면 안 되는 경로
   - 합격과 실패 판정 문장
2. 금지 경로와 판별력 있는 조건을 둡니다.
   - R-B와 R-E(설치 project)는 source 절차(`CONTRIBUTING.md`, `WORKFLOW.md`)에 진입하지 않아야 합니다.
   - R-D는 project 규칙의 언어가 대화 언어와 **달라야** 판별력이 생깁니다.
3. 모델과 auth 경로를 고정합니다.
   - `--model`을 고정합니다.
   - `review-a.py`와 같은 route 확인과 env override 거부를 적용합니다.
4. 5개 사례를 돌리기 전에 negative probe를 1회 실행합니다.
   - fixture 바깥 경로 Read가 거부되는지 확인합니다.
   - 상위나 사용자 instruction 파일이 로드되지 않는지 확인합니다.
   - fixture 바깥을 읽은 사례는 무효로 처리합니다.
5. R-A fixture에 `CLAUDE.md`를 넣는지 여부를 기록합니다.
6. 모든 시도를 보존합니다. 실패한 시도도 포함하며, 문서를 고친 뒤 다시 시도한 경우도 별도 기록합니다. 사례당 1회 관찰은 일반화할 근거가 아니라는 한계를 명시합니다.

### R0-A-M6. 증거와 최종 bytes의 결속, 그리고 freeze 이후 변경 규칙

**근거 (정적)**
- 계획의 순서는 정적·CLI·reader 확인 → 최종 freeze → artifact16 → R1입니다.
- 이 순서에서는 reader와 view 2개 테스트가 freeze 전 bytes에서 실행됩니다.
- 이후 token 측정이나 R1 지적 때문에 managed 문서가 바뀌면 그 증거가 어느 bytes에 대한 것인지 불명확해집니다.

**최소 수정**
1. reader와 CLI 결과마다 실제로 소비한 파일의 hash를 기록합니다.
2. freeze 시점에 그 hash와 대조합니다. 바뀐 파일을 소비한 사례만 다시 실행합니다.
3. freeze 이후 managed byte가 바뀌면 P identity가 바뀝니다. 그때는 다음을 다시 실행합니다. 이 규칙을 계획에 명시합니다.
   - artifact16 1회 (r11 실측 약 600초)
   - M3에서 찾은 소비자 테스트
   - 영향받는 reader 사례
4. R1 이후 보정은 같은 규칙을 따르며, 그 외 변경 시 전체 재실행은 하지 않습니다.

### R0-A-M7. token budget 측정 절차

**근거 (정적)**
- MAINTAINING은 측정 조건으로 `tiktoken==0.13.0`, `o200k_base`, 정확한 입력 파일을 요구합니다.
- 현재 Getting Started, AGENTS, README의 분량으로 보면, 합산 4000 token이 이미 경계에 가깝거나 넘었을 가능성이 있습니다. 이는 추정이며 측정하지 않았습니다.
- A는 AGENTS와 Getting Started에 문구를 더합니다.
- `tiktoken`은 encoding 파일을 네트워크에서 내려받을 수 있습니다.

**최소 수정**
1. **편집 전** 기준선을 먼저 측정합니다. 측정 환경, 파일 hash, 수치를 기록합니다.
2. encoding 파일은 미리 확보한 offline 파일을 쓰고, 그 파일의 hash를 기록합니다.
3. 한도를 넘을 때의 처분을 미리 정합니다.
   - 범위 안에서 문구를 축약합니다.
   - 그래도 넘으면 미달 사실을 기록하고 Owner 결정으로 넘깁니다.
   - PASS로 표기하지 않습니다.
4. MAINTAINING의 "The current candidate has no token-budget result yet"는 stale claim이므로 수정 대상에 포함합니다.

---

## 비차단

- **R0-A-N1. parent-O focused의 효용이 낮음.**
  - MAINTAINING에 따르면 "Parent `-O` does not propagate to installed launcher or auditor children"입니다. 대상 2개 view 테스트는 설치 launcher 자식에서 동작을 확인하므로, parent-O가 더하는 범위는 작습니다.
  - Owner가 parent-O 실행을 빼고 "미검증 한계"로 기록하면 controls 적응과 그에 따른 safety selfcheck 부담이 없어집니다. 최소 범위 원칙에 더 맞습니다.
  - parent-O를 유지한다면 M4를 따릅니다.

- **R0-A-N2. DR-0005의 Decision, Rationale, Consequences.**
  - Decision Guide는 Draft 단계에서 이 세 절을 비워 두고 수락 시에 채우도록 정합니다.
  - 직전 R1-N1의 "본문 작성"은 다음 두 가지로 해석하는 것이 맞습니다.
    - Proposal 본문 정정
    - 활성화 시 넣을 제안 문안을 CHORE에 준비
  - DR-0005는 source 전용이라 활성화 시점에 채워도 P와 Q의 hash에 영향이 없습니다.

- **R0-A-N3. SKILL의 한국어 고정 문장.**
  - 예: "기준만 갱신하며 작업 결과를 수락하거나 완료하지 않습니다."
  - 새 언어 규칙과 일관되게 "사람의 언어로 다음 의미를 명시"하는 예시로 읽히는지 17개 문서 점검 때 확인합니다.
  - 수정이 필요하면 해당 span만 고칩니다.

- **R0-A-N4. "17개 proposed normative 문서" 목록이 packet에 없음.**
  - 편집 전에 목록과 hash를 CHORE에 고정하기를 권고합니다.
  - DR-0006 본문도 이 packet에 없어 "named navigation cutover"의 정확한 범위는 확인할 수 없습니다.

- **R0-A-N5. 직전 R1 비차단 항목의 A 처분.**
  - R1-N3(view의 예외 범위): 제품 code 변경이 A 범위 밖이므로 "A에서 처리하지 않고 이월"한다고 명시합니다.
  - R1-N2(`_replace_product_file` 호출자, `_entry_sync`): 활성화 준비의 정적 기록 항목으로 넣습니다. code는 변경하지 않습니다.

- **R0-A-N6. CONTRIBUTING, WORKFLOW, DECISION-GUIDE 머리말의 조건부 문구.**
  - "Until the Owner accepts and activates…"는 DR-0006이 이미 발효된 지금 시점과 표현이 어긋납니다.
  - main bytes 정합이 목적이므로 A에서는 고치지 않는 것이 맞습니다. 별도 후보로 기록만 합니다.

---

## 핵심 질문별 판단

| 항목 | 판단 |
|---|---|
| 최소 범위와 authority/activation 경계 | 적절합니다. M1-4(WORKFLOW 문장)와 M2-4(source 언어 규칙 위치)의 amendment 여부만 Owner 결정으로 남기면 됩니다. |
| main DR-0006 재사용 | 적절합니다. 6개 파일의 hash가 packet 원문과 일치합니다. DR-0006 본문은 packet에 없어 확인하지 못했습니다. |
| 언어 우선순위 | 방향은 타당합니다. REFERENCE 문구 충돌, 대화와 산출물의 구분, 강제 규칙 충돌 처리가 필요합니다(M2). |
| inherited 656×2 | 소비자 목록, 비문서 byte 동일성, anchor 보존 소비자 갱신을 갖추면 적용 가능합니다(M3). |
| 새 artifact16 | C09, C16 제약을 지키면 충분합니다. Q로 r11 P를 쓰는 것은 실제 문서만 다른 왕복을 직접 시험하므로 적절합니다. |
| reader 5 | 사전 등록, 격리, 판별력 조건(M5) 없이는 언어와 진입에 대한 결론의 근거가 약합니다. |
| 최소 private runner 적응 | M4 조건을 갖추면 충분합니다. N1처럼 아예 빼는 선택지가 더 작습니다. |

## 증거 구분

**정적 판단 (이 리뷰)**
- 위의 모든 지적
- packet 원문 사이의 대조: controls/runner/common 조건, C09·C16 제약, 문서 문구 충돌

**실행 증거 (Driver 기록이며 이 리뷰가 재현하지 않음)**
- r11의 656×2, artifact16, retained17, safety47
- 직전 R1-006 판정

**확인 불가**
- task-local wrapper, controls copy, reader launcher 구현 (아직 없음)
- tests와 src에서 문서를 소비하는 곳의 실제 목록
- `PRODUCT-CAPABILITIES.json`의 code 소비자
- 현재 token 수치
- Claude CLI Read의 경로 격리와 instruction 자동 로드 동작
- DR-0006 본문
- 17개 문서 목록
- r11 anchor 파일의 현재 존재 여부

## Owner 결정 경계

이 리뷰는 다음 어느 것도 부여하지 않습니다.
- 계획 승인 변경
- 결과 수락
- DR-0005/DR-0003 활성화
- WORKFLOW 개정
- commit, push, PR, merge, release
- adopter 적용

Owner가 정할 사항은 다음과 같습니다.
- M1-4: WORKFLOW 문장의 처분 경로
- M2-4: source 언어 규칙의 위치
- M7: token 한도를 넘을 때의 처분
- N1: parent-O focused를 유지할지 여부

### Driver Disposition And Pre-execution Conditions

| 지적 | 처분 및 실행 조건 |
| --- | --- |
| M1 source/installed 진입 | 수용. 명시된 Colvia source 개발 요청일 때만 source 전용 경로를 코드 텍스트로 안내한다. 같은 AGENTS가 managed payload 안에 있다는 이유나 파일명 존재만으로 source 개발을 추론하지 않는다. source와 installed29 양쪽 링크/anchor를 검사한다. 수락된 WORKFLOW bytes는 고치지 않는다. 해당 문장은 DR-0006 재구성의 당시 unchanged-entry 경계를 설명한다는 점을 AGENTS에서 밝히고, 이를 현재화하는 정확한 navigation 문안은 최종 활성화 제안에 준비한다. 그 절차 개정은 이번 실행으로 발효하지 않는다. |
| M2 언어 | 수용. REFERENCE의 project language 문구를 명시 수정하고 대화 설명과 저장 산출물을 구분한다. 명시 요청→project 기본값→대화 언어이며 배포/계약상 강제 언어 충돌은 인간에게 드러낸다. 이번 source의 shipped 영어·Owner 기록 한국어는 이 승인된 task 범위의 지시로만 유지한다. WORKFLOW에 새 일반 언어 정책을 도입하지 않는다. |
| M3 inherited | 수용. `src/tests/colvia`와 source controls bytes/mode를 r11 전체 입력과 대조하고 managed 문서의 직접 문구·경로·데이터 소비자를 조사한다. 포장/불변 inventory 소비자는 C01–C16, 직접 문구/런타임 선언 소비자는 selected focused로 확인한다. CAPABILITIES.runtime은 불변이며 evidence/status 설명만 바꾼다. C16의 delegation-1 marker와 C09의 P≠Q는 유지한다. 기존 r11 원본의 현 소비자는 A 영향판정·활성화 준비이며 exact 결과/계약 및 후속 Git/적용 여부 결정 뒤 보존 목적을 재평가한다. 과거 handoff를 소급 고치지 않는다. |
| M4 native wrapper | 수용. R0에 wrapper 구현이 없었음을 정정한다. 구현/hash/한정 diff/selfcheck를 최종 R1에 제공한다. `require_isolated`, interpreter hash, root/controller 배타 잠금, preflight, smoke-base, 이번 approval hash를 유지한다. parent-O focused는 승인된2 ID만 허용한다. 최적화 mismatch2·잘못된 focused selection·artifact 누락/혼합·anchor source/runtime/receipt drift를 negative checks에 포함한다. 모든 native 한도는 cleanup20초 포함이다. |
| M5 reader | 수용.5사례 fixture hash/필수경로/금지경로/언어/판정문을 먼저 고정한다. source R-A는 CLAUDE 없이 AGENTS만 지정한다. R-B/E는 source 절차 진입 금지, R-D는 한국어 요청+영어 project 기본값으로 분별한다. 명시 모델 `claude-opus-5-5`·구독경로·환경 override 거부를 고정한다. 안전한 합성 외부 sentinel·상위 instruction을 이용한 선행 negative probe1회로 restricted Read 거부와 safe-mode 자동문맥 배제를 확인한다. 부적절한 Read/자동문맥이 있으면 해당 관찰은 무효로 보존하고 보정한다. 모든 시도와 원문을 유지한다. 사례1회는 일반 품질 증거가 아니다. |
| M6 최종 결속 | 수용. reader 실제 입력과 Read 파일, focused 전체 source를 hash로 결속하고 최종 freeze와 대조한다. 이후 managed byte 수정은 영향 reader/직접 소비자 및 새 artifact16만 재실행하며 전체656은 자동 반복하지 않는다. source-only 기록 추가가 managed29를 바꾸지 않았는지도 확인한다. |
| M7 token | 수용. 편집 전 offline tiktoken0.13.0/o200k_base: AGENTS790·README645·Getting Started2949, 합4384로4000초과. network/write 금지 Seatbelt, cache SHA-256 `446a9538cb6c348e3516120d7c08b09f57c36495e2acfffe59a5bf8b0cfb1a2d` 확인. 승인된 문서 정합 안에서 중복/current-history 설명을 줄이고 조건·예외를 유지한다. 최종 재측정이 미달이면 PASS로 보고하지 않는다. |
| N1 | parent-O focused2는 이미 승인된 계획대로 유지하되 child에 -O가 전파되지 않는 제한을 명시한다. |
| N2 | 수용. DR-0005 Decision/Rationale/Consequences는 비워 두고 CHORE에서 activation 삽입안을 준비한다. |
| N3 | 한국어 문장은 설명 의미의 예시로 표시하고 conversation 언어로 설명한다는 기존 지침을 유지한다. |
| N4 | 아래17개 exact 시작 목록과 hash를 고정한다. DR-0006 원문을 직접 읽어 기존 수락/activation 및 shipped 제외 범위를 확인했다. |
| N5 | 기존 R1-N3 view 예외 범위 보정은 A 밖에 두고 미검증 한계를 승계한다. R1-N2의 `_replace_product_file` 호출자와 `_entry_sync` 의미를 활성화 준비의 정적 trace로 기록하며 실행 코드 변경은 없다. |
| N6 | 수락된 main의 조건부 머리말은 그대로 유지하고 DR-0006의 actual activation record로 읽는다. 이 task에서 별도 정책 문서 수정을 확대하지 않는다. |

R0 필수 보완은 위 실행 조건으로 반영했다. 이는 기존 Owner의 일괄 실행 승인 안의 구체화이며 새로운 승인·활성화가 아니다. smoke-base의 기존 runtime7에 더해 실제 문서 소비자 목록을 확정한 뒤 실행한다. reader 선행 probe와 selfcheck는 native 제품 결과·reader 성공과 별개로 보고한다.

### Exact Starting Document Set

| 문서 | 시작 SHA-256 |
| --- | --- |
| `docs/WORKSPACE-CONTRACT.md` | `ec79779599efae941f953a13892d308502198420fe04821d5e4b3852060e9feb` |
| `docs/GENERAL-WORK.md` | `0e9ca23f2b05fb88785c8c80501d4f0f43b32de37d3d0a8c83347a3a24857638` |
| `docs/GUIDED-INTENT-FORMATION.md` | `2868fb3bfe5e393aa2f88073110f8d278f0b62345ba0c2b5b642de62fab067eb` |
| `docs/REFERENCE.md` | `8d1f9f82ab916f1b2b3ca1323dc7222ccde1881b3a4065c04414198ed120c885` |
| `docs/OPERATIONS.md` | `ec53b581e27227f61a5cc7249431828fc82b13c1ffe8d098c7e04ec77e7376f3` |
| `docs/MANUAL-OPERATION.md` | `ea86513c3f907b2ff76a1a0f459d77839ac6fad89fcd31587e77152abe5bd3ed` |
| `docs/SECURITY-AND-SUPPORT.md` | `268bee514abfc5801f75ec2a03ea9339af59724d781376417345d3372058410b` |
| `docs/MAINTAINING.md` | `e7b93aa1872fc38926c21c3625cb67f6dfa22de91cc2efdad857cd8c055b7449` |
| `docs/GETTING-STARTED.md` | `2a958d3f51f41020131c82914e896b63eb879a254b2289ceb043e9320a08aa15` |
| `adapters/colvia-work/SKILL.md` | `870bf4ba9d444e6f97838a8e23c382136949b1d88c8bac77e2c1f7b8a18204f6` |
| `docs/development/CHECKOUT-1-STRUCTURE.md` | `fd4019d4093fbd64ef5dcda8c36ba41cfc319a6e4feb0d84fd048c8d8dd81fe7` |
| `AGENTS.md` | `938b86603e45d1703c784b4cd9f4b8467cea2db6f19d6f0f6c32b76d0812cdea` |
| `CLAUDE.md` | `f7ba473b660c4728a8f0c57b2f5605dd08a2239a271491fac6238eb96ecad2a2` |
| `docs/CONCEPTS.md` | `f8df371daad6354a92306b3cf312a8a8fa2493606292fdfc7a9494413e000778` |
| `docs/README.md` | `1e038ad1ef966a082dd1398cdb507c4ee8e9382566f342a99f2845fa7d3ec805` |
| `README.md` | `cc05cec4070b90303b7db0fcb3a78a75b451a554d4c3822e6a3f3f1861e07eb7` |
| `PRODUCT-CAPABILITIES.json` | `f7cd490c9830191d10a0be819df9cf712fcf28b7d54ebe83f6dbfd197f02faf3` |

## A Batch And Validation Admission Checkpoint

AGENTS의 명시적 source 개발 분기, REFERENCE의 저장 산출물 언어 규칙, adapter pointer, 현재 delegation-1 명령·schema4 안내, 기존 entry-1 역사 경계와 활성화 준비 claim을 일괄 보정했다. 수락된 source procedure5개는 main bytes 그대로이며 development index만 authorized navigation을 더했다. DR-0005의 최종 Decision/Rationale/Consequences는 빈 상태다.

- 편집 후 offline token: AGENTS886, README448, Getting Started2564, 합3898. 기준2000/4000을 충족했다. 앞선4384는 실패 기준선으로 유지한다. 실제 입력 hash는 해당 native source snapshot에 결속한다.
- GFM source21개 및 managed Markdown의 양쪽 소비 경로295개 link/anchor 확인: 오류0, code 밖 literal emphasis0. runtime/fixture/test/controls 실행 입력104개는 r11 frozen bytes/mode와 동일하다. CAPABILITIES는 delegated evidence/status 설명 한 행만 바꾸고 runtime 선언은 유지했다.
- 문서 직접 소비자 정적 조사에서 fresh normal8개와 parent-O view2개를 선정했다. 세부 ID와 나머지 generic byte/path 소비자의 disposition은 private `static-preparation.json`에 있다. fresh artifact16은 실제 변경 payload를 검사한다. 기존656×2는 영향 없는 동작 assertion의 anchor다. 모든 옛 assertion을 새 source에서 실행했다고 주장하지 않는다.
- 기존 `test_document_port_local_links_resolve`는 raw regex로 code fence까지 링크로 오인한다. main DECISION-GUIDE의 역사 인용 안에 있는2개 링크가 그 반례다. 테스트를 실행해 PASS로 표시하지 않았고 테스트 source도 고치지 않았다. 이번 문서 검증은 실제 GFM이 렌더한 source·payload 링크/anchor 검사로 수행했다. 이 legacy oracle의 소스 문서 전수 적용 한계는 최종 R1에 제공한다.
- Reader probe001은 내부 Read 성공·외부 합성 Read 거부를 관측했으나 Driver 결과 파서가 문자열형 stream message에서 실패했다. 원본을 보존하고 그 실행의 cleanup metadata가 미저장이라는 한계로 PASS를 부여하지 않았다. event 타입 처리와 선행 execution receipt 저장을 고친 probe002는10.97초/exit0, 외부 Read 명시 거부, parent instruction marker 없음, input drift0, group absence·cleanup 오류0이다. 이는 합성 경로와 safe-mode 관찰이며 모든 host customization 부재의 일반 증명이 아니다. 실제 계정 email/token/key는 기록하지 않았다.
- Private controls80은 기존77 copy에 최소 parent-O guard 보정과 A admission/selfcheck/합성 fixture helper3개를 더했다. `test.sb`와 `acquire.sb`는 원본 bytes와 동일하다. 새 safety59(기존47+추가12), 실제 own-group TERM/KILL2가 PASS다. Product run에는 고정 Python3.14.7 `-I -S -B`, reviewed argv, root/controller lock, exact approval/runtime/source/reuse hashes, preflight·smoke prerequisite, resource guard와 cleanup 포함 한도를 강제한다.
- Native snapshot211개 source digest `2620bceb916eb7d2ed8e7e6048fad62fe020fac0d9e8f962d51e8f15c8d4bb32`. 관리29 중15개 문서/data 설명이 바뀌었고 executable 변경0이다. Q는 r11의 실제 수락 P와 byte-identical이다. Source-only 이 진행 기록의 후속 추가는 frozen snapshot과 별도로 남기고, managed bytes 동일성으로 결속한다.

이 체크포인트는 결과 수락·계약 활성화·Git/adopter 실행이 아니다. reserve2개는 native 단계 및 최종 R1의 현재 소비자가 있어 유지한다. 실행 source copy는 격리와 exact 입력의 소비자용이며 full backup으로 새 영구 보관을 요구하지 않는다.

### Inherited Static Trace Limits

기존 R1-N2의 `_replace_product_file`은 현재 source에서 `workspace_switch_apply` 안의 launcher 교체와 binding 교체2곳만 호출한다. 이 helper는 staging/대상 parent에 `_entry_sync`를 호출하며 비실행파일 binding 교체에는 B1 검증 flag를 준다. `_entry_sync`는 sync 결과가 pass가 아니거나 OSError일 때 보존/재시도 안내와 함께 `HV2-WORKSPACE-PRODUCT`를 발생시킨다. 따라서 그 docstring의 transition-only 표현과 달리 실제 호출 범위에는 same-window replacement가 포함된다. 이것은 현 source 정적 trace이며 새 runtime 재현이나 power-loss 보증이 아니다. A는 그 실행 코드를 바꾸지 않았다. R1-N3 view exception 범위와 모든 live-child/exit87 조합의 미검증 한계도 승계한다.


## A Reader And Consumer Observations — 2026-10-18

Fresh native smoke7/7, 문서 직접 소비자 normal8/8(33.905초), parent-O view2/2(18.589초)가 완료됐다. 각 실행의 입력 동일성, 자연 종료와 group absence를 확인했다. parent-O는 설치 launcher/auditor 자식에게 전파되지 않는다. 별도 합성 fixture의 init preview/apply/view12회는 모두 exit0이며 기존 project-owned 파일 bytes와 view read-only를 확인했다. 이는 테스트 개수에 합산하지 않는다.

Reader5개는 각각 새 `claude-opus-5-5` 세션, `claude.ai/firstParty/pro`, restricted Read-only로 실행했다. 다섯 실행 모두 exit0, input drift0, 금지/외부 Read0, group absence 확인·cleanup 오류0이다. 아래 엄격 판정은 실행 성공과 구별한다.

| 사례 | 초 | 엄격 사전 기준 | 실제 관찰과 한계 |
| --- | --- | --- | --- |
| R-A | 61.639 | PASS | 필수6경로를 읽고 DR-0006의 실제 activation, Draft3절 공란, 인간 Owner 및 Git 별도 권한을 설명했다. 사본에 넣지 않은 optional CHORE를 추가로 요청해 missing을 정확히 알렸다. 그 task의 실제 내용 확인이나 선정 성공은 주장하지 않는다. |
| R-B | 29.512 | 미달 | manual/adapter 진입과 한국어 계획은 관찰됐다. Reference 직접 Read는 없으므로 사전 기준 미달이다. adapter의 요약 언어 규칙만 소비했다. |
| R-C | 29.123 | 미달 | 한국어 project 기본값보다 명시적 영어 산출물 요청을 우선했다. Reference 직접 Read는 없어 미달이다. 끝의 문서 저장에 항상 intent/Work가 선행한다는 설명은 과도한 일반화다. Reference는 명시된 narrative 기록 요청과 기존 scope/pending/reference 검사를 구별한다. 그 발언을 제품 규칙이나 검증된 안내로 채택하지 않는다. |
| R-D | 28.459 | 미달 | 한국어 대화와 별개로 영어 project 기본값을 따랐다. Reference 직접 Read는 없어 미달이다. |
| R-E | 39.404 | 미달 | LOCAL-KEEP-471, local rule, 기존 계획/사람 결정 기록과 알림·외부계정 제외를 보존했다. typed intent/Work가 없는 narrative resume로 설명했다. Reference 및 project README 직접 Read가 빠져 미달이다. managed CLAUDE 설명과 project CLAUDE를 충돌로 부른 것은 서로 다른 파일 범위를 혼동한 관찰이며 실제 덮어쓰기는 없었다. |

언어 선택은5개에서 기대와 맞았지만 사전 등록한 필수 Read 기준은1/5만 충족했다. 기준을 사후 완화하거나 미달4개를 PASS로 표시하지 않는다. 요청은 응답으로 반환하는 초안이어서 saved-document trigger가 모호했고, adapter 안의 언어 요약을 읽은 것과 Reference 원문을 읽은 것은 다른 증거다. 문구를 고친 뒤 성공할 때까지 재추첨하지 않는다. 이 구분과 C/E의 과도한 설명을 최종 R1의 별도 판단 대상으로 제공한다. 일반 agent 품질·자동 진입·public first-success 또는 실제 adopter 사용은 주장하지 않는다.

관측 원문은 sandbox 내부 실제 target에서 생성한 뒤 reader fixture로 bytes/mode-identical 복사했다. Reader에게는 그 복사 증명을 주지 않아 target 경로 차이를 올바르게 경고했다. 따라서 복사 위치에서 CLI를 재실행했거나 그 위치의 live authority를 확인했다고 주장하지 않는다. 실제 CLI 결과, 복사 검증과 reader 문서 읽기는 각각 별개다. R-A의 필수 source entry 성공은 현재 owning task 내용 확인·선정 완료까지 포함하지 않는다.

### Source-only Structural Supplement Completion

17개 열거 중 source-only CHECKOUT-1-STRUCTURE가 entry-1 shape만 기술하고 delegation delta가 빠진 것을 확인했다. 승인된 successor 정합 범위에서 현재 설계/구현의 schema3 grant·exact actor/K·schema4/window 조항을 추가했다. 기존 역사 본문을 지우지 않고 named replacement와 유효 entry-1 읽기 경계를 명시했다. 이는 새 정책/실행 코드 변경이 아니다. 해당 source-only 파일은 native frozen snapshot 이후 추가 변경됐지만 managed29에는 포함되지 않고 reader5개 어느 Read도 소비하지 않았다. 새 GFM/정적 correspondence/R1로 검증하며, 영향 없는 focused나 reader를 다시 실행하지 않는다.

## Exact Successor Proposal — Not Accepted Or Activated

아래17개는 기술 계약11개와 entry/설명/data6개를 합한 대상 목록이다. 초기 계획의 "17개 normative" 표현은 범주를 넓게 부른 것이며 Concepts/README/CAPABILITIES를 새 normative authority로 승격하지 않는다. 앞선 결정의 기술11·source-only 보충문 및 consumer 구분을 유지한다. 이 표는 첫 R1의 CRLF 지적을 보정한 최종 후보(v2)다. 첫 A payload와 다른 managed 파일은 SECURITY 한 문장뿐이며 reader는 그 파일을 읽지 않았다. 관리29개와 이 표의17개는 correction native 입력과 같고, 후속 진행 기록은 source-only다.

| 문서 | 분류 | Bytes | 제안 SHA-256 | 정확한 변경·적용 범위 |
| --- | --- | --- | --- | --- |
| [docs/WORKSPACE-CONTRACT.md](../WORKSPACE-CONTRACT.md) | 기술 계약11 | 39286 | `752b01299f1cc8846a52b7f8b61abe864a9d8fc0e9ba61e2bfe5debf21f43469` | Root primitives/current candidate pointers 및 Delegation-1 Implementation Candidate: rank6·managed29·schema4 pair·old writer/late-lock·detach provenance·one-way boundary. 기존 identity/truth/recovery 및 First B1 보장 유지. |
| [docs/GENERAL-WORK.md](../GENERAL-WORK.md) | 기술 계약11 | 46509 | `a4e1be991ebf13c322b78f2d5eaf0134696c09c90a134706455396a72d448445` | 기본 human path를 유지하고 Delegation-1 Implementation Candidate의 exact ordinary isolated accept 예외·K 소비·selected revoke·ancestry·parent 경계를 적용한다. Current machine command/schema 설명 정합. |
| [docs/GUIDED-INTENT-FORMATION.md](../GUIDED-INTENT-FORMATION.md) | 기술 계약11 | 5783 | `e0bbc35d46abe8c131aa1581a4e46ee15ee26cd89a7a99d6ddc565af52ea5bb9` | Draft And Acceptance 및 Delegation-1 Implementation Candidate: schema3 non-null grant, exact human intent acceptance, no-grant/parent 구분. intent 수락 주체는 변경하지 않는다. |
| [docs/REFERENCE.md](../REFERENCE.md) | 기술 계약11 | 61763 | `8ed44e4d49479cee850bd310e8d5b3e13dcb7a5df5cbf6d4ce15bef66d3639a4` | Current commands/outcomes/diagnostics, Document Language, Repository-Owned Rules 및 Delegation-1 Implementation Candidate. 저장 언어 우선순위·mandatory 충돌·project authority·정확한 grant/조회 한계를 함께 적용한다. |
| [docs/OPERATIONS.md](../OPERATIONS.md) | 기술 계약11 | 14983 | `e4a3c2c2846ad36e3cdc794ba85760486e8092beeda8544aa921f9849e09f374` | 현행 delegation-1 init/update/repair/detach 안내와 Delegation-1 Implementation Candidate. exact entry-1 predecessor·forward recovery·동일 window rollback·과거 entry 전환 의미 유지. |
| [docs/MANUAL-OPERATION.md](../MANUAL-OPERATION.md) | 기술 계약11 | 4901 | `61bf75fbdbec7f2f828f248c9c482aeb9b446f73037d471b4a9a5cf6ebe828f4` | Retained Evidence/Recovery Boundary 및 Delegation-1 Implementation Candidate: 기존 기록과 schema4 pairing을 구분하고 exact-source 복구·권한 기록 보존. |
| [docs/SECURITY-AND-SUPPORT.md](../SECURITY-AND-SUPPORT.md) | 기술 계약11 | 8687 | `9be4676c928f5ea23d725d8533ab4a81ec453be59014d9527dcfc80b62c6354d` | Runtime And Scope 및 Delegation-1 Implementation Candidate: actor 비인증·host payload enforcement 미검증·기존 플랫폼/실제사용 제한. 역사 관측을 새 후보 PASS로 바꾸지 않는다. |
| [docs/MAINTAINING.md](../MAINTAINING.md) | 기술 계약11 | 22396 | `d9700cb6e6950a740bb85ab818151491cd36acb9a4a916cad49b31a03db24070` | Validation Frequency/Evidence Reuse, Reading Budget, Inventory Window Compatibility, Delegation-1 Implementation Candidate. 역사 campaign cap과 Owner continuation 예외, cumulative risk-based selection, fresh artifact/reader와 inherited 증거 구분. |
| [docs/GETTING-STARTED.md](../GETTING-STARTED.md) | 기술 계약11 | 12791 | `8ae24cb75a9e96320529639f681497823baad738838dd81a57411a2d1d434cd3` | Start/init, human review, current Delegation-1 Implementation Candidate. source/installed 구분·현재 profile/schema·exact predecessor·one-way 경고. 보존된 Entry-1 절은 역사 안내. |
| [adapters/colvia-work/SKILL.md](../../adapters/colvia-work/SKILL.md) | 기술 계약11 | 26891 | `fc96b182cfa86f16b50e9b5d16a708721ce253aa719e546c483e090b8308e552` | 진입/설명/Document Language pointer, project narrative/local override와 Delegation-1 acceptance 안내. 정확한 grant 없는 수락·일반 source self-accept·parent 수락 위임은 없음. |
| [docs/development/CHECKOUT-1-STRUCTURE.md](../development/CHECKOUT-1-STRUCTURE.md) | 기술 계약11 | 53395 | `288fb2347c945015ce4ea9940198bafe350aaaf4a8c63487f69de87f06810e9e` | 새 Current reading boundary 및 Delegation-1 Successor Delta의3개 절만 명시 대체: Window, schema3 grant/actor, selected ancestry/소비, lifecycle schema4. 나머지 보존 구조는 불변. |
| [AGENTS.md](../../AGENTS.md) | entry/설명/data6 | 4403 | `725bb5d5da19f3b2176a022d427eeac111fb71d94f2186091458ce5ff2d5ee84` | Authority Floor, Start의 명시적 source 개발 경로와 installed 경로, 현재 candidate 지침. managed 폴더 위치만으로 source 작업을 추론하지 않는다. |
| [CLAUDE.md](../../CLAUDE.md) | entry/설명/data6 | 436 | `f7ba473b660c4728a8f0c57b2f5605dd08a2239a271491fac6238eb96ecad2a2` | 기존 thin canonical pointer bytes 유지. 설치 project의 고유 CLAUDE를 교체하라는 뜻이 아니다. |
| [docs/CONCEPTS.md](../CONCEPTS.md) | entry/설명/data6 | 4642 | `bdb24c79632f86905e3cf7df4f6a01d2a1f2746fe5b926f3e93760dd365d7a0a` | 기본 human path 설명과 Delegation-1 Implementation Candidate의 한정 예외/소비 시점. 설명용이며 normative 기술 집합을 늘리지 않는다. |
| [docs/README.md](../README.md) | entry/설명/data6 | 6455 | `905ee80ddc529fc8500d0c22f0bc53abfdd2236b2673a77ca9fbbd5909fe1c5f` | 현재 candidate/유효 exact entry-1/역사 증거·문서 authority 구분과 navigation. source-only 문서를 managed payload에 요구하지 않는다. |
| [README.md](../../README.md) | entry/설명/data6 | 2239 | `c87ceef5954d38d9b9bfdfedf297d686685e1ae3d48cf3b49c414baf8757cccd` | 현재 candidate setup/navigation·미활성/미검증 경계. token 축약은 의미·경고·역사 기준을 보존한다. |
| [PRODUCT-CAPABILITIES.json](../../PRODUCT-CAPABILITIES.json) | entry/설명/data6 | 5108 | `9dbffd8485a8ffd1aaeb5ed0ec34d1cb71f27ab229d06d1923a93e15451afb5d` | delegated-ordinary-acceptance 행의 development evidence/status 설명. runtime 필드 및 나머지 capability 의미 불변; 데이터가 자체 권한을 부여하지 않는다. |

- 새 managed P: `49969df17f06e85cae8039c8dbd8cbf43a39f3ca8a317fceace4edd19596ad0b` (`product-release-49969df17f06e85cae8039c8`), delegation-1/29 paths.
- 비교 Q: `d4dd27cf8c98be1cd321b02d2dae62c9c6d2ff344ffa7034a5dd12a6df955526` (`product-release-d4dd27cf8c98be1cd321b02d`), 기존 M1/M2 수락 P 그대로. P와 Q는 서로 다르다.
- exact entry-1 predecessor: `2216a2634eb3fa5d6a8bfa7c7d4847b29fb2443ba7b367156c15b15ddb5a17e0`. 다른 entry-1 release를 새로 허용하지 않는다.
- DR-0005 제안 본문: 5690 bytes, SHA-256 `737c34eb9cc323185af0ceef0709c5a889b02a5a8ba5d04fbce3f203c09dbc5c`. 현재 Draft의 최종3절은 공란이다. 아래 삽입안은 이 CHORE에만 있으며 적용하지 않았다.
- Managed freeze/reader binding receipt: private `final-candidate-v2.json`, SHA-256 `cb7785b10aa90f8d71f8980753733fcaeac605b62da8e542fc11904da8ce3a5e`. 원본/결과 소비자는 최종 R1 및 Owner의 exact 결과·활성화 판단이다. source-only 이후 기록은 이 managed identity를 바꾸지 않는다.

### Proposed DR-0005 Final Sections

다음은 Owner가 위 exact 제안과 named amendments를 수락할 때만 DR-0005의 빈 절에 넣을 문안이다. 실제 결정 날짜와 Owner 원문·이 CHORE의 수락 당시 hash를 activation appendix에 결속한다. 이 제안의 작성 날짜를 발효일로 사용하지 않는다.

> Decision: Accept the exact delegation-1 successor identified in the A preparation record, limited to the accepted intent-bound ordinary isolated-worker accept grant, its actor/consumption/revocation/recovery rules, paired lifecycle schema 4 and exact entry-1 transition. The Owner retains intent and source-development result acceptance, all ungranted actions and parent acceptance. Activate only with the separate dated Owner activation record naming these exact document hashes, P identity and the clauses below. A development result, review verdict or synthetic installation does not activate them.
>
> Rationale: The bounded grant permits one named ordinary result acceptance while keeping the existing exact intent/Work identity, content checks, serialized publication and recovery guarantees. The source/installed entry and artifact-language guidance make the applicable project rules explicit. Reuse of identified unchanged assertions plus fresh consumer/artifact evidence is proportional to the prose delta. The reader observations support only their reported language/entry behavior; they do not establish general comprehension, public onboarding, caller authentication or unattended operation.
>
> Consequences: New schema-3 intent writes require delegation-1; new lifecycle actions use schema 4. The first durable new transition receipt bars downgrade to entry-1. A lawful durable delegated accept consumes its exact key even after cancellation/revocation, and selected revoke ancestry remains a barrier. Existing no-grant/provider-null human use and ordinary child/human parent boundaries remain. Operators retain exact sources and original recovery inputs; independent authentication, immutable-payload enforcement, production/public qualification and actual adoption remain unverified or separately authorized. Git publication and adopter application are not included.

### Proposed DR-0003 Lineage Appendix And Intake Interpretation

기존 DR-0003의 보호된 원문·기존 activation appendix·frontmatter는 수정하지 않는다. 별도 Owner 활성화 시 그 뒤에 `Delegation-1 Named Authority And Source-Entry Amendment — <actual date>`를 append하고 DR-0005의 exact 입력, 위17개 target·P 및 실제 Owner 원문을 연결한다. 지금 append하거나 발효하지 않는다.

제안하는 정확한 amendment 본문:

> Human authority remains the default. Only DR-0005's exact activated contract may permit the named distinct delegate one ordinary isolated-worker result acceptance for the accepted draft's exact Work, scope and consumption key. It grants no continuation finalization or reprioritization, phase-open or broader continuation authority, intent acceptance, rebind, reject, cancellation, revoke, lifecycle, Git or parent authority. Source-development result acceptance remains human. One control writer means one serialized cooperating Core writer under the existing guard; multiple permitted decision actors add no concurrent same-Work content-editing or uncoordinated-finalizer authority.
>
> This amends the Development Index's L-4 only for that exact ordinary acceptance exception; L-4 is not reclassified as CONT-only and every other prohibition remains. Onboarding criterion 4 continues to require exact human acceptance for the provider-null route; the separate isolated-worker exception does not turn that route into unattended acceptance. Criterion 10 continues to forbid self-acceptance as the Owner; an activated distinct delegate acts under its own recorded actor and exact grant, never as authenticated Owner. Criterion 13 remains the no-new-grant-root/no-silent-extension requirement for phase-open and continuation; ordinary acceptance under this amendment grants neither. Existing intake priority, public-readiness criteria and unknown coverage remain unchanged.
>
> The mirrored ordinary-result authority clauses in General Work (Delegation-1 Implementation Candidate), Guided Intent Formation (Draft And Acceptance and Delegation-1 Implementation Candidate), Reference (Human Review and Delegation-1 Implementation Candidate), the installed adapter's acceptance instructions, Agent Entry (Authority Floor/Start), Getting Started's review/default path, and the structural supplement's Work Decisions And Selections actor predicate gain only this same explicitly bounded exception. Default/historical human wording and every unrelated obligation retain their meaning. Concepts illustrates the distinction without becoming another normative authority.

위 문안은 named DR-0003 lineage amendment이며 Development Index 기존 L-4/criteria 원문을 소급 덮어쓰지 않는다. 활성화 시 exact appendix를 가리키는 source-only navigation만 기존 index에 더하는 제안이다. DR-0006이 이미 옮긴 규칙 소유권·accepted hash·역사는 유지한다.

### Proposed Source-Entry Navigation Amendment

DR-0006의 relocation 결과를 재승인하지 않는다. 그 후속 shipped AGENTS 경로만 위 exact target으로 수락할 때, `docs/development/WORKFLOW.md`의 Source And Installed Project Entry 마지막 문단을 아래로 대체하는 named source-entry amendment를 함께 결정하도록 준비한다. 수락된 현재 WORKFLOW bytes는 아직 main과 같다. 해당 location/entry 조항 이외의 source procedure 및 언어 정책은 바꾸지 않는다.

> At the DR-0006 source-only relocation, the unchanged AGENTS/CLAUDE entry had no verified automatic route to these source rules. The separately accepted A entry amendment adds a conditional route through source-only CONTRIBUTING when the agent is explicitly asked to develop Colvia itself in its trusted source checkout. An installed project still starts with its own rules and the verified manual/adapter from ./colvia view; presence inside a managed manual never selects source development. This route does not require runtime installation or typed Work creation, and adds no task-selection or execution authority. DR-0006's other relocated obligations and historical identities remain unchanged.

이 단락은 위 named DR-0003 source-entry appendix에 함께 명시하고 actual revised WORKFLOW hash를 활성화 기록에 남기는 제안이다. 새 source 언어 정책은 만들지 않는다. 이번 task의 shipped 영어/Owner 기록 한국어는 해당 task 지시일 뿐이다.

### DR-0002 / DR-0004 Successor And Frozen Labels

별도 activation 시 DR-0004의 entry-1 및 First B1 supplement에서 현재 ordinary accept·intent shape·window/schema·lifecycle/writer 설명 중 위 표에 특정한 부분만 DR-0005 successor로 대체한다. DR-0002/0003/0004는 전체 Superseded가 되지 않는다. 원래 accepted prefix, hashes, exact entry-1 predecessor, First B1의0600/0644 reader 관측 허용과 publication/sync 의미 및 무관한 보장은 보존한다. DR-0004의 후속 source-only appendix는 DR-0005의 exact activation과 이 표를 가리키되 과거 기록을 다시 쓰지 않는다.

Owner가 실제 활성화를 결정하면 exact frozen 문서 안의 Proposed/unactivated/preparation 라벨은 그 바이트를 준비하던 당시의 상태를 가리키며, 이름 붙인 source-only activation 기록이 그 후의 효력을 결정하도록 제안한다. 이것은 기존 DR-0004의 frozen-label 관행을 따르는 선택이다. 라벨을 바꾸려고 installed payload를 수정하거나 새 release를 만들어서는 안 된다. 이 제안 자체는 아직 미활성이고, Owner가 다른 라벨 처리 방식을 선택해 managed bytes를 바꾸면 affected consumer/reader와 새 artifact16을 다시 검증해야 한다.

### Owner Decisions Remaining

1. 이 A의 exact 결과와 보고된 reader 미달/한계를 수락할지 결정한다. 기존 M1/M2 수락은 유지하며 A 결과 수락으로 재사용하지 않는다.
2. DR-0005의 exact successor, 위 DR-0003 authority/source-entry amendment와 DR-0004 lineage/frozen-label 처리를 수락·활성화할지 별도로 결정한다. 이때 실제 Owner 원문·날짜·exact bytes를 해당 source-only 기록에 결속한다.
3. [설치본 label 선택지](#frozen-labels-source-activation-and-installed-reader-consequences) 중 source만 활성화하고 설치 위임 사용을 보류할지, label을 고친 새 release를 검증한 뒤 사용할지 결정한다. 어느 쪽도 아직 선택되지 않았다.
4. [예상 oracle non-pass와 후속 후보](#expected-complete-run-nonpass-and-follow-up-owner)의 별도 선정·해소/처분 및 계약 활성화 선행조건 여부를 정한다. 현재 source complete PASS는 없다.
5. Git/공개 release/각 실제 adopter의 적용은 각각 별도 결정한다. 적용 권고는 현재 **보류** 상태다. 검토된 소스 변경과 합성 검증만으로 현 운영 설치를 바꾸지 않는다.

기존 uncommitted source worktree와 r11 anchor, A frozen inputs/실행 결과/reader 원문은 위 Owner 결정과 exact evidence 소비가 끝날 때까지 기존 경로에서 보존한다. 이후 사용/복구 필요와 승인 조건을 다시 확인한다. 빈 scratch와 소모 완료 reserve는 최종 R1 종료 후 정리할 수 있으며, 보존과 cleanup을 구별해 기록한다.


### Exact Artifact Closure Before R1

현재 상태 안내: 아래는 첫 A P의 역사 결과다. 현재 검토 대상은 `final-candidate-v2.json`의 P `49969df17f06e85cae8039c8dbd8cbf43a39f3ca8a317fceace4edd19596ad0b`이며 최신 실행은 Corrected Artifact Closure에 있다. 아래 원래 수치와 기록은 유지한다.

새 P `ef6e7d918e13dd78753c5e9ee2c0d06235024679c12257bcfebdfe85ab801ea6`와 Q `d4dd27cf8c98be1cd321b02d2dae62c9c6d2ff344ffa7034a5dd12a6df955526`의 C01–C16은 normal16/16 PASS, 611.68초, exit0이다. 전체656 ID를 수집하되 선택16만 실행했고 skip/xfail/미시작/미완료0, 입력 drift0, group absence 확인·cleanup 오류0이다. 실행 source digest는 `2620bceb916eb7d2ed8e7e6048fad62fe020fac0d9e8f962d51e8f15c8d4bb32`다. Source-only 후속 구조 보충/이 기록은 그 snapshot과 구별하고 managed29 bytes 동일성으로 결속했다. 원본 result SHA-256 `08efb9bdbe311a2564490e73072a1ea911c5731d5d61930f209368770d1be1f3`, counts `b578722df2643dcaaf253afad9d72179fee3fba5ef9a5125f3652be7710848dc`, executed order `1cf92322fca59bf9e342df6d9f66d61c0df60b8b68bc595e57b15e42622ce1a6`를 보존한다.

기존 r11 normal656/parent-O656·retained17씩은 exact 원본과 변경 영향 분석으로 제한 재사용했다. Source-only code-fence를 오인하는 legacy link assertion은 새 PASS로 재사용하지 않았고 실제 GFM 검사로 대체했다. 최종 GFM22파일323 link/anchor 오류0, offline token3898(AGENTS886/README448/Getting Started2564), 실행 입력104개 동일을 확인했다. 실제 reader는 언어5/5 관찰·엄격 Read1/5 PASS 및4미달이며 별도 표의 과도한 설명 한계를 유지한다.

최신 remote main을 `git ls-remote origin refs/heads/main`으로 재확인한 값도 `a93f71c359c4f0a9d57fcfb50d5999160e870f77`이다. source procedure5개는 그 bytes와 같고 development index에는 task navigation2개만 더했다. HEAD는 `d86bd1fd7754144e5c8538712724ae78571941bf`, staged content는 HEAD와 같다. Git publication·계약 활성화·실제 adopter 변경은 없다.


## R1 First Result And Bounded Correction — 2026-10-18

Fresh Claude Opus5.5 (`claude-opus-5-5`), `claude.ai/firstParty/pro`, session `85554421-1e35-4b14-9238-65bfc4056628`. 도구 없는 정적 검토132.6초, exit0, input drift0/102, group absence 확인·cleanup 오류0. 입력862392 bytes SHA-256 `d809a34d86c9cf01fb02fe552e5da150e4f4fbae8b54e0990659b90a547759dc`. 판정은 Blocker0·필수3·비차단7이다. 아래 원문은 Driver 처분/Owner 결정과 구별한다.

### Reviewer Verbatim

# 최종 R1 정적 검토: CHORE-20261018-001 (A 문서 보정·활성화 준비)

이 세션에는 도구가 없습니다. 그래서 plan 파일 작성, ExitPlanMode 호출, 실행은 하지 않았습니다. 아래 내용은 제공된 packet만 읽고 내린 정적 판단입니다. 이 verdict는 Owner의 결과 수락, 범위 확대, 계약 활성화를 대신하지 않습니다.

## 결론

- **Blocker: 0건**
- **결과 제출 전 필수: 3건** (R1-A-M1–M3)
- **비차단: 7건** (R1-A-N1–N7)

**A 결과로 충분한 부분**
- 제품 실행 bytes(protected 104)는 변경이 없습니다.
- 변경된 managed 문서의 직접 소비자는 다음으로 새로 확인했습니다: focused normal 8, parent-O 2, artifact16.
- 그 외 영향 없는 assertion은 r11 656×2를 제한적으로 재사용했습니다. 이 구조는 MAINTAINING의 cumulative reuse 규칙에 맞습니다.

**reader 결과의 판정**
- 결과는 투명하고, 사전 기준을 바꾸지 않았으며, 재시도로 PASS를 만들지도 않았습니다.
- A의 완료 기준 2("관찰하고 성공/실패와 제한을 기록")에 대해서는 이것으로 충분합니다.
- 교정 관찰을 추가로 강제하지는 않습니다. 다만 R-C에서 드러난 adapter 문구 문제는 아래 N1로 남깁니다.

---

## 결과 제출 전 필수

### R1-A-M1. SECURITY-AND-SUPPORT의 CRLF 예외 범위가 다른 기술 계약과 모순

**근거 (정적)**
- `docs/SECURITY-AND-SUPPORT.md` Runtime And Scope 절은 "Only verified active checkout-1 or entry-1 enables this unchanged-CRLF exception."이라고 씁니다.
- 반면 같은 제안 집합의 다음 문서는 모두 delegation-1을 포함합니다.
  - `docs/GENERAL-WORK.md`: "checkout-1, entry-1 or delegation-1"
  - `docs/MAINTAINING.md` Checkout Proof
  - `PRODUCT-CAPABILITIES.json` same-repository 행
- 이 문장은 r11에서 이어진 것이지만, A의 범위인 "기술 계약 11개 점검·current-candidate 안내 정리"에 해당합니다.

**결과**
- 이 exact bytes로 활성화하면 기술 계약 11개 안에 서로 모순되는 규범이 생깁니다.

**최소 수정 (둘 중 하나)**
- (a) 그 한 문장에 delegation-1을 추가합니다. 수정하면 managed bytes가 바뀌므로 다음이 필요합니다.
  - 새 P 산출
  - artifact16 1회
  - GFM 검사
  - reuse-anchor `allowed_changed` 보정과 selfcheck (N6 참조)
  - SECURITY는 reader가 읽지 않았고 token 대상도 아니므로 reader와 token은 재실행하지 않습니다.
- (b) 수정하지 않는다면, "알려진 모순, 활성화 전 보정 필요"로 CHORE의 Owner Decisions에 명시합니다.

### R1-A-M2. legacy link 테스트가 현재 source에서 실패할 것으로 예상되는데, 이 사실이 결과에 명시되지 않음

**근거**
- `static-pre-r1.json`의 disposition과 CHORE의 Exact Artifact Closure 기록에 따르면, `test_document_port_local_links_resolve`의 raw regex가 main DECISION-GUIDE의 fenced 링크 2개를 링크로 오인합니다.

**판단**
- A가 이 테스트를 PASS로 재사용하지 않고 GFM 감사로 대체한 판단은 타당합니다.
- 하지만 이 판단에는 다음 결론이 따릅니다.
  - 현재 source(main+A)에서 전체 suite를 돌리면 1건이 실패할 것으로 예상됩니다. 이는 정적 예측이며 실행하지 않았습니다.
  - 따라서 이후 어떤 complete matrix나 release 자격도 이 실패에 막힙니다.
- CHORE에는 "한계를 R1에 제공"한다고만 적혀 있습니다. 다음 complete run의 예상 결과와 후속 소유자가 없습니다.

**최소 수정 (source-only 문구, managed bytes 불변)**
- CHORE의 Owner Decisions Remaining에 한 항목을 추가합니다.
  - 미실행 상태에서 예상되는 non-pass 1건
  - 원인
  - 별도 test-oracle 보정 후보(DR-0003 New Source Candidates 경로)
- 이 항목이 활성화나 release 자격의 선행 조건인지는 Owner가 정합니다.

### R1-A-M3. frozen label이 설치 adopter에게 미치는 결과가 활성화안에 드러나지 않음

**근거 (정적)**
- 설치본에서 agent가 읽을 수 있는 문서는 managed payload뿐입니다. source-only 활성화 기록은 볼 수 없습니다.
  - `AGENTS.md`: "describe the unactivated delegation-1 implementation candidate"
  - adapter "Exact Delegated Ordinary Acceptance": "only under the activated delegation-1 contract"
- 반면 Core(`work.py` `_bound_delegation` 경로)는 활성화 여부와 관계없이 유효한 grant를 허용합니다.

**결과**
- DR-0004 방식으로 라벨을 그대로 두고 활성화하면, 이 P를 쓰는 adopter의 agent는 위임 수락을 문구상 금지된 것으로 읽습니다. 안전한 방향(fail-closed)이긴 합니다.
- 결과적으로 prose와 Core의 동작이 갈립니다. 활성화 후에도 adopter 쪽에서는 기능이 사실상 막혀 있게 됩니다.
- source 전용 문서였던 DR-0004 선례와 달리, 이번에는 adopter가 실제로 영향을 받습니다.

**최소 수정**
- CHORE의 "DR-0002 / DR-0004 Successor And Frozen Labels" 절에 이 결과를 한 문단으로 적습니다.
- Owner가 고를 선택지를 명시합니다.
  1. frozen label을 수용하고 adopter에서는 비활성 상태로 둡니다.
  2. 라벨을 고친 새 release를 만들고, 영향받는 consumer·reader와 artifact16을 다시 검증합니다.

---

## 비차단

- **R1-A-N1. adapter의 저장 경계 문구 (R-C 관찰)**
  - R-C가 말한 "문서 저장 전에는 intent 수락과 Work가 필요하다"는 adapter step 4의 "Project Markdown created after Work start belongs in the Work scope"를 과일반화한 것으로 보입니다. Reference Project Document Assistance의 "explicit request authorizes that narrative edit"와 어긋납니다.
  - 제품 정책으로 채택하지 않은 Driver 처분은 적절합니다.
  - 다음에 managed bytes를 고칠 때 adapter "Requested Project Documents"에 한 문장을 추가하기를 권고합니다: Work가 없고 범위 제약도 없으면, 명시적 기록 요청이 narrative 편집을 승인한다.
  - M1(a)과 함께 처리하면 artifact 재실행 비용이 추가되지 않습니다.

- **R1-A-N2. managed `docs/README.md` 표의 "Claude is a pointer" (R-E 관찰)**
  - 이 문구는 Harness 자신의 CLAUDE.md를 가리킵니다. 그런데 R-E는 이를 project CLAUDE 정책으로 오인했습니다.
  - Getting Started는 기존 project의 CLAUDE를 보존하라고 구분해 두었으므로, 실제 지침 충돌은 아닙니다. 추후 문구 정리 후보입니다.

- **R1-A-N3. adapter 머리말 라벨 불일치**
  - adapter: "Delegation-1 implementation candidate; qualification and activation remain pending"
  - 나머지 문서: "development candidate; contract activation remains pending"
  - frozen label로 수용할 수 있습니다. 문구를 다시 고칠 때 맞추면 됩니다.

- **R1-A-N4. GENERAL-WORK의 CRLF 문단 링크**
  - old-window worker의 rebind 절차를 historical 절인 "Transition To Entry-1"로 안내합니다.
  - delegation-1 전환 시의 rebind는 OPERATIONS Delegation-1 절에 있으므로, 링크 대상을 그 절로 맞추는 것을 권고합니다.

- **R1-A-N5. `PRODUCT-CAPABILITIES.json` 날짜 불일치**
  - 최상위 `evidence_as_of`는 2026-10-07, 갱신된 행은 2026-10-18입니다. 의미에는 영향이 없습니다.

- **R1-A-N6. 재실행 시 admission 입력 보정 필요**
  - `reuse-anchor.json`의 `allowed_changed`에 `docs/development/CHECKOUT-1-STRUCTURE.md`가 없습니다.
  - 현재 live source로 native snapshot을 다시 만들면 `a_admission.validate_anchor`가 "outside reviewed prose"로 거부합니다. fail-closed이므로 올바른 동작입니다.
  - M1(a)이나 label 보정으로 artifact16을 다시 돌릴 경우, 고정 admission 입력 변경과 selfcheck 재실행을 계획에 포함해야 합니다.

- **R1-A-N7. 활성화 bookkeeping 누락 목록** (활성화를 결정할 때 함께 처리)
  - (a) DECISION-GUIDE catalog에 DR-0005 행이 없습니다. DR-0003 상태 문구에 DR-0005 amendment를 반영하는 항목도 제안안에 없습니다.
  - (b) DR-0005 본문의 "Proposed DR-0003 Amendment" 인용문과 CHORE의 상세 amendment 문안이 서로 다릅니다. CHORE 쪽이 더 넓어 cancellation, phase-open, criteria 4/10/13 해석을 포함합니다. 활성화 기록에서 CHORE 문안이 우선한다고 명시해야 합니다.
  - (c) DR-0005의 활성화 조건은 "complete normal/parent-O" 링크를 요구합니다. 그런데 그 증거는 Q-source에서 실행된 inherited anchor입니다. 새 P에 대한 complete 실행이 아니라는 점을 활성화 기록에 명시해야 합니다.

---

## 핵심 판단

| 항목 | 판단 |
|---|---|
| 기술 계약 11개와 entry/설명/data 6개의 구분 | 적절합니다. CONCEPTS, README, CAPABILITIES를 normative로 승격하지 않았습니다. M1 한 문장은 예외입니다. |
| source 정합 | source procedure 5개가 main bytes와 같고, index에는 navigation 2줄만 추가됐습니다. |
| 실행·기록·복구 의미 불변 | protected 104 bytes·mode가 같고 runtime 선언도 같습니다. M1/M2 구현을 다시 검토할 사유는 없습니다. |
| native 적응 | 다음 safeguard가 갖춰져 있습니다: focused-parent-O를 정확히 2개 ID로 제한(controller와 runner 이중 검사), 최적화 불일치 시 양방향 거부, smoke 선행, `test.sb`/`acquire.sb` 불변, lock·interpreter·approval 고정, selfcheck 59, TERM/KILL 2. |
| reader | 언어 선택 5/5 관찰, 엄격 기준 1/5 PASS. 투명하게 보고된 결과로서 A 준비에 충분합니다. 일반 이해, 자율 CLI 진입, adopter 사용에 대한 근거는 아닙니다. |
| WORKFLOW unchanged-entry 문장 | 수락된 bytes를 유지하고, 활성화 때 대체할 문단을 준비해 둔 처분은 타당합니다. |

## 증거 구분

**정적 판단 (이 리뷰)**
- 위의 모든 지적
- 문서 간 대조
- controls diff와 wrapper 검토

**Driver 실행 증거 (이 리뷰는 재현하지 않음)**

| 실행 | 결과 |
|---|---|
| safety | 59 |
| TERM/KILL | 2 |
| canary, smoke | 7/7 |
| focused normal | 8/8 |
| focused parent-O | 2/2 |
| artifact | 16/16 (611.68초) |
| reader | 5회 실행 |
| GFM | 323 링크, 오류 0 |
| token | 3898 |

**inherited (Q-source 기준, P의 fresh 결과 아님)**
- r11 normal 656 / parent-O 656
- retained 17×2

**미확인·미실행**
- legacy link 테스트의 실제 실패 여부
- live source에서의 전체 suite
- 설치 adopter에서 frozen label 아래 agent가 실제로 어떻게 동작하는지
- host 인증과 불변 payload 강제
- 실제 adopter 사용

## Owner 결정 경계

이 리뷰는 다음 어느 것도 부여하지 않습니다.
- A 결과 수락
- DR-0005, DR-0003, WORKFLOW amendment 활성화
- Git 작업
- release
- adopter 적용

Owner가 정할 사항은 다음과 같습니다.
- M1: 지금 고칠지(a), 기록만 할지(b)
- M3: frozen label을 유지할지, 라벨을 고친 release를 만들지
- M2: test-oracle 보정이 활성화나 release 자격의 선행 조건인지
- N7: 활성화 기록의 bookkeeping 범위

### Driver Disposition

| 항목 | 처분 |
| --- | --- |
| M1 | accept. 기존 A의 current-contract 정합 승인으로 SECURITY의 CRLF 문장에 delegation-1을 더한다. 새로운 지원이나 runtime 정책을 채택하는 것이 아니라 기존 구현/GENERAL-WORK/CAPABILITIES와 맞춘다. N6을 반영한 별도 fixed correction 입력에서 safety59·canary·smoke prerequisite와 artifact16을 실행한다. reader5개가 SECURITY를 읽지 않았고 token3파일도 불변이므로 그 둘은 재실행하지 않는다. 정상/O 문서소비자 결과는 이번 한 문구와 직접 관계가 없으며 보호된 실행·assertion은 그대로다. 전체656은 반복하지 않는다. |
| M2 | accept. 아래 예상 non-pass와 별도 test-oracle 후보/소유/선정 조건을 명시한다. 실제 test 실패 재현으로 세지 않는다. |
| M3 | accept. 아래 설치본의 label 한계와 두 activation 선택지를 명시한다. 지금 label이나 activation state를 바꾸지 않는다. |
| N1 | accept as nonblocking. R-C의 저장 전 typed Work 강제 발언은 제품 정책으로 채택하지 않는다. 향후 문서저장/first-entry 지침을 별도로 보정할 때 adapter의 명시적 narrative 편집 범위를 문장으로 더하고 해당 reader를 확인한다. 이번 필수 CRLF 한 문장 보정에 의미가 다른 adapter 변경을 합쳐 새 entry 관찰 범위를 넓히지 않는다. |
| N2 | accept as nonblocking. managed CLAUDE 설명은 Harness payload 자체에 한정하며 project CLAUDE 규칙이 아니다. 현재 Getting Started 보존 지침을 따른다. 후속 first-entry 문구 보정의 대상으로 유지한다. |
| N3 | accept as nonblocking. qualification/activation pending 머리말은 frozen 준비 label로 유지하고 아래 Owner label 선택에 함께 포함한다. 새 PASS claim으로 해석하지 않는다. |
| N4 | accept as nonblocking. GENERAL-WORK의 old-window CRLF worker 링크는 역사 transition으로 남고 현 delegation-1 재개는 OPERATIONS의 해당 절을 따른다. 다음 관련 문구 보정 때 링크를 정리한다. |
| N5 | accept as nonblocking. CAPABILITIES 최상위 날짜는 원래 evidence 시점이고 개별 delegated 행에 2026-10-18 관측을 명시했다. 단일 최신 날짜로 과거 행까지 재검증한 듯 보이지 않도록 행별 범위를 유지한다. |
| N6 | accept. 새 correction snapshot의 allowed_changed에 source-only CHECKOUT-1-STRUCTURE를 정확히 포함한다. 기존 실행 입력/원본은 바꾸지 않는다. 새 입력을 기존 같은59 safety assertions로 검증하고 isolation/policy/mode guard는 그대로 둔다. |
| N7 | accept. 아래 exact 활성화 bookkeeping안으로 source-only catalog/lineage, 상세 amendment 우선범위, inherited complete anchor의 의미를 명시한다. 실제 accepted 문서는 아직 수정하지 않는다. |

R1은 reader의 관찰/성공·실패·제한 기록이 A 완료 기준2를 충족하며 추가 관찰을 강제하지 않는다고 판단했다. Driver는 이를 현재 제한된 준비 결과로만 채택하며 strict Read1/5를5/5 PASS로 바꾸지 않는다. Reviewer의 M1(a/b)와 label 선택 제안은 새로운 승인 요구가 아니다. 이미 승인된 A 문구 정합 안에서 M1(a)를 수행하고, 실제 activation/adopter 선택은 Owner에게 남긴다.

### Expected Complete-Run Nonpass And Follow-up Owner

현재 main+A source의 전체 suite를 새로 실행하면 `test_document_port_local_links_resolve`가 fenced 역사 링크2개를 실제 링크로 오인하여 알려진1건 non-pass가 날 것으로 정적으로 예상한다. 이 반례는 실행하지 않았으며 다른 실패가 없다는 보장도 아니다. 기존 full656×2를 현재 source의 새 complete PASS로 표기하지 않는다. A의 source/payload 실제 link coverage는 별도 GFM 검사로 채웠다.

후속 후보는 “문서 링크 oracle을 실제 Markdown 링크에 한정하고 fenced 역사 예시를 제외하도록 보정”이다. 소유자는 Colvia Source Driver이며, Owner가 DR-0003/WORKFLOW의 New Source Candidates 경로로 별도 선정·범위를 승인한 뒤에만 test source 보정과 집중 검증을 시작한다. A는 이 테스트/기존 main 문서를 고치거나 새 task를 시작하지 않는다. 다음 complete/release 검증을 계획하기 전에 이 예상 실패를 해소하거나 명시된 적격성 조건/미해결 처분을 결정해야 하며, 기록만으로 실패가 PASS가 되지는 않는다. 계약 활성화의 선행조건으로도 삼을지는 별도 Owner 판단이다.

### Frozen Labels: Source Activation And Installed Reader Consequences

위 frozen-label 제안은 설치 reader가 source-only activation 기록을 자동으로 읽을 수 없다는 한계가 있다. AGENTS의 unactivated 안내와 adapter의 activated-contract 조건은 그대로인 반면 Core에는 source 결정의 activation을 조회하는 필드/강제기가 없다. 따라서 source 계약만 활성화해도 이 payload의 agent가 위임 수락을 비활성으로 해석해 보류할 수 있다. 이는 문구/실행 가능성 사이의 정적 불일치이며 실제 adopter 관찰로 재현한 결과가 아니다. Core가 자동으로 비활성화된다는 뜻도 아니다.

Owner의 두 선택은 다음과 같다.

1. exact frozen labels를 유지하고 source 계약만 활성화한다. 설치 adopter의 delegated 기능은 사용 보류 상태로 두며, 이 source-only 기록을 설치 진입/기능 준비 완료로 주장하지 않는다. 기존 human/no-grant 경로와 별도 adopter 적용 결정은 유지한다.
2. 활성화 의미와 맞는 managed entry/adapter/index label을 별도 정확한 문안으로 고쳐 새 release identity를 만든다. 해당 문구를 소비하는 reader/consumer와 artifact16을 검증한 뒤, 그 새 bytes를 Owner가 수락하고 adopter 적용을 별도로 결정한다.

A는 이 둘을 자동 선택·발효하지 않는다. 아래 보정 P는 CRLF 정합만 바꾸며 frozen-label 의미는 그대로다. 위 선택지 외의 “source 기록을 읽었다고 추정하고 설치 agent 권한을 확대”하는 우회는 제안하지 않는다.

### Proposed Activation Bookkeeping Delta

Owner가 activation을 실제 결정할 때 아래 source-only 조치를 함께 검토·적용하도록 제안한다. 지금 main의 accepted source 문서/기존 DR activation 기록은 바꾸지 않는다.

- Decision Guide catalog에 DR-0005를 `Accepted; exact delegation-1 ordinary accept and named authority/source-entry amendment effective <actual Owner activation date>; see exact activation record`로 연결한다. 해당 행은 실제 결정 전에는 넣지 않는다. DR-0003 catalog 설명에는 그 named authority/source-entry amendment가 더해졌음을 표시하며 기존 DR-0004/DR-0006 계보를 유지한다.
- DR-0005의 Proposed DR-0003 Amendment는 요약이고, 실제 수락 대상은 이 CHORE의 `Proposed DR-0003 Lineage Appendix And Intake Interpretation`에 있는 상세 문안이다. cancellation/phase-open 및 criteria4/10/13 해석을 포함한 그 exact 문안이 named 범위에서 우선한다는 문장을 DR-0005 activation appendix에 넣는다. 기존 summary/historical bytes를 소급 수락 범위로 바꾸지 않는다.
- DR-0005의 complete normal/parent-O 조건은 원래 r11/Q source의656×2와 현재 P까지의 cumulative impact analysis·fresh consumer/정확한 artifact evidence를 조합한 것으로 명시한다. 이것은 P source에서의 fresh complete 실행이 아니다. strict reader 미달, legacy link oracle 예상 non-pass, label/adopter 제약과 남은 host/platform 한계를 함께 연결한다. Owner가 이 조합을 수락하는 것과 어떤 release/public 자격을 부여하는 것은 별개다.

이 source-only 기록 변경과 SECURITY 한 문장만 다음 R1의 delta다. 추가 reader retry, 전수 regression, 실제 activation/Git/adopter 실행은 없다. 실행에 필요한 새 correction copy는 기존 root 아래의 별도 task-owned 입력이며 기존 snapshot을 덮어쓰지 않는다.


### Correction Admission And Evidence Reuse

현재 상태 안내: 이 절의 진행형 표현은 correction 실행 중 작성한 체크포인트다. artifact16은 이후612.358초16/16 PASS로 끝났고 최종 R1도 완료했다. 해당 결과는 아래 Corrected Artifact Closure와 Final R1 And Driver Closeout에 있다.

보정 native source digest는 `3f8ec70b867d8e7022a578763041520e2c95d58fc43cb575c4cc8c3353eb6f8a`, 새 최종 P는 `49969df17f06e85cae8039c8dbd8cbf43a39f3ca8a317fceace4edd19596ad0b`다. Q는 기존 수락 P 그대로다. Current table/v2 binding이 최신 activation target이며 첫 A P와611.68초 artifact 결과는 이전 입력의 역사 증거로 남는다. 최초 frozen source와 비교한 source 변경은 SECURITY 한 문장, source-only 구조 보충문, 이 진행 기록뿐이다. runtime/test/permission/record/recovery 실행 bytes는 불변이다.

Correction 준비에서 제품 자식 실행 전 거부2건을 보존했다. 첫째는 nested correction 경로가 기존 `campaign storage root` 형식과 맞지 않았고, 둘째는 controls manifest에 단순 SHA 대신 source-file metadata object를 넣은 준비 오류였다. 둘 다 common.config가 자식 spawn 전에 거부하여 제품 테스트 실행 수0이다. 승인된 artifact root의 `/colvia-rule-entry-language-correction-20261018/implementation`을 새로 사용하고 올바른 기존 controls schema로 r01 invocation을 만들었다. 원본 실패 입력은 덮어쓰지 않았고 실제 config/anchor 사전 검사를 통과했다. common/controller/runner/Seatbelt policy를 완화하지 않았다. 새 launcher는 r00→r01 path 및 identity filename만 다르다.

새 입력의 safety59·TERM/KILL2, acquire/canary/collection, smoke7은 통과했고 artifact16을 진행한다. 기존 focused8/O2와 reader5, token3898은 변경 영향을 위와 같이 한정해 재사용한다. Security를 어느 reader도 Read하지 않았고 token3개 파일 hash도 같다는 점을 다시 확인했다. 이들은 새 P의 fresh 실행이라고 표시하지 않는다.

보존/정리: 첫 A의 소비 완료 native reserve512MiB와 거부된 nested attempt의 reserve512MiB를 각각 정리했다. 원본 입력·실패 기록·reader 결과는 보존한다. source worktree/기존 실행 경로를 이동·retarget하지 않았고, 새 correction 경로만 추가했다. 새 reserve는 현재 native 검증의 소비자가 있어 유지하며 review reserve는 후속 R1이 사용한다.


### Corrected Artifact Closure

최종 P `49969df17f06e85cae8039c8dbd8cbf43a39f3ca8a317fceace4edd19596ad0b`의 C01–C16 normal16/16 PASS, 612.358초, exit0. 새 source digest `3f8ec70b867d8e7022a578763041520e2c95d58fc43cb575c4cc8c3353eb6f8a`에서 입력 drift0, skip/xfail/미시작/미완료0, 자연 종료·group absence 확인·cleanup 오류0이다. 이전 source와 ordered test ID/occurrence656개는 정확히 같다. control80개 중 차이는 campaign root data1개뿐이고 실행 code/Seatbelt는 같다. r01 launcher는 고정 경로/identity 파일명만 바뀌었다. Artifact result SHA-256 `baefcf03f1ed7261a02ac9030961ab1bbc156ef1f000c4c7096cfebdecf3b305`, counts `b578722df2643dcaaf253afad9d72179fee3fba5ef9a5125f3652be7710848dc`, 실행 ID 원문 `1a96c003d3ab388891827401281a0f25a586ae44ed0b69f8eb18e2e392ec0f9f`를 보존한다.

이는 첫 A P의16/16을 새 P PASS로 바꾼 것이 아니라 보정된 새 P를 실제로 실행한 별도 결과다. 기존 reader/normal8/O2/token은 한 문장 변경의 영향 분석으로 재사용하며 P의 새 reader/complete PASS로 표기하지 않는다. Runtime/record/권한/복구 의미는 바꾸지 않았고 새 전체656×2는 수행하지 않았다. M2 예상 test-oracle non-pass와 M3 label/adopter 선택 및 N7 bookkeeping은 위 source-only 제안대로 유지한다.


## Final R1 And Driver Closeout

Fresh Claude Opus5.5 (`claude-opus-5-5`), `claude.ai/firstParty/pro`, session `92cdcde2-f681-40bc-b02a-62cab3cc9084`의 tools 없는 정적 검토다. 실행 97.87초, exit0, 입력 drift0/44, group absence 확인·cleanup 오류0. 입력317107 bytes SHA-256 `bd4d65eaf931788451a953c5eb0074dd6ed1b8a4abc9cf7049cdea6ff0186b7c`. 이번 A의 정적 review3회 누적468.44초다. R0→첫 R1→보정 R1의 원문과 각 처분을 이 기록에 보존했다.

최종 판정은 Blocker0·필수수정0·비차단6이다. 첫 R1 필수 M1–M3는 모두 해소됐다. 아래 원문은 전달받은 그대로 fenced Markdown에 보존하며 Driver 판단이나 Owner 승인으로 바꾸지 않는다.

### Final Reviewer Verbatim

````markdown
# 후속 R1 정적 검토: CHORE-20261018-001 (첫 R1 필수 M1–M3 보정 확인)

이 세션에는 도구가 없습니다. plan 파일 작성, ExitPlanMode 호출, 실행, 편집, 위임은 하지 않았습니다. 아래 내용은 제공된 packet만 읽고 내린 정적 판단입니다. 이 verdict는 Owner의 A 결과 수락, 계약 활성화, label 선택, Git 작업, adopter 적용을 대신하지 않습니다.

## 결론

- **Blocker: 0건**
- **필수수정: 0건**
- **비차단: 6건** (R1-F-N1–N6)

첫 R1의 필수 M1–M3는 모두 해소됐습니다. 이번 좁은 delta가 이미 검토된 M1/M2 구현과 충돌하는 지점은 찾지 못했습니다. 근거는 다음과 같습니다.

- protected 실행 bytes 104개가 변경되지 않았습니다.
- runtime 선언과 controls 실행 코드도 같습니다.

현재 final-candidate-v2와 exact 활성화안은 Owner에게 제시할 수 있는 상태입니다. 아래 한계는 함께 보고해야 합니다.

---

## 필수 M1–M3 해소 판정

### M1. SECURITY의 CRLF 예외 범위 — 해소

**diff (정적 확인)**
- 바뀐 것은 `docs/SECURITY-AND-SUPPORT.md` Runtime And Scope의 한 문장뿐입니다.
- 문장은 "Only verified active checkout-1, entry-1 or delegation-1 enables this unchanged-CRLF exception."입니다.

**다른 계약과의 정합 (정적 확인)**
- `docs/GENERAL-WORK.md` 문장과 일치합니다: "requires verified active checkout-1, entry-1 or delegation-1 inventory"
- `docs/MAINTAINING.md` Checkout Proof 문장과 일치합니다: "Only a verified active checkout-1, entry-1 or delegation-1 inventory"

**hash 대조 (정적 확인)**
- 수정본 hash `9be4676c…`가 다음 세 곳에서 같습니다.
  - Exact Successor Proposal 표
  - `final-candidate-v2.json`의 `managed_files`/`successor_documents`
  - P inventory
- 크기는 Q 8632 bytes → 8687 bytes입니다. 이는 추가한 문자열 `", … or delegation-1"`의 길이와 맞습니다.

**불변 조건 (정적 확인)**
- C16 marker 대상 4파일(README, MAINTAINING, OPERATIONS, SKILL)은 변경되지 않았습니다.
- C09 조건인 P ≠ Q가 유지됩니다: `49969df1…` ≠ `d4dd27cf…`.

**실행 증거 (Driver 기록이며 재현하지 않음)**

| 항목 | 결과 |
|---|---|
| safety | 59 OK |
| TERM/KILL | 2 |
| acquire / canary / collect | PASS |
| smoke | 7/7 |
| artifact (`source_digest 3f8ec70b…`) | 16/16, 612.358초, skip/xfail/미시작/미완료 0, group absent, cleanup 오류 0 |

### M2. legacy link oracle의 예상 non-pass — 해소

"Expected Complete-Run Nonpass And Follow-up Owner" 절에 다음이 모두 들어 있습니다.
- `test_document_port_local_links_resolve`가 1건 non-pass를 낼 것이라는 **정적 예측**이며, 실행하지 않았다는 사실
- 다른 실패가 없다는 보장은 아니라는 점
- 원인: fenced 역사 링크 2개를 링크로 오인
- 후속 후보: 실제 Markdown 링크로 한정하는 oracle 보정
- 소유자: Source Driver
- 시작 조건: Owner가 New Source Candidates 경로로 선정한 뒤
- release·complete 검증 전에 해소하거나 처분해야 한다는 점
- 활성화 선행조건으로 삼을지는 Owner가 판단한다는 점

예측을 실패 재현으로 세지 않았고, 656×2를 현재 source의 complete PASS로 표기하지도 않았습니다.

### M3. frozen label이 설치 reader에 미치는 결과 — 해소

"Frozen Labels: Source Activation And Installed Reader Consequences" 절의 내용은 다음과 같습니다.
- Core에는 source activation 상태를 조회하는 기능이 없습니다.
- 설치된 AGENTS·adapter 문구 때문에 agent가 위임 수락을 보류할 수 있습니다(fail-closed).
- 이것은 정적 불일치이며, 실제 adopter에서 재현한 결과가 아닙니다.
- Owner의 두 선택지가 명시돼 있습니다.
  1. source만 활성화하고 adopter의 위임 사용은 보류합니다.
  2. label을 고친 새 release를 만들고 영향받는 검증을 다시 수행합니다.
- 선택을 자동으로 하지 않고, 권한을 넓히는 우회도 제안하지 않습니다.

### N7 bookkeeping — 준비 완료, 미적용

"Proposed Activation Bookkeeping Delta"에 다음이 있습니다.
- catalog 행과 DR-0003 계보 표시
- 상세 CHORE 문안이 DR-0005 요약보다 우선한다는 문장
- inherited complete anchor가 P에서 새로 실행한 결과가 아니라는 명시

---

## 비차단

**R1-F-N1. 보정본의 GFM 수치가 다시 기록되지 않았습니다.**
- 근거:
  - `static-corrected.json`의 hash `97c59072…`가 고정 admission identity의 `static-preparation.json`과 같습니다.
  - 따라서 GFM 22파일, 323 link 결과는 첫 A source에서 나온 값입니다.
  - 바뀐 문장에는 링크나 강조 markup이 없으므로, 구조에 영향이 없다고 정적으로 판단합니다.
- 최소 처분: CHORE에 "GFM 323은 첫 A 결과를 재사용하며, 변경 문장에는 링크가 없다"는 한 줄을 넣습니다. 비용이 작으므로 GFM 검사를 다시 돌려도 됩니다.

**R1-F-N2. focused 테스트의 SECURITY 소비를 "직접 관계 없음"으로 단정했습니다.**
- 근거:
  - `test_document_port_managed_payload_generic_disclosure_guard`는 focused 대상이지만 `direct_consumers` 목록에는 없습니다.
  - 이 테스트는 managed payload 전체를 generic하게 검사할 가능성이 있습니다(이 packet으로는 확인 불가).
  - 추가 문자열 `delegation-1`이 disclosure 패턴에 걸릴 가능성은 낮다고 정적으로 봅니다.
- 최소 처분: "새 P에서 실행하지 않았고, 영향 분석으로 재사용한다"고 표기를 정확히 합니다.

**R1-F-N3. 역사 절이 현재 값처럼 읽힐 수 있습니다.**
- "Exact Artifact Closure Before R1"은 첫 A의 P `ef6e7d91…`과 611.68초를 superseded 표시 없이 제시합니다.
  - 뒤쪽 "Correction Admission" 절에서 역사 증거라고 밝히긴 합니다.
- "Correction Admission" 절에는 "artifact16을 진행한다"는 진행형 문장이 남아 있습니다.
- 최소 처분: 해당 절 머리에 "첫 A P의 역사 결과이며 현재 target은 v2"라는 한 줄을 넣습니다.

**R1-F-N4. Owner Decisions Remaining 목록에 항목이 빠져 있습니다.**
- 3개 항목 중에 M2 oracle 처분이 없습니다.
- M3의 label 선택 1/2는 "frozen-label 처리"라는 표현으로만 들어 있습니다.
- 각 절에 내용이 있으므로 비차단입니다.
- 최소 처분: 목록에서 두 절을 교차 참조합니다.

**R1-F-N5. preflight 거부 2건은 기계적 차단에 걸리지 않습니다.**
- 근거:
  - `run-native-r01.py`의 선행 실패 차단은 `r01/calls/*/result.json`만 확인합니다.
  - 두 거부는 `common.config` 단계, 즉 call 디렉터리를 만들기 전에 발생했습니다. 따라서 result.json이 애초에 없습니다.
- 정리:
  - 이 차단을 우회한 것은 아닙니다.
  - 두 건의 집계는 기록에 의존합니다: `failed-correction-admission.json`, `admission-failure-002.json`, `correction-comparison.failed_startups=2`.
  - 이 구분을 최종 보고에 유지하면 됩니다.

**R1-F-N6. reader 근거의 결속 대상을 명시해야 합니다.**
- reader 5개의 Read 경로는 첫 A release(`product-release-ef6e7d918…`) payload입니다.
- 활성화 기록에는 다음을 함께 적어야 합니다.
  - reader는 첫 A P의 bytes를 읽었습니다.
  - 그 bytes는 v2와 SECURITY를 제외하고 같습니다.
  - SECURITY는 Read되지 않았습니다.
- `final-candidate-v2.reader_and_token_reuse`가 이 내용을 일부 담고 있습니다.

**이월 (회귀 아님)**
- 첫 R1의 N1–N5는 계속 열려 있습니다.
  - adapter의 narrative 저장 경계
  - CLAUDE pointer 문구
  - adapter 머리말 label
  - GENERAL-WORK 링크
  - CAPABILITIES 날짜
- Driver 처분대로 다음 managed 문구 보정 때 다룹니다.
- 이번 delta에 adapter 변경을 섞지 않은 판단은 범위상 타당합니다.

---

## 증거 구분

**정적 판단 (이 리뷰)**
- 위 판정 전부
- diff·hash·크기 대조
- 세 계약의 CRLF 문장 대조
- launcher diff가 경로·identity 파일명만 바꿨다는 확인
- `campaign.json`이 root 1필드만 다르다는 확인
- `common.config`의 root 형식·hash 문자열 요구와 두 거부 원인의 대응

**새 P에 대한 Driver 실행 증거 (재현하지 않음)**
- safety 59, TERM/KILL 2
- acquire, canary, collect, smoke 7/7
- artifact 16/16

**재사용 증거 (새 P에서 fresh 실행이 아님)**
- focused normal 8 / parent-O 2
- reader 5: 언어 5/5, 엄격 기준 1/5
- token 3898
- GFM 323
- 첫 A의 artifact 16
- r11 656×2와 retained 17×2

**확인 불가·미실행**
- 현재 source에서의 complete suite (예상 oracle non-pass 1건 포함)
- 보정 bytes에 대한 GFM 재실행
- disclosure guard의 새 P 실행
- 설치 adopter에서 frozen label 아래 agent가 실제로 어떻게 동작하는지
- host 인증과 불변 payload 강제
- 실제 adopter 사용

## Owner 결정 경계

- 이 리뷰는 A 결과 수락, DR-0005·DR-0003·WORKFLOW amendment 활성화, label 선택, oracle 보정 선정, Git 작업, release, adopter 적용 중 어느 것도 부여하지 않습니다.
- reader의 엄격 기준 1/5 미달과 위 한계를 포함해 결과를 수락할지는 Owner가 결정합니다.
````

### Final Driver Disposition

| 항목 | 처분과 적용 범위 |
| --- | --- |
| R1-F-N1 | defend + clarify. `build-correction-review.py`는 current B를 읽는 `check-a-corrected-static.py`를 실제 실행했다. 기존 report에는 입력별 hash/실행시간이 없고 결과 수치가 같아서 같은 hash가 나온다. 같은 report hash만으로 미실행이라고 판단할 수는 없다. 혼동을 없애기 위해 최종 기록 포함 current22파일의 입력 hash를 결과에 결속하여 GFM·link/anchor·강조 검사를 새로 수행한다. 아래 최종 정적 결과가 현재 근거다. |
| R1-F-N2 | accept/clarify. generic disclosure guard는 SECURITY를 포함한 managed payload 전부를 읽는다(`tests/test_productization_safety.py:503–513`). filename literal만 찾는 `direct_consumers` 탐색은 이 generic 소비를 포착하지 못했다. 첫 처분의 “직접 관계 없음”은 이 테스트에는 부정확하다. first A의 normal8/O2를 새 P에서 실행하지 않았고 변경 영향 분석으로 재사용한다. 실제 고정 regex를 현재 SECURITY에 적용한 정적 검사에서 match0이며 추가 문자열은 식별 가능한 외부 프로젝트 정보를 넣지 않는다. 이것을 설치 init을 포함하는 원래 테스트의 새 실행 PASS라고 부르지 않는다. |
| R1-F-N3 | accept. 첫 A artifact 절과 correction 진행 체크포인트 머리에 역사 시점·현재 v2 target·종료된 결과 위치를 표시했다. 원래 수치와 역사 문장은 덮어쓰지 않았다. |
| R1-F-N4 | accept. Owner Decisions Remaining에서 label 선택1/2 및 예상 oracle non-pass/후속 선정 절을 직접 연결했다. 실제 선택·활성화는 없다. |
| R1-F-N5 | accept. preflight 거부2건은 call directory 생성 전 오류이므로 r01의 per-call result 실패 차단에는 들어가지 않는다. 실패 원본 설정·오류 기록과 집계로 추적한다. 자식 테스트0이며 기계적 차단을 우회한 것으로 주장하지 않는다. |
| R1-F-N6 | accept. reader5개가 실제로 읽은 installed release는 첫 A P `ef6e7d918e13dd78753c5e9ee2c0d06235024679c12257bcfebdfe85ab801ea6`다. 새 P와 managed bytes 차이는 SECURITY 한 문장뿐이고 어느 reader도 그 파일을 읽지 않았다. 따라서 읽은 bytes의 관찰을 재사용하며 새 release 경로의 reader 실행으로 표기하지 않는다. 실제 활성화 기록에도 이 결속과 strict Read1/5·언어5/5 관찰 한계를 그대로 싣는다. |

추가 수치 정정: Reviewer의 SECURITY Q8632→현재8687 비교는 누적 A 차이55 bytes다. 이번 한 문장 보정 자체는 첫 A8673→현재8687의14 bytes 증가다. 두 비교의 기준을 구분하며 Reviewer 원문은 수정하지 않는다.

이월된 첫 R1 비차단 N1–N5(서술 문서 저장 경계, project/managed CLAUDE 표현, 준비 label, 역사 링크, evidence 날짜)는 기존 처분대로 후속 관련 문구 변경의 후보다. 이번 source-only 기록 정리는 검토된 제품 bytes·활성화 선택지·권한·runtime·test를 바꾸지 않는다. 새 managed 검증이나 추가 정적 R1을 자동 반복할 사유는 없다.

### Current Result And Owner Boundary

A 완료 기준1–5에 대한 Driver 작업은 끝났고 exact 결과·활성화안을 Owner에게 제출한다. Work 상태는 Owner 결과 수락 전 Active로 유지한다. DR-0005는 Draft, Decision/Rationale/Consequences는 여전히 비어 있고 현행 technical contract는 DR-0004 entry-1이다. source procedure5개는 main `a93f71c359c4f0a9d57fcfb50d5999160e870f77`과 같으며 index의 추가 navigation2개만 구분한다. 최종 검토 중 원격 main도 같은 revision임을 재확인했다.

최종 managed P는 `49969df17f06e85cae8039c8dbd8cbf43a39f3ca8a317fceace4edd19596ad0b`다. 새 P의 safety59·TERM/KILL2·smoke7/7·artifact16/16은 실제 새 실행이고, normal8/O2·reader5·token3898은 첫 A에서 실행/측정한 근거의 영향 분석 재사용이다. r11의656×2는 별도 inherited anchor다. 현재 source의 complete suite, legacy oracle 실제 실패, frozen label 아래 실제 adopter 행동은 실행하지 않았다.

실제 A 결과 수락, activation, Git publication/release, adopter 적용은 수행하지 않았다. Owner가 선택할 사항은 위 Owner Decisions Remaining5개다. activation과 별개로 현재 실제 adopter 적용 권고는 보류한다.


### Final Preservation And Cleanup

최종 R1 종료 후 잠금 획득과 모든 알려진 review/native/reader process-group 부재를 확인했다. 별도 agent 작업도 없었다. 아래 정리는 기존 상시 승인 조건 안에서 수행했다.

- 보존: source worktree의 고유 미커밋 M1/M2+A, 기존 r11 anchor, 첫 A와 보정 P의 입력/실행 결과, reader 원문·fixture, review packet/identity/원문·핵심 metadata, preflight 거부 설정·manifest·오류 기록. 소비자는 Owner의 exact A 결과/활성화 결정과 그에 따른 제한된 evidence 재사용이며, 해당 결정 및 의존 검증이 끝나면 필요성을 다시 판단한다. source worktree의 결과 수락 조건도 아직 충족되지 않았다.
- 이번 삭제: 사용이 끝난 reserve2개 합계1GiB, 보존된 response와 일치하는 중복 review transport3개, 빈 stderr3개, 실패 시도의 중복 입력377개, 검증된 빈 디렉터리73개. 파일385개·1087521194 bytes다. 중복 입력은 보정 task의 기존 필수 사본과 파일별 실제 bytes·mode를 비교한 뒤 제거했다. 고유한 root 설정·실패 invocation·원본 manifest는 남겼다. 새 backup은 만들지 않았다.
- 앞선 단계 삭제와 합치면 소비 완료 reserve4개·총2GiB를 정리했다. 마지막 복구본·고유 결과·worktree는 삭제하지 않았다.
- 활성 경로 변경: 없음. source worktree와 필요한 첫 A/보정 실행 경로를 이동하거나 retarget하지 않았다. 실패 시도 중복 입력의 복구 대응은 기존 `cleanup-final.json`에 묶고, 원본 실패 경로를 실행 가능한 상태로 남겼다고 주장하지 않는다.

현재 보존 경로는 source `SOURCE_CHECKOUT`, 첫 A `PRIVATE_A_EVIDENCE`, 보정 `PRIVATE_A_CORRECTION_EVIDENCE`, 기존 M1/M2 anchor `PRIVATE_IMPLEMENTATION_EVIDENCE`다. 이 기록이 소비자·보존 종료조건을 소유하며 별도 backlog/보존 registry를 만들지 않는다.

### Final Static Evidence

현재 문서 바이트를 읽는 `check-a-closeout-static.py`로 GFM 렌더·local link/anchor·literal emphasis, protected104·managed29·CAPABILITIES 및 diff whitespace를 확인한다. `static-closeout.json`의 current_input_hashes가 이번 원문/처분/정리까지 포함한 입력22파일을 결속한다. 이 검사는 문서 구조 확인이며 제품 suite·reader·실제 adopter 실행이 아니다. 새 제품 바이트는 추가하지 않았다.


## Owner Result Acceptance — 2026-10-18

> A 결과는 수락해. 설치본 라벨을 활성화에 맞게 정리하는 작업과 링크 검사 oracle 보정을 묶어 후속 계획을 제안해. 기존 증거를 재사용하고, 실제 활성화·Git·adopter 적용은 아직 보류해.

Owner는 최종 R1까지 제출한 A 결과를 수락했다. 이 수락은 A의 문서 보정·검증·활성화 준비 결과에 한정하며 실제 계약 활성화·Git·adopter 적용을 승인하지 않는다. 앞선 “Owner 수락 대기” 표현은 각 당시 체크포인트이며 현재 상태는 이 수락 기록이다. 기존 M1/M2 결과 수락도 유지한다.

수락 대상은 P `49969df17f06e85cae8039c8dbd8cbf43a39f3ca8a317fceace4edd19596ad0b`, `final-candidate-v2.json`의 managed29/successor17, 최종 R1 `R1-a-correction-002`와 보고된 한계다. 수락 직전 결과 문서 SHA-256 `3df089903c82988b049293c3277b95d805326449e7c1aebe902f50b1d202a27a`의 정확한 bytes를 기존 A artifact directory의 `accepted-a-result-20261018.md`로 보존했다. Owner 수락 기록 전 현재 파일과 candidate/hash 일치를 다시 확인했다.

| A 완료 기준 | 수락된 결과 |
| --- | --- |
| 규칙 진입과 local 보존 | source 조건부 진입, 설치 view/manual/adapter 경로 및 합성 local-rule 보존 검증. 자율 CLI·일반 adopter 이해는 주장하지 않음 |
| reader 관찰과 제한 | 언어5/5 관찰, strict Read1/5 통과·4미달과 과도한 해석을 모두 남긴 제한된 준비 결과 |
| current 안내와 역사 의미 | scoped 문구 보정과 정확한 successor17 준비. runtime·권한·기록·복구 의미 불변 |
| 새 실행과 재사용 구분 | 최종 P artifact16/16 및 safety/smoke, focused/reader/token 재사용, r11 complete anchor와 새 GFM22/325를 구분 |
| R1 및 exact 제출안 | Blocker0·필수0, 비차단 처분, hash/조항/activation 선택지와 미실행 oracle 한계 제출 |

이로써 CHORE-20261018-001은 Done이다. DR-0005는 Draft이며 source 기술 계약은 아직 DR-0004 entry-1이다. 실제 adopter 적용 권고는 계속 보류한다. 이번 수락은 strict reader 결과를5/5로 고치거나 현재 source complete PASS를 새로 부여하지 않는다.

후속 [설치본 라벨·링크 oracle 통합 계획](delegation-activation-label-and-link-oracle-plan.md)의 proposal-1 SHA-256 `2238f2015ee47d9b70202aa9a04f1ca37cddf00e9e3b5c6e31794e54c748eec6`를 작성했다. 이는 새 실행·외부 검토 승인 전 계획이며 serial task ID는 아직 없다. 후속 제안의 소유자는 그 note다. 새 작업 결과를 이 완료된 A에 덧붙이지 않는다. index는 A 완료 링크와 새 후보의 탐색만 갱신했고, 변경 identity/diff는 후속 계획의 Navigation Record에 있다.

보존 목적을 재평가했다. 기존 worktree는 고유 미커밋 M1/M2+A와 구체적인 후속 재사용 대상이라 유지한다. r11/A/correction 입력·결과·reader 원문은 후속 계획의 누적 영향/R0/새 P 검증 소비자로 이어진다. R0에서 증거 재사용을 확정하거나 후속을 선정하지 않는 시점에 생성 fixture·중복물 필요를 다시 판단한다. 이미 제거한 reserve·중복 transport·사본은 복원하지 않는다. 이번 단계에서는 활성 경로 이동·retarget·파일 삭제가 없다.
