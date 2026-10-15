# First B1 Permission Observation Amendment

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
