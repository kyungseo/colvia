# R3b 응답 — 네 잔여 질문의 집중 정확성 검토

작성 2026-11-06 · Reviewer: Claude Opus 5.5 (`claude-opus-5-5`) · session identity: 확인 불가(harness가 제공하지 않음)

이 문서는 Reviewer 의견이다. Driver 처분, Owner 결정, 구현 승인, 결과 수락을 대신하지 않는다.

## 0. 검토 조건

- 독립성: 이 대화는 새 대화다. R2·R3a 응답이나 비공식 방향 의견을 이 대화에서 작성하지 않았다. 이전 대화의 기억은 이 대화에 주어지지 않았다. 요청 순서대로 R3a 판정은 내 판단을 정리한 뒤 마지막에 읽었다.
- 접근 범위: 요청서, manifest, manifest의 6개 파일만 읽었다. 그 밖의 source, 개발 기록, 저장소, 설정은 열지 않았다. 다른 model이나 agent는 호출하지 않았다.
- 입력 drift: 검토 전후 6개 파일의 SHA-256과 byte 수가 manifest와 모두 일치했다(drift 0). 요청서 SHA-256 앞자리는 `653bb4808de4`, manifest는 `50bb0a49b128`이다.
- 실행: 제품 명령, 시험, 설치, 네트워크, model 호출은 하지 않았다. 각 지적에 근거 종류를 붙였다.
  - `[정적]`: 입력 문서와 excerpt에서 추론한 내용
  - `[외부 기억]`: Git·SQLite·OS 동작에 대한 기억. 이번에 확인하지 않았다.
  - 재현된 실패는 없다. 측정이 빠졌다는 사실을 실패가 재현된 것으로 다루지 않았다.
- 확인 불가로 남긴 것: `official_documents.py: safe_text`의 실제 검출·decode 범위. excerpt에 없으므로 열지 않았다(Q4-b 참조).

## 1. 판정

판정: 해당 단계 전 필수 보정(corrections before affected phase). 구조적 blocker는 없다.

- 네 방향은 모두 유지할 수 있다. protected opaque entry, generic edge envelope, 조기 host 진단, index lock 소유 복구가 그것이다. 각 amendment는 R3a의 지적을 대부분 실제 계약 문장으로 바꿨다.
- 남은 빈틈은 대부분 문장 수준의 보정이다. 다만 하나는 본문 제거 여부와 무관하게 P1 store 배치(layout)에 영향을 준다. C4의 restore·migration 활성화를 같은 SQLite 경로 위에서 rename으로 하면 열린 handle·journal 짝 문제가 생긴다(M3). 이것은 제거 제안을 검토하다 드러났지만 C4 자체의 결함이다.
- 본문 제거는 Owner 선택으로 남긴다. 내 권장은 첫 공개에서 보존을 유지하고 그 한계를 고지하는 것이다(§3). 제거를 나중에 넣어도 형식 호환이 깨지지 않기 때문이다.

권장 경로 한 줄: M1–M6을 각 단계 전에 C1–C8·refusal map·시험 계획에 반영한다. Owner는 보존 유지(권장)와 최소 제거 명령 중 하나를 고르고, 조기 진단의 실행 범위·예산을 정한다. 그 뒤 P0부터 시작한다.

| 구분 | 항목 |
| --- | --- |
| Driver 보정 | M1 opaque entry 경계, M2 edge envelope, M3 store 활성화·fence, M4 진단 계획 보완, M5 Git lock 복구, M6 RF-27 문구 |
| Owner 선택 | 본문 제거 포함 여부, 조기 진단의 실제 실행 범위·예산, 100시간 중단 상한에 도달했을 때의 처리 |

## 2. 필수 보정

### M1. [Q1 · P1 형식 고정 전, P2/P8 시험] opaque entry의 추가·종류 변경·조상 경로 규칙과 submodule 관측 정책

방향 판단: 내용 보존을 주장하지 않는 protected opaque entry는 안전하다. 단, 아래 네 빈틈을 닫아야 한다. "superproject Work는 submodule이나 symlink 대상의 내용을 보존·승인하지 않는다"는 고지는 정확하고 필요하다.

a. 추가·종류 변경과 조상 경로 `[정적]`
- 조항: disposition A "Missing/changed opaque entries are out-of-scope changes", "Opaque paths cannot be selected for edit, materialization or changed Git integration".
- 실패 1: 에이전트가 승인 범위 안의 일반 파일을 symlink로 바꾸거나, 새 symlink·gitlink를 추가한다. "missing/changed"에는 추가와 종류 변경이 명시되지 않았다. 승인 범위 안의 경로라서 범위 밖 변경으로 분류되지 않을 수 있다. 그러면 수락할 수 없는 opaque entry가 결과에 들어간다.
- 실패 2: 원본 workspace에서 수락된 `docs/a.md`를 적용하거나 통합한다. 그런데 대상 workspace나 대상 HEAD에서는 `docs`가 symlink 또는 gitlink다. "opaque path"를 그 경로 자체로만 읽으면 조상 경로를 통한 쓰기를 막는 문장이 없다. 그러면 symlink를 따라 project 밖에 쓰거나, C6 후보 tree에서 D/F 충돌이 생긴다. C2의 "revalidate ancestry"가 일부를 막지만 opaque 규칙과 연결되어 있지 않다.
- 최소 보정:
  - opaque entry의 추가·제거·변경·종류 변경(regular↔symlink, directory↔gitlink)은 위치가 승인 범위 안이어도 모두 refuse한다.
  - 선택 경로가 원본 tree, 대상 HEAD, 대상 index, 대상 working tree 중 어느 하나에서라도 opaque entry이거나 그 아래에 있으면 refuse한다. 반대 방향 D/F 충돌도 refuse한다.
