# R1 design review disposition

Status: Driver disposition, not Owner acceptance or executed qualification. The [review](review-r1.md) used the same session as prior trials/proposals; a fresh focused review of the corrected design remains pending. The original response and frozen inputs are preserved. This source copy keeps the technical findings and limitations without personal delivery details.

## 필수 지적 처분

| 항목 | Driver 처분 | 구현에 미치는 영향 |
| --- | --- | --- |
| F1 저장 위치와 sandbox | 채택. Codex 공식 문서가 기본 workspace-write의 .git 및 해석된 gitdir 하위를 읽기 전용으로 명시한다. 현재 세션의 권한 정의도 일치한다. 제품 쓰기 시험을 재현했다는 뜻은 아니다. | .git/colvia를 무조건적인 기본 위치로 확정했던 안을 철회한다. 저장 계층은 위치와 분리하고, 연결 방식·권한·앱 worktree 접근을 함께 해결한 뒤 locator를 고정한다. |
| F2 Git 밖 기록과 백업 | 채택, 표현 보정. Git push/clone에는 따라가지 않는다. 모든 백업에서 빠진다는 표현은 과하다. 전체 파일 백업은 포함할 수 있다. | versioned export/import와 실제 복원 시험을 필수로 둔다. 갱신 전 로컬 복구 사본과 기기 분실에 대비한 외부 백업은 구분한다. 데이터 약속은 권장 위치와 함께 Owner에게 제시한다. |
| F3 트리 정규형 | 결함 채택, 고정 256개 분할로 즉시 교체하는 제안은 보류. 평균 분포 계산만으로 100만 파일 용량을 보장할 수 없다. 긴 경로·분포 편중에서 leaf 한도가 먼저 걸릴 수 있다. | 동일 집합이면 동일 root가 되는 생성·분할·삭제 후 합치기 규칙을 명세화한다. 순서 변경·삭제 후 재삽입 속성 시험과 크기 경계를 포함한다. 아래 대안을 집중 재검토한다. |
| F4 SQLite | 채택. macOS fullfsync 설정, hot journal 복구 필요 상태, 짧은 읽기 transaction, 최소 SQLite 버전, versioned export를 명세에 넣는다. | 설정값 하나를 정전 내구성의 무조건 보장으로 표현하지 않는다. 지원 OS·파일시스템·실제 런타임을 확인하고 중단 주입 시험을 별도로 한다. |
| F5 D7 비교 정책 | 수락 파일 확인과 제출 범위 검사를 분리하는 방향 채택. 제시된 동등 판정 알고리즘은 불충분하다. | 기준 목록에 없던 새 파일을 새 ignore 규칙으로 숨기는 반례도 막아야 한다. 과거 수락의 유효성과 현재 제출 가능성을 별도로 답한다. |
| F6 Git 후보·index | 채택, 구현 순서 보정 필요. ref 갱신 직후 index를 맞추는 두 동작은 하나의 원자적 변경이 아니다. | 후보 기준·부분 staging·HEAD 경쟁·ref/index 사이 중단·복구 상태를 먼저 정의한다. 사용자 index와 기존 변경을 덮어쓰지 않는다. |
| F7 기능별 비용 누락 | 채택. 기존 32–52시간을 전체 기능 이식의 확정 견적으로 사용하지 않는다. | worker/umbrella·공식 실행·전달/알림·플랫폼 이식 비용을 별도로 넣는다. 일정만을 이유로 기존 기능을 공개 뒤로 미루는 제안은 채택하지 않는다. |
| F8 거부 규칙 목록 | 채택. 기능 단위 회귀표만으로는 부족하다. | 오류·조건·모듈별 정적 목록에 유지/통합/폐기 사유를 남기고, 동등한 조건은 묶어서 검증한다. 단순 검색 목록을 전수 안전성 인증으로 주장하지 않는다. |

### F1의 확인 근거와 남은 선택

