# Concurrency Design Conditions And Current Assumptions

Status: Driver 정적 분석·명세 제안, 2026-11-06. 동시 실행 구현·경쟁 시험을 수행한 결과가 아니다. 기준은 the prepared Colvia source input, HEAD `37ec0752fd7b1854c4f2765243826f2a73e57a6a`와 보존된 미커밋 보강이다. 소스 상대 경로는 Colvia 저장소를 기준으로 한다. 행 번호는 분석 당시 위치이며 구현 후 다시 확인한다.


## Decision

S11 네 항목 모두 새 기록 계약에 포함한다. 현재도 Work별 current와 여러 Work의 기록이 있으므로, 전체를 단일 Work 시스템이라고 규정하지 않는다. 한 번의 기록 게시를 직렬화하는 것, 외부 효과를 한 건으로 제한하는 것, 여러 작업의 내용을 동시에 편집하는 것은 서로 다르다.

| 조건 | 명세에 넣을 계약 | 공개 후로 남길 기능 |
| --- | --- | --- |
| ① 여러 살아 있는 Work | authority 안에 Work별 head, workspace identity, baseline, 결과·시도 identity를 둔다. 전역 active Work 하나로 실제 상태를 표현하지 않는다. 화면에서 선택한 Work는 권위가 아닌 탐색 상태다 | 여러 workspace 실행 예약·분배·병렬 UI |
| ② 공용 lock과 CAS | 같은 authority의 쓰기는 같은 lock을 사용한다. 모든 변경 가능한 권위 head는 예상 이전 참조와 대조한 뒤 게시한다. 여러 head를 바꾸는 동작은 하나의 복구 가능한 transaction으로 다룬다 | 처리량을 높이기 위한 lock 분할·분산 lock |
| ③ 내부 ID와 제목 분리 | 프로젝트/authority namespace, Work·시도·제출 ID와 사람이 읽는 제목을 분리한다. 충분한 무작위성을 가진 ID를 생성하고 중복을 검사한다. 이동·export/import에서 identity를 보존한다. 내용 hash는 무결성 식별이며 업무 identity를 대신하지 않는다 | 여러 clone의 자동 기록 병합·사용자/기기 협업 |
| ④ 범위 겹침 | claim에 workspace, 기준점, 읽기 의존·쓰기 경로, 경로 정책 버전을 명시한다. 같은 workspace의 충돌 쓰기는 실행 전에 거부하거나 명시적 순서로 예약한다. 다른 workspace의 같은 경로는 각자 작업할 수 있지만 통합 대상에서는 다시 충돌 판정한다 | 자동 병합·줄 단위 편집 소유권·실시간 공동 편집 |

clone은 namespace까지 복제할 수 있다. 고유 ID만으로 clone들이 하나의 최신 기록을 공유한다고 판단하지 않는다. 같은 ID에 다른 bytes가 오거나 서로 다른 head가 오면 충돌로 남기며 자동 last-write-wins로 합치지 않는다.

CAS는 기록 경합을 막지만 외부 editor와 모델 도구의 파일 쓰기까지 잠그지 않는다. 범위 claim도 관찰 계약이지 OS 접근 차단이 아니다. 제출·수락 때 실제 파일과 정책을 다시 대조해야 한다. 첫 공개의 실행 정책을 직렬로 두더라도 여러 active/review Work의 조회·보존과 기존 한정 worker/umbrella 계약을 없애지 않는다.

## Current Code Inventory

아래는 Core의 저장·제출·수락·후속·delivery·공식 실행·topology 경로를 읽은 목록이다. 문자열 검색만으로 전체 코드의 동시성 안전성을 인증한 목록이 아니며, UI·플랫폼 프로세스의 모든 경합을 전수 실행하지 않았다.

