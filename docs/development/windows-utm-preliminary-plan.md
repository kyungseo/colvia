# Windows UTM Preliminary Plan

Date: 2026-10-17
State: R0 completed — request-changes; Driver disposition recorded; product implementation and contract acceptance pending
Source baseline: `a93f71c359c4f0a9d57fcfb50d5999160e870f77`

2026-10-17 후속 승인과 결과: Owner가 승인한 제품 외부 격리 probe 1회의 관측·원출력 검증·계약 변경안은 [CHORE-20261017-001](CHORE-20261017-001-windows-utm-feasibility-probe.md)에 기록했다. 해당 record가 후속 진행 정본이며, 이 문서의 아래 계획·R0·Driver 처분·Owner 미결 표기는 당시 상태로 보존한다. 후속 R1-P01과 Driver 판단도 같은 record에 연결했다. Owner 결과/계약 수락, 제품 구현·공개 admission은 아직 없다.

## Recommendation

Windows 11 공통 지원과 실제 검증 환경을 별도로 표시하는 B안을 우선 권고한다. UTM의 대표 guest에서 필요한 전체 검증을 먼저 수행하고 x64·물리 PC 확인은 후속 보완으로 둔다. 이는 아직 수락되지 않은 정책안이다. 현재 제품은 Python 표준 라이브러리와 Git subprocess를 사용하지만, 파일 잠금·경로 검사·권한·동기화·런처는 POSIX 가정에 의존한다. Windows 지원은 import 몇 곳을 조건부 처리하는 작업으로 끝나지 않는다. 파일 안전성 계약과 배포 inventory를 먼저 정하고 그 경계를 구현해야 한다.

이번 결과는 구현 전 계획과 변경 전 Windows 진단이다. Owner의 이미지 준비 완료 통지와 복제 VM 설정 승인 후, 실제 ARM64 guest에서 현재 source의 `fcntl` import 실패와 native 진입 실패를 관측했다. 이 결과는 Windows 지원 성공이 아니다. source 조사, 제한된 실행, 외부 API 문서 근거, 앞으로 할 시험을 구분한다.

```text
현재 완료: source/호스트 조사 + guest baseline + R0/Driver 처분
  → 별도 승인된 제품 외부 격리 실험 → 결과로 필요한 계약 amendment 확정·수락
  → 제품 구현 실행 승인
  → Windows 이식/검증 + macOS 회귀 → R1 + 결과 수락
  → live macOS Preview 이후 별도의 Windows 정식 admission 판정
```

위 순서의 제품 구현/qualification은 필요한 amendment와 실행 계획 수락 후에만 가능하다. 제품 source를 바꾸지 않는 격리 feasibility probe는 최종 기술 계약 수락을 선행 조건으로 만들지 않는 timing 문안을 아래에 제안한다. 어느 probe도 이번 리뷰 승인만으로 실행하지 않는다.

## Authority And Scope

