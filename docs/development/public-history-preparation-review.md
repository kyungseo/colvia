# Public History Preparation Review

Date: 2026-10-27
State: R0 REVISE preserved; Owner selected the Driver-corrected implementation on 2026-10-27; progress belongs to the linked Work.

## Owner Scope And Authorization

Owner는 7파일 공개 이력 정리의 R0를 승인하고 원본·기존 검증 증거 보존, 구현·테스트·재빌드·live 실행·commit·push 금지를 명시했다. 첫 호출 시도는 자동 승인 검토가 구체적 외부 전송 승인을 요구하여 reviewer 시작 전에 차단했다. 이후 Owner가 동일한 비식별 packet을 Claude.ai 구독 계정으로 전송해 도구 없는 정적 R0를 1회 수행하도록 명시적으로 승인했다. 해당 1회가 완료됐다. 이 승인에 구현이나 재리뷰는 포함되지 않는다.

## Review Request And Identity

목적은 7파일 정리 계획의 공개 안전성, 실행 대상 binding·승인·부모 증거의 의미, 검증 범위와 보존 계획을 검토하는 것이다. 제공 입력은 계획, 관련 workflow, 7파일의 제한된 source/document 발췌다. private 대상명·경로·branch·Owner message ID를 치환하고 64자리 digest는 equality 관계를 보존하는 대체값으로 바꿨다. full journal·full source는 제공하지 않았다. 따라서 전체 구현 감사나 실행 증거를 대신하지 않는다.

Codex Driver / Claude Reviewer / human Owner. 신규 CLI 세션과 별도 모델을 사용했으며 제한된 packet에 의존한다. 인증은 claude.ai / firstParty 구독 경로로 확인했고 도구·MCP·slash command·hooks를 비활성화했다. 허용은 정적 읽기 1회, timeout 600초였으며 임의 명령·테스트·소스 수정 권한은 없었다.

- Actual model: `claude-opus-5-5`
- Session: `2552ab94-14b2-4837-811e-4e6eb943a8af`
- Exact transmitted packet SHA-256: `361b58a08feb1e4c932bf7d76b55335cbc905587c8cccb6db0366505138e7cb6`
- Verbatim response SHA-256 (UTF-8 result text): `b2f1d572e0e443d1773a3dc4eae778af60e5086b1b7b64256bb05e7ce83d092c`
- CLI: 2.1.310; exit 0; elapsed 176.75 seconds; model turns 1; tool calls 0; MCP servers 0.

exact source base/diff identity와 diff 밖 untracked 입력의 SHA는 private input manifest에 보존했다. 리뷰 전후 기존 source 92파일, 원본 복구본 7파일, packet·원 계획의 bytes와 HEAD·staged 상태를 확인했고 drift가 없었다. 이 review note만 작성·갱신했으며 구현 7파일은 변경하지 않았다. 기존 실패·qualification·Owner 수락 증거를 수정하거나 삭제하지 않았다.

## Retention

7개 원본은 후속 승인된 정리의 복구 소비자가 사용한다. packet·원 계획·review 결과는 Owner 계획 결정과 R1 비교를 위해 유지한다. 원본 증거는 기존 보존 위치에 남는다. raw review event 출력은 현재 Owner의 R0 처분 확인이 끝나고 이 기록의 원문·metadata가 충분함을 확인할 때 재평가한다. private 경로나 원래 외부 대상 식별자는 공개 기록에 넣지 않는다.

## Driver Disposition

