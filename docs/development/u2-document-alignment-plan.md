# 사용자 흐름과 U2 개발 문서 정렬 계획

상태: R0-01 REVISE, Driver 보정 반영. 문서 보강 방향은 Owner가 선택했다. 보정 계획의 실행 승인과 제품 문서 수정, R1 및 결과 수락은 아직 이루어지지 않았다. 이 문서는 WORKFLOW의 Preliminary Review Location에 따른 source-only 계획이며 정식 개발 작업 ID를 선점하지 않는다.

## 목적과 승인된 방향

처음 읽는 사람이 무엇을 요청하고, 에이전트가 어디까지 진행하며, 언제 사람이 판단하고, 중단 뒤 어떻게 이어가는지 이해하도록 기존 문서를 보강한다. 개발 문서는 완료된 U2 결과와 다음 판단을 바로 찾도록 연결한다.

Owner는 2026-10-27 대화에서 통합된 문서 보강 범위에 “진행하자.”라고 답했다. “진행하자.”는 작업 선택과 방향에 대한 승인으로 유지한다. WORKFLOW의 R0-before-execution-approval 순서에 따라, R0 처분이 반영된 정확한 계획 revision의 실행 승인은 Owner가 별도로 기록한다. 승인 후 날짜별 미사용 ID를 확인하여 CHORE 기록 하나를 만들고 이 노트에 dated pointer를 남긴다. 그 CHORE 기록만 이후 진행을 소유한다. 필수 R0/R1, 정확한 결과 수락과 Git/배포/도입처 실행의 별도 경계는 유지한다.

현재 계획의 기준은 source commit `17dc804a6af4e168d1bb73aa765e9354db4952ba`이다. source용 CONTRIBUTING → WORKFLOW, MAINTAINING, 현재 development index와 U2 완료 기록을 확인했다. 기존 checkout의 다른 작업은 보존한다.

## 사용자 문서에서 설명할 흐름

할 일 선택과 범위 확인 → 승인 범위에서 수행·검증·수정 → 결과와 계획 반영안 검토 → 결과 수락 및 기록 정렬 → 다음 일 선택 또는 나중에 재개.

한 작업 안의 반복과 다음 작업을 고르는 흐름을 구분한다. 아래 요청은 자연어 예시이며 필수 명령이나 무제한 실행 승인이 아니다.

| 요청 | 설명할 행동과 판단 |
| --- | --- |
| 현재 상태와 다음 할 일을 알려줘 | 현재 Work·계획·후속 선택을 읽고 추천한다. 추천만으로 선택이나 실행을 기록하지 않는다. |
| 이전 작업 이어가자 | 현재 기록·승인·pending 복구·입력을 확인한다. 유효한 같은 승인은 재사용하고 실제 미확정 사항만 묻는다. |
| 이 기능을 구현하고 테스트에서 발견한 문제까지 고쳐줘 | 범위·검증·한도·중단 조건이 정해지면 그 안에서 수정한다. 새 범위나 한도 변경은 해당 결정을 받는다. |
| 결과를 계획에 반영하고 다음 할 일을 제안해줘 | 수락 전 완료·잔여 반영안을 준비하고 수락 후 실제 상태와 남은 문서 조치를 설명한다. 제출 결과나 수락된 필수 입력을 임의 변경하지 않는다. |
| 지금 멈추고 나중에 이어가자 | 필요한 입력·결과와 재개 조건을 기존 기록에 남기고 다음 세션에서 다시 확인한다. 백그라운드 자동 재개를 약속하지 않는다. |

아래 개발 묶음 설명은 source 개발 안내를 위한 것이다. README, GETTING-STARTED, CONCEPTS, GENERAL-WORK와 adapter의 첫 사용 흐름에는 U 라벨을 넣지 않는다. 현재 있는 행동을 이름으로 설명하며 설치 전제와 혼동하지 않게 한다. U 라벨은 development 문서에 두고 docs/README에는 설치 안내와 source 개발용 검증의 차이만 짧게 설명한다. 설치 manual에서 배포되지 않은 development 파일로 링크하지 않는다.

U1/U2/U3는 개발 계획 묶음이다. 사용자 명령이나 모드로 만들지 않는다. U1은 계획·결과·후속 선택의 연결, U2는 승인한 작업 안의 수행·검증·보정과 재개, U3는 지원 환경의 설치·업데이트·복구·제거 경험을 지향한다. 이것이 모든 환경의 검증 완료를 뜻하지 않으며 기존 운영 기능을 없는 것으로 설명하지 않는다.

