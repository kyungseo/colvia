# R1 구조 검토 응답 — Clean-start 새 형식 계약

작성 2026-11-06 · Reviewer: Claude Opus 5.5 (`claude-opus-5-5`) · Owner 수동 전달분 검토

이 문서는 원문 검토를 보존한 source-only 기록이다. 아래 packet/input 이름은 당시 입력 식별자이며 저장소 실행이나 비공개 파일 접근을 요구하는 링크가 아니다. 현재 처분은 [Driver 의견](review-disposition.md)을 따른다.

## 0. 검토 조건과 한계

- 입력: `R1-STRUCTURE-PACKET.md` (sha256 `32bdccbb…8517`, 373줄). `R1-inputs.json`의 packet hash와 일치함을 확인했다. 구성 문서 세 개(NEW-FORMAT-CONTRACT, FOCUSED-DIAGNOSTICS-RESULT, CONCURRENCY-ASSUMPTIONS)와 source 발췌 네 개만 근거로 삼았다.
- 독립성 한계: 이 세션은 CLI·데스크톱 시험을 관찰했고(D1–D7), STRUCTURE-PROPOSAL(S1–S11)과 R0 응답을 쓴 같은 세션이다. 내가 제안한 S6·S11이 반영된 부분은 내 제안을 내가 검토하는 셈이다. 독립 reviewer를 대체하지 않는다.
- packet 조건 위반 공개: packet은 "명령·파일 접근 없음"을 요구했지만, packet 본문을 읽고 input identity를 대조하려고 파일 읽기와 `shasum`·`grep`만 실행했다. 다른 명세 파일(IMPLEMENTATION-SPEC-DRAFT, STRUCTURE-DECISION-DRAFT 최신본)이나 source는 이번 검토에서 열지 않았다. 다만 이전 대화에서 읽은 초안·시험 기록 지식은 남아 있으며, 그것을 쓴 곳은 표시했다.
- 근거 구분:
  - [정적] 이번 packet 문장에서 추론한 것
  - [외부 지식] SQLite·Git·agent sandbox의 문서화된 동작에 대한 내 지식. 이번에 실행 확인하지 않았다.
  - [Driver 실행] FOCUSED-DIAGNOSTICS의 측정·index 재현. 나는 아무것도 실행하지 않았다.

## 1. 판정

**구현 전 필수 수정 후 진행 가능(ready with mandatory corrections)**

큰 방향(Git 저장소당 공통 authority, workspace별 결과, 승인 파일의 전후 본문 보존, Git 통합 분리, SQLite로 transaction 위임)은 맞다. 다만 아래 두 가지는 형식이 첫 공개로 고정되기 전에 결정해야 하고, 되돌리는 비용이 크다.

1. authority 위치가 agent sandbox에서 실제로 쓰기 가능한지 아직 확인되지 않았다(F1). 확인 전에는 locator(2단계)를 구현하지 않는다.
2. 기록이 Git 밖으로 나가는 데이터 약속 변경은 Owner의 명시 결정이 필요하다(F2).

나머지 필수 수정(F3–F8)은 계약 문구를 고치면 되고, 1단계(pure schema·store) 착수를 막지 않는다.

```
1단계 store/tree ── F3·F4 반영 후 착수 가능
2단계 locator ───── F1 확인 + F2 Owner 결정 후
3단계 lifecycle ─── F5·F8·F9·F10 반영
4단계 capability ── F7 범위 결정 후
5단계 Git 통합 ──── F6 계약을 형식 고정 전에 명시
```

## 2. 구현 전 필수 수정

### F1. [Blocker 후보 · 축1] `.git/colvia`가 agent의 기본 sandbox에서 쓰기 금지일 수 있다

