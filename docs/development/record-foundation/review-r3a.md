# R3a 응답 — 구현 계약과 최종 방향 검토

작성 2026-11-06 · Reviewer: Claude Opus 5.5 (`claude-opus-5-5`) · session identity: 확인 불가(harness가 제공하지 않음)

이 문서는 Reviewer 의견이다. Driver 처분, Owner 결정, 구현 승인, 결과 수락을 대신하지 않는다.

## 0. 검토 조건과 독립성 한계

- 입력: R3a identity manifest의 13개 파일. 검토 전후 모두 sha256과 byte 수가 manifest와 일치했다(drift 0). base `37ec0752fd7b`. 요청문 sha256 앞자리 `5691afe33063`, manifest `2af2cf87d69c`.
- 독립성: 요청은 "fresh conversation"을 전제했지만 이 세션은 그 조건을 충족하지 않는다. 이 세션이 다음을 직접 작성했다.
  - R2 응답
  - Owner가 전달한 21:11 무렵 비공식 방향 의견
  - 그 의견의 통합본

  따라서 direction-advice-disposition은 내 의견에 대한 처분을 내가 검토하는 셈이다. 독립 검토가 필요하면 새 세션 검토를 별도로 두어야 한다.
- 허용 범위 위반 공개: 요청은 지정 파일 읽기와 hash 계산만 허용했다. 이번 검토 중 아래 두 가지를 근거로 하기 위해 지정 목록 밖의 파일을 읽었다.
  - S1: 현재 관측 코드의 symlink 처리. `src/hv2ref/work.py`, `src/hv2ref/workspace.py`를 grep으로 읽었다.
  - R3: 현재 payload 검사. `src/hv2ref/official_controller.py`와 해당 PATCH 개발 기록을 읽었다.

  나머지 지적은 지정 입력만 근거로 한다. 또 이 세션은 이전 대화에서 기존 source 목록, 시험 규모 등 지정 목록 밖 자료를 이미 읽었다. 그 지식이 판단에 섞였을 수 있다. Driver는 S1·R3를 지정 입력 밖 근거로 보고 직접 확인하거나 버릴 수 있다.
- 실행 없음: 제품 명령·시험·설치·네트워크·모델 호출을 하지 않았다. 아래 반례는 모두 재현하지 않은 정적 추론이다. `[외부 지식]`은 SQLite·Git·호스트 동작에 대한 기억이며 이번에 확인하지 않았다.

## 1. 판정

판정: 해당 단계 전 필수 보정(mandatory corrections before affected phase). 구조적 blocker는 없다.

R2 처분과 C1–C8은 R2의 필수 지적을 대부분 실제 계약 문장으로 닫았다. 공통 정본, 작업 폴더 identity, chunk 게시, 논리 export, Git 복구 표, 첫 설치와 갱신 신뢰의 분리가 서로 모순 없이 연결된다.

남은 문제는 형식 고정(P1) 전에 정해야 하는 확장·범위 결정 두 가지다. 그 밖에 연결 단계 두 곳, 복구 상태 한 곳, 이식 범주 한 곳이 비어 있다. 이 검토는 성능이나 플랫폼 지원을 보증하지 않는다.

## 2. 필수 보정

### S1. [High · P1 전 · Driver 결정, 공개 범위에 영향] symlink와 gitlink가 하나라도 있는 저장소 전체를 쓸 수 없다