## 파일별 변경안과 읽기 순서

| 대상 | 읽기 문제와 제한된 보강 |
| --- | --- |
| README.md | 기존 첫 문단을 제품 목적 중심으로 고치고 Concepts의 흐름·예시로 짧게 연결한다. 지원 범위는 보존한다. 반복되는 전체 설명을 추가하지 않는다. |
| docs/README.md | 사용자 안내, 설치 profile, source 개발용 검증과 실제 실행 구성의 차이를 안내한다. 개발 완료를 제품 설치 완료로 설명하지 않는다. installed manual의 링크는 shipped 경로 안에서 해결한다. |
| docs/GETTING-STARTED.md | 설치 세부 절차 앞에 Concepts의 사용 흐름·요청 예시로 연결하는 짧은 진입 문장을 둔다. 사람의 판단은 기존 첫 Work 흐름에서 유지한다. 설치·첫 Work·복구 anchor를 보존한다. |
| docs/CONCEPTS.md | 전체 사용자 흐름과 다섯 요청 예시를 모으는 정본 위치다. 영문 예시를 쓰고 요청 언어가 필수 문법은 아님을 설명한다. 작업 안의 반복과 다음 작업 선택, 사람의 판단·재개를 연결하며 정확한 수락·권한 의미를 유지한다. |
| docs/GENERAL-WORK.md | 기존 Supervised Work Iteration을 사용자 흐름에서 찾게 한다. 반복 승인과 새 정확한 수락의 차이를 설명한다. |
| adapters/colvia-work/SKILL.md | 기존 Project Rules / Follow-Up / Handoff 지침 사이의 문서 영향·검토·종료 연결을 명확히 한다. 명령 실행 권한이나 자동 로딩을 추가하지 않는다. |
| docs/REFERENCE.md | 공통 행동과 프로젝트별 문서 위치·변경 유형 매핑의 책임을 기존 절차 안에서 연결한다. 별도 장부를 만들지 않는다. |
| docs/development/README.md | 상단에 U2 closeout의 수락·잔여/다음 판단 절 링크와 이번 CHORE 링크만 둔다. closed notice 외에 진행 요약을 복제하지 않는다. dated intake와 이전 관측은 그대로 둔다. |
| docs/development/FEAT-20261021-002-u2-single-host-source.md | 상단에 dated historical pointer를 추가하여 후속 기록을 안내한다. 실패·미완료·당시 소유권 원문은 보존한다. |
| docs/development/FEAT-20261022-001-prepared-tool-plan-live-qualification.md | 완료·수락 범위를 확인하고 새 문서 작업과의 연결이 필요한 경우 dated pointer만 추가한다. 과거 실행 기록은 수정하지 않는다. |
| docs/development/WORKFLOW.md | 기존 계획·검토·종료의 문서 영향 및 navigation 책임을 필요한 교차참조로 연결한다. 의무의 범위나 조건 변경이 필요하면 아래 amendment 경계를 따른다. |

OPERATIONS, SECURITY-AND-SUPPORT, root PRODUCT-CAPABILITIES.json, MAINTAINING, GUIDED-INTENT-FORMATION, MANUAL-OPERATION도 대조한다. 실제 모순이나 누락 연결에만 수정하고 이미 정확한 문구는 유지한다. PRODUCT-CAPABILITIES.json은 대조만 하며 수정하지 않는다. 산문이 아닌 파일의 변경이 필요하면 해당 작업을 멈추고 범위와 검증을 다시 제시한다. index 및 두 FEAT 기록의 navigation 변경은 기준 revision과 bounded diff를 정식 작업 기록에서 식별한다. 영문 제품 문서는 영문을 유지하며 전체 번역을 하지 않는다. 한국어 계획·결과 기록은 자연스러운 문장으로 작성한다. 기존 anchor는 보존하거나 영향받는 참조를 함께 고친다.

## 의미와 범위의 고정점