- 위치: NEW-FORMAT-CONTRACT "Chosen Foundation" — "Git authority under verified common-dir/colvia".
- 반례 [외부 지식, 미검증]: Codex CLI·앱의 기본 `workspace-write` sandbox는 쓰기 가능한 root 안의 최상위 `.git` 디렉터리를 읽기 전용으로 둔다고 알고 있다. 그렇다면 primary checkout에서 `./colvia`가 `state.sqlite3`와 rollback journal을 만들 때 쓰기가 거부된다. 모든 기록 쓰기마다 권한 상승 확인창이 뜨거나 명령이 실패한다. linked worktree 세션에서는 common-dir 자체가 쓰기 root 밖이다. Claude Code 앱도 저장소의 일부 Git 파일을 sandbox 보호 대상으로 다룬다.
- 왜 필수인가: 확인창이 작업마다 반복되면 "작은 일반 사용 흐름"(축6)이 무너진다. 위치는 첫 공개 뒤 바꾸려면 migration이 필요하다.
- 최소 수정:
  1. 2단계 전에 qualification probe를 한다(약 15–30분 추정). 대상은 Codex CLI 기본 모드, Codex 앱 기본·worktree 모드, Claude Code CLI·데스크톱 기본 모드이고, 각각 primary와 linked worktree에서 시험한다. 확인할 것은 `<common-dir>/colvia/` 생성, SQLite DB와 journal 생성·삭제, `BEGIN IMMEDIATE` commit이다.
  2. 막히면 조용히 다른 위치로 우회하지 않고 Owner 결정으로 올린다. 선택지는 "쓰기마다 권한 상승"과 "working tree 안 위치"(`git clean -fdx`로 기록이 지워지는 위험)이며, 사용자 흐름을 바꾸는 결정이다. 계약도 "user-facing feature decision returns to Owner"라고 적고 있다.
  3. 통과하면 지금 설계를 유지한다. common-dir은 `git clean -x`에서 안전하고 working tree 관찰에도 섞이지 않는다는 장점이 있다.

### F2. [High · 축3·5] 기록이 Git 이력에서 빠지는 데이터 약속 변경이 명시되지 않았다

- 위치: "Chosen Foundation", "Transactional Authority" — authority가 `.git` 안의 SQLite 한 파일이다.
- 반례 [정적]: 시험에서는 `.hrn/`을 commit해서 기록이 push·clone·백업과 함께 다녔다. 새 형식에서는 다음이 된다.
  - clone에는 기록이 없다.
  - 노트북을 잃거나 `.git`을 다시 만들면 수락 이력도 모두 사라진다.
  - SQLite 파일 하나가 유일한 사본이고, 페이지 손상 시 "unavailable" 말고는 복구 경로가 없다.
- 평가: 이 방향 자체는 맞다고 본다. `git status` 소음(D4)과 branch 전환 시 기록 되돌림이 사라지기 때문이다. 다만 "기록은 이 컴퓨터의 이 저장소에만 있다"는 것은 사용자 데이터 약속이 바뀌는 일이다.
- 최소 수정: Owner가 명시적으로 수락하게 한다. 사용자 문서와 connect preview에 "기록은 Git에 포함되지 않음, 백업은 export"를 한 줄로 적는다. export·import는 3단계 필수 기능으로 두고(이미 포함됨), export 형식을 공개 호환 표면으로 versioning한다(F4 ⑤).

### F3. [High · 축3·6] adaptive hash-trie는 정규형 규칙이 없고, 더 단순한 고정 분할로 충분하다