- 시험: 승인 경로를 symlink로 바꾸기, 새 gitlink 추가, 대상에서만 조상이 symlink 또는 gitlink인 경우의 적용과 통합.

b. submodule의 dirty 판정이 설정으로 숨겨질 수 있음 `[정적 + 외부 기억]`
- 조항: disposition A "inspect verified topology, checkout HEAD and dirty/untracked state under a defined, non-mutating observation policy".
- 실패: superproject 쪽 `submodule.<name>.ignore=all|dirty|untracked`이나 `diff.ignoreSubmodules`가 설정되어 있다고 하자. `submodule.<name>.ignore`는 `.gitmodules`나 Git metadata의 config에 있다. 또는 submodule 자체의 `info/exclude`, `.gitignore`, `status.showUntrackedFiles`가 바뀐다. 그러면 기본 status는 submodule을 깨끗하다고 보고한다 `[외부 기억]`. 그 결과 gitlink OID가 그대로인 상태에서 submodule 안의 추적 파일 편집이 통과한다. C5가 고정하는 정책 입력은 superproject만 다룬다.
- 최소 보정:
  - submodule 관측은 위 설정을 명시적으로 무효화한다. 예를 들어 `--ignore-submodules=none`, untracked 전체 표시 같은 고정 override를 쓴다.
  - submodule 내부의 ignore와 config 출처는 C5와 같은 방식으로 고정 정책 입력에 넣는다. 이것이 바뀌면 dirty나 inspect 불가로 처리한다.
  - nested submodule은 재귀 관측하거나, 첫 구현에서는 refuse한다.
  - 초기화되지 않은 상태와 초기화된 상태 사이의 전환이 Work 중에 일어나면 범위 밖 변경으로 처리한다.
  - dirty·inspect 불가 판정은 제출 때뿐 아니라 Work 시작(scope 승인) 때도 보여 준다. 그래야 결국 거부될 작업을 사용자가 시작하지 않는다. 이것은 권장 사항이다.
- 시험: ignore 설정으로 숨긴 submodule 편집, submodule exclude 변경, nested submodule, Work 중 init/deinit.

c. Windows의 `core.symlinks=false` placeholder `[외부 기억]`
- 조항: disposition A "Windows link emulation and reparse points require platform-specific evidence".
- 실패: Windows에서 symlink 생성이 꺼져 있으면 Git은 index mode `120000` entry를 대상 문자열이 담긴 일반 파일로 checkout한다. C2의 "Git/native mode evidence must agree"만 적용하면 두 결과가 나올 수 있다. 하나는 이 저장소 전체를 쓸 수 없게 되는 것이다. 다른 하나는 placeholder를 일반 파일로 보고 편집을 허용하는 것이다. 후자는 opaque 보호를 우회한다.
- 최소 보정:
  - index `120000`과 native 일반 파일의 조합은 Windows 정책에서 "emulated symlink"로 분류한다.
  - 그 파일의 bytes는 symlink 대상 문자열로 비교한다. 편집은 opaque 변경으로 refuse한다.
  - 비 Git 폴더의 Windows reparse point는 정본 대상 문자열을 정할 근거가 없다. print name과 substitute name이 다를 수 있기 때문이다. 따라서 첫 구현에서는 지금처럼 refuse한다. macOS 비 Git symlink는 대상 문자열 bytes로 기록할 수 있다.
- 시험: placeholder 편집, 실제 NTFS symlink, junction refuse.

d. 대체되는 기존 거부 규칙을 명시 `[정적]`
- 다음 문장은 opaque entry를 refuse한다고 적고 있다. disposition은 이것을 바꾼다고 말하지만, 대체 목록에 올라 있지 않다.
  - C2 entry mode 집합
  - C6 "no ... submodule ... in the operation"
  - RF-04/RF-T04 "unsupported file kinds refuse"
  - RF-13 제목
  - 현재 source의 `_regular_files`, tracked-entry mode 검사, Windows index 분류기(`mode not in (100644, 100755)`)
- 최소 보정:
  - refusal map의 "Intentional replacement" 절에 한 줄을 넣는다. symlink와 gitlink는 opaque로 받아들이고, special device·multiple link·reparse·알 수 없는 종류는 계속 refuse한다고 적는다.
  - C6의 문구를 바꾼다. "변경된 gitlink 또는 gitlink 아래 선택 경로는 refuse, 변경 없는 gitlink·symlink index entry는 flag까지 그대로 보존"으로 쓴다.
  - C6 후보는 대상 HEAD tree에 선택 경로만 적용해 만든다. 그러므로 변경 없는 opaque entry는 구성상 그대로 남는다. 시험에서는 I1의 `160000`/`120000` entry가 I0와 byte 단위로 같은지만 확인하면 된다.