- `continuation-1` 설치 profile과 U2 source/adapter qualification은 구분한다. U2 통합에서 30개 managed path의 bytes는 바뀌지 않았다. 일반 업데이트만으로 U2 Host가 설치되거나 실행되지 않는다.
- 검증 후보, 결과 제출, 정확한 수락, Git 반영, 배포는 별개다. 후속 선택은 실행 권한이 아니다. 같은 행동·대상·입력·전제조건의 유효한 승인만 재사용한다.
- required reference, pending ticket, 제출 내용, 수락된 입력·결과, 정확한 복구 조건을 보존한다. Core가 문서를 자동 수정하는 기능을 추가하지 않는다.
- plan/continuation 정렬은 공통 행동이다. 문서 currentness 보고는 해당 프로젝트가 적용 규칙을 채택한 경우의 행동으로 설명하며 두 절차를 섞지 않는다. 이번 source 문서 정렬은 Owner가 명시적으로 선택한 작업 범위다.
- 공통 adapter는 공통 행동을 안내하고 프로젝트 규칙은 실제 문서 경로와 갱신 대상을 연결한다. Colvia source 개발 절차는 개발 인덱스·작업 기록의 종료 연결을 소유한다.
- 새 의무, 예외, 수락 조건 또는 기존 조건의 삭제는 단순 설명 수정으로 처리하지 않는다. 영향을 받는 조항과 named amendment를 준비하고 별도 Owner 판단 전에는 적용하지 않는다. 특히 adapter의 조건부 문서 영향 보고를 무조건적 새 규칙으로 바꾸지 않는다.
- U2 Core/Host/adapter 실행 구현, 플랫폼 지원 확장, 다른 진행 작업 조작, 도입처 payload 수정, commit/push/PR/merge/release는 제외한다. private 대상 식별정보는 source에 기록하지 않는다.
- 오래된 작업의 실패를 성공으로 바꾸거나 기존 intake를 현재 진행표로 덮어쓰지 않는다. 상세 진행 소유자는 하나이며 새 STATUS/registry를 만들지 않는다.

## 검증 선택과 한도

누적 변경은 설명·정보 순서·문서 연결과 의미를 유지한 agent 지침 보강이다. 실행 코드·schema·수락·복구 의미는 바꾸지 않는다. 새 문서 bytes는 release identity를 바꾸므로 현재 후보의 inventory와 consumer 경로를 새로 검사한다. 기존 U2 결과는 지원 주장 범위를 확인하는 역사적 근거로만 사용하고 이 후보의 새 PASS나 완전 회귀 anchor로 부르지 않는다.

정적 검사: 다섯 요청별 진입·행동·판단·중단/재개 경로, 문서와 adapter의 일치, 개발 상태와 후속 연결, 변경된 링크 및 inbound anchor, GFM 렌더링 후 코드 밖 literal `**` 잔여, public disclosure, `git diff --check`, 실행 파일·tests unchanged 여부를 확인한다. Reading Budget은 설계 제약으로 유지한다. 수정 전 지정 도구 `tiktoken==0.13.0`, `o200k_base`로 기준값을 측정하고 최종 AGENTS 및 AGENTS+README+Getting Started의 2,000/4,000 token 한도를 확인한다. 사전 확인에서 사용 가능한 현재 Python과 bundled Python에는 tiktoken이 없다. 별도 의존성을 설치하지 않는다. 측정이 불가능한 상태에서는 README·Getting Started에 전체 예시를 추가하지 않고 Concepts 링크 한 줄 수준으로 제한하며 budget 미확인으로 보고한다. 지정 도구를 확보해 측정한 값이 한도를 넘는 경우에도 예시·설명을 Concepts로 옮기고 링크를 남긴다. 다른 tokenizer의 숫자를 지정 도구의 통과로 대신하지 않는다.

아래 기존 `tests.test_productization_safety.ActualWorkspaceInitTests`의 일곱 test ID를 normal 모드로 선택한다. assertion이나 timeout을 수정하지 않는다.

1. `test_document_port_status_and_doctor_expose_verified_docs_read_only`
2. `test_document_port_agent_publication_resumes_original_request`
3. `test_document_port_managed_payload_generic_disclosure_guard`
4. `test_document_port_local_links_resolve`
5. `test_actual_update_rollback_round_trip_preserves_truth_and_runs_both_launchers`
6. `test_repair_exact_active_preserves_completed_truth_and_originals`
7. `test_detach_port_plain_audit_and_document_preservation`

이 검사는 이 후보의 설치 문서 접근, read-only 조회, 원래 요청으로 재개, 정확한 inventory, update/rollback, repair, detach 소비를 다룬다. 선택·수집·실행 ID와 skip/error/failure를 기록하며 7개 focused run으로만 보고한다. 새 전체 회귀 결과를 주장하지 않는다.