[Codex 공식 sandbox 문서](https://learn.chatgpt.com/docs/agent-approvals-security#protected-paths-in-writable-roots)는 writable root 아래의 .git과 gitdir 포인터가 가리키는 위치를 재귀적으로 보호한다고 설명한다. 따라서 매번 권한을 올리지 않고 기록을 쓴다는 목표에 현재 위치안은 맞지 않는다. Claude의 모든 실행 모드까지 이 근거로 단정하지 않는다.

대안을 매번 권한 상승과 Git working tree 내부 두 가지로만 제한하지 않는다. 저장소 공용 authority의 논리적 정체성과 물리적 위치를 분리하고, 연결 단계에서 허용된 저장 위치를 고정하는 안도 비교한다. 다만 외부 폴더도 앱 sandbox에 막힐 수 있으므로 단순 경로 이동을 해결책으로 취급하지 않는다. 허용된 폴더, linked worktree의 접근, git clean·clone·삭제·복구를 함께 만족하는 실제 경로가 필요하다. 이번에는 권한 변경·우회·실제 설치를 수행하지 않았다.

### F3의 보정 제안

적응형 구조를 유지한다면 경로 정규화·고정 hash 함수·encoding을 먼저 고정한다. 각 subtree는 전체 entry 집합만의 함수로 만든다. leaf가 되는 조건을 entry 수와 정확한 직렬화 크기로 정의하고, 조건을 넘을 때만 다음 hash byte로 분할한다. 비어 있는 자식은 없애고, 삭제 후 leaf 조건을 만족하면 반드시 합친다. 자식과 entry 정렬, 중복 거부, 최대 깊이와 크기 초과 시 게시 전 거부를 고정한다. incremental 갱신도 이 정규형과 같아야 한다.

이는 구현·성능 검증 전 제안이다. 고정 256-bucket은 단순성의 장점이 있으므로 비교에서 버리지 않되, 평균 크기를 지원 한도로 발표하거나 확장 필요성을 형식 변경으로 미루는 근거로 쓰지 않는다.

### F5에서 빠진 반례

기준 시점에 없던 범위 밖 파일 secret.txt를 만들고, 동시에 ignore에 secret.txt를 추가했다고 가정한다. 기준 admitted 목록만 현재 정책으로 검사하면 새로 제외된 기준 파일은 없다. 현재 관찰에서도 파일이 숨겨져 변경을 놓칠 수 있다. 이는 아직 실행하지 않은 정적 반례다.

제출 시 과거/현재 정책의 실제 효과를 현재 파일 집합까지 포함해 비교하거나, 변경 효과가 검증된 구조 경계 내부에만 있다는 보수적 증명이 필요하다. 증명할 수 없으면 해당 제출을 멈춘다. 등록 worktree 삭제 뒤 그 경로에 일반 파일이 생긴 경우, global exclude와 부정 패턴도 포함한다. 이미 수락한 결과의 bytes·mode 확인을 이 정책 차이만으로 무효화하지 않는다.

### F6에서 먼저 정할 계약

후보는 사용자 index 전체가 아니라 현재 HEAD와 보존된 Work 변경으로 구성하는 방향이다. 다만 수락 경로의 HEAD가 Work 시작 기준과 다르면 보존한 결과 전체를 덮어씌워 중간 편집을 잃게 해서는 안 된다. 기준 일치 확인 또는 명시적인 병합 계약이 필요하다.

Git ref와 index를 함께 바꾸는 자동 통합에는 저장된 실행 의도, 예상 HEAD·index, 잠금·경쟁 처리, 단계별 중단 후 재개 규칙이 필요하다. ref CAS 성공 후 index 갱신 전에 죽는 경우를 성공이나 안전한 거부로 표시하지 않는다. Colvia DB까지 포함한 여러 저장소를 원자적으로 바꿀 수 있다고 가정하지 않는다. 복구 상태와 실제 Git 결과를 대조한다.

관찰 명령의 index 재기록·fsmonitor·외부 filter 실행을 통제하되 프로젝트 필수 hook 정책을 몰래 우회하지 않는다. CRLF/filter/LFS의 raw 본문과 Git blob 차이를 명시한다. 자동 통합을 지원하지 못하는 조건은 정확히 안내하고, 일반 Work 수락과 Git 통합을 혼동하지 않는다. 이는 통합 설계의 필수 조건이며, 완성된 프로토콜이나 실행 검증 결과는 아니다.

## 권장 지적 처분

| 항목 | 처분 |
| --- | --- |
| F9 옛 .hrn과 충돌 | 새 형식 이름·위치 분리 취지 채택. 옛 .hrn을 무조건 일반 내용으로 수집하는 안은 채택하지 않는다. 과거 기록·배포 사본을 새 결과에 대량 포함할 수 있다. 이전 설치 흔적은 해석·이관하지 않고 연결 시 명시적으로 처리할 경계로 본다. 실제 삭제는 하지 않는다. |
| F10 범위 추가 시 before | 가짜 시작 본문 금지 채택. 새 경로의 승인된 기준 시점과 이미 존재하던 편집을 표시한다. 필요하면 새 기준으로 범위를 승인받고 before를 보존한다. 최초 시작의 본문이 없는데 있는 것처럼 쓰지 않는다. |
| F11 동기화 폴더 | 로컬 DB 운영 조건·알려진 동기화 경로 진단 채택. 경로 이름만으로 동기화 부재나 안전성을 보증하지 않는다. OS 동기화 설정은 변경하지 않는다. |
| F12 workspace 수명 | 삭제·prune·경로 재사용·프로젝트 복사와 identity 충돌 시험 채택. 같은 경로 문자열만으로 같은 workspace라고 판단하지 않는다. |
| F13 성능 목표 | 내부 목표와 실측 구분 채택. 선택 조회, 전체 조회, 본문 검증, 일반 Work 처리, 저장 증가량을 나눠 측정한다. 제안된 1초는 검증된 지원 약속이 아니다. |
| F14 사용자 부담 | 정상 경로에서 범위와 결과 결정만 남기는 목표 채택. 이미 구체적으로 승인한 범위를 다시 묻지 않는다. 내부 경로·토큰은 기본 설명에서 제외한다. 연결 시 의도된 파일 추가와 매 Work마다 생기는 Git 잡음은 구분한다. |

SQLite 설정 근거: [fullfsync 공식 설명](https://www.sqlite.org/pragma.html#pragma_fullfsync). 이 설정은 지원 시스템에서 F_FULLFSYNC 사용을 요청한다. 실제 전원 장애 시험을 수행한 것으로 해석하지 않는다.


## Next review

Review the corrected authority/permission and backup proposal, tree canonicalization, ignore-policy counterexample, Git ref/index interruption protocol, capability estimates and [runtime/extension contract](runtime-and-extension.md) together. Do not repeat the original review unchanged. Maintain first-public compatibility and existing capability scope. No actual installation or publication is authorized by this document.