기준은 [Contributing](../../CONTRIBUTING.md), [Source Workflow](WORKFLOW.md), [Windows Admission](README.md#windows-admission), [Decision Guide](../DECISION-GUIDE.md), [Maintaining](../MAINTAINING.md)이다. DR-0006의 2026-10-16 수락·발효로 source workflow와 decision guide의 재배치가 유효하다. 기술 계약은 DR-0004의 entry-1 활성화 및 First B1 supplement를 따른다. 문서에 남은 candidate 표기를 현재 미발효라는 근거로 사용하지 않는다.

Owner는 환경 조사, 현재 source baseline 진단, 구체적인 이식 계획과 R0 입력 준비를 승인했다. UTM 직접 조사를 이미지 준비까지 유예한 뒤, 준비 완료를 알리고 복제 VM에서 필요한 설정을 진행하도록 승인했다. 그 범위에서 전달용 공유 폴더와 task-owned NTFS 경로를 준비하고 공식 CPython 3.14.7 ARM64를 사용자 범위에 설치했다. 앞서 별도 승인으로 호스트 pyenv 전역 기본값도 `system`에서 기존 `3.14.7`로 바꿨다. 이 승인들은 제품 구현·지원 정책 수락으로 확대하지 않는다.

이 문서가 이번 준비의 단일 source-owned 진행 정본이다. 정식 개발 record ID나 runtime Work/intent는 만들지 않는다. 기존 Windows 후보를 중복 등록하거나 Development Index의 수락된 criteria를 수정하지 않는다. 이후 Owner가 실제 Windows 관측을 반영한 R0의 Claude CLI 검토와 Driver 판단 정리를 명시적으로 승인하여 해당 정적 리뷰 1회를 완료했다. 제품 구현, probe 실행, 계약 수락·활성화, commit/push/PR/merge, 공개 지원 승격, 실제 adopter 적용은 승인되지 않았다. 기존 다른 작업의 checkout·미커밋 변경·리뷰·프로세스는 가져오거나 조작하지 않는다.

## Fixed Inputs And Observations

| 항목 | 이번에 관측한 사실 | 의미와 제한 |
| --- | --- | --- |
| 원격 main / open PR | 위 baseline commit / 조회 시 0개; fetch 완료 | 이 시점의 조회이며 다음 통합 때 재확인 |
| 전용 checkout | baseline에서 새 branch/worktree 생성 | 기존 primary의 미추적 파일을 복사하지 않음 |
| shipped 실행 코드 조사 | `colvia`와 `src/hv2ref/*.py` 11개, 총 12개 파일 AST 분석 | 제품 import/실행 없이 분석; 자체 native binary/extension 또는 CPU 분기 미관측 |
| 전체 추적 파일 조사 | `.exe/.dll/.pyd/.so/.dylib/.cmd/.bat/.ps1` 파일 없음 | 미래 Windows 구현의 native API/패키징 위험이 없다는 뜻은 아님 |
| 테스트 정적 조사 | top-level class에 선언된 `test_*` method 609개 | 실행 discovery 수가 아님. factory·상속·동적 suite를 포함한 완전성 근거로 쓰지 않음 |
| 호스트 | macOS 27.0.1 / build 26A434 / arm64; Git 2.54.0 (Apple Git-157) | Windows 환경의 대용이 아님 |
| 호스트 Python 정정 | Homebrew `python@3.14`는 3.14.8, 초기 전역 `system`은 3.15.0; pyenv 3.14.7은 이미 설치되어 있었음 | primary의 `.python-version`은 3.14.7. 이후 Owner 요청으로 전역도 3.14.7로 변경 |
| 선택된 호스트 interpreter | final CPython 3.14.7, `Py_GIL_DISABLED=0`; 실행 파일 digest 별도 보존 | 버전 gate 조건 충족. 이 pyenv build의 완전한 제품 qualification은 주장하지 않음 |
| 호스트 실행 | 명시한 3.14.7로 `-I -B colvia --source-checkout --help`, exit 0 | source help만 확인. lifecycle, Windows, 전체 회귀 실행 아님 |
| Windows 실제 baseline | ARM64 guest의 `import fcntl`과 explicit Python source help 모두 exit 1, `ModuleNotFoundError` | 기준 source 그대로 관측. 제품 수정·monkeypatch 없음 |
| Windows native entry | 직접 CreateProcess는 WinError 193; `cmd /d /c`는 exit 1, 명령 인식 실패 | `Get-Command`가 파일을 찾는 것과 실행 가능성을 구별 |
| 기존 PASS 재사용 | 없음 | 과거 424-ID 또는 다른 build 결과를 이번 candidate PASS로 가져오지 않음 |

정적 진단 도구 자체는 처음에 호스트 3.14.8로 실행했으며 제품을 import하지 않았다. 그 기록은 유효한 정적 관측으로 보존한다. Python 경로 혼동을 숨기거나 Windows 실패로 바꾸어 쓰지 않는다.

## Guest Environment And Remaining Qualification

2026-10-17에 다음 실제 값을 기록했다. 아래 확인 기준은 후속 qualification에도 유지한다.

| 관측 항목 | 실제 값 | 제한 |
| --- | --- | --- |
| UTM / Windows | UTM 4.7.5; Windows 11 Pro 26H2, 10.0.26300.9711, ARM64 | 한 복제 VM의 재현 기록이며 지원 build allowlist가 아님 |
| shell / cmd | Windows PowerShell 5.1.26100.9711, Desktop, ARM64; cmd 10.0.26300.9711 | Git Bash/WSL 우회 없음 |
| CPython | 공식 3.14.7 final, 64-bit ARM64, PE `0xaa64`, `win-arm64`, `Py_GIL_DISABLED=0` | 버전 gate 적합; 제품 qualification 아님 |
| Git | 2.56.0.windows.2; 관측한 `git.exe` PE `0xaa64` | Git의 모든 내부 child binary를 별도로 검증한 것은 아님 |
| 계정 / 경로 | 실행 token 비승격·비SYSTEM, token group 목록에 Administrators SID 미관측; C: fixed NTFS | 전용 무자격증명 계정·network/filesystem 격리 qualification은 미완료 |
| source | 기준 commit의 독립 clone, 198개 tracked blob 전부 SHA-256 일치, 실행 전후 clean | 설치 제품이나 다른 branch를 검증하지 않음 |
| Git checkout | 새 clone의 `core.autocrlf=false`, `core.filemode=false`, `core.symlinks=false`, `core.eol` unset; `check-attr --source=HEAD` exit 0 | 기존/global Git 설정을 바꾸지 않음; CRLF 변형 시험은 미실행 |

Python 설치 파일은 공식 release SHA-256과 Windows Authenticode의 Python Software Foundation 서명 `Valid`를 확인했고 installer exit 0였다. [Python 3.14.7 공식 배포](https://www.python.org/downloads/release/python-3147/)의 ARM64 installer에는 Experimental 표기가 있다. 이 배포 표기는 기록하되 제품의 공통 지원 정책을 자동 결정하지 않는다.

작업용 source와 입력·출력은 존재하지 않음을 확인한 guest 내부 경로에 만들었고 ancestor의 reparse 여부를 검사했다. 공유 폴더는 전달용이며 제품 실행 cwd와 log 원본은 C: NTFS였다. 이 단순 경로 검사는 race-safe 제품 confinement 또는 VM 전체의 보안 격리 증명이 아니다.

| 확인 항목 | 필요한 증거 | 통과하지 못하면 |
| --- | --- | --- |
| Windows | edition, DisplayVersion, CurrentBuildNumber, UBR, OS architecture | 재현용 tuple을 확정하고 실제 시험 범위를 표시. 기록한 build와 다른 값을 자동 실행 거절 조건으로 만들지 않음 |
| CPU와 runtime | guest OS architecture, PowerShell process architecture, Python/Git executable architecture; emulation 여부 | ARM guest의 x64 process를 native x64 PC 검증으로 표시하지 않음 |
| 사용자 | 실행 token의 비승격 여부와 일반 사용자 계정 조건; 개인 식별 경로는 private evidence에만 보존 | admin token만 있으면 일반 사용자 시험 전 provision 필요 |
| 파일시스템 | guest 내부 고정 드라이브 NTFS, source/fixture/log root의 reparse·junction·공유·동기화 여부 | Mac 공유폴더/UNC/cloud sync를 기본 fixture 경로로 사용하지 않음 |
| shell | Windows PowerShell 또는 PowerShell의 정확한 edition/version 및 cmd | Git Bash/WSL로 성공을 우회하지 않음 |
| Git | 버전/실행 파일/digest, `check-attr --source` 기능, autocrlf/eol/filemode/core.symlinks와 실제 bytes | 버전 숫자만으로 필요한 capability를 추정하지 않음 |
| CPython | final GIL-enabled 3.14.6 또는 3.14.7; distributor, executable digest, bitness/architecture, child identity | 3.14.8·3.15·prerelease·free-threaded를 동등한 것으로 취급하지 않음 |
| 검증 경계 | task-owned NTFS 경로, credential 없는 합성 target, 실행/쓰기/network 제한 | 격리 검증 전 mutating lifecycle/test suite 실행 금지 |

이번 설정 승인으로 복제 VM의 공유 폴더를 전용 전달 폴더로 지정했다. 기준 source는 호스트에서 만든 Git bundle로 전달했으며 인증값을 복제하지 않았다. 입력 manifest와 파일 digest를 확인하고 guest NTFS의 독립 clone에서 실행했다. QEMU guest agent 호출은 agent 미연결로 사용할 수 없어 화면의 비승격 PowerShell과 공유 파일 전달을 사용했다. 새로운 guest agent 설치나 OS 보안 정책 변경은 수행하지 않았다. mutating suite에 필요한 전용 계정·실행 격리는 후속 계획에서 별도로 확정한다.

## Baseline Diagnosis

실제 baseline에서 `import fcntl`은 exit 1이었다. source help도 `colvia:110` → `cli.py:10` → `jsonio.py:4`에서 같은 `ModuleNotFoundError`로 종료했다. 두 child 모두 15초 제한 안에 끝났고, 기록된 두 명령의 전체 실행 구간은 약 1.46초다. native 직접 실행은 WinError 193, cmd 진입은 exit 1이었다. 아래 표의 나머지는 여전히 정적 위험 또는 후속 검증 가설이다.

| 관측 지점 | 정적 사실 / 예상 영향 | Windows baseline에서 확인할 것 |
| --- | --- | --- |
| `jsonio.py:4,149–183` | unconditional `import fcntl`, `flock` 사용. CPython 문서의 fcntl은 Unix 전용 | exact 3.14.7에서 import와 source help 모두 동일한 import 실패 재현; CLI parser/doctor 이전 실패 |
| `view.py:83–108`, `candidates.py:148–175` | `O_DIRECTORY/O_NOFOLLOW/O_NONBLOCK`, descriptor-relative open/stat/listdir | import 해결 뒤 별도 이식 시험. 현재 import 실패를 넘기려고 monkeypatch하지 않음 |
| `product.py:420–438,697–740` | umask, exact 0600 prefix, 0755 final launcher, fchmod | Windows ACL/실행 권한이 이 조건과 어떻게 대응하는지 확인. fchmod 함수의 존재 자체는 Windows 3.13+에서 지원되므로 ‘API 없음’으로 오진하지 않음 |
| `jsonio.py:100–126`, `product.py:563–620` | file fsync, directory open/fsync, D3의 non-pass 거절, read-only handle fsync도 존재 | 파일 flush / directory flush / 교체 성공을 각각 관측; 하나로 PASS를 합성하지 않음 |
| `product.py` switch/repair, `work.py` publication | os.replace, file identity, mode 증명 | 열린 destination handle·read-only attribute·ACL 거절·중단 후 exact retry |
| `work.py:45–78,104–130` | NFC·case alias는 거절하지만 reserved device/ADS/trailing dot-space 검사는 없음; mode는 stat 실행 bit에서 유도 | `CON`, `NUL.txt`, `COM¹`, `a:stream`, `a.`, `a `, case alias, Unicode, Git executable mode |
| `colvia` | Unix shebang, extension 없는 entry, fixed 11-module bootstrap allowlist | 직접 CreateProcess WinError 193 및 cmd exit 1 재현; PowerShell의 `Get-Command` 탐색 성공을 launcher 성공으로 취급하지 않음 |
| tests / verification controls | fcntl, SIGKILL 값, POSIX mode, Seatbelt 전제 및 explicit suite factory 존재 | Windows counterpart oracle/runner 필요. broad skip, signal 기대값 삭제, factory 누락을 PASS로 취급하지 않음 |
| checkout/inventory | raw-byte digest와 한정된 unchanged-CRLF 예외 | source payload CRLF 변환과 사용자 project CRLF 예외를 혼동하지 않음 |

공식 문서 근거: [fcntl](https://docs.python.org/3.14/library/fcntl.html), [os platform support](https://docs.python.org/3.14/library/os.html). 조회일은 2026-10-17이며 rolling 3.14 문서가 3.14.8을 표시한다. 이는 API 설계 참고이며 허용 patch 확대나 exact 3.14.7 실행 증거가 아니다.

제품 baseline은 source identity와 bytes 확인 후 exact Python import/help, 이어 native entry를 관측했다. child당 15초 제한을 지켰고 timeout은 없었다. 초기 runbook의 전체 진단 10분 예상 경계는 UI 입력·전달 준비까지 합하면 초과했다. 이를 전체 10분 내 완료로 보고하지 않는다. 후속 실행에서는 환경 준비 예산과 제품 진단 예산을 시작 전에 분리해야 한다. 예상 import 실패를 그대로 보존했으며 lifecycle writer, 전체 suite 또는 실패를 우회하는 monkeypatch는 실행하지 않았다.

## Minimal Port Design

### Platform Boundary

제품 record/intent/acceptance 알고리즘을 OS별로 복제하지 않는다. 파일 잠금, 안전한 open/read, 파일 발행/replace, flush, 파일 identity/권한 관측만 좁은 내부 경계로 묶는다. 현 POSIX 구현의 의미를 보존하고 Windows 구현은 조건부로 불러온다. 새 helper는 하나의 내부 module을 우선 검토하되, bootstrap 이전에 검증하지 않은 helper를 import하지 않는다. stdlib `ctypes`로 documented Win32 API를 사용하는 안을 우선 비교하며 외부 dependency/native build 추가는 기본안에 포함하지 않는다.

새 module을 추가하면 launcher의 검증 대상과 exact inventory도 바뀐다. 문서상 설계 후보일 뿐 현재 module allowlist를 수정하지 않았다. bootstrap에는 payload 검증 이전에 필요한 최소 stdlib-only 경로 검사를 유지해야 한다.

### Lock And Safe Paths

stable lock anchor의 동일성과 단일 cooperating writer를 유지한다. Windows 후보는 `CreateFileW` handle과 `LockFileEx/UnlockFileEx`의 고정 byte range다. 상속 금지, acquire/unlock, 비정상 종료 후 재획득, 같은 process 재진입 및 기존 thread guard를 검증한다. 기다림/timeout은 기존 계약과 비교하고 임의의 10초 실패를 새 의미로 넣지 않는다. `msvcrt.locking(LK_LOCK)`은 1초 간격 10회 재시도하므로 단순 치환안에서 제외하는 것이 적절하다. [LockFileEx](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-lockfileex), [msvcrt.locking](https://docs.python.org/3.14/library/msvcrt.html).

모든 경로 component의 실제 spelling, type, reparse tag와 handle identity를 검사한다. leaf에서만 `FILE_FLAG_OPEN_REPARSE_POINT`를 사용하는 것으로 ancestor junction race까지 해결됐다고 보지 않는다. ancestor handles를 유지하며 delete/rename 공유 제한과 재검사를 조합하는 설계를 spike에서 입증한다. 입증되지 않으면 mutation을 거절하고 계약을 재검토한다. arbitrary same-account attacker에 대한 새 보장은 만들지 않되, 기존 링크/외부 파일 읽기·쓰기 거절 조건은 약화하지 않는다. [CreateFileW](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-createfilew).

case-sensitive NTFS directory, 8.3 alias, drive-relative/UNC/device namespace, hardlink와 unknown reparse tag를 포함한다. 기본 지원은 검증한 local NTFS로 한정하고 unsupported 경로를 자동 정규화하거나 경로 밖으로 해석하지 않는다. [Windows naming](https://learn.microsoft.com/en-us/windows/win32/fileio/naming-a-file).

### Publication, Durability And Permissions

immutable `CREATE_NEW`와 staged same-volume replacement를 구분한다. `os.replace`를 우선 평가하고 Win32 직접 호출이 필요한 경우에만 좁힌다. replace failure는 source/destination/binding 관측을 남기고 exact retry 또는 stable refusal로 끝내며 delete-then-copy fallback을 넣지 않는다. 열린 handle, ACL, read-only attribute와 antivirus 경합을 시험한다. `ReplaceFileW`의 WRITE_THROUGH flag는 지원되지 않으므로 flush 대용으로 쓰지 않는다. [ReplaceFileW](https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-replacefilew).

파일 flush, directory metadata 관측, atomic replace, process termination recovery, power-loss persistence를 별개로 기록한다. `FlushFileBuffers`의 handle access 조건과 실제 NTFS 결과를 먼저 측정한다. 공통 `sync_directory`는 lock 획득 전과 일반 publication에서도 쓰인다. 이 공통 결과 분류와 checkout-1→entry-1 전환 전용 D3를 분리한다. Windows에서 그 과거 전환을 지원하지 않는 범위안을 우선 비교하되, 기존 macOS D3 거절은 그대로 둔다. directory sync를 구현하기 어렵다고 `pass`를 반환하거나 NTFS라는 이유만으로 의무를 자동 면제해서는 안 된다. 표준 사용자에서 기존 의미를 충족할 수 없다면 명시적인 Windows durability 계약을 새로 수락하고 inventory/window 및 old-writer fencing에 반영해야 한다. [FlushFileBuffers](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-flushfilebuffers).

POSIX 0600/0755와 Windows read-only bit/ACL을 동등하다고 보지 않는다. 0600/0755는 기존 전환의 부분/완성 상태 표식이기도 하다. 그 전환을 제외할 경우 도달하지 않는 상태기계를 Windows에 자동 복제하지 않는다. 새 Windows 발행에 필요한 완성 상태 표식은 staging 이름과 검증된 rename을 우선 비교하고 spike로 확인한다. 권한은 상속 ACL 유지와 새 기밀성 주장 없음이 우선안이며, private DACL을 새 요구로 넣으려면 별도 이유와 계약이 필요하다. 임의로 권한을 넓히거나 machine-wide ACL을 바꾸지 않는다. Git 100644/100755 의미도 Windows stat로 다시 만들어서는 안 된다. tracked mode와 manifest 원뜻을 보존하고 실행 bit 변경을 표현할 수 없는 경우 명시적으로 거절한다. standalone non-Git mode 표현은 amendment 검토 항목이다.

### Launcher, Inventory And Compatibility

R0 이후에는 명시적 Python 진입과 제한된 `.cmd` shim을 비교하며, 전자를 최초 경로의 우선 권고로 둔다. `"<python.exe>" -I -B colvia ...`가 기존 native-launcher 요구를 충족하는지는 Owner가 결정해야 한다. `.cmd`의 실행 중 자기 교체·삭제와 shell 인자 재해석을 별도로 검증하기 전에는 shim을 확정하지 않는다. 경로·Unicode·임의 인자를 편의상 조용히 축소하는 안은 채택하지 않는다. PowerShell에서도 `.cmd`를 실행할 수 있으므로 추가 `.ps1`과 execution-policy 변경을 기본 요구로 만들지 않는다. 정확한 supported interpreter 선택, `-I -B`, argv/Unicode/공백/`&|()%!^` 인자, stdin JSON, stdout/stderr/exit code, CWD 독립 실행, source/installed 진입 구별을 시험한다. arbitrary Python이 먼저 잡히면 명확하게 거절해야 한다.

managed launcher 추가, module 추가, 권한·sync·receipt 해석 변경을 entry-1에 조용히 넣지 않는다. 기존 reader의 exact membership와 양방향 의미 호환을 만족하는지 검토하고, 현재 예상으로는 명시적인 successor inventory window가 필요하다. window 이름·schema version은 아직 배정하지 않는다. literal old inventory, old reader의 safe refusal, new records를 읽을 수 없는 old writer 차단, update/rollback/repair/detach prefix를 설계에 포함한다. Windows 첫 설치는 fresh target이며 macOS workspace를 Windows로 옮기는 기능은 이번 범위가 아니다.

## Affected Files

| 범위 | 예상 영향 |
| --- | --- |
| `src/hv2ref/jsonio.py`, 새 내부 platform helper 후보 | conditional imports, lock/open/sync/replace primitives |
| `workspace.py`, `work.py` | 경로·topology·file identity·Git mode·publication |
| `product.py`, `colvia`, native launcher 후보 | 권한과 D3, installed bootstrap, inventory, transition/repair/detach |
| `view.py`, `candidates.py` | no-follow bounded reader; byte/size/link/race 조건 보존 |
| `cli.py`, `PRODUCT-CAPABILITIES.json` | unsupported runtime/OS capability 진단과 help, 실제 지원과 검증 tuple 표시 |
| tests 및 독립 auditor/runner | Windows process/handle/reparse counterpart, discovery와 isolation, old window 호환 |
| `WORKSPACE-CONTRACT`, `SECURITY-AND-SUPPORT`, `OPERATIONS`, `GETTING-STARTED`, `REFERENCE`, `MAINTAINING` 및 entry/adapter 관련 설명 | 실제 설계로 영향을 받는 clauses만 amendment·문서 동시 정렬 |
| source-only development/decision 자료 | 선택 후 record, 필요한 amendment, 입력/결과/한계 |

runtime module 전역 refactor, schema 재설계, 새 scheduler, optional provider, Enterprise 기능은 포함하지 않는다. 위 목록은 영향 분석이며 파일 수정 승인 목록이 아니다.

## Architecture And Support Policy

### Preferred Proposal And Admission Basis

B안인 Windows 11 공통 지원 + 실제 검증 환경 별도 표기를 우선 검토·권고한다. 이는 2026-10-17 Owner의 계획 보완 요청을 반영한 제안이며 정책 수락·활성화나 지원 선언이 아니다. 현행 exact-architecture 기준을 변경하는 amendment와 잔여 위험을 R0에서 함께 검토한 뒤 Owner가 별도로 결정한다.

| 안 | 제안하는 지원 정책 | 실제 검증의 표시 | 판단 |
| --- | --- | --- | --- |
| B — 우선 권고 | Windows 11 ARM64/x64에 공통 정책 적용; 아래 명시적 runtime·filesystem·기능 조건을 충족하는 환경 | UTM 대표 환경의 exact tuple과 실제 실행 결과를 표시. x64·물리 PC 등 미실측 환경은 미검증으로 남김 | 대표 환경의 전체 검증과 구현 위험 분석으로 최초 admission을 판단하는 안. 필요한 amendment와 잔여 위험 수락 전에는 효력 없음 |
| A — 비교 대안 | qualified exact tuple에만 지원을 한정 | 해당 tuple 이외는 미검증 | 현행 기준을 그대로 유지하는 대안. B의 안전 조건을 충족할 수 없다는 구체적 근거가 생기면 Owner가 재검토하며 자동 전환하지 않음 |

목표는 UTM의 대표 Windows 11 환경 하나에서 필요한 complete normal/parent-optimized regression, explicit factory·lifecycle·중단/복구 검증과 관련 macOS 회귀를 수행하는 것이다. guest architecture는 준비 후 실제 확인해 기록한다. 아키텍처마다 전체 suite를 복제하거나 물리 PC 확보를 최초 지원 판정의 필수 조건으로 자동 추가하지 않는다. x64 실행과 물리 PC 관측은 후속 보완이다. 대표 guest가 ARM64라면 그 안의 x64 emulation 결과도 native x64 PC 결과와 구분한다.

B가 수락되더라도 제품의 지원 범위와 실행 증거의 범위는 다르다. 최초 admission은 수락된 대표 환경 증거·구현 분석·알려진 결함 처분·잔여 위험에 근거한다. 실행하지 않은 환경에 PASS나 exact-environment qualification을 부여하지 않는다. 반대로 아직 시험하지 않았다는 사실만으로 B의 제안된 지원 범위에서 그 환경을 자동 제외하지 않는다. 알려진 integrity 결함은 단순한 미검증 불확실성으로 덮을 수 없다.

### Reproduction Record, Support Conditions And Refusal

| 구분 | 기록하거나 제안하는 내용 | 제품에서의 의미 |
| --- | --- | --- |
| 재현용 환경 기록 | Windows edition/build/UBR, guest·process architecture와 emulation, UTM/hardware, Python/Git 배포본·version·executable digest, shell, NTFS 및 checkout 설정, source/artifact/runner identity | 시험을 다시 수행하고 차이를 조사하기 위한 값. 모든 값이 지원 allowlist 또는 실행 거절 조건이 되는 것은 아님 |
| 지원 정책안 | Windows 11 ARM64/x64, 일반 사용자, guest 또는 물리 PC의 local NTFS, native PowerShell/cmd 진입, 필요한 Git/Win32 기능 | Mac 공유폴더·UNC·cloud sync를 기본 지원 경로로 확대하지 않음. Windows build·edition·Python/Git vendor를 시험 기록과 같다는 이유만으로 고정하지 않음 |
| 유지하는 명시적 runtime 조건 | final GIL-enabled CPython 3.14.6 또는 3.14.7 | 이 patch/build-mode allowlist는 현행 계약이므로 유지. 3.14.8/3.15/prerelease/free-threaded 추가는 별도 qualification/결정 |
| 기능·안전 조건 | `check-attr --source`, 선택한 Win32 API/ABI, 승인된 lock/path/sync/permission 계약, 현재 window와 안전한 target | 기능 부재·안전성 확인 실패·명시적 unsupported 상태를 근거로 거절. 시험한 Git version/vendor 또는 Windows build와 다르다는 사실만으로 거절하지 않음 |
| 실제 판정 표시 | exact tuple별 complete 실행, focused 실행, 실패, 미실행, unavailable와 범위 | `지원 정책상 대상`을 `그 환경에서 테스트 PASS`로 표시하지 않음. 현 `runtime.supported`의 version/build-mode 의미도 임의로 OS qualification 의미로 바꾸지 않음 |

재현용 실행 파일 digest와 source/artifact digest도 역할이 다르다. 전자는 시험 identity이며 일반 사용자 interpreter의 해시 allowlist가 아니다. 후자의 managed inventory 검증은 기존 제품 무결성 계약이므로 계속 필요하다. 특정 OS build/배포본을 실제로 제한해야 한다면 API 부재나 재현된 결함 등 이유, 영향 범위, 대안을 먼저 제시하여 명시적으로 결정한다.

### Named Amendment Scope

아래 조항은 baseline의 현재 원문을 기준으로 R0에 함께 제시한다. 문서 설명만 바꾸어 현행 의무를 우회하지 않는다. DR-0003의 intake amendment 및 Maintaining의 해당 검증 조항에 대한 명시적인 Owner-accepted amendment를 준비해야 하며, 이 note는 그 수락을 기록하지 않는다. 기술 계약의 exact 수정 파일·조항·발효 범위도 Decision Guide에 따라 고정한다.

| 현재 조항 | B와의 충돌 또는 명확화 필요 | 제안하는 변경 |
| --- | --- | --- |
| Development Index: Windows Admission 첫 문장의 exact edition/build/architecture/runtime 선택 | 시험 tuple 선택과 지원 범위 제한이 결합될 수 있음 | exact 대표 환경 선택·기록은 유지하고 지원 범위와 별개임을 명시 |
| 같은 절의 unobserved editions/architectures qualification 금지 | 공통 지원 판정에도 모든 architecture 실측이 필요하다는 현재 경계를 바꾸어야 함 | 미관측 tuple의 PASS/qualification 금지는 유지하되, 대표 환경과 명시적 위험 판단에 근거한 Windows 11 공통 지원 admission을 허용하는 named exception으로 교체 |
| 같은 절의 complete regression 및 열 가지 criteria | 대표 환경에서 충족할 범위와 후속 보완의 구별 필요 | 대표 UTM의 complete 두 모드·focused lifecycle·관련 macOS 회귀는 필수. 각 architecture/물리 PC 전체 실행은 자동 필수로 두지 않음. 나머지 무결성·복구·native·CI/mock 비대체 조건 유지 |
| Maintaining: Validation의 each OS/runtime/build combination, Validation Frequency의 runtime/platform additions, Evidence Reuse의 new runtime/platform combinations complete 요구 | 모든 Windows variant에 full matrix를 요구하는 해석과 직접 충돌 | 최초 Windows 대표 환경에는 full matrix. 같은 승인된 Windows 구현의 추가 architecture/build/distributor에는 아래 위험 기반 focused 검증을 기본으로 하는 명시적 예외. 새 OS, 허용 밖 Python, record/acceptance/recovery 변경 및 입증된 넓은 영향에 대한 기존 complete 의무는 유지 |
| Development Index: Public Core / GA의 consistent exact macOS/Windows support | 재현 tuple을 제품 지원 목록과 같게 취급할 수 있음 | 수락된 platform 지원 조건과 exact 검증 환경을 각각 일관되게 명시. 두 플랫폼의 anonymous lifecycle 및 다른 GA 조건은 유지하고 architecture별 전수 실행을 새 조건으로 추가하지 않음 |
| Security And Support: Runtime And Scope와 현재 지원 설명, capability/help/manual | 이미 runtime gate와 distributor/OS qualification을 구별함 | 이 구별을 보존하고 수락 후 공통 지원 정책과 실제 환경별 결과를 나란히 표시. 과거 Windows unqualified 관측을 소급 변경하지 않음 |

지원 정책 amendment의 핵심 문안 제안은 다음과 같다. 기존 기술 안전 조건의 약화, 물리 검증 waiver의 무조건적 안전 보장, 또는 지금의 지원 선언으로 읽지 않는다.

> Windows 11 support may cover ARM64 and x64 under the accepted runtime, filesystem and capability requirements. Initial admission uses complete normal and parent-optimized validation on one representative UTM guest, required lifecycle and recovery evidence, and relevant macOS regression. Record the exact tested environment separately. Untested environments remain untested; their absence alone does not require another complete suite or a physical PC before initial admission. Additional variants use implementation-risk-based focused checks. A proposed full rerun must identify the uncovered failure mechanism, why focused checks are insufficient, and the affected scope. Environment-record differences alone do not create runtime rejection conditions.

### Existing Code And New Windows Risk

현재 baseline에서 자체 native binary/extension 또는 CPU 분기가 관측되지 않았다는 사실은 기존 Python 로직의 CPU 의존성이 작다는 판단을 뒷받침한다. 아직 작성하지 않은 Windows 구현의 이식성을 증명하지는 않는다. 특히 stdlib `ctypes`를 사용해도 native API의 타입·calling convention·구조체·handle lifetime 위험은 새로 생긴다. R0와 구현 종료 시 실제로 선택한 API·binding·packaging을 고정하고 아래 시험을 그 구현에 맞춰 확정한다. 사용하지 않은 API 조합까지 의무 시험으로 늘리지 않는다.

| 검증 영역 | 대표 UTM에서 확인할 구체적인 항목 | 추가 architecture/물리 PC의 focused 보완 |
| --- | --- | --- |
| ABI / ctypes | 각 호출의 `argtypes/restype`, Windows calling convention, HANDLE/pointer와 정수 폭, `OVERLAPPED` 등 실제 구조체의 size/alignment/field offset을 공식 선언과 대조. NULL/invalid handle, 실패 반환값·last-error, Unicode buffer 길이·수명, handle close/비상속을 실제 API 성공·실패 경로로 확인 | 선택한 interpreter/process architecture에서 binding/layout와 실제 API smoke 반복. 자체 binding의 같은 상수를 비교하는 것만으로 oracle를 만들지 않음. x64 emulation은 그 실행 형태로 기록 |
| 잠금과 경로 | 실제 두 process의 경합·배타성·해제·비정상 종료 후 재획득, anchor 교체와 재진입, child handle 상속 여부. ancestor/leaf reparse·junction·hardlink·race에서 외부 bytes 및 truth 보존 | lock/reparse primitive와 process 종료/복구에 실제 차이가 있는지 집중 확인. instruction-set 이름만 다르다는 이유로 Work/intent 전부를 반복하지 않음 |
| 교체·동기화·권한 | 선택한 `os.replace` 또는 Win32 교체 API에서 열린 handle의 share mode, read-only/ACL 거절, staged same-volume replace와 B1 전후 중단, flush 실패/복구, file identity·Git mode를 확인. 독립적인 bytes/truth/handle 관측 사용 | x64 runtime의 API 경로와 물리 PC의 storage/endpoint software 차이를 focused 재현. 교체 성공을 directory durability나 power-loss PASS로 표시하지 않음 |
| native launcher / 배포 | 실제 선택한 `.cmd` 등에서 interpreter·child architecture, `-I -B`, source/installed 경로, CWD 독립, 공백/Unicode/메타문자 argv·stdin·exit, 잘못된 Python 거절, inventory/update/repair/detach 확인 | 해당 배포본·architecture에서 launcher/child와 패키지 선택 smoke. native extension·별도 binary packaging이 도입되면 그 추가 차이를 새 위험으로 평가 |

타입·호출 규약의 근거는 [ctypes](https://docs.python.org/3.14/library/ctypes.html), [Windows Data Types](https://learn.microsoft.com/en-us/windows/win32/winprog/windows-data-types), [OVERLAPPED](https://learn.microsoft.com/en-us/windows/win32/api/minwinbase/ns-minwinbase-overlapped)다. 2026-10-17 조회 문서는 설계 입력이며 exact guest 실행의 대체 증거가 아니다. 함수명만 같은 두 binding이나 둘 다 64-bit라는 사실만으로 ABI 검증을 면제하지 않는다.

### Escalation And Residual Risk

추가 architecture의 full matrix가 필요하다고 판단하면 Driver가 (1) 관측되거나 근거 있는 failure mechanism, (2) 영향을 받는 reader/writer/acceptance/recovery 경로, (3) 위 focused 시험과 기존 대표 환경 anchor로 다룰 수 없는 이유, (4) 필요한 환경·exact IDs/모드·예상 시간과 최초 admission에 미치는 영향을 먼저 설명한다. Owner의 해당 범위 결정 없이 물리 PC 확보나 전체 재검증을 새 필수 조건으로 추가하지 않는다. 단, 알려진 무결성 문제의 영향을 받는 작업은 보존·중단 경계를 따른다.

예를 들어 다른 architecture에서 별도 native implementation/packaging이 제품 경로를 바꾸거나, 실제 crash/handle truncation/동시성 실패가 나타나고 그 영향이 공통 publication·recovery 전체로 번지는 경우에는 focused 확인만으로 부족할 수 있다. 우선 영향을 좁혀 검사하고, 좁힐 수 없는 근거가 있을 때 해당 조합의 complete matrix를 제안한다. 단순히 build/vendor가 다르거나 그 PC를 아직 구하지 못했다는 이유는 이 확장의 충분한 근거가 아니다. 공통 record/acceptance/recovery 자체를 바꾸는 경우의 기존 full regression 의무는 별도로 유지한다.

잔여 위험은 미실측 x64 native API/배포본 차이, 물리 storage·endpoint software 간섭, Windows update별 동작 차이, 대표 VM이 드러내지 못하는 경합이다. R0는 대표 환경에서의 예방/거절·복구 증거와 후속 집중 검증이 이 위험을 어떻게 다루는지 평가한다. 위험 처분과 지원 정책 수락은 Owner 결정이며, 실제 후속 관측이 나올 때 기존 지원 설명을 재평가한다. 알려진 안전 결함이 없는 미검증 환경을 PASS로 만들거나, 증거 없는 모든 불확실성을 최초 admission의 새 blocker로 바꾸지 않는다.

## Timing Amendment Proposal

이 절은 수락되지 않은 최소 amendment안이다. DR-0003의 accepted Windows intake 중 Development Index `Windows Admission` 첫 문장의 시점만 아래 문장으로 교체하는 안을 검토한다. 현재 문서는 수정하지 않는다.

> Windows preparation and R0 planning may proceed before macOS Preview under explicit Owner authorization. Separately authorized feasibility probes may run outside product source in a reviewed disposable boundary without accepting prospective product contracts first. Product implementation and product qualification require the then-required contract amendments and bounded execution plan to be accepted. Formal Windows admission and public support promotion remain after live macOS Preview and require the then-accepted Windows admission criteria, review and Owner acceptance.

이 timing amendment 자체는 환경 기록의 정확성, standard-user guest NTFS, native launcher, 무결성·복구 criteria, CI/mock 비대체, Public Core/GA 선행 관계를 유지한다. B안에 필요한 지원 범위·대표 환경 검증 기준의 변경은 위 Named Amendment Scope에 명시해 함께 R0에 제시하되 별도로 식별하여 수락해야 한다. 시점 변경만으로 그 정책이나 sync/permission/window 계약, R0/R1, 구현·공개 권한을 수락하지 않는다.

## Verification And Completion Plan

### Bounded Stages

| 단계 | 실행할 내용 | 완료 조건 / 시간 경계 |
| --- | --- | --- |
| P0: 준비 완료 | source/host 정적 진단, 계획과 R0 입력 | source note·private evidence·명시적 미확인 목록; 무거운 suite 없음 |
| P1: baseline 관측 완료 | ARM64 guest tuple, source bytes, import/help 및 native 진입 실패 | exact source/runtime와 실패 출력 보존; child 15초 준수. 환경 준비 포함 10분 예상은 초과; 제품 writer 없음 |
| P2: 별도 승인 후 spike | 제품 외부 probe로 lock, ancestor/reparse, flush/replace, permission/state, launcher/ABI 후보 관측 | VM 복구점·공유 분리·network 차단·무자격증명 경계 확인 후 1개 합성 NTFS target군. 실행 항목당 5분·총 30분 초안; 작성/환경 준비 시간은 별도 추정. exact 명령과 예산은 실행 승인 전에 고정 |
| P3: 별도 승인 후 구현 | 수락된 seam·window 계약과 oracle/runner, 구현 종료 후 runner qualification | 통합된 main 재기준화; focused positive/refusal/interruption 및 runner 경계 검증. P4 전에 declared/discovered/executed ID와 counterpart/N/A 근거를 고정 |
| P4: 고정 candidate qualification | 대표 UTM Windows의 full normal + parent-optimized, focused lifecycle/explicit factories, 관련 macOS regression | source/runtime/runner/inventory drift 없음, complete discovery/execution 근거. 추가 x64/물리 PC는 위험 기반 후속 focused lane; 자동 full/최초 admission gate 없음 |
| P5: 결과 검토 | R1, Driver 처분, Owner 결과 수락 | exact candidate와 미해결 항목, 이후 정식 admission 시점 판정 |

P2의 측정 결과로 P4의 예산을 정한다. Windows/macOS 모두 최초 전체 실행의 임시 상한은 mode당 90분 제안이며, 시작 전 측정 시간+여유를 근거로 확정한다. 무조건 더 기다리는 방식은 금지한다. 자연 종료·child 회수·budget 중단을 구분하고 budget 종료는 incomplete다. 실행 중인 주 작업과 무거운 시험을 겹치지 않도록 시작 시 자원 상태를 확인한다. 승인되지 않은 reviewer는 호출하지 않는다.

### Required Matrix

| ID | 검증 내용 | 성공 기준 |
| --- | --- | --- |
| W01 | 재현용 exact tuple, 명시적 Python 조건과 child identity, Git/Win32 capability | 계약상 runtime·기능·안전 조건 위반 시 거절. 환경 기록값 차이만으로 거절하지 않음 |
| W02 | native help/doctor/init/status/update/rollback/repair/detach; preview/apply/refusal | POSIX shell 없이 동일 목적 달성; 실패 전후 truth 보존 |
| W03 | file flush, directory 처리, open handles, replacement 실패·중단 | sync/replace/복구를 각각 판정; false pass·power-loss 주장 없음 |
| W04 | CRLF/case/NFC/reserved/ADS/trailing dot-space/8.3/reparse/hardlink | unsupported 입력을 쓰기·외부 읽기 전에 결정적으로 거절 |
| W05 | fresh clone/worktree, non-Git target, current-format intent/Work/worker·umbrella | 기존 authority와 acceptance 의미 보존 |
| W06 | 두 writer 경합, 실제 process 종료, 부분 발행·foreign edit·exact retry | 중복 수락/authority 손상 없음; 안정된 non-pass 또는 명시적 복구 |
| W07 | 대표 UTM의 complete normal/parent-optimized + explicit factory tests + 관련 macOS 회귀 | declared ordered IDs = discovered = executed를 대조하고 modes, skips/failures, budgets, 독립 oracle를 기록. POSIX 전용 ID는 Windows counterpart 또는 구체적인 N/A 근거를 대응시키며 broad skip을 complete PASS로 세지 않음. 추가 architecture의 focused/미실행은 complete PASS와 분리 |
| W08 | help/capability/manual/adapter, reader/resume | runtime gate·지원 조건·실측 환경을 구별하고 각 설명을 일관되게 유지 |
| W09 | autocrlf false/true, payload/manifest/inventory/refetch | managed bytes가 checkout 설정으로 조용히 변하지 않음; project CRLF exception 범위 유지 |
| W10 | authenticated prerelease와 anonymous 공개 절차 구분 | private 성공을 public onboarding PASS로 사용하지 않음 |

unittest 기본 명령은 Maintaining을 따른다. Windows에서도 interpreter를 절대 경로로 고정하고 child용 `PYTHONDONTWRITEBYTECODE=1`, `PYTHONPATH=src`를 설정한 격리 runner에서 `-B -m unittest discover -s tests -v`와 `-B -O ...`를 실행한다. child가 `-O`를 상속한다고 가정하지 않는다. 기본 discovery에 들어오지 않는 `tests/test_entry_window_transition.py`의 explicit factory와 새 Windows oracle를 별도 열거한다. 609라는 AST 숫자를 complete collection 크기로 쓰지 않는다.

현재 있는 suite family는 `test_workspace`, `test_productization_safety`, `test_runtime_admission`, `test_worktree_checkout_bytes`, `test_worktree_execution`, `test_worktree_integration`, `test_worktree_process_safety`, `test_worktree_process_recovery`, `test_umbrella_lifecycle`, `test_umbrella_recovery`, `test_candidates`, `test_human_view`다. 이 목록은 focus 영역이며 완전한 실행 allowlist가 아니다. P3 종료 시 실제 ordered IDs/모드/runner bytes를 고정한 후 P4에 들어간다. Windows oracle가 미작성인 현재 exact 실행 ID를 꾸며 내지 않는다.

### Isolation And Recovery

일반 worktree만으로 실행 격리를 주장하지 않는다. spike 전에는 복구 가능한 disposable VM 경계와 복구점을 확인하고, 전달용 공유 폴더를 분리하며, network를 차단하고 credential 없는 실행 계정을 준비한다. 기존 복제본이라는 사실만으로 복구점이나 무자격증명 상태를 추정하지 않는다. guest NTFS의 별도 source/fixtures/output, child process 회수와 합성 외부 경로 canary를 확인한다. 필요한 입력 복사와 로그 보존 경로를 먼저 검증하고 공유 분리는 실행 직전에 한다. 이번 리뷰 중 VM 설정은 바꾸지 않았다. Windows runner는 아직 없다. 제품 외부 spike에는 승인된 disposable guest 경계를 사용하고, 제품 suite의 guest 내부 쓰기 제한·runner qualification은 P3 종료 전에 검증한다. 이 둘을 동일한 선행 조건으로 묶지 않는다. runner/safety oracle 변경도 source workflow의 R0/R1 대상이며, 이번 정적 계획 리뷰를 미작성 runner의 qualification으로 간주하지 않는다. VM 전체가 격리돼도 guest 내부 쓰기 경계까지 입증한 것으로 보지 않는다. Job Object의 process 회수 기능만으로 filesystem/network 격리를 주장하지 않는다.

process별 fixture temp 경로는 task-owned durable guest root 아래로 지정한다. 전역 TEMP/TMPDIR나 OS policy를 변경하지 않는다. 실패 시 해당 synthetic state·request·receipt·출력만 보존하고 unsupported state를 지워서 재개하지 않는다. 복구는 exact approved retry 또는 별도 Owner disposition이다. baseline source는 Git에서 복구 가능하며 구현 전 branch가 기준이다. 제품 transition 뒤 rollback 제한은 successor 계약으로 확정한다. 실제 사용자 project에 lifecycle을 실행하지 않는다.

## Integration With Concurrent Main Work

현재 별도 진행 중인 ordinary acceptance 변경은 `colvia`, product/work/workspace/intent/cli/candidates/view, capability, 문서와 시험에 걸쳐 있다. 파일명 수준의 읽기 전용 확인만 했으며 그 작업의 미커밋 bytes를 본 준비로 가져오지 않았다. 이 파일들은 Windows 계획과 겹친다.

기존 main을 고정해 사전 조사하되, 구현 시작 또는 qualification 동결 전에는 최신 원격 main과 해당 작업의 수락·통합 상태를 재확인한다. 통합된 commit에서 달라진 inventory/window, acceptance 권한, bootstrap allowlist, process recovery, test discovery를 다시 비교한다. 통합되지 않은 변경은 cherry-pick/복사하지 않는다. baseline 실패는 원 commit의 역사로 보존하고 successor에 같은 실패가 있다고 자동 간주하지 않는다. 충돌은 Windows task의 범위에서 해소하고 주 작업의 결과를 임의 수정하지 않는다.

## R0 Completion And Open Decisions

2026-10-17 Owner 승인으로 Claude 정적 R0를 완료했다. 판정은 request-changes이며 아래에 응답 원문과 Driver 처분을 분리했다. Owner의 구현/계약 수락은 아직 없다. source note와 기준 commit, source/host 진단, 공식 API 링크, 영향 파일, 실제 ARM64 guest tuple·실패 관측·입력/원출력 digest를 검토 입력에 반영했다. 변경 전 baseline에 필요한 환경·실패 재현 공백은 채웠다. 실행 격리, Win32 spike, 계약 amendment와 최종 qualification 계획은 여전히 검토·결정 대상이며 이 packet 자체가 구현 승인은 아니다.

R0의 질문은 다음 여섯 가지다.

1. Windows ancestor/reparse race와 lock anchor identity를 기존 안전 조건보다 약화하지 않고 구현할 수 있는가?
2. standard-user NTFS에서 D3 sync와 0600/0755 의미를 그대로 충족할 수 있는가, 아니면 어떤 named amendment가 필요한가?
3. native launcher/helper inventory와 receipt/window 변화가 old writer 및 downgrade를 안전하게 차단하는가?
4. 실제 선택할 ctypes/Win32 ABI·잠금·replace·launcher의 집중 검증과 Git mode·CRLF·reserved/ADS·open-handle 독립 oracle가 false PASS를 막는가? 기존 코드의 낮은 CPU 의존성과 새 native boundary 위험을 구별했는가?
5. B의 공통 지원 정책, 대표 UTM 전체 실행, 추가 x64/물리 PC 후속 focused 검증을 구별했는가? Named Amendment Scope의 현행 충돌 조항을 충분히 바꾸면서 환경 기록을 runtime allowlist로 만들지 않는가? 더 넓은 full matrix를 요구한다면 focused 증거로 부족한 구체적 이유와 최초 admission 영향은 무엇인가?
6. Preview timing amendment가 정식 admission/공개 승격의 선행 조건을 그대로 보존하는가?

이번 호출의 exact packet은 동결해 보존한다. 아래 문서 보완은 리뷰 후 Driver 판단이며 Claude가 수정본을 다시 승인한 것이 아니다. 후속 리뷰가 필요하면 새 입력을 식별하고 기존 packet을 덮어쓰지 않는다. 최종 응답 원문, accept/revise/defend/needs-user 처분, 실제 Owner 결정을 이 note에 구분한다.

## Preparation Result And Retention

현재 완료: source worktree 고정, 정적 진단, 호스트 runtime 선택 정정 및 전역 3.14.7 변경 확인, host source help, 복제 guest 준비와 실제 tuple 기록, 기준 source의 import/help/native 실패 재현, 이식/회귀/통합 계획, Timing Amendment 초안, 실제 관측을 반영한 R0 입력, Claude R0와 Driver 처분. 미완료: Windows runner·무자격증명 계정 격리 qualification, API spike, 계약·실행 범위 결정 및 모든 제품 구현·수락·공개 작업.

source note는 이 checkout에 보존한다. private task artifacts에는 호스트 경로/실행 digest·진단 원출력과 guest runbook·R0 packet을 보존한다. 해당 경로는 source/Git 공개 문서에 넣지 않는다. consumer는 Owner의 실제 관측 검토와 다음 R0/승인된 이식 준비이며, 계획이 successor record로 정확히 이관되거나 폐기 결정되어 유일한 증거·재개 의존성이 사라질 때 보존 필요를 재평가한다. 현재는 R0의 기준 source 대조와 후속 승인된 이식 준비라는 재사용 계획이 있어 host worktree와 guest clone/runtime을 유지한다. guest baseline 준비까지 임시 저장소에서 이동하거나 삭제한 파일은 없었다. 이후 R0에서 final과 동일한 partial, 빈 stderr·도구 임시 디렉터리와 일회용 반영 도구를 정리했다. 원문·검토 입력·baseline 증거와 active 경로는 유지한다.

준비 문서 검증: local links와 whitespace 검사, GFM 렌더링을 통과했다. Python helper 4개는 AST parse를 통과했고 guest 전용 helper 2개는 호스트 실행을 거절했다. 이 초기 문서 검증 뒤 Windows PowerShell 5.1에서 준비 스크립트와 두 guest Python helper를 실제 실행했고, 결과·해시를 추가 보존했다. 이는 제품 suite 통과가 아니다. 최초 검사 helper가 no-index diff의 정상 difference exit 1을 오류로 간주하여 판정을 정정했다. 이는 제품 또는 Windows 실패가 아니다.

2026-10-17 정책안 보완: Owner 요청으로 B를 우선 권고안으로 구체화하고 재현 기록/지원 조건/실행 거절을 분리했다. 현행 exact-architecture 및 환경별 full 검증 조항의 amendment, Win32 구현 위험별 시험, 추가 full matrix의 근거·영향 설명 요건을 R0에 포함했다. 이는 계획 변경 승인만 반영하며 정책 수락·지원 선언·R0 호출은 아니다. 그 보완 시점의 UTM 대기는 이후 Owner 준비 완료 통지로 해제됐다. guest NTFS, 작업 격리, 통합 후보 영향 검증과 macOS Preview 이후 정식 admission 조건은 유지한다.


## Cross-Agent Review And Discussion

### R0 Request And Input Identity

Owner는 2026-10-17 실제 Windows 관측을 반영한 R0를 Claude로 검토하고 Driver 판단과 구현 전 결정 사항을 정리하도록 승인했다. 제품 구현 금지는 유지됐다. Driver는 Codex, Reviewer는 Claude Opus 5.5 (`claude-opus-5-5`), 최종 결정자는 Owner다. Claude Code 2.1.302의 새 session `6e4012c7-68dc-471e-8839-b0439ef4574b`에서 tools 없는 정적 검토 1회를 수행했다. 인증은 `claude.ai` / first-party / Pro였고 API key 경로로 전환하지 않았다. CLI exit 0, 315.588초, tool event 0이며 이는 리뷰 응답 완료이지 제품 시험 PASS가 아니다.

| 입력/결과 | 식별값 |
| --- | --- |
| source baseline | `a93f71c359c4f0a9d57fcfb50d5999160e870f77`; tracked product diff 없음 |
| 리뷰 당시 untracked plan SHA-256 | `19af8c0bdc992307255741317e4cc6bff5a980172cf36481ab1b9504e23564f9` |
| 해당 new-file diff SHA-256 | `3287bc3e82602b377781aacd7b2da97d1701d0395b16c794dca733851971619c` |
| frozen packet SHA-256 | `a2e75c99bf2c9cf7b60b8017a03cae2520f8cccc82fc366b742c4edb1d4705ab` |
| request + packet stdin SHA-256 | `7b63a0cf6f6ae8f6f0c01bc90842d4cfed5d2c1df87f011167ad6ccfd484e7ea` |
| Reviewer final SHA-256 | `c4b55c139c4c1df620b3c6fa91e01d95ff1166853f8503b75bce930ad995dfc9`; 27,888 bytes |
| drift 검사 | 32개 입력 호출 전후 일치; 설명되지 않은 drift 없음 |

packet은 당시 계획, 계약/코드 발췌, source·host·guest 관측 요약 및 digest를 포함했다. packet의 과거 호출 미승인 표기는 request wrapper에서 이번 1회 승인에 한해 갱신했다. private 원출력 전체나 VM 접근 권한을 Reviewer에게 제공하지 않았다. Reviewer는 관측을 재현하거나 raw digest를 독립 대조하지 않았다. 새 모델/session과 도구 제한은 기록된 독립성 경계이며, 제공된 발췌 밖까지 검토했다고 주장하지 않는다.

### Driver Disposition

`accept`는 지적을 계획에 반영한다는 뜻이며 Owner의 정책 수락이 아니다. `revise`는 핵심 위험을 수용하되 제안의 적용 범위나 해결책을 수정한다. 아래는 source baseline을 읽어 판단한 결과와 공식 문서 확인이며 새 Windows 시험은 실행하지 않았다.

| Finding | 판단 | 근거와 반영 / 남은 결정 |
| --- | --- | --- |
| F1 · P1 · 공통 sync와 D3 | revise | `jsonio.py:116–129,176`에서 directory open은 try 밖이며 flock보다 먼저 실행된다. 공통 helper 문제를 수용한다. 다만 `_entry_sync`와 `product.py:1464–1472`는 과거 전환에 D3를 적용한다. Windows의 과거 전환 제외를 우선 비교한다. NTFS만 보고 `not-applicable`로 면제하지 않으며, 실제 결과 분류와 허용 기능은 spike 후 계약으로 결정한다. |
| F2 · P1 · 경로 검사 | accept | junction/reparse 대응과 direct `O_NOFOLLOW`/`dir_fd` 의존성 목록을 구현 전 고정한다. 모든 component의 reparse 기본 거절, ancestor race 및 unknown tag 시험이 필요하다. lock 해제 지연의 시험 상한은 제품의 blocking 의미와 분리한다. Windows 종료 oracle는 SIGKILL과 동일하다고 부르지 않는다. |
| F3 · P1 · mode와 상태 | revise | mode가 상태 표식인 점과 `work.py:128`의 stat 기반 Git mode 유도 문제를 수용한다. 그러나 0600/0755 전환 상태는 제외할 lifecycle에까지 새 Windows 계약으로 복제하지 않는다. 지원 경로의 실제 call graph만 대상으로 staging/rename 상태와 상속 ACL 유지안을 비교한다. Git mode는 index/manifest 의미를 보존한다. |
| F4 · P2 · reader share와 replace | revise | sharing violation 위험을 수용한다. 우선 안정 non-pass와 exact retry를 비교하고 모든 reader를 Win32 opener로 바꾸는 확장은 측정으로 정당화한다. delete-pending 반복과 자기 교체 결과는 미재현 가설이다. reader share mode별 probe가 선택 근거다. |
| F5 · P1 · launcher | revise / needs-user | `.cmd`를 기본값으로 확정하지 않는다. explicit Python 진입을 우선 권고하고 native-launcher 요구 해석을 Owner 결정으로 남긴다. batch 인자 재해석은 공식 Python 문서에서도 확인했다. 자기 교체 문제와 safe-character 해결책은 아직 실측하지 않았으며, 기존 인자 계약 축소를 자동 수용하지 않는다. |
| F6 · P1 · inventory와 Git 이동 | revise | fresh-only라는 설명만으로 Git clone 경로가 차단되지는 않는다. 아래 정적 분석상 module/managed-path 추가 시 같은 entry-1 호환 주장은 성립하지 않는다. successor window를 우선 권고한다. 생성 OS를 추정해 blanket 거절하는 대신 실제 window/inventory와 현재 환경 capability를 검사한다. 전체 old-writer fence가 입증됐다는 뜻은 아니다. |
| F7 · P2 · 격리와 completeness | accept | mutating probe 전에 공유를 분리하고 disposable VM 복구점·network·credential 경계를 확인한다. 제품 suite runner qualification은 P3 종료 조건으로 분리한다. declared/discovered/executed ID 대응과 counterpart/N/A 근거를 P4 전에 고정하며 skip을 PASS로 세지 않는다. |
| F8 · P2 · B 정책 세부 | revise / defend | OS architecture × process architecture, 지원 정책 대상/실행 관측/정확한 환경 qualification을 분리한다. edition 명칭과 제품 Enterprise tier도 구별한다. x64 smoke를 admission 필수로 앞당기는 부분은 채택하지 않는다. Reviewer도 B를 반박하는 구체적 failure mechanism을 제시하지 않았으므로 Owner의 후속 보완 방향을 유지한다. 알려진 결함이 발견되면 기존 escalation 규칙을 따른다. |
| F9 · P2 · timing 문안 | accept | `then-accepted Windows admission criteria`로 정리하고 제품 외부 feasibility probe를 제품 구현/qualification과 분리한 수정 초안을 제시했다. Preview 이후 formal admission은 유지한다. 아직 amendment 수락은 아니다. |
| F10 · P3 · 통합·예산 | revise | 제품 P3는 ordinary acceptance 통합 상태를 확인하고 그 commit에 재기준화한 뒤 착수하는 안을 권고한다. spike는 독립 가능하다. 30분은 probe 실행 예산 초안이며 작성/환경 준비는 별도다. PATH로 호출한 Git과 관측 executable digest의 결합은 이번 baseline의 한계로 남기고 다음 실행에서 절대 경로를 고정한다. |

### Additional Static Evidence And Limits

- 현재 `colvia:63–84`는 entry-1 식별과 importable package의 정확한 11-module membership을 검사한다. 새 12번째 module은 이전 launcher의 검사를 통과하지 않는다. `.cmd`만 추가하는 경우는 이 검사 하나로 결론 내리지 않는다.
- `product.py:329–347`은 window별 exact path와 순서를 검사하므로 기존 entry-1 이름 아래 managed member를 추가하면 이전 reader가 거절한다. `product.py:895–908`은 binding chain이 참조하는 retained release도 검증한다. 이는 source의 정적 확인이며 임의의 모든 과거 writer가 안전하게 fence된다는 실행 증거는 아니다. 새 후보가 정해지면 audited old writer별 active/pending/retained 상태 및 guard 이후 거절을 검증해야 한다.
- 현재 receipt/binding만으로 생성 OS를 확정하는 새 필드는 없다. “타 platform에서 생성됐으므로 거절”이라는 문구만으로 강제할 수 없다. window와 계약상 관측 가능한 capability로 경계를 정하며, provenance field를 새로 넣는다면 별도 record 변경으로 심의한다.
- D3 전용 helper와 0600/0755 전환 predicate는 기존 전환 경로의 의미다. Windows에서 그 경로를 제외하는 결정은 D3의 전면 재설계를 줄일 수 있다. 공통 lock/publication helper, Git mode, 새 Windows 발행의 복구 의미는 여전히 해결해야 한다.
- 공식 문서 확인: Windows chmod는 POSIX permission 의미를 제공하지 않는다([Python os](https://docs.python.org/3.14/library/os.html#os.chmod)). batch 진입은 shell 인자 재해석 위험을 가진다([Python subprocess](https://docs.python.org/3.14/library/subprocess.html#security-considerations)). process 종료 후 lock 해제는 지연될 수 있다([LockFileEx](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-lockfileex)). flush의 handle access 조건([FlushFileBuffers](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-flushfilebuffers))과 move의 write-through 설명([MoveFileExW](https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-movefileexw))을 API 선택 시 분리한다. 같은-volume rename의 directory durability를 flag 이름만으로 증명하지 않는다. 2026-10-17 조회한 rolling Python 문서는 3.14.8이며 exact guest 3.14.7의 실행 결과를 대신하지 않는다.

### Decisions Before Product Implementation

아래는 Driver 권고이며 전부 Owner 결정 대기다. spike로 답을 얻어야 하는 세부까지 지금 확정하는 순환은 만들지 않는다.

| 결정 | Driver 권고 | 결정 시점 |
| --- | --- | --- |
| B 지원 기준과 architecture 표기 (Reviewer D7) | Windows 11 ARM64/x64 공통 정책 + 대표 UTM 전체 검증을 유지. OS/process 축을 각각 기록하고 ARM64 OS의 emulated x64는 별도 미검증 구성으로 표시. edition 자체를 자동 제한하지 않고 필요한 capability를 명시. x64/물리 확인은 후속 focused | 축·표기 방향은 구현 전, emulation의 최종 지원 표기·잔여 위험은 admission 전 |
| 최초 lifecycle 범위 (D1) | 새 successor workspace와 같은 window의 update/rollback/repair/detach. Windows의 checkout-1→entry-1 전환과 기존 entry-1 이주는 최초 범위에서 제외하고 안정 거절 설계. macOS의 기존 기능은 유지 | 제품 구현 전 |
| inventory/window (D2) | 새 module/managed member 또는 상태 의미 변경이 있으면 successor window. 실제 이름·exact membership·audited old-writer fence와 retained history는 통합된 후보에서 고정 | 제품 구현 전 |
| 진입 형태 (D4) | explicit Python 진입을 최초 경로로 우선 권고. Owner가 native-launcher 충족 여부를 결정. `.cmd`는 안전한 인자·자기 교체 검증 후 필요성이 확인되면 선택 | 제품 구현 전; 구현안은 probe 결과 활용 |
| 권한·상태·durability·share (D3/D5/D6) | 상속 ACL 유지, 새 기밀성 주장 없음, staging/완성 rename 후보, 안정 non-pass/exact retry를 기본 방향으로 비교. 결과 어휘와 허용 mutation은 실측 후 확정; 기존 D3 false-pass 금지 | 방향은 probe 입력, 최종 계약은 spike 후 제품 구현 전 |
| timing과 통합 순서 (D8/D9) | probe는 제품 source 밖에서 별도 승인, 제품 P3는 통합된 main 재기준화 뒤 필요한 amendment/실행 승인 후. formal admission은 live macOS Preview 이후 | probe 전 bounded plan; 제품 구현 전 해당 amendment |

Timing/B 수락 조합: timing만 수락되면 기존 admission 기준이 유지된다. B만 수락되면 기존 실행 시점 제한이 유지된다. 둘 다 수락되면 변경된 실행 시점과 B의 대표 환경 기준을 함께 적용한다. 어느 조합도 제품 실행·공개 지원을 자동 승인하지 않는다.

권고하는 다음 범위는 제품 외부 feasibility probe 1회다. 실행 전에 exact probe bytes/명령, 합성 target, VM 복구점, 공유 분리, network·credential 경계, child 회수와 실행 예산을 고정한다. lock/ancestor·reparse/flush·replace/state·mode/launcher/ABI를 실제 선택한 후보에 맞춰 묶는다. 이 R0는 계획 위험을 검토했지만 미작성 probe나 runner를 사전 승인한 것은 아니다. 최종 기술 계약 수락은 관측 뒤에 하며, 새 정보가 변경하는 계약·runner 범위에 필요한 후속 검토를 거친다.

### Actual Owner Decisions

확인된 승인: 환경 준비와 baseline, B를 우선 권고로 구체화하는 계획 보완, 이번 Claude R0와 Driver 판단 정리. 미수락: B 정책 발효, lifecycle/window/launcher/permission/durability 계약, timing amendment, probe 실행, 제품 구현/qualification, 결과 수락과 공개 admission. 이번 문서 변경은 계획·리뷰 기록이며 이 경계를 바꾸지 않는다.

### Record Verification

R0 원문 27,888 bytes의 digest와 문서 내 원문 일치를 확인했고 frozen packet은 변경하지 않았다. GFM 렌더링에서 code 밖 literal `**`가 없고 local links 5개가 유효하다. 작성 부분의 whitespace와 tracked diff 검사를 통과했다. 원문의 trailing spaces는 verbatim 의무에 따라 보존했으며 초기 문서 검사에서 이를 작성 오류로 분류한 부분을 바로잡았다. 제품 tracked diff는 비어 있고 source 변경은 이 untracked 계획 문서 하나다. 이 검사는 문서·보존 검증이며 제품 실행 결과가 아니다.

### Verbatim Reviewer Response

아래 fenced block은 응답 27,888 bytes를 그대로 보존한다. 끝의 문서 구분용 newline은 원문 밖이다. 리뷰 당시 계획에 대한 의견이며 위 Driver 수정안을 다시 검토한 응답이 아니다.

````markdown
# R0 정적 계획 검토 — Windows UTM 이식 계획

검토 범위와 한계: 이 검토는 제공된 frozen packet의 bytes만 읽은 정적 검토입니다. 도구 실행, 파일 접근, VM 접근, 네트워크 조회, 시험 실행은 하지 않았습니다. packet에 들어 있는 Windows 관측은 Driver가 제공한 증거이며, 제가 재현한 결과가 아닙니다. packet SHA-256(`a2e75c99…05ab`)과 raw evidence digest도 독립적으로 대조하지 못했습니다. 아래에서 Windows/CPython 동작으로 서술한 내용은 공개 문서와 알려진 동작에 근거한 추론입니다. 이 추론은 spike로 확인해야 하며, 제가 재현한 반례가 아닙니다.

---

## 1. Verdict

**계획 검토 판정: request-changes (제품 구현 계획 기준)**

이 판정은 계획 검토 의견일 뿐이며 Owner 승인이 아닙니다.

- 제품 구현 계획으로서는 수정이 필요합니다. 기존 POSIX 검사가 Windows에서 실패하지 않고 조용히 약해지는 경로가 계획에 명시되지 않았습니다(F2, F3). `.cmd` launcher 고유의 위험과 interpreter 선택 방식이 managed inventory와 충돌합니다(F5). Git으로 운반된 workspace를 통한 cross-platform old-writer 문제도 범위에서 빠져 있습니다(F6).
- 격리 spike 계획으로서는 F7의 격리 조건, 특히 공유 폴더 분리를 추가하면 조건부로 수용할 수 있습니다. spike는 계약 amendment 수락을 전제로 하지 않습니다.
- B 정책안은 구조적으로 타당합니다. 다만 architecture 축의 정의와 지원 표기 용어를 먼저 확정해야 합니다(F8). universal full matrix나 물리 PC gate는 요구하지 않습니다.

---

## 2. Findings

### R0-F1 (P1) — import만 해결해도 첫 lock 획득 전에 실패하며, D3의 적용 범위를 Windows 범위 결정으로 줄일 수 있음

- **위치**: `jsonio.py:116–129`(`sync_directory`), `:148–149`(`_ensure_parent`), `:176`(`exclusive_file_lock` 안에서 `flock` 직전), `product.py:563–586`, `:609–610`, `WORKSPACE-CONTRACT.md:331`. 계획의 Baseline Diagnosis 표 `jsonio.py:100–126` 행.
- **관측**: 실패가 관측된 지점은 `jsonio.py:4`의 `import fcntl`뿐입니다.
- **추론**: Windows CPython의 `os.open(dir, O_RDONLY)`는 CRT 경로에서 `FILE_FLAG_BACKUP_SEMANTICS` 없이 호출됩니다. 따라서 `PermissionError`(errno 13)로 실패할 가능성이 높습니다. errno 13은 `{EINVAL, ENOTSUP}` 분기에 해당하지 않으므로 그대로 raise됩니다. 그 결과 다음 문제가 생깁니다.
  - (1) D3와 무관한 공통 경로인 lock 획득, `write_new_bytes`, `replace_bytes`, `durability_probe`도 모두 실패합니다.
  - (2) 계획 표는 이 문제를 "transition 중 D3"로만 다루고, 공통 helper가 lock을 잡기 전에 실패한다는 점을 적지 않았습니다.
  - (3) `product.py:610`의 read-only handle `os.fsync`는 `FlushFileBuffers`의 write access 조건에 걸릴 가능성이 있습니다.
- **위험**: 구현자가 공통 `sync_directory`에서 errno 13을 `unavailable`로 분류하기만 하면 lock 경로가 통과합니다. 그러면 D3 경로도 같은 helper를 공유하므로 분류 의미가 섞입니다. 계획이 금지한 false pass가 공통 helper를 통해 들어올 수 있습니다.
- **추가 관찰**: D3("Directory synchronization is mandatory for the bounded transition path")는 checkout-1→entry-1 transition(S0–S6)에만 적용됩니다(`product.py:564`의 docstring). Windows 첫 설치는 fresh entry-1이고 checkout-1은 Windows에서 실행된 적이 없습니다. 따라서 Windows에서 이 transition을 안정 코드로 거절하는 범위 결정을 내리면 D3 amendment가 불필요할 수 있습니다. 남는 것은 공통 helper의 directory 결과 분류 문제입니다.
- **권고**:
  - 공통 helper의 Windows 결과 분류를 D3 분류와 별도 계약 항목으로 분리합니다. 예: `directory_fsync: "not-applicable:ntfs"` 또는 실측한 handle flush 결과.
  - Windows에서 checkout-1→entry-1 transition을 거절할지를 먼저 결정합니다(결정 D1).
  - `MOVEFILE_WRITE_THROUGH`의 문서상 보장은 copy-and-delete 이동을 대상으로 합니다. same-volume rename의 directory durability 근거로 쓰면 안 되고, `ReplaceFileW`와 같은 취급을 받아야 합니다.
- **차단 범위**: (a) 제품 구현을 차단합니다(범위와 분류 결정 전). (b) spike는 차단하지 않습니다. directory handle flush를 표준 사용자로 측정하는 것이 spike 항목입니다.

### R0-F2 (P1) — 기존 link 거절 검사가 Windows에서 실패하지 않고 약해짐: junction이 directory로 통과

- **위치**: `workspace.py:62–66`(`_require_kind`), `:116–121`, `colvia:20–22`, `:74–75`, `jsonio.py:157–175`, `work.py:105–110`. 계획의 "Lock And Safe Paths".
- **추론**:
  - Windows CPython의 `lstat`은 directory junction에 대해 `S_ISDIR`=True, `S_ISLNK`=False를 반환하는 것으로 알려져 있습니다(`os.path.islink`가 False이고 `isjunction`이 따로 있음). 그러면 `_require_kind`, launcher 조상 검사, target 검사(`resolve(strict=True)`가 junction을 따라감)가 모두 junction 조상을 정상 directory로 받아들입니다.
  - symlink와 name-surrogate가 아닌 reparse tag(cloud files, AppExecLink 등)는 `S_ISREG`로 보일 수 있습니다.
  - `os.O_NOFOLLOW` 조건 처리가 모듈마다 다릅니다. `jsonio`는 `hasattr`로 확인하므로 Windows에서 조용히 생략합니다. `product.py:704`, `:756`, `view.py:90–93`, `candidates.py:156–159`는 직접 참조하므로 호출 시점에 `AttributeError`가 납니다. `dir_fd`와 `os.listdir(fd)`는 Windows에서 지원되지 않습니다.
- **계획의 공백**: 계획은 "기존 링크/외부 파일 거절 조건은 약화하지 않는다"고 선언합니다. 그러나 import만 조건 처리하면 기존 검사들이 의미를 잃은 채 통과한다는 사실은 적지 않았습니다. 이 상태에서 기존 suite를 돌리면 link 거절 시험이 symlink fixture만 사용하는 경우 junction 경로는 검증되지 않고 PASS가 나옵니다.
- **lock 관련 추가 위험**: `LockFileEx` 문서는 process 종료 시 잠금 해제가 "available system resources"에 따라 지연될 수 있다고 적고 있습니다. W06의 "비정상 종료 후 재획득"을 즉시 재시도로 판정하면 flaky 결과가 나옵니다. 또한 `test_worktree_process_recovery.py:219`의 `actual SIGKILL` 같은 oracle은 Windows의 `TerminateProcess`와 의미가 다릅니다(`signal.SIGKILL`은 Windows에 없음).
- **권고**:
  - 구현 전에 `S_ISLNK`/`is_symlink`/`S_ISDIR`/`S_ISREG`/`O_NOFOLLOW` 사용 지점을 전부 열거한 표를 만듭니다. 각 지점의 Windows 대응을 정합니다(`st_file_attributes & FILE_ATTRIBUTE_REPARSE_POINT`, `st_reparse_tag`, 또는 handle 기반 검사).
  - "reparse 속성이 있는 모든 경로 component는 거절"을 기본값으로 둡니다.
  - lock 재획득 oracle은 "기존 계약의 blocking 의미를 유지하되 측정된 상한까지 기다림"으로 정의합니다.
- **차단 범위**: (a) 차단합니다. (b) spike는 차단하지 않습니다(ancestor handle 유지와 share 제한 조합이 핵심 spike 항목). (c) junction/unknown-tag 시험 증거 없이는 admission을 할 수 없습니다.

### R0-F3 (P1) — mode bit가 권한일 뿐 아니라 transition 상태 표식임. Windows `st_mode`로는 표현할 수 없음

- **위치**: `product.py:424`, `:433–435`, `:716–736`, `:753`, `work.py:128`, `WORKSPACE-CONTRACT.md:319–325`.
- **추론**:
  - Windows CPython의 `st_mode` 권한 비트는 read-only 속성에 따라 0o444 또는 0o666입니다. 실행 비트는 확장자(`.exe/.bat/.cmd/.com`)에서 유도됩니다.
  - 따라서 `mode == 0o600`과 `0o755`는 관측할 수 없습니다. `_entry_file_prefix`와 `_entry_publish`는 항상 거절하게 됩니다.
  - 3.13+의 `os.fchmod(fd, 0o755)`는 read-only 속성만 해제합니다.
  - 중요한 점은 계약에서 0600과 0755가 "불완전 N(S3a/S3b)과 완성된 실행 N"을 구별하는 **상태 표식으로** 쓰인다는 것입니다. 계획은 이를 ACL과 기밀성 문제로만 다루고 있습니다.
  - `work.py:128`의 Git mode 유도는 Windows에서 확장자 기반입니다. 그래서 `.cmd` 파일은 Git이 100644로 기록해도 100755로 보이고, 확장자 없는 실행 script는 100644로 보입니다. 새 `.cmd` shim이 들어오면 이것이 managed path가 됩니다.
- **권고**:
  - Windows에서 상태 표식을 무엇으로 대체할지 계약으로 정합니다. 후보는 staging 이름 분리, read-only 속성, 완성 후 별도 rename입니다.
  - 기밀성 측면은 Security 문서 line 5의 "one trusted local OS account" 가정을 근거로 "상속 ACL 유지, 새 기밀성 주장 없음"을 기본안으로 비교합니다.
  - Git mode는 Windows stat에서 절대 유도하지 않습니다. tracked index mode나 manifest만 사용하고, 표현할 수 없으면 거절합니다. 계획의 방향과 같으며 구현 지점을 명시하라는 요청입니다.
- **차단 범위**: (a) 차단합니다(permission/상태 계약). (b) 차단하지 않습니다.

### R0-F4 (P2) — replace/unlink 실패의 주원인은 reader의 share mode이며, launcher bootstrap도 해당됨

- **위치**: `jsonio.py:205–219`, `colvia:26`(`path.read_bytes()`), `WORKSPACE-CONTRACT.md:321`(S4 unlink 후 "if O is visible again, re-observe").
- **추론**:
  - Python `open`과 `os.open`은 `FILE_SHARE_DELETE` 없이 handle을 엽니다. 다른 process의 reader가 짧게 열어 두기만 해도 `os.replace`(`MoveFileExW`)와 unlink가 sharing violation으로 실패할 수 있습니다. 여기서 reader는 동시에 실행되는 `colvia status`, launcher bootstrap, 백신, indexer를 포함합니다.
  - delete-pending 상태의 이름은 `lstat`에서 `PermissionError`로 보일 수 있습니다. 이 경우 `_exists`가 `FileNotFoundError`만 잡으므로 raise됩니다. S4의 "O가 다시 보이면 재관측" 규칙과 결합하면 진전 없는 반복이 생길 수 있습니다.
- **위험**: S5 binding replace 도중에 일시적 PermissionError가 나면 transition 중간 refusal이 됩니다. ordinary 경로에서는 사용성이 떨어지는 문제지만, transition 경로에서는 복구가 필요한 상태가 됩니다.
- **권고**: 다음 둘 중 하나를 계약으로 고릅니다.
  - (가) 모든 product reader가 `FILE_SHARE_DELETE` opener를 사용합니다. 이 경우 stdlib-only launcher bootstrap에도 ctypes가 들어가므로 bootstrap 신뢰 코드가 늘어납니다.
  - (나) writer가 sharing violation을 "안정 non-pass + exact retry"로 분류합니다. 자동 retry loop는 금지합니다.

  delete-pending, POSIX rename/delete semantics(`FILE_RENAME_FLAG_POSIX_SEMANTICS` 등)는 spike에서 관측만 하고, 동작을 가정하지 않습니다.
- **차단 범위**: (a) 정책 선택은 구현 전에 필요합니다. (b) 차단하지 않습니다.

### R0-F5 (P1) — `.cmd` launcher의 고유 위험과, interpreter 선택 방식과 managed inventory의 충돌

- **위치**: 계획 "Launcher, Inventory And Compatibility", `colvia:1`, `:50–51`, Maintaining line 73–75.
- **추론에 근거한 구체 메커니즘**:
  1. **실행 중 자기 교체**: cmd.exe는 batch 파일을 offset 기준으로 다시 읽습니다. update/switch/repair/detach가 실행 중인 `.cmd`를 교체하거나 삭제하면, python child가 끝난 뒤 cmd가 새 bytes의 같은 offset을 해석하거나 "batch file cannot be found"를 출력합니다. 이로 인해 exit code가 바뀌거나 의도하지 않은 명령이 실행될 수 있습니다. W02의 exit code 계약과 직접 충돌합니다.
  2. **인자 재해석**: `CreateProcess`로 `.bat/.cmd`를 호출하면 cmd가 명령줄을 다시 parse합니다. 이 문제는 Python `subprocess` 문서가 경고하는 BatBadBut 계열입니다. adapter나 agent가 list argv로 `.cmd`를 호출하면 `%`, `^`, `"`, `&` 때문에 인자가 변형되거나 명령이 주입될 수 있습니다. confirmation token이 request bytes에 묶여 있으므로 인자 변형은 integrity 문제입니다.
  3. **interpreter 선택과 고정 bytes의 충돌**: managed `.cmd`는 inventory digest가 고정된 bytes여야 합니다. 그래서 기계별 Python 절대 경로를 넣을 수 없습니다. PATH 검색은 Store alias stub(`WindowsApps\python.exe`)을 잡을 수 있습니다. `py -3.14`는 patch를 고르지 못하고 설치 여부도 보장되지 않습니다.
- **권고**: 결정 D4로 다음 대안을 비교합니다.
  - (가) managed `.cmd` 안에서 single-line 호출과 `exit /b`를 같은 parse 단위에 두고, argv는 안전 문자 집합으로 제한하고 payload는 stdin으로만 받습니다.
  - (나) 문서화된 진입을 `"<python.exe>" -I -B colvia …`로 정합니다. 새 managed file이 없으므로 inventory 변화가 없습니다. 이것이 Development Index의 "native launcher without POSIX shell"을 충족하는지는 Owner 해석이 필요합니다.
  - (다) 별도 native exe. packaging 위험이 새로 생기므로 기본안에서 제외합니다.

  어떤 안이든 interpreter 확인은 Python 쪽 runtime gate와 child identity 검사로 하고, 지원되지 않는 Python은 안정 코드로 거절해야 합니다. 현재 launcher의 except tuple에는 `ImportError`가 없어서 baseline처럼 traceback과 exit 1로 끝납니다.
- **차단 범위**: (a) 차단합니다(launcher 형태). (b) spike에 1~2 항목을 추가해야 합니다(실행 중 교체, 메타문자 argv).

### R0-F6 (P1) — "fresh target only" 범위가 Git으로 운반되는 workspace를 막지 못함. window 결정은 정적 분석으로 먼저 가능

- **위치**: 계획 "Windows 첫 설치는 fresh target이며 macOS workspace를 Windows로 옮기는 기능은 이번 범위가 아니다", `WORKSPACE-CONTRACT.md:325`("including after a Git checkout"), Maintaining line 87–89, `colvia:71–79`.
- **추론**:
  - 계약 문구로 보아 `colvia`와 `.hrn/product/binding.json`은 tracked될 수 있습니다. 그렇다면 macOS adopter의 repository를 Windows에서 clone하는 상황은 "이동 기능"이 아니라 일상적인 경로입니다. 반대로 Windows에서 만든 record가 commit되어 macOS의 old entry-1 writer 앞에 나타날 수도 있습니다.
  - autocrlf=true이면 canonical JSON 검사(`colvia:44`)에서 fail-closed가 되므로 다행입니다. 그러나 이것은 우연히 얻은 안전입니다.
  - Windows에서 old entry-1 release는 `fcntl` import 실패로 자연스럽게 fence됩니다. 관측 사실에서 나온 유용한 성질입니다. 하지만 crash 형태여서 안정 refusal은 아닙니다.
  - 모듈 추가(12번째)나 `.cmd` 추가는 `colvia:78`의 exact package membership과 29-path entry-1 membership을 바꿉니다.
- **권고**:
  - 첫 admission 범위로 다음을 명시적으로 거절할지 결정합니다(D1). (i) Windows 제품이 macOS나 다른 platform에서 생성된 workspace를 만났을 때, (ii) macOS writer가 Windows에서 생성된 record를 만났을 때.
  - 새 inventory_id 필요 여부는 구현 없이 old entry-1 reader 코드를 정적으로 분석해 답할 수 있습니다(31-path entry-1 inventory를 거절하는지, retained release를 순회하는지). 이 질문을 spike나 구현 이후로 미루지 않습니다.
  - Windows의 mode/상태 표식이 바뀌면(F3) record 관측 의미가 바뀌므로, 현재 정보로는 successor window를 기본값으로 권고합니다.
- **차단 범위**: (a) 차단합니다. (b) 차단하지 않습니다.

### R0-F7 (P2) — test oracle 완전성과 실행 격리: 공유 폴더는 host 쓰기 경로이며, runner 단계가 없음

- **위치**: 계획 "Isolation And Recovery", "Required Matrix W07", Bounded Stages 표, `tests/test_entry_window_transition.py:11`, Workflow line 64.
- **관측**: 전달용 UTM 공유 폴더가 설정되어 있습니다. 전용 무자격증명 계정과 격리는 qualification되지 않았습니다.
- **추론**:
  1. 공유 폴더는 guest에서 host로 쓸 수 있는 경로입니다. 계획은 "Mac 공유폴더를 fixture 경로로 쓰지 않음"만 적었고, mutating 실행 중 분리하거나 read-only로 두는 조건은 없습니다. path 결함이 있는 제품 코드가 이 경로로 탈출할 수 있습니다.
  2. top-level `import fcntl` 때문에 기본 discovery에서는 `_FailedTest`가 나고, explicit factory는 import error가 납니다. "complete"의 정의가 없으면 broad skip과 platform 분기가 complete로 집계될 수 있습니다.
  3. Windows runner는 Workflow line 64에 따라 R0/R1 대상인 "runners, safety oracles" 변경입니다. 그러나 Stage 표의 P2(spike)와 P3(구현) 어디에도 runner qualification 단계가 없습니다.
- **권고**:
  - spike와 mutating 실행 전에 다음을 갖춥니다. 일회용 VM clone 또는 snapshot에서 되돌리기, 공유 폴더 분리, network 차단, credential 없음, 외부 canary.
  - spike 용도로는 일회용 VM 경계로 충분하다고 명시합니다. guest 내부 쓰기 경계 증명은 P4 qualification용으로 분리합니다. 이렇게 해야 runner 구현이 spike를 막는 순환이 생기지 않습니다.
  - P4 전에 "선언된 ordered ID 집합 = discovered = executed"와 POSIX 전용 ID별 Windows counterpart 또는 근거 있는 N/A ledger를 고정합니다. 여기에 skip 수를 함께 기록합니다.
- **차단 범위**: (b) spike 실행을 차단합니다(공유 폴더와 snapshot 조건 추가 전). (c) admission을 차단합니다(ledger).

### R0-F8 (P2) — B 정책: architecture 축이 모호하고 용어 체계가 부족함. focused x64 smoke 시점은 저비용으로 앞당길 수 있음

- **위치**: "Preferred Proposal And Admission Basis", 정책 문안 blockquote, Security line 9, Development Index line 162.
- **관측**: 대표 tuple은 ARM64이고, 공식 3.14.7 ARM64 installer에는 Experimental 표기가 있습니다.
- **구체적 불일치**:
  1. "ARM64/x64"가 OS architecture인지 interpreter process architecture인지 정의되지 않았습니다. ARM64 Windows에서 x64 Python을 emulation으로 쓰는 구성은 현실적으로 흔합니다. 이 구성이 지원인지, 미검증인지, 거절인지에 따라 runtime refusal 코드가 달라집니다. 정책 문제이면서 구현 입력입니다.
  2. 현재 문서에는 "runtime gate 적합(execute 가능)"과 "qualified" 두 상태만 있습니다. B는 "supported-but-untested"라는 세 번째 상태를 새로 만들지만, capability/help에서 쓸 용어가 정해지지 않았습니다.
  3. "Enterprise"가 제품 tier 제외 문구(Development Index line 162)와 Windows 11 Enterprise edition 사이에서 겹칩니다. edition 범위(Home/Pro/Enterprise/Education)를 명시해야 합니다.
- **x64에 대한 판단**: ARM64와 x64는 둘 다 LLP64이고, 선택될 파일 API는 variadic이 아닙니다. 그래서 ctypes ABI 차이만으로 full matrix를 요구할 근거는 약합니다. B를 반박할 구체 메커니즘은 찾지 못했습니다. 다만 다수 사용자가 x64인 상황에서 첫 지원 선언이 x64 실행 0회에 근거하게 됩니다. UTM은 Apple Silicon에서 x64 Windows guest를 full-system emulation으로 돌릴 수 있습니다(느림). launcher, binding layout, lock/replace primitive smoke 정도의 focused 실행은 물리 PC 없이 가능합니다.
- **권고**: B를 유지하되 다음을 결정합니다.
  - (a) 축을 "OS arch × interpreter process arch"로 정의하고, 첫 admission에서는 emulated x64 process를 "미검증, 별도 표기"로 둡니다.
  - (b) focused x64 smoke를 첫 admission 전에 둘지(권고) 아니면 후속으로 둘지 Owner가 정합니다. 앞당기더라도 complete suite는 요구하지 않습니다.
  - (c) Experimental 표기는 정책이 자동으로 결정하지 않는다는 계획의 입장을 유지하되, 대표 tuple로 x64를 고르는 대안도 비교합니다.
- **차단 범위**: (a) 축 정의만 구현 전에 필요합니다. (c) 나머지는 admission 전에만 필요합니다.

### R0-F9 (P2) — Timing amendment 문구와 B amendment의 상호작용

- **위치**: "Timing Amendment Proposal" blockquote 마지막 문장, "Named Amendment Scope".
- **추론**: "require the existing exact-environment evidence"에서 "existing"은 현행 Windows Admission 절(unobserved architectures qualification 금지와 결합된 기준)을 가리키는 것으로 읽힐 수 있습니다. timing amendment만 먼저 수락되고 B가 나중에 수락되면, 두 문구가 서로 다른 admission 기준을 가리킵니다. 계획은 두 amendment를 "별도로 수락"한다고 적었지만, 문구의 상호 참조는 다루지 않았습니다.
- **권고**: "existing"을 "the then-accepted Windows admission criteria"로 바꿉니다. 수락 순서별(timing만 수락 / 둘 다 수락 / B만 수락) 결과 문구를 표로 제시합니다. Preview 이후 formal admission과 공개 승격이라는 선행 조건은 보존되어 있으며, 이 점은 타당합니다.
- **차단 범위**: (a) Preview 이전에 구현하려면 timing amendment 수락이 선행되어야 합니다. (c) 문구 정합.

### R0-F10 (P3) — 절차, 통합, 예산

- **위치**: "Integration With Concurrent Main Work", Bounded Stages P2, P4 예산, `guest-baseline.py`의 `git` 호출.
- **내용**:
  - 동시에 진행 중인 ordinary acceptance 작업도 inventory/window, bootstrap allowlist, discovery를 바꿀 수 있습니다. 두 successor window가 충돌할 수 있으므로, Windows P3를 그 작업의 통합 이후로 직렬화할지 결정해야 합니다.
  - 이 R0의 행 번호 근거는 통합 후 무효가 될 수 있습니다.
  - P2의 "항목당 5분·총 30분"은 probe 작성 시간을 포함하는지 불분명합니다.
  - Windows의 process 생성 비용과 실시간 검사는 macOS의 38분 기록을 기준으로 삼기 어렵게 만듭니다. 계획대로 측정에서 출발하는 것은 타당합니다.
  - baseline helper는 PATH의 `git`을 호출합니다. digest를 확인한 `git.exe`와 실제 호출된 binary의 결합은 증명되지 않았습니다. baseline 결론(import 실패)에는 영향이 없습니다.
- **차단 범위**: 차단하지 않습니다. (a) 착수 시점의 재확인 항목입니다.

---

## 3. 제품 구현 전 결정 사항

### 정책·계약 결정 (Owner, spike 없이 가능)

| ID | 결정 | 대안 | 권고 |
| --- | --- | --- | --- |
| D1 | Windows lifecycle 범위 | (a) macOS와 완전 동등(checkout-1→entry-1 transition 포함, 외부 생성 workspace 지원) (b) fresh entry-1 init, 같은 window의 update/rollback/repair/detach만 허용하고 transition과 타 platform 생성 workspace는 안정 코드로 거절 | (b). D3 amendment 필요성이 사라질 수 있고(F1), cross-platform fencing이 단순해짐(F6) |
| D2 | inventory window | (a) 같은 entry-1 window 유지 (b) 이름 미정의 successor window | old reader 정적 분석 결과를 근거로 결정. 현재 정보로는 (b) |
| D3 | 상태 표식과 권한의 Windows 대응 | (a) platform별 상태 표식을 successor 계약에 명시하고 상속 ACL 유지 (b) 명시적 private DACL | (a)와 "새 기밀성 주장 없음" |
| D4 | native 진입 형태 | `.cmd` 제한형 / 문서화된 explicit interpreter 진입 / native exe | (나) explicit 진입과 (가) 제한형 `.cmd` 중 Owner가 "native launcher" 해석으로 선택. (다)는 제외 |
| D5 | 공통 helper durability 분류 어휘 | `unavailable` 재사용 / Windows 전용 분류 | 전용 분류. D3 refusal 의미와 분리 |
| D6 | reader share 정책 | share-delete opener / writer의 안정 non-pass와 exact retry | 측정 전 잠정 (나). 최종 결정은 spike 이후 |
| D7 | B 정책 세부 | 축 정의, emulated x64 처리, supported/qualified/observed 용어, edition 범위, focused x64 smoke 시점 | 축 = OS×process. emulated는 별도 미검증. x64 focused smoke는 첫 admission 전(complete 아님) |
| D8 | timing amendment 문구와 수락 순서 | 현재 문구 / "then-accepted criteria" 참조 | 후자 |
| D9 | 동시 작업과의 순서 | 병행 / 통합 이후 P3 | 통합 이후 P3. spike는 병행 가능 |

### spike로 확정할 구현 세부 (증거로 결정, 별도 승인 필요)

- `LockFileEx` 경합, 비정상 종료 후 해제 지연, handle 비상속, 같은 process 재진입.
- 표준 사용자 권한에서 directory handle 열기와 `FlushFileBuffers` 성공 여부. 결과는 durability 주장 없이 관측값으로만 기록.
- `os.replace` / `MoveFileExW` / POSIX-semantics rename에서 열린 handle(share mode별), read-only 속성, delete-pending 관측.
- junction, symlink, unknown reparse tag 탐지와 ancestor handle 유지의 race 동작.
- `.cmd` 실행 중 교체·삭제 시 exit code, 그리고 메타문자 argv 왕복.
- ctypes 선언 layout(`OVERLAPPED` 등)과 실패 경로의 last-error.
- 단위 실행 시간 측정(P4 예산 입력).

### 순환을 피하는 전제

spike는 제품 source를 바꾸지 않습니다. task root에 둔 throwaway probe로 진행하고, 일회용 VM clone에서 공유 폴더를 분리하고 network를 차단한 상태로 실행합니다. 따라서 계약 amendment 수락이 필요하지 않습니다. spike 계획(명령, 경계, 시간)을 고정하면 이 R0를 spike의 R0로 삼을지 Owner가 정할 수 있습니다. spike 결과는 D3/D5/D6의 증거가 되고, 그 뒤 amendment 수락과 구현 승인이 이어집니다.

---

## 4. 타당한 점, 남은 불확실성, 독립 검증 불가 항목

**타당한 점**

- 관측(import, help, native 진입 실패)과 정적 가설, 공식 문서 근거, 미래 시험을 일관되게 구분했습니다. helper의 exit 0을 PASS로 바꾸지 않았고, 609라는 AST 숫자를 collection 크기로 쓰지 않았습니다.
- `msvcrt.locking` 배제, `ReplaceFileW` WRITE_THROUGH 오용 금지, delete-then-copy fallback 금지, D3 `pass` 위조 금지가 모두 정확한 방향입니다.
- 재현 tuple, 지원 조건, 실행 거절의 3분할이 명확합니다. executable digest를 allowlist로 만들지 않는 구분도 좋습니다.
- full rerun을 제안할 때 failure mechanism, 영향 경로, focused 불충분 이유를 함께 요구하는 escalation 규칙은 Maintaining의 4점 평가와 정합합니다.
- 기존 PASS를 재사용하지 않았고, budget 소진을 incomplete로 취급하며, Preview 이후 formal admission을 유지했습니다.

**남은 불확실성**

- 위 F1~F5의 Windows CPython과 Win32 동작은 문서와 알려진 동작에 근거한 추론입니다. 특히 다음 항목은 spike 전까지 미확정입니다: directory `os.open`의 errno, `lstat`의 junction 분류, 잠금 해제 지연, delete-pending 노출, directory handle flush.
- `.hrn`과 `colvia`의 tracked 여부는 계약 문구에서 추론했습니다.
- fresh init, same-entry switch, repair, detach가 0600/0755 predicate를 실제로 거치는지는 제공된 발췌만으로 확인하지 못했습니다.
- old entry-1 reader가 확장된 inventory를 어떻게 처리하는지는 해당 reader 코드가 packet에 없어서 판단하지 못했습니다.

**독립적으로 검증하지 못한 것**

packet과 raw evidence digest, 198개 blob 일치, guest tuple 값, Authenticode 확인, token group 관측, 공식 문서의 현재 내용, 동시 작업의 실제 diff. 이번 검토에서 시험을 실행하거나 반례를 재현한 것은 없습니다.
````