추가로 제안했던 이전 실제 release → 최종 문서 후보의 custom round trip은 수행하지 않는다. 기존 round-trip test는 이 후보를 설치하고 launcher 주석만 다른 synthetic 변형으로 update/rollback한다. 따라서 현재 문서의 포장·소비 경로는 검사하지만 특정 이전 실제 release에서 문서 bytes가 바뀌는 전환을 확인하지는 않는다. 이는 실제 도입처 update 준비에서 채워야 할 미검증 범위이며 이번 문서 결과를 배포 적격성으로 보고하지 않는다.

실행 명세는 다음과 같이 고정했다. `SOURCE`는 위 base에서 승인된 문서 변경만 더한 전용 checkout, `TASK_ROOT`는 이 작업의 전용 durable artifact directory다. 정확한 로컬 경로는 private 실행 묶음에 있으며 source 문서에는 식별정보를 넣지 않는다. 전체 runnable controls는 Owner에게 실행 승인 대상으로 제공한다.

- 명령: `python3 "$TASK_ROOT/validation-controls/run-focused.py"`. 이 controller는 `/usr/bin/sandbox-exec -f "$TASK_ROOT/validation-controls/focused.sb" CPYTHON_3_14_7 -I -S -B "$TASK_ROOT/validation-controls/focused.py"` 한 번만 실행한다.
- test runtime: final GIL-enabled CPython 3.14.7, 실행 파일 SHA-256 `868ca5e6a127883eff41edb3b46878e982c2e8fff6e5dd150cafff24b9aaffc5`. 시스템 기본 3.14.8은 사용하지 않는다. normal 모드다.
- 작업 디렉터리: `SOURCE`. fixture와 per-process temporary directory: `TASK_ROOT/validation-work/`, `TASK_ROOT/validation-work/temp/`. log와 summary도 같은 write boundary에 둔다. source와 controls는 읽기 전용이다.
- 격리: Seatbelt deny-default, network allow 없음, runtime·시스템 라이브러리·source·controls·fixture만 읽기 허용, fixture와 `/dev/null`만 쓰기 허용. child 환경은 PATH/LANG/bytecode/TMPDIR/Git 제한값만 전달하며 자격증명 변수·사용자 Git 설정을 전달하지 않는다. HOME은 재지정하지 않는다.
- 실행 전 합성 read/write/network canary, 일곱 ID의 정확한 수집을 확인한다. 실행 후 runtime/source drift를 대조한다. child bytecode 금지와 기존 45초 subprocess timeout을 유지한다.
- 1회·누적 15분. 경계 검사 실패, 실제 검사 실패, 입력 drift, timeout은 affected lane을 중단하며 자동 재시도·의존성 추가·timeout/권한 확대를 하지 않는다. 준비된 Python controls는 compile 검사만 했으며 sandbox 및 tests는 아직 실행하지 않았다.


agent 진입·재개 행동은 최종 지침에 대해 다섯 요청 및 stale reference/pending ticket/new acceptance 상황을 정적으로 대조한다. 이는 실제 native agent 실행이나 사용자 이해도 관측이 아니다. 설명 변경이 새로운 agent 행동·수락·복구 의미를 요구하거나 이 검사로 상호작용 위험을 한정할 수 없으면 affected action을 멈추고 필요한 추가 검증과 범위를 제시한다. 현재는 새 전체 제품 회귀나 별도 사용자 연구를 계획하지 않는다.

계획상 예상은 문서 수정·선택 검사·R0/R1 대응 60–90분, Reviewer 응답 대기 10–30분이다. 이번 범위의 사전 판단이며 측정 보장은 아니다. 제안 누적 중단 한도는 Reviewer 대기를 포함해 실행 착수 후 120분이고, Owner 응답 대기는 제외하며 겹치는 시간은 한 번만 센다. 실행 계획 확정 시 실제 확인된 준비량을 반영한다. 한도 도달·범위 확대·규칙 의미 변경은 남은 일과 다음 비용을 보고한다.

## R0 요청과 결과 처리

Reviewer는 계획이 승인 범위와 기존 계약을 보존하는지, 다섯 요청과 U2 설치/검증 구분을 충분히 다루는지, 문서 currentness 연결이 새 규칙으로 바뀌지 않는지, 좁힌 검증이 변경 위험을 다루는지 검토한다. 실질적인 blocker부터 파일/조항·이유·최소 수정 방향을 제시한다. 테스트 실행이나 파일 쓰기는 허용하지 않는다.

