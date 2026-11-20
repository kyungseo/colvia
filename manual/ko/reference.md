# 지원 환경과 참고 자료

[사용 설명서](README.md) · 한국어 · [English](../en/reference.md)

찾아볼 때 쓰는 자료입니다. 절차는 각 안내 페이지에 있습니다.

[지원 환경](#environments) · [파일과 폴더 위치](#locations) · [명령 요약](#commands) · [용어](#glossary) · [문제가 생겼을 때](#problems)

<a id="environments" name="environments"></a>

## 지원 환경

Colvia Preview는 macOS Apple Silicon과 Windows 11 x64·ARM64에서 Codex와 Claude Code의 CLI·데스크톱 앱을 대상으로 합니다.

| 항목 | Preview 지원 범위 |
| --- | --- |
| 운영체제 | macOS Apple Silicon, Windows 11 x64·ARM64 |
| 에이전트 | Codex와 Claude Code의 CLI·데스크톱 앱. Windows에서는 Windows용 앱과 CLI |
| 파일시스템 | macOS의 로컬 APFS, Windows의 로컬 NTFS |
| 검증하지 않은 환경 | 네트워크 공유, 동기화되는 기록 저장소, Windows ReFS·Dev Drive |
| 후속 후보 | Linux와 추가 에이전트. WSL은 Linux 지원을 검토할 때 함께 다룹니다. |

설치와 업데이트를 시작할 때는 운영체제에 맞는 공식 설치 명령을 사용하세요. 설치나 업데이트가 멈췄다면 [업데이트와 중단 복구](maintenance.md#update-recovery)에서 현재 상태에 맞는 절차를 확인하세요. 격리 폴더의 제출본 반영을 다시 시작할 때는 준비 기록과 대상 폴더의 연결부터 확인하세요.

에이전트에 따라 작업 폴더뿐 아니라 Colvia 기록 폴더의 접근을 허용해야 할 수 있습니다. 검증한 Windows x64 설정은 사용자 승인과 지정 기록 폴더 쓰기를 허용한 Codex 앱, Windows 샌드박스 백엔드를 `mxc`로 지정한 Codex CLI 0.167.1입니다. 다른 앱 버전과 승인 방식은 확인 범위가 다를 수 있습니다.

파일 수와 변경량에 따라 기록·백업에 필요한 공간과 처리 시간이 달라집니다. 기록을 자동으로 삭제하지 않으므로 큰 파일이 있는 프로젝트에서는 저장 공간을 확인하세요.

<a id="execution-readiness" name="execution-readiness"></a>

### 문서 실행 준비 상태 확인

첫 Preview에서 Colvia의 에이전트 직접 호출 기능은 비활성입니다. 설치된 실행기의 `execution readiness`로 현재 설정을 확인할 수 있습니다. 이 명령은 프로젝트 기록을 열거나 모델을 시작하지 않습니다. 필요한 파일이 바뀌었거나 없다면 표시된 상태를 확인하세요.

<a id="locations" name="locations"></a>

## 파일과 폴더 위치

<a id="기기--colvia-관리-폴더" name="기기--colvia-관리-폴더"></a>

### 이 계정의 Colvia 관리 폴더

| 운영체제 | 위치 |
| --- | --- |
| macOS | `~/Library/Application Support/Colvia` |
| Windows | `%LOCALAPPDATA%\Colvia` |

| 하위 항목 | 내용 |
| --- | --- |
| `bin/` | 실행기 `colvia`와 관리 도구 `colvia-manage`(Windows에서는 `.exe`), macOS의 알림 수신기 |
| `notification-tools/` | Windows의 알림 수신기 |
| `runtime/` | 전용 Python과 Colvia 코드가 든 런타임 슬롯, 현재 선택 정보 |
| `authorities/<프로젝트 ID>/` | 프로젝트별 기록. SQLite 데이터베이스가 여기에 있습니다. |
| `backups/` | 업데이트 전에 남기는 기록 복구본 |
| `operations/` | 설치·업데이트·연결 같은 관리 작업의 진행 기록과 제거할 때 옮겨 둔 설치 파일 |
| `trust/` | 업데이트 검증에 쓰는 신뢰 정보 |

이 폴더의 파일을 직접 고치거나 지우지 마세요. 복구가 필요하면 [업데이트와 중단 복구](maintenance.md#update-recovery)의 절차를 사용하세요. 에이전트가 기록을 읽고 쓰려면 앱이나 CLI에서 이 폴더의 접근을 허용해야 할 수 있습니다. 설치 제거를 마치고 계정 기록까지 버릴 때는 [임시 수동 삭제 안내](maintenance.md#remove-all)를 따르세요.

### 프로젝트 폴더

연결하면 프로젝트 폴더에 다음 항목이 추가됩니다. 연결 미리보기에서 같은 목록을 확인할 수 있습니다.

| 항목 | 내용 |
| --- | --- |
| `colvia` (macOS), `colvia.cmd` (Windows) | 프로젝트 실행기. 설치본의 실행기를 이 프로젝트 경로로 호출합니다. |
| `AGENTS.md`, `CLAUDE.md` | 파일 끝에 Colvia 안내 블록을 덧붙입니다. 파일이 없으면 새로 만듭니다. 기존 내용은 그대로 둡니다. |
| 연결 정보 | 일반 폴더에서는 `.colvia-link.json`, Git 저장소에서는 공통 Git 디렉터리의 `colvia/connection.json`. 같은 저장소의 worktree도 이 프로젝트 연결을 기준으로 각각 등록됩니다. |

연결 정보는 어느 프로젝트인지 알려 주는 표시일 뿐 기록 자체가 아닙니다. 이 파일을 다른 폴더에 복사해도 그 폴더가 같은 기록을 쓰게 되지는 않습니다.

<a id="commands" name="commands"></a>

## 명령 요약

평소에는 에이전트가 이 명령들을 대신 호출합니다. 직접 실행할 때는 프로젝트 폴더에서 macOS의 `./colvia`, Windows PowerShell의 `.\colvia.cmd`를 사용하세요. 각 명령의 정확한 인자는 `./colvia <명령> --help`로 확인합니다.

### 프로젝트 실행기

| 명령 | 하는 일 |
| --- | --- |
| `guide` | 짧은 시작 안내를 엽니다. 제출·수락은 `guide work`, 중단 후 복구는 `guide recovery`처럼 필요한 주제를 붙여 읽을 수 있습니다. 두 방식 모두 프로젝트 기록을 열지 않고 설치본에서 검증한 안내를 읽습니다. |
| `project status` | 현재 Work에서 내 검토와 다음 행동을 보여 줍니다. 일부만 표시하면 더 볼 수 있습니다. |
| `ordinary list` | 현재 목록에서 보관·폐기 항목을 숨깁니다. `--list-mode current`, `archived`, `all`을 선택할 수 있습니다. JSON 무옵션은 기존 전체 목록입니다. |
| `ordinary lifecycle-preview` · `ordinary lifecycle-apply` | [중단·재개·폐기·대체](work.md#work-lifecycle) |
| `ordinary view`, `ordinary review`, `ordinary content` | Work의 상태, 검토할 제출본, 보관된 본문을 봅니다. |
| `ordinary progress` | 첫 제출 전에 진행 메모를 저장합니다. |
| `ordinary scope-preview` · `ordinary scope-apply` | [첫 제출 전 파일 추가](work.md#scope-change) |
| `ordinary plan`, `plan-review`, `approve`, `start`, `submit`, `accept`, `revise`, `archive` | 계획 기록부터 범위 승인, 제출, 수락, 수정 요청, 보관까지 Work를 진행합니다. |
| `candidate ranked`, `candidate priority-history`, `candidate priority-preview`, `candidate priority-set` | 열린 후보의 순위와 변경 이력을 확인합니다. [사용 예](work.md#candidate-priority) |
| `candidate list`, `candidate save`, `followup` | 다음에 할 일의 후보와 Work의 후속 선택을 보고 기록합니다. |
| `composition` | 상위 Work에 바로 아래 하위 Work를 지정합니다. |
| `worker` | 격리 폴더의 제출본을 대상 폴더에 반영합니다. |
| `delivery` | 준비된 결과의 제출을 맡기고 알림을 보냅니다. |
| `git-integration` | 수락한 결과를 별도 승인으로 Git에 반영하고, 중단된 반영을 복구합니다. |
| `backup status`, `backup export` | 기록 백업 상태를 보고 내보냅니다. |
| `execution readiness` | 문서 실행 설정을 확인합니다. 이 Preview에서 문서 실행 기능은 비활성입니다. |
| `manage` | 같은 설치본의 관리 도구를 호출합니다. |

미리보기와 승인 적용 모두 같은 파일·이유·검사를 지정합니다. 적용할 때만 확인값과 사용자 승인 문구가 필요합니다.

```text
ordinary scope-preview WORK_ID --edit table.md --create appendix.md --reason "Appendix" --check "Sources"
ordinary scope-apply WORK_ID --edit table.md --create appendix.md --reason "Appendix" --check "Sources" --receipt RECEIPT --statement "Approved"
```

첫 제출 전 메모는 `--json ordinary view WORK_ID`에서 받은 `progress_receipt`를 사용합니다. `first_project_note`가 참이면 첫 저장 전 구버전 호환 조건을 알려 주세요. 각 항목은 최대 2,048자의 한 줄입니다. 승인 경로 중 앞의 128개 파일까지 비교하며 한도 밖의 경로나 읽을 수 없는 파일은 확인 불가로 표시합니다.

```text
ordinary progress WORK_ID --receipt RECEIPT --done "…" --checked "…" --remaining "…" --next-action "…"
```

출력은 기본으로 사람이 읽는 요약이고, `--json`을 명령 그룹 앞에 붙이면 기계용 출력이 됩니다. 관련 Work나 진단에 필요한 식별자는 사람용 출력에도 나타날 수 있습니다.

### 관리 도구

`colvia-manage` 또는 프로젝트 실행기의 `manage`로 호출합니다. 파일로 저장해 적용에 쓰는 미리보기처럼 JSON을 출력하는 명령도 있습니다.

| 명령 | 하는 일 |
| --- | --- |
| `status` | 설치한 버전과 상태를 봅니다. |
| `update`, `update-status`, `update-resume` | 업데이트하고, 중단된 업데이트의 상태를 확인하고 재개합니다. |
| `update-rollback-preview`, `update-rollback` | 새 런타임을 선택하기 전에 중단된 업데이트에서 바꾼 설치 파일을 되돌립니다. 이전 버전으로 되돌리는(downgrade) 명령이 아닙니다. |
| `--finish-plain-work ordinary list`, `--finish-plain-work backup export` (프로젝트 실행기) | 직접 Git을 초기화한 원래 폴더에서 기록 조회·백업 및 기존 Work 마무리. [Git 안내](git.md#adopt-git) |
| `git-transition-preview ROOT`, `git-transition-apply`, `git-transition-cancel OPERATION`, `git-transition-resume-preview OPERATION`, `git-transition-resume OPERATION` | 쓰던 일반 폴더의 Git 전환을 미리보고 승인한 뒤 같은 ID로 재개합니다. 변경된 파일·스테이징은 재개 미리보기에서 다시 확인합니다. [Git](git.md#adopt-git) |
| `connect-preview`, `connect`, `connect-resume`, `connect-cancel` | 폴더를 연결합니다. 새 로컬 저장소를 만들려면 `connect-preview ROOT --init-git`으로 미리보세요. 등록한 Git이 없으면 `--git-executable 절대경로`를 추가해 계정 등록도 함께 확인합니다. 승인한 계획·확인값·승인 문구·작업 번호로 `connect`를 실행하고, 중단되면 `connect-resume 작업번호`로 이어갑니다. 연결 파일 적용 준비 전에는 `connect-cancel 작업번호`로 예약을 취소할 수 있습니다. |
| `detach-preview`, `detach` | 프로젝트 연결을 해제합니다. |
| `move-preview`, `move-apply`, `move-status`, `move-resume` | 옮긴 폴더에 기존 연결을 이어 줍니다. |
| `git-register-preview`, `git-register` | 사용할 Git 실행 파일을 등록합니다. |
| `notice-enable`, `notice-disable`, `notice-check` | 알림을 켜고 끄고 확인합니다. |
| `restore-prepare`, `restore-apply`, `rebind-preview`, `rebind` | 백업을 복원하고 복원한 기록을 폴더에 연결합니다. |
| `repair-preview`, `repair-apply` | 호환되는 이전 런타임으로 복구합니다. `--repair` 옵션으로 실행한 복구 모드에서만 사용합니다(예: `colvia-manage --repair repair-preview`). 현재 기록과 호환되는 복구 대상이 있어야 합니다. |

제거와 재설치는 관리 도구가 아니라 공식 설치 스크립트로 진행합니다. [기록을 보존하면서 Colvia 제거하기](maintenance.md#uninstall)

<a id="glossary" name="glossary"></a>

## 용어

| 용어 | 뜻 |
| --- | --- |
| Work(작업 단위) | 범위를 정해 맡기고 검토하는 작업 한 건. 목표, 파일 범위, 검사, 제출본, 결정이 여기에 남습니다. |
| 계획 | 에이전트가 제안한 목표·파일 범위·검사·제외 항목. 기록하면 범위에 든 기존 파일의 본문이 보관됩니다. |
| 범위 승인 | 그 계획으로 일을 맡기겠다는 사용자의 결정 |
| 제출본 | 에이전트가 검토용으로 제출한 결과. 바뀐 본문과 검사 결과를 담습니다. |
| 수락 | 읽어 본 그 제출본을 받아들이겠다는 사용자의 결정. Git 커밋이나 배포를 뜻하지 않습니다. |
| 수정 요청 | 제출본을 고쳐 달라는 결정. 같은 Work에서 이어갑니다. |
| 후보 | 나중에 할 수 있는 일로 저장해 둔 항목. 저장만으로 실행 권한이 생기지 않습니다. |
| 후속 선택 | Work 뒤에 무엇을 할지에 대한 기록. 후보, 다른 Work, 후속 없음, 미정을 구분합니다. |
| 하위 Work | 큰 목표를 나눈 바로 아래 Work. 각 결과와 상위 결과를 따로 수락합니다. |
| 격리 폴더 | 같은 저장소에 등록한 별도 Git 작업 폴더(worktree) |
| 미리보기와 확인값 | 상태를 바꾸기 전에 보여 주는 변경 내용과, 그 내용에 묶인 값(receipt). 확인값이 맞을 때에만 적용됩니다. |
| 프로젝트 실행기 | 프로젝트 폴더의 `colvia` 또는 `colvia.cmd` |
| 관리 도구 | 설치본을 관리하는 `colvia-manage` |
| 연결 | 프로젝트 폴더를 Colvia 기록과 이어 주는 일. 해제해도 파일과 기록은 남습니다. |

<a id="problems" name="problems"></a>

## 문제가 생겼을 때

먼저 에이전트에게 어디서 멈췄는지 물어보세요. 상황에 맞는 안내는 다음과 같습니다.

| 상황 | 볼 곳 |
| --- | --- |
| 실행기가 열리지 않거나 폴더·기록에 접근할 수 없음 | [접근이 막혔을 때](install.md#access) |
| 범위 밖 변경으로 제출이 거부됨 | [맡기고 검토하기](work.md#review) · [승인 범위 밖의 파일이 필요해졌을 때](work.md#scope-change) |
| 새 대화에서 이전 작업을 찾지 못함 | [새 대화나 다른 에이전트에서 이어가기](work.md#resume) |
| 설치나 업데이트가 중단됨 | [설치나 업데이트가 중단됐을 때](maintenance.md#update-recovery) |
| macOS에서 작업 폴더를 다시 확인하라는 안내 | [작업 폴더 다시 확인하기](maintenance.md#folder-confirmation) |
| 프로젝트 폴더를 옮김 | [프로젝트 폴더를 옮긴 뒤 이어가기](records.md#move) |
| 등록된 Git worktree 때문에 명령이 멈춤 | [worktree 등록 확인하기](git.md#git-worktree-registration) |
| Git 반영이 중단됨 | [중단된 Git 반영 복구하기](git.md#git-recovery) |
| 알림이 오지 않거나 결과가 열리지 않음 | [알림 설정하기](maintenance.md#notifications) |
| 격리 폴더 결과의 반영이 중단됨 | [하위 Work와 격리 폴더의 결과](work.md#child-works) |

보존된 파일이나 기록을 지워서 오류를 없애려 하지 마세요. 상태를 확인할 수 없을 때는 멈추고 진단을 요청하는 것이 안전합니다.

## 이전 참조 문서에서 찾아왔다면

<a id="notifications" name="notifications"></a>

- [알림 켜기와 결과 열기](maintenance.md#notifications)

<a id="resume-details" name="resume-details"></a>

- [새 대화에서 이어가기](work.md#resume)

<a id="review-details" name="review-details"></a>

- [제출본을 검토하고 수락하기](work.md#review)

---

[사용 설명서로 돌아가기](README.md) · [아키텍처](architecture.md)