- 위치: "Transactional Authority" 넷째 문단 — branch 최대 256, leaf 128 entries, depth 8까지 분할.
- 반례 1 [정적]: 정규형 규칙이 없다. 분할은 정의돼 있지만 삭제 뒤 다시 합치는 규칙이 없다. 그러면 같은 경로 집합이라도 만든 순서에 따라 root hash가 달라진다. 예를 들어 129개를 넣고 1개를 지운 tree와 128개를 넣은 tree가 다르게 나온다. root hash로 비교하면 "변경됨" 오판이 나고 중복 제거도 깨진다. 합치기 규칙을 넣으면 split·merge·depth 경계 시험이 그만큼 늘어난다.
- 반례 2 [정적]: depth 8이 필요한 경우가 사실상 없다. 한 leaf가 넘치려면 128개 넘는 경로가 SHA-256 앞 8 bytes를 공유해야 하는데, 이는 실현 불가능하다. 반면 depth·split·traversal 예산 검증 코드는 실제로 생긴다.
- 대안 계산 [정적]: 경로 hash의 첫 byte 기준 256 bucket을 한 단계만 둔다.

  | 파일 수 | bucket당 entry | leaf 크기 대략 | 1경로 변경 시 다시 쓰는 양 |
  | ---: | ---: | ---: | --- |
  | 3,000 | ~12 | ~2KB | leaf 1개 + root(~10KB) |
  | 100,000 | ~390 | ~60KB | leaf 1개 + root |
  | 1,000,000 | ~3,900 | ~600KB | 4MiB 한도 안 |

- 최소 수정(권장 설계 하나): adaptive trie를 고정 1단계 256-bucket map으로 바꾼다.
  - root는 비어 있지 않은 bucket의 (index, kind, digest, length) 목록이다. leaf는 경로순으로 정렬한 고유 entry다.
  - 구조가 entry 집합만의 함수이므로 정규형이 자동으로 보장된다.
  - leaf가 4MiB를 넘으면 게시 전에 거부한다.
  - 비교는 bucket digest가 다른 leaf만 연다.
  - 확장이 필요해지면 형식 version을 올린다.
  - 속성 시험: 같은 집합을 임의의 추가·삭제 순서로 만들어도 root가 같아야 한다.

### F4. [High · 축2·5] SQLite 사용 계약에 빠진 설정과 상태가 있다

- 위치: "Transactional Authority", "First Public Release".
- 반례와 수정 [외부 지식, 미검증]:
  1. macOS 내구성: macOS에서 SQLite의 `synchronous=FULL`은 기본적으로 `fsync`만 부르고, 이것은 드라이브 캐시를 비우지 않는다. 그래서 정전 시 commit된 수락이 사라질 수 있다. 수정: macOS에서 `PRAGMA fullfsync=ON`을 쓴다. 내구성 표현은 지원 OS별로 한정한다.
  2. hot journal과 읽기 전용 조회: crash 뒤 hot journal이 남아 있으면 read-only connection은 rollback을 못 해서 `SQLITE_READONLY_ROLLBACK` 계열 오류가 난다. 계약은 "corrupt면 unavailable"만 정의해서, 정상적으로 복구 가능한 상태를 손상으로 보고할 수 있다. 수정: "복구 필요" 상태를 따로 분류한다. 다음 writer나 `repair`가 rw로 열어 복구한다. 읽기 전용 sandbox 세션에서는 그 사실만 안내한다. fault-injection 목록에 추가한다.
  3. 긴 읽기 transaction: rollback-journal 모드에서는 reader가 SHARED lock을 쥐는 동안 writer가 commit할 수 없다. "Query uses one read transaction"을 대용량 본문 hash 검증까지 넓히면, 다른 세션의 수락이 busy timeout으로 실패한다. 수정: 읽기 transaction은 head와 참조 목록 확정까지만 쓴다. 게시된 객체는 갱신·삭제하지 않는다(GC 없음)는 불변식에 기대어, 객체 본문 읽기는 이어지는 짧은 transaction으로 나눈다. 이 불변식은 계약에 명시해, 이후 GC 도입 시 함께 재검토하게 한다. writer에는 명시적 busy timeout을 두고, 시간이 넘으면 "다른 Colvia 작업 진행 중"으로 거부한다.
  4. SQLite library version: Python 표준 `sqlite3`는 빌드에 따라 SQLite 버전이 다르다. source launcher는 PATH의 `python3`을 쓰고 managed runtime은 고정 버전이다. STRICT table, `RETURNING` 같은 기능을 쓰면 오래된 library에서는 schema를 열 수 없다. 수정: 최소 SQLite 버전을 schema 계약에 기록한다. 열 때 `sqlite3.sqlite_version`을 확인하고, 그 버전을 넘는 기능은 쓰지 않는다. runtime 호환성 검사(rollback 허용 여부)에 이 값을 포함한다.
  5. export 형식도 공개 호환 표면이다. version을 붙이고, 한 version 전 export를 import하는 시험을 둔다.