별도 허가가 있다면 fresh Claude CLI에 고정 packet만 전달한다. 각 round는 tools0, 기존 구독 인증 경로 확인, source 및 계획 identity 전후 대조를 따른다. 승인 요청 범위는 R0 1회, R1 1회와 범위 안 보정 재검토 최대 2회, round당 최대 15분·전체 최대 45분이다. 자동 재시도·다른 인증/모델/도구 경로로 fallback하지 않는다. CLI 전송 승인이 없으면 packet 준비까지만 진행한다.

R0-01 원문과 Driver disposition은 아래에 기록했다. 보정 계획의 Owner 실행 승인 후 정식 CHORE 기록을 만들고 이후 실행·R1·Owner 결과 수락은 그 기록 하나에 남긴다. 이 노트는 dated pointer와 함께 계획/R0 이력으로 보존한다. Reviewer의 승인 의견은 Owner 결정이 아니다.

## 완료 결과와 후속 경계

수정 파일·사용자 흐름, 기준 source/installed 범위, 실행 검사·정적 대조·미관측 한계, 개발 문서 정렬과 잔여를 보고한다. U2 실제 적용에는 별도 Host 배포물, 프로젝트 연결, 관측·검증·복구 계획이 필요하다는 공백을 설명한다. 구체적인 도입 대상과 설치 관측은 private 작업 기록에서만 다룬다. 이후 실제 적용은 정확한 대상·후보·범위 승인으로 진행한다.

최종 결과 수락 전까지 소스 변경과 필요한 리뷰 응답을 보존한다. 재생성 가능한 렌더·synthetic fixture는 실제 소비가 끝나고 필요한 결과가 기존 기록에 남으면 standing cleanup 조건에 따라 정리한다. 계획·결과·미해결 실패와 마지막 recovery copy는 유지한다.

## CLI 검토 전송 승인 — 2026-10-27

Owner는 이번 문서 작업의 R0·R1 각 1회와 범위 내 보정 재검토 최대 2회, 회당 15분·총 45분, 기존 Claude 구독 인증과 tools0, 도입처 자료 제외 조건에 “Claude CLI 검토 승인”이라고 답했다. 이는 해당 자료 전송·응답 수집의 승인이고 계획 실행·결과 수락·Git 작업을 대신하지 않는다.

## R0-01 입력과 실제 실행

R0는 제품 파일 수정 전 고정 packet을 정적으로 검토했다. source base는 위와 같으며 plan과 source 발췌가 packet에 포함됐다. 당시 tracked diff는 비어 있었고 untracked plan은 `3e5c9e3459156b0acaa9228caeeecdef0636a82fea115696341da1017058f96d`로 식별된다. packet SHA-256은 `8c4d2906ffb25701a2711d428ca39b18f816256cd4721a51803f072d3652c352`이다. 리뷰 중 source/plan drift는 없었다.

실제 Reviewer: Claude Opus 5.5 (`claude-opus-5-5`), CLI 2.1.310, fresh session `62bf1de8-d7b1-401e-8cfc-fb113cfc8936`. tools 0, MCP 0, claude.ai/firstParty/pro 인증을 확인했다. 발췌를 받은 정적 검토이므로 전체 source나 실제 agent 행동의 독립 실행 검토는 아니다. 실제 소요 104.821초, exit 0, timeout 없음. Reviewer 누적 45분 중 104.821초를 사용했으며 남은 한도는 약 43분 15초다.

### Reviewer 최종 응답 원문

# R0 검토 결과: `docs/development/u2-document-alignment-plan.md`

**Verdict: REVISE.** BLOCKED 사유는 없습니다. 승인 경계, 제외 범위, 공개 범위, 기존 기록 보존, 그리고 정적 대조와 실행 검증의 구분은 전반적으로 잘 지켜졌습니다. 다만 아래 Medium 항목은 실행 승인 전에 계획에 반영해야 합니다.

검토 조건: Reviewer는 Claude (`claude-opus-5-5`)이며, 도구를 쓰지 않고 제공된 발췌만 정적으로 읽었습니다. 테스트 ID가 실제로 있는지, token 수, 30개 managed path의 bytes가 그대로인지는 확인하지 못했습니다. 이 의견은 Owner 결정이 아닙니다.

---

## Medium

