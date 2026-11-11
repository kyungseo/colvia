# P3 결과 정적 검토 (frozen source only)

## 검토 전제

- 제공된 소스 본문만 읽었습니다. 실행, 테스트, 파일 접근은 하지 않았습니다.
- 아래 발견은 모두 정적 추론입니다. 재현 증거는 없습니다.
- Driver가 보고한 테스트 통과는 독립 관찰로 취급하지 않았습니다.
- 패킷에 본문이 없는 의존성은 동작을 가정하지 않고 불확실성으로 표시했습니다. 해당 의존성은 observation.verify_scope, observation.policy_transition, graph.validate_closure, GenerationStore.commit_heads와 begin_import, tree.read_tree와 entry_at, bodies 입니다.

## 발견 사항 (영향 큰 순서)

### 1. [높음] 관찰에 포함되지 않는 scope 경로 때문에 Work가 active 상태에서 영구히 멈춤

- 위치: src/colvia/work.py `plan`, `_observe_from_plan`, `submit`. src/colvia/workspace.py `LocalWorkspace.capture`. src/colvia/observe.py `observe`(Git 분기의 admitted 계산).
- 원인:
  - Git 관찰은 `admitted = (비무시 파일) | index | protected` 만 포함합니다. `protected`에는 기준선 경로만 들어가고, 승인된 scope는 들어가지 않습니다.
  - 반면 `capture` 마지막의 `self.selected(paths)` 비교는 ignore 정책과 경계를 무시하고 실제 파일을 읽습니다.
- 반례:
  1. Git 작업공간의 `.gitignore`에 `out/`이 있습니다.
  2. scope가 `out/report.md`인 계획을 승인하고 시작합니다.
  3. 작업이 `out/report.md`를 새로 만듭니다.
  4. submit 시점의 current snapshot에는 이 파일이 없습니다. 따라서 `changed=[]`가 되고 after map도 비어 있습니다.
  5. 그런데 `selected`는 파일을 반환하므로 `body-observation-changed`로 실패합니다. 재시도해도 같은 결과입니다.
- 왜 멈추는가: revise는 review 단계에서만, plan 교체는 planned 단계에서만 가능합니다. 따라서 이 Work는 빠져나갈 경로가 없습니다.
- 같은 계열의 경우:
  - scope가 등록된 nested workspace나 container 경계 아래에 있는 경우.
  - scope가 gitlink 내부 경로(예: `sub/file`)인 경우.
  - 이미 존재하는 ignored 파일이 scope인 경우에는 plan 단계에서 같은 오해성 코드로 실패합니다.
- 최소 수정:
  - plan 단계에서 scope 경로를 검사합니다. 경계(nested, container, `.git`), opaque gitlink 하위, 정책상 미관찰 경로라면 명시 코드(예: `scope-not-observable`)로 거부합니다.
  - ignored 경로를 허용할 의도라면 `plan`, `_observe_from_plan`, `_recheck_observation`, `_validate_head`의 `protected`에 scope를 합집합으로 넣어 관찰과 `selected` 판단을 일치시킵니다.
- 불확실성: verify_scope가 이미 이런 경로를 거부하는지는 패킷만으로 알 수 없습니다. 거부하지 않는다면 위 반례가 그대로 성립합니다.

### 2. [중간] review가 현재 파일 확인 실패 시 예외를 던져 결정 경로가 막힘

- 위치: src/colvia/work.py `review`, `submit` 반환부.
- 원인: `view`는 `_result_agrees`의 OSError와 RecordError를 잡지만, `review`는 잡지 않습니다. accept와 revise에 필요한 receipt는 사실상 `review`에서만 얻습니다.
- 반례:
  1. submit이 성공한 뒤, scope 파일 `report.md`가 디렉터리로 바뀌거나 권한이 000이 됩니다.
  2. `review`는 `scope-entry-not-regular` 또는 access-denied로 실패하고 receipt를 반환하지 않습니다.
  3. 사람은 수정 요청(revise)을 기록할 방법이 없습니다.