- 위치: implementation-contracts C2 "Symlink, reparse, special-device and multiply linked content files are refused"와 entry mode 집합 `100644`/`100755`.
- 반례 [지정 입력 밖 source 근거]: 현재 관측 코드는 추적 entry mode가 두 값이 아니거나 파일이 일반 파일이 아니면 관측 전체를 거부한다. C2는 이 동작을 새 형식에 그대로 옮긴다. 그러면 추적된 symlink 하나(문서의 `README` 링크, node 설정의 `bin` 링크 등)나 submodule(gitlink) 하나가 있는 저장소에서는 일반 Work 자체를 시작할 수 없다. 승인 범위와 관계없이 그렇다. 기존 제품도 같은 제약이라 회귀는 아니다. 그러나 첫 공개 대상 저장소의 상당 부분을 미리 배제하게 된다.
- 왜 P1 전인가: entry mode 집합은 tree hash 형식의 일부다. 공개 뒤 넓히면 읽는 쪽 version을 올려야 하고 이전 runtime과 호환이 끊긴다.
- 최소 보정:
  - symlink는 `120000`, 대상 문자열 bytes의 digest로 기록한다.
  - gitlink는 `160000`, commit id로 기록한다.
  - 두 종류 모두 "보호 대상 opaque entry"로 관측에 넣는다. 범위 밖 변경 검출에는 포함하고, 승인 범위에 넣는 편집·적용·Git 통합은 거부한다. 링크를 따라가지 않고, 내용으로 materialize하지도 않는다.
  - 비 Git 폴더의 symlink도 같은 방식으로 기록한다. special device와 hard link가 여러 개인 파일은 지금처럼 거부한다.
- 시험: symlink·submodule이 있는 저장소에서 일반 Work 성공. symlink 대상 변경은 범위 밖 변경으로 거부. symlink를 승인 범위에 넣으려 하면 거부. 링크를 따라가지 않음.

### S2. [High · P1 전 · Driver] 모르는 객체 종류를 구분할 기준이 형식에 없다

- 위치: C2 "Unknown required kinds/fields refuse; an optional display extension may be skipped only if it is outside every decision dependency", 그리고 C3 bounded long-term use의 "Store edge roles".
- 반례 [정적]: v1.1이 선택 기능(예: 검토 메모)용 새 객체 종류를 결과에 연결했다고 하자. v1.0 reader는 그 종류를 모른다. 그런데 그 객체가 결정 의존인지 표시용인지는 객체 종류 이름으로는 알 수 없다. 참조한 쪽의 역할 정보로만 알 수 있다.
  - 안전하게 전부 거부하면, 선택 기능 하나를 쓴 뒤에는 이전 runtime이 그 Work를 읽지 못한다. "호환 rollback"과 "기능 해제 후 기록 읽기"가 사실상 불가능해진다.
  - 추측해서 건너뛰면 결정 의존을 놓칠 수 있다.
  - 본문 제거 정책(S3)과 공개 뒤 capability 추가도 모두 이 판단에 걸린다.
- 최소 보정: v1 참조 edge에 고정 역할 집합을 둔다. 예: `decision`, `integrity`, `provenance`, `display`. 규칙은 다음과 같다.
  - `decision`·`integrity` 아래의 모르는 종류는 거부한다.
  - `provenance`·`display` 아래의 모르는 종류는 "이 버전에서 표시할 수 없는 항목"으로 표시하고 결정에는 쓰지 않는다.
  - root map의 capability별 항목에도 같은 역할 값을 둔다.
  - export header의 "format requirements"에는 필수 reader 기능 목록을 넣는다.

  예약 enum 하나로는 부족하다는 Driver 판단에 동의한다. 다만 여기서 필요한 것은 enum이 아니라 이 분류 규칙이다.
- 시험: 합성 v1.1 객체를 `display`와 `decision` 역할로 각각 연결하고, v1.0 reader가 각각 표시 불가와 거부로 처리하는지 확인한다. 역할 값 자체를 모르면 거부한다.

### S3. [High · P1 전 · Owner 정책] 본문 제거 예외: 결정 방식과 v1 최소 계약

