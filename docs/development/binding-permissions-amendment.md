# First B1 Permission Observation Amendment

## Current Reading Guide

The permission observation supplement is accepted and effective under [DR-0004](../decisions/DR-0004-colvia-managed-entry-and-one-way-transition.md#first-b1-permission-observation-activation--2026-10-15). Read [Technical Closeout](#technical-closeout--2026-10-16) for the current English summary of the correction, accepted evidence and remaining limits.

The preparation and acceptance records below retain their original English and Korean text. Their Proposed/unactivated labels describe the preparation revision; the named activation record determines the current effect. The preserved text is historical evidence, not a second current status.

## Preserved Preparation And Acceptance Record

Status: Proposed; implementation and bounded diagnosis authorized on 2026-10-15. Contract activation and release qualification are not authorized.

This proposes the observation-only supplement to DR-0004 C0-M and the S6/wrong-mode paragraphs of WORKSPACE-CONTRACT. Initial B1 and binding.next publication remain 0600, with unchanged exclusive publication, one-link/type/bytes checks and synchronization. An exact complete current first-transition B1 may also be read at 0644. No chmod, completion marker, broad permission mask or new schema/window is introduced. Other modes, residual binding.next and launcher modes other than 0755 remain refused.

Old entry-1 readers retain their first-B1 0600 requirement. A 0644 old installation therefore needs the separately qualified independent new source for an authorized update. Same-entry B2/B3 and typed local/worker/parent/planning record meaning retain their existing contract. Recovery repeats current-B1 sync; historical replay cannot synchronize a newer binding.

The accepted DR-0004 record, C0-M publication requirement and historical activation hashes are preserved. WORKSPACE-CONTRACT and OPERATIONS describe an unactivated candidate. This source-only proposal is outside managed29. Exact successor hashes, completion/qualification evidence and Owner activation remain separate decisions. The existing binding-permissions-r0-plan.md task record owns implementation, limited execution, review and residual work; this proposal is not an execution authorization.

## Adjusted Verification Scope

2026-10-15 Owner가 sandbox 정책을 유지한 검증 범위 조정을 승인했다. 일반 권한0600/0644의 허용과0640/0664/0666/0700의 거부는 실제 파일로 검사한다. `test_completed_binding_mode_allowlist_ordinary_modes`와 `test_binding_mode_readers_never_chmod_ordinary_modes`는 이 실제 범위만 가진다.

두 테스트의04600/04644 실제 파일 subcase4개는 sandbox의 `file-write-setugid` 거부 때문에 unavailable이다. `test_completed_binding_mode_predicate_with_synthetic_metadata`는 실제 binding 파일을0600으로 유지하고 해당 inode의 lstat/fstat mode만 대체해 verifier의 판정 로직을 검사한다. 성공하더라도 특수 권한 파일의 실제 검사·설치 reader/CLI 실증을 통과한 것으로 세지 않는다.

조정된 집중 범위는 기존42개 중 두 ID를 위 일반 권한 ID로 대체하고 논리 단위검사1개를 더한43개다. 기존 PASS8개를 비용 보정 목적으로 반복하지 않고, 실행 가능한 미측정34개와 새 단위검사1개의 비용을 보정한다. 원래42개 전체 PASS, full suite, 최종 개발 수락, 계약 발효 또는 실제 대상 업데이트를 의미하지 않는다.

## Subsequent Verification Acceptance

위 Adjusted Verification Scope는 당시 sandbox 내부에서 특수 권한 파일을 생성할 수 없었던 시점의 범위 기록이다. 2026-10-15 Owner는 합성 시험 파일 준비만 sandbox 밖에서 수행하는 좁은 예외를 승인했다. 실제 검증은 기존 sandbox와 실행 상한 안에서 수행했으며, 실제04600/04644 파일에 대한 verifier 거부2개와 source/installed status·doctor·view 거부 및 파일 불변성2개, 총4개 하위 사례가 PASS했다. 이 실제 파일 검증 공백은 해소됐다. 논리 단위검사는 실제 파일 검증과 별도의 증거로 유지한다.

Owner는 재사용한 회귀·문서42개와 논리1개, 이번 실제 파일4개 하위 사례의 누적 검증 결과를 최종 수락했다. 전체42개를 다시 실행했거나47개 독립 test ID를 통과했다는 의미는 아니다. 이후 별도 비용 보정은 기본 절차로 삼지 않고, 유효한 완료 결과를 재사용하며 검증 실행 중 시간·자원을 측정한다. 상세 실행 증거와 수락은 기존 binding-permissions-r0-plan.md 작업 기록에 있다. 계약 발효·exact release qualification·실제 adopter update는 이 검증 결과 수락과 별도다.


## Activation Record — 2026-10-15

The Owner accepted the exact permission observation supplement under [DR-0004: First B1 Permission Observation Activation](../decisions/DR-0004-colvia-managed-entry-and-one-way-transition.md#first-b1-permission-observation-activation--2026-10-15). The preceding preparation text is preserved. The linked record owns the exact member hashes, current normative effect and evidence limits. This source-only appendix does not change managed29 bytes, qualify a public release or authorize an adopter update by itself.


## Technical Closeout — 2026-10-16

The correction allows a completed first-transition B1 to be read after Git checkout recreates it with unchanged bytes at mode 0644. The Owner accepted the implementation and bounded verification results on 2026-10-15, then separately activated the permission observation supplement. This section makes the completed correction's technical result readable in the source repository. It establishes no new contract or additional verification acceptance.

### Source Identity And Effect

| Item | Fixed Evidence |
| --- | --- |
| Implementation, tests and fixed controls merge | `43a10086f28da32097c7687b6bd74e58dd45abdf` |
| Activation record merge | `38eaeeccde5a8633febd413044c9e4835e368d74` |
| Inventory SHA-256 for the 29 managed files | `2216a2634eb3fa5d6a8bfa7c7d4847b29fb2443ba7b367156c15b15ddb5a17e0` |
| Current contract and exact member hashes | [DR-0004 permission observation activation](../decisions/DR-0004-colvia-managed-entry-and-one-way-transition.md#first-b1-permission-observation-activation--2026-10-15) |

The allowed modes are 0600 and 0644 for an exact completed current first-transition B1. Initial B1 and binding.next publication remain 0600, and readers do not chmod. Other modes, residual binding.next, type/link/bytes mismatches and launcher modes other than 0755 remain refused. Current-B1 synchronization, the prohibition on historical replay synchronizing a newer binding, same-entry B2/B3 and typed record meaning are unchanged.

### Accepted Evidence And Remaining Limits

- The Owner accepted the cumulative results of 42 regression/document cases, one separate logical predicate case and four actual 04600/04644 file subcases. This was neither a single rerun of all 42 cases nor a result for 47 independent test IDs. The earlier sandbox refusal to create special-mode files and the synthetic metadata check remain preserved; the later four actual-file subcases closed that observation gap.
- Four additional current-document A1 cases passed in separate executions of three and one. An independent copy of a private target completed L-to-Q update, installed status/doctor/view after the unchanged binding bytes were recreated at 0644, and Q-to-L rollback. The trial preserved eleven completed Work records, eleven intents, zero pending records and 461 protected entries. The copy trial itself did not change the actual installation.
- Actual target application used separate authorization for the exact target, candidate, recovery material and request/token, with its own result record. Private target identities, the original recovery copy and detailed execution/review originals remain in the existing operations records. This summary replaces neither those originals nor the execution evidence required for reuse.
- These results do not establish a complete normal/parent-optimized anchor for the current candidate, the full factory/C4/C5 matrix, another OS/runtime or public qualification. The parent-O/public condition, the historical detach failure whose cause remains unresolved and its investigation triggers, and C4/C5 reuse limits remain. Follow [Maintaining's verification and reuse criteria](../MAINTAINING.md#evidence-reuse-and-selection).

Development result acceptance, contract activation, Git integration and actual installation results each require their own evidence. They do not establish general release qualification or acceptance by every adopter. Adding this closeout record alone requires no installation update.

### Documentation Correction Authorization

On 2026-10-16, the Owner authorized this minimal technical closeout and its Development Index link while preserving the original text and evidence. The Owner explicitly replaced R0/R1 for this document correction only with source comparison, link, GFM rendering and diff checks. Code, contracts and verification scope remain unchanged; no new product tests or external Reviewer review are performed. Git commit/push/PR/merge and acceptance of this document correction remain separate.

The baseline is the activation merge revision above. The initial correction appended this section to the existing body and added only a navigation link in the Development Index. Earlier mentions of binding-permissions-r0-plan.md are historical references to the preserved detailed task original. That original is neither overwritten nor copied into public-intent source. New follow-up work must be selected separately under the existing development procedure.

The Owner subsequently authorized English current guidance and closeout prose in this document, with the original text and acceptance evidence preserved and the separate private operations documents remaining in Korean. The current reading guide identifies the preserved historical sections. The earlier Korean closeout draft remains recoverable outside this checkout; the source history and acceptance records retain their exact original bytes.

Document checks confirmed preservation of the original historical text and detailed task original, with changes limited to two source-only documents in the correction as a whole. Product code, tests and managed payload are unchanged. GFM rendering found no literal emphasis delimiters outside code; new link targets and anchors and `git diff --check` were checked. These are document check results, not rerun product tests or Owner acceptance of this document correction.
