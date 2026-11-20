# 설치와 프로젝트 연결

[사용 설명서](README.md) · 한국어 · [English](../en/install.md)

Colvia를 사용할 운영체제 계정에 한 번 설치한 뒤, 해당 계정에서 사용할 프로젝트 폴더를 하나씩 연결하세요. 같은 계정에서 설치한 Colvia로 여러 프로젝트를 사용할 수 있습니다.

[설치하기](#install) · [설치한 버전 확인하기](#check-installed-version) · [프로젝트 폴더 연결하기](#connect) · [접근이 막혔을 때](#access)

## 시작하기 전에

- Codex 또는 Claude Code를 설치하고 로그인하세요.
- 사용 중인 운영체제와 에이전트가 [지원 환경](reference.md#environments)에 해당하는지 확인하세요.
- 운영체제의 실행 허용, 알림 허용, Codex·Claude 구독 로그인은 사용자가 직접 해야 할 수 있습니다. 이는 전용 Python 준비와 별개입니다.

<a id="install" name="install"></a>

## 설치하기

[공식 설치 페이지](https://colvia.github.io/downloads/#ko)에서 운영체제에 맞는 설치 명령을 복사해 실행하세요. Colvia가 배포 파일을 내려받아 검증하고 전용 Python을 준비합니다. 준비가 끝나면 [설치한 버전](#check-installed-version)을 확인하세요. 이후 절차는 [업데이트와 중단 복구](maintenance.md#update)에서 확인할 수 있습니다.

체험을 마친 뒤에는 [기록을 보존하며 제거](maintenance.md#uninstall)하거나 [임시 수동 절차로 이 계정의 연결과 기록까지 삭제](maintenance.md#remove-all)할 수 있습니다.

Windows에서는 시작 메뉴에서 일반 PowerShell을 표준 사용자로 열어 설치 명령을 실행하세요. 앱 전용 셸에서 설치 위치를 확인할 수 없다는 안내가 나오면 일반 PowerShell에서 이어가세요. 디스크 공간이 부족하다는 안내가 나오면 표시된 필요 공간과 여유 공간을 확인하세요.

<a id="check-installed-version" name="check-installed-version"></a>

### 설치한 버전 확인하기

Colvia 준비가 끝나면 아래 명령을 실행해 `Colvia` 뒤에 표시되는 버전을 확인하세요.

macOS 터미널

```sh
"$HOME/Library/Application Support/Colvia/bin/colvia-manage" status
```

Windows의 일반 PowerShell

```powershell
& (Join-Path ([Environment]::GetFolderPath("LocalApplicationData")) "Colvia\bin\colvia-manage.exe") status
```

<a id="connect" name="connect"></a>

## 프로젝트 폴더 연결하기

설치가 끝나면 사용할 프로젝트 폴더에서 Codex 또는 Claude Code를 열고 요청하세요.

> 이 폴더에 Colvia를 연결해 주세요.

Git을 쓰지 않는 폴더가 Colvia 기록과 같은 볼륨에 있고 두 경로가 서로 겹치지 않으면, 첫 연결 때 Git 사용 여부를 선택할 수 있습니다. “일반 폴더로 쓸게요” 또는 “이 폴더에서 Git도 시작할게요”라고 답하세요. 빈 폴더와 기존 자료가 있는 폴더 모두 가능합니다. Git을 선택하면 미리보기에서 폴더 위치와 새 로컬 저장소의 첫 브랜치(`main`)를 확인하세요. 계정에 Git 등록이 필요하면 같은 미리보기에 사용할 실행 파일이 표시됩니다. 내용을 보고 승인하거나 여기서 취소하세요. 기존 파일은 스테이징되지 않으며, 첫 커밋과 원격 저장소 연결은 나중에 결정할 수 있습니다. 승인한 뒤 연결이 중단되면 에이전트에게 같은 작업 번호로 연결을 이어 달라고 요청하세요. Colvia가 프로젝트 연결 파일의 적용을 준비하기 전이라면 “연결 예약을 취소하고 다시 보여 주세요”라고 해도 됩니다. 이미 만든 Git 저장소와 계정에 등록한 Git은 그대로 남습니다.

보고서를 쓰거나 웹앱을 만드는 등 새 일을 시작할 때는 빈 폴더를 연결해도 됩니다. 이미 작업 중인 프로젝트에도 연결할 수 있습니다. Git을 사용하는 프로젝트 폴더라면 먼저 [에이전트에게 Git 등록을 요청](git.md#git-register)한 뒤 저장소의 최상위 폴더에서 연결합니다.

에이전트가 보여 주는 연결 미리보기에서 폴더, 추가할 실행기와 안내, 기록 저장 위치를 확인한 뒤 승인하세요. 기존 프로젝트 규칙을 사용하고, 필요한 경우 에이전트 지침에 Colvia 안내를 덧붙입니다.

### 연결하면 달라지는 것

| 위치 | 담기는 내용 |
| --- | --- |
| 프로젝트 폴더 | 프로젝트 실행기(macOS의 `colvia`, Windows의 `colvia.cmd`), 연결 정보, 에이전트용 안내 |
| 운영체제의 사용자 데이터 폴더 | 프로젝트별 작업 기록을 담은 SQLite 데이터베이스, 전용 실행기와 관리 도구 |

Colvia는 운영체제의 사용자 데이터 폴더에 있는 SQLite 데이터베이스에 프로젝트별 작업 기록을 보관합니다. 프로젝트 폴더에는 연결 정보와 에이전트용 안내를 둡니다. 앱과 CLI는 같은 전용 실행기를 사용합니다. 정확한 경로는 [파일과 폴더 위치](reference.md#locations)에 있습니다.

연결한 폴더에서는 macOS의 `./colvia guide` 또는 Windows의 프로젝트 실행기 `colvia.cmd`(PowerShell에서는 `.\colvia.cmd guide`)로 안내를 읽습니다. 에이전트는 같은 실행기로 `ordinary list`를 호출해 현재 작업을 확인합니다.

연결을 마치면 [하고 싶은 일부터 시작](work.md#start)하세요.

<a id="access" name="access"></a>

## 접근이 막혔을 때

작업이 막혔다면 에이전트에게 어디서 멈췄는지 물어보세요. 다음 세 경우는 각각 해결 방법이 다릅니다.

- 실행기가 열리지 않는 경우
- 파일이나 기록 폴더를 읽고 쓸 수 없는 경우
- Colvia가 승인 범위 밖의 변경을 거부한 경우

앱이나 CLI에서 필요한 경로만 허용할 수 있다면 그 방법을 사용하세요. 필요한 경로에만 권한을 줄 방법을 확인할 수 없다면 해당 변경을 멈추고, 어디서 막혔는지와 다음에 할 수 있는 일을 확인하세요. 확인하는 동안 파일 접근은 필요한 경로로 제한하고, 시험 기능은 꺼 둔 채 진행하세요.

에이전트에 따라 작업 폴더뿐 아니라 Colvia 기록 폴더의 접근을 허용해야 할 수 있습니다. 확인한 구성은 [지원 환경](reference.md#environments)에 있습니다.

---

다음 · [따라 하기](tutorial.md) · [일을 맡기고 검토하기](work.md)
