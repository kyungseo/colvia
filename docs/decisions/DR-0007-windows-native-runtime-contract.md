---
id: DR-0007
status: Accepted
date: 2026-10-17
---

# DR-0007: Windows Native Runtime Contract

Accepted contract revision: 0.10
Accepted: 2026-10-18 (KST)
Revised: 2026-10-18 (KST)
Track: Product
Source baseline: `a93f71c359c4f0a9d57fcfb50d5999160e870f77`
Progress owner: [CHORE-20261017-001](../development/CHORE-20261017-001-windows-utm-feasibility-probe.md)
Linked decisions: [DR-0002](DR-0002-checkout-1-contract-baseline.md), [DR-0003](DR-0003-source-development-procedure-and-bounded-intake.md), [DR-0004](DR-0004-colvia-managed-entry-and-one-way-transition.md)

## Question

B안을 유지하면서 Windows 11에서 파일 identity, 잠금, 발행·복구, mode와 native 진입을 어떤 계약으로 제공할 것인가? 현재 POSIX 동작을 그대로 흉내 내지 않으면서 기존 authority·exact recovery 의미를 보존할 최초 범위를 정한다.

## Reading And State

Owner는 2026-10-18 DR-0007 v0.10의 S1–S8과 A1–A15를 수락했다. B안과 공통 조건 중심 worker 지원을 유지하며, Windows 전용 새 inventory window의 fresh init과 같은 window 안의 lifecycle을 준비한다. inventory window는 함께 설치하고 읽고 쓰는 managed member와 record 호환 범위를 식별하는 단위다.

계약은 수락되었고 후속 구현·검증 계획을 준비했다. 제품 구현·추가 실험은 아직 승인되지 않았다. 현재 운영 기술 계약은 entry-1과 First B1이며, Windows의 통합 qualification·Owner 결과 수락·별도 activation과 formal admission은 남아 있다.

```text
v0.10 S1–S8·A1–A15 exact 계약 수락
  → 후속 계획 준비 → 계획 review·실행 승인
  → 통합 제품 qualification·결과 수락·별도 activation
  → live macOS Preview 이후 Windows 정식 admission
```

qualification은 특정 제품·환경에서의 검증이고, admission은 그 증거에 근거한 지원 수락이다. 아래 S1–S8·A1–A15와 기존 개정 이력은 검토된 bytes를 유지한다. 그 안의 Draft·권고·수락 전 표현은 검토 당시의 문안이며 현재 상태는 이 절과 다음 수락 기록을 따른다. 수락한 것은 v0.10의 단일 권고 계약 묶음이며 Options의 비채택 대안을 함께 수락한 것으로 해석하지 않는다.

## Owner Contract Acceptance — 2026-10-18

Owner의 요청은 다음과 같다.

> DR-0007 v0.10의 S1–S8과 A1–A15 계약을 수락할게. 수락 기록을 정리하고 후속 구현·검증 계획을 작성해줘. B안과 공통 조건 중심 worker 지원은 유지하고, 추가 실험이나 제품 구현은 아직 시작하지 마.

