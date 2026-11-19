# Record foundation structure

Status: implementation design draft. This document explains module ownership and rationale; it does not activate a new runtime format. The [task](../FEAT-20261106-002-record-foundation.md) owns progress, [design](design.md) owns the proposed store contract, and [runtime/extension](runtime-and-extension.md) owns install and adapter requirements. Private comparison names and historical delivery metadata are not product dependencies.

English reference, 2026-11-19. The [original wording at the translation base](https://github.com/kyungseo/colvia/blob/eed271ad5aa665f0002c9eded69d82f224da9ce0/docs/development/record-foundation/structure.md) governs the dated decisions and evidence. The Owner [accepted this English reference](../document-language-result-review.md#owner-acceptance).

## Layers And Dependencies

The proposal’s user flow and the import graph serve different purposes. The arrows below show the fixed dependency direction. Lower layers do not depend on the UI, Git or the operating system.

```text
CLI / View / agent entry             Composition root
           │                              │ wires adapters
           ▼                              ▼
Application: Work, acceptance, query, lifecycle services
           │             ▲
           ▼             │ implement ports
Domain / schema / ports  ◀── storage, Git/non-Git observation,
                              platform, provider, notification adapters
```

| Responsibility | Owning module (role names pending implementation) | Constraint |
| --- | --- | --- |
| Work, acceptance and references | Domain and schema | A decision has the same meaning across operating systems, Git configurations and apps. |
| Find the authoritative records and identify the project | Authority resolver | Never infer authority from a branch or remote name alone, or automatically promote an old copy. |
| Locate workspaces and app worktrees | Workspace topology | A directory named `.claude` is insufficient evidence to exclude its entire contents. |
| Observe the file set, contents and policies | Observation service and Git/non-Git adapters | Commands share ignore rules. Report policy changes separately from content changes. |
| Immutable objects, heads, transactions and recovery | Store service | Use one source of truth. Indexes and caches are derived. |
| Coordinate execution, submission and acceptance | Application services | Keep UI output and provider calls outside the domain. |
| Read current and historical results | Query service | A partial query cannot certify the integrity of the whole store. |
| Provider, notification and platform effects | Capability adapters | A model judgment or a notification click cannot substitute for acceptance in Core. |
| Installation and project entry | Packaging, composition and agent entry | Keep instructions for developing the source out of installed projects. |

Give each concept one owner for validation and repeat the necessary checks at its boundaries. Application services depend on ports. The composition root connects them to concrete adapters.

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

Archiving changes the state of a Work and how it is found. Preserve the Work and its contents. Keep files in place until their locators are stable. Revoking an acceptance or reopening work adds an event or decision while preserving the sealed bytes.

A checkpoint can stay unchanged while a file it references is modified. Store immutable objects by content hash, check hashes on read, and verify the referenced dependencies when recording a decision. A full audit covers objects outside an ordinary query. Archiving does not run garbage collection or guarantee a reduction in storage.

이번 기록에는 명령 전체 시간이 있고 내부 단계별 profiler가 없다. 파일 관측·전체 그래프 검증·실행기 해시 비용의 비율을 나눠 계산할 수 없다. managed 실행기 비용도 이번 source/Python 측정으로 대신하지 않는다. 당시 종료된 측정에 몰래 추가하지 않았으며, 이후 별도 [집중 진단](diagnostics.md)에서 시간 분해를 완료했다. 새 managed 실행기 비용은 여전히 별도 검증이다.


## Current corrections and compatibility

The earlier unmeasured profiling gap is resolved by [diagnostics](diagnostics.md); the OS-data authority policy has since been adopted and [C1–C8](implementation-contracts.md) now specify the detailed R2 treatment. Actual host access and implementation qualification remain open. The [R1 disposition](review-disposition.md) is historical. The labels S1–S11 identify design topics, not external source dependencies.

Pre-public trial migration/readers/profile compatibility are excluded. New connection, capability/version management, update, failure recovery and detach remain required. The first public release begins the obligation to preserve records, settings, bodies and human acceptances. Existing bounded worker/umbrella, execution/cancellation and notification semantics are not discarded for schedule reasons. Future parallel execution is separate from concurrency-safe record identities and transactions.


## Structural Topics In Plain Terms

S1 defines layers and dependency direction; S2 assigns each identity/observation concept one owner; S3 separates authoritative records from regenerable projections while protecting last recovery exports. S4 removes pre-public compatibility obligations, not first-public update protection. S5 provides one ordinary entry per platform with separately managed optional capabilities. S6 makes bounded verification and preserved archived history part of the record design. S7 separates user, agent and maintainer documents. S8 requires self-contained public source/tests, correctly placed reusable helpers, installed links, distinct product/version/support identities, reproducible release assets and support/update operations. S9 measures the old implementation before comparing replacements. S10 separates source-development and installed-project entry. S11 preserves common authority, Work/workspace identities and CAS/conflict information without implementing parallel scheduling. These definitions supersede any need to consult a private proposal to understand the table.