- 현재 상태: direction-advice-disposition은 예외 허용과 공개 전 최소 운영 명령을 권장했다. 아직 Owner 결정 전이다. 비용은 견적에 포함되지 않았다.
- 판단: 제안의 원칙(결정 사실 보존, 공유 chunk 영향 미리보기, 중단 상태 분류, 옛 백업의 한계 고지, 안전한 완전 삭제는 약속하지 않음)은 맞다. 다만 제자리 삭제(in-place)를 전제하면 비용과 위험이 커진다. 대신 이미 C4에 있는 export→restore 경로를 재사용하는 재구성 방식을 권한다.
- 권장 방식 (재구성 기반 제거):
  1. 미리보기: 제거 대상 body와 같은 chunk를 공유하는 모든 body와 그것을 쓰는 결과·결정을 보여 준다. chunk가 같다는 것은 같은 bytes를 담고 있다는 뜻이므로, 공유 consumer도 같은 비밀을 가지고 있을 수 있다. 일부만 지우면 제거가 완료되지 않았다고 표시한다.
  2. Owner가 승인하면, 대상 body descriptor를 "의도적 제거" 상태로 바꾼 논리 export를 새 미게시 store로 restore한다. 남은 참조가 없는 chunk는 이때 빠진다.
  3. 새 store를 전체 검증한 뒤 C1의 instance 교체로 활성화한다. 이전 DB 파일은 파일 단위로 지운다. 파일 단위로 지우므로 free page에 남은 bytes 문제가 생기지 않는다. 다만 OS snapshot, 이전 export, 백업, Git 이력, 원본 파일에 남은 사본은 별도 정리 대상으로 목록화한다.
  4. 중단 안전성은 C4의 "새 store에서 검증 후 활성화" 구조가 그대로 제공한다. 제자리 삭제의 동시성·중단 상태 분류를 새로 만들 필요가 없다.
  5. 대가: 재구성 시간과 일시적인 2배 공간이 든다. 작업 중에는 쓰기를 멈춘다(C4 migration의 quiesce와 같은 방식).
- v1 최소 reader·writer·export 계약 (Owner가 채택할 때):
  - body 상태 세 가지: 보존 / 결정 참조가 있는 의도적 제거 / 손상·불가. 의도적 제거는 제거 결정 record(승인자, 시각, 사유 범주)를 참조해야 한다. 자유 서술 사유에 비밀이 들어가지 않게 한다.
  - 제거된 body에 의존하는 동작(적용, Git 통합, 재수락)은 거부한다. 과거 수락 사실과 조회는 유지한다.
  - export v1 frame이 "의도적 부재 body"를 표현한다. restore 때 옛 로컬 사본에서 자동으로 채우지 않는다.
  - 이전 reader는 S2 규칙에 따라 이 상태를 거부한다(fail closed).
- Owner가 채택하지 않을 때 v1 최소: S2 분류 규칙과 "누락 chunk는 손상"만 둔다. 연결 안내에 "승인 파일의 전후 본문은 계속 보존되며 개별 삭제는 지원하지 않는다. 필요하면 프로젝트 기록 전체 삭제만 가능하다"고 적는다. 나중에 도입할 때는 schema version을 올리는 정상 경로로 추가한다.
- 추가 비용 [판단, 실측 아님]:
  - S2 분류 규칙: 1–2h (채택 여부와 무관하게 필요)
  - 재구성 기반 제거: 8–13h (상태·record·export frame 3–5h, 미리보기·명령·중단·공유 chunk·이전 reader 시험 5–8h)
  - 제자리 삭제 방식: 14–22h로 추정
- Owner 결정 문안 예: "첫 공개에 재구성 기반 개별 본문 제거 운영 명령을 포함한다(완전 삭제 보장 없음, 외부 사본은 별도)" 또는 "첫 공개에서는 제외하고 보존을 고지한다".

### S4. [Medium-High · P2 진입 전 · Owner 실행 승인 필요] 호스트 접근 확인이 너무 늦고 실패 대안이 없다