### M1. 실행 승인 시점과 정식 기록 생성이 불명확함
- **위치:** 머리 상태 문단, `목적과 승인된 방향` 둘째 문단, `R0 요청과 결과 처리` 마지막 문단
- **문제:** "방향과 범위 승인은 유지한다"와 "R0 결과가 범위를 바꿀 때는 변경점을 제시한다"를 함께 읽으면, 범위가 그대로일 때는 2026-10-27의 "진행하자."가 곧 실행 승인인 것처럼 읽힙니다. WORKFLOW `Review And Evidence`에 따르면 R0는 실행 승인 *전에* 하는 검토입니다. 또 `Start And Select`와 `Preliminary Review Location`은 계획 승인 후 정식 기록을 하나 만들고, 이 노트에는 링크 또는 dated historical pointer를 남기도록 요구합니다. 그런데 이 계획은 "이 위치 또는 이어지는 정식 작업 기록"이라고만 적어 진행 기록의 소유자가 정해지지 않습니다.
- **최소 보정:** 다음 내용을 한두 문장으로 명시하세요.
  - "진행하자."는 선택과 방향에 대한 승인이다.
  - 실행 승인은 R0 처분이 반영된 정확한 계획 revision에 대해 Owner가 별도로 기록한다.
  - 승인 후 `CHORE-YYYYMMDD-NNN` 기록을 하나 만들고, 이 노트에는 dated pointer를 남겨 이후 진행 소유자를 그 기록 하나로 정한다.

### M2. Development Index 수정이 navigation 범위를 넘을 수 있음
- **위치:** `파일별 변경안과 읽기 순서`의 `docs/development/README.md` 행
- **문제:** WORKFLOW `Candidate And Navigation Changes`는 index의 navigation을 task/closeout 링크와 selected·closed·dropped notice로 한정합니다. index는 진행 상황을 복제하지 않아야 합니다. 그런데 "현재 U2 완료 결과와 다음 판단의 연결"이 요약 문장으로 쓰이면 진행 상황 미러링에 해당합니다. 같은 절은 변경된 revision과 bounded diff를 승인 기록에 남기라고도 요구하는데, 계획에는 이 내용이 없습니다. 이전 FEAT 기록에 추가할 pointer도 마찬가지입니다.
- **최소 보정:** index 추가분은 U2 closeout(수락 기록)과 그 잔여·다음 판단 절로 가는 링크, 그리고 이번 task 링크로 한정하세요. index와 두 FEAT 기록의 결과 revision과 bounded diff는 정식 작업 기록에 남긴다고 적으세요.

### M3. 사용자 문서에서 U1/U2/U3 표기가 지원 경계를 흐릴 수 있음
- **위치:** `사용자 문서에서 설명할 흐름`의 마지막 문단, `의미와 범위의 고정점` 첫 항목
- **문제:** 이 문단이 "사용자 문서에서 설명할 흐름" 절에 들어 있어서, README와 GETTING-STARTED에 U 라벨이 노출될 수 있습니다. 문제는 세 가지입니다.
  - 기존 Supervised Work Iteration(host 감독 지침)을 "U2"라고 부르면, 독자는 이 기능이 U2 Host를 설치해야 쓸 수 있다고 오해하기 쉽습니다. 계획 스스로 "일반 업데이트만으로 U2 Host가 설치되지 않는다"고 적고 있습니다.
  - U3의 "지향" 설명은 shipped 문서 안에서 로드맵 약속처럼 읽힙니다.
  - 처음 읽는 사람에게 내부 개발 라벨은 읽는 흐름을 방해합니다.
- **최소 보정:** shipped 사용자 문서(README, GETTING-STARTED, CONCEPTS, GENERAL-WORK, adapter)에서는 U 라벨을 쓰지 말고, 지금 있는 행동만 설명하세요. U 라벨과 "source qualification ≠ 설치"라는 구분은 `docs/README.md`의 개발 문서 안내와 `docs/development/` 안에만 둔다고 명시하세요.

### M4. Reading Budget을 사후 측정이 아니라 설계 제약으로 다뤄야 함
- **위치:** `검증 선택과 한도`의 정적 검사 문단, README·GETTING-STARTED 행
- **문제:** 이 계획은 필수로 읽는 두 문서에 흐름 설명과 요청 예시 다섯 개를 *추가*합니다. GETTING-STARTED는 지금도 길어서 MAINTAINING `Reading Budget And Claims`의 4,000 token 한도에 대한 여유가 확인되지 않은 상태입니다. "도구가 없으면 한계를 보고한다"는 측정 방법만 정할 뿐, 한도를 넘었을 때 무엇을 할지는 정하지 않습니다.
- **최소 보정:** 다음을 계획에 추가하세요.
  - 수정 전에 기준 token 수를 먼저 측정한다.
  - 한도를 넘으면 예시를 CONCEPTS나 GENERAL-WORK로 옮기고 링크로 대체한다.
  - 측정할 수 없으면 필수 문서 두 개에 넣는 추가분을 링크 한 줄 수준으로 줄이고, budget이 미확인임을 보고한다.