- 본문을 SQLite에 두는 것 자체에 대한 판단: Driver 안을 유지해도 된다. 큰 본문 import 동안 writer lock이 길어지는 것은 per-file 256MiB·Work당 1GiB 한도로 묶인다. 별도 파일 객체 저장소를 두면 fsync·rename·고아 파일 규칙이 추가돼 저장 방식이 둘이 된다. 이 비용이 얻는 정확성보다 크다고 본다. 조건: 한도 크기 import의 lock 유지 시간을 측정해서, 다른 writer의 busy timeout보다 길면 per-file 한도를 낮춘다.

### F5. [High · 축1] D7 "실제 효과가 구조 경계 안에 한정됨을 증명"하는 규칙이 정의되지 않았다

- 위치: "Bodies, Observation And Acceptance" 셋째 문단. source `validate_manifest`는 ignore fingerprint가 다르면 무조건 거부한다.
- 반례 [정적 + 데스크톱 시험 D7]: Claude 앱이 `info/exclude`에 `.claude/worktrees/` 한 줄을 추가했다. 그러자 worktree를 지운 뒤에도 수락한 보고서가 "비교 기준이 달라져 확인이 필요"로 남았다. 계약은 whitelist를 금지했다(맞다). 하지만 무엇을 계산해야 "동등"인지가 없어서, 구현자가 결국 문자열 비교나 whitelist로 돌아갈 위험이 있다. 또 서로 다른 두 질문이 섞여 있다.
- 최소 수정(규칙 하나):
  1. 수락 결과가 그대로인지 묻는 질문은 수락한 경로의 bytes·mode만 비교한다. ignore 정책과 무관하다. 그 경로가 지금 무시 대상이 됐다면 그 사실만 알린다.
  2. 제출 범위 판정에서는 기준 관찰에 기록된 admitted 경로 목록에 현재 정책을 적용한다. 현재 정책이 새로 제외하는 기준 경로가 모두 검증된 구조 경계(같은 common-dir에 등록된 worktree 디렉터리) 안에 있으면 동등으로 본다. 하나라도 경계 밖이면 "포함 정책 변경"으로 거부한다.
  3. 새로 포함되는 경로(이전에 무시되던 것)는 결과 쪽에서 추가로 나타난다. 그러면 기존 범위 검사가 범위 밖 추가로 거부한다. 따라서 이전 정책을 재현할 필요가 없다.
  4. ignore 원문(`info/exclude`, `core.excludesFile` 내용)은 provenance용 작은 객체로 보존하되, 동등 판정에는 쓰지 않는다.
- 이 규칙에서 D7 시나리오는 이렇게 된다. worktree가 남아 있으면 제외 경로가 경계 안이므로 동등이다. worktree를 지운 뒤에는 제외되는 기준 경로가 없으므로 역시 동등이다. 사용자가 `*.log`를 추가했는데 기준에 `debug.log`가 있었다면 거부된다(경계 밖).

### F6. [High · 축4] Git 후보 계약에 후보 정의, 통합 뒤 index, Git 부작용 규칙이 없다