- 위치: final-direction-check "호스트 접근을 일찍 확인", implementation-plan 순서 보완 "P2의 가장 얇은 실행기/authority 읽기·쓰기 경로가 준비되면".
- 문제 [정적]:
  - 이 확인은 정책 ①(사용자 데이터 위치와 좁은 허용)이 성립하는지를 결정한다. 그런데 계획상 P0·P1과 P2 일부, 약 15–25h를 쓴 뒤에 실행된다.
  - 이 확인에 제품 코드는 필요 없다. 대상 디렉터리에서 SQLite DB와 journal을 만들고, commit하고, 복구하는 정도면 된다. 일회용 스크립트로 충분하다.
  - 실패했을 때의 대안이 미리 정해져 있지 않다. 실패하면 P2에서 멈춘 채 정책 결정을 다시 기다리게 된다.
- 최소 보정:
  1. 이 확인을 P0와 병행하는 별도 실행 묶음으로 Owner에게 제시한다. 실제 호스트 설정 변경을 포함하므로 별도 승인이 필요하다.
  2. 통과 기준을 미리 적는다.
     - 네 호스트 형태의 기본 모드에서, 명령마다 권한 요청이 뜨지 않고 정본 디렉터리에 DB와 journal을 생성·commit·복구할 수 있다.
     - 앱이 만든 worktree 세션에서도 같다.
     - 호스트를 재시작한 뒤에도 허용이 유지된다.
     - 형제 디렉터리 쓰기는 여전히 거부된다(허용 범위가 좁은지 확인).
  3. 실패 시 대안을 Owner 결정용으로 미리 둔다.
     - (a) authorities 루트 전체 허용: 범위가 넓어진다.
     - (b) 해당 조합은 명령마다 권한 확인을 받는 "제약 있음"으로 둔다.
     - (c) 해당 조합은 지원 밖으로 둔다.

     store 계층(P1)은 위치와 무관하므로 어느 결과든 P1 작업은 버려지지 않는다.

### S5. [Medium · P2·P3 전 · Driver] 새 worktree가 생길 때마다 연결 확인을 다시 받을 수 있다

- 위치: C1 "Creation/removal of locators occurs only in an explicitly authorized connection operation", "A nested app worktree is a boundary only after this proof".
- 반례 [정적]:
  1. 앱이 이미 연결된 프로젝트에 새 worktree를 만들고 그 안에서 세션을 시작한다. 그 workspace는 아직 정본에 등록되지 않았다. 등록이 "명시적 연결 동작"이라면, worktree를 새로 만들 때마다 사람에게 연결 승인을 다시 받는다. 요청 우선순위 4의 "이미 유효한 승인 반복 없음"과 충돌한다.
  2. 연결할 때 AGENTS.md 같은 project entry를 고쳤지만 commit하지 않았다. 이 상태에서 앱이 HEAD 기준으로 worktree를 만들면, 그 worktree에는 Colvia 진입 안내가 없다. 그 세션의 에이전트는 Colvia를 쓰지 않고 작업한다. 작업은 진행되지만 기록과 범위 보호가 조용히 빠진다.
- 최소 보정:
  - (1) 이미 연결된 common-dir에 속하고 Git worktree 등록이 확인된 linked worktree는, 처음 사용할 때 자동으로 새 workspace로 등록한다. 이것은 정본 쓰기일 뿐이며 locator 쓰기나 Git 쓰기가 아니다. 사람의 연결 승인은 요구하지 않는다. 다른 저장소·orphan·모호한 경우는 지금처럼 거부한다.
  - (2) 연결 결과 안내에 "진입 안내 변경을 commit해야 새 worktree에도 적용된다"는 다음 행동을 넣는다. 또 Colvia가 실행될 때 현재 workspace의 entry가 연결 당시와 다르면 짧게 알린다. Colvia가 실행되지 않는 세션은 감지할 수 없다는 한계도 사용자 문서에 적는다.
- 시험: 연결 후 새 linked worktree에서 추가 승인 없이 첫 Work 진행. 다른 저장소의 nested 폴더는 거부. entry를 commit하지 않은 상태에서 만든 worktree에 대한 안내.