### M2. [Q1 · P1 형식 고정 전] edge envelope: 역할 고정, 순서 의미, import 깊이, 숨은 참조

방향 판단: role과 ref를 분리하고, digest에 role을 포함하고, 모르는 role을 refuse하는 규칙은 옳다. 다만 아래 네 항목이 있어야 "결정 의존을 낮춰 적을 수 없다"는 성질이 실제로 강제된다.

a. field마다 역할을 하나로 고정 `[정적]`
- 조항: "Parent kind/version/field schemas specify permitted roles".
- 실패: 어떤 field가 `{decision, provenance}`처럼 둘 이상의 역할을 허용한다고 하자. writer가 `provenance`를 고르면, 선택 조회 국소성 규칙 때문에 reader가 그 의존을 검증하지 않고 지나간다. "required fields cannot be weakened"는 필수 field의 존재만 보장한다. 역할 선택까지 막지는 않는다.
- 보충: "If an operation needs provenance to justify its decision, that dependency is required regardless of its label"은 구현자가 operation마다 판단하게 만든다.
- 최소 보정:
  - v1에서는 `(kind, version, field)`마다 역할을 정확히 하나로 정한다. 다른 역할 label은 schema 위반으로 refuse한다.
  - operation별 필수 closure는 정적 표로 정의한다. 형식은 operation → 필수 (kind, field) 집합이다. label은 그 표와 일치하는지 검사하는 대상이지 판단의 근거가 아니다.
- 시험: 역할을 낮춘 edge를 쓰는 writer는 refuse, 역할을 낮춘 import도 refuse.

b. 의미 있는 순서는 local ordinal에 두지 않음 `[정적]`
- 조항: "Creation ordinals are derived local storage values ... Restore ... assigns fresh topological ordinals".
- 실패: 같은 결과에 대한 두 결정이나 두 후속 항목처럼 edge로 연결되지 않은 형제 객체의 앞뒤를 ordinal로 정한다고 하자. 그러면 restore 뒤 다른 위상 순서가 매겨져 "현재 결정"이 바뀔 수 있다.
- 최소 보정: 대체(supersede), 최신, 표시 순서처럼 의미가 있는 순서는 hash된 객체 안의 edge나 sequence field, 또는 root map의 head로만 표현한다. ordinal은 쓰기 때의 순환 방지와 저장 효율에만 쓴다.
- 시험: 같은 export를 서로 다른 위상 순서로 restore해도 모든 조회 결과가 같아야 한다.

c. import의 위상 검증은 결정 traversal 깊이 64에 묶지 않음 `[정적]`
- 조항: C3 표 "Graph depth 64 ... per bounded decision traversal", disposition "Restore validates generic edges, rejects cycles".
- 실패: 개정이나 provenance chain이 64보다 긴 오래된 project가 있다. 깊이 64 검증기를 import에 그대로 쓰면 정상 backup을 restore할 수 없다. export frame은 위상 순서가 아니라 kind/version/digest 순서다. 그래서 import는 전체를 staging한 뒤 반복적으로 검증해야 한다.
- 최소 보정: import·전체 감사는 C3의 전체 객체·bytes 예산 안에서 반복 위상 정렬로 검증한다. 깊이 64는 결정 traversal에만 적용한다.
- 시험: 길이 65 이상인 chain의 export/restore, 순서를 섞은 frame.

d. 숨은 참조 금지를 강제하는 방법 `[정적]`
- 조항: "no hidden authoritative object references inside opaque payloads".
- 실패: 알려진 kind의 payload 안에 reference 형태의 값이 envelope 밖에 들어 있다. export reachability는 그 대상을 놓친다. restore 뒤 새 runtime이 dangling 참조를 만난다.
- 최소 보정:
  - payload는 다른 객체를 envelope의 edge index로만 가리킨다.
  - 알려진 kind의 validator는 payload 안의 raw reference 객체를 refuse한다.
  - 모르는 optional kind의 숨은 참조는 검증할 수 없다. 이것은 writer conformance 시험과 남는 한계로 명시한다.

참고(필수 아님): 모르는 role을 refuse하면 이후 version이 선택 data에 새 role을 추가하는 것도 required-feature 증가가 된다. C4의 rollback 조건과는 일관된다. 의도된 trade-off로 한 줄 적어 두면 된다. 모르는 kind를 건너뛸 수 있는지는 그 객체가 아니라 그것을 가리키는 알려진 부모 edge의 역할로 정한다는 점도 같은 문장에 넣으면 된다.

### M3. [Q2에서 발견, 제거와 무관 · P1 store 배치 고정 전, P7 시험] 열려 있을 수 있는 SQLite 경로를 rename이나 unlink로 교체하지 않음