| Finding | Disposition | Plan correction / basis |
| --- | --- | --- |
| F1 High | accept | Rust 테스트 추가·컴파일을 제외하고 JSON literal 정적 비교만 제안한다. Rust compile/test 미실행을 명시한다. |
| F2 High | accept | 공개 노출·해시 참조 검색을 구현 승인 전으로 옮겼다. 제한된 읽기 확인에서 결과물 추가 수정 근거는 없었다. 7개 결과물과 R0/Work/인덱스 추적 표면 수를 별도 공개한다. |
| F3 High | revise | admission 대상이 바뀌는 점을 인정한다. 만료 deadline과 wall/continuous clock guard를 읽어 보완했으나 실행 불가를 무조건 보장하지 않는다. 승인 부재는 정책 경계이며 기술적 차단 증거와 구분한다. |
| F4 Medium-High | accept | 데이터 계약 3개를 고정한다. 실제 guard에 도달하는 기존 fixture를 확인하지 못했으므로 mismatch 실행 검증을 약속하지 않는다. guard 추출·새 fixture 확대를 하지 않는다. |
| F5 Medium | accept | 공개 파생물·중립화 인용 표지·원본 SHA 의미·표시용 branch/path 매핑을 명시한다. 원본 원문·승인 의미는 보존한다. |
| F6 Medium | revise | packet이 보지 못한 이 preliminary 리뷰 기록은 R0 시작 전에 이미 작성돼 있었다. source workflow의 verbatim 요구를 따라 공개 안전성을 확인한 응답 원문을 아래에 둔다. exact private source mapping은 비공개 증거에 유지한다. 공개 기록에는 실제 packet digest를 남기며 이를 원본 source digest로 오인하게 하지 않는다. |
| O1 / O5 | accept | synthetic 접두를 사용하고 양언어 JSON key 집합·parsing 검증을 계획에 포함한다. |
| O2 | accept | hash 기반 식별자 guard 대체를 하지 않는다. |
| O3 / O4 | accept | 무관한 README 갱신은 제외하고 공개 provenance 분류 기준을 명시한다. |

이 처분은 Driver의 계획 보정이다. Reviewer의 REVISE를 승인으로 변경하지 않았으며 Owner의 구현 수락도 기록하지 않았다.

## Revised Plan — Driver Proposal, Not Re-reviewed

원래 R0 판정은 REVISE다. 다음은 Driver 보정 제안이며 Reviewer의 approve나 Owner의 구현 승인으로 바꾸지 않는다. 이번에 허용된 reviewer 호출 1회는 소진했다. 재리뷰를 실행하지 않았다.

### Scope And File Count

구현 결과물은 기존 7파일을 유지한다: qualification 문서 3개, `docs/development/verification/u2-host/adapters/codex.py`, `tests/test_u2_host.py`, host `README.md`, `codex-rs/app-server/src/lib.rs`.

현재 새로 작성한 source 파일은 이 preliminary R0 기록 1개뿐이다. 이 파일은 위 7개 구현 결과물과 별도다. 후속 구현을 선택하면 workflow상 새 development Work 1개와 Development Index 연결 1개가 필요하다. 따라서 승인 범위는 7개 결과물 + 이미 존재하는 R0 기록의 후속 갱신 + Work/인덱스 2개로 구분해야 한다. 완료된 qualification Work를 다시 실행 상태로 바꾸지 않는다. 추적 파일을 지금 추가하지 않았다.

### Exact Proposed Changes