### S6. [Medium · P8 전 · Driver] 중단 후 남은 `index.lock`이 사용자의 Git을 막는다

- 위치: C6 protocol 2–4, 중단 분류 표.
- 반례 [외부 지식]: C6는 단계 2에서 대상 index lock을 잡고 단계 4에서 index를 교체한다. 그 사이에 process가 죽으면 `index.lock` 파일이 남는다. 그러면 사용자의 모든 Git 명령이 "다른 git 프로세스 실행 중" 오류로 실패한다. 분류 표는 ref와 index 값만 보고 lock 상태를 다루지 않는다. 그래서 복구가 lock을 남겨 둘지, 지울지, I1을 마저 쓸지 정해지지 않았다.
- 최소 보정:
  - prepared record에 lock 소유 증거를 남긴다(operation ID, lock 파일 identity, 그때까지 쓴 bytes digest).
  - 복구할 때 lock이 우리 것이고 소유 process가 없으면, ref 단계에 따라 처리한다. O이면 lock을 제거한다. N이면 C6 조건을 재확인한 뒤 I1을 완료하거나 lock을 제거하고 "N/I0"로 남긴다.
  - lock이 우리 것이 아니면 건드리지 않고 안내만 한다.
- 시험: 단계 2·3·4 사이마다 kill한 뒤 lock 상태별 복구. 외부에서 만든 lock은 보존.

### S7. [Medium · P5 전 · Driver] 공식 실행의 비밀 패턴 송신 거부가 거부 규칙 목록에서 이름을 잃었다

- 위치: refusal-map RF-27. 대상 source는 `official_controller.py: checked_payload`이지만, 거부 조건 열에는 "Protocol size/deadline/identity mismatch…"만 있다.
- 반례 [지정 입력 밖 source 근거]: 현재 `checked_payload`에는 송신 frame, 도구 결과, 교체 구간 경계를 대상으로 하는 고정 비밀 패턴 검출기가 있다(이전 PATCH로 보강된 거부 의미). 의미 경계 이름에 이것이 없으면, 이식할 때 "프로토콜 크기 검사"로만 옮겨져 비밀 패턴 거부가 조용히 빠질 수 있다. RF-36은 새 safeguard만 다루므로 여기에 해당하지 않는다.
- 최소 보정: RF-27(또는 별도 RF 행)에 "송신·도구 반환·쓰기 예약 전 고정 비밀 패턴 거부, 교체 경계와 escape를 푼 payload 포함, 원문·비밀 hash를 기록하지 않음"을 명시한다. 기존 negative fixture를 RF-T에 연결한다. 검출기의 미탐·오탐 한계는 지금과 같이 유지하며 보호 범위를 넓히지 않는다.

## 3. 권장 보정