| 위치 | 실제 가정/제약 | 새 형식에서의 처리 |
| --- | --- | --- |
| `src/hv2ref/work.py:1685` WorkStore._all; `:1007` current 검사 | `.hrn/work/<id>`별 current가 있고 여러 Work를 순회한다. 전역 active Work 포인터가 아니다 | Work별 head를 유지. 읽기 비용 문제와 단일 Work 문제를 혼동하지 않음 |
| `src/hv2ref/work.py:2001` ordinary_command; `:2132` baseline 검사; `:2141` snapshot/manifest | serial local edit 편의 경로. 각 Work baseline은 있으나 같은 target의 전체 관측 차이를 결과로 삼음 | workspace별 관측을 명시. 같은 폴더의 다른 Work 편집은 자동으로 자기 결과에 흡수하지 않음 |
| `src/hv2ref/work.py:511` validate_manifest, 특히 `:538` scope 검사 | 전체 base→result 차이가 그 Work의 정확한 파일 범위 안이어야 함. 같은 폴더에서 B가 다른 파일을 바꾸어도 A의 제출을 막을 수 있음 | 현재 범위 밖 변경 검출은 유지. 추후 다른 Work 변경과 외부 변경을 구별할 근거가 없으면 거부; 단순히 diff를 scope로 잘라 통과시키지 않음 |
| `src/hv2ref/workspace.py:755` writer_guard | target의 `.hrn/locks/writer.lock` 하나로 협력 writer를 직렬화 | lock 위치·키를 workspace가 아닌 authority로 이동. 서로 다른 worktree가 다른 lock을 잡는 실수를 방지 |
| `src/hv2ref/workspace.py:478` linked-worktree 분류, `:486` mutation 거부 | linked worktree 쓰기를 허용하지 않는 topology 경계 | 검증된 common-dir/authority와 workspace를 분리한 뒤 허용; 일반 중첩·외부 authority 보호는 유지 |
| `src/hv2ref/work.py:1720` _pending_guard | 다른 Work의 미완료 worker·umbrella publication/decision이 프로젝트 쓰기를 막음. content 적용에는 더 강한 전역 pending 검사 | 미완료 transaction 복구 경계 유지. 장래 scoped transaction을 도입하기 전 무조건 제거하지 않음 |
| `src/hv2ref/intent.py:309`, `:332`; `src/hv2ref/candidates.py:305`; `src/hv2ref/continuation.py:420`, `:450` | 미완료 intent/Work/후속 기록 게시가 다른 기능의 쓰기도 막음 | 같은 transaction protocol로 통합하고, 살아 있는 Work와 미완료 게시를 구별 |
| `src/hv2ref/continuation.py:759` one_active unique index; `:765` effect fence | 프로젝트 inbox에서 queued/question/running/reconcile 요청을 합쳐 한 건만 허용. 모든 Work가 하나라는 뜻은 아님 | 별도 effect/request ID와 Work 연결을 유지. 첫 공개의 한 건 한도는 서비스 정책으로 유지; 병렬 delivery는 별도 검증 후 확장 |
| `src/hv2ref/continuation.py:610` _delivery_observe, `:623` 검사 | 다른 Work의 pending decision/selection도 delivery admission을 막음; 일반 local Work만 수용 | 실행 승인·실제 효과와 공용 기록 transaction의 관계를 명시. 임의 병렬화하지 않음 |
| `src/hv2ref/workspace.py:787` 실행 기록 guard; `src/hv2ref/official_state.py:238` require_no_open | 종료되지 않은 공식 실행이 일반 writer를 막음. 공식 capsule 내부도 callback 순서를 검증함(`:157` 이후) | 외부 효과의 불확실 상태와 복구를 유지. 동시 공식 실행은 별도 capability/권한 설계 후 허용 |
| `src/hv2ref/work.py:1892` expected_selection_ref; `:2132` baseline; `:2247` revision 재개 | 같은 Work의 기준/선택이 바뀌면 거부하는 기존 optimistic check | 새 authority에서도 유지·확장. 모든 head 전이에 적용됐는지는 새 writer 검증 목록으로 확인 |
| `src/hv2ref/work.py:1699` casefold 검사; `:2007` 사용자 지정 wid; `:2135` ordinary-submit | Work ID가 경로/사람이 지은 slug 역할도 맡고, ordinary의 일부 하위 ID는 Work 안에서만 유일 | namespace가 붙은 내부 ID와 제목 분리. Work 안의 local ID를 전역 고유 ID로 오해하지 않음 |
| `src/hv2ref/candidates.py:327` selected; `src/hv2ref/continuation.py:374` pending 한 건 | 다음 후보 선택 한 개, Work의 후속 게시 pending 한 개는 각각의 의미상 cardinality | 여러 Work 실행 제한으로 확대 해석하지 않음. 후속 선택 의미는 별도 제품 결정 없이 변경하지 않음 |

## Acceptance Cases For The New Format

구현 뒤에 확인할 조건이며 이번에 실행한 결과가 아니다.

1. 두 Work가 active/review로 공존하고 각각의 head·baseline·알림 링크를 잃지 않는다.
2. 같은 Work의 같은 예상 head로 경쟁한 두 쓰기에서 한 개만 게시되고, 패자는 재검토를 요구한다. 서로 다른 Work 게시도 authority transaction의 부분 상태를 노출하지 않는다.
3. workspace가 다른 두 writer도 같은 authority lock으로 모인다. 중단 후 공개된 선택과 orphan 객체를 구별하고 복구한다.
4. 제목이 같거나 같은 사용자 slug를 가진 서로 다른 Work가 충돌하지 않는다. 충돌 ID 입력은 거부하며 clone 자동 병합으로 해결하지 않는다.
5. 같은 workspace의 겹친 쓰기, 다른 파일 쓰기, 경로 alias·대소문자·부모/자식 경로·삭제/추가·rename을 구별한다. 다른 workspace에서 같은 경로를 편집한 결과는 별도 결과로 남고, 통합에서 충돌을 드러낸다.
6. 외부 편집은 claim에 없더라도 다시 감지한다. 경고만 보인 뒤 잘못된 수락을 허용하지 않는다.
7. 조회·기존 worker/umbrella·수락 위임·한 건 delivery의 현재 의미가 보존된다. 여러 Work 보관을 병렬 자동 실행 성공으로 표시하지 않는다.

동시성 코드·OS 경합 검증은 실행되지 않았다. 현재 측정 목록을 바꾸지 않았으며, [구현 명세](design.md)의 미래 수락 조건으로 연결한다.