- 위치: "Git Candidate Contract".
- 반례 1 [정적]: 후보 tree가 무엇인지 정의되지 않았다. "complete tree"가 사용자 index에서 나온다면, 관계없는 staged 수정이 Colvia 수락 commit에 섞인다. HEAD에서 나온다면 그 사실을 적어야 한다.
- 반례 2 [정적 + 외부 지식]: 통합 뒤 index가 어긋난다. `commit-tree`와 `update-ref`로 hook 없이 commit하면, HEAD에는 새 `report.md`가 있지만 사용자 index에는 옛 `report.md`가 남는다. 그러면 `git status`가 수락한 변경을 되돌리는 staged 변경으로 보여 준다. 사용자가 이어서 `git commit`(`-a` 없이)을 하면 수락한 결과가 되돌려진다. "No implicit stage/unstage"만으로는 이 경우를 막지 못한다.
- 반례 3 [외부 지식]: Git 명령의 부작용이 있다.
  - `git status`는 index를 기회적으로 다시 쓴다(optional locks).
  - `core.fsmonitor`가 설정돼 있으면 관찰 중 사용자 hook 프로그램이 실행된다.
  - `update-index`·`hash-object --path`는 clean filter(LFS 등)와 autocrlf 변환을 적용한다. 그래서 Windows `core.autocrlf=true`에서 후보 blob이 working tree bytes와 달라진다.
- 최소 수정:
  1. 후보 = 현재 HEAD tree + 수락된 Work 변경, 변경 bytes는 보존 본문에서 가져온다(live working tree 아님). 관계없는 staged entry는 후보에 넣지 않고 사용자 index에 그대로 둔다. 수락 경로가 index에서 다르게 staged돼 있으면 거부한다.
  2. ref 갱신은 `update-ref <ref> <new> <old>`로 CAS한다. 그 직후 수락 경로의 index entry만 새 blob으로 맞춘다. 이때 `index.lock` 규약을 따르고, 관찰 이후 index가 바뀌었으면 거부한다. 이 index 갱신은 통합 동작의 명시적 일부로 계약에 적는다.
  3. 모든 Git 호출은 `GIT_OPTIONAL_LOCKS=0`, `-c core.fsmonitor=false`로 하고, hook이 없는 plumbing만 쓴다. 관찰 hash는 Colvia가 raw bytes로 계산한다.
  4. 첫 공개에서는 후보 경로에 filter driver, `text`/`eol` 변환 속성, autocrlf가 적용되면 통합을 거부한다. 그 경로는 사용자가 직접 Git으로 처리하게 안내한다.
  5. 시기: 실제 구현은 5단계지만, 후보 record schema는 형식 고정 전에 확정해야 하므로 계약에는 지금 적는다.

### F7. [High · 축7] 32–52h 산정에 4단계 capability 이식이 들어 있지 않다

- 위치: "Estimate And Authority" 세부 산정, "Regression And Incremental Order" 4단계.
- 반례 [정적]: 4단계(planning/follow-up, worker/umbrella, optional official execution, delivery/notification, platform ports)가 세부 산정 네 칸 어디에도 없다. "integration/docs 8–14h"에 공식 실행 capsule과 delivery 이식이 들어갈 수는 없다. CONCURRENCY-ASSUMPTIONS 목록만 봐도 이 기능들은 저마다 고유의 pending·fence·callback 순서 규칙을 갖고 있다. 그래서 64h 상한이 4단계 중간에 닿을 가능성이 높고, 그 시점의 제품은 일부만 이식된 상태다. "do not ship two formats"이니 이전 구현으로 돌아갈 수도 없다.
- 최소 수정:
  1. 첫 공개 capability 집합을 Owner가 정한다. 내 권장: core ordinary + planning/follow-up + 알림 진입 + Git 후보.
  2. worker/umbrella와 official execution은 공개 뒤 capability 추가로 붙인다. 이것은 F4·First Public Release의 schema 확장 경로를 실제로 시험하는 첫 사례가 된다. 단, 그 기능을 쓰는 내부 프로젝트는 그동안 새 제품으로 옮기지 않는다.
  3. capability마다 산정과 상한을 따로 두고, 1–3단계 실측 뒤 재산정한다.

### F8. [Medium-High · 축6] "기존 안전 의미 보존"을 확인할 목록이 없다