| ID | 단계 | 내용 | 최소 보정 |
| --- | --- | --- | --- |
| R1 | P2 | C5 4항 "stale child registrations must first be reconciled"가 Git의 `worktree prune`을 뜻한다면 `.git` 쓰기가 필요하다. 기본 sandbox 세션에서는 그것 때문에 제출이 막힌다 | 조정 대상은 Colvia 정본의 구조 registry이며 Git metadata를 고치지 않는다고 명시한다. Git 쪽 정리가 필요하면 안내만 한다 |
| R2 | P2 | 복사된 root는 쓰기만 거부한다. 읽기에서 원래 프로젝트의 Work를 그대로 보여 주면 D3과 비슷한 혼동이 생긴다 | 복사본에서는 기록을 보여 주지 않고 "연결된 프로젝트의 사본, 미연결"과 다음 행동만 표시한다 |
| R3 | P1 | creation ordinal은 행 속성이고 export 정렬은 digest 기준이다. import 때 ordinal을 어떻게 정하는지 정의가 없다 | ordinal은 로컬 값이며 객체 identity와 export에 포함하지 않는다고 적는다. import는 위상 순서로 다시 부여하고 순환은 거부한다 |
| R4 | P1 | staged chunk를 dedup으로 재사용하는 import가 그 claim을 남기지 않으면, repair가 그 chunk를 지운 뒤 게시가 실패한다(안전하지만 원인이 모호하다) | chunk와 import 사이의 claim을 다대다로 기록한다. repair는 claim이 없는 chunk만 회수한다 |
| R5 | P7 | 관리 도구가 없거나 손상됐을 때의 "authenticated repair path"가 무엇인지 정해지지 않았다 | 신뢰 metadata 저장 위치를 runtime slot과 분리해 repair 후에도 보존한다. repair bundle의 root는 기존 root의 유효한 후속(rotation chain)인지 확인하고, 아니면 명시적으로 경고한다 |
| R6 | P7 | storage summary를 매 transaction마다 counter로 갱신하면 drift 버그가 생길 수 있다 | 가능한 값은 요청 시 SQL 집계로 계산한다. 비싼 값은 추정치로 표시한다 |
| R7 | P2 | WSL: Linux 배포본이 없으므로 실제 위험 경로는 Windows 실행 파일을 WSL에서 호출하는 경우와 프로젝트가 `\\wsl$` 같은 경로에 있는 경우다 | native entry가 프로젝트 root의 경로 종류를 확인해 WSL 공유 경로를 거부하는 것부터 한다. Linux process 검출은 Linux 대상 착수 때 정의한다 |
| R8 | 문서 | final-direction-check 본문은 아직 "50–75/100 유지"라고 쓰는데, implementation-plan은 75–120이 현재 예측이라고 쓴다 | final-direction-check에 "견적은 implementation-plan의 최신 절을 따른다"는 pointer 한 줄을 넣는다 |
| R9 | P2 | 사용자가 Work 도중 workspace 밖의 global ignore를 바꾸면, 거부만 있고 빠져나갈 경로가 없다 | 원복하거나 "남은 작업을 새 기준으로 별도 시작"하는 두 경로를 안내 문구에 정한다 |

## 4. 요청 항목별 확인

- D7 부모 container: `.claude/worktrees/` 처리, 숨김 항목을 포함한 직계 항목 검증, 관측마다 재증명, 비어 있는 이전 container와 다시 생긴 container 구분이 모두 들어 있다. 맞는 보정이다. 실제 앱이 그 container 안에 worktree가 아닌 자체 파일을 두는지는 정적으로 알 수 없다. 그런 파일이 있으면 규칙상 거부되므로 실제 앱 확인 항목으로 둔다. 남은 문제는 R1뿐이다.
- 묶음 쓰기와 EXTRA: 1 MiB chunk, transaction당 4 MiB·64개는 적절하다. `synchronous=EXTRA`와 macOS `fullfsync`를 함께 쓰면 commit마다 강제 sync가 여러 번 일어나 작은 쓰기도 느려진다 [외부 지식]. 정확성을 우선한다는 선택은 타당하다. 측정 항목에 "작은 Work 한 번의 commit 수와 소요 시간"을 넣는다.
- 첫 설치 bundle과 갱신 신뢰: 첫 설치는 HTTPS를 신뢰한다는 가정으로 명시했고, 기존 manager가 서명 metadata를 먼저 검증하며, 같은 명령을 다시 실행해도 약한 경로로 우회하지 않는다. 일관된다. 남은 것은 R5다.
- WSL과 native 구분: 방향은 맞다. R7로 범위를 단순화할 수 있다.
- hook 저장소의 수동 handoff: 부분 staging 보존, hook이 바꾼 결과 확인, `git add .` 금지가 있어 충분하다.
- 검증된 export 상태 표시: 시도와 검증 완료를 구분하고, 대상 존재를 추정하지 않으며, 알림을 만들지 않는다. 적절하다.
- 조회와 전체 감사 분리, 용량, 비 Git, 조기 접근 확인(Driver가 요청한 네 가지 도전 지점):
  - 조회와 감사 분리, 용량 정리, 비 Git 경로: 맞다. 단, edge 역할(S2)이 형식에 들어가야 조회 국소성이 실제로 강제된다.
  - 조기 접근 확인: 방향은 맞지만 시점과 실패 대안이 부족하다(S4).