- 조항:
  - C1 "The authority contains `state.sqlite3` and SQLite-owned transient journal files"
  - C4 "migrate to a separate store, validate it, then activate one binding"
  - C1 restore 활성화
  - disposition B의 cutover
- 문제 `[정적 + 외부 기억]`: 새 store를 어디에 두고 어떻게 활성화하는지 정해져 있지 않다. 가장 자연스러운 구현은 새 파일을 `state.sqlite3`로 rename하는 것이다. 그런데 SQLite 문서는 다음을 손상 원인으로 든다 `[외부 기억]`.
  - 사용 중인 DB 파일의 rename·unlink
  - 다른 DB와 짝이 맞지 않는 hot journal
- 구체 실패: 옛 inode를 연 채로 남은 process가 있다고 하자.
  - 그 process가 쓰기를 시작하면 이름 기반 `state.sqlite3-journal`을 만든다. 그 이름은 이제 새 DB와 짝이 된다. 그 process가 중간에 죽으면 새 DB가 남의 journal로 rollback된다.
  - 반대로, 옛 handle의 reader가 새 DB writer의 journal을 hot journal로 오인할 수 있다. POSIX advisory lock은 inode 단위라 서로의 lock이 보이지 않기 때문이다. 그러면 reader가 그 journal을 옛 파일에 적용하고 지운다.
  - Windows에서는 열린 파일 교체가 sharing violation으로 실패할 수 있다 `[외부 기억]`.
- 이 문제는 본문 제거가 없어도 C4 restore·schema migration 활성화에서 똑같이 생긴다.
- 최소 보정:
  1. store 파일은 세대 이름으로 둔다. 예: `state-<generation>.sqlite3`. authority 안의 작은 active pointer는 원자적으로 교체하고 동기화한다. 같은 성질을 주는 동등한 방식도 된다. 이에 맞춰 C1의 "contains state.sqlite3" 문장을 고친다.
  2. 활성화 직전에 옛 store에 마지막 쓰기로 fence(retired, 후속 generation)를 기록한다.
  3. 모든 transaction은 시작할 때 fence를 확인한다. C3의 "pinned root 뒤 immutable closure를 paging하는 read"도 page마다 다시 확인한다. 불변성만으로는 retire된 store를 계속 읽어도 된다는 근거가 되지 않는다.
  4. 쓰기 경로는 page를 수정하기 전에 fence를 확인한다.
  5. 옛 파일 삭제는 별도 상태다. 실패하거나 아직 처리되지 않은 상태를 "retire 대기"로 보고한다.
- 시험(P1 harness, P7에서 재사용):
  - 활성화 경계마다 kill
  - 옛 handle에서 read 계속, 옛 handle에서 write 시도
  - 활성화 직후 hot journal이 남은 경우
  - Windows에서 열린 옛 파일 삭제
- 비용: P7의 restore·migration 활성화에 원래 들어 있어야 할 일이다. 새 범주라기보다 P1 배치 결정을 앞당기고 fault 시험을 늘리는 일이다(§5).

### M4. [Q3 · 진단 실행 제시 전] 조기 host 진단 계획 보완

방향 판단: 이 진단은 sandbox 동작을 가정하지 않는다. 기준선 기록, 기준선이 실제로 격리할 때만 형제 거부를 시험, 실제 설치 검증과의 분리, broader grant의 Owner 선택이 모두 들어 있다. 진단이 실제 설치 검증을 대신하지 않는다는 점도 명시되어 있다. 다만 결과를 과하게 읽거나 흔적이 남는 것을 막는 다음 항목이 빠졌다.

a. 전이 표 `[정적]`: 범용 probe에서 얻은 결과 가운데 최종 managed entry로 옮겨 쓸 수 있는 것과 없는 것을 미리 적는다.
- 옮겨 쓸 수 있을 가능성: path 기반 쓰기 허용, DB·journal 생성·삭제·동기화, 재시작 뒤 유지
- 옮겨 쓸 수 없는 것: 명령 문자열이나 실행 파일 기준의 허용 규칙, macOS quarantine·서명, launcher routing

이 표가 없으면 "명령마다 다시 묻지 않음"이라는 결과가 probe 명령에서만 성립한 것인지 구분할 수 없다.

b. 원복 계획 `[정적]`: 진단은 실제 OS data 경로에 fixture authority를 만들고 host 허용을 추가한다. 실행을 제시할 때 다음을 함께 적는다.
- 추가할 허용과 fixture 경로
- 종료 후 원복 절차
- 원복 확인 방법: host 설정 파일의 전후 비교. 쓰기 probe만으로 확인하지 않는다.
- 원복에 실패했을 때 보고하는 방식

"새 허용이 의도하지 않은 경로를 더하지 않음"도 설정 diff로 확인한다. 특히 한 authority 허용이 형제 authority나 authorities 루트를 덮지 않는지 본다.