### M5. synthetic round trip runner가 승인 대상에 고정되지 않음
- **위치:** `검증 선택과 한도`, "same-window 이전 source → 최종 문서 후보 … 최종 runner에 … 고정한 뒤 실행한다"
- **문제:** 명령, 입력, runtime, 출력 위치를 실행 승인 *뒤에* 정하면, Owner가 보지 않은 명령이 추가되는 셈입니다. 이는 WORKFLOW `Execute Within The Approved Boundary`("silently add new commands" 금지)와 `Agent Collaboration`(실행 시 명령·runtime·경계를 고정하라는 요구)에 어긋납니다. 또 일곱 개 테스트 중 `test_actual_update_rollback_round_trip…`과 겹치는 부분이 무엇이고 남는 위험이 무엇인지 설명되어 있지 않습니다.
- **최소 보정:** 실행 승인을 받을 계획 revision에 runner 명세를 넣으세요. 명세에는 명령, CPython 정확한 patch, 작업 디렉터리, fixture 위치, 네트워크와 자격증명 차단 방법, 시간 한도가 들어가야 합니다. 그리고 일곱 개 테스트가 덮지 못하는 지점을 한 문장으로 적으세요. 명세를 미리 고정할 수 없다면 이 검사를 빼고 미검증 한계로 보고하세요.

---

## Low

### L1. plan 정렬과 문서 currentness를 구분해야 함
- **위치:** `사용자 문서에서 설명할 흐름` 표의 넷째 요청 행, `의미와 범위의 고정점` 넷째 항목
- **문제:** adapter `Follow-Up And Plan Alignment`의 plan 완료·잔여 반영안은 공통 행동입니다. 반면 문서 영향 보고는 "Where the applicable project rules require"라는 조건이 붙어 있고, REFERENCE의 currentness 예시는 프로젝트가 선택해서 채택하는 규칙입니다. 사용자 문서에서 이 둘을 섞으면 선택 규칙이 기본 동작처럼 읽힙니다.
- **최소 보정:** 고정점에 한 문장을 추가하세요. "사용자 문서에서 문서 currentness 보고는 프로젝트가 규칙을 채택한 경우에만 수행된다고 설명하고, plan/continuation 정렬과 구분한다."

### L2. 요청 예시의 언어와 정본 위치가 정해지지 않음
- **위치:** `파일별 변경안과 읽기 순서`의 마지막 문단, GETTING-STARTED·CONCEPTS·GENERAL-WORK 행
- **문제:** 영문 문서에 들어갈 다섯 요청 예시를 어떤 언어로 쓸지 정해져 있지 않습니다. adapter는 "Korean example"이라고 표기하는 관례를 씁니다. 또 같은 흐름이 여러 문서에 반복될 위험이 있습니다.
- **최소 보정:** 예시 언어를 정하세요(영문으로 쓰거나, adapter처럼 표기한 한국어 예). 흐름 설명은 문서 하나를 정본으로 두고 나머지 문서는 링크하도록 명시하세요.

### L3. 비산문 파일 수정 시 중단 조건이 필요함
- **위치:** `파일별 변경안과 읽기 순서`의 "root PRODUCT-CAPABILITIES.json … 대조"
- **문제:** 이 파일은 JSON이라 기계가 읽는 주장일 수 있습니다. 수정하면 "산문만 변경"이라는 위험 분류가 무너집니다.
- **최소 보정:** "산문이 아닌 파일의 수정이 필요해지면 해당 작업을 멈추고 범위와 검증을 다시 제시한다"를 추가하세요.

### L4. 선택한 테스트의 수집 여부를 확인해야 함
- **위치:** `검증 선택과 한도`의 테스트 목록
- **최소 보정:** 일곱 개 ID가 실제로 수집·실행되었는지 결과에 기록하고, 이것이 focused run이지 complete run이 아님을 명시한다고 적으세요. MAINTAINING `Evidence Reuse And Selection`에 따른 것입니다.

---

## 확인된 적정 사항