## 5. 시간 견적

- 75–120h 예측에서 P4·P5·P7 보정은 반영됐다. 그 밖에 낙관적인 단계 [판단]:
  - P3 5–8h: 일반 Work, intent, 보완·수락, 조회·View, archive, 후보·후속을 모두 포함한다. 8–14h로 본다.
  - P6 3–5h: 맡기기 DB를 정본으로 합치는 일, 늦은 응답·불명 효과, 알림 연결을 포함한다. 5–9h로 본다.
  - P9 6–9h: 누적 회귀, 규모 비교, 패키지, 한영 사용자 문서 전면 갱신, 리뷰 반영을 포함한다. 문서만으로도 상당하다. 10–16h로 본다.
- 이번 지적으로 늘어나는 양: S1 2–4h, S2 1–2h, S5 2–3h, S6 2–3h, S7 1h. S3을 채택하면 8–13h가 추가된다. S4 확인은 실제 qualification 예산에서 앞당겨 쓰는 것이며 Owner 대기는 별도다.
- 위 항목을 반영한 내 판단은 약 90–145h(본문 제거 제외)다. 제안 중단 상한 100h는 예상 범위의 중간보다 낮다. 그러므로 P3 뒤 재산정에서 상한을 조정할지 Owner가 결정할 가능성이 높다는 점을 지금 명시해 두는 게 좋다. 상한을 자동으로 늘리라는 권고가 아니다.
- 실제 qualification 12–20h(상한 28h)를 구현과 분리한 구성은 적절하다.

## 6. 최소 보정 목록

1. S1 symlink·gitlink를 보호 대상 opaque entry로 처리 (P1 전, Driver 결정)
2. S2 참조 edge 역할과 모르는 종류 분류 규칙을 v1에 넣음 (P1 전)
3. S3 본문 제거 정책 결정: 재구성 기반 채택 또는 제외·고지 (P1 전, Owner)
4. S4 호스트 접근 확인을 P0와 병행하는 별도 실행으로 앞당기고, 통과 기준과 실패 대안을 미리 정함 (P2 전, Owner 실행 승인)
5. S5 확인된 linked worktree 자동 등록, entry commit 안내 (P2·P3 전)
6. S6 `index.lock` 소유 기록과 중단 복구 (P8 전)
7. S7 RF-27에 비밀 패턴 송신 거부 명시 (P5 전)

## 7. 권장 구현 순서

```text
P0 회귀 기준 고정 ─┬─ (병행) S4 호스트 접근 확인 — Owner 실행 승인 후
                   └─ Owner 결정: S3 본문 제거 정책 / Driver 결정: S1 entry 범위
P1 store·trie·chunk (S1·S2·S3 결정 반영, R3·R4)
P2 정본 연결·관측 (S4 결과 반영, S5-1, R1·R2·R7·R9)
P3 일반 Work (S5-2) → 재산정, 상한 조정 여부 Owner 확인
P4 worker·umbrella → P5 공식 실행 (S7) → P6 맡기기·알림
P7 export·갱신·bootstrap·서명 (R5·R6, S3 채택 시 제거 명령)
P8 Git 통합 (S6)
P9 누적 회귀·문서·결과 리뷰 → 별도 qualification 묶음
```

구조적 blocker는 없다. 위 보정을 해당 단계 전에 반영하면 이 방향으로 단계별 구현을 시작할 수 있다. 성능 수치와 플랫폼별 지원은 이 검토로 보증되지 않으며, P1·P2 측정과 실제 qualification에서 확인해야 한다.
