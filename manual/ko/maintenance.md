# 업데이트, 알림, 연결 해제와 제거

[사용 설명서](README.md) · 한국어 · [English](../en/maintenance.md)

설치한 뒤에 필요한 운영 절차입니다. 범위가 서로 다르니 먼저 무엇을 하려는지 확인하세요.

| 하려는 일 | 영향 범위 | 남는 것 |
| --- | --- | --- |
| [업데이트](#update) | 이 계정의 Colvia 설치본 | 이 설치본에 연결한 프로젝트의 기록과 연결 정보 |
| [알림 켜기·끄기](#notifications) | 이 계정의 알림 수신 | Work의 기존 기록 |
| [프로젝트 연결 해제](#disconnect) | 프로젝트 하나 | 사용자가 작성한 파일과 작업 기록 |
| [Colvia 제거](#uninstall) | 이 계정의 설치본 | 프로젝트 파일, Work 기록, 승인, 제출본, 프로젝트 연결, 설정, 업데이트 신뢰 정보 |
| [기록까지 완전히 삭제하기](#remove-all) | 이 계정에서 연결했던 모든 프로젝트 | 사용자 프로젝트 파일과 별도 위치에 보관한 사본 |

<a id="update" name="update"></a>

## 업데이트

업데이트하면 기존 Work가 유지됩니다. 사용을 끝내려면 [기록 보존 제거](#uninstall) 또는 [기록까지 완전 제거](#remove-all)를 선택하세요.

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

**1. 제거 범위를 미리 보세요.** 관리 폴더의 `operations/` 아래에 같은 이름의 폴더가 없는 실행 ID를 고르세요. 예에서는 `remove-colvia`입니다.

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

<a id="remove-all" name="remove-all"></a>

## 이 계정에서 Colvia와 작업 기록을 완전히 제거하기

에이전트에게 “Colvia를 완전 제거해 줘. 지울 목록부터 보여 줘”라고 요청하세요. 보관할 Work가 있으면 먼저 [계정 관리 폴더 밖으로 내보내세요](records.md#backup). 미리보기에서 연결 폴더별 관리 파일, 지워질 Work의 상태별 건수, 내장 백업과 설치 파일을 확인하세요. 이동했거나 열 수 없는 폴더는 다시 연결해 확인하거나 이번 정리에서 제외할 수 있습니다. 제외한 폴더와 공용 Git 폴더에는 연결 흔적이 남을 수 있습니다.

위 제거 안내에 따라 공식 설치 스크립트를 저장하고 **설치한 계정에서** 미리보기를 실행하세요. Windows에서는 위와 같이 스크립트를 `$installer`에 불러오세요.

| 단계 | macOS 터미널 | Windows PowerShell |
| --- | --- | --- |
| 미리보기 | `/bin/sh ./install.sh --purge-preview remove-all` | `& $installer -PurgePreview remove-all` |
| 목록을 승인한 뒤 적용 | `/bin/sh ./install.sh --purge remove-all RECEIPT` | `& $installer -Purge remove-all -Receipt RECEIPT` |
| 중단된 제거 이어가기 | `/bin/sh ./install.sh --resume-purge remove-all RECEIPT` | `& $installer -ResumePurge remove-all -Receipt RECEIPT` |

미확인 폴더를 모두 제외하려면 미리보기와 적용 명령 끝에 macOS는 `--exclude-unavailable`, Windows는 `-ExcludeUnavailable`을 붙이세요. 지울 항목과 제외한 폴더를 확인한 뒤 한 번 승인하고, `RECEIPT` 자리에 그 미리보기의 확인값을 쓰세요. 연결된 프로젝트에서는 Colvia가 넣은 항목부터 정리합니다. 사용자 파일과 Git 스테이징은 보존하고, 계정 DB와 내장 백업은 마지막에 지웁니다.

사용 중이면 쓰기 작업을 마친 뒤 진행하세요. 중단되면 실행 ID와 확인값을 보관하고 같은 작업을 재개하세요. 소유권이나 파일 변경 때문에 멈췄다면 오류와 남은 경로를 확인하세요. 제거 뒤에는 제외한 폴더와 설치 도구가 표시한 준비 폴더도 확인하세요. 이전 설치기의 준비 폴더는 아래 수동 안내의 마지막 단계에서 확인할 수 있습니다.

제외한 폴더의 파일은 남지만 이 계정에 보관한 해당 Work 기록은 다른 기록과 함께 지워집니다. 쓰기 잠금이 계속되면 Colvia로 작업 중인 앱을 닫으세요. `remove-all`은 예시 실행 ID입니다. 승인 전에 이미 사용한 이름이면 새 이름으로 미리보기를 여세요. 제거가 시작된 뒤에는 처음 승인한 이름과 확인값으로 재개하세요. 관리 파일이 중간에 바뀌었다면 편집본을 별도로 보관하고 승인 당시 내용과 위치를 복구한 뒤 재개하세요. 복구할 수 없으면 작업을 멈추고 남은 파일과 제거 기록을 보존하세요.

이미 기록 보존 제거를 마쳤다면 미리보기에 `records-retained-after-uninstall`이 표시됩니다. 아래 수동 절차에서 이미 끝낸 단계를 확인하고 남은 자료를 정리하세요. 미리보기의 `retained_preparation_paths`에 나온 이전 설치 준비 폴더도 마지막 단계에서 확인하세요.

### 구버전 설치기로 수동 정리하기

일반 제거는 다시 설치했을 때 Work를 이어갈 수 있도록 기록을 남깁니다. **이 계정에서 모든 프로젝트의 Work·승인·제출본과 복구 자료까지 버릴 때만** 아래 절차를 따르세요. 일부 프로젝트를 계속 쓴다면 [그만 쓸 프로젝트만 연결 해제](#disconnect)하세요.

1. **연결했던 프로젝트를 먼저 확인하세요.** 현재 모든 연결 경로를 한 번에 열거하는 명령은 없습니다. 관리자의 `status` 숫자에는 연결을 해제하고 남긴 기록도 포함될 수 있습니다. 일반 폴더에서는 숨김 파일 `.colvia-link.json`을 확인하세요. Git 프로젝트에서는 `git rev-parse --path-format=absolute --git-common-dir`이 알려 주는 공용 폴더 안의 `colvia/connection.json`을 확인하세요. 두 파일 모두 확인용입니다. 직접 지우지 마세요. 연결했던 폴더를 모두 확인하기 어렵거나 원래 연결한 작업 폴더가 사라졌다면 기록 보존 제거까지만 진행하세요.
2. 보관할 Work는 [기록 내보내기](records.md#backup)로 **삭제할 폴더 밖에** 저장하고, 내보내기가 완료됐는지와 저장한 파일의 위치를 확인하세요. 프로젝트 파일은 따로 보관하세요. 각 프로젝트의 원래 연결 폴더에서 에이전트에게 “Colvia가 추가한 항목을 미리 보여 주세요. 승인하면 연결을 해제하고 완료 상태를 확인해 주세요”라고 요청하세요. 여러 Git worktree가 있으면 처음 연결한 worktree에서 진행합니다. 프로젝트마다 [연결 해제](#disconnect) 결과가 `detached`인지 확인하세요. 에이전트는 관리자의 `--json` 출력에서 `state`를 볼 수 있습니다. `pending`이나 오류가 나오면 멈추세요. 프로젝트 파일, 직접 쓴 안내, Git 이력과 스테이징은 남습니다.
3. 알림을 켰다면 [알림을 끄세요](#notifications). 진행 중인 작업을 마치고 Colvia를 사용하는 창과 프로세스를 닫은 뒤, [일반 제거](#uninstall)의 **1·2단계까지만** 실행하세요. 이번 실행 ID에 대해 `"state": "removed"`와 `"records_preserved": true`가 나왔는지 확인하세요. 중단·오류·복구 중이거나 사용자 지정 경로에 설치했다면 관리 폴더를 보존하세요.
4. 아래 명령은 **기본 관리 폴더를 선택해 보여 줍니다**. 그 안에는 모든 프로젝트의 SQLite 기록, 내장 백업, 업데이트 신뢰 정보, 제거 복구 파일이 있습니다. 내용을 열어 개인 파일이 섞여 있지 않은지 확인한 뒤 **같은 명령을 다시 실행**하세요. 선택된 항목의 이름이 `Colvia`이고 경로가 [내 계정의 기본 관리 폴더](reference.md#locations)와 일치할 때만 일반 휴지통으로 옮기세요. 선택된 항목이 보이지 않거나 링크·정션이거나 즉시 영구 삭제하겠다는 대화상자가 뜨면 취소하세요. Windows에서는 Shift+Delete를 사용하지 마세요.

   macOS 터미널

   ```bash
   folder="$HOME/Library/Application Support/Colvia"
   if [ -d "$folder" ] && [ ! -L "$folder" ]; then open -R "$folder"; else echo "기본 Colvia 폴더를 확인할 수 없습니다."; fi
   ```

   Windows PowerShell

   ```powershell
   $folder = Join-Path ([Environment]::GetFolderPath('LocalApplicationData')) 'Colvia'
   $item = Get-Item -LiteralPath $folder -Force -ErrorAction SilentlyContinue
   if ($item -and $item.PSIsContainer -and -not ($item.Attributes -band [IO.FileAttributes]::ReparsePoint)) { Start-Process explorer.exe -ArgumentList ('/select,"' + $folder + '"') } else { Write-Warning 'Colvia 폴더를 찾을 수 없습니다.' }
   ```

5. 설치 출력의 `Recovery files:` 뒤에 나온 **정확한 경로**와 일치하는 `Colvia-bootstrap-…` 폴더만 개별적으로 휴지통에 옮기세요. 설치 로그가 없거나 출처가 불확실하면 그 폴더는 남겨 두세요. 2단계에서 보관한 내보내기 파일과 개인 백업은 삭제 대상에서 제외하세요.
6. 기본 위치에서 `Colvia` 폴더가 사라졌고 프로젝트 파일과 보관할 백업이 남았는지 확인하세요. 영구 삭제하려면 휴지통에서 방금 옮긴 항목만 삭제 날짜로 구분하세요. Windows에서는 원래 위치도 확인하세요. 이 단계부터 해당 기록과 복구 파일은 휴지통에서 되살릴 수 없습니다. OS 알림과 권한, 사용자가 설정한 앱 접근 권한·PATH, Git 이력, Time Machine 등 시스템 백업과 동기화 사본은 별도로 남을 수 있습니다.

---

다음 · [지원 환경과 참고 자료](reference.md) · [구조가 궁금하다면 · 설치와 업데이트](architecture.md#install-update)