- CLI 전송 승인은 R0와 R1 각 1회, 재검토 최대 2회, 15분/45분 한도, tools0, 도입처 자료 제외로 범위가 한정되어 있습니다. 실행·수락·Git 승인과도 분리되어 있습니다.
- 새 의무를 만들 때 named amendment와 Owner 판단을 거치는 경계를 두었고, adapter의 조건부 보고를 무조건 규칙으로 바꾸는 것을 명시적으로 금지했습니다.
- 바뀐 shipped bytes에 대해 inventory, update/rollback, repair, detach 소비를 검사하도록 선택했습니다. 전체 matrix를 요구하지 않은 것은 MAINTAINING에 맞습니다. agent 행동에 대한 정적 대조를 실제 실행으로 부르지 않은 점도 적절합니다.
- 계획 본문에 private 식별정보가 없습니다.

M1–M5를 처분해 반영하면, 수정된 계획 revision에 대해 Owner 실행 승인을 진행할 수 있다고 봅니다. 처분과 편집은 Driver가, 실행 승인은 Owner가 결정합니다.

### Driver disposition

| 항목 | 처분 | 반영 및 남은 경계 |
| --- | --- | --- |
| M1 | accept | 선택·방향 승인과 R0 이후 정확한 계획 실행 승인을 구분했다. 승인 뒤 하나의 CHORE 기록으로 진행 소유권을 넘긴다. |
| M2 | accept | index를 closeout/잔여 절과 이번 task의 링크·closed notice에 한정했다. index/이전 기록 navigation diff는 정식 작업 기록에서 식별한다. |
| M3 | revise | 첫 사용 문서와 adapter에는 U 라벨을 넣지 않는다. 개발 묶음은 development에 두며 shipped docs/README에는 설치와 source 검증의 차이만 설명한다. 배포되지 않은 development 파일로 링크하지 않는다. |
| M4 | accept | Concepts를 흐름·예시의 정본으로 정했다. tiktoken 미설치 상태에서 첫 진입 두 문서는 짧은 링크만 추가하고 budget 미확인으로 보고한다. 무단 의존성 설치는 하지 않는다. |
| M5 | accept | 추가 custom round trip을 빼고 그 미검증 범위를 명시했다. 기존 7개 검사만 정확한 runtime·명령·경계·한도로 고정한 controls를 준비했다. |
| L1 | accept | 공통 plan/continuation 정렬과 프로젝트가 채택한 문서 currentness 규칙을 구분했다. |
| L2 | accept | Concepts의 영문 요청 예시를 정본으로 하고 다른 문서는 짧게 연결한다. |
| L3 | accept | PRODUCT-CAPABILITIES.json은 대조만 한다. 비산문 변경은 재계획 대상으로 명시했다. |
| L4 | accept | 일곱 ID의 선택·수집·실행 및 skip/failure를 기록한다. AST로 일곱 메서드 존재만 확인했으며 아직 실행하지 않았다. |

이 보정은 Driver 처분이며 Reviewer 재검토 PASS가 아니다. R0-01의 REVISE 원문을 보존한다. 실행 승인 전 아래 controls와 보정 계획을 Owner에게 제공한다.

### 준비된 검사 controls identity

| File | SHA-256 |
| --- | --- |
| `focused.py` | `123a049c4d0a260158946305a332d0076099d72927334e5801b8a43c404d493a` |
| `focused.sb` | `1be252b3ab9272b916609b68c700f6087ebaa4fe2f8df8df0de5636b0c1da51b` |
| `input.json` | `0d925b526be3df03f3805f810c0771bb9036040e28e38000aa97662b5fc562a7` |
| `run-focused.py` | `60074c346c76086d29301fadd53609be20ac97e84b333eb47d65e4aa47b48737` |

검사 controls는 이 작업의 private 실행 묶음에만 있으며 제품 배포물이나 새 영구 validation registry가 아니다. 필요한 검사와 결과 수락이 끝나면 실제 소비·보존 조건을 재평가한다.

## 실행 승인과 진행 소유권 — 2026-10-27

Owner는 보정 계획 `97b6624914da11ddf44bdc0d60c8ae684550e61f92dddd51e55cbe0525798a9b`의 실행을 승인했다. 위 원래 bytes `[0, 31416)`는 승인 시점 그대로다. 이후 실행·R1·결과·잔여는 [CHORE-20261027-002](CHORE-20261027-002-user-flow-and-development-doc-alignment.md) 하나가 소유한다. 이 노트는 계획과 R0 이력으로 보존한다.