c. 형제 linked worktree `[정적]`: app worktree는 nested지만 sibling linked worktree 세션은 common dir이 세션 root 밖에 있다. C1 시험 목록에도 sibling이 있다. 다음을 진단 항목에 넣는다.
- 그 세션에서 common dir과 worktree 목록을 읽을 수 있는지
- Git 실행 파일을 해석할 수 있는지
- 첫 등록이 authority 쓰기만 필요하고 Git metadata 쓰기는 필요 없는지

d. 대상 축소는 Owner 결정 `[정적]`: 다음 문장을 추가한다. "실패한 조합을 첫 공개 대상에서 빼거나 '제약 있음'으로 표시하는 것은 Owner 결정이며, 근거와 함께 기록한다." 지금 문장은 broader grant와 구조 변경만 Owner 선택으로 둔다. 실패한 조합을 대상에서 조용히 빼는 길은 막지 않는다. authority를 workspace 안으로 옮기는 대안도 Owner 정책 ①을 바꾸므로 같은 분류에 넣는다.

e. 범위 표시 `[정적]`: 확보된 OS·architecture에서만 진단을 실행했다면, 결과를 첫 공개 target 전체의 가능성으로 보고하지 않는다. Windows x64 환경이 미확보일 수 있다는 점은 plan에 이미 있다. 이 점을 진단 결과의 cell에 표시한다.

읽기 전용 해석과 첫 승인 등록(S5): disposition C의 문장으로 충분하다. 확인된 linked worktree는 읽기에서만 잠정 해석하고, 첫 승인 상태 변경 때 membership과 generation을 다시 확인하고 등록한다. 복사본은 등록하지 않는다. 추가할 시험은 두 가지다.
- 같은 새 worktree에서 두 세션이 동시에 첫 등록
- 등록 직전 worktree가 제거되거나 다른 저장소로 교체된 경우

entry 누락: "entry commit 필요 안내, 자동 commit 금지, 실행되지 않은 세션은 감지 불가" 세 가지로 충분하다. 필수 보정은 없다.

### M5. [Q4 · P8 전] Git lock 복구의 남은 경계

방향 판단: 배타 생성, 지속 소유 기록, file identity, process-start identity, 증명되지 않은 lock 보존, 교체된 lock 보존은 모두 맞다. 다만 다음 항목이 빠졌다.

a. 생성 전 의도 기록과 알 수 없는 생존 상태 `[정적]`
- 실패: lock을 만든 뒤 소유를 기록하기 전에 죽으면 그 lock은 증명되지 않은 상태로 남는다. 이때 Colvia가 만든 것인지 외부가 만든 것인지 구분할 근거조차 없다. 또 sandbox 안에서는 다른 process를 조회할 수 없을 수 있다. 이 경우 생존 여부를 확인할 수 없다.
- 최소 보정:
  - O_EXCL 생성 직전에 operation ID, 대상 path, nonce를 담은 의도 record를 짧은 transaction으로 지속 저장한다. 그러면 증명되지 않은 lock을 "Colvia 가능성 있음"과 "외부"로 나눠 안내할 수 있다. 소유 증명 자체는 여전히 생성 뒤 identity 기록이 필요하다.
  - 생존 여부를 확인할 수 없으면 살아 있는 것으로 본다.

b. Git 하위 process가 남기는 ref lock `[정적 + 외부 기억]`
- 실패: C6 단계 3의 ref CAS는 Git process(`update-ref` 같은 것)가 수행한다. 그 process가 중간에 죽으면 다음 lock이 남을 수 있다 `[외부 기억]`.
  - `refs/heads/<branch>.lock`
  - `packed-refs.lock`
  - `HEAD.lock`

  이 lock들도 사용자의 Git을 막는다. disposition D는 index lock만 다룬다.
- 최소 보정:
  - 실행 중인 Git 하위 process를 시간 초과만으로 kill하지 않는다. C3의 "duration만으로 commit 중단 금지"와 같은 원칙이다.
  - 중단 뒤 ref·packed-refs·HEAD lock이 있으면 "Git 동작 중단, lock 존재"로 분류한다. 자동으로 지우지 않는다.
- 시험: ref 갱신 중 kill.

c. 인계 방식은 하나로 정하고, rename 뒤 bytes 검증은 필수 `[정적]`
- 문제: 죽은 소유자의 lock을 이어서 쓸지, 지우고 다시 잡을지 두 경로가 모두 열려 있다. POSIX에는 handle 기준 rename이 없어 path 경쟁이 남는다 `[외부 기억]`.
- 최소 보정:
  - 한 경로를 고정한다. 권장은 소유 증명 → 증거 보존 → 제거 → O_EXCL 재획득 → I1 기록이다.
  - rename 뒤 index bytes가 I1 digest와 같은지 확인한다. 다르면 외부 분기로 분류한다. C6 단계 4의 "verify ref/index"를 이 digest 비교로 구체화한다.

d. Windows에서 ref CAS 뒤 index 교체 실패 `[외부 기억]`
- 실패: 다른 process(IDE, Git 관리 도구)가 `index`를 공유 삭제 없이 열고 있으면 교체가 sharing violation으로 실패할 수 있다. 그러면 상태가 N/I0이고 lock은 살아 있는 Colvia가 쥔 채로 남는다.
- 최소 보정: 짧고 유한한 재시도 뒤 처리 방식을 정한다. index가 여전히 I0이면 Colvia lock을 해제하고 N/I0을 명시적 복구 대상으로 보고하는 방식이 권장이다. 사용자 Git을 오래 막지 않기 위해서다.
- 시험: 교체 순간 `index`를 다른 handle이 연 상태.