- 위치: "Regression And Incremental Order" 첫 문단의 semantic oracle 목록.
- 반례 [정적]: oracle 목록은 기능 단위다. 현재 코드의 개별 거부 규칙은 목록에 없다. 예를 들면 `_pending_guard`의 "다른 Work의 worker pending이 프로젝트 쓰기를 막음", "pending Work blocks worker content application", relation cycle 거부, case alias 거부 같은 것들이다. 새 코드를 새로 쓰면 이런 규칙은 시험이 없는 한 조용히 빠진다. UUID key로 바꾸면서 case alias 검사가 불필요해 보이더라도, 경로의 대소문자 alias는 여전히 대소문자를 구분하지 않는 macOS 파일 시스템에서 위험하다.
- 최소 수정: 3단계 전에 현재 거부 지점 목록을 만든다(오류 code·메시지별, module별). 각 지점을 유지/통합/폐기로 분류하고 이유를 한 줄 적는다. 유지 항목마다 새 시험을 하나씩 둔다. 정적 grep 기반 목록으로 충분하고, 전수 인증이라고 주장하지 않는다.

## 3. 권장 수정 (구현 중 반영 가능)

| ID | 축 | 내용 | 최소 수정 |
| --- | --- | --- | --- |
| F9 | 5 | 비 Git authority가 옛 시험 형식과 같은 `.hrn` 이름이다. 옛 `.hrn/`이 남은 폴더에서 새 형식과 섞이거나, 옛 관찰 제외 규칙이 남아 그 안의 편집이 보이지 않을 수 있다 | 새 이름(예: `.colvia/`)을 쓴다. `.hrn`은 특별 취급하지 않는 일반 내용으로 본다. connect preview에서 "이전 시험 기록은 읽지 않음"을 한 번 알린다 |
| F10 | 3 | 실행 중 범위 확장(revise)으로 경로를 추가할 때, 그 경로가 이미 고쳐졌다면 시작 시점 본문이 없다 | revise 시점 bytes가 시작 기준 hash와 같을 때만 before bytes를 보존한다. 다르면 "기준 본문 없음, hash만"이라고 기록·표시하고 가짜 본문을 만들지 않는다 |
| F11 | 1·3 | Codex 앱의 새 프로젝트 기본 위치가 `~/Documents/ChatGPT/`다(D3). iCloud 데스크탑·문서 동기화가 켜져 있으면 SQLite DB와 journal이 동기화·저장 공간 최적화 대상이 된다 | connect 때 알려진 동기화 root(`~/Library/CloudStorage`, `~/Library/Mobile Documents`, 동기화 중인 Desktop/Documents)를 확인해 경고하고 확인을 받는다. 감지 방법은 qualification이 필요하다 |
| F12 | 1·2 | workspace 수명 경계 시험이 없다 | 시험 추가: 제출 뒤 앱 worktree 삭제·보관(D1), `git worktree prune` 뒤 같은 경로 재추가(새 workspace로 취급), 폴더 통째 복사로 같은 project UUID가 둘 생긴 경우(reconnect 시 사본 감지·거부) |
| F13 | 7 | 성능 목표가 없다. 진단은 graph·topology가 지배적임을 보였다 [Driver 실행] | 내부 목표만 둔다(공개 주장 아님). 예: 3,000 파일·100 Work에서 선택 Work 조회 ≤1초, 일반 Work 1건당 DB 증가량 측정 |
| F14 | 6 | 일반 사용 흐름의 수락 기준이 숫자로 없다 | scripted 시험 하나: 새 연결 프로젝트에서 일반 Work 1건에 사람 결정 2번(범위·수락), 기본 응답에 내부 용어·경로 없음, `git status`에 Colvia 파일 없음(D4 해소 확인) |

## 4. 수정된 계약 요지 (교체 문구 제안)

