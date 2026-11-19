# 업데이트, 알림, 연결 해제와 제거

[사용 설명서](README.md) · 한국어 · [English](../en/maintenance.md)

설치한 뒤에 필요한 운영 절차입니다. 범위가 서로 다르니 먼저 무엇을 하려는지 확인하세요.

| 하려는 일 | 영향 범위 | 남는 것 |
| --- | --- | --- |
| [업데이트](#update) | 이 계정의 Colvia 설치본 | 이 설치본에 연결한 프로젝트의 기록과 연결 정보 |
| [알림 켜기·끄기](#notifications) | 이 계정의 알림 수신 | Work의 기존 기록 |
| [프로젝트 연결 해제](#disconnect) | 프로젝트 하나 | 사용자가 작성한 파일과 작업 기록 |
| [Colvia 제거](#uninstall) | 이 계정의 설치본 | 프로젝트 파일, Work 기록, 승인, 제출본, 프로젝트 연결, 설정, 업데이트 신뢰 정보 |

<a id="update" name="update"></a>

## 업데이트

에이전트에게 “Colvia를 업데이트해 주세요.”라고 요청하세요. Colvia를 설치한 계정에서 진행합니다. 에이전트가 설치된 관리 도구와 공식 배포 주소에 접근할 수 있으면 업데이트를 실행할 수 있습니다. 앱에서 실행 권한을 요청하면 명령을 확인한 뒤 승인하세요. 에이전트가 이 계정에서 실행할 수 없다면 터미널에서 직접 실행하세요.

직접 업데이트하려면 [공식 설치 페이지](https://colvia.github.io/downloads/#ko)에서 처음 설치할 때 사용한 명령을 다시 실행하세요. `PATH`에 관리 도구가 등록돼 있으면 `colvia-manage update`를 실행해도 됩니다. 기본 위치에 설치했다면 아래 명령을 사용해 `PATH` 설정 없이 실행할 수 있습니다.

macOS 터미널

```bash
"$HOME/Library/Application Support/Colvia/bin/colvia-manage" update
```

Windows PowerShell

```powershell
& (Join-Path ([Environment]::GetFolderPath("LocalApplicationData")) "Colvia\bin\colvia-manage.exe") update
```

Colvia는 설치할 때 확인한 배포 주소에서 새 버전을 확인합니다. 이미 최신 버전이면 현재 런타임을 계속 사용합니다.

업데이트 전에 등록된 기록의 복구본을 남기고, 기록에 필요한 기능과 새 런타임이 선언한 기능을 대조합니다. 이 호환성 확인이 모든 사용자 작업을 실제로 실행해 보는 것은 아닙니다. 이전 런타임으로 돌아갈 때도 작업 이력을 과거로 되돌리지 않습니다.

<a id="update-recovery" name="update-recovery"></a>

### 설치나 업데이트가 중단됐을 때

업데이트가 중단되면 설치 파일을 바꾸기 전에 어디까지 진행됐는지 먼저 확인하세요. 재개하려면 준비한 배포본과 현재 상태가 일치하고 검증도 유효해야 합니다.

| 상황 | 이어가는 방법 |
| --- | --- |
| 최초 설치의 다운로드가 중단됨 | 실패 기록을 보존한 상태에서 새로 다운로드할 수 있습니다. |
| 이미 준비한 설치가 중단됨 | 같은 파일로 재개합니다. |
| 검증 유효기간이 지남 | 같은 배포 파일을 다시 인증하거나, 이전 런타임이 아직 선택돼 있을 때 중단된 업데이트 파일만 이전 상태로 복구합니다. |
| 최초 설치가 일부 진행된 뒤 원래 배포본을 더 이상 사용할 수 없음 | 설치 상태와 보관(quarantine) 미리보기를 확인하세요. 이 설치가 만든 것으로 확인된 파일만 따로 보관하고 기존 신뢰 정보를 유지한 채 새 배포본을 준비할 수 있습니다. 보관 도중 중단되면 같은 실행을 재개합니다. |

다른 파일로 바뀐 배포 정보나 외부에서 수정한 파일은 덮어쓰지 않습니다. 출처가 불명확하거나 외부에서 바뀐 파일은 자동 정리하지 않습니다. 보존한 파일을 지워 우회하지 마세요.

<a id="folder-confirmation" name="folder-confirmation"></a>

### macOS에서 작업 폴더를 다시 확인하라는 안내가 나올 때

해당 프로젝트와 폴더를 먼저 확인하세요. 미리보기에 표시된 프로젝트와 폴더를 백업과 대조한 뒤 확인을 적용하세요. 기존 작업 범위와 보관한 본문, 결정은 그대로 유지됩니다. 중간에 멈추면 실행 상태를 확인하고 같은 실행에서 남은 폴더만 이어서 처리하세요. 폴더를 옮기거나 교체했다면 [이동 조건](records.md#move)부터 확인하세요. 작업을 이어가려면 프로젝트의 연결 기록을 읽을 수 있는 실행기를 사용하세요.

<a id="notifications" name="notifications"></a>

## 알림 설정하기

현재 설치본의 알림 수신기를 연결하고 운영체제에서 알림을 허용하세요. 알림을 사용할 수 있는 환경에서는 알림을 눌러 해당 Work를 열고, 제출본을 읽은 뒤 수락할지 결정합니다. 알림을 누르는 것만으로 결과가 수락되지는 않습니다.

Windows에서 수신기가 업데이트됐다면 새 알림을 보내기 전에 현재 설치본에서 알림 연결을 다시 확인하세요. 전달 여부를 확인할 수 없으면 해당 알림의 기록을 남깁니다. 같은 알림을 다시 보낼지는 따로 결정합니다. 알림을 놓쳤거나 결과가 열리지 않으면 같은 프로젝트 대화에서 “검토할 결과가 있나요?”라고 물어보세요.

새 알림을 그만 받으려면 에이전트에게 “이 계정의 Colvia 알림을 꺼 주세요.”라고 요청하세요. 설치된 관리자의 `notice-disable` 명령을 사용합니다. Work의 기존 기록은 남고, 이후에도 프로젝트 대화에서 검토할 결과를 확인할 수 있습니다.

<a id="disconnect" name="disconnect"></a>

## 프로젝트 연결 해제하기

같은 프로젝트에서 “내 파일과 기록을 보존하면서 Colvia 연결만 해제하려고 해요. 변경 미리보기를 보여 주세요”라고 요청하세요. Colvia가 관리하는 연결 정보와 안내를 확인한 뒤 해제를 승인합니다. 사용자가 작성한 파일과 작업 기록은 보존합니다.

이전 작업을 나중에 이어갈 계획이라면 연결 해제 전에 [기록을 백업하세요](records.md#backup). 복원한 기록을 폴더에 연결할 때는 폴더의 정체성과 변경 내용을 확인합니다. 설치 환경을 정리하려면 아래의 [기록을 보존하는 제거 절차](#uninstall)를 사용하세요.

<a id="uninstall" name="uninstall"></a>

## 기록을 보존하면서 Colvia 제거하기

에이전트에게 “작업 기록을 보존하면서 Colvia를 제거하려고 해요. 무엇이 제거되고 무엇이 남는지 미리 보여 주세요.”라고 요청하세요. Colvia를 설치한 계정에서 필요한 접근 권한이 있으면 에이전트가 공식 설치 스크립트로 제거를 미리 볼 수 있습니다. 제거할 항목과 보존할 항목을 확인한 뒤 승인하면, 에이전트에게 제거를 이어서 맡길 수 있습니다. 프로젝트 파일, Work 기록, 승인, 제출본, 프로젝트 연결, 설정과 업데이트 신뢰 정보는 남습니다. 직접 실행하고 싶거나 앱에서 실행이 막히면 아래 명령을 사용하세요.

### 명령으로 직접 제거하기

Colvia를 설치한 표준 계정의 기본 관리 폴더에서 진행합니다. 진행 중인 Work·Git 반영·업데이트를 먼저 마무리하고 Colvia 작업 창과 알림 창을 닫으세요. [macOS ARM64](https://colvia.github.io/downloads/preview/macos-arm64/install.sh), [Windows x64](https://colvia.github.io/downloads/preview/windows-x64/install.ps1), [Windows ARM64](https://colvia.github.io/downloads/preview/windows-arm64/install.ps1) 중 내 환경에 맞는 공식 설치 스크립트를 파일로 저장하세요. 파일을 저장한 폴더에서 macOS 터미널이나 일반 Windows PowerShell을 사용하세요.

**1. 제거 범위를 미리 보세요.** 사용하지 않은 실행 ID를 고르세요. 예에서는 `remove-colvia`입니다.

macOS 터미널

```bash
/bin/sh ./install.sh --uninstall-preview remove-colvia
```

Windows PowerShell

```powershell
$path = (Resolve-Path -LiteralPath .\install.ps1).Path
$installer = [ScriptBlock]::Create([IO.File]::ReadAllText($path))
& $installer -UninstallPreview remove-colvia
```

**2. 미리보기를 확인한 뒤 제거하세요.** `RECEIPT_FROM_PREVIEW`를 미리보기의 확인값으로 바꾸세요. PowerShell에서는 앞서 사용한 창에서 이어서 실행하세요.

macOS 터미널

```bash
/bin/sh ./install.sh --uninstall remove-colvia RECEIPT_FROM_PREVIEW
```

Windows PowerShell

```powershell
& $installer -Uninstall remove-colvia -Receipt RECEIPT_FROM_PREVIEW
```

확인값은 미리보기에서 확인할 수 있습니다. 중단됐다면 같은 실행 ID와 확인값으로 macOS의 `--resume-uninstall` 또는 Windows의 `-ResumeUninstall`을 사용하세요.

Colvia는 제거한 설치 파일을 [관리 폴더](reference.md#locations)의 `operations/<실행 ID>/retired/`에 옮겨 보관합니다. 중단된 제거를 되돌릴 때 이 파일을 사용하며, 보관하는 동안에는 디스크 공간을 계속 사용합니다.

**3. 필요할 때 다시 설치하세요.** 같은 계정에서 평소 설치 명령을 실행하세요. 같은 프로젝트를 열고 이전 Work와 제출본을 확인할 수 있습니다. 재설치가 중단되어 재개 안내가 뜨면 저장한 스크립트의 macOS `--resume-reinstall` 또는 Windows `-ResumeReinstall` 옵션으로 이어가세요. 복구할 수 있도록 기록과 관리 폴더 전체를 보존하세요.

제거가 중단되고 아직 재설치를 시작하기 전이라면, Windows에서는 `-RestoreUninstall <실행 ID> -Receipt <확인값>`, macOS에서는 `--restore-uninstall <실행 ID> <확인값>`으로 설치 파일을 원래 위치에 복구하세요. Windows 알림을 사용했다면 제거를 되돌리거나 재설치한 뒤 다시 켜세요.

---

다음 · [지원 환경과 참고 자료](reference.md) · [구조가 궁금하다면 · 설치와 업데이트](architecture.md#install-update)