e. 증명되지 않은 lock의 사용자 경로 `[정적]`
- 다음 정보를 짧게 보고한다.
  - 어느 lock인지
  - 왜 증명되지 않았는지
  - 의도 record가 있는지
- 사용자가 다른 Git process가 없음을 확인한 뒤 직접 지우는 것이 표준 해결이라고 안내한다. Colvia는 지우지 않는다. 지금은 "자동 삭제 안 함"만 있고, 사용자가 다음에 무엇을 할지가 없다.

부분 index와 ref 상태: index 교체는 rename이므로 `index`에 부분 상태가 생기지 않는다. 부분 상태는 lock 내용에만 생긴다. 기존 O/I0, N/I0, N/I1, O/I1, 외부 분기 표에 다음 열 하나만 추가하면 된다: lock(index, ref) 상태 = 없음 / 소유 증명 / 증명 안 됨 / 교체됨.

### M6. [Q4 · P5 전] RF-27 문구가 excerpt의 기존 의미를 모두 담지 않음

방향 판단: 고정 비밀 패턴, nested escape, 결합 결과, 늦은 효과의 의미는 대체로 옮겨졌다. excerpt와 대조하면 다음이 빠졌거나 모호하다. 모두 기존 의미를 유지하는 일이며 새 PII 기능이 아니다.

a. 식별자 guard 누락 `[정적]`: `checked_payload`는 data payload(`protocol=False`)에서 home 경로, drive 경로, email 형태를 `unapproved document identifier`로 refuse한다. 시험 `test_send_checks_nested_json_escapes_and_identifiers`도 home 경로를 refuse한다. amendment는 "secret-pattern"만 말하므로, 이식할 때 이 guard가 빠질 수 있다.
- 보정: RF-27에 "data payload의 고정 식별자 guard, protocol frame은 필요한 runtime 경로만 예외"를 넣는다. 다음 두 문장도 그대로 옮긴다.
  - "식별자 예외는 secret 검사를 끄지 않음"(source 주석)
  - "식별자 검사는 bounded 형태로 유지"

b. 검출 주체 누락 `[정적, 일부 확인 불가]`: 검출은 `_CREDENTIAL`과 `official_documents.py: safe_text`가 함께 한다. FAKE 문자열과 `sk-` 경계 결합 사례는 excerpt의 `_CREDENTIAL`에 없는 형태다. 따라서 `safe_text`가 검출하는 것으로 추정한다. nested `\u` escape decode도 `safe_text` 쪽으로 보인다.
- 보정: RF-27 source pointer에 `safe_text`를 추가한다. "supported nested decoding" 대신 현재 시험된 decode 형태를 이름으로 적는다.
- 한계: `safe_text`의 실제 범위는 이번에 확인하지 않았다.

c. 실행 전 보존 문맥 검사 누락 `[정적]`: `checked_preserved_output`은 교체 구간 밖의 앞뒤 문맥을 CLI 허용과 시작 전에 검사한다. 한도는 262,144다. amendment의 "composed replacement content before its write reservation"은 실행 뒤 결합 검사만 말한다.
- 보정: "실행 허용 전 보존 문맥 검사"와 "writer 전 완전한 새 출력 재검사"를 둘 다 적는다.

d. 관측 가능한 기준을 정확히 `[정적]`
- 거부된 frame은 첫 byte도 쓰지 않는다. 앞서 전달된 frame·byte 수는 바뀌지 않는다. 거부 응답은 고정 사유(`content_rejected`)만 담고 원문을 되돌려 보내지 않는다.
- "before its write reservation"은 시험 기준으로 바꾼다. 시험 `test_actual_boundary_join_refused_before_write_reservation`에서 callback 예약 행은 1개 존재하고 recovery-ready 행은 0개다. status는 interrupted, 효과는 none, 원본 bytes는 그대로다. 새 상태 기계의 이름으로 이 관계를 고정한다.
- "Do not log"를 "rejected 원문과 그 hash를 run·journal·evidence 어떤 파일에도 남기지 않음"으로 넓힌다. 시험은 run 디렉터리 전체에 FAKE가 없는지 확인한다.
- 늦은 거부는 earlier applied를 none으로 바꾸지 못한다. 또 clean completion도 아닌 interrupted로 끝난다.

e. 구조 한도 `[정적]`: depth 16, node 4,096, 제어 문자 refuse(`\n\r\t` 제외), 문자열 key, 정수 범위, 기본 한도 65,536을 RF-27의 "size"에 포함한다고 명시한다. 이 한도들이 새 serializer에서 다르게 바뀌면 그 이유를 기록한다.

## 3. Q2 본문 제거 — 보존 유지와 재구성 제안의 비교 (Owner 선택)