| 항목 | 수락 및 현재 상태 |
| --- | --- |
| 수락 대상 | DR-0007 v0.10, 177,174 bytes, SHA-256 `cd6f3bf06d842afb8f71aac98e95382acc04b4524ee54b80af179b11ad0c3add`의 S1–S8과 A1–A15; 그 본문이 참조하는 exact window/pair·worker·named amendment 의미 포함 |
| 검토 근거 | [R1-D10과 Driver 판단](../development/CHORE-20261017-001-windows-utm-feasibility-probe.md#r1-d10--draft-010-static-re-review--2026-10-18): 전체 approve, findings 없음. 정적 문서 검토이며 제품 검증이 아님 |
| 리뷰 응답 identity | 10,936 bytes, SHA-256 `a5e719d52df72969bb0d2e2f613a6e30c4647ffb11c8378e01013b36be867f77` |
| exact 내용 보존 | 기존 R1-D10 frozen packet에서 수락 당시 전체 v0.10 bytes를 복구할 수 있음. 이 파일의 현재 수락 metadata와 원 수락 대상 identity를 구별 |
| 적용 시점 | 후속 Windows 구현·검증의 확정 설계 기준으로 수락. 기존 설치물·runtime allowlist·normative 기술 문서의 activation은 아직 없음 |
| 이번 허용 작업 | 수락 기록·catalog/navigation 정렬과 [후속 구현·검증 계획](../development/windows-native-implementation-plan.md) 작성·문서 검증 |
| 남은 경계 | 실행 승인, 제품 qualification·결과 수락·별도 activation, live macOS Preview 이후 formal admission, Git/adopter action |

수락된 S1–S8과 A1–A15 본문은 변경하지 않는다. 이번 기록 추가는 새 v0.11 계약 제안이 아니다. 실제 기록 보존·문서 검증과 후속 계획의 identity는 [기존 진행 정본](../development/CHORE-20261017-001-windows-utm-feasibility-probe.md#owner-contract-acceptance-and-follow-up-plan--2026-10-18)에 남긴다.

## Authorization And Basis

2026-10-17 Owner는 “후속 리뷰와 네 판단을 반영해 미결 선택이 표시된 계약 초안을 작성해줘. 각 선택의 권고안과 근거도 함께 정리해. B안은 유지하고, 추가 실험이나 제품 구현은 아직 시작하지 마.”라고 요청했다. 문서 작성·정적 대조·문서 검증만 수행하며, 새 probe·제품 실행·reviewer 재호출·계약 발효·Git publication은 이번 작성 범위에 포함하지 않는다.

입력은 같은 source baseline의 [관측 결과](../development/CHORE-20261017-001-windows-utm-feasibility-probe.md#observations-and-r0-comparison), [R1-P01과 Driver 처분](../development/CHORE-20261017-001-windows-utm-feasibility-probe.md#cross-agent-review-and-discussion--r1-p01), [추가 정적 확인](../development/CHORE-20261017-001-windows-utm-feasibility-probe.md#additional-static-checks-by-driver)이다. R1-P01 응답 SHA-256은 `fbe384a05394c1f0eb6bccc0c70a2750136e28fc98b3af5d5fe70d2c0cb54066`이다. 원응답과 실행 증거는 기존 record에 보존하며 여기서는 계약 선택의 근거만 소비한다.

현재 유효 계약은 DR-0004의 entry-1 activation과 First B1 supplement를 포함한다. 남아 있는 candidate 표기를 미발효의 근거로 해석하지 않는다. 이 Draft의 신규 문안은 그 유효 계약을 아직 대체하지 않는다. baseline 이후 병렬 변경은 통합 전에 다시 비교해야 한다.

2026-10-18 (KST) Owner는 “리뷰 결과와 네 최종 권고를 반영해 DR-0007을 v0.2로 보완해줘. S6의 논리 mode 기본값과 최초 지원 제한도 명확히 적어줘. B안은 유지하고, 추가 실험이나 제품 구현은 아직 시작하지 마.”라고 요청했다. 이번 변경은 그 문서 보완과 정적·문서 검증에 한정한다.

v0.2는 [R1-D01과 Driver 처분](../development/CHORE-20261017-001-windows-utm-feasibility-probe.md#cross-agent-review-and-discussion--r1-d01), [S1–S8 최종 권고](../development/CHORE-20261017-001-windows-utm-feasibility-probe.md#final-driver-recommendations-for-s1s8), [Driver의 로컬 정적 대조](../development/CHORE-20261017-001-windows-utm-feasibility-probe.md#local-static-cross-checks-by-driver)를 추가 입력으로 사용했다. R1-D01 최종 응답 SHA-256은 `7af67b21922878134381c9a01d6e1374ba5cd4c674f417fcef3edb700e41c78b`이다. Reviewer는 source와 실험 원출력을 직접 읽지 않았으며, Driver의 정적 대조와 새 권고는 별도 판단이다.

v0.1의 28,302 bytes, SHA-256 `8053b06be2ec8d2c79cf74e20eae9aa56d5e7cb8cac8c7b97d2263e099ec194a`는 기존 frozen review packet에서 복구할 수 있다. 기존 리뷰 원문과 당시 판단은 진행 기록에 그대로 둔다.

2026-10-18 (KST) Owner는 “리뷰 결과와 네 권고를 반영해 DR-0007을 v0.3으로 보완해줘. worker mode 변경의 최초 지원 제한과 기존 계약·admission 기준에 미치는 영향도 명확히 적어줘. B안은 유지하고 추가 실험이나 제품 구현은 아직 시작하지 마.”라고 요청했다. 이번 개정은 이 문서 보완과 정적·문서 검증에 한정한다. 문안에 권고를 반영하는 승인과 그 계약을 수락·발효하는 결정은 구별한다.

추가 입력은 [R1-D02 재리뷰와 Driver 판단](../development/CHORE-20261017-001-windows-utm-feasibility-probe.md#r1-d02-draft-02-re-review-and-driver-judgment--2026-10-18)이다. Reviewer 최종 응답 SHA-256은 `5a96a66aacafd64228c604a64e2a2486da8375fb44b6ed845c3584d7e87e1ef5`이다. Reviewer는 v0.2 문서만 읽었으며 D02-D1은 이후 Driver의 로컬 source 대조에서 나온 정적 판단이다. v0.2의 45,332 bytes, SHA-256 `ebe30bbaeae01c58105a3439506a7ed5c1081a734da434a810cdad2bf4b294db`는 기존 R1-D02 frozen packet에서 복구할 수 있다.

2026-10-18 (KST) Owner는 “리뷰 결과와 네 권고를 반영해 DR-0007을 v0.4로 보완해줘. 삭제 관측·worker 공통 적용 조건과 관련 계약·admission의 정확한 개정 문안을 작성하고, 기존 binding/profile의 식별 충분성도 확인해줘. B안은 유지하고 추가 실험이나 제품 구현은 아직 시작하지 마.”라고 요청했다. 이번 개정은 지정 Draft와 기존 진행 기록, 필요한 정적·문서 검증에 한정한다.

추가 입력은 [R1-D03 재리뷰와 Driver 판단](../development/CHORE-20261017-001-windows-utm-feasibility-probe.md#r1-d03-draft-03-re-review-and-driver-judgment--2026-10-18)이다. Reviewer 최종 응답 SHA-256은 `759cb62596a5574c6e9d6c1bb8102d6cfc6d6d3d3c89871077a0927ef88b6877`이다. Reviewer는 v0.3만 읽었고 source·기존 계약 원문을 독립 확인하지 않았다. v0.3의 60,267 bytes, SHA-256 `4a6ec954a348133950bc6db42ee488dda434888ffc99206296d268594662e181`는 기존 R1-D03 frozen packet에서 복구할 수 있다.

2026-10-18 (KST) Owner는 “리뷰 결과와 네 권고를 반영해 DR-0007을 v0.5로 보완해줘. worker 지원은 공통 조건 중심으로 유지하고, 삭제 관측·detach 이후 식별·old writer 거절 실패 처분과 남은 exact 계약 문안을 구체화해줘. B안은 유지하고 추가 실험이나 제품 구현은 아직 시작하지 마.”라고 요청했다. 이번 변경은 지정 Draft, 기존 진행 기록과 정적·문서 검증에 한정한다.

입력은 [R1-D04와 Driver 처분](../development/CHORE-20261017-001-windows-utm-feasibility-probe.md#r1-d04-draft-04-re-review-and-driver-judgment--2026-10-18)이다. Reviewer 최종 응답 SHA-256은 `871e0d851ced07ffea01fa086fdf24e57623ea8926e7716fe1479cb6b9b59929`다. source의 init/detach 경로와 eligible worker 사례는 Driver의 별도 정적 대조이며 실행 재현이 아니다. v0.4의 85,672 bytes, SHA-256 `3901b4c5f6edbc21be065bf900e6ee7fbb610ba5bdf9dacb3d196ef49d2e62ff`는 기존 R1-D04 packet에서 복구할 수 있다.

2026-10-18 (KST) Owner는 “리뷰 결과와 네 권고를 반영해 DR-0007을 v0.6으로 보완해줘. old writer 거절 미확인 처분, detach4 제거 후 검증, A1–A15의 Windows 적용 범위와 exact repair mode 의미를 명확히 해줘. B안과 공통 조건 중심 worker 지원은 유지하고 추가 실험이나 제품 구현은 시작하지 마.”라고 요청했다. 이번 변경도 지정 Draft, 기존 진행 기록과 정적·문서 검증에 한정한다.

입력은 [R1-D05와 Driver 처분](../development/CHORE-20261017-001-windows-utm-feasibility-probe.md#r1-d05-draft-05-re-review-and-driver-judgment--2026-10-18) 및 그 안의 D05-D1이다. Reviewer 최종 응답 SHA-256은 `f7e54388cf3ed00ad4f58d2861580942f9579178b2da33283aaa24a702d5bac7`이다. Reviewer는 v0.5만 검토했으며 detach inventory·CLI·repair source의 확인은 Driver의 별도 정적 판단이다. v0.5의 122,770 bytes, SHA-256 `d5f407c0710f5d215a29c9851e67b85271b21def0e7dbc8716c208f18afcb7ee`는 R1-D05 frozen packet에서 복구할 수 있다. 새 Windows repair mode 의미는 여기서 제안하며 구현·실측한 사실로 표시하지 않는다.

2026-10-18 (KST) Owner는 “리뷰 결과와 네 권고를 반영해 DR-0007을 v0.7로 보완해줘. read-only 파일의 생성·교체·제거 정책과 NTFS mutation 검사 경계를 명확히 하고, repair 재시도와 새 preview의 구분, 남은 상태 문구·대응표도 정리해줘. B안과 공통 조건 중심 worker 지원은 유지하고 추가 실험이나 제품 구현은 시작하지 마.”라고 요청했다. 이 요청은 아래 문서 개정과 정적 정합성 검증을 승인한다. 신규 계약 수락·제품 구현·추가 실험·reviewer 호출은 포함하지 않는다.

입력은 [R1-D06 재리뷰와 Driver 처분](../development/CHORE-20261017-001-windows-utm-feasibility-probe.md#r1-d06-draft-06-re-review-and-driver-judgment--2026-10-18)이다. Reviewer 최종 응답 SHA-256은 `c1636bca4d96e3d37381db4b15ad0bfd930ac4510178a952df7630e7204edd13`이다. v0.6의 140,365 bytes, SHA-256 `8d595d93d57855903cf0ee28d13b94838a4d5679afb72a445fe7ea5bc7e767ef`는 해당 frozen packet에서 복구할 수 있다. 기존 리뷰 원문과 당시 처분은 수정하지 않는다.

2026-10-18 (KST) Owner는 “R1-D07과 네 판단을 반영해 DR-0007 v0.8로 보완해줘. A12 본문 위치, read-only가 남은 새 preview의 거절, 필수 flush 대상의 사전 검사 범위를 명확히 하고 관련 문구도 정렬해줘. 채택하지 않은 지적은 반영하지 말고, B안과 공통 조건 중심 worker 지원은 유지해. 추가 실험이나 제품 구현은 시작하지 마.”라고 요청했다. 이번 변경은 지정 Draft와 기존 진행 기록의 보완, 정적·문서 검증까지다. 계약 수락·제품 실행·추가 실험·reviewer 호출은 포함하지 않는다.

입력은 [R1-D07 재리뷰와 Driver 처분](../development/CHORE-20261017-001-windows-utm-feasibility-probe.md#r1-d07-draft-07-re-review-and-driver-judgment--2026-10-18)이다. Reviewer 최종 응답 SHA-256은 `0d1fc7e4200315058078351a6bbf421df0d9c7db7897da9bca0dc22bc0dfe44a`다. v0.7의 161,600 bytes, SHA-256 `3fc5737cc87fe7e07649d31e5298b7dde7598cff087980f0821ad5c4e4a75afe`는 R1-D07 frozen packet에서 복구할 수 있다. source와 공식 플랫폼 문서 대조는 Driver의 별도 정적 확인이며 새 실행 증거가 아니다. 이전 리뷰와 Owner 원문은 보존한다.

2026-10-18 (KST) Owner는 “R1-D08과 네 판단을 반영해 DR-0007을 v0.9로 보완해줘. 버전 표기와 A9/A12 후행 빈 줄을 정리하고, worker preflight 참조와 preview 조기 진단 설명도 최소 범위로 반영해줘. defend한 지적은 반영하지 말고, B안과 공통 조건 중심 worker 지원은 유지해. 추가 실험이나 제품 구현은 시작하지 마.”라고 요청했다. 이번 범위는 지정 Draft와 기존 진행 기록의 최소 문서 보완 및 정적·문서 검증이다. 계약 수락·제품 실행·추가 실험·reviewer 호출은 포함하지 않는다.

입력은 [R1-D08 재리뷰와 Driver 처분](../development/CHORE-20261017-001-windows-utm-feasibility-probe.md#r1-d08--draft-08-static-re-review--2026-10-18)이다. Reviewer 최종 응답 SHA-256은 `c6be232f058b76b0b5d27e15e1e725cc993565f8bbb6172635fa875b9e4bad7f`다. v0.8의 172,048 bytes, SHA-256 `c3a16bf378a02e56975f1665bcecaf9f6cc6e7a581ee160a65784322d8ee890d`는 R1-D08 frozen packet에서 복구할 수 있다. source 대조와 defend 처분은 Driver의 별도 정적 판단이며 Windows 실행 증거가 아니다. 이전 Owner 원문·리뷰·개정 이력은 보존한다.

2026-10-18 (KST) Owner는 “R1-D09과 네 판단을 반영해 DR-0007을 v0.10으로 보완해줘. 상태 문구 세 곳을 실제 리뷰 이력에 맞추고, 조기 진단을 fresh repair preview로 한정해 non-pass일 때 실행 request/token이 없음을 명시해줘. B안과 공통 조건 중심 worker 지원은 유지하고 추가 실험이나 제품 구현은 시작하지 마.”라고 요청했다. 이번 범위는 지정 Draft와 기존 진행 기록의 문서 보완 및 정적·문서 검증이다. 계약 수락·제품 실행·추가 실험·reviewer 호출은 포함하지 않는다.

입력은 [R1-D09 재리뷰와 Driver 처분](../development/CHORE-20261017-001-windows-utm-feasibility-probe.md#r1-d09--draft-09-static-re-review--2026-10-18)이다. Reviewer 최종 응답 SHA-256은 `444574d042968e3f3e5e34531cb07716b057fe8e6762a83fe1eea867eeef48ee`다. v0.9의 174,893 bytes, SHA-256 `fac6d6fd2b314403561c571d5620c9e9aba959bd40e1b23a062f9c378d690386`는 R1-D09 frozen packet에서 복구할 수 있다. Reviewer는 해당 Draft만 읽었으며 source·target 본문 대조는 Driver의 별도 정적 판단이다. 이전 Owner 원문·리뷰·개정 이력은 보존한다.

## Revision 0.2 Changes

| 리뷰 지적 | 반영한 계약 설명 |
| --- | --- |
| F1 · 의미와 메커니즘 | Owner가 고를 의미와 계획에서 정할 방법을 분리하고, 문서 준비와 제품 mutation의 순서를 구분 |
| F2 · fresh의 old-writer·교차 OS 노출 | fresh에도 old-writer 거절 확인이 필요함을 명시. 기존 macOS 기본 동작 유지 |
| F3 · blocking 취소 | 작업 진입 전 취소의 종료 상태와 scratch anchor 예외를 명시 |
| F4 · sync와 복구 | 기존 필수/허용 unavailable 차이, 실패 출력·디스크 상태, 재flush의 새 관측 의미를 구분 |
| F5 · native 진입 | 절대 Python 경로와 PowerShell 5.1 qualification 대상을 명시. 미검증 상태 유지 |
| F6 · ancestor 범위 | volume root부터 실제 검사 경로까지의 chain을 명시하고 기존 membership/ignore 범위 유지 |
| F7 · mode와 지원 제한 | 공개된 `100644` 논리 기본값, provenance, non-Git `100755` 의도의 최초 미지원, 기존 기록 보존 |
| F8 · exact retry | 기존 operation·request·token·candidate와 recover 조건 유지. 새 명령·단회 token 가정 없음 |

## Revision 0.3 Changes

v0.3은 [R1-D02의 7개 필수 지적과 4개 선택적 보완에 대한 Driver 처분](../development/CHORE-20261017-001-windows-utm-feasibility-probe.md#r1-d02-finding-dispositions), [추가 worker finding D02-D1](../development/CHORE-20261017-001-windows-utm-feasibility-probe.md#d02-d1-driver-finding--worker-mode-change-under-an-unchanged-index)을 반영한다. S6 안에 worker 적용 경계를 따로 두어 mode를 관측하는 규칙과 실제 결과를 적용할 수 있는 범위를 구별했다. 기존 heading과 S1의 B 문안은 유지한다.

| 입력 | 보완한 내용 |
| --- | --- |
| R2-F1 | 일반 snapshot의 index membership/mode와 working-tree bytes 분리. retained tree 검증은 기존 계약에 따름 |
| R2-F2 | Windows OS/runtime·window 적용 범위, macOS 기존 의미 유지, provenance 식별의 충분성 확인 |
| R2-F3 | unknown·unmerged·허용 외 index mode를 기본값으로 대체하지 않음 |
| R2-F4–F5 | 과거 100755 의미 보존, completed replay와 pending recovery 구분, 거절 단위는 기존 operation 전체 |
| R2-F6–F7 | permission만으로 구분 못 하는 발행 상태는 unknown; 관측마다 같은 정책 재평가; 원참조 기대값과 실제 관측 분리 |
| R2-P3-a–d | stat 근거의 관측 범위, 제품 입력과 Git 표현 구별, 관련 출력의 정책 일치, 재리뷰 상태 갱신 |
| D02-D1 | index 불변으로 post-mode를 독립 관측하지 못하는 worker 결과의 최초 적용 제한 및 발행 전 거절 |
| 기존 계약·admission 영향 | 변경을 제안하는 지원 범위와 유지할 무결성 의무를 named map 및 열 가지 기준에 대응 |

## Revision 0.4 Changes

| 입력 | 반영한 내용 |
| --- | --- |
| R3-F1 · Driver revise | index는 후보 membership과 tracked mode의 출처이며 실제 부재는 별도 관측. 현행 snapshot의 삭제 관측을 보존하고 alias/type/unknown을 삭제로 처리하지 않음 |
| R3-F2 · Driver revise | worker mode 적용의 공통 필요조건, 예시 집합과 criterion 5 검증 목록 정렬. 기존 baseline·retained-source·physical·whole-result 의무 유지 |
| R3-F3 · Driver accept | 정책상 최초 미지원, prepare 이후 drift/stale, 관측 불가 unknown을 구별 |
| R3-F4 · Driver revise | 기존 ordinary reject와 pending cancellation 구별. prepare 이후 drift의 발행 전 거절 검증 명시 |
| R3-F5 · Driver accept | R1-D03의 실제 판정과 v0.4 미리뷰·미수락 상태를 함께 표시 |
| Owner 요청 · exact amendment | Structure·General Work·Windows criteria 5/8의 삽입·교체 위치와 영어 본문을 작성. 현재 normative 파일은 수정하지 않음 |
| Owner 요청 · binding/profile 식별 | 기존 값은 Windows 정책 식별에 불충분. 기존 release/binding 구조를 이용하는 Windows 전용 successor와 실행 환경 재검증을 권고. 새 field/schema는 기본 채택하지 않음 |

## Revision 0.5 Changes

| 입력 | 반영한 내용 |
| --- | --- |
| D04-F1 · Driver revise | 비부재 관측은 affected operation의 non-pass이며 삭제 entry 생략으로 숨기지 않음. 실제 부재는 S3 경로·ancestor 검사와 함께 판정 |
| D04-F2/F8 · Owner 방향 | 지원은 공통 조건과 기존 모든 guard로 판정. 예시 목록은 닫지 않으며 index-only tracked add와 eligible untracked의 정적 사례·qualification 요구를 정렬 |
| D04-F3 · Driver revise | init plan/token의 기존 release/window 결속을 명시. `windows-1` profile·fresh 후보 선택과 paired detach schema 4의 정책 식별을 구체 후보로 제안 |
| D04-F4 · Driver revise | old writer가 실제 발행하면 qualification/activation 중단. 최소 유효 fence 또는 검증 가능한 비노출 근거를 처분하고, 새 persisted 의미는 수락 대상에 포함 |
| D04-F5 · Driver revise | 최초 native Windows 11 ARM64/ARM64·x64/x64 64-bit process 조합과 제외 조합을 제안. B 배정·미관측 표시·formal timing 유지 |
| D04-F6/F7 · Driver 처분 | Windows 한정 heading, operation이 Git을 변경하지 않는다는 표현, A3 용어·조항 참조·S1 동시 수락 정렬 |
| 남은 exact 문안 | A6–A15에 admission timing, path/lock/flush/publication/retry, lifecycle·detach4, membership/pairs, runtime, native entry, qualification·retained reading을 제시 |

`windows-1`, profile, 29-member 집합과 detach4는 이번 문서의 구체 제안이다. 사용 가능한 runtime 값이나 채택된 계약으로 표시하지 않는다. 새 detach version은 삭제 뒤에도 정책을 구별하기 위한 제안이며, 기존 detach1/2/3 기록을 다시 쓰지 않는다.

## Revision 0.6 Changes

| 입력 | 보완한 내용 |
| --- | --- |
| D05-F1 · Driver revise | 실제 노출된 known old writer의 거절이 미확인·실행 불가이면 qualification/activation을 닫지 않음. 유효 거절 또는 검증 가능한 비노출 처분이 필요하며 모든 역사적 writer 회수를 새 gate로 만들지 않음 |
| D05-F2 · Driver revise | 기존 path/digest/size 목록을 그대로 사용해 제거 전·후 검증을 구별. 29 paths는 release별 payload 집합이며 전체 removal 수가 아님. 제거된 bytes는 현재 재해시할 수 없음을 명시 |
| D05-F3/F4/F5/F6 · Driver accept | Workspace의 entry-1 profile·repair·planning, Structure의 Window·pair·repair, Reference의 current-source 문장을 Windows에 한해 명시적으로 한정. CRLF는 동일 증명 아래 확장, path clause와 index-only add의 실제 부재 조건을 정확히 참조 |
| D05-F7/F9 · Driver defend | detach4의 windows-1 전용 의미와 기존 detach `--profile`을 유지. repair에 새 profile option을 추가하지 않음 |
| D05-F8/F10 · Driver revise | Security의 runtime 범위를 정본으로 참조. 표준 사용자 검증 환경과 매 writer의 OS/process gate를 구별. 신규 windows-1 경로의 old-target 거절을 기존 entry-1 source의 소급 OS gate로 확대하지 않음 |
| D05-D1 · Driver 정적 finding | windows-1 repair1의 `FileObservation.mode`를 read-only 관측 0/1로 정의. before/after·backup·drift·recovery/replay 비교와 독립 발행 완료 의무를 명시하고 기존 POSIX 의미 보존 |

새 mode 의미는 기존 integer field의 Windows 한정 계약 변경안이다. 새 field나 repair schema를 자동 추가하지 않지만, windows-1 candidate 식별과 양방향 reader 검증을 포함해 exact 수락해야 한다.

## Revision 0.7 Changes

| 입력 | 보완한 내용 |
| --- | --- |
| D06-F1 · Driver revise | Windows writer의 새 파일은 read-only clear로 생성. 교체·제거할 기존 read-only 파일은 첫 durable publication 전 operation 전체를 거절. 관측 뒤 drift·부분 실패와 보존 의무는 유지 |
| D06-F1 · repair 구분 | 기존 request의 exact 재시도, 외부 backup evidence, 실제 product pending barrier, 별도 새 preview를 구별. 같은 요청이 drift로 거절되는 것을 모든 복구의 영구 교착으로 표현하지 않음 |
| D06-F2 · Driver revise | native local NTFS를 target·staging·lock/scratch·외부 backup 등 실제 mutation 경로의 검사 조건으로 명시. 표준 사용자 qualification 조건과 구별하고 `fixed` drive 제한은 추가하지 않음 |
| D06-F3/F4 · Driver accept | 현재 리뷰 상태를 R1-D06/v0.7로 바로잡고 첫 named map에 A14 Manual Operation target을 연결 |
| D06-F5/F6 · Driver revise | detach receipt에 내장된 complete plan으로 read-only 검증. 외부 original plan/token은 mutation recovery에서 확인. detach4를 모르는 reader의 결과는 해당 검증 증거로 인정하지 않음 |
| D06-F7/F8 · Driver revise | Windows literal/payload가 candidate 생성 전에 명시적으로 준비되어야 함을 고정. old-writer 처분 pointer와 S2의 추가 repair qualification을 기존 criterion 2 원문과 구별해 대응 |

이 개정의 read-only 사전 거절과 NTFS 검사 문안도 아직 Draft다. v0.6의 성공 미보장을 더 구체적인 최초 지원 제한으로 바꾸는 후보이며, 이미 채택된 정책이나 새 실행 결과로 표시하지 않는다.

## Revision 0.8 Changes

| 입력 | 보완한 내용 |
| --- | --- |
| D07-F1 · Driver accept | A12의 영어 단락을 exact amendment fence 안으로 이동. 코드 블록 밖의 의도된 본문이 적용 대상에서 빠지지 않도록 검증 |
| D07-F2 · Driver accept | 교체가 필요한 read-only 파일이 남으면 새 repair preview도 non-pass이며 실행 request/token이 없음을 명시. 원 flag가 복원돼도 원 retry의 모든 관측·backup·candidate·binding·prefix 조건을 재검증 |
| D07-F3 · Driver revise | 교체·제거 외에 operation의 필수 flush 때문에 write-capable open이 필요한 기존 파일을 전체 사전 검사 범위에 포함. 순수 읽기·보존 파일과 구별하고 필수 동기화는 생략하지 않음 |
| D07-F4/F7 · Driver accept | read/preserve 면제가 repair의 bound 관측을 면제하지 않음을 명시. native local NTFS 지원 경계와 standard-user qualification 문장을 정렬 |
| D07-F5/F6 · Driver defend | 파일 READONLY를 디렉터리 거절 조건으로 추가하지 않고, external repair backup/receipt의 위치와 pending authority 밖 의미를 유지 |

필수 flush 사전 검사 범위도 이번 Draft의 exact 수락 후보다. 디렉터리 권한 검사, 기존 필수/허용 unavailable 동기화 의무, B와 worker 공통 조건은 바꾸지 않는다. v0.7의 in-memory 문서 검증이 A12 fence 밖 본문 누락을 잡지 못한 한계는 R1-D07 기록에 보존한다.

## Revision 0.9 Changes

| 입력 | 보완한 내용 |
| --- | --- |
| D08-F2 · Driver accept | 현재 권고 묶음의 잔존 `v0.7` 표기를 `현재 revision`으로 정리하고 현재 상태·검증 범위를 v0.9에 맞춤 |
| D08-F3 · Driver accept | A9/A12 exact fence의 후행 빈 줄 두 개를 제거. 본문 추출·메모리상 적용에서 후행 공백을 정규화하지 않고 raw bytes를 비교 |
| D08-F4 · Driver revise | preview가 이미 확인한 read-only 필수 flush 대상을 조기 non-pass로 알릴 수 있음을 선택 설명으로 추가. preview mutation이나 새 gate를 요구하지 않고 apply의 전체 사전 검사를 유지 |
| D08-F5 · Driver accept | A2에 Workspace의 Windows NTFS/read-only preflight가 함께 적용된다는 참조 한 문장 추가. 공통 조건과 지원 예시는 유지 |

D08-F1은 defend 처분대로 기존 문안을 유지한다. completed replay, First B1, 필수/허용 unavailable 동기화, B와 worker 공통 필요조건의 의미는 바꾸지 않는다. v0.8 문서 검증이 `trimEnd()` 이후 논리 본문을 적용해 raw fence의 후행 bytes를 그대로 검증하지 못한 한계는 R1-D08 기록에 보존한다.

## Revision 0.10 Changes

| 입력 | 보완한 내용 |
| --- | --- |
| D09-F1 · Driver revise | admission 대응표는 현재 revision을 가리키고, Open Points의 개정 설명과 리뷰 상태를 실제 v0.9/R1-D09 이력에 맞춤. 새 v0.10의 미재리뷰·미수락 상태를 명시 |
| D09-F2 · Driver revise | A9의 선택 조기 진단을 fresh repair preview로 한정하고, 그 진단이 non-pass를 반환할 때 실행 request/token을 제공하지 않음을 명시 |

진단은 이미 확인한 read-only 필수 flush 대상을 다루는 선택 설명이다. preview의 새 필수 검사나 mutation gate를 추가하지 않으며, apply의 전체 사전 검사와 발행된 token의 증거 한계는 유지한다. B·S1–S8·worker 공통 필요조건·기존 defend 처분은 바꾸지 않는다. R1-D09의 판정은 v0.9에 대한 이력이며 v0.10의 리뷰·계약 수락으로 재사용하지 않는다.

## Options Considered

표의 권고안은 아래 Proposed Clauses에 구체화했다. 각 행은 독립 수락이 가능한 완성 계약이라는 뜻이 아니며, lifecycle·mode·durability·window 사이의 의존성은 Open Points에서 함께 해결한다.

| 선택 | Driver 권고안 | 대안과 비용 | 현재 상태 |
| --- | --- | --- | --- |
| S1 · 지원·검증 정책과 시점 | B 유지: ARM64/x64 공통 정책과 실측 tuple을 구별. 대표 UTM 전체 검증, x64·물리 PC focused 보완, formal admission은 live macOS Preview 이후 | 추가 full matrix에는 구체 실패 mechanism과 focused 검사로 부족한 이유 필요 | B 지시됨; named amendment 미결 |
| S2 · 최초 lifecycle와 inventory | windows-1/profile·기존 29 paths·fresh/same-window, init1/switch2/repair1/detach4 후보; macOS 유지 | detach4는 기존 fields로 제거 뒤 정책을 구별. 다른 persisted 구분·이주는 별도 범위 | 구체 후보·pair·호환 규칙 문안 작성; 수락 미결 |
| S3 · 경로 검사와 identity | 실제 mutation 경로의 native local NTFS 확인, volume root부터 reparse/unknown 거절과 identity 재검증 | data-access ancestor pinning은 선택 시 보강. 모든 race 차단의 신규 의무는 비권고 | 경로·unsupported 문안 수락 미결 |
| S4 · writer 잠금 | 안정 anchor·delete share 제외·비상속 handle·timeout 없는 대기. 취소 종료 시 lock/handle 비보유 | timeout/즉시 실패는 caller 의미 변경. scratch anchor는 남을 수 있음 | 취소·scratch 의미 수락 미결 |
| S5 · 동기화와 발행 | 기존 필수/허용 unavailable를 phase별 대응. 진단 전용, authorized exact recovery에서 필요한 재flush | 모든 directory flush를 새 mandatory로 바꾸거나 receipt 필드를 추가하려면 별도 정책 선택 | 의무 대응·복구 관측 의미 수락 미결 |
| S6 · 상태·권한·content mode | Windows successor의 index/default·`100644` 규칙 유지. 새 파일 read-only clear, 교체·제거 및 필수 flush 기존 파일의 사전 거절, repair 0/1 관측 | non-Git `100755` 의도 및 index 불변으로 post-mode를 독립 관측하지 못하는 worker 결과 적용은 최초 미지원. 전체 지원에는 명시 mode authority 설계 필요 | 적용 범위·기본값·worker 포함 제한 수락 미결 |
| S7 · native 진입 | 절대 경로의 지원 Python + `-I -B`. 현재 PowerShell 5.1을 최초 qualification 대상으로 선택, `.cmd` 보류 | 필요한 입력 보존 실패 시 지원 미선언; exact PowerShell 7 대안 또는 기존 입력 경로 설명을 다시 제시 | native 기준 해석·shell 대상 수락 미결 |
| S8 · replace 실패와 retry | 자동 retry 0회, 원 request의 exact 재호출과 별도 새 repair preview 구별. 실제 pending barrier 보존 | bounded 자동 retry는 오류·횟수·예산·중단 의미를 별도로 결정 | 재시도·실패 분류 의미 수락 미결 |

## Proposed Clauses

아래 문안의 “한다/거절한다”는 수락 후 적용할 계약 문구의 초안이다. 현재 구현이나 현재 발효 상태를 서술하지 않는다.

### S1 — Support Policy And Admission Timing

**제안 문안:** Windows 11 지원 정책의 대상은 ARM64와 x64로 정한다. 정책 대상과 실제 검증 범위를 따로 표시한다. 실제 증거에는 edition/build, OS·process architecture, filesystem, shell, Git, final CPython build, source/artifact와 runner identity를 기록한다. 관측하지 않은 tuple을 실측·qualification 완료로 표시하지 않는다.

대표 UTM guest에서 normal·parent-optimized 전체 regression과 선택한 lifecycle 검증을 수행한다. x64와 물리 PC는 ABI, native API, process/launcher, 파일 잠금·replace 등 차이를 의심할 구체 지점에 focused 보완을 배정한다. x64·물리 환경의 부재만으로 별도 전체 suite나 물리 PC 필수 gate를 자동 생성하지 않는다. architecture별 실패 mechanism, 영향 범위와 focused 검사로 부족한 이유가 있으면 추가 전체 검증을 제안할 수 있다.

Windows 정식 admission은 live macOS Preview 이후다. 그 이전의 source-only 조사·계약 작성과 별도 승인된 격리 feasibility probe는 가능하다. 제품 변경은 필요한 계약 선택과 별도 실행 승인을 거치며, admission 시점의 제한을 없애지 않는다. 현행 열 가지 Windows criteria의 격리·native NTFS·전체 회귀·지원 문서 정합성은 유지한다.

**근거:** probe는 Windows 11 Pro 26H2, build 10.0.26300.9711, ARM64의 한 guest에서만 수행됐다. architecture별 추가 전체 검증을 필수화할 반증은 이번 결과에 없었다. 이는 x64 성공 증거가 아니다. R1-P01은 B 유지에 동의했다.

**미결:** S1-A는 현행 Windows Admission의 timing 문구에 위 준비/정식 admission 구분을 반영할지, S1-B는 공통 지원 대상·대표 실측·미관측 보완을 help/capabilities/docs에서 어떻게 동일하게 표시할지다. 둘 다 이 문안을 우선 권고한다. 지원 승격 시점과 exact public claim은 후속 admission의 실제 증거로 결정한다.

### S2 — Initial Lifecycle And Inventory Window

**제안 문안:** 최초 Windows 범위는 fresh successor 설치와 해당 window 내부의 preview/apply/refusal, status/doctor, update/rollback, exact repair, receipt-bound detach, current-format intent/Work/worker integrity로 한다. S6의 mode 제한도 이 범위에 적용한다. 기존 window에서 successor로의 Windows 이주와 cross-window rollback은 최초 범위 밖이다. unsupported 이주를 detach/reinstall이나 receipt 삭제로 우회하지 않는다. 기존 project truth와 pending 상태는 보존한다.

기존 macOS의 기본 window·init/update 동작은 이번 Windows 작업으로 바꾸지 않는다. 공통 module에 손대면 macOS regression 의무를 유지한다. 다른 OS에서 같은 successor를 읽거나 쓰는 조합도 별도 호환 근거 없이 지원으로 표시하지 않는다.

| 대상 조합 | 최초 권고 범위 |
| --- | --- |
| Windows fresh successor와 검증한 same-window writer | 선택한 lifecycle·S6 제한 아래 qualification 대상 |
| 신규 windows-1 Windows 경로 → predecessor/current old window | 기존 기록을 보존하며 가능한 진단과 unsupported 이유를 제공. 이 경로의 old-window mutation·successor 이주는 지원하지 않음. 기존 entry-1 source에 OS gate를 소급 추가하는 뜻은 아님 |
| 알려진 cooperating old writer가 successor에 접근 | fresh에도 발행 전 거절 확인 필요. 실제 노출된 writer의 거절이 미확인이면 미지원 label만으로 닫지 않고 qualification/activation을 중단. 검증된 비노출 대안은 아래 처분 적용 |
| 기존 macOS 기본 경로 | 현행 계약 유지. Windows 준비를 이유로 default window나 이주 정책 변경 없음 |

Windows 전용 successor를 사용해 S6의 mode 정책을 기존 macOS·old window와 구분한다. [Binding And Profile Identity Assessment](#binding-and-profile-identity-assessment)에서 확인했듯 현행 `entry-1`/CLI profile만으로 이 구별은 성립하지 않는다. 기존 binding의 release/window 참조 구조는 새 정책을 담는 데 사용할 수 있지만, 새 window 값에 Windows 전용 의미를 부여하는 계약 변경과 대응 reader/writer 검증이 필요하다. 구체 후보는 [Exact Window And Lifecycle Proposal](#exact-window-and-lifecycle-proposal)에 제시한다. window/profile은 `windows-1`, ordered membership은 기존 29 paths, detach는 paired4로 제안하며 exact 수락 대상이다. 실제 새 artifact와 실행 가능한 writer 조합은 qualification 계획에서 고정한다.

old-writer 거절 미확인의 구체 처분은 [Reader And Writer Combinations](#reader-and-writer-combinations)와 A5/A13을 따른다. S2에 포함한 exact repair의 qualification은 현행 admission criterion 2의 열거에 repair가 이미 있다는 뜻이 아니라, 이번 최초 Windows lifecycle 범위에 추가해 수락할 검증 의무다.

**근거와 권고:** launcher의 exact 11-module 검사, product의 inventory·retained-release 검사에 새 module이 영향을 준다. 새 Windows 상태 표현까지 고려하면 successor를 우선 준비하는 편이 명확하다. fresh라도 old writer가 접근할 수 있어 이주 제외만으로 거절 확인을 생략할 수 없다. fresh init·same-window repair에도 mode와 read-only fsync가 남으므로 과거 transition 제외만으로 이식이 끝나지 않는다.

**대안·미결:** 같은 window를 여러 OS에서 공유하며 현재 OS에 따라 mode 해석만 바꾸는 대안은 과거 record가 어느 정책으로 생성됐는지 구별하지 못한다. 그 대안을 선택하려면 persisted 정책 identity와 교차 OS reader·migration 의미를 별도로 설계해야 하므로 현재 권고로 택하지 않는다. 이주 포함안도 source→target→operation과 중단 prefix의 별도 범위·수락이 필요하며 반드시 새 DR를 만들 필요는 없다. Windows 전용 successor와 이 개정의 구체 값·record pair·repair mode 의미는 미수락 후보이며, 실제 writer/artifact qualification은 남아 있다. 알려진 old writer가 발행하면 candidate qualification/activation을 중단하고 아래 실패 처분을 따른다. 단일 이름이나 미검증 조합의 잔여 위험 표기만으로 통과시키지 않는다.

### S3 — Path Observation And Identity

**제안 문안:** 한 trusted local OS account와 cooperating agents라는 기존 보안 경계를 유지한다. Windows 지원 경로는 native local NTFS로 한정한다. volume root부터 target root까지의 절대 경로 chain, 그리고 실제 검사 대상 ancestor와 leaf까지 reparse attribute/tag를 확인하고 기본적으로 reparse를 거절한다. unknown·읽기 실패·판별 불가를 정상 경로로 간주하지 않는다. junction, mount point, redirected/cloud 경로도 이 규칙에 따라 지원 여부를 판정한다.

native local NTFS는 실제 mutation 전 검사 조건이다. target의 authority·managed runtime·변경할 content, staging, lock/scratch와 외부 repair backup 등 operation이 만들거나 바꾸거나 제거할 경로를 포함한다. 없는 leaf는 가장 가까운 기존 ancestor의 실제 volume·identity와 이후 생성 경로를 검증한다. path 문자열·drive letter·guest라는 설명만으로 NTFS를 추정하지 않으며 remote/non-NTFS/관측 불가는 non-pass다. scratch 생성 전에도 해당 경로를 검사하고, writer guard 안과 필요한 발행 지점에서 다시 확인한다.

bytes를 교체하지 않아도 해당 operation의 필수 flush 때문에 write-capable handle을 열어야 하는 기존 파일은 실제 검사 경로에 포함한다. 기존 staging member·receipt·외부 backup request/original 등이 해당하는지는 call-site 의무로 정하며, 모든 retained release나 읽기 source를 자동 포함하지 않는다. 이 파일들의 read-only 사전 검사와 recovery 재검사는 S6/A7을 따른다. 필수 flush를 생략해 검사 대상에서 빼지 않는다.

replace의 source와 destination은 같은 admitted volume이어야 한다. 외부 backup 전체가 target과 같은 volume이어야 한다는 새 제한은 없으며, copy·flush하는 각 경로가 native local NTFS이고 기존 독립·보존 조건을 만족해야 한다. read-only source에 대한 기존 검증을 완화하지 않지만 이 mutation 검사 때문에 관련 없는 모든 읽기 경로를 새로 조사하지 않는다. fixed drive라는 추가 조건이나 관리자 token gate는 도입하지 않는다. 표준 사용자 guest에서의 qualification은 S1의 증거 조건으로 별도로 유지한다.

기존 content membership/ignore와 Git topology 검사 범위는 유지한다. 이 조항 때문에 관련 없는 모든 디렉터리를 재귀 조사하거나 기존 제외 경로의 내용을 새로 수집하지 않는다. 기존 hard-link 제한과 content/root identity, case·normalization·reserved name·trailing dot/space 규칙을 보존한다.

관측한 경로와 실제 열린 handle의 identity를 대조하고 쓰기 전 필요한 검사를 반복한다. final-path 문자열만으로 alias·없는 leaf 생성·replace 대상·모든 race를 해결했다고 보지 않는다. 차이가 관측되면 affected mutation을 거절하고 상태를 보존한다. 이 계약은 같은 계정의 임의 비협조적 변경을 완전히 차단한다는 보장이 아니다.

**근거:** 표준 사용자 junction이 생성됐고 `is_symlink=False`인 채 하위 경로가 synthetic 외부 위치로 이어졌다. metadata-only ancestor handle은 이름 변경을 막지 못했다. 이는 data-access handle의 pinning 효과를 시험한 결과가 아니다.

**대안·미결:** 기본안은 위 검사 경계와 기존 identity 의미를 Windows에서 보존하는 것이다. data-access ancestor pinning을 선택할 경우 권한·share 조합과 create/replace 사용 지점을 계획에서 먼저 정한다. 여기서 B-1 probe는 그 선택한 ancestor handle이 rename을 막는지 확인하는 좁은 후속 실험 후보이며, 지원 정책 B나 DR-0004의 First B1 supplement와 다른 이름이다. 현재 관측은 모든 pinning의 반증이 아니고 B-1 실행도 승인되지 않았다. 경로·unsupported 의미는 Owner 선택 대상으로, 정확한 identity fields·alias 비교·검사 순서는 계획 세부로 남긴다.

### S4 — Stable Writer Lock

**제안 문안:** 하나의 안정된 lock anchor를 공유하는 cooperating writer guard를 유지한다. Win32 handle은 비상속으로 만들고 anchor에 `FILE_SHARE_DELETE`를 허용하지 않는다. caller는 guard 안에서 authority와 상태를 재검증하며, read-only inspection은 lock 파일을 만들지 않는다. lock을 얻었다고 작업이 허가되거나 여러 파일이 원자적으로 바뀌는 것은 아니다.

프로세스 간 경합은 timeout 없는 대기를 유지하고 같은 thread의 재진입은 기존처럼 즉시 거절한다. 기본 timeout 또는 자동 takeover를 추가하지 않는다. 대기 중 사용자 interrupt는 작업을 취소할 수 있어야 한다. mutation section에 진입하기 전에 취소되면 종료 시 lock/handle을 남기지 않고 authority·content를 쓰지 않는다. 대기 준비로 만든 정상 scratch parent/anchor는 남을 수 있다. lock 획득과 interrupt가 경합할 수 있으므로 “한 번도 lock을 얻지 않았다”는 의미로 정의하지 않는다. 이미 mutation section에 진입했다면 실제 발행 prefix와 기존 중단·복구 규칙을 적용한다.

byte-range 후보는 offset 0, length 1이다. 모든 writer가 같은 range를 사용하고 empty anchor와도 동작하는지 qualification에서 확인한다. 정상 종료·interrupt의 handle 정리와 강제 종료 뒤 다른 writer의 재획득을 검증하되 OS 해제 지연의 상한을 관측 없이 약속하지 않는다.

**근거:** delete share가 없는 anchor는 삭제가 거절됐다. delete share를 허용하면 기존 lock이 남아 있는 동안 같은 이름을 새로 만들어 다른 lock을 얻었다. 다만 probe는 flags=3인 즉시 실패 방식과 1-byte fixture만 시험했다. blocking, interrupt, empty anchor는 미검증이다. child의 invalid-handle 결과만으로 비상속 제어 전체가 입증되지는 않는다. 기존 helper도 blocking 전에 parent/anchor를 준비하므로 “아무 파일도 바뀌지 않는다”는 취소 약속은 맞지 않는다.

**대안·미결:** timeout·nonblocking default는 기존 caller 의미를 바꾸므로 우선안에서 제외한다. Owner는 대기·취소·scratch 의미를 선택한다. polling/overlapped 여부, acquisition/cancellation 순서와 대기 간격은 계획에서 고정한다. typed Win32 signature·pointer width·오류 전달·range·empty anchor·Ctrl+C·child 비상속·정리는 제품 qualification 대상이며, 계약 문안 선택 전에 새 probe를 일괄 요구하지 않는다. ARM64 관측을 x64 ABI 검증으로 쓰지 않는다.

### S5 — Flush And Publication Semantics

**제안 문안:** file flush, directory flush, replace/publication과 recovery 관측을 별도 단계로 구분한다. 기존 계약과 call site가 정한 필수 동기화와 허용된 unavailable를 Windows의 대응 단계에 명시한다. 필수 단계의 실패·unavailable는 non-pass이며 NTFS라는 이유로 N/A나 PASS로 바꾸지 않는다. 기존에 unavailable를 허용한 공통 helper를 이 초안만으로 새 mandatory 단계로 바꾸지도 않는다. macOS D3의 기존 필수 의무는 유지한다.

Windows file 및 필요한 directory flush는 write-capable handle의 명시한 API 결과로 판단한다. 새 파일·교체 파일은 기존에 필요한 content flush와 발행 순서를 보존하고, namespace 변경 뒤 parent sync의 의무는 각 call site에 대응한다. fresh init launcher와 기존 exact staging/receipt·외부 repair backup 등의 재확인에 남아 있는 read-only descriptor fsync도 call site별로 대응한다. 그중 필수 flush 때문에 write-capable open이 필요한 기존 파일은 S6/A7의 발행 전 전체 사전 검사에 포함하며, 교체하지 않는다는 이유로 동기화를 생략하지 않는다. API 성공은 OS가 그 요청에 성공을 반환했다는 관측이며 power-loss persistence 보장이 아니다.

| 관측 phase | 보존·진단·재호출 의미 |
| --- | --- |
| 발행 전 실패 | 원본·staging의 실제 상태와 실패 API를 관측. publication이 없었다는 결론은 확인한 범위에서만 제시 |
| 발행 후 필수 flush 완료 전 실패 | 앞선 발행을 없었던 것으로 표시하거나 자동 undo하지 않음. 허용된 prefix인지 기존 기록과 bytes/identity로 재검증 |
| 필수 flush 완료 후 후속 단계 실패 | 이미 관측한 성공과 뒤의 실패를 구별. 이를 전체 operation 성공으로 바꾸지 않음 |
| phase나 bytes/identity를 판별할 수 없음 | unknown 유지. 부재·PASS로 바꾸거나 receipt를 만들어 추정 상태를 확정하지 않음 |

디스크의 기존 request·receipt·staging·content 보존과 실패 출력의 보존은 구별한다. 진단 전용안을 택하면 출력에 있는 실패 phase가 다음 process에도 persisted됐다고 가정하지 않는다. 다음 호출은 기존 durable 기록과 실제 bytes/identity를 다시 읽고, 허용된 exact recovery인지 판정한다. 그 근거로 판정할 수 없으면 affected mutation을 거절한다.

필요한 재flush는 이미 승인된 exact apply/recovery의 해당 단계에서만 수행한다. read-only status/doctor는 재flush하지 않는다. 재flush 성공은 그 시점의 새 관측이며 과거 실패 단계가 성공했거나 그동안 power-loss persistence가 보장됐다는 증거가 아니다. 재flush 자체가 새 복구 경로나 다른 prefix를 허용하지 않는다.

진단에는 API method, 실행 결과, phase와 오류를 구별해 표현한다. `succeeded`, `failed`, `unavailable`, `not-attempted`는 설명용 범주이며 새 CLI enum이나 persisted schema로 확정한 값이 아니다. 새 receipt 필드 없이 진단으로 노출하는 최소안을 우선 권고한다.

**근거:** Python directory open은 errno 13이었다. probe의 write/read-write directory handle에서는 FlushFileBuffers가 성공했고 zero/read access에서는 error 5였다. source의 file fsync는 예외를 전파하지만 macOS fullfsync 결과와 일부 directory unavailable는 반환값이다. 공통 callers와 D3의 pass 요구도 다르므로 모든 sync가 이미 같은 mandatory 계약이라는 해석은 맞지 않는다. 현재 확인한 경로에서 결과 dict는 typed record에 저장되지 않으며 durability diagnostic CLI가 별도로 반환한다.

**대안·미결:** Owner 선택은 필수/허용 unavailable의 대응 원칙, 진단 전용, 복구 시 새 관측 의미다. 모든 directory flush를 mandatory로 올리거나 결과를 receipt에 넣는 대안은 의무·schema/window·old-reader 영향을 함께 수락해야 한다. 선택한 원칙 아래 lifecycle·일반 truth write·immutable 재확인의 phase, API/flag·오류 매핑·실패 주입 지점은 계획에서 고정한다. 그 과정에서 기존 의무나 reader 의미를 바꾸는 항목이 발견되면 해당 계약 선택을 다시 제시한다.

### S6 — Publication State, Permissions And Content Mode

**제안 문안:** Windows에서 `0600`/`0755`를 POSIX와 동등한 보안 또는 발행 완료 표식으로 쓰지 않는다. 설치 중 ACL을 임의로 확대하거나 ownership을 바꾸지 않고 선택한 trusted-local account 경계를 유지한다. 상속 ACL만으로 별도 기밀성·다른 계정 차단을 보증하지 않는다. read-only attribute도 권한 격리의 증거가 아니다.

완성·미완성은 허용된 staging/publication prefix, exact bytes·membership·binding과 receipt의 관계로 판정한다. 정상적으로 도달 가능한 fresh/same-window/repair 상태를 먼저 열거하고 interrupted/unknown을 보존한다. 권한 bit만으로 구별되던 상태를 다른 독립 durable 근거로 구분할 수 없으면 unknown으로 둔다. managed member의 Windows stat mode를 무결성 판정의 대용 증거로 삼거나 임의 권한 숫자로 prefix 검사를 통과시키지 않는다. 새 persisted 표식이 필요하면 S2의 window·reader 의미와 함께 수락 대상으로 제시한다.

#### Logical Mode Source And Default

아래 mode 출처 규칙은 승인할 Windows 전용 successor와 검증한 native Windows runtime 조합에만 적용한다. macOS와 기존 window의 mode 관측 의미는 바꾸지 않는다. 현재 binding/profile은 그 조합을 식별하지 못하며, 기존 release/window 참조 구조를 재사용하는 권고와 조건은 [Binding And Profile Identity Assessment](#binding-and-profile-identity-assessment)에 기록했다. 새 window의 의미와 runtime 검사 없이 이름만으로 정책을 추정하지 않는다. 항목별 provenance field나 mode registry를 기본으로 추가하지 않는다.

`100644`/`100755`는 content manifest의 논리 mode다. Windows 기본값 `100644`도 기존 TreeEntry의 같은 논리값이며 별도의 세 번째 mode가 아니다. 다만 그 출처가 Windows 기본 정책임을 알린다. 이 값으로 Windows ACL·기밀성·파일 실행 가능성을 판단하지 않는다. 설치 launcher의 발행 상태와 일반 project content의 mode 출처도 구별한다.

| 관측·작업 종류 | 최초 Windows 권고 규칙 | 출처·보존 조건 |
| --- | --- | --- |
| Git tracked content의 일반 snapshot | index로 후보 membership과 존재하는 tracked file의 mode를 정하고, 실제 bytes·존재 여부는 working tree에서 관측 | 아래 삭제/unknown 경계와 index 안정성 확인. unstaged bytes가 index blob과 다르다는 이유만으로 거절하지 않음 |
| exact retained Git tree가 계약상 입력인 작업 | 그 exact tree의 mode와 기존 retained-source 검증 적용 | 기존에 명시된 checkout 예외를 포함한 bytes·membership·mode 검증을 유지. 일반 snapshot의 관측을 이 기대값으로 대체하지 않음 |
| Git 저장소의 일반 untracked file | 논리 기본값 `100644` | Windows untracked default라는 출처를 알림. 제품의 명시 `100755` 의도 입력은 최초 제공하지 않음 |
| standalone non-Git의 일반 content snapshot | 논리 기본값 `100644` | Windows non-Git default라는 출처를 알림. 일반 `100644` Work 전체를 제외하지 않음 |
| Git 분류·index entry·mode가 unknown, 허용 외 mode 또는 관측 중 변경 | 기본값으로 대체하지 않음 | 읽기·분류 실패와 unmerged·unsupported를 원인에 맞게 구분. 관련 mutation을 거절하고 상태를 보존 |
| exact recovery/replay가 원래 참조한 manifest | 그 원참조의 mode·bytes를 기대값으로 보존 | 현재 관측과 독립 대조. 불일치 시 유리한 쪽을 선택하거나 임의 과거 manifest를 고르지 않음. 아래 읽기·mutation 경계 적용 |

index와 non-ignored untracked 목록은 후보 membership을 정하며, 실제 snapshot entry는 안전하게 관측한 regular file에 대해서만 만든다. stage-0 tracked 후보가 남아 있어도 정확한 경로의 실제 부재를 확인하면 entry에서 제외하여 삭제로 관측한다. alias, 다른 type, reparse, 접근 실패나 불안정한 관측은 affected operation의 관측을 non-pass로 만든다. 이 경로를 성공 snapshot에서 생략하거나 삭제로 기록하지 않는다. 부재는 S3에 따라 정확한 경로와 검사 대상 ancestor를 확인한 경우에만 인정하며, parent의 type/identity 문제를 없는 leaf로 처리하지 않는다. skip-worktree 등 부재가 삭제를 뜻하는지 분류가 필요한 경우를 무조건 삭제로 간주하지 않으며, 판단할 수 없으면 unknown으로 보존한다. 따라서 index를 바꾸지 않고 삭제한 뒤에도 실제 부재를 whole-result에 반영할 수 있다.

Git 여부 판별 실패나 index 읽기 실패를 “untracked” 또는 “non-Git”으로 간주하지 않는다. unmerged entry와 `120000`/`160000` 등 허용 외 mode의 기존 거절을 유지한다. 실제 경로가 Windows에서 regular file처럼 보인다는 이유로 이 entry를 `100644`로 바꾸지 않는다. stage-0·intent-to-add·skip-worktree 등 정확한 분류와 관측 안정성 검사는 계획에서 정한다.

같은 Work에 같은 mode 규칙을 적용한다는 뜻은 각 snapshot·worker 결과·비교에서 같은 분류 함수를 다시 평가한다는 것이다. Work 시작 시 경로별 출처를 동결하지 않는다. untracked `100644`→tracked `100755`와 tracked `100755`→untracked `100644`는 모두 출처 변화와 실제 mode delta로 표시한다. 이를 worker의 chmod 결과로 추정하지 않는다. 이 관측 규칙은 기존 baseline·drift·rebind 조건을 면제하거나 새 baseline의 자동 수락을 허용하지 않는다.

새 untracked/non-Git 파일의 기본값은 이름이나 확장자와 무관하게 `100644`다. 확장자·Windows association·chmod 결과로 `100755` 의도를 추정하지 않는다. 제품의 별도 mode 입력 미제공은 사용자의 표준 Git staging/mode 표현을 금지하는 뜻이 아니다. Git에서 mode를 표현할 수 있다는 사실과 제품이 그 결과를 적용할 수 있다는 사실은 구별한다.

출처와 최초 제한은 관련 preview·status·worker 결과·capabilities/help/docs에서 일관되게 설명한다. 매 항목에 새 persisted field를 두거나 모든 출력에 장문 알림을 붙일 필요는 없다. 알림 단위·위치는 계획에서 정하되 정책 출처와 미지원 이유를 숨기지 않는다.

#### Initial Support Limits

최초 Windows non-Git 경로는 `100755` 의도를 새로 생성하거나 변경하는 기능을 제공하지 않는다. 일반 untracked에도 제품의 명시 `100755` 입력을 제공하지 않는다. 기존 non-Git base 또는 참조 manifest에 `100755`가 있으면 그 의미를 `100644` delta로 흡수해 재개·발행하지 않는다. 원참조의 mode를 보존·적용·재검증할 수 없는 mutation과 pending recovery는 최초 지원 범위 밖이다.

affected mutation은 해당 mode 의미를 쓰거나 발행하거나 검증해야 하는 기존 operation 전체다. 일부 파일만 건너뛰고 나머지를 성공으로 처리하지 않는다. 해당 mode 의미와 무관한 operation을 이 사유만으로 project 전체에서 차단하지도 않는다. 이미 존재하는 worker/parent pending이 다른 writer를 막는 기존 barrier는 그대로 유지한다. unknown, unsupported와 기존 stale 조건은 각각 유지하며 구체 오류 매핑은 계획에서 정한다.

기존 기록의 읽기·진단, completed replay, pending recovery를 구별한다. 읽기 계약이 허용하는 기록은 원 mode와 함께 읽는다. 새 쓰기 없는 completed replay는 기존 runtime·graph·ticket·현재 상태 등의 검증을 유지하며, mode 적용 미지원만으로 새로운 mutation 거절을 추가하지 않는다. 기존 검증 실패까지 무시하고 성공을 보장하는 뜻은 아니다. pending recovery가 원 mode를 재현할 수 없으면 stable non-pass로 남긴다.

지원하지 않는 의도 때문에 원본 content, 과거 record, pending 상태 또는 원참조를 삭제·변경하지 않는다. `100644`로 바꾼 대체 request를 exact recovery로 표시하지 않는다. 정상 fresh Windows non-Git 경로가 만들지 않는 `100755` 기록을 만났다는 사실은 old-window·교차 OS·topology 변경 경로의 지원을 뜻하지 않는다. Windows에서 그 상태를 해소하는 경로는 최초 범위 밖이며 receipt 삭제·detach/reinstall·새 request로 우회하지 않는다. 기존 취소가 있는 operation도 그 원래 조건을 충족할 때만 사용할 수 있다.

#### Initial Worker Application Boundary

worker 결과 적용은 control의 HEAD·index·refs를 바꾸지 않으며, 완료 전에 독립적으로 관측한 전체 결과가 manifest result와 일치해야 한다. Windows의 index/default 정책 아래 두 의무를 함께 만족시킬 수 있는 결과만 최초 적용 대상으로 삼는다.

공통 적용 조건은 현재 검증한 control의 분류를 기준으로 적용 후 mode 또는 부재를 예측하는 것이다. result에 파일이 남는 경로는 control의 지원되는 stage-0 tracked 분류라면 그 index mode를 사용하고, 성공적으로 untracked로 분류된 경로라면 `100644`를 사용한다. result에서 삭제할 경로는 적용 후 부재가 목표다. base와 result 경로의 합집합 전체에서 이 예측과 result의 mode/부재가 같아야 한다. index 읽기 실패, unmerged·허용 외 mode, ignore/membership 또는 특수 flag의 해석 불가는 untracked 기본값으로 대체하지 않는다.

이 조건은 mode 적용 가능성에 대한 추가 필요조건이다. retained Git base/result·exact baseline·scope·membership·ignore·physical occupant·authority/runtime·required refs 등 기존 검증을 대신하지 않는다. 예측된 부재는 실제 부재의 증거가 아니며, 적용 후 bytes·membership·mode·부재를 다시 관측해 전체 result와 독립 대조한다. result manifest는 기대값이지 현재 mode나 실제 파일 존재 여부의 관측 근거가 아니다. prepare·apply·최종 검증은 같은 분류 의미를 쓰고, 발행 경계마다 필요한 관측을 갱신한다.

Owner 지시대로 지원은 이 공통 조건과 기존 모든 guard로 판정한다. 아래 표는 대표 예시이며 닫힌 지원 목록이 아니다. 표에 없다는 이유만으로 지원 또는 미지원을 결정하지 않고, 실제 분류와 전체 조건을 적용한다.

| control에 적용할 결과 | 최초 Windows 제안 범위 |
| --- | --- |
| tracked `100644` 또는 `100755`의 mode 유지 + content 변경 | 기존 모든 검증을 충족하면 qualification 대상 |
| exact base와 실제 경로에는 없지만 정상 stage-0 index entry가 있는 경로의 add | 해당 index mode와 result가 같고 기존 모든 검증을 충족하면 qualification 대상. `100755`여도 새 untracked 경로와 다른 분류 |
| 현재 untracked `100644`의 content 변경 또는 삭제 | retained Git provenance·exact baseline 등 기존 worker 자격도 충족하는 경우만 qualification 대상. 일반 local/non-Git snapshot 지원이 worker 자격을 대신하지 않음 |
| 새 untracked 경로의 `100644` 결과 | 같은 조건 아래 qualification 대상 |
| tracked `100644`/`100755` 파일의 삭제 | 실제 namespace 부재와 전체 result를 검증하는 qualification 대상. 잔존 index entry가 파일 존재를 뜻하지 않음 |
| 기존 경로의 `100644→100755` 또는 `100755→100644` 결과 | mode-only와 bytes 동반 변경 모두 최초 적용 미지원 |
| 새 untracked 경로의 `100755` 결과 | 최초 적용 미지원. `100755`를 유지한 rename/move/copy가 새 untracked destination을 만들 때도 같음 |
| 지원·미지원 결과가 섞인 operation | 전체 거절. 파일별 부분 성공 없음 |
| 그 밖의 결과 | 공통 조건과 기존 검증으로 판정. 정책상 post-mode를 실현할 수 없으면 미지원, 분류 불가면 unknown |

rename/move/copy는 실제 manifest의 delete/add/modify로 평가한다. 새 untracked destination의 `100755` 제한을 모든 rename/copy의 일괄 금지로 확장하지 않는다. 예를 들어 control index가 `100644`인 경로에 retained result `100755`를 적용하면 교체 뒤 index는 여전히 `100644`이므로 whole-result를 만족할 수 없다. 반대로 supported deletion은 실제 경로의 부재를 관측하므로 index entry가 남아 있어도 이 mode 변경 반례와 다르다.

새 worker accept prepare는 공통 조건을 확인해 미지원 결과에 적용 가능한 ticket을 발급하지 않는다. apply는 기존 exact baseline·authority 조건과 공통 조건을 재검증하고, 거절할 경우 새 work-decision·selection·current 또는 project content를 발행하기 전에 operation 전체를 멈춘다. S4가 허용한 lock/scratch 생성은 구별하며 invocation 전체가 zero-write라고 주장하지 않는다.

원래 적용 가능했던 결과가 prepare 또는 decision 이후 control index/membership 변화 때문에 불일치하면 기존 drift/stale 규칙을 따른다. 해당 관측이 가능한데도 이를 영구적인 정책 미지원으로 바꾸지 않는다. 이미 pending이면 원 decision·prefix·content를 보존하며 기존 exact 재호출·취소 조건을 유지한다. 정책상 post-mode를 실현할 수 없는 원 결과는 unsupported, 분류할 수 없는 상태는 unknown으로 남긴다. 기존 취소의 all-pre/no-durable-selection 조건을 넓히거나 history를 다시 쓰지 않는다.

기존 검증을 충족한 review submission, 읽기·진단과 ordinary reject는 accept 적용 가능성과 구별한다. 새 mode 적용 조건만으로 이러한 비적용 처분을 막지 않으며 새 decline 명령을 만들지 않는다. pending accept의 cancellation은 ordinary reject와 다른 기존 조건을 따른다. completed replay의 기존 읽기 조건, 다른 writer에 대한 pending barrier도 그대로 유지한다.

전체 mode 적용을 지원하려면 적용된 논리 mode를 독립적으로 입증하는 authority와 durable identity, reader·snapshot·recovery 비교 의미를 별도로 설계해야 한다. control index 자동 변경, 임의 manifest fallback, 새 registry/sidecar를 이번 초안에서 채택하지 않는다. 이 제한은 Windows 최초 지원 범위에 대한 명시적 축소 제안이며 macOS의 기존 worker mode 변경 계약을 축소하지 않는다.

#### Windows File Creation And Mutation Policy

Windows writer가 새로 만들거나 교체를 위해 staging하는 파일은 native `FILE_ATTRIBUTE_READONLY`를 clear로 관측한 뒤 발행한다. managed runtime, authority record, receipt, scratch·backup 파일과 writer가 새로 발행하는 content에도 적용하며, read-only flag를 immutability나 완료 표식으로 사용하지 않는다. 기존 파일·source·preserve-only evidence의 속성을 이 규칙으로 정규화하지 않는다.

init/update/rollback/repair/detach와 intent/Work/worker/planning mutation은 첫 durable authority/content/receipt/backup publication 전에 두 집합의 기존 파일 전체를 검사한다. 하나는 교체·제거할 파일, 다른 하나는 bytes를 바꾸지 않아도 해당 operation의 필수 flush 때문에 write-capable open이 필요한 파일이다. 하나라도 read-only이면 operation 전체를 non-pass로 거절하고 원 속성·bytes를 보존한다. unknown은 별도 non-pass다. 정상 guard 준비 scratch는 남을 수 있으나 검사 통과 전 authority/content나 복구용 backup을 발행하지 않는다. guard 안과 실제 교체·제거·필수 flush 직전에 재검사한다. recovery는 원 목록·허용 prefix 안의 남은 교체·제거와 그 prefix에서 필수인 재flush 대상을 함께 검사한다. 이미 발행된 파일도 필수 재flush가 있으면 포함한다. 이미 완료되어 읽기만 하는 replay에는 새 mutation gate나 flush를 붙이지 않는다.

필수 write-capable flush가 없는 순수 읽기·보존 파일은 read-only라는 이유만으로 이 사전 검사에서 거절하지 않는다. 이 면제는 repair의 bound before/after 같은 기존 관측 비교를 면제하지 않는다. 디렉터리는 기존 type·empty·identity·access 검사를 따르며 파일용 read-only flag를 디렉터리 권한의 대용으로 쓰지 않는다. 사전 검사 뒤 속성·identity drift 또는 실제 replace/remove/flush 실패가 생기면 원 request·backup·실제 prefix와 evidence를 보존한다. 원 파일의 flag 해제·ACL 확장·ownership 변경·delete-then-copy로 성공을 강행하지 않는다. 필수/허용 unavailable 동기화 구분은 S5를 유지하며 exact 영어 문안은 A7/A8/A9에 있다.

#### Windows Exact Repair Mode

일반 content의 논리 mode와 repair의 `FileObservation.mode`는 다른 계약이다. windows-1 candidate로 식별한 repair1에서만 `mode`를 native `FILE_ATTRIBUTE_READONLY`의 관측값으로 정의한다. flag가 없으면 integer `0`, 있으면 `1`이며 bool은 허용하지 않는다. 현재 stat 숫자나 확장자별 execute bit를 변환해 넣지 않는다. 다른 window의 POSIX mode 의미는 보존한다.

missing은 기존처럼 `before: null`이다. 존재하는 regular file은 exact bytes·size와 read-only flag를 일관되게 관측한다. 읽기 실패·type/reparse/identity 불일치는 unknown/non-pass다. `mode=1`은 유효한 read-only 관측값이지만 교체가 필요한 해당 파일을 이번 repair의 실행 가능한 request에 포함할 수는 없다. 그런 preview는 제한 이유를 보고하며 새 실행 request/token을 제공하지 않는다. 실행 가능한 request의 before는 null 또는 mode 0이고, after bytes·size는 exact active candidate, `after.mode`는 모든 경로에서 0이다. 이는 v0.6의 before 유지 규칙을 허용된 writable/missing 집합에 적용한 값이며 기존 파일의 flag를 해제하는 동작이 아니다. launcher에도 `0755`를 요구하지 않는다. before와 after가 같으면 repair 항목이 아니며 read-only만 해제하는 권한 복구 기능은 없다.

apply 직전·lock 안 재검사와 복구는 같은 Windows 관측을 다시 계산해 original before 또는 허용된 after와 비교한다. read-only flag drift도 exact request의 drift다. backup은 원 bytes와 canonical request의 관측값을 보존하며 원본이 없는 상태에서 repaired bytes를 backup으로 만들지 않는다. receipt 뒤 completed replay도 after 전체와 독립 product 검증을 요구한다. 완료 후 bound 파일의 flag가 0에서 1로 바뀌면 read-only replay라도 after 불일치로 non-pass다. 순수 읽기 면제는 이 관측 비교를 없애지 않는다. `mode` 일치만으로 완료를 선택하지 않는다.

교체할 staging file의 관측 flag는 after의 0과 같아야 한다. S6/A7의 전체 사전 검사는 read-only 교체·제거 대상과 필수 write-capable flush가 필요한 기존 파일에 적용한다. original file의 flag·ACL·ownership을 바꿔 replace를 강행하지 않는다. 검사 뒤 drift·실패는 원 request·backup·실제 prefix를 보존한 non-pass다. 원 before/after와 맞지 않는 속성 상태에서는 같은 exact retry를 거절한다. 교체가 필요한 read-only 파일이 남아 있으면 별도 새 preview도 non-pass이며 실행 request/token이 없다. 외부 backup은 product pending authority가 아니지만, 남은 손상에 read-only 교체 대상이 없고 현재 product·truth·candidate·pending 및 다른 기존 guard를 모두 만족할 때만 새 preview가 실행 요청을 제시할 수 있다. 외부에서 원 flag가 복원되면 원 retry도 다시 판정할 수 있으나 bytes·backup·candidate·binding·prefix를 포함한 모든 조건이 여전히 필요하다. 이 설명은 제품의 속성 해제 기능이나 복원 지시가 아니다. S8/A9/A11의 새 request·새 backup·승인 경계를 유지한다.

#### Evidence, Alternatives And Pending Choice

기존 probe에서 사용한 파일의 chmod 0600/0755와 Git index 100755는 Windows stat 0666으로 보였다. 이 관측은 해당 사례에 한정된다. [CPython 3.14.7의 Windows 구현](https://github.com/python/cpython/blob/v3.14.7/Modules/posixmodule.c#L1915-L1934)은 특정 실행 확장자에 execute bit를 더하므로 모든 이름에서 stat 0666이라고 일반화하지 않는다. 이 source 확인은 guest 확장자별 추가 실측이 아니다.

baseline `a93f71c`에서 Driver가 정적으로 확인한 현재 `_stable_file`은 stat execute bit로 mode를 정한다. Git snapshot도 index mode를 검사한 뒤 실제 TreeEntry에는 stat-derived mode를 넣는다. worker apply는 Git을 바꾸지 않고 파일 bytes/chmod를 적용하며 final에서 whole-result를 요구한다. 따라서 위 index/default 정책과 worker 제한은 구현된 동작이 아니라 R1-D02와 [D02-D1의 정적 대조](../development/CHORE-20261017-001-windows-utm-feasibility-probe.md#d02-d1-driver-finding--worker-mode-change-under-an-unchanged-index)에 따른 개정 제안이다. D02-D1은 실행 재현이나 Claude의 독립 source 검증을 받지 않았다.

권고는 공개 기본값과 위 최초 제한으로 일반 Work 및 mode가 안정된 worker 범위를 남기는 것이다. 첫 버전부터 명시 mode 입력·적용 authority를 제공하는 대안은 schema·reader·replay·window 설계와 qualification 범위를 키운다. Owner가 수락할 의미는 Windows 적용 조합, 기본값·출처, unknown 경계, 기존 기록·replay 보존, non-Git 및 worker 최초 제한이다. 현재 binding/profile의 불충분성, 기존 init chain의 충분성, detach 뒤 식별을 위한 구체 후보는 [Binding And Profile Identity Assessment](#binding-and-profile-identity-assessment)에 기록했다. index 안정성, 물리 occupant와 논리 snapshot의 일치, 사전 검사 위치, 발행 predicate와 알림 형식은 계획에서 구체화한다. 새 persisted 의미가 필요하면 S2와 함께 exact 수락 대상으로 제시한다.

### S7 — Native Entry And Argument Contract

**제안 문안:** 최초 Windows 진입 후보는 절대 경로의 exact supported Python을 명시해 `-I -B`로 관리 launcher 또는 독립 trusted source를 호출하는 방식이다. POSIX shell/WSL/Git Bash를 요구하지 않는다. PATH의 Store alias나 우연히 선택된 Python으로 실행 증거를 대체하지 않는다. Windows executable bit는 진입 성공의 전제나 증거로 사용하지 않는다.

현재 guest의 Windows PowerShell 5.1을 최초 qualification 대상으로 삼는다. 이는 5.1 지원이 이미 입증됐다는 뜻이 아니다. 정확한 interpreter build와 shell tuple, 실행 예, argv·기존 `--input` file/stdin·exit code, 공백·한국어·quote·필요한 metacharacter 입력을 실제 제품으로 확인한다. 기존 문서가 허용한 입력을 이식 편의를 위해 축소하지 않으며 새 stdin schema를 추가하지 않는다. shell escaping 책임이라는 설명만으로 이 검증을 생략하지 않는다.

필요한 입력을 5.1에서 보존할 수 없으면 지원을 선언하지 않는다. PowerShell 7 계열의 exact 대안이나 기존 입력 경로를 사용하는 정확한 예를 제시하고 바뀌는 지원 범위를 판단한다. 7.3+를 지금 새 필수 의존성으로 확정하지 않는다. `.cmd` wrapper는 최초 범위에서 제외한다.

**근거:** probe는 Python에서 명시적 Python child를 생성한 10개 인자 왕복만 확인했다. 두 `.cmd` 호출은 cmd용으로 적절하지 않은 quoting harness에서 echo 전에 실패했으므로 정상 argv 성공이나 일반적인 injection 재현의 근거가 아니다. 실행 중 batch 내용을 바꾼 사례는 기존 tail 미실행을 관측했지만 atomic replace 시험은 아니었다. 현 launcher는 isolated/no-bytecode 조건과 검증된 import 경로를 이미 다루며, 그 보호를 Windows에서 보존·검증할 필요가 있다.

**대안·미결:** Owner는 explicit Python을 native-launcher criterion의 허용 구현으로 인정할지와 최초 shell 대상을 선택한다. interpreter/runtime gate·isolated import, exact shell 명령과 입력 oracle, 동시 reader·실행 중 update/detach의 관측은 계획·qualification에서 고정한다. 이후 `.cmd`를 선택하면 정상 호출 harness, self-update/delete 시점과 안정된 별도 wrapper 여부를 비교한다. 현재는 추가 shell 실험을 시작하지 않는다.

### S8 — Replace Failure And Exact Retry

**제안 문안:** 파일 교체는 승인된 같은 filesystem의 발행 절차로 수행하며 delete-then-copy fallback을 금지한다. 자동 retry는 기본 0회다. access/sharing 오류가 발생하면 실패 phase와 native error, 읽을 수 있는 old/new/temp 상태를 남긴다. 읽기 실패·권한 거절을 파일 부재로 처리하지 않는다. 읽을 수 없는 상태는 unknown으로 보존한다.

명시적 exact retry는 기존 operation을 다시 호출하는 것이다. 새 retry 명령을 만들지 않는다. 원 request·token·candidate와 해당 operation의 recover 옵션·허용 prefix·재검증 규칙을 유지한다. 원래 계약이 같은 입력의 재호출을 허용할 때 그 규칙을 따르고, bytes/identity·operation/state가 달라지거나 허용 prefix가 아니면 기존 stale/refusal 규칙에 따라 거절한다. completed replay와 pending recovery를 같은 것으로 처리하지 않는다.

현재 lifecycle token은 canonical request digest에서 계산되므로 단회 소비형이라고 가정하지 않는다. 실패했다는 이유만으로 새 token/preview를 만들거나 token을 바꿔 pending을 우회하지 않는다. 원인이 사라졌다는 추정만으로 이전 mutation 부재나 retry 성공을 선언하지 않고 receipt·truth를 지워 성공 경로를 만들지 않는다. 기존 승인이 해당 exact 재호출을 포괄하면 별도 human 승인 단계를 자동 추가하지 않는다.

repair에서는 원 request/token·original backup에 맞는 exact retry와 별도 새 preview를 구별한다. 두 파일 중 첫 파일만 교체된 뒤 두 번째 파일의 read-only flag가 0에서 1로 달라지면 같은 recovery는 원 before/after 불일치로 거절한다. 그 파일을 교체해야 하고 read-only로 남아 있는 동안에는 새 preview도 non-pass이며 실행 request/token이 없다. 원 backup은 그대로 보존한다. 외부에서 flag가 원 before로 복원되면 원 request의 exact retry도 다시 판정할 수 있지만, 모든 bytes·관측·backup·candidate·binding·허용 prefix가 맞아야 하며 성공을 보장하지 않는다. 제품이 속성을 해제하거나 그 외부 변경을 지시하는 절차는 추가하지 않는다. 외부 repair backup은 binding-selection history의 pending authority가 아니므로 그 존재만으로 모든 새 preview를 금지하거나 영구 교착이라고 단정하지 않는다.

새 preview는 현재 active product·truth·candidate와 기존 pending 예외를 다시 검증하는 별도 읽기다. 남은 손상 집합에 read-only 교체 대상이 없어야 실행 가능한 요청을 만들 수 있으며, 새 apply도 S6/A7의 교체·제거 및 필수 flush 사전 검사를 충족해야 한다. 실제 pending lifecycle·detach·다른 기존 barrier가 있으면 우회하지 않는다. 새 실행 가능한 preview가 허용될 때에도 새 operation identity·새 exact request/token·새 외부 backup 경로를 사용하고, 원 요청의 token을 새 요청에 적용하지 않는다. 기존 요청·backup·부분 결과는 추후 처분까지 보존하며 이전 작업을 완료·취소 처리하거나 repaired bytes로 원 backup을 재구성하지 않는다. 새 apply에는 그 exact 요청을 포괄하는 기존 절차상의 승인이 필요하다. 지원하지 않는 read-only 대상의 속성을 임의로 해제하거나 실패 직후 자동으로 새 preview/apply를 실행하지 않는다.

**근거:** probe의 Python reader와 native share 3/7 reader 모두 열린 동안 `os.replace`가 WinError 5로 실패했고 close 후 성공했다. 이 관측만으로 모든 native rename API가 실패하거나 원인이 share mode 하나라고 단정하지 않는다. 전체 reader를 일괄 교체하는 근거도 아니다. nonempty directory replace 실패는 Windows만의 반증으로 쓰지 않는다. 현재 init exact recovery와 completed replay는 동일 request/source/confirmation의 별도 상태 의미를 가진다.

**대안·미결:** Owner 선택은 자동 retry 0회, 기존 operation 재호출과 실패 분류 의미다. bounded 자동 retry를 택하려면 오류·횟수·총 예산·상태 재검증·interrupt를 별도로 결정한다. 선택한 API별 pre-publication / post-publication-pre-required-flush / post-required-flush / unknown 대응과 각 operation의 실제 recover 인자는 계획에서 고정한다. S5의 분류는 새 복구 권한이나 token 수명 규칙을 추가하지 않는다.

## Binding And Profile Identity Assessment

**판정:** 현행 `entry-1` binding과 `--profile entry-1` 값만으로 Windows의 mode 정책을 식별하기에는 불충분하다. 다만 기존 `Binding → ReleaseRef → Inventory → exact payload` 구조는 Windows 전용 successor의 정책 identity를 운반할 수 있다. 권고는 그 구조에 새 window의 고정된 의미를 결합하고 실행 환경을 재검증하는 것이다. 이는 정적 설계 판단이며 현재 Windows 지원이나 구현 검증 PASS가 아니다.

| baseline에서 확인한 위치 | 실제로 식별하는 것 | 식별하지 않는 것 |
| --- | --- | --- |
| [Structure — Product Inventory And Lifecycle](../development/CHECKOUT-1-STRUCTURE.md#product-inventory-and-lifecycle), `product.py`의 `_init_binding_receipt` | binding의 active/prior release와 operation, release의 전체 digest와 `inventory_id` | 독립 OS·architecture·mode-policy field가 없음. 현행 `entry-1` 값은 Windows 정책을 뜻하지 않음 |
| `product.py`의 `_serial_inventory`, `verify_workspace_release` 및 root `colvia` | exact membership·inventory digest·payload bytes·launcher 선언의 일치 | digest 자체는 실제 실행 OS나 검증 tuple의 증명이 아님 |
| `cli.py`의 `--profile` 및 `run` | source lifecycle 분기에서 `entry-1`을 명시하도록 요구 | profile은 binding/plan의 persisted field가 아니며, artifact나 실행 OS의 증명도 아님 |
| `workspace.py`의 `runtime_supported` | final·GIL-enabled CPython의 명시 버전 집합 | OS·architecture·Windows mode 정책을 검사하지 않음 |
| `product.py`의 `require_workspace_runtime` | active `entry-1`, isolated/no-bytecode Python, control launcher와 loaded payload provenance | Windows 전용 정책 mapping 또는 native Windows 검사 없음 |
| `workspace.py`의 `target_fingerprint` | 검증한 절대 경로의 bytes hash | OS/runtime 정책 identity나 historical mode 출처를 대신하지 못함 |

현행 allowlist는 `entry-1`까지이며 Windows successor 값은 없다. 현재 값은 Windows 정책을 식별하지 못한다. source init은 launcher declaration을 읽어 candidate inventory를 만들고 원 plan의 `candidate_release={id, sha256, inventory_id}`에 넣는다. canonical request 전체가 token에 결속되며 apply는 candidate와 원 plan을 다시 비교한다. 따라서 binding 이전 identity를 위해 새 field가 필요하다는 우려는 현행 shape에 해당하지 않는다. 이 확인은 아직 없는 Windows 선택·검사 경로의 실행 증거가 아니다.

반면 현행 detach plan의 `candidate_release`는 null이다. receipt는 prior binding ref와 제거할 binding/inventory의 digest를 보존하지만 product 제거 뒤 그 digest만으로 window literal을 복원할 수 없다. detached root의 재초기화 금지는 `.hrn/detached.json`과 기존 root 상태로 집행되므로 Windows label이 없어도 유지된다. 그러나 Windows reader가 inventory 제거 뒤의 pending detach를 같은 정책으로 이어가려면 원 plan 자체에서 적용 window를 구별해야 한다.

이를 위해 아래 `windows-1` 전용 paired detach schema `4`를 권고한다. 필드는 기존 detach shape와 같고 plan과 receipt의 version을 함께 4로 고정한다. version 4가 `windows-1`에만 대응한다는 새 의미, 그 window의 exact removal membership과 prior binding/inventory digest 검증을 함께 수락해야 한다. version 숫자만 보고 damaged receipt를 정상으로 보거나 실제 runtime·환경이 qualified됐다고 판단하지 않는다. 원 기록이 schema 1/2/3이면 Windows 의미로 재분류하지 않고 기존 역사적 규칙으로 읽는다. 이미 발행된 기록의 version을 올리는 migration은 이번 범위가 아니다.

이 선택은 `Binding`, `ReleaseRef`, `Inventory`, `TreeEntry`에 새 mode-policy field를 넣지 않는 권고를 유지한다. 다만 “모든 schema 의미가 그대로다”는 결론은 아니다. Windows window와 detach4는 분명한 persisted 계약 변경이다. 같은 window의 모든 허용 release는 동일한 mode 정책과 detach4 의미를 유지한다. 다른 정책을 같은 window에 덮어쓰거나 현재 OS로 과거 mode를 재해석하지 않는다.

B의 정책 대상과 실제 qualification tuple은 계속 구별한다. runtime gate를 통과하는 것, 정확한 policy identity를 검증하는 것, 특정 환경에서 검증을 마친 것은 각각 다르다. 관측 tuple 하나를 자동 제품 allowlist로 바꾸지 않으며 unknown 상태를 다른 window의 정책으로 대신 처리하지 않는다.

## Exact Window And Lifecycle Proposal

아래는 v0.10에서 선택되어 2026-10-18 수락된 계약 묶음이다. 표의 제안 표현은 검토 당시의 값을 보존한다. 제품 구현·qualification·activation은 아직 없으며 미래 구현 artifact의 digest는 qualification 때 고정한다. 계약 수락은 완료되었고 그 digest가 있어야 계획을 준비할 수 있는 것은 아니다.

| 항목 | 구체 제안 | 의미와 남은 증거 |
| --- | --- | --- |
| Inventory window / source profile | `windows-1` / `--profile windows-1` | 현행 allowlist에 없는 신규 값. native Windows source 경로는 이 후보만 선택·검증하고 entry-1 자동 fallback 금지 |
| Launcher / adapter | `colvia` / `adapters/colvia-work/SKILL.md` | 명시 Python 진입. `.cmd`·새 registry·새 managed module은 이 membership 제안에 없음 |
| Ordered membership | A9의 정확한 29 paths | entry-1의 경로 집합을 그대로 사용하되 window·payload bytes는 별도. 구현 중 member가 필요하면 이 목록을 수정·재수락 |
| Root / inventory / binding | format 1 / inventory 1 / binding 1 | 기존 필드 유지. 새 window의 의미는 별도 수락하며 root version만으로 호환을 추정하지 않음 |
| Init | plan 1 / receipt 1 | candidate release에 windows-1, expected binding null. 원 request/token/candidate 일치 |
| Same-window update / rollback | plan 2 / receipt 2 | prior·candidate 모두 windows-1. rollback은 검증한 직전 release. entry-1 paired2 의미와 구별 |
| Exact repair | plan 1 / receipt 1 | candidate가 exact active windows-1. A9의 read-only 관측 mode 0/1과 외부 backup·drift/replay 비교. 기존 pending 예외·보존 의무 유지 |
| Detach | plan 4 / receipt 4 | Windows 전용 pair. candidate null, prior binding ref와 exact remove/preserve inventory 유지. 제거 뒤에도 version과 고정 membership으로 정책 식별 |
| Intent / Work / candidate records | 현재 각 family의 schema 유지 | local/worker/parent·planning 원의미 유지. mode 관측만 S6의 windows-1 정책 적용; 새 per-entry field 없음 |
| Native runtime | Windows 11 ARM64 OS + ARM64 64-bit CPython 또는 x64 OS + x64 64-bit CPython | A10 Security Runtime And Scope가 version/build-mode 정본. 현재 final·GIL-enabled 3.14.6/3.14.7 및 isolated/no-bytecode 유지. 정확한 build 실측은 qualification 증거 |
| 최초 제외 runtime | 32-bit, x64-on-ARM64 등 emulated process, POSIX 호환 runtime, 다른 OS | 초기 지원 밖이라는 제안. 문자열 이름만으로 판별하지 않고 실제 OS/process/runtime 조건을 검증. 포함 확대는 별도 계약·증거 |
| Native shell | Windows PowerShell 5.1 + absolute Python path | 입력 보존을 입증해야 지원 가능. 실패 시 미지원 유지, PowerShell 7 대안은 별도 선택 |

표준 사용자 실행은 최초 지원·admission 증거의 환경 조건이며 elevated 실행은 이번 qualification에 포함하지 않는다. 새 per-writer 관리자 token 거절 규칙은 추가하지 않는다. 반면 native local NTFS는 A7의 실제 mutation 경로 검사 조건이며 OS/process/runtime gate와 함께 집행한다. 이 구별이 B의 대표 UTM 전체 검증과 x64/물리 focused 보완 배정을 바꾸지는 않는다. 미관측 x64를 qualified로 표시하지 않고 추가 full matrix·물리 PC gate를 자동으로 만들지 않는다.

### Reader And Writer Combinations

| 실행 주체 → 대상 | 허용 의미의 제안 |
| --- | --- |
| 독립 Windows source → native Windows fresh target | 명시 windows-1 profile, 검증한 candidate 선언/inventory, native runtime 일치 뒤 init preview/apply. 다른 window candidate는 mutation 전 거절 |
| 설치된 windows-1 control writer → 같은 window | active binding/release/payload를 검증하고 허용한 local/parent/worker·planning 및 same-window lifecycle 수행. ticket과 binding drift 규칙 유지 |
| 같은 window의 worker → control | 등록된 동일 Git common directory, exact retained base/result와 현재 검증한 worker/control runtime pair 아래 제출. worker가 control authority를 직접 쓰지 않음 |
| 독립·retained windows-1 source → 같은 window의 중단 상태 | original request/token·candidate 또는 active binding·detach4와 exact prefix가 일치하는 기존 recovery만 허용. 한 window의 허용 release는 양방향 reader 의미를 보존해야 함 |
| entry-1 및 그 이전의 알려진 cooperating source/installed writer → windows-1 | authority/content 발행 전 거절을 qualification으로 확인. 기존 version만으로 성공 거절을 추정하지 않음 |
| 신규 windows-1 경로 → old window 또는 다른 OS | 허용된 진단/원기록 읽기만; 이 경로의 old-window mutation·이주·cross-window/cross-OS rollback 미지원. 기존 entry-1 source에 새 OS gate를 backport하는 제안 아님 |
| detach4 → source reader | receipt 안의 complete plan·preserve/remove inventory와 실제 prefix를 검증. read-only 읽기에 별도 외부 plan/token을 필수화하지 않음. mutation recovery는 원 target·원 exact plan/token 필요. policy 식별은 환경이나 과거 flush 성공 증명이 아님 |

writer audit의 최소 기존 입력은 이 source baseline `a93f71c359c4f0a9d57fcfb50d5999160e870f77`, DR-0004의 entry-1 activation release digest `596946e9370c7de83313417b7e23362a8ce19c5f25a5b8ce72e8dc422b9c49ea`, First B1 release digest `2216a2634eb3fa5d6a8bfa7c7d4847b29fb2443ba7b367156c15b15ddb5a17e0`, retained checkout-1 predecessor digest `8bd0eeac55fb0af92b61a7a36a98adb9957b880c791b957b20c319a51c5577f3`다. 서로 다른 source commit과 release digest를 같은 identity로 취급하지 않는다. 이는 알려진 비교 입력을 식별한 것이며 그 exact bytes의 회수·실행·모든 historical writer 검증을 마쳤다는 뜻이 아니다. 실제 접근 가능한 추가 old writer와 새 Windows artifact는 qualification 계획에서 exact identity로 고정하며 미확인 항목을 통과로 닫지 않는다.

실제로 노출된 known cooperating old writer는 authority/content 발행 전 거절이 확인되어야 한다. 거절이 미확인·실행 불가이거나 그 writer가 발행할 수 있으면 해당 candidate의 qualification과 activation을 완료하지 않는다. 미확인 상태를 “unsupported”로 이름만 바꿔 통과시키지 않는다. 모든 historical writer의 회수를 새 필수 gate로 만들지는 않으며 실제 접근 가능한 writer 집합과 접근 경로를 먼저 고정한다. 거절을 실행 확인할 수 없다면 검증 가능한 비노출 경계로 해당 접근이 제외됨을 입증해야 한다. 노출 자체가 불명확하면 비노출로 닫을 수 없다. 잔여 위험 label만으로 통과시키지 않는다. 기존 shape로 가능한 최소 유효 거절 장치부터 검토하고, 충분하지 않으면 old reader가 거절하는 format/schema 구분 또는 그 writer가 해당 대상에 접근하지 않는 검증 가능한 운영 경계를 제안한다. 단순 사용 자제 문구는 비노출 근거가 아니다. 선택한 조치가 persisted 의미·지원 범위·신뢰 경계를 바꾸면 exact 문안을 다시 수락해야 한다. 실패만으로 새 field가 필수라고 단정하지 않으며 비협조적인 같은 계정의 임의 편집까지 차단한다고 약속하지 않는다.

## Named Amendment Map

이 표는 수락된 A1–A15가 후속 통합에서 수정할 named scope를 식별한다. 오른쪽 문서의 기술 조항을 이번 기록 작업에서 적용·발효하지 않는다. 영향 없는 macOS 계약과 역사적 acceptance bytes는 보존한다. worker 관련 변경·유지 의무는 다음 절에서 더 좁게 식별하며, [Exact Proposed Contract Amendments](#exact-proposed-contract-amendments)에 A1–A15의 삽입·교체 위치와 본문을 제시한다.

| 기존 조항·authority | 제안 변경 | 연결 선택 |
| --- | --- | --- |
| DR-0003 retained Windows intake; [Development Index — Windows Admission](../development/README.md#windows-admission) | B의 policy/observation 분리, 준비와 formal admission timing, native 진입 해석; criterion 5의 최초 worker 지원 집합과 criteria 6–9의 거절·검증·표시 영향 명시 | S1, S6, S7 |
| DR-0002 technical baseline / DR-0004 entry-1·First B1; [Workspace — Root Primitives, Layer Responsibilities](../WORKSPACE-CONTRACT.md#root-primitives) | Windows의 path/identity·lock·sync·권한 관측을 명시. 기존 trusted-local 경계와 macOS 의미 유지 | S3–S6 |
| [Workspace — Init, Update, Exact Repair, Detach](../WORKSPACE-CONTRACT.md#actual-init-and-recovery-development); [Operations](../OPERATIONS.md) | fresh/same-window, read-only 생성·교체·제거, exact retry와 새 repair preview, 미지원 이주·기록 보존 | S2, S5, S6, S8 |
| [Manual Operation — Retained Evidence](../MANUAL-OPERATION.md#retained-evidence) | A14의 내장 complete plan을 이용한 detach4 읽기와 qualified reader 증거, mutation recovery 입력과의 구별 | S2, S6, S8 |
| [Structure — Content Trees And Manifests](../development/CHECKOUT-1-STRUCTURE.md#content-trees-and-manifests); [General Work](../GENERAL-WORK.md) | Windows index/default 출처, unknown 거절, 공개 100644 기본값과 non-Git 100755 최초 제한. 논리값·exact manifest·원기록 의미 유지 | S6 |
| [General Work — Worker Publication Development Checkpoint](../GENERAL-WORK.md#worker-publication-development-checkpoint)의 mode 적용·완료·중단 복구 문단 | 최초 Windows의 mode-change/새 untracked 100755 결과 적용 제한과 발행 전 거절. index 불변·whole-result·기존 replay/cancellation 의무 유지 | S6 |
| [Structure — Exact Managed Membership](../development/CHECKOUT-1-STRUCTURE.md#exact-managed-membership); [Maintaining — Inventory Window Compatibility](../MAINTAINING.md#inventory-window-compatibility) | exact successor 이름·membership·OS/runtime/profile·reader/writer 집합과 pair 검증; fresh와 이주 범위 구별 | S2, S6 |
| [Security And Support](../SECURITY-AND-SUPPORT.md), [Getting Started](../GETTING-STARTED.md), [Reference](../REFERENCE.md), help/capabilities/managed entry | 지원 정책·실측 tuple·기본값·unsupported·실행 예·오류 의미의 일치. 실제 활성화 시 exact 기술 문서 집합 갱신 | S1, S3, S5–S8 |


| Exact 문안 | 고정하는 named scope |
| --- | --- |
| A1–A5 | 삭제·mode·worker·admission 5/8·정책 identity |
| A6 | B의 준비/정식 timing·native entry·runtime scope |
| A7–A9 | 실제 NTFS mutation 경로·read-only 정책·lock/flush/retry, lifecycle/detach4, membership/pairs·repair 관측 |
| A10–A12 | runtime support, native operations·arguments·failure 해석 |
| A13–A15 | qualification·old-writer 처분, retained reading·첫 진입 안내 |

## Worker Contract And Admission Impact

아래는 수락된 S6 최초 제한이 후속 Windows 통합에 미치는 영향이다. 현행 normative 문서와 admission 기준의 기술 본문은 이번 기록 작업에서 수정하지 않는다. Windows 지원을 전제로 기준을 완료 처리하거나 기존 macOS 기능을 축소하지 않는다.

| 기존 계약·기준 | Windows successor에서 제안하는 변경 | 그대로 유지할 의무 |
| --- | --- | --- |
| [Structure — Content Trees And Manifests](../development/CHECKOUT-1-STRUCTURE.md#content-trees-and-manifests)의 TreeEntry·Change·manifest | S6의 index/default 출처와 unknown 거절을 명시. 논리 mode가 달라지는 실제 delta와 Windows 출처를 표시 | 허용 mode 두 값, mode를 포함한 exact entry/digest·changes, scope·membership·ignore·provenance 검증. 새 필드/schema를 임의 추가하지 않음 |
| [General Work — Worker Publication Development Checkpoint](../GENERAL-WORK.md#worker-publication-development-checkpoint)의 add/delete/executable-mode apply 문단 | 최초 Windows에는 S6의 독립 post-mode 관측이 가능한 결과만 적용. mode 변경 및 새 untracked 100755는 위 경계에서 사전 거절 | control HEAD·index·refs 불변, 원본·retained source 보존, 전체 result 일치 뒤 완료 selection, 부분 파일 성공 금지 |
| 같은 문단의 interrupted apply·historical replay | 최초 미지원 mode의 pending recovery는 상태를 보존한 non-pass. 새 결과는 durable decision/content 발행 전 제한 검사 | 원참조·원 request와 기존 retry/cancellation 조건, completed replay의 기존 읽기 조건, stale·outside drift·unknown 거절 |
| Windows criterion 5 · current-format intent/Work/worker integrity | 지원할 worker 결과 집합을 S6 범위로 명시적으로 제한하는 amendment 후보 | 지원 결과의 실제 lifecycle·integrity 검증과 미지원 결과의 발행 전 거절·보존 검증. 기록 파싱만으로 integrity PASS 처리하지 않음 |
| Windows criteria 6–8 · recovery/regression/parity | 제한 사례의 안정적 non-pass, 관련 expected result, 지원 설명을 동일한 문안에 맞춤 | 중단·동시성·normal/parent-optimized 전체 회귀·focused lifecycle·macOS 회귀 의무. 전체 suite를 일부 mode 사례로 대체하지 않음 |
| Windows criterion 9 · inventory bytes/digest | content 논리 mode 정책과 source/artifact inventory identity를 구별 | checkout 설정을 이유로 source/artifact/manifest bytes나 digest를 묵시적으로 바꾸지 않음. 두 autocrlf 검증 유지 |

이 제안은 worker 무결성 검사를 완화해 더 많은 결과를 통과시키는 변경이 아니다. 새 Windows 지원 집합을 제한하고, 그 밖의 결과가 안전하게 거절되는지 입증해야 한다. 기존 성공 기대의 mode-change 사례를 Windows에서 미지원 예상 거절로 바꾸려면 이 계약 범위의 수락과 명시적 검증 계획에 연결한다. skip·실행 불가·실패를 PASS로 바꾸거나 기존 macOS 기대 결과를 변경하지 않는다. 공개 설명도 “Windows worker 전체 mode 동등성”을 주장할 수 없다.

S1의 B 검증 배정과 정식 admission 시점은 유지한다. 이 제한을 받아들여도 native Windows admission과 Public Core/GA의 기존 선후 관계는 없어지지 않는다. 해당 amendment는 이번에 수락되었지만 구현·검증·activation 전까지 현행 admission 기준을 충족한 것으로 처리하지 않는다.

## Exact Proposed Contract Amendments

아래 A1–A15는 지정 위치에 넣기로 수락된 정확한 영어 개정 본문이다. target 문서의 기존 영어 문체를 유지하며 이번 기록 작업에서는 그 기술 본문을 적용하지 않는다. `windows-1`/profile, A9의 membership·record pair와 runtime 범위는 후속 구현·검증의 확정 기준이다. 계약 수락은 runtime allowlist 적용이나 지원 발효를 뜻하지 않는다. 각 Windows 한정 절이 기존 generic 문장을 어떻게 한정하는지 삽입 위치에 명시하며, 역사적 계약·macOS 의미·관계없는 의무는 유지한다.

### A1 — Structure Content Observation

대상: [Structure — Content Trees And Manifests](../development/CHECKOUT-1-STRUCTURE.md#content-trees-and-manifests). 기존 shape와 provenance field 설명은 유지하고 이 절의 마지막에 아래 단락을 추가한다. 기존 일반 membership 문장은 Windows에 한해 이 관측 규칙으로 구체화한다.

````markdown
#### Windows Successor Content Observation

For windows-1 only, Git index entries and non-ignored untracked paths define candidate membership; they do not prove that a file exists. A snapshot includes only safely observed regular files under the existing scope-independent membership and ignore rules. An ordinary tracked candidate that is confirmed absent from the actual namespace has no TreeEntry, even while its index entry remains. Confirm absence under Workspace Contract's Windows Native Observation And Publication for the exact path and its examined ancestors. Aliases, unexpected types, reparse points, inaccessible paths and unstable observations make the affected observation non-pass; do not omit them from a successful snapshot or record them as deletions. Special index states whose absence cannot be classified as deletion remain non-pass.

Within windows-1, an existing supported stage-0 tracked file takes logical mode from the validated index and bytes from the working tree. An unstaged content change is not refused merely because its bytes differ from the index blob. A successfully classified untracked or standalone non-Git regular file uses logical mode 100644 regardless of extension. Failed Git/index classification, unmerged entries, unsupported modes and indeterminate flags do not fall back to that default. Re-evaluate the same policy on each observation. This policy does not change the two allowed TreeEntry modes, exact tree/digest rules, retained-tree verification or existing baseline and drift guards. A logical mode is not evidence of Windows permissions or executability.

Preserve original manifest modes and bytes as expected values for existing records. Do not relabel a retained 100755 record, select a historical manifest as current observation or rewrite an unsupported pending operation. The initial windows-1 non-Git path has no product input for creating or changing a 100755 intent and does not support mutation or pending recovery requiring that intent to be reproduced. Reads and historical completed replay retain their existing checks; application limitations do not add a mutation gate to an otherwise permitted read-only replay. Existing windows and macOS semantics are unchanged.
````

### A2 — General Work Worker Application

대상: [General Work — Worker Publication Development Checkpoint](../GENERAL-WORK.md#worker-publication-development-checkpoint). 기존 “add/delete/executable-mode changes” 문단은 보존하고, 같은 절의 마지막·Git Integration And Candidate Reuse 바로 앞에 아래 Windows 한정 단락을 추가한다.

````markdown
### Windows Initial Worker Application

The windows-1 successor adds a mode-feasibility condition to worker result acceptance. All existing retained Git provenance, exact baseline, scope, membership, ignore-policy, physical-occupant, authority/runtime and required-reference checks remain mandatory. The operation does not change the control HEAD, index or refs. This condition does not authorize an uncommitted worker result or replace any existing guard. Workspace Contract's Windows Native Observation And Publication also applies its operation-specific NTFS/read-only preflight to these writes.

For windows-1, extend the unchanged explicit CRLF exception to verified active windows-1 under exactly the same retained text/eol=crlf proof and exclusions; other windows keep their original admission. Windows lifecycle follows Workspace Contract's Windows Fresh And Same-Window Lifecycle and Operations' Windows-1 Native Entry And Recovery. Those Windows-only clauses qualify this document's entry-1 source-profile, exact-active-repair and schema-3 detach descriptions; they do not admit an old-window transition.

Using the currently validated control classification, predict the logical mode that a remaining result path would have after application without changing the index: use its supported stage-0 index mode, or 100644 only when the path is successfully classified as untracked. A result deletion requires absence after application. Across the union of base and result paths, every predicted mode or absence must agree with the result; a mismatch refuses the entire operation, and an indeterminate classification remains non-pass without default substitution. Prediction is an additional necessary condition, not evidence of actual content or absence. Re-observe actual bytes, membership, mode and absence independently before selecting completion; the whole result must match. The expected manifest cannot supply the current observation.

Initial application eligibility is defined by that common condition together with every existing guard, not by a closed example list. Examples include stable tracked 100644/100755 content changes, eligible existing untracked 100644 content changes or deletions, new untracked 100644 results, and tracked deletions of either mode. A supported stage-0 index entry for a path absent from both the exact base and the safely observed actual control namespace may also allow a result addition at the same index mode, including 100755, if all retained-source, baseline and physical checks hold. It is not a new untracked 100755 case. Qualification must cover these distinct classifications; an example is not an unconditional support grant.

Mode-changing results and new untracked destinations requiring 100755 are initially unsupported, including rename/move/copy results requiring that destination mode. Evaluate actual manifest changes and destination classification rather than imposing a blanket rename prohibition. An index entry surviving a real deletion is not proof of a remaining file. Mixed supported/unsupported results refuse as a whole.

New accept prepare refuses an unsupported result without issuing an applicable ticket. Apply repeats existing baseline/authority checks and the mode-feasibility check before publishing a new decision, selection, current or project-content change. Lock/scratch effects remain governed by the lock contract; the invocation is not claimed to make zero filesystem writes. Later control index or membership drift follows existing drift/stale rules, distinct from a policy-level unsupported result or unknown classification.

Preserve already published pending prefixes, original decisions, content and exact recovery inputs. Keep existing retry, cancellation and completed-replay conditions, including the all-pre/no-durable-selection cancellation boundary and pending barriers on other writers. A valid review submission and ordinary reject remain distinct from content application; this mode condition alone does not forbid those operations. No new command, index mutation, mode registry or manifest fallback is introduced. Existing macOS worker mode-change behavior and qualification expectations are unchanged.
````

### A3 — Windows Admission Criterion 5

대상: [Windows Admission](../development/README.md#windows-admission)의 “Ten criteria remain” 문장에서 다섯 번째 semicolon 항목 `fresh clone/worktree and current-format intent/Work/worker integrity`만 아래 한 문장 조각으로 교체한다. 나머지 항목·순서·현재 선후 조건은 유지한다.

````text
fresh clone/worktree and current-format intent/Work/worker integrity within windows-1's common-condition mode/application contract, with both supported completion and whole-operation prepublication refusal verified
````

같은 절의 기존 ten-criteria 문단 뒤에 아래 검증 범위 단락을 추가한다. 이어 A4의 표시 단락을 둔다.

````markdown
For criterion 5, qualify the common-condition support definition in General Work's Windows Initial Worker Application and Structure's Windows Successor Content Observation. Representative successful cases include stable tracked 100644/100755 content changes, eligible existing untracked 100644 content changes/deletions, new untracked 100644 results, tracked deletions of either mode, and an index-only tracked path absent from both the exact base and the safely observed actual control namespace receiving an addition at its unchanged supported index mode. These are examples, not a closed support list or sufficient conditions. Eligibility still requires retained Git provenance, exact baseline and all other guards; a parsed record or an unreachable fixture is not a pass.

Verify whole-operation refusal of mode-changing results, new untracked 100755 destinations and mixed supported/unsupported results before a new decision or project-content publication. Include prepare success followed by index/membership drift and apply refusal, indeterminate classifications, and actual namespace absence after deletion. A surviving index entry does not prove file existence; unsafe or unreadable observations are non-pass rather than deletion.

Criteria 6–9 retain interruption/concurrency, exact retry or stable non-pass, complete normal and parent-optimized regression plus focused lifecycle and macOS regression, support-description parity, and inventory-byte/digest preservation. Keep pending/replay/cancellation distinctions and existing macOS successful mode-change expectations. Tie Windows expected refusals to the accepted scope; do not turn skips, unavailable execution or unexpected failures into passes. Preserve both autocrlf checks and the representative-UTM/full-suite and focused-follow-up allocation in this Windows Admission section.
````

### A4 — Windows Admission Criterion 8

대상: 같은 “Ten criteria remain” 문장의 여덟 번째 항목 `capability/help/doc support parity`만 아래 조각으로 교체한다.

````text
capability/help/doc support parity for windows-1's exact supported and unsupported scope, logical-mode provenance and record-preservation boundaries
````

A3의 추가 단락 뒤에 아래 본문을 삽입한다.

````markdown
For criterion 8, align relevant preview, status, worker results, capabilities, help and documentation with the accepted windows-1 runtime scope and observed or unobserved environment tuples. Explain index-derived tracked modes, the explicit 100644 untracked/non-Git default, non-pass unknown/unsafe observations, the initial non-Git 100755 limitation, and common-condition worker eligibility. Include the mode-change/new-untracked-100755 limits and the distinct index-only tracked-add case. Preserve original-record reading, ordinary reject, pending recovery/cancellation and completed read-only replay. Identify Windows policy after detach only through a validated paired schema-4 receipt and its exact contract; do not infer a window from a bare digest or current host OS. Do not claim full Windows worker mode parity, POSIX permission equivalence or qualification of unobserved tuples.
````

### A5 — Windows Policy Identity

대상: [Structure — Product Inventory And Lifecycle](../development/CHECKOUT-1-STRUCTURE.md#product-inventory-and-lifecycle)의 Exact Managed Membership 다음·Plans, Bindings And Receipts 앞에 아래 절을 추가한다. 기존 shape와 역사적 window 목록은 덮어쓰지 않는다. window literal·membership 및 lifecycle schema/window pairs의 구체 목록은 A9에 제시한다. A5/A9의 의미와 적용 범위를 함께 수락해야 하며, 실제 reader/writer 검증은 여전히 필요하다.

````markdown
### Windows Successor Policy Binding

The windows-1 inventory window carries one accepted Windows content-mode policy across all its allowed releases. Existing ReleaseRef, Inventory and Binding fields carry that policy identity through the exact release/window and verified payload. Do not reinterpret an existing window by host OS or silently change this policy within the same window.

An installed writer selects the policy through its verified active binding, release, inventory and launcher/payload, and separately verifies actual native Windows/runtime conditions. Fresh source init requires explicit profile windows-1 and a verified windows-1 candidate; neither profile nor OS alone proves the candidate. The original canonical request/plan includes candidate_release with id, sha256 and inventory_id and binds the confirmation token. Exact recovery revalidates that same identity and original plan. Candidate or profile mismatch is non-pass before mutation, apart from existing guard-permitted scratch effects.

Windows detach uses only paired plan/receipt schema 4 under the Windows Window And Record Pairs clause. The unchanged fields retain prior binding reference, removal inventory and preservation inventory. Version 4 designates windows-1 even after product removal, only when the complete receipt, membership, digest and prefix checks pass. Historical versions 1/2/3 are not relabeled. A digest alone cannot recover deleted inventory bytes or the window name, and policy identification is not runtime qualification. Detached authority cannot be reinitialized or attached by this contract.

Use the exact membership and record pairs below. Unknown/inconsistent combinations or execution outside the Windows runtime scope remain non-pass with state preserved. Known cooperating old writers that can reach the candidate must be verified to refuse before authority/content publication. An unverified or unavailable refusal check for such an exposed writer, as well as an observed publication, prevents completion of candidate qualification and activation until an effective minimum refusal mechanism is verified or evidenced non-exposure removes that access path. Unknown exposure is not non-exposure. Bound the actual exposed-writer set and identities; this is not a requirement to recover every historical writer. A residual-risk label or usage warning is insufficient. Reaccept any changed persisted meaning, support scope or trust boundary; failure does not by itself prove a new field is necessary. Initial lifecycle is fresh and same-window only. Existing macOS defaults and historical meanings are unchanged.
````

A1–A15는 지정한 Windows clause만 보완한다. A9의 새 window/pair 의미를 제외한 root·record shape와 다른 accepted lifecycle·역사적 acceptance bytes는 보존한다. 아래 나머지 조항과 window/runtime 묶음을 포함해 exact 수락 대상을 정하며, 일부 문안 작성만으로 DR 전체 수락이 완료되지는 않는다.

### A6 — Windows Admission Timing And Native Scope

대상: [Windows Admission](../development/README.md#windows-admission)의 `After macOS Preview, select exact Windows 11...`로 시작하는 첫 정책 문단 전체를 아래 문안으로 교체한다. 앞의 source-only probe pointer와 ten-criteria 문장은 유지하며 5·8번만 A3/A4로 교체한다. A3/A4와 이 문단은 같은 amendment 묶음으로 수락한다.

````markdown
Formal native Windows admission follows live macOS Preview. Before then, source-only research and contract/plan preparation, and separately authorized isolated feasibility probes, may proceed. Product mutation requires the applicable accepted contract and execution authorization. Provisioning the account and environment remains the Owner's responsibility.

The initial policy targets native Windows 11 ARM64 with an ARM64 64-bit CPython process, and Windows 11 x64 with an x64 64-bit CPython process, on native local NTFS; standard-user execution is the qualification environment described below. Emulated architecture pairs, 32-bit processes, POSIX compatibility runtimes and other operating systems are outside this initial windows-1 scope. Native entry is an explicit absolute path to CPython satisfying Security And Support's Runtime And Scope (currently final, GIL-enabled CPython 3.14.6 or 3.14.7), with -I -B and the managed colvia launcher or independently trusted source. This can satisfy the native-launcher criterion without a POSIX shell or executable-bit assumption. Windows PowerShell 5.1 is the initial qualification target; it is not qualified by this statement. Do not add a .cmd wrapper or require PowerShell 7 without a separately selected scope.

Standard-user execution is the initial support/admission evidence boundary; elevated execution is not qualified here. It does not introduce an administrator-token refusal gate at every writer entry. Native local/guest NTFS is also an actual mutation-path requirement under Workspace Contract's Windows Native Observation And Publication, distinct from environment qualification. Actual OS/process/runtime admission remains a separate mutation gate. Record the actual edition/build, OS/process architecture, filesystem, shell, Git, CPython build, source/artifact and runner identity. Perform complete normal and parent-optimized regression and selected lifecycle qualification in the representative UTM guest. Assign focused x64 and physical-machine follow-up to concrete ABI, native API, process/launcher, locking and replace differences. Missing x64 or physical-machine evidence does not automatically create another full-suite or mandatory physical-machine gate; propose additional complete runs only with a concrete failure mechanism and why focused checks cannot resolve it. Preserve unobserved and unqualified tuple labels. Hosted x64 CI/mocks cannot replace real Windows acceptance, and runtime admission does not itself qualify an environment.
````

### A7 — Workspace Path, Lock And Publication Semantics

대상: [Workspace — Root Primitives](../WORKSPACE-CONTRACT.md#root-primitives) 끝, Record Encoding And Shape Boundaries 직전에 아래 절을 삽입한다. 기존 generic root/record 의미는 보존하고 Windows 한정 관측·잠금·발행 의미를 명시한다.

````markdown
## Windows Native Observation And Publication

These rules apply only to windows-1 on its admitted native Windows runtime. Keep the trusted-local-account/cooperating-writer boundary and existing Git topology, content membership and ignore scope. Examine the absolute ancestor chain from the volume root through the target and the ancestors/leaf of each path actually inspected. Refuse reparse points and indeterminate or unreadable classifications; do not treat them as ordinary paths or absence. Preserve existing hard-link, type, identity, case/normalization, reserved-name and trailing-dot/space constraints. Do not recursively inspect unrelated excluded content merely because this clause exists. Compare opened-handle identity with the path observation and repeat the required checks before writing. A final-path string alone is not proof against every alias or same-account race.

Before any filesystem mutation, verify native local NTFS for every path the operation will create, write, replace or remove: target authority/runtime and changed content, staging, lock/scratch and any external repair backup. Include existing files whose mandatory synchronization in that operation requires a write-capable handle, even when their bytes remain unchanged; do not add unrelated read paths or every retained release to that set. For an absent path, validate the actual volume and identity of its nearest existing ancestor and the admitted creation chain; revalidate newly opened/created paths before relying on them. Do not infer filesystem/locality from a drive letter, path string, guest label or profile. Remote, non-NTFS, indeterminate or inaccessible mutation paths are non-pass. Apply this check before creating guard scratch, repeat it under the writer guard and at the required publication boundaries, and retain the preceding reparse/identity checks. A same-account race can still cause later failure; preserve the actual prefix.

Each replacement source/destination pair must be on the same admitted volume. A separate external backup may use another verified native local NTFS volume under the existing outside-target/source and durable-copy rules; this is not permission for cross-volume replace. This mutation gate does not recursively scan unrelated content or add a new filesystem condition to otherwise permitted read-only inspection. Keep existing source/read-path checks. Do not add a fixed-drive-type restriction or administrator-token gate. Standard-user qualification evidence and actual filesystem admission remain distinct.

Cooperating writers share one stable anchor and the same byte range, offset 0 and length 1, using non-inheritable handles without delete sharing. Keep indefinite contention waiting and immediate same-thread reentry refusal; add no default timeout or takeover. An interrupt before entering the mutation section must leave no held lock/handle and no authority/content writes when the invocation exits. Normal scratch parents/anchor created while preparing to wait may remain. Do not promise that the lock was never transiently acquired. After mutation entry, interruption follows the actual publication prefix and existing recovery rules. Read-only inspection creates no anchor. Qualification must cover empty anchors, cancellation/acquisition races, process termination and handle cleanup; this clause does not promise an unobserved OS release-time bound.

Map each existing required or explicitly permitted-unavailable synchronization step to its Windows publication phase. Required failure or unavailable is non-pass; NTFS alone does not waive it. Do not silently promote a helper's permitted unavailable result into a new mandatory obligation. Preserve macOS-specific mandatory sync duties. File and required directory flushes use explicit results from appropriate write-capable handles. Preserve content-before-publication ordering and each call site's parent-sync requirement, including init launcher and immutable-member revalidation. API success observes that request's OS result, not power-loss persistence.

Distinguish failure before publication, after publication but before required flush, after required flush, and unknown phase/state. Preserve actual original, staged and published bytes; never report earlier publication as absent or automatically undo it. Diagnostic phase/API/error output is not a persisted receipt field. A later invocation re-observes durable records, bytes and identity and proceeds only within the original exact operation's admitted prefix. Read-only status/doctor do not reflush. A required reflush belongs only to authorized apply/recovery and is a new observation, not proof that the earlier flush succeeded.

Windows permission bits, ACL inheritance, read-only attributes and executable suffixes do not prove POSIX confidentiality or publication completion. Do not broaden ACLs or change ownership to make the operation pass. Determine completion from admitted prefixes, exact bytes/membership and binding/receipt relationships. If states formerly separated only by permission bits lack an independent durable distinction, preserve them as unknown/non-pass. Do not invent a mode value or receipt to force classification; a required new persisted distinction must be separately specified and accepted.

New files created by windows-1 writers, including managed runtime, authority, receipts, published content, staging/scratch and external backup files, must have native FILE_ATTRIBUTE_READONLY clear before publication/use as the new file. Read-only is not an immutability, confidentiality or completion marker. Do not normalize existing files, retained evidence or read-only sources to meet this creation rule.

Before the operation's first durable authority/content/receipt/backup publication, preflight the union of existing files it will replace/remove and existing files whose required flush needs a write-capable open, even without byte replacement. Refuse the whole operation if any such file has FILE_ATTRIBUTE_READONLY set; an unavailable or unsafe observation is separately unknown/non-pass. This includes init, update/rollback, repair, detach and intent/Work/worker/planning writes. The flush subset follows each operation's actual mandatory call sites, including admitted existing staging/receipt/backup revalidation where required, not all retained releases or read-only sources. Do not omit a required flush to avoid this gate or turn permitted-unavailable synchronization into a new obligation. Normal guard-preparation scratch may remain, but no authority/content or recovery backup may be published before this check succeeds. Repeat checks under the writer guard and before the relevant replacement/removal/required flush. During recovery check every remaining replacement/removal and every required reflush in the admitted original prefix, including already published files when that prefix requires their reflush; do not rewrite the request or published evidence.

Files only read or preserved unchanged, with no required write-capable flush, are not refused solely for being read-only under this mutation preflight. This exemption does not waive bound observations such as Windows Exact Repair Observation. Directory type, identity, emptiness and access rules remain separate; a file read-only flag is not a directory access test. If attribute/identity drift or an actual replace/remove/flush failure occurs after preflight, preserve the original request, backup, evidence and actual prefix. Never clear an existing target or evidence file's read-only flag, broaden ACLs, change ownership or use delete-then-copy to force success. Completed read-only replay keeps its existing exact observations and gains no mutation gate or reflush.

Replacement stays on the admitted filesystem and uses no delete-then-copy fallback. Automatic retries are zero. On access/sharing or other replace failure, report the actual phase, native error and observable old/new/staged state; unreadable is not absent. Explicit retry reuses the existing operation, request, token, candidate, recover option and prefix rules. It introduces no retry command, one-use token or automatic replacement preview. Preserve completed replay versus pending recovery. Existing authorization may cover the exact retry; this clause adds no repeated approval when action, target, inputs and prerequisites remain covered.
````

### A8 — Workspace Windows Lifecycle And Detach

대상: [Workspace Contract](../WORKSPACE-CONTRACT.md) 마지막에 아래 절을 추가한다. Actual Init And Recovery의 source profile/exact-active-repair 문장, Planning Preservation의 binding/current-writer 목록, 기존 switch·detach의 새 쓰기 version을 windows-1에 한해 아래 조합으로 한정한다. 기존 entry-1/First B1·역사적 source 의미는 보존한다.

````markdown
## Windows Fresh And Same-Window Lifecycle

Windows-1 admits fresh initialization and same-window update/rollback, exact active repair and receipt-bound detach under the existing preview/confirmation, pending, truth-preservation and exact-recovery rules. For windows-1 only, this clause qualifies the entry-1-only source-profile and exact-active-repair statements in Actual Init And Recovery (Development), the binding/current-writer list in Planning Preservation, and the new-write switch/detach version statements: source init/update/rollback/detach selects windows-1; repair has no profile option and requires the exact active windows-1 candidate; a verified applied windows-1 binding admits the same retained planning and current writer duties. It neither broadens an old source allowlist nor adds an OS gate to historical entry-1 source. No predecessor-to-windows-1 or cross-OS transition is admitted. An old window is not a fresh target; do not use detach/reinstall, receipt deletion or a replacement request to bypass that boundary. Existing macOS defaults and entry-1/First B1 semantics remain unchanged.

Fresh init requires explicit source profile windows-1, a verified candidate with inventory_id windows-1 and the admitted native runtime. The original plan's candidate release, format/home/target and canonical request token bind the operation before a binding exists. New init uses plan/receipt 1 and binding 1. Same-window switch uses paired plan/receipt 2 with both prior and candidate in windows-1; rollback selects exactly the recorded compatible prior release. Do not rank windows-1 above old windows to create an implicit migration. Repair uses the existing plan/receipt 1 shape, exact active candidate, external backup and unchanged binding; it preserves the existing narrow pending-record exception. Its FileObservation.mode uses Structure's Windows Exact Repair Observation, not the POSIX launcher-0755 rule. Bytes, namespace/identity, publication prefix and binding/receipt checks remain independent of that attribute observation.

All windows-1 lifecycle creation, replacement, removal and required synchronization follows Windows Native Observation And Publication's native local NTFS and read-only rules. New managed/authority/receipt files are created with read-only clear. Before the first durable publication, reject the whole operation if any existing file to be replaced/removed or opened with write capability for a required flush is read-only, including init and same-window repair/switch/detach. For detach this gate precedes .hrn/detached.json publication and covers the complete remove set plus any existing file with a required write-capable flush; recovery checks the admitted remaining suffix and required reflushes in the actual prefix. Preserve-only truth without such a flush is not rejected for its flag alone; all bound observations still apply. This is a Windows initial support restriction, not an automatic attribute-clearing transition or a proof that later races/failures cannot leave a partial prefix.

Windows detach uses paired plan/receipt 4 with the existing detach field set. Its candidate_release remains null. The expected/prior binding ref, exact managed remove inventory, preserved format/ignore/truth inventory, original target and operation remain bound as before. Reuse the existing complete path/digest/size lists: the remove set includes the launcher, product init plan, binding, every lifecycle receipt, and each retained release inventory plus its exact 29-path payload. Twenty-nine is the per-release payload membership, not the number of total removals. Preserve exactly the format/ignore and every truth-ref file under the existing scope; do not add arbitrary project files to removal. Only windows-1 releases using its fixed ordered membership may enter this detach plan; no historical-window mixture is admitted. Before first publication, verify the original binding and all release inventories establish that window, every planned digest and the complete removal/preservation set. Preserve size/reader-limit checks, pending barriers and exact prefix validation.

Publish .hrn/detached.json durably before any removal, then remove only verified listed files and verified-empty managed directories in the existing order. After any removal, validate the complete canonical plan/receipt pair: version 4 in both, action/operation/home, null candidate/result binding, expected/prior binding equality, exact ordered path/digest/size lists and their internal digest links. The remove list must still express the complete admitted layout: per-release inventory and exact fixed payload paths, release ID versus inventory digest prefix, expected binding digest versus its remove entry, and launcher digest/size versus an admitted retained payload launcher. Verify case/name/type, size and reader-limit constraints. These retained links are assertions bound before removal, not fresh hashes of files already deleted.

The receipt embeds the complete canonical plan. Read-only validation uses that embedded plan and the actual preserved/remnant state; it does not require a separate external original-plan file or confirmation token. Mutation recovery still requires the original exact request/token and original target under the existing operation contract. Retained plan fields do not authorize a writer merely because a reader can validate them.

Observe the actual filesystem independently. Every remaining removable file must match its listed bytes/size and the admitted removal-order suffix; every already removed path must be safely absent, never merely unreadable. After file removal, admit only the existing ordered directory-removal prefix and verified-empty managed directories. Preserved format/ignore/truth bytes and references remain exact and their current graphs retain the reader's existing validation scope. Changed preserved content, an unexpected occupant, unsafe absence or out-of-order remnant is non-pass. Mutation recovery also revalidates the original target and exact request/token; read-only clone auditing retains its existing exemption from the original filesystem path and gains no mutation right.

After inventory/binding removal, validated paired schema 4 and the fixed windows-1 contract identify the policy from this complete bound inventory and admitted actual prefix. A bare version, digest or count of 29 is insufficient. Deleted payload and metadata bytes cannot be rehashed or reconstructed from their hashes: their pre-removal validation is carried by the durable exact plan/receipt under the existing trusted-local/cooperating-writer boundary. Do not claim a new signature or hostile same-account tamper guarantee. A partial prefix resumes only through a compatible independently trusted windows-1 source and the original plan/token. A valid complete receipt supports read-only completed replay; it grants no new attachment, initialization or mutation. Unknown versions, mixed pairs, wrong membership, unsafe occupants or changed preserved bytes remain non-pass. Do not convert historical schema 1/2/3 receipts to 4.

Windows publication completion follows the Windows Native Observation And Publication clause. A successful primitive, parse, matching schema or policy label alone is not a completed lifecycle. Any state requiring a new durable marker must be specified and accepted before being implemented; this lifecycle clause does not authorize guessing a completed prefix.
````

### A9 — Structure Exact Window And Record Pairs

대상: [Structure — Exact Managed Membership](../development/CHECKOUT-1-STRUCTURE.md#exact-managed-membership) 다음에 넣는 A5 절 뒤, 기존 Plans, Bindings And Receipts 앞에 아래 절을 삽입한다. Common Types And Exact Bytes의 Window row, Plans, Bindings And Receipts의 window/rank·version 설명, Exact Repair Request의 mode 규칙, Detach Plan And Receipt의 새 쓰기/pair 문장을 windows-1에 한해 아래 절로 한정한다. 기존 entry-1와 역사적 값·bytes는 유지한다.

````markdown
### Windows Window And Record Pairs

For windows-1 only, this section extends the Window scalar in Common Types And Exact Bytes and qualifies the closed candidate-window, lifecycle-version and window-rank statements in Plans, Bindings And Receipts, the mode rule in Exact Repair Request and the new-write/pair rules in Detach Plan And Receipt. Add windows-1 as an admitted candidate/readable window only under these explicit pairs; it has no rank permitting transition to or from older windows. Existing entries and their historical meanings remain literal.

Windows-1 uses WORKSPACE_INVENTORY_ID = "windows-1" in the managed colvia launcher and explicit source profile windows-1. Its ordered managed membership is exactly the following 29 paths in UTF-8 order. The path set reuses entry-1; window identity and payload bytes are separate. Do not derive historical memberships from this list or silently add a module or wrapper.

Prepare and explicitly identify a Windows source/artifact whose launcher already contains that literal and whose payload bytes are fixed before candidate creation. Candidate construction reads and verifies those bytes; --profile windows-1 and the current OS do not synthesize or rewrite the literal/payload. Preserve the macOS default entry-1 input. The future build/packaging plan must identify the prepared Windows source bytes and any explicit preparation step from common source. Candidate packaging preserves those fixed bytes under the existing source/artifact equality rules; checkout conversion and runtime/profile selection do not rewrite them. The preparation mechanism remains a plan detail unless it changes accepted identity or support semantics, in which case exact acceptance is required. This clause selects no build mechanism and creates no artifact.

```text
.gitignore
AGENTS.md
CLAUDE.md
PRODUCT-CAPABILITIES.json
README.md
adapters/colvia-work/SKILL.md
colvia
docs/CONCEPTS.md
docs/GENERAL-WORK.md
docs/GETTING-STARTED.md
docs/GUIDED-INTENT-FORMATION.md
docs/MAINTAINING.md
docs/MANUAL-OPERATION.md
docs/OPERATIONS.md
docs/README.md
docs/REFERENCE.md
docs/SECURITY-AND-SUPPORT.md
docs/WORKSPACE-CONTRACT.md
src/hv2ref/__init__.py
src/hv2ref/candidates.py
src/hv2ref/cli.py
src/hv2ref/errors.py
src/hv2ref/intent.py
src/hv2ref/jsonio.py
src/hv2ref/product.py
src/hv2ref/umbrella.py
src/hv2ref/view.py
src/hv2ref/work.py
src/hv2ref/workspace.py
```

| Family/action | Windows-1 versions and binding |
| --- | --- |
| Root format / inventory / binding | 1 / 1 / 1; existing exact fields; release inventory_id is windows-1 |
| Init plan / receipt | 1 / 1; candidate windows-1, expected binding null |
| Update or rollback plan / receipt | 2 / 2; prior and candidate windows-1; existing exact same-window chain |
| Repair plan / receipt | 1 / 1; candidate equals exact active windows-1; unchanged binding; Windows Exact Repair Observation below defines mode |
| Detach plan / receipt | 4 / 4; candidate null; expected/prior binding ref and existing remove/preserve fields; windows-1 only |
| Intent, Work, manifest, ticket, decision, selection, current and planning | Existing family-specific versions and fields, including current parent revision forms; no new per-entry mode-policy field |

Do not treat schema 2 switch alone as a window proof: its release references must identify the admitted same window. Paired detach 4 designates windows-1 because that version admits no other window or membership. Verify the whole canonical plan/receipt, matching versions, operation/home/target, original binding digest, exact inventories and actual prefix. Before product removal, establish the window from verified release inventories; afterward validate the full retained removal/preservation lists, internal links and actual removal prefix under Workspace Contract's Windows Fresh And Same-Window Lifecycle. The fixed schema-4 contract retains policy meaning; it does not make removed bytes currently available for rehashing. Historical pairs remain literal and are never re-emitted as 4.

Windows-1 extends the existing narrowly defined unchanged-CRLF exception under the same retained text/eol=crlf proof, whole-tree and raw-byte rules. It does not admit changed converted files, changed attributes or arbitrary filters, or silently normalize inventory/manifest bytes. Qualification must establish this behavior under both autocrlf settings. Its declaration is not runtime evidence.

Every allowed windows-1 release must preserve records and fixed mode semantics in both read directions, including Q-created local/worker/parent/planning records after rollback to P and detach4 reading/recovery. Unknown or inconsistent pairs refuse mutation. An incompatible semantic change needs a separately accepted window/transition design; neither matching membership nor a new profile grants migration.

#### Windows Exact Repair Observation

This is a windows-1-only persisted meaning for the existing RepairFile.before/after FileObservation shape in repair plan/receipt 1. Select it only from the verified exact active candidate_release with inventory_id windows-1 and the unchanged binding, never from the current host, filename or integer alone. Other windows retain their original POSIX mode interpretation; do not rewrite historical requests.

For an existing safely observed regular file, mode is integer 1 when native FILE_ATTRIBUTE_READONLY is set and integer 0 when it is clear. Booleans, other integers and unavailable attribute observations are invalid here; do not derive it from stat permissions, extension, Git mode or the expected manifest. Observe bytes, size, attribute and identity consistently; an unreadable, unsafe or unstable observation is non-pass. A missing file still has before null, not a fabricated mode. sha256 and size_bytes continue to bind the exact raw bytes.

After bytes and size equal the exact active candidate. An executable repair request admits before null or an existing observation with mode 0, and after.mode is integer 0 for every path including colvia. Mode 1 remains a valid read-only observation, but if such a file needs replacement, preview reports unsupported/non-pass and produces no executable repair request/token; a supplied request containing that replacement is refused before durable publication. Preserving the pre-existing attribute applies only to writable files; this rule does not authorize clearing a target attribute. Before must differ from after. Read-only-only changes are not repaired or normalized, and no launcher-0755 requirement applies. This field does not represent ACLs, ownership, executable capability, TreeEntry logical mode or all NTFS attributes.

Recompute observations before apply and again under the writer guard. Initial apply requires each actual observation to equal its original before; authorized recovery permits only before or after under the existing exact prefix rules. Attribute drift is request drift even if bytes match. Never replace an original expectation with a new observation. Unlisted active files must already satisfy their exact candidate bytes/size and all independent product/prefix checks; their read-only flag is not a hidden executable-mode repair requirement. If an operation requires a write-capable flush of such a file, Workspace's separate preflight still applies; pure reading alone does not create that obligation.

The external backup retains canonical request.json and exact original byte files before replacement. Publish the existing repair receipt and select completion only after every actual target observation equals its after and all independent candidate-byte, active-product, binding and admitted-prefix checks pass. The request records original mode; the byte backup does not claim to preserve an ACL or all file metadata. Missing originals cannot be reconstructed from repaired bytes. Validate backup membership, byte digests/sizes and its exact request before recovery. Completed replay requires the complete existing backup/receipt, each actual target observation equal to its after and independent active-product/binding/prefix validation; a receipt or mode match alone is insufficient. Changing a bound repaired file from after.mode 0 to 1 makes completed replay non-pass even though replay is read-only; the mutation-preflight exemption does not waive these observations.

Prepare replacement files with the requested after attribute clear before publication. Before any backup/request/receipt/content publication, apply Workspace's whole-operation read-only preflight to existing replacement/removal files and existing files requiring write-capable flushes, together with its native local NTFS path checks. This includes existing external backup request/original files when exact recovery must reflush them; their unchanged bytes do not exempt them. Do not clear the original attribute, broaden ACLs, change ownership or use delete-then-copy to force replacement. Later attribute drift or failed publication preserves the exact request, backup and actual prefix as non-pass. No permission-only repair or success for every read-only target is promised. Attribute mismatch/failure never proves missing bytes or completed publication.

An exact retry/recovery keeps the original request/token, backup and before/after expectations. While an attribute differs from the admitted original before/after observation, the old request is refused. If the original attribute is restored externally, the original retry may be reconsidered only with every exact byte/observation, backup, candidate, binding and prefix check satisfied; restoration alone does not ensure success. This is not a product attribute-clearing action or an instruction to restore it. The external repair backup/receipt is evidence, not a pending node in the product binding-selection chain. A fresh preview is a separate read of current state: while any remaining damaged file requiring replacement is read-only, it is non-pass and produces no executable request/token. Only when no such replacement target remains and all current active-product, candidate, truth and existing pending guards permit it may a fresh preview produce an executable request. Do not bypass a real pending lifecycle/detach barrier; its apply must also pass Workspace's required-flush preflight. A fresh repair preview may also report a known read-only file requiring a write-capable open for that operation's mandatory flush as non-pass without mutation and without an executable request/token; this optional early diagnostic neither replaces apply's whole-operation preflight nor makes an issued token proof of apply admissibility. Use a new operation identity, canonical request/token and new external backup destination, retaining prior requests, original backup bytes and partial evidence until explicitly dispositioned. New apply requires authorization covering that exact request. It does not complete/cancel the prior attempt or reconstruct its original backup from repaired bytes. Do not automatically re-preview/apply or clear attributes as a fallback.

Qualify missing/damaged launcher/member cases, writable observations, whole-operation refusal of read-only replacement/removal and required-write-capable-flush targets before any durable publication, pure read-only preserved/unlisted files, attribute drift after preflight, failed replace/flush, interruption before/after backup and replacement, exact recovery and completed replay. Cover bound after-attribute drift on completed replay, existing backup files requiring reflush, and any original retry after external attribute restoration with all exact guards still required. Separately check fresh-preview refusal while a read-only replacement target remains, an admissible fresh preview with retained external evidence and new identity/backup, and refusal for actual product pending or another existing guard. Existing pending exceptions, preservation and two-direction windows-1 reader obligations remain. These are future product qualification requirements, not executed results or new automatic recovery actions.
````

### A10 — Security Runtime Scope

대상: [Security — Runtime And Scope](../SECURITY-AND-SUPPORT.md#runtime-and-scope)의 기존 CPython paragraph 뒤, Historical Observations 앞에 아래 단락을 추가한다. 기존 다른 window의 “OS gate가 아니다” 설명과 Windows 신규 scope의 차이를 명시한다.

````markdown
Runtime And Scope in this document remains the authority for the allowed CPython version/build-mode; the native-entry examples and admission text refer to it. Windows-1 adds an actual OS/process-runtime gate and the native local NTFS mutation-path gate to that requirement. Its initial policy permits native Windows 11 ARM64 with an ARM64 64-bit CPython process and Windows 11 x64 with an x64 64-bit CPython process on local NTFS. Standard-user local/guest NTFS is the initial supported qualification environment; elevated execution is not qualified. Standard-user evidence does not introduce a new administrator-token check/refusal at each writer entry. Filesystem admission is not evidence-only: before filesystem mutation verify actual native local NTFS for target, staging, lock/scratch, external backup, other written/removed paths and existing files with mandatory write-capable flushes under Workspace's Windows Native Observation And Publication; remote, non-NTFS and unknown paths are non-pass. Do not add a fixed-drive-type restriction. Emulated architecture pairs, 32-bit processes, POSIX compatibility runtimes and other operating systems are not admitted for Windows-1 mutation. Verify actual conditions; a profile name, executable path or version string alone is insufficient. Read-only diagnostics may report unsupported or unknown conditions without authorizing writes. This Windows-only restriction does not change existing macOS defaults or reinterpret old windows.

Policy scope is not environment qualification. State the exact observed edition/build, architectures, filesystem, shell, Git, CPython and artifact/runner tuple and any unobserved follow-up. Use the fixed windows-1 content-mode, worker-application, lifecycle and detach4 rules; do not claim full worker mode parity, POSIX permission equivalence, general same-account race protection or power-loss persistence. The existing explicit unchanged-CRLF exception is extended to windows-1 only with its unchanged proof and exclusions; qualification still must verify it. Never use current support prose to relabel historical evidence.
````

### A11 — Operations Native Entry And Recovery

대상: [Operations](../OPERATIONS.md) 끝에 아래 절을 추가한다. 기존 예시와 entry-1 transition 절은 해당 기존 window에 계속 적용한다.

````markdown
## Windows-1 Native Entry And Recovery

For a qualified windows-1 project, invoke the verified managed colvia file through an absolute allowed Python path with -I -B from native Windows PowerShell. Replace the illustrative paths with the exact qualified paths; do not copy them as installed locations:

```powershell
& 'C:\Runtime\python.exe' -I -B 'C:\Project\colvia' view
```

For independent source init/update/rollback/detach, retain --source-checkout and explicitly select --profile windows-1 together with the existing target, candidate and operation arguments. Source repair retains its existing interface and exact-active-source checks; do not invent a new repair profile argument. The profile selects a requested policy, while verified candidate/active release and actual runtime checks establish whether that request is admissible. Do not fall back to entry-1 or select a window from host OS alone.

Use only fresh or same-window operations. Retain original preview requests/tokens and compatible recovery source outside the target on durable storage before applying. Interrupted lifecycle uses its existing --apply --recover --input FILE --confirm TOKEN path where supported; worker acceptance uses the original work apply ticket and does not gain a lifecycle --recover option. Re-observe state and preserve unknown/torn bytes; automatic replace retry is zero. Existing exact authorization can cover the original retry without a new generic approval step.

Before mutation, apply Workspace Contract's actual native local NTFS path checks and whole-operation read-only preflight for existing files to replace/remove and existing files requiring write-capable flushes. New files are read-only clear; preserved/read-only source files are not normalized. For detach the complete remove set and any required-flush files must pass before publishing the detach receipt. Recovery includes required reflushes of the admitted existing prefix. Pure read/preserve exemption does not waive exact bound observations, and completed read-only replay gains no mutation or reflush. Later drift or failure still requires exact prefix preservation.

For repair, distinguish retrying the original exact request from preparing a separate request. If an attribute or other bound observation differs from admitted before/after, refuse the old retry without changing its token/backup or claiming success. External restoration of the original attribute permits reconsideration only if every exact byte/observation, backup, candidate, binding and prefix condition holds; it is not a product action, a restoration instruction or a success guarantee. External repair evidence alone is not a product pending barrier. While a remaining replacement target is read-only, a fresh preview is also non-pass with no executable request/token. Only when no such target remains and all current active-product/candidate/truth and existing pending guards permit it may a separate preview describe an executable repair. Its apply must satisfy the full Workspace preflight, including required flushes. Use a new operation identity/request/token and new backup destination, preserve prior originals/evidence and obtain the authorization required for that exact apply. Do not bypass actual pending lifecycle/detach, automatically re-preview, clear attributes, or treat the new result as completion of the old request.

Detach4 publishes the receipt first and preserves project truth and instructions as the existing detach procedure requires. After launcher removal, mutation recovery uses compatible independent windows-1 source and the same plan/token. Read-only validation uses the complete plan embedded in the receipt and does not require a separate external original-plan file or token. A validated complete detach4 identifies the windows-1 policy but does not certify runtime, prior flush outcomes or permit reinitialization. Keep useful manuals and any required exact recovery inputs outside the removal set. Historical detach1/2/3 retain their own reader/recovery scope; never reinterpret them from the current Windows host.
````

### A12 — Reference Windows Arguments And Failures

대상: [Reference](../REFERENCE.md) 끝에 아래 절을 추가한다. Source Utilities의 entry-1-only profile, Checkout Compatibility Limits의 current-source/switch2/detach3 설명과 Human Review의 current candidate/execution 문장을 windows-1에 한해 아래 범위로 한정한다. 기존 argument·input schema·exit precedence와 역사적 entry-1 source 의미는 유지한다.

````markdown
## Windows-1 Command And Failure Boundary

For windows-1 only, the explicit window/pairs in Structure's Windows Window And Record Pairs and Workspace's Windows Fresh And Same-Window Lifecycle qualify the entry-1-only profile statement in Source Utilities, the current-source and new-write version statements in Checkout Compatibility Limits, and the candidate/execution window statements in Human Review. Windows-1 source selects windows-1 for init/update/rollback/detach, uses same-window switch2 and detach4, and admits repair1 only against the exact active windows-1 candidate without a new profile option. Current-format planning follows the applied windows-1 binding. Retained historical entry-1 source and records keep their existing contract; this clause does not backport an OS gate or admit an old-window target through the new Windows path.

The windows-1 native entry is an absolute allowed Python invocation with -I -B and the verified colvia file; it does not require a POSIX shell, executable bit or .cmd wrapper. Independent source lifecycle uses explicit windows-1 profile where that command already accepts --profile. Preserve existing command names, --input file/stdin schemas, request/token semantics and exit-code precedence. A profile or filename alone is not provenance.

Before declaring Windows PowerShell 5.1 supported, verify the real product's argv, file/stdin inputs and exit codes, including required spaces, Korean text, quotes and metacharacters. Do not narrow the existing accepted input contract for portability. If preservation fails, report that shell path as unsupported and select an exact alternative or demonstrated existing input path before making a support claim; this clause does not install or mandate PowerShell 7.

Report policy-level unsupported, classification unknown, later drift/stale and actual publication/sync/replace failure distinctly. Preserve the native error and observable phase/state without adding a new persisted diagnostic field or silently mapping unreadable to absent. The diagnostic categories are not new CLI enum values. Read-only diagnostics do not repair or reflush. A matching old request/token is not proof that prerequisites remain valid or that a previous failed invocation made no change.

An existing read-only replacement/removal target or an existing file requiring a write-capable open for mandatory flush is policy-level unsupported for the whole proposed operation before its first durable publication; an unavailable filesystem/attribute observation is unknown. The required-flush subset follows Workspace Contract's operation-specific duties, including recovery reflushes, not all unchanged files. Later attribute changes are drift; actual replace/remove/flush failures report the observed phase and preserve the prefix. Native local NTFS applies to those actual operation paths, including guard scratch and external backup; a standard-user qualification label alone does not satisfy it. Pure read/preserve exemption never waives bound repair observations. While a remaining repair replacement target is read-only, a fresh preview is non-pass with no executable request/token. Original exact retry after external attribute restoration still requires all admitted before/after observations and exact backup, candidate, binding and prefix checks. A separately admissible fresh request uses its own identity/token/backup and existing exact authorization under Structure and Operations; no new command, automatic fallback or permission-clearing action is introduced.
````

### A13 — Maintaining Windows Qualification

대상: [Maintaining — Inventory Window Compatibility](../MAINTAINING.md#inventory-window-compatibility) 끝, Umbrella Candidate Boundary 앞에 아래 절을 삽입한다. 기존 normal/parent-optimized·reuse 정책을 면제하지 않는다.

````markdown
### Windows-1 Qualification Boundary

Windows-1 uses the exact Windows membership and record-pair contract, not the entry-1-only candidate declaration. Explicitly prepare/identify the Windows literal and payload before candidate creation without importing candidate code. Profile/OS selection does not rewrite payload bytes. Fix the prepared Windows source identity and verify exact source/artifact/published/refetched bytes under the existing equality rules. Identify any common-source preparation before that comparison; do not hide a transformation in packaging or runtime selection. Preserve historical memberships and current macOS defaults. A matching window, profile, schema or payload digest is not qualification. For windows-1 only, its explicit window/pairs qualify the current-writer and schema-3 statements in Checkout Proof And Detach Versions and Entry-1 Candidate Validation Boundary; those statements retain their entry-1 and historical meanings.

Fix each source/installed/retained writer and artifact identity for the selected compatibility matrix before execution. Verify new-window old-writer refusal before authority/content publication, including fresh targets and local/intent/worker/parent/planning/lifecycle paths; cover incomplete init, same-window switches and detach4 prefixes. For an exposed known cooperating old writer, both an observed publication and an unverified/unavailable refusal check block completion of candidate qualification and activation. Fix the actual exposure set and paths; unknown exposure cannot be claimed as non-exposure. Require verified refusal or an evidenced non-exposure boundary removing that access path; a warning or residual-risk label is insufficient. Any changed persisted semantics, support scope or trust boundary returns to exact contract acceptance. Do not claim every historical writer was checked from one unknown-window test, and do not require recovery of all historical writers when the bounded exposure analysis establishes that they cannot reach the candidate.

Qualify current-format integrity using the common worker condition and existing guards, including stable tracked modes, eligible untracked cases, index-only tracked additions, deletion absence, mixed unsupported results and prepare-to-apply drift. Keep original pending/replay/cancellation behavior, independent whole-result observation, original record bytes and macOS successful mode-change expectations. Verify same-window bidirectional reading, Q-created records on P, Windows Exact Repair Observation and its independent completion checks, detach4's complete post-removal inventory/internal-link/suffix/preservation validation, and the inability to initialize detached authority.

Verify native local NTFS admission for existing/absent target paths, staging, guard scratch, external backups and existing files with mandatory write-capable flushes; include non-NTFS/remote/unknown refusals, volume identity drift and same-volume replacement without imposing a fixed-drive-type or same-volume-backup rule. Verify new-file read-only-clear observations and whole-operation rejection before first durable publication for existing read-only replacement/removal or mandatory-write-capable-flush files. Distinguish pure preserved/read-only files from required reflushes in an admitted recovery prefix; retain required sync duties. Cover post-check drift, actual flush failure and interrupted prefixes in init/switch/repair/detach and authority/worker publication as applicable. For repair, cover completed-replay bound-attribute drift, exact retry eligibility after external attribute restoration, fresh-preview refusal while a read-only replacement target remains, and a separately admissible fresh preview with preserved old evidence, new identity/backup and existing authorization. Prove actual pending barriers still refuse the latter. These cases are part of the selected qualification scope, not extra mandatory full matrices.

Use a compatible qualified reader for detach4 evidence, including its embedded complete plan and post-removal state. Do not assume older readers were changed by this contract: an unsupported or unknown reader's output, including a false PASS, is not detach4 validation evidence. If such output was required for the qualification decision, the corresponding proof is non-pass until valid evidence is supplied. This read-only evidence disposition is distinct from the exposed old-writer publication/refusal gate.

Run the complete normal and parent-optimized regression plus focused lifecycle and macOS regression/reuse assessment under the existing evidence-selection rules. Use the representative native UTM full run and focused x64/physical follow-up allocation specified for Windows admission; add full runs only with a concrete mechanism and justification. Fix runner boundary, discovery/executed ID ledger, budgets and actual runtime tuple. Unavailable execution, skipped cases or unexpected failures are not passes. Historical probe timing or source inspection does not establish those product budgets or results.
````

### A14 — Manual Retained Windows Evidence

대상: [Manual Operation — Retained Evidence](../MANUAL-OPERATION.md#retained-evidence) 끝, Recovery Boundary 앞에 아래 단락을 추가한다.

````markdown
For windows-1, read original modes and canonical records without translating them from current host permissions. While the product is present, verify policy through the binding/release/inventory chain. After complete product removal, only a paired detach4 receipt validated under Workspace's Windows Fresh And Same-Window Lifecycle (complete remove/preserve path/digest/size lists, internal links, actual absence/prefix and preserved bytes) identifies windows-1 policy; the removed inventory's digest cannot reconstruct its contents. The receipt embeds the complete canonical plan. Read-only validation uses that plan and actual preserved/remnant state without requiring a separate external original-plan file/token; mutation recovery retains the original exact request/token and target requirement. Historical detach1/2/3 retain their original meanings, and unavailable policy provenance remains unknown rather than guessed. Reading retained evidence grants no new mutation, attachment or reinitialization. Use a compatible qualified reader to validate the receipt, preserved truth and admitted removal prefix. This contract cannot change older audit code: a reader that does not understand detach4 supplies no detach4 validation evidence, even if it prints PASS. If that output is required for qualification, the proof remains non-pass until compatible evidence is available; it is not an old-writer publication event.
````

### A15 — Getting Started And Managed Agent Entry

대상: [Getting Started](../GETTING-STARTED.md)의 Initialize A Fresh Project 앞과 [managed adapter](../../adapters/colvia-work/SKILL.md)의 Human Review Response 앞에 아래 같은 영어 단락을 넣는다. 이는 Windows 진입 설명이며 두 문서의 human authority·planning·기존 macOS 안내는 그대로 둔다. help/capabilities와 root entry의 대응 설명은 동일 범위를 사용해야 하며 실제 qualified tuple·artifact를 알기 전에 지원 완료 문구를 쓰지 않는다.

````markdown
## Windows-1 Entry

For a qualified windows-1 target, run the verified colvia launcher through an absolute allowed Python path with -I -B from native Windows PowerShell, then follow the verified view/manual paths as usual. For windows-1, this invocation replaces the generic ./colvia command prefix in the surrounding instructions; preserve the command arguments and human authority checks. Independent source lifecycle selects the explicit windows-1 profile and verifies the matching candidate and native runtime. Do not use a POSIX shell, executable-bit assumption, entry-1 fallback or an unverified interpreter alias to stand in for that entry. Fresh and same-window use follow the Windows contract; old-window/cross-OS migration and reinitializing detached authority are unsupported. Report the exact qualified tuple and any unavailable observations. These instructions do not accept an intent/result, authorize a writer or qualify the environment themselves.
````

## Windows Admission Criteria Mapping

이 표는 [현행 열 가지 기준](../development/README.md#windows-admission)을 현재 revision의 A1–A15 문안과 대응한다. 문서 대응은 실행 PASS가 아니다. S1/S7 및 S2/S6의 명시 범위는 named amendment 후보이며 나머지 기준을 면제하지 않는다. 현재 여섯 묶음 probe만으로 아래 기준이 완료됐다고 표시하지 않는다.

| 현행 기준 | 초안에서 다루는 의미 | 후속 qualification에 남는 검증 |
| --- | --- | --- |
| 1 · exact tuple | S1의 공통 정책과 실측/미관측 구별 | edition/build·architecture·native NTFS·shell·Git·final CPython·artifact/runner identity |
| 2 · native lifecycle | S2 최초 범위, S7 explicit Python 해석. exact repair는 S2가 추가하는 별도 Windows 의무이며 현행 criterion 2 열거를 소급 수정한 뜻이 아님 | POSIX shell 없이 doctor/init/status/update/rollback/detach의 preview/apply/refusal·보존 상태. 추가로 S2/A9의 same-window repair 관측·read-only 교체/필수 flush 사전 거절·read-only가 남은 새 preview 거절·exact retry·backup/replay 검증 |
| 3 · sync/replace/interruption 분류 | S4·S5·S8의 대기·취소·실패·복구 의미 | 실제 phase/API 대응, 필수/허용 unavailable, power-loss 과장 없는 결과 |
| 4 · 경로·이름·reparse | S3/A7의 실제 NTFS mutation 경로·ancestor chain과 unknown 거절 | target·staging·lock/scratch·backup의 native local NTFS 및 CRLF/case/reserved/trailing-dot-space/reparse 처리. 미존재 경로·volume drift·remote/non-NTFS 거절 |
| 5 · fresh clone/worktree와 current-format integrity | S2·S6의 지원 집합과 공통 mode 필요조건을 A3의 exact amendment로 제한 | 기존 모든 guard 아래 tracked 644/755 content-only, 자격을 만족하는 기존 untracked 644 변경·삭제, 새 untracked 644, tracked 삭제와 index-only tracked add. 예시는 닫힌 목록이 아님. mode-change·새 untracked 755·mixed-result의 새 decision/content 발행 전 전체 거절, prepare→index/membership drift→apply 거절, 실제 삭제 부재 검증 |
| 6 · abrupt termination/concurrency | S4·S5·S8의 exact retry 또는 stable non-pass; read-only 사전 거절 이후 drift/실패와 새 repair preview 구별 | 중단·동시 writer·open handle·실제 prefix, 원기록·기존 cancellation·pending barrier 보존. 외부 backup evidence와 실제 pending을 구별하고 read-only 교체 대상이 남으면 새 preview도 거절. 원 request 재호출·필수 재flush 대상 검사·bound replay drift 검증 |
| 7 · complete regression | S1 대표 UTM 전체 검증과 macOS 유지. S6 제한은 suite 축소 면제가 아님 | normal/parent-optimized 전체 regression, focused lifecycle, macOS regression/reuse 판정. Windows의 지원·거절 기대를 exact 수락 범위에 연결하고 기존 macOS mode 성공 기대 유지 |
| 8 · capability/help/doc parity | S1·S2·S6·S7의 지원/미지원·출처를 A4의 exact amendment에 대응 | 관련 preview/status/worker·capabilities/help/docs에 non-Git 755, worker mode-change·새 untracked 755 destination 및 rename/copy 파생 제한, 원기록·reject/recovery/replay 구분, 미관측 tuple 표시. 전체 mode 동등성 주장 금지 |
| 9 · checkout가 inventory bytes/digest를 암묵 변경하지 않음 | S2 exact membership, S6의 content mode와 inventory identity 구별 | 두 autocrlf 설정, CRLF 및 checkout 차이 아래 artifact/source/manifest/digest. mode 기본값을 이유로 원 artifact/manifest를 재작성하거나 digest 불일치를 면제하지 않음 |
| 10 · authenticated prerelease와 anonymous public 구별 | S1의 단계·증거 구별 유지 | 각 실제 전달 경로의 validation. private probe를 anonymous 증거로 대체하지 않음 |

native 표준 사용자·격리 경계는 유지하며 hosted x64 CI/mocks가 실제 Windows 증거를 대체하지 않는다. 관측하지 않은 edition/architecture, optional provider, Enterprise의 qualification은 여전히 없다.

## Open Points And Decision Order

B와 공통 조건 중심 worker 지원을 유지한 v0.10은 R1-D10 정적 리뷰에서 approve를 받았고, Owner가 2026-10-18 S1–S8과 A1–A15를 수락했다. 아래 표의 계약 선택은 확정되었으며 마지막 열의 구현·qualification 입력과 증거가 남아 있다.

| 수락한 계약 묶음 | 수락 값과 의미 | 구현·qualification에서 고정하거나 입증할 것 |
| --- | --- | --- |
| Window·reader 의미 | windows-1/profile, 기존 29 paths, init1/switch2/repair1/detach4, 기존 field와 Windows repair mode 의미 | exact 새 source/artifact·추가 실제 노출 old writer·source/installed/retained 조합. 기존 seed identity는 위 표에 명시 |
| Runtime·admission | native Windows 11 ARM64/ARM64·x64/x64 64-bit, final/GIL CPython 3.14.6/3.14.7, PowerShell 5.1 qualification, B 배정과 formal timing | OS/process/runtime 검사 방법, 정확한 환경 tuple와 실제 입력 보존. 미검증을 지원 완료로 표시하지 않음 |
| Path·lock·publication | A7의 실제 NTFS 경로·ancestor/non-pass, 새 파일 read-only clear·교체/제거 및 필수 flush 기존 파일의 전체 사전 거절, 안정 anchor·필수 sync·unknown prefix·자동 retry 0 | API/flag·호출 phase 대응표·오류 전달·중단 prefix·기존 obligation 보존. 새 persisted 구분이 필요하면 문안부터 보완 |
| Content·worker | A1–A4의 삭제 관측과 공통 필요조건, 비열거 tracked add·eligible untracked, whole-result·기록/replay 보존 | classification/특수 flag·physical state·발행 전 재검증·실제 성공/거절 fixture |
| Detach·old writer | A5/A8/A9의 paired4 inventory·제거 후 검증과 역사 보존, 노출 writer의 거절 실패·미확인 때 qualification/activation 중단 | 제거 전·후와 중단 suffix, 내부 digest 링크·preserve bytes, 실제 노출 writer 거절 또는 검증 가능한 비노출 근거 |
| Repair mode·retry | A8/A9의 read-only 관측 0/1, 실행 request는 before null/0·after 0, 원 request retry와 별도 새 preview 구별 | whole-operation 교체/제거·필수 flush 사전 거절, read-only가 남은 새 preview 거절, 외부 backup·pending·bound replay drift·양방향 reader 검증 |
| Exact amendment 범위 | A1–A15의 target·삽입/교체 문안과 유지 조항 | 통합 baseline drift, 11-member 기술 계약 및 관련 설명의 최종 bytes/parity |

다음 대상은 [후속 계획](../development/windows-native-implementation-plan.md)의 review와 실행 승인이다. 이미 수락한 계약을 반복 수락하도록 요구하지 않는다. source/artifact digest와 실행 결과는 구현·qualification 뒤에 고정하며, 선택하지 않은 scope·persisted 의미·reader 호환을 구현 편의로 추가하지 않는다.

계약과 계획 세부는 함께 문서로 준비할 수 있다. API 선택 등 의미를 바꾸지 않는 매개변수마다 반복 승인을 만들지 않는다. 알려진 old-writer 실패를 문서만으로 통과시키거나 새로운 field/format을 자동 채택하지도 않는다. 이 문안에 없는 실제 publication prefix를 구현 과정에서 발견하면 필요한 exact 의미를 제시한 뒤 그 부분을 진행한다.

v0.10의 R1-D10 결과와 Owner 수락은 위 dated 기록을 따른다. 비채택 디렉터리 파일-flag gate와 repair receipt 위치 변경, defend한 completed replay 변경은 여전히 제외한다. 이번 요청은 수락 기록과 계획 준비까지이며 추가 probe·제품 구현·제품 suite·실제 Windows qualification과 Git publication은 시작하지 않는다.

## Promotion Conditions

- 완료: B와 공통 조건 중심 worker 방향을 유지한 v0.10 S1–S8·A1–A15를 Owner가 exact 수락했다. 근거는 2026-10-18의 명시 요청이며 review verdict만으로 수락 처리한 것이 아니다.
- 이번 revision에서 값과 문안이 마련된 항목과 실제 qualification이 남은 항목을 구별한다. 선택한 scope·persisted 의미·reader 호환·필수 sync 의무가 바뀌면 관련 문안과 수락 범위를 갱신한다. future artifact digest를 가상으로 채우거나 runtime 값을 이미 유효하다고 표시하지 않는다.
- 계약 정적 리뷰 R1-D10은 완료되었다. 후속 계획 R0와 구현 결과 R1은 기존 source procedure를 따르며 이번 계획 작성 승인으로 reviewer를 자동 호출하지 않는다.
- 계약·계획 문서 준비는 함께 할 수 있다. 제품 mutation은 필요한 계약 수락과 실행 승인 뒤에 한다. exact integrated candidate의 qualification·Owner 결과 수락과 별도 activation, live macOS Preview 이후 Windows formal admission을 구별한다.
- known exposed old-writer의 발행 또는 거절 미확인, unresolved unsafe/unknown state, missing required qualification을 잔여 위험 label이나 미지원 표기만으로 통과시키지 않는다. 이전 계약·review·원출력·acceptance bytes와 pending/완료 기록 의미를 보존한다.

실측 결과 수락, 계약 수락, 제품 실행 승인, 결과 수락/activation, 공개 admission/publication은 각각 대상과 범위를 식별한다. 같은 Owner 메시지가 여러 범위를 명시할 수 있으나 하나를 다른 것으로 추정하지 않는다.

## Verification And Limits

2026-10-18 수락 기록·계획 준비에서는 수락된 S1–S8과 A1–A15 raw 본문·이전 Owner 인용·개정 이력의 불변, R1-D10 exact 입력 복구, catalog/navigation의 한정 변경과 문서 렌더링·링크를 확인한다. 아래 v0.10 작성 검증 설명은 당시 수행한 범위를 보존하며 이번 작업을 새 제품 실행으로 해석하지 않는다.

이번 v0.10 작성 검증은 R1-D09 처분에 따른 현재 상태 문구 세 곳의 실제 리뷰 이력, A9 선택 조기 진단의 fresh repair preview 범위와 non-pass 시 실행 request/token 부재를 확인한다. 나머지 A1–A15 본문과 기존 defend 처분, B·worker 공통 조건이 유지되는지 비교한다. GFM 렌더링·code 밖 literal 강조 기호·local link·whitespace·disclosure·제품 diff도 검사한다. A1–A15의 exact 영어 본문이 fence 안에 모두 들어 있는지 확인하고, fence 구분자만 제외한 raw 본문을 trim·후행 공백 정규화 없이 메모리상의 target 사본에 적용해 전체 삽입 bytes·위치·렌더링을 검사한다. text 조각은 구분 newline을 제외한 한 줄을 그대로 교체하며, 실제 normative 파일은 수정하지 않는다. 이 문서 검증은 의미적 완전성이나 제품 실행 성공의 증명이 아니다.

기존 R0/R1-P01/R1-D01–D10 원문과 frozen packet을 보존한다. 이전 v0.1–v0.10 exact bytes는 각 대응 Draft review packet에서 복구할 수 있다. 수락 기록과 계획 준비의 입력·bounded diff는 수락 identity와 후속 검토를 위해 보존하며, 재현 가능한 일회성 작성·검사 산출물은 검증 뒤 정리한다.

이번 수락 기록과 계획 준비에서는 제품 suite, VM 재실행, 신규 architecture/shell/API 관측, reviewer 호출과 제품 계약 activation을 수행하지 않는다. windows-1/native runtime/detach4와 repair mode 의미는 수락되었지만 아직 미구현·미검증이다. source의 구조와 읽기 경로를 확인했다는 사실을 Windows 실행 PASS로 표시하지 않는다. 실제 문서 검증과 revision identity는 기존 진행 정본의 dated 기록에 남긴다.

후속 제품 계획은 exact tuple·source/artifact·runner boundary·고정 discovery/executed ID ledger·normal/parent-optimized budget과 macOS regression/reuse 판단을 명시한다. 이전 6-family probe 시간은 제품 suite 예산이 아니며 clipboard integration·restore boot 미관측 등 기존 경계는 해당 qualification에서 별도 처분한다.

## Reversal Cost

현재는 계약만 수락했고 새 durable 제품 기록은 없으므로 구현 전 변경 비용은 비교적 낮다. 다만 수락된 의미를 바꾸려면 named amendment와 Owner 수락이 필요하며 ID는 재사용하지 않는다. 수락 후 새 window/schema·mode 의미가 durable record로 사용되면 High: old/new reader와 lifecycle 경계가 생겨 단순 rollback으로 되돌릴 수 없다. explicit Python 진입과 retry 0회 정책만의 문서·구현 선택은 상대적으로 작지만, 이미 발행된 기록의 의미 보존은 별개다.

## Decision

2026-10-18 Owner는 검토된 v0.10의 S1–S8과 A1–A15를 다음 묶음으로 수락했다. 정확한 영어 amendment와 placement는 위 A1–A15가 정본이며 이 요약이 본문을 대체하지 않는다.

| 계약 | 수락한 선택 |
| --- | --- |
| S1 | B안: 대표 UTM 전체 검증과 필요한 x64/물리 focused 보완, 정책 범위와 실제 tuple 구별, live macOS Preview 뒤 formal admission |
| S2 | windows-1 fresh·same-window lifecycle, 29 paths와 init1/switch2/repair1/detach4, 기존 창 이주 제외 |
| S3 | native local NTFS와 실제 ancestor·reparse·identity 관측, 불명확한 상태의 non-pass |
| S4 | stable anchor의 timeout 없는 잠금 대기, 상속·교체 방지와 취소 의미 |
| S5 | 필수/허용 unavailable flush 의무와 실제 publication 상태, unknown·중단 복구의 구별 |
| S6 | read-only 관측·생성/교체/제거/필수 flush 사전 검사, index/default mode·실제 삭제, 공통 조건 중심 whole-result worker 지원 |
| S7 | 절대 Python 경로의 native 진입, PowerShell 5.1 입력 계약의 실제 qualification |
| S8 | 자동 replace retry 0회, 원 request/token·exact candidate의 기존 recovery, 새 preview와 원 retry 구별 |

A1–A15는 content·worker·admission·window/pair·runtime·lifecycle·사용법·qualification·retained evidence의 named 변경 본문으로 수락한다. 이를 실제 source·문서·artifact에 통합하는 실행과 activation은 위 남은 조건을 따른다.

## Rationale

B는 대표 환경의 충분한 전체 검증을 유지하면서 메커니즘 차이에 맞춰 보완 증거를 배정한다. Windows 전용 window는 macOS의 과거 기록과 새 mode/repair/detach 의미를 구별한다. worker는 개별 사례의 닫힌 목록 대신 독립 post-mode/부재 관측과 whole-result 공통 조건으로 경계를 정한다.

기존 probe와 R1-D01–D10·Driver 처분을 통해 문안의 범위와 미결 의미를 정리했으며 마지막 R1-D10은 approve였다. 이 근거는 계약을 선택하는 데 쓰였고 Win32 API나 통합 제품의 정확성·내구성·지원 qualification을 대신하지 않는다.

## Consequences

후속 구현·검증은 수락된 S1–S8과 A1–A15를 기준으로 수행해야 한다. shared writer·snapshot·lifecycle과 exact source preparation, Windows/macOS 회귀 및 old-writer 노출 검증이 필요하다. 노출 old-writer 거절 미확인·필수 관측 unknown·qualification 누락을 남긴 채 activation하지 않는다.

현재 entry-1·First B1 activation과 역사적 acceptance bytes는 유지한다. Windows 구현 결과 수락·exact activation·formal admission·Git publication·adopter 적용을 각각 식별하며 이번 계약 수락으로 자동 승인하지 않는다. 기존 실험 결과 수락이나 VM recovery 정리도 이번 범위에 포함하지 않는다.


## Windows Integration Amendment 01 — Accepted 2026-10-22

Owner는 `windows-integration-amendment-01.md` SHA-256 `583631d754b0fa962fd8944ecbdf0abdc29519c280c99a8cd26d0d5094bba760`에 대해 “개정안 수락, 기존 통합 작업에 반영”으로 응답했다. 기존 S1–S8·A1–A15의 역사적 수락 bytes를 보존하며, 다음 통합 후보에 한해 아래 exact amendment를 적용한다. 구현·문서 통합은 이미 승인된 Work에서 계속한다. qualification·결과 수락·activation·admission은 별도이며 아직 완료되지 않았다.

1. Introduce inventory_id/source profile `windows-2` for the Windows integration successor. Do not redefine `windows-1` or relabel its original source, artifacts, receipts or evidence. The common macOS source retains `continuation-1`. A prepared Windows source declares `windows-2` explicitly before candidate construction; profile or host detection never rewrites payload bytes.
2. The windows-2 ordered managed membership is exactly the 30 paths listed below, matching the literal continuation-1 membership at main `7d012f5297de1d9a77aa0b8187406f4785221573`. Its launcher module allowlist includes continuation.py and has 12 Python modules. Preserve every historical membership literally. Equal membership does not imply equal window or policy.
3. All new windows-2 init, update, rollback, exact repair and detach plans AND receipts use paired schema 6. Reuse the corresponding current continuation-1 schema-5 field shapes and operation guards, with windows-2 references and schema 6; do not change existing schema-5 semantics. Reject mixed versions and unknown schema/action/window pairs. Root format, binding and inventory retain their existing exact schemas.
4. Admit native Windows fresh init and windows-2 same-window lifecycle only. No entry/delegation/continuation/windows-1 migration, cross-OS update, cross-window rollback or detached-authority reinitialization is added. New windows-2 source must not resume historical operations under schema 1–5. Retain exact compatible historical source/request/token for their original recovery. When old Windows evidence cannot be unambiguously classified, preserve it and report unavailable; do not interpret its detach4 as delegation evidence or the reverse. Existing main historical readers retain their original supported scope.
5. Preserve DR-0007's accepted native Windows environment gates, explicit absolute Python -I -B entry, local NTFS restrictions, replacement/flush duties and failure distinctions, whole-operation read-only preflight, B option, worker common-condition limits, logical content modes and unchanged-CRLF proof. Apply those policies to windows-2. For windows-2 repair schema6 only, FileObservation.mode remains the native read-only observation integer 0/1 selected from the exact verified active windows-2 release, never the host or integer alone. Existing windows-1 repair1 retains its historical meaning.
6. Include the accepted delegation and U1 behavior of the pinned main, including delegated intent/Work reading and publication, immutable continuation history/current, project-wide pending/integrity refusal, quota and truth preservation. Keep their existing authority boundaries and record schemas. Apply Windows durable-publication/preflight requirements to their new writer paths too. Lifecycle observation caching from main must preserve Windows native observation and publication guarantees. No U2 host automation, new permissions or scheduler is included.
7. A complete schema6 detach identifies windows-2 only after validation of the complete canonical plan/receipt pair, exact removal/preservation membership, linked digests and actual prefix/preserved bytes. It is not environment qualification or proof that every historical flush succeeded. Original complete/pending/recovery obligations remain, now with continuation truth preserved. Validate both read directions for permitted windows-2 P/Q releases, including Q-created delegation/continuation records after same-window rollback to P. Never re-emit historical pairs as 6.
8. Before final qualification, fix the exact prepared source and candidate identities and the exposed predecessor writer set. Verify pre-publication refusal by accessible entry/delegation/continuation/windows-1 writers and wrong-profile/schema pairs, including receipt-only and interrupted prefixes, or retain a verified non-exposure boundary where the original contract permits it. Reuse unaffected historical evidence with its identity and scope; the new window/schema/inventory and new Windows writer paths require fresh evidence. Focused integration checks precede the separately bounded final matrix. No test result alone accepts the result, activates the contract or grants Windows admission.

### Exact Ordered Membership

```text
.gitignore
AGENTS.md
CLAUDE.md
PRODUCT-CAPABILITIES.json
README.md
adapters/colvia-work/SKILL.md
colvia
docs/CONCEPTS.md
docs/GENERAL-WORK.md
docs/GETTING-STARTED.md
docs/GUIDED-INTENT-FORMATION.md
docs/MAINTAINING.md
docs/MANUAL-OPERATION.md
docs/OPERATIONS.md
docs/README.md
docs/REFERENCE.md
docs/SECURITY-AND-SUPPORT.md
docs/WORKSPACE-CONTRACT.md
src/hv2ref/__init__.py
src/hv2ref/candidates.py
src/hv2ref/cli.py
src/hv2ref/continuation.py
src/hv2ref/errors.py
src/hv2ref/intent.py
src/hv2ref/jsonio.py
src/hv2ref/product.py
src/hv2ref/umbrella.py
src/hv2ref/view.py
src/hv2ref/work.py
src/hv2ref/workspace.py
```


수락 응답 시각: 2026-10-22T01:36:36.587134Z. 위 proposal SHA의 원문 상태 표시는 당시 Proposed를 유지하며 수락된 exact bytes의 의미는 이 수락 기록으로 결속한다.


## Windows Verification Amendment 02 — Accepted 2026-10-28

Owner는 2026-10-28 FEAT-20261018-003의 야간 실행안 전체를 명시적으로 승인했다. 수락 대상 계획 SHA-256은 `750d7ed99c6331c0776611fe53b85e74f449354d367c7d6e3a92ee18fb814b0a`, 고정 선택 목록 SHA-256은 `433c7664ab620f808e126d18bf70d058740924f6991f75267bc152f6fed9cf88`이다. 이는 검증 방식 개정의 수락·발효이며, 실행 결과 수락이나 Windows admission은 아니다.

변경한 조항은 S1, A3의 검증 범위 단락, A6의 대표 검증 배정, A13의 Windows qualification, criteria 6–9 중 normal/parent-optimized 전체 반복 요구 및 criterion 7 대응이다. 같은 요구를 담은 Maintaining의 Windows-2 절과 구현 계획 P4/V11에 한정한다. 원 S1–S8·A1–A15, v0.10 수락 및 Amendment 01의 원문과 다른 의미는 보존한다.

이번 지정 ARM64 UTM·GIL-enabled CPython 3.14.7·일반 사용자·local NTFS의 Windows-2 후보와 승인된 한정 보정에만 다음을 적용한다. normal 전체 적용 대상은 source-aware 누적 원장으로 대사하고, parent-optimized 전체 반복은 고정 133개 ID와 실제 guest compile/import 비교, source·installed 명시적 -O 정상/거절, 자식 mode 관측, qualified auditor의 명시적 -O 정상/손상 검증으로 대체한다. 제어기·독립 oracle은 normal이다. 여섯 final P/Q 사례는 같은 고정 artifact에서 실행했을 때 중복 없이 재사용한다. 실행·상속·제외/별도처분·미해결을 분리한다.

공유 fixture·assertion·discovery·dependency·runner·isolation 및 누적 제품 변경의 영향을 평가하고 필요한 실제 집중 검증으로 해소한다. macOS 기존 normal/-O 전체 근거와 후속 영향 검증, 노출 old-writer 거절, 중단/경쟁/복구, qualified reader, exact bytes 및 나머지 안전 기준은 유지한다. 최적화 민감 분기·runtime/dependency/flag 변경·설명되지 않는 mode/import 차이·사라지는 필수 oracle·넓은 공유 변경·근거 복구 불가이면 해당 재사용을 확정하지 않고 필요한 전체 영향 범위를 실행하거나 미완료로 보고한다. 미래 후보 면제·지원 확대·activation·publication·adopter 적용·결과 수락을 허용하지 않는다.

정확한 실행 범위·한도·결과는 [기존 Work](../development/FEAT-20261018-003-windows-native-implementation.md), 일반 규칙에 대한 한정 예외는 [Maintaining](../MAINTAINING.md#windows-verification-amendment-02--accepted-2026-10-28)에 연결한다.