1. v42–v56의 `replacement_work`는 `synthetic-reference-a` / `synthetic-operations-guide-check`, v57은 `synthetic-reference-a-regression` / `synthetic-operations-guide-regression`으로 고정한다. Python과 Rust의 대응 값 16쌍만 변경한다. v41의 기존 합성 값, 다른 allocation 필드, guard·deadline·승인·부모 digest는 그대로 둔다. 값 주입 설정, helper 추출, guard 변경, hash 기반 대상 비교는 제외한다.
2. Rust에는 새 테스트 코드를 추가하지 않는다. compile·cargo test·debug/release rebuild를 모두 제외한다. 구현 후 승인된 검증에서는 파일을 읽어 Python JSON 및 Rust raw-string JSON을 파싱하고 버전·key·값의 대응을 비교한다. raw-string 구분자와 JSON 문법도 읽기 기반으로 확인한다. 이를 Rust compile/test PASS로 표기하지 않는다.
3. Python 집중 테스트는 `test_public_history_replacement_mapping`, `test_public_history_replacement_versions`, `test_public_history_v41_preserved`의 데이터 계약 3개로 고정하는 안을 제안한다. 범위는 16개 변경 쌍의 정확한 값, replacement가 있는 버전 집합 41–57, v41 기존 합성 쌍 보존이다. 실제 source module의 allocation을 읽고, guard의 비교식을 테스트 안에서 재구현하지 않는다. 현재 검토한 fixture에서는 해당 실제 launch guard에 도달하는 준비된 mismatch fixture를 확인하지 못했으므로 이번 계획에서 동적 거부 검증을 약속하지 않는다. guard 미변경은 원본 diff로만 확인하고, 기존 거부 검증은 원래 후보의 증거로만 재사용한다. 이 테스트들은 아직 작성·실행하지 않았다.
4. 변경 전후 private 비교는 16쌍의 값 외 모든 필드가 같은지, 다른 버전의 allocation과 guard가 같은지 확인한다. 원본은 7파일 보존본과 바이트 비교한다. private 검사 입력에 실제 식별자가 있어도 공개 테스트·로그에는 복사하지 않는다. 정적 구조 비교와 동적 테스트 결과를 구분한다.
5. 문서 3개와 README는 원본과 공개 파생물의 관계를 명시한다. 실제 대상명은 `Reference A`, branch는 `reference-a-guide-branch`, 문서 path는 `docs/briefs/reference-a-operations-guide.md` 같은 표시용 label로 일관되게 치환한다. 표시용 path는 실제 존재하는 링크로 만들지 않는다. 실행용 합성 ID와 표시용 label의 대응을 문서에 설명한다. 비식별화한 인용은 `[공개용 중립화]` 표지를 남기며 원문 그대로라고 주장하지 않는다. 기존 SHA는 원본 bytes 기준이라는 의미를 유지하고, 공개 사본의 새 SHA나 새 Owner 승인으로 바꾸지 않는다. 실제 외부 revision은 중립 표기로 제거한다.
6. v42–v57의 새 ID는 기존 승인 묶음에서 코드상 비교 대상이 달라지는 변경이다. 기존 승인은 새 합성 대상을 승인하지 않는다. 원래 실제 대상의 재실행 재현성은 공개 후보에서 의도적으로 보존되지 않으며 원본으로만 복구할 수 있다. 고정 deadline과 정상 wall/continuous clock에 따른 실행 예산 거부는 아래 정적 근거로 설명하되, 실제 실행 차단을 재현했다거나 합성 변경이 모든 환경에서 무해하다고 주장하지 않는다. 이 주장보다 강한 기술적 보장이 필요하면 현 7파일·guard 불변 범위의 보정으로 포장하지 않고 별도 설계·승인을 요청한다.

### Read-only Scope Check Before Implementation Approval

Driver는 R0 이후 기존 후보 Colvia 33파일과 runtime 59파일의 현재 bytes를 확인하고, 알려진 실제 외부 대상·Owner·경로·branch·revision 패턴과 7원본의 현재 SHA/path 참조를 검색했다. 실제 식별자 hit는 기존 3문서와 Python/Rust 두 소스 안에 있었다. Claude 두 adapter와 `tests/fixtures/u2_host.py`에는 해당 대상명·replacement 필드가 없었다. 두 저장소의 nonignored 파일 검색에서도 7원본의 현재 SHA를 고정한 참조는 발견하지 못했다. path 참조만 있는 기존 문서는 경로를 바꾸지 않으므로 추가 수정 근거가 아니다.

따라서 현재 확인으로 결과물 7개 밖의 구현 수정은 제안하지 않는다. 알려진 패턴과 현재 SHA 검색 결과이며 모든 과거 SHA·알려지지 않은 식별자·ignored private 파일까지 안전하다는 인증이 아니다. 구현 승인 전후 공개 노출 검사는 최종 후보 전체와 새 추적 문서·메시지·참조까지 포함한다. 추가 식별자가 나오면 조용히 범위를 늘리지 않고 경로·이유를 제시한다. 실제 사용자/경로를 흉내 낸 합성 negative fixture와 경로 거부 정규식, 필수 dependency/license attribution은 유지한다. 자체 source revision과 필요한 public upstream reference는 보존 가능하지만 외부 비교 provenance는 중립화한다. reviewer session/Owner message 식별자는 공개 문서에 필요한 최소 정보만 남기며 외부 자료를 추적하게 하는 값을 제거한다.

### Static Admission Evidence And Limits

Python `codex.py` 982–988행은 wall clock과 continuous elapsed의 오차를 2초로 제한한다. 1153행은 remaining budget을 고정 run deadline과 현재 시각의 차이로 제한하며, 1175행·2265행 등에서 남은 예산을 요구한다. 이는 정상 시계와 기존 경로에서 과거 deadline을 가진 allocation의 새 실행을 거부한다는 정적 근거다. v42–55 deadline은 2026-10-25 17:08:33.976 UTC, v56은 17:28:33.976 UTC, v57은 2026-10-26 03:41:25 UTC로 모두 검토 날짜 이전이다. 이 확인은 파일 읽기와 literal 해석이며 제품 실행·보안 재현 결과가 아니다. Rust에서 `replacement_work`는 현재 파일의 allocation 데이터에만 나타났으므로 Rust parity 주장은 데이터 대응으로 제한한다.

