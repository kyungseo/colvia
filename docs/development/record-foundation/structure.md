# Record foundation structure

Status: implementation design draft. This document explains module ownership and rationale; it does not activate a new runtime format. The [task](../FEAT-20261106-002-record-foundation.md) owns progress, [design](design.md) owns the proposed store contract, and [runtime/extension](runtime-and-extension.md) owns install and adapter requirements. Private comparison names and historical delivery metadata are not product dependencies.

## Layers And Dependencies

제안서의 화살표는 사용자 흐름으로는 유용하지만 import 순서와 같지는 않다. 아래쪽이 UI·Git·OS를 알지 않는 의존 방향으로 고정한다.

```text
CLI / View / agent entry             Composition root
           │                              │ 조립
           ▼                              ▼
Application: Work, acceptance, query, lifecycle services
           │             ▲
           ▼             │ ports 구현
Domain / schema / ports  ◀── storage, Git/non-Git observation,
                              platform, provider, notification adapters
```

| 책임 | 소유 모듈(역할명; 파일명은 구현 시 확정) | 금지 사항 |
| --- | --- | --- |
| Work·수락·참조 의미 | Domain/schema | OS·Git·앱 이름에 따른 결정 의미 변경 |
| 정본 찾기·프로젝트 identity | Authority resolver | branch/remote 이름만으로 정본 추정, 구 사본 자동 승격 |
| 작업 폴더와 앱 worktree 경계 | Workspace topology | `.claude` 이름만 보고 통째로 무시 |
| 파일 집합·내용·정책 관측 | Observation service와 Git/non-Git adapter | 명령마다 별도 ignore 해석, 정책 변화와 내용 변화를 혼합 |
| 불변 객체·head·transaction·복구 | Store service | 두 정본 쓰기, index/cache를 독립 권위로 취급 |
| 실행·제출·수락 조합 | Application services | 직접 UI 출력·provider 호출을 domain에 삽입 |
| 현재/과거 결과 조회 | Query service | 부분 조회를 전체 무결성 검사라고 표시 |
| provider·알림·플랫폼 효과 | Capability adapters | Core 수락을 모델 판단이나 알림 클릭으로 대체 |
| 설치·진입 안내 | Packaging/composition/agent entry | 소스 개발 지침을 설치 프로젝트에 자동 주입 |

같은 개념의 검증을 한 곳에서 수행하되 필요한 경계의 재검사는 삭제하지 않는다. Application은 ports에 의존하고 구체 adapter는 composition root가 연결한다.

## S1–S11 Disposition