- 추가 문제: submit은 publish가 끝난 뒤 `self.review(work)`를 호출합니다. 여기서 실패하면 CLI는 오류를 보고하지만 제출은 이미 커밋된 상태입니다. 사용자가 다시 시도하면 `work-not-active`를 받습니다.
- 최소 수정:
  - `review`도 `view`와 같은 방식으로 예외를 잡고, `current_matches=None`과 `current_unavailable`을 설정한 채 receipt를 반환합니다.
  - accept는 기존처럼 `_result_agrees`가 거짓이거나 실패하면 거부합니다.

### 3. [중간] 서로 다른 workspace 사이에 Work가 교체될 수 있음

- 위치: src/colvia/work.py `plan`(prior 처리부), `work_key`.
- 원인:
  - `work:<name>` 키는 프로젝트 전역입니다.
  - `plan`은 prior head를 `_object`로만 읽고, prior head의 workspace가 현재 workspace와 같은지 확인하지 않습니다.
  - receipt는 공개 값(project, instance, work, head ref)의 해시이므로 호출자가 직접 계산할 수 있습니다.
- 반례:
  1. Git linked workspace A에 planned 상태의 `report`가 있습니다.
  2. workspace B의 호출자가 저장소에서 head ref를 읽어 approve receipt를 계산합니다.
  3. 그 값을 `replace_receipt`로 넘기면 A의 계획이 B 소유 계획으로 대체됩니다.
- 반례 성립 범위: B에서 `plan_review`를 호출하면 wrong-workspace로 막히므로, 정상 UI 경로로는 일어나지 않습니다. receipt를 직접 계산한 경우에만 성립합니다.
- 최소 수정: prior가 있을 때 `head_summary`를 사용하고 `payload['workspace']==self.workspace.workspace`를 요구합니다. 다르면 `work-already-exists` 또는 `wrong-workspace`로 거부합니다.

### 4. [중간, 의도 불확실] dirty 상태이거나 HEAD가 이동한 gitlink가 있으면 프로젝트 전체 관찰이 실패함

- 위치: src/colvia/adapters/opaque_git.py `inspect_gitlink`, src/colvia/presentation.py `MESSAGES`.
- 원인: gitlink의 상태가 다음 중 하나이면 observe 전체가 실패합니다.
  - submodule HEAD가 parent index의 OID와 다름.
  - 무시되지 않은 untracked 파일이 있음.
  - 내용이 수정됨.
  - staged 변경이 있음.
- 반례: 작업 범위와 무관한 submodule에 수정 파일이 하나 있으면 plan, start, submit이 모두 `gitlink-content-changed`로 실패합니다. 이 코드에는 전용 메시지가 없어 일반 문구만 표시됩니다.
- 추가 문제: `mode,kind,oid=parts[0].split(b' ')`는 형식이 예상과 다르면 RecordError가 아닌 ValueError를 냅니다. CLI는 이를 잡지 않으므로 traceback이 출력됩니다.
- 최소 수정:
  - 요구가 "dirty 상태도 opaque 상태로 기록하고 보호"라면, dirty 여부를 opaque state 값에 포함시켜 관찰을 계속하고 변화만 감지해야 합니다.
  - 요구가 "거부"라면, `gitlink-*` 코드에 사용자 안내 메시지를 추가하고 ls-tree 파싱 실패를 RecordError로 변환합니다.

### 5. [낮음~중간] map_update가 도달 불가능한 중간 노드까지 객체로 내보냄

- 위치: src/colvia/maps.py `map_update`(`write`, `staged`, 반환부).
- 원인:
  - collapse로 부모가 leaf로 합쳐질 때, 먼저 기록한 child leaf가 staged에 남습니다.
  - 빈 bucket을 위해 만든 빈 leaf도 staged에 남습니다.
  - `MapObjects.objects`가 staged 전체를 반환합니다.