### Verification After Separate Implementation Approval

별도 구현 승인 시에만 위 데이터 계약 테스트와 private 정적 비교, 최종 후보 노출 검사, 링크/GFM 렌더링을 수행하는 안이다. 지금은 어떤 테스트도 실행하지 않았다. 전체 suite, Rust compile/test, rebuild, native/MCP/live 실행은 계획에서도 제외한다. 기존 12개 집중 검사나 native qualification의 PASS는 원래 소스에 대한 재사용 근거이며 새 후보의 새 PASS가 아니다. 변경 결과는 R1과 Owner 수락을 별도로 거친다. Commit·push는 계속 별도다.

## Reviewer Response Verbatim

아래는 받은 응답 원문이다. Driver 보정으로 고치지 않았다.

````markdown
# R0 Plan Review — 공개 이력 준비 7파일 정리안

**Reviewer 역할:** 독립 Claude Reviewer. 정적 읽기만 했고 도구 호출 0회입니다. 실제 model/session identity는 CLI metadata에 기록됩니다.

**판정: REVISE**

방향은 타당합니다. 원본 보존, 승인의 재사용 금지, 기존 native PASS를 새 소스에 부여하지 않는 점, guard 완화 금지가 모두 들어 있습니다. 그러나 다음 문제가 남아 있어 구현 승인 요청 전에 계획 문구를 보정해야 합니다.

- 최신 no-rebuild 범위와 Rust 검증 방식이 충돌합니다.
- 범위 확정 순서가 뒤집혀 있습니다.
- 합성 ID가 기존 승인 묶음 아래에서 갖는 admission 의미가 명시되지 않았습니다.
- 집중 테스트 내용이 R0 시점에 정해지지 않았습니다.
- verbatim 기록과 SHA 결속이 훼손될 위험이 있습니다.

보정은 모두 계획 문서 수준에서 가능합니다. 필수 보정 중 protected guard를 바꾸는 것은 없습니다. 다만 F2의 결과에 따라 구현 파일이 7개를 넘을 수 있으며, 아래에 명시했습니다.

---

## 필수 보정 (Blockers)

### F1. [High] Rust unit test 컴파일이 최신 no-rebuild 제약과 충돌
- **위치:** Required Verification §2 "Rust는 관련 unit test를 한 번의 묶음으로 컴파일·실행한다". Recommended Scope 표의 `codex-rs/app-server/src/lib.rs` 행 "기존 테스트 영역에 대응 검증을 추가".
- **정적 근거:**
  - `cargo test`는 `codex-app-server` crate 전체와 test target을 컴파일합니다. 제외 대상이 release binary rebuild만이 아니라 "rebuilds" 전반이라면, debug test build도 rebuild에 해당합니다.
  - 마지막 문단 "release 바이너리 rebuild ... 반복하지 않는다"는 release만 언급합니다. 그래서 §2와 최신 Owner 범위 사이에 해석 공백이 생깁니다.
  - FEAT-20261021-003:507–521에 따르면 `target/debug/incremental` 등의 삭제 제안이 있었습니다. 현재 cache 상태는 이 packet으로 알 수 없으므로, 컴파일 비용도 미확정입니다.
  - 컴파일하지 않은 Rust 테스트 코드를 공개 commit 후보에 넣으면 이후 첫 build에서 실패할 위험이 있습니다.
- **최소 보정 (권고안 B):**
  - lib.rs 변경을 `u2_allocation`의 v42–v57 raw string 안의 `replacement_work` 값 16개로만 한정합니다. 새 Rust 테스트는 이번 범위에서 제외합니다.
  - Rust 검증은 private 정적 parity 검사로 대체합니다. 예: `python3 -I` 스크립트로 lib.rs:3530–3545의 `r#"…"#` literal과 codex.py:487/490의 JSON을 각각 파싱하고 필드별로 비교합니다. 이는 파일 읽기이며 build가 아닙니다.
  - 결과 기록에 "Rust compile/test 미실행, 정적 parity만"을 명시합니다.
  - 합성 ID에 `"#`가 없으므로 raw string 종료 위험은 없습니다. 그래도 위 검사로 확인합니다.
