# Delegation Profile Labels And Local-Link Oracle

- ID: PATCH-20261018-002
- Status: Done — human Owner accepted the exact result on 2026-10-18. The separately authorized exact source activation and bounded validation are complete. Git, release and adopter application remain withheld.
- Started: 2026-10-18
- Risk / mode: L2 / Standard.
- Roles: human Owner, Codex Driver, fresh Claude CLI Reviewer.

Current reading boundary: earlier pending/proposal/withheld statements and review responses below retain their original pre-acceptance meaning. The [dated Owner closeout](#owner-result-acceptance-and-source-contract-activation--2026-10-18) records the current result and source-activation state.

## Owner Authorization — 2026-10-18

> 제안한 후속 계획으로 진행해. 설치본 라벨과 링크 oracle 보정을 묶어 R0부터 최종 R1까지 이어가. 기존 증거를 재사용하고, 범위 내 작은 수정마다 재승인이나 전수 검증을 반복하지 마. 실제 활성화·Git·adopter 적용은 계속 보류해.

The Owner approved proposal-1, SHA-256 `2238f2015ee47d9b70202aa9a04f1ca37cddf00e9e3b5c6e31794e54c748eec6`, in [the combined plan](delegation-activation-label-and-link-oracle-plan.md). This record owns subsequent progress. A remains accepted and Done; [its exact result](CHORE-20261018-001-rule-entry-language-activation-preparation.md#owner-result-acceptance--2026-10-18) is an input, not reopened work. R0 through final R1 and bounded in-scope corrections are authorized together; no repeated permission or full-matrix run is required for each small correction.

## Inputs, Scope And Limits

Starting HEAD `d86bd1fd7754144e5c8538712724ae78571941bf` on the existing delegation development branch. The accepted A P is `49969df17f06e85cae8039c8dbd8cbf43a39f3ca8a317fceace4edd19596ad0b`; its 29 managed files and exact 17-document successor set remain baseline evidence. The approved proposal fixes 15 label files, the one local-link oracle and a bounded test helper, source-only result/activation proposal, and task-local admission changes. Runtime, authority semantics, dependencies, historical First B1/entry-1 wording and actual DR activation stay unchanged. Git and actual adopter actions remain withheld.

Use the plan's cumulative r11→A→follow-up selection: inherit unaffected 656×2/retained17×2 evidence, reproduce the old link failure once, run new helper normal/parent-O and selected consumers, four preregistered reader scenarios, GFM/token/inventory checks, and one final C01–C16 normal artifact lane. Historical evidence is not a fresh complete pass.

Per-call limits: acquire/canary/collection300s, oracle/focused600s, artifact1800s, reader300s including cleanup20s; static review900s plus cleanup20s. Keep CPython3.14.7 `-I -S -B`, native network/credential isolation, locks and process-group cleanup; 8/12GiB task and 25/15GiB free-space thresholds. Authentication must be `claude.ai/firstParty/pro`. Failure inputs/attempts stay distinct; no blanket test-file exemption or timeout increase.

Completion criteria are the five numbered outcomes in the approved plan: profile/grant clarity, before/after oracle evidence, exact new P evidence and limitations, final R1 disposition plus exact activation proposal, then Owner result acceptance. Actual activation remains a later decision.

## Retention And Next Step

Task-local scripts, review inputs/responses and required raw results support this task's R0/R1, before/after oracle claim and exact-P qualification. Keep them until those consumers and Owner acceptance are satisfied; then reassess disposable copies under standing cleanup authorization. The existing checkout contains unique uncommitted prior work and this concrete follow-up; retain it. Existing A/r11 evidence is referenced in place, not copied into a new archive.

Initial checkpoint before R0 (historical): R0 of the fixed label diff, fence-aware oracle, scoped admission and evidence reuse; implement authorized corrections after disposition. No implementation has been applied at this checkpoint.

Navigation change: selection notice and prior closeout follow-up pointer only. Index SHA-256 `c071ce7d3f10d44aff4dd1b5582b87f7b9a20eaccfd749b6fded33adcabf1503`; bounded diff SHA-256 `330fc6b0f34ad7e06d772c44e78c24f2e37d7c72d7ee9fdd60d1207cc7874378`. Criteria and purpose remain unchanged.

## R0 — Plan And Exact Proposed Delta

Fresh static Claude CLI review, model `claude-opus-5-5`, session `9afebd43-8be1-4ed2-8015-1e005730c561`; expected subscription route verified. Tools none, 161.26 seconds, exit0, no input drift, process group absent. Base HEAD is the starting revision above; proposed label diff SHA-256 `475fbb66001538f6a73fa8013bb5a7efda32a3f25279ecc9cb702bebfe665d6f`, input packet SHA-256 `f7648a10851484bcf1c6f862b97671d623baf2f8c1ef52b852fa07aa1a272630`. Artifact inputs absent from Git diff include proposed helper/label patch, Owner approval and this new record. Static review is not executed evidence or Owner acceptance.

### Verbatim Reviewer Response

# R0 정적 검토: 설치본 profile 라벨과 fenced-code 링크 oracle

## 판정

**조건부 수용 (Blocker 0, 필수 5, 선택 8)**

- fence helper의 의미는 정적으로 볼 때 계획의 인정 범위와 일치합니다.
- admission 구조는 byte 재구성 방식이라 경계가 충분히 좁습니다.
- 라벨 문안에서 기존 의미가 일부 빠졌습니다. 아래 필수 지적으로 보정하면 됩니다.
- 전체 suite(656×2)는 요구하지 않습니다. runtime, 권한, record 의미의 변경이 없고 영향이 test 1개와 문서 소비자에 한정되기 때문입니다.

## 증거 구분

- **정적 관찰**: 아래 모든 지적은 제공된 packet 바이트만 읽고 추론한 것입니다.
- **실행 증거**: 이 검토에는 없습니다. 테스트, collection, artifact, reader는 모두 계획 단계입니다.
- **확인 불가**: 다음 항목은 packet에 없어 판단하지 못했습니다.
  - `DECISION-GUIDE.md` 원문과 실제 fenced 예시의 형태
  - 15개 파일에서 수정 범위 밖에 남아 있는 entry-1 "current" 문장과 First B1 문장
  - `ActualWorkspaceInitTests`의 setUp과 decorator
  - controller 원문 (`selected_identities`, `allowed`)
  - 기존 GFM 검사의 대상 파일 목록

## 필수 지적

### M1. "human authentication" 비증명 문구 누락
- **위치**: docs 9개 공통 section 문장(`docs/README.md` 포함), `docs/MAINTAINING.md`
- **이유**: 기존 문장은 "proves no runtime qualification, **human authentication** or adopter readiness"였습니다. 새 문장은 "Owner authorization"으로 대체했는데, 승인과 인증은 다른 개념입니다. 본문 일부(SECURITY, CONCEPTS)가 비인증을 따로 설명하지만, section 진입 문장의 한정이 약해졌습니다.
- **최소 보정**: 목록에 하나를 추가합니다.
  - `...does not prove Owner authorization, human authentication, source-contract activation, runtime qualification or adopter readiness.`
  - MAINTAINING에도 같은 항목을 넣습니다.

### M2. SKILL 예외 조건의 의미 변경이 "Preserved authority conditions"와 충돌
- **위치**: `adapters/colvia-work/SKILL.md` 133행 부근
- **이유**:
  - packet의 보존 조건 블록은 "only under the activated delegation-1 contract" 원문을 담고 있습니다. 그런데 제안 edit은 정확히 그 문장을 "For an authorized exact delegation-1 installation"으로 바꿉니다.
  - 그 결과, 사용 시점에 adapter만 읽는 agent에게는 activation 조건이 사라집니다. docs/README가 요구하는 "activation + exact installation" 이중 승인과도 문장 단위로 어긋납니다.
- **최소 보정**: 둘 중 하나로 정리합니다.
  - (a) 보존 블록이 pre-edit baseline임을 명시하고, 새 문장을 보존 대상으로 다시 고정합니다.
  - (b) 문장을 다음과 같이 바꿉니다. `For a delegation-1 installation whose exact installation and source-contract activation the Owner has authorized ([Profile and authorization](../../docs/README.md#delegation-1-implementation-candidate)), ...`
  - 나머지 금지·소비·human 목록 문장은 그대로 둡니다.

### M3. 문서 내 entry-1 "current" 서술에 대한 우선순위 규칙 누락
- **위치**: docs 8개 공통 section 문장. REFERENCE, OPERATIONS 등 기존 문장에 "replaces this document's `entry-1` current-candidate statements"가 있던 곳입니다.
- **이유**:
  - 기존 문장은 같은 문서 안의 entry-1 current 서술을 이 section이 대체한다고 명시했습니다.
  - 새 문장 "Use this profile's rules for new operations"는 그 효과를 암시만 합니다. 다른 위치에 entry-1을 current로 서술한 문장이 남아 있으면 어느 쪽이 우선인지 근거가 없습니다.
  - 남은 문장이 있는지는 확인할 수 없습니다.
- **최소 보정**: 둘 중 하나를 택합니다.
  - 한 절을 추가합니다. `Where this document elsewhere describes `entry-1` as current, this section governs new operations.`
  - 또는 15개 파일에서 entry-1 current 서술의 잔존 여부를 검색하고, 그 결과(0건 또는 역사 문장 목록)를 R1 증거로 고정합니다.

### M4. baseline 실패의 예상 signature를 실행 전에 고정
- **위치**: 계획 Scope 2의 1단계, normal baseline attempt
- **이유**:
  - 기존 oracle은 첫 assertion 실패에서 멈춥니다. 따라서 baseline 실행은 fenced 예시 2개 중 **첫 번째 하나만** 실제로 관측합니다.
  - 예상 메시지를 고정하지 않으면, 다른 원인으로 실패해도 "예상 실패 재현"으로 기록될 수 있습니다.
- **최소 보정**:
  - 실행 전에 예상 결과를 고정합니다: 실패 test ID, `AssertionError`, 메시지 `DECISION-GUIDE.md: docs/docs/<첫 예시>`, non-zero exit.
  - 두 번째 예시는 "정적 확인만 있음"으로 기록합니다.
  - 불일치하면 non-pass로 남기고 원인을 분석합니다.

### M5. cloned controls의 비교 기준과 선택 목록의 정확성
- **위치**: 새 task-local controls, `a_selfcheck.py`에 대응하는 새 selfcheck
- **이유**:
  - `controller.selected_identities`는 parent-O에서 "exact two"를 강제합니다. 새 구성은 normal 8개, O 6개입니다.
  - 숫자만 바꾸면 subset, superset, 순서 변경 공격을 다시 검증하지 못합니다.
  - `test_policy_is_not_relaxed`는 `ANCHOR['invocation']['paths']['controls']`와 비교합니다. clone이 자기 자신이나 clone 경로를 기준으로 삼으면 oracle이 맹목이 됩니다.
- **최소 보정**:
  - 정확한 ordered ID 목록 2개를 선택 입력에 결속합니다. 각 목록마다 기존 `test_parent_o_exact_selection` 형태의 반례(앞부분만 선택, 미승인 ID 추가, 역순)를 둡니다.
  - Seatbelt 비교 기준은 A 원본 controls 경로로 고정합니다.
  - 변경 admission 반례를 포함합니다:
    - helper 외 1바이트 변경
    - 치환 표현의 0회 또는 2회 출현
    - mode 변경
    - 다른 protected 파일 변경

## 선택 지적

1. **fence 맹목성 경계**
   - unclosed fence는 문서 끝까지 링크를 숨깁니다. CommonMark에는 부합하지만, 실제 문서에 잘못된 fence 하나가 들어가면 이후 링크 회귀가 조용히 사라집니다.
   - list/blockquote 같은 container 안의 fence 종료도 인정 범위에 없습니다. 예: 4칸 이상 들여쓴 닫기.
   - 권장: R1에서 실제 source의 문서별 숨김 링크 수를 기록합니다(DECISION-GUIDE 2개, 나머지 0개). container fence를 non-claim 목록에 명시합니다.
   - 안전한 방향도 있습니다. 들여쓴 code, tab 들여쓰기, blockquote의 `> ```` 줄은 링크를 *더 많이* 검사하는 쪽이므로 숨김 위험이 없습니다.
2. **heading 유지 문장**
   - 현재 문안으로 충분히 명확하며, anchor나 링크를 고칠 필요는 없습니다.
   - 다만 heading의 "Candidate"가 상태 표시로 읽히지 않도록 다음 정도를 덧붙이는 것을 권합니다: `Its heading is retained for existing links and does not indicate activation status.`
3. **`docs/README.md`의 source checkout 문맥**
   - 첫 문장 "instructions for the verified installed release"는 source checkout에서 읽으면 사실과 다릅니다.
   - AGENTS 3행 "development candidate"와도 병존합니다.
   - 권장 문구: `for this release (source or verified installation)`.
4. **AGENTS.md**: 제거된 "Editing these files does not activate the contract"는 source 개발자에게 직접 필요한 한정입니다. 유지를 권합니다.
5. **collection 비교 방식**
   - unittest loader는 class 이름 순서로 수집하므로 `DocumentLinkOracleTests`가 기존 ID 사이에 끼어들 수 있습니다.
   - 비교는 "추가 3개를 제거한 subsequence가 기존 ordered 목록과 동일한지"로 정의하십시오.
6. **링크 조각과 적용 범위**
   - 이 oracle은 fragment를 검증하지 않고(`split("#")[0]`), adapter도 대상이 아닙니다.
   - 새 링크 텍스트가 들어간 `adapters/colvia-work/SKILL.md`, `AGENTS.md`, `README.md`의 `#delegation-1-implementation-candidate` anchor는 GFM/anchor 검사 대상에 포함되는지 확인하십시오.
7. **잔여 "candidate" 표현**
   - 수정하지 않은 문장에 남아 있습니다: SKILL "current Operations candidate section", GETTING-STARTED "exact candidate source".
   - heading을 참조하는 의미라면 유지해도 됩니다. R1 검색 결과에서 의도한 유지 문장으로 표시하십시오.
8. **unbound 호출 방식**
   - `ActualWorkspaceInitTests.test_document_port_local_links_resolve(self)`는 원본 메서드에 skip 계열 decorator나 setUp 의존이 없을 때만 의도대로 동작합니다(확인 불가).
   - 원본에 decorator가 없음을 정적으로 확인해 기록하십시오.

## 정적으로 확인된 긍정 사항

- **helper 의미**
  - 닫기 조건이 정확합니다: 같은 문자, opening 이상 길이, 0–3칸 들여쓰기, 뒤에는 공백·tab만.
  - backtick info string 거부가 정확하고, `re.escape`와 quantifier 조합도 올바릅니다.
  - 9개 사례가 각 분기를 모두 지납니다.
- **oracle 실효성**
  - 통합 positive test는 치환 전 oracle이었다면 `docs/docs/a.md`에서 실패합니다. 즉 치환 자체를 검출합니다.
  - 마지막 negative 사례는 메시지 정규식 `after-missing.md`로 fence 숨김과 fence 밖 검출을 함께 구분합니다.
  - `../outside.md`는 실제 파일이 존재하므로 containment 경로만 시험합니다.
- **admission**
  - 역적용 후 SHA와 mode를 exact 비교하므로, 그 밖의 바이트 변경을 막는 데 충분합니다. AST 대조는 보조로 남겨도 무해합니다.
  - 새 표현 문자열은 helper 본문에 나오지 않으므로 출현 1회 검사를 할 수 있습니다.
- **소유권과 권한**
  - 다음 사항은 계속 유지됩니다: no-grant human 기본, source-development 결과 수락은 human, 실제 activation·Git·adopter 보류, DR-0005 Draft 유지.

### Driver Disposition

- M1: accept: preserve explicit human-authentication non-proof
- M2: accept: preserve source-contract activation and exact installation authorization in adapter; packet preserved block was pre-edit baseline
- M3: accept: explicit precedence for new operations; historical limits unchanged
- M4: accept: preregister exact first failure signature; second remains static until synthetic negative check
- M5: accept: bind normal8 and parentO6 exact ordered lists with subset/superset/reversal negatives; preserve A Seatbelt as comparator; test exact delta/import/setup/mode/expression count/protected drift

All optional points are accepted as bounded clarity/check improvements; no anchor rename or expanded parser support. The corrected label diff is `3fc300476cde5774b52dcf97b8d39ebc703f13cd0d5f51b8f7d085480fba93a7`. The oracle is undecorated and reads only `self.source` plus TestCase assertions. The original first failure is preregistered as `AssertionError: DECISION-GUIDE.md: docs/decisions/DR-0002-checkout-1-contract-baseline.md`; the second fenced link remains a static finding until its separate helper negative case. Runtime and the other test assertions remain protected.

## Baseline Reproduction And Implementation

The old oracle ran once in attempt r00: 1 selected/run, 1 failure, 0 errors/skips/unstarted/unfinished; native exit1, wrapper exit2. It failed with the exact preregistered `AssertionError: False is not true : DECISION-GUIDE.md: docs/decisions/DR-0002-checkout-1-contract-baseline.md`. Execution remains non-pass. The second fenced example was not reached by this old method. Required safety66, TERM/KILL2, canary, ordered collection656 and smoke7 passed; process groups were absent and inputs unchanged. The existing accepted A frozen source was reused after proving every traversed document, runtime and test dependency equal to current pre-edit bytes; changed source-only task/index text lies outside this oracle traversal.

A distinct corrected attempt r01 consumes the preserved failure and exact correction disposition; no failed slot is cleared or reused. Applied 15 managed label files and the bounded oracle/helper in one batch. Existing imports, setup, other test functions and runtime stay unchanged. Raw implementation diff SHA-256 `af9b86265e31126f8919d16280a4f22bc9a40d8ce757cda6777c1a15d8249698`; the 3 new helper IDs do not replace old IDs. Fragment/reference/autolink/indented/container code parsing and full GFM are outside the helper claim; GFM rendering remains a separate document check.

### Full Managed Label Coverage Before Freeze

The broad managed scan found one remaining current-state label in the CLAUDE tool projection, nine `activation remains pending` headers and two source-status paragraphs. They are the same installed-label defect covered by the approved plan’s whole-managed search, so the final label delta covers 16 managed files. The CLAUDE change only replaces its current profile label; the separate project-owned CLAUDE preservation question stays out of scope. First B1 historical labels at Operations45 and Workspace Contract327 remain byte-identical. Actual source decision/activation records are unchanged.

The first static-check attempt also expected the two historical labels in reverse order; the initial ordering-only diagnosis was incomplete. A second attempt exposed the missed CLAUDE label. Both non-passes and their diagnostics remain preserved; the final checker compares the exact two historical paths/lines and rejects all other current unactivated/pending labels. This is an authoring correction before current input freeze, not a product test rerun or weakened acceptance criterion. Additional diff SHA-256 `19178cfb956afe78e378cb0625cc95a26940a91a90e3bba1bb76377855b0b6c0`.


## Frozen Candidate And Targeted Evidence — 2026-10-18

새 후보는 managed29와 successor17을 모두 native/reader 입력과 bytes/mode 동일하게 고정했다. source digest는 `d7f59a6acc6a517ea858c5cf27a87ea2714eb6d073d5d37062dc34bbec335f26`이다. 이후 이 진행 기록의 evidence/제안 추가는 source-only이며 frozen snapshot에 소급 포함하지 않는다. Runtime/권한/record 의미와 actual activation 기록은 변하지 않았다.

| 검사 | 새 실행 결과 | 의미와 한계 |
| --- | --- | --- |
| 기존 oracle 기준선 | r00: 1 failure / 1 run, native exit1, wrapper exit2 | 정확한 첫 fenced 예시 오탐 재현. non-pass로 보존; 두 번째 예시는 기존 oracle에서 도달하지 않음. |
| safety / TERM-KILL | r00·r01 각각66 / 2 통과 | exact test delta와 normal8/O6 ordered selection, inherited Seatbelt/resource/cleanup 조건. |
| collection | r01 659 = 기존656 + helper3 | 기존 ordered subsequence와 factory16 동일. collection을 실행 PASS 수로 세지 않음. |
| smoke | r01 7/7, 16.503초 | native exit0, skip/unstarted/error0, cleanup 확인. |
| focused normal | 8/8, 20.446초 | 링크 oracle·negative/missing/path escape·실제 문서/view 소비자. |
| focused parent-O | 6/6, 19.027초 | 두 view와 oracle/helper를 최적화 parent에서 확인. 전체 최적화 suite 재실행 아님. |
| reader fixture setup | 30개 고정 CLI/helper 호출 성공 | 실제 원래 합성 target의 view/work/prepare를 관측하고 read-only 사본으로 전달. apply 없음. |
| token | AGENTS916, README448, Getting Started2602; 합3966 | o200k_base/tiktoken0.13.0, network/write denied. 기준4384 non-pass는 역사로 보존. |
| artifact C01–C16 | 이 freeze 시점에는 실행 중; 이후16/16 완료 | [Exact Artifact Closure](#exact-artifact-closure-before-r1)의 확정 결과를 참조한다. |

기존 r11 complete656×2와 retained17×2는 변경 없는 runtime/기존 assertion의 근거로 재사용한다. 전체659개를 새 후보에서 실행했다고 주장하지 않는다. 기존 보호104개 중103개는 exact unchanged이고, 나머지 test 파일은 helper 삽입과 oracle 단일 표현만 역적용하면 원래 bytes/mode와 일치한다. 정적 검사에서 두 역사 First B1 라벨만 의도적으로 남고, 링크 oracle이 제외하는 fenced 링크는 DECISION-GUIDE의2개뿐이다. runtime/data schema, admission의 credential/network/resource/process 경계는 확대하지 않았다.

### Reader Disposition

모델 `claude-opus-5-5`, fresh session4개, `claude.ai/firstParty/pro`, Read-only 경계 probe 성공 후 각1회 관측했다. 네 실행 모두 exit0, 입력 drift0, group absence/cleanup 확인이다. 실행 성공과 strict 독해 성공을 구분한다.

| 사례 | strict 판정 | 관측 |
| --- | --- | --- |
| L-S source | 미달 | source entry 및 activation/Git/adopter 보류를 이해했지만 필수 DR-0005 원문을 읽지 않았다. 파일은 fixture에 있었고, 답변은 기존 A/PATCH 요약에 의존하며 경로를 찾지 못했다고 밝혔다. source의 no-install/no-typed-Work 조건도 명시하지 않았다. |
| L-G exact grant | 통과 | 합성 Owner activation+exact 설치 전제에서 delegate-1/work-a/isolated-worktree/a,b의 ordinary accept만 허용. 오래된 미활성 라벨로 거부하지 않고 live guard·confirmation·근거 한계를 유지했다. |
| L-H no grant | 통과 | 실제 no-grant refusal과 human 기본 수락을 설명하고 grant를 발명하지 않았다. |
| L-R actor mismatch | 통과 | delegate-other 요청과 delegate-1 grant 불일치 및 실제 prepare 거부를 설명했다. actor 재표기 우회 없음. stale/consumed/revoked 전수 관측은 아님. |

Strict3/4이며 L-S를 PASS로 바꾸거나 성공할 때까지 반복하지 않는다. 이 source-only 탐색 한계는 R1에 제출하며 일반 자동 발견/온보딩 품질을 주장하지 않는다. 현 catalog에 DR-0005 직접 행이 없다는 정적 사실은 기존 상태이며 이번 managed label/oracle 수정이 만든 회귀로 단정하지 않는다. 이전 A의 language5/5와 strict1/5는 별도 역사 관측으로 유지하고, 언어 규칙 bytes가 변하지 않았다는 범위에서만 재사용한다. 실제 source 계약은 여전히 DR-0005 Draft이고 이 합성 전제가 실제 활성화나 adopter 승인은 아니다.

## Exact Successor Proposal — Not Accepted Or Activated

이번 PATCH의 exact 제출안은 아래17개 및 새 P다. 이전 A는 수락/Done 상태로 유지한다. A에 있던 두 label 선택지는 이번 Owner가 라벨 보정 후 새 P 검증을 선정하면서 이 작업 범위에서 해소됐고, 옛 “payload를 바꾸지 않는다” 제안은 이 새 제출안에 적용하지 않는다. 이전 역사 문장을 소급 수정하지 않는다. 이 표의 분류는 기술11과 entry/설명/data6이며 설명 문서를 새 normative authority로 승격하지 않는다.

| 문서 | 분류 | Bytes | 제안 SHA-256 | 정확한 변경·적용 범위 |
| --- | --- | --- | --- | --- |
| [docs/WORKSPACE-CONTRACT.md](../WORKSPACE-CONTRACT.md) | 기술 계약11 | 39265 | `41a9df6f039ae1d79778e7ff581238e96caa53fba13494a6aa72d4c2716c3083` | Root primitives/current candidate pointers 및 Delegation-1 Implementation Candidate: rank6·managed29·schema4 pair·old writer/late-lock·detach provenance·one-way boundary. 기존 identity/truth/recovery 및 First B1 보장 유지. |
| [docs/GENERAL-WORK.md](../GENERAL-WORK.md) | 기술 계약11 | 46488 | `17616358e2e90ddc79bbe1d547657d65fb23cc705ef2d754131ed9d722bd7279` | 기본 human path를 유지하고 Delegation-1 Implementation Candidate의 exact ordinary isolated accept 예외·K 소비·selected revoke·ancestry·parent 경계를 적용한다. Current machine command/schema 설명 정합. |
| [docs/GUIDED-INTENT-FORMATION.md](../GUIDED-INTENT-FORMATION.md) | 기술 계약11 | 5762 | `3779746783fcdafb031b31496591cbc83b0440f910d370814daf211d7c12d0a6` | Draft And Acceptance 및 Delegation-1 Implementation Candidate: schema3 non-null grant, exact human intent acceptance, no-grant/parent 구분. intent 수락 주체는 변경하지 않는다. |
| [docs/REFERENCE.md](../REFERENCE.md) | 기술 계약11 | 61718 | `40846b4d32cada4ee9d7389bbfa94988556de2d654c27a9cde3e656bcba32585` | Current commands/outcomes/diagnostics, Document Language, Repository-Owned Rules 및 Delegation-1 Implementation Candidate. 저장 언어 우선순위·mandatory 충돌·project authority·정확한 grant/조회 한계를 함께 적용한다. |
| [docs/OPERATIONS.md](../OPERATIONS.md) | 기술 계약11 | 14962 | `831bd67e4039dfa609c76f153671af7459dfc826420b0c9710ebe71f7f6d3e2b` | delegation-1 profile의 init/update/repair/detach 안내와 Delegation-1 Implementation Candidate. exact entry-1 predecessor·forward recovery·동일 window rollback·과거 entry 전환 의미 유지. |
| [docs/MANUAL-OPERATION.md](../MANUAL-OPERATION.md) | 기술 계약11 | 4880 | `50dfcf918d0ad49daa8dd98071db9071266f23a48f28e489adaa70ef59e429c2` | Retained Evidence/Recovery Boundary 및 Delegation-1 Implementation Candidate: 기존 기록과 schema4 pairing을 구분하고 exact-source 복구·권한 기록 보존. |
| [docs/SECURITY-AND-SUPPORT.md](../SECURITY-AND-SUPPORT.md) | 기술 계약11 | 8666 | `1d2deb6dc97378fff618a55c99f3d9ffc152d4757b7cd791e2487c7e919ab2c0` | Runtime And Scope 및 Delegation-1 Implementation Candidate: actor 비인증·host payload enforcement 미검증·기존 플랫폼/실제사용 제한. 역사 관측을 새 후보 PASS로 바꾸지 않는다. |
| [docs/MAINTAINING.md](../MAINTAINING.md) | 기술 계약11 | 22401 | `9265382726b28ee0667c9be96b154e5a7fdec35a9264c47ea1b3248ef9ce8446` | Validation Frequency/Evidence Reuse, Reading Budget, Inventory Window Compatibility, Delegation-1 Implementation Candidate. 역사 campaign cap과 Owner continuation 예외, cumulative risk-based selection, fresh artifact/reader와 inherited 증거 구분. |
| [docs/GETTING-STARTED.md](../GETTING-STARTED.md) | 기술 계약11 | 13070 | `16607a11d475a29a506b5c93f3a7f6b80caa4e90a0f2ec25d810256f678c4f7b` | Start/init, human review, current Delegation-1 Implementation Candidate. source/installed 구분·현재 profile/schema·exact predecessor·one-way 경고. 보존된 Entry-1 절은 역사 안내. |
| [adapters/colvia-work/SKILL.md](../../adapters/colvia-work/SKILL.md) | 기술 계약11 | 27057 | `e5347f5cad5bf04787fa6fa5330638e6a36acf862cd4571e9df47900bd852890` | 진입/설명/Document Language pointer, project narrative/local override와 Delegation-1 acceptance 안내. 정확한 grant 없는 수락·일반 source self-accept·parent 수락 위임은 없음. |
| [docs/development/CHECKOUT-1-STRUCTURE.md](../development/CHECKOUT-1-STRUCTURE.md) | 기술 계약11 | 53395 | `288fb2347c945015ce4ea9940198bafe350aaaf4a8c63487f69de87f06810e9e` | 새 Current reading boundary 및 Delegation-1 Successor Delta의3개 절만 명시 대체: Window, schema3 grant/actor, selected ancestry/소비, lifecycle schema4. 나머지 보존 구조는 불변. |
| [AGENTS.md](../../AGENTS.md) | entry/설명/data6 | 4550 | `a05b299186dccc5941c62622bd712993cbf306fe183319e198715aa432fb3b2a` | profile 라벨과 source/installed 조건부 경로; 문서·binding이 Owner 승인/활성화를 증명하지 않는다. Authority Floor와 human 기본/정확한 grant 경계 유지. |
| [CLAUDE.md](../../CLAUDE.md) | entry/설명/data6 | 416 | `bab2972abc99133e9b3ad3c1aa442f45e2cd4da6b7385d70e11f07984c42c3b5` | thin canonical pointer와 delegation-1 profile 라벨. project-owned CLAUDE 보존 문제는 이 범위 밖이다. |
| [docs/CONCEPTS.md](../CONCEPTS.md) | entry/설명/data6 | 4635 | `b75a3854b81fa592d28593553990599e8f70c24b40a2369a57686d13234fb0da` | 기본 human path 설명과 Delegation-1 Implementation Candidate의 한정 예외/소비 시점. 설명용이며 normative 기술 집합을 늘리지 않는다. |
| [docs/README.md](../README.md) | entry/설명/data6 | 7085 | `c6f8e780e16bf431beea52597427373941e095fbe079f2aa60f2deec214d67da` | source 또는 검증된 설치의 profile 지침, 별도 Owner 활성화/exact 설치와 bound grant 조건. 유지 heading은 활성화 상태를 표시하지 않는다. |
| [README.md](../../README.md) | entry/설명/data6 | 2237 | `15c39342911d29b686024e51f58d3fdf404ad5aaa7075248135a7d4cd74deac3` | delegation-1 profile setup/navigation. source-contract 활성화와 exact 설치 승인을 별개로 요구한다. |
| [PRODUCT-CAPABILITIES.json](../../PRODUCT-CAPABILITIES.json) | entry/설명/data6 | 5167 | `6f98db7c9f13a4c76896868a197399c768292da66e0c9cd09b0ce9c5da809e35` | 이번 변경은 project-local-product-lifecycle boundary의 미활성 라벨만 보정한다. 앞선 delegated evidence 설명과 runtime 필드는 불변이다. |

- P: `98e4b0aa321383d648843d6bb05ea150bf15da5816a60403c04d0c5ea42f6a35` (`product-release-98e4b0aa321383d648843d6b`), delegation-1 / managed29.
- Q: `49969df17f06e85cae8039c8dbd8cbf43a39f3ca8a317fceace4edd19596ad0b` (`product-release-49969df17f06e85cae8039c8`), Owner가 수락한 A P 그대로.
- exact entry-1 predecessor: `2216a2634eb3fa5d6a8bfa7c7d4847b29fb2443ba7b367156c15b15ddb5a17e0`; 추가 predecessor 없음.
- DR-0005 입력: 5690 bytes / `737c34eb9cc323185af0ceef0709c5a889b02a5a8ba5d04fbce3f203c09dbc5c`, Draft 및 최종3절 공란 그대로.
- `final-candidate.json` SHA-256 `98d4ef35ed7fc5fd018977f76285b6018fc96727ee065075b9e03fa3b39d6436`; `reader-disposition.json` SHA-256 `fba681ceddcde646eb960ebf752210eba72a6294f02ab027409343efa8b656ce`. named consumer는 최종 R1 및 Owner의 exact 결과/활성화 판단이다.

### Proposed DR-0005 Final Sections

다음은 Owner가 위 exact 제안과 named amendments를 수락할 때만 DR-0005의 빈 절에 넣을 문안이다. 실제 결정 날짜와 Owner 원문·이 PATCH의 수락 당시 hash를 activation appendix에 결속한다. 이 제안의 작성 날짜를 발효일로 사용하지 않는다.

> Decision: Accept the exact delegation-1 successor identified in the PATCH-20261018-002 preparation record, limited to the accepted intent-bound ordinary isolated-worker accept grant, its actor/consumption/revocation/recovery rules, paired lifecycle schema 4 and exact entry-1 transition. The Owner retains intent and source-development result acceptance, all ungranted actions and parent acceptance. Activate only with the separate dated Owner activation record naming these exact document hashes, P identity and the clauses below. A development result, review verdict or synthetic installation does not activate them.
>
> Rationale: The bounded grant permits one named ordinary result acceptance while keeping the existing exact intent/Work identity, content checks, serialized publication and recovery guarantees. The source/installed entry and artifact-language guidance make the applicable project rules explicit. Reuse of identified unchanged assertions plus fresh consumer/artifact evidence is proportional to the prose delta. The three installed reader cases meet their preregistered criteria; the source reader does not, because it missed the required DR-0005 original. These one-shot observations do not establish general comprehension, automatic source discovery, public onboarding, caller authentication or unattended operation.
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

> At the DR-0006 source-only relocation, the unchanged AGENTS/CLAUDE entry had no verified automatic route to these source rules. The separately accepted entry amendment identified in PATCH-20261018-002 adds a conditional route through source-only CONTRIBUTING when the agent is explicitly asked to develop Colvia itself in its trusted source checkout. An installed project still starts with its own rules and the verified manual/adapter from ./colvia view; presence inside a managed manual never selects source development. This route does not require runtime installation or typed Work creation, and adds no task-selection or execution authority. DR-0006's other relocated obligations and historical identities remain unchanged.

이 단락은 위 named DR-0003 source-entry appendix에 함께 명시하고 actual revised WORKFLOW hash를 활성화 기록에 남기는 제안이다. 새 source 언어 정책은 만들지 않는다. 이번 task의 shipped 영어/Owner 기록 한국어는 해당 task 지시일 뿐이다.

### DR-0002 / DR-0004 Successor And Installed Labels

별도 activation 시 DR-0004의 entry-1 및 First B1 supplement에서 위17개 표가 특정한 ordinary accept·intent shape·window/schema·lifecycle/writer 조항만 DR-0005 successor로 대체하도록 제안한다. DR-0002/0003/0004 전체를 Superseded로 바꾸지 않는다. 원래 accepted prefix/hash, exact entry-1 predecessor, First B1의0600/0644 reader 허용과 publication/sync 의무는 보존한다. 후속 source-only appendix는 exact 새 P 및 위 표를 가리키며 역사 기록을 다시 쓰지 않는다.

설치된 managed 문서는 profile과 정확한 grant 조건을 설명한다. 남겨둔 `Delegation-1 Implementation Candidate` heading은 링크용이며 활성화 상태가 아니다. Owner의 source-contract activation 및 exact 설치/업데이트 승인이 각각 있어야 한다. 문서/binding/준비 token은 승인·인증·활성화의 증명이 아니다. Core가 source 결정 문서를 조회하거나 활성화 여부를 인증·강제한다고 주장하지 않는다. 역사 First B1 라벨2개는 보존하며, 후속 activation 기록이 명시한 범위만 효력을 바꾼다.

이 제출안은 실제 DR-0005/0003/0004/0006/WORKFLOW의 상태·최종 절·accepted history에 적용하지 않았다. 실제 발효일은 나중의 Owner 결정과 정확한 적용 기록으로만 정한다. 새로 고정한 payload를 설치 현장에서 문구만 바꾸어 재사용해서는 안 된다.

### Remaining Boundary

새 링크 oracle은 코드 fence 오탐만 보정한다. fragment, reference/autolink, indented/container code 및 full GFM parser 지원을 주장하지 않는다. 별도의 GFM 문서/anchor 검사는 최종 기록까지 수행한다. Strict source reader 미달과 기존 A/r11의 생산환경·인증·host enforcement·실사용 한계는 남는다. 결과 수락은 human Owner에게 있으며 실제 activation·Git·release·adopter 적용은 계속 보류한다. 일반 adopter 적용 권고는 보류, 현재 설치 상태는 확인하지 않았다.


## Exact Artifact Closure Before R1

고정 P `98e4b0aa321383d648843d6bb05ea150bf15da5816a60403c04d0c5ea42f6a35`의 normal C01–C16이16/16 PASS, 566.553초, exit0으로 끝났다. 전체659개를 수집했지만 선택16개만 실행했다. skip/xfail/미시작/미완료0, source/control/runtime 입력 drift0, 자연 종료 및 group absence/cleanup을 확인했다. 한도1800초는 올리지 않았고 artifact 재실행은 없다.

고정 명령은 `python3.14 -I -S -B run-native-labels.py r01 artifact-final`이다. Python3.14.7와 source digest `d7f59a6acc6a517ea858c5cf27a87ea2714eb6d073d5d37062dc34bbec335f26` 및 정확한 native 입력/argv/Seatbelt는 보존된 invocation에 결속했다. result SHA-256 `4c5997caa7c9db76d96f57d306857df468aa2fbc0590be4d0fd678cc45f22c2f`, counts `ed206207770f0dc543dd6dcee1df3db2bf1ef4584bc8399157bf7b348a5c26b1`, executed order `6a220a1d953ae33f6ae52f0335ff6b0703698136df449949cbd908af396072da`. `artifact-closure.json`은 이 command와 원본 결과를 연결한다. 독자 strict3/4 및 소스 실제 활성화 보류는 이 통과로 바뀌지 않는다.


## R1 — Final Result Review And Proposal Correction

Fresh static Claude CLI `claude-opus-5-5`, session `b2ff88e3-6783-4ab8-afb3-5de99f88afd7`, expected subscription route verified; tools none, 184.08초/exit0, input drift0, group absent, cleanup 오류0. Input packet SHA-256 `b4afea234986e626f228bf3fd1ac88d76d25defce07dfe05282b67fa89836af1`, cumulative uncommitted Git diff SHA-256 `618acf03875dc3bd6c6a825c8bf78de3132aea5d9c167ba0af1ea0005001cdcc`; untracked record/plan 및 private controls/fixtures/evidence는 별도 exact input identity로 결속했다. Reviewer 정적 판단과 Driver 실행 증거, Owner 결정은 별개다.

### Verbatim Reviewer Response

# 최종 R1 정적 검토: delegation-1 설치본 라벨과 fenced-link oracle

## 판정

**제출 가능, 조건부 (Blocker 0 / 필수 1 / 선택 7)**

- **결과 제출**: 명시된 한계를 붙여 지금 Owner에게 제출할 수 있습니다.
  - 대상은 16개 label 파일, test-only fence helper와 oracle 단일 표현, 새 P `98e4b0aa…`, 그리고 targeted 증거입니다.
  - 필수 지적 M1은 결과 bytes나 실행 증거를 바꾸지 않습니다.
- **활성화 제안**: M1을 제안 문안에 반영한 뒤 exact activation proposal로 제출하십시오.
  - 반영은 source-only 제안 텍스트 추가로 끝납니다. 실제 source 편집, reader 재시도, 재실행은 필요 없습니다.
- **재실행**: 전체 659개 재실행은 요구하지 않습니다.
  - 이번 변경은 runtime, 권한, record 의미에 닿지 않습니다.
  - 변경된 test 파일은 정확한 역적용으로 원래 bytes로 돌아갑니다.
  - 변경 문서의 직접 소비자는 fresh focused, smoke, artifact16, 또는 내용과 무관한 inherited fixture 중 하나에 대응됩니다.

## 증거 구분

- **정적 관찰(이 검토가 직접 한 것)**: packet 안의 diff, 원문 절, helper 코드, admission/controller 코드, JSON 기록, reader 응답만 읽고 추론했습니다. 아래 지적은 모두 이 범주입니다.
- **Driver가 기록한 실행 증거(제가 실행한 것이 아님)**:
  - r00: 이전 oracle이 사전 고정한 signature와 정확히 같게 실패했습니다(non-pass로 보존).
  - r01: safety66×2, TERM/KILL 2×2, canary, collection659(=656+3), smoke 7/7, focused normal 8/8, parent-O 6/6, artifact C01–C16 16/16 (566.553초).
  - 그 밖: token 3966, GFM 24파일/353링크 issues 0, reader 4건(실행·경계 4/4, strict 3/4).
- **확인 불가**:
  - 15개 문서의 전체 본문. 잔여 entry-1 "current" 문장과 "candidate" 문장의 전수를 직접 보지 못했습니다.
  - inherited 소비자 test 본문. 예: `test_document_port_workspace_error_codes_are_documented`, `test_contract_inventory_bytes_sizes_and_paths_are_strict`가 변경 문구에 의존하지 않는지.
  - `docs/development/README.md`와 `WORKFLOW.md` 원문, DR-0003/0004/0006 원문.
  - `capabilities_changed_rows`의 비교 기준(아래 선택 2).
  - r11 656×2 원본 결과. identity 재사용 주장으로만 받았습니다.

## 필수 지적

### M1. 활성화 제안에 DECISION-GUIDE 탐색 갱신이 빠져 있음

- **대상**: exact 활성화 제안(PROPOSAL ONLY). 결과 수락에는 비차단입니다.
- **근거(정적)**:
  - `docs/DECISION-GUIDE.md`의 "For the current technical set, follow the exact [entry-1 activation]… and [First B1 supplement]…" 문장은 DR-0005 활성화 뒤에 사실과 달라집니다.
  - 같은 guide의 catalog에는 DR-0005 행이 없습니다. 이 catalog는 스스로를 "records relevant to these entry, procedure and technical-contract boundaries"라고 설명합니다.
  - 제안은 Development Index에 대한 source-only navigation 추가와 WORKFLOW 문단 대체만 명시하고, DECISION-GUIDE는 다루지 않습니다.
  - 따라서 제안대로 활성화하면 source decision guide가 계속 entry-1을 현행 기술 집합으로 안내합니다. 활성화 기록 자체가 새 source 불일치를 만듭니다.
- **L-S 미달과의 관계**: L-S가 DR-0005를 찾지 못한 원인과 같은 탐색 공백입니다. 다만 그 공백은 이번 managed label 수정이 만든 회귀가 아니라 기존 상태입니다.
- **최소 보정**: 활성화 제안에 named source-only navigation 항목 하나를 추가합니다. 내용은 활성화 시점에 다음 두 가지를 함께 기록한다는 것입니다.
  - DECISION-GUIDE catalog에 DR-0005 행을 추가합니다(상태와 activation appendix 링크).
  - "current technical set" 문장이 DR-0005 activation 기록을 가리키게 합니다.
- **하지 않아도 되는 것**: 지금 DECISION-GUIDE를 편집하거나 L-S를 다시 시도할 필요는 없습니다. 이 항목은 DR-0006 relocation 결과를 재승인하지 않는다는 점도 함께 명시하십시오.

## 집중 항목별 판단

### 1. 인간 인증 비증명과 "활성화 + exact 설치" 이중 승인 — 충족
- 공통 section 문구는 Owner authorization, human authentication, source-contract activation, runtime qualification, adopter readiness 다섯 가지를 모두 비증명으로 명시합니다(R0 M1 반영 확인).
- MAINTAINING은 human authentication, activation, adopter update를 명시합니다.
- AGENTS는 Owner authorization과 activation을 명시하고, Authority Floor의 "confirmation tokens do not prove human authorization"과 "Actor strings… not authentication"이 나머지를 보완합니다.
- 이중 조건은 다섯 곳 모두에 들어 있습니다: SKILL 133행 부근, docs/README, README, GETTING-STARTED, PRODUCT-CAPABILITIES. R0 M2 반영을 확인했습니다.

### 2. Bounded grant, human 기본값, 라벨 — 충족
- "no grant keeps the human default"와 "source development result acceptance remains human"이 유지됩니다.
- 유지된 heading은 활성화 상태를 표시하지 않는다는 문장이 들어갔습니다.
- 우선순위 문장 "Where this document elsewhere describes `entry-1` as current, this section governs new operations"가 추가됐습니다(R0 M3).
- 라벨 문구가 활성화 여부에 중립이므로, 같은 bytes가 활성화 뒤에도 사실로 남습니다. exact P를 그대로 활성화 대상으로 삼으려는 설계와 맞습니다.

### 3. First B1 역사 예외 — 보존 확인, 한계 공개 권장(선택 1)
- `docs/OPERATIONS.md:45`와 `docs/WORKSPACE-CONTRACT.md:327`이 byte-identical로 남았고, 이 둘 외의 미활성/pending 라벨은 거부됩니다. scope가 정한 대로입니다.

### 4. Fence 종료 처리와 oracle 실효성 — 충족(정적)
- **닫기 조건이 정확합니다**: 같은 문자, opening 이상 길이, 0–3칸 들여쓰기, 뒤에는 공백·tab만. backtick info string 거부와 tilde info 허용도 CommonMark와 맞습니다.
- **불일치는 안전한 방향입니다**: tab이나 4칸 들여쓴 opener를 fence로 보지 않아 링크를 더 많이 검사합니다.
- **실효성이 입증됩니다**:
  - 통합 positive test는 이전 oracle이었다면 `docs/docs/a.md`에서 실패합니다.
  - 다섯 번째 negative test는 메시지 `after-missing.md`로 "fence 숨김 성공"과 "fence 밖 검출"을 구분합니다. fence가 무시됐다면 메시지가 `README.md: missing.md`가 되어 regex에 걸리지 않습니다.
  - `../outside.md`는 실제 파일이 있으므로 containment 분기만 시험합니다.
- **실제 corpus와 일치합니다**: 제외된 링크는 DECISION-GUIDE의 2개뿐이고, 이는 r00이 관측한 첫 실패 링크(DR-0002)와 `text` fence 안의 두 번째 링크에 해당합니다.
- **unbound 호출이 안전합니다**: 원 method에 decorator가 없고 `self.source`와 assert만 쓰므로 unbound 호출이 의도대로 동작합니다. unittest assert는 `-O`에 영향받지 않으므로 parent-O 결과도 유효합니다.

### 5. 역적용 admission과 선택 음성 테스트 — 충족
- `validate_test_delta`는 다음을 모두 요구하므로, 사실상 bytes를 정확히 고정합니다:
  - addition과 새 표현이 각각 정확히 1회 출현
  - 역적용 결과가 old SHA와 일치
  - raw bytes가 new SHA와 일치
  - mode는 `validate_anchor`가 `old_mode`로 고정
- AST 대조는 중복이지만 해가 없습니다.
- normal8과 parent-O6은 exact list 동등성으로 묶였고, subset, superset, 역순 반례가 있습니다.
- normal 선택이 test 파일 SHA를 key로 쓰므로 baseline(1개)과 corrected(8개)가 분리됩니다.
- Seatbelt 비교 기준은 A 원본 controls 절대경로로 고정돼 있습니다. `campaign.json`은 root와 approval hash만 바뀌었습니다.

### 6. 누적 증거 대응과 한계 — 대체로 충족
- `test_runtime_capability_declaration_matches_admission`은 매핑에서 "inherited"로 분류됐지만, 실제로는 최종 digest `d7f59a6…`에서 실행된 smoke7에 포함돼 fresh 실행됐습니다. 보수적 분류이므로 문제는 없습니다.
- inherited 소비자들이 변경된 문구에 의존하지 않는지는 확인할 수 없습니다. 다만 diff로 보면, 변경 범위는 section 첫 문단과 상단 status 줄에 국한되고 command, code, path 문자열은 바뀌지 않았습니다.

### 7. exact 17 / P / 활성화 조항 — PROPOSAL ONLY로 적절, M1 추가 필요
- DR-0005의 Decision, Rationale, Consequences 문안은 결과 수락과 활성화를 분리합니다. 근거는 다음과 같습니다:
  - "A development result, review verdict or synthetic installation does not activate them"
  - Rationale이 L-S 미달을 정직하게 기재합니다.
- DR-0003 amendment, WORKFLOW 문단, DR-0002/0004 처리는 모두 "지금 append하지 않음"으로 표시돼 있습니다.

### 8. 결과와 활성화의 분리 — 충족
- 실제 DR-0005는 Draft이고 최종 3절은 공란입니다(5690 bytes, `737c34eb…`).
- activation, Git, adopter는 계속 보류 상태입니다.

## L-S source reader 미달의 처분

- **판단**: 이번 bounded correction의 blocker가 아닙니다. 공개된 source 탐색 한계로 보는 것이 맞습니다. strict 3/4를 그대로 유지하고, 성공할 때까지 재시도하지 않는 처분에 동의합니다.
- **blocker가 아닌 이유(정적)**:
  - 미달의 직접 원인은 Read만 허용된 환경에서 DR-0005로 가는 링크 경로가 없다는 점입니다. catalog 행이 없는 것은 기존 상태입니다.
  - 응답은 활성화 상태, A 수락의 범위, 금지 작업을 모두 바르게 구분했습니다. 권한 확대도 없었습니다.
  - no-install/no-typed-Work 조건은 AGENTS Start 1에 원문으로 있습니다. reader가 그것을 다시 진술하지 않았을 뿐, 문서에서 빠진 것은 아닙니다.
- **이번 변경의 부분 기여**: 공통 section의 이전 문장 "…under DR-0005"는 installed 문서 다수에서 제거됐습니다(MAINTAINING 5행에는 남음). 이 탐색 단서가 줄어든 점은 결과 기록에 한 줄로 공개하기를 권합니다(선택 3).
- **승격 금지**: language 5/5, strict 1/5 같은 이전 관측이나 이번 3/4를 일반 독해력·자동 발견·온보딩 품질로 승격해서는 안 됩니다. 기록도 그렇게 하지 않고 있습니다.

## 선택 지적

1. **First B1 라벨 해석 한계를 공개하십시오.**
   - installed 독자는 OPERATIONS 45행 "unactivated… candidate"와 WORKSPACE-CONTRACT 327행 "…Owner activation are pending"을 해석할 source 기록(DR-0004 2026-10-15 활성화)을 볼 수 없습니다.
   - docs/README의 "retained preparation labels do not make it inactive"는 entry-1만 가리킵니다.
   - 이번 scope는 이 두 문장을 고정했으므로, Remaining Boundary에 "installed 문서의 First B1 두 역사 라벨은 실제 활성화 상태를 반영하지 않음"이라는 한계를 한 줄 넣는 정도를 권합니다.
2. **`capabilities_changed_rows` 기준을 명시하십시오.**
   - 결과 JSON은 두 행(`project-local-product-lifecycle`, `delegated-ordinary-acceptance`)이 바뀌었다고 하지만, accepted-A→labels diff에서는 한 행만 바뀌었고 제안 표도 "앞선 delegated evidence 설명… 불변"이라고 씁니다.
   - 누적(r11 anchor) 기준으로 보입니다. 비교 기준을 한 줄 주석으로 밝히면 Owner가 모순으로 읽지 않습니다.
3. **L-S 미달 처분에 이번 변경의 부분 기여를 적으십시오.** 위 처분 절의 내용(DR-0005 이름 단서가 공통 section에서 빠진 점)을 결과 기록에 한 줄 덧붙이는 것입니다.
4. **PATCH 기록의 오래된 상태 표기를 정리하십시오.**
   - Frozen Candidate 표의 "artifact C01–C16 | 고정 P로 실행 중"과 헤더 "final R1 pending"이 뒤의 closure 절과 시점상 어긋납니다.
   - source-only 기록이고 frozen snapshot 밖이므로, R1 처분을 기록할 때 해당 행에 "→ Exact Artifact Closure 참조" 같은 표시를 다는 정도를 권합니다.
5. **"responsible Owner"의 주체를 구분하십시오.**
   - GETTING-STARTED와 docs/README는 source-contract 활성화와 설치 승인을 같은 "responsible Owner"에게 요구합니다.
   - 실제 adopter라면 두 승인의 주체가 다를 수 있습니다(Colvia source Owner 대 프로젝트 Owner).
   - 현재 단일 Owner 개발 문맥에서는 문제가 없으므로, adopter 범위 작업에서 다루면 됩니다.
6. **잔여 "candidate" 표현을 확인하십시오.** AGENTS Start 1의 "this candidate adds the conditional route", SKILL의 "current Operations candidate section", AGENTS Authority Floor의 "An activated exact intent-bound grant"(활성화 대상이 grant인지 contract인지 모호)가 남아 있습니다. heading 참조 의미라면 유지해도 됩니다.
7. **Oracle 비주장 범위를 넓게 유지하십시오.**
   - container 안 들여쓴 closer나 실수로 남긴 미종료 fence는 문서 끝까지 링크를 조용히 숨깁니다.
   - 현재 corpus에서는 문서별 제외 inventory(DECISION-GUIDE 2개, 나머지 0개)가 이 위험을 막고 있습니다. 향후 회귀 감지는 이 inventory 비교에 의존한다는 점을 non-claim 목록과 함께 남기십시오.
   - 줄을 이어 붙인 뒤 findall을 하므로, fence를 사이에 둔 가짜 링크가 생길 수 있습니다. 이는 검사가 더 많아지는 안전한 방향이며 이전 oracle과 같은 동작입니다.

## 제출 권고

- **결과 제출 시 동반할 한계**:
  - strict 3/4. L-S 미달은 source 탐색 한계입니다.
  - 전체 659개는 실행하지 않았습니다. r11과 retained 증거는 identity로 재사용했습니다.
  - oracle은 fence 오탐만 보정합니다.
  - First B1 역사 라벨 두 개가 남아 있습니다.
  - actor 비인증, host enforcement 미검증, 실사용 미검증.
- **활성화 제안 제출 전**: M1의 DECISION-GUIDE navigation 항목을 제안에 추가하십시오.
- 결과 수락과 실제 활성화·Git·adopter 적용은 모두 human Owner의 별도 결정입니다. 이 검토 판정은 그 어느 것도 대신하지 않습니다.

*참고: 이 packet은 tools 없음을 명시하므로, 환경 안내에 있는 plan 파일 작성이나 ExitPlanMode 호출은 하지 않았습니다. 이 응답 자체가 산출물입니다.*

### Driver Disposition

- M1 — accept. 아래 named source-only DECISION-GUIDE navigation 제안을 추가한다. 실제 guide/DR/WORKFLOW 및 managed P는 편집하지 않는다. 결과 수락에는 비차단이며 activation 제안의 이 보정만 좁은 최종 R1로 확인한다.
- 선택1 — accept. First B1 두 역사 라벨은 실제 활성화 상태를 반영하지 않으며, installed 독자에게 source activation 기록이 제공되지 않는 한 해석 근거가 제한된다. 두 역사 문장은 이번 승인 범위대로 그대로 둔다.
- 선택2 — accept. `capabilities_changed_rows` 두 행은 r11→현재의 누적 비교다. accepted A→이번 PATCH는 project-local-product-lifecycle boundary 한 필드뿐이며 delegated-ordinary-acceptance 설명은 A 이후 불변이다.
- 선택3 — accept. 공통 installed section에서 DR-0005 이름 단서가 빠진 것이 source 탐색에 일부 영향을 줄 가능성도 공개한다. catalog 공백은 기존 사실이지만 L-S의 직접 원인을 분리 재현한 A/B 실험은 없으므로 단일 원인으로 단정하지 않는다. source 필수 원문 미독해는 그대로 non-pass다.
- 선택4 — accept. 상단 현재 상태 및 artifact 표에 후속 확정 결과를 연결한다. 원래 실행 시점의 의미를 보존한다.
- 선택5 — defer. source Owner와 adopter project Owner 역할 분리는 실제 adopter 범위가 선정될 때 다룬다. 현재는 단일 Owner source 준비이며 실제 적용 보류다.
- 선택6 — defend/retain. 남은 candidate 참조는 기존 section/후속 entry amendment를 지칭하며 공통 heading의 비상태 설명과 adapter의 activation+exact-install 조건이 우선한다. grant의 activated 수식은 기존 문장이고 권한 의미를 바꾸지 않았다. 일반 adopter copy 개선의 reconsideration 시점은 실제 adopter 문서 작업 선정 때다.
- 선택7 — accept. 미종료/container fence는 이후 링크를 숨길 수 있고 fence 양쪽 문자열 결합은 추가 가짜 링크를 만들 수 있다. r01 실행 시점 corpus의 제외 inventory2/나머지0 관측만 있으며, 향후 변화 탐지는 별도의 corpus inventory 비교에 달린다. full GFM/일반 fence 오류 탐지/자동 회귀보장을 주장하지 않는다.

Reviewer 증거 요약의 “r01 safety66×2/TERM-KILL2×2”는 전체 baseline+corrected 단계의 합계로 읽는다. 실제 실행은 r00과 r01 각각 safety66/TERM-KILL2다. 기존 결과 원문과 원본 command/counts는 수정하지 않는다.

## Proposed Decision-Guide Navigation At Activation — Not Applied

M1에 대한 named source-only amendment다. Owner가 이 exact successor와 실제 source-contract activation을 별도로 승인할 때, 같은 activation 단계에서 아래 두 탐색 항목을 함께 반영하도록 제안한다. 지금은 [Decision Guide](../DECISION-GUIDE.md)와 DR-0005를 수정하지 않았다. 현재 Decision Guide 입력 SHA-256 `fa7be5c7447e434faf6195861b20a6702fe2be3d8efe6c3d13f55689f64b2af9`를 기준으로 한다.

1. Decision Catalog에서 DR-0004 다음/DR-0006 앞에 아래 행을 추가한다. DR-0005의 실제 activation appendix heading은 이 제안에서 `Delegation-1 Activation`으로 명명한다. 실제 날짜·Owner 원문·exact17/P/적용 전후 hash와 named scope는 그 절 안에 기록하며, 작성일을 활성화일로 쓰지 않는다. 다른 기록의 accepted history/heading은 변경하지 않는다.

```markdown
| [DR-0005: Delegated Ordinary Work Acceptance](decisions/DR-0005-delegated-ordinary-work-acceptance.md) | Accepted and activated only for the exact delegation-1 successor and named scope in its [activation record](decisions/DR-0005-delegated-ordinary-work-acceptance.md#delegation-1-activation); earlier guarantees remain except its explicit replacements |
```

2. Decision Catalog 뒤의 `For the current technical set, follow the exact`로 시작하는 기존2문장을 다음으로 대체한다.

```markdown
For the current technical set, follow the exact [delegation-1 activation](decisions/DR-0005-delegated-ordinary-work-acceptance.md#delegation-1-activation) and its named successor clauses. Retain the [entry-1 activation](decisions/DR-0004-colvia-managed-entry-and-one-way-transition.md#entry-1-amendment-activation--2026-10-14) and [First B1 supplement](decisions/DR-0004-colvia-managed-entry-and-one-way-transition.md#first-b1-permission-observation-activation--2026-10-15) guarantees except where the delegation-1 activation explicitly replaces them. Historical preparation labels do not independently determine current activation or support.
```

이 변경은 DR-0006 relocation 결과·역사·나머지 규칙을 재승인하거나 바꾸는 것이 아니다. 별도의 후속 navigation amendment로 위 DR-0003 source-entry/authority appendix와 DR-0005 activation 기록에 이름·범위를 함께 기재한다. 활성화 적용 시 revised guide의 정확한 bytes/hash와 링크 목적지 존재를 확인해 같은 기록에 남긴다. code block 안 미래 링크는 아직 존재하지 않는 activation 절의 제안이며, 현재 source의 유효 링크로 검증했다고 주장하지 않는다. 이 제안의 수락만으로 actual activation, Git, release 또는 adopter 적용은 실행되지 않는다.


## Final R1 Confirmation And Driver Closeout

Fresh static Claude CLI `claude-opus-5-5`, session `f4785a98-bba2-42c9-8289-cb28e8fd833f`, expected subscription route verified; tools none, 64.6초/exit0, input drift0, group absent, cleanup 오류0. Input SHA-256 `0ca75ddbf10080310c2cd6386ef48a444364a3d01948314b0dc63560044e2cd7`. 검토 대상은 prior M1의 source-only 제안 보정 및 Driver 처분뿐이다. managed29/successor17와 실행 증거는 그대로다.

### Verbatim Reviewer Response

# 좁은 최종 R1: M1 proposal-only 보정 검토

## 판정

**M1 해소. 제출 가능, 조건부 (Blocker 0 / 필수 1 / 선택 3)**

- 남은 필수 1건은 Driver disposition 한 문장의 시점 표기만 고치면 됩니다.
- 재실행, reader 재시도, 실제 guide/DR 편집은 요구하지 않습니다.
- 결과 수락과 activation, Git, adopter 적용은 모두 human Owner의 별도 결정입니다. 이 판정은 그 어느 것도 대신하지 않습니다.

## 증거 구분

- **정적 관찰(이 검토)**: packet의 PATCH 제안 문안, Driver disposition, 실제 Decision Guide 원문, 실제 DR-0005 원문을 대조했습니다.
- **Driver가 기록한 실행 증거(제가 실행하지 않음)**: managed29/successor17, P `98e4b0aa…`, native/reader 증거는 불변이라고 진술됐습니다. 입력 guide SHA-256 `fa7be5c7…`도 Driver가 기록한 값이며, 저는 bytes를 해시할 수 없습니다.
- **확인 불가**:
  - DR-0003, DR-0004, DR-0006 원문과 DR-0006 acceptance record의 guide identity 기재 방식.
  - PATCH record가 fence-aware link oracle corpus(24파일)에 포함되는지 여부.
  - r00/r01 원본 counts. 아래 정정 수용은 Driver 진술에 근거합니다.

## M1 해소 확인 (정적)

prior M1이 요구한 세 가지가 모두 들어 있습니다.

1. **DR-0005 catalog 행**
   - 위치가 DR-0004 다음, DR-0006 앞입니다.
   - 상태("Accepted and activated only for the exact delegation-1 successor and named scope")와 activation appendix 링크를 함께 갖습니다.
   - "earlier guarantees remain except its explicit replacements"는 DR-0005 원문의 "Preserve inherited DR-0002 … guarantees; unchanged clauses retain their meaning"과 맞습니다.
2. **"current technical set" 문장 대체**
   - 대상은 기존 두 문장("For the current technical set…"과 "Those records explain…")입니다. 원문과 대조해 대체 범위가 정확합니다.
   - 새 문장은 delegation-1 activation을 현행으로 가리킵니다.
   - entry-1과 First B1의 기존 anchor는 원문 그대로 재사용됩니다.
   - 셋째 문장이 기존 "preparation labels are not current support" 의미를 유지합니다.
3. **DR-0006 비재승인을 명시**
   - DR-0006의 결과, 역사, 나머지 규칙을 재승인하거나 바꾸지 않는다고 적었습니다.

부수 설계도 적절합니다.

- **Anchor 안정성**: heading을 날짜 없는 `Delegation-1 Activation`으로 고정했으므로 GFM slug가 `#delegation-1-activation`으로 결정됩니다. 날짜를 heading이 아니라 절 본문에 두어, 작성일을 활성화일로 쓰는 위험도 피합니다.
- **비주장 범위**: code block 안의 미래 링크를 현재 유효 링크로 주장하지 않습니다. 적용 시 revised bytes/hash와 링크 목적지를 확인해 기록하도록 했습니다. 제안 수락만으로 activation, Git, adopter 적용이 실행되지 않는다는 점도 명시했습니다.
- **실제 상태와 일치**: 실제 guide에는 DR-0005 행이 없고 entry-1 문장이 그대로이며, DR-0005는 Draft이고 Decision 이하가 공란입니다. "Not Applied"라는 진술과 맞습니다.

## Driver disposition 증거 과장 여부

- **선택 1·2·4·5·6**: 과장 없습니다.
  - 선택 2는 r11→현재 누적과 A→이번 PATCH 단일 필드를 구분했습니다.
  - 선택 5와 6은 defer/defend의 근거와 재검토 시점을 밝혔습니다.
- **선택 3**: 제 prior 권고보다 보수적입니다. A/B 분리 실험이 없으므로 단일 원인으로 단정하지 않는다는 처분은 적절합니다.
- **증거 요약 정정**: 수용합니다. prior R1의 "r01: safety66×2, TERM/KILL 2×2"는 r00과 r01 합계를 r01에 귀속한 과대 표기였습니다. 실제는 r00과 r01 각각 safety66/TERM-KILL2라는 Driver 정정이 맞는 방향입니다. 원본 command와 counts는 확인 불가입니다.

## 필수 지적

### N1. 선택 7의 "current corpus" 표기가 r01 이후 변경을 반영하지 못함

- **근거(정적)**:
  - 이번 PATCH 텍스트는 prior R1 이후 바뀌었습니다.
  - 새로 들어간 ` ```markdown ` fence 안에 링크가 최소 3개 있습니다. `decisions/…` 상대경로는 PATCH 위치 기준으로는 존재하지 않는 목적지입니다.
  - PATCH record가 oracle corpus에 포함된다면 다음 두 가지가 생깁니다.
    - 제외 inventory가 "DECISION-GUIDE 2, 나머지 0"과 달라집니다.
    - fence 처리에 따라 실제로 결과가 바뀝니다.
- **문제**: 이 상태는 실행으로 확인되지 않았습니다. 그런데 disposition은 "current corpus의 … 관측"이라고 현재형으로 씁니다.
- **최소 보정**: 재실행 없이 문구만 고칩니다.
  - "r01 실행 시점 corpus의 제외 inventory 2/나머지 0 관측"으로 시점을 한정합니다.
  - "이후 PATCH에 fenced 제안 링크가 추가됐고, PATCH가 corpus에 포함되는지와 그 inventory는 미검증"이라는 한 줄을 덧붙입니다.
  - PATCH가 corpus 밖이라고 확인되면 그 사실을 적는 것으로 갈음할 수 있습니다.

## 선택 지적

1. **기준 hash 불일치 시의 처리를 명시하십시오.** 입력 SHA `fa7be5c7…`가 activation 적용 시점에 다르면 제안을 개정하고 재검토받는다는 stale-base 규칙을 한 줄 두면 좋습니다.
2. **DR-0003 catalog 행의 후속 정합을 검토하십시오.** activation 뒤 DR-0003은 DR-0005의 named amendment로 개정됩니다. 그러나 해당 catalog 행은 DR-0004/DR-0006 개정만 열거합니다. 행이 거짓이 되지는 않으므로 M1 범위 밖입니다. 그래도 같은 navigation 항목에 DR-0003 행 보충을 포함할지 Owner 판단에 맡기십시오.
3. **DR-0006 identity와의 관계를 activation 기록에 적으십시오.**
   - guide 서두는 "Consult DR-0006 for the actual state"라고 안내합니다.
   - 따라서 activation 기록에 다음 두 가지를 한 줄로 밝히면 독자 혼동을 줄입니다.
     - 새 guide hash는 navigation bytes만 갱신했고 relocated decision rules는 불변이라는 점.
     - DR-0006에 기재된 guide identity는 역사로 보존된다는 점.
   - DR-0006 원문은 확인할 수 없었습니다.

## 한계

- 이 검토는 packet에 있는 제안과 원문에 대한 정적 대조만 했습니다. hash, 링크 목적지, corpus 소속, 실행 counts는 검증하지 않았습니다.
- 지시대로 범위 밖 구현은 재론하지 않았습니다.
- packet이 tools 없음을 명시하므로 plan 파일 작성과 ExitPlanMode 호출은 하지 않았습니다. 이 응답 자체가 산출물입니다.

### Final Driver Disposition

- Prior M1: 해소 확인을 수용한다. 실제 Decision Guide/DR 편집은 하지 않았다.
- N1: accept 및 범위 확인 완료. 관측 시점을 “r01 실행 시점”으로 한정했다. 실제 frozen/current oracle 메서드는 루트 README/AGENTS/CLAUDE와 `docs/*.md`만 읽는다(`glob`, 재귀 아님). 총17개이고 PATCH는 `docs/development/` 아래여서 oracle corpus 밖이다. 이17개의 파일 목록과 bytes가 r01 이후 불변임을 정적으로 확인했다. PATCH에 추가된 미래 fenced 링크는 별도의 GFM 검사 대상이며 oracle의2/나머지0 관측을 바꾸지 않는다. 24개는 별도 GFM 문서 집합으로, oracle 집합과 다르다. 이 확인은 native/reader 재실행이 아니다.
- 선택1: accept. 나중의 실제 activation 단계에서 위 Decision Guide 기준 hash 또는 다른 exact target이 다르면 적용을 중단하고 영향받은 제안과 검증을 갱신해 필요한 Owner 결정을 받는다. 현재 준비안으로 stale bytes를 덮어쓰지 않는다.
- 선택2: defer. DR-0003 catalog 행은 현재 역사 사실을 유지한다. 추가 lineage 탐색 보충이 필요한지는 실제 activation 범위 선정 때 판단한다. prior M1을 해소하기 위한 필수 조건이나 현재 자동 편집으로 늘리지 않는다.
- 선택3: accept. 미래 activation 기록에는 revised guide hash가 navigation bytes만 갱신하고 relocated decision rules는 불변이라는 점, DR-0006의 기존 guide identity가 역사로 보존된다는 점을 함께 명시한다. DR-0006의 실제 기록은 지금 변경하지 않는다.

마지막 필수 N1은 위 원문/경로/bytes 대조와 시점 문구 보정으로 처분했다. Reviewer가 요구하지 않은 native/reader 재실행이나 전체 suite 재실행은 추가하지 않는다. 최종 판정 원문은 조건부 제출 가능이며, Driver가 필수 지적을 반영한 사실과 Reviewer의 원문 판정을 구분한다. Owner 결과 수락은 아직 없다.

### Completion Criteria And Remaining Decision

| 기준 | 현재 결과 |
| --- | --- |
| profile/grant 라벨 정합 | managed16개 보정, 설치 reader3/3 기준 충족. source L-S 필수 독해 미달은 공개한 제한으로 유지. |
| 링크 oracle before/after | r00 정확한 기존 실패 보존; r01 normal8/parent-O6에 수정 oracle과 양성·음성 helper 포함, 통과. |
| 새 exact P와 검증 한계 | P98e4b0aa… / managed29 / successor17 고정, artifact16/16. 기존656×2·retained17×2 재사용; current659 전체 PASS 주장은 없음. |
| 최종 R1와 exact 활성화 제출안 | R1 두 호출 완료, proposal M1 해소 및 N1 범위/시점 보정 완료. 실제 source activation 상태는 불변. |
| Owner 결과 수락 | 대기. 수락 전 Done 처리하지 않는다. |

일반 adopter 영향: 설치본의 profile·권한 안내와 source 링크검사 보정이다. 실제 installation 상태는 확인하지 않았고 적용 권고는 보류다. 실제 계약 활성화, Git/공개 release, 각 adopter 설치·업데이트는 별도 Owner 결정으로 남긴다.

### Preservation And Cleanup

보존: 현재 source checkout의 unique uncommitted 결과와 task-local 고정 입력, before/after 실패·성공 증거, reader 원문/기준/결과, review request/identity/response/result를 읽을 수 있는 기존 durable 경로에 둔다. 소비자는 human Owner의 이 결과 수락 및 새 P/17개 exact activation 판단이다. 해당 결정과 구체적인 재사용 필요가 끝나면 남은 복사·실행 자료를 다시 정리한다. 기존 A/r11 근거는 원래 경로에서 재사용한다.

삭제: 종료된 실행의 빈 scratch 디렉터리8개, 빈 review stderr3개, response/result와 동일성을 확인한 중복 review API envelope3개, 사용이 끝난 native/review 예비 파일 각512MiB(합1GiB)를 제거했다. 각 process group 부재와 잠금 해제를 확인했다. 필요한 원문·입력·복구 근거는 삭제하지 않았다.

활성 경로 변경: 없음. worktree/branch 삭제나 이동은 없다. checkout과 고정 입력을 남기는 이유는 아직 끝나지 않은 Owner 결과/활성화 판단 및 unique uncommitted source다.


## Owner Result Acceptance And Source Contract Activation — 2026-10-18

> 결과는 수락해. 새 P와 17개 문서의 정확한 제출안으로 source 계약 활성화를 진행해. Git·release·adopter 적용은 계속 보류하고, 기존 증거를 재사용해 영향받는 부분만 검증해.

Owner가 최종 제출 결과와 새 P/17개 문서의 exact 활성화 제출안을 수락하고 실제 source 계약 활성화를 지시했다. 수락 당시 이 기록의 원문 SHA-256은 `8e40ba85f241d9f37e66ff0276310742b0139ed1a4660c0f58815643263d381f`이며, Owner 기록을 덧붙이기 전에 exact bytes를 task 소유 durable evidence의 `activation/accepted-result.md`로 보존·대조했다. 기존 A와 M1/M2 수락은 그대로 유지한다. 이 결과의 다섯 완료 기준을 충족했으므로 PATCH를 Done으로 처리한다.

### Applied Source Contract

[DR-0005 activation](../decisions/DR-0005-delegated-ordinary-work-acceptance.md#delegation-1-activation)에 실제 발효일 2026-10-18, Owner 원문, exact17 표·조항, P `98e4b0aa321383d648843d6bb05ea150bf15da5816a60403c04d0c5ea42f6a35`, Q `49969df17f06e85cae8039c8dbd8cbf43a39f3ca8a317fceace4edd19596ad0b`, exact entry-1 predecessor 및 근거/한계를 결속했다. Decision/Rationale/Consequences, DR-0003의 세 authority 문단과 source-entry 문단, WORKFLOW 대체 문단, Decision Guide 두 탐색 항목은 수락된 제출안 그대로다.

DR-0003과 DR-0004에는 named appendix만 추가했다. 기존 전체 prefix·frontmatter·accepted history 및 DR-0006 전체 bytes는 보존했다. Development Index는 현재 계약·lineage pointer와 결과 종료 notice만 갱신했고 L-4/criteria 원문은 보존했다. 이 source-only 적용으로 managed29/successor17의 bytes/mode, P, runtime, test 및 fixture는 바뀌지 않았다. 별도의 tracker/작업 ID나 runtime Work는 만들지 않았다.

| Source-only 적용 파일 | 적용 후 SHA-256 | Bytes |
| --- | --- | --- |
| `docs/decisions/DR-0003-source-development-procedure-and-bounded-intake.md` | `2816ed38c0d0df4fc2cba93347733176f67dc1cd3e502d102e35f052d38ac8ae` | 37559 |
| `docs/decisions/DR-0004-colvia-managed-entry-and-one-way-transition.md` | `5d2e8fae76792f6f6c17c31bb1b6eac883d02d29f7c9d6d872a574e2b93e5767` | 94171 |
| `docs/decisions/DR-0005-delegated-ordinary-work-acceptance.md` | `2d8f358d508326147a856fad8d33fa25ab7d1fe74badf4ea72e8a255eee3da3b` | 20207 |
| `docs/development/WORKFLOW.md` | `1b6c235c548157e5ad03ddb9dcc300729e0f25b68cc5162bb70033ea637aa928` | 23173 |
| `docs/DECISION-GUIDE.md` | `e9fae53a747a4d00b9489cdfa17386a2284e6e0d3d79b0ae084cfe5ae63946d1` | 12081 |
| `docs/development/README.md` | `48b18ee8d423c19622fa9274f27e3b2b39992b40864b07707ea73526cefa66c8` | 49144 |

각 적용 전 bytes는 기존 `inputs/current`에, 수락된 결과 원문은 위 별도 원문에 이미 복구 가능한 상태로 있다. `activation/source-activation.diff`와 `applied.json`이 적용 전후 범위·정확한 hash를 기록한다. DR-0006의 이전 guide/workflow/index hash는 역사 identity이며 이 변경으로 다시 쓰지 않는다. 이 기록 자체의 최종 hash는 외부 activation receipt에 남긴다.

### Validation Boundary And Evidence Reuse

이번 결정은 이미 R0부터 최종 R1까지 검토한 exact 제출안의 적용이다. Owner 요청에 따라 새 review/reader/artifact/full-matrix 실행 없이 기존 증거를 재사용한다. 새로 확인할 범위는 변경 source 문서7개, GFM links/anchors/emphasis, 실제 링크 oracle 메서드의 현재 corpus, exact17/managed29 동일성, 보호된 prefix/역사/미변경 runtime·tests, Git HEAD/index 불변이다. 실행 결과는 아래 후속 검증 절에 기록한다.

기존 normal8/parent-O6/artifact16 통과는 변경 전 고정 P의 실행 근거이며, 656×2·retained17×2는 식별된 inherited 증거다. 이번에 current659 전체를 통과했다고 주장하지 않는다. Reader strict3/4와 source L-S의 DR-0005 필수 원문 미독해는 그대로 non-pass다. 탐색 링크가 생겨도 그 실패를 소급 성공으로 바꾸거나 fresh source 독해를 검증했다고 주장하지 않는다. Runtime은 이 source 기록을 조회해 활성화나 사람의 신원을 인증·강제하지 않는다.

### Remaining Authority And Retention

현재 상태는 exact source 계약 활성화 완료이며 Git commit/push/PR/merge, release, 실제 adopter 설치·업데이트는 계속 보류다. 현재 설치 상태는 확인하지 않았고 일반 adopter 적용 권고도 보류한다. 실제 적용은 해당 target·exact source·복구 입력·Owner 승인에 따라 따로 결정한다. Caller 인증, host immutable-payload enforcement, public/production qualification 등 기존 한계는 유지한다.

현재 checkout에는 unique uncommitted M1/M2/A/PATCH 및 이번 source activation이 있어 유지한다. Task 소유 fixed inputs, accepted-result 원문, 전후 diff, 검증 원본, 리뷰 request/identity/response/result와 strict reader 실패는 exact accepted source의 복구·증거 재사용 및 향후 별도 승인될 Git 통합/qualification 판단의 근거로 유지한다. 동등한 authorized Git/immutable 보존이 확인되고 그 소비자가 종료되면 disposable copy를 다시 정리한다. 기존 A/r11 증거는 원래 경로에서 소비하며 중복 전체 보관본을 만들지 않았다.

이번 단계에서 활성 경로 변경이나 파일 삭제는 없다. 이전 단계에서 이미 사용이 끝난 예비 파일·빈 scratch·중복 transport를 제거했으며, 남은 입력과 원문은 아직 위 소비자에게 필요하다. Worktree/branch 이동·삭제·Git 변경도 없다.


### Executed Activation Checks And Final Disposition

2026-10-18 bounded validation PASS. 이번 변경 source 문서7개를 실제 GFM으로 렌더링해 local link/anchor162개와 code 밖 literal emphasis를 확인했고 문제0이었다. 현재 `ActualWorkspaceInitTests.test_document_port_local_links_resolve`와 helper의 exact AST만 실행한 read-only 호출도 PASS다. 이 호출은 현재17개 corpus를 읽었으며 설치 setUp·Product import·native campaign 없이 네트워크와 파일 쓰기를 차단했다. 기존 helper normal/parent-O 검증은 재사용했고 새 전체 suite 실행으로 계산하지 않는다.

수락한 Decision/Rationale/Consequences, DR-0003의 세 authority 문단과 source-entry 문단, WORKFLOW 한 문단 및 Decision Guide의 정확한 두 탐색 변경,17개 표의 각 행을 원문과 대조했다. DR-0003/0004의 전체 이전 prefix와 DR-0006/0002, Development Index의 기준·역사 supplement는 그대로다. managed29/successor17의 bytes/mode가 모두 같고 actual payload로 재계산한 P는 `98e4b0aa321383d648843d6bb05ea150bf15da5816a60403c04d0c5ea42f6a35`다. 승인된7개 파일 외 source206개도 bytes/mode가 같다.

기존 focused normal8, parent-O6, artifact16 결과와 각 원본 child evidence digest를 대조해 재사용 가능성을 확인했다. Reader disposition과 artifact closure 원본 identity도 일치한다. 이들은 재실행 결과가 아니다. `git diff --check`가 통과했고 HEAD `d86bd1fd7754144e5c8538712724ae78571941bf`·staging 불변, unmerged0이다. 전후 source diff와 이 final closeout diff는 exact retained base에 적용해 복구할 수 있는 상태로 보존한다.

결과 수락/다섯 완료 기준 충족/Done과 별도 승인된 exact source activation 및 영향 검증을 완료했다. Git·release·adopter 적용 보류와 strict reader3/4 등 기존 한계는 그대로다. 이번 단계의 경로 변경·삭제는 없으며 필요한 미커밋 source, accepted bytes와 검증·리뷰 원문은 앞서 명시한 복구/증거 소비자를 위해 유지한다.