- 반례: 17개 키를 가진 branch에서 키 하나를 삭제하면 다음이 일어납니다.
  - 수정된 child leaf가 staged에 기록됩니다.
  - 부모는 16개 키짜리 leaf로 합쳐집니다.
  - child leaf는 결과 root에서 도달할 수 없지만 objects에 포함됩니다.
- 영향: 이번 저장공간 증가 수정의 목적과 반대로, 갱신할 때마다 쓰레기 객체가 쌓일 수 있습니다.
- 확인한 점: build_map과의 정규 형태 동등성은 성립한다고 판단했습니다. leaf와 branch의 임계값, 빈 child 제거, collapse 규칙이 일관됩니다. 경계(radix16, leaf16, depth16)도 일관됩니다.
- 최소 수정: 반환 직전에 결과 root에서 staged 안의 도달 가능한 노드만 수집해 반환합니다.
- 불확실성: commit_heads가 도달 불가능한 객체를 거부하는지, 그대로 저장하는지 알 수 없습니다. 거부한다면 이 문제는 저장공간 증가가 아니라 갱신 실패로 나타납니다.

### 6. [낮음] archive나 restore 뒤의 중복 accept가 stale 오류로 보고됨

- 위치: src/colvia/work.py `accept`(completed 분기).
- 원인: `link(head,'previous')`가 review head라고 가정합니다. archive를 하면 previous가 completed head로 바뀝니다.
- 반례: 수락한 뒤 archive를 하고, 같은 review receipt로 accept를 다시 보냅니다. 이미 수락된 작업인데도 `stale-result-receipt`("검토 대상이 바뀌었습니다")가 반환됩니다.
- 영향: 상태는 안전하지만, 사용자에게 잘못된 안내가 나갑니다.
- 최소 수정: completed head를 previous 방향으로 따라가며 decision이 같은 head를 지나, 첫 review head의 receipt와 비교합니다. 단계 수에는 상한을 둡니다.
- 관련 사항: archive 값이 이미 같아도 새 head를 쓰므로, 이 오류 상황이 불필요하게 생깁니다. 값이 같으면 no-op으로 처리하는 것을 권합니다.

### 7. [낮음] 관리 경로 차단이 대소문자와 정규화를 구분함

- 위치: src/colvia/work.py `plan`(managed-path 검사).
- 원인: 비교가 정확 문자열 비교입니다. 따라서 `.GIT/config`나 `.Colvia-link.json` 같은 경로가 승인 scope에 들어갈 수 있습니다.
- 영향: 기본 설정의 macOS 파일 시스템은 대소문자를 구분하지 않아 이 경로가 실제 관리 파일을 가리킵니다. 관찰은 경계 때문에 이 변경을 보지 못하므로, 기록 무결성 문제는 아닙니다. 다만 사람이 관리 경로 편집을 승인한 것처럼 보이는 계획이 만들어집니다.
- 최소 수정: 경로 구성요소를 NFC 정규화하고 casefold한 값으로 비교합니다.

### 8. [낮음, 의미 확인 필요] 같은 workspace에서 동시에 진행되는 두 Work가 서로를 막음

- 위치: src/colvia/work.py `submit`(기준선 전체에 대한 verify_scope).
- 반례:
  1. Work one과 two가 같은 workspace에서 모두 active입니다.
  2. two가 `two.md`를 수정합니다.
  3. one을 submit하면 `outside-scope-change`가 납니다.
  4. 순서를 바꿔도 같습니다. 한쪽이 revise된 뒤 다시 제출할 때도 같습니다.
- 테스트와의 관계: 제출된 테스트는 두 Work를 순차로 진행하므로 이 상황을 다루지 않습니다.
- 판단: 직렬화가 의도라면 수정은 필요 없습니다. 다만 메시지가 "맡긴 범위 밖 파일도 바뀌었습니다"로만 나와 원인(다른 Work)을 알 수 없습니다. 원인을 구분할 수 있게 하는 정도가 최소 대응입니다.