### 판단의 요지

- 보존을 유지해도 첫 공개 형식에 추가할 것이 없다. 나중에 제거를 도입하면 새 required feature가 된다. 이전 runtime은 C4 규칙에 따라 해당 store를 refuse한다. 이전 backup은 그대로 읽힌다. 따라서 제거를 미뤄도 첫 공개 호환을 해치지 않는다 `[정적]`.
- 재구성 제안의 원칙은 맞다. 제자리 변경 금지, overlay, 공유 chunk 미리보기, 옛 backup 한계 고지, 물리적 삭제를 약속하지 않음이 그것이다. 그러나 활성화와 retire는 M3을 먼저 풀어야 안전하다. 또 아래 a–e가 추가로 필요하다.
- 권장: 첫 공개는 보존을 유지하고 고지한다. M3은 C4를 위해 어차피 구현한다. 그러면 이후 제거 명령의 가장 위험한 부분이 미리 해결된다. 단, Owner가 "실수로 보존된 credential 본문을 개별 제거할 수 없는 상태"를 공개 차단 사유로 본다면 아래 최소 범위를 택한다.

### 제거를 택할 때 추가로 필요한 것 `[정적]`

a. overlay와 불변 root
- 재구성된 store에는 제거 이전 root를 옮기지 않는다. 그러면 옛 root를 따라가 overlay를 우회할 수 없다.
- overlay map은 이후 모든 root에서 단조 증가만 허용한다. 줄이는 쓰기는 CAS 단계에서 refuse한다.
- 감사에서 "chunk가 없는 descriptor"는 그 root의 overlay가 덮을 때만 유효하다. 그 밖에는 지금처럼 손상이다.

b. digest가 남음
- C2 identity를 유지하려면 tree leaf, descriptor, chunk 참조의 SHA-256이 남는다. 짧은 credential 파일이라면 digest가 추측 확인 수단이 된다. RF-27은 비밀의 hash를 남기지 않는 쪽을 택했으므로, 같은 기준에서 이것은 남는 노출이다.
- identity를 바꾸지 않는 한 이 노출은 제거할 수 없다. 미리보기와 문서에 이 한계를 고지한다. digest 재계산은 이력 재작성이므로 범위 밖이다.

c. locator와 instance
- C1 locator에는 `authority_instance_uuid`와 `binding_epoch`가 들어 있다. 제거를 새 instance로 처리하면 모든 workspace locator를 다시 써야 한다. 그러면 Git dir 쓰기 권한과 연결되지 않은 worktree 문제가 생긴다.
- 최소 범위에서는 instance와 locator를 그대로 두고, authority 내부 store generation만 올린다(M3의 pointer).

d. 옛 backup과 repair로 다시 채워지는 문제
- 살아 있는 instance가 있으면, restore·repair가 그 instance의 overlay를 이어받는다. 이어받지 않으려면 명시 확인을 받는다.
- 살아 있는 instance가 없으면 다시 채워지는 것을 감지할 수 없다. 이 한계를 고지한다.

e. 공유 chunk
- 제거하지 않는 본문과 공유되는 chunk가 있으면 그 bytes는 남는 본문에도 있다. 최소 범위에서는 자동 확장하지 않는다. "공유 대상이 있어 제거가 완료되지 않음"으로 refuse하고, 대상 추가는 사용자의 명시 선택으로만 한다.

### 첫 공개 최소 계약·운영 범위 (택할 때)

- 대상은 본문 단위다. 본문 일부를 가리는 redaction, 결정·tree·digest 제거, 되돌리기 명령은 없다.
- 실행은 offline이다. 살아 있는 Colvia process lease가 있거나 확인할 수 없으면 refuse한다(RF-18 lease 재사용).
- 단계: 미리보기(내용 출력 없음) → 확인 → export와 overlay 주입 → 새 generation store 검증 → fence → pointer 교체 → 옛 파일 retire(대기 가능).
- 제거된 본문에 의존하는 적용, 재실행, 새 수락, umbrella 구성, Git 통합은 refuse한다. 과거 수락 사실과 조회는 유지한다.
- 고지 항목: export, OS snapshot, 원본 파일, Git 이력, 파일 시스템 잔존물, digest 노출.
- 삭제 실행은 이 검토에서 승인하지 않는다.

### 증가 비용 범주 (측정 아님)

| 범주 | 성격 | 다른 단계와의 관계 |
| --- | --- | --- |
| overlay kind, reader/writer requirement, 감사 의미 | 형식 | P1 형식 작업에 일부 겹침 |
| 영향 미리보기(본문, tree, 결정, 공유 chunk) | 읽기 traversal | export·감사 traversal 재사용 |
| 재구성 filter | 새 코드 | C4 export/restore 재사용, 증가분은 작음 |
| 활성화·fence·retire | M3 | C4에 원래 필요. 제거 전용으로 다시 세지 않음 |
| 소비자별 "의도적 부재" 거부 | 여러 단계 | P3–P6, P8 각각에 작은 증가. 놓치기 쉬운 범주 |
| 재유입 guard와 고지 문서 | 문서·소량 코드 | P9 문서와 겹침 |
| fault 시험(경계마다 kill) | 시험 | P1 harness 재사용 |
| Windows 옛 파일 retire 확인 | 실제 검증 | qualification 예산. 구현 시간이 아님 |

