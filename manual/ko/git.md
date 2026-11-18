# Git과 함께 쓰기

[사용 설명서](README.md) · 한국어 · [English](../en/git.md)

Git을 사용하는 프로젝트에서는 연결 전에 Git을 Colvia에 등록합니다. 결과를 수락하는 일과 그 결과를 Git에 반영하는 일은 별개의 결정입니다.

[Git 등록하기](#git-register) · [명령으로 등록하기](#git-register-cli) · [Git에 결과 반영하기](#git-integration) · [중단된 Git 반영 복구하기](#git-recovery)

<a id="git-register" name="git-register"></a>

## Git 등록하기

일반 폴더는 바로 연결할 수 있습니다. Git을 사용하는 프로젝트 폴더라면 저장소를 연결하기 전에 평소 쓰는 채팅에서 요청하세요.

> 이 프로젝트에서 쓰는 Git을 Colvia에 등록해 주세요.

에이전트가 현재 환경에서 쓰는 Git 실행 파일을 찾아 등록 미리보기를 준비할 수 있습니다. 경로가 여러 개라면 실제로 쓰는 Git을 골라 주세요. 미리보기에서 경로를 확인하고 등록을 승인하면, 에이전트가 미리보기 원본으로 등록을 적용합니다. 기존 등록을 바꾸는 경우에는 교체할 경로를 확인하고 별도로 승인하세요. 등록을 확인한 뒤 저장소의 최상위 폴더에서 [연결을 요청](install.md#connect)하세요. 같은 Colvia 설치에서 이미 등록한 Git은 다른 프로젝트를 연결할 때도 사용할 수 있습니다.

앱이나 CLI가 등록에 필요한 경로나 실행을 막으면, 에이전트에게 어느 접근이 필요한지 확인하세요. 앱에서 필요한 범위만 허용할 수 있으면 그 방법을 쓰고, 직접 진행하려면 [아래 명령](#git-register-cli)을 사용하세요.

<a id="git-register-cli" name="git-register-cli"></a>

### 명령으로 Git 등록하기

신뢰하는 Git 설치의 실행 파일을 지정하세요. Windows PowerShell에서 `(Get-Command git).Source`로 사용 중인 Git 경로를 확인할 수 있습니다. 일반 PowerShell은 설치에 사용하고, 미리보기 원본을 파일로 저장할 때는 명령 프롬프트(cmd.exe)를 사용하세요. Windows PowerShell 5.1의 `>` 또는 `Out-File`은 출력의 인코딩을 바꿀 수 있습니다.

**Windows.** 명령 프롬프트에서 아직 `git-registration.json`이 없는 로컬 NTFS 폴더를 사용하세요. 아래 예의 Git 경로는 방금 확인한 실제 절대 경로로 바꾸세요.

```cmd
"%LOCALAPPDATA%\Colvia\bin\colvia.exe" manage git-register-preview "C:\Path\To\Git\cmd\git.exe" > git-registration.json
```

이 미리보기는 Git을 실행하지 않습니다. 저장한 파일을 읽어 Git 경로, 파일 해시, `receipt` 값을 확인하세요. `receipt`는 미리보기에 들어 있는 확인값입니다. 파일을 편집하거나 다시 저장하지 마세요. 미리보기에서 오류가 나면 그 파일을 적용하지 마세요. 안내된 원인을 해결한 뒤 다른 이름으로 새 미리보기를 저장하세요. 검토 후 등록을 승인했다면 같은 명령 프롬프트에서 아래의 `RECEIPT_FROM_PREVIEW`를 그 값으로 바꿔 적용하세요. 기존 등록을 바꿀 때는 교체를 확인한 뒤에만 `--replace`를 붙입니다.

```cmd
"%LOCALAPPDATA%\Colvia\bin\colvia.exe" manage git-register --plan git-registration.json --receipt "RECEIPT_FROM_PREVIEW"
```

**macOS.** 아직 `git-registration.json`이 없는 로컬 폴더에서 터미널을 여세요. 아래의 `/path/to/git`은 사용 중인 Git 실행 파일의 절대 경로로 바꿉니다. 미리보기를 저장해 위와 같은 방식으로 검토한 뒤, 등록을 승인했다면 `RECEIPT_FROM_PREVIEW`를 확인값으로 바꿔 적용하세요.

```sh
"$HOME/Library/Application Support/Colvia/bin/colvia" manage git-register-preview "/path/to/git" > git-registration.json
"$HOME/Library/Application Support/Colvia/bin/colvia" manage git-register --plan git-registration.json --receipt "RECEIPT_FROM_PREVIEW"
```

미리보기를 검토하고 등록을 승인하면 Colvia 관리자가 선택한 실행 파일의 해시를 다시 확인한 뒤 Git 버전을 조회합니다. 해시는 그 실행 파일만 다루므로 Git 설치 출처와 함께 설치된 구성요소도 신뢰할 수 있어야 합니다.

<a id="git-worktree-registration" name="git-worktree-registration"></a>

## 등록된 worktree 때문에 명령이 멈췄을 때

Git에 등록된 worktree(별도 작업 폴더)가 사라졌거나 등록에 `bare` 항목이 있으면, Colvia는 연결 미리보기나 이미 연결한 프로젝트의 명령에서 저장소 구조를 확인하다 멈출 수 있습니다. 에이전트에게 문제가 된 등록을 보여 달라고 요청하세요. 직접 살펴보려면 Git 저장소에서 아래 명령을 실행하세요.

```sh
git worktree list --porcelain
```

- `prunable` 표시가 있으면 경로부터 확인하세요. 폴더를 옮겼거나 드라이브에 접근할 수 없다면 원래 경로에서 접근을 복구하세요. 실제로 사라진 폴더라면 저장소 관리자에게 해당 경로의 브랜치·작업 파일·스테이징을 확인하고 필요한 자료를 보존한 뒤 그 등록을 정리해 달라고 요청하세요.
- `bare` 표시가 있으면 작업 폴더 없이 Git 데이터만 가진 저장소입니다. 지원 조건을 충족하는 일반 Git 작업 폴더가 있는지 저장소 관리자에게 확인해 달라고 요청하세요.

Git의 일괄 정리 명령은 여러 등록에 영향을 줄 수 있습니다. `.git` 내부와 다른 worktree 등록을 보존하고, 관리자가 확인한 조치 뒤 막혔던 명령을 다시 확인하세요. 연결 중에 멈췄다면 [연결 미리보기](install.md#connect)를 다시 확인하세요.

<a id="git-integration" name="git-integration"></a>

## Git에 결과 반영하기

수락한 제출본은 임시 커밋(WIP 커밋) 없이도 Colvia에 남아 나중에 현재 파일과 비교할 수 있습니다. 수락한 결과를 Git에 반영하려면 커밋에 들어갈 변경 전체와 현재 스테이징 상태를 확인하고 별도로 승인하세요. Colvia는 Git 객체를 만들기 전에 수락한 파일과 커밋 메시지를 내 기기에서 검사합니다. 알려진 형태의 토큰·개인 키나 설정에 직접 적은 비밀번호·API 키를 발견하면 위치를 알려줍니다. 해당 값을 지우거나 환경변수 참조로 바꾼 뒤 수정본을 다시 제출하고 수락하세요. 메시지에서 발견했다면 메시지만 고치세요. 이 검사는 Colvia를 통해 Git에 반영할 때 적용되며, 이미 저장한 Work와 Git 이력은 원래 내용을 유지합니다.

`.env`, `.env.local`, `.env.production`과 `secrets/` 폴더 아래의 파일은 내용과 관계없이 추가·수정이 차단됩니다. 하위 프로젝트에도 같은 규칙이 적용되며 대소문자를 구분하지 않습니다. 공유할 설정은 `secrets/` 밖에 `.env.example`이나 `.env.template`으로 두고 실제 값 대신 환경변수를 참조하세요. 예시 파일도 내용 검사를 거칩니다. `.netrc`(Windows의 `_netrc` 포함), Terraform 상태 파일 `*.tfstate`와 백업 `*.tfstate.backup`, `*.tfstate.<숫자>.backup`도 추가·수정이 차단됩니다. 이미 추적 중인 보호 파일을 삭제할 때는 미리보기에 삭제 사실만 표시합니다.

`.npmrc`는 프로젝트에서 공유할 수 있습니다. `_authToken`, `_auth`, `_password` 같은 인증 항목에 값을 직접 적으면 Git 반영이 멈춥니다. 레지스트리 주소와 설정은 두고 인증값을 `${NPM_TOKEN}`처럼 환경변수로 참조하세요. 기존 토큰을 환경변수 참조로 바꾸면 미리보기에 새 설정만 표시됩니다.

이전 파일에 자격증명이 있거나 내용을 검사할 수 없으면 삭제 사실 또는 새 내용을 보여주고 이전 본문은 숨깁니다. 새로 추가하거나 수정하는 파일은 검사 가능한 UTF-8 텍스트여야 합니다. 예전 미리보기를 다시 준비하라는 안내가 나오면 새 후보를 만드세요. 후보를 준비하면 Git 객체가 만들어집니다. 현재 브랜치와 스테이징 영역에 반영하는 일은 후보를 검토한 뒤 별도로 승인합니다.

Colvia는 다른 파일에 스테이징한 변경을 보존합니다. 선택한 파일의 스테이징 내용이 현재 커밋과 수락한 결과 중 어느 쪽에도 맞지 않으면, 스테이징한 변경을 보호하기 위해 Git 반영을 멈춥니다.

작업 중 branch를 바꾸거나 pull·rebase로 기준이 바뀌면 자동으로 새 기준을 승인하지 않습니다. 범위 밖 변경을 숨기지 않고, 이어갈 방법을 확인합니다. 프로젝트 하위 폴더의 독립 연결이나 Git 사용 여부가 바뀐 폴더의 자동 전환은 첫 Preview의 지원 범위 밖입니다. 심볼릭 링크와 submodule은 그대로 보호할 수 있지만 편집 대상으로 삼지 않습니다.

Git hook이 있거나 자동 통합 조건을 만족하지 않으면 Colvia가 임의로 hook을 끄거나 index를 초기화하지 않습니다. 수동 Git 작업으로 이어갈 때도 수락한 결과와 commit할 내용을 다시 대조하세요.

<a id="git-recovery" name="git-recovery"></a>

## 중단된 Git 반영 복구하기

Colvia의 Git 반영이 중단됐다면 `index.lock`을 지우거나 새 commit을 만들지 마세요. 원본 index를 보존하는 도중 현재 index가 잠시 없을 수 있습니다. 통합 상태를 조회하고 복구 경로로 이어가며, 잠금 소유자를 확인하지 못하면 먼저 진단해야 합니다. Windows의 Git 반영은 같은 볼륨의 준비 공간이 필요하며, 실행 비트가 없는 hook 파일도 활성 hook으로 취급합니다.

Windows에서 Colvia의 Git 반영이 중단되면 에이전트에게 “중단된 Git 반영 상태와 잠금 위치를 확인해 줘”라고 요청하세요. Colvia가 잠금 파일을 옮기기 전에 남긴 기록과 현재 파일이 일치하면 상태 확인 뒤 복구를 이어갈 수 있습니다. Git 반영 전 중단이면 이번 반영을 하지 않은 상태로 정리하고, 이미 반영을 시작했다면 승인된 변경의 완료 여부를 확인합니다. 다른 Git 프로그램의 잠금, 변경된 파일, Colvia가 만든 것으로 확인할 근거가 없는 잠금은 자동으로 가져오거나 지우지 않습니다. 다른 Git 작업이 끝났는데도 계속 막히면 중단 기록을 보존해 진단을 요청하세요. Work 수락과 새 Git 반영 승인은 이 복구와 별개입니다.

---

다음 · [기록과 백업, 폴더 이동](records.md) · [구조가 궁금하다면 · Git과의 경계](architecture.md#git-boundary)