| 항목 | 처분 | 조건 |
| --- | --- | --- |
| S1·S2 | 채택 | 위 층/책임표로 의존 방향 수정. 구현 뒤 import 경계와 중복 의미 검사 |
| S3 | 보완 채택 | 정본 하나·파생 index 재생성. export는 복구 checkpoint이며 마지막 복구본일 수 있으므로 cache처럼 삭제하지 않음 |
| S4 | Owner 방침 반영 | 새 형식으로 신규 연결. 공개/비공개 legacy reader·converter 신규 개발과 구 이력 자동 이관은 제외. 미래 unknown version 거부와 잘못된 store 쓰기 차단은 유지 |
| S5 | 기존 선택형 실행 유지 | 플랫폼별 기본 진입 하나. 기존 공식 실행을 선택 모듈로 유지한다. 제거 결정은 별도이며 이름 정리만으로 현재 기능을 빼지 않음 |
| S6 | 보완 채택 | 완료 Work를 보관해도 검색·본문·결정·후속 연결은 그대로. checkpoint 파일 hash만으로 참조 대상의 현재 무결성을 증명하지 않음. 접근 시 객체 검증·결정의 의존 관계 검증·명시적 전체 감사가 필요 |
| S7 | 채택 | 사용자/에이전트/개발 기록 분리. 첫 진입은 읽을 순서와 핵심 계약만; 초기 진입20–40줄, 첫 skill60–100줄은 편집 목표이며 안전 계약을 삭제하는 하드 한도 아님 |
| S8 | 채택 | 11-04 감사6건 재사용: 공개 allowlist·시험 종속성, 문서 아래 실행 도우미, 설치본 조건부 링크, 이름/버전/지원 역할, 합성 배포물 제외·재현 가능 빌드, 신고·갱신 운영 경로. 과거 수치를 현재 상태로 재검증했다고 표시하지 않음 |
| S9 | 채택 | [정적 기준값](measurements.md#static-baseline-and-new-inputs)과 현재 측정 보존. 문자열 빈도를 실제 분기 수나 품질 점수로 오해하지 않음 |
| S10 | 채택 | 개발용 AGENTS/CLAUDE와 설치 프로젝트용 entry 분리. 현재 기능은 기능 이름, 과거 이름은 비공개 이력. 버전 식별·dependency/법적 고지를 기계적 검색0 목표로 삭제하지 않음 |
| S11 | 네 조건 모두 채택 | 공용 authority, Work별 context/head, 충돌 검사·CAS, 내부 ID/제목 분리, workspace별 scope. 실행 병렬화·여러 clone 병합은 포함하지 않음 |

## Archive And Integrity

보관은 상태·탐색 정책으로 설계하고, Work를 삭제하거나 요약문으로 대체하지 않는다. 실제 locator가 안정되기 전 파일을 임의로 옮기지 않는다. 과거 수락을 취소하거나 재개할 때도 새 사건/선택을 추가하고 봉인한 과거 bytes를 고치지 않는다.

봉인 체크포인트를 그대로 둔 채 그 안의 파일을 바꿀 수 있으므로, 체크포인트 hash만 보는 방식은 매번 전체 검증과 같은 보장을 하지 않는다. 불변 content-addressed 객체, 읽을 때 hash 확인, 결정 시 참조 closure 검증을 결합하고, 전체 감사와 일반 조회의 보장 범위를 구분한다. archive는 자동 GC가 아니며 공간 감소를 약속하지 않는다.

이번 기록에는 명령 전체 시간이 있고 내부 단계별 profiler가 없다. 파일 관측·전체 그래프 검증·실행기 해시 비용의 비율을 나눠 계산할 수 없다. managed 실행기 비용도 이번 source/Python 측정으로 대신하지 않는다. 당시 종료된 측정에 몰래 추가하지 않았으며, 이후 별도 [집중 진단](diagnostics.md)에서 시간 분해를 완료했다. 새 managed 실행기 비용은 여전히 별도 검증이다.


## Current corrections and compatibility

The earlier unmeasured profiling gap is resolved by [diagnostics](diagnostics.md); the OS-data authority policy has since been adopted and [C1–C8](implementation-contracts.md) now specify the detailed R2 treatment. Actual host access and implementation qualification remain open. The [R1 disposition](review-disposition.md) is historical. The labels S1–S11 identify design topics, not external source dependencies.

Pre-public trial migration/readers/profile compatibility are excluded. New connection, capability/version management, update, failure recovery and detach remain required. The first public release begins the obligation to preserve records, settings, bodies and human acceptances. Existing bounded worker/umbrella, execution/cancellation and notification semantics are not discarded for schedule reasons. Future parallel execution is separate from concurrency-safe record identities and transactions.


## Structural Topics In Plain Terms

S1 defines layers and dependency direction; S2 assigns each identity/observation concept one owner; S3 separates authoritative records from regenerable projections while protecting last recovery exports. S4 removes pre-public compatibility obligations, not first-public update protection. S5 provides one ordinary entry per platform with separately managed optional capabilities. S6 makes bounded verification and preserved archived history part of the record design. S7 separates user, agent and maintainer documents. S8 requires self-contained public source/tests, correctly placed reusable helpers, installed links, distinct product/version/support identities, reproducible release assets and support/update operations. S9 measures the old implementation before comparing replacements. S10 separates source-development and installed-project entry. S11 preserves common authority, Work/workspace identities and CAS/conflict information without implementing parallel scheduling. These definitions supersede any need to consult a private proposal to understand the table.