R3a의 8–13시간은 위 표의 "소비자별 거부"와 "활성화"를 어떻게 셌는지 나뉘어 있지 않다. 활성화를 M3으로 옮기면 제거 전용 증가분은 줄어든다. 소비자별 거부를 넣으면 늘어난다. 측정 전 숫자를 새로 제시하지 않는다.

## 4. 요청 항목별 결론

| 질문 | 결론 |
| --- | --- |
| Q1 opaque entry | 방향은 안전하다. M1 a–d 보정이 필요하다. dirty submodule refuse는 안전하지만, submodule이 자주 dirty한 저장소에서 Work를 쓸 수 없게 된다는 사용성 한계는 고지가 필요하다 |
| Q1 edge envelope | 모르는 kind, 모르는 role, 불변 digest, 손실 없는 export 방향은 맞다. 역할 고정, 순서 의미, import 깊이, 숨은 참조 강제(M2)가 필요하다 |
| Q2 제거 | Owner 선택. 권장은 보존 유지와 고지다. M3은 제거 여부와 무관하게 필수다 |
| Q3 진단 | sandbox를 가정하지 않고, 실제 설치 검증을 대신한다고 주장하지 않는다. M4 a–e 보완이 필요하다. 첫 승인 등록과 entry 누락 처리는 충분하다 |
| Q4 Git lock | M5 a–e가 필요하다. 특히 ref lock과 Windows 교체 실패 |
| Q4 RF-27 | M6 a–e. 식별자 guard와 실행 전 문맥 검사가 빠져 있다 |

D7, managed runtime, 첫 설치 신뢰 정책은 다시 다루지 않았다. 이번 입력에서 새 구체 모순을 찾지 못했다.

## 5. 비용 — 빠진 범주와 중복 위험

기준: Driver 75–120h, R3a 90–145h. 둘 다 제거와 실제 qualification을 제외한다. 아래는 판단이며 측정이 아니다. 단계 합계에 기계적으로 더하지 않는다.

- 빠졌을 가능성이 있는 범주:
  1. store generation·fence(M3): P7 견적이 rename 방식을 가정했다면 빠져 있다. P1 배치 결정과 P1/P7 fault 시험이다.
  2. submodule 관측 정책과 Windows placeholder(M1 b·c): P2 관측에 새로 들어가는 platform 분기다. R3a의 S1 2–4h는 형식과 기본 시험만 가정한 것으로 보인다.
  3. Git 하위 process lock과 Windows 교체 실패(M5 b·d): P8의 6–9h 안에 들어 있다고 보기 어렵다.
  4. 진단 원복과 설정 diff 확인(M4 b): qualification 예산에서 앞당겨 쓰는 셀이라면 그 예산에서 센다. 구현 시간에 다시 넣지 않는다.
  5. 고지 문서(opaque 한계, 보존, digest): P9 문서에 포함한다.
- 중복 위험:
  - R3a가 지적별 시간(S1 2–4h 등)을 단계 범위 위에 더했다면, P1/P8 범위에 이미 있던 일과 겹칠 수 있다.
  - 제거의 활성화 비용을 M3과 따로 세면 같은 일을 두 번 세게 된다.
  - plan의 "실제 qualification 포함 87–140"은 Driver 75–120에 12–20을 더한 것이다. 이것을 R3a 90–145와 비교하면 기준이 다르다.
- 상한: Driver 견적의 중간값(97.5h)과 R3a 견적의 하한(90h)이 이미 100시간 근처다. 위 빠진 범주까지 생각하면, 100시간 중단 상한은 P8·P9 전에 도달할 가능성이 높다. 이것은 완료 보장이 아니다. 또 상한을 넘겨도 된다는 권한도 아니다. P1/P2와 P3 재산정 때 Owner가 다시 판단할 지점으로 미리 표시해 둔다.

## 6. 보정 목록 (단계 순)

1. M3 store generation·fence·paged read 재확인 — P1 store 배치 고정 전
2. M2 a–d 역할 고정, 순서 의미, import 깊이, 숨은 참조 — P1 형식 고정 전
3. M1 a·d opaque 추가·종류 변경·조상 규칙과 대체 목록 — P1 형식 고정 전. M1 b·c는 P2
4. M4 a–e 진단 전이 표, 원복, sibling, 대상 축소의 Owner 결정, 범위 표시 — 진단 실행 제시 전
5. M6 a–e RF-27 문구 — P5 전
6. M5 a–e Git lock — P8 전
7. Owner: 본문 제거(권장: 보존과 고지), 진단 실행 범위·예산, 100시간 상한 도달 시 처리

이 검토는 정적 검토다. Owner 수락, 구현 승인, 플랫폼·host 지원 보증이 아니다. 표시한 `[외부 기억]` 동작은 해당 단계의 시험이나 qualification에서 확인해야 한다.