### 9. [낮음] CLI 실패 처리의 빈틈

- 위치: src/colvia/cli.py `main`, `plan` 입력 처리.
- 문제:
  - RecordError와 OSError 이외의 예외(ValueError 등, 예: 인자에 NUL 문자)는 traceback으로 출력됩니다.
  - 사람용 출력에서 store-outcome-unknown이 나면 "실행 기록을 확인해 주세요"라고만 하고 operation id를 보여주지 않습니다.
  - `--path`를 중복으로 주면, begin_import와 body capture가 이미 진행된 뒤 스키마 검증에서 일반 메시지로 실패합니다.
- 최소 수정:
  - 예상하지 못한 예외는 일반 실패 코드로 변환합니다.
  - outcome-unknown일 때는 사람용 출력에도 operation id를 한 줄 포함합니다.
  - `plan` 시작 시점에 scope 중복과 정규형을 검사합니다.

## 정적으로 문제를 찾지 못한 부분 (추론)

- 승인과 수락:
  - 승인 receipt는 head ref를 통해 정확한 plan 내용에 결합됩니다. 계획을 교체하면 이전 receipt는 무효가 됩니다.
  - 수락은 한 번만 기록되고, 중복 accept는 새 head를 만들지 않습니다.
  - revise는 approval을 유지하고, 결과 revision을 증가시키며, provenance 체인을 이어갑니다.
- 원본 보존과 조회: 이전 본문은 provenance 체인으로 조회할 수 있고, result_content는 body를 끝까지 소비해 digest를 검증합니다.
- 범위 밖 변경과 검토 후 변경: 범위 밖 변경은 submission에 들어가지 않습니다. 검토 후 scope 파일이 바뀌면 accept가 거부됩니다.
- 기존 보호 경로: `protected`를 admitted와 snapshot에 합집합으로 넣어, 새 ignore 규칙이 기존 보호 경로를 숨기지 못합니다.
- D7 container: 모든 child가 등록된 nested workspace이고 identity가 맞을 때만 경계로 인정합니다. 관찰 마지막에 prove를 다시 실행하므로, 그 사이에 생긴 고아 파일도 감지됩니다.
- symlink와 placeholder: 변경되면 범위 밖 변경으로 처리되고, scope에 포함하는 것은 거부됩니다.
- candidate와 followup: 기록만 하며 Work를 시작하거나 수락하지 않습니다.
- 페이지 조회: 커서가 root에 결합되어, root가 바뀐 뒤 쓰면 중복이나 누락 대신 거부됩니다. 마지막 페이지가 정확히 limit개일 때 next가 없는 것도 맞습니다.
- Git 없는 환경: plain 작업공간은 Git 실행 파일 없이 동작합니다.

## 남은 차단 사항

1. 발견 1(관찰 밖 scope로 인한 영구 정지)은 P3 기본 경로에서 Work가 회복 불가능해지는 경우입니다. 수정 전 해소를 권합니다.
2. 발견 2(review 실패 시 결정 불가)도 사람의 결정 경로를 막으므로 함께 수정해야 합니다.
3. 발견 3과 4는 의도를 확인한 뒤 거부나 안내를 명시하는 수정이 필요합니다.
4. 발견 5 이하는 차단 사항은 아닙니다.

## 검토 한계

- 실행이나 재현을 전혀 하지 않았습니다. 모든 반례는 소스 흐름을 읽고 추론한 것입니다.
- 아래 모듈은 본문이 없어 동작을 확인하지 못했습니다. 그중 verify_scope의 동작에 따라 발견 1의 범위가 달라질 수 있습니다.
  - observation (verify_scope, policy_transition)
  - graph.validate_closure
  - storage의 commit_heads, begin_import, ValidationView
  - tree, bodies, codec, schemas
- P1 저장소 감사 범위는 지시에 따라 다시 검토하지 않았습니다.
- 설치형 런처, 호스트 qualification, P4~P9 항목은 범위 밖입니다.