- **대안 A:** Owner가 "filtered debug `cargo test` 1회"를 별도 예외로 명시 승인합니다. 이때 test 이름, cache 상태, 예상 비용을 미리 고정합니다.
- 두 안 모두 7파일 안에서 끝나며 guard 변경은 없습니다.

### F2. [High] 공개 노출 검사가 사후 단계에 있어 7파일 충분성이 확정되지 않음
- **위치:** Required Verification §4 "추가 발견 시 … 수정 범위를 먼저 조정". Recommended Scope "최소 수정 대상은 … 7파일". Preservation 절 "단일 작업 기록과 인덱스 연결".
- **정적 근거:**
  - §4는 검증 목록에 있지만, 수정 범위를 결정하는 입력입니다. R0와 구현 승인이 7파일 전제 위에서 이뤄진 뒤 범위가 바뀌면 승인 근거가 무효가 됩니다.
  - 7파일을 넘을 가능성이 구체적으로 보입니다.
    - (a) FEAT-20261022-001:7576의 "두 adapter"로 보아 Claude adapter에도 v42–v57 같은 allocation이 있을 수 있습니다.
    - (b) `tests/test_u2_host.py` 또는 `tests/fixtures/u2_host.py`에 PRIVATE_TARGET_* 값이 이미 hard-code되어 있을 수 있습니다.
    - (c) 일부 테스트나 고정 입력이 7파일의 SHA를 pin했을 수 있습니다. closeout:7575에 "고정 Python 입력75개"가 있고, codex.py가 그중 하나일 가능성이 있습니다.
    - (d) 후속 추적 항목(task 기록과 Development Index)을 선택하면 실제 편집은 최소 9파일입니다.
- **최소 보정:**
  - §4의 33+59파일 read-only 검색을 구현 승인 전 gate로 옮깁니다.
  - 같은 gate에서 7파일 SHA나 path를 pin한 테스트, fixture, 기록을 read-only로 검색합니다.
  - 그 결과로 최종 파일 목록을 확정해 Owner 승인 대상에 넣습니다.
  - 추적 기록 2파일은 "7개 결과물 + 추적 2개"로 승인 대상에 명시합니다.
- 이 gate는 검색만 하므로 test나 build에 해당하지 않습니다. 단, 이번 리뷰 세션에서는 수행하지 않았습니다.

### F3. [High] 합성 ID는 기존 승인·선행 binding 아래에서 admission 가능한 값이 됨
- **위치:** Recommended Scope "기존 approval/receipt는 새 합성 대상의 실행 승인이 아니며". codex.py:2283–2285. codex.py:521–528 및 lib.rs:3587의 resume_authorization 필드.
- **정적 근거:**
  - v42–v57 allocation은 기존 `approval_plan_sha256`, `owner_message_id`, `parent` digest를 그대로 유지합니다.
  - resume_authorization의 exact field(lib.rs:3586)에는 home/work가 없습니다. 따라서 코드상으로는 기존 승인 packet과 기존 private 선행 journal을 가진 실행이 새 합성 대상을 통과시킬 수 있습니다. 반대로 실제 대상은 거부됩니다.
  - 계획의 "승인이 아니다"는 정책 선언일 뿐, 코드의 fail-closed 근거를 제시하지 않습니다.
  - 정적 근거로 보이는 것은 deadline guard입니다. codex.py:508에서 `origin_wall_ms < run_deadline_ms == cfg`를 검사합니다.
    - v42–v55의 `1792948113976`은 2026-10-25 17:08:33 UTC 무렵입니다.
    - v56은 +1200초입니다.
    - v57의 `1792986085000`은 2026-10-26 03:41:25 UTC 무렵입니다.
    - 따라서 2026-10-27 기준으로 모두 만료된 것으로 보입니다.
  - 다만 `origin_wall_ms`가 실제 시계와 결속되는지는 packet 밖 코드에 달려 있습니다. README:42의 2초 wall/monotonic guard 등이 해당합니다. 이는 정적 추론일 뿐입니다.
- **최소 보정:**
  - 계획과 README에 "v42–v57 합성 ID는 역사 allocation의 공개용 label이다. 기존 승인은 이 label의 대상을 승인하지 않는다. 실행 불가 근거는 고정 run_deadline 만료(정적 추론)와 별도 승인 부재다"라고 적습니다.
  - "실제 대상에 대한 v42–v57 재실행 재현성은 의도적으로 상실된다"도 명시합니다.
  - deadline 값과 guard는 변경하지 않습니다.