1. Authority 위치: `<common-dir>/colvia/`. 단, agent 기본 모드 qualification을 통과해야 하며, 실패하면 Owner 결정으로 올린다. 기록은 Git에 포함되지 않고 백업은 versioned export로 한다는 점을 사용자 문서에 적는다.
2. Store:
   - SQLite rollback journal, `synchronous=FULL`, macOS는 `fullfsync=ON`, 최소 SQLite 버전을 확인한다.
   - writer는 `BEGIN IMMEDIATE`로 head를 확인하고 객체를 넣은 뒤 head를 갱신한다. busy timeout이 지나면 명시적으로 거부한다.
   - reader는 head 확정에만 transaction을 쓰고, 불변 객체는 짧은 transaction으로 나눠 읽는다.
   - hot journal은 손상이 아니라 "복구 필요" 상태다.
3. Tree metadata: 경로 hash 첫 byte 기준 고정 256-bucket, 1단계. 정규형이 구조적으로 보장되고, leaf 4MiB를 넘으면 거부한다.
4. 관찰 동등성: 수락 결과 확인은 해당 경로 bytes만 본다. 제출 판정은 "새로 제외된 기준 경로가 모두 등록 worktree 경계 안"일 때만 동등으로 본다. whitelist 없음.
5. Git 통합: 후보는 HEAD + 보존 본문 기반 변경이다. `update-ref` CAS를 하고, 직후 수락 경로의 index만 맞춘다. optional locks·fsmonitor·hook·filter는 끈다. 변환 속성이 있는 경로는 거부한다.
6. 첫 공개 capability 집합은 Owner가 정한다. 나머지는 공개 뒤 schema 확장으로 붙인다. capability별 산정을 둔다.

## 5. 최소 회귀 시험 추가

1. tree 정규형 속성 시험: 같은 집합, 임의 순서로 만들어도 같은 root.
2. leaf 한도 직전·정확히 한도·초과(4MiB) 시험, 초과는 게시 전에 거부.
3. crash 직후 hot journal + read-only 조회 → "복구 필요", 다음 writer가 복구, 수락 내용 동일.
4. 긴 조회 중 다른 세션의 수락 → 성공하거나 명시적 busy 거부. 부분 게시 없음.
5. 최소 미만 SQLite 버전 → 열기 전에 거부.
6. D7: exclude 추가(경계 안) → 동등. `*.log` 추가(경계 밖, 기준에 존재) → 거부. 수락 결과 확인 질문은 정책 변경과 무관하게 답한다.
7. Git: 관계없는 staged 수정 + 부분 staging 상태에서 통합 → 후보에 섞이지 않음, 통합 뒤 `git status`가 수락 경로를 깨끗하게 보여 줌, 나머지 index entry bytes 동일.
8. Git: 모든 Colvia 명령 전후 index bytes가 같음(통합 명령 제외). fsmonitor·filter가 설정된 저장소에서 외부 프로그램이 실행되지 않음.
9. Git: `update-ref` 직전에 사용자가 commit → CAS 실패, 아무것도 바뀌지 않음.
10. 범위 확장 시 이미 바뀐 경로 → "기준 본문 없음" 표시, 가짜 before bytes 없음.
11. workspace 삭제·prune·재추가·폴더 복사(F12).
12. 거부 지점 목록의 유지 항목별 시험(F8).
13. agent 기본 sandbox qualification probe(F1). 제품 회귀 시험이 아니라 2단계 진입 조건이다.

## 6. Owner 결정이 필요한 것

1. 기록을 Git 밖(이 컴퓨터의 이 저장소)에만 두고 export로 백업하는 데이터 약속을 수락할지(F2).
2. F1 probe가 실패할 때 어떤 사용자 흐름을 택할지(probe 뒤 결정).
3. 첫 공개 capability 집합(F7). 내 권장은 core ordinary + planning/follow-up + 알림 진입 + Git 후보.

이 응답은 구조 검토 의견이다. 결과 수락, 구현 승인 범위의 변경, commit·설치·공개를 대신하지 않는다.
