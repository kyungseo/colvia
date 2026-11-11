> Source-owned verbatim review. See [Driver disposition](review-r2-disposition.md). This review does not activate the proposed format or authorize host settings changes.

# R2 집중 구조 검토 응답 — 새 기록 기반과 공개 실행환경

작성 2026-11-06 · Reviewer: Claude Opus 5.5 (`claude-opus-5-5`) · Owner 수동 요청분

이 문서는 Reviewer 의견이다. Driver 처분, Owner 결정, 구현 승인, 결과 수락을 대신하지 않는다.

## 0. 검토 조건과 한계

- 입력 기준: Colvia `37ec0752fd7b` + 구현 worktree(branch `codex/record-foundation-20261106`)의 미커밋 문서. 검토한 파일과 sha256 앞 12자리는 아래와 같다.

  | 파일 | sha256(앞 12자리) |
  | --- | --- |
  | `docs/development/FEAT-20261106-002-record-foundation.md` | `8c3ff6da084e` |
  | `docs/development/document-ownership.md` | `e2c2dfa4704b` |
  | `record-foundation/design.md` | `23456e1b4513` |
  | `record-foundation/structure.md` | `81a97c13b8f7` |
  | `record-foundation/concurrency.md` | `315a35ce19c3` |
  | `record-foundation/runtime-and-extension.md` | `0ec401056b35` |
  | `record-foundation/validation.md` | `313edb83b72d` |
  | `record-foundation/measurements.md` | `df7bcdc33806` |
  | `record-foundation/diagnostics.md` | `e3d8ad68e4bc` |
  | `record-foundation/review-r1.md` | `814d16aa1655` |
  | `record-foundation/review-disposition.md` | `cb209b21d007` |
  | `AGENTS.md`·`CLAUDE.md`·`docs/development/README.md`의 미커밋 diff | `71ddfefe2194` |

- 추가로 읽은 것: 기존 bootstrap 동작을 확인하려고 `distribution/macos.py`, `distribution/windows/bootstrap.go`, `src/hv2ref/` 파일 목록을 grep으로 읽었다. 비공개 작업 근거 디렉터리의 구현 준비 메모와 회귀 후보 inventory JSON은 F8 산출물 존재 여부를 확인하려고 구조만 읽었다.
- 실행한 것: 파일 읽기, `grep`, `shasum`, `ls`, inventory JSON 구조를 읽는 Python 한 번. 제품 파일 수정·시험·설치·네트워크 접근·추가 모델 호출은 하지 않았다.
- 독립성: 이 세션은 R0·R1 대화의 맥락을 갖고 있지 않다. 다만 R1과 같은 모델 계열이라 모델 독립성은 제한된다. 링크된 Codex sandbox 공식 문서와 SQLite 문서를 직접 열어 보지 않았다.
- 근거 표시:
  - [정적] 이번 입력 문서와 source를 읽고 추론한 것
  - [외부 지식] SQLite·Git·OS·호스트의 문서화된 동작에 대한 지식. 이번에 실행으로 확인하지 않았다
  - [Driver 기록] 저장소 문서에 기록된 Driver 측정·진단. 나는 재현하지 않았다

## 1. 판정

결론: 방향은 유지하되, 구현 착수 전 필수 보정 10건이 필요하다.

공용 authority, workspace별 결과, 전후 본문 보존, SQLite 위임, Git 통합 분리라는 큰 방향은 맞다. R1 처분도 대부분 타당하다. 그러나 다음 세 가지는 아직 "미결"이 아니라 현재 문장대로 구현하면 틀리는 상태다.

1. 모든 workspace가 공유하면서 모든 세션의 기본 쓰기 범위 안에 있는 물리 위치는 구조적으로 존재하지 않는다. 위치를 "고르는" 문제가 아니라 권한 부여 방식을 설계하는 문제다(M1).
2. 큰 본문 import를 한 transaction에 넣으면 rollback-journal 모드에서 reader가 막힌다. "짧은 읽기 transaction" 계약과 충돌한다(M3).
3. Git 통합 쪽의 "hook 없는 plumbing", "ref 다음 index" 전제는 실제 Git 동작이나 sandbox 권한과 맞지 않는다(M6).

단계별로 막는 항목은 아래와 같다.

```text
1단계 schema/store/trie ─ M3(본문 staging), M4(경로·트리 정규형)
2단계 locator/관측 ────── M1(위치·권한·identity), M5(ignore), M7(실행기·Git 발견), M10(D1–D7 정의)
3단계 lifecycle/export ── M2(백업·복원 약속), M9-b(거부 지점 목록)
착수 일정 확정 전 ──────── M9-a(기능별 산정·중단 상한)
5단계 Git/배포 ─────────── M6(통합 protocol), M8(설치 신뢰 기준)
                           단, M6 후보 schema와 M8 key 고정은 첫 공개 형식 고정 전에 결정
```

Owner 결정이 필요한 것은 M1(위치와 호스트 설정 변경 허용), M2(데이터·백업 약속), M8(설치·갱신 신뢰 기준)이다. 나머지는 Driver가 명세 문장과 시험 목록을 보정하면 된다.

## 2. 필수 수정

### M1. [축1] 공유 authority 위치는 "권한 부여 설계"로 다시 정의해야 한다