### F4. [Medium-High] 집중 테스트 내용이 미정이고, 거부 테스트가 tautology가 될 위험
- **위치:** Required Verification §2 "가능한 순수 비교·기존 fixture 경로로 검사 … 테스트 이름과 범위는 구현 전 고정한다".
- **정적 근거:**
  - 실제 비교는 `LiveSession.launch()` 안에 있습니다(codex.py:2284–2285). 이 지점은 fd_controller, `validate_native_launch`의 binary/spec digest 검사, runtime spec 읽기를 지난 뒤에야 도달합니다.
  - 기존 fixture가 이 경로까지 도달하지 못하면, "잘못된 home/work/혼합 거부"는 테스트 안에서 비교식을 재구현하는 tautology가 됩니다.
  - 비교식을 helper로 추출하면 guard 코드 변경이 되어 범위를 넘습니다.
  - 테스트 내용이 R0 이후에 정해지면 R0가 그 테스트를 검토할 수 없습니다.
- **최소 보정:** 지금 테스트 범위를 고정합니다.
  - (i) v42–v56은 primary 합성 쌍, v57은 regression 합성 쌍과 정확히 일치하는지 확인합니다.
  - (ii) v41은 기존 값 그대로인지 확인합니다.
  - (iii) `replacement_work`를 가진 version 집합이 정확히 41–57인지 확인합니다.
  - (iv) 테스트 소스와 allocation 어디에도 PRIVATE 값이 없는지 확인합니다. 실제 값이 아닌 패턴 수준으로 검사합니다.
  - (v) 실제 guard 경로까지 가는 기존 fixture가 있을 때만 mismatch와 혼합 거부를 그 경로로 검사합니다. 없으면 "거부 경로는 미변경 guard 코드(diff 근거)로만 주장"이라고 기록합니다.
  - fixture 수정이 필요하면 8번째 파일이 되므로 F2 gate에서 함께 확정합니다.

### F5. [Medium] verbatim 기록·Owner 인용·SHA 결속의 권위가 공개 사본에서 흐려짐
- **위치:** Recommended Scope의 FEAT-20261022-001 행 "식별 가능한 인용문을 정리". plan 문서:270–272 "Reviewer Response Verbatim". FEAT-20261022-001:11/7571의 Owner 인용과 :13의 plan SHA. Preservation 절. WORKFLOW:66–68.
- **정적 근거:**
  - WORKFLOW는 최종 reviewer 응답의 verbatim 보존과 실제 Owner 결정의 구분을 요구합니다.
  - 공개 사본에서 인용문을 조용히 바꾸면, 그 문서가 verbatim이라고 표방하는 내용과 실제 bytes가 어긋납니다.
  - FEAT-20261022-001:13의 "승인 시점 SHA-256"은 원본 plan bytes에 결속되어 있습니다. 공개 사본에서는 이 SHA가 일치하지 않는데, 그 사실이 드러나지 않습니다.
  - 같은 문서의 :7562에는 `docs/briefs/PRIVATE_TARGET_WORK.md`와 `PRIVATE_TARGET_BRANCH`가 있습니다. 그런데 계획에는 branch용 중립 label이 없고, 문서 path와 코드 ID의 매핑 규칙도 없습니다.
- **최소 보정:**
  - 인용과 verbatim 구간의 치환은 inline 표지로 남깁니다. 예: `[공개용 중립화]`.
  - private 원본이 권위 있는 기록이고, 공개 사본은 파생물이라고 문서에 명시합니다. 이때 private 경로는 노출하지 않습니다.
  - 공개 사본에 남는 SHA는 "원본 bytes 기준"이라고 표기합니다.
  - branch와 문서 path의 중립 label을 코드 ID와 같은 표로 고정합니다.
  - 모두 문서 내부 수정이므로 파일 수는 늘지 않습니다.

### F6. [Medium] 이 R0 기록의 위치와 공개 안전성
- **위치:** Required Verification §5. 계획 머리말 "Private task artifact; … not a public commit input". WORKFLOW:60, 66–68.
- **정적 근거:** WORKFLOW는 R0 요청, 입력 identity, verbatim 응답, Driver 처분을 지정 기록에 두도록 요구합니다. 그런데 계획 자체는 private이고, 공개 기록 위치는 지정되지 않았습니다. 이 packet은 pseudonymize되어 있으므로, 공개 기록에 그대로 옮겨도 되는지도 결정해야 합니다.
- **최소 보정:**
  - R0 원문은 private task에 둡니다.
  - 공개 측(F2의 추적 기록)에는 pseudonymize된 입력 identity와 처분만 연결한다고 명시합니다.
  - 이 내용은 F2의 추적 2파일 안에서 처리합니다.