- 현재 상태: design.md는 물리 위치를 미결로 두고 "sandbox access, workspace binding, backup, clean/delete를 먼저 해결"하라고 한다. runtime 계약 6항은 경로만 옮기거나 매번 권한 상승하는 해법을 금지한다. 방향은 맞지만, 해법이 존재하는지에 대한 판단이 없다.
- 반례 [정적 + 외부 지식]:
  - Claude Code 앱 worktree는 primary checkout 안의 `.claude/worktrees/<name>`에 생긴다(D7 기록). 그 세션의 쓰기 범위는 해당 worktree다. primary 최상위의 `.colvia/`나 common-dir은 범위 밖이다.
  - Codex 앱 worktree는 프로젝트 밖 별도 위치에 생기는 것으로 알고 있다 [외부 지식]. 그러면 primary 안의 어떤 위치도 범위 밖이다.
  - common-dir 아래는 Codex 기본 workspace-write에서 읽기 전용이다(처분 F1).
  - primary working tree 안의 `.colvia/`는 primary 세션에서는 쓸 수 있다. 그러나 `git clean -fdx` 한 번에 유일한 정본이 지워진다.
  - 따라서 "공유"와 "모든 세션의 기본 쓰기 범위 안"을 동시에 만족하는 위치는 없다. 어느 안이든 최소 한 종류의 세션에는 명시적인 쓰기 허용이 필요하다.