---

## 선택 권고 (Non-blocking)

- **O1. 명칭:** v41은 `u2-synthetic-h04-…` 형식입니다. 합성 표지를 일관되게 하려면 `synthetic-` 접두를 고려할 만합니다. 예: `synthetic-reference-a`. 접두가 있으면 F3의 equality admission이 미래의 실제 이름과 충돌할 여지도 줄어듭니다.
- **O2. 비권고 대안:** 실제 ID의 digest로 비교하면 원래 동작을 보존할 수 있습니다. 그러나 guard 식을 변경해야 하고, ID 엔트로피가 낮으면 사전 대입으로 역산될 수 있습니다. 채택하지 않는 것을 권합니다.
- **O3. README 범위:** README:3의 "진행 중" 문구는 Done 상태와 어긋납니다. 이번에는 합성 ID 관계 문단만 추가하고, 다른 stale 문구는 고치지 않거나 별도 항목으로 남기기를 권합니다.
- **O4. 공개 기준 명확화:** 다음 항목의 공개 여부를 F2 gate 기준에 명시하면 판단 편차가 줄어듭니다.
  - public upstream revision(예: FEAT-20261022-001:17의 source base)
  - reviewer session ID(plan:270)
  - task 이름(:7596–7597)
- **O5. 보완:** "16쌍 외 필드 동일" 비교에 Python과 Rust 양쪽의 JSON 재파싱 성공과 key 집합 동일을 포함하면 F1 정적 검사를 보완할 수 있습니다.

---

## 보정 후 범위 영향

| 항목 | 7파일 초과 여부 | Protected guard 변경 |
| --- | --- | --- |
| F1(B) / F3 / F4 / F5 | 없음 | 없음 |
| F2 | 발견 결과에 따라 Claude adapter, fixture 등 추가 가능. 추적 기록 2파일 선택 시 확정적으로 초과 | 없음 |
| F6 | F2 추적 파일 안에서 처리 | 없음 |
| O2 (비권고) | 없음 | **있음** |

## 미실행 검사와 증거 한계

- **미실행:** test, build, Rust compile, Python 실행, 검색(F2 gate), live, native, reviewer 재호출, Git 작업. 모든 판단은 제공된 발췌에 대한 정적 읽기입니다.
- **미제공 자료:**
  - Rust 쪽 `replacement_work` 사용처. 발췌상으로는 Rust가 이 값을 실제로 비교하는지 확인할 수 없고, F4의 Rust parity는 데이터 수준으로만 판단했습니다.
  - `Admission`, `scope_identity` 내부
  - `tests/fixtures/u2_host.py`
  - Claude adapter
  - 33+59 후보 전체
  - native journal과 대형 Work 원문
- **추론의 한계:**
  - F3의 deadline 만료는 epoch 계산과 guard 식에 근거한 추론이며, 실제 시계와의 결속은 확인하지 못했습니다.
  - surrogate digest 값은 실제 승인으로 취급하지 않았습니다.
  - v58 qualification과 이전 집중 검사는 원본 bytes에 대한 주장으로만 읽었습니다. 변경된 소스에 대한 live PASS는 추론하지 않습니다.
- 이 리뷰는 구현 승인이 아니며, R1·결과 수락·Git 작업과도 별개입니다.
````

## Owner Decision

R0 packet 전송·1회 정적 리뷰 승인만 확인했다. 보정안 구현 승인, R1 결과 수락, commit·push는 아직 없다.

## Implementation Selection — 2026-10-27

Owner가 R0 Driver 보정안의 7파일 구현과 필요한 Work·인덱스 기록, Python 데이터 계약 3개 및 정적·문서 검사만 승인했다. 이후 진행은 [CHORE-20261027-001](CHORE-20261027-001-public-history-preparation.md)에서만 기록한다. 위 R0 원문·당시 판정·Owner 결정은 그 시점의 이력으로 보존하며, R1·결과 수락·commit·push는 승인하지 않았다.