- 추가 반례 [정적]: `cp -R repo repo-copy`로 폴더를 복사하면 `.git` 안의 연결 정보도 복사된다. 정본이 workspace 밖에 있으면 두 저장소가 같은 정본에 쓴다. 정본이 폴더 안에 있던 시험 형식보다 더 나쁜 결과다. R1 F12는 "사본 감지"만 적었고, 정본 공유 상황은 다루지 않았다.
- 최소 보정안(Owner에게 제시할 권장안 하나):
  1. 정본은 사용자 데이터 위치의 프로젝트별 디렉터리에 둔다. 예: macOS `~/Library/Application Support/Colvia/authorities/<project-uuid>/`, Windows `%LOCALAPPDATA%\Colvia\authorities\<project-uuid>\`.
  2. Git 프로젝트의 연결 정보(project UUID, 연결 nonce)는 common-dir 안 작은 파일이나 local git config에 둔다. 세션에서는 읽기만 하면 된다. 이 파일은 sandbox 밖에서 실행되는 설치·연결 단계가 쓴다. 비 Git 폴더는 폴더 안 marker를 쓰고, 그 marker를 구조 경계로 관측에서 제외한다.
  3. 호스트별로 `authorities/` 한 곳을 추가 쓰기 범위로 한 번 등록한다. 설치 도구가 목적·범위·회수 방법을 보여 주고 동의를 받는다. 해제(detach) 때 회수한다. 디스크 전체나 home 전체 권한은 쓰지 않는다.
  4. 정본은 연결 당시 common-dir의 realpath, volume 식별자, nonce를 기록한다. 열 때마다 대조한다. 불일치하면 쓰기를 거부하고 "새 프로젝트로 연결" 또는 "이동 확인"(원래 경로가 사라졌고 nonce가 같은지 확인)을 안내한다.
  5. 2단계 진입 조건: 위 설정이 Codex CLI·앱, Claude Code CLI·데스크톱의 기본 모드에서 실제로 적용되는지 확인하는 probe. 이 설정을 어디서 지원하는지는 [외부 지식·미검증]이다. 지원하지 않는 호스트·모드가 있으면 그 조합을 12개 원장에 "제약 있음"으로 올리고 Owner 결정으로 넘긴다.
- 이 안의 비용: 프로젝트를 지워도 정본은 남는다(R6 참조). 저장소 백업에는 포함되지 않는다(M2). 호스트 설정을 바꾸는 단계가 한 번 생긴다.

### M2. [축1] 백업·복원 약속을 "논리 export"로 구체화하고 Owner 수락을 기록해야 한다

- 현재 상태: F2 처분은 "versioned export/import와 실제 복원 시험 필수", "데이터 약속은 Owner에게 제시"이다. 아직 Owner 결정 기록이 없고, export 방법도 "consistent SQLite snapshot + verified manifest"까지만 정해져 있다.
- 반례 [외부 지식]:
  - SQLite online backup API는 다른 연결이 원본을 바꾸면 처음부터 다시 시작한다. 쓰기가 잦으면 큰 DB의 백업이 끝나지 않을 수 있다.
  - `VACUUM INTO`는 실행 내내 읽기 transaction을 잡는다. rollback-journal 모드에서는 그동안 다른 writer가 commit하지 못한다.
  - Windows 기본 파일 기록 백업은 사용자 라이브러리 중심이다. `%LOCALAPPDATA%`는 기본 대상이 아닌 것으로 알고 있다 [미검증]. M1 위치를 쓰면 Windows 사용자는 기본 백업만으로는 기록을 보호받지 못한다.
- 최소 보정안:
  1. 사용자에게 보여 줄 백업 수단은 논리 export로 정한다. 짧은 읽기 transaction으로 모든 head를 고정한다. 그다음 불변 객체를 짧은 transaction으로 나눠 stream한다. 객체가 불변이고 게시된 객체의 GC가 없으므로 결과는 고정한 시점과 일치한다. 설계의 조회 방식과 같은 원리다.
  2. export 파일에는 format version, project UUID, head 목록, 객체(kind/digest/length), 마지막 manifest digest를 둔다. import는 빈 authority에만 허용하고 병합하지 않는다.
  3. 갱신 전 로컬 복구 사본은 별도로 둔다. 설치 도구가 maintenance 상태(다른 writer 거부)에서 `VACUUM INTO`로 만들고, 사본에서 `integrity_check`와 객체 hash 검증을 한다. 마지막 복구 사본은 다음 갱신이 성공적으로 검증된 뒤에만 지운다.
  4. 사용자 문구 예: "작업 기록은 Git과 clone에 포함되지 않고 이 컴퓨터에만 저장됩니다. 다른 기기나 백업으로 보관하려면 내보내기를 사용하세요." 플랫폼별 기본 백업 포함 여부는 확인한 경우에만 적는다.
  5. 시험: export → 정본 삭제 → import 후 head·본문·수락 이력이 같은지. 쓰기와 동시에 export해도 결과가 고정 시점과 같은지. 한 version 전 export를 import할 수 있는지.

### M3. [축1·2] 큰 본문 import가 reader를 막는다

- 위치: design.md "Store bodies as content-addressed immutable blobs … A body import and the metadata referencing it commit together." 그리고 한도 "body 256MiB per file, 1GiB per Work".
- 반례 [외부 지식]: rollback-journal 모드에서 writer의 변경 page가 page cache를 넘으면 DB 파일에 spill해야 한다. 이때 EXCLUSIVE lock이 필요하다. EXCLUSIVE 이후에는 새 reader가 SHARED lock을 얻지 못하고 busy가 된다. 1GiB import는 기본 cache(수 MB)를 바로 넘는다. 따라서 import 내내 다른 세션의 조회·알림 진입·View가 busy로 실패한다. R1 F4는 "lock이 한도로 묶인다"며 이 구조를 수용했는데, writer끼리만 본 판단이다. reader 차단은 다루지 않았다.
- 최소 보정안(둘 중 하나를 명세에 고정):
  1. 권장: 본문을 고정 크기 chunk(예: 4MiB)로 나눈다. chunk마다 짧은 write transaction에서 "staged" 상태로 commit한다. 본문 객체는 chunk 참조 목록이다. 마지막 게시 transaction은 작은 metadata와 head 갱신만 한다. staged 행은 import session ID를 갖는다. 게시되지 않은 staged 행은 같은 session의 재시도나 명시적 repair만 회수한다. 이것은 게시된 객체의 GC가 아니므로 "no automatic GC" 원칙과 충돌하지 않는다. 계약 문장도 "본문과 참조가 함께 commit"에서 "참조 게시는 원자적, 게시 전 staged bytes는 존재 가능"으로 바꾼다.
  2. 대안: 한 transaction 유지 시 per-file·per-Work 한도를 실측 기반으로 크게 낮추고, writer 지속 시간 상한을 reader busy timeout보다 짧게 둔다.
- 시험: 한도 크기 import 중 다른 연결의 head 조회가 busy 없이 끝나는지(1안). import 도중 kill 후 staged 행이 게시 참조에 나타나지 않는지. repair가 게시 객체를 건드리지 않는지.
- 참고 [외부 지식]: 표준 `sqlite3`에서 BLOB을 나눠 쓰려면 `Connection.blobopen`(Python 3.11+)이 필요하다. 관리 runtime은 3.14라 문제없지만 최소 Python 조건으로 적어 둔다.

### M4. [축2] 경로 정규형이 tree hash 형식에 들어가는데 정의되지 않았다

- 위치: design.md trie 문단 "SHA-256(canonical relative path)". canonical의 정의가 없다.
- 반례 [외부 지식]: macOS의 Git은 기본적으로 `core.precomposeunicode=true`라 index 경로를 NFC로 다룬다. 파일시스템 열거(`os.listdir`)는 저장된 형태 그대로 돌려주므로 NFD일 수 있다. 같은 파일 `한글.md`가 Git 관측에서는 NFC bytes, 비 Git 관측이나 직접 열거에서는 NFD bytes가 된다. 경로 hash가 달라 다른 leaf에 들어가고, 거짓 추가·삭제나 중복 경로가 생긴다. 대소문자를 구분하지 않는 APFS·NTFS에서 `A.md`와 `a.md`도 같은 문제다.
- 반례 [정적]: Windows 예약 이름(`CON`, `NUL.txt`), 끝의 점·공백, `\` 구분자, 실행 bit가 없는 플랫폼의 mode가 정의되지 않았다. 같은 Work를 Codex에서 시작하고 Claude에서 이어 가도 같은 기계라면 문제없다. 하지만 관측 adapter가 Git과 비 Git 두 개라 두 adapter가 같은 entry bytes를 내야 한다.
- 최소 보정안:
  1. canonical path: UTF-8, `/` 구분, NFC 정규화. `.`·`..`·빈 segment·NUL·앞뒤 `/`는 거부한다. UTF-8이 아닌 이름은 거부한다.
  2. 정규화 결과가 같거나 대소문자 비구분 volume에서 casefold 결과가 같은 entry가 둘이면 alias로 거부한다. 실제 쓰기에 쓸 on-disk 표기는 entry에 별도 field로 둔다.
  3. Windows에서 만들 수 없는 이름은 관측 시 거부하거나 명시적으로 "지원 밖"으로 표시한다.
  4. mode는 `regular`·`executable`·`symlink` 세 값으로 하고, 플랫폼별 판정 출처를 적는다(예: Windows Git 프로젝트는 index mode, 비 Git은 항상 regular).
  5. 트리: 처분의 교정 규칙은 아래처럼 함수로 쓰면 정규형이 된다. `node(S, d) = Leaf(sorted(S))` (|S|와 직렬화 크기가 한도 이내일 때), 아니면 `Branch({b: node(S_b, d+1) | S_b ≠ ∅})`. 여기서 b는 경로 hash의 d번째 byte다. "분할·삭제 후 합치기"를 절차로 적지 말고 이 함수를 정의로 둔다. 증분 구현은 이 함수와 같아야 한다는 속성 시험의 대상일 뿐이다. 빈 집합 root와 leaf 정렬 키(canonical path bytes)도 고정한다.
  6. 시험 seam: SHA-256으로는 1,000만 파일에서도 depth 2를 넘지 않는다. depth 8, 분할, 삭제 후 합치기 경로는 실제 입력으로 거의 실행되지 않는다. pure 함수에 hash 함수를 주입할 수 있게 하고, 1–2 bit hash로 depth 상한·초과 거부·합치기를 속성 시험한다.

### M5. [축2] ignore 변경 판정 규칙을 실제 계산 가능한 형태로 정해야 한다

- 현재 상태: 처분 F5는 R1 알고리즘의 결함(기준에 없던 `secret.txt`를 새 규칙으로 숨김)을 찾았다. 그러나 "실제 효과 비교 또는 보수적 증명"까지만 정했다. 계산 방법이 없다.
- 추가 반례 [정적 + 외부 지식]:
  1. 부정 규칙 제거: 기준 `.gitignore`에 `*.env`와 `!keep.env`가 있었는데 `!keep.env`를 지운다. 추가된 줄이 없으므로 "추가 줄만 검사"하는 규칙도 놓친다.
  2. 실행 환경 차이: global excludes 위치는 `core.excludesFile`이나 `$XDG_CONFIG_HOME/git/ignore`에서 정해진다. GUI 앱과 login shell의 환경 변수가 다르면, 같은 workspace에서 CLI로 시작하고 앱에서 제출할 때 정책이 달라진다. 숨김과 거짓 거부가 둘 다 가능하다.
  3. 범위 안 `.gitignore` 편집: Work가 승인 범위 안에서 `.gitignore`를 고치면 그 Work 자신이 정책을 바꾼다. 같은 제출에서 새로 숨겨진 파일은 현재 정책으로는 보이지 않는다.
  4. 기준 정책 재평가 불가: per-directory `.gitignore`는 승인 파일이 아니면 본문이 보존되지 않는다(design.md). 그래서 나중에 기준 정책을 다시 평가할 수 없다.
- 최소 보정안(거짓 수락 없음, 거짓 거부 허용):
  1. 기준 관측 때 모든 정책 원천을 raw bytes로 보존한다: workspace 안 모든 ignore 파일, `info/exclude`, 실제로 해석된 global excludes 파일, 그 경로를 결정한 config origin(`git config --show-origin`). 작고 drift 판정에 꼭 필요하므로 본문 비보존 원칙의 예외로 명시한다.
  2. 제출 때 원천별로 비교한다. 기준 줄이 순서대로 그대로 남고 추가 줄이 모두 부정(`!`)이 아니면 "순수 추가"다. 원천 삭제, 줄 삭제·변경, 부정 줄 추가, 해석 경로 변경이 있으면 정책 축소·변경으로 보고 제출을 멈춘다.
  3. 순수 추가일 때는 무시된 미추적 경로를 열거한다(`git ls-files -o -i --exclude-standard --directory`). 각 경로의 결정 규칙을 `git check-ignore -v`로 구하고, 원천 식별 + pattern 문자열로 비교한다(줄 번호는 밀리므로 쓰지 않는다). 결정 규칙이 추가 줄인 경로는 둘 중 하나여야 한다. 검증된 구조 경계(등록 worktree root, 그 부모 안에 등록 root만 있는 경우) 안에 있거나, 기준 tree에 있고 bytes가 같아야 한다. 디렉터리로 보고되면 한도 안에서 재귀 열거한다. 어느 쪽도 아니면 거부하고 해당 경로 목록을 보여 준다.
  4. 거부 후 진행하려면 사용자가 목록을 보고 새 기준을 명시적으로 승인한다. 이 승인은 "숨겨진 변경이 없다"는 사람 확인이며 자동 동등 판정이 아니다.
  5. D7 결과: `info/exclude`에 `.claude/worktrees/` 추가는 순수 추가다. 그 아래가 등록 worktree root뿐이면 통과한다. 등록 해제된 남은 폴더가 있으면 D1 orphan 규칙대로 거부한다. `secret.txt` 추가와 `*.log` 추가는 거부한다. `!keep.env` 삭제도 거부한다.
  6. 비 Git workspace의 정책 원천(내장 제외 목록만인지, Colvia 고유 파일이 있는지)을 명시한다. 현재 문서에 없다.

### M6. [축2] Git 통합: sandbox 권한, hook, 다른 worktree, 교차 workspace 적용이 빠졌다

- 처분 F6의 "ref와 index는 원자적이지 않다"는 맞다. 그 위에 아래 네 가지가 빠졌다.
- 반례 [정적 + 외부 지식]:
  1. sandbox: blob·commit 객체 쓰기와 `update-ref`는 모두 `.git` 쓰기다. M1·F1에 따라 Codex 기본 모드에서는 Git 통합 자체가 실행되지 않는다. "Git whole-candidate support"를 앱 기본 흐름의 기능처럼 읽으면 안 된다.
  2. hook: Git 2.28 이후 `update-ref`는 `reference-transaction` hook을 실행한다. index를 쓰는 명령은 `post-index-change` hook을 실행할 수 있다. 따라서 R1 F6③ "hook이 없는 plumbing만 쓴다"는 사실과 다르다. 반대로 plumbing으로 commit하면 프로젝트의 `pre-commit`·`commit-msg`를 조용히 건너뛴다. design.md가 금지한 "몰래 우회"에 해당한다.
  3. 다른 worktree에 checkout된 branch: workspace A가 `refs/heads/main`을 갱신하는데 primary가 `main`을 checkout하고 있다. 그러면 primary의 HEAD만 움직이고 index·working tree는 옛 상태다. `git status`가 수락한 변경의 역방향을 보여 준다. 통합 대상 index를 A 것만 맞추는 R1 안으로는 막지 못한다.
  4. 교차 workspace: worker 결과(workspace W)를 primary(T)에 넣을 때 T의 working tree에는 그 bytes가 없다. ref와 index만 바꾸면 T의 working tree가 index보다 뒤처진다. 이어서 `git commit -a`를 하면 수락 결과가 되돌아간다.
- 최소 보정안:
  1. 통합 종류를 둘로 나눈다. (a) Git commit 통합: bytes를 가진 그 workspace의 HEAD branch에만 commit한다. (b) 내용 적용: W의 결과를 T의 working tree에 쓴다. T의 현재 bytes가 기준과 같은지 CAS로 확인한 뒤 쓰며, Git과 무관하다(기존 worker 적용 의미). 두 동작을 한 명령에 묶지 않는다.
  2. Git commit 통합은 `.git` 쓰기 권한이 필요한 명시적 동작이다. 기본 sandbox에서는 권한 상승을 한 번 요청하거나, 사용자가 실행할 명령을 안내한다. Work 수락 흐름에는 권한 상승을 넣지 않는다.
  3. 상태 기록 순서: DB에 의도 기록(예상 old ref, new commit, 예상 index digest, 바꿀 경로) commit → `update-ref <ref> <new> <old>` → DB `REF_UPDATED` → index CAS → DB `DONE`.
  4. index CAS: 현재 index를 private 사본에 복사하고 `GIT_INDEX_FILE`로 대상 경로만 갱신한다. 그다음 `index.lock`을 직접 배타 생성한다. 실제 index digest가 예상과 같을 때만 사본 bytes를 lock에 쓰고 rename한다. 다르면 index를 건드리지 않고, 사용자가 맞출 경로를 안내한다.
  5. 복구: ref가 old면 미적용. new면 `REF_UPDATED`. 둘 다 아니면 `merge-base --is-ancestor new <ref>`로 우리 commit이 이력에 있는지 본다. 있으면 "통합 후 사용자가 이어서 commit함"으로 기록하고 index는 자동으로 고치지 않는다. 없으면 "외부에서 ref 변경"으로 남긴다. 추측해서 성공으로 표시하지 않는다.
  6. 사전 거부 조건: 대상 branch가 다른 worktree에 checkout됨(`git worktree list --porcelain`), detached가 아닌데 HEAD가 branch를 가리키지 않음, 적용 대상이 되는 hook(`pre-commit`, `prepare-commit-msg`, `commit-msg`, `post-commit`, `reference-transaction`, `post-index-change`)이 활성 상태, filter·eol 변환 경로, LFS·submodule, conflict index. hook이 없을 때도 실행 중 hook 추가 경쟁을 막도록 `-c core.hooksPath=<빈 디렉터리>`로 실행한다.
  7. 형식 고정 전에 확정할 것: 통합 의도 record schema와 상태 값. 구현은 5단계에 해도 된다.

### M7. [축3] 실행기와 Git 도구를 workspace에서 찾는 방식이 미정이다

- 위치: runtime 계약 4항 "일반 폴더, linked worktree, 앱 생성 worktree 모두 정확한 authority와 전용 실행기를 찾아야 한다." 요구만 있고 방법이 없다. 현재 진입 문서는 `./colvia view --details`로 프로젝트 최상위 파일을 가정한다.
- 반례 [정적]:
  - `./colvia`가 무시 대상 파일이면 Codex 외부 worktree와 Claude nested worktree에는 존재하지 않는다.
  - 추적 파일이면 각 branch의 commit 시점 사본이 checkout된다. 그러면 오래된 binding을 가리킬 수 있다.
  - 실행기의 절대 경로를 project entry(AGENTS.md 등 추적 파일)에 적으면 개인 경로가 저장소에 들어가고 다른 기계에서 틀린다.
- 반례 [외부 지식]: Git은 binding에 포함되지 않는다. macOS에서 Command Line Tools가 없으면 `/usr/bin/git` 호출 때 설치 대화상자가 뜨고 명령은 실패한다. 앱과 CLI가 서로 다른 git(Xcode, Homebrew, 앱 내장)을 쓰면 version과 ignore 해석이 달라질 수 있다(M5-2와 연결).
- 최소 보정안:
  1. 실행기는 사용자별 고정 위치 하나에 둔다(예: macOS `~/.colvia/bin/colvia`, Windows `%LOCALAPPDATA%\Colvia\bin\colvia.exe`). project entry에는 플랫폼별로 이 사용자 상대 경로만 적는다. 실행기는 cwd에서 `git rev-parse --git-common-dir`(읽기 전용)나 비 Git marker로 프로젝트 binding을 찾는다. worktree에 복사된 파일에 의존하지 않는다.
  2. Git 실행 파일은 관측 context가 한 번 해석한다. 경로·version·config origin을 기록하고, 최소 version 미만이면 거부한다. macOS에서는 CLT 설치 여부를 먼저 확인해 대화상자 유발을 피한다.
  3. 12개 원장에 "선택된 git 경로·version" 열을 추가한다.

### M8. [축3] 한 명령 설치의 신뢰 기준과 갱신 신뢰를 첫 공개 전에 고정해야 한다

- 현재 상태: runtime 계약은 "공급·서명 방식 미결, 실제 경로 검증 전에 해결"로 둔다. 미결로 표시한 것은 맞다. 그러나 이 결정은 첫 공개 후 바꾸기 가장 어려운 항목이므로 단계 순서상 늦다.
- 근거 [정적]: 기존 macOS bootstrap은 표시된 배포 확인값을 사용자가 `--apply --confirm <digest>`로 다시 입력하는 2단계다(`distribution/macos.py`). Windows bootstrap은 내장 catalog와 Python ZIP hash를 고정한다. 한 명령 요구는 첫째 방식의 사람 확인을 없앤다. 그러면 신뢰 기준이 사실상 "명령이 가리키는 HTTPS 출처"로 바뀐다.
- 반례 [정적]:
  1. 같은 출처의 manifest와 자산 hash는 출처가 침해되면 함께 바뀐다(계약도 인정한다).
  2. "현재 설치와 호환되는 최신 공개 버전 확인"은 변경 가능한 channel index를 뜻한다. 서명된 index가 없으면 오래된 취약 버전을 최신으로 내미는 공격을 막을 수 없다.
  3. 갱신 서명 key를 첫 공개 설치본에 넣지 않으면, 이후 key를 넣어도 이미 설치된 사용자는 첫 갱신을 같은 약한 경로로 받는다.
- 최소 보정안(Owner 결정용 하나):
  1. 첫 설치의 신뢰는 "공식 HTTPS 출처와 bootstrap에 고정된 manifest digest"로 명시하고, 그 이상을 주장하지 않는다.
  2. 첫 공개 설치본부터 갱신 manifest 서명 검증 공개 key를 고정한다. channel index에도 서명과 단조 증가 번호를 붙인다. 설치된 version보다 낮은 version은 명시적 옵션 없이는 거부한다.
  3. 플랫폼 코드 서명(Windows bootstrap 실행 파일, macOS 알림 수신 앱)의 필요 여부와 상태를 12개 원장에 열로 둔다. OS 실행 허용 안내와 연결된다.

### M9. [축4] F7 기능별 산정과 F8 거부 지점 목록이 아직 없다

- 현재 상태: 처분은 F7·F8을 모두 채택했다. 그러나 저장소에도 비공개 근거에도 산출물이 없다.
  - 비공개 inventory JSON은 기존 시험 17개 파일의 시험 이름 목록, 즉 의미 oracle 후보다. source의 거부 지점(오류·조건) 목록이 아니다.
  - 기존 32–52시간은 무효로 표시됐고 대체 산정이 없다.
  - Owner는 기능 연기를 채택하지 않았다. 그래서 R1이 지적한 "상한이 4단계 중간에 닿는" 위험이 그대로 남는다.
- 반례 [정적]: 이식 대상 규모가 크다. 공식 실행 13개 module 약 4.4천 줄, `product.py` 2.5천 줄(연결·갱신·복구·해제), `continuation.py` 1.4천 줄, `view.py` 1.5천 줄, 그리고 macOS·Windows 배포·알림 수신 코드다. 회귀 지도에는 View 출력(간결·상세 화면)의 유지 의미 행이 없다. 또 oracle 기준이 되는 미커밋 보강 중 FEAT-20261106-001은 아직 Active·수락 전이라 이식 기준이 바뀔 수 있다.
- 최소 보정안:
  - (a) 구현 일정 확정 전: 기능별 예상 시간과 누적 중단 상한을 분리해 표로 둔다(store, context/lifecycle, worker/umbrella, 공식 실행, delivery/알림, 플랫폼·runtime·배포, Git, 검증). 상한 도달 시 규칙도 적는다: "새 형식은 출하하지 않고 현재 후보가 유지되며, 남은 기능과 비용을 보고한다."
  - (b) 3단계 전: source 거부 지점 정적 목록을 만든다(module, 조건, 오류 code·문구, 유지/통합/폐기, 이유, 새 시험 ID). View 출력 의미를 회귀 지도에 한 행 추가한다.
  - (c) oracle 기준 revision(보존된 diff digest)을 validation.md에 고정한다. FEAT-001의 이후 변경이 새 구현에 반영되는 경로나 동결 시점을 적는다.

### M10. [축5] 저장소 명세가 비공개 자료의 이름과 경로에 기대는 부분이 있다

- 반례 [정적]:
  1. design.md와 validation.md는 D1·D7을 규범적 시험 사례로 쓴다("D1/D7 synthetic fixtures"). 그런데 D1–D7의 정의가 저장소에 없다. D7은 design.md에 한 문장 요약이 있지만, D1은 일부만 있고 D2–D6은 전혀 없다. 공개 독자와 새 구현자는 시험을 재구성할 수 없다.
  2. measurements.md와 diagnostics.md는 `verification/logs/*`, `verification/diagnostics*.py`를 상대 경로처럼 적는다. 저장소에는 그런 경로가 없다. 비공개 위치를 가리키는 흔적이며, 공개 저장소에서는 깨진 참조다.
  3. structure.md의 S1–S11과 "11-04 감사 6건"은 원 제안·감사 문서가 비공개다. 처분 내용은 표에 있지만 S5·S8 등은 원 항목을 모르면 뜻이 불완전하다.
  4. F1의 핵심 근거는 외부 공식 문서 링크 하나다. 이번에 열어 확인하지 않았으며 URL이 해당 문서의 정식 위치인지 확인이 필요하다. 링크가 바뀌어도 판단이 남도록 근거 문장을 한 줄 요약해 둔다.
- 최소 보정안: D1–D7을 design.md나 validation.md에 각 한 줄로 정의한다(관측 조건 → 기대 결과). `verification/…` 경로 표기는 "유지보수자 비공개 근거(저장소 밖)"로 바꾼다. S·감사 항목은 처분 표에 원 요지를 한 구절씩 넣는다. 외부 문서 근거는 확인 날짜와 요지 한 줄을 남긴다. 측정 수치 자체는 익명 합성 결과라 그대로 두어도 된다.
- 확인 결과: 개인 경로, 계정, 외부 비교 저장소 실명은 이번 입력 문서에서 발견하지 못했다. 단, source 상대 경로 `src/hv2ref/...`와 내부 profile 이름 `continuation-1`은 남아 있다. 공개 시점의 노출 판단은 Owner 몫이다.

## 3. 권장 수정

| ID | 축 | 내용 | 최소 보정 |
| --- | --- | --- | --- |
| R1 | 1 | schema version 하나뿐이면, 새 capability가 table을 추가하는 순간 이전 runtime이 DB 전체를 거부한다. "호환 rollback 허용"이 사실상 불가능해진다 | SQLite 파일 형식처럼 `read_min_version`과 `write_min_version`을 나눈다. 이전 runtime은 읽기 전용으로 열고 모르는 객체 kind는 "이 버전에서 표시 불가"로 남긴다 |
| R2 | 3 | runtime·payload slot 보존과 정리 규칙이 없다. Windows는 실행 중 파일을 지울 수 없다 | 현재와 직전 검증 slot 두 개만 남긴다. 그 이전 slot은 사용 중이 아닐 때 다음 갱신에서 정리한다. 정리 실패는 갱신 실패로 보지 않는다 |
| R3 | 1 | F11 동기화 경고가 iCloud 중심이다 | Windows 11 OneDrive 알려진 폴더 이동(Documents·Desktop)도 포함한다 [외부 지식]. 실시간 백신이 journal 파일을 잡아 삭제 오류가 나는 경우를 Windows qualification 항목에 넣는다 |
| R4 | 3 | 확장 경계의 "모델/provider 연결" 행은 현재 소비자가 없다. Colvia는 모델이 아니라 에이전트 CLI·앱을 부른다 | 문서상 경계로만 두고 port나 interface를 만들지 않는다. EXT-AGENT-LOCAL 착수 때 정의한다. 지금 범위가 과하지 않게 유지하는 조건이다 |
| R5 | 2 | leaf 4MiB byte 한도는 128 entry 한도에 먼저 걸려 사실상 도달할 수 없다(경로 4KiB 가정) | 경로 최대 bytes와 entry 최대 직렬화 크기를 정하고, byte 한도를 "형식 검증용 상한"으로만 남긴다. 실제로 쓰이는 경계 시험은 entry 수 기준으로 한다 |
| R6 | 1 | M1 안에서는 프로젝트를 지워도 정본이 남는다 | 연결된 정본 목록(경로 존재 여부 포함)과 명시적 정본 삭제 명령을 둔다. detach와 삭제는 계속 분리한다 |
| R7 | 3 | managed 실행기가 실행할 때마다 runtime tree를 검증한다(`verify-tree.sh`). 이 비용을 측정한 적이 없다 [Driver 기록] | 새 SQLite 경로의 시간 측정에 실행기 시작 비용을 별도 항목으로 넣는다 |
| R8 | 5 | `CLAUDE.md`가 `@AGENTS.md` import와 "Read and follow AGENTS.md" 문장을 함께 가진다 | 동작에는 문제없다. 설치 payload 안의 CLAUDE.md가 사용자 프로젝트에서 자동으로 읽히는 경로가 실제로 있는지 확인하고, 없으면 새로 추가한 경고 문장은 줄인다 |
| R9 | 2 | non-Git 일반 폴더의 이동·복사도 identity 충돌을 만든다 | M1-4의 realpath·volume·nonce 대조를 non-Git marker에도 적용한다 |

## 4. 기존 R1 검토·처분과의 대조

| R1 항목 | R1 주장 | Driver 처분 | 이번 판단 |
| --- | --- | --- | --- |
| F1 | probe가 통과하면 `.git/colvia` 유지 | 기본 위치 철회, 위치·권한 동시 해결 | 처분이 맞다. 다만 probe로 풀리는 문제가 아니다. 공유 위치와 기본 쓰기 범위를 동시에 만족하는 위치가 없으므로 명시적 권한 부여 설계가 필요하다(M1). R1이 든 common-dir의 장점(`git clean` 안전)은 그 위치를 쓸 수 없어 의미가 없다 |
| F2 | Owner 수락, export 필수 | 채택, 표현 보정 | 동의. Owner 결정이 아직 기록되지 않았다. export 방법과 Windows 백업 범위를 보충한다(M2) |
| F3 | 정규형 없음, 고정 256 bucket으로 교체 | 결함 채택, 교체 보류, 정규 규칙 제시 | 처분의 규칙은 함수로 정의하면 정규형이다. 교체는 필요 없다. R1의 "depth 8은 사실상 불필요"는 맞으므로, 그 경로는 hash 주입 시험으로만 검증할 수 있다(M4-5·6). 처분과 R1 모두 경로 정규형 정의를 놓쳤다(M4-1–4) |
| F4 | fullfsync, hot journal, 짧은 읽기, 최소 version, export version | 채택 | 동의. 단 R1의 "본문 import lock은 한도로 묶인다"는 틀렸다. cache spill이 reader를 막는다(M3) |
| F5 | 기준 admitted 목록에 현재 정책 적용 | 방향 채택, 알고리즘 불충분(새 파일 숨김 반례) | 처분이 맞다. 부정 규칙 제거, 실행 환경 차이, 범위 안 ignore 편집, 기준 정책 재평가 불가도 같은 종류의 구멍이다. 계산 가능한 보수 규칙을 제시했다(M5) |
| F6 | HEAD+보존 본문 후보, update-ref CAS 후 index, hook 없는 plumbing | 채택, 원자성 없음 지적 | 처분이 맞다. R1의 "hook 없는 plumbing"은 사실과 다르다. sandbox `.git` 쓰기, 다른 worktree checkout, 교차 workspace 적용이 빠졌다(M6) |
| F7 | 32–52h에 capability 이식 누락, 일부 기능 공개 뒤로 | 누락 채택, 연기 불채택 | Owner 방침상 연기 불채택은 정당하다. 그 대가로 기능별 산정과 상한 도달 규칙이 착수 전 필수가 된다. 아직 없다(M9-a) |
| F8 | 거부 지점 정적 목록 | 채택 | 아직 만들지 않았다. 비공개 inventory는 시험 이름 목록이라 대체물이 아니다(M9-b) |
| F9 | 새 이름 사용, `.hrn`은 일반 내용으로 | 이름 분리 채택, 일반 내용 취급 불채택 | 처분이 낫다. 옛 기록이 Work 결과에 대량으로 섞일 수 있다. 다만 "연결 시 명시적 경계"가 관측 제외인지 연결 거부인지 아직 정해야 한다 |
| F10 | 범위 확장 시 가짜 before 금지 | 채택 | 동의 |
| F11 | macOS 동기화 경고 | 채택 | 동의. Windows OneDrive로 넓힌다(R3). M1 안을 쓰면 정본은 동기화 폴더 밖이라 위험이 working tree 쪽으로 줄어든다 |
| F12 | workspace 수명 시험 | 채택 | 동의. 정본이 workspace 밖이면 폴더 복사가 정본 공유로 바뀌므로 필수(M1-4)로 올린다 |
| F13·F14 | 내부 성능 목표, 사용자 부담 수락 기준 | 채택 | 동의 |

R1 자체의 한계도 다시 적는다. R1은 이전 시험과 제안을 쓴 같은 세션이었고 packet 밖 source를 보지 않았다. 이번 검토는 맥락은 독립이지만 같은 모델 계열이다.

## 5. 축별 요약 답변

1. 기록 위치·앱 권한·본문 보존·백업·갱신·복구: 저장 계층의 원리(불변 객체, CAS, staged 게시 분리)는 성립한다. 위치·권한(M1), 백업 약속(M2), 대형 본문 lock(M3)을 보정하기 전까지는 앱 기본 권한에서 성립한다고 볼 수 없다. 갱신·복구 계약은 원칙이 충분하다. 단 schema 호환 수준 분리(R1)가 없으면 "호환 rollback"이 실제로는 거의 불가능하다.
2. 트리 정규형·ignore·Git ref/index: 정규형은 함수 정의와 경로 정규형(M4)을 넣으면 성립한다. ignore는 계산 규칙이 없고(M5), Git은 hook·권한·다른 worktree 경계가 빠졌다(M6).
3. 한 명령 설치·전용 실행기·확장 경계: 요구는 충분히 구체적이다. 확장 경계는 과하지 않다(R4만 조정). 빠진 것은 실행기·Git 발견 방법(M7)과 신뢰 기준·갱신 서명(M8)이다.
4. 기존 기능 이식·거부 규칙·검증·비용: 회귀 지도의 기능 범위는 거의 맞다(View 행 추가). 하지만 거부 지점 목록과 기능별 산정이 둘 다 없다(M9).
5. 비공개 의존: 기술 결론은 대부분 저장소로 옮겨졌다. D1–D7 정의, `verification/` 경로, S·감사 원 항목이 남아 있다(M10).

## 6. 추가할 최소 시험

1. 연결 후 Codex·Claude 각 기본 모드, primary·외부 worktree·nested worktree에서 정본 DB와 journal의 생성·commit·복구(M1-5 probe).
2. `cp -R`·`mv` 후 정본 쓰기 거부와 이동 확인 흐름(M1-4, R9).
3. 쓰기와 동시에 export, export→삭제→import 동등성, 한 version 전 export import(M2).
4. 한도 크기 본문 import 중 다른 연결의 조회가 busy 없이 끝남, import 중 kill 후 staged 미게시(M3).
5. NFC·NFD, 대소문자 alias, Windows 예약 이름. Git·비 Git 관측이 같은 entry bytes를 냄(M4).
6. hash 주입 속성 시험: 임의 추가·삭제 순서에서 root 동일, depth 상한 초과 거부, 삭제 후 합치기(M4).
7. ignore: `secret.txt`, `*.log`, `!keep.env` 삭제, 범위 안 `.gitignore` 편집, 환경 변수가 다른 앱·CLI 쌍, D7 통과, D1 orphan 거부(M5).
8. Git: 다른 worktree에 checkout된 branch 거부, 활성 hook 거부, ref 갱신 후 index 갱신 전 kill → 복구 분류, 통합 후 사용자 commit → index 미수정(M6).
9. Command Line Tools 없는 macOS에서 대화상자 없이 Git 부재 안내, PATH 앞 다른 git(M7).
10. 서명 불일치 갱신 manifest 거부, 낮은 version channel index 거부(M8).

## 7. 보정 규모 추정

[추정, 근거: 이번에 읽은 문서 분량과 보정 항목 수] 명세 문장 보정(M3–M7, M10)은 Driver 기준 약 3–5 활동시간이다. 거부 지점 정적 목록(M9-b)은 Core·공식 실행 약 15천 줄 대상이라 2–4시간, 기능별 산정표(M9-a)는 1–2시간으로 본다. M1·M2·M8은 Owner 결정 대기 시간이 따로 들고, M1 probe는 실제 호스트 실행 승인이 필요하다. 이 수치는 실측이 아니며, 호스트 설정 지원 여부(M1-5)에 따라 크게 달라질 수 있다.

## 8. Owner 결정이 필요한 것

1. 정본을 사용자 데이터 위치에 두고 호스트별로 쓰기 범위를 한 번 추가하는 안(M1)을 받아들일지. 받아들이지 않으면 어느 세션 종류를 제약 조합으로 둘지.
2. "기록은 Git·clone에 포함되지 않고 이 컴퓨터에만 있으며, 백업은 내보내기로 한다"는 데이터 약속(M2).
3. 첫 설치 신뢰 기준과 첫 공개부터 갱신 서명 key를 고정하는 안(M8).
4. 기능별 산정 결과가 기존 중단 상한을 넘을 때 상한을 조정할지(M9-a 이후).

이 응답은 구조 검토 의견이다. 결과 수락, 구현 승인 범위 변경, commit·설치·공개를 대신하지 않는다.
